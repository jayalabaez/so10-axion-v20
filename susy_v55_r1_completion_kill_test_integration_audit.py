#!/usr/bin/env python3
"""Integrate the V55 R1 matter completion and symmetry-complete kill test.

The audit preserves the exact sparse Hessian as a conditional certificate, then
tests whether the terms omitted from that texture can be forbidden by additive
ordinary or R symmetries.  Results from inequivalent anomaly or flavour ledgers
are kept separate; no cross-action gate promotion is permitted.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V55_R1_COMPLETION_KILL_TEST_INTEGRATION_AUDIT.json"
MD_PATH = ROOT / "SUSY_V55_R1_COMPLETION_KILL_TEST_INTEGRATION_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v55_r1_completion_kill_test_integration_audit.py"

INPUTS = {
    "v54_master": ROOT / "SUSY_V54_THEORY_REDESIGN_INTEGRATION_AUDIT.json",
    "matter_hessian": ROOT / "SUSY_V55_R1_MATTER_HESSIAN_AUDIT.json",
    "matter_operator": ROOT / "SUSY_V55_R1_MATTER_OPERATOR_AUDIT.json",
    "selector_no_go": ROOT / "SUSY_V55_R1_RESIDUAL_SELECTOR_NO_GO_AUDIT.json",
    "proton_feasibility": ROOT / "SUSY_V55_R1_DEGREE9_PROTON_FEASIBILITY_AUDIT.json",
    "gs_matter_anomaly": ROOT / "SUSY_V55_R1_GS_MATTER_ANOMALY_AUDIT.json",
}

EXPECTED_CORES = {
    "v54_master": "3dabe44528f698e0c39fa69deb8e25c0ec990989495e63f85374b3a0a9487c8e",
    "matter_hessian": "efe7e8ba789ab93d12fbd4e478af4a91e8e670fe4361b4b4f9191a9e0eb6b098",
    "matter_operator": "895f999b53fcf7c4e513e0f9c6ee3245d166d8db8d3cfceaff3d9d8c2af25330",
    "selector_no_go": "4419949188586eb7ded9551f1cb11c683a672cb30b4ae65d482e6273ba3d7a19",
    "proton_feasibility": "6959457039b2828c1602e0e0e225b90a24da402260c24b39535a6c3783cbc665",
    "gs_matter_anomaly": "ac4c31629b1d5e862c9175f754488e7eea490418a981fd9636bee3ef9f6a3e7f",
}

STATUS = (
    "V55_R1_COMPLETION_KILL_TEST__SPARSE_280_COORDINATE_HESSIAN_EXACT_"
    "RANK197_NULL83__SYMMETRY_COMPLETION_FORCES_hAH2_AND_LhH2__GENERIC_"
    "RANK201_NULL79_WITH_ZERO_WEAK_HIGGS_MODES__ADDITIVE_SELECTOR_REPAIR_"
    "IMPOSSIBLE_AT_FIXED_TOPOLOGY__MIXED_FAMILY_DEGREE9_PROTON_CLASS_EXACT_"
    "BUT_NUMERIC_LIFETIME_UNDETERMINED__GS_BRANCHES_FORMAL_OR_INCOMPATIBLE__"
    "R1_REJECTED__ZERO_V55_GATE_CLOSURES__COMPLETE_THEORY_FALSE"
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
        raise RuntimeError(f"missing V55 input: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    actual = canonical_sha(value)
    if value.get("core_sha256") != actual:
        raise RuntimeError(f"stale canonical core: {path.name}")
    if actual != EXPECTED_CORES[name]:
        raise RuntimeError(f"unexpected upstream core: {path.name}")
    return value


def clause_ledger() -> list[dict[str, str]]:
    return [
        {
            "id": "C1",
            "status": "FAIL_OPERATOR_COMPLETENESS",
            "statement": (
                "The displayed R1 texture omits h A H2 and L h H2 even though every "
                "additive ordinary/R selector preserving the source and filter terms "
                "also preserves both fillers."
            ),
        },
        {
            "id": "C2",
            "status": "PARTIAL_SPARSE_ACTION_ONLY",
            "statement": (
                "A complete explicit sparse chiral superpotential exists, but its zero "
                "coefficients are not protected and therefore do not define the generic EFT."
            ),
        },
        {
            "id": "C3",
            "status": "FAIL_INTENDED_KERNEL_AFTER_COMPLETION",
            "statement": (
                "The exact sparse 280-coordinate Hessian has four weak modes; adding either "
                "forced filler raises the rank by four and leaves no weak-Higgs zero mode."
            ),
        },
        {
            "id": "C4",
            "status": "OPEN_GLOBAL_VACUUM",
            "statement": (
                "No physical GS modulus/vector sector, full D-flat solution, soft spectrum, "
                "global minimum, or tunnelling analysis is present."
            ),
        },
        {
            "id": "C5",
            "status": "OPEN_MATCHING",
            "statement": (
                "No one-action threshold calculation or frozen low-energy Wilson array has "
                "been derived."
            ),
        },
        {
            "id": "C6",
            "status": "FAIL_ONE_ACTION_GS_MATTER_COMPATIBILITY",
            "statement": (
                "The 133-singlet universal-family/RHN repair, the 128-singlet family-only "
                "repair, and the five-singlet differentiated-family repair belong to "
                "different ledgers and cannot be merged."
            ),
        },
        {
            "id": "C7",
            "status": "OPEN_PREDICTIVE_LIKELIHOOD",
            "statement": (
                "No current joint flavour, proton, collider, precision, or cosmological "
                "likelihood and withheld prediction exists."
            ),
        },
    ]


def gate_ledger() -> list[dict[str, Any]]:
    decisions = {
        "G1": (
            "The frozen historical ordinary-Spin quotient/anomaly lemma is retained only in "
            "its old namespace; no physical GS/global quotient exists for R1."
        ),
        "G2": "The C1-C7 same-action conjunction fails.",
        "G3": (
            "The sparse local Hessian is exact, but the symmetry-complete R1 action has the "
            "wrong kernel and lacks the GS/global vacuum sector."
        ),
        "G4": (
            "FAILED for R1: forced renormalizable h A H2 and L h H2 terms generically lift "
            "all four weak-Higgs zero modes."
        ),
        "G5": "No dark-sector or cosmological action and likelihood exists.",
        "G6": (
            "The matter-extended one-loop Spin(10) coefficient is recorded, but complete "
            "thresholds and two-loop running are absent."
        ),
        "G7": (
            "A genuine mixed-family degree-nine proton class exists; it can be numerically "
            "suppressed, but its matched Wilson coefficient and lifetime are unknown."
        ),
        "G8": (
            "Universal charges do not protect flavour textures; differentiated bounded "
            "survivors have no compatible completed GS/matter action or current global fit."
        ),
    }
    return [
        {
            "gate": f"G{i}",
            "closed": i == 1,
            "V55_candidate_closed": False,
            "scope": "frozen ordinary-Spin namespace only" if i == 1 else "V55 R1",
            "decision": decisions[f"G{i}"],
        }
        for i in range(1, 9)
    ]


def source_manifest() -> list[dict[str, Any]]:
    paths = [Path(__file__), TEST_PATH, *INPUTS.values()]
    return [
        {"path": path.name, "exists": path.is_file(), "sha256": sha256_file(path)}
        for path in paths
    ]


def build_report() -> dict[str, Any]:
    inputs = {name: load_bound(name, path) for name, path in INPUTS.items()}
    v54 = inputs["v54_master"]
    matter = inputs["matter_hessian"]
    operators = inputs["matter_operator"]
    selector = inputs["selector_no_go"]
    proton = inputs["proton_feasibility"]
    gs = inputs["gs_matter_anomaly"]

    sparse = matter["local_matter_hessian_certificate"]
    sparse_gs = matter["single_GS_repaired_action"]
    charges = matter["charges_action_and_operator_screen"]
    filler = selector["source_filter_filler_theorem"]
    tensor = operators["Spin10_center_and_tensor_audit"]
    search = operators["bounded_integer_family_charge_search"]
    anomaly_reaudit = operators["family_dependent_anomaly_reaudit"]
    formal_gs = gs["selected_formal_repair"]
    reference_slice = proton["benchmark_slices"][0]

    filler_rank_increment = filler["weak_rank_after"] - filler["weak_rank_before"]
    completed_rank = sparse["hessian_rank"] + filler_rank_increment
    completed_nullity = sparse["hessian_nullity"] - filler_rank_increment

    clauses = clause_ledger()
    gates = gate_ledger()

    integration_checks = {
        "all_input_cores_are_canonical_and_expected": all(
            inputs[name]["core_sha256"] == expected
            for name, expected in EXPECTED_CORES.items()
        ),
        "V54_promoted_no_candidate_gate": (
            v54["final_decision"]["full_gates_closed_for_V54_candidate"] == 0
        ),
        "sparse_matter_hessian_is_exact_280_rank197_null83": (
            sparse["coordinates"] == 280
            and sparse["hessian_rank"] == 197
            and sparse["hessian_nullity"] == 83
            and sparse["kernel_exact"]
            and sparse["kernel_decomposition"]
            == {
                "Spin10_gauge": 33,
                "U1_gauge": 1,
                "extra": 0,
                "light_matter": 45,
                "weak_Higgs": 4,
            }
        ),
        "universal_charge_matrices_are_not_texture_protected": (
            not charges["declared_sparse_texture"]["protected_by_U1"]
            and "every entry" in charges["symmetry_complete_flavor_statement"]
        ),
        "additive_selector_theorem_forces_both_fillers": (
            filler["forced_operators"]
            == ["h_10 A45 H2_10", "L h_10 H2_10"]
            and filler["renormalizable"]
            and filler["weak_Higgs_nullity_after"] == 0
        ),
        "symmetry_complete_blockwise_rank_consequence_is_201_null79": (
            filler_rank_increment == 4
            and completed_rank == 201
            and completed_nullity == 79
            and 34 + 45 == completed_nullity
        ),
        "exact_tensor_correction_keeps_only_six_mixed_F4_patterns": (
            tensor["single_family_F_i_fourth_power_is_absent"]
            and tensor["three_plus_one_family_pattern_is_absent"]
            and tensor["total_family_invariants"] == 6
            and tensor["gauge_valid_patterns"]
            == [
                [2, 2, 0],
                [2, 0, 2],
                [0, 2, 2],
                [2, 1, 1],
                [1, 2, 1],
                [1, 1, 2],
            ]
        ),
        "differentiated_family_survivors_break_fixed_GS_repair": (
            search["accepted_strict_monotone_count"] == 178
            and anomaly_reaudit[
                "accepted_differentiated_candidates_preserve_fixed_GS_repair"
            ]
            == 0
        ),
        "formal_five_singlet_GS_branch_is_not_physical_completion": (
            formal_gs["mass_certificate"]["Hessian_rank"] == 5
            and formal_gs["anomalies"]["family_charges"] == ["-2", "1", "11"]
            and not gs["verdict"]["physical_GS_completion_complete"]
        ),
        "degree9_proton_class_is_neither_fatal_nor_safe_without_matching": (
            not proton["decision"]["degree9_operator_is_automatically_fatal"]
            and not proton["decision"]["degree9_operator_is_proved_safe"]
            and not proton["decision"]["G7_closed"]
        ),
        "no_completion_clause_passes": all(
            not row["status"].startswith("PASS") for row in clauses
        ),
        "no_V55_candidate_gate_is_closed": not any(
            row["V55_candidate_closed"] for row in gates
        ),
        "only_frozen_G1_is_cumulatively_retained": [
            row["gate"] for row in gates if row["closed"]
        ]
        == ["G1"],
    }

    report: dict[str, Any] = {
        "schema": "susy-v55-r1-completion-kill-test-integration-audit-v1",
        "status": STATUS,
        "input_core_hashes": {
            name: inputs[name]["core_sha256"] for name in INPUTS
        },
        "expected_input_core_hashes": EXPECTED_CORES,
        "same_action_rule": (
            "A gate closes only if all hypotheses are proved in one canonical action. "
            "Sparse-Hessian, differentiated-flavour, and formal-GS certificates from "
            "different charge or field ledgers may not be assembled into one theory."
        ),
        "revision_of_V54": {
            "preserved_result": (
                "The V54 charged-source sparse Hessian and its V55 matter extension are "
                "algebraically valid for the displayed coefficient texture."
            ),
            "withdrawn_classification": (
                "R1_CONTINUOUS_PARENT_FI is no longer an executable frontier candidate; "
                "it is a rejected fixed-topology texture."
            ),
            "reason": (
                "The zero coefficients of h A H2 and L h H2 cannot be protected by any "
                "product of additive Abelian ordinary/R selectors that retains the required "
                "source and filter terms."
            ),
            "prior_gate_reversal": False,
            "why_no_gate_reversal": "V54 itself closed zero candidate gates.",
        },
        "sparse_matter_completion": {
            "family_charges": [11, 11, 11],
            "RH_neutrino_charges": [-10, -10, -10],
            "displayed_terms": [
                "F_i F_j H1",
                "F_i barC N_j",
                "(P^2 R^2/M_*^3) N_i N_j",
            ],
            "all_displayed_terms_neutral": charges["all_displayed_terms_neutral"],
            "coordinates": sparse["coordinates"],
            "H_rank": sparse["hessian_rank"],
            "H_nullity": sparse["hessian_nullity"],
            "Q_rank": sparse["gauge_orbit_rank"],
            "kernel_decomposition": sparse["kernel_decomposition"],
            "matter_block": {
                "coordinates": sparse["matter_block_coordinates"],
                "rank": sparse["matter_block_rank"],
                "nullity": sparse["matter_block_nullity"],
                "heavy_RHN_determinant_identity": sparse["heavy_RHN_subblock"][
                    "determinant_identity"
                ],
            },
            "texture_protected_by_U1": charges["declared_sparse_texture"][
                "protected_by_U1"
            ],
            "symmetry_complete_flavor_statement": charges[
                "symmetry_complete_flavor_statement"
            ],
            "conditional_GS_singlet_extension": {
                "coordinates": sparse_gs["coordinates"],
                "H_rank": sparse_gs["hessian_rank"],
                "H_nullity": sparse_gs["hessian_nullity"],
                "spectator_count": sparse_gs["spectators"]["coordinate_count"],
                "scope": (
                    "exact for the universal-family plus three-RHN ledger; no physical "
                    "GS modulus, Kahler potential, or string embedding"
                ),
            },
        },
        "symmetry_completion_kill_test": {
            "theorem_scope": filler["scope"],
            "required_terms": filler["required_terms"],
            "forced_operators": filler["forced_operators"],
            "exact_derivation": filler["exact_derivation_mod_N"],
            "actual_charge_arithmetic": filler["actual_charge_arithmetic"],
            "removing_L_alone_is_sufficient": False,
            "A_weak_block_coefficient": filler["A_weak_block_coefficient"],
            "one_weak_component_determinant": filler[
                "one_weak_component_determinant_with_h_A_H2_coefficient_x"
            ],
            "one_weak_component_actual_determinant": filler[
                "one_weak_component_determinant_at_actual_A_weak_coefficient"
            ],
            "weak_rank_before": filler["weak_rank_before"],
            "weak_rank_after": filler["weak_rank_after"],
            "weak_Higgs_nullity_after": filler["weak_Higgs_nullity_after"],
            "generic_symmetry_complete_280_coordinate_consequence": {
                "derivation": (
                    "At the zero-matter vacuum the forced filler acts in the existing "
                    "h/A/H2 weak block and spans the four sparse weak null directions. "
                    "Its exact rank increment therefore adds to the bound sparse Hessian."
                ),
                "coordinates": sparse["coordinates"],
                "H_rank": completed_rank,
                "H_nullity": completed_nullity,
                "kernel_decomposition": {
                    "Spin10_gauge": 33,
                    "U1_gauge": 1,
                    "light_matter": 45,
                    "weak_Higgs": 0,
                    "extra": 0,
                },
                "coefficient_scope": (
                    "generic nonzero allowed coefficient; an accidental tuned zero is not "
                    "a symmetry protection and is radiatively unstable"
                ),
            },
            "fixed_topology_additive_selector_rescue_exists": False,
            "G4_result": "FAILED_FOR_R1",
        },
        "matter_tensor_and_family_results": {
            "exact_D5_tensor_correction": {
                "same_family_Fi4_absent": tensor[
                    "single_family_F_i_fourth_power_is_absent"
                ],
                "three_plus_one_absent": tensor[
                    "three_plus_one_family_pattern_is_absent"
                ],
                "genuine_mixed_patterns": tensor["gauge_valid_patterns"],
                "multiplicity_each": tensor["valid_pattern_multiplicities"],
            },
            "universal_family_problem": (
                "U1 permits every symmetric Yukawa, RHN-link, and Majorana entry; the "
                "displayed sparse matrices are coefficient choices rather than symmetry "
                "textures."
            ),
            "half_integer_low_degree_search": {
                "strict_solution_count": matter["family_charge_search"][
                    "strict_solution_count"
                ],
                "safe_through_total_degree": 8,
                "nearest_candidate_charges": matter["family_charge_search"][
                    "nearest_top_only_candidate"
                ]["qF"],
                "nearest_candidate_first_F4_total_degree": matter[
                    "family_charge_search"
                ]["nearest_top_only_candidate"]["first_F4_dressing"]["total_degree"],
            },
            "broader_integer_proxy_search": {
                "triples_scanned": search["scanned_charge_triples"],
                "hierarchical_proxy_survivors": search[
                    "accepted_hierarchical_proxy_count"
                ],
                "strict_monotone_survivors": search[
                    "accepted_strict_monotone_count"
                ],
                "maximum_first_proton_dressing_insertions": search[
                    "maximum_proton_dressing_insertions_in_strict_proxy"
                ],
                "lowest_charge_strict_example": anomaly_reaudit[
                    "strict_best_lowest_charge_example"
                ]["charges"],
                "fixed_GS_repair_survivors": anomaly_reaudit[
                    "accepted_differentiated_candidates_preserve_fixed_GS_repair"
                ],
            },
            "residual_direct_Yukawa_theorem": selector["theorem"],
        },
        "anomaly_branch_ledger": [
            {
                "id": "A1_UNIVERSAL_MATTER_PLUS_RHN",
                "family_charges": [11, 11, 11],
                "RH_neutrinos_included": True,
                "spectator_count": sparse_gs["spectators"]["coordinate_count"],
                "exact_massive_spectator_Hessian": True,
                "physical_GS_completion": False,
                "fatal_other_issue": "forced Higgs filler and unprotected flavour",
            },
            {
                "id": "A2_Q11_FAMILY_ONLY_REDUCED_REPAIR",
                "family_charges": [11, 11, 11],
                "RH_neutrinos_included": False,
                "spectator_count": gs["fixed_q11_repair_reduction"][
                    "smaller_128_singlet_repair"
                ]["anomalies"]["spectator_count"],
                "exact_massive_spectator_Hessian": True,
                "physical_GS_completion": False,
                "cross_action_warning": (
                    "This 128-field arithmetic ledger omits the three N_i charges and cannot "
                    "replace the 133-field repair in A1."
                ),
            },
            {
                "id": "A3_DIFFERENTIATED_FORMAL_REPAIR",
                "family_charges": formal_gs["family_charges"],
                "RH_neutrinos_included": False,
                "spectator_count": formal_gs["anomalies"]["spectator_count"],
                "spectator_charges": formal_gs["spectator_charges"],
                "spectator_H_rank": formal_gs["mass_certificate"]["Hessian_rank"],
                "anomalies": {
                    "A10": formal_gs["anomalies"]["Spin10_squared_U1"],
                    "TrQ": formal_gs["anomalies"]["TrQ"],
                    "TrQ3": formal_gs["anomalies"]["TrQ3"],
                    "kA": formal_gs["anomalies"]["kA_from_cubic_universality"],
                },
                "physical_GS_completion": False,
                "cross_action_warning": (
                    "No complete RHN/flavour action or full matter-extended Hessian uses "
                    "this charge ledger."
                ),
            },
        ],
        "proton_feasibility": {
            "operator": proton["operator_matching"]["UV_operator"],
            "total_degree": proton["operator_matching"]["total_degree"],
            "effective_scale": proton["operator_matching"]["effective_scale"],
            "testable_inequality": proton["operator_matching"]["testable_inequality"],
            "experimental_mode": proton["experimental_input"]["mode"],
            "experimental_lower_limit_yr": proton["experimental_input"][
                "partial_lifetime_lower_limit_yr_90CL"
            ],
            "published_reference_required_Meff_over_kappa_GeV": reference_slice[
                "required_Meff_over_abs_kappa_GeV"
            ],
            "published_reference_maximum_c_kappa_eta": reference_slice[
                "maximum_abs_c_times_kappa_times_xS4_xR"
            ],
            "automatically_fatal": proton["decision"][
                "degree9_operator_is_automatically_fatal"
            ],
            "proved_safe": proton["decision"]["degree9_operator_is_proved_safe"],
            "G7_closed": proton["decision"]["G7_closed"],
            "boundary": proton["decision"]["reason"],
        },
        "V55_candidate_clause_ledger": clauses,
        "gate_ledger": gates,
        "hard_next_architecture_obligations": [
            {
                "id": "N1_CHANGE_SOURCE_FILTER_TOPOLOGY",
                "requirement": (
                    "Break at least one exact equality behind q(A)=q(B)=q(L), for example by "
                    "changing the MA^2/MAB source pair or the barC A C/L barC C pair. Merely "
                    "removing L is insufficient because h A H2 remains forced."
                ),
            },
            {
                "id": "N2_PROTECT_THE_FILTER",
                "requirement": (
                    "Supply an exact non-Abelian, locality, mediator, or representation-level "
                    "selection rule that allows the desired filter chain while forbidding "
                    "every rank-lifting Higgs filler."
                ),
            },
            {
                "id": "N3_RECOMPUTE_FULL_GEOMETRY",
                "requirement": (
                    "For the changed action solve F and D and recompute the complete Hessian "
                    "and gauge-orbit quotient; the kernel must be exactly 34 gauge, 45 light "
                    "matter, and four weak-Higgs directions before soft breaking."
                ),
            },
            {
                "id": "N4_ONE_ACTION_MATTER_GS_OPERATORS",
                "requirement": (
                    "Embed realistic Yukawa/RHN textures, the physical GS modulus/vector and "
                    "a complete tensor/operator census in that same action."
                ),
            },
            {
                "id": "N5_MATCH_AND_TEST",
                "requirement": (
                    "Derive thresholds and Wilson tensors, perform current flavour/proton "
                    "likelihoods, and add SUSY breaking, EWSB, global-vacuum and cosmological "
                    "tests before any gate promotion."
                ),
            },
        ],
        "final_decision": {
            "bounded_V55_R1_analysis_finished": True,
            "R1_fixed_topology_rejected": True,
            "same_action_completion": False,
            "complete_theory": False,
            "empirical_new_physics_discovery": False,
            "selected_complete_candidate": None,
            "selected_executable_frontier_candidate": None,
            "V55_candidate_closed_gates": [],
            "full_gates_closed_for_V55_candidate": 0,
            "cumulative_reusable_closed_gates": ["G1"],
            "next_redesign_trigger": (
                "Start V56 only from a changed source/filter topology; parameter changes or "
                "additional additive Abelian selectors cannot rescue R1."
            ),
            "honest_outcome": (
                "V55 completes the bounded R1 kill test. It preserves an exact conditional "
                "matter Hessian and finds useful tensor, anomaly, and proton results, but "
                "proves that the fixed R1 topology cannot naturally retain the MSSM Higgs "
                "pair. R1 is rejected and no complete theory exists."
            ),
        },
        "verification_run": {
            "date": "2026-08-29",
            "python_compile": {"V55_scripts": 6, "passed": True},
            "focused_V55_pytest": {
                "passed": 69,
                "failed": 0,
                "scope": "all six V55 component and integration test modules",
            },
            "historical_pytest": {
                "passed": 766,
                "failed": 0,
                "scope": "all test_susy_v40 through test_susy_v55 modules",
            },
            "supported_artifact_freshness_checks_passed": True,
        },
        "primary_sources": [
            {
                "title": (
                    "Constraining Proton Lifetime in SO(10) with Stabilized "
                    "Doublet-Triplet Splitting"
                ),
                "url": "https://arxiv.org/abs/1003.2625",
                "use": "reference proton-lifetime scaling only",
            },
            {
                "title": (
                    "Search for proton decay via p to anti-neutrino K+ using 260 kiloton-year "
                    "data of Super-Kamiokande"
                ),
                "url": "https://arxiv.org/abs/1408.1195",
                "use": "experimental p to anti-neutrino K+ lower limit",
            },
            {
                "title": "The Green-Schwarz mechanism in heterotic orbifolds",
                "url": "https://arxiv.org/abs/1110.6901",
                "use": "single anomalous-U1 universality and FI conventions",
            },
        ],
        "integrity_checks": integration_checks,
        "n_failed_integrity_checks": sum(
            not value for value in integration_checks.values()
        ),
        "source_manifest": source_manifest(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report["status"] != STATUS or report["core_sha256"] != canonical_sha(report):
        raise RuntimeError("V55 integration status or core drift")
    if report["n_failed_integrity_checks"] or not all(
        report["integrity_checks"].values()
    ):
        raise RuntimeError("V55 integration integrity failure")
    decision = report["final_decision"]
    if not decision["R1_fixed_topology_rejected"]:
        raise RuntimeError("R1 rejection was lost")
    if decision["complete_theory"] or decision["same_action_completion"]:
        raise RuntimeError("V55 completion was overclaimed")
    if decision["V55_candidate_closed_gates"]:
        raise RuntimeError("V55 candidate gate was overpromoted")


def render_markdown(report: Mapping[str, Any]) -> str:
    sparse = report["sparse_matter_completion"]
    kill = report["symmetry_completion_kill_test"]
    complete = kill["generic_symmetry_complete_280_coordinate_consequence"]
    matter = report["matter_tensor_and_family_results"]
    anomaly = {row["id"]: row for row in report["anomaly_branch_ledger"]}
    proton = report["proton_feasibility"]
    return f"""# V55 R1 completion kill-test integration audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Decision

