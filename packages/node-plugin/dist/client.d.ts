import type { AuditEntry, PluginOptions, SecurityGateResult, ValidationReport } from "./types.js";

export declare class AgentGuardClient {
  cliPath: string;
  dbPath: string;
  workspaceDir: string;
  constructor(options?: PluginOptions);
  runCommand(args: string[]): Promise<string>;
  runCommandSync(args: string[]): string;
  init(noHooks?: boolean): Promise<string>;
  sync(): Promise<string>;
  synthesizePrompt(roleId: string, scope?: string): Promise<string>;
  enforceGate(roleId: string, toolName: string): Promise<SecurityGateResult>;
  validate(): Promise<ValidationReport>;
  runQualityGate(): Promise<{ success: boolean; output: string }>;
  runTaguchi(options?: {
    array?: "L4" | "L8" | "L9" | "L12" | "L18";
    factors?: string[];
    snrValues?: number[];
    snrType?: "smaller_the_better" | "larger_the_better" | "nominal_the_best";
  }): Promise<any>;
  estimateTokens(prompt: string, completion?: string, tier?: string): Promise<any>;
  recordTokenTelemetry(entry: {
    prompt: string;
    user?: string;
    model?: string;
    tier?: string;
    completion?: string;
  }): Promise<string>;
  getTokenHistogram(user?: string, bins?: number): Promise<any>;
  runTokenCheck(user?: string, days?: number): Promise<any>;
}
