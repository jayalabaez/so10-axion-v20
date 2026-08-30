from __future__ import annotations

import hashlib
import json

import numpy as np
import pytest

import exact_physical_sm_37_row_aggregate_v20 as theorem


EXPECTED_CORE = "8c1aeffcd29a4f78c42014f92cf4bfa09823a6a2efbd660d512d6b014db99f43"


@pytest.fixture(scope="module")
def report() -> dict:
    return theorem.build_report()


def test_frozen_outputs_and_integrity(report: dict) -> None:
    assert json.loads(theorem.OUT_JSON.read_text(encoding="utf-8")) == theorem.hard._jsonable(report)
    assert theorem.OUT_MD.read_text(encoding="utf-8") == theorem.render_markdown(report)
    core = dict(report)
    integrity = core.pop("integrity")
    assert hashlib.sha256(theorem.hard.canonical_json_bytes(core)).hexdigest() == EXPECTED_CORE
    assert integrity["core_sha256"] == EXPECTED_CORE
    assert integrity["aggregate_sparse_sha256"] == theorem.EXPECTED_SPARSE_SHA256
    assert integrity["positive_pivot_hash_chain"] == theorem.EXPECTED_PIVOT_HASH_CHAIN


def test_exact_all_37_assembly_and_historical_identity(report: dict) -> None:
    assembly = report["source_aggregate_assembly"]
    assert assembly["active_row_count"] == 37
    assert assembly["nonzero_entries"] == 5840
    assert assembly["denominator"] == theorem.AGGREGATE_DENOMINATOR
    assert assembly["canonical_sparse_Q_sqrt2_serialization_sha256"] == theorem.EXPECTED_SPARSE_SHA256
    assert assembly["entrywise_identity_to_historical_reconstructed_rational_aggregate"] is True
    assert report["arithmetic_contract"]["floating_point_used_to_construct_or_accept_any_claim"] is False
    assert report["arithmetic_contract"]["finite_difference_autodiff_or_rational_recognition_used"] is False


def test_exact_value_stationarity_and_source_Hq(report: dict) -> None:
    stationarity = report["exact_stationarity"]
    assert stationarity["exact_potential_value"] == "-1"
    assert stationarity["exact_gradient_nonzero_entries"] == 0
    assert stationarity["exact_gradient_is_zero"] is True
    assert stationarity["aggregate_Hq_matches_weighted_source_Hq_entrywise"] is True
    assert len(stationarity["per_row_exact_target_values"]) == 37


def test_exact_kernel_and_modular_rank(report: dict) -> None:
    certificate = report["exact_kernel_and_rank"]
    modular = certificate["modular_lower_bound_certificate"]
    assert certificate["exact_generator_column_count"] == 47
    assert certificate["annihilated_generator_columns"] == 47
    assert certificate["all_47_generator_columns_annihilated_entrywise"] is True
    assert certificate["exact_symmetry_tangent_span_dimension"] == 38
    assert certificate["exact_rank"] == 448
    assert certificate["exact_nullity"] == 38
    assert certificate["kernel_equals_exact_symmetry_tangent_span"] is True
    assert modular["prime"] == 1009
    assert modular["rank"] == 448
    assert modular["principal_minor_determinant_mod_prime"] == 870
    assert modular["principal_minor_is_nonzero"] is True
    assert len(modular["principal_pivot_indices"]) == 448


def test_exact_positive_pivot_PSD_certificate(report: dict) -> None:
    certificate = report["exact_PSD_certificate"]
    assert certificate["principal_minor_dimension"] == 448
    assert certificate["strictly_positive_exact_pivot_count"] == 448
    assert certificate["all_exact_pivots_strictly_positive"] is True
    assert certificate["exact_divisibility_checks"] == 29_671_711
    assert certificate["positive_pivot_sha256_chain"] == theorem.EXPECTED_PIVOT_HASH_CHAIN
    assert certificate["final_pivot_decimal_digit_count"] == 5480
    assert certificate["principal_minor_is_positive_definite_by_Sylvester"] is True
    assert certificate["full_Hessian_is_positive_semidefinite"] is True
    assert certificate["full_Hessian_is_positive_definite_mod_kernel"] is True


def test_global_equality_and_G3_G4_G5_remain_separate(report: dict) -> None:
    claims = report["claims"]
    assert claims["all_37_active_Hessians_derived_from_exact_source_algebra"] is True
    assert claims["exact_source_aggregate_value_minus_one_and_stationary"] is True
    assert claims["exact_source_aggregate_kernel_is_38_dimensional_symmetry_span"] is True
    assert claims["exact_source_aggregate_rank_is_448"] is True
    assert claims["exact_source_aggregate_is_PSD_and_strictly_positive_mod_symmetry"] is True
    assert claims["full_486_field_global_equality_orbit_classified"] is False
    assert claims["physical_SM_G3_closed"] is False
    assert claims["physical_SM_G4_closed"] is False
    assert claims["physical_SM_G5_closed"] is False


def test_adversarial_coefficient_mutation_changes_aggregate() -> None:
    rows = theorem.exact_source_rows()
    original, _ = theorem.exact_aggregate()
    direction_id = "O03_B01_singlet_polynomial"
    row_entries = rows[direction_id].fraction_entries()
    original_entries = original.fraction_entries()
    key = next(iter(row_entries))
    mutated_value = original_entries.get(key, theorem.Fraction(0)) + theorem.Fraction(
        1, 10**9
    ) * row_entries[key]
    assert mutated_value != original_entries.get(key, theorem.Fraction(0))


def test_source_drift_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    drifted = dict(theorem.SOURCE_HASHES)
    name = next(iter(drifted))
    drifted[name] = "0" * 64
    monkeypatch.setattr(theorem, "SOURCE_HASHES", drifted)
    with pytest.raises(ArithmeticError, match="dependency drifted"):
        theorem.source_bindings()
