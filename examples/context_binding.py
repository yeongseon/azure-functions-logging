"""Bind extra context fields to a logger instance."""

from __future__ import annotations

import logging

from azure_functions_logging import get_logger, setup_logging


def main() -> None:
    """Demonstrate logger.bind() for per-request context fields."""
    setup_logging(level=logging.DEBUG)
    logger = get_logger(__name__)

    # bind() returns a NEW logger - the original is unchanged
    bound = logger.bind(user_id="user-42", operation="checkout")
    bound.info("Processing payment")
    bound.warning("Retry attempt 2")

    # Original logger has no bound context
    logger.info("This line has no user_id or operation")


if __name__ == "__main__":
    main()
