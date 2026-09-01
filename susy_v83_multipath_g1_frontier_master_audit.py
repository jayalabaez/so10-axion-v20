#!/usr/bin/env python3
"""V83 fail-closed master for the cyclic/WCS/instanton-string frontier.

The master binds the frozen V82 master and the V83 route.  V83 constructs an
exact smooth-bulk cyclic C4 quotient, the Q4 torsion linking form and even-U
reference quadratic shadow, the local rank-one 4 SO(11) instanton-string
worldsheet, and a compact T2 x S4 cohomological source-incidence witness.

These gains do not provide the full square-space-group H_Gamma lift.  A
Spin(11)-center translation cocycle, nonunique bulk kernel, missing localized
and BV/regulator descents, unevaluated modified eta invariant, unselected
differential WCS refinement, h0 hidden extension for delta, and absent
on-shell source glue remain.  No extension is accepted, the current action
remains rejected, and all G1--G8 gates remain open.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
V82_MASTER_PATH = ROOT / "SUSY_V82_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V83_ROUTE_PATH = ROOT / "SUSY_V83_CYCLIC_PARENT_WCS_INSTANTON_STRING_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V83_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT / "SUSY_V83_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v83_multipath_g1_frontier_master_audit.py"

EXPECTED_CORES = {
    "v82_master": "bb9d2fe3c3369d4ed270ea299bd8e53d0ae911b2685269ab6ef85bd0f4f9455d",
    "v83_route": "a2133df04b79a28d87dc9248aa5fac52c9392137e21ce1099034a6cba2048456",
}

SCHEMA = "susy_v83_multipath_g1_frontier_master_audit_v1"
VERSION = "V83"
DATE = "2026-09-01"
STATUS = (
    "V83_MULTIPATH_G1_FRONTIER_MASTER_AUDIT__V82_MASTER_AND_V83_ROUTE_CORES_BOUND__"
    "CYCLIC_SMOOTH_BULK_C4_LIFT_EXACT__RECORDED_CYCLE_DATA_MATCH_V82_JQ__KERNEL_NONUNIQUE__"
    "FULL_GAMMA_TRANSLATION_AND_STRATIFIED_DESCENT_OPEN__"
    "MONNIER_MOORE_BARE_FORMULA_EXACT_SIGNATURE_TERM_ZERO__NUMERIC_MODIFIED_XI_OPEN__"
    "Q4_LINKING_AND_U_GAUSS_SUM_EXACT__REFERENCE_WCS_SHADOW_MINUS_ONE_ONLY__"
    "4SO11_INSTANTON_STRING_AND_COMPACT_SOURCE_INCIDENCE_EXACT__FULL_HGAMMA_D15_OPEN__"
    "DELTA_H0_EXTENSION_OPEN__TOTAL_MU4_CHARACTER_UNKNOWN__NO_ACCEPTED_EXTENSION__"
    "CURRENT_ACTION_REJECTED__G1_TO_G8_OPEN"
)


def canonical_sha(value: Any) -> str:
    body = copy.deepcopy(value)
    if isinstance(body, dict):
        body.pop("core_sha256", None)
    payload = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def normalized_file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_bound(path: Path, expected: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    embedded = value.get("core_sha256")
    if embedded != canonical_sha(value):
        raise RuntimeError(f"noncanonical parent core for {path.name}")
    if embedded != expected:
        raise RuntimeError(f"bound core mismatch for {path.name}")
    return value


def route_matrix(v82: Mapping[str, Any], v83: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = [copy.deepcopy(row) for row in v82["route_matrix"]]
    rows.append(
        {
            "ordinal": len(rows) + 1,
            "route_id": "B83",
            "name": "cyclic bulk parent, Q4 WCS shadow and 4 SO(11) instanton-string adjudication",
            "same_action_microscopic_completion": False,
            "accepted": False,
            "selected_open_candidates": v83["candidate_adjudication"]["selected_ids"],
        }
    )
    return rows


def acceptance_criteria() -> list[dict[str, str]]:
    rows = [
        ("A1", "V82 master and V83 route canonical lineage", "PASS_EXACT"),
        ("A2", "charged-hyper Sp(3) half-angle root", "PASS_EXACT"),
        ("A3", "combined cyclic rotation fourth power in diagonal kernel", "PASS_EXACT"),
        ("A4", "smooth-bulk field center parities descend", "PASS_EXACT"),
        ("A5", "smooth-bulk center kernel uniquely selected", "OPEN_TWO_CHOICES"),
        ("A6", "recorded cyclic cycle-data projection matches jq(q)", "PASS_EXACT_DATA_MATCH_ORDER4"),
        ("A7", "full square-space-group translation relations", "OPEN_Z11_COCYCLE"),
        ("A8", "SO(11) quotient escape", "REJECTED_STRONG_QUANTIZATION_B_NOT_IN_2U"),
        ("A9", "fixed-stratum and localized representation descent", "OPEN_UNCONSTRUCTED"),
        ("A10", "all BV/BRST and regulator representation descents", "OPEN_UNCONSTRUCTED"),
        ("A11", "Monnier-Moore bare character formula", "PASS_EXACT_SYMBOLIC"),
        ("A12", "U-lattice signature eta term", "PASS_EXACT_ZERO"),
        ("A13", "modified eta xi_Rprime on lifted Q4", "OPEN_UNEVALUATED"),
        ("A14", "V81 ordinary spin-half eta shadow as physical phase", "REJECTED_WRONG_OPERATOR"),
        ("A15", "Q4 torsion linking form", "PASS_EXACT_PERFECT"),
        ("A16", "g=u+2v self-linking", "PASS_EXACT_ONE_HALF"),
        ("A17", "even-U normalized reference Gauss sum", "PASS_EXACT_ONE"),
        ("A18", "flat even-U reference WCS shadow", "PASS_EXACT_MINUS_ONE"),
        ("A19", "reference shadow equals physical differential WCS", "OPEN_NOT_SELECTED"),
        ("A20", "raw and Arf-normalized algebraic refinement ambiguity", "PASS_EXACT_256_REFINEMENTS_EIGHT_PAIRS"),
        ("A21", "total bare-times-WCS character", "OPEN_UNKNOWN_MU4"),
        ("A22", "delta equals twice the half decoration", "PASS_EXACT"),
        ("A23", "ordinary complex eta detects epsilon", "PASS_EXACT_ONE_HALF"),
        ("A24", "ordinary complex eta detects delta", "PASS_EXACT_ZERO_MOD1"),
        ("A25", "delta h0 hidden extension", "OPEN_ZERO_OR_ORDER2"),
        ("A26", "formal half-eta is a bordism character", "REJECTED_W8_TILDE_FILLING_AMBIGUITY"),
        ("A27", "h=0 gauge/anomaly/matter subsector matches local rank-one 4 SO(11) data", "PASS_EXACT_SUBSECTOR"),
        ("A28", "unit instanton-string (0,4) Sp(k) quiver", "PASS_PUBLISHED_LOCAL_SECTOR"),
        ("A29", "one-string full central charges", "PASS_EXACT_42_54"),
        ("A30", "one-string interacting central charges", "PASS_EXACT_38_48"),
        ("A31", "compact T2 x S4 source-incidence equation", "PASS_EXACT_COHOMOLOGICAL"),
        ("A32", "on-shell half-BPS compact background", "OPEN_UNCONSTRUCTED"),
        ("A33", "differential WCS/worldsheet source glue", "OPEN_UNCONSTRUCTED"),
        ("A34", "pure instanton tower realizes Q4 residues", "REJECTED_MOD4_PARITY"),
        ("A35", "topology and KSV select unique integral Q4 charge", "REJECTED_INFINITE_FAMILIES"),
        ("A36", "full H_Gamma D15 defect anomaly/fusion", "OPEN_UNCONSTRUCTED"),
        ("A37", "same-action microscopic completion", "OPEN_FAILED"),
        ("A38", "spectrum, vacuum, thresholds, cosmology and phenomenology", "BLOCKED_BY_ACTION"),
    ]
    return [{"id": key, "requirement": req, "status": status} for key, req, status in rows]


def build_report() -> dict[str, Any]:
    v82 = load_bound(V82_MASTER_PATH, EXPECTED_CORES["v82_master"])
    v83 = load_bound(V83_ROUTE_PATH, EXPECTED_CORES["v83_route"])
    routes = route_matrix(v82, v83)
    previous = v82["strict_master_decision"]
    current = v83["terminal_decision"]
    cyclic = v83["smooth_bulk_cyclic_parent_audit"]
    bare = v83["regulated_bare_anomaly_contract"]
    wcs = v83["Q4_linking_and_reference_WCS_audit"]
    delta = v83["relative_delta_hidden_extension_audit"]
    string = v83["instanton_string_and_compact_source_audit"]
    lifts = v83["infinite_charge_lift_nonselection_audit"]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "input_core_hashes": {
            "V82_master": v82["core_sha256"],
            "V83_route": v83["core_sha256"],
        },
        "lineage": {
            "parent_master": "V82",
            "new_route": "B83",
            "parent_route_count": len(v82["route_matrix"]),
            "parent_route_matrix_sha256": canonical_sha(v82["route_matrix"]),
            "supersession_scope": v83["lineage"]["supersession_scope"],
        },
        "route_matrix": routes,
        "acceptance_criteria": acceptance_criteria(),
        "gate_ledger": v83["gate_ledger"],
        "consolidated_theory_card": {
            "current_action_status": current["current_action_status"],
            "research_program_status": current["research_program_status"],
            "accepted_extension_count": sum(1 for row in routes if row["accepted"]),
            "selected_open_candidates": v83["candidate_adjudication"]["selected_ids"],
            "strongest_same_parent_scaffold": (
                "h=0 local 4 SO(11) tensor branch + smooth-bulk cyclic C4 quotient + exact-order-four jq(Q4) shadow + "
                "compact T2 x S4 source incidence, with full Gammahat/BV/regulator/WCS glue still missing"
            ),
            "exact_gains": [
                "charged-hyper Sp(3) root completes the five-factor cyclic central fourth power",
                "all displayed smooth-bulk center parities descend through the diagonal quotient",
                "the recorded cyclic cycle data project to the same Spin(11) bundle and order-four class as V82 jq(q)",
                "bulk fields leave exactly two center kernels containing the rotation fourth power",
                "the unrepaired square-space-group relation is localized to a Spin(11)-center translation cocycle",
                "the canonical Monnier-Moore bare character is fixed and the U signature term vanishes",
                "Q4 torsion linking matrix and g self-linking are exact",
                "the even-U reference Gauss sum is one and its flat qhat shadow is minus one",
                "256 algebraic refinement characters give eight joint phase pairs, proving the linking form and primary torsion class alone do not select the physical WCS phase",
                "delta is sharpened to the h0 multiplication-by-two hidden extension with a degree-eight obstruction to half-eta promotion",
                "the h=0 gauge/anomaly/matter subsector matches the local rank-one 4 SO(11) tensor-branch data",
                "the unit instanton string has a published (0,4) Sp(k) worldsheet with full central charges (42,54)",
                "T2 x S4 with a Spin(11) instanton and charge-b string solves the compact cohomological source equation",
                "pure instanton stacks cannot realize either optional Q4 residue",
                "infinite positive formal lifts prove topology and conditional KSV screens cannot select a unique Q4 charge",
            ],
            "retired_shortcuts": [
                "calling a single cyclic quotient the full square-orbifold parent",
                "ignoring the charged-hyper Sp(3) center when taking the rotation fourth power",
                "using smooth adjoint/vector matter to choose the Spin(11) global center kernel",
                "killing the Spin(11) center despite the b not in 2U strong-quantization obstruction",
                "calling V81's ordinary complex spin-half eta shadow a physical bare phase",
                "calling the flat even-U reference shadow the physical differential WCS holonomy",
                "choosing a finite mu4 counterterm without declaring a changed quantum integrand",
                "formally dividing the integer delta eta invariant by two without an eight-dimensional parity theorem",
                "applying the nondegenerate KSV positive-level formula to Q=b instanton strings",
                "calling compact cohomological source incidence an on-shell half-BPS compactification",
                "using a stack of b strings for an odd-first-coordinate Q4 residue",
                "assuming necessary positivity/unitarity screens select a unique integral charge",
            ],
            "remaining_global_blockers": v83["open_obligations"],
        },
        "strict_master_decision": {
            "inherited_AHSS_through_E3": previous["inherited_AHSS_through_E3"],
            "inherited_AHSS_E3_total_order": previous["inherited_AHSS_E3_total_order"],
            "inherited_split_Z4_proved": previous["inherited_split_Z4_proved"],
            "inherited_qhat_Q4_reduced_order": previous["qhat_Q4_reduced_order"],
            "smooth_bulk_cyclic_C4_lift_constructed": current["smooth_bulk_cyclic_C4_lift_constructed"],
            "cycle_level_H78_shadow": cyclic["constructed_object"]["cycle_level_H78_shadow"],
            "cycle_data_projection": cyclic["constructed_object"]["cycle_data_projection_to_reduced_H78"],
            "functorial_HGamma_to_H78_forgetful_map_constructed": cyclic["constructed_object"]["functorial_HGamma_to_H78_forgetful_map_constructed"],
            "bulk_kernel_choices_containing_rotation": cyclic["bulk_kernel_nonuniqueness"]["subgroups_containing_rotation_fourth_power"],
            "unique_global_center_kernel_selected": current["unique_global_center_kernel_selected"],
            "translation_relation_defect": cyclic["square_space_group_relation_cocycle"]["choice_U_equals_V_equals_what_relation_defects"]["AVAinvU"],
            "SO11_global_form_route_passes_quantization": cyclic["square_space_group_relation_cocycle"]["SO11_global_form_route_passes_quantization"],
            "full_Gammahat_space_group_constructed": current["full_Gammahat_space_group_constructed"],
            "full_HGamma_parent_lift_constructed": current["full_HGamma_parent_lift_constructed"],
            "bare_character_target": bare["exact_target"],
            "U_signature": bare["lattice_signature_term"]["signature"],
            "physical_bare_phase_evaluated": current["physical_bare_phase_evaluated"],
            "Q4_linking_matrix": wcs["linking_form"]["matrix_mod1"],
            "Q4_g_self_linking": wcs["linking_form"]["L_g_g"],
            "reference_Gauss_sum": wcs["even_U_reference_quadratic_refinement"]["normalized_Gauss_sum"],
            "reference_qhat_WCS_shadow": current["reference_qhat_WCS_shadow"],
            "physical_WCS_phase_evaluated": current["physical_WCS_phase_evaluated"],
            "total_anomaly_character_exponent": wcs["total_anomaly_character_constraint"]["current_total_character_exponent"],
            "bare_times_WCS_identity_proved": current["bare_times_WCS_identity_proved"],
            "delta_equals_two_epsilon": delta["classes"]["delta_equals_two_epsilon"],
            "epsilon_complex_rho": delta["ordinary_complex_eta"]["epsilon_vector_rho"],
            "delta_complex_rho_mod1": delta["ordinary_complex_eta"]["delta_complex_rho_mod1"],
            "delta_Adams_candidate": delta["Adams_diagnosis"]["candidate"],
            "delta_exact_order": current["delta_exact_order"],
            "local_4SO11_instanton_worldsheet_constructed": current["local_4SO11_instanton_worldsheet_constructed"],
            "instanton_string_full_central_charges": [
                string["known_local_0_4_worldsheet"]["one_string_full_cL"],
                string["known_local_0_4_worldsheet"]["one_string_full_cR"],
            ],
            "compact6_source_Y": string["compact_six_dimensional_source_incidence"]["Y_vector"],
            "compact6_source_residual": string["compact_six_dimensional_source_incidence"]["source_equation_residual"],
            "compact6_cohomological_source_incidence_constructed": current["compact6_cohomological_source_incidence_constructed"],
            "compact6_on_shell_half_BPS_solution_constructed": current["compact6_on_shell_half_BPS_solution_constructed"],
            "instanton_tower_reaches_Q4_residues": current["instanton_tower_reaches_Q4_residues"],
            "infinite_formal_Q4_charge_lifts": lifts["theorem"]["infinitely_many_distinct_integral_lifts"],
            "unique_integral_Q4_charge_lift_selected": current["unique_integral_Q4_charge_lift_selected"],
            "full_HGamma_D15_sector_constructed": current["full_HGamma_D15_sector_constructed"],
            "same_action_microscopic_completion_found": current["same_action_microscopic_completion_found"],
            "accepted_full_parent_action_exists": current["accepted_full_parent_action_exists"],
            "accepted_extension_count": sum(1 for row in routes if row["accepted"]),
            "current_action_status": current["current_action_status"],
            "research_program_status": current["research_program_status"],
            "closed_gates": current["closed_gates"],
            "theory_complete": current["theory_complete"],
            "honest_outcome": current["honest_outcome"],
        },
        "fail_closed_logic": {
            "G1_requires_full_HGamma_and_common_regulator": True,
            "G6_requires_on_shell_source_and_global_worldsheet_glue": True,
            "G8_requires_numeric_bare_and_physical_WCS_total_character_one": True,
            "reference_WCS_shadow_is_not_physical_value": True,
            "local_worldsheet_is_not_full_orbifold_D15": True,
            "cohomological_incidence_is_not_on_shell_solution": True,
            "accept_if_exact_local_gains_only": False,
        },
        "next_required_action": v83["next_required_action"],
        "primary_sources": copy.deepcopy(v83["primary_sources"]),
        "source_manifest": copy.deepcopy(v83["source_manifest"]),
        "artifact_hashes": {
            "line_ending_policy": "SHA256 after CRLF-to-LF normalization",
            "generator_sha256": normalized_file_sha(Path(__file__)),
            "test_sha256": normalized_file_sha(TEST_PATH),
        },
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    decision = report["strict_master_decision"]
    gains = "".join(f"- {item}\n" for item in report["consolidated_theory_card"]["exact_gains"])
    blockers = "".join(f"- {item}\n" for item in report["consolidated_theory_card"]["remaining_global_blockers"])
    gates = "".join(f"- {key}: {value}\n" for key, value in report["gate_ledger"].items())
    return f"""# V83 multipath G1 frontier master audit

