"""F93: a smooth-sector R lift, fixed-wall mass selection, and local matching.

The R element is new action data in the known smooth-bulk centralizer.  Passing
its matrices through the known central kernel is not a construction of missing
localized representations, a global gauged QK action, or a quantum R symmetry.
"""
from __future__ import annotations

import copy
import json
from fractions import Fraction as F
from itertools import product
from pathlib import Path

import sympy as sp

import v92_singlet_projector_certificate as projectors


ROOT = Path(__file__).resolve().parent
V92_PATH = ROOT / "SUSY_V92_PROJECTORS_LENS_WCS_COMPACT_DECK_ROOT_AUDIT.json"
V92_CORE = "3d4365681c9ebdbcbda6d9d57377a1046a6ab00b3a8b1b2290f2858a7ee4f4fb"
PROJECTOR_CORE = "5d4c91e596ef5182b63f5be4869a41c0c79005dc4dd0fc8cf3683d12c66363fd"


def matrix(value):
    return sp.Matrix([[sp.sympify(x) for x in row] for row in value])


def clean(value):
    return sp.Matrix(value).applyfunc(sp.simplify)


def zero(value):
    return clean(value) == sp.zeros(value.rows, value.cols)


def matrix_json(value):
    return [[str(x) for x in row] for row in clean(value).tolist()]


def load_inputs():
    v92 = json.loads(V92_PATH.read_text(encoding="utf-8"))
    if v92.get("core_sha256") != V92_CORE or projectors.canonical_sha(v92) != V92_CORE:
        raise RuntimeError("changed or noncanonical V92 parent")
    report = v92["smooth_singlet_projectors"]
    if report.get("core_sha256") != PROJECTOR_CORE or projectors.canonical_sha(report) != PROJECTOR_CORE:
        raise RuntimeError("changed V92 projector certificate")
    p = projectors.load_parents()
    if p["v70"]["lorentz_SU2R_and_N1_superfield_lift"]["SU2R_twist"]["preserved_supercharge_product_exponents_mod8"] != [0, 0]:
        raise RuntimeError("the geometric N1 superspace lift changed")
    fields = {row["field"]:row for row in p["v90"]["charged_neutral_and_compensator_repair"]["continuous_charge_table"]}
    if any((fields[name]["continuous_U1_8_charge"],fields[name]["Z4R"]) != expected
           for name,expected in (("Phi_+",(8,0)),("Phi_-",(-8,0)))):
        raise RuntimeError("inherited Phi charges changed")
    return v92, report, p


def block_R_certificate(block, rho):
    """rho is the phase exponent on a whole complex flavor block, mod4."""
    if type(rho) is not int or rho not in range(4):
        raise ValueError("rho must be an integer in Z/4")
    d = block["hyper_count"]
    D = sp.I**rho * sp.eye(d)
    RF = projectors.symplectic_embed(D)
    J = projectors.symplectic_form(d)
    scalar = clean(sp.I*RF)
    hyperino = sp.kronecker_product(sp.eye(2), RF.inv().T)
    real = sp.kronecker_product(projectors.symplectic_form(1), J)
    twists = {key:matrix(value) for key, value in block["underlying_flavor"].items()
              if key in ("A", "U", "V", "external_k")}
    charge = sp.diag(*block["continuous_symplectic_charge_diagonal"])
    constant = sp.diag(matrix(block["constant_projectors"]["plus"]),
                       matrix(block["constant_projectors"]["minus"]))
    checks = {
        "R_flavor_unitary": zero(RF.conjugate().T*RF-sp.eye(2*d)),
        "R_flavor_symplectic": zero(RF.T*J*RF-J),
        "R_flavor_quaternionic_reality": zero(J*sp.conjugate(RF)-RF*J),
        "R_flavor_fourth_identity": zero(RF**4-sp.eye(2*d)),
        "R_scalar_fourth_identity": zero(scalar**4-sp.eye(2*d)),
        "commutes_with_continuous_charge": zero(RF*charge-charge*RF),
        "commutes_with_constant_projector": zero(scalar*constant-constant*scalar),
        "hyperino_SMW_reality_preserved": zero(real*sp.conjugate(hyperino)-hyperino*real),
    }
    checks.update({"commutes_with_"+key:zero(RF*value-value*RF) for key,value in twists.items()})
    for point, row in block["strata"].items():
        h = matrix(row["hyperino_matrix"])
        checks["commutes_with_hyperino_"+point] = zero(hyperino*h-h*hyperino)
    # Kernel entries are central +/- identities.  This element normalizes the
    # SAME kernel, without imposing R^2=(-1)^F or adding a quotient relation.
    if block["Gammahat_kernel_action_exponents_mod2"] != {
        "hyperscalars":{"krot":0,"kspin":0}, "hyperinos":{"krot":0,"kspin":0}
    }:
        raise RuntimeError("known singlet kernel descent changed")
    if not all(checks.values()):
        raise RuntimeError("proposed R element failed an exact smooth-sector check")
    rp, rm = (1+rho)%4, (1-rho)%4
    modes = block["constant_modes"]
    q = block["q_magnitude"]
    return {
        "q_magnitude":q, "kind":block["kind"], "m":block["m"],
        "hyper_count_per_block":d, "flavor_rho_mod4":rho,
        "R_flavor":matrix_json(RF), "N1_scalar_R":matrix_json(scalar),
        "N1_plus_minus_scalar_R_charges":[rp,rm],
        "N1_plus_minus_fermion_R_charges":[(rp-1)%4,(rm-1)%4],
        "partner_superpotential_charge_mod4":(rp+rm)%4,
        "constant_modes":[{"charge":q,"scalar_R":rp,"fermion_R":(rp-1)%4}]*modes["plus"]
                         +[{"charge":-q,"scalar_R":rm,"fermion_R":(rm-1)%4}]*modes["minus"],
        "checks":checks,
        "existing_kernel_action_exponents_mod2":copy.deepcopy(block["Gammahat_kernel_action_exponents_mod2"]),
    }


