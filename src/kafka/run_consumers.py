"""
Kafka Consumer Runner

CLI script to run Kafka consumers.

Usage:
    python -m src.kafka.run_consumers --consumer all
    python -m src.kafka.run_consumers --consumer hume-request
    python -m src.kafka.run_consumers --consumer hume-result
    python -m src.kafka.run_consumers --consumer state-change
    python -m src.kafka.run_consumers --consumer alert
"""

import argparse
import logging
import signal
import sys
from threading import Thread, Event
from typing import Optional

from src.config.loader import get_config, get_kafka_config, get_neo4j_config, get_hume_config, get_emotional_thresholds
from src.kafka.consumers import (
    HumeRequestConsumer,
    HumeResultConsumer,
    StateChangeConsumer,
    AlertConsumer,
)
from src.kafka.producers import HumeProducer, AlertProducer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Shutdown event for graceful termination
shutdown_event = Event()


def get_neo4j_client():
    """Create Neo4j client."""
    from src.loaders.neo4j_loader import Neo4jLoader
    config = get_neo4j_config()
    return Neo4jLoader(
        uri=config["uri"],
        user=config["user"],
        password=config["password"],
        database=config.get("database", "neo4j")
    )


def get_hume_client():
    """Create Hume client."""
    from src.integrations.hume_client import HumeClient
    config = get_hume_config()
    return HumeClient(api_key=config.get("api_key"))


def create_consumer(consumer_type: str, kafka_config: dict):
    """Create a consumer instance by type."""
    bootstrap_servers = kafka_config.get("bootstrap_servers", "localhost:9092")
    
    if consumer_type == "hume-request":
        hume_client = get_hume_client()
        result_producer = HumeProducer(bootstrap_servers=bootstrap_servers)
        return HumeRequestConsumer(
            hume_client=hume_client,
            result_producer=result_producer,
            bootstrap_servers=bootstrap_servers
        )
    
    elif consumer_type == "hume-result":
        neo4j_client = get_neo4j_client()
        alert_producer = AlertProducer(bootstrap_servers=bootstrap_servers)
        thresholds = get_emotional_thresholds()
        return HumeResultConsumer(
            neo4j_client=neo4j_client,
            alert_producer=alert_producer,
            thresholds=thresholds,
            bootstrap_servers=bootstrap_servers
        )
    
    elif consumer_type == "state-change":
        neo4j_client = get_neo4j_client()
        return StateChangeConsumer(
            neo4j_client=neo4j_client,
            bootstrap_servers=bootstrap_servers
        )
    
    elif consumer_type == "alert":
        neo4j_client = get_neo4j_client()
        return AlertConsumer(
            neo4j_client=neo4j_client,
            bootstrap_servers=bootstrap_servers
        )
    
    else:
        raise ValueError(f"Unknown consumer type: {consumer_type}")


def run_consumer_thread(consumer_type: str, kafka_config: dict):
    """Run a consumer in a thread."""
    try:
        consumer = create_consumer(consumer_type, kafka_config)
        logger.info(f"Starting consumer: {consumer_type}")
        
        while not shutdown_event.is_set():
            try:
                # Run consumer (will block)
                consumer.run()
            except Exception as e:
                if not shutdown_event.is_set():
                    logger.error(f"Consumer {consumer_type} error: {e}")
                    # Wait before retry
                    shutdown_event.wait(5)
                    
    except Exception as e:
        logger.error(f"Failed to create consumer {consumer_type}: {e}")


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info("Shutdown signal received")
    shutdown_event.set()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run Kafka consumers")
    parser.add_argument(
        "--consumer",
        choices=["all", "hume-request", "hume-result", "state-change", "alert"],
        default="all",
        help="Which consumer(s) to run"
    )
    parser.add_argument(
        "--config",
        default="config",
        help="Configuration directory"
    )
    
    args = parser.parse_args()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Load configuration
    kafka_config = get_kafka_config()
    
    # Determine which consumers to run
    if args.consumer == "all":
        consumer_types = ["hume-request", "hume-result", "state-change", "alert"]
    else:
        consumer_types = [args.consumer]
    
    # Start consumers in threads
    threads = []
    for consumer_type in consumer_types:
        thread = Thread(
            target=run_consumer_thread,
            args=(consumer_type, kafka_config),
            daemon=True,
            name=f"consumer-{consumer_type}"
        )
        thread.start()
        threads.append(thread)
        logger.info(f"Started thread for: {consumer_type}")
    
    logger.info(f"Running {len(threads)} consumer(s). Press Ctrl+C to stop.")
    
    # Wait for shutdown
    try:
        while not shutdown_event.is_set():
            shutdown_event.wait(1)
            
            # Check if any threads have died unexpectedly
            for thread in threads:
                if not thread.is_alive() and not shutdown_event.is_set():
                    logger.warning(f"Thread {thread.name} died unexpectedly")
                    
    except KeyboardInterrupt:
        pass
    
    logger.info("Shutting down consumers...")
    shutdown_event.set()
    
    # Wait for threads to finish
    for thread in threads:
        thread.join(timeout=10)
    
    logger.info("All consumers stopped")


if __name__ == "__main__":
    main()
