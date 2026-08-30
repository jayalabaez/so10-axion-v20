"""Regression tests for the V43 self-paired/Pfaffian Z66 threshold audit."""

from __future__ import annotations

import json
import subprocess
import sys

import susy_v43_pfaffian_product_escape_audit as v43


REPORT = v43.build_report()


def test_full_v40_product_triangle_gravity_and_ps_target_ledger_is_explicit() -> None:
    baseline = REPORT["baseline_full_U1F_U1X_U1H_local_triangle_gravity_PS_audit"]
    host = baseline["V40_host_full_local_row_ledger"]
    assert host["U1_PS_squared"]["X"] == {"SU4": -8, "SU2L": -8, "SU2R": -8}
    assert host["U1_gravity"] == {"F": 0, "X": -33, "H": 0}
    assert host["U1_cubic_and_all_cross_triangles"] == {
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
    assert baseline["critical_X_PS_target"] == {"SU4": 8, "SU2L": 8, "SU2R": 8}


def test_self_majorana_even_x_branch_is_massable_and_really_evicts_dirac_gravity_parity() -> None:
    witness = REPORT["self_paired_massable_witnesses"]["self_majorana_singlet"]
    branch = witness["massability_and_Z66_branch"]
    assert witness["all_declared_X_VEVs_are_multiples_of_66"] is True
    assert witness["all_new_threshold_X_VEVs_preserve_old_Z66_and_Z5610_direction"] is True
    assert branch["all_terms_continuous_U1F_X_H_neutral"] is True
    assert branch["all_terms_Z66_and_Z5610_neutral"] is True
    assert branch["all_terms_have_Z4R_superpotential_charge_two"] is True
    assert branch["unbroken_X_remnant"] == "Z66 because the only X-charged VEVs are +66 and -66"
    assert "before any later V40 P/Pb PQ VEV" in branch["threshold_scope"]
    assert branch["mass_rank_witness"]["matter_rank"] == 1
    assert branch["mass_rank_witness"]["Sigma_T_hessian_rank"] == 2
    assert branch["mass_rank_witness"]["all_isolated_chiral_and_vector_degrees_accounted_for"] is True
    gravity = REPORT["self_majorana_gravity_escape"]["critical_values"]
    assert gravity == {
        "V40_host_X_gravity": -33,
        "self_majorana_packet_X_gravity_increment": 33,
        "combined_X_gravity": 0,
        "combined_X_cubed": 41184,
        "combined_X_PS_squared": {"SU4": -8, "SU2L": -8, "SU2R": -8},
    }


def test_real_and_pfaffian_ps_witnesses_obey_the_correct_moduli_and_massability() -> None:
    witnesses = REPORT["self_paired_massable_witnesses"]
    real = witnesses["real_PS_majorana"]
    pf = witnesses["pseudoreal_PS_pfaffian"]
    assert real["local_anomaly_increment"]["U1_PS_squared"]["X"] == {
        "SU4": 66,
        "SU2L": 0,
        "SU2R": 0,
    }
    assert real["local_anomaly_increment"]["U1_gravity"]["X"] == 198
    assert real["massability_and_Z66_branch"]["mass_rank_witness"]["matter_chiral_component_rank"] == 6
    assert pf["local_anomaly_increment"]["U1_PS_squared"]["X"] == {
        "SU4": 0,
        "SU2L": 66,
        "SU2R": 0,
    }
    assert pf["local_anomaly_increment"]["U1_gravity"]["X"] == 132
    assert pf["massability_and_Z66_branch"]["mass_rank_witness"]["flavour_rank"] == 2
    assert pf["massability_and_Z66_branch"]["mass_rank_witness"]["SU2L_Witten_doublet_count_from_block"] == 2
    assert pf["local_anomaly_increment"]["pure_Pati_Salam_and_SU2_global_checks"]["SU2L_Witten_even"] is True


def test_symmetric_and_pfaffian_theorem_closes_the_ordinary_threshold_class_only() -> None:
    theorem = REPORT["ordinary_Z66_self_paired_Pfaffian_threshold_theorem"]
    assert theorem["Dirac_block"]["mixed_PS_increment_lattice"] == "66 Z"
    assert theorem["symmetric_real_Majorana_block"]["mixed_PS_increment_lattice"] == "33 Z"
    assert theorem["skew_pseudoreal_Pfaffian_block"]["mixed_PS_increment_lattice"] == "66 Z"
    assert theorem["V40_required_increment_mod_33"] == {"SU4": 8, "SU2L": 8, "SU2R": 8}
    assert theorem["target_lies_in_allowed_lattice"] is False
    assert REPORT["decision"]["fully_local_continuous_anomaly_free_product_parent_exists_in_stated_class"] is False
    assert REPORT["full_gate_closed"] is False
    assert REPORT["complete_theory_exists"] is False


def test_artifacts_replay() -> None:
    result = subprocess.run(
        [sys.executable, "-B", str(v43.ROOT / "susy_v43_pfaffian_product_escape_audit.py"), "--write", "--check"],
        cwd=v43.ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "V43_PFAFFIAN_PRODUCT_ESCAPE_ARTIFACTS_CHECK_PASS" in result.stdout
    stored = json.loads(v43.JSON_PATH.read_text(encoding="utf-8"))
    assert stored["status"] == REPORT["status"]
    assert stored["core_sha256"] == v43.canonical_sha(stored)
    assert stored["n_failed"] == 0