def singlet_R_extension(projector_report):
    rows, modes = [], []
    phase_census = [0]*4
    for item in projector_report["eleven_mode_normal_aligned_witness"]["direct_sum_blocks"]:
        block, copies = item["certificate"], item["copies"]
        rho = 0
        if block["q_magnitude"] == 8 and block["kind"] == "line":
            rho = {0:3,3:1}[block["m"]]
        result = block_R_certificate(block,rho)
        rows.append({"copies":copies,"certificate":result})
        phase_census[rho] += copies*block["hyper_count"]
        modes += copies*result["constant_modes"]
    modes = sorted(modes,key=lambda row:row["charge"])
    if len(modes) != 11 or phase_census != [265,1,0,1]:
        raise RuntimeError("minimal R-flavor support changed")
    return {
        "construction":"Rtilde=(1_T,1_Spin11,diag(i,-i)_R,D_H3,D_H267,1_k)",
        "new_choice_not_forced_by_V92":True,
        "N1_convention":"theta -> i*theta; selected hyperscalar row carries common Sp1_R factor i",
        "block_formula":"D_rho=diag(i^rho I_d,i^-rho I_d); N1 scalars=i*D_rho, so (r_plus,r_minus)=(1+rho,1-rho)",
        "nontrivial_flavor_support":"rho=3 on Phi_+ hyper; rho=1 on Phi_- hyper; rho=0 on the other265 hypers",
        "complex_half_flavor_phase_multiplicities_rho0123":phase_census,
        "compressed_direct_sum_blocks":rows,
        "constant_mode_R_assignments":modes,
        "all_nine_extras_scalar_R1_fermion_R0":all(r["scalar_R"]==1 and r["fermion_R"]==0 for r in modes if abs(r["charge"])!=8),
        "both_Phi_constants_scalar_R0":all(r["scalar_R"]==0 for r in modes if abs(r["charge"])==8),
        "minimum_nontrivial_flavor_hyper_pairs_with_this_common_R_factor":2,
        "minimality_reason":"Each Phi constant requires rho=3 for a plus zero mode or rho=1 for a minus zero mode; the two constant modes are in distinct hypers. All other pairs can take rho=0.",
        "order_exactly_four_on_smooth_quotient":"theta has phase i, and the nine extra scalars square to -1; fourth powers are identity",
        "new_relation_R_squared_equals_fermion_parity_imposed":False,
        "descends_through_all_current_smooth_kernel_generators":True,
        "reason":"R commutes with all central kernel elements and all bound A,U,V,k matrices; existing representations still kill krot and kspin.",
        "full_unknown_localized_R_representation_constructed":False,
    }


