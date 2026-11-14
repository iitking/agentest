from __future__ import annotations

from collections.abc import Callable
from typing import Any


class MockTool:
    """Mock tool helper for recording tool calls and providing canned deterministic responses."""

    def __init__(
        self,
        name: str,
        *,
        return_value: Any = None,
        side_effect: Callable[..., Any] | None = None,
    ):
        self.name = name
        self.return_value = return_value
        self.side_effect = side_effect
        self.calls: list[dict[str, Any]] = []

    def __call__(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        if self.side_effect is not None:
            return self.side_effect(**kwargs)
        return self.return_value

    @property
    def call_count(self) -> int:
        return len(self.calls)

    @property
    def called(self) -> bool:
        return len(self.calls) > 0

    def reset(self) -> None:
        self.calls.clear()


def mock_tool(
    name: str,
    *,
    return_value: Any = None,
    side_effect: Callable[..., Any] | None = None,
) -> MockTool:
    """Create a mock tool callable for unit testing agents without network or external side-effects."""
    return MockTool(name, return_value=return_value, side_effect=side_effect)
