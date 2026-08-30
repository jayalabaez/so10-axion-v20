#!/usr/bin/env python3
"""V67 multipath master for the index-changing and proton-stress frontiers.

This master does not splice the two V67 audits into an action.  It preserves
the V66 A60 and C rows byte-for-canonical-object, supersedes only B66 with a
fail-closed B67 summary, and keeps the currently bound Spin(11) action
rejected.  D67 is a candidate new six-dimensional action; the T66/B3 results
are conditional route diagnostics.  No extension is accepted and no gate is
closed.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping


VERSION = "V67"
DATE = "2026-08-30"
SCHEMA = "susy_v67_multipath_g1_frontier_master_audit/v1"
ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V67_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
MD_PATH = ROOT / "SUSY_V67_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v67_multipath_g1_frontier_master_audit.py"

INPUTS = {
    "v66_master": ROOT / "SUSY_V66_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
    "v67_index_route": ROOT / "SUSY_V67_SPIN11_INDEX_PARTNER_6D_ESCAPE_AUDIT.json",
    "v67_g7_route": ROOT / "SUSY_V67_SPIN11_T66_BARYON_PROTON_STRESS_AUDIT.json",
}
EXPECTED_CORES = {
    "v66_master": "499382834b9b63a23e10dbc16106dfb1db0f2bfeae17163862afd4f1467e9fa4",
    "v67_index_route": "5927f64eec6bc27d68b7d429eab11ee1f0efc9709041064f47baaabc25f0eebb",
    "v67_g7_route": "859ecfc4185738bd4e1cb8ecc0c14d3640f3c3abd588b8ce67a167f4771d738f",
}
V66_ROW_SHA = {
    "A60": "13d94100a9df22894d99e9dded6f66f8bb9ced99c73e16e33163785ba4bdc6dd",
    "B66": "c8f37fe5cb678c156b810489ec37e0d5354b9e30fd7519241c48f16e24691042",
    "C": "15eae74e91c5db8d43e4a76be7d1407921f5bef79f5486d470d5b05a831467b3",
}
EXPECTED_REGRESSION_FILES = 20
EXPECTED_REGRESSION_TESTS = 262
STATUS = (
    "V67_MULTIPATH_G1_FRONTIER_MASTER__V66_MASTER_AND_TWO_V67_ROUTE_CORES_BOUND__"
    "A60_AND_C_PRESERVED__ONLY_B66_TO_B67_SUPERSESSION__CURRENT_SPIN11_ACTION_"
    "REJECTED__D67_QR2_INDEX_PARTNER_6D_IS_CANDIDATE_NEW_ACTION_ONLY__T66_B3_IS_"
    "CONDITIONAL_ROUTE_AUDIT_ONLY__EXACT_ZERO_REMOVED_ONLY_IN_INHERITED_5D_"
    "CANDIDATE_OPERATOR__5D_SPLIT_BULK_UNCLASSIFIED__PHYSICAL_MASS_AND_LOCAL_6D_"
    "ACTION_OPEN__6D_POINT_COUPLING_DOUBLE_LATTICE_UNREGULATED__FORMAL_V62_5D_GS_"
    "DIAGNOSTIC_ONLY__T66_PRE_MAJORANA_DELTA_B_DELTA_L_OPERATOR_EXACT__POST_MAJORANA_"
    "DELTA_B_MINUS1_DELTA_L_PLUS1__SCOPED_FAMILY_DETERMINANT_SELECTOR_NO_GO__B3_IR_"
    "LINEAR_MOD3_CUBIC_MOD9_NOT_EMBEDDED__B3_SUPPLEMENTS_MATTER_PARITY__H66_T66_"
    "PROTON_PROXIES_ONLY__"
    "NO_CROSS_ROUTE_SPLICE__NO_ACCEPTED_EXTENSION__G1_TO_G8_OPEN_ZERO_PROMOTIONS"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha(value: Mapping[str, Any], key: str = "core_sha256") -> str:
    body = copy.deepcopy(dict(value))
    body.pop(key, None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def object_sha(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def load_bound(name: str) -> dict[str, Any]:
    path = INPUTS[name]
    if not path.is_file():
        raise RuntimeError(f"missing bound input: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    actual = canonical_sha(value)
    if value.get("core_sha256") != actual:
        raise RuntimeError(f"stale canonical core: {path.name}")
    if actual != EXPECTED_CORES[name]:
        raise RuntimeError(f"unexpected canonical core: {path.name}")
    return value


def route_by_id(master: Mapping[str, Any], route_id: str) -> dict[str, Any]:
    return copy.deepcopy(
        next(row for row in master["route_matrix"] if row["route_id"] == route_id)
    )


def frozen_v66_row(master: Mapping[str, Any], route_id: str) -> dict[str, Any]:
    row = route_by_id(master, route_id)
    if object_sha(row) != V66_ROW_SHA[route_id]:
        raise RuntimeError(f"changed V66 route row: {route_id}")
    return row


def regression_scope() -> dict[str, Any]:
    prior_re = re.compile(r"^test_susy_v(?:59|60|61|62|63|64|65|66)_.*\.py$")
    route_tests = {
        "test_susy_v67_spin11_index_partner_6d_escape_audit.py",
        "test_susy_v67_spin11_t66_baryon_proton_stress_audit.py",
    }
    test_re = re.compile(r"^def test_", re.MULTILINE)
    rows = []
    for path in sorted(ROOT.glob("test_susy_v*.py")):
        if prior_re.match(path.name) or path.name in route_tests:
            rows.append(
                {
                    "path": path.name,
                    "test_functions": len(
                        test_re.findall(path.read_text(encoding="utf-8"))
                    ),
                }
            )
    return {
        "selection": (
            "all V59-V66 audit tests plus the two bound V67 route tests; "
            "the V67 master test is excluded"
        ),
        "count_unit": "top-level test functions before pytest parametrization",
        "file_count": len(rows),
        "test_count": sum(row["test_functions"] for row in rows),
        "expected_file_count": EXPECTED_REGRESSION_FILES,
        "expected_test_count": EXPECTED_REGRESSION_TESTS,
        "files": rows,
    }


def candidate_matrix(
    v66_b: Mapping[str, Any], index: Mapping[str, Any], g7: Mapping[str, Any]
) -> list[dict[str, Any]]:
    inherited = {row["id"]: row for row in v66_b["candidate_extensions"]}
    proxy = {
        row["branch"]: row for row in g7["dimension_six_proton_proxy"]["rows"]
    }
    return [
        {
            "id": "D67",
            "kind": "CANDIDATE_NEW_ACTION",
            "status": index["terminal_decision"]["D67_status"],
            "accepted": False,
            "same_action_complete": False,
            "advance": "qR=2 conjugate partner removes the exact zero in the inherited 5D candidate operator",
            "open_boundary": (
                "physical colored mass is open; 5D split-bulk is unclassified; "
                "the 6D point coupling needs a regulated double lattice and a local action"
            ),
        },
        {
            "id": "H66",
            "kind": "INHERITED_CONDITIONAL_EXTENSION",
            "status": inherited["H66"]["status"],
            "accepted": False,
            "same_action_complete": False,
            "proton_proxy": "CENTRAL_FAIL_ONLY",
            "proxy_passes": proxy["H66"]["central_proxy_passes"],
        },
        {
            "id": "T66",
            "kind": "CONDITIONAL_ROUTE_AUDIT",
            "status": g7["terminal_decision"]["T66_status"],
            "accepted": False,
            "same_action_complete": False,
            "proton_proxy": "CENTRAL_PASS_ONLY",
            "proxy_passes": proxy["T66"]["central_proxy_passes"],
            "dimension_five_portal_unprotected": True,
        },
        {
            "id": "B3_IR",
            "kind": "CONDITIONAL_IR_SELECTOR",
            "status": g7["terminal_decision"]["B3_status"],
            "accepted": False,
            "same_action_complete": False,
            "embedded_in_5D": g7["claim_boundary"]["B3_embedded_in_5D"],
        },
    ]


def b67_row(
    v66: Mapping[str, Any], index: Mapping[str, Any], g7: Mapping[str, Any]
) -> dict[str, Any]:
    old_b = frozen_v66_row(v66, "B66")
    return {
        "route_id": "B67",
        "name": "Spin(11) index-changing and proton-stress frontier, fail closed",
        "supersedes_V66_route_id": "B66",
        "bound_core_sha256": EXPECTED_CORES["v66_master"],
        "bound_route_cores": {
            "index_partner_6D": index["core_sha256"],
            "T66_baryon_proton_stress": g7["core_sha256"],
        },
        "inherited_B66_row_sha256": object_sha(old_b),
        "current_bound_action_status": "REJECTED",
        "V64_null_mode_stands_for_current_action": old_b["V64_null_mode_stands"],
        "WZ_term": old_b["WZ_term"],
        "D67_candidate_new_action": {
            "classification": index["classification"],
            "spectral_index_repair": copy.deepcopy(index["spectral_index_repair"]),
            "charge_anomaly_and_proton_audit": copy.deepcopy(
                index["charge_anomaly_and_proton_audit"]
            ),
            "geometry_and_6D_escape": copy.deepcopy(index["geometry_and_6D_escape"]),
            "acceptance_matrix": copy.deepcopy(index["acceptance_matrix"]),
            "terminal_decision": copy.deepcopy(index["terminal_decision"]),
            "accepted": False,
        },
        "T66_B3_conditional_route_audit": {
            "t66_u_portal_schur_complement": copy.deepcopy(
                g7["t66_u_portal_schur_complement"]
            ),
            "unified_selector_one_sided_no_go": copy.deepcopy(
                g7["unified_selector_one_sided_no_go"]
            ),
            "conditional_b3_ir_escape": copy.deepcopy(
                g7["conditional_b3_ir_escape"]
            ),
            "dimension_six_proton_proxy": copy.deepcopy(
                g7["dimension_six_proton_proxy"]
            ),
            "dimension_five_portal_stress": copy.deepcopy(
                g7["dimension_five_portal_stress"]
            ),
            "gate_decision": copy.deepcopy(g7["gate_decision"]),
            "claim_boundary": copy.deepcopy(g7["claim_boundary"]),
            "terminal_decision": copy.deepcopy(g7["terminal_decision"]),
            "accepted": False,
        },
        "candidate_matrix": candidate_matrix(old_b, index, g7),
        "accepted_extension_count": 0,
        "same_action_microscopic_completion": False,
        "cross_route_evidence_spliced": False,
        "G1_closed": False,
        "closed_gates": [],
    }


def master_gates(v66: Mapping[str, Any]) -> list[dict[str, Any]]:
    prior = {row["gate"]: row for row in v66["gate_ledger"]}
    decisions = {
        "G1": (
            "OPEN: the current action remains REJECTED; D67 removes the zero only in the inherited "
            "5D candidate operator. 5D split-bulk is unclassified, and neither a certified physical "
            "mass nor a regulated local 6D action exists."
        ),
        "G2": "OPEN: no one coefficient-level action, flavor determinant, soft spectrum or pole matching exists.",
        "G3": "OPEN: 6D compactification, moduli/saxion stabilization, hidden vacuum and full Hessian are absent.",
        "G4": (
            "OPEN WITH EXACT ADVANCE: a qR=2 conjugate row makes the inherited 5D candidate "
            "operator invertible; the bound 5D action still has the V64 zero."
        ),
        "G5": "OPEN: no accepted exotic spectrum, decay calculation, collider ordering or relic history exists.",
        "G6": "OPEN: inflation, reheating, defects and moduli history remain absent.",
        "G7": (
            "OPEN WITH MATERIAL ADVANCE: the displayed T66 pre-Majorana DeltaB=DeltaL=-1 "
            "operator, post-Majorana field numbers and scoped family-determinant selector no-go "
            "are exact; B3 is an unembedded supplement to matter parity and the proton results are proxies."
        ),
        "G8": "OPEN: no UV regulator, complete local anomaly polynomial, Dai-Freed phase or predictivity score exists.",
    }
    return [
        {
            "gate": gate,
            "status": "OPEN",
            "V67_master_closed": False,
            "decision": decisions[gate],
            "inherited_V66_status": prior[gate]["status"],
            "cross_route_aggregation_used": False,
        }
        for gate in (f"G{i}" for i in range(1, 9))
    ]


def theory_card(b67: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "name": "V67 fail-closed Spin(11) multipath frontier card",
        "current_bound_action_status": "REJECTED",
        "exact_advances": [
            "D67 qR=2 conjugate row removes the exact zero from the inherited 5D candidate mass operator",
            "the inherited 5D light-root equation and overlap suppression are explicit",
            "5D split-bulk locality remains unclassified rather than excluded",
            "a genuine 6D point coupling requires a regulated and renormalized double KK lattice",
            "the inherited GS (SU3,SU2) shift (0,2) is only a formal V62 5D diagnostic",
            "T66 generates an exact pre-Majorana DeltaB=DeltaL=-1 Schur-complement operator",
            "after Majorana matching the displayed operator has DeltaB=-1 and DeltaL=+1",
            "the scoped family-dependent determinant theorem forbids eliminating every conjugate portal under h=0 and GM-neutrality",
            "the displayed IR B3 passes linear mod 3 and cubic mod 9, supplements matter parity, and is not a 5D local embedding",
            "H66 centrally fails and T66 centrally passes only the frozen conditional gauge proxy",
        ],
        "candidate_matrix": copy.deepcopy(b67["candidate_matrix"]),
        "accepted_extension_count": 0,
        "cross_route_splicing_allowed": False,
        "open_obligations": [
            "classify 5D split-bulk Spin(11) representations and parities",
            "construct a local supersymmetric 6D Spin(11) action and parity representation",
            "regulate and renormalize the 6D double-lattice point coupling or derive a fixed-line alternative",
            "derive the physical index-partner mass above the colored-exotic floor",
            "cancel local irreducible/reducible anomalies and the Dai-Freed phase",
            "embed any B3-like selector in the local unified action",
            "compute mass-basis Wilson tensors, KK sums, dressing, running and proton lifetimes",
            "supply soft terms, pole thresholds, flavor, vacuum, cosmology and a UV regulator",
        ],
        "honesty_clause": (
            "D67, H66, T66 and B3_IR are distinct conditional objects.  Their evidence "
            "cannot be combined into a completed action without a new same-action recomputation."
        ),
    }


def recompute(report: Mapping[str, Any]) -> dict[str, bool]:
    try:
        v66 = load_bound("v66_master")
        index = load_bound("v67_index_route")
        g7 = load_bound("v67_g7_route")
        expected_b67 = b67_row(v66, index, g7)
    except Exception:
        v66, index, g7, expected_b67 = {}, {}, {}, {}

    routes = {row.get("route_id"): row for row in report.get("route_matrix", [])}
    b = routes.get("B67", {})
    d = b.get("D67_candidate_new_action", {})
    spectral = d.get("spectral_index_repair", {})
    minimal = spectral.get("minimal_index_change", {})
    infinite = spectral.get("inherited_5D_infinite_tower", {})
    sixdim = spectral.get("six_dimensional_nonimport", {})
    light = spectral.get("light_singular_value", {})
    charge = d.get("charge_anomaly_and_proton_audit", {})
    gs = charge.get("formal_V62_5D_integrated_GS_diagnostic", {})
    geometry = d.get("geometry_and_6D_escape", {})
    d_terminal = d.get("terminal_decision", {})
    p = b.get("T66_B3_conditional_route_audit", {})
    schur = p.get("t66_u_portal_schur_complement", {})
    selector = p.get("unified_selector_one_sided_no_go", {})
    b3 = p.get("conditional_b3_ir_escape", {})
    proxies = {
        row.get("branch"): row
        for row in p.get("dimension_six_proton_proxy", {}).get("rows", [])
    }
    dim5 = p.get("dimension_five_portal_stress", {})
    candidates = {row.get("id"): row for row in b.get("candidate_matrix", [])}
    criteria = report.get("acceptance_criteria", [])
    gates = report.get("gate_ledger", [])
    strict = report.get("strict_master_decision", {})
    scope = report.get("regression_scope", {})

    finite_checks = minimal.get("finite_exact_checks", [])
    anomaly_sum = charge.get("global_mixed_R_anomaly", {}).get("sum", {})
    standard_b3 = b3.get("standard_discrete_anomaly_checks", {})
    linear_residues = standard_b3.get("linear_residues_mod3", {})
    post_majorana = schur.get("heavy_N_matching", {}).get(
        "post_Majorana_field_numbers", {}
    )
    exact_operator = (
        "W_eff=-(lambda_ij rho_kl/M10) epsilon^abc uc_k,a dc_i,b dc_j,c Nc_l"
    )
    return {
        "input_cores": report.get("input_core_hashes") == EXPECTED_CORES,
        "exact_bound_rebuild": bool(expected_b67) and b == expected_b67,
        "route_order_and_supersession": list(routes) == ["A60", "B67", "C"] and b.get("supersedes_V66_route_id") == "B66",
        "A60_preserved": object_sha(routes.get("A60", {})) == V66_ROW_SHA["A60"],
        "C_preserved": object_sha(routes.get("C", {})) == V66_ROW_SHA["C"],
        "B66_historical_row_bound": b.get("inherited_B66_row_sha256") == V66_ROW_SHA["B66"],
        "current_action_rejected": b.get("current_bound_action_status") == "REJECTED" and b.get("V64_null_mode_stands_for_current_action") is True and b.get("WZ_term") == "NONE_FORCED",
        "candidate_operator_exact_zero_removed": minimal.get("finite_determinant") == "det A'_N = M product_n k_n" and minimal.get("all_finite_checks_pass") is True and len(finite_checks) == 8 and all(row.get("matches") for row in finite_checks) and infinite.get("exact_zero_removed") is True,
        "physical_mass_still_open": light.get("exact_equation_for_inherited_5D_operator_below_first_KK_pole") == "M^2=m^2[1+alpha^2 tan(mL)/(mL)], 0<mL<pi/2" and light.get("no_parametrically_light_mode_proved_without_parameters") is False and d_terminal.get("physical_colored_mass_certified") is False,
        "qR2_selector_and_anomaly": charge.get("mass_terms_preserve_Z4R_without_q2_VEV") is True and charge.get("tree_level_Schur_theorem", {}).get("induced_four_matter_superpotential") == "0" and anomaly_sum == {"Delta_A3": 0, "Delta_A2": 0} and gs.get("formal_delta_c_diagnostic_mod4") == {"SU3": 0, "SU2": 2} and gs.get("status") == "FORMAL_5D_BOOKKEEPING_NOT_A_DERIVED_6D_LOCAL_COUPLING",
        "D67_new_action_only": geometry.get("current_5D_action", {}).get("wall_local_Q_only_patch_exists") is False and geometry.get("current_5D_action", {}).get("split_bulk_5D_status") == "UNCLASSIFIED__NO_EXHAUSTIVE_SPIN11_PARITY_OR_REPRESENTATION_NO_GO" and geometry.get("D67_6D_escape_candidate", {}).get("status") == "CANDIDATE_NEW_ACTION_NOT_CONSTRUCTED" and geometry.get("D67_6D_escape_candidate", {}).get("local_group") == "SU3C x SU2L x U1Y x U1X" and sixdim.get("status") == "OPEN_NOT_THE_INHERITED_5D_TAN_EQUATION" and "logarithmically" in sixdim.get("point_local_double_KK_asymptotic", "") and d_terminal.get("same_action_microscopic_completion_found") is False,
        "T66_exact_B_L_operator": schur.get("exact_derivation_pass") is True and schur.get("effective_superpotential_i_less_than_j") == exact_operator and schur.get("global_numbers", {}).get("Delta_B") == -1 and schur.get("global_numbers", {}).get("Delta_L") == -1 and schur.get("global_numbers", {}).get("Delta_B_minus_L") == 0 and schur.get("global_numbers", {}).get("scope") == "pre-Majorana matching: uc dc dc Nc" and post_majorana.get("Delta_B") == -1 and post_majorana.get("Delta_L") == 1 and post_majorana.get("Delta_B_minus_L") == -2 and post_majorana.get("operator") == "uc dc dc L Hu",
        "unified_selector_no_go": selector.get("result") == "NO_SCOPED_FAMILY_DEPENDENT_UNIFIED_ABELIAN_SELECTOR_CAN_FORBID_ALL_CONJUGATE_PORTALS" and selector.get("family_dependent_scan", {}).get("counterexample_count") == 0 and selector.get("family_dependent_scan", {}).get("charge_assignment_count") == 179998 and "does not assert" in selector.get("determinant_permutation_theorem", {}).get("conclusion", ""),
        "B3_conditional_not_embedded": b3.get("classification") == "CONDITIONAL_IR_ESCAPE_ONLY" and b3.get("modulus") == 3 and standard_b3.get("pass") is True and linear_residues and all(value == 0 for value in linear_residues.values()) and standard_b3.get("integer_parent_cubic_AZZZ_residue_mod9") == 0 and b3.get("symmetry_stack", {}).get("B3_is_not_a_replacement_for_matter_parity") is True and b3.get("current_action_compatibility", {}).get("accepted") is False and b3.get("current_action_compatibility", {}).get("IR_anomaly_pass_is_not_a_5D_embedding") is True,
        "H66_T66_proxies_only": p.get("dimension_six_proton_proxy", {}).get("claim_boundary") == "NO_LIFETIME_PREDICTION" and proxies.get("H66", {}).get("central_proxy_passes") is False and proxies.get("T66", {}).get("central_proxy_passes") is True and all(row.get("branch_globally_decided") is False for row in proxies.values()),
        "T66_dimension_five_open": dim5.get("O1_unprotected_portals_pass_comparison") is False and dim5.get("claim_boundary") == "CONDITIONAL_FEASIBILITY_BOUND_NOT_A_LIFETIME" and dim5.get("illustrative_common_T66_threshold", {}).get("maximum_abs_lambda_rho_thetaN_D", 1.0) < 3.0e-16,
        "candidate_isolation": set(candidates) == {"D67", "H66", "T66", "B3_IR"} and all(row.get("accepted") is False and row.get("same_action_complete") is False for row in candidates.values()) and candidates.get("D67", {}).get("kind") == "CANDIDATE_NEW_ACTION" and candidates.get("T66", {}).get("kind") == "CONDITIONAL_ROUTE_AUDIT" and candidates.get("B3_IR", {}).get("embedded_in_5D") is False,
        "regression_262_test_functions": scope.get("count_unit") == "top-level test functions before pytest parametrization" and scope.get("file_count") == EXPECTED_REGRESSION_FILES and scope.get("test_count") == EXPECTED_REGRESSION_TESTS and sum(row.get("test_functions", 0) for row in scope.get("files", [])) == EXPECTED_REGRESSION_TESTS,
        "A1_A8_open": [row.get("id") for row in criteria] == [f"A{i}" for i in range(1, 9)] and all(row.get("status") == "OPEN" for row in criteria),
        "G1_G8_open": [row.get("gate") for row in gates] == [f"G{i}" for i in range(1, 9)] and all(row.get("status") == "OPEN" and row.get("V67_master_closed") is False and row.get("cross_route_aggregation_used") is False for row in gates),
        "no_splice_no_acceptance": report.get("cross_route_composition_rule", {}).get("cross_route_splicing_allowed") is False and report.get("cross_route_composition_rule", {}).get("aggregated_gate_closure") is False and b.get("cross_route_evidence_spliced") is False and b.get("accepted_extension_count") == 0,
        "fail_closed": strict.get("current_Spin11_action_status") == "REJECTED" and strict.get("exact_zero_removed_in_D67_inherited_5D_candidate_operator") is True and strict.get("split_bulk_5D_status") == "UNCLASSIFIED" and strict.get("D67_6D_double_lattice_regulated") is False and strict.get("V62_GS_shift_0_2_status") == "FORMAL_5D_DIAGNOSTIC_ONLY" and strict.get("D67_status") == "CANDIDATE_NEW_ACTION_NOT_CONSTRUCTED" and strict.get("B3_T66_status") == "CONDITIONAL_ROUTE_AUDIT_ONLY" and strict.get("accepted_extension_count") == 0 and strict.get("same_action_microscopic_completion_found") is False and strict.get("V67_G1_closed") is False and strict.get("V67_G7_closed") is False and strict.get("closed_gates") == [] and strict.get("complete_theory") is False,
    }


def source_manifest() -> list[dict[str, Any]]:
    return [
        {"path": path.name, "exists": path.is_file(), "sha256": file_sha(path)}
        for path in (Path(__file__), TEST_PATH, *INPUTS.values())
    ]


def build_report() -> dict[str, Any]:
    v66 = load_bound("v66_master")
    index = load_bound("v67_index_route")
    g7 = load_bound("v67_g7_route")
    a = frozen_v66_row(v66, "A60")
    c = frozen_v66_row(v66, "C")
    old_b = frozen_v66_row(v66, "B66")
    b = b67_row(v66, index, g7)
    gates = master_gates(v66)
    scope = regression_scope()
    if (
        scope["file_count"] != EXPECTED_REGRESSION_FILES
        or scope["test_count"] != EXPECTED_REGRESSION_TESTS
    ):
        raise RuntimeError("unexpected V59-V67 route regression scope")

    report: dict[str, Any] = {
        "version": VERSION,
        "date": DATE,
        "schema": SCHEMA,
        "status": STATUS,
        "question": (
            "Do the V67 index-changing candidate and G7 stress audit close any gate "
            "inside one bound action?"
        ),
        "input_core_hashes": copy.deepcopy(EXPECTED_CORES),
        "lineage": {
            "parent_V66_master_core": v66["core_sha256"],
            "V67_index_route_core": index["core_sha256"],
            "V67_G7_route_core": g7["core_sha256"],
            "superseded_route": {
                "route_id": "B66",
                "source_row_sha256": object_sha(old_b),
                "historical_artifact_modified": False,
            },
            "replacement_route": {
                "route_id": "B67",
                "accepted": False,
                "current_bound_action_status": "REJECTED",
            },
            "route_A60_row_sha256_unchanged": object_sha(a),
            "route_C_row_sha256_unchanged": object_sha(c),
            "supersession_scope": "B66 to B67 only",
        },
        "upstream_status": {
            "V66_master": v66["status"],
            "V67_index_route": index["status"],
            "V67_G7_route": g7["status"],
        },
        "artifact_integrity": {
            "V66_and_V67_route_artifacts_modified": False,
            "A60_and_C_rows_preserved_exactly": True,
            "current_bound_Spin11_action_status": "REJECTED",
        },
        "regression_scope": scope,
        "route_matrix": [a, b, c],
        "consolidated_theory_card": theory_card(b),
        "acceptance_criteria": copy.deepcopy(v66["acceptance_criteria"]),
        "cross_route_composition_rule": {
            "logical_rule": (
                "D67, H66, T66 and B3_IR are separate candidate or diagnostic objects. "
                "No index, anomaly, unification or proton evidence transfers between them "
                "without one explicit action and a full recomputation."
            ),
            "cross_route_splicing_allowed": False,
            "aggregated_gate_closure": False,
        },
        "comparison_conclusion": {
            "heterotic_A60": v66["comparison_conclusion"]["heterotic"],
            "Spin11_B67": (
                "Current action REJECTED. D67 is a new-action candidate; H66/T66 and "
                "B3_IR remain conditional diagnostics with no lifetime or local embedding."
            ),
            "gauged_U1R_C": v66["comparison_conclusion"]["gauged_U1R"],
            "frontier": "Accept a branch only after all obligations close in one versioned action.",
        },
        "strict_master_decision": {
            "current_Spin11_action_status": "REJECTED",
            "V64_null_mode_stands_in_current_action": True,
            "exact_zero_removed_in_D67_inherited_5D_candidate_operator": True,
            "split_bulk_5D_status": "UNCLASSIFIED",
            "D67_6D_double_lattice_regulated": False,
            "V62_GS_shift_0_2_status": "FORMAL_5D_DIAGNOSTIC_ONLY",
            "physical_colored_mass_certified": False,
            "D67_status": "CANDIDATE_NEW_ACTION_NOT_CONSTRUCTED",
            "B3_T66_status": "CONDITIONAL_ROUTE_AUDIT_ONLY",
            "accepted_extension_count": 0,
            "same_action_microscopic_completion_found": False,
            "V67_G1_closed": False,
            "V67_G7_closed": False,
            "closed_gates": [],
            "complete_theory": False,
            "honest_outcome": (
                "V67 proves an index-changing theorem for the inherited 5D candidate "
                "operator and sharpens the scoped T66 proton obstruction, but neither "
                "result is an accepted local action; "
                "the bound action remains REJECTED and G1-G8 remain OPEN."
            ),
        },
        "gate_ledger": gates,
        "source_policy": {
            "master_adds_no_new_literature_or_empirical_claim": True,
            "route_claim_boundaries_preserved": True,
            "proton_proxies_are_not_lifetimes": True,
        },
        "source_manifest": source_manifest(),
    }
    checks = recompute(report)
    report["integrity_checks"] = checks
    report["n_integrity_checks"] = len(checks)
    report["n_failed_integrity_checks"] = sum(not value for value in checks.values())
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise AssertionError("V67 master canonical core mismatch")
    try:
        checks = recompute(report)
    except Exception as exc:
        raise AssertionError(f"V67 master recomputation mismatch: {exc}") from exc
    failed = [name for name, ok in checks.items() if not ok]
    if report.get("integrity_checks") != checks:
        failed.append("cached_integrity_checks")
    if report.get("n_integrity_checks") != len(checks):
        failed.append("n_integrity_checks")
    if report.get("n_failed_integrity_checks") != sum(
        not value for value in checks.values()
    ):
        failed.append("n_failed_integrity_checks")
    if failed:
        raise AssertionError(f"V67 master recomputation mismatch: {failed}")


def render_markdown(report: Mapping[str, Any]) -> str:
    rows = {row["route_id"]: row for row in report["route_matrix"]}
    b = rows["B67"]
    d = b["D67_candidate_new_action"]
    spectral = d["spectral_index_repair"]
    light = spectral["light_singular_value"]
    sixdim = spectral["six_dimensional_nonimport"]
    geometry = d["geometry_and_6D_escape"]
    p = b["T66_B3_conditional_route_audit"]
    schur = p["t66_u_portal_schur_complement"]
    selector = p["unified_selector_one_sided_no_go"]
    selector_scan = selector["family_dependent_scan"]
    b3 = p["conditional_b3_ir_escape"]
    proxies = {row["branch"]: row for row in p["dimension_six_proton_proxy"]["rows"]}
    dim5 = p["dimension_five_portal_stress"]
    candidate_rows = "\n".join(
        f"| {row['id']} | {row['kind']} | {row['status']} | {row['accepted']} |"
        for row in b["candidate_matrix"]
    )
    gate_rows = "\n".join(
        f"| {row['gate']} | {row['status']} | {row['decision']} |"
        for row in report["gate_ledger"]
    )
    obligations = "\n".join(
        f"- {item}" for item in report["consolidated_theory_card"]["open_obligations"]
    )
    return f"""# V67 multipath G1 frontier master audit

