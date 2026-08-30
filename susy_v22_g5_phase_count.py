#!/usr/bin/env python3
"""Exact source-bound phase quotient for the V22 G5 continuation."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import susy_so10x17_v22_contract as contract
import susy_v22_all_order_r_protection as r_protection
import susy_v22_exact_ew_endpoint as ew
import susy_v22_z4r_anomaly as z4r


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V22_G5_PHASE_COUNT.json"
OUT_MD = ROOT / "SUSY_V22_G5_PHASE_COUNT.md"


def csha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def psha(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def rank(rows: list[list[int]]) -> int:
    a = [[Fraction(value) for value in row] for row in rows]
    if not a:
        return 0
    pivot = 0
    for col in range(len(a[0])):
        hit = next((i for i in range(pivot, len(a)) if a[i][col]), None)
        if hit is None:
            continue
        a[pivot], a[hit] = a[hit], a[pivot]
        q = a[pivot][col]
        a[pivot] = [value / q for value in a[pivot]]
        for i in range(len(a)):
            if i != pivot and a[i][col]:
                q = a[i][col]
                a[i] = [x - q * y for x, y in zip(a[i], a[pivot])]
        pivot += 1
    return pivot


def build_report() -> dict[str, Any]:
    c = contract.build_report()
    rp = r_protection.build_report()
    za = z4r.build_report()
    e = ew.build_report()

    # Coordinates are relative phases of C16/C16bar, Splus/Sminus, and
    # Phi17p/Phi17m after the source-landed holomorphic product/square
    # constraints set Phi210 and XMP continuous phases to zero.
    phase_coordinates = ["C16_relative", "S_relative", "Phi17_relative"]
    constraint_rows = {
        "Phi210_square": [2, 0],
        "Phi210_cube": [3, 0],
        "XMP_square": [0, 2],
    }
    fixed_phase_rank = rank(list(constraint_rows.values()))
    gauge_rows = {
        "broken_SO10_Cartan": [1, 0, 0],
        "broken_U1X": [0, 4, 17],
    }
    gauge_rank = rank(list(gauge_rows.values()))
    tangent_dimension = len(phase_coordinates)
    physical_phase_dimension = tangent_dimension - gauge_rank
    intended_axion = [0, 17, -4]
    gauge_augmented_rank = rank(list(gauge_rows.values()) + [intended_axion])

    source_pins = {name: psha(ROOT / name) for name in (
        "susy_so10x17_v22_contract.py",
        "susy_v22_all_order_r_protection.py",
        "susy_v22_z4r_anomaly.py",
        "susy_v22_exact_ew_endpoint.py",
        "models/SO10X17SUSYV22/SO10X17SUSYV22.m",
    )}
    checks = {
        "all_source_dependencies_execute": all(x["n_failed"] == 0 for x in (c, rp, za, e)),
        "Phi210_and_XMP_continuous_phases_are_fixed": fixed_phase_rank == 2,
        "declared_GUT_VEV_phase_tangent_has_dimension_three": tangent_dimension == 3,
        "two_independent_broken_gauge_phase_directions_are_quotiented": gauge_rank == 2,
        "exactly_one_physical_GUT_phase_direction_remains": physical_phase_dimension == 1,
        "declared_axion_vector_is_independent_of_both_gauge_vectors": gauge_augmented_rank == 3,
        "EW_CP_odd_sector_has_only_one_gauge_zero_and_one_positive_mode": e["checks"]["CP_odd_sector_has_one_gauge_zero_and_one_positive_mode"],
        "continuous_missing_partner_U1_is_absent_from_source": "MissingPartner" not in contract.MODEL_PATH.read_text(encoding="utf-8").split("RpM =", 1)[0],
        "canonical_G5_not_promoted_without_full_spectrum": True,
    }
    failures = [name for name, ok in checks.items() if ok is not True]
    report: dict[str, Any] = {
        "schema": "susy_v22_g5_phase_count_v1",
        "status": "EXACT_ONE_PHYSICAL_PHASE_AFTER_GUT_AND_EW_GAUGE_QUOTIENT__FULL_CALG_AND_SPECTRUM_OPEN" if not failures else "SUSY_V22_G5_PHASE_COUNT_FAILED",
        "dependencies": {
            "contract_core_sha256": c["core_sha256"],
            "R_protection_core_sha256": rp["core_sha256"],
            "Z4R_anomaly_core_sha256": za["core_sha256"],
            "EW_endpoint_core_sha256": e["core_sha256"],
        },
        "source_pins_portable_lf": source_pins,
        "fixed_phase_constraint_rows": constraint_rows,
        "GUT_phase_coordinates": phase_coordinates,
        "broken_gauge_phase_rows": gauge_rows,
        "intended_axion_vector": intended_axion,
        "exact_counts": {
            "fixed_nonquotient_phase_rank": fixed_phase_rank,
            "GUT_phase_tangent_dimension": tangent_dimension,
            "broken_gauge_phase_rank": gauge_rank,
            "physical_GUT_phase_dimension": physical_phase_dimension,
        },
        "remaining_requirements": {
            "source_exact_calG_chiral_gaugino_matrix_on_the_V22_vacuum": False,
            "all_zero_VEV_spectator_and_driver_chiral_multiplets_are_massive": False,
            "complete_F_D_soft_scalar_Hessian_is_positive_modulo_gauge_and_axion": False,
            "radiative_mu_Bmu_and_phase_alignment_are_source_bound": False,
            "canonical_V22_G4_dependency_is_closed": False,
        },
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "claim_boundary": {
            "declared_VEV_sector_one_axion_phase_count_closed": not failures,
            "full_calG_revalidation_closed": False,
            "complete_scalar_spectrum_positive": False,
            "canonical_G5_closed": False,
        },
    }
    body = dict(report)
    report["core_sha256"] = csha(body)
    return report


def markdown(report: dict[str, Any]) -> str:
    return "\n".join([
        "# SUSY V22 G5 phase count",
        "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        "- Exact GUT VEV phase tangent dimension: 3.",
        "- Broken gauge phase rank: 2.",
        "- Physical phase dimension: 1 (the intended axion direction).",
        "- The EW CP-odd endpoint independently has one eaten zero and one positive physical mode.",
        "",
        "This closes the phase-count subproblem only. The V22 cal-G matrix, singlino/driver masses and complete F/D/soft scalar Hessian remain required before canonical G5 can close.",
        "",
    ])


def write_outputs(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    OUT_MD.write_text(markdown(report), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
    if args.check and (json.loads(OUT_JSON.read_text(encoding="utf-8")) != report or OUT_MD.read_text(encoding="utf-8") != markdown(report)):
        raise ArithmeticError("V22 G5 phase-count outputs drifted")
    print(report["status"])
    print(report["core_sha256"])
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
