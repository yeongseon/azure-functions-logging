"""Basic logging setup with azure-functions-logging."""

from __future__ import annotations

import logging

from azure_functions_logging import get_logger, setup_logging


def main() -> None:
    """Demonstrate basic setup_logging + get_logger usage."""
    setup_logging(level=logging.DEBUG)
    logger = get_logger(__name__)

    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")


if __name__ == "__main__":
    main()
