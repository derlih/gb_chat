from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from gb_chat.db.engine import make_engine
from sqlalchemy.orm import sessionmaker

TIME_FACTORY_TIMESTAMP = 1619857471.0


@pytest.fixture
def time_factory():
    return MagicMock(
        return_value=datetime.fromtimestamp(TIME_FACTORY_TIMESTAMP, timezone.utc)
    )


@pytest.fixture
def session_factory():
    engine = make_engine("sqlite:///:memory:")
    return sessionmaker(engine)
