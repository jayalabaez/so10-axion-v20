from __future__ import annotations

import hashlib
import json

import numpy as np
import pytest

import exact_physical_sm_last_six_hessians_v20 as theorem


EXPECTED_CORE = "07666dc9ea513c579ed5f82d19f9b636b21926f552dab49b4b02af288762348b"
EXPECTED_ROWS = "8dc05342e8e77784d339692d796f88c7191e8141cf6fd4a6cb770dcc56dd37aa"
EXPECTED_VALUES = {
    "O14_B01_Phi_Sigma_Sigmadag_cubic": "1/25",
    "O35_B01_H_Sigma_hermitian": "1/50",
    "O35_B02_H_Sigma_hermitian": "1/50",
    "O46_B01_Phi2_HdagH_channels": "1",
    "O46_B02_Phi2_HdagH_channels": "0",
    "O46_B03_Phi2_HdagH_channels": "3/5",
}


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
    assert integrity["ordered_six_row_digest_sha256"] == EXPECTED_ROWS


def test_six_exact_rows_and_homogeneity(report: dict) -> None:
    rows = report["certified_rows"]
    assert len(rows) == 6
    assert {row["direction_id"] for row in rows} == set(EXPECTED_VALUES)
    for row in rows:
        assert row["exact_target_jet_from_homogeneity"]["value"] == EXPECTED_VALUES[row["direction_id"]]
        assert row["Hessian"]["dimension"] == 486
        assert row["Hessian"]["symmetric_entrywise_over_Q"] is True
        assert row["exact_target_jet_from_homogeneity"]["q_dot_gradient_equals_degree_times_value_exactly"] is True


def test_tensor_source_contracts(report: dict) -> None:
    certificates = report["family_certificates"]
    assert certificates["O14"]["operator_Hermitian_exactly"] is True
    assert certificates["O14"]["double_interior_table_shape"] == [10, 10, 126, 120]
    assert certificates["O35"]["exact_SO10_generator_count"] == 45
    assert certificates["O46"]["exact_Phi_interior_table_shape"] == [10, 210, 120]
    assert certificates["O46"]["exact_nonzero_45_pair_matrices"] == 1575
    assert report["arithmetic_contract"]["floating_point_used_to_construct_or_accept_Hessians"] is False


def test_all_37_available_but_aggregate_and_global_still_open(report: dict) -> None:
    assert report["scope_accounting"]["total_active_source_Hessians_available"] == 37
    claims = report["claims"]
    assert claims["all_37_active_source_Hessians_available_across_three_theorems"] is True
    assert claims["exact_37_row_aggregate_stationarity_kernel_rank_PSD_proved_here"] is False
    assert claims["full_486_field_global_equality_orbit_classified"] is False
    assert claims["physical_SM_G3_closed"] is False
    assert claims["physical_SM_G4_closed"] is False
    assert claims["physical_SM_G5_closed"] is False


def test_adversarial_row_mutation_changes_digest() -> None:
    rows, _ = theorem.exact_rows()
    original = rows["O14_B01_Phi_Sigma_Sigmadag_cubic"]
    mutated = original.numerator.copy()
    index = tuple(np.argwhere(mutated != 0)[0])
    mutated[index] += 1
    assert theorem.hard.RationalHessian.normalized(mutated, original.denominator).sha256() != original.sha256()


def test_source_drift_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    drifted = dict(theorem.SOURCE_HASHES)
    name = next(iter(drifted))
    drifted[name] = "0" * 64
    monkeypatch.setattr(theorem, "SOURCE_HASHES", drifted)
    with pytest.raises(ArithmeticError, match="dependency drifted"):
        theorem.source_bindings()
