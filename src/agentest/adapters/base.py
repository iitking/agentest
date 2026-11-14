from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from agentest.trace import Trace


class Adapter(ABC):
    """Converts one agent framework into agentest Traces.

    To support a new framework, subclass this in a new file in adapters/.
    """

    name: str

    @abstractmethod
    def run(
        self,
        agent: Any,
        prompt: str,
        *,
        tools: dict[str, Callable] | None = None,
        mock_tools: dict[str, Callable] | None = None,
    ) -> Trace:
        """Run the agent and return a normalized Trace."""
