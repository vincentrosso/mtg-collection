#!/usr/bin/env python3
"""Render highlights.pdf (2 pages) from data/bundle.js via headless Chrome.

Page 1: featured cards. Page 2: lots + top cards in each set.
Reads only the public bundle, so nothing internal can leak into the PDF.
"""
import html
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SITE = "https://vincentrosso.github.io/mtg-collection/"
TOP_PER_SET = 9

LOTS = [
    ("Revised complete set + extras", "A complete Revised (1994) set, plus extra copies."),
    ("The Dark — complete set", "All 119 cards, kept together in a binder."),
    ("Fallen Empires lot", "About 920 cards."),
    ("Revised commons & uncommons", "About 1,300, counted."),
    ("Bulk", "About 1,250 — Kamigawa, Ravnica, The Dark."),
]


def money(n):
    if n is None:
        return "—"
    return f"${n:,.2f}" if n < 100 else f"${n:,.0f}"


def base(name):
    return re.sub(r"\s*\(.*?\)", "", name).strip().lower()


def norm_set(s):
    s = re.sub(r"\s*\(1994\)$", "", s or "").strip()
    return s or "Other"


def main():
    raw = (ROOT / "data" / "bundle.js").read_text()
    data = json.loads(raw[raw.index("{"):raw.rindex("}") + 1])
    e = html.escape

    featured = sorted(data["cards"], key=lambda c: c.get("est_total") or 0, reverse=True)
    feat_names = {base(c["card"]) for c in featured}
    rows1 = []
    for c in featured:
        price = c["asking_price"] if c.get("asking_price") is not None else c.get("est_each")
        status = (c.get("status") or "available").lower()
        badge = f' <span class="b">{e(status)}</span>' if status in ("sold", "pending") else ""
        rows1.append(
            f'<tr class="{"sold" if status == "sold" else ""}"><td>{e(c["card"])}{badge}</td>'
            f'<td>{e(c["set"])}</td><td class="n">{c["qty"]}</td>'
            f'<td class="n">{money(price)}</td><td class="m">{e(c.get("notes") or "")}</td></tr>')
    feat_cards = sum(c["qty"] for c in featured)

    by_set = defaultdict(list)
    for r in data["inventory"]:
        by_set[norm_set(r["set"])].append(r)
    sets = sorted(by_set.items(), key=lambda kv: -sum(r["qty"] for r in kv[1]))
    blocks = []
    for name, rows in sets:
        qty = sum(r["qty"] for r in rows)
        top = sorted((r for r in rows if r["price"] and base(r["card"]) not in feat_names),
                     key=lambda r: -r["price"])[:TOP_PER_SET]
        if not top and qty < 20:
            continue
        items = "".join(
            f'<li><span>{e(r["card"])}{" ×" + str(r["qty"]) if r["qty"] > 1 else ""}</span>'
            f'<span class="n">{money(r["price"])}</span></li>' for r in top)
        blocks.append(
            f'<div class="set"><h3>{e(name)}<small>{qty:,} cards</small></h3>'
            f'<ul>{items or "<li><span>Commons / bulk</span></li>"}</ul></div>')
    lots = "".join(f"<div class='lot'><b>{e(t)}</b> — {e(d)}</div>" for t, d in LOTS)

    doc = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size: letter; margin: 0.45in 0.5in; }}
* {{ box-sizing: border-box; }}
body {{ font: 9.6pt/1.3 -apple-system, "Helvetica Neue", Arial, sans-serif; color: #1c1c1c; margin: 0; }}
.page {{ page-break-after: always; }} .page:last-child {{ page-break-after: auto; }}
h1 {{ font-size: 19pt; margin: 0; letter-spacing: -.01em; }}
.sub {{ color: #555; margin: 2px 0 10px; }}
h2 {{ font-size: 12pt; margin: 0 0 6px; padding-bottom: 3px; border-bottom: 2px solid #1f3557; color: #1f3557; }}
h2 small {{ font-weight: 400; color: #666; font-size: 9pt; margin-left: 8px; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ padding: 3.4px 6px; border-bottom: .5pt solid #ddd; text-align: left; vertical-align: top; }}
th {{ background: #eef1f6; font-size: 8.6pt; }}
tr:nth-child(even) td {{ background: #fafafa; }}
.n {{ text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }}
.m {{ color: #666; font-size: 8.6pt; }}
tr.sold td {{ color: #999; text-decoration: line-through; }}
.b {{ font-size: 7pt; font-weight: 700; text-transform: uppercase; background: #fdf1dc; color: #8a5a00; padding: 0 4px; border-radius: 6px; }}
.lots {{ display: grid; grid-template-columns: 1fr 1fr; gap: 3px 18px; margin-bottom: 12px; }}
.lot {{ padding: 2px 0; }}
.sets {{ columns: 3; column-gap: 16px; }}
.set {{ break-inside: avoid; margin-bottom: 8px; }}
.set h3 {{ font-size: 10pt; margin: 0 0 2px; display: flex; justify-content: space-between; border-bottom: .5pt solid #bbb; }}
.set h3 small {{ font-weight: 400; color: #666; font-size: 8pt; }}
.set ul {{ list-style: none; margin: 0; padding: 0; }}
.set li {{ display: flex; justify-content: space-between; gap: 6px; font-size: 8.8pt; padding: 1px 0; }}
.foot {{ color: #777; font-size: 8pt; margin-top: 8px; }}
</style></head><body>
<section class="page">
  <h1>Vintage MTG Collection</h1>
  <div class="sub">1994 Revised · Legends · The Dark · Antiquities — personal collection, owned since 1994, raw (ungraded). Prices are market estimates per card.</div>
  <h2>Featured cards<small>{len(featured)} lines · {feat_cards} cards</small></h2>
  <table><thead><tr><th>Card</th><th>Set</th><th class="n">Qty</th><th class="n">Price ea.</th><th>Notes</th></tr></thead>
  <tbody>{"".join(rows1)}</tbody></table>
  <div class="foot">Full list: {SITE}</div>
</section>
<section class="page">
  <h2>Lots</h2>
  <div class="lots">{lots}</div>
  <h2>Highlights by set<small>top cards beyond the featured list</small></h2>
  <div class="sets">{"".join(blocks)}</div>
  <div class="foot">Full searchable inventory: {SITE} · Not affiliated with Wizards of the Coast.</div>
</section>
</body></html>"""

    src = ROOT / "highlights.html"
    out = ROOT / "highlights.pdf"
    src.write_text(doc)
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={out}", src.as_uri()],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    src.unlink()
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
