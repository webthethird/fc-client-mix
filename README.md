# fc-client-mix

A daily archive of which Farcaster clients people actually post through.

## Why this exists

`haatz.quilibrium.com/v2/farcaster/stats/daily` publishes a per-client breakdown of
network activity. Two things make it worth copying:

1. **It starts on 2026-11-04.** Requesting earlier dates returns the base statistics with no
   client dimension at all. There is no backfill, so no record of the client mix before that
   date exists anywhere.
2. **It is one endpoint on one node.** That node returned `502` to every request on
   2026-11-03. A day lost while nobody is holding a copy is lost for good.

This repository keeps the response verbatim, one file per UTC day, so the record survives
independently of the service and so questions nobody has asked yet can still be answered.

## What a day looks like

`data/YYYY-MM-DD.json` holds the endpoint's own object plus provenance: when it was fetched,
the exact URL, and the `notes` block carrying the definitions, so the data cannot drift away
from the meaning of its fields.

Per client, per day: active FIDs, exclusive FIDs (people who used *only* that client),
messages split by action, and retention against 7/20/30 days earlier.

## Reading it honestly

**FIDs and messages disagree, often wildly.** On 2026-11-04, Terminus accounted for 8 active
accounts and 6,038 messages — 0.3% of people and 15% of traffic. Either number alone misleads.
A handful of automated accounts can move message share by tens of percent between consecutive
days.

**`exclusive_fids` is the figure closest to "which client do people use".** On 2026-11-05,
2,474 of 3,499 active accounts used only the official client.

**The series begins on 2026-11-04 because tracking began then**, not because anything happened
on that date. Nothing here can show a before-and-after for the October vote.

**After the Hypersnap fork this measures Hypersnap's view**, not the whole network. The two
chains currently share validators, so today it is the whole network; that will stop being true.

## Running it

    python3 scripts/archive.py          # DAYS_BACK=5 by default

Idempotent: a completed day already on disk is never rewritten. A day stored while the endpoint
still marked it `partial` is replaced once a repaired copy appears. A GitHub Action runs this
every six hours and commits anything new.
