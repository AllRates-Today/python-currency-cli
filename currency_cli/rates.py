"""Rate lookups.

Two data paths, both from AllRatesToday (https://allratestoday.com):

* Official central bank tables: keyless, edge-cached, published once a day.
  https://allratestoday.com/api/open/central-bank/<bank>
* Live mid-market rates for 160+ currencies: needs a free API key in the
  ALLRATES_API_KEY environment variable.
  https://allratestoday.com/api/v1/rates
"""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request

OPEN = "https://allratestoday.com/api/open"
LIVE = "https://allratestoday.com/api/v1/rates"
UA = "python-currency-cli (github.com/AllRates-Today/python-currency-cli)"


def _get(url: str, headers: dict | None = None) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=15) as res:
        return json.load(res)


def list_sources() -> list[dict]:
    """Every central bank and tax authority, with its latest publication date."""
    return _get(f"{OPEN}/central-banks")["sources"]


def latest_table(bank: str = "ecb") -> dict:
    """The bank's latest published table: {'bank', 'rate_date', 'rates': [...]}."""
    return _get(f"{OPEN}/central-bank/{bank.lower()}")


def convert(amount: float, source: str, target: str, bank: str = "ecb") -> dict:
    """Convert using the bank's published rate, its inverse, or a cross via the
    bank's home currency. The result says which, so it can be cited correctly."""
    source, target = source.upper(), target.upper()
    if source == target:
        return {"amount": amount, "result": amount, "rate": 1.0, "method": "identity", "bank": bank}
    table = latest_table(bank)
    rates = {(r["base"], r["quote"]): r["value"] for r in table["rates"]}

    if (source, target) in rates:
        rate, method = rates[(source, target)], "published"
    elif (target, source) in rates:
        rate, method = 1 / rates[(target, source)], "inverse"
    else:
        # cross via whichever currency the bank quotes everything against
        homes = {b for b, _ in rates} | {q for _, q in rates}
        rate = None
        for home in homes:
            a = rates.get((home, source)) or (1 / rates[(source, home)] if (source, home) in rates else None)
            b = rates.get((home, target)) or (1 / rates[(target, home)] if (target, home) in rates else None)
            if a and b:
                rate, method = b / a, f"cross via {home}"
                break
        if rate is None:
            raise ValueError(f"{bank} does not publish a rate covering {source}/{target}")
    return {
        "amount": amount, "source": source, "target": target, "rate": rate,
        "result": round(amount * rate, 4), "method": method,
        "bank": table["bank"], "date": table["rate_date"],
        "attribution": table.get("attribution", {}).get("url", "https://allratestoday.com"),
    }


def live_rate(source: str, target: str, api_key: str | None = None) -> dict:
    """Real-time mid-market rate. Needs a free key from https://allratestoday.com/register."""
    key = api_key or os.environ.get("ALLRATES_API_KEY")
    if not key:
        raise RuntimeError("Set ALLRATES_API_KEY (free at https://allratestoday.com/register) for live rates")
    qs = urllib.parse.urlencode({"source": source.upper(), "target": target.upper()})
    return _get(f"{LIVE}?{qs}", {"Authorization": f"Bearer {key}"})
