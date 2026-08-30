from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "susy_v67_multipath_g1_frontier_master_audit.py"
SPEC = importlib.util.spec_from_file_location("v67_master", SCRIPT)
assert SPEC and SPEC.loader
v67 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v67)


def built() -> dict:
    report = v67.build_report()
    v67.validate(report)
    return report


def routes(report: dict) -> dict[str, dict]:
    return {row["route_id"]: row for row in report["route_matrix"]}


def b67(report: dict) -> dict:
    return routes(report)["B67"]


def test_metadata_core_and_three_exact_inputs() -> None:
    report = built()
    assert (report["version"], report["date"], report["schema"]) == (
        "V67",
        "2026-08-30",
        "susy_v67_multipath_g1_frontier_master_audit/v1",
    )
    assert report["core_sha256"] == v67.canonical_sha(report)
    assert report["input_core_hashes"] == v67.EXPECTED_CORES


def test_only_b66_is_superseded_and_a60_c_are_exactly_preserved() -> None:
    report = built()
    rs = routes(report)
    assert list(rs) == ["A60", "B67", "C"]
    assert b67(report)["supersedes_V66_route_id"] == "B66"
    assert report["lineage"]["supersession_scope"] == "B66 to B67 only"
    assert report["lineage"]["superseded_route"]["historical_artifact_modified"] is False
    assert v67.object_sha(rs["A60"]) == v67.V66_ROW_SHA["A60"]
    assert v67.object_sha(rs["C"]) == v67.V66_ROW_SHA["C"]
    assert b67(report)["inherited_B66_row_sha256"] == v67.V66_ROW_SHA["B66"]


def test_current_action_rejected_v64_null_and_no_wz_stand() -> None:
    b = b67(built())
    assert b["current_bound_action_status"] == "REJECTED"
    assert b["V64_null_mode_stands_for_current_action"] is True
    assert b["WZ_term"] == "NONE_FORCED"
    assert b["accepted_extension_count"] == 0
    assert b["same_action_microscopic_completion"] is False


def test_d67_candidate_operator_removes_zero_but_mass_is_open() -> None:
    d = b67(built())["D67_candidate_new_action"]
    repair = d["spectral_index_repair"]
    minimum = repair["minimal_index_change"]
    assert minimum["new_operator"] == (
        "A'_N=[[diag(k_n),mu 1_N],[0...0,M]], shape (N+1) x (N+1)"
    )
    assert minimum["finite_determinant"] == "det A'_N = M product_n k_n"
    assert minimum["all_finite_checks_pass"] is True
    assert len(minimum["finite_exact_checks"]) == 8
    tower = repair["inherited_5D_infinite_tower"]
    assert tower["exact_zero_removed"] is True
    assert tower["scope"] == (
        "exact only for the inherited one-dimensional V64 half-integer tower and its wall mixing"
    )
    light = repair["light_singular_value"]
    assert light["exact_equation_for_inherited_5D_operator_below_first_KK_pole"] == (
        "M^2=m^2[1+alpha^2 tan(mL)/(mL)], 0<mL<pi/2"
    )
    assert light["no_parametrically_light_mode_proved_without_parameters"] is False
    assert d["terminal_decision"]["physical_colored_mass_certified"] is False


def test_qr2_preserves_selector_and_exact_global_anomaly_cancellation() -> None:
    charge = b67(built())["D67_candidate_new_action"][
        "charge_anomaly_and_proton_audit"
    ]
    assert charge["mass_terms_preserve_Z4R_without_q2_VEV"] is True
    assert charge["tree_level_Schur_theorem"]["induced_four_matter_superpotential"] == "0"
    assert charge["global_mixed_R_anomaly"]["sum"] == {
        "Delta_A2": 0,
        "Delta_A3": 0,
    }
    gs = charge["formal_V62_5D_integrated_GS_diagnostic"]
    assert gs[
        "formal_delta_c_diagnostic_mod4"
    ] == {"SU2": 2, "SU3": 0}
    assert gs["status"] == "FORMAL_5D_BOOKKEEPING_NOT_A_DERIVED_6D_LOCAL_COUPLING"
    assert "not computed" in gs["not_a_6D_local_completion"]


def test_d67_is_new_6d_action_candidate_not_a_5d_patch() -> None:
    d = b67(built())["D67_candidate_new_action"]
    geometry = d["geometry_and_6D_escape"]
    current = geometry["current_5D_action"]
    assert current["wall_local_Q_only_patch_exists"] is False
    assert current["split_bulk_5D_status"] == (
        "UNCLASSIFIED__NO_EXHAUSTIVE_SPIN11_PARITY_OR_REPRESENTATION_NO_GO"
    )
    escape = geometry["D67_6D_escape_candidate"]
    assert escape["status"] == "CANDIDATE_NEW_ACTION_NOT_CONSTRUCTED"
    assert escape["local_group"] == "SU3C x SU2L x U1Y x U1X"
    assert any("Spin(11)" in item for item in escape["not_imported_from_literature"])
    assert any("anomaly" in item for item in escape["not_imported_from_literature"])
    sixdim = d["spectral_index_repair"]["six_dimensional_nonimport"]
    assert sixdim["status"] == "OPEN_NOT_THE_INHERITED_5D_TAN_EQUATION"
    assert "logarithmically" in sixdim["point_local_double_KK_asymptotic"]
    assert d["terminal_decision"]["same_action_microscopic_completion_found"] is False


