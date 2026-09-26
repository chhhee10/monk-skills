-- 0007_invoice_amounts_in_rupees.sql
-- Finance wants rupee amounts in the reporting views (FIN-88). Convert invoices.amount_paise
-- (INTEGER, paise) to invoices.amount_inr (NUMERIC(12,2), rupees). Pure unit conversion.
-- Author: arjun.k   Scheduled: Sat 2026-09-27 22:00 IST maintenance window   Reviewed by: (pending)
BEGIN;
ALTER TABLE invoices ADD COLUMN amount_inr NUMERIC(12,2);
UPDATE invoices SET amount_inr = amount_paise / 100;
ALTER TABLE invoices DROP COLUMN amount_paise;
INSERT INTO schema_migrations (version, name, applied_at) VALUES (7, 'invoice_amounts_in_rupees', datetime('now'));
COMMIT;
