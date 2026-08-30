from __future__ import annotations

from fractions import Fraction

import canonical_g3_physical_ew_global_vacuum_v21 as g3


def test_report_closes_only_canonical_g3():
    report = g3.build_report()
    assert report["n_failed"] == 0
    assert report["closure_complete"] is True
    assert report["scope_boundary"] == {
        "canonical_G3_closed": True,
        "absolute_electroweak_hierarchy_h_174_GeV_proved": False,
        "canonical_G4_closed": False,
        "canonical_G5_through_G8_closed": False,
    }


def test_complete_891_direction_ledger_and_zero_higher_operators():
    ledger = g3.complete_direction_ledger()
    assert ledger["degree_direction_counts"] == {
        "2": 5,
        "3": 6,
        "4": 40,
        "5": 119,
        "6": 721,
    }
    assert ledger["canonical_total_real_directions"] == 891
    assert ledger["degree_at_most_four_real_directions"] == 51
    assert ledger["zero_dimension_five_directions"] == 119
    assert ledger["zero_dimension_six_directions"] == 721
    assert len(ledger["nonzero_coefficients"]) == 28


def test_sos_expands_to_every_and_only_selected_coefficient():
    report = g3.sos_decomposition()
    observed = {}
    for term in report["terms"]:
        assert term["nonnegative"] is True
        for key, value in term["expansion"].items():
            observed[key] = observed.get(key, Fraction()) + Fraction(value)
    assert observed == g3.COEFFICIENTS
    assert report["expanded_constant"] == "3127/2500"
    assert report["global_lower_bound"] == "V>=-1 on all 486 real fields"


def test_exact_stationarity_rank_kernel_and_axion():
    row = g3.exact_hessian_certificate()
    assert row["exact_field_term_value"] == "-5627/2500"
    assert row["exact_constant"] == "3127/2500"
    assert row["exact_total_value"] == "-1"
    assert row["exact_gradient_nonzero_entries"] == 0
    assert row["modular_rank_prime"] == 1009
    assert row["modular_rank"] == row["exact_rank"] == 448
    assert row["principal_minor_determinant_mod_prime"] == 961
    assert row["exact_nullity"] == 38
    assert row["gauge_orbit_rank"] == 37
    assert row["full_symmetry_orbit_rank"] == 38
    assert row["intended_axion_direction_count"] == 1
    assert row["all_448_non_symmetry_modes_strictly_positive"] is True


def test_global_zero_locus_is_one_connected_orbit():
    orbit = g3.global_orbit_certificate()
    assert orbit["broken_gauge_directions"] == 37
    assert orbit["zero_locus_parameter_dimensions"]["total"] == 38
    assert orbit["exact_stabilizer_is_SU3C_plus_U1em"] is True
    assert orbit["all_global_minima_one_continuous_symmetry_orbit"] is True
    assert orbit["no_deeper_extremum"] is True
    assert orbit["no_disconnected_equal_minimum"] is True


def test_exact_invariant_identities_are_bound():
    identities = g3.invariant_identities()
    assert identities["Phi_quartic_exact_J_basis"] == {
        "J0": "-21/200",
        "J2": "2467/28800",
        "J3": "-77/3200",
        "J4": "119/115200",
    }
    assert identities["A_square_exact_weights"] == ["40", "72", "28", "-8", "-12", "12"]
    assert identities["A_square_exact_residuals"] == ["0"] * 6
    assert identities["Phi_Sigma_residual_Gram_diagonal"] == [64, 32, 32, 24]
    assert identities["H_Sigma_Fierz_identity"] == "I1-I45=||i_H Sigma||^2"


def test_adversarial_coefficient_mutation_breaks_sos_identity(monkeypatch):
    mutated = dict(g3.COEFFICIENTS)
    mutated["O35_B02_H_Sigma_hermitian"] += Fraction(1, 101)
    monkeypatch.setattr(g3, "COEFFICIENTS", mutated)
    try:
        g3.sos_decomposition()
    except ArithmeticError as error:
        assert "does not reproduce" in str(error)
    else:
        raise AssertionError("mutated coefficient was accepted")


def test_stored_outputs_are_fresh():
    report = g3.build_report()
    assert g3.OUT_JSON.is_file()
    assert g3.OUT_MD.is_file()
    import json

    assert json.loads(g3.OUT_JSON.read_text(encoding="utf-8")) == report
    assert g3.OUT_MD.read_text(encoding="utf-8") == g3.markdown(report)
