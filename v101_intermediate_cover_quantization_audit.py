"""F101: exact P/4 period lattices on all five specified central covers.

This classifies smooth response levels on named scout categories, not the
allowed backgrounds or anomaly cancellation of a complete physical action.
"""
from __future__ import annotations

import copy
from pathlib import Path

import sympy as sp
import susy_v91_multipath_g1_frontier_master_audit as common
import v100_correlated_quotient_period_audit as previous
import v100_modified_equivariant_cover_audit as covers

ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v100_route": ("SUSY_V100_CORRELATED_QUANTIZATION_MODIFIED_ACTION_SECTION_AUDIT.json", "804242337e0681fe39a84891badd9545447b7f980794366da6a45d4f3277018a"),
    "v100_master": ("SUSY_V100_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json", "5727d33c6678cdf23539387e20b2a3cae2ab92095723adfb2a368c7fd2d75a24"),
}
x, d, c, ell, p, r2 = sp.symbols("x d c ell p r2")
IDS = ("old", "gauge_root", "natural_spin_c", "diagonal", "combined")


def Q(normal=x, determinant=d):
    return sp.expand(determinant**3/4+normal*determinant**2/8)


def J(twist, normal=x, with_R=False):
    total = twist+normal/2
    bare = total**3/6-total*p/24
    return sp.expand(2*bare-total*r2 if with_R else bare)


def index_difference(line, with_R=False):
    return sp.expand(J(2*line, with_R=with_R)-2*J(line, with_R=with_R)+J(0, with_R=with_R))


def kernels():
    D, KT, KS = covers.D, covers.KT, covers.KS
    diagonal = tuple((a+b) % 2 for a, b in zip(KT, KS))
    return dict(zip(IDS, (covers.lift.span((D, KT, KS)), covers.lift.span((D, KT)),
                          covers.lift.span((D, KS)), covers.lift.span((D, diagonal)), covers.lift.span((D,)))))


def load_inputs():
    parents = {key: common.load_bound(ROOT/name, core) for key, (name, core) in PARENTS.items()}
    route, master = parents["v100_route"], parents["v100_master"]
    if master["input_core_hashes"]["v100_route"] != PARENTS["v100_route"][1]:
        raise RuntimeError("V100 route/master edge changed")
    if master["next_required_action"]["id"] != "F101_PHYSICAL_BACKGROUND_RESTRICTION_RELATIVE_ACTION_AND_SECTION_SOLVABILITY":
        raise RuntimeError("F101 obligation changed")
    for key, module in (("correlated_quotient_period", previous), ("modified_equivariant_cover", covers)):
        saved = route[key]
        if saved.get("core_sha256") != common.canonical_sha(saved) or saved != module.build_certificate():
            raise RuntimeError("frozen V100 derivation changed: "+key)
        for name in (module.__name__+".py", "test_"+module.__name__+".py"):
            if common.file_sha(ROOT/name) != route["artifact_hashes"][name]:
                raise RuntimeError("frozen V100 source/test changed: "+name)
    return route


def cp3_witness(identifier):
    if identifier not in IDS:
        raise ValueError("unknown intermediate cover")
    # Entries: degree N, degree D, Spin11 central endpoint, R/flavor endpoint.
    data = {"old": (-1, 1, 0, 1), "gauge_root": (-3, 2, 1, 1),
            "natural_spin_c": (0, 1, 1, 0), "diagonal": (-1, 1, 0, 1), "combined": (-2, 2, 0, 0)}
    nx, dd, spin, rr = data[identifier]
    endpoint = (0, nx % 2, spin, rr, rr, rr, dd % 2)
    if endpoint not in kernels()[identifier]:
        raise RuntimeError("the CP3 cocharacter fails to close in its stated cover")
    twist_degree = dd//2 if identifier in ("gauge_root", "combined") else dd
    with_R = identifier in ("old", "gauge_root", "diagonal")
    base_weights = [sp.Rational(nx+rr, 2), sp.Rational(nx-rr, 2)] if with_R else [sp.Rational(nx, 2)]
    if any(not k.is_Integer for k in base_weights):
        raise RuntimeError("total Clifford weights must be integral on spin CP3")
    indices = [sum(previous.cp3_spin_index(int(k+n*twist_degree)) for k in base_weights) for n in range(3)]
    for n, index in enumerate(indices):
        polynomial_index = J(n*twist_degree, normal=sp.Integer(nx), with_R=with_R).subs({p: 4, r2: -sp.Rational(rr, 4)})
        if polynomial_index != index:
            raise RuntimeError("independent CP3 holomorphic/index computation disagrees")
    period = Q(sp.Integer(nx), sp.Integer(dd))
    return {
        "manifold": "spin CP3; integral H^3=1 and p1=4H^2",
        "N_degree": nx, "D_degree": dd,
        "cocharacter_endpoint": list(endpoint),
        "endpoint_in_stated_kernel": True,
        "cocharacter": "Tangent spin structure is separate. Normal and gauge paths have weights N_degree/2 and D_degree/2. Spin11 uses the plane spin path ending at its central minus identity iff its endpoint bit is 1. R,H3,H267 use half-angle symplectic Cartan paths iff their endpoint bits are 1. Extend the O(1) principal U1 bundle through this closed quotient cocharacter.",
        "Spin11_path_endpoint_bit": spin, "R_H3_H267_path_endpoint_bit": rr,
        "total_Clifford_base_line_degrees": [int(k) for k in base_weights],
        "index_twist_line_degree": twist_degree, "R_completed_index_used": with_R,
        "indices_at_powers_0_1_2": [int(k) for k in indices],
        "index_finite_difference": int(indices[2]-2*indices[1]+indices[0]),
        "Q_period": str(period), "period_numerator": int(sp.numer(period)), "period_denominator": int(sp.denom(period)),
        "projective_internal_factors_claimed_separately_genuine": False,
        "actual_physical_or_Higgs_background_admissibility_proved": False,
    }


