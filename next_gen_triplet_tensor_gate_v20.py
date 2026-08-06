#!/usr/bin/env python3
"""Authoritative exact triplet-tensor subgate for SO(10) axion v20.

Combines the two independent non-SUSY five-form calculations:

1. exact 126bar branching, kinetic normalization, and lambda4 portal CGs;
2. exact 210·126bar†·126bar cubic diagonal/intra-126 CGs.

It also consumes the repository contamination audit and fail-closes all legacy
holomorphic/dimension-one triplet matrices as physical non-SUSY M^2 inputs.
The output is a G1/G6 subgate, not a complete model gate.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import exact_126bar_triplet_clebsch_v20 as portal
import exact_210_126bar_cubic_clebsch_v20 as cubic
import triplet_proxy_contamination_audit_v20 as contamination

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "NEXT_GEN_TRIPLET_TENSOR_GATE_V20.json"
OUT_MD = ROOT / "NEXT_GEN_TRIPLET_TENSOR_GATE_V20.md"


def build_report() -> dict[str, Any]:
    portal_report = portal.build_report()
    cubic_report = cubic.build_report()
    contamination_report = contamination.build_report()

    execution_failures: list[str] = []
    for name, report in (
        ("portal", portal_report),
        ("cubic", cubic_report),
        ("contamination", contamination_report),
    ):
        if report.get("n_failed", 1) != 0:
            execution_failures.append(f"{name}: {report.get('failures')}")

    portal_flags = portal_report.get("flag", {})
    cubic_flags = cubic_report.get("flag", {})
    contamination_flags = contamination_report.get("flag", {})

    exact_closed = {
        "126bar_t2_t2bar_t4bar_weight_branching": bool(
            portal_flags.get("exact_126bar_weight_branching_derived")
        ),
        "canonical_triplet_kinetic_normalization": bool(
            portal_flags.get("canonical_triplet_kinetic_normalization_derived")
        ),
        "lambda4_Phi_H_Sigmabar_S_triplet_clebsches": bool(
            portal_flags.get("lambda4_triplet_portal_clebsches_derived")
        ),
        "210_126bar_dag_126bar_cubic_contraction": bool(
            cubic_flags.get("exact_210_126bar_cubic_contraction_derived")
        ),
        "t4bar_diagonal_cubic_clebsch": bool(
            cubic_flags.get("t4bar_diagonal_clebsch_derived")
        ),
        "t2bar_t4bar_intra126_clebsch": bool(
            cubic_flags.get("t2bar_t4bar_mixing_clebsch_derived")
        ),
        "legacy_proxy_dependency_graph_invalidated": bool(
            contamination_flags.get("legacy_physical_triplet_chain_invalidated")
        ),
    }

    remaining = {
        "complete_mixed_invariant_ring": True,
        "all_universal_norm_and_independent_tensor_component_clebsches": True,
        "complete_10_H_charge_sector_diagonal_blocks": True,
        "complete_126bar_charge_sector_diagonal_blocks": True,
        "all_mixing_relevant_210_component_states": True,
        "nambu_doubled_real_scalar_hessian": True,
        "stationary_gauge_quotiented_positive_vacuum": True,
        "physical_threshold_spectrum": True,
        "two_loop_component_matching": True,
        "unique_proton_lifetime": True,
    }

    checks = {
        "upstreams_execute": not execution_failures,
        "all_exact_subproblems_closed": all(exact_closed.values()),
        "legacy_symmetric_4x4_rejected": not portal_flags.get(
            "legacy_symmetric_4x4_charge_sector_valid", True
        ),
        "cubic_coefficient_has_mass_dimension_one": cubic_report.get(
            "operator", {}
        ).get("coefficient_mass_dimension")
        == 1,
        "no_susy_matrix_used_as_nonsusy_M2": not cubic_flags.get(
            "uses_susy_mass_matrix_as_nonsusy_scalar_m2", True
        ),
        "full_component_CG_remains_open": not cubic_flags.get(
            "full_component_CG_complete", True
        ),
        "physical_spectrum_remains_open": not cubic_flags.get(
            "physical_triplet_spectrum_complete", True
        ),
        "unique_lifetime_remains_open": not cubic_flags.get(
            "exact_unique_proton_lifetime", True
        ),
        "whole_model_not_validated": not cubic_flags.get(
            "whole_model_validated", True
        ),
        "whole_model_not_excluded": not cubic_flags.get(
            "whole_model_excluded", True
        ),
    }
    failures = execution_failures + [name for name, ok in checks.items() if not ok]

    portal_coefficients = portal_report.get("portal_clebsches", {})
    cubic_matrices = cubic_report.get("sector_matrices_cartesian", {}).get(
        "antitriplet_sector", {}
    )

    return {
        "status": (
            "NEXT_GEN_EXACT_TRIPLET_TENSOR_SUBGATE_PASS__FULL_SPECTRUM_BLOCKED"
            if not failures
            else "NEXT_GEN_TRIPLET_TENSOR_SUBGATE_FAILED"
        ),
        "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "exact_subproblems_closed": exact_closed,
        "portal_coefficients_cartesian": {
            "Hbar10_from_t2": portal_coefficients.get(
                "Hbar10_from_t2_triplet", {}
            ).get("coefficients_cartesian"),
            "H10_from_t2bar": portal_coefficients.get(
                "H10_from_t2bar_antitriplet", {}
            ).get("coefficients_cartesian"),
            "H10_from_t4bar": portal_coefficients.get(
                "H10_from_t4bar_antitriplet", {}
            ).get("coefficients_cartesian"),
        },
        "cubic_210_126bar_matrices_cartesian": {
            name: row.get("matrix") for name, row in cubic_matrices.items()
        },
        "published_coordinate_translation": {
            "portal": portal_report.get("aulakh_coordinate_translation"),
            "cubic": cubic_report.get("aulakh_coordinate_translation"),
        },
        "accepted_quadratic_structure": {
            "independent_complex_field_components_by_hypercharge": portal_report.get(
                "corrected_nonsusy_charge_sectors"
            ),
            "physical_real_hessian_requirement": (
                "Build a Nambu-doubled real scalar Hessian, or equivalent "
                "Hermitian charge blocks plus allowed holomorphic B-terms. "
                "Do not diagonalize the historical symmetric dimension-one 4x4 "
                "as a non-SUSY physical scalar M2."
            ),
            "legacy_symmetric_4x4_authoritative": False,
        },
        "remaining_blockers": remaining,
        "upstream_status": {
            "portal": portal_report.get("status"),
            "cubic": cubic_report.get("status"),
            "contamination": contamination_report.get("status"),
        },
        "flag": {
            "authoritative_next_gen_triplet_subgate": True,
            "direct_portal_triplet_clebsches_complete_for_derived_states": not failures,
            "cubic_210_126bar_triplet_clebsches_complete_for_derived_channel": not failures,
            "legacy_triplet_proxy_authoritative": False,
            "complete_G1_invariant_ring": False,
            "complete_G2_component_potential": False,
            "physical_triplet_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "The exact five-form route closes the 126bar triplet branching, "
            "kinetic normalization, lambda4 portal CGs, and the nontrivial "
            "210·126bar†·126bar t4bar diagonal/intra-126 CG family. The old "
            "symmetric dimension-one 4x4 remains non-authoritative. A physical "
            "spectrum still requires the complete projected non-SUSY potential "
            "and Nambu-doubled Hessian at the unique vacuum."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Next-generation exact triplet tensor subgate — v20",
            "",
            f"**Status:** `{report['status']}`",
            f"**State:** `{report['overall_state']}`",
            "",
            report["verdict"],
            "",
            "## Exact subproblems closed",
            "",
            *[
                f"- `{name}`: {value}"
                for name, value in report["exact_subproblems_closed"].items()
            ],
            "",
            "## Remaining blockers",
            "",
            *[
                f"- `{name}`"
                for name, value in report["remaining_blockers"].items()
                if value
            ],
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
