from __future__ import annotations

import json

import susy_v53_filter_selector_candidate_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def test_Z9_is_smallest_bounded_candidate() -> None:
    value = report()
    assert min(row["modulus"] for row in value["bounded_search"]["candidates"]) == 9
    assert value["verdict"]["candidate"] == "Z9 proton factor times exact Z2 matter parity"


def test_all_required_terms_allowed() -> None:
    assert all(report()["required_operator_checks"].values())


def test_complete_degree6_dressing_census_forbidden() -> None:
    census = report()["complete_F4_VEV_dressing_census_through_degree6"]
    assert census["row_count"] == 28
    assert census["all_forbidden"]
    assert all(row["forbidden"] for row in census["rows"])
    assert len(census["rows_sha256"]) == 64


def test_matter_parity_exact_and_odd_classes_forbidden() -> None:
    parity = report()["matter_parity"]
    assert parity["all_declared_VEVs_even"]
    assert parity["odd_matter_monomials_forbidden_all_orders"]
    assert parity["conservative_mod2_ledgers"]["odd_Weyl_components_mod2"] == 0


def test_anomalies_cancel_with_massive_spectators() -> None:
    repair = report()["discrete_anomaly_repair"]
    assert repair["base"] == {"Spin10_squared_Z9": 4, "gravity_squared_Z9": 3, "Z9_cubed": 3}
    assert all(value == 0 for value in repair["total_mod9"].values())
    assert repair["all_spectator_masses_generated_by_P"]
    assert repair["FF_spectator10_Yukawas_forbidden"]
    assert repair["spectator_singlet_linear_and_direct_seesaw_mixings_forbidden"]


def test_residual_and_first_exact_degree8_limit_exposed() -> None:
    value = report()
    assert value["residual_group"]["Z9_gcd_with_VEV_charges"] == 1
    assert value["residual_group"]["Z2_matter_parity_remnant"] == "exact"
    assert value["first_exposed_higher_degree_class"]["total_degree"] == 8
    assert value["first_exposed_higher_degree_class"]["Z9_charge"] == 0
    assert value["first_exposed_higher_degree_class"]["Spin10_singlet_multiplicity"] == 72


def test_beta_cost() -> None:
    running = report()["perturbativity"]
    assert (running["filter_source_T"], running["three_matter16_T"], running["two_vector10_spectator_pairs_T"]) == (36, 6, 4)
    assert running["total_T"] == 46
    assert running["b_Landau"] == 22
    assert 800 < running["pole_over_matching_scale_at_g0p73"] < 900


def test_fail_closed_no_gate_promotion() -> None:
    value = report()
    assert not value["verdict"]["complete_theory"]
    assert value["gate_effect"]["G8"] == "PARTIAL_SELECTOR_CANDIDATE_ONLY"
    assert not value["gate_effect"]["promotions"]


def test_generated_artifacts_current() -> None:
    value = report()
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)
