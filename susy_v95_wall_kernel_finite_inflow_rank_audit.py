"""F95: necessary wall/defect inflow data and original-Jacobian rank bounds."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import sympy as sp
import susy_v91_multipath_g1_frontier_master_audit as common
import v95_wall_symmetry_lift_audit as wall
import v95_local_u1_inflow_lattice_audit as local
import v95_defect_finite_inflow_audit as finite
import v95_original_jacobian_rank_height_audit as geometry

ROOT = Path(__file__).resolve().parent
STEM = "SUSY_V95_WALL_KERNEL_FINITE_INFLOW_RANK_AUDIT"
OUT_JSON, OUT_MD = (ROOT / (STEM + ext) for ext in (".json", ".md"))
TEST_PATH = ROOT / "test_susy_v95_wall_kernel_finite_inflow_rank_audit.py"
PARENTS = {
    "v94_route": ("SUSY_V94_BOUNDARY_DEFECTS_AND_MW_DESCENT_AUDIT.json",
                  "17fd3a60008545b7bde77756ed8b5ec7dd590c18c1cbb1344a5a7cc67dd2686f"),
    "v94_master": ("SUSY_V94_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
                   "8332984113477ebbbc8a1bc44915475cc3c38003c8c3a7ac9c9a5e35fc11da06"),
}
MODULES = (wall, local, finite, geometry)
HELPERS = tuple(module.__name__ for module in MODULES)
STATUS = "V95_UNCHANGED_WALL_EMBEDDING_REJECTED__NECESSARY_INFLOW_TARGETS_AND_RANK_BOUND__NO_ACCEPTED_PARENT"
NEXT_ID = "F96_QUANTIZED_RELATIVE_INFLOW_AND_ORIGINAL_MW_GENERATOR"
canonical_sha, file_sha = common.canonical_sha, common.file_sha


def content():
    parents = {key: common.load_bound(ROOT/name, core) for key,(name,core) in PARENTS.items()}
    old = parents["v94_route"]
    if parents["v94_master"]["next_required_action"]["id"] != "F95_RELATIVE_SPIN_NORMAL_DEFECT_GLUE_AND_INVARIANT_MW_SECTION":
        raise RuntimeError("F95 parent obligation changed")
    w, u, d, g = (module.build_certificate() for module in MODULES)
    for module, certificate in zip(MODULES, (w,u,d,g)):
        module.validate_certificate(certificate)
    old_wall = old["normal_wall_quantization"]["conditional_product_lift_wall_module"]
    if (w["wall_module_descent"]["complex_Weyl_components"] != old_wall["complex_Weyl_components"] or
        w["wall_module_descent"]["failing_complex_Weyl_components"] != old_wall["components_failing_natural_diagonal_spin_kernel"]):
        raise RuntimeError("new kernel result silently changed the V94 module")
    if u["normalization"]["V94_normal_module_changes_this_slice"]:
        raise RuntimeError("normal and U1 anomaly slices were conflated")
    old_defect = old["Phi_zero_locus_and_defect_matching"]
    unit = next(r for r in old_defect["mass_and_index"]["winding_samples"] if r["mass_winding"] == 1)
    if (d["inherited_spectrum"]["net_real_chiral_index"] != unit["signed_total_real_index"] or
        d["inherited_spectrum"]["net_central_charge"] != unit["signed_chiral_central_charge"]):
        raise RuntimeError("finite defect calculation changed the inherited mass operator")
    if g["coefficient_payload_sha256"] != old["actual_Jacobian_and_quadratic_section"]["coefficient_payload_sha256"]:
        raise RuntimeError("geometry changed the original coefficient member")
    periods = [sp.Rational(r["CP3_index_period"]) for r in u["physical_fixed_loci"]]
    shifted = [sp.Rational(r["shifted_CP3_period"]) for r in u["formal_zero_sum_inflow_target"]["rows"]]
    if periods != [sp.Rational(487,4),sp.Rational(487,4),-sp.Rational(21,2)] or sum(periods) != sum(shifted) or sum(periods) != 233:
        raise RuntimeError("local fractional transfer changed the integrated index")
    rank = g["original_free_MW_rank_bound"]
    if rank["original_field_rank_upper_bound"] != 12 or rank["V94_original_torsion_order"] != 1:
        raise RuntimeError("generic K3 rank/torsion summary failed")
    branches = g["conditional_target_height_normalizations"]["branches"]
    if [(b["q_displayed_over_q_section_Sh"],b["required_section_height_class_S_F"],b["surviving_nodes"]) for b in branches] != [(1,["148","768"],[0]),(2,["37","192"],[1])]:
        raise RuntimeError("physical charge and section-height normalization were conflated")
    hashes = {"generator_sha256":file_sha(Path(__file__)),"test_sha256":file_sha(TEST_PATH)}
    for stem in HELPERS:
        for filename in (stem+".py","test_"+stem+".py"):
            hashes[filename] = file_sha(ROOT/filename)
    sources = {}
    for certificate in (w,u,d,g):
        for row in certificate["primary_sources"]:
            sources[row["url"]] = {"url":row["url"],"use":row.get("use",row.get("role","primary reference"))}
    return {
        "schema":"susy_v95_wall_kernel_finite_inflow_rank_audit_v1",
        "version":"V95","status":STATUS,
        "input_core_hashes":{key:value[1] for key,value in PARENTS.items()},
        "scope":"separate SUSY/C8 research branch; canonical V21 physical gate evidence unchanged",
        "wall_symmetry_lift":w,
        "local_U1_inflow_lattice":u,
        "finite_defect_inflow":d,
        "original_Jacobian_rank_height":g,
        "cross_certificate_checks":{
            "unchanged_V94_wall_components_per_C4":28,
            "unchanged_V94_geometric_kernel_failures_per_C4":8,
            "local_U1_slice_is_not_the_f_zero_normal_slice":True,
            "bare_CP3_local_periods":[str(v) for v in periods],
            "formally_shifted_CP3_local_periods":[str(v) for v in shifted],
            "integrated_CP3_index_before_and_after":"233",
            "CP3_index_periods_are_not_defect_eta_phases":True,
            "finite_defect_uses_unchanged_unit_mass_index":True,
            "V94_defect_curvature_residual":old_defect["unit_defect_curvature_matching"]["restricted_B4_plus_defect_I4"],
            "geometry_uses_original_unchanged_coefficients":True,
            "rank_bound_obtained_by_field_inclusion_not_fixed_specialization":True,
            "all_checks_prove_quantized_same_action_completion":False,
        },
        "supersession_boundary":{
            "V94_conditional_product_lift_polynomial_identity_retracted":False,
            "unchanged_module_repair_by_independent_internal_centers": "REJECTED: D is already the identity before the internal quotient",
            "changed_correlated_tangential_embedding_or_new_boundary_structure_excluded":False,
            "fractional_inflow_class_is_quantized_action":False,
            "enlarged_integer_charge_Weyl_lattice_equals_full_Gammahat_representation_lattice":False,
            "bare_defect_phase_is_the_anomaly_of_the_complete_theory":False,
            "V94_defect_curvature_match_retracted":False,
            "original_exact_free_rank_known":False,
            "displayed_height_equals_primitive_section_height_without_normalization":False,
            "V94_cover_section_descent_obstruction_or_twist_fiber_change_retracted":False,
        },
        "terminal_decision":{
            "unchanged_wall_independent_center_repair_excluded":True,
            "pure_U1_fractional_inflow_class_computed":True,
            "restricted_finite_defect_inverse_phase_targets_computed":True,
            "original_free_rank_upper_bound_computed":True,
            "conditional_normalization_aware_height_restrictions_computed":True,
            "actual_original_nonzero_section_constructed":False,
            "actual_original_exact_free_rank_computed":False,
            "full_Gammahat_wall_representations_frozen":False,
            "quantized_relative_WCS_Dai_Freed_trivialization_constructed":False,
            "same_action_microscopic_parent_accepted":False,
            "all_F95_obligations_fully_completed":False,
            "theory_complete":False,"closed_gates":[],
        },
        "gate_ledger":{
            "G1":"OPEN: necessary inflow and geometry targets are sharper, but no common microscopic action realizes them.",
            "G2":"OPEN: the scoped mass-defect operator is unchanged; full interactions, supersymmetry breaking and scales remain missing.",
            "G3":"OPEN: the unchanged V94 wall module fails the geometric kernel even with independent R/flavor signs; a replacement boundary structure is unconstructed.",
            "G4":"OPEN: fractional pure-U1 local classes and finite defect inverse phases are computed, not cancelled by a quantized relative action.",
            "G5":"OPEN: full Gammahat differential inflow, Pfaffian orientation, KK/BV determinant and regulator remain unconstructed.",
            "G6":"OPEN: there is no accepted common-action spectrum and threshold/two-loop unification calculation.",
            "G7":"OPEN: finite defect witnesses refine the selector audit; full quantum gluing, stable vacuum and cosmology remain incomplete.",
            "G8":"OPEN: original MW torsion is trivial and 0<=rank<=12; no original nonzero section, exact rank, realized height or complete matter spectrum is proved.",
        },
        "next_required_action":{
            "id":NEXT_ID,"accepted":False,
            "primary":"Construct or exclude a quantized relative inflow action with the pure-U1 fractional source class (+I(q=2)/4,+I(q=2)/4,-I(q=2)/2), all mixed normal/R/nonabelian terms, and inverse isolated-defect phases (-i on the chosen lens convention, -1 on the torus). Specify a valid boundary tangential map and field representations; independent internal signs cannot repair the unchanged V94 module.",
            "parallel":"Determine the original generic-K3 Picard/Mordell-Weil rank or construct a K-rational non-torsion section. Fix the physical charge normalization before testing its height: the scale-two candidate requires section height37S+192F and near-component intersection, not a primitive height148S+768F by assumption.",
            "not_a_valid_shortcut":"A formal fractional transfer, a nontrivial bare-defect witness, a rank upper bound or a necessary height condition is not a completed quantum theory or a proof of section existence.",
        },
        "primary_sources":list(sources.values()),"artifact_hashes":hashes,
    }


def build_report():
    report=content()
    report["core_sha256"]=canonical_sha(report)
    return report


def validate_report(report):
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("V95 route core is noncanonical")
    body=copy.deepcopy(report)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("V95 route arithmetic, lineage, artifacts or scope changed")


def render_markdown(report):
    lines=["# SUSY V95: wall kernel, necessary inflow and original section bounds","",
        "Status: "+report["status"],"","Core SHA256: "+report["core_sha256"],"",
        "## Outcome","",
        "F95 rules out a specific wall repair, derives exact targets for a different inflow completion, and bounds the original Jacobian's free rank. No common action is accepted. All eight SUSY/C8 gates remain OPEN; canonical V21 physical evidence is unchanged. These are mathematical/model audits, not experimental confirmation.","",
        "## The unchanged wall cannot be repaired with internal signs","",
        "The inclusion Spin4 x Spin2 into Spin6 has kernel D=(-1,-1). D is already the identity in Spin6 before the R/flavor/gauge quotient, so tensoring an independent internal representation cannot change its action. Eight of V94's 28 Weyl components per C4 fail this identity: five in E*, one in det(E), and two positive-charge singlets. N1 scalar partners fail the same test. This excludes the unchanged embedding, not every new boundary cover or correlated tangential structure.","",
        "The formal R assignment r_R=2q_N makes the geometric phase neutral but retains the same eight failures. Its full Cartan anomaly is I_wall(x+2y), not I_wall(x); setting y=-x/2 removes the wall polynomial rather than cancelling the frozen bare normal anomaly. A genuinely different embedding requires recomputing its full bulk and boundary curvature and finite data.","",
        "## Exact fractional U(1) inflow target","",
        "Set the normal and Spin11 Cartan curvatures to zero. The bare anomaly moments (TrQ,TrQ^3) are (47/2,754) at each C4 and (3,-60) on the physical C2 orbit, the sum of its two cover points. Ordinary integer-charge Weyl polynomials lie in Z(1,1)+Z(2,8), because q^3-q is divisible by6. Each local remainder lies outside this enlarged lattice; no set of ordinary wall Weyls alone can cancel it. The actual frozen gauge-representation lattice is smaller, not larger.","",
        "On spin CP3 with f=H and p1=4H^2, the three bare index periods are 487/4,487/4,-21/2. Define J2=I(q=2)=4f^3/3-f*p1/12. The formal transfer (+J2/4,+J2/4,-J2/2) has zero sum and changes these periods to122,122,-11. A common denominator divisible by4 is necessary in this enlarged lattice and this representative attains4. The integrated bulk index remains233, with moments(50,1448); the full visible moments remain(-68,1408). Nothing global has been cancelled by redistributing a zero-sum polynomial.","",
        "This specifies a necessary fractional class only. The shifted local polynomials are nonzero; physical representations, source quantization, mixed anomalies and a differential inflow action remain missing. CP3 is an index-integrality witness, not a lens-space defect phase or a test of a nowhere-zero Higgs phase.","",
        "## Finite defect phases and the Majorana sign","",
        "For the unchanged isolated unit defect, retain three complex channels of physical C8 charge2 and three real channels of charge4. With xi=(eta+h)/2, the gravitationally subtracted phase is exp[-2*pi*i*(3*rho2+(3/2)*rho4)]. The real half is taken before discarding integral spectral data.","",
        "On primitive L8^3(1,1), the explicitly fixed spectral orientation gives bare phase+i and required inverse inflow-i for both spin lifts. Reversing the common orientation/chirality conjugates both phases. On flat S1 x odd-spin T2 with primitive holonomy, the bare and inverse phases are both-1 for either S1 spin choice. The torus sign comes from the Majorana kernel term; reducing modulo1 before taking the real half would lose it.","",
        "The normal spin root shifts the induced tangent spin structure; the physical charge4 Majoranas cannot be called neutral without retaining the corresponding rank-nine spin-change factor. These admissible isolated-model witnesses refine V94's local curvature match but neither generate the full Gammahat bordism group nor construct its relative trivialization. The common bulk/defect orientation dictionary and purely gravitational completion also remain open.","",
        "## Original geometry: a bound and two conditional heights","",
        "Keep the original coefficients and write K=C(X)(T), with X transcendental. Extending constants to the algebraic closure of C(X) yields an elliptic K3 with16 finite I1 fibers and I2*/D6 at infinity. Shioda-Tate and the characteristic-zero K3 Picard bound give0<=rank E(K)<=12 by field inclusion, not numerical specialization. V94's trivial torsion theorem remains valid. No original-field nonzero section or exact rank has been found.","",
        "Original-field sections can meet only the monodromy-fixed simple components0 or1. Their generic-K3 heights are4+2m or3+2m, respectively, with m=P.O>=0. Under the stated flat crepant threefold assumptions, b(P)=2*Kbar+2*pi_*(P.O)-c(P)*S. If displayed charges equal Shioda charges, the scout target148S+768F requires component0 and pi_*(P.O)=72S+378F. If displayed charges are twice Shioda charges, the section height is37S+192F, requiring component1 and pi_*(P.O)=17S+90F.","",
        "The scale-two branch is conditionally compatible with the Spin^c11 parity: singlet/vector charges become even and spinor charges odd. This is a normalization and central-weight check, not a derived global gauge group or an existing section. Neither branch is excluded or proved to exist. V94's anti-invariant cover point still does not descend, and its quadratic twist still changes the required gauge fiber.","",
        "## Next step","",report["next_required_action"]["id"],"",
        report["next_required_action"]["primary"],"",report["next_required_action"]["parallel"],"",
        "## Primary sources","",
    ]
    lines.extend("- ["+row["use"]+"]("+row["url"]+")" for row in report["primary_sources"])
    return "\n".join(lines)+"\n"


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--write",action="store_true")
    args=parser.parse_args()
    report=build_report()
    validate_report(report)
    if args.write:
        OUT_JSON.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8",newline="\n")
        OUT_MD.write_text(render_markdown(report),encoding="utf-8",newline="\n")
    print(json.dumps({"version":"V95","core_sha256":report["core_sha256"],"closed_gates":[],"next":NEXT_ID},indent=2))


if __name__=="__main__":
    main()
