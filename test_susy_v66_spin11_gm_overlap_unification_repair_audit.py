from __future__ import annotations

import copy
import json
import math

import pytest

import susy_v66_spin11_gm_overlap_unification_repair_audit as audit


@pytest.fixture(scope="module")
def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def test_bound_lineage_and_canonical_core(report: dict) -> None:
    assert report["lineage"]["bound_V65_route_core"] == (
        audit.EXPECTED_V65_ROUTE_CORE
    )
    assert report["lineage"]["bound_V65_master_core"] == (
        audit.EXPECTED_V65_MASTER_CORE
    )
    assert report["lineage"]["bound_V64_null_mode_route_core"] == (
        audit.EXPECTED_V64_ROUTE_CORE
    )
    assert report["core_sha256"] == audit.canonical_sha(report)
    assert report["n_failed_integrity_checks"] == 0


def test_regression_scope_is_208_not_199(report: dict) -> None:
    regression = report["V65_integrity_scope_correction"]
    assert regression["file_count"] == 16
    assert regression["current_full_test_count"] == 208
    assert regression["claimed_narrow_count"] == 199
    assert regression["omitted_file_test_count"] == 9
    assert regression["full_suite_is_208_not_199"]


def test_gm_is_allowed_but_not_constructed_and_overlap_is_explicit(
    report: dict,
) -> None:
    gm = report["gm_overlap_and_retraction"]
    assert gm["z4r_allows_charge_zero_bilinear"]
    assert not gm["nonzero_mass_constructed_in_bound_action"]
    assert "Fbar^I" in gm["general_supergravity_mass"]
    assert gm["v64_null_mode_normalization"]["effective_bilinear"] == (
        "Z_eff = c_K/(1+alpha^2)"
    )
    assert gm["v64_null_mode_normalization"]["portal_amplitude_overlap"] == (
        "1/sqrt(1+alpha^2)"
    )
    assert gm["V65_action_upgrade"] == "RETRACTED"


def test_martin_vaughn_matrices_are_derived_exactly(report: dict) -> None:
    mv = report["martin_vaughn_group_theory"]
    assert mv["MSSM"]["b"] == ["33/5", "1", "-3"]
    assert mv["MSSM"]["B"] == audit.matrix_strings(
        audit.EXPECTED_MSSM_B_MATRIX
    )
    assert mv["MSSM"]["reproduces_standard_B"]
    assert mv["orphan_Q_pair"]["Delta_B"] == [
        ["1/75", "3/5", "16/15"],
        ["1/5", "21", "16"],
        ["2/15", "6", "68/3"],
    ]
    assert mv["Uc_and_Ec_companions"]["Delta_b"] == ["14/5", "0", "1"]
    assert mv["complete_10_plus_10bar"]["Delta_b"] == ["3", "3", "3"]
    assert mv["complete_10_plus_10bar"]["one_loop_shift_is_universal"]


def test_exact_one_loop_family_and_numerics(report: dict) -> None:
    one = report["one_loop_threshold_solution"]
    powers = one["analytic_c_family"]["derived_exact_powers"]
    assert powers["MS"] == "-21/32"
    assert powers["MQ"] == "11/32"
    assert powers["MG"] == "3/64"
    assert powers["alphaU_inverse_ln_c"] == "-121/(128*pi)"
    assert one["inputs"]["input_literals"]["alphaEM_inverse"] == "127.930"
    c1 = one["c_equals_1"]
    assert math.isclose(c1["MS_GeV"], 2.25084e11, rel_tol=1e-5)
    assert math.isclose(c1["MQ_GeV"], 2.25084e11, rel_tol=1e-5)
    assert math.isclose(c1["MG_GeV"], 4.54981e15, rel_tol=1e-5)
    assert math.isclose(c1["alphaU_inverse"], 34.16816, rel_tol=1e-6)
    assert c1["max_inverse_coupling_residual"] < 1e-10
    low = one["fixed_MS_1_TeV"]
    assert math.isclose(low["MQ_GeV"], 5.337995621e15, rel_tol=1e-9)
    assert math.isclose(low["MG_GeV"], 1.797161841e16, rel_tol=1e-9)


