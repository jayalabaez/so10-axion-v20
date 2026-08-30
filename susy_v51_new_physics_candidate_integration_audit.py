#!/usr/bin/env python3
"""Integrate the V51 Clifford-locked deconstruction candidate fail-closed.

V51 is a concrete possible route, not a promoted theory.  The audit keeps the
frozen V50 same-action frontier separate from the new microscopic candidate so
that exact source and representation results cannot be combined across actions
without an explicit equivalence/matching certificate.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V51_NEW_PHYSICS_CANDIDATE_INTEGRATION_AUDIT.json"
MD_PATH = ROOT / "SUSY_V51_NEW_PHYSICS_CANDIDATE_INTEGRATION_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v51_new_physics_candidate_integration_audit.py"

INPUTS = {
    "v50_master": ROOT / "SUSY_V50_G2_FRONTIER_INTEGRATION_AUDIT.json",
    "source_orbit": ROOT / "SUSY_V51_PHYSICAL_SOURCE_ORBIT_AUDIT.json",
    "source_hessian": ROOT / "SUSY_V51_CARTESIAN_SOURCE_HESSIAN_AUDIT.json",
    "cartesian_c5_c7": ROOT
    / "SUSY_V51_CARTESIAN_MEDIATOR_C5_C7_FEASIBILITY_AUDIT.json",
    "degree4_factors": ROOT / "SUSY_V51_DEGREE4_CARTESIAN_FACTOR_AUDIT.json",
    "mediator_moose": ROOT
    / "SUSY_V51_REPRESENTATION_FAITHFUL_MEDIATOR_MOOSE_AUDIT.json",
}

V50_SHARED_ACTION_SHA256 = (
    "04c6e60038412d99b7c2e9a80c4159fb1a6ba328a159df7b62a8fb45ec1158e4"
)
STATUS = (
    "V51_NEW_PHYSICS_CLIFFORD_LOCKED_DECONSTRUCTION_CANDIDATE_INTEGRATED__"
    "EXACT_SOURCE_ORBIT_HESSIAN_AND_DEGREE4_FACTOR_CENSUS__"
    "12_RESIDUAL_A5_CHIRALS_AND_LANDAU_WINDOW_BELOW1P70_KILL_CONTROLLED_UV__"
    "NO_SAME_ACTION_IDENTITY__NO_G2_CLAUSE_OR_FULL_GATE_PROMOTED"
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


def load_hashed_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"missing input: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"input is not a JSON object: {path.name}")
    if value.get("core_sha256") != canonical_sha(value):
        raise RuntimeError(f"stale canonical core: {path.name}")
    return value


def result(report: Mapping[str, Any], identifier: str) -> Mapping[str, Any]:
    return next(
        row for row in report["V50_exact_results"] if row["id"] == identifier
    )


def source_manifest() -> list[dict[str, Any]]:
    paths = [Path(__file__), TEST_PATH, *INPUTS.values()]
    return [
        {
            "path": path.name,
            "exists": path.is_file(),
            "sha256": sha256_file(path),
        }
        for path in paths
    ]


def frontier_clause_assessment(v50: Mapping[str, Any]) -> list[dict[str, str]]:
    """Update the V50 frontier without pretending V51 is the same action."""

    rows = copy.deepcopy(v50["G2_closure_assessment"])
    updates = {
        "C3": {
            "landed": (
                "V51 publishes the exact 465x22 source orbit, rank-443 projector, "
                "465x465 Cartesian Hessian, HQ=0 Ward identity and a nondegenerate "
                "443-dimensional source pullback.  The candidate link tangent and "
                "endpoint incidence blocks are also explicit."
            ),
            "blocker": (
                "These are subblock theorems, not a V50 same-action identification. "
                "The combined PS/SU5 endpoint count leaves 12 uneaten A5-like chirals, "
                "and the complete interacting variational domain is absent."
            ),
        },
        "C4": {
            "landed": (
                "At the tuned F-flat witness H-dagger-H is positive on the exact "
                "443-dimensional source quotient; the candidate has canonical elementary "
                "Kahler terms and paired nonzero source/vector Goldstone spectra."
            ),
            "blocker": (
                "The 12 residual endpoint chirals, full host/source quotient metric, "
                "A/Xi/C/R7/R8/Z lift and complete interacting physical pencil are unresolved."
            ),
        },
        "C5": {
            "landed": (
                "A representation-faithful vectorlike mediator theorem now realizes every "
                "resolved holomorphic factor channel at tree level."
            ),
            "blocker": (
                "The physical field table/background Hessians, one-loop 1PI mixing, finite "
                "link/mediator thresholds, bare-to-DRbar maps, affine rematch and scale "
                "cancellation are absent."
            ),
        },
        "C7": {
            "landed": (
                "All 168 source rows now have exact degree-two/three or degree-four "
                "multiplicities and Cartesian factor data; all 34 PS primitives have "
                "chirality-correct Cartesian projector tensors and ordered orientations."
            ),
            "blocker": (
                "The factor currents have not been embedded in one complete retained action, "
                "and the contracted source-to-PS physical Wilson array is still absent."
            ),
        },
    }
    for row in rows:
        if row["id"] in updates:
            row.update(updates[row["id"]])
    return rows


def candidate_clause_assessment() -> list[dict[str, str]]:
    return [
        {
            "id": "C1",
            "status": "unassessed_for_new_action",
            "statement": (
                "The new link, multiplier, transport, source and mediator content has not "
                "received a complete fixed-order invariant/operator census."
            ),
        },
        {
            "id": "C2",
            "status": "candidate_locality_only",
            "statement": (
                "The finite 4D action is site-local or nearest-neighbour, but no action hash "
                "or matching identity equates it to the frozen V50 retained action."
            ),
        },
        {
            "id": "C3",
            "status": "partial",
            "statement": (
                "Exact source/link subblocks exist; 12 endpoint A5-like chirals and the full "
                "interacting domain remain unresolved."
            ),
        },
        {
            "id": "C4",
            "status": "partial",
            "statement": (
                "Canonical elementary metrics and source positivity pass, but the complete "
                "physical quotient/pencil is not assembled."
            ),
        },
        {
            "id": "C5",
            "status": "partial",
            "statement": "Tree mediator elimination passes; one-loop matching does not exist.",
        },
        {
            "id": "C6",
            "status": "unassessed_for_new_action",
            "statement": (
                "The V50 selector policy is reusable, but the enlarged candidate field/action "
                "census has not been rerun and cannot inherit the V50 pass automatically."
            ),
        },
        {
            "id": "C7",
            "status": "partial",
            "statement": (
                "Factor spaces and PS primitives are explicit; the same-action physical "
                "Wilson array is missing."
            ),
        },
    ]


def updated_gate_ledger(v50: Mapping[str, Any]) -> list[dict[str, Any]]:
    ledger = copy.deepcopy(v50["gate_ledger"])
    for row in ledger:
        if row["gate"] == "G2":
            row.update(
                {
                    "closed": False,
                    "advance": (
                        "V51 exactly closes the source orbit/Hessian subproblem, resolves "
                        "all source-row multiplicities/factors and constructs a finite local "
                        "representation-faithful candidate."
                    ),
                    "blocker": (
                        "No V50/V51 same-action identity; 12 residual A5-like chirals; full "
                        "physical metric/pencil, one-loop rematch and Wilson array missing; "
                        "candidate perturbative UV control fails."
                    ),
                }
            )
        elif row["gate"] == "G3":
            row["advance"] = (
                "An explicit tuned Cartesian F- and D-flat witness has exact Hessian rank 443 "
                "on the physical source quotient."
            )
            row["blocker"] = (
                "m1=M1=0 lacks radiative protection; the 12 endpoint chirals, full scalar "
                "potential, soft terms and global vacuum selection remain open."
            )
        elif row["gate"] == "G6":
            row["advance"] = (
                "The candidate spectrum is explicit enough for a one-loop Spin(10) "
                "perturbativity kill test."
            )
            row["blocker"] = (
                "At g=0.73 the optimistic Landau poles are only 1.6975 and 1.6610 link "
                "scales above threshold; no lean or strong/composite UV completion is built."
            )
        elif row["gate"] == "G7":
            row["advance"] = (
                "All 168 source-row multiplicities/factor channels and 34 PS primitive "
                "projector tensors are resolved."
            )
            row["blocker"] = (
                "No final contracted physical Wilson array, dressing/running or B/L rates."
            )
    return ledger


def updated_stage_ledger(v50: Mapping[str, Any]) -> list[dict[str, Any]]:
    ledger = copy.deepcopy(v50["stage_ledger"])
    for row in ledger:
        if row["stage"] == "S0":
            row.update(
                {
                    "status": "OPEN_WITH_EXACT_CARTESIAN_SOURCE_WITNESS",
                    "passed": (
                        "exact 465-field stationarity, rank-22 orbit, rank-443 source "
                        "Hessian and nondegenerate physical pullback"
                    ),
                    "missing": (
                        "radiative protection of the tuned masses, 12 endpoint chirals, "
                        "radion/soft dynamics and global branch selection"
                    ),
                }
            )
        elif row["stage"] == "S2":
            row.update(
                {
                    "status": "OPEN_WITH_REPRESENTATION_FAITHFUL_CANDIDATE",
                    "passed": (
                        "exact local link rigidity, 32 projected transport profiles and "
                        "source-side Rxi spectral pairing"
                    ),
                    "missing": (
                        "same-action identity, lift of 12 A5-like chirals, full physical "
                        "pencil, loop matching and controlled UV window"
                    ),
                }
            )
        elif row["stage"] == "S3":
            row.update(
                {
                    "status": "OPEN_WITH_COMPLETE_FACTOR_CENSUS",
                    "passed": (
                        "all source row multiplicities/factors and all PS primitive "
                        "Cartesian projectors"
                    ),
                    "missing": (
                        "one-action coefficient/current embedding, final Wilson array, "
                        "B/L ring, dressing and rates"
                    ),
                }
            )
    return ledger


def exact_results(
    orbit: Mapping[str, Any],
    hessian: Mapping[str, Any],
    c5c7: Mapping[str, Any],
    degree4: Mapping[str, Any],
    moose: Mapping[str, Any],
) -> list[dict[str, Any]]:
    qz = orbit["orbit_and_projector_certificate"]
    hc = hessian["hessian_certificate"]
    inventory = c5c7["incidence_inventory"]
    d4 = degree4["degree_four_certificate"]
    link = moose["Clifford_locked_link"]
    transport = moose["rectangular_spinor_transport"]
    rxi = moose["source_side_coupled_Rxi"]
    running = moose["perturbativity_stress_test"]
    return [
        {
            "id": "E46",
            "result": "exact physical source orbit and quotient",
            "statement": (
                "The 465-component source chart has an exact rank-22 broken orbit and an "
                "exact Hermitian rank-443 quotient projector."
            ),
            "value": {
                "Q_shape": qz["selected_broken_map_Q"]["shape"],
                "Q_rank": qz["selected_Gram"]["exact_rank"],
                "Q_sha256": qz["selected_broken_map_Q"]["canonical_matrix_sha256"],
                "Z_shape": qz["physical_projector_Z"]["shape"],
                "Z_rank": qz["physical_projector_Z"]["rank"],
                "Z_sha256": qz["physical_projector_Z"]["canonical_projector_sha256"],
            },
        },
        {
            "id": "E47",
            "result": "exact Cartesian source Hessian",
            "statement": (
                "One normalized superpotential gives an exact F/D-flat tuned witness.  Its "
                "465x465 symmetric Hessian obeys HQ=0, has rank 443, and is nondegenerate on "
                "the physical source section."
            ),
            "value": {
                "H_shape": hc["published_H"]["shape"],
                "H_sha256": hc["published_H"]["canonical_H_sha256"],
                "H_rank": hc["exact_rank_proof"]["exact_rank_H"],
                "H_nullity": hc["exact_rank_proof"]["exact_nullity_H"],
                "HQ_exact_zero": hc["Ward_identity"]["HQ_exact_zero_all_46_columns"],
                "physical_pullback_shape": hc["physical_pullback"]["shape"],
                "physical_pullback_sha256": hc["physical_pullback"][
                    "canonical_mod13_pullback_sha256"
                ],
                "tuned_unprotected_parameters": ["m1=0", "M1=0"],
            },
        },
        {
            "id": "E48",
            "result": "chirality-correct Cartesian PS bridge",
            "statement": (
                "The PS parity, all 48 degree-two/three source rows and all 34 PS "
                "superpotential/derivative primitives are explicit with direct chirality "
                "tensors and ordered-orientation rules."
            ),
            "value": {
                "low_degree_rows": inventory["degree_two_or_three_rows_resolved_here"],
                "low_degree_resolution": inventory["low_degree_resolution_counts"],
                "PS_primitives": inventory["ps_total_primitive_declarations"],
                "bar16_PS_covariance_residual": c5c7[
                    "PS_superpotential_projector_certificate"
                ]["projected_tensor_certificates"]["bar16"][
                    "PS_covariance_residual"
                ],
            },
        },
        {
            "id": "E49",
            "result": "complete degree-four factor census",
            "statement": (
                "Exact D5 character intersections decide every remaining degree-four row "
                "and a finite normalized Cartesian factor registry resolves every nonzero "
                "copy channel."
            ),
            "value": d4,
        },
        {
            "id": "E50",
            "result": "finite representation-faithful deconstruction candidate",
            "statement": (
                "A 5-site 4D N=1 moose has an exact 567x612 Clifford-lock Jacobian of rank "
                "567, leaving precisely the 45 Spin(10) orbit tangents; projected rectangular "
                "transport has exactly 32 desired chiral profiles."
            ),
            "value": {
                "sites": moose["candidate_contract"]["sites"],
                "edges": moose["candidate_contract"]["edges"],
                "link_constraint_dimension": link["constraint_dimension"],
                "link_rank": link["complex_rank_exact"],
                "link_nullity": link["complex_nullity_exact"],
                "transport_profiles": transport["total_chiral_profile_count"],
                "extra_transport_profiles": transport[
                    "additional_uncontrolled_transport_zero_modes"
                ],
            },
        },
        {
            "id": "E51",
            "result": "combined endpoint Rxi obstruction",
            "statement": (
                "The source U(1) normalization and nonzero vector/Goldstone spectra match, "
                "but the exact PS/SU5 incidence partition leaves 12 uneaten A5-like chirals."
            ),
            "value": {
                "U1F": rxi["shared_U1F"],
                "partition": rxi["combined_host_PS_source_SU5"][
                    "generator_partition"
                ],
                "uneaten_A5_like_chirals": rxi[
                    "combined_host_PS_source_SU5"
                ]["total_uneaten_A5_like_chirals"],
            },
        },
        {
            "id": "E52",
            "result": "perturbative UV kill test",
            "statement": (
                "With canonical dynamical multipliers and g=0.73, the optimistic one-loop "
                "Spin(10) Landau poles occur below 1.70 link scales, rejecting this polynomial "
                "moose as a controlled perturbative UV completion."
            ),
            "value": {
                "g_link": running["gauge_coupling_at_link_scale"],
                "interior_b": running["interior_site"]["b_one_loop"],
                "interior_pole_ratio": running["interior_site"][
                    "Landau_pole_over_link_scale"
                ],
                "source_b": running["source_site"]["b_one_loop"],
                "source_pole_ratio": running["source_site"][
                    "Landau_pole_over_link_scale"
                ],
                "controlled_perturbative_window": running[
                    "controlled_perturbative_window"
                ],
            },
        },
    ]


def unresolved_defects() -> list[dict[str, str]]:
    return [
        {
            "id": "D16",
            "defect": "same_action_identity_and_full_physical_assembly",
            "statement": (
                "Publish a complete V51 action manifest/hash and an explicit matching map to "
                "the V50 A/Xi/C/R7/R8/Z action, then differentiate the full physical pencil."
            ),
        },
        {
            "id": "D17",
            "defect": "twelve_uneaten_endpoint_chirals",
            "statement": (
                "Construct a local gauge-covariant interaction that lifts the 12 "
                "neither-PS-nor-SU5 A5-like chirals without adding new light modes or anomalies."
            ),
        },
        {
            "id": "D18",
            "defect": "one_loop_matching_missing",
            "statement": (
                "Compute the complete background Hessians, DRbar counterterms, 1PI mixing, "
                "finite link/mediator thresholds and matching-scale cancellation."
            ),
        },
        {
            "id": "D19",
            "defect": "final_physical_Wilson_array_missing",
            "statement": (
                "Embed every factor/copy tensor and PS primitive in one coefficient/current "
                "convention and emit the contracted source-to-PS Wilson array."
            ),
        },
        {
            "id": "D20",
            "defect": "controlled_UV_completion_missing",
            "statement": (
                "Replace the 567-multiplier link by a much leaner perturbative realization or "
                "construct and test a genuine strong/composite link completion."
            ),
        },
    ]


def build_report() -> dict[str, Any]:
    loaded = {name: load_hashed_json(path) for name, path in INPUTS.items()}
    v50 = loaded["v50_master"]
    orbit = loaded["source_orbit"]
    hessian = loaded["source_hessian"]
    c5c7 = loaded["cartesian_c5_c7"]
    degree4 = loaded["degree4_factors"]
    moose = loaded["mediator_moose"]
    frontier = frontier_clause_assessment(v50)
    frontier_passed = [row["id"] for row in frontier if row["status"] == "pass"]
    candidate = candidate_clause_assessment()
    gates = updated_gate_ledger(v50)
    d4 = degree4["degree_four_certificate"]
    rxi = moose["source_side_coupled_Rxi"]
    running = moose["perturbativity_stress_test"]

    integrity = {
        "all_input_core_hashes_valid": True,
        "all_component_integrity_checks_pass": (
            orbit["n_failed"] == 0
            and all(orbit["checks"].values())
            and hessian["n_failed"] == 0
            and all(hessian["checks"].values())
            and c5c7["n_failed_integrity_checks"] == 0
            and all(c5c7["integrity_checks"].values())
            and degree4["n_failed_integrity_checks"] == 0
            and all(degree4["integrity_checks"].values())
            and moose["n_failed_integrity_checks"] == 0
            and all(moose["integrity_checks"].values())
        ),
        "V50_same_action_hash_is_preserved_only_as_reference": (
            result(v50, "E39")["value"]["shared_action_sha256"]
            == V50_SHARED_ACTION_SHA256
        ),
        "V51_candidate_has_no_same_action_identity": (
            "shared_action_sha256" not in moose
            and moose["candidate_contract"]["sites"] == 5
            and len(moose["field_content"]) > 0
        ),
        "source_orbit_and_Hessian_exact": (
            orbit["orbit_and_projector_certificate"]["selected_Gram"][
                "exact_rank"
            ]
            == 22
            and hessian["hessian_certificate"]["exact_rank_proof"][
                "exact_rank_H"
            ]
            == 443
            and hessian["hessian_certificate"]["Ward_identity"][
                "HQ_exact_zero_all_46_columns"
            ]
        ),
        "all_168_source_rows_have_multiplicity_and_factor_resolution": (
            c5c7["incidence_inventory"]["degree_two_or_three_rows_resolved_here"]
            == 48
            and d4["total_rows"] == 120
            and d4["zero_rows"] + d4["nonempty_rows"] == 120
            and d4["all_nonzero_copy_multiplicities_one"]
        ),
        "all_34_PS_primitives_are_chirality_correct": (
            c5c7["incidence_inventory"]["ps_total_primitive_declarations"] == 34
            and c5c7["integrity_checks"][
                "projected_PS_Yukawa_tensors_covariant"
            ]
            and c5c7["integrity_checks"][
                "mixed_tensor_reverse_orientation_rules_exact"
            ]
        ),
        "candidate_link_and_transport_local_theorems_pass": (
            moose["Clifford_locked_link"]["complex_rank_exact"] == 567
            and moose["Clifford_locked_link"]["complex_nullity_exact"] == 45
            and moose["rectangular_spinor_transport"][
                "total_chiral_profile_count"
            ]
            == 32
            and moose["rectangular_spinor_transport"][
                "additional_uncontrolled_transport_zero_modes"
            ]
            == 0
        ),
        "source_U1F_normalization_is_exactly_bound": (
            rxi["shared_U1F"]["primitive_Theta_charges"] == [3, -3]
            and rxi["shared_U1F"]["candidate_charge_norm_squared"] == 18
            and rxi["shared_U1F"]["source_orbit_norm_squared"] == 18
            and rxi["shared_U1F"]["candidate_source_normalization_matches"]
        ),
        "combined_endpoint_exposes_exactly_12_residual_chirals": (
            rxi["combined_host_PS_source_SU5"]["generator_partition"]
            == {
                "PS_intersection_SU5__SM": 12,
                "PS_only": 9,
                "SU5_only": 12,
                "neither": 12,
                "sum": 45,
            }
            and rxi["combined_host_PS_source_SU5"][
                "total_uneaten_A5_like_chirals"
            ]
            == 12
        ),
        "controlled_perturbative_candidate_is_killed": (
            not running["controlled_perturbative_window"]
            and running["interior_site"]["Landau_pole_over_link_scale"] < 1.70
            and running["source_site"]["Landau_pole_over_link_scale"] < 1.67
        ),
        "frontier_ledger_remains_three_of_seven": frontier_passed
        == ["C1", "C2", "C6"],
        "candidate_ledger_has_no_full_pass_or_promotion": (
            all(row["status"] != "pass" for row in candidate)
            and not moose["gate_effect"]["G2_closed"]
            and moose["gate_effect"]["gates_promoted"] == []
        ),
        "only_G1_is_closed": (
            [row["gate"] for row in gates if row["closed"]] == ["G1"]
        ),
    }
    failures = [name for name, passed in integrity.items() if not passed]
    if failures:
        raise RuntimeError("V51 integration integrity failure: " + ", ".join(failures))

    report: dict[str, Any] = {
        "schema": "susy-v51-new-physics-candidate-integration-audit-v1",
        "status": STATUS,
        "scientific_verdict": {
            "possible_solution_candidate": True,
            "complete_theory": False,
            "new_physics_discovery": False,
            "controlled_perturbative_UV_completion": False,
            "G2_closed": False,
            "full_gates_closed": 1,
            "closed_gates": ["G1"],
            "statement": (
                "V51 is a concrete and falsifiable representation-faithful route.  It solves "
                "the source-orbit/Hessian and invariant-factor subproblems, but its first "
                "polynomial moose realization fails perturbative UV control and contains 12 "
                "unlifted endpoint chirals.  It is not a completed or validated theory."
            ),
        },
        "candidate_architecture": {
            "name": "Clifford-locked PS-to-Spin(10) deconstructed source-mediator candidate",
            "definition": (
                "A finite 4D N=1 product-Spin(10) moose whose vector and spinor links are "
                "locked by covariant Clifford constraints, with a PS endpoint projector, "
                "the exact 210+126+bar126+singlet source action, rectangular chiral "
                "transport and vectorlike channel mediators."
            ),
            "rescue_hypotheses_not_constructed": [
                "a lean link realization with far smaller total Dynkin index",
                "a genuine strong/composite link sector reproducing the same local orbit",
            ],
        },
        "same_action_decision": {
            "V50_shared_action_sha256": V50_SHARED_ACTION_SHA256,
            "V51_shared_action_sha256": None,
            "equivalence_proved": False,
            "reason": (
                "V51 changes the microscopic U(1) topology and adds link, multiplier, "
                "transport and mediator fields.  Exact subblocks therefore cannot be combined "
                "with V50 clause passes as one action until an explicit matching identity exists."
            ),
        },
        "frozen_G2_contract": v50["frozen_G2_contract"],
        "V50_frontier_clause_assessment": frontier,
        "V50_frontier_fully_passed_clauses": frontier_passed,
        "V51_candidate_clause_assessment": candidate,
        "V51_exact_results": exact_results(orbit, hessian, c5c7, degree4, moose),
        "unresolved_defects": unresolved_defects(),
        "smallest_next_candidate_patch": [
            (
                "Construct one anomaly-safe local lifting interaction for the 12 residual "
                "A5-like chirals and recompute the complete host/source Hessian and Rxi pencil."
            ),
            (
                "Replace the high-index 567-multiplier link with a lean perturbative link, or "
                "supply a calculable strong/composite completion with the same exact orbit."
            ),
            (
                "Freeze one complete action hash, embed every factor/current, emit the physical "
                "Wilson array, and perform full one-loop DRbar threshold/scale matching."
            ),
        ],
        "gate_ledger": gates,
        "stage_ledger": updated_stage_ledger(v50),
        "input_core_hashes": {
            name: value["core_sha256"] for name, value in loaded.items()
        },
        "primary_sources": [
            {
                "title": "Arkani-Hamed, Cohen and Georgi: (De)constructing Dimensions",
                "url": "https://arxiv.org/abs/hep-th/0104005",
            },
            {
                "title": "Marti and Pomarol: Supersymmetric theories with compact extra dimensions in N=1 superfields",
                "url": "https://arxiv.org/abs/he-th/0106256",
            },
            {
                "title": "Hebecker: 5D super Yang-Mills in 4D superspace and brane operators",
                "url": "https://arxiv.org/abs/hep-ph/0112230",
            },
            {
                "title": "Nath and Syed: Couplings of SO(10) spinor and tensor representations",
                "url": "https://arxiv.org/abs/he-th/0109116",
            },
            {
                "title": "Aulakh and Girdhar: Minimal supersymmetric SO(10) spectra",
                "url": "https://arxiv.org/abs/hep-ph/0612021",
            },
            {
                "title": "Brignole: One-loop effective Kahler potential for chiral multiplets",
                "url": "https://arxiv.org/abs/1205.3492",
            },
        ],
        "integrity_checks": integrity,
        "n_failed_integrity_checks": 0,
        "source_manifest": source_manifest(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    exact = "\n".join(
        f"- **{row['id']} — {row['result']}:** {row['statement']}"
        for row in report["V51_exact_results"]
    )
    defects = "\n".join(
        f"- **{row['id']} — {row['defect']}:** {row['statement']}"
        for row in report["unresolved_defects"]
    )
    candidate = "\n".join(
        f"- `{row['id']}` — `{row['status']}`: {row['statement']}"
        for row in report["V51_candidate_clause_assessment"]
    )
    gates = "\n".join(
        f"- `{row['gate']}` — `{'closed' if row['closed'] else 'open'}`: "
        f"{row['advance']} Remaining: {row['blocker']}"
        for row in report["gate_ledger"]
    )
    patch = "\n".join(
        f"{index}. {value}"
        for index, value in enumerate(report["smallest_next_candidate_patch"], 1)
    )
    sources = "\n".join(
        f"- [{row['title']}]({row['url']})" for row in report["primary_sources"]
    )
    return f"""# V51 new-physics candidate integration audit

