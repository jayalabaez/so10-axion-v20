"""Preserve the V93 route history and append only the scoped F94 results."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import susy_v91_multipath_g1_frontier_master_audit as common

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V94_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT / "SUSY_V94_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v94_multipath_g1_frontier_master_audit.py"
V93_PATH = ROOT / "SUSY_V93_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V94_PATH = ROOT / "SUSY_V94_BOUNDARY_DEFECTS_AND_MW_DESCENT_AUDIT.json"
EXPECTED_CORES = {
    "v93_master": "d34479d8daa9a37d090e2d2ace471464171a0c28208d3d88b77e5dc168a97932",
    "v94_route": "17fd3a60008545b7bde77756ed8b5ec7dd590c18c1cbb1344a5a7cc67dd2686f",
}
STATUS = "V94_MASTER__CONDITIONAL_BOUNDARY_AND_DEFECT_PROGRESS__SECTION_DESCENT_OBSTRUCTION__NO_ACCEPTED_PARENT"
canonical_sha, file_sha, load_bound = common.canonical_sha, common.file_sha, common.load_bound


def content():
    previous = load_bound(V93_PATH, EXPECTED_CORES["v93_master"])
    route = load_bound(V94_PATH, EXPECTED_CORES["v94_route"])
    normal = route["normal_wall_quantization"]
    defect = route["Phi_zero_locus_and_defect_matching"]
    geom = route["actual_Jacobian_and_quadratic_section"]
    visible = route["visible_Higgs_patch_and_periods"]
    routes = copy.deepcopy(previous["route_matrix"])
    routes.append({"ordinal": len(routes)+1, "route_id": "B94",
        "name": "conditional normal-wall completion, Phi defect curvature matching and actual section descent",
        "accepted": False, "same_action_microscopic_completion": False,
        "selected_exact_scaffolds": [
            "normal Spin2 period screen and alternative 28-Weyl-per-C4 product-lift wall module, not a frozen Gammahat sector",
            "mass-defect real index and tangent/normal curvature identity; full differential action remains missing",
            "visible threshold and independent-phase period audit, with forced-zero Higgs-domain distinction",
            "actual Jacobian torsion triviality; anti-invariant non-torsion cover point and incompatible gauge-changing twist",
        ]})
    criteria = [
        ("A1", "canonical V93/V94 lineage", "PASS_EXACT"),
        ("A2", "normal Spin2 curvature-period repair", "PASS_RESTRICTED_PRODUCT_SPIN_CATEGORY"),
        ("A3", "explicit wall cancellation of the C4 f=0 polynomial", "PASS_CONDITIONAL_28_WEYL_MODULE"),
        ("A4", "new wall module descends to the natural diagonal spin quotient", "REJECTED_EIGHT_COMPONENT_KERNEL_FAILURE"),
        ("A5", "full frozen Gammahat wall and quantum normal lift", "OPEN_UNCONSTRUCTED"),
        ("A6", "nine-field mass-defect index", "PASS_CONDITIONAL_FREDHOLM_INDEX"),
        ("A7", "unit-defect tangent and normal curvature matching", "PASS_EXACT_NOT_DIFFERENTIAL_TRIVIALIZATION"),
        ("A8", "unrestricted independent-periodic visible Phi formula", "REJECTED_PERIOD_176_OVER_3_NOT_A_HIGGS_NO_GO"),
        ("A9", "actual Jacobian torsion subgroup", "PASS_PROVED_TRIVIAL"),
        ("A10", "explicit quadratic-extension point has infinite order", "PASS_EXACT"),
        ("A11", "that point or a nonzero multiple descends to original base", "REJECTED_ANTI_INVARIANT_INFINITE_ORDER"),
        ("A12", "quadratic twist keeps the required B5 gauge fiber", "REJECTED_FORCED_A1_FIBER"),
        ("A13", "original free MW rank, height and full spectrum", "OPEN_UNCOMPUTED"),
        ("A14", "common quantized relative completion and microscopic parent", "OPEN_NOT_FOUND"),
    ]
    unit = next(r for r in defect["mass_and_index"]["winding_samples"] if r["mass_winding"] == 1)
    return {
        "schema": "susy_v94_multipath_g1_frontier_master_v1", "version": "V94", "status": STATUS,
        "input_core_hashes": copy.deepcopy(EXPECTED_CORES),
        "lineage": {"parent_master": "V93", "new_route": "B94",
                    "parent_route_count": len(previous["route_matrix"]),
                    "parent_route_matrix_sha256": canonical_sha(previous["route_matrix"]),
                    "canonical_V21_gate_scope_unchanged": True,
                    "this_master_gate_scope": "separate SUSY/C8 completion branch"},
        "route_matrix": routes,
        "acceptance_criteria": [{"id": i, "requirement": name, "status": status} for i,name,status in criteria],
        "consolidated_theory_card": {
            "accepted_extension_count": sum(bool(r["accepted"]) for r in routes),
            "conditional_wall_Weyl_components": normal["conditional_product_lift_wall_module"]["complex_Weyl_components"],
            "wall_component_count_scope": "per C4 stratum; conditional independent replication at both would give56, not an established global placement",
            "wall_components_failing_natural_diagonal_kernel": normal["conditional_product_lift_wall_module"]["components_failing_natural_diagonal_spin_kernel"],
            "normal_spin_period_pass_scope": "closed ordinary spin4 with chosen normal Spin2 root and specified descent allocation",
            "unit_defect_real_chiral_index": unit["signed_total_real_index"],
            "unit_defect_net_chiral_central_charge": unit["signed_chiral_central_charge"],
            "unit_defect_I4": defect["unit_defect_curvature_matching"]["defect_I4"],
            "defect_curvature_exact_residual": defect["unit_defect_curvature_matching"]["restricted_B4_plus_defect_I4"],
            "full_visible_TrQ_TrQ3": [visible["census"]["moments"]["full"][k] for k in ("TrQ","TrQ3")],
            "actual_Jacobian_torsion_order": geom["actual_full_torsion_theorem"]["torsion_order"],
            "actual_Jacobian_free_MW_rank": geom["actual_full_torsion_theorem"]["free_Mordell_Weil_rank"],
            "cover_point_nonzero_multiples_descend": not geom["quadratic_extension_point"]["no_nonzero_integer_multiple_descends_to_K"],
            "twist_has_non_torsion_section": geom["quadratic_twist_redesign"]["section_is_non_torsion"],
            "twist_minimal_S_orders": geom["quadratic_twist_redesign"]["minimal_S_orders_f_g_Delta"],
            "twist_preserves_required_B5": geom["quadratic_twist_redesign"]["preserves_required_S_B5_algebra"],
            "full_quantum_anomaly_cancelled": False, "same_action_spectrum_and_geometry_realized": False,
            "soft_spectrum_unification_cosmology_complete": False,
        },
        "supersession_ledger": copy.deepcopy(route["supersession_boundary"]),
        "strict_master_decision": copy.deepcopy(route["terminal_decision"]),
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
        raise RuntimeError("V94 master core noncanonical")
    body = copy.deepcopy(report)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("V94 master arithmetic, lineage or scope changed")


def render_markdown(report):
    lines = ["# SUSY V94 multipath frontier master", "",
        "Status: " + report["status"], "", "Core SHA256: " + report["core_sha256"], "",
        "V94 supplies an explicit conditional boundary-matter construction, a local Higgs-defect anomaly match and a geometric section with a proved descent obstruction. Accepted extensions: 0. All eight SUSY/C8 gates remain OPEN.", "",
        "## What changed", "",
        "A chosen normal Spin2 lift admits a restricted integral-period repair. An alternative product-lift wall module with 28 Weyl components per C4 location exactly cancels that location's full f=0 normal/gauge/gravity polynomial. Independent replication at both C4 locations would mean56 components; global placement is unconstructed. Eight components per module fail the natural diagonal spin kernel, so this is not yet a Gammahat-compatible physical sector; all f-dependent and global completion obligations remain.", "",
        "The nine-field mass loop gives real chiral index9 at unit winding, with net central charge9/2. The simple-zero defect's tangent and normal curvature anomaly exactly matches the V93 Higgs-phase term. This does not construct the interacting defect solution, regulated differential inflow or finite Pfaffian phase.", "",
        "The full visible anomaly is retained across the heavy threshold. A naive independent period-one Phi formula fails a 176/3 period test, but that flux background forces Higgs zeros. This is a domain restriction requiring defect completion, not a no-go against every Higgs WZ theory.", "",
        "The actual Jacobian has no nontrivial Mordell-Weil torsion. An explicit infinite-order point exists over its bisection quadratic extension, but it is anti-invariant and no nonzero multiple descends. Its quadratic twist has a rational infinite-order section while changing the required I2*/B5 fiber to I2/A1. The original free rank and height remain unknown.", "",
        "## Acceptance ledger", ""]
    lines.extend("- " + row["id"] + ": " + row["status"] + " — " + row["requirement"] for row in report["acceptance_criteria"])
    lines.extend(["", "## Scope and next step", "",
        "No complete theory, accepted common action or experimental confirmation is claimed. Canonical V21 physical evidence is unchanged.", "",
        report["next_required_action"]["id"], "", report["next_required_action"]["primary"], "",
        report["next_required_action"]["parallel"], "", "## Primary sources", ""])
    lines.extend("- [" + row["use"] + "](" + row["url"] + ")" for row in report["primary_sources"])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate_report(report)
    if args.write:
        OUT_JSON.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8",newline="\n")
        OUT_MD.write_text(render_markdown(report),encoding="utf-8",newline="\n")
    print(json.dumps({"version":"V94","core_sha256":report["core_sha256"],"route_count":len(report["route_matrix"]),
                     "accepted_extensions":report["consolidated_theory_card"]["accepted_extension_count"],
                     "closed_gates":[],"next":report["next_required_action"]["id"]},indent=2))


if __name__ == "__main__":
    main()
