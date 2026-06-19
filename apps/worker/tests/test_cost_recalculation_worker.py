from dataclasses import dataclass

from gastroledger_worker.cost_recalculation import CostRecalculationWorker


@dataclass
class Job:
    job_id: str = "job-1"
    tenant_id: str = "tenant-1"
    correlation_id: str = "correlation-1"
    ingredient_id: str = "ingredient-1"


class RecordingStore:
    def __init__(self) -> None:
        self.job = Job()
        self.completed: list[str] = []
        self.failed: list[tuple[str, str]] = []
        self.recalculated: list[Job] = []
        self.raise_on_recalculate = False

    def lease_next(self, worker_id: str):
        assert worker_id == "worker-1"
        job, self.job = self.job, None
        return job

    def recalculate(self, job: Job) -> None:
        if self.raise_on_recalculate:
            raise RuntimeError("cost unavailable")
        self.recalculated.append(job)

    def complete(self, job: Job) -> None:
        self.completed.append(job.job_id)

    def fail(self, job: Job, detail: str) -> None:
        self.failed.append((job.job_id, detail))


def test_worker_completes_one_leased_cost_recalculation() -> None:
    store = RecordingStore()

    processed = CostRecalculationWorker(store=store, worker_id="worker-1").run_once()

    assert processed
    assert store.recalculated == [Job()]
    assert store.completed == ["job-1"]
    assert store.failed == []


def test_worker_records_retry_evidence_without_hiding_failure() -> None:
    store = RecordingStore()
    store.raise_on_recalculate = True

    processed = CostRecalculationWorker(store=store, worker_id="worker-1").run_once()

    assert processed
    assert store.completed == []
    assert store.failed == [("job-1", "cost unavailable")]


def test_worker_returns_false_when_no_job_is_available() -> None:
    store = RecordingStore()
    store.job = None

    assert not CostRecalculationWorker(store=store, worker_id="worker-1").run_once()