def test_t66_exact_baryon_lepton_operator_and_unified_selector_no_go() -> None:
    p = b67(built())["T66_B3_conditional_route_audit"]
    schur = p["t66_u_portal_schur_complement"]
    assert schur["exact_derivation_pass"] is True
    assert schur["effective_superpotential_i_less_than_j"] == (
        "W_eff=-(lambda_ij rho_kl/M10) epsilon^abc uc_k,a dc_i,b dc_j,c Nc_l"
    )
    assert schur["global_numbers"] == {
        "B_of_uc_dc_dc": "-1",
        "Delta_B": -1,
        "Delta_B_minus_L": 0,
        "Delta_L": -1,
        "L_of_Nc": "-1",
        "scope": "pre-Majorana matching: uc dc dc Nc",
    }
    post = schur["heavy_N_matching"]["post_Majorana_field_numbers"]
    assert post["operator"] == "uc dc dc L Hu"
    assert (post["Delta_B"], post["Delta_L"], post["Delta_B_minus_L"]) == (
        -1,
        1,
        -2,
    )
    no_go = p["unified_selector_one_sided_no_go"]
    assert no_go["result"] == (
        "NO_SCOPED_FAMILY_DEPENDENT_UNIFIED_ABELIAN_SELECTOR_CAN_FORBID_ALL_CONJUGATE_PORTALS"
    )
    assert no_go["family_dependent_scan"]["charge_assignment_count"] == 179998
    assert no_go["family_dependent_scan"]["counterexample_count"] == 0
    assert "does not assert" in no_go["determinant_permutation_theorem"]["conclusion"]


def test_b3_is_minimal_conditional_ir_escape_not_local_embedding() -> None:
    b3 = b67(built())["T66_B3_conditional_route_audit"][
        "conditional_b3_ir_escape"
    ]
    assert b3["classification"] == "CONDITIONAL_IR_ESCAPE_ONLY"
    assert b3["modulus"] == 3
    assert b3["minimality_scan"]["minimal_modulus_within_scan"] == 3
    standard = b3["standard_discrete_anomaly_checks"]
    assert standard["pass"] is True
    assert all(value == 0 for value in standard["linear_residues_mod3"].values())
    assert standard["integer_parent_cubic_AZZZ_residue_mod9"] == 0
    assert b3["symmetry_stack"]["B3_is_not_a_replacement_for_matter_parity"] is True
    compatibility = b3["current_action_compatibility"]
    assert compatibility["accepted"] is False
    assert compatibility["IR_anomaly_pass_is_not_a_5D_embedding"] is True


def test_h66_t66_proxies_and_dimension_five_boundary_are_exact() -> None:
    p = b67(built())["T66_B3_conditional_route_audit"]
    proxy = p["dimension_six_proton_proxy"]
    rows = {row["branch"]: row for row in proxy["rows"]}
    assert proxy["claim_boundary"] == "NO_LIFETIME_PREDICTION"
    assert rows["H66"]["central_proxy_passes"] is False
    assert rows["H66"]["lifetime_over_limit"] == pytest.approx(0.06498870601033924)
    assert rows["T66"]["central_proxy_passes"] is True
    assert rows["T66"]["lifetime_over_limit"] == pytest.approx(5.9870901669808845)
    assert all(row["branch_globally_decided"] is False for row in rows.values())
    dim5 = p["dimension_five_portal_stress"]
    assert dim5["O1_unprotected_portals_pass_comparison"] is False
    assert dim5["claim_boundary"] == "CONDITIONAL_FEASIBILITY_BOUND_NOT_A_LIFETIME"
    assert dim5["illustrative_common_T66_threshold"][
        "maximum_abs_lambda_rho_thetaN_D"
    ] == pytest.approx(2.521534213303378e-16)


def test_candidates_are_isolated_no_cross_route_splice() -> None:
    report = built()
    b = b67(report)
    candidates = {row["id"]: row for row in b["candidate_matrix"]}
    assert set(candidates) == {"D67", "H66", "T66", "B3_IR"}
    assert candidates["D67"]["kind"] == "CANDIDATE_NEW_ACTION"
    assert candidates["T66"]["kind"] == "CONDITIONAL_ROUTE_AUDIT"
    assert candidates["B3_IR"]["embedded_in_5D"] is False
    assert all(row["accepted"] is False for row in candidates.values())
    assert all(row["same_action_complete"] is False for row in candidates.values())
    assert b["cross_route_evidence_spliced"] is False
    assert report["cross_route_composition_rule"]["cross_route_splicing_allowed"] is False
    assert report["cross_route_composition_rule"]["aggregated_gate_closure"] is False


