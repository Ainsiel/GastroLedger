import base64
import hashlib
import hmac
import secrets
from dataclasses import dataclass

from gastroledger_api.application.identifiers import ActorId, TenantId


@dataclass(frozen=True)
class IssuedSession:
    raw_token: str
    token_hash: str


@dataclass(frozen=True)
class SessionLoginResult:
    tenant_id: TenantId
    actor_id: ActorId
    tenant_name: str
    tenant_slug: str
    session_token: str


class InvalidCredentials(Exception):
    pass


class TenantLoginAmbiguous(Exception):
    pass


class ScryptPasswordHasher:
    def hash(self, password: str) -> str:
        salt = secrets.token_bytes(16)
        digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
        return "scrypt${}${}".format(
            base64.urlsafe_b64encode(salt).decode("ascii"),
            base64.urlsafe_b64encode(digest).decode("ascii"),
        )

    def verify(self, password: str, encoded: str) -> bool:
        try:
            algorithm, salt_value, digest_value = encoded.split("$", 2)
            if algorithm != "scrypt":
                return False
            salt = base64.urlsafe_b64decode(salt_value)
            expected = base64.urlsafe_b64decode(digest_value)
        except (ValueError, TypeError):
            return False
        actual = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
        return hmac.compare_digest(actual, expected)


class SessionTokenIssuer:
    def issue(self) -> IssuedSession:
        raw_token = secrets.token_urlsafe(32)
        return IssuedSession(raw_token=raw_token, token_hash=self.hash(raw_token))

    def hash(self, raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
