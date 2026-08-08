#!/usr/bin/env python3
"""Authoritative scalar contract for the manuscript's gauged U(1)_X theory.

The manuscript does not define the stand-alone SO(10) x PQ x Z17 model used
by the historical ``require_x=False`` scalar census.  It explicitly gauges a
primitive U(1)_X, assigns X(Phi17)=17, and obtains Z17 after spontaneous
breaking.  Consequently every polynomial in the unbroken Lagrangian must be
exactly X neutral.

This module recovers the gauged subset from the existing tensor compiler
without renumbering its directions.  The no-X compiler is retained as a useful
superset, but its 20 X-charged directions and 40 real coefficients are not
parameters of the manuscript's theory.
"""
from __future__ import annotations

import argparse
import inspect
import json
import re
from pathlib import Path
from typing import Any

import g1_exact_declared_symmetry_character_census_v20 as census
import exact_x_symmetry_consistency_gate_v20 as exact_x_gate
import live_g1_tensor_closure_ledger_v20 as g1
import live_g2_derivative_coverage_ledger_v20 as g2
import nonsusy_z17_pq_potential_filter_v20 as operator_filter

ROOT = Path(__file__).resolve().parent
MANUSCRIPT = ROOT / "axion_so10_theory_v20.tex"
MODEL_SCAFFOLD = ROOT / "models" / "SO10Z17AxionV20.m"
OUT_JSON = ROOT / "GAUGED_U1X_SCALAR_CONTRACT_V20.json"
OUT_MD = ROOT / "GAUGED_U1X_SCALAR_CONTRACT_V20.md"


def _direction_id(orbit_index: int, basis_index: int, family: str) -> str:
    return f"O{orbit_index + 1:02d}_B{basis_index + 1:02d}_{family}"


def _parameter_ids(direction_id: str, self_conjugate: bool) -> tuple[str, ...]:
    if self_conjugate:
        return (f"lambda::{direction_id}",)
    return (f"re::{direction_id}", f"im::{direction_id}")


def _contract_rows(*, require_x: bool) -> list[dict[str, Any]]:
    all_orbits = census.orbits(census.census(False))
    selected = census.orbits(census.census(require_x))
    full_indices = {
        tuple(int(value) for value in row["orbit_key"]): index
        for index, row in enumerate(all_orbits)
    }
    rows: list[dict[str, Any]] = []
    for orbit in selected:
        key = tuple(int(value) for value in orbit["orbit_key"])
        counts = dict(zip(census.FIELD_ORDER, key, strict=True))
        base_key = key[:5]
        base = g1.BASE_FAMILIES[base_key]
        orbit_index = full_indices[key]
        charge = census.charge(key)
        for basis_index, basis_label in enumerate(base["basis"]):
            direction_id = _direction_id(orbit_index, basis_index, base["id"])
            rows.append(
                {
                    "direction_id": direction_id,
                    "orbit_index_in_64_direction_superset": orbit_index,
                    "representative": orbit["representative"],
                    "self_conjugate": bool(orbit["self_conjugate"]),
                    "base_family": base["id"],
                    "base_key": list(base_key),
                    "basis_index": basis_index,
                    "basis_label": str(basis_label),
                    "normalization": base["normalization"],
                    "source_modules": list(base["sources"]),
                    "charge": charge,
                    "parameter_ids": list(
                        _parameter_ids(direction_id, bool(orbit["self_conjugate"]))
                    ),
                }
            )
    return rows


def _orbit_multiplicity_audit(
    orbits: list[dict[str, Any]], *, contract: str
) -> list[dict[str, Any]]:
    """Bind every D5 character multiplicity to its compiler basis."""
    rows: list[dict[str, Any]] = []
    for orbit in orbits:
        key = tuple(int(value) for value in orbit["orbit_key"])
        base_key = key[:5]
        base = g1.BASE_FAMILIES.get(base_key)
        d5_multiplicity = int(orbit["so10_singlet_multiplicity"])
        base_multiplicity = None if base is None else int(base["multiplicity"])
        basis_length = None if base is None else len(base["basis"])
        rows.append(
            {
                "contract": contract,
                "representative": orbit["representative"],
                "orbit_key": list(key),
                "base_key": list(base_key),
                "base_family": None if base is None else base["id"],
                "D5_singlet_multiplicity": d5_multiplicity,
                "base_declared_multiplicity": base_multiplicity,
                "basis_length": basis_length,
                "multiplicities_equal": (
                    base is not None
                    and d5_multiplicity == base_multiplicity == basis_length
                ),
            }
        )
    return rows


