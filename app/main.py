from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.limiter import limiter
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.logging import LoggingMiddleware
from app.routers import auth, categories, expenses, budgets, insights

setup_logging()

app = FastAPI(
    title="Expense Tracker API",
    version="1.0.0",
    docs_url="/docs",
)

# rate limiter
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."}
    )

# middleware — order matters, first added = outermost
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENVIRONMENT == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routers
app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(expenses.router)
app.include_router(budgets.router)
app.include_router(insights.router)

@app.get("/")
async def root():
    return {
        "message": "Expense Tracker API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health():
    return {"status": "ok", "environment": settings.ENVIRONMENT}