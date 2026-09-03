"""F101: the actual Phi lines restrict a Higgs phase, not all UV backgrounds.

All cocharacters below live in the explicitly restricted smooth Cartan scout.
The two selected Phi components are source-bound, but their nonlinear QK vacuum
and all localized coupling tensors are not constructed. No gate is closed.
"""
from __future__ import annotations

import copy
from functools import lru_cache
import json
from pathlib import Path

import sympy as sp

import susy_v91_multipath_g1_frontier_master_audit as common
import v92_singlet_projector_certificate as projectors
import v98_gammahat_compensator_audit as center


ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v100_route": ("SUSY_V100_CORRELATED_QUANTIZATION_MODIFIED_ACTION_SECTION_AUDIT.json", "804242337e0681fe39a84891badd9545447b7f980794366da6a45d4f3277018a"),
    "v100_master": ("SUSY_V100_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json", "5727d33c6678cdf23539387e20b2a3cae2ab92095723adfb2a368c7fd2d75a24"),
    "v92_route": ("SUSY_V92_PROJECTORS_LENS_WCS_COMPACT_DECK_ROOT_AUDIT.json", "3d4365681c9ebdbcbda6d9d57377a1046a6ab00b3a8b1b2290f2858a7ee4f4fb"),
    "v93_route": ("SUSY_V93_LOCALIZED_ANOMALY_R_LIFT_JACOBIAN_AUDIT.json", "4f81852d9e272d3fb12946ad41cb01d9f93462f75cef69123106a80b03f092f2"),
    "v95_route": ("SUSY_V95_WALL_KERNEL_FINITE_INFLOW_RANK_AUDIT.json", "e8ed3aa98cc23726cd41d0b62bbfb8822253d7a9282f1184ba22a77956cb4729"),
}
HELPER_CORES = {
    "smooth_singlet_projectors": "5d4c91e596ef5182b63f5be4869a41c0c79005dc4dd0fc8cf3683d12c66363fd",
    "smooth_R_and_wall_mass_extension": "c4f752b27ae64d447689e96f1125fc34e6b0b94aeaee95a8ee80f0ed52e6cacf",
    "wall_symmetry_lift": "f02222c5f9be6108807ad6be836e2eefbaf1c7c07a5ae0abe72d086e934b3e1f",
    "correlated_quotient_period": "36b93bf55a9bada29e72a5dd68d3636c09d7265a4a8922dd283b532dc4b14660",
    "spectator_GS_obstruction": "4ea657addec22e96eddcdab707cd5159da24eaaa6d288fe1d55f2da4263f8bd3",
}
canonical_sha, file_sha = common.canonical_sha, common.file_sha
ZETA = (1+sp.I)/sp.sqrt(2)
x, d, r, ep, em, e2, e4, e6 = sp.symbols("x d r e_plus e_minus e2 e4 e6")
SCALAR_BITS = (0, 0, 0, 1, 0, 1, 0)


def matrix(value):
    return sp.Matrix([[sp.sympify(z) for z in row] for row in value])


def mj(value):
    return projectors.matrix_json(value)


