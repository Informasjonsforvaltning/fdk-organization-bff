"""Gunicorn module."""

import logging
import multiprocessing
from os import environ as env
import sys
from typing import Any

from dotenv import load_dotenv
from gunicorn import glogging
from pythonjsonlogger import jsonlogger

load_dotenv()

HOST_PORT = env.get("HOST_PORT", "8080")
DEBUG_MODE = env.get("DEBUG_MODE", False)
LOG_LEVEL = env.get("LOG_LEVEL", "INFO")

# Gunicorn config
bind = ":" + HOST_PORT
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2 * multiprocessing.cpu_count()
timeout = 180
loglevel = str(LOG_LEVEL)
accesslog = "-"


class StackdriverJsonFormatter(jsonlogger.JsonFormatter, object):
    """json log formatter."""

    def __init__(
        self: Any,
        fmt: str = "%(levelname) %(message)",
        style: str = "%",
        *args: Any,
        **kwargs: Any
    ) -> None:
        """Init json-logger."""
        jsonlogger.JsonFormatter.__init__(self, fmt=fmt, *args, **kwargs)

    def process_log_record(self: Any, log_record: Any) -> Any:
        """Process log record to a json-format compatible with Stackdriver."""
        log_record["severity"] = log_record["levelname"]
        del log_record["levelname"]
        log_record["serviceContext"] = {"service": "fdk-organization-bff"}
        return super(StackdriverJsonFormatter, self).process_log_record(log_record)


# Override the logger to remove healthcheck (ping) from the access log and format logs as json
class CustomGunicornLogger(glogging.Logger):
    """Custom Gunicorn Logger class."""

    def setup(self: Any, cfg: Any) -> None:
        """Set up function."""
        super().setup(cfg)

        access_logger = logging.getLogger("gunicorn.access")
        access_logger.addFilter(PingFilter())
        access_logger.addFilter(ReadyFilter())
        access_logger.addFilter(BlackboxExporterFilter())

        root_logger = logging.getLogger()
        root_logger.setLevel(loglevel)

        other_loggers = [
            "gunicorn",
            "gunicorn.error",
            "gunicorn.http",
            "gunicorn.http.wsgi",
        ]
        loggers = [logging.getLogger(name) for name in other_loggers]
        loggers.append(root_logger)
        loggers.append(access_logger)

        json_handler = logging.StreamHandler(sys.stdout)
        json_handler.setFormatter(StackdriverJsonFormatter())

        for logger in loggers:
            for handler in logger.handlers:
                logger.removeHandler(handler)
            logger.addHandler(json_handler)


class PingFilter(logging.Filter):
    """Custom Ping Filter class."""

    def filter(self: Any, record: logging.LogRecord) -> bool:
        """Filter function."""
        return "GET /ping" not in record.getMessage()


class ReadyFilter(logging.Filter):
    """Custom Ready Filter class."""

    def filter(self: Any, record: logging.LogRecord) -> bool:
        """Filter function."""
        return "GET /ready" not in record.getMessage()


class BlackboxExporterFilter(logging.Filter):
    """Custom Blackbox Exporter Filter class."""

    def filter(self: Any, record: logging.LogRecord) -> bool:
        """Filter function."""
        return "Blackbox Exporter" not in record.getMessage()


logger_class = CustomGunicornLogger
