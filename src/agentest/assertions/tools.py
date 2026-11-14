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
