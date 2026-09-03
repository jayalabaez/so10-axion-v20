"""F99: actual replacement slots, fixed-bulk obstruction and flavor costs.

Only the new helper/test are modified. No old particles are removed, and no
new matter sector is installed. All conclusions retain their stated category.
"""
from __future__ import annotations

import copy
from functools import lru_cache
from itertools import product
import json
from pathlib import Path

import sympy as sp

import susy_v91_multipath_g1_frontier_master_audit as common
import v98_transport_physical_realization_audit as carrier


ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v98_route": ("SUSY_V98_GEOMETRIC_DESCENT_RESPONSE_AND_SECTION_AUDIT.json", "6cd7985cd073e6db6ab27ad3e1b22b312bd966696b8aba30e6f76c9735139767"),
    "v98_master": ("SUSY_V98_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json", "a1032f9531a12a91bfeb1ba0c13fb3e7703a60a70982f65e7122d237c11083cf"),
    "v92_route": ("SUSY_V92_PROJECTORS_LENS_WCS_COMPACT_DECK_ROOT_AUDIT.json", "3d4365681c9ebdbcbda6d9d57377a1046a6ab00b3a8b1b2290f2858a7ee4f4fb"),
    "v91_route": ("SUSY_V91_SPINC_QUANTIZATION_TENSOR_CONE_FINITE_TORSION_AUDIT.json", "4a581af0dd4cfc6fd3f66ef1e3ea2801b9770c67822d984a02deb602865c0322"),
}
EMBEDDED_CORES = {
    "transport_physical_realization": "2945976d514dca4a0f5d58a36de2289b9110f97eea12f093ec9305a9124688bb",
    "gammahat_compensator": "ecd2788cdfa6825e65e052406f586b138d01964c703621f02748c366743db769",
    "smooth_singlet_projectors": "5d4c91e596ef5182b63f5be4869a41c0c79005dc4dd0fc8cf3683d12c66363fd",
}
canonical_sha, file_sha = common.canonical_sha, common.file_sha
d, u, v, w, x, p, P1, P2 = carrier.d, carrier.u, carrier.v, carrier.w, carrier.x, carrier.p, carrier.P1, carrier.P2
I8, I6 = carrier.I8, carrier.I6
Q = (0, 2, 4, 6, 8)
OLD_COUNTS = (144, 3, 19, 11, 90)
G = sp.Matrix([[0, 1], [1, 0]])


def matrix(rows):
    return sp.Matrix([[sp.sympify(z) for z in row] for row in rows])


def clean(value):
    return sp.Matrix(value).applyfunc(sp.simplify)


def mj(value):
    return [[str(z) for z in row] for row in clean(value).tolist()]


def load_inputs():
    parents = {key: common.load_bound(ROOT/name, core) for key, (name, core) in PARENTS.items()}
    route, master, old = parents["v98_route"], parents["v98_master"], parents["v92_route"]
    if master["input_core_hashes"]["v98_route"] != PARENTS["v98_route"][1] or master["next_required_action"]["id"] != "F99_SPECTATOR_OR_SPINC_INFLOW_AND_ORIGINAL_SECTION_ELIMINATION":
        raise RuntimeError("V98 master lineage or F99 obligation changed")
    for key in ("transport_physical_realization", "gammahat_compensator"):
        saved = route[key]
        if saved.get("core_sha256") != EMBEDDED_CORES[key] or canonical_sha(saved) != EMBEDDED_CORES[key]:
            raise RuntimeError("F98 carrier or geometric certificate changed")
    saved = old["smooth_singlet_projectors"]
    if saved.get("core_sha256") != EMBEDDED_CORES["smooth_singlet_projectors"] or canonical_sha(saved) != EMBEDDED_CORES["smooth_singlet_projectors"]:
        raise RuntimeError("the actual old singlet projectors changed")
    if saved["input_core_hashes"]["v91"] != PARENTS["v91_route"][1]:
        raise RuntimeError("old projector-to-scout edge changed")
    for basename in ("v98_transport_physical_realization_audit", "v98_gammahat_compensator_audit"):
        for name in (basename+".py", "test_"+basename+".py"):
            if file_sha(ROOT/name) != route["artifact_hashes"][name]:
                raise RuntimeError("F98 source/test differs from its frozen route: "+name)
    for name in ("v92_singlet_projector_certificate.py", "test_v92_singlet_projector_certificate.py"):
        if file_sha(ROOT/name) != old["artifact_hashes"][name]:
            raise RuntimeError("actual old projector source/test changed: "+name)
    v91 = parents["v91_route"]
    for name, key in (("susy_v91_spinc_quantization_tensor_cone_finite_torsion_audit.py", "generator_sha256"),
                      ("test_susy_v91_spinc_quantization_tensor_cone_finite_torsion_audit.py", "test_sha256")):
        if file_sha(ROOT/name) != v91["artifact_hashes"][key]:
            raise RuntimeError("the smooth-bulk source/test changed: "+name)
    return parents


