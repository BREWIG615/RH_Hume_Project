"""
Kafka Base Classes

Base producer and consumer implementations with JSON serialization.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Generator, Optional
import json
import logging

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)


class BaseProducer:
    """
    Base Kafka producer with JSON serialization.
    
    Example:
        producer = BaseProducer(bootstrap_servers="localhost:9092")
        producer.publish("my.topic", {"key": "value"}, key="my-key")
        producer.close()
    """
    
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        **kwargs
    ):
        """
        Initialize Kafka producer.
        
        Args:
            bootstrap_servers: Kafka broker addresses
            **kwargs: Additional KafkaProducer arguments
        """
        default_config = {
            "bootstrap_servers": bootstrap_servers,
            "value_serializer": lambda v: json.dumps(v, default=str).encode("utf-8"),
            "key_serializer": lambda k: k.encode("utf-8") if k else None,
            "acks": "all",
            "retries": 3,
            "retry_backoff_ms": 100,
        }
        default_config.update(kwargs)
        
        self.producer = KafkaProducer(**default_config)
        self._bootstrap_servers = bootstrap_servers
        logger.info(f"Kafka producer initialized: {bootstrap_servers}")
    
    def publish(
        self,
        topic: str,
        value: dict,
        key: Optional[str] = None,
        headers: Optional[list] = None
    ) -> bool:
        """
        Publish message to topic.
        
        Args:
            topic: Target topic
            value: Message value (will be JSON serialized)
            key: Optional message key
            headers: Optional message headers
            
        Returns:
            True if successful
        """
        # Add metadata
        value["_published_at"] = datetime.now().isoformat()
        value["_producer"] = self.__class__.__name__
        
        try:
            future = self.producer.send(
                topic,
                value=value,
                key=key,
                headers=headers
            )
            record_metadata = future.get(timeout=10)
            logger.debug(
                f"Published to {topic}: partition={record_metadata.partition}, "
                f"offset={record_metadata.offset}"
            )
            return True
        except KafkaError as e:
            logger.error(f"Failed to publish to {topic}: {e}")
            return False
    
    def flush(self, timeout: float = 10.0):
        """Flush pending messages."""
        self.producer.flush(timeout=timeout)
    
    def close(self):
        """Close the producer."""
        self.producer.close()
        logger.info("Kafka producer closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class BaseConsumer(ABC):
    """
    Base Kafka consumer with JSON deserialization.
    
    Subclasses must implement process_message().
    
    Example:
        class MyConsumer(BaseConsumer):
            def process_message(self, message) -> bool:
                print(message.value)
                return True
        
        consumer = MyConsumer(topics=["my.topic"], group_id="my-group")
        consumer.run()
    """
    
    def __init__(
        self,
        topics: list[str],
        group_id: str,
        bootstrap_servers: str = "localhost:9092",
        **kwargs
    ):
        """
        Initialize Kafka consumer.
        
        Args:
            topics: List of topics to subscribe to
            group_id: Consumer group ID
            bootstrap_servers: Kafka broker addresses
            **kwargs: Additional KafkaConsumer arguments
        """
        default_config = {
            "bootstrap_servers": bootstrap_servers,
            "group_id": group_id,
            "value_deserializer": lambda v: json.loads(v.decode("utf-8")),
            "auto_offset_reset": "earliest",
            "enable_auto_commit": True,
            "auto_commit_interval_ms": 5000,
        }
        default_config.update(kwargs)
        
        self.consumer = KafkaConsumer(*topics, **default_config)
        self.running = True
        self._topics = topics
        self._group_id = group_id
        
        logger.info(f"Kafka consumer initialized: topics={topics}, group={group_id}")
    
    @abstractmethod
    def process_message(self, message) -> bool:
        """
        Process a single message.
        
        Args:
            message: Kafka message with .value, .key, .topic, etc.
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    def run(self):
        """Run the consumer loop."""
        logger.info(f"Starting consumer for topics: {self._topics}")
        
        try:
            while self.running:
                messages = self.consumer.poll(timeout_ms=1000)
                
                for topic_partition, records in messages.items():
                    for record in records:
                        try:
                            success = self.process_message(record)
                            if not success:
                                logger.warning(
                                    f"Failed to process message: "
                                    f"topic={record.topic}, offset={record.offset}"
                                )
                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                            self._handle_error(record, e)
        except KeyboardInterrupt:
            logger.info("Consumer interrupted")
        finally:
            self.consumer.close()
            logger.info("Consumer closed")
    
    def _handle_error(self, message, error: Exception):
        """
        Handle processing error.
        
        Override in subclass to implement dead letter queue, etc.
        """
        logger.error(
            f"Message processing failed: topic={message.topic}, "
            f"offset={message.offset}, error={error}"
        )
    
    def stop(self):
        """Signal the consumer to stop."""
        self.running = False
        logger.info("Consumer stop requested")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
