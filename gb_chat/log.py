# type: ignore
import logging.config
import socket
from contextlib import contextmanager

import structlog
from structlog.contextvars import (bind_contextvars, merge_contextvars,
                                   unbind_contextvars)


def configure_logging(processor):
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
                        structlog.processors.format_exc_info,
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

    structlog.configure_once(
        processors=[
            merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
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
        bind_contextvars(client=connection.client.name)

    try:
        yield
    finally:
        unbind_contextvars("client")
