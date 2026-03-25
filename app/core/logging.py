"""Logging setup."""

import logging
import sys

from pythonjsonlogger import jsonlogger

from app.core.config import get_settings
from app.utils.tracking import get_request_id


class RequestAwareJsonFormatter(jsonlogger.JsonFormatter):
    """JSON formatter that injects the request ID."""

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record["request_id"] = get_request_id()
        log_record["logger"] = record.name
        log_record["level"] = record.levelname


def configure_logging() -> None:
    """Configure root logging for the application."""
    settings = get_settings()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        RequestAwareJsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s"
        )
    )

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(settings.log_level.upper())
