# Em Electromagnetic Leakage Agent

> **Domain:** Hardware Security & Electromagnetic Side-Channel Analysis
> **Standards:** TEMPEST / NATO SDIP-27 / CAP / CLSI / ISO

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## Overview

Em Electromagnetic Leakage Agent is a multi-agent evaluation system for analyzing electromagnetic side-channel leakage, RF emissions, and hardware security compliance. It processes task payloads through specialized worker agents that check safety boundaries, protocol conformance, and invariant thresholds.

The system exposes:
- A CLI for interactive and batch evaluation
- A FastAPI REST API for programmatic access
- A WebSocket telemetry streamer for real-time monitoring
- Prometheus-compatible operational metrics

---

## Architecture

```
em-electromagnetic-leakage-agent/
├── agents/                  # Core agent framework (Pydantic-based)
│   ├── __init__.py          # Package version
│   ├── base.py              # PHI guard, HMAC audit trail, security
│   ├── models.py            # Data models with input validation
│   ├── workers.py           # Specialized evaluation workers
│   ├── supervisor.py        # Multi-agent orchestrator
│   ├── api.py               # FastAPI REST endpoints
│   ├── metrics.py           # Prometheus metrics collector
│   ├── learning.py          # Bayesian calibration engine
│   ├── llm_factory.py       # LLM provider adapter (mock by default)
│   └── streamer.py          # WebSocket telemetry broadcaster
├── em_leakage_agent/        # Frontier domain engine (dataclass-based)
│   ├── models.py            # Frontier payload definitions
│   ├── engine.py            # Core algorithmic engine
│   ├── agents.py            # Sub-agent implementations
│   ├── cli.py               # CLI for frontier engine
│   └── server.py            # FastAPI server factory
├── tests/                   # Pytest test suite
├── web/index.html           # Operations console (static HTML)
├── cli.py                   # Primary CLI entry point
├── simulator.py             # Stress testing simulator
├── enrichment.py            # Additional enrichment engines
└── Dockerfile               # Container build
```

---

## Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/em-electromagnetic-leakage-agent.git
cd em-electromagnetic-leakage-agent

# Install dependencies
pip install fastapi uvicorn pydantic pytest
```

---

## Configuration

| Environment Variable | Description | Default |
|:---------------------|:------------|:--------|
| `AUDIT_SECRET_KEY` | HMAC-SHA256 signing key for audit trail | Random per-process (ephemeral) |
| `MODEL_PROVIDER` | LLM provider (`mock`, `ollama`, `claude`, `openai`) | `mock` |

> **Security Note:** Always set `AUDIT_SECRET_KEY` in production to ensure audit signature reproducibility across restarts.

---

## CLI Usage

### Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### Supervisory Chat
```bash
python cli.py chat "What is the system status?"
```

### Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### Verify Audit Integrity
```bash
python cli.py verify-audit
```

### Start REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

---

## REST API Endpoints

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| `GET` | `/health` | Health check |
| `GET` | `/metrics` | Prometheus operational metrics |
| `POST` | `/api/audit` | Submit task for evaluation |
| `POST` | `/api/chat` | Supervisory chat query |
| `GET` | `/api/audit/logs` | Retrieve and verify audit trail |

### Example API Request
```bash
curl -X POST http://localhost:8000/api/audit \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "TASK-2026-001",
    "target_identifier": "KEY-01",
    "primary_metric": 28.5,
    "secondary_metric": 14.2,
    "status_descriptor": "DISCORDANT_ANOMALY",
    "is_critical_flag": true
  }'
```

---

## Input Data Schema

| Field | Type | Description | Requirement |
|:------|:-----|:------------|:------------|
| `task_id` | `str` | Unique task identifier | Required |
| `target_identifier` | `str` | Target entity key | Required |
| `primary_metric` | `float` | Primary measurement (finite) | Required |
| `secondary_metric` | `float` | Secondary measurement (finite) | Optional (default: `0.0`) |
| `status_descriptor` | `str` | Status or phenotype code | Optional (default: `NOMINAL`) |
| `is_critical_flag` | `bool` | Emergency escalation flag | Optional (default: `false`) |

> **Validation:** Metric values must be finite (NaN and Infinity are rejected). Identifier fields are stripped and must not be empty.

---

## Testing

```bash
# Run full test suite
pytest -v

# Run with coverage
pytest -v --cov=agents --cov=em_leakage_agent
```

---

## Simulation & Benchmarking

```bash
# Run stress simulation (default: 100 tasks)
python simulator.py 1000
```

---

## Container Deployment

```bash
# Build and run with Docker
docker build -t em-electromagnetic-leakage-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key em-electromagnetic-leakage-agent

# Or use Docker Compose
docker-compose up -d
```

---

## Security Features

- **Zero-PHI Outbound Interceptor:** Regex-based detection and blocking of SSNs, MRNs, phone numbers, and patient identifiers
- **HMAC-SHA256 Audit Trail:** Tamper-evident, chained cryptographic audit log with secure key generation
- **Input Validation:** Rejection of non-finite metric values and empty identifiers
- **File Operation Safety:** Proper error handling for file not found and permission errors
