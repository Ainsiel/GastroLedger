from datetime import date
from typing import Protocol


class ExpiryAlertStore(Protocol):
    def lease_next(self, worker_id: str): ...

    def generate(self, job: object, as_of: date) -> None: ...

    def complete(self, job: object) -> None: ...

    def fail(self, job: object, detail: str) -> None: ...


class ExpiryAlertWorker:
    def __init__(self, *, store: ExpiryAlertStore, worker_id: str) -> None:
        self._store = store
        self._worker_id = worker_id

    def run_once(self, as_of: date) -> bool:
        job = self._store.lease_next(self._worker_id)
        if job is None:
            return False
        try:
            self._store.generate(job, as_of)
        except Exception as error:
            self._store.fail(job, str(error))
        else:
            self._store.complete(job)
        return True
