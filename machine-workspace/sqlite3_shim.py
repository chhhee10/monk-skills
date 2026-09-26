#!/usr/bin/env python3
"""A small stand-in for the sqlite3 CLI, backed by Python's sqlite3 module.

setup.sh installs it as `sqlite3` only when the real CLI is missing. Supports the common cases:
  sqlite3 [-readonly] [-header] [-column|-box|-table|-markdown|-csv|-json|-list|-line] [-separator S] [-bail] DB ["SQL or .command" ...]
  sqlite3 DB < script.sql
Dot commands: .tables, .schema [table], .indexes [table], .headers on|off, .mode MODE, .read FILE, .quit
"""

import csv
import json
import sqlite3
import sys
from urllib.parse import quote

MODES = {
    "-column": "column", "-box": "column", "-table": "column", "-markdown": "column",
    "-csv": "csv", "-json": "json", "-list": "list", "-line": "line",
}


class Shell:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.mode, self.header, self.sep, self.bail, self.failed = "list", False, "|", False, False

    def show(self, cols: list[str], rows: list[tuple]) -> None:
        text = lambda v: "" if v is None else str(v)  # noqa: E731
        out = sys.stdout
        if self.mode == "json":
            if rows:
                out.write(json.dumps([dict(zip(cols, r)) for r in rows], default=str) + "\n")
        elif self.mode == "csv":
            w = csv.writer(out, lineterminator="\n")
            if self.header:
                w.writerow(cols)
            w.writerows([[text(v) for v in r] for r in rows])
        elif self.mode == "line":
            width = max(len(c) for c in cols)
            for r in rows:
                out.write("\n".join(f"{c.rjust(width)} = {text(v)}" for c, v in zip(cols, r)) + "\n\n")
        elif self.mode == "column":
            widths = [max([len(c)] + [len(text(r[i])) for r in rows]) for i, c in enumerate(cols)]
            line = lambda vals: "  ".join(v.ljust(w) for v, w in zip(vals, widths)).rstrip()  # noqa: E731
            out.write(line(cols) + "\n" + line(["-" * w for w in widths]) + "\n")
            for r in rows:
                out.write(line([text(v) for v in r]) + "\n")
        else:
            if self.header:
                out.write(self.sep.join(cols) + "\n")
            for r in rows:
                out.write(self.sep.join(text(v) for v in r) + "\n")

    def dot(self, line: str) -> None:
        cmd, *args = line.split()
        if cmd in (".quit", ".exit"):
            sys.exit(1 if self.failed else 0)
        if cmd in (".headers", ".header"):
            self.header = bool(args) and args[0] == "on"
        elif cmd == ".mode" and args:
            self.mode = {"box": "column", "table": "column", "markdown": "column"}.get(args[0], args[0])
        elif cmd == ".read" and args:
            path = line.split(None, 1)[1].strip().strip("'\"")
            try:
                with open(path, encoding="utf-8") as f:
                    self.run(f.read())
            except OSError as e:
                self.error(f"cannot open \"{path}\": {e.strerror}")
        elif cmd == ".tables":
            names = [r[0] for r in self.db.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' ORDER BY 1")]
            print("  ".join(names))
        elif cmd in (".schema", ".indexes", ".indices"):
            kind = "AND type = 'index'" if cmd != ".schema" else ""
            where = "AND tbl_name = ?" if args else ""
            q = f"SELECT {'sql' if cmd == '.schema' else 'name'} FROM sqlite_master WHERE sql IS NOT NULL {kind} {where} ORDER BY type DESC, name"
            for (s,) in self.db.execute(q, args[:1]):
                print(s + (";" if cmd == ".schema" else ""))
        else:
            self.error(f"unsupported dot command in this shim: {cmd}")

    def error(self, msg: str) -> None:
        print(f"Error: {msg}", file=sys.stderr)
        self.failed = True
        if self.bail:
            sys.exit(1)

    def run(self, text: str) -> None:
        buf = ""
        for line in text.splitlines(keepends=True):
            if not buf.strip() and line.lstrip().startswith("."):
                self.dot(line.strip())
                continue
            for ch in line:
                buf += ch
                if ch == ";" and sqlite3.complete_statement(buf):
                    self.execute(buf)
                    buf = ""
        if buf.strip():
            self.execute(buf)

    def execute(self, sql: str) -> None:
        try:
            cur = self.db.execute(sql)
            if cur.description:
                self.show([d[0] for d in cur.description], cur.fetchall())
        except sqlite3.Error as e:
            self.error(f"{e} (in: {' '.join(sql.split())[:120]})")


def main(argv: list[str]) -> int:
    opts = {"header": False, "mode": "list", "sep": "|", "bail": False, "readonly": False}
    rest = []
    it = iter(argv)
    for a in it:
        if a == "-readonly":
            opts["readonly"] = True
        elif a in ("-header", "-headers"):
            opts["header"] = True
        elif a == "-noheader":
            opts["header"] = False
        elif a in MODES:
            opts["mode"] = MODES[a]
            opts["header"] = opts["header"] or a in ("-column", "-box", "-table")
        elif a == "-separator":
            opts["sep"] = next(it, "|")
        elif a == "-bail":
            opts["bail"] = True
        elif a == "-batch":
            continue
        elif a in ("-version", "--version"):
            print(f"{sqlite3.sqlite_version} (python sqlite3 module shim)")
            return 0
        elif a.startswith("-") and not rest:
            # Like the real CLI: an unknown option must not be taken for the database path.
            print(f"sqlite3: Error: unknown option: {a} (this is a small shim; see sqlite3_shim.py)", file=sys.stderr)
            return 1
        else:
            rest.append(a)
    path = rest[0] if rest else ":memory:"
    try:
        if opts["readonly"] and path != ":memory:":
            db = sqlite3.connect(f"file:{quote(path)}?mode=ro", uri=True, isolation_level=None)
        else:
            db = sqlite3.connect(path, isolation_level=None)
    except sqlite3.Error as e:
        print(f'Error: unable to open database "{path}": {e}', file=sys.stderr)
        return 1
    shell = Shell(db)
    shell.mode, shell.header, shell.sep, shell.bail = opts["mode"], opts["header"], opts["sep"], opts["bail"]
    if len(rest) > 1:
        for cmd in rest[1:]:
            shell.run(cmd)
    elif not sys.stdin.isatty():
        shell.run(sys.stdin.read())
    else:
        print("sqlite3 shim: pass SQL as an argument or on stdin (no interactive mode)", file=sys.stderr)
        return 1
    return 1 if shell.failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