def frozen_bulk_data(v91):
    scout = v91["quantized_scout"]
    iso = v91["tensor_cone"]["F4_lattice_map"]
    conversion = sp.Matrix(iso["columns_in_S_F_basis"])
    a = conversion.inv()*sp.Matrix(iso["a_maps_to_K"])
    b = conversion.inv()*sp.Matrix(iso["b_maps_to_S"])
    c = sp.Matrix([sp.Rational(z) for z in scout["c"]])
    if (list(a), list(b), list(c), scout["singlet_counts_by_q0_q2_q4_q6_q8"], scout["bulk_vector_charge_magnitudes"]) != ([2, 2], [2, -1], [-472, -148], list(OLD_COUNTS), [6, 4, 6]):
        raise RuntimeError("the actual old smooth bulk changed")
    if (-6*(a.T*G*c)[0], 3*(c.T*G*c)[0], (b.T*G*c)[0]) != (7440, 419136, 176):
        raise RuntimeError("frozen bulk anomaly normalization changed")
    return a, b, c


def old_slot_certificate(saved):
    witness = saved["eleven_mode_normal_aligned_witness"]
    blocks = [r for r in witness["direct_sum_blocks"] if r["certificate"]["q_magnitude"] == 0]
    if len(blocks) != 1 or blocks[0]["copies"] != 36 or blocks[0]["certificate"]["kind"] != "four_orbit":
        raise RuntimeError("old q0 fields are not the frozen 36 orbit copies")
    block = blocks[0]["certificate"]
    A, U, V = (matrix(block["effective_plus"][k]) for k in ("A", "U", "V"))
    Am, Um, Vm = (matrix(block["effective_minus_column"][k]) for k in ("A", "U", "V"))
    ranks = [len((aa-sp.eye(4)).col_join(uu-sp.eye(4)).col_join(vv-sp.eye(4)).nullspace()) for aa, uu, vv in ((A, U, V), (Am, Um, Vm))]
    strata = {}
    for point, word, order in (("z00", "A", 4), ("z11", "UA", 4), ("z10", "UA2", 2), ("z01", "VA2", 2)):
        S = {"A": A, "UA": U*A, "UA2": U*A*A, "VA2": V*A*A}[word]
        traces = [sp.simplify(sp.trace(S**j)) for j in range(1, order)]
        if any(z != 0 for z in traces):
            raise RuntimeError("old neutral orbit has a nonzero nonidentity trace")
        eta = sp.Symbol("eta")
        phase_multiplicities = [1]*4 if order == 4 else [2, 2]
        polynomial = sp.expand(sum(count*carrier.local_I6(order, m, eta) for m, count in enumerate(phase_multiplicities)))
        if polynomial != 0:
            raise RuntimeError("old orbit's full normal/gauge/flavor local trace is nonzero")
        strata[point] = {"stabilizer": word, "order": order, "matrix": mj(S), "nonidentity_traces": [str(z) for z in traces],
                         "eigenphase_multiplicities": phase_multiplicities, "I6_at_arbitrary_commuting_multiplicity_root_eta": str(polynomial)}
    R = carrier.ZETA*A
    T = sp.diag(1, sp.I, -1, -sp.I)*A**2
    quaternionic_checks = [clean(T*sp.conjugate(Z)-Z*T) == sp.zeros(4) for Z in (R, U, V)]
    pair_intertwiner = sp.diag(sp.eye(4), T)
    pair_checks = [clean(pair_intertwiner*matrix(block["underlying_flavor"][key])*pair_intertwiner.inv()-sp.diag(Z, Z)) == sp.zeros(8)
                   for key, Z in (("A", R), ("U", U), ("V", V))]
    joint = [(str(U[i, i]), str(V[i, i])) for i in range(4)]
    if ranks != [0, 0] or len(set(joint)) != 4 or not all(quaternionic_checks+pair_checks) or clean(T*sp.conjugate(T)) != -sp.eye(4):
        raise RuntimeError("neutral orbit irreducibility, reality or constant modes changed")
    return {
        "frozen_block_certificate_sha256": canonical_sha(block),
        "source_total_q0_hypers": 144, "source_four_orbit_copies": 36,
        "chosen_actual_copy_labels": ["q0_four_orbit_copy_"+str(j) for j in range(1, 5)],
        "labels_are_basis_choices_among_identical_frozen_copies": True,
        "selected_six_dimensional_hypers": 16, "remaining_identical_q0_orbit_copies": 32,
        "effective_plus_A_U_V": {key: mj(Z) for key, Z in zip(("A", "U", "V"), (A, U, V))},
        "underlying_flavor": copy.deepcopy(block["underlying_flavor"]),
        "constant_plus_minus_dimensions_per_copy": ranks, "removed_constant_N1_chiral_modes": 0,
        "strata": strata,
        "old_neutral_means_trivial_under_full_flavor": False,
        "old_flavor_background": "A commuting U4 acts on the four selected orbit copies; its roots eta_a each occur four times. The actual old smooth polynomial is 4*sum_a I8(eta_a), not16*I8(0) on arbitrary flavor backgrounds.",
        "irreducible_plus_orbit": {
            "joint_U_V_eigenvalue_pairs": joint,
            "proof": "The four joint translation eigenlines are distinct, and A cycles them transitively. Every invariant complex subspace is therefore zero or the entire four-dimensional orbit.",
            "complex_dimension": 4, "quaternionic_intertwiner_T": mj(T),
            "T_conjugate_T": mj(T*sp.conjugate(T)), "intertwining_checks": quaternionic_checks,
            "full_pair_complex_intertwiner": mj(pair_intertwiner),
            "full_pair_to_R_plus_R_checks_A_U_V": pair_checks,
            "full_eight_component_pair_is_two_identical_four_irreps": True,
            "full_q0_symplectic_space_is_72_copies_of_this_irrep": True,
            "any_equivariant_q0_removal_has_even_hyper_count": True,
            "reason_for_even_count": "A q0 hyper subrepresentation with r full-hyper units has complex symplectic dimension2r. The old space is isotypic with irreducible complex dimension4, so2r must be divisible by4. This statement allows arbitrary mixing of identical copies, not only literal deletion of displayed four-orbits.",
        },
        "slot_selection_preserves_full_old_Sp267": False,
        "slot_selection_is_an_accepted_replacement": False,
    }


