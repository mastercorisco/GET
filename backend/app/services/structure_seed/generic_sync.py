"""Sincronização genérica da estrutura documental a partir de catálogos versionados."""

from __future__ import annotations

import json
import uuid
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import AppSettings
from app.domain.block.models import DEFAULT_LISTS_JSON, DevelopmentPoint
from app.domain.block.block_enrichment import (
    classify_point_for_authoring,
    enrich_block_header,
    enrich_project_authoring,
)
from app.domain.block.ordering import normalize_block_point_orders, normalize_project_block_point_orders
from app.models.document import DocumentNode
from app.models.project import Project
from app.services.document_service import compute_display_codes
from app.services.structure_seed.catalog_types import StructureCatalog
from app.services.structure_seed.registry import load_catalog
from app.services.structure_seed.matching import best_title_match, texts_match, token_jaccard
from app.services.structure_seed.templates import pick_template
from app.services.workspace_paths import WorkspacePaths
from app.services.workspace_exclusivity import workspace_exclusive
from app.services.workspace_service import require_workspace_session, workspace_session

SyncMode = Literal["seed_empty", "migrate"]
MIGRATION_NOTE = "Rever após sincronização estrutural — ponto não mapeado no inventário."
INTENDED_OUTCOME = (
    "O tópico fica descrito com fronteiras claras, sem inventar requisitos não fornecidos."
)


@dataclass
class StructureSyncResult:
    project_id: str
    run_id: str
    dry_run: bool
    applied: bool
    skipped: bool
    backup_id: str | None
    report_path: str
    fascicles: int = 0
    blocks: int = 0
    catalog_points: int = 0
    warnings: list[str] = field(default_factory=list)
    blocking_errors: list[str] = field(default_factory=list)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _point_title(text: str) -> str:
    title = text.strip()
    if len(title) <= 120:
        return title
    cut = title[:117].rsplit(" ", 1)[0]
    return (cut or title[:117]) + "…"


def _load_nodes(session: Session, project_id: str) -> list[DocumentNode]:
    return list(
        session.scalars(
            select(DocumentNode).where(DocumentNode.project_id == project_id).order_by(DocumentNode.sort_key)
        )
    )


def _children(nodes: list[DocumentNode]) -> dict[str | None, list[DocumentNode]]:
    out: dict[str | None, list[DocumentNode]] = {}
    for node in nodes:
        out.setdefault(node.parent_id, []).append(node)
    for kids in out.values():
        kids.sort(key=lambda n: (n.sort_key, n.created_at, n.id))
    return out


def _fascicle_sort_key(ordinal: int) -> int:
    return ordinal * 1000


def _block_sort_key(fascicle_ordinal: int, block_ordinal: int) -> int:
    return fascicle_ordinal * 1000 + block_ordinal * 10


def _append_open_question(lists_json: str, text: str) -> str:
    try:
        data = json.loads(lists_json or DEFAULT_LISTS_JSON)
    except json.JSONDecodeError:
        data = json.loads(DEFAULT_LISTS_JSON)
    if not isinstance(data.get("open_questions"), list):
        data["open_questions"] = []
    data["open_questions"].append({"text": text})
    return json.dumps(data, ensure_ascii=False)


def _parse_llm_context(raw: str) -> dict:
    try:
        data = json.loads(raw or "{}")
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _structure_stamp(context: dict) -> dict | None:
    stamp = context.get("structure_catalog")
    return stamp if isinstance(stamp, dict) else None


@contextmanager
def _sync_session(app_settings: AppSettings, *, dry_run: bool):
    if dry_run:
        session, paths = require_workspace_session(app_settings)
        try:
            yield session, paths
            session.rollback()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    else:
        with workspace_session(app_settings, begin_immediate=True) as (session, paths):
            yield session, paths


def _match_fascicles(
    catalog: StructureCatalog,
    nodes: list[DocumentNode],
    *,
    mode: SyncMode,
) -> tuple[dict[str, str], list[str]]:
    """catalog fascicle code -> node id"""
    mapping: dict[str, str] = {}
    warnings: list[str] = []
    fascicles = [n for n in nodes if n.node_type == "fascicle"]
    used: set[str] = set()
    code_by_id = compute_display_codes(nodes)

    for spec in catalog.fascicles:
        if mode == "seed_empty":
            continue
        legacy_id = None
        for f in fascicles:
            if f.id in used:
                continue
            if code_by_id.get(f.id) == spec.code:
                legacy_id = f.id
                break
        if legacy_id is None:
            candidates = [(f.id, f.title) for f in fascicles if f.id not in used]
            hit = best_title_match(spec.title, candidates, threshold=0.35)
            if hit:
                legacy_id = hit[0]
        if legacy_id:
            mapping[spec.code] = legacy_id
            used.add(legacy_id)
        else:
            warnings.append(f"Fascículo novo: {spec.code}")

    return mapping, warnings


