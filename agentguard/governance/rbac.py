"""Role-Based Access Control (RBAC) and tool authorization engine."""

from __future__ import annotations

from typing import List, Optional, Set, Tuple

from agentguard.core.models import (
    AgentGraphEdge,
    AgentGraphNode,
    AgentGraphPlane,
    RBACPermissionError,
)


class RBACManager:
    """Manages role registrations and tool authorization graphs."""

    @staticmethod
    def create_role_node(
        role_id: str,
        role_name: str,
        scope: str = "root",
        permitted_tools: Optional[List[str]] = None,
        forbidden_tools: Optional[List[str]] = None,
        parent_role_id: Optional[str] = None
    ) -> Tuple[AgentGraphNode, List[AgentGraphEdge]]:
        """Construct role node and relational authorization edges."""
        formatted_id = role_id if role_id.startswith("role:") else f"role:{role_id}"
        node = AgentGraphNode(
            id=formatted_id,
            plane=AgentGraphPlane.RULES.value,
            type="agent_role",
            label=role_name,
            content=f"Agent Role '{role_name}' operating in scope '{scope}'.",
            properties={
                "role_id": role_id.removeprefix("role:"),
                "scope": scope,
                "permitted_tools": permitted_tools or [],
                "forbidden_tools": forbidden_tools or [],
                "parent_role_id": parent_role_id
            }
        )

        edges: List[AgentGraphEdge] = []
        for tool in permitted_tools or []:
            tool_id = tool if tool.startswith("tool:") else f"tool:{tool}"
            edges.append(AgentGraphEdge(
                source=formatted_id,
                target=tool_id,
                relation="AUTHORIZES_TOOL",
                plane=AgentGraphPlane.RULES.value
            ))

        if parent_role_id:
            parent_id = parent_role_id if parent_role_id.startswith("role:") else f"role:{parent_role_id}"
            edges.append(AgentGraphEdge(
                source=formatted_id,
                target=parent_id,
                relation="INHERITS_FROM",
                plane=AgentGraphPlane.RULES.value
            ))

        return node, edges

    @staticmethod
    def verify_tool_execution(
        role_id: str,
        tool_name: str,
        authorized_tools: Set[str],
        forbidden_tools: Set[str]
    ) -> bool:
        """Verify if a tool invocation is permitted for the active role."""
        clean_tool = tool_name.removeprefix("tool:")
        if clean_tool in forbidden_tools:
            raise RBACPermissionError(
                f"RBAC Security Gate Denied: Tool '{clean_tool}' is EXPLICITLY FORBIDDEN for role '{role_id}'."
            )
        if clean_tool not in authorized_tools and "*" not in authorized_tools:
            raise RBACPermissionError(
                f"RBAC Security Gate Denied: Tool '{clean_tool}' is NOT AUTHORIZED for role '{role_id}'."
            )
        return True
