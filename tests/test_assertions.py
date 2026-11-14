import pytest

from agentest import Step, Trace, max_cost, max_steps, max_tokens, run_agent, tool_called


def make_trace():
    return Trace(
        prompt="hi",
        steps=[
            Step(kind="llm", tokens=100, cost_usd=0.01),
            Step(kind="tool_call", name="search", args={"q": "cats", "limit": 5}),
            Step(kind="final", output="done"),
        ],
    )


def test_tool_called_by_name():
    assert tool_called(make_trace(), "search")


def test_tool_called_missing():
    assert not tool_called(make_trace(), "delete")


def test_tool_called_args_subset_match():
    assert tool_called(make_trace(), "search", args={"q": "cats"})


def test_tool_called_args_mismatch():
    assert not tool_called(make_trace(), "search", args={"q": "dogs"})


def test_budget_assertions():
    t = make_trace()
    assert max_steps(t, 3)
    assert not max_steps(t, 2)
    assert max_cost(t, usd=0.02)
    assert not max_cost(t, usd=0.001)
    assert max_tokens(t, 100)
    assert not max_tokens(t, 99)


def test_failure_message_contains_timeline():
    check = tool_called(make_trace(), "delete")
    assert "expected tool 'delete'" in repr(check)
    assert "tool_call search" in repr(check)


def test_runner_records_steps_and_unknown_tool_errors():
    def agent(prompt, rec):
        return rec.call_tool("nope")

    with pytest.raises(KeyError):
        run_agent(agent, "x", tools={})
