-- 0005_customer_status.sql: churned customers stay for history but are not billed.
BEGIN;
ALTER TABLE customers ADD COLUMN status TEXT NOT NULL DEFAULT 'active';
INSERT INTO schema_migrations (version, name, applied_at) VALUES (5, 'customer_status', datetime('now'));
COMMIT;
