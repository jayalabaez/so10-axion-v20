#!/usr/bin/env python3
"""Deterministic execution harness for the SO(10) axion v20 validation program.

Two modes are intentionally separate:

* ``--pre-unit`` generates artifacts that unit-test consumers require on a
  clean checkout.  This prevents workflow-ordering failures from masquerading
  as physics failures.
* ``--full`` executes the complete repository validation chain and records
  every command, duration, and return code.  It continues after failures so a
  single early error cannot hide later independent failures.

The harness does not promote an unimplemented calculation to a pass.
Scientific classification is produced by ``theory_validation_matrix_v20.py``.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent

PRE_UNIT_COMMANDS: tuple[tuple[str, ...], ...] = (
    (sys.executable, "portal_full_complex_orientation_sphere_v20.py"),
)

FULL_COMMANDS: tuple[tuple[str, ...], ...] = (
    (sys.executable, "audit_v20_errors.py"),
    (sys.executable, "so10_axion_v20_engine.py", "--output", "so10_axion_v20_verdict.json"),
    *PRE_UNIT_COMMANDS,
    (sys.executable, "falsify_v20.py"),
    (sys.executable, "run_v20_referee_next.py"),
    (sys.executable, "extensive_confirm_falsify_v20.py"),
    (sys.executable, "verify_tan_beta_profile_semantics.py"),
    (sys.executable, "next_physics_analysis_v20.py"),
    (sys.executable, "literature_sweep_150uev_v20.py"),
    (sys.executable, "home_public_37ghz_search_v20.py"),
    (sys.executable, "gravitas_axion_v20_37ghz.py"),
    (sys.executable, "public_data_indirect_audit_v20.py"),
    (sys.executable, "full_fermion_matching_v20.py"),
    (sys.executable, "tan_beta_profile_v20.py"),
    (sys.executable, "reanalysis_portal_beta_v20.py"),
    (sys.executable, "portal_tensors_abcd_v20.py"),
    (sys.executable, "physical_cf_matching_v20.py"),
    (sys.executable, "global_flavour_fit_v20.py"),
    (sys.executable, "cmb_public_data_pipeline_v20.py"),
    (sys.executable, "empirical_roadmap_lock_v20.py"),
    (sys.executable, "next_phenomenology_lock_v20.py"),
    (sys.executable, "push_phenomenology_limits_v20.py"),
    (sys.executable, "common_scale_so10_yukawa_v20.py"),
    (sys.executable, "two_loop_so10_210_yukawa_v20.py"),
    (sys.executable, "channel_fcnc_rates_v20.py"),
    (sys.executable, "na62_pointwise_limit_v20.py"),
    (sys.executable, "twist_massless_limit_v20.py"),
    (sys.executable, "portal_constraint_ray_v20.py"),
    (sys.executable, "portal_boundary_heavy_spectrum_v20.py"),
    (sys.executable, "portal_family_orientation_map_v20.py"),
    (sys.executable, "portal_full_complex_orientation_sphere_v20.py"),
    (sys.executable, "theory_certification_math_v20.py"),
    (sys.executable, "pati_salam_yukawa_matching_v20.py"),
    (sys.executable, "portal_yukawa_posterior_v20.py"),
    (sys.executable, "haloscope_37ghz_limit_compare_v20.py"),
    (sys.executable, "uv_vacuum_alignment_v20.py"),
    (sys.executable, "yukawa_rge_2loop_v20.py"),
    (sys.executable, "fcnc_exact_likelihood_v20.py"),
    (sys.executable, "strict_rg_audit_v20.py"),
    (sys.executable, "close_open_gaps_v20.py"),
    (sys.executable, "integrate_full_complex_orientation_v20.py"),
    (sys.executable, "exact_x_symmetry_consistency_gate_v20.py"),
    (sys.executable, "sarah_pyrate_210n_model_file_v20.py"),
    (sys.executable, "gauged_u1x_scalar_contract_v20.py", "--write"),
    (sys.executable, "g1_exact_declared_symmetry_character_census_v20.py", "--write"),
    (
        sys.executable,
        "exact_gauged_u1x_stationarity_rank_certificate_v20.py",
        "--write",
    ),
    (sys.executable, "gauged_u1x_g2_derivative_audit_v20.py", "--write"),
    (
        sys.executable,
        "exact_gauged_u1x_physical_quotient_v20.py",
        "--write",
    ),
    (
        sys.executable,
        "exact_gauged_u1x_g3_pd_rank_certificate_v20.py",
        "--recompute-heavy",
        "--write",
    ),
    (
        sys.executable,
        "exact_gauged_u1x_g3_a_square_recoupling_v20.py",
        "--recompute",
        "--write",
    ),
    (
        sys.executable,
        "exact_gauged_u1x_g3_sos_bfb_stationarity_v20.py",
        "--recompute",
        "--write",
    ),
    (
        sys.executable,
        "exact_gauged_u1x_g3_global_counterexample_v20.py",
        "--write",
    ),
    (
        sys.executable,
        "exact_gauged_u1x_g3_kernel_quartic_bound_v20.py",
        "--write",
    ),
    (
        sys.executable,
        "exact_gauged_u1x_g3_replacement_stationary_orbit_v20.py",
        "--write",
    ),
    (
        sys.executable,
        "exact_gauged_u1x_g3_su5_delta_pd_sos_v20.py",
        "--write",
    ),
    (
        sys.executable,
        "exact_gauged_u1x_g3_su5_delta_hsx_extension_v20.py",
        "--write",
    ),
    (
        sys.executable,
        "exact_gauged_u1x_g3_su5_delta_hsx_exact_hessian_v20.py",
        "--write",
    ),
    (
        sys.executable,
        "exact_gauged_u1x_g3_su5_phi_orbit_lemma_v20.py",
        "--write",
    ),
    (
        sys.executable,
        "exact_gauged_u1x_g3_su5_phi_local_component_v20.py",
        "--write",
    ),
    (
        sys.executable,
        "exact_gauged_u1x_g3_su5_phi_su3_slice_v20.py",
        "--write",
    ),
    (
        sys.executable,
        "exact_gauged_u1x_g3_su5_equality_orbit_v20.py",
        "--write",
    ),
    (
        sys.executable,
        "exact_gauged_u1x_g3_su5_fixed_f_offkernel_bound_v20.py",
        "--write",
    ),
    (
        sys.executable,
        "exact_gauged_u1x_g3_su5_max_negative_zero_residual_bound_v20.py",
        "--write",
    ),
    (
        sys.executable,
        "exact_gauged_u1x_g3_su5_max_negative_full_residual_bound_v20.py",
        "--write",
    ),
    (
        sys.executable,
        "exact_gauged_u1x_g3_su5_chiral_global_gap_reduction_v20.py",
        "--write",
    ),
    (
        sys.executable,
        "exact_gauged_u1x_g3_alternative_global_sos_audit_v20.py",
        "--write",
    ),
    (
        sys.executable,
        "gauged_u1x_g3_sos_candidate_v20.py",
        "--recompute-heavy",
        "--write",
    ),
    (sys.executable, "gauged_u1x_g3_stability_v20.py", "--write"),
    (
        sys.executable,
        "gauged_u1x_g3_corrected_common_kernel_v20.py",
        "--recompute-heavy",
        "--write",
    ),
    (sys.executable, "g1_g8_gate_ledger_v20.py", "--write"),
    (sys.executable, "final_g3_acceptance_gate_v20.py", "--write"),
    (sys.executable, "g1_g8_execution_roadmap_v20.py", "--write"),
    (sys.executable, "authoritative_full_model_gate_v20.py"),
    (sys.executable, "theory_validation_matrix_v20.py", "--expect-blocked"),
    (sys.executable, "theory_confirmation_verdict_v20.py", "--expect-blocked"),
    (sys.executable, "ultimate_theory_gate_v20.py", "--expect-blocked"),
    (sys.executable, "ultimate_theory_gate_v20.py", "--expect-blocked", "--no-write"),
    (sys.executable, "-m", "unittest", "discover", "-v"),
    (
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
        "test_exact_gauged_u1x_g3_su5_fixed_f_offkernel_bound_v20.py",
        "test_exact_gauged_u1x_g3_su5_max_negative_zero_residual_bound_v20.py",
        "test_exact_gauged_u1x_g3_su5_max_negative_full_residual_bound_v20.py",
        "test_exact_gauged_u1x_g3_su5_chiral_global_gap_reduction_v20.py",
        "test_exact_gauged_u1x_g3_alternative_global_sos_audit_v20.py",
        "test_final_g3_acceptance_gate_v20.py",
        "test_gauged_u1x_g3_sos_candidate_v20.py",
        "test_gauged_u1x_g3_stability_v20.py",
        "test_gauged_u1x_g3_corrected_common_kernel_v20.py",
        "test_g1_g8_gate_ledger_v20.py",
        "test_g1_g8_execution_roadmap_v20.py",
        "test_theory_validation_matrix_v20.py",
        "test_replicate_v20.py",
    ),
)


def _portable_command(command: tuple[str, ...]) -> tuple[str, ...]:
    if command and command[0] == sys.executable:
        return ("python", *command[1:])
    return command


def _display(command: tuple[str, ...]) -> str:
    return " ".join(_portable_command(command))


def run_commands(
    commands: tuple[tuple[str, ...], ...],
    *,
    continue_after_failure: bool,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for index, command in enumerate(commands, start=1):
        started = time.monotonic()
        environment = os.environ.copy()
        for name in (
            "OPENBLAS_NUM_THREADS",
            "OMP_NUM_THREADS",
            "MKL_NUM_THREADS",
            "NUMEXPR_NUM_THREADS",
        ):
            environment[name] = "1"
        completed = subprocess.run(
            command,
            cwd=ROOT,
            check=False,
            env=environment,
        )
        elapsed = time.monotonic() - started
        row = {
            "index": index,
            "command": list(_portable_command(command)),
            "display": _display(command),
            "returncode": int(completed.returncode),
            "elapsed_seconds": float(elapsed),
            "passed": completed.returncode == 0,
        }
        rows.append(row)
        if completed.returncode != 0 and not continue_after_failure:
            break
    failures = [row for row in rows if not row["passed"]]
    return {
        "status": "PASS" if not failures and len(rows) == len(commands) else "FAIL",
        "n_commands_requested": len(commands),
        "n_commands_executed": len(rows),
        "n_failed": len(failures),
        "failures": failures,
        "commands": rows,
    }


def write_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Validation execution — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        f"- Mode: `{report['mode']}`",
        f"- Commands requested: {report['n_commands_requested']}",
        f"- Commands executed: {report['n_commands_executed']}",
        f"- Failed commands: {report['n_failed']}",
        "",
        "## Command ledger",
        "",
    ]
    for row in report["commands"]:
        mark = "PASS" if row["passed"] else "FAIL"
        lines.append(
            f"- **{mark}** `{row['display']}` "
            f"({row['elapsed_seconds']:.3f} s, rc={row['returncode']})"
        )
    if report["failures"]:
        lines += ["", "## Failures", ""]
        lines.extend(f"- `{row['display']}`" for row in report["failures"])
    lines += [
        "",
        "## Interpretation",
        "",
        (
            "This file certifies execution and reproducibility only. "
            "Scientific validity is classified separately by "
            "`THEORY_VALIDATION_MATRIX_V20`."
        ),
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pre-unit", action="store_true")
    group.add_argument("--full", action="store_true")
    args = parser.parse_args()

    mode = "PRE_UNIT" if args.pre_unit else "FULL"
    commands = PRE_UNIT_COMMANDS if args.pre_unit else FULL_COMMANDS
    report = run_commands(
        commands,
        continue_after_failure=bool(args.full),
    )
    report["mode"] = mode
    report["commit_sha"] = os.getenv("GITHUB_SHA", "")
    report["workflow_run_id"] = os.getenv("GITHUB_RUN_ID", "")

    ROOT.joinpath("VALIDATION_EXECUTION_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    ROOT.joinpath("VALIDATION_EXECUTION_V20.md").write_text(
        write_markdown(report),
        encoding="utf-8",
    )
    print(json.dumps({
        "status": report["status"],
        "mode": mode,
        "n_commands_executed": report["n_commands_executed"],
        "n_failed": report["n_failed"],
        "failures": [row["display"] for row in report["failures"]],
    }, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
