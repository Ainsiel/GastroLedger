from gastroledger_api.technical.postgres_platform import sqlalchemy_database_url


def test_postgresql_url_explicitly_selects_the_psycopg_driver() -> None:
    database_url = "postgresql://runtime:secret@postgres:5432/gastroledger"

    assert sqlalchemy_database_url(database_url) == (
        "postgresql+psycopg://runtime:secret@postgres:5432/gastroledger"
    )


def test_explicit_sqlalchemy_driver_is_preserved() -> None:
    database_url = "postgresql+psycopg://runtime:secret@postgres:5432/gastroledger"

    assert sqlalchemy_database_url(database_url) == database_url
