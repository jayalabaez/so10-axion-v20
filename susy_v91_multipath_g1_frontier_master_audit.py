#!/usr/bin/env python3
"""V91 master: preserve V90 history and append only scoped F91 conclusions."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V91_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT / "SUSY_V91_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v91_multipath_g1_frontier_master_audit.py"
V90_PATH = ROOT / "SUSY_V90_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V91_PATH = ROOT / "SUSY_V91_SPINC_QUANTIZATION_TENSOR_CONE_FINITE_TORSION_AUDIT.json"
EXPECTED_CORES = {
    "v90_master":"a79ce1980e99f356901cb6b26e7b63927184656a9eecce075a29d416922db276",
    "v91_route":"4a581af0dd4cfc6fd3f66ef1e3ea2801b9770c67822d984a02deb602865c0322",
}
STATUS = "V91_MASTER__QUOTIENT_OBSTRUCTION_REPAIRED_AT_ORDINARY_SOURCE_LEVEL__NEW_SYMMETRY_SCOUT__NO_ACCEPTED_QUANTUM_PARENT"


def canonical_sha(value):
    body = copy.deepcopy(value)
    if isinstance(body,dict):
        body.pop("core_sha256",None)
    return hashlib.sha256(json.dumps(body,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def file_sha(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n",b"\n")).hexdigest()


def load_bound(path, expected):
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("core_sha256") != expected or canonical_sha(value) != expected:
        raise RuntimeError("master parent core changed: "+path.name)
    return value


def content():
    previous = load_bound(V90_PATH,EXPECTED_CORES["v90_master"])
    route = load_bound(V91_PATH,EXPECTED_CORES["v91_route"])
    routes = copy.deepcopy(previous["route_matrix"])
    routes.append({
        "ordinal":len(routes)+1,"route_id":"B91",
        "name":"ordinary Spin^c source quantization, conditional F4 cone, finite torsion and anti-equivariant geometry scout",
        "accepted":False,"same_action_microscopic_completion":False,
        "selected_exact_scaffolds":[
            "V90 ordinary continuous quotient has order-two source-quantization obstruction",
            "opposite-sheet F4 Mori cone and all its nonzero effective curve volumes are positive",
            "new 267-hyper charge distribution solves smooth-bulk equations and complete cocharacter integrality",
            "ordinary H4(BG8;Z) and 16 source torsion refinements are explicit",
            "old identity-base deck roots excluded; new member has exact deck-root symmetry and simple boundary roots",
        ],
    })
    criteria = [
        ("A1","V90/V91 canonical lineage","PASS_EXACT"),
        ("A2","positive frozen tensor sheet","REJECTED_UNIVERSAL_ORDINARY_U1_SIGN"),
        ("A3","opposite-sheet conditional F4 effective cone","PASS_EXACT_CONDITIONAL_GEOMETRIC_IDENTIFICATION"),
        ("A4","V90 fixed ordinary continuous quotient","REJECTED_ORDER_TWO_SOURCE_QUANTIZATION"),
        ("A5","new scout smooth-bulk polynomial","PASS_EXACT"),
        ("A6","new scout complete ordinary cocharacter integrality","PASS_EXACT"),
        ("A7","new scout 267 SMW/Gammahat projectors and local inflow","OPEN_UNCONSTRUCTED"),
        ("A8","ordinary finite degree-four integral source choices","PASS_EXACT_16_TOPOLOGICAL_CHOICES"),
        ("A9","full tangential relative Dai-Freed/WCS anomaly","OPEN_UNCOMPUTED"),
        ("A10","primitive C8 after retained visible vacuum","REJECTED_BREAKS_TO_C2"),
        ("A11","V90 deck root over identity F4 base","REJECTED_GENERIC_JACOBIAN_ARGUMENT"),
        ("A12","new anti-equivariant member symmetry and boundary","PASS_EXACT_SCOUT"),
        ("A13","new member compact smoothness/resolution/orbibundle","OPEN_UNCOMPUTED"),
        ("A14","accepted same-action microscopic quantum completion","OPEN_NOT_FOUND"),
    ]
    return {
        "schema":"susy_v91_multipath_g1_frontier_master_audit_v1",
        "version":"V91","status":STATUS,
        "input_core_hashes":dict(EXPECTED_CORES),
        "lineage":{
            "parent_master":"V90","new_route":"B91",
            "parent_route_count":len(previous["route_matrix"]),
            "parent_route_matrix_sha256":canonical_sha(previous["route_matrix"]),
            "canonical_V21_gate_scope_unchanged":True,
            "this_master_gate_scope":"separate SUSY/C8 completion branch",
        },
        "route_matrix":routes,
        "acceptance_criteria":[{"id":i,"requirement":name,"status":status} for i,name,status in criteria],
        "consolidated_theory_card":{
            "selected_branch_status":"QUANTIZED_ORDINARY_SOURCE_SCOUT_PLUS_UNVERIFIED_DECK_ROOT_GEOMETRY",
            "accepted_extension_count":sum(bool(r["accepted"]) for r in routes),
            "new_singlet_counts_q0_q2_q4_q6_q8":route["quantized_scout"]["singlet_counts_by_q0_q2_q4_q6_q8"],
            "new_abelian_coefficient":route["quantized_scout"]["c"],
            "smooth_bulk_D2_D4":[route["quantized_scout"]["moments"][k] for k in ("D2","D4")],
            "full_cocharacter_integrality":route["quantized_scout"]["complete_cocharacter_certificate"]["all_cocharacters_quantized"],
            "quantum_anomaly_cancelled":False,
            "primitive_C8_preserved":False,
            "geometric_scout_smoothness_certified":False,
            "soft_spectrum_unification_cosmology_complete":False,
        },
        "supersession_ledger":{
            "V90_wrong_frozen_sheet_strengthened_to_universal_sheet_no_go":True,
            "V90_opposite_sheet_unknown_refined_to_conditional_F4_cone_witness":True,
            "V90_fixed_continuous_quotient_rejected_by_global_source_quantization":True,
            "nearby_quantized_scout_is_new_bulk_charge_data":True,
            "new_bulk_counts_determine_equivariant_zero_modes":False,
            "ordinary_bordism_target_is_full_Gammahat_target":False,
            "new_coefficients_inherit_V90_compact_smoothness":False,
            "old_V90_geometry_certificate_retracted":False,
            "full_complex_no_deck_root_theorem_claimed":False,
        },
        "strict_master_decision":copy.deepcopy(route["terminal_decision"]),
        "gate_ledger":copy.deepcopy(route["gate_ledger"]),
        "next_required_action":copy.deepcopy(route["next_required_action"]),
        "primary_sources":copy.deepcopy(route["primary_sources"]),
        "artifact_hashes":{"generator_sha256":file_sha(Path(__file__)),
                           "test_sha256":file_sha(TEST_PATH)},
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
        "# SUSY V91 multipath frontier master","",
        "Status: "+r["status"],"","Core SHA256: "+r["core_sha256"],"",
        "V91 rejects the old ordinary continuous quotient by exact global source quantization, then supplies a nearby scout that clears that necessary test and the smooth-bulk equations. It also constructs a new geometric symmetry/boundary scout. Neither is an accepted same-action quantum completion.","",
        "Accepted extensions: "+str(card["accepted_extension_count"]),"",
        "## Selected candidate","",
        "Singlet counts at q=(0,2,4,6,8): "+str(card["new_singlet_counts_q0_q2_q4_q6_q8"])+".",
        "Abelian coefficient c="+str(card["new_abelian_coefficient"])+". D2,D4="+str(card["smooth_bulk_D2_D4"])+".",
        "The full ordinary cocharacter lattice is quantized. The conditional F4 cone has positive effective-curve volumes for t>1. The 267 projectors, relative anomaly trivialization, height/spectrum realization and complete visible selector remain unresolved.","",
        "## Acceptance ledger","",
    ]
    lines.extend("- "+x["id"]+": "+x["status"]+" — "+x["requirement"] for x in r["acceptance_criteria"])
    lines.extend(["","## Gate scope","",
                  "All eight SUSY/C8 gates remain OPEN. Canonical V21 gate evidence is unchanged. No soft-spectrum, unification, cosmology or empirical completion is claimed.","",
                  "## Next required action","",r["next_required_action"]["id"],"",
                  r["next_required_action"]["primary"],"",r["next_required_action"]["parallel"],"",
                  "## Primary sources",""])
    lines.extend("- ["+x["id"]+"]("+x["url"]+"): "+x["use"] for x in r["primary_sources"])
    return "\n".join(lines)+"\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write",action="store_true")
    args = parser.parse_args()
    r = build_report()
    if args.write:
        OUT_JSON.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n",encoding="utf-8",newline="\n")
        OUT_MD.write_text(render_markdown(r),encoding="utf-8",newline="\n")
    print(json.dumps({"version":"V91","core_sha256":r["core_sha256"],"route_count":len(r["route_matrix"]),
        "accepted_extensions":r["consolidated_theory_card"]["accepted_extension_count"],
        "closed_gates":[],"next":r["next_required_action"]["id"]},indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
