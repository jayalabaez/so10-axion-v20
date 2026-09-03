"""F103: normal-frame covariance is stronger than a frozen finite phase test.

This audits the unchanged independent normal symmetry with neutral numerical
couplings. It neither rejects every frame-fixed local model nor installs a
charged tensor, correlated quotient, localized representation or QK vacuum.
"""
from __future__ import annotations

import copy
from functools import lru_cache
from itertools import product
import json
from pathlib import Path

import sympy as sp

import v102_driver_mass_background_audit as previous
import v95_wall_symmetry_lift_audit as geometry

ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v102_route": ("SUSY_V102_CUBIC_EXCLUSION_COMMON_TENSOR_TARGET_AUDIT.json", "3d3f664328d8e92b069ff75f2f9599287e65703fa37c565e998351e07ea6e79e"),
    "v102_master": ("SUSY_V102_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json", "6c9421c299c4e8976a62a1ba50382e0a88d7ac4c8f289a18b94811d46aff88e5"),
}
DRIVER_CORE = "afc65cd55881b5ce6570926d38ef4b2268ee8541f9e69c40be72410288b67855"
FINITE_CORE = "156b8c4965b70a82660f3e18cdd79e69b7e9b8bf8005d52c6bd24bbb2c55b526"
canonical_sha, file_sha, mj = previous.canonical_sha, previous.file_sha, previous.mj
ZERO_NORMAL_BULK_SCALARS = ("Phi_+", "Phi_-", "B0", "A0", "H_uA", "H_uB", "H_dC", "S2", "S4", "S6")
D_GEOM = (1, 1, 0, 0, 0, 0, 0)
KERNEL_GENERATORS = (D_GEOM, (1, 0, 1, 1, 1, 1, 0), (0, 0, 1, 0, 0, 0, 1))


def load_inputs():
    current = {k: previous.previous.common.load_bound(ROOT/name, core) for k, (name, core) in PARENTS.items()}
    route, master = current["v102_route"], current["v102_master"]
    if master["input_core_hashes"]["v102_route"] != PARENTS["v102_route"][1] or master["next_required_action"]["id"] != "F103_HIGHER_SECTION_HEIGHT_ATLAS_AND_GLOBAL_QUANTUM_VACUUM_COMPLETION":
        raise RuntimeError("V102 lineage or F103 obligation changed")
    pins = {}
    for report, base in ((route, "susy_v102_cubic_exclusion_common_tensor_target_audit"), (master, "susy_v102_multipath_g1_frontier_master_audit")):
        for name, key in ((base+".py", "generator_sha256"), ("test_"+base+".py", "test_sha256")):
            pins[name] = report["artifact_hashes"][key]
    for key, core, base in (("driver_mass_background", DRIVER_CORE, "v102_driver_mass_background_audit"),
                            ("finite_VEV_stabilizer", FINITE_CORE, "v102_full_vev_finite_stabilizer_audit")):
        if route[key].get("core_sha256") != core or canonical_sha(route[key]) != core:
            raise RuntimeError("frozen F102 helper changed: "+key)
        for name in (base+".py", "test_"+base+".py"):
            pins[name] = route["artifact_hashes"][name]
    for name, expected in pins.items():
        if file_sha(ROOT/name) != expected:
            raise RuntimeError("F102 source/test changed: "+name)
    old = previous.load_inputs()  # Fresh V101, V95 kernel/theta, V93 tensors, V92 projectors, V90/V70 action.
    kernel = old["v95_route"]["wall_symmetry_lift"]["geometric_kernel"]
    if kernel["generators"]["D"] != list(D_GEOM) or kernel["generators"]["krot_T"] != list(KERNEL_GENERATORS[1]) or kernel["generators"]["kspin"] != list(KERNEL_GENERATORS[2]):
        raise RuntimeError("the literal geometric pullback kernel changed")
    theta = old["v95_route"]["wall_symmetry_lift"]["N1_charge_bookkeeping"]
    if (theta["theta_normal_charge"], theta["theta_R_Cartan_weight"]) != ("1/2", 1):
        raise RuntimeError("the selected normal/R superspace branch changed")
    current.update(old)
    current["f103_source_bindings"] = pins
    current["f102_driver"] = route["driver_mass_background"]
    return current


