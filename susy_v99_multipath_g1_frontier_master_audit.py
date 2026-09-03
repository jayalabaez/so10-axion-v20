"""Append the independently scoped F99 results; preserve all 26 old routes."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import susy_v91_multipath_g1_frontier_master_audit as common

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT/"SUSY_V99_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT/"SUSY_V99_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT/"test_susy_v99_multipath_g1_frontier_master_audit.py"
V98_PATH = ROOT/"SUSY_V98_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V99_PATH = ROOT/"SUSY_V99_QUOTIENT_OBSTRUCTIONS_NORMAL_PAIR_SECTION_AUDIT.json"
EXPECTED_CORES = {
    "v98_master": "a1032f9531a12a91bfeb1ba0c13fb3e7703a60a70982f65e7122d237c11083cf",
    "v99_route": "240bf71045bda94015027eccbaeebec93fc2caa8940a5dd100e914ad24330c4e",
}
HELPER_KEYS = ("determinant_root_descent", "spectator_replacement_anomaly", "normal_half_period_pairing", "original_section_elimination")
NEXT_ID = "F100_MODIFIED_EQUIVARIANT_ACTION_AND_ORIGINAL_SECTION_EXISTENCE"
STATUS = "V99_MASTER__FROZEN_REPAIR_OBSTRUCTIONS__QUANTIZED_SHARED_NORMAL_PAIR__CONDITIONAL_ORIGINAL_TRACE__ALL_BRANCH_GATES_OPEN"
canonical_sha, file_sha, load_bound = common.canonical_sha, common.file_sha, common.load_bound


def theory_card(route, rows, previous):
    f, m, n, g = (route[key] for key in HELPER_KEYS)
    lift = f["frozen_square_space_group_root_obstruction"]
    ambiguity = f["chosen_root_response_ambiguity"]
    minimal = m["minimal_sixteen_replacement_obstruction"]
    extended = m["bounded_regular_character_extensions"]
    pair = n["shared_reflected_U5_pair"]
    trace = g["quadratic_trace_construction"]["actual_original_member_formulas"]
    old = previous["consolidated_theory_card"]
    return {
        "accepted_extension_count": sum(bool(row["accepted"]) for row in rows),
        "bound_helper_core_hashes": {key: route[key]["core_sha256"] for key in HELPER_KEYS},
        "determinant_root": {
            "quantized_chosen_cover_response": copy.deepcopy(f["bound_V98_quantized_chosen_root_response"]),
            "D_holonomies_A_U_V": copy.deepcopy(lift["D_holonomies_A_U_V"]),
            "space_group_abelianization": lift["space_group_abelianization"],
            "frozen_equivariant_root_exists": lift["equivariant_square_root_on_unchanged_space_group_exists"],
            "root_choice_relative_phases": [r["combined_relative_phase"] for r in ambiguity["both_circle_spin_structure_tests"]],
            "specific_response_descends_after_forgetting_root": ambiguity["specific_V98_response_descends_after_forgetting_root"],
            "root_sign_scope": "natural stable Spin-c plus continuously extended Spin-c11 gauge restriction; C is not a flat finite-C8-only bundle on CP2",
            "changed_central_extension": copy.deepcopy(lift["explicit_changed_central_extension"]),
            "bare_eta_KT_failure_repaired": f["remaining_obligations"]["bare_eta_KT_representation_problem_resolved"],
            "full_relative_action_constructed": f["remaining_obligations"]["boundary_corner_trivializations_and_full_Dai_Freed_regulator_constructed"],
        },
        "spectator_replacement": {
            "actual_slots": copy.deepcopy(m["actual_old_slots"]),
            "minimal_scope": minimal["scope"],
            "minimal_actual_removal_vectors_checked": minimal["enumerated_actual_removal_count"],
            "minimal_rational_survivors": copy.deepcopy(minimal["rationally_factorizing_removals"]),
            "moment_equation": minimal["necessary_and_sufficient_quartic_equation_after_first_two"],
            "unique_c_shift": copy.deepcopy(minimal["unique_c_shift"]),
            "analytic_proof": copy.deepcopy(minimal["analytic_proof"]),
            "bounded_twenty_and_twenty_four_extensions": copy.deepcopy(extended),
            "full_independent_flavor_and_spectrum": copy.deepcopy(m["full_independent_flavor_replacement"]),
            "flavor_GS_and_representation_scope": copy.deepcopy(m["flavor_GS_and_full_representation_scope"]),
            "same_action_spectrum_and_GS_constructed": m["terminal_decision"]["same_action_SUSY_spectrum_or_quantized_GS_completion_constructed"],
        },
        "normal_pair": {
            "single_target": n["exact_normal_period_lattice"]["target_T"],
            "obstruction_order": n["closed6_order_two_obstruction"]["exact_order"],
            "minimum_positive_quantized_stack": n["exact_normal_period_lattice"]["minimum_positive_stack_for_quantization_on_this_category"],
            "closed6_sign": n["closed6_order_two_obstruction"]["phase"],
            "common_reflected_pair": copy.deepcopy(pair),
            "separate_obstructions": copy.deepcopy(n["separate_obstructions_retained"]),
            "normal_pair_is_an_independent_local_repair": n["terminal_decision"]["independent_local_normal_repair_accepted"],
        },
        "original_section": {
            "coefficient_payload_sha256": g["coefficient_payload_sha256"],
            "original_equation_list_sha256": g["original_equation_list_sha256"],
            "exceptional_chart": copy.deepcopy(g["exceptional_chart_exact_equations"]),
            "universal_trace_identity": copy.deepcopy(g["quadratic_trace_construction"]["universal_group_law_identity"]),
            "actual_trace": copy.deepcopy(trace),
            "repeated_root_and_descent": copy.deepcopy(g["repeated_root_and_descent"]),
            "conditional_height_and_rank": copy.deepcopy(g["conditional_height_and_rank_compatibility"]),
            "limitations": copy.deepcopy(g["limitations"]),
        },
        "actual_original_MW_torsion_order": old["actual_original_MW_torsion_order"],
        "actual_original_MW_free_rank": None,
        "actual_original_MW_free_rank_bounds": copy.deepcopy(old["actual_original_MW_free_rank_bounds"]),
        "actual_original_nonzero_section_constructed": False,
        "all_original_cubic_sections_excluded": False,
        "all_original_rational_sections_excluded": False,
        "conditional_unit_charge_section_height_S_F": copy.deepcopy(old["conditional_unit_charge_section_height_S_F"]),
        "conditional_doubled_charge_section_height_S_F": copy.deepcopy(old["conditional_doubled_charge_section_height_S_F"]),
        "full_quantum_anomaly_cancelled": False,
        "same_action_spectrum_and_geometry_realized": False,
        "soft_spectrum_unification_cosmology_complete": False,
        "experimental_confirmation": False,
    }


def content():
    previous = load_bound(V98_PATH, EXPECTED_CORES["v98_master"])
    route = load_bound(V99_PATH, EXPECTED_CORES["v99_route"])
    rows = copy.deepcopy(previous["route_matrix"])
    if len(rows) != 26 or [r["ordinal"] for r in rows] != list(range(1, 27)):
        raise RuntimeError("all 26 ordered historical routes are required")
    if route["input_core_hashes"]["v98_master"] != EXPECTED_CORES["v98_master"] or route["next_required_action"]["id"] != NEXT_ID:
        raise RuntimeError("V99 lineage or F100 obligation changed")
    if not previous["lineage"]["canonical_V21_gate_scope_unchanged"]:
        raise RuntimeError("canonical V21 scope changed")
    for key in HELPER_KEYS:
        if route[key].get("core_sha256") != canonical_sha(route[key]):
            raise RuntimeError("noncanonical V99 helper: "+key)
    if set(route["gate_ledger"]) != {"G"+str(i) for i in range(1, 9)} or not all(v.startswith("OPEN:") for v in route["gate_ledger"].values()):
        raise RuntimeError("V99 may not promote a branch gate")
    decision = route["terminal_decision"]
    if decision["closed_gates"] or decision["theory_complete"] or decision["same_action_microscopic_parent_accepted"]:
        raise RuntimeError("V99 does not accept a complete microscopic parent")
    rows.append({
        "ordinal": 27, "route_id": "B99",
        "name": "frozen determinant-root and spectator replacement obstructions, shared normal response and conditional original quadratic trace",
        "accepted": False, "same_action_microscopic_completion": False,
        "selected_exact_scaffolds": [
            "the frozen square-space-group determinant has no equivariant square root; the explicit changed central extension is not installed",
            "the chosen-root eta-plus-cup response changes sign on a liftable continuous quotient root-choice test",
            "all minimal sixteen-for-sixteen replacements fail rational bulk factorization; bounded twenty/twenty-four extensions fail rational, quotient or projector tests",
            "the natural Spin-c normal obstruction has exact order two and the shared reflected pair has an integer eta-plus-cup response",
            "the exceptional repeated-root chart is excluded; a distinct-root chart solution would give a primitive original height-four trace without requiring a square K discriminant",
        ],
    })
    criteria = [
        ("A1", "frozen equivariant determinant root", "REJECTED_TRANSLATION_CHARACTER"),
        ("A2", "forgetting the root in the V98 continuous chosen-root response", "REJECTED_EXACT_ETA_PLUS_CUP_SIGN"),
        ("A3", "minimal actual spectator replacement with frozen other bulk matter", "REJECTED_ANALYTIC_MOMENT_OBSTRUCTION"),
        ("A4", "twenty/twenty-four regular-character replacements", "REJECTED_WITHIN_EXHAUSTIVE_BOUNDED_ANSATZ"),
        ("A5", "shared reflected normal-pair quantization", "PASS_STATED_CLOSED5_CATEGORY_NOT_INDEPENDENT_GLUE"),
        ("A6", "exceptional repeated-root exclusion and original quadratic trace", "PASS_EXCLUSION_AND_CONDITIONAL_TRACE_EXISTENCE_OPEN"),
        ("A7", "same-action full microscopic parent and original MW generator", "OPEN_NO_ACCEPTED_PARENT"),
    ]
    return {
        "schema": "susy_v99_multipath_g1_frontier_master_v1", "version": "V99", "status": STATUS,
        "input_core_hashes": copy.deepcopy(EXPECTED_CORES),
        "lineage": {"parent_master": "V98", "new_route": "B99", "parent_route_count": 26,
                    "parent_route_matrix_sha256": canonical_sha(previous["route_matrix"]),
                    "canonical_V21_gate_scope_unchanged": True,
                    "this_master_gate_scope": "separate SUSY/C8 completion branch"},
        "route_matrix": rows,
        "acceptance_criteria": [{"id": key, "requirement": need, "status": status} for key, need, status in criteria],
        "consolidated_theory_card": theory_card(route, rows, previous),
        "cross_sector_scope_checks": copy.deepcopy(route["cross_sector_scope_checks"]),
        "supersession_ledger": copy.deepcopy(route["supersession_boundary"]),
        "strict_master_decision": copy.deepcopy(decision),
        "gate_ledger": copy.deepcopy(route["gate_ledger"]),
        "next_required_action": copy.deepcopy(route["next_required_action"]),
        "primary_sources": copy.deepcopy(route["primary_sources"]),
        "artifact_hashes": {"generator_sha256": file_sha(Path(__file__)), "test_sha256": file_sha(TEST_PATH)},
    }


def build_report():
    report = content()
    report["core_sha256"] = canonical_sha(report)
    return report


def validate_report(report):
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("V99 master core is noncanonical")
    body = copy.deepcopy(report)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("V99 master arithmetic, lineage or scope changed")


def render_markdown(report):
    card = report["consolidated_theory_card"]
    if card["accepted_extension_count"] != 0:
        raise RuntimeError("readable master cannot conceal an accepted extension")
    paragraphs = [
        "# SUSY V99 multipath frontier master",
        "Status: "+report["status"], "Core SHA256: "+report["core_sha256"],
        "The next step was executed. V99 makes the failed repair assumptions precise and supplies scoped mathematical constructions. Accepted extensions: 0. All eight gates in this SUSY/C8 branch remain OPEN; canonical V21 evidence is unchanged.",
        "## Determinant-root response: two independent obstructions",
        "The frozen space group has abelianization C4 x C2 and determinant character D(A)=1, D(U)=D(V)=-1. This translation character is not a square. An explicit minimal nonsplit central C2 extension admits a root, but changes both C2 stabilizers to C4 and is not the original orbifold action. It does not repair the bare eta operators' remaining internal/tangential KT relation.",
        "Independently, on the natural Spin-c/continuous-gauge restriction CP2 x S1, two chosen roots projecting to the same quotient connection change the V98 response by -1. The eta contribution is +1; the differential cup contributes 3/2 modulo integers. Both circle spin structures give the same sign. This is not a finite-C8-only background or a full physical Gammahat classification. V98's quantization with a chosen root is valid; forgetting that data is not.",
        "## Particle replacement: actual slots, exact rejection",
        "Four actual neutral orbit copies provide 16 hyper slots and remove no free constant modes. But all 2,956 permitted sixteen-for-sixteen charge-count replacements fail rational smooth anomaly factorization with the old a,b, tensors and other bulk matter fixed. The exact reduced equation is 108B-3456A-A^2=0, with A=24-sum_removed(q/2)^2 and B=72-sum_removed(q/2)^4. Congruences and bounded moments exclude every solution; enumeration confirms the proof.",
        "All three 20-hyper regular-character variants also fail. Six 24-hyper variants leave one rational scout: c'=(-464,-144), removing 19 neutral and 5 charge-eight hypers. Its quotient source is (-57,-37/2), not integral. The actual neutral representation independently requires an even hyper removal, excluding 19. Larger additions, other carriers and changed tensor content are not excluded by this bounded result.",
        "The original 16-hyper counterprofile would add eight free N1 chirals and retain independent flavor anomalies. Primitive SU4 c4 and z*c3 terms are not Green-Schwarz products. A global flavor anomaly alone is not automatically inconsistent; the cancellation requirement matters. No full unchanged Sp267 representation, mass lifting or accepted SUSY action is constructed.",
        "## Positive response result: the normal obstruction has order two",
        "For natural Spin-c determinant N with x=c1(N), T=-x*c2(E)/2+x^3/8+x*p1/8 satisfies 2T=J_x(x)-15J_x(0)-x*c2(E). The integer eta levels (1,-15) and integral cup define a quantized response on closed5, including nonbounding backgrounds. The single target has period 3/2 on CP2 x CP1, so the minimal positive stack is exactly 2.",
        "On one shared background, E0=A+B and E1=A+B* make the summed normal target quantized by xi_c(N)-15xi_c(1)-hol[x*(c2(A)+c2(B))]. This does not split into independent absolute wall repairs. The single-wall closed6 sign, bare eta KT obstruction, separate SU2 sign and finite-defect gluing remain explicit obligations.",
        "## Original geometry: a conditional point construction",
        "The all-linear-remainders-zero chart retains six equations in z,H over C(X), z=r^2 nonzero and 2H-alpha nonzero. Its two K roots give points whose group-law sum has explicit original-field coordinates of T-degrees (4,6), leading terms 36T^4/z and -216T^6/r^3. The construction needs no square K discriminant. Nonsquare z still prevents this trace from descending.",
        "The exact affine D6 calculation bounds every nonzero geometric section's height below by 5/2. A realized trace has height 4 and is primitive; a repeated K root would imply a half-trace point of height 1 and is therefore excluded. The remaining two cubic points would be independent over the constant extension containing their roots. A rank-at-least-two conclusion over the original field requires a chart solution with both z and the K discriminant square, which has not been found.",
        "If a target section of height 37 or 148 also exists alongside the original trace, the two cannot generate a rank-one group: 37/4 and 37 are not rational squares. Neither existence hypothesis is established. The original rank remains 0..11, torsion remains 1, and no full threefold height divisor or physical U1 normalization is claimed.",
        "## Acceptance ledger",
    ]
    criteria = "\n".join("- "+row["id"]+": "+row["status"]+" — "+row["requirement"] for row in report["acceptance_criteria"])
    tail = ["## Next obligation", report["next_required_action"]["id"], report["next_required_action"]["primary"],
            report["next_required_action"]["parallel"], "No complete theory, same-action quantum completion or experimental confirmation is claimed. All 26 earlier route records are preserved.", "## Primary sources"]
    sources = "\n".join("- ["+row["use"]+"]("+row["url"]+")" for row in report["primary_sources"])
    return "\n\n".join(paragraphs)+"\n\n"+criteria+"\n\n"+"\n\n".join(tail)+"\n\n"+sources+"\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate_report(report)
    if args.write:
        OUT_JSON.write_text(json.dumps(report, sort_keys=True, indent=2)+"\n", encoding="utf-8", newline="\n")
        OUT_MD.write_text(render_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps({"version": "V99", "core_sha256": report["core_sha256"], "route_count": len(report["route_matrix"]),
                      "accepted_extensions": report["consolidated_theory_card"]["accepted_extension_count"], "closed_gates": [], "next": NEXT_ID}, indent=2))


if __name__ == "__main__":
    main()
