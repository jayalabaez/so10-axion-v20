#!/usr/bin/env python3
"""V59 master audit for the three microscopic G1 frontier routes.

This certificate binds the canonical V58 heterotic near-match and the three
independent V59 route audits:

* route A: corrected heterotic Z4R data sufficiency,
* route B: Spin(11) gauge-Higgs completion,
* route C: gauged-U(1)R fixed-point/local-GS completion.

The inputs describe different actions or different completion questions.  A
pass in one row therefore cannot repair a failure in another row.  The master
is deliberately fail-closed: no route supplies one same-action microscopic G1
completion, all G1--G8 gates remain open, and a future live Orbifolder
regeneration may supersede only route A's present data-sufficiency row after a
new canonical certificate is produced.

Nothing in this file is an empirical discovery or a completed theory.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V59_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
MD_PATH = ROOT / "SUSY_V59_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v59_multipath_g1_frontier_master_audit.py"

INPUTS = {
    "v58_baseline": ROOT / "SUSY_V58_HETEROTIC_G1_MICROSCOPIC_COMPLETION_AUDIT.json",
    "route_a_heterotic": ROOT / "susy_v59_heterotic_corrected_z4r_data_sufficiency_audit.json",
    "route_b_spin11": ROOT / "SUSY_V59_SPIN11_GAUGE_HIGGS_COMPLETION_AUDIT.json",
    "route_c_gauged_u1r": ROOT / "SUSY_V59_GAUGED_U1R_LOCAL_COMPLETION_AUDIT.json",
}

EXPECTED_CORES = {
    "v58_baseline": "c31d5fe65fc5bd96279bb739f5284854a624b2ee1586004c9b84998225d382c6",
    "route_a_heterotic": "38747dee7e8bafdae38ddea1408c8163d625ff6cb836aaa97304f4479624250b",
    "route_b_spin11": "bf666eb5e4d57bff18b05182d7d6cc7874bbc26dd71897153faf9ee67a5f8c42",
    "route_c_gauged_u1r": "27b4e032ff10065b534c1c62c2adf88f677b07c228f243b5376227fdb307ac8d",
}

STATUS = (
    "V59_MULTIPATH_G1_FRONTIER_MASTER__V58_BASELINE_AND_THREE_V59_ROUTE_"
    "CORES_BOUND__HETEROTIC_ROUTE_IS_SOURCE_DATA_FRONTIER_NOT_PHYSICAL_NO_"
    "GO__SPIN11_ROUTE_HAS_EXACT_TWO_WEAK_ZERO_MODES_AND_SHARP_ABELIAN_"
    "SELECTOR_NO_GO__GAUGED_U1R_ROUTE_HAS_CONSTRUCTIVE_270_SINGLET_PARITIES_"
    "AND_EXACT_EXISTING_LOCAL_GS_REJECTION__NO_SAME_ACTION_G1_COMPLETION__"
    "NO_CROSS_ROUTE_SPLICING__LIVE_ORBIFOLDER_REGENERATION_MAY_SUPERSEDE_"
    "ROUTE_A_ROW__G1_TO_G8_OPEN__COMPLETE_THEORY_FALSE"
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


def load_bound(name: str) -> dict[str, Any]:
    path = INPUTS[name]
    if not path.is_file():
        raise RuntimeError(f"missing V59 master input: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    actual = canonical_sha(value)
    if value.get("core_sha256") != actual:
        raise RuntimeError(f"stale canonical core: {path.name}")
    if actual != EXPECTED_CORES[name]:
        raise RuntimeError(f"unexpected upstream core: {path.name}")
    return value


def all_gates_open(value: Mapping[str, Any]) -> bool:
    ledger = value.get("gate_ledger", [])
    return (
        len(ledger) == 8
        and {row.get("gate") for row in ledger} == {f"G{i}" for i in range(1, 9)}
        and all(row.get("status") == "OPEN" for row in ledger)
    )


def route_a_row(value: Mapping[str, Any]) -> dict[str, Any]:
    theorem = value["data_sufficiency_theorem"]
    witness = value["exact_ambiguity_witness"]
    old = value["exact_published_scope_derivations"]
    terminal = value["terminal_decision"]
    return {
        "route_id": "A",
        "name": "corrected heterotic Z4R worldsheet route",
        "bound_core_sha256": value["core_sha256"],
        "classification": "SOURCE_DATA_FRONTIER__NOT_A_PHYSICAL_NO_GO",
        "tested_object": (
            "whether the published V58 macrostate ledger alone determines the "
            "corrected gamma-sensitive charges and complete anomaly/GS ledger"
        ),
        "exact_gains": [
            {
                "claim": "the old visible non-Abelian residues are reproduced exactly",
                "certificate": {
                    "A_SU3": old["A_SU3_signed"],
                    "A_SU2": old["A_SU2_signed"],
                    "eta": old["eta_for_Z4R"],
                    "universal_mod_eta": old["visible_nonabelian_universal_mod_eta"],
                },
                "scope": old["scope"],
            },
            {
                "claim": "the published table is proven insufficient for corrected charges",
                "certificate": {
                    "equation": theorem["equation"],
                    "published_table_determines_corrected_charges": theorem[
                        "published_table_alone_determines_corrected_charges"
                    ],
                    "published_table_determines_full_anomalies": theorem[
                        "published_table_alone_determines_full_anomaly_rows"
                    ],
                },
            },
            {
                "claim": "an exact information-loss witness changes a mixed anomaly residue",
                "certificate": {
                    "gamma_pair": [
                        witness["completion_A_gamma"],
                        witness["completion_B_gamma"],
                    ],
                    "charge_difference_mod_4": witness["charge_difference"],
                    "SU2_anomaly_difference_mod_2": witness[
                        "SU2_mixed_anomaly_difference"
                    ],
                    "purpose": witness["purpose"],
                },
            },
        ],
        "blocking_certificate": {
            "type": "PUBLISHED_SOURCE_NON_IDENTIFIABILITY",
            "equation": theorem["equation"],
            "missing_microdata": theorem["missing_required_data"],
            "physical_Z4R_no_go": theorem["physical_no_go_for_Z4R"],
            "scope_boundary": theorem["scope_boundary"],
        },
        "same_action_microscopic_completion": terminal["V59_G1_closed"],
        "G1_closed": terminal["V59_G1_closed"],
        "closed_gates": terminal["closed_gates"],
        "requires_new_worldsheet_or_Orbifolder_calculation": terminal[
            "requires_new_worldsheet_or_Orbifolder_calculation"
        ],
        "supersedable_by_live_regeneration": True,
        "gate_ledger_all_open": all_gates_open(value),
    }


def route_b_row(value: Mapping[str, Any]) -> dict[str, Any]:
    zero = value["gauge_and_zero_mode_audit"]
    rank = value["rank_breaking_sector"]
    selector = value["proton_selector_obstruction"]
    mediator = value["bulk_mediator_and_nonlocal_Yukawa"]
    anomalies = value["local_global_and_Dai_Freed_anomalies"]
    terminal = value["terminal_decision"]
    return {
        "route_id": "B",
        "name": "Spin(11) gauge-Higgs route",
        "bound_core_sha256": value["core_sha256"],
        "classification": "MATHEMATICAL_CANDIDATE_WITH_SCOPED_SELECTOR_NO_GO",
        "tested_object": (
            "a 5D supersymmetric Spin(11) interval skeleton with local Spin(10) "
            "families, gauge-Higgs weak modes, rank breaking, and mirror mediators"
        ),
        "exact_gains": [
            {
                "claim": "the interval projector leaves only the desired weak chirals",
                "certificate": {
                    "weak_chiral_zero_modes": zero["weak_chiral_zero_modes"],
                    "colored_chiral_zero_modes": zero["colored_chiral_zero_modes"],
                    "Sigma_zero_component_count": zero["Sigma_zero_component_count"],
                    "SM_decomposition": zero["SM_decomposition"],
                },
            },
            {
                "claim": "the displayed rank-breaking five plus fivebar block is full rank",
                "certificate": {
                    "superpotential": rank["superpotential"],
                    "determinant": rank["five_mass_determinant"],
                    "normalized_example_determinant": rank[
                        "normalized_example_determinant"
                    ],
                    "new_light_colored_states": rank[
                        "new_light_colored_states_after_generic_rank_breaking"
                    ],
                },
            },
            {
                "claim": "a gauge-covariant nonlocal Yukawa kernel is defined",
                "certificate": {
                    "kernel": mediator["gauge_covariant_kernel"],
                    "full_realistic_yukawa_sector_closed": mediator[
                        "full_realistic_yukawa_sector_closed"
                    ],
                },
            },
        ],
        "blocking_certificate": {
            "type": "ABELIAN_NON_R_PROTON_SELECTOR_NO_GO_IN_STATED_CLASS",
            "scope": selector["theorem_scope"],
            "proof": selector["proof"],
            "finite_scan": selector["finite_scan"],
            "loopholes_not_excluded": selector["loopholes_not_excluded"],
            "additional_open_obligations": {
                "full_realistic_yukawas": mediator[
                    "full_realistic_yukawa_sector_closed"
                ],
                "Dai_Freed_status": anomalies["Dai_Freed"]["strict_status"],
                "full_quantum_anomaly_trivialization": anomalies[
                    "full_quantum_anomaly_trivialization_closed"
                ],
                "UV_regulator": "NOT_EXHIBITED",
            },
        },
        "same_action_microscopic_completion": terminal[
            "one_action_candidate_accepted"
        ],
        "G1_closed": terminal["V59_G1_closed"],
        "closed_gates": terminal["V59_closed_gates"],
        "sharp_obstruction_proved": terminal["sharp_obstruction_proved"],
        "supersedable_by_live_regeneration": False,
        "gate_ledger_all_open": all_gates_open(value),
    }


def route_c_row(value: Mapping[str, Any]) -> dict[str, Any]:
    seed = value["integrated_u1r_seed"]
    singlets = value["singlet_parity_solution"]
    mixed = value["fixed_point_mixed_U1R_gauge_anomaly_ledger"]
    obligations = value["localized_GS_and_global_obligations"]
    decision = value["strict_decision"]
    failed = [
        row["fixed_point"]
        for row in mixed
        if not row["lies_in_existing_bulk_GS_direction"]
    ]
    return {
        "route_id": "C",
        "name": "gauged-U(1)R to Z4R local-orbifold route",
        "bound_core_sha256": value["core_sha256"],
        "classification": "INTEGRATED_BULK_ADVANCE_WITH_EXACT_EXISTING_LOCAL_GS_REJECTION",
        "tested_object": (
            "the exact integrated Spin(10) x U(1)R seed on the V56 four-fixed-point "
            "projector using only the existing bulk Spin(10) GS direction"
        ),
        "exact_gains": [
            {
                "claim": "the integrated six-dimensional seed factorizes on an integral unimodular lattice",
                "certificate": {
                    "T": seed["spectrum"]["T"],
                    "V": seed["spectrum"]["V"],
                    "H": seed["spectrum"]["H"],
                    "H_minus_V_plus_29T": seed["spectrum"][
                        "H_minus_V_plus_29T"
                    ],
                    "factorization_exact": seed["anomaly_polynomial"][
                        "factorization_exact"
                    ],
                    "integral_unimodular": seed["string_charge_lattice"][
                        "integral_unimodular"
                    ],
                },
            },
            {
                "claim": "all singlet hypermultiplet parities have a constructive VEV-compatible solution",
                "certificate": {
                    "all_270_singlets_assigned": singlets[
                        "all_270_singlets_assigned"
                    ],
                    "q0_global_zero_modes": singlets["q0_global_zero_mode_count"],
                    "q4_global_zero_modes": singlets["q4_global_zero_mode_count"],
                    "local_parity_moments": singlets["local_parity_moments"],
                },
            },
            {
                "claim": "fixed-point proportionality is tested with exact two-by-two minors",
                "certificate": {
                    row["fixed_point"]: {
                        "local": row["local_mixed_anomaly_coefficients"],
                        "bulk_direction": row[
                            "bulk_tr10_restriction_coefficients"
                        ],
                        "minors": row["two_by_two_minors"],
                    }
                    for row in mixed
                },
            },
        ],
        "blocking_certificate": {
            "type": "EXISTING_BULK_GS_DIRECTION_REJECTED_AT_THREE_FIXED_POINTS",
            "failed_fixed_points": failed,
            "passes_all_four": obligations["standard_bulk_tensor_inflow_test"][
                "passes_all_four"
            ],
            "principle": obligations["standard_bulk_tensor_inflow_test"][
                "principle"
            ],
            "open_data_deficits": {
                "normal_bundle": obligations["normal_bundle_local_lorentz"][
                    "status"
                ],
                "self_dual_strings": obligations["self_dual_strings"]["status"],
                "faithful_residual_Z4R": value[
                    "residual_Z4R_normalization_audit"
                ]["faithful_residual_Z4R_proved"],
            },
        },
        "same_action_microscopic_completion": decision[
            "same_action_microscopic_completion"
        ],
        "G1_closed": decision["V59_G1_closed"],
        "closed_gates": decision["closed_gates"],
        "singlet_parity_problem_solved": decision[
            "singlet_parity_problem_solved"
        ],
        "supersedable_by_live_regeneration": False,
        "gate_ledger_all_open": all_gates_open(value),
    }


def gate_ledger(v58: Mapping[str, Any]) -> list[dict[str, Any]]:
    baseline = {row["gate"]: row for row in v58["gate_ledger"]}
    g1_reason = (
        "OPEN: none of the three canonical V59 routes supplies one same-action "
        "microscopic completion. Route A needs regenerated statewise CFT data; route "
        "B fails its commuting Abelian non-R selector class and has Dai--Freed/UV "
        "obligations; route C fails the existing local GS direction at three points."
    )
    rows = []
    for index in range(1, 9):
        gate = f"G{index}"
        reason = g1_reason if gate == "G1" else (
            f"OPEN: no V59 route proves {gate} in the same action; the bound V58 "
            f"baseline remains: {baseline[gate]['decision']}"
        )
        rows.append(
            {
                "gate": gate,
                "status": "OPEN",
                "V59_master_closed": False,
                "decision": reason,
                "cross_route_aggregation_used": False,
            }
        )
    return rows


def source_manifest() -> list[dict[str, Any]]:
    return [
        {"path": path.name, "exists": path.is_file(), "sha256": sha256_file(path)}
        for path in (Path(__file__), TEST_PATH, *INPUTS.values())
    ]


def build_report() -> dict[str, Any]:
    v58 = load_bound("v58_baseline")
    route_a = load_bound("route_a_heterotic")
    route_b = load_bound("route_b_spin11")
    route_c = load_bound("route_c_gauged_u1r")

    routes = [route_a_row(route_a), route_b_row(route_b), route_c_row(route_c)]
    gates = gate_ledger(v58)

    extension = {
        "id": "LIVE_ORBIFOLDER_CORRECTED_CHARGE_REGENERATION",
        "state": "AWAITING_EXTERNAL_REGENERATION",
        "current_route_id": "A",
        "current_bound_route_core": route_a["core_sha256"],
        "current_row_is_supersedable": True,
        "why": (
            "route A proves only non-identifiability from the published macrostate "
            "projection; it does not prove a physical no-go for the exact CFT"
        ),
        "minimum_replacement_payload": route_a[
            "minimum_new_calculation_payload"
        ],
        "replacement_contract": [
            "write a distinct canonical route artifact rather than mutating this master or the bound route file",
            "bind statewise constructing elements, p_sh, q_sh, oscillators, twist-field eigenvectors and gamma_h",
            "map corrected charges one-to-one to the post-VEV physical massless basis",
            "include the normalized U(1) metric, all visible/hidden/gravitational anomaly rows, and GS/axion/local data",
            "replace EXPECTED_CORES['route_a_heterotic'] only after canonical validation and focused tests",
        ],
        "supersession_semantics": {
            "supersedes_only": "route A data-sufficiency row",
            "does_not_retroactively_close_G1": True,
            "does_not_change_route_B_or_C_certificates": True,
            "new_same_action_proof_required": (
                "corrected Z4R plus complete anomaly/GS trivialization plus a controlled "
                "vacuum in the regenerated heterotic action"
            ),
        },
    }

    no_same_action_pass = all(
        not row["same_action_microscopic_completion"] for row in routes
    )
    no_gate_promotion = all(
        row["status"] == "OPEN" and not row["V59_master_closed"] for row in gates
    )

    integrity = {
        "all_four_input_cores_are_canonical_and_expected": True,
        "V58_baseline_has_zero_closed_gates": (
            v58["terminal_decision"]["V58_closed_gates"] == []
            and all_gates_open(v58)
        ),
        "all_three_route_ledgers_are_open": all(
            row["gate_ledger_all_open"] for row in routes
        ),
        "route_A_is_not_misreported_as_a_physical_no_go": (
            not routes[0]["blocking_certificate"]["physical_Z4R_no_go"]
            and routes[0]["requires_new_worldsheet_or_Orbifolder_calculation"]
        ),
        "route_A_ambiguity_witness_is_bound": (
            routes[0]["exact_gains"][2]["certificate"][
                "charge_difference_mod_4"
            ]
            == "2"
            and routes[0]["exact_gains"][2]["certificate"][
                "SU2_anomaly_difference_mod_2"
            ]
            == "1"
        ),
        "route_B_projector_and_rank_determinant_are_bound": (
            routes[1]["exact_gains"][0]["certificate"][
                "weak_chiral_zero_modes"
            ]
            == 2
            and routes[1]["exact_gains"][0]["certificate"][
                "colored_chiral_zero_modes"
            ]
            == 0
            and routes[1]["exact_gains"][1]["certificate"]["determinant"]
            == "-lambda*lambdabar*v^2"
        ),
        "route_B_selector_no_go_is_scoped_and_bound": (
            routes[1]["sharp_obstruction_proved"]
            and routes[1]["blocking_certificate"]["finite_scan"][
                "no_counterexample"
            ]
            and not routes[1]["same_action_microscopic_completion"]
        ),
        "route_C_constructive_singlet_parities_are_bound": (
            routes[2]["singlet_parity_problem_solved"]
            and routes[2]["exact_gains"][1]["certificate"][
                "all_270_singlets_assigned"
            ]
        ),
        "route_C_existing_local_GS_rejection_is_bound": (
            routes[2]["blocking_certificate"]["failed_fixed_points"]
            == ["O_GG", "O_flipped", "O_PS"]
            and not routes[2]["blocking_certificate"]["passes_all_four"]
        ),
        "no_route_has_a_same_action_microscopic_completion": no_same_action_pass,
        "cross_route_splicing_is_forbidden": True,
        "live_regeneration_extension_is_explicit_and_nonpromoting": (
            extension["current_row_is_supersedable"]
            and extension["supersession_semantics"][
                "does_not_retroactively_close_G1"
            ]
        ),
        "all_master_gates_remain_open": no_gate_promotion,
    }

    report: dict[str, Any] = {
        "schema": "susy_v59_multipath_g1_frontier_master_audit/v1",
        "status": STATUS,
        "question": (
            "Do any of the three completed V59 microscopic routes close strict G1 "
            "in one action, and what exact frontier remains if none does?"
        ),
        "input_core_hashes": EXPECTED_CORES,
        "upstream_status": {
            "V58": v58["status"],
            "route_A": route_a["status"],
            "route_B": route_b["status"],
            "route_C": route_c["status"],
        },
        "V58_baseline": {
            "bound_core_sha256": v58["core_sha256"],
            "strongest_near_match": v58["terminal_decision"][
                "strongest_near_match"
            ],
            "same_action_G1_completion": v58["terminal_decision"][
                "same_action_G1_completion"
            ],
            "selected_lead_action": v58["terminal_decision"][
                "selected_lead_action"
            ],
            "honest_outcome": v58["terminal_decision"]["honest_outcome"],
            "strict_G1_matrix": v58["strict_G1_matrix"],
        },
        "route_matrix": routes,
        "cross_route_composition_rule": {
            "logical_rule": (
                "Strict G1 is existential over a single versioned action, not a "
                "conjunction of route-local passes taken from inequivalent actions."
            ),
            "route_action_families_are_distinct": True,
            "cross_route_splicing_allowed": False,
            "aggregated_G1_closure": False,
            "examples_forbidden": [
                "V58's modular-invariant CFT plus route B's weak projector",
                "route B's rank-breaking determinant plus route C's integrated lattice",
                "route C's singlet parity witness plus an unregenerated heterotic charge ledger",
            ],
        },
        "comparison_conclusion": {
            "heterotic": (
                "V58 remains the strongest real microscopic near-match. Route A is a "
                "data-identifiability frontier, not a falsification of its physical Z4R."
            ),
            "Spin11": (
                "Route B proves an exact two-weak/zero-colored projector and repairs the "
                "rank-breaking five block, but proves a commuting Abelian non-R selector "
                "no-go in its stated local-family class and leaves quantum/UV data open."
            ),
            "gauged_U1R": (
                "Route C completes the integrated seed and 270-singlet parity problem, "
                "then exactly rejects the existing bulk GS direction at three fixed points."
            ),
            "frontier": (
                "No tested route is a complete theory. The live heterotic regeneration "
                "is the only pending computation that may supersede an existing row "
                "without first proposing a new action."
            ),
        },
        "live_heterotic_regeneration_extension": extension,
        "strict_master_decision": {
            "same_action_microscopic_completion_found": False,
            "V59_G1_closed": False,
            "closed_gates": [],
            "complete_theory": False,
            "empirical_discovery": False,
            "master_is_a_frontier_certificate_not_an_action": True,
            "honest_outcome": (
                "The three routes add exact, non-overlapping information but no one "
                "versioned action closes G1. G1--G8 remain open. Route A may be "
                "superseded by a live Orbifolder/worldsheet regeneration; such a result "
                "must be rebound and re-audited before any promotion."
            ),
        },
        "gate_ledger": gates,
        "source_policy": {
            "master_adds_no_new_literature_claim": True,
            "route_primary_sources_are_in_the_bound_route_artifacts": True,
            "route_claims_are_scoped_by_their_canonical_cores": True,
        },
        "source_manifest": source_manifest(),
        "integrity_checks": integrity,
        "n_integrity_checks": len(integrity),
        "n_failed_integrity_checks": sum(not value for value in integrity.values()),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise AssertionError("V59 multipath canonical core mismatch")
    if report["n_failed_integrity_checks"] != 0:
        failed = [
            name for name, ok in report["integrity_checks"].items() if not ok
        ]
        raise AssertionError(f"V59 multipath integrity failures: {failed}")
    if report["strict_master_decision"]["same_action_microscopic_completion_found"]:
        raise AssertionError("master must not promote an absent same-action completion")
    if report["cross_route_composition_rule"]["cross_route_splicing_allowed"]:
        raise AssertionError("master must not splice inequivalent actions")
    if any(row["status"] != "OPEN" for row in report["gate_ledger"]):
        raise AssertionError("V59 multipath master promoted a gate")


def render_markdown(report: Mapping[str, Any]) -> str:
    routes = {row["route_id"]: row for row in report["route_matrix"]}
    route_a = routes["A"]
    route_b = routes["B"]
    route_c = routes["C"]
    extension = report["live_heterotic_regeneration_extension"]
    route_rows = "\n".join(
        (
            f"| {row['route_id']} | {row['name']} | {row['classification']} | "
            f"{row['G1_closed']} |"
        )
        for row in report["route_matrix"]
    )
    gate_rows = "\n".join(
        f"| {row['gate']} | {row['status']} | {row['decision']} |"
        for row in report["gate_ledger"]
    )
    minimum_payload = "\n".join(
        f"- {item}" for item in extension["minimum_replacement_payload"]
    )
    replacement_contract = "\n".join(
        f"- {item}" for item in extension["replacement_contract"]
    )
    return f"""# V59 multipath G1 frontier master audit

