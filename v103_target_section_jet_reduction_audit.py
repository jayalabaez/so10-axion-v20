"""Exact triangular reductions of the actual height targets, not new sections."""
from __future__ import annotations

import copy
from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path

import sympy as sp
import susy_v91_multipath_g1_frontier_master_audit as common

ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v102_route": ("SUSY_V102_CUBIC_EXCLUSION_COMMON_TENSOR_TARGET_AUDIT.json", "3d3f664328d8e92b069ff75f2f9599287e65703fa37c565e998351e07ea6e79e"),
    "v102_master": ("SUSY_V102_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json", "6c9421c299c4e8976a62a1ba50382e0a88d7ac4c8f289a18b94811d46aff88e5"),
}
ATLAS_CORE = "b5b51c1e062eb751e2bb1986c07c1a92bb7ebfa6f1f7a14abf1240f9d6f6c82c"
NEXT_ID = "F103_HIGHER_SECTION_HEIGHT_ATLAS_AND_GLOBAL_QUANTUM_VACUUM_COMPLETION"
T, X, u = sp.symbols("T X u")
alpha, beta, gamma, delta, epsilon = sp.symbols("alpha beta gamma delta epsilon")
SYMBOLS = {str(v): v for v in (T, X, u, alpha, beta, gamma, delta, epsilon)}
canonical_sha, file_sha = common.canonical_sha, common.file_sha


def parse(value):
    return sp.sympify(value, locals=SYMBOLS)


def load_inputs():
    reports = {key: common.load_bound(ROOT/name, core) for key, (name, core) in PARENTS.items()}
    route, master = reports["v102_route"], reports["v102_master"]
    if master["input_core_hashes"]["v102_route"] != PARENTS["v102_route"][1] or master["next_required_action"]["id"] != NEXT_ID:
        raise RuntimeError("V102 lineage or the F103 obligation changed")
    for key, base in (("v102_route", "susy_v102_cubic_exclusion_common_tensor_target_audit"),
                      ("v102_master", "susy_v102_multipath_g1_frontier_master_audit")):
        for name, pin in ((base+".py", "generator_sha256"), ("test_"+base+".py", "test_sha256")):
            if file_sha(ROOT/name) != reports[key]["artifact_hashes"][pin]:
                raise RuntimeError("bound V102 source/test changed: "+name)
    for name, digest in route["artifact_hashes"].items():
        if name.endswith(".py") and file_sha(ROOT/name) != digest:
            raise RuntimeError("bound V102 helper source/test changed: "+name)
    old = route["target_height_pole_atlas"]
    if old.get("core_sha256") != ATLAS_CORE or canonical_sha(old) != ATLAS_CORE:
        raise RuntimeError("the exact target pole atlas changed")
    if [r["height"] for r in old["target_sections"]] != [37, 148]:
        raise RuntimeError("the target normalization changed")
    return route, master


def conv(a, b, limit=None):
    size = len(a)+len(b)-1
    if limit is not None:
        size = min(size, limit+1)
    out = [0]*size
    for i, v in enumerate(a):
        for j, w in enumerate(b[:max(0, size-i)]):
            out[i+j] += v*w
    return out


def coeff(poly, index):
    return poly[index] if 0 <= index < len(poly) else 0


def coefficient_vectors(parameters):
    a, b, g, d, e = parameters
    return ([-432, -324*a, 0, -324*(e+g), -324*a*e, 0, -324*e*g],
            [3456, 3888*a, 729*b*b, 3888*(e+g), 3888*a*e+1458*b*d,
             729*b*b*e, 729*d*d+3888*e*g, 1458*b*d*e, 0, 729*d*d*e])


def arithmetic(prime):
    if prime is None:
        return Fraction, lambda numerator, denominator: Fraction(numerator, denominator)
    if type(prime) is not int or prime <= 3 or not sp.isprime(prime):
        raise ValueError("a prime greater than three is required")
    def norm(value):
        value = Fraction(value)
        return value.numerator*pow(value.denominator, -1, prime) % prime
    return norm, lambda a, b: (int(a)*pow(int(b), -1, prime)) % prime


