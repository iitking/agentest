<div align="center">

# 🧪 agentest

### **pytest for AI Agents**
*Assert on what your agent did, not just what it said.*

[![CI](https://github.com/iitking/agentest/actions/workflows/ci.yml/badge.svg)](https://github.com/iitking/agentest/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Pytest](https://img.shields.io/badge/pytest-plugin-0A9EDC.svg?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

<p align="center">
  <a href="#-why-agentest">Why agentest?</a> •
  <a href="#-terminal-demo">Demo</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-quickstart">Quickstart</a> •
  <a href="#-assertions-reference">Assertions</a> •
  <a href="#-trace-replay-for-ci">Replay</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-roadmap">Roadmap</a> •
  <a href="#-contributing">Contributing</a>
</p>

</div>

---

## ⚡ Terminal Demo

![agentest Demo](assets/demo.svg)

---

## 💡 Why agentest?

LLM text outputs are **non-deterministic**, making traditional unit tests brittle and flaky:

```python
# ❌ Flaky & Brittle: Breaks when prompt or LLM wording slightly changes
assert "Your refund of $499 has been processed" in agent.run(prompt)
```

With **agentest**, you test execution behavior instead of text phrasing:

```python
# ✅ Deterministic & Robust: Asserts exactly what actions took place
assert tool_called(trace, "lookup_order", args={"order_id": "123"})
assert tool_called(trace, "issue_refund", args={"amount": 499})
assert no_forbidden_tool(trace, ["delete_account", "drop_db"])
assert tool_order(trace, ["lookup_order", "issue_refund"])
assert no_loop(trace, max_repeats=2)
assert max_steps(trace, 8)
assert max_cost(trace, usd=0.05)
```

### What You Can Test
- 🎯 **Tool Selection**: Did the agent call the right tool with expected arguments?
- 🪜 **Tool Sequence**: Did tools execute in the right order (`tool_order`)?
- 🛑 **Safety Guardrails**: Did it strictly avoid destructive operations (`no_forbidden_tool`)?
- 🔄 **Loop Prevention**: Did it get trapped in an infinite cycle calling the same tool repeatedly (`no_loop`)?
- 💰 **Budget Limits**: Did it stay strictly under your dollar cost, token, and step budgets?
- ⏱️ **Latency Limits**: Did the agent finish execution within your SLA constraints?

---

## 🛠️ Tech Stack

| Component | Technology | Description |
|---|---|---|
| **Language** | Python 3.10+ | Clean modern dataclasses, structural typing, and PEP 585/604 annotations |
| **Testing Engine** | `pytest >= 7.0` | Integrated directly via `pytest11` entry points with markers and fixtures |
| **Linter & Formatter** | [Ruff](https://github.com/astral-sh/ruff) | Blazing-fast linting and import formatting |
| **Type Checker** | [Mypy](https://mypy-lang.org/) | Strict static type checking |
| **Packaging** | [Hatchling](https://hatch.pypa.io/) | Modern PEP 517/PEP 621 build backend and wheel target management |
| **CI / CD** | GitHub Actions | Automated multi-version matrix testing across Python 3.10, 3.11, 3.12, 3.13 |
| **Agent Ecosystem** | Framework-agnostic | Extensible adapter layer for LangGraph, CrewAI, AutoGen, OpenAI Agents SDK, and plain functions |

---

## 🚀 Quickstart

### 1. Installation

```bash
pip install agentest
```

### 2. Write your test

```python
# test_support_agent.py
from agentest import (
    run_agent,
    tool_called,
    tool_order,
    no_forbidden_tool,
    max_steps,
    max_cost,
)
from my_agent import support_agent, TOOLS

def test_refund_flow():
    # Run agent and capture a normalized execution Trace
    trace = run_agent(support_agent, "I want a refund for order #123", tools=TOOLS)

    # Behavior assertions
    assert tool_called(trace, "lookup_order", args={"order_id": "123"})
    assert tool_called(trace, "issue_refund")
    assert tool_order(trace, ["lookup_order", "issue_refund"])
    assert no_forbidden_tool(trace, ["delete_account", "ban_user"])

    # Budget assertions
    assert max_steps(trace, 8)
    assert max_cost(trace, usd=0.05)
```

### 3. Run with pytest

```bash
pytest -v
```

---

## 📖 Assertions Reference

### 🛠️ Tool & Action Checks

```python
from agentest import tool_called, tool_order, no_forbidden_tool, tool_call_count

# Check if a specific tool was invoked (with optional subset argument matching)
assert tool_called(trace, "search_docs", args={"query": "pricing"})

# Check that tools were executed in a required sequence (subsequence or strict contiguous)
assert tool_order(trace, ["lookup_user", "charge_card", "send_email"])
assert tool_order(trace, ["charge_card", "send_email"], strict=True)

# Safety check: ensure hazardous tools were never invoked
assert no_forbidden_tool(trace, ["drop_table", "delete_account"])

# Verify call frequency
assert tool_call_count(trace, "search_docs", count=1)
assert tool_call_count(trace, "llm_retry", max_count=2)
```

### 🔄 Cycle & Loop Detection

```python
from agentest import no_loop

# Detect if the agent called the exact same tool with identical arguments repeatedly
assert no_loop(trace, max_repeats=2)
```

### 💰 Budget & Resource Guardrails

```python
from agentest import max_cost, max_steps, max_tokens, max_latency

assert max_cost(trace, usd=0.02)         # Limit total cost to 2 cents
assert max_steps(trace, limit=6)          # Limit total steps (LLM + tool calls)
assert max_tokens(trace, limit=1500)      # Limit total prompt + completion tokens
assert max_latency(trace, seconds=4.5)    # Limit execution time
```

---

## 📼 Trace Replay for CI (Zero LLM Costs)

Don't want to spend API credits every time CI runs? Use `agentest` Trace Replay:

```python
from agentest import save_trace, load_trace, tool_called, max_cost

# 1. Record once during development
trace = run_agent(my_agent, "test prompt")
save_trace(trace, "tests/fixtures/refund_trace.json")

# 2. Re-assert forever in CI offline (no API keys, zero dollars)
replay_trace = load_trace("tests/fixtures/refund_trace.json")
assert tool_called(replay_trace, "lookup_order")
assert max_cost(replay_trace, usd=0.05)
```

---

## 🎭 Deterministic Mocking

Easily mock third-party APIs or databases:

```python
from agentest import mock_tool, run_agent

# Create a canned mock tool
mock_search = mock_tool("search_db", return_value={"results": ["doc1", "doc2"]})

trace = run_agent(my_agent, "find documents", mock_tools={"search_db": mock_search})

# Inspect mock usage
assert mock_search.called
assert mock_search.call_count == 1
assert mock_search.calls[0] == {"query": "documents"}
```

---

## 🔌 Framework Adapters

### Built-in LangGraph Support

```python
from agentest.adapters import LangGraphAdapter
from agentest import tool_called

adapter = LangGraphAdapter()
trace = adapter.run(compiled_langgraph_agent, "Book a flight to NYC")

assert tool_called(trace, "flight_search", args={"destination": "NYC"})
```

---

## 📊 Rich Failure Diagnostics

When an assertion fails, `agentest` doesn't just print `AssertionError: False`. It prints a full chronological timeline of your agent's run:

```text
FAILED: expected tool 'issue_refund' to be called, but it was not
Trace for prompt: 'I want a refund for order #123'
  1. llm gpt-4o tokens=312 cost=$0.0016
  2. tool_call lookup_order({'order_id': '123'})
  3. llm gpt-4o tokens=180 cost=$0.0009
  4. final output: 'I cannot process this refund request.'
  total: 4 steps, 492 tokens, $0.0025
```

---

## 🏛️ Architecture

```
   Your Test (pytest)
          │
          ▼
   pytest Plugin (`pytest11`)
          │
          ├──▶ Adapter (Plain Python / LangGraph / CrewAI) ──▶ Agent Runtime
          │          │                                                │
          │          └──◀────── Trace Recorder (Steps) ───────────────┘
          ▼
     Assertions (`Check`)
          │
          ▼
   Timeline Reporter (Terminal / JSON / HTML)
```

---

## 📂 Repository Layout

```
agentest/
├── .github/
│   ├── workflows/ci.yml         # Multi-version matrix CI (Python 3.10-3.13)
│   ├── ISSUE_TEMPLATE/          # Structured templates for new adapters & assertions
│   │   ├── 01_new_adapter.yml
│   │   ├── 02_new_assertion.yml
│   │   ├── 03_bug_report.yml
│   │   └── 04_feature_request.yml
│   ├── PULL_REQUEST_TEMPLATE.md # PR checklist
│   └── dependabot.yml           # Automated weekly security updates
├── assets/
│   └── demo.svg                 # Dark-mode terminal visual asset
├── src/agentest/
│   ├── __init__.py              # Unified exports
│   ├── trace.py                 # Trace and Step dataclasses + timeline formatter
│   ├── runner.py                # run_agent() execution wrapper
│   ├── plugin.py                # pytest plugin hooks and fixtures
│   ├── mocks.py                 # mock_tool and MockTool helpers
│   ├── replay.py                # save_trace() and load_trace() JSON serializers
│   ├── assertions/
│   │   ├── base.py              # Check dataclass
│   │   ├── tools.py             # tool_called, tool_call_count
│   │   ├── order.py             # tool_order (strict and relaxed)
│   │   ├── safety.py            # no_forbidden_tool
│   │   ├── loops.py             # no_loop (cycle detection)
│   │   ├── budget.py            # max_steps, max_cost, max_tokens
│   │   └── latency.py           # max_latency
│   └── adapters/
│       ├── base.py              # Adapter abstract base class
│       ├── plain_python.py      # PlainPythonAdapter & Recorder
│       └── langgraph.py         # LangGraphAdapter
├── examples/
│   ├── support_agent.py         # Demo agent implementation
│   └── test_support_agent.py    # Executable example tests
├── tests/
│   ├── test_assertions.py       # Full assertions test suite
│   ├── test_replay.py           # Serialization & replay tests
│   ├── test_mocks.py            # MockTool tests
│   └── test_langgraph_adapter.py# LangGraph adapter tests
├── CONTRIBUTING.md              # Contributor onboarding & guide
├── pyproject.toml               # Build configuration
└── README.md
```

---

## 🗺️ Roadmap

- [x] **Phase 1: Core Architecture**
  - [x] Modern `pyproject.toml` layout with Hatchling backend
  - [x] GitHub Actions automated CI matrix (Python 3.10–3.13)
  - [x] `Trace` and `Step` dataclasses with `timeline()` formatting
  - [x] `PlainPythonAdapter` and `Recorder`
  - [x] Pytest plugin skeleton with `@pytest.mark.agent` and `agent_runner` fixture

- [x] **Phase 2: Behavioral Guardrails & Adapters**
  - [x] `tool_order` assertion (strict and relaxed sequence matching)
  - [x] `no_forbidden_tool` assertion
  - [x] `no_loop` repeated tool call cycle detection
  - [x] `max_latency` and `tool_call_count` assertions
  - [x] LangGraph adapter (`LangGraphAdapter`)
  - [x] Deterministic `mock_tool` helper
  - [x] Trace replay (`save_trace`, `load_trace`) for zero-cost offline CI

- [ ] **Phase 3: Community & Expanded Ecosystem (Contributions Wanted! 🚀)**
  - [ ] CrewAI adapter (`CrewAIAdapter`)
  - [ ] Microsoft AutoGen adapter (`AutoGenAdapter`)
  - [ ] Pydantic AI adapter (`PydanticAIAdapter`)
  - [ ] OpenAI Agents SDK / LiteLLM adapter
  - [ ] Colored terminal timeline reporter
  - [ ] HTML / JSON test report export

- [ ] **Phase 4: Launch & Distribution**
  - [ ] Publish to PyPI (`pip install agentest`)
  - [ ] GitHub Action that comments cost and step diffs on PRs
  - [ ] MkDocs documentation site

---

## 🤝 Contributing

We want you to build with us! Whether you want to add an adapter for your favorite framework, propose a new safety check, or write a tutorial:

1. **Fork & Clone**:
   ```bash
   git clone https://github.com/iitking/agentest.git
   cd agentest
   ```
2. **Setup virtual environment**:
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -e ".[dev]"
   ```
3. **Verify tests & linting**:
   ```bash
   pytest
   ruff check .
   ```
4. **Submit a PR**: Check out [CONTRIBUTING.md](CONTRIBUTING.md) for full details and open issues!

---

## 📜 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

<div align="center">
  <b>Built with ❤️ by <a href="https://github.com/iitking">Nivesh Kumar Meena</a> and contributors</b>
</div>
