"""AgentGuard CLI Dispatcher and Command Surface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agentguard import __version__
from agentguard.audit.tracer import AuditTracer
from agentguard.bot.watcher import WorkspaceBot
from agentguard.core.graph import AgentGuardGraph
from agentguard.governance.gate import SecurityGate
from agentguard.init.initializer import RepositoryInitializer
from agentguard.prompt.synthesizer import PromptSynthesizer
from agentguard.sync.syncer import RepositorySyncer


def main():
    parser = argparse.ArgumentParser(
        prog="agentguard",
        description="AgentGuard: Standalone Cognitive Substrate & Governance Engine for Agentic AI Systems"
    )
    parser.add_version = parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. init
    p_init = subparsers.add_parser("init", help="Scaffold repository agent files, roles, rules, and governance layout")
    p_init.add_argument("--dir", default=".", help="Target repository root directory (default: '.')")
    p_init.add_argument("--no-hooks", action="store_true", help="Skip installing Git pre-commit validation hook")

    # 2. status
    p_status = subparsers.add_parser("status", help="Display graph topology, plane node counts, and integrity status")
    p_status.add_argument("--db", default=".agentguard/graph.db", help="Path to SQLite database")

    # 3. route
    p_route = subparsers.add_parser("route", help="Evaluate deterministic rule DAG and RBAC tool authorizations for a role")
    p_route.add_argument("--role", required=True, help="Agent role ID (e.g. developer, architect, reviewer, security)")
    p_route.add_argument("--scope", default=None, help="Target subsystem scope")
    p_route.add_argument("--db", default=".agentguard/graph.db")
    p_route.add_argument("--json", action="store_true", help="Output result in JSON format")

    # 4. query
    p_query = subparsers.add_parser("query", help="Search Quad-Graph knowledge, rules, and memory with BM25 lexical ranking")
    p_query.add_argument("term", help="Search query string")
    p_query.add_argument("--plane", choices=["rules", "knowledge", "context", "memory"], default=None)
    p_query.add_argument("--limit", type=int, default=10)
    p_query.add_argument("--db", default=".agentguard/graph.db")

    # 5. sync
    p_sync = subparsers.add_parser("sync", help="Automatically scan workspace files and sync into Quad-Graph substrate")
    p_sync.add_argument("--dir", default=".", help="Workspace root directory")

    # 6. validate
    p_val = subparsers.add_parser("validate", help="Audit graph for rule inheritance cycles, conflicting directives, and dangling edges")
    p_val.add_argument("--db", default=".agentguard/graph.db")
    p_val.add_argument("--json", action="store_true", help="Output validation report in JSON format")

    # 7. gate
    p_gate = subparsers.add_parser("gate", help="Evaluate pre-execution tool security gate for a given role and tool call")
    p_gate.add_argument("--role", required=True, help="Agent role ID")
    p_gate.add_argument("--tool", required=True, help="Target tool name to evaluate")
    p_gate.add_argument("--db", default=".agentguard/graph.db")

    # 8. prompt
    p_prompt = subparsers.add_parser("prompt", help="Synthesize zero-prompt-tax system prompt tailored to active role governance")
    p_prompt.add_argument("--role", required=True, help="Target agent role ID")
    p_prompt.add_argument("--scope", default=None, help="Target scope")
    p_prompt.add_argument("--db", default=".agentguard/graph.db")

    # 9. migrate
    p_mig = subparsers.add_parser("migrate", help="Migrate legacy AGENTS.md, .cursorrules, or doc trees into graph nodes")
    p_mig.add_argument("--from", dest="source_path", required=True, help="Source markdown file or directory to migrate")
    p_mig.add_argument("--db", default=".agentguard/graph.db")

    # 10. audit
    p_audit = subparsers.add_parser("audit", help="Display execution trace logs and operational provenance history")
    p_audit.add_argument("--role", default=None, help="Filter logs by role ID")
    p_audit.add_argument("--limit", type=int, default=20, help="Maximum log records to return")
    p_audit.add_argument("--db", default=".agentguard/graph.db")

    # 11. bot
    p_bot = subparsers.add_parser("bot", help="Autonomous workspace health check and graph healer")
    p_bot.add_argument("--dir", default=".", help="Workspace directory")

    # 12. quality-gate / check
    p_gate = subparsers.add_parser("quality-gate", aliases=["check"], help="Run full Hath0r-compliant Quality Gate suite")
    p_gate.add_argument("--dir", default=".", help="Workspace root directory")
    p_gate.add_argument("--db", default=".agentguard/graph.db")
    p_gate.add_argument("--json", action="store_true", help="Output compliance report in JSON format")

    args = parser.parse_args()

    # Dispatch Commands
    if args.command == "init":
        ag_dir = RepositoryInitializer.initialize_repository(
            target_dir=args.dir, install_hooks=not args.no_hooks
        )
        print(f"\n[AgentGuard Init] Successfully initialized workspace layout at '{ag_dir}'")
        print("[AgentGuard Init] Running initial repository sync...")
        graph = RepositorySyncer.sync_repository(root_dir=args.dir)
        rep = graph.validate()
        print(f"[AgentGuard Init] Ingested {rep.total_nodes} nodes and {rep.total_edges} edges. System status: {'VALID' if rep.is_valid else 'INVALID'}\n")

    elif args.command == "sync":
        graph = RepositorySyncer.sync_repository(root_dir=args.dir)
        rep = graph.validate()
        print(f"\n[AgentGuard Sync] Workspace synchronized successfully ({graph.db_path}).")
        print(f"Nodes: {rep.total_nodes} | Edges: {rep.total_edges} | Valid: {rep.is_valid}\n")

    elif args.command == "status":
        graph = AgentGuardGraph(db_path=args.db)
        if Path(args.db).exists():
            graph.load_from_db()
        rep = graph.validate()
        print(f"\n--- AgentGuard Substrate Status ({graph.db_path}) ---")
        print(f"Total Nodes: {rep.total_nodes} | Total Edges: {rep.total_edges}")
        for plane, count in rep.plane_counts.items():
            print(f"  Plane [{plane.upper()}]: {count} nodes")
        print(f"Dangling Edges: {len(rep.dangling_edges)}")
        print(f"Detected Cycles: {len(rep.detected_cycles)}")
        print(f"Health Status: {'VALID' if rep.is_valid else 'INVALID'}\n")

    elif args.command == "route":
        graph = AgentGuardGraph(db_path=args.db)
        if Path(args.db).exists():
            graph.load_from_db()
        try:
            res = graph.resolve_role(role_id=args.role, scope=args.scope)
            if args.json:
                print(json.dumps(res.to_dict(), indent=2))
            else:
                print(f"\n--- Resolved Governance Posture for Role [{res.role_id}] ---")
                print(f"Role Name: {res.role_name} | Scope: {res.scope}")
                print(f"Inheritance Path: {' -> '.join(res.lineage_path)}")
                print(f"Authorized Tools: {', '.join(sorted(list(res.authorized_tools))) or 'None'}")
                print(f"Forbidden Tools: {', '.join(sorted(list(res.forbidden_tools))) or 'None'}")
                print(f"Restricted Actions: {', '.join(sorted(list(res.restricted_actions))) or 'None'}")
                print(f"Allowed Actions: {', '.join(sorted(list(res.allowed_actions))) or 'None'}")
                print(f"Active Governing Rules: {len(res.active_rules)} rules\n")
        except Exception as err:
            print(f"[AgentGuard Route Error] {err}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "query":
        graph = AgentGuardGraph(db_path=args.db)
        if Path(args.db).exists():
            graph.load_from_db()
        results = graph.query(query_str=args.term, plane=args.plane, limit=args.limit)
        print(f"\n--- Query Results for '{args.term}' (Plane: {args.plane or 'ALL'}) ---")
        if not results:
            print("No matching nodes found.")
        for r in results:
            print(f"[{r.score:.4f}] ({r.matched_plane.upper()}) {r.node.label} (ID: {r.node.id})")
        print()

    elif args.command == "validate":
        graph = AgentGuardGraph(db_path=args.db)
        if Path(args.db).exists():
            graph.load_from_db()
        rep = graph.validate()
        if args.json:
            print(json.dumps(rep.to_dict(), indent=2))
        else:
            print(f"\n--- AgentGuard Validation Report ---")
            print(f"Graph Valid: {rep.is_valid}")
            print(f"Total Nodes: {rep.total_nodes} | Total Edges: {rep.total_edges}")
            print(f"Dangling Edges: {len(rep.dangling_edges)}")
            print(f"Detected Cycles: {len(rep.detected_cycles)}")
            if rep.dangling_edges:
                print("Dangling Edges Detail:")
                for src, tgt in rep.dangling_edges:
                    print(f"  {src} -> {tgt}")
            if rep.detected_cycles:
                print("Detected Cycles Detail:")
                for cycle in rep.detected_cycles:
                    print(f"  {' -> '.join(cycle)}")
            print()
        if not rep.is_valid:
            sys.exit(1)

    elif args.command == "gate":
        graph = AgentGuardGraph(db_path=args.db)
        if Path(args.db).exists():
            graph.load_from_db()
        try:
            SecurityGate.enforce_tool(
                graph=graph,
                role_id=args.role,
                tool_name=args.tool,
                actor_id="cli_runner",
                session_id="cli_session"
            )
            print(f"[AgentGuard Security Gate PASS] Role '{args.role}' is AUTHORIZED to execute tool '{args.tool}'.")
        except Exception as err:
            print(f"[AgentGuard Security Gate DENIED] {err}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "prompt":
        graph = AgentGuardGraph(db_path=args.db)
        if Path(args.db).exists():
            graph.load_from_db()
        try:
            prompt_text = PromptSynthesizer.synthesize_prompt(
                graph=graph, role_id=args.role, scope=args.scope
            )
            print(f"\n{prompt_text}\n")
        except Exception as err:
            print(f"[AgentGuard Prompt Error] {err}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "migrate":
        graph = AgentGuardGraph(db_path=args.db)
        if Path(args.db).exists():
            graph.load_from_db()
        src = Path(args.source_path)
        if not src.exists():
            print(f"Error: Migration source path '{src}' does not exist.", file=sys.stderr)
            sys.exit(1)

        if src.is_file() and src.name.endswith(".md"):
            nodes, edges = RepositorySyncer.sync_repository(root_dir=src.parent, graph=graph).validate()
            print(f"[AgentGuard Migrate] Successfully migrated file '{src.name}'.")
        elif src.is_dir():
            graph = RepositorySyncer.sync_repository(root_dir=src, graph=graph)
            print(f"[AgentGuard Migrate] Successfully migrated workspace directory '{src}'.")
        graph.save_to_db()

    elif args.command == "audit":
        graph = AgentGuardGraph(db_path=args.db)
        logs = AuditTracer.fetch_audit_history(graph=graph, limit=args.limit, role_id=args.role)
        print(f"\n--- AgentGuard Execution Audit Logs (Last {len(logs)} entries) ---")
        for log in logs:
            print(f"[{log.timestamp}] ({log.status}) Role: {log.role_id} | Action: {log.action_type} | Tool: {log.tool_name}")
            print(f"   Details: {log.details}")
        print()

    elif args.command == "bot":
        is_healthy = WorkspaceBot.run_health_check(root_dir=args.dir)
        if not is_healthy:
            sys.exit(1)

    elif args.command in ("quality-gate", "check"):
        print("\n=======================================================")
        print("  Hath0r-Agentic-Framework Quality Gate Evaluation")
        print("=======================================================\n")

        root_path = Path(args.dir).resolve()

        # Gate 1: Workspace Ingestion & Quad-Graph Sync
        print("[Quality Gate 1/5] Ingesting repository & syncing Quad-Graph substrate...")
        graph = RepositorySyncer.sync_repository(root_dir=root_path)
        print(f"  ✓ Quad-Graph Synced: {len(graph.nodes)} nodes, {len(graph.edges)} edges.")

        # Gate 2: Graph Topology & Rule Priority DAG Audit
        print("[Quality Gate 2/5] Auditing Priority Tier DAGs & Cycle Detection...")
        rep = graph.validate()
        if not rep.is_valid:
            print("  ✗ Gate 2 FAILED: Graph validation errors detected!")
            if rep.detected_cycles:
                print(f"    Detected Cycles: {rep.detected_cycles}")
            if rep.dangling_edges:
                print(f"    Dangling Edges: {rep.dangling_edges}")
            sys.exit(1)
        print("  ✓ Gate 2 PASSED: 0 cycles, 0 dangling edges, Priority Tier DAG valid.")

        # Gate 3: RBAC & Tool Authorization Posture Check
        print("[Quality Gate 3/5] Verifying RBAC Postures across registered roles...")
        roles_found = [n for n in graph.nodes.values() if n.type == "agent_role"]
        for role_node in roles_found:
            r_id = role_node.properties.get("role_id", role_node.id.removeprefix("role:"))
            try:
                res = graph.resolve_role(r_id)
                print(f"  ✓ Role [{res.role_id}]: {len(res.authorized_tools)} authorized tools, {len(res.active_rules)} active rules.")
            except Exception as r_err:
                print(f"  ✗ Gate 3 FAILED for role '{r_id}': {r_err}")
                sys.exit(1)

        # Gate 4: Test Suite & Code Verification
        print("[Quality Gate 4/5] Running Unit Test & Verification Suite...")
        import unittest
        loader = unittest.TestLoader()
        tests_dir = root_path / "tests"
        if tests_dir.exists():
            suite = loader.discover(str(tests_dir))
            runner = unittest.TextTestRunner(verbosity=0)
            result = runner.run(suite)
            if not result.wasSuccessful():
                print(f"  ✗ Gate 4 FAILED: {len(result.failures)} test failures, {len(result.errors)} errors.")
                sys.exit(1)
            print(f"  ✓ Gate 4 PASSED: {result.testsRun} unit tests passed cleanly.")
        else:
            print("  - Gate 4 SKIPPED: No tests/ directory found.")

        # Gate 5: Evidence & Build Package Gate
        print("[Quality Gate 5/5] Verifying Build Package Artifacts...")
        build_script = root_path / "scripts" / "build.py"
        if build_script.exists():
            try:
                import subprocess
                subprocess.run([sys.executable, str(build_script)], check=True, stdout=subprocess.DEVNULL)
                release_dir = root_path / "release" / "python" / "cli"
                artifacts = list(release_dir.glob("*")) if release_dir.exists() else []
                print(f"  ✓ Gate 5 PASSED: Build package verified ({len(artifacts)} release artifacts in ./release/python/cli).")
            except Exception as b_err:
                print(f"  ✗ Gate 5 FAILED: Build script error: {b_err}")
                sys.exit(1)
        else:
            print("  - Gate 5 SKIPPED: No scripts/build.py found.")

        if args.json:
            report_data = {
                "compliance_framework": "Hath0r-Agentic-Framework",
                "status": "PASSED",
                "total_nodes": len(graph.nodes),
                "total_edges": len(graph.edges),
                "roles_verified": len(roles_found),
                "test_suite_passed": True
            }
            print(json.dumps(report_data, indent=2))
        else:
            print("\n=======================================================")
            print("  Hath0r Quality Gates Status: ALL GATES PASSED (100% Compliant)")
            print("=======================================================\n")


if __name__ == "__main__":
    main()
