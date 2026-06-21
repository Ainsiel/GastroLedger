from dataclasses import dataclass
from datetime import date

from gastroledger_worker.expiry_alerts import ExpiryAlertWorker


@dataclass
class Job:
    job_id: str = "job-1"
    tenant_id: str = "tenant-1"
    correlation_id: str = "correlation-1"


class RecordingStore:
    def __init__(self) -> None:
        self.job = Job()
        self.generated: list[tuple[Job, date]] = []
        self.completed: list[str] = []
        self.failed: list[tuple[str, str]] = []
        self.raise_on_generate = False

    def lease_next(self, worker_id: str):
        assert worker_id == "expiry-worker-1"
        job, self.job = self.job, None
        return job

    def generate(self, job: Job, as_of: date) -> None:
        if self.raise_on_generate:
            raise RuntimeError("expiry scan unavailable")
        self.generated.append((job, as_of))

    def complete(self, job: Job) -> None:
        self.completed.append(job.job_id)

    def fail(self, job: Job, detail: str) -> None:
        self.failed.append((job.job_id, detail))


def test_worker_completes_one_expiry_alert_job() -> None:
    store = RecordingStore()
    as_of = date(2026, 6, 21)

    assert ExpiryAlertWorker(store=store, worker_id="expiry-worker-1").run_once(as_of)
    assert store.generated == [(Job(), as_of)]
    assert store.completed == ["job-1"]
    assert store.failed == []


def test_worker_records_failure_for_retry() -> None:
    store = RecordingStore()
    store.raise_on_generate = True

    assert ExpiryAlertWorker(store=store, worker_id="expiry-worker-1").run_once(date(2026, 6, 21))
    assert store.completed == []
    assert store.failed == [("job-1", "expiry scan unavailable")]


def test_worker_returns_false_without_available_job() -> None:
    store = RecordingStore()
    store.job = None

    assert not ExpiryAlertWorker(store=store, worker_id="expiry-worker-1").run_once(
        date(2026, 6, 21)
    )
