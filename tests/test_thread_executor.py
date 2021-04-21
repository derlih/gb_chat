from unittest.mock import MagicMock

import pytest
from gb_chat.common.thread_executor import IoThreadExecutor


@pytest.mark.parametrize("tasks", [[MagicMock()], [MagicMock(), MagicMock()]])
def test_io_thread_execute(tasks):
    io_thread_executor = IoThreadExecutor()
    for task in tasks:
        io_thread_executor.schedule(task)

    io_thread_executor.execute_all()
    for task in tasks:
        task.assert_called_once()
