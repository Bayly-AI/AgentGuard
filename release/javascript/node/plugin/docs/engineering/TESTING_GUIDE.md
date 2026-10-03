# AgentGuard Testing & Quality Gate Verification Guide

> **Specification:** AgentGuard Testing & Quality Assurance Standard  
> **Version:** 1.0.0  
> **Test Framework:** Standard Library `unittest` (Zero External Dependencies)  

---

## 1. Testing Philosophy & Discipline

In alignment with **Tier 3 Repository Standards (`CR-REPO-001`)**, AgentGuard strictly enforces Test-Driven Development (TDD) discipline. Code modifications to core graph models, governance resolvers, or CLI dispatchers must be accompanied by unit tests.

### Key Verification Goals
1. **Zero Regression:** All 20 core unit tests must pass cleanly before any code is merged.
2. **Determinism:** Rule DAG evaluation, RBAC permission checks, and cycle detection must return 100% deterministic results across test runs.
3. **Isolation:** Tests execute against isolated temporary directories and SQLite database files (`tempfile.TemporaryDirectory()`).

---

## 2. Test Suite Structure (`tests/`)

The test suite is organized into six targeted modules:

```
tests/
├── test_graph.py           # Quad-Graph core, SQLite persistence, Okapi BM25, cycle detection
├── test_rbac.py            # RBAC Manager, priority tier DAG resolver, Security Gate
├── test_init.py            # Repository Initializer, scaffolding, template validation
├── test_sync.py            # Markdown policy parser, Python AST code parser, workspace syncer
├── test_tracer_and_bot.py  # Audit Tracer, session provenance, Workspace Bot watcher
└── test_cli.py             # CLI subcommand integration (init, route, prompt, gate, quality-gate)
```

---

## 3. Running Tests

### Running All Unit Tests
Run the standard Python unittest discovery:

```bash
python3 -m unittest discover tests
```

### Running Specific Test Modules
```bash
# Test Quad-Graph core
python3 -m unittest tests/test_graph.py

# Test RBAC and Security Gate
python3 -m unittest tests/test_rbac.py

# Test CLI integration
python3 -m unittest tests/test_cli.py
```

### Running Hath0r Quality Gates Suite
The Quality Gate command runs the full validation suite including sync, DAG cycle audits, RBAC posture checks, unit tests, and build package checks:

```bash
agentguard quality-gate
# or
python3 -m agentguard check
```

---

## 4. Writing New Unit Tests

When adding features or refactoring modules, follow this test pattern:

```python
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from agentguard.core.graph import AgentGuardGraph

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        self.graph = AgentGuardGraph(db_path=self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_feature_behavior(self):
        # Arrange
        # Act
        # Assert
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
```
