#!/usr/bin/env python3
"""Fail-closed mathematical G6 gate for the dimension-six EFT branch."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import exact_eft_physical_scalar_spectrum_v20 as spectrum
import final_g4_eft_mathematical_gate_v20 as g4_gate
import final_g5_eft_mathematical_gate_v20 as g5_gate


STATUS = "FINAL_EFT_G6_TREE_LEVEL_MATHEMATICAL_PASS_RELEASE_OPEN"
BASE_MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
EFT_MODEL_CONTRACT_ID = spectrum.MODEL_CONTRACT_ID
OUT_JSON = HERE / "FINAL_G6_EFT_MATHEMATICAL_GATE_V20.json"
OUT_MD = HERE / "FINAL_G6_EFT_MATHEMATICAL_GATE_V20.md"

EXPECTED_CORE_SHA256 = (
    "e34b791478bf9cb00f951819cbfec45a99d51be776889d8a4e13cf1717eee738"
)
EXPECTED_SPECTRUM_CORE_SHA256 = (
    "abb704133c8be22b424ba20e23387d6f30412e6c82ab3a214e88bd8df5bef9cc"
)
EXPECTED_G4_CORE_SHA256 = (
    "931a152aed49eb28bf415a1aca093e923850cf68db3f40ccf1d2027b447a8c09"
)
EXPECTED_G5_CORE_SHA256 = (
    "1b578471e74626e3b186cf7398aebd35349a67f45940b9c37d42bb49c1b8c8ba"
)
EXPECTED_ARTIFACT_SHA256 = {
    "spectrum_source": (
        HERE / "exact_eft_physical_scalar_spectrum_v20.py",
        "cdcc25b383098464fc6312d553dff555d19c57388df7de08db48b4167ebc5a36",
    ),
    "spectrum_JSON": (
        HERE / "EXACT_EFT_PHYSICAL_SCALAR_SPECTRUM_V20.json",
        "797a90473c064a78ef313d56f1894d71114643a19ebd373e86fe8b2911bcf416",
    ),
    "G4_gate_JSON": (
        HERE / "FINAL_G4_EFT_MATHEMATICAL_GATE_V20.json",
        "98664542a4e1bbfba233652737826b974963a31c2e86a15e2d73fda1457d987b",
    ),
    "G5_gate_JSON": (
        HERE / "FINAL_G5_EFT_MATHEMATICAL_GATE_V20.json",
        "6d6e4fd9932a03e35146afb1bca850666e883aaed5e23b73b81f0f703e4e7db9",
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
            raise ArithmeticError(f"frozen EFT G6 dependency drifted: {name}")
        observed[name] = digest
    return observed


def build_report() -> dict[str, Any]:
    artifacts = _artifact_guard()
    exact = spectrum.build_report()
    g4 = g4_gate.build_report()
    g5 = g5_gate.build_report()
    factor = exact["exact_factorization"]
    quotient = exact["physical_quotient"]
    checks = {
        "spectrum_core_source_bound": exact["core_sha256"] == EXPECTED_SPECTRUM_CORE_SHA256,
        "same_EFT_contract_as_G4_G5": (
            exact["model_contract_id"] == EFT_MODEL_CONTRACT_ID
            and g4["contract"]["EFT_model_contract_id"] == EFT_MODEL_CONTRACT_ID
            and g5["contract"]["EFT_model_contract_id"] == EFT_MODEL_CONTRACT_ID
        ),
        "mathematical_EFT_G4_closed": (
            g4["core_sha256"] == EXPECTED_G4_CORE_SHA256
            and g4["classification"]["mathematical_G4_closed_for_EFT_model"]
        ),
        "mathematical_EFT_G5_closed": (
            g5["core_sha256"] == EXPECTED_G5_CORE_SHA256
            and g5["classification"]["mathematical_G5_closed_for_EFT_model"]
        ),
        "complete_486_degree_factorization": factor["total_algebraic_degree"] == 486,
        "exact_38_dimensional_symmetry_kernel": factor["zero_multiplicity"] == 38,
        "complete_448_dimensional_positive_massive_spectrum": (
            factor["positive_massive_multiplicity"] == 448
            and factor["all_nonzero_roots_strictly_positive"]
        ),
        "complete_residual_group_provenance": (
            exact["stabilizer_provenance"][
                "operators_commute_exactly_with_Hessian_and_kinetic_metric"
            ]
            and sum(
                row["full_real_dimension"]
                for row in exact["stabilizer_provenance"]["sector_reports"].values()
            )
            == 486
        ),
        "complete_exact_algebraic_mixing_subspaces": exact["mixing_classification"]["complete"],
        "physical_PQ_axion_retained": (
            quotient["gauged_tangent_dimension"] == 37
            and quotient["physical_PQ_axion_count"] == 1
            and quotient["gauge_quotient_dimension"] == 449
            and quotient["all_38_zero_modes_are_unphysical"] is False
        ),
        "tree_level_exact_uncertainty_is_zero": (
            exact["uncertainty_scope"]["exact_algebraic_tree_level_uncertainty"] == "0"
        ),
        "release_uncertainties_remain_open": (
            exact["uncertainty_scope"]["absolute_scale_and_Wilson_matching_complete"] is False
            and exact["uncertainty_scope"]["loop_and_pole_mass_corrections_complete"] is False
            and exact["uncertainty_scope"]["physical_threshold_uncertainties_complete"] is False
        ),
    }
    if not all(checks.values()):
        failed = [name for name, value in checks.items() if not value]
        raise ArithmeticError(f"EFT G6 mathematical gate failed: {failed}")

    release_criteria = {
        "mathematical_tree_level_EFT_G6_complete": True,
        "absolute_Lambda_EFT_and_Wilson_matching_approved": False,
        "loop_running_and_pole_mass_spectrum_complete": False,
        "threshold_uncertainty_budget_complete": False,
        "external_extended_model_contract_executed": False,
        "authoritative_G1_closed": False,
        "authoritative_G2_closed": False,
        "authoritative_renormalizable_G3_G4_G5_closed": False,
        "parallel_EFT_G6_integrated_into_release_orchestrators": True,
    }
    blockers = [
        name for name, value in release_criteria.items()
        if name != "mathematical_tree_level_EFT_G6_complete" and not value
    ]
    decisive = {
        "contract": {
            "base_model_contract_id": BASE_MODEL_CONTRACT_ID,
            "EFT_model_contract_id": EFT_MODEL_CONTRACT_ID,
            "scope": "normalized exact tree-level dimension-six EFT spectrum",
        },
        "artifact_sha256": artifacts,
        "upstream_cores": {
            "spectrum": exact["core_sha256"],
            "G4": g4["core_sha256"],
            "G5": g5["core_sha256"],
        },
        "mathematical_checks": checks,
        "spectrum_summary": {
            "ambient_real_fields": 486,
            "gauge_quotient_dimension": 449,
            "physical_PQ_axions": 1,
            "positive_massive_modes": 448,
            "primitive_factors": factor["primitive_factor_count"],
            "distinct_mass_squared_roots_including_zero": factor[
                "distinct_mass_squared_root_count_including_zero"
            ],
            "residual_group": exact["stabilizer_provenance"]["unbroken_group"],
            "mixing_subspaces_complete": True,
        },
        "release_criteria": release_criteria,
        "release_blockers": blockers,
        "classification": {
            "mathematical_G6_closed_for_EFT_model": True,
            "release_G6_verified_for_EFT_model": False,
            "authoritative_renormalizable_G6_closed": False,
            "authoritative_G6_gate_mutated": False,
            "whole_model_validated": False,
        },
        "verdict": (
            "Mathematical tree-level G6 is exact for the registered dimension-six "
            "EFT.  Release and the original authoritative renormalizable G6 remain open."
        ),
    }
    return {"status": STATUS, **decisive, "core_sha256": _canonical_sha256(decisive)}


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["spectrum_summary"]
    return "\n".join(
        [
            "# Final EFT G6 mathematical gate",
            "",
            f"- Status: `{report['status']}`",
            f"- Core SHA256: `{report['core_sha256']}`",
            f"- Gauge quotient: {summary['gauge_quotient_dimension']}",
            f"- Physical PQ axion: {summary['physical_PQ_axions']}",
            f"- Positive massive modes: {summary['positive_massive_modes']}",
            f"- Primitive factors: {summary['primitive_factors']}",
            "",
            report["verdict"],
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--allow-unfrozen", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if not args.allow_unfrozen:
        if not EXPECTED_CORE_SHA256:
            raise ArithmeticError("EXPECTED_CORE_SHA256 is not frozen")
        if report["core_sha256"] != EXPECTED_CORE_SHA256:
            raise ArithmeticError("frozen EFT G6 core drifted")
    if args.write:
        OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        OUT_MD.write_text(render_markdown(report))
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