def spin2_weight(q_normal):
    if isinstance(q_normal, (bool, float)):
        raise ValueError("an exact half-integral normal charge is required")
    q = sp.sympify(q_normal)
    if q.is_Rational is not True or (2*q).is_Integer is not True:
        raise ValueError("an exact half-integral normal charge is required")
    return int(2*q)


def kernel_character(q_normal, tangent_bit, internal=(0, 0, 0, 0, 0)):
    if type(tangent_bit) is not int or tangent_bit not in (0, 1) or len(internal) != 5 or any(type(v) is not int or v not in (0, 1) for v in internal):
        raise ValueError("one tangent bit and five exact internal center bits are required")
    character = [tangent_bit, spin2_weight(q_normal) % 2, *internal]
    return [sum(a*b for a, b in zip(character, gen)) % 2 for gen in KERNEL_GENERATORS]


def normal_registry():
    values = {name: sp.Integer(0) for name in ZERO_NORMAL_BULK_SCALARS}
    values["H_dSigma"] = sp.Integer(1)
    return {name: values.get(name, sp.Symbol("q_"+name.replace("+", "plus").replace("-", "minus"))) for name in previous.FIELD_NAMES}


def normal_equations(network):
    values = normal_registry()
    return [(row["id"], sp.expand(previous.line_sum(row["factors"], values)-(1 if row["operator_kind"] == "superpotential" else 0)))
            for row in network if row["include_in_constant_tensor_system"]]


def geometric_descent(p):
    gamma = geometry.clifford_generators()
    tangent = (gamma[0]*gamma[1])**2
    normal = (gamma[4]*gamma[5])**2
    checks = {"both_2pi_lifts_minus_identity": tangent == normal == -sp.eye(8),
              "D_geom_is_literal_identity_in_Spin6": tangent*normal == sp.eye(8),
              "theta_descends": kernel_character(sp.Rational(1, 2), 1, (0, 1, 0, 0, 0)) == [0, 0, 0],
              "independent_internal_bits_never_repair_half_normal_scalar_D": all(kernel_character(sp.Rational(1, 2), 0, bits)[0] == 1 for bits in product((0, 1), repeat=5))}
    if not all(checks.values()):
        raise RuntimeError("normal/tangent kernel derivation failed")
    return {
        "coordinate_order": ["T4", "N2", "Spin11", "R", "H3", "H267", "k4"],
        "kernel_generators_D_KT_KS": [list(g) for g in KERNEL_GENERATORS], "checks": checks,
        "normalization": "N is the normal SO(2) line, x=c1(N); a Spin(2) character has integer weight k=2*qN. A 2pi normal rotation is the central minus element of Spin(2).",
        "scalar_necessary_rule": "D_geom acts by (-1)^(2*qN) on a Lorentz scalar, so qN must be an integer in the unchanged pullback category.",
        "fermion_necessary_rule": "For the chosen N1 branch qN(psi)=qN(phi)-1/2. The Weyl tangent minus sign gives the same D exponent; an integral-charge scalar has a half-odd-integral-charge fermion.",
        "theta_normal_R_charges": ["1/2", 1], "superpotential_normal_R_charges": [1, 2],
        "independent_internal_factors_have_trivial_D_action": True,
        "center_screen_constructs_full_localized_representation": False,
        "full_kernel_source_core": p["v95_route"]["wall_symmetry_lift"]["core_sha256"],
    }


