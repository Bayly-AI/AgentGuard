"""Dynamic Zero-Prompt-Tax System Prompt Synthesizer."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from agentguard.core.graph import AgentGuardGraph


class PromptSynthesizer:
    """Synthesizes minimal, deterministic system prompts tailored to active agent role governance."""

    @staticmethod
    def synthesize_prompt(
        graph: AgentGuardGraph,
        role_id: str,
        scope: Optional[str] = None
    ) -> str:
        """Render zero-prompt-tax system prompt for target agent role."""
        resolved = graph.resolve_role(role_id=role_id, scope=scope)

        lines = [
            f"# Agent Governance Mandate: {resolved.role_name} (`role:{resolved.role_id}`)",
            f"**Scope:** `{resolved.scope}` | **Inheritance Lineage:** `{' -> '.join(resolved.lineage_path)}`",
            "",
            "## Authorized Tools",
            f"Allowed Tools: {', '.join(sorted(list(resolved.authorized_tools))) if resolved.authorized_tools else 'None'}",
            f"Forbidden Tools: {', '.join(sorted(list(resolved.forbidden_tools))) if resolved.forbidden_tools else 'None'}",
            "",
            "## Active Governing Rules (Evaluated Tier Dominance)",
        ]

        if not resolved.active_rules:
            lines.append("- No explicit governing rules active for this scope.")
        else:
            for rule in resolved.active_rules:
                prio = rule.properties.get("priority", 1)
                lines.append(f"- **[Tier {prio}] {rule.label}**: {rule.content.strip()}")

        if resolved.restricted_actions:
            lines.extend([
                "",
                "## Restricted Actions (Forbidden)",
                f"{', '.join(sorted(list(resolved.restricted_actions)))}"
            ])

        lines.extend([
            "",
            "---",
            "*System prompt dynamically synthesized by AgentGuard Zero-Prompt-Tax Engine.*"
        ])

        return "\n".join(lines)
