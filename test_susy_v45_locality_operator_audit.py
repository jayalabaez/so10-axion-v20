"""Regression tests for the reduced-core V45 locality/operator audit."""

from __future__ import annotations

import json
import subprocess
import sys

import susy_v45_locality_operator_audit as v45


REPORT = v45.build_report()


def test_authoritative_core_is_reduced_and_has_no_B_hypers() -> None:
    assert set(REPORT["field_table"]) == {
        "Q1", "Q2", "Q3", "Qc1", "Qc2", "Qc3", "H", "LF", "LA", "RA", "RF"
    }
    assert REPORT["decision"]["separate_Bplus_Bminus_singlet_hypers"].startswith("REJECTED")
    assert REPORT["rejected_redundant_B_option"]["verdict"].startswith("DO_NOT_INCLUDE")


def test_charge_orientation_identity_and_degree_frontiers() -> None:
    for row in REPORT["field_table"].values():
        assert row["u1f"] == 3 * row["s"] + 9 * row["t9"]
    frontier = REPORT["local_orientation_frontier"]
    assert frontier["first_nonzero_orientation"] == 12
    assert frontier["no_PS_U1F_invariant_through_degree"] == 19
    assert frontier["first_PS_U1F_invariant_degree"] == 20
    assert frontier["no_Z4R_superpotential_through_degree"] == 22
    assert frontier["first_Z4R_superpotential_degree"] == 23


def test_degree20_wall_witness_is_real_but_not_a_W_term() -> None:
    witnesses = REPORT["explicit_local_witnesses"]
    for key in ("degree20_plus", "degree20_minus"):
        row = witnesses[key]
        assert row["PS_U1F_invariant"]
        assert row["quantum_numbers"]["degree"] == 20
        assert abs(row["quantum_numbers"]["orientation"]) == 12
        assert row["quantum_numbers"]["r4"] == 0
        assert not row["superpotential_allowed"]


def test_first_explicit_oriented_W_witness_is_degree23() -> None:
    witnesses = REPORT["explicit_local_witnesses"]
    for key in ("degree23_plus_W", "degree23_minus_W"):
        row = witnesses[key]
        assert row["quantum_numbers"]["degree"] == 23
        assert abs(row["quantum_numbers"]["orientation"]) == 12
        assert row["quantum_numbers"]["r4"] == 2
        assert row["superpotential_allowed"]


def test_complete_renormalizable_wall_W_is_4x4_plus_mirror_yukawa() -> None:
    ring = REPORT["renormalizable_PS_wall_superpotential"]
    assert ring["count"] == 17
    assert ring["no_linear_or_quadratic_W"]
    assert all(row["quantum_numbers"]["degree"] == 3 for row in ring["operators"])
    fields = {tuple(sorted(row["fields"])) for row in ring["operators"]}
    assert tuple(sorted(("Q1", "H", "Qc1"))) in fields
    assert tuple(sorted(("Q1", "H", "RA"))) in fields
    assert tuple(sorted(("LF", "H", "Qc1"))) in fields
    assert tuple(sorted(("LF", "H", "RA"))) in fields
    assert tuple(sorted(("LA", "H", "RF"))) in fields


def test_integrated_zero_mode_anomaly_rows_cancel_but_localized_audit_is_open() -> None:
    anomaly = REPORT["integrated_anomaly_arithmetic"]
    assert anomaly["integrated_zero_mode_total"] == {
        "SU2L_squared_U1F": 0,
        "SU2R_squared_U1F": 0,
        "SU4_squared_U1F": 0,
        "gravity_U1F": 0,
        "U1F_cubic": 0,
    }
    assert anomaly["SU2_Witten_doublet_counts_including_H"] == {"SU2L": 22, "SU2R": 22}
    assert anomaly["all_displayed_integrated_rows_zero"]
    assert "parity-resolved localized" in anomaly["not_certified"]


def test_four_transmission_result_is_scoped_and_G7_remains_open() -> None:
    theorem = REPORT["restricted_four_transmission_theorem"]
    assert theorem["general_solution"] == "k=3 ell, m=-4 ell"
    assert theorem["minimum_nonzero"] == {"net_orientation": 12, "source_units": 4}
    assert "does not prove four independent factors" in theorem["important_limit"]
    assert not REPORT["decision"]["G7_closed"]


def test_audit_is_fail_closed_and_artifacts_reproduce() -> None:
    assert REPORT["decision"]["closed_gate_count"] == 0
    assert REPORT["n_failed_integrity_checks"] == 0
    assert all(REPORT["integrity_checks"].values())
    assert REPORT["core_sha256"] == v45.canonical_sha(REPORT)
    result = subprocess.run(
        [sys.executable, "-B", str(v45.ROOT / "susy_v45_locality_operator_audit.py"), "--check"],
        cwd=v45.ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "V45_LOCALITY_OPERATOR_AUDIT_CHECK_PASS" in result.stdout
    stored = json.loads(v45.JSON_PATH.read_text(encoding="utf-8"))
    assert stored["core_sha256"] == v45.canonical_sha(stored)
