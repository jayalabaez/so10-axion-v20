from __future__ import annotations

import hashlib
import json

import exact_g6_sm_provenance_feasibility_v20 as theorem


def test_frozen_report_matches_live_builder() -> None:
    live = theorem.build_report()
    frozen = json.loads(theorem.OUT_JSON.read_text(encoding="utf-8"))
    assert live == frozen
    assert live["n_failed"] == 0
    if theorem.EXPECTED_CORE_SHA256 != "TO_BE_FROZEN":
        assert live["core_sha256"] == theorem.EXPECTED_CORE_SHA256


def test_G89_is_not_the_standard_electromagnetic_generator() -> None:
    report = theorem.build_report()
    certificate = report["vector_10_nonconjugacy_certificate"]
    assert certificate["actual_G89"]["rank_on_real_vector_10"] == 2
    assert certificate["standard_Q3"]["rank_on_real_vector_10"] == 8
    assert (
        certificate["actual_G89"]["squared_charge_multiplicities"]
        != certificate["standard_Q3"]["squared_charge_multiplicities"]
    )


def test_selected_background_is_not_standard_SM_neutral() -> None:
    report = theorem.build_report()
    background = report["selected_background_audit"]
    delta = background["selected_Delta_quantum_numbers_in_standard_embedding"]
    assert delta["minus_Y6_squared_eigenvalue"] == 36
    assert delta["four_C2L_eigenvalue"] == 0
    assert delta["four_C2R_eigenvalue"] == 8
    assert background["selected_Delta_signed_quantum_numbers"] == {
        "B_minus_L": "-2",
        "T3R": "0",
        "Y": "-1",
        "Q": "-1",
    }
    true_singlet = background["true_SM_neutral_126bar_singlet"]
    assert true_singlet["signed_Y6"] == 0
    assert true_singlet["signed_Q3"] == 0
    assert true_singlet["Y6_annihilation_nnz"] == 0
    assert true_singlet["Q3_annihilation_nnz"] == 0
    assert true_singlet["orthogonal_to_selected_Delta_raw"]
    uniqueness = background["true_SM_singlet_uniqueness"]
    assert uniqueness["exact_rational_rank"] == 250
    assert uniqueness["exact_real_nullity"] == 2
    assert uniqueness["unique_complex_SM_singlet"]
    assert background["selected_full_target_tangents"] == {
        "standard_Q3_nnz": 10,
        "standard_Q3_norm_squared": 90,
        "actual_G89_nnz": 0,
    }


def test_coordinate_projectors_exist_but_mass_labels_do_not() -> None:
    report = theorem.build_report()
    feasibility = report["projector_feasibility"]
    assert feasibility["UV_coordinate_SO10_PS_SM_ancestry"] == "EXACTLY_RECONSTRUCTIBLE"
    assert (
        feasibility["frozen_G6_mass_eigenspace_standard_SU2L_x_U1Y_labels"]
        == "NOT_DEFINED_BY_SIMULTANEOUS_PROJECTORS"
    )
    commutants = report["mass_pencil_commutant"]
    assert commutants["actual_G89"]["nnz"] == 0
    assert commutants["standard_Y6"]["nnz"] > 0
    assert commutants["standard_Q3"]["nnz"] > 0
    assert commutants["standard_4C2L"]["nnz"] > 0


def test_naive_true_SM_singlet_swap_live_regression() -> None:
    observed = theorem.recompute_live_true_sm_swap_diagnostic()
    expected = theorem.RECORDED_TRUE_SM_SWAP_DIAGNOSTIC
    for name, target in expected.items():
        value = observed[name]
        if isinstance(target, int):
            assert value == target
        else:
            assert abs(value - target) < 2.0e-12
    assert observed["removed_signed_current_beta"] == 0.05
    assert observed["direction_rows"] == 44
    assert observed["parameter_rows"] == 51
    assert observed["naive_swap_is_stationary"] is False
    assert observed["naive_swap_is_locally_stable"] is False


def test_release_classification_fails_closed() -> None:
    classification = theorem.build_report()["classification"]
    assert classification["exact_coordinate_carrier_provenance_projectors_constructed"]
    assert classification["mathematical_tree_level_mass_factorization_remains_valid"]
    assert classification["frozen_G6_physical_U1em_provenance_complete"] is False
    assert classification["prior_positive_physical_G6_interpretation_valid"] is False
    assert (
        classification["prior_positive_mathematical_G6_as_physical_SM_spectrum_valid"]
        is False
    )
    assert classification["mathematical_physical_G6_closed"] is False
    assert classification["release_level_G6_complete"] is False
    assert classification["positive_G7_threshold_input_complete"] is False
    downgrade = theorem.build_report()["recommended_gate_downgrades"]
    assert downgrade["formal_EFT_G6_mass_factorization_under_SU3_x_U1_89"]
    assert downgrade["mathematical_physical_SM_G6"] is False
    assert downgrade["mathematical_G7"] is False


def test_terminal_report_hashes_are_frozen() -> None:
    expected = {
        theorem.OUT_JSON: theorem.EXPECTED_REPORT_RAW_SHA256["json"],
        theorem.OUT_MD: theorem.EXPECTED_REPORT_RAW_SHA256["md"],
    }
    for path, digest in expected.items():
        assert digest != "TO_BE_FROZEN"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
