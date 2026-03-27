# Velocity Scaling Playbook

## Overview

Guide for scaling from demo (batch) to production (streaming) velocity.

## Current State (Demo)

- Batch processing with Delta Lake
- Manual CLI job runner
- Single load + optional refresh

## Target State (Production)

- Streaming with Kafka consumers
- Databricks Workflows orchestration
- Near real-time updates

## Migration Steps

### Phase 1: Kafka Consumer Activation

1. Deploy consumer services
2. Enable `kafka_enabled` feature flag
3. Monitor consumer lag

### Phase 2: Processing Optimization

1. Implement micro-batching (15-minute windows)
2. Add backpressure handling
3. Configure consumer scaling

### Phase 3: Full Streaming

1. Switch to continuous consumers
2. Implement exactly-once semantics
3. Add stream processing for aggregations

## Monitoring

- Consumer lag metrics
- Processing throughput
- Error rates by consumer
