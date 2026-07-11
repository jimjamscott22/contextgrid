"""ASGI middleware for ContextGrid API performance observability."""

from typing import Callable, Optional
import logging
import os
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("api.timing")


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Log method, path, status, and duration for every HTTP request."""

    def __init__(self, app, slow_ms: Optional[int] = None):
        """
        Args:
            app: ASGI application.
            slow_ms: Duration threshold for WARNING logs. Defaults to
                ``SLOW_REQUEST_MS`` env (200 if unset).
        """
        super().__init__(app)
        if slow_ms is None:
            slow_ms = int(os.getenv("SLOW_REQUEST_MS", "200"))
        self.slow_ms = slow_ms

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Measure wall-clock time around the downstream app."""
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000.0
        msg = (
            f"{request.method} {request.url.path} "
            f"{response.status_code} {duration_ms:.1f}ms"
        )
        if duration_ms >= self.slow_ms:
            logger.warning("slow request: %s", msg)
        else:
            logger.info(msg)
        return response
