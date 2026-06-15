from gastroledger_api.modules.platform_organization.domain.registration import (
    RegistrationValidationError,
    validate_registration,
)


def test_valid_registration_normalizes_tenant_slug_and_admin_email() -> None:
    registration = validate_registration(
        tenant_name="  Sabor Central  ",
        tenant_slug="Sabor-Central",
        admin_email=" ADMIN@EXAMPLE.COM ",
        password="StrongPassword123",
        branch_name="  Downtown  ",
        branch_code=" Main ",
    )

    assert registration.tenant_name == "Sabor Central"
    assert registration.tenant_slug == "sabor-central"
    assert registration.admin_email == "admin@example.com"
    assert registration.branch_name == "Downtown"
    assert registration.branch_code == "MAIN"


def test_invalid_credentials_report_stable_field_errors() -> None:
    try:
        validate_registration(
            tenant_name="",
            tenant_slug="Invalid slug!",
            admin_email="not-an-email",
            password="weak",
            branch_name=None,
            branch_code=None,
        )
    except RegistrationValidationError as error:
        assert {detail.field for detail in error.details} == {
            "tenantName",
            "tenantSlug",
            "adminEmail",
            "password",
        }
    else:
        raise AssertionError("invalid registration must fail")


def test_registration_rejects_unbounded_password_and_branch_fields() -> None:
    try:
        validate_registration(
            tenant_name="Tenant",
            tenant_slug="tenant",
            admin_email="admin@example.com",
            password="Aa1" + ("x" * 126),
            branch_name="x" * 121,
            branch_code="X" * 64,
        )
    except RegistrationValidationError as error:
        assert {detail.field for detail in error.details} == {
            "password",
            "firstBranch.name",
            "firstBranch.code",
        }
    else:
        raise AssertionError("unbounded registration fields must fail")