def load_inputs():
    parents = {key: common.load_bound(ROOT/name, core) for key, (name, core) in PARENTS.items()}
    route, master = parents["v100_route"], parents["v100_master"]
    if master["input_core_hashes"]["v100_route"] != PARENTS["v100_route"][1]:
        raise RuntimeError("V100 route/master lineage changed")
    if master["next_required_action"]["id"] != "F101_PHYSICAL_BACKGROUND_RESTRICTION_RELATIVE_ACTION_AND_SECTION_SOLVABILITY":
        raise RuntimeError("F101 obligation changed")
    for report, base in ((route, "susy_v100_correlated_quantization_modified_action_section_audit"),
                         (master, "susy_v100_multipath_g1_frontier_master_audit")):
        for name, key in ((base+".py", "generator_sha256"), ("test_"+base+".py", "test_sha256")):
            if file_sha(ROOT/name) != report["artifact_hashes"][key]:
                raise RuntimeError("V100 source/test changed: "+name)
    for parent_key, helper_key, base in (
        ("v100_route", "correlated_quotient_period", "v100_correlated_quotient_period_audit"),
        ("v100_route", "spectator_GS_obstruction", "v100_spectator_GS_obstruction_audit"),
        ("v92_route", "smooth_singlet_projectors", "v92_singlet_projector_certificate"),
        ("v93_route", "smooth_R_and_wall_mass_extension", "v93_mass_sector_symmetry_descent"),
        ("v95_route", "wall_symmetry_lift", "v95_wall_symmetry_lift_audit"),
    ):
        report = parents[parent_key]
        helper = report[helper_key]
        if helper.get("core_sha256") != HELPER_CORES[helper_key] or canonical_sha(helper) != HELPER_CORES[helper_key]:
            raise RuntimeError("bound helper changed: "+helper_key)
        for name in (base+".py", "test_"+base+".py"):
            if file_sha(ROOT/name) != report["artifact_hashes"][name]:
                raise RuntimeError("bound helper source/test changed: "+name)
    for name in ("v92_singlet_mass_module.py", "test_v92_singlet_mass_module.py"):
        if file_sha(ROOT/name) != parents["v92_route"]["artifact_hashes"][name]:
            raise RuntimeError("bound mass module source/test changed: "+name)
    old = projectors.load_parents()
    projectors.source_contract(old)
    theta = parents["v95_route"]["wall_symmetry_lift"]["N1_charge_bookkeeping"]
    if (theta["theta_normal_charge"], theta["theta_R_Cartan_weight"]) != ("1/2", 1):
        raise RuntimeError("selected N1 normal/R bookkeeping changed")
    if old["v70"]["lorentz_SU2R_and_N1_superfield_lift"]["SU2R_twist"]["U_R"] != "diag(zeta^-1,zeta), zeta=exp(i pi/4)":
        raise RuntimeError("ordered scalar R row changed")
    parents["v70"] = old["v70"]
    parents["v90"] = old["v90"]
    return parents


def scalar_line(r_root, flavor_root, determinant, q, side):
    """Selected N1 R-first row; the minus is the conjugate flavor/gauge line."""
    if type(q) is not int or q < 0 or q % 2 or side not in ("plus", "minus"):
        raise ValueError("an even nonnegative continuous charge and a selected side are required")
    sign = 1 if side == "plus" else -1
    return sp.expand(r_root+sign*(flavor_root+sp.Rational(q, 2)*determinant))


def profile_roots(profile):
    if profile not in ("original", "Phi_only_compensation", "selected_mass_tensor_compensation"):
        raise ValueError("unknown cocharacter profile")
    roots = {"Phi_plus": sp.Rational(1, 2), "Phi_minus": sp.Rational(1, 2),
             "S2": sp.Rational(1, 2), "S4": sp.Rational(1, 2), "S6": sp.Rational(1, 2)}
    if profile != "original":
        roots.update(Phi_plus=-sp.Rational(9, 2), Phi_minus=-sp.Rational(7, 2))
    if profile == "selected_mass_tensor_compensation":
        roots.update(S2=-sp.Rational(1, 2), S4=-sp.Rational(3, 2), S6=-sp.Rational(5, 2))
    return roots


def block_name(block):
    if block["kind"] != "line":
        return None
    q = block["q_magnitude"]
    return ("Phi_plus" if block["m"] == 0 else "Phi_minus") if q == 8 else "S"+str(q)


