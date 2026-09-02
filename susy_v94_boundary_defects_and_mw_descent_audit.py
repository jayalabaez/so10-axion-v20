"""F94: scoped normal-wall completion, defect matching and MW descent tests."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import sympy as sp
import susy_v91_multipath_g1_frontier_master_audit as common
import v94_normal_wall_quantization as normal
import v94_phi_defect_anomaly_matching as defects
import v94_jacobian_mordell_weil_audit as geometry
import v94_visible_higgs_global_patch_audit as visible

ROOT = Path(__file__).resolve().parent
STEM = "SUSY_V94_BOUNDARY_DEFECTS_AND_MW_DESCENT_AUDIT"
OUT_JSON, OUT_MD = (ROOT / (STEM + ext) for ext in (".json", ".md"))
TEST_PATH = ROOT / "test_susy_v94_boundary_defects_and_mw_descent_audit.py"
PARENTS = {
    "v93_route": ("SUSY_V93_LOCALIZED_ANOMALY_R_LIFT_JACOBIAN_AUDIT.json",
                  "4f81852d9e272d3fb12946ad41cb01d9f93462f75cef69123106a80b03f092f2"),
    "v93_master": ("SUSY_V93_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
                   "d34479d8daa9a37d090e2d2ace471464171a0c28208d3d88b77e5dc168a97932"),
}
HELPERS = ("v94_normal_wall_quantization", "v94_phi_defect_anomaly_matching",
           "v94_jacobian_mordell_weil_audit", "v94_visible_higgs_global_patch_audit")
STATUS = "V94_CONDITIONAL_NORMAL_WALL_MODULE_AND_DEFECT_MATCH__QUADRATIC_SECTION_DOES_NOT_DESCEND__NO_ACCEPTED_PARENT"
NEXT_ID = "F95_RELATIVE_SPIN_NORMAL_DEFECT_GLUE_AND_INVARIANT_MW_SECTION"
canonical_sha, file_sha = common.canonical_sha, common.file_sha


def content():
    parents = {key: common.load_bound(ROOT / name, core)
               for key, (name, core) in PARENTS.items()}
    if parents["v93_master"]["next_required_action"]["id"] != "F94_QUANTIZED_RELATIVE_WALL_COMPLETION_AND_MW_HEIGHT":
        raise RuntimeError("F94 lineage obligation changed")
    n, d, g, v = (module.build_certificate() for module in (normal, defects, geometry, visible))
    for module, certificate in zip((normal, defects, geometry, visible), (n, d, g, v)):
        module.validate_certificate(certificate)
    # Independently place the conditional U5 wall polynomial at BOTH C4 loci.
    old_bulk = parents["v93_route"]["bare_bulk_local_anomaly"]["calculation"]
    wall = sp.sympify(n["conditional_product_lift_wall_module"]["full_wall_polynomial"])
    e = sp.symbols("e1:6")
    reflected = sp.expand(wall.subs({z:-z for z in e[2:]}, simultaneous=True))
    normal_sums = []
    for point, poly in (("z00",wall),("z11",reflected)):
        bare = sp.sympify(old_bulk["per_stratum"][point]["total"]).subs(sp.Symbol("f"),0)
        difference = sp.expand(bare + poly)
        if difference != 0:
            raise RuntimeError("conditional wall cancellation fails at " + point)
        normal_sums.append({"stratum":point,"bare_plus_conditional_wall_f_zero":str(difference)})
    charge_rows = d["mass_and_index"]["ordered_charges"]
    heavy = v["census"]["moments"]["heavy"]
    if (sum(charge_rows),sum(q**3 for q in charge_rows)) != (heavy["TrQ"],heavy["TrQ3"]):
        raise RuntimeError("defect operator and visible threshold use different charges")
    if d["unit_defect_curvature_matching"]["restricted_B4_plus_defect_I4"] != "0":
        raise RuntimeError("defect curvature match failed")
    old_geometry = parents["v93_route"]["actual_member_Jacobian_and_torsor"]
    if g["coefficient_payload_sha256"] != old_geometry["coefficient_payload_sha256"]:
        raise RuntimeError("geometry switched coefficient member")
    if (g["actual_full_torsion_theorem"]["torsion_order"] != 1 or
        not g["quadratic_extension_point"]["point_is_non_torsion"] or
        not g["quadratic_extension_point"]["no_nonzero_integer_multiple_descends_to_K"] or
        g["quadratic_twist_redesign"]["minimal_S_orders_f_g_Delta"] != [0,0,2]):
        raise RuntimeError("section/twist summary no longer follows from computed helper")
    hashes = {"generator_sha256": file_sha(Path(__file__)), "test_sha256": file_sha(TEST_PATH)}
    for stem in HELPERS:
        for filename in (stem + ".py", "test_" + stem + ".py"):
            hashes[filename] = file_sha(ROOT / filename)
    sources = {}
    for report in (n, d, g, v):
        for row in report["primary_sources"]:
            sources[row["url"]] = {"url": row["url"], "use": row.get("use", row.get("role", "primary reference"))}
    return {
        "schema": "susy_v94_boundary_defects_and_mw_descent_audit_v1",
        "version": "V94", "status": STATUS,
        "input_core_hashes": {key: value[1] for key, value in PARENTS.items()},
        "scope": "separate SUSY/C8 research branch; canonical V21 physical gate evidence unchanged",
        "normal_wall_quantization": n,
        "Phi_zero_locus_and_defect_matching": d,
        "actual_Jacobian_and_quadratic_section": g,
        "visible_Higgs_patch_and_periods": v,
        "cross_certificate_checks": {
            "both_C4_normal_restrictions": normal_sums,
            "conditional_wall_components_per_C4": 28,
            "conditional_components_if_independently_replicated_at_both_C4": 56,
            "replication_constructs_global_wall_orbibundle": False,
            "defect_operator_and_visible_threshold_heavy_moments_match": True,
            "defect_B4_plus_I4": "0",
            "actual_Jacobian_uses_unchanged_V93_coefficients": True,
            "checks_prove_global_same_action_completion": False,
        },
        "supersession_boundary": {
            "V93_half_period_result_retracted": False,
            "new_normal_spin_lift_is_same_as_an_independent_ordinary_normal_axion": False,
            "effective_stabilizer_no_root_proves_full_Gammahat_no_root": False,
            "conditional_product_wall_module_is_an_accepted_microscopic_sector": False,
            "defect_normal_equals_six_dimensional_orbifold_normal": False,
            "defect_local_index_proves_full_interacting_SUGRA_spectrum": False,
            "independent_scalar_period_failure_excludes_Higgs_WZ_with_defects": False,
            "no_Jacobian_torsion_implies_no_free_MW_generators": False,
            "quadratic_extension_section_is_an_actual_base_field_U1_generator": False,
            "quadratic_twist_preserves_the_B5_gauge_fiber": False,
        },
        "terminal_decision": {
            "conditional_normal_spin_period_repair_constructed": True,
            "conditional_wall_fermion_normal_slice_cancellation_constructed": True,
            "mass_sector_defect_index_and_curvature_matching_computed": True,
            "actual_Jacobian_torsion_subgroup_trivial": True,
            "explicit_non_torsion_section_over_quadratic_extension_constructed": True,
            "that_section_or_nonzero_multiple_descends_to_original_field": False,
            "actual_Jacobian_free_rank_and_height_computed": False,
            "full_Gammahat_wall_representations_frozen": False,
            "quantized_relative_WCS_Dai_Freed_trivialization_constructed": False,
            "same_action_microscopic_parent_accepted": False,
            "all_F94_obligations_fully_completed": False,
            "theory_complete": False, "closed_gates": [],
        },
        "gate_ledger": {
            "G1": "OPEN: an explicit conditional normal-wall sector exists, but no common Gammahat-compatible quantum parent glues it to the defect theory and geometry.",
            "G2": "OPEN: the nine-singlet mass loop has a scoped defect index; full interacting mass operators, supersymmetry breaking and scales remain missing.",
            "G3": "OPEN: proposed wall normal representations require an additional product/central lift; the frozen full localized representation problem is not solved.",
            "G4": "OPEN: normal-slice cancellation and defect curvature matching pass stated assumptions, but all f-dependent and relative/global anomalies remain untrivialized.",
            "G5": "OPEN: no common regulated KK/BV determinant, Pfaffian orientation or full relative WCS/Dai-Freed theory has been constructed.",
            "G6": "OPEN: no accepted same-action full spectrum and threshold/two-loop unification calculation follows from these partial sectors.",
            "G7": "OPEN: heavy matching is retained across the local defect calculation; finite equivariance, the full quantum selector and cosmology remain incomplete.",
            "G8": "OPEN: actual Jacobian torsion is trivial, but its free MW rank/height remain unknown; the explicit quadratic section is anti-invariant and its twist changes B5 to A1.",
        },
        "next_required_action": {
            "id": NEXT_ID, "accepted": False,
            "primary": "Realize the proposed normal-spin root and wall module in one explicit Gammahat/R-compatible bundle action; cancel the remaining U1-dependent local polynomial and glue the computed Phi defect theory into a quantized relative anomaly trivialization.",
            "parallel": "Find an invariant non-torsion section of the ORIGINAL Jacobian or prove its free rank; compute its actual height and codimension-two matter. The anti-invariant section and the gauge-changing twist do not solve this obligation.",
            "not_a_valid_shortcut": "Do not equate an integral restricted anomaly polynomial, a local defect inflow match, or a section on a different curve with an accepted full theory.",
        },
        "primary_sources": list(sources.values()), "artifact_hashes": hashes,
    }


def build_report():
    report = content()
    report["core_sha256"] = canonical_sha(report)
    return report


def validate_report(report):
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("V94 core is noncanonical")
    body = copy.deepcopy(report)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("V94 arithmetic, lineage, files or scientific scope changed")


def render_markdown(report):
    lines = ["# SUSY V94: boundary lifts, Higgs defects and section descent", "",
        "Status: " + report["status"], "", "Core SHA256: " + report["core_sha256"], "",
        "## Outcome", "",
        "F94 produces a conditional boundary-matter repair, a local defect anomaly match, and an exact restriction on a newly constructed geometric section. It does not complete a gate or establish a full quantum theory.", "",
        "## Normal-wall repair and its price", "",
        "For the C4 anomaly at f=0, a separately chosen normal-spin lift x=2u permits an integral normal descent four-form c2(E)-p1(T4)/4-u^2 on closed spin four-manifolds. Moving mixed f terms to the f-descent is essential; keeping the old allocation can impose stronger period screens. This does not quantize the remaining gauge-dependent terms.", "",
        "The fixed-allocation fourfold/eightfold period screens concern a naive independently periodic formula extended over arbitrary normal bundles. A genuinely nowhere-zero charge-one phase in the normal-root line trivializes that line, requiring u=0 integrally; a charge-q phase requires q*u=0. Mixed-flux examples therefore probe extension across defects or patches, not a no-go on the restricted nonzero-phase domain. The S4 half-c2 test has u=0 and retains its earlier force.", "",
        "An alternative is an explicit wall-fermion witness on a separate Spin4 x Spin2 product lift: E at normal charge 1/2, E* at 0, det(E) at 0, det(E)^(-1) at -1/2, two singlets at +1 and fourteen singlets at -1/2. Its 28 Weyl components in 20 multiplets PER C4 stratum cancel that stratum's entire frozen restriction f=0. Independently replicating the module at both C4 locations would require 56 components, but no global wall orbibundle placement has been constructed. These wall and axion proposals are alternative partial repairs, not contributions to add twice. No minimality, masses or supersymmetric completion are claimed.", "",
        "That witness does not descend through the natural diagonal tangent/normal spin kernel. A parity argument excludes a fermion-only half-c2 repair under that restricted diagonal assumption and zero SU5 cubic anomaly. More general internal R/flavor compensation is not excluded. Likewise the normal line has no square-root character on the effective C4/C2 stabilizers; the necessary pullbacks are C8/C4. Whether the existing full Gammahat lift supplies the needed compatible root remains open.", "",
        "## Higgs zeros and anomaly matching", "",
        "The symmetric nine-Weyl mass matrix has determinant proportional to -Phi_minus^9. An isolated, asymptotically gapped winding-n mass defect has real chiral index 9n: at unit winding, three complex and three real net chiral channels, with net chiral central charge 9/2. These are the minimal decoupled-profile counts; accidental opposite-chirality pairs are not excluded by the index. This is a scoped mass-operator result, not the full interacting supergravity string spectrum.", "",
        "With d=c1(D)=2f for the Spin^c(11) gauge determinant, Phi_minus is a section of D^(-4). A simple transverse zero has defect normal line D^(-4) and a spin root D^(-2). The local channel anomaly is I4=(3/2)d^2-(3/16)p1(TSigma). Restricting the V93 matching coefficient -18f^2+3p1(TM4)/16, using p1(TM4)|Sigma=p1(TSigma)+16d^2, gives exactly -I4. This defect normal is distinct from the six-dimensional orbifold normal.", "",
        "The visible moments remain TrQ=-68, TrQ^3=1408. Integrating out the nine heavy fields leaves (-104,544), with the difference retained by the matching phase. The ordinary Spin4 x C8 pure-fermion restriction passes both above and below this threshold; that is not the full mixed/global anomaly test.", "",
        "A naive independent period-one Phi compensator for the FULL gauge polynomial has period 176/3 on spin S2 x S2 with integral f=a+b and other curvatures zero. Its phase is not single-valued on that unrestricted product domain. But a nowhere-zero Phi requires 8c1(L)=0 (equivalently 4c1(D)=0), so this background necessarily contains zeros and lies outside the phase-only Higgs EFT. The test rejects the naive unrestricted formula, not a properly completed Higgs theory with defects.", "",
        "## Actual geometry and a new, incompatible twist", "",
        "For the frozen Jacobian over C(F4), a polynomial specialization and exact unit-ideal computation exclude rational two-torsion even over complex coefficients. Additive I2* reduction then forces the entire Mordell-Weil torsion subgroup to be trivial. This does not determine the free rank.", "",
        "Set d_geo=s*(L+s*p4), the nonsquare defining the bisection extension. The point (12*s*L, 27*s^2*p1*sqrt(d_geo)) lies on the original Jacobian over the quadratic extension and has infinite order. Good reductions of its rational specialization have 5 and 16 points, which rule out torsion. The extension involution sends the point to its negative, so neither it nor any nonzero multiple descends to the original base field.", "",
        "The corresponding quadratic twist has an explicit base-field non-torsion section, but at S its minimal orders become (0,0,2): the I2*/B5 fiber becomes I2/A1. This is a different geometric candidate, not the required Spin11-plus-U1 completion. The original Jacobian's free rank, height, full charged spectrum and same-action realization remain open.", "",
        "## Next step", "", report["next_required_action"]["id"], "",
        report["next_required_action"]["primary"], "", report["next_required_action"]["parallel"], "",
        "All eight SUSY/C8 gates remain OPEN. Canonical V21 physical evidence is unchanged. No experimental confirmation is claimed.", "",
        "## Primary sources", ""]
    lines.extend("- [" + row["use"] + "](" + row["url"] + ")" for row in report["primary_sources"])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate_report(report)
    if args.write:
        OUT_JSON.write_text(json.dumps(report, sort_keys=True, indent=2)+"\n", encoding="utf-8", newline="\n")
        OUT_MD.write_text(render_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps({"version": "V94", "core_sha256": report["core_sha256"], "closed_gates": [], "next": NEXT_ID}, indent=2))


if __name__ == "__main__":
    main()
