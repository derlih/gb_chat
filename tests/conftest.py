from unittest.mock import MagicMock

import pytest
from gb_chat.db.engine import make_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def time_factory():
    return MagicMock(return_value=123)


@pytest.fixture
def session_factory():
    engine = make_engine("sqlite:///:memory:")
    return sessionmaker(engine)
