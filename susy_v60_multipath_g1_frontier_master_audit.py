#!/usr/bin/env python3
"""V60 master audit after the live Orbifolder corrected-charge regeneration.

This is a new master, not an edit of V59.  It supersedes the V59 heterotic
data-sufficiency frontier with the source-locked 92-state live-Orbifolder
certificate, while carrying forward and directly binding the V59 Spin(11) and
gauged-U(1)R routes.

The Kappl candidate is rejected as the sought G1 completion in the tested
corrected Abelian basis: every odd corrected plane-R combination has
non-universal visible/hidden residues, and all available U(1) and printed
space-group mixings fail to repair them.  This is not a universal heterotic or
full physical-symmetry no-go.  The freely acting translation is not preserved
as a conjugacy class by the tested rho action, and local/threshold/axion data
remain unknown.  All G1--G8 gates therefore stay open.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V60_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
MD_PATH = ROOT / "SUSY_V60_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v60_multipath_g1_frontier_master_audit.py"

INPUTS = {
    "v59_master": ROOT / "SUSY_V59_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
    "v60_live_heterotic": ROOT / "susy_v60_heterotic_corrected_z4r_live_orbifolder_audit.json",
    "v59_spin11": ROOT / "SUSY_V59_SPIN11_GAUGE_HIGGS_COMPLETION_AUDIT.json",
    "v59_gauged_u1r": ROOT / "SUSY_V59_GAUGED_U1R_LOCAL_COMPLETION_AUDIT.json",
}

CORE_KEYS = {
    "v59_master": "core_sha256",
    "v60_live_heterotic": "canonical_core_sha256",
    "v59_spin11": "core_sha256",
    "v59_gauged_u1r": "core_sha256",
}

EXPECTED_CORES = {
    "v59_master": "9a74431ca080341d56225c6cc85edb937d3cafaa902bbacb556dbb325d78d24a",
    "v60_live_heterotic": "096537e4701bea02c8d6a3563adfd24b4247c90a8258621eef6c2ce801991ecd",
    "v59_spin11": "bf666eb5e4d57bff18b05182d7d6cc7874bbc26dd71897153faf9ee67a5f8c42",
    "v59_gauged_u1r": "27b4e032ff10065b534c1c62c2adf88f677b07c228f243b5376227fdb307ac8d",
}

STATUS = (
    "V60_MULTIPATH_G1_FRONTIER_MASTER__V59_MASTER_AND_LIVE_ORBIFOLDER_CORE_"
    "BOUND__V59_ROUTE_A_SUPERSEDED__92_STATE_CORRECTED_CHARGE_AMBIGUITY_"
    "RESOLVED_CONDITIONALLY__SIX_GAMMA_SHIFTS_EXACT__EVERY_ODD_CORRECTED_"
    "PLANE_R_COMBINATION_NONUNIVERSAL__AVAILABLE_U1_AND_PRINTED_SPACE_GROUP_"
    "MIXINGS_CANNOT_REPAIR__KAPPL_CANDIDATE_REJECTED_AS_G1_COMPLETION__NO_"
    "ODD_PLANE_R_COMBINATION_CLASS_PRESERVES_TAU__LOCAL_THRESHOLD_AXION_"
    "COMPLETION_OPEN__"
    "NOT_A_UNIVERSAL_HETEROTIC_NO_GO__V59_SPIN11_AND_GAUGED_U1R_ROUTES_"
    "CARRIED_FORWARD__NO_CROSS_ROUTE_SPLICING__G1_TO_G8_OPEN"
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


def load_bound(name: str) -> dict[str, Any]:
    path = INPUTS[name]
    if not path.is_file():
        raise RuntimeError(f"missing V60 master input: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    key = CORE_KEYS[name]
    stored = value.get(key)
    actual = canonical_sha(value, key)
    if stored != actual:
        raise RuntimeError(f"stale canonical core: {path.name}")
    if actual != EXPECTED_CORES[name]:
        raise RuntimeError(f"unexpected upstream core: {path.name}")
    return value


def route_by_id(master: Mapping[str, Any], route_id: str) -> dict[str, Any]:
    return copy.deepcopy(
        next(row for row in master["route_matrix"] if row["route_id"] == route_id)
    )


def full_tau_odd_r_scan(value: Mapping[str, Any]) -> dict[str, Any]:
    """Enumerate all W-charge-two plane-R point actions on the free shift."""

    obstruction = value["full_CFT_obstruction"]
    upstream = obstruction["all_odd_sum_plane_R_combinations"]
    tau = tuple(Fraction(piece) for piece in obstruction["tau"])
    orbit = {
        tuple(Fraction(piece) for piece in row)
        for row in obstruction["point_group_conjugacy_orbit"]
    }
    occupied = [index for index, component in enumerate(tau) if component]
    if occupied != [1, 3, 5]:
        raise RuntimeError(f"unexpected freely acting tau support: {occupied}")

    point_group_flip_counts = sorted(
        {
            sum(candidate[index] != tau[index] for index in occupied)
            for candidate in orbit
        }
    )
    rows = []
    for coefficients in product(range(4), repeat=3):
        if sum(coefficients) % 2 != 1:
            continue
        transformed = list(tau)
        odd_planes = []
        for plane, coefficient in enumerate(coefficients):
            if coefficient % 2:
                odd_planes.append(plane + 1)
                transformed[2 * plane] *= -1
                transformed[2 * plane + 1] *= -1
        transformed_tuple = tuple(transformed)
        rows.append(
            {
                "coefficients_mod4": list(coefficients),
                "odd_planes": odd_planes,
                "occupied_half_components_flipped": len(odd_planes),
                "rho_tau": [str(piece) for piece in transformed_tuple],
                "in_point_group_conjugacy_orbit": transformed_tuple in orbit,
            }
        )

    upstream_rows = {
        tuple(row["coefficients_mod4"]): row for row in upstream["rows"]
    }
    rows_match_upstream = all(
        tuple(row["coefficients_mod4"]) in upstream_rows
        and upstream_rows[tuple(row["coefficients_mod4"])]["odd_plane_flip_count"]
        == row["occupied_half_components_flipped"]
        and upstream_rows[tuple(row["coefficients_mod4"])][
            "in_point_group_conjugacy_orbit"
        ]
        == row["in_point_group_conjugacy_orbit"]
        and upstream_rows[tuple(row["coefficients_mod4"])]["rho_tau"]
        == row["rho_tau"]
        for row in rows
    ) and len(upstream_rows) == len(rows)

    return {
        "derivation": (
            "point-group conjugation flips an even number of tau's occupied "
            "half-components, while c1+c2+c3 odd implies an odd number of odd "
            "c_i and hence an odd number of flipped occupied half-components"
        ),
        "source": "upstream theorem independently re-enumerated from data bound by the V60 live-route core",
        "upstream_parity_theorem": obstruction["parity_theorem"],
        "upstream_point_group_plane_flip_parities": upstream[
            "point_group_plane_flip_parities"
        ],
        "upstream_every_candidate_fails_class_preservation": upstream[
            "every_candidate_fails_class_preservation"
        ],
        "independent_rows_match_upstream_certificate": rows_match_upstream,
        "point_group_orbit_size": len(orbit),
        "point_group_occupied_flip_counts": point_group_flip_counts,
        "coefficient_domain": "c_i in Z4 and c1+c2+c3 odd",
        "combinations_tested": len(rows),
        "R_type_occupied_flip_counts": sorted(
            {row["occupied_half_components_flipped"] for row in rows}
        ),
        "class_preserving_count": sum(
            row["in_point_group_conjugacy_orbit"] for row in rows
        ),
        "every_allowed_combination_fails_class_preservation": all(
            not row["in_point_group_conjugacy_orbit"] for row in rows
        ),
        "rows": rows,
        "scope_caveat": (
            "This excludes a class-preserving diagonal action in the tested space "
            "group. It does not exclude a sector-permuting winding or generalized symmetry."
        ),
    }


def heterotic_live_row(value: Mapping[str, Any]) -> dict[str, Any]:
    spectrum = value["spectrum"]
    anomalies = value["non_Abelian_mixed_Z4R_anomalies"]
    corrected = anomalies["corrected_conditional_massless_ledger"]
    scan = anomalies["all_three_corrected_plane_R_audit"]["coefficient_scan"]
    repair = value["mixing_repair_audit"]
    tau = value["full_CFT_obstruction"]
    terminal = value["terminal_decision"]
    factors = anomalies["factor_order"]
    tau_scan = full_tau_odd_r_scan(value)
    return {
        "route_id": "A60",
        "name": "live-Orbifolder corrected heterotic Z4R route",
        "bound_core_sha256": value["canonical_core_sha256"],
        "classification": "KAPPL_CANDIDATE_REJECTED_IN_TESTED_CORRECTED_BASIS__NOT_UNIVERSAL_HETEROTIC_NO_GO",
        "supersedes_V59_route_id": "A",
        "tested_object": (
            "the source-locked Kappl E8xE8 freely quotiented candidate, its 92 "
            "regenerated massless chiral multiplets, all corrected plane-R "
            "combinations with superpotential charge two, nine available U(1)s, "
            "and six printed non-R space-group Z2 generators"
        ),
        "conditional_charge_reconstruction": {
            "status": terminal["conditional_92_state_charge_reconstruction"],
            "vendored_fixture_sha256": value["source_lock"][
                "susy_v60_heterotic_corrected_z4r_live_orbifolder_fixture.json"
            ]["sha256"],
            "vendored_fixture_matches_expected": value["source_lock"][
                "susy_v60_heterotic_corrected_z4r_live_orbifolder_fixture.json"
            ]["matches_expected"],
            "field_count": spectrum["field_count"],
            "all_oscillators_absent": spectrum["all_oscillators_absent"],
            "all_affine_hg_equations_pass": spectrum["all_affine_hg_equations_pass"],
            "changed_field_count": spectrum["changed_field_count"],
            "changed_fields": [
                {
                    "field": row["field"],
                    "orbifolder_field_no": row["orbifolder_field_no"],
                    "gamma_h": row["gamma_h"],
                    "old_q_mod4": row["qZ4R_old_mod4"],
                    "corrected_q_mod4": row["qZ4R_corrected_mod4"],
                }
                for row in spectrum["changed_fields"]
            ],
            "charge_formula": value["geometry_and_conventions"][
                "spin_lift_integer_normalization"
            ]["qZ4R_corrected"],
            "h_g_equation": value["geometry_and_conventions"]["h_g_derivation"][
                "equation"
            ],
        },
        "corrected_hidden_anomaly_certificate": {
            "formula": anomalies["formula"],
            "factor_order": factors,
            "anomaly_representatives": [
                corrected[name]["A_representative"] for name in factors
            ],
            "residue_vector_mod2": anomalies["corrected_residue_vector_mod2"],
            "universal": anomalies["corrected_residues_universal"],
            "hidden_nonuniversality": (
                anomalies["corrected_residue_vector_mod2"][:3]
                != anomalies["corrected_residue_vector_mod2"][3:]
            ),
        },
        "complete_tested_Abelian_basis_scan": {
            "domain": scan["domain"],
            "coefficients_tested": scan["coefficients_tested"],
            "residue_pattern_counts": scan["residue_pattern_counts"],
            "universal_case_count": scan["universal_case_count"],
            "universal_case_exists": scan["universal_case_exists"],
            "continuous_U1_columns_all_universal": all(
                repair["continuous_U1"][
                    "each_column_is_universal_across_all_non_Abelian_factors"
                ]
            ),
            "space_group_mixings_enumerated": repair[
                "space_group_exhaustive_binary_search"
            ]["mixings_enumerated"],
            "space_group_repair_exists": repair[
                "space_group_exhaustive_binary_search"
            ]["repair_exists"],
            "available_U1_and_printed_SG_cannot_repair": repair[
                "available_U1_and_printed_space_group_mixings_cannot_repair"
            ],
            "no_combination_in_tested_basis_repairs": repair[
                "no_Abelian_combination_in_plane_R_x_U1_9_x_SG_basis_repairs"
            ],
            "scope_caveat": repair["scope_caveat"],
        },
        "full_CFT_scope_obstruction": {
            "rho2_tau": tau["rho2_tau"],
            "rho2_tau_equals_tau_minus_e4": tau[
                "rho2_tau_equals_tau_minus_e4"
            ],
            "rho2_tau_in_conjugacy_orbit": tau[
                "rho2_tau_in_conjugacy_orbit"
            ],
            "no_h_tau_in_space_group": tau["no_h_tau_in_space_group"],
            "scope": tau["scope"],
            "all_odd_plane_R_tau_class_scan": tau_scan,
        },
        "unknown_obligations": value["unknown_obligations"],
        "candidate_G1_completion_rejected": (
            terminal["corrected_non_Abelian_anomaly_universality"] == "FAIL"
            and terminal["repair_by_available_U1_or_printed_space_group_mixings"]
            == "FAIL"
        ),
        "full_physical_symmetry_no_go_proved": terminal[
            "physical_symmetry_no_go_proved"
        ],
        "same_action_microscopic_completion": terminal["strict_G1_closed"],
        "G1_closed": terminal["strict_G1_closed"],
        "closed_gates": [],
    }


def carried_route(
    v59_master: Mapping[str, Any], route_id: str, direct: Mapping[str, Any]
) -> dict[str, Any]:
    row = route_by_id(v59_master, route_id)
    if row["bound_core_sha256"] != direct["core_sha256"]:
        raise RuntimeError(f"V59 route {route_id} row/direct core mismatch")
    row["carried_forward_unchanged_from_V59_master_core"] = v59_master[
        "core_sha256"
    ]
    row["direct_core_rebound_in_V60"] = True
    return row


def gate_ledger(v59_master: Mapping[str, Any]) -> list[dict[str, Any]]:
    prior = {row["gate"]: row for row in v59_master["gate_ledger"]}
    rows = []
    for index in range(1, 9):
        gate = f"G{index}"
        if gate == "G1":
            decision = (
                "OPEN: live regeneration resolves the 92-state charge ambiguity "
                "conditionally but rejects the Kappl candidate in the tested corrected "
                "Abelian basis through hidden-anomaly non-universality. The rho(tau) "
                "class-preservation failure and local/threshold/axion deficits prevent "
                "a full physical no-go. Spin(11) and gauged-U1R remain independently open."
            )
        else:
            decision = (
                f"OPEN: V60 adds no same-action proof of {gate}; the prior fail-closed "
                f"frontier remains: {prior[gate]['decision']}"
            )
        rows.append(
            {
                "gate": gate,
                "status": "OPEN",
                "V60_master_closed": False,
                "decision": decision,
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
    v59_master = load_bound("v59_master")
    live = load_bound("v60_live_heterotic")
    spin11 = load_bound("v59_spin11")
    gauged = load_bound("v59_gauged_u1r")

    old_a = route_by_id(v59_master, "A")
    new_a = heterotic_live_row(live)
    route_b = carried_route(v59_master, "B", spin11)
    route_c = carried_route(v59_master, "C", gauged)
    routes = [new_a, route_b, route_c]
    gates = gate_ledger(v59_master)

    supersession = {
        "superseded_route": {
            "master_core": v59_master["core_sha256"],
            "route_id": "A",
            "route_core": old_a["bound_core_sha256"],
            "classification": old_a["classification"],
        },
        "replacement_route": {
            "route_id": "A60",
            "route_core": live["canonical_core_sha256"],
            "classification": new_a["classification"],
        },
        "what_is_resolved": (
            "the published-table ambiguity is replaced by a source-locked conditional "
            "92-state reconstruction with exact gamma phases and six corrected shifts"
        ),
        "what_is_not_resolved": (
            "a class-preserving full-CFT symmetry action, local/threshold/axion GS "
            "completion, post-VEV corrected generator, or a universal heterotic theorem"
        ),
        "route_B_core_unchanged": route_b["bound_core_sha256"],
        "route_C_core_unchanged": route_c["bound_core_sha256"],
        "V59_master_modified": False,
    }

    no_same_action = all(
        not row["same_action_microscopic_completion"] for row in routes
    )
    integrity = {
        "all_four_input_cores_are_canonical_and_expected": True,
        "V59_route_A_is_replaced_not_mutated": (
            supersession["superseded_route"]["route_id"] == "A"
            and supersession["replacement_route"]["route_id"] == "A60"
            and supersession["superseded_route"]["route_core"]
            != supersession["replacement_route"]["route_core"]
            and not supersession["V59_master_modified"]
        ),
        "conditional_92_state_reconstruction_passes": (
            new_a["conditional_charge_reconstruction"]["status"] == "PASS"
            and new_a["conditional_charge_reconstruction"][
                "vendored_fixture_sha256"
            ]
            == "79ef2c19fd0b9a563ac36a06a3099e4b240966ef3dd8fe968fe4029d9b237f51"
            and new_a["conditional_charge_reconstruction"][
                "vendored_fixture_matches_expected"
            ]
            and new_a["conditional_charge_reconstruction"]["field_count"] == 92
            and new_a["conditional_charge_reconstruction"][
                "all_affine_hg_equations_pass"
            ]
        ),
        "six_exact_gamma_shifts_are_bound": (
            new_a["conditional_charge_reconstruction"]["changed_field_count"] == 6
            and [
                row["field"]
                for row in new_a["conditional_charge_reconstruction"][
                    "changed_fields"
                ]
            ]
            == ["F_41", "F_42", "F_80", "F_81", "F_91", "F_92"]
        ),
        "corrected_visible_hidden_residue_nonuniversality_is_bound": (
            new_a["corrected_hidden_anomaly_certificate"][
                "anomaly_representatives"
            ]
            == ["3", "1", "7", "2", "2"]
            and new_a["corrected_hidden_anomaly_certificate"][
                "residue_vector_mod2"
            ]
            == ["1", "1", "1", "0", "0"]
            and not new_a["corrected_hidden_anomaly_certificate"]["universal"]
        ),
        "every_odd_plane_R_combination_is_nonuniversal": (
            new_a["complete_tested_Abelian_basis_scan"]["coefficients_tested"]
            == 32
            and new_a["complete_tested_Abelian_basis_scan"][
                "universal_case_count"
            ]
            == 0
            and not new_a["complete_tested_Abelian_basis_scan"][
                "universal_case_exists"
            ]
        ),
        "available_U1_and_printed_SG_mixings_do_not_repair": (
            new_a["complete_tested_Abelian_basis_scan"][
                "continuous_U1_columns_all_universal"
            ]
            and new_a["complete_tested_Abelian_basis_scan"][
                "space_group_mixings_enumerated"
            ]
            == 64
            and not new_a["complete_tested_Abelian_basis_scan"][
                "space_group_repair_exists"
            ]
            and new_a["complete_tested_Abelian_basis_scan"][
                "no_combination_in_tested_basis_repairs"
            ]
        ),
        "Kappl_candidate_is_rejected_as_tested_G1_completion": new_a[
            "candidate_G1_completion_rejected"
        ],
        "result_is_not_misreported_as_universal_heterotic_no_go": (
            not new_a["full_physical_symmetry_no_go_proved"]
            and not new_a["G1_closed"]
        ),
        "rho_tau_class_preservation_failure_is_bound": (
            new_a["full_CFT_scope_obstruction"]["no_h_tau_in_space_group"]
            and not new_a["full_CFT_scope_obstruction"][
                "rho2_tau_in_conjugacy_orbit"
            ]
        ),
        "all_32_odd_plane_R_actions_fail_tau_class_preservation": (
            new_a["full_CFT_scope_obstruction"][
                "all_odd_plane_R_tau_class_scan"
            ]["combinations_tested"]
            == 32
            and new_a["full_CFT_scope_obstruction"][
                "all_odd_plane_R_tau_class_scan"
            ]["point_group_occupied_flip_counts"]
            == [0, 2]
            and new_a["full_CFT_scope_obstruction"][
                "all_odd_plane_R_tau_class_scan"
            ]["R_type_occupied_flip_counts"]
            == [1, 3]
            and new_a["full_CFT_scope_obstruction"][
                "all_odd_plane_R_tau_class_scan"
            ]["every_allowed_combination_fails_class_preservation"]
            and new_a["full_CFT_scope_obstruction"][
                "all_odd_plane_R_tau_class_scan"
            ]["upstream_every_candidate_fails_class_preservation"]
            and new_a["full_CFT_scope_obstruction"][
                "all_odd_plane_R_tau_class_scan"
            ]["independent_rows_match_upstream_certificate"]
        ),
        "local_threshold_axion_obligations_remain_open": (
            len(new_a["unknown_obligations"]) == 5
            and live["terminal_decision"]["full_GS_local_threshold_completion"]
            == "OPEN"
        ),
        "V59_Spin11_route_is_directly_rebound_unchanged": (
            route_b["bound_core_sha256"] == spin11["core_sha256"]
            and route_b["direct_core_rebound_in_V60"]
        ),
        "V59_gauged_U1R_route_is_directly_rebound_unchanged": (
            route_c["bound_core_sha256"] == gauged["core_sha256"]
            and route_c["direct_core_rebound_in_V60"]
        ),
        "no_route_has_same_action_microscopic_completion": no_same_action,
        "cross_route_splicing_is_forbidden": True,
        "all_G1_to_G8_gates_remain_open": all(
            row["status"] == "OPEN"
            and not row["V60_master_closed"]
            and not row["cross_route_aggregation_used"]
            for row in gates
        ),
    }

    report: dict[str, Any] = {
        "schema": "susy_v60_multipath_g1_frontier_master_audit/v1",
        "status": STATUS,
        "question": (
            "After the live Orbifolder corrected-charge regeneration, does the "
            "heterotic route or either carried V59 route close strict G1 in one action?"
        ),
        "input_core_hashes": EXPECTED_CORES,
        "lineage": {
            "parent_master_core": v59_master["core_sha256"],
            "V58_baseline_core_via_parent": v59_master["V58_baseline"][
                "bound_core_sha256"
            ],
            "supersession": supersession,
        },
        "upstream_status": {
            "V59_master": v59_master["status"],
            "V60_live_heterotic": live["status"],
            "V59_Spin11": spin11["status"],
            "V59_gauged_U1R": gauged["status"],
        },
        "route_matrix": routes,
        "cross_route_composition_rule": {
            "logical_rule": (
                "Strict G1 must be proved by one versioned action. Conditional "
                "heterotic charges, a Spin(11) projector, and a gauged-U1R lattice "
                "cannot be conjoined across inequivalent actions."
            ),
            "cross_route_splicing_allowed": False,
            "aggregated_G1_closure": False,
            "route_specific_obstructions_remain_scoped": True,
        },
        "comparison_conclusion": {
            "heterotic": (
                "The live calculation is a decisive advance: the 92-state charge "
                "ambiguity is conditionally resolved, and the Kappl candidate fails "
                "corrected visible/hidden universality throughout the tested Abelian "
                "basis. Full-CFT class preservation and GS completion are still open, "
                "so this is not a universal heterotic no-go."
            ),
            "Spin11": v59_master["comparison_conclusion"]["Spin11"],
            "gauged_U1R": v59_master["comparison_conclusion"]["gauged_U1R"],
            "frontier": (
                "A different microscopic heterotic model or an enlarged sector-"
                "permuting/threshold completion is required on route A; routes B and C "
                "retain their separately certified obstructions."
            ),
        },
        "strict_master_decision": {
            "Kappl_candidate_G1_completion_rejected": True,
            "universal_heterotic_no_go": False,
            "same_action_microscopic_completion_found": False,
            "V60_G1_closed": False,
            "closed_gates": [],
            "complete_theory": False,
            "empirical_discovery": False,
            "master_is_a_frontier_certificate_not_an_action": True,
            "honest_outcome": (
                "The regenerated ledger rejects this Kappl candidate as the desired G1 "
                "completion in the complete tested corrected Abelian basis. It does not "
                "prove all heterotic realizations impossible, nor a full physical "
                "symmetry no-go for the freely quotiented CFT. No same-action route "
                "closes G1, and G1--G8 remain open."
            ),
        },
        "gate_ledger": gates,
        "source_policy": {
            "master_adds_no_new_literature_claim": True,
            "live_route_primary_sources_and_external_file_hashes_are_bound_by_its_core": True,
            "carried_route_primary_sources_remain_in_their_bound_artifacts": True,
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
        raise AssertionError("V60 multipath canonical core mismatch")
    if report["n_failed_integrity_checks"] != 0:
        failed = [
            name for name, ok in report["integrity_checks"].items() if not ok
        ]
        raise AssertionError(f"V60 multipath integrity failures: {failed}")
    decision = report["strict_master_decision"]
    if decision["universal_heterotic_no_go"]:
        raise AssertionError("candidate rejection was overgeneralized")
    if decision["same_action_microscopic_completion_found"]:
        raise AssertionError("V60 master promoted an absent completion")
    if report["cross_route_composition_rule"]["cross_route_splicing_allowed"]:
        raise AssertionError("V60 master spliced inequivalent actions")
    if any(row["status"] != "OPEN" for row in report["gate_ledger"]):
        raise AssertionError("V60 multipath master promoted a gate")


def render_markdown(report: Mapping[str, Any]) -> str:
    rows = {row["route_id"]: row for row in report["route_matrix"]}
    heterotic = rows["A60"]
    b = rows["B"]
    c = rows["C"]
    supersession = report["lineage"]["supersession"]
    tau_scan = heterotic["full_CFT_scope_obstruction"][
        "all_odd_plane_R_tau_class_scan"
    ]
    shifts = "\n".join(
        f"| {row['field']} | {row['orbifolder_field_no']} | {row['gamma_h']} | "
        f"{row['old_q_mod4']} | {row['corrected_q_mod4']} |"
        for row in heterotic["conditional_charge_reconstruction"]["changed_fields"]
    )
    gate_rows = "\n".join(
        f"| {row['gate']} | {row['status']} | {row['decision']} |"
        for row in report["gate_ledger"]
    )
    unknown = "\n".join(f"- {item}" for item in heterotic["unknown_obligations"])
    return f"""# V60 multipath G1 frontier master audit

