from gastroledger_api.composition import create_application


def test_supplier_offers_are_session_scoped_public_api() -> None:
    schema = create_application().openapi()

    assert schema["paths"]["/api/v1/procurement/suppliers"]["get"]["responses"]["200"]
    assert schema["paths"]["/api/v1/procurement/suppliers"]["post"]["responses"]["201"]
    assert schema["paths"]["/api/v1/procurement/offers"]["get"]["responses"]["200"]
    assert schema["paths"]["/api/v1/procurement/offers"]["post"]["responses"]["201"]

    for schema_name in ("SupplierRequest", "SupplierOfferRequest"):
        properties = schema["components"]["schemas"][schema_name]["properties"]
        assert "tenantId" not in properties
        assert "actorId" not in properties
