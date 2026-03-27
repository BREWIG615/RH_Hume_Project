"""
Kafka Module

Event streaming infrastructure for asynchronous processing.

Topics:
    raw.ingest: Incoming data events
    hume.requests: Communications queued for Hume processing
    hume.results: Hume analysis results
    state.changes: Entity state change events
    alerts.created: New alerts/review items
"""

from src.kafka.base import BaseProducer, BaseConsumer
from src.kafka.producers import (
    IngestProducer,
    HumeProducer,
    StateChangeProducer,
    AlertProducer,
)

__all__ = [
    "BaseProducer",
    "BaseConsumer",
    "IngestProducer",
    "HumeProducer",
    "StateChangeProducer",
    "AlertProducer",
]
