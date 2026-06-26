\set ON_ERROR_STOP on

\if :{?seed_environment}
\else
\set seed_environment develop
\endif

\if :{?seed_tenant_slug}
\else
\set seed_tenant_slug gastroledger-admin
\endif

\if :{?seed_tenant_name}
\else
\set seed_tenant_name GastroLedger Admin Tenant
\endif

\if :{?seed_admin_email}
\else
\set seed_admin_email admin@gastroledger.local
\endif

\if :{?seed_admin_password_hash}
\else
\set seed_admin_password_hash scrypt$Z2FzdHJvbGVkZ2VyLXNlZWQ=$5b8sBNT5rWQopwkLNexIIDCv_2jLGp5bmoh4vH_JsXLJ9nNh_3WyweljI5jTxvpOw2V8ghJt0VNpiEZX0f8SCw==
\endif

\set tenant_id 00000000-0000-4000-8000-000000000001
\set admin_user_id 00000000-0000-4000-8000-000000000002
\set manager_user_id 00000000-0000-4000-8000-000000000003
\set invitation_id 00000000-0000-4000-8000-000000000004
\set admin_role_id 00000000-0000-4000-8000-000000000005
\set manager_role_id 00000000-0000-4000-8000-000000000006
\set main_branch_id 00000000-0000-4000-8000-000000000101
\set outlet_branch_id 00000000-0000-4000-8000-000000000102
\set main_kitchen_id 00000000-0000-4000-8000-000000000201
\set dry_storage_id 00000000-0000-4000-8000-000000000202
\set outlet_kitchen_id 00000000-0000-4000-8000-000000000203
\set kg_unit_id 00000000-0000-4000-8000-000000000301
\set gram_unit_id 00000000-0000-4000-8000-000000000302
\set liter_unit_id 00000000-0000-4000-8000-000000000303
\set ml_unit_id 00000000-0000-4000-8000-000000000304
\set each_unit_id 00000000-0000-4000-8000-000000000305
\set kg_to_g_id 00000000-0000-4000-8000-000000000311
\set g_to_kg_id 00000000-0000-4000-8000-000000000312
\set l_to_ml_id 00000000-0000-4000-8000-000000000313
\set ml_to_l_id 00000000-0000-4000-8000-000000000314
\set tomato_id 00000000-0000-4000-8000-000000000401
\set basil_id 00000000-0000-4000-8000-000000000402
\set mozzarella_id 00000000-0000-4000-8000-000000000403
\set archived_chili_id 00000000-0000-4000-8000-000000000404
\set supplier_farm_id 00000000-0000-4000-8000-000000000501
\set supplier_dairy_id 00000000-0000-4000-8000-000000000502
\set tomato_offer_id 00000000-0000-4000-8000-000000000511
\set basil_offer_id 00000000-0000-4000-8000-000000000512
\set mozzarella_offer_id 00000000-0000-4000-8000-000000000513
\set sauce_recipe_id 00000000-0000-4000-8000-000000000601
\set pizza_recipe_id 00000000-0000-4000-8000-000000000602
\set sauce_version_id 00000000-0000-4000-8000-000000000611
\set pizza_version_id 00000000-0000-4000-8000-000000000612
\set pizza_future_version_id 00000000-0000-4000-8000-000000000613
\set sauce_tomato_component_id 00000000-0000-4000-8000-000000000621
\set sauce_basil_component_id 00000000-0000-4000-8000-000000000622
\set pizza_sauce_component_id 00000000-0000-4000-8000-000000000623
\set pizza_mozz_component_id 00000000-0000-4000-8000-000000000624
\set future_pizza_sauce_component_id 00000000-0000-4000-8000-000000000625
\set future_pizza_mozz_component_id 00000000-0000-4000-8000-000000000626
\set sauce_cost_snapshot_id 00000000-0000-4000-8000-000000000631
\set pizza_cost_snapshot_id 00000000-0000-4000-8000-000000000632
\set pizza_future_cost_snapshot_id 00000000-0000-4000-8000-000000000633
\set main_price_id 00000000-0000-4000-8000-000000000641
\set outlet_price_id 00000000-0000-4000-8000-000000000642
\set receipt_id 00000000-0000-4000-8000-000000000701
\set tomato_receipt_line_id 00000000-0000-4000-8000-000000000711
\set basil_receipt_line_id 00000000-0000-4000-8000-000000000712
\set mozzarella_receipt_line_id 00000000-0000-4000-8000-000000000713
\set receipt_tx_id 00000000-0000-4000-8000-000000000721
\set tomato_lot_id 00000000-0000-4000-8000-000000000731
\set basil_lot_id 00000000-0000-4000-8000-000000000732
\set mozzarella_lot_id 00000000-0000-4000-8000-000000000733
\set tomato_receipt_entry_id 00000000-0000-4000-8000-000000000741
\set basil_receipt_entry_id 00000000-0000-4000-8000-000000000742
\set mozzarella_receipt_entry_id 00000000-0000-4000-8000-000000000743
\set production_batch_id 00000000-0000-4000-8000-000000000801
\set production_tx_id 00000000-0000-4000-8000-000000000802
\set sauce_lot_id 00000000-0000-4000-8000-000000000803
\set production_tomato_entry_id 00000000-0000-4000-8000-000000000811
\set production_basil_entry_id 00000000-0000-4000-8000-000000000812
\set production_output_entry_id 00000000-0000-4000-8000-000000000813
\set transfer_id 00000000-0000-4000-8000-000000000901
\set transfer_line_id 00000000-0000-4000-8000-000000000902
\set transfer_dispatch_tx_id 00000000-0000-4000-8000-000000000903
\set transfer_receive_tx_id 00000000-0000-4000-8000-000000000904
\set outlet_tomato_lot_id 00000000-0000-4000-8000-000000000905
\set transfer_dispatch_entry_id 00000000-0000-4000-8000-000000000911
\set transfer_receive_entry_id 00000000-0000-4000-8000-000000000912
\set waste_posted_id 00000000-0000-4000-8000-000000000a01
\set waste_corrected_id 00000000-0000-4000-8000-000000000a02
\set waste_rejected_id 00000000-0000-4000-8000-000000000a03
\set waste_pending_id 00000000-0000-4000-8000-000000000a04
\set waste_posted_tx_id 00000000-0000-4000-8000-000000000a11
\set waste_corrected_tx_id 00000000-0000-4000-8000-000000000a12
\set waste_correction_tx_id 00000000-0000-4000-8000-000000000a13
\set waste_posted_entry_id 00000000-0000-4000-8000-000000000a21
\set waste_corrected_entry_id 00000000-0000-4000-8000-000000000a22
\set waste_correction_entry_id 00000000-0000-4000-8000-000000000a23
\set expiry_alert_id 00000000-0000-4000-8000-000000000b01
\set expiry_notification_id 00000000-0000-4000-8000-000000000b02
\set acknowledged_alert_id 00000000-0000-4000-8000-000000000b03
\set acknowledged_notification_id 00000000-0000-4000-8000-000000000b04
\set cost_job_id 00000000-0000-4000-8000-000000000c01
\set expiry_job_id 00000000-0000-4000-8000-000000000c02
\set offer_outbox_id 00000000-0000-4000-8000-000000000c11
\set receipt_outbox_id 00000000-0000-4000-8000-000000000c12
\set production_outbox_id 00000000-0000-4000-8000-000000000c13
\set sauce_projection_snapshot_id 00000000-0000-4000-8000-000000000c21
\set pizza_projection_snapshot_id 00000000-0000-4000-8000-000000000c22

