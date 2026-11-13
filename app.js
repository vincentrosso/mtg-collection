(function () {
  const data = window.MTG_DATA;
  if (!data) {
    document.getElementById("grid").textContent = "Data missing — run: python3 build.py";
    return;
  }
  const money = (n) => "$" + Math.round(n).toLocaleString("en-US");
  const el = (tag, cls, text) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  };

  // ---- Featured grid ----
  const grid = document.getElementById("grid");
  const cards = [...data.cards].sort((a, b) => (b.est_total || 0) - (a.est_total || 0));
  for (const c of cards) {
    const status = (c.status || "available").toLowerCase();
    const tile = el("article", "tile" + (status === "sold" ? " is-sold" : ""));
    if (c.photo) {
      const ph = el("div", "ph");
      const img = new Image();
      img.src = "photos/" + c.photo;
      img.alt = c.card;
      img.loading = "lazy";
      img.onerror = () => ph.remove();
      ph.appendChild(img);
      tile.appendChild(ph);
    }

    const body = el("div", "body");
    body.appendChild(el("div", "name", c.card));
    body.appendChild(el("div", "meta", c.set + " · Qty " + c.qty));
    if (c.notes) body.appendChild(el("div", "note", c.notes));
    const foot = el("div", "foot");
    let priceEl;
    if (c.asking_price != null) priceEl = el("span", "price", money(c.asking_price) + (c.qty > 1 ? " ea" : ""));
    else if (c.est_each) priceEl = el("span", "price", "~" + money(c.est_each) + (c.qty > 1 ? " ea" : ""));
    else priceEl = el("span", "price offer", "Make an offer");
    foot.appendChild(priceEl);
    foot.appendChild(el("span", "badge " + status, status));
    body.appendChild(foot);
    tile.appendChild(body);
    grid.appendChild(tile);
  }

  // ---- Inventory table ----
  const rows = data.inventory;
  const q = document.getElementById("q");
  const setSel = document.getElementById("setFilter");
  const tbody = document.querySelector("#inv tbody");
  const count = document.getElementById("count");
  const ths = document.querySelectorAll("#inv th");

  const setCounts = {};
  for (const r of rows) { const s = r.set || "(unknown)"; setCounts[s] = (setCounts[s] || 0) + 1; }
  Object.keys(setCounts).sort((a, b) => setCounts[b] - setCounts[a] || a.localeCompare(b))
    .forEach((s) => setSel.appendChild(new Option(s + " (" + setCounts[s] + ")", s)));

  let sortKey = "card", sortDir = 1;

  function render() {
    const term = q.value.trim().toLowerCase();
    const set = setSel.value;
    const out = rows.filter((r) =>
      (!set || (r.set || "(unknown)") === set) &&
      (!term || r.card.toLowerCase().includes(term) || r.notes.toLowerCase().includes(term)));
    out.sort((a, b) => {
      const x = a[sortKey], y = b[sortKey];
      if (typeof x === "number" || typeof y === "number") return ((x ?? -1) - (y ?? -1)) * sortDir;
      return String(x).localeCompare(String(y)) * sortDir;
    });
    const frag = document.createDocumentFragment();
    for (const r of out) {
      const tr = document.createElement("tr");
      tr.appendChild(el("td", "", r.card));
      tr.appendChild(el("td", "", r.set));
      tr.appendChild(el("td", "", r.rarity));
      tr.appendChild(el("td", "n", String(r.qty)));
      tr.appendChild(el("td", "n", r.price != null ? "$" + r.price.toFixed(2) : "—"));
      tr.appendChild(el("td", "notes", r.notes));
      frag.appendChild(tr);
    }
    tbody.replaceChildren(frag);
    const cardsTotal = out.reduce((s, r) => s + r.qty, 0);
    count.textContent = out.length + " lines · " + cardsTotal.toLocaleString("en-US") + " cards";
    ths.forEach((th) => th.setAttribute("aria-sort",
      th.dataset.k === sortKey ? (sortDir > 0 ? "ascending" : "descending") : "none"));
  }

  ths.forEach((th) => th.addEventListener("click", () => {
    const k = th.dataset.k;
    if (k === sortKey) sortDir = -sortDir;
    else { sortKey = k; sortDir = (k === "qty" || k === "price") ? -1 : 1; }
    render();
  }));
  q.addEventListener("input", render);
  setSel.addEventListener("change", render);
  render();
})();