def all_removals(total):
    if type(total) is not int or not 0 <= total <= sum(OLD_COUNTS):
        raise ValueError("removal count must fit the actual spectrum")
    rows = []
    for n2 in range(min(OLD_COUNTS[1], total)+1):
        for n4 in range(min(OLD_COUNTS[2], total-n2)+1):
            for n6 in range(min(OLD_COUNTS[3], total-n2-n4)+1):
                for n8 in range(min(OLD_COUNTS[4], total-n2-n4-n6)+1):
                    n0 = total-n2-n4-n6-n8
                    if n0 <= OLD_COUNTS[0]:
                        rows.append((n0, n2, n4, n6, n8))
    return rows


def removal_moments(row):
    return sum(n*r*r for n, r in zip(row, range(5))), sum(n*r**4 for n, r in zip(row, range(5)))


def obstruction_row(removed, added_m2=24, added_m4=72):
    m2, m4 = removal_moments(removed)
    A, B = added_m2-m2, added_m4-m4
    return {"removed_counts_q0_q2_q4_q6_q8": list(removed), "A": A, "B": B,
            "necessary_quartic_residual": 108*B-3456*A-A*A}


def replacement_obstruction(a, b, c):
    A, B = sp.symbols("A B")
    dc1, dc2 = sp.symbols("dc1 dc2")
    delta = sp.Matrix([dc1, dc2])
    solution = sp.solve([(a.T*G*delta)[0]+4*A/6, (b.T*G*delta)[0]], (dc1, dc2))
    shift = delta.subs(solution)
    expected = sp.Matrix([-2*A/9, -A/9])
    polynomial = sp.expand((c+shift).dot(G*(c+shift))-c.dot(G*c)-16*B/3)
    if shift != expected or sp.expand(polynomial+sp.Rational(4, 81)*(108*B-3456*A-A*A)) != 0:
        raise RuntimeError("fixed-bulk elimination changed")
    rows = [obstruction_row(row) for row in all_removals(16)]
    good = [row for row in rows if row["necessary_quartic_residual"] == 0]
    if len(rows) != 2956 or good:
        raise RuntimeError("actual minimal replacement obstruction failed")
    negative_cases = [{"t": t, "A": -36*t, "required_fourth_moment_excess_over_16_times_second": -312+576*t-12*t*t} for t in range(1, 7)]
    if min(r["required_fourth_moment_excess_over_16_times_second"] for r in negative_cases) != 252:
        raise RuntimeError("analytic bounded-moment exclusion changed")
    neutral_shift = shift.subs(A, 24)
    candidate_c = c+neutral_shift
    return {
        "scope": "Exactly sixteen new V98 hyper units replacing sixteen actual old Spin11-singlet hypers, with old Spin11/vector/gravity/tensor content and a,b in U fixed; any old projector choice is allowed in this necessary charge-only screen. No extra dynamical spectator vector is installed.",
        "a": [str(z) for z in a], "b": [str(z) for z in b], "old_c": [str(z) for z in c],
        "tensor_pairing_U": [[0, 1], [1, 0]],
        "old_counts_q0_q2_q4_q6_q8": list(OLD_COUNTS),
        "new_carrier_counts_q0_q2_q4_q6_q8": [4, 8, 4, 0, 0],
        "variables": "A=24-sum_removed(q/2)^2, B=72-sum_removed(q/2)^4; deltaD2=4A, deltaD4=16B",
        "equations": ["a.c'=-D2'/6", "b.c'=176", "3*c'.c'=D4'"],
        "unique_c_shift": [str(z) for z in shift],
        "necessary_and_sufficient_quartic_equation_after_first_two": "108*B-3456*A-A^2=0",
        "rational_factorization_test_not_only_integrality_test": True,
        "enumerated_actual_removal_count": len(rows), "enumerated_rows_sha256": canonical_sha(rows),
        "rationally_factorizing_removals": good,
        "analytic_proof": [
            "The quartic equation implies A^2 divisible by108, so A=18k with k integer.",
            "Every allowed r=q/2 obeys r^4-r^2 divisible by12. Hence B-A is divisible by12; substitution B=576k+3k^2 forces k even. Thus A is divisible by36.",
            "Sixteen removed charges in0..4 give -232<=A<=24. The only cases are A=0 and A=-36t for1<=t<=6.",
            "For negative A, the required removed fourth moment exceeds16 times its second moment by -312+576t-12t^2, positive in every case. This contradicts r^4<=16r^2 for each allowed charge.",
            "For A=0, old removed moments must be(24,72). Their difference48 forces n(q4)=4 and n(q6)=n(q8)=0, after which n(q2)=8. The actual spectrum has only3 q2 hypers.",
        ],
        "negative_A_cases": negative_cases,
        "A_zero_forced_removal_counts": [4, 8, 4, 0, 0],
        "actual_neutral_four_orbit_example": {
            "removed_counts": [16, 0, 0, 0, 0], "resulting_counts": [132, 11, 23, 11, 90],
            "deltaD2": 96, "deltaD4": 1152, "c_prime": [str(z) for z in candidate_c],
            "c_prime_squared": str(candidate_c.dot(G*candidate_c)),
            "required_D4_prime_over3": str(c.dot(G*c)+384),
            "quartic_mismatch": str(polynomial.subs({A: 24, B: 72})),
            "c_prime_integral": False,
        },
        "some_other_a_b_tensor_spectrum_or_charge_alphabet_excluded": False,
        "V98_response_only_Spin_c_option_excluded": False,
        "extra_W_flavor_GS_coefficients_can_fix_failure_on_W_zero_restriction": False,
    }


