"""F95: the V94 wall candidate fails the unchanged geometric Gammahat pullback.

This is a restricted representation-theoretic obstruction, not a theorem
excluding every new boundary structure.  R/flavor Cartan diagnostics below
retain their anomaly curvatures and do not construct full representations.
"""
from __future__ import annotations

import copy
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v94_route": ("SUSY_V94_BOUNDARY_DEFECTS_AND_MW_DESCENT_AUDIT.json",
                  "17fd3a60008545b7bde77756ed8b5ec7dd590c18c1cbb1344a5a7cc67dd2686f"),
    "v94_master": ("SUSY_V94_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
                   "8332984113477ebbbc8a1bc44915475cc3c38003c8c3a7ac9c9a5e35fc11da06"),
    "v93_route": ("SUSY_V93_LOCALIZED_ANOMALY_R_LIFT_JACOBIAN_AUDIT.json",
                  "4f81852d9e272d3fb12946ad41cb01d9f93462f75cef69123106a80b03f092f2"),
    "v90": ("SUSY_V90_EXTERNAL_C8_QUOTIENT_DAIFREED_REES_EQUIVARIANCE_AUDIT.json",
            "ec095daa641345934d285a56a1916bf701352ee5cb113018296487ade36b966f"),
    "v70": ("SUSY_V70_SPIN11_LOCALIZED_PARENT_SPIN_FLAVOR_COMPLETION_AUDIT.json",
            "3e7b8e53916fbbc05bdcdf9632bcf4359aa4888b037df775c37d8d7d2551b228"),
}
NORMAL_CORE = "d96d980252f3bfa8bc96da385812c1e0cb4e173add8b9da77a05fe28678be697"
R_CORE = "c4f752b27ae64d447689e96f1125fc34e6b0b94aeaee95a8ee80f0ed52e6cacf"
E = sp.symbols("e1:6")
x, p, y = sp.symbols("x p y")
D = [1, 1, 0, 0, 0, 0, 0]
KROT_T = [1, 0, 1, 1, 1, 1, 0]
KROT_N = [0, 1, 1, 1, 1, 1, 0]
KSPIN = [0, 0, 1, 0, 0, 0, 1]


def canonical_sha(value):
    body = copy.deepcopy(value)
    body.pop("core_sha256", None)
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_parents():
    reports = {}
    for key, (name, expected) in PARENTS.items():
        value = json.loads((ROOT/name).read_text(encoding="utf-8"))
        if value.get("core_sha256") != expected or canonical_sha(value) != expected:
            raise RuntimeError("changed or noncanonical F95 wall parent: " + key)
        reports[key] = value
    master = reports["v94_master"]
    if master["input_core_hashes"]["v94_route"] != PARENTS["v94_route"][1]:
        raise RuntimeError("V94 route/master edge changed")
    if master["next_required_action"]["id"] != "F95_RELATIVE_SPIN_NORMAL_DEFECT_GLUE_AND_INVARIANT_MW_SECTION":
        raise RuntimeError("F95 obligation changed")
    normal = reports["v94_route"]["normal_wall_quantization"]
    rlift = reports["v93_route"]["smooth_R_and_wall_mass_extension"]
    for key, value, expected in (("normal", normal, NORMAL_CORE), ("R", rlift, R_CORE)):
        if value.get("core_sha256") != expected or canonical_sha(value) != expected:
            raise RuntimeError("bound helper changed: " + key)
    if rlift["known_kernel_coordinates"] != ["T", "Spin11", "R", "H3", "H267", "k4"]:
        raise RuntimeError("frozen center coordinates changed")
    if rlift["known_kernel_generators"] != {"krot": [1, 1, 1, 1, 1, 0], "kspin": [0, 1, 0, 0, 0, 1]}:
        raise RuntimeError("frozen Gammahat kernel changed")
    if rlift["singlet_R_extension"]["new_relation_R_squared_equals_fermion_parity_imposed"]:
        raise RuntimeError("independent R4 was replaced by a new spin quotient")
    group = reports["v90"]["G8_component_extension"]
    if group["group"] != "G8=(Spin(11) x C8)/<(z,k^4)>" or group["representation_descent_rule"] != "Spin11 center bit c plus q8 equals 0 mod 2":
        raise RuntimeError("external C8 quotient changed")
    susy = reports["v70"]["lorentz_SU2R_and_N1_superfield_lift"]
    if susy["SU2R_twist"]["U_R"] != "diag(zeta^-1,zeta), zeta=exp(i pi/4)" or susy["SU2R_twist"]["preserved_supercharge_product_exponents_mod8"] != [0, 0]:
        raise RuntimeError("preserved N1 branch changed")
    return reports


