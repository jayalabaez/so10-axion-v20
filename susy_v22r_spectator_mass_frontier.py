#!/usr/bin/env python3
"""Exact spectator-mass frontier for the active V22R EFT truncation.

Z0, Z1 and Z2 were introduced as gauge-singlet discrete-R anomaly
spectators.  This audit checks the complete 108-sector degree<=4 catalogue
and the 67 sectors in the first audited XMP-spurion leakage layer.  That
layer is explicitly not a complete degree-five census.  Neither audited
scope contains a spectator field, so the global-SUSY superpotential Hessian
has three exact zero rows and columns throughout those scopes.

This is a scoped obstruction to the G5 massive-spectator requirement.  It is
not an all-order masslessness theorem: higher operators, supergravity, or a
declared R-breaking soft/hidden sector could change the result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import susy_so10x17_v22_contract as v22


ROOT = Path(__file__).resolve().parent
CATALOGUE_JSON = ROOT / "SUSY_V22R_OPERATOR_CATALOGUE.json"
SPURION_JSON = ROOT / "SUSY_V22R_BROKEN_SELECTOR_SPURION_FRONTIER.json"
CONTRACT_JSON = ROOT / "SUSY_SO10X17_V22R_CONTRACT.json"
OUT_JSON = ROOT / "SUSY_V22R_SPECTATOR_MASS_FRONTIER.json"
OUT_MD = ROOT / "SUSY_V22R_SPECTATOR_MASS_FRONTIER.md"
SCHEMA = "susy_v22r_spectator_mass_frontier_v1"
SPECTATORS = ("Z0", "Z1", "Z2")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value: dict[str, Any]) -> str:
    body = dict(value)
    body.pop("core_sha256", None)
    return sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode())


def load_checked(path: Path) -> dict[str, Any]:
    report = json.loads(path.read_text(encoding="utf-8"))
    expected = report.get("core_sha256")
    if not isinstance(expected, str) or canonical_sha(report) != expected:
        raise ArithmeticError(f"invalid core hash in {path.name}")
    return report


def row_spectators(counts: dict[str, int]) -> list[str]:
    return [name for name in SPECTATORS if int(counts.get(name, 0)) > 0]


def build_report() -> dict[str, Any]:
    catalogue = load_checked(CATALOGUE_JSON)
    spurion = load_checked(SPURION_JSON)
    contract = load_checked(CONTRACT_JSON)

    degree_four_hits = [
        {"sector_id": row["sector_id"], "monomial": row["monomial"],
         "spectators": row_spectators(row["counts"])}
        for row in catalogue["operator_sectors"] if row_spectators(row["counts"])
    ]
    degree_five_rows = [
        row for row in spurion["all_82_exact_lifts"]
        if row["lifted_degree"] == 5 and not row["lifted_is_inside_108_catalogue"]
    ]
    field_names = tuple(contract["field_content"]["field_names"])
    source_fields = {field["name"]: field for field in v22.FIELDS}
    degree_five_hits = []
    for row in degree_five_rows:
        counts = {
            name: int(power)
            for name, power in zip(field_names, row["lifted_count_tuple"]) if power
        }
        hits = row_spectators(counts)
        if hits:
            degree_five_hits.append({"monomial": row["lifted_monomial"], "spectators": hits})

    charges = contract["symmetry"]["Z28R_field_charges"]
    checks = {
        "V22R_contract_passes": contract["n_failed"] == 0,
        "complete_degree_four_catalogue_has_108_sectors":
            len(catalogue["operator_sectors"]) == 108,
        "none_of_the_108_sectors_contains_Z0_Z1_or_Z2": degree_four_hits == [],
        "first_audited_XMP_spurion_leakage_layer_has_67_degree_five_lifts":
            len(degree_five_rows) == 67,
        "none_of_the_67_first_audited_XMP_spurion_leakage_lifts_contains_Z0_Z1_or_Z2":
            degree_five_hits == [],
        "complete_degree_five_census_is_explicitly_not_claimed": True,
        "all_three_spectators_are_SO10_and_U1X_singlets": all(
            source_fields[name]["SO10_dimension"] == 1 and source_fields[name]["X"] == 0
            for name in SPECTATORS
        ),
        "spectator_Z28R_charges_match_the_source":
            {name: charges[name] for name in SPECTATORS} == {"Z0": 20, "Z1": 12, "Z2": 12},
        "global_SUSY_superpotential_Hessian_has_three_zero_spectator_rows_in_scope": True,
        "soft_or_supergravity_mass_generation_is_not_claimed": True,
        "all_order_masslessness_is_not_claimed": True,
    }
    failures = [name for name, passed in checks.items() if passed is not True]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "namespace": "active.susy_so10x17.v22r.G5.spectator_mass_frontier",
        "status": (
            "V22R_THREE_SPECTATOR_CHIRAL_MULTIPLETS_MASSLESS_THROUGH_FIRST_AUDITED_"
            "XMP_SPURION_LEAKAGE_LAYER__NOT_COMPLETE_DEGREE5_CENSUS__G5_OPEN"
            if not failures else "V22R_SPECTATOR_MASS_AUDIT_FAILED"
        ),
        "overall_state": "EXACT_SCOPED_G5_OBSTRUCTION" if not failures else "EXECUTION_FAIL",
        "source_manifest": [
            {"path": path.name, "mode": "raw", "sha256": sha256(path.read_bytes())}
            for path in (CATALOGUE_JSON, SPURION_JSON, CONTRACT_JSON)
        ],
        "spectators": [
            {
                "name": name,
                "SO10": 1,
                "U1X": 0,
                "Z28R": charges[name],
                "degree_le_4_sector_occurrences": 0,
                "first_audited_XMP_spurion_leakage_layer_occurrences": 0,
            }
            for name in SPECTATORS
        ],
        "catalogue_audit": {
            "degree_le_4_sectors": len(catalogue["operator_sectors"]),
            "degree_le_4_spectator_hits": degree_four_hits,
            "first_degree_5_spurion_sectors": len(degree_five_rows),
            "first_degree_5_spectator_hits": degree_five_hits,
            "first_audited_XMP_spurion_leakage_layer": {
                "source_operator_degree": 5,
                "sectors": len(degree_five_rows),
                "spectator_hits": degree_five_hits,
                "complete_degree_five_census": False,
                "scope_statement": (
                    "This is the first audited XMP-spurion leakage layer, not a complete "
                    "degree-five census."
                ),
            },
        },
        "mass_matrix_consequence": {
            "framework": "global N=1 supersymmetry with the declared Wilsonian superpotential",
            "fermion_mass_matrix": "M_ij = partial_i partial_j W",
            "exact_zero_rows_and_columns": list(SPECTATORS),
            "minimum_massless_chiral_multiplets_in_scope": 3,
            "Kahler_metric_can_remove_the_zero_rank_without_additional_mass_sources": False,
            "ordinary_soft_scalar_masses_alone_lift_the_spectator_fermions": False,
        },
        "resolution_options_not_executed": [
            "land higher-dimensional spectator-driver operators and re-solve the driver constraints",
            "add anomaly-consistent R-charge-two spectator partners and rerun the G1 selector/anomalies",
            "declare a source-bound supergravity or R-breaking hidden-sector fermion-mass mechanism",
        ],
        "claim_boundary": {
            "spectator_masslessness_through_degree_four_closed": not failures,
            "spectator_masslessness_through_first_audited_XMP_spurion_leakage_layer_closed":
                not failures,
            "complete_degree_five_census_closed": False,
            "all_order_spectator_masslessness_closed": False,
            "full_soft_and_supergravity_spectrum_closed": False,
            "V22R_G5_massive_spectator_requirement_closed": False,
            "V22R_G5_closed": False,
        },
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def markdown(report: dict[str, Any]) -> str:
    return "\n".join([
        "# SUSY V22R spectator-mass frontier", "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        "- Spectators absent from all 108 degree<=4 sectors: `Z0, Z1, Z2`.",
        "- Spectators absent from all 67 sectors in the first audited XMP-spurion leakage layer: `Z0, Z1, Z2`.",
        "- Complete degree-five census: `not performed`.",
        "- Exact massless global-SUSY chiral multiplets in this scope: at least `3`.", "",
        "The declared superpotential is independent of all three anomaly spectators through the",
        "accepted truncation and the first audited XMP-spurion leakage layer. This layer is not a",
        "complete degree-five census. Within the audited scopes, the fermion Hessian therefore has",
        "three exact zero rows and columns. Kähler normalization or ordinary scalar soft masses",
        "do not by themselves give those fermions a mass.", "",
        "Higher operators, a revised anomaly/selector sector, or a source-bound supergravity/hidden",
        "sector could lift them. None is currently specified, so the G5 massive-spectator requirement",
        "and full V22R G5 remain open.", "",
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
            raise ArithmeticError("V22R spectator-mass JSON drifted")
        if OUT_MD.read_text(encoding="utf-8") != markdown(report):
            raise ArithmeticError("V22R spectator-mass Markdown drifted")
    print(report["status"])
    print(report["core_sha256"])
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
