from agentest import mock_tool


def test_mock_tool_return_value():
    tool = mock_tool("calculator", return_value=42)

    res = tool(x=10, y=32)
    assert res == 42
    assert tool.called
    assert tool.call_count == 1
    assert tool.calls[0] == {"x": 10, "y": 32}

    tool.reset()
    assert not tool.called
    assert tool.call_count == 0


def test_mock_tool_side_effect():
    tool = mock_tool("echo", side_effect=lambda text: f"echo: {text}")

    res = tool(text="hello")
    assert res == "echo: hello"
    assert tool.call_count == 1
