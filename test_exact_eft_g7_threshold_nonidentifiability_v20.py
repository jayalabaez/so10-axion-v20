from __future__ import annotations

from fractions import Fraction
import hashlib
import json

import pytest

import exact_eft_g7_threshold_nonidentifiability_v20 as theorem


def test_frozen_report_matches_live_builder() -> None:
    live = theorem.build_report()
    frozen = json.loads(theorem.OUT_JSON.read_text())
    assert live == frozen
    assert live["n_failed"] == 0
    if theorem.EXPECTED_CORE_SHA256 != "TO_BE_FROZEN":
        assert live["core_sha256"] == theorem.EXPECTED_CORE_SHA256


def test_exact_electroweak_restriction_collision() -> None:
    report = theorem.build_report()
    c = report["threshold_restriction_counterexample"]
    assert c["same_SU3C_x_U1em_restriction"] is True
    assert c["same_frozen_G6_masses"] is True
    assert c["restriction_map_noninjective"] is True
    assert c["completion_A"]["complex_scalar_one_loop_delta_b2"] == "0"
    assert c["completion_A"]["complex_scalar_one_loop_delta_bY"] == "1/3"
    assert c["completion_B"]["complex_scalar_one_loop_delta_b2"] == "1/6"
    assert c["completion_B"]["complex_scalar_one_loop_delta_bY"] == "1/6"
    assert Fraction(1, 3) != Fraction(1, 6)


def test_exact_G6_modes_and_scale_collision_are_bound() -> None:
    report = theorem.build_report()
    checks = report["checks"]
    assert checks["neutral_collision_mode_exact"]
    assert checks["charged_collision_mode_exact"]
    scale = report["absolute_scale_counterexample"]
    assert scale == {
        "completion_A_mass_unit": "M0",
        "completion_B_mass_unit": "2*M0",
        "same_normalized_G6_spectrum": True,
        "threshold_log_shift": "ln(2)",
        "absolute_scale_unidentified": True,
    }


def test_reduced_executable_is_not_the_authoritative_contract() -> None:
    report = theorem.build_report()
    scope = report["reduced_RGE_model_scope"]
    assert "gauged U(1)_X" in scope["authoritative_contract"]
    assert "SO(10) only" in scope["available_executable_contract"]
    assert not scope["full_210_quartic_basis_present"]
    assert not scope["lambda4_CGC_present"]
    assert not scope["dimension6_O6_lock_present"]
    assert not scope["two_loop_SO10_complete"]


def test_classification_is_fail_closed() -> None:
    report = theorem.build_report()
    classification = report["classification"]
    assert classification["exact_EFT_G7_input_nonidentifiability_proved"]
    assert classification["mathematical_EFT_G7_closed"] is False
    assert classification["EFT_release_G7_verified"] is False
    assert classification["authoritative_renormalizable_G7_closed"] is False
    assert all(value is True for value in report["integration"].values())
    assert "G7_NONIDENTIFIABILITY_DOWNSTREAM_INTEGRATION_REQUIRED" not in report["release_blockers"]


def test_dependency_drift_fails_closed(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{}\n")
    original = theorem.DEPENDENCIES["G6_spectrum_JSON"]
    monkeypatch.setitem(
        theorem.DEPENDENCIES,
        "G6_spectrum_JSON",
        (bad, original[1], original[2]),
    )
    with pytest.raises(ArithmeticError, match="dependency drifted"):
        theorem.build_report()


def test_report_files_have_frozen_raw_hashes() -> None:
    # Populated by the terminal refreeze; this guards accidental report drift
    # without making the theorem depend on its own source bytes.
    expected = {
        theorem.OUT_JSON: theorem.EXPECTED_REPORT_RAW_SHA256["json"],
        theorem.OUT_MD: theorem.EXPECTED_REPORT_RAW_SHA256["md"],
    }
    for path, digest in expected.items():
        if digest == "TO_BE_FROZEN":
            pytest.skip("terminal report pins await integration refreeze")
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
