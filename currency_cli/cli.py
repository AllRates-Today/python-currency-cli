from __future__ import annotations

import argparse
import json
import sys

from . import rates


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="currency", description="Convert currencies using official central bank rates.")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("convert", help="convert an amount, e.g. currency convert 100 USD EUR")
    c.add_argument("amount", type=float)
    c.add_argument("source")
    c.add_argument("target")
    c.add_argument("--bank", default="ecb", help="source code, e.g. ecb, fed, boe, rbi, hmrc (default ecb)")
    c.add_argument("--live", action="store_true", help="use real-time mid-market rate (needs ALLRATES_API_KEY)")
    c.add_argument("--json", action="store_true")

    t = sub.add_parser("table", help="print a bank's latest published table")
    t.add_argument("bank", nargs="?", default="ecb")
    t.add_argument("--json", action="store_true")

    sub.add_parser("sources", help="list every central bank and tax authority")

    a = p.parse_args(argv)
    try:
        if a.cmd == "convert":
            if a.live:
                r = rates.live_rate(a.source, a.target)
                rate = r["rates"][0]["rate"] if "rates" in r else r["rate"]
                out = {"amount": a.amount, "result": round(a.amount * rate, 4), "rate": rate, "method": "live mid-market"}
            else:
                out = rates.convert(a.amount, a.source, a.target, a.bank)
            if a.json:
                print(json.dumps(out, indent=2))
            else:
                print(f"{a.amount:g} {a.source.upper()} = {out['result']:.4f} {a.target.upper()}  (rate {out['rate']:.6g}, {out['method']}"
                      + (f", {out['bank']} {out['date']}" if "date" in out else "") + ")")
        elif a.cmd == "table":
            tb = rates.latest_table(a.bank)
            if a.json:
                print(json.dumps(tb, indent=2))
            else:
                print(f"{tb['bank']} {tb['rate_date']}")
                for r in tb["rates"]:
                    print(f"  {r['base']}/{r['quote']:<4} {r['type']:<16} {r['value']}")
        else:
            for s in rates.list_sources():
                flag = " (stale)" if s.get("stale") else ""
                print(f"  {s['code']:<10} {s['latest'] or '-':<10} {s['name']}{flag}")
        return 0
    except Exception as e:  # noqa: BLE001
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
