"""Positive carrier realizations: local character matching has a bulk price.

No V97 Dirac gap is transferred.  All representation/spectrum statements use
explicit new compensated-lift assumptions.  The unchanged geometric kernel
still excludes a bare normal-root twist of an ordinary six-dimensional field.
"""
from __future__ import annotations

import copy
from functools import lru_cache
import hashlib
from itertools import product
import json
from pathlib import Path

import sympy as sp

import v97_mixed_gauge_relative_glue_audit as previous
import v96_local_transport_quantization_audit as kernel


ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v97_route": ("SUSY_V97_EQUIVARIANT_INDEX_RELATIVE_GLUE_SECTION_AUDIT.json", "161eb53a3e453c80b3887d365e31c32c6846d1c6f8d45b474b849f07a3de2020"),
    "v97_master": ("SUSY_V97_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json", "f7ccb9c8d047a3135330ed7c8a361fd4625ca343547cf05b9cc31a7158b50e31"),
}
MIXED_CORE = "42192f27cd064aa00cb33c4a38cc67a3c94c03c6aa10a0cea7ea7348b6e6dd16"
d, u, v, w, x, p = sp.symbols("d u v w x p")
P1, P2, y, v1, v2, r1, r2 = sp.symbols("P1 P2 y v1 v2 r1 r2")
C = {0: 1, 1: -2, 2: 1}
J = sp.Matrix([[0, 1], [-1, 0]])
ZETA = kernel.ZETA


def canonical_sha(value):
    body = copy.deepcopy(value)
    body.pop("core_sha256", None)
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def clean(matrix):
    return matrix.applyfunc(sp.simplify)


def matrix_json(matrix):
    return [[str(sp.simplify(z)) for z in row] for row in matrix.tolist()]


