from typing import List

from sqlalchemy.orm.session import Session

from ..common.types import TimeFactory
from .tables import User, UserHistory, UserHistoryEventEnum


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
