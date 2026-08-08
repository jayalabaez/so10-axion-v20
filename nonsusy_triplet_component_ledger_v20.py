#!/usr/bin/env python3
"""Signed machine-readable color-triplet component and M_T^2 provenance ledger."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import nonsusy_z17_pq_potential_filter_v20 as signed_filter

ROOT = Path(__file__).resolve().parent

FORBIDDEN = {
    "210_H 10_H^dag 10_H",
    "10_H 126bar_H S",
    "bare_10_H^2",
    "bare_126bar_H^2",
    "126bar_H^2 S",
}


def component_ledger() -> list[dict[str, Any]]:
    return [
        {
            "id": "T10",
            "parent_so10": "10_H",
            "sm": "(3,1,-1/3)",
            "conjugate_id": "T10bar",
            "mediates_scalar_d6_proton_decay": True,
            "kinetic_normalization_derived": False,
            "yukawa_tensor": "Y_10",
            "status": "STANDARD_QUANTUM_NUMBERS__NORMALIZATION_OPEN",
        },
        {
            "id": "T10bar",
            "parent_so10": "10_H",
            "sm": "(3bar,1,+1/3)",
            "conjugate_id": "T10",
            "mediates_scalar_d6_proton_decay": True,
            "kinetic_normalization_derived": False,
            "yukawa_tensor": "Y_10",
            "status": "STANDARD_QUANTUM_NUMBERS__NORMALIZATION_OPEN",
        },
        {
            "id": "T126_primary",
            "parent_so10": "126bar_H",
            "sm": "(3,1,-1/3)",
            "ps": "(6,1,1)",
            "aulakh_label": "t2",
            "conjugate_id": "T126bar_primary",
            "mediates_scalar_d6_proton_decay": True,
            "kinetic_normalization_derived": False,
            "yukawa_tensor": "Y_126",
            "status": "PUBLISHED_PS_BRANCHING_LOCKED__NORM_AND_CG_OPEN",
        },
        {
            "id": "T126bar_primary",
            "parent_so10": "126bar_H",
            "sm": "(3bar,1,+1/3)",
            "ps": "conjugate of (6,1,1)",
            "aulakh_label": "t2bar",
            "conjugate_id": "T126_primary",
            "mediates_scalar_d6_proton_decay": True,
            "kinetic_normalization_derived": False,
            "yukawa_tensor": "Y_126",
            "status": "PUBLISHED_PS_BRANCHING_LOCKED__NORM_AND_CG_OPEN",
        },
        {
            "id": "Tprime_126",
            "parent_so10": "126bar_H",
            "sm": "(3,1,-1/3)",
            "ps": "(10,1,3)",
            "aulakh_label": "t4",
            "conjugate_id": "Tprime_126bar",
            "mediates_scalar_d6_proton_decay": True,
            "kinetic_normalization_derived": False,
            "yukawa_tensor": "Y_126",
            "status": "PUBLISHED_PS_BRANCHING_LOCKED__NORM_AND_CG_OPEN",
            "note": (
                "Aulakh t4 from 126bar (10,1,3); promoted from the former "
                "T126_additional_OPEN slot. Kinetic norm and nonsusy CG remain OPEN."
            ),
        },
        {
            "id": "Tprime_126bar",
            "parent_so10": "126bar_H",
            "sm": "(3bar,1,+1/3)",
            "ps": "conjugate of (10,1,3)",
            "aulakh_label": "t4bar",
            "conjugate_id": "Tprime_126",
            "mediates_scalar_d6_proton_decay": True,
            "kinetic_normalization_derived": False,
            "yukawa_tensor": "Y_126",
            "status": "PUBLISHED_PS_BRANCHING_LOCKED__NORM_AND_CG_OPEN",
        },
        {
            "id": "T210_t5_heavy",
            "parent_so10": "210_H",
            "sm": None,
            "ps": "(15,1,3)",
            "aulakh_label": "t5",
            "conjugate_id": None,
            "mediates_scalar_d6_proton_decay": False,
            "kinetic_normalization_derived": False,
            "yukawa_tensor": None,
            "status": "PUBLISHED_HEAVY_AT_MGUT__NOT_IN_LIGHT_WORKING_BASIS",
            "note": "Integrated out at M_GUT; not a light d=6 scalar mediator.",
        },
        {
            "id": "T210_mixing_fragments_OPEN",
            "parent_so10": "210_H",
            "sm": None,
            "conjugate_id": None,
            "mediates_scalar_d6_proton_decay": None,
            "kinetic_normalization_derived": False,
            "yukawa_tensor": None,
            "status": "ANY_LIGHT_MIXING_FRAGMENT_BEYOND_HEAVY_T5_REMAINS_OPEN",
        },
    ]


def build_report() -> dict[str, Any]:
    ops = signed_filter.operator_catalogue(require_x=True)
    by_name = {row["name"]: row for row in ops}
    allowed_mt = {
        name: row
        for name, row in by_name.items()
        if row.get("feeds_triplet_mass")
        and row["status"] in {"ALLOWED", "CHARGE_OK_SO10_OPEN"}
    }
    forbidden_present = {
        name: by_name[name]["status"] for name in FORBIDDEN if name in by_name
    }

    matrix_entries = {
        "M11_T10_T10bar_GeV2": {
            "operators": [
                "10_H^dag 10_H",
                "10_H^2 S",
                "(10_H^dag 10_H)^2",
                "210_H^dag 210_H 10_H^dag 10_H",
                "|S|^2 |10_H|^2",
                "|Phi17|^2 |10_H|^2",
            ],
            "component_cg_coefficients_derived": False,
        },
        "M22_T126_T126bar_GeV2": {
            "operators": [
                "126bar_H^dag 126bar_H",
                "210_H 126bar_H^dag 126bar_H",
                "(126bar_H^dag 126bar_H)^2",
                "210_H^dag 210_H 126bar_H^dag 126bar_H",
                "|S|^2 |126bar_H|^2",
                "|Phi17|^2 |126bar_H|^2",
            ],
            "component_cg_coefficients_derived": False,
        },
        "M12_T10_T126bar_GeV2": {
            "operators": ["210 · 10 · 126 · S"],
            "component_cg_coefficients_derived": False,
        },
    }
    listed_ops = {
        name for entry in matrix_entries.values() for name in entry["operators"]
    }
    invalid_listed = sorted(
        name
        for name in listed_ops
        if name not in by_name
        or by_name[name]["status"] not in {"ALLOWED", "CHARGE_OK_SO10_OPEN"}
    )
    components = component_ledger()
    checks = {
        "component_ids_unique": len({row["id"] for row in components}) == len(components),
        "forbidden_210_10dag10_rejected": forbidden_present.get("210_H 10_H^dag 10_H") == "SO10_FORBIDDEN",
        "forbidden_10_126_S_rejected": forbidden_present.get("10_H 126bar_H S") == "SO10_FORBIDDEN",
        "bare_10_mass_rejected_by_charge": forbidden_present.get("bare_10_H^2") == "CHARGE_FORBIDDEN",
        "lambda4_offdiag_allowed": "210 · 10 · 126 · S" in allowed_mt,
        "matrix_entries_have_mass_squared_units": all(name.endswith("_GeV2") for name in matrix_entries),
        "matrix_uses_only_signed_allowed_operators": not invalid_listed,
        "no_forbidden_operator_in_matrix": not bool(listed_ops.intersection(FORBIDDEN)),
        "physical_completion_not_claimed": all(
            not entry["component_cg_coefficients_derived"] for entry in matrix_entries.values()
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "SIGNED_TRIPLET_COMPONENT_LEDGER_BUILT__PS_BRANCHING_PARTIAL__CG_OPEN"
            if not failures
            else "SIGNED_TRIPLET_COMPONENT_LEDGER_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "components": components,
        "matrix_basis_minimal": ["T10", "T126_primary"],
        "matrix_basis_published_light": [
            "T10",
            "T10bar",
            "T126_primary",
            "Tprime_126",
        ],
        "matrix_entries": matrix_entries,
        "signed_allowed_triplet_operators": sorted(allowed_mt),
        "forbidden_operator_status": forbidden_present,
        "invalid_listed_operators": invalid_listed,
        "flag": {
            "machine_readable_component_ledger": True,
            "signed_operator_filter_applied": True,
            "mass_squared_provenance_recorded": True,
            "published_ps_126bar_t2_t4_locked": True,
            "full_component_basis_complete": False,
            "full_126_multiplicity_complete": False,
            "kinetic_normalization_derived": False,
            "mixing_relevant_210_fragments_complete": False,
            "physical_component_CG_complete": False,
            "physical_triplet_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
        },
        "next_exact_calculation": [
            "derive kinetic normalization tensors for T10/T126/Tprime working states",
            "derive each listed diagonal component Clebsch coefficient (nonsusy)",
            "derive the lambda4 off-diagonal component Clebsch coefficient",
            "expand the minimal 2x2 ledger matrix to the published 4-state light basis",
            "decide whether any light 210 mixing fragment beyond heavy t5 is required",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("NONSUSY_TRIPLET_COMPONENT_LEDGER_V20.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
