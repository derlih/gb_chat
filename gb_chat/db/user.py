import re

from sqlalchemy import INTEGER, VARCHAR, Column
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import and_, exists

from .types import Base


class InvalidName(ValueError):
    pass


class InvalidPassword(ValueError):
    pass


class UserExists(ValueError):
    pass


class User(Base):
    __tablename__ = "users"

    user_id = Column("id", INTEGER, primary_key=True)
    username = Column(VARCHAR, nullable=False, unique=True)
    password = Column(VARCHAR, nullable=False)


class UserStorage:
    def __init__(self, session: Session) -> None:
        self._session = session

    def register_user(self, username: str, password: str) -> None:
        self._check_username(username)
        self._check_password_complexity(password)

        try:
            self._session.add(User(username=username, password=password))
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
