"""Regression tests for the V41 U(1)_F-to-Z9 source-sector audit."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import susy_v41_z9_u1f_source_sector_audit as audit


ROOT = Path(__file__).resolve().parent


def test_declared_source_terms_respect_every_listed_selector() -> None:
    report = audit.build_report()
    terms = report["superpotential_charge_audit"]
    assert len(terms["rows"]) == 10
    assert terms["all_U1F_neutral"]
    assert terms["all_Z9_neutral"]
    assert terms["all_Z4R_charge_two"]
    assert terms["all_Z5610_neutral"]
    assert terms["all_PQ_neutral"]
    assert terms["all_declared_PS_invariants"]


def test_canonical_branch_is_F_D_flat_and_retains_exact_z9() -> None:
    report = audit.build_report()
    branch = report["canonical_F_D_flat_branch"]
    assert branch["branch"]["zero_F"]
    assert branch["FI_deformed_solution"]["zero_D"]
    assert branch["FI_deformed_solution"]["both_nonzero_for_finite_xi_F_and_mu_F"]
    assert branch["unbroken_gauge_subgroup"] == {
        "VEV_charges": [9, -9],
        "gcd_of_nonzero_VEV_charges": 9,
        "result": "Z9",
        "every_nonzero_branch_VEV_is_zero_mod_9": True,
    }


def test_anomalons_and_dirac_messenger_have_a_full_rank_mass_witness() -> None:
    report = audit.build_report()
    mass = report["massability_audit"]
    assert [row["rank_of_witness"] for row in mass["anomalon_thresholds"][:2]] == [4, 4]
    assert all(row["all_chiral_pairs_massable"] for row in mass["anomalon_thresholds"])
    assert mass["Higgs_stabilizer_and_vector"]["physical_massless_source_chiral_multiplet_on_canonical_branch"] is False
    assert mass["Dirac_neutrino_messenger"]["tree_level_elimination"]["effective_operator"] == "-(y1 y2/M_F) Q H Sc NDirac"
    assert mass["all_required_U1F_breaking_and_anomalon_fields_massable_on_witness"]


def test_anomaly_recheck_and_host_embedding_boundary_are_fail_closed() -> None:
    report = audit.build_report()
    anomaly = report["ordinary_anomaly_recheck"]
    assert anomaly["totals"] == {"SU4": 0, "SU2L": 0, "SU2R": 0, "gravity": 0, "cubic": 0}
    assert anomaly["all_listed_ordinary_PS_times_U1F_anomalies_cancel"]
    embedding = report["host_embedding_boundary"]
    assert embedding["all_three_signatures_identical"]
    assert all(row["allowed_by_listed_product_symmetries"] for row in embedding["representative_allowed_cross_terms"])
    assert embedding["embedding_is_complete"] is False
    assert report["decision"]["full_gate_closed"] == []


def test_write_check_round_trip() -> None:
    result = subprocess.run(
        [sys.executable, "-B", str(ROOT / "susy_v41_z9_u1f_source_sector_audit.py"), "--write", "--check"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "SUSY V41 Z9 U1F source-sector audit: PASS" in result.stdout
    payload = json.loads((ROOT / "SUSY_V41_Z9_U1F_SOURCE_SECTOR_AUDIT.json").read_text(encoding="utf-8"))
    assert payload["status"] == audit.STATUS
    assert payload["core_sha256"] == audit.canonical_sha(payload)
