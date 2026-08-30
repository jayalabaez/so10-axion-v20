from __future__ import annotations

import json

import numpy as np

import susy_v51_representation_faithful_mediator_moose_audit as audit


EXPECTED_CORE_SHA256 = "011af19f4825da85cc073fc58c12b7308355d2e486e2a1f12135dc0ea7cadf7b"
EXPECTED_LINK_JACOBIAN_SHA256 = (
    "fd3345516989a5e015d9bdb1d4f21eb839e27288e45610434f96be23377f88b8"
)


def test_covariant_minimal_link_jacobian_has_exact_finite_field_rank() -> None:
    matrices = audit.link_constraint_jacobians()
    jacobian = matrices["minimal"]
    assert jacobian.shape == (567, 612)
    assert matrices["orthogonality"].shape == (55, 612)
    assert matrices["invariant_pairing"].shape == (256, 612)
    assert matrices["contracted_clifford"].shape == (256, 612)
    rank, pivots, residual = audit.gaussian_integer_mod_rank(jacobian)
    assert residual == 0.0
    assert rank == len(pivots) == 567
    assert len(set(pivots)) == 567
    assert audit.matrix_sha256(jacobian) == EXPECTED_LINK_JACOBIAN_SHA256


def test_modular_certificate_uses_a_valid_gaussian_integer_map() -> None:
    jacobian = audit.link_constraint_jacobians()["minimal"]
    rank_13, _, _ = audit.gaussian_integer_mod_rank(
        jacobian, prime=13, image_of_i=5
    )
    assert (5 * 5 + 1) % 13 == 0
    assert rank_13 == 567


def test_all_45_spin_tangents_are_independent_and_annihilated() -> None:
    jacobian = audit.link_constraint_jacobians()["minimal"]
    tangents = audit.explicit_spin_tangents()
    assert tangents.shape == (612, 45)
    rank, _, residual = audit.gaussian_integer_mod_rank((2.0 * tangents).T)
    assert residual == 0.0
    assert rank == 45
    assert audit.maximum_abs(jacobian @ tangents) == 0.0


def test_invariant_pairing_removes_exactly_the_common_scaling_modulus() -> None:
    certificate = audit.link_rigidity_certificate()
    assert certificate["without_invariant_pairing_full_Clifford_rank"] == 566
    assert certificate["without_invariant_pairing_nullity"] == 46
    assert certificate["extra_modulus_without_pairing"] == 1
    assert certificate["complex_rank_exact"] == 567
    assert certificate["complex_nullity_exact"] == 45
    assert certificate["certified_minor_shape"] == [567, 567]
    assert certificate["certified_minor_nonzero_mod_prime"]
    multipliers = certificate["multiplier_representation_table"]
    assert [row["complex_components"] for row in multipliers] == [55, 256, 256]
    assert multipliers[2]["representation"] == "(bar16_left,16_right)"
    orbit = certificate["finite_group_orbit_certificate"]
    assert len(orbit["trials"]) == 3
    assert orbit["worst_residual"] < 1.0e-12


def test_cartesian_PS_parity_has_8_plus_8_split_and_21_generator_centralizer() -> None:
    certificate = audit.ps_parity_certificate()
    for block in certificate["chirality_blocks"].values():
        assert block["Hermitian_residual"] == 0.0
        assert block["involution_residual"] == 0.0
        assert block["trace"] == 0.0
        assert block["plus_projector_rank"] == 8
        assert block["minus_projector_rank"] == 8
        assert block["commuting_Spin10_generator_count"] == 21
        assert block["noncommuting_Spin10_generator_count"] == 24


def test_rectangular_hopping_keeps_only_the_32_selected_PS_profiles() -> None:
    desired, unwanted = audit.hopping_matrices()
    certificate = audit.hopping_certificate()
    assert desired.shape == (4, 5)
    assert np.linalg.matrix_rank(desired) == 4
    assert unwanted.shape == (4, 4)
    assert np.linalg.matrix_rank(unwanted) == 4
    assert abs(np.linalg.det(unwanted) - 1.0) < 1.0e-14
    assert certificate["desired_nullity"] == 1
    assert certificate["unwanted_nullity"] == 0
    assert certificate["total_chiral_profile_count"] == 32
    assert certificate["additional_uncontrolled_transport_zero_modes"] == 0
    assert certificate["desired_formula_residual"] < 1.0e-14
    assert certificate["unwanted_formula_residual"] < 1.0e-14