def block_cocharacter(block, copies, flavor_root):
    """Exact commuting Lie-generator checks, including reality and projectors."""
    n = block["hyper_count"]
    a = sp.Rational(flavor_root)
    if (2*a).q != 1 or int(2*a) % 2 != 1:
        raise ValueError("the frozen KN+KS endpoint requires every flavor weight odd-half-integral")
    H = sp.diag(*([a]*n+[-a]*n))
    J = projectors.symplectic_form(n)
    Q = sp.diag(*block["continuous_symplectic_charge_diagonal"])
    P = sp.diag(matrix(block["constant_projectors"]["plus"]), matrix(block["constant_projectors"]["minus"]))
    rho4 = {"Phi_plus": 3, "Phi_minus": 1}.get(block_name(block), 0)
    RF = sp.diag(*([sp.I**rho4]*n+[sp.I**(-rho4)]*n))
    checks = {
        "Hermitian_generator": H.conjugate().T == H,
        "symplectic_Lie_algebra": H.T*J+J*H == sp.zeros(2*n),
        "quaternionic_path_reality": J*sp.conjugate(H)+H*J == sp.zeros(2*n),
        "commutes_with_charge": H*Q == Q*H,
        "commutes_with_N1_projector": H*P == P*H,
        "commutes_with_V93_Rtilde": H*RF == RF*H,
        "endpoint_minus_identity": all(sp.simplify(sp.exp(2*sp.pi*sp.I*z)+1) == 0 for z in H.diagonal()),
    }
    checks.update({"commutes_with_"+name: H*matrix(block["underlying_flavor"][name]) == matrix(block["underlying_flavor"][name])*H
                   for name in ("A", "U", "V", "external_k")})
    # Full hyperscalar complexification is R tensor H. Its real involution is
    # the product of two quaternionic structures, NOT four independent scalars.
    K = H+Q/2
    W = sp.kronecker_product(sp.diag(sp.Rational(1, 2), -sp.Rational(1, 2)), sp.eye(2*n))+sp.kronecker_product(sp.eye(2), K)
    reality = sp.kronecker_product(projectors.symplectic_form(1), J)
    checks["full_scalar_real_involution_square_one"] = reality*sp.conjugate(reality) == sp.eye(4*n)
    checks["full_scalar_path_preserves_real_involution"] = reality*sp.conjugate(W)+W*reality == sp.zeros(4*n)
    Af = matrix(block["underlying_flavor"]["A"])
    scalar_A = projectors.clean(ZETA**-1*Af)
    checks["source_ordered_R_first_scalar_row"] = scalar_A == sp.diag(matrix(block["effective_plus"]["A"]), matrix(block["effective_minus_column"]["A"]))
    if not all(checks.values()):
        raise RuntimeError("cocharacter failed actual block checks")
    return {"kind": block["kind"], "q_magnitude": block["q_magnitude"], "m": block["m"],
            "copies": copies, "hypers_per_copy": n, "positive_flavor_weight": str(a),
            "paired_generator": mj(H), "N1_scalar_weights": [str(z) for z in W.diagonal()[:2*n]],
            "full_real_scalar_complexification_weights": [str(z) for z in W.diagonal()],
            "constant_projector": mj(P), "checks": checks}


def selected_fields(saved):
    rows = []
    blocks = saved["eleven_mode_normal_aligned_witness"]["direct_sum_blocks"]
    for item in blocks:
        b = item["certificate"]
        if b["kind"] != "line":
            continue
        name = block_name(b)
        side = "minus" if name == "Phi_minus" else "plus"
        rho = {"Phi_plus": 3, "Phi_minus": 1}.get(name, 0)
        i = 0 if side == "plus" else 1
        scalar_R = sp.I*sp.diag(sp.I**rho, sp.I**(-rho))
        A = projectors.clean(ZETA**-1*matrix(b["underlying_flavor"]["A"]))
        if A[i, i] != 1 or b["constant_modes"][side] != 1:
            raise RuntimeError("selected scalar no longer has its constant line")
        strata = {point: {"phase": str(matrix(value[side+"_matrix"])[0, 0]),
                          "projector": value[side+"_projector"]} for point, value in b["strata"].items()}
        if any(row["phase"] != "1" or row["projector"] != [["1"]] for row in strata.values()):
            raise RuntimeError("selected field is not present at all four strata")
        rows.append({"name": name, "copies": item["copies"], "side": side, "q_magnitude": b["q_magnitude"],
                     "continuous_charge": b["q_magnitude"]*(1 if side == "plus" else -1),
                     "m": b["m"], "flavor_Rtilde_rho_mod4": rho,
                     "scalar_Rtilde_phase": str(scalar_R[i, i]), "scalar_A_matrix": mj(A),
                     "scalar_Rtilde_matrix": mj(scalar_R), "strata": strata,
                     "source_block_sha256": canonical_sha(b)})
    if sum(row["copies"] for row in rows) != 11:
        raise RuntimeError("the eleven selected N1 lines changed")
    return rows


