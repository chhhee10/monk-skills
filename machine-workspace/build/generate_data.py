#!/usr/bin/env python3
"""Maintainers only: regenerates the deterministic data files under ../workspace.

setup.sh never runs this; it copies the committed outputs. Run it after changing the story,
then `python3 generate_data.py --facts` prints the ground truth the demo prompts are checked against.

Writes:
  workspace/db/ledgerly.sql          (schema from migrations 0001-0006 + data, iterdump format)
  workspace/data/sales_2026_q3.csv   (Q3 invoices to date, from the same data)
  workspace/logs/app.log             (2026-09-25, api + worker logs)
  workspace/logs/nginx/access.log    (2026-09-25 13:00-17:30)
"""

import csv
import io
import random
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

WS = Path(__file__).resolve().parent.parent / "workspace"
SNAPSHOT = date(2026, 9, 24)  # prod dump taken 2026-09-24 23:00 IST
LOG_DAY = date(2026, 9, 25)
IST = "+05:30"

SURNAMES = [
    "Sharma", "Iyer", "Kapoor", "Reddy", "Nair", "Gupta", "Patel", "Menon", "Rao", "Das", "Joshi", "Bose", "Khan",
    "Singh", "Chopra", "Pillai", "Kulkarni", "Banerjee", "Mehta", "Verma", "Shetty", "Hegde", "Agarwal", "Saxena",
]
KINDS = [
    "Traders", "Textiles", "Foods", "Logistics", "Pharma", "Electricals", "Enterprises", "Exports", "Hardware",
    "Clinics", "Studios", "Motors", "Agro", "Constructions", "Jewellers", "Tutorials", "Caterers", "Opticals",
]
CITIES = ["Bengaluru", "Mumbai", "Delhi", "Pune", "Hyderabad", "Chennai", "Kolkata", "Ahmedabad"]
CITY_WEIGHTS = [26, 18, 16, 11, 11, 9, 5, 4]
PRICE_PAISE = {"starter": 49900, "growth": 99900, "scale": 199900}  # per seat per month
SEATS = {"starter": (1, 5), "growth": (3, 25), "scale": (10, 60)}
CHANNELS = ["self-serve", "sales", "partner"]


def slug(name: str) -> str:
    return "".join(ch for ch in name.lower() if ch.isalnum())