def _match_blocks(
    catalog: StructureCatalog,
    nodes: list[DocumentNode],
    fascicle_map: dict[str, str],
    legacy_codes: dict[str, str],
    *,
    mode: SyncMode,
) -> tuple[dict[str, str], list[dict], list[str]]:
    """block code -> node id"""
    mapping: dict[str, str] = {}
    ambiguous: list[dict] = []
    warnings: list[str] = []
    blocks = [n for n in nodes if n.node_type == "block"]
    used: set[str] = set()
    by_parent: dict[str | None, list[DocumentNode]] = {}
    for b in blocks:
        by_parent.setdefault(b.parent_id, []).append(b)

    for fascicle in catalog.fascicles:
        fascicle_id = fascicle_map.get(fascicle.code)
        parent_pool = by_parent.get(fascicle_id, []) if fascicle_id else blocks

        for block_spec in fascicle.blocks:
            if mode == "seed_empty":
                continue
            node_id = None
            for b in parent_pool:
                if b.id in used:
                    continue
                if legacy_codes.get(b.id) == block_spec.code:
                    node_id = b.id
                    break
            if node_id is None:
                candidates = [(b.id, b.title) for b in blocks if b.id not in used]
                hit = best_title_match(block_spec.title, candidates, threshold=0.42, used=used)
                if hit:
                    node_id = hit[0]
                elif mode == "migrate":
                    scored = sorted(
                        ((b.id, token_jaccard(block_spec.title, b.title)) for b in blocks if b.id not in used),
                        key=lambda x: -x[1],
                    )
                    if len(scored) >= 2 and scored[0][1] >= 0.42 and scored[1][1] >= scored[0][1] - 0.05:
                        ambiguous.append(
                            {
                                "block_code": block_spec.code,
                                "title": block_spec.title,
                                "candidates": [scored[0][0], scored[1][0]],
                            }
                        )
            if node_id:
                mapping[block_spec.code] = node_id
                used.add(node_id)
            else:
                warnings.append(f"Bloco novo: {block_spec.code} — {block_spec.title}")

    return mapping, ambiguous, warnings


def _ensure_fascicle(
    session: Session,
    project_id: str,
    spec,
    node_id: str | None,
    sort_key: int,
) -> str:
    if node_id:
        node = session.get(DocumentNode, node_id)
        if node:
            node.title = spec.title
            node.sort_key = sort_key + 500_000
            session.flush()
            return node.id
    node = DocumentNode(
        id=str(uuid.uuid4()),
        project_id=project_id,
        parent_id=None,
        node_type="fascicle",
        title=spec.title,
        sort_key=sort_key + 500_000,
    )
    session.add(node)
    session.flush()
    return node.id


def _ensure_block(
    session: Session,
    project_id: str,
    fascicle_id: str,
    spec,
    node_id: str | None,
    sort_key: int,
) -> str:
    if node_id:
        node = session.get(DocumentNode, node_id)
        if node:
            node.title = spec.title
            node.parent_id = fascicle_id
            node.sort_key = sort_key + 500_000
            session.flush()
            return node.id
    node = DocumentNode(
        id=str(uuid.uuid4()),
        project_id=project_id,
        parent_id=fascicle_id,
        node_type="block",
        title=spec.title,
        sort_key=sort_key + 500_000,
    )
    session.add(node)
    session.flush()
    return node.id


def _finalize_sort_keys(session: Session, nodes: list[DocumentNode]) -> None:
    for node in nodes:
        if node.sort_key >= 500_000:
            node.sort_key -= 500_000
    session.flush()


