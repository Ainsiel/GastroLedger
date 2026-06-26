\set ON_ERROR_STOP on

BEGIN;

CREATE UNIQUE INDEX IF NOT EXISTS platform_warehouses_id_tenant_uq
ON platform_warehouses (id, tenant_id);

CREATE TABLE IF NOT EXISTS procurement_supplier_receipts (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    idempotency_key text NOT NULL,
    order_reference text NOT NULL,
    supplier_id uuid NOT NULL,
    warehouse_id uuid NOT NULL,
    received_on date NOT NULL,
    status text NOT NULL CHECK (status IN ('accepted', 'partial', 'rejected')),
    actor_id uuid NOT NULL REFERENCES platform_users(id),
    correlation_id text NOT NULL,
    accepted_at timestamptz NOT NULL,
    UNIQUE (tenant_id, idempotency_key),
    UNIQUE (id, tenant_id),
    FOREIGN KEY (supplier_id, tenant_id)
        REFERENCES procurement_suppliers (id, tenant_id),
    FOREIGN KEY (warehouse_id, tenant_id)
        REFERENCES platform_warehouses (id, tenant_id)
);

CREATE TABLE IF NOT EXISTS procurement_supplier_receipt_lines (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    receipt_id uuid NOT NULL,
    ingredient_id uuid NOT NULL,
    purchase_unit_id uuid NOT NULL,
    lot_code text NOT NULL,
    ordered_quantity numeric(24, 10) NOT NULL CHECK (ordered_quantity > 0),
    delivered_quantity numeric(24, 10) NOT NULL CHECK (delivered_quantity > 0),
    accepted_quantity numeric(24, 10) NOT NULL CHECK (accepted_quantity >= 0),
    remaining_quantity numeric(24, 10) NOT NULL CHECK (remaining_quantity >= 0),
    unit_cost numeric(24, 10) NOT NULL CHECK (unit_cost > 0),
    expiry_date date NOT NULL,
    temperature numeric(12, 4) NOT NULL,
    status text NOT NULL CHECK (status IN ('accepted', 'partial', 'rejected')),
    rejection_reason text,
    UNIQUE (id, tenant_id),
    FOREIGN KEY (receipt_id, tenant_id)
        REFERENCES procurement_supplier_receipts (id, tenant_id),
    FOREIGN KEY (ingredient_id, tenant_id)
        REFERENCES menu_ingredients (id, tenant_id),
    FOREIGN KEY (purchase_unit_id, tenant_id)
        REFERENCES menu_units (id, tenant_id)
);

CREATE TABLE IF NOT EXISTS inventory_transactions (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    warehouse_id uuid NOT NULL,
    source_receipt_id uuid NOT NULL,
    transaction_type text NOT NULL CHECK (transaction_type = 'supplier_receipt'),
    actor_id uuid NOT NULL REFERENCES platform_users(id),
    correlation_id text NOT NULL,
    occurred_at timestamptz NOT NULL,
    UNIQUE (tenant_id, source_receipt_id),
    UNIQUE (id, tenant_id),
    FOREIGN KEY (warehouse_id, tenant_id)
        REFERENCES platform_warehouses (id, tenant_id),
    FOREIGN KEY (source_receipt_id, tenant_id)
        REFERENCES procurement_supplier_receipts (id, tenant_id)
);

CREATE TABLE IF NOT EXISTS inventory_lots (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    warehouse_id uuid NOT NULL,
    ingredient_id uuid NOT NULL,
    unit_id uuid NOT NULL,
    lot_code text NOT NULL,
    expiry_date date NOT NULL,
    unit_cost numeric(24, 10) NOT NULL CHECK (unit_cost > 0),
    source_receipt_line_id uuid NOT NULL,
    created_at timestamptz NOT NULL,
    UNIQUE (tenant_id, warehouse_id, lot_code),
    UNIQUE (id, tenant_id),
    FOREIGN KEY (warehouse_id, tenant_id)
        REFERENCES platform_warehouses (id, tenant_id),
    FOREIGN KEY (ingredient_id, tenant_id)
        REFERENCES menu_ingredients (id, tenant_id),
    FOREIGN KEY (unit_id, tenant_id)
        REFERENCES menu_units (id, tenant_id),
    FOREIGN KEY (source_receipt_line_id, tenant_id)
        REFERENCES procurement_supplier_receipt_lines (id, tenant_id)
);

CREATE TABLE IF NOT EXISTS inventory_entries (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    transaction_id uuid NOT NULL,
    lot_id uuid NOT NULL,
    quantity numeric(24, 10) NOT NULL CHECK (quantity <> 0),
    unit_cost numeric(24, 10) NOT NULL CHECK (unit_cost > 0),
    UNIQUE (tenant_id, transaction_id, lot_id),
    FOREIGN KEY (transaction_id, tenant_id)
        REFERENCES inventory_transactions (id, tenant_id),
    FOREIGN KEY (lot_id, tenant_id)
        REFERENCES inventory_lots (id, tenant_id)
);

CREATE TABLE IF NOT EXISTS inventory_stock_balances (
    lot_id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    warehouse_id uuid NOT NULL,
    quantity numeric(24, 10) NOT NULL CHECK (quantity >= 0),
    updated_at timestamptz NOT NULL,
    FOREIGN KEY (lot_id, tenant_id)
        REFERENCES inventory_lots (id, tenant_id),
    FOREIGN KEY (warehouse_id, tenant_id)
        REFERENCES platform_warehouses (id, tenant_id)
);

GRANT SELECT, INSERT ON
    procurement_supplier_receipts,
    procurement_supplier_receipt_lines,
    inventory_transactions,
    inventory_lots,
    inventory_entries,
    inventory_stock_balances
TO gastroledger_app;

ALTER TABLE procurement_supplier_receipts ENABLE ROW LEVEL SECURITY;
ALTER TABLE procurement_supplier_receipts FORCE ROW LEVEL SECURITY;
ALTER TABLE procurement_supplier_receipt_lines ENABLE ROW LEVEL SECURITY;
ALTER TABLE procurement_supplier_receipt_lines FORCE ROW LEVEL SECURITY;
ALTER TABLE inventory_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_transactions FORCE ROW LEVEL SECURITY;
ALTER TABLE inventory_lots ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_lots FORCE ROW LEVEL SECURITY;
ALTER TABLE inventory_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_entries FORCE ROW LEVEL SECURITY;
ALTER TABLE inventory_stock_balances ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_stock_balances FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS procurement_supplier_receipts_scope ON procurement_supplier_receipts;
CREATE POLICY procurement_supplier_receipts_scope ON procurement_supplier_receipts
USING (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)
WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid);
DROP POLICY IF EXISTS procurement_supplier_receipt_lines_scope ON procurement_supplier_receipt_lines;
CREATE POLICY procurement_supplier_receipt_lines_scope ON procurement_supplier_receipt_lines
USING (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)
WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid);
DROP POLICY IF EXISTS inventory_transactions_scope ON inventory_transactions;
CREATE POLICY inventory_transactions_scope ON inventory_transactions
USING (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)
WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid);
DROP POLICY IF EXISTS inventory_lots_scope ON inventory_lots;
CREATE POLICY inventory_lots_scope ON inventory_lots
USING (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)
WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid);
DROP POLICY IF EXISTS inventory_entries_scope ON inventory_entries;
CREATE POLICY inventory_entries_scope ON inventory_entries
USING (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)
WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid);
DROP POLICY IF EXISTS inventory_stock_balances_scope ON inventory_stock_balances;
CREATE POLICY inventory_stock_balances_scope ON inventory_stock_balances
USING (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)
WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid);

COMMIT;
