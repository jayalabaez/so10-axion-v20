"""Regression tests for the V39 split-six source-level repair."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import susy_v39_g7_g8_architecture as v39


ROOT = Path(__file__).resolve().parent


def test_v39_static_contract_and_local_forbiddance() -> None:
    report = v39.build_report()
    assert report["source_contract"]["all_static_checks_pass"]
    selector = report["V39_selector_and_necessary_anomaly_audit"]
    assert selector["all_displayed_W_terms_Z3_neutral"]
    assert selector["all_displayed_W_terms_external_Z4R_charge_two"]
    assert selector["all_four_local_sources_forbidden"]
    assert [row["Z3"] for row in selector["dangerous_local_sources"]] == [1, 2, 1, 2]


def test_minimal_selector_and_necessary_residues() -> None:
    report = v39.build_report()
    search = report["minimal_split_six_selector_search"]
    assert search["minimum_order"] == 3
    assert {row["q_Q"] for row in search["minimum_solutions"]} == {1, 2}
    selector = report["V39_selector_and_necessary_anomaly_audit"]
    assert selector["pure_Z3_Hsieh_Dai_Freed_convention"]["both_vanish"]
    assert selector["mixed_PS_Z3_standard_doubled_Dynkin"]["residues_mod_3"] == {"SU4": 0, "SU2L": 0, "SU2R": 0}
    cross = selector["necessary_Z3_Z5610_cross_residues"]
    assert cross["C_Z3_Z5610_squared_mod_3"] == 0
    assert cross["C_Z3_squared_Z5610_mod_3"] == 0


def test_unsplit_no_go_and_fail_closed_gate_status() -> None:
    report = v39.build_report()
    no_go = report["V37_unsplit_additive_selector_no_go"]
    assert "4q(Q)=4q(Qc)=0" in no_go["deduction"][2]
    g7, g8, g1 = report["gate_statuses"]
    assert not g7["full_gate_closed"]
    assert not g8["full_gate_closed"]
    assert not g1["full_gate_closed"]
    assert not report["complete_theory_exists"]


def test_explicit_degree_nine_Qc4_vev_dressing_keeps_G7_open() -> None:
    report = v39.build_report()
    witness = report["explicit_Qc4_PSVev_dressing_witness"]
    assert witness["both_selectors_allow_both_operators"] is True
    assert [row["chiral_degree"] for row in witness["operators"]] == [9, 9]
    assert [(row["Z3"], row["Z4R"], row["Z5610"], row["PQ"]) for row in witness["operators"]] == [
        (0, 2, 0, 0),
        (0, 2, 0, 0),
    ]
    assert "does not protect the full Qc^4 operator ring" in witness["conclusion"]


def test_active_V39_quality_is_freshly_enumerated_with_Z3() -> None:
    quality = v39.build_report()["canonical_branch_and_PQ_quality_scope"]["fresh_V39_charge_lattice_enumeration"]
    assert quality["superpotential"]["first_breaking_degree"] == 33
    assert quality["Kahler"]["first_breaking_degree"] == 32
    assert quality["superpotential"]["witness_multiplicities"]
    assert quality["Kahler"]["witness_multiplicities"]
    assert quality["exact_W33_K32_equalities_established"] is True
    attainment = quality["gauge_singlet_attainment_witnesses"]
    assert attainment["W_degree_33"]["multiplicities"] == {"P": 33}
    assert attainment["Kahler_degree_32"]["multiplicities"] == {
        "P": 6,
        "A32": 21,
        "A16dag": 1,
        "A17dag": 4,
    }
    assert attainment["both_are_exact_breaking_gauge_singlets"] is True


def test_written_artifacts_are_reproducible() -> None:
    subprocess.run([sys.executable, "-B", str(ROOT / "susy_v39_g7_g8_architecture.py"), "--check"], check=True, cwd=ROOT)
    payload = json.loads((ROOT / "SUSY_V39_G7_G8_ARCHITECTURE.json").read_text(encoding="utf-8"))
    assert payload["status"] == v39.STATUS
