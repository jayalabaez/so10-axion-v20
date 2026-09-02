#!/usr/bin/env python3
"""V92 master: append scoped F92 results without accepting a quantum parent."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import susy_v91_multipath_g1_frontier_master_audit as common

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT/"SUSY_V92_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT/"SUSY_V92_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT/"test_susy_v92_multipath_g1_frontier_master_audit.py"
V91_PATH = ROOT/"SUSY_V91_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V92_PATH = ROOT/"SUSY_V92_PROJECTORS_LENS_WCS_COMPACT_DECK_ROOT_AUDIT.json"
EXPECTED_CORES = {
    "v91_master":"f21fb9db8839a6cd3ceb3372abb1b4fb8ecf600ebe500aa33b31f45e890d07ae",
    "v92_route":"3d4365681c9ebdbcbda6d9d57377a1046a6ab00b3a8b1b2290f2858a7ee4f4fb",
}
STATUS = "V92_MASTER__PROJECTORS_LENS_WCS_AND_SMOOTH_DECK_ROOT__GLOBAL_ACTION_AND_SPECTRUM_GLUE_OPEN"
canonical_sha, file_sha, load_bound = common.canonical_sha, common.file_sha, common.load_bound


def content():
    previous = load_bound(V91_PATH,EXPECTED_CORES["v91_master"])
    route = load_bound(V92_PATH,EXPECTED_CORES["v92_route"])
    routes = copy.deepcopy(previous["route_matrix"])
    routes.append({
        "ordinal":len(routes)+1,"route_id":"B92",
        "name":"explicit 267 singlet projectors, ordinary lens WCS screen and compact smooth deck-root member",
        "accepted":False,"same_action_microscopic_completion":False,
        "selected_exact_scaffolds":[
            "two full smooth-sector projector witnesses with different constant-mode spectra",
            "conditional normal-aligned witness has eleven chiral modes; local mass ansatz lifts nine under new R assumptions",
            "selected source passes four ordinary C4/C8 lens tests including the even-U WCS counterterm",
            "eight of sixteen torsion labels pass this lens screen, not a full bordism character",
            "compact crepant member is geometrically smooth; regular order-four lift squares to deck",
            "holomorphic form character is i; diagonal bundle and actual spectrum remain open",
        ],
    })
    criteria = [
        ("A1","V91/V92 canonical lineage","PASS_EXACT"),
        ("A2","267 smooth-sector SMW and central-kernel projectors","PASS_EXACT_AT_SYMMETRIC_ORIGIN"),
        ("A3","selected eleven-mode normal-channel alignment","PASS_CONDITIONAL_NOT_ANOMALY_CANCELLATION"),
        ("A4","nine additional singlet masses","PASS_LOCAL_ANSATZ_WITH_NEW_R_ASSIGNMENT"),
        ("A5","full R action and fixed-wall mass interaction","OPEN_UNCONSTRUCTED"),
        ("A6","four ordinary closed-lens fermion/WCS ratios","PASS_EXACT_SELECTED_SOURCE"),
        ("A7","ordinary source torsion labels surviving lens screen","PASS_EXACT_8_OF_16"),
        ("A8","full Gammahat relative Dai-Freed/WCS anomaly","OPEN_UNCOMPUTED"),
        ("A9","new member compact crepant smooth resolution","PASS_EXACT_GOOD_REDUCTION_AND_PROPER_MODEL"),
        ("A10","global order-four automorphism squaring to deck","PASS_EXACT_OVER_Q_I"),
        ("A11","standalone volume-preserving quotient","REJECTED_OMEGA_CHARACTER_I"),
        ("A12","compatible diagonal geometric and field bundle","OPEN_UNCONSTRUCTED"),
        ("A13","necessary Hodge target (9,143,-268)","PASS_CONDITIONAL_DICTIONARY_NOT_ACTUAL_SPECTRUM"),
        ("A14","Mordell-Weil rank, height and actual matter spectrum","OPEN_UNCOMPUTED"),
        ("A15","accepted same-action microscopic quantum completion","OPEN_NOT_FOUND"),
    ]
    decision = route["terminal_decision"]
    return {
        "schema":"susy_v92_multipath_g1_frontier_master_audit_v1",
        "version":"V92","status":STATUS,
        "input_core_hashes":dict(EXPECTED_CORES),
        "lineage":{
            "parent_master":"V91","new_route":"B92",
            "parent_route_count":len(previous["route_matrix"]),
            "parent_route_matrix_sha256":canonical_sha(previous["route_matrix"]),
            "canonical_V21_gate_scope_unchanged":True,
            "this_master_gate_scope":"separate SUSY/C8 completion branch",
        },
        "route_matrix":routes,
        "acceptance_criteria":[{"id":i,"requirement":name,"status":status} for i,name,status in criteria],
        "consolidated_theory_card":{
            "selected_branch_status":"CONSTRUCTIVE_SCOPED_CERTIFICATES_NOT_YET_ONE_QUANTUM_ACTION",
            "accepted_extension_count":sum(bool(r["accepted"]) for r in routes),
            "bulk_singlet_counts_q0_q2_q4_q6_q8":[144,3,19,11,90],
            "smooth_sector_projectors_constructed":decision["explicit_267_singlet_smooth_sector_projectors_constructed"],
            "selected_constant_chiral_modes":decision["conditional_normal_aligned_witness_zero_modes"],
            "conditionally_massive_extra_modes":route["conditional_extra_singlet_mass_module"]["calculation"]["rank_for_v_nonzero"],
            "ordinary_closed_lens_tests_passed":4,
            "torsion_labels_passing_this_screen":decision["torsion_labels_passing_this_screen"],
            "compact_geometric_smoothness_certified":decision["compact_geometrically_smooth_member_certified"],
            "global_order_four_deck_root_certified":decision["global_regular_order_four_deck_root_certified"],
            "holomorphic_volume_form_character":"I",
            "necessary_hodge_target":copy.deepcopy(route["conditional_spectrum_geometry_target"]["necessary_hodge_tuple"]),
            "actual_geometric_hodge_numbers_computed":False,
            "full_R_mass_module_embedding_certified":False,
            "quantum_anomaly_cancelled":False,
            "primitive_C8_preserved_by_retained_vacuum":False,
            "same_action_spectrum_and_geometry_realized":False,
            "soft_spectrum_unification_cosmology_complete":False,
        },
        "supersession_ledger":{
            "V91_bulk_charge_and_source_quantization_data_retained":True,
            "V91_unconstructed_smooth_singlet_projectors_now_explicit":True,
            "bulk_counts_uniquely_determine_equivariant_spectrum":False,
            "bare_central_lens_sign_is_complete_anomaly_veto":False,
            "ordinary_closed_lens_screen_replaces_relative_anomaly":False,
            "V91_geometric_scout_smoothness_now_proved_for_its_own_coefficients":True,
            "old_V90_geometry_certificate_retracted":False,
            "old_Spin11_only_Hodge_tuple_reusable_for_continuous_U1_scout":False,
            "conditional_mass_terms_erase_anomaly_matching":False,
            "all_F92_obligations_fully_completed":False,
        },
        "strict_master_decision":copy.deepcopy(decision),
        "gate_ledger":copy.deepcopy(route["gate_ledger"]),
        "next_required_action":copy.deepcopy(route["next_required_action"]),
        "primary_sources":copy.deepcopy(route["primary_sources"]),
        "artifact_hashes":{"generator_sha256":file_sha(Path(__file__)),"test_sha256":file_sha(TEST_PATH)},
    }


def build_report():
    result = content()
    result["core_sha256"] = canonical_sha(result)
    validate_report(result)
    return result


def validate_report(result):
    if result.get("core_sha256") != canonical_sha(result):
        raise RuntimeError("master core not canonical")
    body = copy.deepcopy(result)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("master lineage, arithmetic or acceptance boundary changed")


def render_markdown(r):
    card = r["consolidated_theory_card"]
    lines = [
        "# SUSY V92 multipath frontier master","",
        "Status: "+r["status"],"","Core SHA256: "+r["core_sha256"],"",
        "V92 supplies explicit singlet projectors, a conditional local singlet-mass module, an ordinary four-lens anomaly screen including WCS, and a compact smooth member with a global order-four deck root. The constructions are not yet glued into one microscopic quantum action. No gate is closed.","",
        "Accepted extensions: "+str(card["accepted_extension_count"]),"",
        "## Results and limits","",
        "All 267 smooth-sector singlet projectors are explicit. The selected normal-aligned witness has eleven constant chiral modes; nine have a full-rank mass matrix in a new conditional local ansatz. Its independent R assignment and global wall interaction are unconstructed, and normal-channel alignment is not total anomaly cancellation.","",
        "The selected V91 source passes both spin lifts of ordinary C4 and C8 lens spaces after including the even-U WCS counterterm. Eight of sixteen torsion labels pass this screen. Full Gammahat bordism, localized gauge-normal anomalies and relative wall trivializations remain open.","",
        "The compact coefficient member has a smooth crepant resolution, with a global regular order-four automorphism over Q(i) whose square is deck. But tau*Omega=i*Omega: a standalone volume-preserving quotient is excluded, and a compatible diagonal bundle is still needed.","",
        "If the V91 continuous scout has the stipulated flat elliptic realization with exactly Spin11 and one U1, its necessary Hodge tuple is (9,143,-268). This is a spectrum-derived target, not a computation of the new member's Hodge numbers, Mordell-Weil rank, height or matter spectrum.","",
        "## Acceptance ledger","",
    ]
    lines.extend("- "+x["id"]+": "+x["status"]+" — "+x["requirement"] for x in r["acceptance_criteria"])
    lines.extend(["","## Gate scope","",
        "All eight SUSY/C8 gates remain OPEN. Canonical V21 gate evidence is unchanged. No complete soft spectrum, unification, cosmology or experimental confirmation is claimed.","",
        "## Next required action","",r["next_required_action"]["id"],"",
        r["next_required_action"]["primary"],"",r["next_required_action"]["parallel"],"",
        "## Primary sources",""])
    lines.extend("- ["+x["use"]+"]("+x["url"]+")" for x in r["primary_sources"])
    return "\n".join(lines)+"\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write",action="store_true")
    args = parser.parse_args()
    r = build_report()
    if args.write:
        OUT_JSON.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n",encoding="utf-8",newline="\n")
        OUT_MD.write_text(render_markdown(r),encoding="utf-8",newline="\n")
    print(json.dumps({"version":"V92","core_sha256":r["core_sha256"],"route_count":len(r["route_matrix"]),
                     "accepted_extensions":r["consolidated_theory_card"]["accepted_extension_count"],
                     "closed_gates":[],"next":r["next_required_action"]["id"]},indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
