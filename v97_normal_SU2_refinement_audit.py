"""F97: a nonabelian normal/R scout and its indispensable flat Z2 factor.

All statements concern an explicit ordinary-spin product background category.
They do not construct supersymmetric wall matter or a full Gammahat action.
"""
from __future__ import annotations

import copy
from itertools import product
from pathlib import Path

import sympy as sp
import susy_v91_multipath_g1_frontier_master_audit as common
import v95_wall_symmetry_lift_audit as kernel

ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v96_route": ("SUSY_V96_QUANTIZED_RESPONSES_AND_SECTION_FRONTIER_AUDIT.json", "2c1575f64d2aa3414e6b504d72c20a9a76160825aac7389259ac26402ab8f215"),
    "v96_master": ("SUSY_V96_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json", "d8328579f5162e59a855336aa66bff8ca180f1d7062bb066ee241bbed99503b2"),
}
u, y, p, e2, r2, t, e3 = sp.symbols("u y p e2 r2 t e3")


def line_index(c):
    return sp.expand(c**3/6-c*p/24)


def su2_weights(highest):
    if type(highest) is not int or highest < 0:
        raise ValueError("nonnegative integral highest weight required")
    return list(range(highest, -highest-1, -2))


def su2_index(normal_weight, highest):
    if type(normal_weight) is not int:
        raise ValueError("integral normal-root weight required")
    cartan = sp.expand(sum(line_index(normal_weight*u+w*y) for w in su2_weights(highest)))
    if cartan.subs(y, -y) != cartan:
        raise RuntimeError("a complete SU2 character must be Weyl invariant")
    return sp.expand(cartan.subs(y*y, -r2))


def dynkin_index_twice(highest):
    """Instanton index normalized to one for a single SU2 doublet."""
    return sum(w*w for w in su2_weights(highest))//2


