from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

import final_g4_eft_mathematical_gate_v20 as gate


def test_parallel_eft_g4_mathematical_classification_is_exact_and_scoped() -> None:
    report = gate.build_report()
    classification = report["classification"]

    assert report["status"] == gate.STATUS
    assert classification["mathematical_G4_closed_for_EFT_model"] is True
    assert (
        classification["mathematical_G4_closed_for_original_renormalizable_model"]
        is False
    )
    assert classification["release_G4_verified_for_EFT_model"] is False
    assert classification["authoritative_renormalizable_G4_gate_mutated"] is False
    assert classification["whole_model_validated"] is False
    assert report["release_criteria"][
        "parallel_EFT_G4_integrated_into_release_orchestrators"
    ] is True
    assert report["production_mapping"]["release_integration_completed"] is True
    assert "release_integration_required" not in report["production_mapping"]
    assert set(report["release_blockers"]) == {
        "Lambda_EFT_and_positive_Wilson_matching_approved",
        "radiative_stability_completed",
        "external_extended_model_contract_executed",
        "G1_promoted_closed",
        "G2_promoted_closed",
        "release_G3_verified_for_EFT_model",
    }


def test_same_witness_exact_quotient_and_hessian_close_mathematical_g4() -> None:
    report = gate.build_report()
    geometry = report["exact_EFT_witness_quotient_geometry"]
    hessian = report["exact_Hessian_classification"]

    assert geometry["exact_tangent_ranks"] == {
        "SO10": 36,
        "SO10_plus_U1X": 37,
        "SO10_plus_U1X_plus_PQ": 38,
    }
    assert geometry["gauge_quotient_dimension_including_axion"] == 449
    assert geometry["independent_PQ_axion_dimension"] == 1
    assert geometry["massive_transverse_quotient_dimension"] == 448
    assert geometry["source_binding_exact"] is True

    assert hessian["negative_modes"] == 0
    assert hessian["unexplained_zero_modes"] == 0
    assert hessian["massless_physical_axion_modes"] == 1
    assert hessian["strictly_positive_massive_transverse_modes"] == 448
    assert hessian["Hessian_rank"] == 448
    assert hessian["Hessian_nullity"] == 38
    assert hessian["positive_kappa_family"][
        "rank448_nullity38_for_every_positive_kappa"
    ] is True
    assert (
        hessian["positive_kappa_family"]["kernel_identity"]
        == "ker H(kappa)=ker H0 intersect ker J for every kappa>0"
    )
    assert hessian["stabilized_payload_sha256"] == (
        gate.EXPECTED_STABILIZED_HESSIAN_PAYLOAD_SHA256
    )
    assert all(report["mathematical_checks"].values())


def test_semantic_mutations_fail_the_mathematical_mapping() -> None:
    theorem_report = json.loads(gate.THEOREM_JSON.read_text(encoding="utf-8"))
    g3_report = gate.g3_gate.build_report()
    quotient = json.loads(gate.QUOTIENT_JSON.read_text(encoding="utf-8"))
    geometry = gate.exact_eft_witness_quotient_geometry()

    mutated = copy.deepcopy(theorem_report)
    mutated["exact_stabilized_Hessian"]["stabilized"]["exact_rank"] = 447
    checks = gate._mathematical_checks(mutated, g3_report, quotient, geometry)
    assert checks["stabilized_Hessian_rank448_nullity38_exact"] is False

    mutated_geometry = copy.deepcopy(geometry)
    mutated_geometry["exact_tangent_ranks"]["SO10_plus_U1X"] = 36
    checks = gate._mathematical_checks(
        theorem_report, g3_report, quotient, mutated_geometry
    )
    assert checks["gauged_orbit_rank_37_exact"] is False


def test_raw_dependency_drift_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    drifted = tmp_path / "theorem.json"
    drifted.write_bytes(gate.THEOREM_JSON.read_bytes() + b"\n")
    pins = dict(gate.EXPECTED_ARTIFACT_SHA256)
    pins["EFT_G3_theorem_JSON"] = (
        drifted,
        pins["EFT_G3_theorem_JSON"][1],
    )
    monkeypatch.setattr(gate, "EXPECTED_ARTIFACT_SHA256", pins)
    with pytest.raises(ArithmeticError, match="dependency drifted"):
        gate.build_report()


def test_report_artifacts_are_deterministic(tmp_path: Path) -> None:
    report = gate.build_report()
    out_json = tmp_path / "gate.json"
    out_md = tmp_path / "gate.md"
    gate.write_report(report, out_json=out_json, out_md=out_md)
    first_json = out_json.read_bytes()
    first_md = out_md.read_bytes()
    gate.write_report(report, out_json=out_json, out_md=out_md)
    assert out_json.read_bytes() == first_json
    assert out_md.read_bytes() == first_md
    assert json.loads(first_json)["core_sha256"] == report["core_sha256"]
    assert "mathematical EFT G4: `true`" in first_md.decode("utf-8")
