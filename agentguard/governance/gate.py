"""Pre-execution Security Gate and Runtime Integration Hooks."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from agentguard.core.models import AuditRecord, RBACPermissionError
from agentguard.governance.rbac import RBACManager

if TYPE_CHECKING:
    from agentguard.core.graph import AgentGuardGraph


class SecurityGate:
    """Pre-execution governance gate that intercepts tool and action calls."""

    @staticmethod
    def enforce_tool(
        graph: AgentGuardGraph,
        role_id: str,
        tool_name: str,
        actor_id: str = "agent_runner",
        session_id: str = "active_session"
    ) -> bool:
        """Evaluate whether role is authorized to execute the target tool."""
        resolved = graph.resolve_role(role_id)
        clean_tool = tool_name.removeprefix("tool:")

        try:
            RBACManager.verify_tool_execution(
                role_id=role_id,
                tool_name=clean_tool,
                authorized_tools=resolved.authorized_tools,
                forbidden_tools=resolved.forbidden_tools
            )
            # Log successful gate evaluation
            graph.log_audit(AuditRecord(
                session_id=session_id,
                actor_id=actor_id,
                role_id=role_id,
                action_type="TOOL_GATE",
                tool_name=clean_tool,
                status="ALLOWED",
                details=f"Tool '{clean_tool}' authorized for role '{role_id}'"
            ))
            return True

        except RBACPermissionError as err:
            # Log denied gate evaluation
            graph.log_audit(AuditRecord(
                session_id=session_id,
                actor_id=actor_id,
                role_id=role_id,
                action_type="TOOL_GATE",
                tool_name=clean_tool,
                status="DENIED",
                details=str(err)
            ))
            raise

    @staticmethod
    def enforce_action(
        graph: AgentGuardGraph,
        role_id: str,
        action_name: str,
        actor_id: str = "agent_runner",
        session_id: str = "active_session"
    ) -> bool:
        """Evaluate whether an action directive is permitted for the active role."""
        resolved = graph.resolve_role(role_id)

        if action_name in resolved.restricted_actions:
            err_msg = f"Action Gate Denied: Action '{action_name}' is RESTRICTED for role '{role_id}'."
            graph.log_audit(AuditRecord(
                session_id=session_id,
                actor_id=actor_id,
                role_id=role_id,
                action_type="ACTION_GATE",
                tool_name=action_name,
                status="DENIED",
                details=err_msg
            ))
            raise RBACPermissionError(err_msg)

        graph.log_audit(AuditRecord(
            session_id=session_id,
            actor_id=actor_id,
            role_id=role_id,
            action_type="ACTION_GATE",
            tool_name=action_name,
            status="ALLOWED",
            details=f"Action '{action_name}' permitted for role '{role_id}'"
        ))
        return True
