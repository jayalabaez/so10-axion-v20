from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "susy_v66_multipath_g1_frontier_master_audit.py"
SPEC = importlib.util.spec_from_file_location("v66_master", SCRIPT)
assert SPEC and SPEC.loader
v66 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v66)


def built() -> dict:
    report = v66.build_report()
    v66.validate(report)
    return report


def routes(report: dict) -> dict[str, dict]:
    return {row["route_id"]: row for row in report["route_matrix"]}


def test_metadata_core_and_exact_inputs() -> None:
    report = built()
    assert (report["version"], report["date"], report["schema"]) == (
        "V66", "2026-08-30", "susy_v66_multipath_g1_frontier_master_audit/v1"
    )
    assert report["core_sha256"] == v66.canonical_sha(report)
    assert report["input_core_hashes"] == v66.EXPECTED_CORES


def test_only_b65_is_superseded_and_a60_c_are_preserved() -> None:
    report = built()
    rs = routes(report)
    assert list(rs) == ["A60", "B66", "C"]
    assert rs["B66"]["supersedes_V65_route_id"] == "B65"
    assert report["lineage"]["supersession_scope"] == "B65 to B66 only"
    assert report["lineage"]["superseded_route"]["historical_artifact_modified"] is False
    assert rs["A60"]["bound_core_sha256"] == v66.EXPECTED_CORES["A60"]
    assert rs["C"]["bound_core_sha256"] == v66.EXPECTED_CORES["C"]
    assert v66.object_sha(v66.strip_carry(rs["A60"])) == v66.V65_ROW_SHA["A60"]
    assert v66.object_sha(v66.strip_carry(rs["C"])) == v66.V65_ROW_SHA["C"]


def test_v65_retraction_current_rejection_and_v64_no_wz() -> None:
    report = built()
    b = routes(report)["B66"]
    assert b["V65_artifact_integrity"] == "PRESERVED"
    assert b["V65_action_upgrade"] == "RETRACTED"
    assert b["current_action_status"] == "REJECTED"
    assert b["V64_null_mode_core"] == v66.V64_NULL_CORE
    assert b["V64_null_mode_stands"] is True
    assert b["WZ_term"] == "NONE_FORCED"


def test_full_pre_v66_suite_is_208_not_199() -> None:
    scope = built()["regression_scope_correction"]
    assert scope["pre_V66_file_count"] == 16
    assert scope["pre_V66_test_count"] == 208
    assert scope["incorrect_prior_narrow_count"] == 199
    assert sum(row["test_functions"] for row in scope["files"]) == 208
    assert all("v66" not in row["path"] for row in scope["files"])


def test_gm_formula_and_overlap_suppression() -> None:
    gm = routes(built())["B66"]["gm_overlap"]
    norm = gm["v64_null_mode_normalization"]
    assert gm["general_supergravity_mass"] == (
        "mu_Q = [m_3/2 Z_Q - Fbar^I partial_bar_I Z_Q]/sqrt(Y_Q Y_Qbar)"
    )
    assert gm["nonzero_mass_constructed_in_bound_action"] is False
    assert norm["effective_bilinear"] == "Z_eff = c_K/(1+alpha^2)"
    assert norm["portal_amplitude_overlap"] == "1/sqrt(1+alpha^2)"
    assert norm["portal_rate_suppression"] == "1/(1+alpha^2)"


def test_beta_order_one_loop_formulas_and_low_ms_result() -> None:
    b = routes(built())["B66"]
    group, one = b["beta_and_two_loop_matrices"], b["one_loop_crossing"]
    assert group["convention"] == "rows and columns are ordered (U1_GUT, SU2_L, SU3_c)"
    assert group["orphan_Q_pair"]["Delta_b"] == ["1/5", "3", "2"]
    assert group["complete_10_plus_10bar"]["Delta_b"] == ["3", "3", "3"]
    assert one["analytic_c_family"]["derived_exact_powers"] == {
        "MG": "3/64", "MQ": "11/32", "MS": "-21/32",
        "alphaU_inverse_ln_c": "-121/(128*pi)",
    }
    assert v66.one_loop_residual(one, one["c_equals_1"]) < 1e-10
    assert v66.one_loop_residual(one, one["fixed_MS_1_TeV"]) < 1e-10
    assert one["c_equals_1"]["MS_GeV"] == pytest.approx(2.250826151424409e11)
    assert one["c_equals_1"]["MG_GeV"] == pytest.approx(4.549789822040069e15)
    assert one["fixed_MS_1_TeV"]["MS_GeV"] == 1000.0
    assert one["fixed_MS_1_TeV"]["MQ_GeV"] == pytest.approx(5.337995621018032e15)
    assert one["fixed_MS_1_TeV"]["MG_GeV"] == pytest.approx(1.797161840637619e16)