def _sync_points(
    session: Session,
    block_id: str,
    fascicle_code: str,
    block_title: str,
    target_texts: list[str],
    report: dict,
    *,
    preserve_rich_content: bool,
) -> None:
    existing = list(
        session.scalars(
            select(DevelopmentPoint)
            .where(DevelopmentPoint.block_id == block_id)
            .where(DevelopmentPoint.status != "obsolete")
            .order_by(DevelopmentPoint.sort_order, DevelopmentPoint.id)
        )
    )
    used_point_ids: set[str] = set()
    template_id = pick_template(fascicle_code, block_title)

    for order, bullet in enumerate(target_texts, start=1):
        matched: DevelopmentPoint | None = None
        best_score = 0.0
        for point in existing:
            if point.id in used_point_ids:
                continue
            for probe in (point.core_idea, point.title):
                if not probe:
                    continue
                if texts_match(probe, bullet):
                    matched = point
                    best_score = 1.0
                    break
                score = token_jaccard(probe, bullet)
                if score > best_score:
                    best_score = score
                    matched = point
        if matched and best_score < 0.45:
            matched = None

        if matched:
            used_point_ids.add(matched.id)
            matched.sort_order = order * 10
            title = _point_title(bullet)
            rich = bool(matched.core_idea.strip()) and not texts_match(matched.core_idea, bullet)
            if matched.status == "approved" or (preserve_rich_content and rich):
                matched.needs_review = True
                report["content_preserved"].append(
                    {"point_id": matched.id, "block_id": block_id, "reason": "approved_or_rich"}
                )
            else:
                if not matched.core_idea.strip() or matched.core_idea.strip() == matched.title.strip():
                    matched.core_idea = bullet
                matched.title = title
            if not matched.intended_outcome.strip():
                matched.intended_outcome = INTENDED_OUTCOME
            continue

        point = DevelopmentPoint(
            id=str(uuid.uuid4()),
            block_id=block_id,
            sort_order=order * 10,
            title=_point_title(bullet),
            core_idea=bullet,
            intended_outcome=INTENDED_OUTCOME,
            llm_freedom="strict",
            status="draft",
            template_id=template_id,
            needs_review=False,
            lists_json=DEFAULT_LISTS_JSON,
        )
        session.add(point)
        report["points_created"].append({"block_id": block_id, "title": point.title})

    for point in existing:
        if point.id in used_point_ids:
            continue
        point.needs_review = True
        point.lists_json = _append_open_question(point.lists_json, MIGRATION_NOTE)
        report["orphan_points"].append({"point_id": point.id, "block_id": block_id})

    normalize_block_point_orders(session, block_id, run_id="sync_points")

    block = session.get(DocumentNode, block_id)
    if block is not None:
        titles = [
            t
            for t in (
                session.scalars(
                    select(DevelopmentPoint.title)
                    .where(DevelopmentPoint.block_id == block_id)
                    .where(DevelopmentPoint.status != "obsolete")
                    .order_by(DevelopmentPoint.sort_order)
                )
            )
            if (t or "").strip()
        ]
        enrich_block_header(block, titles)
        for p in session.scalars(
            select(DevelopmentPoint)
            .where(DevelopmentPoint.block_id == block_id)
            .where(DevelopmentPoint.status != "obsolete")
        ):
            classify_point_for_authoring(p, clear_needs_review=False)


