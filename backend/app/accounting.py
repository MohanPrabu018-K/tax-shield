"""Phase 3 — deterministic double-entry accounting. No AI in this path.

Chart of Accounts + Journals (idempotent) + Ledger + Trial Balance + P&L +
Balance Sheet + Cash Flow. All money rounded to 2dp. Pure functions take
plain dicts so they are unit-testable without Mongo.
"""
from datetime import datetime

ASSET, LIABILITY, EQUITY, INCOME, EXPENSE = "asset", "liability", "equity", "income", "expense"

# code, name, type, cashflow class (operating/investing/financing/none)
COA_SEED = [
    ("1000", "Cash", ASSET, "operating"), ("1010", "Bank - Primary", ASSET, "operating"),
    ("1020", "UPI Clearing", ASSET, "operating"), ("1100", "Accounts Receivable", ASSET, "operating"),
    ("1200", "GST Input Credit", ASSET, "operating"), ("1210", "TDS Receivable", ASSET, "operating"),
    ("1300", "Inventory", ASSET, "investing"), ("1400", "Fixed Assets", ASSET, "investing"),
    ("1410", "Accumulated Depreciation", ASSET, "investing"), ("1500", "Other Assets", ASSET, "operating"),
    ("2000", "Accounts Payable", LIABILITY, "operating"), ("2100", "GST Output Tax", LIABILITY, "operating"),
    ("2110", "GST Payable (Net)", LIABILITY, "operating"), ("2200", "TDS Payable", LIABILITY, "operating"),
    ("2300", "Tax Payable", LIABILITY, "operating"), ("2400", "Loans", LIABILITY, "financing"),
    ("2500", "Other Liabilities", LIABILITY, "operating"),
    ("3000", "Owner Capital", EQUITY, "financing"), ("3100", "Owner Drawings", EQUITY, "financing"),
    ("3200", "Retained Earnings", EQUITY, "none"),
    ("4000", "Sales Revenue", INCOME, "operating"), ("4100", "Service Revenue", INCOME, "operating"),
    ("4200", "Other Income", INCOME, "operating"),
    ("5000", "Cost of Goods Sold", EXPENSE, "operating"), ("5100", "Rent", EXPENSE, "operating"),
    ("5200", "Salaries", EXPENSE, "operating"), ("5300", "Utilities", EXPENSE, "operating"),
    ("5400", "Travel", EXPENSE, "operating"), ("5500", "Office", EXPENSE, "operating"),
    ("5600", "Insurance", EXPENSE, "operating"), ("5700", "Loan Interest", EXPENSE, "operating"),
    ("5800", "Depreciation", EXPENSE, "operating"), ("5900", "Other Expenses", EXPENSE, "operating"),
]

CONTRA = {"1410", "3100"}  # debit-normal equity/asset offsets
COA = {c: {"code": c, "name": n, "type": t, "cashflow": cf} for c, n, t, cf in COA_SEED}


def _r(x) -> float:
    return round(float(x or 0), 2)


def validate_journal(lines: list[dict]) -> None:
    """Raise ValueError unless lines form a balanced entry."""
    if len(lines) < 2:
        raise ValueError("Journal needs at least 2 lines")
    dr = cr = 0.0
    for ln in lines:
        if ln.get("account_code") not in COA:
            raise ValueError(f"Unknown account {ln.get('account_code')}")
        d, c = _r(ln.get("debit")), _r(ln.get("credit"))
        if d < 0 or c < 0 or (d == 0 and c == 0) or (d > 0 and c > 0):
            raise ValueError("Each line must have exactly one of debit/credit positive")
        dr += d
        cr += c
    if round(dr - cr, 2) != 0:
        raise ValueError(f"Unbalanced journal: Dr {dr} != Cr {cr}")


def _active(journals: list[dict]) -> list[dict]:
    """Posted entries only. Reversals are separate offsetting entries (audit
    trail preserved); their net effect cancels naturally in the balances."""
    return [j for j in journals if j.get("status", "posted") == "posted"]


def trial_balance(accounts: list[dict], journals: list[dict]) -> dict:
    bal: dict[str, dict] = {a["code"]: {"code": a["code"], "name": a["name"],
                                        "type": a["type"], "debit": 0.0, "credit": 0.0}
                            for a in accounts}
    for j in _active(journals):
        for ln in j.get("lines", []):
            b = bal.get(ln["account_code"])
            if b:
                b["debit"] = _r(b["debit"] + ln.get("debit", 0))
                b["credit"] = _r(b["credit"] + ln.get("credit", 0))
    rows = [b for b in bal.values() if b["debit"] or b["credit"]]
    td = _r(sum(b["debit"] for b in rows))
    tc = _r(sum(b["credit"] for b in rows))
    return {"rows": rows, "total_debit": td, "total_credit": tc, "balanced": td == tc}


