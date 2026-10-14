# Runbook: AgentGuard Phoenix Guardrail Telemetry & Operations

> **Operational Runbook** for inspecting security evaluation spans, guardrail decisions, and PII protection in AgentGuard.

## 1. Quick Verification

```sh
# Run security scan verification via Python
PYTHONPATH=. python3 -c "
from agentguard.bot import guard_bot
report = guard_bot.scan_interaction('Summarize HR 8278', 'The bill clarifies crypto regulations.')
assert report['decision'] == 'ALLOW'
print('Scan Decision:', report['decision'])
"

# Run pytest on guardrail tests
PYTHONPATH=. pytest tests/test_phoenix_guardrail.py
```

## 2. Telemetry Spans

All security scans emit OpenInference spans:
- `openinference.span.kind`: `GUARDRAIL`
- `guardrail.name`: `comprehensive_security_scan`
- `guardrail.decision`: `ALLOW` | `BLOCK`
- `guardrail.threat_detected`: `true` | `false`
- `guardrail.confidence_score`: float \([0.0, 1.0]\)
