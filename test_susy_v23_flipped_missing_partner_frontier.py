from __future__ import annotations

import copy
import json

import pytest

import susy_v23_flipped_missing_partner_frontier as frontier


@pytest.fixture(scope="module")
def report() -> dict:
    return frontier.build_report()


def test_table_i_and_three_complete_27s(report: dict) -> None:
    fields = report["field_content"]
    assert [sum(r["sector"] == f"matter_27_family_{i}" for r in fields) for i in range(1, 4)] == [3, 3, 3]
    by_name = {row["name"]: row for row in fields}
    assert (by_name["Phi"]["U1A_charge"], by_name["Phi"]["Z2_parity"]) == (0, -1)
    assert (by_name["C"]["U1A_charge"], by_name["C"]["Z2_parity"]) == (-2, 1)
    assert (by_name["PhiPrime"]["multiplicity"], by_name["PhiPrime"]["U1A_charge"]) == (2, 5)
    assert (by_name["PhiBarPrime"]["multiplicity"], by_name["PhiBarPrime"]["U1A_charge"]) == (2, 4)
    assert (by_name["SPrime"]["U1A_charge"], by_name["SPrime"]["VEV_status"]) == (8, "zero")


def test_exact_continuous_anomalies_and_beta_ledgers(report: dict) -> None:
    assert report["continuous_SO10xU1Vprime_anomalies"] == {
        "SO10_squared_U1Vprime": 0,
        "gravity_squared_U1Vprime": 0,
        "U1Vprime_cubed": 0,
    }
    base = report["RG_coefficients"]["base"]
    assert (base["sum_T"], base["sum_C2_times_T"], base["b10"], base["B10_10"]) == (25, "549/4", 1, 565)
    assert (base["bVprime"], base["B10_Vprime"], base["BVprime_10"], base["BVprime_Vprime"]) == ("43/3", "17/3", 255, "89/9")
    optional = report["RG_coefficients"]["with_optional_KSVZ_10"]
    assert (optional["sum_T"], optional["sum_C2_times_T"], optional["b10"], optional["B10_10"]) == (26, "567/4", 2, 599)


def test_coupled_two_loop_benchmarks(report: dict) -> None:
    base = report["coupled_two_loop_gauge_only_base"]
    assert base["alpha10_inverse_at_120MGUT"] == pytest.approx(21.71948392, abs=1e-8)
    assert base["alphaVprime_inverse_at_120MGUT"] == pytest.approx(12.36798050, abs=1e-8)
    assert base["finite_and_below_point1"]
    assert base["formal_common_threshold_and_gA_zero_truncation"] is True
    assert base["omits_anomalous_U1A_gauge_coupling_and_kinetic_mixing"] is True
    assert base["omits_intermediate_SU5xU1X_breaking_and_matching"] is True
    assert base["physical_stage_resolved_RGE_closed"] is False


def test_published_structural_ranks_and_light_pair(report: dict) -> None:
    ranks = report["published_missing_partner_rank_ledger"]
    assert (ranks["triplet"]["generic_rank"], ranks["triplet"]["nullity"]) == (7, 0)
    assert (ranks["doublet"]["generic_rank"], ranks["doublet"]["nullity"]) == (3, 1)
    assert ranks["doublet"]["identically_zero_row"] == "CBar"
    assert ranks["doublet"]["identically_zero_column"] == "C"
    assert ranks["doublet"]["published_light_pair"] == {"Hu": "(LbarPrime)_C", "Hd": "(LbarPrimeStar)_CBar"}


def test_threshold_exponents_are_fail_closed(report: dict) -> None:
    thresholds = report["Table_I_threshold_frontier"]
    assert thresholds["Table_I_Delta"] == "-1/2"
    assert thresholds["minimum_triplet_determinant_exponent"] == 27
    assert thresholds["minimum_heavy_doublet_determinant_exponent"] == 17
    assert len(thresholds["triplet_minimum_matching_1_based"]) == 7
    assert len(thresholds["heavy_doublet_minimum_matching_1_based"]) == 3
    assert thresholds["staged_breaking"]["vPhi_over_vC"] == pytest.approx(9.690941652528, abs=1e-12)
    assert thresholds["staged_breaking"]["between_vPhi_and_vC"] == "SU5xU1X"
    assert thresholds["staged_breaking"]["single_stage_SO10xU1Vprime_running_is_physical"] is False
    assert thresholds["physical_threshold_spectrum_closed"] is False