def test_two_loop_diagnostics_are_not_precision_claims() -> None:
    two = routes(built())["B66"]["two_loop_diagnostics"]
    assert two["claim_boundary"] == (
        "these are gauge-only diagnostics, not precision unification fits"
    )
    assert two["orphan_only_raw_no_matching"]["computed"]["MS"] == pytest.approx(
        4.7603782293529834e11
    )
    assert two["orphan_only_universal_MSbar_to_DRbar"]["computed"]["MS"] == pytest.approx(
        4.991969752897142e11
    )
    assert two["full_ten_raw_no_matching"]["computed"]["MS"] == pytest.approx(
        13839.052519326706
    )
    assert len(two["not_included"]) == 4


def test_h66_t66_are_candidates_only_and_t66_dangers_are_explicit() -> None:
    b = routes(built())["B66"]
    candidates = {row["id"]: row for row in b["candidate_extensions"]}
    assert set(candidates) == {"H66", "T66"}
    assert b["accepted_extension_count"] == 0
    assert b["same_action_microscopic_completion"] is False
    assert all(row["not_complete"] for row in candidates.values())
    assert all(
        row["status"] == "CANDIDATE_CONDITIONAL_EXTENSION"
        for row in candidates.values()
    )
    t = candidates["T66"]
    assert t["total_Delta_b"] == ["3", "3", "3"]
    assert t["baryon_safety"]["inherits_V65_claim"] is False
    assert "Uc_X dc dc" in t["baryon_safety"]["reason"]
    assert "Ec_X L L" in t["baryon_safety"]["reason"]
    assert any("embedding" in item for item in t["missing"])
    assert any("anomaly" in item for item in t["missing"])


def test_complete_card_a1_a8_and_established_gates_are_open() -> None:
    report = built()
    card = report["consolidated_theory_card"]
    assert card["current_bound_action_status"] == "REJECTED"
    assert all(not row["accepted"] for row in card["candidate_extensions"])
    assert [row["id"] for row in report["acceptance_criteria"]] == [
        f"A{i}" for i in range(1, 9)
    ]
    assert all(row["status"] == "OPEN" for row in report["acceptance_criteria"])
    assert [row["gate"] for row in report["gate_ledger"]] == [
        f"G{i}" for i in range(1, 9)
    ]
    assert all(row["status"] == "OPEN" for row in report["gate_ledger"])
    assert "post-rank" in report["gate_ledger"][3]["decision"]
    assert "inflation" in report["gate_ledger"][5]["decision"]
    assert "proton lifetime" in report["gate_ledger"][6]["decision"]
    strict = report["strict_master_decision"]
    assert strict["accepted_extension_count"] == 0
    assert strict["same_action_microscopic_completion_found"] is False
    assert strict["V66_G1_closed"] is False
    assert strict["closed_gates"] == []
    assert strict["complete_theory"] is False


def mutate_status(report: dict) -> None:
    routes(report)["B66"]["current_action_status"] = "ACCEPTED"


def mutate_gate(report: dict) -> None:
    report["gate_ledger"][0]["status"] = "CLOSED"


def mutate_gm(report: dict) -> None:
    routes(report)["B66"]["gm_overlap"]["v64_null_mode_normalization"][
        "effective_bilinear"
    ] = "Z_eff=c_K"


def mutate_beta(report: dict) -> None:
    routes(report)["B66"]["beta_and_two_loop_matrices"]["orphan_Q_pair"][
        "Delta_b"
    ] = ["2", "3", "1/5"]


def mutate_candidate(report: dict) -> None:
    routes(report)["B66"]["candidate_extensions"][1]["not_complete"] = False
    routes(report)["B66"]["accepted_extension_count"] = 1


def mutate_scope(report: dict) -> None:
    report["regression_scope_correction"]["pre_V66_test_count"] = 199


def mutate_claim(report: dict) -> None:
    routes(report)["B66"]["two_loop_diagnostics"][
        "claim_boundary"
    ] = "precision unification established"


def mutate_splice(report: dict) -> None:
    report["cross_route_composition_rule"]["cross_route_splicing_allowed"] = True


@pytest.mark.parametrize(
    "mutation",
    [
        mutate_status, mutate_gate, mutate_gm, mutate_beta,
        mutate_candidate, mutate_scope, mutate_claim, mutate_splice,
    ],
)
def test_validator_recomputes_and_rejects_recanonicalized_mutations(mutation) -> None:
    report = built()
    mutation(report)
    report["core_sha256"] = v66.canonical_sha(report)
    with pytest.raises(AssertionError, match="V66 master recomputation mismatch"):
        v66.validate(report)


def test_generated_artifacts_and_check_mode_are_current() -> None:
    report = built()
    assert json.loads(v66.JSON_PATH.read_text(encoding="utf-8")) == report
    assert v66.MD_PATH.read_text(encoding="utf-8") == v66.render_markdown(report)
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert report["core_sha256"] in proc.stdout

