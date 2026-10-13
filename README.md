# EM Electromagnetic Leakage Agent

### [Open the Live Application →](https://abusuraihsakhri.github.io/em-electromagnetic-leakage-agent/)

A deterministic, illustrative threshold evaluator for hardware-security telemetry. The repository contains a browser console, a Python CLI, a FastAPI service and a separate legacy frontier evaluator. **It does not ingest RF signals, recover cryptographic keys, implement TEMPEST tests, or certify compliance.** The built-in bounds are example values, not calibrated EM emission limits.

## Browser console

Open `web/index.html` locally to evaluate measurements without a server. The browser applies the same primary worker thresholds: primary > 25, secondary > 12 or a critical flag, and configured anomaly keywords. It displays a structured result that can be downloaded as JSON. **Browser output is not HMAC-signed**; values are processed locally and are not uploaded by the page. A GitHub Pages deployment workflow is included, but public availability must be checked after deployment.

## Python setup

Python 3.9+ (CI tests 3.10–3.12):

```bash
git clone https://github.com/abusuraihsakhri/em-electromagnetic-leakage-agent.git
cd em-electromagnetic-leakage-agent
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[api,test]"
pytest -q
```

Run the primary workflow:

```bash
em-electromagnetic-leakage-engine audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
em-electromagnetic-leakage-engine batch -i sample.csv -o results.csv
em-electromagnetic-leakage-engine verify-audit
em-electromagnetic-leakage-engine serve --host 127.0.0.1 --port 8000
```

The legacy frontier workflow is available via `em-leakage-frontier` (its thresholds differ). The CLI also supports `chat`, which is a deterministic mock response, **not** a remote LLM or live analysis. The primary API provides `GET /health`, `GET /metrics`, `POST /api/audit`, `POST /api/chat` and `GET /api/audit/logs`. API docs are available at `/docs` on a running server.

## Security and data handling

The Python audit logger creates a chained HMAC-SHA256 record for each successful evaluation and verifies each signature. Its records are held **in process memory**, so they disappear on restart; supplying `AUDIT_SECRET_KEY` does not make them persistent. The regex-based identifier guard provides limited screening, **not verified de-identification or HIPAA compliance**. Do not provide sensitive patient or cryptographic information. The mock LLM makes no external model calls.

For multi-user or network-facing deployment, configure a strong independent `API_AUTH_TOKEN` (the API expects `X-API-Key`) and `AUDIT_SECRET_KEY`; terminate HTTPS at a trusted proxy and add rate limiting and durable audit storage as needed. The API is intentionally unauthenticated when `API_AUTH_TOKEN` is absent, for local development only. The Docker Compose configuration requires both secrets and binds to localhost.

```bash
cp .env.example .env
# Fill .env with two independently generated secret values.
docker compose up --build
```

Treat any key previously committed to source control as compromised and replace it. Do not commit a populated `.env`.

## Development and limitations

- Primary stack: Pydantic 2, FastAPI (optional), Uvicorn (optional), pytest, standard-library HMAC.
- Browser stack: static HTML/CSS/JavaScript; no Pyodide required.
- The static site can run under GitHub Pages. FastAPI, server-side HMAC, and persistent audit history cannot run on GitHub Pages.
- No actual EM capture, spectral density calculation, hardware integration, or standards validation is provided.
- Run `python -m compileall -q agents em_leakage_agent cli.py enrichment.py simulator.py` and `pytest -q` before deployment.
- The browser uses standard modern DOM, Blob, and download APIs; test on current Chromium/Firefox/Safari.

## License

MIT (see [LICENSE](LICENSE)).
