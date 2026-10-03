"""Workspace Syncer that orchestrates parsing and graph ingestion."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List

from agentguard.core.graph import AgentGuardGraph
from agentguard.core.models import AgentGraphNode, AgentGraphPlane, RulePriority
from agentguard.sync.code_parser import CodeASTParser
from agentguard.sync.md_parser import MarkdownParser


class RepositorySyncer:
    """Scans workspace and ingests rules, roles, documents, and AST nodes into AgentGuard graph."""

    @staticmethod
    def sync_repository(root_dir: Path | str = ".", graph: AgentGuardGraph | None = None) -> AgentGuardGraph:
        """Run full workspace sync and persist to database."""
        root = Path(root_dir).resolve()
        ag_dir = root / ".agentguard"
        db_path = ag_dir / "graph.db" if ag_dir.exists() else ".agentguard/graph.db"

        if graph is None:
            graph = AgentGuardGraph(db_path=db_path)

        graph.clear()

        # 1. Ingest .agentguard/rules/*.json
        rules_dir = ag_dir / "rules"
        if rules_dir.exists():
            for rule_file in sorted(rules_dir.glob("*.json")):
                try:
                    data = json.loads(rule_file.read_text(encoding="utf-8"))
                    if isinstance(data, list):
                        for item in data:
                            prio = RulePriority(item.get("priority", 3))
                            graph.register_rule(
                                rule_id=item["id"],
                                title=item.get("title", item["id"]),
                                content=item.get("content", ""),
                                priority=prio,
                                target_scope=item.get("target_scope", "root"),
                                governs_roles=item.get("governs_roles", []),
                                restricted_actions=item.get("restricted_actions", []),
                                allowed_actions=item.get("allowed_actions", [])
                            )
                except Exception as err:
                    print(f"Warning: Failed parsing rule file {rule_file}: {err}")

        # 2. Ingest .agentguard/agents/*.json
        agents_dir = ag_dir / "agents"
        if agents_dir.exists():
            for agent_file in sorted(agents_dir.glob("*.json")):
                try:
                    data = json.loads(agent_file.read_text(encoding="utf-8"))
                    graph.register_role(
                        role_id=data["role_id"],
                        role_name=data.get("role_name", data["role_id"]),
                        scope=data.get("scope", "root"),
                        permitted_tools=data.get("permitted_tools", []),
                        forbidden_tools=data.get("forbidden_tools", []),
                        parent_role_id=data.get("parent_role_id")
                    )
                except Exception as err:
                    print(f"Warning: Failed parsing agent file {agent_file}: {err}")

        # 3. Ingest AGENTS.md
        agents_md = root / "AGENTS.md"
        if agents_md.exists():
            md_nodes, md_edges = MarkdownParser.parse_agents_md(agents_md)
            for node in md_nodes:
                graph.add_node(node)
            for edge in md_edges:
                graph.add_edge(edge)

        # 4. Ingest .agentguard/knowledge/*.md and docs/*.md
        knowledge_paths = [ag_dir / "knowledge", root / "docs"]
        for k_path in knowledge_paths:
            if k_path.exists():
                for doc_file in k_path.rglob("*.md"):
                    node, edges = MarkdownParser.parse_doc_file(doc_file)
                    graph.add_node(node)
                    for edge in edges:
                        graph.add_edge(edge)

        # 5. Ingest Python AST files in src/ or agentguard/
        code_paths = [root / "src", root / "agentguard"]
        for c_path in code_paths:
            if c_path.exists():
                for py_file in c_path.rglob("*.py"):
                    ast_nodes, ast_edges = CodeASTParser.parse_python_file(py_file)
                    for node in ast_nodes:
                        graph.add_node(node)
                    for edge in ast_edges:
                        graph.add_edge(edge)

        # 6. Auto-stub missing target nodes (e.g. cross-referenced docs not yet created)
        missing_targets = set()
        for edge in graph.edges:
            if edge.target not in graph.nodes and not edge.target.startswith("tool:") and not edge.target.startswith("ast:class_ref:"):
                missing_targets.add(edge.target)

        for target_id in missing_targets:
            if target_id.startswith("doc:"):
                doc_name = target_id.removeprefix("doc:")
                graph.add_node(AgentGraphNode(
                    id=target_id,
                    plane=AgentGraphPlane.KNOWLEDGE.value,
                    type="unresolved_document",
                    label=f"Cross-referenced Document ({doc_name})",
                    content=f"Placeholder for cross-referenced document '{doc_name}'. File not yet created in repository.",
                    properties={"status": "unresolved_stub"}
                ))

        # Persist graph state
        graph.save_to_db()
        return graph
