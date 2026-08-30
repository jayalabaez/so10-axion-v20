#!/usr/bin/env python3
"""Exact one-loop SO(10) perturbativity window for the corrected V22 EFT."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import susy_so10x17_v22_contract as contract


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V22_PERTURBATIVE_WINDOW.json"
OUT_MD = ROOT / "SUSY_V22_PERTURBATIVE_WINDOW.md"


def q(x: Fraction | int) -> str:
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def csha(v: Any) -> str:
    return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def ln_bounds(value: Fraction, terms: int = 24) -> tuple[Fraction, Fraction]:
    """Rigorous bounds using ln(y)=2*atanh((y-1)/(y+1))."""
    if value <= 1:
        raise ValueError("value must exceed one")
    x = (value - 1) / (value + 1)
    partial = 2 * sum((x ** (2 * n + 1) / (2 * n + 1) for n in range(terms)), Fraction())
    tail = 2 * x ** (2 * terms + 1) / ((2 * terms + 1) * (1 - x * x))
    return partial, partial + tail


def build_report() -> dict[str, Any]:
    report = contract.build_report()
    sum_t = sum(row["multiplicity"] * row["SO10_Dynkin_index"] for row in report["fields"])
    c_adj = 8
    b = sum_t - 3 * c_adj
    alpha_inverse_gut = Fraction(24)
    pi_lower, pi_upper = Fraction(333, 106), Fraction(355, 113)
    ln15_lower, ln15_upper = ln_bounds(Fraction(3, 2))
    ln2_lower, ln2_upper = ln_bounds(Fraction(2))
    # alpha^{-1}(r M_GUT)=alpha^{-1}(M_GUT)-b ln(r)/(2 pi).
    inv15_lower = alpha_inverse_gut - Fraction(b) * ln15_upper / (2 * pi_lower)
    inv15_upper = alpha_inverse_gut - Fraction(b) * ln15_lower / (2 * pi_upper)
    inv2_upper = alpha_inverse_gut - Fraction(b) * ln2_lower / (2 * pi_upper)
    checks = {
        "N1_SO10_one_loop_coefficient_is_exact": sum_t == 296 and b == 272,
        "pi_bounds_are_ordered": pi_lower < pi_upper,
        "log_bounds_are_ordered": 0 < ln15_lower < ln15_upper and 0 < ln2_lower < ln2_upper,
        "coupling_is_finite_through_1p5_MGUT": inv15_lower > 0,
        "one_loop_Landau_pole_occurs_before_2_MGUT": inv2_upper < 0,
        "no_claim_of_Planck_scale_perturbativity": True,
        "canonical_G4_requires_full_tensor_RG_not_only_gauge_one_loop": True,
    }
    failures = [k for k, ok in checks.items() if ok is not True]
    out: dict[str, Any] = {
        "schema": "susy_v22_perturbative_window_v1",
        "status": "EXACT_ONE_LOOP_EFFECTIVE_GUT_WINDOW_TO_1P5_MGUT__UV_COMPLETION_BEFORE_2MGUT_REQUIRED" if not failures else "V22_PERTURBATIVITY_AUDIT_FAILED",
        "contract_core_sha256": report["core_sha256"],
        "one_loop_formula": "alpha^-1(mu)=24-b*ln(mu/MGUT)/(2*pi)",
        "SO10": {"sum_chiral_Dynkin_indices": sum_t, "C2_adjoint": c_adj, "b_one_loop": b},
        "rigorous_rational_bounds": {
            "pi_lower": q(pi_lower), "pi_upper": q(pi_upper),
            "ln_3_over_2_lower": q(ln15_lower), "ln_3_over_2_upper": q(ln15_upper),
            "ln_2_lower": q(ln2_lower), "ln_2_upper": q(ln2_upper),
            "alpha_inverse_at_1p5_MGUT_lower": q(inv15_lower),
            "alpha_inverse_at_1p5_MGUT_upper": q(inv15_upper),
            "alpha_inverse_at_2_MGUT_upper": q(inv2_upper),
        },
        "declared_validity": {
            "controlled_effective_interval": "M_soft <= mu <= 1.5 M_GUT, subject to the still-open full tensor RG audit",
            "mandatory_UV_completion_scale": "strictly below 2 M_GUT in the one-loop benchmark alpha_GUT^-1=24",
            "Planck_scale_completion_claimed": False,
        },
        "checks": checks, "n_checks": len(checks), "n_failed": len(failures), "failures": failures,
        "claim_boundary": {"gauge_one_loop_window_closed": not failures, "all_dimensionless_couplings_perturbative": False,
                           "canonical_G4_closed": False, "canonical_G5_closed": False},
    }
    body = dict(out); out["core_sha256"] = csha(body)
    return out


def markdown(r: dict[str, Any]) -> str:
    return "\n".join(["# SUSY V22 perturbative window", "", f"- Status: `{r['status']}`", f"- Core: `{r['core_sha256']}`",
        f"- Exact one-loop coefficient: `b={r['SO10']['b_one_loop']}`.",
        "- The benchmark remains perturbative through `1.5 M_GUT` but reaches its one-loop Landau pole before `2 M_GUT`.", "",
        "V22 is therefore only a short-distance effective GUT unless an ultraviolet completion is supplied. This result does not by itself close canonical G4.", ""])


def write_outputs(r: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8", newline="\n")
    OUT_MD.write_text(markdown(r), encoding="utf-8", newline="\n")


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--write",action="store_true"); p.add_argument("--check",action="store_true"); a=p.parse_args(); r=build_report()
    if a.write: write_outputs(r)
    if a.check and (json.loads(OUT_JSON.read_text(encoding="utf-8")) != r or OUT_MD.read_text(encoding="utf-8") != markdown(r)):
        raise ArithmeticError("V22 perturbative-window output drift")
    print(r["status"]); print(r["core_sha256"]); return 0 if r["n_failed"] == 0 else 1


if __name__ == "__main__": raise SystemExit(main())
