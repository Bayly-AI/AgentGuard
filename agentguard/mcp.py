"""Model Context Protocol (MCP) Stdio JSON-RPC Server for AgentGuard."""

import json
import sys
from typing import Any, Dict

from agentguard.core.graph import AgentGuardGraph
from agentguard.governance.gate import SecurityGate
from agentguard.governance.taguchi import ArrayType, Factor, SNRType, TaguchiEngine, calculate_snr
from agentguard.prompt.synthesizer import PromptSynthesizer
from agentguard.telemetry.tokens import TokenTelemetry


class AgentGuardMCPServer:
    """Zero-dependency stdio JSON-RPC 2.0 MCP Server for Anthropic Claude Desktop & Claude Code."""

    def __init__(self, workspace_dir: str = "."):
        self.workspace_dir = workspace_dir
        self.db_path = f"{workspace_dir}/.agentguard/graph.db"

    def get_tools_list(self) -> list:
        return [
            {
                "name": "agentguard_gate",
                "description": "Pre-execution RBAC Security Gate check for AI agent tool execution authorization.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "role_id": {"type": "string", "description": "Active agent role (e.g. developer, reviewer, security, architect)"},
                        "tool_name": {"type": "string", "description": "Target tool name to execute (e.g. view_file, replace_file_content)"},
                    },
                    "required": ["role_id", "tool_name"],
                },
            },
            {
                "name": "agentguard_prompt",
                "description": "Synthesizes minimal zero-prompt-tax system prompt tailored for target agent role.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "role_id": {"type": "string", "description": "Active agent role"},
                        "scope": {"type": "string", "description": "Optional subsystem scope filter"},
                    },
                    "required": ["role_id"],
                },
            },
            {
                "name": "agentguard_taguchi",
                "description": "Taguchi Robust Design, Orthogonal Arrays (L4, L8, L9, L12, L18), and SNR Optimizer.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "array": {"type": "string", "enum": ["L4", "L8", "L9", "L12", "L18"], "default": "L9"},
                        "factors": {"type": "array", "items": {"type": "string"}, "description": "List of factor parameter names"},
                        "snr_values": {"type": "array", "items": {"type": "number"}, "description": "List of response float values for SNR calculation"},
                        "snr_type": {"type": "string", "enum": ["smaller_the_better", "larger_the_better", "nominal_the_best"], "default": "smaller_the_better"},
                    },
                },
            },
            {
                "name": "agentguard_finops",
                "description": "FinOps token telemetry recording, 90-day usage audits, and equal-width distribution histogram analytics.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["estimate", "record", "histogram", "check"], "default": "histogram"},
                        "prompt": {"type": "string", "description": "Prompt text for record action"},
                        "user_id": {"type": "string", "default": "default_user"},
                        "bins": {"type": "integer", "default": 10},
                    },
                },
            },
            {
                "name": "agentguard_quality_gate",
                "description": "Executes full Hath0r-compliant Quality Gates evaluation suite.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "dir": {"type": "string", "default": "."},
                    },
                },
            },
        ]

    def handle_tool_call(self, name: str, args: Dict[str, Any]) -> str:
        if name == "agentguard_gate":
            graph = AgentGuardGraph(db_path=self.db_path)
            try:
                graph.load_from_db()
                res = SecurityGate.enforce_tool(
                    graph=graph,
                    role_id=args.get("role_id", "developer"),
                    tool_name=args.get("tool_name", ""),
                )
                return json.dumps({"allowed": res.allowed, "role_id": res.role_id, "tool_name": res.tool_name, "reason": res.reason})
            except Exception as e:
                return json.dumps({"allowed": False, "error": str(e)})

        elif name == "agentguard_prompt":
            graph = AgentGuardGraph(db_path=self.db_path)
            try:
                graph.load_from_db()
                prompt = PromptSynthesizer.synthesize_prompt(
                    graph=graph,
                    role_id=args.get("role_id", "developer"),
                    scope=args.get("scope"),
                )
                return prompt
            except Exception as e:
                return f"Error synthesizing prompt: {str(e)}"

        elif name == "agentguard_taguchi":
            if "snr_values" in args and args["snr_values"]:
                vals = [float(v) for v in args["snr_values"]]
                stype = SNRType(args.get("snr_type", "smaller_the_better"))
                snr = calculate_snr(vals, snr_type=stype)
                return json.dumps({"snr_db": round(snr, 4), "snr_type": stype.value, "values": vals})
            else:
                array_t = ArrayType(args.get("array", "L9"))
                raw_factors = args.get("factors") or ["Factor_1", "Factor_2", "Factor_3"]
                factors = [Factor(name=str(f), levels=[1, 2] if array_t != ArrayType.L9 else [1, 2, 3]) for f in raw_factors]
                matrix = TaguchiEngine.generate_matrix(array_type=array_t, factors=factors)
                return json.dumps({"array_type": array_t.value, "factors": [f.name for f in factors], "runs": matrix})

        elif name == "agentguard_finops":
            from pathlib import Path
            telemetry = TokenTelemetry(workspace_dir=Path(self.workspace_dir))
            action = args.get("action", "histogram")
            if action == "estimate":
                est = telemetry.estimate(
                    prompt=args.get("prompt", ""),
                    completion=args.get("completion", ""),
                    tier=args.get("tier", "standard"),
                )
                return json.dumps(est)
            elif action == "record":
                rec = telemetry.record(
                    prompt=args.get("prompt", ""),
                    user_id=args.get("user_id", "default_user"),
                )
                return json.dumps(rec)
            elif action == "histogram":
                hist = telemetry.histogram(user_id=args.get("user_id"), bins_count=args.get("bins", 10))
                return json.dumps(hist)
            else:
                rep = telemetry.generate_report(user_id=args.get("user_id", "default_user"))
                return json.dumps(rep)

        elif name == "agentguard_quality_gate":
            graph = AgentGuardGraph(db_path=self.db_path)
            graph.sync_repository(root_dir=args.get("dir", "."))
            cycles, dangling = graph.validate_graph()
            return json.dumps({
                "status": "PASSED" if len(cycles) == 0 and len(dangling) == 0 else "DEGRADED",
                "cycles_count": len(cycles),
                "dangling_edges_count": len(dangling),
                "total_nodes": len(graph.nodes),
                "total_edges": len(graph.edges),
            })

        return f"Unknown tool name: {name}"

    def run_stdio(self):
        """Run the stdio JSON-RPC event loop."""
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue

            try:
                req = json.loads(line)
            except Exception:
                continue

            req_id = req.get("id")
            method = req.get("method")

            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "agentguard", "version": "1.0.0"},
                    },
                }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

            elif method == "notifications/initialized":
                pass  # Client notification, no response required

            elif method == "ping":
                resp = {"jsonrpc": "2.0", "id": req_id, "result": {}}
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": self.get_tools_list()},
                }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

            elif method == "tools/call":
                params = req.get("params", {})
                tool_name = params.get("name", "")
                tool_args = params.get("arguments", {})
                res_text = self.handle_tool_call(tool_name, tool_args)
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": res_text}],
                        "isError": False,
                    },
                }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

            else:
                if req_id is not None:
                    resp = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {"code": -32601, "message": f"Method not found: {method}"},
                    }
                    sys.stdout.write(json.dumps(resp) + "\n")
                    sys.stdout.flush()


def run_mcp_server(workspace_dir: str = "."):
    server = AgentGuardMCPServer(workspace_dir=workspace_dir)
    server.run_stdio()
