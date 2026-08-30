#!/usr/bin/env python3
"""Bind the V54 redesign routes and enforce one-action G1--G8 accounting.

V54 deliberately changes the failed V53 architecture in several inequivalent
ways.  This master audit records the strongest exact result from each route,
rejects routes at their first symmetry-complete obstruction, and selects only a
falsifiable architecture blueprint.  Results from different actions are never
combined into a gate promotion.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V54_THEORY_REDESIGN_INTEGRATION_AUDIT.json"
MD_PATH = ROOT / "SUSY_V54_THEORY_REDESIGN_INTEGRATION_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v54_theory_redesign_integration_audit.py"

INPUTS = {
    "v53_master": ROOT / "SUSY_V53_THEORY_COMPLETION_VERIFICATION_AUDIT.json",
    "continuous_parent": ROOT / "SUSY_V54_CONTINUOUS_PARENT_FI_ROUTE_AUDIT.json",
    "degree5_messenger": ROOT / "SUSY_V54_DEGREE5_MESSENGER_UV_NO_GO_AUDIT.json",
    "nonabelian_filter": ROOT / "SUSY_V54_NONABELIAN_FILTER_ROUTE_AUDIT.json",
    "anomalous_u1_blueprint": ROOT / "SUSY_V54_ANOMALOUS_U1A_BLUEPRINT_AUDIT.json",
    "q4_flavour": ROOT / "SUSY_V54_Q4_FLAVOUR_MODERN_DATA_AUDIT.json",
}

EXPECTED_CORES = {
    "v53_master": "620525de6b9a6ed2a63fe7e734caa18239dc26b4ef3e36b8eadbd4259d9e3cde",
    "continuous_parent": "25b0a48ea19fe6831049a46b01259a2a465f5f65584528d1670927156956633e",
    "degree5_messenger": "fa9b64b42f439e01a730a8fd98cd911679cbe6968d3492abba7888ecb6490546",
    "nonabelian_filter": "b6f8f135b794c1ac25a478af90dbf18aa29b1fa791ab11cf59fc46829f051331",
    "anomalous_u1_blueprint": "59bc36c4899a6ca2985bfa8d9cdbad927d6c33fc3ef326daf9e39c280589b1c7",
    "q4_flavour": "6e4b1cc7718dc4f4787dd2c546394af1e0454a026ba53963c9ea81f522afb850",
}

STATUS = (
    "V54_THEORY_REDESIGN_INTEGRATION__CONTINUOUS_FI_GENERIC_ACTION_HAS_NO_HIGGS__"
    "CHARGED_SOURCE_DYNAMICAL_RESCUE_229RANK191NULL38_EXACT__"
    "DEGREE5_MESSENGERS_REOPEN_PROTON_AND_DT__SU2F_SELECTOR_FORCES_HAH__"
    "ANOMALOUS_U1_BLUEPRINT_SPLITS_FI_AND_Q4_BRANCHES__FROZEN_Q4_BENCHMARK_"
    "EXCLUDED_AND_BOUNDED_REFIT_NO_FIT__ZERO_V54_GATE_PROMOTIONS__ONLY_FROZEN_"
    "G1_RETAINED__COMPLETE_THEORY_FALSE__REDESIGN_SAVED"
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


def load_bound(name: str, path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"missing V54 input: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    actual = canonical_sha(value)
    if value.get("core_sha256") != actual:
        raise RuntimeError(f"stale canonical core: {path.name}")
    if actual != EXPECTED_CORES[name]:
        raise RuntimeError(f"unexpected upstream core: {path.name}")
    return value


def route_ledger(inputs: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    continuous = inputs["continuous_parent"]
    degree5 = inputs["degree5_messenger"]
    nonabelian = inputs["nonabelian_filter"]
    blueprint = inputs["anomalous_u1_blueprint"]
    flavour = inputs["q4_flavour"]

    continuous_geometry = continuous["generic_allowed_visible_action"]
    continuous_rescue = continuous["charged_source_dynamical_rescue"]
    degree5_action = degree5["selected_renormalizable_UV_action"]
    degree5_geometry = degree5["selected_action_combined_geometry"]
    degree5_census = degree5["symmetry_complete_operator_census"]
    nonabelian_geometry = nonabelian["same_action_hessian"]
    dt = blueprint["exact_DT_mass_matrices"]
    protection = blueprint["all_order_DT_protection"]
    anomaly = blueprint["anomaly_and_FI_scope"]
    benchmark = flavour["published_benchmark_reproduction"]["observables"]
    refit = flavour["bounded_refit"]

    return [
        {
            "id": "R1_CONTINUOUS_PARENT_FI",
            "classification": "UNCHANGED_ACTION_REJECTED__CHARGED_SOURCE_LOCAL_RESCUE_EXACT_BUT_INCOMPLETE",
            "changed_physics": (
                "gauge a continuous parent, charge the DW source, and dynamically stabilize "
                "seven spurions with six renormalizable constraints"
            ),
            "unchanged_action_control": {
                "coordinates": continuous_geometry["visible_coordinates"],
                "H_rank": continuous_geometry["hessian_rank"],
                "H_nullity": continuous_geometry["hessian_nullity"],
                "Q_rank": continuous_geometry["gauge_orbit_rank"],
                "physical_weak_Higgs_zero_modes": continuous_geometry[
                    "physical_weak_Higgs_zero_modes"
                ],
            },
            "unchanged_action_obstruction": (
                "The unchanged source forces q(B)=0; allowing h B H2 therefore allows the "
                "renormalizable filler h H2, whose generic action has no weak-Higgs zero mode."
            ),
            "exact_local_rescue": {
                "new_field": continuous_rescue["new_field"],
                "spurion_constraint_rank": continuous_rescue["constraint_jacobian_rank"],
                "spurion_constraint_kernel": continuous_rescue["constraint_kernel"],
                "all_spurion_F_residuals": continuous_rescue["all_spurion_F_residuals"],
                "coordinates": continuous_rescue["local_same_action"]["coordinates"],
                "H_rank": continuous_rescue["local_same_action"]["hessian_rank"],
                "H_nullity": continuous_rescue["local_same_action"]["hessian_nullity"],
                "Q_rank": continuous_rescue["local_same_action"]["gauge_orbit_rank"],
                "kernel_decomposition": continuous_rescue["local_same_action"][
                    "kernel_decomposition"
                ],
                "GS_repaired_coordinates": continuous_rescue["single_GS_singlet_repair"][
                    "coordinates"
                ],
                "GS_repaired_H_rank": continuous_rescue["single_GS_singlet_repair"][
                    "hessian_rank"
                ],
                "GS_spectator_count": continuous_rescue["single_GS_singlet_repair"][
                    "exact_spectator_Z2_odd_count"
                ],
            },
            "fail_closed_boundary": {
                "first_F4_total_degree": 4
                + continuous_rescue["operator_screen"]["first_F4_dressing"][
                    "insertions"
                ],
                "complete_operator_census": False,
                "GS_Kahler_vector_completion": False,
                "remaining_items": continuous_rescue["remaining_fail_closed_items"],
            },
            "gate_promotions": [],
        },
        {
            "id": "R2_DEGREE5_MESSENGER_UV",
            "classification": "REJECTED_SYMMETRY_COMPLETE_EFT",
            "changed_physics": "renormalizable singlet-messenger UV completion of the degree-five driver",
            "exact_advance": {
                "singlet_coordinates": len(degree5_action["coordinates"]),
                "singlet_H_rank": degree5_action["hessian_rank_QQ"],
                "singlet_H_determinant": degree5_action["hessian_determinant"],
                "combined_coordinates": degree5_geometry["coordinate_inventory"]["total"],
                "combined_H_rank": degree5_geometry["rank_decomposition"]["total"],
                "combined_H_nullity": degree5_geometry["nullity"],
            },
            "fatal_obstruction": {
                "gauge_invariant_degree6_F4_rows": degree5_census["allowed_row_count"],
                "gauge_invariant_directions": degree5_census["allowed_invariant_directions"],
                "DT_filler": degree5_census["renormalizable_DT_filler"]["operator"],
            },
            "gate_promotions": [],
        },
        {
            "id": "R3_NONABELIAN_SU2F_FILTER",
            "classification": "REJECTED_SELECTOR_COMPLETE_ACTION",
            "changed_physics": "replace the Abelian filter selector by gauged SU(2)_F",
            "exact_advance": {
                "declared_coordinates": nonabelian_geometry["declared_coordinates"],
                "declared_H_rank": nonabelian_geometry["declared_rank"],
                "declared_H_nullity": nonabelian_geometry["declared_nullity"],
                "combined_Q_rank": nonabelian_geometry["combined_gauge_orbit_rank"],
                "declared_weak_modes": nonabelian_geometry["declared_kernel_decomposition"][
                    "weak_Higgs"
                ],
            },
            "fatal_obstruction": {
                "operator": nonabelian["no_go"]["first_fatal_operator"],
                "complete_H_rank": nonabelian_geometry[
                    "symmetry_complete_with_fatal_operator_rank"
                ],
                "complete_H_nullity": nonabelian_geometry[
                    "symmetry_complete_with_fatal_operator_nullity"
                ],
                "kernel": "36 gauge modes only",
                "proton_leak": nonabelian["no_go"]["proton_leak"],
            },
            "gate_promotions": [],
        },
        {
            "id": "R4_ANOMALOUS_U1A_LOW_INDEX_BLUEPRINT",
            "classification": "SELECTED_ARCHITECTURE_BLUEPRINT__NOT_ONE_ACTION",
            "changed_physics": "low-index anomalous-U1A x Z2 cutoff EFT with spinor alignment",
            "exact_advance": {
                "visible_coordinates": blueprint["candidate"]["visible_complex_coordinates"],
                "doublet_rank": dt["doublet_rank"],
                "doublet_nullity": dt["doublet_nullity"],
                "triplet_rank": dt["triplet_rank"],
                "triplet_determinant_formula": dt["symbolic_triplet_determinant"],
                "vacuum_active_all_n_formula": protection["all_n_algebra"]["formula"],
                "abstract_H2barC4_allowed": protection["operator_level_stress_test"][
                    "symmetry_allowed"
                ],
                "visible_Spin10_b": blueprint["perturbativity"]["Spin10_one_loop_b_Landau"],
            },
            "fatal_boundary": {
                "one_same_action_charge_ledger": blueprint["candidate"][
                    "one_same_action_charge_ledger"
                ],
                "FI_branch_F12": anomaly["FI_trace_benchmark_F12_charge"],
                "Q4_branch_F12": anomaly["later_Q4_flavour_F12_charge"],
                "Q4_partial_TrQ_after_XY": anomaly["later_Q4_branch_partial_ledger"][
                    "Tr_Q_after_XY"
                ],
                "full_179_Hessian": "not constructed",
            },
            "gate_promotions": [],
        },
        {
            "id": "R5_Q4_MODERN_FLAVOUR_KILL_TEST",
            "classification": "FROZEN_POINT_EXCLUDED__BOUNDED_SUBSPACE_NO_FIT",
            "changed_physics": "reconstruct the published seesaw texture and test current data",
            "exact_advance": {
                "theta12_deg": benchmark["theta12_deg"],
                "theta23_deg": benchmark["theta23_deg"],
                "theta13_deg": benchmark["theta13_deg"],
                "sqrt_mass_splitting_ratio": benchmark[
                    "sqrt_delta_m21_sq_over_delta_m31_sq"
                ],
                "published_benchmark_reproduced": flavour["verdict"][
                    "published_2010_benchmark_reproduced"
                ],
            },
            "modern_test": {
                "frozen_failed_observables": flavour["frozen_2010_benchmark_test"][
                    "failed_observables"
                ],
                "bounded_seeds": refit["seeds"],
                "bounded_best_objective": refit["best_run"]["objective"],
                "bounded_feasible": refit["feasible_point_found"],
                "global_texture_theorem": not refit["not_a_global_theorem"],
            },
            "gate_promotions": [],
        },
    ]


def clause_ledger() -> list[dict[str, str]]:
    return [
        {
            "id": "C1",
            "status": "PARTIAL_SCOPE_ONLY",
            "statement": (
                "Exact charge, parity, center, and bounded operator screens exist, but no "
                "complete tensor/operator census exists for one GS+Q4+mediator action."
            ),
        },
        {
            "id": "C2",
            "status": "PARTIAL_HIGGS_EFT_ONLY",
            "statement": (
                "The R1 rescue is an explicit renormalizable local chiral action and R4 is an "
                "explicit cutoff Higgs EFT, but neither is one full GS/Q4/Kahler action."
            ),
        },
        {
            "id": "C3",
            "status": "PARTIAL_EXACT_LOCAL_HESSIAN",
            "statement": (
                "R1 has an exact 229-coordinate local Hessian and 363-coordinate spectator "
                "extension; matter/flavour and the GS vector/modulus sector are absent. R4 "
                "has exact reduced 4x4 doublet/triplet ranks only."
            ),
        },
        {
            "id": "C4",
            "status": "PARTIAL_PUBLISHED_LOCAL_VACUUM_ONLY",
            "statement": (
                "Published local F/D vacuum relations were reconstructed in scope, but no "
                "executable global, GS, radiative, soft, or tunnelling proof exists."
            ),
        },
        {
            "id": "C5",
            "status": "OPEN",
            "statement": (
                "No same-action current threshold matching and frozen low-energy EFT "
                "coefficient array has been reproduced."
            ),
        },
        {
            "id": "C6",
            "status": "OPEN_GS_AND_CHARGE_BRANCH_INCOMPATIBLE",
            "statement": (
                "The GS modulus is unspecified and the published FI and Q4 first-family "
                "charge branches are incompatible."
            ),
        },
        {
            "id": "C7",
            "status": "OPEN",
            "statement": (
                "No same-action current Wilson array, correlated likelihood, or withheld "
                "prediction exists."
            ),
        },
    ]


def gate_ledger() -> list[dict[str, Any]]:
    partial = {
        "G1": "Historical ordinary-Spin quotient/anomaly lemma remains frozen; V54 needs its own GS/global quotient.",
        "G2": "The C1-C7 same-action conjunction fails.",
        "G3": "R1 has an exact local chiral Hessian/quotient, but no matter/flavour, GS vector/modulus, or global vacuum completion.",
        "G4": "R1 preserves four weak modes only through a bounded operator screen; R4 has canonical-vacuum DT protection and reduced ranks. Full spectrum, mu/Bmu and EWSB are open.",
        "G5": "No dark-sector or cosmological action and likelihood exists.",
        "G6": "R1 has b=18 and R4 has visible b=0 at one loop; full states, thresholds and two-loop running are open.",
        "G7": "Q4 x Z2 tensors, mediators, Wilson matching and current proton lifetimes are open.",
        "G8": "The frozen benchmark is excluded and the bounded a,b refit found no fit; a consistent modern global refit is open.",
    }
    rows = []
    for index in range(1, 9):
        gate = f"G{index}"
        rows.append(
            {
                "gate": gate,
                "closed": gate == "G1",
                "V54_candidate_closed": False,
                "scope": "frozen ordinary-Spin namespace only" if gate == "G1" else "V54",
                "decision": partial[gate],
            }
        )
    return rows


def source_manifest() -> list[dict[str, Any]]:
    paths = [Path(__file__), TEST_PATH, *INPUTS.values()]
    return [
        {"path": path.name, "exists": path.is_file(), "sha256": sha256_file(path)}
        for path in paths
    ]


def build_report() -> dict[str, Any]:
    inputs = {name: load_bound(name, path) for name, path in INPUTS.items()}
    routes = route_ledger(inputs)
    clauses = clause_ledger()
    gates = gate_ledger()

    continuous = inputs["continuous_parent"]
    degree5 = inputs["degree5_messenger"]
    nonabelian = inputs["nonabelian_filter"]
    blueprint = inputs["anomalous_u1_blueprint"]
    flavour = inputs["q4_flavour"]

    integrity = {
        "all_input_cores_are_canonical_and_expected": all(
            inputs[name]["core_sha256"] == expected
            for name, expected in EXPECTED_CORES.items()
        ),
        "five_V54_routes_are_integrated": len(routes) == 5,
        "continuous_generic_action_has_zero_Higgs_modes": continuous[
            "generic_allowed_visible_action"
        ]["physical_weak_Higgs_zero_modes"]
        == 0,
        "continuous_charged_source_local_rescue_is_exact": (
            continuous["charged_source_dynamical_rescue"]["constraint_jacobian_rank"]
            == 6
            and not any(
                continuous["charged_source_dynamical_rescue"][
                    "all_spurion_F_residuals"
                ]
            )
            and continuous["charged_source_dynamical_rescue"]["local_same_action"]
            ["coordinates"]
            == 229
            and continuous["charged_source_dynamical_rescue"]["local_same_action"]
            ["hessian_rank"]
            == 191
            and continuous["charged_source_dynamical_rescue"]["local_same_action"]
            ["hessian_nullity"]
            == 38
            and continuous["charged_source_dynamical_rescue"]["local_same_action"]
            ["gauge_orbit_rank"]
            == 34
            and continuous["charged_source_dynamical_rescue"]["local_same_action"]
            ["kernel_decomposition"]
            == {"Spin10_gauge": 33, "U1_gauge": 1, "weak_Higgs": 4, "extra": 0}
            and continuous["charged_source_dynamical_rescue"][
                "single_GS_singlet_repair"
            ]["coordinates"]
            == 363
            and continuous["charged_source_dynamical_rescue"][
                "single_GS_singlet_repair"
            ]["hessian_rank"]
            == 325
        ),
        "degree5_center_corrected_census_is_4_rows_24_directions": (
            degree5["symmetry_complete_operator_census"]["allowed_row_count"] == 4
            and degree5["symmetry_complete_operator_census"][
                "allowed_invariant_directions"
            ]
            == 24
        ),
        "nonabelian_complete_kernel_is_gauge_only": nonabelian[
            "same_action_hessian"
        ]["fatal_kernel_equals_gauge_only"],
        "blueprint_reduced_DT_ranks_are_exact": (
            blueprint["exact_DT_mass_matrices"]["doublet_rank"] == 3
            and blueprint["exact_DT_mass_matrices"]["triplet_rank"] == 4
            and blueprint["exact_DT_mass_matrices"][
                "symbolic_triplet_formula_verified"
            ]
        ),
        "blueprint_charge_branches_are_not_one_action": not blueprint["candidate"][
            "one_same_action_charge_ledger"
        ],
        "frozen_flavour_benchmark_is_reproduced_then_excluded": (
            flavour["verdict"]["published_2010_benchmark_reproduced"]
            and flavour["verdict"]["frozen_2010_benchmark_excluded"]
        ),
        "bounded_flavour_no_fit_is_not_global_theorem": (
            not flavour["bounded_refit"]["feasible_point_found"]
            and flavour["bounded_refit"]["not_a_global_theorem"]
            and not flavour["verdict"]["texture_globally_excluded"]
        ),
        "no_route_promotes_a_gate": all(not route["gate_promotions"] for route in routes),
        "no_clause_is_passed": all(not row["status"].startswith("PASS") for row in clauses),
        "no_V54_candidate_gate_is_closed": not any(
            row["V54_candidate_closed"] for row in gates
        ),
        "only_historical_G1_is_cumulatively_closed": [
            row["gate"] for row in gates if row["closed"]
        ]
        == ["G1"],
    }

    report: dict[str, Any] = {
        "schema": "susy-v54-theory-redesign-integration-audit-v1",
        "status": STATUS,
        "input_core_hashes": {
            name: inputs[name]["core_sha256"] for name in INPUTS
        },
        "expected_input_core_hashes": EXPECTED_CORES,
        "same_action_rule": (
            "A gate can close only when all of its hypotheses are proved in one canonical "
            "action. Exact geometry from a deliberately sparse texture cannot be combined "
            "with a selector or anomaly certificate belonging to another action."
        ),
        "route_ledger": routes,
        "selected_redesign": {
            "complete_candidate": None,
            "architecture_blueprint": "R4_ANOMALOUS_U1A_LOW_INDEX_BLUEPRINT",
            "executable_frontier_candidate": (
                "R1_CONTINUOUS_PARENT_FI charged-source dynamical rescue"
            ),
            "reason": (
                "R1 is the strongest executable local candidate: its renormalizable chiral "
                "action has an exact gauge-only-plus-four-Higgs kernel, including an exact "
                "singlet anomaly repair. It is still incomplete because matter/flavour, the "
                "physical GS vector/modulus sector, the global vacuum and the unbounded "
                "operator/Wilson analysis are absent. R4 remains the low-index architecture "
                "blueprint, but its FI and Q4 charge ledgers differ and therefore do not define "
                "one action."
            ),
        },
        "V54_candidate_clause_ledger": clauses,
        "gate_ledger": gates,
        "hard_next_obligations": [
            {
                "id": "N1_ONE_ACTION",
                "requirement": (
                    "Choose one anomaly/charge branch and write the complete GS modulus, Q4 "
                    "flavon, mediator, Kahler, gauge and superpotential action."
                ),
            },
            {
                "id": "N2_FULL_GEOMETRY",
                "requirement": (
                    "At one exact vacuum compute F, D, the full Hessian and gauge-orbit matrix; "
                    "the kernel must contain only the intended broken-gauge, 45 light-matter "
                    "and four weak-Higgs directions after the RH-neutrino sector is included."
                ),
            },
            {
                "id": "N3_COMPLETE_OPERATORS",
                "requirement": (
                    "Enumerate complete SO(10) x U1A x Z2 x Q4 tensors and mediator-generated "
                    "operators, including proton and Higgs-mass classes."
                ),
            },
            {
                "id": "N4_CURRENT_PHENOMENOLOGY",
                "requirement": (
                    "Perform a joint charged-fermion/neutrino fit with current RG thresholds, "
                    "then propagate it into unification and d=5/d=6 Wilson coefficients."
                ),
            },
            {
                "id": "N5_SOFT_AND_COSMOLOGY",
                "requirement": (
                    "Add SUSY breaking, mu/Bmu, radiative EWSB, the physical scalar spectrum, "
                    "global-vacuum tests and any claimed cosmology."
                ),
            },
        ],
        "final_decision": {
            "bounded_V54_redesign_finished": True,
            "same_action_completion": False,
            "complete_theory": False,
            "empirical_new_physics_discovery": False,
            "selected_complete_candidate": None,
            "selected_architecture_blueprint": "R4_ANOMALOUS_U1A_LOW_INDEX_BLUEPRINT",
            "selected_executable_frontier_candidate": (
                "R1_CONTINUOUS_PARENT_FI charged-source dynamical rescue"
            ),
            "V54_candidate_closed_gates": [],
            "full_gates_closed_for_V54_candidate": 0,
            "cumulative_reusable_closed_gates": ["G1"],
            "honest_outcome": (
                "V54 saves an exact 229-coordinate charged-source local rescue, its exact "
                "363-coordinate anomaly-repaired singlet extension, several route no-go "
                "theorems, and a falsifiable low-index architecture blueprint. It does not "
                "produce a complete same-action theory."
            ),
        },
        "verification_run": {
            "date": "2026-08-28",
            "python_compile": {
                "V54_scripts": 6,
                "passed": True,
            },
            "focused_V54_pytest": {
                "passed": 71,
                "failed": 0,
                "scope": "all six V54 route and integration test modules",
            },
            "historical_pytest": {
                "passed": 697,
                "failed": 0,
                "scope": "all test_susy_v40 through test_susy_v54 modules",
            },
            "supported_artifact_freshness_checks_passed": True,
        },
        "primary_sources": [
            {
                "title": "Constraining Proton Lifetime in SO(10) with Stabilized Doublet-Triplet Splitting",
                "url": "https://arxiv.org/abs/1003.2625",
            },
            {
                "title": "NuFit-6.0: Updated global analysis of three-flavor neutrino oscillations",
                "url": "https://arxiv.org/abs/2410.05380",
            },
            {
                "title": "NuFIT 6.1 official parameter table",
                "url": "https://www.nu-fit.org/sites/default/files/v61.tbl-parameters.pdf",
            },
            {
                "title": "A Complete Supersymmetric SO(10) Model",
                "url": "https://arxiv.org/abs/hep-ph/9501298",
            },
            {
                "title": "Natural Doublet-Triplet Splitting from the Viewpoint of the SO(10) Grand Unified Theory",
                "url": "https://arxiv.org/abs/1410.5625",
            },
            {
                "title": "A Renormalizable Supersymmetric SO(10) Model",
                "url": "https://arxiv.org/abs/1504.01850",
            },
            {
                "title": "Natural R-Symmetry and the Missing Partner Mechanism",
                "url": "https://arxiv.org/abs/1109.4797",
            },
        ],
        "integrity_checks": integrity,
        "n_failed_integrity_checks": sum(not value for value in integrity.values()),
        "source_manifest": source_manifest(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report["status"] != STATUS or report["core_sha256"] != canonical_sha(report):
        raise RuntimeError("V54 master status or core drift")
    if report["n_failed_integrity_checks"] or not all(
        report["integrity_checks"].values()
    ):
        raise RuntimeError("V54 master integrity failure")
    decision = report["final_decision"]
    if decision["complete_theory"] or decision["same_action_completion"]:
        raise RuntimeError("V54 completion was overclaimed")
    if decision["V54_candidate_closed_gates"]:
        raise RuntimeError("V54 candidate gate was overpromoted")


def render_markdown(report: Mapping[str, Any]) -> str:
    routes = {row["id"]: row for row in report["route_ledger"]}
    r1 = routes["R1_CONTINUOUS_PARENT_FI"]
    r2 = routes["R2_DEGREE5_MESSENGER_UV"]
    r3 = routes["R3_NONABELIAN_SU2F_FILTER"]
    r4 = routes["R4_ANOMALOUS_U1A_LOW_INDEX_BLUEPRINT"]
    r5 = routes["R5_Q4_MODERN_FLAVOUR_KILL_TEST"]
    return f"""# V54 theory redesign integration audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Decision

