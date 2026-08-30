#!/usr/bin/env python3
"""Release and adversarial tests for the complete canonical V21 G1 proof."""
from __future__ import annotations

import json
from pathlib import Path
import shutil

import canonical_g1_complete_operator_ring_dim6_v21 as producer
import canonical_g1_g8_gauged_u1x_v21 as canonical


ROOT = Path(__file__).resolve().parent


def test_frozen_complete_G1_report_is_fresh_and_all_criteria_are_exact():
    report = producer.build_report()
    frozen = json.loads(producer.OUT_JSON.read_text(encoding="utf-8"))
    assert report == frozen
    assert producer.render_markdown(report) == producer.OUT_MD.read_text(
        encoding="utf-8"
    )
    assert report["qualified_gate_id"] == canonical.G1_ID
    assert report["closure_complete"] is True
    assert type(report["n_failed"]) is int and report["n_failed"] == 0
    assert report["failures"] == []
    assert all(
        row["passed"] is True for row in report["acceptance_evidence"].values()
    )
    proof = report["proof_summary"]
    assert proof["neutral_field_content_sectors"] == 168
    assert proof["complex_invariant_directions"] == 891
    assert proof["degree_five_directions"] == 119
    assert proof["degree_six_directions"] == 721
    assert proof["v3_SARAH_runtime_attestation_valid"] is True


def test_trusted_verifier_closes_canonical_G1_with_G2_now_downstream_closed():
    state = canonical.validate_gate_artifact(canonical.GATES[0], ROOT)
    assert state["valid"] is True, state["errors"]
    assert state["closed"] is True
    assert state["trusted_verifier_result"][
        "all_acceptance_criteria_verified"
    ] is True
    report = canonical.build_report(ROOT)
    assert report["closure_counts"] == {"closed": 3, "open": 5}
    assert all(row["closed"] is True for row in report["gates"][:3])
    assert all(row["closed"] is False for row in report["gates"][3:])
    assert report["overall_state"] == "BLOCKED"
    assert report["classification"]["whole_model_validated"] is False


def _copy_verification_root(destination: Path) -> None:
    artifact = json.loads(producer.OUT_JSON.read_text(encoding="utf-8"))
    paths = {row["path"] for row in artifact["source_manifest"]}
    paths.update(
        {
            canonical.GATES[0]["required_artifact"],
            canonical.GATES[0]["trusted_verifier"]["path"],
        }
    )
    for relative in sorted(paths):
        source = ROOT / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def test_channel_report_mutation_is_rejected_by_the_frozen_verifier(tmp_path):
    _copy_verification_root(tmp_path)
    path = tmp_path / "CANONICAL_G1_SUSYNO_CHANNEL_BASIS_V21.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["rows"][0]["constructive_channel_count"] += 1
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    state = canonical.validate_gate_artifact(canonical.GATES[0], tmp_path)
    assert state["valid"] is False
    assert state["closed"] is False
    assert "trusted_verifier_result_not_exact" in state["errors"]


def test_scope_does_not_claim_derivative_gauge_or_fermion_EFT_operators():
    report = json.loads(producer.OUT_JSON.read_text(encoding="utf-8"))
    scope = report["proof_summary"]["scope"]
    assert scope.startswith("derivative-free scalar polynomial potential ring")
    criterion = report["acceptance_evidence"]["A1"]["criterion"]
    assert "derivative-free" in criterion
    assert "scalar polynomial potential operators" in criterion
    assert "fermion" not in criterion.lower()
    assert "gauge-field" not in criterion.lower()
