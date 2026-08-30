from __future__ import annotations

import json

import susy_v55_r1_residual_selector_no_go_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def test_upstream_and_core_are_canonical() -> None:
    value = report()
    assert value["upstream_core_sha256"] == audit.EXPECTED_UPSTREAM_CORE
    assert value["matter_operator_core_sha256"] == audit.EXPECTED_MATTER_CORE
    assert value["core_sha256"] == audit.canonical_sha(value)


def test_exact_congruence_chain_ends_at_mixed_family_F4() -> None:
    derivation = report()["theorem"]["exact_derivation_mod_N"]
    assert derivation[-1] == "2 r(Fa)+2 r(Fb)=2 r(H2)=w"


def test_full_additive_symmetry_forces_L_h_H2() -> None:
    theorem = report()["source_filter_filler_theorem"]
    assert theorem["forced_operators"] == ["h_10 A45 H2_10", "L h_10 H2_10"]
    assert theorem["renormalizable"]
    assert theorem["L_VEV_nonzero"]
    assert theorem["A_weak_block_coefficient"] == 3
    assert theorem["one_weak_component_determinant_with_h_A_H2_coefficient_x"] == "x^2"
    assert theorem["one_weak_component_determinant_at_actual_A_weak_coefficient"] == 9
    assert (theorem["weak_rank_before"], theorem["weak_rank_after"]) == (12, 16)
    assert theorem["weak_Higgs_nullity_after"] == 0
    assert "r(A)=r(B)" in theorem["exact_derivation_mod_N"][0]


def test_finite_scan_has_no_counterexample() -> None:
    finite = report()["finite_verification"]
    assert finite["maximum_modulus"] == 128
    assert finite["factors_checked"] == 254
    assert finite["solution_count"] > 0
    assert finite["counterexample_count"] == 0
    assert finite["counterexamples"] == []


def test_finite_rows_include_ordinary_and_R_factors() -> None:
    rows = report()["finite_verification"]["per_modulus"]
    assert [row["modulus"] for row in rows] == list(range(2, 129))
    assert all("ordinary_solution_count" in row and "R_solution_count" in row for row in rows)


def test_actual_continuous_U1_has_no_residual_subgroup() -> None:
    actual = report()["actual_R1_witness"]
    assert actual["VEV_charge_gcd_and_residual_order"] == 1
    assert 1 in actual["continuous_U1_VEV_charges"]


def test_actual_degree9_operator_is_exactly_neutral() -> None:
    actual = report()["actual_R1_witness"]
    assert actual["mixed_F1_squared_F2_squared_charge"] == 44
    assert actual["S_power4_R_dressing_charge"] == -44
    assert actual["total_degree"] == 9
    assert "S^4 R" in actual["allowed_operator"]


def test_SO10_tensor_filter_removes_same_family_but_keeps_mixed() -> None:
    tensor = report()["SO10_tensor_certificate"]
    assert tensor["same_family_F_i_fourth_power_is_absent"]
    assert tensor["nonzero_mixed_family_pattern"] == [2, 2, 0]
    assert tensor["mixed_family_multiplicity"] == 1


def test_scope_and_escapes_are_not_overclaimed() -> None:
    value = report()
    assert "additive residual Abelian" in value["theorem"]["scope"]
    assert len(value["logical_escapes_not_excluded"]) == 4
    assert "not promoted" in value["gate_ledger"]["G7"]


def test_all_integrity_checks_pass() -> None:
    value = report()
    assert value["n_failed_checks"] == 0
    assert all(value["checks"].values())


def test_generated_artifacts_are_current() -> None:
    value = report()
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)
