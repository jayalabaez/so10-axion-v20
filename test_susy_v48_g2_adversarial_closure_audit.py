from __future__ import annotations

import json

import susy_v48_g2_adversarial_closure_audit as audit


def test_v47_does_not_pass_the_seven_clause_G2_gate() -> None:
    report = audit.build_report()
    assert report["decision"]["number_of_mandatory_criteria"] == 7
    assert report["decision"]["number_fully_passed_by_V47"] == 0
    assert not report["decision"]["G2_closed_from_V47"]
    assert report["decision"]["promotion_now"] == "REJECT"


def test_every_mandatory_clause_is_fail_closed() -> None:
    report = audit.build_report()
    rows = {row["id"]: row for row in report["closure_criteria"]}
    assert set(rows) == {f"C{i}" for i in range(1, 8)}
    assert all(not row["passes"] for row in rows.values())
    assert rows["C3"]["V47_state"] == "conditional"
    assert rows["C1"]["V47_state"] == "partial"


def test_all_order_no_go_has_explicit_neutral_dressing() -> None:
    report = audit.build_report()
    witness = report["all_order_no_go"]["explicit_witness"]
    assert witness["neutral_invariant"].startswith("Y=ThetaPlus^dagger")
    assert witness["primitive_U1F_charge"] == "-3+3=0"
    assert witness["R_charge"].startswith("0")
    assert "every n>=0" in witness["tower"]
    assert "Wilsonian" in report["all_order_no_go"]["consequence"]


def test_smallest_route_is_fixed_order_and_no_new_field() -> None:
    report = audit.build_report()
    route = report["smallest_legitimate_construction"]
    assert "no new propagating fields" in route["name"]
    assert route["accuracy_contract"]["recommended_order"].endswith("O(Lambda^-1)")
    assert "O(E^2/Lambda^2)" in route["accuracy_contract"]["remainder"]
    assert len(route["LO_source_superpotential"]) == 5
    basis = route["boundary_basis_through_dimension_five"]
    assert len(basis) == 7
    assert any("Fayet-Iliopoulos" in item for item in basis)
    assert any("Q_i^dagger HLF" in item for item in basis)


def test_positive_norm_self_adjointness_and_wilson_requirements_are_explicit() -> None:
    report = audit.build_report()
    route = report["smallest_legitimate_construction"]
    variational = route["variational_certificate"]
    wilson = route["Wilson_certificate"]
    assert "B_N=B_N^dagger" in variational["LO_Nambu_condition"]
    assert "Z_bulk>0" in variational["positive_norm"]
    assert "Gamma_HH(p)^(-1)" in wilson["exact_structure"]
    assert len(wilson["checks"]) == 4


def test_gate_scope_does_not_move_later_gate_obligations_into_G2() -> None:
    report = audit.build_report()
    excluded = report["gate_definition"]["excluded_and_owned_elsewhere"]
    assert set(excluded) == {"G3", "G6", "G7", "G8"}
    assert "global vacuum" in excluded["G3"]
    assert "numerical pole tower" in excluded["G6"]
    assert "baryon" in excluded["G7"]


def test_v47_positive_results_are_retained_without_promotion() -> None:
    report = audit.build_report()
    retained = report["V47_retained_positive_results"]
    assert retained["G1_closed"]
    assert retained["all_relevant_neutral_source_terms_included"]
    assert retained["conditional_Hermitian_extension_self_adjoint"]
    assert retained["constant_B_zero_mode_count"] == 0
    assert not report["decision"]["G2_closed_from_V47"]


def test_integrity_core_and_rendered_artifacts() -> None:
    report = audit.build_report()
    assert report["n_failed_integrity_checks"] == 0
    assert all(report["integrity_checks"].values())
    assert audit.canonical_sha(report) == report["core_sha256"]
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(report)


def test_combined_v48_only_closes_the_regulator_clause() -> None:
    report = audit.build_report()
    rows = {row["id"]: row for row in report["combined_V48_adversarial_review"]["criteria"]}
    assert report["combined_V48_adversarial_review"]["number_fully_passed"] == 1
    assert rows["C2"]["passes"]
    assert all(not rows[key]["passes"] for key in rows if key != "C2")
    assert not report["decision"]["G2_closed_after_combined_V48"]


def test_parity_census_records_ps_mu_derivatives_and_four_source_Hc_mirrors() -> None:
    census = audit.build_report()["parity_resolved_operator_census"]
    assert len(census["PS_even_direct_traces"]["H"]) == 4
    assert len(census["PS_even_direct_traces"]["Hc"]) == 4
    assert census["PS_zero_derivative_superpotential"]["correct_spinor_cubic_count"] == 19
    assert "mu_H" in census["PS_zero_derivative_superpotential"]["additional_allowed_relevant_operator"]
    assert census["PS_normal_derivatives"]["status_in_operator_artifact"] == "absent"
    assert len(census["source_collar_Hc_test"]["allowed_HcHc_portals"]) == 4


def test_operator_artifact_is_reviewed_as_representative_not_full_matching() -> None:
    report = audit.build_report()
    c7 = next(row for row in report["combined_V48_adversarial_review"]["criteria"] if row["id"] == "C7")
    assert c7["state"] == "partial"
    assert "representative matrices" in c7["reason"]
    assert "19 PS vertices" in c7["reason"]