def regular_extension_screen(c):
    records = []
    for extra in (1, 2):
        total = 16+4*extra
        removals = all_removals(total)
        for t0 in range(extra+1):
            for t1 in range(extra-t0+1):
                t2 = extra-t0-t1
                rows = [obstruction_row(row, 24+4*t1+16*t2, 72+4*t1+64*t2) for row in removals]
                good = []
                for row in rows:
                    if row["necessary_quartic_residual"] != 0:
                        continue
                    A = row["A"]
                    cp = c+sp.Matrix([-sp.Rational(2*A, 9), -sp.Rational(A, 9)])
                    half = (cp+4*sp.Matrix([2, -1]))/8
                    good.append({**row, "c_prime": [str(z) for z in cp],
                                 "ordinary_quotient_half_source": [str(z) for z in half],
                                 "ordinary_quotient_source_integral": all(z.q == 1 for z in half),
                                 "q0_removal_count_even": row["removed_counts_q0_q2_q4_q6_q8"][0] % 2 == 0})
                records.append({"total_new_and_removed_hypers": total, "regular_extra_t0_t1_t2": [t0, t1, t2],
                                "candidate_counts_q0_q2_q4_q6_q8": [4+4*t0, 8+4*t1, 4+4*t2, 0, 0],
                                "new_free_N1_chiral_count_before_any_replacement": 8+2*extra,
                                "actual_removal_vectors_checked": len(rows), "all_rows_sha256": canonical_sha(rows),
                                "rational_candidates": good})
    survivors = [(r, g) for r in records for g in r["rational_candidates"]]
    if len(survivors) != 1 or survivors[0][0]["regular_extra_t0_t1_t2"] != [0, 1, 1] or survivors[0][1]["removed_counts_q0_q2_q4_q6_q8"] != [19, 0, 0, 0, 5]:
        raise RuntimeError("bounded regular-character extension screen changed")
    return {
        "scope": "Only add one or two regular C4 characters to the same D powers0,1,2, preserving the signed nonidentity character. Remove an equal number of actual old singlets, with old a,b and all other bulk multiplets fixed.",
        "complete_solution": "A_n=|c_n|+t_n, t_n>=0; orientation-minus N_m=(A_n,A_n-c_n,A_n+c_n,A_n), c=(1,-2,1)",
        "records": records,
        "number_of_twenty_hyper_variants": 3, "number_of_twenty_four_hyper_variants": 6,
        "twenty_hyper_rational_candidates": 0, "twenty_four_hyper_rational_candidates": 1,
        "sole_rational_scout_rejected_by_frozen_quotient_quantization": True,
        "sole_rational_scout_rejected_by_actual_q0_projector_divisibility": True,
        "q0_projector_reason": "The sole scout removes19 neutral hypers, i.e.38 complex symplectic components. The frozen neutral representation contains only complex irreducibles of dimension4;38 is not a multiple of4. Continuous gauge charge is retained, so q0 cannot mix with q8 despite their equal finite C8 residue.",
        "at_least_one_q8_Phi_line_would_be_removed_in_a_literal_block_selection": True,
        "q8_scope": "A five-hyper removal from22 charged four-orbits plus the two q8 Phi lines needs one of those lines in a literal whole-block selection; this is not used as the general obstruction.",
        "surviving_frozen_category_candidates": 0,
        "all_larger_regular_additions_or_other_carriers_excluded": False,
    }


