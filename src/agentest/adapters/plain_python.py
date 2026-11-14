"""Adapter for plain Python agents.

An agent is any callable:  agent(prompt, rec) -> final_output
It talks to tools through `rec.call_tool(name, **args)` and reports LLM usage
through `rec.log_llm(tokens=..., cost_usd=...)`.
"""
from __future__ import annotations

import time
from typing import Any, Callable, Dict, Optional

from agentest.trace import Step, Trace

from .base import Adapter


class Recorder:
    def __init__(self, trace: Trace, tools: Dict[str, Callable]):
        self.trace = trace
        self.tools = tools

    def call_tool(self, name: str, **args: Any) -> Any:
        if name not in self.tools:
            raise KeyError(f"tool {name!r} is not registered")
        start = time.perf_counter()
        output = self.tools[name](**args)
        self.trace.steps.append(
            Step(kind="tool_call", name=name, args=args, output=output,
                 latency_s=time.perf_counter() - start)
        )
        return output

    def log_llm(self, tokens: int = 0, cost_usd: float = 0.0, model: Optional[str] = None) -> None:
        self.trace.steps.append(Step(kind="llm", name=model, tokens=tokens, cost_usd=cost_usd))


class PlainPythonAdapter(Adapter):
    name = "plain_python"

    def run(self, agent, prompt, *, tools=None, mock_tools=None) -> Trace:
        trace = Trace(prompt=prompt)
        effective_tools = {**(tools or {}), **(mock_tools or {})}  # mocks win
        rec = Recorder(trace, effective_tools)
        trace.final_output = agent(prompt, rec)
        trace.steps.append(Step(kind="final", output=trace.final_output))
        return trace
