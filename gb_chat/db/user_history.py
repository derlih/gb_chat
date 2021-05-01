from sqlalchemy import DATETIME, INTEGER, Column, ForeignKey

from ..common.types import TimeFactory
from .types import Base, SessionFactory
from .user import User


class UserHistory(Base):
    __tablename__ = "user_history"

    user_id = Column(INTEGER, ForeignKey("users.id"), primary_key=True)
    login_time = Column("loggedin_at", DATETIME(), nullable=False)


class UserHistoryStorage:
    def __init__(
        self, session_factory: SessionFactory, time_factory: TimeFactory
    ) -> None:
        self._session_factory = session_factory
        self._time_factory = time_factory

    def add_login_record(self, user: User) -> None:
        pass