def rank_mod2(matrix):
    rows = [[int(v) % 2 for v in row] for row in matrix]
    if not rows:
        return 0
    pivot = 0
    for col in range(len(rows[0])):
        found = next((i for i in range(pivot, len(rows)) if rows[i][col]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        for i in range(len(rows)):
            if i != pivot and rows[i][col]:
                rows[i] = [(a+b) % 2 for a, b in zip(rows[i], rows[pivot])]
        pivot += 1
        if pivot == len(rows):
            break
    return pivot


def product_bordism():
    # Integral cohomology is torsion-free and even. Sq1 therefore vanishes.
    degree2 = [u, t]
    degree4 = [u*u, u*t, t*t, e2, r2]
    degree6 = [u**3, u*u*t, u*t*t, t**3, u*e2, t*e2, e3, u*r2, t*r2]
    sq2_degree2 = [u*u, t*t]
    sq2_degree4 = [0, u*u*t+u*t*t, 0, t*e2+e3, 0]
    monomials = (u, t, e2, r2, e3)
    coefficient = lambda expression, monomial: int(sp.Poly(expression, *monomials).coeff_monomial(monomial)) % 2
    # Homological differentials are dual to Sq2 (with integral reduction on q=0).
    outgoing = [[coefficient(poly, mon) for mon in degree4] for poly in sq2_degree2]
    incoming = [[coefficient(poly, mon) for mon in degree6] for poly in sq2_degree4]
    composition = sp.Matrix(outgoing)*sp.Matrix(incoming)
    if any(int(v) % 2 for v in composition):
        raise RuntimeError("d2 squared is nonzero")
    surviving_dimension = len(degree4)-rank_mod2(outgoing)-rank_mod2(incoming)
    if surviving_dimension != 1:
        raise RuntimeError("product-category bordism computation changed")
    return {
        "background_category": "ordinary Spin tangent times U1_M times SU2_R times U5_E, with genuine independent bundles",
        "degree2_basis": [str(v) for v in degree2],
        "degree4_basis": [str(v) for v in degree4],
        "degree6_basis": [str(v) for v in degree6],
        "Sq2_on_degree2": [str(v) for v in sq2_degree2],
        "Sq2_on_degree4": [str(v) for v in sq2_degree4],
        "d2_outgoing_H4_Z2_to_H2_Z2": outgoing,
        "d2_incoming_H6_Z_to_H4_Z2": incoming,
        "outgoing_rank": rank_mod2(outgoing), "incoming_rank": rank_mod2(incoming),
        "E3_4_1_dimension": surviving_dimension,
        "surviving_dual_class": "c2(R)",
        "higher_differentials": "Only total-degree-five E2 entry is H4(-;Z2). Outgoing d3 lands in H1(-;Omega3)=0; d4 maps finite Z2 to the torsion-free E4_0_4=Z and is zero. Higher outgoing and all higher incoming entries are outside the first quadrant.",
        "extension_problem": "one surviving associated-graded group, hence no extension ambiguity",
        "Omega5": "Z2", "order": 2,
        "generator": "S4 with a unit SU2_R instanton times the periodic spin circle; M and E trivial",
        "generator_mod2_Dirac_index": 1,
        "this_is_the_full_Gammahat_bordism_group": False,
    }


def content():
    parents = {key: common.load_bound(ROOT/name, core) for key, (name, core) in PARENTS.items()}
    if parents["v96_master"]["next_required_action"]["id"] != "F97_EQUIVARIANT_MASS_DEFECT_INDEX_AND_FULL_RELATIVE_GLUE":
        raise RuntimeError("F97 obligation changed")
    old = parents["v96_route"]["normal_relative_CS"]["new_normal_repairs"][0]
    v95_route = common.load_bound(ROOT/"SUSY_V95_WALL_KERNEL_FINITE_INFLOW_RANK_AUDIT.json", parents["v96_route"]["input_core_hashes"]["v95_route"])
    for name in ("v95_wall_symmetry_lift_audit.py", "test_v95_wall_symmetry_lift_audit.py"):
        if common.file_sha(ROOT/name) != v95_route["artifact_hashes"][name]:
            raise RuntimeError("known geometric kernel source pin changed")
    for name in ("v96_normal_relative_cs_audit.py", "test_v96_normal_relative_cs_audit.py"):
        if common.file_sha(ROOT/name) != parents["v96_route"]["artifact_hashes"][name]:
            raise RuntimeError("V96 normal helper pin changed")
    if old["normal_root_charges"] != [-3, -3]:
        raise RuntimeError("V96 selected normal charges changed")
    target = -u*e2+u**3+u*p/4
    fermions = su2_index(-3, 1)
    cs = -u*e2+10*u**3-3*u*r2
    reference_fermions = 2*line_index(-3*u)
    reference_cs = -u*e2+10*u**3
    if sp.expand(fermions+cs-target) != 0 or sp.expand(fermions-reference_fermions-3*u*r2) != 0:
        raise RuntimeError("nonabelian normal/R cancellation failed")
    bits = [1, 1, 0, 1, 0, 0, 0]
    generators = (kernel.D, kernel.KROT_T, kernel.KSPIN)
    all_kernel = [[sum(a*g[i] for a, g in zip(coeffs, generators)) % 2 for i in range(7)] for coeffs in product(range(2), repeat=3)]
    checks = [kernel.dot_mod2(bits, g) for g in all_kernel]
    if any(checks) or len(set(map(tuple, all_kernel))) != 8:
        raise RuntimeError("new representation fails a known geometric central relation")
    n = sp.symbols("n", integer=True, positive=True)
    index_difference = sp.factor((2*n)*((2*n)**2-1)/6-n)
    if index_difference != 4*n*(n-1)*(n+1)/3:
        raise RuntimeError("SU2 Witten-parity identity changed")
    sample_rows = []
    for highest in range(1, 16, 2):
        dim = highest+1
        instanton = dynkin_index_twice(highest)
        if instanton % 2 != (dim//2) % 2:
            raise RuntimeError("half-integral SU2 parity law failed")
        sample_rows.append({"highest_weight": highest, "dimension": dim, "instanton_index": instanton, "Witten_parity": instanton % 2})
    return {
        "schema": "v97_normal_SU2_refinement_and_flat_torsion_v1",
        "status": "NONABELIAN_RESTRICTED_CURVATURE_REPAIR_WITH_EXPLICIT_REQUIRED_Z2_REFINEMENT__FULL_PARENT_OPEN",
        "input_core_hashes": {key: value[1] for key, value in PARENTS.items()},
        "changed_representation": {
            "old_V96_R_Cartan_weights": [-3, -3], "new_complete_SU2_R_highest_weight": 1,
            "new_R_weights": [-1, 1], "normal_root_weight_for_both_components": -3,
            "Weyl_multiplets": 1, "complex_Weyl_components": 2,
            "associated_fermion_bundle": "S_plus(T4) tensor M^(-3) tensor R_fundamental; gauge/flavor singlet",
            "representation_of_product_cover_and_known_central_quotient": True,
            "known_center_character_bits": bits, "all_eight_kernel_exponents": checks,
            "unbroken_SU2_R_at_the_actual_orbifold_wall_established": False,
            "C4_normal_R_weight_exponents_mod8": [(-3-w) % 8 for w in (-1, 1)],
            "C4_exponents_mean": "normal zeta^k times frozen R twist zeta^(-r); not an intrinsic-wall projection prescription",
            "preserves_V96_qN_minus_r_over2_zero_for_every_component": False,
            "same_V96_R_representation_claimed": False,
            "complete_supermultiplet_or_global_wall_placement_constructed": False,
        },
        "nonabelian_curvature_repair": {
            "definitions": "u=c1(M), e2=c2(E), r2=c2(R), p=p1(T); Cartan restriction r2=-y^2",
            "fermion_I6": str(fermions), "integer_CS_I6": str(cs), "target_I6": str(target),
            "residual": str(sp.expand(fermions+cs-target)),
            "reference_R_trivial_fermion_I6": str(reference_fermions), "reference_CS_I6": str(reference_cs),
            "new_fermion_R_term": str(sp.expand(fermions-reference_fermions)),
            "compensating_integer_mixed_R_CS": "-3*u*r2",
            "differential_character": "-c1hat(M) cup c2hat(E)+10*c1hat(M)^3-3*c1hat(M) cup c2hat(R)",
            "integer_coefficients": [-1, 10, -3],
            "action_on_closed_Y5": "exponentiated holonomy of the degree-six differential character, defined also on nonbounding manifolds",
            "R_bundle_need_not_split_into_Cartan_lines": True,
            "new_sector_total_curvature_independent_of_R": True,
            "original_bulk_R_flavor_anomalies_have_been_computed_or_cancelled": False,
            "all_full_theory_anomalies_cancelled": False,
        },
        "forced_Witten_class_in_this_ansatz": {
            "assumptions": "complete SU2_R multiplets, other internal flavor centers trivial, odd normal-root weight k for each multiplet, and no gravitational CS term so sum(d_R*k)=-6",
            "SU2_highest_weights_required_odd": True,
            "instanton_index_formula": "A_R=d_R*(d_R^2-1)/6",
            "parity_proof": "write d_R=2n; A_R-n=4*n*(n-1)*(n+1)/3 is a multiple of4 because three consecutive integers have product divisible by3. Thus A_R=n mod2. Since k is odd, sum A_R=sum(d_R*k)/2=-3=1 mod2.",
            "symbolic_index_minus_n": str(index_difference), "sample_rows": sample_rows,
            "required_trace_normal_weight": -6, "forced_Witten_parity": 1,
            "test_background": "S4 unit SU2_R instanton times periodic S1, M and E trivial with trivial connections",
            "new_fermion_phase": "-1", "displayed_bosonic_CS_phase": "+1",
            "local_polynomial_cancellation_alone_removes_new_Witten_class": False,
            "changing_only_complete_SU2_multiplets_within_ansatz_removes_it": False,
            "full_parent_bare_R_torsion_already_computed": False,
            "full_parent_total_Witten_anomaly_proved_nonzero": False,
            "scope": "constraint on the added SU2-completed repair sector, not a no-go for the actual parent or a wall preserving only the R Cartan",
        },
        "restricted_product_bordism": product_bordism(),
        "flat_refinement": {
            "reference": "two ordinary-spin line Weyls M^(-3) with R acting trivially, plus K10; a comparison countertheory, not a physical Gammahat representation",
            "relative_curvature_new_minus_reference": "0",
            "relative_phase_on_product_generator": "-1",
            "relative_anomaly_character": "nu_R(Y,R)=(-1)^(ind2 D5_Rfund)",
            "proof": "the curvature-zero ratio is a character of the computed product bordism Z2; evaluation on its unit-instanton periodic-circle generator uniquely determines it",
            "explicit_flat_inverse_response": "nu_R itself, since nu_R^2=1",
            "multiplying_by_nu_R_restores_reference_on_all_stated_product_backgrounds": True,
            "restores_reference_means_trivializes_reference_anomaly": False,
            "same_action_5D_inflow_realizing_nu_R_constructed": False,
            "two_C4_sectors_cancel_on_shared_diagonal_R_background": True,
            "shared_diagonal_cancellation_proves_independent_endpoint_gluing": False,
            "natural_Spin_c_half_period_from_V96_removed": False,
            "full_Gammahat_or_SU2_twisted_tangential_descent_proved": False,
        },
        "terminal_decision": {
            "new_complete_SU2_fermion_representation_on_product_cover": True,
            "new_sector_normal_and_R_curvature_match_on_product_category": True,
            "required_flat_Z2_refinement_computed": True,
            "same_action_parent_accepted": False, "closed_gates": [],
        },
        "primary_sources": [
            {"url": "https://arxiv.org/abs/2011.05768", "use": "Sections3-4 define integral differential-character holonomy and distinguish it from a full equivariant lift; used for the new SU2-invariant degree-six character."},
            {"url": "https://arxiv.org/abs/1207.5449", "use": "Higher cup-product Chern-Simons actions supply the global construction for integral mixed Chern classes; not a same-action microscopic realization."},
            {"url": "https://arxiv.org/abs/1810.00844", "use": "Sections2.2-2.3 give the periodic-circle instanton test and SU2 representation parity formula; section2.7 distinguishes ordinary spin from spin-SU2 anomalies."},
            {"url": "https://arxiv.org/abs/1808.00009", "use": "Section2.2.3 and the SU(n) computation in Section3.4 supply ordinary-spin AHSS d2 as dual Sq2 and Sq2(c2)=c1*c2+c3. The product-group calculation is performed here."},
            {"url": "https://arxiv.org/abs/hep-th/9405012", "use": "Exponentiated eta invariants, determinant lines and gluing; a curvature-zero ratio is treated as a restricted flat anomaly character, not as a full parent cancellation."},
        ],
    }


def build_certificate():
    out = content()
    out["core_sha256"] = common.canonical_sha(out)
    return out


def validate_certificate(out):
    if out.get("core_sha256") != common.canonical_sha(out):
        raise RuntimeError("noncanonical F97 normal SU2 certificate")
    body = copy.deepcopy(out)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("F97 normal SU2 arithmetic, scope or lineage changed")
