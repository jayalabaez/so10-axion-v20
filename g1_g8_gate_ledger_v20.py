#!/usr/bin/env python3
"""Contract-aware, fail-closed G1-G8 ledger for the v20 candidate.

The manuscript's gauged U(1)_X contract is authoritative.  The repository now
contains a statically consistent, tool-native SARAH input for that gauge
contract, but no current external SARAH execution attestation is available.
Consequently no authoritative whole-theory gate may yet be reported closed.  The former
64-direction/91-parameter G1/G2 calculations and
their 449-dimensional G3 quotient remain valuable, but only as explicitly
scoped historical Option-C subtheorems.

Scientific blocking is not an audit execution failure: a correct current
report has ``n_failed=0``, ``overall_state=BLOCKED``, and no closed gates.  The
exact-X 44-direction/51-parameter multiplicity census, the source-bound
component-tensor G1 ring, and the G2 derivative audit are completed scoped
subtheorems.  Their authoritative promotion remains fail-closed on the external
SARAH execution attestation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import exact_x_symmetry_consistency_gate_v20 as exact_x
import g1_exact_declared_symmetry_character_census_v20 as gauged_g1
import gauged_u1x_g2_derivative_audit_v20 as gauged_g2
import nonsusy_z17_pq_potential_filter_v20 as gauged_filter
import live_g1_tensor_closure_ledger_v20 as historical_g1
import live_g2_derivative_coverage_ledger_v20 as historical_g2
import g3_full_hessian_classification_v20 as historical_g3_hessian
import g3_stationary_stability_search_v20 as historical_g3_search
import corrected_rank1_endpoint_v21 as corrected_rank1

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G1_G8_GATE_LEDGER_V20.json"
OUT_MD = ROOT / "G1_G8_GATE_LEDGER_V20.md"
RENORMALIZABLE_G1_COMPONENT_TENSOR_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.json"
)
RENORMALIZABLE_G1_COMPONENT_TENSOR_SOURCE = (
    ROOT / "exact_gauged_u1x_g1_component_tensor_closure_v20.py"
)
RENORMALIZABLE_G1_COMPONENT_TENSOR_CORE_SHA256 = (
    "32bed88b5fad0fe6e51cf19c3b3e120d53362150cfc1db6eafd8c897e24223b7"
)
RENORMALIZABLE_G1_COMPONENT_TENSOR_RAW_SHA256 = (
    "bec8587376c7dc5a29b45c9c7f0110fcbed98a3ae2d130aaf00bb42f6997aca4"
)
RENORMALIZABLE_G1_COMPONENT_TENSOR_SOURCE_RAW_SHA256 = (
    "ca2b92198cbb7cbe6c7051b9c5952bc4af1462ba33db02eaa126533213b1e87f"
)
RENORMALIZABLE_G1_DIRECTION_MAP_SHA256 = (
    "657b739208f46ece75bfed977aa30ce1baa25f7aeed861b81007e81c7551684d"
)
G3_SOS_JSON = ROOT / "GAUGED_U1X_G3_SOS_CANDIDATE_V20.json"
G3_PD_JSON = ROOT / "EXACT_GAUGED_U1X_G3_PD_RANK_CERTIFICATE_V20.json"
G3_A_SQUARE_JSON = ROOT / "EXACT_GAUGED_U1X_G3_A_SQUARE_RECOUPLING_V20.json"
G3_SOS_BFB_JSON = ROOT / "EXACT_GAUGED_U1X_G3_SOS_BFB_STATIONARITY_V20.json"
G3_KERNEL_BOUND_JSON = ROOT / "EXACT_GAUGED_U1X_G3_KERNEL_QUARTIC_BOUND_V20.json"
G3_REPLACEMENT_JSON = ROOT / "EXACT_GAUGED_U1X_G3_REPLACEMENT_STATIONARY_ORBIT_V20.json"
G3_SU5_PD_JSON = ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_PD_SOS_V20.json"
G3_SU5_HSX_JSON = ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXTENSION_V20.json"
G3_SU5_HSX_EXACT_HESSIAN_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXACT_HESSIAN_V20.json"
)
G3_SU5_EQUALITY_JSON = ROOT / "EXACT_GAUGED_U1X_G3_SU5_EQUALITY_ORBIT_V20.json"
G3_SU5_PHI_ORBIT_JSON = ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_ORBIT_LEMMA_V20.json"
G3_SU5_PHI_LOCAL_COMPONENT_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_LOCAL_COMPONENT_V20.json"
)
G3_SU5_PHI_SU3_SLICE_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_SU3_SLICE_V20.json"
)
G3_SU5_GAP_JSON = ROOT / "EXACT_GAUGED_U1X_G3_SU5_CHIRAL_GLOBAL_GAP_REDUCTION_V20.json"
G3_ALTERNATIVE_GLOBAL_SOS_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_ALTERNATIVE_GLOBAL_SOS_AUDIT_V20.json"
)
FINAL_G3_EFT_ACCEPTANCE_JSON = ROOT / "FINAL_G3_EFT_ACCEPTANCE_GATE_V20.json"
FINAL_G3_EFT_ACCEPTANCE_CORE_SHA256 = (
    "472770981ee7f9ad5880d614826e687c6d9402c286980b421a2bad7d079f09fb"
)
FINAL_G3_EFT_ACCEPTANCE_RAW_SHA256 = (
    "482f9da84d677e24594ca536a2c257602e02f5187419df5cba5356f771ddbaf0"
)
FINAL_G4_EFT_MATHEMATICAL_JSON = ROOT / "FINAL_G4_EFT_MATHEMATICAL_GATE_V20.json"
FINAL_G4_EFT_MATHEMATICAL_CORE_SHA256 = (
    "931a152aed49eb28bf415a1aca093e923850cf68db3f40ccf1d2027b447a8c09"
)
FINAL_G4_EFT_MATHEMATICAL_RAW_SHA256 = (
    "98664542a4e1bbfba233652737826b974963a31c2e86a15e2d73fda1457d987b"
)
FINAL_G5_EFT_MATHEMATICAL_JSON = ROOT / "FINAL_G5_EFT_MATHEMATICAL_GATE_V20.json"
FINAL_G5_EFT_MATHEMATICAL_CORE_SHA256 = (
    "1b578471e74626e3b186cf7398aebd35349a67f45940b9c37d42bb49c1b8c8ba"
)
FINAL_G5_EFT_MATHEMATICAL_RAW_SHA256 = (
    "6d6e4fd9932a03e35146afb1bca850666e883aaed5e23b73b81f0f703e4e7db9"
)
FINAL_G6_EFT_MATHEMATICAL_JSON = ROOT / "FINAL_G6_EFT_MATHEMATICAL_GATE_V20.json"
FINAL_G6_EFT_GATE_SOURCE = ROOT / "final_g6_eft_mathematical_gate_v20.py"
FINAL_G6_EFT_MATHEMATICAL_CORE_SHA256 = (
    "e34b791478bf9cb00f951819cbfec45a99d51be776889d8a4e13cf1717eee738"
)
FINAL_G6_EFT_MATHEMATICAL_RAW_SHA256 = (
    "85000f555eb3bc4e2e4bc49236a82ce2161987212906d78efd667bb52dd432f8"
)
FINAL_G6_EFT_GATE_SOURCE_RAW_SHA256 = (
    "6ef314bf22e1d6ce43b382b5cb6e7673cef1e328f2f4c38abdafab6038edc150"
)
FINAL_G6_EFT_SPECTRUM_CORE_SHA256 = (
    "abb704133c8be22b424ba20e23387d6f30412e6c82ab3a214e88bd8df5bef9cc"
)
FINAL_G6_EFT_SPECTRUM_SOURCE_RAW_SHA256 = (
    "cdcc25b383098464fc6312d553dff555d19c57388df7de08db48b4167ebc5a36"
)
FINAL_G6_EFT_SPECTRUM_JSON_RAW_SHA256 = (
    "797a90473c064a78ef313d56f1894d71114643a19ebd373e86fe8b2911bcf416"
)
EFT_MODEL_CONTRACT_ID = (
    "gauged_u1x_phi17_v20_eft_o6_current_kernel_gamma_1_over_20"
)
G3_SU5_FIXED_F_OFFKERNEL_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_SU5_FIXED_F_OFFKERNEL_BOUND_V20.json"
)
G3_SU5_MAX_NEGATIVE_ZERO_RESIDUAL_JSON = (
    ROOT
    / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_ZERO_RESIDUAL_BOUND_V20.json"
)
G3_SU5_MAX_NEGATIVE_FULL_RESIDUAL_JSON = (
    ROOT
    / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_FULL_RESIDUAL_BOUND_V20.json"
)
G3_SU5_MAX_NEGATIVE_RANK1_SU3_SLICE_JSON = (
    ROOT
    / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_RANK1_SU3_SLICE_V20.json"
)
G3_RANK1_SU4_STABILIZER_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_STABILIZER_V20.json"
)
G3_RANK1_SU4_PHI210_INTERTWINERS_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_INTERTWINERS_V20.json"
)
G3_RANK1_SU4_ALIGNED_CARRIERS_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_ALIGNED_CARRIERS_V20.json"
)
G3_RANK1_SU4_PHI210_QUADRATIC_BASIS_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_QUADRATIC_BASIS_V20.json"
)
G3_RANK1_SU4_AUGMENTED_SOS_CENSUS_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CENSUS_V20.json"
)
G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_V20.json"
)
G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.json"
)
G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_V20.json"
)
RANK1_SU4_ORDERED_LABELS = (
    "H1",
    "H2",
    "H3",
    "X12",
    "Y12",
    "X13",
    "Y13",
    "X14",
    "Y14",
    "X23",
    "Y23",
    "X24",
    "Y24",
    "X34",
    "Y34",
)
RANK1_SU4_MODULAR_PRIME = 1_000_003
RANK1_SU4_BRANCHING = {
    "1": 4, "4": 4, "4bar": 4, "6": 4, "10": 1,
    "10bar": 1, "15": 2, "20": 2, "20bar": 2, "20prime": 1,
}

STATUS_CLOSED = "CLOSED"
STATUS_PARTIAL = "PARTIAL"
STATUS_OPEN = "OPEN"
STATUS_BLOCKED = "BLOCKED"

AUTHORITATIVE_CONTRACT_ID = "gauged_u1x_phi17_v20"
HISTORICAL_CONTRACT_ID = "historical_option_c_no_x_v20"
STATIC_CONTRACT_BLOCKER = exact_x.STATIC_CONTRACT_BLOCKER
CONTRACT_BLOCKER = exact_x.EXTERNAL_EXECUTION_BLOCKER

DEPENDENCIES: dict[str, list[str]] = {
    "MODEL_CONTRACT": [],
    "G1": ["MODEL_CONTRACT"],
    "G2": ["G1"],
    "G3": ["G2"],
    "G4": ["G2", "G3"],
    "G5": ["G1", "G2"],
    "G6": ["G3", "G4", "G5"],
    "G7": ["G6"],
    "G8": ["G3", "G6", "G7"],
}


def _root_contract_evidence_complete(x_report: dict[str, Any]) -> bool:
    """Require native syntax plus v2 bound execution evidence for promotion."""
    scaffold = x_report.get("executable_scaffold_contract", {})
    lagrangian = scaffold.get("lagrangian", {})
    external = x_report.get("external_model_validation", {})
    external_checks = external.get("checks", {})
    required_external = (
        "tool_native_model_format_matches_path",
        "external_process_command_matches_tool",
        "input_manifest_schema_is_supported",
        "input_manifest_sha256_matches_entries",
        "primary_model_is_bound_in_input_manifest",
        "validation_driver_is_bound_to_command",
        "captured_process_log_is_hash_bound",
        "captured_process_log_has_all_required_pass_markers",
    )
    return bool(
        scaffold.get("model_syntax_class") == "sarah_native"
        and scaffold.get("tool_native_sarah_syntax") is True
        and scaffold.get("statically_executable_model_contract") is True
        and lagrangian.get("registered_in_GaugeES_LagrangianInput") is True
        and external.get("schema") == exact_x.EXTERNAL_VALIDATION_SCHEMA
        and external.get("valid") is True
        and all(external_checks.get(name) is True for name in required_external)
    )


def _acyclic_dependencies() -> bool:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return False
        if node in visited:
            return True
        if node not in DEPENDENCIES:
            return False
        visiting.add(node)
        if not all(visit(parent) for parent in DEPENDENCIES[node]):
            return False
        visiting.remove(node)
        visited.add(node)
        return True

    return all(visit(node) for node in DEPENDENCIES)


def _historical_option_c_subtheorems() -> dict[str, Any]:
    """Preserve prior calculations without promoting them across contracts."""
    return {
        "model_contract_id": HISTORICAL_CONTRACT_ID,
        "authoritative_for_gauged_model": False,
        "scope_warning": (
            "These results are conditional theorems of the historical no-X "
            "potential and cannot close the manuscript's gauged-U(1)_X gates."
        ),
        "source_contract_ids": {
            "G1": historical_g1.MODEL_CONTRACT_ID,
            "G2": historical_g2.MODEL_CONTRACT_ID,
            "G3_hessian": historical_g3_hessian.MODEL_CONTRACT_ID,
            "G3_search": historical_g3_search.MODEL_CONTRACT_ID,
        },
        "G1": {
            "scoped_status": "CLOSED_UNDER_HISTORICAL_OPTION_C",
            "base_tensor_families": 18,
            "invariant_directions": 64,
            "real_potential_parameters": 91,
        },
        "G2": {
            "scoped_status": "CLOSED_UNDER_HISTORICAL_OPTION_C",
            "real_field_dimension": 486,
            "gradient_entries": 486,
            "dense_Hessian_shape": [486, 486],
            "symmetric_Hessian_entries": 118341,
        },
        "G3": {
            "scoped_status": "PHYSICAL_SADDLE_UNDER_HISTORICAL_OPTION_C",
            "stationary_tadpoles": 486,
            "massive_physical_quotient_dimension": 449,
            "anchored_witness_negative_modes": 46,
            "anchored_witness_zero_modes": 0,
            "anchored_witness_positive_modes": 403,
            "stationary_affine_dimension": 77,
            "stability_search_iterations": 80,
            "best_minimum_equilibrated_eigenvalue": -0.025502339625368114,
            "strict_local_minimum_found": False,
            "whole_gauged_model_excluded": False,
        },
    }


@lru_cache(maxsize=1)
def _load_or_build_gauged_g2_report() -> dict[str, Any]:
    """Reuse the release artifact; build it when the ledger runs standalone."""
    if gauged_g2.OUT_JSON.exists():
        try:
            report = json.loads(gauged_g2.OUT_JSON.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            report = None
        if (
            isinstance(report, dict)
            and report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
            and "stationary_Hessian_bridge" in report
            and "counts" in report
            and "flags" in report
            and report["flags"].get(
                "exact_projector_zero_corrected_normalized_SVD_rank_13"
            )
            is True
            and report["flags"].get(
                "stationarity_rank_13_exactly_certified"
            )
            is True
            and report["flags"].get(
                "stationarity_nullity_38_exactly_certified"
            )
            is True
        ):
            return report
    return gauged_g2.build_report()


def _load_json_artifact(path: Path) -> dict[str, Any]:
    """Load a required release artifact without silently rebuilding its claims."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _renormalizable_g1_component_tensor_closure(
    report: dict[str, Any],
    *,
    raw_sha256: str = "",
    source_raw_sha256: str = "",
) -> dict[str, Any]:
    """Validate the source-bound mathematical G1 theorem without fabricating release."""
    closure = report.get("closure", {})
    classification = report.get("classification", {})
    counts = report.get("counts", {})
    integration = report.get("integration", {})
    release_blockers = set(report.get("release_blockers", []))
    integration_keys = {
        "consumed_by_central_G1_G8_ledger",
        "consumed_by_execution_roadmap",
        "consumed_by_validation_matrix",
        "release_orchestrators_execute_read_only",
    }
    integration_values = {
        name: integration.get(name) for name in sorted(integration_keys)
    }
    integration_complete = bool(
        set(integration) == integration_keys
        and all(value is True for value in integration_values.values())
    )
    integration_pending = bool(
        set(integration) == integration_keys
        and all(value is False for value in integration_values.values())
    )
    integration_blocker = "G1_COMPONENT_TENSOR_CLOSURE_DOWNSTREAM_INTEGRATION_REQUIRED"
    integration_state_fail_closed = bool(
        (integration_complete and integration_blocker not in release_blockers)
        or (integration_pending and integration_blocker in release_blockers)
    )
    direction_ids = list(report.get("direction_ids", []))
    parameter_ids = list(report.get("parameter_ids", []))
    family_ids = list(report.get("family_ids", []))
    embedded_checks = report.get("checks", {})
    source_hashes = report.get("source_sha256", {})
    checks = {
        "artifact_present": bool(report),
        "status_exact": (
            report.get("status")
            == "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_RING_CLOSED"
            and report.get("overall_state") == "CLOSED_SUBPROBLEM"
            and report.get("n_failed") == 0
            and report.get("failures") == []
        ),
        "core_sha256_exact": (
            report.get("core_sha256")
            == RENORMALIZABLE_G1_COMPONENT_TENSOR_CORE_SHA256
        ),
        "raw_sha256_exact": (
            raw_sha256 == RENORMALIZABLE_G1_COMPONENT_TENSOR_RAW_SHA256
        ),
        "source_raw_sha256_exact": (
            source_raw_sha256
            == RENORMALIZABLE_G1_COMPONENT_TENSOR_SOURCE_RAW_SHA256
        ),
        "model_contract_exact": (
            report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        ),
        "canonical_direction_map_exact": (
            report.get("canonical_direction_map_sha256")
            == RENORMALIZABLE_G1_DIRECTION_MAP_SHA256
        ),
        "counts_exact": (
            counts.get("multidegrees") == 34
            and counts.get("Hermitian_conjugacy_orbits") == 28
            and counts.get("invariant_directions") == 44
            and counts.get("self_conjugate_directions") == 37
            and counts.get("complex_paired_directions") == 7
            and counts.get("real_parameters") == 51
            and counts.get("tensor_families") == 18
            and counts.get("real_field_dimension") == 486
        ),
        "canonical_ids_are_complete_and_unique": (
            len(direction_ids) == len(set(direction_ids)) == 44
            and len(parameter_ids) == len(set(parameter_ids)) == 51
            and len(family_ids) == len(set(family_ids)) == 18
            and sum(item.startswith("lambda::") for item in parameter_ids) == 37
            and sum(item.startswith("re::") for item in parameter_ids) == 7
            and sum(item.startswith("im::") for item in parameter_ids) == 7
        ),
        "all_embedded_mathematical_checks_pass": (
            len(embedded_checks) == 21
            and all(value is True for value in embedded_checks.values())
        ),
        "all_source_hashes_are_portable_sha256": (
            report.get("source_hash_convention")
            == "text bytes canonicalized to LF before SHA-256"
            and len(source_hashes) == 18
            and all(
                isinstance(value, str)
                and len(value) == 64
                and set(value).issubset(set("0123456789abcdef"))
                for value in source_hashes.values()
            )
        ),
        "mathematical_G1_closure_exact": (
            closure.get("declared_symmetry_charge_multidegrees_degree_le_4_closed")
            is True
            and closure.get("so10_singlet_multiplicities_degree_le_4_closed")
            is True
            and closure.get("gauged_u1x_44_direction_subcensus_closed") is True
            and closure.get("explicit_component_tensor_subset_integration_closed")
            is True
            and closure.get("normalized_component_tensor_basis_all_44_directions_closed")
            is True
            and closure.get("full_renormalizable_G1_mathematical_ring_closed")
            is True
            and closure.get("external_model_execution_contract_closed") is False
        ),
        "mathematical_not_authoritative_or_release": (
            classification.get("scoped_mathematical_G1_closed") is True
            and classification.get("authoritative_G1_promoted_closed") is False
            and classification.get("release_G1_verified") is False
            and classification.get("renormalizable_model_mutated") is False
            and classification.get("new_physics_required_for_G1") is False
        ),
        "external_SARAH_blocker_preserved": CONTRACT_BLOCKER in release_blockers,
        "downstream_integration_state_is_fail_closed": integration_state_fail_closed,
    }
    source_bound = all(checks.values())
    return {
        "namespace": "RENORMALIZABLE_G1_COMPONENT_TENSOR_CLOSURE",
        "artifact": RENORMALIZABLE_G1_COMPONENT_TENSOR_JSON.name,
        "source": RENORMALIZABLE_G1_COMPONENT_TENSOR_SOURCE.name,
        "expected_core_sha256": RENORMALIZABLE_G1_COMPONENT_TENSOR_CORE_SHA256,
        "core_sha256": report.get("core_sha256"),
        "expected_raw_sha256": RENORMALIZABLE_G1_COMPONENT_TENSOR_RAW_SHA256,
        "raw_sha256": raw_sha256,
        "expected_source_raw_sha256": (
            RENORMALIZABLE_G1_COMPONENT_TENSOR_SOURCE_RAW_SHA256
        ),
        "source_raw_sha256": source_raw_sha256,
        "expected_direction_map_sha256": RENORMALIZABLE_G1_DIRECTION_MAP_SHA256,
        "direction_map_sha256": report.get("canonical_direction_map_sha256"),
        "model_contract_id": report.get("model_contract_id"),
        "source_bound": source_bound,
        "mathematical_G1_closed_for_renormalizable_model": bool(
            source_bound
            and classification.get("scoped_mathematical_G1_closed") is True
        ),
        "authoritative_G1_promoted_closed": False,
        "release_G1_verified": False,
        "renormalizable_model_mutated": False,
        "new_physics_required_for_G1": False,
        "downstream_integration_completed": integration_complete,
        "integration": integration_values,
        "release_blockers": list(report.get("release_blockers", [])) if source_bound else [],
        "counts": dict(counts) if source_bound else {},
        "checks": checks,
    }


