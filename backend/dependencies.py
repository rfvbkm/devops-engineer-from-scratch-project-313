from fastapi import Depends
from sqlmodel import Session

from .database import get_session
from .repositories.links import LinkRepository


def get_link_repository(
    session: Session = Depends(get_session),
) -> LinkRepository:
    return LinkRepository(session)