def size_check(n):
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative integer pole degree required")


def near_reduction(n, Z, W, parameters, prime=None):
    """U=-24+sum U_i u^i; solve coefficient degrees 1..2n+3 exactly."""
    size_check(n)
    norm, div = arithmetic(prime)
    if len(Z) != n+1 or len(W) != 3*n+5 or norm(Z[0]) != 1:
        raise ValueError("near chart requires Z(0)=1 and full padded coefficient vectors")
    Z, W = list(map(norm, Z)), list(map(norm, W))
    a, b = coefficient_vectors(list(map(norm, parameters)))
    Z2 = conv(Z, Z)
    aZ4, bZ6 = conv(a, conv(Z2, Z2)), conv(b, conv(conv(Z2, Z2), Z2))
    W2 = conv(W, W)
    U = [norm(-24)]
    pivots = []
    for k in range(1, 2*n+4):
        cube_known = sum(U[i]*U[j]*coeff(U, k-i-j)
                         for i in range(len(U)) for j in range(len(U)) if 0 <= k-i-j < len(U))
        known = cube_known+sum(U[i]*coeff(aZ4, k-i) for i in range(len(U)))+coeff(bZ6, k)-coeff(W2, k-1)
        U.append(norm(div(-known, 1296)))
        pivots.append(1296)
    cube, linear = conv(conv(U, U), U), conv(U, aZ4)
    residual = [norm(coeff(cube, k)+coeff(linear, k)+coeff(bZ6, k)-coeff(W2, k-1)) for k in range(6*n+10)]
    if any(residual[:2*n+4]):
        raise RuntimeError("the near triangular recurrence failed")
    return {"Z": Z, "U": U, "W": W, "residual": residual,
            "tail": residual[2*n+4:], "pivots": pivots}


def identity_reduction(n, Z, U, parameters, prime=None):
    """Normalize U(0)=V(0)=1 without roots and solve V_1..V_(3n+6)."""
    size_check(n)
    norm, div = arithmetic(prime)
    if len(Z) != n+1 or len(U) != 2*n+5 or norm(U[0]) != 1 or not any(norm(v) for v in Z):
        raise ValueError("identity chart requires U(0)=1, nonzero Z and full padded vectors")
    Z, U = list(map(norm, Z)), list(map(norm, U))
    a, b = coefficient_vectors(list(map(norm, parameters)))
    Z2 = conv(Z, Z)
    aUZ4 = conv(conv(a, U), conv(Z2, Z2))
    bZ6 = conv(b, conv(conv(Z2, Z2), Z2))
    cube = conv(conv(U, U), U)
    degree = 6*n+12
    F = [norm(coeff(cube, k)+coeff(aUZ4, k-2)+coeff(bZ6, k-3)) for k in range(degree+1)]
    V = [norm(1)]
    for k in range(1, 3*n+7):
        known = sum(V[i]*V[k-i] for i in range(1, k))
        V.append(norm(div(F[k]-known, 2)))
    squared = conv(V, V)
    residual = [norm(coeff(squared, k)-F[k]) for k in range(degree+1)]
    if any(residual[:3*n+7]):
        raise RuntimeError("the identity triangular recurrence failed")
    return {"Z": Z, "U": U, "V": V, "residual": residual,
            "tail": residual[3*n+7:], "pivots": [2]*(3*n+6)}


