"""F94 normal-root period screens and a conditional wall-fermion witness.

All results are conditional on explicitly stated tangential structures.  An
ordinary spin four-manifold with a Spin^c(11) *gauge* bundle is not a general
Gammahat background.  A normal Spin(2) root is not an automatically available
equivariant line on the effective C4/C2 orbifold, even though the frozen bulk
lift already contains correlated half-angle factors.  No relative quantum
action or globally compatible new wall representation is constructed here.
"""
from __future__ import annotations

import copy
import hashlib
from itertools import combinations
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v93_route": ("SUSY_V93_LOCALIZED_ANOMALY_R_LIFT_JACOBIAN_AUDIT.json",
                  "4f81852d9e272d3fb12946ad41cb01d9f93462f75cef69123106a80b03f092f2"),
    "v93_master": ("SUSY_V93_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
                   "d34479d8daa9a37d090e2d2ace471464171a0c28208d3d88b77e5dc168a97932"),
    "v91_quotient": ("SUSY_V91_SPINC_QUANTIZATION_TENSOR_CONE_FINITE_TORSION_AUDIT.json",
                     "4a581af0dd4cfc6fd3f66ef1e3ea2801b9770c67822d984a02deb602865c0322"),
}
E = sp.symbols("e1:6")
f, x, p, u, c, t, c2 = sp.symbols("f x p u c t c2")
VARIABLES = E + (f, x, p, u)


def canonical_sha(value):
    body = copy.deepcopy(value)
    body.pop("core_sha256", None)
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_parents():
    reports = {}
    for key, (name, expected) in PARENTS.items():
        value = json.loads((ROOT/name).read_text(encoding="utf-8"))
        if value.get("core_sha256") != expected or canonical_sha(value) != expected:
            raise RuntimeError("changed or noncanonical F94 normal parent: " + key)
        reports[key] = value
    if reports["v93_master"]["input_core_hashes"]["v93_route"] != PARENTS["v93_route"][1]:
        raise RuntimeError("V93 route/master edge changed")
    if reports["v93_master"]["next_required_action"]["id"] != "F94_QUANTIZED_RELATIVE_WALL_COMPLETION_AND_MW_HEIGHT":
        raise RuntimeError("F94 obligation changed")
    group = reports["v91_quotient"]["old_quotient_obstruction"]["group"]
    if group != "H=Spin^c(11)=(Spin(11) x U1)/<(z,-1)>":
        raise RuntimeError("ordinary gauge quotient changed")
    return reports


def pairing(a, b):
    """Intersection form of S2 x S2 on its integral a,b generators."""
    return sp.Rational(a[0])*sp.Rational(b[1])+sp.Rational(a[1])*sp.Rational(b[0])


def fixed_normal_form(n, quotient=False):
    """n*A_frozen after x=n*u, and optionally f=c/2."""
    if type(n) is not int or n < 1:
        raise ValueError("normal covering degree must be a positive integer")
    A = c2/2-f*t+sp.Rational(39, 2)*f**2-sp.Rational(87, 16)*f*x-(p+x**2)/8
    result = n*A.subs(x, n*u)
    return sp.expand(result.subs(f, c/2) if quotient else result)


def fixed_period(n, flux, trace, normal, c2_number=0, p1_number=0):
    return sp.simplify(n*sp.Rational(c2_number, 2)-n*pairing(flux, trace)
                       +sp.Rational(39*n, 2)*pairing(flux, flux)
                       -sp.Rational(87*n*n, 16)*pairing(flux, normal)
                       -sp.Rational(n*p1_number, 8)-sp.Rational(n**3, 8)*pairing(normal, normal))


