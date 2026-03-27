# RH Hume Project

**Contested Logistics Intelligence Platform**

A multi-technology intelligence platform for monitoring and analyzing contested logistics environments in the Indo-Pacific region. Features graph-based data modeling, emotional signal extraction from communications, and agentic AI capabilities.

## 🎯 Core Value Propositions

1. **Ground truth from emotional signals** — Understand what your people are actually experiencing through Hume AI analysis of communications
2. **Impact and options immediately** — When disruptions hit, see affected assets, routes, and facilities instantly with recommended alternatives

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           QLIK SENSE                                │
│                    (Primary User Interface)                         │
│     Dashboards │ Embedded Chat │ Narratives │ Visualizations       │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          AGENT API                                  │
│              FastAPI │ ReAct Agent │ Tool Execution                │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        ▼                         ▼                         ▼
┌───────────────┐       ┌─────────────────┐       ┌─────────────────┐
│    NEO4J      │       │     KAFKA       │       │   DELTA LAKE    │
│  Graph Store  │       │  Event Stream   │       │   Data Lake     │
└───────────────┘       └─────────────────┘       └─────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        ▼                         ▼                         ▼
┌───────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   CLAUDE AI   │       │    HUME AI      │       │    OPENAI       │
│   Reasoning   │       │   Emotional     │       │   Embeddings    │
└───────────────┘       └─────────────────┘       └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose (or Podman)
- Python 3.11+
- API Keys:
  - [Anthropic Claude](https://console.anthropic.com)
  - [Hume AI](https://platform.hume.ai)
  - [OpenAI](https://platform.openai.com) (for embeddings, optional)

### Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/rh_hume_project.git
cd rh_hume_project

# Initial setup
make setup

# Configure environment
cp docker/.env.example docker/.env
# Edit docker/.env with your API keys

# Start all services
make up

# Initialize Kafka topics and Neo4j indexes
make init

# Generate synthetic demo data
make generate-data

# Run full processing pipeline
make run-pipeline

# Verify everything is working
make check-health
```

### Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Qlik Sense** | (Local Desktop) | Primary user interface |
| **Agent API** | http://localhost:8000 | REST API for chat |
| **API Docs** | http://localhost:8000/docs | OpenAPI documentation |
| **Neo4j Browser** | http://localhost:7474 | Graph database UI |
| **Kafka UI** | http://localhost:8080 | Message queue monitoring |

## 📁 Project Structure

```
rh_hume_project/
├── src/                          # Application source code
│   ├── agent/                    # Agentic framework
│   │   ├── react_agent.py        # ReAct loop implementation
│   │   ├── guardrails.py         # Safety guardrails
│   │   └── tools/                # 9 core agent tools
│   ├── api/                      # FastAPI REST API
│   │   ├── main.py               # Application entry
│   │   └── routes/               # API endpoints
│   ├── kafka/                    # Event streaming
│   │   ├── producers.py          # Kafka producers
│   │   ├── consumers.py          # Kafka consumers
│   │   └── run_consumers.py      # Consumer runner
│   ├── processing/               # Data processing
│   │   ├── delta_engine.py       # Delta Lake abstraction
│   │   └── transforms/           # Data transformations
│   ├── loaders/                  # Data loading
│   │   ├── neo4j_loader.py       # Neo4j batch loader
│   │   └── entity_loaders.py     # Entity-specific loaders
│   ├── integrations/             # External services
│   │   ├── hume_client.py        # Hume AI client
│   │   ├── claude_client.py      # Claude API client
│   │   └── embedding_client.py   # Embedding services
│   ├── schema/                   # Schema management
│   ├── models/                   # Domain models
│   ├── config/                   # Configuration
│   └── utils/                    # Utilities
│
├── jobs/                         # Batch processing jobs
│   ├── runner.py                 # CLI job runner
│   ├── synthetic_data.py         # Demo data generation
│   ├── etl_pipeline.py           # ETL processing
│   └── ...
│
├── qlik/                         # Qlik Sense assets
│   ├── app/                      # Qlik app exports
│   ├── scripts/                  # Load scripts
│   └── extensions/               # Custom extensions
│
├── docker/                       # Docker configuration
│   ├── docker-compose.yml        # Full stack
│   └── Dockerfile.*              # Service images
│
├── config/                       # Configuration files
│   ├── default.yaml              # Base config
│   ├── development.yaml          # Dev overrides
│   └── logging.yaml              # Logging config
│
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── golden/                   # Agent quality tests
│
├── docs/                         # Documentation
│   ├── architecture/             # Architecture docs
│   ├── guides/                   # How-to guides
│   └── playbooks/                # Operational playbooks
│
├── scripts/                      # Utility scripts
├── notebooks/                    # Jupyter notebooks
└── data/                         # Data directory (gitignored)
```

## 🔧 Development

### Common Commands

```bash
# Start/stop services
make up                    # Start all services
make down                  # Stop all services
make restart               # Restart all services

# View logs
make logs                  # All logs
make logs service=api      # Specific service

# Run jobs
make generate-data         # Generate synthetic data
make run-pipeline          # Full ETL pipeline
make run-job JOB=etl       # Specific job

# Development
make shell-api             # Shell into API container
make test                  # Run tests
make lint                  # Run linters

# Demo
make reset-demo            # Reset to demo state
make check-health          # Verify services
```

### Running Tests

```bash
# All tests
make test

# Unit tests only
make test-unit

# Golden tests (agent quality)
make test-golden

# With coverage
make coverage
```

### Code Quality

```bash
# Lint code
make lint

# Format code
make format

# Type checking
make typecheck
```

## 🗺️ Demo Scenario: Taiwan Strait Disruption

The demo showcases the platform's response to a maritime route denial:

1. **Normal Operations** — Network Overview shows all routes open
2. **Disruption Occurs** — Taiwan Strait becomes denied
3. **Immediate Impact** — Alerts fire, emotional indicators spike
4. **Ask the Agent** — "What's the impact of the Taiwan Strait closure?"
5. **Find Options** — "Find alternate routes to Kadena"
6. **Decision Ready** — Executive dashboard shows summary and recommendations

## 📊 Qlik Dashboards

| Sheet | Description | Primary User |
|-------|-------------|--------------|
| Network Overview | Map-based view of all facilities and routes | Executive |
| Daily Supply Posture | Asset readiness, shortages, emotional summary | Executive |
| Facility Status | Deep dive on single facility | Analyst |
| Route Assessment | Route details, risks, alternatives | Analyst |
| Inventory Runway | Parts/supplies approaching reorder | Both |
| Alert Summary | Open alerts by priority, trends | Both |
| Review Queue | Pending items for human review | Analyst |
| Emotional Health | Hume signal trends by facility/region | Both |

## 🔌 API Endpoints

### Chat

```bash
# Send chat message
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the status of Kadena?"}'
```

### Health

```bash
# Basic health check
curl http://localhost:8000/health

# Readiness check (includes dependencies)
curl http://localhost:8000/health/ready
```

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Graph Database | Neo4j 5.x | Network modeling, traversals |
| Event Streaming | Apache Kafka | Async processing, event bus |
| Data Lakehouse | Delta Lake | Data storage, time travel |
| LLM | Claude (Anthropic) | Agent reasoning |
| Emotional AI | Hume AI | Communication analysis |
| Embeddings | OpenAI / BGE | Vector search |
| Visualization | Qlik Sense | Dashboards, reporting |
| API | FastAPI | REST endpoints |
| Containers | Docker | Deployment |

## 📚 Documentation

- [Architecture Overview](docs/architecture/overview.md)
- [Getting Started Guide](docs/guides/getting_started.md)
- [Development Guide](docs/guides/development.md)
- [Deployment Guide](docs/guides/deployment.md)
- [API Reference](docs/api/openapi.yaml)

### Playbooks

- [Velocity Scaling](docs/playbooks/velocity_scaling.md) — Batch to streaming
- [IL5 Compliance](docs/playbooks/il5_compliance.md) — Security authorization path
- [Graph ETL](docs/playbooks/graph_etl.md) — Data transformation patterns

## 🔐 Security & Compliance

- Demo: Unclassified synthetic data
- Production: Designed for IL5 compliance path
- See [IL5 Compliance Playbook](docs/playbooks/il5_compliance.md)

## 📈 Roadmap

- [x] Requirements gathering (68 questions)
- [x] Architecture design
- [x] Project structure
- [ ] Synthetic data generation
- [ ] Neo4j schema implementation
- [ ] Kafka event streaming
- [ ] Hume AI integration
- [ ] Agent framework
- [ ] Qlik dashboards
- [ ] Demo scenario

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## 📄 License

Proprietary — All rights reserved.

## 👤 Author

Craig — The Hume Project

---

*Built for contested logistics intelligence in the Indo-Pacific region.*
