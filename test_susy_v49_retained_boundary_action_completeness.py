from __future__ import annotations

import json

import numpy as np

import susy_v49_retained_boundary_action_completeness as audit


def test_exact_pure_source_quartic_basis_has_12_sectors_and_23_directions() -> None:
    basis = audit.pure_source_quartic_basis()
    assert basis["sector_count"] == 12
    assert basis["direction_count"] == 23
    observed = {row["monomial"]: row["exact_invariant_multiplicity"] for row in basis["rows"]}
    assert observed == {
        "S^4": 1,
        "S^2 ThetaPlus ThetaMinus": 1,
        "S^2 Phi^2": 1,
        "S^2 Sigma barSigma": 1,
        "S Phi^3": 1,
        "S Phi Sigma barSigma": 1,
        "ThetaPlus^2 ThetaMinus^2": 1,
        "ThetaPlus ThetaMinus Phi^2": 1,
        "ThetaPlus ThetaMinus Sigma barSigma": 1,
        "Phi^4": 4,
        "Phi^2 Sigma barSigma": 6,
        "Sigma^2 barSigma^2": 4,
    }


def test_every_quartic_direction_has_a_unique_coefficient_and_channel_label() -> None:
    rows = audit.pure_source_quartic_basis()["rows"]
    channels = [channel for row in rows for channel in row["channels"]]
    assert [channel["global_direction"] for channel in channels] == list(range(1, 24))
    assert len({channel["coefficient"] for channel in channels}) == 23
    assert all(row["U1F_charge"] == 0 for row in rows)
    assert all(row["exact_invariant_multiplicity"] == len(row["channels"]) for row in rows)


def test_ps_mu_and_complete_Hc_profile_coordinates_are_retained() -> None:
    report = audit.build_report()
    ps = report["PS_wall_action"]
    collar = report["source_collar_holomorphic_basis"]
    assert any("mu_H" in item for item in ps["superpotential"])
    assert ps["spinor_cubic_count"] == 19
    assert len(collar["HH_known_nonempty_degree_three_witnesses"]) == 4
    assert len(collar["HH_known_nonempty_degree_four_witnesses"]) == 12
    assert len(collar["HcHc_known_nonempty_degree_three_witnesses"]) == 4
    assert len(collar["HcHc_known_nonempty_degree_four_witnesses"]) == 12
    assert len(collar["HcH_odd_profile_degree_two"]) == 4
    assert len(collar["HcH_odd_profile_degree_three"]) == 8
    assert {
        degree: len(rows)
        for degree, rows in collar["HH_charge_complete_candidate_sectors_by_degree"].items()
    } == {"2": 2, "3": 10, "4": 30}
    assert {
        degree: len(rows)
        for degree, rows in collar["HcHc_charge_complete_candidate_sectors_by_degree"].items()
    } == {"2": 2, "3": 10, "4": 30}
    assert {
        degree: len(rows)
        for degree, rows in collar["HcH_charge_complete_candidate_sectors_by_degree"].items()
    } == {"2": 4, "3": 20, "4": 60}
    assert len(collar["HcH_degree_four_cross_pair_nonempty_witnesses"]) == 4
    for family in ("HH", "HcHc", "HcH"):
        assert all(
            row["U1F_charge"] == 0
            for rows in collar[f"{family}_charge_complete_candidate_sectors_by_degree"].values()
            for row in rows
        )


def test_mixed_Kahler_census_has_all_zero_and_one_insertion_sectors() -> None:
    basis = audit.mixed_kahler_basis()
    assert basis["counts"] == {
        "known_nonempty_zero_insertion_witnesses": 8,
        "known_nonempty_one_insertion_witnesses": 32,
        "charge_complete_zero_insertion_candidates": 16,
        "charge_complete_one_insertion_candidates": 80,
        "known_nonempty_S": 8,
        "known_nonempty_Phi": 8,
        "known_nonempty_Theta": 8,
        "known_nonempty_Sigma": 4,
        "known_nonempty_barSigma": 4,
    }
    assert len(set(basis["known_nonempty_zero_insertion_witnesses"])) == 8
    assert len(set(basis["known_nonempty_one_chiral_insertion_witnesses_plus_hc"])) == 32
    assert len(basis["charge_complete_zero_insertion_candidates"]) == 16
    assert len(basis["charge_complete_one_chiral_insertion_candidates_plus_hc"]) == 80
    assert all(
        row["U1F_charge"] == 0
        for key in (
            "charge_complete_zero_insertion_candidates",
            "charge_complete_one_chiral_insertion_candidates_plus_hc",
        )
        for row in basis[key]
    )


