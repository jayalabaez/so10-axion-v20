"""F96 ordinary spin eta-CS levels versus an equivariant transport candidate.

Integer-level spin eta-CS is constructed only in the stated ordinary product
spin category.  Fractional independent edges fail there.  A torus root phase
and a virtual shifted determinant reproduce the desired equivariant profile,
but neither supplies the missing quantum orbifold gluing or a same-action
supersymmetric sector.  In particular all induced normal terms are retained.
"""
from __future__ import annotations

import copy
from functools import lru_cache
import hashlib
from itertools import product
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v95_route": ("SUSY_V95_WALL_KERNEL_FINITE_INFLOW_RANK_AUDIT.json", "e8ed3aa98cc23726cd41d0b62bbfb8822253d7a9282f1184ba22a77956cb4729"),
    "v95_master": ("SUSY_V95_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json", "7a20530db05af160ce76e1b5e297001befc5eafd3696a13ba9ac692bbe94dd88"),
    "v94_route": ("SUSY_V94_BOUNDARY_DEFECTS_AND_MW_DESCENT_AUDIT.json", "17fd3a60008545b7bde77756ed8b5ec7dd590c18c1cbb1344a5a7cc67dd2686f"),
    "v91": ("SUSY_V91_SPINC_QUANTIZATION_TENSOR_CONE_FINITE_TORSION_AUDIT.json", "4a581af0dd4cfc6fd3f66ef1e3ea2801b9770c67822d984a02deb602865c0322"),
    "v71": ("SUSY_V71_SPIN11_NORMAL_BUNDLE_EQUIVARIANT_GS_AUDIT.json", "0162828ebd2b1e28d4fcbcf4ea1e6c61178d305cec79abd6d36a55719bb0f1ea"),
    "v70": ("SUSY_V70_SPIN11_LOCALIZED_PARENT_SPIN_FLAVOR_COMPLETION_AUDIT.json", "3e7b8e53916fbbc05bdcdf9632bcf4359aa4888b037df775c37d8d7d2551b228"),
}
LOCAL_CORE = "fcecfcfe68e40050682562b7536a1a1c2c47e350b9794cc60f9fd2923e992b5d"
f, p, x, c = sp.symbols("f p x c")
X, Y, t = sp.symbols("X Y t")
ZETA = (1+sp.I)/sp.sqrt(2)
J = sp.Matrix([[0, 1], [-1, 0]])


def canonical_sha(value):
    body = copy.deepcopy(value)
    body.pop("core_sha256", None)
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def matrix_json(value):
    return [[str(sp.simplify(v)) for v in row] for row in value.tolist()]


def clean(value):
    return value.applyfunc(sp.simplify)


def load_parents():
    reports = {}
    for key, (name, expected) in PARENTS.items():
        report = json.loads((ROOT/name).read_text(encoding="utf-8"))
        if report.get("core_sha256") != expected or canonical_sha(report) != expected:
            raise RuntimeError("changed or noncanonical F96 transport parent: " + key)
        reports[key] = report
    if reports["v95_master"]["input_core_hashes"]["v95_route"] != PARENTS["v95_route"][1]:
        raise RuntimeError("V95 master-to-route edge changed")
    if reports["v95_master"]["next_required_action"]["id"] != "F96_QUANTIZED_RELATIVE_INFLOW_AND_ORIGINAL_MW_GENERATOR":
        raise RuntimeError("F96 obligation changed")
    local = reports["v95_route"]["local_U1_inflow_lattice"]
    if local.get("core_sha256") != LOCAL_CORE or canonical_sha(local) != LOCAL_CORE:
        raise RuntimeError("V95 local U1 profile changed")
    if local["formal_zero_sum_inflow_target"]["signed_localized_source_weights"] != ["1/4", "1/4", "-1/2"]:
        raise RuntimeError("transport source coefficients changed")
    if reports["v91"]["old_quotient_obstruction"]["group"] != "H=Spin^c(11)=(Spin(11) x U1)/<(z,-1)>":
        raise RuntimeError("physical gauge quotient changed")
    if reports["v70"]["lorentz_SU2R_and_N1_superfield_lift"]["geometry"] != "square T2/Z4, phi=pi/2":
        raise RuntimeError("square torus geometry changed")
    return reports