def model_certificate(old):
    saved = old["unchanged_curve"]
    A, B = parse(saved["A"]), parse(saved["B"])
    a, b = coefficient_vectors((alpha, beta, gamma, delta, epsilon))
    pa, pb = sum(v*u**i for i, v in enumerate(a)), sum(v*u**i for i, v in enumerate(b))
    if sp.expand(u**6*A.subs(T, 1/u)-pa) != 0 or sp.expand(u**9*B.subs(T, 1/u)-pb) != 0:
        raise RuntimeError("the local coefficient arrays changed the frozen curve")
    c1, c2, z1, z2, w0, w1, d1, d2, z0 = sp.symbols("c1 c2 z1 z2 w0 w1 d1 d2 z0")
    near = (-24+c1*u+c2*u*u)**3+pa*(-24+c1*u+c2*u*u)*(1+z1*u+z2*u*u)**4+pb*(1+z1*u+z2*u*u)**6-u*(w0+w1*u)**2
    nc1 = sp.solve(sp.expand(near).coeff(u, 1), c1)[0]
    expected = -48*z1-9*alpha+w0*w0/sp.Integer(1296)
    if sp.expand(nc1-expected) != 0:
        raise RuntimeError("the near leading equation changed")
    identity = (1+d1*u+d2*u*u)**2-(1+c1*u+c2*u*u)**3-u*u*pa*(1+c1*u+c2*u*u)*(z0+z1*u)**4-u**3*pb*(z0+z1*u)**6
    id1 = sp.solve(sp.expand(identity).coeff(u, 1), d1)[0]
    id2 = sp.solve(sp.expand(identity).coeff(u, 2).subs(d1, id1), d2)[0]
    if sp.expand(id1-3*c1/2) != 0 or sp.expand(id2-(3*c2/sp.Integer(2)+3*c1*c1/8-216*z0**4)) != 0:
        raise RuntimeError("the identity leading equations changed")
    return {"a_coefficients_low_to_high": [str(v) for v in a], "b_coefficients_low_to_high": [str(v) for v in b],
            "minimal_infinity_coefficients": "A_infinity=u^2*a(u), B_infinity=u^3*b(u)",
            "exact_original_coefficient_array_residuals": ["0", "0"],
            "near_first_solved_coefficient": str(nc1),
            "resolved_near_coordinate_at_infinity": "U1+48*Z1=-9*alpha+W0^2/1296",
            "near_component_condition_holds_even_when_W0_zero": True,
            "identity_first_two_solved_coefficients": [str(id1), str(id2)]}


def sample_certificate(old):
    substitutions = {parse(key): parse(value) for key, value in old["unchanged_curve"]["coefficient_dictionary"].items()}
    parameters = [int(substitutions[v].subs(X, 1)) for v in (alpha, beta, gamma, delta, epsilon)]
    rows = []
    for prime in (101, 103):
        n = 17
        Z = [1]+[(i*i+3*i+5) % prime for i in range(1, n+1)]
        W = [(i*i+7*i+3) % prime for i in range(3*n+5)]
        data = near_reduction(n, Z, W, parameters, prime)
        rows.append({"chart": "near_height37", "prime": prime, "n": n,
                     "input_Z": Z, "input_free_W": W, "solved_U": data["U"],
                     "vanishing_low_residual_count": 2*n+4, "remaining_residual": data["tail"]})
        for m in (0, 1, 72):
            n = 72
            Z = [0]*m+[(i*i+2*i+1) % prime for i in range(n+1-m)]
            U = [1]+[(i*i+5*i+2) % prime for i in range(1, 2*n+5)]
            data = identity_reduction(n, Z, U, parameters, prime)
            rows.append({"chart": "identity_height148", "prime": prime, "n": n, "O_intersection_at_infinity": m,
                         "input_Z": Z, "input_free_U": U, "solved_V": data["V"],
                         "vanishing_low_residual_count": 3*n+7, "remaining_residual": data["tail"]})
    return {"parameters_at_X_one": parameters, "rows": rows,
            "all_rows_are_exact_recursion_checks_not_generic_existence_or_exclusion": True,
            "all_example_tails_are_nonzero": all(any(row["remaining_residual"]) for row in rows)}


