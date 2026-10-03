"""Unit tests for FinOps Token Telemetry and Distribution Histogram in AgentGuard."""

import shutil
import tempfile
import unittest
from pathlib import Path

from agentguard.telemetry.tokens import TokenTelemetry


class TestTokenTelemetry(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.telemetry = TokenTelemetry(workspace_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_record_telemetry(self):
        rec = self.telemetry.record(
            prompt="Hello AgentGuard, please optimize this query.",
            user_id="raybayly",
            model="claude-3-5-sonnet",
            completion="Optimized query output",
        )
        self.assertIn("id", rec)
        self.assertGreater(rec["prompt_tokens"], 0)
        self.assertGreater(rec["completion_tokens"], 0)
        self.assertGreater(rec["cost_usd"], 0.0)

    def test_histogram_generation(self):
        # Record 20 entries with varying token lengths
        for i in range(1, 21):
            self.telemetry.record(
                prompt="Short prompt " * i,
                user_id="test_user",
                completion="Response " * i,
            )

        hist = self.telemetry.histogram(user_id="test_user", bins_count=5)
        self.assertEqual(hist["total_records"], 20)
        self.assertGreater(hist["total_tokens"], 0)
        self.assertEqual(len(hist["bins"]), 5)
        self.assertIn("stats", hist)
        self.assertIn("min", hist["stats"])
        self.assertIn("max", hist["stats"])
        self.assertIn("mean", hist["stats"])

    def test_generate_report(self):
        self.telemetry.record(prompt="Sample prompt for report", user_id="report_user")
        rep = self.telemetry.generate_report(user_id="report_user", days=90)
        self.assertTrue(rep["success"])
        self.assertEqual(rep["total_records"], 1)
        self.assertIn("ascii_histogram", rep)


if __name__ == "__main__":
    unittest.main()
