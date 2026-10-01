"""Bounded, process-wide admission for expensive portfolio-demo computations.

No client-address trust, unbounded per-IP map, external store or paid service.
Limits reset on restart and apply per process, not across replicas.
"""
from collections import deque
from threading import Lock
from time import monotonic

from fastapi.responses import JSONResponse

MAX_DRAWS = 10_000
MAX_GRID = 20_000


def expensive(method, path):
    path = path.removeprefix('/api/v1/').removeprefix('/api/')
    head = path.split('/')[0]
    return head in {'scenario', 'robustness', 'threshold', 'reversal', 'research', 'optimize'} or (
        head == 'runs' and (method == 'POST' or path.endswith('/replay')))


class ComputeBudget:
    def __init__(self, per_minute=120, concurrent=2, clock=monotonic):
        self.per_minute, self.concurrent, self.clock = per_minute, concurrent, clock
        self.starts = deque(maxlen=per_minute)
        self.active = 0
        self.lock = Lock()

    def enter(self):
        with self.lock:
            now = self.clock()
            while self.starts and self.starts[0] <= now - 60:
                self.starts.popleft()
            if self.active >= self.concurrent or len(self.starts) >= self.per_minute:
                return False
            self.starts.append(now)
            self.active += 1
            return True

    def leave(self):
        with self.lock:
            self.active -= 1


def install_compute_limits(app):
    app.state.compute_budget = ComputeBudget()

    @app.middleware('http')
    async def admission(request, call_next):
        if not request.url.path.startswith('/api/') or not expensive(request.method, request.url.path):
            return await call_next(request)
        budget = app.state.compute_budget
        if not budget.enter():
            return JSONResponse({'detail': 'Compute limit reached; retry later',
                                 'request_id': getattr(request.state, 'request_id', None)},
                                status_code=429, headers={'Retry-After': '60'})
        try:
            return await call_next(request)
        finally:
            budget.leave()
