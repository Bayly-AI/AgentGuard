import { execFile, execFileSync } from "child_process";
import { promisify } from "util";
import { existsSync } from "fs";
import { resolve } from "path";
import type {
  AuditEntry,
  PluginOptions,
  SecurityGateResult,
  ValidationReport,
} from "./types.ts";

const execFileAsync = promisify(execFile);

export class AgentGuardClient {
  public cliPath: string;
  public dbPath: string;
  public workspaceDir: string;

  constructor(options: PluginOptions = {}) {
    this.workspaceDir = options.workspaceDir
      ? resolve(options.workspaceDir)
      : process.cwd();

    // Auto-detect CLI binary path
    if (options.cliPath) {
      this.cliPath = options.cliPath;
    } else if (process.env.AGENTGUARD_CLI) {
      this.cliPath = process.env.AGENTGUARD_CLI;
    } else {
      let curr = this.workspaceDir;
      let found: string | null = null;
      for (let i = 0; i < 5; i++) {
        const candidate = resolve(curr, "release/python/cli/agentguard");
        if (existsSync(candidate)) {
          found = candidate;
          break;
        }
        const parent = resolve(curr, "..");
        if (parent === curr) break;
        curr = parent;
      }
      this.cliPath = found || "agentguard";
    }

    this.dbPath = options.dbPath
      ? resolve(options.dbPath)
      : resolve(this.workspaceDir, ".agentguard/graph.db");
  }

  /**
   * Run CLI command asynchronously
   */
  public async runCommand(args: string[]): Promise<string> {
    try {
      const { stdout } = await execFileAsync(this.cliPath, args, {
        cwd: this.workspaceDir,
      });
      return stdout.trim();
    } catch (err: any) {
      const errMsg = err.stderr || err.stdout || err.message;
      throw new Error(`[AgentGuard CLI Error] ${errMsg}`);
    }
  }

  /**
   * Run CLI command synchronously
   */
  public runCommandSync(args: string[]): string {
    try {
      return execFileSync(this.cliPath, args, {
        cwd: this.workspaceDir,
        encoding: "utf-8",
      }).trim();
    } catch (err: any) {
      const errMsg = err.stderr || err.stdout || err.message;
      throw new Error(`[AgentGuard CLI Error] ${errMsg}`);
    }
  }

  /**
   * Initialize workspace layout (.agentguard/, AGENTS.md, git hooks)
   */
  public async init(noHooks: boolean = false): Promise<string> {
    const args = ["init", "--dir", this.workspaceDir];
    if (noHooks) args.push("--no-hooks");
    return await this.runCommand(args);
  }

  /**
   * Sync workspace files into Quad-Graph substrate
   */
  public async sync(): Promise<string> {
    return await this.runCommand(["sync", "--dir", this.workspaceDir]);
  }

  /**
   * Synthesize zero-prompt-tax system prompt for a target role
   */
  public async synthesizePrompt(roleId: string, scope?: string): Promise<string> {
    const args = ["prompt", "--role", roleId, "--db", this.dbPath];
    if (scope) args.push("--scope", scope);
    return await this.runCommand(args);
  }

  /**
   * Enforce pre-execution RBAC tool security gate
   */
  public async enforceGate(roleId: string, toolName: string): Promise<SecurityGateResult> {
    try {
      await this.runCommand([
        "gate",
        "--role",
        roleId,
        "--tool",
        toolName,
        "--db",
        this.dbPath,
      ]);
      return { allowed: true, roleId, toolName, details: "Security Gate PASSED" };
    } catch (err: any) {
      return {
        allowed: false,
        roleId,
        toolName,
        error: err.message,
        details: "Security Gate DENIED",
      };
    }
  }

  /**
   * Validate graph topology, priority tier DAGs, and cycle detection
   */
  public async validate(): Promise<ValidationReport> {
    const output = await this.runCommand(["validate", "--db", this.dbPath, "--json"]);
    try {
      return JSON.parse(output);
    } catch {
      return {
        is_valid: !output.includes("Graph Valid: False"),
        total_nodes: 0,
        total_edges: 0,
        detected_cycles: [],
        dangling_edges: [],
      };
    }
  }

  /**
   * Execute full Hath0r Quality Gates suite
   */
  public async runQualityGate(): Promise<{ success: boolean; output: string }> {
    try {
      const output = await this.runCommand(["quality-gate", "--dir", this.workspaceDir, "--db", this.dbPath]);
      return { success: true, output };
    } catch (err: any) {
      return { success: false, output: err.message };
    }
  }
}
