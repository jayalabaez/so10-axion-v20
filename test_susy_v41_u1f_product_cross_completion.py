from __future__ import annotations

import json
import subprocess
import sys

import susy_v41_u1f_product_cross_completion as v41


REPORT = v41.build_report()


def test_exact_two_pair_cross_anomaly_cancellation_and_f_only_preservation() -> None:
    cross = REPORT["continuous_cross_triangle_audit"]
    assert cross["baseline_V40_rows"] == {
        "F_X_squared": -360,
        "F_squared_X": -270,
        "F_H_squared": 0,
        "F_squared_H": 0,
        "F_X_H": 6,
    }
    assert cross["threshold_increment"] == {
        "F_X_squared": 360,
        "F_squared_X": 270,
        "F_H_squared": 0,
        "F_squared_H": 0,
        "F_X_H": -6,
    }
    assert cross["net_rows"] == {name: 0 for name in v41.TRIANGLE_ROWS}
    assert cross["all_genuine_F_X_H_triangle_rows_cancel"] is True
    assert REPORT["F_only_anomaly_preservation"]["threshold_increment"] == {
        "F_cubed": 0,
        "F_gravity": 0,
        "F_PS_squared": 0,
    }


def test_mass_terms_and_derived_crt_charges_are_exact() -> None:
    fields = {row["field"]: row for row in REPORT["threshold_field_packet"]}
    assert fields["ChiAPlus"]["z5610"] == 510
    assert fields["ChiAMinus"]["z5610"] == 5270
    assert fields["ChiBPlus"]["z5610"] == 4741
    assert fields["ChiBMinus"]["z5610"] == 699
    mass = REPORT["massability"]
    assert mass["all_terms_continuous_neutral"] is True
    assert mass["all_terms_finite_neutral"] is True
    assert mass["all_terms_have_Z4R_superpotential_charge_two"] is True
    assert mass["mass_matrix"]["rank_if_lambda_A_lambda_B_<P><Pb>_nonzero"] == 4
    for entry in mass["superpotential_terms"]:
        assert entry["U1F"] == entry["U1X"] == entry["U1H"] == entry["PQ_numerator_over_170"] == 0
        assert entry["Z9"] == entry["Z5610"] == 0
        assert entry["Z4R"] == 2


def test_finite_residues_and_same_orientation_selector_proof_survive() -> None:
    finite = REPORT["finite_remnant_audit"]
    assert finite["threshold_Z9_increment"] == {
        "Delta_s1_canonical": 18,
        "Delta_s3_canonical": 486,
        "linear_condition_2Delta_s1_mod_9": 0,
        "cubic_condition_110Delta_s3_mod_54": 0,
        "C_Z9_Z5610_squared_mod_9_increment": 0,
        "C_Z9_squared_Z5610_mod_9_increment": 0,
    }
    assert finite["combined_V40_plus_threshold"]["all_listed_finite_rows_still_vanish"] is True
    ring = REPORT["same_orientation_ring_preservation"]
    assert ring["same_orientation_source_charges"] == {"Q4": 3, "Qc4": 6}
    assert ring["same_orientation_all_ring_subproof_preserved_conditionally"] is True


def test_residual_preserving_and_simple_gs_obstructions_are_nonvacuous() -> None:
    theta = REPORT["residual_preserving_theta_threshold_no_go"]
    assert theta["required_increment_mod_9"] == 3
    assert "multiple of nine" in theta["conclusion"]
    assert len(theta["full_rank_block_extension"]) == 4
    assert "does not rely on diagonal" in theta["full_rank_block_extension"][-1]
    minimal = REPORT["restricted_two_pair_minimality"]
    assert minimal["one_pair_identity"]["integer_solution_exists"] is False
    assert minimal["two_pair_solution"]["sum_C_F_X_H"] == "0 - 6 = -6"
    gs = REPORT["simple_quantized_GS_subcase"]
    assert gs["integer_solution"] == {"k_XX": 40, "k_XH": None}
    assert "not an integer" in gs["obstruction"]


def test_boundary_is_fail_closed_and_artifacts_replay() -> None:
    assert REPORT["full_gate_closed"] is False
    assert REPORT["complete_theory_exists"] is False
    assert REPORT["n_failed"] == 0
    assert REPORT["core_sha256"] == v41.canonical_sha(REPORT)
    assert all(row["exists"] and len(row["sha256"]) == 64 for row in REPORT["source_manifest"])
    if v41.JSON_PATH.is_file():
        stored = json.loads(v41.JSON_PATH.read_text(encoding="utf-8"))
        assert stored["core_sha256"] == v41.canonical_sha(stored)
        assert stored["status"] == REPORT["status"]
    result = subprocess.run(
        [sys.executable, "-B", str(v41.ROOT / "susy_v41_u1f_product_cross_completion.py"), "--check"],
        cwd=v41.ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "V41_U1F_PRODUCT_CROSS_COMPLETION_ARTIFACTS_CHECK_PASS" in result.stdout
