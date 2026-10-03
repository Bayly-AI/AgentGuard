"""Integration unit tests for AgentGuard CLI command surface."""

import os
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestCLISurface(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.root_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _run_cli(self, args: list[str]) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(REPO_ROOT)
        cmd = [sys.executable, "-m", "agentguard"] + args
        return subprocess.run(cmd, cwd=self.root_path, capture_output=True, text=True, env=env)

    def test_cli_init_and_status(self):
        res_init = self._run_cli(["init", "--no-hooks"])
        self.assertEqual(res_init.returncode, 0, f"init failed: {res_init.stderr}")
        self.assertIn("Successfully initialized workspace layout", res_init.stdout)

        res_status = self._run_cli(["status"])
        self.assertEqual(res_status.returncode, 0, f"status failed: {res_status.stderr}")
        self.assertIn("Health Status: VALID", res_status.stdout)

    def test_cli_route_and_prompt(self):
        self._run_cli(["init", "--no-hooks"])

        res_route = self._run_cli(["route", "--role", "developer"])
        self.assertEqual(res_route.returncode, 0, f"route failed: {res_route.stderr}")
        self.assertIn("Software Engineering Agent", res_route.stdout)

        res_prompt = self._run_cli(["prompt", "--role", "developer"])
        self.assertEqual(res_prompt.returncode, 0, f"prompt failed: {res_prompt.stderr}")
        self.assertIn("Agent Governance Mandate", res_prompt.stdout)

    def test_cli_gate_pass_and_fail(self):
        self._run_cli(["init", "--no-hooks"])

        res_pass = self._run_cli(["gate", "--role", "developer", "--tool", "view_file"])
        self.assertEqual(res_pass.returncode, 0, f"gate pass failed: {res_pass.stderr}")

        res_fail = self._run_cli(["gate", "--role", "reviewer", "--tool", "replace_file_content"])
        self.assertNotEqual(res_fail.returncode, 0)
        self.assertIn("DENIED", res_fail.stderr)

    def test_cli_query_and_validate(self):
        self._run_cli(["init", "--no-hooks"])

        res_query = self._run_cli(["query", "TDD discipline"])
        self.assertEqual(res_query.returncode, 0, f"query failed: {res_query.stderr}")
        self.assertIn("Query Results", res_query.stdout)

        res_val = self._run_cli(["validate"])
        self.assertEqual(res_val.returncode, 0, f"validate failed: {res_val.stderr}")
        self.assertIn("Graph Valid: True", res_val.stdout)

    def test_cli_quality_gate(self):
        self._run_cli(["init", "--no-hooks"])

        res_qg = self._run_cli(["quality-gate"])
        self.assertEqual(res_qg.returncode, 0, f"quality-gate failed: {res_qg.stderr}")
        self.assertIn("Hath0r Quality Gates Status: ALL GATES PASSED", res_qg.stdout)


if __name__ == "__main__":
    unittest.main()
