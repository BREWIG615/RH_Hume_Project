"""
Kafka Topic Initialization

Creates required Kafka topics with appropriate configuration.
"""

import os
import logging
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Topic definitions
TOPICS = [
    {
        "name": "raw.ingest",
        "partitions": 3,
        "replication_factor": 1,
        "config": {
            "retention.ms": "604800000",  # 7 days
            "cleanup.policy": "delete",
        }
    },
    {
        "name": "hume.requests",
        "partitions": 3,
        "replication_factor": 1,
        "config": {
            "retention.ms": "86400000",  # 1 day
            "cleanup.policy": "delete",
        }
    },
    {
        "name": "hume.results",
        "partitions": 3,
        "replication_factor": 1,
        "config": {
            "retention.ms": "604800000",  # 7 days
            "cleanup.policy": "delete",
        }
    },
    {
        "name": "state.changes",
        "partitions": 3,
        "replication_factor": 1,
        "config": {
            "retention.ms": "2592000000",  # 30 days
            "cleanup.policy": "delete",
        }
    },
    {
        "name": "alerts.created",
        "partitions": 1,
        "replication_factor": 1,
        "config": {
            "retention.ms": "604800000",  # 7 days
            "cleanup.policy": "delete",
        }
    },
    {
        "name": "graph.updates",
        "partitions": 3,
        "replication_factor": 1,
        "config": {
            "retention.ms": "86400000",  # 1 day
            "cleanup.policy": "delete",
        }
    },
    {
        "name": "narrative.requests",
        "partitions": 1,
        "replication_factor": 1,
        "config": {
            "retention.ms": "86400000",  # 1 day
            "cleanup.policy": "delete",
        }
    },
]


def init_topics(bootstrap_servers: str = None) -> bool:
    """
    Create Kafka topics if they don't exist.
    
    Args:
        bootstrap_servers: Kafka broker addresses (default from environment)
        
    Returns:
        True if successful
    """
    if bootstrap_servers is None:
        bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    
    logger.info(f"Connecting to Kafka: {bootstrap_servers}")
    
    try:
        admin = KafkaAdminClient(
            bootstrap_servers=bootstrap_servers,
            client_id="topic-initializer"
        )
    except Exception as e:
        logger.error(f"Failed to connect to Kafka: {e}")
        return False
    
    # Create topics
    topics_to_create = []
    for topic_def in TOPICS:
        topic = NewTopic(
            name=topic_def["name"],
            num_partitions=topic_def["partitions"],
            replication_factor=topic_def["replication_factor"],
            topic_configs=topic_def.get("config", {})
        )
        topics_to_create.append(topic)
    
    # Try to create each topic
    created = 0
    for topic in topics_to_create:
        try:
            admin.create_topics([topic], validate_only=False)
            logger.info(f"Created topic: {topic.name}")
            created += 1
        except TopicAlreadyExistsError:
            logger.info(f"Topic already exists: {topic.name}")
        except Exception as e:
            logger.error(f"Failed to create topic {topic.name}: {e}")
    
    admin.close()
    logger.info(f"Topic initialization complete. Created {created} new topics.")
    return True


def list_topics(bootstrap_servers: str = None) -> list[str]:
    """
    List existing Kafka topics.
    
    Args:
        bootstrap_servers: Kafka broker addresses
        
    Returns:
        List of topic names
    """
    if bootstrap_servers is None:
        bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    
    try:
        admin = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
        topics = admin.list_topics()
        admin.close()
        return list(topics)
    except Exception as e:
        logger.error(f"Failed to list topics: {e}")
        return []


def delete_topics(topic_names: list[str], bootstrap_servers: str = None) -> bool:
    """
    Delete Kafka topics.
    
    Args:
        topic_names: List of topic names to delete
        bootstrap_servers: Kafka broker addresses
        
    Returns:
        True if successful
    """
    if bootstrap_servers is None:
        bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    
    try:
        admin = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
        admin.delete_topics(topic_names)
        admin.close()
        logger.info(f"Deleted topics: {topic_names}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete topics: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        topics = list_topics()
        print("Existing topics:")
        for topic in sorted(topics):
            print(f"  - {topic}")
    else:
        success = init_topics()
        sys.exit(0 if success else 1)