def weyl_index(q, root=f):
    q = sp.Rational(q)
    return q**3*root**3/6-q*root*p/24


def cp3_period(poly):
    """Ordinary spin CP3, f=H, p1=4H^2, integral H^3=1."""
    h = sp.Symbol("H")
    return sp.expand(poly.subs({f: h, p: 4*h*h})).coeff(h, 3)


def phase_label(value):
    value = sp.Rational(value) % 1
    return {sp.Integer(0): "+1", sp.Rational(1, 4): "+i", sp.Rational(1, 2): "-1", sp.Rational(3, 4): "-i"}.get(value, "exp(2*pi*i*"+str(value)+")")


def ordinary_eta_cs_certificate():
    index = weyl_index(2)
    determinant_index = weyl_index(1, c)
    if sp.expand(index.subs(f, c/2)-determinant_index) != 0 or cp3_period(index) != 1:
        raise RuntimeError("charge-two index is not the primitive determinant-line index")
    levels = [sp.Rational(1, 4), sp.Rational(1, 4), -sp.Rational(1, 2)]
    return {
        "gauge_group": "Spin^c(11) is a GAUGE quotient; tangent bundles remain independently ordinary spin",
        "physical_line": "D=det(gauge Spin^c11), c1(D)=c=2f; (g,z) acts on D by z^2",
        "charge_two_singlet_is_a_genuine_gauge_representation": True,
        "charge_one_gauge_singlet_is_a_genuine_representation": False,
        "J2": str(index), "J2_in_integral_determinant_class": str(determinant_index),
        "closed_spin6_integrality": "integral J2 = index(D_spin tensor D) in Z by the ordinary twisted spin index theorem",
        "spin_CS_definition_on_closed_Y5": "Z_k(Y5,D)=exp(2*pi*i*k*xi(D_Y5 tensor D)), xi=(eta+h)/2, k in Z; the sign is the chosen positive inflow convention",
        "bounding_formula": "Z_k=exp(2*pi*i*k*integral_W6 J2); APS relates this to eta and makes the integer-level expression independent of fillings",
        "nonbounding_definition_uses_eta_not_an_assumption_of_bounding": True,
        "on_boundaries_value_is_a_relative_determinant_line_element": True,
        "ordinary_integer_level_refinement_exists": True,
        "necessary_and_sufficient_levels_in_the_one_parameter_J2_family": "integers",
        "necessity_scope": "standalone ordinary spin eta-CS with precisely k*J2 curvature on arbitrary allowed gauge bundles, without additional boundary or topological data",
        "primitive_witness": {"manifold": "CP3", "c1_tangent": "4H", "p1": "4H^2", "covering_line": "L=O(1)", "determinant_line": "D=L^2=O(2)", "Spin11_bundle": "trivial", "spin": True, "period_J2": "1", "gauge_quotient_admissible": True},
        "requested_levels": [{"level": str(k), "CP3_extension_ambiguity": str(k), "ambiguity_phase": phase_label(k), "ordinary_independent_edge_quantized": k.q == 1} for k in levels],
        "sum_of_three_ambiguities": str(sum(levels)),
        "zero_sum_makes_independent_fillings_unambiguous": False,
        "reason": "An independent edge filling can be changed by a disjoint closed CP3 without changing the others. Correlating fillings is additional relative data, not ordinary independent edge CS.",
        "same_test_is_the_F95_defect_lens_phase": False,
        "half_or_quarter_eta_power_has_a_canonical_local_refinement_from_this_data": False,
        "all_equivariant_or_relative_fractional_inflow_excluded": False,
        "full_Gammahat_spin_refinement_constructed": False,
    }


