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

## Free services only

`render.yaml` defines one `plan: free` web service, no database, disk, worker,
paid add-on or third-party monitoring service. Deployment remains parked until
account access and explicit deployment approval are given. Do not upgrade the
plan or attach a paid service to work around a free-tier limit.

Render's current free-service policy (checked 2026-10-01): idle web services spin
down after 15 minutes and may take about a minute to wake. Local run JSON is lost
on spin-down, restart or redeploy. Export important run/memo artifacts before
leaving the demo. There are 750 free instance hours per workspace per month;
build minutes and outbound bandwidth also have included limits. A free compute
plan alone does NOT guarantee zero charges: overages can bill when a payment
method is present. For this user's free-only requirement, verify that the
workspace has no payment method and will suspend services/builds at limits
before deploying. If the account cannot enforce zero charges, stop and ask.
No payment method or paid resource is required by this blueprint.

Source: https://render.com/docs/free . Re-check these terms at deployment time.

## Compute protection scope

API draws are capped at 10,000, optimization at 8 options / 20,000 combinations,
and expensive endpoints share 120 starts/minute and at most 2 active computations
per process. Both route mounts use the same admission budget. A rejected request
returns structured 429 with Retry-After and request ID. Replay of older oversized
runs is available offline, not through the API. These in-memory limits reset on
restart and are NOT a distributed rate limit, authentication, traffic filtering
or production DDoS protection. Keep the single-process demo architecture until
an operational review approves anything broader.
