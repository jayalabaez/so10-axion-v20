"""F100: a genuine correlated Clifford index quantizes 2P, not P/4.

The category here is the stable continuous central-quotient scout. It is
not an identification of the full physical orbifold background category.
"""
from __future__ import annotations

import copy
from pathlib import Path

import sympy as sp
import susy_v91_multipath_g1_frontier_master_audit as common
import v98_gammahat_compensator_audit as center
import v99_determinant_root_descent_audit as previous

ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v99_route": ("SUSY_V99_QUOTIENT_OBSTRUCTIONS_NORMAL_PAIR_SECTION_AUDIT.json", "240bf71045bda94015027eccbaeebec93fc2caa8940a5dd100e914ad24330c4e"),
    "v99_master": ("SUSY_V99_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json", "72c499490e86c3b9da3e436d95bc6d7b9907806f214ac491be1336b310e2fd39"),
}
x, d, p, r2, h, t = sp.symbols("x d p r2 h t")
SIGMA = (1, 1, 0, 0, 0, 0, 0)
COMPLETED = (1, 1, 0, 1, 0, 0, 0)


def target():
    return d**3+x*d*d/2


def completed_index(n):
    """Degree six Ahat exp(x/2+n*d) ch(R); r2=c2 of formal R roots."""
    z = x/2+n*d
    return sp.expand(z**3/3-z*p/12-z*r2)


def cp3_spin_index(k):
    if type(k) is not int:
        raise ValueError("integral line degree required")
    return sp.Rational(k**3-k, 6)


def cp3_witness(n):
    if type(n) is not int:
        raise ValueError("integral determinant twist required")
    # The total normal-half times R module has honest weights 1,0.
    return cp3_spin_index(n+1)+cp3_spin_index(n)


def stack_row(n):
    if type(n) is not int or n < 1:
        raise ValueError("positive integral stack required")
    value = sp.Rational(3*n, 8)
    return {"multiplicity": n, "CP3_period": str(value),
            "period_mod1": str(value % 1), "quantized_on_stated_category": n % 8 == 0}


def load_inputs():
    parents = {key: common.load_bound(ROOT/name, core) for key, (name, core) in PARENTS.items()}
    route, master = parents["v99_route"], parents["v99_master"]
    if master["input_core_hashes"]["v99_route"] != PARENTS["v99_route"][1]:
        raise RuntimeError("V99 route/master lineage changed")
    if master["next_required_action"]["id"] != "F100_MODIFIED_EQUIVARIANT_ACTION_AND_ORIGINAL_SECTION_EXISTENCE":
        raise RuntimeError("F100 obligation changed")
    saved = route["determinant_root_descent"]
    if saved.get("core_sha256") != common.canonical_sha(saved) or saved != previous.build_certificate():
        raise RuntimeError("frozen V99 center/descent certificate changed")
    for name in ("v99_determinant_root_descent_audit.py", "test_v99_determinant_root_descent_audit.py"):
        if common.file_sha(ROOT/name) != route["artifact_hashes"][name]:
            raise RuntimeError("V99 finite source/test changed: "+name)
    return saved


