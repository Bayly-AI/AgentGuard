import { AgentGuardClient } from "./client.js";
import type { PluginOptions } from "./types.js";

export type * from "./types.js";
export { AgentGuardClient, AgentGuardClient as AgentGraph } from "./client.js";

export declare class AgentGuardPlugin {
  client: AgentGuardClient;
  constructor(options?: PluginOptions);
  wrapTool<T>(roleId: string, toolName: string, toolFn: () => Promise<T>): Promise<T>;
  expressGateMiddleware(roleIdParam?: string, toolNameParam?: string): (req: any, res: any, next: any) => Promise<any>;
}