def test_host_and_source_ordinary_anomaly_ledgers_cancel_exactly() -> None:
    certificate = audit.anomaly_certificate()
    assert certificate["host_selected_totals"][
        "U1F_SU2L_squared_doubled"
    ] == -12
    assert certificate["host_visible_totals"][
        "U1F_SU2L_squared_doubled"
    ] == 12
    assert certificate["host_selected_totals"][
        "U1F_SU2R_squared_doubled"
    ] == 12
    assert certificate["host_visible_totals"][
        "U1F_SU2R_squared_doubled"
    ] == -12
    assert all(value == 0 for value in certificate["host_complete_totals"].values())
    assert all(value == 0 for value in certificate["source_spin10_totals"].values())


def test_exact_source_orbit_is_bound_and_source_side_Rxi_spectra_pair() -> None:
    certificate = audit.source_side_rxi_certificate()
    source = certificate["source_orbit_input"]
    assert source["canonical_core_valid"]
    assert source["declared_core_sha256"] == (
        "d8718c1feee465940b8362c9a43d446448eebbf60481b42e035ef5f36d4e2d95"
    )
    assert source["Q_shape"] == [465, 22]
    assert source["Q_exact_rank"] == 22
    assert source["projector_shape"] == [465, 465]
    assert source["projector_rank"] == 443
    assert source["Gram_diagonal"] == [2] + [7] * 20 + [18]
    assert source["published_U1F_Theta_charges"] == [3, -3]
    assert source["published_U1F_column_matches_Theta_charges"]
    assert certificate["source_broken_Spin_generators"] == 21
    assert certificate["all_source_broken_D_full_rank"]
    assert certificate["worst_broken_vector_Goldstone_pairing_residual"] < 2.0e-14
    assert certificate["unbroken_Spin_generators"] == 24
    assert certificate["unbroken_vector_zero_modes_per_generator"] == 1
    assert certificate["unbroken_nonzero_spectral_pairing_residual"] < 2.0e-14
    assert certificate["shared_U1F"]["source_orbit_norm_squared"] == 18
    assert certificate["shared_U1F"]["primitive_Theta_charges"] == [3, -3]
    assert certificate["shared_U1F"]["candidate_charge_norm_squared"] == 18
    assert certificate["shared_U1F"]["candidate_source_normalization_matches"]
    hessian = certificate["source_hessian_input"]
    assert hessian["canonical_core_valid"]
    assert hessian["declared_core_sha256"] == (
        "54e9caa653b03dec77cbd388595a2d3dbcb828e2dbebf6d9b46bed77b038fee4"
    )
    assert hessian["all_465_F_terms_exact_zero"]
    assert hessian["H_shape"] == [465, 465]
    assert hessian["H_exact_rank"] == 443
    assert hessian["H_exact_nullity"] == 22
    assert hessian["kernel_equals_gauge_orbit"]
    assert hessian["HQ_exact_zero_all_46_columns"]
    assert hessian["physical_pullback_shape"] == [443, 443]
    assert hessian["physical_pullback_rank_mod_13"] == 443
    assert hessian["physical_pullback_determinant_mod_13"] == 8
    assert hessian["physical_pullback_nondegenerate"]

    combined = certificate["combined_host_PS_source_SU5"]
    assert combined["generator_partition"] == {
        "PS_intersection_SU5__SM": 12,
        "PS_only": 9,
        "SU5_only": 12,
        "neither": 12,
        "sum": 45,
    }
    assert combined["both_SM"]["massless_vectors_per_generator"] == 1
    assert combined["PS_only"]["D_rank"] == 5
    assert combined["SU5_only"]["D_rank"] == 4
    assert combined["neither"]["D_rank"] == 4
    assert combined["neither"]["uneaten_chirals_per_generator"] == 1
    assert combined["total_uneaten_A5_like_chirals"] == 12
    for row in combined["neither"]["representative_norm_cases"]:
        assert row["D_shape"] == [5, 4]
        assert row["D_rank"] == 4
        assert row["vector_zero_modes"] == 0
        assert row["Goldstone_zero_modes"] == 1
        assert row["nonzero_spectral_pairing_residual"] < 2.0e-14


