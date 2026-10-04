"""Phases 3-13 tests — deterministic, no DB. Run: py -m pytest backend/tests -q."""
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.accounting import (COA, validate_journal, trial_balance, profit_and_loss,
                            balance_sheet, cash_flow, journals_for_transaction)
from app.finance import (fingerprint, find_duplicates, suggest_category, age_buckets,
                         receivables_payables_summary)
from app.invoicing import compute_totals, next_number, transition, apply_payment, invoice_journals
from app.gst import validate_gstin, split_gst, validate_hsn, gstr1_summary, gstr3b_summary, gst_reconcile
from app.tds import compute_tds, tds_payable_summary, TDS_SECTIONS
from app.taxplus import classify_gain, capital_gain, itr_applicability, planning_opportunities
from app.docsintel import classify_document, check_evidence, verify_transition, link_summary
from app.intel import (month_end_close, what_changed, detect_anomalies, forecast_cash,
                       business_health)
from app.practice import review_transition, practice_overview
from app.inventory import stock_on_hand, build_bill, low_stock
from app.integrations import integration_status, to_csv
from app import feature_flags as ff


def _accts():
    return [{"code": c, "name": v["name"], "type": v["type"]} for c, v in COA.items()]


def _j(lines, _id="a"):
    return {"_id": _id, "lines": lines, "status": "posted"}


# ---- Phase 3 ----
def test_coa_balanced_types():
    types = {v["type"] for v in COA.values()}
    assert {"asset", "liability", "equity", "income", "expense"} <= types
    assert len(COA) >= 30


def test_journal_must_balance():
    with pytest.raises(ValueError):
        validate_journal([{"account_code": "1010", "debit": 100, "credit": 0}])
    with pytest.raises(ValueError):
        validate_journal([{"account_code": "1010", "debit": 100, "credit": 0},
                          {"account_code": "4000", "debit": 0, "credit": 99}])
    validate_journal([{"account_code": "1010", "debit": 100, "credit": 0},
                      {"account_code": "4000", "debit": 0, "credit": 100}])


def test_journal_unknown_account():
    with pytest.raises(ValueError):
        validate_journal([{"account_code": "9999", "debit": 1, "credit": 0},
                          {"account_code": "4000", "debit": 0, "credit": 1}])


def test_trial_balance_zero_sum():
    tb = trial_balance(_accts(), [
        _j([{"account_code": "1010", "debit": 1000, "credit": 0},
            {"account_code": "4000", "debit": 0, "credit": 1000}], "1"),
        _j([{"account_code": "5100", "debit": 200, "credit": 0},
            {"account_code": "1010", "debit": 0, "credit": 200}], "2")])
    assert tb["balanced"] and tb["total_debit"] == tb["total_credit"] == 1200


def test_reversed_excluded():
    js = [_j([{"account_code": "1010", "debit": 500, "credit": 0},
              {"account_code": "4000", "debit": 0, "credit": 500}], "1"),
          {"_id": "2", "status": "posted", "reverses_id": "1",
           "lines": [{"account_code": "4000", "debit": 500, "credit": 0},
                     {"account_code": "1010", "debit": 0, "credit": 500}]}]
    tb = trial_balance(_accts(), js)
    # audit trail kept (both entries visible) but balances net to zero
    assert tb["balanced"] and tb["total_debit"] == 1000
    bank = next(r for r in tb["rows"] if r["code"] == "1010")
    assert round(bank["debit"] - bank["credit"], 2) == 0


def test_pl_and_bs():
    js = [_j([{"account_code": "1010", "debit": 1000, "credit": 0},
              {"account_code": "4000", "debit": 0, "credit": 1000}], "1"),
          _j([{"account_code": "5100", "debit": 300, "credit": 0},
              {"account_code": "1010", "debit": 0, "credit": 300}], "2")]
    pl = profit_and_loss(_accts(), js)
    assert pl == {"revenue": 1000, "cogs": 0, "gross_profit": 1000, "expenses": 300,
                  "total_expenses": 300, "net_profit": 700, "balanced": True}
    bs = balance_sheet(_accts(), js, pl["net_profit"])
    assert bs["balanced"] and bs["assets"] == 700