def old_smooth_sector_R(p):
    h_exp = p["v88"]["flavor_centralizer_audit"]["H_AC"]["exponents_mod8"]
    if h_exp != [4,0,4,4,0,4]:
        raise RuntimeError("old smooth flavor translation changed")
    # Reconstruct the actual source half-angle flavor lift from its bound m's.
    # All matrices are diagonal in (A,B,C,A*,B*,C*); no copy permutation is assumed.
    source_rows = p["v88"]["B_neutral_Gammahat_lift"]["projector_reconstruction"]["rows"]
    source_m = {row["hyper"]:row["m"] for row in source_rows}
    a3_plus = [(1+2*source_m[name])%8 for name in ("A","B","C")]
    a3_exp = a3_plus+[(-x)%8 for x in a3_plus]
    if a3_exp != [7,1,3,1,7,5]:
        raise RuntimeError("bound charged-hyper A3 phases changed")
    zeta = (1+sp.I)/sp.sqrt(2)
    A3 = sp.diag(*(zeta**x for x in a3_exp))
    H = sp.diag(*(zeta**x for x in h_exp))
    RF = projectors.symplectic_embed(-sp.I*sp.eye(3))
    J = projectors.symplectic_form(3)
    charges = p["v91"]["quantized_scout"]["bulk_vector_charge_magnitudes"]
    Q = sp.diag(*(charges+[-q for q in charges]))
    k = sp.diag(*(zeta**q for q in charges+[-q for q in charges]))
    checks = {
        "commutes_A3":zero(RF*A3-A3*RF), "commutes_H_AC":zero(RF*H-H*RF),
        "symplectic":zero(RF.T*J*RF-J), "fourth_identity":zero(RF**4-sp.eye(6)),
        "commutes_continuous_U1_and_primitive_k":zero(RF*Q-Q*RF) and zero(RF*k-k*RF),
    }
    table = {row["field"]:row for row in p["v90"]["charged_neutral_and_compensator_repair"]["continuous_charge_table"]}
    matching = []
    for field, side, q in (("H_uA","plus",6),("A0","minus",-6),
                           ("B0","plus",4),("H_uB","minus",-4),("H_dC","plus",6)):
        derived = 0 if side=="plus" else 2
        if table[field]["Z4R"] != derived or table[field]["continuous_U1_8_charge"] != q:
            raise RuntimeError("bound smooth bulk R assignment no longer matches")
        matching.append({"field":field,"N1_side":side,"continuous_charge":q,"derived_scalar_R":derived})
    if table["H_dSigma"]["Z4R"] != 0:
        raise RuntimeError("bound Sigma R charge changed")
    if not all(checks.values()):
        raise RuntimeError("old smooth R-flavor extension failed")
    return {
        "flavor_D_H3":matrix_json(RF), "A3_exponents_mod8":a3_exp,
        "H_AC_exponents_mod8":h_exp, "checks":checks,
        "bound_bulk_field_matches":matching,
        "Sigma_scalar_R":0, "N1_vector_gaugino_R":1,
        "localized_Fi_PA_X_Xbar_S8_SB_SX_and_mediator_lifts_constructed":False,
    }


def wall_selection(projector_report):
    blocks = [item["certificate"] for item in projector_report["eleven_mode_normal_aligned_witness"]["direct_sum_blocks"]]
    selected = {"S"+str(q):(next(b for b in blocks if b["kind"]=="line" and b["q_magnitude"]==q and b["m"]==0),"plus") for q in (2,4,6)}
    selected["Phi_minus"] = (next(b for b in blocks if b["kind"]=="line" and b["q_magnitude"]==8 and b["m"]==3),"minus")
    rows = []
    for point in ("z00","z11","z10","z01"):
        fields = {}
        for name,(block,side) in selected.items():
            source = block["strata"][point]
            phase, projection = matrix(source[side+"_matrix"]),matrix(source[side+"_projector"])
            if phase != sp.eye(1) or projection != sp.eye(1):
                raise RuntimeError("a selected field is absent or noninvariant at a wall")
            fields[name] = {"N1_side":side,"phase":str(phase[0,0]),"invariant_projector_rank":1}
        channels = []
        for names in (("Phi_minus","S2","S6"),("Phi_minus","S4","S4")):
            phases = [sp.sympify(fields[name]["phase"]) for name in names]
            rcharges = [0,1,1]
            channels.append({"fields":list(names),"orbifold_product_phase":str(sp.prod(phases)),
                             "orbifold_d2theta_phase":"1","independent_R4_product_phase":str(sp.I**sum(rcharges)),
                             "independent_R4_d2theta_phase":"-1","all_displayed_selection_rules_pass":True})
        rows.append({"point":point,"stabilizer":selected["S2"][0]["strata"][point]["stabilizer"],
                     "fields":fields,"mass_channels":channels})
    return {
        "rows":rows,
        "Phi_minus_identification":"minus field of q8,m=3,eta=+1 line; NOT its plus field with phase -i",
        "geometric_theta_character":"one at all four stabilizers by the bound V70 preserved N1 supercharge",
        "normal_delta_measure_character":"one: orientation-preserving rotation preserves the real delta2(z-z_fixed) measure",
        "full_hyper_derivative_pairing":"R_plus*R_minus=-1 matches d2theta=-1, while normal derivative is neutral under the NEW independent R",
        "new_wall_tensor":"Phi_minus*(S2^T lambda S6 + S4^T kappa S4/2), with lambda=I3,kappa=I3 as a witness",
        "one_explicit_orbit_choice":"a term at z00 and its lattice translates; z00 is A-fixed and every selected field is invariant there",
        "if_both_Z2_representatives_are_used":"z10,z01 are one A orbit and their coupling tensors must be related by transport; equal tensors suffice for these invariant lines",
        "wall_coupling_mass_dimension_for_canonical_6D_bulk_fields":-3,
        "constant_mode_normalization":"for area A and normalized uniform modes, lambda_4=lambda_wall/A^(3/2); a nonzero wall coefficient gives nonzero overlap",
        "invariant_under_entire_unreduced_Sp267_flavor_group":False,
        "new_coupling_selects_flavor_tensor_and_reduces_flavor_symmetry":True,
        "full_localized_frame_or_gauged_flavor_tensor_completion_constructed":False,
        "operator_derived_from_existing_6D_action":False,
        "mass_scale_numerically_fixed":False,
    }


