#!/usr/bin/env python3
"""Archive Farcaster's daily per-client activity breakdown.

haatz publishes this at /v2/farcaster/stats/daily, but only from its
`tracked_from` date -- 2026-11-04 -- and asking for earlier dates returns the
base statistics with no client dimension at all. There is no backfill. So the
record exists only for as long as the endpoint keeps serving it, and the node
returned 502 to every request on 2026-11-03. This keeps a copy.

One file per UTC day, holding the response verbatim rather than a summary, so
questions nobody has thought of yet can still be answered later. A day already
stored is left alone unless the stored copy was marked `partial`, which the
endpoint sets while a day's coverage is still being repaired.
"""
import json, os, sys, urllib.request, datetime, hashlib

SRC = "https://haatz.quilibrium.com/v2/farcaster/stats/daily"
DAYS_BACK = int(os.environ.get("DAYS_BACK", "5"))   # re-check recent days for repairs
TOP = 30                                            # clients before the "other" bucket
OUT = os.path.join(os.path.dirname(__file__), "..", "data")

def fetch(frm, to):
    url = f"{SRC}?from={frm}&to={to}&clients={TOP}"
    req = urllib.request.Request(url, headers={"User-Agent": "fc-client-mix/1.0 (archival)"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return url, json.load(r)

def main():
    today = datetime.datetime.now(datetime.timezone.utc).date()
    frm = (today - datetime.timedelta(days=DAYS_BACK)).isoformat()
    url, payload = fetch(frm, today.isoformat())
    notes = payload.get("notes", {})
    wrote, skipped, repaired = [], [], []
    for day in payload.get("days", []):
        c = day.get("clients")
        if not c:
            continue                      # before tracked_from: no client dimension to keep
        path = os.path.join(OUT, f"{day['date']}.json")
        if os.path.exists(path):
            prev = json.load(open(path))
            if not prev.get("day", {}).get("clients", {}).get("partial"):
                skipped.append(day["date"]); continue
            repaired.append(day["date"])
        rec = {
            "date": day["date"],
            "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "source": url,
            "tracked_from": notes.get("clients", {}).get("tracked_from"),
            "notes": notes,               # definitions travel with the data
            "day": day,
        }
        with open(path, "w") as f:
            json.dump(rec, f, indent=1, sort_keys=True)
        wrote.append(day["date"])
    print(f"wrote {len(wrote)}: {wrote}")
    if repaired: print(f"  (replaced partial copies for {repaired})")
    print(f"unchanged {len(skipped)}: {skipped}")
    have = sorted(f[:-5] for f in os.listdir(OUT) if f.endswith(".json"))
    print(f"archive now holds {len(have)} days: {have[0]} .. {have[-1]}" if have else "archive empty")
    if not wrote and not skipped:
        print("WARNING: the response carried no client data at all", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
