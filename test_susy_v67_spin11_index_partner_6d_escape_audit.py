from __future__ import annotations

import copy
import json
import math

import pytest

import susy_v67_spin11_index_partner_6d_escape_audit as audit


@pytest.fixture(scope="module")
def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def _rehash(value: dict) -> dict:
    value["core_sha256"] = audit.canonical_sha(value)
    return value


def test_bound_lineage_and_canonical_core(report: dict) -> None:
    assert report["lineage"]["bound_input_cores"] == audit.EXPECTED_CORES
    assert report["core_sha256"] == audit.canonical_sha(report)
    assert report["n_integrity_checks"] == len(report["integrity_checks"])
    assert report["n_failed_integrity_checks"] == 0
    assert all(report["integrity_checks"].values())


def test_finite_index_change_is_exact(report: dict) -> None:
    repair = report["spectral_index_repair"]["minimal_index_change"]
    assert repair["finite_determinant"] == "det A'_N = M product_n k_n"
    assert repair["kernel_trivial_if"] == "M != 0 and k_0=pi/(2L)>0"
    assert repair["all_finite_checks_pass"]
    assert len(repair["finite_exact_checks"]) == 8
    assert all(row["determinant"] == row["expected_M_product_k"] for row in repair["finite_exact_checks"])


def test_v64_null_is_rebound_and_candidate_zero_is_removed(report: dict) -> None:
    spectral = report["spectral_index_repair"]
    assert spectral["bound_V64_operator"]["right_kernel_dimension"] == 1
    assert spectral["bound_V64_operator"]["normalizable_infinite_kernel"] is True
    tower = spectral["inherited_5D_infinite_tower"]
    assert tower["exact_zero_removed"] is True
    assert tower["Dai_Freed_or_GS_changes_index"] is False
    assert "inherited one-dimensional V64" in tower["scope"]


def test_light_root_equation_is_checked_without_a_mass_overclaim(report: dict) -> None:
    light = report["spectral_index_repair"]["light_singular_value"]
    assert light["all_root_residuals_below_1e_10"]
    assert light["no_parametrically_light_mode_proved_without_parameters"] is False
    assert "alpha^2 tan(mL)/(mL)" in light[
        "exact_equation_for_inherited_5D_operator_below_first_KK_pole"
    ]
    for row in light["numerical_dimensionless_checks"]:
        assert 0.0 < row["m_times_L"] < math.pi / 2.0
        assert abs(row["equation_residual"]) < 1.0e-10


def test_light_root_branch_is_fail_closed() -> None:
    assert audit.light_root(0.0, 1.0) == 1.0
    with pytest.raises(ValueError, match="no secular root below"):
        audit.light_root(0.0, math.pi / 2.0)
    with pytest.raises(ValueError, match="no secular root below"):
        audit.light_root(0.0, 10.0)
    with pytest.raises(ArithmeticError, match="not bracketed"):
        audit.light_root(1.0, 1.0e12)


def test_finite_N_singular_value_independently_matches_secular_sum(
    report: dict,
) -> None:
    light = report["spectral_index_repair"]["light_singular_value"]
    rows = light["independent_finite_N_ATA_checks"]
    assert len(rows) == 4
    assert light["all_independent_finite_N_checks_pass"]
    assert light["finite_roots_converge_from_above_in_sample"]
    assert all(row["absolute_difference"] < 1.0e-9 for row in rows)
    assert all(row["finite_root_minus_infinite_root"] > 0.0 for row in rows)


def test_6d_candidate_does_not_import_the_5d_tangent_spectrum(report: dict) -> None:
    scope = report["spectral_index_repair"]["six_dimensional_nonimport"]
    assert scope["status"] == "OPEN_NOT_THE_INHERITED_5D_TAN_EQUATION"
    assert "logarithmically" in scope["point_local_double_KK_asymptotic"]
    assert "cannot be imported" in scope["consequence"]


def test_z4r_mass_terms_and_tree_schur_result(report: dict) -> None:
    charge = report["charge_anomaly_and_proton_audit"]
    assert charge["mass_terms_preserve_Z4R_without_q2_VEV"]
    schur = charge["tree_level_Schur_theorem"]
    assert schur["status"] == "PASS_MINIMAL_ONE_SIDED_HOLOMORPHIC_CHANNEL_ONLY"
    assert schur["candidate_value"] == "lambdatilde=0 exactly by Z4R"
    assert schur["induced_four_matter_superpotential"] == "0"
    assert "not_a_complete_selector_proof" in schur


