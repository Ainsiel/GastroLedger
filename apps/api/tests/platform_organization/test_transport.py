from gastroledger_api.composition import create_application


def test_platform_registration_and_tenant_identity_are_public_api_operations() -> None:
    schema = create_application().openapi()

    assert schema["paths"]["/api/v1/tenants/register"]["post"]["responses"]["201"]
    assert schema["paths"]["/api/v1/session/tenant"]["get"]["responses"]["200"]
