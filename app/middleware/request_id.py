import time
from ulid import ULID
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(ULID())
        request.state.request_id = request_id
        request.state.start_time = time.perf_counter()

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - request.state.start_time) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration_ms}ms"
        return response