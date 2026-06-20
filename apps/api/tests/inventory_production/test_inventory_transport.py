from gastroledger_api.composition import create_application


def test_production_batch_is_a_session_scoped_public_api() -> None:
    schema = create_application().openapi()
    operation = schema["paths"][
        "/api/v1/inventory/production-batches/{batchId}/post"
    ]["post"]

    assert operation["responses"]["201"]
    properties = schema["components"]["schemas"]["ProductionBatchRequest"]["properties"]
    assert "tenantId" not in properties
    assert "actorId" not in properties
