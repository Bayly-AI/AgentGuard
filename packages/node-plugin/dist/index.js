import { AgentGuardClient } from "./client.js";

export * from "./types.js";
export { AgentGuardClient, AgentGuardClient as AgentGraph } from "./client.js";

/**
 * Main AgentGuard Node.js Plugin class.
 */
export class AgentGuardPlugin {
  constructor(options = {}) {
    this.client = new AgentGuardClient(options);
  }

  /**
   * Wrap any tool execution function with AgentGuard pre-execution security gating.
   */
  async wrapTool(roleId, toolName, toolFn) {
    const gate = await this.client.enforceGate(roleId, toolName);
    if (!gate.allowed) {
      throw new Error(`[AgentGuard DENIED] Role '${roleId}' cannot execute tool '${toolName}': ${gate.error}`);
    }
    return await toolFn();
  }

  /**
   * Express / Connect middleware for security gating HTTP endpoints.
   */
  expressGateMiddleware(roleIdParam = "roleId", toolNameParam = "toolName") {
    return async (req, res, next) => {
      const roleId = req.headers["x-agent-role"] || req.params[roleIdParam] || req.body[roleIdParam];
      const toolName = req.params[toolNameParam] || req.body[toolNameParam];

      if (!roleId || !toolName) {
        return res.status(400).json({ error: "Missing x-agent-role or toolName for AgentGuard Security Gate" });
      }

      const gate = await this.client.enforceGate(roleId, toolName);
      if (!gate.allowed) {
        return res.status(403).json({
          error: "AgentGuard Security Gate Intercepted Execution",
          roleId,
          toolName,
          details: gate.error
        });
      }

      next();
    };
  }
}