Status: `{report['status']}`

## Result

**The live regeneration rejects the Kappl candidate as the desired G1
completion in the tested corrected Abelian basis. It does not prove a universal
heterotic no-go. G1--G8 remain OPEN.**

This distinct V60 master supersedes only the V59 heterotic route-A row. It
binds the prior V59 master and directly rebinds the unchanged Spin(11) and
gauged-U(1)R cores. No route-local gain is spliced into another action.

## Exact supersession

```text
V59 route A: {supersession['superseded_route']['route_core']}
V60 route A: {supersession['replacement_route']['route_core']}
V59 master:  {supersession['superseded_route']['master_core']}
```

The old published-table non-identifiability was correct but is no longer the
operative frontier. Live Orbifolder output now supplies a conditional,
source-locked 92-state reconstruction. The V59 master and route files were not
modified.

## Conditional 92-state reconstruction

All 92 regenerated massless chiral multiplets pass the affine `h_g` equations;
all have zero oscillator contribution. The formula is

```text
{heterotic['conditional_charge_reconstruction']['charge_formula']}
{heterotic['conditional_charge_reconstruction']['h_g_equation']}
```

Exactly six fields change by two modulo four:

| Field | Orbifolder number | gamma_h | old q | corrected q |
|---|---:|---:|---:|---:|
{shifts}

