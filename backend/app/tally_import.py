"""Tally Prime XML & Standard Accounting Import/Export Parser.

Parses standard Tally Prime XML export formats for:
1. Ledgers (Masters) with group mapping to TaxShield Chart of Accounts
2. Vouchers (Daybook / Transactions: Sales, Purchase, Payment, Receipt, Journal)
3. Trial Balance summaries
4. Duplicate detection (date, voucher number, amount)
5. Strict double-entry balance enforcement (Sum Debits == Sum Credits)
6. Export: Serializes TaxShield journal entries into Tally-compliant XML
"""

import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple


# Standard mapping of Tally Master Groups to TaxShield Account Categories
TALLY_GROUP_MAP = {
    # Assets
    "current assets": "asset",
    "bank accounts": "asset",
    "cash-in-hand": "asset",
    "sundry debtors": "asset",
    "deposits (asset)": "asset",
    "loans & advances (asset)": "asset",
    "stock-in-hand": "asset",
    "fixed assets": "asset",
    "investments": "asset",
    # Liabilities
    "current liabilities": "liability",
    "sundry creditors": "liability",
    "duties & taxes": "liability",
    "provisions": "liability",
    "bank od a/c": "liability",
    "loans (liability)": "liability",
    "secured loans": "liability",
    "unsecured loans": "liability",
    # Equity
    "capital account": "equity",
    "reserves & surplus": "equity",
    # Income
    "sales accounts": "income",
    "direct incomes": "income",
    "indirect incomes": "income",
    # Expense
    "purchase accounts": "expense",
    "direct expenses": "expense",
    "indirect expenses": "expense",
}


def map_tally_group(parent_group: str) -> str:
    """Map a Tally group name to TaxShield's 5 core types: asset, liability, equity, income, expense."""
    cleaned = (parent_group or "").strip().lower()
    return TALLY_GROUP_MAP.get(cleaned, "expense" if "expense" in cleaned else "asset")


def parse_tally_date(date_str: str) -> str:
    """Parse Tally YYYYMMDD date format into ISO YYYY-MM-DD."""
    cleaned = (date_str or "").strip()
    if len(cleaned) == 8 and cleaned.isdigit():
        return f"{cleaned[:4]}-{cleaned[4:6]}-{cleaned[6:8]}"
    return cleaned


def parse_tally_xml_masters(xml_content: str) -> List[Dict[str, Any]]:
    """
    Parse Tally XML Masters for Ledgers.
    Extracts name, parent group, opening balance, and TaxShield category.
    """
    root = ET.fromstring(xml_content)
    ledgers = []
    
    # Locate all LEDGER nodes
    for ledger_node in root.iter("LEDGER"):
        name = ledger_node.get("NAME") or ""
        if not name:
            name_elem = ledger_node.find("NAME")
            if name_elem is not None and name_elem.text:
                name = name_elem.text

        parent_node = ledger_node.find("PARENT")
        parent = parent_node.text if parent_node is not None and parent_node.text else "General"

        op_node = ledger_node.find("OPENINGBALANCE")
        op_val = float(op_node.text) if op_node is not None and op_node.text else 0.0

        if name:
            ledgers.append({
                "name": name.strip(),
                "tally_parent": parent.strip(),
                "account_type": map_tally_group(parent),
                "opening_balance": abs(op_val),
                "balance_type": "credit" if op_val < 0 else "debit",
            })

    return ledgers