Version: {report['version']}
Date: {report['date']}
Schema: {report['schema']}
Status: {report['status']}

## Result

The current bound Spin(11) action remains **REJECTED**. V67 contains two exact
advances, but neither is an accepted extension: D67 changes the chiral index in
the inherited 5D candidate operator, while the T66/B3 audit makes a scoped
proton obstruction explicit. No evidence is spliced between routes and G1-G8
remain OPEN.

Only B66 is superseded by B67. A60 and C are carried with their exact V66 row
hashes, {report['lineage']['route_A60_row_sha256_unchanged']} and
{report['lineage']['route_C_row_sha256_unchanged']}.

## D67 index-changing candidate

The old rectangular operator is
`{spectral['minimal_index_change']['old_operator']}`. Adding one opposite
chirality qR=2 row gives
`{spectral['minimal_index_change']['new_operator']}` with
`{spectral['minimal_index_change']['finite_determinant']}`. The finite checks
pass and the inherited 5D operator has no exact zero when M is nonzero.

This is not yet a physical exotic-mass result. The lowest root satisfies
`{light['exact_equation_for_inherited_5D_operator_below_first_KK_pole']}`, and
overlap can suppress it.
No numerical colored-mass floor has been certified.

This theorem is five-dimensional. A 5D split-bulk realization is
**{geometry['current_5D_action']['split_bulk_5D_status']}**, not excluded. For a
genuine 6D point-local coupling,
`{sixdim['point_local_double_KK_asymptotic']}`; its status is
**{sixdim['status']}**. The inherited tangent equation cannot be imported, and
the formal V62 GS shift (SU3,SU2)=(0,2) is not a derived 6D local coupling.