def graph_transport_certificate(normal):
    strata = normal["normal_root_isotropy"]["strata"]
    orders = [strata[k]["effective_order"] for k in ("z00", "z11", "z10", "z01")]
    if orders != [4, 4, 2, 2]:
        raise RuntimeError("frozen stabilizer orders changed")
    # One quotient edge from the physical C2 orbit to each C4 point. A free
    # edge orbit has four lifts. At a fixed endpoint each lift contributes.
    cover_boundary = sp.Matrix([[4, 0], [0, 4], [-2, -2], [-2, -2]])
    quotient_push = sp.Matrix([[sp.Rational(1, 4), 0, 0, 0], [0, sp.Rational(1, 4), 0, 0], [0, 0, sp.Rational(1, 4), sp.Rational(1, 4)]])
    quotient_boundary = quotient_push*cover_boundary
    target_cover = sp.Matrix([1, 1, -1, -1])
    target = sp.Matrix([sp.Rational(1, 4), sp.Rational(1, 4), -sp.Rational(1, 2)])
    if quotient_push*target_cover != target or quotient_boundary != sp.Matrix([[1, 0], [0, 1], [-1, -1]]):
        raise RuntimeError("cover degree or physical C2 orbit normalization changed")
    return {
        "physical_vertices": ["z00", "z11", "physical_C2_orbit"], "cover_points": ["z00", "z11", "z10", "z01"],
        "generic_cover_degree": 4, "effective_stabilizer_orders_on_cover": orders,
        "cover_integer_source_divisor": [int(v) for v in target_cover], "quotient_source_coefficients": [str(v) for v in target],
        "quotient_push_matrix": matrix_json(quotient_push), "free_edge_orbit_boundary_on_cover": matrix_json(cover_boundary),
        "ordinary_quotient_edge_incidence": matrix_json(quotient_boundary),
        "required_levels_on_two_reference_edges": ["1/4", "1/4"],
        "integer_free_edge_orbits_generate_requested_divisor": False,
        "minimal_multiple_of_target_in_integer_edge_boundary_lattice": 4,
        "fourfold_target_integer_edge_levels": [1, 1],
        "fourfold_target_cover_boundary": [4, 4, -4, -4],
        "proof_for_any_equivariant_subdivision": "All nontrivial rotations of the square torus have isolated fixed points. Choose an equivariant cell subdivision with free open edges. A four-edge orbit contributes a multiple4 at a C4 endpoint and a multiple2 at each C2 endpoint. After division by cover degree4 and summing the C2 orbit, every physical endpoint level is integral. Adding integer-level edges and cycles cannot change this.",
        "scope": "ordinary integer-level determinant-line eta-CS on free edge orbits, with no isotropy-dependent endpoint refinement or additional topological transport sector",
        "integer_cover_divisor_alone_proves_ordinary_quantization": False,
        "fourfold_counterterm_cancels_original_fractional_classes": False,
        "equivariant_fractional_transport_in_general_excluded": False,
    }