def _parallel_eft_g3_acceptance(
    report: dict[str, Any], *, raw_sha256: str = ""
) -> dict[str, Any]:
    """Validate and expose the EFT G3 result without mutating G3 or G4."""
    classification = report.get("classification", {})
    contract = report.get("contract", {})
    mathematical_checks = report.get("mathematical_checks", {})
    production_mapping = report.get("production_mapping", {})
    release_criteria = report.get("release_criteria", {})
    required_release_blockers = {
        "Lambda_EFT_and_positive_Wilson_matching_approved",
        "radiative_stability_completed",
        "external_extended_model_contract_executed",
        "G1_promoted_closed",
        "G2_promoted_closed",
    }
    checks = {
        "artifact_present": bool(report),
        "status_exact": (
            report.get("status")
            == "FINAL_EFT_G3_ACCEPTANCE__MATHEMATICAL_PASS_RELEASE_OPEN"
        ),
        "core_sha256_exact": (
            report.get("core_sha256")
            == FINAL_G3_EFT_ACCEPTANCE_CORE_SHA256
        ),
        "raw_sha256_exact": (
            raw_sha256 == FINAL_G3_EFT_ACCEPTANCE_RAW_SHA256
        ),
        "base_contract_exact": (
            contract.get("base_model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        ),
        "EFT_contract_exact": (
            contract.get("EFT_model_contract_id") == EFT_MODEL_CONTRACT_ID
        ),
        "authoritative_parameter_count_51": (
            contract.get("authoritative_renormalizable_parameter_count") == 51
            and contract.get("authoritative_51_parameter_contract_unchanged")
            is True
        ),
        "selected_nonzero_parameter_count_27": (
            contract.get("selected_nonzero_renormalizable_parameter_count")
            == 27
        ),
        "single_dimension_six_operator": (
            contract.get("dimension_six_operator_count") == 1
            and mathematical_checks.get("operator_is_dimension_six_EFT") is True
        ),
        "EFT_mathematical_G3_closed": (
            classification.get("mathematical_G3_closed_for_EFT_model") is True
            and mathematical_checks.get("EFT_mathematical_G3_flag") is True
            and mathematical_checks.get("arbitrary_486_field_lower_bound")
            is True
            and mathematical_checks.get("selected_global_minimum") is True
            and mathematical_checks.get("unique_declared_symmetry_orbit")
            is True
        ),
        "renormalizable_G3_unchanged_and_open": (
            classification.get(
                "mathematical_G3_closed_for_original_renormalizable_model"
            )
            is False
            and classification.get("renormalizable_gate_mutated") is False
            and mathematical_checks.get("renormalizable_G3_not_relabelled")
            is True
            and production_mapping.get("do_not_flip")
            == "FINAL_G3_ACCEPTANCE_GATE_V20 for the renormalizable model"
        ),
        "G4_not_closed": (
            classification.get("G4_closed") is False
            and mathematical_checks.get("G4_not_relabelled") is True
        ),
        "EFT_release_open": (
            classification.get("release_G3_verified_for_EFT_model") is False
            and required_release_blockers.issubset(
                set(report.get("release_blockers", []))
            )
            and all(
                release_criteria.get(name) is False
                for name in required_release_blockers
            )
        ),
        "parallel_namespace_exact": (
            production_mapping.get("new_parallel_gate_required")
            == "EFT_G3_ACCEPTANCE"
        ),
        "parallel_production_mapping_integrated": (
            classification.get("production_gate_integrated") is True
            and release_criteria.get("authoritative_EFT_contract_registered")
            is True
            and release_criteria.get("clean_production_gate_integration_completed")
            is True
        ),
        "whole_model_not_excluded": (
            classification.get("whole_model_excluded") is False
        ),
    }
    source_bound = all(checks.values())
    return {
        "namespace": "EFT_G3_ACCEPTANCE",
        "artifact": FINAL_G3_EFT_ACCEPTANCE_JSON.name,
        "expected_core_sha256": FINAL_G3_EFT_ACCEPTANCE_CORE_SHA256,
        "core_sha256": report.get("core_sha256"),
        "expected_raw_sha256": FINAL_G3_EFT_ACCEPTANCE_RAW_SHA256,
        "raw_sha256": raw_sha256,
        "EFT_model_contract_id": contract.get("EFT_model_contract_id"),
        "base_model_contract_id": contract.get("base_model_contract_id"),
        "source_bound": source_bound,
        "mathematical_G3_closed_for_EFT_model": bool(
            source_bound
            and classification.get("mathematical_G3_closed_for_EFT_model")
            is True
        ),
        "release_G3_verified_for_EFT_model": False,
        "mathematical_G3_closed_for_original_renormalizable_model": False,
        "renormalizable_gate_mutated": False,
        "G4_closed": False,
        "release_blockers": (
            list(report.get("release_blockers", [])) if source_bound else []
        ),
        "checks": checks,
    }


def _parallel_eft_g4_mathematical(
    report: dict[str, Any], *, raw_sha256: str = ""
) -> dict[str, Any]:
    """Validate the parallel EFT G4 theorem without promoting legacy G4."""
    classification = report.get("classification", {})
    contract = report.get("contract", {})
    mathematical_checks = report.get("mathematical_checks", {})
    hessian = report.get("exact_Hessian_classification", {})
    production_mapping = report.get("production_mapping", {})
    release_criteria = report.get("release_criteria", {})
    required_release_blockers = {
        "Lambda_EFT_and_positive_Wilson_matching_approved",
        "radiative_stability_completed",
        "external_extended_model_contract_executed",
        "G1_promoted_closed",
        "G2_promoted_closed",
        "release_G3_verified_for_EFT_model",
    }
    checks = {
        "artifact_present": bool(report),
        "status_exact": (
            report.get("status")
            == "FINAL_EFT_G4_MATHEMATICAL_PASS_RELEASE_OPEN"
        ),
        "core_sha256_exact": (
            report.get("core_sha256")
            == FINAL_G4_EFT_MATHEMATICAL_CORE_SHA256
        ),
        "raw_sha256_exact": (
            raw_sha256 == FINAL_G4_EFT_MATHEMATICAL_RAW_SHA256
        ),
        "contract_exact_and_renormalizable_contract_unchanged": (
            contract.get("base_model_contract_id") == AUTHORITATIVE_CONTRACT_ID
            and contract.get("EFT_model_contract_id") == EFT_MODEL_CONTRACT_ID
            and contract.get("authoritative_51_parameter_contract_unchanged")
            is True
        ),
        "upstream_cores_exact": (
            report.get("theorem_core_sha256")
            == "2eca279488d92d8bd9eca974c0d598340124f025e62212cd8a188413a6e8b7d0"
            and report.get("upstream_G3_gate_core_sha256")
            == FINAL_G3_EFT_ACCEPTANCE_CORE_SHA256
        ),
        "all_embedded_mathematical_checks_pass": (
            bool(mathematical_checks)
            and all(value is True for value in mathematical_checks.values())
        ),
        "exact_physical_hessian_classification": (
            hessian.get("full_real_dimension") == 486
            and hessian.get("gauge_quotient_dimension_including_axion") == 449
            and hessian.get("massless_physical_axion_modes") == 1
            and hessian.get("massive_transverse_dimension") == 448
            and hessian.get("negative_modes") == 0
            and hessian.get("unexplained_zero_modes") == 0
            and hessian.get("strictly_positive_massive_transverse_modes") == 448
            and hessian.get("Hessian_rank") == 448
            and hessian.get("Hessian_nullity") == 38
            and hessian.get("positive_kappa_family", {}).get(
                "rank448_nullity38_for_every_positive_kappa"
            )
            is True
        ),
        "EFT_mathematical_G4_closed": (
            classification.get("mathematical_G4_closed_for_EFT_model") is True
        ),
        "renormalizable_G4_unchanged_and_open": (
            classification.get(
                "mathematical_G4_closed_for_original_renormalizable_model"
            )
            is False
            and classification.get(
                "authoritative_renormalizable_G4_gate_mutated"
            )
            is False
            and production_mapping.get("do_not_flip")
            == "authoritative renormalizable G4"
        ),
        "EFT_release_open": (
            classification.get("release_G4_verified_for_EFT_model") is False
            and set(report.get("release_blockers", []))
            == required_release_blockers
            and all(
                release_criteria.get(name) is False
                for name in required_release_blockers
            )
        ),
        "parallel_namespace_exact": (
            production_mapping.get("new_parallel_gate")
            == "EFT_G4_MATHEMATICAL"
            and production_mapping.get("release_integration_completed") is True
            and "release_integration_required" not in production_mapping
        ),
        "parallel_integration_completed": (
            release_criteria.get(
                "parallel_EFT_G4_integrated_into_release_orchestrators"
            )
            is True
        ),
        "whole_model_not_validated": (
            classification.get("whole_model_validated") is False
        ),
    }
    source_bound = all(checks.values())
    return {
        "namespace": "EFT_G4_MATHEMATICAL",
        "artifact": FINAL_G4_EFT_MATHEMATICAL_JSON.name,
        "expected_core_sha256": FINAL_G4_EFT_MATHEMATICAL_CORE_SHA256,
        "core_sha256": report.get("core_sha256"),
        "expected_raw_sha256": FINAL_G4_EFT_MATHEMATICAL_RAW_SHA256,
        "raw_sha256": raw_sha256,
        "EFT_model_contract_id": contract.get("EFT_model_contract_id"),
        "base_model_contract_id": contract.get("base_model_contract_id"),
        "source_bound": source_bound,
        "mathematical_G4_closed_for_EFT_model": bool(
            source_bound
            and classification.get("mathematical_G4_closed_for_EFT_model")
            is True
        ),
        "release_G4_verified_for_EFT_model": False,
        "mathematical_G4_closed_for_original_renormalizable_model": False,
        "authoritative_renormalizable_G4_gate_mutated": False,
        "release_blockers": (
            list(report.get("release_blockers", [])) if source_bound else []
        ),
        "checks": checks,
    }


def _parallel_eft_g5_mathematical(
    report: dict[str, Any], *, raw_sha256: str = ""
) -> dict[str, Any]:
    """Validate the parallel EFT G5 theorem without promoting legacy G5."""
    classification = report.get("classification", {})
    contract = report.get("contract", {})
    mathematical_checks = report.get("mathematical_checks", {})
    proof_reuse = report.get("proof_reuse", {})
    production_mapping = report.get("production_mapping", {})
    release_criteria = report.get("release_criteria", {})
    required_release_blockers = {
        "Lambda_EFT_and_positive_Wilson_matching_approved",
        "radiative_stability_completed",
        "external_extended_model_contract_executed",
        "G1_promoted_closed",
        "G2_promoted_closed",
    }
    checks = {
        "artifact_present": bool(report),
        "status_exact": (
            report.get("status")
            == "FINAL_EFT_G5_MATHEMATICAL_GATE__MATHEMATICAL_PASS_RELEASE_OPEN"
        ),
        "core_sha256_exact": (
            report.get("core_sha256")
            == FINAL_G5_EFT_MATHEMATICAL_CORE_SHA256
        ),
        "raw_sha256_exact": (
            raw_sha256 == FINAL_G5_EFT_MATHEMATICAL_RAW_SHA256
        ),
        "contract_exact_and_renormalizable_contract_unchanged": (
            contract.get("base_model_contract_id") == AUTHORITATIVE_CONTRACT_ID
            and contract.get("EFT_model_contract_id") == EFT_MODEL_CONTRACT_ID
            and contract.get("real_field_dimension") == 486
            and contract.get("authoritative_renormalizable_parameter_count")
            == 51
            and contract.get("selected_nonzero_renormalizable_parameter_count")
            == 27
            and contract.get("dimension_six_operator_count") == 1
            and contract.get("authoritative_51_parameter_contract_unchanged")
            is True
        ),
        "all_embedded_mathematical_checks_pass": (
            bool(mathematical_checks)
            and all(value is True for value in mathematical_checks.values())
        ),
        "frozen_theorem_composition_exact": (
            proof_reuse.get("kind")
            == "composition_of_existing_frozen_exact_theorems"
            and proof_reuse.get("new_SOS_constructed_or_claimed") is False
            and proof_reuse.get("EFT_theorem_core_sha256")
            == "2eca279488d92d8bd9eca974c0d598340124f025e62212cd8a188413a6e8b7d0"
            and proof_reuse.get("O6_theorem_core_sha256")
            == "598d916da16e746c8be30e979a13a27a47d1600e2dd4bee7b9cf9fc398ec9da1"
            and proof_reuse.get("immutable_EFT_G3_gate_core_sha256")
            == FINAL_G3_EFT_ACCEPTANCE_CORE_SHA256
            and report.get("exact_global_lower_bound") == "-40661/20000"
        ),
        "EFT_mathematical_G5_closed": (
            classification.get("mathematical_G5_closed_for_EFT_model") is True
            and classification.get("new_SOS_claimed") is False
        ),
        "renormalizable_G5_unchanged_and_blocked": (
            classification.get("authoritative_renormalizable_G5_closed")
            is False
            and classification.get(
                "authoritative_renormalizable_G5_blocked_by_model_contract"
            )
            is True
            and classification.get("authoritative_renormalizable_G5_blocker")
            == CONTRACT_BLOCKER
            and classification.get("authoritative_renormalizable_G5_mutated")
            is False
            and production_mapping.get("do_not_flip")
            == (
                "authoritative G5 in G1_G8_GATE_LEDGER_V20 for the "
                "renormalizable model"
            )
        ),
        "EFT_release_open": (
            classification.get("release_G5_verified_for_EFT_model") is False
            and set(report.get("release_blockers", []))
            == required_release_blockers
            and all(
                release_criteria.get(name) is False
                for name in required_release_blockers
            )
        ),
        "parallel_namespace_exact": (
            report.get("namespace") == "EFT_G5_MATHEMATICAL"
            and production_mapping.get("new_parallel_gate")
            == "EFT_G5_MATHEMATICAL"
            and production_mapping.get("downstream_integration_completed")
            is True
        ),
        "parallel_integration_completed": (
            release_criteria.get("downstream_parallel_G5_integration_completed")
            is True
        ),
        "whole_model_not_excluded": (
            classification.get("whole_model_excluded") is False
        ),
    }
    source_bound = all(checks.values())
    return {
        "namespace": "EFT_G5_MATHEMATICAL",
        "artifact": FINAL_G5_EFT_MATHEMATICAL_JSON.name,
        "expected_core_sha256": FINAL_G5_EFT_MATHEMATICAL_CORE_SHA256,
        "core_sha256": report.get("core_sha256"),
        "expected_raw_sha256": FINAL_G5_EFT_MATHEMATICAL_RAW_SHA256,
        "raw_sha256": raw_sha256,
        "EFT_model_contract_id": contract.get("EFT_model_contract_id"),
        "base_model_contract_id": contract.get("base_model_contract_id"),
        "source_bound": source_bound,
        "mathematical_G5_closed_for_EFT_model": bool(
            source_bound
            and classification.get("mathematical_G5_closed_for_EFT_model")
            is True
        ),
        "release_G5_verified_for_EFT_model": False,
        "authoritative_renormalizable_G5_closed": False,
        "authoritative_renormalizable_G5_blocked_by_model_contract": True,
        "authoritative_renormalizable_G5_mutated": False,
        "new_SOS_claimed": False,
        "release_blockers": (
            list(report.get("release_blockers", [])) if source_bound else []
        ),
        "checks": checks,
    }


def _parallel_eft_g6_spectrum(
    report: dict[str, Any], *, raw_sha256: str = "", gate_source_raw_sha256: str = ""
) -> dict[str, Any]:
    """Validate exact tree-level EFT G6 without promoting authoritative G6."""
    classification = report.get("classification", {})
    contract = report.get("contract", {})
    mathematical_checks = report.get("mathematical_checks", {})
    spectrum = report.get("spectrum_summary", {})
    artifacts = report.get("artifact_sha256", {})
    upstream = report.get("upstream_cores", {})
    release_criteria = report.get("release_criteria", {})
    release_blockers = set(report.get("release_blockers", []))
    nonmathematical_release_criteria = {
        name
        for name in release_criteria
        if name != "mathematical_tree_level_EFT_G6_complete"
    }
    false_release_criteria = {
        name
        for name in nonmathematical_release_criteria
        if release_criteria.get(name) is False
    }
    integration_criterion = release_criteria.get(
        "parallel_EFT_G6_integrated_into_release_orchestrators"
    )
    checks = {
        "artifact_present": bool(report),
        "status_exact": (
            report.get("status")
            == "FINAL_EFT_G6_TREE_LEVEL_MATHEMATICAL_PASS_RELEASE_OPEN"
        ),
        "core_sha256_exact": (
            report.get("core_sha256") == FINAL_G6_EFT_MATHEMATICAL_CORE_SHA256
        ),
        "raw_sha256_exact": raw_sha256 == FINAL_G6_EFT_MATHEMATICAL_RAW_SHA256,
        "gate_source_raw_sha256_exact": (
            gate_source_raw_sha256 == FINAL_G6_EFT_GATE_SOURCE_RAW_SHA256
        ),
        "contract_exact": (
            contract.get("base_model_contract_id") == AUTHORITATIVE_CONTRACT_ID
            and contract.get("EFT_model_contract_id") == EFT_MODEL_CONTRACT_ID
            and contract.get("scope")
            == "normalized exact tree-level dimension-six EFT spectrum"
        ),
        "spectrum_source_and_JSON_raw_pins_exact": (
            artifacts.get("spectrum_source")
            == FINAL_G6_EFT_SPECTRUM_SOURCE_RAW_SHA256
            and artifacts.get("spectrum_JSON")
            == FINAL_G6_EFT_SPECTRUM_JSON_RAW_SHA256
        ),
        "upstream_cores_and_gate_JSON_pins_exact": (
            upstream.get("spectrum") == FINAL_G6_EFT_SPECTRUM_CORE_SHA256
            and upstream.get("G4") == FINAL_G4_EFT_MATHEMATICAL_CORE_SHA256
            and upstream.get("G5") == FINAL_G5_EFT_MATHEMATICAL_CORE_SHA256
            and artifacts.get("G4_gate_JSON")
            == FINAL_G4_EFT_MATHEMATICAL_RAW_SHA256
            and artifacts.get("G5_gate_JSON")
            == FINAL_G5_EFT_MATHEMATICAL_RAW_SHA256
        ),
        "all_embedded_mathematical_checks_pass": (
            bool(mathematical_checks)
            and all(value is True for value in mathematical_checks.values())
        ),
        "complete_exact_tree_level_spectrum": (
            spectrum.get("ambient_real_fields") == 486
            and spectrum.get("gauge_quotient_dimension") == 449
            and spectrum.get("physical_PQ_axions") == 1
            and spectrum.get("positive_massive_modes") == 448
            and spectrum.get("primitive_factors") == 45
            and spectrum.get("distinct_mass_squared_roots_including_zero") == 61
            and spectrum.get("residual_group") == "SU(3)_C x U(1)_em"
            and spectrum.get("mixing_subspaces_complete") is True
        ),
        "EFT_mathematical_G6_closed": (
            classification.get("mathematical_G6_closed_for_EFT_model") is True
            and release_criteria.get("mathematical_tree_level_EFT_G6_complete")
            is True
        ),
        "renormalizable_authoritative_G6_unchanged": (
            classification.get("authoritative_renormalizable_G6_closed") is False
            and classification.get("authoritative_G6_gate_mutated") is False
        ),
        "EFT_release_open_and_criteria_fail_closed": (
            classification.get("release_G6_verified_for_EFT_model") is False
            and nonmathematical_release_criteria
            and all(
                isinstance(release_criteria.get(name), bool)
                for name in nonmathematical_release_criteria
            )
            and release_blockers == false_release_criteria
        ),
        "parallel_integration_state_classified": (
            isinstance(integration_criterion, bool)
            and (
                "parallel_EFT_G6_integrated_into_release_orchestrators"
                in release_blockers
            )
            is (not integration_criterion)
        ),
        "whole_model_not_validated": (
            classification.get("whole_model_validated") is False
        ),
    }
    source_bound = all(checks.values())
    return {
        "namespace": "EFT_G6_TREE_LEVEL_MATHEMATICAL",
        "artifact": FINAL_G6_EFT_MATHEMATICAL_JSON.name,
        "expected_core_sha256": FINAL_G6_EFT_MATHEMATICAL_CORE_SHA256,
        "core_sha256": report.get("core_sha256"),
        "expected_raw_sha256": FINAL_G6_EFT_MATHEMATICAL_RAW_SHA256,
        "raw_sha256": raw_sha256,
        "expected_gate_source_raw_sha256": FINAL_G6_EFT_GATE_SOURCE_RAW_SHA256,
        "gate_source_raw_sha256": gate_source_raw_sha256,
        "expected_spectrum_core_sha256": FINAL_G6_EFT_SPECTRUM_CORE_SHA256,
        "spectrum_core_sha256": upstream.get("spectrum"),
        "expected_spectrum_source_raw_sha256": (
            FINAL_G6_EFT_SPECTRUM_SOURCE_RAW_SHA256
        ),
        "spectrum_source_raw_sha256": artifacts.get("spectrum_source"),
        "expected_spectrum_JSON_raw_sha256": FINAL_G6_EFT_SPECTRUM_JSON_RAW_SHA256,
        "spectrum_JSON_raw_sha256": artifacts.get("spectrum_JSON"),
        "EFT_model_contract_id": contract.get("EFT_model_contract_id"),
        "base_model_contract_id": contract.get("base_model_contract_id"),
        "source_bound": source_bound,
        "mathematical_G6_closed_for_EFT_model": bool(
            source_bound
            and classification.get("mathematical_G6_closed_for_EFT_model") is True
        ),
        "release_G6_verified_for_EFT_model": False,
        "authoritative_renormalizable_G6_closed": False,
        "authoritative_G6_gate_mutated": False,
        "whole_model_validated": False,
        "parallel_integration_completed": integration_criterion is True,
        "spectrum_summary": dict(spectrum) if source_bound else {},
        "release_blockers": list(report.get("release_blockers", [])) if source_bound else [],
        "checks": checks,
    }


def _canonical_json_sha256(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _file_sha256(path: Path) -> str:
    try:
        # Git may materialize text sources with CRLF on Windows.  The frozen
        # provenance certificates use the repository's canonical LF bytes.
        payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        return hashlib.sha256(payload).hexdigest()
    except OSError:
        return ""


def _raw_file_sha256(path: Path) -> str:
    """Hash the exact artifact bytes without newline canonicalization."""
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def _rank1_su4_stabilizer_infrastructure_exact(report: dict[str, Any]) -> bool:
    """Validate the fixed-endpoint SU(4) stabilizer without promoting G3."""
    checks = report.get("checks", {})
    scope = report.get("scope", {})
    tangent = report.get("joint_stabilizer_tangent", {})
    endpoint = tangent.get("fixed_endpoint", {})
    source_actions = tangent.get("source_actions", {})
    phi210 = report.get("Phi210_action", {})
    required_checks = (
        "fifteen_correct_shifted_SU4_generators_exact",
        "fixed_h_minus_q_over_4_endpoint_bound_exact",
        "joint_tangent_rank_30_modular_lower_bound_exact",
        "explicit_fifteen_dimensional_kernel_upper_bound_exact",
        "joint_stabilizer_kernel_exhausted_exactly_by_SU4",
        "old_offset_zero_SU4_embedding_rejected_by_h_minus_exactly",
        "integral_SU4_Lie_structure_constants_close_exactly",
        "Phi210_actions_integral_skew_faithful_and_Lie_exact",
    )
    required_scope_keys = {
        "G3_closed",
        "H_fixed_to_h_minus",
        "Sigma_fixed_to_normalized_explicit_decomposable_pure_spinor_q_over_4",
        "arbitrary_Phi_Schur_SOS_SDP_constructed",
        "arbitrary_Phi_Schur_SOS_SDP_feasible",
        "arbitrary_max_negative_Sigma_proved",
        "arbitrary_rank1_Phi_bound_proved",
        "common_continuous_stabilizer_identified_as_SU4",
        "exact_Phi210_SU4_action_available_for_next_stage",
        "infrastructure_only",
        "whole_model_excluded",
    }
    required_endpoint_keys = {
        "H",
        "H_numerator_norm_squared",
        "Sigma",
        "endpoint_binding_exact",
        "integer_tangent_numerators",
        "q",
        "q_coordinate_norm_squared",
    }
    generator_basis = report.get("generator_basis", {})
    lie_algebra = report.get("Lie_algebra", {})
    wrong_offset = tangent.get("wrong_offset_zero_SU4_negative_control", {})
    return bool(
        report.get("n_checks") == len(required_checks)
        and report.get("n_failed") == 0
        and report.get("failed_checks") == []
        and report.get("status")
        == "EXACT_RANK1_SU4_STABILIZER_INFRASTRUCTURE_CERTIFIED"
        and report.get("overall_state")
        == "STABILIZER_INFRASTRUCTURE_CLOSED__ARBITRARY_PHI_SDP_OPEN"
        and report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and set(checks) == set(required_checks)
        and set(scope) == required_scope_keys
        and set(endpoint) == required_endpoint_keys
        and all(checks.get(name) is True for name in required_checks)
        and scope.get("H_fixed_to_h_minus") is True
        and scope.get(
            "Sigma_fixed_to_normalized_explicit_decomposable_pure_spinor_q_over_4"
        )
        is True
        and scope.get("common_continuous_stabilizer_identified_as_SU4") is True
        and scope.get("exact_Phi210_SU4_action_available_for_next_stage") is True
        and scope.get("infrastructure_only") is True
        and scope.get("arbitrary_Phi_Schur_SOS_SDP_constructed") is False
        and scope.get("arbitrary_Phi_Schur_SOS_SDP_feasible") is False
        and scope.get("arbitrary_rank1_Phi_bound_proved") is False
        and scope.get("arbitrary_max_negative_Sigma_proved") is False
        and scope.get("G3_closed") is False
        and scope.get("whole_model_excluded") is False
        and tangent.get("proof_grade") is True
        and tangent.get("prime") == RANK1_SU4_MODULAR_PRIME
        and tangent.get("displayed_kernel_rank_mod_prime") == 15
        and tangent.get("displayed_kernel_residual_max_abs") == 0
        and tangent.get("exact_tangent_rank_over_Q_R") == 30
        and tangent.get("exact_tangent_nullity") == 15
        and tangent.get("displayed_kernel_shape") == [45, 15]
        and tangent.get("explicit_kernel_is_complete") is True
        and tangent.get("joint_tangent_rank_mod_prime") == 30
        and tangent.get("joint_tangent_shape") == [272, 45]
        and tangent.get("rank_lower_bound_over_Q_R") == 30
        and tangent.get("kernel_upper_bound_on_tangent_rank") == 30
        and endpoint.get("endpoint_binding_exact") is True
        and endpoint.get("H") == "h_-=(e0-i e1)/sqrt(2)"
        and endpoint.get("Sigma") == "q/4"
        and endpoint.get("q")
        == "q=(e0+i e1)(e2+i e3)(e4+i e5)(e6+i e7)(e8+i e9)"
        and endpoint.get("H_numerator_norm_squared") == 2
        and endpoint.get("q_coordinate_norm_squared") == 16
        and source_actions.get("SO10_generator_count") == 45
        and source_actions.get("H_action_shape") == [45, 10, 10]
        and source_actions.get("Sigma_action_shape") == [45, 126, 126]
        and source_actions.get("ordered_generator_labels_match_exactly") is True
        and source_actions.get("H_generators_integral_real_skew") is True
        and source_actions.get(
            "Sigma_generators_Gaussian_integral_antihermitian"
        )
        is True
        and wrong_offset.get("H_tangent_residual_max_abs") == 1
        and wrong_offset.get("Sigma_tangent_residual_max_abs") == 0
        and wrong_offset.get("joint_tangent_residual_max_abs") == 1
        and wrong_offset.get("does_not_stabilize_fixed_h_minus") is True
        and wrong_offset.get("wrong_embedding_rejected_exactly") is True
        and phi210.get("proof_grade") is True
        and phi210.get("prime") == RANK1_SU4_MODULAR_PRIME
        and phi210.get("representation") == "real Lambda^4(R^10) = Phi210"
        and phi210.get("action_count") == 15
        and phi210.get("action_shapes") == [[210, 210]]
        and phi210.get("ordered_labels") == list(RANK1_SU4_ORDERED_LABELS)
        and phi210.get("all_action_dtypes_integral") is True
        and phi210.get("maximum_abs_action_entry") == 1
        and phi210.get("flattened_action_rank_mod_prime") == 15
        and phi210.get("skew_transpose_max_abs_residual") == 0
        and phi210.get("Lie_commutator_reconstruction_max_abs") == 0
        and bool(phi210.get("source_binding"))
        and generator_basis.get("proof_grade") is True
        and generator_basis.get("prime") == RANK1_SU4_MODULAR_PRIME
        and generator_basis.get("generator_count") == 15
        and generator_basis.get("Cartan_generator_count") == 3
        and generator_basis.get("offdiagonal_generator_count") == 12
        and generator_basis.get("complex_planes")
        == [[2, 3], [4, 5], [6, 7], [8, 9]]
        and generator_basis.get("coefficient_matrix_shape") == [45, 15]
        and generator_basis.get("coefficient_rank_mod_prime") == 15
        and generator_basis.get("ordered_labels") == list(RANK1_SU4_ORDERED_LABELS)
        and generator_basis.get("all_coefficients_are_signed_units") is True
        and generator_basis.get("all_support_is_in_indices_2_through_9") is True
        and lie_algebra.get("proof_grade") is True
        and lie_algebra.get("Lie_algebra_dimension") == 15
        and lie_algebra.get("basis_labels") == list(RANK1_SU4_ORDERED_LABELS)
        and lie_algebra.get("Cartan_commutator_max_abs") == 0
        and lie_algebra.get("Jacobi_max_abs_residual") == 0
        and lie_algebra.get("antisymmetry_max_abs_residual") == 0
        and lie_algebra.get("coefficient_commutator_reconstruction_max_abs") == 0
        and lie_algebra.get("vector_commutator_reconstruction_max_abs") == 0
        and lie_algebra.get("maximum_abs_structure_constant") == 2
        and lie_algebra.get("coordinate_block_unimodular") is True
        and lie_algebra.get("structure_constants_integral") is True
    )


def _rank1_su4_phi210_intertwiners_exact(
    report: dict[str, Any], stabilizer_report: dict[str, Any]
) -> bool:
    """Validate the 210 intertwiner census and every open-scope guard."""
    checks = report.get("checks", {})
    scope = report.get("scope", {})
    provenance = report.get("companion_stabilizer_provenance", {})
    intertwiner = report.get("intertwiner", {})
    rows = intertwiner.get("intertwinings", [])
    carriers = report.get("carriers", {})
    carrier_rows = carriers.get("carriers", [])
    character = report.get("character_branching", {})
    integral_c8 = report.get("integral_C8", {})
    companion_tangent = stabilizer_report.get("joint_stabilizer_tangent", {})
    companion_phi210 = stabilizer_report.get("Phi210_action", {})
    required_true_checks = (
        "Gaussian_exterior_basis_Bdagger_B_equals_16I_exact",
        "all_15_live_SU4_intertwinings_exact",
        "Cartan_weights_exact",
        "SSYT_character_branching_exact",
        "integral_C8_spectrum_and_minimal_polynomial_exact",
        "deterministic_25_carrier_decomposition_complete",
        "Sym2_invariant_multiplicity_is_45_exact",
        "companion_model_contract_matches_exactly",
        "companion_stabilizer_report_green_and_endpoint_scoped",
        "companion_h_minus_q_over_4_tangent_provenance_exact",
        "companion_Phi210_action_provenance_exact",
        "companion_embedded_certificates_match_live_inputs",
    )
    required_false_checks = {
        "SU4_Schur_SDP_constructed",
        "arbitrary_Phi_bound_proved",
        "G3_closed",
    }
    required_scope_keys = {
        "G3_closed",
        "H_fixed_to_h_minus",
        "Phi210_complexified_representation_resolved",
        "SU4_invariant_quadratic_form_basis_constructed",
        "Schur_SOS_SDP_constructed",
        "Sigma_fixed_to_q_over_4",
        "Sym2_SU4_invariant_dimension_45_proved",
        "arbitrary_rank1_Phi_proved",
        "arbitrary_real_Phi_lower_bound_proved",
        "companion_stabilizer_provenance_exact",
        "deterministic_irreducible_carriers_complete",
        "rank1_endpoint_SU4_stabilizer_used",
        "whole_model_excluded",
    }
    required_provenance_keys = {
        "Phi210_action_proof_grade",
        "all_required_provenance_exact",
        "fixed_endpoint",
        "model_contract_id",
        "module",
        "n_failed",
        "overall_state",
        "status",
        "tangent_proof_grade",
    }
    return bool(
        _rank1_su4_stabilizer_infrastructure_exact(stabilizer_report)
        and report.get("n_checks") == 15
        and report.get("n_failed") == 0
        and report.get("failures") == []
        and report.get("status")
        == "EXACT_RANK1_SU4_PHI210_INTERTWINER_INFRASTRUCTURE_CERTIFIED"
        and report.get("overall_state")
        == "SU4_SCHUR_INFRASTRUCTURE_CLOSED__SDP_AND_G3_OPEN"
        and report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and set(checks) == set(required_true_checks) | required_false_checks
        and set(scope) == required_scope_keys
        and set(provenance) == required_provenance_keys
        and all(checks.get(name) is True for name in required_true_checks)
        and checks.get("SU4_Schur_SDP_constructed") is False
        and checks.get("arbitrary_Phi_bound_proved") is False
        and checks.get("G3_closed") is False
        and scope.get("H_fixed_to_h_minus") is True
        and scope.get("Sigma_fixed_to_q_over_4") is True
        and scope.get("rank1_endpoint_SU4_stabilizer_used") is True
        and scope.get("companion_stabilizer_provenance_exact") is True
        and scope.get("Phi210_complexified_representation_resolved") is True
        and scope.get("deterministic_irreducible_carriers_complete") is True
        and scope.get("Sym2_SU4_invariant_dimension_45_proved") is True
        and scope.get("SU4_invariant_quadratic_form_basis_constructed") is False
        and scope.get("Schur_SOS_SDP_constructed") is False
        and scope.get("arbitrary_real_Phi_lower_bound_proved") is False
        and scope.get("arbitrary_rank1_Phi_proved") is False
        and scope.get("G3_closed") is False
        and scope.get("whole_model_excluded") is False
        and provenance.get("all_required_provenance_exact") is True
        and provenance.get("module")
        == "exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py"
        and provenance.get("model_contract_id")
        == stabilizer_report.get("model_contract_id")
        and provenance.get("n_failed") == stabilizer_report.get("n_failed")
        and provenance.get("status") == stabilizer_report.get("status")
        and provenance.get("overall_state")
        == stabilizer_report.get("overall_state")
        and provenance.get("fixed_endpoint")
        == companion_tangent.get("fixed_endpoint")
        and provenance.get("tangent_proof_grade")
        == companion_tangent.get("proof_grade")
        and provenance.get("Phi210_action_proof_grade")
        == companion_phi210.get("proof_grade")
        and intertwiner.get("proof_grade") is True
        and intertwiner.get("exterior_basis_shape") == [210, 210]
        and intertwiner.get("exterior_basis_Bdagger_B_equals_16I_exact") is True
        and intertwiner.get("one_form_Gram_real_exact") is True
        and intertwiner.get("one_form_Gram_imaginary_zero_exact") is True
        and intertwiner.get("Cartan_weight_diagonalization_exact") is True
        and intertwiner.get("n_distinct_Cartan_weights") == 65
        and intertwiner.get("zero_weight_multiplicity") == 12
        and intertwiner.get("intertwining_count") == 15
        and intertwiner.get("all_15_intertwinings_exact") is True
        and isinstance(rows, list)
        and len(rows) == 15
        and all(
            row.get("exact") is True
            and row.get("real_residual_max_abs") == 0
            and row.get("imaginary_residual_max_abs") == 0
            for row in rows
            if isinstance(row, dict)
        )
        and all(isinstance(row, dict) for row in rows)
        and [row.get("generator") for row in rows]
        == list(RANK1_SU4_ORDERED_LABELS)
        and character.get("proof_grade") is True
        and character.get("exterior_dimension") == 210
        and character.get("SSYT_reconstructed_dimension") == 210
        and character.get("all_SSYT_dimensions_exact") is True
        and character.get("SSYT_character_identity_exact") is True
        and integral_c8.get("proof_grade") is True
        and integral_c8.get("shape") == [210, 210]
        and integral_c8.get("integral") is True
        and integral_c8.get("symmetric_exact") is True
        and integral_c8.get("commutes_with_all_15_generators_exact") is True
        and integral_c8.get("spectrum_exact_over_Q") is True
        and integral_c8.get("minimal_polynomial_exact") is True
        and integral_c8.get("minimal_polynomial_annihilates_exact") is True
        and integral_c8.get("modular_prime") == RANK1_SU4_MODULAR_PRIME
        and integral_c8.get("minimal_polynomial_roots")
        == [0, 15, 20, 32, 36, 39, 48]
        and integral_c8.get("annihilator_intermediate_maxima")[-1:] == [0]
        and integral_c8.get("modular_nullities_sum") == 210
        and integral_c8.get("modular_eigenspace_nullities")
        == {
            "0": 4,
            "15": 32,
            "20": 24,
            "32": 30,
            "36": 20,
            "39": 80,
            "48": 20,
        }
        and integral_c8.get("expected_spectrum_multiplicities")
        == {
            "0": 4,
            "15": 32,
            "20": 24,
            "32": 30,
            "36": 20,
            "39": 80,
            "48": 20,
        }
        and integral_c8.get("canonical_Phi210_symmetric_exact") is True
        and integral_c8.get("canonical_to_exterior_C8_intertwining_exact") is True
        and integral_c8.get("imaginary_part_zero_exact") is True
        and integral_c8.get("int64_arithmetic_safe") is True
        and carriers.get("proof_grade") is True
        and carriers.get("carrier_count") == 25
        and carriers.get("concatenated_carrier_shape") == [210, 210]
        and carriers.get("concatenated_carrier_rank_mod_prime") == 210
        and carriers.get("Sym2_Phi210_SU4_singlet_dimension") == 45
        and carriers.get("SU4_invariant_quadratic_multiplicity_sector_dimension")
        == 45
        and "future_Schur_SDP_multiplicity_matrix_dimension" not in carriers
        and carriers.get("natural_exterior_block_count") == 16
        and isinstance(carrier_rows, list)
        and len(carrier_rows) == 25
        and all(
            isinstance(row, dict)
            and row.get("C8_eigen_equation_exact") is True
            and row.get("SSYT_character_exact") is True
            and row.get("exact_modular_rank") == row.get("expected_dimension")
            for row in carrier_rows
        )
        and carriers.get("all_15_generators_preserve_natural_blocks_exact")
        is True
        and carriers.get("all_carrier_dimensions_eigenvalues_characters_exact")
        is True
    )


def _rank1_su4_aligned_carriers_exact(
    report: dict[str, Any],
    intertwiners_report: dict[str, Any],
    stabilizer_report: dict[str, Any],
) -> bool:
    """Fail closed on the literal 25-carrier alignment and physical real maps."""
    checks = report.get("checks", {})
    scope = report.get("scope", {})
    provenance = report.get("upstream_provenance", {})
    source = provenance.get("source_contract", {})
    alignment = report.get("alignment", {})
    alignment_provenance = report.get("alignment_provenance", {})
    carriers = alignment.get("carriers", [])
    families = alignment.get("families", [])
    true_checks = {
        "model_contract_and_endpoint_provenance_exact",
        "upstream_source_bytes_match_pinned_contract_exact",
        "upstream_full_schema_and_literal_certificates_exact",
        "upstream_intertwiner_report_green_and_scope_exact",
        "upstream_live_Gaussian_intertwiner_exact",
        "upstream_25_carrier_census_exact",
        "upstream_embedded_certificates_match_live_inputs",
        "alignment_full_schema_and_literals_exact",
        "integral_A3_Chevalley_system_exact",
        "integer_and_rational_arithmetic_safety_exact",
        "deterministic_lowering_words_align_all_25_carriers_exact",
        "common_source_actions_on_all_equivalent_copies_exact",
        "physical_live_Phi210_embeddings_exact",
        "physical_conjugation_and_real_structures_exact",
        "aligned_25_carrier_direct_sum_rank_210_exact",
    }
    false_checks = {
        "SU4_invariant_quadratic_basis_constructed",
        "Schur_SOS_SDP_constructed",
        "arbitrary_real_Phi_lower_bound_proved",
        "G3_closed",
    }
    true_scope = {
        "H_fixed_to_h_minus", "Sigma_fixed_to_q_over_4",
        "rank1_endpoint_SU4_stabilizer_used",
        "aligned_complexified_Phi210_carriers_constructed",
        "physical_real_structure_and_Gaussian_embeddings_constructed",
    }
    false_scope = {
        "SU4_invariant_quadratic_form_basis_constructed",
        "Schur_SOS_SDP_constructed", "arbitrary_real_Phi_lower_bound_proved",
        "arbitrary_rank1_Phi_proved", "G3_closed", "whole_model_excluded",
    }
    provenance_keys = {
        "module", "model_contract_id", "status", "n_failed",
        "intertwiner_proof_grade", "carrier_proof_grade",
        "embedded_certificates_match", "source_contract",
        "source_contract_exact", "upstream_report_sha256",
        "expected_upstream_report_sha256",
        "upstream_intertwiner_certificate_sha256",
        "expected_upstream_intertwiner_certificate_sha256",
        "upstream_carrier_certificate_sha256",
        "expected_upstream_carrier_certificate_sha256",
        "full_schema_and_literals_exact", "all_required_provenance_exact",
    }
    source_keys = {
        "upstream_module", "upstream_module_sha256",
        "expected_upstream_module_sha256", "stabilizer_module",
        "stabilizer_module_sha256", "expected_stabilizer_module_sha256",
        "both_modules_resolve_to_repository_root_exact",
        "source_bytes_match_pinned_contract_exact", "proof_grade",
    }
    alignment_keys = {
        "proof_grade", "modular_prime", "generator_labels",
        "simple_Chevalley_system", "family_count", "families", "carrier_count",
        "carriers", "expected_irrep_multiplicities",
        "observed_irrep_multiplicities", "upstream_carrier_order_exact",
        "all_family_word_counts_equal_dimensions", "all_25_carriers_exact",
        "all_equivalent_copies_use_common_source_actions_exact",
        "concatenated_aligned_basis_shape",
        "concatenated_aligned_basis_rank_mod_prime",
        "concatenated_aligned_basis_sha256", "exact_rank_argument",
        "exterior_conjugation_shape",
        "exterior_conjugation_signed_permutation_exact",
        "exterior_conjugation_square_equals_identity_exact",
        "Gaussian_basis_conjugation_is_physical_exact",
        "all_25_physical_Gaussian_embeddings_intertwine_live_Phi210_exact",
        "all_25_conjugate_carrier_maps_exact",
        "all_25_conjugate_maps_involutive_exact",
        "conjugation_compatible_with_all_15_generators_exact",
        "complex_type_carrier_count", "self_conjugate_real_type_carrier_count",
        "rational_matrix_convention",
        "exact_integer_and_rational_arithmetic_safety",
    }
    carrier_keys = {
        "name", "irrep", "copy_index", "highest_weight", "dimension",
        "natural_block", "lowering_word_count", "lowering_word_maximum_length",
        "basis_maximum_absolute_entry", "basis_sha256",
        "aligned_rank_mod_prime", "highest_weight_primitive_and_raising_annihilated",
        "C8_eigen_equation_exact", "all_15_common_source_actions_intertwine_exact",
        "natural_block_support_exact", "source_action_denominators",
        "exterior_gram_sha256", "canonical_basis_real_sha256",
        "canonical_basis_imaginary_sha256",
        "all_15_live_canonical_Phi210_actions_intertwine_exact",
        "reality_kind", "conjugate_carrier_name", "conjugation_map_denominator",
        "conjugation_map_sha256", "conjugation_involution_exact",
        "physical_conjugation_embedding_exact",
    }
    family_keys = {
        "irrep", "dimension", "multiplicity", "reference_carrier_name",
        "lowering_words", "lowering_word_sha256", "common_source_action_count",
        "common_source_actions_sha256",
    }
    names = {row.get("name") for row in carriers if isinstance(row, dict)}
    rows_by_name = {
        row.get("name"): row for row in carriers if isinstance(row, dict)
    }
    upstream_intertwiner = intertwiners_report.get("intertwiner", {})
    upstream_carriers = intertwiners_report.get("carriers", {})
    expected_alignment_hash = (
        "f74b7845b57472f62773c398fa927b551b5d9d09f86bd7defb92a6ed71adbe15"
    )
    return bool(
        _rank1_su4_phi210_intertwiners_exact(
            intertwiners_report, stabilizer_report
        )
        and _canonical_json_sha256(report)
        == "d2da0572dc33a1f3f88b5ac5df3343201650ca660498f34ff59806a607015c67"
        and set(report) == {
            "status", "overall_state", "model_contract_id", "n_checks",
            "n_failed", "failures", "checks", "upstream_provenance",
            "alignment", "alignment_provenance", "scope", "next_exact_target",
            "verdict",
        }
        and report.get("status")
        == "EXACT_RANK1_SU4_ALIGNED_CARRIER_INFRASTRUCTURE_CERTIFIED"
        and report.get("overall_state")
        == "SU4_ALIGNED_CARRIERS_CLOSED__INVARIANT_BASIS_SDP_AND_G3_OPEN"
        and report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and report.get("n_checks") == 19
        and report.get("n_failed") == 0 and report.get("failures") == []
        and set(checks) == true_checks | false_checks
        and all(checks.get(key) is True for key in true_checks)
        and all(checks.get(key) is False for key in false_checks)
        and set(scope) == true_scope | false_scope
        and all(scope.get(key) is True for key in true_scope)
        and all(scope.get(key) is False for key in false_scope)
        and set(provenance) == provenance_keys
        and provenance.get("module")
        == "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py"
        and provenance.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and provenance.get("status") == intertwiners_report.get("status")
        and provenance.get("n_failed") == 0
        and all(
            provenance.get(key) is True
            for key in (
                "intertwiner_proof_grade", "carrier_proof_grade",
                "embedded_certificates_match", "source_contract_exact",
                "full_schema_and_literals_exact", "all_required_provenance_exact",
            )
        )
        and provenance.get("upstream_report_sha256")
        == provenance.get("expected_upstream_report_sha256")
        == _canonical_json_sha256(intertwiners_report)
        and provenance.get("upstream_intertwiner_certificate_sha256")
        == provenance.get("expected_upstream_intertwiner_certificate_sha256")
        == _canonical_json_sha256(upstream_intertwiner)
        and provenance.get("upstream_carrier_certificate_sha256")
        == provenance.get("expected_upstream_carrier_certificate_sha256")
        == _canonical_json_sha256(upstream_carriers)
        and set(source) == source_keys
        and source.get("upstream_module") == provenance.get("module")
        and source.get("stabilizer_module")
        == "exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py"
        and source.get("upstream_module_sha256")
        == source.get("expected_upstream_module_sha256")
        == _file_sha256(ROOT / source.get("upstream_module", ""))
        and source.get("stabilizer_module_sha256")
        == source.get("expected_stabilizer_module_sha256")
        == _file_sha256(ROOT / source.get("stabilizer_module", ""))
        and all(
            source.get(key) is True
            for key in (
                "both_modules_resolve_to_repository_root_exact",
                "source_bytes_match_pinned_contract_exact", "proof_grade",
            )
        )
        and set(alignment_provenance) == {
            "certificate_sha256", "expected_live_certificate_sha256",
            "full_schema_and_literals_exact",
        }
        and alignment_provenance.get("full_schema_and_literals_exact") is True
        and alignment_provenance.get("certificate_sha256")
        == alignment_provenance.get("expected_live_certificate_sha256")
        == _canonical_json_sha256(alignment) == expected_alignment_hash
        and set(alignment) == alignment_keys
        and alignment.get("proof_grade") is True
        and alignment.get("modular_prime") == RANK1_SU4_MODULAR_PRIME
        and alignment.get("generator_labels") == list(RANK1_SU4_ORDERED_LABELS)
        and alignment.get("family_count") == len(families) == 10
        and alignment.get("carrier_count") == len(carriers) == len(names) == 25
        and alignment.get("expected_irrep_multiplicities") == RANK1_SU4_BRANCHING
        and alignment.get("observed_irrep_multiplicities") == RANK1_SU4_BRANCHING
        and alignment.get("concatenated_aligned_basis_shape") == [210, 210]
        and alignment.get("concatenated_aligned_basis_rank_mod_prime") == 210
        and alignment.get("exterior_conjugation_shape") == [210, 210]
        and alignment.get("complex_type_carrier_count") == 14
        and alignment.get("self_conjugate_real_type_carrier_count") == 11
        and all(
            alignment.get(key) is True
            for key in (
                "upstream_carrier_order_exact", "all_family_word_counts_equal_dimensions",
                "all_25_carriers_exact",
                "all_equivalent_copies_use_common_source_actions_exact",
                "exterior_conjugation_signed_permutation_exact",
                "exterior_conjugation_square_equals_identity_exact",
                "Gaussian_basis_conjugation_is_physical_exact",
                "all_25_physical_Gaussian_embeddings_intertwine_live_Phi210_exact",
                "all_25_conjugate_carrier_maps_exact",
                "all_25_conjugate_maps_involutive_exact",
                "conjugation_compatible_with_all_15_generators_exact",
            )
        )
        and sum(row.get("dimension", 0) for row in carriers) == 210
        and all(
            isinstance(row, dict) and set(row) == carrier_keys
            and row.get("irrep") in RANK1_SU4_BRANCHING
            and row.get("dimension") == row.get("lowering_word_count")
            == row.get("aligned_rank_mod_prime")
            and row.get("conjugate_carrier_name") in names
            and rows_by_name[row.get("conjugate_carrier_name")].get(
                "conjugate_carrier_name"
            ) == row.get("name")
            and row.get("conjugation_map_denominator", 0) > 0
            and all(value > 0 for value in row.get("source_action_denominators", []))
            and all(
                row.get(key) is True
                for key in (
                    "highest_weight_primitive_and_raising_annihilated",
                    "C8_eigen_equation_exact",
                    "all_15_common_source_actions_intertwine_exact",
                    "natural_block_support_exact",
                    "all_15_live_canonical_Phi210_actions_intertwine_exact",
                    "conjugation_involution_exact",
                    "physical_conjugation_embedding_exact",
                )
            )
            for row in carriers
        )
        and all(
            isinstance(row, dict) and set(row) == family_keys
            and row.get("irrep") in RANK1_SU4_BRANCHING
            and row.get("multiplicity") == RANK1_SU4_BRANCHING[row.get("irrep")]
            and row.get("dimension") == len(row.get("lowering_words", []))
            and row.get("common_source_action_count") == 15
            and row.get("reference_carrier_name") in names
            for row in families
        )
        and alignment.get("simple_Chevalley_system", {}).get("proof_grade") is True
        and alignment.get("simple_Chevalley_system", {}).get(
            "all_actions_integral_real"
        ) is True
        and alignment.get("simple_Chevalley_system", {}).get(
            "all_12_Serre_relations_exact"
        ) is True
        and alignment.get("exact_integer_and_rational_arithmetic_safety", {}).get(
            "proof_grade"
        ) is True
        and alignment.get("exact_integer_and_rational_arithmetic_safety", {}).get(
            "all_live_conservative_bounds_fit_int64"
        ) is True
    )


def _rank1_su4_phi210_quadratic_basis_exact(
    report: dict[str, Any],
    stabilizer_report: dict[str, Any],
    intertwiners_report: dict[str, Any],
    aligned_report: dict[str, Any],
) -> bool:
    """Fail closed on the exact 45-dimensional live invariant basis."""
    checks = report.get("checks", {})
    scope = report.get("scope", {})
    provenance = report.get("source_provenance", {})
    constraint = report.get("constraint_system", {})
    census = report.get("real_form_completeness", {})
    basis = report.get("quadratic_basis", {})
    construction = report.get("construction_metadata", {})
    reconstruction = report.get("reconstruction_api", {})
    rows = basis.get("ordered_basis_metadata", [])
    check_keys = {
        "model_contract_and_live_companions_exact",
        "Cartan_reduced_constraint_nullity_45_exact",
        "real_form_completeness_upper_bound_45_exact",
        "explicit_real_symmetric_integral_basis_exact",
        "all_basis_matrices_live_invariant_exact",
        "lower_and_upper_dimensions_match_exact",
    }
    true_scope = {
        "H_fixed_to_h_minus", "Sigma_fixed_to_q_over_4",
        "rank1_endpoint_SU4_stabilizer_used", "canonical_real_Phi210_chart_used",
        "SU4_invariant_quadratic_form_basis_constructed",
        "SU4_invariant_quadratic_form_basis_complete",
        "SU4_invariant_quadratic_form_dimension_45_exact",
    }
    false_scope = {
        "augmented_homogeneous_Schur_SOS_SDP_constructed",
        "arbitrary_real_Phi_lower_bound_proved", "arbitrary_rank1_Phi_proved",
        "G3_closed", "whole_model_validated", "whole_model_excluded",
    }
    provenance_keys = {
        "stabilizer_module", "stabilizer_module_sha256", "intertwiner_module",
        "intertwiner_module_sha256", "companion_model_contract_id",
        "stabilizer_status", "intertwiner_status",
        "stabilizer_report_equals_live_report_exact",
        "intertwiner_report_equals_live_report_exact",
        "carrier_certificate_equals_embedded_and_live_exact",
        "all_required_live_provenance_exact",
    }
    constraint_keys = {
        "proof_grade", "Cartan_generator_count", "non_Cartan_generator_count",
        "Cartan_weight_zero_symmetric_monomial_count", "reduced_constraint_shape",
        "reduced_constraint_nnz", "reduced_constraint_maximum_absolute_entry",
        "modular_prime", "reduced_constraint_rank_mod_prime", "free_column_count",
        "integer_nullspace_shape", "integer_nullspace_maximum_absolute_entry",
        "integer_nullspace_nnz", "integer_nullspace_residual_zero_exact",
        "all_45_nullvectors_invariant_under_all_15_exterior_actions_exact",
        "exact_rational_rank", "exact_rational_nullity", "rank_nullity_argument",
        "constraint_sha256", "nullspace_sha256",
    }
    census_keys = {
        "proof_grade", "complexified_branching", "expected_complexified_branching",
        "branching_exact", "self_conjugate_real_types",
        "self_conjugate_symmetric_pairing_dimension",
        "complex_types_with_conjugates", "complex_Hermitian_real_dimension",
        "total_real_symmetric_invariant_dimension_upper_bound",
        "dimension_identity", "real_form_argument",
    }
    basis_keys = {
        "proof_grade", "matrix_count", "matrix_shape", "all_shapes_210_by_210_exact",
        "all_entries_integral_exact", "all_matrices_symmetric_exact",
        "all_matrices_primitive_exact", "all_canonical_first_entries_positive_exact",
        "all_45_commute_with_all_15_live_Phi210_generators_exact",
        "upper_triangle_column_rank_mod_prime", "modular_prime", "independence_argument",
        "minimum_nnz", "maximum_nnz", "total_nnz", "maximum_absolute_entry",
        "basis_sha256", "ordered_basis_metadata", "Gram_shape", "Gram_rank_mod_prime",
        "Gram_minimum_diagonal", "Gram_maximum_diagonal", "Gram_sha256",
        "polynomial_monomial_count", "polynomial_upper_triangle_convention",
        "integer_matrix_to_primitive_polynomial_scale_factors",
        "primitive_polynomial_rows_exact", "primitive_polynomial_basis_rank_mod_prime",
        "primitive_polynomial_basis_sha256",
    }
    construction_keys = {
        "modular_pivot_upper_triangle_coordinates",
        "modular_pivot_upper_triangle_flat_indices",
        "nonzero_real_imaginary_candidate_count", "selected_candidate_indices",
        "selected_candidate_origins",
    }
    reconstruction_keys = {
        "basis_accessor", "Gram_accessor", "exact_reconstruction_accessor",
        "integral_evaluation_accessor", "primitive_polynomial_accessor",
        "matrix_to_polynomial_accessor", "polynomial_to_matrix_accessor",
        "formula", "polynomial_convention", "rational_return_convention",
        "exact_arithmetic_contract", "ordered_basis_hash", "Gram_hash",
    }
    expected_hashes = {
        "constraint": "cddac4827dc47c663c8ca7b4ebe9ccb2338103ae5daf917c4eb615f4c3659d90",
        "nullspace": "a92c9fc421809623e50a0c7dc043d546cd866e7acaa819cffab3ae52da3998d6",
        "basis": "27c0649758c87aa2cbe39ae04596f4bd6df511ba3ca4004013bdcf936599b694",
        "gram": "17d352a43fc0a555df3d2abbe0f59f1ceecc89498648a84703bcf0ccd9c23124",
        "polynomial": "a9d417aa7210143ad6bd69f62dce358239673b6c0c7bc545f9b65ec586002caa",
    }
    return bool(
        _rank1_su4_stabilizer_infrastructure_exact(stabilizer_report)
        and _rank1_su4_phi210_intertwiners_exact(
            intertwiners_report, stabilizer_report
        )
        and _rank1_su4_aligned_carriers_exact(
            aligned_report, intertwiners_report, stabilizer_report
        )
        and _canonical_json_sha256(report)
        == "497a8c1db29e7d88f30bd1cc68902cc7981da4a3fefd5586bd15bad323d1e259"
        and set(report) == {
            "status", "overall_state", "model_contract_id", "n_checks",
            "n_failed", "failures", "checks", "source_provenance",
            "constraint_system", "real_form_completeness", "quadratic_basis",
            "construction_metadata", "reconstruction_api", "scope",
            "next_exact_target", "verdict",
        }
        and report.get("status")
        == "EXACT_RANK1_SU4_PHI210_QUADRATIC_BASIS_CERTIFIED"
        and report.get("overall_state")
        == "SU4_INVARIANT_QUADRATIC_BASIS_CLOSED__AUGMENTED_SDP_AND_G3_OPEN"
        and report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and report.get("n_checks") == len(check_keys)
        and report.get("n_failed") == 0 and report.get("failures") == []
        and set(checks) == check_keys
        and all(checks.get(key) is True for key in check_keys)
        and set(scope) == true_scope | false_scope
        and all(scope.get(key) is True for key in true_scope)
        and all(scope.get(key) is False for key in false_scope)
        and set(provenance) == provenance_keys
        and provenance.get("companion_model_contract_id")
        == AUTHORITATIVE_CONTRACT_ID
        and provenance.get("stabilizer_status") == stabilizer_report.get("status")
        and provenance.get("intertwiner_status") == intertwiners_report.get("status")
        and provenance.get("stabilizer_module")
        == "exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py"
        and provenance.get("intertwiner_module")
        == "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py"
        and provenance.get("stabilizer_module_sha256")
        == _file_sha256(ROOT / provenance.get("stabilizer_module", ""))
        and provenance.get("intertwiner_module_sha256")
        == _file_sha256(ROOT / provenance.get("intertwiner_module", ""))
        and all(
            provenance.get(key) is True
            for key in (
                "stabilizer_report_equals_live_report_exact",
                "intertwiner_report_equals_live_report_exact",
                "carrier_certificate_equals_embedded_and_live_exact",
                "all_required_live_provenance_exact",
            )
        )
        and set(constraint) == constraint_keys
        and constraint.get("proof_grade") is True
        and constraint.get("Cartan_generator_count") == 3
        and constraint.get("non_Cartan_generator_count") == 12
        and constraint.get("Cartan_weight_zero_symmetric_monomial_count") == 551
        and constraint.get("reduced_constraint_shape") == [5952, 551]
        and constraint.get("reduced_constraint_rank_mod_prime") == 506
        and constraint.get("exact_rational_rank") == 506
        and constraint.get("exact_rational_nullity") == 45
        and constraint.get("free_column_count") == 45
        and constraint.get("integer_nullspace_shape") == [551, 45]
        and constraint.get("integer_nullspace_residual_zero_exact") is True
        and constraint.get(
            "all_45_nullvectors_invariant_under_all_15_exterior_actions_exact"
        ) is True
        and constraint.get("modular_prime") == RANK1_SU4_MODULAR_PRIME
        and constraint.get("constraint_sha256") == expected_hashes["constraint"]
        and constraint.get("nullspace_sha256") == expected_hashes["nullspace"]
        and set(census) == census_keys
        and census.get("proof_grade") is True
        and census.get("branching_exact") is True
        and census.get("complexified_branching") == RANK1_SU4_BRANCHING
        and census.get("expected_complexified_branching") == RANK1_SU4_BRANCHING
        and census.get("self_conjugate_symmetric_pairing_dimension") == 24
        and census.get("complex_Hermitian_real_dimension") == 21
        and census.get("total_real_symmetric_invariant_dimension_upper_bound") == 45
        and census.get("self_conjugate_real_types") == {
            "1": {"multiplicity": 4, "symmetric_pairings": 10},
            "6": {"multiplicity": 4, "symmetric_pairings": 10},
            "15": {"multiplicity": 2, "symmetric_pairings": 3},
            "20prime": {"multiplicity": 1, "symmetric_pairings": 1},
        }
        and census.get("complex_types_with_conjugates") == {
            "4/4bar": {"multiplicity": 4, "Hermitian_real_dimension": 16},
            "10/10bar": {"multiplicity": 1, "Hermitian_real_dimension": 1},
            "20/20bar": {"multiplicity": 2, "Hermitian_real_dimension": 4},
        }
        and set(basis) == basis_keys
        and basis.get("proof_grade") is True
        and basis.get("matrix_count") == len(rows) == 45
        and basis.get("matrix_shape") == [210, 210]
        and basis.get("all_shapes_210_by_210_exact") is True
        and basis.get("all_entries_integral_exact") is True
        and basis.get("all_matrices_symmetric_exact") is True
        and basis.get("all_matrices_primitive_exact") is True
        and basis.get(
            "all_45_commute_with_all_15_live_Phi210_generators_exact"
        ) is True
        and basis.get("upper_triangle_column_rank_mod_prime") == 45
        and basis.get("Gram_shape") == [45, 45]
        and basis.get("Gram_rank_mod_prime") == 45
        and basis.get("primitive_polynomial_basis_rank_mod_prime") == 45
        and basis.get("modular_prime") == RANK1_SU4_MODULAR_PRIME
        and basis.get("basis_sha256") == expected_hashes["basis"]
        and basis.get("Gram_sha256") == expected_hashes["gram"]
        and basis.get("primitive_polynomial_basis_sha256")
        == expected_hashes["polynomial"]
        and all(
            isinstance(row, dict)
            and set(row) == {
                "basis_index", "nnz", "maximum_absolute_entry",
                "Frobenius_norm_squared", "matrix_sha256",
            }
            and row.get("basis_index") == index
            and isinstance(row.get("matrix_sha256"), str)
            and len(row.get("matrix_sha256")) == 64
            for index, row in enumerate(rows)
        )
        and set(construction) == construction_keys
        and construction.get("nonzero_real_imaginary_candidate_count") == 73
        and len(construction.get("selected_candidate_indices", [])) == 45
        and len(construction.get("selected_candidate_origins", [])) == 45
        and len(construction.get("modular_pivot_upper_triangle_coordinates", [])) == 45
        and len(construction.get("modular_pivot_upper_triangle_flat_indices", [])) == 45
        and set(reconstruction) == reconstruction_keys
        and reconstruction.get("ordered_basis_hash") == expected_hashes["basis"]
        and reconstruction.get("Gram_hash") == expected_hashes["gram"]
        and reconstruction.get("formula") == "Q(c)=sum_{a=0}^{44} c_a Q_a"
        and set(reconstruction.get("exact_arithmetic_contract", {})) == {
            "integral_evaluation", "rational_reconstruction",
            "polynomial_encoding", "live_basis_maximum_absolute_entry",
        }
        and reconstruction.get("exact_arithmetic_contract", {}).get(
            "live_basis_maximum_absolute_entry"
        ) == 8
    )


def _rank1_su4_augmented_sos_census_exact(
    report: dict[str, Any],
    stabilizer_report: dict[str, Any],
    intertwiners_report: dict[str, Any],
    aligned_report: dict[str, Any],
    quadratic_report: dict[str, Any],
) -> bool:
    """Fail closed on the abstract augmented-SOS census, not on a PSD claim."""
    checks = report.get("checks", {})
    scope = report.get("scope", {})
    provenance = report.get("source_provenance", {})
    representation = report.get("augmented_representation", {})
    target = report.get("invariant_quartic_target", {})
    universal = report.get("universal_multiplication_and_section", {})
    coefficient_map = report.get("abstract_coefficient_map_census", {})
    cubic = coefficient_map.get("cubic_cross_sector", {})
    public_apis = report.get("public_exact_APIs", {})
    check_keys = {
        "Frobenius_Schur_indicators_computed_and_real_types_exact",
        "Schur_parameter_19594_grade_census_exact",
        "abstract_invariant_map_ranks_and_kernels_exact",
        "augmented_dimension_35_isotypic_types_and_824_copies_exact",
        "coordinate_map_absence_declared_fail_closed",
        "cubic_abstract_zero_interface_reserved_without_physical_claim",
        "frozen_aligned_carrier_and_quadratic_basis_APIs_exact",
        "invariant_target_6585_grade_census_exact",
        "live_Phi210_character_and_exact_branching_certified",
        "nine_real_and_thirteen_complex_isotypic_blocks_exact",
        "real_symmetric_and_complex_Hermitian_conventions_complete",
        "universal_GL211_equivariant_section_exact",
    }
    true_scope = {
        "H_fixed_to_h_minus",
        "Sigma_fixed_to_q_over_4",
        "rank1_endpoint_SU4_stabilizer_used",
        "augmented_homogeneous_representation_census_constructed",
        "all_22_real_Hermitian_Schur_block_sizes_certified",
        "abstract_invariant_grade_ranks_certified",
        "quadratic_target_invariant_basis_dimension_45_bound_live",
        "universal_GL211_multiplication_and_rational_section_constructed",
    }
    false_scope = {
        "all_35_isotypic_type_maps_spanning_824_irreducible_copies_constructed",
        "ordered_invariant_cubic_basis_constructed",
        "ordered_invariant_quartic_basis_constructed",
        "Schur_coordinate_6585_by_19594_coefficient_matrix_constructed",
        "physical_G3_gap_target_vector_constructed",
        "physical_G3_gap_cubic_zero_RHS_certified",
        "augmented_Schur_SOS_SDP_constructed",
        "augmented_Schur_SOS_SDP_feasibility_certified",
        "augmented_Schur_SOS_SDP_infeasibility_certified",
        "arbitrary_real_Phi_lower_bound_proved",
        "arbitrary_rank1_Phi_proved",
        "G3_closed",
        "whole_model_validated",
        "whole_model_excluded",
    }
    provenance_keys = {
        "aligned_module", "aligned_report_sha256", "aligned_source_sha256",
        "alignment_certificate_sha256", "all_required_frozen_API_provenance_exact",
        "expected_aligned_report_sha256", "expected_aligned_source_sha256",
        "expected_alignment_certificate_sha256", "expected_quadratic_basis_sha256",
        "expected_quadratic_report_sha256", "expected_quadratic_source_sha256",
        "model_contract_id", "proof_grade", "quadratic_basis_matrix_count",
        "quadratic_basis_sha256", "quadratic_module", "quadratic_report_sha256",
        "quadratic_source_sha256",
    }
    representation_keys = {
        "Frobenius_Schur_classification_computed_exact", "Phi210_branching",
        "Phi210_branching_expected_exact", "Phi210_character_sha256",
        "Phi210_weight_character_dimension", "Phi210_weight_count",
        "Schur_real_parameter_count", "Schur_real_parameter_grade_counts",
        "Sym2Phi_character_sha256", "Sym2Phi_dimension",
        "all_Gelfand_Tsetlin_character_dimensions_match_Weyl_exact",
        "augmented_character_sha256", "augmented_homogeneous_dimension",
        "complex_Hermitian_block_count", "complex_irreducible_copy_count",
        "complex_irreducible_copy_grade_counts_t2_tPhi_Phi2", "complex_irrep_rows",
        "complex_isotypic_type_count", "expected_augmented_multiplicities_exact",
        "proof_grade", "real_isotypic_block_count", "real_isotypic_blocks",
        "real_symmetric_block_count", "represented_real_dimension",
    }
    target_keys = {
        "Weyl_group_order", "expected_symmetric_power_dimensions",
        "invariant_equation_count", "invariant_equation_grade_counts",
        "proof_grade", "symmetric_power_character_sha256",
        "symmetric_power_dimensions", "target_sector",
        "trivial_multiplicity_extraction",
    }
    universal_keys = {
        "all_representative_identities_exact",
        "equality_and_grade_pattern_representative_count",
        "invariant_restriction_surjective_exact", "invariant_surjectivity_argument",
        "linear_dimension", "linear_space",
        "multiplication_after_section_is_identity_exact", "multiplication_formula",
        "proof_grade", "quadratic_monomial_dimension", "quadratic_monomial_space",
        "raw_domain_grade_dimensions", "raw_grade_kernel_dimensions",
        "raw_grade_ranks_exact", "raw_quartic_polynomial_dimension",
        "raw_symmetric_Gram_dimension", "raw_target_grade_dimensions",
        "section_formula", "section_is_GL211_equivariant_by_naturality_exact",
        "section_preserves_Phi_degree_exact",
    }
    coefficient_map_keys = {
        "Schur_coordinate_matrix_constructed",
        "Schur_coordinate_matrix_shape_when_constructed",
        "abstract_grade_kernel_dimensions_exact", "abstract_grade_ranks_exact",
        "abstract_total_kernel_dimension_exact", "abstract_total_rank_exact",
        "cubic_cross_sector", "domain_real_parameter_grade_counts", "map",
        "missing_coordinate_data", "proof_grade",
        "surjectivity_is_abstract_not_a_coordinate_matrix",
        "target_invariant_row_grade_counts",
    }
    cubic_keys = {
        "abstract_interface_RHS", "abstract_zero_RHS_interface_contract_reserved",
        "abstract_zero_RHS_row_count_reserved",
        "all_1414_cross_variables_present_in_census_exact",
        "all_478_cubic_target_rows_reserved_exact", "block_rows",
        "invariant_target_row_count", "nonzero_block_row_count",
        "physical_G3_gap_cubic_zero_RHS_certified",
        "physical_G3_gap_target_vector_constructed", "real_Schur_variable_count",
        "source", "zero_RHS_is_interface_contract_not_a_physical_vector_certificate",
    }
    public_api_keys = {
        "Frobenius_Schur_indicator", "Phi_character", "Schur_grade_counts",
        "augmented_character", "character_decompositions", "polarized_Gram_section",
        "polarized_tensor_section", "raw_Gram_entry_map", "real_isotypic_blocks",
        "symmetric_power_character", "target_grade_counts",
    }
    expected_aligned_report = (
        "d2da0572dc33a1f3f88b5ac5df3343201650ca660498f34ff59806a607015c67"
    )
    expected_aligned_source = (
        "5671857444bda7d53db45393e28a3b9ac0784d0f2a63aa1e541eb5e356d23ccc"
    )
    expected_alignment = (
        "f74b7845b57472f62773c398fa927b551b5d9d09f86bd7defb92a6ed71adbe15"
    )
    expected_quadratic_report = (
        "497a8c1db29e7d88f30bd1cc68902cc7981da4a3fefd5586bd15bad323d1e259"
    )
    expected_quadratic_source = (
        "4eec63ba40b888de736c84f607019ba0f21915028b423578502893744bab1060"
    )
    expected_quadratic_basis = (
        "27c0649758c87aa2cbe39ae04596f4bd6df511ba3ca4004013bdcf936599b694"
    )
    return bool(
        _rank1_su4_stabilizer_infrastructure_exact(stabilizer_report)
        and _rank1_su4_phi210_intertwiners_exact(
            intertwiners_report, stabilizer_report
        )
        and _rank1_su4_aligned_carriers_exact(
            aligned_report, intertwiners_report, stabilizer_report
        )
        and _rank1_su4_phi210_quadratic_basis_exact(
            quadratic_report, stabilizer_report, intertwiners_report,
            aligned_report,
        )
        and _file_sha256(
            ROOT / "exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py"
        ) == "3e0d7f2eac73eec950960f1ffd78c9584a4b15d070c84889080cf4c67d5a4d63"
        and _canonical_json_sha256(report)
        == "703a3819fea5afe857757082190f9cf1e22f283ab0ddcc882c2f011b65ba58f3"
        and set(report) == {
            "abstract_coefficient_map_census", "augmented_representation",
            "blocking_gap", "checks", "failures", "invariant_quartic_target",
            "model_contract_id", "n_checks", "n_failed", "next_exact_target",
            "overall_state", "public_exact_APIs", "scope", "source_provenance",
            "status", "universal_multiplication_and_section", "verdict",
        }
        and report.get("status")
        == "EXACT_RANK1_SU4_AUGMENTED_SOS_CENSUS_AND_UNIVERSAL_MAP_CERTIFIED"
        and report.get("overall_state")
        == "SU4_AUGMENTED_SOS_CENSUS_CLOSED__SCHUR_EMBEDDINGS_SDP_AND_G3_OPEN"
        and report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and report.get("n_checks") == len(check_keys)
        and report.get("n_failed") == 0
        and report.get("failures") == []
        and set(checks) == check_keys
        and all(checks.get(key) is True for key in check_keys)
        and set(scope) == true_scope | false_scope
        and all(scope.get(key) is True for key in true_scope)
        and all(scope.get(key) is False for key in false_scope)
        and set(provenance) == provenance_keys
        and provenance.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and provenance.get("proof_grade") is True
        and provenance.get("all_required_frozen_API_provenance_exact") is True
        and provenance.get("aligned_module")
        == "exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py"
        and provenance.get("quadratic_module")
        == "exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py"
        and provenance.get("aligned_report_sha256")
        == provenance.get("expected_aligned_report_sha256")
        == _canonical_json_sha256(aligned_report)
        == expected_aligned_report
        and provenance.get("aligned_source_sha256")
        == provenance.get("expected_aligned_source_sha256")
        == _file_sha256(ROOT / provenance.get("aligned_module", ""))
        == expected_aligned_source
        and provenance.get("alignment_certificate_sha256")
        == provenance.get("expected_alignment_certificate_sha256")
        == _canonical_json_sha256(aligned_report.get("alignment", {}))
        == expected_alignment
        and provenance.get("quadratic_report_sha256")
        == provenance.get("expected_quadratic_report_sha256")
        == _canonical_json_sha256(quadratic_report)
        == expected_quadratic_report
        and provenance.get("quadratic_source_sha256")
        == provenance.get("expected_quadratic_source_sha256")
        == _file_sha256(ROOT / provenance.get("quadratic_module", ""))
        == expected_quadratic_source
        and provenance.get("quadratic_basis_sha256")
        == provenance.get("expected_quadratic_basis_sha256")
        == quadratic_report.get("quadratic_basis", {}).get("basis_sha256")
        == expected_quadratic_basis
        and provenance.get("quadratic_basis_matrix_count") == 45
        and set(representation) == representation_keys
        and representation.get("proof_grade") is True
        and representation.get("Phi210_weight_character_dimension") == 210
        and representation.get("Sym2Phi_dimension") == 22_155
        and representation.get("augmented_homogeneous_dimension") == 22_366
        and representation.get("represented_real_dimension") == 22_366
        and representation.get("complex_isotypic_type_count") == 35
        and representation.get("complex_irreducible_copy_count") == 824
        and representation.get("complex_irreducible_copy_grade_counts_t2_tPhi_Phi2")
        == [1, 25, 798]
        and representation.get("real_isotypic_block_count") == 22
        and representation.get("real_symmetric_block_count") == 9
        and representation.get("complex_Hermitian_block_count") == 13
        and representation.get("Schur_real_parameter_count") == 19_594
        and representation.get("Schur_real_parameter_grade_counts")
        == [1, 4, 90, 1_414, 18_085]
        and len(representation.get("complex_irrep_rows", [])) == 35
        and len(representation.get("real_isotypic_blocks", [])) == 22
        and all(
            isinstance(row, dict)
            and set(row) == {
                "complex_dimension", "dynkin", "multiplicity_Phi",
                "multiplicity_Sym2Phi", "multiplicity_augmented",
            }
            for row in representation.get("complex_irrep_rows", [])
        )
        and all(
            isinstance(row, dict)
            and set(row) == {
                "Frobenius_Schur_indicator", "Frobenius_Schur_type",
                "Frobenius_Schur_type_argument", "PSD_cone", "conjugate_dynkin",
                "coordinate_convention",
                "cubic_tPhi_to_Phi2_cross_real_parameter_count",
                "graded_multiplicities_t2_tPhi_Phi2", "irrep_complex_dimension",
                "multiplicity_matrix_order", "real_Schur_parameter_count",
                "real_block_kind", "real_parameter_grade_counts",
                "representative_dynkin", "represented_real_dimension",
                "self_conjugate", "young_diagram_box_count",
            }
            for row in representation.get("real_isotypic_blocks", [])
        )
        and set(target) == target_keys
        and target.get("proof_grade") is True
        and target.get("invariant_equation_count") == 6_585
        and target.get("invariant_equation_grade_counts")
        == [1, 4, 45, 478, 6_057]
        and target.get("symmetric_power_dimensions")
        == [1, 210, 22_155, 1_565_620, 83_369_265]
        and target.get("expected_symmetric_power_dimensions")
        == [1, 210, 22_155, 1_565_620, 83_369_265]
        and set(universal) == universal_keys
        and universal.get("proof_grade") is True
        and universal.get("linear_dimension") == 211
        and universal.get("quadratic_monomial_dimension") == 22_366
        and universal.get("raw_symmetric_Gram_dimension") == 250_130_161
        and universal.get("raw_quartic_polynomial_dimension") == 84_957_251
        and universal.get("multiplication_after_section_is_identity_exact") is True
        and universal.get("section_is_GL211_equivariant_by_naturality_exact") is True
        and universal.get("section_preserves_Phi_degree_exact") is True
        and universal.get("invariant_restriction_surjective_exact") is True
        and universal.get("raw_grade_ranks_exact")
        == [1, 210, 22_155, 1_565_620, 83_369_265]
        and set(coefficient_map) == coefficient_map_keys
        and coefficient_map.get("proof_grade") is True
        and coefficient_map.get("domain_real_parameter_grade_counts")
        == [1, 4, 90, 1_414, 18_085]
        and coefficient_map.get("target_invariant_row_grade_counts")
        == [1, 4, 45, 478, 6_057]
        and coefficient_map.get("abstract_grade_ranks_exact")
        == [1, 4, 45, 478, 6_057]
        and coefficient_map.get("abstract_grade_kernel_dimensions_exact")
        == [0, 0, 45, 936, 12_028]
        and coefficient_map.get("abstract_total_rank_exact") == 6_585
        and coefficient_map.get("abstract_total_kernel_dimension_exact") == 13_009
        and coefficient_map.get("Schur_coordinate_matrix_constructed") is False
        and coefficient_map.get("Schur_coordinate_matrix_shape_when_constructed")
        == [6_585, 19_594]
        and coefficient_map.get("surjectivity_is_abstract_not_a_coordinate_matrix")
        is True
        and set(cubic) == cubic_keys
        and cubic.get("real_Schur_variable_count") == 1_414
        and cubic.get("invariant_target_row_count") == 478
        and cubic.get("nonzero_block_row_count") == 7
        and len(cubic.get("block_rows", [])) == 7
        and cubic.get("abstract_interface_RHS") == "zero"
        and cubic.get("abstract_zero_RHS_row_count_reserved") == 478
        and cubic.get("abstract_zero_RHS_interface_contract_reserved") is True
        and cubic.get("all_1414_cross_variables_present_in_census_exact") is True
        and cubic.get("all_478_cubic_target_rows_reserved_exact") is True
        and cubic.get("zero_RHS_is_interface_contract_not_a_physical_vector_certificate")
        is True
        and cubic.get("physical_G3_gap_target_vector_constructed") is False
        and cubic.get("physical_G3_gap_cubic_zero_RHS_certified") is False
        and all(
            isinstance(row, dict)
            and set(row) == {
                "Phi2_multiplicity", "real_block_kind",
                "real_cross_parameter_count", "representative_dynkin",
                "tPhi_multiplicity",
            }
            for row in cubic.get("block_rows", [])
        )
        and set(public_apis) == public_api_keys
    )


def _rank1_su4_augmented_sos_cubic_map_exact(
    report: dict[str, Any],
    stabilizer_report: dict[str, Any],
    intertwiners_report: dict[str, Any],
    aligned_report: dict[str, Any],
    quadratic_report: dict[str, Any],
    census_report: dict[str, Any],
) -> bool:
    """Fail closed on the exact cubic Schur map, never on a physical RHS."""
    checks = report.get("checks", {})
    scope = report.get("scope", {})
    provenance = report.get("source_provenance", {})
    targets = report.get("Sym2_target_carriers", {})
    pairings = report.get("contragredient_pairings", {})
    domain = report.get("physical_cubic_domain", {})
    cubic_map = report.get("cubic_coordinate_map", {})
    arithmetic = report.get("exact_arithmetic_safety", {})
    public_apis = report.get("public_exact_APIs", {})
    target_families = targets.get("families", [])
    pairing_families = pairings.get("families", [])
    block_rows = domain.get("all_22_augmented_block_rows", [])

    check_keys = {
        "abstract_478_coordinate_zero_placeholder_exact_and_nonphysical",
        "all_1414_complexified_cross_tensors_constructed_exact",
        "all_22_real_Hermitian_block_rows_and_1414_variables_exact",
        "all_required_Sym2_highest_weight_carriers_exact",
        "all_target_carriers_use_frozen_common_words_and_actions_exact",
        "all_ten_contragredient_pairings_exact",
        "exact_rank_478_and_kernel_936_certified",
        "explicit_integer_478_by_1414_coordinate_map_exact",
        "frozen_census_aligned_quadratic_and_intertwiner_provenance_exact",
        "full_SDP_and_G3_absence_declared_fail_closed",
        "integer_rational_and_modular_arithmetic_safety_exact",
        "physical_realification_rank_1414_exact",
    }
    true_scope = {
        "H_fixed_to_h_minus",
        "Sigma_fixed_to_q_over_4",
        "rank1_endpoint_SU4_stabilizer_used",
        "all_1414_real_structure_fixed_cubic_Schur_cross_variables_constructed",
        "explicit_478_by_1414_cubic_coordinate_map_constructed",
        "cubic_map_rank_478_and_kernel_dimension_936_exact",
        "abstract_478_coordinate_zero_placeholder_available",
    }
    false_scope = {
        "degree_zero_coefficient_map_constructed",
        "degree_one_coefficient_map_constructed",
        "degree_two_coefficient_map_constructed",
        "degree_four_coefficient_map_constructed",
        "full_6585_by_19594_Schur_coordinate_matrix_constructed",
        "physical_G3_gap_target_vector_constructed",
        "physical_G3_gap_cubic_zero_RHS_certified",
        "augmented_Schur_SOS_SDP_constructed",
        "augmented_Schur_SOS_SDP_feasibility_certified",
        "augmented_Schur_SOS_SDP_infeasibility_certified",
        "arbitrary_real_Phi_lower_bound_proved",
        "arbitrary_rank1_Phi_proved",
        "G3_closed",
        "whole_model_validated",
        "whole_model_excluded",
    }
    provenance_keys = {
        "aligned_module", "aligned_n_failed", "aligned_source_sha256",
        "aligned_status", "all_required_frozen_provenance_exact",
        "census_module", "census_n_failed",
        "census_physical_G3_gap_cubic_zero_RHS_certified",
        "census_physical_G3_gap_target_vector_constructed",
        "census_report_sha256", "census_source_sha256", "census_status",
        "expected_aligned_source_sha256", "expected_census_report_sha256",
        "expected_census_source_sha256", "expected_intertwiner_source_sha256",
        "expected_quadratic_basis_sha256", "expected_quadratic_report_sha256",
        "expected_quadratic_source_sha256", "intertwiner_module",
        "intertwiner_source_sha256", "live_Schur_parameter_grade_counts",
        "live_target_invariant_grade_counts", "model_contract_id", "proof_grade",
        "quadratic_basis_sha256", "quadratic_module",
        "quadratic_report_sha256", "quadratic_source_sha256",
    }
    target_keys = {
        "all_common_lowering_word_carriers_have_full_rank_exact",
        "all_copies_aligned_by_exact_highest_weight_universality",
        "all_highest_vectors_raise_to_zero_exact",
        "all_highest_weight_nullities_match_character_census_exact",
        "all_reference_copies_intertwine_9_Chevalley_actions_exact",
        "families", "irrep_family_count", "proof_grade", "representation",
        "total_complex_carrier_copy_count", "total_isotypic_dimension",
    }
    target_family_keys = {
        "checked_Chevalley_action_count", "concatenated_nnz",
        "concatenated_rank_by_highest_weight_evaluation_exact",
        "concatenated_sha256", "concatenated_shape", "constraint_nnz",
        "constraint_sha256", "constraint_shape", "copy_count", "dimension",
        "every_copy_alignment_follows_from_highest_weight_universality_exact",
        "every_copy_full_rank_mod_prime", "free_columns",
        "highest_vectors_maximum_absolute_entry", "highest_vectors_nnz",
        "highest_vectors_sha256", "highest_weight",
        "highest_weight_evaluation_rank_argument", "individual_copy_ranks_mod_prime",
        "irrep", "lowering_word_count", "maximum_absolute_entry",
        "maximum_rational_reconstruction_denominator", "modular_rank", "nullity",
        "proof_grade", "raising_residual_zero_exact", "rank_nullity_argument",
        "reference_copy_all_9_Chevalley_actions_intertwine_exact",
        "source_Chevalley_imaginary_residuals_zero_exact",
        "source_weight_space_dimension",
    }
    pairing_keys = {
        "all_15_compact_tensor_equations_exact",
        "all_pairing_spaces_one_dimensional_exact", "families",
        "pairing_family_count", "proof_grade",
    }
    pairing_family_keys = {
        "all_15_compact_tensor_invariance_equations_exact", "constraint_nnz",
        "constraint_sha256", "constraint_shape", "dimension", "exact_nullity",
        "matrix_maximum_absolute_entry", "matrix_nnz", "matrix_sha256",
        "maximum_rational_reconstruction_denominator", "modular_rank",
        "proof_grade", "rank_nullity_argument", "source_irrep",
        "target_contragredient_irrep", "weight_zero_variable_count",
    }
    domain_keys = {
        "Gram_symmetric_off_diagonal_multiplier", "all_22_augmented_block_rows",
        "all_22_block_provenance_rows_exact",
        "all_multiplications_commute_with_physical_conjugation_exact",
        "all_selected_vectors_satisfy_physical_real_structure_exact",
        "complexified_domain_basis_count", "complexified_raw_image_total_nnz",
        "complexified_raw_tensor_total_nnz", "domain_basis_metadata_sha256",
        "domain_modular_elimination_fill", "domain_modular_pivot_count",
        "expected_complexified_counts_by_irrep", "nonzero_cubic_block_count",
        "observed_complexified_counts_by_irrep", "physical_basis_count",
        "physical_candidate_count", "physical_component_counts",
        "physical_real_block_counts", "proof_grade",
    }
    block_row_keys = {
        "Phi2_multiplicity", "all_variables_constructed_exact",
        "constructed_physical_basis_variable_count",
        "expected_cubic_cross_real_parameter_count", "real_block_kind",
        "representative_dynkin", "tPhi_multiplicity",
    }
    map_keys = {
        "Gram_convention", "abstract_zero_interface_placeholder_dtype",
        "abstract_zero_interface_placeholder_nnz",
        "abstract_zero_interface_placeholder_shape",
        "abstract_zero_placeholder_is_not_a_physical_G3_target",
        "all_478_abstract_interface_placeholder_entries_zero_exact",
        "coordinate_map_maximum_absolute_entry", "coordinate_map_nnz",
        "coordinate_map_sha256", "coordinate_map_shape", "exact_kernel_dimension",
        "exact_rank", "full_physical_image_maximum_absolute_entry",
        "full_physical_image_nnz", "full_physical_image_sha256",
        "full_physical_image_shape", "independent_domain_column_indices",
        "modular_prime", "physical_G3_gap_cubic_zero_RHS_certified",
        "physical_G3_gap_target_vector_constructed", "proof_grade",
        "rank_argument", "rank_mod_prime",
        "selected_minor_determinant_nonzero_mod_prime",
        "selected_minor_rank_mod_prime", "selected_minor_sha256",
        "source_coordinate_space", "target_coordinate_metadata_sha256",
        "target_coordinate_space", "target_imaginary_coordinate_count",
        "target_pivot_row_count", "target_real_coordinate_count",
    }
    arithmetic_keys = {
        "Fraction_based_constraint_denominator_clearing_exact",
        "Python_integer_sparse_aggregation_exact",
        "all_recorded_bounds_fit_signed_int64",
        "checked_sparse_products_reject_unsafe_int64_bounds",
        "conservative_live_product_absolute_bound", "maximum_live_absolute_entry",
        "modular_rational_reconstruction_verified_over_Z_exact",
        "modular_row_update_absolute_bound", "proof_grade",
        "signed_int64_maximum", "storage_dtype",
    }
    public_api_keys = {
        "abstract_zero_interface_placeholder", "coordinate_map",
        "domain_metadata", "map_convention", "target_metadata",
    }
    expected_counts = {
        "1": 180, "4": 240, "4bar": 240, "6": 248, "10": 39,
        "10bar": 39, "20": 124, "20bar": 124, "20prime": 42, "15": 138,
    }
    expected_real_blocks = {
        "(0, 0, 0)": 180, "(0, 0, 1)": 480, "(0, 0, 2)": 78,
        "(0, 1, 0)": 248, "(0, 1, 1)": 248, "(0, 2, 0)": 42,
        "(1, 0, 1)": 138,
    }
    expected_census_source = (
        "3e0d7f2eac73eec950960f1ffd78c9584a4b15d070c84889080cf4c67d5a4d63"
    )
    expected_census_report = (
        "703a3819fea5afe857757082190f9cf1e22f283ab0ddcc882c2f011b65ba58f3"
    )
    expected_aligned_source = (
        "5671857444bda7d53db45393e28a3b9ac0784d0f2a63aa1e541eb5e356d23ccc"
    )
    expected_intertwiner_source = (
        "76fa77c99b8d6e963e8694acf74280de29ced4c7a7623bffa991aead77329f49"
    )
    expected_quadratic_source = (
        "4eec63ba40b888de736c84f607019ba0f21915028b423578502893744bab1060"
    )
    expected_quadratic_report = (
        "497a8c1db29e7d88f30bd1cc68902cc7981da4a3fefd5586bd15bad323d1e259"
    )
    expected_quadratic_basis = (
        "27c0649758c87aa2cbe39ae04596f4bd6df511ba3ca4004013bdcf936599b694"
    )
    return bool(
        _rank1_su4_stabilizer_infrastructure_exact(stabilizer_report)
        and _rank1_su4_phi210_intertwiners_exact(
            intertwiners_report, stabilizer_report
        )
        and _rank1_su4_aligned_carriers_exact(
            aligned_report, intertwiners_report, stabilizer_report
        )
        and _rank1_su4_phi210_quadratic_basis_exact(
            quadratic_report, stabilizer_report, intertwiners_report,
            aligned_report,
        )
        and _rank1_su4_augmented_sos_census_exact(
            census_report, stabilizer_report, intertwiners_report,
            aligned_report, quadratic_report,
        )
        and _file_sha256(
            ROOT / "exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py"
        ) == "589952b9b0a0b6af1543b87c89b0f3626a4bfb9c4219821a915fe04fab8af690"
        and _canonical_json_sha256(report)
        == "f1486e4100e15c457cef9d0377665a06dbbb6a31e9476de1a1c9de5333da8e45"
        and set(report) == {
            "Sym2_target_carriers", "checks", "contragredient_pairings",
            "cubic_coordinate_map", "exact_arithmetic_safety", "failures",
            "model_contract_id", "n_checks", "n_failed", "next_exact_target",
            "overall_state", "physical_cubic_domain", "public_exact_APIs",
            "scope", "source_provenance", "status", "verdict",
        }
        and report.get("status")
        == "EXACT_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_CERTIFIED"
        and report.get("overall_state")
        == "SU4_AUGMENTED_CUBIC_MAP_CLOSED__FULL_SDP_AND_G3_OPEN"
        and report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and report.get("n_checks") == len(check_keys)
        and report.get("n_failed") == 0
        and report.get("failures") == []
        and set(checks) == check_keys
        and all(checks.get(key) is True for key in check_keys)
        and set(scope) == true_scope | false_scope
        and all(scope.get(key) is True for key in true_scope)
        and all(scope.get(key) is False for key in false_scope)
        and set(provenance) == provenance_keys
        and provenance.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and provenance.get("proof_grade") is True
        and provenance.get("all_required_frozen_provenance_exact") is True
        and provenance.get("census_module")
        == "exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py"
        and provenance.get("census_source_sha256")
        == provenance.get("expected_census_source_sha256")
        == _file_sha256(ROOT / provenance.get("census_module", ""))
        == expected_census_source
        and provenance.get("census_report_sha256")
        == provenance.get("expected_census_report_sha256")
        == _canonical_json_sha256(census_report)
        == expected_census_report
        and provenance.get("census_status")
        == "EXACT_RANK1_SU4_AUGMENTED_SOS_CENSUS_AND_UNIVERSAL_MAP_CERTIFIED"
        and provenance.get("census_n_failed") == 0
        and provenance.get("census_physical_G3_gap_target_vector_constructed")
        is False
        and provenance.get("census_physical_G3_gap_cubic_zero_RHS_certified")
        is False
        and provenance.get("aligned_module")
        == "exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py"
        and provenance.get("aligned_source_sha256")
        == provenance.get("expected_aligned_source_sha256")
        == _file_sha256(ROOT / provenance.get("aligned_module", ""))
        == expected_aligned_source
        and provenance.get("aligned_status")
        == "EXACT_RANK1_SU4_ALIGNED_CARRIER_INFRASTRUCTURE_CERTIFIED"
        and provenance.get("aligned_n_failed") == 0
        and provenance.get("intertwiner_module")
        == "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py"
        and provenance.get("intertwiner_source_sha256")
        == provenance.get("expected_intertwiner_source_sha256")
        == _file_sha256(ROOT / provenance.get("intertwiner_module", ""))
        == expected_intertwiner_source
        and provenance.get("quadratic_module")
        == "exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py"
        and provenance.get("quadratic_source_sha256")
        == provenance.get("expected_quadratic_source_sha256")
        == _file_sha256(ROOT / provenance.get("quadratic_module", ""))
        == expected_quadratic_source
        and provenance.get("quadratic_report_sha256")
        == provenance.get("expected_quadratic_report_sha256")
        == _canonical_json_sha256(quadratic_report)
        == expected_quadratic_report
        and provenance.get("quadratic_basis_sha256")
        == provenance.get("expected_quadratic_basis_sha256")
        == quadratic_report.get("quadratic_basis", {}).get("basis_sha256")
        == expected_quadratic_basis
        and provenance.get("live_Schur_parameter_grade_counts")
        == [1, 4, 90, 1_414, 18_085]
        and provenance.get("live_target_invariant_grade_counts")
        == [1, 4, 45, 478, 6_057]
        and set(targets) == target_keys
        and targets.get("proof_grade") is True
        and targets.get("irrep_family_count") == 10
        and targets.get("total_complex_carrier_copy_count") == 540
        and targets.get("total_isotypic_dimension") == 6_032
        and len(target_families) == 10
        and {row.get("irrep") for row in target_families}
        == {"1", "4", "4bar", "6", "10", "10bar", "20", "20bar", "20prime", "15"}
        and all(
            isinstance(row, dict)
            and set(row) == target_family_keys
            and row.get("proof_grade") is True
            for row in target_families
        )
        and all(
            targets.get(key) is True
            for key in (
                "all_common_lowering_word_carriers_have_full_rank_exact",
                "all_copies_aligned_by_exact_highest_weight_universality",
                "all_highest_vectors_raise_to_zero_exact",
                "all_highest_weight_nullities_match_character_census_exact",
                "all_reference_copies_intertwine_9_Chevalley_actions_exact",
            )
        )
        and set(pairings) == pairing_keys
        and pairings.get("proof_grade") is True
        and pairings.get("pairing_family_count") == 10
        and pairings.get("all_pairing_spaces_one_dimensional_exact") is True
        and pairings.get("all_15_compact_tensor_equations_exact") is True
        and len(pairing_families) == 10
        and all(
            isinstance(row, dict)
            and set(row) == pairing_family_keys
            and row.get("exact_nullity") == 1
            and row.get("all_15_compact_tensor_invariance_equations_exact") is True
            and row.get("proof_grade") is True
            for row in pairing_families
        )
        and set(domain) == domain_keys
        and domain.get("proof_grade") is True
        and domain.get("complexified_domain_basis_count") == 1_414
        and domain.get("physical_candidate_count") == 2_754
        and domain.get("physical_basis_count") == 1_414
        and domain.get("domain_modular_pivot_count") == 1_414
        and domain.get("expected_complexified_counts_by_irrep") == expected_counts
        and domain.get("observed_complexified_counts_by_irrep") == expected_counts
        and domain.get("physical_component_counts")
        == {"imaginary_minus": 667, "real_plus": 747}
        and domain.get("physical_real_block_counts") == expected_real_blocks
        and domain.get("all_multiplications_commute_with_physical_conjugation_exact")
        is True
        and domain.get("all_selected_vectors_satisfy_physical_real_structure_exact")
        is True
        and domain.get("all_22_block_provenance_rows_exact") is True
        and domain.get("nonzero_cubic_block_count") == 7
        and domain.get("Gram_symmetric_off_diagonal_multiplier") == 2
        and domain.get("domain_basis_metadata_sha256")
        == "765a0f92ef26b1e8335e212595389ddc73e4a54274fd2b3450f04b9bd56383a5"
        and len(block_rows) == 22
        and all(
            isinstance(row, dict)
            and set(row) == block_row_keys
            and row.get("all_variables_constructed_exact") is True
            for row in block_rows
        )
        and sum(
            int(row.get("constructed_physical_basis_variable_count", 0))
            for row in block_rows
        ) == 1_414
        and set(cubic_map) == map_keys
        and cubic_map.get("proof_grade") is True
        and cubic_map.get("full_physical_image_shape") == [43_820, 1_414]
        and cubic_map.get("full_physical_image_nnz") == 287_472
        and cubic_map.get("full_physical_image_maximum_absolute_entry") == 32
        and cubic_map.get("full_physical_image_sha256")
        == "f2b09f7a6596469b25e1f8c0dc2eb109029f99ac9b774f8deaf335432161e0fb"
        and cubic_map.get("coordinate_map_shape") == [478, 1_414]
        and cubic_map.get("coordinate_map_nnz") == 3_145
        and cubic_map.get("coordinate_map_maximum_absolute_entry") == 32
        and cubic_map.get("coordinate_map_sha256")
        == "77035bb3e5960879c54da3673670eb024b4ed0c0e60752fcc26973eee023941a"
        and cubic_map.get("modular_prime") == 1_000_003
        and cubic_map.get("rank_mod_prime") == 478
        and cubic_map.get("selected_minor_rank_mod_prime") == 478
        and cubic_map.get("selected_minor_determinant_nonzero_mod_prime") is True
        and cubic_map.get("selected_minor_sha256")
        == "6a27a6bb10d4c486e2ae6b0232bd871be088ede4f64daa706c0df66da0a9017f"
        and cubic_map.get("exact_rank") == 478
        and cubic_map.get("exact_kernel_dimension") == 936
        and len(cubic_map.get("independent_domain_column_indices", [])) == 478
        and len(set(cubic_map.get("independent_domain_column_indices", []))) == 478
        and cubic_map.get("target_pivot_row_count") == 478
        and cubic_map.get("target_real_coordinate_count") == 272
        and cubic_map.get("target_imaginary_coordinate_count") == 206
        and cubic_map.get("target_coordinate_metadata_sha256")
        == "fb3f4a2c9fde59b087cc1d95c4f08685ac51b720df354ff0cc2090c37536a482"
        and cubic_map.get("abstract_zero_interface_placeholder_shape") == [478]
        and cubic_map.get("abstract_zero_interface_placeholder_dtype") == "int64"
        and cubic_map.get("abstract_zero_interface_placeholder_nnz") == 0
        and cubic_map.get("all_478_abstract_interface_placeholder_entries_zero_exact")
        is True
        and cubic_map.get("abstract_zero_placeholder_is_not_a_physical_G3_target")
        is True
        and cubic_map.get("physical_G3_gap_target_vector_constructed") is False
        and cubic_map.get("physical_G3_gap_cubic_zero_RHS_certified") is False
        and set(arithmetic) == arithmetic_keys
        and arithmetic.get("proof_grade") is True
        and arithmetic.get("all_recorded_bounds_fit_signed_int64") is True
        and arithmetic.get("checked_sparse_products_reject_unsafe_int64_bounds")
        is True
        and arithmetic.get("conservative_live_product_absolute_bound")
        == 22_686_720
        and arithmetic.get("modular_row_update_absolute_bound")
        == 1_000_005_000_006
        and arithmetic.get("signed_int64_maximum") == 9_223_372_036_854_775_807
        and set(public_apis) == public_api_keys
        and public_apis.get("coordinate_map") == "exact_cubic_coordinate_map()"
        and public_apis.get("abstract_zero_interface_placeholder")
        == "abstract_zero_cubic_interface_placeholder()"
        and public_apis.get("domain_metadata") == "cubic_domain_basis_metadata()"
        and public_apis.get("target_metadata") == "cubic_target_coordinate_metadata()"
    )


def _rank1_su4_augmented_sos_quartic_map_exact(
    report: dict[str, Any],
    census_report: dict[str, Any],
    cubic_report: dict[str, Any],
) -> bool:
    """Fail closed on the exact quartic Schur map, never on PSD or G3."""
    scope = report.get("scope", {})
    dimensions = report.get("dimensions", {})
    provenance = report.get("provenance", {})
    carriers = report.get("carrier_certificate", {})
    pairings = report.get("pairing_certificate", {})
    realification = report.get("realification_certificate", {})
    invariance = report.get("representative_invariance_certificate", {})
    coefficient_map = report.get("coefficient_map_certificate", {})
    cache_contract = report.get("cache_and_mutation_contract", {})
    arithmetic = report.get("arithmetic_contract", {})

    true_scope = {
        "homogeneous_quartic_Schur_coefficient_map_constructed_exact",
        "all_35_complex_carrier_families_constructed_exact",
        "all_22_real_block_pairings_constructed_exact",
    }
    false_scope = {
        "physical_quartic_target_constructed",
        "standard_PSD_congruences_for_real_type_fixed_bases_constructed",
        "semidefinite_feasibility_solved",
        "arbitrary_Phi_stationarity_or_lower_bound_proved",
        "G3_closed",
    }
    carrier_row_keys = {
        "alternate_prime_nullity", "alternate_prime_rank",
        "concatenated_maximum_absolute_entry", "concatenated_nnz",
        "concatenated_sha256", "concatenated_shape", "constraint_nnz",
        "constraint_sha256", "constraint_shape", "copy_count", "dimension",
        "highest_weight", "maximum_rational_reconstruction_denominator",
        "nullity", "raising_residual_zero_exact",
    }
    pairing_row_keys = {
        "component_metric_sha256", "conjugate_dynkin", "copy_count",
        "dimension", "pairing_maximum_absolute_entry", "pairing_nnz",
        "pairing_sha256", "positive_inverse_metric_normalization_exact",
        "rational_inverse_denominator", "real_block_kind",
        "representative_dynkin", "self_conjugate",
    }
    realification_row_keys = {
        "PSD_cone", "block_index", "conjugate_dynkin",
        "first_domain_ordinal", "multiplicity", "past_last_domain_ordinal",
        "physical_component_counts", "quartic_parameter_count",
        "real_block_kind", "real_type_fixed_basis_recipe_sha256",
        "representative_dynkin", "self_conjugate",
    }
    invariance_row_keys = {
        "all_9_Chevalley_tensor_residuals_zero_exact",
        "representative_diagonal_image_physically_real_exact",
        "representative_dynkin", "symmetric_tensor_nnz",
        "symmetric_tensor_sha256",
    }
    map_keys = {
        "coordinate_map_CSR", "coordinate_map_block_nnz",
        "coordinate_map_sha256", "density",
        "estimated_dense_int32_bytes_avoided",
        "estimated_dense_int64_bytes_avoided", "first_modular_prime",
        "first_pass_image_count_until_full_rank",
        "first_prime_elimination_fill", "first_prime_maximum_basis_vector_nnz",
        "first_prime_rank", "full_image_stream_sha256",
        "full_stream_image_count", "kernel_dimension_over_Q_exact",
        "maximum_full_image_absolute_coefficient", "maximum_full_image_nnz",
        "nnz", "physical_component_counts",
        "pivot_physical_quartic_coordinates",
        "pivot_physical_quartic_coordinates_sha256", "proof_grade",
        "rank_argument", "rank_over_Q_exact", "second_modular_prime",
        "second_prime_elimination_fill",
        "second_prime_maximum_basis_vector_nnz",
        "second_prime_selected_minor_rank", "selected_domain_columns",
        "selected_domain_columns_sha256", "shape",
    }
    csr = coefficient_map.get("coordinate_map_CSR", {})
    census_source = provenance.get("census_source", "")
    cubic_source = provenance.get("cubic_source", "")
    return bool(
        _file_sha256(
            ROOT
            / "exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20.py"
        ) == "28633a2dba4d70f019a3e63ca87e8224ca11630a9e7c53bc963aedc6824208c1"
        and _canonical_json_sha256(report)
        == "ac48f6e6183a5b51ced47fcb8f4a1a9218df9bcf0951b632d8644f2a3d850f68"
        and _canonical_json_sha256(census_report)
        == "703a3819fea5afe857757082190f9cf1e22f283ab0ddcc882c2f011b65ba58f3"
        and _canonical_json_sha256(cubic_report)
        == "f1486e4100e15c457cef9d0377665a06dbbb6a31e9476de1a1c9de5333da8e45"
        and set(report) == {
            "arithmetic_contract", "cache_and_mutation_contract",
            "carrier_certificate", "coefficient_map_certificate",
            "dimensions", "honest_conclusion", "model_contract_id",
            "overall_state", "pairing_certificate", "proof_grade",
            "provenance", "realification_certificate",
            "representative_invariance_certificate", "scope", "status",
        }
        and report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and report.get("status")
        == "EXACT_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_CERTIFIED"
        and report.get("overall_state")
        == "SU4_AUGMENTED_QUARTIC_MAP_CLOSED__PHYSICAL_TARGET_SDP_AND_G3_OPEN"
        and report.get("proof_grade") is True
        and isinstance(report.get("honest_conclusion"), str)
        and "G3 remain open" in report.get("honest_conclusion", "")
        and set(scope) == true_scope | false_scope
        and all(scope.get(name) is True for name in true_scope)
        and all(scope.get(name) is False for name in false_scope)
        and set(dimensions) == {
            "Phi", "Sym2_Phi", "complex_isotypic_types",
            "irreducible_copies", "quartic_domain", "quartic_kernel",
            "quartic_target", "real_Schur_blocks",
        }
        and dimensions == {
            "Phi": 210, "Sym2_Phi": 22_155,
            "complex_isotypic_types": 35, "irreducible_copies": 798,
            "real_Schur_blocks": 22, "quartic_domain": 18_085,
            "quartic_target": 6_057, "quartic_kernel": 12_028,
        }
        and set(provenance) == {
            "census_overall_state", "census_source",
            "census_source_sha256_canonical_LF", "census_status",
            "cubic_overall_state", "cubic_source",
            "cubic_source_sha256_canonical_LF", "cubic_status",
            "dependency_hashes_match_exact", "pinned_grade_counts",
            "proof_grade",
        }
        and provenance.get("proof_grade") is True
        and provenance.get("dependency_hashes_match_exact") is True
        and provenance.get("pinned_grade_counts") == {
            "domain": [1, 4, 90, 1_414, 18_085],
            "target": [1, 4, 45, 478, 6_057],
            "kernel": [0, 0, 45, 936, 12_028],
        }
        and census_source
        == "exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py"
        and provenance.get("census_source_sha256_canonical_LF")
        == _file_sha256(ROOT / census_source)
        == "3e0d7f2eac73eec950960f1ffd78c9584a4b15d070c84889080cf4c67d5a4d63"
        and provenance.get("census_status") == census_report.get("status")
        == "EXACT_RANK1_SU4_AUGMENTED_SOS_CENSUS_AND_UNIVERSAL_MAP_CERTIFIED"
        and provenance.get("census_overall_state")
        == census_report.get("overall_state")
        == "SU4_AUGMENTED_SOS_CENSUS_CLOSED__SCHUR_EMBEDDINGS_SDP_AND_G3_OPEN"
        and cubic_source
        == "exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py"
        and provenance.get("cubic_source_sha256_canonical_LF")
        == _file_sha256(ROOT / cubic_source)
        == "589952b9b0a0b6af1543b87c89b0f3626a4bfb9c4219821a915fe04fab8af690"
        and provenance.get("cubic_status") == cubic_report.get("status")
        == "EXACT_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_CERTIFIED"
        and provenance.get("cubic_overall_state")
        == cubic_report.get("overall_state")
        == "SU4_AUGMENTED_CUBIC_MAP_CLOSED__FULL_SDP_AND_G3_OPEN"
        and set(carriers) == {
            "all_exact_highest_nullities_match_at_two_primes",
            "all_exact_raising_residuals_zero", "complex_isotypic_family_count",
            "estimated_CSR_storage_bytes_int64", "families_sha256",
            "irreducible_copy_count", "maximum_absolute_carrier_entry",
            "proof_grade", "rows", "total_carrier_dimension_with_multiplicity",
            "total_concatenated_nnz",
        }
        and carriers.get("proof_grade") is True
        and carriers.get("complex_isotypic_family_count") == 35
        and carriers.get("irreducible_copy_count") == 798
        and carriers.get("total_carrier_dimension_with_multiplicity") == 22_155
        and carriers.get("total_concatenated_nnz") == 177_751
        and carriers.get("maximum_absolute_carrier_entry") == 13_824
        and carriers.get("all_exact_highest_nullities_match_at_two_primes") is True
        and carriers.get("all_exact_raising_residuals_zero") is True
        and len(carriers.get("rows", [])) == 35
        and all(set(row) == carrier_row_keys for row in carriers.get("rows", []))
        and set(pairings) == {
            "all_pairings_are_positive_integer_multiples_of_inverse_metrics_exact",
            "component_metric", "maximum_absolute_pairing_entry",
            "pairings_sha256", "proof_grade", "real_block_count", "rows",
        }
        and pairings.get("proof_grade") is True
        and pairings.get("real_block_count") == 22
        and pairings.get("maximum_absolute_pairing_entry") == 4_976_640
        and pairings.get(
            "all_pairings_are_positive_integer_multiples_of_inverse_metrics_exact"
        ) is True
        and len(pairings.get("rows", [])) == 22
        and all(set(row) == pairing_row_keys for row in pairings.get("rows", []))
        and set(realification) == {
            "all_real_type_fixed_bases_checked_at_both_primes", "block_count",
            "domain_dimension", "integer_realification_convention",
            "ordered_tensor_multiplication_convention", "proof_grade",
            "real_type_warning_for_future_SDP", "rows",
        }
        and realification.get("proof_grade") is True
        and realification.get("block_count") == 22
        and realification.get("domain_dimension") == 18_085
        and realification.get("all_real_type_fixed_bases_checked_at_both_primes")
        is True
        and "must be constructed before an SDP"
        in realification.get("real_type_warning_for_future_SDP", "")
        and len(realification.get("rows", [])) == 22
        and all(
            set(row) == realification_row_keys
            for row in realification.get("rows", [])
        )
        and set(invariance) == {
            "all_22_representative_diagonal_images_physically_real_exact",
            "all_22_representatives_all_9_Chevalley_residuals_zero_exact",
            "proof_grade", "representative_count", "rows",
        }
        and invariance.get("proof_grade") is True
        and invariance.get("representative_count") == 22
        and invariance.get(
            "all_22_representatives_all_9_Chevalley_residuals_zero_exact"
        ) is True
        and invariance.get(
            "all_22_representative_diagonal_images_physically_real_exact"
        ) is True
        and len(invariance.get("rows", [])) == 22
        and all(set(row) == invariance_row_keys for row in invariance.get("rows", []))
        and set(coefficient_map) == map_keys
        and coefficient_map.get("proof_grade") is True
        and coefficient_map.get("shape") == [6_057, 18_085]
        and coefficient_map.get("nnz") == 115_641
        and coefficient_map.get("coordinate_map_sha256")
        == "ebb7b8b5cbca5d1c6e1f41d1e83e7229e2b885ec4fd34e23f305c788a4a1eb9b"
        and coefficient_map.get("full_image_stream_sha256")
        == "4807d170ed880cb4bcccaed29d054826d136d0057326fe2d1b252e1ff109422d"
        and coefficient_map.get("first_modular_prime") == 1_000_003
        and coefficient_map.get("second_modular_prime") == 1_000_033
        and coefficient_map.get("first_prime_rank") == 6_057
        and coefficient_map.get("second_prime_selected_minor_rank") == 6_057
        and coefficient_map.get("rank_over_Q_exact") == 6_057
        and coefficient_map.get("kernel_dimension_over_Q_exact") == 12_028
        and coefficient_map.get("first_pass_image_count_until_full_rank") == 16_140
        and coefficient_map.get("full_stream_image_count") == 18_085
        and coefficient_map.get("maximum_full_image_nnz") == 21_072
        and coefficient_map.get("maximum_full_image_absolute_coefficient")
        == 27_869_184
        and len(coefficient_map.get("selected_domain_columns", [])) == 6_057
        and len(set(coefficient_map.get("selected_domain_columns", []))) == 6_057
        and len(coefficient_map.get("pivot_physical_quartic_coordinates", []))
        == 6_057
        and set(csr) == {"data", "indices", "indptr"}
        and len(csr.get("data", [])) == 115_641
        and len(csr.get("indices", [])) == 115_641
        and len(csr.get("indptr", [])) == 6_058
        and set(cache_contract) == {
            "private_lru_caches_used_for_exact_heavy_objects",
            "public_carrier_and_pairing_data_return_deep_copies",
            "public_sparse_map_returns_defensive_copy",
            "unverified_external_binary_cache_used",
        }
        and cache_contract.get("private_lru_caches_used_for_exact_heavy_objects")
        is True
        and cache_contract.get("public_carrier_and_pairing_data_return_deep_copies")
        is True
        and cache_contract.get("public_sparse_map_returns_defensive_copy") is True
        and cache_contract.get("unverified_external_binary_cache_used") is False
        and set(arithmetic) == {
            "first_modular_prime", "integer_carriers_pairings_images_and_coordinate_map",
            "rational_operations_restricted_to_exact_metric_inversion",
            "second_modular_prime",
            "signed_int64_results_checked_or_python_integer_fallback",
        }
        and arithmetic.get("first_modular_prime") == 1_000_003
        and arithmetic.get("second_modular_prime") == 1_000_033
        and arithmetic.get("integer_carriers_pairings_images_and_coordinate_map")
        is True
        and arithmetic.get("rational_operations_restricted_to_exact_metric_inversion")
        is True
        and arithmetic.get("signed_int64_results_checked_or_python_integer_fallback")
        is True
    )


def _rank1_su4_augmented_sos_psd_routes_and_stale_payload_well_formed(
    report: dict[str, Any],
    census_report: dict[str, Any],
    cubic_report: dict[str, Any],
    quartic_report: dict[str, Any],
) -> bool:
    """Recognize the rejected v20 payload and its retained route schema.

    The standard-cone congruences and lower-grade source APIs are retained as
    generation inputs for v21.  The assembled v20 target was built with the
    wrong quartic chart and is never accepted as a physical target or primal.
    """
    scope = report.get("scope", {})
    routes = report.get("standard_PSD_coordinate_routes", {})
    physical = report.get("physical_target", {})
    full_target = physical.get("full_graded_chart", {})
    quartic_target = physical.get("quartic", {})
    provenance = report.get("provenance", {})
    rejection = report.get("rejection", {})
    expected_hashes = provenance.get("expected_dependency_hashes", {})
    actual_hashes = provenance.get("actual_dependency_hashes", {})
    bindings = provenance.get("dependency_file_bindings", {})

    true_scope = {
        "all_22_standard_PSD_coordinate_routes_constructed",
        "all_nine_real_type_standard_PSD_congruences_constructed",
        "all_thirteen_complex_blocks_in_standard_Hermitian_coordinates",
        "legacy_physical_target_rejected",
        "structural_PSD_routes_retained_for_v21_generation",
    }
    false_scope = {
        "coefficient_map_reparameterized_in_standard_PSD_coordinates",
        "semidefinite_feasibility_solved",
        "exact_primal_PSD_certificate_constructed",
        "exact_dual_Farkas_certificate_constructed",
        "arbitrary_Phi_lower_bound_proved",
        "equality_orbit_classification_proved",
        "full_486_field_Hessian_classification_proved",
        "physical_target_formula_all_five_grades_constructed",
        "physical_target_full_6585_row_vector_constructed",
        "G3_closed",
    }
    pinned_dependency_hashes = {
        "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_V20.json":
            "505f846291320e0671ff1208dc34339d0c2302f24ab80e9569b73d6479b2db8a",
        "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.json":
            "056e1a90c028f0aaca8fb17f2f53dfb02d5e7a33230ec3675537d2778755266a",
        "exact_gauged_u1x_g3_pd_rank_certificate_v20.py":
            "e2499baf3f7a572df7647ca02f109666a549c9e2c1989110c682ee584e0483c6",
        "exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py":
            "5671857444bda7d53db45393e28a3b9ac0784d0f2a63aa1e541eb5e356d23ccc",
        "exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py":
            "3e0d7f2eac73eec950960f1ffd78c9584a4b15d070c84889080cf4c67d5a4d63",
        "exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py":
            "589952b9b0a0b6af1543b87c89b0f3626a4bfb9c4219821a915fe04fab8af690",
        "exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20.py":
            "28633a2dba4d70f019a3e63ca87e8224ca11630a9e7c53bc963aedc6824208c1",
        "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py":
            "76fa77c99b8d6e963e8694acf74280de29ced4c7a7623bffa991aead77329f49",
        "exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py":
            "4eec63ba40b888de736c84f607019ba0f21915028b423578502893744bab1060",
        "exact_gauged_u1x_g3_su5_max_negative_rank1_su3_slice_v20.py":
            "6b2cfe46503833d8ac81dae385bef1bfa192bc0d4aa1dce392f2513b270aa14b",
        "exact_phisigma_casimir_projectors_v20.py":
            "372401c9b760e7b4e2224d4b6b2151611e68e7ba786ec735ebbd8baeb0103355",
    }
    binding_exact = bool(
        set(bindings) == set(pinned_dependency_hashes)
        and all(
            binding.get("imported_file_basename") == name
            and binding.get("repository_local_path") == name
            and binding.get("required_parent") == "."
            and binding.get("portable_sha256") == digest
            for name, digest in pinned_dependency_hashes.items()
            for binding in (bindings.get(name, {}),)
        )
    )
    live_dependencies_exact = all(
        _file_sha256(ROOT / name) == digest
        for name, digest in pinned_dependency_hashes.items()
    )
    prior_quartic_scope = quartic_report.get("scope", {})
    return bool(
        _file_sha256(
            ROOT
            / "exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py"
        ) == "8493a90d9b689bc02479151529ac697425f56087f2bdbebb40176f418b7c0ff8"
        and _canonical_json_sha256(report)
        == "ebd1ec3edf7a02fc3919b55f61906d56269f490d28e70703e25c1c8b88e93566"
        and _canonical_json_sha256(census_report)
        == "703a3819fea5afe857757082190f9cf1e22f283ab0ddcc882c2f011b65ba58f3"
        and _canonical_json_sha256(cubic_report)
        == "f1486e4100e15c457cef9d0377665a06dbbb6a31e9476de1a1c9de5333da8e45"
        and _canonical_json_sha256(quartic_report)
        == "ac48f6e6183a5b51ced47fcb8f4a1a9218df9bcf0951b632d8644f2a3d850f68"
        and set(report) == {
            "claim_boundary", "exact_arithmetic_safety", "model_contract_id",
            "overall_state", "physical_target", "proof_grade", "provenance",
            "rejection", "scope", "standard_PSD_coordinate_routes", "status",
        }
        and report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and report.get("status")
        == "REJECTED_V20_PHYSICAL_TARGET__STRUCTURAL_PSD_ROUTES_ONLY"
        and report.get("overall_state")
        == "STRUCTURAL_PSD_ROUTES_RETAINED__V20_PHYSICAL_TARGET_REJECTED__SUPERSEDED_BY_V21"
        and report.get("proof_grade") is False
        and rejection == {
            "corrected_certificate_raw_sha256":
                "dd40a508a08c219117ddefaf574652a24f0e1f868d011e05f558ecafc9600e03",
            "corrected_map_numerator_csr_sha256":
                "1834c8439fa3e44459f7ba871420a4351cd0b4de194dec6f5c4a84c1f39d3a16",
            "corrected_publication_manifest_raw_sha256":
                "7ecf96a12321b9df5e7d118ce0fb83e65ad9859516b520936408ec4d46a11017",
            "corrected_target_numerator_sha256":
                "14debcfaf02d4b8c20d1d43a2e1f82d6a7390e28428fc63dd21a9c5f90aec0cf",
            "reason": (
                "The v20 extremal-minor raw-Schur reconstruction does not equal "
                "the collapsed ordered-spectral physical quartic, and the "
                "grade-0/grade-1 map normalization is wrong."
            ),
            "retained_content": (
                "The 22 standard PSD-coordinate congruence routes are structural "
                "generation provenance only."
            ),
            "superseded_by": "corrected_rank1_publication_v21",
            "v20_physical_target_accepted": False,
            "v20_primal_or_arbitrary_Phi_theorem_accepted": False,
        }
        and set(scope) == true_scope | false_scope
        and all(scope.get(name) is True for name in true_scope)
        and all(scope.get(name) is False for name in false_scope)
        and routes.get("all_22_cones_have_standard_coordinate_routes") is True
        and routes.get("real_type_block_count") == 9
        and len(routes.get("real_type_rows", [])) == 9
        and routes.get("complex_Hermitian_block_count") == 13
        and len(routes.get("complex_Hermitian_rows", [])) == 13
        and routes.get("standard_real_parameter_count") == 7_979
        and routes.get("standard_complex_parameter_count") == 11_615
        and routes.get("standard_total_parameter_count") == 19_594
        and physical.get("accepted_as_physical_target") is False
        and physical.get("constant") == {"numerator": 237, "denominator": 200}
        and physical.get("cubic", {}).get("row_count") == 478
        and physical.get("cubic", {}).get("all_target_rows_zero_exact") is True
        and quartic_target.get("row_count") == 6_057
        and quartic_target.get("common_denominator") == 3_375
        and quartic_target.get("nonzero_count") == 825
        and quartic_target.get("numerator_sha256")
        == "38476cff340ef8702735d48d7dbdf644ed41f8dc4a359264d33d966f177145ad"
        and quartic_target.get("pivot_physical_quartic_coordinates_sha256")
        == "f33cb0163f3cdc4a3480cb55e09329888c8cf0641cc0acab4cb01f8075058ce4"
        and quartic_target.get("all_i_times_anti_real_rows_zero_exact") is True
        and quartic_target.get("proof_grade") is False
        and full_target.get("grade_lengths") == [1, 4, 45, 478, 6_057]
        and full_target.get("row_count") == 6_585
        and full_target.get("common_denominator") == 1_728_000
        and full_target.get("total_nonzero_count") == 845
        and full_target.get("nonzero_count_by_grade") == {
            "constant": 1, "linear": 2, "quadratic": 17,
            "cubic": 0, "quartic": 825,
        }
        and full_target.get("numerator_sha256")
        == "e2d9eec1b01b3eeefc4a54d404db93171aa6600ea9ef646a215ab0b5401f7630"
        and len(full_target.get("numerator", [])) == 6_585
        and full_target.get("primitive_common_fraction") is True
        and full_target.get("proof_grade") is False
        and provenance.get("repository_local_dependency_root") == "."
        and provenance.get("all_dependency_files_required_beside_this_module")
        is True
        and provenance.get("dependency_hash_algorithm")
        == "SHA256 of UTF-8 text after LF normalization"
        and "no external shadow can satisfy it"
        in provenance.get("source_module_path_binding", "")
        and expected_hashes == pinned_dependency_hashes
        and actual_hashes == pinned_dependency_hashes
        and provenance.get("all_dependency_hashes_match_exact") is True
        and binding_exact
        and live_dependencies_exact
        and prior_quartic_scope.get("physical_quartic_target_constructed")
        is False
        and prior_quartic_scope.get(
            "standard_PSD_congruences_for_real_type_fixed_bases_constructed"
        ) is False
        and prior_quartic_scope.get("semidefinite_feasibility_solved") is False
        and prior_quartic_scope.get(
            "arbitrary_Phi_stationarity_or_lower_bound_proved"
        ) is False
        and prior_quartic_scope.get("G3_closed") is False
    )


def _rank1_su4_augmented_sos_psd_target_exact(
    report: dict[str, Any],
    census_report: dict[str, Any],
    cubic_report: dict[str, Any],
    quartic_report: dict[str, Any],
) -> bool:
    """The v20 assembled physical target is superseded and always rejected."""
    del report, census_report, cubic_report, quartic_report
    return False


def _gauged_u1x_g3_frontier(
    sos_report: dict[str, Any],
    pd_report: dict[str, Any],
    a_square_report: dict[str, Any],
    sos_bfb_report: dict[str, Any],
    kernel_bound_report: dict[str, Any],
    replacement_report: dict[str, Any],
    su5_pd_report: dict[str, Any],
    su5_hsx_report: dict[str, Any],
    su5_hsx_exact_hessian_report: dict[str, Any],
    su5_equality_report: dict[str, Any],
    su5_phi_orbit_report: dict[str, Any],
    su5_phi_local_component_report: dict[str, Any],
    su5_phi_su3_slice_report: dict[str, Any],
    su5_gap_report: dict[str, Any],
    su5_fixed_f_offkernel_report: dict[str, Any],
    su5_max_negative_zero_residual_report: dict[str, Any],
    su5_max_negative_full_residual_report: dict[str, Any],
    su5_max_negative_rank1_su3_slice_report: dict[str, Any],
    rank1_su4_stabilizer_report: dict[str, Any],
    rank1_su4_phi210_intertwiners_report: dict[str, Any],
    rank1_su4_aligned_carriers_report: dict[str, Any],
    rank1_su4_phi210_quadratic_basis_report: dict[str, Any],
    rank1_su4_augmented_sos_census_report: dict[str, Any],
    rank1_su4_augmented_sos_cubic_map_report: dict[str, Any],
    rank1_su4_augmented_sos_quartic_map_report: dict[str, Any],
    rank1_su4_augmented_sos_psd_target_report: dict[str, Any],
    rank1_su4_corrected_publication: dict[str, Any],
    alternative_global_sos_report: dict[str, Any],
) -> dict[str, Any]:
    """Bind rejected branches and the surviving SU(5)+Delta G3 frontier."""
    sos_flags = sos_report.get("flags", {})
    coefficients = sos_report.get("coefficient_vector", {})
    symbolic = coefficients.get("symbolic_nonzero", {})
    quotient = sos_report.get("symmetry_quotient", {})
    nested_pd = sos_report.get("exact_rank_certificate", {})
    nested_a_square = sos_report.get(
        "exact_A_square_recoupling_certificate", {}
    )
    nested_global_counterexample = sos_report.get(
        "exact_global_counterexample_certificate", {}
    )
    nested_global_flags = nested_global_counterexample.get("flags", {})

    pd_flags = pd_report.get("flags", {})
    nested_sos_bfb = sos_report.get(
        "exact_SOS_BFB_stationarity_certificate", {}
    )
    pd_direct = pd_report.get("direct_P_plus_Delta_certificate", {})
    pd_core = pd_report.get("direct_exact_ranks", {}).get(
        "H_Phi_plus_K", {}
    )
    pd_extension = pd_report.get("exact_full_kernel_argument", {})

    a_flags = a_square_report.get("flags", {})
    a_certificate = a_square_report.get("certificate", {})
    sos_bfb_flags = sos_bfb_report.get("flags", {})
    kernel_flags = kernel_bound_report.get("flags", {})
    replacement_flags = replacement_report.get("flags", {})
    su5_scope = su5_pd_report.get("scope", {})
    hsx_flags = su5_hsx_report.get("flag", {})
    hsx_candidate = su5_hsx_report.get("chiral_H_candidate", {})
    hsx_orbit = hsx_candidate.get("exact_orbit", {})
    hsx_bfb = su5_hsx_report.get("BFB_certificate", {})
    hsx_hessian = su5_hsx_report.get("live_full_gradient_and_quotient_Hessian", {})
    hsx_global = su5_hsx_report.get("global_status", {})
    hsx_exact_flags = su5_hsx_exact_hessian_report.get("flags", {})
    equality_scope = su5_equality_report.get("scope", {})
    equality_lemma = su5_equality_report.get("remaining_global_lemma", {})
    equality_global = su5_equality_report.get(
        "Phi_global_signed_zero_theorem", {}
    )
    phi_orbit_scope = su5_phi_orbit_report.get("scope", {})
    phi_orbit_lemma = su5_phi_orbit_report.get("corrected_global_lemma", {})
    phi_local_scope = su5_phi_local_component_report.get("scope", {})
    phi_su3_scope = su5_phi_su3_slice_report.get("scope", {})
    phi_su3_checks = su5_phi_su3_slice_report.get("checks", {})
    gap_flags = su5_gap_report.get("flags", {})
    gap_acceptance = su5_gap_report.get("final_acceptance_test", {})
    gap_reduction = su5_gap_report.get("small_beta_global_reduction", {})
    fixed_f_offkernel_scope = su5_fixed_f_offkernel_report.get("scope", {})
    fixed_f_offkernel_checks = su5_fixed_f_offkernel_report.get("checks", {})
    max_negative_scope = su5_max_negative_zero_residual_report.get("scope", {})
    max_negative_checks = su5_max_negative_zero_residual_report.get("checks", {})
    max_negative_full_scope = su5_max_negative_full_residual_report.get(
        "scope", {}
    )
    max_negative_full_checks = su5_max_negative_full_residual_report.get(
        "checks", {}
    )
    rank1_su3_scope = su5_max_negative_rank1_su3_slice_report.get("scope", {})
    rank1_su3_checks = su5_max_negative_rank1_su3_slice_report.get("checks", {})
    rank1_su4_stabilizer_scope = rank1_su4_stabilizer_report.get("scope", {})
    rank1_su4_stabilizer_checks = rank1_su4_stabilizer_report.get("checks", {})
    rank1_su4_intertwiner_scope = rank1_su4_phi210_intertwiners_report.get(
        "scope", {}
    )
    rank1_su4_intertwiner_checks = rank1_su4_phi210_intertwiners_report.get(
        "checks", {}
    )
    rank1_su4_aligned_scope = rank1_su4_aligned_carriers_report.get(
        "scope", {}
    )
    rank1_su4_quadratic_scope = rank1_su4_phi210_quadratic_basis_report.get(
        "scope", {}
    )
    rank1_su4_census_scope = rank1_su4_augmented_sos_census_report.get(
        "scope", {}
    )
    rank1_su4_cubic_scope = rank1_su4_augmented_sos_cubic_map_report.get(
        "scope", {}
    )
    rank1_su4_quartic_scope = rank1_su4_augmented_sos_quartic_map_report.get(
        "scope", {}
    )
    rank1_su4_quartic_map = rank1_su4_augmented_sos_quartic_map_report.get(
        "coefficient_map_certificate", {}
    )
    rank1_su4_psd_target_scope = rank1_su4_augmented_sos_psd_target_report.get(
        "scope", {}
    )
    rank1_su4_psd_routes = rank1_su4_augmented_sos_psd_target_report.get(
        "standard_PSD_coordinate_routes", {}
    )
    rank1_su4_physical_target = rank1_su4_augmented_sos_psd_target_report.get(
        "physical_target", {}
    )
    rank1_su4_full_target = rank1_su4_physical_target.get(
        "full_graded_chart", {}
    )
    rank1_su4_quartic_target = rank1_su4_physical_target.get("quartic", {})
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
    alternative_flags = alternative_global_sos_report.get("flags", {})

    artifacts_present = {
        "SOS_candidate": bool(sos_report),
        "direct_exact_PD_rank": bool(pd_report),
        "exact_A_square_recoupling": bool(a_square_report),
        "exact_SOS_BFB_stationarity": bool(sos_bfb_report),
        "fixed_P_kernel_no_go": bool(kernel_bound_report),
        "lower_replacement_orbit": bool(replacement_report),
        "SU5_Delta_PD_global_SOS": bool(su5_pd_report),
        "SU5_Delta_HSX_extension": bool(su5_hsx_report),
        "SU5_Delta_HSX_exact_Hessian": bool(su5_hsx_exact_hessian_report),
        "SU5_Delta_equality_orbit": bool(su5_equality_report),
        "SU5_Delta_Phi_orbit_lemma_audit": bool(su5_phi_orbit_report),
        "SU5_Delta_Phi_local_component_theorem": bool(
            su5_phi_local_component_report
        ),
        "SU5_Delta_Phi_SU3_fixed_slice_theorem": bool(
            su5_phi_su3_slice_report
        ),
        "SU5_Delta_chiral_global_gap_reduction": bool(su5_gap_report),
        "SU5_fixed_F_full_offkernel_bound": bool(su5_fixed_f_offkernel_report),
        "SU5_max_negative_all_zero_residual_bound": bool(
            su5_max_negative_zero_residual_report
        ),
        "SU5_max_negative_full_residual_pure_Delta_bound": bool(
            su5_max_negative_full_residual_report
        ),
        "SU5_max_negative_rank1_SU3_four_dimensional_slice_bound": bool(
            su5_max_negative_rank1_su3_slice_report
        ),
        "rank1_SU4_stabilizer_infrastructure": bool(rank1_su4_stabilizer_report),
        "rank1_SU4_Phi210_intertwiner_infrastructure": bool(
            rank1_su4_phi210_intertwiners_report
        ),
        "rank1_SU4_aligned_carrier_infrastructure": bool(
            rank1_su4_aligned_carriers_report
        ),
        "rank1_SU4_Phi210_quadratic_basis": bool(
            rank1_su4_phi210_quadratic_basis_report
        ),
        "rank1_SU4_augmented_SOS_census": bool(
            rank1_su4_augmented_sos_census_report
        ),
        "rank1_SU4_augmented_SOS_cubic_map": bool(
            rank1_su4_augmented_sos_cubic_map_report
        ),
        "rank1_SU4_augmented_SOS_quartic_map": bool(
            rank1_su4_augmented_sos_quartic_map_report
        ),
        "rank1_SU4_legacy_v20_PSD_routes_and_rejected_target": bool(
            rank1_su4_augmented_sos_psd_target_report
        ),
        "rank1_SU4_corrected_fixed_endpoint_publication_v21": bool(
            rank1_su4_corrected_publication
        ),
        "alternative_global_SOS_audit": bool(alternative_global_sos_report),
    }
    a_square_exact = bool(
        a_square_report.get("status") == "EXACT_A_SQUARE_RECOUPLING_CERTIFIED"
        and a_square_report.get("overall_state") == "CLOSED_SUBPROBLEM"
        and a_square_report.get("n_failed") == 0
        and a_certificate.get("source_binding_exact") is True
        and a_certificate.get("proof_grade") is True
        and a_certificate.get("unique_weights")
        == ["40", "72", "28", "-8", "-12", "12"]
        and a_flags.get("A_square_recoupling_exactly_source_bound") is True
        and a_flags.get("complete_potential_BFB_exactly_certified") is False
        and a_flags.get("full_Hessian_exactly_source_bound") is False
        and a_flags.get("strict_local_minimum_certified") is False
        and a_flags.get("G3_closed") is False
    )
    sos_bfb_exact = bool(
        sos_bfb_report.get("status")
        == "EXACT_COMPLETE_POTENTIAL_BFB_AND_SELECTED_STATIONARITY_CERTIFIED"
        and sos_bfb_report.get("overall_state") == "CLOSED_SUBPROBLEM"
        and sos_bfb_report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and sos_bfb_report.get("n_failed") == 0
        and sos_bfb_flags.get(
            "complete_27_parameter_SOS_identity_exactly_source_bound"
        )
        is True
        and sos_bfb_flags.get("complete_potential_BFB_exactly_certified") is True
        and sos_bfb_flags.get("selected_vacuum_stationarity_exactly_certified")
        is True
        and sos_bfb_flags.get("selected_vacuum_global_minimum_certified") is False
        and sos_bfb_flags.get("selected_vacuum_unique_modulo_symmetry") is False
        and sos_bfb_flags.get("G3_closed") is False
    )
    pd_direct_and_fail_closed = bool(
        pd_report.get("status")
        == "DIRECT_EXACT_TRANSVERSE_HESSIAN_PASS__SOS_AND_GLOBAL_EXTREMA_EXTERNAL"
        and pd_report.get("overall_state") == STATUS_OPEN
        and pd_report.get("n_failed") == 0
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
    sos_exact_local_and_globally_rejected = bool(
        sos_report.get("status")
        == "EXACT_BFB_STATIONARY_STRICT_LOCAL_MINIMUM__GLOBAL_COUNTEREXAMPLE"
        and sos_report.get("overall_state") == STATUS_OPEN
        and sos_report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and sos_report.get("n_failed") == 0
        and coefficients.get("nonzero_count") == 27
        and coefficients.get("maximum_absolute_coefficient") == 9.125
        and symbolic.get("lambda::O48_B01_Phi_self_quartics") == "-21/200"
        and quotient.get("SO10_plus_U1X_plus_global_PQ_rank") == 38
        and quotient.get("massive_transverse_dimension") == 448
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
        and nested_pd.get("status") == pd_report.get("status")
        and nested_pd.get("direct_exact_ranks", {}).get("H_Phi_plus_K", {})
        == pd_core
        and nested_sos_bfb.get("status") == sos_bfb_report.get("status")
        and nested_a_square.get("status") == a_square_report.get("status")
        and nested_a_square.get("certificate", {}).get("unique_weights")
        == a_certificate.get("unique_weights")
        and nested_global_counterexample.get("n_failed") == 0
        and nested_global_flags.get(
            "lower_energy_field_witness_exactly_certified"
        )
        is True
        and nested_global_flags.get("selected_vacuum_global_minimum_disproved")
        is True
    )
    fixed_p_no_go_exact = bool(
        kernel_bound_report.get("n_failed") == 0
        and kernel_flags.get("fixed_P_strict_local_global_no_go_exact") is True
        and kernel_flags.get("fixed_P_branch_closed_negative") is True
        and kernel_flags.get("G3_closed") is False
        and kernel_flags.get("whole_model_excluded") is False
    )
    replacement_wrong_symmetry = bool(
        replacement_report.get("n_failed") == 0
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
    su5_pd_exact_frontier = bool(
        su5_pd_report.get("n_failed") == 0
        and su5_pd_report.get("status")
        == "EXACT_SU5_DELTA_PD_GLOBAL_SOS_CANDIDATE_CERTIFIED"
        and su5_scope.get("Phi_Sigma_global_minimum_exact") is True
        and su5_scope.get("Phi_Sigma_stationarity_exact") is True
        and su5_scope.get("SO10_to_SM_stabilizer_dimension_exact") is True
        and su5_scope.get("Phi_Sigma_Hessian_rank_429_nullity_33_exact") is True
        and su5_scope.get("Phi_Sigma_quotient_strictly_positive_exact") is True
        and su5_scope.get("Phi_Sigma_equality_set_locally_one_orbit") is True
        and su5_scope.get("full_486_field_stationarity") is False
        and su5_scope.get("global_orbit_uniqueness") is False
        and su5_scope.get("G3_closed") is False
    )
    su5_hsx_honest_frontier = bool(
        su5_hsx_report.get("n_failed") == 0
        and su5_hsx_report.get("status")
        == "EXACT_REAL_H_NO_GO__CHIRAL_H_STRICT_LOCAL_CANDIDATE__GLOBAL_GAP_OPEN"
        and su5_hsx_report.get("overall_state")
        == "G3_PROMISING_CANDIDATE_NOT_CLOSED"
        and su5_hsx_report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and hsx_flags.get("real_H_e6_extension_exactly_excluded") is True
        and hsx_flags.get("chiral_H_exact_stationary_candidate_constructed")
        is True
        and hsx_flags.get("full_486_gradient_zero_live") is True
        and hsx_flags.get(
            "strict_448_quotient_local_minimum_high_confidence_numeric"
        )
        is True
        and hsx_flags.get("full_quartic_BFB_certified") is True
        and hsx_flags.get("full_global_minimum_certified") is False
        and hsx_flags.get("G3_closed") is False
        and hsx_flags.get("whole_model_excluded") is False
        and hsx_orbit.get("SO10_rank") == 36
        and hsx_orbit.get("SO10_plus_U1X_rank") == 37
        and hsx_orbit.get("SO10_plus_U1X_plus_PQ_rank") == 38
        and hsx_orbit.get("physical_quotient_dimension") == 448
        and hsx_orbit.get("source_binding_exact") is True
        and hsx_bfb.get("homogeneous_quartic_BFB_certified") is True
        and hsx_bfb.get("finite_field_global_gap_certified") is False
        and hsx_hessian.get("proof_grade") is False
        and hsx_hessian.get("transverse_dimension") == 448
        and hsx_hessian.get("negative_transverse_eigenvalues_below_minus_1e_minus_9")
        == 0
        and hsx_hessian.get("zero_transverse_eigenvalues_at_1e_minus_9") == 0
        and hsx_global.get("full_homogeneous_quartic_BFB_exact") is True
        and hsx_global.get("beta_deformed_finite_field_global_gap_exact") is False
        and hsx_global.get("global_equality_orbits_classified") is False
        and hsx_global.get("G3_closed") is False
    )
    su5_hsx_exact_hessian_closed = bool(
        su5_hsx_exact_hessian_report.get("status")
        == "EXACT_FULL_HESSIAN_RANK_448_NULLITY_38_CERTIFIED"
        and su5_hsx_exact_hessian_report.get("overall_state")
        == "CLOSED_FULL_LOCAL_HESSIAN_SUBPROBLEM"
        and su5_hsx_exact_hessian_report.get("model_contract_id")
        == AUTHORITATIVE_CONTRACT_ID
        and su5_hsx_exact_hessian_report.get("n_failed") == 0
        and hsx_exact_flags.get("exact_rank_448") is True
        and hsx_exact_flags.get("exact_nullity_38") is True
        and hsx_exact_flags.get("exact_PSD") is True
        and hsx_exact_flags.get("strict_quotient_positive") is True
        and hsx_exact_flags.get("kernel_equals_38_symmetry_tangents") is True
        and hsx_exact_flags.get("source_binding_exact") is True
        and hsx_exact_flags.get("proof_grade") is True
        and su5_hsx_exact_hessian_report.get("G3_closed") is False
    )
    su5_equality_honestly_reduced = bool(
        su5_equality_report.get("n_failed") == 0
        and su5_equality_report.get("status")
        == "EXACT_GLOBAL_EQUALITY_CLASSIFICATION__SIGNED_PHI_THEOREM_CLOSED__G3_OPEN"
        and su5_equality_report.get("overall_state")
        == "GLOBAL_EQUALITY_ORBITS_CLOSED"
        and equality_scope.get("fixed_F_Sigma_global_equality_classified") is True
        and equality_scope.get(
            "fixed_Delta_diagonal_Phi_global_equality_classified"
        )
        is True
        and equality_scope.get(
            "fixed_Delta_two_tau_plus_representatives_equivalent"
        )
        is True
        and equality_scope.get("literal_single_Phi_orbit_statement_refuted")
        is True
        and equality_scope.get("minus_F_mixed_branch_excluded_exact") is True
        and equality_scope.get("corrected_signed_Phi_orbit_theorem_open") is False
        and equality_scope.get("corrected_signed_Phi_orbit_theorem_proved")
        is True
        and equality_scope.get("signed_Phi_orbits_locally_isolated_exactly")
        is True
        and equality_scope.get("complete_SU3_fixed_Phi_slice_classified_exactly")
        is True
        and equality_scope.get("distant_disconnected_Phi_components_excluded")
        is True
        and equality_scope.get(
            "all_arbitrary_Phi_global_equalities_classified"
        )
        is True
        and equality_scope.get("global_equality_orbit_classification_complete")
        is True
        and equality_scope.get("quantitative_beta_global_coercivity_proved")
        is False
        and equality_scope.get("G3_closed") is False
        and equality_scope.get("whole_model_excluded") is False
        and equality_lemma.get("proved") is True
        and equality_lemma.get("literal_single_orbit_version_refuted") is True
        and equality_lemma.get("corrected_signed_two_orbit_version") is True
        and equality_lemma.get("source_bound_certificate_available") is True
        and equality_lemma.get("source_bound_partial_certificate_available") is True
        and equality_lemma.get("signed_orbits_locally_isolated_exactly") is True
        and equality_lemma.get("complete_SU3_fixed_slice_classified_exactly")
        is True
        and equality_lemma.get("SU3_fixed_slice_real_dimension") == 16
        and equality_lemma.get("distant_disconnected_components_excluded") is True
        and equality_lemma.get("quantitative_orbit_distance_bound_proved")
        is False
        and equality_lemma.get("numerical_search_is_not_a_substitute") is True
        and equality_global.get("frozen_source_sha256")
        == "17038c6fb82ba565a16228f5f5c03026f0ab8e3ad7959792498c2785b9653066"
        and equality_global.get("core_sha256")
        == "db493a74303a57862f09c2a92118ea3d66b8b12ecbaea9162155d4ab3baafecc"
        and equality_global.get("external_theorem_dependency", {}).get("kind")
        == "published subgroup-classification theorem"
    )
    su5_phi_orbit_audit_honest = bool(
        su5_phi_orbit_report.get("status")
        == "LITERAL_SINGLE_ORBIT_LEMMA_REFUTED__SIGNED_GLOBAL_LEMMA_OPEN"
        and su5_phi_orbit_report.get("overall_state")
        == "SHARP_COUNTEREXAMPLE_AND_REDUCTION"
        and su5_phi_orbit_report.get("n_failed") == 0
        and phi_orbit_scope.get("literal_plus_orbit_only_statement_refuted")
        is True
        and phi_orbit_scope.get("complete_SU4_invariant_slice_classified")
        is True
        and phi_orbit_scope.get("corrected_signed_two_orbit_theorem_proved")
        is False
        and phi_orbit_scope.get("all_arbitrary_real_four_forms_classified")
        is False
        and phi_orbit_scope.get(
            "PD_global_equality_orbit_classification_complete"
        )
        is False
        and phi_orbit_scope.get("G3_closed") is False
        and phi_orbit_scope.get("whole_model_excluded") is False
        and phi_orbit_lemma.get("proved") is False
        and phi_orbit_lemma.get("counterexample_found") is False
    )
    su5_phi_local_components_closed = bool(
        su5_phi_local_component_report.get("status")
        == "EXACT_LOCAL_COMPONENT_THEOREM_CLOSED__DISTANT_COMPONENTS_OPEN"
        and su5_phi_local_component_report.get("overall_state")
        == "LOCAL_COMPONENT_THEOREM_CLOSED"
        and su5_phi_local_component_report.get("n_failed") == 0
        and phi_local_scope.get("plus_F_local_component_classified") is True
        and phi_local_scope.get("minus_F_local_component_classified") is True
        and phi_local_scope.get("signed_orbit_locally_isolated") is True
        and phi_local_scope.get("explicit_neighborhood_radius_available") is False
        and phi_local_scope.get("disconnected_distant_components_excluded")
        is False
        and phi_local_scope.get("corrected_signed_global_orbit_theorem_proved")
        is False
        and phi_local_scope.get(
            "PD_global_equality_orbit_classification_complete"
        )
        is False
        and phi_local_scope.get("G3_closed") is False
        and phi_local_scope.get("whole_model_excluded") is False
    )
    su5_phi_su3_slice_closed = bool(
        su5_phi_su3_slice_report.get("status")
        == "EXACT_COMPLETE_SU3_FIXED_SLICE_CLASSIFIED__GENERIC_GLOBAL_OPEN"
        and su5_phi_su3_slice_report.get("overall_state")
        == "SU3_FIXED_SLICE_CLOSED"
        and su5_phi_su3_slice_report.get("n_failed") == 0
        and phi_su3_checks.get("displayed_space_is_complete_SU3_fixed_space")
        is True
        and phi_su3_checks.get("restricted_projector_rowspace_reduced_exactly")
        is True
        and phi_su3_checks.get(
            "eight_nondiagonal_directions_have_real_SOS_obstruction"
        )
        is True
        and phi_su3_checks.get("complete_SU3_fixed_slice_is_signed_Kahler_orbit")
        is True
        and phi_su3_scope.get(
            "complete_16_real_dimensional_SU3_fixed_space_classified"
        )
        is True
        and phi_su3_scope.get(
            "all_nonzero_slice_solutions_are_signed_Kahler_squares"
        )
        is True
        and phi_su3_scope.get("all_arbitrary_real_four_forms_classified") is False
        and phi_su3_scope.get("disconnected_distant_components_excluded") is False
        and phi_su3_scope.get("corrected_signed_global_orbit_theorem_proved")
        is False
        and phi_su3_scope.get("G3_closed") is False
        and phi_su3_scope.get("whole_model_excluded") is False
    )
    su5_chiral_gap_honestly_reduced = bool(
        su5_gap_report.get("n_failed") == 0
        and su5_gap_report.get("status")
        == "GLOBAL_GAP_REDUCED_TO_QUANTITATIVE_COERCIVITY"
        and su5_gap_report.get("overall_state") == "FINAL_G3_TEST_OPEN"
        and su5_gap_report.get("model_contract_id") == AUTHORITATIVE_CONTRACT_ID
        and gap_flags.get("lower_witness_found") is False
        and gap_flags.get("conditional_small_positive_beta_route_exists") is True
        and gap_flags.get("beta_1_over_20_global_minimum_certified") is False
        and gap_flags.get("PD_equality_orbits_classified") is True
        and gap_flags.get("global_equality_orbits_classified") is False
        and gap_flags.get("G3_closed") is False
        and gap_flags.get("whole_model_excluded") is False
        and gap_acceptance.get("currently_passes") is False
        and gap_reduction.get("theorem_ready") is False
        and gap_reduction.get("beta_equals_1_over_20_covered_by_theorem") is False
    )
    su5_fixed_f_full_gap_closed = bool(
        su5_fixed_f_offkernel_report.get("n_failed") == 0
        and su5_fixed_f_offkernel_report.get("status")
        == "EXACT_FIXED_F_FULL_OFFKERNEL_BETA_GAP_CERTIFIED"
        and su5_fixed_f_offkernel_report.get("overall_state")
        == "CLOSED_FIXED_F_GLOBAL_SUBPROBLEM"
        and fixed_f_offkernel_checks.get(
            "mixed_offkernel_gap_at_least_6_over_5_exact"
        )
        is True
        and fixed_f_offkernel_checks.get("pure_hplus_current_error_bound_exact")
        is True
        and fixed_f_offkernel_checks.get("kernel_chirality_cross_zero_exact")
        is True
        and fixed_f_offkernel_checks.get("cross_block_bound_exact") is True
        and fixed_f_offkernel_checks.get("rational_inside_outside_patch_positive")
        is True
        and fixed_f_offkernel_checks.get("full_fixed_F_equality_orbit_exact")
        is True
        and fixed_f_offkernel_scope.get("Phi_fixed_to_F") is True
        and fixed_f_offkernel_scope.get("H_arbitrary") is True
        and fixed_f_offkernel_scope.get("Sigma_arbitrary") is True
        and fixed_f_offkernel_scope.get("beta_equals_1_over_20") is True
        and fixed_f_offkernel_scope.get(
            "global_gap_nonnegative_on_full_fixed_F_stratum"
        )
        is True
        and fixed_f_offkernel_scope.get("equality_is_selected_SU5_flag_orbit")
        is True
        and fixed_f_offkernel_scope.get("arbitrary_Phi_proved") is False
        and fixed_f_offkernel_scope.get("G3_closed") is False
    )
    su5_max_negative_all_zero_route_excluded = bool(
        su5_max_negative_zero_residual_report.get("n_failed") == 0
        and su5_max_negative_zero_residual_report.get("status")
        == "EXACT_PURE_DELTA_MAX_NEGATIVE_MIXED_ZERO_ROUTE_EXCLUDED"
        and su5_max_negative_zero_residual_report.get("overall_state")
        == "CLOSED_PURE_DELTA_MAX_NEGATIVE_MIXED_ZERO_STRATUM__ARBITRARY_PHI_OPEN"
        and su5_max_negative_zero_residual_report.get("model_contract_id")
        == AUTHORITATIVE_CONTRACT_ID
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
        and su5_max_negative_zero_residual_report.get("exact_stratum_gap", {}).get(
            "strict_margin"
        )
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
        su5_max_negative_full_residual_report.get("n_failed") == 0
        and su5_max_negative_full_residual_report.get("status")
        == "EXACT_MAX_NEGATIVE_FULL_RESIDUAL_PURE_DELTA_BOUND_CERTIFIED"
        and su5_max_negative_full_residual_report.get("overall_state")
        == "CLOSED_MAX_NEGATIVE_PURE_DELTA_ARBITRARY_PHI_SUBPROBLEM"
        and su5_max_negative_full_residual_report.get("model_contract_id")
        == AUTHORITATIVE_CONTRACT_ID
        and max_negative_full_scope.get("Sigma_on_pure_Delta_orbit") is True
        and max_negative_full_scope.get(
            "H_current_saturates_I45_equals_minus_NH_NSigma"
        )
        is True
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
    rank1_required_checks = (
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
    su5_max_negative_rank1_su3_slice_closed = bool(
        su5_max_negative_rank1_su3_slice_report.get("n_failed") == 0
        and su5_max_negative_rank1_su3_slice_report.get("failed_checks") == []
        and su5_max_negative_rank1_su3_slice_report.get("status")
        == "EXACT_RANK1_SU3_DANGEROUS_SLICE_BOUND_CERTIFIED"
        and su5_max_negative_rank1_su3_slice_report.get("overall_state")
        == "CLOSED_RANK1_SU3_SLICE__ARBITRARY_RANK1_PHI_OPEN"
        and su5_max_negative_rank1_su3_slice_report.get("model_contract_id")
        == AUTHORITATIVE_CONTRACT_ID
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
            for name in rank1_required_checks
        )
        and rank1_su3_checks.get("arbitrary_rank1_Phi_proved") is False
        and rank1_su3_checks.get("arbitrary_Sigma35_proved") is False
        and rank1_su3_checks.get("G3_closed") is False
        and su5_max_negative_rank1_su3_slice_report.get("SOS", {}).get(
            "strict_anchor_lower_bound"
        )
        == "3/200"
        and su5_max_negative_rank1_su3_slice_report.get("radial_patch", {}).get(
            "restricted_global_minimum"
        )
        == "1/5000"
    )
    rank1_su4_stabilizer_infrastructure_exact = (
        _rank1_su4_stabilizer_infrastructure_exact(rank1_su4_stabilizer_report)
    )
    rank1_su4_phi210_intertwiners_exact = (
        _rank1_su4_phi210_intertwiners_exact(
            rank1_su4_phi210_intertwiners_report,
            rank1_su4_stabilizer_report,
        )
    )
    rank1_su4_aligned_carriers_exact = _rank1_su4_aligned_carriers_exact(
        rank1_su4_aligned_carriers_report,
        rank1_su4_phi210_intertwiners_report,
        rank1_su4_stabilizer_report,
    )
    rank1_su4_phi210_quadratic_basis_exact = (
        _rank1_su4_phi210_quadratic_basis_exact(
            rank1_su4_phi210_quadratic_basis_report,
            rank1_su4_stabilizer_report,
            rank1_su4_phi210_intertwiners_report,
            rank1_su4_aligned_carriers_report,
        )
    )
    rank1_su4_augmented_sos_census_exact = (
        _rank1_su4_augmented_sos_census_exact(
            rank1_su4_augmented_sos_census_report,
            rank1_su4_stabilizer_report,
            rank1_su4_phi210_intertwiners_report,
            rank1_su4_aligned_carriers_report,
            rank1_su4_phi210_quadratic_basis_report,
        )
    )
    rank1_su4_augmented_sos_cubic_map_exact = (
        _rank1_su4_augmented_sos_cubic_map_exact(
            rank1_su4_augmented_sos_cubic_map_report,
            rank1_su4_stabilizer_report,
            rank1_su4_phi210_intertwiners_report,
            rank1_su4_aligned_carriers_report,
            rank1_su4_phi210_quadratic_basis_report,
            rank1_su4_augmented_sos_census_report,
        )
    )
    rank1_su4_augmented_sos_quartic_map_exact = (
        rank1_su4_augmented_sos_census_exact
        and rank1_su4_augmented_sos_cubic_map_exact
        and _rank1_su4_augmented_sos_quartic_map_exact(
            rank1_su4_augmented_sos_quartic_map_report,
            rank1_su4_augmented_sos_census_report,
            rank1_su4_augmented_sos_cubic_map_report,
        )
    )
    rank1_su4_legacy_psd_routes_and_stale_payload_well_formed = (
        rank1_su4_augmented_sos_quartic_map_exact
        and _rank1_su4_augmented_sos_psd_routes_and_stale_payload_well_formed(
            rank1_su4_augmented_sos_psd_target_report,
            rank1_su4_augmented_sos_census_report,
            rank1_su4_augmented_sos_cubic_map_report,
            rank1_su4_augmented_sos_quartic_map_report,
        )
    )
    alternative_global_sos_honestly_open = bool(
        alternative_global_sos_report.get("n_failed") == 0
        and alternative_global_sos_report.get("status")
        == "ALTERNATIVE_GLOBAL_SOS_AUDIT_COMPLETE__NO_CERTIFIED_REPLACEMENT"
        and alternative_global_sos_report.get("overall_state")
        == "G3_GLOBAL_ALTERNATIVE_OPEN"
        and alternative_flags.get(
            "all_vanishing_45_current_Gram_completion_excluded"
        )
        is True
        and alternative_flags.get(
            "all_vanishing_affine_SOS_completion_excluded"
        )
        is True
        and alternative_flags.get(
            "all_vanishing_unique_chiral_quartic_completion_excluded"
        )
        is True
        and alternative_flags.get(
            "nonvanishing_residual_gradient_cancellation_excluded"
        )
        is False
        and alternative_flags.get("different_vacuum_orbit_excluded") is False
        and alternative_flags.get("globally_certifiable_alternative_found") is False
        and alternative_flags.get("current_candidate_global_minimum_certified")
        is False
        and alternative_flags.get("G3_closed") is False
        and alternative_flags.get("whole_model_excluded") is False
    )
    integrity_pass = bool(
        all(artifacts_present.values())
        and a_square_exact
        and sos_bfb_exact
        and pd_direct_and_fail_closed
        and sos_exact_local_and_globally_rejected
        and fixed_p_no_go_exact
        and replacement_wrong_symmetry
        and su5_pd_exact_frontier
        and su5_hsx_honest_frontier
        and su5_hsx_exact_hessian_closed
        and su5_equality_honestly_reduced
        and su5_phi_orbit_audit_honest
        and su5_phi_local_components_closed
        and su5_phi_su3_slice_closed
        and su5_chiral_gap_honestly_reduced
        and su5_fixed_f_full_gap_closed
        and su5_max_negative_all_zero_route_excluded
        and su5_max_negative_full_residual_pure_delta_closed
        and su5_max_negative_rank1_su3_slice_closed
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
    )
    return {
        "model_contract_id": AUTHORITATIVE_CONTRACT_ID,
        "overall_state": STATUS_OPEN if integrity_pass else "EXECUTION_FAIL",
        "artifacts_present": artifacts_present,
        "integrity_pass": integrity_pass,
        "exact_A_square_recoupling_source_bound": a_square_exact,
        "exact_SOS_BFB_stationarity_source_bound": sos_bfb_exact,
        "direct_exact_PD_rank_honestly_scoped": pd_direct_and_fail_closed,
        "SOS_candidate_exact_local_and_globally_rejected": (
            sos_exact_local_and_globally_rejected
        ),
        "fixed_P_branch_exactly_excluded": fixed_p_no_go_exact,
        "lower_replacement_rejected_for_wrong_symmetry": replacement_wrong_symmetry,
        "SU5_Delta_PD_exact_global_frontier": su5_pd_exact_frontier,
        "SU5_Delta_PD_exact_Hessian_rank": 429
        if su5_pd_exact_frontier
        else None,
        "SU5_Delta_PD_exact_Hessian_nullity": 33
        if su5_pd_exact_frontier
        else None,
        "SU5_Delta_PD_full_486_extension_open": not bool(
            su5_scope.get("full_486_field_stationarity")
        ),
        "SU5_Delta_PD_disconnected_equality_orbits_open": not bool(
            equality_scope.get("global_equality_orbit_classification_complete")
        ),
        "SU5_Delta_PD_equality_orbits_classified_exactly": bool(
            equality_scope.get("global_equality_orbit_classification_complete")
        ),
        "SU5_Delta_HSX_honest_frontier": su5_hsx_honest_frontier,
        "SU5_Delta_HSX_nonzero_real_parameters": (
            su5_hsx_report.get("coefficient_map", {}).get("nonzero_count")
        ),
        "SU5_Delta_HSX_maximum_absolute_coefficient": (
            su5_hsx_report.get("coefficient_map", {}).get(
                "maximum_absolute_coefficient"
            )
        ),
        "SU5_Delta_HSX_exact_symmetry_ranks": [
            hsx_orbit.get("SO10_rank"),
            hsx_orbit.get("SO10_plus_U1X_rank"),
            hsx_orbit.get("SO10_plus_U1X_plus_PQ_rank"),
        ],
        "SU5_Delta_HSX_transverse_dimension": hsx_hessian.get(
            "transverse_dimension"
        ),
        "SU5_Delta_HSX_minimum_transverse_eigenvalue_numeric": hsx_hessian.get(
            "minimum_transverse_eigenvalue"
        ),
        "SU5_Delta_HSX_full_Hessian_proof_grade": hsx_hessian.get("proof_grade"),
        "SU5_Delta_HSX_exact_Hessian_closed": su5_hsx_exact_hessian_closed,
        "SU5_Delta_HSX_exact_Hessian_rank": 448
        if su5_hsx_exact_hessian_closed
        else None,
        "SU5_Delta_HSX_exact_Hessian_nullity": 38
        if su5_hsx_exact_hessian_closed
        else None,
        "SU5_Delta_HSX_exact_Hessian_PSD": hsx_exact_flags.get("exact_PSD"),
        "SU5_Delta_HSX_exact_Hessian_kernel_is_symmetry": hsx_exact_flags.get(
            "kernel_equals_38_symmetry_tangents"
        ),
        "SU5_Delta_HSX_exact_quotient_positive": hsx_exact_flags.get(
            "strict_quotient_positive"
        ),
        "SU5_Delta_HSX_full_quartic_BFB_exact": hsx_global.get(
            "full_homogeneous_quartic_BFB_exact"
        ),
        "SU5_Delta_HSX_finite_field_global_gap_open": not bool(
            hsx_global.get("beta_deformed_finite_field_global_gap_exact")
        ),
        "SU5_Delta_HSX_global_equality_classification_open": not bool(
            hsx_global.get("global_equality_orbits_classified")
        ),
        "SU5_Delta_equality_honestly_reduced": su5_equality_honestly_reduced,
        "SU5_Delta_Phi_orbit_audit_honest": su5_phi_orbit_audit_honest,
        "SU5_Delta_literal_single_Phi_orbit_refuted": phi_orbit_scope.get(
            "literal_plus_orbit_only_statement_refuted"
        ),
        "SU5_Delta_signed_Phi_orbit_theorem_open": not bool(
            equality_scope.get("corrected_signed_Phi_orbit_theorem_proved")
        ),
        "SU5_Delta_signed_Phi_orbit_theorem_closed": bool(
            equality_scope.get("corrected_signed_Phi_orbit_theorem_proved")
        ),
        "SU5_Delta_SU4_Phi_slice_classified": phi_orbit_scope.get(
            "complete_SU4_invariant_slice_classified"
        ),
        "SU5_Delta_signed_Phi_local_components_closed": (
            su5_phi_local_components_closed
        ),
        "SU5_Delta_distant_Phi_components_excluded": equality_scope.get(
            "distant_disconnected_Phi_components_excluded"
        ),
        "SU5_Delta_Phi_SU3_fixed_slice_closed": su5_phi_su3_slice_closed,
        "SU5_Delta_Phi_SU3_fixed_slice_dimension": 16
        if su5_phi_su3_slice_closed
        else None,
        "SU5_Delta_fixed_F_Sigma_one_orbit_exact": equality_scope.get(
            "fixed_F_Sigma_global_equality_classified"
        ),
        "SU5_Delta_diagonal_Phi_slice_one_orbit_exact": equality_scope.get(
            "fixed_Delta_diagonal_Phi_global_equality_classified"
        ),
        "SU5_Delta_global_Phi_orbit_lemma_open": not bool(
            equality_lemma.get("proved")
        ),
        "SU5_Delta_global_Phi_orbit_lemma_closed": bool(
            equality_lemma.get("proved")
        ),
        "SU5_Delta_global_Phi_orbit_theorem_core_sha256": equality_global.get(
            "core_sha256"
        ),
        "SU5_Delta_global_Phi_orbit_external_dependency": equality_global.get(
            "external_theorem_dependency", {}
        ).get("theorem"),
        "SU5_Delta_global_Phi_orbit_lemma": equality_lemma.get("statement"),
        "SU5_Delta_chiral_global_gap_honestly_reduced": (
            su5_chiral_gap_honestly_reduced
        ),
        "SU5_Delta_chiral_lower_witness_found": gap_flags.get(
            "lower_witness_found"
        ),
        "SU5_Delta_chiral_small_beta_route_exists": gap_flags.get(
            "conditional_small_positive_beta_route_exists"
        ),
        "SU5_Delta_chiral_beta_1_over_20_global_certified": gap_flags.get(
            "beta_1_over_20_global_minimum_certified"
        ),
        "SU5_Delta_chiral_final_acceptance_test_passes": gap_acceptance.get(
            "currently_passes"
        ),
        "SU5_fixed_F_full_offkernel_gap_closed": su5_fixed_f_full_gap_closed,
        "SU5_fixed_F_gap_equality_is_selected_flag": fixed_f_offkernel_scope.get(
            "equality_is_selected_SU5_flag_orbit"
        ),
        "SU5_arbitrary_Phi_offstratum_gap_open": not bool(
            fixed_f_offkernel_scope.get("arbitrary_Phi_proved")
        ),
        "SU5_max_negative_all_zero_residual_route_excluded": (
            su5_max_negative_all_zero_route_excluded
        ),
        "SU5_max_negative_all_zero_residual_strict_margin": (
            su5_max_negative_zero_residual_report.get("exact_stratum_gap", {}).get(
                "strict_margin"
            )
        ),
        "SU5_max_negative_pure_Delta_full_residual_gap_closed": (
            su5_max_negative_full_residual_pure_delta_closed
        ),
        "SU5_max_negative_pure_Delta_full_residual_minimum": (
            max_negative_full_scope.get("restricted_gap_global_minimum")
        ),
        "SU5_max_negative_rank1_SU3_four_dimensional_slice_closed": (
            su5_max_negative_rank1_su3_slice_closed
        ),
        "SU5_max_negative_rank1_SU3_slice_dimension": rank1_su3_scope.get(
            "Phi_slice_real_dimension"
        ),
        "SU5_max_negative_rank1_SU3_ambient_dimension": rank1_su3_scope.get(
            "full_SU3_fixed_space_real_dimension"
        ),
        "SU5_max_negative_rank1_SU3_slice_minimum": (
            su5_max_negative_rank1_su3_slice_report.get("radial_patch", {}).get(
                "restricted_global_minimum"
            )
        ),
        "SU5_max_negative_arbitrary_rank1_Phi_open": not bool(
            rank1_su3_checks.get("arbitrary_rank1_Phi_proved")
        ),
        "rank1_SU4_stabilizer_infrastructure_exact": (
            rank1_su4_stabilizer_infrastructure_exact
        ),
        "rank1_SU4_joint_stabilizer_dimension": (
            rank1_su4_stabilizer_report.get("joint_stabilizer_tangent", {}).get(
                "exact_tangent_nullity"
            )
        ),
        "rank1_SU4_Phi210_intertwiner_infrastructure_exact": (
            rank1_su4_phi210_intertwiners_exact
        ),
        "rank1_SU4_Phi210_carrier_count": (
            rank1_su4_phi210_intertwiners_report.get("carriers", {}).get(
                "carrier_count"
            )
        ),
        "rank1_SU4_Sym2_invariant_dimension": (
            rank1_su4_phi210_intertwiners_report.get("carriers", {}).get(
                "Sym2_Phi210_SU4_singlet_dimension"
            )
        ),
        "rank1_SU4_aligned_carriers_exact": rank1_su4_aligned_carriers_exact,
        "rank1_SU4_aligned_direct_sum_rank": (
            rank1_su4_aligned_carriers_report.get("alignment", {}).get(
                "concatenated_aligned_basis_rank_mod_prime"
            )
        ),
        "rank1_SU4_physical_real_maps_exact": bool(
            rank1_su4_aligned_scope.get(
                "physical_real_structure_and_Gaussian_embeddings_constructed"
            )
            is True
        ),
        "rank1_SU4_Phi210_quadratic_basis_exact": (
            rank1_su4_phi210_quadratic_basis_exact
        ),
        "rank1_SU4_quadratic_constraint_shape": (
            rank1_su4_phi210_quadratic_basis_report.get(
                "constraint_system", {}
            ).get("reduced_constraint_shape")
        ),
        "rank1_SU4_quadratic_constraint_rank": (
            rank1_su4_phi210_quadratic_basis_report.get(
                "constraint_system", {}
            ).get("exact_rational_rank")
        ),
        "rank1_SU4_quadratic_constraint_nullity": (
            rank1_su4_phi210_quadratic_basis_report.get(
                "constraint_system", {}
            ).get("exact_rational_nullity")
        ),
        "rank1_SU4_quadratic_basis_count": (
            rank1_su4_phi210_quadratic_basis_report.get(
                "quadratic_basis", {}
            ).get("matrix_count")
        ),
        "rank1_SU4_quadratic_basis_rank": (
            rank1_su4_phi210_quadratic_basis_report.get(
                "quadratic_basis", {}
            ).get("upper_triangle_column_rank_mod_prime")
        ),
        "rank1_SU4_quadratic_live_invariance_exact": (
            rank1_su4_phi210_quadratic_basis_report.get(
                "quadratic_basis", {}
            ).get("all_45_commute_with_all_15_live_Phi210_generators_exact")
        ),
        "rank1_SU4_Schur_SOS_SDP_open": (
            rank1_su4_quadratic_scope.get(
                "augmented_homogeneous_Schur_SOS_SDP_constructed"
            )
            is False
        ),
        "rank1_SU4_arbitrary_Phi_bound_open": (
            rank1_su4_quadratic_scope.get("arbitrary_rank1_Phi_proved")
            is False
        ),
        "rank1_SU4_augmented_SOS_census_exact": (
            rank1_su4_augmented_sos_census_exact
        ),
        "rank1_SU4_augmented_homogeneous_dimension": (
            rank1_su4_augmented_sos_census_report.get(
                "augmented_representation", {}
            ).get("augmented_homogeneous_dimension")
        ),
        "rank1_SU4_augmented_complex_isotypic_type_count": (
            rank1_su4_augmented_sos_census_report.get(
                "augmented_representation", {}
            ).get("complex_isotypic_type_count")
        ),
        "rank1_SU4_augmented_complex_irreducible_copy_count": (
            rank1_su4_augmented_sos_census_report.get(
                "augmented_representation", {}
            ).get("complex_irreducible_copy_count")
        ),
        "rank1_SU4_augmented_real_isotypic_block_count": (
            rank1_su4_augmented_sos_census_report.get(
                "augmented_representation", {}
            ).get("real_isotypic_block_count")
        ),
        "rank1_SU4_augmented_real_symmetric_block_count": (
            rank1_su4_augmented_sos_census_report.get(
                "augmented_representation", {}
            ).get("real_symmetric_block_count")
        ),
        "rank1_SU4_augmented_complex_Hermitian_block_count": (
            rank1_su4_augmented_sos_census_report.get(
                "augmented_representation", {}
            ).get("complex_Hermitian_block_count")
        ),
        "rank1_SU4_augmented_Schur_real_parameter_count": (
            rank1_su4_augmented_sos_census_report.get(
                "augmented_representation", {}
            ).get("Schur_real_parameter_count")
        ),
        "rank1_SU4_augmented_invariant_equation_count": (
            rank1_su4_augmented_sos_census_report.get(
                "invariant_quartic_target", {}
            ).get("invariant_equation_count")
        ),
        "rank1_SU4_augmented_abstract_total_rank": (
            rank1_su4_augmented_sos_census_report.get(
                "abstract_coefficient_map_census", {}
            ).get("abstract_total_rank_exact")
        ),
        "rank1_SU4_augmented_abstract_total_kernel_dimension": (
            rank1_su4_augmented_sos_census_report.get(
                "abstract_coefficient_map_census", {}
            ).get("abstract_total_kernel_dimension_exact")
        ),
        "rank1_SU4_augmented_coordinate_Schur_map_open": (
            rank1_su4_census_scope.get(
                "Schur_coordinate_6585_by_19594_coefficient_matrix_constructed"
            ) is False
        ),
        "rank1_SU4_augmented_isotypic_maps_open": (
            rank1_su4_census_scope.get(
                "all_35_isotypic_type_maps_spanning_824_irreducible_copies_constructed"
            ) is False
        ),
        "rank1_SU4_augmented_physical_target_open": (
            rank1_su4_census_scope.get(
                "physical_G3_gap_target_vector_constructed"
            ) is False
            and rank1_su4_census_scope.get(
                "physical_G3_gap_cubic_zero_RHS_certified"
            ) is False
        ),
        "rank1_SU4_augmented_Schur_SOS_SDP_open": (
            rank1_su4_census_scope.get("augmented_Schur_SOS_SDP_constructed")
            is False
            and rank1_su4_census_scope.get(
                "augmented_Schur_SOS_SDP_feasibility_certified"
            ) is False
            and rank1_su4_census_scope.get(
                "augmented_Schur_SOS_SDP_infeasibility_certified"
            ) is False
        ),
        "rank1_SU4_augmented_arbitrary_Phi_bound_open": (
            rank1_su4_census_scope.get("arbitrary_real_Phi_lower_bound_proved")
            is False
            and rank1_su4_census_scope.get("arbitrary_rank1_Phi_proved")
            is False
        ),
        "rank1_SU4_augmented_cubic_map_exact": (
            rank1_su4_augmented_sos_cubic_map_exact
        ),
        "rank1_SU4_augmented_cubic_carrier_copy_count": (
            rank1_su4_augmented_sos_cubic_map_report.get(
                "Sym2_target_carriers", {}
            ).get("total_complex_carrier_copy_count")
        ),
        "rank1_SU4_augmented_cubic_real_variable_count": (
            rank1_su4_augmented_sos_cubic_map_report.get(
                "physical_cubic_domain", {}
            ).get("physical_basis_count")
        ),
        "rank1_SU4_augmented_cubic_coordinate_map_shape": (
            rank1_su4_augmented_sos_cubic_map_report.get(
                "cubic_coordinate_map", {}
            ).get("coordinate_map_shape")
        ),
        "rank1_SU4_augmented_cubic_coordinate_map_nnz": (
            rank1_su4_augmented_sos_cubic_map_report.get(
                "cubic_coordinate_map", {}
            ).get("coordinate_map_nnz")
        ),
        "rank1_SU4_augmented_cubic_coordinate_map_rank": (
            rank1_su4_augmented_sos_cubic_map_report.get(
                "cubic_coordinate_map", {}
            ).get("exact_rank")
        ),
        "rank1_SU4_augmented_cubic_coordinate_map_kernel_dimension": (
            rank1_su4_augmented_sos_cubic_map_report.get(
                "cubic_coordinate_map", {}
            ).get("exact_kernel_dimension")
        ),
        "rank1_SU4_augmented_cubic_zero_placeholder_nonphysical": (
            rank1_su4_augmented_sos_cubic_map_report.get(
                "cubic_coordinate_map", {}
            ).get("abstract_zero_placeholder_is_not_a_physical_G3_target")
            is True
            and rank1_su4_augmented_sos_cubic_map_report.get(
                "cubic_coordinate_map", {}
            ).get("physical_G3_gap_target_vector_constructed") is False
            and rank1_su4_augmented_sos_cubic_map_report.get(
                "cubic_coordinate_map", {}
            ).get("physical_G3_gap_cubic_zero_RHS_certified") is False
        ),
        "rank1_SU4_augmented_cubic_other_graded_maps_open": all(
            rank1_su4_cubic_scope.get(name) is False
            for name in (
                "degree_zero_coefficient_map_constructed",
                "degree_one_coefficient_map_constructed",
                "degree_two_coefficient_map_constructed",
                "degree_four_coefficient_map_constructed",
            )
        ),
        "rank1_SU4_augmented_cubic_full_coordinate_map_open": (
            rank1_su4_cubic_scope.get(
                "full_6585_by_19594_Schur_coordinate_matrix_constructed"
            ) is False
        ),
        "rank1_SU4_augmented_cubic_physical_target_open": (
            rank1_su4_cubic_scope.get(
                "physical_G3_gap_target_vector_constructed"
            ) is False
            and rank1_su4_cubic_scope.get(
                "physical_G3_gap_cubic_zero_RHS_certified"
            ) is False
        ),
        "rank1_SU4_augmented_cubic_Schur_SOS_SDP_open": all(
            rank1_su4_cubic_scope.get(name) is False
            for name in (
                "augmented_Schur_SOS_SDP_constructed",
                "augmented_Schur_SOS_SDP_feasibility_certified",
                "augmented_Schur_SOS_SDP_infeasibility_certified",
            )
        ),
        "rank1_SU4_augmented_cubic_arbitrary_Phi_bound_open": (
            rank1_su4_cubic_scope.get("arbitrary_real_Phi_lower_bound_proved")
            is False
            and rank1_su4_cubic_scope.get("arbitrary_rank1_Phi_proved")
            is False
        ),
        "rank1_SU4_augmented_cubic_G3_open": (
            rank1_su4_cubic_scope.get("G3_closed") is False
            and rank1_su4_cubic_scope.get("whole_model_validated") is False
            and rank1_su4_cubic_scope.get("whole_model_excluded") is False
        ),
        "rank1_SU4_augmented_quartic_map_exact": (
            rank1_su4_augmented_sos_quartic_map_exact
        ),
        "rank1_SU4_augmented_quartic_carrier_family_count": (
            rank1_su4_augmented_sos_quartic_map_report.get(
                "dimensions", {}
            ).get("complex_isotypic_types")
        ),
        "rank1_SU4_augmented_quartic_irreducible_copy_count": (
            rank1_su4_augmented_sos_quartic_map_report.get(
                "dimensions", {}
            ).get("irreducible_copies")
        ),
        "rank1_SU4_augmented_quartic_real_block_count": (
            rank1_su4_augmented_sos_quartic_map_report.get(
                "dimensions", {}
            ).get("real_Schur_blocks")
        ),
        "rank1_SU4_augmented_quartic_coordinate_map_shape": (
            rank1_su4_quartic_map.get("shape")
        ),
        "rank1_SU4_augmented_quartic_coordinate_map_nnz": (
            rank1_su4_quartic_map.get("nnz")
        ),
        "rank1_SU4_augmented_quartic_coordinate_map_rank": (
            rank1_su4_quartic_map.get("rank_over_Q_exact")
        ),
        "rank1_SU4_augmented_quartic_coordinate_map_kernel_dimension": (
            rank1_su4_quartic_map.get("kernel_dimension_over_Q_exact")
        ),
        "rank1_SU4_augmented_quartic_physical_target_open": (
            rank1_su4_quartic_scope.get("physical_quartic_target_constructed")
            is False
        ),
        "rank1_SU4_augmented_quartic_standard_PSD_congruences_open": (
            rank1_su4_quartic_scope.get(
                "standard_PSD_congruences_for_real_type_fixed_bases_constructed"
            ) is False
        ),
        "rank1_SU4_augmented_quartic_SDP_open": (
            rank1_su4_quartic_scope.get("semidefinite_feasibility_solved")
            is False
        ),
        "rank1_SU4_augmented_quartic_arbitrary_Phi_bound_open": (
            rank1_su4_quartic_scope.get(
                "arbitrary_Phi_stationarity_or_lower_bound_proved"
            ) is False
        ),
        "rank1_SU4_augmented_quartic_G3_open": (
            rank1_su4_quartic_scope.get("G3_closed") is False
        ),
        "rank1_SU4_legacy_v20_PSD_routes_and_stale_payload_well_formed": (
            rank1_su4_legacy_psd_routes_and_stale_payload_well_formed
        ),
        "rank1_SU4_legacy_v20_physical_target_valid": False,
        "rank1_SU4_legacy_v20_primal_valid": False,
        "rank1_SU4_augmented_standard_PSD_route_count": (
            rank1_su4_psd_routes.get("real_type_block_count", 0)
            + rank1_su4_psd_routes.get("complex_Hermitian_block_count", 0)
        ),
        "rank1_SU4_augmented_standard_PSD_parameter_count": (
            rank1_su4_psd_routes.get("standard_total_parameter_count")
        ),
        "rank1_SU4_augmented_real_type_PSD_congruences_exact": (
            rank1_su4_psd_target_scope.get(
                "all_nine_real_type_standard_PSD_congruences_constructed"
            ) is True
        ),
        "rank1_SU4_augmented_complex_Hermitian_coordinates_exact": (
            rank1_su4_psd_target_scope.get(
                "all_thirteen_complex_blocks_in_standard_Hermitian_coordinates"
            ) is True
        ),
        "rank1_SU4_corrected_fixed_endpoint_theorem_exact": (
            rank1_su4_corrected_exact
        ),
        "rank1_SU4_corrected_publication_manifest_sha256": (
            rank1_su4_corrected_view.get("publication_manifest_raw_sha256")
        ),
        "rank1_SU4_corrected_positive_Gram_map_shape": (
            rank1_su4_corrected_view.get("map_shape")
        ),
        "rank1_SU4_corrected_positive_Gram_map_common_denominator": (
            rank1_su4_corrected_view.get("map_common_denominator")
        ),
        "rank1_SU4_corrected_positive_Gram_map_nnz": (
            rank1_su4_corrected_view.get("map_nnz")
        ),
        "rank1_SU4_corrected_positive_Gram_map_sha256": (
            rank1_su4_corrected_view.get("map_numerator_csr_sha256")
        ),
        "rank1_SU4_corrected_physical_target_common_denominator": (
            rank1_su4_corrected_view.get("target_common_denominator")
        ),
        "rank1_SU4_corrected_physical_target_nonzero_count": (
            rank1_su4_corrected_view.get("target_nonzero_count")
        ),
        "rank1_SU4_corrected_physical_target_sha256": (
            rank1_su4_corrected_view.get("target_numerator_sha256")
        ),
        "rank1_SU4_corrected_exact_coefficient_equalities": (
            rank1_su4_corrected_view.get("exact_coefficient_equalities")
        ),
        "rank1_SU4_corrected_strict_positive_Gram_blocks": (
            rank1_su4_corrected_view.get("strict_positive_Gram_blocks")
        ),
        "rank1_SU4_corrected_strict_positive_LDL_pivots": (
            rank1_su4_corrected_view.get("strict_positive_LDL_pivots")
        ),
        "rank1_SU4_corrected_arbitrary_real_Phi_at_fixed_endpoint": (
            rank1_su4_corrected_view.get(
                "arbitrary_real_Phi_at_fixed_endpoint"
            )
        ),
        "rank1_SU4_corrected_strict_positive_off_homogeneous_origin": (
            rank1_su4_corrected_view.get(
                "strict_positive_off_homogeneous_origin"
            )
        ),
        "rank1_SU4_corrected_A_greater_than_3_over_200_at_t1": (
            rank1_su4_corrected_view.get("A_greater_than_3_over_200_at_t1")
        ),
        "rank1_SU4_corrected_p_zero_set_at_t1_empty": (
            rank1_su4_corrected_view.get("p_zero_set_at_t1_empty")
        ),
        "rank1_SU4_corrected_global_Sigma_proved": (
            rank1_su4_corrected_view.get("global_Sigma_proved")
        ),
        "rank1_SU4_corrected_general_H_proved": (
            rank1_su4_corrected_view.get("general_H_proved")
        ),
        "rank1_SU4_corrected_full_H_proved": (
            rank1_su4_corrected_view.get("full_H_proved")
        ),
        "rank1_SU4_corrected_full_Hessian_proved": (
            rank1_su4_corrected_view.get("full_Hessian_proved")
        ),
        "rank1_SU4_corrected_G3_closed": (
            rank1_su4_corrected_view.get("G3_closed")
        ),
        "SU5_max_negative_arbitrary_Sigma_orientation_open": not bool(
            rank1_su3_scope.get("arbitrary_max_negative_Sigma")
        ),
        "SU5_arbitrary_Phi_nonzero_residual_cancellations_open": not bool(
            max_negative_full_scope.get("nonzero_Phi_Sigma_residuals_covered")
            and max_negative_full_scope.get(
                "nonzero_chiral_Phi_H_residual_covered"
            )
        ),
        "SU5_arbitrary_non_pure_Delta_Sigma_uniform_coercivity_open": not bool(
            max_negative_full_scope.get("arbitrary_Sigma_orientation_proved")
        ),
        "SU5_arbitrary_Phi_uniform_coercivity_open": not bool(
            max_negative_full_scope.get("arbitrary_Sigma_orientation_proved")
        ),
        "alternative_global_SOS_audit_honestly_open": (
            alternative_global_sos_honestly_open
        ),
        "all_vanishing_global_SOS_replacements_excluded": bool(
            alternative_flags.get(
                "all_vanishing_45_current_Gram_completion_excluded"
            )
            and alternative_flags.get(
                "all_vanishing_affine_SOS_completion_excluded"
            )
            and alternative_flags.get(
                "all_vanishing_unique_chiral_quartic_completion_excluded"
            )
        ),
        "nonvanishing_residual_global_SOS_replacements_excluded": (
            alternative_flags.get(
                "nonvanishing_residual_gradient_cancellation_excluded"
            )
        ),
        "candidate_nonzero_real_parameters": coefficients.get("nonzero_count"),
        "candidate_real_parameter_count": 51,
        "candidate_maximum_absolute_coefficient": coefficients.get(
            "maximum_absolute_coefficient"
        ),
        "candidate_J0": symbolic.get(
            "lambda::O48_B01_Phi_self_quartics"
        ),
        "exact_PD_rank": pd_core.get("rank"),
        "exact_PD_nullity": pd_core.get("nullity"),
        "exact_full_Hessian_rank": pd_extension.get(
            "exact_full_Hessian_rank"
        ),
        "direct_exact_PD_source_binding": pd_flags.get(
            "direct_exact_source_binding"
        ),
        "complete_potential_BFB_exactly_certified": sos_flags.get(
            "complete_potential_BFB_exactly_certified"
        ),
        "strict_local_minimum_certified": sos_flags.get(
            "strict_local_minimum_certified"
        ),
        "selected_vacuum_stationarity_exactly_certified": sos_flags.get(
            "selected_vacuum_stationarity_exactly_compiler_certified"
        ),
        "global_minimum_certified": sos_flags.get(
            "selected_vacuum_global_minimum_certified"
        ),
        "selected_global_minimum_disproved": sos_flags.get(
            "selected_vacuum_global_minimum_disproved"
        ),
        "exact_lower_energy_field_witness_certified": sos_flags.get(
            "exact_lower_energy_field_witness_certified"
        ),
        "constructive_candidate_rejected_for_G3": sos_flags.get(
            "constructive_candidate_rejected_for_G3"
        ),
        "global_uniqueness_certified": sos_flags.get(
            "selected_vacuum_unique_modulo_symmetry"
        ),
        "G3_closed": sos_flags.get("G3_closed"),
        "whole_model_validated": sos_flags.get("whole_model_validated"),
        "whole_model_excluded": sos_flags.get("whole_model_excluded"),
        "remaining_exact_step": pd_report.get("next_exact_step"),
    }


def _gauged_u1x_scalar_subtheorems(
    g1_report: dict[str, Any],
    g1_component_tensor_closure: dict[str, Any],
    g2_report: dict[str, Any],
    *,
    contract_consistent: bool,
) -> dict[str, Any]:
    """Expose completed scalar calculations without closing whole-model gates."""
    g1_closure = g1_report.get("closure", {})
    g1_flags = g1_report.get("flags", {})
    g1_multiplicity_census_complete = bool(
        g1_report.get("n_failed") == 0
        and g1_closure.get(
            "declared_symmetry_charge_multidegrees_degree_le_4_closed"
        )
        is True
        and g1_closure.get("so10_singlet_multiplicities_degree_le_4_closed")
        is True
        and g1_closure.get("gauged_u1x_44_direction_subcensus_closed") is True
        and g1_flags.get("renormalizable_G1_multiplicity_census_closed") is True
    )
    g1_component_tensors_complete = bool(
        g1_component_tensor_closure.get("source_bound") is True
        and g1_component_tensor_closure.get(
            "mathematical_G1_closed_for_renormalizable_model"
        )
        is True
        and g1_component_tensor_closure.get("model_contract_id")
        == AUTHORITATIVE_CONTRACT_ID
        and g1_component_tensor_closure.get("direction_map_sha256")
        == RENORMALIZABLE_G1_DIRECTION_MAP_SHA256
    )
    full_g1_closed = bool(
        g1_multiplicity_census_complete
        and g1_component_tensors_complete
    )
    g2_scoped_audit_complete = bool(
        g2_report.get("n_failed") == 0
        and g2_report.get("flags", {}).get("G2_gauged_u1x_derivatives_certified")
        is True
    )
    stationary = g2_report["stationary_Hessian_bridge"][
        "promoted_stationarity_matrix"
    ]
    return {
        "model_contract_id": AUTHORITATIVE_CONTRACT_ID,
        "scope": (
            "exact-X-neutral renormalizable scalar potential on the canonical "
            "486-real field chart"
        ),
        "whole_model_gate_closure": False,
        "promoted_to_authoritative_G1_G2": bool(
            contract_consistent and full_g1_closed and g2_scoped_audit_complete
        ),
        "blocked_only_from_promotion_by_model_contract_mismatch": (
            not contract_consistent and full_g1_closed
        ),
        "renormalizable_G1_component_tensor_closure": (
            g1_component_tensor_closure
        ),
        "G1": {
            "scoped_status": (
                "COMPLETE_GAUGED_U1X_MULTIPLICITY_CENSUS__FULL_G1_OPEN"
                if g1_multiplicity_census_complete and not full_g1_closed
                else "COMPLETE_GAUGED_U1X_FULL_COMPONENT_TENSOR_INTEGRATION"
                if full_g1_closed
                else "GAUGED_U1X_MULTIPLICITY_CENSUS_INCOMPLETE"
            ),
            "multiplicity_census_complete": g1_multiplicity_census_complete,
            "explicit_component_tensor_subset_integration_complete": (
                g1_component_tensors_complete
            ),
            "mathematical_component_tensor_closure_complete": (
                g1_component_tensors_complete
            ),
            "character_census_remains_multiplicity_only": bool(
                g1_closure.get("explicit_component_tensor_subset_integration_closed")
                is False
                and g1_flags.get("g1_explicit_tensor_subset_reaudit_open") is True
                and g1_flags.get("g1_closed") is False
            ),
            "full_G1_closed": full_g1_closed,
            "full_renormalizable_G1_mathematical_ring_closed": full_g1_closed,
            "authoritative_G1_promoted_closed": bool(
                contract_consistent and full_g1_closed
            ),
            "release_G1_verified": bool(contract_consistent and full_g1_closed),
            "remaining_exact_target": (
                "Supply the hash-bound external SARAH v2 execution attestation."
                if full_g1_closed
                else "Restore the source-bound 44-direction component-tensor theorem."
            ),
            "hermitian_conjugacy_orbits": g1_report["counts"][
                "hermitian_conjugacy_orbits"
            ],
            "invariant_directions": g1_report["counts"][
                "total_potential_orbit_multiplicity"
            ],
            "real_potential_parameters": g1_report["counts"][
                "total_real_potential_parameters"
            ],
        },
        "G2": {
            "scoped_status": "COMPLETE_GAUGED_U1X_DENSE_DERIVATIVE_AUDIT",
            "scoped_derivative_audit_complete": g2_scoped_audit_complete,
            "authoritative_promotion_blocked_on_full_G1": not full_g1_closed,
            "authoritative_promotion_blocked_on_model_contract": (
                not contract_consistent
            ),
            "authoritative_promotion_ready_after_model_contract": bool(
                full_g1_closed and g2_scoped_audit_complete
            ),
            "invariant_directions": g2_report["counts"]["invariant_directions"],
            "real_potential_parameters": g2_report["counts"]["real_parameters"],
            "real_field_dimension": g2_report["counts"]["real_field_dimension"],
            "gradient_entries_per_parameter": g2_report["counts"][
                "gradient_entries_per_parameter"
            ],
            "dense_Hessian_shape": g2_report["counts"][
                "Hessian_shape_per_parameter"
            ],
            "promoted_stationarity_rank": stationary["rank"],
            "promoted_stationarity_nullity": stationary["nullity"],
            "raw_dense_rank_14_certified": g2_report["flags"][
                "raw_dense_rank_14_is_certified"
            ],
            "exact_Delta_R_projector_zero_certificate": g2_report["flags"][
                "exact_Delta_R_projector_zero_certificate"
            ],
            "exact_projector_zero_corrected_normalized_SVD_rank_13": g2_report["flags"][
                "exact_projector_zero_corrected_normalized_SVD_rank_13"
            ],
            "stationarity_rank_13_exactly_certified": g2_report["flags"][
                "stationarity_rank_13_exactly_certified"
            ],
            "stationarity_nullity_38_exactly_certified": g2_report["flags"][
                "stationarity_nullity_38_exactly_certified"
            ],
            "G3_closed": g2_report["flags"]["G3_closed"],
        },
    }


def _expected_gate_statuses(
    contract_consistent: bool,
    *,
    g1_full_component_tensors_closed: bool = False,
    g2_scoped_derivatives_complete: bool = True,
) -> dict[str, str]:
    """Return the next scientifically honest frontier for the contract state."""
    if not contract_consistent:
        return {f"G{i}": STATUS_BLOCKED for i in range(1, 9)}
    g1_status = (
        STATUS_CLOSED if g1_full_component_tensors_closed else STATUS_OPEN
    )
    g2_status = (
        STATUS_CLOSED
        if g1_status == STATUS_CLOSED and g2_scoped_derivatives_complete
        else STATUS_OPEN
        if g1_status == STATUS_CLOSED
        else STATUS_BLOCKED
    )
    return {
        "G1": g1_status,
        "G2": g2_status,
        "G3": STATUS_OPEN if g2_status == STATUS_CLOSED else STATUS_BLOCKED,
        "G4": STATUS_BLOCKED,
        "G5": (
            STATUS_CLOSED
            if g1_status == STATUS_CLOSED and g2_status == STATUS_CLOSED
            else STATUS_BLOCKED
        ),
        "G6": STATUS_BLOCKED,
        "G7": STATUS_BLOCKED,
        "G8": STATUS_BLOCKED,
    }


def _build_gates(
    *,
    contract_consistent: bool,
    contract_blocker: str = CONTRACT_BLOCKER,
    scoped: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    specifications = {
        "G1": (
            "Invariant ring and component Clebsch tensors",
            [
                "complete and source-bind the explicit component-tensor/Clebsch integration for the exact 44-direction/51-parameter multiplicity census",
            ],
        ),
        "G2": (
            "Fully projected non-SUSY component potential",
            [
                "promote the completed 44/51/486 dense derivative and Ward-identity audit only after full G1 component-tensor integration and executable-contract repair",
            ],
        ),
        "G3": (
            "Stationarity and global vacuum",
            [
                "classify every competing stationary symmetry orbit and compare exact potential values",
                "prove global minimality and uniqueness, or exhibit a lower competing extremum",
            ],
        ),
        "G4": (
            "Gauge quotient, axion directions, and physical Hessian",
            [
                "carry the exact rank-37 gauge quotient (449, axion included) and rank-38 massive/transverse quotient (448) to an accepted G3 witness, recomputing if its stabilizer changes",
                "classify all remaining Hessian zero and negative modes at that witness",
            ],
        ),
        "G5": (
            "Boundedness from below",
            [
                "promote the completed source-bound SOS/BFB certificate after repairing the executable model contract"
            ],
        ),
        "G6": (
            "Physical threshold spectrum",
            ["await authoritative G3/G4/G5 and emit the complete positive spectrum"],
        ),
        "G7": (
            "Validated two-loop RGE and threshold matching",
            ["await G6 and independently validate the full beta system"],
        ),
        "G8": (
            "Proton-decay prediction and falsification",
            ["await authoritative G3/G6/G7 before any unique lifetime claim"],
        ),
    }
    g1_full_component_tensors_closed = bool(
        scoped and scoped["G1"]["full_G1_closed"] is True
    )
    g2_scoped_derivatives_complete = bool(
        scoped and scoped["G2"]["scoped_derivative_audit_complete"] is True
    )
    statuses = _expected_gate_statuses(
        contract_consistent,
        g1_full_component_tensors_closed=g1_full_component_tensors_closed,
        g2_scoped_derivatives_complete=g2_scoped_derivatives_complete,
    )
    gates: dict[str, dict[str, Any]] = {}
    for name, (title, open_scope) in specifications.items():
        status = statuses[name]
        unsatisfied = [
            dependency
            for dependency in DEPENDENCIES[name]
            if (
                dependency == "MODEL_CONTRACT" and not contract_consistent
            ) or (
                dependency != "MODEL_CONTRACT"
                and statuses.get(dependency) != STATUS_CLOSED
            )
        ]
        if status == STATUS_BLOCKED:
            blocking_root = (
                contract_blocker
                if not contract_consistent
                else "DEPENDENCY_NOT_CLOSED"
            )
        else:
            blocking_root = None
        gates[name] = {
            "status": status,
            "authoritative_model_contract_id": AUTHORITATIVE_CONTRACT_ID,
            "blocking_root": blocking_root,
            "unsatisfied_dependencies": unsatisfied,
            "closed_on_current_authoritative_contract": status == STATUS_CLOSED,
            "closure_route_defined": True,
            "title": title,
            "dependencies": list(DEPENDENCIES[name]),
            "authoritative_closed_scope": (
                [
                    "promoted exact-X multiplicity census and explicit component Clebsch tensors"
                    if name == "G1"
                    else (
                        "promoted exact-X dense derivative and Ward audit"
                        if name == "G2"
                        else "source-bound complete-potential SOS/BFB certificate"
                    )
                ]
                if status == STATUS_CLOSED
                else []
            ),
            "open_scope": open_scope,
            "historical_option_c_evidence_retained": name in {"G1", "G2", "G3", "G4"},
        }
        if scoped is not None and name in {"G1", "G2"}:
            gates[name]["scoped_calculation_status"] = scoped[name]["scoped_status"]
            gates[name]["scoped_calculation_complete"] = bool(
                scoped[name].get(
                    "multiplicity_census_complete"
                    if name == "G1"
                    else "scoped_derivative_audit_complete"
                )
            )
            gates[name]["full_gate_calculation_complete"] = bool(
                scoped[name].get("full_G1_closed")
                if name == "G1"
                else scoped[name].get("scoped_derivative_audit_complete")
            )
            gates[name]["scoped_calculation_evidence"] = scoped[name]
    return gates


def _build_report_from_inputs(
    *,
    x_report: dict[str, Any],
    g1_report: dict[str, Any],
    g2_report: dict[str, Any],
    filter_report: dict[str, Any],
    g1_component_tensor_report: dict[str, Any] | None = None,
    g1_component_tensor_raw_sha256: str | None = None,
    g1_component_tensor_source_raw_sha256: str | None = None,
    g3_sos_report: dict[str, Any] | None = None,
    g3_pd_report: dict[str, Any] | None = None,
    g3_a_square_report: dict[str, Any] | None = None,
    g3_sos_bfb_report: dict[str, Any] | None = None,
    g3_kernel_bound_report: dict[str, Any] | None = None,
    g3_replacement_report: dict[str, Any] | None = None,
    g3_su5_pd_report: dict[str, Any] | None = None,
    g3_su5_hsx_report: dict[str, Any] | None = None,
    g3_su5_hsx_exact_hessian_report: dict[str, Any] | None = None,
    g3_su5_equality_report: dict[str, Any] | None = None,
    g3_su5_phi_orbit_report: dict[str, Any] | None = None,
    g3_su5_phi_local_component_report: dict[str, Any] | None = None,
    g3_su5_phi_su3_slice_report: dict[str, Any] | None = None,
    g3_su5_gap_report: dict[str, Any] | None = None,
    g3_su5_fixed_f_offkernel_report: dict[str, Any] | None = None,
    g3_su5_max_negative_zero_residual_report: dict[str, Any] | None = None,
    g3_su5_max_negative_full_residual_report: dict[str, Any] | None = None,
    g3_su5_max_negative_rank1_su3_slice_report: dict[str, Any] | None = None,
    g3_rank1_su4_stabilizer_report: dict[str, Any] | None = None,
    g3_rank1_su4_phi210_intertwiners_report: dict[str, Any] | None = None,
    g3_rank1_su4_aligned_carriers_report: dict[str, Any] | None = None,
    g3_rank1_su4_phi210_quadratic_basis_report: dict[str, Any] | None = None,
    g3_rank1_su4_augmented_sos_census_report: dict[str, Any] | None = None,
    g3_rank1_su4_augmented_sos_cubic_map_report: dict[str, Any] | None = None,
    g3_rank1_su4_augmented_sos_quartic_map_report: dict[str, Any] | None = None,
    g3_rank1_su4_augmented_sos_psd_target_report: dict[str, Any] | None = None,
    g3_rank1_su4_corrected_publication: dict[str, Any] | None = None,
    g3_alternative_global_sos_report: dict[str, Any] | None = None,
    final_g3_eft_acceptance_report: dict[str, Any] | None = None,
    final_g3_eft_acceptance_raw_sha256: str | None = None,
    final_g4_eft_mathematical_report: dict[str, Any] | None = None,
    final_g4_eft_mathematical_raw_sha256: str | None = None,
    final_g5_eft_mathematical_report: dict[str, Any] | None = None,
    final_g5_eft_mathematical_raw_sha256: str | None = None,
    final_g6_eft_mathematical_report: dict[str, Any] | None = None,
    final_g6_eft_mathematical_raw_sha256: str | None = None,
    final_g6_eft_gate_source_raw_sha256: str | None = None,
) -> dict[str, Any]:
    """Build a ledger from fresh reports, including repaired-contract states."""
    declared_contract_consistent = bool(x_report["contract_consistent"])
    contract_evidence_complete = _root_contract_evidence_complete(x_report)
    contract_consistent = bool(
        declared_contract_consistent and contract_evidence_complete
    )
    contract_blocker = str(x_report.get("blocker") or CONTRACT_BLOCKER)
    historical = _historical_option_c_subtheorems()
    if g1_component_tensor_report is None:
        g1_component_tensor_report = _load_json_artifact(
            RENORMALIZABLE_G1_COMPONENT_TENSOR_JSON
        )
    if g1_component_tensor_raw_sha256 is None:
        g1_component_tensor_raw_sha256 = _raw_file_sha256(
            RENORMALIZABLE_G1_COMPONENT_TENSOR_JSON
        )
    if g1_component_tensor_source_raw_sha256 is None:
        g1_component_tensor_source_raw_sha256 = _raw_file_sha256(
            RENORMALIZABLE_G1_COMPONENT_TENSOR_SOURCE
        )
    g1_component_tensor_closure = _renormalizable_g1_component_tensor_closure(
        g1_component_tensor_report,
        raw_sha256=g1_component_tensor_raw_sha256,
        source_raw_sha256=g1_component_tensor_source_raw_sha256,
    )
    scoped = _gauged_u1x_scalar_subtheorems(
        g1_report,
        g1_component_tensor_closure,
        g2_report,
        contract_consistent=contract_consistent,
    )
    g1_full_component_tensors_closed = bool(scoped["G1"]["full_G1_closed"])
    g2_scoped_derivatives_complete = bool(
        scoped["G2"]["scoped_derivative_audit_complete"]
    )
    if g3_sos_report is None:
        g3_sos_report = _load_json_artifact(G3_SOS_JSON)
    if g3_pd_report is None:
        g3_pd_report = _load_json_artifact(G3_PD_JSON)
    if g3_a_square_report is None:
        g3_a_square_report = _load_json_artifact(G3_A_SQUARE_JSON)
    if g3_sos_bfb_report is None:
        g3_sos_bfb_report = _load_json_artifact(G3_SOS_BFB_JSON)
    if g3_kernel_bound_report is None:
        g3_kernel_bound_report = _load_json_artifact(G3_KERNEL_BOUND_JSON)
    if g3_replacement_report is None:
        g3_replacement_report = _load_json_artifact(G3_REPLACEMENT_JSON)
    if g3_su5_pd_report is None:
        g3_su5_pd_report = _load_json_artifact(G3_SU5_PD_JSON)
    if g3_su5_hsx_report is None:
        g3_su5_hsx_report = _load_json_artifact(G3_SU5_HSX_JSON)
    if g3_su5_hsx_exact_hessian_report is None:
        g3_su5_hsx_exact_hessian_report = _load_json_artifact(
            G3_SU5_HSX_EXACT_HESSIAN_JSON
        )
    if g3_su5_equality_report is None:
        g3_su5_equality_report = _load_json_artifact(G3_SU5_EQUALITY_JSON)
    if g3_su5_phi_orbit_report is None:
        g3_su5_phi_orbit_report = _load_json_artifact(G3_SU5_PHI_ORBIT_JSON)
    if g3_su5_phi_local_component_report is None:
        g3_su5_phi_local_component_report = _load_json_artifact(
            G3_SU5_PHI_LOCAL_COMPONENT_JSON
        )
    if g3_su5_phi_su3_slice_report is None:
        g3_su5_phi_su3_slice_report = _load_json_artifact(
            G3_SU5_PHI_SU3_SLICE_JSON
        )
    if g3_su5_gap_report is None:
        g3_su5_gap_report = _load_json_artifact(G3_SU5_GAP_JSON)
    if g3_su5_fixed_f_offkernel_report is None:
        g3_su5_fixed_f_offkernel_report = _load_json_artifact(
            G3_SU5_FIXED_F_OFFKERNEL_JSON
        )
    if g3_su5_max_negative_zero_residual_report is None:
        g3_su5_max_negative_zero_residual_report = _load_json_artifact(
            G3_SU5_MAX_NEGATIVE_ZERO_RESIDUAL_JSON
        )
    if g3_su5_max_negative_full_residual_report is None:
        g3_su5_max_negative_full_residual_report = _load_json_artifact(
            G3_SU5_MAX_NEGATIVE_FULL_RESIDUAL_JSON
        )
    if g3_su5_max_negative_rank1_su3_slice_report is None:
        g3_su5_max_negative_rank1_su3_slice_report = _load_json_artifact(
            G3_SU5_MAX_NEGATIVE_RANK1_SU3_SLICE_JSON
        )
    if g3_rank1_su4_stabilizer_report is None:
        g3_rank1_su4_stabilizer_report = _load_json_artifact(
            G3_RANK1_SU4_STABILIZER_JSON
        )
    if g3_rank1_su4_phi210_intertwiners_report is None:
        g3_rank1_su4_phi210_intertwiners_report = _load_json_artifact(
            G3_RANK1_SU4_PHI210_INTERTWINERS_JSON
        )
    if g3_rank1_su4_aligned_carriers_report is None:
        g3_rank1_su4_aligned_carriers_report = _load_json_artifact(
            G3_RANK1_SU4_ALIGNED_CARRIERS_JSON
        )
    if g3_rank1_su4_phi210_quadratic_basis_report is None:
        g3_rank1_su4_phi210_quadratic_basis_report = _load_json_artifact(
            G3_RANK1_SU4_PHI210_QUADRATIC_BASIS_JSON
        )
    if g3_rank1_su4_augmented_sos_census_report is None:
        g3_rank1_su4_augmented_sos_census_report = _load_json_artifact(
            G3_RANK1_SU4_AUGMENTED_SOS_CENSUS_JSON
        )
    if g3_rank1_su4_augmented_sos_cubic_map_report is None:
        g3_rank1_su4_augmented_sos_cubic_map_report = _load_json_artifact(
            G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_JSON
        )
    if g3_rank1_su4_augmented_sos_quartic_map_report is None:
        g3_rank1_su4_augmented_sos_quartic_map_report = _load_json_artifact(
            G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_JSON
        )
    if g3_rank1_su4_augmented_sos_psd_target_report is None:
        g3_rank1_su4_augmented_sos_psd_target_report = _load_json_artifact(
            G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_JSON
        )
    if g3_rank1_su4_corrected_publication is None:
        g3_rank1_su4_corrected_publication = (
            corrected_rank1.load_validated_publication()
        )
    if g3_alternative_global_sos_report is None:
        g3_alternative_global_sos_report = _load_json_artifact(
            G3_ALTERNATIVE_GLOBAL_SOS_JSON
        )
    eft_acceptance_loaded_from_disk = final_g3_eft_acceptance_report is None
    if eft_acceptance_loaded_from_disk:
        final_g3_eft_acceptance_report = _load_json_artifact(
            FINAL_G3_EFT_ACCEPTANCE_JSON
        )
    if final_g3_eft_acceptance_raw_sha256 is None:
        final_g3_eft_acceptance_raw_sha256 = (
            _raw_file_sha256(FINAL_G3_EFT_ACCEPTANCE_JSON)
            if eft_acceptance_loaded_from_disk
            else ""
        )
    parallel_eft_g3_acceptance = _parallel_eft_g3_acceptance(
        final_g3_eft_acceptance_report,
        raw_sha256=final_g3_eft_acceptance_raw_sha256,
    )
    eft_g4_loaded_from_disk = final_g4_eft_mathematical_report is None
    if eft_g4_loaded_from_disk:
        final_g4_eft_mathematical_report = _load_json_artifact(
            FINAL_G4_EFT_MATHEMATICAL_JSON
        )
    if final_g4_eft_mathematical_raw_sha256 is None:
        final_g4_eft_mathematical_raw_sha256 = (
            _raw_file_sha256(FINAL_G4_EFT_MATHEMATICAL_JSON)
            if eft_g4_loaded_from_disk
            else ""
        )
    parallel_eft_g4_mathematical = _parallel_eft_g4_mathematical(
        final_g4_eft_mathematical_report,
        raw_sha256=final_g4_eft_mathematical_raw_sha256,
    )
    eft_g5_loaded_from_disk = final_g5_eft_mathematical_report is None
    if eft_g5_loaded_from_disk:
        final_g5_eft_mathematical_report = _load_json_artifact(
            FINAL_G5_EFT_MATHEMATICAL_JSON
        )
    if final_g5_eft_mathematical_raw_sha256 is None:
        final_g5_eft_mathematical_raw_sha256 = (
            _raw_file_sha256(FINAL_G5_EFT_MATHEMATICAL_JSON)
            if eft_g5_loaded_from_disk
            else ""
        )
    parallel_eft_g5_mathematical = _parallel_eft_g5_mathematical(
        final_g5_eft_mathematical_report,
        raw_sha256=final_g5_eft_mathematical_raw_sha256,
    )
    eft_g6_loaded_from_disk = final_g6_eft_mathematical_report is None
    if eft_g6_loaded_from_disk:
        final_g6_eft_mathematical_report = _load_json_artifact(
            FINAL_G6_EFT_MATHEMATICAL_JSON
        )
    if final_g6_eft_mathematical_raw_sha256 is None:
        final_g6_eft_mathematical_raw_sha256 = (
            _raw_file_sha256(FINAL_G6_EFT_MATHEMATICAL_JSON)
            if eft_g6_loaded_from_disk
            else ""
        )
    if final_g6_eft_gate_source_raw_sha256 is None:
        final_g6_eft_gate_source_raw_sha256 = _raw_file_sha256(
            FINAL_G6_EFT_GATE_SOURCE
        )
    parallel_eft_g6_spectrum = _parallel_eft_g6_spectrum(
        final_g6_eft_mathematical_report,
        raw_sha256=final_g6_eft_mathematical_raw_sha256,
        gate_source_raw_sha256=final_g6_eft_gate_source_raw_sha256,
    )
    g3_frontier = _gauged_u1x_g3_frontier(
        g3_sos_report,
        g3_pd_report,
        g3_a_square_report,
        g3_sos_bfb_report,
        g3_kernel_bound_report,
        g3_replacement_report,
        g3_su5_pd_report,
        g3_su5_hsx_report,
        g3_su5_hsx_exact_hessian_report,
        g3_su5_equality_report,
        g3_su5_phi_orbit_report,
        g3_su5_phi_local_component_report,
        g3_su5_phi_su3_slice_report,
        g3_su5_gap_report,
        g3_su5_fixed_f_offkernel_report,
        g3_su5_max_negative_zero_residual_report,
        g3_su5_max_negative_full_residual_report,
        g3_su5_max_negative_rank1_su3_slice_report,
        g3_rank1_su4_stabilizer_report,
        g3_rank1_su4_phi210_intertwiners_report,
        g3_rank1_su4_aligned_carriers_report,
        g3_rank1_su4_phi210_quadratic_basis_report,
        g3_rank1_su4_augmented_sos_census_report,
        g3_rank1_su4_augmented_sos_cubic_map_report,
        g3_rank1_su4_augmented_sos_quartic_map_report,
        g3_rank1_su4_augmented_sos_psd_target_report,
        g3_rank1_su4_corrected_publication,
        g3_alternative_global_sos_report,
    )
    gates = _build_gates(
        contract_consistent=contract_consistent,
        contract_blocker=contract_blocker,
        scoped=scoped,
    )
    gates["G3"]["constructive_frontier_evidence"] = g3_frontier
    gates["G5"]["constructive_frontier_evidence"] = g3_frontier

    statuses = {name: row["status"] for name, row in gates.items()}
    closed = [name for name, status in statuses.items() if status == STATUS_CLOSED]
    partial = [name for name, status in statuses.items() if status == STATUS_PARTIAL]
    open_gates = [name for name, status in statuses.items() if status == STATUS_OPEN]
    blocked = [name for name, status in statuses.items() if status == STATUS_BLOCKED]

    gauged_counts = g1_report["counts"]
    historical_ids = set(historical["source_contract_ids"].values())
    expected_statuses = _expected_gate_statuses(
        contract_consistent,
        g1_full_component_tensors_closed=g1_full_component_tensors_closed,
        g2_scoped_derivatives_complete=g2_scoped_derivatives_complete,
    )
    contract_state_classified = (
        contract_consistent
        and x_report.get("blocker") is None
        and not x_report.get("scientific_blockers", [])
    ) or (
        not contract_consistent
        and x_report.get("blocker") == contract_blocker
        and contract_blocker in x_report.get("scientific_blockers", [])
    )

    def dependency_closed(dependency: str) -> bool:
        if dependency == "MODEL_CONTRACT":
            return contract_consistent
        return statuses[dependency] == STATUS_CLOSED

    checks = {
        "exact_X_audit_executes": x_report["n_failed"] == 0,
        "parallel_EFT_G3_acceptance_is_source_bound_and_release_open": (
            parallel_eft_g3_acceptance["source_bound"] is True
            and parallel_eft_g3_acceptance[
                "mathematical_G3_closed_for_EFT_model"
            ]
            is True
            and parallel_eft_g3_acceptance[
                "release_G3_verified_for_EFT_model"
            ]
            is False
            and parallel_eft_g3_acceptance[
                "mathematical_G3_closed_for_original_renormalizable_model"
            ]
            is False
            and parallel_eft_g3_acceptance["renormalizable_gate_mutated"]
            is False
            and parallel_eft_g3_acceptance["G4_closed"] is False
        ),
        "parallel_EFT_G4_mathematical_is_source_bound_and_release_open": (
            parallel_eft_g4_mathematical["source_bound"] is True
            and parallel_eft_g4_mathematical[
                "mathematical_G4_closed_for_EFT_model"
            ]
            is True
            and parallel_eft_g4_mathematical[
                "release_G4_verified_for_EFT_model"
            ]
            is False
            and parallel_eft_g4_mathematical[
                "mathematical_G4_closed_for_original_renormalizable_model"
            ]
            is False
            and parallel_eft_g4_mathematical[
                "authoritative_renormalizable_G4_gate_mutated"
            ]
            is False
        ),
        "parallel_EFT_G5_mathematical_is_source_bound_and_release_open": (
            parallel_eft_g5_mathematical["source_bound"] is True
            and parallel_eft_g5_mathematical[
                "mathematical_G5_closed_for_EFT_model"
            ]
            is True
            and parallel_eft_g5_mathematical[
                "release_G5_verified_for_EFT_model"
            ]
            is False
            and parallel_eft_g5_mathematical[
                "authoritative_renormalizable_G5_closed"
            ]
            is False
            and parallel_eft_g5_mathematical[
                "authoritative_renormalizable_G5_mutated"
            ]
            is False
            and parallel_eft_g5_mathematical["new_SOS_claimed"] is False
        ),
        "parallel_EFT_G6_spectrum_is_source_bound_and_release_open": (
            parallel_eft_g6_spectrum["source_bound"] is True
            and parallel_eft_g6_spectrum[
                "mathematical_G6_closed_for_EFT_model"
            ]
            is True
            and parallel_eft_g6_spectrum[
                "release_G6_verified_for_EFT_model"
            ]
            is False
            and parallel_eft_g6_spectrum[
                "authoritative_renormalizable_G6_closed"
            ]
            is False
            and parallel_eft_g6_spectrum["authoritative_G6_gate_mutated"]
            is False
            and parallel_eft_g6_spectrum["whole_model_validated"] is False
        ),
        "parallel_EFT_G4_G5_G6_do_not_promote_authoritative_frontier": (
            statuses == expected_statuses
            and (
                contract_consistent
                or all(
                    statuses[name] == STATUS_BLOCKED
                    for name in ("G3", "G4", "G5", "G6")
                )
            )
        ),
        "consistent_contract_requires_tool_native_bound_evidence": bool(
            not declared_contract_consistent or contract_evidence_complete
        ),
        "legacy_pseudo_sarah_cannot_close_model_contract": bool(
            x_report.get("executable_scaffold_contract", {}).get(
                "model_syntax_class"
            )
            != "legacy_pseudo_sarah_metadata"
            or not contract_consistent
        ),
        "authoritative_contract_state_classified": contract_state_classified,
        "gauged_G1_character_report_executes": g1_report["n_failed"] == 0,
        "gauged_G1_contract_id_is_authoritative": (
            g1_report["model_contract_id"] == AUTHORITATIVE_CONTRACT_ID
        ),
        "gauged_G1_counts_are_28_44_51": (
            gauged_counts["hermitian_conjugacy_orbits"] == 28
            and gauged_counts["total_potential_orbit_multiplicity"] == 44
            and gauged_counts["total_real_potential_parameters"] == 51
        ),
        "gauged_G1_multiplicity_census_is_complete": (
            scoped["G1"]["multiplicity_census_complete"] is True
        ),
        "gauged_G1_component_tensor_theorem_is_source_bound_and_mathematically_closed": (
            g1_component_tensor_closure["source_bound"] is True
            and g1_component_tensor_closure[
                "mathematical_G1_closed_for_renormalizable_model"
            ]
            is True
            and scoped["G1"][
                "explicit_component_tensor_subset_integration_complete"
            ]
            is True
            and scoped["G1"]["full_G1_closed"] is True
        ),
        "gauged_G1_character_census_remains_multiplicity_only": (
            scoped["G1"]["character_census_remains_multiplicity_only"] is True
            and g1_report.get("flags", {}).get(
                "g1_explicit_tensor_subset_reaudit_open"
            )
            is True
            and g1_report.get("flags", {}).get("g1_closed") is False
        ),
        "full_G1_never_closes_without_source_bound_component_tensor_theorem": (
            statuses["G1"] != STATUS_CLOSED
            or (
                contract_consistent
                and g1_component_tensor_closure["source_bound"] is True
                and g1_component_tensor_closure[
                    "mathematical_G1_closed_for_renormalizable_model"
                ]
                is True
                and scoped["G1"][
                    "explicit_component_tensor_subset_integration_complete"
                ]
                is True
                and scoped["G1"]["full_G1_closed"] is True
            )
        ),
        "gauged_scalar_filter_executes": filter_report["n_failed"] == 0,
        "gauged_scalar_filter_enforces_X": filter_report[
            "declared_symmetry_contract"
        ]["continuous_X_imposed"]
        is True,
        "gauged_G2_dense_derivative_audit_passes": (
            g2_report["n_failed"] == 0
            and g2_report["model_contract_id"] == AUTHORITATIVE_CONTRACT_ID
            and g2_report["flags"]["G2_gauged_u1x_derivatives_certified"] is True
        ),
        "gauged_G2_counts_are_44_51_486": (
            g2_report["counts"]["invariant_directions"] == 44
            and g2_report["counts"]["real_parameters"] == 51
            and g2_report["counts"]["real_field_dimension"] == 486
            and g2_report["counts"]["Hessian_shape_per_parameter"] == [486, 486]
        ),
        "gauged_G2_exact_rank_nullity_are_13_38": (
            scoped["G2"]["promoted_stationarity_rank"] == 13
            and scoped["G2"]["promoted_stationarity_nullity"] == 38
            and scoped["G2"]["raw_dense_rank_14_certified"] is False
            and scoped["G2"]["exact_Delta_R_projector_zero_certificate"] is True
            and scoped["G2"][
                "exact_projector_zero_corrected_normalized_SVD_rank_13"
            ] is True
            and scoped["G2"]["stationarity_rank_13_exactly_certified"] is True
            and scoped["G2"]["stationarity_nullity_38_exactly_certified"] is True
        ),
        "gauged_G1_multiplicity_census_and_G2_scoped_audit_are_complete": (
            gates["G1"]["scoped_calculation_complete"] is True
            and gates["G2"]["scoped_calculation_complete"] is True
            and gates["G1"]["full_gate_calculation_complete"]
            == scoped["G1"]["full_G1_closed"]
            and scoped["G2"]["authoritative_promotion_blocked_on_full_G1"]
            == (not scoped["G1"]["full_G1_closed"])
        ),
        "historical_sources_share_scoped_contract": historical_ids
        == {HISTORICAL_CONTRACT_ID},
        "historical_64_91_results_preserved": (
            historical["G1"]["invariant_directions"] == 64
            and historical["G1"]["real_potential_parameters"] == 91
        ),
        "historical_449_saddle_and_search_preserved": (
            historical["G3"]["massive_physical_quotient_dimension"] == 449
            and historical["G3"]["anchored_witness_negative_modes"] == 46
            and historical["G3"]["stability_search_iterations"] == 80
            and historical["G3"]["best_minimum_equilibrated_eigenvalue"]
            == -0.025502339625368114
        ),
        "gauged_G3_required_constructive_artifacts_present": all(
            g3_frontier["artifacts_present"].values()
        ),
        "gauged_G3_exact_A_square_recoupling_source_bound": (
            g3_frontier["exact_A_square_recoupling_source_bound"] is True
        ),
        "gauged_G3_exact_SOS_BFB_stationarity_source_bound": (
            g3_frontier["exact_SOS_BFB_stationarity_source_bound"] is True
        ),
        "gauged_G3_direct_exact_PD_rank_is_honestly_scoped": (
            g3_frontier["direct_exact_PD_rank_honestly_scoped"] is True
        ),
        "gauged_G3_SOS_candidate_exact_local_and_globally_rejected": (
            g3_frontier["SOS_candidate_exact_local_and_globally_rejected"] is True
        ),
        "gauged_G3_failed_branches_and_SU5_PD_frontier_exactly_classified": (
            g3_frontier["fixed_P_branch_exactly_excluded"] is True
            and g3_frontier[
                "lower_replacement_rejected_for_wrong_symmetry"
            ]
            is True
            and g3_frontier["SU5_Delta_PD_exact_global_frontier"] is True
            and g3_frontier["SU5_Delta_PD_full_486_extension_open"] is True
            and g3_frontier[
                "SU5_Delta_PD_disconnected_equality_orbits_open"
            ]
            is False
            and g3_frontier["SU5_Delta_PD_equality_orbits_classified_exactly"]
            is True
        ),
        "gauged_G3_SU5_HSX_extension_is_promising_and_fail_closed": (
            g3_frontier["SU5_Delta_HSX_honest_frontier"] is True
            and g3_frontier["SU5_Delta_HSX_nonzero_real_parameters"] == 28
            and g3_frontier["SU5_Delta_HSX_maximum_absolute_coefficient"] == 11.0
            and g3_frontier["SU5_Delta_HSX_exact_symmetry_ranks"]
            == [36, 37, 38]
            and g3_frontier["SU5_Delta_HSX_transverse_dimension"] == 448
            and g3_frontier["SU5_Delta_HSX_minimum_transverse_eigenvalue_numeric"]
            > 0.0
            and g3_frontier["SU5_Delta_HSX_full_Hessian_proof_grade"] is False
            and g3_frontier["SU5_Delta_HSX_full_quartic_BFB_exact"] is True
            and g3_frontier["SU5_Delta_HSX_finite_field_global_gap_open"] is True
            and g3_frontier[
                "SU5_Delta_HSX_global_equality_classification_open"
            ]
            is True
        ),
        "gauged_G3_SU5_HSX_full_Hessian_is_exactly_closed": (
            g3_frontier["SU5_Delta_HSX_exact_Hessian_closed"] is True
            and g3_frontier["SU5_Delta_HSX_exact_Hessian_rank"] == 448
            and g3_frontier["SU5_Delta_HSX_exact_Hessian_nullity"] == 38
            and g3_frontier["SU5_Delta_HSX_exact_Hessian_PSD"] is True
            and g3_frontier[
                "SU5_Delta_HSX_exact_Hessian_kernel_is_symmetry"
            ]
            is True
            and g3_frontier["SU5_Delta_HSX_exact_quotient_positive"] is True
        ),
        "gauged_G3_SU5_equality_problem_is_exactly_reduced_and_fail_closed": (
            g3_frontier["SU5_Delta_equality_honestly_reduced"] is True
            and g3_frontier["SU5_Delta_Phi_orbit_audit_honest"] is True
            and g3_frontier[
                "SU5_Delta_literal_single_Phi_orbit_refuted"
            ]
            is True
            and g3_frontier["SU5_Delta_signed_Phi_orbit_theorem_open"] is False
            and g3_frontier["SU5_Delta_signed_Phi_orbit_theorem_closed"] is True
            and g3_frontier["SU5_Delta_SU4_Phi_slice_classified"] is True
            and g3_frontier[
                "SU5_Delta_signed_Phi_local_components_closed"
            ]
            is True
            and g3_frontier["SU5_Delta_distant_Phi_components_excluded"]
            is True
            and g3_frontier["SU5_Delta_Phi_SU3_fixed_slice_closed"] is True
            and g3_frontier["SU5_Delta_Phi_SU3_fixed_slice_dimension"] == 16
            and g3_frontier["SU5_Delta_fixed_F_Sigma_one_orbit_exact"] is True
            and g3_frontier["SU5_Delta_diagonal_Phi_slice_one_orbit_exact"]
            is True
            and g3_frontier["SU5_Delta_global_Phi_orbit_lemma_open"] is False
            and g3_frontier["SU5_Delta_global_Phi_orbit_lemma_closed"] is True
            and g3_frontier[
                "SU5_Delta_global_Phi_orbit_theorem_core_sha256"
            ]
            == "db493a74303a57862f09c2a92118ea3d66b8b12ecbaea9162155d4ab3baafecc"
        ),
        "gauged_G3_SU5_chiral_global_gap_is_reduced_and_fail_closed": (
            g3_frontier["SU5_Delta_chiral_global_gap_honestly_reduced"] is True
            and g3_frontier["SU5_fixed_F_full_offkernel_gap_closed"] is True
            and g3_frontier["SU5_fixed_F_gap_equality_is_selected_flag"] is True
            and g3_frontier["SU5_arbitrary_Phi_offstratum_gap_open"] is True
            and g3_frontier[
                "SU5_max_negative_all_zero_residual_route_excluded"
            ]
            is True
            and g3_frontier[
                "SU5_max_negative_all_zero_residual_strict_margin"
            ]
            == "7859/140295000"
            and g3_frontier[
                "SU5_max_negative_pure_Delta_full_residual_gap_closed"
            ]
            is True
            and g3_frontier[
                "SU5_max_negative_pure_Delta_full_residual_minimum"
            ]
            == "1/5000"
            and g3_frontier[
                "SU5_arbitrary_Phi_nonzero_residual_cancellations_open"
            ]
            is False
            and g3_frontier[
                "SU5_arbitrary_non_pure_Delta_Sigma_uniform_coercivity_open"
            ]
            is True
            and g3_frontier["SU5_arbitrary_Phi_uniform_coercivity_open"] is True
            and g3_frontier["SU5_Delta_chiral_lower_witness_found"] is False
            and g3_frontier["SU5_Delta_chiral_small_beta_route_exists"] is True
            and g3_frontier[
                "SU5_Delta_chiral_beta_1_over_20_global_certified"
            ]
            is False
            and g3_frontier[
                "SU5_Delta_chiral_final_acceptance_test_passes"
            ]
            is False
        ),
        "gauged_G3_rank1_SU3_four_dimensional_slice_is_exact_and_fail_closed": (
            g3_frontier[
                "SU5_max_negative_rank1_SU3_four_dimensional_slice_closed"
            ]
            is True
            and g3_frontier["SU5_max_negative_rank1_SU3_slice_dimension"] == 4
            and g3_frontier["SU5_max_negative_rank1_SU3_ambient_dimension"]
            == 16
            and g3_frontier["SU5_max_negative_rank1_SU3_slice_minimum"]
            == "1/5000"
            and g3_frontier["SU5_max_negative_arbitrary_rank1_Phi_open"]
            is True
            and g3_frontier[
                "SU5_max_negative_arbitrary_Sigma_orientation_open"
            ]
            is True
            and g3_frontier["G3_closed"] is False
        ),
        "gauged_G3_rank1_SU4_infrastructure_is_exact_and_fail_closed": (
            g3_frontier["rank1_SU4_stabilizer_infrastructure_exact"] is True
            and g3_frontier["rank1_SU4_joint_stabilizer_dimension"] == 15
            and g3_frontier[
                "rank1_SU4_Phi210_intertwiner_infrastructure_exact"
            ]
            is True
            and g3_frontier["rank1_SU4_Phi210_carrier_count"] == 25
            and g3_frontier["rank1_SU4_Sym2_invariant_dimension"] == 45
            and g3_frontier["rank1_SU4_aligned_carriers_exact"] is True
            and g3_frontier["rank1_SU4_aligned_direct_sum_rank"] == 210
            and g3_frontier["rank1_SU4_physical_real_maps_exact"] is True
            and g3_frontier["rank1_SU4_Phi210_quadratic_basis_exact"] is True
            and g3_frontier["rank1_SU4_quadratic_constraint_shape"]
            == [5952, 551]
            and g3_frontier["rank1_SU4_quadratic_constraint_rank"] == 506
            and g3_frontier["rank1_SU4_quadratic_constraint_nullity"] == 45
            and g3_frontier["rank1_SU4_quadratic_basis_count"] == 45
            and g3_frontier["rank1_SU4_quadratic_basis_rank"] == 45
            and g3_frontier[
                "rank1_SU4_quadratic_live_invariance_exact"
            ] is True
            and g3_frontier["rank1_SU4_Schur_SOS_SDP_open"] is True
            and g3_frontier["rank1_SU4_arbitrary_Phi_bound_open"] is True
            and g3_frontier["rank1_SU4_augmented_SOS_census_exact"] is True
            and g3_frontier["rank1_SU4_augmented_homogeneous_dimension"]
            == 22_366
            and g3_frontier[
                "rank1_SU4_augmented_complex_isotypic_type_count"
            ] == 35
            and g3_frontier[
                "rank1_SU4_augmented_complex_irreducible_copy_count"
            ] == 824
            and g3_frontier["rank1_SU4_augmented_real_isotypic_block_count"]
            == 22
            and g3_frontier[
                "rank1_SU4_augmented_real_symmetric_block_count"
            ] == 9
            and g3_frontier[
                "rank1_SU4_augmented_complex_Hermitian_block_count"
            ] == 13
            and g3_frontier["rank1_SU4_augmented_Schur_real_parameter_count"]
            == 19_594
            and g3_frontier["rank1_SU4_augmented_invariant_equation_count"]
            == 6_585
            and g3_frontier["rank1_SU4_augmented_abstract_total_rank"]
            == 6_585
            and g3_frontier[
                "rank1_SU4_augmented_abstract_total_kernel_dimension"
            ] == 13_009
            and g3_frontier["rank1_SU4_augmented_coordinate_Schur_map_open"]
            is True
            and g3_frontier["rank1_SU4_augmented_isotypic_maps_open"] is True
            and g3_frontier["rank1_SU4_augmented_physical_target_open"]
            is True
            and g3_frontier["rank1_SU4_augmented_Schur_SOS_SDP_open"]
            is True
            and g3_frontier["rank1_SU4_augmented_arbitrary_Phi_bound_open"]
            is True
            and g3_frontier["rank1_SU4_augmented_cubic_map_exact"] is True
            and g3_frontier[
                "rank1_SU4_augmented_cubic_carrier_copy_count"
            ] == 540
            and g3_frontier[
                "rank1_SU4_augmented_cubic_real_variable_count"
            ] == 1_414
            and g3_frontier[
                "rank1_SU4_augmented_cubic_coordinate_map_shape"
            ] == [478, 1_414]
            and g3_frontier[
                "rank1_SU4_augmented_cubic_coordinate_map_nnz"
            ] == 3_145
            and g3_frontier[
                "rank1_SU4_augmented_cubic_coordinate_map_rank"
            ] == 478
            and g3_frontier[
                "rank1_SU4_augmented_cubic_coordinate_map_kernel_dimension"
            ] == 936
            and g3_frontier[
                "rank1_SU4_augmented_cubic_zero_placeholder_nonphysical"
            ] is True
            and g3_frontier[
                "rank1_SU4_augmented_cubic_other_graded_maps_open"
            ] is True
            and g3_frontier[
                "rank1_SU4_augmented_cubic_full_coordinate_map_open"
            ] is True
            and g3_frontier[
                "rank1_SU4_augmented_cubic_physical_target_open"
            ] is True
            and g3_frontier[
                "rank1_SU4_augmented_cubic_Schur_SOS_SDP_open"
            ] is True
            and g3_frontier[
                "rank1_SU4_augmented_cubic_arbitrary_Phi_bound_open"
            ] is True
            and g3_frontier["rank1_SU4_augmented_cubic_G3_open"] is True
            and g3_frontier["rank1_SU4_augmented_quartic_map_exact"] is True
            and g3_frontier[
                "rank1_SU4_augmented_quartic_carrier_family_count"
            ] == 35
            and g3_frontier[
                "rank1_SU4_augmented_quartic_irreducible_copy_count"
            ] == 798
            and g3_frontier[
                "rank1_SU4_augmented_quartic_real_block_count"
            ] == 22
            and g3_frontier[
                "rank1_SU4_augmented_quartic_coordinate_map_shape"
            ] == [6_057, 18_085]
            and g3_frontier[
                "rank1_SU4_augmented_quartic_coordinate_map_nnz"
            ] == 115_641
            and g3_frontier[
                "rank1_SU4_augmented_quartic_coordinate_map_rank"
            ] == 6_057
            and g3_frontier[
                "rank1_SU4_augmented_quartic_coordinate_map_kernel_dimension"
            ] == 12_028
            and g3_frontier[
                "rank1_SU4_augmented_quartic_physical_target_open"
            ] is True
            and g3_frontier[
                "rank1_SU4_augmented_quartic_standard_PSD_congruences_open"
            ] is True
            and g3_frontier[
                "rank1_SU4_augmented_quartic_SDP_open"
            ] is True
            and g3_frontier[
                "rank1_SU4_augmented_quartic_arbitrary_Phi_bound_open"
            ] is True
            and g3_frontier["rank1_SU4_augmented_quartic_G3_open"] is True
            and g3_frontier[
                "rank1_SU4_legacy_v20_PSD_routes_and_stale_payload_well_formed"
            ] is True
            and g3_frontier["rank1_SU4_legacy_v20_physical_target_valid"]
            is False
            and g3_frontier["rank1_SU4_legacy_v20_primal_valid"] is False
            and g3_frontier[
                "rank1_SU4_augmented_standard_PSD_route_count"
            ] == 22
            and g3_frontier[
                "rank1_SU4_augmented_standard_PSD_parameter_count"
            ] == 19_594
            and g3_frontier[
                "rank1_SU4_augmented_real_type_PSD_congruences_exact"
            ] is True
            and g3_frontier[
                "rank1_SU4_augmented_complex_Hermitian_coordinates_exact"
            ] is True
            and g3_frontier[
                "rank1_SU4_corrected_fixed_endpoint_theorem_exact"
            ] is True
            and g3_frontier[
                "rank1_SU4_corrected_publication_manifest_sha256"
            ] == corrected_rank1.EXPECTED_MANIFEST_RAW_SHA256
            and g3_frontier[
                "rank1_SU4_corrected_positive_Gram_map_shape"
            ] == [6_585, 19_594]
            and g3_frontier[
                "rank1_SU4_corrected_positive_Gram_map_common_denominator"
            ] == 256
            and g3_frontier[
                "rank1_SU4_corrected_positive_Gram_map_nnz"
            ] == 138_550
            and g3_frontier[
                "rank1_SU4_corrected_positive_Gram_map_sha256"
            ] == corrected_rank1.EXPECTED_MAP_SHA256
            and g3_frontier[
                "rank1_SU4_corrected_physical_target_common_denominator"
            ] == 576_000
            and g3_frontier[
                "rank1_SU4_corrected_physical_target_nonzero_count"
            ] == 512
            and g3_frontier[
                "rank1_SU4_corrected_physical_target_sha256"
            ] == corrected_rank1.EXPECTED_TARGET_SHA256
            and g3_frontier[
                "rank1_SU4_corrected_exact_coefficient_equalities"
            ] == 6_585
            and g3_frontier[
                "rank1_SU4_corrected_strict_positive_Gram_blocks"
            ] == 22
            and g3_frontier[
                "rank1_SU4_corrected_strict_positive_LDL_pivots"
            ] == 824
            and g3_frontier[
                "rank1_SU4_corrected_arbitrary_real_Phi_at_fixed_endpoint"
            ] is True
            and g3_frontier[
                "rank1_SU4_corrected_strict_positive_off_homogeneous_origin"
            ] is True
            and g3_frontier[
                "rank1_SU4_corrected_A_greater_than_3_over_200_at_t1"
            ] is True
            and g3_frontier[
                "rank1_SU4_corrected_p_zero_set_at_t1_empty"
            ] is True
            and g3_frontier[
                "rank1_SU4_corrected_global_Sigma_proved"
            ] is False
            and g3_frontier["rank1_SU4_corrected_general_H_proved"] is False
            and g3_frontier["rank1_SU4_corrected_full_H_proved"] is False
            and g3_frontier[
                "rank1_SU4_corrected_full_Hessian_proved"
            ] is False
            and g3_frontier["rank1_SU4_corrected_G3_closed"] is False
            and g3_frontier["G3_closed"] is False
            and g3_frontier["whole_model_excluded"] is False
        ),
        "gauged_G3_alternative_global_SOS_routes_are_honestly_audited": (
            g3_frontier["alternative_global_SOS_audit_honestly_open"] is True
            and g3_frontier[
                "all_vanishing_global_SOS_replacements_excluded"
            ]
            is True
            and g3_frontier[
                "nonvanishing_residual_global_SOS_replacements_excluded"
            ]
            is False
        ),
        "gauged_G3_constructive_frontier_is_27_51_429_33_448": (
            g3_frontier["candidate_nonzero_real_parameters"] == 27
            and g3_frontier["candidate_real_parameter_count"] == 51
            and g3_frontier["candidate_maximum_absolute_coefficient"] == 9.125
            and g3_frontier["candidate_J0"] == "-21/200"
            and g3_frontier["exact_PD_rank"] == 429
            and g3_frontier["exact_PD_nullity"] == 33
            and g3_frontier["exact_full_Hessian_rank"] == 448
        ),
        "gauged_G3_local_minimum_and_global_counterexample_certified": (
            g3_frontier["integrity_pass"] is True
            and g3_frontier["direct_exact_PD_source_binding"] is True
            and g3_frontier["complete_potential_BFB_exactly_certified"] is True
            and g3_frontier[
                "selected_vacuum_stationarity_exactly_certified"
            ]
            is True
            and g3_frontier["strict_local_minimum_certified"] is True
            and g3_frontier["global_minimum_certified"] is False
            and g3_frontier["selected_global_minimum_disproved"] is True
            and g3_frontier[
                "exact_lower_energy_field_witness_certified"
            ]
            is True
            and g3_frontier["constructive_candidate_rejected_for_G3"] is True
            and g3_frontier["global_uniqueness_certified"] is False
            and g3_frontier["G3_closed"] is False
            and g3_frontier["whole_model_validated"] is False
            and g3_frontier["whole_model_excluded"] is False
        ),
        "dependency_graph_acyclic": _acyclic_dependencies(),
        "model_contract_precedes_G1": DEPENDENCIES["G1"] == ["MODEL_CONTRACT"],
        "all_eight_gates_present": set(gates) == {f"G{i}" for i in range(1, 9)},
        "gate_frontier_matches_contract_state": statuses == expected_statuses,
        "closed_gates_have_closed_dependencies": all(
            all(dependency_closed(parent) for parent in DEPENDENCIES[name])
            for name in closed
        ),
        "open_gates_have_closed_dependencies": all(
            all(dependency_closed(parent) for parent in DEPENDENCIES[name])
            for name in open_gates
        ),
        "G5_closure_respects_full_G1_G2_dependencies": (
            statuses["G5"] == expected_statuses["G5"]
            and not any(
                statuses[f"G{i}"] == STATUS_CLOSED for i in (3, 4, 6, 7, 8)
            )
        ),
        "whole_model_neither_validated_nor_excluded": (
            x_report["flag"]["whole_model_validated"] is False
            and x_report["flag"]["whole_model_excluded"] is False
            and historical["G3"]["whole_gauged_model_excluded"] is False
        ),
    }
    audit_failures = [name for name, passed in checks.items() if not passed]

    if audit_failures:
        status = "G1_G8_LEDGER_AUDIT_EXECUTION_FAILED"
        overall_state = "EXECUTION_FAIL"
    elif contract_consistent and statuses["G1"] == STATUS_CLOSED and statuses[
        "G2"
    ] == STATUS_CLOSED:
        status = (
            "G1_G8_LEDGER_AUDIT_COMPLETE__MODEL_CONTRACT_CONSISTENT__"
            "G1_G2_G5_CLOSED__G3_GLOBAL_OPEN"
        )
        overall_state = STATUS_OPEN
    elif contract_consistent:
        status = (
            "G1_G8_LEDGER_AUDIT_COMPLETE__MODEL_CONTRACT_CONSISTENT__"
            "G1_COMPONENT_TENSOR_INTEGRATION_OPEN__G2_DEPENDENCY_BLOCKED"
        )
        overall_state = STATUS_OPEN
    else:
        status = (
            "G1_G8_LEDGER_AUDIT_COMPLETE__MODEL_CONTRACT_BLOCKED__"
            "MATHEMATICAL_G1_COMPONENT_RING_AND_G2_DERIVATIVE_AUDIT_RECERTIFIED"
        )
        overall_state = STATUS_BLOCKED

    scientific_blockers = [
        "GAUGED_U1X_G3_G8_CLOSURE_REQUIRED",
        "G3_ARBITRARY_NON_PURE_DELTA_SIGMA_UNIFORM_COERCIVITY_OPEN",
    ]
    if not g1_full_component_tensors_closed:
        scientific_blockers[0:0] = [
            "G1_EXPLICIT_COMPONENT_TENSOR_INTEGRATION_OPEN",
            "G2_AUTHORITATIVE_PROMOTION_BLOCKED_ON_FULL_G1",
        ]
    if not contract_consistent:
        scientific_blockers[0:0] = list(
            x_report.get("scientific_blockers") or [contract_blocker]
        )

    closure_waves = [
        {
            "wave": 0,
            "id": "MODEL_CONTRACT",
            "status": STATUS_CLOSED if contract_consistent else STATUS_BLOCKED,
            "deliverable": (
                "Execute the shipped hash-bound validation driver with a real "
                "SARAH installation and retain its v2 process attestation."
            ),
        },
        {
            "wave": 1,
            "gates": ["G1"],
            "status": gates["G1"]["status"],
            "scoped_calculation_status": (
                "SOURCE_BOUND_FULL_RENORMALIZABLE_G1_MATHEMATICAL_RING_CLOSED"
            ),
            "deliverable": (
                "Promote the source-bound 44-direction/51-parameter mathematical "
                "G1 theorem only after the external SARAH contract attestation."
            ),
        },
        {
            "wave": 2,
            "gates": ["G2"],
            "status": gates["G2"]["status"],
            "scoped_calculation_status": "DENSE_DERIVATIVE_AUDIT_COMPLETE",
            "deliverable": (
                "Promote the completed 44/51/486 derivative and Ward audit only "
                "after the source-bound mathematical G1 theorem and external SARAH "
                "contract are both authoritative."
            ),
        },
        {
            "wave": 3,
            "gates": ["G3", "G4", "G5"],
            "status": (
                "G3_OPEN__G4_BLOCKED_ON_G3__G5_CLOSED"
                if statuses["G3"] == STATUS_OPEN
                else "BLOCKED_ON_G2"
            ),
            "deliverable": (
                "Promote the source-bound BFB, exact selected stationarity, and "
                "strict-local-minimum certificate after contract repair, while "
                "retaining the exact counterexample that rejects globality. To "
                "close G3, prove uniform coercivity for arbitrary non-pure-Delta "
                "Sigma orientations on the surviving SU(5)+Delta chiral-H "
                "branch. Its full 486-real Hessian is now exactly PSD "
                "with rank/nullity 448/38 and symmetry kernel exactly 38; the "
                "complete maximally-negative pure-Delta sector is already "
                "excluded for arbitrary real Phi and nonzero residuals with "
                "sharp gap 1/5000. The prior four-real-dimensional SU(3) "
                "regression is historical and subsumed. At fixed H=h_- and "
                "Sigma=q/4, the corrected v21 exact theorem covers every real "
                "Phi210. Its exact SU(4) "
                "stabilizer, aligned rank-210 carrier real maps, and explicit "
                "complete 45-element Phi210 invariant quadratic basis feed an "
                "exact 22366-dimensional augmented census with 35 isotypic "
                "types/824 copies, 22 real/Hermitian blocks, 19594 Schur "
                "parameters, and 6585 invariant rows. The complete cubic "
                "interface is explicit: all 1414 real cross variables map "
                "through a 478x1414 integer matrix of exact rank 478 and kernel "
                "dimension 936. Its zero placeholder is not a physical target. "
                "The homogeneous quartic interface is also exact: its "
                "6057x18085 integer map has rank 6057 and kernel dimension "
                "12028. The legacy v20 assembled physical target is rejected. "
                "The corrected 6585x19594 standard positive-Gram map, corrected "
                "ordered-spectral target, and exact strict 22-block/824-pivot "
                "primal prove p(t,Phi)>0 off the homogeneous origin, hence "
                "A(Phi)>3/200 at t=1 for every real Phi210. Global Sigma, "
                "general/full H, the full Hessian, and G3 remain open."
            ),
        },
        {"wave": 4, "gates": ["G6"], "status": "BLOCKED_ON_G3_G4_G5"},
        {"wave": 5, "gates": ["G7"], "status": "BLOCKED_ON_G6"},
        {"wave": 6, "gates": ["G8"], "status": "BLOCKED_ON_G3_G6_G7"},
    ]

    verdict = (
        "The ledger audit succeeds and the repaired gauged-U(1)_X contract "
        "promotes full G1, including the multiplicity census and explicit "
        "component tensors, plus the G2 dense derivative theorem to CLOSED. A "
        "perturbative 27-of-51 SOS candidate with J0=-21/200 has a "
        "source-bound complete-potential BFB proof, exact stationarity, direct "
        "P+Delta rank/nullity 429/33, and a proof of positivity on all 448 "
        "transverse Hessian directions. The selected orbit is a strict local "
        "minimum, but an exact field witness is lower by 25*r^4/19008 and "
        "rejects it as the global vacuum. The fixed-P branch is now excluded "
        "exactly, and its lower replacement has the wrong gauge stabilizer. A "
        "new SU(5)+Delta branch is an exact global Phi/Sigma minimum with the "
        "correct SM stabilizer and exact quotient rank 429. Its chiral-H full "
        "Hessian is exactly PSD with rank/nullity 448/38 and kernel precisely the "
        "38 symmetry tangents. The complete maximally-negative pure-Delta sector "
        "is excluded for arbitrary real Phi and all nonzero residuals, with sharp "
        "gap 1/5000. The prior four-real-dimensional SU(3) regression is "
        "historical and subsumed. At fixed H=h_- and Sigma=q/4, the corrected "
        "v21 exact theorem covers every real Phi210. The "
        "exact SU(4) stabilizer, aligned rank-210 carrier real maps, and explicit "
        "complete 45-element Phi210 invariant quadratic basis feed the exact "
        "22366-dimensional augmented census (35 types/824 copies, 22 blocks, "
        "19594 parameters, 6585 rows). The complete cubic Schur interface is "
        "explicit, with 1414 real variables and an exact-rank-478, 478x1414 "
        "integer map whose kernel has dimension 936. Its reserved zero vector "
        "is not a physical G3 target. The exact quartic Schur map has shape "
        "6057x18085, rank 6057, and kernel dimension 12028. The legacy v20 "
        "assembled physical target is rejected. The corrected 6585x19594 "
        "standard positive-Gram map, ordered-spectral target, and exact strict "
        "22-block/824-pivot primal prove p(t,Phi)>0 off the homogeneous origin, "
        "hence A(Phi)>3/200 at t=1 for every real Phi210. Global Sigma, "
        "general/full H, the full Hessian, and G3 remain open. "
        "G5 is CLOSED; G4 and G6-G8 remain "
        "dependency-blocked. Historical "
        "Option-C evidence remains scoped and closes no gauged-model gate."
        if contract_consistent
        and statuses["G1"] == STATUS_CLOSED
        and statuses["G2"] == STATUS_CLOSED
        else "The ledger audit succeeds, but all G1-G8 gates are BLOCKED. The "
        "gauged-U(1)_X SARAH input, charge catalogues, Lagrangian registration, "
        "and hash-bound validation bundle are now statically consistent; Wave 0 "
        "still requires a real external SARAH execution attestation. The gauged G1 "
        "multiplicity census, source-bound normalized component-tensor ring, and G2 "
        "dense derivative theorem are recertified as 44 directions, 51 parameters, "
        "18 tensor families, and 486 fields. Three structural gradient "
        "columns vanish exactly; matching exact lower- and upper-rank certificates "
        "prove stationarity rank/nullity 13/38. "
        "The character census remains explicitly multiplicity-only; the separate G1 "
        "theorem supplies its complete source-bound tensor integration without changing "
        "that census scope. G1 and the G2 scoped audit cannot be promoted until the "
        "external model contract closes. A perturbative "
        "27-of-51 SOS candidate with J0=-21/200 is explicit. Exact source-bound "
        "SOS identities prove complete-potential BFB and stationarity. Direct "
        "Gaussian-integer/Fraction/Q(sqrt(2)) assembly gives P+Delta rank/nullity "
        "429/33, and the exact extension leaves only 38 symmetry tangents, proving "
        "a strict local minimum on all 448 transverse directions. An exact "
        "symmetry-inequivalent field configuration is lower by 25*r^4/19008, "
        "so this selected global vacuum and candidate are rejected. The fixed-P "
        "branch is exactly excluded, and the lower stationary replacement has "
        "the wrong gauge symmetry. A new SU(5)+Delta Phi/Sigma branch has an "
        "exact global SOS minimum, the correct SM stabilizer, and exact quotient "
        "rank/nullity 429/33. Its chiral-H full-field extension is exactly BFB, "
        "stationary and symmetry-correct. The source-bound 486-real Hessian is "
        "exactly PSD with rank/nullity 448/38, and its kernel is exactly the 38 "
        "symmetry tangents. The literal one-orbit Phi lemma is refuted by -F; the "
        "complete maximally-negative pure-Delta sector is excluded for arbitrary "
        "real Phi and all nonzero residuals with sharp gap 1/5000. The prior "
        "four-real-dimensional SU(3) regression is historical and subsumed. "
        "At fixed H=h_- and Sigma=q/4, the corrected v21 exact theorem covers "
        "every real Phi210. Its exact SU(4) stabilizer, aligned "
        "rank-210 carrier real maps, explicit complete 45-element Phi210 "
        "invariant quadratic basis, and exact augmented census are certified. "
        "The complete cubic interface now has all 1414 real Schur cross "
        "variables and an exact-rank-478, 478x1414 map with kernel dimension "
        "936; its abstract zero placeholder is not the physical gap target. "
        "The homogeneous quartic interface is now an exact-rank-6057, "
        "6057x18085 map with kernel dimension 12028. The legacy v20 assembled "
        "physical target is rejected. The corrected 6585x19594 standard "
        "positive-Gram map, ordered-spectral target, and exact strict "
        "22-block/824-pivot primal prove p(t,Phi)>0 off the homogeneous origin, "
        "hence A(Phi)>3/200 at t=1 for every real Phi210. Global Sigma, "
        "general/full H, the full Hessian, and G3 remain open. The "
        "historical 64/91 "
        "derivative theorem, 449-dimensional "
        "quotient, 46-mode saddle, and 80-iteration no-PSD search are preserved "
        "as Option-C subtheorems and neither validate nor exclude the gauged model."
    )
    if contract_consistent and statuses["G1"] == STATUS_OPEN:
        verdict = (
            "The ledger audit succeeds and the gauged-U(1)_X executable contract "
            "is consistent, but full G1 remains OPEN. Its exact renormalizable "
            "multiplicity census is complete at 28 Hermitian conjugacy orbits, "
            "44 invariant directions, and 51 real parameters; the explicit "
            "component-tensor/Clebsch integration is still open. The exact "
            "44/51/486 G2 derivative and Ward-identity audit is a complete scoped "
            "subtheorem with stationarity rank/nullity 13/38, but authoritative "
            "G2 remains dependency-BLOCKED until full G1 closes. Consequently G3, "
            "G4, G5, G6, G7, and G8 remain dependency-BLOCKED, and no full-model "
            "gate is promoted by contract repair alone. Historical Option-C "
            "evidence remains scoped and closes no gauged-model gate."
        )
    verdict += (
        " In the parallel dimension-six EFT namespace, the exact normalized "
        "tree-level physical scalar spectrum closes mathematical G6: all 486 "
        "real modes are classified into 37 gauge tangents, one physical PQ "
        "axion, and 448 strictly positive massive modes with exact residual-group "
        "and mixing provenance. EFT release G6 and authoritative renormalizable "
        "G6 remain false."
        if parallel_eft_g6_spectrum["mathematical_G6_closed_for_EFT_model"]
        else " The parallel EFT G6 spectrum gate is missing or invalid."
    )

    return {
        "status": status,
        "overall_state": overall_state,
        "model_contract_id": AUTHORITATIVE_CONTRACT_ID,
        "declared_contract_consistent": declared_contract_consistent,
        "contract_evidence_complete": contract_evidence_complete,
        "contract_consistent": contract_consistent,
        "scientific_blockers": scientific_blockers,
        "n_checks": len(checks),
        "n_failed": len(audit_failures),
        "failures": audit_failures,
        "audit_failures": audit_failures,
        "checks": checks,
        "model_contract_reports": {
            "exact_X": x_report,
            "gauged_G1_character_census": g1_report,
            "gauged_G1_component_tensor_closure": g1_component_tensor_report,
            "gauged_G2_derivative_audit": g2_report,
            "gauged_scalar_filter": filter_report,
            "gauged_G3_SOS_candidate": g3_sos_report,
            "gauged_G3_direct_exact_PD_rank": g3_pd_report,
            "gauged_G3_exact_A_square_recoupling": g3_a_square_report,
            "gauged_G3_exact_SOS_BFB_stationarity": g3_sos_bfb_report,
            "gauged_G3_fixed_P_kernel_no_go": g3_kernel_bound_report,
            "gauged_G3_lower_replacement_orbit": g3_replacement_report,
            "gauged_G3_SU5_Delta_PD_global_SOS": g3_su5_pd_report,
            "gauged_G3_SU5_Delta_HSX_extension": g3_su5_hsx_report,
            "gauged_G3_SU5_Delta_HSX_exact_Hessian": (
                g3_su5_hsx_exact_hessian_report
            ),
            "gauged_G3_SU5_Delta_equality_orbit": g3_su5_equality_report,
            "gauged_G3_SU5_Delta_Phi_orbit_lemma_audit": (
                g3_su5_phi_orbit_report
            ),
            "gauged_G3_SU5_Delta_Phi_local_component_theorem": (
                g3_su5_phi_local_component_report
            ),
            "gauged_G3_SU5_Delta_Phi_SU3_fixed_slice_theorem": (
                g3_su5_phi_su3_slice_report
            ),
            "gauged_G3_SU5_Delta_chiral_global_gap": g3_su5_gap_report,
            "gauged_G3_SU5_fixed_F_full_offkernel_bound": (
                g3_su5_fixed_f_offkernel_report
            ),
            "gauged_G3_SU5_max_negative_all_zero_residual_bound": (
                g3_su5_max_negative_zero_residual_report
            ),
            "gauged_G3_SU5_max_negative_full_residual_pure_Delta_bound": (
                g3_su5_max_negative_full_residual_report
            ),
            "gauged_G3_SU5_max_negative_rank1_SU3_four_dimensional_slice_bound": (
                g3_su5_max_negative_rank1_su3_slice_report
            ),
            "gauged_G3_rank1_SU4_stabilizer_infrastructure": (
                g3_rank1_su4_stabilizer_report
            ),
            "gauged_G3_rank1_SU4_Phi210_intertwiner_infrastructure": (
                g3_rank1_su4_phi210_intertwiners_report
            ),
            "gauged_G3_rank1_SU4_aligned_carrier_infrastructure": (
                g3_rank1_su4_aligned_carriers_report
            ),
            "gauged_G3_rank1_SU4_Phi210_quadratic_basis": (
                g3_rank1_su4_phi210_quadratic_basis_report
            ),
            "gauged_G3_rank1_SU4_augmented_SOS_census": (
                g3_rank1_su4_augmented_sos_census_report
            ),
            "gauged_G3_rank1_SU4_augmented_SOS_cubic_map": (
                g3_rank1_su4_augmented_sos_cubic_map_report
            ),
            "gauged_G3_rank1_SU4_augmented_SOS_quartic_map": (
                g3_rank1_su4_augmented_sos_quartic_map_report
            ),
            "gauged_G3_rank1_SU4_legacy_v20_PSD_routes_and_rejected_target": (
                g3_rank1_su4_augmented_sos_psd_target_report
            ),
            "gauged_G3_rank1_SU4_corrected_fixed_endpoint_publication_v21": (
                g3_rank1_su4_corrected_publication
            ),
            "gauged_G3_alternative_global_SOS_audit": (
                g3_alternative_global_sos_report
            ),
            "parallel_EFT_G3_acceptance_gate": final_g3_eft_acceptance_report,
            "parallel_EFT_G4_mathematical_gate": (
                final_g4_eft_mathematical_report
            ),
            "parallel_EFT_G5_mathematical_gate": (
                final_g5_eft_mathematical_report
            ),
            "parallel_EFT_G6_mathematical_gate": (
                final_g6_eft_mathematical_report
            ),
        },
        "renormalizable_G1_component_tensor_closure": (
            g1_component_tensor_closure
        ),
        "gauged_u1x_scalar_subtheorems": scoped,
        "gauged_u1x_g3_constructive_frontier": g3_frontier,
        "parallel_EFT_G3_acceptance": parallel_eft_g3_acceptance,
        "parallel_EFT_G4_mathematical": parallel_eft_g4_mathematical,
        "parallel_EFT_G5_mathematical": parallel_eft_g5_mathematical,
        "parallel_EFT_G6_spectrum": parallel_eft_g6_spectrum,
        "historical_option_c_subtheorems": historical,
        "dependencies": DEPENDENCIES,
        "gates": gates,
        "summary": {
            "closed": closed,
            "partial": partial,
            "open": open_gates,
            "blocked": blocked,
            "n_closed": len(closed),
            "n_partial": len(partial),
            "n_open": len(open_gates),
            "n_blocked": len(blocked),
        },
        "closure_waves": closure_waves,
        "feasibility": {
            "closure_program_defined": True,
            "current_authoritative_closed_gates": len(closed),
            "historical_subtheorems_reusable_after_contract_filtering": True,
            "gauged_G1_multiplicity_census_complete": scoped["G1"][
                "multiplicity_census_complete"
            ],
            "gauged_G1_full_component_tensor_integration_complete": scoped["G1"][
                "full_G1_closed"
            ],
            "gauged_G2_dense_derivative_scoped_subtheorem_complete": scoped["G2"][
                "scoped_derivative_audit_complete"
            ],
            "gauged_G3_constructive_candidate_available": g3_frontier[
                "integrity_pass"
            ],
            "gauged_G3_direct_exact_source_binding_complete": g3_frontier[
                "direct_exact_PD_source_binding"
            ]
            is True,
            "guarantee_model_survives_recertification": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": verdict,
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    return _build_report_from_inputs(
        x_report=exact_x.build_report(),
        g1_report=gauged_g1.build_report(),
        g2_report=_load_or_build_gauged_g2_report(),
        filter_report=gauged_filter.build_report(),
        g3_sos_report=_load_json_artifact(G3_SOS_JSON),
        g3_pd_report=_load_json_artifact(G3_PD_JSON),
        g3_a_square_report=_load_json_artifact(G3_A_SQUARE_JSON),
        g3_sos_bfb_report=_load_json_artifact(G3_SOS_BFB_JSON),
        g3_kernel_bound_report=_load_json_artifact(G3_KERNEL_BOUND_JSON),
        g3_replacement_report=_load_json_artifact(G3_REPLACEMENT_JSON),
        g3_su5_pd_report=_load_json_artifact(G3_SU5_PD_JSON),
        g3_su5_hsx_report=_load_json_artifact(G3_SU5_HSX_JSON),
        g3_su5_hsx_exact_hessian_report=_load_json_artifact(
            G3_SU5_HSX_EXACT_HESSIAN_JSON
        ),
        g3_su5_equality_report=_load_json_artifact(G3_SU5_EQUALITY_JSON),
        g3_su5_phi_orbit_report=_load_json_artifact(G3_SU5_PHI_ORBIT_JSON),
        g3_su5_phi_local_component_report=_load_json_artifact(
            G3_SU5_PHI_LOCAL_COMPONENT_JSON
        ),
        g3_su5_phi_su3_slice_report=_load_json_artifact(
            G3_SU5_PHI_SU3_SLICE_JSON
        ),
        g3_su5_gap_report=_load_json_artifact(G3_SU5_GAP_JSON),
        g3_su5_fixed_f_offkernel_report=_load_json_artifact(
            G3_SU5_FIXED_F_OFFKERNEL_JSON
        ),
        g3_su5_max_negative_zero_residual_report=_load_json_artifact(
            G3_SU5_MAX_NEGATIVE_ZERO_RESIDUAL_JSON
        ),
        g3_su5_max_negative_full_residual_report=_load_json_artifact(
            G3_SU5_MAX_NEGATIVE_FULL_RESIDUAL_JSON
        ),
        g3_su5_max_negative_rank1_su3_slice_report=_load_json_artifact(
            G3_SU5_MAX_NEGATIVE_RANK1_SU3_SLICE_JSON
        ),
        g3_rank1_su4_stabilizer_report=_load_json_artifact(
            G3_RANK1_SU4_STABILIZER_JSON
        ),
        g3_rank1_su4_phi210_intertwiners_report=_load_json_artifact(
            G3_RANK1_SU4_PHI210_INTERTWINERS_JSON
        ),
        g3_rank1_su4_aligned_carriers_report=_load_json_artifact(
            G3_RANK1_SU4_ALIGNED_CARRIERS_JSON
        ),
        g3_rank1_su4_phi210_quadratic_basis_report=_load_json_artifact(
            G3_RANK1_SU4_PHI210_QUADRATIC_BASIS_JSON
        ),
        g3_rank1_su4_augmented_sos_census_report=_load_json_artifact(
            G3_RANK1_SU4_AUGMENTED_SOS_CENSUS_JSON
        ),
        g3_rank1_su4_augmented_sos_cubic_map_report=_load_json_artifact(
            G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_JSON
        ),
        g3_rank1_su4_augmented_sos_quartic_map_report=_load_json_artifact(
            G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_JSON
        ),
        g3_rank1_su4_augmented_sos_psd_target_report=_load_json_artifact(
            G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_JSON
        ),
        g3_rank1_su4_corrected_publication=(
            corrected_rank1.load_validated_publication()
        ),
        g3_alternative_global_sos_report=_load_json_artifact(
            G3_ALTERNATIVE_GLOBAL_SOS_JSON
        ),
        final_g3_eft_acceptance_report=_load_json_artifact(
            FINAL_G3_EFT_ACCEPTANCE_JSON
        ),
        final_g3_eft_acceptance_raw_sha256=_raw_file_sha256(
            FINAL_G3_EFT_ACCEPTANCE_JSON
        ),
        final_g4_eft_mathematical_report=_load_json_artifact(
            FINAL_G4_EFT_MATHEMATICAL_JSON
        ),
        final_g4_eft_mathematical_raw_sha256=_raw_file_sha256(
            FINAL_G4_EFT_MATHEMATICAL_JSON
        ),
        final_g5_eft_mathematical_report=_load_json_artifact(
            FINAL_G5_EFT_MATHEMATICAL_JSON
        ),
        final_g5_eft_mathematical_raw_sha256=_raw_file_sha256(
            FINAL_G5_EFT_MATHEMATICAL_JSON
        ),
    )


def write_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# G1-G8 contract-aware gate ledger - v20",
        "",
        f"**Status:** `{report['status']}`",
        f"**Overall state:** `{report['overall_state']}`",
        f"**Contract consistent:** `{report['contract_consistent']}`",
        "",
        report["verdict"],
        "",
        "## Critical path",
        "",
        "`MODEL_CONTRACT -> G1 -> G2 -> G3/G4/G5 -> G6 -> G7 -> G8`",
        "",
        "## Parallel EFT G3/G4/G5 classifications",
        "",
        (
            "- Dimension-six EFT mathematical G3: "
            f"**{report['parallel_EFT_G3_acceptance']['mathematical_G3_closed_for_EFT_model']}**"
        ),
        (
            "- EFT release G3 verified: "
            f"**{report['parallel_EFT_G3_acceptance']['release_G3_verified_for_EFT_model']}**"
        ),
        (
            "- Dimension-six EFT mathematical G4: "
            f"**{report['parallel_EFT_G4_mathematical']['mathematical_G4_closed_for_EFT_model']}**"
        ),
        (
            "- EFT release G4 verified: "
            f"**{report['parallel_EFT_G4_mathematical']['release_G4_verified_for_EFT_model']}**"
        ),
        (
            "- Dimension-six EFT mathematical G5: "
            f"**{report['parallel_EFT_G5_mathematical']['mathematical_G5_closed_for_EFT_model']}**"
        ),
        (
            "- EFT release G5 verified: "
            f"**{report['parallel_EFT_G5_mathematical']['release_G5_verified_for_EFT_model']}**"
        ),
        "- The authoritative renormalizable G3, G4, and G5 gates are unchanged.",
        "",
        "## Authoritative gates",
        "",
    ]
    lines.extend(
        (
            f"- `{name}`: `{row['status']}` - "
            + (
                ", ".join(row["authoritative_closed_scope"])
                if row["status"] == STATUS_CLOSED
                else row["open_scope"][0]
            )
        )
        for name, row in report["gates"].items()
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
