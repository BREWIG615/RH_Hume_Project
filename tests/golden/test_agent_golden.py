"""Golden tests for agent quality."""

import pytest
import yaml
from pathlib import Path


@pytest.fixture
def golden_cases():
    """Load golden test cases."""
    cases_file = Path(__file__).parent / "test_cases.yaml"
    with open(cases_file) as f:
        data = yaml.safe_load(f)
    return data["test_cases"]


@pytest.mark.golden
def test_golden_cases_loaded(golden_cases):
    """Verify golden test cases load correctly."""
    assert len(golden_cases) >= 8
    assert all("query" in case for case in golden_cases)
    assert all("expected_tools" in case for case in golden_cases)


@pytest.mark.golden
@pytest.mark.skip(reason="Agent not yet implemented")
def test_facility_status_simple(golden_cases):
    """Test simple facility status query."""
    case = next(c for c in golden_cases if c["id"] == "facility_status_simple")
    # TODO: Implement when agent is ready
    # result = agent.run(case["query"])
    # assert all(tool in result.tools_used for tool in case["expected_tools"])