Status: `{report['status']}`

## Result

**No completed V59 route closes strict G1 in one action. G1--G8 remain OPEN.**

The master binds V58 and all three V59 route cores. It does not combine a pass
from one action with a pass from another. Route A is an information-deficit
result and may be replaced by a live Orbifolder regeneration; routes B and C
contain exact, action-scoped obstructions.

| Route | Completion family | Exact classification | G1 closed |
|---|---|---|---|
{route_rows}

## Bound baseline

V58 remains `{report['V58_baseline']['strongest_near_match']}`. Its exact CFT,
Narain lattice, modular arithmetic, and source-locked light-spectrum advances
remain real. Its corrected residual-R/GS ledger, controlled F-flat vacuum, and
local/6D Spin(10) match remain open; it has no selected lead action that closes
G1.

## Route A: corrected heterotic charges

The corrected charge is

```text
{route_a['blocking_certificate']['equation']}
```

The published Table E.2 projection omits the statewise data needed for the
`gamma_hg` term. Holding all published macro columns fixed while changing the
omitted gamma from 0 to 1/2 changes a Z4 charge by
`{route_a['exact_gains'][2]['certificate']['charge_difference_mod_4']}` and an
SU(2)^2-Z4R anomaly by
`{route_a['exact_gains'][2]['certificate']['SU2_anomaly_difference_mod_2']}`
modulo two. This proves source non-identifiability only. It does **not** prove
that the physical residual Z4R is inconsistent.

