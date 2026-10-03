import { test, before, after } from "node:test";
import assert from "node:assert";
import { mkdtempSync, rmSync, existsSync } from "node:fs";
import { join, resolve } from "node:path";
import { tmpdir } from "node:os";

import { AgentGuardClient, AgentGuardPlugin } from "../src/index.ts";

let REPO_ROOT = process.cwd();
for (let i = 0; i < 5; i++) {
  if (existsSync(resolve(REPO_ROOT, "release/python/cli/agentguard"))) break;
  REPO_ROOT = resolve(REPO_ROOT, "..");
}
const CLI_PATH = resolve(REPO_ROOT, "release/python/cli/agentguard");

test("Node.js AgentGuard Plugin Test Suite", async (t) => {
  let tempDir: string;
  let client: AgentGuardClient;
  let plugin: AgentGuardPlugin;

  before(() => {
    tempDir = mkdtempSync(join(tmpdir(), "ag-node-test-"));
    client = new AgentGuardClient({
      cliPath: CLI_PATH,
      workspaceDir: tempDir,
    });
    plugin = new AgentGuardPlugin({
      cliPath: CLI_PATH,
      workspaceDir: tempDir,
    });
  });

  after(() => {
    rmSync(tempDir, { recursive: true, force: true });
  });

  await t.test("1. Initialize workspace with init()", async () => {
    const output = await client.init(true);
    assert.match(output, /Successfully initialized workspace layout/);
    assert.strictEqual(existsSync(join(tempDir, "AGENTS.md")), true);
    assert.strictEqual(existsSync(join(tempDir, ".agentguard")), true);
  });

  await t.test("2. Synthesize dynamic system prompt for developer role", async () => {
    const prompt = await client.synthesizePrompt("developer");
    assert.match(prompt, /Agent Governance Mandate/);
    assert.match(prompt, /developer/);
  });

  await t.test("3. Security Gate allows authorized tool calls (developer + view_file)", async () => {
    const gate = await client.enforceGate("developer", "view_file");
    assert.strictEqual(gate.allowed, true);
    assert.strictEqual(gate.details, "Security Gate PASSED");
  });

  await t.test("4. Security Gate blocks unauthorized tool calls (reviewer + replace_file_content)", async () => {
    const gate = await client.enforceGate("reviewer", "replace_file_content");
    assert.strictEqual(gate.allowed, false);
    assert.match(gate.error!, /DENIED/);
  });

  await t.test("5. Wrap tool function with wrapTool()", async () => {
    const result = await plugin.wrapTool("developer", "view_file", async () => {
      return "File content retrieved successfully";
    });
    assert.strictEqual(result, "File content retrieved successfully");

    await assert.rejects(
      async () => {
        await plugin.wrapTool("reviewer", "replace_file_content", async () => {
          return "File edited";
        });
      },
      /AgentGuard DENIED/
    );
  });

  await t.test("6. Validate graph substrate topology and priority tier DAGs", async () => {
    const report = await client.validate();
    assert.strictEqual(report.is_valid, true);
  });

  await t.test("7. Execute Hath0r Quality Gates suite", async () => {
    const qg = await client.runQualityGate();
    assert.strictEqual(qg.success, true);
    assert.match(qg.output, /Hath0r Quality Gates Status: ALL GATES PASSED/);
  });

  await t.test("8. Execute Taguchi Orthogonal Array matrix generation & SNR calculation", async () => {
    const matrix = await client.runTaguchi({
      array: "L9",
      factors: ["temp", "pressure"],
    });
    assert.strictEqual(matrix.array_type, "L9");
    assert.strictEqual(matrix.runs.length, 9);

    const snr = await client.runTaguchi({
      snrValues: [10.0, 12.0, 8.0, 11.0],
      snrType: "smaller_the_better",
    });
    assert.strictEqual(typeof snr.snr_db, "number");
  });

  await t.test("9. Record token telemetry & compute FinOps histogram", async () => {
    const recOutput = await client.recordTokenTelemetry({
      prompt: "Hello AgentGuard",
      user: "node_tester",
      model: "claude-3-5-sonnet",
    });
    assert.match(recOutput, /Recorded telemetry entry/);

    const hist = await client.getTokenHistogram("node_tester", 5);
    assert.strictEqual(hist.total_records, 1);
    assert.strictEqual(hist.bins.length, 5);

    const check = await client.runTokenCheck("node_tester", 90);
    assert.strictEqual(check.total_records, 1);
  });
});
