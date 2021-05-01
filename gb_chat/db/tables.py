from enum import IntEnum, auto
from typing import TYPE_CHECKING, Any, List, Optional, Type

from sqlalchemy import INTEGER, TIMESTAMP, VARCHAR, Column, ForeignKey
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.sql.type_api import TypeDecorator

Base: Type[DeclarativeMeta] = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column("id", INTEGER, primary_key=True)
    username = Column(VARCHAR, nullable=False, unique=True)
    password = Column(VARCHAR, nullable=False)
    history: List["UserHistory"]


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
