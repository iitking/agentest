from __future__ import annotations

from agentest.trace import Trace

from .base import Check


def max_latency(trace: Trace, seconds: float) -> Check:
    """Assert that the total execution latency was under the specified threshold.

    Args:
        trace: The recorded execution Trace.
        seconds: Maximum acceptable duration in seconds.
    """
    total_latency = sum(s.latency_s for s in trace.steps)
    ok = total_latency <= seconds
    return Check(
        ok,
        f"total latency {total_latency:.2f}s (limit {seconds:.2f}s)",
        trace,
    )
