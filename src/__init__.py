"""
RH Hume Project - Contested Logistics Intelligence Platform

The Hume Project is a multi-technology intelligence platform for monitoring
and analyzing contested logistics environments, featuring:

- Graph-based data modeling (Neo4j)
- Emotional signal extraction (Hume AI)
- Agentic AI capabilities (Claude)
- Event streaming (Kafka)
- Business intelligence (Qlik Sense)

Modules:
    agent: Agentic framework with tools and ReAct reasoning
    api: FastAPI REST endpoints
    kafka: Event streaming producers and consumers
    processing: Data processing and Delta Lake operations
    loaders: Neo4j data loading utilities
    integrations: External service clients (Hume, Claude, OpenAI)
    schema: Schema validation and drift detection
    models: Domain models and enumerations
    config: Configuration management
    utils: Shared utilities
"""

__version__ = "0.1.0"
__author__ = "Craig"
__project__ = "The Hume Project"
