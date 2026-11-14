from __future__ import annotations

from typing import Any

from agentest.trace import Trace

from .base import Check


def tool_called(trace: Trace, name: str, args: dict[str, Any] | None = None) -> Check:
    """True if the agent called tool `name`.

    If `args` is given, the call must contain those key/value pairs
    (extra arguments in the call are allowed).
    """
    for step in trace.tool_calls:
        if step.name != name:
            continue
        if args is None or all(step.args.get(k) == v for k, v in args.items()):
            return Check(True, f"tool {name!r} was called", trace)
    detail = f" with args {args}" if args else ""
    return Check(False, f"expected tool {name!r} to be called{detail}, but it was not", trace)


def tool_call_count(
    trace: Trace,
    name: str,
    *,
    count: int | None = None,
    min_count: int | None = None,
    max_count: int | None = None,
) -> Check:
    """Assert on how many times tool `name` was called.

    Args:
        trace: The recorded execution Trace.
        name: Name of the tool.
        count: Exact expected call count.
        min_count: Minimum acceptable call count.
        max_count: Maximum acceptable call count.
    """
    actual_count = sum(1 for s in trace.tool_calls if s.name == name)

    if count is not None and actual_count != count:
        return Check(
            False,
            f"expected tool {name!r} to be called exactly {count} times, got {actual_count}",
            trace,
        )
    if min_count is not None and actual_count < min_count:
        return Check(
            False,
            f"expected tool {name!r} to be called at least {min_count} times, got {actual_count}",
            trace,
        )
    if max_count is not None and actual_count > max_count:
        return Check(
            False,
            f"expected tool {name!r} to be called at most {max_count} times, got {actual_count}",
            trace,
        )

    return Check(
        True,
        f"tool {name!r} call count ({actual_count}) is within expectations",
        trace,
    )
