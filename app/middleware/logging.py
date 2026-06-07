import time
import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = structlog.get_logger()

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        request_id = getattr(request.state, "request_id", "-")
        duration_ms = round((time.perf_counter() - request.state.start_time) * 1000, 2) if hasattr(request.state, "start_time") else -1

        logger.info(
            "request",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        return response