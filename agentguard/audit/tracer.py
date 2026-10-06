"""Audit trail tracer and operational provenance reconstruction engine."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from agentguard.core.models import AuditRecord

if TYPE_CHECKING:
    from agentguard.core.graph import AgentGuardGraph


class AuditTracer:
    """Manages recording and querying execution audit traces across agent runs."""

    @staticmethod
    def record_trace(
        graph: AgentGuardGraph,
        session_id: str,
        actor_id: str,
        role_id: str,
        action_type: str,
        tool_name: str,
        status: str,
        details: str
    ) -> AuditRecord:
        """Record an audit trace record in graph storage."""
        record = AuditRecord(
            session_id=session_id,
            actor_id=actor_id,
            role_id=role_id,
            action_type=action_type,
            tool_name=tool_name,
            status=status,
            details=details
        )
        graph.log_audit(record)
        return record

    @staticmethod
    def fetch_audit_history(
        graph: AgentGuardGraph,
        limit: int = 50,
        role_id: Optional[str] = None
    ) -> List[AuditRecord]:
        """Retrieve recent audit trace records."""
        return graph.get_audit_logs(limit=limit, role_id=role_id)
