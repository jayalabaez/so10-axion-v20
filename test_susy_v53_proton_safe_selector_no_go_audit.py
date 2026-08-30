from __future__ import annotations

import json

import susy_v53_proton_safe_selector_no_go_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def test_exact_representation_dimensions_and_F4_multiplicity() -> None:
    value = report()
    assert value["integrity_checks"]["representation_dimensions_are_54_45_16_16_10_48_4"]
    assert value["exact_D5_invariant_census"]["fatal_F4_row"]["Spin10_singlet_multiplicity"] == 6


def test_complete_degree_four_census_is_nonempty_and_hashed() -> None:
    census = report()["exact_D5_invariant_census"]
    assert census["total_multidegrees"] == sum(
        row["multidegrees"] for row in census["degree_counts"].values()
    )
    assert len(census["rows_sha256"]) == 64
    assert all(row["degree"] <= 4 for row in census["rows"])


def test_non_r_symbolic_no_go_anchor() -> None:
    for modulus in range(2, 65):
        for charges in audit.cyclic_solutions(modulus, False):
            assert 4 * charges["F"] % modulus == 0


def test_r_symbolic_no_go_anchor() -> None:
    for modulus in range(2, 65):
        w = 2 % modulus
        for charges in audit.cyclic_solutions(modulus, True):
            assert 4 * charges["F"] % modulus == w


def test_bounded_search_finds_no_proton_safe_assignment() -> None:
    search = report()["bounded_cyclic_search"]
    assert search["maximum_modulus"] == 64
    assert not search["proton_safe_solutions"]
    assert all(row["solutions_forbidding_F4"] == 0 for row in search["rows"])


def test_product_groups_are_fail_closed() -> None:
    value = report()
    assert not value["verdict"]["finite_Abelian_product_escape"]
    assert "componentwise" in value["exact_modular_no_go"]["product_groups"]


def test_smallest_escape_is_not_mislabeled_complete() -> None:
    escape = report()["smallest_escape"]
    assert len(escape["required_action_changes"]) == 3
    assert escape["illustrative_operator_level_Z5_non_R_charges_not_yet_anomaly_complete"]["F"] == 1
    assert "not constructed" in escape["decision"]
    assert "fails closed" in escape["decision"]


def test_no_gate_promotion() -> None:
    effect = report()["gate_effect"]
    assert effect["G2"] == "OPEN"
    assert effect["G7"] == "OPEN"
    assert effect["G8"].startswith("OPEN")
    assert not effect["clauses_promoted"]


def test_generated_artifacts_current() -> None:
    value = report()
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)
