-- 0002_payments.sql: one row per payment received; an invoice can be paid in parts.
BEGIN;
CREATE TABLE payments (
  id INTEGER PRIMARY KEY,
  invoice_id INTEGER NOT NULL REFERENCES invoices(id),
  paid_at TEXT NOT NULL,
  amount_paise INTEGER NOT NULL,
  method TEXT NOT NULL CHECK (method IN ('upi', 'neft', 'card', 'cheque'))
);
CREATE INDEX idx_payments_invoice ON payments(invoice_id);
INSERT INTO schema_migrations (version, name, applied_at) VALUES (2, 'payments', datetime('now'));
COMMIT;
