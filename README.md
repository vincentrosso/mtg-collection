# MTG Collection site

Static for-sale page: featured cards, lots, searchable inventory. No backend.

## Edit → rebuild

Data lives in `data/high_value.json` and `data/full_inventory.csv`. After any edit:

```bash
python3 build.py      # writes data/bundle.js (strips Location/Value, drops "Given to Thomas" rows)
open index.html       # works straight from disk
```

- **Mark a card sold:** set its `status` to `sold` (or `pending`) in `data/high_value.json`, then rebuild.
  Sold tiles stay on the page, greyed out.
- **Set a price:** set `asking_price` (a number). `null` shows "Make an offer".
- **Add photos:** drop `underground-sea.jpg` (and `underground-sea-back.jpg`) into `photos/`, then set
  that card's `photo` to `"underground-sea.jpg"`. Use your own photos only.

## Deploy

Not chosen yet. **Upload only** `index.html`, `styles.css`, `app.js`, `data/bundle.js`, `photos/` —
never `data/full_inventory.csv` or `data/high_value.json`, which still hold the internal Location
and Value columns.
