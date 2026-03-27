"""Integration tests for Hume client."""

import pytest
from src.integrations.hume_client import HumeClient


@pytest.mark.integration
def test_hume_mock_analysis():
    """Test Hume mock analysis (no API key)."""
    client = HumeClient(api_key=None)
    
    result = client.analyze_text("I am very worried about the situation.")
    
    assert "anxiety" in result
    assert 0.0 <= result["anxiety"] <= 1.0
    assert result["anxiety"] > 0.3  # Should detect "worried"