def torus_phase_certificate():
    F = Y**2-X**3+X
    A = {X: -X, Y: sp.I*Y}
    g = X/Y
    image_g = sp.cancel(g.subs(A, simultaneous=True))
    fourth_reduced = sp.cancel(X**4/(X**3-X)**2)
    quotient_function = t/(t-1)**2
    checks = {
        "A_preserves_curve_zero_locus": sp.expand(F.subs(A, simultaneous=True)+F) == 0,
        "g_has_character_i": sp.cancel(image_g-sp.I*g) == 0,
        "g_fourth_descends": sp.cancel(fourth_reduced-quotient_function.subs(t, X**2)) == 0,
        "quotient_t_is_invariant": sp.expand((X**2).subs(A, simultaneous=True)-X**2) == 0,
    }
    rows = [
        {"point": "z00", "curve_point": "O", "ord_X": -2, "ord_Y": -3, "ord_g": 1, "stabilizer": 4, "coarse_t": "infinity"},
        {"point": "z11", "curve_point": "P0=(0,0)", "ord_X": 2, "ord_Y": 1, "ord_g": 1, "stabilizer": 4, "coarse_t": "0"},
        {"point": "z10", "curve_point": "P+=(1,0)", "ord_X": 0, "ord_Y": 1, "ord_g": -1, "stabilizer": 2, "coarse_t": "1"},
        {"point": "z01", "curve_point": "P-=(-1,0)", "ord_X": 0, "ord_Y": 1, "ord_g": -1, "stabilizer": 2, "coarse_t": "1"},
    ]
    if not all(checks.values()) or any(r["ord_X"]-r["ord_Y"] != r["ord_g"] for r in rows):
        raise RuntimeError("exact square-torus divisor/character calculation failed")
    return {
        "curve": "E0:Y^2=X^3-X", "normalized_square_torus_uniformization": "X proportional to wp(z), Y proportional to wp'(z); scaling is irrelevant to the divisor and phase",
        "quarter_turn_A": "(X,Y)->(-X,iY), corresponding to z->i*z", "g": "X/Y", "divisor_rows": rows,
        "divisor": "O+P0-P+-P-", "cover_degree_sum": 0,
        "coarse_quotient_coordinate": "t=X^2", "coarse_quotient_map_degree": 4,
        "fourth_power_identity": "g^4=t/(t-1)^2", "checks": checks,
        "minimum_invariant_positive_power_of_g": 4,
        "g_is_an_ordinary_function_on_the_quotient": False,
        "g_is_an_explicit_equivariant_meromorphic_section": True,
        "orbifold_flat_line_character_on_A": "i",
        "local_orbifold_loop_phase_residues": {"z00": "1/4", "z11": "1/4", "physical_C2_orbit": "-1/2"},
        "connection_one_form": "beta=d(arg(g))/(2*pi) on the punctured cover; beta is A-invariant and descends with the displayed rational loop periods",
        "formal_local_descent": "S_local=2*pi*i*integral beta wedge CS5(D), dCS5=J2: delta S_local=2*pi*i*integral d(beta) wedge I4^(1), with physical source weights(1/4,1/4,-1/2)",
        "formal_local_descent_is_a_global_quantized_functional": False,
        "missing_quantum_data": "an equivariant differential/eta refinement for the order4 phase line, stabilizer corrections, and relative endpoint gluing; an ordinary quarter power of eta is not supplied by the meromorphic identity",
        "cover_degree_argument_is_not_a_no_go_against_equivariant_fractions": True,
    }


@lru_cache(maxsize=None)
def normal_kernel_series(order, power):
    if order not in (2, 4) or power not in range(1, order):
        raise ValueError("nonidentity C2/C4 kernel required")
    root = ZETA**power if order == 4 else sp.I
    denominator = [sp.simplify((root-(-1)**n/root)/(2**n*sp.factorial(n))) for n in range(4)]
    reciprocal = [sp.simplify(1/denominator[0])]
    for n in range(1, 4):
        reciprocal.append(sp.simplify(-sum(denominator[k]*reciprocal[n-k] for k in range(1, n+1))/denominator[0]))
    return reciprocal


def phase_series(order, m):
    if m not in range(order):
        raise ValueError("invalid phase")
    h = ZETA*sp.I**m if order == 4 else sp.I*(-1)**m
    return [sp.simplify(sum(h**j*normal_kernel_series(order, j)[n] for j in range(1, order))/4) for n in range(4)]


def phase_polynomial(order, m, q=2):
    a0, a1, a2, a3 = phase_series(order, m)
    return sp.expand(a0*weyl_index(q)+a1*x*((q*f)**2/2-p/24)+a2*x*x*q*f+a3*x**3)


def full_SMW_polynomial(H, Q, order):
    coefficients = {}
    for n, r, factor in ((0, 3, 1), (0, 1, -p/24), (1, 2, 1), (1, 0, -p/24), (2, 1, 1), (3, 0, 1)):
        value = sp.simplify(sum(normal_kernel_series(order, j)[n]*sp.trace(H**j*Q**r) for j in range(1, order))/(8*sp.factorial(r)))
        coefficients[(n, r)] = value*factor*x**n*f**r
    return sp.expand(sum(coefficients.values()))


