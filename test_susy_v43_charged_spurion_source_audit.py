"""Regression tests for the V43 charged-spurion source boundary."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import susy_v43_charged_spurion_source_audit as audit


ROOT = Path(__file__).resolve().parent


def test_charged_spurion_replaces_only_the_naked_stheta_term() -> None:
    report = audit.build_report()
    terms = report["term_audit"]
    assert terms["source_redesign"]["removed_term"] == "-kappa mu_F^2 STheta"
    assert terms["source_redesign"]["replacement"] == "M_Omega STheta Omega"
    assert terms["all_retained_and_new_terms_allowed"]
    assert terms["all_original_U1F_Z4R_Z5610_PQ_checks_remain_true"]


def test_renormalizable_and_restricted_all_order_driver_portals_are_absent_on_branch() -> None:
    report = audit.build_report()
    cubic = report["renormalizable_source_host_portal_audit"]
    assert len(cubic["abelian_allowed_source_host_monomials"]) == 3
    assert len(cubic["source_host_rows_excluded_by_necessary_PS_singlet_filter"]) == 3
    assert cubic["potentially_PS_invariant_source_host_monomials_after_necessary_filter"] == []
    assert cubic["abelian_allowed_X_or_Zp_source_monomials"] == []
    ring = report["restricted_all_order_driver_source_ring"]
    assert ring["finite_exhaustive_crosscheck_bounds"]["counterexamples"] == []
    assert ring["all_checked_nontrivial_portals_vanish_on_F_branch"]


def test_coupled_f_branch_preserves_z9_but_zero_fi_gauged_branch_is_no_go() -> None:
    report = audit.build_report()
    f_terms = report["full_coupled_F_term_audit"]
    assert f_terms["formal_branch"]["all_source_F_terms_zero"]
    assert f_terms["formal_branch"]["all_host_F_terms_zero_given_an_F_flat_host_solution"]
    assert f_terms["anomalon_mass_witness_preserved"]["all_original_V41_anomalons_massable_when_ThetaPlus_and_ThetaMinus_are_nonzero"]
    d_terms = report["minimal_D_and_residual_audit"]
    assert not d_terms["zero_FI_D_terms"]["zero_FI_D_flat_branch_exists"]
    assert d_terms["conditional_FI_escape"]["formal_F_and_D_flat_solution_exists"]
    assert d_terms["conditional_FI_escape"]["unbroken_U1F_subgroup"] == "Z9"


def test_new_gauge_anomaly_and_neutral_compensator_boundary_fail_closed() -> None:
    report = audit.build_report()
    anomaly = report["new_U1S_anomaly_audit"]
    assert anomaly["new_U1S_rows"]["PS_squared_U1S"] == {"SU4": 0, "SU2L": 0, "SU2R": 4}
    assert anomaly["new_U1S_rows"]["gravity_U1S"] == 9
    assert anomaly["new_U1S_rows"]["U1S_cubed"] == 9
    assert anomaly["new_U1S_rows"]["U1F_squared_U1S"] == -56
    assert anomaly["new_U1S_rows"]["U1F_U1S_squared"] == -2
    assert not anomaly["all_new_U1S_local_rows_cancel"]
    recurrence = report["neutral_compensator_recurrence"]
    assert all(row["allowed"] for row in recurrence["generic_portals"])
    assert not recurrence["F_term_consequence"]["unperturbed_host_branch_is_F_flat_when_Omega_and_OmegaBar_nonzero"]
    assert report["decision"]["full_gate_closed"] == []


def test_write_check_round_trip() -> None:
    result = subprocess.run(
        [sys.executable, "-B", str(ROOT / "susy_v43_charged_spurion_source_audit.py"), "--write", "--check"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "SUSY V43 charged-spurion source audit: PASS" in result.stdout
    payload = json.loads((ROOT / "SUSY_V43_CHARGED_SPURION_SOURCE_AUDIT.json").read_text(encoding="utf-8"))
    assert payload["status"] == audit.STATUS
    assert payload["core_sha256"] == audit.canonical_sha(payload)
