# AgentGuard CLI Command Surface Reference

> **Executable Command:** `agentguard` or `python3 -m agentguard`  
> **Version:** `1.0.0`  

---

## Command Overview

The `agentguard` CLI serves as the governed front door for repository initialization, rule routing, BM25 querying, continuous graph validation, dynamic prompt synthesis, pre-execution tool security gating, and workspace auditing.

| Subcommand | Description | Exit Codes |
| :--- | :--- | :--- |
| `agentguard init` | Scaffold repository `.agentguard/` directory layout, default rules, roles, and git pre-commit hook | 0 on success |
| `agentguard status` | Display graph topology, plane node counts, dangling edges, and system health status | 0 if valid |
| `agentguard route` | Evaluate deterministic rule DAG and RBAC tool authorizations for a target agent role | 0 on success, 1 on error |
| `agentguard query` | Search Quad-Graph knowledge, rules, and memory with Okapi BM25 ranking | 0 on success |
| `agentguard sync` | Ingest repository files (`AGENTS.md`, `.agentguard/`, `docs/`, `src/`) into SQLite database | 0 on success |
| `agentguard validate` | Audit graph for inheritance cycles, conflicting directives, and dangling edge references | 0 if valid, 1 if invalid |
| `agentguard gate` | Pre-execution RBAC tool authorization gate check for runtime agent integration | 0 if allowed, 1 if denied |
| `agentguard prompt` | Synthesize minimal, zero-prompt-tax system prompt tailored to active role governance | 0 on success, 1 on error |
| `agentguard migrate` | Ingest legacy `AGENTS.md`, `.cursorrules`, or doc trees into graph substrate | 0 on success |
| `agentguard audit` | Retrieve operational trace log history and execution provenance | 0 on success |
| `agentguard bot` | Autonomous workspace watcher and graph health checker | 0 if healthy, 1 if degraded |
| `agentguard quality-gate` | Execute full Hath0r-compliant Quality Gates suite (Sync, DAG Audit, RBAC, Unit Tests, Build Verification) | 0 if 100% compliant, 1 on failure |

---

## Detailed Subcommand Usage & Examples

### 1. `agentguard init`
Scaffolds `.agentguard/` directory structure, writes default JSON rule templates for Tiers 1-4, creates default role definitions (`architect`, `developer`, `reviewer`, `security`), creates `AGENTS.md` if missing, installs `.git/hooks/pre-commit`, and runs initial sync.

```bash
# Initialize current workspace
agentguard init

# Initialize specific directory without git hooks
agentguard init --dir ./my-project --no-hooks
```

---

### 2. `agentguard status`
Inspects graph topology, node breakdown across Planes (`RULES`, `KNOWLEDGE`, `CONTEXT`, `MEMORY`), edge density, and dangling edge status.

```bash
agentguard status
agentguard status --db .agentguard/graph.db
```

---

### 3. `agentguard route`
Resolves role ancestry lineage, authorized tools, forbidden tools, allowed/restricted actions, and active governing rules sorted by priority tier.

```bash
# Evaluate governance for developer role
agentguard route --role developer

# Output in JSON format for automated harnesses
agentguard route --role security --json
```

---

### 4. `agentguard query`
Performs Okapi BM25 lexical search over indexed knowledge nodes, rule policies, and memory entries.

```bash
agentguard query "secret masking API keys"
agentguard query "TDD discipline" --plane rules --limit 5
```

---

### 5. `agentguard sync`
Re-scans repository files, updates AST code nodes, ingests markdown documentation, and refreshes the SQLite database.

```bash
agentguard sync
agentguard sync --dir ./src
```

---

### 6. `agentguard validate`
Audits the graph substrate for rule cycles (`RuleCycleError`), priority collisions (`RuleConflictError`), or dangling target references. Suitable for CI/CD pipeline blocking.

```bash
agentguard validate
agentguard validate --json
```

---

### 7. `agentguard gate`
Evaluates whether a target agent role is authorized to execute a specific tool call before execution occurs.

```bash
# Check if developer role can call view_file (Passes)
agentguard gate --role developer --tool view_file

# Check if reviewer role can call replace_file_content (Denied with exit code 1)
agentguard gate --role reviewer --tool replace_file_content
```

---

### 8. `agentguard prompt`
Outputs a dynamically synthesized system prompt containing strictly active governing rules and authorized tool signatures (Zero-Prompt-Tax).

```bash
agentguard prompt --role developer
```

---

### 9. `agentguard audit`
Prints recent execution trace log history and gate evaluation records.

```bash
agentguard audit --limit 20
agentguard audit --role developer
```
