"""Regression tests for the V43 targeted Z4M G7 selector repair audit."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import susy_v43_g7_z4m_selector_repair as v43


ROOT = Path(__file__).resolve().parent


def test_all_v40_and_v41_required_terms_survive_the_new_selector() -> None:
    terms = v43.build_report()["required_term_audit"]
    assert terms["V40_term_count"] == 36
    assert terms["messenger_and_effective_term_count"] == 4
    assert terms["all_U1F_neutral"]
    assert terms["all_Z9_neutral"]
    assert terms["all_Z4R_target_two"]
    assert terms["all_Z4M_neutral"]


def test_z4m_is_the_smallest_targeted_arithmetic_repair_and_preserves_dirac_route() -> None:
    report = v43.build_report()
    assert report["candidate"]["smallest_order_that_blocks_six_Qc_witness"] == 4
    assert report["candidate"]["why_Z2_and_Z3_fail"] == {"Z2_witness_charge": 0, "Z3_witness_charge": 0}
    rows = {row["label"]: row for row in report["named_B_L_and_required_operator_audit"]}
    assert rows["V42_six_matter_witness"]["selector_signature"]["Z4M"] == 2
    assert not rows["V42_six_matter_witness"]["selector_signature"]["allowed_by_new_Z4M"]
    assert rows["required_Dirac_operator"]["selector_signature"]["allowed_by_new_Z4M"]


def test_named_lower_b_l_controls_remain_blocked() -> None:
    rows = {row["label"]: row for row in v43.build_report()["named_B_L_and_required_operator_audit"]}
    for label in ("left_one_PS_VEV_precursor", "right_one_PS_VEV_precursor", "delta_RPV_control", "bilinear_LH_control"):
        assert rows[label]["selector_signature"]["Z4M"] != 0
        assert rows[label]["blocked_by_union_of_old_and_new_selectors"]
    assert rows["conventional_Q4_epsilon"]["selector_signature"]["Z9"] == 3
    assert rows["conventional_Qc4_epsilon"]["selector_signature"]["Z9"] == 6


def test_v42_frontier_is_reproduced_but_not_overclaimed() -> None:
    frontier = v43.build_report()["independent_V42_degree12_frontier"]
    assert len(frontier["rows"]) == 6
    assert frontier["blocked_rows"] == 4
    assert frontier["witness_row_blocked"]
    assert len(frontier["unblocked_orientation_neutral_rows"]) == 2


def test_no_decoupling_only_ordinary_discrete_gauge_completion() -> None:
    report = v43.build_report()
    anomaly = report["continuous_parent_and_discrete_anomaly_boundary"]
    assert anomaly["mixed_PS_rows_cancel"]
    assert anomaly["continuous_gravity_and_cubic_still_nonzero"]
    assert anomaly["Z4M_low_energy_necessary_screen"]["gravity_residue_mod_eta"] == 1
    assert not anomaly["Z4M_low_energy_necessary_screen"]["gravity_pass"]
    no_go = report["ordinary_unbroken_selector_no_go"]
    assert no_go["ordinary_no_GS_orders_passing_necessary_screen"] == [2, 3, 6]
    assert no_go["orders_that_both_pass_and_block_witness"] == []


def test_written_artifacts_are_reproducible_and_fail_closed() -> None:
    subprocess.run([sys.executable, "-B", str(ROOT / "susy_v43_g7_z4m_selector_repair.py"), "--write"], check=True, cwd=ROOT)
    subprocess.run([sys.executable, "-B", str(ROOT / "susy_v43_g7_z4m_selector_repair.py"), "--check"], check=True, cwd=ROOT)
    report = json.loads((ROOT / "SUSY_V43_G7_Z4M_SELECTOR_REPAIR_AUDIT.json").read_text(encoding="utf-8"))
    assert report["status"] == v43.STATUS
    assert not report["decision"]["candidate_is_anomaly_complete_discrete_gauge_symmetry"]
    assert not report["decision"]["G7_closed"]