def pure_normal_tensor_audit(p, network):
    values = normal_registry()
    variables = [values[k] for k in previous.FIELD_NAMES if values[k].is_Symbol]
    equations = normal_equations(network)
    M, rhs = sp.linear_eq_to_matrix([e for _, e in equations], variables)
    reduced = [e for label, e in equations if not label.startswith("V93_")]
    solved = list(sp.linsolve(reduced, variables))
    if len(solved) != 1 or M.shape != (18, 11) or (M.rank(), M.row_join(rhs).rank()) != (10, 11):
        raise RuntimeError("the complete normal tensor obstruction changed")
    rows = []
    for row in network:
        target = 1 if row["operator_kind"] == "superpotential" else 0
        product_charge = previous.line_sum(row["factors"], values)
        rows.append({"id": row["id"], "factors": row["factors"], "operator_kind": row["operator_kind"],
                     "included_in_frozen_action_screen": row["include_in_constant_tensor_system"],
                     "normal_field_product_charge": str(product_charge), "normal_target_charge": target,
                     "required_coefficient_normal_charge": str(sp.expand(target-product_charge))})
    direct = [row for row in rows if row["id"].startswith("V93_")]
    if any(row["normal_field_product_charge"] != "0" or row["required_coefficient_normal_charge"] != "1" for row in direct):
        raise RuntimeError("the direct singlet mass tensor obstruction changed")
    return {
        "scope": "Unchanged independent continuous normal frame symmetry; actual hyperscalar normal charges; fixed numerical coefficients neutral under that symmetry; the selected N1 measure with qN(W)=1. The uniform-family algebra below is separate from the more general family theorem.",
        "known_bulk_scalar_normal_charges": {k: int(values[k]) for k in (*ZERO_NORMAL_BULK_SCALARS, "H_dSigma")},
        "unknown_localized_scalar_charge_names": [str(v) for v in variables],
        "all_22_source_tensor_rows": rows, "allowed_equation_order": [label for label, _ in equations],
        "allowed_normal_equations": [str(e) for _, e in equations],
        "integer_coefficient_matrix": [[int(z) for z in row] for row in M.tolist()], "integer_rhs": [int(z) for z in rhs],
        "number_of_equations": M.rows, "number_of_unknowns": M.cols,
        "matrix_rank": M.rank(), "augmented_rank": M.row_join(rhs).rank(),
        "all_written_constant_tensors_covariant_under_independent_normal": False,
        "two_direct_V93_obstructions": direct,
        "V93_arbitrary_family_lambda_and_kappa_must_vanish_with_neutral_coefficients": True,
        "nonzero_V93_nine_mode_mass_extension_under_this_symmetry": False,
        "dropping_only_V93_mass_rows_rational_solution": {str(v): str(z) for v, z in zip(variables, solved[0])},
        "uniform_10_5bar_1_normal_charges_without_V93_rows": ["1/2", "1/2", "1/2"],
        "uniform_matter_solution_descends_through_D": False,
        "X_normal_charge_is_not_fixed_before_a_chosen_VEV_reduction": True,
        "bulk_derivative_and_GM_rows_have_zero_residual": [label for label, e in equations if e == 0],
        "normal_carrying_density_derivative_or_coefficient_was_silently_added": False,
    }


def symmetric_texture(weights, target=1):
    if not weights or any(type(q) is not int for q in weights) or type(target) is not int:
        raise ValueError("nonempty integral normal weights and an integral target are required")
    n = len(weights)
    Y = sp.zeros(n)
    for i in range(n):
        for j in range(i, n):
            if weights[i]+weights[j] == target:
                Y[i, j] = Y[j, i] = sp.Symbol("y"+str(i)+"_"+str(j))
    return Y


