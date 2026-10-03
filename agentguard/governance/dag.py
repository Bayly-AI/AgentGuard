"""Directed Acyclic Graph (DAG) Rule Resolution and Priority Tier Conflict Resolver."""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple

from agentguard.core.models import (
    AgentGraphEdge,
    AgentGraphNode,
    AgentGraphPlane,
    ResolvedRuleSet,
    RuleConflictError,
    RuleCycleError,
    RulePriority,
)


class GovernanceDAGResolver:
    """Evaluates rule inheritance DAGs, tool RBAC, and priority tier dominance."""

    @staticmethod
    def resolve_role_rules(
        role_id: str,
        nodes: Dict[str, AgentGraphNode],
        outgoing_edges: Dict[str, List[AgentGraphEdge]],
        incoming_edges: Dict[str, List[AgentGraphEdge]],
        scope: Optional[str] = None
    ) -> ResolvedRuleSet:
        """Resolve effective governance rule set for a target agent role."""
        formatted_role_id = role_id if role_id.startswith("role:") else f"role:{role_id}"
        if formatted_role_id not in nodes:
            raise ValueError(f"Target role '{role_id}' not found in AgentGuard substrate.")

        role_node = nodes[formatted_role_id]
        role_name = role_node.label
        effective_scope = scope or role_node.properties.get("scope", "root")

        # 1. Direct Ancestry Traversal & Cycle Detection
        lineage: List[str] = []
        visited: Set[str] = set()
        curr: Optional[str] = formatted_role_id

        while curr:
            if curr in visited:
                raise RuleCycleError(
                    f"Inheritance cycle detected in Rule DAG: {' -> '.join(lineage)} -> {curr}"
                )
            visited.add(curr)
            lineage.append(curr)

            inherits = [e for e in outgoing_edges.get(curr, []) if e.relation == "INHERITS_FROM"]
            curr = inherits[0].target if inherits else None

        # 2. Accumulate Authorized & Forbidden Tools
        authorized_tools: Set[str] = set()
        forbidden_tools: Set[str] = set()

        for r_id in lineage:
            r_node = nodes.get(r_id)
            if r_node:
                authorized_tools.update(r_node.properties.get("permitted_tools", []))
                forbidden_tools.update(r_node.properties.get("forbidden_tools", []))

            for edge in outgoing_edges.get(r_id, []):
                if edge.relation == "AUTHORIZES_TOOL":
                    authorized_tools.add(edge.target.removeprefix("tool:"))

        # Forbidden tools override authorized tools
        authorized_tools.difference_update(forbidden_tools)

        # 3. Collect Applicable Rule Policies
        applicable_rules: Dict[str, AgentGraphNode] = {}

        # A. Rules explicitly governing lineage roles
        for r_id in lineage:
            for inc in incoming_edges.get(r_id, []):
                if inc.relation == "GOVERNS":
                    rule_node = nodes.get(inc.source)
                    if rule_node and rule_node.is_valid_at():
                        applicable_rules[rule_node.id] = rule_node

        # B. Rules matching target scope or root scope
        for node in nodes.values():
            if node.plane == AgentGraphPlane.RULES.value and node.type == "rule_policy":
                rule_scope = node.properties.get("target_scope", "root")
                if rule_scope in ("root", effective_scope, "*") and node.is_valid_at():
                    applicable_rules[node.id] = node

        # 4. Sort Rules by Priority Tier Dominance (Tier 4 > Tier 3 > Tier 2 > Tier 1)
        sorted_rules = sorted(
            applicable_rules.values(),
            key=lambda r: int(r.properties.get("priority", RulePriority.REPO_STANDARD)),
            reverse=True
        )

        # 5. Resolve Action Directives & Detect Same-Tier Collisions
        restricted_actions: Set[str] = set()
        allowed_actions: Set[str] = set()
        action_map: Dict[str, Tuple[int, bool, str]] = {}  # action -> (priority, is_allowed, rule_id)

        for rule in sorted_rules:
            prio = int(rule.properties.get("priority", RulePriority.REPO_STANDARD))

            # Process restricted actions in rule
            for act in rule.properties.get("restricted_actions", []):
                if act in action_map:
                    prev_prio, prev_allowed, prev_rule = action_map[act]
                    if prio == prev_prio and prev_allowed:
                        raise RuleConflictError(
                            f"Rule Priority Collision at Tier {prio}: Action '{act}' restricted by [{rule.id}] "
                            f"conflicts with allowed directive in [{prev_rule}]."
                        )
                    # If prio < prev_prio, higher tier already set the rule policy dominance
                else:
                    action_map[act] = (prio, False, rule.id)

            # Process allowed actions in rule
            for act in rule.properties.get("allowed_actions", []):
                if act in action_map:
                    prev_prio, prev_allowed, prev_rule = action_map[act]
                    if prio == prev_prio and not prev_allowed:
                        raise RuleConflictError(
                            f"Rule Priority Collision at Tier {prio}: Action '{act}' allowed by [{rule.id}] "
                            f"conflicts with restricted directive in [{prev_rule}]."
                        )
                else:
                    action_map[act] = (prio, True, rule.id)

        for act, (_, is_allowed, _) in action_map.items():
            if is_allowed:
                allowed_actions.add(act)
            else:
                restricted_actions.add(act)

        return ResolvedRuleSet(
            role_id=role_id.removeprefix("role:"),
            role_name=role_name,
            scope=effective_scope,
            active_rules=sorted_rules,
            authorized_tools=authorized_tools,
            forbidden_tools=forbidden_tools,
            restricted_actions=restricted_actions,
            allowed_actions=allowed_actions,
            lineage_path=lineage
        )
