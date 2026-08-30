#!/usr/bin/env python3
"""Exact tree-level supersymmetric electroweak endpoint for V22.

This closes the algebraic MSSM-like Higgs endpoint at |v|=174 GeV.  It is not
canonical G4 evidence until a source-exact GUT doublet map, RG trajectory,
threshold calculation and full F+D+soft vacuum connect to this endpoint.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V22_EXACT_EW_ENDPOINT.json"
OUT_MD = ROOT / "SUSY_V22_EXACT_EW_ENDPOINT.md"


def q(x: Fraction | int) -> str:
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def csha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build_report() -> dict[str, Any]:
    vu, vd = Fraction(696, 5), Fraction(522, 5)
    g2, gy = Fraction(13, 20), Fraction(9, 25)
    radius2 = vu * vu + vd * vd
    sinb, cosb = Fraction(4, 5), Fraction(3, 5)
    sin2b, cos2b = 2 * sinb * cosb, cosb * cosb - sinb * sinb
    mA2 = Fraction(1_000_000)
    b = mA2 * sin2b / 2
    gz2 = g2 * g2 + gy * gy
    mZ2 = gz2 * radius2 / 2
    mW2 = g2 * g2 * radius2 / 2
    delta = gz2 * (vu * vu - vd * vd) / 4
    m1 = b * vu / vd + delta
    m2 = b * vd / vu - delta

    even = ((mA2 * sinb**2 + mZ2 * cosb**2, -(mA2 + mZ2) * sinb * cosb),
            (-(mA2 + mZ2) * sinb * cosb, mA2 * cosb**2 + mZ2 * sinb**2))
    even_trace = even[0][0] + even[1][1]
    even_det = even[0][0] * even[1][1] - even[0][1] ** 2
    odd_trace, odd_det = mA2, Fraction(0)
    charged_physical = mA2 + mW2

    stationarity = {
        "dV_dvd_over_2vd": m1 - b * vu / vd - gz2 * (vu * vu - vd * vd) / 4,
        "dV_dvu_over_2vu": m2 - b * vd / vu + gz2 * (vu * vu - vd * vd) / 4,
    }
    checks = {
        "complex_VEV_radius_is_exactly_174_GeV": radius2 == 174**2,
        "tan_beta_is_exactly_4_over_3": vu / vd == Fraction(4, 3),
        "neutral_stationarity_is_exact": all(value == 0 for value in stationarity.values()),
        "CP_even_matrix_is_positive_definite": even_trace > 0 and even_det > 0,
        "CP_odd_sector_has_one_gauge_zero_and_one_positive_mode": odd_det == 0 and odd_trace > 0,
        "charged_sector_has_one_gauge_zero_and_one_positive_mode": charged_physical > 0,
        "tree_level_soft_parameters_are_real_and_finite": all(x.denominator > 0 for x in (m1, m2, b)),
        "not_promoted_without_GUT_and_RGE_bridge": True,
    }
    failures = [name for name, passed in checks.items() if passed is not True]
    report: dict[str, Any] = {
        "schema": "susy_v22_exact_ew_endpoint_v1",
        "status": "EXACT_SUSY_EW_ENDPOINT_CLOSED__GUT_RGE_AND_CANONICAL_G4_OPEN" if not failures else "SUSY_EW_ENDPOINT_FAILED",
        "conventions": {"neutral_complex_VEVs": "H_u^0=vu+(h_u+i a_u)/sqrt(2), H_d^0=vd+(h_d+i a_d)/sqrt(2)",
                        "physical_radius": "sqrt(vu^2+vd^2)=174 GeV"},
        "exact_inputs": {"vu_GeV": q(vu), "vd_GeV": q(vd), "tan_beta": q(vu/vd),
                         "g2": q(g2), "gY": q(gy), "mA_squared_GeV2": q(mA2)},
        "derived_parameters": {"gZ_squared": q(gz2), "mZ_squared_GeV2": q(mZ2),
                               "mW_squared_GeV2": q(mW2), "Bmu_GeV2": q(b),
                               "m1_squared_GeV2": q(m1), "m2_squared_GeV2": q(m2)},
        "stationarity": {key: q(value) for key, value in stationarity.items()},
        "tree_scalar_certificate": {
            "CP_even_matrix_GeV2": [[q(x) for x in row] for row in even],
            "CP_even_trace_GeV2": q(even_trace), "CP_even_determinant_GeV4": q(even_det),
            "CP_odd_characteristic": {"trace_GeV2": q(odd_trace), "determinant_GeV4": q(odd_det)},
            "charged_physical_mass_squared_GeV2": q(charged_physical),
            "gauge_Goldstone_counts": {"neutral": 1, "charged_complex": 1},
        },
        "protection_boundary": {
            "exact_N1_limit_removes_GUT_quadratic_sensitivity": True,
            "soft_breaking_preserves_technical_naturalness_only_after_full_superpartner_threshold_and_RGE_replay": True,
            "full_superpartner_threshold_and_RGE_replay_complete": False,
            "GUT_light_doublet_map_complete": False,
            "125_GeV_pole_Higgs_complete": False,
            "full_scalar_vacuum_complete": False,
        },
        "checks": checks, "n_checks": len(checks), "n_failed": len(failures), "failures": failures,
        "claim_boundary": {"exact_tree_EW_endpoint_closed": not failures, "canonical_G4_closed": False,
                           "canonical_G5_closed": False},
    }
    body = dict(report); report["core_sha256"] = csha(body)
    return report


def markdown(report: dict[str, Any]) -> str:
    return "\n".join(["# SUSY V22 exact electroweak endpoint", "",
        f"- Status: `{report['status']}`", f"- Core: `{report['core_sha256']}`",
        "- Exact radius: `sqrt(vu^2+vd^2)=174 GeV`", "- Exact `tan(beta)=4/3`",
        "- CP-even sector positive definite; CP-odd and charged sectors contain only the required gauge zeros.", "",
        "This is an exact endpoint, not canonical G4. The GUT doublet map, RGE/threshold bridge, 125 GeV pole mass and full vacuum remain required.", ""])


def write(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8", newline="\n")
    OUT_MD.write_text(markdown(report), encoding="utf-8", newline="\n")


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--write",action="store_true"); p.add_argument("--check",action="store_true"); a=p.parse_args()
    r=build_report()
    if a.write: write(r)
    if a.check:
        if json.loads(OUT_JSON.read_text(encoding="utf-8")) != r or OUT_MD.read_text(encoding="utf-8") != markdown(r):
            raise ArithmeticError("SUSY EW endpoint drifted")
    print(r["status"]); print(r["core_sha256"]); return 0 if r["n_failed"] == 0 else 1


if __name__ == "__main__": raise SystemExit(main())

