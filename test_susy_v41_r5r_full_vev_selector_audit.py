"""Tests for the V41 all-visible-VEV discrete-R no-go audit."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import susy_v41_r5r_full_vev_selector_audit as audit


ROOT = Path(__file__).resolve().parent
REPORT = audit.build_report()


def test_rebuilt_w_has_type_i_and_every_term_is_r5_allowed() -> None:
    witness = REPORT["representative_R5_operator_witness"]
    assert witness["all_required_terms_allowed"]
    assert witness["type_I_mechanism"]["source"] == "y_N Sbc Qc Nv + M_N Nv Nv / 2"
    assert {row["R5"] for row in witness["required_terms"]} == {2}


def test_all_visible_vevs_and_hh_dressings_preserve_the_source_block() -> None:
    proof = REPORT["all_visible_VEV_protection"]
    assert proof["R5_of_nonzero_visible_VEVs"] == {"H": 0, "Sc": 0, "Sbc": 0, "P": 0, "Pb": 0}
    assert proof["residual_R5_stabilizer_order"] == 5
    assert [row["R_N"] for row in proof["local_driver_sources"]] == [1, 1, 1, 1]
    assert proof["all_local_sources_forbidden"]
    assert all(row["R5_for_every_integer_k"] == 1 for row in proof["electroweak_HH_dressing_test"])
    assert all(row["forbidden_for_every_k"] for row in proof["electroweak_HH_dressing_test"])


def test_exhaustive_orders_confirm_the_single_gs_no_go() -> None:
    scan = REPORT["exhaustive_N3_to_N96_enumeration"]
    assert scan["range"] == [3, 96]
    assert scan["branch_count"] == 141
    assert scan["all_type_I_equations_hold"]
    assert scan["protective_branch_count"] == 139
    assert scan["protective_and_standard_single_GS_count"] == 0
    assert scan["protective_and_even_weaker_doubled_GS_count"] == 0
    assert REPORT["R5_core_anomaly"]["core_doubled_rows_D"] == {"SU4": 8, "SU2L": 2, "SU2R": -6}
    assert REPORT["R5_core_anomaly"]["equal_level_single_GS_universal"] is False


def test_escape_routes_are_not_silently_promoted() -> None:
    escape = REPORT["escape_requirements_not_claimed"]
    assert "cannot repair" in escape["massive_exotic_threshold_no_repair"]["consequence"]
    assert escape["multi_axion_or_nonuniversal_WZ_escape"]["formal_mod5_counterterm_witness"] == {
        "convention": "all four formal axion shifts delta=1; levels are the negatives of the listed core residues",
        "k_a_SU4": 1,
        "k_a_SU2L": 4,
        "k_a_SU2R": 3,
        "k_a_gravity": 3,
    }
    assert REPORT["decision"]["equal_level_single_GS_discrete_R_completion_found"] is False
    assert REPORT["decision"]["gates_promoted"] == []


def test_write_and_check_are_reproducible() -> None:
    result = subprocess.run(
        [sys.executable, "-B", str(ROOT / "susy_v41_r5r_full_vev_selector_audit.py"), "--write", "--check"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "PASS" in result.stdout
    payload = json.loads((ROOT / "SUSY_V41_FULL_VEV_RSYM_NO_GO_AUDIT.json").read_text(encoding="utf-8"))
    assert payload["core_sha256"] == audit.canonical_sha(payload)