def cocharacter_certificate(saved, profile):
    roots = profile_roots(profile)
    blocks = []
    for item in saved["eleven_mode_normal_aligned_witness"]["direct_sum_blocks"]:
        b = item["certificate"]
        blocks.append(block_cocharacter(b, item["copies"], roots.get(block_name(b), sp.Rational(1, 2))))
    if sum(row["copies"]*row["hypers_per_copy"] for row in blocks) != 267:
        raise RuntimeError("the cocharacter does not account for all 267 old hypers")
    endpoint = tuple((a+b) % 2 for a, b in zip(center.KN, center.KS))
    if endpoint not in center.old_kernel() or any(center.character_descent(SCALAR_BITS, center.old_kernel())):
        raise RuntimeError("actual scalar or cocharacter kernel descent failed")
    degrees = {name: scalar_line(sp.Rational(1, 2), roots[name], 1, q, side)
               for name, q, side in (("Phi_plus", 8, "plus"), ("Phi_minus", 8, "minus"),
                                      ("S2", 2, "plus"), ("S4", 4, "plus"), ("S6", 6, "plus"))}
    pp, pm = degrees["Phi_plus"], degrees["Phi_minus"]
    theta2 = sp.Integer(2)  # x+2r on the bound x=d=1, r=1/2 path.
    cubic = [pm+degrees["S2"]+degrees["S6"], pm+2*degrees["S4"]]
    coupling = [theta2-z for z in cubic]
    return {
        "profile": profile, "space": "spin CP3 with H^3=1, N=D=O(1), p1=4H^2",
        "R_first_root": "1/2", "all_other_H3_and_unlisted_H267_positive_roots": "1/2",
        "selected_H267_positive_roots": {k: str(v) for k, v in roots.items()},
        "lift_endpoint": list(endpoint), "endpoint_kernel_word": "KN+KS",
        "same_known_central_quotient_endpoint": True,
        "all267_compressed_blocks": blocks,
        "selected_N1_scalar_line_degrees": {k: int(v) for k, v in degrees.items()},
        "Phi_pair_bundle": "O("+str(pp)+") + O("+str(pm)+")",
        "Phi_pair_c1_coefficient_H": int(pp+pm), "Phi_pair_c2_coefficient_H2": int(pp*pm),
        "both_selected_Phi_lines_topologically_trivial": pp == pm == 0,
        "D_fourth_power_trivial": False,
        "superpotential_line_degree": int(theta2), "displayed_cubic_degrees": [int(z) for z in cubic],
        "required_lambda_kappa_coupling_line_degrees": [int(z) for z in coupling],
        "constant_V93_lambda_kappa_covariant_under_this_Cartan": all(z == 0 for z in coupling),
        "V100_P_over4_period_unchanged": "3/8",
        "actual_physical_background_admissibility_proved": False,
        "full_old_action_coupling_stabilizer_proved": False,
        "unbroken_supersymmetry_or_covariantly_constant_VEV_proved": False,
    }


