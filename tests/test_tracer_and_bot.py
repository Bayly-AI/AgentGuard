"""Unit tests for Audit Tracer and Workspace Bot watcher."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from agentguard.audit.tracer import AuditTracer
from agentguard.bot.watcher import WorkspaceBot
from agentguard.core.graph import AgentGuardGraph
from agentguard.init.initializer import RepositoryInitializer


class TestTracerAndBot(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.root_path = Path(self.temp_dir.name)
        self.db_path = self.root_path / "test_tracer.db"
        self.graph = AgentGuardGraph(db_path=self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_audit_tracer_recording_and_retrieval(self):
        rec1 = AuditTracer.record_trace(
            graph=self.graph,
            session_id="sess_01",
            actor_id="dev_user",
            role_id="developer",
            action_type="tool_execution",
            tool_name="view_file",
            status="SUCCESS",
            details="Viewed file AGENTS.md"
        )
        self.assertEqual(rec1.role_id, "developer")
        self.assertEqual(rec1.status, "SUCCESS")

        rec2 = AuditTracer.record_trace(
            graph=self.graph,
            session_id="sess_01",
            actor_id="dev_user",
            role_id="reviewer",
            action_type="tool_execution",
            tool_name="replace_file_content",
            status="DENIED",
            details="Role reviewer is forbidden from editing files."
        )

        logs = AuditTracer.fetch_audit_history(graph=self.graph, limit=10)
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[0].status, "DENIED")  # Most recent first

        filtered_logs = AuditTracer.fetch_audit_history(graph=self.graph, role_id="developer")
        self.assertEqual(len(filtered_logs), 1)
        self.assertEqual(filtered_logs[0].tool_name, "view_file")

    def test_workspace_bot_health_check(self):
        RepositoryInitializer.initialize_repository(target_dir=self.root_path, install_hooks=False)
        is_healthy = WorkspaceBot.run_health_check(root_dir=self.root_path)
        self.assertTrue(is_healthy)


if __name__ == "__main__":
    unittest.main()