{report['final_decision']['honest_outcome']}

The fixed R1 topology is rejected. The V55 candidate closes `0/8` gates. The
only cumulative closed gate remains the frozen historical `G1` lemma in its old
ordinary-Spin namespace; it is not a V55 closure. No empirical discovery is
claimed.

## Exact correction to V54

The sparse matter-extended action has `{sparse['coordinates']}` complex
coordinates, Hessian rank `{sparse['H_rank']}`, nullity `{sparse['H_nullity']}`
and gauge-orbit rank `{sparse['Q_rank']}`. Its kernel is exactly 34 gauge + 45
light-matter + 4 weak-Higgs directions. This algebra is preserved.

It is not symmetry-complete. The required terms `{', '.join(kill['required_terms'])}`
imply `q(A)=q(B)=q(L)` factor by factor for every additive ordinary or R symmetry.
Therefore every such selector that keeps `h B H2` also keeps both
`h A H2` and `L h H2`. Removing `L` alone does not solve the problem.

For one weak component the `h A H2` determinant is `{kill['one_weak_component_determinant']}`;
the actual A coefficient is `{kill['A_weak_block_coefficient']}`, giving determinant
`{kill['one_weak_component_actual_determinant']}`. The weak rank rises from
`{kill['weak_rank_before']}` to `{kill['weak_rank_after']}`. Hence the generic
symmetry-complete `{complete['coordinates']}`-coordinate Hessian has derived exact
rank `{complete['H_rank']}` and nullity `{complete['H_nullity']}` = 34 gauge + 45
light matter, with zero weak-Higgs modes. An accidental zero Wilson coefficient
would be an unprotected tuning, not a theory-level solution.

