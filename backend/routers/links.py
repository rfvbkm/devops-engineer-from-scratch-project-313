import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from ..config import get_short_link_base
from ..database import get_session
from ..models import Link
from ..schemas import LinkCreate, LinkRead, LinkUpdate

router = APIRouter()


def _parse_range(range_param: Optional[str]) -> Optional[tuple[int, int]]:
    if range_param is None:
        return None
    try:
        raw = json.loads(range_param)
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="Invalid range") from None
    if not isinstance(raw, list) or len(raw) != 2:
        raise HTTPException(status_code=422, detail="Invalid range")
    start, end = raw
    if type(start) is not int or type(end) is not int:
        raise HTTPException(status_code=422, detail="Invalid range")
    if start < 0 or end < start:
        raise HTTPException(status_code=422, detail="Invalid range")
    return (start, end)


def _content_range(
    total: int,
    *,
    had_range: bool,
    start: int,
    n: int,
) -> str:
    if n == 0:
        return f"links */{total}"
    if had_range:
        last = start + n - 1
        return f"links {start}-{last}/{total}"
    return f"links 0-{n - 1}/{total}"


def to_link_read(link: Link) -> LinkRead:
    base = get_short_link_base()
    short_url = f"{base}/{link.short_name}"
    return LinkRead(
        id=link.id,
        original_url=link.original_url,
        short_name=link.short_name,
        short_url=short_url,
    )


@router.get("")
def list_links(
    session: Session = Depends(get_session),
    range_param: Optional[str] = Query(default=None, alias="range"),
) -> JSONResponse:
    bounds = _parse_range(range_param)
    count_stmt = select(func.count(Link.id))
    total = session.exec(count_stmt).one()

    stmt = select(Link).order_by(Link.id)
    start = 0
    if bounds is not None:
        start, end = bounds
        stmt = stmt.offset(start).limit(end - start + 1)

    rows = list(session.exec(stmt).all())
    payload = [to_link_read(link) for link in rows]
    n = len(payload)
    cr = _content_range(total, had_range=bounds is not None, start=start, n=n)
    return JSONResponse(
        content=jsonable_encoder(payload),
        headers={"Content-Range": cr},
    )


@router.post(
    "",
    response_model=LinkRead,
    status_code=status.HTTP_201_CREATED,
)
def create_link(
    body: LinkCreate,
    session: Session = Depends(get_session),
) -> LinkRead:
    link = Link(original_url=body.original_url, short_name=body.short_name)
    session.add(link)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Short name already exists",
        ) from None
    session.refresh(link)
    return to_link_read(link)


@router.get("/{link_id}", response_model=LinkRead)
def get_link(link_id: int, session: Session = Depends(get_session)) -> LinkRead:
    link = session.get(Link, link_id)
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
        )
    return to_link_read(link)


@router.put("/{link_id}", response_model=LinkRead)
def update_link(
    link_id: int,
    body: LinkUpdate,
    session: Session = Depends(get_session),
) -> LinkRead:
    link = session.get(Link, link_id)
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
        )
    link.original_url = body.original_url
    link.short_name = body.short_name
    session.add(link)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Short name already exists",
        ) from None
    session.refresh(link)
    return to_link_read(link)


@router.delete("/{link_id}")
def delete_link(
    link_id: int,
    session: Session = Depends(get_session),
) -> Response:
    link = session.get(Link, link_id)
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
        )
    session.delete(link)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
