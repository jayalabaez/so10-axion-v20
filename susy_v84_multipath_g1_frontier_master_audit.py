#!/usr/bin/env python3
"""V84 fail-closed master for the Gammahat/C4F/F4 redesign frontier.

The master binds the frozen V83 master and the V84 route.  V84 exactly rejects
the unchanged five-factor square-space-group parent, constructs a minimal C4F
central-algebra and operator scaffold, computes the smooth Q4 bare phase up to
the still-unpinned conjugation convention, screens a sixteen-element algebraic
r2 coefficient family, and embeds the frozen anomaly/string lattice in F4.

The C4F and F4 objects are complementary redesign scaffolds, not one accepted
global action.  Fixed-stratum isotropy, a compact non-split I2* Weierstrass
model, the global Spin(11) form, the full BV/regulator complex, physical WCS
refinement, reducible-lift/junction glue, the candidate delta d3/d4/extension and an entangled half-BPS
relative source remain open.  No route is accepted and G1--G8 remain open.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
V83_MASTER_PATH = ROOT / "SUSY_V83_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V84_ROUTE_PATH = ROOT / "SUSY_V84_GAMMAHAT_BARE_PHASE_F4_HETEROTIC_STRING_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V84_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT / "SUSY_V84_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v84_multipath_g1_frontier_master_audit.py"

EXPECTED_CORES = {
    "v83_master": "b4a626429afcd28a9147c6b0ab2dd00e2304fc611c7499df1eb39dd76fa217f6",
    "v84_route": "ca9bbf53dcceb9fc422119e73b969b6d3b2c4db1619c8846134320768a26275f",
}

SCHEMA = "susy_v84_multipath_g1_frontier_master_audit_v1"
VERSION = "V84"
DATE = "2026-09-01"
STATUS = (
    "V84_MULTIPATH_G1_FRONTIER_MASTER_AUDIT__V83_MASTER_AND_V84_ROUTE_CORES_BOUND__"
    "UNCHANGED_FIVE_FACTOR_GAMMAHAT_REJECTED_EXACT__C4F_SPINOR_GRADING_REDESIGN_SELECTED_OPEN__"
    "SMOOTH_Q4_BARE_PHASE_PRIMITIVE_FOURTH_ROOT__ALGEBRAIC_R2_SCREEN_NONCANCELLING__"
    "F4_SO11_LIE_ALGEBRA_SPECTRUM_HETEROTIC_STRING_AND_REDUCIBLE_EFFECTIVE_RESIDUE_LIFTS_EXACT__"
    "PRODUCT_CAP_ORDINARY_ONLY__DELTA_SOURCE_PAGE_D3_D4_AND_EXTENSION_OPEN__NO_ACCEPTED_EXTENSION__"
    "CURRENT_ACTION_REJECTED__REDESIGN_PROGRAM_VIABLE__G1_TO_G8_OPEN"
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


def route_matrix(v83: Mapping[str, Any], v84: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = [copy.deepcopy(row) for row in v83["route_matrix"]]
    rows.append(
        {
            "ordinal": len(rows) + 1,
            "route_id": "B84",
            "name": "full-Gammahat no-go, C4F spinor grading and F4 heterotic-string redesign",
            "same_action_microscopic_completion": False,
            "accepted": False,
            "selected_open_candidates": v84["candidate_adjudication"]["selected_ids"],
        }
    )
    return rows


def acceptance_criteria() -> list[dict[str, str]]:
    rows = [
        ("A1", "V83 master and V84 route canonical lineage", "PASS_EXACT"),
        ("A2", "all central translation-deck choices enumerated", "PASS_EXACT_1024"),
        ("A3", "unchanged five-factor Kmin satisfies both Gammahat relations", "REJECTED_PURE_Z11_FORCED"),
        ("A4", "Kmax localized 16 descent", "REJECTED_ODD_SPIN11_CENTER"),
        ("A5", "Kmax SO11 Green-Schwarz quantization", "REJECTED_B_NOT_IN_2U"),
        ("A6", "C4F diagonal kernel keeps Spin11 faithful", "PASS_EXACT"),
        ("A7", "independent C4F gauge/flavor translation signs", "PASS_EXACT_8_OF_16_BY_PARITY"),
        ("A8", "C4F smooth descent and localized pure-center repair", "PASS_EXACT"),
        ("A9", "C4F charge/stabilizer ledger with fatal adjoint trilinear identified", "PASS_EXACT_SCOPED_OPERATOR_LEDGER"),
        ("A10", "C4F complete fixed-stratum isotropy", "OPEN_UNCONSTRUCTED"),
        ("A11", "C4F discrete and mixed Dai-Freed anomalies", "OPEN_UNCOMPUTED"),
        ("A12", "C4F full BV/regulator/WCS parent", "OPEN_UNCONSTRUCTED"),
        ("A13", "Q4 coefficient-line eta tables", "PASS_EXACT"),
        ("A14", "gauge-fixed Rarita Vec-1 contribution", "PASS_EXACT_ONE_HALF"),
        ("A15", "smooth cyclic Q4 bare phase conjugacy class", "PASS_EXACT_PRIMITIVE_FOURTH_ROOT"),
        ("A16", "determinant/Pfaffian convention selects +i versus -i", "OPEN_CONJUGATION_PIN"),
        ("A17", "reference even-U WCS cancels bare phase", "REJECTED_ODD_TOTAL_CHARACTER"),
        ("A18", "sixteen algebraic r2 coefficient shifts cancel", "REJECTED_SCREEN_WCS_ONLY_PLUS_MINUS_ONE"),
        ("A19", "algebraic r2 screen classifies physical refinements", "OPEN_FALSE_BOUNDARY_NOT_A_CLASSIFICATION"),
        ("A20", "odd reduced-Z4 counterterm extends globally", "OPEN_UNPROVED_AND_ACTION_CHANGING"),
        ("A21", "H2(F4) equals frozen U lattice with S=b and K=a", "PASS_EXACT"),
        ("A22", "so11 Lie algebra on F4 has frozen 3 vectors and 266 neutral hypers", "PASS_EXACT_SCAFFOLD"),
        ("A23", "F4 fiber is critical heterotic string with full (24,12)", "PASS_PUBLISHED_UV_SECTOR"),
        ("A24", "both Q4 residues have coefficient-minimal effective lifts", "PASS_EXACT"),
        ("A25", "residue lifts are elementary irreducible strings", "REJECTED_FIXED_SECTION_COMPONENTS"),
        ("A26", "junction worldsheet/inflow/WCS glue", "OPEN_UNCONSTRUCTED"),
        ("A27", "explicit compact non-split I2star Weierstrass model", "OPEN_UNCONSTRUCTED"),
        ("A28", "Mordell-Weil and global Spin11 form", "OPEN_UNCOMPUTED"),
        ("A29", "unwarped constant-scalar H=0 T2xS4 half-BPS ansatz", "REJECTED_NO_PARALLEL_S4_SPINOR"),
        ("A30", "ordinary product relative cap and source trivialization", "PASS_EXACT"),
        ("A31", "product cap double realizes Q4", "REJECTED_FORGETFUL_CLASS_ZERO_VS_ORDER4"),
        ("A32", "entangled warped/fluxed Q4-relative source", "OPEN_UNCONSTRUCTED"),
        ("A33", "potential incoming AHSS d3/d4 source pages survive to the required pages", "OPEN_PRECURSOR_PAGE_SURVIVAL_AND_DIFFERENTIAL_VALUES"),
        ("A34", "half-vector eta resolves delta", "REJECTED_FILLING_DEPENDENT"),
        ("A35", "delta exact order", "OPEN_ZERO_OR_ORDER2"),
        ("A36", "same-action microscopic completion", "REJECTED_EXACT_IN_SCOPED_ORDINARY_PARENT"),
        ("A37", "redesigned full parent action", "OPEN_C4F_F4_NOT_GLOBALLY_GLued"),
        ("A38", "vacuum, spectrum, thresholds, cosmology and phenomenology", "BLOCKED_BY_FULL_ACTION"),
    ]
    return [{"id": key, "requirement": requirement, "status": status} for key, requirement, status in rows]


def build_report() -> dict[str, Any]:
    v83 = load_bound(V83_MASTER_PATH, EXPECTED_CORES["v83_master"])
    v84 = load_bound(V84_ROUTE_PATH, EXPECTED_CORES["v84_route"])
    routes = route_matrix(v83, v84)
    prior = v83["strict_master_decision"]
    current = v84["terminal_decision"]
    gamma = v84["unchanged_five_factor_Gammahat_no_go"]
    c4f = v84["C4F_spinor_grading_repair_scout"]
    phase = v84["regulated_Q4_bare_and_WCS_audit"]
    f4 = v84["F4_SO11_heterotic_string_scaffold"]
    cap = v84["relative_cap_BPS_and_delta_audit"]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "input_core_hashes": {"V83_master": v83["core_sha256"], "V84_route": v84["core_sha256"]},
        "lineage": {
            "parent_master": "V83",
            "new_route": "B84",
            "parent_route_count": len(v83["route_matrix"]),
            "parent_route_matrix_sha256": canonical_sha(v83["route_matrix"]),
            "supersession_scope": v84["lineage"]["supersession_scope"],
        },
        "route_matrix": routes,
        "acceptance_criteria": acceptance_criteria(),
        "gate_ledger": copy.deepcopy(v84["gate_ledger"]),
        "consolidated_theory_card": {
            "current_action_status": current["current_action_status"],
            "research_program_status": current["research_program_status"],
            "accepted_extension_count": sum(1 for row in routes if row["accepted"]),
            "selected_open_candidates": v84["candidate_adjudication"]["selected_ids"],
            "strongest_redesigned_scaffold": "C4F diagonal spin-charge parent algebra plus F4 so11 Lie-algebra/heterotic UV lattice and reducible effective residue lifts",
            "exact_gains": [
                "every unchanged central translation lift forces the pure Spin11 center",
                "localized 16 descent and SO11 strong quantization independently reject the forced Kmax quotient",
                "a minimal non-R C4F factor repairs the central algebra without killing Spin11",
                "eight of sixteen independent C4F gauge/flavor sign rows pass exactly by the parity-sum theorem",
                "the C4F charge ledger preserves displayed Yukawa/rank terms while retaining V65's fatal spinor-adjoint warning",
                "the smooth cyclic Q4 bare Dai-Freed phase is a primitive fourth root up to conjugation",
                "the reference WCS branch and sixteen over-inclusive algebraic r2 coefficient-shift rows cannot cancel that phase",
                "F4 identifies S=b, F as the null heterotic charge, and K as the gravitational vector",
                "the so11 Lie algebra on the -4 section reproduces exactly three vectors and 266 neutral hypers",
                "the critical heterotic fiber string has interacting (20,6) and full (24,12) central charges",
                "S+F and 3S+F are the unique coefficient-minimal effective lifts of the two Q4 residues",
                "negative section intersection proves both residue lifts are reducible charge/curve configurations and only candidate junctions",
                "a bounding product cap gives an ordinary flat-ambiguity-free source trivialization",
                "the restricted direct product is non-BPS and every product double is bordism-distinct from Q4",
                "four explicit target-side AHSS maps adjacent to h0*p plus every r>=5 map are eliminated; potential incoming d3/d4 source-page survival and values remain open",
            ],
            "retired_shortcuts": [
                "repairing the unchanged Gammahat relations with flavor signs alone",
                "killing z11 and retaining localized spinors or the frozen odd component of b",
                "calling the C4F central algebra a complete stratified quantum parent",
                "selecting +i or -i without a determinant/Pfaffian convention pin",
                "identifying a Lambda/4Lambda coefficient scan with V78 local 2Y corrections or physical WCS refinements",
                "calling a topological F4 spectrum match an explicit compact Weierstrass model",
                "calling S+F or 3S+F an irreducible elementary string",
                "calling ordinary differential source trivialization WCS/worldsheet glue",
                "using an unwarped round S4 instanton product as a half-BPS solution",
                "using a product double to represent the Q4 order-four bordism class",
                "using filling-dependent half eta to decide delta",
            ],
            "remaining_global_blockers": copy.deepcopy(v84["open_obligations"]),
        },
        "strict_master_decision": {
            "inherited_AHSS_through_E3": prior["inherited_AHSS_through_E3"],
            "inherited_AHSS_E3_total_order": prior["inherited_AHSS_E3_total_order"],
            "inherited_split_Z4_proved": prior["inherited_split_Z4_proved"],
            "inherited_qhat_Q4_reduced_order": prior["inherited_qhat_Q4_reduced_order"],
            "unchanged_Gammahat_assignments_enumerated": gamma["finite_enumeration"]["raw"],
            "pure_Spin11_center_forced": current["pure_Spin11_center_forced"],
            "unchanged_five_factor_parent_rejected_exactly": current["unchanged_five_factor_parent_rejected_exactly"],
            "C4F_kernel_contains_pure_z11": c4f["extended_kernel"]["contains_pure_Spin11_center"],
            "C4F_Spin11_faithful": c4f["extended_kernel"]["Spin11_remains_faithful"],
            "C4F_direct_matched_representative_rows_pass": c4f["lift_choice"]["all_four_direct_bit_matched_rows_pass"],
            "C4F_independent_sign_rows_passing": c4f["lift_choice"]["independent_rows_passing"],
            "C4F_fatal_spinor_adjoint_target_vacuum_admissible": next(row for row in c4f["operator_audit"]["rows"] if row["operator"] == "Cbar 45 C")["target_vacuum_admissible"],
            "C4F_localized_pure_center_repaired": c4f["representation_descent"]["localized_16_pure_center_repaired"],
            "C4F_full_localized_isotropy_constructed": current["C4F_full_localized_isotropy_constructed"],
            "C4F_full_quantum_parent_constructed": current["C4F_discrete_anomaly_BV_WCS_parent_constructed"],
            "smooth_Q4_bare_phase_values": current["smooth_Q4_bare_phase_possible_values"],
            "smooth_Q4_bare_phase_primitive_fourth_root": phase["bare_character"]["primitive_fourth_root_proved"],
            "bare_phase_fully_BV_orientation_pinned": phase["bare_character"]["fully_BV_orientation_pinned"],
            "algebraic_r2_shift_WCS_counts": phase["algebraic_r2_coefficient_shift_screen"]["WCS_exponent_counts"],
            "algebraic_r2_screen_classifies_physical_refinements": False,
            "all_full_HGamma_WCS_refinements_fail": current["all_full_HGamma_WCS_refinements_fail"],
            "F4_section_fiber_canonical": [f4["geometry"]["section_S"], f4["geometry"]["fiber_F"], f4["geometry"]["canonical_K"]],
            "F4_so11_Lie_algebra_vector_and_neutral_hypers": [f4["so11_Lie_algebra_divisor_spectrum"]["vector_hypers"], f4["so11_Lie_algebra_divisor_spectrum"]["H_neutral"]],
            "F4_global_gauge_group_matched": f4["so11_Lie_algebra_divisor_spectrum"]["global_gauge_group_or_line_operator_match"],
            "critical_heterotic_full_central_charges": f4["critical_heterotic_fiber_string"]["full_cL_cR"],
            "minimal_effective_residue_lifts": [row["Q"] for row in f4["effective_Q4_residue_lifts"]["rows"]],
            "residue_lifts_irreducible": any(row["irreducible_curve"] for row in f4["effective_Q4_residue_lifts"]["rows"]),
            "explicit_compact_F4_Weierstrass_parent_constructed": current["explicit_compact_F4_Weierstrass_parent_constructed"],
            "restricted_T2xS4_half_BPS_solution_exists": current["restricted_T2xS4_half_BPS_solution_exists"],
            "ordinary_relative_product_cap_constructed": current["ordinary_relative_product_cap_constructed"],
            "product_cap_double_represents_Q4": current["product_cap_double_represents_Q4"],
            "delta_potential_associated_graded_candidate_differentials": cap["delta_AHSS_d3_d4_candidate_audit"]["potential_incoming_AHSS_differentials_on_associated_graded_candidate"],
            "delta_d3_source_page_survival_computed": cap["delta_AHSS_d3_d4_candidate_audit"]["source_page_precursor_audit"]["d3_source_E3_survival_computed"],
            "delta_d4_source_page_survival_computed": cap["delta_AHSS_d3_d4_candidate_audit"]["source_page_precursor_audit"]["d4_source_E4_survival_computed"],
            "delta_d3_value_computed": cap["delta_AHSS_d3_d4_candidate_audit"]["d3_value_computed"],
            "delta_d4_value_computed": cap["delta_AHSS_d3_d4_candidate_audit"]["candidate_d4_value_computed"],
            "delta_chain_level_candidate_identification_proved": cap["delta_AHSS_d3_d4_candidate_audit"]["chain_level_identification_of_delta_with_candidate_proved"],
            "delta_post_Einfinity_extension_resolved": cap["delta_AHSS_d3_d4_candidate_audit"]["post_Einfinity_hidden_extension_resolved"],
            "delta_exact_order": current["delta_exact_order"],
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
            "unchanged_parent_no_go_does_not_reject_action_changes": True,
            "C4F_algebra_is_not_full_stratified_parent": True,
            "F4_topological_spectrum_match_is_not_explicit_compact_UV_model": True,
            "smooth_cycle_phase_is_not_full_HGamma_source_completed_phase": True,
            "algebraic_coefficient_scan_is_not_physical_refinement_classification": True,
            "ordinary_cap_is_not_WCS_or_Dai_Freed_glue": True,
            "G1_requires_one_full_action_regulator_and_global_parent": True,
            "G6_requires_junction_and_entangled_source_glue": True,
            "G8_requires_selected_physical_total_anomaly_character_one": True,
            "accept_if_scaffolds_only": False,
        },
        "next_required_action": copy.deepcopy(v84["next_required_action"]),
        "primary_sources": copy.deepcopy(v84["primary_sources"]),
        "source_manifest": copy.deepcopy(v84["source_manifest"]),
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
    return f"""# V84 multipath G1 frontier master audit

