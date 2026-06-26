\set ON_ERROR_STOP on

BEGIN;

-- Delivery-infrastructure migration contract only. Functional schema starts in TDD work orders.
SELECT current_database() AS database_name, current_user AS database_user;

COMMIT;