def family_yukawa_audit(p):
    repair = p["v90"]["charged_neutral_and_compensator_repair"]
    registry = repair["operator_charge_registry"]
    if (registry["10"]["U1_X"], registry["H_uA"]["U1_X"], registry["10"]["U1_8"], registry["H_uA"]["U1_8"]) != (-1, 2, -3, 6):
        raise RuntimeError("the actual U(5) up tensor changed")
    component_rows = repair["visible_zero_mode_conditional_shadow"]["signed_component_rows"]
    family_components = [row for row in component_rows if row["field"] in ("Q", "u_c", "e_c")]
    action = {row["field"]: row for row in repair["continuous_charge_table"]}
    if len(family_components) != 3 or any(row["copies"] != 3 or row["X"] != -1 for row in family_components) or (action["D"]["U5_X_representation"], action["Dbar"]["U5_X_representation"]) != ("5_+2", "5bar_-2"):
        raise RuntimeError("the actual three 10 multiplicities or mediator representation changed")
    weights = [0, 1, 0]
    Y = symmetric_texture(weights)
    Q = sp.diag(*weights)
    if Q.T*Y+Y*Q != Y or Y.rank() != 2 or Y.det() != 0:
        raise RuntimeError("the nonuniversal rank-two counterexample changed")
    four = symmetric_texture([0, 1, 0, 1]).subs({sp.Symbol("y0_1"): 1, sp.Symbol("y0_3"): 0, sp.Symbol("y1_2"): 0, sp.Symbol("y2_3"): 1})
    if four.det() != 1:
        raise RuntimeError("the even-family exception must remain explicit")
    allzero = symmetric_texture([0, 0, 0])
    return {
        "U5_tensor": "epsilon_abcde 10_i^(ab) 10_j^(cd) H_uA^e; U1_X charges -1-1+2=0 and continuous U1_8 charges -3-3+6=0",
        "family_tensor_is_symmetric": True,
        "bound_three_family_component_rows": copy.deepcopy(family_components),
        "symmetry_proof": "Interchanging the two antisymmetric index pairs in epsilon is four transpositions, hence even; commuting chiral superfields leave a symmetric family tensor.",
        "normal_generator": "Any compact normal U(1) representation can be diagonalized on the three identical U(5) 10 multiplicities. D requires every scalar weight q_i in Z; no common-family-weight assumption is needed.",
        "covariance_equation": "Q^T Y+Y Q=Y, equivalently Y_ij!=0 only if q_i+q_j=1",
        "invertible_determinant_condition": "2 Tr(Q)=3; equivalently det(E10)^2 has normal weight 3",
        "general_odd_family_theorem": "For n odd and an odd target c, an invertible bilinear would require 2 sum(q_i)=n*c, impossible for integral weights. With symmetric Y, q pairs only with c-q and no integral fixed weight exists; Y is a direct sum of off-diagonal blocks [0 A; A^T 0], so its rank is even.",
        "three_family_maximum_rank": 2,
        "nonuniversal_witness": {"scalar_normal_weights": weights, "matrix": mj(Y), "rank": Y.rank(), "determinant": str(Y.det()), "covariance_residual": mj(Q.T*Y+Y*Q-Y)},
        "uniform_zero_normal_weight_matrix": mj(allzero),
        "even_family_scope_counterexample": {"weights": [0, 1, 0, 1], "matrix": mj(four), "determinant": int(four.det()), "new_family_installed": False},
        "half_normal_formal_diagonal_exception": {"weights": ["1/2"]*3, "matrix": mj(sp.eye(3)), "D_exponents_of_scalars_and_fermions": [1, 1], "valid_unchanged_representation": False},
        "given_three_family_U5_sector_assumed_not_mixed_with_new_10s": True,
        "normal_generator_commutes_with_the_written_U5_wall_representation": True,
        "independently_reassigning_SM_Q_and_u_c_normals_without_a_common_U5_10_is_this_same_ansatz": False,
        "existing_D_Dbar_are_5_and_5bar_not_additional_10s": True,
        "full_KK_or_nonlocal_mass_matrix_rank_bounded_by_this_theorem": False,
        "all_compactifications_or_higher_dimensional_repairs_excluded": False,
        "source_up_Yukawa_was_already_a_proved_nondegenerate_tensor": False,
    }