Status: {report['status']}

Core SHA-256: {report['core_sha256']}

## Master decision

V84 appends unaccepted route B84.  The unchanged five-factor ordinary parent
is now exactly rejected: all {decision['unchanged_Gammahat_assignments_enumerated']}
translation-deck assignments force pure z11, which is incompatible with both
localized 16s and the frozen Green--Schwarz vector.

The selected C4F redesign keeps Spin(11) faithful and repairs the central
translation algebra and displayed interaction scaffold.  It is not a full
parent because localized isotropy, discrete anomalies and the common
BV/regulator/WCS complex remain absent.

On the candidate smooth Q4 bundle the bare phase is one of
{tuple(decision['smooth_Q4_bare_phase_values'])}, necessarily a primitive
fourth root.  The reference WCS branch and the new sixteen-row algebraic r2
coefficient screen do not cancel it.  That screen is not a classification of
physical refinements, and the full-HGamma result remains open.

F4 realizes (S,F,K)={tuple(tuple(x) for x in decision['F4_section_fiber_canonical'])},
reproduces (three vector hypers, 266 neutral hypers), and supplies the critical
heterotic fiber string.  The minimal residue lifts are
{tuple(tuple(x) for x in decision['minimal_effective_residue_lifts'])}; both
are reducible charge/curve configurations and only candidate junctions.  An
explicit compact Weierstrass/global-form model and junction worldsheet are not
constructed.

