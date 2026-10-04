"""
AgentGuard Phoenix Security Evaluation Bot.

Executes autonomous red-teaming checks and guardrail inspections over agent
interaction inputs and outputs, exporting OpenInference security telemetry.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import structlog
from ..telemetry.phoenix import AgentGuardPhoenixTracer, guard_tracer
from ..audit.phoenix_evals import JailbreakEvaluationJudge, PiiRedactionJudge

logger = structlog.get_logger(__name__)


class PhoenixGuardBot:
    """Automated security evaluation bot for AI agent interactions."""

    def __init__(self, tracer: Optional[AgentGuardPhoenixTracer] = None) -> None:
        self.tracer = tracer or guard_tracer
        self.jailbreak_judge = JailbreakEvaluationJudge()
        self.pii_judge = PiiRedactionJudge()

    def scan_interaction(
        self,
        prompt: str,
        completion: str = "",
        policy_id: str = "default-policy",
        agent_id: str = "unknown-agent",
    ) -> Dict[str, Any]:
        """Scan a prompt and completion for safety, jailbreaks, and PII leaks."""
        with self.tracer.trace_guardrail_check("comprehensive_security_scan", policy_id=policy_id, agent_id=agent_id) as ctx:
            jb_res = self.jailbreak_judge.evaluate(prompt)
            pii_res = self.pii_judge.evaluate(prompt, completion)

            all_passed = jb_res.passed and pii_res.passed
            ctx["threat_detected"] = not all_passed
            ctx["decision"] = "ALLOW" if all_passed else "BLOCK"
            ctx["confidence_score"] = min(jb_res.score, pii_res.score)

            report = {
                "decision": ctx["decision"],
                "all_passed": all_passed,
                "jailbreak_evaluation": {
                    "passed": jb_res.passed,
                    "score": jb_res.score,
                    "violations": jb_res.violations,
                    "details": jb_res.details,
                },
                "pii_evaluation": {
                    "passed": pii_res.passed,
                    "score": pii_res.score,
                    "violations": pii_res.violations,
                    "details": pii_res.details,
                },
            }

            logger.info(
                "agentguard_scan_completed",
                decision=report["decision"],
                threat_detected=ctx["threat_detected"],
                agent_id=agent_id,
            )

            return report


guard_bot = PhoenixGuardBot()