Status: `{report['status']}`

## Outcome

V51 is a **serious possible solution route**, not a completed theory.  It
solves the exact source-orbit/Hessian and invariant-factor subproblems, but the
first representation-faithful polynomial moose has 12 uneaten endpoint chirals
and a one-loop Spin(10) Landau window below 1.70 link scales.

**No G2 clause is promoted by V51.  G2 remains open.  Full gates closed: 1/8,
G1 only.**

## Candidate physics

{report['candidate_architecture']['definition']}

The two possible rescue directions are explicitly hypotheses, not results:
{'; '.join(report['candidate_architecture']['rescue_hypotheses_not_constructed'])}.

## Exact results

{exact}

## Same-action decision

{report['same_action_decision']['reason']}  The frozen V50 action hash is
`{report['same_action_decision']['V50_shared_action_sha256']}`; V51 has no
equivalent shared-action certificate.

## Candidate C1-C7 assessment

{candidate}

The historical V50 frontier remains `C1,C2,C6` passed for the V50 action only.

## Remaining defects

{defects}

## Smallest next patch

{patch}

## G1-G8 ledger

{gates}

## Primary sources

{sources}

Core SHA-256: `{report['core_sha256']}`
"""


def validate(report: Mapping[str, Any]) -> None:
    if report["status"] != STATUS:
        raise RuntimeError("status drifted")
    if report["core_sha256"] != canonical_sha(report):
        raise RuntimeError("canonical hash drifted")
    if report["n_failed_integrity_checks"] or not all(
        report["integrity_checks"].values()
    ):
        raise RuntimeError("integrity checks failed")
    if report["V50_frontier_fully_passed_clauses"] != ["C1", "C2", "C6"]:
        raise RuntimeError("V50 frontier clause ledger drifted")
    if any(
        row["status"] == "pass"
        for row in report["V51_candidate_clause_assessment"]
    ):
        raise RuntimeError("V51 candidate was overpromoted")
    if report["scientific_verdict"]["G2_closed"]:
        raise RuntimeError("G2 was overpromoted")
    if [row["gate"] for row in report["gate_ledger"] if row["closed"]] != ["G1"]:
        raise RuntimeError("full gate ledger drifted")


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
    expected_md = render_markdown(report)
    if not JSON_PATH.is_file() or JSON_PATH.read_text(encoding="utf-8") != expected_json:
        raise RuntimeError("V51 master JSON missing or stale; run --write")
    if not MD_PATH.is_file() or MD_PATH.read_text(encoding="utf-8") != expected_md:
        raise RuntimeError("V51 master Markdown missing or stale; run --write")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--print-json", action="store_true")
    args = parser.parse_args()
    if args.write:
        report = write_artifacts()
        print(report["status"])
        print(report["core_sha256"])
    if args.check:
        check_artifacts()
        print("V51_NEW_PHYSICS_CANDIDATE_INTEGRATION_AUDIT_CHECK_PASS")
    if args.print_json or (not args.write and not args.check):
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
