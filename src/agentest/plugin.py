"""pytest plugin. Loaded automatically via the `pytest11` entry point."""
from __future__ import annotations

import pytest

from agentest.runner import run_agent


def pytest_configure(config):
    config.addinivalue_line("markers", "agent: mark a test as an agent behavior test")


@pytest.fixture
def agent_runner():
    """Fixture form of run_agent:  trace = agent_runner(my_agent, 'prompt')"""
    return run_agent