def xor(a, b):
    return [(aa+bb) % 2 for aa, bb in zip(a, b)]


def dot_mod2(a, b):
    return sum(aa*bb for aa, bb in zip(a, b)) % 2


def center_map(bits):
    """Restriction Spin4 x Spin2 -> Spin6 sends the two -1 centers to -1."""
    if len(bits) != 7 or any(v not in (0, 1) for v in bits):
        raise ValueError("seven center bits required")
    return [(bits[0]+bits[1]) % 2] + list(bits[2:])


def central_solutions(k_normal, tangent_bit=1, modulus=2):
    if type(k_normal) is not int or tangent_bit not in (0, 1) or modulus not in (2, 4):
        raise ValueError("integral normal weight, tangent bit, and modulus 2 or4 required")
    solutions = []
    for r, h3, h267 in product(range(modulus), repeat=3):
        character = [tangent_bit, k_normal % 2, 0, r % 2, h3 % 2, h267 % 2, 0]
        if all(dot_mod2(character, g) == 0 for g in (D, KROT_T, KROT_N, KSPIN)):
            solutions.append([r, h3, h267])
    return solutions


def clifford_generators():
    s1 = sp.Matrix([[0, 1], [1, 0]])
    s2 = sp.Matrix([[0, -sp.I], [sp.I, 0]])
    s3 = sp.diag(1, -1)
    identity = sp.eye(2)
    return [sp.kronecker_product(*([s3]*j+[s]+[identity]*(2-j)))
            for j in range(3) for s in (s1, s2)]


def kernel_certificate(rlift):
    old = rlift["known_kernel_generators"]
    old_elements = [[0]*6, old["krot"], old["kspin"], xor(old["krot"], old["kspin"])]
    inverse_image = [list(bits) for bits in product(range(2), repeat=7) if center_map(bits) in old_elements]
    generated = []
    for a, b, c in product(range(2), repeat=3):
        generated.append([int(a*D[j]+b*KROT_T[j]+c*KSPIN[j]) % 2 for j in range(7)])
    gamma = clifford_generators()
    g12, g56 = gamma[0]*gamma[1], gamma[4]*gamma[5]
    checks = {
        "Clifford_anticommutators": all(gamma[i]*gamma[j]+gamma[j]*gamma[i] == (2*sp.eye(8) if i == j else sp.zeros(8)) for i in range(6) for j in range(6)),
        "tangent_and_normal_bivectors_commute": g12*g56 == g56*g12,
        "both_two_pi_lifts_are_minus_identity": g12*g12 == -sp.eye(8) and g56*g56 == -sp.eye(8),
        "D_maps_to_literal_identity_in_Spin6": g12*g12*g56*g56 == sp.eye(8),
        "D_maps_to_zero_old_center_bits": center_map(D) == [0]*6,
        "two_krot_preimages_agree": center_map(KROT_T) == center_map(KROT_N) == old["krot"],
        "two_krot_preimages_differ_by_D": xor(KROT_T, KROT_N) == D,
        "full_inverse_image_kernel_has_eight_elements": len(inverse_image) == 8 and sorted(inverse_image) == sorted(generated),
    }
    if not all(checks.values()):
        raise RuntimeError("exact geometric kernel calculation failed")
    return {
        "old_coordinates": rlift["known_kernel_coordinates"], "old_generators": old,
        "expanded_coordinates": ["T4", "N2", "Spin11", "R", "H3", "H267", "k4"],
        "center_map": "(t4,n2,g,r,h3,h267,k4) -> (t4+n2,g,r,h3,h267,k4) mod2",
        "generators": {"D": D, "krot_T": KROT_T, "krot_N_redundant": KROT_N, "kspin": KSPIN},
        "full_inverse_image_kernel": sorted(inverse_image), "checks": checks,
        "proof": "In the Clifford embedding each tangent/normal2pi rotation is -1 in Spin6; their product D is1 before any R/flavor/gauge quotient. Pulling back an independent internal representation gives identity on D.",
        "restriction": "the unchanged geometric inclusion with independent internal factors; not a theorem about a new correlated tangential structure or new boundary cover",
        "independent_R_flavor_or_C8_character_can_change_D": False,
        "existing_half_angle_factors_denied": False,
    }