def _write_report(
    paths: WorkspacePaths, project_id: str, run_id: str, body: dict, *, report_prefix: str
) -> Path:
    out_dir = paths.root / "migration_reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{report_prefix}_{project_id}_{run_id}.json"
    path.write_text(json.dumps(body, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def apply_structure_catalog(
    app_settings: AppSettings,
    project_id: str,
    *,
    catalog_id: str | None = None,
    mode: SyncMode = "migrate",
    dry_run: bool = True,
    catalog: StructureCatalog | None = None,
    backup_id: str | None = None,
    preserve_rich_content: bool = True,
    exclusive_lock: str = "structure_catalog_sync",
    report_prefix: str = "structure_catalog",
) -> StructureSyncResult:
    if catalog is None:
        if not catalog_id:
            raise ValueError("Indique catalog_id ou catalog.")
        catalog = load_catalog(catalog_id)
    min_fascicles = catalog.fascicle_count
    min_blocks = catalog.block_count
    run_id = str(uuid.uuid4())[:8]
    report: dict = {
        "run_id": run_id,
        "project_id": project_id,
        "mode": mode,
        "dry_run": dry_run,
        "catalog_checksum": catalog.checksum,
        "content_preserved": [],
        "points_created": [],
        "orphan_points": [],
        "orphan_nodes": [],
        "ambiguous_blocks": [],
        "warnings": [],
        "counts": {},
    }
    warnings: list[str] = []
    blocking: list[str] = []
    skipped = False

    exclusive = nullcontext() if dry_run else workspace_exclusive(exclusive_lock)
    with exclusive:
        with _sync_session(app_settings, dry_run=dry_run) as (session, paths):
            project = session.get(Project, project_id)
            if project is None:
                raise ValueError("Projecto não encontrado.")

            ctx = _parse_llm_context(project.llm_context_json)
            stamp = _structure_stamp(ctx)
            nodes = _load_nodes(session, project_id)
            legacy_codes = compute_display_codes(nodes) if nodes else {}

            if (
                not dry_run
                and stamp
                and stamp.get("checksum") == catalog.checksum
                and stamp.get("id") == catalog.id
            ):
                if (
                    len([n for n in nodes if n.node_type == "fascicle"]) == min_fascicles
                    and len([n for n in nodes if n.node_type == "block"]) >= min_blocks
                ):
                    skipped = True

            if skipped:
                report["skipped"] = True
                path = _write_report(paths, project_id, run_id, report, report_prefix=report_prefix)
                return StructureSyncResult(
                    project_id=project_id,
                    run_id=run_id,
                    dry_run=dry_run,
                    applied=False,
                    skipped=True,
                    backup_id=backup_id,
                    report_path=str(path),
                    fascicles=catalog.fascicle_count,
                    blocks=catalog.block_count,
                    catalog_points=catalog.point_count,
                    warnings=warnings,
                    blocking_errors=blocking,
                )

            fascicle_map, fascicle_warnings = _match_fascicles(catalog, nodes, mode=mode)
            warnings.extend(fascicle_warnings)

            block_map, ambiguous, block_warnings = _match_blocks(
                catalog, nodes, fascicle_map, legacy_codes, mode=mode
            )
            warnings.extend(block_warnings)
            report["ambiguous_blocks"] = ambiguous

            mapped_ids: set[str] = set(fascicle_map.values()) | set(block_map.values())

            for fascicle in catalog.fascicles:
                f_sort = _fascicle_sort_key(fascicle.ordinal)
                fascicle_id = _ensure_fascicle(
                    session,
                    project_id,
                    fascicle,
                    fascicle_map.get(fascicle.code),
                    f_sort,
                )
                fascicle_map[fascicle.code] = fascicle_id
                mapped_ids.add(fascicle_id)

                for block in fascicle.blocks:
                    b_sort = _block_sort_key(fascicle.ordinal, block.ordinal)
                    block_id = _ensure_block(
                        session,
                        project_id,
                        fascicle_id,
                        block,
                        block_map.get(block.code),
                        b_sort,
                    )
                    block_map[block.code] = block_id
                    mapped_ids.add(block_id)
                    _sync_points(
                        session,
                        block_id,
                        fascicle.code,
                        block.title,
                        block.development_points,
                        report,
                        preserve_rich_content=preserve_rich_content,
                    )

            nodes = _load_nodes(session, project_id)
            _finalize_sort_keys(session, nodes)

            for node in nodes:
                if node.id in mapped_ids:
                    continue
                if node.node_type == "block":
                    node.block_status = "needs_review"
                    report["orphan_nodes"].append({"node_id": node.id, "title": node.title, "type": "block"})
                elif node.node_type == "fascicle" and not any(
                    c.parent_id == node.id for c in nodes if c.node_type == "block"
                ):
                    report["orphan_nodes"].append({"node_id": node.id, "title": node.title, "type": "fascicle"})

            if not dry_run:
                renumber_stats = normalize_project_block_point_orders(session, project_id, run_id=run_id)
                report["point_renumber"] = renumber_stats
                report["authoring_enrich"] = enrich_project_authoring(
                    session, project_id, run_id=run_id, clear_needs_review=False
                )

            fascicle_n = len([n for n in _load_nodes(session, project_id) if n.node_type == "fascicle"])
            block_n = len([n for n in _load_nodes(session, project_id) if n.node_type == "block"])
            report["counts"] = {
                "fascicles": fascicle_n,
                "blocks": block_n,
                "catalog_points": catalog.point_count,
            }
            report["warnings"] = warnings

            if not dry_run:
                ctx["structure_catalog"] = {
                    "id": catalog.id,
                    "checksum": catalog.checksum,
                    "applied_at": _utcnow().isoformat(),
                }
                project.llm_context_json = json.dumps(ctx, ensure_ascii=False, sort_keys=True)
                session.flush()

            if fascicle_n < min_fascicles or block_n < min_blocks:
                blocking.append(
                    f"Contagens após sync: fascículos={fascicle_n} blocos={block_n} "
                    f"(mínimo {min_fascicles}/{min_blocks})"
                )

            path = _write_report(paths, project_id, run_id, report, report_prefix=report_prefix)

    return StructureSyncResult(
        project_id=project_id,
        run_id=run_id,
        dry_run=dry_run,
        applied=not dry_run and not skipped,
        skipped=skipped,
        backup_id=backup_id,
        report_path=str(path),
        fascicles=catalog.fascicle_count,
        blocks=catalog.block_count,
        catalog_points=catalog.point_count,
        warnings=warnings,
        blocking_errors=blocking,
    )
