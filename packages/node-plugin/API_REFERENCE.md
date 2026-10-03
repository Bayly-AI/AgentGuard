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

---

## Class: `AgentGuardPlugin`

High-level wrapper for Node.js agent frameworks and middleware.

### `wrapTool<T>(roleId: string, toolName: string, toolFn: () => Promise<T>): Promise<T>`
Wraps tool execution function with automatic pre-execution security gate checks.

### `expressGateMiddleware(roleIdParam?: string, toolNameParam?: string)`
Returns Express/Connect middleware for HTTP endpoint security gating.
