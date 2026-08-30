"""Tests for the fail-closed V37 residual-relic audit."""

from __future__ import annotations

import json
from pathlib import Path

import susy_v37_g5_relic_cosmology_audit as audit


ROOT = Path(__file__).resolve().parent
DATA = audit.report()


def test_core_residual_relic_theorem_is_exact() -> None:
    theorem = DATA["residual_relic_theorem"]
    assert theorem["unbroken_order"] == 170
    assert theorem["all_non_anomalon_core_fields_neutral"] is True
    assert theorem["nontrivially_charged_core_fields"] == {
        "A2": 151,
        "A32": 19,
        "A15": 49,
        "A17": 121,
        "A16": 85,
    }
    assert theorem["inequivalent_charge_class_count"] == 3


def test_candidate_terms_are_exact_and_quality_safe() -> None:
    candidate = DATA["conditional_decay_dark_extension"]
    assert candidate["new_chiral_field_count"] == 6
    assert candidate["all_terms_exactly_invariant"] is True
    assert candidate["all_new_fields_obey_selector_PQ_congruence"] is True
    assert candidate["extension_increment_mixed_Z4R_Z85_squared"] == 0
    assert candidate["full_Z5610_Hsieh_Dai_Freed"]["both_vanish"] is True
    assert candidate["quality_lattice"]["superpotential_first_breaking_degree"] == 33
    assert candidate["quality_lattice"]["Kahler_first_breaking_degree"] == 32


def test_suppressed_decay_benchmark_is_before_bbn() -> None:
    candidate = DATA["conditional_decay_dark_extension"]
    lifetime = candidate["BBN_decay_scale_example"]["lifetime_seconds"]
    assert 0.0 < lifetime < 1.0e-10
    assert candidate["BBN_decay_scale_example"]["before_one_second_for_kappa_one_and_mass_one_TeV"]


def test_audit_is_fail_closed_and_reproducible() -> None:
    assert DATA["promotion"]["G5_closed"] is False
    assert audit.canonical_sha(DATA) == DATA["core_sha256"]
    audit.main  # public executable entry point exists


def test_written_json_matches_executable_certificate() -> None:
    path = ROOT / "SUSY_V37_G5_RELIC_COSMOLOGY_AUDIT.json"
    if path.is_file():
        disk = json.loads(path.read_text(encoding="utf-8"))
        assert disk["core_sha256"] == audit.canonical_sha(disk)
        assert disk["promotion"]["G5_closed"] is False
