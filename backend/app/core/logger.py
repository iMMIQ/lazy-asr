"""
Logger configuration module for the ASR service.
Provides structured logging with consistent formatting across the application.
"""

import logging
import structlog
from typing import Any, Dict


def setup_logging() -> None:
    """
    Configure structured logging for the application.
    """
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
        handlers=[logging.StreamHandler()],
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger instance for the specified module.

    Args:
        name: The name of the module (usually __name__)

    Returns:
        A structured logger instance
    """
    return structlog.get_logger(name)


# Initialize logging when module is imported
setup_logging()
