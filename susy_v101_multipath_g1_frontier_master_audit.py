"""Append F101 while preserving all28 historical routes and canonical V21 scope."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import susy_v91_multipath_g1_frontier_master_audit as common

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT/"SUSY_V101_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT/"SUSY_V101_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT/"test_susy_v101_multipath_g1_frontier_master_audit.py"
V100_PATH = ROOT/"SUSY_V100_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V101_PATH = ROOT/"SUSY_V101_COVER_LIFT_HIGGS_SECTION_SOLVABILITY_AUDIT.json"
EXPECTED_CORES = {
    "v100_master": "5727d33c6678cdf23539387e20b2a3cae2ab92095723adfb2a368c7fd2d75a24",
    "v101_route": "a2c321a1889b312305dca187fda511892a2d0e9b3e9e9b18fbcd0a2b9cba42b6",
}
HELPER_KEYS = ("frozen_space_group_cover_obstruction", "Higgs_background_restriction", "intermediate_cover_quantization", "original_section_solvability")
NEXT_ID = "F102_NONZERO_PIVOT_SECTION_CHARTS_AND_COMMON_ACTION_BACKGROUND_RECONSTRUCTION"
STATUS = "V101_MASTER__EXACT_COVER_COSTS_AND_ACTION_OBSTRUCTIONS__ONE_SECTION_CHART_EXCLUDED__ALL_BRANCH_GATES_OPEN"
canonical_sha, file_sha, load_bound = common.canonical_sha, common.file_sha, common.load_bound


def theory_card(route, rows, previous):
    old = previous["consolidated_theory_card"]
    retained = ("actual_original_MW_torsion_order", "actual_original_MW_free_rank_bounds",
                "conditional_unit_charge_section_height_S_F", "conditional_doubled_charge_section_height_S_F")
    return {
        "accepted_extension_count": sum(bool(row["accepted"]) for row in rows),
        "bound_helper_core_hashes": {key: route[key]["core_sha256"] for key in HELPER_KEYS},
        "historical_V100_card_sha256": canonical_sha(old),
        **{key: copy.deepcopy(route[key]) for key in HELPER_KEYS},
        "preserved_natural_Spin_c_normal_pair": copy.deepcopy(old["preserved_natural_Spin_c_normal_pair"]),
        **{key: copy.deepcopy(old[key]) for key in retained},
        "actual_original_MW_free_rank": None,
        "actual_original_nonzero_section_constructed": False,
        "exceptional_all_zero_linear_pivot_chart_excluded": True,
        "nonzero_linear_pivot_charts_still_open": [1, 2, 3],
        "historical_conditional_exceptional_pair_has_instance_on_original_member": False,
        "all_original_cubic_sections_excluded": False,
        "all_original_rational_sections_excluded": False,
        "physical_background_category_identified": False,
        "full_quantum_anomaly_cancelled": False,
        "same_action_spectrum_and_geometry_realized": False,
        "soft_spectrum_unification_cosmology_complete": False,
        "experimental_confirmation": False,
    }


def content():
    previous = load_bound(V100_PATH, EXPECTED_CORES["v100_master"])
    route = load_bound(V101_PATH, EXPECTED_CORES["v101_route"])
    rows = copy.deepcopy(previous["route_matrix"])
    if len(rows) != 28 or [r["ordinal"] for r in rows] != list(range(1, 29)):
        raise RuntimeError("all28 ordered historical routes are required")
    if route["input_core_hashes"]["v100_master"] != EXPECTED_CORES["v100_master"] or route["next_required_action"]["id"] != NEXT_ID:
        raise RuntimeError("V101 lineage or F102 obligation changed")
    if not previous["lineage"]["canonical_V21_gate_scope_unchanged"]:
        raise RuntimeError("canonical V21 scope changed")
    for key in HELPER_KEYS:
        if route[key].get("core_sha256") != canonical_sha(route[key]):
            raise RuntimeError("noncanonical V101 helper: "+key)
    if set(route["gate_ledger"]) != {"G"+str(i) for i in range(1, 9)} or not all(v.startswith("OPEN:") for v in route["gate_ledger"].values()):
        raise RuntimeError("V101 may not promote a branch gate")
    decision = route["terminal_decision"]
    if decision["closed_gates"] or decision["theory_complete"] or decision["same_action_microscopic_parent_accepted"]:
        raise RuntimeError("V101 has no accepted complete microscopic parent")
    for report, base in ((previous, "susy_v100_multipath_g1_frontier_master_audit"),
                         (route, "susy_v101_cover_lift_higgs_section_solvability_audit")):
        for name, key in ((base+".py", "generator_sha256"), ("test_"+base+".py", "test_sha256")):
            if file_sha(ROOT/name) != report["artifact_hashes"][key]:
                raise RuntimeError("bound master/route source changed: "+name)
    for key, value in route["artifact_hashes"].items():
        if key.endswith(".py") and file_sha(ROOT/key) != value:
            raise RuntimeError("bound F101 helper source/test changed: "+key)
    rows.append({
        "ordinal": 29, "route_id": "B101",
        "name": "exact five-cover response costs, exhaustive frozen-action lift obstruction, actual Higgs restrictions and generic exceptional-section exclusion",
        "accepted": False, "same_action_microscopic_completion": False,
        "selected_exact_scaffolds": [
            "the five specified smooth covers have exact positive response stack minima8,2,4,8,1; primitive CP3 cocharacters prove necessity",
            "all89 central generator choices show that no proper cover in this list lifts the unchanged frozen square-group representation",
            "index2 checkerboard and minimum-index4 translation restrictions give explicit changed-domain lifts without installing a new compactification",
            "the original CP3 cannot support the selected nonzero Phi VEVs; internal compensation preserves the selected mass tensor but not a demonstrated full action",
            "two controlled valuations and a universal polynomial saturation consequence exclude the original all-zero-linear-pivot section chart; three other charts remain open",
        ],
    })
    criteria = [
        ("A1", "exact response levels on all five specified smooth covers", "PASS_SCOPED_LEVELS_8_2_4_8_1"),
        ("A2", "single response and unchanged frozen S representation on one listed cover", "REJECTED_BY_EXHAUSTIVE_CENTRAL_LIFT_TEST"),
        ("A3", "changed spatial subgroup lifts", "PASS_EXPLICIT_SECTIONS_NOT_ADOPTED_COMPACTIFICATIONS"),
        ("A4", "original CP3 in the specified nonzero-Phi patch", "REJECTED_NONTRIVIAL_COMBINED_SCALAR_LINES"),
        ("A5", "compensated Higgs and displayed constant mass tensor", "PASS_SELECTED_CARTAN_ONLY_FULL_ACTION_OPEN"),
        ("A6", "generic original all-zero-linear-pivot section chart", "EXCLUDED_TWO_VALUATIONS_AND_UNIVERSAL_SATURATION"),
        ("A7", "remaining sections and common physical completion", "OPEN_NO_ACCEPTED_PARENT"),
    ]
    return {
        "schema": "susy_v101_multipath_g1_frontier_master_v1", "version": "V101", "status": STATUS,
        "input_core_hashes": copy.deepcopy(EXPECTED_CORES),
        "lineage": {"parent_master": "V100", "new_route": "B101", "parent_route_count": 28,
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
        raise RuntimeError("V101 master core is noncanonical")
    body = copy.deepcopy(report)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("V101 master arithmetic, lineage or scope changed")


def render_markdown(report):
    if report["consolidated_theory_card"]["accepted_extension_count"]:
        raise RuntimeError("the readable master may not conceal an accepted extension")
    paragraphs = [
        "# SUSY V101 multipath frontier master",
        "Status: "+report["status"], "Core SHA256: "+report["core_sha256"],
        "The next step is saved as V101. One original section chart is now rigorously excluded, and the response, symmetry and Higgs alternatives have sharper limits. This is verified mathematical progress, not a completed physical theory. All G1-G8 in this SUSY/C8 branch remain OPEN. All28 historical routes and canonical V21 evidence are preserved.",
        "## What advanced",
        "The five intermediate symmetry covers have exact minimum response multiplicities8,2,4,8,1, in the order old quotient, gauge-root, natural Spin-c, diagonal, combined. Integral cup or eta constructions give sufficiency; genuine CP3 cocharacters give primitive periods and necessity. The diagonal cover's genuine Spin-c operator does not make a single Q response quantized on every diagonal background. Matching response curvatures do not prove equal torsion phases.",
        "The actual frozen square-group representation lifts to none of the four proper covers, even after all central choices of generator lifts. Its two invariant defects force both independent deck generators to disappear. Therefore no cover in this list provides both the unchanged representation and an absolute single-Q smooth response. This is not a theorem excluding every new symmetry or relative theory.",
        "There are explicit domain changes: an index2 checkerboard subgroup lifts to the gauge-root cover, and the translation subgroup lifts to the combined cover with minimum index4. These are not installed compactifications. In particular, removing rotations changes the old fixed strata and chirality calculation; a new spectrum cannot be declared unchanged.",
        "The actual selected Higgs lines on V100's original CP3 are O(5) and O(-4), so that background cannot lie in the specified everywhere-nonzero Phi patch. R/flavor compensation can trivialize those combined lines while retaining the3/8 response period. An additional explicit retuning preserves the selected constant mass tensors and all compressed projectors. The full coupling stabilizer, nonlinear QK vacuum, physical backgrounds and UV Higgs-zero defects remain to be constructed. Gauge charge alone does not justify imposing D^4 trivial.",
        "The original exceptional all-zero-linear-pivot section chart is now excluded over algebraic_closure(C(X)). After w=z+4H-3alpha/2, exact Newton-face and coordinate-axis certificates forbid poles at both X=1 and the prime101. A universal polynomial consequence c*ell-b*mu=a*E is derived before specialization and remains valid when a degenerates. The augmented seven-polynomial residue ideal is[1], giving the contradiction. This is not an inference from a finite scan or an uncontrolled specialization.",
        "V100's trace/difference and lattice formulas remain valid conditional identities, but this now-excluded exceptional chart supplies no actual instance on the original generic member. The three nonzero-linear-pivot charts remain OPEN. Original rank is still0..11, torsion1; no actual nonzero section or physical height divisor has been established.",
        "## What remains unresolved",
        "A common action still needs its full spectrum and masses, background category, anomalies and relative boundary/corner data, regulator, soft sector, unification and cosmology. Exact software tests check the recorded derivations and their scope; they are not experimental confirmation or proof that nature realizes this model.",
        "## Acceptance ledger",
    ]
    criteria = "\n".join("- "+row["id"]+": "+row["status"] for row in report["acceptance_criteria"])
    tail = ["## Next obligation", report["next_required_action"]["id"], report["next_required_action"]["primary"], report["next_required_action"]["parallel"],
            "[Detailed F101 derivations](SUSY_V101_COVER_LIFT_HIGGS_SECTION_SOLVABILITY_AUDIT.md)", "## Primary sources"]
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
    print(json.dumps({"version": "V101", "core_sha256": report["core_sha256"], "route_count": len(report["route_matrix"]),
                      "accepted_extensions": report["consolidated_theory_card"]["accepted_extension_count"], "closed_gates": [], "next": NEXT_ID}, indent=2))


if __name__ == "__main__":
    main()
