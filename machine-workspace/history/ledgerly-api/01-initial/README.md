# ledgerly-api

Core billing helpers behind Ledgerly's `/v1` API: money formatting, invoice totals and payment terms.
Pure Python standard library, no dependencies.

## Run the tests

```
python3 -m unittest discover -s tests -v
```

## Conventions

- Money is always integer **paise** (₹1 = 100 paise). Convert at the edges with `money.to_paise` and `money.format_inr`.
- Dates are `datetime.date`, serialized as ISO 8601 (`2026-09-25`).
