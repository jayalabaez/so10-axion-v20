"""Append F100 while preserving all 27 old routes and canonical V21 scope."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import susy_v91_multipath_g1_frontier_master_audit as common

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT/"SUSY_V100_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT/"SUSY_V100_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT/"test_susy_v100_multipath_g1_frontier_master_audit.py"
V99_PATH = ROOT/"SUSY_V99_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V100_PATH = ROOT/"SUSY_V100_CORRELATED_QUANTIZATION_MODIFIED_ACTION_SECTION_AUDIT.json"
EXPECTED_CORES = {
    "v99_master": "72c499490e86c3b9da3e436d95bc6d7b9907806f214ac491be1336b310e2fd39",
    "v100_route": "804242337e0681fe39a84891badd9545447b7f980794366da6a45d4f3277018a",
}
HELPER_KEYS = ("modified_equivariant_cover", "spectator_GS_obstruction", "correlated_quotient_period", "original_section_existence")
NEXT_ID = "F101_PHYSICAL_BACKGROUND_RESTRICTION_RELATIVE_ACTION_AND_SECTION_SOLVABILITY"
STATUS = "V100_MASTER__EXACT_RESPONSE_LEVELS__REGULAR_SPECTATOR_OBSTRUCTION__CONDITIONAL_SECTION_LATTICE__ALL_BRANCH_GATES_OPEN"
canonical_sha, file_sha, load_bound = common.canonical_sha, common.file_sha, common.load_bound


def theory_card(route, rows, previous):
    old = previous["consolidated_theory_card"]
    retained = ("actual_original_MW_torsion_order", "actual_original_MW_free_rank_bounds",
                "conditional_unit_charge_section_height_S_F", "conditional_doubled_charge_section_height_S_F")
    return {
        "accepted_extension_count": sum(bool(row["accepted"]) for row in rows),
        "bound_helper_core_hashes": {key: route[key]["core_sha256"] for key in HELPER_KEYS},
        "historical_V99_card_sha256": canonical_sha(old),
        **{key: copy.deepcopy(route[key]) for key in HELPER_KEYS},
        "preserved_natural_Spin_c_normal_pair": copy.deepcopy(old["normal_pair"]),
        **{key: copy.deepcopy(old[key]) for key in retained},
        "actual_original_MW_free_rank": None,
        "actual_original_nonzero_section_constructed": False,
        "all_original_cubic_sections_excluded": False,
        "all_original_rational_sections_excluded": False,
        "physical_background_category_identified": False,
        "full_quantum_anomaly_cancelled": False,
        "same_action_spectrum_and_geometry_realized": False,
        "soft_spectrum_unification_cosmology_complete": False,
        "experimental_confirmation": False,
    }


def content():
    previous = load_bound(V99_PATH, EXPECTED_CORES["v99_master"])
    route = load_bound(V100_PATH, EXPECTED_CORES["v100_route"])
    rows = copy.deepcopy(previous["route_matrix"])
    if len(rows) != 27 or [r["ordinal"] for r in rows] != list(range(1, 28)):
        raise RuntimeError("all 27 ordered historical routes are required")
    if route["input_core_hashes"]["v99_master"] != EXPECTED_CORES["v99_master"] or route["next_required_action"]["id"] != NEXT_ID:
        raise RuntimeError("V100 lineage or F101 obligation changed")
    if not previous["lineage"]["canonical_V21_gate_scope_unchanged"]:
        raise RuntimeError("canonical V21 scope changed")
    for key in HELPER_KEYS:
        if route[key].get("core_sha256") != canonical_sha(route[key]):
            raise RuntimeError("noncanonical V100 helper: "+key)
    if set(route["gate_ledger"]) != {"G"+str(i) for i in range(1, 9)} or not all(v.startswith("OPEN:") for v in route["gate_ledger"].values()):
        raise RuntimeError("V100 may not promote a branch gate")
    decision = route["terminal_decision"]
    if decision["closed_gates"] or decision["theory_complete"] or decision["same_action_microscopic_parent_accepted"]:
        raise RuntimeError("V100 has no accepted complete microscopic parent")
    for report, base in ((previous, "susy_v99_multipath_g1_frontier_master_audit"),
                         (route, "susy_v100_correlated_quantization_modified_action_section_audit")):
        for name, key in ((base+".py", "generator_sha256"), ("test_"+base+".py", "test_sha256")):
            if file_sha(ROOT/name) != report["artifact_hashes"][key]:
                raise RuntimeError("bound master/route source changed: "+name)
    for key, value in route["artifact_hashes"].items():
        if key.endswith(".py") and file_sha(ROOT/key) != value:
            raise RuntimeError("bound F100 helper source/test changed: "+key)
    rows.append({
        "ordinal": 28, "route_id": "B100",
        "name": "explicit combined operator cover, exact correlated response level, regular spectator obstruction and conditional original section lattice",
        "accepted": False, "same_action_microscopic_completion": False,
        "selected_exact_scaffolds": [
            "the minimal simultaneous C and bare Sigma operator cover has degree4 and a nonsplit square-group pullback; physical orbifold realization is not installed",
            "a genuine R-completed Clifford index quantizes2P on the stated continuous quotient scout; CP3 proves the minimum stack of P/4 is8",
            "the minimum screened gauge-only regular replacement has40 hypers but loses both Phi fields and fails required independent-W cancellation",
            "mixed W equations and the entire finite old fourth-moment budget exclude every regular replacement under the stated frozen GS assumptions",
            "conditional cubic points have Gram matrix[[3,-1],[-1,3]], and their height8 difference yields a distinct square-class descent route without proving existence",
        ],
    })
    criteria = [
        ("A1", "combined operator cover and smooth inverse response", "PASS_CHANGED_CATEGORY_ONLY_ORBIFOLD_DOMAIN_OPEN"),
        ("A2", "single P/4 response on all stated correlated smooth backgrounds", "REJECTED_PRIMITIVE_EIGHTH_PERIOD"),
        ("A3", "eightfold target on the same stated continuous quotient", "PASS_GENUINE_CLIFFORD_ETA_RESPONSE_NOT_SINGLE_TARGET_REPAIR"),
        ("A4", "regular positive carrier with required independent-W frozen GS trivialization", "REJECTED_MIXED_MOMENT_BUDGET_FOR_ENTIRE_FAMILY"),
        ("A5", "minimum gauge-only40 replacement", "PASS_NECESSARY_SCREEN_ONLY_LOSES_PHI_MASS_MODULE"),
        ("A6", "conditional section lattice and difference descent", "PASS_EXACT_CONDITIONAL_GEOMETRY_EXISTENCE_OPEN"),
        ("A7", "full physical action, background identification and section solution", "OPEN_NO_ACCEPTED_PARENT"),
    ]
    return {
        "schema": "susy_v100_multipath_g1_frontier_master_v1", "version": "V100", "status": STATUS,
        "input_core_hashes": copy.deepcopy(EXPECTED_CORES),
        "lineage": {"parent_master": "V99", "new_route": "B100", "parent_route_count": 27,
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
        raise RuntimeError("V100 master core is noncanonical")
    body = copy.deepcopy(report)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("V100 master arithmetic, lineage or scope changed")


def render_markdown(report):
    card = report["consolidated_theory_card"]
    if card["accepted_extension_count"]:
        raise RuntimeError("the readable master may not conceal an accepted extension")
    paragraphs = [
        "# SUSY V100 multipath frontier master",
        "Status: "+report["status"], "Core SHA256: "+report["core_sha256"],
        "The next step is saved as V100. There are useful exact results, but no accepted complete theory. All G1-G8 in this SUSY/C8 branch remain OPEN. All27 earlier route records and canonical V21 evidence are preserved.",
        "## What advanced",
        "On the stated smooth continuous central-quotient scout, adding the R doublet to the formal normal-half spinor gives genuine Dirac operators E_n. Their virtual index is index(E_2)-2index(E_1)+index(E_0)=2P, where P=d^3+x*d^2/2. The resulting integer eta response is defined even on nonbounding closed5 backgrounds. A correlated spin CP3 background with N=D=O(1) gives P/4=3/8, so eight is the exact minimum quantized stack. This is a response-level theorem, not eight new particles, not a cancellation of the single target, and not yet a theorem about the actual physical orbifold category.",
        "A separate degree-four central cover makes the individual gauge root and natural Spin-c operators genuine. Its smooth inverse response has curvature-P/4. However, the actual pulled-back square action has lifted orders8,8,4,4 and an ineffective C2 x C2 kernel; its naive invariant projection kills those bare operator fibers. The cover and response are explicit mathematical options, but an orbifold Dirac domain, relative gluing and microscopic realization remain missing.",
        "The first gauge-only regular replacement passing the specified count, GS, quotient and neutral-parity screens uses40 hypers. Its c'=(-456,-140) has integral quotient half-source(-56,-18). It necessarily removes the old Phi pair and two charge-four light lines, leaving27 free chirals in the restricted free-projector calculation and destroying the inherited Phi mass module. It is not a full repair.",
        "The spectator constraint is stronger than the old bounded scan: pure-W equations require N=108, and the mixed equations force a removed fourth moment of at least25461 versus the entire available24238. Every regular replacement in that frozen GS ansatz fails if independent W anomalies must be trivialized. This does not declare an anomalous global spectator inconsistent, nor exclude changed charges, tensors, other fields or a relative sector.",
        "The original-section calculation identifies the vector component of I2*, giving conditional cubic-point heights3 and pairing-1, determinant8. The rank-two lattice is saturated in its geometric rational span. Its trace and difference have heights4 and8. The difference can descend when z*Delta_K is square even if the factors are individually nonsquare. This is a genuine additional search route on the original Jacobian, but no actual z,H solution or generic no-section certificate exists. Rank stays0..11 and torsion1.",
        "## What remains unresolved",
        "The physical background category, same-action positive SUSY spectrum, masses, full anomaly and relative boundary/corner data, regulator, soft terms, unification and cosmology are not complete. Passing exact code tests validates the recorded calculations and scope checks, not the theory as an empirical description of nature.",
        "## Acceptance ledger",
    ]
    criteria = "\n".join("- "+row["id"]+": "+row["status"] for row in report["acceptance_criteria"])
    tail = ["## Next obligation", report["next_required_action"]["id"], report["next_required_action"]["primary"], report["next_required_action"]["parallel"],
            "[Detailed F100 derivations](SUSY_V100_CORRELATED_QUANTIZATION_MODIFIED_ACTION_SECTION_AUDIT.md)", "## Primary sources"]
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
    print(json.dumps({"version": "V100", "core_sha256": report["core_sha256"], "route_count": len(report["route_matrix"]),
                      "accepted_extensions": report["consolidated_theory_card"]["accepted_extension_count"], "closed_gates": [], "next": NEXT_ID}, indent=2))


if __name__ == "__main__":
    main()
