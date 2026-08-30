#!/usr/bin/env python3
"""Integrate the V53 exact advances and enforce one-action theory closure.

The component V53 audits establish several strong intermediate results.  This
master audit binds their canonical cores, records what is exact, and prevents a
cross-action promotion: the elementary filter Hessian uses a P-driver that is
not invariant under the proton-safe Z9 selector candidate.  The result is a
bounded stopping theorem for the present renormalizable Abelian route, not a
claim that all possible Spin(10) model building has been exhausted.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V53_THEORY_COMPLETION_VERIFICATION_AUDIT.json"
MD_PATH = ROOT / "SUSY_V53_THEORY_COMPLETION_VERIFICATION_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v53_theory_completion_verification_audit.py"

INPUTS = {
    "v52_master": ROOT / "SUSY_V52_NEW_PHYSICS_ROUTE_INTEGRATION_AUDIT.json",
    "whole_action": ROOT / "SUSY_V53_LOW_INDEX_WHOLE_ACTION_AUDIT.json",
    "selector_no_go": ROOT / "SUSY_V53_PROTON_SAFE_SELECTOR_NO_GO_AUDIT.json",
    "natural_dt": ROOT / "SUSY_V53_NATURAL_DT_FILTER_AUDIT.json",
    "elementary_filter": ROOT / "SUSY_V53_ELEMENTARY_FILTER_HESSIAN_AUDIT.json",
    "selector_candidate": ROOT / "SUSY_V53_FILTER_SELECTOR_CANDIDATE_AUDIT.json",
    "driver_no_go": ROOT / "SUSY_V53_FILTER_DRIVER_COMPATIBILITY_NO_GO_AUDIT.json",
}

EXPECTED_CORES = {
    "v52_master": "9ffa78a63afd3ff0a1e948ff2deffc701f229c5b7cae46b354d6cf5ebecb3df8",
    "whole_action": "9218b06e866c00dcc6e3348751ace04fea2e1958cb6fe046fc5c9b912896bcb8",
    "selector_no_go": "3ad9373cb18224f72bfcedc0457378c996966cc5cbef5e4e3f4f3772e592e58b",
    "natural_dt": "e01f86a4b3a2a843d822616bd43980c8ef0c9d24ce6b41b47655d4a4a51c35b2",
    "elementary_filter": "993b549668243b06d082a7def8591c63141dfa402d6372b133c19cfa8f8b6ff6",
    "selector_candidate": "33de88b196a5096f7169cc3156d68cd9f4fa33e985adf0c23ea6c67a1a732dce",
    "driver_no_go": "3777e4ab0f03591ca736f71e282f86a8f232fee83fb2f1d378e789fea6765bf4",
}

REFEREE_FILES = [
    ROOT / "SUSY_V53_INTERMEDIATE_REFEREE.md",
    ROOT / "susy_v53_intermediate_referee_verification.py",
    ROOT / "test_susy_v53_intermediate_referee_verification.py",
]

EXPECTED_REFEREE_HASHES = {
    "SUSY_V53_INTERMEDIATE_REFEREE.md": "63c65af1c8b857eee9ed311b631c945c4fab0732161bbedf9c3f27e6922df044",
    "susy_v53_intermediate_referee_verification.py": "a91090a344a17a55a6cc3fef84852ea9bdf86da2ed2205728492add5480fa0c9",
    "test_susy_v53_intermediate_referee_verification.py": "347edc39ecbfd538c02b9ec620dfb1064c4cc21aa0e9aa626253aea4d730071a",
}

STATUS = (
    "V53_THEORY_COMPLETION_VERIFICATION__EXACT193_WHOLE_ACTION_KERNEL__"
    "EXACT176_CROSS_COUPLED_DW_SOURCE__EXACT218_ELEMENTARY_FILTER_HESSIAN__"
    "BOUNDED_Z9xZ2_SELECTOR_CANDIDATE__ELEMENTARY_DRIVER_NOT_Z9_INVARIANT__"
    "EXHAUSTIVE_SAFE_RENORMALIZABLE_DRIVER_NO_GO_THROUGH6_ADDED_SINGLETS__"
    "SAME_ACTION_COMPLETION_FALSE__G2_TO_G8_OPEN__ONLY_FROZEN_G1_RETAINED__"
    "BOUNDED_ROUTE_FINISHED__COMPLETE_THEORY_REJECTED"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def load_hashed_json(name: str, path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"missing input: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"input is not an object: {path.name}")
    actual = canonical_sha(value)
    if value.get("core_sha256") != actual:
        raise RuntimeError(f"stale canonical core: {path.name}")
    if actual != EXPECTED_CORES[name]:
        raise RuntimeError(f"unexpected upstream core: {path.name}")
    return value


def source_manifest() -> list[dict[str, Any]]:
    paths = [Path(__file__), TEST_PATH, *INPUTS.values(), *REFEREE_FILES]
    return [
        {"path": path.name, "exists": path.is_file(), "sha256": sha256_file(path)}
        for path in paths
    ]


def clause_ledger() -> list[dict[str, str]]:
    return [
        {
            "id": "C1",
            "status": "PARTIAL",
            "statement": (
                "Exact finite operator censuses and bounded selector screens exist, but no "
                "most-general selector-allowed census for one completed action exists; the "
                "Z9 candidate first leaks a dangerous class at degree eight."
            ),
        },
        {
            "id": "C2",
            "status": "PASS_LOCAL_ACTION_ONLY",
            "statement": (
                "The selector-free source plus elementary filter and driver is an explicit "
                "local renormalizable four-dimensional action."
            ),
        },
        {
            "id": "C3",
            "status": "PARTIAL",
            "statement": (
                "Its 218-coordinate holomorphic Hessian is exact, but no single Hessian also "
                "contains the Z9 selector, anomaly spectators, three families, four N fields, "
                "and a compatible full-rank driver."
            ),
        },
        {
            "id": "C4",
            "status": "PARTIAL",
            "statement": (
                "The canonical local supersymmetric vacuum and gauge kernel are exact; global, "
                "radiative, soft-term, and tunnelling stability are not established."
            ),
        },
        {
            "id": "C5",
            "status": "OPEN",
            "statement": (
                "There is no same-action one-loop matching calculation, physical threshold "
                "cancellation, or frozen EFT coefficient array."
            ),
        },
        {
            "id": "C6",
            "status": "OPEN_INCOMPATIBLE",
            "statement": (
                "The repaired Z9 selector forbids the elementary X(P^2-v^2) driver, and the "
                "safe renormalizable neutral-driver search through six added singlet VEVs is "
                "rank deficient."
            ),
        },
        {
            "id": "C7",
            "status": "OPEN",
            "statement": (
                "No same-action Wilson array, running to observables, likelihood, or withheld "
                "prediction has been constructed."
            ),
        },
    ]


def gate_ledger() -> list[dict[str, Any]]:
    return [
        {
            "gate": "G1",
            "closed": True,
            "V53_candidate_closed": False,
            "scope": "frozen ordinary-Spin topology/anomaly namespace only",
            "advance": (
                "The previously established ordinary-Spin quotient/anomaly result remains a "
                "reusable lemma."
            ),
            "blocker": (
                "It is not a reclosure for the V53 Z9 filter action and supplies no continuous "
                "parent for that selector."
            ),
        },
        {
            "gate": "G2",
            "closed": False,
            "V53_candidate_closed": False,
            "advance": (
                "V53 provides exact source, filter, selector, and no-go certificates with "
                "canonical provenance."
            ),
            "blocker": (
                "The C1-C7 conjunction fails because the exact filter Hessian and proton-safe "
                "selector do not belong to one compatible action."
            ),
        },
        {
            "gate": "G3",
            "closed": False,
            "V53_candidate_closed": False,
            "advance": (
                "The selector-free 218-coordinate action has F=D=0, rank(H)=181, nullity 37, "
                "and exactly 33 gauge plus four intended weak-Higgs zero directions."
            ),
            "blocker": (
                "The result omits the selector-compatible driver, anomaly spectators, full "
                "matter sector, SUSY breaking, and global/radiative vacuum analysis."
            ),
        },
        {
            "gate": "G4",
            "closed": False,
            "V53_candidate_closed": False,
            "advance": (
                "The elementary filter has color rank 24 and weak rank 12 with nullity four on "
                "an open set, leaving one Higgs-doublet pair without a coefficient equality."
            ),
            "blocker": (
                "Its shaping protection is incompatible with the tested Z9 driver; mu/Bmu, "
                "soft breaking, radiative EWSB, and the physical scalar spectrum are absent."
            ),
        },
        {
            "gate": "G5",
            "closed": False,
            "V53_candidate_closed": False,
            "advance": "No unsupported dark-sector or cosmological claim is made.",
            "blocker": (
                "No dark/PQ action, relic history, baryogenesis calculation, BBN/CMB test, or "
                "cosmological likelihood exists."
            ),
        },
        {
            "gate": "G6",
            "closed": False,
            "V53_candidate_closed": False,
            "advance": (
                "One-loop inventory screens are explicit: the selector-free filter has b=18 "
                "and pole ratio 3756.93; the anomaly-repaired selector candidate has b=22 and "
                "pole ratio 841.13 at g=0.73."
            ),
            "blocker": (
                "The former lacks the selector and the latter lacks a stabilized full action; "
                "two-loop running, thresholds, unification, and physical pole matching are open."
            ),
        },
        {
            "gate": "G7",
            "closed": False,
            "V53_candidate_closed": False,
            "advance": (
                "The unchanged V52 action has an exact Abelian selector no-go, and the changed "
                "Z9 candidate forbids all F16^4 dressings through total degree six."
            ),
            "blocker": (
                "The Z9 candidate exposes 72 F16^4 barC^4 invariant directions at degree eight; "
                "no mediator matching, Wilson coefficients, dressing, or decay rates exist."
            ),
        },
        {
            "gate": "G8",
            "closed": False,
            "V53_candidate_closed": False,
            "advance": (
                "Yukawa and inverse-seesaw operator classes are compatible with the bounded "
                "Z9 x exact-matter-parity charge ledger."
            ),
            "blocker": (
                "The inverse-seesaw mu parameter is not naturally small, and no selector-compatible "
                "full mass matrix, flavor fit, uncertainty propagation, or withheld prediction exists."
            ),
        },
    ]


def build_report() -> dict[str, Any]:
    data = {name: load_hashed_json(name, path) for name, path in INPUTS.items()}
    whole = data["whole_action"]
    no_go = data["selector_no_go"]
    natural = data["natural_dt"]
    elementary = data["elementary_filter"]
    selector = data["selector_candidate"]
    driver = data["driver_no_go"]

    whole_exact = whole["exact_whole_action_rank_certificate"]["declared_elementary_action"]
    census = no_go["exact_D5_invariant_census"]
    source = natural["exact_source_witness"]
    dt = natural["doublet_triplet"]
    geometry = elementary["full_same_action_geometry"]
    filter_block = elementary["filter_mass_blocks"]
    selector_census = selector["complete_F4_VEV_dressing_census_through_degree6"]
    exposed = selector["first_exposed_higher_degree_class"]
    driver_rows = driver["exhaustive_search"]["rows"]

    advances = [
        {
            "id": "A1_declared_sparse_whole_action",
            "scope": "unchanged V52 source plus matter, one H10, and four N singlets",
            "exact": True,
            "coordinates": whole_exact["coordinate_sum"],
            "H_rank": whole_exact["H_rank_mod37"],
            "H_nullity": whole_exact["H_nullity"],
            "Q_rank": whole_exact["Q_rank_mod37"],
            "kernel": whole_exact["kernel_decomposition"],
            "limitation": "tuned DT and no complete selector",
        },
        {
            "id": "A2_unchanged_action_selector_no_go",
            "scope": "declared V52 field contract through invariant degree four and ZN/ZNR through N=64",
            "exact": True,
            "invariant_multidegrees": census["total_multidegrees"],
            "invariant_directions": census["total_invariant_multiplicity"],
            "F16_power4_family_invariants": census["fatal_F4_row"]["Spin10_singlet_multiplicity"],
            "required_charge_assignments": sum(
                row["solutions_to_required_terms"]
                for row in no_go["bounded_cyclic_search"]["rows"]
            ),
            "proton_safe_assignments": len(
                no_go["bounded_cyclic_search"]["proton_safe_solutions"]
            ),
            "limitation": "no-go applies to the unchanged declared action and additive finite Abelian products",
        },
        {
            "id": "A3_cross_coupled_DW_source_and_two10_rank_split",
            "scope": "new 176-coordinate E+A+B+C+barC source, plus a separately evaluated two-10 filter",
            "exact": True,
            "source_H_rank": source["hessian_rank"],
            "source_H_nullity": source["hessian_nullity"],
            "source_Q_rank": source["orbit_rank"],
            "uncoupled_control_extra_moduli": natural["lean_uncoupled_adjoint_control"]["physical_chiral_zero_modes_beyond_gauge"],
            "two10_full_rank": dt["cartesian_rank"],
            "two10_weak_nullity": dt["weak_nullity"],
            "limitation": "the minimal Abelian selector also permits fatal H1^2 fillers",
        },
        {
            "id": "A4_elementary_filter_Hessian",
            "scope": "selector-free 176-coordinate DW source plus four 10s and P,X driver",
            "exact": True,
            "coordinates": elementary["coordinate_inventory"]["total"],
            "H_rank": geometry["hessian_rank_mod37"],
            "H_nullity": geometry["hessian_nullity"],
            "Q_rank": geometry["orbit_rank_mod37"],
            "filter_color_rank": filter_block["color_rank"],
            "filter_weak_rank": filter_block["weak_rank"],
            "filter_weak_nullity": filter_block["weak_nullity"],
            "extra_zero_modes": geometry["nullity_decomposition"]["extra"],
            "limitation": "no complete shaping selector; generic H1^2 lifts the four intended modes",
        },
        {
            "id": "A5_bounded_Z9xZ2_selector_candidate",
            "scope": "changed filter action, all F16^4 dressings with zero, one, or two declared VEV insertions",
            "exact": True,
            "smallest_modulus_through_Z32": 9,
            "screened_rows": selector_census["row_count"],
            "all_screened_forbidden": selector_census["all_forbidden"],
            "anomaly_residues_after_spectators": selector["discrete_anomaly_repair"]["total_mod9"],
            "exact_matter_parity": selector["matter_parity"]["all_declared_VEVs_even"],
            "first_exposed_degree": exposed["total_degree"],
            "first_exposed_multiplicity": exposed["Spin10_singlet_multiplicity"],
            "limitation": "Z9 is fully broken and the candidate has no compatible stabilized driver",
        },
        {
            "id": "A6_filter_driver_compatibility_no_go",
            "scope": "fixed safe Z9, neutral renormalizable drivers, zero through six added singlet VEV fields",
            "exact": True,
            "elementary_driver_invariant": driver["elementary_driver_check"]["invariant"],
            "safe_charge_multisets_by_added_fields": [
                row["safe_charge_multisets"] for row in driver_rows
            ],
            "minimum_rank_deficit_by_added_fields": [
                row["rank_deficit_at_least"] for row in driver_rows
            ],
            "renormalizable_compatible_driver_found": driver["verdict"]["renormalizable_compatible_driver_found"],
            "first_bounded_escape_degree": driver["smallest_bounded_escape"]["maximum_monomial_degree"],
            "limitation": "bounded theorem, not a no-go for non-Abelian or changed continuous symmetry architectures",
        },
    ]

    same_action = {
        "closure_rule": (
            "A gate may be promoted only when the action, selector, stabilized vacuum, Hessian, "
            "spectrum, matching, and observable map share one field and operator contract."
        ),
        "elementary_filter_core": EXPECTED_CORES["elementary_filter"],
        "selector_candidate_core": EXPECTED_CORES["selector_candidate"],
        "driver_compatibility_core": EXPECTED_CORES["driver_no_go"],
        "elementary_driver": "X(P^2-v^2)",
        "Z9_charge_of_P_squared": driver["elementary_driver_check"]["P2_charge"],
        "elementary_driver_Z9_invariant": driver["elementary_driver_check"]["invariant"],
        "safe_full_rank_renormalizable_driver_found_through_six_added_singlets": driver["verdict"]["renormalizable_compatible_driver_found"],
        "same_action_filter_Hessian_and_selector_certificate": False,
        "cross_action_gate_promotion_permitted": False,
        "decision": (
            "The exact 218-coordinate Hessian cannot be inherited by the Z9 selector candidate; "
            "there is no verified completed V53 action."
        ),
    }

    perturbativity = [
        {
            "action": "V52 sparse whole action",
            "b_Landau": whole["perturbativity"]["elementary_whole_action"]["b_Landau"],
            "pole_over_matching": whole["perturbativity"]["elementary_whole_action"]["pole_over_matching_scale"],
            "passes_100x": True,
            "passes_1000x": True,
            "scope": "tuned DT; no selector completion",
        },
        {
            "action": "cross-coupled DW plus two 10s and matter",
            "b_Landau": natural["perturbativity"]["one_loop_b"],
            "pole_over_matching": natural["perturbativity"]["formal_pole_over_matching_at_g_0p73"],
            "passes_100x": natural["perturbativity"]["above_100x"],
            "passes_1000x": natural["perturbativity"]["above_1000x"],
            "scope": "filter completion absent",
        },
        {
            "action": "selector-free elementary four-10 filter",
            "b_Landau": elementary["perturbativity"]["one_loop_b"],
            "pole_over_matching": elementary["perturbativity"]["formal_pole_over_matching_at_g_0p73"],
            "passes_100x": elementary["perturbativity"]["above_100x"],
            "passes_1000x": elementary["perturbativity"]["above_1000x"],
            "scope": "exact Hessian; shaping selector absent",
        },
        {
            "action": "anomaly-repaired Z9 selector inventory",
            "b_Landau": selector["perturbativity"]["b_Landau"],
            "pole_over_matching": selector["perturbativity"]["pole_over_matching_scale_at_g0p73"],
            "passes_100x": True,
            "passes_1000x": False,
            "scope": "selector candidate; stabilized compatible driver absent",
        },
    ]

    clauses = clause_ledger()
    gates = gate_ledger()
    stopping = {
        "bounded_route": (
            "low-index elementary Spin(10), additive finite Abelian shaping, fixed safe Z9 "
            "candidate, neutral polynomial drivers of degree at most three, and at most six "
            "added nonzero singlet VEV fields"
        ),
        "route_exhausted": True,
        "theorem": (
            "Every enumerated proton-safe renormalizable neutral-driver sector has exponent-"
            "Jacobian rank at least one below the number of nonzero VEV variables, so its "
            "holomorphic driver Hessian retains a modulus."
        ),
        "not_claimed": (
            "This is not a theorem against all Spin(10) theories, non-Abelian shaping groups, "
            "charged continuous parents, or explicit nonrenormalizable UV completions."
        ),
        "smallest_bounded_algebraic_escape": {
            "driver_degree": driver["smallest_bounded_escape"]["maximum_monomial_degree"],
            "added_Z9_charges": driver["smallest_bounded_escape"]["added_charges"],
            "status": "nonrenormalizable and therefore a new action requiring explicit UV matching",
        },
        "honest_next_architectures": [
            {
                "id": "N1_nonAbelian_or_continuous_parent",
                "task": (
                    "Design the selector and P-breaking driver simultaneously using a non-Abelian "
                    "filter symmetry or a charged continuous parent."
                ),
                "kill_test": (
                    "Reject unless every required term, anomaly, F/D equation, gauge orbit, full "
                    "Hessian, and dangerous operator class is recomputed in one action."
                ),
            },
            {
                "id": "N2_degree5_UV_completion",
                "task": (
                    "UV-complete the first degree-five driver escape with explicit mediators and "
                    "derive the low-energy operator rather than inserting it by hand."
                ),
                "kill_test": (
                    "Reject if mediator-induced operators restore F16^4 dressings, leave moduli, or "
                    "push the one-loop pole below the declared validity window."
                ),
            },
            {
                "id": "N3_anomalous_U1A_missing_VEV_branch",
                "task": (
                    "Rebuild the published anomalous-U1A/FI missing-VEV route as a complete explicit "
                    "action with a repository-executable Hessian and matching calculation."
                ),
                "kill_test": (
                    "Do not import literature ranks; require a frozen regulator, Green-Schwarz or "
                    "Stueckelberg completion, full operator census, thresholds, and proton amplitudes."
                ),
            },
        ],
    }

    final_decision = {
        "bounded_V53_analysis_finished": True,
        "complete_theory": False,
        "empirical_new_physics_discovery": False,
        "same_action_completion": False,
        "selected_complete_candidate": None,
        "V53_candidate_closed_gates": [],
        "cumulative_reusable_closed_gates": ["G1"],
        "full_gates_closed_for_V53_candidate": 0,
        "G2_closed": False,
        "statement": (
            "V53 is complete as a bounded exact audit: it validates real intermediate source and "
            "filter Hessians and proves why they cannot be combined with the tested selector. "
            "It does not furnish a complete or experimentally validated theory."
        ),
    }

    integrity = {
        "all_input_cores_are_canonical_and_expected": all(
            data[name]["core_sha256"] == EXPECTED_CORES[name] for name in INPUTS
        ),
        "scoped_intermediate_referee_files_are_bound": all(
            path.is_file()
            and sha256_file(path) == EXPECTED_REFEREE_HASHES[path.name]
            for path in REFEREE_FILES
        ),
        "whole_action_193_rank_nullity_closes": (
            whole_exact["coordinate_sum"] == 193
            and whole_exact["H_rank_mod37"] + whole_exact["H_nullity"] == 193
            and whole_exact["Q_plus_K_rank_mod37"] == whole_exact["H_nullity"]
            and whole_exact["HQ_exact_zero"]
            and whole_exact["HK_exact_zero"]
        ),
        "unchanged_action_F4_no_go_is_exact": (
            census["total_multidegrees"] == 66
            and census["total_invariant_multiplicity"] == 365
            and census["fatal_F4_row"]["Spin10_singlet_multiplicity"] == 6
            and not no_go["bounded_cyclic_search"]["proton_safe_solutions"]
        ),
        "cross_coupled_DW_source_kernel_is_gauge": (
            source["source_coordinates"] == 176
            and source["hessian_rank"] == 143
            and source["hessian_nullity"] == 33
            and source["orbit_rank"] == 33
            and source["kernel_equals_broken_gauge_orbit"]
        ),
        "two10_DT_rank_split_is_exact_but_unprotected": (
            dt["cartesian_rank"] == 16
            and dt["color_rank"] == 12
            and dt["weak_rank"] == 4
            and dt["weak_nullity"] == 4
            and dt["generic_allowed_H1_squared_lifts_all"]
        ),
        "elementary_filter_218_kernel_is_gauge_plus_one_pair": (
            geometry["hessian_rank_mod37"] + geometry["hessian_nullity"] == 218
            and geometry["nullity_decomposition"]
            == {"broken_gauge_orbit": 33, "intended_weak_Higgs": 4, "extra": 0}
            and geometry["ward_product_exactly_zero"]
        ),
        "selector_candidate_is_bounded_and_anomaly_repaired": (
            selector_census["row_count"] == 28
            and selector_census["all_forbidden"]
            and all(value == 0 for value in selector["discrete_anomaly_repair"]["total_mod9"].values())
            and exposed["total_degree"] == 8
            and exposed["Spin10_singlet_multiplicity"] == 72
        ),
        "elementary_driver_is_not_Z9_invariant": (
            driver["elementary_driver_check"]["P2_charge"] == 4
            and not driver["elementary_driver_check"]["invariant"]
        ),
        "safe_renormalizable_driver_search_has_rank_deficit": (
            [row["safe_charge_multisets"] for row in driver_rows]
            == [1, 4, 10, 20, 35, 56, 84]
            and all(
                row["maximum_exact_Jacobian_rank"] < row["VEV_variables"]
                for row in driver_rows
            )
        ),
        "same_action_promotion_is_forbidden": (
            not same_action["same_action_filter_Hessian_and_selector_certificate"]
            and not same_action["cross_action_gate_promotion_permitted"]
        ),
        "C1_C7_conjunction_fails": any(row["status"] != "PASS" for row in clauses),
        "only_frozen_G1_is_cumulatively_closed": (
            [row["gate"] for row in gates if row["closed"]] == ["G1"]
            and not any(row["V53_candidate_closed"] for row in gates)
        ),
        "complete_theory_is_not_claimed": not final_decision["complete_theory"],
    }

    report: dict[str, Any] = {
        "schema": "susy-v53-theory-completion-verification-audit-v1",
        "status": STATUS,
        "input_core_hashes": EXPECTED_CORES,
        "source_manifest": source_manifest(),
        "exact_advance_ledger": advances,
        "same_action_compatibility": same_action,
        "V53_candidate_clause_ledger": clauses,
        "gate_ledger_scope": (
            "Closed flags are cumulative reusable results in their frozen namespace. "
            "V53_candidate_closed is the same-action closure flag for this construction."
        ),
        "gate_ledger": gates,
        "perturbativity_route_comparison": perturbativity,
        "bounded_stopping_theorem": stopping,
        "independent_intermediate_referee": {
            "scope": (
                "cross-coupled natural-DT source, its two-10 rank split, and the unchanged-action "
                "selector no-go; it predates and does not independently certify the later Z9 "
                "candidate, driver no-go, or this master integration"
            ),
            "status": "APPROVE_SCOPED_INTERMEDIATE_RESULTS__REJECT_THEORY_OR_G2_PROMOTION",
            "exact_checks": 20,
            "files": [path.name for path in REFEREE_FILES],
            "expected_sha256": EXPECTED_REFEREE_HASHES,
        },
        "primary_sources": [
            {
                "title": "A Renormalizable Supersymmetric SO(10) Model with Natural Doublet-Triplet Splitting",
                "url": "https://arxiv.org/abs/1410.5625",
                "scope": "published filter architecture; V53 ranks are independently recomputed",
            },
            {
                "title": "Stabilizing the Doublet-Triplet Splitting in SO(10)",
                "url": "https://arxiv.org/abs/1003.2625",
                "scope": "alternative anomalous-U1A missing-VEV architecture, not imported as a V53 certificate",
            },
            {
                "title": "A New Doublet-Triplet Splitting Mechanism for Supersymmetric SO(10)",
                "url": "https://arxiv.org/abs/hep-ph/9810315",
                "scope": "complementary missing-VEV/filter construction",
            },
            {
                "title": "Note on Discrete Gauge Anomalies",
                "url": "https://arxiv.org/abs/hep-th/9109045",
                "scope": "discrete anomaly constraints and instanton-invariance criterion",
            },
        ],
        "final_decision": final_decision,
        "integrity_checks": integrity,
        "n_failed_integrity_checks": sum(not value for value in integrity.values()),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report["status"] != STATUS:
        raise RuntimeError("status drift")
    if report["core_sha256"] != canonical_sha(report):
        raise RuntimeError("canonical core drift")
    if report["n_failed_integrity_checks"] or not all(report["integrity_checks"].values()):
        raise RuntimeError("integrity failure")
    decision = report["final_decision"]
    if decision["complete_theory"] or decision["same_action_completion"] or decision["G2_closed"]:
        raise RuntimeError("theory overpromotion")
    if decision["V53_candidate_closed_gates"]:
        raise RuntimeError("candidate gate overpromotion")
    if report["same_action_compatibility"]["cross_action_gate_promotion_permitted"]:
        raise RuntimeError("cross-action promotion")


def render_markdown(report: Mapping[str, Any]) -> str:
    exact = {row["id"]: row for row in report["exact_advance_ledger"]}
    same = report["same_action_compatibility"]
    stop = report["bounded_stopping_theorem"]
    lines = [
        "# V53 theory completion verification audit",
        "",
        f"Status: `{report['status']}`",
        "",
        f"Core SHA-256: `{report['core_sha256']}`",
        "",
        "## Outcome",
        "",
        report["final_decision"]["statement"],
        "",
        "No complete V53 candidate closes any of G1-G8. The historical ordinary-Spin G1 "
        "result remains reusable only in its frozen namespace; G2-G8 remain open.",
        "",
        "## What is exact",
        "",
        (
            f"- The declared 193-coordinate sparse whole action has rank "
            f"{exact['A1_declared_sparse_whole_action']['H_rank']} and nullity "
            f"{exact['A1_declared_sparse_whole_action']['H_nullity']}; its kernel is exactly "
            "33 gauge, 45 light-matter, and four weak-Higgs directions."
        ),
        (
            "- The changed 176-coordinate cross-coupled missing-VEV source has rank 143, "
            "nullity 33, and kernel equal to the broken gauge orbit."
        ),
        (
            "- The selector-free 218-coordinate elementary filter action has rank 181, "
            "nullity 37 = 33 gauge + four weak-Higgs directions, color rank 24, and no "
            "unintended local chiral modulus."
        ),
        (
            "- The anomaly-repaired Z9 x exact Z2 matter-parity candidate forbids direct "
            "F16^4 and all zero/one/two-VEV dressings through degree six; its first exposed "
            "exact class is degree eight with multiplicity 72."
        ),
        "",
        "## Decisive same-action obstruction",
        "",
        (
            f"The exact filter Hessian uses `{same['elementary_driver']}`, but "
            f"`q(P^2)={same['Z9_charge_of_P_squared']} mod 9`; the driver is not Z9 invariant. "
            "An exhaustive safe renormalizable neutral-driver search with zero through six "
            "added singlet VEVs always has rank deficit at least one. Therefore the Hessian "
            "cannot be inherited by the selector candidate."
        ),
        "",
        "## Gate verdict",
        "",
    ]
    for row in report["gate_ledger"]:
        state = "CLOSED (frozen prior namespace)" if row["gate"] == "G1" else "OPEN"
        lines.append(f"- **{row['gate']} — {state}.** {row['blocker']}")
    lines += [
        "",
        "## Bounded stopping theorem",
        "",
        stop["theorem"],
        "",
        stop["not_claimed"],
        "",
        (
            "The first bounded algebraic escape uses a degree-five driver with added Z9 "
            f"charges {stop['smallest_bounded_algebraic_escape']['added_Z9_charges']}. It is "
            "nonrenormalizable and must be treated as a new action with explicit UV mediators "
            "and matching."
        ),
        "",
        "## Honest next architectures",
        "",
    ]
    for row in stop["honest_next_architectures"]:
        lines.append(f"- **{row['id']}**: {row['task']} Kill test: {row['kill_test']}")
    lines += [
        "",
        "## Scope",
        "",
        (
            "The repository certificates establish mathematical properties of explicitly "
            "declared supersymmetric actions and bounded searches. They are not experimental "
            "evidence for new physics, a precision phenomenological fit, or a complete theory."
        ),
        "",
    ]
    return "\n".join(lines)


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    validate(report)
    JSON_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> None:
    report = build_report()
    validate(report)
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if JSON_PATH.read_text(encoding="utf-8") != expected_json:
        raise RuntimeError("stale JSON")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("stale Markdown")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        report = write_artifacts()
        print(report["status"])
        print(report["core_sha256"])
    if args.check:
        check_artifacts()
        print("V53_THEORY_COMPLETION_VERIFICATION_AUDIT_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
