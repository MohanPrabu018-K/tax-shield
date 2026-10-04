"""Phase 12 — inventory + POS: products, stock moves, cart-to-bill.

Bill posts: stock decrement + sales invoice totals (via invoicing.compute_totals)
+ accounting legs (via invoicing.invoice_journals). No paid hardware needed.
"""


def _r(x) -> float:
    return round(float(x or 0), 2)


def stock_on_hand(moves: list[dict], product_id: str) -> float:
    bal = 0.0
    for m in moves:
        if str(m.get("product_id")) != str(product_id):
            continue
        q = float(m.get("qty", 0))
        if m.get("type") in ("purchase", "adjust_in"):
            bal += q
        elif m.get("type") in ("sale", "adjust_out"):
            bal -= q
    return _r(bal)


def build_bill(cart: list[dict], products: dict, inter_state: bool = False) -> dict:
    """cart: [{sku, qty}]. Returns items + totals or raises (unknown SKU, short stock)."""
    from app.invoicing import compute_totals

    items = []
    for line in cart:
        p = products.get(line.get("sku", ""))
        if not p:
            raise ValueError(f"Unknown SKU {line.get('sku')}")
        qty = float(line.get("qty", 0))
        if qty <= 0:
            raise ValueError("Qty must be positive")
        if _r(p.get("stock", 0)) < qty:
            raise ValueError(f"Insufficient stock for {p.get('name')} ({p.get('stock')} left)")
        items.append({"desc": p.get("name"), "hsn": p.get("hsn", ""),
                      "qty": qty, "rate": float(p.get("rate", 0)),
                      "discount_pct": 0, "gst_rate": float(p.get("gst_rate", 0))})
    totals = compute_totals(items, inter_state)
    return {"items": items, "inter_state": inter_state, **totals}


def low_stock(products: list[dict]) -> list[dict]:
    return [{"sku": p.get("sku"), "name": p.get("name"),
             "stock": p.get("stock", 0), "reorder_at": p.get("reorder_at", 5)}
            for p in products
            if float(p.get("stock", 0)) <= float(p.get("reorder_at", 5))]