def full_flavor_polynomials(saved):
    eta = sp.symbols("eta0:4")
    removed = sp.expand(4*sum(I8(z) for z in eta))
    rows = []
    for block in carrier.positive_blocks(-1):
        n, m, count = block["D_power"], block["phase"], block["multiplicity"]
        roots = [n*d+w+sp.Symbol("xi_%s_%s_%s" % (n, m, k)) for k in range(count)]
        rows.append({**block, "multiplicity_flavor_factor": "U(%s)" % count,
                     "roots": [str(z) for z in roots],
                     "I8": str(sum(I8(z) for z in roots)),
                     "C4_I6": str(sum(carrier.local_I6(4, m, z) for z in roots)),
                     "C2_cover_I6": str(sum(carrier.local_I6(2, m, z) for z in roots))})
    new_bulk = sum(sp.sympify(row["I8"]) for row in rows)
    new_c4 = sum(sp.sympify(row["C4_I6"]) for row in rows)
    new_c2 = sum(sp.sympify(row["C2_cover_I6"]) for row in rows)
    xi = sorted(new_bulk.free_symbols-{d, w, P1, P2}, key=str)
    delta = sp.expand(new_bulk-removed)
    common_delta = sp.expand(delta.subs({z: 0 for z in tuple(xi)+eta}))
    expected = sp.sympify(saved["positive_hyper_bulk_and_flavor_anomalies"]["hypothetical_neutral_replacement"]["remaining_common_root_delta_I8"])
    if sp.expand(common_delta-expected) != 0 or delta.coeff(P2) != 0:
        raise RuntimeError("actual-slot replacement polynomial failed its common-root check")
    independent_modes = sum((1 if row["phase"] == 0 else -1)*sum(I6(sp.sympify(z)) for z in row["roots"])
                            for row in rows if row["phase"] in (0, 3))
    integrated = sp.expand((2*new_c4+2*new_c2).subs(x, 0))
    if sp.expand(integrated-independent_modes) != 0 or integrated == 0:
        raise RuntimeError("independent-flavor constant-mode check failed")
    common_c4 = sp.expand(new_c4.subs({z: 0 for z in xi}))
    common_c2 = sp.expand(2*new_c2.subs({z: 0 for z in xi}))
    if sp.expand(common_c4+d*d*(d+w)/4) != 0 or sp.expand(common_c2-d*d*(d+w)/2) != 0:
        raise RuntimeError("counterprofile normal/flavor curvature was lost")
    return {
        "normalization": "One full hyper is I8(z)=[Ahat*(exp(z)+exp(-z))/2]_8. P1,P2 refer to T6; p,x refer to T4 and the normal SO2 line in localized I6. No SMW double counting.",
        "old_removed_multiplicity_U4_roots": [str(z) for z in eta],
        "old_removed_I8": str(removed), "old_removed_local_I6_all_strata": "0 for every commuting U4 background",
        "new_independent_flavor_blocks": rows,
        "full_replacement_delta_I8": str(delta),
        "common_flavor_zero_delta_I8": str(common_delta),
        "with_normal_compensator_curvatures_retained": str(sp.expand(common_delta.subs(w, u+v))),
        "irreducible_gravity_delta_P2": str(delta.coeff(P2)),
        "new_local_counterprofile_on_common_flavor_backgrounds": [str(common_c4), str(common_c4), str(common_c2)],
        "independent_flavor_integrated_I6": str(integrated),
        "independent_4D_zero_mode_I6": str(sp.expand(independent_modes)),
        "index_crosscheck_exact": True,
        "new_constant_mode_charge_rows": copy.deepcopy(saved["positive_hyper_constant_spectrum"]["charge_and_chirality_rows"]),
        "old_constant_modes_removed": 0, "new_constant_modes_added": 8,
        "conditional_total_old_plus_new_N1_chiral_modes": 19,
        "common_D_W_zero_mode_anomaly_delta": "0",
        "independent_flavor_anomaly_delta_vanishes": False,
        "masses_or_interactions_constructed": False, "V97_Dirac_gap_reused": False,
        "count_and_polynomial_replacement_is_installed_or_consistent": False,
    }


