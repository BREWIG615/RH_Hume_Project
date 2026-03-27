"""
Kafka Producers

Domain-specific producers for publishing events.
"""

from datetime import datetime
from typing import Optional
import logging

from src.kafka.base import BaseProducer

logger = logging.getLogger(__name__)


class IngestProducer(BaseProducer):
    """Producer for raw data ingestion events."""
    
    def publish_entity(
        self,
        entity_type: str,
        entity_id: str,
        data: dict,
        source: Optional[str] = None
    ) -> bool:
        """
        Publish an ingested entity.
        
        Args:
            entity_type: Type of entity (e.g., "Asset", "Facility")
            entity_id: Entity identifier
            data: Entity data
            source: Data source identifier
            
        Returns:
            True if successful
        """
        event = {
            "event_type": "entity_ingested",
            "entity_type": entity_type,
            "entity_id": entity_id,
            "data": data,
            "source": source or data.get("_source_system", "unknown"),
            "timestamp": datetime.now().isoformat(),
        }
        return self.publish("raw.ingest", event, key=f"{entity_type}:{entity_id}")
    
    def publish_batch(
        self,
        entity_type: str,
        entities: list[dict],
        source: Optional[str] = None
    ) -> int:
        """
        Publish a batch of entities.
        
        Args:
            entity_type: Type of entities
            entities: List of entity data dicts (must have 'id' field)
            source: Data source identifier
            
        Returns:
            Number of successfully published entities
        """
        success_count = 0
        for entity in entities:
            entity_id = entity.get("id")
            if entity_id and self.publish_entity(entity_type, entity_id, entity, source):
                success_count += 1
        
        self.flush()
        logger.info(f"Published {success_count}/{len(entities)} {entity_type} entities")
        return success_count


class HumeProducer(BaseProducer):
    """Producer for Hume processing requests and results."""
    
    def request_analysis(
        self,
        communication_id: str,
        content: str,
        metadata: Optional[dict] = None
    ) -> bool:
        """
        Queue a communication for Hume analysis.
        
        Args:
            communication_id: Communication identifier
            content: Text content to analyze
            metadata: Additional metadata
            
        Returns:
            True if successful
        """
        event = {
            "event_type": "hume_request",
            "communication_id": communication_id,
            "content": content,
            "metadata": metadata or {},
            "requested_at": datetime.now().isoformat(),
        }
        return self.publish("hume.requests", event, key=communication_id)
    
    def publish_result(
        self,
        communication_id: str,
        scores: dict,
        metadata: Optional[dict] = None
    ) -> bool:
        """
        Publish Hume analysis results.
        
        Args:
            communication_id: Communication identifier
            scores: Emotional scores dict
            metadata: Additional metadata
            
        Returns:
            True if successful
        """
        event = {
            "event_type": "hume_result",
            "communication_id": communication_id,
            "scores": scores,
            "metadata": metadata or {},
            "processed_at": datetime.now().isoformat(),
        }
        return self.publish("hume.results", event, key=communication_id)


class StateChangeProducer(BaseProducer):
    """Producer for entity state change events."""
    
    def publish_change(
        self,
        entity_type: str,
        entity_id: str,
        field: str,
        old_value: str,
        new_value: str,
        changed_by: str = "system"
    ) -> bool:
        """
        Publish a state change event.
        
        Args:
            entity_type: Type of entity
            entity_id: Entity identifier
            field: Changed field name
            old_value: Previous value
            new_value: New value
            changed_by: Actor that made the change
            
        Returns:
            True if successful
        """
        event = {
            "event_type": "state_change",
            "entity_type": entity_type,
            "entity_id": entity_id,
            "field": field,
            "old_value": str(old_value) if old_value is not None else None,
            "new_value": str(new_value) if new_value is not None else None,
            "changed_by": changed_by,
            "changed_at": datetime.now().isoformat(),
        }
        return self.publish("state.changes", event, key=f"{entity_type}:{entity_id}")


class AlertProducer(BaseProducer):
    """Producer for alert creation events."""
    
    def publish_alert(
        self,
        alert_id: str,
        alert_type: str,
        severity: str,
        entity_type: str,
        entity_id: str,
        reason: str,
        details: Optional[dict] = None,
        priority: Optional[float] = None
    ) -> bool:
        """
        Publish an alert creation event.
        
        Args:
            alert_id: Unique alert identifier
            alert_type: Type of alert (e.g., "emotional_signal", "inventory")
            severity: Severity level (flag, alert, escalate)
            entity_type: Type of related entity
            entity_id: Related entity identifier
            reason: Human-readable reason
            details: Additional details
            priority: Priority score (0.0-1.0)
            
        Returns:
            True if successful
        """
        # Calculate priority if not provided
        if priority is None:
            priority_map = {"escalate": 1.0, "alert": 0.7, "flag": 0.4}
            priority = priority_map.get(severity, 0.5)
        
        event = {
            "event_type": "alert_created",
            "alert_id": alert_id,
            "alert_type": alert_type,
            "severity": severity,
            "priority": priority,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "reason": reason,
            "details": details or {},
            "created_at": datetime.now().isoformat(),
        }
        return self.publish("alerts.created", event, key=alert_id)
