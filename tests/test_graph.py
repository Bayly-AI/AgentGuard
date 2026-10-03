"""Unit tests for AgentGuard Quad-Graph core and storage."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from agentguard.core.graph import AgentGuardGraph
from agentguard.core.models import (
    AgentGraphEdge,
    AgentGraphNode,
    AgentGraphPlane,
    RuleConflictError,
    RuleCycleError,
    RulePriority,
)


class TestAgentGuardGraph(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_graph.db"
        self.graph = AgentGuardGraph(db_path=self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_node_and_edge_addition(self):
        node = AgentGraphNode(
            id="doc:arch",
            plane=AgentGraphPlane.KNOWLEDGE.value,
            type="document",
            label="Architecture Overview",
            content="System architecture specification"
        )
        self.graph.add_node(node)
        self.assertIn("doc:arch", self.graph.nodes)

        edge = AgentGraphEdge(
            source="doc:arch",
            target="tool:view_file",
            relation="AUTHORIZES_TOOL",
            plane=AgentGraphPlane.RULES.value
        )
        self.graph.add_edge(edge)
        self.assertEqual(len(self.graph.edges), 1)

    def test_role_registration_and_resolution(self):
        self.graph.register_role(
            role_id="architect",
            role_name="Systems Architect",
            scope="root",
            permitted_tools=["view_file", "search_web"],
            forbidden_tools=["force_git_push"]
        )

        self.graph.register_role(
            role_id="developer",
            role_name="Software Engineer",
            scope="root",
            permitted_tools=["replace_file_content", "run_command"],
            forbidden_tools=["drop_database"],
            parent_role_id="architect"
        )

        self.graph.register_rule(
            rule_id="rule_001",
            title="TDD Discipline Rule",
            content="Always write unit tests first.",
            priority=RulePriority.REPO_STANDARD,
            target_scope="root",
            governs_roles=["architect", "developer"]
        )

        resolved = self.graph.resolve_role("developer")
        self.assertEqual(resolved.role_id, "developer")
        self.assertIn("architect", resolved.lineage_path[1])
        self.assertIn("view_file", resolved.authorized_tools)
        self.assertIn("replace_file_content", resolved.authorized_tools)
        self.assertIn("force_git_push", resolved.forbidden_tools)
        self.assertEqual(len(resolved.active_rules), 1)

    def test_cycle_detection(self):
        self.graph.register_role(role_id="role_a", role_name="Role A", parent_role_id="role_b")
        self.graph.register_role(role_id="role_b", role_name="Role B", parent_role_id="role_a")

        with self.assertRaises(RuleCycleError):
            self.graph.resolve_role("role_a")

    def test_bm25_query(self):
        node1 = AgentGraphNode(
            id="doc:security",
            plane=AgentGraphPlane.KNOWLEDGE.value,
            type="document",
            label="Security Policies",
            content="Authentication, OAuth2 tokens, and secret masking rules."
        )
        node2 = AgentGraphNode(
            id="doc:database",
            plane=AgentGraphPlane.KNOWLEDGE.value,
            type="document",
            label="Database Schema",
            content="PostgreSQL tables, indexes, and primary keys."
        )
        self.graph.add_node(node1)
        self.graph.add_node(node2)

        results = self.graph.query("OAuth2 secret tokens")
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0].node.id, "doc:security")

    def test_agentgraph_alias_and_init(self):
        from agentguard import AgentGraph, AgentGuardGraph
        self.assertIs(AgentGraph, AgentGuardGraph)

        temp_workspace = Path(self.temp_dir.name) / "agentgraph_init_workspace"
        graph = AgentGraph.init(workspace_dir=temp_workspace, no_hooks=True)
        self.assertTrue((temp_workspace / ".agentguard").exists())
        self.assertTrue((temp_workspace / "AGENTS.md").exists())
        self.assertGreater(len(graph.nodes), 0)


if __name__ == "__main__":
    unittest.main()
