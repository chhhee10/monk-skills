-- 0003_customer_city_plan.sql: where the customer is and what they pay for.
BEGIN;
ALTER TABLE customers ADD COLUMN city TEXT;
ALTER TABLE customers ADD COLUMN plan TEXT NOT NULL DEFAULT 'starter';
ALTER TABLE customers ADD COLUMN seats INTEGER NOT NULL DEFAULT 1;
INSERT INTO schema_migrations (version, name, applied_at) VALUES (3, 'customer_city_plan', datetime('now'));
COMMIT;
