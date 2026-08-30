from __future__ import annotations

import hashlib
import json

import numpy as np
import pytest

import exact_physical_sm_easy_21_hessians_v20 as theorem


EXPECTED_CORE = "b0c44e534585ae0e078218f33069d1e86b1353278a841d206ba21111819324db"
EXPECTED_ORDERED_ROWS = "acafb60a3d208efa63d2fcf7f580f14979882c4c0e08d84d99fdb52e60e2ef2b"
EXPECTED_VALUES = {
    "O03_B01_singlet_polynomial": "1/2",
    "O04_B01_singlet_polynomial": "1/50",
    "O05_B01_126bar_norm": "1/50",
    "O06_B01_Hdag_H_norm": "1",
    "O07_B01_Phi_norm": "1",
    "O17_B01_Phi_cubic": "0",
    "O20_B01_singlet_polynomial": "1/4",
    "O22_B01_singlet_polynomial": "1/100",
    "O23_B01_singlet_polynomial": "1/2500",
    "O25_B01_126bar_norm": "1/100",
    "O26_B01_126bar_norm": "1/2500",
    "O33_B01_Hdag_H_norm": "1/2",
    "O34_B01_Hdag_H_norm": "1/50",
    "O36_B01_H_self_quartics": "0",
    "O36_B02_H_self_quartics": "1",
    "O42_B01_Phi_norm": "1/2",
    "O43_B01_Phi_norm": "1/50",
    "O48_B01_Phi_self_quartics": "1",
    "O48_B02_Phi_self_quartics": "24",
    "O48_B03_Phi_self_quartics": "192",
    "O48_B04_Phi_self_quartics": "3552",
}


@pytest.fixture(scope="module")
def report() -> dict:
    return theorem.build_report()


def test_frozen_outputs_and_core_pin(report: dict) -> None:
    frozen = json.loads(theorem.OUT_JSON.read_text(encoding="utf-8"))
    assert frozen == theorem.hard._jsonable(report)
    assert theorem.OUT_MD.read_text(encoding="utf-8") == theorem.render_markdown(report)
    core = dict(report)
    integrity = core.pop("integrity")
    assert hashlib.sha256(theorem.hard.canonical_json_bytes(core)).hexdigest() == EXPECTED_CORE
    assert integrity["core_sha256"] == EXPECTED_CORE
    assert integrity["ordered_21_row_digest_sha256"] == EXPECTED_ORDERED_ROWS


def test_exact_21_row_inventory_values_and_homogeneity(report: dict) -> None:
    rows = report["certified_rows"]
    assert len(rows) == 21
    assert {row["direction_id"] for row in rows} == set(EXPECTED_VALUES)
    for row in rows:
        assert row["exact_target_jet_from_homogeneity"]["value"] == EXPECTED_VALUES[row["direction_id"]]
        assert row["Hessian"]["dimension"] == 486
        assert row["Hessian"]["symmetric_entrywise_over_Q"] is True
        assert row["Hessian"]["canonical_sparse_rational_sha256"]
        assert row["exact_target_jet_from_homogeneity"][
            "Hq_equals_degree_minus_1_times_gradient_exactly"
        ] is True
        assert row["exact_target_jet_from_homogeneity"][
            "q_dot_gradient_equals_degree_times_value_exactly"
        ] is True


def test_exact_source_reconstructions_and_arithmetic_contract(report: dict) -> None:
    arithmetic = report["arithmetic_contract"]
    assert arithmetic["floating_point_used_to_construct_or_accept_Hessians"] is False
    assert arithmetic["finite_difference_autodiff_or_rational_recognition_used"] is False
    assert report["family_certificates"]["H_self_quartics"][
        "I1_plus_I54_reconstructs_HdagH_squared_Hessian_entrywise_over_Q"
    ] is True
    assert report["family_certificates"]["H_self_quartics"]["target_HdotH_exactly_zero"] is True
    assert report["family_certificates"]["Phi_cubic"]["exact_signed_integer_two_form_basis"] is True
    assert report["family_certificates"]["Phi_self_quartics"]["all_int64_preflights_pass"] is True


def test_combined_31_of_37_scope_remains_fail_closed(report: dict) -> None:
    scope = report["scope_accounting"]
    claims = report["claims"]
    assert scope["hard_theorem_rows"] == 10
    assert scope["rows_certified_here"] == 21
    assert scope["combined_exact_source_rows"] == 31
    assert scope["remaining_row_count"] == 6
    assert tuple(scope["remaining_rows"]) == theorem.OPEN_ROWS
    assert claims["exact_source_algebra_Hessians_for_all_37_active_rows"] is False
    assert claims["exact_full_witness_aggregate_stationarity"] is False
    assert claims["exact_full_witness_symmetry_kernel"] is False
    assert claims["exact_full_witness_rank_448_and_PSD"] is False
    assert claims["full_486_field_global_equality_orbit_classified"] is False
    assert claims["physical_SM_G3_closed"] is False
    assert claims["physical_SM_G4_closed"] is False
    assert claims["physical_SM_G5_closed"] is False


def test_adversarial_hessian_entry_mutation_changes_digest() -> None:
    target = theorem.foundation.integer_target_vector()
    rows, _certificate = theorem.exact_phi_self_rows(target)
    original = rows["O48_B04_Phi_self_quartics"]
    mutated = original.numerator.copy()
    index = tuple(np.argwhere(mutated != 0)[0])
    mutated[index] += 1
    adversarial = theorem.hard.RationalHessian.normalized(mutated, original.denominator)
    assert adversarial.sha256() != original.sha256()


def test_adversarial_missing_H_channel_breaks_reconstruction() -> None:
    target = theorem.foundation.integer_target_vector()
    rows, certificate = theorem.exact_h_self_rows(target)
    channel_1 = rows["O36_B01_H_self_quartics"].fraction_entries()
    channel_54 = rows["O36_B02_H_self_quartics"].fraction_entries()
    assert channel_1 != channel_54
    assert certificate[
        "I1_plus_I54_reconstructs_HdagH_squared_Hessian_entrywise_over_Q"
    ] is True


def test_source_drift_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    drifted = dict(theorem.SOURCE_HASHES)
    name = next(iter(drifted))
    drifted[name] = "f" * 64
    monkeypatch.setattr(theorem, "SOURCE_HASHES", drifted)
    with pytest.raises(ArithmeticError, match="dependency drifted"):
        theorem.source_bindings()
