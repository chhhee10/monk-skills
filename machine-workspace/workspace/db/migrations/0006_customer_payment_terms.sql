-- 0006_customer_payment_terms.sql: per-customer payment terms (Net 7/15/30/45). Default Net 15.
BEGIN;
ALTER TABLE customers ADD COLUMN net_days INTEGER NOT NULL DEFAULT 15 CHECK (net_days IN (7, 15, 30, 45));
INSERT INTO schema_migrations (version, name, applied_at) VALUES (6, 'customer_payment_terms', datetime('now'));
COMMIT;