def alternative_R_assignments():
    dense = [[r2,r4,r6] for r2,r4,r6 in product(range(4),repeat=3)
             if (r2+r6)%4==2 and 2*r4%4==2]
    diagonal_count = sum(1 for r2 in product(range(4),repeat=3)
                         for r4 in product(range(4),repeat=3)
                         if all(2*x%4==2 for x in r4))
    return {
        "fixed_Phi_scalar_R":0,
        "dense_lambda_and_kappa_triplet_uniform_solutions_r2_r4_r6":dense,
        "dense_solution_count":len(dense),
        "fixed_diagonal_pairing_independent_generation_solution_count":diagonal_count,
        "diagonal_rule":"choose each r2_i freely inZ4, r6_i=2-r2_i; each r4_i is1 or3",
        "selected_all_one_assignment":[1,1,1],
        "alternative_requires_recomputing_R_anomalies":True,
    }


def anomaly_matching():
    charges = [2]*3+[4]*3+[6]*3
    tr1, tr3 = sum(charges),sum(q**3 for q in charges)
    x,p1,phi,epsilon = sp.symbols("x p1 phi epsilon")
    k4 = F(tr3,6)*x*x-F(tr1,24)*p1
    exponent = -phi*k4/8
    variation = sp.expand(exponent.subs(phi,phi-8*epsilon)-exponent)
    if sp.expand(variation-epsilon*k4) != 0:
        raise RuntimeError("local anomaly-matching descent failed")
    return {
        "heavy_left_Weyl_charges":charges,"TrQ":tr1,"TrQ3":tr3,
        "heavy_fermion_R_charges":[0]*9,
        "all_heavy_mixed_continuous_or_discrete_R_moments_vanish_in_selected_R_assignment":True,
        "convention":"positive index chirality I6=[Ahat(T) sum exp(q*x)]_6; x=F/(2pi), p1 integral, alpha/(2pi)=epsilon; opposite chirality reverses every sign",
        "I6_heavy":"144*x^3-(3/2)*x*p1",
        "consistent_descent_K4":str(sp.expand(k4)),
        "Phi_phase":"Phi_minus=|Phi_minus|*exp(2*pi*i*phi); delta(phi)=-8*epsilon",
        "local_IR_matching_log_phase_over_2pi_i":str(sp.expand(exponent)),
        "variation_equals_removed_heavy_fermion_descent":str(variation),
        "matching_not_counterterm_sign":"This restores the anomaly carried by the removed heavy fields in the low-energy description; the opposite sign would cancel that anomaly instead.",
        "ordinary_spin4_axion_period_check": {
            "assumptions":"closed smooth spin four-manifold, integral ordinary U1 line bundle, ignoring torsion refinements",
            "integer_relations":"integral(x^2)=2l by Wu parity; integral(p1)=48k since the spin Dirac index in4D is even",
            "phi_shift_one_phase_exponent":"-36*l+9*k, hence integral",
            "curvature_period_check_passes":True,
        },
        "ordinary_spin4_with_Spin_c11_gauge_quotient_period_check": {
            "assumptions":"tangent bundle remains ordinary spin; gauge Spin^c(11) has f=c1(det)/2, and x in the local polynomial denotes f",
            "integer_relations":"integral(c1(det)^2)=2l and integral(p1(T))=48k",
            "phi_shift_one_phase_exponent":"-9*l+9*k, hence integral",
            "curvature_period_check_passes":True,
            "covers_nonspin_tangential_Gammahat_or_torsion_backgrounds":False,
        },
        "pure_untwisted_C8_heavy_fermion_screen": {
            "source_formula":"Hsieh Eq1.2: (n^2+3n+2)*Delta_s3=0 mod6n, 2*Delta_s1=0 modn",
            "n":8,"linear_numerator":2*tr1,"linear_modulus":8,"linear_residue":2*tr1%8,
            "cubic_numerator":90*tr3,"cubic_modulus":48,"cubic_residue":90*tr3%48,
            "pure_heavy_fermion_Spin4_times_C8_restriction_passes":2*tr1%8==0 and 90*tr3%48==0,
            "full_Gammahat_or_mixed_or_continuous_anomaly_cancelled":False,
        },
        "only_valid_locally_on_Phi_nonzero_patch":True,
        "mass_determinant_proportional_to":"-Phi_minus^9",
        "new_invented_axion_required":False,
        "zero_locus_defect_terms_and_global_phase_gluing_constructed":False,
        "supersymmetric_WZ_completion_constructed":False,
        "differential_torsion_or_Dai_Freed_completion_constructed":False,
        "mass_erases_anomaly_matching_obligation":False,
        "full_V90_vacuum_primitive_C8_restored":False,
    }


