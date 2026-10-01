"""Application composition; resource endpoints live in routes/."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .observability import install_observability
from .limits import install_compute_limits
from .routes.context import ROOT
from .routes import evidence, cases, scenarios, runs, analysis, memos, system

app = FastAPI(title="District Health Access Lab", version="0.3.0",
              description="Observed indicator table + separate hypothetical simulation. Not policy advice.")
install_compute_limits(app)
install_observability(app)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"],
                   allow_methods=["GET", "POST"], allow_headers=["*"])

for resource in (evidence, cases, scenarios, runs, analysis, memos, system):
    app.include_router(resource.router, prefix="/api/v1")
    app.include_router(resource.router, prefix="/api", include_in_schema=False)
app.add_api_route("/health", system.health, methods=["GET"], include_in_schema=False)

if (ROOT / "web/dist").exists():
    app.mount("/", StaticFiles(directory=ROOT / "web/dist", html=True), name="web")
