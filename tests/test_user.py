import pytest
from gb_chat.db.engine import make_engine
from gb_chat.db.user import (InvalidName, InvalidPassword, UserExists,
                             UserStorage)
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def engine():
    return make_engine("sqlite:///:memory:")


@pytest.fixture
def session_factory(engine):
    return sessionmaker(engine)


@pytest.fixture
def sut(session_factory):
    return UserStorage(session_factory)


VALID_USERNAME = "user"
VALID_PASSWORD = "P@ssw0rd"


@pytest.mark.parametrize("username", ["", " ", "user 1", "usr"])
def test_registers_user_raises_when_username_invalid(username, sut):
    with pytest.raises(InvalidName):
        sut.register_user(username, VALID_PASSWORD)


@pytest.mark.parametrize("password", ["", "qwerty", "password", "passw0rd", "Passw0rd"])
def test_registers_user_raises_when_password_invalid(password, sut):
    with pytest.raises(InvalidPassword):
        sut.register_user(VALID_USERNAME, password)


def test_registers_user(sut):
    sut.register_user(VALID_USERNAME, VALID_PASSWORD)


@pytest.fixture
def sut_with_user(sut):
    sut.register_user(VALID_USERNAME, VALID_PASSWORD)
    return sut


def test_registers_user_raises_when_same_name(sut_with_user):
    with pytest.raises(UserExists):
        sut_with_user.register_user(VALID_USERNAME, "P@ssw0rd111")


@pytest.mark.parametrize(
    "username,password", [(VALID_USERNAME, "pass"), ("user1", VALID_PASSWORD)]
)
def test_credentials_invalid(username, password, sut_with_user):
    assert not sut_with_user.credentials_valid(username, password)
