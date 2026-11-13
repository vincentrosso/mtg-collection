(function () {
  const data = window.MTG_DATA;
  const table = document.getElementById("list");
  if (!data) { table.insertAdjacentHTML("afterend", "<p>Data missing — run: python3 build.py</p>"); return; }

  const money = (n) => n == null ? "—"
    : "$" + n.toLocaleString("en-US", { minimumFractionDigits: n < 100 ? 2 : 0, maximumFractionDigits: n < 100 ? 2 : 0 });
  const el = (tag, cls, text) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  };

  // Groups: Featured first, then each set by line count.
  const featured = [...data.cards]
    .sort((a, b) => (b.est_total || 0) - (a.est_total || 0))
    .map((c) => ({
      card: c.card, set: c.set, rarity: "", qty: c.qty,
      price: c.asking_price != null ? c.asking_price : c.est_each,
      notes: c.notes || "", status: (c.status || "available").toLowerCase(),
    }));
  const bySet = {};
  for (const r of data.inventory) (bySet[r.set || "(unknown set)"] ||= []).push({ ...r, status: "" });
  const setNames = Object.keys(bySet).sort((a, b) => bySet[b].length - bySet[a].length || a.localeCompare(b));
  for (const s of setNames) bySet[s].sort((a, b) => (b.price ?? -1) - (a.price ?? -1) || a.card.localeCompare(b.card));
  const groups = [{ name: "Featured", rows: featured }, ...setNames.map((s) => ({ name: s, rows: bySet[s] }))];

  const sel = document.getElementById("setFilter");
  groups.forEach((g) => sel.appendChild(new Option(g.name + " (" + g.rows.length + ")", g.name)));

  const q = document.getElementById("q");
  const count = document.getElementById("count");

  function render() {
    const term = q.value.trim().toLowerCase();
    const only = sel.value;
    table.querySelectorAll("tbody").forEach((b) => b.remove());
    let lines = 0, cards = 0;
    for (const g of groups) {
      if (only && g.name !== only) continue;
      const rows = g.rows.filter((r) => !term ||
        r.card.toLowerCase().includes(term) || r.notes.toLowerCase().includes(term));
      if (!rows.length) continue;
      const tb = document.createElement("tbody");
      const qty = rows.reduce((s, r) => s + (r.qty || 0), 0);
      const hr = el("tr", "group");
      const th = el("th", "", g.name);
      th.colSpan = 6;
      th.appendChild(el("span", "gmeta", rows.length + " lines · " + qty.toLocaleString("en-US") + " cards"));
      hr.appendChild(th);
      tb.appendChild(hr);
      for (const r of rows) {
        const tr = el("tr", r.status === "sold" ? "sold" : "");
        const name = el("td", "", r.card);
        if (r.status === "sold" || r.status === "pending") name.appendChild(el("span", "badge " + r.status, r.status));
        tr.appendChild(name);
        tr.appendChild(el("td", "c-set", r.set));
        tr.appendChild(el("td", "c-r", r.rarity));
        tr.appendChild(el("td", "n", String(r.qty)));
        tr.appendChild(el("td", "n", money(r.price)));
        tr.appendChild(el("td", "c-notes", r.notes));
        tb.appendChild(tr);
      }
      table.appendChild(tb);
      lines += rows.length; cards += qty;
    }
    count.textContent = lines + " lines · " + cards.toLocaleString("en-US") + " cards";
  }

  q.addEventListener("input", render);
  sel.addEventListener("change", render);
  render();
})();
