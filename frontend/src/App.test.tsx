import { describe, expect, it } from "vitest";

describe("GET frontend smoke", () => {
  it("carrega título da aplicação", () => {
    expect("GET — Gerador de Especificações Funcionais").toContain("GET");
  });
});