def classification_rows():
    group_kernels = kernels()
    sigma_C = tuple((a+b) % 2 for a, b in zip(covers.SIGMA, covers.CCHAR))
    rows = []
    for identifier in IDS:
        kernel = group_kernels[identifier]
        witness = cp3_witness(identifier)
        level = witness["period_denominator"]
        if witness["period_numerator"] != 1:
            raise RuntimeError("a primitive positive period witness is required")
        root_line = identifier in ("gauge_root", "combined")
        target = Q(determinant=2*c) if root_line else Q()
        if identifier in ("old", "diagonal"):
            density = 2*d**3+x*d*d
            response = "exp(2*pi*i*hol(2*d_hat^3+x_hat*d_hat^2))"
            proof = "N and D are genuine lines. The displayed degree-six integral differential cup polynomial defines an absolute closed5 response for 8Q, even on oriented backgrounds with these lines and without a separate spinor factor."
            alternative = index_difference(d, with_R=True)
        elif identifier == "gauge_root":
            density = 4*c**3+x*c*c
            response = "exp(2*pi*i*hol(4*c_hat^3+x_hat*c_hat^2))"
            proof = "C and N are genuine lines; the integral differential cup polynomial defines a closed5 response for 2Q. No bare natural Spin-c spinor is assumed."
            alternative = index_difference(c, with_R=True)+2*c**3
        elif identifier == "natural_spin_c":
            density = index_difference(d)
            response = "exp(2*pi*i*(xi_Sigma(D^2)-2*xi_Sigma(D)+xi_Sigma(1)))"
            proof = "The genuine natural Spin-c module Sigma has determinant N. The virtual index of Sigma tensor (D-1)^2 equals P=4Q. Integer reduced-eta levels define its closed5 response."
            alternative = density
        else:
            density = index_difference(c)+c**3
            response = "exp(2*pi*i*(xi_Sigma(C^2)-2*xi_Sigma(C)+xi_Sigma(1)+hol(c_hat^3)))"
            proof = "Both Sigma and C are genuine; the V100 integer eta-plus-cup construction quantizes a single Q."
            alternative = density
        if sp.expand(density-level*target) != 0 or sp.expand(alternative-density) != 0:
            raise RuntimeError("the claimed response level does not have the target curvature")
        rows.append({
            "id": identifier, "kernel": [list(k) for k in kernel], "cover_degree_over_old": 8//len(kernel),
            "C_genuine": not any(covers.lift.character_descent(covers.CCHAR, kernel)),
            "Sigma_N_genuine": not any(covers.lift.character_descent(covers.SIGMA, kernel)),
            "Sigma_C_with_determinant_ND_genuine": not any(covers.lift.character_descent(sigma_C, kernel)),
            "Sigma_R_genuine": not any(covers.lift.character_descent(previous.COMPLETED, kernel)),
            "Q_in_genuine_line_coordinates": str(target),
            "exact_period_lattice": "(1/"+str(level)+") Z", "minimum_positive_integer_stack": level,
            "primitive_CP3_witness": witness,
            "quantized_level_density": str(sp.expand(density)), "positive_closed5_response": response,
            "sufficiency_proof": proof,
            "necessity_proof": "The displayed closed6 background has Q period 1/"+str(level)+". A positive stack n can be an absolute response on every background in this category only if n is divisible by "+str(level)+". Powers of the given response establish sufficiency.",
            "period_lattice_exactness": "All periods lie in this lattice by the response/index proof; disjoint unions and orientation reversals of the primitive witness realize the entire additive lattice.",
            "alternative_index_plus_cup_density": str(sp.expand(alternative)),
            "matching_curvature_claims_full_phase_equality": False,
            "any_flat_bordism_difference_between_choices_computed": False,
        })
    if [row["minimum_positive_integer_stack"] for row in rows] != [8, 2, 4, 8, 1]:
        raise RuntimeError("the five-cover period classification changed")
    return rows


