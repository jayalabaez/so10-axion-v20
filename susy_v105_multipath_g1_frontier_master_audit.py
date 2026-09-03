"""Preserve 32 historical routes; explicitly supersede the corrupted B104 cores."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import susy_v91_multipath_g1_frontier_master_audit as common

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT/"SUSY_V105_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT/"SUSY_V105_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT/"test_susy_v105_multipath_g1_frontier_master_audit.py"
PREVIOUS_PATH = ROOT/"SUSY_V104_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
ROUTE_PATH = ROOT/"SUSY_V105_Q2_REPAIR_FULL_REDUCTION_AUDIT.json"
EXPECTED_CORES = {"v104_master": "ecaff36a770c6d3bea417b7ddfa7238345b0508e62e2c320aa7d2d6ccc13e064", "v105_route": "75d6be819200079760202dd9cd4dadf13cb0978717edf677149caa00eb8aa045"}
NEXT_ID = "F106_Q2_RECONSTRUCTION_CHARTS_Q1_TARGETS_AND_COVARIANT_ACTION_REPAIR"
canonical_sha, file_sha, load_bound = common.canonical_sha, common.file_sha, common.load_bound


def content():
    previous = load_bound(PREVIOUS_PATH, EXPECTED_CORES["v104_master"])
    route = load_bound(ROUTE_PATH, EXPECTED_CORES["v105_route"])
    if route["input_core_hashes"]["v104_master"] != EXPECTED_CORES["v104_master"] or route["parent_obligation"] != previous["next_required_action"]["id"]:
        raise RuntimeError("the V105 parent edge or obligation changed")
    if route["next_required_action"]["id"] != NEXT_ID:
        raise RuntimeError("the F106 obligation changed")
    for report, base in ((previous, "susy_v104_multipath_g1_frontier_master_audit"), (route, "susy_v105_q2_repair_full_reduction_audit")):
        for name, pin in ((base+".py", "generator_sha256"), ("test_"+base+".py", "test_sha256")):
            if file_sha(ROOT/name) != report["artifact_hashes"][pin]:
                raise RuntimeError("bound integration source/test changed: "+name)
    for name, value in route["artifact_hashes"].items():
        if name.endswith(".py") and file_sha(ROOT/name) != value:
            raise RuntimeError("bound F105 helper source/test changed: "+name)
    helper = route["q2_repair_full_reduction"]
    if helper.get("core_sha256") != canonical_sha(helper):
        raise RuntimeError("noncanonical F105 helper")
    for name, sha in helper["independent_V105_correction_compatibility"]["source_and_test_pins"].items():
        if file_sha(ROOT/name) != sha:
            raise RuntimeError("independent incoming V105 correction changed: "+name)
    rows = copy.deepcopy(previous["route_matrix"])
    if len(rows) != 32 or [r["ordinal"] for r in rows] != list(range(1, 33)):
        raise RuntimeError("the complete 32-route historical record is required")
    if not route["supersession_boundary"]["V104_corrupted_cores_and_28_97_91_witnesses_retracted_as_original_Q2_evidence"]:
        raise RuntimeError("the B104 derived evidence retraction must be explicit")
    if helper["retraction_and_replacement"]["V104_derived_cores_and_28_97_91_witnesses_accepted_as_original_Q2_evidence"]:
        raise RuntimeError("corrupted B104 evidence cannot remain active")
    if helper["retraction_and_replacement"]["corrected_witnesses_mod101"] != [81, 14, 16]:
        raise RuntimeError("corrected projection witnesses changed")
    decision = route["terminal_decision"]
    if any(decision[k] for k in ("Q2_solved", "Q2_excluded", "same_action_microscopic_parent_accepted", "theory_complete")) or decision["closed_gates"]:
        raise RuntimeError("no section or physical completion is accepted here")
    if set(route["gate_ledger"]) != {"G"+str(i) for i in range(1, 9)} or not all(v.startswith("OPEN:") for v in route["gate_ledger"].values()):
        raise RuntimeError("all branch gates remain open")
    rows.append({"ordinal": 33, "route_id": "B105", "name": "source conversion retraction, corrected Q2 confinement and complete residual root atlas",
                 "accepted": False, "same_action_microscopic_completion": False,
                 "selected_exact_scaffolds": [
                     "the frozen V104 converter sends h to1 and shifts parameter exponents; its derived core evidence is explicitly superseded",
                     "five exact original-residual division identities replace that evidence, with new fixed projection determinants81,14,16mod101",
                     "five regular rational-q reconstruction charts and one zero-slope square-condition chart cover the full corrected Q2 point set",
                     "the parameter systems, Q1, target sections, rank and same-action physical repair remain unsolved",
                 ]})
    if any(r["accepted"] for r in rows):
        raise RuntimeError("no accepted extension exists in this ledger")
    card = copy.deepcopy(previous["consolidated_theory_card"])
    historical_q2 = card.pop("q2_core_reduction")
    card.update({
        "accepted_extension_count": 0,
        "historical_V104_card_sha256": canonical_sha(previous["consolidated_theory_card"]),
        "historical_V104_q2_derived_claims": {"active_evidence": False, "status": "SUPERSEDED_SOURCE_CONVERSION_ERROR", "snapshot": historical_q2},
        "q2_core_reduction": {"source": "corrected V105 original-residual certificate", "helper_core_sha256": helper["core_sha256"],
                              "Q2_confined_to_proper_subvariety": True, "corrected_determinants_mod101": [81, 14, 16],
                              "all_five_residuals_reconstructed": True, "regular_reconstruction_charts": 5,
                              "zero_slope_original_field_square_condition_retained": True, "Q2_solved": False, "Q2_excluded": False},
        "q2_repair_full_reduction": copy.deepcopy(helper),
        "all_original_quartic_sections_excluded": False, "all_original_rational_sections_excluded": False,
        "actual_original_nonzero_section_constructed": False, "actual_target_sections_constructed": False,
        "actual_original_MW_free_rank": None, "experimental_confirmation": False,
    })
    criteria = copy.deepcopy(previous["acceptance_criteria"])
    for row in criteria:
        if row["id"] == "A3":
            row["status"] = "V104_CORE_EVIDENCE_SUPERSEDED__CORRECTED_Q2_ATLAS_AND_CONFINEMENT__Q1_Q2_UNSOLVED"
    return {"schema": "susy_v105_multipath_g1_frontier_master_v1", "version": "V105",
            "status": "V105_MASTER__EXPLICIT_V104_EVIDENCE_RETRACTION__CORRECTED_COMPLETE_Q2_REDUCTION__ALL_BRANCH_GATES_OPEN",
            "input_core_hashes": copy.deepcopy(EXPECTED_CORES),
            "lineage": {"parent_master": "V104", "new_route": "B105", "parent_route_count": 32,
                        "parent_route_matrix_sha256": canonical_sha(previous["route_matrix"]),
                        "canonical_V21_gate_scope_unchanged": True, "this_master_gate_scope": "separate SUSY/C8 completion branch"},
            "route_matrix": rows, "acceptance_criteria": criteria, "consolidated_theory_card": card,
            "supersession_ledger": copy.deepcopy(route["supersession_boundary"]),
            "cross_sector_scope_checks": copy.deepcopy(route["cross_sector_scope_checks"]),
            "strict_master_decision": copy.deepcopy(decision), "gate_ledger": copy.deepcopy(route["gate_ledger"]),
            "next_required_action": copy.deepcopy(route["next_required_action"]), "primary_sources": copy.deepcopy(route["primary_sources"]),
            "artifact_hashes": {"generator_sha256": file_sha(Path(__file__)), "test_sha256": file_sha(TEST_PATH)}}


def build_report():
    out = content()
    out["core_sha256"] = canonical_sha(out)
    return out


def validate_report(out):
    if out.get("core_sha256") != canonical_sha(out):
        raise RuntimeError("noncanonical V105 master")
    body = copy.deepcopy(out)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("V105 master differs from its bound evidence")


def render_markdown(out):
    parts = ["# SUSY V105 multipath frontier master", "Status: "+out["status"], "Core SHA256: "+out["core_sha256"],
             "All 32 historical route records are preserved exactly. B105 is appended as unaccepted route 33. The corrupted part of B104 is explicitly marked as superseded evidence, not silently carried forward. All G1-G8 remain OPEN and canonical V21 scope is unchanged.",
             "## V104 retraction and corrected evidence",
             "A variable-indexing error in the V104 polynomial converter sent h to 1 and shifted all five parameter exponents. Its residual cores and determinant values 28,97,91 are not valid evidence for the original Q2 chart. Its separate leading quadratic identity and h-independent discriminant remain correct. Passing snapshot tests and matching hashes did not establish the missing polynomial round trip.",
             "V105 reconstructs all five original residuals by exact universal division identities. The corrected leading cores have h-degrees 4 and 3, with nonzero fixed 7-by-7 determinants 81,14,16 modulo 101. This independently reestablishes confinement to a proper projection zero locus; it does not exclude that locus or Q2.",
             "The incoming index-correction commit 3cf518b is preserved. Its raw determinant values 65,52,20 agree with these normalized core values by the exact factor t^30 M^14; the four underlying linear coefficients also agree identically. These are different normalizations of the same corrected calculation, not conflicting corrections.",
             "## Full Q2 reconstruction atlas, not a solved section",
             "Five regular charts choose the first nonzero ell_i. On each, one norm equation and four cross equations are equivalent to all original residuals, with q=-mu_i/ell_i and an automatically square discriminant. The sixth case retains all ell_i=mu_i=0 and requires the discriminant to be a square in C(X), including zero. No variable pivot, repeated root or rational-function pole case is silently discarded.",
             "The remaining t,p,h equations have not been solved. Q1, the height-37 and height-148 target systems and general rational sections remain open. Original rank stays 0..11 and torsion order 1; no section, rank increase, full covariant action, quantum inflow, vacuum or empirical confirmation is established.",
             "## Next obligation", out["next_required_action"]["id"], out["next_required_action"]["primary"], out["next_required_action"]["parallel"],
             "[Detailed V105 derivation and retraction](SUSY_V105_Q2_REPAIR_FULL_REDUCTION_AUDIT.md)", "## Primary sources"]
    return "\n\n".join(parts)+"\n\n"+"\n".join("- ["+r["use"]+"]("+r["url"]+")" for r in out["primary_sources"])+"\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    out = build_report()
    validate_report(out)
    if args.write:
        OUT_JSON.write_text(json.dumps(out, sort_keys=True, indent=2)+"\n", encoding="utf-8", newline="\n")
        OUT_MD.write_text(render_markdown(out), encoding="utf-8", newline="\n")
    print(json.dumps({"version": "V105", "core_sha256": out["core_sha256"], "route_count": len(out["route_matrix"]), "closed_gates": [], "next": NEXT_ID}, indent=2))


if __name__ == "__main__":
    main()
