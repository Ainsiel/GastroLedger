import logging
import os


def configure_logging() -> None:
    """Configure the shared technical runtime without domain behavior."""
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
    )

