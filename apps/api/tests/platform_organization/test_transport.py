import asyncio
import json
from typing import Any

from fastapi import FastAPI

from gastroledger_api.composition import create_application
from gastroledger_api.technical.registration_rate_limit import RegistrationRateLimiter


async def invoke_registration(
    application: FastAPI,
    body: dict[str, object],
) -> tuple[int, dict[str, Any], dict[str, str]]:
    messages: list[dict[str, Any]] = []
    sent = False

    async def receive() -> dict[str, Any]:
        nonlocal sent
        if not sent:
            sent = True
            return {
                "type": "http.request",
                "body": json.dumps(body).encode(),
                "more_body": False,
            }
        return {"type": "http.disconnect"}

    async def send(message: dict[str, Any]) -> None:
        messages.append(message)

    headers = [(b"content-type", b"application/json")]
    await application(
        {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "POST",
            "scheme": "http",
            "path": "/api/v1/tenants/register",
            "raw_path": b"/api/v1/tenants/register",
            "query_string": b"",
            "headers": headers,
            "client": ("127.0.0.1", 12345),
            "server": ("test", 80),
        },
        receive,
        send,
    )
    start = next(message for message in messages if message["type"] == "http.response.start")
    response_body = b"".join(
        message.get("body", b"")
        for message in messages
        if message["type"] == "http.response.body"
    )
    headers = {
        key.decode(): value.decode()
        for key, value in start.get("headers", [])
    }
    return int(start["status"]), json.loads(response_body), headers


async def invoke_tenant_identity(
    application: FastAPI, query_string: bytes
) -> tuple[int, dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    sent = False

    async def receive() -> dict[str, Any]:
        nonlocal sent
        if not sent:
            sent = True
            return {"type": "http.request", "body": b"", "more_body": False}
        return {"type": "http.disconnect"}

    async def send(message: dict[str, Any]) -> None:
        messages.append(message)

    await application(
        {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": "/api/v1/session/tenant",
            "raw_path": b"/api/v1/session/tenant",
            "query_string": query_string,
            "headers": [],
            "client": ("127.0.0.1", 12345),
            "server": ("test", 80),
        },
        receive,
        send,
    )
    start = next(message for message in messages if message["type"] == "http.response.start")
    response_body = b"".join(
        message.get("body", b"")
        for message in messages
        if message["type"] == "http.response.body"
    )
    return int(start["status"]), json.loads(response_body)


def test_platform_registration_and_tenant_identity_are_public_api_operations() -> None:
    schema = create_application().openapi()

    assert schema["paths"]["/api/v1/tenants/register"]["post"]["responses"]["201"]
    assert schema["paths"]["/api/v1/session/tenant"]["get"]["responses"]["200"]


def test_transport_validation_uses_the_stable_problem_shape() -> None:
    status, body, _headers = asyncio.run(invoke_registration(create_application(), {}))

    assert status == 422
    assert body["type"] == "platform.validation_error"
    assert body["status"] == 422
    assert body["correlationId"]
    assert {error["field"] for error in body["errors"]} == {
        "tenantName",
        "tenantSlug",
        "adminEmail",
        "password",
    }


def test_public_registration_is_rate_limited_before_use_case_execution() -> None:
    application = create_application(
        registration_rate_limiter=RegistrationRateLimiter(limit=1, window_seconds=60)
    )

    first_status, _first_body, _first_headers = asyncio.run(
        invoke_registration(application, {})
    )
    second_status, second_body, second_headers = asyncio.run(
        invoke_registration(application, {})
    )

    assert first_status == 422
    assert second_status == 429
    assert second_body["type"] == "platform.registration_rate_limited"
    assert second_headers["retry-after"] == "60"


def test_public_registration_rejects_an_unbounded_request_body() -> None:
    status, body, _headers = asyncio.run(
        invoke_registration(create_application(), {"padding": "x" * (17 * 1024)})
    )

    assert status == 422
    assert body["type"] == "platform.registration_payload_too_large"
    assert body["errors"] == [
        {"field": "body", "code": "too_large", "detail": "reduce request size"}
    ]


def test_malformed_tenant_id_uses_the_stable_validation_problem() -> None:
    status, body = asyncio.run(
        invoke_tenant_identity(create_application(), b"tenantId=not-a-uuid")
    )

    assert status == 422
    assert body["type"] == "platform.validation_error"
    assert body["status"] == 422
    assert body["errors"] == [
        {"field": "query.tenantId", "code": "uuid_parsing", "detail": "review field"}
    ]
