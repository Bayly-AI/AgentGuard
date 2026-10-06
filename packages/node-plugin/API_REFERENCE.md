# @agentguard/node-plugin API Reference

## Class: `AgentGuardClient`

Direct interface to the AgentGuard CLI and Quad-Graph Substrate.

### `constructor(options?: PluginOptions)`
- `options.cliPath?: string` - Path to `agentguard` binary (auto-detected if omitted).
- `options.dbPath?: string` - Path to SQLite `.agentguard/graph.db`.
- `options.workspaceDir?: string` - Target repository directory (defaults to `process.cwd()`).

### `init(noHooks?: boolean): Promise<string>`
Scaffolds `.agentguard/` directory layout, `AGENTS.md`, and Git pre-commit validation hooks.

### `synthesizePrompt(roleId: string, scope?: string): Promise<string>`
Synthesizes dynamic zero-prompt-tax system prompt tailored for target role.

### `enforceGate(roleId: string, toolName: string): Promise<SecurityGateResult>`
Evaluates pre-execution RBAC tool authorization. Returns `{ allowed: boolean, roleId, toolName, details, error }`.

### `validate(): Promise<ValidationReport>`
Audits Quad-Graph topology, Priority Tier DAGs, cycle detection, and dangling edges.

### `runQualityGate(): Promise<{ success: boolean, output: string }>`
Executes the full 5 Hath0r Quality Gates suite sequentially.

### `runTaguchi(options?: TaguchiOptions): Promise<any>`
Generates Taguchi Orthogonal Arrays (L4, L8, L9, L12, L18) or computes Signal-to-Noise Ratio (SNR) in dB.

### `Class Alias: AgentGraph`
`AgentGraph` is exported as a direct class alias for `AgentGuardClient` (`import { AgentGraph } from "agentguard-node-plugin"`).

### `estimateTokens(prompt: string, completion?: string, tier?: string): Promise<TokenEstimationResult>`
Estimates prompt/completion token count and projected model cost USD.

### `recordTokenTelemetry(entry: TelemetryRecord): Promise<string>`
Records an agent prompt interaction to the FinOps telemetry ledger.

### `getTokenHistogram(user?: string, bins?: number): Promise<HistogramResult>`
Computes equal-width statistical token usage distribution histogram (min, max, mean, median, p95, p99, std dev).

### `runTokenCheck(user?: string, days?: number): Promise<FinOpsReport>`
Executes trailing 90-day FinOps usage analytics and model cost audit.

---

## Class: `AgentGuardPlugin`

High-level wrapper for Node.js agent frameworks and middleware.

### `wrapTool<T>(roleId: string, toolName: string, toolFn: () => Promise<T>): Promise<T>`
Wraps tool execution function with automatic pre-execution security gate checks.

### `expressGateMiddleware(roleIdParam?: string, toolNameParam?: string)`
Returns Express/Connect middleware for HTTP endpoint security gating.
