# Contributing to agentest 🧪

Thanks for helping make AI agents reliable and testable! 

`agentest` is designed with modularity at its core so that most contributions require writing **just one self-contained file**:
- A new behavioral assertion in `src/agentest/assertions/`
- A new agent framework adapter in `src/agentest/adapters/`
- A new reporter or diagnostic tool in `src/agentest/reporters/`

---

## 🛠️ Local Development Setup

1. **Fork and Clone** the repository:
   ```bash
   git clone https://github.com/iitking/agentest.git
   cd agentest
   ```

2. **Create and Activate a Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies in Editable Mode**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run the Test Suite & Linter**:
   ```bash
   pytest -v
   ruff check .
   ```

If both commands pass cleanly, your environment is ready!

---

## 🧭 Ways to Contribute

| Area | What you build | Where it lives |
|---|---|---|
| **New Assertion** | Add check for agent behavior (e.g. `tool_arg_schema`, `no_pii`) | `src/agentest/assertions/` |
| **New Adapter** | Connect frameworks (CrewAI, AutoGen, PydanticAI, DSPy, Smolagents) | `src/agentest/adapters/` |
| **Replay & Mocking** | Enhance offline trace playback and tool mock fixtures | `src/agentest/replay.py`, `mocks.py` |
| **Reporters** | Terminal colors, rich diffs, or HTML/JSON exports | `src/agentest/reporters/` |
| **Docs & Examples** | Tutorials ("How to test customer support agents") | `examples/`, `docs/` |

---

## 🔌 How to Add an Adapter

To support a new framework (e.g., CrewAI, AutoGen, OpenAI Agents SDK):

1. Create `src/agentest/adapters/<framework_name>.py`.
2. Subclass `Adapter` and implement `run()`:

```python
# src/agentest/adapters/my_framework.py
from typing import Any, Callable
from agentest.adapters.base import Adapter
from agentest.trace import Step, Trace

class MyFrameworkAdapter(Adapter):
    name = "my_framework"

    def run(
        self,
        agent: Any,
        prompt: str,
        *,
        tools: dict[str, Callable] | None = None,
        mock_tools: dict[str, Callable] | None = None,
    ) -> Trace:
        trace = Trace(prompt=prompt)

        # 1. Execute agent
        result = agent.run(prompt)

        # 2. Extract tool calls and LLM steps into normalized Steps
        # trace.steps.append(Step(kind="tool_call", name="...", args={...}))
        # trace.steps.append(Step(kind="llm", tokens=..., cost_usd=...))

        trace.final_output = result
        trace.steps.append(Step(kind="final", output=result))
        return trace
```

3. Export your class in `src/agentest/adapters/__init__.py`.
4. Add unit tests in `tests/test_<framework_name>_adapter.py` using mock/fake runs (never requiring real API keys in CI).

---

## ✅ How to Add an Assertion

1. Create a function in `src/agentest/assertions/<category>.py` returning a `Check`:

```python
from agentest.trace import Trace
from .base import Check

def contains_tool_arg(trace: Trace, tool_name: str, key: str) -> Check:
    """Assert that whenever tool_name was called, argument 'key' was present."""
    matching_calls = [s for s in trace.tool_calls if s.name == tool_name]
    if not matching_calls:
        return Check(False, f"tool {tool_name!r} was never called", trace)

    missing = [s for s in matching_calls if key not in s.args]
    ok = len(missing) == 0
    return Check(ok, f"all calls to {tool_name!r} contained argument {key!r}", trace)
```

2. Export it in `src/agentest/assertions/__init__.py` and `src/agentest/__init__.py`.
3. Add tests in `tests/test_assertions.py` covering both passing and failing conditions.

---

## 🎯 High-Priority "Good First Issues"

Ready to contribute? Pick one of these:
1. **CrewAI Adapter**: Subclass `Adapter` to parse CrewAI crew executions into a `Trace`.
2. **AutoGen Adapter**: Connect Microsoft AutoGen multi-agent conversable agent turns.
3. **Pydantic AI Adapter**: Wrap PydanticAI agent runs.
4. **Tool Argument Schema Assertion**: Assert tool arguments conform to a JSON Schema or Pydantic model (`assert tool_args_schema(trace, "order_item", Schema)`).
5. **Colored Terminal Reporter**: Enhance failure messages with colored ANSI formatting (green checks, red crosses, yellow highlights).
6. **PR Cost Diff GitHub Action**: Action that inspects trace cost deltas and comments on PRs.

---

## 📋 Pull Request Guidelines

- Branch off `main`: `git checkout -b feat/your-feature-name`
- Run `ruff check .` and make sure it is completely clean.
- Run `pytest` and verify all tests pass.
- Write clear, concise commit messages (e.g. `feat: add crewai adapter`).
- Keep PRs focused: one feature or bug fix per PR makes review and merging fast!

---

## Code of Conduct

We are committed to providing a welcoming, inclusive, and harassment-free community. We adhere to the [Contributor Covenant](https://www.contributor-covenant.org/).
