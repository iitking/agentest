"""Adapter for LangGraph agents.

Converts LangGraph compiled graphs (StateGraph) and message histories into normalized agentest Traces.
"""
from __future__ import annotations

import time
from typing import Any, Callable

from agentest.trace import Step, Trace

from .base import Adapter


class LangGraphAdapter(Adapter):
    name = "langgraph"

    def run(
        self,
        agent: Any,
        prompt: str,
        *,
        tools: dict[str, Callable] | None = None,
        mock_tools: dict[str, Callable] | None = None,
    ) -> Trace:
        trace = Trace(prompt=prompt)
        input_payload = {"messages": [("user", prompt)]}
        start_time = time.perf_counter()

        # Execute graph (supports .invoke or callable)
        if hasattr(agent, "invoke") and callable(agent.invoke):
            result = agent.invoke(input_payload)
        elif callable(agent):
            result = agent(input_payload)
        else:
            raise TypeError(f"agent {agent!r} must be callable or have an .invoke() method")

        total_latency = time.perf_counter() - start_time

        # Extract message objects/dicts
        messages: list[Any] = []
        if isinstance(result, dict) and "messages" in result:
            messages = result["messages"]
        elif hasattr(result, "messages"):
            messages = getattr(result, "messages")
        elif isinstance(result, list):
            messages = result

        for msg in messages:
            # Check for tool_calls attached to message
            tool_calls = getattr(msg, "tool_calls", None) or (
                msg.get("tool_calls") if isinstance(msg, dict) else None
            )
            if tool_calls:
                for tc in tool_calls:
                    name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
                    args = tc.get("args") if isinstance(tc, dict) else getattr(tc, "args", {})
                    trace.steps.append(Step(kind="tool_call", name=name, args=args))

            # Check for tool result messages
            msg_type = getattr(msg, "type", None) or (
                msg.get("type") if isinstance(msg, dict) else None
            )
            if msg_type == "tool":
                tool_name = getattr(msg, "name", None) or (
                    msg.get("name") if isinstance(msg, dict) else None
                )
                content = getattr(msg, "content", None) or (
                    msg.get("content") if isinstance(msg, dict) else None
                )
                trace.steps.append(Step(kind="tool_result", name=tool_name, output=content))

            # Extract usage metadata / token usage if present
            usage = getattr(msg, "usage_metadata", None) or (
                msg.get("usage_metadata") if isinstance(msg, dict) else None
            )
            if usage:
                tokens = (
                    usage.get("total_tokens", 0)
                    if isinstance(usage, dict)
                    else getattr(usage, "total_tokens", 0)
                )
                trace.steps.append(Step(kind="llm", tokens=tokens))

        # Determine final text output
        final_output: Any = ""
        if messages:
            last_msg = messages[-1]
            final_output = getattr(last_msg, "content", None) or (
                last_msg.get("content") if isinstance(last_msg, dict) else str(last_msg)
            )
        else:
            final_output = result

        trace.final_output = final_output
        trace.steps.append(Step(kind="final", output=final_output, latency_s=total_latency))
        return trace
