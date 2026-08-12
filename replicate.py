#!/usr/bin/env python3
"""One-command pristine replication of the v20 package.

Runs: golden-anchor checks → independent error audit → v20 engine →
unit tests → external next-step packages (flavour / thresholds / haloscope
forecast).  Exits nonzero on any failure.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
GOLDEN = ROOT / "golden" / "expected_anchors_v20.json"


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["SO10_PUBLISHED_API_ROOT"] = str(ROOT)
    for name in (
        "OPENBLAS_NUM_THREADS",
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
    ):
        environment[name] = "1"
    subprocess.run(cmd, cwd=ROOT, check=True, env=environment)


def check_golden_anchors() -> None:
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    # Live anomaly arithmetic (no package import of engines)
    light = (
        3 * 2 + 5 * 2 * (2 - 6),
        3 * 16 + 5 * 16 * (2 - 6),
        3 * 16 + 5 * 16 * (2**3 + (-6) ** 3),
    )
    charges = [tuple(x) for x in golden["minimality"]["canonical_charges"]]
    heavy = (
        2 * sum(x + y for x, y in charges),
        16 * sum(x + y for x, y in charges),
        16 * sum(x**3 + y**3 for x, y in charges),
    )
    total = tuple(a + b for a, b in zip(light, heavy))
    assert list(light) == golden["anomalies"]["light"], light
    assert list(heavy) == golden["anomalies"]["heavy"], heavy
    assert list(total) == golden["anomalies"]["total"], total
    assert 17**2 - 4 * 76 == golden["minimality"]["one_pair_discriminant"]
    print("[PASS] golden anomaly / minimality anchors", flush=True)


def check_current_root_contract() -> None:
    report = json.loads(
        (ROOT / "EXACT_X_SYMMETRY_CONSISTENCY_GATE_V20.json").read_text(
            encoding="utf-8"
        )
    )
    scaffold = report["executable_scaffold_contract"]
    external = report["external_model_validation"]
    repository_manifest = report["repository_external_input_manifest"]
    assert report["n_failed"] == 0 and report["overall_state"] == "BLOCKED"
    assert report["static_contract_consistent"] is True
    assert report["contract_consistent"] is False
    assert (
        report["blocker"]
        == "AUTHORITATIVE_GAUGED_U1X_EXTERNAL_SARAH_EXECUTION_REQUIRED"
    )
    assert scaffold["model_syntax_class"] == "sarah_native"
    assert scaffold["legacy_pseudo_sarah_grammar"] is False
    assert scaffold["tool_native_sarah_syntax"] is True
    assert scaffold["statically_executable_model_contract"] is True
    assert repository_manifest["valid"] is True
    assert external["valid"] is False
    assert external["checks"]["external_process_was_executed"] is False
    assert external["checks"]["captured_process_log_is_hash_bound"] is False
    print(
        "[PASS] root contract is statically native and honestly BLOCKED only on "
        "missing bound external SARAH evidence",
        flush=True,
    )


def main() -> int:
    print("=== v20 pristine replication ===", flush=True)
    check_golden_anchors()
    run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    run([sys.executable, "audit_v20_errors.py"])
    run([sys.executable, "so10_axion_v20_engine.py", "--output", "so10_axion_v20_verdict.json"])
    run([sys.executable, "exact_x_symmetry_consistency_gate_v20.py"])
    check_current_root_contract()
    run([sys.executable, "sarah_pyrate_210n_model_file_v20.py"])
    run([sys.executable, "gauged_u1x_scalar_contract_v20.py", "--write"])
    run([sys.executable, "g1_exact_declared_symmetry_character_census_v20.py", "--write"])
    run([sys.executable, "exact_gauged_u1x_g1_component_tensor_closure_v20.py"])
    run(
        [
            sys.executable,
            "exact_gauged_u1x_stationarity_rank_certificate_v20.py",
            "--write",
        ]
    )
    run([sys.executable, "gauged_u1x_g2_derivative_audit_v20.py"])
    run(
        [
            sys.executable,
            "exact_gauged_u1x_physical_quotient_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_pd_rank_certificate_v20.py",
            "--recompute-heavy",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_a_square_recoupling_v20.py",
            "--recompute",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_sos_bfb_stationarity_v20.py",
            "--recompute",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_global_counterexample_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_kernel_quartic_bound_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_replacement_stationary_orbit_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_delta_pd_sos_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_delta_hsx_extension_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_delta_hsx_exact_hessian_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_phi_orbit_lemma_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_phi_local_component_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_phi_su3_slice_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_phi_self_zero_global_signed_kaehler_classification_v20.py",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_equality_orbit_v20.py",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_fixed_f_offkernel_bound_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_max_negative_zero_residual_bound_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_max_negative_full_residual_bound_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_max_negative_rank1_su3_slice_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20.py",
        ]
    )
    run(
        [
            sys.executable,
            "-B",
            "corrected_rank1_publication_v21/freeze_exact_gauged_u1x_g3_rank1_su4_corrected_publication_v21.py",
            "--check",
        ]
    )
    run(
        [
            sys.executable,
            "-B",
            "corrected_rank1_publication_v21/exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_primal_v21.py",
            "--check",
        ]
    )
    run(
        [
            sys.executable,
            "-B",
            "corrected_rank1_publication_v21/verify_exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_primal_v21.py",
        ]
    )
    run(
        [
            sys.executable,
            "-B",
            "corrected_rank1_publication_v21/verify_exact_gauged_u1x_g3_rank1_su4_corrected_fixed_endpoint_theorem_v21.py",
        ]
    )
    run(
        [
            sys.executable,
            "-B",
            "corrected_rank1_endpoint_v21.py",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_chiral_global_gap_reduction_v20.py",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_alternative_global_sos_audit_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "gauged_u1x_g3_sos_candidate_v20.py",
            "--recompute-heavy",
        ]
    )
    run([sys.executable, "gauged_u1x_g3_stability_v20.py"])
    run(
        [
            sys.executable,
            "gauged_u1x_g3_corrected_common_kernel_v20.py",
            "--recompute-heavy",
        ]
    )
    run(
        [
            sys.executable,
            "exact_hsigma_current_endomorphism_dimension6_stabilizer_v20.py",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_eft_current_kernel_stabilized_global_v20.py",
        ]
    )
    run([sys.executable, "final_g3_eft_acceptance_gate_v20.py"])
    run([sys.executable, "final_g4_eft_mathematical_gate_v20.py"])
    run([sys.executable, "final_g5_eft_mathematical_gate_v20.py"])
    run([sys.executable, "exact_eft_physical_scalar_spectrum_v20.py"])
    run([sys.executable, "final_g6_eft_mathematical_gate_v20.py"])
    run([sys.executable, "g1_g8_gate_ledger_v20.py"])
    run([sys.executable, "final_g3_acceptance_gate_v20.py"])
    run([sys.executable, "g1_g8_execution_roadmap_v20.py"])
    run([sys.executable, "authoritative_full_model_gate_v20.py"])
    run([sys.executable, "falsify_v20.py"])
    run([sys.executable, "run_v20_external_next_steps.py"])
    run([sys.executable, "run_v20_referee_next.py"])
    run([sys.executable, "extensive_confirm_falsify_v20.py"])
    run([sys.executable, "next_physics_analysis_v20.py"])
    run([sys.executable, "literature_sweep_150uev_v20.py"])
    run([sys.executable, "home_public_37ghz_search_v20.py"])
    run([sys.executable, "gravitas_axion_v20_37ghz.py"])
    run([sys.executable, "public_data_indirect_audit_v20.py"])
    run([sys.executable, "full_fermion_matching_v20.py"])
    run([sys.executable, "tan_beta_profile_v20.py"])
    run([sys.executable, "verify_tan_beta_profile_semantics.py"])
    run([sys.executable, "reanalysis_portal_beta_v20.py"])
    run([sys.executable, "portal_tensors_abcd_v20.py"])
    run([sys.executable, "physical_cf_matching_v20.py"])
    run([sys.executable, "global_flavour_fit_v20.py", "--no-write"])
    run([sys.executable, "cmb_public_data_pipeline_v20.py"])
    run([sys.executable, "empirical_roadmap_lock_v20.py"])
    run([sys.executable, "next_phenomenology_lock_v20.py"])
    run([sys.executable, "close_open_gaps_v20.py"])
    run(
        [
            sys.executable,
            "theory_validation_matrix_v20.py",
            "--expect-blocked",
            "--no-write",
        ]
    )
    run(
        [
            sys.executable,
            "theory_confirmation_verdict_v20.py",
            "--expect-blocked",
            "--no-write",
        ]
    )
    run(
        [
            sys.executable,
            "ultimate_theory_gate_v20.py",
            "--expect-blocked",
            "--no-write",
        ]
    )
    run([sys.executable, "-m", "unittest", "discover", "-v"])
    run(
        [
            sys.executable,
            "-B",
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "test_exact_x_symmetry_consistency_gate_v20.py",
            "test_g1_exact_declared_symmetry_character_census_v20.py",
            "test_exact_gauged_u1x_g1_component_tensor_closure_v20.py",
            "test_gauged_u1x_scalar_contract_v20.py",
            "test_gauged_u1x_g2_derivative_audit_v20.py",
            "test_exact_gauged_u1x_stationarity_rank_certificate_v20.py",
            "test_exact_gauged_u1x_physical_quotient_v20.py",
            "test_exact_gauged_u1x_g3_pd_rank_certificate_v20.py",
            "test_exact_gauged_u1x_g3_a_square_recoupling_v20.py",
            "test_exact_gauged_u1x_g3_sos_bfb_stationarity_v20.py",
            "test_exact_gauged_u1x_g3_global_counterexample_v20.py",
            "test_exact_gauged_u1x_g3_kernel_quartic_bound_v20.py",
            "test_exact_gauged_u1x_g3_replacement_stationary_orbit_v20.py",
            "test_exact_gauged_u1x_g3_su5_delta_pd_sos_v20.py",
            "test_exact_gauged_u1x_g3_su5_delta_hsx_extension_v20.py",
            "test_exact_gauged_u1x_g3_su5_delta_hsx_exact_hessian_v20.py",
            "test_exact_gauged_u1x_g3_su5_phi_orbit_lemma_v20.py",
            "test_exact_gauged_u1x_g3_su5_phi_local_component_v20.py",
            "test_exact_gauged_u1x_g3_su5_phi_su3_slice_v20.py",
            "test_exact_phi_zero_degree8_conductor_identity_v20.py",
            "test_exact_phi_zero_cubic_cauchy_bridge_v20.py",
            "test_exact_phi_self_zero_global_sextic_syzygy_v20.py",
            "test_exact_phi_self_zero_global_signed_kaehler_classification_v20.py",
            "test_exact_gauged_u1x_g3_su5_equality_orbit_v20.py",
            "test_exact_gauged_u1x_g3_su5_fixed_f_offkernel_bound_v20.py",
            "test_exact_gauged_u1x_g3_su5_max_negative_zero_residual_bound_v20.py",
            "test_exact_gauged_u1x_g3_su5_max_negative_full_residual_bound_v20.py",
            "test_exact_gauged_u1x_g3_su5_max_negative_rank1_su3_slice_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20.py",
            "corrected_rank1_publication_v21/test_exact_gauged_u1x_g3_rank1_su4_corrected_publication_v21.py",
            "test_corrected_rank1_endpoint_v21.py",
            "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py",
            "test_exact_gauged_u1x_g3_su5_chiral_global_gap_reduction_v20.py",
            "test_exact_gauged_u1x_g3_alternative_global_sos_audit_v20.py",
            "test_exact_hsigma_current_endomorphism_dimension6_stabilizer_v20.py",
            "test_exact_gauged_u1x_g3_su5_eft_current_kernel_stabilized_global_v20.py",
            "test_final_g3_eft_acceptance_gate_v20.py",
            "test_final_g4_eft_mathematical_gate_v20.py",
            "test_final_g5_eft_mathematical_gate_v20.py",
            "test_exact_eft_physical_scalar_spectrum_v20.py",
            "test_final_g6_eft_mathematical_gate_v20.py",
            "test_g1_g8_gate_ledger_v20.py",
            "test_final_g3_acceptance_gate_v20.py",
            "test_gauged_u1x_g3_sos_candidate_v20.py",
            "test_gauged_u1x_g3_stability_v20.py",
            "test_gauged_u1x_g3_corrected_common_kernel_v20.py",
            "test_g1_g8_execution_roadmap_v20.py",
            "test_theory_validation_matrix_v20.py",
        ]
    )
    run(
        [
            sys.executable,
            "-B",
            "corrected_rank1_publication_v21/freeze_exact_gauged_u1x_g3_rank1_su4_corrected_publication_v21.py",
            "--check",
        ]
    )
    print("=== REPLICATION PASS (SCIENTIFIC STATE: BLOCKED) ===", flush=True)
    print(
        "Passing replication means the fail-closed snapshot is reproducible. "
        "It does not validate the manuscript model or claim a discovery.",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
