"""Data models, dataclasses, enums, and exception types for AgentGuard."""

from __future__ import annotations

import datetime
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class AgentGraphPlane(str, Enum):
    """The four canonical cognitive planes + extensible plane."""
    RULES = "rules"
    KNOWLEDGE = "knowledge"
    CONTEXT = "context"
    MEMORY = "memory"
    EXTENSIBLE = "extensible"


class RulePriority(int, Enum):
    """Deterministic rule DAG priority tiers (Tier 4 > Tier 3 > Tier 2 > Tier 1)."""
    ROLE_GUIDELINE = 1
    SUBSYSTEM_RULE = 2
    REPO_STANDARD = 3
    ORG_INVARIANT = 4


class RuleCycleError(Exception):
    """Raised when an inheritance cycle is detected in the rule DAG."""


class RuleConflictError(Exception):
    """Raised when opposing rule directives collide at the same priority tier."""


class RBACPermissionError(Exception):
    """Raised when an agent role attempts an unauthorized tool execution or restricted action."""


@dataclass
class AgentGraphNode:
    """Core entity node within the Quad-Graph substrate."""
    id: str
    plane: str
    type: str
    label: str
    content: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    is_current: bool = True
    created_at: str = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

    def is_valid_at(self, as_of: Optional[str] = None, only_current: bool = True) -> bool:
        """Evaluate bitemporal validity of node."""
        if only_current and not self.is_current:
            return False
        if not as_of:
            return True if not only_current else self.is_current
        if self.valid_from and self.valid_from > as_of:
            return False
        if self.valid_to and self.valid_to < as_of:
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AgentGraphNode:
        return cls(**data)


@dataclass
class AgentGraphEdge:
    """Relational directed edge connecting entity nodes across or within planes."""
    source: str
    target: str
    relation: str
    plane: Optional[str] = None
    weight: float = 1.0
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    is_current: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_valid_at(self, as_of: Optional[str] = None, only_current: bool = True) -> bool:
        """Evaluate bitemporal validity of edge."""
        if only_current and not self.is_current:
            return False
        if not as_of:
            return True if not only_current else self.is_current
        if self.valid_from and self.valid_from > as_of:
            return False
        if self.valid_to and self.valid_to < as_of:
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AgentGraphEdge:
        return cls(**data)


@dataclass
class ResolvedRuleSet:
    """Resolved governance posture for a target agent role and scope."""
    role_id: str
    role_name: str
    scope: str
    active_rules: List[AgentGraphNode]
    authorized_tools: Set[str]
    forbidden_tools: Set[str]
    restricted_actions: Set[str]
    allowed_actions: Set[str]
    lineage_path: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role_id": self.role_id,
            "role_name": self.role_name,
            "scope": self.scope,
            "active_rules": [r.to_dict() for r in self.active_rules],
            "authorized_tools": sorted(list(self.authorized_tools)),
            "forbidden_tools": sorted(list(self.forbidden_tools)),
            "restricted_actions": sorted(list(self.restricted_actions)),
            "allowed_actions": sorted(list(self.allowed_actions)),
            "lineage_path": self.lineage_path,
        }


@dataclass
class SearchResult:
    """Result item returned by lexical/BM25 query search."""
    node: AgentGraphNode
    score: float
    matched_plane: str


@dataclass
class ValidationReport:
    """Graph integrity and health audit report."""
    is_valid: bool
    total_nodes: int
    total_edges: int
    plane_counts: Dict[str, int]
    dangling_edges: List[Tuple[str, str]]
    detected_cycles: List[List[str]]
    conflicts: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "total_nodes": self.total_nodes,
            "total_edges": self.total_edges,
            "plane_counts": self.plane_counts,
            "dangling_edges": self.dangling_edges,
            "detected_cycles": self.detected_cycles,
            "conflicts": self.conflicts,
        }


@dataclass
class AuditRecord:
    """Execution audit trace log entry."""
    session_id: str
    actor_id: str
    role_id: str
    action_type: str
    tool_name: str
    status: str
    details: str
    timestamp: str = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
