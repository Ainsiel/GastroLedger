\set ON_ERROR_STOP on
BEGIN;
CREATE TABLE IF NOT EXISTS inventory_waste_records (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES platform_tenants(id), command_key text NOT NULL,
 warehouse_id uuid NOT NULL, lot_id uuid NOT NULL, quantity numeric(24,10) NOT NULL CHECK(quantity>0),
 unit_cost numeric(24,10) NOT NULL CHECK(unit_cost>0), reason text NOT NULL,
 status text NOT NULL CHECK(status IN ('pending_approval','posted','rejected','corrected')),
 requested_by uuid NOT NULL REFERENCES platform_users(id), decision_by uuid REFERENCES platform_users(id),
 decision_reason text, correlation_id text NOT NULL, created_at timestamptz NOT NULL, updated_at timestamptz NOT NULL,
 UNIQUE(tenant_id,command_key), UNIQUE(id,tenant_id),
 FOREIGN KEY(warehouse_id,tenant_id) REFERENCES platform_warehouses(id,tenant_id),
 FOREIGN KEY(lot_id,tenant_id) REFERENCES inventory_lots(id,tenant_id));
ALTER TABLE inventory_transactions ADD COLUMN IF NOT EXISTS source_waste_id uuid;
DO $$ BEGIN
 IF EXISTS(SELECT 1 FROM pg_constraint WHERE conname='inventory_transactions_type_source_check') THEN ALTER TABLE inventory_transactions DROP CONSTRAINT inventory_transactions_type_source_check; END IF;
 IF NOT EXISTS(SELECT 1 FROM pg_constraint WHERE conname='inventory_transactions_waste_fk') THEN ALTER TABLE inventory_transactions ADD CONSTRAINT inventory_transactions_waste_fk FOREIGN KEY(source_waste_id,tenant_id) REFERENCES inventory_waste_records(id,tenant_id); END IF;
 ALTER TABLE inventory_transactions ADD CONSTRAINT inventory_transactions_type_source_check CHECK(
  (transaction_type='supplier_receipt' AND source_receipt_id IS NOT NULL AND source_production_batch_id IS NULL AND source_transfer_id IS NULL AND source_waste_id IS NULL) OR
  (transaction_type='production' AND source_receipt_id IS NULL AND source_production_batch_id IS NOT NULL AND source_transfer_id IS NULL AND source_waste_id IS NULL) OR
  (transaction_type IN ('transfer_dispatch','transfer_receipt') AND source_receipt_id IS NULL AND source_production_batch_id IS NULL AND source_transfer_id IS NOT NULL AND source_waste_id IS NULL) OR
  (transaction_type IN ('waste','waste_correction') AND source_receipt_id IS NULL AND source_production_batch_id IS NULL AND source_transfer_id IS NULL AND source_waste_id IS NOT NULL));
END $$;
GRANT SELECT,INSERT,UPDATE ON inventory_waste_records TO gastroledger_app;
ALTER TABLE inventory_waste_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_waste_records FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS inventory_waste_records_scope ON inventory_waste_records;
CREATE POLICY inventory_waste_records_scope ON inventory_waste_records USING(tenant_id=nullif(current_setting('app.current_tenant_id',true),'')::uuid) WITH CHECK(tenant_id=nullif(current_setting('app.current_tenant_id',true),'')::uuid);
COMMIT;