def test_pure_source_Kahler_basis_has_six_metrics_and_thirteen_cubic_sectors() -> None:
    basis = audit.pure_source_kahler_basis()
    assert basis["counts"] == {"quadratic": 6, "cubic": 13}
    assert len(set(basis["quadratic_metric_sectors"])) == 6
    assert len(set(basis["cubic_one_over_Lambda_sectors_plus_hc"])) == 13
    assert "positive definite" in basis["positivity"]


def test_source_wall_gauge_and_FI_coordinates_are_retained() -> None:
    basis = audit.source_wall_gauge_basis()
    assert len(basis["constant_gauge_kinetic"]) == 2
    assert len(basis["one_source_gauge_kinetic"]) == 3
    assert "cS10" in basis["one_source_gauge_kinetic"][0]
    assert "cPhi" in basis["one_source_gauge_kinetic"][2]
    assert "xiF_L" in basis["FI"]
    assert "positive real part" in basis["conditions"]


def test_IBP_module_has_two_independent_coordinates_per_channel() -> None:
    for channel_count in (1, 2, 4, 7):
        normal = audit.derivative_normal_form(channel_count)
        assert normal["relation_rank"] == channel_count
        assert normal["quotient_dimension"] == 2 * channel_count
        assert normal["representative_residual"] < 1.0e-14
    normal = audit.derivative_normal_form()
    assert "Do not set O_minus or M_o to zero" in normal["EOM_reduction"]


def test_strong_wall_invalidates_fixed_derivative_Hc_suppression() -> None:
    certificate = audit.strong_wall_scaling_certificate()
    rows = list(certificate["epsilon_scan"].values())
    hchc = [row["average_Hc_Xi_Hc"] for row in rows]
    mixed = [row["average_rho_odd_H_C_Hc"] for row in rows]
    assert abs(certificate["HcHc_value"]) > 1.0e-5
    assert abs(certificate["odd_mixed_value"]) > 1.0e-5
    assert np.max(np.abs(np.asarray(hchc) - hchc[0])) < 1.0e-14
    assert np.max(np.abs(np.asarray(mixed) - mixed[0])) < 1.0e-14
    assert "O(1)" in certificate["conclusion"]


def test_full_A_Xi_C_generator_preserves_the_boundary_symplectic_form() -> None:
    certificate = audit.hamiltonian_transfer_certificate()
    assert certificate["generator_Hamiltonian_residual"] < 1.0e-13
    assert certificate["path_ordered_transfer_symplectic_residual"] < 1.0e-11
    assert abs(certificate["determinant"] - 1.0) < 1.0e-11


def test_Kahler_canonicalization_propagates_Yukawa_shift_covariantly() -> None:
    certificate = audit.field_redefinition_certificate()
    assert max(certificate.values()) < 1.0e-11


def test_artifact_is_fail_closed_for_full_G2_and_point_locality() -> None:
    report = audit.build_report()
    assert report["adversarial_verdict"]["C1_retained_sector"] == "PASS_ABSTRACTLY"
    assert report["adversarial_verdict"]["full_G2"] == "OPEN"
    assert "bilocal" in report["gauge_covariance_and_locality"]["limitation"]
    assert any(
        "point-local five-dimensional" in item
        for item in report["scope_contract"]["not_claimed"]
    )


def test_integrity_hash_and_rendered_files() -> None:
    report = audit.build_report()
    assert report["n_failed_integrity_checks"] == 0
    assert all(report["integrity_checks"].values())
    assert audit.canonical_sha(report) == report["core_sha256"]
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(report)