## Matter, tensor, and proton results

The universal charges `q(F_i)=11`, `q(N_i)=-10` make all displayed Yukawa,
RH-neutrino link, and Majorana terms neutral and give a 51-coordinate matter
block of rank 6/nullity 45. They also permit every matrix entry, so the sparse
flavour texture is not symmetry-protected.

The exact D5 character calculation corrects an earlier proxy: same-family
`F_i^4` and `F_i^3 F_j` singlets are absent. Six mixed-family patterns remain,
all with multiplicity one: `{matter['exact_D5_tensor_correction']['genuine_mixed_patterns']}`.
For universal charges this includes the exact total-degree-nine class
`{proton['operator']}`.

The operator is not automatically fatal and is not proved safe. With the 2010
reference scaling, the current lifetime input requires
`M_eff/|kappa| = {proton['published_reference_required_Meff_over_kappa_GeV']:.6e} GeV`,
or `|c kappa| xS^4 xR < {proton['published_reference_maximum_c_kappa_eta']:.6g}`
at the recorded cutoff. Physical VEV ratios, coefficients, flavour rotations,
triplet matching, SUSY dressing and spectrum are not fixed, so `G7` stays open.

## Anomaly branches are not interchangeable

- The universal-family plus three-RHN sparse ledger has an exact
  `{anomaly['A1_UNIVERSAL_MATTER_PLUS_RHN']['spectator_count']}`-singlet formal
  repair, but no physical GS modulus/Kahler/string completion and the Higgs
  filler remains fatal.
