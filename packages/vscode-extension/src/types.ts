export type QuadPlane = "agents" | "rules" | "memory" | "code";

export interface GraphNode {
  id: string;
  label: string;
  plane: QuadPlane;
  node_type?: string;
  priority?: number;
  properties?: Record<string, any>;
}

export interface SecurityGateResult {
  role: string;
  tool: string;
  authorized: boolean;
  reason?: string;
  governing_rules?: string[];
}

export interface FinOpsMetrics {
  prompt_tokens_saved_pct: number;
  average_prompt_tokens: number;
  annual_savings_estimate: string;
  telemetry_records_count: number;
}

export interface ValidationReport {
  is_valid: boolean;
  cycle_count: number;
  cycles: string[][];
  dangling_edge_count: number;
  dangling_edges: any[];
  node_count: number;
  edge_count: number;
}
