"""AgentGuard: Standalone Cognitive Substrate & Governance Engine for Agentic AI Systems.

Provides Quad-Graph cognitive substrate (RulesGraph, KnowledgeGraph, ContextGraph, MemoryGraph),
deterministic rule inheritance DAGs, role-based tool authorization (RBAC), repository initialization,
zero-prompt-tax system prompt synthesis, pre-execution tool security gating, and workspace auditing.
"""

__version__ = "1.0.0"
__author__ = "Bayly AI / AgentGuard Core Team"

from agentguard.core.models import (
    AgentGraphEdge,
    AgentGraphNode,
    AgentGraphPlane,
    ResolvedRuleSet,
    RulePriority,
    SearchResult,
    ValidationReport,
)
from agentguard.core.graph import AgentGuardGraph

__all__ = [
    "AgentGraphNode",
    "AgentGraphEdge",
    "AgentGraphPlane",
    "RulePriority",
    "ResolvedRuleSet",
    "SearchResult",
    "ValidationReport",
    "AgentGuardGraph",
]
