from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from config import get_short_link_base
from database import get_session
from models import Link
from schemas import LinkCreate, LinkRead, LinkUpdate

router = APIRouter()


def to_link_read(link: Link) -> LinkRead:
    base = get_short_link_base()
    short_url = f"{base}/{link.short_name}"
    return LinkRead(
        id=link.id,
        original_url=link.original_url,
        short_name=link.short_name,
        short_url=short_url,
    )


@router.get("", response_model=list[LinkRead])
def list_links(session: Session = Depends(get_session)) -> list[LinkRead]:
    stmt = select(Link).order_by(Link.id)
    links = session.exec(stmt).all()
    return [to_link_read(link) for link in links]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_link(
    body: LinkCreate,
    session: Session = Depends(get_session),
) -> Response:
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
    return Response(
        content="undefined",
        media_type="text/plain; charset=utf-8",
        status_code=status.HTTP_201_CREATED,
    )


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