BEGIN;

SET LOCAL row_security = off;

INSERT INTO platform_tenants (id, slug, name, status, created_at)
VALUES (:'tenant_id'::uuid, :'seed_tenant_slug', :'seed_tenant_name', 'active', '2026-06-26 12:00:00+00')
ON CONFLICT (id) DO NOTHING;

INSERT INTO platform_tenant_settings (tenant_id, locale, base_currency, branch_limit)
VALUES (:'tenant_id'::uuid, 'es-CL', 'CLP', 5)
ON CONFLICT (tenant_id) DO NOTHING;

INSERT INTO platform_users (id, normalized_login, password_hash, created_at)
VALUES
    (:'admin_user_id'::uuid, lower(:'seed_admin_email'), :'seed_admin_password_hash', '2026-06-26 12:00:00+00'),
    (:'manager_user_id'::uuid, 'manager.seed@gastroledger.local', 'seeded-nonlogin-disabled', '2026-06-26 12:05:00+00')
ON CONFLICT (id) DO UPDATE
SET password_hash = CASE
        WHEN platform_users.id = :'admin_user_id'::uuid THEN EXCLUDED.password_hash
        ELSE platform_users.password_hash
    END;

INSERT INTO platform_memberships (tenant_id, user_id, role)
VALUES
    (:'tenant_id'::uuid, :'admin_user_id'::uuid, 'tenant_admin'),
    (:'tenant_id'::uuid, :'manager_user_id'::uuid, 'branch_manager')
ON CONFLICT (tenant_id, user_id) DO NOTHING;

INSERT INTO platform_branches (id, tenant_id, code, name)
VALUES
    (:'main_branch_id'::uuid, :'tenant_id'::uuid, 'MAIN', 'Casa Matriz'),
    (:'outlet_branch_id'::uuid, :'tenant_id'::uuid, 'OUTLET', 'Sucursal Providencia')
ON CONFLICT (id) DO NOTHING;

INSERT INTO platform_membership_roles (id, tenant_id, user_id, role, scope, branch_id)
VALUES
    (:'admin_role_id'::uuid, :'tenant_id'::uuid, :'admin_user_id'::uuid, 'tenant_admin', 'tenant', NULL),
    (:'manager_role_id'::uuid, :'tenant_id'::uuid, :'manager_user_id'::uuid, 'branch_manager', 'branch', :'main_branch_id'::uuid)
ON CONFLICT (id) DO NOTHING;

