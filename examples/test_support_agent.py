from agentest import max_cost, max_steps, run_agent, tool_called
from support_agent import TOOLS, support_agent


def test_refund_flow():
    trace = run_agent(support_agent, "I want a refund for order #123", tools=TOOLS)

    assert tool_called(trace, "lookup_order", args={"order_id": "123"})
    assert tool_called(trace, "issue_refund")
    assert not tool_called(trace, "delete_account")
    assert max_steps(trace, 8)
    assert max_cost(trace, usd=0.05)


def test_mock_tool_is_used():
    mock = {"lookup_order": lambda order_id: {"order_id": order_id, "amount": 10}}
    trace = run_agent(support_agent, "refund please", tools=TOOLS, mock_tools=mock)

    refund_call = [s for s in trace.tool_calls if s.name == "issue_refund"][0]
    assert refund_call.args["amount"] == 10
