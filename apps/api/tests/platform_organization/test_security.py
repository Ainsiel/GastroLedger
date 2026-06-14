from gastroledger_api.modules.platform_organization.application.security import (
    ScryptPasswordHasher,
    SessionTokenIssuer,
)


def test_password_hash_is_salted_and_verifiable() -> None:
    hasher = ScryptPasswordHasher()

    first = hasher.hash("StrongPassword123")
    second = hasher.hash("StrongPassword123")

    assert first != second
    assert first.startswith("scrypt$")
    assert hasher.verify("StrongPassword123", first)
    assert not hasher.verify("wrong-password", first)


def test_session_token_is_opaque_and_only_hash_is_persistable() -> None:
    issuer = SessionTokenIssuer()

    session = issuer.issue()

    assert len(session.raw_token) >= 32
    assert session.raw_token not in session.token_hash
    assert issuer.hash(session.raw_token) == session.token_hash
