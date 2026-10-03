# Repository Layout & Agent File Organization Standard

> **Specification:** AgentGuard Repository Layout Standard  
> **Version:** 1.0.0  

---

## 1. Directory Structure Standard

When AgentGuard is initialized in a repository via `agentguard init`, it establishes a standard directory layout for organizing agent files, rules, role manifests, and subsystem governance:

```
my-repository/
├── AGENTS.md                         # Root repository agent policy and role manifest
├── .agentguard/                      # AgentGuard governance directory
│   ├── config.json                   # AgentGuard project & scan configuration
│   ├── graph.db                      # SQLite ACID Quad-Graph database
│   ├── rules/                        # Tiered Rule Policy JSON Files
│   │   ├── 10_org_invariants.json    # Tier 4: Non-bypassable organizational constraints
│   │   ├── 20_repo_standards.json    # Tier 3: Repository-wide build, test, and lint standards
│   │   ├── 30_subsystem_rules.json   # Tier 2: Subsystem & API compatibility rules
│   │   └── 40_role_guidelines.json   # Tier 1: Role guidelines & output formatting rules
│   ├── agents/                       # Agent Role Manifests (RBAC Tool Permissions)
│   │   ├── architect.json            # Systems Architect Agent role definition
│   │   ├── developer.json            # Software Engineer Agent role definition
│   │   ├── reviewer.json             # Code Reviewer Agent role definition
│   │   └── security.json             # Security Compliance Auditor Agent role definition
│   ├── knowledge/                    # Static Architecture Specs & Domain Dictionaries
│   │   └── architecture.md           # High-level architecture specification
│   ├── memory/                       # Long-term session logs & reflections
│   └── subsystems/                   # Subsystem AGENTS.md scoping rules
│       ├── api/                      # Scoped rules for src/api
│       └── db/                       # Scoped rules for src/db
└── docs/                             # Workspace Documentation Tree
```

---

## 2. File Schema Specifications

### 2.1. Config File (`.agentguard/config.json`)
```json
{
  "project_name": "My Enterprise Repository",
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
  "pre_commit_hook": true,
  "zero_prompt_tax": true
}
```

---

### 2.2. Agent Role Manifest (`.agentguard/agents/<role_id>.json`)
```json
{
  "role_id": "developer",
  "role_name": "Software Engineering Agent",
  "scope": "root",
  "permitted_tools": [
    "view_file",
    "replace_file_content",
    "write_to_file",
    "run_command",
    "query_graph"
  ],
  "forbidden_tools": [
    "force_git_push",
    "drop_database"
  ],
  "parent_role_id": "architect"
}
```

---

### 2.3. Tiered Rule JSON Schema (`.agentguard/rules/<tier_file>.json`)
```json
[
  {
    "id": "cr_org_001_no_direct_push",
    "title": "Strict Main Branch Push Lock",
    "priority": 4,
    "target_scope": "root",
    "restricted_actions": [
      "direct_git_push_main",
      "force_git_push"
    ],
    "content": "No agent or human automated script may perform direct git push to main or production release branches."
  }
]
```

---

## 3. Best Practices for Subsystem Governance

1. **Scoped AGENTS.md Files:** For multi-module monorepos, place sub-scoped governance directives in module folders (e.g. `src/api/AGENTS.md`). AgentGuard's `sync` engine automatically ingests sub-scoped rules into Tier 2 (`SUBSYSTEM_RULE`).
2. **Explicit Inheritance:** Use `parent_role_id` to build lean specialist roles that inherit baseline tool authorizations from primary roles (e.g. `frontend_dev` inheriting from `developer`).
3. **Automated Commit Gate:** Always keep `.git/hooks/pre-commit` active to guarantee that no broken rule DAGs or cyclic dependencies are committed to version control.
