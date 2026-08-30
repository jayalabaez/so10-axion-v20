from __future__ import annotations

import json

import susy_v55_r1_degree9_proton_feasibility_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def test_selector_core_and_operator_are_bound() -> None:
    value = report()
    assert value["selector_core_sha256"] == audit.EXPECTED_SELECTOR_CORE
    assert value["operator_matching"]["total_degree"] == 9
    assert "S^4 R" in value["operator_matching"]["UV_operator"]


def test_exact_five_VEV_coefficient_map() -> None:
    matching = report()["operator_matching"]
    assert matching["coefficient_before_VEVs"] == "c / Lambda^6"
    assert matching["effective_scale"] == "Meff = Lambda / (abs(c) xS^4 xR)"


def test_experimental_and_comparison_inputs_are_scoped() -> None:
    value = report()
    assert value["experimental_input"]["partial_lifetime_lower_limit_yr_90CL"] == 5.9e33
    assert "used only for scaling" in value["comparison_contract"]["scope"]


def test_reference_required_scale_is_exact() -> None:
    row = report()["benchmark_slices"][0]
    assert abs(row["required_Meff_over_abs_kappa_GeV"] - 4.388425034760681e19) < 1e7
    assert abs(row["maximum_abs_c_times_kappa_times_xS4_xR"] - 0.05468932432454966) < 1e-14


def test_benchmark_spectra_are_parameterized_not_selected() -> None:
    rows = report()["benchmark_slices"]
    assert [row["label"] for row in rows] == [
        "published_2010_reference_spectrum",
        "illustrative_2TeV_1TeV_spectrum",
        "illustrative_5TeV_1TeV_spectrum",
        "illustrative_10TeV_2TeV_spectrum",
    ]


def test_small_equal_VEV_slices_pass_only_the_comparison_contract() -> None:
    for row in report()["benchmark_slices"]:
        for slice_ in row["illustrative_slices"]:
            assert slice_["comparison_lifetime_yr_for_abs_c_kappa_1"] > 5.9e33
            assert slice_["maximum_abs_c_times_kappa"] > 1


def test_decision_is_feasible_but_not_closed() -> None:
    decision = report()["decision"]
    assert not decision["degree9_operator_is_automatically_fatal"]
    assert not decision["degree9_operator_is_proved_safe"]
    assert not decision["G7_closed"]
    assert "Wilson tensor" in decision["required_next_artifact"]


def test_core_and_checks_are_canonical() -> None:
    value = report()
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["n_failed_checks"] == 0
    assert all(value["checks"].values())


def test_generated_artifacts_are_current() -> None:
    value = report()
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)