The old visible ledger is reproduced in its historical scope:
`A3={route_a['exact_gains'][0]['certificate']['A_SU3']}` and
`A2={route_a['exact_gains'][0]['certificate']['A_SU2']}`, universal modulo
`eta={route_a['exact_gains'][0]['certificate']['eta']}`. It is not relabeled as
the corrected full-state ledger.

## Route B: Spin(11) gauge-Higgs

The exact interval projector gives
`{route_b['exact_gains'][0]['certificate']['weak_chiral_zero_modes']}` weak
chiral zero modes and
`{route_b['exact_gains'][0]['certificate']['colored_chiral_zero_modes']}`
colored chiral zero modes. The rank-breaking five block has

```text
det M5 = {route_b['exact_gains'][1]['certificate']['determinant']}.
```

The sharp obstruction is scoped: for an Abelian non-R 0-form selector
commuting with Spin(10), a neutral gauge-Higgs 10, three local 16s, and generic
full-rank symmetric Yukawa support, the determinant-cycle proof forces a
same-family `16_i^4` invariant. The finite scan found no counterexample in
{route_b['blocking_certificate']['finite_scan']['full_rank_charge_assignments_checked']}
full-rank assignments over moduli 2 through 24. Exact R, non-Abelian,
split/bulk-family, and explicitly regulated topological routes are not excluded.

