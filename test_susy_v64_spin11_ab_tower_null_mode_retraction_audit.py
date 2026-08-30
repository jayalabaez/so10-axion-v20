from __future__ import annotations

import json
from fractions import Fraction

import susy_v64_spin11_ab_tower_null_mode_retraction_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def test_bound_cores_are_canonical_and_expected() -> None:
    value = report()
    lineage = value["lineage"]
    assert lineage["bound_V63_route_core"] == audit.EXPECTED_V63_ROUTE_CORE
    assert lineage["bound_V63_master_core"] == audit.EXPECTED_V63_MASTER_CORE
    assert lineage["bound_V62_route_core"] == audit.EXPECTED_V62_ROUTE_CORE
    assert lineage["bound_V59_spin11_core"] == audit.EXPECTED_V59_SPIN11_CORE
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["n_failed_integrity_checks"] == 0


def test_finite_mass_operator_has_exact_right_kernel() -> None:
    finite = report()["finite_KK_mass_operator"]
    assert finite["all_truncations_pass"]
    assert finite["per_complex_Q_direction"]["shape"] == "N x (N+1)"
    for row in finite["exact_rational_truncation_checks"]:
        assert row["shape"] == [row["N"], row["N"] + 1]
        assert row["rank"] == row["N"]
        assert row["right_nullity"] == 1
        assert row["diagonal_minor_nonzero"]
        assert row["null_residual_zero"]
        assert set(row["null_residual_exact"]) == {"0"}


def test_mass_operator_action_annihilates_general_formula_exactly() -> None:
    diagonal = [Fraction(3, 7), Fraction(5, 11), Fraction(13, 17)]
    mu = Fraction(19, 23)
    vector = [-mu / k for k in diagonal] + [Fraction(1)]
    assert audit.exact_mass_action(diagonal, mu, vector) == [
        Fraction(0),
        Fraction(0),
        Fraction(0),
    ]


def test_infinite_null_mode_is_normalizable_and_has_flat_bulk_profile() -> None:
    infinite = report()["infinite_normalizable_null_mode"]
    assert infinite["norm_finite_for_every_finite_alpha"]
    assert "pi^2/2" in infinite["half_integer_sum_identity"]
    assert "1+g5^2 v^2 L" in infinite["normalization_derivation"]
    convergence = infinite["norm_convergence"]
    assert convergence[-1]["error_to_exact"] < convergence[0]["error_to_exact"]
    assert convergence[-1]["error_to_exact"] < 0.001
    assert all(
        sample["absolute_error_to_minus_1"] < 0.001
        for sample in infinite["profile_samples"]
    )
    assert "flat profile" in infinite["bulk_profile"]


def test_massive_determinant_converges_but_omits_kernel() -> None:
    massive = report()["massive_determinant_and_secular_flow"]
    sample = massive["sample"]
    convergence = sample["convergence"]
    assert convergence[-1]["error_to_closed_form"] < convergence[0][
        "error_to_closed_form"
    ]
    assert convergence[-1]["error_to_closed_form"] < 0.001
    assert "M_N M_N^dag" in massive["operator_mismatch"]
    assert "exact zero eigenvalue" in massive["operator_mismatch"]


def test_massive_roots_are_bracketed_and_zero_is_spurious() -> None:
    massive = report()["massive_determinant_and_secular_flow"]
    assert massive["all_massive_roots_bracketed"]
    assert massive["x_zero_is_spurious_after_multiplication"]
    assert "x=0 explicitly excluded" in massive["massive_secular_equation"]
    assert "1+alpha^2" in massive["equivalent_unmultiplied_equation"]
    for row in massive["massive_roots"]:
        assert row["lower_half_integer_pi"] < row["x"] < row["upper_integer_pi"]
        assert abs(row["residual"]) < 1.0e-10


def test_primary_source_and_representation_correct_v63() -> None:
    correction = report()["representation_and_primary_source_correction"]
    source = correction["primary_source_certificate"]
    assert source["reported_count"] == {
        "rank_breaking_NG_directions": 21,
        "eaten_by_zero_mode_gauge_fields": 9,
        "uneaten_tree_massless": 12,
    }
    assert source["agrees_with_rectangular_kernel"]
    assert correction["V63_XY_claim"] == "RETRACTED"
    assert correction["SM_decomposition"]["Q_type_rank_vev_coupled"] == [
        "(3,2)_(+1/6)",
        "(3bar,2)_(-1/6)",
    ]
    assert "X/Y" in correction["correction"]


def test_corrected_ir_ledger_closes_without_wz() -> None:
    ledger = report()["corrected_post_VEV_anomaly_ledger"]
    assert ledger["surviving_sector"]["complex_chiral_components"] == 12
    assert ledger["surviving_sector"]["mixed_R_anomaly"] == {
        "Delta_A3": "-2",
        "Delta_A2": "-3",
    }
    assert ledger["MSSM_only_ledger_from_V61"] == {"A3": "3", "A2": "1"}
    assert ledger["actual_IR_ledger_MSSM_plus_exotics"] == {
        "A3": "1",
        "A2": "-2",
    }
    assert ledger["V62_orbifold_wall_sum"] == {"A3": "1", "A2": "-2"}
    assert ledger["matching_identities"]["both_close_without_WZ"]
    assert ledger["V63_forced_WZ_status"].startswith("RETRACTED")
    assert ledger["WZ_functional_for_this_matching"] == "NOT_FORCED"
    assert len(ledger["why_no_V63_WZ_functional_was_derived"]) == 5
    assert any(
        "q=0" in reason
        for reason in ledger["why_no_V63_WZ_functional_was_derived"]
    )


