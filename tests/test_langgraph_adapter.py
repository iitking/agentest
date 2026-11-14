from agentest.adapters import LangGraphAdapter
from agentest.assertions import tool_called


class FakeLangGraphAgent:
    """Simulates a compiled LangGraph runnable with .invoke()."""

    def invoke(self, input_payload: dict):
        class AIMessage:
            tool_calls = [{"name": "search_db", "args": {"query": "pricing"}}]
            usage_metadata = {"total_tokens": 150}

        class ToolMessage:
            type = "tool"
            name = "search_db"
            content = "Product price: $29"

        class FinalMessage:
            content = "The pricing is $29 per month."

        return {
            "messages": [
                AIMessage(),
                ToolMessage(),
                FinalMessage(),
            ]
        }


def test_langgraph_adapter_records_trace():
    adapter = LangGraphAdapter()
    agent = FakeLangGraphAgent()

    trace = adapter.run(agent, "What is the price?")
    assert trace.prompt == "What is the price?"
    assert trace.final_output == "The pricing is $29 per month."
    assert tool_called(trace, "search_db", args={"query": "pricing"})
    assert any(s.kind == "tool_result" and s.name == "search_db" for s in trace.steps)
    assert trace.total_tokens == 150
