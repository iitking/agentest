from __future__ import annotations

from collections.abc import Iterable

from agentest.trace import Trace

from .base import Check


def no_forbidden_tool(trace: Trace, forbidden: str | Iterable[str]) -> Check:
    """Assert that the agent avoided calling any forbidden/prohibited tools.

    Args:
        trace: The recorded execution Trace.
        forbidden: A single tool name or an iterable of tool names that must NOT be called.
    """
    if isinstance(forbidden, str):
        forbidden_set = {forbidden}
    else:
        forbidden_set = set(forbidden)

    called_forbidden = [s.name for s in trace.tool_calls if s.name in forbidden_set]
    if not called_forbidden:
        return Check(True, f"no forbidden tools {sorted(forbidden_set)} were called", trace)

    unique_called = sorted(set(called_forbidden))
    return Check(
        False,
        f"forbidden tool(s) {unique_called} were called during execution",
        trace,
    )
