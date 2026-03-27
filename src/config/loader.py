"""
Configuration Loader

Hierarchical configuration with environment variable substitution.

Load order (later overrides earlier):
1. default.yaml
2. {environment}.yaml
3. local.yaml (gitignored)
4. Environment variables
"""

from pathlib import Path
from typing import Any, Optional
from functools import lru_cache
import os
import yaml
import logging

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Configuration loading error."""
    pass


class Config:
    """
    Hierarchical configuration with environment variable substitution.
    
    Example:
        config = get_config()
        neo4j_uri = config.get("neo4j.uri")
        batch_size = config.get("processing.batch_size", 1000)
    """
    
    def __init__(self, data: dict):
        self._data = data
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get config value using dot notation.
        
        Args:
            key: Dot-separated key path (e.g., 'neo4j.uri')
            default: Default value if key not found
            
        Returns:
            Configuration value with environment variables substituted
        """
        keys = key.split('.')
        value = self._data
        
        try:
            for k in keys:
                value = value[k]
            return self._substitute_env_vars(value)
        except (KeyError, TypeError):
            return default
    
    def __getitem__(self, key: str) -> Any:
        """Get config value, raising KeyError if not found."""
        value = self.get(key)
        if value is None:
            raise KeyError(f"Configuration key not found: {key}")
        return value
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists in config."""
        return self.get(key) is not None
    
    def _substitute_env_vars(self, value: Any) -> Any:
        """Substitute ${VAR} patterns with environment variables."""
        if isinstance(value, str):
            # Handle ${VAR} pattern
            if value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                env_value = os.environ.get(env_var)
                if env_value is None:
                    logger.warning(f"Environment variable {env_var} not set")
                return env_value
            return value
        elif isinstance(value, dict):
            return {k: self._substitute_env_vars(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._substitute_env_vars(item) for item in value]
        return value
    
    def as_dict(self) -> dict:
        """Return full config as dictionary with env vars substituted."""
        return self._substitute_env_vars(self._data)
    
    def section(self, key: str) -> 'Config':
        """
        Get a config section as a new Config object.
        
        Args:
            key: Section key
            
        Returns:
            Config object for the section
        """
        section_data = self.get(key, {})
        if isinstance(section_data, dict):
            return Config(section_data)
        raise ConfigurationError(f"Section {key} is not a dictionary")


def deep_merge(base: dict, override: dict) -> dict:
    """
    Deep merge two dictionaries, with override taking precedence.
    
    Args:
        base: Base dictionary
        override: Override dictionary
        
    Returns:
        Merged dictionary
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def load_yaml(path: Path) -> dict:
    """Load a YAML file, returning empty dict if not found."""
    if not path.exists():
        return {}
    
    with open(path) as f:
        return yaml.safe_load(f) or {}


@lru_cache(maxsize=1)
def load_config(
    environment: Optional[str] = None,
    config_dir: str = "config"
) -> Config:
    """
    Load configuration with hierarchical overrides.
    
    Args:
        environment: Environment name (default from APP_ENVIRONMENT env var)
        config_dir: Path to config directory
        
    Returns:
        Config object
        
    Load order:
    1. default.yaml
    2. {environment}.yaml
    3. local.yaml (gitignored, for developer overrides)
    """
    config_path = Path(config_dir)
    
    # Determine environment
    env = environment or os.environ.get("APP_ENVIRONMENT", "development")
    logger.info(f"Loading configuration for environment: {env}")
    
    # Load base config
    config = load_yaml(config_path / "default.yaml")
    if not config:
        raise ConfigurationError(f"Could not load default.yaml from {config_path}")
    
    # Load environment-specific config
    env_config = load_yaml(config_path / f"{env}.yaml")
    if env_config:
        config = deep_merge(config, env_config)
        logger.debug(f"Merged {env}.yaml")
    
    # Load local overrides (gitignored)
    local_config = load_yaml(config_path / "local.yaml")
    if local_config:
        config = deep_merge(config, local_config)
        logger.debug("Merged local.yaml")
    
    return Config(config)


def get_config() -> Config:
    """Get the loaded configuration (cached singleton)."""
    return load_config()


def reload_config() -> Config:
    """Force reload of configuration (clears cache)."""
    load_config.cache_clear()
    return load_config()


# =============================================================================
# Convenience Functions
# =============================================================================

def get_neo4j_config() -> dict:
    """Get Neo4j configuration with credentials from environment."""
    config = get_config()
    return {
        "uri": config.get("neo4j.uri", "bolt://localhost:7687"),
        "user": os.environ.get("NEO4J_USER", "neo4j"),
        "password": os.environ.get("NEO4J_PASSWORD", "password"),
        "database": config.get("neo4j.database", "neo4j"),
    }


def get_kafka_config() -> dict:
    """Get Kafka configuration."""
    config = get_config()
    kafka_config = config.get("kafka", {})
    
    # Override bootstrap servers from environment if set
    env_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS")
    if env_servers:
        kafka_config["bootstrap_servers"] = env_servers
    
    return kafka_config


def get_agent_config() -> dict:
    """Get agent configuration with API keys from environment."""
    config = get_config()
    agent_config = config.get("agent", {})
    
    # Add API keys from environment
    agent_config["api_keys"] = {
        "anthropic": os.environ.get("CLAUDE_API_KEY"),
        "openai": os.environ.get("OPENAI_API_KEY"),
        "hume": os.environ.get("HUME_API_KEY"),
    }
    
    return agent_config


def get_hume_config() -> dict:
    """Get Hume configuration with API key from environment."""
    config = get_config()
    hume_config = config.get("hume", {})
    hume_config["api_key"] = os.environ.get("HUME_API_KEY")
    return hume_config


def get_feature_flags() -> dict:
    """Get feature flags."""
    config = get_config()
    return config.get("feature_flags", {})


def is_feature_enabled(feature: str) -> bool:
    """Check if a feature flag is enabled."""
    flags = get_feature_flags()
    return flags.get(feature, False)


def get_data_paths() -> dict:
    """Get data directory paths."""
    config = get_config()
    return config.get("data_paths", {})


def get_emotional_thresholds() -> dict:
    """Get emotional signal thresholds."""
    config = get_config()
    return config.get("emotional_thresholds", {})