Status: {report['status']}

Core SHA-256: {report['core_sha256']}

## Master decision

V83 adds route B83 without accepting an extension.  A smooth-bulk cyclic C4
quotient now exists, and its recorded cycle data project to
{decision['cycle_level_H78_shadow']}.  This matches the Spin(11) bundle and
exact order-four V82 class, but is not a functorial full-parent forgetful map.
The full square-space-group lift still fails
to exist: the translation presentation retains defect
{decision['translation_relation_defect']}, the smooth bulk leaves
{decision['bulk_kernel_choices_containing_rotation']} center-kernel choices,
and localized/BV/regulator descents are missing.

The canonical bare character is {decision['bare_character_target']}; the U
signature term is zero, but its modified eta invariant is unevaluated.  The
Q4 linking form and even-U reference Gauss sum are exact, giving a reference
qhat WCS shadow {decision['reference_qhat_WCS_shadow']}.  Refinement ambiguity
leaves the physical total character exponent {decision['total_anomaly_character_exponent']}.
Delta remains {decision['delta_exact_order']} at Adams candidate
{decision['delta_Adams_candidate']}.

The matching local 4 SO(11) gauge/anomaly/matter subsector's unit instanton
string is now concrete, with
full central charges {tuple(decision['instanton_string_full_central_charges'])}.
The compact T2 x S4 source equation has Y={tuple(decision['compact6_source_Y'])}
and residual {tuple(decision['compact6_source_residual'])}.  This is exact
cohomological incidence, not an on-shell H_Gamma compactification.  Pure
instanton stacks miss the Q4 residues and infinitely many formal nondegenerate
lifts prevent unique charge selection.

