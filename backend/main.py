import os
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, Response
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sqlmodel import Session, select

from .config import init_config
from .database import get_session, init_db
from .models import Link
from .routers.links import router as links_router


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


@app.get("/r/{short_name}")
def redirect_short_link(
    short_name: str,
    session: Session = Depends(get_session),
) -> RedirectResponse:
    stmt = select(Link).where(Link.short_name == short_name)
    link = session.exec(stmt).first()
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
        )
    return RedirectResponse(url=link.original_url, status_code=307)


@app.get("/ping")
def ping() -> Response:
    # inline + charset: иначе часть браузеров предлагает скачать ответ как файл
    return Response(
        content="pong",
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": "inline"},
    )