def build_certificate():
    v92, report, p = load_inputs()
    result = {
        "schema":"v93_mass_sector_symmetry_descent_v1",
        "status":"PASS_NEW_SMOOTH_R_CENTRALIZER_AND_FIXED_WALL_CHARACTERS__LOCAL_MATCHING_ONLY",
        "input_core_hashes":{"v92":V92_CORE,"v92_projectors":PROJECTOR_CORE,
                             **{name:value["core_sha256"] for name,value in p.items()}},
        "known_kernel_coordinates":report["new_flavor_sector"]["kernel_coordinates"],
        "known_kernel_generators":report["new_flavor_sector"]["kernel_generators"],
        "singlet_R_extension":singlet_R_extension(report),
        "old_smooth_bulk_R_extension":old_smooth_sector_R(p),
        "fixed_wall_selection":wall_selection(report),
        "R_assignment_family":alternative_R_assignments(),
        "mass_anomaly_matching":anomaly_matching(),
        "V92_mass_rank_retained":v92["conditional_extra_singlet_mass_module"]["calculation"]["rank_for_v_nonzero"],
        "supersession_scope":"upgrades V92's unconstructed R assignment to an explicit linear smooth-sector lift and checks four wall isotropy characters; does not upgrade its global action or anomaly flags",
        "limitations": {
            "independent_R_is_forced_or_unique":False,
            "all_inherited_localized_R_and_Gammahat_representations_constructed":False,
            "full_gauged_QK_SUGRA_action_with_new_wall_tensor_constructed":False,
            "complete_relative_WCS_and_common_regulator_constructed":False,
            "quantum_Z4R_is_anomaly_free":False,
            "full_theory_or_any_gate_closed":False,
        },
        "primary_sources":[
            {"url":"https://arxiv.org/abs/hep-th/0602155","use":"N1 bulk hyper action and geometric partner twists, Eq1 and44-45; not a source of the newly chosen R assignment"},
            {"url":"https://arxiv.org/abs/1808.01334","use":"Sp1_R doublet hyperscalars versus R-singlet hyperinos; SMW structure, section2.1; even quaternionic Dirac index in4D, section2.2"},
            {"url":"https://arxiv.org/abs/0802.0634","use":"index-normalized4D Weyl anomaly and descent, Eq11.28-11.31; local axion matching mechanism, Eq12.6-12.9"},
            {"url":"https://arxiv.org/abs/1808.02881","use":"Eq1.2 pure untwisted Spin(4) x C8 fermion restriction only; not the full Gammahat anomaly"},
        ],
    }
    if result["V92_mass_rank_retained"] != 9:
        raise RuntimeError("V92 local full-rank mass ansatz changed")
    result["core_sha256"] = projectors.canonical_sha(result)
    return result


def validate_certificate(report):
    if report.get("core_sha256") != projectors.canonical_sha(report) or report != build_certificate():
        raise RuntimeError("changed F93 mass/R certificate")


if __name__ == "__main__":
    print(json.dumps(build_certificate(),indent=2,sort_keys=True))
