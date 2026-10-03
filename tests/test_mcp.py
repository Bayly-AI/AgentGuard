"""Unit tests for Model Context Protocol (MCP) server in AgentGuard."""

import json
import unittest

from agentguard.mcp import AgentGuardMCPServer


class TestAgentGuardMCPServer(unittest.TestCase):
    def setUp(self):
        self.server = AgentGuardMCPServer(workspace_dir=".")

    def test_get_tools_list(self):
        tools = self.server.get_tools_list()
        self.assertEqual(len(tools), 5)
        names = [t["name"] for t in tools]
        self.assertIn("agentguard_gate", names)
        self.assertIn("agentguard_prompt", names)
        self.assertIn("agentguard_taguchi", names)
        self.assertIn("agentguard_finops", names)
        self.assertIn("agentguard_quality_gate", names)

    def test_handle_taguchi_tool_call(self):
        res_str = self.server.handle_tool_call(
            "agentguard_taguchi",
            {"snr_values": [10.0, 12.0, 8.0], "snr_type": "smaller_the_better"},
        )
        res = json.loads(res_str)
        self.assertIn("snr_db", res)

    def test_handle_finops_tool_call(self):
        res_str = self.server.handle_tool_call(
            "agentguard_finops",
            {"action": "histogram", "bins": 5},
        )
        res = json.loads(res_str)
        self.assertIn("total_records", res)


if __name__ == "__main__":
    unittest.main()