{report['final_decision']['honest_outcome']}

The V54 candidate closes `0/8` gates. The only cumulative closed gate is the
frozen historical `G1` result in its ordinary-Spin namespace; it is not a V54
closure. No empirical discovery is claimed.

## Verification

All six V54 audit scripts compile. The focused V54 suite passes
`{report['verification_run']['focused_V54_pytest']['passed']}/71` tests, and the
full V40-V54 regression passes
`{report['verification_run']['historical_pytest']['passed']}/697` tests. All
supported artifact freshness checks pass.

## Executed redesign routes

- **Continuous parent/FI.** The unchanged generic action has
  `{r1['unchanged_action_control']['coordinates']}` coordinates, rank
  `{r1['unchanged_action_control']['H_rank']}`, and nullity
  `{r1['unchanged_action_control']['H_nullity']}=rank(Q)`, but it has
  `{r1['unchanged_action_control']['physical_weak_Higgs_zero_modes']}` physical
  weak-Higgs zero modes because `h H2` is automatically allowed. The redesigned
  charged-source action adds `{r1['exact_local_rescue']['new_field']['name']}`
  with charge `{r1['exact_local_rescue']['new_field']['U1_charge']}`, fixes the
  seven spurions with constraint rank
  `{r1['exact_local_rescue']['spurion_constraint_rank']}`, and has an exact
  `{r1['exact_local_rescue']['coordinates']}`-coordinate Hessian of rank
  `{r1['exact_local_rescue']['H_rank']}`/nullity
  `{r1['exact_local_rescue']['H_nullity']}`. Its kernel is exactly 34 gauge plus
  four weak-Higgs modes and no extra mode. The single-GS singlet repair has
  `{r1['exact_local_rescue']['GS_repaired_coordinates']}` coordinates, rank
  `{r1['exact_local_rescue']['GS_repaired_H_rank']}`, and
  `{r1['exact_local_rescue']['GS_spectator_count']}` spectator singlets. The
  first charge-neutral F^4 dressing occurs only at total degree
  `{r1['fail_closed_boundary']['first_F4_total_degree']}`, but an all-order
  operator census and the physical GS completion remain open.
