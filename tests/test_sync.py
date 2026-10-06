"""Unit tests for Markdown parser, Python AST code parser, and workspace syncer."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from agentguard.core.graph import AgentGuardGraph
from agentguard.init.initializer import RepositoryInitializer
from agentguard.sync.code_parser import CodeASTParser
from agentguard.sync.md_parser import MarkdownParser
from agentguard.sync.syncer import RepositorySyncer


class TestSyncAndParsers(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.root_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_markdown_parser(self):
        md_file = self.root_path / "AGENTS.md"
        md_file.write_text(
            "# System Guidelines\n\n"
            "## 1. System Invariants\n"
            "- **CR-ORG-001:** No direct git push to main.\n"
            "- **CR-ORG-002:** Destructive database wipe prohibited.\n\n"
            "## 2. References\n"
            "See [Architecture Spec](docs/arch.md) for details.\n",
            encoding="utf-8"
        )

        nodes, edges = MarkdownParser.parse_agents_md(md_file)
        self.assertTrue(len(nodes) > 1)  # doc node + rule nodes
        rule_nodes = [n for n in nodes if n.type == "rule_policy"]
        self.assertEqual(len(rule_nodes), 2)

    def test_code_ast_parser(self):
        py_file = self.root_path / "sample.py"
        py_file.write_text(
            "class SampleClass:\n"
            "    '''Docstring for SampleClass.'''\n"
            "    def sample_method(self, x: int) -> int:\n"
            "        '''Docstring for sample_method.'''\n"
            "        return x + 1\n",
            encoding="utf-8"
        )

        nodes, edges = CodeASTParser.parse_python_file(py_file)
        self.assertTrue(len(nodes) >= 3)  # module, class, method
        class_nodes = [n for n in nodes if n.type == "code_class"]
        func_nodes = [n for n in nodes if n.type == "code_function"]

        self.assertEqual(len(class_nodes), 1)
        self.assertEqual(class_nodes[0].label, "Class SampleClass")
        self.assertEqual(len(func_nodes), 1)
        self.assertEqual(func_nodes[0].label, "SampleClass.sample_method")

    def test_repository_syncer(self):
        RepositoryInitializer.initialize_repository(target_dir=self.root_path, install_hooks=False)
        graph = AgentGuardGraph(db_path=self.root_path / ".agentguard" / "graph.db")

        # Create dummy python file in root_path
        (self.root_path / "app.py").write_text("def run_app(): pass", encoding="utf-8")

        graph = RepositorySyncer.sync_repository(root_dir=self.root_path, graph=graph)
        report = graph.validate()

        self.assertTrue(report.is_valid)
        self.assertTrue(report.total_nodes > 0)
        self.assertTrue(report.total_edges > 0)


if __name__ == "__main__":
    unittest.main()
