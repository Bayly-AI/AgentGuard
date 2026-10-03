"""Unit tests for RBAC, Security Gate, and Prompt Synthesizer."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from agentguard.core.graph import AgentGuardGraph
from agentguard.core.models import RBACPermissionError, RulePriority
from agentguard.governance.gate import SecurityGate
from agentguard.prompt.synthesizer import PromptSynthesizer


class TestRBACAndGate(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_rbac.db"
        self.graph = AgentGuardGraph(db_path=self.db_path)

        self.graph.register_role(
            role_id="developer",
            role_name="Software Engineer",
            scope="root",
            permitted_tools=["view_file", "write_to_file", "run_command"],
            forbidden_tools=["force_git_push", "drop_database"]
        )

        self.graph.register_rule(
            rule_id="org_001",
            title="Main Push Restriction",
            content="Direct push to main is forbidden.",
            priority=RulePriority.ORG_INVARIANT,
            target_scope="root",
            restricted_actions=["direct_git_push_main"]
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_security_gate_allowed_tool(self):
        res = SecurityGate.enforce_tool(
            graph=self.graph,
            role_id="developer",
            tool_name="view_file"
        )
        self.assertTrue(res)

    def test_security_gate_forbidden_tool(self):
        with self.assertRaises(RBACPermissionError):
            SecurityGate.enforce_tool(
                graph=self.graph,
                role_id="developer",
                tool_name="force_git_push"
            )

    def test_security_gate_unauthorized_tool(self):
        with self.assertRaises(RBACPermissionError):
            SecurityGate.enforce_tool(
                graph=self.graph,
                role_id="developer",
                tool_name="unregistered_dangerous_tool"
            )

    def test_prompt_synthesis(self):
        prompt = PromptSynthesizer.synthesize_prompt(self.graph, "developer")
        self.assertIn("Software Engineer", prompt)
        self.assertIn("view_file", prompt)
        self.assertIn("force_git_push", prompt)
        self.assertIn("Main Push Restriction", prompt)


if __name__ == "__main__":
    unittest.main()
