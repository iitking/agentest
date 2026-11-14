# Contributing to agentest

Thanks for helping! agentest is built so that most contributions are **one small file**: a new assertion, a new adapter, or a new reporter.

## Setup

```bash
git clone https://github.com/<your-username>/agentest.git
cd agentest
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check .
```

If `pytest` passes, you're ready.

## Ways to contribute

| I want to... | Where to look |
|---|---|
| Add an assertion (e.g. `tool_order`) | `src/agentest/assertions/` |
| Support a new framework (AutoGen, OpenAI Agents SDK, ...) | `src/agentest/adapters/` |
| Improve error messages or reports | `src/agentest/trace.py`, `reporters/` |
| Write docs or a tutorial | `docs/`, `examples/` |
| Fix a bug | open an issue first, then a PR |

Look for issues labeled **good first issue**.

## Adding an assertion

1. Create a function in `src/agentest/assertions/` that takes a `Trace` and returns a `Check`:

```python
from agentest.trace import Trace
from .base import Check

def max_latency(trace: Trace, seconds: float) -> Check:
    total = sum(s.latency_s for s in trace.steps)
    return Check(total <= seconds, f"latency {total:.2f}s (limit {seconds}s)", trace)
```

2. Export it in `assertions/__init__.py` and `agentest/__init__.py`.
3. Add tests in `tests/` for both the passing and failing case.

## Adding an adapter

1. Create `src/agentest/adapters/<framework>.py` and subclass `Adapter`.
2. Implement `run()` so it returns a normalized `Trace` (record every LLM call and tool call as a `Step`).
3. Add a small example in `examples/` and a test that does not need a real API key (use a fake or mocked model).

## Pull request checklist

- [ ] Tests added or updated, and `pytest` passes
- [ ] `ruff check .` is clean
- [ ] Public functions have a one-line docstring
- [ ] PR is small and focused (one thing per PR)
- [ ] No API keys or secrets committed

## Style

- Python 3.9+ compatible, type hints on public functions
- Keep dependencies minimal: the core should only depend on `pytest`
- Be kind in reviews. We follow the [Contributor Covenant](https://www.contributor-covenant.org/).

## Questions

Open a GitHub Discussion or an issue. We reply within 24 hours.
