# AgentGuard Technical Reference & Developer Guide

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/Bayly-AI/AgentGuard)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](pyproject.toml)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero%20external-success.svg)](#)

> **AgentGuard** is a zero-dependency, standalone cognitive substrate and governance control plane for enterprise AI agent systems. This technical document provides setup instructions, developer how-to guides, architecture specifications, and an exhaustive function-by-function CLI reference.

---

## 📌 Quick Navigation

- [Installation & Setup](#-installation--setup)
- [Command Surface & Function Review](#-command-surface--function-review)
- [Developer How-To Guides](#-developer-how-to-guides)
  - [1. Initializing Repository Layout](#1-initializing-repository-layout)
  - [2. Writing Priority Tier Rules](#2-writing-priority-tier-rules)
  - [3. Pre-Execution Security Gate Integration](#3-pre-execution-security-gate-integration)
  - [4. Zero-Prompt-Tax System Prompt Synthesis](#4-zero-prompt-tax-system-prompt-synthesis)
  - [5. FastMCP & Model Context Protocol Integration](#5-fastmcp--model-context-protocol-integration)
- [System Architecture Deep Dive](#-system-architecture-deep-dive)
- [Testing & Quality Gate Verification](#-testing--quality-gate-verification)
- [Complete Documentation Suite](#-complete-documentation-suite)

---

## ⚙️ Installation & Setup

### Prerequisites
- **Operating System:** macOS, Linux, or Windows (WSL / POSIX)
- **Python Version:** Python 3.9 or higher
- **External Dependencies:** **Zero.** Built strictly using standard Python libraries (`sqlite3`, `ast`, `dataclasses`, `json`, `math`, `argparse`, `re`).

### Option 1: Install from Source (Editable Mode)

```bash
git clone https://github.com/Bayly-AI/AgentGuard.git
cd AgentGuard
pip install -e .
```

### Option 2: Install Node.js Plugin from NPM Registry

```bash
npm install agentguard-node-plugin
```

### Option 3: Run Standalone Binary directly (No Python Install Required)

The standalone executable CLI is packaged as a single zero-dependency binary in [./release/python/cli/agentguard](file:///Users/raybayly/Development/OpenSource/AgentGuard/release/python/cli/agentguard):

```bash
./release/python/cli/agentguard --version
```

---

## 🛠️ Command Surface & Function Review

The `agentguard` CLI provides 12 core subcommands for repository setup, governance routing, search, security gating, and quality assurance:

| Subcommand | Function Purpose & Review | Primary Options | Exit Code |
| :--- | :--- | :--- | :--- |
| **`init`** | Scaffolds `.agentguard/` layout, JSON rule templates for Tiers 1-4, default roles (`architect`, `developer`, `reviewer`, `security`), `AGENTS.md`, and Git pre-commit hooks. | `--dir <path>`, `--no-hooks` | `0` on success |
| **`status`** | Audits graph topology, node breakdown across Planes (`RULES`, `KNOWLEDGE`, `CONTEXT`, `MEMORY`), edge count, dangling edges, and health status. | `--db <path>` | `0` if valid |
| **`route`** | Resolves role ancestry lineage, authorized tools, forbidden tools, allowed/restricted actions, and active governing rules sorted by tier dominance. | `--role <id>`, `--scope <scope>`, `--json` | `0` on success |
| **`query`** | Searches Quad-Graph knowledge nodes, policies, and memory entries using Okapi BM25 lexical ranking ($k_1=1.5, b=0.75$). | `term`, `--plane <plane>`, `--limit <n>` | `0` on success |
| **`sync`** | Re-scans repository Markdown files (`AGENTS.md`, `docs/`) and Python AST source files, updating the SQLite graph. | `--dir <path>` | `0` on success |
| **`validate`** | Audits graph substrate for inheritance cycles (`RuleCycleError`), same-tier priority collisions (`RuleConflictError`), or dangling references. | `--db <path>`, `--json` | `0` if valid, `1` if broken |
| **`gate`** | Evaluates pre-execution RBAC tool security gate for a given role and tool call before runtime side effects occur. | `--role <id>`, `--tool <name>` | `0` if allowed, `1` if denied |
| **`prompt`** | Synthesizes minimal zero-prompt-tax system prompt containing strictly active rules and authorized tool signatures for target role. | `--role <id>`, `--scope <scope>` | `0` on success |
| **`migrate`** | Ingests legacy `AGENTS.md`, `.cursorrules`, or doc trees into graph substrate nodes. | `--from <path>` | `0` on success |
| **`audit`** | Retrieves operational trace log history and execution provenance records from SQLite `audit_logs` table. | `--role <id>`, `--limit <n>` | `0` on success |
| **`bot`** | Autonomous workspace health watcher daemon checking graph integrity and auto-syncing updates. | `--dir <path>` | `0` if healthy, `1` if degraded |
| **`quality-gate`** | Executes the 5 Hath0r Quality Gates (Sync, Priority Tier DAG Audit, RBAC Verification, Unit Tests, Build Artifacts) sequentially. | `--dir <path>`, `--json` | `0` if 100% compliant |

---

## 📖 Developer How-To Guides

### 1. Initializing Repository Layout

In any Git repository, run:

```bash
agentguard init
```

This generates the following directory structure:

```
my-repo/
├── AGENTS.md                         # Structured root repository agent policy
├── .git/hooks/pre-commit             # Automated pre-commit governance validation hook
└── .agentguard/                      # Governance directory
    ├── config.json                   # Scan and project configuration
    ├── graph.db                      # SQLite ACID Quad-Graph database
    ├── rules/                        # Tiered Rule Policy JSON Files (Tiers 1-4)
    ├── agents/                       # Agent Role Manifests (RBAC Tool Permissions)
    ├── knowledge/                    # Static Architecture Specs
    ├── memory/                       # Historical recall
    └── subsystems/                   # Scoped module rules
```

---

### 2. Writing Priority Tier Rules

Rules are structured as JSON files in `.agentguard/rules/`. Priority tiers enforce explicit dominance:

$$\text{Tier 4: ORG\_INVARIANT} \succ \text{Tier 3: REPO\_STANDARD} \succ \text{Tier 2: SUBSYSTEM\_RULE} \succ \text{Tier 1: ROLE\_GUIDELINE}$$

Example Tier 4 Organizational Invariant (`.agentguard/rules/10_org_invariants.json`):

```json
[
  {
    "id": "cr_org_001_no_direct_push",
    "title": "Strict Main Branch Push Lock",
    "priority": 4,
    "target_scope": "root",
    "restricted_actions": ["direct_git_push_main", "force_git_push"],
    "content": "No agent or human automated script may perform direct git push to main or production release branches."
  }
]
```

---

### 3. Pre-Execution Security Gate Integration

Wrap LLM tool invocation calls with `SecurityGate.enforce_tool()` to prevent unauthorized actions:

```python
from agentguard.core.graph import AgentGuardGraph
from agentguard.governance.gate import SecurityGate

# Load Quad-Graph substrate
graph = AgentGuardGraph(db_path=".agentguard/graph.db")
graph.load_from_db()

def dispatch_tool(role_id: str, tool_name: str, tool_args: dict):
    # Pre-execution RBAC Security Gate
    SecurityGate.enforce_tool(
        graph=graph,
        role_id=role_id,
        tool_name=tool_name,
        actor_id="agent_runner_v1",
        session_id="session_402"
    )
    # Execute tool safely if gate passes
    return run_tool_logic(tool_name, tool_args)
```

---

### 4. Zero-Prompt-Tax System Prompt Synthesis

Synthesize minimal, role-tailored system prompts on demand:

```python
from agentguard.prompt.synthesizer import PromptSynthesizer

# Synthesize prompt for developer role
system_prompt = PromptSynthesizer.synthesize_prompt(graph=graph, role_id="developer")
print(system_prompt)
```

---

### 5. FastMCP & Model Context Protocol Integration

Expose tools safely via MCP servers:

```python
from mcp.server.fastmcp import FastMCP
from agentguard.core.graph import AgentGuardGraph
from agentguard.governance.gate import SecurityGate

mcp_server = FastMCP("Governed-Agent-Server")
graph = AgentGuardGraph(db_path=".agentguard/graph.db")

@mcp_server.tool()
def execute_database_query(role_id: str, query: str) -> str:
    SecurityGate.enforce_tool(graph, role_id=role_id, tool_name="execute_database_query")
    return db_client.execute(query)
```

---

## 🧬 System Architecture Deep Dive

AgentGuard partitions entity nodes and relational edges across four canonical planes in a property graph backed by SQLite:

```
                  +-----------------------------------+
                  |      Quad-Graph Substrate         |
                  +-----------------------------------+
                  |  RulesGraph      | KnowledgeGraph |
                  |  ContextGraph    | MemoryGraph    |
                  +-----------------------------------+
```

- **RulesGraph:** Role ancestry DAGs, tool permissions, and priority policy directives.
- **KnowledgeGraph:** Repository documents, API contracts, and Python AST source nodes.
- **ContextGraph:** Ephemeral task sessions, spans, and tool execution logs.
- **MemoryGraph:** Long-term temporal recall, bitemporal validities (`valid_from`, `valid_to`), decisions, and reflections.

For full technical specifications, see [docs/engineering/ARCHITECTURE.md](docs/engineering/ARCHITECTURE.md).

---

## 🧪 Testing & Quality Gate Verification

### Run Unit Test Suite
```bash
python3 -m unittest discover tests
```

### Run Hath0r Quality Gates Check
```bash
agentguard quality-gate
```

---

## 📚 Complete Documentation Suite

- **Master Sitemap & Index:** [docs/INDEX.md](docs/INDEX.md)
- **Technical Architecture:** [docs/engineering/ARCHITECTURE.md](docs/engineering/ARCHITECTURE.md)
- **CLI Command Reference:** [docs/engineering/CLI_REFERENCE.md](docs/engineering/CLI_REFERENCE.md)
- **Repository Layout Standard:** [docs/engineering/REPO_ORGANIZATION.md](docs/engineering/REPO_ORGANIZATION.md)
- **Developer Integration Guide:** [docs/engineering/RUNTIME_INTEGRATION.md](docs/engineering/RUNTIME_INTEGRATION.md)
- **Migration Guide:** [docs/engineering/MIGRATION_GUIDE.md](docs/engineering/MIGRATION_GUIDE.md)
- **Hath0r Quality Gates Standard:** [docs/engineering/QUALITY_GATES.md](docs/engineering/QUALITY_GATES.md)
- **Testing Guide:** [docs/engineering/TESTING_GUIDE.md](docs/engineering/TESTING_GUIDE.md)
