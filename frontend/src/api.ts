export type Workspace = {
  id: string;
  root_path: string;
  local_user_name: string;
  database_path: string;
  backups_path: string;
  exports_path: string;
  imports_path: string;
};

function apiErrorMessage(body: unknown, fallback: string): string {
  if (body && typeof body === "object" && "detail" in body) {
    const detail = (body as { detail: unknown }).detail;
    if (typeof detail === "string") {
      return detail;
    }
    if (Array.isArray(detail)) {
      return detail.map((item) => JSON.stringify(item)).join("; ");
    }
  }
  return fallback;
}

export async function fetchCurrentWorkspace(): Promise<Workspace | null> {
  const res = await fetch("/api/workspace");
  if (!res.ok) throw new Error("Falha ao obter workspace.");
  const data: unknown = await res.json();
  if (data === null) {
    return null;
  }
  return data as Workspace;
}

export async function createWorkspace(rootPath: string, localUserName: string): Promise<Workspace> {
  const res = await fetch("/api/workspace/create", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ root_path: rootPath, local_user_name: localUserName }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(apiErrorMessage(body, "Falha ao criar workspace."));
  }
  return res.json();
}

export async function openWorkspace(rootPath: string): Promise<Workspace> {
  const res = await fetch("/api/workspace/open", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ root_path: rootPath }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(apiErrorMessage(body, "Falha ao abrir workspace."));
  }
  return res.json();
}