def full_mass_coefficient_lines(p):
    h = previous.previous
    x, r, d, ep, em, e2, e4, e6 = h.x, h.r, h.d, h.ep, h.em, h.e2, h.e4, h.e6
    W = x+2*r
    scalars = {"Phi_+": h.scalar_line(r, ep, d, 8, "plus"), "Phi_-": h.scalar_line(r, em, d, 8, "minus"),
               "S2": h.scalar_line(r, e2, d, 2, "plus"), "S4": h.scalar_line(r, e4, d, 4, "plus"), "S6": h.scalar_line(r, e6, d, 6, "plus")}
    coeff = {"lambda": sp.expand(W-scalars["Phi_-"]-scalars["S2"]-scalars["S6"]),
             "kappa": sp.expand(W-scalars["Phi_-"]-2*scalars["S4"])}
    expected = {"lambda": x-r+em-e2-e6, "kappa": x-r+em-2*e4}
    if any(sp.expand(coeff[k]-expected[k]) != 0 for k in coeff):
        raise RuntimeError("a required normal/R/flavor curvature was omitted")
    roots = h.profile_roots("selected_mass_tensor_compensation")
    cp3 = {x: 1, r: sp.Rational(1, 2), d: 1, ep: roots["Phi_plus"], em: roots["Phi_minus"], e2: roots["S2"], e4: roots["S4"], e6: roots["S6"]}
    cp3_values = {k: sp.expand(v.subs(cp3)) for k, v in coeff.items()}
    pure_normal = {r: 0, d: 0, ep: 0, em: 0, e2: 0, e4: 0, e6: 0}
    if list(cp3_values.values()) != [0, 0] or any(sp.expand(v.subs(pure_normal)) != x for v in coeff.values()):
        raise RuntimeError("the restricted witness and independent-normal contrast changed")
    selected = {row["name"]: row for row in p["saved_higgs"]["actual_selected_scalar_weights"]}
    finite_rows = []
    for name, factors in (("lambda", ("Phi_minus", "S2", "S6")), ("kappa", ("Phi_minus", "S4", "S4"))):
        R_product = sp.prod(sp.sympify(selected[f]["scalar_Rtilde_phase"]) for f in factors)
        phase_products = {stratum: sp.prod(sp.sympify(selected[f]["strata"][stratum]["phase"]) for f in factors) for stratum in ("z00", "z11", "z10", "z01")}
        if R_product != -1 or any(v != 1 for v in phase_products.values()):
            raise RuntimeError("the finite saved mass tensor no longer passes")
        finite_rows.append({"tensor": name, "scalar_Rtilde_product": str(R_product), "W_Rtilde_phase": "-1",
                            "all_four_frozen_stratum_products": {k: str(v) for k, v in phase_products.items()}, "theta_frozen_orbifold_phase": "1", "W_frozen_orbifold_phase": "1"})
    coupled = {ep: -r-4*d, em: r-4*d, e4: x/2-2*d, e6: x-4*d-e2}
    if any(sp.expand(v.subs(coupled, simultaneous=True)) != 0 for v in (scalars["Phi_+"], scalars["Phi_-"], *coeff.values())):
        raise RuntimeError("the exact formal locking equations changed")
    return {
        "formal_root_order": [str(z) for z in (x, r, d, ep, em, e2, e4, e6)],
        "scalar_lines": {k: str(v) for k, v in scalars.items()}, "superpotential_line": str(W),
        "required_coefficient_line_c1": {k: str(v) for k, v in coeff.items()},
        "pure_normal_restriction": {k: str(v.subs(pure_normal)) for k, v in coeff.items()},
        "independent_R_coefficient_weight": -1,
        "R_and_all_flavor_curvatures_retained": True,
        "formal_Phi_VEV_and_mass_tensor_locking": {str(k): str(v) for k, v in coupled.items()},
        "locking_scope": "Necessary Cartan curvature/character equations after selecting the actual component lines. Division by two retains an integral root/torsion obligation; this is not a complete full nonabelian representation or global G-structure construction.",
        "frozen_CP3_selected_roots": {str(k): str(v) for k, v in cp3.items()},
        "CP3_both_coefficient_degrees": {k: int(v) for k, v in cp3_values.items()},
        "finite_original_mass_tensor_checks": finite_rows,
        "pure_normal_quarter_rotation_coefficient_phase": "I", "necessary_compensating_internal_quarter_phase": "-I",
        "pure_normal_line_alone_preserves_saved_combined_orbifold_twist": False,
        "neutral_coefficients_in_fixed_combined_chart_imply_independent_normal_covariance": False,
        "coefficient_line_is_a_new_installed_field": False,
    }


