#!/usr/bin/env python3
"""V64 multipath master: retract only V63 route B and fail closed.

This master binds the stable V63 multipath master and the stable V64 exact
AB-tower null-mode audit.  Routes A60 and C are copied unchanged and may not
be spliced into route B.  Only the V63 route-B claims that the twelve Q-type
Goldstone chirals dissolve, that their (-2,-3) ledger forces a WZ term, and
that the same rank VEV fixes the X/Y scale are superseded.

The corrected current Spin(11) action contains twelve normalizable colored
chiral components.  Its physical infrared ledger is (A3,A2)=(1,-2), already
equal to the V62 pre-VEV wall sum, so no WZ functional is forced.  The V61
selector result is retained as arithmetic only and the V62 localized ledger
is retained only in its pre-VEV, Lie-algebra-level scope.  Every G1--G8 gate
remains OPEN and the current Spin(11) action is rejected pending an explicit
repair satisfying R1--R5.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V64_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
MD_PATH = ROOT / "SUSY_V64_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v64_multipath_g1_frontier_master_audit.py"

V63_MASTER_PATH = ROOT / "SUSY_V63_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V64_ROUTE_PATH = ROOT / "SUSY_V64_SPIN11_AB_TOWER_NULL_MODE_RETRACTION_AUDIT.json"

EXPECTED_V63_MASTER_CORE = (
    "89a16112997c2e0fb8439209b4c17e160f165c20b846697ee7da4a93cc22f3e3"
)
EXPECTED_V64_ROUTE_CORE = (
    "fe36b2f6f0e1786253827183bf7f8dc2dd9e15a94b7f036d5e9e6e0739717a1d"
)
EXPECTED_A60_CORE = (
    "096537e4701bea02c8d6a3563adfd24b4247c90a8258621eef6c2ce801991ecd"
)
EXPECTED_C_CORE = (
    "27b4e032ff10065b534c1c62c2adf88f677b07c228f243b5376227fdb307ac8d"
)

STATUS = (
    "V64_MULTIPATH_G1_FRONTIER_MASTER__V63_MASTER_AND_STABLE_V64_ROUTE_CORE_"
    "BOUND__ONLY_ROUTE_B63_SUPERSEDED_BY_B64__TWELVE_NORMALIZABLE_Q_TYPE_"
    "COLORED_CHIRAL_COMPONENTS_SURVIVE__ACTUAL_IR_LEDGER_1_MINUS2__NO_WZ_"
    "FORCED__V63_XY_NOTE_WITHDRAWN__CURRENT_SPIN11_ACTION_REJECTED__V61_"
    "SELECTOR_ARITHMETIC_AND_V62_PRE_VEV_LEDGER_CONDITIONAL_ONLY__A60_AND_C_"
    "UNCHANGED__NO_CROSS_ROUTE_SPLICING__G1_TO_G8_OPEN__ZERO_PROMOTIONS"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha(value: Mapping[str, Any], core_key: str = "core_sha256") -> str:
    body = copy.deepcopy(dict(value))
    body.pop(core_key, None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def load_bound(path: Path, expected_core: str, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"missing {label}: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    stored = value.get("core_sha256")
    actual = canonical_sha(value)
    if stored != actual:
        raise RuntimeError(f"stale canonical core for {label}: {path.name}")
    if actual != expected_core:
        raise RuntimeError(f"unexpected stable core for {label}: {actual}")
    return value


def route_by_id(master: Mapping[str, Any], route_id: str) -> dict[str, Any]:
    matches = [
        copy.deepcopy(row)
        for row in master["route_matrix"]
        if row["route_id"] == route_id
    ]
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one route {route_id}, got {len(matches)}")
    return matches[0]


def retraction_by_prefix(
    v64_route: Mapping[str, Any], prefix: str
) -> dict[str, Any]:
    matches = [
        copy.deepcopy(row)
        for row in v64_route["retraction_ledger"]
        if row["prior_claim"].startswith(prefix)
    ]
    if len(matches) != 1:
        raise RuntimeError(f"expected one V64 retraction beginning {prefix!r}")
    return matches[0]


def route_b64(
    v64_route: Mapping[str, Any], prior_b63: Mapping[str, Any]
) -> dict[str, Any]:
    ledger = v64_route["corrected_post_VEV_anomaly_ledger"]
    terminal = v64_route["terminal_decision"]
    representation = v64_route["representation_and_primary_source_correction"]
    return {
        "route_id": "B64",
        "name": (
            "Spin(11) gauge-Higgs route after exact AB-tower null-mode "
            "retraction audit"
        ),
        "bound_core_sha256": v64_route["core_sha256"],
        "classification": v64_route["classification"],
        "supersedes_V63_route_id": prior_b63["route_id"],
        "superseded_V63_route_core": prior_b63["bound_core_sha256"],
        "supersession_scope": (
            "only V63 route B: Goldstone dissolution, forced WZ inflow, and "
            "the rank-VEV-shifted X/Y note"
        ),
        "exact_light_spectrum": {
            "normalizable_Q_type_complex_chiral_components": ledger[
                "surviving_sector"
            ]["complex_chiral_components"],
            "irreps": ledger["surviving_sector"]["irreps"],
            "finite_operator_shape": v64_route["finite_KK_mass_operator"][
                "per_complex_Q_direction"
            ]["shape"],
            "right_nullity_per_complex_direction": 1,
            "infinite_kernel_normalizable": v64_route[
                "infinite_normalizable_null_mode"
            ]["norm_finite_for_every_finite_alpha"],
        },
        "corrected_post_VEV_ledger": {
            "MSSM_only": ledger["MSSM_only_ledger_from_V61"],
            "surviving_Q_type": ledger["surviving_sector"]["mixed_R_anomaly"],
            "actual_IR": ledger["actual_IR_ledger_MSSM_plus_exotics"],
            "V62_pre_VEV_wall_sum": ledger["V62_orbifold_wall_sum"],
            "both_match_without_WZ": ledger["matching_identities"][
                "both_close_without_WZ"
            ],
        },
        "WZ_status": {
            "V63_forced_WZ_claim_valid": terminal["V63_forced_WZ_claim_valid"],
            "functional_for_this_matching": ledger[
                "WZ_functional_for_this_matching"
            ],
            "double_counting_forbidden_while_exotics_are_light": True,
        },
        "V63_XY_note": representation["V63_XY_claim"],
        "conditional_preservations": {
            "V61_selector": "PRESERVED_AS_ARITHMETIC_ONLY",
            "V62_pre_VEV_ledger": "PRESERVED_CONDITIONALLY",
        },
        "repair_acceptance_criteria": copy.deepcopy(
            v64_route["repair_acceptance_criteria"]
        ),
        "current_action_accepted": terminal["current_Spin11_action_accepted"],
        "same_action_microscopic_completion": False,
        "G1_closed": terminal["V64_G1_closed"],
        "closed_gates": [],
    }


def conditional_preservations(v64_route: Mapping[str, Any]) -> dict[str, Any]:
    selector = retraction_by_prefix(v64_route, "V61:")
    localized = retraction_by_prefix(v64_route, "V62:")
    return {
        "V61_selector_arithmetic": {
            "status": selector["V64_status"],
            "preserved_claim": selector["prior_claim"],
            "scope": selector["reason"],
            "not_a_physical_IR_spectrum_certificate": True,
        },
        "V62_pre_VEV_localized_ledger": {
            "status": localized["V64_status"],
            "preserved_claim": localized["prior_claim"],
            "scope": localized["reason"],
            "post_VEV_MSSM_only_interpretation_rejected": True,
            "large_gauge_and_Dai_Freed_completion_still_open": True,
        },
    }


def discrete_coefficient_scope(v64_route: Mapping[str, Any]) -> dict[str, Any]:
    anomaly = v64_route["corrected_post_VEV_anomaly_ledger"][
        "surviving_sector"
    ]["mixed_R_anomaly"]
    return {
        "symmetry": "Z4R",
        "eta_for_even_N": 2,
        "half_index_convention": {
            "Delta_A3": anomaly["Delta_A3"],
            "Delta_A2": anomaly["Delta_A2"],
            "residues_mod_eta": {"SU3": 0, "SU2_L": 1},
        },
        "integer_index_convention_2A": {
            "Delta_a3": -4,
            "Delta_a2": -6,
            "residues_mod4": {"SU3": 0, "SU2_L": 2},
        },
        "exact_integer_WZ_coefficients_fixed_by_discrete_congruence": False,
        "continuous_U1R_lift_and_regulator_specified": False,
        "interpretation": (
            "the discrete anomaly fixes only residue classes; while the "
            "Q-type chirals are light, their determinant carries those residues "
            "and assigning the same ledger to WZ would double-count"
        ),
    }


def downgraded_theory_card(
    v63_master: Mapping[str, Any], v64_route: Mapping[str, Any]
) -> dict[str, Any]:
    prior = v63_master["consolidated_theory_card"]
    active_inventory = [
        item for item in prior["action_inventory"] if "Wess-Zumino" not in item
    ]
    return {
        "name": (
            "downgraded 5D SUSY Spin(11) repair candidate on "
            "S1/(Z2xZ2')"
        ),
        "standing": "CURRENT_ACTION_REJECTED__REPAIR_CANDIDATE_ONLY",
        "candidate_action_accepted": False,
        "complete_theory": False,
        "active_action_inventory": active_inventory,
        "excluded_from_active_action": [
            "the V63 anomaly-forced (-2,-3) Goldstone Wess-Zumino term",
            "the V63 assertion that the rank VEV shifts the X/Y proton scale",
        ],
        "certified_scoped_results": [
            "the V61 exhaustive selector scan remains an arithmetic charge-classification result",
            "the V62 fixed-plane projector trace remains a conditional pre-VEV localized ledger",
            "the gauge-adjoint projector still supplies two weak Higgs zero modes",
            "the current rank-sector 5+5bar pairing result is not promoted to a complete-spectrum certificate",
            "V64 exactly proves one normalizable Q-type chiral kernel per complex affected direction",
            "twelve Q-type complex chiral components survive in total",
            "their (-2,-3) anomaly makes the actual IR ledger (1,-2), equal to the V62 wall sum without WZ",
        ],
        "exact_blocker": v64_route["terminal_decision"]["exact_blocker"],
        "repair_acceptance_criteria": copy.deepcopy(
            v64_route["repair_acceptance_criteria"]
        ),
        "remaining_obligations": copy.deepcopy(
            v64_route["remaining_obligations"]
        ),
        "honesty_clause": (
            "this is a rejected current action and a fail-closed repair card, "
            "not a completed or phenomenologically viable theory; no result "
            "from A60 or C is imported into the Spin(11) action"
        ),
    }


def gate_ledger(v64_route: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for upstream in v64_route["gate_ledger"]:
        rows.append(
            {
                "gate": upstream["gate"],
                "status": "OPEN",
                "V64_master_closed": False,
                "gate_promoted": False,
                "cross_route_aggregation_used": False,
                "decision": (
                    f"{upstream['decision']} Routes A60 and C remain unchanged "
                    "with their own scoped obstructions; no cross-route splice is allowed."
                ),
            }
        )
    return rows


def source_manifest() -> dict[str, dict[str, Any]]:
    paths = {
        "audit_script": Path(__file__),
        "pytest": TEST_PATH,
        "bound_V63_master": V63_MASTER_PATH,
        "bound_V64_route": V64_ROUTE_PATH,
    }
    return {
        name: {
            "path": path.name,
            "exists": path.is_file(),
            "sha256": sha256_file(path),
        }
        for name, path in paths.items()
    }


def build_report() -> dict[str, Any]:
    v63_master = load_bound(
        V63_MASTER_PATH, EXPECTED_V63_MASTER_CORE, "V63 multipath master"
    )
    v64_route = load_bound(
        V64_ROUTE_PATH, EXPECTED_V64_ROUTE_CORE, "stable V64 route audit"
    )

    prior_a = route_by_id(v63_master, "A60")
    prior_b = route_by_id(v63_master, "B63")
    prior_c = route_by_id(v63_master, "C")
    corrected_b = route_b64(v64_route, prior_b)
    routes = [copy.deepcopy(prior_a), corrected_b, copy.deepcopy(prior_c)]

    preservation = conditional_preservations(v64_route)
    coefficient_scope = discrete_coefficient_scope(v64_route)
    card = downgraded_theory_card(v63_master, v64_route)
    gates = gate_ledger(v64_route)
    v63_only_retractions = [
        copy.deepcopy(row)
        for row in v64_route["retraction_ledger"]
        if row["prior_claim"].startswith("V63:")
    ]

    supersession = {
        "scope": "ONLY_ROUTE_B63",
        "parent_master_core": v63_master["core_sha256"],
        "superseded_route": {
            "route_id": prior_b["route_id"],
            "route_core": prior_b["bound_core_sha256"],
            "classification": prior_b["classification"],
        },
        "replacement_route": {
            "route_id": corrected_b["route_id"],
            "route_core": corrected_b["bound_core_sha256"],
            "classification": corrected_b["classification"],
        },
        "retracted_V63_route_B_claims": v63_only_retractions,
        "route_A60_preserved_exactly": True,
        "route_C_preserved_exactly": True,
        "V63_master_modified": False,
        "what_changes": (
            "twelve normalizable Q-type colored chiral components survive; "
            "actual IR=(1,-2); no WZ is forced; the V63 X/Y note is "
            "withdrawn; the current Spin(11) action is rejected"
        ),
        "what_does_not_change": (
            "A60 and C, the V61 selector theorem in arithmetic scope, and the "
            "V62 fixed-plane ledger in conditional pre-VEV scope"
        ),
    }

    report: dict[str, Any] = {
        "schema": "susy_v64_multipath_g1_frontier_master_audit/v1",
        "version": "V64",
        "date": "2026-08-29",
        "status": STATUS,
        "question": (
            "After the exact AB-tower null-mode counterexample, does any "
            "single route close G1, and which V63 claims remain valid?"
        ),
        "input_core_hashes": {
            "V63_multipath_master": EXPECTED_V63_MASTER_CORE,
            "V64_stable_route_retraction": EXPECTED_V64_ROUTE_CORE,
        },
        "lineage": {
            "parent_V63_master_core": v63_master["core_sha256"],
            "stable_V64_route_core": v64_route["core_sha256"],
            "V61_master_core_via_parent": v63_master["lineage"][
                "V61_master_core_via_parent"
            ],
            "V62_route_core_via_V64": v64_route["lineage"][
                "bound_V62_route_core"
            ],
            "route_A60_core": prior_a["bound_core_sha256"],
            "route_C_core": prior_c["bound_core_sha256"],
            "supersession": supersession,
        },
        "upstream_status": {
            "V63_master": v63_master["status"],
            "V64_route": v64_route["status"],
        },
        "route_matrix": routes,
        "route_B_retraction": {
            "normalizable_Q_type_complex_chiral_components": 12,
            "actual_IR_ledger": {"A3": "1", "A2": "-2"},
            "WZ_forced": False,
            "WZ_double_counting_rule": (
                "do not assign (-2,-3) to WZ while the light Q-type chirals "
                "already carry that anomaly; doing so would double-count"
            ),
            "V63_XY_note": "WITHDRAWN",
            "current_Spin11_action": "REJECTED",
        },
        "discrete_Z4R_coefficient_scope": coefficient_scope,
        "conditional_preservations": preservation,
        "downgraded_candidate_theory_card": card,
        "cross_route_composition_rule": {
            "logical_rule": (
                "Strict G1 must be proved by one versioned action; A60, B64, "
                "and C are inequivalent routes and cannot lend fields, anomaly "
                "sectors, or successful subclaims to one another."
            ),
            "cross_route_splicing_allowed": False,
            "aggregated_G1_closure": False,
            "route_A60_row_identical_to_V63": routes[0] == prior_a,
            "route_C_row_identical_to_V63": routes[2] == prior_c,
        },
        "comparison_conclusion": {
            "heterotic": copy.deepcopy(
                v63_master["comparison_conclusion"]["heterotic"]
            ),
            "Spin11": (
                "The present action is rejected: twelve normalizable Q-type "
                "colored chiral components survive. Their anomaly closes the "
                "IR-to-wall identities without WZ, so the V63 forced-WZ and "
                "rank-shifted X/Y claims are withdrawn."
            ),
            "gauged_U1R": copy.deepcopy(
                v63_master["comparison_conclusion"]["gauged_U1R"]
            ),
            "frontier": (
                "No route supplies a same-action microscopic completion. "
                "Route B must first add and audit a lifting sector satisfying "
                "R1--R5; A60 and C retain their unchanged obstructions."
            ),
        },
        "strict_master_decision": {
            "only_route_B63_superseded": True,
            "twelve_Q_type_chiral_components_survive": True,
            "actual_IR_ledger": {"A3": "1", "A2": "-2"},
            "V63_forced_WZ_claim_valid": False,
            "V63_XY_note_valid": False,
            "current_Spin11_action_accepted": False,
            "same_action_microscopic_completion_found": False,
            "V64_G1_closed": False,
            "closed_gates": [],
            "gate_promotions": 0,
            "complete_theory": False,
            "empirical_discovery": False,
            "master_is_a_frontier_certificate_not_an_action": True,
            "next_obligation": (
                "supply an explicit modified action and pass all R1--R5 "
                "repair acceptance criteria before recomputing any WZ claim"
            ),
            "honest_outcome": (
                "V64 retracts only the invalid V63 route-B completion claim. "
                "The current Spin(11) action fails strict G1 because twelve "
                "colored chiral components remain light. No route closes G1, "
                "and every G1--G8 gate remains OPEN."
            ),
        },
        "gate_ledger": gates,
        "source_policy": {
            "master_adds_no_new_primary_literature_claim": True,
            "primary_sources_are_in_the_bound_V64_route_artifact": True,
            "V64_route_derivation_controls_the_retraction": True,
        },
        "source_manifest": source_manifest(),
    }

    repair_ids = [row["id"] for row in card["repair_acceptance_criteria"]]
    integrity = {
        "both_bound_cores_are_canonical_and_expected": True,
        "V64_route_binds_this_exact_V63_master": (
            v64_route["lineage"]["bound_V63_master_core"]
            == EXPECTED_V63_MASTER_CORE
        ),
        "route_ids_are_exactly_A60_B64_C": [
            row["route_id"] for row in routes
        ]
        == ["A60", "B64", "C"],
        "only_B63_is_superseded": (
            supersession["scope"] == "ONLY_ROUTE_B63"
            and prior_b["route_id"] == "B63"
            and corrected_b["route_id"] == "B64"
            and len(v63_only_retractions) == 3
        ),
        "route_A60_is_exactly_preserved": routes[0] == prior_a,
        "route_C_is_exactly_preserved": routes[2] == prior_c,
        "route_A60_core_is_expected": prior_a["bound_core_sha256"]
        == EXPECTED_A60_CORE,
        "route_C_core_is_expected": prior_c["bound_core_sha256"]
        == EXPECTED_C_CORE,
        "cross_route_splicing_is_forbidden": not report[
            "cross_route_composition_rule"
        ]["cross_route_splicing_allowed"],
        "twelve_normalizable_Q_type_chirals_are_bound": (
            corrected_b["exact_light_spectrum"][
                "normalizable_Q_type_complex_chiral_components"
            ]
            == 12
            and corrected_b["exact_light_spectrum"][
                "right_nullity_per_complex_direction"
            ]
            == 1
            and corrected_b["exact_light_spectrum"][
                "infinite_kernel_normalizable"
            ]
        ),
        "actual_IR_is_1_minus2_and_matches_walls": (
            corrected_b["corrected_post_VEV_ledger"]["actual_IR"]
            == {"A3": "1", "A2": "-2"}
            and corrected_b["corrected_post_VEV_ledger"][
                "V62_pre_VEV_wall_sum"
            ]
            == {"A3": "1", "A2": "-2"}
            and corrected_b["corrected_post_VEV_ledger"][
                "both_match_without_WZ"
            ]
        ),
        "WZ_is_not_forced_or_double_counted": (
            not report["route_B_retraction"]["WZ_forced"]
            and corrected_b["WZ_status"]["functional_for_this_matching"]
            == "NOT_FORCED"
            and corrected_b["WZ_status"][
                "double_counting_forbidden_while_exotics_are_light"
            ]
        ),
        "discrete_congruence_fixes_only_residues": (
            coefficient_scope["half_index_convention"]["residues_mod_eta"]
            == {"SU3": 0, "SU2_L": 1}
            and coefficient_scope["integer_index_convention_2A"][
                "residues_mod4"
            ]
            == {"SU3": 0, "SU2_L": 2}
            and not coefficient_scope[
                "exact_integer_WZ_coefficients_fixed_by_discrete_congruence"
            ]
        ),
        "V63_XY_note_is_withdrawn": report["route_B_retraction"][
            "V63_XY_note"
        ]
        == "WITHDRAWN",
        "current_Spin11_action_is_rejected": (
            not corrected_b["current_action_accepted"]
            and not card["candidate_action_accepted"]
        ),
        "V61_selector_is_arithmetic_only": preservation[
            "V61_selector_arithmetic"
        ]["status"]
        == "PRESERVED_AS_ARITHMETIC_ONLY",
        "V62_ledger_is_pre_VEV_conditional_only": preservation[
            "V62_pre_VEV_localized_ledger"
        ]["status"]
        == "PRESERVED_CONDITIONALLY",
        "repair_criteria_are_exactly_R1_through_R5": repair_ids
        == ["R1", "R2", "R3", "R4", "R5"],
        "downgraded_card_excludes_forced_WZ": all(
            "Wess-Zumino" not in item for item in card["active_action_inventory"]
        ),
        "no_route_has_same_action_G1_completion": all(
            not row["same_action_microscopic_completion"]
            and not row["G1_closed"]
            and row["closed_gates"] == []
            for row in routes
        ),
        "all_G1_to_G8_gates_are_open_without_promotion": (
            len(gates) == 8
            and [row["gate"] for row in gates]
            == [f"G{index}" for index in range(1, 9)]
            and all(
                row["status"] == "OPEN"
                and not row["V64_master_closed"]
                and not row["gate_promoted"]
                and not row["cross_route_aggregation_used"]
                for row in gates
            )
        ),
        "zero_gate_promotions_and_no_complete_theory": (
            report["strict_master_decision"]["gate_promotions"] == 0
            and not report["strict_master_decision"]["complete_theory"]
        ),
        "all_manifest_files_exist_and_are_hashed": all(
            row["exists"] and row["sha256"]
            for row in report["source_manifest"].values()
        ),
    }
    report["integrity_checks"] = integrity
    report["n_integrity_checks"] = len(integrity)
    report["n_failed_integrity_checks"] = sum(
        not value for value in integrity.values()
    )
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("V64 multipath canonical core mismatch")
    if report["n_failed_integrity_checks"] != 0:
        failed = [
            key for key, value in report["integrity_checks"].items() if not value
        ]
        raise RuntimeError(f"V64 multipath integrity failures: {failed}")

    v63_master = load_bound(
        V63_MASTER_PATH, EXPECTED_V63_MASTER_CORE, "V63 multipath master"
    )
    load_bound(V64_ROUTE_PATH, EXPECTED_V64_ROUTE_CORE, "stable V64 route audit")
    routes = report["route_matrix"]
    if [row["route_id"] for row in routes] != ["A60", "B64", "C"]:
        raise RuntimeError("route matrix must be exactly A60, B64, C")
    if routes[0] != route_by_id(v63_master, "A60"):
        raise RuntimeError("route A60 was not preserved exactly")
    if routes[2] != route_by_id(v63_master, "C"):
        raise RuntimeError("route C was not preserved exactly")
    if routes[1]["bound_core_sha256"] != EXPECTED_V64_ROUTE_CORE:
        raise RuntimeError("route B64 is not bound to the stable V64 core")
    if routes[1]["supersedes_V63_route_id"] != "B63":
        raise RuntimeError("V64 master may supersede only B63")
    if report["lineage"]["supersession"]["scope"] != "ONLY_ROUTE_B63":
        raise RuntimeError("supersession escaped route B")

    ledger = routes[1]["corrected_post_VEV_ledger"]
    if ledger["actual_IR"] != {"A3": "1", "A2": "-2"}:
        raise RuntimeError("corrected physical IR ledger changed")
    if ledger["actual_IR"] != ledger["V62_pre_VEV_wall_sum"]:
        raise RuntimeError("corrected IR-to-wall identity failed")
    if not ledger["both_match_without_WZ"]:
        raise RuntimeError("corrected matching must close without WZ")
    if report["route_B_retraction"]["WZ_forced"]:
        raise RuntimeError("V64 may not force the retracted WZ term")
    if report["discrete_Z4R_coefficient_scope"][
        "exact_integer_WZ_coefficients_fixed_by_discrete_congruence"
    ]:
        raise RuntimeError("discrete congruence fixes residues, not exact integers")

    preservation = report["conditional_preservations"]
    if preservation["V61_selector_arithmetic"]["status"] != (
        "PRESERVED_AS_ARITHMETIC_ONLY"
    ):
        raise RuntimeError("V61 selector scope was overpromoted")
    if preservation["V62_pre_VEV_localized_ledger"]["status"] != (
        "PRESERVED_CONDITIONALLY"
    ):
        raise RuntimeError("V62 pre-VEV ledger scope was overpromoted")

    repairs = report["downgraded_candidate_theory_card"][
        "repair_acceptance_criteria"
    ]
    if [row["id"] for row in repairs] != ["R1", "R2", "R3", "R4", "R5"]:
        raise RuntimeError("repair criteria R1-R5 are incomplete or reordered")
    if report["downgraded_candidate_theory_card"]["candidate_action_accepted"]:
        raise RuntimeError("the current Spin11 action must remain rejected")
    if report["cross_route_composition_rule"]["cross_route_splicing_allowed"]:
        raise RuntimeError("cross-route splicing is forbidden")
    if any(
        row["status"] != "OPEN"
        or row["V64_master_closed"]
        or row["gate_promoted"]
        or row["cross_route_aggregation_used"]
        for row in report["gate_ledger"]
    ):
        raise RuntimeError("all G1-G8 gates must remain OPEN without promotion")
    if report["strict_master_decision"]["gate_promotions"] != 0:
        raise RuntimeError("V64 master may not promote a gate")
    if report["strict_master_decision"]["complete_theory"]:
        raise RuntimeError("V64 master may not claim a complete theory")
    if report["source_manifest"] != source_manifest():
        raise RuntimeError("V64 multipath source manifest is stale")


def render_markdown(report: Mapping[str, Any]) -> str:
    correction = report["route_B_retraction"]
    scope = report["discrete_Z4R_coefficient_scope"]
    card = report["downgraded_candidate_theory_card"]
    lines = [
        "# SUSY V64 multipath G1 frontier master audit",
        "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        f"- Bound V63 master: `{report['input_core_hashes']['V63_multipath_master']}`",
        f"- Bound stable V64 route: `{report['input_core_hashes']['V64_stable_route_retraction']}`",
        "- Outcome: **only route B63 is superseded; the current Spin(11) action is rejected and all G1--G8 gates remain OPEN.**",
        "- Gate promotions: **0/8**.",
        "",
        "## Master correction",
        "",
        (
            "The exact V64 mass operator has one normalizable right-kernel mode "
            "per complex Q-type direction. Twelve colored chiral components "
            "therefore survive. Their mixed-R ledger is (-2,-3), making the "
            "physical IR ledger (A3,A2)=(1,-2), exactly equal to the V62 "
            "pre-VEV wall sum. No WZ term is forced. Assigning the same "
            "(-2,-3) ledger to WZ while these fields are light would double-count."
        ),
        "",
        f"- V63 X/Y note: **{correction['V63_XY_note']}**.",
        f"- Current Spin(11) action: **{correction['current_Spin11_action']}**.",
        "- V63 forced-WZ claim: **RETRACTED**.",
        "",
        "## Route matrix",
        "",
        "| Route | Bound core | Standing | G1 |",
        "|---|---|---|---|",
    ]
    for row in report["route_matrix"]:
        if row["route_id"] == "B64":
            standing = "current action rejected; repair R1--R5 required"
        else:
            standing = "preserved exactly from V63 with its scoped obstruction"
        lines.append(
            f"| {row['route_id']} | `{row['bound_core_sha256']}` | {standing} | OPEN |"
        )
    lines.extend(
        [
            "",
            "A60 and C are exact structural copies of their V63 rows. No field, "
            "anomaly sector, or successful subclaim is spliced across routes.",
            "",
            "## Discrete coefficient scope",
            "",
            (
                "For Z4R, eta=2. In the half-index convention, (-2,-3) gives "
                f"residues {scope['half_index_convention']['residues_mod_eta']} "
                "modulo 2. In the doubled integer-index convention, (-4,-6) "
                f"gives {scope['integer_index_convention_2A']['residues_mod4']} "
                "modulo 4. These congruences fix only residue classes, not exact "
                "integer WZ coefficients. No continuous U(1)R lift or regulator "
                "has been supplied."
            ),
            "",
            "## Scoped preservations",
            "",
        ]
    )
    for name, item in report["conditional_preservations"].items():
        lines.append(f"- `{name}`: **{item['status']}** — {item['scope']}")
    lines.extend(
        [
            "",
            "## Downgraded candidate theory card",
            "",
            f"- Standing: **{card['standing']}**.",
            f"- Exact blocker: {card['exact_blocker']}.",
            f"- Honesty clause: {card['honesty_clause']}.",
            "",
            "Scoped certified results:",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in card["certified_scoped_results"])
    lines.extend(
        [
            "",
            "Excluded from the active action:",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in card["excluded_from_active_action"])
    lines.extend(
        [
            "",
            "## Exact remaining repair criteria",
            "",
            "| ID | Required criterion | Fail-closed test |",
            "|---|---|---|",
        ]
    )
    for row in card["repair_acceptance_criteria"]:
        lines.append(
            f"| {row['id']} | {row['criterion']} | {row['fail_closed_test']} |"
        )
    lines.extend(
        [
            "",
            "## Remaining obligations",
            "",
        ]
    )
    for row in card["remaining_obligations"]:
        lines.append(
            f"- **{row['status']} — {row['obligation']}**: {row['detail']}"
        )
    lines.extend(
        [
            "",
            "## G1--G8 ledger",
            "",
            "| Gate | Status | Decision |",
            "|---|---|---|",
        ]
    )
    for row in report["gate_ledger"]:
        lines.append(f"| {row['gate']} | {row['status']} | {row['decision']} |")
    lines.extend(
        [
            "",
            "## Integrity",
            "",
        ]
    )
    for key, value in report["integrity_checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Bound primary-source scope",
            "",
            (
                "The primary-source bibliography and the exact quadratic "
                "derivation are carried by the bound stable V64 route audit. "
                "This master adds no independent literature claim."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write JSON and Markdown")
    parser.add_argument("--check", action="store_true", help="verify generated artifacts")
    args = parser.parse_args()
    report = build_report()
    validate(report)
    if args.write:
        write_outputs(report)
    if args.check:
        if not JSON_PATH.is_file() or not MD_PATH.is_file():
            raise RuntimeError("generated V64 multipath artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("generated V64 multipath JSON is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("generated V64 multipath Markdown is stale")
    print(report["status"])
    print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