def _net(row: dict) -> float:
    return _r(row["debit"] - row["credit"])


def profit_and_loss(accounts: list[dict], journals: list[dict]) -> dict:
    tb = trial_balance(accounts, journals)
    by_code = {r["code"]: r for r in tb["rows"]}
    rev = _r(sum(_net(by_code[c]) * -1 for c in by_code if COA[c]["type"] == INCOME))
    exp = _r(sum(_net(by_code[c]) for c in by_code if COA[c]["type"] == EXPENSE))
    cogs = _r(_net(by_code["5000"]) if "5000" in by_code else 0)
    gross = _r(rev - cogs)
    return {"revenue": rev, "cogs": cogs, "gross_profit": gross,
            "expenses": _r(exp - cogs) if cogs else exp,
            "total_expenses": exp, "net_profit": _r(rev - exp),
            "balanced": tb["balanced"]}


def balance_sheet(accounts: list[dict], journals: list[dict], net_profit: float = 0) -> dict:
    tb = trial_balance(accounts, journals)
    by_code = {r["code"]: r for r in tb["rows"]}
    assets = _r(sum(_net(by_code[c]) * (-1 if c in CONTRA else 1)
                    for c in by_code if COA[c]["type"] == ASSET))
    liab = _r(sum(_net(by_code[c]) * -1 for c in by_code if COA[c]["type"] == LIABILITY))
    eq = _r(sum(_net(by_code[c]) * (-1 if c in CONTRA else 1)
                for c in by_code if COA[c]["type"] == EQUITY))
    eq_total = _r(eq + net_profit)
    return {"assets": assets, "liabilities": liab, "equity": eq,
            "net_profit": net_profit, "equity_total": eq_total,
            "balanced": _r(assets) == _r(liab + eq_total)}


def cash_flow(journals: list[dict]) -> dict:
    """Cash movement in 1000/1010/1020 grouped by offset-account class. Simplified
    direct view: operating / investing / financing + net change."""
    out = {"operating": 0.0, "investing": 0.0, "financing": 0.0}
    for j in _active(journals):
        for ln in j.get("lines", []):
            if ln["account_code"] not in ("1000", "1010", "1020"):
                continue
            delta = _r(ln.get("debit", 0) - ln.get("credit", 0))
            others = [x for x in j["lines"] if x["account_code"] not in ("1000", "1010", "1020")]
            cls = COA.get(others[0]["account_code"], {}).get("cashflow", "operating") if others else "operating"
            if cls == "none":
                cls = "operating"
            out[cls] = _r(out[cls] + delta)
    out["net_change"] = _r(out["operating"] + out["investing"] + out["financing"])
    return out


# Transaction -> journals ("one transaction -> everything", accounting leg).
# Income categories post Dr Bank / Cr revenue; expenses Dr expense / Cr Bank.
TX_POSTING = {
    "salary": ("4100", INCOME), "freelance": ("4100", INCOME), "business": ("4000", INCOME),
    "rental": ("4200", INCOME), "bank_interest": ("4200", INCOME), "dividends": ("4200", INCOME),
    "capital_gains": ("4200", INCOME), "other": ("4200", INCOME),
}
EXP_POSTING = {"fuel": "5900", "travel": "5400", "office": "5500", "utilities": "5300",
               "insurance": "5600", "loan_interest": "5700", "education": "5900",
               "medical": "5900", "donations": "5900", "rent": "5100", "retirement": "5900"}


def journals_for_transaction(tx: dict) -> list[dict] | None:
    """Return [journal-lines] auto-posting for a transaction, or None if N/A."""
    amt = _r(tx.get("amount", 0))
    if amt <= 0:
        return None
    ttype = (tx.get("transaction_type") or "").lower()
    if ttype == "income":
        rev, _ = TX_POSTING.get((tx.get("category") or "other"), ("4200", INCOME))
        return [{"account_code": "1010", "debit": amt, "credit": 0},
                {"account_code": rev, "debit": 0, "credit": amt}]
    if ttype == "expense":
        exp = EXP_POSTING.get((tx.get("category") or "other"), "5900")
        return [{"account_code": exp, "debit": amt, "credit": 0},
                {"account_code": "1010", "debit": 0, "credit": amt}]
    return None