def parse_tally_xml_vouchers(xml_content: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Parse Tally XML Vouchers (Daybook entries).
    Extracts voucher number, date, type, narration, and entries.
    Validates double-entry equality and flags duplicates.
    Returns:
      (vouchers, warnings)
    """
    root = ET.fromstring(xml_content)
    vouchers = []
    warnings = []
    seen_keys = set()

    for vch in root.iter("VOUCHER"):
        vch_type = vch.get("VCHTYPE") or ""
        if not vch_type:
            t_node = vch.find("VOUCHERTYPENAME")
            if t_node is not None and t_node.text:
                vch_type = t_node.text

        date_node = vch.find("DATE")
        date_str = parse_tally_date(date_node.text if date_node is not None else "")

        vch_num_node = vch.find("VOUCHERNUMBER")
        vch_num = vch_num_node.text.strip() if vch_num_node is not None and vch_num_node.text else ""

        narr_node = vch.find("NARRATION")
        narration = narr_node.text.strip() if narr_node is not None and narr_node.text else ""

        entries = []
        debit_total = 0.0
        credit_total = 0.0

        # Ledger entries in Tally are nested inside ALLLEDGERENTRIES.LIST or LEDGERENTRIES.LIST
        for leg in vch.iter():
            if leg.tag in ("ALLLEDGERENTRIES.LIST", "LEDGERENTRIES.LIST"):
                l_name_node = leg.find("LEDGERNAME")
                amt_node = leg.find("AMOUNT")
                if l_name_node is not None and amt_node is not None and amt_node.text:
                    l_name = l_name_node.text.strip()
                    try:
                        amt = float(amt_node.text.strip())
                    except ValueError:
                        continue

                    # In Tally XML, negative amounts represent Credits, positive are Debits
                    if amt < 0:
                        cr = abs(amt)
                        dr = 0.0
                        credit_total += cr
                    else:
                        dr = abs(amt)
                        cr = 0.0
                        debit_total += dr

                    entries.append({
                        "ledger_name": l_name,
                        "debit": dr,
                        "credit": cr,
                    })

        if not entries:
            continue

        # Double-entry balance check: within 1 paisa (0.01) tolerance
        diff = abs(debit_total - credit_total)
        is_balanced = diff < 0.01

        # Duplicate detection key
        dedup_key = f"{date_str}:{vch_num}:{round(max(debit_total, credit_total), 2)}"
        is_duplicate = dedup_key in seen_keys
        if is_duplicate:
            warnings.append(f"Duplicate voucher detected: #{vch_num} on {date_str} for ₹{debit_total:,.2f}")
        else:
            seen_keys.add(dedup_key)

        if not is_balanced:
            warnings.append(f"Voucher #{vch_num} on {date_str} is unbalanced: Dr ₹{debit_total:,.2f} != Cr ₹{credit_total:,.2f}")

        vouchers.append({
            "voucher_type": vch_type or "Journal",
            "voucher_number": vch_num,
            "date": date_str,
            "narration": narration,
            "entries": entries,
            "total_debit": round(debit_total, 2),
            "total_credit": round(credit_total, 2),
            "is_balanced": is_balanced,
            "is_duplicate": is_duplicate,
        })

    return vouchers, warnings


def parse_tally_trial_balance(xml_content: str) -> Dict[str, Any]:
    """Parse and verify Trial Balance from Tally XML."""
    ledgers = parse_tally_xml_masters(xml_content)
    total_debits = sum(l["opening_balance"] for l in ledgers if l["balance_type"] == "debit")
    total_credits = sum(l["opening_balance"] for l in ledgers if l["balance_type"] == "credit")

    balanced = abs(total_debits - total_credits) < 0.01
    return {
        "ledgers_count": len(ledgers),
        "total_debit": round(total_debits, 2),
        "total_credit": round(total_credits, 2),
        "difference": round(abs(total_debits - total_credits), 2),
        "is_balanced": balanced,
        "ledgers": ledgers,
    }


def export_to_tally_xml(journals: List[Dict[str, Any]], company_name: str = "TaxShield Client") -> str:
    """
    Export TaxShield journal entries into Tally-compliant XML format.
    Can be directly imported into Tally Prime via 'Import Data -> Vouchers'.
    """
    root = ET.Element("ENVELOPE")
    
    header = ET.SubElement(root, "HEADER")
    tally_request = ET.SubElement(header, "TALLYREQUEST")
    tally_request.text = "Import Data"

    body = ET.SubElement(root, "BODY")
    import_data = ET.SubElement(body, "IMPORTDATA")
    
    req_desc = ET.SubElement(import_data, "REQUESTDESC")
    report_name = ET.SubElement(req_desc, "REPORTNAME")
    report_name.text = "All Masters"

    req_data = ET.SubElement(import_data, "REQUESTDATA")

    for j in journals:
        msg = ET.SubElement(req_data, "TALLYMESSAGE", {"xmlns:UDF": "TallyUDF"})
        vch = ET.SubElement(msg, "VOUCHER", {"VCHTYPE": j.get("voucher_type", "Journal"), "ACTION": "Create"})
        
        # Date: YYYYMMDD
        date_raw = j.get("date", "").replace("-", "")
        v_date = ET.SubElement(vch, "DATE")
        v_date.text = date_raw

        v_num = ET.SubElement(vch, "VOUCHERNUMBER")
        v_num.text = str(j.get("voucher_number") or j.get("number") or "1")

        v_type = ET.SubElement(vch, "VOUCHERTYPENAME")
        v_type.text = j.get("voucher_type", "Journal")

        v_narr = ET.SubElement(vch, "NARRATION")
        v_narr.text = j.get("narration", "")

        for entry in j.get("entries", []):
            leg = ET.SubElement(vch, "ALLLEDGERENTRIES.LIST")
            
            lname = ET.SubElement(leg, "LEDGERNAME")
            lname.text = entry.get("ledger_name", "General")

            amt = ET.SubElement(leg, "AMOUNT")
            # In Tally: Debit is positive, Credit is negative
            dr = float(entry.get("debit", 0.0))
            cr = float(entry.get("credit", 0.0))
            if cr > 0:
                amt.text = f"-{cr:.2f}"
            else:
                amt.text = f"{dr:.2f}"

    return ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")

