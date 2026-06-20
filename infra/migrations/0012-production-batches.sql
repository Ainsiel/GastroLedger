\set ON_ERROR_STOP on

BEGIN;

CREATE TABLE IF NOT EXISTS inventory_production_batches (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    idempotency_key text NOT NULL,
    batch_number text NOT NULL,
    warehouse_id uuid NOT NULL,
    recipe_version_id uuid NOT NULL,
    expected_yield numeric(24, 10) NOT NULL CHECK (expected_yield > 0),
    actual_yield numeric(24, 10) NOT NULL CHECK (actual_yield > 0),
    variance_quantity numeric(24, 10) NOT NULL,
    variance_reason text,
    output_lot_code text NOT NULL,
    produced_on date NOT NULL,
    status text NOT NULL CHECK (status = 'posted'),
    actor_id uuid NOT NULL REFERENCES platform_users(id),
    correlation_id text NOT NULL,
    posted_at timestamptz NOT NULL,
    UNIQUE (tenant_id, idempotency_key),
    UNIQUE (tenant_id, batch_number),
    UNIQUE (id, tenant_id),
    FOREIGN KEY (warehouse_id, tenant_id) REFERENCES platform_warehouses(id, tenant_id),
    FOREIGN KEY (recipe_version_id, tenant_id) REFERENCES menu_recipe_versions(id, tenant_id)
);

ALTER TABLE inventory_transactions
    DROP CONSTRAINT IF EXISTS inventory_transactions_transaction_type_check,
    DROP CONSTRAINT IF EXISTS inventory_transactions_tenant_id_source_receipt_id_key,
    ALTER COLUMN source_receipt_id DROP NOT NULL,
    ADD COLUMN IF NOT EXISTS source_production_batch_id uuid;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'inventory_transactions_type_source_check') THEN
        ALTER TABLE inventory_transactions ADD CONSTRAINT inventory_transactions_type_source_check CHECK (
            (transaction_type = 'supplier_receipt' AND source_receipt_id IS NOT NULL AND source_production_batch_id IS NULL)
            OR (transaction_type = 'production' AND source_receipt_id IS NULL AND source_production_batch_id IS NOT NULL)
        );
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'inventory_transactions_receipt_uq') THEN
        ALTER TABLE inventory_transactions ADD CONSTRAINT inventory_transactions_receipt_uq UNIQUE (tenant_id, source_receipt_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'inventory_transactions_production_uq') THEN
        ALTER TABLE inventory_transactions ADD CONSTRAINT inventory_transactions_production_uq UNIQUE (tenant_id, source_production_batch_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'inventory_transactions_production_fk') THEN
        ALTER TABLE inventory_transactions ADD CONSTRAINT inventory_transactions_production_fk
            FOREIGN KEY (source_production_batch_id, tenant_id)
            REFERENCES inventory_production_batches(id, tenant_id);
    END IF;
END $$;

ALTER TABLE inventory_lots
    ALTER COLUMN ingredient_id DROP NOT NULL,
    ALTER COLUMN expiry_date DROP NOT NULL,
    ALTER COLUMN source_receipt_line_id DROP NOT NULL,
    ADD COLUMN IF NOT EXISTS prepared_recipe_version_id uuid,
    ADD COLUMN IF NOT EXISTS source_production_batch_id uuid;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'inventory_lots_item_check') THEN
        ALTER TABLE inventory_lots ADD CONSTRAINT inventory_lots_item_check CHECK (
            (ingredient_id IS NOT NULL AND prepared_recipe_version_id IS NULL)
            OR (ingredient_id IS NULL AND prepared_recipe_version_id IS NOT NULL)
        );
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'inventory_lots_source_check') THEN
        ALTER TABLE inventory_lots ADD CONSTRAINT inventory_lots_source_check CHECK (
            (source_receipt_line_id IS NOT NULL AND source_production_batch_id IS NULL)
            OR (source_receipt_line_id IS NULL AND source_production_batch_id IS NOT NULL)
        );
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'inventory_lots_recipe_fk') THEN
        ALTER TABLE inventory_lots ADD CONSTRAINT inventory_lots_recipe_fk
            FOREIGN KEY (prepared_recipe_version_id, tenant_id)
            REFERENCES menu_recipe_versions(id, tenant_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'inventory_lots_production_fk') THEN
        ALTER TABLE inventory_lots ADD CONSTRAINT inventory_lots_production_fk
            FOREIGN KEY (source_production_batch_id, tenant_id)
            REFERENCES inventory_production_batches(id, tenant_id);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS inventory_lots_fefo_idx
ON inventory_lots (tenant_id, warehouse_id, ingredient_id, expiry_date, created_at);

GRANT SELECT, INSERT ON inventory_production_batches TO gastroledger_app;
GRANT UPDATE ON inventory_stock_balances TO gastroledger_app;

ALTER TABLE inventory_production_batches ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_production_batches FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS inventory_production_batches_scope ON inventory_production_batches;
CREATE POLICY inventory_production_batches_scope ON inventory_production_batches
USING (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)
WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid);

COMMIT;
