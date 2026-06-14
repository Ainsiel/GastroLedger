from pathlib import Path

from gastroledger_worker.healthcheck import is_healthy


def test_worker_healthcheck_accepts_a_recent_heartbeat(tmp_path: Path) -> None:
    heartbeat = tmp_path / "worker.heartbeat"
    heartbeat.write_text("100", encoding="ascii")

    assert is_healthy(heartbeat, now=105)


def test_worker_healthcheck_rejects_a_missing_heartbeat(tmp_path: Path) -> None:
    assert not is_healthy(tmp_path / "missing.heartbeat", now=105)

