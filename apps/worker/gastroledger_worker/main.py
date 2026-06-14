import logging
import os
import signal
import time
from pathlib import Path

from gastroledger_api.runtime import configure_logging

LOGGER = logging.getLogger(__name__)
HEARTBEAT_PATH = Path(os.getenv("WORKER_HEARTBEAT_PATH", "/tmp/gastroledger-worker.heartbeat"))
HEARTBEAT_INTERVAL_SECONDS = int(os.getenv("WORKER_HEARTBEAT_INTERVAL_SECONDS", "5"))
_running = True


def stop_worker(_signum: int, _frame: object) -> None:
    global _running
    _running = False


def run() -> None:
    configure_logging()
    signal.signal(signal.SIGTERM, stop_worker)
    signal.signal(signal.SIGINT, stop_worker)
    LOGGER.info("GastroLedger worker technical entry point started")

    while _running:
        HEARTBEAT_PATH.write_text(str(time.time()), encoding="ascii")
        time.sleep(HEARTBEAT_INTERVAL_SECONDS)

    LOGGER.info("GastroLedger worker technical entry point stopped")


if __name__ == "__main__":
    run()

