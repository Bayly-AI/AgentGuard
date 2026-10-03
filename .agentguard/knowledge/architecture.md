# Workspace Architecture Overview

> **Plane:** KnowledgeGraph (`doc:architecture.md`)

This repository is governed by AgentGuard's Quad-Graph cognitive substrate.

## Subsystems
1. **Core Engine:** Quad-Graph data models, SQLite storage, Okapi BM25 lexical search.
2. **Governance:** Deterministic Rule Priority DAG, RBAC tool authorization, pre-execution gates.
3. **Repository Init & Sync:** Workspace scaffolding, markdown and code AST ingestion.
