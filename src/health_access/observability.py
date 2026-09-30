"""Local structured request logging and safe API errors without an external platform."""
import json
import logging
import time
from uuid import uuid4

from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("health_access")


def install_observability(app):
    @app.middleware("http")
    async def record_request(request: Request, call_next):
        request.state.request_id = uuid4().hex
        start = time.perf_counter()
        try:
            size = int(request.headers.get("content-length", "0") or 0)
        except ValueError:
            size = 1_000_001
        if size > 1_000_000:
            response = JSONResponse({"detail": "Request body too large", "request_id": request.state.request_id}, status_code=413)
        else:
            try:
                response = await call_next(request)
            except Exception:
                logger.exception("Request failed")
                response = JSONResponse({"detail": "Internal server error", "request_id": request.state.request_id}, status_code=500)
        response.headers["X-Request-ID"] = request.state.request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        logger.info(json.dumps({"event": "api_request", "request_id": request.state.request_id,
                                "method": request.method, "path": request.url.path,
                                "status": response.status_code,
                                "elapsed_ms": round((time.perf_counter()-start)*1000, 2)}))
        return response

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        return JSONResponse({"detail": exc.detail, "request_id": getattr(request.state, "request_id", None)}, status_code=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        # Do not echo arbitrary incoming values or secret-bearing input payloads.
        errors = [{"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]} for e in exc.errors()]
        return JSONResponse({"detail": errors, "request_id": getattr(request.state, "request_id", None)}, status_code=422)
