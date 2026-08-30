from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

import exact_physical_sm_hard_projector_hessians_v20 as theorem


ROOT = Path(__file__).resolve().parent
EXPECTED_CORE_SHA256 = "5c464a3e6725a8ba993d672667d16ea5fb6105b3f8015febcc90c7ea68640d59"
EXPECTED_ORDERED_ROW_DIGEST = "7f0297fdbb26fb4d9347de6df5500012ad20ca27c217d7dd39f2b1822dad7495"
EXPECTED_ROW_DIGESTS = {
    "O27_B01_126bar_self_projectors": "05bfdb2145e4b8e2b6c97acae8fecfe966b12c92dba3e3e560de522fb1e09167",
    "O27_B02_126bar_self_projectors": "6c576b4f65852c8127656f049d6573ebbae3b1316af65b4ebdff474b8044b308",
    "O27_B03_126bar_self_projectors": "20d2c0d437f981cb9cbef785be9d6978242e44d5b9015746c8aea6ab0eb0e9c2",
    "O27_B04_126bar_self_projectors": "8a55688b634668f4f1d98156af49ec175383e800d0258a7d6853a4f7743c992e",
    "O44_B01_Phi2_Sigma_projectors": "b163bfc1f2da40f674f6dbfcf4010601c89a6c011768c02c3434bd285fa7c0e8",
    "O44_B02_Phi2_Sigma_projectors": "978c1c92708f103fe1db1c49bb58f23054e33d7c48257d78309622565c6cbb20",
    "O44_B03_Phi2_Sigma_projectors": "10e19c3e53f44cc431083e47a881219b8e0f56264f5ab89e1d48939e2c06e990",
    "O44_B04_Phi2_Sigma_projectors": "9b1cae09643e736b13f1eedfa071cf0a07b9f45e53009f9a744283fdbe9a4c16",
    "O44_B05_Phi2_Sigma_projectors": "bfc5675403a5d183c52f1f321165741bbacf20fb0eeb394a9216ff0689ee15ae",
    "O44_B06_Phi2_Sigma_projectors": "6023d5fb2fd3f84031a7208e83cc13e8f2a14d03d57e906487f73e1ab2001920",
}


@pytest.fixture(scope="module")
def report() -> dict:
    return theorem.build_report()


def test_frozen_report_reproduces_exactly(report: dict) -> None:
    frozen = json.loads(theorem.OUT_JSON.read_text(encoding="utf-8"))
    assert frozen == theorem._jsonable(report)
    assert theorem.OUT_MD.read_text(encoding="utf-8") == theorem.render_markdown(report)
    core = dict(report)
    integrity = core.pop("integrity")
    assert hashlib.sha256(theorem.canonical_json_bytes(core)).hexdigest() == EXPECTED_CORE_SHA256
    assert integrity["core_sha256"] == EXPECTED_CORE_SHA256
    assert integrity["ordered_ten_row_digest_sha256"] == EXPECTED_ORDERED_ROW_DIGEST


def test_exact_row_inventory_digests_and_euler_identities(report: dict) -> None:
    rows = report["certified_rows"]
    assert len(rows) == 10
    assert {row["direction_id"] for row in rows} == set(EXPECTED_ROW_DIGESTS)
    for row in rows:
        assert (
            row["Hessian"]["canonical_sparse_rational_sha256"]
            == EXPECTED_ROW_DIGESTS[row["direction_id"]]
        )
        assert row["Hessian"]["dimension"] == 486
        assert row["Hessian"]["denominator"] > 0
        assert row["Hessian"]["nonzero_entries_full_matrix"] > 0
        assert row["Hessian"]["symmetric_entrywise_over_Q"] is True
        assert row["exact_target_jet_from_homogeneity"]["Hq_equals_3_gradient_exactly"] is True
        assert row["exact_target_jet_from_homogeneity"]["q_dot_gradient_equals_4V_exactly"] is True


def test_projector_reconstructions_are_exact_not_tolerance_checks(report: dict) -> None:
    arithmetic = report["arithmetic_contract"]
    assert arithmetic["floating_point_used_to_construct_or_accept_Hessians"] is False
    assert arithmetic["finite_difference_autodiff_or_rational_recognition_used"] is False
    assert arithmetic["canonical_digest_is_over_reduced_sparse_rational_entries"] is True
    families = report["family_certificates"]
    assert families["O27_126bar_self_projectors"][
        "four_projector_Hessians_reconstruct_unprojected_norm_quartic_entrywise_over_Q"
    ] is True
    assert families["O44_Phi2_Sigma_projectors"][
        "six_channel_Hessians_reconstruct_unprojected_contraction_entrywise_over_Q"
    ] is True
    assert families["O27_126bar_self_projectors"]["all_preflight_bounds_within_signed_int64"] is True
    assert families["O44_Phi2_Sigma_projectors"]["all_preflight_bounds_within_signed_int64"] is True


def test_scope_is_explicitly_fail_closed(report: dict) -> None:
    scope = report["scope_accounting"]
    claims = report["claims"]
    assert scope["active_witness_row_count"] == 37
    assert scope["exact_source_rows_certified_here"] == 10
    assert scope["remaining_active_row_count"] == 27
    assert len(scope["remaining_active_rows"]) == 27
    assert claims["exact_source_algebra_Hessians_for_all_10_O27_O44_rows"] is True
    assert claims["exact_source_algebra_Hessians_for_all_37_active_witness_rows"] is False
    assert claims["exact_full_witness_aggregate_stationarity"] is False
    assert claims["exact_full_witness_symmetry_kernel"] is False
    assert claims["exact_full_witness_rank_448_and_PSD"] is False
    assert claims["full_486_field_global_equality_orbit_classified"] is False
    assert claims["physical_SM_G3_closed"] is False
    assert claims["physical_SM_G4_closed"] is False
    assert claims["physical_SM_G5_closed"] is False


def test_adversarial_target_and_rational_digest_mutations_fail(report: dict) -> None:
    target = theorem.foundation.integer_target_vector().copy()
    target[0] += 1
    assert int(target @ target) != 1632

    rows, _certificate = theorem.exact_o27_hessians()
    original = rows["54"]
    mutated = original.numerator.copy()
    first = np.argwhere(mutated != 0)[0]
    mutated[tuple(first)] += 1
    adversarial = theorem.RationalHessian.normalized(mutated, original.denominator)
    assert adversarial.sha256() != original.sha256()


def test_adversarial_projector_omission_breaks_exact_reconstruction() -> None:
    rows, certificate = theorem.exact_o27_hessians()
    all_sum = theorem._rational_sum(rows.values())
    omitted_sum = theorem._rational_sum(
        row for channel, row in rows.items() if channel != "54"
    )
    assert all_sum != omitted_sum
    assert certificate[
        "four_projector_Hessians_reconstruct_unprojected_norm_quartic_entrywise_over_Q"
    ] is True


def test_source_hash_drift_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    drifted = dict(theorem.SOURCE_HASHES)
    name = next(iter(drifted))
    drifted[name] = "0" * 64
    monkeypatch.setattr(theorem, "SOURCE_HASHES", drifted)
    with pytest.raises(ArithmeticError, match="dependency drifted"):
        theorem.source_bindings()
