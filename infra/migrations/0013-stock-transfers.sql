\set ON_ERROR_STOP on
BEGIN;
CREATE TABLE IF NOT EXISTS inventory_transfers (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES platform_tenants(id), transfer_number text NOT NULL,
 source_warehouse_id uuid NOT NULL, destination_warehouse_id uuid NOT NULL, status text NOT NULL,
 requested_by uuid NOT NULL REFERENCES platform_users(id), approved_by uuid REFERENCES platform_users(id),
 correlation_id text NOT NULL, created_at timestamptz NOT NULL, updated_at timestamptz NOT NULL,
 UNIQUE(tenant_id, transfer_number), UNIQUE(id, tenant_id), CHECK(source_warehouse_id <> destination_warehouse_id),
 FOREIGN KEY(source_warehouse_id,tenant_id) REFERENCES platform_warehouses(id,tenant_id),
 FOREIGN KEY(destination_warehouse_id,tenant_id) REFERENCES platform_warehouses(id,tenant_id));
CREATE TABLE IF NOT EXISTS inventory_transfer_lines (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES platform_tenants(id), transfer_id uuid NOT NULL UNIQUE,
 item_type text NOT NULL CHECK(item_type IN ('ingredient','prepared_recipe')), item_id uuid NOT NULL, unit_id uuid NOT NULL,
 requested_quantity numeric(24,10) NOT NULL CHECK(requested_quantity > 0), approved_quantity numeric(24,10) NOT NULL DEFAULT 0,
 dispatched_quantity numeric(24,10) NOT NULL DEFAULT 0, received_quantity numeric(24,10) NOT NULL DEFAULT 0,
 loss_quantity numeric(24,10) NOT NULL DEFAULT 0, loss_reason text,
 FOREIGN KEY(transfer_id,tenant_id) REFERENCES inventory_transfers(id,tenant_id),
 CHECK(approved_quantity >= 0 AND approved_quantity <= requested_quantity),
 CHECK(dispatched_quantity >= 0 AND dispatched_quantity <= approved_quantity),
 CHECK(received_quantity >= 0 AND loss_quantity >= 0 AND received_quantity + loss_quantity <= dispatched_quantity));
ALTER TABLE inventory_transactions ADD COLUMN IF NOT EXISTS source_transfer_id uuid, ADD COLUMN IF NOT EXISTS command_key text;
ALTER TABLE inventory_lots ADD COLUMN IF NOT EXISTS source_transfer_id uuid, ADD COLUMN IF NOT EXISTS source_lot_id uuid;
DO $$ BEGIN
 IF EXISTS(SELECT 1 FROM pg_constraint WHERE conname='inventory_transactions_type_source_check') THEN ALTER TABLE inventory_transactions DROP CONSTRAINT inventory_transactions_type_source_check; END IF;
 IF NOT EXISTS(SELECT 1 FROM pg_constraint WHERE conname='inventory_transactions_transfer_fk') THEN ALTER TABLE inventory_transactions ADD CONSTRAINT inventory_transactions_transfer_fk FOREIGN KEY(source_transfer_id,tenant_id) REFERENCES inventory_transfers(id,tenant_id); END IF;
 IF NOT EXISTS(SELECT 1 FROM pg_constraint WHERE conname='inventory_transactions_command_uq') THEN ALTER TABLE inventory_transactions ADD CONSTRAINT inventory_transactions_command_uq UNIQUE(tenant_id,command_key); END IF;
 ALTER TABLE inventory_transactions ADD CONSTRAINT inventory_transactions_type_source_check CHECK(
  (transaction_type='supplier_receipt' AND source_receipt_id IS NOT NULL AND source_production_batch_id IS NULL AND source_transfer_id IS NULL) OR
  (transaction_type='production' AND source_receipt_id IS NULL AND source_production_batch_id IS NOT NULL AND source_transfer_id IS NULL) OR
  (transaction_type IN ('transfer_dispatch','transfer_receipt') AND source_receipt_id IS NULL AND source_production_batch_id IS NULL AND source_transfer_id IS NOT NULL));
 IF EXISTS(SELECT 1 FROM pg_constraint WHERE conname='inventory_lots_source_check') THEN ALTER TABLE inventory_lots DROP CONSTRAINT inventory_lots_source_check; END IF;
 IF NOT EXISTS(SELECT 1 FROM pg_constraint WHERE conname='inventory_lots_transfer_fk') THEN ALTER TABLE inventory_lots ADD CONSTRAINT inventory_lots_transfer_fk FOREIGN KEY(source_transfer_id,tenant_id) REFERENCES inventory_transfers(id,tenant_id); END IF;
 IF NOT EXISTS(SELECT 1 FROM pg_constraint WHERE conname='inventory_lots_source_lot_fk') THEN ALTER TABLE inventory_lots ADD CONSTRAINT inventory_lots_source_lot_fk FOREIGN KEY(source_lot_id,tenant_id) REFERENCES inventory_lots(id,tenant_id); END IF;
 ALTER TABLE inventory_lots ADD CONSTRAINT inventory_lots_source_check CHECK(
  (source_receipt_line_id IS NOT NULL AND source_production_batch_id IS NULL AND source_transfer_id IS NULL) OR
  (source_receipt_line_id IS NULL AND source_production_batch_id IS NOT NULL AND source_transfer_id IS NULL) OR
  (source_receipt_line_id IS NULL AND source_production_batch_id IS NULL AND source_transfer_id IS NOT NULL));
END $$;
GRANT SELECT,INSERT,UPDATE ON inventory_transfers,inventory_transfer_lines TO gastroledger_app;
ALTER TABLE inventory_transfers ENABLE ROW LEVEL SECURITY; ALTER TABLE inventory_transfers FORCE ROW LEVEL SECURITY;
ALTER TABLE inventory_transfer_lines ENABLE ROW LEVEL SECURITY; ALTER TABLE inventory_transfer_lines FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS inventory_transfers_scope ON inventory_transfers; CREATE POLICY inventory_transfers_scope ON inventory_transfers USING(tenant_id=nullif(current_setting('app.current_tenant_id',true),'')::uuid) WITH CHECK(tenant_id=nullif(current_setting('app.current_tenant_id',true),'')::uuid);
DROP POLICY IF EXISTS inventory_transfer_lines_scope ON inventory_transfer_lines; CREATE POLICY inventory_transfer_lines_scope ON inventory_transfer_lines USING(tenant_id=nullif(current_setting('app.current_tenant_id',true),'')::uuid) WITH CHECK(tenant_id=nullif(current_setting('app.current_tenant_id',true),'')::uuid);
COMMIT;
