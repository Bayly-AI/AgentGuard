import { AgentGuardClient } from "./client.ts";
import type { PluginOptions, SecurityGateResult } from "./types.ts";

export type * from "./types.ts";
export { AgentGuardClient, AgentGuardClient as AgentGraph } from "./client.ts";

/**
 * Main AgentGuard Node.js Plugin class.
 */
export class AgentGuardPlugin {
  public client: AgentGuardClient;

  constructor(options: PluginOptions = {}) {
    this.client = new AgentGuardClient(options);
  }

  /**
   * Wrap any tool execution function with AgentGuard pre-execution security gating.
   */
  public async wrapTool<T>(
    roleId: string,
    toolName: string,
    toolFn: () => Promise<T>
  ): Promise<T> {
    const gate = await this.client.enforceGate(roleId, toolName);
    if (!gate.allowed) {
      throw new Error(`[AgentGuard DENIED] Role '${roleId}' cannot execute tool '${toolName}': ${gate.error}`);
    }
    return await toolFn();
  }

  /**
   * Express / Connect middleware for security gating HTTP endpoints.
   */
  public expressGateMiddleware(roleIdParam: string = "roleId", toolNameParam: string = "toolName") {
    return async (req: any, res: any, next: any) => {
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
