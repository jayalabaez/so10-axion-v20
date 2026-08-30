"""Regression tests for the V42 PS/PQ/EW VEV epsilon G7 audit."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import susy_v42_g7_ps_vev_epsilon_audit as v42


ROOT = Path(__file__).resolve().parent


def test_declared_vev_ring_has_exact_z9_and_r_parity_property() -> None:
    ring = v42.build_report()["declared_VEV_ring_theorem"]
    assert ring["all_VEV_generators_Z9_neutral"]
    assert ring["all_VEV_generators_R_even"]
    assert "q_Z9(D)=0" in ring["all_order_charge_formula"]["Z9"]


def test_low_degree_ps_vev_sources_are_classified_without_false_closure() -> None:
    rows = {row["label"]: row for row in v42.build_report()["explicit_low_degree_contraction_classification"]}
    assert rows["conventional_left_same_orientation_epsilon"]["selector_signature"]["Z9"] == 3
    assert rows["conventional_right_same_orientation_epsilon"]["selector_signature"]["Z9"] == 6
    for label in ("left_epsilon_one_PS_VEV_precursor", "right_epsilon_one_PS_VEV_precursor"):
        signature = rows[label]["selector_signature"]
        assert signature["Z9"] == 0
        assert signature["Z4R"] == 3
        assert not signature["W_allowed_by_listed_selectors"]
        assert not signature["Kahler_allowed_by_listed_selectors"]
    assert rows["delta_left_lepton_RPV_control"]["selector_signature"]["Z9"] == 3


def test_explicit_six_matter_witness_is_clean_and_b_l_violating() -> None:
    witness = v42.build_report()["selector_allowed_six_matter_witness"]
    assert witness["operator"] == "ThetaPlus^2 (Qc)^6 (Sbc)^2 / M^7"
    assert witness["selector_signature"] == {
        "U1F": 0,
        "Z9": 0,
        "Z4R": 2,
        "Z5610": 0,
        "PQ_numerator_over_170": 0,
        "W_allowed_by_listed_selectors": True,
        "Kahler_allowed_by_listed_selectors": False,
    }
    assert (witness["Delta_B"], witness["Delta_L"]) == (-1, -3)
    assert witness["full_listed_selector_clean"]


def test_bounded_scan_identifies_no_clean_row_below_degree_ten() -> None:
    scan = v42.build_report()["bounded_single_epsilon_frontier"]
    assert scan["no_clean_W_selector_row_below_degree_ten"]
    assert scan["earliest_clean_W_selector_row"]["complete_field_degree"] == 10
    assert scan["earliest_clean_W_selector_row"]["counts"] == {"Q": 0, "Qc": 6, "Sbc": 2, "Sc": 0, "H": 0}
    assert len(scan["clean_W_selector_rows"]) >= 1


def test_written_artifacts_are_reproducible() -> None:
    subprocess.run([sys.executable, "-B", str(ROOT / "susy_v42_g7_ps_vev_epsilon_audit.py"), "--write"], check=True, cwd=ROOT)
    subprocess.run([sys.executable, "-B", str(ROOT / "susy_v42_g7_ps_vev_epsilon_audit.py"), "--check"], check=True, cwd=ROOT)
    payload = json.loads((ROOT / "SUSY_V42_G7_PS_VEV_EPSILON_AUDIT.json").read_text(encoding="utf-8"))
    assert payload["status"] == v42.STATUS
    assert not payload["gate_boundary"]["G7_closed"]
