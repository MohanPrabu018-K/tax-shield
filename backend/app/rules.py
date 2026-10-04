"""Versioned deterministic rule registry (Phase 2).

The live TaxAnalysisEngine keeps working unchanged: this registry SHADOWS
the current hardcoded values with provenance + effective FY ranges +
activate/rollback semantics. Engine lookups fall back to the legacy
hardcoded defaults, so behavior is identical until a rule version is
explicitly activated after tests pass.

Lifecycle: DRAFT -> VALIDATING -> TESTED -> APPROVED -> ACTIVE (or REJECTED).
Activation never overwrites history; rollback re-points `active_version`.

Rule document shape (conceptual, per master spec):
  jurisdiction/domain/law/section/rule_type/parameters/conditions/
  effective_from/effective_until/tax_period/source/source_version/
  validation_status/approved_by/activated_at/checksum
"""
import hashlib
import json
from copy import deepcopy
from datetime import datetime

from app.tax_periods import parse_fy

DOMAIN_INCOME_TAX = "INCOME_TAX"

# Seed = exact values the engine uses today (analysis.py). Any change to
# statutory numbers MUST go through a new version + regression gate.
_SEED_VERSIONS = [
    {
        "version": 1,
        "domain": DOMAIN_INCOME_TAX,
        "law": "Income-tax Act, 1961 (slab provisions as applied by engine)",
        "section": "slab/87A/surcharge/cess",
        "rule_type": "slab_table",
        "status": "ACTIVE",
        "tax_periods": ["2024-25"],
        "parameters": {
            "old": {
                "slabs": [[250000, 0.0], [500000, 0.05], [750000, 0.10],
                          [1000000, 0.15], [1250000, 0.20], [1500000, 0.25],
                          ["inf", 0.30]],
                "rebate_limit": 500000, "rebate_max": 12500,
            },
            "new": {
                "slabs": [[300000, 0.0], [600000, 0.05], [900000, 0.10],
                          [1200000, 0.15], [1500000, 0.20], ["inf", 0.30]],
                "rebate_limit": 700000, "rebate_max": 25000,
            },
            "surcharge": {"over_50L": 0.10, "over_1Cr": 0.15, "over_2Cr": 0.25,
                          "new_regime_cap": 0.25},
            "cess": 0.04,
            "thresholds": {"freelance_invoice": 50000,
                           "advance_tax_threshold": 10000,
                           "advance_tax_trigger_multiplier": 100,
                           "ais_high_risk_diff": 50000,
                           "recon_match_tolerance": 1},
            "readiness_weights": {"documentation": 0.30, "compliance": 0.25,
                                  "reconciliation": 0.20, "tax_accuracy": 0.15,
                                  "actionability": 0.10},
        },
        "source": {"authority": "engine-baseline",
                   "title": "Values as implemented by TaxAnalysisEngine (pre-versioning)",
                   "url": None, "publication_date": None, "retrieved_date": "2026-10-02"},
        "approved_by": "baseline",
        "activated_at": "2026-10-02T00:00:00Z",
    }
]


def _checksum(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


class RuleRegistry:
    """In-memory registry with optional Mongo persistence for snapshots."""

    def __init__(self) -> None:
        self._versions: dict[int, dict] = {}
        self._active_version: int | None = None
        for seed in _SEED_VERSIONS:
            self._store(seed["version"], seed, seed["status"])

    def _store(self, version: int, doc: dict, status: str) -> dict:
        snap = deepcopy(doc)
        snap["version"] = version
        snap["validation_status"] = status
        snap["checksum"] = _checksum({k: v for k, v in snap.items() if k != "checksum"})
        self._versions[version] = snap
        if status == "ACTIVE":
            self._active_version = version
        return snap

    # ---- reads (engine path) ----
    def active(self) -> dict:
        assert self._active_version is not None
        return deepcopy(self._versions[self._active_version])

    def get(self, version: int) -> dict:
        if version not in self._versions:
            raise KeyError(f"rule version {version} not found")
        return deepcopy(self._versions[version])

    def versions(self) -> list[dict]:
        return [deepcopy(v) for _, v in sorted(self._versions.items())]

    def slab_params(self, regime: str, tax_period: str | None = None) -> dict:
        """Slab params for a regime; validates the tax period parses as FY."""
        if tax_period is not None:
            parse_fy(tax_period)  # raises ValueError on bad period
        params = self.active()["parameters"]
        if regime not in ("old", "new"):
            regime = "old"
        return deepcopy(params[regime])

    # ---- lifecycle (admin path; tests must pass before ACTIVE) ----
    def propose(self, parameters: dict, *, domain: str = DOMAIN_INCOME_TAX,
                tax_periods: list[str], law: str = "", section: str = "",
                source: dict | None = None) -> dict:
        for fy in tax_periods:
            parse_fy(fy)
        version = max(self._versions) + 1
        return self._store(version, {
            "domain": domain, "law": law, "section": section,
            "rule_type": "slab_table", "status": "DRAFT",
            "tax_periods": tax_periods, "parameters": deepcopy(parameters),
            "source": source or {}, "approved_by": None, "activated_at": None,
        }, "DRAFT")

    def mark(self, version: int, status: str) -> dict:
        allowed = {"DRAFT", "VALIDATING", "TESTED", "APPROVED", "ACTIVE", "REJECTED"}
        if status not in allowed:
            raise ValueError(f"bad status {status}")
        snap = self.get(version)
        snap["validation_status"] = status
        if status == "ACTIVE":
            self._active_version = version
            snap["activated_at"] = datetime.utcnow().isoformat() + "Z"
        self._versions[version] = snap
        return deepcopy(snap)

    def activate(self, version: int) -> dict:
        snap = self.get(version)
        if snap["validation_status"] not in ("TESTED", "APPROVED", "ACTIVE"):
            raise ValueError("Only TESTED/APPROVED versions can be activated. "
                             "Run the regression suite first; fail-closed.")
        return self.mark(version, "ACTIVE")

    def rollback(self, version: int) -> dict:
        """Rollback = re-activate a prior version. History is never deleted."""
        return self.activate(version)


registry = RuleRegistry()