def restricted_and_frame_alternatives(p, network):
    cp3 = {k: sp.Integer(v) for k, v in p["f102_driver"]["CP3_common_tensor_witness_k0"]["selected_component_degrees"].items()}
    residuals = [sp.expand(previous.line_sum(row["factors"], cp3)-(2 if row["operator_kind"] == "superpotential" else 0)) for row in network if row["include_in_constant_tensor_system"]]
    if any(v != 0 for v in residuals):
        raise RuntimeError("the frozen restricted positive tensor witness changed")
    values = {k: sp.Integer(0) for k in previous.FIELD_NAMES}
    for k in ("S8", "SB", "SX", "P_A", "Dbar", "H_dSigma"):
        values[k] = sp.Integer(1)
    required = [{"id": row["id"], "coefficient_qN": int(sp.expand((1 if row["operator_kind"] == "superpotential" else 0)-previous.line_sum(row["factors"], values)))}
                for row in network if row["include_in_constant_tensor_system"]]
    charged = [r for r in required if r["coefficient_qN"]]
    if len(charged) != 7 or any(r["coefficient_qN"] != 1 for r in charged):
        raise RuntimeError("the illustrative all-integral normal assignment price changed")
    return {
        "positive_restricted_character_witness": {"source": "V102 CP3 common tensor k=0 witness", "field_degrees": {k: int(v) for k, v in cp3.items()},
            "theta_degree": 1, "W_degree": 2, "all_18_tensor_residuals": [int(v) for v in residuals],
            "up_identity_3_by_3_covariance": "2*1+0=2", "V93_lambda_kappa_identity_covariance": "0+1+1=2",
            "same_scalar_normal_charges_reassigned_by_this_witness": False,
            "interpretation": "These are combined normal/R/flavor/gauge cocharacter weights, not pure normal charges. The closed endpoint and old bulk matrices are preserved as in V102, but the missing localized full representations and nonlinear background are not supplied by this calculation.",
            "full_independent_normal_representation_constructed": False, "full_physical_CP3_background_accepted": False},
        "all_integral_pure_normal_assignment_with_explicit_tensor_price": {"scalar_normal_charges": {k: int(v) for k, v in values.items()}, "all_18_required_coefficient_charges": required,
            "seven_normal_charged_tensor_rows": charged, "new_coefficients_or_fields_installed": False,
            "scope": "At normal-charge level one may assign integral scalar charges and expose all seven required coefficient charges instead of choosing forbidden half-normal matter scalars. Their different R/flavor and finite characters must still be completed; a common bare N-valued number is not a full solution."},
        "frame_patch": "On a chosen trivialized normal bundle the saved 4D polynomial can be used as a frame-fixed component algebra. With its numerical coefficients held fixed it is not invariant under arbitrary local independent normal rotations. Promoting coefficients to transforming sections or restricting the background structure is extra action data, not a contradiction in the earlier finite character arithmetic.",
        "global_normal_tensor": "A nowhere-zero section of a genuine charge-one normal line trivializes that entire line, including torsion. A chosen frame does not exist on arbitrary N. If the coefficient includes internal factors, the whole combined coefficient line, not N alone, must be trivialized.",
        "CP3_uncompensated_normal_line": "For N=O(1), a nowhere-zero section is impossible; the inherited combined coefficient lines instead have degree zero after flavor retuning. This does not by itself prove they extend to a full physical background.",
        "possible_explicit_redesigns_not_adopted": ["normal-index-carrying covariant localized density/derivative or background tensor", "diagonal normal/internal G-structure with an explicit global lift and all old representations", "different higher-dimensional operators or mediator content with a recomputed vacuum and anomaly ledger"],
        "UV_zero_loci_and_relative_anomaly_matching_remain": True,
        "unrestricted_curvatures_can_be_discarded_before_pulling_back_full_anomaly": False,
        "new_quotient_spurion_or_full_vacuum_installed": False,
    }


@lru_cache(maxsize=2)
def pure_json(input_json):
    p = json.loads(input_json)
    network = previous.coupling_network(p)
    if network != p["f102_driver"]["source_bound_operator_network"]:
        raise RuntimeError("the full inherited tensor ledger changed")
    return json.dumps({"geometric_normal_descent": geometric_descent(p),
                       "independent_normal_tensor_system": pure_normal_tensor_audit(p, network),
                       "three_family_up_Yukawa_obstruction": family_yukawa_audit(p),
                       "mass_tensor_full_curvature_and_finite_checks": full_mass_coefficient_lines(p),
                       "restricted_witness_and_redesign_boundary": restricted_and_frame_alternatives(p, network)}, sort_keys=True, separators=(",", ":"))


