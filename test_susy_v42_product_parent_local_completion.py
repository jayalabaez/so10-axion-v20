"""Regression tests for the V42 local product-parent anomaly packet."""

from __future__ import annotations

import json
import subprocess
import sys

import susy_v42_product_parent_local_completion as v42


REPORT = v42.build_report()


def test_every_local_continuous_product_triangle_and_gravity_row_cancels() -> None:
    audit = REPORT["full_local_continuous_anomaly_audit"]
    assert audit["U1_PS_squared"] == {
        "F": {"SU4": 0, "SU2L": 0, "SU2R": 0},
        "X": {"SU4": 0, "SU2L": 0, "SU2R": 0},
        "H": {"SU4": 0, "SU2L": 0, "SU2R": 0},
    }
    assert audit["U1_gravity"] == {"F": 0, "X": 0, "H": 0}
    assert audit["U1_cubic_and_all_cross_triangles"] == {
        "F_F_F": 0,
        "F_F_X": 0,
        "F_F_H": 0,
        "F_X_X": 0,
        "F_X_H": 0,
        "F_H_H": 0,
        "X_X_X": 0,
        "X_X_H": 0,
        "X_H_H": 0,
        "H_H_H": 0,
    }
    ps = audit["pure_Pati_Salam_and_SU2_global_checks"]
    assert ps == {
        "SU4_cubed": 0,
        "SU2L_Witten_doublet_count": 38,
        "SU2R_Witten_doublet_count": 54,
        "SU2L_Witten_even": True,
        "SU2R_Witten_even": True,
    }
    assert audit["all_local_continuous_gauge_and_mixed_gravitational_rows_vanish"] is True


def test_incremental_ledger_reproduces_the_v40_and_v41_bottleneck_then_zero() -> None:
    ledger = REPORT["incremental_anomaly_ledger"]
    v40_host = ledger["V40_host"]
    assert v40_host["U1_gravity"] == {"F": 0, "X": -33, "H": 0}
    assert v40_host["U1_PS_squared"]["X"] == {"SU4": -8, "SU2L": -8, "SU2R": -8}
    assert v40_host["U1_cubic_and_all_cross_triangles"] == {
        "F_F_F": 0,
        "F_F_X": -270,
        "F_F_H": 0,
        "F_X_X": -360,
        "F_X_H": 6,
        "F_H_H": 0,
        "X_X_X": 5247,
        "X_X_H": 432,
        "X_H_H": -9520,
        "H_H_H": 0,
    }
    after_v41 = ledger["plus_V41_F_cross_threshold"]
    assert all(value == 0 for key, value in after_v41["U1_cubic_and_all_cross_triangles"].items() if key.startswith("F_"))
    assert after_v41["U1_cubic_and_all_cross_triangles"]["X_X_X"] == 4797
    assert after_v41["U1_cubic_and_all_cross_triangles"]["X_X_H"] == 472
    assert after_v41["U1_cubic_and_all_cross_triangles"]["X_H_H"] == -9522
    assert ledger["plus_V42_full_packet"] == {
        "U1_PS_squared": {
            "F": {"SU4": 0, "SU2L": 0, "SU2R": 0},
            "X": {"SU4": 0, "SU2L": 0, "SU2R": 0},
            "H": {"SU4": 0, "SU2L": 0, "SU2R": 0},
        },
        "U1_gravity": {"F": 0, "X": 0, "H": 0},
        "U1_cubic_and_all_cross_triangles": {
            "F_F_F": 0,
            "F_F_X": 0,
            "F_F_H": 0,
            "F_X_X": 0,
            "F_X_H": 0,
            "F_H_H": 0,
            "X_X_X": 0,
            "X_X_H": 0,
            "X_H_H": 0,
            "H_H_H": 0,
        },
        "pure_Pati_Salam_and_SU2_global_checks": {
            "SU4_cubed": 0,
            "SU2L_Witten_doublet_count": 38,
            "SU2R_Witten_doublet_count": 54,
            "SU2L_Witten_even": True,
            "SU2R_Witten_even": True,
        },
    }