def portable_sha(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_parents():
    reports = {}
    for key, (filename, expected) in PARENTS.items():
        value = json.loads((ROOT/filename).read_text(encoding="utf-8"))
        if value.get("core_sha256") != expected or canonical_sha(value) != expected:
            raise RuntimeError("changed or noncanonical F98 physical-carrier parent: "+key)
        reports[key] = value
    route, master = reports["v97_route"], reports["v97_master"]
    if master["input_core_hashes"]["v97_route"] != PARENTS["v97_route"][1]:
        raise RuntimeError("V97 master-route edge changed")
    if master["next_required_action"]["id"] != "F98_GAMMAHAT_TRANSPORT_LIFT_AND_ORIGINAL_SQUARE_SECTION":
        raise RuntimeError("F98 obligation changed")
    frozen = route["mixed_gauge_relative_glue"]
    if frozen.get("core_sha256") != MIXED_CORE or canonical_sha(frozen) != MIXED_CORE:
        raise RuntimeError("frozen virtual carrier changed")
    for name in ("v97_mixed_gauge_relative_glue_audit.py", "test_v97_mixed_gauge_relative_glue_audit.py"):
        if portable_sha(ROOT/name) != route["artifact_hashes"][name]:
            raise RuntimeError("V97 mixed-carrier source or test changed")
    if frozen != previous.build_certificate():
        raise RuntimeError("V97 mixed helper no longer reproduces its parent")
    return reports


def I6(z):
    return sp.expand(z**3/6-p*z/24)


def I8(z):
    return sp.expand(z**4/24-P1*z*z/48+(7*P1*P1-4*P2)/5760)


def local_I6(order, phase, root):
    coefficients = kernel.phase_series(order, phase % order)
    a0, a1, a2, a3 = coefficients
    return sp.expand(a0*I6(root)+a1*x*(root*root/2-p/24)+a2*x*x*root+a3*x**3)


def target_P(root=w):
    return sp.expand(d*d*(d+root))


def phase_counts(coefficient, regular=None):
    if not isinstance(coefficient, int) or regular is not None and not isinstance(regular, int):
        raise ValueError("integer virtual and regular multiplicities are required")
    regular = abs(coefficient) if regular is None else regular
    values = [regular, regular+coefficient, regular-coefficient, regular]
    if min(values) < 0:
        raise ValueError("negative physical multiplicity")
    return values


def positive_blocks(orientation=1):
    if orientation not in (-1, 1):
        raise ValueError("orientation must be plus or minus one")
    rows = []
    for n, coefficient in C.items():
        for phase, count in enumerate(phase_counts(orientation*coefficient)):
            if count:
                rows.append({"D_power": n, "covering_U1_charge": 2*n, "phase": phase,
                             "multiplicity": count, "six_dimensional_chirality": 1})
    return rows


def local_sum(rows, order, root=w):
    return sp.expand(sum(row["six_dimensional_chirality"]*row["multiplicity"]*
                         local_I6(order, row["phase"], row["D_power"]*d+root) for row in rows))


def projector(phase):
    return sp.simplify(sum(phase**j for j in range(4))/4)


def character_realization():
    N = sp.symbols("N0:4")
    c = sp.Symbol("c", integer=True)
    matrix = sp.Matrix([[1, 0, -1, 0], [0, 1, 0, -1], [1, -1, 1, -1]])
    solution = sp.linsolve((matrix, sp.Matrix([c, c, -2*c])), N)
    expected = sp.FiniteSet((N[3], N[3]+c, N[3]-c, N[3]))
    if solution != expected or matrix.nullspace() != [sp.ones(4, 1)]:
        raise RuntimeError("complete nonidentity character solution changed")
    rows = []
    for orientation in (1, -1):
        blocks = positive_blocks(orientation)
        c4, c2 = local_sum(blocks, 4), local_sum(blocks, 2)
        if sp.expand(c4-orientation*target_P()/4) != 0 or sp.expand(2*c2+orientation*target_P()/2) != 0:
            raise RuntimeError("positive-multiplicity local anomaly profile failed")
        rows.append({"orientation": orientation, "blocks": blocks, "full_hyper_count": sum(b["multiplicity"] for b in blocks),
                     "per_physical_stratum_I6": [str(c4), str(c4), str(2*c2)],
                     "remaining_profile_with_original_target": [str(sp.expand(c4+target_P(u)/4)), str(sp.expand(c4+target_P(u)/4)), str(sp.expand(2*c2-target_P(u)/2))] if orientation == -1 else None})
    return {
        "status": "EXACT_POSITIVE_MULTIPLICITY_CHARACTER_REALIZATION_UNDER_NEW_COMPENSATED_LIFT_ASSUMPTIONS",
        "virtual_coefficients_D0_D1_D2": [1, -2, 1],
        "required_linewise_nonidentity_character": "sum_m N_m*i^(m*j)=c*(i^j-i^(2*j)), j=1,2,3",
        "real_integer_constraint_matrix": matrix_json(matrix), "right_hand_side": ["c", "c", "-2*c"],
        "complete_solution": "(N0,N1,N2,N3)=(A,A+c,A-c,A), A integer and A>=|c|",
        "proof": "The three nonidentity Fourier equations have rank3 and kernel generated by(1,1,1,1). This regular C4 character has zero trace on every nonidentity element, including the C2 stabilizer. Positivity requires A>=|c|.",
        "minimum_within_this_linewise_C4_character_ansatz": 16,
        "multiplicity_domain": "Sixteen full hyper units in the linewise C4 and commuting-unitary-multiplicity-centralizer ansatz. This is not a sixteen-hyper representation of the entire frozen nonabelian Sp267 flavor group; retaining that full group can require tensor-product partners and a different anomaly and spectrum count.",
        "minimum_is_claimed_over_all_possible_physical_repairs": False,
        "regular_character_additions_D0_D1_D2": [1, 2, 1],
        "realizations": rows,
        "orientation_minus_is_the_counterprofile_for_P_W": True,
        "local_fixed_trace_matching_preserves_the_bulk_anomaly": False,
        "new_compensated_lift_is_an_original_Gammahat_representation": False,
        "full_frozen_nonabelian_flavor_representation_constructed": False,
    }


def matrices_and_reality():
    rows = []
    F = sp.diag(1/ZETA, ZETA)
    M_A = sp.diag(ZETA, 1/ZETA)
    for row in positive_blocks():
        n, phase = row["D_power"], row["phase"]
        h = sp.simplify(ZETA*sp.I**phase)
        H = sp.diag(h, sp.conjugate(h))
        K = sp.diag(sp.I**n, (-sp.I)**n)
        U = (-1)**n*sp.eye(2)
        Qd, Qw = sp.diag(n, -n), sp.diag(1, -1)
        plus, minus = sp.I**phase, -sp.I/(sp.I**phase)
        checks = {
            "H_unitary": clean(H.adjoint()*H) == sp.eye(2),
            "H_symplectic": clean(H.T*J*H) == J,
            "H_quaternionic_reality": clean(J*sp.conjugate(H)-H*J) == sp.zeros(2),
            "H_fourth_minus_identity": clean(H**4) == -sp.eye(2),
            "normal_compensator_product_identity": clean(M_A*F) == sp.eye(2),
            "commuting_Abelian_charges": H*Qd == Qd*H and H*Qw == Qw*H,
            "charge_pair_symplectic": Qd.T*J+J*Qd == sp.zeros(2) and Qw.T*J+J*Qw == sp.zeros(2),
            "effective_periodic_translations": clean(U*K**2) == sp.eye(2),
            "N1_pairing_constraint": sp.simplify(plus*minus*sp.I) == 1,
        }
        if not all(checks.values()):
            raise RuntimeError("new positive hyper block failed a matrix check")
        rows.append({**row, "effective_H": matrix_json(H), "external_C8_K": matrix_json(K),
                     "flavor_U_V": matrix_json(U), "Q_D": matrix_json(Qd), "Q_W": matrix_json(Qw),
                     "N1_plus_phase": str(plus), "N1_minus_phase": str(minus),
                     "N1_constant_projector_ranks": [int(projector(plus)), int(projector(minus))], "checks": checks})
    return {
        "status": "EXPLICIT_COMPENSATED_BLOCK_MATRICES_AND_SMW_PAIR_PACKAGING_ONLY",
        "positive_half_root": "z_n=n*d+u+v=n*d+w; negative half has all Abelian charges reversed",
        "actual_normal_isotropy": matrix_json(M_A), "conditional_flavor_compensator": matrix_json(F),
        "rows": rows,
        "SMW_normalization": "Use one half of the conjugate-pair trace. A full charged hyper R+R* is counted once per displayed multiplicity, not twice.",
        "full_independent_SU2_F_representation_asserted": False,
        "flavor_group_scope": "Only commuting Abelian F and the unitary multiplicity centralizers are used. The displayed opposite-charge 2x2 block is not an independent nonabelian SU2_F doublet. Its diagonal W action does not commute with the off-diagonal generators of the entire frozen Sp267 fundamental; the full old flavor representation has not been extended, and tensor-product partners may be necessary.",
        "continuous_SU2_R_assignment": "Standard (1,0) hyperinos are SU2_R singlets; their four real scalar partners form SU2_R doublets. No R charge is assigned to a hyperino to repair its geometric kernel.",
        "independent_discrete_R4_assignment_for_new_fields_frozen": False,
        "these_matrix_checks_construct_full_Gammahat_or_Pfaffian_gluing": False,
    }


def positive_spectrum():
    rows = []
    for n, coefficient in C.items():
        A = abs(coefficient)
        rows += [{"source_phase": 0, "D_power": n, "covering_U1_charge": 2*n, "W_charge": 1,
                  "multiplicity": A, "four_dimensional_chirality": "left", "N1_chiral_multiplets": A},
                 {"source_phase": 3, "D_power": -n, "covering_U1_charge": -2*n, "W_charge": -1,
                  "multiplicity": A, "four_dimensional_chirality": "left", "N1_chiral_multiplets": A}]
    anomaly = sp.expand(sum(row["multiplicity"]*I6(row["D_power"]*d+row["W_charge"]*w) for row in rows))
    if anomaly != 0 or sum(row["multiplicity"] for row in rows) != 8:
        raise RuntimeError("positive-hyper constant-mode spectrum changed")
    return {
        "status": "EXACT_CONSTANT_MODE_PROJECTORS_FOR_THE_SELECTED_FREE_COMPENSATED_HYPERS_NOT_A_DEFECT_MASS_SPECTRUM",
        "assumptions": "Periodic flat cover and effective translations1, selected effective H, no transverse flux, vanishing scalar expectation values and no added local interactions. This is a new free-hyper spectrum calculation.",
        "charge_and_chirality_rows": rows, "N1_chiral_multiplet_count": 8,
        "vectorlike_pairs_by_D_magnitude": {"0": 1, "1": 2, "2": 1},
        "same_count_for_counterprofile_orientation": True,
        "common_D_W_gauge_and_mixed_gravitational_I6": str(anomaly),
        "all_pair_members_are_Spin11_singlets": True,
        "four_dimensional_zero_modes_are_additional_massless_fields_in_this_free_candidate": True,
        "supersymmetric_mass_terms_or_background_lifting_these_modes_constructed": False,
        "V97_Dirac_gap_applied_to_this_carrier": False,
        "common_gauge_vectorlike_means_anomaly_free_under_independent_flavor_backgrounds": False,
        "full_normal_polynomial_is_identified_with_an_ordinary_4D_zero_mode_trace": False,
    }


def bulk_and_flavor_anomalies():
    rows = positive_blocks()
    bulk = sp.expand(sum(row["multiplicity"]*I8(row["D_power"]*d+w) for row in rows))
    expected = (3*d**4+sp.Rational(20,3)*d**3*w+6*d*d*w*w+sp.Rational(8,3)*d*w**3+sp.Rational(2,3)*w**4
                -P1*(d*d/2+sp.Rational(2,3)*d*w+w*w/3)+(7*P1**2-4*P2)/360)
    if sp.expand(bulk-expected) != 0 or bulk.coeff(P2) != -sp.Rational(1, 90):
        raise RuntimeError("bulk positive-hyper anomaly polynomial changed")
    flavor_rows = []
    for row in rows:
        n, phase, count = row["D_power"], row["phase"], row["multiplicity"]
        names = ["xi_%s_%s_%s" % (n, phase, k) for k in range(count)]
        roots = [n*d+u+v+sp.Symbol(name) for name in names]
        flavor_rows.append({**row, "unbroken_multiplicity_flavor_factor": "U(%s)" % count,
                            "extra_flavor_Chern_roots": names, "full_positive_half_roots": [str(z) for z in roots],
                            "I8": str(sum(I8(z) for z in roots)),
                            "C4_I6": str(sum(local_I6(4, phase, z) for z in roots)),
                            "C2_cover_I6": str(sum(local_I6(2, phase, z) for z in roots))})
    all_xi = {sp.Symbol(name): 0 for row in flavor_rows for name in row["extra_flavor_Chern_roots"]}
    full_bulk = sum(sp.sympify(row["I8"]) for row in flavor_rows)
    full_c4 = sum(sp.sympify(row["C4_I6"]) for row in flavor_rows)
    full_c2 = sum(sp.sympify(row["C2_cover_I6"]) for row in flavor_rows)
    if sp.expand(full_bulk.subs(all_xi)-bulk.subs(w,u+v)) != 0 or sp.expand(full_c4.subs(all_xi)-target_P(u+v)/4) != 0:
        raise RuntimeError("full multiplicity-flavor polynomial does not restrict to common backgrounds")
    zero_mode_flavor = sum((1 if row["phase"] == 0 else -1)*sum(I6(sp.sympify(z)) for z in row["full_positive_half_roots"])
                          for row in flavor_rows if row["phase"] in (0, 3))
    integrated = sp.expand((2*full_c4+2*full_c2).subs(x,0))
    if sp.expand(integrated-zero_mode_flavor) != 0 or integrated == 0:
        raise RuntimeError("independent-flavor zero-mode anomaly crosscheck failed")
    replacement = sp.expand(bulk-16*I8(sp.Integer(0)))
    if replacement.coeff(P2) != 0 or replacement.coeff(P1,2) != 0 or replacement == 0:
        raise RuntimeError("hypothetical neutral replacement anomaly cost failed")
    return {
        "one_full_hyper_I8": str(I8(sp.Symbol("z"))),
        "conventions": "Positive hyperino chirality; P1=p1(T6), P2=p2(T6) in I8. Separately p=p1(T4), x=c1(normal SO2), u=x/2 on the geometric restriction in fixed-locus I6. Ahat(T)=1-p1/24+(7p1^2-4p2)/5760.",
        "SMW_pair_I8_equals_one_line_I8": "[Ahat*(exp(z)+exp(-z))/2]_8=I8(z); no extra factor2",
        "common_root_bulk_I8": str(bulk), "with_normal_and_flavor_curvatures": str(sp.expand(bulk.subs(w,u+v))),
        "irreducible_P2_coefficient": str(bulk.coeff(P2)),
        "delta_H_V_T": [16, 0, 0], "delta_H_minus_V_plus_29T": 16,
        "ordinary_GS_quadratic_four_form_factorization_can_cancel_this_P2_term": False,
        "bulk_anomaly_can_be_ignored_because_regular_C4_traces_vanish": False,
        "restricted_no_go": "An additive nonempty sector of standard same-chirality (1,0) hypers, with the old vector/tensor/gravity spectrum unchanged, has a nonzero irreducible gravitational anomaly. Orbifold phases and Green-Schwarz products of degree-four classes do not change or cancel that coefficient.",
        "all_extensions_with_new_vector_tensor_or_other_sectors_excluded": False,
        "hypothetical_neutral_replacement": {
            "operation": "Replace sixteen identified old, genuinely gauge/normal/flavor-trivial full hypers by the candidate sixteen, instead of adding them. No old states are selected or removed here.",
            "delta_H_V_T": [0,0,0], "subtracted_I8": str(16*I8(sp.Integer(0))),
            "remaining_common_root_delta_I8": str(replacement),
            "irreducible_gravity_rank_cancels_under_this_assumption": True,
            "new_gauge_normal_flavor_and_mixed_anomalies_cancel": False,
            "old_neutral_states_and_projectors_identified": False,
            "old_localized_anomaly_or_zero_mode_subtraction_computed": False,
            "same_action_replacement_adopted": False,
        },
        "full_multiplicity_flavor_polynomial_rows": flavor_rows,
        "flavor_scope": "The sum of these rows retains every Chern root of the U(N_n,m) multiplicity centralizer commuting with the chosen gauge charges and rotation. By the splitting principle it specifies the invariant local polynomial for those unitary factors, not a claim about an unspecified larger flavor group.",
        "SU2_R_perturbative_terms_of_new_hyperinos": "0: the selected standard hyperinos are actual SU2_R singlets",
        "new_SU2_R_Witten_doublets_from_hyperinos": 0,
        "independent_discrete_R_flavor_and_global_anomalies_completed": False,
        "integrated_x_zero_flavor_polynomial": str(integrated),
        "independent_4D_zero_mode_flavor_polynomial": str(sp.expand(zero_mode_flavor)),
        "integrated_x_zero_index_crosscheck_exact": True,
        "generic_flavor_backgrounds_leave_extra_uncanceled_local_terms": True,
    }


def opposite_chirality_realization():
    rows = []
    for n, c in C.items():
        sign = 1 if c > 0 else -1
        rows += [{"D_power": n, "phase": 1, "multiplicity": abs(c), "six_dimensional_chirality": sign},
                 {"D_power": n, "phase": 2, "multiplicity": abs(c), "six_dimensional_chirality": -sign}]
    if sum(row["multiplicity"] for row in rows) != 8:
        raise RuntimeError("opposite-chirality physical count changed")
    c4, c2 = local_sum(rows,4), local_sum(rows,2)
    bulk = sp.expand(sum(row["six_dimensional_chirality"]*row["multiplicity"]*I8(row["D_power"]*d+w) for row in rows))
    if sp.expand(c4-target_P()/4) != 0 or sp.expand(2*c2+target_P()/2) != 0 or bulk != 0:
        raise RuntimeError("opposite-chirality anomaly cancellation failed")
    w1, w2 = u+v1+r1*y, u+v2+r2*y
    unequal_bulk = sp.expand(sum(c*(I8(n*d+w1)-I8(n*d+w2)) for n,c in C.items()))
    expected = d*d*(w1-w2)*(d+(w1+w2)/2)
    if sp.expand(unequal_bulk-expected) != 0:
        raise RuntimeError("opposite-chirality R/flavor mismatch polynomial failed")
    for row in rows:
        h = sp.simplify(ZETA*sp.I**row["phase"])
        left, right = (h/ZETA,ZETA*h) if row["six_dimensional_chirality"] == 1 else (ZETA*h,h/ZETA)
        row["positive_half_left_right_rotation"] = [str(sp.simplify(left)),str(sp.simplify(right))]
        row["constant_positive_half_left_right_projectors"] = [int(projector(left)),int(projector(right))]
        if row["constant_positive_half_left_right_projectors"] != [0,0]:
            raise RuntimeError("new opposite-chirality constant-mode projector changed")
    return {
        "status": "POSITIVE_FERMION_MULTIPLICITIES_REALIZE_SIGNED_VIRTUAL_TRACE_BUT_NOT_STANDARD_HYPER_ONLY_6D_N1_SUSY",
        "rows": rows, "SMW_chiral_block_count": 8, "chirality_plus_and_minus_counts": [4,4],
        "common_background_bulk_I8": str(bulk), "per_physical_stratum_I6": [str(c4),str(c4),str(2*c2)],
        "R_flavor_equality_required_for_displayed_bulk_cancellation": "The two opposing terms must have identical full continuous representations/background roots, not only equal gauge charge.",
        "general_roots_for_diagnostic": [str(w1),str(w2)],
        "general_R_flavor_mismatch_I8": str(unequal_bulk),
        "factored_mismatch": "d^2*(w1-w2)*(d+(w1+w2)/2)",
        "unequal_background_local_C4_I6": str(sp.expand((target_P(w1)+target_P(w2))/8)),
        "R_charges_r1_r2_in_diagnostic_are_not_assigned_to_standard_hyperinos": True,
        "SUSY_obstruction_scope": "In fixed 6D (1,0) supersymmetry, all standard hyperinos have one chirality and are SU2_R singlets. Opposite-chirality fermions belong instead to vector/gravity sectors with different R representations and additional bosons; replacing four hyperinos by opposite chirality singlets is not a hypermultiplet completion. New gauge or gravitational multiplets and their whole anomaly ledger have not been constructed.",
        "same_6D_N1_hyper_only_completion_exists": False,
        "all_other_SUSY_completions_excluded": False,
        "new_constant_projectors_computed_independently": True,
        "spatial_mass_operator_or_nonconstant_mass_spectrum_computed": False,
        "V97_charge_two_Dirac_gap_reused": False,
        "positive_kinetic_field_count_is_a_quantized_relative_determinant_action": False,
    }


def geometric_and_flavor_scope():
    q = sp.diag(1,-1)
    off = sp.Matrix([[0,1],[1,0]])
    if q*off-off*q == sp.zeros(2):
        raise RuntimeError("off-diagonal flavor was incorrectly treated as commuting")
    return {
        "unchanged_geometric_kernel": "D=(-1_Spin4,-1_Spin2) is identity in Spin6. A 6D spinor restricts with tangent bit1 and normal bit1, hence D acts+1.",
        "normal_M_twisted_hyperino_bits_T4_N2": [1,0],
        "normal_M_twisted_scalar_bits_T4_N2": [0,1],
        "D_on_each_M_twisted_field": -1,
        "opposite_6D_chirality_repairs_D": False,
        "independent_internal_F_or_R_character_repairs_D": False,
        "reason": "An independent internal factor evaluates to1 on the pure geometric kernel D, so no internal charge changes its failed sign. Repairing the A^4 equation alone is insufficient.",
        "conditional_category_change": "One can investigate a different correlated normal/flavor category in which D is paired with -1_F. This is not the unchanged Spin6/Gammahat category, and this helper does not install or prove that extension.",
        "conditional_genuine_line": "W=M*F, w=u+v; the compensating Cartan has holonomy zeta^-1 and its curvature v is retained",
        "original_P": str(target_P(u)), "conditional_P_W": str(target_P(u+v)),
        "introduced_flavor_term": str(sp.expand(target_P(u+v)-target_P(u))),
        "identifying_F_with_M_inverse": "v=-u makes W trivial and P_W=d^3; it removes the desired mixed d^2*u term instead of preserving the original target.",
        "flat_flavor_restriction": "v=0 is only a local curvature restriction; the order8 holonomy, torsion class, geometric-kernel descent and relative quantum gluing still need proof.",
        "offdiagonal_SU2_F_commutator_with_unit_charge": matrix_json(q*off-off*q),
        "full_independent_SU2_F_without_extra_partners_constructed": False,
        "full_frozen_Sp267_flavor_embedding_constructed": False,
        "centralizer_boundary": "The symplectic Cartan pair passes reality checks only for the stated commuting subgroup. A nontrivial diagonal U1_W on the same pair cannot commute with the old off-diagonal Sp267 generators. Restoring the entire original flavor factor may require tensor-product multiplicities; neither those particles nor their anomaly polynomial are supplied here.",
    }


@lru_cache(maxsize=1)
def _pure_json():
    return json.dumps({"geometric_and_flavor_scope":geometric_and_flavor_scope(),
                       "opposite_chirality_realization":opposite_chirality_realization(),
                       "positive_hyper_character_realization":character_realization(),
                       "explicit_matrices_and_SMW_packaging":matrices_and_reality(),
                       "positive_hyper_constant_spectrum":positive_spectrum(),
                       "positive_hyper_bulk_and_flavor_anomalies":bulk_and_flavor_anomalies()}, sort_keys=True, separators=(",",":"))


def build_certificate():
    load_parents()
    result = {"schema":"v98_transport_positive_physical_realization_v1",
              "input_core_hashes":{k:z[1] for k,z in PARENTS.items()}, "embedded_v97_mixed_core":MIXED_CORE,
              "scope":"Exact representation and polynomial alternatives under explicit compensated-lift assumptions; no unchanged Gammahat, complete supersymmetric action or full relative transport accepted.",
              **json.loads(_pure_json()),
              "terminal_decision":{
                  "positive_multiplicity_local_character_witness_found":True,
                  "minimum_hypers_in_linewise_regular_character_ansatz":16,
                  "extra_constant_N1_chiral_multiplets_in_selected_free_hyper_candidate":8,
                  "new_hyper_bulk_gravitational_anomaly_units":16,
                  "unchanged_bulk_spectrum_plus_hyper_only_repair_viable":False,
                  "opposite_chirality_hyper_only_6D_N1_completion_constructed":False,
                  "original_normal_M_Gammahat_kernel_repaired_by_independent_flavor":False,
                  "flavor_curvature_omitted":False,
                  "full_relative_quantized_transport_or_global_anomaly_cancellation_constructed":False,
                  "same_action_parent_accepted":False,"accepted_extensions":0,"closed_gates":[]},
              "primary_sources":[
                  {"url":"https://arxiv.org/abs/hep-th/0512019","use":"Section2 lists (1,0) multiplet chiralities and R indices; Section3.1 Eq3.5 gives H-V+29T=273 and the irreducible gravitational obstruction. This fixes the hyper-only SUSY/no-go scope."},
                  {"url":"https://arxiv.org/abs/2002.04619","use":"Section2 explicitly takes hyperfermions neutral under R while gravitino, dilatino and gauginos carry R charge. Their different R representations cannot be exchanged while keeping the old anomaly ledger."},
                  {"url":"https://arxiv.org/abs/1008.1062","use":"Section2 Eq2.6 relates the irreducible gravitational anomaly to H-V+29T. A fixed-point character cancellation is not a cancellation of the unlocalized bulk polynomial."},
                  {"url":"https://arxiv.org/abs/hep-th/0612212","use":"Shifted fixed-point anomaly kernels with normal Lorentz data; the exact kernel coefficients are rebound from the frozen V96/V97 chain and traced with the actual conjugate SMW pair."},
                  {"url":"https://web.math.ucsb.edu/~dai/book.pdf","use":"Spin representations and the twisted Dirac index: [Ahat ch]_8 gives the normalized full-hyper polynomial after the symplectic half-trace."},
              ]}
    result["core_sha256"] = canonical_sha(result)
    return result


def validate_certificate(result):
    if result.get("core_sha256") != canonical_sha(result) or result != build_certificate():
        raise RuntimeError("F98 physical-carrier certificate changed in arithmetic, lineage or scope")


if __name__ == "__main__":
    print(json.dumps(build_certificate(), indent=2, sort_keys=True))