## Corrected hidden-anomaly rejection

With factor order

```text
{heterotic['corrected_hidden_anomaly_certificate']['factor_order']}
```

the anomaly representatives and residues are

```text
A_G       = {heterotic['corrected_hidden_anomaly_certificate']['anomaly_representatives']}
A_G mod 2 = {heterotic['corrected_hidden_anomaly_certificate']['residue_vector_mod2']}.
```

The visible `SU(3)C`, `SU(2)L`, and hidden `SU(3)` residues are one; the two
hidden `SU(2)` residues are zero. Thus the corrected generator is not universal.

The exhaustive corrected-plane scan tests
`{heterotic['complete_tested_Abelian_basis_scan']['coefficients_tested']}` odd
coefficient triples. Its only residue patterns are
`{heterotic['complete_tested_Abelian_basis_scan']['residue_pattern_counts']}`;
neither is universal. All nine printed continuous-U(1) anomaly columns are
universal shifts and cannot change relative residues. All
`{heterotic['complete_tested_Abelian_basis_scan']['space_group_mixings_enumerated']}`
binary combinations of the six printed non-R space-group generators likewise
produce no repair.

This rejects the Kappl candidate within the complete tested
`plane-R x U(1)^9 x SG` basis.

## Why this is not a full physical no-go