def test_every_new_mass_term_is_continuous_neutral_and_has_a_rank_witness() -> None:
    mass = REPORT["massability_audit"]
    assert mass["all_mass_terms_continuous_U1F_X_H_neutral"] is True
    assert mass["all_mass_terms_finite_Z9_Z5610_neutral"] is True
    assert mass["all_mass_terms_have_Z4R_superpotential_charge_two"] is True
    assert mass["all_mass_terms_PQ_neutral"] is True
    assert mass["all_stabilizer_terms_continuous_neutral"] is True
    assert mass["all_stabilizer_terms_have_Z4R_superpotential_charge_two"] is True
    assert mass["full_rank_witness"]["term_ranks"] == {
        "Pb_ChiA": 1,
        "P_ChiB": 1,
        "Pb_D6": 2,
        "Pb_Lx": 4,
        "Pb_Rx": 4,
        "XiMinus_M98": 1,
        "XiPlus_P9": 1,
        "XiPlus_P1": 1,
        "XiPlus_P0x5": 18,
        "XiPlus_P0x6": 1,
        "XiPlus_P0x13": 1,
        "XiPlus_P0x14": 2,
    }
    assert mass["full_rank_witness"]["all_spectator_blocks_full_rank"] is True


def test_z9_is_preserved_but_the_old_x_selector_boundary_is_explicit() -> None:
    finite = REPORT["finite_selector_boundary"]
    assert finite["Z9_arithmetic"]["listed_Z9_rows_vanish"] is True
    assert finite["Z9_arithmetic"] == {
        "Delta_s1_canonical": 504,
        "Delta_s3_canonical": 13824,
        "linear_condition_2Delta_s1_mod_9": 0,
        "cubic_condition_110Delta_s3_mod_54": 0,
        "C_Z9_Z5610_squared_mod_9": 0,
        "C_Z9_squared_Z5610_mod_9": 0,
        "listed_Z9_rows_vanish": True,
    }
    assert finite["all_declared_product_VEVs_preserve_Z9"] is True
    assert finite["Z5610_preservation"]["XiPlus_z5610"] == 85
    assert finite["Z5610_preservation"]["XiMinus_z5610"] == 5525
    assert finite["Z5610_preservation"]["Xi_VEVs_neutral_under_old_Z5610"] is False
    assert finite["Z4R_boundary"]["full_Z4R_preserved_by_Xi_branch"] is False
    assert REPORT["conditional_X_H_higgs_branch"]["Higgsing"] == {
        "U1F_VEV_charges": [9, -9, 0, 0, 0, 0],
        "U1X_VEV_charges": [0, 0, 2, -2, 1, -1, 0, 0],
        "U1H_VEV_charges": [0, 0, 0, 0, 0, 0, 85, -85],
        "unbroken_from_F": "Z9",
        "unbroken_from_X": "trivial because gcd(2,2,1,1)=1",
        "unbroken_from_H": "Z85",
        "full_host_vacuum_solved": False,
    }


def test_even_x_residual_no_go_and_fail_closed_promotion_boundary() -> None:
    theorem = REPORT["even_X_residual_threshold_no_go"]
    assert theorem["input_ledger"] == {
        "V40_host_A_gravity_squared_U1X": -33,
        "V41_P_Pb_threshold_increment": 0,
        "combined_pre_V42_value": -33,
        "combined_pre_V42_value_mod_2": 1,
    }
    assert theorem["ordinary_even_X_Dirac_pair_local_completion_exists"] is False
    assert "odd-X VEV" in theorem["conclusion"]
    assert REPORT["full_gate_closed"] is False
    assert REPORT["complete_theory_exists"] is False
    assert REPORT["n_failed"] == 0
    assert REPORT["core_sha256"] == v42.canonical_sha(REPORT)
    assert all(row["exists"] and len(row["sha256"]) == 64 for row in REPORT["source_manifest"])


def test_artifacts_replay() -> None:
    result = subprocess.run(
        [sys.executable, "-B", str(v42.ROOT / "susy_v42_product_parent_local_completion.py"), "--write", "--check"],
        cwd=v42.ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "V42_PRODUCT_PARENT_LOCAL_COMPLETION_ARTIFACTS_CHECK_PASS" in result.stdout
    stored = json.loads(v42.JSON_PATH.read_text(encoding="utf-8"))
    assert stored["core_sha256"] == v42.canonical_sha(stored)
    assert stored["status"] == REPORT["status"]
