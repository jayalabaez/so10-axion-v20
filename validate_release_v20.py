#!/usr/bin/env python3
"""Fail-closed release gate for the combined v17/v19/v20 package."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

import g1_g8_gate_ledger_v20 as gate_ledger


ROOT = Path(__file__).resolve().parent
MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
V17_ENGINE = ROOT / "so10_axion_v17_engine.py"
V19_ENGINE = ROOT / "so10_axion_v19_engine.py"
V20_ENGINE = ROOT / "so10_axion_v20_engine.py"
V17_VERDICT = ROOT / "so10_axion_v17_verdict.json"
V19_VERDICT = ROOT / "so10_axion_v19_verdict.json"
V20_VERDICT = ROOT / "so10_axion_v20_verdict.json"
TEX = ROOT / "axion_so10_theory_v20.tex"
PDF = ROOT / "axion_so10_theory_v20.pdf"
LOG = ROOT / "axion_so10_theory_v20.log"

# Files that complete the script/test/report bundles for the current exact-X
# G1--G3 release chain and its reproducibility gates.  Keep paths relative so
# the checksum manifest is portable across checkout locations and platforms.
FINAL_THEOREM_CORE_PATHS: tuple[str, ...] = (
    ".gitattributes",
    "AUTHORITATIVE_FULL_MODEL_GATE_V20.md",
    "EXACT_X_SYMMETRY_CONSISTENCY_GATE_V20.md",
    "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_RANK1_SU3_SLICE_V20.json",
    "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_RANK1_SU3_SLICE_V20.md",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_STABILIZER_V20.json",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_STABILIZER_V20.md",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_INTERTWINERS_V20.json",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_INTERTWINERS_V20.md",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_ALIGNED_CARRIERS_V20.json",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_ALIGNED_CARRIERS_V20.md",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_QUADRATIC_BASIS_V20.json",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_QUADRATIC_BASIS_V20.md",
    "G1_EXACT_DECLARED_SYMMETRY_CHARACTER_CENSUS_V20.json",
    "G1_EXACT_DECLARED_SYMMETRY_CHARACTER_CENSUS_V20.md",
    "G1_G8_EXECUTION_ROADMAP_V20.md",
    "G1_G8_GATE_LEDGER_V20.md",
    "GAUGED_U1X_SCALAR_CONTRACT_V20.md",
    "REPLICATE.md",
    "THEORY_CONFIRMATION_VERDICT.md",
    "THEORY_VALIDATION_MATRIX_V20.md",
    "ULTIMATE_THEORY_GATE_V20.md",
    "ULTIMATE_THEORY_GATE_V20_SCOPE.md",
    "VALIDATION_EXECUTION_V20.md",
    "VALIDATION_EXECUTION_V20_VERDICT.json",
    "g1_exact_declared_symmetry_character_census_v20.py",
    "exact_gauged_u1x_g3_su5_max_negative_rank1_su3_slice_v20.py",
    "exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py",
    "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py",
    "exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py",
    "exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py",
    "prepare_validation_artifacts_v20.py",
    "replicate.py",
    "test_authoritative_full_model_gate_v20.py",
    "test_exact_x_symmetry_consistency_gate_v20.py",
    "test_exact_gauged_u1x_g3_su5_max_negative_rank1_su3_slice_v20.py",
    "test_exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py",
    "test_exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py",
    "test_exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py",
    "test_exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py",
    "test_g1_exact_declared_symmetry_character_census_v20.py",
    "test_g1_g8_execution_roadmap_v20.py",
    "test_g1_g8_gate_ledger_v20.py",
    "test_gauged_u1x_scalar_contract_v20.py",
    "test_prepare_validation_artifacts_v20.py",
    "test_theory_validation_matrix_v20.py",
    "test_ultimate_theory_gate_v20.py",
    "test_validate_release_v20.py",
)


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    environment = os.environ.copy()
    environment["SOURCE_DATE_EPOCH"] = "1785638400"
    for name in (
        "OPENBLAS_NUM_THREADS",
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
    ):
        environment[name] = "1"
    subprocess.run(command, cwd=ROOT, check=True, env=environment)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def rank1_su4_release_predicates(
    stabilizer_report: dict,
    intertwiners_report: dict,
    aligned_report: dict,
    quadratic_report: dict,
) -> tuple[bool, bool, bool, bool]:
    """Return exact, fail-closed infrastructure predicates for the release."""
    stabilizer_exact = gate_ledger._rank1_su4_stabilizer_infrastructure_exact(
        stabilizer_report
    )
    intertwiners_exact = gate_ledger._rank1_su4_phi210_intertwiners_exact(
        intertwiners_report,
        stabilizer_report,
    )
    aligned_exact = gate_ledger._rank1_su4_aligned_carriers_exact(
        aligned_report, intertwiners_report, stabilizer_report
    )
    quadratic_exact = gate_ledger._rank1_su4_phi210_quadratic_basis_exact(
        quadratic_report, stabilizer_report, intertwiners_report, aligned_report
    )
    return stabilizer_exact, intertwiners_exact, aligned_exact, quadratic_exact


def write_checksums(files: list[Path], *, root: Path | None = None) -> None:
    repository_root = (ROOT if root is None else root).resolve()
    entries: list[tuple[str, Path]] = []
    for path in files:
        resolved = path.resolve()
        try:
            relative = resolved.relative_to(repository_root).as_posix()
        except ValueError as exc:
            raise ValueError(
                f"checksum path is outside repository: {resolved}"
            ) from exc
        entries.append((relative, resolved))

    names = [name for name, _ in entries]
    require(len(names) == len(set(names)), "duplicate release-core checksum path")
    lines = []
    for relative, path in sorted(entries):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {relative}")
    (repository_root / "SHA256SUMS").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def main() -> int:
    run([sys.executable, "-m", "compileall", "-q", str(ROOT)])

    run(
        [
            sys.executable,
            str(V17_ENGINE),
            "--trials",
            "100000",
            "--output",
            str(V17_VERDICT),
        ]
    )
    v17 = json.loads(V17_VERDICT.read_text())
    require(v17["n_checks_total"] == 65, "v17 check count changed")
    require(v17["n_checks_failed"] == 0 and v17["failures"] == [], "v17 engine failed")

    run([sys.executable, str(V19_ENGINE), "--output", str(V19_VERDICT)])
    v19 = json.loads(V19_VERDICT.read_text())
    require(v19["n_checks_total"] == 59, "v19 check count changed")
    require(v19["n_checks_failed"] == 0 and v19["failures"] == [], "v19 engine failed")
    require(
        v19["uv_completion"]["quality_overcatalogue"]["minimum"]["P"] == 13,
        "v19 historical P=13 regression changed",
    )

    run([sys.executable, str(V20_ENGINE), "--output", str(V20_VERDICT)])
    v20 = json.loads(V20_VERDICT.read_text())
    require(v20["n_checks_total"] == 42, "v20 check count changed")
    require(v20["n_checks_failed"] == 0 and v20["failures"] == [], "v20 engine failed")
    require(
        v20["completion"]["quality_overcatalogue"]["minimum"]["P"] == 8,
        "v20 P=8 threshold result changed",
    )
    require(
        v20["completion"]["minimality"]["minimum_number_of_pairs"] == 3,
        "v20 three-pair minimum changed",
    )
    require(
        v20["amplitudes"]["dominant_computed_unit_coefficient_term"]
        == "v20_U1X_direct_scalar_dimension21",
        "dominant v20 computed term changed",
    )
    require(
        v20["completion"]["running"]["continuous_from_spectator_corrected_alpha_GUT"][
            "conservative"
        ]["landau_pole_below_MPl"],
        "continuous Spin(10) soft-falsification flag missing",
    )

    run([sys.executable, "exact_x_symmetry_consistency_gate_v20.py"])
    run([sys.executable, "sarah_pyrate_210n_model_file_v20.py"])
    run([sys.executable, "gauged_u1x_scalar_contract_v20.py", "--write"])
    run([sys.executable, "g1_exact_declared_symmetry_character_census_v20.py", "--write"])
    run(
        [
            sys.executable,
            "exact_gauged_u1x_stationarity_rank_certificate_v20.py",
            "--write",
        ]
    )
    run([sys.executable, "gauged_u1x_g2_derivative_audit_v20.py", "--write"])
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
            "exact_gauged_u1x_g3_su5_equality_orbit_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "exact_gauged_u1x_g3_su5_chiral_global_gap_reduction_v20.py",
            "--write",
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
            "--write",
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
            "exact_gauged_u1x_g3_alternative_global_sos_audit_v20.py",
            "--write",
        ]
    )
    run(
        [
            sys.executable,
            "gauged_u1x_g3_sos_candidate_v20.py",
            "--recompute-heavy",
            "--write",
        ]
    )
    run([sys.executable, "gauged_u1x_g3_stability_v20.py", "--write"])
    run(
        [
            sys.executable,
            "gauged_u1x_g3_corrected_common_kernel_v20.py",
            "--recompute-heavy",
            "--write",
        ]
    )
    run([sys.executable, "g1_g8_gate_ledger_v20.py", "--write"])
    run([sys.executable, "final_g3_acceptance_gate_v20.py", "--write"])
    run([sys.executable, "g1_g8_execution_roadmap_v20.py", "--write"])
    run([sys.executable, "authoritative_full_model_gate_v20.py"])
    run([sys.executable, "theory_validation_matrix_v20.py", "--expect-blocked"])
    run([sys.executable, "theory_confirmation_verdict_v20.py", "--expect-blocked"])
    run([sys.executable, "ultimate_theory_gate_v20.py", "--expect-blocked"])
    contract = json.loads(
        (ROOT / "EXACT_X_SYMMETRY_CONSISTENCY_GATE_V20.json").read_text()
    )
    model_scaffold_audit = json.loads(
        (ROOT / "SARAH_PYRATE_MODEL_FILE_V20_VERDICT.json").read_text()
    )
    gauged_g2 = json.loads(
        (ROOT / "GAUGED_U1X_G2_DERIVATIVE_AUDIT_V20.json").read_text()
    )
    exact_rank = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_STATIONARITY_RANK_CERTIFICATE_V20.json"
        ).read_text()
    )
    exact_quotient = json.loads(
        (ROOT / "EXACT_GAUGED_U1X_PHYSICAL_QUOTIENT_V20.json").read_text()
    )
    exact_pd_rank = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_PD_RANK_CERTIFICATE_V20.json"
        ).read_text()
    )
    exact_a_square = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_A_SQUARE_RECOUPLING_V20.json"
        ).read_text()
    )
    exact_sos = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_SOS_BFB_STATIONARITY_V20.json"
        ).read_text()
    )
    exact_global_counterexample = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_GLOBAL_COUNTEREXAMPLE_V20.json"
        ).read_text()
    )
    exact_kernel_bound = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_KERNEL_QUARTIC_BOUND_V20.json"
        ).read_text()
    )
    exact_replacement = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_REPLACEMENT_STATIONARY_ORBIT_V20.json"
        ).read_text()
    )
    exact_su5_pd = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_PD_SOS_V20.json"
        ).read_text()
    )
    exact_su5_hsx = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXTENSION_V20.json"
        ).read_text()
    )
    exact_su5_hsx_hessian = json.loads(
        (
            ROOT
            / "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXACT_HESSIAN_V20.json"
        ).read_text()
    )
    exact_su5_phi_orbit = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_ORBIT_LEMMA_V20.json"
        ).read_text()
    )
    exact_su5_phi_local = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_LOCAL_COMPONENT_V20.json"
        ).read_text()
    )
    exact_su5_phi_su3 = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_SU3_SLICE_V20.json"
        ).read_text()
    )
    exact_su5_equality = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_SU5_EQUALITY_ORBIT_V20.json"
        ).read_text()
    )
    exact_su5_gap = json.loads(
        (
            ROOT
            / "EXACT_GAUGED_U1X_G3_SU5_CHIRAL_GLOBAL_GAP_REDUCTION_V20.json"
        ).read_text()
    )
    exact_fixed_f_bound = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_SU5_FIXED_F_OFFKERNEL_BOUND_V20.json"
        ).read_text()
    )
    exact_max_negative_bound = json.loads(
        (
            ROOT
            / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_ZERO_RESIDUAL_BOUND_V20.json"
        ).read_text()
    )
    exact_max_negative_full_bound = json.loads(
        (
            ROOT
            / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_FULL_RESIDUAL_BOUND_V20.json"
        ).read_text()
    )
    exact_max_negative_rank1_su3_slice = json.loads(
        (
            ROOT
            / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_RANK1_SU3_SLICE_V20.json"
        ).read_text()
    )
    exact_rank1_su4_stabilizer = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_STABILIZER_V20.json"
        ).read_text()
    )
    exact_rank1_su4_phi210_intertwiners = json.loads(
        (
            ROOT
            / "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_INTERTWINERS_V20.json"
        ).read_text()
    )
    exact_rank1_su4_aligned_carriers = json.loads(
        (
            ROOT
            / "EXACT_GAUGED_U1X_G3_RANK1_SU4_ALIGNED_CARRIERS_V20.json"
        ).read_text()
    )
    exact_rank1_su4_phi210_quadratic_basis = json.loads(
        (
            ROOT
            / "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_QUADRATIC_BASIS_V20.json"
        ).read_text()
    )
    exact_alternative_sos = json.loads(
        (
            ROOT / "EXACT_GAUGED_U1X_G3_ALTERNATIVE_GLOBAL_SOS_AUDIT_V20.json"
        ).read_text()
    )
    final_g3 = json.loads((ROOT / "FINAL_G3_ACCEPTANCE_GATE_V20.json").read_text())
    g3_candidate = json.loads(
        (ROOT / "GAUGED_U1X_G3_SOS_CANDIDATE_V20.json").read_text()
    )
    gauged_g3 = json.loads(
        (ROOT / "GAUGED_U1X_G3_STABILITY_V20.json").read_text()
    )
    corrected_common_kernel = json.loads(
        (ROOT / "GAUGED_U1X_G3_CORRECTED_COMMON_KERNEL_V20.json").read_text()
    )
    matrix = json.loads(
        (ROOT / "THEORY_VALIDATION_MATRIX_V20_VERDICT.json").read_text()
    )
    ultimate = json.loads(
        (ROOT / "ULTIMATE_THEORY_GATE_V20_VERDICT.json").read_text()
    )
    require(contract["n_failed"] == 0, "authoritative X-contract audit failed")
    require(
        not contract["contract_consistent"]
        and contract["static_contract_consistent"] is True
        and contract["blocker"]
        == "AUTHORITATIVE_GAUGED_U1X_EXTERNAL_SARAH_EXECUTION_REQUIRED",
        "exact-X external-execution blocker was misclassified",
    )
    root_scaffold = contract["executable_scaffold_contract"]
    root_external = contract["external_model_validation"]
    require(
        root_scaffold["model_syntax_class"]
        == "sarah_native"
        and root_scaffold["legacy_pseudo_sarah_grammar"] is False
        and root_scaffold["tool_native_sarah_syntax"] is True
        and root_scaffold["statically_executable_model_contract"] is True
        and root_scaffold["scalar_charges_match_manuscript"] is True
        and root_scaffold["fermion_catalogue_exact"] is True
        and root_scaffold["lagrangian"][
            "registered_in_GaugeES_LagrangianInput"
        ]
        is True,
        "native SARAH static contract failed",
    )
    require(
        root_external["valid"] is False
        and root_external["checks"]["captured_process_log_is_hash_bound"]
        is False
        and contract["repository_external_input_manifest"]["valid"] is True,
        "external model evidence or repository input manifest was misclassified",
    )
    require(
        model_scaffold_audit["n_failed"] == 0
        and model_scaffold_audit["overall_state"] == "BLOCKED"
        and model_scaffold_audit["status"]
        == "SARAH_NATIVE_STATIC_CONTRACT__EXTERNAL_VALIDATION_BLOCKED"
        and model_scaffold_audit["flag"]["sarah_model_tool_native"] is True
        and model_scaffold_audit["flag"][
            "sarah_static_contract_consistent"
        ]
        is True
        and model_scaffold_audit["flag"]["pyrate_model_tool_native"] is False
        and model_scaffold_audit["flag"]["charge_locks_encoded"] is True
        and model_scaffold_audit["flag"]["external_validation_v2_valid"] is False
        and model_scaffold_audit["flag"][
            "live_sarah_or_pyrate_executable_run"
        ]
        is False,
        "native SARAH static/external execution boundary changed",
    )
    require(
        exact_rank["n_failed"] == 0
        and exact_rank["certified"] is True
        and exact_rank["rank"] == 13
        and exact_rank["nullity"] == 38
        and exact_rank["checks"]["exact_rank_upper_bound_13_certified"] is True
        and exact_rank["checks"]["exact_rank_lower_bound_13_certified"] is True,
        "standalone exact stationarity-rank certificate failed",
    )
    require(gauged_g2["n_failed"] == 0, "gauged U(1)_X G2 audit failed")
    require(
        gauged_g2["counts"]["invariant_directions"] == 44
        and gauged_g2["counts"]["real_parameters"] == 51
        and gauged_g2["counts"]["real_field_dimension"] == 486,
        "gauged U(1)_X G2 dimensions changed",
    )
    require(
        gauged_g2["stationary_Hessian_bridge"]["promoted_stationarity_matrix"][
            "rank"
        ]
        == 13
        and gauged_g2["stationary_Hessian_bridge"][
            "promoted_stationarity_matrix"
        ]["nullity"]
        == 38,
        "gauged U(1)_X G2 stationarity rank/nullity changed",
    )
    require(
        gauged_g2["flags"]["exact_Delta_R_projector_zero_certificate"] is True
        and gauged_g2["flags"][
            "exact_projector_zero_corrected_normalized_SVD_rank_13"
        ] is True
        and gauged_g2["flags"]["stationarity_rank_13_exactly_certified"] is True
        and gauged_g2["flags"]["stationarity_nullity_38_exactly_certified"] is True
        and gauged_g2["flags"][
            "stationarity_rank_upper_bound_13_exactly_certified"
        ]
        is True
        and gauged_g2["flags"][
            "exact_Sigma_conventions_bound_to_live_compiler_chart"
        ]
        is True
        and gauged_g2["flags"]["exact_Phi_int64_preflight_safety_certified"]
        is True
        and gauged_g2["flags"][
            "compiler_gradients_bound_to_exact_nonzero_13x13_minor"
        ]
        is True
        and gauged_g2["flags"][
            "exact_informed_13_row_constraint_representation_ready"
        ]
        is True
        and gauged_g2["flags"][
            "exact_P24_trace_288_bound_to_compiled_dense_Hessian"
        ]
        is True,
        "gauged U(1)_X G2 rank-evidence scope changed",
    )
    require(
        exact_quotient["model_contract_id"] == MODEL_CONTRACT_ID
        and exact_quotient["certified"] is True
        and exact_quotient["exact_certificate"]["certified"] is True
        and exact_quotient["live_compiler_binding"]["compiler_binding_passes"]
        is True
        and exact_quotient["gauge_quotient_dimension_including_axion"] == 449
        and exact_quotient["massive_transverse_quotient_dimension"] == 448,
        "standalone exact physical-quotient certificate failed",
    )
    require(
        exact_a_square["n_failed"] == 0
        and exact_a_square["status"] == "EXACT_A_SQUARE_RECOUPLING_CERTIFIED"
        and exact_a_square["certificate"]["unique_weights"]
        == ["40", "72", "28", "-8", "-12", "12"]
        and exact_a_square["certificate"]["identity_residuals"]
        == ["0", "0", "0", "0", "0", "0"]
        and exact_a_square["certificate"]["source_binding_exact"] is True
        and exact_a_square["certificate"]["proof_grade"] is True
        and exact_a_square["flags"][
            "A_square_recoupling_exactly_source_bound"
        ]
        is True
        and exact_a_square["flags"]["G3_closed"] is False,
        "exact A-square recoupling certificate failed or was over-promoted",
    )
    require(
        exact_sos["n_failed"] == 0
        and exact_sos["status"]
        == "EXACT_COMPLETE_POTENTIAL_BFB_AND_SELECTED_STATIONARITY_CERTIFIED"
        and exact_sos["overall_state"] == "CLOSED_SUBPROBLEM"
        and exact_sos["model_contract_id"] == MODEL_CONTRACT_ID
        and exact_sos["coefficient_binding"]["nonzero_parameter_count"] == 27
        and exact_sos["boundedness"]["source_binding_exact"] is True
        and exact_sos["stationarity"]["source_binding_exact"] is True
        and exact_sos["flags"][
            "complete_27_parameter_SOS_identity_exactly_source_bound"
        ]
        is True
        and exact_sos["flags"]["complete_potential_BFB_exactly_certified"]
        is True
        and exact_sos["flags"][
            "selected_vacuum_stationarity_exactly_certified"
        ]
        is True
        and exact_sos["flags"]["selected_vacuum_global_minimum_certified"]
        is False
        and exact_sos["flags"]["selected_vacuum_unique_modulo_symmetry"]
        is False
        and exact_sos["flags"]["full_Hessian_exactly_source_bound"] is False
        and exact_sos["flags"]["strict_local_minimum_certified"] is False
        and exact_sos["flags"]["G3_closed"] is False,
        "exact SOS/BFB/stationarity subcertificate failed or over-promoted",
    )
    pd_ranks = exact_pd_rank["direct_exact_ranks"]
    pd_extension = exact_pd_rank["exact_full_kernel_argument"]
    require(
        exact_pd_rank["n_failed"] == 0
        and exact_pd_rank["status"]
        == "DIRECT_EXACT_TRANSVERSE_HESSIAN_PASS__SOS_AND_GLOBAL_EXTREMA_EXTERNAL"
        and exact_pd_rank["overall_state"] == "OPEN"
        and pd_ranks["K"] == {"rank": 278, "nullity": 184, "PSD": True}
        and pd_ranks["H_Phi"] == {"rank": 186, "nullity": 276, "PSD": True}
        and pd_ranks["H_Phi_plus_K"]
        == {"rank": 429, "nullity": 33, "PSD": True}
        and pd_extension["exact_P_plus_Delta_gauge_orbit"]["exact_orbit_rank"]
        == 33
        and pd_extension["explicit_quotient_constraint_Jacobian"]["shape"]
        == [26, 24]
        and pd_extension["explicit_quotient_constraint_Jacobian"][
            "exact_rational_rank"
        ]
        == 19
        and pd_extension["exact_full_Hessian_rank"] == 448
        and pd_extension["remaining_kernel_dimension"] == 38
        and pd_extension["source_binding_exact"] is True
        and pd_extension["proof_grade"] is True
        and exact_pd_rank["direct_P_plus_Delta_certificate"][
            "source_binding_exact"
        ]
        is True
        and exact_pd_rank["direct_P_plus_Delta_certificate"]["proof_grade"]
        is True
        and exact_pd_rank["flags"]["conditional_exact_LDL_on_reconstructed_matrix"]
        is False
        and exact_pd_rank["flags"]["direct_exact_source_binding"] is True
        and exact_pd_rank["flags"]["proof_grade_P_plus_Delta_PSD"] is True
        and exact_pd_rank["flags"]["proof_grade_full_rank_448"] is True
        and exact_pd_rank["flags"][
            "strict_transverse_Hessian_positive_certified"
        ]
        is True
        and exact_pd_rank["flags"]["global_minimum_certified"] is False
        and exact_pd_rank["flags"]["global_uniqueness_certified"] is False
        and exact_pd_rank["flags"]["G3_closed"] is False,
        "direct exact P+Delta/full-transverse certificate failed or over-promoted",
    )
    require(
        exact_global_counterexample["n_failed"] == 0
        and exact_global_counterexample["flags"][
            "lower_energy_field_witness_exactly_certified"
        ]
        is True
        and exact_global_counterexample["flags"][
            "selected_vacuum_global_minimum_disproved"
        ]
        is True
        and exact_global_counterexample["flags"]["G3_closed"] is False
        and exact_global_counterexample["flags"]["whole_model_excluded"] is False,
        "exact global counterexample failed or was promoted to a model-wide no-go",
    )
    require(
        exact_kernel_bound["n_failed"] == 0
        and exact_kernel_bound["flags"][
            "fixed_P_strict_local_global_no_go_exact"
        ]
        is True
        and exact_kernel_bound["flags"]["fixed_P_branch_closed_negative"]
        is True
        and exact_kernel_bound["flags"]["G3_closed"] is False
        and exact_kernel_bound["flags"]["whole_model_excluded"] is False,
        "fixed-P exact gap-curvature no-go failed or exceeded its scope",
    )
    require(
        exact_replacement["n_failed"] == 0
        and exact_replacement["flags"][
            "replacement_full_stationarity_exact"
        ]
        is True
        and exact_replacement["flags"][
            "replacement_symmetry_orbit_rank_exact"
        ]
        is True
        and exact_replacement["flags"][
            "replacement_target_gauge_symmetry_correct"
        ]
        is False
        and exact_replacement["flags"][
            "replacement_strict_local_minimum_proof_grade"
        ]
        is False
        and exact_replacement["flags"]["G3_closed"] is False,
        "lower replacement orbit was misclassified",
    )
    su5_scope = exact_su5_pd["scope"]
    require(
        exact_su5_pd["n_failed"] == 0
        and exact_su5_pd["status"]
        == "EXACT_SU5_DELTA_PD_GLOBAL_SOS_CANDIDATE_CERTIFIED"
        and su5_scope["Phi_Sigma_global_minimum_exact"] is True
        and su5_scope["Phi_Sigma_stationarity_exact"] is True
        and su5_scope["SO10_to_SM_stabilizer_dimension_exact"] is True
        and su5_scope["Phi_Sigma_Hessian_rank_429_nullity_33_exact"] is True
        and su5_scope["Phi_Sigma_quotient_strictly_positive_exact"] is True
        and su5_scope["Phi_Sigma_equality_set_locally_one_orbit"] is True
        and su5_scope["full_486_field_stationarity"] is False
        and su5_scope["global_orbit_uniqueness"] is False
        and su5_scope["G3_closed"] is False,
        "SU(5)+Delta exact PD certificate failed or was over-promoted",
    )
    hsx_flags = exact_su5_hsx["flag"]
    hsx_orbit = exact_su5_hsx["chiral_H_candidate"]["exact_orbit"]
    hsx_live = exact_su5_hsx["live_full_gradient_and_quotient_Hessian"]
    require(
        exact_su5_hsx["n_failed"] == 0
        and hsx_flags["real_H_e6_extension_exactly_excluded"] is True
        and hsx_flags["chiral_H_exact_stationary_candidate_constructed"] is True
        and hsx_flags["full_quartic_BFB_certified"] is True
        and hsx_flags["full_global_minimum_certified"] is False
        and hsx_flags["G3_closed"] is False
        and [
            hsx_orbit["SO10_rank"],
            hsx_orbit["SO10_plus_U1X_rank"],
            hsx_orbit["SO10_plus_U1X_plus_PQ_rank"],
        ]
        == [36, 37, 38]
        and hsx_live["transverse_dimension"] == 448
        and hsx_live["proof_grade"] is False
        and hsx_live["negative_transverse_eigenvalues_below_minus_1e_minus_9"]
        == 0
        and hsx_live["zero_transverse_eigenvalues_at_1e_minus_9"] == 0,
        "SU(5)+Delta chiral-H frontier failed or numerical inertia was over-promoted",
    )
    exact_hessian_flags = exact_su5_hsx_hessian["flags"]
    exact_hessian_closed = (
        exact_su5_hsx_hessian["status"]
        == "EXACT_FULL_HESSIAN_RANK_448_NULLITY_38_CERTIFIED"
        and exact_su5_hsx_hessian["overall_state"]
        == "CLOSED_FULL_LOCAL_HESSIAN_SUBPROBLEM"
        and all(
            exact_hessian_flags[name] is True
            for name in (
                "exact_rank_448",
                "exact_nullity_38",
                "exact_PSD",
                "strict_quotient",
                "proof_grade",
                "source_binding",
            )
        )
    )
    exact_hessian_open = (
        exact_su5_hsx_hessian["status"]
        == "EXACT_HESSIAN_CERTIFICATE_INCOMPLETE"
        and exact_su5_hsx_hessian["overall_state"] == "G3_EXACT_LOCAL_TEST_OPEN"
        and exact_hessian_flags["proof_grade"] is False
    )
    require(
        exact_su5_hsx_hessian["model_contract_id"] == MODEL_CONTRACT_ID
        and exact_su5_hsx_hessian.get("n_failed", 0) == 0
        and exact_su5_hsx_hessian["G3_closed"] is False
        and (exact_hessian_closed or exact_hessian_open),
        "SU(5)+Delta exact Hessian audit failed or over-promoted G3",
    )
    phi_orbit_scope = exact_su5_phi_orbit["scope"]
    require(
        exact_su5_phi_orbit["n_failed"] == 0
        and exact_su5_phi_orbit["status"]
        == "LITERAL_SINGLE_ORBIT_LEMMA_REFUTED__SIGNED_GLOBAL_LEMMA_OPEN"
        and exact_su5_phi_orbit["overall_state"]
        == "SHARP_COUNTEREXAMPLE_AND_REDUCTION"
        and exact_su5_phi_orbit["checks"][
            "literal_single_orbit_lemma_is_refuted"
        ]
        is True
        and exact_su5_phi_orbit["checks"][
            "corrected_signed_global_lemma_not_overclaimed"
        ]
        is True
        and phi_orbit_scope["literal_plus_orbit_only_statement_refuted"] is True
        and phi_orbit_scope["complete_SU4_invariant_slice_classified"] is True
        and phi_orbit_scope["all_arbitrary_real_four_forms_classified"] is False
        and phi_orbit_scope["corrected_signed_two_orbit_theorem_proved"] is False
        and phi_orbit_scope["PD_global_equality_orbit_classification_complete"]
        is False
        and phi_orbit_scope["G3_closed"] is False
        and phi_orbit_scope["whole_model_excluded"] is False
        and exact_su5_phi_orbit["corrected_global_lemma"]["proved"] is False,
        "literal Phi orbit refutation/signed-open audit was not reproduced",
    )
    phi_local_scope = exact_su5_phi_local["scope"]
    require(
        exact_su5_phi_local["n_failed"] == 0
        and exact_su5_phi_local["status"]
        == "EXACT_LOCAL_COMPONENT_THEOREM_CLOSED__DISTANT_COMPONENTS_OPEN"
        and exact_su5_phi_local["overall_state"]
        == "LOCAL_COMPONENT_THEOREM_CLOSED"
        and phi_local_scope["plus_F_local_component_classified"] is True
        and phi_local_scope["minus_F_local_component_classified"] is True
        and phi_local_scope["signed_orbit_locally_isolated"] is True
        and phi_local_scope["explicit_neighborhood_radius_available"] is False
        and phi_local_scope["disconnected_distant_components_excluded"] is False
        and phi_local_scope["corrected_signed_global_orbit_theorem_proved"]
        is False
        and phi_local_scope["PD_global_equality_orbit_classification_complete"]
        is False
        and phi_local_scope["G3_closed"] is False
        and phi_local_scope["whole_model_excluded"] is False,
        "signed Phi local-component theorem failed or over-promoted globality",
    )
    phi_su3_scope = exact_su5_phi_su3["scope"]
    phi_su3_checks = exact_su5_phi_su3["checks"]
    require(
        exact_su5_phi_su3["n_failed"] == 0
        and exact_su5_phi_su3["status"]
        == "EXACT_COMPLETE_SU3_FIXED_SLICE_CLASSIFIED__GENERIC_GLOBAL_OPEN"
        and exact_su5_phi_su3["overall_state"] == "SU3_FIXED_SLICE_CLOSED"
        and phi_su3_checks["displayed_space_is_complete_SU3_fixed_space"]
        is True
        and phi_su3_checks["restricted_projector_rowspace_reduced_exactly"]
        is True
        and phi_su3_checks[
            "eight_nondiagonal_directions_have_real_SOS_obstruction"
        ]
        is True
        and phi_su3_checks["complete_SU3_fixed_slice_is_signed_Kahler_orbit"]
        is True
        and phi_su3_scope[
            "complete_16_real_dimensional_SU3_fixed_space_classified"
        ]
        is True
        and phi_su3_scope[
            "all_nonzero_slice_solutions_are_signed_Kahler_squares"
        ]
        is True
        and phi_su3_scope["all_arbitrary_real_four_forms_classified"] is False
        and phi_su3_scope["disconnected_distant_components_excluded"] is False
        and phi_su3_scope["corrected_signed_global_orbit_theorem_proved"] is False
        and phi_su3_scope["G3_closed"] is False
        and phi_su3_scope["whole_model_excluded"] is False,
        "complete SU(3)-fixed Phi slice failed or over-promoted globality",
    )
    equality_scope = exact_su5_equality["scope"]
    equality_lemma = exact_su5_equality["remaining_global_lemma"]
    require(
        exact_su5_equality["n_failed"] == 0
        and equality_scope["fixed_F_Sigma_global_equality_classified"] is True
        and equality_scope[
            "fixed_Delta_diagonal_Phi_global_equality_classified"
        ]
        is True
        and equality_scope["global_equality_orbit_classification_complete"]
        is False
        and equality_lemma["proved"] is False
        and equality_lemma["numerical_search_is_not_a_substitute"] is True
        and equality_scope["G3_closed"] is False,
        "SU(5)+Delta equality classification was not fail-closed",
    )
    gap_flags = exact_su5_gap["flags"]
    require(
        exact_su5_gap["n_failed"] == 0
        and gap_flags["lower_witness_found"] is False
        and gap_flags["conditional_small_positive_beta_route_exists"] is True
        and gap_flags["beta_1_over_20_global_minimum_certified"] is False
        and gap_flags["global_equality_orbits_classified"] is False
        and gap_flags["G3_closed"] is False
        and exact_su5_gap["small_beta_global_reduction"]["hypotheses"][
            "exact_full_486_Hessian_kernel_equals_the_38_symmetry_tangents"
        ]
        is True
        and exact_su5_gap["final_acceptance_test"]["currently_passes"] is False,
        "chiral-H global-gap reduction failed or was over-promoted",
    )
    fixed_f_scope = exact_fixed_f_bound["scope"]
    fixed_f_checks = exact_fixed_f_bound["checks"]
    require(
        exact_fixed_f_bound["n_failed"] == 0
        and exact_fixed_f_bound["status"]
        == "EXACT_FIXED_F_FULL_OFFKERNEL_BETA_GAP_CERTIFIED"
        and exact_fixed_f_bound["overall_state"]
        == "CLOSED_FIXED_F_GLOBAL_SUBPROBLEM"
        and fixed_f_checks["mixed_offkernel_gap_at_least_6_over_5_exact"] is True
        and fixed_f_checks["pure_hplus_current_error_bound_exact"] is True
        and fixed_f_checks["kernel_chirality_cross_zero_exact"] is True
        and fixed_f_checks["cross_block_bound_exact"] is True
        and fixed_f_checks["rational_inside_outside_patch_positive"] is True
        and fixed_f_checks["full_fixed_F_equality_orbit_exact"] is True
        and fixed_f_scope["Phi_fixed_to_F"] is True
        and fixed_f_scope["H_arbitrary"] is True
        and fixed_f_scope["Sigma_arbitrary"] is True
        and fixed_f_scope["beta_equals_1_over_20"] is True
        and fixed_f_scope["global_gap_nonnegative_on_full_fixed_F_stratum"]
        is True
        and fixed_f_scope["equality_is_selected_SU5_flag_orbit"] is True
        and fixed_f_scope["arbitrary_Phi_proved"] is False
        and fixed_f_scope["G3_closed"] is False,
        "fixed-F full off-kernel gap certificate failed or over-promoted G3",
    )
    max_negative_scope = exact_max_negative_bound["scope"]
    max_negative_checks = exact_max_negative_bound["checks"]
    require(
        exact_max_negative_bound["n_failed"] == 0
        and exact_max_negative_bound["status"]
        == "EXACT_PURE_DELTA_MAX_NEGATIVE_MIXED_ZERO_ROUTE_EXCLUDED"
        and exact_max_negative_bound["overall_state"]
        == "CLOSED_PURE_DELTA_MAX_NEGATIVE_MIXED_ZERO_STRATUM__ARBITRARY_PHI_OPEN"
        and exact_max_negative_bound["model_contract_id"]
        == MODEL_CONTRACT_ID
        and max_negative_checks["exact_rank_168_nullity_42"] is True
        and max_negative_checks["kernel_splits_35_plus_7_exactly"] is True
        and max_negative_checks["live_HSX_and_PD_coefficients_bound_exactly"]
        is True
        and max_negative_checks[
            "N_and_C00_C11_contraction_identities_computed_exactly"
        ]
        is True
        and max_negative_checks[
            "Phi_radial_plus_I54_lower_bound_1_over_141"
        ]
        is True
        and max_negative_checks["worst_radial_current_minimum_exact"] is True
        and max_negative_checks["strict_positive_stratum_margin_exact"] is True
        and max_negative_checks[
            "u_zero_and_v_zero_radial_boundaries_closed_exactly"
        ]
        is True
        and exact_max_negative_bound["exact_stratum_gap"]["strict_margin"]
        == "7859/140295000"
        and max_negative_scope[
            "strongest_all_zero_max_negative_route_excluded"
        ]
        is True
        and max_negative_scope[
            "strongest_pure_Delta_mixed_zero_max_negative_route_excluded"
        ]
        is True
        and max_negative_scope[
            "normalized_affine_stratum_requires_u_gt_0_v_gt_0"
        ]
        is True
        and max_negative_scope[
            "u_zero_and_v_zero_boundaries_closed_separately"
        ]
        is True
        and max_negative_scope["nonzero_residual_cancellations_excluded"] is False
        and max_negative_scope["arbitrary_Phi_global_gap_proved"] is False
        and max_negative_scope["G3_closed"] is False,
        "max-negative all-zero-residual certificate failed or over-promoted G3",
    )
    max_negative_full_scope = exact_max_negative_full_bound["scope"]
    max_negative_full_checks = exact_max_negative_full_bound["checks"]
    require(
        exact_max_negative_full_bound["n_failed"] == 0
        and exact_max_negative_full_bound["status"]
        == "EXACT_MAX_NEGATIVE_FULL_RESIDUAL_PURE_DELTA_BOUND_CERTIFIED"
        and exact_max_negative_full_bound["overall_state"]
        == "CLOSED_MAX_NEGATIVE_PURE_DELTA_ARBITRARY_PHI_SUBPROBLEM"
        and exact_max_negative_full_bound["model_contract_id"]
        == MODEL_CONTRACT_ID
        and max_negative_full_scope["Sigma_on_pure_Delta_orbit"] is True
        and max_negative_full_scope["Phi_arbitrary_real_210"] is True
        and max_negative_full_scope["nonzero_Phi_Sigma_residuals_covered"]
        is True
        and max_negative_full_scope["nonzero_chiral_Phi_H_residual_covered"]
        is True
        and max_negative_full_scope["u_v_all_nonnegative"] is True
        and max_negative_full_scope["restricted_gap_global_minimum"] == "1/5000"
        and max_negative_full_scope["arbitrary_Sigma_orientation_proved"]
        is False
        and max_negative_full_scope["G3_closed"] is False
        and all(max_negative_full_checks.values()),
        "max-negative full-residual pure-Delta certificate failed or over-promoted G3",
    )
    rank1_scope = exact_max_negative_rank1_su3_slice["scope"]
    rank1_checks = exact_max_negative_rank1_su3_slice["checks"]
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
    require(
        exact_max_negative_rank1_su3_slice["n_failed"] == 0
        and exact_max_negative_rank1_su3_slice["failed_checks"] == []
        and exact_max_negative_rank1_su3_slice["status"]
        == "EXACT_RANK1_SU3_DANGEROUS_SLICE_BOUND_CERTIFIED"
        and exact_max_negative_rank1_su3_slice["overall_state"]
        == "CLOSED_RANK1_SU3_SLICE__ARBITRARY_RANK1_PHI_OPEN"
        and exact_max_negative_rank1_su3_slice["model_contract_id"]
        == MODEL_CONTRACT_ID
        and rank1_scope["H_fixed_to_h_minus"] is True
        and rank1_scope[
            "Sigma_fixed_to_normalized_explicit_decomposable_pure_spinor"
        ]
        is True
        and rank1_scope["Phi_restricted_to_four_real_SU3_fixed_variables"]
        is True
        and rank1_scope["Phi_slice_real_dimension"] == 4
        and rank1_scope["full_SU3_fixed_space_real_dimension"] == 16
        and rank1_scope["full_SU3_fixed_space_proved"] is False
        and rank1_scope["u_v_arbitrary_nonnegative"] is True
        and rank1_scope["arbitrary_real_Phi"] is False
        and rank1_scope["arbitrary_max_negative_Sigma"] is False
        and rank1_scope["G3_closed"] is False
        and rank1_scope["whole_model_excluded"] is False
        and all(rank1_checks[name] is True for name in rank1_required_checks)
        and rank1_checks["arbitrary_rank1_Phi_proved"] is False
        and rank1_checks["arbitrary_Sigma35_proved"] is False
        and rank1_checks["G3_closed"] is False
        and exact_max_negative_rank1_su3_slice["SOS"][
            "strict_anchor_lower_bound"
        ]
        == "3/200"
        and exact_max_negative_rank1_su3_slice["radial_patch"][
            "restricted_global_minimum"
        ]
        == "1/5000",
        "rank-one SU(3) four-dimensional slice certificate failed or overclaimed G3",
    )
    (
        rank1_su4_stabilizer_exact,
        rank1_su4_phi210_intertwiners_exact,
        rank1_su4_aligned_carriers_exact,
        rank1_su4_phi210_quadratic_basis_exact,
    ) = rank1_su4_release_predicates(
        exact_rank1_su4_stabilizer,
        exact_rank1_su4_phi210_intertwiners,
        exact_rank1_su4_aligned_carriers,
        exact_rank1_su4_phi210_quadratic_basis,
    )
    require(
        rank1_su4_stabilizer_exact,
        "rank-one SU(4) stabilizer infrastructure drifted or overclaimed scope",
    )
    require(
        rank1_su4_phi210_intertwiners_exact,
        (
            "rank-one SU(4) Phi210 intertwiner infrastructure drifted, lost "
            "provenance, or overclaimed scope"
        ),
    )
    require(
        rank1_su4_aligned_carriers_exact,
        "rank-one SU(4) aligned-carrier/real-map certificate drifted or overclaimed scope",
    )
    require(
        rank1_su4_phi210_quadratic_basis_exact,
        "rank-one SU(4) Phi210 invariant quadratic-basis certificate drifted or overclaimed G3",
    )
    alternative_flags = exact_alternative_sos["flags"]
    require(
        exact_alternative_sos["n_failed"] == 0
        and exact_alternative_sos["status"]
        == "ALTERNATIVE_GLOBAL_SOS_AUDIT_COMPLETE__NO_CERTIFIED_REPLACEMENT"
        and exact_alternative_sos["overall_state"] == "G3_GLOBAL_ALTERNATIVE_OPEN"
        and alternative_flags[
            "all_vanishing_45_current_Gram_completion_excluded"
        ]
        is True
        and alternative_flags["all_vanishing_affine_SOS_completion_excluded"]
        is True
        and alternative_flags[
            "all_vanishing_unique_chiral_quartic_completion_excluded"
        ]
        is True
        and alternative_flags[
            "nonvanishing_residual_gradient_cancellation_excluded"
        ]
        is False
        and alternative_flags["different_vacuum_orbit_excluded"] is False
        and alternative_flags["globally_certifiable_alternative_found"] is False
        and alternative_flags["G3_closed"] is False
        and alternative_flags["whole_model_excluded"] is False,
        "alternative global-SOS audit failed or overclaimed its no-go scope",
    )
    require(
        final_g3["n_failed"] == 0
        and final_g3["overall_state"] == "OPEN"
        and final_g3["classification"]["mathematical_G3_closed"] is False
        and final_g3["classification"]["release_G3_verified"] is False
        and final_g3["classification"]["theory_still_viable"] is True,
        "final G3 acceptance gate failed or promoted incomplete evidence",
    )
    candidate_coefficients = g3_candidate["coefficient_vector"]
    require(
        g3_candidate["n_failed"] == 0
        and candidate_coefficients["nonzero_count"] == 27
        and candidate_coefficients["maximum_absolute_coefficient"] == 73 / 8
        and candidate_coefficients["symbolic_nonzero"][
            "lambda::O48_B01_Phi_self_quartics"
        ]
        == "-21/200"
        and g3_candidate["flags"][
            "positive_J0_normalization_is_without_loss_of_generality"
        ]
        is False
        and g3_candidate["flags"][
            "P_plus_Delta_Qsqrt2_component_LDL_conditional"
        ]
        is False
        and g3_candidate["flags"][
            "A_square_recoupling_exactly_source_bound"
        ]
        is True
        and g3_candidate["flags"]["complete_potential_BFB_exactly_certified"]
        is True
        and g3_candidate["flags"][
            "selected_vacuum_stationarity_exactly_compiler_certified"
        ]
        is True
        and g3_candidate["flags"]["full_448_kernel_count_conditional"] is False
        and g3_candidate["flags"][
            "P_plus_Delta_source_binding_exactly_certified"
        ]
        is True
        and g3_candidate["flags"]["full_448_kernel_count_exact"] is True
        and g3_candidate["flags"]["full_448_PSD_feasibility_certified"] is True
        and g3_candidate["flags"]["strict_local_minimum_certified"] is True
        and g3_candidate["flags"][
            "selected_vacuum_global_minimum_certified"
        ]
        is False
        and g3_candidate["flags"][
            "selected_vacuum_global_minimum_disproved"
        ]
        is True
        and g3_candidate["flags"][
            "exact_lower_energy_field_witness_certified"
        ]
        is True
        and g3_candidate["flags"]["constructive_candidate_rejected_for_G3"]
        is True
        and g3_candidate["flags"]["selected_vacuum_unique_modulo_symmetry"]
        is False
        and g3_candidate["flags"]["G3_closed"] is False,
        "constructive exact local G3 candidate failed or was globally over-promoted",
    )
    require(gauged_g3["n_failed"] == 0, "gauged U(1)_X G3 audit failed")
    require(
        gauged_g3["status"]
        == "G3_SELECTED_VACUUM_REJECTED_BY_EXACT_GLOBAL_COUNTEREXAMPLE"
        and gauged_g3["overall_state"] == "OPEN",
        "gauged U(1)_X G3 exact global-counterexample state changed",
    )
    require(
        gauged_g3["coverage"]["invariant_directions"] == 44
        and gauged_g3["coverage"]["real_parameters"] == 51
        and gauged_g3["coverage"]["real_field_dimension"] == 486
        and gauged_g3["coverage"]["gauge_quotient_dimension_including_axion"]
        == 449
        and gauged_g3["coverage"]["massive_transverse_quotient_dimension"]
        == 448,
        "gauged U(1)_X G3 dimensions changed",
    )
    require(
        gauged_g3["flags"][
            "gauge_quotient_dimension_449_including_axion_certified"
        ]
        is True
        and gauged_g3["flags"][
            "massive_transverse_quotient_dimension_448_certified"
        ]
        is True
        and gauged_g3["flags"]["stationarity_rank_13_exactly_certified"] is True
        and gauged_g3["flags"]["stationarity_nullity_38_exactly_certified"]
        is True
        and gauged_g3["flags"][
            "exact_three_structural_zero_gradient_certificates"
        ]
        is True
        and gauged_g3["flags"][
            "G3_exact_informed_13_row_constraints_ready"
        ]
        is True
        and gauged_g3["flags"][
            "legacy_reference_equilibrated_common_kernel_135_invalidated"
        ]
        is True
        and gauged_g3["flags"][
            "constructive_sparse_27_parameter_candidate_found"
        ]
        is True
        and gauged_g3["flags"][
            "historical_positive_J0_normalization_invalidated"
        ]
        is True
        and gauged_g3["flags"][
            "constructive_candidate_conditional_rank448_evidence"
        ]
        is False
        and gauged_g3["flags"][
            "constructive_candidate_direct_exact_source_binding"
        ]
        is True
        and gauged_g3["flags"][
            "constructive_candidate_exact_rank448_certificate"
        ]
        is True
        and gauged_g3["flags"]["G3_fixed_vacuum_strict_minimum_certified"]
        is True
        and gauged_g3["flags"]["G3_fixed_vacuum_PSD_feasible_certified"]
        is True
        and gauged_g3["flags"]["complete_potential_BFB"] is True
        and gauged_g3["flags"][
            "G3_selected_vacuum_global_no_go_certified"
        ]
        is True
        and gauged_g3["flags"][
            "exact_lower_energy_field_witness_certified"
        ]
        is True
        and gauged_g3["flags"]["constructive_candidate_rejected_for_G3"]
        is True
        and gauged_g3["flags"]["global_competing_extrema_exhausted"] is False
        and gauged_g3["flags"]["G3_closed"] is False
        and gauged_g3["flags"]["whole_model_validated"] is False
        and gauged_g3["flags"]["whole_model_excluded"] is False,
        "gauged U(1)_X G3 scope was over-promoted",
    )
    corrected = corrected_common_kernel["corrected_common_kernel_diagnostic"]
    require(
        corrected_common_kernel["n_failed"] == 0
        and corrected_common_kernel["overall_state"] == "OPEN"
        and corrected_common_kernel["flags"][
            "legacy_common_kernel_dimension_135_invalidated"
        ]
        is True
        and corrected_common_kernel["flags"][
            "exact_H6_radial_flat_direction_refuted"
        ]
        is True
        and corrected["corrected_common_kernel"]["rank"] == 448
        and corrected["corrected_common_kernel"]["nullity"] == 0
        and corrected["proof_grade"] is False
        and corrected["certified_PSD_feasibility"] is False
        and corrected["certified_no_go"] is False,
        "corrected G3 common-kernel evidence changed scope",
    )
    require(
        matrix["overall_state"] == "BLOCKED"
        and not matrix["full_theory_validated"],
        "external model-execution blocker was promoted past the validation matrix",
    )
    require(
        ultimate["overall_state"] == "BLOCKED"
        and not ultimate["internal_candidate_approved"]
        and not ultimate["full_phenomenology_approved"]
        and not ultimate["whole_model_excluded"],
        "ultimate gate promoted or excluded the externally unattested model",
    )

    suite = unittest.defaultTestLoader.discover(str(ROOT))
    n_tests = suite.countTestCases()
    require(n_tests >= 154, f"expected at least 154 tests, found {n_tests}")
    run([sys.executable, "-m", "unittest", "-v"])
    run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "test_exact_x_symmetry_consistency_gate_v20.py",
            "test_g1_exact_declared_symmetry_character_census_v20.py",
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
            "test_exact_gauged_u1x_g3_su5_equality_orbit_v20.py",
            "test_exact_gauged_u1x_g3_su5_chiral_global_gap_reduction_v20.py",
            "test_exact_gauged_u1x_g3_su5_fixed_f_offkernel_bound_v20.py",
            "test_exact_gauged_u1x_g3_su5_max_negative_zero_residual_bound_v20.py",
            "test_exact_gauged_u1x_g3_su5_max_negative_full_residual_bound_v20.py",
            "test_exact_gauged_u1x_g3_su5_max_negative_rank1_su3_slice_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py",
            "test_exact_gauged_u1x_g3_alternative_global_sos_audit_v20.py",
            "test_final_g3_acceptance_gate_v20.py",
            "test_gauged_u1x_g3_sos_candidate_v20.py",
            "test_gauged_u1x_g3_stability_v20.py",
            "test_gauged_u1x_g3_corrected_common_kernel_v20.py",
            "test_g1_g8_gate_ledger_v20.py",
            "test_g1_g8_execution_roadmap_v20.py",
            "test_theory_validation_matrix_v20.py",
            "test_replicate_v20.py",
        ]
    )

    pdflatex = shutil.which("pdflatex")
    require(pdflatex is not None, "pdflatex is required")
    latex = [pdflatex, "-interaction=nonstopmode", "-halt-on-error", TEX.name]
    run(latex)
    run(latex)
    stable = hashlib.sha256(PDF.read_bytes()).hexdigest()
    run(latex)
    rebuilt = hashlib.sha256(PDF.read_bytes()).hexdigest()
    require(rebuilt == stable, "PDF is not byte-reproducible after stabilization")

    forbidden = (
        "LaTeX Warning",
        "Package hyperref Warning",
        "Overfull \\hbox",
        "Underfull \\hbox",
        "Overfull \\vbox",
        "Underfull \\vbox",
        "undefined references",
        "multiply defined",
    )
    log_text = LOG.read_text(errors="replace")
    hits = [marker for marker in forbidden if marker in log_text]
    require(not hits, f"LaTeX log defects: {hits}")
    require(PDF.read_bytes()[:5] == b"%PDF-", "invalid PDF header")
    require(PDF.stat().st_size > 100_000, "PDF unexpectedly small")

    pdfinfo = shutil.which("pdfinfo")
    require(pdfinfo is not None, "pdfinfo is required")
    metadata = subprocess.run(
        [pdfinfo, str(PDF)], cwd=ROOT, check=True, text=True, capture_output=True
    ).stdout
    require("Pages:           14" in metadata, "expected a fourteen-page manuscript")

    core = [
        ROOT / "README.md",
        ROOT / "REFEREE_AUDIT_v20.md",
        ROOT / "V20_ERROR_AUDIT.md",
        TEX,
        PDF,
        ROOT / "decay_safe_completion_v20.py",
        ROOT / "decay_threshold_v20.py",
        ROOT / "audit_v20_errors.py",
        ROOT / "physics_push_v20.py",
        ROOT / "full_fermion_matching_v20.py",
        ROOT / "portal_tensors_abcd_v20.py",
        ROOT / "physical_cf_matching_v20.py",
        ROOT / "global_flavour_fit_v20.py",
        ROOT / "cmb_public_data_pipeline_v20.py",
        ROOT / "empirical_roadmap_lock_v20.py",
        ROOT / "next_phenomenology_lock_v20.py",
        ROOT / "close_open_gaps_v20.py",
        ROOT / "verify_tan_beta_profile_semantics.py",
        ROOT / "tan_beta_profile_v20.py",
        ROOT / "reanalysis_portal_beta_v20.py",
        ROOT / "FERMION_PORTAL_CURRENT_THEOREM.md",
        ROOT / "FULL_FERMION_MATCHING_V20_VERDICT.json",
        ROOT / "PORTAL_TENSORS_ABCD_V20_VERDICT.json",
        ROOT / "PHYSICAL_CF_MATCHING_V20_VERDICT.json",
        ROOT / "GLOBAL_FLAVOUR_FIT_V20_VERDICT.json",
        ROOT / "CMB_PUBLIC_PIPELINE_V20_VERDICT.json",
        ROOT / "EMPIRICAL_ROADMAP_LOCK_V20_VERDICT.json",
        ROOT / "NEXT_PHENOMENOLOGY_LOCK_V20_VERDICT.json",
        ROOT / "OPEN_GAPS_CLOSURE_V20_VERDICT.json",
        ROOT / "TAN_BETA_PROFILE_V20_VERDICT.json",
        ROOT / "V20_PORTAL_BETA_REANALYSIS_VERDICT.json",
        ROOT / "models" / "SO10Z17AxionV20.m",
        ROOT / "models" / "EXACT_X_EXTERNAL_INPUT_MANIFEST_V20.json",
        ROOT / "tools" / "validate-exact-x-model.wls",
        ROOT / "run_exact_x_sarah_validation_v20.py",
        ROOT / "models" / "SO10Z17AxionV20_pyrate.yaml",
        ROOT / "exact_x_symmetry_consistency_gate_v20.py",
        ROOT / "sarah_pyrate_210n_model_file_v20.py",
        ROOT / "test_sarah_pyrate_210n_model_file_v20.py",
        ROOT / "SARAH_PYRATE_MODEL_FILE_V20_VERDICT.json",
        ROOT / "SARAH_PYRATE_MODEL_FILE_V20.md",
        ROOT / "gauged_u1x_scalar_contract_v20.py",
        ROOT / "gauged_u1x_g2_derivative_audit_v20.py",
        ROOT / "exact_gauged_u1x_stationarity_rank_certificate_v20.py",
        ROOT / "exact_gauged_u1x_physical_quotient_v20.py",
        ROOT / "exact_gauged_u1x_g3_pd_rank_certificate_v20.py",
        ROOT / "exact_gauged_u1x_g3_a_square_recoupling_v20.py",
        ROOT / "exact_gauged_u1x_g3_sos_bfb_stationarity_v20.py",
        ROOT / "exact_gauged_u1x_g3_global_counterexample_v20.py",
        ROOT / "exact_gauged_u1x_g3_kernel_quartic_bound_v20.py",
        ROOT / "exact_gauged_u1x_g3_replacement_stationary_orbit_v20.py",
        ROOT / "exact_gauged_u1x_g3_su5_delta_pd_sos_v20.py",
        ROOT / "exact_gauged_u1x_g3_su5_delta_hsx_extension_v20.py",
        ROOT / "exact_gauged_u1x_g3_su5_delta_hsx_exact_hessian_v20.py",
        ROOT / "exact_gauged_u1x_g3_su5_phi_orbit_lemma_v20.py",
        ROOT / "exact_gauged_u1x_g3_su5_phi_local_component_v20.py",
        ROOT / "exact_gauged_u1x_g3_su5_phi_su3_slice_v20.py",
        ROOT / "exact_gauged_u1x_g3_su5_equality_orbit_v20.py",
        ROOT / "exact_gauged_u1x_g3_su5_chiral_global_gap_reduction_v20.py",
        ROOT / "exact_gauged_u1x_g3_su5_fixed_f_offkernel_bound_v20.py",
        ROOT / "exact_gauged_u1x_g3_su5_max_negative_zero_residual_bound_v20.py",
        ROOT / "exact_gauged_u1x_g3_su5_max_negative_full_residual_bound_v20.py",
        ROOT / "exact_gauged_u1x_g3_alternative_global_sos_audit_v20.py",
        ROOT / "final_g3_acceptance_gate_v20.py",
        ROOT / "gauged_u1x_g3_sos_candidate_v20.py",
        ROOT / "gauged_u1x_g3_stability_v20.py",
        ROOT / "gauged_u1x_g3_corrected_common_kernel_v20.py",
        ROOT / "test_gauged_u1x_g3_stability_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_pd_rank_certificate_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_a_square_recoupling_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_sos_bfb_stationarity_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_global_counterexample_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_kernel_quartic_bound_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_replacement_stationary_orbit_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_su5_delta_pd_sos_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_su5_delta_hsx_extension_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_su5_delta_hsx_exact_hessian_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_su5_phi_orbit_lemma_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_su5_phi_local_component_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_su5_phi_su3_slice_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_su5_equality_orbit_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_su5_chiral_global_gap_reduction_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_su5_fixed_f_offkernel_bound_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_su5_max_negative_zero_residual_bound_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_su5_max_negative_full_residual_bound_v20.py",
        ROOT / "test_exact_gauged_u1x_g3_alternative_global_sos_audit_v20.py",
        ROOT / "test_final_g3_acceptance_gate_v20.py",
        ROOT / "test_replicate_v20.py",
        ROOT / "test_gauged_u1x_g3_sos_candidate_v20.py",
        ROOT / "test_gauged_u1x_g3_corrected_common_kernel_v20.py",
        ROOT / "g1_g8_gate_ledger_v20.py",
        ROOT / "g1_g8_execution_roadmap_v20.py",
        ROOT / "authoritative_full_model_gate_v20.py",
        ROOT / "theory_validation_matrix_v20.py",
        ROOT / "theory_confirmation_verdict_v20.py",
        ROOT / "ultimate_theory_gate_v20.py",
        ROOT / "EXACT_X_SYMMETRY_CONSISTENCY_GATE_V20.json",
        ROOT / "GAUGED_U1X_SCALAR_CONTRACT_V20.json",
        ROOT / "GAUGED_U1X_G2_DERIVATIVE_AUDIT_V20.json",
        ROOT / "GAUGED_U1X_G2_DERIVATIVE_AUDIT_V20.md",
        ROOT / "EXACT_GAUGED_U1X_STATIONARITY_RANK_CERTIFICATE_V20.json",
        ROOT / "EXACT_GAUGED_U1X_STATIONARITY_RANK_CERTIFICATE_V20.md",
        ROOT / "EXACT_GAUGED_U1X_PHYSICAL_QUOTIENT_V20.json",
        ROOT / "EXACT_GAUGED_U1X_PHYSICAL_QUOTIENT_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_PD_RANK_CERTIFICATE_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_PD_RANK_CERTIFICATE_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_A_SQUARE_RECOUPLING_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_A_SQUARE_RECOUPLING_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_SOS_BFB_STATIONARITY_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_SOS_BFB_STATIONARITY_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_GLOBAL_COUNTEREXAMPLE_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_GLOBAL_COUNTEREXAMPLE_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_KERNEL_QUARTIC_BOUND_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_KERNEL_QUARTIC_BOUND_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_REPLACEMENT_STATIONARY_ORBIT_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_REPLACEMENT_STATIONARY_ORBIT_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_PD_SOS_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_PD_SOS_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXTENSION_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXTENSION_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXACT_HESSIAN_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXACT_HESSIAN_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_ORBIT_LEMMA_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_ORBIT_LEMMA_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_LOCAL_COMPONENT_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_LOCAL_COMPONENT_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_SU3_SLICE_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_SU3_SLICE_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_EQUALITY_ORBIT_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_EQUALITY_ORBIT_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_CHIRAL_GLOBAL_GAP_REDUCTION_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_CHIRAL_GLOBAL_GAP_REDUCTION_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_FIXED_F_OFFKERNEL_BOUND_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_FIXED_F_OFFKERNEL_BOUND_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_ZERO_RESIDUAL_BOUND_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_ZERO_RESIDUAL_BOUND_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_FULL_RESIDUAL_BOUND_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_FULL_RESIDUAL_BOUND_V20.md",
        ROOT / "EXACT_GAUGED_U1X_G3_ALTERNATIVE_GLOBAL_SOS_AUDIT_V20.json",
        ROOT / "EXACT_GAUGED_U1X_G3_ALTERNATIVE_GLOBAL_SOS_AUDIT_V20.md",
        ROOT / "FINAL_G3_ACCEPTANCE_GATE_V20.json",
        ROOT / "FINAL_G3_ACCEPTANCE_GATE_V20.md",
        ROOT / "GAUGED_U1X_G3_SOS_CANDIDATE_V20.json",
        ROOT / "GAUGED_U1X_G3_SOS_CANDIDATE_V20.md",
        ROOT / "GAUGED_U1X_G3_STABILITY_V20.json",
        ROOT / "GAUGED_U1X_G3_STABILITY_V20.md",
        ROOT / "GAUGED_U1X_G3_CORRECTED_COMMON_KERNEL_V20.json",
        ROOT / "GAUGED_U1X_G3_CORRECTED_COMMON_KERNEL_V20.md",
        ROOT / "G1_G8_GATE_LEDGER_V20.json",
        ROOT / "G1_G8_EXECUTION_ROADMAP_V20.json",
        ROOT / "AUTHORITATIVE_FULL_MODEL_GATE_V20.json",
        ROOT / "THEORY_VALIDATION_MATRIX_V20_VERDICT.json",
        ROOT / "THEORY_CONFIRMATION_VERDICT.json",
        ROOT / "ULTIMATE_THEORY_GATE_V20_VERDICT.json",
        V20_ENGINE,
        V20_VERDICT,
        ROOT / "test_decay_safe_completion_v20.py",
        ROOT / "test_decay_threshold_v20.py",
        ROOT / "test_audit_v20_errors.py",
        ROOT / "test_physics_push_v20.py",
        ROOT / "test_gauged_u1x_g2_derivative_audit_v20.py",
        ROOT / "test_exact_gauged_u1x_stationarity_rank_certificate_v20.py",
        ROOT / "test_exact_gauged_u1x_physical_quotient_v20.py",
        ROOT / "so10_axion_v17_engine.py",
        V17_VERDICT,
        ROOT / "so10_axion_v19_engine.py",
        V19_VERDICT,
        ROOT / "requirements.txt",
        Path(__file__),
    ]
    core.extend(ROOT / relative for relative in FINAL_THEOREM_CORE_PATHS)
    external_model_attestation = (
        ROOT / "models" / "EXACT_X_EXTERNAL_MODEL_VALIDATION_V20.json"
    )
    if external_model_attestation.exists():
        core.append(external_model_attestation)
    require(all(path.exists() for path in core), "release core is incomplete")
    write_checksums(core)
    print(
        f"RELEASE GATE PASS: v17 65/65; v19 59/59; v20 42/42; "
        f"tests {n_tests}/{n_tests}; clean 14-page PDF; scientific state BLOCKED"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
