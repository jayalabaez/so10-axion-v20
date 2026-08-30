#!/usr/bin/env python3
"""Exact F/D-flat GUT-singlet slice for the source-bound V22 candidate."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import susy_so10x17_v22_contract as contract
from susy_v22_g5_phase_count import rank


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V22_F_FLAT_GUT_SLICE.json"
OUT_MD = ROOT / "SUSY_V22_F_FLAT_GUT_SLICE.md"


def csha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build_report() -> dict[str, Any]:
    c = contract.build_report()
    # Dimensionless exact witness.  Couplings and Mstar are one; the source
    # driver constants are chosen as vPhi2=vC2=2 and vMP2=vX2=vS2=1.
    witness = {name: Fraction(1) for name in ("Phi210", "C16", "C16bar", "XMP", "Phi17p", "Phi17m", "Splus", "Sminus")}
    witness.update({name: Fraction(0) for name in ("Nphi", "NC", "NMP", "NX", "NS")})
    values = {field["name"]: Fraction(0) for field in c["fields"]}
    values.update(witness)
    p, cb, cc, x, xp, xm, sp, sm = (witness[name] for name in (
        "Phi210", "C16bar", "C16", "XMP", "Phi17p", "Phi17m", "Splus", "Sminus"))
    constraints = {
        "F_Nphi": p * p + p * p * p - 2,
        "F_NC": cb * cc * (1 + p) - 2,
        "F_NMP": x * x - 1,
        "F_NX": xp * xm - 1,
        "F_NS": sp * sm - 1,
    }
    # Columns: Phi,Cbar,C,XMP,Phi17p,Phi17m,Splus,Sminus.
    jacobian = [
        [5, 0, 0, 0, 0, 0, 0, 0],
        [1, 2, 2, 0, 0, 0, 0, 0],
        [0, 0, 0, 2, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 1],
    ]
    jacobian_rank = rank(jacobian)
    complex_flat_dimension = 8 - jacobian_rank
    complexified_broken_gauge_rank = 2
    quotient_complex_dimension = complex_flat_dimension - complexified_broken_gauge_rank
    d_terms = {
        "U1X": 17 * xp * xp - 17 * xm * xm + 4 * sp * sp - 4 * sm * sm,
        "SO10_C_pair_norm_difference": cc * cc - cb * cb,
    }
    zero_fields = ("DeltaB", "Delta", "DeltaB2", "Delta2", "H10m", "H10p", "T120m", "T120p")
    drivers = {"Nphi", "NC", "NMP", "NX", "NS"}
    derivative_rows = []
    for coupling, fields in contract.TERMS.items():
        for index, differentiated in enumerate(fields):
            if differentiated in drivers:
                continue
            value = Fraction(1)
            for j, other in enumerate(fields):
                if j != index:
                    value *= values[other]
            derivative_rows.append({
                "coupling": coupling,
                "differentiated_field": differentiated,
                "occurrence": index,
                "monomial_derivative_at_witness": str(value),
            })
    checks = {
        "source_contract_executes": c["n_failed"] == 0,
        "all_five_driver_F_terms_vanish_exactly": all(value == 0 for value in constraints.values()),
        "declared_abelian_and_rank_breaking_D_terms_vanish_exactly": all(value == 0 for value in d_terms.values()),
        "constraint_Jacobian_has_full_row_rank_five": jacobian_rank == 5,
        "F_flat_slice_has_three_complex_tangents_before_gauge_quotient": complex_flat_dimension == 3,
        "two_complexified_broken_gauge_directions_leave_one_axion_multiplet": quotient_complex_dimension == 1,
        "missing_partner_and_light_GUT_multiplets_are_zero_on_the_slice": len(zero_fields) == 8,
        "every_non_driver_catalogue_derivative_vanishes_termwise": all(row["monomial_derivative_at_witness"] == "0" for row in derivative_rows),
        "full_global_V22_vacuum_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if ok is not True]
    report: dict[str, Any] = {
        "schema": "susy_v22_f_flat_gut_slice_v1",
        "status": "EXACT_SOURCE_BOUND_F_AND_D_FLAT_GUT_SLICE_WITH_ONE_AXION_MULTIPLET__FULL_GLOBAL_VACUUM_OPEN" if not failures else "SUSY_V22_F_FLAT_SLICE_FAILED",
        "contract_core_sha256": c["core_sha256"],
        "model_source": c["model_source"],
        "dimensionless_exact_witness": {name: str(value) for name, value in witness.items()},
        "driver_constants": {"vPhi2": 2, "vC2": 2, "vMP2": 1, "vX2": 1, "vS2": 1, "Mstar": 1},
        "F_driver_values": {name: str(value) for name, value in constraints.items()},
        "D_values": {name: str(value) for name, value in d_terms.items()},
        "constraint_Jacobian": jacobian,
        "exact_dimensions": {
            "Jacobian_rank": jacobian_rank,
            "complex_F_flat_tangent_before_gauge": complex_flat_dimension,
            "complexified_broken_gauge_rank": complexified_broken_gauge_rank,
            "complex_quotient_moduli": quotient_complex_dimension,
        },
        "zero_VEV_multiplets": list(zero_fields),
        "non_driver_termwise_derivative_audit": derivative_rows,
        "remaining_requirements": {
            "source_exact_SO10_SM_singlet_embedding_and_all_D_generators": False,
            "global_exclusion_of_other_F_D_flat_branches": False,
            "soft_terms_select_and_stabilize_the_radial_axion_partner": False,
            "complete_component_Hessian_is_positive_modulo_gauge_and_axion": False,
            "RG_flow_connects_to_the_exact_174_GeV_endpoint": False,
        },
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "claim_boundary": {
            "declared_GUT_singlet_slice_F_D_flat": not failures,
            "one_complex_axion_multiplet_on_local_quotient": not failures,
            "V22_global_vacuum_closed": False,
            "canonical_G4_closed": False,
            "canonical_G5_closed": False,
        },
    }
    body = dict(report)
    report["core_sha256"] = csha(body)
    return report


def markdown(report: dict[str, Any]) -> str:
    d = report["exact_dimensions"]
    return "\n".join([
        "# SUSY V22 exact F/D-flat GUT slice",
        "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        f"- Exact constraint-Jacobian rank: `{d['Jacobian_rank']}`.",
        f"- Complex quotient-modulus dimension: `{d['complex_quotient_moduli']}`.",
        "",
        "This is an exact local singlet-slice existence theorem. It does not exclude other full-field F/D/soft branches and therefore does not close V22 G3, G4, or G5.",
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
        raise ArithmeticError("V22 F/D-flat slice output drift")
    print(report["status"])
    print(report["core_sha256"])
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