def test_cash_flow_buckets():
    js = [_j([{"account_code": "1010", "debit": 1000, "credit": 0},
              {"account_code": "4000", "debit": 0, "credit": 1000}], "1"),
          _j([{"account_code": "1400", "debit": 400, "credit": 0},
              {"account_code": "1010", "debit": 0, "credit": 400}], "2")]
    cf = cash_flow(js)
    assert cf["operating"] == 1000 and cf["investing"] == -400
    assert cf["net_change"] == 600


def test_auto_post_tx():
    assert journals_for_transaction({"transaction_type": "income", "category": "salary",
                                     "amount": 50000})[0]["account_code"] == "1010"
    assert journals_for_transaction({"transaction_type": "expense", "category": "rent",
                                     "amount": 10000})[0]["account_code"] == "5100"
    assert journals_for_transaction({"transaction_type": "transfer", "amount": 5}) is None
    assert journals_for_transaction({"transaction_type": "income", "amount": -1}) is None


# ---- Phase 4 ----
def test_fingerprint_stable():
    a = {"date": "2024-06-01", "description": "  Salary  Credit ", "amount": 50000}
    b = {"date": "2024-06-01", "description": "salary credit", "amount": 50000.0}
    assert fingerprint(a) == fingerprint(b)


def test_dedup_within_file_and_existing():
    rows = [{"date": "2024-06-01", "description": "x", "amount": 10},
            {"date": "2024-06-01", "description": "x", "amount": 10},
            {"date": "2024-06-02", "description": "y", "amount": 5}]
    uniq, dups = find_duplicates(rows, {fingerprint(rows[2])})
    assert len(uniq) == 1 and len(dups) == 2


def test_suggest_category():
    s = suggest_category("Uber trip to client")
    assert s["category"] == "travel" and s["gst_relevant"] is True
    s2 = suggest_category("zzzz unknown")
    assert s2["needs_review"] is True


def test_aging_buckets():
    now = datetime.utcnow()
    items = [{"due_date": now - timedelta(days=45), "balance": 100, "status": "sent"},
             {"due_date": now + timedelta(days=5), "balance": 50, "status": "sent"},
             {"due_date": now - timedelta(days=1), "balance": 10, "status": "paid"}]
    b = age_buckets(items, now)
    assert b["d31_60"] == 100 and b["current"] == 50 and b["total"] == 150


# ---- Phase 5 ----
def test_invoice_totals_intra():
    t = compute_totals([{"qty": 2, "rate": 1000, "discount_pct": 10, "gst_rate": 18}])
    assert t["taxable_value"] == 1800 and t["cgst"] == 162 and t["sgst"] == 162
    assert t["grand_total"] == 2124


def test_invoice_totals_inter():
    t = compute_totals([{"qty": 1, "rate": 1000, "discount_pct": 0, "gst_rate": 18}],
                       inter_state=True)
    assert t["igst"] == 180 and t["cgst"] == 0 and t["grand_total"] == 1180


def test_invoice_bad_item():
    with pytest.raises(ValueError):
        compute_totals([{"qty": 0, "rate": 100, "gst_rate": 18}])


def test_numbering_and_lifecycle():
    n, s = next_number(0, "INV", "2024-25")
    assert n == "INV-2024-25-0001" and s == 1
    assert transition("draft", "sent") == "sent"
    with pytest.raises(ValueError):
        transition("paid", "sent")


def test_payment_flow():
    inv = {"grand_total": 1000, "paid_total": 0, "status": "sent"}
    inv = apply_payment(inv, 400)
    assert inv["status"] == "partially_paid" and inv["balance"] == 600
    inv = apply_payment(inv, 600)
    assert inv["status"] == "paid"
    with pytest.raises(ValueError):
        apply_payment(inv, 1)