def add_months(d: date, n: int, day: int) -> date:
    m = d.month - 1 + n
    return date(d.year + m // 12, m % 12 + 1, day)


def customers(rng: random.Random) -> list[dict]:
    out, used = [], set()
    for i in range(90):
        cid = 1001 + i
        while True:
            name = f"{rng.choice(SURNAMES)} {rng.choice(KINDS)}"
            if name not in used:
                break
        if cid == 1042:
            name = "Sharma Traders"
        elif name == "Sharma Traders":
            name = "Sharma Textiles" if "Sharma Textiles" not in used else f"Sharma {KINDS[i % len(KINDS)]} Co"
        used.add(name)
        plan = rng.choices(["starter", "growth", "scale"], [45, 40, 15])[0]
        lo, hi = SEATS[plan]
        # More sign-ups recently: Ledgerly is growing.
        created = date(2025, 3, 1) + timedelta(days=int((rng.random() ** 0.7) * (SNAPSHOT - date(2025, 3, 1)).days))
        out.append({
            "id": cid, "name": name, "email": f"accounts@{slug(name)}.example", "created_at": created.isoformat(),
            "city": rng.choices(CITIES, CITY_WEIGHTS)[0], "plan": plan, "seats": rng.randint(lo, hi),
            "status": "active", "net_days": rng.choices([7, 15, 30], [10, 70, 20])[0],
            "channel": rng.choices(CHANNELS, [55, 30, 15])[0], "churn_after": None,
        })
    c1042 = out[41]
    c1042.update(city="Delhi", plan="growth", seats=12, net_days=45, created_at="2025-04-14", channel="sales")
    c1063 = out[62]
    c1063.update(net_days=45, plan="scale", seats=24, created_at="2025-07-02", channel="sales")
    for c in rng.sample([c for c in out if c["id"] not in (1042, 1063)], 7):
        c["status"] = "churned"
        c["churn_after"] = rng.randint(2, 7)  # invoices billed in 2026 before churning
    return out


def invoices_and_payments(rng: random.Random, custs: list[dict]) -> tuple[list[dict], list[dict]]:
    invs, pays = [], []
    for c in sorted(custs, key=lambda c: c["created_at"]):
        created = date.fromisoformat(c["created_at"])
        day = min(created.day, 28)
        start = max(date(created.year, created.month, day), date(2026, 1, day))
        if start < created:
            start = add_months(start, 1, day)
        n = 0
        while True:
            issued = add_months(start, n, day)
            if issued > SNAPSHOT or (c["churn_after"] is not None and n >= c["churn_after"]):
                break
            n += 1
            invs.append({"customer": c, "issued_on": issued})
    invs.sort(key=lambda i: (i["issued_on"], i["customer"]["id"]))
    for idx, inv in enumerate(invs):
        c, issued = inv["customer"], inv["issued_on"]
        subtotal = c["seats"] * PRICE_PAISE[c["plan"]]
        gst = subtotal * 18 // 100  # exact: prices are whole rupees
        # Terms changed to Net 45 on 2026-09-21 for 1042 and 1063; older invoices kept Net 15.
        net = c["net_days"] if not (c["net_days"] == 45 and issued < date(2026, 9, 21)) else 15
        due = issued + timedelta(days=net)
        r = rng.random()
        if r < 0.012:
            status = "void"
        elif issued >= SNAPSHOT - timedelta(days=1) and r < 0.08:
            status = "draft"
        elif due < SNAPSHOT:
            status = "paid" if r < 0.94 else "sent"
        else:
            status = "paid" if r < 0.3 else "sent"
        inv.update(
            id=idx + 1, number=f"LDG-{issued.year}-{idx + 1:05d}", due_on=due, status=status,
            subtotal=subtotal, gst=gst, amount_paise=subtotal + gst,
        )
        if status == "paid":
            paid_on = min(issued + timedelta(days=rng.randint(1, net + 4)), SNAPSHOT)
            method = rng.choices(["upi", "neft", "card", "cheque"], [40, 35, 20, 5])[0]
            parts = [inv["amount_paise"]]
            if rng.random() < 0.1:
                first = inv["amount_paise"] // 2
                parts = [first, inv["amount_paise"] - first]
            for k, amount in enumerate(parts):
                on = min(paid_on + timedelta(days=3 * k), SNAPSHOT)  # second part three days later
                at = datetime.combine(on, datetime.min.time()) + timedelta(minutes=rng.randint(9 * 60, 20 * 60))
                pays.append({"invoice_id": inv["id"], "paid_at": at.strftime("%Y-%m-%d %H:%M:%S"), "amount_paise": amount, "method": method})
    for k, p in enumerate(sorted(pays, key=lambda p: (p["paid_at"], p["invoice_id"]))):
        p["id"] = k + 1
    return invs, sorted(pays, key=lambda p: p["id"])


def build_db(custs: list[dict], invs: list[dict], pays: list[dict]) -> sqlite3.Connection:
    db = sqlite3.connect(":memory:")
    for f in sorted((WS / "db" / "migrations").glob("000[1-6]_*.sql")):
        db.executescript(f.read_text())
    applied = ["2025-03-02 22:14:05", "2025-05-17 22:03:41", "2025-08-09 22:20:13", "2025-11-22 22:07:56", "2026-02-14 22:11:30", "2026-07-11 22:05:02"]
    for v, at in enumerate(applied, 1):
        db.execute("UPDATE schema_migrations SET applied_at = ? WHERE version = ?", (at, v))
    db.executemany(
        "INSERT INTO customers (id, name, email, created_at, city, plan, seats, status, net_days) VALUES (?,?,?,?,?,?,?,?,?)",
        [(c["id"], c["name"], c["email"], c["created_at"] + " 10:00:00", c["city"], c["plan"], c["seats"], c["status"], c["net_days"]) for c in custs],
    )
    db.executemany(
        "INSERT INTO invoices (id, number, customer_id, issued_on, due_on, status, amount_paise) VALUES (?,?,?,?,?,?,?)",
        [(i["id"], i["number"], i["customer"]["id"], i["issued_on"].isoformat(), i["due_on"].isoformat(), i["status"], i["amount_paise"]) for i in invs],
    )
    db.executemany(
        "INSERT INTO payments (id, invoice_id, paid_at, amount_paise, method) VALUES (?,?,?,?,?)",
        [(p["id"], p["invoice_id"], p["paid_at"], p["amount_paise"], p["method"]) for p in pays],
    )
    db.commit()
    return db


def write_dump(db: sqlite3.Connection) -> None:
    head = "-- Ledgerly prod database dump (customer contacts anonymized), taken 2026-09-24 23:00 IST.\n-- Schema at migration 0006. Rebuild: python3 -c \"import sqlite3; sqlite3.connect('ledgerly.db').executescript(open('ledgerly.sql').read())\"\n"
    (WS / "db" / "ledgerly.sql").write_text(head + "\n".join(db.iterdump()) + "\n")


def write_sales(invs: list[dict]) -> list[dict]:
    rows = []
    for i in invs:
        if not (date(2026, 7, 1) <= i["issued_on"] <= SNAPSHOT) or i["status"] in ("void", "draft"):
            continue
        c = i["customer"]
        rows.append({
            "date": i["issued_on"].isoformat(), "invoice_no": i["number"], "customer_id": c["id"], "customer": c["name"],
            "city": c["city"], "plan": c["plan"], "seats": c["seats"], "subtotal_inr": f"{i['subtotal'] / 100:.2f}",
            "gst_inr": f"{i['gst'] / 100:.2f}", "total_inr": f"{i['amount_paise'] / 100:.2f}", "channel": c["channel"],
        })
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    (WS / "data" / "sales_2026_q3.csv").write_text(buf.getvalue())
    return rows


GET_PATHS = ["/v1/invoices?page=1", "/v1/invoices?page=2", "/v1/invoices?status=sent", "/v1/customers/{cid}", "/v1/invoices/{inv}", "/v1/dashboard/summary"]
TRACE = """Traceback (most recent call last):
  File "/srv/ledgerly-web/app/routes.py", line 88, in post_invoices
    body = handlers.create_invoice(payload)
  File "/srv/ledgerly-api/ledgerly_api/handlers.py", line 26, in create_invoice
    due = due_date(issued, int(payload.get("net_days", DEFAULT_NET_DAYS)))
  File "/srv/ledgerly-api/ledgerly_api/invoices.py", line 42, in due_date
    return issued_on.replace(month=issued_on.month + 1, day=day - days_in_month)
ValueError: day is out of range for month"""


def ts(t: datetime) -> str:
    return t.strftime("%Y-%m-%dT%H:%M:%S.") + f"{t.microsecond // 1000:03d}{IST}"


def write_logs(rng: random.Random, custs: list[dict]) -> dict:
    day0 = datetime.combine(LOG_DAY, datetime.min.time())
    at = lambda h, m, s, ms=0: day0 + timedelta(hours=h, minutes=m, seconds=s, milliseconds=ms)  # noqa: E731
    app: list[tuple[datetime, str]] = []
    nginx: list[tuple[datetime, str]] = []
    ids = [c["id"] for c in custs if c["status"] == "active"]
    rid = lambda: f"req_{rng.getrandbits(32):08x}"  # noqa: E731
    web_ips = ["10.20.1.14", "10.20.1.15"]
    agents = ["ledgerly-web/3.8.1", "ledgerly-web/3.8.1", "ledgerly-mobile/2.2.0 (Android 15)", "python-requests/2.32.3"]

    def request(t: datetime, method: str, path: str, status: int, ms: int, host: str, level: str = "INFO", extra: str = "") -> str:
        r = rid()
        app.append((t, f"{ts(t)} {level} [{host}] http: {method} {path} {status} {ms}ms request_id={r}{extra}"))
        if day0 + timedelta(hours=13) <= t < day0 + timedelta(hours=17, minutes=30):
            size = {200: rng.randint(420, 9800), 201: rng.randint(380, 900), 500: 162, 504: 167}.get(status, 150)
            ua = rng.choice(agents)
            nginx.append((t, f'{rng.choice(web_ips)} - - [{t.strftime("%d/%b/%Y:%H:%M:%S")} +0530] "{method} {path} HTTP/1.1" {status} {size} "-" "{ua}" rt={ms / 1000:.3f} req={r}'))
        return r

    def fill(path_tmpl: str) -> str:
        return path_tmpl.format(cid=rng.choice(ids), inv=rng.randint(1, 640))

    for host in ("api-prod-1", "api-prod-2"):
        t = at(9, 0, 2, rng.randint(0, 900))
        app.append((t, f"{ts(t)} INFO [{host}] app: ledgerly-api 1.4.0 (ledgerly-web 3.8.1) starting, workers=4, db pool size=10"))
    t = at(9, 0, 5, 120)
    app.append((t, f"{ts(t)} INFO [worker-prod-1] jobs: scheduler up (reminders 10:30, reconcile-payments 14:00, reminders 17:00)"))

    # Baseline traffic 09:00-18:30.
    t = at(9, 0, 30)
    burst_start, burst_end = at(14, 2, 10, 318), at(14, 8, 56)
    while t < at(18, 30, 0):
        t += timedelta(seconds=rng.randint(8, 40), milliseconds=rng.randint(0, 999))
        if burst_start - timedelta(seconds=20) <= t <= burst_end:
            continue
        host = rng.choice(["api-prod-1", "api-prod-2"])
        if rng.random() < 0.18:
            request(t, "POST", "/v1/invoices", 201, rng.randint(55, 180), host)
        else:
            request(t, "GET", fill(rng.choice(GET_PATHS)), 200, rng.randint(12, 140), host)

    for h, m, n in ((10, 30, 41), (17, 0, 33)):
        t = at(h, m, 0, 310)
        app.append((t, f"{ts(t)} INFO [worker-prod-1] jobs.reminders: queued {n} reminder emails"))
    t = at(11, 47, 12, 604)
    app.append((t, f"{ts(t)} WARN [api-prod-2] db: slow query 1840ms: SELECT * FROM invoices WHERE status = ? ORDER BY due_on LIMIT 50 OFFSET 400"))
    t = at(13, 20, 44, 17)
    app.append((t, f"{ts(t)} WARN [api-prod-1] auth: 5 failed logins for user=meera.joshi from 203.0.113.77 in 2m; locked for 15m"))

    # 14:00 reconcile-payments job holds pool connections; API requests time out waiting.
    t = at(14, 1, 58, 441)
    app.append((t, f"{ts(t)} INFO [worker-prod-1] jobs.reconcile: started batch=2026-09-25 payments=567 source=bank-feed concurrency=10"))
    t = at(14, 2, 4, 90)
    app.append((t, f"{ts(t)} WARN [api-prod-1] db.pool: pool exhausted (size=10 in_use=10 waiting=6)"))
    t = burst_start
    timeouts = 0
    while t <= burst_end:
        host = rng.choice(["api-prod-1", "api-prod-2"])
        method, path = ("POST", "/v1/invoices") if rng.random() < 0.35 else ("GET", fill(rng.choice(GET_PATHS)))
        r = rid()
        waiting = rng.randint(8, 41)
        app.append((t, f"{ts(t)} ERROR [{host}] db.pool: timeout acquiring connection after 5000ms (size=10 in_use=10 waiting={waiting}) request_id={r}"))
        t2 = t + timedelta(milliseconds=rng.randint(3, 12))
        app.append((t2, f"{ts(t2)} WARN [{host}] http: {method} {path} 504 {5000 + (t2 - t).microseconds // 1000}ms request_id={r}"))
        nginx.append((t2, f'{rng.choice(web_ips)} - - [{t2.strftime("%d/%b/%Y:%H:%M:%S")} +0530] "{method} {path} HTTP/1.1" 504 167 "-" "{rng.choice(agents)}" rt={5 + (t2 - t).microseconds / 1e6:.3f} req={r}'))
        timeouts += 1
        t += timedelta(seconds=rng.randint(4, 14), milliseconds=rng.randint(0, 999))
    t = at(14, 3, 40, 377)
    app.append((t, f"{ts(t)} WARN [worker-prod-1] jobs.reconcile: bank-feed API slow (p95 2.8s), each worker holds its db connection while waiting"))
    t = at(14, 9, 9, 702)
    app.append((t, f"{ts(t)} INFO [worker-prod-1] jobs.reconcile: finished batch=2026-09-25 in 431s (567 payments matched, 0 mismatches)"))
    t = at(14, 9, 12, 5)
    app.append((t, f"{ts(t)} INFO [api-prod-1] db.pool: recovered (size=10 in_use=2 waiting=0)"))

    # Net 45 invoices fail in due_date (ledgerly-api 1.4.0).
    crashes = [(at(16, 41, 7, 883), 1042), (at(16, 43, 31, 204), 1042), (at(16, 52, 18, 559), 1063)]
    for t, cid in crashes:
        request(t, "POST", "/v1/invoices", 500, rng.randint(20, 40), "api-prod-1", "ERROR", f" customer_id={cid} net_days=45")
        app.append((t + timedelta(milliseconds=1), TRACE))

    app.sort(key=lambda e: e[0])
    nginx.sort(key=lambda e: e[0])
    (WS / "logs" / "app.log").write_text("\n".join(line for _, line in app) + "\n")
    (WS / "logs" / "nginx" / "access.log").write_text("\n".join(line for _, line in nginx) + "\n")
    return {"timeouts": timeouts, "burst": (ts(burst_start), ts(burst_end)), "crashes": [ts(t) for t, _ in crashes]}


def facts(db: sqlite3.Connection, rows: list[dict], logs: dict) -> None:
    q = lambda sql: db.execute(sql).fetchall()  # noqa: E731
    print("customers", q("SELECT count(*), sum(status='active'), sum(status='churned') FROM customers"))
    print("invoices", q("SELECT count(*) FROM invoices"), q("SELECT status, count(*) FROM invoices GROUP BY 1"))
    print("payments", q("SELECT count(*), sum(amount_paise) FROM payments"))
    print("0007 affected rows (paise != 0):", q("SELECT count(*), sum(amount_paise % 100) FROM invoices WHERE amount_paise % 100 != 0"))
    print("invoice total paise:", q("SELECT sum(amount_paise) FROM invoices"))
    print("net_days 45:", q("SELECT id, name, city FROM customers WHERE net_days = 45"))
    overdue = q(f"SELECT count(*), sum(amount_paise) FROM invoices WHERE status='sent' AND due_on < '{LOG_DAY.isoformat()}'")
    print("overdue as of 2026-09-25 (sent, due_on < 2026-09-25):", overdue)
    by_month: dict[str, float] = defaultdict(float)
    by_city: dict[str, float] = defaultdict(float)
    city_month: dict[tuple[str, str], float] = defaultdict(float)
    by_cust: Counter = Counter()
    by_plan: dict[str, float] = defaultdict(float)
    for r in rows:
        v = float(r["subtotal_inr"])
        by_month[r["date"][:7]] += v
        by_city[r["city"]] += v
        city_month[(r["city"], r["date"][:7])] += v
        by_cust[r["customer"]] += v
        by_plan[r["plan"]] += v
    print("sales rows", len(rows), "subtotal", round(sum(float(r["subtotal_inr"]) for r in rows), 2), "total", round(sum(float(r["total_inr"]) for r in rows), 2))
    print("by month", {k: round(v, 2) for k, v in sorted(by_month.items())})
    print("by city", sorted(((round(v, 2), k) for k, v in by_city.items()), reverse=True))
    print("by plan", {k: round(v, 2) for k, v in by_plan.items()})
    print("top customers", [(k, round(v, 2)) for k, v in by_cust.most_common(5)])
    for city in CITIES:
        jul, sep = city_month[(city, "2026-07")], city_month[(city, "2026-09")]
        print(f"  {city}: Jul {jul:.2f} Aug {city_month[(city, '2026-08')]:.2f} Sep {sep:.2f}")
    print("logs", logs)


def main() -> None:
    rng = random.Random(20260925)
    custs = customers(rng)
    invs, pays = invoices_and_payments(rng, custs)
    db = build_db(custs, invs, pays)
    write_dump(db)
    rows = write_sales(invs)
    logs = write_logs(random.Random(925), custs)
    if "--facts" in sys.argv:
        facts(db, rows, logs)


if __name__ == "__main__":
    main()
