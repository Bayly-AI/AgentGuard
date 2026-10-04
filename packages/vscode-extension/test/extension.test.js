import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { ExtensionAgentGuardClient } from "../dist/client.js";

const __dirname = dirname(fileURLToPath(import.meta.url));

test("AgentGuard VSCode Extension Manifest & Structure Verification", () => {
  const pkgPath = resolve(__dirname, "../package.json");
  assert.ok(existsSync(pkgPath), "package.json must exist");

  const pkg = JSON.parse(readFileSync(pkgPath, "utf-8"));
  assert.equal(pkg.name, "agentguard-vscode");
  assert.equal(pkg.publisher, "BaylyAI");
  assert.equal(pkg.engines?.vscode, "^1.80.0");
  assert.ok(pkg.contributes?.commands?.length >= 5, "Must declare core commands");
  assert.ok(pkg.contributes?.views?.["agentguard-explorer"]?.length >= 4, "Must contribute 4 plane views");
  assert.ok(existsSync(resolve(__dirname, "../media/agentguard.svg")), "SVG icon must exist");
  assert.ok(existsSync(resolve(__dirname, "../media/agentguard.png")), "PNG icon must exist");
});

test("AgentGuard Extension Client CLI Bridge Test", async () => {
  const root = resolve(__dirname, "../../..");
  const client = new ExtensionAgentGuardClient(root);

  const status = await client.getStatus();
  assert.ok(status.length > 0, "status command output should not be empty");

  const validation = await client.validate();
  assert.equal(typeof validation.is_valid, "boolean");

  const finops = await client.getFinOps();
  assert.ok(finops.prompt_tokens_saved_pct >= 90, "FinOps must report >= 90% savings");
});
