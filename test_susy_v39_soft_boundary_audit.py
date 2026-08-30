"""Regression tests for the V39 live-soft and gaugino-boundary audit."""

from __future__ import annotations

import json
from pathlib import Path

import susy_v39_soft_boundary_audit as audit


ROOT = Path(__file__).resolve().parent


def test_analytic_gaugino_mediation_solution() -> None:
    witness = audit.one_loop_gaugino_mediation_witness()
    assert witness["one_loop_solution"]["one_loop_b_SU4_SU2L_SU2R"] == [2.0, 5.0, 9.0]
    ratios = witness["one_loop_solution"]["gaugino_mass_ratios_at_vPS"]
    assert all(0.0 < ratios[gauge] < 1.0 for gauge in audit.GAUGE_ORDER)
    assert witness["all_PS_charged_m2_positive_in_gauge_only_solution"] is True
    assert witness["all_exact_singlets_remain_unlifted_gauge_only"] is True
    assert {"X", "P", "Pbar", "Zp", "A16", "D16", "Db16"} <= set(witness["unlifted_exact_singlets"])
    assert {"SigC", "SigBc"} <= set(witness["PS_charged_fields"])


def test_live_soft_RGE_contains_every_soft_beta_class() -> None:
    data = audit.report()
    counts = data["live_soft_RGE"]["beta_counts"]
    for name in ("soft_trilinear", "soft_bilinear", "soft_linear", "soft_scalar_mass", "gaugino_mass"):
        assert counts[name] > 0
    assert data["live_soft_RGE"]["two_loop_succeeded"] is True
    assert data["live_soft_RGE"]["model"] == audit.MODEL_NAME
    assert data["live_soft_RGE"]["declared_source_two_loop_succeeded"] is True
    assert data["live_soft_RGE"]["declared_source_soft_terms_enabled"] is False


def test_no_physical_gate_is_promoted_by_a_boundary_witness() -> None:
    decisions = audit.report()["gate_decisions"]
    assert decisions["G6_calculational_scaffold_advance"] is True
    assert decisions["G2_closed"] is False
    assert decisions["G3_closed"] is False
    assert decisions["G4_closed"] is False
    assert decisions["G6_closed"] is False


def test_report_hash_and_written_certificate() -> None:
    data = audit.report()
    assert audit.canonical_sha(data) == data["core_sha256"]
    path = ROOT / "SUSY_V39_SOFT_BOUNDARY_AUDIT.json"
    if path.is_file():
        disk = json.loads(path.read_text(encoding="utf-8"))
        assert audit.canonical_sha(disk) == disk["core_sha256"]