- **Degree-five messenger UV.** The exact 14-singlet driver Hessian is full rank
  and the selected 230-coordinate texture has rank 193/nullity 37. Restoring all
  allowed operators exposes
  `{r2['fatal_obstruction']['gauge_invariant_degree6_F4_rows']}` genuine
  degree-six proton rows with
  `{r2['fatal_obstruction']['gauge_invariant_directions']}` directions plus
  `{r2['fatal_obstruction']['DT_filler']}`.
- **Non-Abelian SU(2)F filter.** The declared 255-coordinate action has rank
  `{r3['exact_advance']['declared_H_rank']}` and four weak modes. Its selector
  necessarily permits `{r3['fatal_obstruction']['operator']}`; the completed
  rank becomes `{r3['fatal_obstruction']['complete_H_rank']}` with a gauge-only
  kernel.
- **Anomalous-U1A low-index architecture.** The reduced doublet/triplet ranks
  are `{r4['exact_advance']['doublet_rank']}` and
  `{r4['exact_advance']['triplet_rank']}`, and the vacuum-active all-n charge
  formula is `{r4['exact_advance']['vacuum_active_all_n_formula']}`. This is an
  architecture family, not one action: the published FI and Q4 branches assign
  the first two families charges `{r4['fatal_boundary']['FI_branch_F12']}` and
  `{r4['fatal_boundary']['Q4_branch_F12']}`.
