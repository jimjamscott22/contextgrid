"""Optional bearer-token authentication for API and upload routes."""

from typing import Callable, Optional
import secrets

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from api.config import config


def extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    """Parse a Bearer token from an Authorization header value."""
    if not authorization:
        return None
    scheme, _, remainder = authorization.partition(" ")
    if scheme.lower() != "bearer" or not remainder:
        return None
    return remainder.strip()


def is_protected_path(path: str) -> bool:
    """Return True when the path should require authentication when a token is set."""
    return path.startswith("/api/") or path.startswith("/uploads")


class BearerTokenAuthMiddleware(BaseHTTPMiddleware):
    """Require ``Authorization: Bearer <API_TOKEN>`` when ``API_TOKEN`` is configured."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Reject unauthenticated access to protected routes."""
        if not config.API_TOKEN or not is_protected_path(request.url.path):
            return await call_next(request)

        # Allow CORS preflight without credentials.
        if request.method == "OPTIONS":
            return await call_next(request)

        provided = extract_bearer_token(request.headers.get("Authorization"))
        if provided and secrets.compare_digest(provided, config.API_TOKEN):
            return await call_next(request)

        # <img> and legacy Jinja templates cannot send Authorization headers.
        if request.url.path.startswith("/uploads"):
            query_token = request.query_params.get("token")
            if query_token and secrets.compare_digest(query_token, config.API_TOKEN):
                return await call_next(request)

        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
