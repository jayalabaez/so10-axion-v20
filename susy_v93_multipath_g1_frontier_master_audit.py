#!/usr/bin/env python3
"""V93 master: preserve all earlier route decisions and append scoped F93."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import susy_v91_multipath_g1_frontier_master_audit as common

ROOT=Path(__file__).resolve().parent
OUT_JSON=ROOT/"SUSY_V93_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD=ROOT/"SUSY_V93_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH=ROOT/"test_susy_v93_multipath_g1_frontier_master_audit.py"
V92_PATH=ROOT/"SUSY_V92_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V93_PATH=ROOT/"SUSY_V93_LOCALIZED_ANOMALY_R_LIFT_JACOBIAN_AUDIT.json"
EXPECTED_CORES={
    "v92_master":"e38e8b58d4f86e00271402c9580919a092e024b737a4fc5290e4d20709b5aae8",
    "v93_route":"4f81852d9e272d3fb12946ad41cb01d9f93462f75cef69123106a80b03f092f2",
}
STATUS="V93_MASTER__EXPLICIT_LOCAL_ANOMALY_OBLIGATION_AND_SMOOTH_R_MASS_REPAIR__CONDITIONAL_JACOBIAN_MATTER_MATCH__NO_ACCEPTED_PARENT"
canonical_sha,file_sha,load_bound=common.canonical_sha,common.file_sha,common.load_bound


def content():
    previous=load_bound(V92_PATH,EXPECTED_CORES["v92_master"])
    route=load_bound(V93_PATH,EXPECTED_CORES["v93_route"])
    routes=copy.deepcopy(previous["route_matrix"])
    routes.append({"ordinal":len(routes)+1,"route_id":"B93",
        "name":"localized anomaly polynomial, smooth R-equivariant mass extension and actual Jacobian compatibility",
        "accepted":False,"same_action_microscopic_completion":False,
        "selected_exact_scaffolds":[
            "full shifted-character singlet polynomial and independent charged Cartan/zero-mode crosschecks",
            "bare bulk ordinary GS span obstruction and independently periodic normal-axion half-period failure",
            "explicit smooth-sector R action and all four fixed-wall mass characters; heavy anomaly matching retained",
            "actual Jacobian nonsplit I2* and period-two torsor; conditional nonlocal matter count three matches vector11 census",
        ]})
    criteria=[
        ("A1","canonical V92/V93 lineage","PASS_EXACT"),
        ("A2","all six singlet local gauge-normal-gravity channels","PASS_EXACT_SMW_SHIFTED_CHARACTER"),
        ("A3","bare bulk Cartan polynomial and ordinary zero-mode index","PASS_EXACT_STATED_NORMAL_TENSOR_LIFT"),
        ("A4","ordinary bulk GS alone cancels bare local polynomial","REJECTED_NONBULK_INVARIANT_COMPONENT"),
        ("A5","isolated period-one normal axion with integer levels","REJECTED_HALF_INTEGRAL_SU5_INSTANTON_PERIOD"),
        ("A6","independent smooth-sector R action","PASS_EXACT_NEW_CLASSICAL_CHOICE"),
        ("A7","nine-singlet mass fixed-wall characters","PASS_EXACT_NOT_FULL_FRAME_ACTION"),
        ("A8","heavy anomaly matching and ordinary spin4 curvature periods","PASS_LOCAL_PATCH_AND_PERIOD_SCREEN_ONLY"),
        ("A9","full wall tangential representations and quantized relative anomaly","OPEN_UNCONSTRUCTED"),
        ("A10","actual Jacobian generic codimension-one fibers","PASS_EXACT_NONSPLIT_I2STAR_AND_I1"),
        ("A11","actual torsor section, period and index","NO_SECTION_PERIOD2_INDEX2"),
        ("A12","three vector11 hypers from Jacobian monodromy","PASS_CONDITIONAL_NONLOCAL_MATTER_CONTRIBUTION"),
        ("A13","Jacobian MW rank, height and full U1-charged spectrum","OPEN_UNCOMPUTED"),
        ("A14","common diagonal geometric and physical quantum action","OPEN_NOT_FOUND"),
    ]
    bulk=route["bare_bulk_local_anomaly"]["calculation"]
    mass=route["smooth_R_and_wall_mass_extension"]
    geom=route["actual_member_Jacobian_and_torsor"]
    return {
        "schema":"susy_v93_multipath_g1_frontier_master_audit_v1",
        "version":"V93","status":STATUS,"input_core_hashes":dict(EXPECTED_CORES),
        "lineage":{"parent_master":"V92","new_route":"B93",
                   "parent_route_count":len(previous["route_matrix"]),
                   "parent_route_matrix_sha256":canonical_sha(previous["route_matrix"]),
                   "canonical_V21_gate_scope_unchanged":True,
                   "this_master_gate_scope":"separate SUSY/C8 completion branch"},
        "route_matrix":routes,
        "acceptance_criteria":[{"id":i,"requirement":name,"status":status} for i,name,status in criteria],
        "consolidated_theory_card":{
            "selected_branch_status":"LOCAL_ANOMALY_TARGET_EXPLICIT__QUANTIZED_BOUNDARY_AND_GEOMETRY_GLUE_OPEN",
            "accepted_extension_count":sum(bool(r["accepted"]) for r in routes),
            "bulk_singlet_count":267,"selected_constant_singlet_modes":11,
            "nine_mass_terms_R_and_wall_character_tests_pass":True,
            "R_action_scope":"smooth bulk centralizer and existing kernel, not all localized representations or quantum R anomalies",
            "ordinary_GS_span_rank":bulk["ordinary_bulk_GS_obstruction"]["at_z00"]["basis_rank"],
            "rank_with_bare_local_polynomial":bulk["ordinary_bulk_GS_obstruction"]["at_z00"]["augmented_rank"],
            "independent_normal_axion_half_period_failure":True,
            "full_conditional_visible_continuous_anomaly_tensor":bulk["conditional_visible_gauge_slice"]["visible_tensor"],
            "heavy_singlet_TrQ_TrQ3":[mass["mass_anomaly_matching"]["TrQ"],mass["mass_anomaly_matching"]["TrQ3"]],
            "Jacobian_generic_nonabelian_algebra":geom["S_Jacobian_fiber"]["Tate_gauge_algebra"],
            "torsor_period_and_index":[geom["torsor_section_obstruction"][k] for k in ("period","index")],
            "conditional_Jacobian_nonlocal_vector11_hypers":geom["conditional_Jacobian_nonlocal_matter"]["conditional_nonlocal_vector11_full_hypermultiplets"],
            "Jacobian_MW_rank":None,
            "full_quantum_anomaly_cancelled":False,
            "primitive_C8_restored":False,
            "same_action_spectrum_and_geometry_realized":False,
            "soft_spectrum_unification_cosmology_complete":False,
        },
        "supersession_ledger":copy.deepcopy(route["supersession_boundary"]),
        "strict_master_decision":copy.deepcopy(route["terminal_decision"]),
        "gate_ledger":copy.deepcopy(route["gate_ledger"]),
        "next_required_action":copy.deepcopy(route["next_required_action"]),
        "primary_sources":copy.deepcopy(route["primary_sources"]),
        "artifact_hashes":{"generator_sha256":file_sha(Path(__file__)),"test_sha256":file_sha(TEST_PATH)},
    }


def build_report():
    r=content()
    r["core_sha256"]=canonical_sha(r)
    validate_report(r)
    return r


def validate_report(r):
    if r.get("core_sha256")!=canonical_sha(r):
        raise RuntimeError("V93 master core noncanonical")
    body=copy.deepcopy(r)
    body.pop("core_sha256")
    if body!=content():
        raise RuntimeError("V93 master lineage, arithmetic or scope changed")


def render_markdown(r):
    lines=["# SUSY V93 multipath frontier master","",
        "Status: "+r["status"],"","Core SHA256: "+r["core_sha256"],"",
        "V93 makes the local anomaly obligation explicit and improves two constructive candidates: the nine-singlet mass sector now has a smooth R lift and valid fixed-wall characters, and the actual Jacobian conditionally reproduces the three vector-11 nonlocal hypermultiplets. These are not yet a complete quantum action. Accepted extensions: 0. All eight SUSY/C8 gates remain OPEN.","",
        "## What changed","",
        "The complete six-channel singlet shifted-character polynomial and the bare charged/gravity/tensor Cartan polynomial are exact under the stated lift. Independent trace, constant-mode and visible-component calculations agree. Ordinary bulk GS products do not span the result: rank 9 becomes 10. A naive independent period-one normal axion also fails a unit-instanton half-period test. More general boundary/tangential completions are not excluded.","",
        "An explicit new smooth-sector R action gives the nine extra scalars R=1 and both Phi constants R=0 while preserving the existing orbifold matrices and central-kernel descent. Both cubic mass channels are invariant at all four cover strata. The removed heavy sector's anomaly, TrQ=36 and TrQ^3=864, survives through a local Phi-phase matching term. Full wall/frame coupling, quantum R anomaly and relative global completion remain open.","",
        "The actual Jacobian has nonsplit I2* along S and reduced I1 elsewhere generically. Its eight-point monodromy double cover has genus three; the standard conditional rule and an independent intersection formula yield three vector11 hypers. The torsor has no rational section and period=index=2, but this does not determine Jacobian MW rank. U1 charges, height, extra matter and the torsor's physical contraction remain unknown.","",
        "## Acceptance ledger","",]
    lines.extend("- "+row["id"]+": "+row["status"]+" — "+row["requirement"] for row in r["acceptance_criteria"])
    lines.extend(["","## Scope and next step","",
        "No same-action parent, full anomaly cancellation, experimental confirmation, complete spectrum, unification or cosmology is claimed. Canonical V21 physical gate evidence is unchanged.","",
        r["next_required_action"]["id"],"",r["next_required_action"]["primary"],"",r["next_required_action"]["parallel"],"",
        "The mathematical targets are now specific enough to test proposed repairs; declaring G1 closed would still be unsupported.","",
        "## Primary sources",""])
    lines.extend("- ["+row["use"]+"]("+row["url"]+")" for row in r["primary_sources"])
    return "\n".join(lines)+"\n"


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--write",action="store_true")
    args=parser.parse_args()
    r=build_report()
    if args.write:
        OUT_JSON.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n",encoding="utf-8",newline="\n")
        OUT_MD.write_text(render_markdown(r),encoding="utf-8",newline="\n")
    print(json.dumps({"version":"V93","core_sha256":r["core_sha256"],"route_count":len(r["route_matrix"]),
                     "accepted_extensions":r["consolidated_theory_card"]["accepted_extension_count"],
                     "closed_gates":[],"next":r["next_required_action"]["id"]},indent=2))


if __name__=="__main__":
    main()
