import { test, expect } from "@playwright/test";

test("homepage mostra workspace", async ({ page }) => {
  await page.goto("http://127.0.0.1:4811/");
  await expect(page.getByRole("heading", { name: /GET/ })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Workspace" })).toBeVisible();
});