from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ENGINE = HERE / "susy_v60_heterotic_corrected_z4r_live_orbifolder_audit.py"
SPEC = importlib.util.spec_from_file_location("v60_live_orbifolder", ENGINE)
assert SPEC is not None and SPEC.loader is not None
V60 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = V60
SPEC.loader.exec_module(V60)


def report():
    return V60.build_report()


def test_source_hashes_and_spectrum_are_exact():
    data = report()
    assert all(row["matches_expected"] for row in data["source_lock"].values())
    reproduction = data["self_contained_reproduction"]
    assert reproduction["requires_external_orbifolder_tree"] is False
    assert reproduction["requires_orbifolder_executable"] is False
    assert reproduction["raw_regeneration_hashes_preserved"] is True
    assert reproduction["original_Mendeley_archive_hash_preserved"] is True
    assert data["spectrum"]["field_count"] == 92
    assert data["spectrum"]["all_oscillators_absent"] is True
    assert data["spectrum"]["sector_counts"] == {"U": 12, "T_10": 32, "T_01": 26, "T_11": 22}


def test_reproduction_has_no_temporary_orbifolder_dependency(monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", r"Z:\path_that_does_not_exist")
    assert not hasattr(V60, "ORBI_ROOT")
    assert V60.FIXTURE_PATH.is_file()
    assert V60.sha256_file(V60.FIXTURE_PATH) == V60.EXPECTED_FIXTURE_SHA256
    assert report()["spectrum"]["field_count"] == 92


def test_gamma_basis_is_source_ordered():
    data = report()
    assert data["geometry_and_conventions"]["gamma_column_order"] == [
        "theta", "omega", "e1", "e2", "e3", "e4", "e5", "e6", "tau"
    ]


def test_every_massless_affine_hg_equation_passes():
    fields = V60.parse_fields()
    for field in fields:
        for plane in range(3):
            V60.derive_h_for_plane(field, plane)
    assert report()["spectrum"]["all_affine_hg_equations_pass"] is True


def test_exactly_six_fields_shift():
    changed = report()["spectrum"]["changed_fields"]
    assert [row["field"] for row in changed] == ["F_41", "F_42", "F_80", "F_81", "F_91", "F_92"]
    assert all(row["gamma_h"] == "1/2" for row in changed)
    assert all(row["shift_mod4"] == 2 for row in changed)


def test_shifted_fields_have_expected_hidden_representations():
    changed = report()["spectrum"]["changed_fields"]
    reps = {row["field"]: row["representation"] for row in changed}
    assert reps["F_41"] == [1, 1, 1, 2, 1]
    assert reps["F_42"] == [1, 1, 1, 1, 2]
    assert reps["F_80"] == [1, 1, 1, 1, 2]
    assert reps["F_81"] == [1, 1, 1, 2, 1]
    assert reps["F_91"] == [1, 1, 1, 1, 2]
    assert reps["F_92"] == [1, 1, 1, 2, 1]


def test_corrected_nonabelian_residues_are_nonuniversal():
    anomalies = report()["non_Abelian_mixed_Z4R_anomalies"]
    assert anomalies["corrected_residues_universal"] is False
    assert len(set(anomalies["corrected_residue_vector_mod2"])) > 1


def test_all_three_corrected_plane_residue_vectors_and_scan():
    plane = report()["non_Abelian_mixed_Z4R_anomalies"]["all_three_corrected_plane_R_audit"]
    assert plane["individual_residue_vectors_mod2"] == {
        "R1": ["0", "0", "0", "1", "1"],
        "R2": ["0", "0", "0", "1", "1"],
        "R3": ["1", "1", "1", "0", "0"],
    }
    scan = plane["coefficient_scan"]
    assert scan["coefficients_tested"] == 32
    assert scan["residue_pattern_counts"] == {
        "0,0,0,1,1": 16,
        "1,1,1,0,0": 16,
    }
    assert scan["universal_case_count"] == 0


def test_all_printed_continuous_u1_columns_are_relative_universal():
    u1 = report()["mixing_repair_audit"]["continuous_U1"]
    assert u1["all_U1_mixings_leave_relative_anomalies_invariant"] is True
    assert all(u1["each_column_is_universal_across_all_non_Abelian_factors"])


def test_all_64_space_group_mixings_fail_to_repair():
    search = report()["mixing_repair_audit"]["space_group_exhaustive_binary_search"]
    assert search["mixings_enumerated"] == 64
    assert search["universal_solution_count"] == 0
    assert search["repair_exists"] is False
    mixing = report()["mixing_repair_audit"]
    assert mixing["every_printed_space_group_mixing_shifts_zero_or_all_five_residues"] is True
    assert mixing["no_Abelian_combination_in_plane_R_x_U1_9_x_SG_basis_repairs"] is True


def test_tau_has_no_class_preserving_h():
    obstruction = report()["full_CFT_obstruction"]
    assert obstruction["rho2_tau_equals_tau_minus_e4"] is True
    assert obstruction["rho2_tau_in_conjugacy_orbit"] is False
    assert obstruction["no_h_tau_in_space_group"] is True
    scan = obstruction["all_odd_sum_plane_R_combinations"]
    assert scan["combinations_tested"] == 32
    assert scan["class_preserving_count"] == 0
    assert scan["every_candidate_fails_class_preservation"] is True


def test_fail_closed_terminal_decision():
    terminal = report()["terminal_decision"]
    assert terminal["conditional_92_state_charge_reconstruction"] == "PASS"
    assert terminal["corrected_non_Abelian_anomaly_universality"] == "FAIL"
    assert terminal["all_32_W_charge_2_plane_R_class_preserving_actions"] == "FAIL"
    assert terminal["physical_symmetry_no_go_proved"] is False
    assert terminal["strict_G1_closed"] is False
    assert terminal["gate_promotion"] == "NONE"


def test_generated_json_core_matches_builder_when_present():
    path = V60.JSON_PATH
    if path.exists():
        stored = json.loads(path.read_text(encoding="utf-8"))
        assert stored["canonical_core_sha256"] == report()["canonical_core_sha256"]
