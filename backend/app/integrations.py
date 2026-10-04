"""Phase 13 — integrations: honest status + real exports. No simulated filings.

Anything not officially available returns status 'not_available' with a reason —
never a fake success. Real: CSV/JSON self-exports (Tally/Excel-compatible CSV).
"""
import csv
import io


INTEGRATIONS = [
    {"key": "excel_export", "label": "Excel/CSV export", "status": "available",
     "note": "CSV opens in Excel; no paid dependency."},
    {"key": "tally", "label": "Tally interoperability", "status": "not_available",
     "note": "Adapter planned. Export CSV and import into Tally meanwhile."},
    {"key": "einvoice", "label": "e-Invoice", "status": "not_available",
     "note": "Only when official free access exists. DEMO flows would be labelled."},
    {"key": "ewaybill", "label": "e-Way Bill", "status": "not_available",
     "note": "Only when official free access exists."},
    {"key": "whatsapp", "label": "WhatsApp Business API", "status": "not_available",
     "note": "Core uses browser/system share + copy/download. Adapter interface reserved."},
    {"key": "email", "label": "Email provider", "status": "not_available",
     "note": "Core uses in-app + browser notifications. Provider adapter reserved."},
]


def integration_status() -> list[dict]:
    return [dict(i) for i in INTEGRATIONS]


def to_csv(rows: list[dict], columns: list[str]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=columns, extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow({c: r.get(c, "") for c in columns})
    return buf.getvalue()


TX_COLUMNS = ["date", "description", "amount", "transaction_type", "category",
              "source", "tax_deducted"]
INVOICE_COLUMNS = ["number", "customer", "date", "due_date", "taxable_value",
                   "total_tax", "grand_total", "status"]
PARTY_COLUMNS = ["name", "kind", "gstin", "phone", "address"]
