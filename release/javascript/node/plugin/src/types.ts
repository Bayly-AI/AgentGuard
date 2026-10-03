/**
 * AgentGuard Node.js Plugin Types and Interfaces.
 */

export type RulePriority = 1 | 2 | 3 | 4;

export interface AgentGraphNode {
  id: string;
  plane: "rules" | "knowledge" | "context" | "memory";
  type: string;
  label: string;
  content: string;
  properties: Record<string, any>;
  created_at?: string;
}

export interface AgentGraphEdge {
  source: string;
  target: string;
  relation: string;
  plane: "rules" | "knowledge" | "context" | "memory";
  weight?: number;
}

export interface SecurityGateResult {
  allowed: boolean;
  roleId: string;
  toolName: string;
  details?: string;
  error?: string;
}

export interface ValidationReport {
  is_valid: boolean;
  total_nodes: number;
  total_edges: number;
  detected_cycles: string[][];
  dangling_edges: AgentGraphEdge[];
}

export interface AuditEntry {
  timestamp: string;
  session_id: string;
  actor_id: string;
  role_id: string;
  action_type: string;
  tool_name: string;
  status: "SUCCESS" | "DENIED" | "FAILED";
  details: string;
}

export interface PluginOptions {
  cliPath?: string;
  dbPath?: string;
  workspaceDir?: string;
}
