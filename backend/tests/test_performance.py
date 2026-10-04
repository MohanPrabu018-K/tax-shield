"""P14.3 performance/load benchmarks — in-process, deterministic, no server.

Thresholds are generous (slow shared runners); they catch regressions
(10x blowups), not rank hardware. Live API load plan: docs/LOAD_TEST_PLAN.md.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.analysis import TaxAnalysisEngine
from app.rules import registry
from app.accounting import trial_balance, COA
from app.intel import detect_anomalies


def _bench(fn, *args, iters=200):
    t0 = time.perf_counter()
    for _ in range(iters):
        fn(*args)
    return (time.perf_counter() - t0) / iters * 1000


def test_tax_calc_throughput():
    eng = TaxAnalysisEngine()
    ms = _bench(eng.compute_tax_detailed, 850000, "old")
    assert ms < 5, f"tax calc too slow: {ms:.2f}ms/op"


def test_registry_lookup_throughput():
    ms = _bench(registry.slab_params, "old", None)
    assert ms < 5, f"registry lookup too slow: {ms:.2f}ms/op"


def _big_ledger(n=2000):
    accts = [{"code": c, "name": v["name"], "type": v["type"]} for c, v in COA.items()]
    journals = [{"_id": str(i), "status": "posted",
                 "lines": [{"account_code": "1010", "debit": 100, "credit": 0},
                           {"account_code": "4000", "debit": 0, "credit": 100}]}
                for i in range(n)]
    return accts, journals


def test_trial_balance_2k_journals():
    accts, journals = _big_ledger()
    t0 = time.perf_counter()
    tb = trial_balance(accts, journals)
    ms = (time.perf_counter() - t0) * 1000
    assert tb["balanced"] and tb["total_debit"] == 200000
    assert ms < 1000, f"2k-journal TB too slow: {ms:.0f}ms"


def test_anomaly_scan_2k_transactions():
    txs = [{"_id": str(i), "date": "2024-06-01", "description": f"Vendor payment {i % 50}",
            "amount": 100 + (i % 7)} for i in range(2000)]
    t0 = time.perf_counter()
    flags = detect_anomalies(txs)
    ms = (time.perf_counter() - t0) * 1000
    assert isinstance(flags, list)
    assert ms < 2000, f"2k-tx anomaly scan too slow: {ms:.0f}ms"
