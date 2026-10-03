"""FinOps Token Telemetry and Histogram Analytics Subsystem for AgentGuard."""

from __future__ import annotations

import datetime
import json
import math
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# Benchmark pricing tiers (USD per 1M tokens)
TIER_PRICING: Dict[str, Dict[str, float]] = {
    "light": {"input": 0.15, "output": 0.60},
    "standard": {"input": 3.00, "output": 15.00},
    "reasoning": {"input": 15.00, "output": 60.00},
}


@dataclass
class TokenTelemetry:
    """Manages token telemetry ledger and computes distribution histograms."""

    workspace_dir: Path = field(default_factory=Path.cwd)

    @property
    def ledger_path(self) -> Path:
        return self.workspace_dir / ".agentguard" / "finops" / "token_telemetry.jsonl"

    def estimate(
        self,
        prompt: str,
        completion: str = "",
        tier: str = "standard",
    ) -> Dict[str, Any]:
        """Estimate token counts and projected cost for a prompt and completion."""
        p_len = len(prompt)
        c_len = len(completion)
        p_tok = max(1, math.ceil(p_len / 4.0)) if p_len > 0 else 0
        c_tok = max(1, math.ceil(c_len / 4.0)) if c_len > 0 else 0
        tot_tok = p_tok + c_tok

        tier_key = tier.lower() if tier.lower() in TIER_PRICING else "standard"
        pricing = TIER_PRICING[tier_key]
        cost = (p_tok / 1_000_000.0) * pricing["input"] + (c_tok / 1_000_000.0) * pricing["output"]

        return {
            "prompt_length_chars": p_len,
            "prompt_tokens": p_tok,
            "completion_length_chars": c_len,
            "completion_tokens": c_tok,
            "total_tokens": tot_tok,
            "tier": tier_key,
            "estimated_cost_usd": round(cost, 8),
        }

    def _ensure_dir(self) -> None:
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        prompt: str,
        user_id: str = "default_user",
        model: str = "claude-3-5-sonnet",
        tier: str = "standard",
        completion: str = "",
        session_id: str = "",
        agent_id: str = "agentguard-bot",
        latency_ms: float = 0.0,
        cached: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Record an agent interaction to the token telemetry ledger."""
        self._ensure_dir()
        p_len = len(prompt)
        c_len = len(completion)
        p_tok = max(1, math.ceil(p_len / 4.0)) if p_len > 0 else 0
        c_tok = max(1, math.ceil(c_len / 4.0)) if c_len > 0 else 0
        tot_tok = p_tok + c_tok

        tier_key = tier.lower() if tier.lower() in TIER_PRICING else "standard"
        pricing = TIER_PRICING[tier_key]
        cost = (p_tok / 1_000_000.0) * pricing["input"] + (c_tok / 1_000_000.0) * pricing["output"]
        if cached:
            cost = 0.0

        rec = {
            "id": f"tok_{uuid.uuid4().hex[:12]}",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "timestamp_ns": int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1_000_000_000),
            "user_id": user_id,
            "agent_id": agent_id,
            "session_id": session_id,
            "prompt_length_chars": p_len,
            "prompt_tokens": p_tok,
            "completion_length_chars": c_len,
            "completion_tokens": c_tok,
            "total_tokens": tot_tok,
            "model": model,
            "tier": tier,
            "cost_usd": round(cost, 8),
            "latency_ms": round(latency_ms, 2),
            "cached": cached,
            "metadata": metadata or {},
        }

        with self.ledger_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")

        return rec

    def list_records(
        self,
        user_id: Optional[str] = None,
        model: Optional[str] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tier: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """List telemetry records matching filter criteria."""
        if not self.ledger_path.exists():
            return []

        records: List[Dict[str, Any]] = []
        with self.ledger_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if user_id and data.get("user_id") != user_id:
                        continue
                    if model and data.get("model") != model:
                        continue
                    if agent_id and data.get("agent_id") != agent_id:
                        continue
                    if session_id and data.get("session_id") != session_id:
                        continue
                    if tier and data.get("tier") != tier:
                        continue
                    records.append(data)
                except Exception:
                    continue

        return records[-limit:] if limit > 0 else records

    def histogram(
        self,
        metric: str = "prompt_tokens",
        user_id: Optional[str] = None,
        model: Optional[str] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tier: Optional[str] = None,
        bins_count: int = 10,
        max_bar_width: int = 25,
    ) -> Dict[str, Any]:
        """Compute equal-width statistical histogram of token telemetry records."""
        records = self.list_records(
            user_id=user_id,
            model=model,
            agent_id=agent_id,
            session_id=session_id,
            tier=tier,
            limit=10_000,
        )
        tot_recs = len(records)
        tot_tok = sum(r.get("total_tokens", 0) for r in records)
        tot_cost = round(sum(r.get("cost_usd", 0.0) for r in records), 6)

        values: List[float] = [float(r.get(metric, r.get("prompt_tokens", 0))) for r in records]

        if not values:
            return {
                "metric": metric,
                "total_records": 0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "stats": {"min": 0, "max": 0, "mean": 0, "median": 0, "p95": 0, "p99": 0, "std_dev": 0},
                "bins": [],
                "model_distribution": {},
            }

        values.sort()
        val_min = values[0]
        val_max = values[-1]
        val_sum = sum(values)
        val_mean = round(val_sum / tot_recs, 2)

        def percentile(p: float) -> float:
            k = (tot_recs - 1) * p
            f = math.floor(k)
            c = math.ceil(k)
            if f == c:
                return values[int(k)]
            d0 = values[int(f)] * (c - k)
            d1 = values[int(c)] * (k - f)
            return d0 + d1

        val_median = round(percentile(0.50), 2)
        val_p95 = round(percentile(0.95), 2)
        val_p99 = round(percentile(0.99), 2)

        variance = sum((x - val_mean) ** 2 for x in values) / tot_recs if tot_recs > 0 else 0.0
        val_std_dev = round(math.sqrt(variance), 2)

        # Build equal-width bins
        b_count = max(1, bins_count)
        span = val_max - val_min
        step = span / b_count if span > 0 else 1.0

        bin_counts = [0] * b_count
        for v in values:
            if span == 0:
                bin_idx = 0
            else:
                bin_idx = min(int((v - val_min) / step), b_count - 1)
            bin_counts[bin_idx] += 1

        max_count = max(bin_counts) if bin_counts else 1
        cum_count = 0
        bins_data: List[Dict[str, Any]] = []

        for i in range(b_count):
            c = bin_counts[i]
            cum_count += c
            st = val_min + (i * step)
            en = val_min + ((i + 1) * step) if i < b_count - 1 else val_max
            pct = round((c / tot_recs) * 100.0, 2) if tot_recs > 0 else 0.0
            cum_pct = round((cum_count / tot_recs) * 100.0, 2) if tot_recs > 0 else 0.0

            bar_len = int(round((c / max_count) * max_bar_width)) if max_count > 0 else 0
            ascii_bar = "█" * bar_len

            bins_data.append({
                "bin_index": i + 1,
                "bin_start": round(st, 2),
                "bin_end": round(en, 2),
                "count": c,
                "percentage": pct,
                "cumulative_percentage": cum_pct,
                "ascii_bar": ascii_bar,
            })

        # Model Distribution breakdown
        model_dist: Dict[str, Dict[str, Any]] = {}
        for r in records:
            m = r.get("model", "unknown")
            if m not in model_dist:
                model_dist[m] = {"count": 0, "tokens": 0, "cost_usd": 0.0}
            model_dist[m]["count"] += 1
            model_dist[m]["tokens"] += r.get("total_tokens", 0)
            model_dist[m]["cost_usd"] = round(model_dist[m]["cost_usd"] + r.get("cost_usd", 0.0), 6)

        return {
            "metric": metric,
            "total_records": tot_recs,
            "total_tokens": tot_tok,
            "total_cost_usd": tot_cost,
            "stats": {
                "min": round(val_min, 2),
                "max": round(val_max, 2),
                "mean": val_mean,
                "median": val_median,
                "p95": val_p95,
                "p99": val_p99,
                "std_dev": val_std_dev,
            },
            "bins": bins_data,
            "model_distribution": model_dist,
        }

    def generate_report(
        self,
        user_id: str = "default_user",
        days: int = 90,
    ) -> Dict[str, Any]:
        """Generate comprehensive FinOps token telemetry analysis report."""
        hist = self.histogram(user_id=user_id, bins_count=10)
        tot_recs = hist.get("total_records", 0)
        tot_tok = hist.get("total_tokens", 0)
        tot_cost = hist.get("total_cost_usd", 0.0)
        stats = hist.get("stats", {})
        bins = hist.get("bins", [])
        model_dist = hist.get("model_distribution", {})

        records = self.list_records(user_id=user_id, limit=10_000)
        prompt_tok = sum(r.get("prompt_tokens", 0) for r in records)
        completion_tok = sum(r.get("completion_tokens", 0) for r in records)

        # Format ASCII table
        ascii_lines = [
            "Range           Count      %     Cumulative %  Distribution",
            "-------------------------------------------------------------------------",
        ]
        for b in bins:
            st = b.get("bin_start", 0)
            en = b.get("bin_end", 0)
            c = b.get("count", 0)
            pct = b.get("percentage", 0.0)
            cum = b.get("cumulative_percentage", 0.0)
            bar = b.get("ascii_bar", "")
            range_str = f"[{st:.1f} - {en:.1f}]".ljust(15)
            ascii_lines.append(f"{range_str} {str(c).rjust(5)}   {pct:5.1f}%     {cum:5.1f}%      {bar}")

        ascii_histogram = "\n".join(ascii_lines)

        return {
            "success": True,
            "user_id": user_id,
            "days": days,
            "total_records": tot_recs,
            "total_prompt_tokens": prompt_tok,
            "total_completion_tokens": completion_tok,
            "total_tokens": tot_tok,
            "total_cost_usd": tot_cost,
            "stats": stats,
            "ascii_histogram": ascii_histogram,
            "bins": bins,
            "model_distribution": model_dist,
        }
