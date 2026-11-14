from __future__ import annotations

from agentest.trace import Trace

from .base import Check


def tool_order(trace: Trace, expected_order: list[str], strict: bool = False) -> Check:
    """Assert tools were called in the specified sequence.

    Args:
        trace: The execution Trace to check.
        expected_order: List of tool names in expected order of invocation.
        strict: If False (default), other tool calls may appear between the expected ones.
                If True, expected_order must match consecutively without intermediate tools.
    """
    actual_calls = [s.name for s in trace.tool_calls if s.name is not None]

    if not expected_order:
        return Check(True, "expected_order is empty", trace)

    if strict:
        for i in range(len(actual_calls) - len(expected_order) + 1):
            if actual_calls[i : i + len(expected_order)] == expected_order:
                return Check(True, f"tools were called in strict order: {expected_order}", trace)
        return Check(
            False,
            f"expected tools in strict order {expected_order}, actual sequence was {actual_calls}",
            trace,
        )

    # Subsequence check
    it = iter(actual_calls)
    matched = all(target in it for target in expected_order)
    if matched:
        return Check(True, f"tools were called in order: {expected_order}", trace)
    return Check(
        False,
        f"expected tools in order {expected_order}, actual sequence was {actual_calls}",
        trace,
    )