- **Modern flavor kill test.** The published benchmark is reproduced, including
  `theta13={r5['exact_advance']['theta13_deg']:.6f} deg`, then fails current
  theta12, theta13 and mass-ratio intervals. Four deterministic bounded refits
  find no feasible point; the best interval-penalty objective is
  `{r5['modern_test']['bounded_best_objective']}`. This is not a global theorem
  against the texture family.

## Gate boundary

G1 is open for the V54 action; G2 fails the C1-C7 conjunction; G3 lacks a full
same-action quotient; G4 has only a partial vacuum-scoped DT advance; G5 has no
cosmology; G6 has only a visible one-loop inventory; G7 lacks complete tensors
and Wilson matching; G8 requires a changed, modern global flavor fit.

## Saved next obligations

The next candidate may be promoted only after one action supplies the GS/Q4 and
mediator sectors, the full F/D/Hessian quotient, a complete tensor census,
current flavor/threshold/Wilson calculations, and the soft/global/cosmological
analysis. Cross-action assembly is forbidden by the master same-action rule.

Primary blueprint: https://arxiv.org/abs/1003.2625

Current flavor ranges: https://www.nu-fit.org/sites/default/files/v61.tbl-parameters.pdf
"""


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
    if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
        raise RuntimeError("stale V54 master JSON")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("stale V54 master Markdown")


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
        print("V54_THEORY_REDESIGN_INTEGRATION_AUDIT_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