INSERT INTO platform_invitations (
    id, tenant_id, invitee_login, token_hash, role, scope, branch_id,
    created_by, expires_at, accepted_at, created_at
)
VALUES (
    :'invitation_id'::uuid,
    :'tenant_id'::uuid,
    'ops.invited@gastroledger.local',
    'f6be6155b73a83b9863a1c2c8d359d487fbd6edcfe3d8967b1e62d2f8e2fb0ef',
    'branch_operator',
    'branch',
    :'outlet_branch_id'::uuid,
    :'admin_user_id'::uuid,
    '2026-07-26 12:00:00+00',
    NULL,
    '2026-06-26 12:10:00+00'
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO platform_warehouses (id, tenant_id, branch_id, code, name, type, status)
VALUES
    (:'main_kitchen_id'::uuid, :'tenant_id'::uuid, :'main_branch_id'::uuid, 'MAIN-KITCHEN', 'Cocina principal', 'kitchen', 'active'),
    (:'dry_storage_id'::uuid, :'tenant_id'::uuid, :'main_branch_id'::uuid, 'MAIN-DRY', 'Bodega seca', 'general', 'active'),
    (:'outlet_kitchen_id'::uuid, :'tenant_id'::uuid, :'outlet_branch_id'::uuid, 'OUTLET-KITCHEN', 'Cocina Providencia', 'kitchen', 'active')
ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_units (id, tenant_id, code, name, dimension)
VALUES
    (:'kg_unit_id'::uuid, :'tenant_id'::uuid, 'kg', 'Kilogramo', 'mass'),
    (:'gram_unit_id'::uuid, :'tenant_id'::uuid, 'g', 'Gramo', 'mass'),
    (:'liter_unit_id'::uuid, :'tenant_id'::uuid, 'l', 'Litro', 'volume'),
    (:'ml_unit_id'::uuid, :'tenant_id'::uuid, 'ml', 'Mililitro', 'volume'),
    (:'each_unit_id'::uuid, :'tenant_id'::uuid, 'ea', 'Unidad', 'count')
ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_conversion_factors (id, tenant_id, source_unit_id, target_unit_id, factor, effective_from)
VALUES
    (:'kg_to_g_id'::uuid, :'tenant_id'::uuid, :'kg_unit_id'::uuid, :'gram_unit_id'::uuid, 1000, '2026-01-01'),
    (:'g_to_kg_id'::uuid, :'tenant_id'::uuid, :'gram_unit_id'::uuid, :'kg_unit_id'::uuid, 0.001, '2026-01-01'),
    (:'l_to_ml_id'::uuid, :'tenant_id'::uuid, :'liter_unit_id'::uuid, :'ml_unit_id'::uuid, 1000, '2026-01-01'),
    (:'ml_to_l_id'::uuid, :'tenant_id'::uuid, :'ml_unit_id'::uuid, :'liter_unit_id'::uuid, 0.001, '2026-01-01')
ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_ingredients (
    id, tenant_id, code, name, purchase_unit_id, consumption_unit_id,
    shelf_life_days, critical_stock_quantity, status
)
VALUES
    (:'tomato_id'::uuid, :'tenant_id'::uuid, 'TOMATO', 'Tomate pera', :'kg_unit_id'::uuid, :'kg_unit_id'::uuid, 7, 3, 'active'),
    (:'basil_id'::uuid, :'tenant_id'::uuid, 'BASIL', 'Albahaca fresca', :'kg_unit_id'::uuid, :'kg_unit_id'::uuid, 5, 0.5, 'active'),
    (:'mozzarella_id'::uuid, :'tenant_id'::uuid, 'MOZZ', 'Mozzarella fior di latte', :'kg_unit_id'::uuid, :'kg_unit_id'::uuid, 12, 2, 'active'),
    (:'archived_chili_id'::uuid, :'tenant_id'::uuid, 'CHILI-OLD', 'Ají descontinuado', :'kg_unit_id'::uuid, :'kg_unit_id'::uuid, 20, 1, 'archived')
ON CONFLICT (id) DO NOTHING;

INSERT INTO procurement_suppliers (id, tenant_id, code, name, status)
VALUES
    (:'supplier_farm_id'::uuid, :'tenant_id'::uuid, 'FARM-LOCAL', 'Huerto Local', 'active'),
    (:'supplier_dairy_id'::uuid, :'tenant_id'::uuid, 'DAIRY-ANDES', 'Lacteos Andes', 'active')
ON CONFLICT (id) DO NOTHING;

INSERT INTO procurement_supplier_offers (
    id, tenant_id, supplier_id, ingredient_id, purchase_unit_id,
    price, currency, effective_from, effective_until
)
VALUES
    (:'tomato_offer_id'::uuid, :'tenant_id'::uuid, :'supplier_farm_id'::uuid, :'tomato_id'::uuid, :'kg_unit_id'::uuid, 2200, 'CLP', '2026-06-01', NULL),
    (:'basil_offer_id'::uuid, :'tenant_id'::uuid, :'supplier_farm_id'::uuid, :'basil_id'::uuid, :'kg_unit_id'::uuid, 12000, 'CLP', '2026-06-01', NULL),
    (:'mozzarella_offer_id'::uuid, :'tenant_id'::uuid, :'supplier_dairy_id'::uuid, :'mozzarella_id'::uuid, :'kg_unit_id'::uuid, 8000, 'CLP', '2026-06-01', NULL)
ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_recipes (id, tenant_id, code, name, recipe_type)
VALUES
    (:'sauce_recipe_id'::uuid, :'tenant_id'::uuid, 'SALSA-POMODORO', 'Salsa pomodoro base', 'sub_recipe'),
    (:'pizza_recipe_id'::uuid, :'tenant_id'::uuid, 'PIZZA-MARGHERITA', 'Pizza Margherita', 'menu_item')
ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_recipe_versions (
    id, tenant_id, recipe_id, version, yield_quantity, yield_unit_id,
    effective_from, status, approved_at
)
VALUES
    (:'sauce_version_id'::uuid, :'tenant_id'::uuid, :'sauce_recipe_id'::uuid, 'v1', 4, :'kg_unit_id'::uuid, '2026-06-01', 'approved', '2026-06-01 09:00:00+00'),
    (:'pizza_version_id'::uuid, :'tenant_id'::uuid, :'pizza_recipe_id'::uuid, 'v1', 1, :'each_unit_id'::uuid, '2026-06-01', 'approved', '2026-06-01 09:15:00+00'),
    (:'pizza_future_version_id'::uuid, :'tenant_id'::uuid, :'pizza_recipe_id'::uuid, 'v2', 1, :'each_unit_id'::uuid, '2026-08-01', 'scheduled', '2026-06-26 12:15:00+00')
ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_recipe_components (
    id, tenant_id, recipe_version_id, component_type, ingredient_id,
    component_recipe_id, quantity, unit_id
)
VALUES
    (:'sauce_tomato_component_id'::uuid, :'tenant_id'::uuid, :'sauce_version_id'::uuid, 'ingredient', :'tomato_id'::uuid, NULL, 3.8, :'kg_unit_id'::uuid),
    (:'sauce_basil_component_id'::uuid, :'tenant_id'::uuid, :'sauce_version_id'::uuid, 'ingredient', :'basil_id'::uuid, NULL, 0.2, :'kg_unit_id'::uuid),
    (:'pizza_sauce_component_id'::uuid, :'tenant_id'::uuid, :'pizza_version_id'::uuid, 'sub_recipe', NULL, :'sauce_recipe_id'::uuid, 0.25, :'kg_unit_id'::uuid),
    (:'pizza_mozz_component_id'::uuid, :'tenant_id'::uuid, :'pizza_version_id'::uuid, 'ingredient', :'mozzarella_id'::uuid, NULL, 0.18, :'kg_unit_id'::uuid),
    (:'future_pizza_sauce_component_id'::uuid, :'tenant_id'::uuid, :'pizza_future_version_id'::uuid, 'sub_recipe', NULL, :'sauce_recipe_id'::uuid, 0.3, :'kg_unit_id'::uuid),
    (:'future_pizza_mozz_component_id'::uuid, :'tenant_id'::uuid, :'pizza_future_version_id'::uuid, 'ingredient', :'mozzarella_id'::uuid, NULL, 0.2, :'kg_unit_id'::uuid)
ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_cost_snapshots (id, tenant_id, recipe_version_id, as_of, total_cost, status)
VALUES
    (:'sauce_cost_snapshot_id'::uuid, :'tenant_id'::uuid, :'sauce_version_id'::uuid, '2026-06-01', 10760, 'current'),
    (:'pizza_cost_snapshot_id'::uuid, :'tenant_id'::uuid, :'pizza_version_id'::uuid, '2026-06-01', 2114, 'current'),
    (:'pizza_future_cost_snapshot_id'::uuid, :'tenant_id'::uuid, :'pizza_future_version_id'::uuid, '2026-08-01', 2407, 'current')
ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_item_branch_prices (
    id, tenant_id, recipe_version_id, branch_id, price, currency, effective_from
)
VALUES
    (:'main_price_id'::uuid, :'tenant_id'::uuid, :'pizza_version_id'::uuid, :'main_branch_id'::uuid, 8900, 'CLP', '2026-06-01'),
    (:'outlet_price_id'::uuid, :'tenant_id'::uuid, :'pizza_version_id'::uuid, :'outlet_branch_id'::uuid, 9400, 'CLP', '2026-06-01')
ON CONFLICT (id) DO NOTHING;

INSERT INTO procurement_supplier_receipts (
    id, tenant_id, idempotency_key, order_reference, supplier_id, warehouse_id,
    received_on, status, actor_id, correlation_id, accepted_at
)
VALUES (
    :'receipt_id'::uuid,
    :'tenant_id'::uuid,
    'seed-receipt-2026-06-20',
    'PO-SEED-0001',
    :'supplier_farm_id'::uuid,
    :'main_kitchen_id'::uuid,
    '2026-06-20',
    'accepted',
    :'admin_user_id'::uuid,
    'seed:procurement:receipt',
    '2026-06-20 10:00:00+00'
)
ON CONFLICT (tenant_id, idempotency_key) DO NOTHING;

INSERT INTO procurement_supplier_receipt_lines (
    id, tenant_id, receipt_id, ingredient_id, purchase_unit_id, lot_code,
    ordered_quantity, delivered_quantity, accepted_quantity, remaining_quantity,
    unit_cost, expiry_date, temperature, status, rejection_reason
)
VALUES
    (:'tomato_receipt_line_id'::uuid, :'tenant_id'::uuid, :'receipt_id'::uuid, :'tomato_id'::uuid, :'kg_unit_id'::uuid, 'LOT-TOM-2026-06-28', 12, 12, 12, 0, 2200, '2026-06-28', 4, 'accepted', NULL),
    (:'basil_receipt_line_id'::uuid, :'tenant_id'::uuid, :'receipt_id'::uuid, :'basil_id'::uuid, :'kg_unit_id'::uuid, 'LOT-BASIL-2026-07-10', 1, 1, 1, 0, 12000, '2026-07-10', 4, 'accepted', NULL),
    (:'mozzarella_receipt_line_id'::uuid, :'tenant_id'::uuid, :'receipt_id'::uuid, :'mozzarella_id'::uuid, :'kg_unit_id'::uuid, 'LOT-MOZZ-2026-07-04', 8, 8, 8, 0, 8000, '2026-07-04', 3, 'accepted', NULL)
ON CONFLICT (id) DO NOTHING;

INSERT INTO inventory_transactions (
    id, tenant_id, warehouse_id, source_receipt_id, source_production_batch_id,
    source_transfer_id, command_key, source_waste_id, transaction_type,
    actor_id, correlation_id, occurred_at
)
VALUES (
    :'receipt_tx_id'::uuid,
    :'tenant_id'::uuid,
    :'main_kitchen_id'::uuid,
    :'receipt_id'::uuid,
    NULL,
    NULL,
    NULL,
    NULL,
    'supplier_receipt',
    :'admin_user_id'::uuid,
    'seed:procurement:receipt',
    '2026-06-20 10:05:00+00'
)
ON CONFLICT (tenant_id, source_receipt_id) DO NOTHING;

INSERT INTO inventory_lots (
    id, tenant_id, warehouse_id, ingredient_id, prepared_recipe_version_id,
    unit_id, lot_code, expiry_date, unit_cost, source_receipt_line_id,
    source_production_batch_id, source_transfer_id, source_lot_id, created_at
)
VALUES
    (:'tomato_lot_id'::uuid, :'tenant_id'::uuid, :'main_kitchen_id'::uuid, :'tomato_id'::uuid, NULL, :'kg_unit_id'::uuid, 'LOT-TOM-2026-06-28', '2026-06-28', 2200, :'tomato_receipt_line_id'::uuid, NULL, NULL, NULL, '2026-06-20 10:06:00+00'),
    (:'basil_lot_id'::uuid, :'tenant_id'::uuid, :'main_kitchen_id'::uuid, :'basil_id'::uuid, NULL, :'kg_unit_id'::uuid, 'LOT-BASIL-2026-07-10', '2026-07-10', 12000, :'basil_receipt_line_id'::uuid, NULL, NULL, NULL, '2026-06-20 10:06:00+00'),
    (:'mozzarella_lot_id'::uuid, :'tenant_id'::uuid, :'main_kitchen_id'::uuid, :'mozzarella_id'::uuid, NULL, :'kg_unit_id'::uuid, 'LOT-MOZZ-2026-07-04', '2026-07-04', 8000, :'mozzarella_receipt_line_id'::uuid, NULL, NULL, NULL, '2026-06-20 10:06:00+00')
ON CONFLICT (tenant_id, warehouse_id, lot_code) DO NOTHING;

INSERT INTO inventory_entries (id, tenant_id, transaction_id, lot_id, quantity, unit_cost)
VALUES
    (:'tomato_receipt_entry_id'::uuid, :'tenant_id'::uuid, :'receipt_tx_id'::uuid, :'tomato_lot_id'::uuid, 12, 2200),
    (:'basil_receipt_entry_id'::uuid, :'tenant_id'::uuid, :'receipt_tx_id'::uuid, :'basil_lot_id'::uuid, 1, 12000),
    (:'mozzarella_receipt_entry_id'::uuid, :'tenant_id'::uuid, :'receipt_tx_id'::uuid, :'mozzarella_lot_id'::uuid, 8, 8000)
ON CONFLICT (tenant_id, transaction_id, lot_id) DO NOTHING;

INSERT INTO inventory_production_batches (
    id, tenant_id, idempotency_key, batch_number, warehouse_id, recipe_version_id,
    expected_yield, actual_yield, variance_quantity, variance_reason, output_lot_code,
    produced_on, status, actor_id, correlation_id, posted_at
)
VALUES (
    :'production_batch_id'::uuid,
    :'tenant_id'::uuid,
    'seed-production-2026-06-21',
    'BATCH-SEED-001',
    :'main_kitchen_id'::uuid,
    :'sauce_version_id'::uuid,
    4,
    3.8,
    -0.2,
    'evaporation and trim loss',
    'SAUCE-SEED-001',
    '2026-06-21',
    'posted',
    :'admin_user_id'::uuid,
    'seed:inventory:production',
    '2026-06-21 08:00:00+00'
)
ON CONFLICT (tenant_id, idempotency_key) DO NOTHING;

INSERT INTO inventory_transactions (
    id, tenant_id, warehouse_id, source_receipt_id, source_production_batch_id,
    source_transfer_id, command_key, source_waste_id, transaction_type,
    actor_id, correlation_id, occurred_at
)
VALUES (
    :'production_tx_id'::uuid,
    :'tenant_id'::uuid,
    :'main_kitchen_id'::uuid,
    NULL,
    :'production_batch_id'::uuid,
    NULL,
    NULL,
    NULL,
    'production',
    :'admin_user_id'::uuid,
    'seed:inventory:production',
    '2026-06-21 08:05:00+00'
)
ON CONFLICT (tenant_id, source_production_batch_id) DO NOTHING;

INSERT INTO inventory_lots (
    id, tenant_id, warehouse_id, ingredient_id, prepared_recipe_version_id,
    unit_id, lot_code, expiry_date, unit_cost, source_receipt_line_id,
    source_production_batch_id, source_transfer_id, source_lot_id, created_at
)
VALUES (
    :'sauce_lot_id'::uuid,
    :'tenant_id'::uuid,
    :'main_kitchen_id'::uuid,
    NULL,
    :'sauce_version_id'::uuid,
    :'kg_unit_id'::uuid,
    'SAUCE-SEED-001',
    NULL,
    2831.5789473684,
    NULL,
    :'production_batch_id'::uuid,
    NULL,
    NULL,
    '2026-06-21 08:06:00+00'
)
ON CONFLICT (tenant_id, warehouse_id, lot_code) DO NOTHING;

INSERT INTO inventory_entries (id, tenant_id, transaction_id, lot_id, quantity, unit_cost)
VALUES
    (:'production_tomato_entry_id'::uuid, :'tenant_id'::uuid, :'production_tx_id'::uuid, :'tomato_lot_id'::uuid, -3.8, 2200),
    (:'production_basil_entry_id'::uuid, :'tenant_id'::uuid, :'production_tx_id'::uuid, :'basil_lot_id'::uuid, -0.2, 12000),
    (:'production_output_entry_id'::uuid, :'tenant_id'::uuid, :'production_tx_id'::uuid, :'sauce_lot_id'::uuid, 3.8, 2831.5789473684)
ON CONFLICT (tenant_id, transaction_id, lot_id) DO NOTHING;

INSERT INTO inventory_transfers (
    id, tenant_id, transfer_number, source_warehouse_id, destination_warehouse_id,
    status, requested_by, approved_by, correlation_id, created_at, updated_at
)
VALUES (
    :'transfer_id'::uuid,
    :'tenant_id'::uuid,
    'TR-SEED-001',
    :'main_kitchen_id'::uuid,
    :'outlet_kitchen_id'::uuid,
    'completed',
    :'admin_user_id'::uuid,
    :'manager_user_id'::uuid,
    'seed:inventory:transfer',
    '2026-06-22 09:00:00+00',
    '2026-06-22 10:00:00+00'
)
ON CONFLICT (tenant_id, transfer_number) DO NOTHING;

INSERT INTO inventory_transfer_lines (
    id, tenant_id, transfer_id, item_type, item_id, unit_id,
    requested_quantity, approved_quantity, dispatched_quantity,
    received_quantity, loss_quantity, loss_reason
)
VALUES (
    :'transfer_line_id'::uuid,
    :'tenant_id'::uuid,
    :'transfer_id'::uuid,
    'ingredient',
    :'tomato_id'::uuid,
    :'kg_unit_id'::uuid,
    2,
    2,
    2,
    1.8,
    0.2,
    'damaged in transit'
)
ON CONFLICT (transfer_id) DO NOTHING;

INSERT INTO inventory_transactions (
    id, tenant_id, warehouse_id, source_receipt_id, source_production_batch_id,
    source_transfer_id, command_key, source_waste_id, transaction_type,
    actor_id, correlation_id, occurred_at
)
VALUES
    (:'transfer_dispatch_tx_id'::uuid, :'tenant_id'::uuid, :'main_kitchen_id'::uuid, NULL, NULL, :'transfer_id'::uuid, 'seed-transfer-dispatch', NULL, 'transfer_dispatch', :'admin_user_id'::uuid, 'seed:inventory:transfer:dispatch', '2026-06-22 09:30:00+00'),
    (:'transfer_receive_tx_id'::uuid, :'tenant_id'::uuid, :'outlet_kitchen_id'::uuid, NULL, NULL, :'transfer_id'::uuid, 'seed-transfer-receive', NULL, 'transfer_receipt', :'manager_user_id'::uuid, 'seed:inventory:transfer:receive', '2026-06-22 10:00:00+00')
ON CONFLICT (tenant_id, command_key) DO NOTHING;

INSERT INTO inventory_lots (
    id, tenant_id, warehouse_id, ingredient_id, prepared_recipe_version_id,
    unit_id, lot_code, expiry_date, unit_cost, source_receipt_line_id,
    source_production_batch_id, source_transfer_id, source_lot_id, created_at
)
VALUES (
    :'outlet_tomato_lot_id'::uuid,
    :'tenant_id'::uuid,
    :'outlet_kitchen_id'::uuid,
    :'tomato_id'::uuid,
    NULL,
    :'kg_unit_id'::uuid,
    'TR-SEED-001-LOT-TOM-2026-06-28',
    '2026-06-28',
    2200,
    NULL,
    NULL,
    :'transfer_id'::uuid,
    :'tomato_lot_id'::uuid,
    '2026-06-22 10:01:00+00'
)
ON CONFLICT (tenant_id, warehouse_id, lot_code) DO NOTHING;

INSERT INTO inventory_entries (id, tenant_id, transaction_id, lot_id, quantity, unit_cost)
VALUES
    (:'transfer_dispatch_entry_id'::uuid, :'tenant_id'::uuid, :'transfer_dispatch_tx_id'::uuid, :'tomato_lot_id'::uuid, -2, 2200),
    (:'transfer_receive_entry_id'::uuid, :'tenant_id'::uuid, :'transfer_receive_tx_id'::uuid, :'outlet_tomato_lot_id'::uuid, 1.8, 2200)
ON CONFLICT (tenant_id, transaction_id, lot_id) DO NOTHING;

INSERT INTO inventory_waste_records (
    id, tenant_id, command_key, warehouse_id, lot_id, quantity, unit_cost, reason,
    status, requested_by, decision_by, decision_reason, correlation_id, created_at, updated_at
)
VALUES
    (:'waste_posted_id'::uuid, :'tenant_id'::uuid, 'seed-waste-posted', :'outlet_kitchen_id'::uuid, :'outlet_tomato_lot_id'::uuid, 0.25, 2200, 'prep trim', 'posted', :'manager_user_id'::uuid, NULL, NULL, 'seed:inventory:waste:posted', '2026-06-23 11:00:00+00', '2026-06-23 11:00:00+00'),
    (:'waste_corrected_id'::uuid, :'tenant_id'::uuid, 'seed-waste-corrected', :'main_kitchen_id'::uuid, :'sauce_lot_id'::uuid, 0.1, 2831.5789473684, 'counting error', 'corrected', :'admin_user_id'::uuid, :'manager_user_id'::uuid, 'entered in error', 'seed:inventory:waste:corrected', '2026-06-23 12:00:00+00', '2026-06-23 12:30:00+00'),
    (:'waste_rejected_id'::uuid, :'tenant_id'::uuid, 'seed-waste-rejected', :'main_kitchen_id'::uuid, :'sauce_lot_id'::uuid, 0.2, 2831.5789473684, 'quality review', 'rejected', :'admin_user_id'::uuid, :'manager_user_id'::uuid, 'not operational waste', 'seed:inventory:waste:rejected', '2026-06-23 13:00:00+00', '2026-06-23 13:30:00+00'),
    (:'waste_pending_id'::uuid, :'tenant_id'::uuid, 'seed-waste-pending', :'main_kitchen_id'::uuid, :'mozzarella_lot_id'::uuid, 0.02, 8000, 'manager review pending', 'pending_approval', :'admin_user_id'::uuid, NULL, NULL, 'seed:inventory:waste:pending', '2026-06-23 14:00:00+00', '2026-06-23 14:00:00+00')
ON CONFLICT (tenant_id, command_key) DO NOTHING;

INSERT INTO inventory_transactions (
    id, tenant_id, warehouse_id, source_receipt_id, source_production_batch_id,
    source_transfer_id, command_key, source_waste_id, transaction_type,
    actor_id, correlation_id, occurred_at
)
VALUES
    (:'waste_posted_tx_id'::uuid, :'tenant_id'::uuid, :'outlet_kitchen_id'::uuid, NULL, NULL, NULL, 'seed-waste-posted-tx', :'waste_posted_id'::uuid, 'waste', :'manager_user_id'::uuid, 'seed:inventory:waste:posted', '2026-06-23 11:01:00+00'),
    (:'waste_corrected_tx_id'::uuid, :'tenant_id'::uuid, :'main_kitchen_id'::uuid, NULL, NULL, NULL, 'seed-waste-corrected-tx', :'waste_corrected_id'::uuid, 'waste', :'admin_user_id'::uuid, 'seed:inventory:waste:corrected', '2026-06-23 12:01:00+00'),
    (:'waste_correction_tx_id'::uuid, :'tenant_id'::uuid, :'main_kitchen_id'::uuid, NULL, NULL, NULL, 'seed-waste-correction-tx', :'waste_corrected_id'::uuid, 'waste_correction', :'manager_user_id'::uuid, 'seed:inventory:waste:correction', '2026-06-23 12:30:00+00')
ON CONFLICT (tenant_id, command_key) DO NOTHING;

INSERT INTO inventory_entries (id, tenant_id, transaction_id, lot_id, quantity, unit_cost)
VALUES
    (:'waste_posted_entry_id'::uuid, :'tenant_id'::uuid, :'waste_posted_tx_id'::uuid, :'outlet_tomato_lot_id'::uuid, -0.25, 2200),
    (:'waste_corrected_entry_id'::uuid, :'tenant_id'::uuid, :'waste_corrected_tx_id'::uuid, :'sauce_lot_id'::uuid, -0.1, 2831.5789473684),
    (:'waste_correction_entry_id'::uuid, :'tenant_id'::uuid, :'waste_correction_tx_id'::uuid, :'sauce_lot_id'::uuid, 0.1, 2831.5789473684)
ON CONFLICT (tenant_id, transaction_id, lot_id) DO NOTHING;

INSERT INTO inventory_stock_balances (lot_id, tenant_id, warehouse_id, quantity, updated_at)
VALUES
    (:'tomato_lot_id'::uuid, :'tenant_id'::uuid, :'main_kitchen_id'::uuid, 6.2, '2026-06-23 12:30:00+00'),
    (:'basil_lot_id'::uuid, :'tenant_id'::uuid, :'main_kitchen_id'::uuid, 0.8, '2026-06-21 08:05:00+00'),
    (:'mozzarella_lot_id'::uuid, :'tenant_id'::uuid, :'main_kitchen_id'::uuid, 8, '2026-06-20 10:06:00+00'),
    (:'sauce_lot_id'::uuid, :'tenant_id'::uuid, :'main_kitchen_id'::uuid, 3.8, '2026-06-23 12:30:00+00'),
    (:'outlet_tomato_lot_id'::uuid, :'tenant_id'::uuid, :'outlet_kitchen_id'::uuid, 1.55, '2026-06-23 11:01:00+00')
ON CONFLICT (lot_id) DO NOTHING;

INSERT INTO control_jobs (
    id, tenant_id, job_type, dedup_key, payload, correlation_id, status,
    attempts, available_at, lease_until, leased_by, last_error, created_at, updated_at
)
VALUES
    (:'cost_job_id'::uuid, :'tenant_id'::uuid, 'menu.cost_recalculation', :'tomato_id', jsonb_build_object('ingredientId', :'tomato_id', 'offerId', :'tomato_offer_id'), 'seed:procurement:offer', 'completed', 1, '2026-06-20 09:00:00+00', NULL, NULL, NULL, '2026-06-20 09:00:00+00', '2026-06-20 09:10:00+00'),
    (:'expiry_job_id'::uuid, :'tenant_id'::uuid, 'inventory.expiry_alerts', 'daily-expiry-alerts', '{}'::jsonb, 'seed:inventory:expiry', 'queued', 0, '2026-06-26 00:00:00+00', NULL, NULL, NULL, '2026-06-26 00:00:00+00', '2026-06-26 00:00:00+00')
ON CONFLICT (id) DO NOTHING;

INSERT INTO control_outbox_events (
    id, tenant_id, event_type, aggregate_id, payload, correlation_id, status,
    attempts, available_at, created_at, processed_at, last_error
)
VALUES
    (:'offer_outbox_id'::uuid, :'tenant_id'::uuid, 'procurement.supplier_offer.accepted', :'tomato_offer_id'::uuid, jsonb_build_object('ingredientId', :'tomato_id', 'offerId', :'tomato_offer_id'), 'seed:procurement:offer', 'processed', 1, '2026-06-20 09:00:00+00', '2026-06-20 09:00:00+00', '2026-06-20 09:10:00+00', NULL),
    (:'receipt_outbox_id'::uuid, :'tenant_id'::uuid, 'procurement.supplier_receipt.accepted', :'receipt_id'::uuid, jsonb_build_object('receiptId', :'receipt_id', 'inventoryTransactionId', :'receipt_tx_id'), 'seed:procurement:receipt', 'pending', 0, '2026-06-20 10:05:00+00', '2026-06-20 10:05:00+00', NULL, NULL),
    (:'production_outbox_id'::uuid, :'tenant_id'::uuid, 'inventory.production_batch.posted', :'production_batch_id'::uuid, jsonb_build_object('productionBatchId', :'production_batch_id', 'inventoryTransactionId', :'production_tx_id', 'outputLotId', :'sauce_lot_id'), 'seed:inventory:production', 'pending', 0, '2026-06-21 08:05:00+00', '2026-06-21 08:05:00+00', NULL, NULL)
ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_cost_projection_states (recipe_version_id, tenant_id, status, updated_at, last_error)
VALUES
    (:'sauce_version_id'::uuid, :'tenant_id'::uuid, 'current', '2026-06-20 09:10:00+00', NULL),
    (:'pizza_version_id'::uuid, :'tenant_id'::uuid, 'current', '2026-06-20 09:10:00+00', NULL)
ON CONFLICT (recipe_version_id) DO NOTHING;

INSERT INTO menu_cost_projection_snapshots (
    id, tenant_id, recipe_version_id, source_job_id, total_cost, calculated_at
)
VALUES
    (:'sauce_projection_snapshot_id'::uuid, :'tenant_id'::uuid, :'sauce_version_id'::uuid, :'cost_job_id'::uuid, 10760, '2026-06-20 09:10:00+00'),
    (:'pizza_projection_snapshot_id'::uuid, :'tenant_id'::uuid, :'pizza_version_id'::uuid, :'cost_job_id'::uuid, 2114, '2026-06-20 09:10:00+00')
ON CONFLICT (tenant_id, recipe_version_id, source_job_id) DO NOTHING;

INSERT INTO inventory_expiry_alerts (
    id, tenant_id, warehouse_id, lot_id, expiry_date, rule_key, status,
    created_at, acknowledged_by, acknowledged_at, action_note
)
VALUES
    (:'expiry_alert_id'::uuid, :'tenant_id'::uuid, :'main_kitchen_id'::uuid, :'tomato_lot_id'::uuid, '2026-06-28', 'expiry-within-3-days-v1', 'active', '2026-06-26 06:00:00+00', NULL, NULL, NULL),
    (:'acknowledged_alert_id'::uuid, :'tenant_id'::uuid, :'main_kitchen_id'::uuid, :'basil_lot_id'::uuid, '2026-07-10', 'manual-quality-review-v1', 'acknowledged', '2026-06-24 06:00:00+00', :'manager_user_id'::uuid, '2026-06-24 08:00:00+00', 'Moved into today prep list')
ON CONFLICT (tenant_id, lot_id, rule_key) DO NOTHING;

INSERT INTO control_notifications (
    id, tenant_id, source_alert_id, recipient_role, title, body,
    status, created_at, acknowledged_at
)
VALUES
    (:'expiry_notification_id'::uuid, :'tenant_id'::uuid, :'expiry_alert_id'::uuid, 'branch_operator', 'Lot nearing expiry', 'Lot LOT-TOM-2026-06-28 expires on 2026-06-28.', 'active', '2026-06-26 06:00:00+00', NULL),
    (:'acknowledged_notification_id'::uuid, :'tenant_id'::uuid, :'acknowledged_alert_id'::uuid, 'branch_manager', 'Manual quality review', 'Lot LOT-BASIL-2026-07-10 was reviewed.', 'acknowledged', '2026-06-24 06:00:00+00', '2026-06-24 08:00:00+00')
ON CONFLICT (id) DO NOTHING;

INSERT INTO control_audit_events (id, tenant_id, actor_id, correlation_id, action, object_reference, occurred_at)
VALUES
    ('00000000-0000-4000-8000-000000000d01'::uuid, :'tenant_id'::uuid, :'admin_user_id'::uuid, 'seed:platform', 'tenant.seeded', :'tenant_id', '2026-06-26 12:00:00+00'),
    ('00000000-0000-4000-8000-000000000d02'::uuid, :'tenant_id'::uuid, :'admin_user_id'::uuid, 'seed:menu', 'menu.catalog.seeded', :'pizza_version_id', '2026-06-26 12:01:00+00'),
    ('00000000-0000-4000-8000-000000000d03'::uuid, :'tenant_id'::uuid, :'admin_user_id'::uuid, 'seed:procurement', 'procurement.seeded', :'receipt_id', '2026-06-26 12:02:00+00'),
    ('00000000-0000-4000-8000-000000000d04'::uuid, :'tenant_id'::uuid, :'admin_user_id'::uuid, 'seed:inventory', 'inventory.seeded', :'production_batch_id', '2026-06-26 12:03:00+00'),
    ('00000000-0000-4000-8000-000000000d05'::uuid, :'tenant_id'::uuid, :'manager_user_id'::uuid, 'seed:control', 'control.alert.seeded', :'expiry_alert_id', '2026-06-26 12:04:00+00')
ON CONFLICT (id) DO NOTHING;

COMMIT;