def block_specs(normal):
    rows = copy.deepcopy(normal["conditional_product_lift_wall_module"]["field_blocks"])
    expected = [("E", 1, 5, "1/2"), ("E_dual", 1, 5, "0"), ("det_E", 1, 1, "0"),
                ("det_E_inverse", 1, 1, "-1/2"), ("singlet_positive", 2, 1, "1"), ("singlet_negative", 14, 1, "-1/2")]
    if [(r["representation"], r["copies"], r["dimension"], r["normal_charge_qN"]) for r in rows] != expected:
        raise RuntimeError("V94 wall module changed")
    if any(r["continuous_U1_8_charge"] != 0 or not r["Spin_c11_gauge_center_even"] for r in rows):
        raise RuntimeError("V94 gauge descent changed")
    return rows


def module_descent(rows):
    results, failing = [], 0
    for row in rows:
        k = row["Spin2_integral_weight"]
        solutions = central_solutions(k)
        scalar_solutions = central_solutions(k+1, tangent_bit=0)
        transported = sorted([[(a+1) % 2, b, c] for a, b, c in solutions])
        if transported != sorted(scalar_solutions):
            raise RuntimeError("N1 supersymmetry did not transport kernel characters")
        bad = row["dimension"]*row["copies"]*((1+k) % 2)
        failing += bad
        results.append({"representation": row["representation"], "copies": row["copies"], "dimension": row["dimension"],
                        "fermion_normal_charge": row["normal_charge_qN"], "fermion_Spin2_weight": k,
                        "scalar_normal_charge": str(sp.Rational(row["normal_charge_qN"])+sp.Rational(1, 2)),
                        "scalar_Spin2_weight": k+1, "D_exponent_for_both_components": (1+k) % 2,
                        "fermion_internal_center_solutions_R_H3_H267": solutions,
                        "scalar_internal_center_solutions_R_H3_H267": scalar_solutions,
                        "fermion_mod4_weight_solutions_count": len(central_solutions(k, modulus=4)),
                        "N1_scalar_R_center_is_fermion_R_plus_one": True,
                        "failing_complex_Weyl_components": bad,
                        "central_solution_is_full_representation": False})
    if failing != 8:
        raise RuntimeError("unexpected number of obstructed components")
    return {"rows": results, "complex_Weyl_components": sum(r["dimension"]*r["copies"] for r in rows),
            "failing_complex_Weyl_components": failing, "passing_necessary_kernel_screen_components": 28-failing,
            "unchanged_candidate_descends_to_geometric_Gammahat_pullback": False,
            "same_candidate_rescued_by_independent_R_or_flavor_centers": False,
            "equations": ["D:1+2qN=0 mod2", "krot_T:1+r+h3+h267=0 mod2", "krot_N:2qN+r+h3+h267=0 mod2", "kspin:g+q8=0 mod2 (here both0)"],
            "passing_twenty_components_have_full_localized_representations": False,
            "all_other_boundary_completions_excluded": False}


def weyl_polynomial(weights, q, extra=0):
    return sp.expand(sum((w+q*x+extra)**3/6-(w+q*x+extra)*p/24 for w in weights))


