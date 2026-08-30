"""Regression tests for the V45 S0 group/zero-mode audit."""

from __future__ import annotations

import json
import subprocess
import sys

import susy_v45_s0_group_zero_mode_audit as s0


REPORT = s0.build_report()


def test_exact_D5_PS_SU5_root_intersection_is_SM_algebra() -> None:
    root = REPORT["exact_root_intersection"]
    assert root["D5_root_count"] == 40
    assert root["D5_dimension"] == 45
    assert root["PS_dimension"] == 21
    assert root["SU5_dimension"] == 24
    assert root["intersection_root_count"] == 8
    assert root["intersection_semisimple_rank"] == 3
    assert root["intersection_Cartan_rank"] == 4
    assert root["intersection_dimension"] == 12
    assert root["intersection_algebra"] == "su(3)_C + su(2)_L + u(1)_Y"
    assert root["six_Y_vector"] == [-2, -2, -2, 3, 3]
    assert root["six_Y_is_in_SU5_Cartan"]
    assert root["six_Y_commutes_with_common_semisimple_roots"]
    assert root["PS_generators_lifted_by_boundary_Higgs"] == 9


def test_connected_global_form_is_the_Z6_quotient() -> None:
    sm = REPORT["SM_global_form"]
    assert sm["kernel_order"] == 6
    assert sm["kernel_is_cyclic"]
    assert sm["connected_global_form"] == "(SU(3)_C x SU(2)_L x U(1)_Y)/Z6"


def test_orbifold_removes_adjoint_chiral_and_boundary_VEV_reduces_rank() -> None:
    orbifold = REPORT["orbifold_and_SUSY"]
    assert sum(row["massless_before_boundary_VEV"] for row in orbifold["parity_rows"] if row["sector"].startswith("Spin10 vector")) == 21
    assert orbifold["SUSY_projection"]["massless_adjoint_chiral_count"] == 0
    assert orbifold["SUSY_projection"]["surviving_four_dimensional_SUSY"] == "N=1"
    residual = REPORT["residual_group"]
    assert residual["continuous_rank_after_Theta_pair"] == 4
    assert residual["unbroken_U1F_subgroup_with_chosen_unit_line_lattice"] == "Z9"
    assert residual["unbroken_subgroup_seen_faithfully_by_displayed_local_fields"] == "Z3"


def test_126_pair_leaves_matter_parity_as_a_separate_component() -> None:
    stabilizer = REPORT["boundary_126_stabilizer"]
    assert stabilizer["aligned_nonzero_pair_continuous_stabilizer"] == "SU(5)"
    assert stabilizer["unbroken_center_subgroup"] == "<c^2> = Z2_M"
    assert stabilizer["exact_boundary_stabilizer_in_Spin10"] == "SU(5) x Z2_M"
    assert REPORT["residual_group"]["literal_SM_and_no_finite_extension"] is False


def test_original_naked_doublets_are_not_honest_PS_quotient_representations() -> None:
    audit = REPORT["PS_global_representation_audit"]
    assert audit["inherited_PS_group"] == "(SU(4)_C x SU(2)_L x SU(2)_R)/Z2_diag"
    assert sorted(audit["invalid_V44_classes"]) == ["V44_L0/Lminus9", "V44_R0/Rplus9"]
    assert not audit["original_V44_boundary_manifest_globally_valid"]
    assert not s0.ps_rep_is_honest(0, 1, 0)
    assert not s0.ps_rep_is_honest(0, 0, 1)
    assert s0.ps_rep_is_honest(1, 1, 0)
    assert s0.ps_rep_is_honest(1, 0, 1)


def test_spinorial_repair_matches_all_combined_anomaly_rows_and_Z9_orientation() -> None:
    repair = REPORT["globally_honest_anomalon_repair"]
    assert repair["all_integrated_rows_match"]
    assert repair["all_mass_terms_U1F_neutral"]
    assert repair["residual_Z9_orientation"]["all_SU4_fundamentals_mod9"] == [3]
    assert repair["residual_Z9_orientation"]["all_SU4_antifundamentals_mod9"] == [6]
    assert all(not row["Hc_has_zero_mode"] for row in repair["bulk_zero_mode_realization"])
    assert repair["replacement_integrated_anomaly_ledger"] == {
        "SU4_squared_U1F_doubled": 0,
        "SU2L_squared_U1F_doubled": -36,
        "SU2R_squared_U1F_doubled": 36,
        "gravity_squared_U1F": 0,
        "U1F_cubed": 0,
        "SU4_cubed": 0,
        "SU2L_Witten_doublet_count_mod2": 0,
        "SU2R_Witten_doublet_count_mod2": 0,
    }
    assert repair["minimal_V45_core"]["all_displayed_integrated_local_polynomial_and_Witten_rows_vanish"]
    assert all(value == 0 for value in repair["minimal_V45_core"]["full_integrated_anomaly_ledger"].values())


def test_verdict_is_fail_closed_and_artifacts_reproduce() -> None:
    verdict = REPORT["fail_closed_verdict"]
    assert not verdict["S0_original_V44_manifest_passes"]
    assert verdict["S0_repaired_candidate_group_theory_feasible"]
    assert not verdict["S0_stage_closed"]
    assert verdict["G1_through_G8_promoted"] == []
    assert REPORT["n_failed_integrity_checks"] == 0
    assert all(REPORT["integrity_checks"].values())
    assert REPORT["core_sha256"] == s0.canonical_sha(REPORT)

    result = subprocess.run(
        [sys.executable, "-B", str(s0.ROOT / "susy_v45_s0_group_zero_mode_audit.py"), "--check"],
        cwd=s0.ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "V45_S0_GROUP_ZERO_MODE_AUDIT_CHECK_PASS" in result.stdout
    stored = json.loads(s0.JSON_PATH.read_text(encoding="utf-8"))
    assert stored["core_sha256"] == s0.canonical_sha(stored)
