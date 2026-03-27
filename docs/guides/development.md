# Development Guide

## Local Development

### Without Docker

```bash
# Install dependencies
pip install -e ".[dev]"

# Start external services only
make up-infra

# Run API locally
make dev-api
```

### Code Quality

```bash
# Format code
make format

# Lint
make lint

# Type check
make typecheck

# Run all checks
make pre-commit
```

### Testing

```bash
# All tests
make test

# Unit tests only
make test-unit

# Golden tests (agent quality)
make test-golden
```

## Architecture Decisions

See `docs/architecture/` for detailed architecture documentation.

## Adding a New Agent Tool

1. Create tool class in `src/agent/tools/`
2. Inherit from `BaseTool`
3. Implement `name`, `description`, `parameters`, `execute`
4. Register in `src/agent/tools/__init__.py`
5. Add golden test case in `tests/golden/test_cases.yaml`
