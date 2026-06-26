import os
import socket
from collections.abc import Iterator
from threading import Thread
from time import monotonic, sleep

import psycopg
import pytest
import uvicorn

from gastroledger_api.composition import create_application
from gastroledger_api.technical.registration_rate_limit import RegistrationRateLimiter


@pytest.fixture
def postgres_connection() -> Iterator[psycopg.Connection[tuple[object, ...]]]:
    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("TEST_DATABASE_URL is required for the PostgreSQL integration harness")

    with psycopg.connect(database_url, autocommit=False) as connection:
        yield connection
        connection.rollback()


@pytest.fixture
def database_url() -> str:
    if not os.getenv("TEST_DATABASE_URL"):
        pytest.skip("TEST_DATABASE_URL is required for the PostgreSQL integration harness")
    value = os.getenv("DATABASE_URL")
    if not value:
        pytest.skip("DATABASE_URL is required for the PostgreSQL integration harness")
    return value


@pytest.fixture
def api_base_url(database_url: str) -> Iterator[str]:
    application = create_application(
        database_url=database_url,
        registration_rate_limiter=RegistrationRateLimiter(limit=100),
    )
    listening_socket = socket.socket()
    listening_socket.bind(("127.0.0.1", 0))
    listening_socket.listen()
    port = listening_socket.getsockname()[1]
    server = uvicorn.Server(
        uvicorn.Config(application, log_level="warning", lifespan="off")
    )
    thread = Thread(
        target=server.run,
        kwargs={"sockets": [listening_socket]},
        daemon=True,
    )
    thread.start()
    deadline = monotonic() + 5
    while not server.started and monotonic() < deadline:
        sleep(0.01)
    if not server.started:
        raise RuntimeError("integration HTTP server did not start")

    yield f"http://127.0.0.1:{port}"

    server.should_exit = True
    thread.join(timeout=5)
    listening_socket.close()
    if thread.is_alive():
        raise RuntimeError("integration HTTP server did not stop")

