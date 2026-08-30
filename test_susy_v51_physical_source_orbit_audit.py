from __future__ import annotations

import json

import susy_v51_physical_source_orbit_audit as audit


EXPECTED_Q_SHA256 = "75d8ffd98156a4ac4726bb0841ff3f325e1671ec85a75e013afddd182cd0ee45"
EXPECTED_Z_SHA256 = "52996eb51ccbad6bdf19d5ea54c8b33336215060f188386433d4f62a56a250d8"
EXPECTED_STABILIZER_SHA256 = "937258e0ab3267cbd557578052b6c0851db92fca7c2b73744ec039e597d60efd"


def test_coordinate_chart_is_exactly_465_complex_components() -> None:
    labels = audit.coordinate_labels()
    assert len(labels) == 465
    assert labels[0] == "Phi[0,1,2,3]"
    assert labels[209] == "Phi[6,7,8,9]"
    assert labels[210].startswith("Sigma[")
    assert labels[336].startswith("barSigma[")
    assert labels[-3:] == ("STheta", "ThetaPlus", "ThetaMinus")


def test_aligned_su5_shapes_have_exact_chirality_and_normalization() -> None:
    certificate = audit.representation_certificate()
    assert certificate["vev"]["Phi_support_size"] == 10
    assert certificate["vev"]["Phi_coefficients_all_one"] is True
    assert certificate["vev"]["Sigma_independent_coordinate_norm_squared"] == ["1", "0"]
    assert certificate["vev"]["barSigma_independent_coordinate_norm_squared"] == ["1", "0"]
    assert all(certificate["exact_hodge_checks"].values())


def test_full_so10_orbit_has_rank_21_and_24_stabilizers() -> None:
    certificate = audit.orbit_certificate()["full_SO10_map"]
    assert certificate["shape"] == [465, 45]
    assert certificate["exact_Gram_rank"] == 21
    assert certificate["exact_stabilizer_nullity"] == 24
    assert certificate["all_24_integer_stabilizer_vectors_annihilate_the_vacuum"] is True
    assert certificate["integer_stabilizer_basis_sha256"] == EXPECTED_STABILIZER_SHA256


def test_published_q_is_exact_rank_22_with_frozen_sparse_hash() -> None:
    certificate = audit.orbit_certificate()
    matrix = certificate["selected_broken_map_Q"]
    assert matrix["shape"] == [465, 22]
    assert matrix["nonzero_entries"] == 474
    assert matrix["canonical_matrix_sha256"] == EXPECTED_Q_SHA256
    assert len(matrix["sparse_entries"]) == 474
    assert certificate["selected_Gram"]["exact_rank"] == 22


def test_selected_gram_is_canonical_diagonal() -> None:
    gram = audit.orbit_certificate()["selected_Gram"]
    assert gram["diagonal"] == ["2", *("7" for _ in range(20)), "18"]
    assert gram["off_diagonal_exact_zero"] is True
    assert gram["determinant"] == "2872521586714032036"
    assert gram["positive_definite"] is True


def test_projector_is_exact_rank_443_and_annihilates_q() -> None:
    projector = audit.orbit_certificate()["physical_projector_Z"]
    assert projector["shape"] == [465, 465]
    assert projector["nonzero_entries"] == 7019
    assert projector["canonical_projector_sha256"] == EXPECTED_Z_SHA256
    assert projector["Hermitian_exact"] is True
    assert projector["ZQ_exact_zero"] is True
    assert projector["trace"] == "443"
    assert projector["rank"] == 443
    assert projector["inverse_times_Gram_diagonal"] == ["1"] * 22


def test_legacy_p_delta_hessian_is_rejected_not_relabelled() -> None:
    legacy = audit.legacy_compatibility_audit()
    assert legacy["legacy_exact_orbit_rank"] == 33
    assert legacy["legacy_exact_stabilizer_dimension"] == 12
    assert legacy["Phi_shapes_differ_exactly"] is True
    assert legacy["five_form_shapes_are_orthogonal"] is True
    assert legacy["Hessian_transfer_allowed"] is False


def test_hessian_contract_remains_fail_closed() -> None:
    hessian = audit.hessian_availability_audit()
    assert hessian["new_V51_kinematic_inputs"] == {
        "Cartesian_465_by_22_Q": True,
        "exact_rank_22": True,
        "Hermitian_rank_443_Z": True,
    }
    assert all(hessian["missing_dynamic_inputs"].values())
    assert hessian["physical_Hessian_pullback_executed"] is False


def test_report_passes_without_promoting_a_gate() -> None:
    report = audit.build_report()
    assert report["status"] == audit.STATUS
    assert report["n_failed"] == 0
    assert report["failures"] == []
    assert report["gate_effect"]["G2_clause_promoted"] is None
    assert report["gate_effect"]["G1_to_G8_promoted"] == []
    assert report["core_sha256"] == audit.canonical_sha(report)


def test_committed_artifacts_are_reproducible() -> None:
    audit.check_artifacts()
    observed = json.loads(audit.JSON_PATH.read_text(encoding="utf-8"))
    assert observed["core_sha256"] == audit.canonical_sha(observed)
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(observed)