def normal_isotropy_certificate(source):
    blocks = source["singlet_shifted_character_anomaly"]["block_certificates"]
    first = blocks[0]["certificate"]["strata"]
    rows = {}
    for point, value in first.items():
        n, weight = value["order"], value["normal_weight"]
        if (n, weight) != (4 if point in ("z00", "z11") else 2, 1):
            raise RuntimeError("frozen effective normal character changed")
        roots = [r for r in range(n) if (2*r-weight) % n == 0]
        projection = [j % n for j in range(2*n)]
        checks = {
            "projection_is_homomorphism": all(projection[(a+b) % (2*n)] == (projection[a]+projection[b]) % n for a in range(2*n) for b in range(2*n)),
            "square_of_root_character_is_pulled_normal_character": all((2*j) % (2*n) == (2*projection[j]) % (2*n) for j in range(2*n)),
            "root_kernel_character_is_minus_one": (n % (2*n)) == n,
        }
        if roots or not all(checks.values()):
            raise RuntimeError("effective stabilizer square-root calculation failed")
        rows[point] = {"effective_order": n, "normal_weight": weight,
                       "square_root_characters_on_effective_group": roots,
                       "minimal_cyclic_pullback_order": 2*n,
                       "projection_exponents": projection, "projection_kernel": [0, n],
                       "root_character_weight_on_pullback": 1,
                       "pulled_normal_character_weight": 2, "checks": checks}
    return {"strata": rows,
            "no_root_statement_scope": "no ordinary square-root character on the unchanged effective C4/C2 stabilizers",
            "existing_Gammahat_already_contains_correlated_half_angle_factors": True,
            "independent_normal_root_descends_through_existing_Gammahat_kernel": None,
            "existing_Gammahat_is_proved_to_exclude_the_needed_root": False,
            "new_root_action_requires_explicit_kernel_and_global_compatibility_data": True,
            "spacetime_spin_is_not_the_same_as_equivariant_normal_spin": True}


def period_certificates():
    fixed_rows = []
    for n in range(1, 9):
        fixed_rows.append({"cover_degree": n,
                           "S4_unit_SU5_instanton": str(sp.Rational(n, 2)),
                           "S2xS2_integral_f_a_u_b": str(fixed_period(n, (1, 0), (0, 0), (0, 1))),
                           "S2xS2_quotient_c_t_a_u_b": str(fixed_period(n, (sp.Rational(1, 2), 0), (1, 0), (0, 1))),
                           "all_integral_f_spin4_periods_integral_iff": n % 4 == 0,
                           "all_quotient_spin4_periods_integral_iff": n % 8 == 0})
    fixed = {
        "scope": "the frozen V93 allocation A4 as a naive independently periodic functional extended over arbitrary allowed gauge/normal bundles on closed ordinary spin4 bases",
        "minimum_normal_cover_integral_f": 4,
        "minimum_normal_cover_Spin_c11": 8,
        "proof_and_counterexamples": fixed_rows,
        "integral_f_degree4_four_form": str(fixed_normal_form(4)),
        "quotient_degree8_four_form": str(fixed_normal_form(8, True)),
        "gauge_quotient_geometry": "E is the ordinary rank5 complex U5 bundle in E11=E_real+R; c=c1(det Spin^c11), 2f=c and c=t=c1(E) modulo2",
        "half_flux_witness_is_an_actual_quotient_bundle": "on S2xS2 take E=L_a+1^4, c=t=a, c2(E)=0, u=b; w2(E11)=c mod2",
        "integral_flux_witness_is_admissible": "E trivial, f=a, c=2a, u=b; the gauge quotient parity relation holds",
        "necessity": "S4 forces n even. The integral-flux witness requires16|87*n^2, hence4|n. The half-flux witness requires32|87*n^2, hence8|n.",
        "sufficiency": "At n=4 all coefficients are integral except p1/2, an integral spin class. At n=8 with f=c/2 every coefficient is an integer on integral characteristic classes.",
        "eightfold_cover_is_intrinsic_after_arbitrary_descent_reallocation": False,
        "phase_field_domain": {
            "nowhere_nonzero_charge_one_root_field_requires": "u=0 as an integral class: its phase is a section trivializing the normal-root line, including its torsion class",
            "general_charge_q_requires": "q*u=0 as an integral class on an everywhere-nonzero patch",
            "mixed_flux_counterexamples_admit_everywhere_nonzero_charge_one_root_field": False,
            "mixed_flux_witnesses_test": "only the extension of the independent periodic functional across arbitrary bundles, hence across normal-root zeros/defects or with extra patching data",
            "four_and_eight_bounds_are_no_go_for_restricted_phase_field_domains": False,
            "S4_half_c2_witness_has_u_zero_and_survives_this_restriction": True,
            "root_zeros_defects_and_patchwise_completion_constructed": False,
        },
    }
    reallocated = {
        "minimum_cover_for_half_c2": 2,
        "normal_root_assumption": "choose a compatible Spin2 root M of N, with u=c1(M) and x=2u; this is not established on the full frozen Gammahat orbibundle",
        "normal_four_form": "c2-p/4-u^2",
        "closed_spin4_period_formula": "integral(c2)-12*k-integral(u^2), where integral(p1)=48*k",
        "closed_spin4_pass": True,
        "same_screen_with_Spin_c11_gauge_bundles_passes": True,
        "reason_quotient_flux_does_not_change_this_screen": "the redistributed normal four-form is independent of f and t; c2(E) remains integral for the U5 reduction",
        "examples": [
            {"background": "S4, c2=1,u=0,p=0", "period": "1"},
            {"background": "K3, c2=0,u=0,p=-48", "period": "12"},
            {"background": "S2xS2, c2=0,u=a+b,p=0", "period": "-2"},
            {"background": "S2xS2 quotient E=L_a+1^4,c=t=a,u=b", "period": "0"},
        ],
        "nonspin_warning": {"test": "CP2 with c2=u=0 and p1=3", "formal_period": "-3/4",
                            "admissible_in_the_stated_Spin4_product_category": False,
                            "obstruction_to_full_Gammahat_claimed": False,
                            "reason": "a generalized nonspin tangential lift needs extra R/flavor data and omitted curvatures; this restricted polynomial cannot decide it"},
        "p1_over4_claimed_integral_in_universal_ordinary_H4_BSpin": False,
        "spin_dependent_gravitational_refinement_needed": True,
        "full_Gammahat_lift_constructed": False,
        "period_screen_is_global_differential_trivialization": False,
    }
    return fixed, reallocated


