import logging
import os
import signal
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from gastroledger_api.runtime import configure_logging
from gastroledger_api.technical.postgres_cost_projection import (
    PostgresCostRecalculationStore,
)
from gastroledger_api.technical.postgres_expiry_alerts import PostgresExpiryAlertStore
from gastroledger_worker.cost_recalculation import CostRecalculationWorker
from gastroledger_worker.expiry_alerts import ExpiryAlertWorker

LOGGER = logging.getLogger(__name__)
HEARTBEAT_PATH = Path(os.getenv("WORKER_HEARTBEAT_PATH", "/tmp/gastroledger-worker.heartbeat"))
HEARTBEAT_INTERVAL_SECONDS = int(os.getenv("WORKER_HEARTBEAT_INTERVAL_SECONDS", "5"))
DATABASE_URL = os.getenv("DATABASE_URL", "")
_running = True


def stop_worker(_signum: int, _frame: object) -> None:
    global _running
    _running = False


def run() -> None:
    configure_logging()
    signal.signal(signal.SIGTERM, stop_worker)
    signal.signal(signal.SIGINT, stop_worker)
    LOGGER.info("GastroLedger worker technical entry point started")
    cost_worker = (
        CostRecalculationWorker(
            store=PostgresCostRecalculationStore(DATABASE_URL),
            worker_id=f"cost-worker-{uuid4()}",
        )
        if DATABASE_URL
        else None
    )
    expiry_worker = (
        ExpiryAlertWorker(
            store=PostgresExpiryAlertStore(DATABASE_URL),
            worker_id=f"expiry-worker-{uuid4()}",
        )
        if DATABASE_URL
        else None
    )

    while _running:
        HEARTBEAT_PATH.write_text(str(time.time()), encoding="ascii")
        if cost_worker is not None:
            try:
                cost_worker.run_once()
            except Exception:
                LOGGER.exception("Cost recalculation polling cycle failed")
        if expiry_worker is not None:
            try:
                expiry_worker.run_once(datetime.now(UTC).date())
            except Exception:
                LOGGER.exception("Expiry alert polling cycle failed")
        time.sleep(HEARTBEAT_INTERVAL_SECONDS)

    LOGGER.info("GastroLedger worker technical entry point stopped")


if __name__ == "__main__":
    run()
