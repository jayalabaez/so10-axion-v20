"""F99: exact order of the natural Spin-c normal obstruction and shared pairing.

This constructs restricted closed-five-dimensional responses. It neither
splits a correlated response between independent walls nor descends its bare
Spin-c Dirac operators through the full frozen internal/tangential quotient.
"""
from __future__ import annotations

import copy
from pathlib import Path

import sympy as sp
import susy_v91_multipath_g1_frontier_master_audit as common
import v98_common_response_bordism_audit as previous

ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v98_route": ("SUSY_V98_GEOMETRIC_DESCENT_RESPONSE_AND_SECTION_AUDIT.json", "6cd7985cd073e6db6ab27ad3e1b22b312bd966696b8aba30e6f76c9735139767"),
    "v98_master": ("SUSY_V98_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json", "a1032f9531a12a91bfeb1ba0c13fb3e7703a60a70982f65e7122d237c11083cf"),
}
x, p, e2, a, b, A2, B2, h, j, c = sp.symbols("x p e2 a b A2 B2 h j c")


def spin_c_index(z):
    return sp.expand((z+x/2)**3/6-(z+x/2)*p/24)


def normal_target(second=e2):
    return sp.expand(-x*second/2+x**3/8+x*p/8)


def cp2_cp1_period(expression, normal_h=1, normal_j=2, second=0):
    if any(type(v) is not int for v in (normal_h, normal_j)):
        raise ValueError("integral determinant coefficients required")
    if normal_h % 2 != 1 or normal_j % 2 != 0:
        raise ValueError("determinant must reduce to w2=h modulo two")
    value = sp.expand(expression.subs({x: normal_h*h+normal_j*j, p: 3*h*h, e2: second}))
    return sp.Poly(value, h, j).coeff_monomial(h*h*j)


def multiplicity_row(n):
    if type(n) is not int or n < 1:
        raise ValueError("positive integral stack multiplicity required")
    period = n*cp2_cp1_period(normal_target())
    return {"multiplicity": n, "witness_period": str(period),
            "all_natural_Spin_c_periods_integral": n % 2 == 0,
            "witness_phase": "+1" if period.is_Integer else "-1"}


def load_inputs():
    inputs = {key: common.load_bound(ROOT/name, core) for key, (name, core) in PARENTS.items()}
    route, master = inputs["v98_route"], inputs["v98_master"]
    if master["input_core_hashes"]["v98_route"] != PARENTS["v98_route"][1]:
        raise RuntimeError("V98 route/master lineage changed")
    if master["next_required_action"]["id"] != "F99_SPECTATOR_OR_SPINC_INFLOW_AND_ORIGINAL_SECTION_ELIMINATION":
        raise RuntimeError("F99 obligation changed")
    saved = route["common_response_bordism"]
    if saved.get("core_sha256") != common.canonical_sha(saved) or saved != previous.build_certificate():
        raise RuntimeError("V98 response certificate changed")
    for name in ("v98_common_response_bordism_audit.py", "test_v98_common_response_bordism_audit.py"):
        if common.file_sha(ROOT/name) != route["artifact_hashes"][name]:
            raise RuntimeError("V98 response source/test changed: "+name)
    if saved["natural_Spin_c_determinant_root_response"]["distinct_V96_normal_repair_half_period"]["old_target_period"] != "3/2":
        raise RuntimeError("the distinct normal half-period was lost")
    geometric = route["gammahat_compensator"]["unchanged_geometric_kernel_obstruction"]
    return saved, geometric


