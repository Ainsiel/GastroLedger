from collections import OrderedDict
from collections.abc import Awaitable, Callable
from threading import Lock
from time import monotonic
from typing import Any
from uuid import uuid4

from gastroledger_api.technical.problems import problem_response

AsgiMessage = dict[str, Any]
AsgiReceive = Callable[[], Awaitable[AsgiMessage]]
AsgiSend = Callable[[AsgiMessage], Awaitable[None]]
AsgiScope = dict[str, Any]
AsgiApplication = Callable[[AsgiScope, AsgiReceive, AsgiSend], Awaitable[None]]
REGISTRATION_PATH = "/api/v1/tenants/register"


class RegistrationRateLimiter:
    def __init__(
        self,
        *,
        limit: int = 5,
        window_seconds: int = 60,
        max_keys: int = 4096,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._max_keys = max_keys
        self._clock = clock
        self._windows: OrderedDict[str, tuple[float, int]] = OrderedDict()
        self._lock = Lock()

    def allow(self, key: str) -> bool:
        now = self._clock()
        with self._lock:
            started_at, count = self._windows.get(key, (now, 0))
            if now - started_at >= self.window_seconds:
                started_at, count = now, 0
            if key not in self._windows and len(self._windows) >= self._max_keys:
                self._windows.popitem(last=False)
            self._windows[key] = (started_at, count + 1)
            self._windows.move_to_end(key)
            return count < self.limit


class RegistrationRateLimitMiddleware:
    def __init__(self, app: AsgiApplication, limiter: RegistrationRateLimiter) -> None:
        self._app = app
        self._limiter = limiter

    async def __call__(
        self, scope: AsgiScope, receive: AsgiReceive, send: AsgiSend
    ) -> None:
        if (
            scope["type"] == "http"
            and scope["method"] == "POST"
            and scope["path"] == REGISTRATION_PATH
        ):
            client = scope.get("client")
            key = str(client[0]) if client else "unknown"
            if not self._limiter.allow(key):
                response = problem_response(
                    429,
                    "platform.registration_rate_limited",
                    str(uuid4()),
                    [],
                    headers={"Retry-After": str(self._limiter.window_seconds)},
                )
                await response(scope, receive, send)
                return
        await self._app(scope, receive, send)


class RegistrationPayloadLimitMiddleware:
    def __init__(self, app: AsgiApplication, max_body_bytes: int = 16 * 1024) -> None:
        self._app = app
        self._max_body_bytes = max_body_bytes

    async def __call__(
        self, scope: AsgiScope, receive: AsgiReceive, send: AsgiSend
    ) -> None:
        if not (
            scope["type"] == "http"
            and scope["method"] == "POST"
            and scope["path"] == REGISTRATION_PATH
        ):
            await self._app(scope, receive, send)
            return

        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            body.extend(message.get("body", b""))
            if len(body) > self._max_body_bytes:
                response = problem_response(
                    422,
                    "platform.registration_payload_too_large",
                    str(uuid4()),
                    [{"field": "body", "code": "too_large", "detail": "reduce request size"}],
                )
                await response(scope, receive, send)
                return
            if not message.get("more_body", False):
                break

        delivered = False

        async def replay_receive() -> AsgiMessage:
            nonlocal delivered
            if delivered:
                return {"type": "http.disconnect"}
            delivered = True
            return {"type": "http.request", "body": bytes(body), "more_body": False}

        await self._app(scope, replay_receive, send)
