#!/usr/bin/env python3
"""Fail-closed formal G6 factorization gate for the dimension-six EFT branch.

The original spectrum calculation is algebraically exact, but its elementary
``G_(8,9)`` stabilizer was mislabeled as electromagnetism.  This superseding
gate preserves the formal ``SU(3)_C x U(1)_89`` mass factorization and rejects
its former interpretation as a physical Standard-Model G6 spectrum.
"""
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
import exact_g6_sm_provenance_feasibility_v20 as provenance
import exact_eft_g6_g7_parameterized_matching_v20 as matching
import final_g4_eft_mathematical_gate_v20 as g4_gate
import final_g5_eft_mathematical_gate_v20 as g5_gate


STATUS = "FINAL_EFT_G6_FORMAL_SU3_X_U1_89_FACTOR_PASS__PHYSICAL_G6_OPEN"
BASE_MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
EFT_MODEL_CONTRACT_ID = spectrum.MODEL_CONTRACT_ID
OUT_JSON = HERE / "FINAL_G6_EFT_MATHEMATICAL_GATE_V20.json"
OUT_MD = HERE / "FINAL_G6_EFT_MATHEMATICAL_GATE_V20.md"

EXPECTED_CORE_SHA256 = (
    "3b06ae240c7fce18723f0ce77966e894e688dee65f56859239ff5cf552b1323c"
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
EXPECTED_PROVENANCE_CORE_SHA256 = (
    "0d9bad1158c6c93b29243c08b0265d472be1309267e390edafc3afb556233d39"
)
EXPECTED_MATCHING_CORE_SHA256 = (
    "0c7872a9e309ea817270051a84c685e09fc77ccdbd424e69a71106b7689f275f"
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
    "G6_provenance_source": (
        HERE / "exact_g6_sm_provenance_feasibility_v20.py",
        "8bb67fb09c1cd3b57bf2c02e9ed7f1242a955c5a81ceb7d44dd48435c82618c1",
    ),
    "G6_provenance_JSON": (
        HERE / "EXACT_G6_SM_PROVENANCE_FEASIBILITY_V20.json",
        "a8daa4fb1dadbea48b25ad671a18f8d467384979769772be628a43f75054f6fa",
    ),
    "G6_G7_parameterized_matching_source": (
        HERE / "exact_eft_g6_g7_parameterized_matching_v20.py",
        "4653653de5f7f29b8dd12b7a3d1e387aafab2a193137c08dc2e4be942dceee42",
    ),
    "G6_G7_parameterized_matching_JSON": (
        HERE / "EXACT_EFT_G6_G7_PARAMETERIZED_MATCHING_V20.json",
        "b1bbf35b23a272eadc0a8520f0dac32fb342c7f1f3886088db2d9158acfd5ae9",
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
    provenance_report = provenance.build_report()
    matching_report = matching.build_report()
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
        "formal_complete_486_degree_factorization": (
            factor["total_algebraic_degree"] == 486
        ),
        "exact_38_dimensional_symmetry_kernel": factor["zero_multiplicity"] == 38,
        "complete_448_dimensional_positive_massive_spectrum": (
            factor["positive_massive_multiplicity"] == 448
            and factor["all_nonzero_roots_strictly_positive"]
        ),
        "complete_formal_G89_sector_decomposition": (
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
        "physical_stabilizer_mismatch_source_bound": (
            provenance_report["core_sha256"] == EXPECTED_PROVENANCE_CORE_SHA256
            and provenance_report["classification"][
                "frozen_G6_actual_stabilizer_identified_as_SU3_x_U1_89"
            ]
            is True
            and provenance_report["classification"][
                "mathematical_tree_level_mass_factorization_remains_valid"
            ]
            is True
            and provenance_report["classification"][
                "prior_positive_mathematical_G6_as_physical_SM_spectrum_valid"
            ]
            is False
            and provenance_report["classification"][
                "mathematical_physical_G6_closed"
            ]
            is False
        ),
        "formal_threshold_reinterpretation_source_bound": (
            matching_report["core_sha256"] == EXPECTED_MATCHING_CORE_SHA256
            and matching_report["classification"][
                "formal_residual_SU3_x_U1_89_scalar_threshold_determinants_complete"
            ]
            is True
            and matching_report["classification"][
                "frozen_U1em_identification_correct"
            ]
            is False
            and matching_report["classification"][
                "physical_SM_scalar_thresholds_identified"
            ]
            is False
        ),
    }
    if not all(checks.values()):
        failed = [name for name, value in checks.items() if not value]
        raise ArithmeticError(f"EFT G6 mathematical gate failed: {failed}")

    release_criteria = {
        "formal_SU3_x_U1_89_tree_mass_factorization_complete": True,
        "mathematical_physical_SM_G6_complete": False,
        "SM_preserving_staged_vacuum_verified": False,
        "per_state_SM_and_Pati_Salam_provenance_complete": False,
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
        if name not in {
            "formal_SU3_x_U1_89_tree_mass_factorization_complete",
            "parallel_EFT_G6_integrated_into_release_orchestrators",
        }
        and not value
    ]
    decisive = {
        "contract": {
            "base_model_contract_id": BASE_MODEL_CONTRACT_ID,
            "EFT_model_contract_id": EFT_MODEL_CONTRACT_ID,
            "scope": (
                "normalized exact formal SU3C x U1_89 tree-level dimension-six "
                "EFT mass factorization; not a physical SM spectrum"
            ),
        },
        "artifact_sha256": artifacts,
        "upstream_cores": {
            "spectrum": exact["core_sha256"],
            "G4": g4["core_sha256"],
            "G5": g5["core_sha256"],
            "G6_physical_provenance": provenance_report["core_sha256"],
            "G6_G7_parameterized_matching": matching_report["core_sha256"],
        },
        "mathematical_checks": checks,
        "spectrum_summary": {
            "ambient_real_fields": 486,
            "gauge_quotient_dimension": 449,
            "ungauged_PQ_zero_modes": 1,
            "positive_massive_modes": 448,
            "primitive_factors": factor["primitive_factor_count"],
            "distinct_mass_squared_roots_including_zero": factor[
                "distinct_mass_squared_root_count_including_zero"
            ],
            "residual_group": "SU(3)_C x U(1)_89",
            "upstream_mislabelled_residual_group": exact[
                "stabilizer_provenance"
            ]["unbroken_group"],
            "physical_U1em_interpretation_valid": False,
            "mixing_subspaces_complete": True,
        },
        "release_criteria": release_criteria,
        "release_blockers": blockers,
        "classification": {
            "formal_SU3_x_U1_89_tree_mass_factorization_closed": True,
            "prior_positive_physical_G6_interpretation_valid": False,
            "mathematical_physical_G6_closed": False,
            "mathematical_G6_closed_for_EFT_model": False,
            "release_G6_verified_for_EFT_model": False,
            "authoritative_renormalizable_G6_closed": False,
            "authoritative_G6_gate_mutated": False,
            "whole_model_validated": False,
        },
        "verdict": (
            "The 486-degree tree mass factorization is exact only for the formal "
            "SU(3)_C x U(1)_89 stabilizer of the selected EFT representative. "
            "U(1)_89 is not physical electromagnetism, so physical/mathematical, "
            "release and authoritative G6 all remain open and false."
        ),
    }
    return {"status": STATUS, **decisive, "core_sha256": _canonical_sha256(decisive)}


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["spectrum_summary"]
    return "\n".join(
        [
            "# Final EFT G6 formal-factorization gate",
            "",
            f"- Status: `{report['status']}`",
            f"- Core SHA256: `{report['core_sha256']}`",
            f"- Gauge quotient: {summary['gauge_quotient_dimension']}",
            f"- Ungauged PQ zero mode: {summary['ungauged_PQ_zero_modes']}",
            f"- Corrected residual group: `{summary['residual_group']}`",
            "- Physical/mathematical G6: `False`",
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