For the freely acting translation, the tested second-plane rotation obeys

```text
rho2(tau) = {heterotic['full_CFT_scope_obstruction']['rho2_tau']}
rho2(tau) = tau - e4: {heterotic['full_CFT_scope_obstruction']['rho2_tau_equals_tau_minus_e4']}
rho2(tau) in the space-group conjugacy orbit: {heterotic['full_CFT_scope_obstruction']['rho2_tau_in_conjugacy_orbit']}
```

No class-preserving `h_tau` exists for `rho2` in the tested space group. The
stronger full-plane enumeration uses the bound tau orbit:

```text
point-group occupied-component flip counts = {tau_scan['point_group_occupied_flip_counts']}
odd-sum plane-R flip counts                 = {tau_scan['R_type_occupied_flip_counts']}
odd-sum combinations tested                 = {tau_scan['combinations_tested']}
class-preserving combinations               = {tau_scan['class_preserving_count']}
```

Point-group conjugation changes an even number of tau's occupied
half-components. Every superpotential-charge-two plane-R combination changes
an odd number. Thus none of the 32 R-type combinations is class-preserving on
tau. This still does not exclude a sector-permuting winding or generalized
symmetry, so the conditional 92-state ledger is not promoted to a theorem about
every winding sector. These obligations also remain open:

{unknown}

The exact claim is candidate rejection, not a universal heterotic theorem.

## Carried routes

Route B remains `{b['classification']}`: it has two weak and zero colored
chiral zero modes plus the full-rank rank-breaking block, but its scoped
commuting-Abelian selector no-go and Dai--Freed/UV obligations remain.

Route C remains `{c['classification']}`: its integrated lattice and 270-singlet
parity solution pass, but the existing bulk GS direction fails at GG,
flipped-GG, and Pati--Salam fixed points.

## No cross-route splicing

{report['cross_route_composition_rule']['logical_rule']}

## Gate ledger

| Gate | Status | Decision |
|---|---|---|
{gate_rows}

## Fail-closed decision

{report['strict_master_decision']['honest_outcome']}

Primary-source provenance and external regeneration hashes remain in the
canonically bound route artifacts; this master adds no new literature claim.

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
            raise RuntimeError("generated V60 master artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("generated V60 master JSON is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("generated V60 master Markdown is stale")
    print(report["status"])
    print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
