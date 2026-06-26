\set ON_ERROR_STOP on
BEGIN;

CREATE TABLE IF NOT EXISTS inventory_expiry_alerts (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
 warehouse_id uuid NOT NULL, lot_id uuid NOT NULL, expiry_date date NOT NULL,
 rule_key text NOT NULL, status text NOT NULL CHECK(status IN ('active','acknowledged')),
 created_at timestamptz NOT NULL, acknowledged_by uuid REFERENCES platform_users(id),
 acknowledged_at timestamptz, action_note text,
 UNIQUE(tenant_id,lot_id,rule_key), UNIQUE(id,tenant_id),
 FOREIGN KEY(warehouse_id,tenant_id) REFERENCES platform_warehouses(id,tenant_id),
 FOREIGN KEY(lot_id,tenant_id) REFERENCES inventory_lots(id,tenant_id),
 CHECK((status='active' AND acknowledged_by IS NULL AND acknowledged_at IS NULL AND action_note IS NULL)
    OR (status='acknowledged' AND acknowledged_by IS NOT NULL AND acknowledged_at IS NOT NULL AND length(trim(action_note))>0))
);

CREATE TABLE IF NOT EXISTS control_notifications (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
 source_alert_id uuid NOT NULL UNIQUE, recipient_role text NOT NULL,
 title text NOT NULL, body text NOT NULL,
 status text NOT NULL CHECK(status IN ('active','acknowledged')),
 created_at timestamptz NOT NULL, acknowledged_at timestamptz,
 FOREIGN KEY(source_alert_id,tenant_id) REFERENCES inventory_expiry_alerts(id,tenant_id),
 CHECK((status='active' AND acknowledged_at IS NULL) OR (status='acknowledged' AND acknowledged_at IS NOT NULL))
);

GRANT SELECT,INSERT,UPDATE ON inventory_expiry_alerts,control_notifications TO gastroledger_app;
ALTER TABLE inventory_expiry_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_expiry_alerts FORCE ROW LEVEL SECURITY;
ALTER TABLE control_notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE control_notifications FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS inventory_expiry_alerts_scope ON inventory_expiry_alerts;
CREATE POLICY inventory_expiry_alerts_scope ON inventory_expiry_alerts
 USING(tenant_id=nullif(current_setting('app.current_tenant_id',true),'')::uuid)
 WITH CHECK(tenant_id=nullif(current_setting('app.current_tenant_id',true),'')::uuid);
DROP POLICY IF EXISTS control_notifications_scope ON control_notifications;
CREATE POLICY control_notifications_scope ON control_notifications
 USING(tenant_id=nullif(current_setting('app.current_tenant_id',true),'')::uuid)
 WITH CHECK(tenant_id=nullif(current_setting('app.current_tenant_id',true),'')::uuid);

CREATE OR REPLACE FUNCTION lease_expiry_alert_job(p_worker_id text,p_lease_seconds integer DEFAULT 60)
RETURNS TABLE(job_id uuid,tenant_id uuid,correlation_id text)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=public,pg_temp AS $$
BEGIN
 INSERT INTO control_jobs(id,tenant_id,job_type,dedup_key,payload,correlation_id,status,attempts,available_at,created_at,updated_at)
 SELECT gen_random_uuid(),t.id,'inventory.expiry_alerts','daily-expiry-alerts','{}'::jsonb,
        'expiry-scheduler-'||t.id,'queued',0,now(),now(),now()
 FROM platform_tenants t
 WHERE NOT EXISTS(SELECT 1 FROM control_jobs j WHERE j.tenant_id=t.id AND j.job_type='inventory.expiry_alerts' AND j.status IN ('queued','leased'));
 RETURN QUERY
 WITH candidate AS (
  SELECT id FROM control_jobs WHERE job_type='inventory.expiry_alerts' AND available_at<=now()
   AND (status='queued' OR (status='leased' AND lease_until<now()))
  ORDER BY available_at,created_at FOR UPDATE SKIP LOCKED LIMIT 1)
 UPDATE control_jobs j SET status='leased',leased_by=p_worker_id,
  lease_until=now()+make_interval(secs=>p_lease_seconds),attempts=j.attempts+1,updated_at=now()
 FROM candidate WHERE j.id=candidate.id RETURNING j.id,j.tenant_id,j.correlation_id;
END; $$;
REVOKE ALL ON FUNCTION lease_expiry_alert_job(text,integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION lease_expiry_alert_job(text,integer) TO gastroledger_app;
COMMIT;
