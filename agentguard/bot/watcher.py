"""Autonomous workspace watcher and graph health monitoring daemon."""

from __future__ import annotations

from pathlib import Path

from agentguard.core.graph import AgentGuardGraph
from agentguard.sync.syncer import RepositorySyncer


class WorkspaceBot:
    """Monitors workspace changes, auto-syncs graph, and reports integrity issues."""

    @staticmethod
    def run_health_check(root_dir: Path | str = ".") -> bool:
        """Run graph sync and validate health."""
        root = Path(root_dir).resolve()
        ag_dir = root / ".agentguard"
        db_path = ag_dir / "graph.db" if ag_dir.exists() else ".agentguard/graph.db"

        graph = AgentGuardGraph(db_path=db_path)
        graph = RepositorySyncer.sync_repository(root_dir=root, graph=graph)
        report = graph.validate()

        print(f"\n--- AgentGuard Bot Workspace Audit ({root.name}) ---")
        print(f"Total Nodes: {report.total_nodes} | Total Edges: {report.total_edges}")
        for plane, count in report.plane_counts.items():
            print(f"  Plane [{plane.upper()}]: {count} nodes")
        print(f"Dangling Edges: {len(report.dangling_edges)}")
        print(f"Detected Cycles: {len(report.detected_cycles)}")
        print(f"Health Status: {'HEALTHY' if report.is_valid else 'DEGRADED'}\n")

        return report.is_valid
