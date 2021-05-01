from enum import IntEnum, auto
from typing import TYPE_CHECKING, Any, List, Optional

from sqlalchemy import INTEGER, TIMESTAMP, Column, ForeignKey
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.orm import relationship
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.orm.session import Session
from sqlalchemy.types import TypeDecorator

from ..common.types import TimeFactory
from .types import Base
from .user import User


class UserHistoryEventEnum(IntEnum):
    REGISTER = auto()
    LOGIN = auto()
    LOGOUT = auto()


if TYPE_CHECKING:
    UserHistoryEventEnumEngine = TypeDecorator[UserHistoryEventEnum]
    UserRelationship = RelationshipProperty[User]
else:
    UserHistoryEventEnumEngine = TypeDecorator
    UserRelationship = RelationshipProperty


class UserHistoryEvent(UserHistoryEventEnumEngine):
    impl = INTEGER

    def process_bind_param(  # type: ignore
        self, value: Optional[UserHistoryEventEnum], dialect: Dialect
    ) -> Optional[int]:
        if not value:
            return None

        return value.value

    def process_result_value(
        self, value: Optional[Any], dialect: Dialect
    ) -> Optional[UserHistoryEventEnum]:
        if not value:
            return None

        return UserHistoryEventEnum(int(value))


class UserHistory(Base):
    __tablename__ = "user_history"

    history_id = Column("id", INTEGER, primary_key=True)
    user_id = Column(INTEGER, ForeignKey(User.user_id))
    event = Column(UserHistoryEvent, nullable=False)
    time = Column("at", TIMESTAMP(), nullable=False)

    user: UserRelationship = relationship(User, backref="history")


class UserHistoryStorage:
    def __init__(self, session: Session, time_factory: TimeFactory) -> None:
        self._session = session
        self._time_factory = time_factory

    def all(self) -> List[UserHistory]:
        return self._session.query(UserHistory).all()

    def add_register_record(self, user: User) -> None:
        self._add_record(user, UserHistoryEventEnum.REGISTER)

    def add_login_record(self, user: User) -> None:
        self._add_record(user, UserHistoryEventEnum.LOGIN)

    def add_logout_record(self, user: User) -> None:
        self._add_record(user, UserHistoryEventEnum.LOGOUT)

    def _add_record(self, user: User, event: UserHistoryEventEnum) -> None:
        user.history.append(UserHistory(event=event, time=self._time_factory()))
        self._session.commit()
