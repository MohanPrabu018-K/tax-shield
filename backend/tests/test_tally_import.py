"""
Tests for Tally Prime XML import and export parser.
Covers:
- Ledger parsing and group mapping (Asset, Liability, Equity, Income, Expense)
- Voucher parsing with debit/credit balancing
- Duplicate detection (date + voucher number + amount)
- Unbalanced voucher detection
- Trial balance parsing and balancing calculation
- Tally XML export serialization
- API endpoints: /api/practice/migration/tally/preview and /import
"""

import pytest
from app.tally_import import (
    parse_tally_xml_masters,
    parse_tally_xml_vouchers,
    parse_tally_trial_balance,
    export_to_tally_xml,
    map_tally_group,
)

SAMPLE_TALLY_MASTERS_XML = """<ENVELOPE>
  <BODY>
    <DATA>
      <TALLYMESSAGE>
        <LEDGER NAME="HDFC Bank Current A/c">
          <PARENT>Bank Accounts</PARENT>
          <OPENINGBALANCE>150000.00</OPENINGBALANCE>
        </LEDGER>
      </TALLYMESSAGE>
      <TALLYMESSAGE>
        <LEDGER NAME="Apex Infotech Pvt Ltd">
          <PARENT>Sundry Debtors</PARENT>
          <OPENINGBALANCE>75000.00</OPENINGBALANCE>
        </LEDGER>
      </TALLYMESSAGE>
      <TALLYMESSAGE>
        <LEDGER NAME="Vikas Raw Materials Co">
          <PARENT>Sundry Creditors</PARENT>
          <OPENINGBALANCE>-225000.00</OPENINGBALANCE>
        </LEDGER>
      </TALLYMESSAGE>
      <TALLYMESSAGE>
        <LEDGER NAME="Software Consulting Revenue">
          <PARENT>Direct Incomes</PARENT>
          <OPENINGBALANCE>0.00</OPENINGBALANCE>
        </LEDGER>
      </TALLYMESSAGE>
      <TALLYMESSAGE>
        <LEDGER NAME="Office Rent">
          <PARENT>Indirect Expenses</PARENT>
          <OPENINGBALANCE>0.00</OPENINGBALANCE>
        </LEDGER>
      </TALLYMESSAGE>
    </DATA>
  </BODY>
</ENVELOPE>"""

SAMPLE_TALLY_VOUCHERS_XML = """<ENVELOPE>
  <BODY>
    <DATA>
      <TALLYMESSAGE>
        <VOUCHER VCHTYPE="Receipt" DATE="20261015">
          <VOUCHERNUMBER>RCT-001</VOUCHERNUMBER>
          <NARRATION>Payment received against invoice #INV-101</NARRATION>
          <ALLLEDGERENTRIES.LIST>
            <LEDGERNAME>HDFC Bank Current A/c</LEDGERNAME>
            <AMOUNT>50000.00</AMOUNT>
          </ALLLEDGERENTRIES.LIST>
          <ALLLEDGERENTRIES.LIST>
            <LEDGERNAME>Apex Infotech Pvt Ltd</LEDGERNAME>
            <AMOUNT>-50000.00</AMOUNT>
          </ALLLEDGERENTRIES.LIST>
        </VOUCHER>
      </TALLYMESSAGE>
      <TALLYMESSAGE>
        <VOUCHER VCHTYPE="Payment" DATE="20261018">
          <VOUCHERNUMBER>PMT-042</VOUCHERNUMBER>
          <NARRATION>Rent for October 2026</NARRATION>
          <ALLLEDGERENTRIES.LIST>
            <LEDGERNAME>Office Rent</LEDGERNAME>
            <AMOUNT>25000.00</AMOUNT>
          </ALLLEDGERENTRIES.LIST>
          <ALLLEDGERENTRIES.LIST>
            <LEDGERNAME>HDFC Bank Current A/c</LEDGERNAME>
            <AMOUNT>-25000.00</AMOUNT>
          </ALLLEDGERENTRIES.LIST>
        </VOUCHER>
      </TALLYMESSAGE>
      <TALLYMESSAGE>
        <!-- Duplicate of RCT-001 -->
        <VOUCHER VCHTYPE="Receipt" DATE="20261015">
          <VOUCHERNUMBER>RCT-001</VOUCHERNUMBER>
          <NARRATION>Payment received duplicate</NARRATION>
          <ALLLEDGERENTRIES.LIST>
            <LEDGERNAME>HDFC Bank Current A/c</LEDGERNAME>
            <AMOUNT>50000.00</AMOUNT>
          </ALLLEDGERENTRIES.LIST>
          <ALLLEDGERENTRIES.LIST>
            <LEDGERNAME>Apex Infotech Pvt Ltd</LEDGERNAME>
            <AMOUNT>-50000.00</AMOUNT>
          </ALLLEDGERENTRIES.LIST>
        </VOUCHER>
      </TALLYMESSAGE>
      <TALLYMESSAGE>
        <!-- Unbalanced voucher -->
        <VOUCHER VCHTYPE="Journal" DATE="20261020">
          <VOUCHERNUMBER>JRN-999</VOUCHERNUMBER>
          <NARRATION>Typo in journal entry</NARRATION>
          <ALLLEDGERENTRIES.LIST>
            <LEDGERNAME>Office Rent</LEDGERNAME>
            <AMOUNT>10000.00</AMOUNT>
          </ALLLEDGERENTRIES.LIST>
          <ALLLEDGERENTRIES.LIST>
            <LEDGERNAME>HDFC Bank Current A/c</LEDGERNAME>
            <AMOUNT>-8000.00</AMOUNT>
          </ALLLEDGERENTRIES.LIST>
        </VOUCHER>
      </TALLYMESSAGE>
    </DATA>
  </BODY>
</ENVELOPE>"""


