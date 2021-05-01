import re

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import and_, exists

from .tables import User
from .user_history_storage import UserHistoryStorage


class InvalidName(ValueError):
    pass


class InvalidPassword(ValueError):
    pass


class UserExists(ValueError):
    pass


class UserStorage:
    def __init__(
        self, session: Session, user_history_storage: UserHistoryStorage
    ) -> None:
        self._session = session
        self._user_history_storage = user_history_storage

    def register_user(self, username: str, password: str) -> None:
        self._check_username(username)
        self._check_password_complexity(password)

        try:
            user = User(username=username, password=password)
            self._session.add(user)
            self._user_history_storage.add_register_record(user)
            self._session.commit()
        except IntegrityError:
            raise UserExists()

    def credentials_valid(self, username: str, password: str) -> bool:
        stmt = exists().where(
            and_(User.username == username, User.password == password)
        )
        return self._session.query(stmt).scalar()  # type: ignore

    @staticmethod
    def _check_username(username: str) -> None:
        if not username.isalnum():
            raise InvalidName("username must be alphanumeric")
        if len(username) < 4:
            raise InvalidName("username must be at least 4 chars length")

    @staticmethod
    def _check_password_complexity(password: str) -> None:
        if len(password) < 8:
            raise InvalidPassword("password must be at least 8 chars length")
        if re.search(r"\d", password) is None:
            raise InvalidPassword("password must contain at least one digit")
        if re.search(r"[A-Z]", password) is None:
            raise InvalidPassword("password must contain at least one uppercase letter")
        if re.search(r"[a-z]", password) is None:
            raise InvalidPassword("password must contain at least one lowercase letter")
        if re.search(r"[ !@#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password) is None:
            raise InvalidPassword("password must contain at least one special char")
