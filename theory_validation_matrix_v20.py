#!/usr/bin/env python3
"""Fail-closed scientific validity matrix for the SO(10) axion v20 candidate.

The matrix answers a narrower question than the numerical engines:

* Which sectors are internally checked?
* Which sectors are only conditional on extra assumptions?
* Which calculations are still open?
* What concrete result would reject the present realization?

States:
    PASS         Complete for the scope explicitly named by the gate.
    CONDITIONAL  A viable witness exists, but extra assumptions or unfixed
                 parameters remain.
    OPEN         The required calculation or data do not yet exist.
    FAIL         A required consistency or empirical condition is violated.

``PASS`` never means that nature realizes the theory.  Full phenomenological
validation requires every mandatory gate to pass, including proton decay,
the scalar vacuum, complete thresholds, and a frozen UV portal point.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import unittest
from pathlib import Path
from typing import Any

from audit_v20_errors import build_audit
import exact_x_symmetry_consistency_gate_v20 as exact_x_gate
import g1_g8_gate_ledger_v20 as gate_ledger
import corrected_rank1_endpoint_v21 as corrected_rank1
import canonical_g1_g8_gauged_u1x_v21 as canonical_gates
import authoritative_full_model_gate_v20 as authoritative_gate

ROOT = Path(__file__).resolve().parent
MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
EXACT_X_V3_SOURCE = "exact_x_symmetry_consistency_gate_v20.py"
EXACT_X_V3_TEST = "test_exact_x_symmetry_consistency_gate_v20.py"
EXACT_X_V3_MD = "EXACT_X_SYMMETRY_CONSISTENCY_GATE_V20.md"
EXACT_X_V3_INPUT_MANIFEST = "models/EXACT_X_EXTERNAL_INPUT_MANIFEST_V20.json"
EXACT_X_V3_TRUSTED_SARAH_MANIFEST = (
    "models/SARAH_4_15_3_CANONICAL_SOURCE_TREE_V20.json"
)
RENORMALIZABLE_G1_COMPONENT_TENSOR_SOURCE = (
    "exact_gauged_u1x_g1_component_tensor_closure_v20.py"
)
RENORMALIZABLE_G2_MATHEMATICAL_SOURCE = (
    "exact_gauged_u1x_g2_mathematical_closure_v20.py"
)
FINAL_G6_EFT_GATE_SOURCE = "final_g6_eft_mathematical_gate_v20.py"
EFT_G7_NONIDENTIFIABILITY_SOURCE = (
    "exact_eft_g7_threshold_nonidentifiability_v20.py"
)
G6_SM_PROVENANCE_SOURCE = "exact_g6_sm_provenance_feasibility_v20.py"
G6_G7_PARAMETERIZED_MATCHING_SOURCE = (
    "exact_eft_g6_g7_parameterized_matching_v20.py"
)
AUTHORITATIVE_GAUGE_BETAS_SOURCE = (
    "exact_authoritative_so10_u1x_gauge_betas_v20.py"
)
PYRATE3_GAUGE_REPLAY_SOURCE = "pyrate3_so10_u1x_gauge_beta_replay_v20.py"
PHYSICAL_G7_COMPONENT_THRESHOLD_SOURCE = (
    "exact_physical_g7_component_threshold_contract_v20.py"
)
PHYSICAL_G7_COMPONENT_THRESHOLD_TEST = (
    "test_exact_physical_g7_component_threshold_contract_v20.py"
)
PHYSICAL_G7_COMPONENT_THRESHOLD_MD = (
    "EXACT_PHYSICAL_G7_COMPONENT_THRESHOLD_CONTRACT_V20.md"
)
NORMALIZED_YUKAWA_CGCS_SOURCE = "exact_normalized_so10_yukawa_cgcs_v20.py"
NORMALIZED_YUKAWA_CGCS_TEST = "test_exact_normalized_so10_yukawa_cgcs_v20.py"
NORMALIZED_YUKAWA_CGCS_MD = "EXACT_NORMALIZED_SO10_YUKAWA_CGCS_V20.md"
PHYSICAL_SM_VACUUM_SOURCE = "physical_sm_vacuum_local_feasibility_v20.py"
PHYSICAL_SM_VACUUM_TEST = "test_physical_sm_vacuum_local_feasibility_v20.py"
PHYSICAL_SM_VACUUM_MD = "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.md"
PHYSICAL_SM_SOURCE_EQUALITY_SOURCE = (
    "physical_sm_source_algebra_equality_frontier_v20.py"
)
PHYSICAL_SM_SOURCE_EQUALITY_TEST = (
    "test_physical_sm_source_algebra_equality_frontier_v20.py"
)
PHYSICAL_SM_SOURCE_EQUALITY_MD = (
    "PHYSICAL_SM_SOURCE_ALGEBRA_EQUALITY_FRONTIER_V20.md"
)
PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_SOURCE = (
    "exact_physical_sm_five_amplitude_equality_v20.py"
)
PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_TEST = (
    "test_exact_physical_sm_five_amplitude_equality_v20.py"
)
PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_MD = (
    "EXACT_PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_V20.md"
)
PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_SOURCE = (
    "exact_physical_sm_hard_projector_hessians_v20.py"
)
PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_TEST = (
    "test_exact_physical_sm_hard_projector_hessians_v20.py"
)
PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_MD = (
    "EXACT_PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_V20.md"
)
PHYSICAL_SM_LAST_SIX_HESSIANS_SOURCE = (
    "exact_physical_sm_last_six_hessians_v20.py"
)
PHYSICAL_SM_LAST_SIX_HESSIANS_TEST = (
    "test_exact_physical_sm_last_six_hessians_v20.py"
)
PHYSICAL_SM_LAST_SIX_HESSIANS_MD = (
    "EXACT_PHYSICAL_SM_LAST_SIX_HESSIANS_V20.md"
)
PHYSICAL_SM_37_ROW_AGGREGATE_SOURCE = "exact_physical_sm_37_row_aggregate_v20.py"
PHYSICAL_SM_37_ROW_AGGREGATE_TEST = "test_exact_physical_sm_37_row_aggregate_v20.py"
PHYSICAL_SM_37_ROW_AGGREGATE_MD = "EXACT_PHYSICAL_SM_37_ROW_AGGREGATE_V20.md"
PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_SOURCE = "exact_physical_sm_local_equality_orbit_v20.py"
PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_TEST = "test_exact_physical_sm_local_equality_orbit_v20.py"
PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_MD = "EXACT_PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_V20.md"
PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_SOURCE = (
    "exact_physical_sm_g4_g5_branch_mismatch_v20.py"
)
PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_TEST = (
    "test_exact_physical_sm_g4_g5_branch_mismatch_v20.py"
)
PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_MD = (
    "EXACT_PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_V20.md"
)
PHYSICAL_SM_HEAVY_VECTOR_SOURCE = "exact_physical_sm_heavy_vector_masses_v20.py"
PHYSICAL_SM_HEAVY_VECTOR_TEST = "test_exact_physical_sm_heavy_vector_masses_v20.py"
PHYSICAL_SM_HEAVY_VECTOR_MD = "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MASSES_V20.md"
PHYSICAL_SM_HEAVY_VECTOR_MSBAR_SOURCE = (
    "exact_physical_sm_heavy_vector_msbar_matching_v20.py"
)
PHYSICAL_SM_HEAVY_VECTOR_MSBAR_TEST = (
    "test_exact_physical_sm_heavy_vector_msbar_matching_v20.py"
)
PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MD = (
    "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_V20.md"
)
PHYSICAL_SM_VECTOR_RXI_SOURCE = (
    "exact_physical_sm_vector_rxi_vacuum_cancellation_v20.py"
)
PHYSICAL_SM_VECTOR_RXI_TEST = (
    "test_exact_physical_sm_vector_rxi_vacuum_cancellation_v20.py"
)
PHYSICAL_SM_VECTOR_RXI_MD = (
    "EXACT_PHYSICAL_SM_VECTOR_RXI_VACUUM_CANCELLATION_V20.md"
)
CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_SOURCE = (
    "conditional_physical_sm_eft_hessian_spectrum_v20.py"
)
CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_TEST = (
    "test_conditional_physical_sm_eft_hessian_spectrum_v20.py"
)
CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_MD = (
    "CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_V20.md"
)
PHYSICAL_SM_G6_G7_FRONTIER_SOURCE = (
    "exact_physical_sm_g6_g7_closure_frontier_v20.py"
)
PHYSICAL_SM_G6_G7_FRONTIER_TEST = (
    "test_exact_physical_sm_g6_g7_closure_frontier_v20.py"
)
PHYSICAL_SM_G6_G7_FRONTIER_MD = (
    "EXACT_PHYSICAL_SM_G6_G7_CLOSURE_FRONTIER_V20.md"
)
PHYSICAL_SM_G8_FRONTIER_SOURCE = (
    "exact_physical_sm_g8_identifiability_frontier_v20.py"
)
PHYSICAL_SM_G8_FRONTIER_TEST = (
    "test_exact_physical_sm_g8_identifiability_frontier_v20.py"
)
PHYSICAL_SM_G8_FRONTIER_MD = (
    "EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_V20.md"
)

ARTIFACTS = {
    "engine": "so10_axion_v20_verdict.json",
    "error_audit": "V20_ERROR_AUDIT.json",
    "falsification": "FALSIFICATION_VERDICT.json",
    "extensive": "EXTENSIVE_CONFIRM_FALSIFY_VERDICT.json",
    "global_flavour": "GLOBAL_FLAVOUR_FIT_V20_VERDICT.json",
    "open_gaps": "OPEN_GAPS_CLOSURE_V20_VERDICT.json",
    "vacuum": "UV_VACUUM_ALIGNMENT_V20_VERDICT.json",
    "rge": "YUKAWA_RGE_2LOOP_V20_VERDICT.json",
    "fcnc": "FCNC_EXACT_LIKELIHOOD_V20_VERDICT.json",
    "sphere": "PORTAL_FULL_COMPLEX_ORIENTATION_SPHERE_V20_VERDICT.json",
    "posterior": "PORTAL_YUKAWA_POSTERIOR_V20_VERDICT.json",
    "haloscope": "HALOSCOPE_37GHZ_LIMIT_COMPARE_V20_VERDICT.json",
    "next_physics": "NEXT_PHYSICS_ANALYSIS_VERDICT.json",
    "na62": "NA62_POINTWISE_LIMIT_V20_VERDICT.json",
    "twist": "TWIST_MASSLESS_LIMIT_V20_VERDICT.json",
    "cert_math": "THEORY_CERTIFICATION_MATH_V20_VERDICT.json",
    "pati_salam": "PATI_SALAM_YUKAWA_MATCHING_V20_VERDICT.json",
    "unit_attestation": "CURRENT_UNIT_TEST_ATTESTATION.json",
    "x_contract": "EXACT_X_SYMMETRY_CONSISTENCY_GATE_V20.json",
    "gauged_contract": "GAUGED_U1X_SCALAR_CONTRACT_V20.json",
    "gauged_g2": "GAUGED_U1X_G2_DERIVATIVE_AUDIT_V20.json",
    "renormalizable_g1_component_tensor": (
        "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.json"
    ),
    "renormalizable_g2_mathematical": (
        "EXACT_GAUGED_U1X_G2_MATHEMATICAL_CLOSURE_V20.json"
    ),
    "g1_g8": "G1_G8_GATE_LEDGER_V20.json",
    "g6_spectrum": "G6_FULL_PHYSICAL_SPECTRUM_V20.json",
    "g3_stationarity": "G3_FULL_STATIONARITY_FEASIBILITY_V20.json",
    "g3_hessian": "G3_FULL_HESSIAN_CLASSIFICATION_V20.json",
    "g3_search": "G3_STATIONARY_STABILITY_SEARCH_V20.json",
    "gauged_g3": "GAUGED_U1X_G3_STABILITY_V20.json",
    "gauged_g3_common_kernel": "GAUGED_U1X_G3_CORRECTED_COMMON_KERNEL_V20.json",
    "gauged_g3_sos_candidate": "GAUGED_U1X_G3_SOS_CANDIDATE_V20.json",
    "gauged_g3_pd_rank": "EXACT_GAUGED_U1X_G3_PD_RANK_CERTIFICATE_V20.json",
    "gauged_g3_a_square": "EXACT_GAUGED_U1X_G3_A_SQUARE_RECOUPLING_V20.json",
    "gauged_g3_sos_bfb": "EXACT_GAUGED_U1X_G3_SOS_BFB_STATIONARITY_V20.json",
    "gauged_g3_kernel_bound": "EXACT_GAUGED_U1X_G3_KERNEL_QUARTIC_BOUND_V20.json",
    "gauged_g3_replacement": "EXACT_GAUGED_U1X_G3_REPLACEMENT_STATIONARY_ORBIT_V20.json",
    "gauged_g3_su5_pd": "EXACT_GAUGED_U1X_G3_SU5_DELTA_PD_SOS_V20.json",
    "gauged_g3_su5_hsx": "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXTENSION_V20.json",
    "gauged_g3_su5_hsx_exact_hessian": "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXACT_HESSIAN_V20.json",
    "gauged_g3_su5_equality": "EXACT_GAUGED_U1X_G3_SU5_EQUALITY_ORBIT_V20.json",
    "gauged_g3_su5_phi_orbit": "EXACT_GAUGED_U1X_G3_SU5_PHI_ORBIT_LEMMA_V20.json",
    "gauged_g3_su5_phi_local_component": "EXACT_GAUGED_U1X_G3_SU5_PHI_LOCAL_COMPONENT_V20.json",
    "gauged_g3_su5_phi_su3_slice": "EXACT_GAUGED_U1X_G3_SU5_PHI_SU3_SLICE_V20.json",
    "gauged_g3_su5_gap": "EXACT_GAUGED_U1X_G3_SU5_CHIRAL_GLOBAL_GAP_REDUCTION_V20.json",
    "gauged_g3_su5_fixed_f_offkernel": "EXACT_GAUGED_U1X_G3_SU5_FIXED_F_OFFKERNEL_BOUND_V20.json",
    "gauged_g3_su5_max_negative_zero_residual": "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_ZERO_RESIDUAL_BOUND_V20.json",
    "gauged_g3_su5_max_negative_full_residual": "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_FULL_RESIDUAL_BOUND_V20.json",
    "gauged_g3_su5_max_negative_rank1_su3_slice": "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_RANK1_SU3_SLICE_V20.json",
    "gauged_g3_rank1_su4_stabilizer": "EXACT_GAUGED_U1X_G3_RANK1_SU4_STABILIZER_V20.json",
    "gauged_g3_rank1_su4_phi210_intertwiners": "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_INTERTWINERS_V20.json",
    "gauged_g3_rank1_su4_aligned_carriers": "EXACT_GAUGED_U1X_G3_RANK1_SU4_ALIGNED_CARRIERS_V20.json",
    "gauged_g3_rank1_su4_phi210_quadratic_basis": "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_QUADRATIC_BASIS_V20.json",
    "gauged_g3_rank1_su4_augmented_sos_census": "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CENSUS_V20.json",
    "gauged_g3_rank1_su4_augmented_sos_cubic_map": "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_V20.json",
    "gauged_g3_rank1_su4_augmented_sos_quartic_map": "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.json",
    "gauged_g3_rank1_su4_augmented_sos_psd_target": "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_V20.json",
    "gauged_g3_rank1_su4_corrected_manifest": "corrected_rank1_publication_v21/EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_PUBLICATION_V21_MANIFEST.json",
    "gauged_g3_rank1_su4_corrected_theorem": "corrected_rank1_publication_v21/EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_FIXED_ENDPOINT_THEOREM_V21.json",
    "gauged_g3_rank1_su4_corrected_source": "corrected_rank1_publication_v21/EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_SOURCE_RECONSTRUCTION_V21.json",
    "gauged_g3_rank1_su4_corrected_verify": "corrected_rank1_publication_v21/EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_POSITIVE_GRAM_VERIFY_V21.json",
    "gauged_g3_rank1_su4_corrected_live": "corrected_rank1_publication_v21/EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_LIVE_POLYNOMIAL_V21.json",
    "gauged_g3_rank1_su4_corrected_overflow": "corrected_rank1_publication_v21/EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_ORDERED_SPECTRAL_OVERFLOW_V21.json",
    "gauged_g3_alternative_global_sos": "EXACT_GAUGED_U1X_G3_ALTERNATIVE_GLOBAL_SOS_AUDIT_V20.json",
    "final_g3": "FINAL_G3_ACCEPTANCE_GATE_V20.json",
    "final_g3_eft": "FINAL_G3_EFT_ACCEPTANCE_GATE_V20.json",
    "final_g4_eft": "FINAL_G4_EFT_MATHEMATICAL_GATE_V20.json",
    "final_g5_eft": "FINAL_G5_EFT_MATHEMATICAL_GATE_V20.json",
    "final_g6_eft": "FINAL_G6_EFT_MATHEMATICAL_GATE_V20.json",
    "eft_g7_nonidentifiability": (
        "EXACT_EFT_G7_THRESHOLD_NONIDENTIFIABILITY_V20.json"
    ),
    "g6_sm_provenance": "EXACT_G6_SM_PROVENANCE_FEASIBILITY_V20.json",
    "g6_g7_parameterized_matching": (
        "EXACT_EFT_G6_G7_PARAMETERIZED_MATCHING_V20.json"
    ),
    "authoritative_gauge_betas": (
        "EXACT_AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_V20.json"
    ),
    "pyrate3_gauge_replay": "PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_V20.json",
    "physical_g7_component_threshold": (
        "EXACT_PHYSICAL_G7_COMPONENT_THRESHOLD_CONTRACT_V20.json"
    ),
    "normalized_yukawa_cgcs": "EXACT_NORMALIZED_SO10_YUKAWA_CGCS_V20.json",
    "physical_sm_vacuum": "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.json",
    "physical_sm_source_equality": (
        "PHYSICAL_SM_SOURCE_ALGEBRA_EQUALITY_FRONTIER_V20.json"
    ),
    "physical_sm_five_amplitude_equality": (
        "EXACT_PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_V20.json"
    ),
    "physical_sm_hard_projector_hessians": (
        "EXACT_PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_V20.json"
    ),
    "physical_sm_last_six_hessians": (
        "EXACT_PHYSICAL_SM_LAST_SIX_HESSIANS_V20.json"
    ),
    "physical_sm_37_row_aggregate": (
        "EXACT_PHYSICAL_SM_37_ROW_AGGREGATE_V20.json"
    ),
    "physical_sm_local_equality_orbit": (
        "EXACT_PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_V20.json"
    ),
    "physical_sm_g4_g5_branch_mismatch": (
        "EXACT_PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_V20.json"
    ),
    "physical_sm_heavy_vectors": "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MASSES_V20.json",
    "physical_sm_heavy_vector_msbar": (
        "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_V20.json"
    ),
    "physical_sm_vector_rxi": (
        "EXACT_PHYSICAL_SM_VECTOR_RXI_VACUUM_CANCELLATION_V20.json"
    ),
    "conditional_physical_sm_scalar_spectrum": (
        "CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_V20.json"
    ),
    "physical_sm_g6_g7_closure_frontier": (
        "EXACT_PHYSICAL_SM_G6_G7_CLOSURE_FRONTIER_V20.json"
    ),
    "physical_sm_g8_identifiability_frontier": (
        "EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_V20.json"
    ),
    "authoritative": "AUTHORITATIVE_FULL_MODEL_GATE_V20.json",
}

VALID_STATES = {"PASS", "CONDITIONAL", "OPEN", "BLOCKED", "FAIL"}


def _overall_state(integrity_pass: bool, gates: list[dict[str, Any]]) -> str:
    """Summarize gate state without promoting unresolved work to PASS."""
    if not integrity_pass:
        return "FAIL"
    states = {str(gate.get("state")) for gate in gates}
    for state in ("BLOCKED", "OPEN", "CONDITIONAL"):
        if state in states:
            return state
    return "PASS"


def _dig(value: Any, *path: str, default: Any = None) -> Any:
    current = value
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return value if isinstance(value, dict) else None


def load_reports(root: Path = ROOT) -> tuple[dict[str, dict[str, Any]], list[str]]:
    reports: dict[str, dict[str, Any]] = {}
    missing: list[str] = []
    for key, filename in ARTIFACTS.items():
        value = _load_json(root / filename)
        if value is None:
            missing.append(filename)
        else:
            reports[key] = value

    # The independent audit is cheap and deliberately does not import the
    # model engines. Rebuild it when its JSON artifact is absent.
    if "error_audit" not in reports:
        reports["error_audit"] = build_audit()
        if "V20_ERROR_AUDIT.json" in missing:
            missing.remove("V20_ERROR_AUDIT.json")
    return reports, missing


def _gate(
    name: str,
    state: str,
    summary: str,
    evidence: dict[str, Any],
    kill_condition: str,
    green_condition: str,
    *,
    mandatory_for_full_validation: bool = True,
) -> dict[str, Any]:
    if state not in VALID_STATES:
        raise ValueError(f"invalid gate state {state!r}")
    return {
        "name": name,
        "state": state,
        "summary": summary,
        "evidence": evidence,
        "kill_condition": kill_condition,
        "green_condition": green_condition,
        "mandatory_for_full_validation": bool(mandatory_for_full_validation),
    }


def _core_gate(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    engine = reports.get("engine", {})
    audit = reports.get("error_audit", {})
    falsification = reports.get("falsification", {})
    extensive = reports.get("extensive", {})
    checks = {
        "engine_42_of_42": (
            engine.get("status") == "PASS"
            and engine.get("n_checks_total") == 42
            and engine.get("n_checks_failed") == 0
        ),
        "independent_audit_pass": (
            audit.get("status") == "PASS"
            and audit.get("n_checks_failed") == 0
        ),
        "adversarial_zero_hard_failures": (
            falsification.get("status") == "PASS"
            and falsification.get("n_hard_failed") == 0
            and falsification.get("n_soft_overclaim_missed") == 0
        ),
        "extensive_53_of_53": (
            extensive.get("status") == "PASS"
            and extensive.get("n_extensive_checks") == 53
            and extensive.get("n_failed") == 0
        ),
    }
    present = bool(engine) and bool(audit)
    if any(
        value is False
        for key, value in checks.items()
        if key in ("engine_42_of_42", "independent_audit_pass")
    ):
        state = "FAIL"
    elif not present or not all(checks.values()):
        state = "OPEN"
    else:
        state = "PASS"
    return _gate(
        "mathematical_and_software_core",
        state,
        (
            "Anomalies, group/Lorentz certificates, core numerical anchors, "
            "and adversarial checks are the minimum internal-consistency gate."
        ),
        checks,
        "Any anomaly, nonzero-forced contraction, arithmetic, or reproducibility failure.",
        "Independent implementations reproduce every frozen core result with zero hard failures.",
    )


def _tool_native_bound_root_contract(audit: dict[str, Any]) -> bool:
    scaffold = audit.get(
        "executable_scaffold_contract", audit.get("declared_symmetries", {})
    )
    external = audit.get("external_model_validation", {})
    external_checks = external.get("checks", {})
    return bool(
        scaffold.get("model_syntax_class") == "sarah_native"
        and scaffold.get("tool_native_sarah_syntax") is True
        and scaffold.get("statically_executable_model_contract") is True
        and _dig(
            scaffold,
            "lagrangian",
            "registered_in_GaugeES_LagrangianInput",
            default=False,
        )
        is True
        and external.get("schema") == exact_x_gate.EXTERNAL_VALIDATION_SCHEMA
        and external.get("present") is True
        and external.get("valid") is True
        and external.get("fresh_for_exact_model_bytes") is True
        and set(external_checks)
        == gate_ledger.EXPECTED_EXACT_X_V3_EXTERNAL_CHECKS
        and all(
            external_checks.get(name) is True
            for name in gate_ledger.EXPECTED_EXACT_X_V3_EXTERNAL_CHECKS
        )
    )


def _model_contract_gate(
    reports: dict[str, dict[str, Any]],
    exact_x_v3_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if exact_x_v3_contract is None:
        exact_x_v3_contract = {}
    audit = reports.get("x_contract", {})
    desired = reports.get("gauged_contract", {})
    audit_executes = bool(audit) and audit.get("n_failed") == 0
    desired_executes = bool(desired) and desired.get("n_failed") == 0
    consistent = bool(audit.get("contract_consistent", False))
    implementation_matches = bool(
        desired.get("implementation_matches_manuscript", False)
    )
    tool_native_bound_evidence = _tool_native_bound_root_contract(audit)
    if not audit_executes or not desired_executes:
        state = "OPEN"
    elif (
        not consistent
        or not implementation_matches
        or not tool_native_bound_evidence
    ):
        state = "BLOCKED"
    else:
        state = "PASS"
    return _gate(
        "authoritative_model_contract",
        state,
        (
            "The manuscript gauges U(1)_X. The scalar census and every "
            "tool-native executable model must implement that same contract, "
            "with manifest/log-bound external evidence, before any "
            "G1-G8 result can validate the manuscript."
        ),
        {
            "audit_present": bool(audit),
            "audit_executes": audit_executes,
            "desired_contract_present": bool(desired),
            "desired_contract_executes": desired_executes,
            "contract_consistent": consistent,
            "implementation_matches_manuscript": implementation_matches,
            "tool_native_bound_external_evidence": tool_native_bound_evidence,
            "exact_X_v3_fail_closed_contract_source_bound": (
                exact_x_v3_contract.get("source_bound") is True
            ),
            "trusted_SARAH_4_15_3_source_tree_manifest_closed": (
                exact_x_v3_contract.get(
                    "trusted_SARAH_4_15_3_source_tree_manifest_closed"
                )
                is True
            ),
            "external_v3_execution_attestation_present": (
                exact_x_v3_contract.get(
                    "external_v3_execution_attestation_present"
                )
                is True
            ),
            "authoritative_G1_closed_by_exact_X_v3": False,
            "model_syntax_class": _dig(
                audit,
                "executable_scaffold_contract",
                "model_syntax_class",
            ),
            "conflicts": audit.get("contract_conflicts", []),
            "blockers": audit.get("scientific_blockers", []),
        },
        "The implemented symmetry contract differs from the theory being claimed.",
        (
            "The TeX definition, tool-native gauge sector, exact-X scalar census, "
            "and derivative/quotient calculations carry one matching contract ID, "
            "and v3 evidence binds the trusted SARAH tree, model, driver, "
            "resolved runtime, probe log, and process log."
        ),
    )


def _canonical_authority_gate(
    canonical: dict[str, Any],
    authoritative: dict[str, Any] | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    """Make qualified V21 evidence the sole G1--G8 closure authority.

    The historical scalar ledger remains useful evidence elsewhere in this
    matrix.  Its bare G1--G8 labels are deliberately absent here: neither a
    CLOSED nor a BLOCKED legacy row may promote or veto this gate.
    """
    authoritative = authoritative or {}
    body = dict(canonical) if isinstance(canonical, dict) else {}
    integrity = body.pop("integrity", None)
    summary_integrity_valid = bool(
        isinstance(integrity, dict)
        and integrity.get("core_sha256") == canonical_gates._sha(body)
        and canonical.get("schema") == canonical_gates.SCHEMA
        and canonical.get("contract_namespace")
        == canonical_gates.CONTRACT_NAMESPACE
        and canonical.get("definition_sha256")
        == canonical_gates.DEFINITION_SHA256
        and canonical.get("n_failed") == 0
        and canonical.get("failures") == []
        and all(canonical.get("checks", {}).values())
    )
    live_revalidation_valid = bool(
        summary_integrity_valid
        and authoritative_gate._canonical_evidence_complete(
            canonical, canonical_gates.ROOT if root is None else root
        )
    )
    integrity_valid = live_revalidation_valid
    rows = canonical.get("gates", []) if isinstance(canonical, dict) else []
    qualified_ids = [row.get("qualified_gate_id") for row in rows]
    expected_ids = [row["qualified_gate_id"] for row in canonical_gates.GATES]
    closed = bool(
        integrity_valid
        and qualified_ids == expected_ids
        and len(rows) == 8
        and all(row.get("closed") is True for row in rows)
        and canonical.get("closure_counts") == {"closed": 8, "open": 0}
        and canonical.get("overall_state") == "PASS"
        and canonical.get("classification", {}).get(
            "all_canonical_gates_closed"
        )
        is True
        and canonical.get("classification", {}).get("whole_model_validated")
        is True
    )
    authoritative_present = bool(authoritative)
    authoritative_classification = (
        authoritative.get("classification", {})
        if authoritative_present
        else {}
    )
    authoritative_consistent = bool(
        authoritative_present
        and authoritative.get("canonical_g1_g8") == canonical
        and authoritative.get("canonical_g1_g8_summary")
        == canonical.get("closure_counts")
        and authoritative_classification.get("all_g1_g8_closed") is closed
        and authoritative_classification.get("whole_model_validated") is closed
        and authoritative.get("flag", {}).get(
            "legacy_ledger_controls_authoritative_closure"
        )
        is False
        and authoritative.get("legacy_g1_g8_evidence", {}).get(
            "authoritative_for_closure"
        )
        is False
    )
    if not integrity_valid or (authoritative_present and not authoritative_consistent):
        state = "FAIL"
    elif closed and authoritative_consistent:
        state = "PASS"
    else:
        state = "BLOCKED"
    return _gate(
        "canonical_gauged_u1x_G1_G8_authority",
        state,
        (
            "Qualified canonical V21 evidence, not matching bare numbers in the "
            "legacy scalar ledger, controls full-authoritative G1--G8 closure."
        ),
        {
            "canonical_integrity_valid": integrity_valid,
            "canonical_summary_integrity_valid": summary_integrity_valid,
            "canonical_gate_specific_verifiers_live_revalidated": (
                live_revalidation_valid
            ),
            "canonical_contract_namespace": canonical.get("contract_namespace"),
            "canonical_definition_sha256": canonical.get("definition_sha256"),
            "canonical_closure_counts": canonical.get("closure_counts"),
            "all_canonical_gates_closed": closed,
            "authoritative_report_present": authoritative_present,
            "authoritative_report_matches_canonical_state": (
                authoritative_consistent
            ),
            "legacy_ledger_controls_authoritative_closure": False,
        },
        "Any malformed canonical artifact, broken dependency, or inconsistent authoritative summary.",
        "All eight qualified V21 gates close and the authoritative report reproduces that exact canonical state.",
    )


def _operator_gate(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    audit = reports.get("error_audit", {})
    soft = set(audit.get("soft_falsifications_of_manuscript_overclaims", []))
    incomplete = "manuscript portal list is incomplete" in soft
    state = "OPEN" if incomplete or not audit else "CONDITIONAL"
    return _gate(
        "complete_operator_basis_and_PQ_quality",
        state,
        (
            "The anomaly/PQ-quality core survives, but the independent audit "
            "finds additional charge-allowed monomials and the displayed P=8 "
            "number remains a unit-coefficient kernel rather than a summed amplitude."
        ),
        {
            "independent_audit_available": bool(audit),
            "manuscript_portal_list_incomplete": incomplete,
            "soft_falsifications": sorted(soft),
        },
        (
            "An omitted lower-dimensional gauge/Lorentz invariant gives "
            "|Delta theta| >= 1e-10 for physically reasonable coefficients."
        ),
        (
            "An independent Hilbert-series/exhaustive basis proves completeness "
            "and the summed Wilson/Clebsch/flavour/RG amplitude remains safe."
        ),
    )


def _vacuum_gate(
    reports: dict[str, dict[str, Any]],
    renormalizable_g1_component_tensor_closure: dict[str, Any] | None = None,
    renormalizable_g2_mathematical_closure: dict[str, Any] | None = None,
    parallel_eft_g3_acceptance: dict[str, Any] | None = None,
    parallel_eft_g4_mathematical: dict[str, Any] | None = None,
    parallel_eft_g5_mathematical: dict[str, Any] | None = None,
    parallel_eft_g6_spectrum: dict[str, Any] | None = None,
    g6_sm_provenance: dict[str, Any] | None = None,
    g6_g7_parameterized_matching: dict[str, Any] | None = None,
    physical_sm_vacuum: dict[str, Any] | None = None,
    physical_sm_source_equality: dict[str, Any] | None = None,
    physical_sm_five_amplitude_equality: dict[str, Any] | None = None,
    physical_sm_hard_projector_hessians: dict[str, Any] | None = None,
    physical_sm_last_six_hessians: dict[str, Any] | None = None,
    physical_sm_37_row_aggregate: dict[str, Any] | None = None,
    physical_sm_local_equality_orbit: dict[str, Any] | None = None,
    physical_sm_g4_g5_branch_mismatch: dict[str, Any] | None = None,
    physical_sm_heavy_vectors: dict[str, Any] | None = None,
    conditional_physical_sm_scalar_spectrum: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract_state = _model_contract_gate(reports)["state"]
    ledger = reports.get("g1_g8", {})
    authoritative_gates = ledger.get("gates", {})
    g1_closed = _dig(authoritative_gates, "G1", "status") == "CLOSED"
    g2_closed = _dig(authoritative_gates, "G2", "status") == "CLOSED"
    g3_closed = _dig(authoritative_gates, "G3", "status") == "CLOSED"
    g4_closed = _dig(authoritative_gates, "G4", "status") == "CLOSED"
    g5_closed = _dig(authoritative_gates, "G5", "status") == "CLOSED"
    g6_closed = _dig(authoritative_gates, "G6", "status") == "CLOSED"
    scoped = ledger.get("gauged_u1x_scalar_subtheorems", {})
    ledger_g1_component_tensor_closure = ledger.get(
        "renormalizable_G1_component_tensor_closure", {}
    )
    if renormalizable_g1_component_tensor_closure is None:
        renormalizable_g1_component_tensor_closure = {}
    g1_component_tensor_view_matches_ledger = bool(
        renormalizable_g1_component_tensor_closure
        and ledger_g1_component_tensor_closure
        and renormalizable_g1_component_tensor_closure
        == ledger_g1_component_tensor_closure
    )
    mathematical_g1_component_tensor_closure = bool(
        g1_component_tensor_view_matches_ledger
        and renormalizable_g1_component_tensor_closure.get("source_bound") is True
        and renormalizable_g1_component_tensor_closure.get(
            "mathematical_G1_closed_for_renormalizable_model"
        )
        is True
        and renormalizable_g1_component_tensor_closure.get(
            "authoritative_G1_promoted_closed"
        )
        is False
        and renormalizable_g1_component_tensor_closure.get("release_G1_verified")
        is False
    )
    ledger_g2_mathematical_closure = ledger.get(
        "renormalizable_G2_mathematical_closure", {}
    )
    if renormalizable_g2_mathematical_closure is None:
        renormalizable_g2_mathematical_closure = {}
    g2_mathematical_view_matches_ledger = bool(
        renormalizable_g2_mathematical_closure
        and ledger_g2_mathematical_closure
        and renormalizable_g2_mathematical_closure
        == ledger_g2_mathematical_closure
    )
    mathematical_g2_component_potential_closure = bool(
        mathematical_g1_component_tensor_closure
        and g2_mathematical_view_matches_ledger
        and renormalizable_g2_mathematical_closure.get("source_bound") is True
        and renormalizable_g2_mathematical_closure.get(
            "mathematical_G2_closed_for_renormalizable_model"
        )
        is True
        and renormalizable_g2_mathematical_closure.get(
            "authoritative_G2_promoted_closed"
        )
        is False
        and renormalizable_g2_mathematical_closure.get("release_G2_verified")
        is False
    )
    g1_census_marker = _dig(
        scoped, "G1", "multiplicity_census_complete", default=None
    )
    g1_multiplicity_census_complete = bool(
        g1_census_marker
        if g1_census_marker is not None
        else (
            g1_closed
            or _dig(
                authoritative_gates,
                "G1",
                "scoped_calculation_complete",
                default=False,
            )
            or _dig(scoped, "G1", "scoped_status", default="").startswith(
                "COMPLETE_"
            )
        )
    )
    g1_component_marker = _dig(
        scoped,
        "G1",
        "explicit_component_tensor_subset_integration_complete",
        default=None,
    )
    g1_full_marker = _dig(scoped, "G1", "full_G1_closed", default=None)
    g1_gate_full_marker = _dig(
        authoritative_gates,
        "G1",
        "full_gate_calculation_complete",
        default=None,
    )
    if mathematical_g1_component_tensor_closure:
        # Mathematical component-tensor closure is contract independent.  The
        # authoritative G1 status above still remains fail-closed on the
        # external executable-model contract.
        g1_full_component_tensor_integration_complete = True
    elif g1_component_marker is False:
        g1_full_component_tensor_integration_complete = False
    elif g1_full_marker is not None or g1_gate_full_marker is not None:
        g1_full_component_tensor_integration_complete = bool(
            g1_multiplicity_census_complete
            and (g1_full_marker is True or g1_gate_full_marker is True)
            and g1_component_marker is not False
        )
    else:
        # Compatibility for older, internally consistent ledgers that predate
        # the explicit census/full-G1 split.
        g1_full_component_tensor_integration_complete = bool(g1_closed)
    g1_scoped_complete = g1_multiplicity_census_complete
    scalar_contract = reports.get("gauged_contract", {})
    scalar_contract_pre_audit_g2_flag = _dig(
        scalar_contract,
        "flags",
        "G2_gauged_u1x_derivatives_certified",
        default=None,
    )
    g2_audit = reports.get("gauged_g2", {})
    g2_counts = g2_audit.get("counts", {})
    g2_stationary = _dig(
        g2_audit,
        "stationary_Hessian_bridge",
        "promoted_stationarity_matrix",
        default={},
    )
    g2_scoped_complete = bool(
        g2_audit.get("model_contract_id") == MODEL_CONTRACT_ID
        and g2_audit.get("n_failed") == 0
        and _dig(
            g2_audit,
            "flags",
            "G2_gauged_u1x_derivatives_certified",
            default=False,
        )
        and _dig(
            g2_audit,
            "flags",
            "exact_Delta_R_projector_zero_certificate",
            default=False,
        )
        and _dig(
            g2_audit,
            "flags",
            "exact_projector_zero_corrected_normalized_SVD_rank_13",
            default=False,
        )
        and _dig(
            g2_audit,
            "flags",
            "stationarity_rank_13_exactly_certified",
            default=False,
        )
        and _dig(
            g2_audit,
            "flags",
            "stationarity_nullity_38_exactly_certified",
            default=False,
        )
        and _dig(
            g2_audit,
            "flags",
            "stationarity_rank_upper_bound_13_exactly_certified",
            default=False,
        )
        and g2_counts.get("invariant_directions") == 44
        and g2_counts.get("real_parameters") == 51
        and g2_counts.get("real_field_dimension") == 486
        and g2_stationary.get("rank") == 13
        and g2_stationary.get("nullity") == 38
    )
    dedicated_g2_supersedes_pre_audit_scalar_contract_flag = bool(
        scalar_contract_pre_audit_g2_flag is False and g2_scoped_complete
    )
    spectrum = reports.get("g6_spectrum", {})
    spectrum_classification = spectrum.get("classification", {})
    complete_source_bound_spectrum = bool(
        spectrum.get("model_contract_id") == MODEL_CONTRACT_ID
        and spectrum.get("n_failed") == 0
        and spectrum_classification.get("complete_physical_scalar_spectrum") is True
        and spectrum_classification.get("source_bound_to_authoritative_vacuum")
        is True
        and spectrum_classification.get("all_physical_scalar_eigenstates_classified")
        is True
        and spectrum_classification.get("no_unexplained_zero_or_negative_modes")
        is True
    )
    authoritative_g3_g4_g5_g6_closed = bool(
        g3_closed and g4_closed and g5_closed and g6_closed
    )
    gauged = reports.get("gauged_g3", {})
    gauged_flags = gauged.get("flags", {})
    gauged_coverage = gauged.get("coverage", {})
    common = reports.get("gauged_g3_common_kernel", {})
    common_flags = common.get("flags", {})
    common_diagnostic = common.get("corrected_common_kernel_diagnostic", {})
    common_kernel = common_diagnostic.get("corrected_common_kernel", {})
    sos = reports.get("gauged_g3_sos_candidate", {})
    sos_flags = sos.get("flags", {})
    sos_coefficients = sos.get("coefficient_vector", {})
    sos_quotient = sos.get("symmetry_quotient", {})
    sos_pd = sos.get("exact_rank_certificate", {})
    sos_a_square = sos.get("exact_A_square_recoupling_certificate", {})
    sos_exact_bfb = sos.get("exact_SOS_BFB_stationarity_certificate", {})
    pd_rank = reports.get("gauged_g3_pd_rank", {})
    pd_flags = pd_rank.get("flags", {})
    pd_direct = pd_rank.get("direct_P_plus_Delta_certificate", {})
    pd_ranks = pd_rank.get("direct_exact_ranks", {})
    pd_core = pd_ranks.get("H_Phi_plus_K", {})
    pd_extension = pd_rank.get("exact_full_kernel_argument", {})
    a_square = reports.get("gauged_g3_a_square", {})
    a_square_flags = a_square.get("flags", {})
    a_square_certificate = a_square.get("certificate", {})
    sos_bfb = reports.get("gauged_g3_sos_bfb", {})
    sos_bfb_flags = sos_bfb.get("flags", {})
    kernel_bound = reports.get("gauged_g3_kernel_bound", {})
    kernel_bound_flags = kernel_bound.get("flags", {})
    replacement = reports.get("gauged_g3_replacement", {})
    replacement_flags = replacement.get("flags", {})
    su5_pd = reports.get("gauged_g3_su5_pd", {})
    su5_pd_scope = su5_pd.get("scope", {})
    su5_hsx = reports.get("gauged_g3_su5_hsx", {})
    su5_hsx_flags = su5_hsx.get("flag", {})
    su5_hsx_orbit = _dig(su5_hsx, "chiral_H_candidate", "exact_orbit", default={})
    su5_hsx_bfb = su5_hsx.get("BFB_certificate", {})
    su5_hsx_hessian = su5_hsx.get("live_full_gradient_and_quotient_Hessian", {})
    su5_hsx_global = su5_hsx.get("global_status", {})
    su5_hsx_exact_hessian = reports.get("gauged_g3_su5_hsx_exact_hessian", {})
    su5_hsx_exact_hessian_flags = su5_hsx_exact_hessian.get("flags", {})
    su5_equality = reports.get("gauged_g3_su5_equality", {})
    su5_equality_scope = su5_equality.get("scope", {})
    su5_equality_lemma = su5_equality.get("remaining_global_lemma", {})
    su5_equality_global = su5_equality.get(
        "Phi_global_signed_zero_theorem", {}
    )
    su5_phi_orbit = reports.get("gauged_g3_su5_phi_orbit", {})
    su5_phi_orbit_scope = su5_phi_orbit.get("scope", {})
    su5_phi_orbit_checks = su5_phi_orbit.get("checks", {})
    su5_phi_orbit_corrected = su5_phi_orbit.get("corrected_global_lemma", {})
    su5_phi_local = reports.get("gauged_g3_su5_phi_local_component", {})
    su5_phi_local_scope = su5_phi_local.get("scope", {})
    su5_phi_su3 = reports.get("gauged_g3_su5_phi_su3_slice", {})
    su5_phi_su3_scope = su5_phi_su3.get("scope", {})
    su5_phi_su3_checks = su5_phi_su3.get("checks", {})
    su5_gap = reports.get("gauged_g3_su5_gap", {})
    su5_gap_flags = su5_gap.get("flags", {})
    su5_gap_acceptance = su5_gap.get("final_acceptance_test", {})
    fixed_f_bound = reports.get("gauged_g3_su5_fixed_f_offkernel", {})
    fixed_f_bound_scope = fixed_f_bound.get("scope", {})
    fixed_f_bound_checks = fixed_f_bound.get("checks", {})
    max_negative_bound = reports.get(
        "gauged_g3_su5_max_negative_zero_residual", {}
    )
    max_negative_scope = max_negative_bound.get("scope", {})
    max_negative_checks = max_negative_bound.get("checks", {})
    max_negative_full_bound = reports.get(
        "gauged_g3_su5_max_negative_full_residual", {}
    )
    max_negative_full_scope = max_negative_full_bound.get("scope", {})
    max_negative_full_checks = max_negative_full_bound.get("checks", {})
    rank1_su3_bound = reports.get(
        "gauged_g3_su5_max_negative_rank1_su3_slice", {}
    )
    rank1_su3_scope = rank1_su3_bound.get("scope", {})
    rank1_su3_checks = rank1_su3_bound.get("checks", {})
    rank1_su4_stabilizer = reports.get("gauged_g3_rank1_su4_stabilizer", {})
    rank1_su4_intertwiners = reports.get(
        "gauged_g3_rank1_su4_phi210_intertwiners", {}
    )
    rank1_su4_intertwiner_scope = rank1_su4_intertwiners.get("scope", {})
    rank1_su4_aligned = reports.get(
        "gauged_g3_rank1_su4_aligned_carriers", {}
    )
    rank1_su4_quadratic = reports.get(
        "gauged_g3_rank1_su4_phi210_quadratic_basis", {}
    )
    rank1_su4_quadratic_scope = rank1_su4_quadratic.get("scope", {})
    rank1_su4_census = reports.get(
        "gauged_g3_rank1_su4_augmented_sos_census", {}
    )
    rank1_su4_census_scope = rank1_su4_census.get("scope", {})
    rank1_su4_cubic = reports.get(
        "gauged_g3_rank1_su4_augmented_sos_cubic_map", {}
    )
    rank1_su4_cubic_scope = rank1_su4_cubic.get("scope", {})
    rank1_su4_cubic_map = rank1_su4_cubic.get("cubic_coordinate_map", {})
    rank1_su4_quartic = reports.get(
        "gauged_g3_rank1_su4_augmented_sos_quartic_map", {}
    )
    rank1_su4_quartic_scope = rank1_su4_quartic.get("scope", {})
    rank1_su4_quartic_map = rank1_su4_quartic.get(
        "coefficient_map_certificate", {}
    )
    rank1_su4_psd_target = reports.get(
        "gauged_g3_rank1_su4_augmented_sos_psd_target", {}
    )
    rank1_su4_psd_target_scope = rank1_su4_psd_target.get("scope", {})
    rank1_su4_psd_routes = rank1_su4_psd_target.get(
        "standard_PSD_coordinate_routes", {}
    )
    rank1_su4_physical_target = rank1_su4_psd_target.get("physical_target", {})
    rank1_su4_full_target = rank1_su4_physical_target.get(
        "full_graded_chart", {}
    )
    rank1_su4_quartic_target = rank1_su4_physical_target.get("quartic", {})
    rank1_su4_corrected_publication = {
        "manifest": reports.get("gauged_g3_rank1_su4_corrected_manifest", {}),
        "theorem": reports.get("gauged_g3_rank1_su4_corrected_theorem", {}),
        "source": reports.get("gauged_g3_rank1_su4_corrected_source", {}),
        "verify": reports.get("gauged_g3_rank1_su4_corrected_verify", {}),
        "live": reports.get("gauged_g3_rank1_su4_corrected_live", {}),
        "overflow": reports.get("gauged_g3_rank1_su4_corrected_overflow", {}),
    }
    rank1_su4_corrected_exact = (
        corrected_rank1.corrected_fixed_endpoint_theorem_exact(
            rank1_su4_corrected_publication
        )
    )
    rank1_su4_corrected_view = (
        corrected_rank1.central_view(rank1_su4_corrected_publication)
        if rank1_su4_corrected_exact
        else {}
    )
    alternative_sos = reports.get("gauged_g3_alternative_global_sos", {})
    alternative_sos_flags = alternative_sos.get("flags", {})
    final_g3 = reports.get("final_g3", {})
    final_g3_classification = final_g3.get("classification", {})
    final_g3_eft = reports.get("final_g3_eft", {})
    if parallel_eft_g3_acceptance is None:
        parallel_eft_g3_acceptance = gate_ledger._parallel_eft_g3_acceptance(
            final_g3_eft
        )
    final_g4_eft = reports.get("final_g4_eft", {})
    if parallel_eft_g4_mathematical is None:
        parallel_eft_g4_mathematical = gate_ledger._parallel_eft_g4_mathematical(
            final_g4_eft
        )
    final_g5_eft = reports.get("final_g5_eft", {})
    if parallel_eft_g5_mathematical is None:
        parallel_eft_g5_mathematical = gate_ledger._parallel_eft_g5_mathematical(
            final_g5_eft
        )
    final_g6_eft = reports.get("final_g6_eft", {})
    if g6_sm_provenance is None:
        g6_sm_provenance = {}
    if g6_g7_parameterized_matching is None:
        g6_g7_parameterized_matching = {}
    if physical_sm_vacuum is None:
        physical_sm_vacuum = {}
    if physical_sm_heavy_vectors is None:
        physical_sm_heavy_vectors = {}
    if conditional_physical_sm_scalar_spectrum is None:
        conditional_physical_sm_scalar_spectrum = {}
    if parallel_eft_g6_spectrum is None:
        parallel_eft_g6_spectrum = gate_ledger._parallel_eft_g6_spectrum(
            final_g6_eft,
            gate_source_raw_sha256=gate_ledger._raw_file_sha256(
                ROOT / FINAL_G6_EFT_GATE_SOURCE
            ),
            provenance_audit=g6_sm_provenance,
            parameterized_matching=g6_g7_parameterized_matching,
        )
    corrected_common_kernel_honestly_bound = bool(
        common.get("model_contract_id") == MODEL_CONTRACT_ID
        and common.get("n_failed") == 0
        and common.get("overall_state") == "OPEN"
        and common_flags.get("legacy_common_kernel_dimension_135_invalidated")
        is True
        and common_flags.get("exact_H6_radial_flat_direction_refuted") is True
        and common_kernel.get("rank") == 448
        and common_kernel.get("nullity") == 0
        and common_diagnostic.get("proof_grade") is False
        and common_diagnostic.get("certified_PSD_feasibility") is False
        and common_diagnostic.get("certified_no_go") is False
    )
    a_square_exactly_scoped = bool(
        a_square.get("status") == "EXACT_A_SQUARE_RECOUPLING_CERTIFIED"
        and a_square.get("overall_state") == "CLOSED_SUBPROBLEM"
        and a_square.get("n_failed") == 0
        and a_square_certificate.get("source_binding_exact") is True
        and a_square_certificate.get("proof_grade") is True
        and a_square_certificate.get("unique_weights")
        == ["40", "72", "28", "-8", "-12", "12"]
        and a_square_flags.get("A_square_recoupling_exactly_source_bound") is True
        and a_square_flags.get("complete_potential_BFB_exactly_certified") is False
        and a_square_flags.get("full_Hessian_exactly_source_bound") is False
        and a_square_flags.get("strict_local_minimum_certified") is False
        and a_square_flags.get("G3_closed") is False
    )
    sos_bfb_exactly_scoped = bool(
        sos_bfb.get("status")
        == "EXACT_COMPLETE_POTENTIAL_BFB_AND_SELECTED_STATIONARITY_CERTIFIED"
        and sos_bfb.get("overall_state") == "CLOSED_SUBPROBLEM"
        and sos_bfb.get("model_contract_id") == MODEL_CONTRACT_ID
        and sos_bfb.get("n_failed") == 0
        and sos_bfb_flags.get(
            "complete_27_parameter_SOS_identity_exactly_source_bound"
        )
        is True
        and sos_bfb_flags.get("complete_potential_BFB_exactly_certified") is True
        and sos_bfb_flags.get("selected_vacuum_stationarity_exactly_certified")
        is True
        and sos_bfb_flags.get("selected_vacuum_global_minimum_certified") is False
        and sos_bfb_flags.get("selected_vacuum_unique_modulo_symmetry") is False
        and sos_bfb_flags.get("full_Hessian_exactly_source_bound") is False
        and sos_bfb_flags.get("strict_local_minimum_certified") is False
        and sos_bfb_flags.get("G3_closed") is False
    )
    pd_rank_direct_exact_and_fail_closed = bool(
        pd_rank.get("status")
        == "DIRECT_EXACT_TRANSVERSE_HESSIAN_PASS__SOS_AND_GLOBAL_EXTREMA_EXTERNAL"
        and pd_rank.get("overall_state") == "OPEN"
        and pd_rank.get("n_failed") == 0
        and pd_direct.get("source_binding_exact") is True
        and pd_direct.get("proof_grade") is True
        and pd_core == {"rank": 429, "nullity": 33, "PSD": True}
        and pd_extension.get("exact_full_Hessian_rank") == 448
        and pd_extension.get("remaining_kernel_dimension") == 38
        and pd_extension.get("source_binding_exact") is True
        and pd_extension.get("proof_grade") is True
        and pd_flags.get("conditional_exact_LDL_on_reconstructed_matrix") is False
        and pd_flags.get("direct_exact_source_binding") is True
        and pd_flags.get("proof_grade_P_plus_Delta_PSD") is True
        and pd_flags.get("proof_grade_full_rank_448") is True
        and pd_flags.get("strict_transverse_Hessian_positive_certified") is True
        and pd_flags.get("strict_local_minimum_certified_here") is False
        and pd_flags.get("global_minimum_certified") is False
        and pd_flags.get("global_uniqueness_certified") is False
        and pd_flags.get("G3_closed") is False
        and pd_flags.get("whole_model_validated") is False
        and pd_flags.get("whole_model_excluded") is False
    )
    sos_candidate_exact_local_and_globally_fail_closed = bool(
        sos.get("status")
        == "EXACT_BFB_STATIONARY_STRICT_LOCAL_MINIMUM__GLOBAL_COUNTEREXAMPLE"
        and sos.get("overall_state") == "OPEN"
        and sos.get("model_contract_id") == MODEL_CONTRACT_ID
        and sos.get("n_failed") == 0
        and sos_coefficients.get("nonzero_count") == 27
        and sos_coefficients.get("maximum_absolute_coefficient") == 9.125
        and _dig(
            sos_coefficients,
            "symbolic_nonzero",
            "lambda::O48_B01_Phi_self_quartics",
        )
        == "-21/200"
        and sos_quotient.get("SO10_plus_U1X_plus_global_PQ_rank") == 38
        and sos_quotient.get("massive_transverse_dimension") == 448
        and sos_flags.get("exact_sparse_51_parameter_candidate_constructed") is True
        and sos_flags.get("candidate_inside_4pi_box") is True
        and sos_flags.get(
            "positive_J0_normalization_is_without_loss_of_generality"
        )
        is False
        and sos_flags.get("manifest_BFB_decomposition_candidate_constructed") is True
        and sos_flags.get("A_square_recoupling_exactly_source_bound") is True
        and sos_flags.get("complete_potential_BFB_exactly_certified") is True
        and sos_flags.get(
            "selected_vacuum_stationarity_exactly_compiler_certified"
        )
        is True
        and sos_flags.get("selected_vacuum_global_minimum_certified") is False
        and sos_flags.get("selected_vacuum_global_minimum_disproved") is True
        and sos_flags.get("selected_vacuum_unique_modulo_symmetry") is False
        and sos_flags.get("exact_lower_energy_field_witness_certified") is True
        and sos_flags.get("constructive_candidate_rejected_for_G3") is True
        and sos_flags.get("P_plus_Delta_Qsqrt2_component_LDL_conditional") is False
        and sos_flags.get("P_plus_Delta_source_binding_exactly_certified") is True
        and sos_flags.get("full_448_kernel_count_conditional") is False
        and sos_flags.get("full_448_kernel_count_exact") is True
        and sos_flags.get("full_448_PSD_feasibility_certified") is True
        and sos_flags.get("strict_local_minimum_certified") is True
        and sos_flags.get("G3_closed") is False
        and sos_flags.get("whole_model_validated") is False
        and sos_flags.get("whole_model_excluded") is False
        and sos_pd.get("status") == pd_rank.get("status")
        and _dig(
            sos_pd,
            "direct_exact_ranks",
            "H_Phi_plus_K",
            default={},
        )
        == pd_core
        and sos_exact_bfb.get("status") == sos_bfb.get("status")
        and sos_a_square.get("status") == a_square.get("status")
        and _dig(
            sos_a_square,
            "certificate",
            "unique_weights",
            default=[],
        )
        == a_square_certificate.get("unique_weights")
    )
    fixed_p_branch_exactly_excluded = bool(
        kernel_bound.get("n_failed") == 0
        and kernel_bound_flags.get("fixed_P_strict_local_global_no_go_exact")
        is True
        and kernel_bound_flags.get("fixed_P_branch_closed_negative") is True
        and kernel_bound_flags.get("G3_closed") is False
        and kernel_bound_flags.get("whole_model_excluded") is False
    )
    lower_replacement_rejected_for_wrong_symmetry = bool(
        replacement.get("n_failed") == 0
        and replacement_flags.get("replacement_full_stationarity_exact") is True
        and replacement_flags.get("replacement_symmetry_orbit_rank_exact") is True
        and replacement_flags.get("replacement_target_gauge_symmetry_correct")
        is False
        and replacement_flags.get("replacement_strict_local_minimum_proof_grade")
        is False
        and replacement_flags.get("replacement_global_minimum_established")
        is False
        and replacement_flags.get("G3_closed") is False
    )
    su5_delta_pd_exact_global_frontier = bool(
        su5_pd.get("n_failed") == 0
        and su5_pd.get("status")
        == "EXACT_SU5_DELTA_PD_GLOBAL_SOS_CANDIDATE_CERTIFIED"
        and su5_pd_scope.get("Phi_Sigma_global_minimum_exact") is True
        and su5_pd_scope.get("Phi_Sigma_stationarity_exact") is True
        and su5_pd_scope.get("SO10_to_SM_stabilizer_dimension_exact") is True
        and su5_pd_scope.get("Phi_Sigma_Hessian_rank_429_nullity_33_exact") is True
        and su5_pd_scope.get("Phi_Sigma_quotient_strictly_positive_exact") is True
        and su5_pd_scope.get("Phi_Sigma_equality_set_locally_one_orbit") is True
        and su5_pd_scope.get("full_486_field_stationarity") is False
        and su5_pd_scope.get("global_orbit_uniqueness") is False
        and su5_pd_scope.get("G3_closed") is False
    )
    su5_delta_hsx_honest_frontier = bool(
        su5_hsx.get("n_failed") == 0
        and su5_hsx.get("status")
        == "EXACT_REAL_H_NO_GO__CHIRAL_H_STRICT_LOCAL_CANDIDATE__GLOBAL_GAP_OPEN"
        and su5_hsx_flags.get("real_H_e6_extension_exactly_excluded") is True
        and su5_hsx_flags.get("chiral_H_exact_stationary_candidate_constructed")
        is True
        and su5_hsx_flags.get("full_486_gradient_zero_live") is True
        and su5_hsx_flags.get("full_quartic_BFB_certified") is True
        and su5_hsx_flags.get("full_global_minimum_certified") is False
        and su5_hsx_flags.get("G3_closed") is False
        and su5_hsx_orbit.get("SO10_rank") == 36
        and su5_hsx_orbit.get("SO10_plus_U1X_rank") == 37
        and su5_hsx_orbit.get("SO10_plus_U1X_plus_PQ_rank") == 38
        and su5_hsx_orbit.get("physical_quotient_dimension") == 448
        and su5_hsx_bfb.get("homogeneous_quartic_BFB_certified") is True
        and su5_hsx_bfb.get("finite_field_global_gap_certified") is False
        and su5_hsx_hessian.get("proof_grade") is False
        and su5_hsx_hessian.get("transverse_dimension") == 448
        and su5_hsx_hessian.get("negative_transverse_eigenvalues_below_minus_1e_minus_9")
        == 0
        and su5_hsx_hessian.get("zero_transverse_eigenvalues_at_1e_minus_9") == 0
        and su5_hsx_global.get("global_equality_orbits_classified") is False
    )
    hsx_exact_hessian_closed = bool(
        su5_hsx_exact_hessian.get("status")
        == "EXACT_FULL_HESSIAN_RANK_448_NULLITY_38_CERTIFIED"
        and su5_hsx_exact_hessian.get("overall_state")
        == "CLOSED_FULL_LOCAL_HESSIAN_SUBPROBLEM"
        and su5_hsx_exact_hessian_flags.get("exact_rank_448") is True
        and su5_hsx_exact_hessian_flags.get("exact_nullity_38") is True
        and su5_hsx_exact_hessian_flags.get("exact_PSD") is True
        and su5_hsx_exact_hessian_flags.get("strict_quotient") is True
        and su5_hsx_exact_hessian_flags.get("proof_grade") is True
        and su5_hsx_exact_hessian_flags.get("source_binding") is True
        and su5_hsx_exact_hessian.get("G3_closed") is False
    )
    hsx_exact_hessian_open = bool(
        su5_hsx_exact_hessian.get("status")
        == "EXACT_HESSIAN_CERTIFICATE_INCOMPLETE"
        and su5_hsx_exact_hessian.get("overall_state")
        == "G3_EXACT_LOCAL_TEST_OPEN"
        and su5_hsx_exact_hessian_flags.get("proof_grade") is False
        and su5_hsx_exact_hessian.get("G3_closed") is False
    )
    su5_hsx_exact_hessian_audit_fail_closed = bool(
        su5_hsx_exact_hessian
        and su5_hsx_exact_hessian.get("model_contract_id")
        == MODEL_CONTRACT_ID
        and su5_hsx_exact_hessian.get("n_failed", 0) == 0
        and (hsx_exact_hessian_closed or hsx_exact_hessian_open)
    )
    su5_equality_honestly_reduced = bool(
        su5_equality.get("n_failed") == 0
        and su5_equality.get("status")
        == "EXACT_GLOBAL_EQUALITY_CLASSIFICATION__SIGNED_PHI_THEOREM_CLOSED__G3_OPEN"
        and su5_equality.get("overall_state") == "GLOBAL_EQUALITY_ORBITS_CLOSED"
        and su5_equality_scope.get("fixed_F_Sigma_global_equality_classified")
        is True
        and su5_equality_scope.get(
            "fixed_Delta_diagonal_Phi_global_equality_classified"
        )
        is True
        and su5_equality_scope.get(
            "fixed_Delta_two_tau_plus_representatives_equivalent"
        )
        is True
        and su5_equality_scope.get(
            "literal_single_Phi_orbit_statement_refuted"
        )
        is True
        and su5_equality_scope.get("minus_F_mixed_branch_excluded_exact") is True
        and su5_equality_scope.get("corrected_signed_Phi_orbit_theorem_open")
        is False
        and su5_equality_scope.get("corrected_signed_Phi_orbit_theorem_proved")
        is True
        and su5_equality_scope.get(
            "complete_SU3_fixed_Phi_slice_classified_exactly"
        )
        is True
        and su5_equality_scope.get("global_equality_orbit_classification_complete")
        is True
        and su5_equality_scope.get("quantitative_beta_global_coercivity_proved")
        is False
        and su5_equality_scope.get("G3_closed") is False
        and su5_equality_lemma.get("proved") is True
        and su5_equality_lemma.get("literal_single_orbit_version_refuted") is True
        and su5_equality_lemma.get("corrected_signed_two_orbit_version") is True
        and su5_equality_lemma.get("complete_SU3_fixed_slice_classified_exactly")
        is True
        and su5_equality_lemma.get("SU3_fixed_slice_real_dimension") == 16
        and su5_equality_lemma.get("source_bound_certificate_available") is True
        and su5_equality_lemma.get("source_bound_partial_certificate_available")
        is True
        and su5_equality_lemma.get("numerical_search_is_not_a_substitute") is True
        and su5_equality_lemma.get("quantitative_orbit_distance_bound_proved")
        is False
        and su5_equality_global.get("frozen_source_sha256")
        == "17038c6fb82ba565a16228f5f5c03026f0ab8e3ad7959792498c2785b9653066"
        and su5_equality_global.get("core_sha256")
        == "db493a74303a57862f09c2a92118ea3d66b8b12ecbaea9162155d4ab3baafecc"
    )
    su5_phi_orbit_honestly_refuted_and_open = bool(
        su5_phi_orbit.get("n_failed") == 0
        and su5_phi_orbit.get("status")
        == "LITERAL_SINGLE_ORBIT_LEMMA_REFUTED__SIGNED_GLOBAL_LEMMA_OPEN"
        and su5_phi_orbit.get("overall_state")
        == "SHARP_COUNTEREXAMPLE_AND_REDUCTION"
        and su5_phi_orbit_checks.get("literal_single_orbit_lemma_is_refuted")
        is True
        and su5_phi_orbit_checks.get("corrected_signed_global_lemma_not_overclaimed")
        is True
        and su5_phi_orbit_scope.get("literal_plus_orbit_only_statement_refuted")
        is True
        and su5_phi_orbit_scope.get("complete_SU4_invariant_slice_classified")
        is True
        and su5_phi_orbit_scope.get("all_arbitrary_real_four_forms_classified")
        is False
        and su5_phi_orbit_scope.get("corrected_signed_two_orbit_theorem_proved")
        is False
        and su5_phi_orbit_scope.get(
            "PD_global_equality_orbit_classification_complete"
        )
        is False
        and su5_phi_orbit_scope.get("G3_closed") is False
        and su5_phi_orbit_scope.get("whole_model_excluded") is False
        and su5_phi_orbit_corrected.get("proved") is False
    )
    su5_phi_local_components_exactly_closed = bool(
        su5_phi_local.get("n_failed") == 0
        and su5_phi_local.get("status")
        == "EXACT_LOCAL_COMPONENT_THEOREM_CLOSED__DISTANT_COMPONENTS_OPEN"
        and su5_phi_local.get("overall_state")
        == "LOCAL_COMPONENT_THEOREM_CLOSED"
        and su5_phi_local_scope.get("plus_F_local_component_classified") is True
        and su5_phi_local_scope.get("minus_F_local_component_classified") is True
        and su5_phi_local_scope.get("signed_orbit_locally_isolated") is True
        and su5_phi_local_scope.get("explicit_neighborhood_radius_available")
        is False
        and su5_phi_local_scope.get("disconnected_distant_components_excluded")
        is False
        and su5_phi_local_scope.get(
            "corrected_signed_global_orbit_theorem_proved"
        )
        is False
        and su5_phi_local_scope.get(
            "PD_global_equality_orbit_classification_complete"
        )
        is False
        and su5_phi_local_scope.get("G3_closed") is False
        and su5_phi_local_scope.get("whole_model_excluded") is False
    )
    su5_phi_su3_slice_exactly_closed = bool(
        su5_phi_su3.get("n_failed") == 0
        and su5_phi_su3.get("status")
        == "EXACT_COMPLETE_SU3_FIXED_SLICE_CLASSIFIED__GENERIC_GLOBAL_OPEN"
        and su5_phi_su3.get("overall_state") == "SU3_FIXED_SLICE_CLOSED"
        and su5_phi_su3_checks.get("displayed_space_is_complete_SU3_fixed_space")
        is True
        and su5_phi_su3_checks.get("restricted_projector_rowspace_reduced_exactly")
        is True
        and su5_phi_su3_checks.get(
            "eight_nondiagonal_directions_have_real_SOS_obstruction"
        )
        is True
        and su5_phi_su3_checks.get("complete_SU3_fixed_slice_is_signed_Kahler_orbit")
        is True
        and su5_phi_su3_scope.get(
            "complete_16_real_dimensional_SU3_fixed_space_classified"
        )
        is True
        and su5_phi_su3_scope.get(
            "all_nonzero_slice_solutions_are_signed_Kahler_squares"
        )
        is True
        and su5_phi_su3_scope.get("all_arbitrary_real_four_forms_classified")
        is False
        and su5_phi_su3_scope.get("disconnected_distant_components_excluded")
        is False
        and su5_phi_su3_scope.get("corrected_signed_global_orbit_theorem_proved")
        is False
        and su5_phi_su3_scope.get("G3_closed") is False
        and su5_phi_su3_scope.get("whole_model_excluded") is False
    )
    su5_chiral_gap_honestly_reduced = bool(
        su5_gap.get("n_failed") == 0
        and su5_gap.get("status")
        == "GLOBAL_GAP_REDUCED_TO_QUANTITATIVE_COERCIVITY"
        and su5_gap.get("overall_state") == "FINAL_G3_TEST_OPEN"
        and su5_gap_flags.get("lower_witness_found") is False
        and su5_gap_flags.get("conditional_small_positive_beta_route_exists")
        is True
        and su5_gap_flags.get("beta_1_over_20_global_minimum_certified") is False
        and su5_gap_flags.get("PD_equality_orbits_classified") is True
        and su5_gap_flags.get("global_equality_orbits_classified") is False
        and su5_gap_flags.get("G3_closed") is False
        and su5_gap_acceptance.get("currently_passes") is False
    )
    su5_fixed_f_full_gap_closed = bool(
        fixed_f_bound.get("n_failed") == 0
        and fixed_f_bound.get("status")
        == "EXACT_FIXED_F_FULL_OFFKERNEL_BETA_GAP_CERTIFIED"
        and fixed_f_bound.get("overall_state")
        == "CLOSED_FIXED_F_GLOBAL_SUBPROBLEM"
        and fixed_f_bound_checks.get(
            "mixed_offkernel_gap_at_least_6_over_5_exact"
        )
        is True
        and fixed_f_bound_checks.get("pure_hplus_current_error_bound_exact")
        is True
        and fixed_f_bound_checks.get("kernel_chirality_cross_zero_exact") is True
        and fixed_f_bound_checks.get("cross_block_bound_exact") is True
        and fixed_f_bound_checks.get("rational_inside_outside_patch_positive")
        is True
        and fixed_f_bound_checks.get("full_fixed_F_equality_orbit_exact") is True
        and fixed_f_bound_scope.get("Phi_fixed_to_F") is True
        and fixed_f_bound_scope.get("H_arbitrary") is True
        and fixed_f_bound_scope.get("Sigma_arbitrary") is True
        and fixed_f_bound_scope.get("beta_equals_1_over_20") is True
        and fixed_f_bound_scope.get(
            "global_gap_nonnegative_on_full_fixed_F_stratum"
        )
        is True
        and fixed_f_bound_scope.get("equality_is_selected_SU5_flag_orbit") is True
        and fixed_f_bound_scope.get("arbitrary_Phi_proved") is False
        and fixed_f_bound_scope.get("G3_closed") is False
    )
    su5_max_negative_all_zero_route_excluded = bool(
        max_negative_bound.get("n_failed") == 0
        and max_negative_bound.get("status")
        == "EXACT_PURE_DELTA_MAX_NEGATIVE_MIXED_ZERO_ROUTE_EXCLUDED"
        and max_negative_bound.get("overall_state")
        == "CLOSED_PURE_DELTA_MAX_NEGATIVE_MIXED_ZERO_STRATUM__ARBITRARY_PHI_OPEN"
        and max_negative_bound.get("model_contract_id")
        == MODEL_CONTRACT_ID
        and max_negative_checks.get("exact_rank_168_nullity_42") is True
        and max_negative_checks.get("kernel_splits_35_plus_7_exactly") is True
        and max_negative_checks.get("live_HSX_and_PD_coefficients_bound_exactly")
        is True
        and max_negative_checks.get(
            "N_and_C00_C11_contraction_identities_computed_exactly"
        )
        is True
        and max_negative_checks.get(
            "Phi_radial_plus_I54_lower_bound_1_over_141"
        )
        is True
        and max_negative_checks.get("worst_radial_current_minimum_exact") is True
        and max_negative_checks.get("strict_positive_stratum_margin_exact") is True
        and max_negative_checks.get(
            "u_zero_and_v_zero_radial_boundaries_closed_exactly"
        )
        is True
        and _dig(max_negative_bound, "exact_stratum_gap", "strict_margin")
        == "7859/140295000"
        and max_negative_scope.get(
            "strongest_all_zero_max_negative_route_excluded"
        )
        is True
        and max_negative_scope.get(
            "strongest_pure_Delta_mixed_zero_max_negative_route_excluded"
        )
        is True
        and max_negative_scope.get(
            "normalized_affine_stratum_requires_u_gt_0_v_gt_0"
        )
        is True
        and max_negative_scope.get(
            "u_zero_and_v_zero_boundaries_closed_separately"
        )
        is True
        and max_negative_scope.get("nonzero_residual_cancellations_excluded")
        is False
        and max_negative_scope.get("arbitrary_Phi_global_gap_proved") is False
        and max_negative_scope.get("G3_closed") is False
    )
    su5_max_negative_full_residual_pure_delta_closed = bool(
        max_negative_full_bound.get("n_failed") == 0
        and max_negative_full_bound.get("status")
        == "EXACT_MAX_NEGATIVE_FULL_RESIDUAL_PURE_DELTA_BOUND_CERTIFIED"
        and max_negative_full_bound.get("overall_state")
        == "CLOSED_MAX_NEGATIVE_PURE_DELTA_ARBITRARY_PHI_SUBPROBLEM"
        and max_negative_full_bound.get("model_contract_id")
        == MODEL_CONTRACT_ID
        and max_negative_full_scope.get("Sigma_on_pure_Delta_orbit") is True
        and max_negative_full_scope.get("Phi_arbitrary_real_210") is True
        and max_negative_full_scope.get("nonzero_Phi_Sigma_residuals_covered")
        is True
        and max_negative_full_scope.get("nonzero_chiral_Phi_H_residual_covered")
        is True
        and max_negative_full_scope.get("u_v_all_nonnegative") is True
        and max_negative_full_scope.get("restricted_gap_global_minimum")
        == "1/5000"
        and max_negative_full_scope.get("arbitrary_Sigma_orientation_proved")
        is False
        and max_negative_full_scope.get("G3_closed") is False
        and all(
            max_negative_full_checks.get(name) is True
            for name in (
                "live_restricted_residual_normalizations_exact",
                "single_4125_covariant_Cauchy_bound_exact",
                "anchor_quadratic_has_exact_positive_spectral_floor",
                "anchor_lower_bound_strictly_exceeds_1_over_50",
                "piecewise_u_v_completion_covers_nonnegative_quadrant",
                "exact_1_over_5000_saturation_exhibited",
                "arbitrary_real_Phi_covered",
                "mixed_and_chiral_residuals_not_assumed_zero",
                "arbitrary_Sigma_orientation_not_overclaimed",
                "G3_not_overclaimed",
            )
        )
    )
    su5_max_negative_rank1_su3_four_dimensional_slice_closed = bool(
        rank1_su3_bound.get("n_failed") == 0
        and rank1_su3_bound.get("failed_checks") == []
        and rank1_su3_bound.get("status")
        == "EXACT_RANK1_SU3_DANGEROUS_SLICE_BOUND_CERTIFIED"
        and rank1_su3_bound.get("overall_state")
        == "CLOSED_RANK1_SU3_SLICE__ARBITRARY_RANK1_PHI_OPEN"
        and rank1_su3_bound.get("model_contract_id") == MODEL_CONTRACT_ID
        and rank1_su3_scope.get("H_fixed_to_h_minus") is True
        and rank1_su3_scope.get(
            "Sigma_fixed_to_normalized_explicit_decomposable_pure_spinor"
        )
        is True
        and rank1_su3_scope.get(
            "Phi_restricted_to_four_real_SU3_fixed_variables"
        )
        is True
        and rank1_su3_scope.get("Phi_slice_real_dimension") == 4
        and rank1_su3_scope.get("full_SU3_fixed_space_real_dimension") == 16
        and rank1_su3_scope.get("full_SU3_fixed_space_proved") is False
        and rank1_su3_scope.get("u_v_arbitrary_nonnegative") is True
        and rank1_su3_scope.get("arbitrary_real_Phi") is False
        and rank1_su3_scope.get("arbitrary_max_negative_Sigma") is False
        and rank1_su3_scope.get("G3_closed") is False
        and rank1_su3_scope.get("whole_model_excluded") is False
        and all(
            rank1_su3_checks.get(name) is True
            for name in (
                "rank1_live_residual_source_exact",
                "explicit_endpoint_current_and_self_projectors_exactly",
                "slice_basis_Gram_exact",
                "rank1_common_affine_kernel_rank160_nullity50_exact",
                "angular_projector_Gram_symmetric_exact",
                "angular_projector_int64_overflow_preflight_exact",
                "anchor_polynomial_reconstructed_exactly",
                "rational_SOS_polynomial_identity_exact",
                "rational_SOS_Gram_positive_definite_exact",
                "anchor_at_least_3_over_200_exact",
                "radial_patch_global_minimum_1_over_5000_exact",
                "attaining_slice_witness_evaluated_from_live_arrays_exact",
            )
        )
        and rank1_su3_checks.get("arbitrary_rank1_Phi_proved") is False
        and rank1_su3_checks.get("arbitrary_Sigma35_proved") is False
        and rank1_su3_checks.get("G3_closed") is False
        and _dig(rank1_su3_bound, "SOS", "strict_anchor_lower_bound") == "3/200"
        and _dig(rank1_su3_bound, "radial_patch", "restricted_global_minimum")
        == "1/5000"
    )
    rank1_su4_stabilizer_infrastructure_exact = (
        gate_ledger._rank1_su4_stabilizer_infrastructure_exact(
            rank1_su4_stabilizer
        )
    )
    rank1_su4_phi210_intertwiners_exact = (
        gate_ledger._rank1_su4_phi210_intertwiners_exact(
            rank1_su4_intertwiners,
            rank1_su4_stabilizer,
        )
    )
    rank1_su4_aligned_carriers_exact = (
        gate_ledger._rank1_su4_aligned_carriers_exact(
            rank1_su4_aligned,
            rank1_su4_intertwiners,
            rank1_su4_stabilizer,
        )
    )
    rank1_su4_phi210_quadratic_basis_exact = (
        gate_ledger._rank1_su4_phi210_quadratic_basis_exact(
            rank1_su4_quadratic,
            rank1_su4_stabilizer,
            rank1_su4_intertwiners,
            rank1_su4_aligned,
        )
    )
    rank1_su4_augmented_sos_census_exact = (
        gate_ledger._rank1_su4_augmented_sos_census_exact(
            rank1_su4_census,
            rank1_su4_stabilizer,
            rank1_su4_intertwiners,
            rank1_su4_aligned,
            rank1_su4_quadratic,
        )
    )
    rank1_su4_augmented_sos_cubic_map_exact = (
        gate_ledger._rank1_su4_augmented_sos_cubic_map_exact(
            rank1_su4_cubic,
            rank1_su4_stabilizer,
            rank1_su4_intertwiners,
            rank1_su4_aligned,
            rank1_su4_quadratic,
            rank1_su4_census,
        )
    )
    rank1_su4_augmented_sos_quartic_map_exact = (
        rank1_su4_augmented_sos_census_exact
        and rank1_su4_augmented_sos_cubic_map_exact
        and gate_ledger._rank1_su4_augmented_sos_quartic_map_exact(
            rank1_su4_quartic,
            rank1_su4_census,
            rank1_su4_cubic,
        )
    )
    rank1_su4_legacy_psd_routes_and_stale_payload_well_formed = (
        rank1_su4_augmented_sos_quartic_map_exact
        and gate_ledger._rank1_su4_augmented_sos_psd_routes_and_stale_payload_well_formed(
            rank1_su4_psd_target,
            rank1_su4_census,
            rank1_su4_cubic,
            rank1_su4_quartic,
        )
    )
    alternative_global_sos_honestly_open = bool(
        alternative_sos.get("n_failed") == 0
        and alternative_sos.get("status")
        == "ALTERNATIVE_GLOBAL_SOS_AUDIT_COMPLETE__NO_CERTIFIED_REPLACEMENT"
        and alternative_sos.get("overall_state") == "G3_GLOBAL_ALTERNATIVE_OPEN"
        and alternative_sos_flags.get(
            "all_vanishing_45_current_Gram_completion_excluded"
        )
        is True
        and alternative_sos_flags.get(
            "all_vanishing_affine_SOS_completion_excluded"
        )
        is True
        and alternative_sos_flags.get(
            "all_vanishing_unique_chiral_quartic_completion_excluded"
        )
        is True
        and alternative_sos_flags.get(
            "nonvanishing_residual_gradient_cancellation_excluded"
        )
        is False
        and alternative_sos_flags.get("different_vacuum_orbit_excluded") is False
        and alternative_sos_flags.get("globally_certifiable_alternative_found")
        is False
        and alternative_sos_flags.get("G3_closed") is False
        and alternative_sos_flags.get("whole_model_excluded") is False
    )
    final_g3_honestly_open = bool(
        final_g3.get("n_failed") == 0
        and final_g3.get("status") == "FINAL_G3_ACCEPTANCE_TEST_EXECUTED"
        and final_g3.get("overall_state") == "OPEN"
        and final_g3_classification.get("mathematical_G3_closed") is False
        and final_g3_classification.get("release_G3_verified") is False
        and final_g3_classification.get("whole_model_excluded") is False
        and final_g3_classification.get("theory_still_viable") is True
        and final_g3_classification.get("G3_closed") is False
    )
    g3_frontier_honestly_fail_closed = bool(
        a_square_exactly_scoped
        and sos_bfb_exactly_scoped
        and pd_rank_direct_exact_and_fail_closed
        and sos_candidate_exact_local_and_globally_fail_closed
        and fixed_p_branch_exactly_excluded
        and lower_replacement_rejected_for_wrong_symmetry
        and su5_delta_pd_exact_global_frontier
        and su5_delta_hsx_honest_frontier
        and su5_hsx_exact_hessian_audit_fail_closed
        and su5_equality_honestly_reduced
        and su5_phi_orbit_honestly_refuted_and_open
        and su5_phi_local_components_exactly_closed
        and su5_phi_su3_slice_exactly_closed
        and su5_chiral_gap_honestly_reduced
        and su5_fixed_f_full_gap_closed
        and su5_max_negative_all_zero_route_excluded
        and su5_max_negative_full_residual_pure_delta_closed
        and su5_max_negative_rank1_su3_four_dimensional_slice_closed
        and rank1_su4_stabilizer_infrastructure_exact
        and rank1_su4_phi210_intertwiners_exact
        and rank1_su4_aligned_carriers_exact
        and rank1_su4_phi210_quadratic_basis_exact
        and rank1_su4_augmented_sos_census_exact
        and rank1_su4_augmented_sos_cubic_map_exact
        and rank1_su4_augmented_sos_quartic_map_exact
        and rank1_su4_legacy_psd_routes_and_stale_payload_well_formed
        and rank1_su4_corrected_exact
        and alternative_global_sos_honestly_open
        and final_g3_honestly_open
    )
    gauged_g3_contract_bound = bool(
        gauged.get("model_contract_id") == MODEL_CONTRACT_ID
        and gauged.get("authoritative_for_manuscript_G3_formulation") is True
        and gauged.get("n_failed") == 0
        and gauged_coverage.get("invariant_directions") == 44
        and gauged_coverage.get("real_parameters") == 51
        and gauged_coverage.get("real_field_dimension") == 486
        and gauged_coverage.get("gauge_quotient_dimension_including_axion") == 449
        and gauged_coverage.get("massive_transverse_quotient_dimension") == 448
        and gauged_flags.get(
            "gauge_quotient_dimension_449_including_axion_certified"
        ) is True
        and gauged_flags.get(
            "massive_transverse_quotient_dimension_448_certified"
        ) is True
        and gauged_flags.get("stationarity_nullity_38_exactly_certified") is True
        and gauged_flags.get("constructive_candidate_exact_rank448_certificate")
        is True
        and gauged_flags.get("constructive_candidate_direct_exact_source_binding")
        is True
        and gauged_flags.get("G3_fixed_vacuum_strict_minimum_certified") is True
        and gauged_flags.get("G3_fixed_vacuum_PSD_feasible_certified") is True
        and gauged_flags.get("G3_selected_vacuum_global_no_go_certified") is True
        and gauged_flags.get("exact_lower_energy_field_witness_certified")
        is True
        and gauged_flags.get("constructive_candidate_rejected_for_G3") is True
        and gauged_flags.get("complete_potential_BFB") is True
        and corrected_common_kernel_honestly_bound
        and g3_frontier_honestly_fail_closed
    )
    exact_stationarity_rank = bool(
        gauged_g3_contract_bound
        and gauged_flags.get("stationarity_rank_13_exactly_certified", False)
    )
    model_wide_no_go = bool(
        gauged_g3_contract_bound
        and exact_stationarity_rank
        and gauged_flags.get("model_wide_no_go_certified", False)
        and gauged_flags.get("whole_model_excluded", False)
        and gauged_flags.get("proof_grade_model_wide_no_go", False)
    )
    stable_quotient = bool(
        gauged_g3_contract_bound
        and exact_stationarity_rank
        and gauged_flags.get("G3_fixed_vacuum_strict_minimum_certified", False)
    )
    bfb = bool(
        gauged_g3_contract_bound
        and exact_stationarity_rank
        and gauged_flags.get("complete_potential_BFB", False)
    )
    global_minimum = bool(
        gauged_g3_contract_bound
        and exact_stationarity_rank
        and gauged_flags.get("global_competing_extrema_exhausted", False)
    )
    physical_sm_overlay_bound = bool(
        physical_sm_vacuum.get("source_bound") is True
        and physical_sm_vacuum.get("physical_SM_target_exactly_constructed")
        is True
        and physical_sm_vacuum.get("standard_SU3C_x_U1em_stabilizer_proved")
        is True
        and physical_sm_vacuum.get(
            "reconstructed_stationary_transverse_PSD_witness_available"
        )
        is True
        and physical_sm_vacuum.get(
            "direct_source_algebra_stationary_PSD_witness_available"
        )
        is False
        and physical_sm_vacuum.get("source_bound_global_equality_orbit_proved")
        is False
        and physical_sm_vacuum.get("old_selected_EFT_stabilizer_label_superseded")
        is True
        and all(
            physical_sm_vacuum.get(f"physical_SM_{gate}_closed") is False
            for gate in ("G3", "G4", "G5", "G6", "G7")
        )
    )
    if physical_sm_source_equality is None:
        physical_sm_source_equality = {}
    physical_sm_radial_equality_bound = bool(
        physical_sm_source_equality.get("source_bound") is True
        and physical_sm_source_equality.get(
            "radial_stationary_equality_classified_exactly"
        )
        is True
        and physical_sm_source_equality.get("radial_gcd") == "t - 1"
        and physical_sm_source_equality.get(
            "direct_source_algebra_stationary_Hessian_available"
        )
        is False
        and physical_sm_source_equality.get(
            "complete_nonradial_equality_orbit_proved"
        )
        is False
        and physical_sm_source_equality.get("old_formal_U1_89_EFT_scope_promoted")
        is False
        and all(
            physical_sm_source_equality.get(f"physical_SM_{gate}_closed")
            is False
            for gate in ("G3", "G4", "G5")
        )
    )
    if physical_sm_five_amplitude_equality is None:
        physical_sm_five_amplitude_equality = {}
    physical_sm_five_amplitude_equality_bound = bool(
        physical_sm_five_amplitude_equality.get("source_bound") is True
        and physical_sm_five_amplitude_equality.get(
            "exact_radial_theorem_strictly_extended"
        )
        is True
        and physical_sm_five_amplitude_equality.get(
            "five_real_amplitude_slice_stationary_equality_classified"
        )
        is True
        and physical_sm_five_amplitude_equality.get(
            "exact_real_discrete_sign_variant_count"
        )
        == 16
        and physical_sm_five_amplitude_equality.get(
            "target_strict_minimum_on_five_amplitude_slice"
        )
        is True
        and physical_sm_five_amplitude_equality.get(
            "full_486_field_stationary_equality_classified"
        )
        is False
        and physical_sm_five_amplitude_equality.get(
            "continuous_symmetry_orbit_equivalence_of_16_variants_proved"
        )
        is False
        and physical_sm_five_amplitude_equality.get(
            "direct_source_algebra_full_486_Hessian_available"
        )
        is False
        and all(
            physical_sm_five_amplitude_equality.get(
                f"physical_SM_{gate}_closed"
            )
            is False
            for gate in ("G3", "G4", "G5")
        )
    )
    if physical_sm_hard_projector_hessians is None:
        physical_sm_hard_projector_hessians = {}
    physical_sm_hard_projector_hessians_bound = bool(
        physical_sm_hard_projector_hessians.get("source_bound") is True
        and physical_sm_hard_projector_hessians.get(
            "exact_source_Hessian_row_count"
        )
        == 10
        and physical_sm_hard_projector_hessians.get(
            "remaining_active_row_count"
        )
        == 27
        and physical_sm_hard_projector_hessians.get(
            "all_10_O27_O44_source_Hessians_closed"
        )
        is True
        and physical_sm_hard_projector_hessians.get(
            "all_37_active_source_Hessians_closed"
        )
        is False
        and physical_sm_hard_projector_hessians.get(
            "full_witness_stationarity_rank_PSD_closed"
        )
        is False
        and physical_sm_hard_projector_hessians.get(
            "full_486_global_equality_orbit_closed"
        )
        is False
        and all(
            physical_sm_hard_projector_hessians.get(
                f"physical_SM_{gate}_closed"
            )
            is False
            for gate in ("G3", "G4", "G5")
        )
    )
    if physical_sm_last_six_hessians is None:
        physical_sm_last_six_hessians = {}
    physical_sm_last_six_hessians_bound = bool(
        physical_sm_last_six_hessians.get("source_bound") is True
        and physical_sm_last_six_hessians.get(
            "exact_last_six_source_Hessians_closed"
        )
        is True
        and physical_sm_last_six_hessians.get(
            "all_37_active_source_Hessians_available"
        )
        is True
        and physical_sm_last_six_hessians.get(
            "exact_37_row_aggregate_stationarity_kernel_rank_PSD_closed"
        )
        is False
        and physical_sm_last_six_hessians.get(
            "full_486_global_equality_orbit_closed"
        )
        is False
        and all(
            physical_sm_last_six_hessians.get(f"physical_SM_{gate}_closed")
            is False
            for gate in ("G3", "G4", "G5")
        )
    )
    if physical_sm_37_row_aggregate is None:
        physical_sm_37_row_aggregate = {}
    physical_sm_37_row_aggregate_bound = bool(
        physical_sm_37_row_aggregate.get("source_bound") is True
        and physical_sm_37_row_aggregate.get(
            "all_37_active_Hessians_source_derived"
        )
        is True
        and physical_sm_37_row_aggregate.get(
            "exact_source_aggregate_value_minus_one_and_stationary"
        )
        is True
        and physical_sm_37_row_aggregate.get(
            "exact_source_aggregate_kernel_dimension"
        )
        == 38
        and physical_sm_37_row_aggregate.get("exact_source_aggregate_rank") == 448
        and physical_sm_37_row_aggregate.get(
            "exact_source_aggregate_PSD_and_strict_mod_symmetry"
        )
        is True
        and physical_sm_37_row_aggregate.get(
            "source_bound_local_stationary_Hessian_problem_complete"
        )
        is True
        and physical_sm_37_row_aggregate.get(
            "full_486_global_equality_orbit_closed"
        )
        is False
        and all(
            physical_sm_37_row_aggregate.get(f"physical_SM_{gate}_closed")
            is False
            for gate in ("G3", "G4", "G5")
        )
    )
    if physical_sm_local_equality_orbit is None:
        physical_sm_local_equality_orbit = {}
    physical_sm_local_equality_orbit_bound = bool(
        physical_sm_local_equality_orbit.get("source_bound") is True
        and physical_sm_local_equality_orbit.get(
            "full_486_local_stationary_orbit_classified"
        )
        is True
        and physical_sm_local_equality_orbit.get(
            "full_486_local_stationary_equality_orbit_classified"
        )
        is True
        and physical_sm_local_equality_orbit.get(
            "all_16_sign_variants_one_continuous_K_orbit"
        )
        is True
        and physical_sm_local_equality_orbit.get(
            "target_orbit_strict_local_minimum_mod_K"
        )
        is True
        and physical_sm_local_equality_orbit.get(
            "quantitative_neighborhood_radius_proved"
        )
        is False
        and physical_sm_local_equality_orbit.get(
            "complete_486_global_equality_orbit_classified"
        )
        is False
        and all(
            physical_sm_local_equality_orbit.get(f"physical_SM_{gate}_closed")
            is False
            for gate in ("G3", "G4", "G5")
        )
    )
    if physical_sm_g4_g5_branch_mismatch is None:
        physical_sm_g4_g5_branch_mismatch = {}
    physical_sm_g4_g5_branch_mismatch_bound = bool(
        physical_sm_g4_g5_branch_mismatch.get("source_bound") is True
        and physical_sm_g4_g5_branch_mismatch.get(
            "exact_branch_mismatch_proved"
        )
        is True
        and physical_sm_g4_g5_branch_mismatch.get(
            "unit_rescaling_case_count"
        )
        == 101
        and physical_sm_g4_g5_branch_mismatch.get(
            "current_five_amplitude_target_is_canonical_physical_EW_branch"
        )
        is False
        and physical_sm_g4_g5_branch_mismatch.get(
            "global_no_go_for_other_physical_EW_branches"
        )
        is False
        and all(
            physical_sm_g4_g5_branch_mismatch.get(
                f"physical_SM_{gate}_closed"
            )
            is False
            for gate in ("G4", "G5", "G6", "G7", "G8")
        )
    )
    heavy_vector_tree_contract_bound = bool(
        physical_sm_heavy_vectors.get("source_bound") is True
        and physical_sm_heavy_vectors.get(
            "exact_parameterized_tree_vector_mass_matrix_closed"
        )
        is True
        and physical_sm_heavy_vectors.get(
            "exact_vector_rank_kernel_and_Goldstone_image_closed"
        )
        is True
        and physical_sm_heavy_vectors.get(
            "exact_SU3C_x_U1em_vector_sector_resolution_closed"
        )
        is True
        and physical_sm_heavy_vectors.get(
            "parameterized_vector_threshold_log_inputs_closed"
        )
        is True
        and physical_sm_heavy_vectors.get("pole_vector_masses_closed") is False
        and physical_sm_heavy_vectors.get("physical_G6_closed") is False
        and physical_sm_heavy_vectors.get("physical_G7_closed") is False
    )
    conditional_scalar_tree_contract_bound = bool(
        conditional_physical_sm_scalar_spectrum.get("source_bound") is True
        and conditional_physical_sm_scalar_spectrum.get(
            "conditional_reconstructed_tree_scalar_spectrum_closed"
        )
        is True
        and conditional_physical_sm_scalar_spectrum.get(
            "conditional_tree_Hessian_factorization_closed"
        )
        is True
        and conditional_physical_sm_scalar_spectrum.get(
            "source_algebra_derived_tree_scalar_spectrum_closed"
        )
        is False
        and conditional_physical_sm_scalar_spectrum.get(
            "physical_scalar_pole_spectrum_closed"
        )
        is False
        and conditional_physical_sm_scalar_spectrum.get("physical_G6_closed")
        is False
    )
    if contract_state == "BLOCKED" or (ledger and not (g1_closed and g2_closed)):
        state = "BLOCKED"
    elif (
        contract_state != "PASS"
        or not g1_scoped_complete
        or not g1_full_component_tensor_integration_complete
        or not g2_scoped_complete
        or not mathematical_g2_component_potential_closure
        or not gauged_g3_contract_bound
    ):
        state = "OPEN"
    elif model_wide_no_go:
        state = "FAIL"
    elif (
        stable_quotient
        and bfb
        and global_minimum
        and authoritative_g3_g4_g5_g6_closed
        and complete_source_bound_spectrum
    ):
        state = "PASS"
    else:
        state = "OPEN"
    return _gate(
        "full_scalar_potential_vacuum_and_spectrum",
        state,
        (
            "The exact G1 multiplicity census is distinct from the explicit "
            "component-tensor integration required for full G1. The gauged "
            "44-direction/51-parameter G2 derivatives on 486 real fields are "
            "recertified. Three structural gradient columns vanish exactly, "
            "and exact lower- and upper-rank certificates prove stationarity "
            "rank/nullity 13/38. The gauged SO(10)xU(1)_X orbit has exact rank "
            "37, so its gauge quotient is 449-dimensional and includes the axion; "
            "removing the independent global-PQ direction gives the exactly "
            "448-dimensional massive/transverse Hessian space. A sparse "
            "27-of-51 candidate with J0=-21/200 has a complete source-bound "
            "sum-of-squares decomposition: the potential is exactly BFB and "
            "the selected vacuum is exactly stationary. Direct tensor assembly "
            "gives P+Delta rank/nullity 429/33, while the exact extension "
            "Jacobian leaves only 38 symmetry tangents and proves positivity in "
            "all 448 transverse directions. The selected orbit is therefore a "
            "strict local minimum. An exact symmetry-inequivalent 126bar field "
            "configuration is lower by 25*r^4/19008, and the fixed-P branch obeys "
            "the exact gap/curvature identity gap=-m_transverse^2/8; that branch is "
            "therefore excluded. The lower replacement has the wrong stabilizer. "
            "A new SU(5)-singlet Phi+Delta branch is an exact global minimum in the "
            "Phi/Sigma subsystem and has exact Hessian "
            "rank/nullity 429/33 with a strictly positive local quotient. Its "
            "chiral-H extension is exactly stationary and BFB for the frozen "
            "representative; the provenance audit shows its abelian stabilizer "
            "is U(1)_89 rather than physical electromagnetism. "
            "A new reconstructed target has the exact standard-SM stabilizer. Its "
            "source-derived all-37 Hessian is exactly stationary at V=-1, has "
            "kernel/rank 38/448, and is PSD strictly modulo symmetry. Its full-486 "
            "local stationary/equality orbit is also exact, but the complete global "
            "equality orbit remains open, so these results do not close physical "
            "G3-G7. The old abstract EFT proofs remain formal only. The maximally "
            "negative pure-Delta sector is excluded for "
            "arbitrary real Phi with all residuals retained and sharp gap 1/5000. "
            "The prior four-real-dimensional SU(3) regression is historical and "
            "subsumed. At fixed H=h_- and Sigma=q/4, the corrected v21 exact "
            "theorem covers every real Phi210. At that fixed endpoint, the exact "
            "SU(4) stabilizer and its 15 Phi210 actions are certified, while an "
            "exact aligned 25-carrier rank-210 decomposition and physical real "
            "maps feed an explicit 45-element invariant quadratic basis obtained "
            "from a 5952x551 rank-506 constraint system. The exact augmented "
            "census has 19594 real Schur parameters and 6585 invariant rows. "
            "Its complete cubic interface contains all 1414 real cross variables "
            "and an exact-rank-478, 478x1414 integer map with kernel dimension "
            "936. The reserved zero placeholder is nonphysical. The homogeneous "
            "quartic interface is an exact-rank-6057, 6057x18085 integer map "
            "with kernel dimension 12028. The legacy v20 assembled physical "
            "target is rejected. The corrected 6585x19594 standard positive-Gram "
            "map, ordered-spectral target, and exact strict 22-block/824-pivot "
            "primal prove p(t,Phi)>0 off the homogeneous origin and A(Phi)>3/200 "
            "at t=1 for every real Phi210. For that historical fixed-H/Sigma "
            "frontier, global Sigma, general/full H, and its then-unassembled "
            "Hessian remained open. The current physical-SM branch instead has "
            "the exact source-derived Hessian closure above; its complete global "
            "equality orbit and physical G3 remain open. "
            "The old no-X 64/91 result remains historical."
        ),
        {
            "model_contract_state": contract_state,
            "authoritative_G1_closed": g1_closed,
            "authoritative_G2_closed": g2_closed,
            "authoritative_G3_closed": g3_closed,
            "authoritative_G4_closed": g4_closed,
            "authoritative_G5_closed": g5_closed,
            "authoritative_G6_closed": g6_closed,
            "authoritative_G3_G4_G5_G6_closed": (
                authoritative_g3_g4_g5_g6_closed
            ),
            "gauged_G1_multiplicity_census_complete": (
                g1_multiplicity_census_complete
            ),
            "gauged_G1_full_component_tensor_integration_complete": (
                g1_full_component_tensor_integration_complete
            ),
            "renormalizable_G1_component_tensor_theorem_artifact_present": bool(
                reports.get("renormalizable_g1_component_tensor", {})
            ),
            "renormalizable_G1_component_tensor_theorem_source_bound": (
                renormalizable_g1_component_tensor_closure.get("source_bound")
                is True
            ),
            "renormalizable_G1_component_tensor_theorem_matches_ledger": (
                g1_component_tensor_view_matches_ledger
            ),
            "renormalizable_mathematical_G1_closed": (
                mathematical_g1_component_tensor_closure
            ),
            "renormalizable_G1_authoritative_promotion_closed": (
                renormalizable_g1_component_tensor_closure.get(
                    "authoritative_G1_promoted_closed"
                )
                is True
            ),
            "renormalizable_G1_release_verified": (
                renormalizable_g1_component_tensor_closure.get(
                    "release_G1_verified"
                )
                is True
            ),
            "renormalizable_G1_downstream_integration_completed": (
                renormalizable_g1_component_tensor_closure.get(
                    "downstream_integration_completed"
                )
                is True
            ),
            "renormalizable_G1_external_SARAH_blocker_preserved": (
                gate_ledger.CONTRACT_BLOCKER
                in renormalizable_g1_component_tensor_closure.get(
                    "release_blockers", []
                )
            ),
            "renormalizable_G1_component_tensor_counts": (
                renormalizable_g1_component_tensor_closure.get("counts", {})
            ),
            # Compatibility alias: this means the multiplicity census only.
            "gauged_G1_scoped_calculation_complete": g1_scoped_complete,
            "gauged_G2_scoped_calculation_complete": g2_scoped_complete,
            "renormalizable_G2_mathematical_theorem_artifact_present": bool(
                reports.get("renormalizable_g2_mathematical", {})
            ),
            "renormalizable_G2_mathematical_theorem_source_bound": (
                renormalizable_g2_mathematical_closure.get("source_bound") is True
            ),
            "renormalizable_G2_mathematical_theorem_matches_ledger": (
                g2_mathematical_view_matches_ledger
            ),
            "renormalizable_mathematical_G2_closed": (
                mathematical_g2_component_potential_closure
            ),
            "renormalizable_G2_authoritative_promotion_closed": (
                renormalizable_g2_mathematical_closure.get(
                    "authoritative_G2_promoted_closed"
                )
                is True
            ),
            "renormalizable_G2_release_verified": (
                renormalizable_g2_mathematical_closure.get("release_G2_verified")
                is True
            ),
            "renormalizable_G2_downstream_integration_completed": (
                renormalizable_g2_mathematical_closure.get(
                    "downstream_integration_completed"
                )
                is True
            ),
            "renormalizable_G2_external_SARAH_blocker_preserved": (
                gate_ledger.CONTRACT_BLOCKER
                in renormalizable_g2_mathematical_closure.get(
                    "release_blockers", []
                )
            ),
            "renormalizable_G2_component_potential_counts": (
                renormalizable_g2_mathematical_closure.get("counts", {})
            ),
            "scalar_contract_pre_audit_G2_certified_flag": (
                scalar_contract_pre_audit_g2_flag
            ),
            "dedicated_G2_audit_is_source_authoritative": g2_scoped_complete,
            "dedicated_G2_audit_supersedes_pre_audit_scalar_contract_flag": (
                dedicated_g2_supersedes_pre_audit_scalar_contract_flag
            ),
            "G6_full_physical_spectrum_artifact_present": bool(spectrum),
            "G6_complete_source_bound_physical_spectrum": (
                complete_source_bound_spectrum
            ),
            "gauged_G2_direction_parameter_field_counts": [
                g2_counts.get("invariant_directions"),
                g2_counts.get("real_parameters"),
                g2_counts.get("real_field_dimension"),
            ],
            "gauged_G2_promoted_stationarity_rank_nullity": [
                g2_stationary.get("rank"),
                g2_stationary.get("nullity"),
            ],
            "gauged_G2_exact_projector_zero_corrected_normalized_SVD_rank_13": bool(
                _dig(
                    g2_audit,
                    "flags",
                    "exact_projector_zero_corrected_normalized_SVD_rank_13",
                    default=False,
                )
            ),
            "gauged_G2_stationarity_rank_13_exactly_certified": bool(
                _dig(
                    g2_audit,
                    "flags",
                    "stationarity_rank_13_exactly_certified",
                    default=False,
                )
            ),
            "gauged_G2_stationarity_nullity_38_exactly_certified": bool(
                _dig(
                    g2_audit,
                    "flags",
                    "stationarity_nullity_38_exactly_certified",
                    default=False,
                )
            ),
            "gauged_G2_stationarity_rank_upper_bound_13_exactly_certified": bool(
                _dig(
                    g2_audit,
                    "flags",
                    "stationarity_rank_upper_bound_13_exactly_certified",
                    default=False,
                )
            ),
            "gauged_G3_artifact_present": bool(gauged),
            "gauged_G3_corrected_common_kernel_artifact_present": bool(common),
            "gauged_G3_corrected_common_kernel_honestly_bound": (
                corrected_common_kernel_honestly_bound
            ),
            "gauged_G3_corrected_common_kernel_rank_nullity_numerical": [
                common_kernel.get("rank"),
                common_kernel.get("nullity"),
            ],
            "gauged_G3_corrected_common_kernel_proof_grade": (
                common_diagnostic.get("proof_grade")
            ),
            "gauged_G3_SOS_candidate_artifact_present": bool(sos),
            "gauged_G3_PD_rank_artifact_present": bool(pd_rank),
            "gauged_G3_A_square_artifact_present": bool(a_square),
            "gauged_G3_SOS_BFB_artifact_present": bool(sos_bfb),
            "gauged_G3_fixed_P_kernel_bound_artifact_present": bool(kernel_bound),
            "gauged_G3_lower_replacement_artifact_present": bool(replacement),
            "gauged_G3_SU5_Delta_PD_artifact_present": bool(su5_pd),
            "gauged_G3_SU5_Delta_HSX_artifact_present": bool(su5_hsx),
            "gauged_G3_SU5_Delta_HSX_exact_Hessian_artifact_present": bool(
                su5_hsx_exact_hessian
            ),
            "gauged_G3_SU5_equality_artifact_present": bool(su5_equality),
            "gauged_G3_SU5_Phi_orbit_audit_artifact_present": bool(
                su5_phi_orbit
            ),
            "gauged_G3_SU5_Phi_local_component_artifact_present": bool(
                su5_phi_local
            ),
            "gauged_G3_SU5_Phi_SU3_slice_artifact_present": bool(
                su5_phi_su3
            ),
            "gauged_G3_SU5_global_gap_artifact_present": bool(su5_gap),
            "gauged_G3_SU5_fixed_F_offkernel_artifact_present": bool(
                fixed_f_bound
            ),
            "gauged_G3_SU5_max_negative_zero_residual_artifact_present": bool(
                max_negative_bound
            ),
            "gauged_G3_SU5_max_negative_full_residual_artifact_present": bool(
                max_negative_full_bound
            ),
            "gauged_G3_SU5_max_negative_rank1_SU3_slice_artifact_present": bool(
                rank1_su3_bound
            ),
            "gauged_G3_rank1_SU4_stabilizer_artifact_present": bool(
                rank1_su4_stabilizer
            ),
            "gauged_G3_rank1_SU4_Phi210_intertwiners_artifact_present": bool(
                rank1_su4_intertwiners
            ),
            "gauged_G3_rank1_SU4_aligned_carriers_artifact_present": bool(
                rank1_su4_aligned
            ),
            "gauged_G3_rank1_SU4_Phi210_quadratic_basis_artifact_present": bool(
                rank1_su4_quadratic
            ),
            "gauged_G3_rank1_SU4_augmented_SOS_census_artifact_present": bool(
                rank1_su4_census
            ),
            "gauged_G3_rank1_SU4_augmented_SOS_cubic_map_artifact_present": bool(
                rank1_su4_cubic
            ),
            "gauged_G3_rank1_SU4_augmented_SOS_quartic_map_artifact_present": bool(
                rank1_su4_quartic
            ),
            "gauged_G3_rank1_SU4_augmented_SOS_PSD_target_artifact_present": bool(
                rank1_su4_psd_target
            ),
            "gauged_G3_alternative_global_SOS_artifact_present": bool(
                alternative_sos
            ),
            "final_G3_acceptance_gate_artifact_present": bool(final_g3),
            "parallel_EFT_G3_acceptance_gate_artifact_present": bool(
                final_g3_eft
            ),
            "parallel_EFT_G3_acceptance_source_bound": (
                parallel_eft_g3_acceptance["source_bound"]
            ),
            "parallel_EFT_G3_acceptance_raw_sha256_exact": (
                parallel_eft_g3_acceptance["checks"]["raw_sha256_exact"]
            ),
            "parallel_EFT_mathematical_G3_closed": (
                parallel_eft_g3_acceptance[
                    "mathematical_G3_closed_for_EFT_model"
                ]
            ),
            "parallel_EFT_release_G3_verified": (
                parallel_eft_g3_acceptance[
                    "release_G3_verified_for_EFT_model"
                ]
            ),
            "original_renormalizable_mathematical_G3_closed": (
                parallel_eft_g3_acceptance[
                    "mathematical_G3_closed_for_original_renormalizable_model"
                ]
            ),
            "legacy_EFT_G3_gate_did_not_claim_G4": (
                parallel_eft_g3_acceptance["G4_closed"] is False
            ),
            "parallel_EFT_G4_mathematical_gate_artifact_present": bool(
                final_g4_eft
            ),
            "parallel_EFT_G4_mathematical_source_bound": (
                parallel_eft_g4_mathematical["source_bound"]
            ),
            "parallel_EFT_G4_mathematical_raw_sha256_exact": (
                parallel_eft_g4_mathematical["checks"]["raw_sha256_exact"]
            ),
            "parallel_EFT_G4_integration_completed": (
                parallel_eft_g4_mathematical["checks"][
                    "parallel_integration_completed"
                ]
            ),
            "parallel_EFT_G4_integration_blocker_removed": (
                "parallel_EFT_G4_integrated_into_release_orchestrators"
                not in parallel_eft_g4_mathematical["release_blockers"]
            ),
            "parallel_EFT_G4_closed": (
                parallel_eft_g4_mathematical[
                    "mathematical_G4_closed_for_EFT_model"
                ]
            ),
            "parallel_EFT_release_G4_verified": (
                parallel_eft_g4_mathematical[
                    "release_G4_verified_for_EFT_model"
                ]
            ),
            "original_renormalizable_mathematical_G4_closed": (
                parallel_eft_g4_mathematical[
                    "mathematical_G4_closed_for_original_renormalizable_model"
                ]
            ),
            "parallel_EFT_G5_mathematical_gate_artifact_present": bool(
                final_g5_eft
            ),
            "parallel_EFT_G5_mathematical_source_bound": (
                parallel_eft_g5_mathematical["source_bound"]
            ),
            "parallel_EFT_G5_mathematical_raw_sha256_exact": (
                parallel_eft_g5_mathematical["checks"]["raw_sha256_exact"]
            ),
            "parallel_EFT_G5_integration_completed": (
                parallel_eft_g5_mathematical["checks"][
                    "parallel_integration_completed"
                ]
            ),
            "parallel_EFT_G5_integration_blocker_removed": (
                "downstream_parallel_G5_integration_completed"
                not in parallel_eft_g5_mathematical["release_blockers"]
            ),
            "parallel_EFT_G5_closed": (
                parallel_eft_g5_mathematical[
                    "mathematical_G5_closed_for_EFT_model"
                ]
            ),
            "parallel_EFT_release_G5_verified": (
                parallel_eft_g5_mathematical[
                    "release_G5_verified_for_EFT_model"
                ]
            ),
            "original_renormalizable_mathematical_G5_closed": (
                parallel_eft_g5_mathematical[
                    "authoritative_renormalizable_G5_closed"
                ]
            ),
            "parallel_EFT_G6_spectrum_gate_artifact_present": bool(final_g6_eft),
            "parallel_EFT_G6_spectrum_source_bound": (
                parallel_eft_g6_spectrum["source_bound"]
            ),
            "parallel_EFT_G6_spectrum_raw_sha256_exact": (
                parallel_eft_g6_spectrum["checks"]["raw_sha256_exact"]
            ),
            "parallel_EFT_G6_gate_source_raw_sha256_exact": (
                parallel_eft_g6_spectrum["checks"][
                    "gate_source_raw_sha256_exact"
                ]
            ),
            "parallel_EFT_G6_spectrum_core_sha256_exact": (
                parallel_eft_g6_spectrum["checks"]["core_sha256_exact"]
            ),
            "parallel_EFT_G6_spectrum_dependency_pins_exact": (
                parallel_eft_g6_spectrum["checks"][
                    "spectrum_source_and_JSON_raw_pins_exact"
                ]
                and parallel_eft_g6_spectrum["checks"][
                    "upstream_cores_and_gate_JSON_pins_exact"
                ]
            ),
            "parallel_EFT_G6_integration_completed": (
                parallel_eft_g6_spectrum["parallel_integration_completed"]
            ),
            "parallel_EFT_G6_integration_blocker_removed": (
                "parallel_EFT_G6_integrated_into_release_orchestrators"
                not in parallel_eft_g6_spectrum["release_blockers"]
            ),
            "parallel_EFT_mathematical_G6_closed": (
                parallel_eft_g6_spectrum[
                    "mathematical_G6_closed_for_EFT_model"
                ]
            ),
            "parallel_EFT_formal_SU3_x_U1_89_factorization_closed": (
                parallel_eft_g6_spectrum[
                    "formal_SU3_x_U1_89_tree_factorization_closed"
                ]
            ),
            "G6_physical_stabilizer_audit_source_bound": (
                g6_sm_provenance.get("source_bound") is True
            ),
            "G6_actual_residual_group": g6_sm_provenance.get(
                "actual_residual_group"
            ),
            "G6_physical_U1em_provenance_complete": False,
            "G6_physical_mathematical_closed": False,
            "physical_SM_vacuum_truth_overlay_source_bound": (
                physical_sm_overlay_bound
            ),
            "physical_SM_target_exactly_constructed": bool(
                physical_sm_overlay_bound
            ),
            "physical_SM_standard_stabilizer_proved": bool(
                physical_sm_overlay_bound
            ),
            "old_selected_EFT_actual_stabilizer": physical_sm_vacuum.get(
                "old_selected_EFT_target_actual_stabilizer"
            ),
            "old_selected_EFT_physical_SM_label_superseded": bool(
                physical_sm_overlay_bound
            ),
            "physical_SM_complete_global_source_algebra_equality_witness_closed": False,
            "physical_SM_global_equality_orbit_closed": False,
            "physical_SM_radial_stationary_equality_classified_exactly": (
                physical_sm_radial_equality_bound
            ),
            "physical_SM_radial_stationary_equality_gcd": (
                physical_sm_source_equality.get("radial_gcd")
            ),
            "physical_SM_complete_nonradial_equality_orbit_closed": False,
            "physical_SM_source_algebra_Hessian_closed": (
                physical_sm_37_row_aggregate_bound
            ),
            "physical_SM_five_amplitude_equality_source_bound": (
                physical_sm_five_amplitude_equality_bound
            ),
            "physical_SM_five_amplitude_slice_stationary_equality_classified": (
                physical_sm_five_amplitude_equality_bound
            ),
            "physical_SM_five_amplitude_exact_sign_variant_count": (
                16 if physical_sm_five_amplitude_equality_bound else None
            ),
            "physical_SM_five_amplitude_variants_one_continuous_orbit_proved": (
                physical_sm_local_equality_orbit_bound
            ),
            "physical_SM_complete_global_486_field_stationary_equality_classified": False,
            "physical_SM_hard_projector_Hessians_source_bound": (
                physical_sm_hard_projector_hessians_bound
            ),
            "physical_SM_exact_source_Hessian_rows_closed": (
                37 if physical_sm_37_row_aggregate_bound else None
            ),
            "physical_SM_remaining_active_Hessian_rows": (
                0 if physical_sm_37_row_aggregate_bound else None
            ),
            "physical_SM_all_37_active_source_Hessians_closed": (
                physical_sm_37_row_aggregate_bound
            ),
            "physical_SM_last_six_Hessians_source_bound": (
                physical_sm_last_six_hessians_bound
            ),
            "physical_SM_all_37_active_source_Hessians_available": (
                physical_sm_last_six_hessians_bound
            ),
            "physical_SM_37_row_local_Hessian_theorem_source_bound": (
                physical_sm_37_row_aggregate_bound
            ),
            "physical_SM_source_aggregate_kernel_dimension": (
                38 if physical_sm_37_row_aggregate_bound else None
            ),
            "physical_SM_source_aggregate_rank": (
                448 if physical_sm_37_row_aggregate_bound else None
            ),
            "physical_SM_source_aggregate_PSD_strict_mod_symmetry": (
                physical_sm_37_row_aggregate_bound
            ),
            "physical_SM_full_486_local_equality_orbit_source_bound": (
                physical_sm_local_equality_orbit_bound
            ),
            "physical_SM_16_sign_variants_one_continuous_K_orbit": (
                physical_sm_local_equality_orbit_bound
            ),
            "physical_SM_quantitative_local_orbit_radius_proved": False,
            "physical_SM_full_witness_stationarity_rank_PSD_closed": (
                physical_sm_37_row_aggregate_bound
            ),
            "physical_SM_G4_G5_branch_mismatch_source_bound": (
                physical_sm_g4_g5_branch_mismatch_bound
            ),
            "physical_SM_five_amplitude_target_is_canonical_EW_branch": False,
            "physical_SM_global_no_go_for_other_EW_branches": False,
            "physical_SM_G3_G4_G5_G6_G7_closed": {
                gate: False for gate in ("G3", "G4", "G5", "G6", "G7")
            },
            "physical_SM_heavy_vector_tree_contract_source_bound": (
                heavy_vector_tree_contract_bound
            ),
            "exact_parameterized_heavy_vector_mass_matrix_closed": (
                heavy_vector_tree_contract_bound
            ),
            "exact_heavy_vector_rank_kernel_Goldstone_image_closed": (
                heavy_vector_tree_contract_bound
            ),
            "exact_heavy_vector_SU3C_U1em_sector_resolution_closed": (
                heavy_vector_tree_contract_bound
            ),
            "parameterized_heavy_vector_threshold_log_inputs_closed": (
                heavy_vector_tree_contract_bound
            ),
            "physical_heavy_vector_pole_masses_closed": False,
            "physical_vector_Goldstone_ghost_matching_closed": False,
            "conditional_physical_SM_scalar_tree_spectrum_source_bound": (
                conditional_scalar_tree_contract_bound
            ),
            "conditional_reconstructed_tree_scalar_spectrum_closed": (
                conditional_scalar_tree_contract_bound
            ),
            "source_algebra_derived_physical_scalar_spectrum_closed": False,
            "physical_scalar_pole_spectrum_closed": False,
            "G6_parameterized_formal_G89_matching_source_bound": (
                g6_g7_parameterized_matching.get("source_bound") is True
            ),
            "parallel_EFT_release_G6_verified": (
                parallel_eft_g6_spectrum[
                    "release_G6_verified_for_EFT_model"
                ]
            ),
            "parallel_EFT_G6_spectrum_summary": parallel_eft_g6_spectrum[
                "spectrum_summary"
            ],
            "original_renormalizable_mathematical_G6_closed": (
                parallel_eft_g6_spectrum[
                    "authoritative_renormalizable_G6_closed"
                ]
            ),
            "authoritative_G6_gate_mutated_by_parallel_EFT": (
                parallel_eft_g6_spectrum["authoritative_G6_gate_mutated"]
            ),
            "authoritative_renormalizable_G3_G4_G5_statuses": {
                name: _dig(authoritative_gates, name, "status")
                for name in ("G3", "G4", "G5")
            },
            "authoritative_renormalizable_G3_G4_G5_G6_statuses": {
                name: _dig(authoritative_gates, name, "status")
                for name in ("G3", "G4", "G5", "G6")
            },
            "gauged_G3_SOS_candidate_exact_local_and_globally_fail_closed": (
                sos_candidate_exact_local_and_globally_fail_closed
            ),
            # Compatibility alias retained for older report consumers.
            "gauged_G3_SOS_candidate_honestly_scoped": (
                sos_candidate_exact_local_and_globally_fail_closed
            ),
            "gauged_G3_A_square_recoupling_exactly_source_bound": (
                a_square_exactly_scoped
            ),
            "gauged_G3_SOS_BFB_stationarity_exactly_source_bound": (
                sos_bfb_exactly_scoped
            ),
            "gauged_G3_PD_rank_direct_exact_and_fail_closed": (
                pd_rank_direct_exact_and_fail_closed
            ),
            "gauged_G3_constructive_candidate_nonzero_of_51": [
                sos_coefficients.get("nonzero_count"),
                51,
            ],
            "gauged_G3_constructive_candidate_max_abs_coefficient": (
                sos_coefficients.get("maximum_absolute_coefficient")
            ),
            "gauged_G3_constructive_candidate_J0": _dig(
                sos_coefficients,
                "symbolic_nonzero",
                "lambda::O48_B01_Phi_self_quartics",
            ),
            "gauged_G3_exact_PD_rank_nullity": [
                pd_core.get("rank"),
                pd_core.get("nullity"),
            ],
            "gauged_G3_exact_full_Hessian_rank": pd_extension.get(
                "exact_full_Hessian_rank"
            ),
            "gauged_G3_direct_PD_source_binding": pd_flags.get(
                "direct_exact_source_binding"
            ),
            "gauged_G3_frontier_honestly_fail_closed": (
                g3_frontier_honestly_fail_closed
            ),
            "gauged_G3_fixed_P_branch_exactly_excluded": (
                fixed_p_branch_exactly_excluded
            ),
            "gauged_G3_lower_replacement_rejected_for_wrong_symmetry": (
                lower_replacement_rejected_for_wrong_symmetry
            ),
            "gauged_G3_SU5_Delta_PD_exact_global_frontier": (
                su5_delta_pd_exact_global_frontier
            ),
            "gauged_G3_SU5_Delta_PD_exact_Hessian_rank_nullity": (
                [429, 33] if su5_delta_pd_exact_global_frontier else [None, None]
            ),
            "gauged_G3_SU5_Delta_PD_full_486_extension_open": not bool(
                su5_pd_scope.get("full_486_field_stationarity")
            ),
            "gauged_G3_SU5_Delta_PD_global_orbit_uniqueness_open": not bool(
                su5_pd_scope.get("global_orbit_uniqueness")
            ),
            "gauged_G3_SU5_Delta_HSX_honest_frontier": (
                su5_delta_hsx_honest_frontier
            ),
            "gauged_G3_SU5_Delta_HSX_exact_symmetry_ranks": [
                su5_hsx_orbit.get("SO10_rank"),
                su5_hsx_orbit.get("SO10_plus_U1X_rank"),
                su5_hsx_orbit.get("SO10_plus_U1X_plus_PQ_rank"),
            ],
            "gauged_G3_SU5_Delta_HSX_full_quartic_BFB_exact": (
                su5_hsx_bfb.get("homogeneous_quartic_BFB_certified")
            ),
            "gauged_G3_SU5_Delta_HSX_transverse_dimension": (
                su5_hsx_hessian.get("transverse_dimension")
            ),
            "gauged_G3_SU5_Delta_HSX_full_Hessian_proof_grade": (
                su5_hsx_hessian.get("proof_grade")
            ),
            "gauged_G3_SU5_Delta_HSX_exact_Hessian_audit_fail_closed": (
                su5_hsx_exact_hessian_audit_fail_closed
            ),
            "gauged_G3_SU5_Delta_HSX_exact_Hessian_certified": (
                hsx_exact_hessian_closed
            ),
            "gauged_G3_SU5_Delta_HSX_exact_Hessian_status": (
                su5_hsx_exact_hessian.get("status")
            ),
            "gauged_G3_SU5_equality_honestly_reduced": (
                su5_equality_honestly_reduced
            ),
            "gauged_G3_SU5_Phi_orbit_literal_refuted_signed_open": (
                su5_phi_orbit_honestly_refuted_and_open
            ),
            "gauged_G3_SU5_signed_Phi_local_components_exactly_closed": (
                su5_phi_local_components_exactly_closed
            ),
            "gauged_G3_SU5_distant_Phi_components_excluded": (
                su5_equality_scope.get(
                    "distant_disconnected_Phi_components_excluded"
                )
            ),
            "gauged_G3_SU5_Phi_SU3_fixed_slice_exactly_closed": (
                su5_phi_su3_slice_exactly_closed
            ),
            "gauged_G3_SU5_global_Phi_orbit_lemma_open": not bool(
                su5_equality_lemma.get("proved")
            ),
            "gauged_G3_SU5_global_Phi_orbit_lemma_closed": bool(
                su5_equality_lemma.get("proved")
            ),
            "gauged_G3_SU5_all_PD_equality_orbits_classified_exactly": bool(
                su5_equality_scope.get(
                    "global_equality_orbit_classification_complete"
                )
            ),
            "gauged_G3_SU5_global_Phi_theorem_core_sha256": (
                su5_equality_global.get("core_sha256")
            ),
            "gauged_G3_SU5_quantitative_beta_global_coercivity_open": not bool(
                su5_equality_scope.get(
                    "quantitative_beta_global_coercivity_proved"
                )
            ),
            "gauged_G3_SU5_chiral_global_gap_honestly_reduced": (
                su5_chiral_gap_honestly_reduced
            ),
            "gauged_G3_SU5_fixed_F_full_gap_exactly_closed": (
                su5_fixed_f_full_gap_closed
            ),
            "gauged_G3_SU5_arbitrary_Phi_offstratum_gap_open": not bool(
                fixed_f_bound_scope.get("arbitrary_Phi_proved")
            ),
            "gauged_G3_SU5_max_negative_all_zero_residual_route_excluded": (
                su5_max_negative_all_zero_route_excluded
            ),
            "gauged_G3_SU5_max_negative_all_zero_residual_strict_margin": _dig(
                max_negative_bound,
                "exact_stratum_gap",
                "strict_margin",
            ),
            "gauged_G3_SU5_max_negative_pure_Delta_full_residual_gap_closed": (
                su5_max_negative_full_residual_pure_delta_closed
            ),
            "gauged_G3_SU5_max_negative_pure_Delta_full_residual_minimum": (
                max_negative_full_scope.get("restricted_gap_global_minimum")
            ),
            "gauged_G3_SU5_max_negative_rank1_SU3_four_dimensional_slice_closed": (
                su5_max_negative_rank1_su3_four_dimensional_slice_closed
            ),
            "gauged_G3_SU5_max_negative_rank1_SU3_slice_dimension": (
                rank1_su3_scope.get("Phi_slice_real_dimension")
            ),
            "gauged_G3_SU5_max_negative_rank1_SU3_ambient_dimension": (
                rank1_su3_scope.get("full_SU3_fixed_space_real_dimension")
            ),
            "gauged_G3_SU5_max_negative_rank1_SU3_slice_minimum": _dig(
                rank1_su3_bound,
                "radial_patch",
                "restricted_global_minimum",
            ),
            "gauged_G3_SU5_max_negative_arbitrary_rank1_Phi_open": not bool(
                rank1_su3_checks.get("arbitrary_rank1_Phi_proved")
            ),
            "gauged_G3_rank1_SU4_stabilizer_infrastructure_exact": (
                rank1_su4_stabilizer_infrastructure_exact
            ),
            "gauged_G3_rank1_SU4_joint_stabilizer_dimension": _dig(
                rank1_su4_stabilizer,
                "joint_stabilizer_tangent",
                "exact_tangent_nullity",
            ),
            "gauged_G3_rank1_SU4_Phi210_intertwiner_infrastructure_exact": (
                rank1_su4_phi210_intertwiners_exact
            ),
            "gauged_G3_rank1_SU4_Phi210_carrier_count": _dig(
                rank1_su4_intertwiners,
                "carriers",
                "carrier_count",
            ),
            "gauged_G3_rank1_SU4_Sym2_invariant_dimension": _dig(
                rank1_su4_intertwiners,
                "carriers",
                "Sym2_Phi210_SU4_singlet_dimension",
            ),
            "gauged_G3_rank1_SU4_aligned_carriers_exact": (
                rank1_su4_aligned_carriers_exact
            ),
            "gauged_G3_rank1_SU4_aligned_direct_sum_rank": _dig(
                rank1_su4_aligned,
                "alignment", "concatenated_aligned_basis_rank_mod_prime",
            ),
            "gauged_G3_rank1_SU4_physical_real_maps_exact": _dig(
                rank1_su4_aligned,
                "scope",
                "physical_real_structure_and_Gaussian_embeddings_constructed",
            ),
            "gauged_G3_rank1_SU4_Phi210_quadratic_basis_exact": (
                rank1_su4_phi210_quadratic_basis_exact
            ),
            "gauged_G3_rank1_SU4_quadratic_constraint_shape": _dig(
                rank1_su4_quadratic,
                "constraint_system", "reduced_constraint_shape",
            ),
            "gauged_G3_rank1_SU4_quadratic_constraint_rank": _dig(
                rank1_su4_quadratic,
                "constraint_system", "exact_rational_rank",
            ),
            "gauged_G3_rank1_SU4_quadratic_constraint_nullity": _dig(
                rank1_su4_quadratic,
                "constraint_system", "exact_rational_nullity",
            ),
            "gauged_G3_rank1_SU4_quadratic_basis_count": _dig(
                rank1_su4_quadratic,
                "quadratic_basis", "matrix_count",
            ),
            "gauged_G3_rank1_SU4_quadratic_basis_rank": _dig(
                rank1_su4_quadratic,
                "quadratic_basis", "upper_triangle_column_rank_mod_prime",
            ),
            "gauged_G3_rank1_SU4_quadratic_live_invariance_exact": _dig(
                rank1_su4_quadratic,
                "quadratic_basis",
                "all_45_commute_with_all_15_live_Phi210_generators_exact",
            ),
            "gauged_G3_rank1_SU4_Schur_SOS_SDP_open": (
                rank1_su4_quadratic_scope.get(
                    "augmented_homogeneous_Schur_SOS_SDP_constructed"
                ) is False
            ),
            "gauged_G3_rank1_SU4_arbitrary_Phi_bound_open": (
                rank1_su4_quadratic_scope.get("arbitrary_rank1_Phi_proved")
                is False
            ),
            "gauged_G3_rank1_SU4_augmented_SOS_census_exact": (
                rank1_su4_augmented_sos_census_exact
            ),
            "gauged_G3_rank1_SU4_augmented_homogeneous_dimension": _dig(
                rank1_su4_census,
                "augmented_representation", "augmented_homogeneous_dimension",
            ),
            "gauged_G3_rank1_SU4_augmented_isotypic_type_count": _dig(
                rank1_su4_census,
                "augmented_representation", "complex_isotypic_type_count",
            ),
            "gauged_G3_rank1_SU4_augmented_irreducible_copy_count": _dig(
                rank1_su4_census,
                "augmented_representation", "complex_irreducible_copy_count",
            ),
            "gauged_G3_rank1_SU4_augmented_real_block_count": _dig(
                rank1_su4_census,
                "augmented_representation", "real_isotypic_block_count",
            ),
            "gauged_G3_rank1_SU4_augmented_Schur_parameter_count": _dig(
                rank1_su4_census,
                "augmented_representation", "Schur_real_parameter_count",
            ),
            "gauged_G3_rank1_SU4_augmented_invariant_row_count": _dig(
                rank1_su4_census,
                "invariant_quartic_target", "invariant_equation_count",
            ),
            "gauged_G3_rank1_SU4_augmented_abstract_rank": _dig(
                rank1_su4_census,
                "abstract_coefficient_map_census", "abstract_total_rank_exact",
            ),
            "gauged_G3_rank1_SU4_augmented_coordinate_Schur_map_open": (
                rank1_su4_census_scope.get(
                    "Schur_coordinate_6585_by_19594_coefficient_matrix_constructed"
                ) is False
            ),
            "gauged_G3_rank1_SU4_augmented_isotypic_maps_open": (
                rank1_su4_census_scope.get(
                    "all_35_isotypic_type_maps_spanning_824_irreducible_copies_constructed"
                ) is False
            ),
            "gauged_G3_rank1_SU4_augmented_physical_target_open": (
                rank1_su4_census_scope.get(
                    "physical_G3_gap_target_vector_constructed"
                ) is False
                and rank1_su4_census_scope.get(
                    "physical_G3_gap_cubic_zero_RHS_certified"
                ) is False
            ),
            "gauged_G3_rank1_SU4_augmented_SDP_open": (
                rank1_su4_census_scope.get(
                    "augmented_Schur_SOS_SDP_constructed"
                ) is False
                and rank1_su4_census_scope.get(
                    "augmented_Schur_SOS_SDP_feasibility_certified"
                ) is False
                and rank1_su4_census_scope.get(
                    "augmented_Schur_SOS_SDP_infeasibility_certified"
                ) is False
            ),
            "gauged_G3_rank1_SU4_augmented_arbitrary_Phi_open": (
                rank1_su4_census_scope.get(
                    "arbitrary_real_Phi_lower_bound_proved"
                ) is False
                and rank1_su4_census_scope.get("arbitrary_rank1_Phi_proved")
                is False
            ),
            "gauged_G3_rank1_SU4_augmented_G3_open": (
                rank1_su4_census_scope.get("G3_closed") is False
                and rank1_su4_census_scope.get("whole_model_validated") is False
                and rank1_su4_census_scope.get("whole_model_excluded") is False
            ),
            "gauged_G3_rank1_SU4_augmented_cubic_map_exact": (
                rank1_su4_augmented_sos_cubic_map_exact
            ),
            "gauged_G3_rank1_SU4_augmented_cubic_carrier_copy_count": _dig(
                rank1_su4_cubic,
                "Sym2_target_carriers", "total_complex_carrier_copy_count",
            ),
            "gauged_G3_rank1_SU4_augmented_cubic_real_variable_count": _dig(
                rank1_su4_cubic,
                "physical_cubic_domain", "physical_basis_count",
            ),
            "gauged_G3_rank1_SU4_augmented_cubic_nonzero_block_count": _dig(
                rank1_su4_cubic,
                "physical_cubic_domain", "nonzero_cubic_block_count",
            ),
            "gauged_G3_rank1_SU4_augmented_cubic_map_shape": (
                rank1_su4_cubic_map.get("coordinate_map_shape")
            ),
            "gauged_G3_rank1_SU4_augmented_cubic_map_nnz": (
                rank1_su4_cubic_map.get("coordinate_map_nnz")
            ),
            "gauged_G3_rank1_SU4_augmented_cubic_map_rank": (
                rank1_su4_cubic_map.get("exact_rank")
            ),
            "gauged_G3_rank1_SU4_augmented_cubic_map_kernel_dimension": (
                rank1_su4_cubic_map.get("exact_kernel_dimension")
            ),
            "gauged_G3_rank1_SU4_augmented_cubic_zero_placeholder_nonphysical": (
                rank1_su4_cubic_map.get(
                    "abstract_zero_placeholder_is_not_a_physical_G3_target"
                ) is True
                and rank1_su4_cubic_map.get(
                    "physical_G3_gap_target_vector_constructed"
                ) is False
                and rank1_su4_cubic_map.get(
                    "physical_G3_gap_cubic_zero_RHS_certified"
                ) is False
            ),
            "gauged_G3_rank1_SU4_augmented_cubic_other_maps_open": all(
                rank1_su4_cubic_scope.get(name) is False
                for name in (
                    "degree_zero_coefficient_map_constructed",
                    "degree_one_coefficient_map_constructed",
                    "degree_two_coefficient_map_constructed",
                    "degree_four_coefficient_map_constructed",
                    "full_6585_by_19594_Schur_coordinate_matrix_constructed",
                )
            ),
            "gauged_G3_rank1_SU4_augmented_cubic_physical_target_open": (
                rank1_su4_cubic_scope.get(
                    "physical_G3_gap_target_vector_constructed"
                ) is False
                and rank1_su4_cubic_scope.get(
                    "physical_G3_gap_cubic_zero_RHS_certified"
                ) is False
            ),
            "gauged_G3_rank1_SU4_augmented_cubic_SDP_open": all(
                rank1_su4_cubic_scope.get(name) is False
                for name in (
                    "augmented_Schur_SOS_SDP_constructed",
                    "augmented_Schur_SOS_SDP_feasibility_certified",
                    "augmented_Schur_SOS_SDP_infeasibility_certified",
                )
            ),
            "gauged_G3_rank1_SU4_augmented_cubic_arbitrary_Phi_open": (
                rank1_su4_cubic_scope.get(
                    "arbitrary_real_Phi_lower_bound_proved"
                ) is False
                and rank1_su4_cubic_scope.get("arbitrary_rank1_Phi_proved")
                is False
            ),
            "gauged_G3_rank1_SU4_augmented_cubic_G3_open": (
                rank1_su4_cubic_scope.get("G3_closed") is False
                and rank1_su4_cubic_scope.get("whole_model_validated") is False
                and rank1_su4_cubic_scope.get("whole_model_excluded") is False
            ),
            "gauged_G3_rank1_SU4_augmented_quartic_map_exact": (
                rank1_su4_augmented_sos_quartic_map_exact
            ),
            "gauged_G3_rank1_SU4_augmented_quartic_carrier_family_count": _dig(
                rank1_su4_quartic, "dimensions", "complex_isotypic_types",
            ),
            "gauged_G3_rank1_SU4_augmented_quartic_irreducible_copy_count": _dig(
                rank1_su4_quartic, "dimensions", "irreducible_copies",
            ),
            "gauged_G3_rank1_SU4_augmented_quartic_real_block_count": _dig(
                rank1_su4_quartic, "dimensions", "real_Schur_blocks",
            ),
            "gauged_G3_rank1_SU4_augmented_quartic_map_shape": (
                rank1_su4_quartic_map.get("shape")
            ),
            "gauged_G3_rank1_SU4_augmented_quartic_map_nnz": (
                rank1_su4_quartic_map.get("nnz")
            ),
            "gauged_G3_rank1_SU4_augmented_quartic_map_rank": (
                rank1_su4_quartic_map.get("rank_over_Q_exact")
            ),
            "gauged_G3_rank1_SU4_augmented_quartic_map_kernel_dimension": (
                rank1_su4_quartic_map.get("kernel_dimension_over_Q_exact")
            ),
            "gauged_G3_rank1_SU4_augmented_quartic_physical_target_open": (
                rank1_su4_quartic_scope.get(
                    "physical_quartic_target_constructed"
                ) is False
            ),
            "gauged_G3_rank1_SU4_augmented_quartic_standard_PSD_congruences_open": (
                rank1_su4_quartic_scope.get(
                    "standard_PSD_congruences_for_real_type_fixed_bases_constructed"
                ) is False
            ),
            "gauged_G3_rank1_SU4_augmented_quartic_SDP_open": (
                rank1_su4_quartic_scope.get("semidefinite_feasibility_solved")
                is False
            ),
            "gauged_G3_rank1_SU4_augmented_quartic_arbitrary_Phi_open": (
                rank1_su4_quartic_scope.get(
                    "arbitrary_Phi_stationarity_or_lower_bound_proved"
                ) is False
            ),
            "gauged_G3_rank1_SU4_augmented_quartic_G3_open": (
                rank1_su4_quartic_scope.get("G3_closed") is False
            ),
            "gauged_G3_rank1_SU4_legacy_v20_PSD_routes_and_stale_payload_well_formed": (
                rank1_su4_legacy_psd_routes_and_stale_payload_well_formed
            ),
            "gauged_G3_rank1_SU4_legacy_v20_physical_target_valid": False,
            "gauged_G3_rank1_SU4_legacy_v20_primal_valid": False,
            "gauged_G3_rank1_SU4_augmented_standard_PSD_route_count": (
                rank1_su4_psd_routes.get("real_type_block_count", 0)
                + rank1_su4_psd_routes.get("complex_Hermitian_block_count", 0)
            ),
            "gauged_G3_rank1_SU4_augmented_standard_PSD_parameter_count": (
                rank1_su4_psd_routes.get("standard_total_parameter_count")
            ),
            "gauged_G3_rank1_SU4_augmented_real_type_PSD_congruences_exact": (
                rank1_su4_psd_target_scope.get(
                    "all_nine_real_type_standard_PSD_congruences_constructed"
                ) is True
            ),
            "gauged_G3_rank1_SU4_augmented_complex_Hermitian_coordinates_exact": (
                rank1_su4_psd_target_scope.get(
                    "all_thirteen_complex_blocks_in_standard_Hermitian_coordinates"
                ) is True
            ),
            "gauged_G3_rank1_SU4_corrected_fixed_endpoint_theorem_exact": (
                rank1_su4_corrected_exact
            ),
            "gauged_G3_rank1_SU4_corrected_positive_Gram_map_shape": (
                rank1_su4_corrected_view.get("map_shape")
            ),
            "gauged_G3_rank1_SU4_corrected_positive_Gram_map_common_denominator": (
                rank1_su4_corrected_view.get("map_common_denominator")
            ),
            "gauged_G3_rank1_SU4_corrected_positive_Gram_map_nnz": (
                rank1_su4_corrected_view.get("map_nnz")
            ),
            "gauged_G3_rank1_SU4_corrected_positive_Gram_map_sha256": (
                rank1_su4_corrected_view.get("map_numerator_csr_sha256")
            ),
            "gauged_G3_rank1_SU4_corrected_physical_target_common_denominator": (
                rank1_su4_corrected_view.get("target_common_denominator")
            ),
            "gauged_G3_rank1_SU4_corrected_physical_target_nonzero_count": (
                rank1_su4_corrected_view.get("target_nonzero_count")
            ),
            "gauged_G3_rank1_SU4_corrected_physical_target_sha256": (
                rank1_su4_corrected_view.get("target_numerator_sha256")
            ),
            "gauged_G3_rank1_SU4_corrected_exact_coefficient_equalities": (
                rank1_su4_corrected_view.get("exact_coefficient_equalities")
            ),
            "gauged_G3_rank1_SU4_corrected_strict_positive_Gram_blocks": (
                rank1_su4_corrected_view.get("strict_positive_Gram_blocks")
            ),
            "gauged_G3_rank1_SU4_corrected_strict_positive_LDL_pivots": (
                rank1_su4_corrected_view.get("strict_positive_LDL_pivots")
            ),
            "gauged_G3_rank1_SU4_corrected_arbitrary_real_Phi_at_fixed_endpoint": (
                rank1_su4_corrected_view.get(
                    "arbitrary_real_Phi_at_fixed_endpoint"
                )
            ),
            "gauged_G3_rank1_SU4_corrected_p_zero_set_at_t1_empty": (
                rank1_su4_corrected_view.get("p_zero_set_at_t1_empty")
            ),
            "gauged_G3_rank1_SU4_corrected_global_Sigma_proved": False,
            "gauged_G3_rank1_SU4_corrected_general_H_proved": False,
            "gauged_G3_rank1_SU4_corrected_full_Hessian_proved": False,
            "gauged_G3_rank1_SU4_corrected_G3_closed": False,
            "gauged_G3_SU5_max_negative_arbitrary_Sigma_orientation_open": not bool(
                rank1_su3_scope.get("arbitrary_max_negative_Sigma")
            ),
            "gauged_G3_SU5_arbitrary_Phi_nonzero_residual_cancellations_open": (
                not bool(
                    max_negative_full_scope.get(
                        "nonzero_Phi_Sigma_residuals_covered"
                    )
                    and max_negative_full_scope.get(
                        "nonzero_chiral_Phi_H_residual_covered"
                    )
                )
            ),
            "gauged_G3_SU5_arbitrary_Phi_uniform_coercivity_open": not bool(
                max_negative_full_scope.get("arbitrary_Sigma_orientation_proved")
            ),
            "gauged_G3_SU5_arbitrary_non_pure_Delta_Sigma_coercivity_open": not bool(
                max_negative_full_scope.get("arbitrary_Sigma_orientation_proved")
            ),
            "gauged_G3_alternative_global_SOS_honestly_open": (
                alternative_global_sos_honestly_open
            ),
            "gauged_G3_all_vanishing_global_SOS_routes_excluded": bool(
                alternative_sos_flags.get(
                    "all_vanishing_45_current_Gram_completion_excluded"
                )
                and alternative_sos_flags.get(
                    "all_vanishing_affine_SOS_completion_excluded"
                )
                and alternative_sos_flags.get(
                    "all_vanishing_unique_chiral_quartic_completion_excluded"
                )
            ),
            "gauged_G3_SU5_beta_1_over_20_global_certified": (
                su5_gap_flags.get("beta_1_over_20_global_minimum_certified")
            ),
            "gauged_G3_final_acceptance_test_passes": su5_gap_acceptance.get(
                "currently_passes"
            ),
            "final_G3_acceptance_gate_honestly_open": final_g3_honestly_open,
            "gauged_G3_contract_and_coverage_bound": gauged_g3_contract_bound,
            "gauged_G3_direction_parameter_field_quotient_counts": [
                gauged_coverage.get("invariant_directions"),
                gauged_coverage.get("real_parameters"),
                gauged_coverage.get("real_field_dimension"),
                gauged_coverage.get("gauge_quotient_dimension_including_axion"),
                gauged_coverage.get("massive_transverse_quotient_dimension"),
            ],
            "gauged_G3_gauge_quotient_dimension_449_certified": bool(
                gauged_g3_contract_bound
                and gauged_flags.get(
                    "gauge_quotient_dimension_449_including_axion_certified"
                )
            ),
            "gauged_G3_massive_transverse_dimension_448_certified": bool(
                gauged_g3_contract_bound
                and gauged_flags.get(
                    "massive_transverse_quotient_dimension_448_certified"
                )
            ),
            "gauged_G3_legacy_physical_quotient_448_alias_present": bool(
                gauged_flags.get("physical_quotient_dimension_448_certified")
            ),
            "gauged_G3_stationarity_rank_13_exactly_certified": (
                exact_stationarity_rank
            ),
            "gauged_model_wide_no_go_certified": model_wide_no_go,
            "gauged_strict_local_physical_minimum": stable_quotient,
            "gauged_complete_BFB": bfb,
            "gauged_global_comparison_complete": global_minimum,
            "historical_option_c_stationarity_authoritative": reports.get(
                "g3_stationarity", {}
            ).get("authoritative_for_manuscript", False),
            "historical_option_c_hessian_authoritative": reports.get(
                "g3_hessian", {}
            ).get("authoritative_for_manuscript", False),
            "historical_option_c_search_authoritative": reports.get(
                "g3_search", {}
            ).get("authoritative_for_manuscript", False),
        },
        (
            "A proof-grade no-go shows no BFB stationary vacuum in the complete "
            "gauged scalar theory realizes the required breaking chain."
        ),
        (
            "Complete minimization, Hessian/tachyon tests, Goldstone counting, "
            "global-or-metastable vacuum comparison, authoritative G3-G6 closure, "
            "and a complete source-bound physical scalar spectrum all pass."
        ),
    )


def _rge_gate(
    reports: dict[str, dict[str, Any]],
    eft_g7_nonidentifiability: dict[str, Any] | None = None,
    g6_sm_provenance: dict[str, Any] | None = None,
    g6_g7_parameterized_matching: dict[str, Any] | None = None,
    authoritative_gauge_betas: dict[str, Any] | None = None,
    pyrate3_gauge_replay: dict[str, Any] | None = None,
    physical_g7_component_threshold: dict[str, Any] | None = None,
    normalized_yukawa_cgcs: dict[str, Any] | None = None,
    physical_sm_heavy_vectors: dict[str, Any] | None = None,
    physical_sm_heavy_vector_msbar: dict[str, Any] | None = None,
    physical_sm_vector_rxi: dict[str, Any] | None = None,
    conditional_physical_sm_scalar_spectrum: dict[str, Any] | None = None,
    physical_sm_g6_g7_closure_frontier: dict[str, Any] | None = None,
    physical_g7_recalculated_inputs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rge = reports.get("rge", {})
    flags = rge.get("flag", {})
    chain = bool(flags.get("piecewise_yukawa_chain_integrated"))
    clebsch = bool(flags.get("clebsch_threshold_matching_implemented"))
    full_two_loop = bool(flags.get("two_loop_so10_complete"))
    tensors = bool(flags.get("published_210_tensor_contractions"))
    component_matching = bool(
        flags.get("piecewise_component_threshold_matching_complete")
    )
    if eft_g7_nonidentifiability is None:
        eft_g7_nonidentifiability = {}
    if g6_sm_provenance is None:
        g6_sm_provenance = {}
    if g6_g7_parameterized_matching is None:
        g6_g7_parameterized_matching = {}
    if authoritative_gauge_betas is None:
        authoritative_gauge_betas = {}
    if pyrate3_gauge_replay is None:
        pyrate3_gauge_replay = {}
    if physical_g7_component_threshold is None:
        physical_g7_component_threshold = {}
    if normalized_yukawa_cgcs is None:
        normalized_yukawa_cgcs = {}
    if physical_sm_heavy_vectors is None:
        physical_sm_heavy_vectors = {}
    if physical_sm_heavy_vector_msbar is None:
        physical_sm_heavy_vector_msbar = {}
    if physical_sm_vector_rxi is None:
        physical_sm_vector_rxi = {}
    if conditional_physical_sm_scalar_spectrum is None:
        conditional_physical_sm_scalar_spectrum = {}
    if physical_sm_g6_g7_closure_frontier is None:
        physical_sm_g6_g7_closure_frontier = {}
    if physical_g7_recalculated_inputs is None:
        physical_g7_recalculated_inputs = {}
    physical_g6_mismatch = bool(
        g6_sm_provenance.get("source_bound") is True
        and g6_sm_provenance.get("formal_tree_mass_factorization_valid") is True
        and g6_sm_provenance.get("actual_residual_group")
        == "SU(3)_C x U(1)_89"
        and g6_sm_provenance.get("physical_U1em_provenance_complete") is False
        and g6_sm_provenance.get("physical_mathematical_G6_closed") is False
    )
    formal_matching_bound = bool(
        g6_g7_parameterized_matching.get("source_bound") is True
        and g6_g7_parameterized_matching.get(
            "formal_SU3_x_U1_89_threshold_determinants_complete"
        )
        is True
        and g6_g7_parameterized_matching.get(
            "physical_SM_scalar_thresholds_identified"
        )
        is False
        and g6_g7_parameterized_matching.get("mathematical_G7_closed") is False
    )
    gauge_only_subtheorem_bound = bool(
        authoritative_gauge_betas.get("source_bound") is True
        and authoritative_gauge_betas.get(
            "exact_nonyukawa_two_loop_gauge_polynomial_closed"
        )
        is True
        and authoritative_gauge_betas.get("full_two_loop_gauge_beta_closed") is False
        and authoritative_gauge_betas.get("component_threshold_matching_closed")
        is False
        and authoritative_gauge_betas.get("mathematical_G7_closed") is False
    )
    independent_gauge_replay_bound = bool(
        pyrate3_gauge_replay.get("source_bound") is True
        and pyrate3_gauge_replay.get(
            "second_implementation_for_scoped_gauge_subtheorem"
        )
        is True
        and pyrate3_gauge_replay.get("full_two_loop_gauge_beta_closed") is False
        and pyrate3_gauge_replay.get("mathematical_G7_closed") is False
    )
    physical_component_kernel_bound = bool(
        physical_g7_component_threshold.get("source_bound") is True
        and physical_g7_component_threshold.get(
            "physical_PS_SM_matter_branching_closed"
        )
        is True
        and physical_g7_component_threshold.get(
            "parameterized_one_loop_matter_threshold_kernel_closed"
        )
        is True
        and physical_g7_component_threshold.get(
            "exact_two_loop_nonyukawa_gauge_flow_closed"
        )
        is True
        and physical_g7_component_threshold.get(
            "physical_component_pole_mass_matrices_closed"
        )
        is False
        and physical_g7_component_threshold.get("heavy_vector_matching_closed")
        is False
        and physical_g7_component_threshold.get("physical_G7_closed") is False
        and physical_g7_component_threshold.get("mathematical_G7_closed") is False
        and physical_g7_component_threshold.get("release_G7_verified") is False
        and physical_g7_component_threshold.get(
            "authoritative_renormalizable_G7_closed"
        )
        is False
    )
    normalized_yukawa_cgcs_bound = bool(
        normalized_yukawa_cgcs.get("source_bound") is True
        and normalized_yukawa_cgcs.get("normalized_10_CGCs_closed") is True
        and normalized_yukawa_cgcs.get("normalized_126bar_CGCs_closed") is True
        and normalized_yukawa_cgcs.get(
            "normalized_singlet_duality_CGC_closed"
        )
        is True
        and normalized_yukawa_cgcs.get(
            "canonical_304_Weyl_sparse_embedding_closed"
        )
        is True
        and normalized_yukawa_cgcs.get("all_declared_representation_CGCs_closed")
        is True
        and normalized_yukawa_cgcs.get("flavor_boundary_values_closed") is False
        and normalized_yukawa_cgcs.get("SARAH_Dot_conversion_closed") is False
        and normalized_yukawa_cgcs.get("full_one_two_loop_Yukawa_betas_closed")
        is False
        and normalized_yukawa_cgcs.get(
            "physical_threshold_matching_and_running_closed"
        )
        is False
        and normalized_yukawa_cgcs.get("physical_G7_closed") is False
        and normalized_yukawa_cgcs.get("mathematical_G7_closed") is False
        and normalized_yukawa_cgcs.get("release_G7_verified") is False
    )
    heavy_vector_tree_inputs_bound = bool(
        physical_sm_heavy_vectors.get("source_bound") is True
        and physical_sm_heavy_vectors.get(
            "exact_parameterized_tree_vector_mass_matrix_closed"
        )
        is True
        and physical_sm_heavy_vectors.get(
            "exact_vector_rank_kernel_and_Goldstone_image_closed"
        )
        is True
        and physical_sm_heavy_vectors.get(
            "exact_SU3C_x_U1em_vector_sector_resolution_closed"
        )
        is True
        and physical_sm_heavy_vectors.get(
            "parameterized_vector_threshold_log_inputs_closed"
        )
        is True
        and physical_sm_heavy_vectors.get(
            "vector_Goldstone_ghost_matching_closed"
        )
        is False
        and physical_sm_heavy_vectors.get("pole_vector_masses_closed") is False
        and physical_sm_heavy_vectors.get("physical_G7_closed") is False
    )
    heavy_vector_msbar_inputs_bound = bool(
        physical_sm_heavy_vector_msbar.get("source_bound") is True
        and physical_sm_heavy_vector_msbar.get(
            "combined_heavy_vector_FPghost_Goldstone_MSbar_kernel_closed"
        )
        is True
        and physical_sm_heavy_vector_msbar.get(
            "finite_MSbar_vector_constant_closed"
        )
        is True
        and physical_sm_heavy_vector_msbar.get(
            "exact_SU3_and_physical_QED_group_factors_closed"
        )
        is True
        and physical_sm_heavy_vector_msbar.get(
            "Goldstone_double_count_guard_active"
        )
        is True
        and physical_sm_heavy_vector_msbar.get(
            "arbitrary_Rxi_sector_resolved_matching_closed"
        )
        is False
        and physical_sm_heavy_vector_msbar.get("pole_mass_conversion_closed")
        is False
        and physical_sm_heavy_vector_msbar.get(
            "SM_symmetric_pre_EW_matching_closed"
        )
        is False
        and physical_sm_heavy_vector_msbar.get(
            "complete_scalar_fermion_threshold_matching_closed"
        )
        is False
        and physical_sm_heavy_vector_msbar.get(
            "complete_one_loop_model_matching_closed"
        )
        is False
        and physical_sm_heavy_vector_msbar.get("physical_G6_closed") is False
        and physical_sm_heavy_vector_msbar.get("physical_G7_closed") is False
    )
    vector_rxi_vacuum_bound = bool(
        physical_sm_vector_rxi.get("source_bound") is True
        and physical_sm_vector_rxi.get(
            "zero_background_Rxi_vacuum_determinant_cancellation_closed"
        )
        is True
        and physical_sm_vector_rxi.get("all_37_broken_directions_closed")
        is True
        and physical_sm_vector_rxi.get(
            "Goldstone_FPghost_double_count_guard_closed"
        )
        is True
        and physical_sm_vector_rxi.get(
            "background_covariant_heat_kernel_matching_closed"
        )
        is False
        and physical_sm_vector_rxi.get(
            "sector_resolved_general_background_determinants_closed"
        )
        is False
        and physical_sm_vector_rxi.get("pole_vector_masses_closed") is False
        and physical_sm_vector_rxi.get("physical_G6_closed") is False
        and physical_sm_vector_rxi.get("physical_G7_closed") is False
    )
    conditional_scalar_tree_inputs_bound = bool(
        conditional_physical_sm_scalar_spectrum.get("source_bound") is True
        and conditional_physical_sm_scalar_spectrum.get(
            "conditional_reconstructed_tree_scalar_spectrum_closed"
        )
        is True
        and conditional_physical_sm_scalar_spectrum.get(
            "source_algebra_derived_tree_scalar_spectrum_closed"
        )
        is False
        and conditional_physical_sm_scalar_spectrum.get(
            "physical_scalar_pole_spectrum_closed"
        )
        is False
    )
    physical_g6_g7_frontier_bound = bool(
        physical_sm_g6_g7_closure_frontier.get("source_bound") is True
        and physical_sm_g6_g7_closure_frontier.get(
            "corrected_terminal_artifacts_composed"
        )
        is True
        and physical_sm_g6_g7_closure_frontier.get(
            "continuous_nonidentifiability_proved"
        )
        is True
        and physical_sm_g6_g7_closure_frontier.get(
            "minimal_closure_path_machine_readable"
        )
        is True
        and len(
            physical_sm_g6_g7_closure_frontier.get(
                "minimal_closure_path", []
            )
        )
        == 7
        and physical_sm_g6_g7_closure_frontier.get("unique_pole_spectrum")
        is False
        and physical_sm_g6_g7_closure_frontier.get("unique_threshold_vector")
        is False
        and physical_sm_g6_g7_closure_frontier.get(
            "unique_full_RGE_trajectory"
        )
        is False
        and physical_sm_g6_g7_closure_frontier.get("physical_G6_closed")
        is False
        and physical_sm_g6_g7_closure_frontier.get("physical_G7_closed")
        is False
    )
    recalculated_inputs_bound = bool(
        physical_g7_recalculated_inputs.get("source_bound") is True
        and physical_g7_recalculated_inputs.get(
            "all_resolved_scoped_inputs_closed"
        )
        is True
        and all(
            physical_g7_recalculated_inputs.get(
                "superseded_stale_blockers", {}
            ).values()
        )
        and all(
            value is False
            for value in physical_g7_recalculated_inputs.get(
                "precise_open_inputs", {}
            ).values()
        )
        and physical_g7_recalculated_inputs.get("physical_G7_closed") is False
    )
    formal_U1_89_restriction_audit = bool(
        eft_g7_nonidentifiability.get("source_bound") is True
        and eft_g7_nonidentifiability.get(
            "formal_U1_89_abstract_restriction_noninjectivity_proved"
        )
        is True
        and eft_g7_nonidentifiability.get(
            "exact_physical_EFT_G7_input_nonidentifiability_proved"
        )
        is False
        and eft_g7_nonidentifiability.get(
            "historical_electroweak_lift_interpretation_valid"
        )
        is False
        and eft_g7_nonidentifiability.get(
            "formal_U1_89_restriction_map_noninjective"
        )
        is True
        and eft_g7_nonidentifiability.get("absolute_scale_unidentified") is True
        and eft_g7_nonidentifiability.get("mathematical_EFT_G7_closed") is False
        and eft_g7_nonidentifiability.get("positive_G7_certified") is False
        and eft_g7_nonidentifiability.get("negative_G7_no_go_certified") is False
        and eft_g7_nonidentifiability.get("EFT_release_G7_verified") is False
        and eft_g7_nonidentifiability.get(
            "authoritative_renormalizable_G7_closed"
        )
        is False
        and eft_g7_nonidentifiability.get("downstream_integration_completed")
        is True
    )
    if physical_g6_mismatch:
        state = "BLOCKED"
    elif formal_U1_89_restriction_audit:
        state = "BLOCKED"
    elif full_two_loop and tensors and component_matching:
        state = "PASS"
    elif chain and clebsch:
        state = "CONDITIONAL"
    else:
        state = "OPEN"
    return _gate(
        "two_loop_RGE_unification_and_thresholds",
        state,
        (
            "The exact provenance audit proves the frozen G6 abelian stabilizer "
            "is U(1)_89 rather than physical electromagnetism, so its formal "
            "threshold determinants cannot be consumed as SM input. The corrected "
            "physical PS/SM matter branching, parameterized one-loop matter kernel "
            "and gauge-only one/two-loop polynomial are exact. Normalized SO(10) "
            "10/126bar/singlet representation Yukawa CGCs, the canonical 304-Weyl "
            "embedding, parameterized physical-SM heavy-vector tree masses, "
            "rank/kernel, sectors and threshold logs, and the combined heavy-vector "
            "+ FP-ghost + Goldstone non-SUSY MSbar kernel including its finite "
            "constant are also exact. The zero-background vacuum determinant "
            "cancellation is exact for arbitrary positive Rxi in all 37 broken "
            "directions, while continuous scale and flavor witnesses prove the "
            "remaining full output is not identified. Flavor tensors/boundaries, SARAH "
            "identical-Weyl contraction conversion, the Yukawa/scalar/EFT beta "
            "system, background-covariant general-field determinants and heat-kernel "
            "replay, tree-to-pole "
            "masses with a tadpole/VEV scheme, the stationary pre-EW matching stage, "
            "and complete scalar/fermion thresholds remain open."
            if physical_g6_mismatch
            else "The exact EFT G7 audit proves that the frozen G6 residual spectrum "
            "does not identify electroweak threshold representations or the "
            "absolute matching scale. Published SO(10)+210 two-loop tensors, "
            "running VEVs, and component thresholds also remain open."
            if formal_U1_89_restriction_audit
            else "A diagnostic one-loop Pati-Salam/2HDM chain with the -3 lepton "
            "Clebsch is integrated. Published SO(10)+210 two-loop tensor "
            "contractions, running VEVs, and component thresholds remain open."
        ),
        {
            "piecewise_chain_integrated": chain,
            "clebsch_matching": clebsch,
            "published_210_tensor_contractions": tensors,
            "two_loop_so10_complete": full_two_loop,
            "component_threshold_matching_complete": component_matching,
            "G6_physical_stabilizer_mismatch_proved": physical_g6_mismatch,
            "G6_actual_residual_group": g6_sm_provenance.get(
                "actual_residual_group"
            ),
            "formal_SU3_x_U1_89_threshold_determinants_complete": (
                formal_matching_bound
            ),
            "authoritative_gauge_only_RGE_subtheorem_closed": (
                gauge_only_subtheorem_bound
            ),
            "independent_PyRATE3_gauge_only_replay_closed": (
                independent_gauge_replay_bound
            ),
            "physical_PS_SM_matter_branching_closed": bool(
                physical_component_kernel_bound
            ),
            "parameterized_one_loop_matter_threshold_kernel_closed": bool(
                physical_component_kernel_bound
            ),
            "normalized_SO10_10_CGCs_closed": bool(
                normalized_yukawa_cgcs_bound
            ),
            "normalized_SO10_126bar_CGCs_closed": bool(
                normalized_yukawa_cgcs_bound
            ),
            "normalized_SO10_singlet_duality_CGC_closed": bool(
                normalized_yukawa_cgcs_bound
            ),
            "canonical_304_Weyl_sparse_Yukawa_embedding_closed": bool(
                normalized_yukawa_cgcs_bound
            ),
            "exact_parameterized_heavy_vector_tree_mass_matrix_closed": bool(
                heavy_vector_tree_inputs_bound
            ),
            "exact_heavy_vector_physical_target_provenance_closed": bool(
                heavy_vector_tree_inputs_bound
            ),
            "exact_heavy_vector_rank_kernel_and_sector_resolution_closed": bool(
                heavy_vector_tree_inputs_bound
            ),
            "parameterized_heavy_vector_threshold_log_inputs_closed": bool(
                heavy_vector_tree_inputs_bound
            ),
            "combined_heavy_vector_FPghost_Goldstone_MSbar_kernel_closed": bool(
                heavy_vector_msbar_inputs_bound
            ),
            "finite_MSbar_vector_constant_closed": bool(
                heavy_vector_msbar_inputs_bound
            ),
            "exact_heavy_vector_SU3_and_QED_group_factors_closed": bool(
                heavy_vector_msbar_inputs_bound
            ),
            "heavy_vector_Goldstone_double_count_guard_active": bool(
                heavy_vector_msbar_inputs_bound
            ),
            "zero_background_Rxi_vacuum_determinant_cancellation_closed": bool(
                vector_rxi_vacuum_bound
            ),
            "all_37_broken_vector_directions_Rxi_cancelled": bool(
                vector_rxi_vacuum_bound
            ),
            "conditional_reconstructed_tree_scalar_spectrum_closed": bool(
                conditional_scalar_tree_inputs_bound
            ),
            "continuous_G6_G7_nonidentifiability_frontier_closed": bool(
                physical_g6_g7_frontier_bound
            ),
            "G6_G7_minimal_closure_path_machine_readable": bool(
                physical_g6_g7_frontier_bound
            ),
            "recalculated_scoped_G7_input_resolution_bound": bool(
                recalculated_inputs_bound
            ),
            "stale_normalized_embedding_blocker_superseded": bool(
                recalculated_inputs_bound
            ),
            "stale_unmatched_heavy_vector_provenance_blocker_superseded": bool(
                recalculated_inputs_bound
            ),
            "flavor_boundary_values_closed": False,
            "SARAH_Dot_conversion_closed": False,
            "full_one_two_loop_Yukawa_betas_closed": False,
            "physical_component_pole_mass_matrices_closed": False,
            "background_covariant_general_field_Rxi_determinants_closed": False,
            "background_covariant_heat_kernel_replay_closed": False,
            "stationary_SM_symmetric_pre_EW_heavy_vector_matching_closed": False,
            "complete_scalar_and_fermion_threshold_matching_closed": False,
            "physical_vector_pole_masses_closed": False,
            "physical_scalar_pole_masses_closed": False,
            "legacy_quartic_soft_and_heuristic_RGE_threshold_sources_authoritative": False,
            "full_two_loop_gauge_beta_closed": False,
            "formal_U1_89_abstract_restriction_noninjectivity_proved": (
                formal_U1_89_restriction_audit
            ),
            "exact_physical_EFT_G7_input_nonidentifiability_proved": False,
            "historical_electroweak_lift_interpretation_valid": False,
            "formal_U1_89_restriction_map_noninjective": (
                eft_g7_nonidentifiability.get(
                    "formal_U1_89_restriction_map_noninjective"
                )
            ),
            "absolute_matching_scale_unidentified": (
                eft_g7_nonidentifiability.get("absolute_scale_unidentified")
            ),
            "mathematical_G7_closed": False,
            "positive_G7_certified": False,
            "negative_G7_no_go_certified": False,
            "release_G7_verified": False,
            "authoritative_renormalizable_G7_closed": False,
            "positive_closure_requirements": eft_g7_nonidentifiability.get(
                "positive_closure_requirements", []
            ),
        },
        (
            "Every physically allowed threshold spectrum becomes nonperturbative, "
            "fails unification, destabilizes the vacuum, or destroys the flavour fit."
        ),
        (
            "Reference-validated two-loop beta functions and component matching "
            "yield a perturbative, unified, vacuum-consistent common-scale solution."
        ),
    )


def _flavour_gate(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    flavour = reports.get("global_flavour", {})
    best = flavour.get("best_point", {})
    viable = bool(best.get("viable_chi2_lt_30") or flavour.get("any_viable"))
    chi2 = best.get("chi2")
    common_scale = bool(
        _dig(best, "rg_threshold_status", "common_scale_RG_inputs_applied")
    )
    two_loop_coupled = bool(
        _dig(best, "rg_threshold_status", "two_loop_thresholds_coupled")
    )
    if viable and common_scale and two_loop_coupled:
        state = "PASS"
    elif viable:
        state = "CONDITIONAL"
    elif flavour:
        state = "FAIL"
    else:
        state = "OPEN"
    return _gate(
        "global_quark_lepton_neutrino_fit",
        state,
        (
            "A viable low-scale proxy witness exists, including CKM and PMNS "
            "observables, but it is not yet a full common-scale fit coupled to "
            "the completed threshold/RGE system."
        ),
        {
            "viable_proxy_point": viable,
            "best_chi2": chi2,
            "best_chi2_finite": _finite(chi2),
            "common_scale_RG_inputs_applied": common_scale,
            "two_loop_thresholds_coupled": two_loop_coupled,
        },
        "No acceptable simultaneous quark, charged-lepton, neutrino, CKM and PMNS fit exists.",
        (
            "A frozen common-scale fit predicts held-out observables and remains "
            "stable under complete two-loop running and threshold uncertainties."
        ),
    )


def _portal_gate(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    sphere = reports.get("sphere", {})
    counts = _dig(sphere, "scan", "aggregate_counts", default={})
    if not counts:
        counts = sphere.get("aggregate_counts", {})
    excluded = counts.get("n_NA62_excluded")
    surviving = counts.get("n_NA62_surviving")
    total = counts.get("n_total_points")
    posterior = reports.get("posterior", {})
    full_posterior = bool(
        _dig(
            posterior,
            "flag",
            "full_portal_yukawa_posterior_derived",
            default=False,
        )
        or _dig(
            posterior,
            "flag",
            "portal_yukawa_posterior_derived",
            default=False,
        )
    )
    mixed = (
        isinstance(excluded, int)
        and isinstance(surviving, int)
        and excluded > 0
        and surviving > 0
        and isinstance(total, int)
        and excluded + surviving == total
    )
    if mixed and full_posterior:
        state = "PASS"
    elif mixed:
        state = "CONDITIONAL"
    else:
        state = "OPEN"
    return _gate(
        "UV_portal_selection_and_FCNC",
        state,
        (
            "NA62 excludes most sampled fixed-norm orientations but exact "
            "survivors exist. The result is a geometric orientation measure, "
            "not a UV probability; the UV theory has not selected one portal point."
        ),
        {
            "n_total_orientations": total,
            "n_NA62_excluded": excluded,
            "n_NA62_surviving": surviving,
            "mixed_excluded_and_surviving": mixed,
            "full_UV_portal_posterior": full_posterior,
            "geometric_fraction_is_probability": bool(
                counts.get("geometric_fraction_is_uv_probability", False)
            ),
        },
        (
            "The uniquely UV-derived portal point violates NA62, TWIST, meson mixing, "
            "or another channel-level limit."
        ),
        (
            "The UV Lagrangian fixes all portal magnitudes/phases and the resulting "
            "joint FCNC likelihood passes with component-specific currents."
        ),
    )


def _proton_gate(
    reports: dict[str, dict[str, Any]],
    root: Path,
    physical_sm_g8_frontier: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if physical_sm_g8_frontier is None:
        physical_sm_g8_frontier = {}
    frontier_bound = bool(
        physical_sm_g8_frontier.get("source_bound") is True
        and physical_sm_g8_frontier.get("canonical_G8_contract_audited") is True
        and physical_sm_g8_frontier.get(
            "continuous_absolute_scale_nonidentifiability_proved"
        )
        is True
        and physical_sm_g8_frontier.get(
            "flavor_and_interference_nonidentifiability_audited"
        )
        is True
        and physical_sm_g8_frontier.get(
            "repository_frozen_PDG_2025_single_channel_constraint_verified"
        )
        is True
        and physical_sm_g8_frontier.get("unique_proton_lifetime_or_distribution")
        is False
        and physical_sm_g8_frontier.get("physical_G8_closed") is False
        and physical_sm_g8_frontier.get("release_G8_verified") is False
        and physical_sm_g8_frontier.get("authoritative_G8_closed") is False
    )
    proton = _load_json(root / "PROTON_DECAY_V20_VERDICT.json")
    if proton is None:
        state = "BLOCKED" if frontier_bound else "OPEN"
        evidence = {
            "artifact_present": False,
            "gauge_boson_exchange_computed": False,
            "scalar_exchange_computed": False,
            "channel_ratios_computed": False,
            "physical_SM_G8_identifiability_frontier_source_bound": (
                frontier_bound
            ),
            "canonical_G8_contract_audited": physical_sm_g8_frontier.get(
                "canonical_G8_contract_audited", False
            ),
            "absolute_scale_nonidentifiability_proved": (
                physical_sm_g8_frontier.get(
                    "continuous_absolute_scale_nonidentifiability_proved", False
                )
            ),
            "PDG_2025_single_channel_constraint_verified": (
                physical_sm_g8_frontier.get(
                    "repository_frozen_PDG_2025_single_channel_constraint_verified",
                    False,
                )
            ),
            "unique_proton_lifetime_or_distribution": False,
            "physical_G8_closed": False,
        }
    else:
        excluded = bool(
            _dig(proton, "flag", "model_point_excluded", default=False)
        )
        complete = bool(
            _dig(
                proton,
                "flag",
                "complete_operator_running_and_hadronic_matching",
                default=False,
            )
        )
        state = "FAIL" if excluded else ("PASS" if complete else "CONDITIONAL")
        evidence = {"artifact_present": True, "reported": proton}
    return _gate(
        "proton_decay",
        state,
        (
            "The exact G8 frontier proves that current source-bound inputs do not "
            "identify a unique lifetime or uncertainty distribution."
            if frontier_bound
            else "No complete proton-decay artifact is currently present."
        ),
        evidence,
        "An unavoidable predicted proton lifetime is below a current experimental bound.",
        (
            "Gauge and scalar operators, flavour rotations, RG running and lattice "
            "matrix elements predict allowed lifetimes and frozen channel ratios."
        ),
    )


def _cosmology_gate(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    physics = reports.get("next_physics", {})
    present = bool(physics)
    state = "CONDITIONAL" if present else "OPEN"
    return _gate(
        "axion_cosmology",
        state,
        (
            "Relic-density, BBN and string estimates exist, but the PQ history, "
            "reheating, entropy production, isocurvature and all-DM fraction are "
            "not jointly fixed by one UV cosmology."
        ),
        {
            "next_physics_artifact_present": present,
            "reported_status": physics.get("status"),
        },
        (
            "Every allowed thermal history violates relic abundance, isocurvature, "
            "BBN, domain-wall, or late-decay constraints."
        ),
        (
            "A frozen pre- or post-inflation history yields the observed abundance "
            "and passes isocurvature, strings/domain walls, BBN and reheating tests."
        ),
    )


def _experiment_gate(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    halo = reports.get("haloscope", {})
    flags = halo.get("flag", {})
    real_detection = bool(
        flags.get("real_37GHz_detection")
        or flags.get("experimental_detection")
        or halo.get("real_detection")
    )
    benchmark_excluded = bool(
        flags.get("benchmark_excluded")
        or _dig(halo, "classification", "benchmark_excluded", default=False)
    )
    if benchmark_excluded:
        state = "FAIL"
    elif real_detection:
        state = "PASS"
    else:
        state = "OPEN"
    return _gate(
        "direct_37GHz_experiment",
        state,
        (
            "Public-limit comparison and software injection recovery are not a "
            "real axion observation. A blind magnet-on/off, retuned, repeated "
            "36.6-37.6 GHz search remains required."
        ),
        {
            "comparison_artifact_present": bool(halo),
            "real_detection": real_detection,
            "benchmark_excluded": benchmark_excluded,
        },
        (
            "A calibrated null reaches g_agamma <= 2.3e-14 GeV^-1 across the "
            "benchmark window under the stated local all-DM halo assumption."
        ),
        (
            "Independent apparatus reproduce a signal with the predicted mass, "
            "linewidth, B^2 scaling, retuning behavior and temporal Doppler pattern."
        ),
    )


def _reproducibility_gate(
    reports: dict[str, dict[str, Any]],
    missing: list[str],
    current_test_count: int,
) -> dict[str, Any]:
    attestation = reports.get("unit_attestation", {})
    tests_passed = bool(attestation.get("passed"))
    test_count = attestation.get("tests_discovered")
    count_matches = isinstance(test_count, int) and test_count == current_test_count
    required_missing = [
        name
        for name in (
            "so10_axion_v20_verdict.json",
            "V20_ERROR_AUDIT.json",
            "FALSIFICATION_VERDICT.json",
            "EXTENSIVE_CONFIRM_FALSIFY_VERDICT.json",
            "GAUGED_U1X_G3_SOS_CANDIDATE_V20.json",
            "EXACT_GAUGED_U1X_G3_PD_RANK_CERTIFICATE_V20.json",
            "EXACT_GAUGED_U1X_G3_A_SQUARE_RECOUPLING_V20.json",
            "EXACT_GAUGED_U1X_G3_SOS_BFB_STATIONARITY_V20.json",
            "EXACT_GAUGED_U1X_G3_KERNEL_QUARTIC_BOUND_V20.json",
            "EXACT_GAUGED_U1X_G3_REPLACEMENT_STATIONARY_ORBIT_V20.json",
            "EXACT_GAUGED_U1X_G3_SU5_DELTA_PD_SOS_V20.json",
            "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXTENSION_V20.json",
            "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXACT_HESSIAN_V20.json",
            "EXACT_GAUGED_U1X_G3_SU5_EQUALITY_ORBIT_V20.json",
            "EXACT_GAUGED_U1X_G3_SU5_PHI_ORBIT_LEMMA_V20.json",
            "EXACT_GAUGED_U1X_G3_SU5_PHI_LOCAL_COMPONENT_V20.json",
            "EXACT_GAUGED_U1X_G3_SU5_PHI_SU3_SLICE_V20.json",
            "EXACT_GAUGED_U1X_G3_SU5_CHIRAL_GLOBAL_GAP_REDUCTION_V20.json",
            "EXACT_GAUGED_U1X_G3_SU5_FIXED_F_OFFKERNEL_BOUND_V20.json",
            "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_ZERO_RESIDUAL_BOUND_V20.json",
            "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_FULL_RESIDUAL_BOUND_V20.json",
            "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_RANK1_SU3_SLICE_V20.json",
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_STABILIZER_V20.json",
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_INTERTWINERS_V20.json",
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_ALIGNED_CARRIERS_V20.json",
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_QUADRATIC_BASIS_V20.json",
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CENSUS_V20.json",
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_V20.json",
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.json",
            "EXACT_GAUGED_U1X_G3_ALTERNATIVE_GLOBAL_SOS_AUDIT_V20.json",
            "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.json",
            "EXACT_GAUGED_U1X_G2_MATHEMATICAL_CLOSURE_V20.json",
            "FINAL_G3_ACCEPTANCE_GATE_V20.json",
        )
        if name in missing
    ]
    if required_missing:
        state = "OPEN"
    elif tests_passed and count_matches:
        state = "PASS"
    else:
        state = "OPEN"
    return _gate(
        "reproducibility_and_CI",
        state,
        (
            "This gate requires a current-tree unit-test attestation plus the "
            "independent, adversarial and extensive artifacts from the same run."
        ),
        {
            "unit_test_attestation_present": bool(attestation),
            "unit_tests_passed": tests_passed,
            "tests_discovered": test_count,
            "current_tree_tests_discovered": current_test_count,
            "test_count_matches_current_tree": count_matches,
            "attested_commit": attestation.get("commit_sha"),
            "current_commit": os.getenv("GITHUB_SHA", ""),
            "required_missing": required_missing,
        },
        "The current merged tree cannot reproduce its advertised checks.",
        (
            "A clean environment executes all tests and gates on the exact commit, "
            "with scoped attestation and archived machine-readable artifacts."
        ),
    )


def build_report(root: Path = ROOT) -> dict[str, Any]:
    reports, missing = load_reports(root)
    canonical_report = canonical_gates.build_report(root)
    canonical_authority = _canonical_authority_gate(
        canonical_report,
        reports.get("authoritative"),
        root,
    )
    exact_x_v3_contract = gate_ledger._exact_x_v3_fail_closed_contract(
        reports.get("x_contract", {}),
        source_raw_sha256=gate_ledger._raw_file_sha256(root / EXACT_X_V3_SOURCE),
        test_raw_sha256=gate_ledger._raw_file_sha256(root / EXACT_X_V3_TEST),
        json_raw_sha256=gate_ledger._raw_file_sha256(
            root / ARTIFACTS["x_contract"]
        ),
        markdown_raw_sha256=gate_ledger._raw_file_sha256(root / EXACT_X_V3_MD),
        input_manifest_raw_sha256=gate_ledger._raw_file_sha256(
            root / EXACT_X_V3_INPUT_MANIFEST
        ),
        trusted_sarah_manifest_raw_sha256=gate_ledger._raw_file_sha256(
            root / EXACT_X_V3_TRUSTED_SARAH_MANIFEST
        ),
        external_validation_file_present=(
            root / "models/EXACT_X_EXTERNAL_MODEL_VALIDATION_V20.json"
        ).is_file(),
    )
    renormalizable_g1_component_tensor_closure = (
        gate_ledger._renormalizable_g1_component_tensor_closure(
            reports.get("renormalizable_g1_component_tensor", {}),
            raw_sha256=gate_ledger._raw_file_sha256(
                root / ARTIFACTS["renormalizable_g1_component_tensor"]
            ),
            source_raw_sha256=gate_ledger._raw_file_sha256(
                root / RENORMALIZABLE_G1_COMPONENT_TENSOR_SOURCE
            ),
        )
    )
    ledger_g1_component_tensor_closure = reports.get("g1_g8", {}).get(
        "renormalizable_G1_component_tensor_closure", {}
    )
    renormalizable_g1_component_tensor_closure_matches_ledger = bool(
        ledger_g1_component_tensor_closure
        and renormalizable_g1_component_tensor_closure
        == ledger_g1_component_tensor_closure
    )
    renormalizable_g2_mathematical_closure = (
        gate_ledger._renormalizable_g2_mathematical_closure(
            reports.get("renormalizable_g2_mathematical", {}),
            raw_sha256=gate_ledger._raw_file_sha256(
                root / ARTIFACTS["renormalizable_g2_mathematical"]
            ),
            source_raw_sha256=gate_ledger._raw_file_sha256(
                root / RENORMALIZABLE_G2_MATHEMATICAL_SOURCE
            ),
        )
    )
    ledger_g2_mathematical_closure = reports.get("g1_g8", {}).get(
        "renormalizable_G2_mathematical_closure", {}
    )
    renormalizable_g2_mathematical_closure_matches_ledger = bool(
        ledger_g2_mathematical_closure
        and renormalizable_g2_mathematical_closure
        == ledger_g2_mathematical_closure
    )
    parallel_eft_g3_acceptance = gate_ledger._parallel_eft_g3_acceptance(
        reports.get("final_g3_eft", {}),
        raw_sha256=gate_ledger._raw_file_sha256(
            root / ARTIFACTS["final_g3_eft"]
        ),
    )
    parallel_eft_g4_mathematical = gate_ledger._parallel_eft_g4_mathematical(
        reports.get("final_g4_eft", {}),
        raw_sha256=gate_ledger._raw_file_sha256(
            root / ARTIFACTS["final_g4_eft"]
        ),
    )
    parallel_eft_g5_mathematical = gate_ledger._parallel_eft_g5_mathematical(
        reports.get("final_g5_eft", {}),
        raw_sha256=gate_ledger._raw_file_sha256(
            root / ARTIFACTS["final_g5_eft"]
        ),
    )
    g6_sm_provenance = gate_ledger._g6_sm_provenance_audit(
        reports.get("g6_sm_provenance", {}),
        raw_sha256=gate_ledger._raw_file_sha256(
            root / ARTIFACTS["g6_sm_provenance"]
        ),
        source_raw_sha256=gate_ledger._raw_file_sha256(
            root / G6_SM_PROVENANCE_SOURCE
        ),
    )
    g6_g7_parameterized_matching = gate_ledger._parameterized_g6_g7_matching(
        reports.get("g6_g7_parameterized_matching", {}),
        raw_sha256=gate_ledger._raw_file_sha256(
            root / ARTIFACTS["g6_g7_parameterized_matching"]
        ),
        source_raw_sha256=gate_ledger._raw_file_sha256(
            root / G6_G7_PARAMETERIZED_MATCHING_SOURCE
        ),
    )
    parallel_eft_g6_spectrum = gate_ledger._parallel_eft_g6_spectrum(
        reports.get("final_g6_eft", {}),
        raw_sha256=gate_ledger._raw_file_sha256(
            root / ARTIFACTS["final_g6_eft"]
        ),
        gate_source_raw_sha256=gate_ledger._raw_file_sha256(
            root / FINAL_G6_EFT_GATE_SOURCE
        ),
        provenance_audit=g6_sm_provenance,
        parameterized_matching=g6_g7_parameterized_matching,
    )
    authoritative_gauge_betas = gate_ledger._authoritative_gauge_beta_subtheorem(
        reports.get("authoritative_gauge_betas", {}),
        raw_sha256=gate_ledger._raw_file_sha256(
            root / ARTIFACTS["authoritative_gauge_betas"]
        ),
        source_raw_sha256=gate_ledger._raw_file_sha256(
            root / AUTHORITATIVE_GAUGE_BETAS_SOURCE
        ),
    )
    pyrate3_gauge_replay = gate_ledger._pyrate3_gauge_replay_subtheorem(
        reports.get("pyrate3_gauge_replay", {}),
        raw_sha256=gate_ledger._raw_file_sha256(
            root / ARTIFACTS["pyrate3_gauge_replay"]
        ),
        source_raw_sha256=gate_ledger._raw_file_sha256(
            root / PYRATE3_GAUGE_REPLAY_SOURCE
        ),
        model_raw_sha256=gate_ledger._raw_file_sha256(
            root / "models" / "SO10U1XGaugeAuditV20.model"
        ),
        data_raw_sha256=gate_ledger._raw_file_sha256(
            root / "data" / "PYRATE3_SO10_U1X_GAUGE_BETA_FROZEN_V20.json"
        ),
    )
    physical_g7_component_threshold = (
        gate_ledger._physical_g7_component_threshold_contract(
            reports.get("physical_g7_component_threshold", {}),
            raw_sha256=gate_ledger._raw_file_sha256(
                root / ARTIFACTS["physical_g7_component_threshold"]
            ),
            source_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_G7_COMPONENT_THRESHOLD_SOURCE
            ),
            test_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_G7_COMPONENT_THRESHOLD_TEST
            ),
            markdown_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_G7_COMPONENT_THRESHOLD_MD
            ),
        )
    )
    normalized_yukawa_cgcs = gate_ledger._normalized_so10_yukawa_cgc_contract(
        reports.get("normalized_yukawa_cgcs", {}),
        raw_sha256=gate_ledger._raw_file_sha256(
            root / ARTIFACTS["normalized_yukawa_cgcs"]
        ),
        source_raw_sha256=gate_ledger._raw_file_sha256(
            root / NORMALIZED_YUKAWA_CGCS_SOURCE
        ),
        test_raw_sha256=gate_ledger._raw_file_sha256(
            root / NORMALIZED_YUKAWA_CGCS_TEST
        ),
        markdown_raw_sha256=gate_ledger._raw_file_sha256(
            root / NORMALIZED_YUKAWA_CGCS_MD
        ),
    )
    physical_sm_vacuum = gate_ledger._physical_sm_vacuum_truth_overlay(
        reports.get("physical_sm_vacuum", {}),
        raw_sha256=gate_ledger._raw_file_sha256(
            root / ARTIFACTS["physical_sm_vacuum"]
        ),
        source_raw_sha256=gate_ledger._raw_file_sha256(
            root / PHYSICAL_SM_VACUUM_SOURCE
        ),
        test_raw_sha256=gate_ledger._raw_file_sha256(
            root / PHYSICAL_SM_VACUUM_TEST
        ),
        markdown_raw_sha256=gate_ledger._raw_file_sha256(
            root / PHYSICAL_SM_VACUUM_MD
        ),
    )
    physical_sm_source_equality = (
        gate_ledger._physical_sm_source_algebra_equality_frontier_contract(
            reports.get("physical_sm_source_equality", {}),
            raw_sha256=gate_ledger._raw_file_sha256(
                root / ARTIFACTS["physical_sm_source_equality"]
            ),
            source_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_SOURCE_EQUALITY_SOURCE
            ),
            test_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_SOURCE_EQUALITY_TEST
            ),
            markdown_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_SOURCE_EQUALITY_MD
            ),
        )
    )
    physical_sm_five_amplitude_equality = (
        gate_ledger._physical_sm_five_amplitude_equality_contract(
            reports.get("physical_sm_five_amplitude_equality", {}),
            raw_sha256=gate_ledger._raw_file_sha256(
                root / ARTIFACTS["physical_sm_five_amplitude_equality"]
            ),
            source_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_SOURCE
            ),
            test_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_TEST
            ),
            markdown_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_MD
            ),
        )
    )
    physical_sm_hard_projector_hessians = (
        gate_ledger._physical_sm_hard_projector_hessians_contract(
            reports.get("physical_sm_hard_projector_hessians", {}),
            raw_sha256=gate_ledger._raw_file_sha256(
                root / ARTIFACTS["physical_sm_hard_projector_hessians"]
            ),
            source_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_SOURCE
            ),
            test_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_TEST
            ),
            markdown_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_MD
            ),
        )
    )
    physical_sm_last_six_hessians = (
        gate_ledger._physical_sm_last_six_hessians_contract(
            reports.get("physical_sm_last_six_hessians", {}),
            raw_sha256=gate_ledger._raw_file_sha256(
                root / ARTIFACTS["physical_sm_last_six_hessians"]
            ),
            source_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_LAST_SIX_HESSIANS_SOURCE
            ),
            test_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_LAST_SIX_HESSIANS_TEST
            ),
            markdown_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_LAST_SIX_HESSIANS_MD
            ),
        )
    )
    physical_sm_37_row_aggregate = (
        gate_ledger._physical_sm_37_row_aggregate_contract(
            reports.get("physical_sm_37_row_aggregate", {}),
            raw_sha256=gate_ledger._raw_file_sha256(
                root / ARTIFACTS["physical_sm_37_row_aggregate"]
            ),
            source_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_37_ROW_AGGREGATE_SOURCE
            ),
            test_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_37_ROW_AGGREGATE_TEST
            ),
            markdown_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_37_ROW_AGGREGATE_MD
            ),
        )
    )
    physical_sm_local_equality_orbit = (
        gate_ledger._physical_sm_local_equality_orbit_contract(
            reports.get("physical_sm_local_equality_orbit", {}),
            portable_lf_sha256=gate_ledger._file_sha256(
                root / ARTIFACTS["physical_sm_local_equality_orbit"]
            ),
            source_portable_lf_sha256=gate_ledger._file_sha256(
                root / PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_SOURCE
            ),
            test_portable_lf_sha256=gate_ledger._file_sha256(
                root / PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_TEST
            ),
            markdown_portable_lf_sha256=gate_ledger._file_sha256(
                root / PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_MD
            ),
        )
    )
    physical_sm_g4_g5_branch_mismatch = (
        gate_ledger._physical_sm_g4_g5_branch_mismatch_contract(
            reports.get("physical_sm_g4_g5_branch_mismatch", {}),
            raw_sha256=gate_ledger._raw_file_sha256(
                root / ARTIFACTS["physical_sm_g4_g5_branch_mismatch"]
            ),
            source_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_SOURCE
            ),
            test_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_TEST
            ),
            markdown_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_MD
            ),
        )
    )
    physical_sm_heavy_vectors = gate_ledger._physical_sm_heavy_vector_mass_contract(
        reports.get("physical_sm_heavy_vectors", {}),
        raw_sha256=gate_ledger._raw_file_sha256(
            root / ARTIFACTS["physical_sm_heavy_vectors"]
        ),
        source_raw_sha256=gate_ledger._raw_file_sha256(
            root / PHYSICAL_SM_HEAVY_VECTOR_SOURCE
        ),
        test_raw_sha256=gate_ledger._raw_file_sha256(
            root / PHYSICAL_SM_HEAVY_VECTOR_TEST
        ),
        markdown_raw_sha256=gate_ledger._raw_file_sha256(
            root / PHYSICAL_SM_HEAVY_VECTOR_MD
        ),
    )
    physical_sm_heavy_vector_msbar = (
        gate_ledger._physical_sm_heavy_vector_msbar_matching_contract(
            reports.get("physical_sm_heavy_vector_msbar", {}),
            raw_sha256=gate_ledger._raw_file_sha256(
                root / ARTIFACTS["physical_sm_heavy_vector_msbar"]
            ),
            source_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_HEAVY_VECTOR_MSBAR_SOURCE
            ),
            test_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_HEAVY_VECTOR_MSBAR_TEST
            ),
            markdown_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MD
            ),
        )
    )
    physical_sm_vector_rxi = (
        gate_ledger._physical_sm_vector_rxi_vacuum_cancellation_contract(
            reports.get("physical_sm_vector_rxi", {}),
            raw_sha256=gate_ledger._raw_file_sha256(
                root / ARTIFACTS["physical_sm_vector_rxi"]
            ),
            source_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_VECTOR_RXI_SOURCE
            ),
            test_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_VECTOR_RXI_TEST
            ),
            markdown_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_VECTOR_RXI_MD
            ),
        )
    )
    conditional_physical_sm_scalar_spectrum = (
        gate_ledger._conditional_physical_sm_eft_hessian_spectrum_contract(
            reports.get("conditional_physical_sm_scalar_spectrum", {}),
            raw_sha256=gate_ledger._raw_file_sha256(
                root / ARTIFACTS["conditional_physical_sm_scalar_spectrum"]
            ),
            source_raw_sha256=gate_ledger._raw_file_sha256(
                root / CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_SOURCE
            ),
            test_raw_sha256=gate_ledger._raw_file_sha256(
                root / CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_TEST
            ),
            markdown_raw_sha256=gate_ledger._raw_file_sha256(
                root / CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_MD
            ),
        )
    )
    physical_sm_g6_g7_closure_frontier = (
        gate_ledger._physical_sm_g6_g7_closure_frontier_contract(
            reports.get("physical_sm_g6_g7_closure_frontier", {}),
            raw_sha256=gate_ledger._raw_file_sha256(
                root / ARTIFACTS["physical_sm_g6_g7_closure_frontier"]
            ),
            source_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_G6_G7_FRONTIER_SOURCE
            ),
            test_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_G6_G7_FRONTIER_TEST
            ),
            markdown_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_G6_G7_FRONTIER_MD
            ),
        )
    )
    physical_sm_g8_identifiability_frontier = (
        gate_ledger._physical_sm_g8_identifiability_frontier_contract(
            reports.get("physical_sm_g8_identifiability_frontier", {}),
            raw_sha256=gate_ledger._raw_file_sha256(
                root / ARTIFACTS["physical_sm_g8_identifiability_frontier"]
            ),
            source_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_G8_FRONTIER_SOURCE
            ),
            test_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_G8_FRONTIER_TEST
            ),
            markdown_raw_sha256=gate_ledger._raw_file_sha256(
                root / PHYSICAL_SM_G8_FRONTIER_MD
            ),
        )
    )
    physical_g7_recalculated_inputs = (
        gate_ledger._physical_g7_recalculated_input_resolution(
            physical_g7_component_threshold,
            normalized_yukawa_cgcs,
            physical_sm_heavy_vectors,
            physical_sm_heavy_vector_msbar,
            physical_sm_vector_rxi,
            conditional_physical_sm_scalar_spectrum,
            physical_sm_g6_g7_closure_frontier,
        )
    )
    eft_g7_nonidentifiability = gate_ledger._parallel_eft_g7_nonidentifiability(
        reports.get("eft_g7_nonidentifiability", {}),
        raw_sha256=gate_ledger._raw_file_sha256(
            root / ARTIFACTS["eft_g7_nonidentifiability"]
        ),
        source_raw_sha256=gate_ledger._raw_file_sha256(
            root / EFT_G7_NONIDENTIFIABILITY_SOURCE
        ),
    )
    # A fresh loader avoids leaking ``_top_level_dir`` between temporary
    # release fixtures.  Discovery itself also imports every copied test
    # module.  Preserve and restore the caller's test-module cache so a
    # temporary fixture cannot poison a later nested discovery with a module
    # whose ``__file__`` points at an already-deleted temporary directory.
    cached_test_modules = {
        name: module
        for name, module in sys.modules.items()
        if name.startswith("test_") or ".test_" in name
    }
    try:
        for name in tuple(cached_test_modules):
            sys.modules.pop(name, None)
        current_test_count = (
            unittest.TestLoader().discover(str(root)).countTestCases()
        )
    finally:
        for name in tuple(sys.modules):
            if name.startswith("test_") or ".test_" in name:
                sys.modules.pop(name, None)
        sys.modules.update(cached_test_modules)
    gates = [
        canonical_authority,
        _model_contract_gate(reports, exact_x_v3_contract),
        _core_gate(reports),
        _operator_gate(reports),
        _vacuum_gate(
            reports,
            renormalizable_g1_component_tensor_closure,
            renormalizable_g2_mathematical_closure,
            parallel_eft_g3_acceptance,
            parallel_eft_g4_mathematical,
            parallel_eft_g5_mathematical,
            parallel_eft_g6_spectrum,
            g6_sm_provenance,
            g6_g7_parameterized_matching,
            physical_sm_vacuum,
            physical_sm_source_equality,
            physical_sm_five_amplitude_equality,
            physical_sm_hard_projector_hessians,
            physical_sm_last_six_hessians,
            physical_sm_37_row_aggregate,
            physical_sm_local_equality_orbit,
            physical_sm_g4_g5_branch_mismatch,
            physical_sm_heavy_vectors,
            conditional_physical_sm_scalar_spectrum,
        ),
        _rge_gate(
            reports,
            eft_g7_nonidentifiability,
            g6_sm_provenance,
            g6_g7_parameterized_matching,
            authoritative_gauge_betas,
            pyrate3_gauge_replay,
            physical_g7_component_threshold,
            normalized_yukawa_cgcs,
            physical_sm_heavy_vectors,
            physical_sm_heavy_vector_msbar,
            physical_sm_vector_rxi,
            conditional_physical_sm_scalar_spectrum,
            physical_sm_g6_g7_closure_frontier,
            physical_g7_recalculated_inputs,
        ),
        _flavour_gate(reports),
        _portal_gate(reports),
        _proton_gate(reports, root, physical_sm_g8_identifiability_frontier),
        _cosmology_gate(reports),
        _experiment_gate(reports),
        _reproducibility_gate(reports, missing, current_test_count),
    ]
    states = {gate["name"]: gate["state"] for gate in gates}
    failed = [gate["name"] for gate in gates if gate["state"] == "FAIL"]
    blocked = [gate["name"] for gate in gates if gate["state"] == "BLOCKED"]
    mandatory_open = [
        gate["name"]
        for gate in gates
        if gate["mandatory_for_full_validation"]
        and gate["state"] in {"OPEN", "CONDITIONAL", "BLOCKED"}
    ]
    canonical_closed = bool(
        canonical_authority["state"] == "PASS"
        and canonical_authority["evidence"]["all_canonical_gates_closed"]
        is True
        and canonical_authority["evidence"][
            "authoritative_report_matches_canonical_state"
        ]
        is True
    )

    if canonical_authority["state"] == "FAIL":
        classification = "CANONICAL_G1_G8_AUTHORITY_INTEGRITY_FAILED"
        decision = "REJECT"
    elif canonical_closed:
        classification = "FULL_PHENOMENOLOGY_VALIDATED__NO_DISCOVERY_IMPLIED"
        decision = "VALIDATE_FULL_PHENOMENOLOGY"
    elif states["mathematical_and_software_core"] == "FAIL":
        classification = "CURRENT_REALIZATION_REJECTED"
        decision = "REJECT"
    else:
        classification = "CANONICAL_G1_G8_GATES_OPEN"
        decision = "WITHHOLD_APPROVAL"

    overclaim_errors: list[str] = []
    overclaim_warnings: list[str] = []
    vacuum = reports.get("vacuum", {})
    if (
        "SOLVED" in str(vacuum.get("status", ""))
        and not bool(
            _dig(
                vacuum,
                "flag",
                "scalar_quartic_landscape_fully_minimized",
                default=False,
            )
        )
    ):
        overclaim_warnings.append(
            "vacuum status says alignment is solved under named axioms; "
            "the full scalar landscape remains open"
        )
    rge = reports.get("rge", {})
    if (
        "COMPLETE" in str(rge.get("status", ""))
        and not bool(_dig(rge, "flag", "two_loop_so10_complete", default=False))
    ):
        overclaim_warnings.append(
            "RGE status says the diagnostic piecewise chain is complete; "
            "full two-loop SO(10)+210 closure remains open"
        )
    sphere_probability = bool(
        _dig(
            reports.get("sphere", {}),
            "scan",
            "aggregate_counts",
            "geometric_fraction_is_uv_probability",
            default=_dig(
                reports.get("sphere", {}),
                "aggregate_counts",
                "geometric_fraction_is_uv_probability",
                default=False,
            ),
        )
    )
    if sphere_probability:
        overclaim_errors.append(
            "the fixed-norm Haar orientation fraction is incorrectly labeled "
            "as a UV probability"
        )
    if bool(_dig(vacuum, "flag", "unconditional_unique_Cf", default=False)):
        overclaim_errors.append(
            "conditional vacuum assumptions are incorrectly promoted to "
            "unconditional unique C_f"
        )
    if bool(_dig(rge, "flag", "two_loop_so10_complete", default=False)) and not bool(
        _dig(rge, "flag", "published_210_tensor_contractions", default=False)
    ):
        overclaim_errors.append(
            "full two-loop SO(10) closure is claimed without published 210 "
            "tensor contractions"
        )
    if canonical_closed and classification != (
        "FULL_PHENOMENOLOGY_VALIDATED__NO_DISCOVERY_IMPLIED"
    ):
        overclaim_errors.append("canonical full-validation state machine is inconsistent")

    integrity_pass = bool(
        not overclaim_errors
        and canonical_authority["state"] != "FAIL"
        and (
            canonical_closed
            or states["mathematical_and_software_core"] != "FAIL"
        )
    )
    if overclaim_errors:
        classification = "VALIDATION_MATRIX_FAIL__OVERCLAIM"
        decision = "REJECT"

    return {
        "status": "PASS" if integrity_pass else "FAIL",
        "overall_state": (
            "FAIL"
            if not integrity_pass
            else "PASS"
            if canonical_closed
            else "BLOCKED"
        ),
        "classification": classification,
        "decision": decision,
        "full_theory_validated": bool(canonical_closed and integrity_pass),
        "empirical_discovery": False,
        "canonical_G1_G8_V21": canonical_report,
        "canonical_authoritative_consistency": canonical_authority["evidence"],
        "exact_X_v3_fail_closed_contract": exact_x_v3_contract,
        "renormalizable_G1_component_tensor_closure": (
            renormalizable_g1_component_tensor_closure
        ),
        "renormalizable_G1_component_tensor_closure_matches_ledger": (
            renormalizable_g1_component_tensor_closure_matches_ledger
        ),
        "renormalizable_G2_mathematical_closure": (
            renormalizable_g2_mathematical_closure
        ),
        "renormalizable_G2_mathematical_closure_matches_ledger": (
            renormalizable_g2_mathematical_closure_matches_ledger
        ),
        "parallel_EFT_G3_acceptance": parallel_eft_g3_acceptance,
        "parallel_EFT_G4_mathematical": parallel_eft_g4_mathematical,
        "parallel_EFT_G5_mathematical": parallel_eft_g5_mathematical,
        "parallel_EFT_G6_spectrum": parallel_eft_g6_spectrum,
        "parallel_EFT_G7_nonidentifiability": eft_g7_nonidentifiability,
        "physical_G7_component_threshold_contract": (
            physical_g7_component_threshold
        ),
        "normalized_SO10_Yukawa_CGC_contract": normalized_yukawa_cgcs,
        "physical_SM_vacuum_truth_overlay": physical_sm_vacuum,
        "physical_SM_source_algebra_equality_frontier": (
            physical_sm_source_equality
        ),
        "physical_SM_five_amplitude_equality_contract": (
            physical_sm_five_amplitude_equality
        ),
        "physical_SM_hard_projector_Hessians_contract": (
            physical_sm_hard_projector_hessians
        ),
        "physical_SM_last_six_Hessians_contract": (
            physical_sm_last_six_hessians
        ),
        "physical_SM_37_row_aggregate_contract": (
            physical_sm_37_row_aggregate
        ),
        "physical_SM_local_equality_orbit_contract": (
            physical_sm_local_equality_orbit
        ),
        "physical_SM_G4_G5_branch_mismatch_contract": (
            physical_sm_g4_g5_branch_mismatch
        ),
        "physical_SM_heavy_vector_mass_contract": physical_sm_heavy_vectors,
        "physical_SM_heavy_vector_MSbar_matching_contract": (
            physical_sm_heavy_vector_msbar
        ),
        "physical_SM_vector_Rxi_vacuum_cancellation_contract": (
            physical_sm_vector_rxi
        ),
        "conditional_physical_SM_EFT_Hessian_spectrum_contract": (
            conditional_physical_sm_scalar_spectrum
        ),
        "physical_SM_G6_G7_closure_frontier_contract": (
            physical_sm_g6_g7_closure_frontier
        ),
        "physical_SM_G8_identifiability_frontier_contract": (
            physical_sm_g8_identifiability_frontier
        ),
        "physical_G7_recalculated_input_resolution": (
            physical_g7_recalculated_inputs
        ),
        "current_tree_unit_tests_discovered": current_test_count,
        "n_gates": len(gates),
        "n_failed_gates": len(failed),
        "failed_gates": failed,
        "n_blocked_gates": len(blocked),
        "blocked_gates": blocked,
        "mandatory_nonpass_gates": mandatory_open,
        "overclaim_errors": overclaim_errors,
        "overclaim_warnings": overclaim_warnings,
        "missing_artifacts": missing,
        "gates": gates,
        "kill_tests": {gate["name"]: gate["kill_condition"] for gate in gates},
        "green_requirements": {
            gate["name"]: gate["green_condition"] for gate in gates
        },
        "verdict": (
            "All eight qualified canonical gauged-U(1)_X V21 gates are closed, "
            "and the authoritative full-model report agrees exactly."
            if canonical_closed
            else "Qualified canonical gauged-U(1)_X V21 evidence remains open. "
            "Legacy scalar-ledger gate numbers and historical Option-C results "
            "remain scoped diagnostics; they cannot promote or veto full closure."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Theory validity matrix — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        f"**Classification:** `{report['classification']}`",
        "",
        f"**Decision:** `{report['decision']}`",
        "",
        f"- Full theory validated: **{report['full_theory_validated']}**",
        f"- Empirical discovery: **{report['empirical_discovery']}**",
        (
            "- Renormalizable mathematical G1 component-tensor closure: "
            f"**{report['renormalizable_G1_component_tensor_closure']['mathematical_G1_closed_for_renormalizable_model']}**"
        ),
        (
            "- Authoritative/release G1 promotion: "
            f"**{report['renormalizable_G1_component_tensor_closure']['release_G1_verified']}**"
        ),
        (
            "- Renormalizable mathematical G2 component-potential closure: "
            f"**{report['renormalizable_G2_mathematical_closure']['mathematical_G2_closed_for_renormalizable_model']}**"
        ),
        (
            "- Authoritative/release G2 promotion: "
            f"**{report['renormalizable_G2_mathematical_closure']['release_G2_verified']}**"
        ),
        (
            "- Parallel dimension-six EFT mathematical G3: "
            f"**{report['parallel_EFT_G3_acceptance']['mathematical_G3_closed_for_EFT_model']}**"
        ),
        (
            "- Parallel EFT release G3 verified: "
            f"**{report['parallel_EFT_G3_acceptance']['release_G3_verified_for_EFT_model']}**"
        ),
        (
            "- Parallel dimension-six EFT mathematical G4: "
            f"**{report['parallel_EFT_G4_mathematical']['mathematical_G4_closed_for_EFT_model']}**"
        ),
        (
            "- Parallel EFT release G4 verified: "
            f"**{report['parallel_EFT_G4_mathematical']['release_G4_verified_for_EFT_model']}**"
        ),
        (
            "- Parallel dimension-six EFT mathematical G5: "
            f"**{report['parallel_EFT_G5_mathematical']['mathematical_G5_closed_for_EFT_model']}**"
        ),
        (
            "- Parallel EFT release G5 verified: "
            f"**{report['parallel_EFT_G5_mathematical']['release_G5_verified_for_EFT_model']}**"
        ),
        (
            "- Parallel dimension-six EFT mathematical G6: "
            f"**{report['parallel_EFT_G6_spectrum']['mathematical_G6_closed_for_EFT_model']}**"
        ),
        (
            "- Parallel EFT release G6 verified: "
            f"**{report['parallel_EFT_G6_spectrum']['release_G6_verified_for_EFT_model']}**"
        ),
        (
            "- Formal U(1)_89 abstract restriction noninjectivity: "
            f"**{report['parallel_EFT_G7_nonidentifiability']['formal_U1_89_abstract_restriction_noninjectivity_proved']}**"
        ),
        (
            "- Physical PS/SM matter branching and parameterized one-loop "
            "matter-threshold kernel: "
            f"**{report['physical_G7_component_threshold_contract']['source_bound']}**"
        ),
        (
            "- Normalized SO(10) `10`/`126bar`/singlet Yukawa CGCs: "
            f"**{report['normalized_SO10_Yukawa_CGC_contract']['source_bound']}**"
        ),
        "- Flavor values, SARAH conversion, Yukawa RGEs and physical threshold matching remain open.",
        (
            "- Physical-SM target/stabilizer truth overlay: "
            f"**{report['physical_SM_vacuum_truth_overlay']['source_bound']}**"
        ),
        (
            "- Exact five-real-amplitude equality classification (16 discrete "
            "sign variants; full 486-field/continuous-orbit proof open): "
            f"**{report['physical_SM_five_amplitude_equality_contract']['source_bound']}**"
        ),
        (
            "- Exact hard-projector Hessians (the staged 10/37-row input; the "
            "succeeding 37-row aggregate closes stationarity/rank/PSD): "
            f"**{report['physical_SM_hard_projector_Hessians_contract']['source_bound']}**"
        ),
        (
            "- Exact last-six Hessians (all 37 active source Hessians made "
            "available; the succeeding aggregate closes stationarity/kernel/rank/PSD): "
            f"**{report['physical_SM_last_six_Hessians_contract']['source_bound']}**"
        ),
        (
            "- Exact source-derived 37-row local Hessian theorem (stationary, "
            "38-mode kernel, rank 448, PSD; global equality open): "
            f"**{report['physical_SM_37_row_aggregate_contract']['source_bound']}**"
        ),
        (
            "- Exact full-486 local stationary/equality orbit plus one continuous "
            "K-orbit for all 16 sign variants (radius/global equality open): "
            f"**{report['physical_SM_local_equality_orbit_contract']['source_bound']}**"
        ),
        (
            "- Exact five-amplitude/physical-EW branch mismatch (not a global "
            "hierarchy no-go): "
            f"**{report['physical_SM_G4_G5_branch_mismatch_contract']['source_bound']}**"
        ),
        (
            "- Exact parameterized physical-SM heavy-vector tree inputs: "
            f"**{report['physical_SM_heavy_vector_mass_contract']['source_bound']}**"
        ),
        (
            "- Exact combined heavy-vector + FP-ghost + Goldstone non-SUSY MSbar "
            "kernel and finite constant: "
            f"**{report['physical_SM_heavy_vector_MSbar_matching_contract']['source_bound']}**"
        ),
        (
            "- Conditional reconstructed physical-SM tree scalar spectrum: "
            f"**{report['conditional_physical_SM_EFT_Hessian_spectrum_contract']['source_bound']}**"
        ),
        (
            "- Recalculated scoped G7 inputs with stale embedding/vector blockers "
            "superseded: "
            f"**{report['physical_G7_recalculated_input_resolution']['source_bound']}**"
        ),
        (
            "- Exact G8 identifiability frontier, 101-case scale audit, and "
            "PDG-2025 single-channel constraint: "
            f"**{report['physical_SM_G8_identifiability_frontier_contract']['source_bound']}**"
        ),
        "- Background-covariant general-field Rxi determinants and heat-kernel replay, tree-to-pole vector masses with tadpole/VEV scheme, stationary pre-EW matching, complete scalar/fermion thresholds, physical scale/boundaries, flavor boundaries, SARAH identical-Weyl conversion and full Yukawa betas remain open.",
        "- Old selected EFT target: `SU(3)_C x U(1)_89`; physical-SM G3-G8 remain false.",
        "- Mathematical/release/authoritative G7: **False**/**False**/**False**.",
        "- Original renormalizable G3-G8 remain authoritative and unchanged.",
        f"- Gates: {report['n_gates']}",
        f"- Failed gates: {report['n_failed_gates']}",
        "",
        "## Sector gates",
        "",
        "| Gate | State | Summary |",
        "|---|---|---|",
    ]
    for gate in report["gates"]:
        lines.append(
            f"| `{gate['name']}` | **{gate['state']}** | {gate['summary']} |"
        )
    lines += ["", "## Hard rejection tests", ""]
    for name, text in report["kill_tests"].items():
        lines.append(f"- **{name}:** {text}")
    lines += ["", "## Requirements for a green gate", ""]
    for name, text in report["green_requirements"].items():
        lines.append(f"- **{name}:** {text}")
    lines += ["", "## Overclaim errors", ""]
    if report["overclaim_errors"]:
        lines.extend(f"- {item}" for item in report["overclaim_errors"])
    else:
        lines.append("- None")
    lines += ["", "## Scope warnings", ""]
    if report["overclaim_warnings"]:
        lines.extend(f"- {item}" for item in report["overclaim_warnings"])
    else:
        lines.append("- None")
    lines += ["", "## Verdict", "", report["verdict"], ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    report = build_report()
    if not args.no_write:
        ROOT.joinpath("THEORY_VALIDATION_MATRIX_V20_VERDICT.json").write_text(
            json.dumps(report, indent=2) + "\n",
            encoding="utf-8",
        )
        ROOT.joinpath("THEORY_VALIDATION_MATRIX_V20.md").write_text(
            write_markdown(report),
            encoding="utf-8",
        )
    print(
        json.dumps(
            {
                "status": report["status"],
                "overall_state": report["overall_state"],
                "classification": report["classification"],
                "decision": report["decision"],
                "full_theory_validated": report["full_theory_validated"],
                "n_failed_gates": report["n_failed_gates"],
                "mandatory_nonpass_gates": report["mandatory_nonpass_gates"],
                "overclaim_errors": report["overclaim_errors"],
                "overclaim_warnings": report["overclaim_warnings"],
            },
            indent=2,
        )
    )

    ok = report["status"] == "PASS"
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
