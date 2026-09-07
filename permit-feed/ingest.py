"""Public Chicago building-permit ingest. No keys. No mail."""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "chicago-permits.json"
SOURCE = "https://data.cityofchicago.org/resource/ydr8-5enu.json"


def fetch(limit: int = 50) -> list[dict]:
    q = urllib.parse.urlencode({"$limit": str(limit), "$order": "issue_date DESC"})
    req = urllib.request.Request(
        f"{SOURCE}?{q}",
        headers={"User-Agent": "permit-feed/1", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.loads(resp.read().decode("utf-8"))


def slim(row: dict) -> dict:
    addr = " ".join(
        str(row[k])
        for k in ("street_number", "street_direction", "street_name", "suffix")
        if row.get(k)
    )
    return {
        "permit": row.get("permit_"),
        "status": row.get("permit_status"),
        "issue_date": row.get("issue_date"),
        "work_type": row.get("work_type"),
        "work": row.get("work_description") or row.get("permit_type"),
        "address": addr,
        "reported_cost": row.get("reported_cost"),
        "ward": row.get("ward"),
        "gc": row.get("contact_4_name") or row.get("contact_3_name"),
        "owner": row.get("contact_1_name"),
    }


def main() -> None:
    rows = [slim(r) for r in fetch()]
    payload = {
        "asof": datetime.now(timezone.utc).isoformat(),
        "source": SOURCE,
        "n": len(rows),
        "rows": rows,
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote {OUT} n={len(rows)}")


if __name__ == "__main__":
    main()
