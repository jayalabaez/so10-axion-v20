"""Regression tests for the fail-closed V40 non-UV completion contract."""

from __future__ import annotations

import json
from pathlib import Path

import susy_v40_nonuv_completion_contract as v40


ROOT = Path(__file__).resolve().parent


def test_v39_isolated_yukawa_mechanism_has_a_scale_no_go() -> None:
    no_go = v40.pure_yukawa_scale_no_go()
    assert no_go["V39_pole_below_fPQ"] is True
    assert no_go["fitted_lambda_exceeds_PQ_safe_bound"] is True
    assert 1.1 < no_go["lambda_D_max_without_a_pole_below_fPQ"] < 1.2
    assert no_go["maximum_proxy_annihilation_fraction_if_PQ_safe"] < 0.32
    assert no_go["minimum_proxy_Omega_h2_if_PQ_safe"] > 0.37


def test_vector_portal_has_perturbative_scale_headroom_but_is_not_a_relic_claim() -> None:
    route = v40.vector_portal_feasibility()
    screen = route["tree_level_screen"]
    assert 0.06 < screen["alpha_D_needed_in_tree_proxy"] < 0.08
    assert 0.85 < screen["g_D_needed_in_tree_proxy"] < 1.0
    assert screen["one_loop_pole_above_reduced_Planck"] is True
    assert screen["g_D_below_Planck_safe_bound"] is True
    assert "Z170 if the V39 cascade is retained" in route["candidate_structure_not_yet_a_V40_model"]["visible_remnant_requirement"]
    assert "not a derived solution" in route["feasibility_conclusion"]


def test_hidden_contract_covers_every_v39_gauge_only_singlet() -> None:
    contract = v40.hidden_mediation_contract()
    singlets = contract["V39_obstruction"]["gauge_only_boundary_left_unlifted"]
    assert len(singlets) == 16
    assert {"X", "P", "Pbar", "Zp", "A16", "D16", "Db16"} <= set(singlets)
    assert "mu and Bmu" in " ".join(contract["required_matching_equations"])
    assert "leaves G3, G4, and G6 open" in contract["fail_closed_rule"]


def test_no_gate_is_promoted_and_contract_is_reproducible() -> None:
    data = v40.report()
    decisions = data["gate_decisions"]
    assert all(decisions[f"G{gate}_closed"] is False for gate in (2, 3, 4, 5, 6, 8))
    assert decisions["complete_theory_exists"] is False
    assert v40.canonical_sha(data) == data["core_sha256"]
    path = ROOT / "SUSY_V40_NONUV_COMPLETION_CONTRACT.json"
    if path.is_file():
        disk = json.loads(path.read_text(encoding="utf-8"))
        assert v40.canonical_bytes(disk) == v40.canonical_bytes(data)
        assert v40.canonical_sha(disk) == disk["core_sha256"]
