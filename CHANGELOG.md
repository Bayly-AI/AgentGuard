# Changelog

All notable changes to **AgentGuard** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.3] - 2026-10-29

### Changed
- **Rule Harmonization, `CLAUDE.md` 1:1 Sync & Workflow Upgrade (`CR-CLAUDE-SYNC-001` · `CR-AGENTIC-SEC-001`)**:
  - Eliminated conflicting and duplicate rules in `AGENTS.md`, synchronized `CLAUDE.md` 1:1 with `AGENTS.md`, initialized `THREATMODEL.md`, and upgraded `.agents/skills/clean-repos/SKILL.md` and `.agents/skills/orient/SKILL.md` to use the latest `hath0r` CLI (`v1.15.0`) workflows.

## [1.0.2] - 2026-10-28

### Added
- CR-SEMVER-BUMP-001: every created or merged PR must create or bump the product's Semantic Version (`VERSION` is the source of truth).