def content():
    parent = load_inputs()
    rows = classification_rows()
    saved = parent["modified_equivariant_cover"]["minimal_combined_operator_cover"]["all_five_intermediate_covers_preserving_D_geom"]
    if {tuple(map(tuple, row["kernel"])) for row in rows} != {tuple(map(tuple, row["kernel"])) for row in saved}:
        raise RuntimeError("the classification must cover all and only the five inherited covers")
    diagonal = sp.expand(Q().subs(x, ell-d))
    if diagonal != (d**3+ell*d*d)/8:
        raise RuntimeError("the diagonal Spin-c determinant formula changed")
    return {
        "schema": "v101_five_intermediate_cover_exact_response_period_lattices_v1",
        "status": "EXACT_SMOOTH_LEVELS_8_2_4_8_1__NO_PHYSICAL_BACKGROUND_OR_RELATIVE_COMPLETION_CLAIM",
        "input_core_hashes": {key: value[1] for key, value in PARENTS.items()},
        "category_scope": {
            "cover": parent["correlated_quotient_period"]["category"]["cover"],
            "definition": "Stable smooth scout tangential categories obtained by quotienting this product cover by each subgroup J with <D_geom> contained in J contained in K. Connected compact R/flavor Cartans are retained exactly as in V100.",
            "classification_of_all_possible_symmetry_groups": False,
            "physical_orbifold_or_Higgs_background_category_identified": False,
            "ordinary_Spin_c11_gauge_factor_independent_of_other_factors_assumed": False,
            "finite_C8_only_torsion_anomaly_classification": False,
        },
        "target_Q": str(Q()), "cover_order": list(IDS), "classification": rows,
        "diagonal_cover_analysis": {
            "kernel": "<D_geom,KT+KS>", "genuine_module": "Sigma_C = Sigma_T tensor normal-half tensor gauge-half",
            "Spin_c_determinant": "L=N tensor D; ell=x+d", "Q_in_ell_d": str(diagonal),
            "bare_Sigma_and_C_need_not_exist_separately": True,
            "CP3_L": "O(0)", "CP3_D": "O(1)", "CP3_Q_period": "1/8",
            "minimum_positive_stack_despite_genuine_Spin_c_module": 8,
            "passing_V100_diagonal_deck_product_test_proves_global_extension": False,
            "why_product_test_is_insufficient": "V100 tested a liftable CP2 x S1 family. The present CP3 background is an honest diagonal-cover bundle with odd D and no C root, and excludes any absolute single-Q extension to all diagonal-cover backgrounds.",
            "root_independence_on_every_liftable_subcategory_decided": False,
        },
        "response_scope": {
            "xi": "xi=(eta+dim(kernel))/2 of the full genuine complex Dirac operator; no SMW/Pfaffian halving is used",
            "nonbounding_closed5": "Integer eta levels and integral differential cup holonomies are defined without a chosen filling; their bounding formulas have integral filling changes.",
            "eightfold_response_requires_new_particles_or_R_doublet_in_spectrum": False,
            "eightfold_integral_cup_response_exists_without_a_spin_structure": True,
            "pure_cup_and_index_responses_with_equal_curvature_proved_identical": False,
            "full_torsion_phase_difference_classified": False,
            "closed_boundary_corner_Dai_Freed_trivializations_constructed": False,
            "single_target_can_be_replaced_by_multiple_stack_without_action_change": False,
        },
        "terminal_decision": {
            "all_five_smooth_scout_period_lattices_classified": True,
            "only_combined_cover_has_single_Q_on_all_its_stated_smooth_backgrounds": True,
            "compatibility_with_frozen_space_group_inferred_from_quantization": False,
            "full_physical_anomaly_cancelled": False, "microscopic_parent_accepted": False,
            "theory_complete": False, "closed_gates": [],
        },
        "primary_sources": [
            {"url": "https://web.math.ucsb.edu/~dai/book.pdf", "use": "The twisted Spin-c index and Clifford-module index justify the genuine-module integer response levels. The five kernels, primitive CP3 cocharacters and their exact period lattices are derived in this audit."},
            {"url": "https://arxiv.org/abs/hep-th/9405012", "use": "Kernel-inclusive reduced eta invariants define the integer-level closed5 phases; a boundary determinant-line trivialization is additional data."},
            {"url": "https://math.mit.edu/juvitop/pastseminars/notes_2019_Fall/cheeger-simons.pdf", "use": "Integral differential-character products give closed5 cup holonomies with the displayed integral characteristic curvatures. Equal curvature alone does not establish equality with an eta refinement."},
            {"url": "https://stacks.math.columbia.edu/tag/01XS", "use": "The CP3 line-bundle Euler characteristic independently gives index_spin O(k)=(k^3-k)/6 via chi O(k-2); negative indices are indices, not negative kernel dimensions."},
        ],
    }


def build_certificate():
    out = content()
    out["core_sha256"] = common.canonical_sha(out)
    return out


def validate_certificate(out):
    if out.get("core_sha256") != common.canonical_sha(out):
        raise RuntimeError("noncanonical F101 cover-period certificate")
    body = copy.deepcopy(out)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("F101 cover periods, lineage or scope changed")