def shifted_determinant_certificate(v71):
    for row in v71["spin_half_equivariant_index"]["rows"]:
        if [str(v) for v in phase_series(4, row["m"])] != row["series_coefficients_1_x_x2_x3"]:
            raise RuntimeError("normal kernel differs from bound V71")
    Q, K = sp.diag(2, -2), sp.diag(sp.I, -sp.I)
    U = -sp.eye(2)
    matrices = []
    for m in (1, 2):
        h = sp.simplify(ZETA*sp.I**m)
        H = sp.diag(h, sp.conjugate(h))
        checks = {
            "unitary": clean(H.conjugate().T*H) == sp.eye(2),
            "symplectic": clean(H.T*J*H) == J,
            "quaternionic_reality": clean(J*sp.conjugate(H)-H*J) == sp.zeros(2),
            "H_fourth_is_minus_identity": clean(H**4) == -sp.eye(2),
            "Q_symplectic": Q.T*J+J*Q == sp.zeros(2),
            "Q_commutes": H*Q == Q*H,
            "effective_U_V_translations_are_identity": U*K**2 == sp.eye(2),
            "C4_full_SMW_trace_matches_half_formula": sp.expand(full_SMW_polynomial(H, Q, 4)-phase_polynomial(4, m)) == 0,
            "C2_full_SMW_trace_matches_half_formula": sp.expand(full_SMW_polynomial(clean(H**2), Q, 2)-phase_polynomial(2, m % 2)) == 0,
        }
        plus, minus = sp.I**m, -sp.I/sp.I**m
        checks["N1_pairing_constraint"] = sp.simplify(plus*minus*sp.I) == 1
        ranks = [int(sp.simplify(sum(z**j for j in range(4))/4)) for z in (plus, minus)]
        if not all(checks.values()) or ranks != [0, 0]:
            raise RuntimeError("candidate shifted-character matrix check failed")
        matrices.append({"m": m, "H_C4": matrix_json(H), "H_C2": matrix_json(clean(H**2)), "Q": matrix_json(Q), "external_K": matrix_json(K), "flavor_U_V": matrix_json(U),
                         "plus_phase": str(plus), "minus_phase": str(minus), "constant_N1_projector_ranks": ranks,
                         "C4_I6": str(phase_polynomial(4, m)), "C2_cover_I6": str(phase_polynomial(2, m % 2)), "checks": checks})
    delta4 = sp.expand(phase_polynomial(4, 1)-phase_polynomial(4, 2))
    delta2 = sp.expand(phase_polynomial(2, 1)-phase_polynomial(2, 0))
    if sp.expand(delta4-weyl_index(2)/4+5*f*x*x/16) != 0 or sp.expand(delta2+weyl_index(2)/4-f*x*x/16) != 0:
        raise RuntimeError("full normal polynomial difference changed")
    return {
        "status": "EXACT_VIRTUAL_SHIFTED_DETERMINANT_PROFILE_NOT_A_NEW_ACCEPTED_BULK_SECTOR",
        "meaning_of_minus": "formal difference of two same-charge shifted index/Pfaffian densities; interpreting the inverse determinant as opposite6D chirality requires new matter, action and regulator data",
        "matrix_blocks": matrices, "SMW_factor": "1/2 before summing the conjugate pair", "orbifold_average_at_all_cover_points": "1/4",
        "continuous_charge_magnitude": 2,
        "unlocalized_six_dimensional_index_difference": "0: both virtual terms have the same charge representation and dimension before the equivariant twists",
        "per_physical_stratum_delta_I6": {"z00": str(delta4), "z11": str(delta4), "physical_C2_orbit": str(2*delta2)},
        "per_C2_cover_delta_I6": str(delta2),
        "pure_U1_restriction_matches_requested_transfer": True,
        "new_normal_terms": {"z00": "-5*f*x**2/16", "z11": "-5*f*x**2/16", "physical_C2_orbit": "f*x**2/8"},
        "integrated_delta_I6": str(sp.expand(2*delta4+2*delta2)),
        "integrated_pure_U1_delta_I6": str(sp.expand((2*delta4+2*delta2).subs(x, 0))),
        "new_normal_anomaly_canceled": False,
        "all_zero_mode_projectors_vanish_in_each_virtual_term": True,
        "bulk_gap_survives_a_nonconstant_mass_profile_without_defect_modes": False,
        "full_R_and_flavor_curvature_polynomial_constructed": False,
        "new_virtual_blocks_replace_the_267_hyper_spectrum": False,
        "opposite_chirality_pair_is_an_accepted_6D_N1_sector": False,
        "full_Gammahat_or_finite_7D_anomaly_trivialization_constructed": False,
    }


