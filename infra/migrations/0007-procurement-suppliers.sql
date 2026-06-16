\set ON_ERROR_STOP on

BEGIN;

CREATE TABLE IF NOT EXISTS procurement_suppliers (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    code text NOT NULL,
    name text NOT NULL,
    status text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    UNIQUE (tenant_id, code),
    UNIQUE (id, tenant_id)
);

CREATE TABLE IF NOT EXISTS procurement_supplier_offers (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    supplier_id uuid NOT NULL,
    ingredient_id uuid NOT NULL,
    purchase_unit_id uuid NOT NULL,
    price numeric(24, 10) NOT NULL CHECK (price > 0),
    currency text NOT NULL CHECK (currency ~ '^[A-Z]{3}$'),
    effective_from date NOT NULL,
    effective_until date,
    CHECK (effective_until IS NULL OR effective_until >= effective_from),
    CONSTRAINT procurement_offers_supplier_fk
        FOREIGN KEY (supplier_id, tenant_id)
        REFERENCES procurement_suppliers (id, tenant_id),
    CONSTRAINT procurement_offers_ingredient_fk
        FOREIGN KEY (ingredient_id, tenant_id)
        REFERENCES menu_ingredients (id, tenant_id),
    CONSTRAINT procurement_offers_purchase_unit_fk
        FOREIGN KEY (purchase_unit_id, tenant_id)
        REFERENCES menu_units (id, tenant_id)
);

GRANT SELECT, INSERT, UPDATE ON
    procurement_suppliers,
    procurement_supplier_offers
TO gastroledger_app;

ALTER TABLE procurement_suppliers ENABLE ROW LEVEL SECURITY;
ALTER TABLE procurement_suppliers FORCE ROW LEVEL SECURITY;
ALTER TABLE procurement_supplier_offers ENABLE ROW LEVEL SECURITY;
ALTER TABLE procurement_supplier_offers FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS procurement_suppliers_scope ON procurement_suppliers;
CREATE POLICY procurement_suppliers_scope ON procurement_suppliers
USING (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)
WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid);

DROP POLICY IF EXISTS procurement_supplier_offers_scope ON procurement_supplier_offers;
CREATE POLICY procurement_supplier_offers_scope ON procurement_supplier_offers
USING (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)
WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid);

COMMIT;