def combined_line_and_tensor_formulas():
    lp = scalar_line(r, ep, d, 8, "plus")
    lm = scalar_line(r, em, d, 8, "minus")
    s2, s4, s6 = [scalar_line(r, e, d, q, "plus") for e, q in ((e2, 2), (e4, 4), (e6, 6))]
    theta = x/2+r
    lambda_line = sp.expand(2*theta-lm-s2-s6)
    kappa_line = sp.expand(2*theta-lm-2*s4)
    # A hypothetical conjugate q4 mass uses the OTHER N1 partner of that same
    # hyper. It is not present in the frozen eleven-line V93 mass tensor.
    q4minus = scalar_line(r, e4, d, 4, "minus")
    plus_yukawa = sp.expand(lm+2*(s4-theta))
    minus_yukawa = sp.expand(lp+2*(q4minus-theta))
    both_phi_solution = {ep: -r-4*d, em: r-4*d}
    yp = sp.expand(plus_yukawa.subs(both_phi_solution))
    ym = sp.expand(minus_yukawa.subs(both_phi_solution))
    if sp.expand(yp+ym) != -2*x:
        raise RuntimeError("same-hyper two-Yukawa normal obstruction changed")
    return {
        "formal_roots": "x=c1(N), d=c1(D); r is the first R root; e_plus and e_minus are the positive flavor roots of TWO DISTINCT q8 hypers; e2,e4,e6 denote the selected q2,q4,q6 singleton roots",
        "Phi_plus_line": "R_+ tensor F_Phi+ tensor D^4",
        "Phi_minus_line": "R_+ tensor F_Phi-^dual tensor D^-4",
        "Phi_plus_c1": str(lp), "Phi_minus_c1": str(lm),
        "normal_scalar_weight": 0,
        "individual_R_and_flavor_lines_need_not_descend": True,
        "combined_lines_genuine_after_compatible_Cartan_component_reduction": True,
        "nowhere_zero_VEV_conditions": ["L_Phi+ is trivial as an integral complex line bundle", "L_Phi- is trivial as an integral complex line bundle"],
        "integral_relations": ["(R_+ F_Phi+) is isomorphic to D^-4", "(R_+ F_Phi-^dual) is isomorphic to D^4", "R_+^2 F_Phi+ F_Phi-^dual is trivial"],
        "relations_force_D4_trivial_without_internal_restriction": False,
        "torsion_warning": "The line isomorphisms retain torsion. Zero de Rham curvature alone is not a nowhere-zero-section certificate. A nonzero charge-one section trivializes its ENTIRE associated line, not merely a multiple of its free class.",
        "selected_N1_theta_internal_curvature": str(theta),
        "superpotential_line": "N tensor R_+^2", "superpotential_line_c1": str(2*theta),
        "full_hyper_normal_derivative_pairing_c1": str(sp.expand(scalar_line(r, e4, d, 4, "plus")+scalar_line(r, e4, d, 4, "minus")+x)),
        "derivative_pairing_scope": "The full-hyper partners have opposite flavor/gauge weights; the bound holomorphic normal derivative has character N. Their sum equals the superpotential line for every retuning, so that mandatory bulk pairing is retained at this Cartan level.",
        "theta_scope": "The continuous normal/R bookkeeping is the selected V95 branch. Its extension to curved wall tensor bundles is a conditional diagnostic, not a supersymmetric CP3 vacuum or a completed localized frame.",
        "lambda_coupling_line_c1": str(lambda_line), "kappa_coupling_line_c1": str(kappa_line),
        "mass_tensor": "Phi_minus*(S2^T lambda S6 + S4^T kappa S4/2), with lambda=kappa=I3 in the source-bound local witness",
        "mass_rank_if_nonzero_Phi_and_covariant_nondegenerate_tensors": 9,
        "mass_gap_of_full_theory_proved": False,
        "hypothetical_both_q4_partner_Yukawas": {
            "frozen_V93_contains_both": False,
            "positive_channel": "Phi_minus psi_plus4 psi_plus4",
            "negative_channel": "Phi_plus psi_minus4 psi_minus4, using the OTHER partner of the SAME q4 hyper",
            "after_both_Phi_lines_trivial_positive_c1": str(yp),
            "after_both_Phi_lines_trivial_negative_c1": str(ym),
            "sum_c1": str(sp.expand(yp+ym)),
            "both_constant_channels_require_x_zero_at_curvature_level": True,
            "integral_necessary_condition": "Their product line is N^-2 when both Phi lines are trivial, so both unadorned constant Yukawas require N^2 trivial; x=0 only as a real-curvature consequence. Torsion and independent mass tensors need separate treatment.",
            "CP3_N_O1_passes": False,
            "normal_tensor_or_spurion_could_change_test": True,
        },
    }


@lru_cache(maxsize=2)
def _derived_json(projector_json):
    saved = json.loads(projector_json)
    return json.dumps({"actual_selected_scalar_weights": selected_fields(saved),
                       "combined_Higgs_line_and_mass_tensor": combined_line_and_tensor_formulas(),
                       "CP3_original_cocharacter": cocharacter_certificate(saved, "original"),
                       "CP3_Phi_only_compensated_cocharacter": cocharacter_certificate(saved, "Phi_only_compensation"),
                       "CP3_selected_mass_compensated_cocharacter": cocharacter_certificate(saved, "selected_mass_tensor_compensation")},
                      sort_keys=True, separators=(",", ":"))


