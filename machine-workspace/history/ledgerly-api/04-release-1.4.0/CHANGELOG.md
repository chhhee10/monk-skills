# Changelog

All notable changes to ledgerly-api. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versions follow SemVer.

## [1.4.0] - 2026-08-12

### Added
- Invoice totals with GST rounded per line (`invoices.totals`).
- Payment terms: `invoices.due_date` for Net 7/15/30/45.
- Reminder selection for the daily reminder email (`reminders.reminders_due`).
- `handlers.create_invoice`, behind `POST /v1/invoices`.

## [1.3.0] - 2026-06-30

### Added
- `money.to_paise` and `money.format_inr`, moved out of the monolith.
