from datetime import date
from uuid import uuid4

import psycopg
import pytest
from test_production_batch_ledger import setup_production

from gastroledger_api.modules.inventory_production.public import (
    ExpiryAlertConflict,
    ExpiryAlertIdentity,
    ExpiryAlertNotFound,
    ExpiryAlertService,
)
from gastroledger_api.technical.postgres_expiry_alerts import (
    ExpiryAlertJob,
    PostgresExpiryAlertStore,
)
from gastroledger_worker.expiry_alerts import ExpiryAlertWorker


def test_worker_generates_one_alert_and_acknowledgement_retains_evidence(
    postgres_connection: psycopg.Connection[tuple[object, ...]], database_url: str
) -> None:
    production_identity, warehouse_id, _recipe_id = setup_production(database_url)
    as_of = date(2026, 6, 21)
    job_id = uuid4()
    with postgres_connection.transaction():
        lot_id = postgres_connection.execute(
            "select id from inventory_lots where tenant_id=%s and lot_code='ING-001'",
            (production_identity.tenant_id,),
        ).fetchone()[0]
        postgres_connection.execute(
            "update inventory_lots set expiry_date=%s where id=%s",
            (date(2026, 6, 23), lot_id),
        )
        postgres_connection.execute(
            """update control_jobs set status='completed'
               where tenant_id=%s and job_type='menu.cost_recalculation'""",
            (production_identity.tenant_id,),
        )
        postgres_connection.execute(
            """insert into control_jobs(
                 id,tenant_id,job_type,dedup_key,payload,correlation_id,status,attempts,
                 available_at,created_at,updated_at)
               values(%s,%s,'inventory.expiry_alerts','daily-expiry-alerts','{}',
                 'expiry-integration','queued',0,'2000-01-01',now(),now())""",
            (job_id, production_identity.tenant_id),
        )

    store = PostgresExpiryAlertStore(database_url)
    worker = ExpiryAlertWorker(store=store, worker_id="expiry-integration-worker")
    assert worker.run_once(as_of)
    store.generate(
        ExpiryAlertJob(str(job_id), production_identity.tenant_id, "repeat"),
        as_of,
    )

    identity = ExpiryAlertIdentity(
        production_identity.tenant_id, production_identity.actor_id, "tenant_admin"
    )
    service = ExpiryAlertService(store=store)
    active = service.list_alerts(identity, "active")
    assert len(active) == 1
    assert active[0].lot_id == str(lot_id)
    acknowledged = service.acknowledge(
        identity, active[0].alert_id, "Moved to today's prep", "ack-expiry"
    )
    assert acknowledged.status == "acknowledged"
    assert acknowledged.action_note == "Moved to today's prep"
    assert acknowledged.acknowledged_by == production_identity.actor_id
    assert acknowledged.acknowledged_at is not None
    assert service.list_alerts(identity, "active") == ()
    assert len(service.list_alerts(identity, "acknowledged")) == 1
    with pytest.raises(ExpiryAlertConflict):
        service.acknowledge(identity, active[0].alert_id, "Again", "ack-repeat")
    store.fail(
        ExpiryAlertJob(str(job_id), production_identity.tenant_id, "retry-evidence"),
        "temporary expiry failure",
    )

    with postgres_connection.transaction():
        counts = postgres_connection.execute(
            """select
              (select count(*) from inventory_expiry_alerts where tenant_id=%s),
              (select count(*) from control_notifications where tenant_id=%s),
              (select attempts from control_jobs where id=%s),
              (select status from control_jobs where id=%s),
              (select last_error from control_jobs where id=%s)
            """,
            (
                production_identity.tenant_id,
                production_identity.tenant_id,
                job_id,
                job_id,
                job_id,
            ),
        ).fetchone()
    assert counts == (1, 1, 1, "queued", "temporary expiry failure")


def test_other_tenant_cannot_observe_expiry_alert(
    postgres_connection: psycopg.Connection[tuple[object, ...]],
    database_url: str,
) -> None:
    first, _warehouse_id, _recipe_id = setup_production(database_url)
    second, _warehouse_id, _recipe_id = setup_production(database_url)
    with postgres_connection.transaction():
        postgres_connection.execute(
            """update control_jobs set status='completed'
               where tenant_id in (%s,%s) and job_type='menu.cost_recalculation'""",
            (first.tenant_id, second.tenant_id),
        )
    store = PostgresExpiryAlertStore(database_url)
    store.generate(ExpiryAlertJob(str(uuid4()), first.tenant_id, "isolation"), date(2026, 7, 1))
    first_identity = ExpiryAlertIdentity(first.tenant_id, first.actor_id, "tenant_admin")
    first_alert = store.list_expiry_alerts(first_identity, "active")[0]

    assert (
        store.list_expiry_alerts(
            ExpiryAlertIdentity(second.tenant_id, second.actor_id, "tenant_admin"), "active"
        )
        == ()
    )
    with pytest.raises(ExpiryAlertNotFound):
        store.acknowledge_expiry_alert(
            ExpiryAlertIdentity(second.tenant_id, second.actor_id, "tenant_admin"),
            first_alert.alert_id,
            "Cross tenant",
            "isolation-denied",
        )
