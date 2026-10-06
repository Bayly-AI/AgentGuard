"""Unit tests for repository initialization and sync."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from agentguard.init.initializer import RepositoryInitializer
from agentguard.sync.syncer import RepositorySyncer


class TestInitializerAndSync(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.root_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_repository_initialization(self):
        ag_dir = RepositoryInitializer.initialize_repository(target_dir=self.root_path, install_hooks=False)
        self.assertTrue(ag_dir.exists())
        self.assertTrue((ag_dir / "config.json").exists())
        self.assertTrue((ag_dir / "rules" / "10_org_invariants.json").exists())
        self.assertTrue((ag_dir / "agents" / "developer.json").exists())
        self.assertTrue((self.root_path / "AGENTS.md").exists())

    def test_sync_ingestion(self):
        RepositoryInitializer.initialize_repository(target_dir=self.root_path, install_hooks=False)
        graph = RepositorySyncer.sync_repository(root_dir=self.root_path)

        rep = graph.validate()
        self.assertTrue(rep.is_valid)
        self.assertTrue(rep.total_nodes > 0)
        self.assertTrue(rep.total_edges > 0)

        resolved = graph.resolve_role("developer")
        self.assertEqual(resolved.role_id, "developer")
        self.assertIn("view_file", resolved.authorized_tools)


if __name__ == "__main__":
    unittest.main()
