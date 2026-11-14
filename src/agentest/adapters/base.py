from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional

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
        tools: Optional[Dict[str, Callable]] = None,
        mock_tools: Optional[Dict[str, Callable]] = None,
    ) -> Trace:
        """Run the agent and return a normalized Trace."""
