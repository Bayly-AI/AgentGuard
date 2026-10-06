"""Default file templates and JSON schema definitions for repository initialization."""

from __future__ import annotations

DEFAULT_CONFIG_JSON = """{
  "project_name": "AgentGuard Governed Workspace",
  "version": "1.0.0",
  "db_path": ".agentguard/graph.db",
  "scan_directories": [
    "AGENTS.md",
    ".agentguard/rules",
    ".agentguard/agents",
    ".agentguard/knowledge",
    "docs",
    "src"
  ],
  "rules_priority_order": [
    "10_org_invariants.json",
    "20_repo_standards.json",
    "30_subsystem_rules.json",
    "40_role_guidelines.json"
  ],
  "pre_commit_hook": true,
  "zero_prompt_tax": true
}
"""

ORG_INVARIANTS_JSON = """[
  {
    "id": "cr_org_001_no_direct_push",
    "title": "Strict Main Branch Push Lock",
    "priority": 4,
    "target_scope": "root",
    "restricted_actions": ["direct_git_push_main", "force_git_push"],
    "content": "No agent or human automated script may perform direct git push to main or production release branches. All changes must go through pull request verification and code review."
  },
  {
    "id": "cr_org_002_no_data_deletion",
    "title": "Database Drop Protection",
    "priority": 4,
    "target_scope": "root",
    "restricted_actions": ["drop_database", "truncate_tables", "delete_production_s3"],
    "content": "Destructive database operations and bucket wipe actions are strictly forbidden across all operational agent roles."
  },
  {
    "id": "cr_org_003_secret_sanitization",
    "title": "Strict Secret Masking",
    "priority": 4,
    "target_scope": "root",
    "allowed_actions": ["mask_credentials", "use_vault_broker"],
    "content": "API keys, private tokens, and credentials must never be written to logs, prompts, or commit messages."
  }
]
"""

REPO_STANDARDS_JSON = """[
  {
    "id": "cr_repo_001_tdd_discipline",
    "title": "Test-Driven Development Standard",
    "priority": 3,
    "target_scope": "root",
    "allowed_actions": ["run_unit_tests", "write_test_first"],
    "content": "All non-trivial code modifications must be accompanied by unit tests written prior to implementation or alongside refactoring."
  },
  {
    "id": "cr_repo_002_lint_and_build",
    "title": "Clean Build & Lint Gate",
    "priority": 3,
    "target_scope": "root",
    "allowed_actions": ["verify_lint", "run_build"],
    "content": "All code edits must compile cleanly and pass static analysis checks without swallowing or suppressing linter warnings."
  }
]
"""

SUBSYSTEM_RULES_JSON = """[
  {
    "id": "cr_subsys_001_api_versioning",
    "title": "API Subsystem Backward Compatibility",
    "priority": 2,
    "target_scope": "api",
    "restricted_actions": ["break_api_contract"],
    "content": "Public API endpoints must preserve backward compatibility. Breaking schema changes require explicit version increment and deprecation spans."
  }
]
"""

ROLE_GUIDELINES_JSON = """[
  {
    "id": "cr_role_001_concise_synthesis",
    "title": "Concise Developer Synthesis",
    "priority": 1,
    "target_scope": "root",
    "allowed_actions": ["summarize_changes"],
    "content": "Provide concise, structured markdown updates. Avoid re-stating unchanged code or outputting full transcripts."
  }
]
"""

ROLE_ARCHITECT_JSON = """{
  "role_id": "architect",
  "role_name": "Systems Architect Agent",
  "scope": "root",
  "permitted_tools": ["view_file", "search_web", "query_graph", "read_url_content", "write_to_file"],
  "forbidden_tools": ["execute_prod_migration", "force_git_push"],
  "parent_role_id": null
}
"""

ROLE_DEVELOPER_JSON = """{
  "role_id": "developer",
  "role_name": "Software Engineering Agent",
  "scope": "root",
  "permitted_tools": ["view_file", "replace_file_content", "write_to_file", "run_command", "query_graph"],
  "forbidden_tools": ["force_git_push", "drop_database"],
  "parent_role_id": "architect"
}
"""

ROLE_REVIEWER_JSON = """{
  "role_id": "reviewer",
  "role_name": "Code Review & Security Auditor Agent",
  "scope": "root",
  "permitted_tools": ["view_file", "query_graph", "run_command"],
  "forbidden_tools": ["replace_file_content", "write_to_file", "force_git_push"],
  "parent_role_id": null
}
"""

ROLE_SECURITY_JSON = """{
  "role_id": "security",
  "role_name": "CISO Security Compliance Agent",
  "scope": "root",
  "permitted_tools": ["view_file", "query_graph", "validate_graph", "audit_logs"],
  "forbidden_tools": ["run_command", "replace_file_content", "write_to_file"],
  "parent_role_id": null
}
"""

AGENTS_MD_TEMPLATE = """# Repository Agent Policy & Governance (AGENTS.md)

> **Governed by AgentGuard Quad-Graph Substrate**
> **Scope:** Repository Root Standards & Role Definitions

---

## 1. System Invariants (Tier 4: ORG_INVARIANT)
- **CR-ORG-001:** No direct git push to `main` or production release branches.
- **CR-ORG-002:** Destructive database or bucket wipe commands are strictly prohibited.
- **CR-ORG-003:** Secrets, private keys, and environment tokens must be masked.

## 2. Repository Standards (Tier 3: REPO_STANDARD)
- **CR-REPO-001:** Test-Driven Development (TDD) discipline must be enforced for all logic modifications.
- **CR-REPO-002:** All changes must build cleanly and pass linter analysis prior to completion.

## 3. Active Agent Roles
- **Systems Architect (`role:architect`)**: System design, schema modeling, high-level planning.
- **Software Engineer (`role:developer`)**: Code implementation, test creation, bug fixing.
- **Code Reviewer (`role:reviewer`)**: Static analysis, PR evaluation, compliance audit.
- **Security Auditor (`role:security`)**: RBAC verification, credential masking, vulnerability scanning.

---
*Run `agentguard sync` to ingest this file into `.agentguard/graph.db`.*
"""

KNOWLEDGE_ARCH_MD = """# Workspace Architecture Overview

> **Plane:** KnowledgeGraph (`doc:architecture.md`)

This repository is governed by AgentGuard's Quad-Graph cognitive substrate.

## Subsystems
1. **Core Engine:** Quad-Graph data models, SQLite storage, Okapi BM25 lexical search.
2. **Governance:** Deterministic Rule Priority DAG, RBAC tool authorization, pre-execution gates.
3. **Repository Init & Sync:** Workspace scaffolding, markdown and code AST ingestion.
"""

PRE_COMMIT_HOOK_SCRIPT = """#!/bin/bash
# AgentGuard Pre-Commit Governance Audit Hook

echo "[AgentGuard] Running repository pre-commit governance audit..."

if command -v agentguard &> /dev/null; then
    agentguard validate
    exit_code=$?
elif command -v python3 &> /dev/null && [ -f "agentguard/cli.py" ]; then
    python3 -m agentguard validate
    exit_code=$?
else
    echo "[AgentGuard Warning] agentguard CLI not found in PATH. Skipping pre-commit gate."
    exit 0
fi

if [ $exit_code -ne 0 ]; then
    echo "[AgentGuard Error] Governance audit failed! Resolve DAG cycles or dangling edges before committing."
    exit 1
fi

echo "[AgentGuard] Pre-commit governance check passed cleanly."
exit 0
"""
