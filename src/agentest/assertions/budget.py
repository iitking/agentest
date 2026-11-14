from __future__ import annotations

from agentest.trace import Trace

from .base import Check


def max_steps(trace: Trace, limit: int) -> Check:
    ok = trace.step_count <= limit
    return Check(ok, f"steps {trace.step_count} (limit {limit})", trace)


def max_cost(trace: Trace, usd: float) -> Check:
    ok = trace.total_cost <= usd
    return Check(ok, f"cost ${trace.total_cost:.4f} (limit ${usd:.4f})", trace)


def max_tokens(trace: Trace, limit: int) -> Check:
    ok = trace.total_tokens <= limit
    return Check(ok, f"tokens {trace.total_tokens} (limit {limit})", trace)