def manuscript_contract() -> dict[str, Any]:
    text = MANUSCRIPT.read_text(encoding="utf-8", errors="replace")
    scaffold = MODEL_SCAFFOLD.read_text(encoding="utf-8", errors="replace")
    parsed_manuscript = exact_x_gate.manuscript_contract(text)
    parsed_scaffold = exact_x_gate.declared_symmetries(scaffold)
    return {
        "manuscript_gauges_u1x": parsed_manuscript["gauges_primitive_U1X"],
        "manuscript_phi17_charge_is_17": parsed_manuscript["phi17_X"] == 17,
        "manuscript_claims_anomaly_free_continuous_origin": bool(
            re.search(r"anomaly-free\s+(?:field-theory\s+)?origin", text)
        ),
        "manuscript_X_charge_tuple_parsed": parsed_manuscript[
            "charge_tuple_parsed"
        ],
        "manuscript_X_charge_tuple_labels": parsed_manuscript[
            "x_charge_tuple_labels"
        ],
        "manuscript_X_charge_tuple_values": parsed_manuscript[
            "x_charge_tuple_values"
        ],
        "manuscript_scalar_charges_PQ_X": parsed_manuscript[
            "scalar_final_charge_contract"
        ],
        "manuscript_scalar_charge_contract_matches_expected": parsed_manuscript[
            "scalar_charge_contract_matches_expected"
        ],
        "scaffold_declares_u1x": parsed_scaffold["u1x_gauged"],
        "scaffold_self_identifies_as_scaffold": parsed_scaffold[
            "explicitly_incomplete_scaffold"
        ],
        "scaffold_model_syntax_class": parsed_scaffold["model_syntax_class"],
        "scaffold_tool_native_sarah_syntax": parsed_scaffold[
            "tool_native_sarah_syntax"
        ],
        "scaffold_legacy_pseudo_sarah_grammar": parsed_scaffold[
            "legacy_pseudo_sarah_grammar"
        ],
        "scaffold_gauge_rows": parsed_scaffold["structured_gauge_rows"],
        "scaffold_scalar_charges_PQ_X": parsed_scaffold[
            "observed_scalar_charges_PQ_X"
        ],
        "scaffold_scalar_charges_match_manuscript": parsed_scaffold[
            "scalar_charges_match_manuscript"
        ],
        "scaffold_fermion_catalogue_exact": parsed_scaffold[
            "fermion_catalogue_exact"
        ],
        "scaffold_real_LagHC_present": parsed_scaffold["lagrangian"][
            "real_LagHC_present"
        ],
        "scaffold_real_LagNoHC_present": parsed_scaffold["lagrangian"][
            "real_LagNoHC_present"
        ],
        "scaffold_soft_gaugino_absent": parsed_scaffold[
            "soft_gaugino_absent_in_nonsusy_model"
        ],
        "scaffold_placeholder_free": not parsed_scaffold["placeholder_evidence"],
        "scaffold_lagrangian_registered_in_GaugeES_LagrangianInput": (
            parsed_scaffold["lagrangian"][
                "registered_in_GaugeES_LagrangianInput"
            ]
        ),
        "scaffold_statically_executable_contract": parsed_scaffold[
            "statically_executable_model_contract"
        ],
        "scaffold_semantic_requirements": parsed_scaffold[
            "semantic_requirements"
        ],
        "contract_source": "axion_so10_theory_v20.tex",
        "scaffold_role": (
            "statically consistent tool-native SARAH input; external SARAH "
            "execution is a separate fail-closed requirement"
        ),
    }


