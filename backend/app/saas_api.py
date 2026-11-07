"""Phases 3-13 — SaaS extension router. All routes: auth + user_id scoping.

Deterministic throughout; AI never writes statutory state. Every financial
write is idempotent where it matters (journals) and validated server-side.
"""
from datetime import datetime
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse
from pymongo.errors import DuplicateKeyError

from app.auth import get_current_active_user
from app.database import get_database
from app.models import User
from app.pagination import paginate
from app.validation import parse_object_id
from app.audit import log_event
from app import feature_flags as FF

router = APIRouter()


def _rid(request: Request) -> Optional[str]:
    return getattr(getattr(request, "state", None), "request_id", None)


def doc(d: dict) -> dict:
    out = {}
    for k, v in (d or {}).items():
        if isinstance(v, ObjectId):
            v = str(v)
        elif isinstance(v, datetime):
            v = v.isoformat()
        out[k] = v
    out["id"] = str(d.get("_id", d.get("id", "")))
    return out


def _need(flag: str):
    if not FF.is_enabled(flag):
        raise HTTPException(status_code=403, detail=f"Feature {flag} is not enabled")


def _dt(raw, default=None):
    if raw is None:
        return default or datetime.utcnow()
    if isinstance(raw, datetime):
        return raw
    try:
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00").split("+")[0])
    except Exception:
        raise HTTPException(status_code=422, detail=f"Bad date {raw!r}")


async def _ensure_accounts(db, user_id):
    from app.accounting import COA_SEED

    if await db.accounts.count_documents({"user_id": user_id}) > 0:
        return
    now = datetime.utcnow()
    await db.accounts.insert_many(
        [{"user_id": user_id, "code": c, "name": n, "type": t, "cashflow": cf,
          "active": True, "created_at": now} for c, n, t, cf in COA_SEED])


async def _next_seq(db, user_id, prefix: str) -> int:
    r = await db.counters.find_one_and_update(
        {"user_id": user_id, "prefix": prefix}, {"$inc": {"seq": 1}},
        upsert=True, return_document=True)
    return int(r.get("seq", 1))


# ---------------- Phase 3: accounting ----------------

@router.post("/accounts/ensure-seed")
async def accounts_seed(request: Request, current_user: User = Depends(get_current_active_user)):
    _need("FEATURE_ACCOUNTING")
    db = await get_database()
    await _ensure_accounts(db, current_user.id)
    return {"message": "Chart of accounts ready"}


@router.get("/accounts")
async def accounts_list(current_user: User = Depends(get_current_active_user)):
    _need("FEATURE_ACCOUNTING")
    db = await get_database()
    await _ensure_accounts(db, current_user.id)
    rows = await db.accounts.find({"user_id": current_user.id}).sort("code", 1).to_list(None)
    return [doc(r) for r in rows]


@router.post("/journals")
async def journal_post(body: dict, request: Request,
                       current_user: User = Depends(get_current_active_user)):
    _need("FEATURE_ACCOUNTING")
    from app.accounting import validate_journal

    lines = body.get("lines", [])
    try:
        validate_journal(lines)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    db = await get_database()
    await _ensure_accounts(db, current_user.id)
    jdoc = {"user_id": current_user.id, "date": _dt(body.get("date")),
            "narration": (body.get("narration") or "")[:500],
            "lines": [{"account_code": ln["account_code"],
                       "debit": round(float(ln.get("debit", 0)), 2),
                       "credit": round(float(ln.get("credit", 0)), 2)} for ln in lines],
            "source": body.get("source") or {}, "status": "posted",
            "idempotency_key": body.get("idempotency_key"),
            "created_at": datetime.utcnow()}
    if jdoc["idempotency_key"]:
        jdoc["idempotency_key"] = str(jdoc["idempotency_key"])
        try:
            r = await db.journals.insert_one(jdoc)
            jdoc["_id"] = r.inserted_id
        except DuplicateKeyError:
            existing = await db.journals.find_one(
                {"user_id": current_user.id, "idempotency_key": jdoc["idempotency_key"]})
            out = doc(existing)
            out["deduped"] = True
            return out
    else:
        r = await db.journals.insert_one(jdoc)
        jdoc["_id"] = r.inserted_id
    await log_event("JOURNAL_POSTED", user_id=current_user.id, request_id=_rid(request))
    return doc(jdoc)


@router.get("/journals")
async def journals_list(current_user: User = Depends(get_current_active_user),
                        skip: Optional[int] = None, limit: Optional[int] = None):
    _need("FEATURE_ACCOUNTING")
    db = await get_database()
    rows = await db.journals.find({"user_id": current_user.id}).sort("date", -1).to_list(None)
    return [doc(r) for r in paginate(rows, skip, limit)]


@router.post("/journals/{jid}/reverse")
async def journal_reverse(jid: str, body: dict, request: Request,
                          current_user: User = Depends(get_current_active_user)):
    _need("FEATURE_ACCOUNTING")
    from app.accounting import validate_journal

    db = await get_database()
    orig = await db.journals.find_one(
        {"_id": parse_object_id(jid, "journal"), "user_id": current_user.id})
    if not orig or orig.get("status") != "posted":
        raise HTTPException(status_code=404, detail="Journal not found or not reversible")
    lines = [{"account_code": ln["account_code"], "debit": ln.get("credit", 0),
              "credit": ln.get("debit", 0)} for ln in orig["lines"]]
    validate_journal(lines)
    rev = {"user_id": current_user.id, "date": datetime.utcnow(),
           "narration": f"Reversal of {jid}: {(body.get('narration') or '')[:300]}",
           "lines": lines, "source": {"type": "reversal", "id": jid},
           "status": "posted", "reverses_id": orig["_id"],
           "idempotency_key": f"rev:{jid}", "created_at": datetime.utcnow()}
    try:
        r = await db.journals.insert_one(rev)
        rev["_id"] = r.inserted_id
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Already reversed")
    await log_event("JOURNAL_REVERSED", user_id=current_user.id, obj=jid, request_id=_rid(request))
    return doc(rev)


