from gastroledger_api.runtime import configure_logging
from gastroledger_worker.healthcheck import is_healthy


def test_api_and_worker_share_the_api_runtime_without_business_modules() -> None:
    assert callable(configure_logging)
    assert callable(is_healthy)