def test_two_loop_diagnostics_and_universal_scheme_shift(report: dict) -> None:
    two = report["two_loop_gauge_only_diagnostics"]
    assert two["matrix_derivation_bound"]
    assert two["diagnostics_within_tolerance"]
    raw = two["orphan_only_raw_no_matching"]["computed"]
    assert math.isclose(raw["MS"], 4.760378e11, rel_tol=1e-5)
    assert math.isclose(raw["MG"], 2.266291e15, rel_tol=1e-5)
    assert math.isclose(raw["alphaU"], 0.02859797, rel_tol=1e-5)
    dr = two["orphan_only_universal_MSbar_to_DRbar"]
    assert "C_a(G)/(12pi)" in dr["matching"]
    assert math.isclose(dr["computed"]["MS"], 4.99199e11, rel_tol=1e-5)
    assert math.isclose(dr["computed"]["MG"], 2.36709e15, rel_tol=1e-5)
    assert math.isclose(
        dr["computed"]["alphaU_inverse"], 34.9406, rel_tol=1e-5
    )
    ten = two["full_ten_raw_no_matching"]["computed"]
    assert math.isclose(ten["MS"], 1.383905e4, rel_tol=1e-5)
    assert math.isclose(ten["MG"], 1.216382e16, rel_tol=1e-5)
    assert math.isclose(ten["alphaU"], 0.07873997, rel_tol=1e-5)
    assert len(two["not_included"]) == 4


def test_two_candidate_extensions_are_fail_closed(report: dict) -> None:
    branches = {row["id"]: row for row in report["candidate_extensions"]}
    assert set(branches) == {"H66", "T66"}
    assert all(
        row["status"] == "CANDIDATE_CONDITIONAL_EXTENSION"
        and row["not_complete"]
        for row in branches.values()
    )
    assert not branches["T66"]["baryon_safety"]["inherits_V65_claim"]
    assert "Uc_X dc dc" in branches["T66"]["baryon_safety"]["reason"]
    assert "Ec_X L L" in branches["T66"]["baryon_safety"]["reason"]


def test_acceptance_criteria_and_gates_remain_open(report: dict) -> None:
    criteria = report["acceptance_criteria"]
    assert [row["id"] for row in criteria] == [
        "A1",
        "A2",
        "A3",
        "A4",
        "A5",
        "A6",
        "A7",
        "A8",
    ]
    assert all(row["status"] == "OPEN" for row in criteria)
    assert len(report["gate_ledger"]) == 8
    assert all(row["status"] == "OPEN" for row in report["gate_ledger"])
    terminal = report["terminal_decision"]
    assert terminal["current_bound_action_status"] == "REJECTED"
    assert terminal["V65_conditionally_viable_upgrade"] == "RETRACTED"
    assert terminal["WZ_term"] == "NONE_FORCED"
    assert not terminal["V66_G1_closed"]
    assert not terminal["complete_theory"]


@pytest.mark.parametrize(
    ("path", "replacement"),
    [
        (
            ("gm_overlap_and_retraction", "nonzero_mass_constructed_in_bound_action"),
            True,
        ),
        (
            (
                "martin_vaughn_group_theory",
                "orphan_Q_pair",
                "Delta_B",
                0,
                0,
            ),
            "999",
        ),
        (
            ("one_loop_threshold_solution", "c_equals_1", "MS_GeV"),
            1000.0,
        ),
        (
            ("candidate_extensions", 1, "baryon_safety", "inherits_V65_claim"),
            True,
        ),
        (("terminal_decision", "V66_G1_closed"), True),
    ],
)
def test_validator_rejects_recomputed_core_mutations(
    report: dict, path: tuple, replacement: object
) -> None:
    value = copy.deepcopy(report)
    target = value
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = replacement
    value["core_sha256"] = audit.canonical_sha(value)
    with pytest.raises(RuntimeError, match="V66 recomputation mismatch"):
        audit.validate(value)


def test_generated_json_and_markdown_are_current(report: dict) -> None:
    assert audit.JSON_PATH.is_file()
    assert audit.MD_PATH.is_file()
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(
        report
    )


def test_source_manifest_is_current(report: dict) -> None:
    manifest = report["source_manifest"]
    for row in manifest["local_files"]:
        path = audit.Path(row["path"])
        assert row["exists"] == path.is_file()
        assert row["sha256"] == audit.sha256_file(path)
    assert {source["id"] for source in manifest["primary_sources"]} == {
        "PDG_2025",
        "MARTIN_VAUGHN_1994",
        "GIUDICE_MASIERO_1988",
        "LEE_ET_AL_2010",
        "HOSOTANI_YAMATSU_2015",
    }
