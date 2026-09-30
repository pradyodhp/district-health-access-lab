# Deployment configuration, not a deployed-service claim

No hosted service was launched during this upgrade. The Render blueprint builds dependencies/data/frontend and starts Uvicorn with `/health`. It specifies Python 3.11 and Node 22. Local validation uses the commands below. This is a portfolio demo, not a public production health service.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
python3 scripts/build_data.py
(cd web && npm ci && npm run build)
uvicorn health_access.api:app --app-dir src --host 127.0.0.1 --port 8000
# another shell with the same environment:
python3 scripts/smoke_api.py http://127.0.0.1:8000
```

`PORT` is supplied by Render. Optional `APP_GIT_COMMIT` records artifact code provenance; without it the manifest honestly says unknown. Runs use local disk, excluded from Git, and are not durable across stateless restarts/replicas. Do not claim retained hosted runs. Hosted deployment needs explicit approval, environment/platform verification, durable storage requirements, auth/rate/resource/retention policy and operational review. The current CORS list allows local Vite development; same-origin built assets do not need cross-origin permission. No secrets or patient records are required.