def test_regression_scope_a1_a8_and_g1_g8_remain_open() -> None:
    report = built()
    scope = report["regression_scope"]
    assert scope["file_count"] == 20
    assert scope["test_count"] == 262
    assert scope["count_unit"] == "top-level test functions before pytest parametrization"
    assert sum(row["test_functions"] for row in scope["files"]) == 262
    assert all("multipath_g1_frontier_master_audit.py" not in row["path"] or "v67" not in row["path"] for row in scope["files"])
    assert [row["id"] for row in report["acceptance_criteria"]] == [
        f"A{i}" for i in range(1, 9)
    ]
    assert all(row["status"] == "OPEN" for row in report["acceptance_criteria"])
    assert [row["gate"] for row in report["gate_ledger"]] == [
        f"G{i}" for i in range(1, 9)
    ]
    assert all(row["status"] == "OPEN" for row in report["gate_ledger"])
    strict = report["strict_master_decision"]
    assert strict["current_Spin11_action_status"] == "REJECTED"
    assert strict["accepted_extension_count"] == 0
    assert strict["V67_G1_closed"] is False
    assert strict["V67_G7_closed"] is False
    assert strict["closed_gates"] == []
    assert strict["complete_theory"] is False


def mutate_action(report: dict) -> None:
    b67(report)["current_bound_action_status"] = "ACCEPTED"


def mutate_a60(report: dict) -> None:
    routes(report)["A60"]["classification"] = "MUTATED"


def mutate_index(report: dict) -> None:
    b67(report)["D67_candidate_new_action"]["spectral_index_repair"][
        "inherited_5D_infinite_tower"
    ]["exact_zero_removed"] = False


def mutate_physical_mass(report: dict) -> None:
    b67(report)["D67_candidate_new_action"]["terminal_decision"][
        "physical_colored_mass_certified"
    ] = True


def mutate_6d(report: dict) -> None:
    b67(report)["D67_candidate_new_action"]["geometry_and_6D_escape"][
        "D67_6D_escape_candidate"
    ]["status"] = "ACCEPTED"


def mutate_operator(report: dict) -> None:
    b67(report)["T66_B3_conditional_route_audit"][
        "t66_u_portal_schur_complement"
    ]["global_numbers"]["Delta_B"] = 0


def mutate_selector(report: dict) -> None:
    b67(report)["T66_B3_conditional_route_audit"][
        "unified_selector_one_sided_no_go"
    ]["family_dependent_scan"]["counterexample_count"] = 1


def mutate_b3(report: dict) -> None:
    b67(report)["T66_B3_conditional_route_audit"]["conditional_b3_ir_escape"][
        "current_action_compatibility"
    ]["accepted"] = True


def mutate_proxy(report: dict) -> None:
    b67(report)["T66_B3_conditional_route_audit"]["dimension_six_proton_proxy"][
        "rows"
    ][0]["central_proxy_passes"] = True


def mutate_gate(report: dict) -> None:
    report["gate_ledger"][0]["status"] = "CLOSED"


def mutate_splice(report: dict) -> None:
    report["cross_route_composition_rule"]["cross_route_splicing_allowed"] = True


def mutate_acceptance(report: dict) -> None:
    b67(report)["accepted_extension_count"] = 1
    report["strict_master_decision"]["accepted_extension_count"] = 1


def mutate_scope(report: dict) -> None:
    report["regression_scope"]["test_count"] = 261


@pytest.mark.parametrize(
    "mutation",
    [
        mutate_action,
        mutate_a60,
        mutate_index,
        mutate_physical_mass,
        mutate_6d,
        mutate_operator,
        mutate_selector,
        mutate_b3,
        mutate_proxy,
        mutate_gate,
        mutate_splice,
        mutate_acceptance,
        mutate_scope,
    ],
)
def test_validator_recomputes_and_rejects_recanonicalized_mutations(mutation) -> None:
    report = built()
    mutation(report)
    report["core_sha256"] = v67.canonical_sha(report)
    with pytest.raises(AssertionError, match="V67 master recomputation mismatch"):
        v67.validate(report)


def test_generated_artifacts_and_check_mode_are_current() -> None:
    report = built()
    assert json.loads(v67.JSON_PATH.read_text(encoding="utf-8")) == report
    assert v67.MD_PATH.read_text(encoding="utf-8") == v67.render_markdown(report)
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert report["core_sha256"] in proc.stdout
