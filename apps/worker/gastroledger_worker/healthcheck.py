import os
import time
from pathlib import Path

HEARTBEAT_PATH = Path(os.getenv("WORKER_HEARTBEAT_PATH", "/tmp/gastroledger-worker.heartbeat"))
MAX_HEARTBEAT_AGE_SECONDS = int(os.getenv("WORKER_MAX_HEARTBEAT_AGE_SECONDS", "15"))


def is_healthy(path: Path = HEARTBEAT_PATH, now: float | None = None) -> bool:
    if not path.exists():
        return False

    current_time = time.time() if now is None else now
    return current_time - float(path.read_text(encoding="ascii")) <= MAX_HEARTBEAT_AGE_SECONDS


if __name__ == "__main__":
    raise SystemExit(0 if is_healthy() else 1)

