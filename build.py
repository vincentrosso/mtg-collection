#!/usr/bin/env python3
"""Bundle data/high_value.json + data/full_inventory.csv into data/bundle.js.

The page loads bundle.js with a <script> tag, so index.html works when opened
straight from disk (browsers block fetch() on file://). Internal columns
(Location, Value) and rows given away are stripped HERE, so they never ship.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
HIDDEN_LOCATIONS = {"given to thomas"}


def num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def main():
    hv = json.loads((DATA / "high_value.json").read_text())
    cards = [
        {k: c.get(k) for k in
         ("card", "set", "set_code", "qty", "est_each", "est_total", "notes", "photo", "status", "asking_price")}
        for c in hv["cards"]
    ]

    inventory = []
    with open(DATA / "full_inventory.csv", newline="") as f:
        for row in csv.DictReader(f):
            if (row.get("Location") or "").strip().lower() in HIDDEN_LOCATIONS:
                continue
            inventory.append({
                "set": (row.get("Set") or "").strip(),
                "card": (row.get("Card") or "").strip(),
                "rarity": (row.get("Rarity") or "").strip(),
                "qty": int(num(row.get("Qty")) or 0),
                "price": num(row.get("Unit Price ($)")),
                "notes": (row.get("Notes") or "").strip(),
            })

    out = "window.MTG_DATA = " + json.dumps(
        {"cards": cards, "inventory": inventory}, separators=(",", ":")) + ";\n"
    (DATA / "bundle.js").write_text(out)
    print(f"bundle.js: {len(cards)} featured, {len(inventory)} inventory rows")


if __name__ == "__main__":
    main()
