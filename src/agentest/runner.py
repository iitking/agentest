from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from agentest.adapters import Adapter, PlainPythonAdapter
from agentest.trace import Trace


def run_agent(
    agent: Any,
    prompt: str,
    *,
    tools: Optional[Dict[str, Callable]] = None,
    mock_tools: Optional[Dict[str, Callable]] = None,
    adapter: Optional[Adapter] = None,
) -> Trace:
    """Run an agent and return its Trace. Defaults to the plain-Python adapter."""
    adapter = adapter or PlainPythonAdapter()
    return adapter.run(agent, prompt, tools=tools, mock_tools=mock_tools)
