# ledgerly-api

Core billing helpers behind Ledgerly's `/v1` API: money formatting, invoice totals and payment terms.
Pure Python standard library, no dependencies. The HTTP layer lives in `ledgerly-web` and calls into this package.

## Run the tests

```
python3 -m unittest discover -s tests -v
```

## Conventions

- Money is always integer **paise** (₹1 = 100 paise). Convert at the edges with `money.to_paise` and `money.format_inr`.
- Dates are `datetime.date`, serialized as ISO 8601 (`2026-09-25`).

## POST /v1/invoices → `handlers.create_invoice`

```json
{
  "customer_id": 1042,
  "issued_on": "2026-09-25",
  "net_days": 15,
  "lines": [{"description": "Growth plan, 5 seats", "quantity": 5, "unit_paise": 99900, "gst_percent": 18}]
}
```

- `issued_on` defaults to today, `net_days` to 15 (the customer's terms: 7, 15, 30 or 45), `gst_percent` to 18.
- Returns `issued_on`, `due_on`, `subtotal`, `gst`, `total` (paise) and `total_display` (for example `₹5,894.10`).
- A negative `quantity` makes a credit note line. A zero quantity is an error.

## Errors

| Exception | HTTP | When |
|---|---|---|
| `handlers.BadRequest` | 400 | no lines |
| `ValueError` | 500 | anything else; ledgerly-web logs the traceback |

## Releasing

1. Move the `[Unreleased]` entries in `CHANGELOG.md` under the new version and date.
2. Bump `__version__` in `ledgerly_api/__init__.py` and `version` in `pyproject.toml`.
3. Commit `chore: release vX.Y.Z`, tag `vX.Y.Z`, push the tag. CI builds and deploys.
