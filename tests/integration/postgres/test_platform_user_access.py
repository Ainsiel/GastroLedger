import json
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4

import psycopg


def http_json(
    method: str,
    url: str,
    *,
    payload: dict[str, object] | None = None,
    cookie: str | None = None,
) -> tuple[int, Any, Any]:
    headers = {"content-type": "application/json"}
    if cookie:
        headers["cookie"] = cookie
    request = Request(
        url,
        method=method,
        headers=headers,
        data=json.dumps(payload).encode() if payload is not None else None,
    )
    try:
        with urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read()), response.headers
    except HTTPError as error:
        return error.code, json.loads(error.read()), error.headers


def test_http_admin_invites_branch_scoped_user_once(
    postgres_connection: psycopg.Connection[tuple[object, ...]],
    api_base_url: str,
) -> None:
    slug = f"user-access-{uuid4().hex}"
    created_status, created, admin_headers = http_json(
        "POST",
        f"{api_base_url}/api/v1/tenants/register",
        payload={
            "tenantName": "User Access Tenant",
            "tenantSlug": slug,
            "adminEmail": f"{slug}@example.com",
            "password": "StrongPassword123",
        },
    )
    admin_cookie = admin_headers["set-cookie"].split(";", 1)[0]
    http_json(
        "PATCH",
        f"{api_base_url}/api/v1/tenant/settings",
        payload={"locale": "en", "baseCurrency": "USD", "branchLimit": 2},
        cookie=admin_cookie,
    )
    _, first_branch, _ = http_json(
        "POST",
        f"{api_base_url}/api/v1/branches",
        payload={"name": "Downtown", "code": "MAIN"},
        cookie=admin_cookie,
    )
    _, second_branch, _ = http_json(
        "POST",
        f"{api_base_url}/api/v1/branches",
        payload={"name": "Airport", "code": "AIRPORT"},
        cookie=admin_cookie,
    )

    invite_status, invitation, _ = http_json(
        "POST",
        f"{api_base_url}/api/v1/users/invitations",
        payload={
            "inviteeLogin": f"manager-{slug}@example.com",
            "role": "branch_manager",
            "scope": "branch",
            "branchId": first_branch["branchId"],
            "ttlHours": 24,
        },
        cookie=admin_cookie,
    )
    accept_status, accepted, accepted_headers = http_json(
        "POST",
        f"{api_base_url}/api/v1/users/invitations/accept",
        payload={
            "manualShareToken": invitation["manualShareToken"],
            "password": "StrongPassword123",
        },
    )
    assert accept_status == 200, accepted
    scoped_cookie = accepted_headers["set-cookie"].split(";", 1)[0]
    replay_status, replay, _ = http_json(
        "POST",
        f"{api_base_url}/api/v1/users/invitations/accept",
        payload={
            "manualShareToken": invitation["manualShareToken"],
            "password": "StrongPassword123",
        },
    )
    access_status, access, _ = http_json(
        "GET",
        f"{api_base_url}/api/v1/users/me/branch-access",
        cookie=scoped_cookie,
    )

    with postgres_connection.transaction():
        audit_actions = postgres_connection.execute(
            """
            select action
            from control_audit_events
            where tenant_id = %s
              and action in ('user.invitation_created', 'user.invitation_accepted')
            order by occurred_at
            """,
            (created["tenantId"],),
        ).fetchall()

    assert created_status == 201
    assert invite_status == 201
    assert invitation["manualShareToken"]
    assert accepted["tenantId"] == created["tenantId"]
    assert replay_status == 409
    assert replay["type"] == "platform.invitation_already_used"
    assert access_status == 200
    assert access["branchIds"] == [first_branch["branchId"]]
    assert second_branch["branchId"] not in access["branchIds"]
    assert audit_actions == [
        ("user.invitation_created",),
        ("user.invitation_accepted",),
    ]
