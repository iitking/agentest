from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from agentest.trace import Step, Trace


def save_trace(trace: Trace, path: str | Path) -> None:
    """Save an execution Trace to disk as JSON for offline replay and CI test suites."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    data = asdict(trace)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_trace(path: str | Path) -> Trace:
    """Load a serialized Trace from a JSON file.

    Enables re-running behavioral assertions in CI with zero LLM API costs.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Trace file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    steps = [
        Step(
            kind=s.get("kind", "unknown"),
            name=s.get("name"),
            args=s.get("args", {}),
            output=s.get("output"),
            tokens=s.get("tokens", 0),
            cost_usd=s.get("cost_usd", 0.0),
            latency_s=s.get("latency_s", 0.0),
        )
        for s in data.get("steps", [])
    ]

    return Trace(
        prompt=data.get("prompt", ""),
        steps=steps,
        final_output=data.get("final_output"),
    )
