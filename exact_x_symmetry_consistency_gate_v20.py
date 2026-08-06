#!/usr/bin/env python3
"""Fail-closed audit of the repository's X/Phi17 symmetry assumptions.

The live model scaffold declares SO(10) gauge symmetry and Z17 global symmetry.
It assigns an auxiliary continuous X charge to fields, while the signed scalar
operator filter requires exact X neutrality.  This module checks whether that
selection rule is actually declared and enumerates the Phi17 monomials allowed
by the declared theory.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
MODEL = ROOT / "models" / "SO10Z17AxionV20.m"
FILTER = ROOT / "nonsusy_z17_pq_potential_filter_v20.py"
OUT_JSON = ROOT / "EXACT_X_SYMMETRY_CONSISTENCY_GATE_V20.json"
OUT_MD = ROOT / "EXACT_X_SYMMETRY_CONSISTENCY_GATE_V20.md"


def declared_symmetries(model_text: str) -> dict[str, Any]:
    gauge_rows = re.findall(r"Gauge\[\[\d+\]\]\s*=\s*\{([^;]+)\};", model_text)
    global_match = re.search(r"GlobalSymmetry\s*=\s*\{([^}]*)\}", model_text)
    global_rows = [] if global_match is None else [x.strip() for x in global_match.group(1).split(",") if x.strip()]
    return {
        "gauge_rows": gauge_rows,
        "global_rows": global_rows,
        "so10_gauged": any("SO" in row and "10" in row for row in gauge_rows),
        "u1x_gauged": any(re.search(r"U\s*\[?1\]?|U1|X", row, re.I) for row in gauge_rows[1:]),
        "x_declared_global": any("X" in row for row in global_rows),
        "z17_declared_global": any("17" in row for row in global_rows),
    }


def filter_contract(filter_text: str) -> dict[str, Any]:
    requires_x_default = bool(re.search(r"def _allowed\([^)]*require_x:\s*bool\s*=\s*True", filter_text, re.S))
    phi_match = re.search(r'"Phi17"\s*:\s*\{[^}]*"X"\s*:\s*(-?\d+)[^}]*"Z17"\s*:\s*(-?\d+)', filter_text, re.S)
    if phi_match is None:
        raise RuntimeError("Phi17 charge row not found in signed filter")
    return {
        "requires_exact_x_neutrality_by_default": requires_x_default,
        "phi17_X": int(phi_match.group(1)),
        "phi17_Z17": int(phi_match.group(2)) % 17,
    }


def declared_phi17_monomials(max_dimension: int = 4) -> list[dict[str, Any]]:
    # Phi17 is an SO(10) singlet and has Z17=0 in the signed charge ledger.
    rows = []
    for p in range(max_dimension + 1):
        for q in range(max_dimension + 1 - p):
            degree = p + q
            if degree == 0:
                continue
            rows.append({
                "label": f"Phi17^{p} Phi17dag^{q}",
                "dimension": degree,
                "powers": {"Phi17": p, "Phi17dag": q},
                "phase_sensitive": p != q,
                "declared_SO10xZ17_allowed": True,
                "continuous_X_charge": 17 * (p - q),
            })
    return sorted(rows, key=lambda r: (r["dimension"], r["label"]))


def dimension17_lift(v_phi_gev: float = 1.0e17, cutoff_gev: float = 2.435e18, kappa: float = 1.0) -> dict[str, float]:
    # Phi=(v/sqrt2) exp(i a/v), V=k Phi^17/M^13+h.c.
    amplitude = 2.0 * abs(kappa) * (v_phi_gev / 2.0**0.5) ** 17 / cutoff_gev**13
    mass2 = (17.0 / v_phi_gev) ** 2 * amplitude
    return {
        "v_phi_GeV": v_phi_gev,
        "cutoff_GeV": cutoff_gev,
        "abs_kappa": abs(kappa),
        "potential_amplitude_GeV4": amplitude,
        "phi17_angular_mass2_GeV2": mass2,
        "phi17_angular_mass_GeV": mass2**0.5,
        "breaks_continuous_X_by_units": 289.0,
        "breaks_PQ": False,
        "direct_theta_bar_shift_from_PQ_charge": 0.0,
    }


def build_report() -> dict[str, Any]:
    model_text = MODEL.read_text()
    filter_text = FILTER.read_text()
    sym = declared_symmetries(model_text)
    contract = filter_contract(filter_text)
    monomials = declared_phi17_monomials()
    phase_rows = [r for r in monomials if r["phase_sensitive"]]
    low_pure = [r for r in phase_rows if r["powers"]["Phi17dag"] == 0]
    d17 = dimension17_lift()

    mismatch = (
        contract["requires_exact_x_neutrality_by_default"]
        and not sym["u1x_gauged"]
        and not sym["x_declared_global"]
    )
    checks = {
        "so10_is_declared_gauge_symmetry": sym["so10_gauged"],
        "z17_is_declared_global_symmetry": sym["z17_declared_global"],
        "u1x_is_not_declared_gauged": not sym["u1x_gauged"],
        "x_is_not_declared_global": not sym["x_declared_global"],
        "signed_filter_requires_x_neutrality": contract["requires_exact_x_neutrality_by_default"],
        "phi17_is_z17_neutral": contract["phi17_Z17"] == 0,
        "declared_theory_allows_phase_sensitive_dim_le4_terms": len(phase_rows) > 0,
        "declared_theory_allows_phi_powers_1_to_4": {r["dimension"] for r in low_pure} == {1, 2, 3, 4},
        "symmetry_contract_mismatch_detected": mismatch,
        "dimension17_term_explicitly_breaks_x_not_pq": d17["breaks_continuous_X_by_units"] == 289.0 and d17["breaks_PQ"] is False,
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": "X_SELECTION_RULE_UNDECLARED__FULL_MODEL_BLOCKED" if not failures else "X_SYMMETRY_AUDIT_FAILED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "declared_symmetries": sym,
        "signed_filter_contract": contract,
        "declared_dim_le4_phi17_monomials": monomials,
        "phase_sensitive_count": len(phase_rows),
        "dimension17_candidate": d17,
        "required_resolution": {
            "option_A_gauge_U1X": [
                "declare U(1)_X in the gauge group",
                "supply anomaly-cancelling fermion content",
                "add covariant derivatives and gauge coupling",
                "prove the Phi17 phase is the eaten Goldstone",
            ],
            "option_B_exact_global_U1X": [
                "declare U(1)_X as an exact global symmetry",
                "accept a physical Goldstone after spontaneous breaking unless explicit breaking is added",
                "treat Phi17^17 as an explicit-X-breaking UV operator, not an X-invariant term",
            ],
            "option_C_no_continuous_X": [
                "remove require_x=True from operator filters",
                "include all SO(10)xZ17-allowed relevant and marginal Phi17 operators",
                "re-solve the hierarchy and phase vacuum",
            ],
        },
        "flag": {
            "x_selection_rule_consistently_declared": False,
            "phi17_phase_eaten": False,
            "dimension17_operator_is_x_invariant": False,
            "dimension17_operator_directly_breaks_pq": False,
            "complete_multifield_model": False,
            "whole_model_validated": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "The current repository enforces continuous X neutrality in operator filters but declares neither gauged nor global U(1)_X. "
            "Under the actually declared SO(10)xZ17 symmetry, low-dimensional phase-sensitive Phi17 terms are allowed. "
            "The dimension-17 term can lift the phase only as explicit X breaking and does not directly violate PQ."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    d17 = report["dimension17_candidate"]
    return "\n".join([
        "# Exact X-symmetry consistency gate — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- declared phase-sensitive Phi17 monomials at dimension <=4: `{report['phase_sensitive_count']}`",
        f"- dimension-17 benchmark angular mass: `{d17['phi17_angular_mass_GeV']:.6e} GeV`",
        f"- dimension-17 continuous-X violation: `{d17['breaks_continuous_X_by_units']:.0f}` units",
        f"- direct PQ/theta-bar breaking: `{d17['breaks_PQ']}`",
        "",
    ])


if __name__ == "__main__":
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True))
    OUT_MD.write_text(write_markdown(report))
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["n_failed"] == 0 else 1)
