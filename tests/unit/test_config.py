"""Tests for configuration loading."""

import pytest
from src.config.loader import Config, deep_merge


def test_deep_merge():
    """Test deep merge of dictionaries."""
    base = {"a": 1, "b": {"c": 2, "d": 3}}
    override = {"b": {"c": 4, "e": 5}, "f": 6}
    
    result = deep_merge(base, override)
    
    assert result["a"] == 1
    assert result["b"]["c"] == 4
    assert result["b"]["d"] == 3
    assert result["b"]["e"] == 5
    assert result["f"] == 6


def test_config_get():
    """Test config dot notation access."""
    data = {"neo4j": {"uri": "bolt://localhost:7687"}}
    config = Config(data)
    
    assert config.get("neo4j.uri") == "bolt://localhost:7687"
    assert config.get("missing.key", "default") == "default"