@lru_cache(maxsize=2)
def pure_json(old_json):
    old = json.loads(old_json)
    return json.dumps({"original_local_model": model_certificate(old), "exact_modular_recursion_checks": sample_certificate(old)}, sort_keys=True)


def build_certificate():
    route, master = load_inputs()
    old = route["target_height_pole_atlas"]
    out = {
        "schema": "v103_exact_target_section_triangular_jet_reduction_v1",
        "status": "EXACT_74_BY_73_AND_222_BY_221_TARGET_SYSTEMS__GLOBAL_TAILS_UNSOLVED",
        "input_core_hashes": {key: value[1] for key, value in PARENTS.items()},
        "bound_V102_target_atlas_core": ATLAS_CORE,
        "coefficient_payload_sha256": old["coefficient_payload_sha256"],
        "inherited_frontier": copy.deepcopy(route["nonzero_pivot_section_elimination"]["preserved_frontier"]),
        **json.loads(pure_json(json.dumps(old, sort_keys=True))),
        "near_height37_reduced_system": {
            "height": 37, "global_P_dot_O": 17, "base_and_field": "unchanged P1_T over k=C(X)",
            "coordinates": "u=1/T; Zhat=u^n Z_aff(1/u), Ubar=u^(2n+3) U_aff(1/u), W=u^(3n+4) V_aff(1/u); x_infinity=u*Ubar/Zhat^2, y_infinity=u^2*W/Zhat^3",
            "normalization": "Zhat(0)=1 and Ubar(0)=-24; monic affine Z is achieved by the existing weighted constant rescaling",
            "equation": "Ubar^3+a(u)*Ubar*Zhat^4+b(u)*Zhat^6-u*W^2=0",
            "degrees_Zhat_Ubar_W": [17, 37, 55], "equation_degree_upper_bound": 111,
            "free_variable_names": ["Z"+str(i) for i in range(1, 18)]+["W"+str(i) for i in range(56)],
            "free_variable_count": 73, "solved_U_coefficients": list(range(1, 38)),
            "constant_pivot_for_every_solved_coefficient": 1296,
            "recurrence": "U_k=-[u^k](U_<k^3+a*U_<k*Zhat^4+b*Zhat^6-u*W^2)/1296 for k=1,...,2n+3",
            "remaining_equations": "[u^k]F=0 for k=2n+4,...,6n+9 after the triangular substitution",
            "remaining_coefficient_indices": list(range(38, 112)), "remaining_equation_count": 74,
            "generic_n_counts": "4n+5 free coefficients and 4n+6 tail equations",
            "variable_leading_coefficient_or_W0_divided_out": False,
            "no_algebraic_constant_extension_required": True,
            "near_component_at_infinity_automatic_after_equation_and_normalization": True,
            "global_tail_solved": False,
        },
        "identity_height148_reduced_system": {
            "height": 148, "global_P_dot_O": 72, "base_and_field": "unchanged P1_T over k=C(X)",
            "coordinates": "Uhat=u^(4+2n) U_aff(1/u), Vhat=u^(6+3n) V_aff(1/u), Zhat=u^n Z_aff(1/u)",
            "normalization": "Primitivity and the identity component force Uhat(0)*Vhat(0)!=0 and V0^2=U0^3. Set t=V0/U0 in k*, then scale (U,V,Z) by (t^-2,t^-3,t^-1), giving Uhat(0)=Vhat(0)=1 without adjoining roots.",
            "equation": "Vhat^2-Uhat^3-u^2*a(u)*Uhat*Zhat^4-u^3*b(u)*Zhat^6=0",
            "degrees_Zhat_Uhat_Vhat": [72, 148, 222], "equation_degree_upper_bound": 444,
            "free_variable_names": ["Z"+str(i) for i in range(73)]+["U"+str(i) for i in range(1, 149)],
            "free_variable_count": 221, "solved_V_coefficients": list(range(1, 223)),
            "constant_pivot_for_every_solved_coefficient": 2,
            "recurrence": "V_k=([u^k](Uhat^3+u^2*a*Uhat*Zhat^4+u^3*b*Zhat^6)-sum_{i=1}^{k-1}V_i*V_(k-i))/2",
            "remaining_coefficient_indices": list(range(223, 445)), "remaining_equation_count": 222,
            "generic_n_counts": "3n+5 free coefficients and 3n+6 tail equations",
            "all_infinity_pole_multiplicities_retained": list(range(73)),
            "Z0_divided_out": False, "no_algebraic_constant_extension_required": True,
            "global_tail_solved": False,
        },
        "equivalence_and_local_global_boundary": {
            "triangular_reduction_is_exact_over_Q_original_parameters": True,
            "pivot_proof": "At the near chart's constant term, the derivative in Ubar is3*(-24)^2-432=1296. Thus the degree-k coefficient is1296*U_k plus terms involving only earlier U coefficients. On the normalized identity chart, V0=1 makes the analogous coefficient2*V_k plus lower terms. Future coefficients cannot affect earlier degrees. Induction gives unique polynomial expressions in the free coefficients with only constant rational denominators.",
            "sufficiency_requires_all_tail_equations_and_homogeneous_primitivity": True,
            "remaining_primitivity_conditions": ["Z is not the zero form", "homogeneous gcd(U,Z)=1", "homogeneous gcd(V,Z)=1"],
            "leading_jet_solution_is_a_global_section": False,
            "coefficient_count_is_a_no_solution_proof": False,
            "finite_modular_samples_prove_original_field_solvability": False,
            "near_n0_matches_the_already_excluded_minus24_cubic_degree_pattern": True,
            "identity_n0_matches_the_still_open_quartic_degree_pattern": True,
        },
        "identity_target_infinity_partition": {
            "m": "ord_u(Zhat) ranges0..72; Uhat(0)=Vhat(0)=1 prevents cancellation",
            "O_intersection_at_infinity": "m", "finite_O_intersection_degree": "72-m",
            "affine_degrees_Z_U_V": ["72-m", "148", "222"],
            "minimal_local_orders_x_y_if_m_positive": ["-2m", "-3m"],
            "affine_rational_growth_x_y": ["4+2m", "6+3m"],
            "m72_polynomial_coordinates_possible_in_this_atlas": True,
            "m72_polynomial_degrees_x_y": [148, 222],
            "a_polynomial_x_coordinate_implies_global_integrality": False,
            "height37_requires_nontrivial_finite_denominator_degree": 17,
        },
        "terminal_decision": {"two_exact_reduced_target_systems_constructed": True,
                              "either_target_section_constructed_or_excluded": False,
                              "quartic_chart_solved_here": False, "actual_original_MW_rank_computed": False,
                              "compact_threefold_height_realized": False, "microscopic_parent_accepted": False,
                              "theory_complete": False, "closed_gates": []},
        "primary_sources": [
            {"url": "https://arxiv.org/pdf/0907.0298", "use": "Sections2.4,11.8 and11.17 supply the group-law, height and minimal-coordinate framework. The source-bound near and identity target atlases are reduced here by exact coefficient induction; their unsolved tails are not evidence for point existence."},
            {"url": "https://stacks.math.columbia.edu/tag/04GE", "use": "The simple-root/Henselian lifting principle motivates separating a locally solvable power series from a globally polynomial section. Here the needed recursion is independently explicit with constant pivots1296 and2, and no convergence or local-to-global existence theorem is assumed."},
        ],
    }
    out["core_sha256"] = canonical_sha(out)
    return out


def validate_certificate(out):
    if out.get("core_sha256") != canonical_sha(out) or out != build_certificate():
        raise RuntimeError("F103 target jet reduction, original member or scope changed")


if __name__ == "__main__":
    print(json.dumps(build_certificate(), sort_keys=True, indent=2))