def flavor_GS_and_representation_screen():
    z, c2, c3, c4 = sp.symbols("z c2 c3 c4")
    new = 4*I8(z)-z*z*c2/2+z*c3/2+c2*c2/12-c4/6+P1*c2/24
    old = 16*I8(sp.Integer(0))+c2*c2/3-2*c4/3+P1*c2/6
    diagonal_delta = sp.expand(new-old)
    pi = sp.diag(1, 0)
    rotation = sp.Matrix([[0, 1], [-1, 0]])
    symplectic_generator = sp.diag(rotation, rotation)
    selected_pair = sp.diag(pi, pi)
    J = sp.Matrix([[0, 0, 1, 0], [0, 0, 0, 1], [-1, 0, 0, 0], [0, -1, 0, 0]])
    if symplectic_generator.T*J+J*symplectic_generator != sp.zeros(4) or selected_pair*symplectic_generator-symplectic_generator*selected_pair == sp.zeros(4):
        raise RuntimeError("full flavor subrepresentation obstruction failed")
    return {
        "independent_new_SU4_test": {
            "block": "D_power1, phase1, multiplicity4 in the orientation-minus candidate",
            "z": "d+w=d+u+v", "SU4_fundamental_I8": str(sp.expand(new)),
            "primitive_c4_coefficient": "-1/6", "z_times_c3_coefficient": "1/2",
            "degree_four_invariant_GS_classes_on_this_restriction": ["P1", "z^2", "c2"],
            "ordinary_tensor_GS_products_can_cancel_c4_or_z_c3": False,
            "required_if_full_independent_flavor_anomaly_is_to_be_canceled": "Other sectors must supply opposite primitive c4 and z*c3 coefficients, or the flavor/background category must change. Adding arbitrary GS tensors alone cannot produce these primitive terms.",
        },
        "diagonal_old_new_SU4_test": {
            "old_representation": "four SU4 fundamentals from the four internal orbit dimensions, using the U4 multiplicity symmetry of the four removed actual copies",
            "new_representation": "one SU4 fundamental in the multiplicity4 new block; all other new blocks are singlets under this chosen diagonal SU4",
            "old_I8": str(sp.expand(old)), "replacement_delta_I8": str(diagonal_delta),
            "primitive_c4_delta_coefficient": str(diagonal_delta.coeff(c4)),
            "z_times_c3_delta_coefficient": str(diagonal_delta.coeff(c3).coeff(z)),
            "this_flavor_identification_removes_primitive_anomaly_change": False,
        },
        "global_flavor_vs_gauge_scope": "A nonzero background 't Hooft anomaly of a genuine global flavor symmetry is not by itself a quantum inconsistency. These are exact polynomial/GS-trivialization obstructions if arbitrary independent flavor backgrounds are required to cancel, or if those symmetries are gauged. No claim that the old QK/composite connection equals an arbitrary independent flavor gauge field is made.",
        "full_old_Sp267_compatibility": {
            "proper_sixteen_hyper_subrepresentation_of_unchanged_fundamental_exists": False,
            "proof": "The defining complex Sp267 fundamental is irreducible. An equivariant projector is scalar by Schur's lemma, so a proper rank32 symplectic subspace is not a full-Sp267 representation. The displayed generator already mixes a selected and unselected neutral pair. This does not deny selecting orbit copies after restricting to a smaller commuting subgroup.",
            "small_symplectic_generator": mj(symplectic_generator), "selection_projector": mj(selected_pair),
            "nonzero_commutator": mj(selected_pair*symplectic_generator-symplectic_generator*selected_pair),
            "full_flavor_is_unbroken_by_original_gauging_and_twists": False,
            "smaller_commuting_subgroup_replacement_constructed_at_representation_level": True,
            "global_QK_SUSY_action_away_from_origin_constructed": False,
        },
        "no_negative_physical_multiplicities_used": True,
        "opposite_chirality_or_extra_vector_tensor_completion_constructed": False,
        "all_possible_new_multiplet_completions_excluded": False,
    }


