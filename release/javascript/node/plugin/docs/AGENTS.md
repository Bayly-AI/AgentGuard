# Repository Agent Policy & Governance (AGENTS.md)

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