def su5_exterior_indices():
    roots = (1, 1, 1, 1, -4)
    q2, q3 = sum(z*z for z in roots), sum(z**3 for z in roots)
    rows = []
    for k in range(1, 5):
        weights = [sum(v) for v in combinations(roots, k)]
        ell = sp.Rational(sum(z*z for z in weights), q2)
        anomaly = sp.Rational(sum(z**3 for z in weights), q3)
        if not ell.is_Integer or not anomaly.is_Integer or int(ell-anomaly) % 2:
            raise RuntimeError("SU5 parity generators failed")
        rows.append({"exterior_power": k, "dimension": len(weights), "quadratic_index_ell": int(ell),
                     "cubic_index_A": int(anomaly), "weight_values_on_H": weights})
    return rows


def parity_obstruction():
    return {
        "indices_on_exterior_power_generators": su5_exterior_indices(),
        "normalization": "Tr_R F^2=ell(R)Tr_5 F^2 and Tr_R F^3=A(R)Tr_5 F^3; ell(5)=A(5)=1",
        "all_representation_congruence": "ell(R)=A(R) modulo2 for every finite-dimensional complex SU5 representation",
        "proof": [
            "The four exterior powers of5 have (ell,A)=(1,1),(3,1),(3,-1),(1,-1).",
            "SU5 characters are integral symmetric Laurent polynomials with determinant1, hence integral polynomials in these four exterior-power characters.",
            "Both indices are additive; on a tensor product they obey J(R tensor S)=dim(S)J(R)+dim(R)J(S), since each linear SU5 trace vanishes.",
            "Therefore ell-A remains even under sums, differences and products, proving the congruence on the representation ring, not just a finite scan.",
        ],
        "tangential_assumption": "wall Weyls descend from (Spin4 x Spin2)/<(-1,-1)> with no extra center locking, so every2*qN is odd",
        "kernel_condition": "(-1)_tangent * exp(2*pi*i*qN)=1 for a Weyl field",
        "SU5_cubic_assumption": "sum A(R)=0, including chirality signs; no compensating irreducible SU5 cubic inflow is added",
        "conclusion": "2*sum qN*ell(R)=sum ell(R)=sum A(R)=0 mod2; therefore sum qN*ell(R) is integral, not1/2",
        "fermions_only_cancel_required_half_in_this_structure": False,
        "integer_normal_charges_alone_cancel_required_half": False,
        "no_go_for_every_Gammahat_or_extended_wall_completion": False,
        "single_fundamental_check": {"qN": "1/2", "mixed_x_c2": "-1/2", "SU5_cubic_A": 1,
                                     "cubic_anomaly_free": False},
        "product_lift_escape": "allow mixed parity normal weights on separately chosen Spin4 x Spin2, or construct a different correlated tangential/internal-center lift; neither is inherited here",
    }


def weyl_polynomial(weights, normal_charge):
    return sp.expand(sum((w+normal_charge*x)**3/6-(w+normal_charge*x)*p/24 for w in weights))


