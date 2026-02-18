# FlowForge AI Tests

This directory contains test suites for the FlowForge AI application.

## 🧪 Running Tests

Since the application relies on Docker services (Postgres, MLflow, Ollama), the tests are designed to be run inside the `backend` container.

### Prerequisites

Ensure the Docker stack is running:

```bash
docker-compose up -d
```

### Execution

Run the tests using `pytest` inside the container:

```bash
docker-compose exec backend pytest tests/
```

### Test Files

- `test_agents.py`: Integration tests for the Agentic Architecture, checking Orchestrator connectivity and Agent instantiation.

### Adding Tests

When adding new tests, ensure they are placed in this directory and named with the prefix `test_`.
