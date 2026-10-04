"""
Arize Phoenix & OpenTelemetry Telemetry Subsystem for AgentGuard.

Emits OpenInference security guardrail evaluation spans, inspection latency,
threat classification results, and policy decision telemetry.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Any, Dict, Iterator, Optional

try:
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode
    OTEL_AVAILABLE = True
except Exception:  # pragma: no cover
    trace = None
    Status = None
    StatusCode = None
    OTEL_AVAILABLE = False


class AgentGuardPhoenixTracer:
    """Manages spans and telemetry for AgentGuard security evaluations."""

    def __init__(self, service_name: str = "agentguard") -> None:
        self.service_name = service_name
        self._tracer = trace.get_tracer(service_name) if OTEL_AVAILABLE else None

    @property
    def is_enabled(self) -> bool:
        return OTEL_AVAILABLE and self._tracer is not None

    @contextmanager
    def trace_guardrail_check(
        self,
        guardrail_name: str,
        policy_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> Iterator[Dict[str, Any]]:
        """
        Record a guardrail inspection span.
        """
        start = time.perf_counter()
        span_attrs = {
            "openinference.span.kind": "GUARDRAIL",
            "guardrail.name": guardrail_name,
            "guardrail.policy_id": policy_id or "default",
            "agentguard.service": self.service_name,
        }
        if agent_id:
            span_attrs["agent.id"] = agent_id

        active_span = None
        if self.is_enabled and self._tracer:
            try:
                active_span = self._tracer.start_span(f"guardrail.{guardrail_name}", attributes=span_attrs)
            except Exception:
                active_span = None

        result_context: Dict[str, Any] = {
            "decision": "ALLOW",
            "threat_detected": False,
            "threat_type": None,
            "confidence_score": 1.0,
            "redacted_chars": 0,
        }

        try:
            yield result_context
            if active_span and StatusCode:
                active_span.set_status(Status(StatusCode.OK))
        except Exception as exc:
            result_context["decision"] = "ERROR"
            result_context["error"] = str(exc)
            if active_span and StatusCode:
                active_span.set_status(Status(StatusCode.ERROR, description=str(exc)))
                active_span.record_exception(exc)
            raise
        finally:
            duration_ms = (time.perf_counter() - start) * 1000.0
            if active_span:
                try:
                    active_span.set_attribute("duration_ms", duration_ms)
                    active_span.set_attribute("guardrail.decision", result_context["decision"])
                    active_span.set_attribute("guardrail.threat_detected", result_context["threat_detected"])
                    active_span.set_attribute("guardrail.confidence_score", result_context["confidence_score"])
                    active_span.end()
                except Exception:
                    pass


guard_tracer = AgentGuardPhoenixTracer()