def test_invoice_journals_balance():
    inv = {"grand_total": 1180, "total_tax": 180, "kind": "sale"}
    lines = invoice_journals(inv)
    assert round(sum(l["debit"] for l in lines) - sum(l["credit"] for l in lines), 2) == 0


# ---- Phase 6 ----
def test_gstin_checksum():
    # Verified fixtures (mod-36, GSTN-published algorithm).
    assert validate_gstin("27AAPFU0939F1ZV")["valid"] is True
    assert validate_gstin("33AAACC1206D1ZN")["valid"] is True
    assert validate_gstin("27AAACR5055K1Z7")["valid"] is True
    assert validate_gstin("27AAPFU0939F1ZA")["valid"] is False  # bad check digit
    assert validate_gstin("bogus")["valid"] is False


def test_gst_split():
    s = split_gst(1000, 18, False)
    assert s["cgst"] == 90 and s["sgst"] == 90 and s["total"] == 180
    assert validate_hsn("9983") and validate_hsn("123456") and not validate_hsn("12")


def test_gstr_summaries():
    inv = {"kind": "sale", "status": "sent",
           "items": [{"gst_rate": 18}], "computed": {"lines": [{"taxable": 1000, "cgst": 90, "sgst": 90, "igst": 0}]},
           "total_tax": 180}
    g1 = gstr1_summary([inv])
    assert g1["total_tax"] == 180 and g1["invoice_count"] == 1
    g3 = gstr3b_summary([inv], [{"status": "sent", "total_tax": 80}])
    assert g3 == {"type": "GSTR-3B-preparation", "output_tax": 180, "itc_available": 80,
                  "net_payable": 100, "disclaimer": g3["disclaimer"]}
    assert gst_reconcile(180, 180)["status"] == "matched"
    assert gst_reconcile(180, 200)["status"] == "mismatched"


def test_tds_compute():
    r = compute_tds("194J", 100000)
    assert r["tds"] == 10000 and r["applicable"] is True
    assert compute_tds("194J", 1000)["applicable"] is False  # below threshold
    assert compute_tds("194J", 100000, False)["tds"] == 20000  # no PAN -> 20%
    assert compute_tds("192", 500000)["rate"] is None
    with pytest.raises(ValueError):
        compute_tds("999", 100)
    s = tds_payable_summary([{"tds": 100, "status": "pending"}, {"tds": 50, "status": "paid"}])
    assert s == {"payable": 100, "paid": 50, "count": 2}


# ---- Phase 7 ----
def test_gains_classify():
    g = capital_gain(200000, 280000, "mutual_fund", datetime(2022, 5, 1), datetime(2024, 11, 10))
    assert g == {"gain": 80000, "classification": "LTCG", "asset_type": "mutual_fund",
                 "holding": "2022-05-01 to 2024-11-10", "note": g["note"]}
    assert classify_gain("equity", datetime(2024, 1, 1), datetime(2024, 6, 1)) == "STCG"


def test_itr_forms():
    assert itr_applicability({"income_categories": ["business"]})["form"] == "ITR-3"
    assert itr_applicability({"income_categories": ["business"], "presumptive": True})["form"] == "ITR-4"
    assert itr_applicability({"income_categories": ["salary"]})["form"] == "ITR-1"


def test_planning_needs_headroom():
    opps = planning_opportunities({"estimated_liability": 39000, "total_income": 900000,
                                   "taxable_income": 750000, "outstanding_tax": 0}, 150000, "old")
    assert opps == []
    opps2 = planning_opportunities({"estimated_liability": 50000, "total_income": 890000,
                                   "taxable_income": 790000, "outstanding_tax": 20000}, 100000, "old")
    assert any(o["title"] == "Use remaining 80C headroom" for o in opps2)
    assert any(o["title"] == "Schedule advance tax" for o in opps2)


# ---- Phase 8 ----
def test_doc_classify():
    c = classify_document("Form16_2024-25.pdf")
    assert c["document_type"] == "salary_slip" and c["confidence"] >= 0.65
    assert classify_document("random.xyz")["needs_review"] is True