def anomaly_certificate(rows, normal):
    total, twisted, general_delta = sp.Integer(0), sp.Integer(0), sp.Integer(0)
    detail = []
    for index, row in enumerate(rows):
        weights = [sp.sympify(w) for w in row["weights"]]
        q, copies = sp.Rational(row["normal_charge_qN"]), row["copies"]
        k = int(2*q)
        delta = sp.Symbol("d"+str(index))
        plain = weyl_polynomial(weights, q)
        with_R = weyl_polynomial(weights, q, k*y)
        general = sp.expand(weyl_polynomial(weights, q, delta)-plain)
        derivation = sp.expand(sum(delta*(w+q*x)**2/2+delta**2*(w+q*x)/2+delta**3/6-delta*p/24 for w in weights))
        if general != derivation:
            raise RuntimeError("omitted internal curvature term")
        total += copies*plain
        twisted += copies*with_R
        general_delta += copies*general
        detail.append({"representation": row["representation"], "copies": copies,
                       "fermion_R_Cartan_weight_diagnostic": k, "scalar_R_Cartan_weight_diagnostic": k+1,
                       "fermion_R4_if_flavor_action_trivial": k % 4, "scalar_R4_if_flavor_action_trivial": (k+1) % 4,
                       "qN_minus_rR_over2": "0", "extra_root_symbol": str(delta),
                       "extra_root_meaning": "d_i=r_i*y_R+h3_i*y_H3+h267_i*y_H267 on a chosen Cartan component; not a full nonabelian representation",
                       "one_copy_general_added_anomaly": str(general),
                       "one_copy_R_diagnostic_I6": str(with_R)})
    total, twisted, general_delta = map(sp.expand, (total, twisted, general_delta))
    cc2 = sum(a*b for a, b in combinations(E, 2))
    target = -x*cc2/2+x*p/8+x**3/8
    expected = sp.expand(target.subs(x, x+2*y))
    if sp.expand(total-target) != 0 or twisted != expected or total != sp.sympify(normal["conditional_product_lift_wall_module"]["full_wall_polynomial"]):
        raise RuntimeError("R/flavor anomaly diagnostic disagrees with bound normal target")
    return {
        "convention": "positive4D Weyl I6=[Ahat(T4)ch]_6; x=normal SO2 curvature, y=Sp1_R Cartan root with fundamental weights+-1, p=p1(T4)",
        "scalar_partners_add_no_chiral_fermion_anomaly": True,
        "rows": detail, "original_wall_I6": str(total),
        "R_phase_neutralizing_ansatz": "r_R(fermion)=2qN, r_R(scalar)=2qN+1; flavor charges zero in this Cartan diagnostic",
        "R_ansatz_is_an_actual_new_Gammahat_representation": False,
        "R_ansatz_still_has_eight_D_failures": True,
        "R_diagnostic_full_I6": str(twisted), "R_diagnostic_added_I6": str(sp.expand(twisted-total)),
        "R_diagnostic_compact_identity": "I6_R=-(x+2y)*c2(E)/2+(x+2y)*p/8+(x+2y)^3/8",
        "all_internal_Cartan_shifts_added_I6": str(general_delta),
        "diagonal_connection_y_minus_x_over2_restriction": str(sp.expand(twisted.subs(y, -x/2))),
        "diagonal_restriction_cancels_frozen_bare_normal_anomaly": False,
        "reason": "On y=-x/2 this candidate contributes zero, whereas the frozen normal-only bulk polynomial is nonzero. The full bulk R-curvature polynomial and tangential locking data would also have to be reconstructed before comparing that different background category.",
        "flat_discrete_R4_has_no_nonzero_deRham_y_but_torsion_still_requires_audit": True,
        "R4_mod4_charges_determine_unique_continuous_anomaly": False,
        "lift_ambiguity": "r_R and r_R+4s have identical R4 characters but generally different y-dependent polynomial; finite characters alone do not license a continuous lift",
        "new_curvatures_may_be_dropped_from_a_full_anomaly_claim": False,
        "nonabelian_R_flavor_representations_and_extra_weight_partners_constructed": False,
    }


