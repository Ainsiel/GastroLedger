\set ON_ERROR_STOP on

BEGIN;

CREATE TABLE IF NOT EXISTS control_outbox_events (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    event_type text NOT NULL,
    aggregate_id uuid NOT NULL,
    payload jsonb NOT NULL,
    correlation_id text NOT NULL,
    status text NOT NULL CHECK (status IN ('pending', 'processed')),
    attempts integer NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    available_at timestamptz NOT NULL,
    created_at timestamptz NOT NULL,
    processed_at timestamptz,
    last_error text,
    UNIQUE (id, tenant_id)
);

CREATE TABLE IF NOT EXISTS control_jobs (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    job_type text NOT NULL,
    dedup_key text NOT NULL,
    payload jsonb NOT NULL,
    correlation_id text NOT NULL,
    status text NOT NULL CHECK (status IN ('queued', 'leased', 'completed', 'failed')),
    attempts integer NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    available_at timestamptz NOT NULL,
    lease_until timestamptz,
    leased_by text,
    last_error text,
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    UNIQUE (id, tenant_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS control_jobs_active_dedup
ON control_jobs (tenant_id, job_type, dedup_key)
WHERE status IN ('queued', 'leased');

CREATE TABLE IF NOT EXISTS menu_cost_projection_states (
    recipe_version_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    status text NOT NULL CHECK (status IN ('current', 'pending', 'stale', 'failed')),
    updated_at timestamptz NOT NULL,
    last_error text,
    CONSTRAINT menu_cost_projection_states_version_fk
        FOREIGN KEY (recipe_version_id, tenant_id)
        REFERENCES menu_recipe_versions (id, tenant_id)
);

CREATE TABLE IF NOT EXISTS menu_cost_projection_snapshots (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    recipe_version_id uuid NOT NULL,
    source_job_id uuid NOT NULL,
    total_cost numeric(24, 10) NOT NULL CHECK (total_cost >= 0),
    calculated_at timestamptz NOT NULL,
    UNIQUE (tenant_id, recipe_version_id, source_job_id),
    CONSTRAINT menu_cost_projection_snapshots_version_fk
        FOREIGN KEY (recipe_version_id, tenant_id)
        REFERENCES menu_recipe_versions (id, tenant_id),
    CONSTRAINT menu_cost_projection_snapshots_job_fk
        FOREIGN KEY (source_job_id, tenant_id)
        REFERENCES control_jobs (id, tenant_id)
);

GRANT SELECT, INSERT, UPDATE ON
    control_outbox_events,
    control_jobs,
    menu_cost_projection_states,
    menu_cost_projection_snapshots
TO gastroledger_app;

ALTER TABLE control_outbox_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE control_outbox_events FORCE ROW LEVEL SECURITY;
ALTER TABLE control_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE control_jobs FORCE ROW LEVEL SECURITY;
ALTER TABLE menu_cost_projection_states ENABLE ROW LEVEL SECURITY;
ALTER TABLE menu_cost_projection_states FORCE ROW LEVEL SECURITY;
ALTER TABLE menu_cost_projection_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE menu_cost_projection_snapshots FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS control_outbox_events_scope ON control_outbox_events;
CREATE POLICY control_outbox_events_scope ON control_outbox_events
USING (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)
WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid);
DROP POLICY IF EXISTS control_jobs_scope ON control_jobs;
CREATE POLICY control_jobs_scope ON control_jobs
USING (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)
WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid);
DROP POLICY IF EXISTS menu_cost_projection_states_scope ON menu_cost_projection_states;
CREATE POLICY menu_cost_projection_states_scope ON menu_cost_projection_states
USING (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)
WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid);
DROP POLICY IF EXISTS menu_cost_projection_snapshots_scope ON menu_cost_projection_snapshots;
CREATE POLICY menu_cost_projection_snapshots_scope ON menu_cost_projection_snapshots
USING (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)
WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid);

CREATE OR REPLACE FUNCTION lease_cost_recalculation_job(
    p_worker_id text,
    p_lease_seconds integer DEFAULT 60
)
RETURNS TABLE (
    job_id uuid,
    tenant_id uuid,
    correlation_id text,
    ingredient_id text
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
BEGIN
    RETURN QUERY
    WITH candidate AS (
        SELECT id
        FROM control_jobs
        WHERE job_type = 'menu.cost_recalculation'
          AND available_at <= now()
          AND (
              status = 'queued'
              OR (status = 'leased' AND lease_until < now())
          )
        ORDER BY available_at, created_at
        FOR UPDATE SKIP LOCKED
        LIMIT 1
    )
    UPDATE control_jobs AS job
    SET status = 'leased',
        leased_by = p_worker_id,
        lease_until = now() + make_interval(secs => p_lease_seconds),
        attempts = job.attempts + 1,
        updated_at = now()
    FROM candidate
    WHERE job.id = candidate.id
    RETURNING job.id, job.tenant_id, job.correlation_id,
              job.payload ->> 'ingredientId';
END;
$$;

REVOKE ALL ON FUNCTION lease_cost_recalculation_job(text, integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION lease_cost_recalculation_job(text, integer) TO gastroledger_app;

COMMIT;
