"""JSON structured log output."""

from __future__ import annotations

import logging

from azure_functions_logging import get_logger, setup_logging


def main() -> None:
    """Demonstrate JSON-format log output for production or CI environments."""
    setup_logging(format="json", level=logging.DEBUG)
    logger = get_logger(__name__)

    logger.info("Application started")
    logger.warning("Disk usage above 80%%")
    logger.error("Connection refused")


if __name__ == "__main__":
    main()
