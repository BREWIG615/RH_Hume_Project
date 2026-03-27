"""
Kafka Consumers

Domain-specific consumers for processing events.
"""

from datetime import datetime
from typing import Optional
import uuid
import logging

from src.kafka.base import BaseConsumer
from src.kafka.producers import HumeProducer, AlertProducer

logger = logging.getLogger(__name__)


class HumeRequestConsumer(BaseConsumer):
    """Consumer that processes Hume analysis requests."""
    
    def __init__(
        self,
        hume_client,
        result_producer: HumeProducer,
        **kwargs
    ):
        """
        Initialize Hume request consumer.
        
        Args:
            hume_client: Hume API client
            result_producer: Producer for publishing results
            **kwargs: Additional consumer arguments
        """
        super().__init__(
            topics=["hume.requests"],
            group_id="hume-processor",
            **kwargs
        )
        self.hume = hume_client
        self.result_producer = result_producer
    
    def process_message(self, message) -> bool:
        """Process a Hume analysis request."""
        event = message.value
        comm_id = event.get("communication_id")
        content = event.get("content")
        
        if not comm_id or not content:
            logger.warning(f"Invalid Hume request: missing id or content")
            return False
        
        logger.info(f"Processing Hume request for {comm_id}")
        
        try:
            # Call Hume API
            result = self.hume.analyze_text(content)
            
            # Extract scores
            scores = {
                "anxiety": result.get("anxiety", 0.0),
                "urgency": result.get("urgency", 0.0),
                "confusion": result.get("confusion", 0.0),
                "fear": result.get("fear", 0.0),
                "confidence": result.get("confidence", 0.0),
                "frustration": result.get("frustration", 0.0),
            }
            
            # Publish result
            self.result_producer.publish_result(
                communication_id=comm_id,
                scores=scores,
                metadata={"request_metadata": event.get("metadata", {})}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Hume processing failed for {comm_id}: {e}")
            return False


class HumeResultConsumer(BaseConsumer):
    """Consumer that writes Hume results to Neo4j."""
    
    def __init__(
        self,
        neo4j_client,
        alert_producer: AlertProducer,
        thresholds: dict,
        **kwargs
    ):
        """
        Initialize Hume result consumer.
        
        Args:
            neo4j_client: Neo4j client
            alert_producer: Producer for alerts
            thresholds: Emotional threshold configuration
            **kwargs: Additional consumer arguments
        """
        super().__init__(
            topics=["hume.results"],
            group_id="hume-result-writer",
            **kwargs
        )
        self.neo4j = neo4j_client
        self.alert_producer = alert_producer
        self.thresholds = thresholds
    
    def process_message(self, message) -> bool:
        """Write Hume results to Neo4j and check for alerts."""
        event = message.value
        comm_id = event.get("communication_id")
        scores = event.get("scores", {})
        
        if not comm_id:
            logger.warning("Invalid Hume result: missing communication_id")
            return False
        
        logger.info(f"Writing Hume results for {comm_id}")
        
        try:
            # Calculate severity
            severity_info = self._calculate_severity(scores)
            
            # Update Neo4j
            self.neo4j.execute_cypher("""
                MATCH (c:Communication {id: $comm_id})
                SET c.hume_status = 'processed',
                    c.hume_processed_at = datetime(),
                    c.hume_anxiety = $anxiety,
                    c.hume_urgency = $urgency,
                    c.hume_confusion = $confusion,
                    c.hume_fear = $fear,
                    c.hume_confidence = $confidence,
                    c.hume_frustration = $frustration,
                    c.hume_overall_severity = $overall_severity,
                    c.hume_severity_reason = $severity_reason
            """, {
                "comm_id": comm_id,
                **scores,
                **severity_info,
            })
            
            # Create alert if warranted
            if severity_info["overall_severity"] in ["alert", "escalate"]:
                self._create_alert(comm_id, scores, severity_info)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to write Hume results for {comm_id}: {e}")
            return False
    
    def _calculate_severity(self, scores: dict) -> dict:
        """Calculate overall severity from individual scores."""
        overall = "normal"
        reason = None
        
        # Check escalate thresholds
        escalate_thresholds = self.thresholds.get("escalate", {})
        for emotion, threshold in escalate_thresholds.items():
            if scores.get(emotion, 0) >= threshold:
                overall = "escalate"
                reason = f"{emotion} >= {threshold}"
                break
        
        # Check alert thresholds if not already escalating
        if overall == "normal":
            alert_thresholds = self.thresholds.get("alert", {})
            for emotion, threshold in alert_thresholds.items():
                if scores.get(emotion, 0) >= threshold:
                    overall = "alert"
                    reason = f"{emotion} >= {threshold}"
                    break
        
        # Check compound rules
        if overall != "escalate":
            for rule in self.thresholds.get("compound_rules", []):
                conditions_met = all(
                    scores.get(emotion, 0) >= threshold
                    for emotion, threshold in rule.get("conditions", {}).items()
                )
                if conditions_met:
                    overall = rule.get("action", "alert")
                    reason = rule.get("name", "compound_rule")
                    break
        
        return {
            "overall_severity": overall,
            "severity_reason": reason,
        }
    
    def _create_alert(self, comm_id: str, scores: dict, severity_info: dict):
        """Create alert for high-severity emotional signal."""
        self.alert_producer.publish_alert(
            alert_id=str(uuid.uuid4()),
            alert_type="emotional_signal",
            severity=severity_info["overall_severity"],
            entity_type="Communication",
            entity_id=comm_id,
            reason=severity_info.get("severity_reason", "Elevated emotional signal"),
            details={"scores": scores},
        )


class StateChangeConsumer(BaseConsumer):
    """Consumer that records state changes to Neo4j."""
    
    def __init__(self, neo4j_client, **kwargs):
        """
        Initialize state change consumer.
        
        Args:
            neo4j_client: Neo4j client
            **kwargs: Additional consumer arguments
        """
        super().__init__(
            topics=["state.changes"],
            group_id="state-change-recorder",
            **kwargs
        )
        self.neo4j = neo4j_client
    
    def process_message(self, message) -> bool:
        """Record state change in Neo4j."""
        event = message.value
        
        entity_type = event.get("entity_type")
        entity_id = event.get("entity_id")
        
        if not entity_type or not entity_id:
            logger.warning("Invalid state change: missing entity info")
            return False
        
        logger.info(
            f"Recording state change: {entity_type} {entity_id} "
            f"{event.get('field')}: {event.get('old_value')} → {event.get('new_value')}"
        )
        
        try:
            self.neo4j.execute_cypher("""
                MATCH (e {id: $entity_id})
                CREATE (sc:StateChange {
                    id: randomUUID(),
                    entity_type: $entity_type,
                    entity_id: $entity_id,
                    field: $field,
                    old_value: $old_value,
                    new_value: $new_value,
                    changed_by: $changed_by,
                    changed_at: datetime($changed_at)
                })
                CREATE (sc)-[:FOR_ENTITY]->(e)
            """, {
                "entity_id": entity_id,
                "entity_type": entity_type,
                "field": event.get("field"),
                "old_value": event.get("old_value"),
                "new_value": event.get("new_value"),
                "changed_by": event.get("changed_by", "system"),
                "changed_at": event.get("changed_at", datetime.now().isoformat()),
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to record state change: {e}")
            return False


class AlertConsumer(BaseConsumer):
    """Consumer that creates ReviewItems in Neo4j for alerts."""
    
    def __init__(self, neo4j_client, **kwargs):
        """
        Initialize alert consumer.
        
        Args:
            neo4j_client: Neo4j client
            **kwargs: Additional consumer arguments
        """
        super().__init__(
            topics=["alerts.created"],
            group_id="alert-processor",
            **kwargs
        )
        self.neo4j = neo4j_client
    
    def process_message(self, message) -> bool:
        """Create ReviewItem in Neo4j."""
        event = message.value
        
        alert_id = event.get("alert_id")
        entity_id = event.get("entity_id")
        
        if not alert_id or not entity_id:
            logger.warning("Invalid alert: missing id info")
            return False
        
        logger.info(
            f"Creating alert: {event.get('alert_type')} for "
            f"{event.get('entity_type')} {entity_id}"
        )
        
        try:
            self.neo4j.execute_cypher("""
                MATCH (e {id: $entity_id})
                CREATE (ri:ReviewItem {
                    id: $alert_id,
                    item_type: $alert_type,
                    created_at: datetime($created_at),
                    priority: $priority,
                    status: 'pending',
                    severity: $severity,
                    reason: $reason
                })
                CREATE (ri)-[:CONCERNS]->(e)
            """, {
                "alert_id": alert_id,
                "entity_id": entity_id,
                "alert_type": event.get("alert_type"),
                "created_at": event.get("created_at", datetime.now().isoformat()),
                "priority": event.get("priority", 0.5),
                "severity": event.get("severity", "alert"),
                "reason": event.get("reason", ""),
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
            return False
