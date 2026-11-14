"""Check: a truthy/falsy result that carries a readable failure message.

Usage:  assert tool_called(trace, "search")
When it fails, pytest shows the message and the trace timeline.
"""
from __future__ import annotations

from agentest.trace import Trace


class Check:
    def __init__(self, ok: bool, message: str, trace: Trace):
        self.ok = ok
        self.message = message
        self.trace = trace

    def __bool__(self) -> bool:
        return self.ok

    def __repr__(self) -> str:
        status = "PASSED" if self.ok else "FAILED"
        return f"{status}: {self.message}\n{self.trace.timeline()}"
