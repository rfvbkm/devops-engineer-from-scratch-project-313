import os
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sentry_sdk.integrations.fastapi import FastApiIntegration

from .config import init_config
from .database import init_db
from .routers.links import router as links_router
from .routers.public import router as public_router


def _init_sentry() -> None:
    dsn = os.environ.get("SENTRY_DSN")
    if not dsn or not dsn.strip():
        return
    traces_raw = os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0").strip()
    traces_sample_rate = float(traces_raw or "0")
    sentry_debug = os.environ.get("SENTRY_DEBUG", "").lower() in (
        "1",
        "true",
        "yes",
    )
    sentry_sdk.init(
        dsn=dsn.strip(),
        send_default_pii=True,
        integrations=[FastApiIntegration()],
        traces_sample_rate=traces_sample_rate,
        debug=sentry_debug,
    )


init_config()
_init_sentry()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_config()
    init_db()
    yield
    sentry_sdk.flush(timeout=2.0)


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    sentry_sdk.capture_exception(exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


app.include_router(links_router, prefix="/api/links")
app.include_router(public_router)