def test_anomalous_u1a_planck_blocker(report: dict) -> None:
    u1a = report["anomalous_U1A_frontier"]
    assert u1a["raw_b_U1A"] == 2241
    assert u1a["raw_b_breakdown"] == {
        "three_complete_27_matter": 702,
        "Table_I_nonsinglet_Higgs": 1456,
        "Table_I_singlets": 83,
    }
    assert u1a["one_loop_pole_mu_over_MGUT_at_k1"] == pytest.approx(1.06960540757, abs=1e-11)
    assert u1a["required_kA_strictly_greater_for_pole_above_120MGUT"] == pytest.approx(71.147359122365, abs=1e-10)
    assert u1a["raw_Vprime_U1A_kinetic_mixing_trace"] == 48
    assert u1a["raw_sum_T_SO10_times_qA_squared"] == 260
    assert u1a["omitted_two_loop_B10_A_at_kA1"] == 1040
    assert u1a["Vprime_U1A_kinetic_mixing_generated"] is True
    assert u1a["Planck120_perturbativity_demonstrated"] is False
    assert u1a["Green_Schwarz_normalization_and_hidden_spectrum_landed"] is False


def test_optional_single_10_ksvz_is_rejected(report: dict) -> None:
    ksvz = report["optional_KSVZ_extension"]
    assert ksvz["optional_not_part_of_base_candidate"]
    assert ksvz["route_status"] == "REJECTED_SINGLE_SO10_10_KSVZ_COMPLETION"
    assert (ksvz["formal_N_DW_after_charge_two_VEV_quotient"], ksvz["fa_GeV"]) == (1, 37_140_323_529)
    assert ksvz["axion_mass_micro_eV_using_5p7_relation"] == pytest.approx(153.472007198573, abs=1e-10)
    assert ksvz["flipped_hypercharge_decomposition"]["delta_b_SM_canonical"] == {"b1": "1/10", "b2": 1, "b3": 1}
    assert ksvz["flipped_hypercharge_decomposition"]["is_complete_SM_5_plus_5bar"] is False
    assert ksvz["flipped_hypercharge_decomposition"]["contains_fractionally_charged_states"] is True
    assert ksvz["universal_below_GUT_threshold_exists"] is False
    assert ksvz["coupled_two_loop_threshold_benchmark_valid"] is False
    assert ksvz["viable_KSVZ_extension_landed"] is False
    assert ksvz["U1A_PQ_quality_compatibility_landed"] is False
    assert ksvz["PQ_quality_closed"] is False


def test_model_is_a_zero_W_fail_closed_scaffold(report: dict) -> None:
    model = frontier.MODEL_PATH.read_text(encoding="utf-8")
    assert 'Model`Name = "SO10U1V23FlippedMissingPartner";' in model
    assert model.count("SuperFields[[") == len(frontier.BASE_FIELDS)
    assert model.count("SuperPotential = 0;") == 1
    assert model.count("NameOfStates = {GaugeES};") == 1
    assert '"OptionalKSVZEncodedAsSuperFields" -> False' in model
    assert "{CHiggs, 1, c16," in model
    assert "{C, 1, c16," not in model
    assert report["model_source"]["SuperPotential"] == 0
    assert report["model_source"]["Wolfram_syntax_parse_observed"] is True
    assert report["model_source"]["SARAH_initialization_attested"] is False
    assert report["model_source"]["executable_SARAH_model_landed"] is False
    assert report["model_source"]["missing_auxiliary_model_files"] == ["parameters.m", "particles.m"]


def test_all_full_gates_remain_false(report: dict) -> None:
    assert report["closure_counts"] == {"closed": 0, "open": 8}
    assert [row["gate"] for row in report["G1_G8"]] == [f"G{i}" for i in range(1, 9)]
    assert all(row["closed"] is False and row["full_gate_claim"] is False for row in report["G1_G8"])
    assert report["route_verdict"]["accepted_as_complete_theory"] is False
    assert report["published_physics_caveats"]["Table_I_charge_set_called_unrealistic_for_neutrino_scale_by_source"] is True


def test_frozen_outputs_and_hash(report: dict) -> None:
    assert report["n_failed"] == 0, report["failures"]
    assert json.loads(frontier.OUT_JSON.read_text(encoding="utf-8")) == report
    assert frontier.OUT_MD.read_text(encoding="utf-8") == frontier.markdown(report)
    assert frontier.MODEL_PATH.read_text(encoding="utf-8") == frontier.render_model()
    changed = copy.deepcopy(report)
    changed["route_verdict"]["accepted_as_complete_theory"] = True
    assert frontier.canonical_sha(changed) != frontier.canonical_sha(report)