def build_certificate():
    p = load_inputs()
    saved = p["v92_route"]["smooth_singlet_projectors"]
    mass = p["v93_route"]["smooth_R_and_wall_mass_extension"]["fixed_wall_selection"]
    if mass["invariant_under_entire_unreduced_Sp267_flavor_group"] or not mass["new_coupling_selects_flavor_tensor_and_reduces_flavor_symmetry"]:
        raise RuntimeError("the old wall tensor's flavor-reduction boundary changed")
    cost = p["v100_route"]["spectator_GS_obstruction"]["minimum_scout_actual_projector_cost"]
    if cost["actual_removed_free_charges"] != [4, 4, 8, -8] or not cost["both_old_Phi_plus_minus8_unavoidably_removed"]:
        raise RuntimeError("the N40 replacement no longer removes the actual Phi modes")
    out = {
        "schema": "v101_actual_Higgs_lines_and_restricted_CP3_compensation_v1",
        "status": "ORIGINAL_CP3_EXCLUDED_FROM_SPECIFIED_DEFECT_FREE_VEV_PATCH__INTERNAL_COMPENSATION_CONDITIONAL__UV_AND_FULL_ACTION_OPEN",
        "input_core_hashes": {k: v[1] for k, v in PARENTS.items()},
        "bound_helper_core_hashes": copy.deepcopy(HELPER_CORES),
        "bound_V70_V90_core_hashes": {k: p[k]["core_sha256"] for k in ("v70", "v90")},
        "category_and_scope": {
            "domain": "The displayed central smooth scout restricted to the gauged-charge centralizer, the frozen square-group projectors, and a selected R/Cartan component reduction. A full independent Sp267 times differently charged U1 representation is not assumed.",
            "scalar_center_coordinate_order": center.OLD_COORDINATES,
            "scalar_center_bits": list(SCALAR_BITS),
            "scalar_kernel_exponents": center.character_descent(SCALAR_BITS, center.old_kernel()),
            "hyperscalar_representation": "R_fund tensor H267_fund with quaternionic-times-quaternionic real structure. On the commuting charge decomposition the selected row carries gauge charges +/-q and no normal scalar character.",
            "source_domain": "The V92 linear representation is at the symmetric QK target origin. Extending a specified component to a global nonlinear nonzero-VEV field configuration requires additional action data.",
            "same_quotient_cocycle_is_sufficient_for_physical_background": False,
            "full_old_Sp267_independent_background_allowed": False,
            "full_localized_tensor_or_QK_vacuum_constructed": False,
        },
        **json.loads(_derived_json(json.dumps(saved, sort_keys=True))),
        "nonzero_section_and_multiplet_boundary": {
            "selected_component_VEV": "A VEV in either specified weight line requires a reduction selecting that line and its trivialization. One may not infer this reduction from an arbitrary nonzero vector in a higher-rank associated bundle.",
            "original_two_selected_lines": "O(5) plus O(-4) on CP3; c2=-20H^2 is nonzero, so even a nowhere-zero section of that rank-two sum is obstructed. It does not exclude every nonzero vector in the entire large hypermultiplet bundle.",
            "Chern_proof": "A nowhere-zero section of a complex rank-two bundle splits off a trivial line after choosing a Hermitian metric, forcing c2=0. For a complex line a nowhere-zero section is a trivialization.",
            "SMW_and_scalar_reality_not_doubled": True,
            "all_old_projected_out_fields_removed_from_UV": False,
            "compensated_line_triviality_implies_covariantly_constant_section": False,
            "compensated_line_triviality_implies_F_D_flat_SUSY_vacuum": False,
        },
        "constant_coupling_and_reduction_boundary": {
            "Phi_only_retuning_is_not_enough_for_frozen_V93_mass_tensor": True,
            "additional_nine_line_retuning_preserves_displayed_constant_lambda_kappa": True,
            "mass_compensated_cocharacter_commutes_with_frozen_Rtilde_and_all267_projectors": True,
            "source_wall_tensor_invariant_under_full_Sp267": False,
            "source_wall_tensor_requires_flavor_reduction": True,
            "all_old_V90_Yukawa_driver_and_mediator_tensors_checked": False,
            "missing_data": ["S8, SB, SX and other localized field/frame representations", "fixed nonzero driver constants and all V90 Yukawa/mediator tensor stabilizers", "global gauged QK sigma model and its composite R connection away from the origin", "one supersymmetric vacuum and anomaly-compatible relative regulator/glue"],
            "specific_retuned_cocharacter_is_accepted_physical_background": False,
            "use": "The retuned cocycle refutes the inference that gauge charge ALONE forces D^4 trivial in this combined representation. It is not a proof that the microscopic theory permits this background after every fixed coupling and VEV is imposed.",
        },
        "UV_IR_and_finite_boundary": {
            "defect_free_fixed_VEV_patch": "Everywhere-nonzero selected Phi sections impose the combined line reductions. With separately trivial internal combined factors this reduces to D^4 trivial (or L^8 trivial on the charge-one covering line).",
            "pure_gauge_Phi_stabilizer_on_cover": "C8 for a charge+/-8 Phi pair alone; internal/gauge locking changes the full stabilizer and must not be silently discarded.",
            "V90_full_VEV_charge_magnitudes": [8, 4, 6], "V90_full_VEV_external_stabilizer_order": 2,
            "V90_full_vacuum_scope": "The earlier proposed B0 and X/Xbar VEVs also participate. Their charge gcd is2, so the complete proposed vacuum is not just the Phi-only C8 phase. Their full background representations remain unconstructed.",
            "UV_Higgs_zeros": "Unless the UV definition separately restricts bundles, Higgs configurations with zeros remain allowed and cannot be excluded by using a fixed-modulus low-energy patch. Those defects require anomaly matching and possibly additional modes.",
            "frozen_nine_mode_mass_determinant": "-Phi_minus^9 for lambda=kappa=I3; its nonzero-rank argument fails on Phi_minus=0",
            "UV_anomaly_erased_by_Higgsing": False,
            "finite_C8_or_residual_C2_torsion_anomaly_computed_here": False,
            "V100_smooth_order_eight_claim_retracted": False,
            "V100_CP3_is_proved_physical_orbifold_background": False,
            "single_P_over4_full_relative_repair_accepted": False,
        },
        "N40_replacement_incompatibility": {
            "bound_actual_removed_free_charges": copy.deepcopy(cost["actual_removed_free_charges"]),
            "both_old_Phi_removed": cost["both_old_Phi_plus_minus8_unavoidably_removed"],
            "old_mass_module_preserved": cost["old_Phi_driven_mass_module_preserved"],
            "may_borrow_old_Phi_background_restriction_without_new_Higgs_sector": False,
            "scope": "The gauge-only40 replacement is a different unaccepted spectrum; a rebuilt Higgs sector and all of its curvature/anomaly/coupling data would be required.",
        },
        "terminal_decision": {
            "actual_Phi_combined_lines_derived": True,
            "original_CP3_in_specified_everywhere_nonzero_Phi_patch": False,
            "restricted_compensated_cocycles_and_selected_mass_tensor_checks_constructed": True,
            "all_physical_backgrounds_classified": False,
            "microscopic_parent_accepted": False, "full_anomaly_cancelled": False,
            "theory_complete": False, "closed_gates": [],
        },
        "primary_sources": [
            {"url": "https://arxiv.org/abs/hep-th/0602155", "use": "Equations44-45 give the N1 orbifold hyper partner rule. The ordered R row, actual two Phi blocks, and independent Rtilde are additionally derived from the bound V70/V92/V93 matrices, not from gauge charges alone."},
            {"url": "https://arxiv.org/abs/2009.04692", "use": "Section4 distinguishes bundle reduction in a Goldstone/Higgs effective theory from UV configurations forced through Higgs zeros. It does not authorize removing the UV anomaly on backgrounds outside a fixed-modulus patch."},
            {"url": "https://pi.math.cornell.edu/~hatcher/VBKT/VB.pdf", "use": "Vector-bundle sections and Chern classes: a nonzero line section trivializes the line; a nonzero rank-two section forces top Chern class zero. This proves the derived CP3 O(5) plus O(-4) obstruction."},
            {"url": "https://arxiv.org/abs/1808.01334", "use": "The six-dimensional hypermultiplet reality/counting convention keeps the symplectic conjugate from being an extra hypermultiplet. Full anomaly cancellation requires more than the linear representation and a local mass term."},
        ],
    }
    out["core_sha256"] = canonical_sha(out)
    return out


def validate_certificate(value):
    if value.get("core_sha256") != canonical_sha(value) or value != build_certificate():
        raise RuntimeError("F101 Higgs lines, matrix checks, lineage or scope changed")


if __name__ == "__main__":
    print(json.dumps(build_certificate(), indent=2, sort_keys=True))
