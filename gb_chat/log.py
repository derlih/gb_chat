import logging.config
import socket
import sys
from contextlib import contextmanager
from typing import Any, Optional

import structlog
from structlog.contextvars import (bind_contextvars, merge_contextvars,
                                   unbind_contextvars)


def configure_logging(processor: Any):
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "formater": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": processor,
                    # Adjust log entries that are not from structlog
                    "foreign_pre_chain": [
                        merge_contextvars,
                        structlog.stdlib.add_log_level,
                        structlog.stdlib.add_logger_name,
                        structlog.processors.TimeStamper(fmt="iso"),
                        structlog.processors.format_exc_info,  # type: ignore
                    ],
                },
            },
            "handlers": {
                "default": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "formater",
                },
            },
            "loggers": {
                "": {"handlers": ["default"], "level": "DEBUG", "propagate": True,},
            },
        }
    )

    structlog.configure_once(  # type: ignore
        processors=[  # type: ignore
            merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,  # type: ignore
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


@contextmanager
def bind_remote_address_to_logger(sock: socket.socket):
    try:
        bind_contextvars(remote=sock.getpeername())
    except socket.error:
        pass

    try:
        yield
    finally:
        unbind_contextvars("remote")


@contextmanager
def bind_client_name_to_logger(name: str):
    if name:
        bind_contextvars(client=name)

    try:
        yield
    finally:
        unbind_contextvars("client")


def get_logger(name: Optional[str] = None) -> Any:
    logger = structlog.get_logger()
    if not name:
        f = sys._getframe().f_back  # type: ignore
        name = f.f_globals.get("__name__") or None

    if name:
        return logger.bind(logger=name)
    return logger