The current action remains {decision['current_action_status']}.  All eight
gates remain OPEN and the theory is not complete.

## Exact V83 gains

{gains}
## Remaining blockers

{blockers}
## Next required action

{report['next_required_action']['id']}:
{report['next_required_action']['primary_objective']}

## Gate ledger

{gates}"""


def validate_report(report: Mapping[str, Any]) -> None:
    if canonical_sha(report) != report["core_sha256"]:
        raise RuntimeError("V83 master core is not canonical")
    if report["input_core_hashes"]["V82_master"] != EXPECTED_CORES["v82_master"]:
        raise RuntimeError("V82 master lineage mismatch")
    if report["input_core_hashes"]["V83_route"] != EXPECTED_CORES["v83_route"]:
        raise RuntimeError("V83 route lineage mismatch")
    routes = report["route_matrix"]
    parent = load_bound(V82_MASTER_PATH, EXPECTED_CORES["v82_master"])
    if routes[:-1] != parent["route_matrix"]:
        raise RuntimeError("inherited V82 route matrix was mutated")
    if report["lineage"]["parent_route_matrix_sha256"] != canonical_sha(parent["route_matrix"]):
        raise RuntimeError("inherited V82 route-matrix hash changed")
    if len(routes) != report["lineage"]["parent_route_count"] + 1:
        raise RuntimeError("route matrix length changed")
    if routes[-1]["route_id"] != "B83" or routes[-1]["accepted"]:
        raise RuntimeError("B83 route adjudication changed")
    if [row["ordinal"] for row in routes] != list(range(1, len(routes) + 1)):
        raise RuntimeError("route ordinals are not consecutive")
    decision = report["strict_master_decision"]
    if not decision["smooth_bulk_cyclic_C4_lift_constructed"]:
        raise RuntimeError("exact cyclic lift gain was lost")
    if decision["cycle_level_H78_shadow"] != "jq(q) at the recorded cycle-data level":
        raise RuntimeError("cycle-level H78 shadow changed")
    projection = decision["cycle_data_projection"]
    if not projection["recorded_data_match_jq_q"] or projection["V82_order"] != 4:
        raise RuntimeError("recorded cycle-data projection changed")
    if decision["functorial_HGamma_to_H78_forgetful_map_constructed"]:
        raise RuntimeError("recorded cycle-data projection was promoted to a parent map")
    if decision["bulk_kernel_choices_containing_rotation"] != 2:
        raise RuntimeError("bulk kernel ambiguity changed")
    if decision["unique_global_center_kernel_selected"]:
        raise RuntimeError("global center kernel was falsely selected")
    if decision["translation_relation_defect"] != "z_11":
        raise RuntimeError("translation cocycle changed")
    if decision["SO11_global_form_route_passes_quantization"]:
        raise RuntimeError("strong-quantization-obstructed SO11 route was promoted")
    if decision["full_Gammahat_space_group_constructed"] or decision["full_HGamma_parent_lift_constructed"]:
        raise RuntimeError("cyclic lift was promoted to full parent")
    if decision["U_signature"] != 0 or decision["physical_bare_phase_evaluated"]:
        raise RuntimeError("bare anomaly contract changed")
    if decision["Q4_linking_matrix"] != [["1/2", "1/4"], ["1/4", "0"]]:
        raise RuntimeError("Q4 linking matrix changed")
    if decision["reference_Gauss_sum"] != "1" or decision["reference_qhat_WCS_shadow"] != "-1":
        raise RuntimeError("reference WCS result changed")
    if decision["physical_WCS_phase_evaluated"] or decision["total_anomaly_character_exponent"] != "UNKNOWN":
        raise RuntimeError("reference WCS shadow was promoted")
    if decision["bare_times_WCS_identity_proved"]:
        raise RuntimeError("unknown total character was promoted")
    if decision["delta_exact_order"] != "OPEN_ZERO_OR_ORDER2" or decision["delta_Adams_candidate"] != "h0*p":
        raise RuntimeError("delta hidden-extension contract changed")
    if not decision["local_4SO11_instanton_worldsheet_constructed"]:
        raise RuntimeError("local instanton-string gain was lost")
    if decision["instanton_string_full_central_charges"] != [42, 54]:
        raise RuntimeError("instanton-string central charges changed")
    if decision["compact6_source_Y"] != [-2, 1] or decision["compact6_source_residual"] != [0, 0]:
        raise RuntimeError("compact source incidence changed")
    if not decision["compact6_cohomological_source_incidence_constructed"]:
        raise RuntimeError("compact source witness was lost")
    if decision["compact6_on_shell_half_BPS_solution_constructed"]:
        raise RuntimeError("cohomological incidence was promoted")
    if decision["instanton_tower_reaches_Q4_residues"]:
        raise RuntimeError("instanton residue no-go changed")
    if not decision["infinite_formal_Q4_charge_lifts"] or decision["unique_integral_Q4_charge_lift_selected"]:
        raise RuntimeError("charge nonselection theorem changed")
    if decision["full_HGamma_D15_sector_constructed"]:
        raise RuntimeError("local string was promoted to full D15")
    accepted = [row["route_id"] for row in routes if row["accepted"]]
    if accepted or decision["accepted_extension_count"] != 0:
        raise RuntimeError("route acceptance ledger is nonempty")
    if decision["accepted_full_parent_action_exists"] or decision["same_action_microscopic_completion_found"]:
        raise RuntimeError("unaccepted action was promoted")
    if decision["closed_gates"] or decision["theory_complete"]:
        raise RuntimeError("a gate or theory was closed")
    if not all(value.startswith("OPEN") for value in report["gate_ledger"].values()):
        raise RuntimeError("gate ledger is not fail-closed")


def write_artifacts(report: Mapping[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")


def check_artifacts(report: Mapping[str, Any]) -> None:
    if json.loads(OUT_JSON.read_text(encoding="utf-8")) != report:
        raise RuntimeError(f"stale generated artifact: {OUT_JSON.name}")
    if OUT_MD.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError(f"stale generated artifact: {OUT_MD.name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate_report(report)
    if args.write:
        write_artifacts(report)
    if args.check:
        check_artifacts(report)
    print(report["status"])
    print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