async def _tb(db, user_id):
    from app.accounting import trial_balance

    accounts = await db.accounts.find({"user_id": user_id}).to_list(None)
    journals = await db.journals.find({"user_id": user_id}).to_list(None)
    accts = [{"code": a["code"], "name": a["name"], "type": a["type"]} for a in accounts]
    return trial_balance(accts, journals), accts, journals


@router.get("/ledger/{code}")
async def ledger(code: str, current_user: User = Depends(get_current_active_user)):
    _need("FEATURE_ACCOUNTING")
    from app.accounting import COA

    if code not in COA:
        raise HTTPException(status_code=404, detail="Unknown account")
    db = await get_database()
    journals = await db.journals.find({"user_id": current_user.id}).sort("date", 1).to_list(None)
    entries, bal = [], 0.0
    for j in journals:
        if j.get("status") != "posted":
            continue
        for ln in j.get("lines", []):
            if ln["account_code"] == code:
                bal = round(bal + ln.get("debit", 0) - ln.get("credit", 0), 2)
                entries.append({"date": ln.get("date", j.get("date")), "narration": j.get("narration"),
                                "debit": ln.get("debit", 0), "credit": ln.get("credit", 0),
                                "balance": bal})
    for e in entries:
        if isinstance(e["date"], datetime):
            e["date"] = e["date"].isoformat()
    return {"account": COA[code], "entries": entries, "balance": bal}


@router.get("/trial-balance")
async def trial_balance(current_user: User = Depends(get_current_active_user)):
    _need("FEATURE_ACCOUNTING")
    db = await get_database()
    tb, _, _ = await _tb(db, current_user.id)
    return tb


@router.get("/reports/profit-loss")
async def profit_loss(current_user: User = Depends(get_current_active_user)):
    _need("FEATURE_ACCOUNTING")
    from app.accounting import profit_and_loss

    db = await get_database()
    tb, accts, journals = await _tb(db, current_user.id)
    return profit_and_loss(accts, journals)


@router.get("/reports/balance-sheet")
async def balance_sheet(current_user: User = Depends(get_current_active_user)):
    _need("FEATURE_ACCOUNTING")
    from app.accounting import profit_and_loss, balance_sheet as _bs

    db = await get_database()
    tb, accts, journals = await _tb(db, current_user.id)
    net = profit_and_loss(accts, journals)["net_profit"]
    return _bs(accts, journals, net)


@router.get("/reports/cash-flow")
async def cash_flow(current_user: User = Depends(get_current_active_user)):
    _need("FEATURE_ACCOUNTING")
    from app.accounting import cash_flow as _cf

    db = await get_database()
    journals = await db.journals.find({"user_id": current_user.id}).to_list(None)
    return _cf(journals)


# ---------------- Phase 4: finance ops ----------------

