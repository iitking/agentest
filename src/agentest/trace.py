"""Trace: a normalized record of everything an agent did during one run."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Step:
    kind: str  # "llm" | "tool_call" | "final"
    name: Optional[str] = None  # tool name for tool_call, model name for llm
    args: Dict[str, Any] = field(default_factory=dict)
    output: Any = None
    tokens: int = 0
    cost_usd: float = 0.0
    latency_s: float = 0.0


@dataclass
class Trace:
    prompt: str
    steps: List[Step] = field(default_factory=list)
    final_output: Any = None

    @property
    def tool_calls(self) -> List[Step]:
        return [s for s in self.steps if s.kind == "tool_call"]

    @property
    def step_count(self) -> int:
        return len(self.steps)

    @property
    def total_tokens(self) -> int:
        return sum(s.tokens for s in self.steps)

    @property
    def total_cost(self) -> float:
        return sum(s.cost_usd for s in self.steps)

    def timeline(self) -> str:
        """Human-readable timeline, printed when an assertion fails."""
        lines = [f"Trace for prompt: {self.prompt!r}"]
        for i, s in enumerate(self.steps, 1):
            if s.kind == "tool_call":
                lines.append(f"  {i}. tool_call {s.name}({s.args})")
            elif s.kind == "llm":
                lines.append(f"  {i}. llm {s.name or ''} tokens={s.tokens} cost=${s.cost_usd:.4f}")
            else:
                lines.append(f"  {i}. {s.kind}")
        lines.append(f"  total: {self.step_count} steps, {self.total_tokens} tokens, "
                     f"${self.total_cost:.4f}")
        return "\n".join(lines)
