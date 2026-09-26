# Ledgerly shared workspace

Ledgerly is a small billing and invoicing SaaS company in Bengaluru. This is the team's shared ops box: code, a copy of the billing database, exports from AWS, IAM and the helpdesk, logs, runbooks and notes.
Snapshot of 25 Sep 2026 (IST). Nothing here is connected to live systems.

| Path | What it is |
|---|---|
| `projects/ledgerly-api/` | Billing API helpers (Python, standard library only). A git repo with tags `v1.3.0` and `v1.4.0`. Tests: `python3 -m unittest discover -s tests` |
| `db/ledgerly.db`, `db/ledgerly.sql` | The billing database (customers, invoices, payments) as of 24 Sep 23:00, at migration 0006 |
| `db/migrations/` | Schema migrations. 0007 is scheduled for Sat 27 Sep 22:00 |
| `infra/inventory.json` | AWS inventory export: instances, volumes, load balancers, with owner, last use and monthly cost |
| `iam/users.csv`, `iam/roles.json` | Access export from the admin console, with last login and last use of each role |
| `support/tickets.json` | Helpdesk queue |
| `logs/app.log` | API and worker logs for 25 Sep |
| `logs/nginx/access.log` | Load balancer access log, 25 Sep 13:00-17:30 |
| `logs/archive/` | Rotated logs |
| `runbooks/` | Operational runbooks and the scripts they call |
| `data/sales_2026_q3.csv` | Q3 2026 invoices to date (1 Jul to 24 Sep), excluding void and draft; amounts in rupees |
| `notes/` | Standup notes and the team todo |

Tools on this box: `python3`, `git`, `sqlite3`, `jq`, `rg`, `tree`.