def test_evidence_and_verify():
    assert check_evidence({"document_type": "invoice"}, ["invoice"])["complete"] is True
    assert check_evidence({"document_type": "invoice"}, ["invoice", "bank_statement"])["missing"] == ["bank_statement"]
    assert verify_transition("pending", "verified") == "verified"
    with pytest.raises(ValueError):
        verify_transition("verified", "pending")
    assert link_summary([{"event": "sale"}, {"event": "sale"}])["linked_events"] == 1


# ---- Phase 9 ----
def test_month_end():
    txs = [{"category": "salary", "amount": 100, "document_id": "d1"}]
    r = month_end_close(txs, [], [{"verification_status": "complete"}],
                        {"mismatched": 0, "missing": 0})
    assert r["closable"] is True
    r2 = month_end_close([{"amount": 5}], [], [], {"mismatched": 1, "missing": 0})
    assert r2["closable"] is False


def test_what_changed():
    w = what_changed({"revenue": 118}, {"revenue": 100})
    assert w["metrics"]["revenue"]["pct"] == 18.0
    assert w["top_drivers"][0] == "revenue"


def test_anomalies_and_forecast():
    txs = [{"_id": "1", "date": "2024-01-01", "description": "a", "amount": 10},
           {"_id": "2", "date": "2024-01-01", "description": "a", "amount": 10}]
    flags = detect_anomalies(txs)
    assert any(f["type"] == "duplicate" for f in flags)
    f = forecast_cash(10000, 5000, 2000, 1000, 500, 2)
    assert f["projection"][-1]["projected_balance"] == 13000
    assert f["assumptions"]["guarantee"] == "none — estimate only"


def test_health_explained():
    h = business_health(80, 90, 0, 0, "2024-25")
    assert h["score"] == int(0.5 * 80 + 0.3 * 90)
    assert h["tax_period"] == "2024-25" and "timestamp" in h


# ---- Phase 11/12/13 ----
def test_review_flow():
    from app.practice import review_transition as rt

    assert rt("auto", "needs_review") == "needs_review"
    assert rt("ca", "approved") == "approved"
    with pytest.raises(ValueError):
        rt("auto", "approved")
    ov = practice_overview([{}, {}], [{"status": "open"}], [{"state": "ca"}])
    assert ov == {"clients": 2, "open_tasks": 1, "pending_reviews": 1, "note": ov["note"]}


def test_inventory_bill():
    prods = {"SKU1": {"name": "Soap", "hsn": "3401", "rate": 100, "gst_rate": 18, "stock": 10}}
    bill = build_bill([{"sku": "SKU1", "qty": 2}], prods)
    assert bill["grand_total"] == 236
    with pytest.raises(ValueError):
        build_bill([{"sku": "SKU1", "qty": 99}], prods)
    with pytest.raises(ValueError):
        build_bill([{"sku": "NOPE", "qty": 1}], prods)
    assert stock_on_hand([{"product_id": "p1", "qty": 5, "type": "purchase"},
                          {"product_id": "p1", "qty": 2, "type": "sale"}], "p1") == 3
    assert low_stock([{"sku": "a", "name": "a", "stock": 2, "reorder_at": 5},
                      {"sku": "b", "name": "b", "stock": 9, "reorder_at": 5}])[0]["sku"] == "a"


def test_integrations_honest():
    st = {i["key"]: i["status"] for i in integration_status()}
    assert st["excel_export"] == "available" and st["tally"] == "not_available"
    csv = to_csv([{"a": 1, "b": "x"}], ["a", "b"])
    assert csv.splitlines()[0] == "a,b"


def test_flags_built_modules_on():
    assert ff.is_enabled("FEATURE_ACCOUNTING") is True
    assert ff.is_enabled("FEATURE_GST") is True
    assert ff.is_enabled("FEATURE_CA_WORKSPACE") is True
    assert ff.is_enabled("FEATURE_NOTICE_MANAGEMENT") is False
