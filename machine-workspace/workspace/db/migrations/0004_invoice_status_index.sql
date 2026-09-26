-- 0004_invoice_status_index.sql: the reminders job scans unpaid invoices by due date.
BEGIN;
CREATE INDEX idx_invoices_status_due ON invoices(status, due_on);
INSERT INTO schema_migrations (version, name, applied_at) VALUES (4, 'invoice_status_index', datetime('now'));
COMMIT;
