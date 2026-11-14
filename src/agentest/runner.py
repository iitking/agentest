from __future__ import annotations

from collections.abc import Callable
from typing import Any

from agentest.adapters import Adapter, PlainPythonAdapter
from agentest.trace import Trace


def run_agent(
    agent: Any,
    prompt: str,
    *,
    tools: dict[str, Callable] | None = None,
    mock_tools: dict[str, Callable] | None = None,
    adapter: Adapter | None = None,
) -> Trace:
    """Run an agent and return its Trace. Defaults to the plain-Python adapter."""
    adapter = adapter or PlainPythonAdapter()
    return adapter.run(agent, prompt, tools=tools, mock_tools=mock_tools)
