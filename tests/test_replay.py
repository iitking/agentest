from agentest import Step, Trace, load_trace, save_trace, tool_called


def test_trace_save_and_load(tmp_path):
    trace_file = tmp_path / "sample_trace.json"

    original_trace = Trace(
        prompt="Refund order #99",
        steps=[
            Step(kind="llm", tokens=120, cost_usd=0.0015, latency_s=0.4),
            Step(kind="tool_call", name="lookup", args={"id": 99}, output={"status": "paid"}),
            Step(kind="final", output="Refunded"),
        ],
        final_output="Refunded",
    )

    save_trace(original_trace, trace_file)
    assert trace_file.exists()

    loaded_trace = load_trace(trace_file)
    assert loaded_trace.prompt == "Refund order #99"
    assert loaded_trace.final_output == "Refunded"
    assert loaded_trace.step_count == 3
    assert loaded_trace.total_tokens == 120
    assert loaded_trace.total_cost == 0.0015
    assert tool_called(loaded_trace, "lookup", args={"id": 99})