The ordinary product cap is exact, but the restricted direct product is not
half-BPS and its double is not Q4.  The associated-graded delta candidate
has potential incoming d3 and q2-controlled d4 maps; their source-page
survival, both values, its chain-level identification and the hidden extension
remain open.  Delta remains {decision['delta_exact_order']}.

The current action remains {decision['current_action_status']}.  The redesign
program remains viable, but no route is accepted, G1--G8 remain OPEN, and the
theory is not complete.

## Exact V84 gains

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
        raise RuntimeError("V84 master core is not canonical")
    if report["input_core_hashes"] != {"V83_master": EXPECTED_CORES["v83_master"], "V84_route": EXPECTED_CORES["v84_route"]}:
        raise RuntimeError("V84 master lineage mismatch")
    parent = load_bound(V83_MASTER_PATH, EXPECTED_CORES["v83_master"])
    routes = report["route_matrix"]
    if routes[:-1] != parent["route_matrix"]:
        raise RuntimeError("inherited V83 route matrix was mutated")
    if report["lineage"]["parent_route_matrix_sha256"] != canonical_sha(parent["route_matrix"]):
        raise RuntimeError("inherited V83 route-matrix hash changed")
    if len(routes) != report["lineage"]["parent_route_count"] + 1:
        raise RuntimeError("route matrix length changed")
    if routes[-1]["route_id"] != "B84" or routes[-1]["accepted"]:
        raise RuntimeError("B84 route acceptance changed")
    if [row["ordinal"] for row in routes] != list(range(1, len(routes) + 1)):
        raise RuntimeError("route ordinals are not consecutive")
    decision = report["strict_master_decision"]
    if decision["unchanged_Gammahat_assignments_enumerated"] != 1024 or not decision["pure_Spin11_center_forced"]:
        raise RuntimeError("unchanged Gammahat no-go changed")
    if not decision["unchanged_five_factor_parent_rejected_exactly"]:
        raise RuntimeError("unchanged-parent rejection was lost")
    if decision["C4F_kernel_contains_pure_z11"] or not decision["C4F_Spin11_faithful"]:
        raise RuntimeError("C4F faithful-kernel result changed")
    if (
        not decision["C4F_direct_matched_representative_rows_pass"]
        or decision["C4F_independent_sign_rows_passing"] != 8
        or not decision["C4F_localized_pure_center_repaired"]
    ):
        raise RuntimeError("C4F exact scaffold gain was lost")
    if decision["C4F_fatal_spinor_adjoint_target_vacuum_admissible"]:
        raise RuntimeError("V65-fatal spinor-adjoint trilinear was promoted")
    if decision["C4F_full_localized_isotropy_constructed"] or decision["C4F_full_quantum_parent_constructed"]:
        raise RuntimeError("C4F scaffold was promoted")
    if decision["smooth_Q4_bare_phase_values"] != ["i", "-i"] or not decision["smooth_Q4_bare_phase_primitive_fourth_root"]:
        raise RuntimeError("smooth Q4 bare phase changed")
    if decision["bare_phase_fully_BV_orientation_pinned"]:
        raise RuntimeError("bare phase conjugation was falsely selected")
    if decision["algebraic_r2_shift_WCS_counts"] != {"0": 4, "2": 12}:
        raise RuntimeError("algebraic r2 screen changed")
    if decision["algebraic_r2_screen_classifies_physical_refinements"] or decision["all_full_HGamma_WCS_refinements_fail"]:
        raise RuntimeError("algebraic WCS screen was promoted")
    if decision["F4_section_fiber_canonical"] != [[2, -1], [-1, 0], [2, 2]]:
        raise RuntimeError("F4 charge-lattice map changed")
    if decision["F4_so11_Lie_algebra_vector_and_neutral_hypers"] != [3, 266]:
        raise RuntimeError("F4 spectrum match changed")
    if decision["F4_global_gauge_group_matched"]:
        raise RuntimeError("F4 Lie-algebra match was promoted to a global group")
    if decision["critical_heterotic_full_central_charges"] != [24, 12]:
        raise RuntimeError("critical heterotic string changed")
    if decision["minimal_effective_residue_lifts"] != [[1, -1], [5, -3]] or decision["residue_lifts_irreducible"]:
        raise RuntimeError("F4 residue-junction classification changed")
    if decision["explicit_compact_F4_Weierstrass_parent_constructed"]:
        raise RuntimeError("F4 scaffold was promoted to explicit UV parent")
    if decision["restricted_T2xS4_half_BPS_solution_exists"]:
        raise RuntimeError("restricted product was promoted to BPS")
    if not decision["ordinary_relative_product_cap_constructed"] or decision["product_cap_double_represents_Q4"]:
        raise RuntimeError("product cap result changed")
    delta_maps = decision["delta_potential_associated_graded_candidate_differentials"]
    if (
        decision["delta_exact_order"] != "OPEN_ZERO_OR_ORDER2"
        or len(delta_maps) != 2
        or "potential incoming d3:" not in delta_maps[0]
        or "potential incoming d4:" not in delta_maps[1]
    ):
        raise RuntimeError("delta d3/d4 frontier changed")
    if (
        decision["delta_d3_source_page_survival_computed"]
        or decision["delta_d4_source_page_survival_computed"]
        or decision["delta_d3_value_computed"]
        or decision["delta_d4_value_computed"]
        or decision["delta_chain_level_candidate_identification_proved"]
        or decision["delta_post_Einfinity_extension_resolved"]
    ):
        raise RuntimeError("delta associated-graded candidate was promoted")
    accepted = [row["route_id"] for row in routes if row["accepted"]]
    if accepted or decision["accepted_extension_count"] != 0:
        raise RuntimeError("route acceptance ledger is nonempty")
    if decision["same_action_microscopic_completion_found"] or decision["accepted_full_parent_action_exists"]:
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
