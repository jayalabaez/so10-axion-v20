"""F97: conditional kinetic index, common order-four inflow and section descent."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import sympy as sp
import susy_v91_multipath_g1_frontier_master_audit as common
import v97_normal_SU2_refinement_audit as normal
import v97_equivariant_mass_defect_index_audit as modes
import v97_mixed_gauge_relative_glue_audit as mixed
import v97_original_cubic_section_audit as geometry

ROOT = Path(__file__).resolve().parent
STEM = "SUSY_V97_EQUIVARIANT_INDEX_RELATIVE_GLUE_SECTION_AUDIT"
OUT_JSON, OUT_MD = (ROOT/(STEM+extension) for extension in (".json", ".md"))
TEST_PATH = ROOT/"test_susy_v97_equivariant_index_relative_glue_section_audit.py"
PARENTS = {
    "v96_route": ("SUSY_V96_QUANTIZED_RESPONSES_AND_SECTION_FRONTIER_AUDIT.json", "2c1575f64d2aa3414e6b504d72c20a9a76160825aac7389259ac26402ab8f215"),
    "v96_master": ("SUSY_V96_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json", "d8328579f5162e59a855336aa66bff8ca180f1d7062bb066ee241bbed99503b2"),
}
MODULES = (normal, modes, mixed, geometry)
KEYS = ("normal_SU2_refinement", "equivariant_mass_defect_index", "mixed_gauge_relative_glue", "original_cubic_section")
NEXT_ID = "F98_GAMMAHAT_TRANSPORT_LIFT_AND_ORIGINAL_SQUARE_SECTION"
STATUS = "V97_CONDITIONAL_GAPPED_DIRAC_COMPLETION_AND_COMMON_ORDER4_GLUE__SU2_FLAT_REFINEMENT_AND_CUBIC_BRANCH_EXCLUSION__NO_ACCEPTED_PARENT"
canonical_sha, file_sha = common.canonical_sha, common.file_sha


def crosscheck(parents, n, m, r, g):
    old = parents["v96_route"]
    u, e2, p, c2 = sp.symbols("u e2 p c2")
    target = sp.sympify(n["nonabelian_curvature_repair"]["target_I6"])
    old_target = sp.sympify(old["normal_relative_CS"]["frozen_target"]["repair_target_I6"]).subs(c2, e2)
    if sp.expand(target-old_target) != 0:
        raise RuntimeError("new SU2 scout changed the frozen normal target")
    compact = m["compact_equivariant_index"]["charge_block_results"]
    if [row["invariant_signed_index"] for row in compact] != [0, 0]:
        raise RuntimeError("conditional operator invariant index changed")
    if m["small_mass_compact_gap"]["left_and_right_projected_kernel_dimensions_in_that_range"] != [0, 0]:
        raise RuntimeError("conditional small-mass gap changed")
    profile = r["exact_index_decomposition"]["fractional_profile"]
    # The parent is sorted JSON, so use named physical strata, never dict order.
    old_profile = old["local_transport_quantization"]["equivariant_torus_phase"]["local_orbifold_loop_phase_residues"]
    if profile != [old_profile[k] for k in ("z00", "z11", "physical_C2_orbit")]:
        raise RuntimeError("the common mixed-gauge class changed the source divisor")
    if r["primitive_period_and_order"]["rows"][0]["R_periods"] != ["61/4", "61/4", "-1/2"]:
        raise RuntimeError("primitive quotient periods no longer bind V96")
    if g["coefficient_payload_sha256"] != old["original_section_frontier"]["coefficient_payload_sha256"]:
        raise RuntimeError("the original Jacobian member changed")
    if not g["b4_zero_subbranch_exclusion"]["entire_b4_zero_branch_excluded_over_algebraic_closure_C_X"]:
        raise RuntimeError("new scoped section exclusion failed")
    return {
        "unchanged_normal_target_I6": str(target),
        "old_charge_two_mass_model_and_new_virtual_P_carrier_are_same_sector": False,
        "old_mass_model": "The conditional complex Dirac operator uses the frozen V96 determinant-line charge pair and absolute twists. Its index/gap results do not validate the new virtual carrier.",
        "new_mixed_carrier": "M*(D-1)^2 is an integer virtual index for P; the actual normal-root isotropy changes the finite lift. A projective compensator is necessary and not yet a Gammahat representation.",
        "new_SU2_wall_model": "Replacing the two equal R Cartan weights by one complete SU2 doublet changes the wall model. It preserves the normal target at R=0, and needs the explicitly computed flat nu_R response in the stated product category.",
        "all_new_candidate_sectors_simultaneously_installed_in_one_action": False,
        "common_fractional_inflow_profile": profile,
        "common_order4_class_is_the_same_as_isolated_defect_bordism_anomaly": False,
        "independent_wall_normal_and_Phi_vortex_normal_bundles_identified": False,
        "original_geometry_not_replaced_by_square_transport_torus": True,
        "zero_index_or_a_conditional_gap_cancels_anomalies": False,
        "all_new_quantized_responses_glued_to_parent": False,
    }


def content():
    parents = {key: common.load_bound(ROOT/name, core) for key, (name, core) in PARENTS.items()}
    if parents["v96_master"]["next_required_action"]["id"] != "F97_EQUIVARIANT_MASS_DEFECT_INDEX_AND_FULL_RELATIVE_GLUE":
        raise RuntimeError("F97 lineage obligation changed")
    helpers = [module.build_certificate() for module in MODULES]
    for module, certificate in zip(MODULES, helpers):
        module.validate_certificate(certificate)
    n, m, r, g = helpers
    check = crosscheck(parents, n, m, r, g)
    hashes = {"generator_sha256": file_sha(Path(__file__)), "test_sha256": file_sha(TEST_PATH)}
    sources = {}
    for module, certificate in zip(MODULES, helpers):
        for name in (module.__name__+".py", "test_"+module.__name__+".py"):
            hashes[name] = file_sha(ROOT/name)
        for row in certificate["primary_sources"]:
            sources[row["url"]] = copy.deepcopy(row)
    return {
        "schema": "susy_v97_equivariant_index_relative_glue_section_audit_v1",
        "version": "V97", "status": STATUS,
        "input_core_hashes": {key: value[1] for key, value in PARENTS.items()},
        "scope": "Continuation of the separate SUSY/C8 research branch; canonical V21 physical gate evidence remains unchanged.",
        **dict(zip(KEYS, helpers)), "cross_sector_scope_checks": check,
        "supersession_boundary": {
            "V96_uncomputed_mass_index_now_computed_for_one_explicit_quadratic_model": True,
            "forced_mass_zeros_alone_imply_physical_massless_particles": False,
            "zero_projected_index_means_arbitrary_mass_kernel_vanishes": False,
            "V96_mixed_periods_retracted": False,
            "V96_fractional_periods_now_organized_by_one_primitive_order4_class": True,
            "formal_virtual_carrier_is_accepted_physical_transport": False,
            "V96_equal_R_weights_are_already_a_complete_SU2_doublet": False,
            "new_normal_R_curvature_cancellation_erases_flat_Witten_class": False,
            "V96_original_rank_bound_11_changed": False,
            "b4_zero_cubic_subbranch_now_excluded": True,
            "remaining_cubic_equations_solved_or_square_descent_automatic": False,
        },
        "terminal_decision": {
            "conditional_kinetic_operator_and_equivariant_index_computed": True,
            "conditional_small_mass_projected_gap_proved": True,
            "quantized_integer_mixed_gauge_response_pieces_constructed": True,
            "common_primitive_order4_remainder_identified": True,
            "actual_normal_isotropy_failure_and_conditional_compensator_computed": True,
            "SU2_normal_curvature_scout_and_required_flat_Z2_response_computed": True,
            "original_b4_zero_section_branch_excluded": True,
            "remaining_original_section_system_solved": False,
            "full_SMW_Gammahat_SUSY_action_constructed": False,
            "common_quantized_relative_bulk_wall_defect_action_constructed": False,
            "same_action_microscopic_parent_accepted": False,
            "all_F97_obligations_fully_completed": False,
            "theory_complete": False, "closed_gates": [],
        },
        "gate_ledger": {
            "G1": "OPEN: an explicit conditional quadratic model and restricted quantized responses exist, but no common microscopic parent realizes all of them.",
            "G2": "OPEN: the selected complex operator has index zero and a proved small-mass gap, not the full physical SMW/SUSY spectrum or its mass scales.",
            "G3": "OPEN: the actual normal-root twist obstructs the uncorrected virtual carrier; the order-eight compensator, wall placement and full Gammahat representations remain unconstructed.",
            "G4": "OPEN: local integer responses leave a common primitive P/4 profile, whose correlated relative refinement has not been constructed; the SU2 scout also requires its flat Z2 data.",
            "G5": "OPEN: restricted bordism and phase computations do not supply the full Gammahat determinant, same-action regulator, corner gluing or original bare R-torsion ledger.",
            "G6": "OPEN: no accepted same-action full spectrum, thresholds or numerical unification prediction follows from the conditional gap.",
            "G7": "OPEN: the inherited restricted defect inverse is preserved, but its common five-/three-dimensional realization, gravitational anomaly and cosmology remain unresolved.",
            "G8": "OPEN: original torsion is trivial and 0<=rank<=11; the b4=0 branch is excluded, while four equations with a nonzero-square descent condition remain unsolved.",
        },
        "next_required_action": {
            "id": NEXT_ID, "accepted": False,
            "primary": "Construct or exclude a full Gammahat-compatible order-eight compensating lift for the actual-normal-root carrier M*(D-1)^2, retaining its R/flavor curvatures, SMW reality and positive physical field content. If a lift exists, build the order-four relative determinant/gluing for P=d^2*(d+u), including the required normal/SU2 flat refinement and the inherited defect response. A common filling-period constraint is not a substitute for this action.",
            "parallel": "Solve or rigorously exclude the surviving original-Jacobian four-equation system in z,H,K over C(X), with z nonzero and a square in C(X). Preserve the original coefficient member and charge-normalized height; higher-degree and denominator-bearing sections require separate arguments.",
            "not_a_valid_shortcut": "Do not infer massless particle counts from cover winding, identify the conditional charge-two kinetic model with the new virtual carrier, omit normal-root isotropy, erase a flat anomaly using curvature matching, or drop the original-field square condition.",
        },
        "primary_sources": list(sources.values()), "artifact_hashes": hashes,
    }


def build_report():
    report = content()
    report["core_sha256"] = canonical_sha(report)
    return report


def validate_report(report):
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("V97 route core is noncanonical")
    body = copy.deepcopy(report)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("V97 arithmetic, lineage, source pins or scope changed")


def render_markdown(report):
    lines = [
        "# SUSY V97: equivariant index, relative inflow and section descent", "",
        "Status: "+report["status"], "", "Core SHA256: "+report["core_sha256"], "",
        "## Outcome", "",
        "V97 solves several precisely stated subproblems without accepting a common theory: the projected index and a small-mass gap for an explicit quadratic Dirac model; an exact integer-response decomposition leaving one common order-four class; a nonabelian normal/R repair with its necessary flat refinement; and exclusion of another entire original-section branch. All eight SUSY/C8 gates remain OPEN. No experimental confirmation is claimed.", "",
        "## What the mass zeros actually imply", "",
        "Add an explicit kinetic completion to the frozen mass witness: D_mu=[[2*dbar,lambda*mu],[lambda*conj(mu),2*d]], on a flat square cover torus of side L with periodic spin structure, the frozen effective translation and rotation lifts, and no transverse gauge/flavor connection. The charge+2 block has mu=conj(m), domain phases (i,-i), and codomain phases (-1,-1); the conjugate block reverses charge and four-dimensional chirality. Kinetic and mass covariance are checked together.", "",
        "The compact C4-equivariant index of the charge+2 block is chi1+chi3-2*chi2, with character values (0,2,-4,2). Its invariant multiplicity is exactly zero at every finite mass by elliptic homotopy invariance. The isolated linear-core equations are also solved by Gaussian modes: two C4 cores have odd C4 character, and the C2 pair is induced from the odd C2 character. None of these protected core modes survives projection. This is not a calculation of all accidental paired zero modes of the compact nonlinear profile.", "",
        "More strongly, all invariant sections have no constant Fourier component, so the zero-mass singular gap is 2*pi/L. The exact bound |m|<=1/2 gives gap >=2*pi/L-|lambda|/2. Thus both projected kernels vanish whenever |lambda|*L<4*pi, even though the mass vanishes at all four cover fixed points. Forced mass zeros do not alone imply physical massless particles. The result assumes the displayed kinetic operator, metric, connections and smooth domain; a full SMW/Gammahat/supersymmetric action is not supplied by it.", "",
        "## One common mixed-gauge obstruction, with quantized integer pieces", "",
        "On the preimage of U5 in the gauge Spin^c11 group, write D=det(E)*L_aux^2 and d=c1(D)=t+2*ell. The line L_aux is genuine on this subgroup, not a new odd-charge Spin11-singlet. With I(z)=z^3/6-z*p1/24 and K=I(D*M)-I(D)-I(M), each V96 remainder decomposes exactly as R_C4=Z_C4+P/4 and R_physical_C2=Z_C2-P/2, where P=d^2*(d+u). Z_C4 and Z_C2 have explicit integer eta-index plus integral differential-character responses. Their local negative responses are quantized on the specified product backgrounds.", "",
        "P itself is the integer index I(D^2*M)-2*I(D*M)+I(M). The CP3 quotient test realizes its period 1, proving that the remaining quarter-class has exact order four modulo quantized curvatures. The old periods 61/4,61/4,-1/2 are retained, not retracted. On a common background the fractions sum to zero; independent filling changes cancel only when n0+n1-2*n2=0 mod4. The exact period correlation is necessary data for a relative construction, not a constructed relative action.", "",
        "The virtual bundle M*(D-1)^2 has rank zero, first Chern character zero and index P, so a formal application of the old shifted-character difference has the desired quarter/half profile with no extra normal term. But the actual normal root M has C4 phase zeta. Including it changes both frozen H fourth powers from -I to +I. The resulting raw degree-six trace is zero but the candidate is inadmissible under the frozen closure. Ordinary C4 characters cannot fix this. A displayed compensating matrix F=diag(zeta^-1,zeta), F^4=-I, restores the phases algebraically; its full Gammahat representation, flavor curvature, physical multiplicities and quantum gluing remain unproved.", "",
        "The new virtual P carrier is not the old charge-two Dirac model. Its formal success cannot borrow that model's gap or spectrum. Nor does the common determinant line identify the wall normal bundle with the separate Phi-vortex normal bundle, or glue the five-dimensional responses to the inherited three-dimensional spin-CS/ABK inverse.", "",
        "## A nonabelian R repair must retain its Witten sign", "",
        "As a separate product-category scout, replace the old two equal R Cartan weights by a genuine SU2_R doublet with common normal-root weight -3. Its anomaly polynomial is -9*u^3+3*u*c2(R)+u*p1/4. The integral degree-six character -u*c2(E)+10*u^3-3*u*c2(R) gives precisely the same normal repair target as V96 and cancels the added sector's R-curvature terms without requiring the R bundle to split into lines. The known central kernel acts trivially on this representation. Its orbifold placement and complete supermultiplet are still not constructed.", "",
        "A single Weyl doublet nevertheless has the Witten sign -1 on a unit SU2 instanton times a periodic spin circle, while the displayed bosonic CS response is trivial there. This cannot be avoided just by changing complete SU2 multiplets within the flavor-trivial, odd-normal-weight, no-gravitational-CS ansatz: sum(d_R*k)=-6 forces the total instanton-index parity to be odd.", "",
        "The ordinary-spin product bordism group with U1_M, SU2_R and U5_E is computed by explicit Sq2 matrices to be Z2. The flat ratio of the new doublet/CS response to the R-trivial reference is therefore exactly nu_R=(-1)^(ind2 D5_Rfund), fixed by its generator value. Multiplying by nu_R restores that reference on all backgrounds of this restricted category; it does not trivialize the reference anomaly, identify the original bare R anomaly, or supply a microscopic inflow sector. The broader tangential/normal half-period obstruction and full Gammahat descent remain open.", "",
        "## Original section search: an exact exclusion and a smaller system", "",
        "An exact coordinate change x_section=9*s-6*c, y_section=27*w rewrites the unchanged Jacobian as w^2=s*(s-c)^2-4*a*e*s+b^2*e. In the surviving leading-minus-24 cubic-x branch, split by the leading quartic-y coefficient b4. For b4=0, the h=0 subcase has a necessary equation nonzero at X=1. For h!=0, recursion gives necessary polynomials in h^2; their degrees are preserved at X=1 and modulo 101, where the first pair has resultant 37. This proves the generic resultant nonzero and excludes this leading-minus-24 b4=0 branch even over the algebraic closure of C(X). The statement does not exclude the separate leading-plus-12 branch after a field extension. It is not a rank-specialization argument.", "",
        "Every remaining cubic candidate must therefore have y degree exactly four. Set b4=108*r, z=r^2!=0 and y=108*r*(T^4+H*T^3+K*T^2+L*T+M). Exact elimination reduces the branch to four saved polynomial equations in z,H,K. The only variable denominator is a power of z, and the excluded z=0 case was handled separately. An original-field point additionally requires z to be a square in C(X); a nonsquare gives only a quadratic-cover point whose y changes sign. The reduced system remains unsolved. Torsion stays trivial and the rank bound remains 0<=rank<=11.", "",
        "## Next step", "", report["next_required_action"]["id"], "",
        report["next_required_action"]["primary"], "", report["next_required_action"]["parallel"], "",
        "## Primary sources", "",
    ]
    lines.extend("- ["+row["use"]+"]("+row["url"]+")" for row in report["primary_sources"])
    return "\n".join(lines)+"\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate_report(report)
    if args.write:
        OUT_JSON.write_text(json.dumps(report, sort_keys=True, indent=2)+"\n", encoding="utf-8", newline="\n")
        OUT_MD.write_text(render_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps({"version": "V97", "core_sha256": report["core_sha256"], "closed_gates": [], "next": NEXT_ID}, indent=2))


if __name__ == "__main__":
    main()