def smooth_mass_certificate():
    h1 = sp.diag(ZETA**3, ZETA**5)
    h2 = sp.diag(ZETA**5, ZETA**3)
    m, mbar = sp.symbols("m mbar")
    M = sp.diag(mbar, m)
    Q = sp.diag(2, -2)
    transformed = M.subs({m: sp.I*m, mbar: -sp.I*mbar}, simultaneous=True)
    checks = {
        "twist_ratio": clean(h1*h2.inv()) == sp.diag(-sp.I, sp.I),
        "mass_intertwines_two_twists": clean(transformed-h1*M*h2.inv()) == sp.zeros(2),
        "preserves_continuous_U1_charge": M*Q == Q*M,
        "SMW_quaternionic_mass_reality": J*M.subs({m: mbar, mbar: m}, simultaneous=True) == M*J,
        "translation_intertwiner_is_periodic": True,
    }
    a, b, cc, d = sp.symbols("a b cc d")
    constant = sp.Matrix([[a, b], [cc, d]])
    equations = list(constant*Q-Q*constant)+list(clean(h1*constant*h2.inv()-constant))
    solutions = sp.solve(equations, (a, b, cc, d), dict=True)
    if solutions != [{a: 0, b: 0, cc: 0, d: 0}] or not all(checks.values()):
        raise RuntimeError("constant mass obstruction or smooth profile intertwiner failed")
    return {
        "profile": "m=g/(1+|g|^2), g=X/Y on the square torus",
        "profile_quarter_turn": "m(Az)=i*m(z)", "mass_matrix": matrix_json(M),
        "mass_matrix_equivariance": "M(Az)=H_m1*M(z)*H_m2^-1", "checks": checks,
        "only_constant_charge_preserving_mass": [["0", "0"], ["0", "0"]],
        "smooth_extension_at_g_zero": "g=z*a(z), a(0)!=0: m=z*a(z)/(1+|z*a(z)|^2), so winding+1",
        "smooth_extension_at_g_pole": "v=1/g=z*a(z): m=conjugate(v)/(1+|v|^2), so winding-1",
        "cover_mass_zero_windings": {"z00": 1, "z11": 1, "z10": -1, "z01": -1},
        "cover_signed_winding_sum": 0, "smooth_on_whole_cover": True,
        "nowhere_nonzero_profile": False, "holomorphic_superpotential_mass_profile": False,
        "invariant_point_obstruction": "m=i*m at either A-fixed C4 point and m=-m at either A^2-fixed C2 point, so every continuous equivariant profile of this character vanishes at all four points",
        "mass_scale_potential_and_finite_energy_defect_solution_constructed": False,
        "projected_defect_zero_modes_and_their_Gammahat_representations_computed": False,
        "cover_winding_divided_by_four_is_automatically_a_physical_Weyl_count": False,
        "smooth_matrix_witness_is_a_quantized_relative_action": False,
    }