The current 5D walls do not admit an isolated Q-type local field. The proposed
{geometry['D67_6D_escape_candidate']['literature_geometry']} construction has
local group {geometry['D67_6D_escape_candidate']['local_group']}, but its status
is **{geometry['D67_6D_escape_candidate']['status']}**. Its Spin(11) parity
action, anomaly polynomial, wavefunctions, thresholds and UV completion are
open.

## T66 and B3 proton stress

Integrating out the T66 U pair gives exactly

`{schur['effective_superpotential_i_less_than_j']}`

At pre-Majorana matching it has DeltaB={schur['global_numbers']['Delta_B']},
DeltaL={schur['global_numbers']['Delta_L']} and
Delta(B-L)={schur['global_numbers']['Delta_B_minus_L']}. After the Majorana
inverse-mass insertion, the displayed `uc dc dc L Hu` operator has
DeltaB={schur['heavy_N_matching']['post_Majorana_field_numbers']['Delta_B']} and
DeltaL={schur['heavy_N_matching']['post_Majorana_field_numbers']['Delta_L']}.

The audited scoped, family-dependent determinant-permutation result is
**{selector['result']}**; its scan found
{selector_scan['counterexample_count']} counterexamples in
{selector_scan['charge_assignment_count']} charge assignments. It proves that
all conjugate portals cannot be forbidden under the stated h=0, structurally
full-rank Yukawa and GM-neutral assumptions; it does not prove a selector-allowed
Wilson coefficient is nonzero.

