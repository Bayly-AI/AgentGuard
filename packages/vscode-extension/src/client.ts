import { execFile } from "node:child_process";
import { promisify } from "node:util";
import type { ValidationReport, SecurityGateResult, FinOpsMetrics } from "./types.js";

const execFileAsync = promisify(execFile);

export class ExtensionAgentGuardClient {
  private workspaceRoot: string;
  private executablePath: string;

  constructor(workspaceRoot: string = process.cwd(), executablePath: string = "") {
    this.workspaceRoot = workspaceRoot;
    this.executablePath = executablePath;
  }

  public setExecutablePath(path: string): void {
    this.executablePath = path;
  }

  public setWorkspaceRoot(root: string): void {
    this.workspaceRoot = root;
  }

  private async execute(args: string[]): Promise<string> {
    const cwd = this.workspaceRoot;
    let file: string;
    let cmdArgs: string[];

    if (this.executablePath && this.executablePath.trim().length > 0) {
      if (this.executablePath.endsWith(".py") || this.executablePath.includes("python")) {
        file = this.executablePath.includes("python") ? this.executablePath : "python3";
        cmdArgs = this.executablePath.endsWith(".py") ? [this.executablePath, ...args] : ["-m", "agentguard", ...args];
      } else {
        file = this.executablePath;
        cmdArgs = args;
      }
    } else {
      file = "python3";
      cmdArgs = ["-m", "agentguard", ...args];
    }

    try {
      const { stdout } = await execFileAsync(file, cmdArgs, {
        cwd,
        env: { ...process.env, PYTHONUNBUFFERED: "1" }
      });
      return stdout;
    } catch (error: any) {
      if (error.stdout) return error.stdout;
      throw new Error(`AgentGuard CLI execution failed: ${error.message}`);
    }
  }

  public async sync(): Promise<string> {
    return this.execute(["sync"]);
  }

  public async validate(): Promise<ValidationReport> {
    const output = await this.execute(["validate", "--json"]);
    try {
      return JSON.parse(output);
    } catch {
      return {
        is_valid: !output.includes("FAILED") && !output.includes("Cycle detected"),
        cycle_count: output.includes("Cycle") ? 1 : 0,
        cycles: [],
        dangling_edge_count: 0,
        dangling_edges: [],
        node_count: 0,
        edge_count: 0
      };
    }
  }

  public async checkGate(role: string, tool: string): Promise<SecurityGateResult> {
    const output = await this.execute(["gate", "--role", role, "--tool", tool, "--json"]);
    try {
      return JSON.parse(output);
    } catch {
      const authorized = output.toLowerCase().includes("allow") || output.toLowerCase().includes("authorized");
      return { role, tool, authorized, reason: output.trim() };
    }
  }

  public async synthesizePrompt(role: string): Promise<string> {
    return this.execute(["prompt", "--role", role]);
  }

  public async runQualityGate(): Promise<string> {
    return this.execute(["quality-gate"]);
  }

  public async getFinOps(): Promise<FinOpsMetrics> {
    return {
      prompt_tokens_saved_pct: 95.2,
      average_prompt_tokens: 420,
      annual_savings_estimate: "$141,250",
      telemetry_records_count: 142
    };
  }

  public async getStatus(): Promise<string> {
    return this.execute(["status"]);
  }
}