def build_report() -> dict[str, Any]:
    manuscript = manuscript_contract()
    gauged_rows = _contract_rows(require_x=True)
    no_x_rows = _contract_rows(require_x=False)
    gauged_ids = {row["direction_id"] for row in gauged_rows}
    excluded = [row for row in no_x_rows if row["direction_id"] not in gauged_ids]

    gauged_orbits = census.orbits(census.census(True))
    no_x_orbits = census.orbits(census.census(False))
    gauged_orbit_multiplicities = _orbit_multiplicity_audit(
        gauged_orbits, contract="gauged_u1x_phi17_v20"
    )
    no_x_orbit_multiplicities = _orbit_multiplicity_audit(
        no_x_orbits, contract="historical_option_c_no_x_v20"
    )
    gauged_counts = census.counts(census.census(True))
    no_x_counts = census.counts(census.census(False))
    parameter_ids = [item for row in gauged_rows for item in row["parameter_ids"]]
    excluded_parameters = [item for row in excluded for item in row["parameter_ids"]]
    base_families = {row["base_family"] for row in gauged_rows}
    missing_sources = sorted(
        {
            source
            for row in gauged_rows
            for source in row["source_modules"]
            if not ROOT.joinpath(source).exists()
        }
    )
    owners = g2.family_owners()
    filter_default = inspect.signature(operator_filter._allowed).parameters[
        "require_x"
    ].default
    implementation_mismatches = [
        name
        for name, satisfied in manuscript["scaffold_semantic_requirements"].items()
        if not satisfied
    ]

    checks = {
        "manuscript_is_explicitly_gauged_u1x": manuscript["manuscript_gauges_u1x"],
        "manuscript_phi17_has_x17": manuscript["manuscript_phi17_charge_is_17"],
        "manuscript_full_X_charge_tuple_is_parsed": manuscript[
            "manuscript_X_charge_tuple_parsed"
        ],
        "manuscript_scalar_charge_tuple_matches_contract": manuscript[
            "manuscript_scalar_charge_contract_matches_expected"
        ],
        "manuscript_continuous_origin_is_anomaly_free": manuscript[
            "manuscript_claims_anomaly_free_continuous_origin"
        ],
        "scaffold_role_is_classified": isinstance(
            manuscript["scaffold_self_identifies_as_scaffold"], bool
        ),
        "scaffold_syntax_class_is_explicit": manuscript[
            "scaffold_model_syntax_class"
        ]
        in {
            "sarah_native",
            "legacy_pseudo_sarah_metadata",
            "mixed_or_unrecognized",
        },
        "legacy_pseudo_sarah_is_not_tool_native": bool(
            not manuscript["scaffold_legacy_pseudo_sarah_grammar"]
            or not manuscript["scaffold_tool_native_sarah_syntax"]
        ),
        "operator_filter_requires_explicit_x_contract": (
            filter_default is inspect.Parameter.empty
        ),
        "gauged_multidegree_count_is_34": gauged_counts[
            "charge_and_so10_allowed_multidegrees"
        ]
        == 34,
        "gauged_conjugacy_orbit_count_is_28": len(gauged_orbits) == 28,
        "every_gauged_orbit_D5_base_and_basis_multiplicity_agree": all(
            row["multiplicities_equal"] for row in gauged_orbit_multiplicities
        ),
        "every_historical_orbit_D5_base_and_basis_multiplicity_agree": all(
            row["multiplicities_equal"] for row in no_x_orbit_multiplicities
        ),
        "gauged_direction_count_is_44": len(gauged_rows) == 44,
        "gauged_real_parameter_count_is_51": len(parameter_ids) == 51,
        "all_18_tensor_families_survive": len(base_families) == 18,
        "every_gauged_direction_is_exactly_x_neutral": all(
            row["charge"]["X"] == 0 for row in gauged_rows
        ),
        "exactly_20_x_charged_directions_excluded": len(excluded) == 20
        and all(row["charge"]["X"] != 0 for row in excluded),
        "exactly_40_real_parameters_excluded": len(excluded_parameters) == 40,
        "gauged_schema_is_subset_of_64_91_compiler": (
            set(parameter_ids).isdisjoint(excluded_parameters)
            and len(no_x_rows) == 64
            and no_x_counts["total_real_potential_parameters"] == 91
        ),
        "every_tensor_family_has_one_g2_adapter": set(owners) == base_families
        and all(len(owners[family]) == 1 for family in base_families),
        "all_tensor_sources_present": not missing_sources,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "model_contract_id": "gauged_u1x_phi17_v20",
        "historical_counterfactual_contract_id": "historical_option_c_no_x_v20",
        "status": (
            "GAUGED_U1X_SCALAR_CONTRACT_IDENTIFIED__IMPLEMENTATION_BLOCKED"
            if not failures and implementation_mismatches
            else "GAUGED_U1X_SCALAR_CONTRACT_IDENTIFIED__G2_G3_REAUDIT_OPEN"
            if not failures
            else "GAUGED_U1X_SCALAR_CONTRACT_INTEGRITY_FAILED"
        ),
        "overall_state": (
            "EXECUTION_FAIL"
            if failures
            else "BLOCKED"
            if implementation_mismatches
            else "PARTIAL"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "implementation_matches_manuscript": not implementation_mismatches,
        "implementation_mismatches": implementation_mismatches,
        "checks": checks,
        "authoritative_contract": {
            "gauge": ["SO(10)", "U(1)_X"],
            "accidental_global": ["U(1)_PQ"],
            "residual_after_phi17": "Z17",
            "require_exact_x_neutrality": True,
            "phi17_X_charge": 17,
        },
        "manuscript_and_scaffold": manuscript,
        "counts": {
            "multidegrees": gauged_counts[
                "charge_and_so10_allowed_multidegrees"
            ],
            "hermitian_conjugacy_orbits": len(gauged_orbits),
            "invariant_directions": len(gauged_rows),
            "real_parameters": len(parameter_ids),
            "base_tensor_families": len(base_families),
            "real_field_dimension_before_gauge_quotient": 486,
            "so10_broken_directions_at_physical_ew": 36,
            "u1x_eaten_direction": 1,
            "physical_pq_axion_direction": 1,
            "expected_massive_physical_quotient_dimension": 448,
        },
        "gauged_directions": gauged_rows,
        "gauged_orbit_multiplicity_audit": gauged_orbit_multiplicities,
        "historical_option_c_orbit_multiplicity_audit": no_x_orbit_multiplicities,
        "gauged_parameter_ids": parameter_ids,
        "excluded_option_c_directions": excluded,
        "excluded_option_c_parameter_ids": excluded_parameters,
        "missing_source_modules": missing_sources,
        "flags": {
            "current_model_is_legacy_pseudo_sarah": manuscript[
                "scaffold_legacy_pseudo_sarah_grammar"
            ],
            "current_model_is_tool_native_sarah": manuscript[
                "scaffold_tool_native_sarah_syntax"
            ],
            "option_c_no_continuous_x_rejected": not failures,
            "G1_gauged_u1x_subcensus_closed": not failures,
            "G2_gauged_u1x_derivative_subset_identified": not failures,
            "G2_gauged_u1x_derivatives_certified": False,
            "G2_dense_subset_reaudit_required_in_G3": True,
            "joint_so10_u1x_rank_37_certified": False,
            "massive_quotient_dimension_448_certified": False,
            "legacy_64_91_compiler_is_authoritative_theory": False,
            "current_fixed_vacuum_validated": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The manuscript's scalar theory is the exact-X-neutral 44-direction, "
            "51-real-parameter subset of the existing tensor compiler. The 20 "
            "additional no-X directions are gauge forbidden and cannot be used "
            "to establish stationarity or stability. G3 must include the eaten "
            "U(1)_X phase and a separate physical PQ axion."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    counts = report["counts"]
    OUT_MD.write_text(
        "# Gauged U(1)_X scalar contract - v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        + report["verdict"]
        + "\n\n"
        f"- conjugacy orbits: `{counts['hermitian_conjugacy_orbits']}`\n"
        f"- invariant directions: `{counts['invariant_directions']}`\n"
        f"- real parameters: `{counts['real_parameters']}`\n"
        "- gauged orbit D5/base/basis multiplicities agree: "
        f"`{report['checks']['every_gauged_orbit_D5_base_and_basis_multiplicity_agree']}`\n"
        "- scaffold implementation matches manuscript: "
        f"`{report['implementation_matches_manuscript']}`\n"
        f"- expected massive physical quotient: `{counts['expected_massive_physical_quotient_dimension']}`\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
