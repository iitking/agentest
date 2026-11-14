from __future__ import annotations

import json
from typing import Any

from agentest.trace import Trace

from .base import Check


def _serialize_args(args: dict[str, Any]) -> str:
    try:
        return json.dumps(args, sort_keys=True, default=str)
    except (TypeError, ValueError):
        return str(sorted(args.items()))


def no_loop(trace: Trace, max_repeats: int = 2) -> Check:
    """Assert that the agent did not get trapped in an infinite cycle or loop.

    Detects if the agent repeatedly calls the same tool with identical arguments.

    Args:
        trace: The recorded execution Trace.
        max_repeats: Maximum allowed calls to the exact same tool with identical arguments.
    """
    call_counts: dict[tuple[str, str], int] = {}

    for step in trace.tool_calls:
        tool_name = step.name or ""
        arg_key = _serialize_args(step.args)
        key = (tool_name, arg_key)
        call_counts[key] = call_counts.get(key, 0) + 1

        if call_counts[key] > max_repeats:
            return Check(
                False,
                f"loop detected: tool {tool_name!r} was called {call_counts[key]} times with identical args {step.args} (max allowed {max_repeats})",
                trace,
            )

    return Check(True, f"no repetitive tool call loops detected (limit {max_repeats})", trace)
