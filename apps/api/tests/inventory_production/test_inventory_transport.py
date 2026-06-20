from gastroledger_api.composition import create_application


def test_production_batch_is_a_session_scoped_public_api() -> None:
    schema = create_application().openapi()
    operation = schema["paths"]["/api/v1/inventory/production-batches/{batchId}/post"]["post"]

    assert operation["responses"]["201"]
    properties = schema["components"]["schemas"]["ProductionBatchRequest"]["properties"]
    assert "tenantId" not in properties
    assert "actorId" not in properties
    for path in (
        "/api/v1/inventory/transfers",
        "/api/v1/inventory/transfers/{transferId}/approve",
        "/api/v1/inventory/transfers/{transferId}/dispatch/{commandId}",
        "/api/v1/inventory/transfers/{transferId}/receive/{commandId}",
    ):
        assert schema["paths"][path]["post"]["responses"][
            "200" if path != "/api/v1/inventory/transfers" else "201"
        ]
    for path in (
        "/api/v1/inventory/waste/{commandId}",
        "/api/v1/inventory/waste/{wasteId}/approve/{commandId}",
        "/api/v1/inventory/waste/{wasteId}/reject",
        "/api/v1/inventory/waste/{wasteId}/correct/{commandId}",
    ):
        assert schema["paths"][path]["post"]
