# Billing database

- `ledgerly.sql`: last night's prod dump (2026-09-24 23:00 IST), customer contacts anonymized.
- `ledgerly.db`: SQLite database built from `ledgerly.sql` when this workspace was set up. Treat it as prod data.
- `migrations/`: 0001-0006 are applied in prod (see the `schema_migrations` table). 0007 ships in Saturday's window, 2026-09-27 22:00 IST.

Money columns are integer paise (₹1 = 100 paise). Invoice status is one of `draft`, `sent`, `paid`, `void`; an invoice is overdue when it is `sent` and `due_on` is in the past.

Rehearse a migration on a copy, never on `ledgerly.db` itself:

```
cp ~/workspace/db/ledgerly.db /tmp/rehearsal.db
sqlite3 /tmp/rehearsal.db < ~/workspace/db/migrations/0007_invoice_amounts_in_rupees.sql
```