The displayed four-dimensional escape is {b3['name']}, but it remains
**{b3['classification']}**. Its standard linear residues vanish mod 3 and its
integer-parent cubic residue vanishes mod 9 within the stated scan ansatz. It
supplements, rather than replaces, inherited matter parity, and its different
component charges are not embedded on either current unified wall.

The frozen conditional gauge proxies give:

- H66: {proxies['H66']['central_proxy_lifetime_years']:.6e} years,
  central proxy pass = {proxies['H66']['central_proxy_passes']}.
- T66: {proxies['T66']['central_proxy_lifetime_years']:.6e} years,
  central proxy pass = {proxies['T66']['central_proxy_passes']}.

These are not lifetime predictions. At the illustrative common T66 threshold,
the unprotected dimension-five product would require
`abs(lambda rho theta_N D_flavour) <
{dim5['illustrative_common_T66_threshold']['maximum_abs_lambda_rho_thetaN_D']:.6e}`.

## Candidate isolation

| ID | Kind | Status | Accepted |
|---|---|---|---|
{candidate_rows}

No row is a same-action completion.

## Remaining obligations

{obligations}

## Established gates

| Gate | Status | Decision |
|---|---|---|
{gate_rows}

## Decision

{report['strict_master_decision']['honest_outcome']}

Regression scope: {report['regression_scope']['test_count']} top-level test functions
(before pytest parametrization) in
{report['regression_scope']['file_count']} files.
Core SHA-256: {report['core_sha256']}
"""


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--emit-json", action="store_true")
    parser.add_argument("--emit-markdown", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate(report)
    if args.write:
        write_outputs(report)
    if args.check:
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("stale V67 master JSON")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("stale V67 master Markdown")
    if args.emit_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.emit_markdown:
        print(render_markdown(report), end="")
    else:
        print(report["status"])
        print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
