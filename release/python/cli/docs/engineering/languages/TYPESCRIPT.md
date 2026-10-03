# Canonical AgentGuard TypeScript / Node.js Integration Guide

> **Language:** TypeScript / JavaScript (Node.js 18+, Deno, Bun)  
> **Integration Pattern:** CLI Subprocess IPC / SQLite Quad-Graph Bridge / FastMCP  

---

## 1. Overview & Setup

TypeScript and Node.js agent frameworks (e.g. LangChain JS, LlamaIndex TS, Vercel AI SDK, AutoGen TS) integrate seamlessly with AgentGuard via CLI IPC subprocess wrappers or direct SQLite database calls.

---

## 2. TypeScript AgentGuard Client Class

```typescript
import { execFile } from "child_process";
import { promisify } from "util";

const execFileAsync = promisify(execFile);

export interface SecurityGateResult {
  allowed: boolean;
  roleId: string;
  toolName: string;
  error?: string;
}

export class AgentGuardClient {
  private cliPath: string;
  private dbPath: string;

  constructor(cliPath: string = "agentguard", dbPath: string = ".agentguard/graph.db") {
    this.cliPath = cliPath;
    this.dbPath = dbPath;
  }

  /**
   * Synthesize zero-prompt-tax system prompt for a target role
   */
  async synthesizePrompt(roleId: string, scope?: string): Promise<string> {
    const args = ["prompt", "--role", roleId, "--db", this.dbPath];
    if (scope) args.push("--scope", scope);

    const { stdout } = await execFileAsync(this.cliPath, args);
    return stdout.trim();
  }

  /**
   * Enforce pre-execution RBAC tool security gate
   */
  async enforceSecurityGate(roleId: string, toolName: string): Promise<SecurityGateResult> {
    try {
      await execFileAsync(this.cliPath, [
        "gate",
        "--role", roleId,
        "--tool", toolName,
        "--db", this.dbPath
      ]);
      return { allowed: true, roleId, toolName };
    } catch (error: any) {
      return {
        allowed: false,
        roleId,
        toolName,
        error: error.stderr || error.message
      };
    }
  }
}
```

---

## 3. Vercel AI SDK / LangChain TS Tool Middleware Example

```typescript
import { AgentGuardClient } from "./agentguard";

const guard = new AgentGuardClient();

export async function executeGovernedTool(
  roleId: string,
  toolName: string,
  toolFn: () => Promise<any>
) {
  // Pre-execution Security Gate check
  const gate = await guard.enforceSecurityGate(roleId, toolName);
  if (!gate.allowed) {
    throw new Error(`[AgentGuard DENIED] Role '${roleId}' cannot execute tool '${toolName}': ${gate.error}`);
  }

  // Execute tool logic safely
  return await toolFn();
}
```

---

## 4. Taguchi Optimization & FinOps Token Histogram Usage

```typescript
import { AgentGuardClient } from "agentguard-node-plugin";

const client = new AgentGuardClient();

// Generate L9 Taguchi Orthogonal Array Matrix
const matrix = await client.runTaguchi({
  array: "L9",
  factors: ["temperature", "pressure", "time"],
});

// Compute Signal-to-Noise Ratio (SNR) in dB
const snr = await client.runTaguchi({
  snrValues: [10.0, 12.0, 8.0, 11.0],
  snrType: "smaller_the_better",
});

// Record token usage telemetry
await client.recordTokenTelemetry({
  prompt: "Synthesize prompt",
  user: "developer_1",
  model: "claude-3-5-sonnet",
  completion: "Response text",
});

// Get 10-bin token usage distribution histogram
const histogram = await client.getTokenHistogram("developer_1", 10);
```