def product_wall_module(bare):
    trace = sum(E)
    specs = [
        ("E", list(E), sp.Rational(1, 2), 1),
        ("E_dual", [-e for e in E], sp.Integer(0), 1),
        ("det_E", [trace], sp.Integer(0), 1),
        ("det_E_inverse", [-trace], -sp.Rational(1, 2), 1),
        ("singlet_positive", [sp.Integer(0)], sp.Integer(1), 2),
        ("singlet_negative", [sp.Integer(0)], -sp.Rational(1, 2), 14),
    ]
    rows, total = [], sp.Integer(0)
    components = multiplicities = failing = 0
    for name, weights, q, copies in specs:
        value = weyl_polynomial(weights, q)
        total += copies*value
        parity = (1+int(2*q)) % 2
        rows.append({"representation": name, "weights": [str(w) for w in weights],
                     "copies": copies, "dimension": len(weights), "normal_charge_qN": str(q),
                     "Spin2_integral_weight": int(2*q), "continuous_U1_8_charge": 0,
                     "Spin_c11_gauge_center_even": True,
                     "natural_tangent_normal_diagonal_kernel_exponent_mod2": parity,
                     "one_copy_I6": str(value)})
        components += copies*len(weights)
        multiplicities += copies
        failing += copies*len(weights)*parity
    total = sp.expand(total)
    restriction = sp.expand(bare.subs(f, 0))
    if sp.expand(total+restriction) != 0:
        raise RuntimeError("product-lift wall module does not cancel the full f=0 target")
    trq = sum(copies*len(weights)*q for _, weights, q, copies in specs)
    trq3 = sum(copies*len(weights)*q**3 for _, weights, q, copies in specs)
    cc2 = sum(a*b for a, b in combinations(E, 2))
    spin_form = sp.expand(total.subs(x, 2*u))
    index_line = u**3/6-u*p/24
    index_decomposition = -u*cc2+2*u**3-6*index_line
    if sp.expand(spin_form-index_decomposition) != 0 or (components, multiplicities, failing) != (28, 20, 8):
        raise RuntimeError("wall index quantization or field count changed")
    return {
        "status": "EXACT_CONDITIONAL_PRODUCT_LIFT_NORMAL_SECTOR_WITNESS_NOT_ACCEPTED_WALL",
        "assumed_tangential_group": "separately supplied Spin4 x Spin2 normal cover, together with the U5 reduction of Spin^c11 gauge data",
        "field_blocks": rows, "complex_Weyl_components": components, "irreducible_multiplets_counted_with_copies": multiplicities,
        "minimality_claimed": False,
        "full_wall_polynomial": str(total), "bare_C4_f_zero_polynomial": str(restriction),
        "polynomial_sum": "0", "Tr_normal_Q": str(trq), "Tr_normal_Q3": str(trq3),
        "SU5_and_U5_pure_cubic_gauge_anomalies_cancel": True,
        "mixed_x2_U5_trace_cancels": True,
        "all_f_dependent_anomalies_are_cancelled": False,
        "normal_gauge_gravity_restriction_f_zero_cancelled": True,
        "components_failing_natural_diagonal_spin_kernel": failing,
        "descends_to_natural_Spin4_Spin2_diagonal_quotient": False,
        "descends_to_frozen_Gammahat_with_full_wall_R_data": None,
        "index_integrality_on_closed_spin6": {
            "x_equals_2u_polynomial": str(spin_form),
            "identity": "I6_wall=-u*c2(E)+2*u^3-6*I6_Dirac(L_u)",
            "I6_Dirac_L_u": "u^3/6-u*p1(T)/24",
            "all_periods_integer_in_this_product_spin_category": True,
            "reason": "integral Chern products plus an integer multiple of a twisted spin Dirac index",
            "relative_or_global_anomaly_trivialization_follows": False,
        },
        "new_action_data": ["additional wall fermions and their normal charges", "separate or suitably compensated normal/tangent lift"],
        "unconstructed": ["Gammahat kernel and fixed-wall isotropy for the new fields", "SUSY scalar/R/frame partners and couplings", "masses, decays and cosmology", "f-dependent inflow", "relative WCS/Dai-Freed and global gluing"],
    }