The nonlocal Yukawa kernel is defined but not spectrum/flavour completed;
Dai--Freed trivialization and a UV regulator remain open.

## Route C: gauged U(1)R local completion

The integrated seed has `(T,V,H)=({route_c['exact_gains'][0]['certificate']['T']},
{route_c['exact_gains'][0]['certificate']['V']},
{route_c['exact_gains'][0]['certificate']['H']})`, satisfies
`H-V+29T={route_c['exact_gains'][0]['certificate']['H_minus_V_plus_29T']}`,
factorizes exactly, and uses an integral unimodular string-charge lattice.
All 270 singlet parities are assigned constructively with one neutral and one
charge-four constant coordinate.

The existing bulk Spin(10) GS direction fails at
`{route_c['blocking_certificate']['failed_fixed_points']}`. Exact examples are

```text
O_GG:      local (4,-320), bulk direction (2,40), minor 800
O_flipped: local (4,-320), bulk direction (2,40), minor 800
O_PS:      local (4,-12,-12), bulk direction (2,2,2), minors 32,32,0
```

New localized non-singlet matter or independently quantized subgroup levels
would define a new action. Normal-bundle, dyonic-string/worldsheet, and
faithful residual-q(theta)=1 data also remain open.

## No cross-route splicing

{report['cross_route_composition_rule']['logical_rule']}