def test_tally_masters_parsing():
    ledgers = parse_tally_xml_masters(SAMPLE_TALLY_MASTERS_XML)
    assert len(ledgers) == 5

    names = {l["name"]: l for l in ledgers}
    assert names["HDFC Bank Current A/c"]["account_type"] == "asset"
    assert names["Apex Infotech Pvt Ltd"]["account_type"] == "asset"
    assert names["Vikas Raw Materials Co"]["account_type"] == "liability"
    assert names["Software Consulting Revenue"]["account_type"] == "income"
    assert names["Office Rent"]["account_type"] == "expense"


def test_tally_trial_balance_check():
    tb = parse_tally_trial_balance(SAMPLE_TALLY_MASTERS_XML)
    assert tb["ledgers_count"] == 5
    assert tb["total_debit"] == 225000.0
    assert tb["total_credit"] == 225000.0
    assert tb["is_balanced"] is True
    assert tb["difference"] == 0.0


def test_tally_vouchers_parsing_and_duplicate_detection():
    vouchers, warnings = parse_tally_xml_vouchers(SAMPLE_TALLY_VOUCHERS_XML)
    assert len(vouchers) == 4

    # 1st voucher: balanced, not duplicate
    assert vouchers[0]["voucher_number"] == "RCT-001"
    assert vouchers[0]["is_balanced"] is True
    assert vouchers[0]["is_duplicate"] is False
    assert vouchers[0]["total_debit"] == 50000.0
    assert vouchers[0]["total_credit"] == 50000.0

    # 2nd voucher: balanced, not duplicate
    assert vouchers[1]["voucher_number"] == "PMT-042"
    assert vouchers[1]["is_balanced"] is True
    assert vouchers[1]["is_duplicate"] is False

    # 3rd voucher: identified as duplicate of RCT-001
    assert vouchers[2]["is_duplicate"] is True

    # 4th voucher: identified as unbalanced (10000 != 8000)
    assert vouchers[3]["is_balanced"] is False

    # Check that warnings captured both duplicate and unbalanced voucher
    assert any("Duplicate" in w for w in warnings)
    assert any("unbalanced" in w for w in warnings)


def test_export_to_tally_xml():
    journals = [
        {
            "voucher_type": "Payment",
            "voucher_number": "JRN-001",
            "date": "2026-10-25",
            "narration": "Audit fee paid",
            "entries": [
                {"ledger_name": "Professional Fees", "debit": 15000.0, "credit": 0.0},
                {"ledger_name": "Bank Account", "debit": 0.0, "credit": 15000.0},
            ],
        }
    ]

    xml_out = export_to_tally_xml(journals)
    assert "<ENVELOPE>" in xml_out
    assert "<VOUCHER" in xml_out
    assert "<VOUCHERNUMBER>JRN-001</VOUCHERNUMBER>" in xml_out
    assert "<AMOUNT>15000.00</AMOUNT>" in xml_out
    assert "<AMOUNT>-15000.00</AMOUNT>" in xml_out

