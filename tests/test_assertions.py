import pytest

from agentest import (
    Step,
    Trace,
    max_cost,
    max_latency,
    max_steps,
    max_tokens,
    no_forbidden_tool,
    no_loop,
    run_agent,
    tool_call_count,
    tool_called,
    tool_order,
)


def make_trace():
    return Trace(
        prompt="hi",
        steps=[
            Step(kind="llm", tokens=100, cost_usd=0.01, latency_s=0.5),
            Step(kind="tool_call", name="search", args={"q": "cats", "limit": 5}, latency_s=0.3),
            Step(kind="final", output="done", latency_s=0.2),
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


def test_latency_assertion():
    t = make_trace()
    # Total latency is 0.5 + 0.3 + 0.2 = 1.0s
    assert max_latency(t, 1.5)
    assert not max_latency(t, 0.8)


def test_failure_message_contains_timeline():
    check = tool_called(make_trace(), "delete")
    assert "expected tool 'delete'" in repr(check)
    assert "tool_call search" in repr(check)


def test_runner_records_steps_and_unknown_tool_errors():
    def agent(prompt, rec):
        return rec.call_tool("nope")

    with pytest.raises(KeyError):
        run_agent(agent, "x", tools={})


def test_tool_order_assertions():
    trace = Trace(
        prompt="order flow",
        steps=[
            Step(kind="tool_call", name="lookup_user"),
            Step(kind="tool_call", name="fetch_inventory"),
            Step(kind="tool_call", name="create_order"),
            Step(kind="tool_call", name="send_confirmation"),
        ],
    )

    # Subsequence matching (non-strict)
    assert tool_order(trace, ["lookup_user", "create_order"])
    assert tool_order(trace, ["lookup_user", "fetch_inventory", "send_confirmation"])
    assert not tool_order(trace, ["send_confirmation", "lookup_user"])

    # Strict contiguous matching
    assert tool_order(trace, ["fetch_inventory", "create_order"], strict=True)
    assert not tool_order(trace, ["lookup_user", "create_order"], strict=True)


def test_no_forbidden_tool():
    trace = Trace(
        prompt="safe flow",
        steps=[
            Step(kind="tool_call", name="read_data"),
            Step(kind="tool_call", name="compute_stats"),
        ],
    )

    assert no_forbidden_tool(trace, "delete_database")
    assert no_forbidden_tool(trace, ["drop_table", "delete_database", "shutdown"])

    danger_trace = Trace(
        prompt="danger flow",
        steps=[
            Step(kind="tool_call", name="read_data"),
            Step(kind="tool_call", name="drop_table"),
        ],
    )
    assert not no_forbidden_tool(danger_trace, ["drop_table", "delete_database"])


def test_no_loop():
    # Normal execution without loops
    clean_trace = Trace(
        prompt="search loop",
        steps=[
            Step(kind="tool_call", name="search", args={"page": 1}),
            Step(kind="tool_call", name="search", args={"page": 2}),
            Step(kind="tool_call", name="search", args={"page": 3}),
        ],
    )
    assert no_loop(clean_trace)

    # Repeated tool call with identical args
    looping_trace = Trace(
        prompt="stuck loop",
        steps=[
            Step(kind="tool_call", name="search", args={"q": "bug"}),
            Step(kind="tool_call", name="search", args={"q": "bug"}),
            Step(kind="tool_call", name="search", args={"q": "bug"}),
        ],
    )
    assert not no_loop(looping_trace, max_repeats=2)
    assert no_loop(looping_trace, max_repeats=3)


def test_tool_call_count():
    trace = Trace(
        prompt="counts",
        steps=[
            Step(kind="tool_call", name="fetch"),
            Step(kind="tool_call", name="fetch"),
            Step(kind="tool_call", name="save"),
        ],
    )

    assert tool_call_count(trace, "fetch", count=2)
    assert not tool_call_count(trace, "fetch", count=1)
    assert tool_call_count(trace, "fetch", min_count=1, max_count=3)
    assert not tool_call_count(trace, "fetch", max_count=1)
