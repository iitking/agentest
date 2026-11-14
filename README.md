# agentest

**pytest for AI agents.** Write normal pytest tests that check what your agent *did*: which tools it called, in what order, how many steps it took, and how much it cost.

> Working name: `agentest`. Rename before the first PyPI release if you want.

---

## Why this exists

Agent outputs are non-deterministic, so `assert output == "expected"` doesn't work. What you *can* test is behavior:

- Did the agent call the right tool with the right arguments?
- Did it get stuck in a loop?
- Did it stay under a cost / token / step budget?
- Did it avoid a forbidden tool?

`agentest` gives you a small, framework-agnostic way to assert all of this.

## Quickstart (target: under 2 minutes)

```bash
pip install agentest
```

```python
# test_support_agent.py
from agentest import run_agent, tool_called, max_steps, max_cost

def test_refund_flow(agent):
    trace = run_agent(agent, "I want a refund for order #123")

    assert tool_called(trace, "lookup_order", args={"order_id": "123"})
    assert tool_called(trace, "issue_refund")
    assert not tool_called(trace, "delete_account")
    assert max_steps(trace, 8)
    assert max_cost(trace, usd=0.05)
```

```bash
pytest
```

## Core concepts

| Concept | What it is |
|---|---|
| **Trace** | A recorded run: list of steps (LLM call, tool call, tool result, final answer) with tokens, cost, latency |
| **Adapter** | Converts a framework's agent (LangGraph, CrewAI, AutoGen, plain function) into a Trace |
| **Assertion** | A function that checks a Trace (`tool_called`, `max_steps`, `no_loop`, `max_cost`, ...) |
| **Mock tool** | Replaces a real tool with a fixed response so tests are fast and free |
| **Replay** | Saves a Trace to disk and re-runs assertions without calling the LLM again |

## Architecture

```
your test  ->  pytest plugin  ->  Adapter  ->  Agent (LangGraph / CrewAI / ...)
                    |                              |
                    |<------ Trace recorder <------+
                    v
              Assertions  ->  Reporter (terminal / JSON / HTML)
```

### Adapter interface (the only thing a contributor needs to write)

```python
# src/agentest/adapters/base.py
from abc import ABC, abstractmethod
from agentest.trace import Trace

class Adapter(ABC):
    name: str

    @abstractmethod
    def run(self, agent, prompt: str, *, mock_tools: dict | None = None) -> Trace:
        """Run the agent and return a normalized Trace."""
```

One new file in `adapters/` = one new framework supported. Adapters are discovered through Python entry points, so third parties can ship their own packages too.

## Repo structure

```
agentest/
├── src/agentest/
│   ├── __init__.py
│   ├── trace.py            # Trace, Step dataclasses
│   ├── runner.py           # run_agent()
│   ├── plugin.py           # pytest plugin (fixtures, markers, CLI flags)
│   ├── assertions/
│   │   ├── tools.py        # tool_called, tool_order, no_forbidden_tool
│   │   ├── budget.py       # max_steps, max_cost, max_tokens
│   │   └── loops.py        # no_loop (repeated tool+args detection)
│   ├── adapters/
│   │   ├── base.py
│   │   ├── plain_python.py
│   │   ├── langgraph.py
│   │   └── crewai.py
│   ├── mocks.py            # mock_tool()
│   ├── replay.py           # save/load traces
│   └── reporters/
├── tests/
├── examples/
├── docs/
├── CONTRIBUTING.md
├── pyproject.toml
└── README.md
```

## Build plan

### Phase 1: Core (Week 1)
- [ ] `pyproject.toml`, `src/` layout, ruff, mypy, GitHub Actions CI
- [ ] `Trace` and `Step` dataclasses
- [ ] Plain-Python adapter (agent = any callable that uses a tool-calling wrapper)
- [ ] 3 assertions: `tool_called`, `max_steps`, `max_cost`
- [ ] pytest plugin skeleton and one example test

### Phase 2: Useful (Week 2)
- [ ] `no_loop` assertion, `tool_order`, `no_forbidden_tool`
- [ ] `mock_tool()` for deterministic tests
- [ ] LangGraph adapter
- [ ] Nice failure messages that print the trace as a readable timeline

### Phase 3: Sticky (Week 3)
- [ ] Trace replay (save once, re-assert forever, no LLM cost)
- [ ] CrewAI adapter
- [ ] JSON and HTML reporters
- [ ] Docs site (MkDocs) and a demo GIF in this README

### Phase 4: Launch (Week 4)
- [ ] Publish to PyPI
- [ ] Post on Reddit (r/LangChain, r/LocalLLaMA, r/Python), Hacker News "Show HN", X, LinkedIn
- [ ] Open 10-15 `good first issue` tickets (see below)
- [ ] Reply to every issue and PR within 24 hours for the first month

## Good first issues to open on day 1

1. Add `tool_order` assertion
2. Add `no_forbidden_tool` assertion
3. Add AutoGen adapter
4. Add OpenAI Agents SDK adapter
5. Add `max_latency` assertion
6. Colored terminal timeline reporter
7. Add Pydantic AI adapter
8. Write a tutorial: "Test a customer support agent in 5 minutes"
9. Add a `--agentest-record` CLI flag
10. Improve error message when no tool was called

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The short version:

1. Fork and clone
2. `pip install -e ".[dev]"`
3. `pytest` and `ruff check .`
4. Pick an issue labeled `good first issue`
5. Open a PR (small PRs get merged fastest)

## Roadmap

- LLM-as-judge assertions (optional, off by default)
- Regression dashboard across runs
- GitHub Action that comments cost/step diffs on PRs
- JS/TS port

## License

MIT
