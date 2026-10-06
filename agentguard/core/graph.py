"""AgentGuard Quad-Graph Substrate Engine."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from agentguard.core.models import (
    AgentGraphEdge,
    AgentGraphNode,
    AgentGraphPlane,
    AuditRecord,
    ResolvedRuleSet,
    RulePriority,
    SearchResult,
    ValidationReport,
)
from agentguard.core.search import BM25SearchEngine
from agentguard.core.storage import SQLiteStore
from agentguard.governance.dag import GovernanceDAGResolver
from agentguard.governance.rbac import RBACManager


class AgentGuardGraph:
    """The central Quad-Graph engine unifying RulesGraph, KnowledgeGraph, ContextGraph, and MemoryGraph."""

    def __init__(self, db_path: Path | str = ".agentguard/graph.db") -> None:
        self.db_path = str(db_path)
        self.nodes: Dict[str, AgentGraphNode] = {}
        self.edges: List[AgentGraphEdge] = []
        self._outgoing: Dict[str, List[AgentGraphEdge]] = defaultdict(list)
        self._incoming: Dict[str, List[AgentGraphEdge]] = defaultdict(list)
        self.search_engine = BM25SearchEngine()

    def add_node(self, node: AgentGraphNode) -> None:
        """Add node to graph memory and index it for search."""
        self.nodes[node.id] = node
        self.search_engine.index_node(node)

    def add_edge(self, edge: AgentGraphEdge) -> None:
        """Add relational edge to graph memory."""
        self.edges.append(edge)
        self._outgoing[edge.source].append(edge)
        self._incoming[edge.target].append(edge)

    def get_outgoing(self, source_id: str, relation: Optional[str] = None) -> List[AgentGraphEdge]:
        """Fetch outgoing edges from source_id."""
        edges = self._outgoing.get(source_id, [])
        return [e for e in edges if e.relation == relation] if relation else list(edges)

    def get_incoming(self, target_id: str, relation: Optional[str] = None) -> List[AgentGraphEdge]:
        """Fetch incoming edges to target_id."""
        edges = self._incoming.get(target_id, [])
        return [e for e in edges if e.relation == relation] if relation else list(edges)

    def clear(self) -> None:
        """Reset in-memory graph structures."""
        self.nodes.clear()
        self.edges.clear()
        self._outgoing.clear()
        self._incoming.clear()
        self.search_engine.clear()

    # -------------------------------------------------------------------------
    # Role & Rule Helper Methods
    # -------------------------------------------------------------------------

    def register_role(
        self,
        role_id: str,
        role_name: str,
        scope: str = "root",
        permitted_tools: Optional[List[str]] = None,
        forbidden_tools: Optional[List[str]] = None,
        parent_role_id: Optional[str] = None
    ) -> AgentGraphNode:
        """Register or update an agent role node and its authorization edges."""
        node, edges = RBACManager.create_role_node(
            role_id=role_id,
            role_name=role_name,
            scope=scope,
            permitted_tools=permitted_tools,
            forbidden_tools=forbidden_tools,
            parent_role_id=parent_role_id
        )
        self.add_node(node)
        for edge in edges:
            self.add_edge(edge)
        return node

    def register_rule(
        self,
        rule_id: str,
        title: str,
        content: str,
        priority: RulePriority = RulePriority.REPO_STANDARD,
        target_scope: str = "root",
        governs_roles: Optional[List[str]] = None,
        restricted_actions: Optional[List[str]] = None,
        allowed_actions: Optional[List[str]] = None
    ) -> AgentGraphNode:
        """Register a governance rule policy in the RulesGraph."""
        formatted_id = rule_id if rule_id.startswith("rule:") else f"rule:{rule_id}"
        node = AgentGraphNode(
            id=formatted_id,
            plane=AgentGraphPlane.RULES.value,
            type="rule_policy",
            label=title,
            content=content,
            properties={
                "rule_id": rule_id.removeprefix("rule:"),
                "priority": int(priority),
                "target_scope": target_scope,
                "restricted_actions": restricted_actions or [],
                "allowed_actions": allowed_actions or []
            }
        )
        self.add_node(node)

        for r_id in governs_roles or []:
            formatted_role_id = r_id if r_id.startswith("role:") else f"role:{r_id}"
            self.add_edge(AgentGraphEdge(
                source=formatted_id,
                target=formatted_role_id,
                relation="GOVERNS",
                plane=AgentGraphPlane.RULES.value
            ))
        return node

    def resolve_role(self, role_id: str, scope: Optional[str] = None) -> ResolvedRuleSet:
        """Resolve effective rule set and RBAC authorizations for target role."""
        return GovernanceDAGResolver.resolve_role_rules(
            role_id=role_id,
            nodes=self.nodes,
            outgoing_edges=self._outgoing,
            incoming_edges=self._incoming,
            scope=scope
        )

    # -------------------------------------------------------------------------
    # Search & Validation
    # -------------------------------------------------------------------------

    def query(
        self,
        query_str: str,
        plane: Optional[str] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        """Perform BM25 search across graph nodes."""
        return self.search_engine.query(query_str=query_str, target_plane=plane, limit=limit)

    def validate(self) -> ValidationReport:
        """Audit graph topology for cycle dependencies, dangling edges, and conflicts."""
        plane_counts = Counter(n.plane for n in self.nodes.values())
        dangling_edges: List[Tuple[str, str]] = []

        for e in self.edges:
            # Source must exist in graph
            if e.source not in self.nodes:
                dangling_edges.append((e.source, e.target))
            # Target must exist unless it's an external tool reference or AST class reference
            elif (
                not e.target.startswith("tool:")
                and not e.target.startswith("ast:class_ref:")
                and e.target not in self.nodes
            ):
                dangling_edges.append((e.source, e.target))

        # Inheritance cycle detection in RulesGraph
        cycles: List[List[str]] = []
        visited: Set[str] = set()
        stack: Set[str] = set()

        def dfs(node_id: str, path: List[str]):
            visited.add(node_id)
            stack.add(node_id)
            path.append(node_id)

            for edge in self.get_outgoing(node_id, relation="INHERITS_FROM"):
                if edge.target not in visited:
                    dfs(edge.target, path)
                elif edge.target in stack:
                    start_idx = path.index(edge.target)
                    cycles.append(path[start_idx:] + [edge.target])

            path.pop()
            stack.remove(node_id)

        for n_id, node in self.nodes.items():
            if node.plane == AgentGraphPlane.RULES.value and n_id not in visited:
                dfs(n_id, [])

        is_valid = (len(dangling_edges) == 0 and len(cycles) == 0)

        return ValidationReport(
            is_valid=is_valid,
            total_nodes=len(self.nodes),
            total_edges=len(self.edges),
            plane_counts=dict(plane_counts),
            dangling_edges=dangling_edges,
            detected_cycles=cycles
        )

    # -------------------------------------------------------------------------
    # Persistence & Audit
    # -------------------------------------------------------------------------

    def save_to_db(self) -> None:
        """Persist in-memory graph to SQLite database."""
        store = SQLiteStore(self.db_path)
        store.clear_edges()
        for node in self.nodes.values():
            store.upsert_node(node)
        for edge in self.edges:
            store.add_edge(edge)
        store.close()

    def load_from_db(self) -> None:
        """Load graph nodes and edges from SQLite database."""
        store = SQLiteStore(self.db_path)
        self.clear()
        nodes, edges = store.load_all()
        for node in nodes:
            self.add_node(node)
        for edge in edges:
            self.add_edge(edge)
        store.close()

    def log_audit(self, record: AuditRecord) -> None:
        """Log an execution trace event to SQLite."""
        store = SQLiteStore(self.db_path)
        store.log_audit(record)
        store.close()

    def get_audit_logs(self, limit: int = 50, role_id: Optional[str] = None) -> List[AuditRecord]:
        """Fetch execution trace logs from SQLite."""
        store = SQLiteStore(self.db_path)
        logs = store.load_audit_logs(limit=limit, role_id=role_id)
        store.close()
        return logs

    @classmethod
    def init(cls, workspace_dir: Path | str = ".", no_hooks: bool = False) -> "AgentGuardGraph":
        """Initialize workspace directory layout (.agentguard/, AGENTS.md, git hooks) and sync substrate."""
        from agentguard.init.initializer import RepositoryInitializer
        from agentguard.sync.syncer import RepositorySyncer

        target_dir = Path(workspace_dir)
        RepositoryInitializer.initialize_repository(target_dir=target_dir, install_hooks=not no_hooks)
        graph = RepositorySyncer.sync_repository(root_dir=target_dir)
        return graph


# Alias AgentGraph for seamless developer API access
AgentGraph = AgentGuardGraph