Consequently, V58 modular invariance cannot be combined with the Spin(11)
projector or the route-C lattice; nor can the Spin(11) rank determinant be
combined with the route-C singlet parity solution. Every promotion must be a
same-action proof.

## Live Orbifolder extension point

State: `{extension['state']}`. The current route-A core
`{extension['current_bound_route_core']}` is explicitly supersedable because
its theorem concerns lost publication data, not a physical CFT no-go.

Minimum regenerated payload:

{minimum_payload}

Replacement contract:

{replacement_contract}

Supersession replaces only route A. It does not retroactively close G1 and
does not alter the Spin(11) or gauged-U(1)R certificates.

## Gate ledger

| Gate | Status | Decision |
|---|---|---|
{gate_rows}

## Fail-closed decision

{report['strict_master_decision']['honest_outcome']}

This master adds no new literature claim; primary-source provenance remains in
the four canonically bound input artifacts.

Core SHA-256: `{report['core_sha256']}`
"""


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write JSON and Markdown")
    parser.add_argument("--check", action="store_true", help="verify generated artifacts")
    args = parser.parse_args()

    report = build_report()
    validate(report)
    if args.write:
        write_outputs(report)
    if args.check:
        if not JSON_PATH.is_file() or not MD_PATH.is_file():
            raise RuntimeError("generated V59 master artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("generated V59 master JSON is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("generated V59 master Markdown is stale")
    print(report["status"])
    print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