def content():
    saved = load_inputs()
    old = center.old_kernel()
    if [list(k) for k in old] != saved["inherited_center_and_operator_descent"]["old_kernel"]:
        raise RuntimeError("known center kernel changed")
    checks = {"Sigma": center.character_descent(SIGMA, old),
              "Sigma_tensor_R": center.character_descent(COMPLETED, old)}
    if not any(checks["Sigma"]) or any(checks["Sigma_tensor_R"]):
        raise RuntimeError("R-completed Clifford descent failed")
    endpoint = tuple((a+b) % 2 for a, b in zip(center.KN, center.KS))
    if endpoint != (0, 1, 0, 1, 1, 1, 1) or endpoint not in old:
        raise RuntimeError("CP3 cocharacter does not close in the quotient")
    # Chern-Weil roots of the projective R factor are +/-H/2. Its formal
    # c2 is -H^2/4; it is NOT an ordinary independent SU2 bundle.
    witness_indices = [cp3_witness(n) for n in range(3)]
    for n, index in enumerate(witness_indices):
        polynomial = completed_index(n).subs({x: h, d: h, p: 4*h*h, r2: -h*h/4})
        if sp.expand(polynomial).coeff(h, 3) != index:
            raise RuntimeError("independent CP3 completed index check failed")
    finite_difference = sp.expand(completed_index(2)-2*completed_index(1)+completed_index(0))
    if finite_difference != 2*target() or witness_indices != [0, 1, 5]:
        raise RuntimeError("quotient index quantization failed")
    witness_period = sp.expand(target().subs({x: h, d: h})).coeff(h, 3)/4
    if witness_period != sp.Rational(3, 8):
        raise RuntimeError("primitive eighth-period witness changed")
    return {
        "schema": "v100_correlated_quotient_eighth_period_and_genuine_index_v1",
        "status": "EXACT_ORDER_EIGHT_ON_STATED_CONTINUOUS_SCOUT__GENUINE_2P_RESPONSE__PHYSICAL_GLUE_OPEN",
        "input_core_hashes": {key: value[1] for key, value in PARENTS.items()},
        "category": {
            "name": "Gamma_corr: stable continuous central-quotient scout",
            "cover": "Spin(m)_T x Spin(2)_N x Spin(11) x Sp(1)_R x H3 x H267 x U(1)_gauge",
            "quotient": "K=<D_geom,KT,KS> with the frozen center vectors; tangent projection to SO(m)",
            "flavor_scope": "Use the connected compact flavor factors of the displayed smooth scout, with their central minus identities and symplectic maximal-torus paths. This does not assert that all these independent backgrounds preserve the frozen gauging and square-space-group twists.",
            "normal_and_gauge_lines": "N has Spin(2) covering charge2 and D has U(1)_gauge covering charge2; both are genuine quotient lines",
            "natural_Spin_c_with_determinant_N_required": False,
            "independent_ordinary_SU2_R_bundle_required": False,
            "physical_Gammahat_or_orbifold_category_identified": False,
            "finite_C8_only_bordism_classification": False,
        },
        "genuine_Clifford_module": {
            "coordinate_order": center.OLD_COORDINATES,
            "kernel": [list(k) for k in old], "bare_Sigma_bits": list(SIGMA),
            "Sigma_R_bits": list(COMPLETED), "kernel_exponents": checks,
            "module": "E_n = Sigma_T tensor normal_half_character tensor R_fund tensor D^n",
            "descent": "The TOTAL module, Clifford multiplication and compatible connection descend through every element of K. Sigma and R need not descend separately. D^n is a genuine line for every integral n.",
            "no_rank_one_or_SMW_halving": True,
            "formal_index_JR_n": str(completed_index(sp.Symbol("n"))),
            "formal_R_c2_may_be_fractional": True,
            "virtual_module": "E_2 - 2 E_1 + E_0; equivalently E_0 tensor (D-1)^2",
            "virtual_rank_and_first_Chern_character": [0, 0],
            "degree6_index": str(finite_difference), "equals_twice_P": True,
            "R_curvature_and_p1_cancel_in_this_difference": True,
        },
        "CP3_correlated_witness": {
            "manifold": "CP3, integral H^3=1, w2(T)=0, p1(T)=4H^2",
            "tangent": "the spin structure on CP3, independent of the internal quotient cocharacter",
            "N": "O(1)", "D": "O(1)",
            "cocharacter_lift": "theta -> (1_T, exp(i theta/2)_N, 1_Spin11, diag(exp(i theta/2),exp(-i theta/2))_R, identical half-angle symplectic-torus paths in H3,H267, exp(i theta/2)_gauge)",
            "lift_endpoint_at_2pi": list(endpoint), "endpoint_kernel_word": "KN+KS",
            "construction": "The path is a one-parameter subgroup with endpoint in K, hence defines U1 -> Gamma_corr. Extend the principal U1 bundle of O(1) by this map and combine with the tangent spin structure. No separate square root of O(1) is asserted.",
            "not_an_independent_Spin_c11_gauge_factor": "KT projects to (z11,1) rather than the identity of the isolated (Spin11 x U1)/KS factor. Gamma_corr therefore has no projection obtained by simply forgetting the other factors into that isolated gauge group. Trivial SO11 with odd D is allowed here by the KN+KS correlation; it is not asserted to satisfy a separate Spin-c11 bundle relation.",
            "projective_R_formal_roots": ["H/2", "-H/2"],
            "total_normal_half_R_weights": [1, 0],
            "total_E_n_on_spin_CP3": "Sigma_spin tensor (O(n+1) + O(n))",
            "independent_spin_index_formula": "index_spin O(k)=(k^3-k)/6=chi O(k-2)",
            "indices_E0_E1_E2": [int(q) for q in witness_indices],
            "virtual_index": int(witness_indices[2]-2*witness_indices[1]+witness_indices[0]),
            "P_period": "3/2", "P_over4_period": str(witness_period),
            "natural_Spin_c_N_admissible": False,
            "why_old_restricted_index_cannot_be_used": "Here w2(T)=0 but x=H modulo2. Internal R/flavor cocycles compensate the normal lift; a bare natural Spin-c operator with determinant N does not exist.",
            "is_a_frozen_orbifold_background": False,
        },
        "exact_quantization": {
            "target_Q": str(target()/4),
            "all_Q_periods_in_one_eighth_integers": True,
            "sufficiency": "8Q=2P is the integer index of the displayed genuine virtual Clifford module on every closed6 Gamma_corr background.",
            "necessity": "CP3 gives Q=3/8, so any integer stack n requires 8 to divide n since gcd(3,8)=1.",
            "minimum_positive_stack": 8,
            "closed5_positive_2P_response": "exp(2*pi*i*(xi_Gamma(Y,E_2)-2*xi_Gamma(Y,E_1)+xi_Gamma(Y,E_0)))",
            "xi_definition": "xi=(eta+dim(kernel))/2 for the genuine complex self-adjoint Dirac operator",
            "nonbounding_definition": "Integer reduced-eta levels define this closed5 phase without a chosen filling; APS gives curvature 2P and integer filling changes.",
            "closed6_obstruction_character_for_Q": "exp(2*pi*i*index(E_2-2E_1+E_0)/8)",
            "closed6_character_exact_order": 8,
            "additional_flat_closed5_factor_repairs_nonintegral_filling_period": False,
            "all_positive_stacks": [stack_row(n) for n in range(1, 17)],
            "single_Q_absolute_response_exists_on_all_stated_backgrounds": False,
            "response_is_new_particle_spectrum": False,
            "independent_boundary_corner_trivializations_constructed": False,
        },
        "relation_to_previous_results": {
            "V98_quantization_with_chosen_root_retracted": False,
            "V99_natural_normal_order_two_retracted": False,
            "different_polynomial_from_normal_T": True,
            "why_order_eight_does_not_contradict_chosen_root": "Chosen-root natural Spin-c backgrounds are a smaller category. The CP3 witness has neither natural determinant N nor an ordinary square root of D.",
            "eightfold_index_is_a_descent_of_the_specific_V98_eta_plus_cup": False,
            "scope_of_obstruction": "No absolute Q counterterm on all Gamma_corr smooth backgrounds. This does not forbid a relative bulk theory carrying the opposite anomaly, a restricted physical category, or additional sectors.",
        },
        "terminal_decision": {
            "genuine_same_quotient_response_for_eightfold_target_constructed": True,
            "single_local_P_over4_repair_accepted": False,
            "physical_full_anomaly_cancelled": False,
            "microscopic_SUSY_action_constructed": False,
            "full_relative_Gammahat_action_constructed": False,
            "closed_gates": [],
        },
        "primary_sources": [
            {"url": "https://web.math.ucsb.edu/~dai/book.pdf", "use": "Theorem3.4.2 gives the index of a genuine Clifford module even without a separate spinor-times-vector-bundle factorization. Applied to the explicitly descended total module, it proves the derived 2P identity and its integral periods."},
            {"url": "https://arxiv.org/abs/hep-th/9405012", "use": "Kernel-inclusive reduced eta phases and APS determinant-line formalism define integer-level closed5 responses; boundary trivializations are separate data."},
            {"url": "https://arxiv.org/abs/1810.00844", "use": "Correlated spin/internal structures illustrate why separately projective factors can define genuine fermions. The particular Gamma_corr cocharacter and eighth-period theorem are derived here, not asserted by this source."},
            {"url": "https://stacks.math.columbia.edu/tag/01XS", "use": "Projective-space line-bundle cohomology independently checks the CP3 spin Dirac index via chi(O(k-2))."},
        ],
    }


def build_certificate():
    out = content()
    out["core_sha256"] = common.canonical_sha(out)
    return out


def validate_certificate(out):
    if out.get("core_sha256") != common.canonical_sha(out):
        raise RuntimeError("noncanonical F100 correlated-period certificate")
    body = copy.deepcopy(out)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("F100 correlated-period derivation, scope or lineage changed")