@lru_cache(maxsize=1)
def _math_json(projector_json, scout_json, matter_json):
    projector, scout, matter = (json.loads(z) for z in (projector_json, scout_json, matter_json))
    a, b, c = frozen_bulk_data(scout)
    return json.dumps({"actual_old_slots": old_slot_certificate(projector),
                       "minimal_sixteen_replacement_obstruction": replacement_obstruction(a, b, c),
                       "bounded_regular_character_extensions": regular_extension_screen(c),
                       "full_independent_flavor_replacement": full_flavor_polynomials(matter),
                       "flavor_GS_and_full_representation_scope": flavor_GS_and_representation_screen()}, sort_keys=True, separators=(",", ":"))


def build_certificate():
    parents = load_inputs()
    result = {
        "schema": "v99_actual_spectator_replacement_and_full_flavor_anomaly_audit_v1",
        "status": "ACTUAL_SLOTS_IDENTIFIED__MINIMAL_REPLACEMENT_REJECTED__SOLE_24_SCOUT_FAILS_QUANTIZATION_AND_PROJECTORS__PARENT_OPEN",
        "input_core_hashes": {key: value[1] for key, value in PARENTS.items()},
        "embedded_parent_cores": copy.deepcopy(EMBEDDED_CORES),
        **json.loads(_math_json(json.dumps(parents["v92_route"]["smooth_singlet_projectors"], sort_keys=True),
                               json.dumps(parents["v91_route"], sort_keys=True),
                               json.dumps(parents["v98_route"]["transport_physical_realization"], sort_keys=True))),
        "terminal_decision": {
            "actual_old_slots_and_removed_local_polynomial_identified": True,
            "all_actual_sixteen_for_sixteen_singlet_replacements_with_frozen_other_bulk_rejected": True,
            "twenty_and_twenty_four_regular_extensions_exhausted_in_stated_ansatz": True,
            "full_independent_flavor_curvatures_retained": True,
            "same_action_SUSY_spectrum_or_quantized_GS_completion_constructed": False,
            "full_old_Sp267_flavor_embedding_constructed": False,
            "all_spectator_carriers_or_V98_response_only_option_excluded": False,
            "microscopic_parent_accepted": False, "theory_complete": False, "closed_gates": [],
        },
        "primary_sources": [
            {"url": "https://arxiv.org/abs/1803.07998", "use": "Equations2.9-2.12 fix the abelian/mixed anomaly moment equations; Section2 distinguishes dynamical gauge consistency from uncanceled global flavor 't Hooft anomalies. Both distinctions are retained in the derived replacement tests."},
            {"url": "https://arxiv.org/abs/1110.5916", "use": "Six-dimensional(1,0) anomaly factorization with abelian and nonabelian factors; the fixed U-lattice moment elimination and finite replacement search are independently computed here."},
            {"url": "https://arxiv.org/abs/hep-th/0512019", "use": "Sections2 and3 give hypermultiplet chirality/Sp1R assignments, the symmetric QK target and irreducible quartic versus GS factorization conditions. The proper-flavor-subspace and primitive c4 tests are derived explicitly."},
            {"url": "https://arxiv.org/abs/1808.01334", "use": "Global Green-Schwarz cancellation requires quantized lattice and differential data beyond rational factorization; the sole rational24 scout is not promoted past its half-integral quotient source."},
            {"url": "https://arxiv.org/abs/hep-th/0612212", "use": "The shifted fixed-point index kernel with normal curvature is inherited from the bound V98 implementation and evaluated on the actual old orbit matrices; zero-mode counts are checked separately."},
        ],
    }
    result["core_sha256"] = canonical_sha(result)
    return result


def validate_certificate(result):
    if result.get("core_sha256") != canonical_sha(result) or result != build_certificate():
        raise RuntimeError("F99 replacement arithmetic, source binding or scope changed")


if __name__ == "__main__":
    print(json.dumps(build_certificate(), sort_keys=True, indent=2))
