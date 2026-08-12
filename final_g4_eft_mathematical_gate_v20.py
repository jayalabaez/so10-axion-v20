#!/usr/bin/env python3
"""Fail-closed mathematical G4 adapter for the dimension-six EFT vacuum.

The authoritative G4 requirement is the physical Hessian classification at an
accepted G3 witness.  For the current-kernel EFT witness this means:

* exact SO(10), SO(10)xU(1)_X, and SO(10)xU(1)_XxU(1)_PQ tangent ranks
  36, 37, and 38;
* a 449-dimensional gauge quotient containing one independent PQ axion;
* a 448-dimensional massive/transverse quotient;
* for every positive ``kappa=(1/20)Lambda_EFT^-2``, an exact PSD Hessian of
  rank 448 and nullity 38 whose kernel is precisely the full
  symmetry-tangent image.

This adapter closes mathematical G4 only for the explicitly registered
dimension-six EFT model.  It does not alter the renormalizable G4 gate and it
does not claim EFT release verification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import exact_gauged_u1x_g3_su5_delta_hsx_exact_hessian_v20 as hessian_source
import exact_gauged_u1x_g3_su5_delta_hsx_extension_v20 as hsx_source
import exact_gauged_u1x_g3_su5_eft_current_kernel_stabilized_global_v20 as theorem
import exact_gauged_u1x_physical_quotient_v20 as quotient_source
import final_g3_eft_acceptance_gate_v20 as g3_gate


STATUS = "FINAL_EFT_G4_MATHEMATICAL_PASS_RELEASE_OPEN"
BASE_MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
EFT_MODEL_CONTRACT_ID = (
    "gauged_u1x_phi17_v20_eft_o6_current_kernel_gamma_1_over_20"
)
EXPECTED_CORE_SHA256 = "931a152aed49eb28bf415a1aca093e923850cf68db3f40ccf1d2027b447a8c09"
EXPECTED_THEOREM_CORE_SHA256 = (
    "2eca279488d92d8bd9eca974c0d598340124f025e62212cd8a188413a6e8b7d0"
)
EXPECTED_G3_GATE_CORE_SHA256 = (
    "472770981ee7f9ad5880d614826e687c6d9402c286980b421a2bad7d079f09fb"
)
EXPECTED_STABILIZED_HESSIAN_PAYLOAD_SHA256 = (
    "7ea54d59138f8e5b66aad3d1f1ecb707c65ac9bb0f0e118a597daaccc136b568"
)

THEOREM_SOURCE = (
    HERE / "exact_gauged_u1x_g3_su5_eft_current_kernel_stabilized_global_v20.py"
)
THEOREM_JSON = HERE / "EXACT_EFT_CURRENT_KERNEL_STABILIZED_GLOBAL_G3.json"
G3_GATE_SOURCE = HERE / "final_g3_eft_acceptance_gate_v20.py"
G3_GATE_JSON = HERE / "FINAL_G3_EFT_ACCEPTANCE_GATE_V20.json"
QUOTIENT_SOURCE = HERE / "exact_gauged_u1x_physical_quotient_v20.py"
QUOTIENT_JSON = HERE / "EXACT_GAUGED_U1X_PHYSICAL_QUOTIENT_V20.json"
HSX_SOURCE = HERE / "exact_gauged_u1x_g3_su5_delta_hsx_extension_v20.py"
HESSIAN_SOURCE = (
    HERE / "exact_gauged_u1x_g3_su5_delta_hsx_exact_hessian_v20.py"
)
OUT_JSON = HERE / "FINAL_G4_EFT_MATHEMATICAL_GATE_V20.json"
OUT_MD = HERE / "FINAL_G4_EFT_MATHEMATICAL_GATE_V20.md"

EXPECTED_ARTIFACT_SHA256 = {
    "EFT_G3_theorem_source": (
        THEOREM_SOURCE,
        "d3b3368e8e640b285f43a106f5c236dc2780c01df4d71e88365cb607f35277f9",
    ),
    "EFT_G3_theorem_JSON": (
        THEOREM_JSON,
        "38520c5aed7a3a72dbede3e4358e5edb48c16f35a5bb31601864e1f8dc0e2271",
    ),
    "EFT_G3_gate_source": (
        G3_GATE_SOURCE,
        "bd67e726fb2f482ef415307943bacdc5a54a0ebeae757852fe4c40010d6a0af5",
    ),
    "EFT_G3_gate_JSON": (
        G3_GATE_JSON,
        "482f9da84d677e24594ca536a2c257602e02f5187419df5cba5356f771ddbaf0",
    ),
    "physical_quotient_source": (
        QUOTIENT_SOURCE,
        "5e2a089f32049a82f4d05171df76df27b832b171c0a730dd6922d5e797326a9b",
    ),
    "physical_quotient_JSON": (
        QUOTIENT_JSON,
        "489e0cb60085d799fb59e5f2976b19d357c88be66013e65fb1d92c8ee49ad9bd",
    ),
    "EFT_witness_orbit_source": (
        HSX_SOURCE,
        "c88a76c4bcc1f32ddce9eef15c87fe0a6794f7e0d7643ae774972a9b4b67c71f",
    ),
    "EFT_witness_Hessian_source": (
        HESSIAN_SOURCE,
        "cd4192713d8b3b13f6a9cf492f37d8615e3ead7a1a49fb3c30a1f6de235f7498",
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def _artifact_guard() -> dict[str, str]:
    observed: dict[str, str] = {}
    for name, (path, expected) in EXPECTED_ARTIFACT_SHA256.items():
        digest = _sha256(path)
        if digest != expected:
            raise ArithmeticError(
                f"frozen EFT G4 dependency drifted: {name}: {digest} != {expected}"
            )
        observed[name] = digest
    if theorem.EXPECTED_CORE_SHA256 != EXPECTED_THEOREM_CORE_SHA256:
        raise ArithmeticError("the imported EFT theorem core pin drifted")
    if g3_gate.EXPECTED_CORE_SHA256 != EXPECTED_G3_GATE_CORE_SHA256:
        raise ArithmeticError("the imported EFT G3 gate core pin drifted")
    return observed


def _exact_rank(matrix: Any) -> int:
    rows = tuple(tuple(int(value) for value in row) for row in matrix)
    rank, _pivot_rows, _pivot_columns = quotient_source._row_echelon_metadata(rows)
    return int(rank)


def exact_eft_witness_quotient_geometry() -> dict[str, Any]:
    """Rank the exact tangent prefixes used by the EFT Hessian proof itself."""

    tangent, metadata = hessian_source.exact_symmetry_tangent_matrix()
    if tangent.shape != (486, 47):
        raise ArithmeticError(f"unexpected EFT tangent shape {tangent.shape}")
    ranks = {
        "SO10": _exact_rank(tangent[:, :45]),
        "SO10_plus_U1X": _exact_rank(tangent[:, :46]),
        "SO10_plus_U1X_plus_PQ": _exact_rank(tangent),
    }
    independent_orbit = hsx_source.exact_orbit_rank_certificate()
    expected_ranks = {
        "SO10": 36,
        "SO10_plus_U1X": 37,
        "SO10_plus_U1X_plus_PQ": 38,
    }
    if not (
        metadata["integer_lattice_residual"] == 0.0
        and metadata["source_binding"] is True
        and metadata["exact_rank"] == 38
        and ranks == expected_ranks
        and independent_orbit["source_binding_exact"] is True
        and independent_orbit["integer_lattice_residual"] == 0.0
        and independent_orbit["SO10_rank"] == ranks["SO10"]
        and independent_orbit["SO10_plus_U1X_rank"]
        == ranks["SO10_plus_U1X"]
        and independent_orbit["SO10_plus_U1X_plus_PQ_rank"]
        == ranks["SO10_plus_U1X_plus_PQ"]
        and independent_orbit["physical_quotient_dimension"] == 448
    ):
        raise ArithmeticError("the EFT witness quotient geometry failed")

    gauge_quotient = tangent.shape[0] - ranks["SO10_plus_U1X"]
    massive_quotient = tangent.shape[0] - ranks["SO10_plus_U1X_plus_PQ"]
    axion_nullity = ranks["SO10_plus_U1X_plus_PQ"] - ranks["SO10_plus_U1X"]
    return {
        "real_field_dimension": int(tangent.shape[0]),
        "generator_columns": int(tangent.shape[1]),
        "column_order": "45 SO(10), then U(1)_X, then global PQ",
        "exact_tangent_ranks": ranks,
        "exact_integer_lattice_residual": metadata["integer_lattice_residual"],
        "source_binding_exact": True,
        "gauge_quotient_dimension_including_axion": gauge_quotient,
        "independent_PQ_axion_dimension": axion_nullity,
        "massive_transverse_quotient_dimension": massive_quotient,
        "same_witness_crosscheck": {
            "method": independent_orbit["method"],
            "pivot_column_counts": independent_orbit["pivot_column_counts"],
            "full_symmetry_nullity": independent_orbit["full_symmetry_nullity"],
        },
    }


def _mathematical_checks(
    theorem_report: dict[str, Any],
    g3_report: dict[str, Any],
    quotient_reference: dict[str, Any],
    geometry: dict[str, Any],
) -> dict[str, bool]:
    flags = theorem_report["closure_flags"]
    scope = theorem_report["scope_boundary"]
    candidate = theorem_report["candidate_and_global_SOS"]
    hessian = theorem_report["exact_stabilized_Hessian"]
    base = hessian["beta_zero_base"]
    stabilized = hessian["stabilized"]
    kernel = hessian["kernel_intersection"]
    g3_classification = g3_report["classification"]
    ranks = geometry["exact_tangent_ranks"]
    return {
        "EFT_G3_theorem_core_exact": (
            theorem_report["core_sha256"] == EXPECTED_THEOREM_CORE_SHA256
        ),
        "accepted_EFT_G3_witness_exact": (
            g3_report["core_sha256"] == EXPECTED_G3_GATE_CORE_SHA256
            and g3_classification["mathematical_G3_closed_for_EFT_model"] is True
            and g3_classification["mathematical_G3_closed_for_original_renormalizable_model"]
            is False
        ),
        "EFT_contract_scope_exact": (
            g3_report["contract"]["EFT_model_contract_id"] == EFT_MODEL_CONTRACT_ID
            and candidate["model_contract_id"] == BASE_MODEL_CONTRACT_ID
            and scope["EFT_dimension_six_extension"] is True
            and scope["authoritative_renormalizable_51_parameter_model"] is False
            and candidate["EFT_operator"]["normalized_exact_point"]
            == "gamma=1/20, Lambda_EFT=1"
            and candidate["EFT_operator"]["Wilson_coefficient"]
            == "kappa=gamma/Lambda_EFT^2"
            and candidate["EFT_operator"]["nonnegative_for_all_fields"] is True
        ),
        "authoritative_quotient_convention_source_bound": (
            quotient_reference["status"] == "EXACT_PHYSICAL_QUOTIENT_CERTIFIED"
            and quotient_reference["certified"] is True
            and quotient_reference["model_contract_id"] == BASE_MODEL_CONTRACT_ID
            and quotient_reference["gauge_quotient_dimension_including_axion"]
            == 449
            and quotient_reference["massive_transverse_quotient_dimension"] == 448
        ),
        "EFT_witness_tangent_lattice_source_bound": (
            geometry["source_binding_exact"] is True
            and geometry["exact_integer_lattice_residual"] == 0.0
            and geometry["real_field_dimension"] == 486
        ),
        "SO10_orbit_rank_36_exact": ranks["SO10"] == 36,
        "gauged_orbit_rank_37_exact": ranks["SO10_plus_U1X"] == 37,
        "full_symmetry_orbit_rank_38_exact": (
            ranks["SO10_plus_U1X_plus_PQ"] == 38
        ),
        "gauge_quotient_449_includes_one_PQ_axion": (
            geometry["gauge_quotient_dimension_including_axion"] == 449
            and geometry["independent_PQ_axion_dimension"] == 1
        ),
        "massive_transverse_quotient_448_exact": (
            geometry["massive_transverse_quotient_dimension"] == 448
        ),
        "stabilized_Hessian_is_exact_PSD": (
            base["exact_PSD"] is True
            and stabilized["sum_of_PSD_matrices"] is True
            and stabilized["normalized_exact_point"] == "gamma=1/20, Lambda_EFT=1"
        ),
        "stabilized_Hessian_rank448_nullity38_exact": (
            flags["full_Hessian_PSD_rank_448_nullity_38"] is True
            and stabilized["exact_rank"] == 448
            and stabilized["exact_nullity"] == 38
            and stabilized["payload_sha256"]
            == EXPECTED_STABILIZED_HESSIAN_PAYLOAD_SHA256
        ),
        "Hessian_kernel_equals_full_symmetry_tangents": (
            kernel["exact_symmetry_tangent_rank"] == 38
            and kernel["exact_intersection_nullity"] == 38
            and kernel["base_tangent_residual"] == 0
            and kernel["Jacobian_tangent_residual"] == 0
            and set(kernel["ranks_mod_primes"].values()) == {448}
            and kernel["six_nonsymmetry_base_flats_lifted"] is True
        ),
        "all_positive_kappa_have_same_PSD_kernel_and_rank": (
            base["exact_PSD"] is True
            and stabilized["sum_of_PSD_matrices"] is True
            and kernel["exact_intersection_nullity"] == 38
            and set(kernel["ranks_mod_primes"].values()) == {448}
        ),
        "all_448_transverse_modes_strictly_positive": (
            flags["strict_local_minimum_on_physical_quotient"] is True
            and stabilized["strict_on_448_dimensional_physical_quotient"] is True
        ),
        "accepted_witness_is_exact_stationary_global_minimum": (
            flags["selected_target_exact_stationary"] is True
            and flags["selected_target_global_minimum"] is True
            and flags["global_equality_orbit_unique_mod_declared_symmetries"] is True
        ),
        "legacy_scopes_not_relabelled": (
            flags["G3_closed_for_original_renormalizable_model"] is False
            and flags["G4_closed"] is False
            and g3_classification["G4_closed"] is False
            and g3_classification["renormalizable_gate_mutated"] is False
        ),
    }


def build_report() -> dict[str, Any]:
    artifacts = _artifact_guard()
    theorem_report = json.loads(THEOREM_JSON.read_text(encoding="utf-8"))
    frozen_g3_report = json.loads(G3_GATE_JSON.read_text(encoding="utf-8"))
    live_g3_report = g3_gate.build_report()
    if live_g3_report != frozen_g3_report:
        raise ArithmeticError("the live and frozen EFT G3 gate reports differ")
    quotient_reference = json.loads(QUOTIENT_JSON.read_text(encoding="utf-8"))
    geometry = exact_eft_witness_quotient_geometry()
    checks = _mathematical_checks(
        theorem_report, live_g3_report, quotient_reference, geometry
    )
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise ArithmeticError(f"EFT mathematical G4 mapping failed: {failures}")

    release_criteria = {
        "mathematical_EFT_G3_gate_passed": True,
        "authoritative_EFT_contract_registered": True,
        "Lambda_EFT_and_positive_Wilson_matching_approved": False,
        "radiative_stability_completed": False,
        "external_extended_model_contract_executed": False,
        "G1_promoted_closed": False,
        "G2_promoted_closed": False,
        "release_G3_verified_for_EFT_model": False,
        "parallel_EFT_G4_integrated_into_release_orchestrators": True,
    }
    mathematical_g4_closed = all(checks.values())
    release_g4_verified = mathematical_g4_closed and all(release_criteria.values())
    report: dict[str, Any] = {
        "status": STATUS,
        "contract": {
            "base_model_contract_id": BASE_MODEL_CONTRACT_ID,
            "EFT_model_contract_id": EFT_MODEL_CONTRACT_ID,
            "extension": "(1/20)Lambda_EFT^-2||K_H Sigma||^2",
            "authoritative_51_parameter_contract_unchanged": True,
        },
        "artifact_sha256": artifacts,
        "theorem_core_sha256": theorem_report["core_sha256"],
        "upstream_G3_gate_core_sha256": live_g3_report["core_sha256"],
        "exact_EFT_witness_quotient_geometry": geometry,
        "exact_Hessian_classification": {
            "full_real_dimension": 486,
            "gauge_quotient_dimension_including_axion": 449,
            "massless_physical_axion_modes": 1,
            "massive_transverse_dimension": 448,
            "negative_modes": 0,
            "unexplained_zero_modes": 0,
            "strictly_positive_massive_transverse_modes": 448,
            "Hessian_rank": 448,
            "Hessian_nullity": 38,
            "kernel": "exactly SO(10)xU(1)_XxU(1)_PQ tangents",
            "positive_kappa_family": {
                "coefficient": "kappa=(1/20)Lambda_EFT^-2 > 0 for Lambda_EFT>0",
                "Hessian_form": "H(kappa)=H0+c(kappa) J^T J with c(kappa)>0",
                "kernel_identity": (
                    "ker H(kappa)=ker H0 intersect ker J for every kappa>0"
                ),
                "reason": (
                    "H0 and J^T J are PSD, so a positive weighted sum vanishes "
                    "exactly on the common kernel"
                ),
                "rank448_nullity38_for_every_positive_kappa": True,
                "normalized_exact_payload_point": (
                    "gamma=1/20, Lambda_EFT=1"
                ),
            },
            "stabilized_payload_sha256": EXPECTED_STABILIZED_HESSIAN_PAYLOAD_SHA256,
        },
        "mathematical_checks": checks,
        "release_criteria": release_criteria,
        "release_blockers": [
            name for name, passed in release_criteria.items() if not passed
        ],
        "classification": {
            "mathematical_G4_closed_for_EFT_model": mathematical_g4_closed,
            "mathematical_G4_closed_for_original_renormalizable_model": False,
            "release_G4_verified_for_EFT_model": release_g4_verified,
            "authoritative_renormalizable_G4_gate_mutated": False,
            "whole_model_validated": False,
        },
        "production_mapping": {
            "new_parallel_gate": "EFT_G4_MATHEMATICAL",
            "do_not_flip": "authoritative renormalizable G4",
            "release_integration_completed": True,
        },
        "verdict": (
            "Mathematical G4 is closed for the registered dimension-six EFT "
            "model for every positive kappa=(1/20)Lambda_EFT^-2: the "
            "449-dimensional gauge quotient contains exactly one independent "
            "PQ axion, and the remaining 448-dimensional physical Hessian is "
            "strictly positive. The original renormalizable G4 and EFT release "
            "G4 remain open."
        ),
    }
    report["core_sha256"] = _canonical_sha256(report)
    return report


def _markdown(report: dict[str, Any]) -> str:
    classification = report["classification"]
    hessian = report["exact_Hessian_classification"]
    return "\n".join(
        (
            "# Final EFT mathematical G4 gate - v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- Core SHA-256: `{report['core_sha256']}`",
            f"- EFT contract: `{EFT_MODEL_CONTRACT_ID}`",
            "- exact gauge quotient (axion included): "
            f"`{hessian['gauge_quotient_dimension_including_axion']}`",
            f"- independent PQ axion modes: `{hessian['massless_physical_axion_modes']}`",
            f"- exact massive/transverse quotient: `{hessian['massive_transverse_dimension']}`",
            f"- exact Hessian rank/nullity: `{hessian['Hessian_rank']}/{hessian['Hessian_nullity']}`",
            "- positive coefficient scope: every "
            "`kappa=(1/20)Lambda_EFT^-2 > 0`",
            f"- mathematical EFT G4: `{str(classification['mathematical_G4_closed_for_EFT_model']).lower()}`",
            f"- original renormalizable G4: `{str(classification['mathematical_G4_closed_for_original_renormalizable_model']).lower()}`",
            f"- EFT release G4: `{str(classification['release_G4_verified_for_EFT_model']).lower()}`",
            "",
        )
    )


def write_report(
    report: dict[str, Any], *, out_json: Path = OUT_JSON, out_md: Path = OUT_MD
) -> None:
    out_json.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    out_md.write_text(_markdown(report), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--allow-unfrozen", action="store_true")
    arguments = parser.parse_args()
    report = build_report()
    if not arguments.allow_unfrozen and report["core_sha256"] != EXPECTED_CORE_SHA256:
        raise ArithmeticError(
            f"adapter core drift: {report['core_sha256']} != {EXPECTED_CORE_SHA256}"
        )
    if arguments.write:
        write_report(report)
    if arguments.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(report["status"])
        print(
            "EFT mathematical G4",
            report["classification"]["mathematical_G4_closed_for_EFT_model"],
        )
        print(
            "renormalizable mathematical G4",
            report["classification"][
                "mathematical_G4_closed_for_original_renormalizable_model"
            ],
        )
        print(
            "EFT release G4",
            report["classification"]["release_G4_verified_for_EFT_model"],
        )
        print("core_sha256", report["core_sha256"])


if __name__ == "__main__":
    main()