def equivariant_scope_certificate():
    rows = []
    for m in range(4):
        chars = [sp.I**(m*j) for j in range(4)]
        multiplicity = sp.simplify(sum(chars)/4)
        rows.append({"C4_character_weight": m, "character": [str(v) for v in chars], "identity_sector_contribution": "1/4", "nonidentity_contribution": str(sp.simplify(sum(chars[1:])/4)), "invariant_index": int(multiplicity)})
    return {
        "elementary_equivariant_index_example": rows,
        "example_scope": "a one-dimensional C4 equivariant index representation; its invariant multiplicity is integral while its identity contribution is fractional. This is not the index of a constructed new physical field.",
        "free_fourfold_cover": "a quotient ordinary spin Dirac index pulls back to four times that index; this alone cannot manufacture a quarter-level physical edge",
        "fixed_locus_warning": "orbifold eta/index formulas include nonidentity stabilizer terms. Dividing only the ordinary cover index by4 omits precisely the possible corrections under investigation",
        "ordinary_CP3_obstruction_is_full_equivariant_no_go": False,
        "explicit_new_global_requirements": [
            "a compatible determinant-line eta or differential refinement on the actual Gammahat orbifold and its fixed strata",
            "equivariant gluing for the order4 torus phase, including tangent/normal spin structures rather than a separate unconstrained scalar root",
            "the induced mixed normal term and all R/flavor anomaly curvatures",
            "the forced mass-zero defect spectra, allowed supersymmetric couplings and common regulator",
            "finite/global anomaly and orientation data of the proposed virtual determinant ratio and its endpoint sectors",
        ],
    }


def certificate_content():
    parents = load_parents()
    return {
        "schema": "v96_local_transport_quantization_v1",
        "input_core_hashes": {key: value[1] for key, value in PARENTS.items()},
        "embedded_v95_local_profile_core": LOCAL_CORE,
        "scope": "ordinary spin determinant-line CS quantization, a restricted free-edge obstruction, and an exact equivariant torus/matrix candidate with its uncanceled normal terms",
        "ordinary_eta_CS_quantization": ordinary_eta_cs_certificate(),
        "free_edge_transport_obstruction": graph_transport_certificate(parents["v94_route"]["normal_wall_quantization"]),
        "equivariant_torus_phase": torus_phase_certificate(),
        "virtual_shifted_determinant_profile": shifted_determinant_certificate(parents["v71"]),
        "smooth_equivariant_mass_intertwiner": smooth_mass_certificate(),
        "equivariant_scope_and_missing_data": equivariant_scope_certificate(),
        "terminal_decision": {
            "ordinary_integer_eta_CS_family_quantized_on_product_spin_backgrounds": True,
            "requested_fractional_free_edge_transport_quantized_as_standalone_ordinary_CS": False,
            "explicit_order4_torus_phase_and_smooth_mass_intertwiner_found": True,
            "virtual_character_difference_matches_pure_U1_transport": True,
            "introduced_normal_anomaly_canceled": False,
            "equivariant_quantized_relative_transport_action_constructed": False,
            "all_equivariant_or_topological_repairs_excluded": False,
            "same_action_parent_accepted": False, "closed_gates": [], "accepted_extensions": 0,
        },
        "primary_sources": [
            {"url": "https://arxiv.org/abs/math/0307120", "use": "Reduced eta modulo integers and its Chern-Simons transgression, sections1-2; integer powers are the ordinary eta refinement used here."},
            {"url": "https://arxiv.org/abs/1909.08775", "use": "APS index and relative determinant/Pfaffian interpretation; curvature matching alone does not supply the full anomaly gluing."},
            {"url": "https://arxiv.org/abs/hep-th/0305024", "use": "Section5.1 constructs local forms for globally vanishing localized anomalies; the form-level construction does not itself establish the new global level quantization sought here."},
            {"url": "https://arxiv.org/abs/hep-th/0612212", "use": "Shifted fixed-point characters and normal Lorentz anomaly terms; the exact m1-m2 calculation is derived from the bound V71 normalization."},
            {"url": "https://dlmf.nist.gov/23.3", "use": "Weierstrass differential equation used to normalize the square elliptic curve; divisor, character and fourth-power identity are computed explicitly here."},
            {"url": "https://dlmf.nist.gov/23.5", "use": "Section23.5(iii) identifies the lemniscatic square lattice; no assertion of a quantum field-theory completion is taken from this mathematical source."},
        ],
    }


def build_certificate():
    result = certificate_content()
    result["core_sha256"] = canonical_sha(result)
    return result


def validate_certificate(result):
    if result.get("core_sha256") != canonical_sha(result) or result != build_certificate():
        raise RuntimeError("F96 transport arithmetic, lineage or scope changed")


if __name__ == "__main__":
    print(json.dumps(build_certificate(), indent=2, sort_keys=True))
