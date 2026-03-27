# Architecture Overview

## System Architecture

The Hume Contested Logistics Intelligence Platform is a multi-layered system designed for monitoring, analyzing, and responding to logistics challenges in contested environments.

## Layers

### 1. Presentation Layer (Qlik Sense)
- 8 interactive dashboards
- Embedded AI chat
- AI-generated narratives
- Progressive disclosure for different user roles

### 2. API Layer (FastAPI)
- RESTful endpoints
- WebSocket support for real-time chat
- Session management
- Rate limiting and guardrails

### 3. Intelligence Layer
- **Agent Framework**: Plan-ReAct hybrid approach
- **9 Core Tools**: Cypher queries, facility/asset/route status, inventory runway, alternate routes, alerts, reports, emotional summaries
- **RAG**: Neo4j Vector Index with entity summaries

### 4. Processing Layer
- **Batch Processing**: Delta Lake ETL pipeline
- **Stream Processing**: Kafka event streaming
- **Emotional Analysis**: Hume AI integration

### 5. Storage Layer
- **Graph Database**: Neo4j for network modeling
- **Data Lakehouse**: Delta Lake for analytics
- **Event Store**: Kafka topics for event sourcing

## Data Flow

```
Data Sources → Kafka → Processing → Neo4j/Delta Lake → API → Qlik
                  ↓
              Hume AI
                  ↓
              Alerts
```

## Key Design Decisions

1. **Graph-first modeling**: Neo4j for natural representation of logistics networks
2. **Event sourcing**: Kafka for audit trail and async processing
3. **Hybrid agent**: Plan-ReAct for complex multi-step queries
4. **Feature flags**: Gradual rollout of capabilities
5. **Provenance tracking**: Every node has source and confidence metadata