def content():
    saved, geometric = load_inputs()
    # Tensoring a natural Spin-c spinor by N changes its normal-root
    # charge by two, hence both eta operators have this same center parity.
    eta_bits = [1, 1, 0, 0, 0, 0, 0]
    eta_checks = {key: sum(v*w for v, w in zip(eta_bits, value)) % 2
                  for key, value in geometric["generators"].items()}
    if eta_checks != {"D_geom": 0, "krot_N": 1, "krot_T": 1, "kspin": 0}:
        raise RuntimeError("the bare natural Spin-c operator quotient obstruction changed")
    J0, JN = spin_c_index(0), spin_c_index(x)
    doubled = sp.expand(JN-15*J0-x*e2)
    cubic = sp.expand(JN-3*J0)
    if sp.expand(doubled-2*normal_target()) != 0 or cubic != x**3/2:
        raise RuntimeError("normal Spin-c index decomposition failed")
    # This also proves integral(x^3)/2 is integral, without assuming that
    # x^3/2 is an integral ordinary cohomology class on the classifying space.
    parity_index = sp.expand(JN-15*J0-x*e2)
    parity_characteristic = x**3/2-x*e2
    if sp.expand(parity_index-parity_characteristic) != -12*J0:
        raise RuntimeError("normal obstruction parity identity failed")
    examples = []
    for nh, nj in ((1, 0), (1, 2), (3, 2), (-1, 2), (1, -2), (5, 4)):
        i0, iN = (cp2_cp1_period(z, nh, nj) for z in (J0, JN))
        period = cp2_cp1_period(normal_target(), nh, nj)
        # Holomorphic Euler characteristic of O(k,l) on CP2 x CP1.
        twist_h, twist_j = (nh-3)//2, (nj-2)//2
        chi = lambda k, l: sp.Rational((k+1)*(k+2)*(l+1), 2)
        if [i0, iN] != [chi(twist_h, twist_j), chi(twist_h+nh, twist_j+nj)]:
            raise RuntimeError("independent holomorphic normal-index check failed")
        examples.append({"x_h": nh, "x_j": nj, "J_1": int(i0), "J_N": int(iN),
                         "normal_target_period": str(period), "obstruction_parity": int((2*period) % 2)})
    # A genuine rank-five split U(5) bundle can change the obstruction sign.
    # E=O(h) + O(j) + 1^3 has c2=h*j, not a fictional arbitrary second class.
    split_second = h*j
    split_period = cp2_cp1_period(normal_target(), second=split_second)
    if split_period != 1:
        raise RuntimeError("the independent gauge/normal half-period mixing changed")
    reflected0, reflected1 = A2+B2+a*b, A2+B2-a*b
    pair = sp.expand(normal_target(reflected0)+normal_target(reflected1))
    pair_response = sp.expand(JN-15*J0-x*(A2+B2))
    if sp.expand(pair-pair_response) != 0:
        raise RuntimeError("reflected U5 common normal-pair response failed")
    quarter = sp.sympify(saved["natural_Spin_c_determinant_root_response"]["target_P_over4_with_D_C_squared"])
    return {
        "schema": "v99_normal_half_period_order_and_shared_pair_response_v1",
        "status": "NORMAL_OBSTRUCTION_EXACTLY_ORDER_TWO__SHARED_REFLECTED_PAIR_QUANTIZED__INDEPENDENT_WALL_GLUE_OPEN",
        "input_core_hashes": {key: value[1] for key, value in PARENTS.items()},
        "restricted_category": {
            "tangent": "natural Spin-c with determinant genuine normal line N, x=c1(N)",
            "gauge": "independent genuine U5 bundle E; shared pair uses U2 bundle A and U3 bundle B",
            "normal_root_M_assumed": False,
            "full_frozen_Gammahat_category_identified": False,
            "target_scope": "V96 f=0, independent internal R/flavor curvature zero normal/gauge/gravity slice only",
        },
        "exact_normal_period_lattice": {
            "target_T": str(normal_target()), "J_1": str(J0), "J_N": str(JN),
            "twice_T_index_and_cup": str(doubled), "identity_residual": str(sp.expand(doubled-2*normal_target())),
            "twice_T_eta_integer_levels": {"N": 1, "1": -15},
            "twice_T_integral_cup": "-x*c2(E)",
            "twice_T_closed5_positive_response": "exp(2*pi*i*(xi_c(Y,N)-15*xi_c(Y,1)-hol_Y(x_hat cup c2hat(E))))",
            "xi_definition": "xi_c=(eta_c+dim(kernel))/2 of the genuine Spin-c Dirac operator, twisted by the indicated line",
            "nonbounding_closed5_definition": "integer reduced-eta levels and integral differential cup holonomy require no chosen filling; APS gives curvature 2T and integral filling changes",
            "all_T_periods_in_half_integers": True,
            "minimum_positive_stack_for_quantization_on_this_category": 2,
            "all_positive_stacks_classified": "Every even stack is a power of the displayed 2T response; every odd stack fails the CP2 x CP1 period 3/2 test.",
            "sample_stacks": [multiplicity_row(n) for n in range(1, 9)],
            "T_has_absolute_closed5_response_on_all_these_backgrounds": False,
        },
        "closed6_order_two_obstruction": {
            "phase": "(-1)^(index_c(N)-15*index_c(1)-integral(x*c2(E)))",
            "equivalent_parity": "integral(x^3)/2-integral(x*c2(E)) modulo2",
            "index_proof_x_cube_half_integral": "integral(x^3)/2=index_c(N)-3*index_c(1)",
            "difference_of_parity_formulas": str(sp.expand(parity_index-parity_characteristic)),
            "difference_is_even_integer": "-12*index_c(1)",
            "x_cubed_half_is_claimed_integral_universal_cohomology_class": False,
            "closed6_character_is_bordism_invariant": True,
            "exact_order": 2,
            "CP2_CP1_E_trivial_witness": {"x": "h+2*j", "p1": "3*h^2", "J_1": 0, "J_N": 3,
                                          "T_period": "3/2", "phase": "-1"},
            "independent_holomorphic_checks": examples,
            "genuine_nontrivial_E_example": {"E": "O(h)+O(j)+1^3", "c2": "h*j", "x": "h+2*j",
                                             "T_period": str(split_period), "phase": "+1"},
            "a_flat_closed5_factor_can_repair_this_filling_period": False,
            "relative_interpretation": "A proposed half-response would need a trivialization of this nontrivial closed6 obstruction, or a genuinely coupled relative theory with that anomaly. Naming the sign is not such a trivialization.",
            "relative_bulk_boundary_theory_constructed": False,
        },
        "shared_reflected_U5_pair": {
            "common_background": "one closed Spin-c Y5 with one N and genuine A(U2),B(U3); E0=A+B, E1=A+B*",
            "c2_E0": str(reflected0), "c2_E1": str(reflected1),
            "sum_c2": str(sp.expand(reflected0+reflected1)),
            "target_T0_plus_T1": str(pair),
            "integer_eta_levels": {"N": 1, "1": -15},
            "integral_cup": "-x*(c2(A)+c2(B))",
            "response": "exp(2*pi*i*(xi_c(Y,N)-15*xi_c(Y,1)-hol_Y(x_hat cup (c2hat(A)+c2hat(B)))))",
            "exact_identity_residual": str(sp.expand(pair-pair_response)),
            "quantized_on_all_stated_common_closed5_backgrounds": True,
            "obstruction_character_product_on_shared_closed6": "+1",
            "CP2_CP1_trivial_A_B_pair_period": "3",
            "independent_endpoint_counterexample": "Give endpoint0 the CP2 x CP1 witness and endpoint1 the trivial bordism: the product obstruction is -1. Restriction to common data does not trivialize the external product on independent data.",
            "independent_endpoint_obstruction_phase": "-1",
            "factors_into_two_absolute_natural_Spin_c_T_responses": False,
            "bare_Spin_c_eta_operators_descend_through_full_internal_kernel": False,
            "bare_eta_center_bits": eta_bits,
            "bare_eta_known_kernel_exponents": eta_checks,
            "operator_scope": "Both individual eta operators fail the internal/tangential krot relations. This alone is not a theorem excluding every combined invertible response or correlated relative completion.",
            "actual_orbifold_relative_gluing_constructed": False,
            "common_response_is_new_particles_or_SUSY_multiplets": False,
        },
        "separate_obstructions_retained": {
            "V98_gauge_quarter_response": str(quarter),
            "gauge_quarter_at_C_trivial": str(sp.expand(quarter.subs(c, 0))),
            "gauge_quarter_removes_normal_half_period": False,
            "ordinary_spin_product_SU2_normal_doublet_phase": saved["SU2_flat_refinement"]["V97_added_normal_doublet_phase_on_generator"],
            "two_normal_doublets_on_shared_R_have_product_phase": "+1",
            "independent_R_endpoint_test_product_phase": "-1",
            "normal_pair_quantization_determines_full_parent_SU2_or_defect_phase": False,
            "bare_parent_R_phase_computed": False,
            "finite_CS_ABK_and_corner_data_completed": False,
        },
        "terminal_decision": {
            "normal_obstruction_order_classified_on_natural_Spin_c_category": True,
            "quantized_shared_normal_pair_response_constructed": True,
            "independent_local_normal_repair_accepted": False,
            "full_quantum_Gammahat_parent_accepted": False,
            "same_action_microscopic_inflow_constructed": False,
            "closed_gates": [],
        },
        "primary_sources": [
            {"url": "https://web.math.ucsb.edu/~dai/book.pdf", "use": "Section2.3 defines the Spin-c determinant and the end of Section3.3 gives the integral twisted Spin-c index. The new exact order-two and reflected-pair identities are derived here."},
            {"url": "https://arxiv.org/abs/hep-th/9405012", "use": "Kernel-inclusive reduced eta invariants and determinant-line gluing; defining a closed5 response is not a boundary trivialization."},
            {"url": "https://arxiv.org/abs/1207.5449", "use": "Integral differential cup-product Chern-Simons holonomy supplies the genuine mixed x*c2 term, including nonbounding closed5 backgrounds."},
            {"url": "https://arxiv.org/abs/1810.00844", "use": "Periodic-circle SU2 instanton and mod-two anomaly context. The previously frozen normal-doublet sign is retained, not recomputed as a full Gammahat anomaly."},
        ],
    }


def build_certificate():
    out = content()
    out["core_sha256"] = common.canonical_sha(out)
    return out


def validate_certificate(out):
    if out.get("core_sha256") != common.canonical_sha(out):
        raise RuntimeError("noncanonical F99 normal-pair certificate")
    body = copy.deepcopy(out)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("F99 normal pairing arithmetic, scope or lineage changed")