@router.post("/parties")
async def party_create(body: dict, request: Request,
                       current_user: User = Depends(get_current_active_user)):
    kind = (body.get("kind") or "").lower()
    if kind not in ("customer", "vendor"):
        raise HTTPException(status_code=422, detail="kind must be customer|vendor")
    if not (body.get("name") or "").strip():
        raise HTTPException(status_code=422, detail="name is required")
    db = await get_database()
    pdoc = {"user_id": current_user.id, "kind": kind, "name": body["name"].strip()[:200],
            "gstin": (body.get("gstin") or "").strip().upper() or None,
            "phone": (body.get("phone") or "")[:30], "address": (body.get("address") or "")[:500],
            "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()}
    r = await db.parties.insert_one(pdoc)
    pdoc["_id"] = r.inserted_id
    await log_event("PARTY_CREATED", user_id=current_user.id, request_id=_rid(request))
    return doc(pdoc)


@router.get("/parties")
async def parties_list(kind: Optional[str] = None,
                       current_user: User = Depends(get_current_active_user),
                       skip: Optional[int] = None, limit: Optional[int] = None):
    db = await get_database()
    q: dict = {"user_id": current_user.id}
    if kind:
        q["kind"] = kind
    rows = await db.parties.find(q).sort("name", 1).to_list(None)
    return [doc(r) for r in paginate(rows, skip, limit)]


@router.delete("/parties/{pid}")
async def party_delete(pid: str, current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    r = await db.parties.delete_one(
        {"_id": parse_object_id(pid, "party"), "user_id": current_user.id})
    if r.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Party not found")
    return {"message": "Party deleted"}


@router.post("/imports/analyze")
async def import_analyze(body: dict, current_user: User = Depends(get_current_active_user)):
    """Validate + dedup candidate rows against existing fingerprints. No silent drops."""
    from app.finance import fingerprint, find_duplicates, suggest_category

    rows = body.get("rows", [])
    if not isinstance(rows, list) or len(rows) > 5000:
        raise HTTPException(status_code=422, detail="rows must be a list (max 5000)")
    db = await get_database()
    existing = await db.transactions.find({"user_id": current_user.id}).to_list(None)
    fps = {fingerprint(t) for t in existing}
    uniq, dups = find_duplicates(rows, fps)
    invalid = [r for r in uniq if not r.get("date") or r.get("amount") is None]
    valid = [r for r in uniq if r not in invalid]
    suggestions = [suggest_category(r.get("description", ""), r.get("transaction_type", "expense"))
                   for r in valid[:50]]
    return {"received": len(rows), "importable": len(valid), "duplicates": len(dups),
            "invalid": len(invalid), "invalid_rows": invalid[:20],
            "duplicate_rows": dups[:20], "suggestions": suggestions}


@router.post("/categorize/suggest")
async def categorize_suggest(body: dict,
                             current_user: User = Depends(get_current_active_user)):
    from app.finance import suggest_category

    return suggest_category(body.get("description", ""),
                            body.get("transaction_type", "expense"))


@router.get("/finance/receivables-payables")
async def recv_pay(current_user: User = Depends(get_current_active_user)):
    from app.finance import receivables_payables_summary

    db = await get_database()
    inv = await db.invoices.find({"user_id": current_user.id}).to_list(None)
    for i in inv:
        for k in ("due_date",):
            if isinstance(i.get(k), str):
                try:
                    i[k] = datetime.fromisoformat(i[k])
                except Exception:
                    pass
    sale = [i for i in inv if i.get("kind", "sale") == "sale"]
    purch = [i for i in inv if i.get("kind") == "purchase"]
    return receivables_payables_summary(sale, purch)


# ---------------- Phase 5: invoicing ----------------

async def _make_invoice(db, user_id, body: dict, kind: str, prefix: str) -> dict:
    from app.invoicing import compute_totals
    from app.tax_periods import current_fy

    items = body.get("items", [])
    if not items:
        raise HTTPException(status_code=422, detail="items are required")
    try:
        totals = compute_totals(items, bool(body.get("inter_state", False)))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    fy = current_fy()
    seq = await _next_seq(db, user_id, prefix)
    number = f"{prefix}-{fy}-{seq:04d}"
    now = datetime.utcnow()
    inv = {"user_id": user_id, "kind": kind, "number": number,
           "customer_id": body.get("customer_id"), "customer_name": (body.get("customer_name") or "")[:200],
           "date": _dt(body.get("date"), now), "due_date": _dt(body.get("due_date"), now),
           "items": items, "inter_state": bool(body.get("inter_state", False)),
           "computed": totals, "taxable_value": totals["taxable_value"],
           "total_tax": totals["total_tax"], "grand_total": totals["grand_total"],
           "paid_total": 0.0, "balance": totals["grand_total"], "status": "draft",
           "notes": (body.get("notes") or "")[:1000], "created_at": now, "updated_at": now}
    r = await db.invoices.insert_one(inv)
    inv["_id"] = r.inserted_id
    return inv


@router.post("/invoices")
async def invoice_create(body: dict, request: Request,
                         current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    from app.commerce import check_limit as _check_inv

    await _check_inv(db, current_user.id, "invoices")
    inv = await _make_invoice(db, current_user.id, body,
                              body.get("kind", "sale") if body.get("kind") in ("sale", "purchase") else "sale",
                              "INV")
    # accounting leg (best-effort, never breaks the invoice)
    try:
        from app.invoicing import invoice_journals

        lines = invoice_journals({**inv, "kind": inv["kind"]})
        if lines and FF.is_enabled("FEATURE_ACCOUNTING"):
            await _ensure_accounts(db, current_user.id)
            await db.journals.insert_one(
                {"user_id": current_user.id, "date": inv["date"],
                 "narration": f"Invoice {inv['number']}", "lines": lines,
                 "source": {"type": "invoice", "id": str(inv["_id"])},
                 "status": "posted", "idempotency_key": f"inv:{inv['_id']}",
                 "created_at": datetime.utcnow()})
    except Exception:
        pass
    await log_event("INVOICE_CREATED", user_id=current_user.id, obj=inv["number"],
                    request_id=_rid(request))
    return doc(inv)


@router.get("/invoices")
async def invoices_list(kind: Optional[str] = None, status: Optional[str] = None,
                        current_user: User = Depends(get_current_active_user),
                        skip: Optional[int] = None, limit: Optional[int] = None):
    db = await get_database()
    q: dict = {"user_id": current_user.id}
    if kind:
        q["kind"] = kind
    if status:
        q["status"] = status
    rows = await db.invoices.find(q).sort("date", -1).to_list(None)
    return [doc(r) for r in paginate(rows, skip, limit)]


@router.get("/invoices/{iid}")
async def invoice_get(iid: str, current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    inv = await db.invoices.find_one(
        {"_id": parse_object_id(iid, "invoice"), "user_id": current_user.id})
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return doc(inv)


@router.post("/invoices/{iid}/transition")
async def invoice_transition(iid: str, body: dict,
                             current_user: User = Depends(get_current_active_user)):
    from app.invoicing import transition

    db = await get_database()
    inv = await db.invoices.find_one(
        {"_id": parse_object_id(iid, "invoice"), "user_id": current_user.id})
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    try:
        new = transition(inv.get("status", "draft"), body.get("to", ""))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    await db.invoices.update_one({"_id": inv["_id"]},
                                 {"$set": {"status": new, "updated_at": datetime.utcnow()}})
    inv["status"] = new
    return doc(inv)


@router.post("/invoices/{iid}/payments")
async def invoice_pay(iid: str, body: dict, request: Request,
                      current_user: User = Depends(get_current_active_user)):
    from app.invoicing import apply_payment

    db = await get_database()
    inv = await db.invoices.find_one(
        {"_id": parse_object_id(iid, "invoice"), "user_id": current_user.id})
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    try:
        updated = apply_payment(inv, float(body.get("amount", 0)))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    pay = {"amount": round(float(body.get("amount", 0)), 2),
           "method": (body.get("method") or "manual")[:50],
           "reference": (body.get("reference") or "")[:200],
           "date": _dt(body.get("date")), "created_at": datetime.utcnow()}
    await db.invoices.update_one(
        {"_id": inv["_id"]},
        {"$set": {"status": updated["status"], "paid_total": updated["paid_total"],
                  "balance": updated["balance"], "updated_at": datetime.utcnow()},
         "$push": {"payments": pay}})
    await log_event("PAYMENT_RECORDED", user_id=current_user.id, obj=iid,
                    meta={"amount": pay["amount"]}, request_id=_rid(request))
    updated["_id"] = inv["_id"]
    return doc(updated)


@router.post("/credit-notes")
async def credit_note(body: dict, request: Request,
                      current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    inv = await _make_invoice(db, current_user.id, body, "credit_note", "CN")
    await log_event("CREDIT_NOTE_CREATED", user_id=current_user.id, request_id=_rid(request))
    return doc(inv)


@router.post("/debit-notes")
async def debit_note(body: dict, request: Request,
                     current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    inv = await _make_invoice(db, current_user.id, body, "debit_note", "DN")
    await log_event("DEBIT_NOTE_CREATED", user_id=current_user.id, request_id=_rid(request))
    return doc(inv)


@router.get("/gst/summary")
async def gst_summary(current_user: User = Depends(get_current_active_user)):
    _need("FEATURE_GST")
    from app.gst import gstr1_summary, gstr3b_summary

    db = await get_database()
    inv = await db.invoices.find({"user_id": current_user.id}).to_list(None)
    sale = [i for i in inv if i.get("kind", "sale") == "sale"]
    purch = [i for i in inv if i.get("kind") == "purchase"]
    return {"gstr1": gstr1_summary(sale),
            "gstr3b": gstr3b_summary(sale, purch)}


# ---------------- Phase 6: GST + TDS ----------------

@router.post("/gst/validate")
async def gst_validate(body: dict,
                       current_user: User = Depends(get_current_active_user)):
    from app.gst import validate_gstin

    return validate_gstin(body.get("gstin", ""))


@router.post("/gst/reconcile")
async def gst_reconcile(body: dict,
                        current_user: User = Depends(get_current_active_user)):
    from app.gst import gst_reconcile as _gr

    try:
        return _gr(float(body.get("books_tax", 0)), float(body.get("portal_tax", 0)))
    except (TypeError, ValueError):
        raise HTTPException(status_code=422, detail="books_tax/portal_tax must be numbers")


@router.get("/tds/sections")
async def tds_sections(current_user: User = Depends(get_current_active_user)):
    from app.tds import TDS_SECTIONS

    return {"sections": [{"code": k, "label": v[0], "rate": v[1],
                           "threshold": v[2], "payees": v[3]} for k, v in TDS_SECTIONS.items()]}


@router.post("/tds/compute")
async def tds_compute(body: dict,
                      current_user: User = Depends(get_current_active_user)):
    from app.tds import compute_tds

    try:
        return compute_tds(body.get("section", ""), float(body.get("amount", 0)),
                           body.get("pan_available", True))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/tds-records")
async def tds_record(body: dict, request: Request,
                     current_user: User = Depends(get_current_active_user)):
    from app.tds import compute_tds

    try:
        calc = compute_tds(body.get("section", ""), float(body.get("amount", 0)),
                           body.get("pan_available", True))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    db = await get_database()
    rec = {"user_id": current_user.id, "deductee": (body.get("deductee") or "")[:200],
           "section": calc["section"], "amount": calc["amount"], "tds": calc["tds"],
           "rate": calc["rate"], "date": _dt(body.get("date")), "status": "pending",
           "created_at": datetime.utcnow()}
    r = await db.tds_records.insert_one(rec)
    rec["_id"] = r.inserted_id
    await log_event("TDS_RECORDED", user_id=current_user.id, request_id=_rid(request))
    return doc(rec)


@router.get("/tds-records")
async def tds_list(current_user: User = Depends(get_current_active_user),
                   skip: Optional[int] = None, limit: Optional[int] = None):
    db = await get_database()
    rows = await db.tds_records.find({"user_id": current_user.id}).sort("date", -1).to_list(None)
    return [doc(r) for r in paginate(rows, skip, limit)]


@router.get("/tds/summary")
async def tds_summary(current_user: User = Depends(get_current_active_user)):
    from app.tds import tds_payable_summary

    db = await get_database()
    rows = await db.tds_records.find({"user_id": current_user.id}).to_list(None)
    return tds_payable_summary(rows)


# ---------------- Phase 7: income-tax 2.0 ----------------

@router.post("/gains/compute")
async def gains_compute(body: dict,
                        current_user: User = Depends(get_current_active_user)):
    from app.taxplus import capital_gain

    try:
        buy = _dt(body.get("buy_date"))
        sell = _dt(body.get("sell_date"))
        if sell < buy:
            raise ValueError("sell_date before buy_date")
        return capital_gain(float(body.get("purchase_value", 0)),
                            float(body.get("sale_value", 0)),
                            body.get("asset_type", "other"), buy, sell)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/itr/applicability")
async def itr_apply(body: dict,
                    current_user: User = Depends(get_current_active_user)):
    from app.taxplus import itr_applicability

    out = itr_applicability({"income_categories": body.get("income_categories", []),
                             "presumptive": bool(body.get("presumptive", False))})
    out["disclaimer"] = "Guidance only. Verify against active ITR rules before filing."
    return out


@router.get("/planning/opportunities")
async def planning(regime: str = "old",
                   current_user: User = Depends(get_current_active_user)):
    from app.taxplus import planning_opportunities
    from app.analysis import analysis_engine

    regime = regime if regime in ("old", "new") else "old"
    _, _, _, summary = await analysis_engine.analyze_user_data(current_user.id, regime)
    s = summary.model_dump()
    db = await get_database()
    deds = await db.deductions.find({"user_id": current_user.id}).to_list(None)
    verified = sum(float(d.get("amount", 0)) for d in deds
                   if str(d.get("verification_status")) == "complete")
    return {"regime": regime, "opportunities": planning_opportunities(s, verified, regime),
            "disclaimer": "Estimates from active deterministic rules with required evidence."}


# ---------------- Phase 8: document intelligence ----------------

@router.post("/docs/classify")
async def docs_classify(body: dict,
                        current_user: User = Depends(get_current_active_user)):
    from app.docsintel import classify_document

    return classify_document(body.get("filename", ""), body.get("mime", ""),
                             body.get("text_hint", ""))


@router.post("/docs/evidence-check")
async def docs_evidence(body: dict,
                        current_user: User = Depends(get_current_active_user)):
    from app.docsintel import check_evidence

    if not isinstance(body.get("required"), list):
        raise HTTPException(status_code=422, detail="required must be a list")
    return check_evidence(body.get("document", {}), body["required"])


@router.post("/doc-links")
async def doc_link(body: dict, current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    ln = {"user_id": current_user.id, "event": (body.get("event") or "other")[:100],
          "document_id": body.get("document_id"), "note": (body.get("note") or "")[:500],
          "created_at": datetime.utcnow()}
    r = await db.doc_links.insert_one(ln)
    ln["_id"] = r.inserted_id
    return doc(ln)


@router.get("/doc-links/summary")
async def doc_links_summary(current_user: User = Depends(get_current_active_user)):
    from app.docsintel import link_summary

    db = await get_database()
    rows = await db.doc_links.find({"user_id": current_user.id}).to_list(None)
    return link_summary(rows)


@router.patch("/documents/{did}/verify")
async def doc_verify(did: str, body: dict,
                     current_user: User = Depends(get_current_active_user)):
    from app.docsintel import verify_transition

    db = await get_database()
    d = await db.documents.find_one(
        {"_id": parse_object_id(did, "document"), "user_id": current_user.id})
    if not d:
        raise HTTPException(status_code=404, detail="Document not found")
    try:
        # 'complete' (upload default) is the verified-equivalent in this workflow.
        cur = str(d.get("verification_status", "pending"))
        if cur == "complete":
            cur = "verified"
        new = verify_transition(cur, body.get("to", ""))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    await db.documents.update_one(
        {"_id": d["_id"]},
        {"$set": {"verification_status": new, "verify_note": (body.get("notes") or "")[:500]}})
    return {"message": "Verification updated", "status": new}


# ---------------- Phase 9: financial intelligence ----------------

@router.get("/close/month-end")
async def month_end(current_user: User = Depends(get_current_active_user)):
    from app.intel import month_end_close
    from app.analysis import analysis_engine

    db = await get_database()
    txs = await db.transactions.find({"user_id": current_user.id}).to_list(None)
    inv = await db.invoices.find({"user_id": current_user.id}).to_list(None)
    docs = await db.documents.find({"user_id": current_user.id}).to_list(None)
    recon = await analysis_engine.reconcile_user(current_user.id)
    result = month_end_close(txs, inv, docs, recon)
    # guided steps: map each check to a clear next action
    steps = []
    for k, v in result["checks"].items():
        steps.append({
            "key": k, "status": v,
            "label": k.replace("_", " ").title(),
            "action": ("Review" if v != "ok" else "Done"),
        })
    result["steps"] = steps
    return result


@router.post("/close/month-end")
async def month_end_complete(current_user: User = Depends(get_current_active_user)):
    """Authenticated user explicitly marks the month closed after reviewing readiness."""
    from app.intel import month_end_close
    from app.analysis import analysis_engine

    db = await get_database()
    txs = await db.transactions.find({"user_id": current_user.id}).to_list(None)
    inv = await db.invoices.find({"user_id": current_user.id}).to_list(None)
    docs = await db.documents.find({"user_id": current_user.id}).to_list(None)
    recon = await analysis_engine.reconcile_user(current_user.id)
    result = month_end_close(txs, inv, docs, recon)
    period = datetime.utcnow().strftime("%Y-%m")
    await db.month_closes.update_one(
        {"user_id": current_user.id, "period": period},
        {"$set": {"closed_at": datetime.utcnow(), "closable": result["closable"],
                  "checks": result["checks"]}},
        upsert=True)
    return {"period": period, "closed": True, "closable": result["closable"],
            "message": "Month closed and recorded. Re-run the close summary any time to verify."}


@router.post("/intel/what-changed")
async def changed(body: dict, current_user: User = Depends(get_current_active_user)):
    from app.intel import what_changed

    if not isinstance(body.get("current"), dict) or not isinstance(body.get("previous"), dict):
        raise HTTPException(status_code=422, detail="current/previous objects required")
    return what_changed(body["current"], body["previous"])


@router.get("/intel/anomalies")
async def anomalies(current_user: User = Depends(get_current_active_user)):
    from app.intel import detect_anomalies

    db = await get_database()
    txs = await db.transactions.find({"user_id": current_user.id}).to_list(None)
    flags = detect_anomalies(txs)
    return {"flags": flags, "count": len(flags)}


@router.post("/intel/forecast")
async def forecast(body: dict, current_user: User = Depends(get_current_active_user)):
    from app.intel import forecast_cash

    try:
        return forecast_cash(float(body.get("opening", 0)), float(body.get("receivables_30", 0)),
                             float(body.get("payables_30", 0)), float(body.get("tax_due_30", 0)),
                             float(body.get("recurring_30", 0)), int(body.get("months", 3)))
    except (TypeError, ValueError):
        raise HTTPException(status_code=422, detail="Numeric inputs required")


@router.get("/intel/health")
async def health(tax_period: str = "2024-25",
                 current_user: User = Depends(get_current_active_user)):
    from app.intel import business_health
    from app.analysis import analysis_engine
    from app.tax_periods import parse_fy

    try:
        parse_fy(tax_period)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    _, _, score, summary = await analysis_engine.analyze_user_data(current_user.id)
    s = summary.model_dump()
    db = await get_database()
    docs = await db.documents.find({"user_id": current_user.id}).to_list(None)
    missing = sum(1 for d in docs if str(d.get("verification_status")) != "complete")
    recon = await analysis_engine.reconcile_user(current_user.id)
    return business_health(score.score, recon.get("score", 0),
                           s.get("outstanding_tax", 0), missing, tax_period)


# ---------------- Phase 10: assistant determinism endpoints ----------------

@router.get("/assistant/tax-owed")
async def asst_owed(current_user: User = Depends(get_current_active_user)):
    from app.analysis import analysis_engine

    _, _, _, summary = await analysis_engine.analyze_user_data(current_user.id)
    s = summary.model_dump()
    return {"owed": s.get("estimated_liability", 0), "paid": s.get("tax_paid", 0),
            "outstanding": s.get("outstanding_tax", 0), "regime": s.get("regime", "old"),
            "disclaimer": "Estimate from deterministic rules on available data."}


@router.get("/assistant/attention")
async def asst_attention(current_user: User = Depends(get_current_active_user)):
    from app.analysis import analysis_engine

    db = await get_database()
    obs = await db.obligations.find({"user_id": current_user.id}).to_list(200)
    docs = await db.documents.find({"user_id": current_user.id}).to_list(200)
    missing = [o["title"] for o in obs if "missing" in o.get("title", "").lower()][:5]
    high = [o["title"] for o in obs if str(o.get("risk_level")) == "high"][:5]
    unverified = sum(1 for d in docs if str(d.get("verification_status")) != "complete")
    recon = await analysis_engine.reconcile_user(current_user.id)
    return {"high_risk": high, "missing_documents": missing,
            "unverified_count": unverified, "recon": recon.get("status"),
            "open_obligations": len(obs)}


@router.get("/assistant/overdue-invoices")
async def asst_overdue(current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    now = datetime.utcnow()
    rows = await db.invoices.find(
        {"user_id": current_user.id, "kind": "sale",
         "status": {"$in": ["sent", "viewed", "partially_paid", "overdue"]}}).to_list(200)
    out = []
    for r in rows:
        try:
            due = r["due_date"] if isinstance(r.get("due_date"), datetime) \
                else datetime.fromisoformat(str(r.get("due_date")))
        except Exception:
            continue
        if due < now:
            out.append({"number": r.get("number"), "customer": r.get("customer_name"),
                        "balance": r.get("balance"), "due_date": due.isoformat()})
    return {"overdue": sorted(out, key=lambda x: x["due_date"]),
            "total": round(sum(float(o["balance"] or 0) for o in out), 2)}


# ---------------- Phase 11: practice ----------------

@router.post("/clients")
async def client_create(body: dict, current_user: User = Depends(get_current_active_user)):
    _need("FEATURE_CA_WORKSPACE")
    if not (body.get("name") or "").strip():
        raise HTTPException(status_code=422, detail="name is required")
    db = await get_database()
    from app.commerce import check_limit as _check_clients

    await _check_clients(db, current_user.id, "clients")
    c = {"user_id": current_user.id, "name": body["name"].strip()[:200],
         "contact": (body.get("contact") or "")[:200], "business": (body.get("business") or "")[:200],
         "created_at": datetime.utcnow()}
    r = await db.clients.insert_one(c)
    c["_id"] = r.inserted_id
    return doc(c)


@router.get("/clients")
async def clients_list(current_user: User = Depends(get_current_active_user),
                       skip: Optional[int] = None, limit: Optional[int] = None):
    _need("FEATURE_CA_WORKSPACE")
    db = await get_database()
    rows = await db.clients.find({"user_id": current_user.id}).sort("name", 1).to_list(None)
    return [doc(r) for r in paginate(rows, skip, limit)]


@router.post("/tasks")
async def task_create(body: dict, current_user: User = Depends(get_current_active_user)):
    _need("FEATURE_CA_WORKSPACE")
    from app.practice import check_task

    try:
        check_task(body.get("status", "open"))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    db = await get_database()
    t = {"user_id": current_user.id, "client": (body.get("client") or "")[:200],
         "title": (body.get("title") or "").strip()[:300], "due": body.get("due"),
         "status": body.get("status", "open"), "created_at": datetime.utcnow()}
    if not t["title"]:
        raise HTTPException(status_code=422, detail="title is required")
    r = await db.tasks.insert_one(t)
    t["_id"] = r.inserted_id
    return doc(t)


@router.get("/tasks")
async def tasks_list(current_user: User = Depends(get_current_active_user),
                     skip: Optional[int] = None, limit: Optional[int] = None):
    _need("FEATURE_CA_WORKSPACE")
    db = await get_database()
    rows = await db.tasks.find({"user_id": current_user.id}).sort("created_at", -1).to_list(None)
    return [doc(r) for r in paginate(rows, skip, limit)]


@router.patch("/tasks/{tid}")
async def task_patch(tid: str, body: dict,
                     current_user: User = Depends(get_current_active_user)):
    _need("FEATURE_CA_WORKSPACE")
    from app.practice import check_task

    try:
        check_task(body.get("status", ""))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    db = await get_database()
    r = await db.tasks.update_one(
        {"_id": parse_object_id(tid, "task"), "user_id": current_user.id},
        {"$set": {"status": body["status"]}})
    if r.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task updated"}


@router.post("/doc-requests")
async def docreq_create(body: dict, current_user: User = Depends(get_current_active_user)):
    _need("FEATURE_CA_WORKSPACE")
    from app.practice import check_docreq

    try:
        check_docreq(body.get("status", "requested"))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    if not isinstance(body.get("items"), list) or not body["items"]:
        raise HTTPException(status_code=422, detail="items list required")
    db = await get_database()
    d = {"user_id": current_user.id, "client": (body.get("client") or "")[:200],
         "items": body["items"][:50], "status": body.get("status", "requested"),
         "created_at": datetime.utcnow()}
    r = await db.doc_requests.insert_one(d)
    d["_id"] = r.inserted_id
    return doc(d)


@router.get("/doc-requests")
async def docreq_list(current_user: User = Depends(get_current_active_user),
                      skip: Optional[int] = None, limit: Optional[int] = None):
    _need("FEATURE_CA_WORKSPACE")
    db = await get_database()
    rows = await db.doc_requests.find({"user_id": current_user.id}).sort("created_at", -1).to_list(None)
    return [doc(r) for r in paginate(rows, skip, limit)]


@router.patch("/doc-requests/{did}")
async def docreq_patch(did: str, body: dict,
                       current_user: User = Depends(get_current_active_user)):
    _need("FEATURE_CA_WORKSPACE")
    from app.practice import check_docreq

    try:
        check_docreq(body.get("status", ""))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    db = await get_database()
    r = await db.doc_requests.update_one(
        {"_id": parse_object_id(did, "doc-request"), "user_id": current_user.id},
        {"$set": {"status": body["status"]}})
    if r.matched_count == 0:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"message": "Request updated"}


@router.post("/reviews")
async def review_create(body: dict, current_user: User = Depends(get_current_active_user)):
    _need("FEATURE_CA_WORKSPACE")
    db = await get_database()
    r_ = {"user_id": current_user.id, "entity": (body.get("entity") or "")[:200],
          "state": "auto", "note": (body.get("note") or "")[:500],
          "created_at": datetime.utcnow()}
    r = await db.reviews.insert_one(r_)
    r_["_id"] = r.inserted_id
    return doc(r_)


@router.get("/reviews")
async def reviews_list(current_user: User = Depends(get_current_active_user),
                       skip: Optional[int] = None, limit: Optional[int] = None):
    _need("FEATURE_CA_WORKSPACE")
    db = await get_database()
    rows = await db.reviews.find({"user_id": current_user.id}).sort("created_at", -1).to_list(None)
    return [doc(r) for r in paginate(rows, skip, limit)]


@router.patch("/reviews/{rid}/transition")
async def review_move(rid: str, body: dict,
                      current_user: User = Depends(get_current_active_user)):
    _need("FEATURE_CA_WORKSPACE")
    from app.practice import review_transition

    db = await get_database()
    rev = await db.reviews.find_one(
        {"_id": parse_object_id(rid, "review"), "user_id": current_user.id})
    if not rev:
        raise HTTPException(status_code=404, detail="Review not found")
    try:
        new = review_transition(rev.get("state", "auto"), body.get("to", ""))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    await db.reviews.update_one({"_id": rev["_id"]}, {"$set": {"state": new}})
    return {"message": "Review updated", "state": new}


@router.get("/practice/overview")
async def practice_overview(current_user: User = Depends(get_current_active_user)):
    _need("FEATURE_CA_WORKSPACE")
    from app.practice import practice_overview as _ov

    db = await get_database()
    clients = await db.clients.find({"user_id": current_user.id}).to_list(None)
    tasks = await db.tasks.find({"user_id": current_user.id}).to_list(None)
    reviews = await db.reviews.find({"user_id": current_user.id}).to_list(None)
    return _ov(clients, tasks, reviews)


# ---------------- Phase 12: inventory + POS ----------------

@router.post("/products")
async def product_create(body: dict, current_user: User = Depends(get_current_active_user)):
    _need("FEATURE_INVENTORY")
    if not (body.get("sku") or "").strip() or not (body.get("name") or "").strip():
        raise HTTPException(status_code=422, detail="sku and name are required")
    db = await get_database()
    if await db.products.find_one({"user_id": current_user.id, "sku": body["sku"].strip()}):
        raise HTTPException(status_code=400, detail="SKU already exists")
    opening = round(float(body.get("opening_stock", 0)), 2)
    p = {"user_id": current_user.id, "sku": body["sku"].strip()[:50],
         "name": body["name"].strip()[:200], "hsn": str(body.get("hsn", ""))[:20],
         "unit": (body.get("unit") or "pcs")[:20], "rate": round(float(body.get("rate", 0)), 2),
         "gst_rate": round(float(body.get("gst_rate", 0)), 2),
         "reorder_at": round(float(body.get("reorder_at", 5)), 2),
         "created_at": datetime.utcnow()}
    r = await db.products.insert_one(p)
    p["_id"] = r.inserted_id
    if opening > 0:
        await db.stock_moves.insert_one(
            {"user_id": current_user.id, "product_id": r.inserted_id,
             "qty": opening, "type": "purchase", "ref": "opening",
             "created_at": datetime.utcnow()})
        p["stock"] = opening
    else:
        p["stock"] = 0.0
    return doc(p)


@router.get("/products")
async def products_list(current_user: User = Depends(get_current_active_user),
                        skip: Optional[int] = None, limit: Optional[int] = None):
    _need("FEATURE_INVENTORY")
    from app.inventory import stock_on_hand

    db = await get_database()
    prods = await db.products.find({"user_id": current_user.id}).sort("name", 1).to_list(None)
    moves = await db.stock_moves.find({"user_id": current_user.id}).to_list(None)
    out = []
    for p in prods:
        d = doc(p)
        d["stock"] = stock_on_hand(moves, str(p["_id"]))
        out.append(d)
    return paginate(out, skip, limit)


@router.post("/stock-moves")
async def stock_move(body: dict, current_user: User = Depends(get_current_active_user)):
    _need("FEATURE_INVENTORY")
    if body.get("type") not in ("purchase", "sale", "adjust_in", "adjust_out"):
        raise HTTPException(status_code=422, detail="Bad move type")
    try:
        qty = float(body.get("qty", 0))
    except (TypeError, ValueError):
        raise HTTPException(status_code=422, detail="qty must be a number")
    if qty <= 0:
        raise HTTPException(status_code=422, detail="qty must be positive")
    db = await get_database()
    prod = await db.products.find_one(
        {"_id": parse_object_id(body.get("product_id", ""), "product"),
         "user_id": current_user.id})
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    m = {"user_id": current_user.id, "product_id": prod["_id"], "qty": qty,
         "type": body["type"], "ref": (body.get("ref") or "")[:200],
         "created_at": datetime.utcnow()}
    r = await db.stock_moves.insert_one(m)
    m["_id"] = r.inserted_id
    return doc(m)


@router.get("/stock/{sku}")
async def stock_level(sku: str, current_user: User = Depends(get_current_active_user)):
    _need("FEATURE_INVENTORY")
    from app.inventory import stock_on_hand

    db = await get_database()
    prod = await db.products.find_one({"user_id": current_user.id, "sku": sku})
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    moves = await db.stock_moves.find({"user_id": current_user.id}).to_list(None)
    return {"sku": sku, "name": prod.get("name"), "stock": stock_on_hand(moves, str(prod["_id"]))}


@router.get("/inventory/low-stock")
async def low_stock(current_user: User = Depends(get_current_active_user)):
    _need("FEATURE_INVENTORY")
    from app.inventory import stock_on_hand, low_stock as _ls

    db = await get_database()
    prods = await db.products.find({"user_id": current_user.id}).to_list(None)
    moves = await db.stock_moves.find({"user_id": current_user.id}).to_list(None)
    enriched = []
    for p in prods:
        enriched.append({"sku": p.get("sku"), "name": p.get("name"),
                         "stock": stock_on_hand(moves, str(p["_id"])),
                         "reorder_at": float(p.get("reorder_at", 5))})
    return {"items": _ls(enriched), "count": len(_ls(enriched))}


@router.post("/pos/bill")
async def pos_bill(body: dict, request: Request,
                   current_user: User = Depends(get_current_active_user)):
    """Cart -> totals -> stock decrement -> sale invoice -> accounting legs."""
    _need("FEATURE_POS")
    from app.inventory import build_bill, stock_on_hand

    cart = body.get("cart", [])
    if not cart:
        raise HTTPException(status_code=422, detail="cart is required")
    db = await get_database()
    from app.commerce import check_limit as _check_pos

    await _check_pos(db, current_user.id, "invoices")
    prods = await db.products.find({"user_id": current_user.id}).to_list(None)
    moves = await db.stock_moves.find({"user_id": current_user.id}).to_list(None)
    pmap = {}
    for p in prods:
        pmap[p["sku"]] = {"name": p["name"], "hsn": p.get("hsn", ""),
                          "rate": float(p.get("rate", 0)),
                          "gst_rate": float(p.get("gst_rate", 0)),
                          "stock": stock_on_hand(moves, str(p["_id"])),
                          "id": p["_id"]}
    try:
        bill = build_bill(cart, pmap, bool(body.get("inter_state", False)))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    now = datetime.utcnow()
    for line in cart:
        await db.stock_moves.insert_one(
            {"user_id": current_user.id, "product_id": pmap[line["sku"]]["id"],
             "qty": float(line["qty"]), "type": "sale", "ref": "pos",
             "created_at": now})
    seq = await _next_seq(db, current_user.id, "POS")
    inv = {"user_id": current_user.id, "kind": "sale", "number": f"POS-{seq:05d}",
           "customer_name": (body.get("customer_name") or "Walk-in")[:200],
           "date": now, "due_date": now, "items": bill["items"],
           "computed": {"lines": bill["lines"]}, "taxable_value": bill["taxable_value"],
           "total_tax": bill["total_tax"], "grand_total": bill["grand_total"],
           "paid_total": bill["grand_total"], "balance": 0.0, "status": "paid",
           "payment_method": (body.get("payment_method") or "cash")[:30],
           "payment_reference": (body.get("payment_reference") or "")[:200],
           "created_at": now, "updated_at": now}
    r = await db.invoices.insert_one(inv)
    inv["_id"] = r.inserted_id
    try:
        from app.invoicing import invoice_journals

        lines = invoice_journals({**inv, "kind": "sale"})
        if lines and FF.is_enabled("FEATURE_ACCOUNTING"):
            await _ensure_accounts(db, current_user.id)
            await db.journals.insert_one(
                {"user_id": current_user.id, "date": now,
                 "narration": f"POS bill {inv['number']}", "lines": lines,
                 "source": {"type": "pos", "id": str(inv["_id"])},
                 "status": "posted", "idempotency_key": f"pos:{inv['_id']}",
                 "created_at": now})
    except Exception:
        pass
    await log_event("POS_BILL", user_id=current_user.id, obj=inv["number"],
                    request_id=_rid(request))
    return doc(inv)


# ---------------- Phase 13: integrations ----------------

@router.get("/integrations/status")
async def integrations_status(current_user: User = Depends(get_current_active_user)):
    from app.integrations import integration_status

    return {"integrations": integration_status()}


def _csv_response(name: str, content: str) -> PlainTextResponse:
    return PlainTextResponse(content, media_type="text/csv",
                             headers={"Content-Disposition": f"attachment; filename={name}"})


@router.get("/exports/transactions.csv")
async def export_tx(current_user: User = Depends(get_current_active_user)):
    from app.integrations import to_csv, TX_COLUMNS

    db = await get_database()
    rows = await db.transactions.find({"user_id": current_user.id}).to_list(None)
    for r in rows:
        if isinstance(r.get("date"), datetime):
            r["date"] = r["date"].isoformat()
    return _csv_response("transactions.csv", to_csv(rows, TX_COLUMNS))


@router.get("/exports/invoices.csv")
async def export_inv(current_user: User = Depends(get_current_active_user)):
    from app.integrations import to_csv, INVOICE_COLUMNS

    db = await get_database()
    rows = await db.invoices.find({"user_id": current_user.id}).to_list(None)
    flat = [{"number": r.get("number"), "customer": r.get("customer_name"),
             "date": r.get("date").isoformat() if isinstance(r.get("date"), datetime) else r.get("date"),
             "due_date": r.get("due_date").isoformat() if isinstance(r.get("due_date"), datetime) else r.get("due_date"),
             "taxable_value": r.get("taxable_value"), "total_tax": r.get("total_tax"),
             "grand_total": r.get("grand_total"), "status": r.get("status")} for r in rows]
    return _csv_response("invoices.csv", to_csv(flat, INVOICE_COLUMNS))


@router.get("/exports/parties.csv")
async def export_parties(current_user: User = Depends(get_current_active_user)):
    from app.integrations import to_csv, PARTY_COLUMNS

    db = await get_database()
    rows = await db.parties.find({"user_id": current_user.id}).to_list(None)
    return _csv_response("parties.csv", to_csv(rows, PARTY_COLUMNS))


@router.get("/exports/me")
async def export_me(current_user: User = Depends(get_current_active_user)):
    """Structured JSON self-export (Export My Data)."""
    db = await get_database()
    out = {}
    for coll in ("transactions", "investments", "deductions", "documents", "invoices",
                 "parties", "products", "clients", "tasks"):
        try:
            rows = await db[coll].find({"user_id": current_user.id}).to_list(None)
            out[coll] = [doc(r) for r in rows]
        except Exception:
            out[coll] = []
    out["exported_at"] = datetime.utcnow().isoformat() + "Z"
    return out


# ---------------- auto-post hook (one transaction -> everything) ----------------

async def auto_post_transaction(db, user, tx: dict) -> None:
    """Best-effort accounting leg for a new transaction. Never raises."""
    try:
        if not FF.is_enabled("FEATURE_ACCOUNTING"):
            return
        from app.accounting import journals_for_transaction

        lines = journals_for_transaction(tx)
        if not lines:
            return
        await _ensure_accounts(db, user.id if hasattr(user, "id") else user["_id"])
        uid = user.id if hasattr(user, "id") else user["_id"]
        await db.journals.insert_one(
            {"user_id": uid, "date": tx.get("date", datetime.utcnow()),
             "narration": f"Auto: {tx.get('description', '')[:200]}", "lines": lines,
             "source": {"type": "transaction", "id": str(tx.get("_id"))},
             "status": "posted", "idempotency_key": f"tx:{tx.get('_id')}",
             "created_at": datetime.utcnow()})
    except Exception:
        pass
