from __future__ import annotations

import json

import numpy as np

import susy_v52_low_index_source_audit as v52
import susy_v53_elementary_filter_hessian_audit as audit


def test_driver_vacuum_is_F_flat_and_nonsingular() -> None:
    vacuum = audit.vacuum_audit()
    assert vacuum["P"] == vacuum["v"] == 1
    assert vacuum["X"] == 0
    assert vacuum["F_P"] == vacuum["F_X"] == 0
    assert vacuum["vector_F_nonzero_count"] == 0
    assert vacuum["driver_hessian"] == [[0, 2], [2, 0]]
    assert vacuum["driver_rank"] == 2
    assert vacuum["driver_nullity"] == 0


def test_filter_hessian_is_exact_symmetric_integer_matrix() -> None:
    matrix = audit.filter_hessian()
    assert matrix.shape == (40, 40)
    assert np.array_equal(matrix, matrix.T)
    assert np.issubdtype(matrix.dtype, np.integer)


def test_filter_has_full_color_rank_and_one_weak_pair() -> None:
    result = audit.filter_rank_audit()
    assert result["full_rank"] == 36
    assert result["full_nullity"] == 4
    assert result["color_shape"] == [24, 24]
    assert result["color_rank"] == 24
    assert result["color_nullity"] == 0
    assert result["weak_shape"] == [16, 16]
    assert result["weak_rank"] == 12
    assert result["weak_nullity"] == 4
    assert result["coefficient_equality_required"] is False


def test_generic_H1_mass_fills_filter_kernel() -> None:
    result = audit.filter_rank_audit()
    assert result["H1_squared_unit_filler_rank"] == 40
    assert result["generic_filler_lifts_intended_kernel"] is True


def test_full_same_action_hessian_rank_and_Ward_identity() -> None:
    hessian = audit.full_hessian_numerator()
    orbit = audit.full_orbit_numerator()
    assert hessian.shape == (218, 218)
    assert orbit.shape == (218, 45)
    assert np.array_equal(hessian, hessian.T)
    assert v52.modular_rank(v52._modular_matrix(hessian)) == 181
    assert v52.modular_rank(v52._modular_matrix(orbit)) == 33
    assert np.count_nonzero(hessian @ orbit) == 0
    assert 218 - 181 == 33 + 4


def test_dynkin_budget_includes_four_vectors_and_matter() -> None:
    result = audit.perturbativity_audit()
    assert result["E54_A45_B45_C16_barC16_T"] == 32
    assert result["four_10_filter_T"] == 4
    assert result["three_matter_16_T"] == 6
    assert result["total_chiral_T"] == 42
    assert result["one_loop_b"] == 18
    assert result["above_100x"] is True
    assert result["above_1000x"] is True


def test_report_has_exact_nullity_decomposition_and_fail_closed_selector() -> None:
    report = audit.build_report()
    geometry = report["full_same_action_geometry"]
    assert geometry["rank_decomposition"] == {"source": 143, "filter": 36, "driver": 2, "total": 181}
    assert geometry["nullity_decomposition"] == {"broken_gauge_orbit": 33, "intended_weak_Higgs": 4, "extra": 0}
    assert report["selector_fail_closed"]["explicit_shaping_symmetry_supplied"] is False
    assert report["gate_effect"]["elementary_same_action_vacuum_and_Hessian"] == "CLOSED"
    assert report["gate_effect"]["naturalness_under_complete_selector"] == "OPEN"
    assert report["gate_effect"]["G2"] == "OPEN"
    assert report["gate_effect"]["clause_promotions"] == []


def test_hash_and_artifacts_are_current() -> None:
    report = audit.check_artifacts()
    assert audit.canonical_sha(report) == report["core_sha256"]
    disk = json.loads(audit.JSON_PATH.read_text(encoding="utf-8"))
    assert disk["core_sha256"] == report["core_sha256"]
    assert report["core_sha256"] in audit.MD_PATH.read_text(encoding="utf-8")
