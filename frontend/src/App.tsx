import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { createWorkspace, fetchCurrentWorkspace, openWorkspace } from "./api";

export default function App() {
  const queryClient = useQueryClient();
  const [rootPath, setRootPath] = useState("");
  const [userName, setUserName] = useState("local_user");
  const [error, setError] = useState<string | null>(null);

  const workspaceQuery = useQuery({
    queryKey: ["workspace"],
    queryFn: fetchCurrentWorkspace,
  });

  const createMutation = useMutation({
    mutationFn: () => createWorkspace(rootPath, userName),
    onSuccess: () => {
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["workspace"] });
    },
    onError: (err: Error) => setError(err.message),
  });

  const openMutation = useMutation({
    mutationFn: () => openWorkspace(rootPath),
    onSuccess: () => {
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["workspace"] });
    },
    onError: (err: Error) => setError(err.message),
  });

  return (
    <main>
      <h1>GET — Gerador de Especificações Funcionais</h1>
      <p>Aplicação local (127.0.0.1). SQLite como fonte de verdade.</p>

      <section className="card">
        <h2>Workspace</h2>
        <p>Crie ou abra um workspace de dados separado da aplicação.</p>
        <label htmlFor="rootPath">Caminho do workspace</label>
        <input
          id="rootPath"
          value={rootPath}
          onChange={(e) => setRootPath(e.target.value)}
          placeholder="/caminho/para/workspace-get"
        />
        <label htmlFor="userName">Utilizador local (proveniência)</label>
        <input
          id="userName"
          value={userName}
          onChange={(e) => setUserName(e.target.value)}
        />
        <button type="button" onClick={() => createMutation.mutate()} disabled={!rootPath}>
          Criar workspace
        </button>
        <button
          type="button"
          className="secondary"
          onClick={() => openMutation.mutate()}
          disabled={!rootPath}
        >
          Abrir workspace
        </button>
        {error ? <p className="error">{error}</p> : null}
      </section>

      <section className="card">
        <h2>Estado actual</h2>
        {workspaceQuery.isLoading ? <p>A carregar…</p> : null}
        {workspaceQuery.data ? (
          <pre>{JSON.stringify(workspaceQuery.data, null, 2)}</pre>
        ) : (
          <p>Nenhum workspace aberto.</p>
        )}
      </section>
    </main>
  );
}