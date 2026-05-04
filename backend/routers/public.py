from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, Response

from ..dependencies import get_link_repository
from ..repositories.links import LinkRepository

router = APIRouter()


@router.get("/r/{short_name}")
def redirect_short_link(
    short_name: str,
    repo: LinkRepository = Depends(get_link_repository),
) -> RedirectResponse:
    link = repo.get_by_short_name(short_name)
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
        )
    return RedirectResponse(url=link.original_url, status_code=307)


@router.get("/ping")
def ping() -> Response:
    # inline + charset: иначе часть браузеров предлагает скачать ответ как файл
    return Response(
        content="pong",
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": "inline"},
    )
