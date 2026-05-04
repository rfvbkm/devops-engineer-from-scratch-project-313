from typing import Optional

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from ..models import Link


class DuplicateShortNameError(Exception):
    """Нарушение уникальности short_name."""


class LinkRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def count_links(self) -> int:
        stmt = select(func.count(Link.id))
        return self._session.exec(stmt).one()

    def list_ordered(
        self,
        *,
        offset: int = 0,
        limit: Optional[int] = None,
    ) -> list[Link]:
        stmt = select(Link).order_by(Link.id).offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        return list(self._session.exec(stmt).all())

    def get_by_id(self, link_id: int) -> Optional[Link]:
        return self._session.get(Link, link_id)

    def get_by_short_name(self, short_name: str) -> Optional[Link]:
        stmt = select(Link).where(Link.short_name == short_name)
        return self._session.exec(stmt).first()

    def create(self, *, original_url: str, short_name: str) -> Link:
        link = Link(original_url=original_url, short_name=short_name)
        self._session.add(link)
        try:
            self._session.commit()
        except IntegrityError:
            self._session.rollback()
            raise DuplicateShortNameError from None
        self._session.refresh(link)
        return link

    def update(
        self,
        link: Link,
        *,
        original_url: str,
        short_name: str,
    ) -> Link:
        link.original_url = original_url
        link.short_name = short_name
        self._session.add(link)
        try:
            self._session.commit()
        except IntegrityError:
            self._session.rollback()
            raise DuplicateShortNameError from None
        self._session.refresh(link)
        return link

    def delete_by_id(self, link_id: int) -> bool:
        link = self._session.get(Link, link_id)
        if link is None:
            return False
        self._session.delete(link)
        self._session.commit()
        return True