def certificate_content():
    parents = load_parents()
    normal = parents["v94_route"]["normal_wall_quantization"]
    rlift = parents["v93_route"]["smooth_R_and_wall_mass_extension"]
    rows = block_specs(normal)
    return {
        "schema": "v95_wall_symmetry_lift_audit_v1",
        "input_core_hashes": {key: core for key, (_, core) in PARENTS.items()},
        "embedded_parent_core_hashes": {"v94_normal": NORMAL_CORE, "v93_R_lift": R_CORE},
        "scope": "exact necessary obstruction for the unchanged V94 wall charges in the natural geometric Gammahat pullback; conditional N1 and Cartan-anomaly diagnostics, not a completed wall action",
        "geometric_kernel": kernel_certificate(rlift),
        "wall_module_descent": module_descent(rows),
        "N1_charge_bookkeeping": {
            "selected_branch_is_bound_to_V70": True,
            "theta_tangent_spin": "left Weyl", "theta_normal_charge": "1/2", "theta_R_Cartan_weight": 1,
            "frozen_R_twist": "A_R=exp(-i*phi*R/2), phi=pi/2; theta normal and R phases are zeta and zeta^-1",
            "theta_combined_geometric_phase": "1",
            "superfield_relation": "Phi=phi+sqrt(2)*theta*psi+theta^2*F: qN(phi)=qN(psi)+1/2; r_R(phi)=r_R(psi)+1; flavor/gauge charges unchanged",
            "shared_geometric_charge": "q_geom=qN-r_R/2",
            "auxiliary_F_relation": "qN(F)=qN(psi)-1/2; r_R(F)=r_R(psi)-1",
            "independent_V93_R4_rule": "r4(phi)=r4(psi)+1 mod4; geometric orbifold phases are not these independent R charges",
            "V93_R_element": rlift["singlet_R_extension"]["construction"],
            "V93_R_squared_equals_fermion_parity_was_imposed": False,
            "scalar_and_fermion_D_failure_identical": True,
            "formal_partner_assignment_is_full_supersymmetric_wall_action": False,
            "pure_C4_phase_screen_cannot_replace_kernel_descent": True,
        },
        "retained_internal_anomaly_curvatures": anomaly_certificate(rows, normal),
        "remaining_options_and_obligations": {
            "unchanged_module_plus_independent_center_signs": "REJECTED by eight D characters, before anomaly cancellation",
            "different_correlated_tangential_internal_lift": "not excluded; specify its actual map/kernel and all old/new representations, then recompute normal/R/flavor curvatures and finite equivariance",
            "separate_boundary_Spin4_x_Spin2_cover": "V94 conditional witness retained as a different boundary structure, not inherited Gammahat",
            "new_intrinsic_spin_fermion_sector_may_change_tangential_category": True,
            "projectors_at_both_C4_walls_and_transport_constructed": False,
            "extra_scalar_potential_mass_decay_and_cosmology_constructed": False,
            "R_or_flavor_anomalies_cancelled": False,
            "full_relative_WCS_Dai_Freed_gluing_constructed": False,
        },
        "terminal_decision": {
            "V94_unchanged_module_embeds_in_natural_Gammahat_pullback": False,
            "independent_internal_centers_repair_it": False,
            "new_full_wall_action_constructed": False,
            "every_possible_wall_completion_excluded": False,
            "full_bare_I6_cancelled": False,
            "accepted_extensions": 0, "closed_gates": [], "all_eight_gates_remain_open": True,
        },
        "primary_sources": [
            {"url": "https://arxiv.org/abs/hep-th/0612212", "use": "Sections3.2-4 distinguish normal Lorentz anomalies; section5.1 gives the half-angle SU2R twist and N1 branches. The geometric kernel and candidate obstruction are derived here, not asserted by the paper."},
            {"url": "https://arxiv.org/abs/hep-th/0602155", "use": "N1 superfield expansion/action and equations44-45 motivate tracking both superspace and matter twists; no source assertion of the new wall candidate."},
            {"url": "https://arxiv.org/abs/1808.01334", "use": "Section2 distinguishes R representations/SMW reality and local index polynomials from full anomaly field theories; Cartan weights alone do not construct either."},
        ],
    }


def build_certificate():
    value = certificate_content()
    value["core_sha256"] = canonical_sha(value)
    return value


def validate_certificate(value):
    if value.get("core_sha256") != canonical_sha(value) or value != build_certificate():
        raise RuntimeError("F95 wall symmetry arithmetic, parent or scope changed")


if __name__ == "__main__":
    print(json.dumps(build_certificate(), indent=2, sort_keys=True))