def test_z4r_inventory_has_no_current_full_rank_mass() -> None:
    inventory = report()["Z4R_mass_inventory"]
    scan = {row["operator"]: row for row in inventory["operator_scan"]}
    assert not scan["X_Q X_Qbar"]["allowed_in_W"]
    assert scan["S X_Q X_Qbar (contained in S C Cbar)"]["allowed_in_W"]
    assert inventory["certified_rank_vacuum_S"] == 0
    assert not inventory["q2_conjugate_Q_partner_in_current_inventory"]
    assert not inventory["full_rank_Q_type_mass_matrix_in_current_vacuum"]


def test_retraction_ledger_is_explicit_and_scoped() -> None:
    rows = report()["retraction_ledger"]
    retracted = [row for row in rows if "RETRACTED" in row["V64_status"]]
    preserved = [row for row in rows if row["V64_status"].startswith("PRESERVED")]
    assert len(retracted) == 4
    assert len(preserved) == 2
    assert any("WZ" in row["prior_claim"] for row in retracted)
    assert any("X/Y" in row["prior_claim"] for row in retracted)


def test_repair_acceptance_is_fail_closed() -> None:
    criteria = report()["repair_acceptance_criteria"]
    assert [row["id"] for row in criteria] == ["R1", "R2", "R3", "R4", "R5"]
    assert any("right nullity" in row["fail_closed_test"] for row in criteria)
    assert any("Dai-Freed" in row["fail_closed_test"] for row in criteria)
    assert any("proton" in row["criterion"] for row in criteria)


def test_strict_g1_and_all_gates_remain_open() -> None:
    value = report()
    matrix = {row["criterion"]: row["status"] for row in value["strict_G1_matrix"]}
    assert matrix["rank_breaking_without_light_exotics"] == "FAIL_EXACT"
    assert matrix["V63_Goldstone_dissolution"] == "RETRACTED"
    assert matrix["post_VEV_WZ_inflow"] == "NOT_FORCED"
    assert matrix["strict_G1"] == "OPEN_WITH_CURRENT_SPIN11_ACTION_REJECTED"
    assert len(value["gate_ledger"]) == 8
    assert all(row["status"] == "OPEN" for row in value["gate_ledger"])
    assert value["terminal_decision"]["gate_promotions"] == 0


def test_terminal_decision_does_not_overclaim() -> None:
    terminal = report()["terminal_decision"]
    assert not terminal["V63_dissolution_claim_valid"]
    assert not terminal["V63_forced_WZ_claim_valid"]
    assert not terminal["current_Spin11_action_accepted"]
    assert not terminal["V64_G1_closed"]
    assert not terminal["complete_theory"]
    assert "twelve" in terminal["exact_blocker"]


def test_claim_boundary_is_honest() -> None:
    boundary = report()["claim_boundary"]
    assert not boundary["new_fundamental_physics_invented"]
    assert boundary["exact_quadratic_action_result"]
    assert boundary["massive_determinant_not_confused_with_full_chiral_spectrum"]
    assert boundary["V62_large_gauge_and_saxion_obligations_not_overclaimed"]
    assert boundary["no_gate_promotion"]


def test_generated_json_and_markdown_are_current() -> None:
    value = report()
    assert audit.JSON_PATH.is_file()
    assert audit.MD_PATH.is_file()
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)


def test_source_manifest_is_current() -> None:
    manifest = report()["source_manifest"]
    assert manifest["audit_script"]["sha256"] == audit.sha256_file(
        audit.Path(audit.__file__)
    )
    assert manifest["pytest"]["sha256"] == audit.sha256_file(audit.TEST_PATH)
    assert manifest["bound_V63_route"]["sha256"] == audit.sha256_file(
        audit.V63_ROUTE_PATH
    )
    assert manifest["bound_V63_master"]["sha256"] == audit.sha256_file(
        audit.V63_MASTER_PATH
    )
    assert manifest["bound_V62_route"]["sha256"] == audit.sha256_file(
        audit.V62_ROUTE_PATH
    )
    assert manifest["bound_V59_spin11"]["sha256"] == audit.sha256_file(
        audit.V59_SPIN11_PATH
    )
    assert {source["id"] for source in manifest["primary_sources"]} >= {
        "HOSOTANI_YAMATSU_2015",
        "HALL_NOMURA_2001",
        "HEBECKER_2001",
        "ARKANI_HAMED_GREGOIRE_WACKER_2001",
        "PILO_RIOTTO_2002",
        "GRIPAIOS_2008",
        "GARCIA_ETXEBARRIA_MONTERO_2018",
    }