def test_dynamical_multiplier_field_content_has_a_fatal_small_perturbative_window() -> None:
    certificate = audit.perturbativity_certificate(0.73)
    assert certificate["per_edge_index_at_left_site"] == 106
    assert certificate["per_edge_index_at_right_site"] == 182
    assert certificate["interior_site"]["sum_T"] == 304
    assert certificate["interior_site"]["b_one_loop"] == -280
    assert certificate["source_site"]["sum_T"] == 316
    assert certificate["source_site"]["b_one_loop"] == -292
    assert certificate["interior_site"]["Landau_pole_over_link_scale"] < 1.70
    assert certificate["source_site"]["Landau_pole_over_link_scale"] < 1.67
    assert not certificate["controlled_perturbative_window"]
    assert "contradicts" in certificate["nondynamical_multiplier_limit"]


def test_vectorlike_mediator_elimination_is_exact_and_decoupling_is_explicit() -> None:
    certificate = audit.mediator_elimination_certificate()
    assert certificate["mass_determinant_abs"] > 0.0
    assert certificate["F_Y_residual"] < 1.0e-14
    assert certificate["F_Z_residual"] < 1.0e-14
    assert certificate["effective_superpotential_residual"] < 1.0e-14
    assert certificate["inverse_mass_finite"]
    assert certificate["anomaly_pair_example"]["U1_cubed_sum_per_rep_dimension"] == 0


def test_operator_frontier_is_capability_not_fake_instantiation() -> None:
    coverage = audit.operator_coverage()
    assert coverage["tree_holomorphic"]["pure_source_quartic_directions"] == 23
    assert coverage["tree_holomorphic"]["source_collar_schema_rows"] == 176
    feasibility = coverage["V51_feasibility_input"]
    assert feasibility["canonical_core_valid"]
    assert feasibility["declared_core_sha256"] == feasibility[
        "recomputed_core_sha256"
    ]
    assert len(feasibility["declared_core_sha256"]) == 64
    assert coverage["tree_holomorphic"]["low_degree_rows_resolved"] == 48
    assert coverage["tree_holomorphic"]["low_degree_nonempty"] == 20
    assert coverage["tree_holomorphic"]["low_degree_empty"] == 28
    assert coverage["tree_holomorphic"]["PS_primitives_resolved"] == 34
    assert coverage["tree_holomorphic"]["degree_four_rows_pending"] == 120
    assert not coverage["tree_holomorphic"]["all_rows_instantiated_now"]
    assert coverage["Kahler"]["full_V49_Hermitian_basis"] == "NOT GENERATED OR MATCHED"
    assert coverage["gauge_kinetic_and_FI"]["status"] == "NOT COMPUTED"


def test_report_passes_candidate_C2_but_fail_closes_G2() -> None:
    report = audit.build_report()
    assert report["gate_effect"]["C2"].startswith("CANDIDATE_LOCALITY_PASS_ONLY")
    for clause in ("C3", "C4", "C5", "C7"):
        assert report["gate_effect"][clause].startswith("PARTIAL")
    assert report["gate_effect"]["C6"].startswith("UNASSESSED_FOR_NEW_ACTION")
    assert report["gate_effect"]["candidate_UV_viability"].startswith("FAIL")
    assert not report["gate_effect"]["G2_closed"]
    assert report["gate_effect"]["gates_promoted"] == []
    assert report["kill_tests"]["combined_endpoint_residual_chirals_are_not_hidden"]
    assert report["kill_tests"]["short_Landau_window_is_not_hidden"]
    assert report["n_failed_integrity_checks"] == 0
    assert all(report["integrity_checks"].values())


def test_artifacts_are_current_hashed_and_upstreams_unchanged() -> None:
    report = audit.build_report()
    audit.validate(report)
    assert report["core_sha256"] == audit.canonical_sha(report)
    assert report["core_sha256"] == EXPECTED_CORE_SHA256
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(report)
    for name, digest in report["provenance"]["upstream_sha256"].items():
        if digest is not None:
            assert digest == audit.sha256_file(audit.ROOT / name)
