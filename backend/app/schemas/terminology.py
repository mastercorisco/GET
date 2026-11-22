from typing import Literal

from pydantic import BaseModel, Field

ScopeType = Literal["library", "project"]


class TerminologyCreateRequest(BaseModel):
    scope_type: ScopeType
    scope_id: str | None = None
    preferred_term: str = Field(min_length=1)
    definition: str = Field(min_length=1)
    language: str = Field(default="pt", min_length=1)
    acronym: str | None = None
    synonyms: list[str] = Field(default_factory=list)
    avoid_terms: list[str] = Field(default_factory=list)
    technical_translation: str | None = None
    domain: str | None = None
    notes: str | None = None


class TerminologyUpdateRequest(BaseModel):
    preferred_term: str = Field(min_length=1)
    definition: str = Field(min_length=1)
    language: str = Field(default="pt", min_length=1)
    acronym: str | None = None
    synonyms: list[str] = Field(default_factory=list)
    avoid_terms: list[str] = Field(default_factory=list)
    technical_translation: str | None = None
    domain: str | None = None
    notes: str | None = None


class TerminologyResponse(BaseModel):
    id: str
    scope_type: ScopeType
    scope_id: str
    preferred_term: str
    definition: str
    language: str
    acronym: str | None
    synonyms: list[str]
    avoid_terms: list[str]
    technical_translation: str | None
    domain: str | None
    notes: str | None


class TerminologyOverrideCreateRequest(BaseModel):
    concept_id: str = Field(min_length=1)
    legacy_term: str | None = None
    avoid_in_project: bool = False
    usage_note: str | None = None


class TerminologyOverrideResponse(BaseModel):
    id: str
    project_id: str
    concept_id: str
    preferred_term: str
    legacy_term: str | None
    avoid_in_project: bool
    usage_note: str | None


class TerminologySearchHit(BaseModel):
    concept: TerminologyResponse
    project_override: TerminologyOverrideResponse | None = None