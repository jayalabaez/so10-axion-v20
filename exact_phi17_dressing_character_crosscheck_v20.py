#!/usr/bin/env python3
"""Cross-check historical no-X Phi17 dressings against the exact D5 census."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import exact_phi17_neutral_dressing_completion_v20 as closure
import g1_exact_declared_symmetry_character_census_v20 as census

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_PHI17_DRESSING_CHARACTER_CROSSCHECK_V20.json"
OUT_MD = ROOT / "EXACT_PHI17_DRESSING_CHARACTER_CROSSCHECK_V20.md"

FIELD_MAP = {
    "210_H": "P",
    "210_H_dag": "P",
    "10_H": "H",
    "10_H_dag": "Hb",
    "126bar_H": "D",
    "126bar_H_dag": "Db",
    "S": "S",
    "S_dag": "Sb",
    "Phi17": "X",
    "Phi17_dag": "Xb",
}


def census_counts(counts: dict[str, int]) -> dict[str, int]:
    output = {field: 0 for field in census.FIELDS}
    for name, multiplicity in counts.items():
        output[FIELD_MAP[name]] += int(multiplicity)
    return {name: value for name, value in output.items() if value}


def multiplicity_rows() -> dict[str, Any]:
    live = census.census(False)
    rows: dict[str, Any] = {}
    for addition in closure.ADDITIONS:
        mapped = census_counts(addition["counts"])
        multiplicity = census.find_multiplicity(live, **mapped)
        rows[addition["name"]] = {
            "closure_counts": addition["counts"],
            "census_counts": mapped,
            "degree": sum(mapped.values()),
            "exact_so10_singlet_multiplicity": multiplicity,
            "expected_multiplicity": addition["multiplicity"],
            "matches": multiplicity == addition["multiplicity"],
        }
    return rows


def build_report() -> dict[str, Any]:
    exact_census = census.build_report()
    option_c_counts = census.counts(census.census(False))
    closure_report = closure.build_report()
    rows = multiplicity_rows()
    checks = {
        "exact_live_census_executes": exact_census["n_failed"] == 0,
        "historical_option_c_census_has_74_multidegrees": (
            option_c_counts["charge_and_so10_allowed_multidegrees"] == 74
        ),
        "historical_option_c_census_has_64_coefficient_directions": (
            option_c_counts["total_potential_orbit_multiplicity"] == 64
        ),
        "dressing_closure_executes": closure_report["n_failed"] == 0,
        "seven_rows_crosschecked": len(rows) == 7,
        "all_seven_exact_multiplicity_one": all(
            row["exact_so10_singlet_multiplicity"] == 1
            for row in rows.values()
        ),
        "all_closure_multiplicities_match_character_census": all(
            row["matches"] for row in rows.values()
        ),
        "full_tensor_ring_not_claimed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "model_contract_id": "historical_option_c_no_x_v20",
        "authoritative_for_manuscript": False,
        "status": (
            "PHI17_DRESSINGS_EXACTLY_MATCH_LIVE_D5_CENSUS"
            if not failures
            else "PHI17_DRESSING_CHARACTER_CROSSCHECK_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "authoritative_gauged_census_summary": exact_census["counts"],
        "historical_option_c_census_summary": option_c_counts,
        "multiplicity_rows": rows,
        "flags": {
            "seven_dressings_character_verified": not failures,
            "all_seven_multiplicity_one": not failures,
            "explicit_tensor_provenance_attached": not failures,
            "complete_mixed_tensor_basis": False,
            "complete_component_potential": False,
            "whole_model_validated": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "Every one of the seven Phi17 dressing classes appears with "
            "singlet multiplicity one in the historical no-X D5 census. These "
            "directions carry nonzero U(1)_X charge and are not operators of "
            "the manuscript-authoritative gauged theory."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        OUT_MD.write_text(
            "# Phi17 dressing exact-character cross-check\n\n"
            f"**Status:** `{report['status']}`\n\n"
            + report["verdict"]
            + "\n",
            encoding="utf-8",
        )
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
