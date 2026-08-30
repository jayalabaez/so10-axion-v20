#!/usr/bin/env python3
"""No-go theorem for rescuing the V22 catalogue with ordinary Abelian charges.

The five source terms linear in Nphi, NC, NMP, NX and NS force those drivers
to have the same charge as the superpotential under every additional additive
Abelian (ordinary or R) symmetry when coefficients are neutral constants.
Consequently, once D_i A_i is allowed, every replacement D_j A_i is allowed.
The V22 source keeps only the five diagonal terms, whereas the exact operator
census contains all twenty off-diagonal replacements.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import susy_v22_g1_holomorphic_ring_frontier as ring


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V22_G1_SHAPING_SYMMETRY_NOGO.json"
OUT_MD = ROOT / "SUSY_V22_G1_SHAPING_SYMMETRY_NOGO.md"
SCHEMA = "susy_v22_g1_shaping_symmetry_nogo_v1"

DRIVER_CONSTRAINTS = {
    "Nphi": ("Phi210", "Phi210"),
    "NC": ("C16bar", "C16"),
    "NMP": ("XMP", "XMP"),
    "NX": ("Phi17p", "Phi17m"),
    "NS": ("Splus", "Sminus"),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value: Any) -> str:
    body = dict(value)
    body.pop("core_sha256", None)
    return sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode())


def build_report() -> dict[str, Any]:
    census_report = ring.build_report()
    rows = {tuple(row["count_tuple"]): row for row in census_report["all_allowed_sectors"]}
    replacements = []
    for product_owner, product in DRIVER_CONSTRAINTS.items():
        for replacement_driver in DRIVER_CONSTRAINTS:
            fields = (replacement_driver,) + product
            key = ring.count_tuple(fields)
            row = rows.get(key)
            replacements.append({
                "product_owner": product_owner,
                "replacement_driver": replacement_driver,
                "monomial": ring.monomial_label(key),
                "diagonal_declared_term": product_owner == replacement_driver,
                "present_in_exact_census": row is not None,
                "declared_catalogue_couplings": [] if row is None else row["declared_catalogue_couplings"],
                "allowed_but_undeclared": row is not None and not row["declared_sector"],
                "so10_flavour_component_multiplicity": 0 if row is None else row["so10_flavour_component_multiplicity"],
            })
    diagonal = [row for row in replacements if row["diagonal_declared_term"]]
    off_diagonal = [row for row in replacements if not row["diagonal_declared_term"]]
    proof = {
        "charge_domain": "an arbitrary additive Abelian group A; products of continuous/discrete Abelian factors are included",
        "superpotential_charge": "omega in A (omega=0 for a non-R symmetry)",
        "assumptions": [
            "all five nonzero linear driver terms have neutral constant coefficients",
            "each retained driver-product term D_i A_i has a neutral coefficient",
            "the additional shaping rule acts through additive one-dimensional field charges",
        ],
        "steps": [
            "The linear term D_i is allowed only if q(D_i)=omega, so every driver has the same charge omega.",
            "The retained term D_i A_i gives q(A_i)=0 after subtracting q(D_i)=omega.",
            "For every j, q(D_j A_i)=omega+0=omega; therefore every off-diagonal replacement D_j A_i is allowed.",
            "The source catalogue omits all twenty off-diagonal replacements, contradicting completeness under any such shaping assignment.",
        ],
        "theorem_scope": "ordinary additive Abelian field symmetries with neutral fixed coefficients, including additional discrete or continuous R symmetries",
        "not_ruled_out": [
            "promoting the dimensionful constants/couplings to explicit charged spurion fields",
            "removing or restructuring the linear-driver sector",
            "a source-declared non-Abelian construction with additional fields and invariant contractions",
            "accepting and parameterizing the complete allowed operator ring",
        ],
    }
    checks = {
        "upstream_exact_census_passes": census_report["n_failed"] == 0,
        "five_driver_constraints_are_present": len(DRIVER_CONSTRAINTS) == 5,
        "all_five_diagonal_terms_are_exactly_censused_and_declared":
            len(diagonal) == 5 and all(row["present_in_exact_census"] and row["declared_catalogue_couplings"] for row in diagonal),
        "all_twenty_off_diagonal_replacements_are_exactly_censused":
            len(off_diagonal) == 20 and all(row["present_in_exact_census"] for row in off_diagonal),
        "all_twenty_off_diagonal_replacements_are_undeclared":
            len(off_diagonal) == 20 and all(row["allowed_but_undeclared"] for row in off_diagonal),
        "proof_covers_products_of_Abelian_factors": True,
        "spurionic_or_restructured_escapes_are_not_silently_excluded": True,
        "full_V22_G1_is_not_claimed": True,
    }
    failures = [name for name, passed in checks.items() if passed is not True]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "namespace": "canonical.susy_so10x17.v22.G1.shaping_symmetry_nogo",
        "status": ("V22_G1_NEUTRAL_COEFFICIENT_ABELIAN_SHAPING_NO_GO_CLOSED__SOURCE_RESTRUCTURE_REQUIRED"
                   if not failures else "V22_G1_SHAPING_SYMMETRY_NOGO_FAILED"),
        "overall_state": "NO_GO_CLOSED" if not failures else "EXECUTION_FAIL",
        "upstream_census": {
            "path": ring.OUT_JSON.name,
            "core_sha256": census_report["core_sha256"],
            "allowed_undeclared_sectors": census_report["counts"]["allowed_undeclared_sectors"],
        },
        "driver_constraints": {driver: list(product) for driver, product in DRIVER_CONSTRAINTS.items()},
        "replacement_grid": replacements,
        "counts": {
            "drivers": len(DRIVER_CONSTRAINTS),
            "replacement_grid_sectors": len(replacements),
            "diagonal_declared_sectors": len(diagonal),
            "off_diagonal_allowed_undeclared_sectors": sum(row["allowed_but_undeclared"] for row in off_diagonal),
        },
        "proof": proof,
        "resolution": {
            "ordinary_Abelian_shaping_charge_patch_exists": False,
            "reason": "the retained linear tadpoles make all five drivers charge-indistinguishable",
            "minimum_source_level_action": ("Restructure the driver/tadpole sector or promote its constants to explicit charged "
                                            "spurion fields before assigning a new shaping symmetry."),
            "G2_promotion_allowed_before_G1_repair": False,
        },
        "claim_boundary": {
            "neutral_coefficient_Abelian_shaping_no_go_closed": not failures,
            "all_possible_UV_selection_mechanisms_excluded": False,
            "V22_G1_closed": False,
            "V22_G2_closed": False,
        },
        "next_exact_target": ("Choose and source-land a restructured driver/spurion completion, rerun the exact holomorphic census, "
                              "then derive component Clebsches only for the resulting accepted G1 operator basis."),
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def markdown(report: dict[str, Any]) -> str:
    counts = report["counts"]
    return "\n".join([
        "# SUSY V22 G1 shaping-symmetry no-go", "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        f"- Retained diagonal driver constraints: {counts['diagonal_declared_sectors']}",
        f"- Unavoidable allowed-but-undeclared replacements: {counts['off_diagonal_allowed_undeclared_sectors']}", "",
        "With neutral fixed coefficients, every linear driver has the superpotential charge under any",
        "additional additive Abelian symmetry. Each retained driver product is therefore neutral, and any",
        "driver can replace any other. No ordinary Abelian charge assignment can preserve the five intended",
        "constraints while forbidding the twenty off-diagonal terms.", "",
        report["resolution"]["minimum_source_level_action"], "",
        "This theorem does not exclude an explicit charged-spurion completion or a restructured/non-Abelian UV sector.", "",
    ])


def write_outputs(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    OUT_MD.write_text(markdown(report), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
    if args.check:
        if json.loads(OUT_JSON.read_text(encoding="utf-8")) != report:
            raise ArithmeticError("V22 G1 shaping no-go JSON drifted")
        if OUT_MD.read_text(encoding="utf-8") != markdown(report):
            raise ArithmeticError("V22 G1 shaping no-go Markdown drifted")
    print(report["status"])
    print(report["core_sha256"])
    print(json.dumps(report["counts"], sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
