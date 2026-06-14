import os
from collections.abc import Iterator

import psycopg
import pytest


@pytest.fixture
def postgres_connection() -> Iterator[psycopg.Connection[tuple[object, ...]]]:
    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("TEST_DATABASE_URL is required for the PostgreSQL integration harness")

    with psycopg.connect(database_url, autocommit=False) as connection:
        yield connection
        connection.rollback()