def build_certificate():
    p = load_inputs()
    out = {
        "schema": "v103_independent_normal_frame_tensor_and_family_descent_audit_v1",
        "status": "EXACT_INDEPENDENT_NORMAL_TENSOR_OBSTRUCTION__FINITE_AND_RESTRICTED_WITNESSES_PRESERVED__NO_FULL_ACTION",
        "input_core_hashes": {k: v[1] for k, v in PARENTS.items()},
        "bound_helper_cores": {"v102_driver": DRIVER_CORE, "v102_finite": FINITE_CORE, "v101_Higgs": p["saved_higgs"]["core_sha256"], "v95_kernel_theta": p["v95_route"]["wall_symmetry_lift"]["core_sha256"]},
        "fresh_parent_source_bindings": p["f103_source_bindings"],
        **json.loads(pure_json(json.dumps(p, sort_keys=True, separators=(",", ":")))),
        "source_and_assumption_boundary": {
            "frozen_sources_explicitly_build_finite_combined_orbifold_lifts": True,
            "frozen_sources_complete_continuous_localized_normal_tensor_representations": False,
            "geometric_requirement": "The remnant continuous local normal SO(2) survives at a fixed point of a codimension-two orbifold in the ambient gravitational theory. Extending to arbitrary such backgrounds therefore requires covariance beyond the saved finite combined twist.",
            "assumptions_for_obstruction": ["the unchanged geometric pullback containing literal D_geom", "independent normal transformations rather than an unconstructed diagonal restriction", "the selected theta branch with normal charge 1/2", "actual bulk hyperscalar normal charge zero and Sigma normal charge one", "neutral numerical coefficients and no additional normal-carrying wall density"],
            "no_go_applies_to_every_possible_compactification": False,
            "finite_or_frame_fixed_local_mass_rank_calculations_retracted": False,
            "normal_frame_covariance_equivalent_to_anomaly_cancellation": False,
        },
        "terminal_decision": {"unchanged_independent_normal_extension_with_all_neutral_written_tensors_exists": False,
            "nondegenerate_three_family_constant_up_tensor_in_this_normal_ansatz_exists": False,
            "bounded_normal_representation_obstruction_derived": True,
            "full_localized_Gammahat_representations_constructed": False, "nonlinear_QK_SUSY_vacuum_constructed": False,
            "full_relative_quantum_anomaly_cancelled": False, "same_action_microscopic_parent_accepted": False,
            "theory_complete": False, "closed_gates": []},
        "primary_sources": [
            {"url": "https://arxiv.org/pdf/hep-th/0612212", "use": "Sections 3.2-3.3 retain local SO(4) and normal SO(2) at the fixed locus and distinguish finite boundary conditions from gravitational covariance. Section 5.1 gives the half-angle R twist preserving N1. The present kernel and Yukawa obstruction are independently derived, not claimed as that paper's model."},
            {"url": "https://arxiv.org/pdf/hep-th/0602155", "use": "The bulk N1 hyper action and equations (44)-(45) give the derivative/Sigma normal character and the paired finite hyper twists. They do not install the missing covariant localized tensor density."},
            {"url": "https://web.math.ucsb.edu/~dai/book.pdf", "use": "Sections 1.3 and 2.1 give the Clifford spin lift, Spin(2) square map and cocycle requirement. The actual D_geom identity and representation descent conditions are checked explicitly here."},
            {"url": "https://arxiv.org/pdf/2009.04692", "use": "Section 4 distinguishes a fixed nonzero mass/Higgs reduction from ultraviolet configurations with zeros; the proposed tensor reductions here do not remove ultraviolet anomaly obligations."},
        ],
    }
    out["core_sha256"] = canonical_sha(out)
    return out


def validate_certificate(value):
    if value.get("core_sha256") != canonical_sha(value) or value != build_certificate():
        raise RuntimeError("F103 normal tensor, family rank, parent source or scope changed")


if __name__ == "__main__":
    print(json.dumps(build_certificate(), indent=2, sort_keys=True))
