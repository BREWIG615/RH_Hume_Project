# Getting Started Guide

## Prerequisites

- Docker or Podman
- Python 3.11+
- API Keys:
  - Anthropic Claude
  - Hume AI
  - OpenAI (optional, for embeddings)

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/YOUR_USERNAME/rh_hume_project.git
cd rh_hume_project
make setup
```

### 2. Configure Environment

```bash
cp docker/.env.example docker/.env
# Edit docker/.env with your API keys
```

### 3. Start Services

```bash
make up
make init
```

### 4. Generate Demo Data

```bash
make generate-data
make run-pipeline
```

### 5. Verify

```bash
make check-health
```

### 6. Access

- Neo4j Browser: http://localhost:7474
- Kafka UI: http://localhost:8080
- API Docs: http://localhost:8000/docs

## Next Steps

1. Open Qlik Sense Desktop
2. Connect to data in `data/presentation/`
3. Try the chat endpoint: `curl -X POST http://localhost:8000/api/chat -d '{"message":"What is the status of Kadena?"}'`
