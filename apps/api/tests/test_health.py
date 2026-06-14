from gastroledger_api.app import health


def test_api_health() -> None:
    assert health().model_dump() == {"service": "api", "status": "ok"}
