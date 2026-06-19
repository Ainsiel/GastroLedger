from typing import Protocol


class CostRecalculationStore(Protocol):
    def lease_next(self, worker_id: str): ...

    def recalculate(self, job: object) -> None: ...

    def complete(self, job: object) -> None: ...

    def fail(self, job: object, detail: str) -> None: ...


class CostRecalculationWorker:
    def __init__(self, *, store: CostRecalculationStore, worker_id: str) -> None:
        self._store = store
        self._worker_id = worker_id

    def run_once(self) -> bool:
        job = self._store.lease_next(self._worker_id)
        if job is None:
            return False
        try:
            self._store.recalculate(job)
        except Exception as error:
            self._store.fail(job, str(error))
        else:
            self._store.complete(job)
        return True