- A smaller `{anomaly['A2_Q11_FAMILY_ONLY_REDUCED_REPAIR']['spectator_count']}`-field
  repair is exact only for a family-only ledger that omits the three RHNs.
- The differentiated `{anomaly['A3_DIFFERENTIATED_FORMAL_REPAIR']['family_charges']}`
  branch uses five massive spectators and exact formal anomalies, but it has no
  completed RHN/flavour action or full matter Hessian.

These certificates cannot be combined. The broader family scan finds 178
strict proxy survivors, but zero preserves the fixed universal-family GS repair.

## Verification

All six V55 scripts compile. The focused V55 suite passes
`{report['verification_run']['focused_V55_pytest']['passed']}/69` tests. The full
V40-V55 regression passes `{report['verification_run']['historical_pytest']['passed']}/766`
tests, and all supported freshness checks pass.

## Required redesign

The next architecture must change the source/filter topology so the equations
forcing `q(A)=q(B)=q(L)` no longer hold, or use a genuine non-Abelian,
representation, locality, or mediator selection rule. Only after that change is
it meaningful to recompute the full vacuum/Hessian and add one-action flavour,
GS, operator, threshold, proton, soft, and cosmological sectors.
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
        raise RuntimeError("stale V55 integration JSON")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("stale V55 integration Markdown")


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
        print("V55_R1_COMPLETION_KILL_TEST_INTEGRATION_AUDIT_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