def test_partner_anomaly_cancellation_and_new_gs_shift(report: dict) -> None:
    charge = report["charge_anomaly_and_proton_audit"]
    assert charge["global_mixed_R_anomaly"]["sum"] == {"Delta_A3": 0, "Delta_A2": 0}
    abelian = charge["global_mixed_R_anomaly"]["integrated_abelian_and_gravity"]
    assert abelian["qR2_partner_delta"] == {
        "Delta_AYY_unnormalized": "1/3",
        "Delta_AYY_GUT_normalized": "1/5",
        "Delta_AXX": "12",
        "Delta_AYX": "-2",
        "Delta_Agravity": "12",
    }
    assert all(value == "0" for value in abelian["sum"].values())
    assert abelian["all_cancel"]
    gs = charge["formal_V62_5D_integrated_GS_diagnostic"]
    assert gs["residue_if_V62_5D_convention_is_carried_mod4"] == {"SU3": 0, "SU2": 2}
    assert gs["formal_delta_c_diagnostic_mod4"] == {"SU3": 0, "SU2": 2}
    assert gs["residue_after_formal_diagnostic_mod4"] == {"SU3": 0, "SU2": 0}
    assert gs["formal_5D_congruence_arithmetic_closes"]
    assert "NOT_A_DERIVED_6D" in gs["status"]
    assert "not computed" in gs["not_a_6D_local_completion"]


def test_existing_5d_walls_reject_q_only_patch(report: dict) -> None:
    geometry = report["geometry_and_6D_escape"]
    current = geometry["current_5D_action"]
    assert current["Q_only_qR2_local_field_allowed_at_y0"] is False
    assert current["Q_only_qR2_local_field_allowed_at_yL"] is False
    assert current["wall_local_Q_only_patch_exists"] is False
    assert current["split_bulk_5D_status"].startswith("UNCLASSIFIED")
    assert current["same_action_patch_status"] == "NO_WALL_LOCAL_PATCH_PROVED__SPLIT_BULK_UNRESOLVED"
    assert geometry["D67_6D_escape_candidate"]["status"] == "CANDIDATE_NEW_ACTION_NOT_CONSTRUCTED"


def test_acceptance_and_all_eight_gates_fail_closed(report: dict) -> None:
    assert any(row["status"].startswith("OPEN") for row in report["acceptance_matrix"])
    assert len(report["gate_ledger"]) == 8
    assert all(row["status"] == "OPEN" and not row["V67_closed"] for row in report["gate_ledger"])
    terminal = report["terminal_decision"]
    assert terminal["current_bound_Spin11_action"] == "REJECTED"
    assert terminal["exact_null_mode_removed_in_inherited_5D_candidate_operator"] is True
    assert terminal["physical_colored_mass_certified"] is False
    assert terminal["same_action_microscopic_completion_found"] is False
    assert terminal["closed_gates"] == []
    assert terminal["complete_theory"] is False


@pytest.mark.parametrize(
    "mutator",
    [
        lambda r: r["spectral_index_repair"]["minimal_index_change"].update(
            finite_determinant="det=0"
        ),
        lambda r: r["spectral_index_repair"]["light_singular_value"].update(
            no_parametrically_light_mode_proved_without_parameters=True
        ),
        lambda r: r["charge_anomaly_and_proton_audit"]["formal_V62_5D_integrated_GS_diagnostic"].update(
            formal_delta_c_diagnostic_mod4={"SU3": 0, "SU2": 0}
        ),
        lambda r: r["geometry_and_6D_escape"]["current_5D_action"].update(
            wall_local_Q_only_patch_exists=True
        ),
        lambda r: r["terminal_decision"].update(V67_G1_closed=True),
    ],
)
def test_semantic_mutations_fail_even_after_rehash(report: dict, mutator) -> None:
    changed = copy.deepcopy(report)
    mutator(changed)
    _rehash(changed)
    with pytest.raises(RuntimeError, match="V67 recomputation mismatch"):
        audit.validate(changed)


def test_generated_artifacts_match_live_recomputation(report: dict) -> None:
    assert audit.JSON_PATH.is_file()
    assert audit.MD_PATH.is_file()
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(report)


def test_primary_source_manifest_is_bound(report: dict) -> None:
    assert {row["id"] for row in report["source_manifest"]["primary_sources"]} == {
        "DIENES_DUDAS_GHERGHETTA_1999",
        "HALL_NOMURA_OKUI_SMITH_2002",
        "CSAKI_GROJEAN_HUBISZ_SHIRMAN_TERNING_2004",
        "ARKANI_HAMED_COHEN_GEORGI_2001",
        "VON_GERSDORFF_QUIROS_2003",
        "GARCIA_ETXEBARRIA_MONTERO_2019",
    }
    scopes = {
        row["id"]: row["scope"]
        for row in report["source_manifest"]["primary_sources"]
    }
    assert "arbitrary vectorlike" not in scopes["DIENES_DUDAS_GHERGHETTA_1999"]
    assert "anomaly-safe" not in scopes["CSAKI_GROJEAN_HUBISZ_SHIRMAN_TERNING_2004"]
    assert "four-dimensional zero modes suffice" in scopes["ARKANI_HAMED_COHEN_GEORGI_2001"]
    assert "five- and six-dimensional" in scopes["VON_GERSDORFF_QUIROS_2003"]
    for row in report["source_manifest"]["local_files"]:
        path = audit.Path(row["path"])
        assert row["exists"] == path.is_file()
        assert row["sha256"] == audit.sha256_file(path)