def certificate_content():
    parents = load_parents()
    source = parents["v93_route"]
    calculation = source["bare_bulk_local_anomaly"]["calculation"]
    bare = sp.sympify(calculation["per_stratum"]["z00"]["total"])
    cc2 = sp.expand(sum(a*b for a, b in combinations(E, 2)))
    trace, h2 = sum(E), sum(e**2 for e in E)
    A = sp.cancel((bare-bare.subs(x, 0))/x)
    B = sp.cancel(bare.subs(x, 0)/f)
    A0 = cc2/2-(p+x*x)/8
    moved = -trace+sp.Rational(39, 2)*f-sp.Rational(87, 16)*x
    B0 = sp.expand(B+x*moved)
    Q = sp.expand(2*A0.subs(x, 2*u))
    if sp.expand(A-A0-f*moved) != 0 or sp.expand(bare-x*A0-f*B0) != 0:
        raise RuntimeError("normal/gauge descent reallocation changed the polynomial")
    if sp.expand(bare.subs(x, 2*u)-u*Q-f*B0.subs(x, 2*u)) != 0:
        raise RuntimeError("normal Spin2 root factorization failed")
    if sp.expand(cc2-(trace*trace-h2)/2) != 0:
        raise RuntimeError("U5 Chern-class normalization changed")
    fixed, spin2 = period_certificates()
    return {
        "schema": "v94_normal_wall_quantization_v1",
        "input_core_hashes": {key: core for key, (_, core) in PARENTS.items()},
        "scope": "necessary curvature-period screens and explicit conditional normal-sector alternatives; no full Gammahat or relative quantum wall completion",
        "normal_target_reallocation": {
            "C4_bare_I6": str(bare), "c2_U5_definition": "((sum e_i)^2-sum e_i^2)/2",
            "A4_frozen": str(sp.expand(A)), "B4_frozen": str(sp.expand(B)),
            "A4_reallocated": str(sp.expand(A0)), "B4_reallocated": str(B0),
            "mixed_form_moved_into_gauge_descent": str(moved),
            "Spin2_normal_four_form": str(Q),
            "identity_checks": {"I6_equals_x_A0_plus_f_B0": True,
                                "x_2u_equals_u_Q4_plus_f_B0": True,
                                "normal_reallocation_does_not_change_total_I6": True},
            "normal_and_gauge_currents_fixed_by_this_identity_alone": False,
            "mixed_Bardeen_descent_reallocation_globally_quantized": False,
            "reallocation_is_accepted_counterterm": False,
            "C4_z11": "the same formulas hold with t=e1+e2-e3-e4-e5 and the associated U5 Chern classes",
            "C2_cover": "the f=0 normal restriction vanishes; its mixed f*x^2 term can be assigned wholly to gauge descent, not deleted",
        },
        "normal_root_isotropy": normal_isotropy_certificate(source),
        "fixed_allocation_period_screens": fixed,
        "reallocated_Spin2_period_screen": spin2,
        "wall_fermion_parity_obstruction": parity_obstruction(),
        "conditional_product_lift_wall_module": product_wall_module(bare),
        "terminal_decision": {
            "ordinary_independent_normal_axion_obstruction_sharpened": True,
            "restricted_Spin2_normal_period_screen_passes": True,
            "conditional_product_lift_wall_normal_polynomial_cancellation_found": True,
            "frozen_Gammahat_wall_orbibundle_constructed": False,
            "full_bare_I6_cancelled_on_all_backgrounds": False,
            "normal_lift_or_new_fermions_accepted_as_same_action_physics": False,
            "quantized_relative_WCS_Dai_Freed_trivialization_constructed": False,
            "all_possible_new_boundary_physics_excluded": False,
            "closed_gates": [], "accepted_extensions": 0,
        },
        "primary_sources": [
            {"url": "https://arxiv.org/abs/hep-th/0612212", "use": "Sections3.2-4 require normal-Lorentz anomaly cancellation and allow localized normal-charged matter; local polynomials do not determine global completion."},
            {"url": "https://arxiv.org/abs/1808.01334", "use": "Section2.2 distinguishes local index densities, integral periods and full anomaly field theories; the quaternionic4D spin index is even."},
            {"url": "https://math.berkeley.edu/~teleman/math/RepThry.pdf", "use": "Sections23.6-23.13 describe unitary characters as integral symmetric Laurent polynomials; after det=1, exterior-power generators justify the derived SU5 index parity proof."},
        ],
    }


def build_certificate():
    report = certificate_content()
    report["core_sha256"] = canonical_sha(report)
    return report


def validate_certificate(report):
    if report.get("core_sha256") != canonical_sha(report) or report != build_certificate():
        raise RuntimeError("F94 normal-wall arithmetic, lineage or scope changed")


if __name__ == "__main__":
    print(json.dumps(build_certificate(), indent=2, sort_keys=True))
