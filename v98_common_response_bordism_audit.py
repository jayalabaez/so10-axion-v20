"""F98: continuous-product flat completeness and a changed determinant cover.

These are closed-five-dimensional response theorems, not a full orbifold
determinant, boundary trivialization, or a microscopic theory acceptance.
"""
from __future__ import annotations

import copy
from itertools import combinations_with_replacement
from pathlib import Path

import sympy as sp
import susy_v91_multipath_g1_frontier_master_audit as common
import v97_mixed_gauge_relative_glue_audit as previous
import v97_normal_SU2_refinement_audit as normal_previous

ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v97_route": ("SUSY_V97_EQUIVARIANT_INDEX_RELATIVE_GLUE_SECTION_AUDIT.json", "161eb53a3e453c80b3887d365e31c32c6846d1c6f8d45b474b849f07a3de2020"),
    "v97_master": ("SUSY_V97_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json", "f7ccb9c8d047a3135330ed7c8a361fd4625ca343547cf05b9cc31a7158b50e31"),
}
a, b, ell, u, A2, B2, B3, r2, t, E2, E3, d, p, c = sp.symbols("a b ell u A2 B2 B3 r2 t E2 E3 d p c")


def mod2_rank(matrix):
    rows = [list(map(lambda x: int(x) % 2, row)) for row in matrix]
    pivot = 0
    for column in range(len(rows[0]) if rows else 0):
        found = next((j for j in range(pivot, len(rows)) if rows[j][column]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        for j in range(len(rows)):
            if j != pivot and rows[j][column]:
                rows[j] = [x ^ y for x, y in zip(rows[j], rows[pivot])]
        pivot += 1
    return pivot


def bordism_table(*, local=False, include_R=False):
    if type(local) is not bool or type(include_R) is not bool:
        raise ValueError("category flags must be boolean")
    roots = [t, ell, u] if local else [a, b, ell, u]
    second = [E2] if local else [A2, B2]
    third = [E3] if local else [B3]
    rules = {x: x*x for x in roots}
    rules.update({E2: t*E2+E3} if local else {A2: a*A2, B2: b*B2+B3})
    if include_R:
        second.append(r2)
        rules[r2] = 0
    variables = roots+second+third
    degree2 = roots
    degree4 = [sp.prod(v) for v in combinations_with_replacement(roots, 2)]+second
    degree6 = ([sp.prod(v) for v in combinations_with_replacement(roots, 3)]
               +[x*y for x in roots for y in second]+third)

    def sq2(expression):
        # Sq1=0 because these classes lift integrally; Cartan reduces to a
        # derivation for Sq2. Coefficients are reduced after differentiation.
        value = sum(sp.diff(expression, x)*image for x, image in rules.items())
        return sp.Poly(value, *variables, modulus=2).as_expr()

    sq_low, sq_high = [sq2(v) for v in degree2], [sq2(v) for v in degree4]
    coefficient = lambda expr, mon: int(sp.Poly(expr, *variables).coeff_monomial(mon)) % 2
    outgoing = [[coefficient(expr, mon) for mon in degree4] for expr in sq_low]
    incoming = [[coefficient(expr, mon) for mon in degree6] for expr in sq_high]
    if any(int(v) % 2 for v in sp.Matrix(outgoing)*sp.Matrix(incoming)):
        raise RuntimeError("AHSS d2 composition must vanish")
    out_rank, in_rank = mod2_rank(outgoing), mod2_rank(incoming)
    dimension = len(degree4)-out_rank-in_rank
    if dimension != int(include_R):
        raise RuntimeError("continuous-product Omega5 changed")
    category = "U5_E x U1_L x U1_M" if local else "U2_A x U3_B x U1_L x U1_M"
    if include_R:
        category += " x SU2_R"
    return {
        "ordinary_spin_product_category": category,
        "integral_cohomology": "torsion-free even polynomial Chern ring; odd homology vanishes and reduction H6(Z)->H6(Z2) is onto",
        "degree2_basis": [str(v) for v in degree2],
        "degree4_basis": [str(v) for v in degree4],
        "degree6_basis": [str(v) for v in degree6],
        "Sq2_degree2": [str(v) for v in sq_low], "Sq2_degree4": [str(v) for v in sq_high],
        "d2_outgoing_H4_Z2_to_H2_Z2": outgoing,
        "d2_incoming_H6_Z_to_H4_Z2": incoming,
        "outgoing_rank": out_rank, "incoming_rank": in_rank,
        "E3_4_1_dimension": dimension,
        "only_total_degree5_E2_term": "E2_(4,1)=H4(BG;Z2); Omega5(Spin pt)=0 and all remaining possible terms have odd homological degree or Omega3=0",
        "higher_differentials": "No higher incoming first-quadrant arrows reach (4,1). Outgoing d3 has target H1(BG;Omega3)=0; d4 maps a finite group to E4_(0,4)=Z and is zero. No later targets exist. The target Z has no earlier incoming image because H3(BG;Z2)=0 and Omega3=0.",
        "extension_problem": "only one possibly nonzero total-degree-five associated-graded term",
        "Omega5": "Z2" if include_R else "0",
        "group_order": 2 if include_R else 1,
        "surviving_dual_class": "c2(R)" if include_R else None,
        "full_Gammahat_or_finite_symmetry_category_computed": False,
    }


def integer_common_response(saved):
    cup = previous.C4_cup(previous.ell, previous.A2+previous.B2+previous.a*previous.b)
    cup += previous.C4_cup(previous.ell+previous.b, previous.A2+previous.B2-previous.a*previous.b)
    cup += previous.C2_cup()
    total = previous.R4(previous.a+previous.b, previous.A2+previous.B2+previous.a*previous.b)
    total += previous.R4(previous.a-previous.b, previous.A2+previous.B2-previous.a*previous.b)+previous.R2()
    eta = 35*previous.I(previous.d+previous.u)-10*previous.I(previous.d)-35*previous.I(previous.u)
    difference = sp.expand((total-eta-cup).subs(previous.d, previous.a+previous.b+2*previous.ell))
    if difference != 0 or sp.expand(cup-sp.sympify(saved["exact_index_decomposition"]["common_total_integral_cup_part"])) != 0:
        raise RuntimeError("F98 common response does not reconstruct the actual V97 remainder")
    return {
        "background_relation": "D=det(A)*det(B)*L^2, E0=A+B, E1=A+B*, L1=L*det(B)",
        "determinant_root": "d=a+b+2ell",
        "positive_eta_levels": {"D*M": 35, "D": -10, "M": -35},
        "integral_cup_polynomial": str(sp.expand(cup)),
        "combined_I6_before_d_relation": str(sp.expand(total)),
        "reconstruction_difference_after_d_relation": str(difference),
        "closed_spin5_positive_response": "exp(2*pi*i*(35*xi(Y,D*M)-10*xi(Y,D)-35*xi(Y,M)+hol_Y(C_hat)))",
        "xi_definition": "xi=(eta+dim(kernel))/2; all eta coefficients are integers and C_hat is the integral differential cup polynomial displayed above",
        "negative_response": "complex conjugate of the displayed positive response",
        "equivalent_filling_definition": "exp(2*pi*i*integral_W6 R_total), with the spin structure and A,B,L,M bundles extending Y5; Omega5=0 supplies a filling and integral periods give filling independence",
        "every_closed_spin5_background_of_this_category_bounds": True,
        "same_curvature_flat_ratio": "Any normalized bordism-invariant flat ratio is in Hom(Omega5,U1)=0, so two such closed-five-dimensional anomaly responses with this full restricted curvature agree.",
        "closed5_phase_uniqueness_given_full_restricted_curvature": True,
        "all_boundary_trivializations_or_4D_counterterm_choices_unique": False,
        "actual_parent_anomaly_is_proved_to_factor_through_this_category": False,
        "independent_endpoint_gluing_or_full_equivariant_action_constructed": False,
    }


def determinant_cover(degree):
    if type(degree) is not int or degree < 1:
        raise ValueError("positive integral covering degree required")
    pullback = sp.expand((d*d*(d+u)/4).subs(d, degree*c))
    coefficients_integral = all(v.is_Integer for v in sp.Poly(pullback, c, u).coeffs())
    # For odd degree, spin CP3 with C=O(1), D=O(degree), M trivial
    # is an allowed quotient background and has the odd period degree^3/4.
    cp3_period = sp.Rational(degree**3, 4)
    if coefficients_integral != (degree % 2 == 0):
        raise RuntimeError("determinant-cover divisibility theorem changed")
    return {"cover_degree": degree, "D_relation": "D=C^"+str(degree),
            "P_over4_pullback": str(pullback),
            "integral_cup_coefficients": coefficients_integral,
            "CP3_C_degree1_M_trivial_period": str(cp3_period),
            "CP3_period_mod1": str(cp3_period % 1),
            "local_P_over4_quantized_on_this_cover": coefficients_integral}


def spin_c_root_response():
    x, h, j = sp.symbols("x h j")
    index = lambda z: sp.expand((z+x/2)**3/6-(z+x/2)*p/24)
    virtual = sp.expand(index(2*c)-2*index(c)+index(0))
    target = sp.expand((d*d*(d+x/2)/4).subs(d, 2*c))
    if sp.expand(virtual+c**3-target) != 0:
        raise RuntimeError("natural Spin-c determinant-root index identity failed")
    integrate = lambda value: sp.Poly(sp.expand(value), h, j).coeff_monomial(h*h*j)
    # CP2 x CP1, x=h. Twist its complex spin-c structure (3h+2j) by
    # O(-1,-1). Tensoring further by C=O(1,1) gives the stated line indices.
    mapping = {x: h, c: h+j, p: 3*h*h}
    index_values = [integrate(value.subs(mapping)) for value in (index(2*c), index(c), index(0))]
    target_value = integrate(target.subs(mapping))
    # The distinct old normal target still fails at x=h+2j, c2(E)=0, C=1.
    old_u = (h+2*j)/2
    old_normal_period = integrate(old_u**3+old_u*3*h*h/4)
    if index_values != [6, 1, 0] or target_value != 7 or old_normal_period != sp.Rational(3, 2):
        raise RuntimeError("Spin-c root response or preserved old half-period changed")
    return {
        "tangential_category": "Spin-c(TY) with determinant the genuine normal line N, x=c1(N); independent gauge determinant D=C^2 with chosen genuine line C and connection",
        "normal_half_class": "u=x/2 is only a formal curvature variable; no associated square-root line M is required",
        "Spin_c_line_index": str(index(sp.Symbol("z"))),
        "integer_virtual_index_J_C2_minus_2J_C_plus_J_1": str(virtual),
        "additional_integral_cup": "c^3",
        "target_P_over4_with_D_C_squared": str(target),
        "exact_identity_difference": str(sp.expand(virtual+c**3-target)),
        "closed5_positive_response": "exp(2*pi*i*(xi_c(Y,C^2)-2*xi_c(Y,C)+xi_c(Y,1)+hol_Y(c_hat^3)))",
        "eta_integer_levels": {"C^2": 1, "C": -2, "1": 1},
        "xi_c_definition": "kernel-inclusive reduced eta of the Spin-c Dirac operator with determinant N, twisted by the indicated genuine line",
        "definition_on_nonbounding_closed5": "the integer reduced-eta combination and integral cup holonomy are defined without choosing a bounding6-manifold; APS yields the displayed curvature and integral filling changes",
        "normal_square_root_not_needed_for_this_response": True,
        "CP2_times_CP1_example": {
            "relations": "h^3=j^2=0, integral h^2*j=1", "x": "h", "c": "h+j", "p1": "3*h^2",
            "Spin_c_structure": "complex determinant 3h+2j twisted by O(-1,-1), giving determinant h",
            "normal_square_root_exists": False,
            "three_line_indices": [int(v) for v in index_values],
            "independent_holomorphic_check": "chi(O(1,1))=6, chi(O(0,0))=1, chi(O(-1,-1))=0; the base spin-c structure is the complex one twisted by O(-1,-1)",
            "c_cubed_period": 3, "P_over4_period": int(target_value),
        },
        "minimal_determinant_cover_degree_still_two": True,
        "odd_cover_exclusion": "the ordinary-spin CP3 subset with N trivial still gives the noninteger period r^3/4 for every odd r",
        "distinct_V96_normal_repair_half_period": {
            "test": "Spin-c CP2 x CP1 with x=h+2j, p1=3h^2, c2(E)=0 and C trivial",
            "old_normal_target": "-u*c2(E)+u^3+u*p1/4", "old_target_period": str(old_normal_period),
            "new_quarter_response_period_on_this_test": 0,
            "old_normal_half_period_removed": False,
        },
        "all_full_Gammahat_tangential_backgrounds_identified_with_this_category": False,
        "SU2_R_and_finite_defect_refinements_glued": False,
        "same_action_microscopic_inflow_or_boundary_state_constructed": False,
        "changed_determinant_cover_adopted": False,
    }


def load_inputs():
    inputs = {key: common.load_bound(ROOT/name, core) for key, (name, core) in PARENTS.items()}
    route, master = inputs["v97_route"], inputs["v97_master"]
    if master["input_core_hashes"]["v97_route"] != PARENTS["v97_route"][1]:
        raise RuntimeError("V97 lineage edge changed")
    if master["next_required_action"]["id"] != "F98_GAMMAHAT_TRANSPORT_LIFT_AND_ORIGINAL_SQUARE_SECTION":
        raise RuntimeError("F98 obligation changed")
    for key, module in (("mixed_gauge_relative_glue", previous), ("normal_SU2_refinement", normal_previous)):
        saved = route[key]
        if saved.get("core_sha256") != common.canonical_sha(saved) or saved != module.build_certificate():
            raise RuntimeError("bound V97 helper changed: "+key)
        for name in (module.__name__+".py", "test_"+module.__name__+".py"):
            if common.file_sha(ROOT/name) != route["artifact_hashes"][name]:
                raise RuntimeError("bound V97 source/test changed: "+name)
    return route


def content():
    route = load_inputs()
    mixed, normal = route["mixed_gauge_relative_glue"], route["normal_SU2_refinement"]
    if mixed["primitive_period_and_order"]["rows"][0]["P_period"] != "1":
        raise RuntimeError("the primitive CP3 obstruction was lost")
    tables = {"local": bordism_table(local=True), "common": bordism_table(),
              "local_with_R": bordism_table(local=True, include_R=True),
              "common_with_R": bordism_table(include_R=True)}
    # A direct equality of index polynomials plus Omega5=0 identifies these
    # particular closed5 responses. It never chooses a fourth root of them.
    p_difference = sp.expand(previous.I(2*previous.d+previous.u)-2*previous.I(previous.d+previous.u)+previous.I(previous.u)-previous.P())
    if p_difference != 0:
        raise RuntimeError("P eta/cup curvature identity changed")
    return {
        "schema": "v98_common_continuous_response_bordism_and_determinant_cover_v1",
        "status": "CLOSED5_PRODUCT_REFINEMENT_UNIQUE__DETERMINANT_DOUBLE_COVER_QUANTIZES_QUARTERS__FULL_PARENT_OPEN",
        "input_core_hashes": {key: value[1] for key, value in PARENTS.items()},
        "ordinary_spin_product_bordism": tables,
        "common_integer_response": integer_common_response(mixed),
        "P_eta_cup_comparison": {
            "eta_response": "exp(2*pi*i*(xi(D^2*M)-2*xi(D*M)+xi(M)))",
            "cup_response": "exp(2*pi*i*hol_Y(d_hat*d_hat*(d_hat+u_hat)))",
            "exact_curvature_difference": str(p_difference),
            "equal_on_all_closed_spin5_of_local_and_common_product_categories": True,
            "reason": "the ratio has zero curvature and hence is a bordism character; both computed Omega5 groups vanish",
            "equality_provides_canonical_quarter_roots": False,
        },
        "SU2_flat_refinement": {
            "adding_independent_SU2_R_changes_Omega5_to": "Z2",
            "surviving_test": "S4 unit R instanton times a periodic spin circle, all A,B,L,M bundles trivial",
            "unique_possible_nontrivial_flat_character": "nu_R=(-1)^(ind2 D5_Rfund)",
            "V97_added_normal_doublet_phase_on_generator": normal["flat_refinement"]["relative_phase_on_product_generator"],
            "P_eta_cup_ratio_on_generator": "+1",
            "P_eta_cup_equality_also_holds_with_independent_R": True,
            "P_eta_cup_reason_with_R": "both responses ignore R; the line-index virtual rank is zero on the only generator, so their ratio has trivial generator value",
            "V97_normal_doublet_nu_R_is_erased_by_continuous_gauge_factors": False,
            "original_parent_R_flat_phase_determined": False,
        },
        "quarter_class_and_changed_cover": {
            "old_category_CP3_period_P_over4": "1/4",
            "old_category_closed6_filling_change_phase": "i",
            "adding_a_flat_closed5_character_repairs_nonintegral_curvature_periods": False,
            "small_cover_checks": [determinant_cover(n) for n in range(1, 9)],
            "all_positive_integer_cover_degrees_classified": "D=C^r gives P/4=(r^3/4)*c^3+(r^2/4)*c^2*u. Even r has integral coefficients. Odd r has nonintegral CP3 period r^3/4, so is impossible on the stated unrestricted product backgrounds.",
            "minimum_cover_degree": 2,
            "D_square_root_is_additional_background_data": True,
            "double_cover_local_positive_quarter_response": "holonomy of c_hat^2*(2*c_hat+u_hat), where D=C^2 as line bundles with compatible connection",
            "double_cover_negative_fractional_profile_responses": ["-c_hat^2*(2*c_hat+u_hat)", "-c_hat^2*(2*c_hat+u_hat)", "+2*c_hat^2*(2*c_hat+u_hat)"],
            "original_D_odd_CP3_background_lifts_to_double_cover": False,
            "normal_root_or_independent_flavor_cover_alone_removes_quarter": False,
            "normal_or_flavor_cover_counterexample": "D=O(1), normal and added flavor lines trivial on spin CP3 retains P/4=1/4 regardless of roots of those trivial lines",
            "global_gauge_group_and_allowed_bundles_changed": True,
            "equivalent_reformulation_of_unchanged_theory": False,
            "new_cover_adopted_in_canonical_theory": False,
            "double_cover_repairs_geometric_Spin4_Spin2_identity_of_M_carrier": False,
            "root_cover_bordism_or_discrete_equivariant_gluing_computed": False,
        },
        "natural_Spin_c_determinant_root_response": spin_c_root_response(),
        "terminal_decision": {
            "restricted_continuous_closed5_flat_ambiguity_resolved": True,
            "restricted_integer_eta_and_cup_P_phases_identified": True,
            "minimal_determinant_cover_for_quarter_quantization_computed": True,
            "quantized_quarter_response_without_normal_square_root_on_Spin_c_cover_constructed": True,
            "all_F98_obligations_completed": False,
            "full_quantum_Gammahat_parent_accepted": False, "closed_gates": [],
        },
        "primary_sources": [
            {"url": "https://web.math.ucsb.edu/~dai/book.pdf", "use": "Section2.3 defines the Spin-c determinant; the end of Section3.3 gives the Spin-c index Ahat*exp(c1(N)/2). The integer line-index combination and CP2 x CP1 Euler characteristics are derived here."},
            {"url": "https://arxiv.org/abs/1910.11277", "use": "Sections3,4.3 and6.1 give product cohomology, spin-AHSS d2 dual Sq2, and Sq2(c_i)=c1*c_i+(i-1)c_(i+1). The four product calculations here are performed explicitly, not quoted as the full orbifold group."},
            {"url": "https://arxiv.org/abs/hep-th/9405012", "use": "Reduced eta invariants and determinant-line gluing; the present equalities concern closed5 phases, not a unique boundary trivialization."},
            {"url": "https://arxiv.org/abs/2011.05768", "use": "Sections3-4 distinguish integral differential-character holonomy from an equivariant lift; an integral pullback polynomial gives a quantized response only on its chosen background category."},
            {"url": "https://arxiv.org/abs/1207.5449", "use": "Integral differential cup-product Chern-Simons construction, used explicitly after adding a determinant root; no fractional response on the old category is inferred."},
        ],
    }


def build_certificate():
    result = content()
    result["core_sha256"] = common.canonical_sha(result)
    return result


def validate_certificate(result):
    if result.get("core_sha256") != common.canonical_sha(result):
        raise RuntimeError("F98 continuous response certificate core is noncanonical")
    body = copy.deepcopy(result)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("F98 continuous response arithmetic, lineage or scope changed")
