import os

import sentry_sdk
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration


def _init_sentry() -> None:
    dsn = os.environ.get("SENTRY_DSN")
    if not dsn or not dsn.strip():
        return
    traces_raw = os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0").strip()
    traces_sample_rate = float(traces_raw or "0")
    sentry_sdk.init(
        dsn=dsn.strip(),
        integrations=[
            StarletteIntegration(),
            FastApiIntegration(),
        ],
        traces_sample_rate=traces_sample_rate,
    )


_init_sentry()

app = FastAPI()


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


@app.get("/ping")
def ping() -> Response:
    # inline + charset: иначе часть браузеров предлагает скачать ответ как файл
    return Response(
        content="pong",
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": "inline"},
    )
