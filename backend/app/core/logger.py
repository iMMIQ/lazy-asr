"""
Logger configuration module for the ASR service.
Provides plain text logging with consistent formatting across the application.
"""

import logging
import sys
from typing import Any, Dict, Optional


def setup_logging() -> None:
    """
    Configure plain text logging for the application.
    """
    # Configure logging with plain text format
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s [%(name)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove existing handlers to avoid duplicate logs
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add our handler
    root_logger.addHandler(console_handler)


class CustomLogger:
    """
    Custom logger wrapper that provides a simple interface similar to structlog.
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def info(self, msg: str, *args, **kwargs) -> None:
        """Log an info message."""
        self.logger.info(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        """Log an error message."""
        self.logger.error(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        """Log a warning message."""
        self.logger.warning(msg, *args, **kwargs)

    def debug(self, msg: str, *args, **kwargs) -> None:
        """Log a debug message."""
        self.logger.debug(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs) -> None:
        """Log an exception with traceback."""
        self.logger.exception(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        """Log a critical message."""
        self.logger.critical(msg, *args, **kwargs)


def get_logger(name: str) -> CustomLogger:
    """
    Get a logger instance for the specified module.

    Args:
        name: The name of the module (usually __name__)

    Returns:
        A logger instance
    """
    return CustomLogger(name)


# Initialize logging when module is imported
setup_logging()
