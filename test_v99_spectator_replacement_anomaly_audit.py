import copy
import json
from itertools import combinations, product
import unittest
from unittest.mock import patch

import sympy as sp

import v99_spectator_replacement_anomaly_audit as audit


class TestV99SpectatorReplacement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()
        cls.parents = audit.load_inputs()

    def test_canonical_parents_and_fresh_validation(self):
        self.assertEqual(self.report["input_core_hashes"], {k: v[1] for k, v in audit.PARENTS.items()})
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        audit.validate_certificate(self.report)

    def test_actual_source_and_test_hash_changes_rejected(self):
        original = audit.file_sha
        def changed(path):
            return "0"*64 if path.name == "test_v92_singlet_projector_certificate.py" else original(path)
        with patch.object(audit, "file_sha", side_effect=changed):
            with self.assertRaises(RuntimeError):
                audit.load_inputs()

    def test_a_b_c_recovered_from_frozen_isometry_and_scout(self):
        a, b, c = audit.frozen_bulk_data(self.parents["v91_route"])
        self.assertEqual(list(a), [2, 2])
        self.assertEqual(list(b), [2, -1])
        self.assertEqual(list(c), [-472, -148])
        self.assertEqual((a.T*audit.G*a)[0], 8)
        self.assertEqual((b.T*audit.G*b)[0], -4)
        self.assertEqual(-6*(a.T*audit.G*c)[0], 7440)
        self.assertEqual(3*(c.T*audit.G*c)[0], 419136)

    def test_four_actual_neutral_orbit_copies_are_identified(self):
        row = self.report["actual_old_slots"]
        self.assertEqual(row["source_four_orbit_copies"], 36)
        self.assertEqual(row["selected_six_dimensional_hypers"], 16)
        self.assertEqual(row["remaining_identical_q0_orbit_copies"], 32)
        self.assertEqual(row["chosen_actual_copy_labels"], ["q0_four_orbit_copy_"+str(i) for i in range(1, 5)])
        old = self.parents["v92_route"]["smooth_singlet_projectors"]["eleven_mode_normal_aligned_witness"]
        blocks = [r for r in old["direct_sum_blocks"] if r["certificate"]["q_magnitude"] == 0]
        self.assertEqual(audit.canonical_sha(blocks[0]["certificate"]), row["frozen_block_certificate_sha256"])

    def test_actual_plus_and_minus_constant_kernel_is_zero(self):
        row = self.report["actual_old_slots"]
        A, U, V = [audit.matrix(row["effective_plus_A_U_V"][k]) for k in ("A", "U", "V")]
        for aa, uu, vv in ((A, U, V), (-sp.I*A.inv().T, U.inv().T, V.inv().T)):
            stacked = (aa-sp.eye(4)).col_join(uu-sp.eye(4)).col_join(vv-sp.eye(4))
            self.assertEqual(stacked.rank(), 4)
        self.assertEqual(row["removed_constant_N1_chiral_modes"], 0)

    def test_actual_nonidentity_character_vanishes_at_all_four_strata(self):
        row = self.report["actual_old_slots"]
        for point, item in row["strata"].items():
            S = audit.matrix(item["matrix"])
            self.assertEqual(S**item["order"], sp.eye(4), point)
            for power in range(1, item["order"]):
                self.assertEqual(sp.trace(S**power), 0, point)
            self.assertEqual(item["I6_at_arbitrary_commuting_multiplicity_root_eta"], "0")

    def test_full_normal_shifted_trace_not_only_four_dimensional_zero_modes(self):
        eta = sp.Symbol("eta")
        self.assertEqual(sp.expand(sum(audit.carrier.local_I6(4, m, eta) for m in range(4))), 0)
        self.assertEqual(sp.expand(sum(2*audit.carrier.local_I6(2, m, eta) for m in range(2))), 0)
        self.assertNotEqual(audit.carrier.local_I6(4, 0, eta), 0)

    def test_old_orbit_flavor_reality_is_preserved(self):
        row = self.report["actual_old_slots"]["underlying_flavor"]
        J = audit.matrix(row["symplectic_J"])
        self.assertEqual(J*sp.conjugate(J), -sp.eye(8))
        for key in ("A", "U", "V", "external_k"):
            Z = audit.matrix(row[key])
            self.assertEqual(audit.clean(Z.T*J*Z), J)
            self.assertEqual(audit.clean(J*sp.conjugate(Z)-Z*J), sp.zeros(8))

    def test_four_dimensional_complex_irrep_commutant_is_scalar(self):
        row = self.report["actual_old_slots"]
        A, U, V = [audit.matrix(row["effective_plus_A_U_V"][k]) for k in ("A", "U", "V")]
        variables = sp.symbols("a0:16")
        X = sp.Matrix(4, 4, variables)
        equations = list(X*A-A*X)+list(X*U-U*X)+list(X*V-V*X)
        matrix, rhs = sp.linear_eq_to_matrix(equations, variables)
        self.assertEqual(matrix.rank(), 15)
        self.assertEqual(matrix.nullspace(), [sp.eye(4).reshape(16, 1)])
        self.assertEqual(len(set(zip(U.diagonal(), V.diagonal()))), 4)

    def test_quaternionic_irrep_equivalence_and_even_hyper_divisibility(self):
        row = self.report["actual_old_slots"]
        irrep = row["irreducible_plus_orbit"]
        A, U, V = [audit.matrix(row["effective_plus_A_U_V"][k]) for k in ("A", "U", "V")]
        T = audit.matrix(irrep["quaternionic_intertwiner_T"])
        for Z in (audit.carrier.ZETA*A, U, V):
            self.assertEqual(audit.clean(T*sp.conjugate(Z)-Z*T), sp.zeros(4))
        self.assertEqual(T*sp.conjugate(T), -sp.eye(4))
        self.assertEqual(2*144//4, 72)
        self.assertNotEqual((2*19) % 4, 0)
        self.assertTrue(irrep["any_equivariant_q0_removal_has_even_hyper_count"])

    def test_full_neutral_plus_minus_pair_is_two_identical_irreps(self):
        row = self.report["actual_old_slots"]
        B = audit.matrix(row["irreducible_plus_orbit"]["full_pair_complex_intertwiner"])
        self.assertEqual(audit.clean(B.adjoint()*B), sp.eye(8))
        for key in ("A", "U", "V"):
            plus = audit.matrix(row["effective_plus_A_U_V"][key])
            if key == "A":
                plus = audit.carrier.ZETA*plus
            whole = audit.matrix(row["underlying_flavor"][key])
            self.assertEqual(audit.clean(B*whole*B.inv()-sp.diag(plus, plus)), sp.zeros(8))
        self.assertTrue(row["irreducible_plus_orbit"]["full_eight_component_pair_is_two_identical_four_irreps"])

    def test_all_actual_sixteen_removals_independently_enumerated(self):
        independent = []
        for n0, n2, n4, n6 in product(range(17), range(4), range(17), range(12)):
            n8 = 16-n0-n2-n4-n6
            if n8 >= 0:
                independent.append((n0, n2, n4, n6, n8))
        self.assertEqual(set(independent), set(audit.all_removals(16)))
        self.assertEqual(len(independent), 2956)
        survivors = []
        for row in independent:
            M2 = sum(n*r*r for n, r in zip(row, range(5)))
            M4 = sum(n*r**4 for n, r in zip(row, range(5)))
            A, B = 24-M2, 72-M4
            if 108*B == 3456*A+A*A:
                survivors.append(row)
        self.assertEqual(survivors, [])

    def test_first_two_GS_equations_force_stated_unique_c_shift(self):
        A, B = sp.symbols("A B")
        a, b, c = audit.frozen_bulk_data(self.parents["v91_route"])
        cp = c+sp.Matrix([-2*A/9, -A/9])
        self.assertEqual(sp.expand((a.T*audit.G*cp)[0]+(7440+4*A)/6), 0)
        self.assertEqual(sp.expand((b.T*audit.G*cp)[0]), 176)
        residual = sp.expand((cp.T*audit.G*cp)[0]-(419136+16*B)/3)
        self.assertEqual(sp.expand(residual+sp.Rational(4, 81)*(108*B-3456*A-A*A)), 0)

    def test_analytic_divisibility_reduction_is_exact(self):
        for A in range(-232, 25):
            if (A*A) % 108 == 0:
                self.assertEqual(A % 18, 0)
                k = A//18
                B = 576*k+3*k*k
                if (B-A) % 12 == 0:
                    self.assertEqual(A % 36, 0)
        for r in range(5):
            self.assertEqual((r**4-r*r) % 12, 0)
            self.assertLessEqual(r**4, 16*r*r)

    def test_every_remaining_negative_A_violates_moment_bound(self):
        rows = self.report["minimal_sixteen_replacement_obstruction"]["negative_A_cases"]
        self.assertEqual([r["A"] for r in rows], [-36, -72, -108, -144, -180, -216])
        for row in rows:
            A = row["A"]
            B = 32*A+sp.Rational(A*A, 108)
            required_M2, required_M4 = 24-A, 72-B
            self.assertGreater(required_M4-16*required_M2, 0)
            self.assertEqual(required_M4-16*required_M2, row["required_fourth_moment_excess_over_16_times_second"])

    def test_A_zero_forces_unavailable_eight_q2_hypers(self):
        moments = [(n0, n1, n2, n3, n4) for n1, n2, n3, n4 in product(range(17), repeat=4)
                   if (n0 := 16-n1-n2-n3-n4) >= 0
                   and n1+4*n2+9*n3+16*n4 == 24 and n1+16*n2+81*n3+256*n4 == 72]
        self.assertEqual(moments, [(4, 8, 4, 0, 0)])
        self.assertGreater(moments[0][1], audit.OLD_COUNTS[1])

    def test_actual_neutral_replacement_quartic_mismatch(self):
        row = self.report["minimal_sixteen_replacement_obstruction"]["actual_neutral_four_orbit_example"]
        self.assertEqual(row["resulting_counts"], [132, 11, 23, 11, 90])
        self.assertEqual(row["c_prime"], ["-1432/3", "-452/3"])
        self.assertEqual(sp.sympify(row["c_prime_squared"])-sp.sympify(row["required_D4_prime_over3"]), sp.Rational(33664, 9))
        self.assertEqual(row["quartic_mismatch"], "33664/9")
        self.assertFalse(row["c_prime_integral"])

    def test_regular_characters_leave_nonidentity_profile_unchanged(self):
        for coefficient in (1, -2, 1):
            for extra in range(3):
                A = abs(coefficient)+extra
                counts = [A, A-coefficient, A+coefficient, A]
                for j in (1, 2, 3):
                    char = sum(n*sp.I**(m*j) for m, n in enumerate(counts))
                    self.assertEqual(sp.simplify(char+coefficient*(sp.I**j-sp.I**(2*j))), 0)

    def test_twenty_and_twenty_four_scans_have_complete_bounded_counts(self):
        rows = self.report["bounded_regular_character_extensions"]["records"]
        self.assertEqual(len(rows), 9)
        self.assertEqual([r["actual_removal_vectors_checked"] for r in rows], [5355]*3+[8455]*6)
        for row in rows:
            self.assertEqual(sum(row["candidate_counts_q0_q2_q4_q6_q8"]), row["total_new_and_removed_hypers"])
            self.assertEqual(sum(row["regular_extra_t0_t1_t2"]), (row["total_new_and_removed_hypers"]-16)//4)

    def test_unique_rational_twenty_four_scout_recomputed(self):
        found = []
        for extra in (1, 2):
            for t0 in range(extra+1):
                for t1 in range(extra-t0+1):
                    t2 = extra-t0-t1
                    for removed in audit.all_removals(16+4*extra):
                        M2, M4 = audit.removal_moments(removed)
                        A, B = 24+4*t1+16*t2-M2, 72+4*t1+64*t2-M4
                        if 108*B == 3456*A+A*A:
                            found.append((extra, (t0, t1, t2), removed, A, B))
        self.assertEqual(found, [(2, (0, 1, 1), (19, 0, 0, 0, 5), -36, -1140)])

    def test_rational_scout_still_fails_quotient_source_and_projectors(self):
        row = next(g for r in self.report["bounded_regular_character_extensions"]["records"] for g in r["rational_candidates"])
        cp = sp.Matrix([sp.Rational(z) for z in row["c_prime"]])
        self.assertEqual(list(cp), [-464, -144])
        self.assertEqual(list((cp+4*sp.Matrix([2, -1]))/8), [-57, -sp.Rational(37, 2)])
        self.assertFalse(row["ordinary_quotient_source_integral"])
        self.assertFalse(row["q0_removal_count_even"])
        a, b, c = audit.frozen_bulk_data(self.parents["v91_route"])
        self.assertEqual(-6*(a.T*audit.G*cp)[0], 7440+4*(-36))
        self.assertEqual(3*(cp.T*audit.G*cp)[0], 419136+16*(-1140))

    def test_removed_old_flavor_polynomial_is_not_fictional_trivial_hypers(self):
        row = self.report["full_independent_flavor_replacement"]
        eta = [sp.Symbol(z) for z in row["old_removed_multiplicity_U4_roots"]]
        actual = sp.sympify(row["old_removed_I8"])
        self.assertEqual(sp.expand(actual-4*sum(audit.I8(z) for z in eta)), 0)
        self.assertNotEqual(sp.expand(actual-16*audit.I8(sp.Integer(0))), 0)
        self.assertEqual(sp.expand(actual.subs({z: 0 for z in eta})-16*audit.I8(sp.Integer(0))), 0)

    def test_full_positive_new_multiplicities_SMW_normalization(self):
        row = self.report["full_independent_flavor_replacement"]
        self.assertEqual(sum(b["multiplicity"] for b in row["new_independent_flavor_blocks"]), 16)
        for block in row["new_independent_flavor_blocks"]:
            self.assertGreater(block["multiplicity"], 0)
            roots = [sp.sympify(z) for z in block["roots"]]
            self.assertEqual(sp.expand(sp.sympify(block["I8"])-sum(audit.I8(z) for z in roots)), 0)
        full = sp.sympify(row["full_replacement_delta_I8"])
        self.assertEqual(full.coeff(audit.P2), 0)
        self.assertEqual(full.coeff(audit.P1, 2), 0)

    def test_replacement_counterprofile_retains_W_and_normal_flavor_curvatures(self):
        row = self.report["full_independent_flavor_replacement"]
        P = audit.d**2*(audit.d+audit.w)
        self.assertEqual([sp.expand(sp.sympify(z)-value) for z, value in zip(row["new_local_counterprofile_on_common_flavor_backgrounds"], [-P/4, -P/4, P/2])], [0, 0, 0])
        actual = sp.sympify(row["with_normal_compensator_curvatures_retained"])
        expected = sp.sympify(row["common_flavor_zero_delta_I8"]).subs(audit.w, audit.u+audit.v)
        self.assertEqual(sp.expand(actual-expected), 0)
        self.assertTrue(actual.has(audit.v))

    def test_full_independent_flavor_index_matches_new_zero_modes(self):
        row = self.report["full_independent_flavor_replacement"]
        localized = sum(2*sp.sympify(b["C4_I6"])+2*sp.sympify(b["C2_cover_I6"]) for b in row["new_independent_flavor_blocks"])
        index = sp.expand(localized.subs(audit.x, 0))
        self.assertEqual(sp.expand(index-sp.sympify(row["independent_4D_zero_mode_I6"])), 0)
        self.assertNotEqual(index, 0)
        self.assertEqual(row["old_constant_modes_removed"], 0)
        self.assertEqual(row["new_constant_modes_added"], 8)
        self.assertEqual(row["conditional_total_old_plus_new_N1_chiral_modes"], 19)
        self.assertFalse(row["V97_Dirac_gap_reused"])
        self.assertFalse(row["masses_or_interactions_constructed"])

    def test_SU4_primitive_anomaly_polynomial_independently_from_roots(self):
        z, y0, y1, y2, c2, c3, c4 = sp.symbols("z y0 y1 y2 c2 c3 c4")
        roots = [y0, y1, y2, -y0-y1-y2]
        chern = {c2: sum(a*b for a, b in combinations(roots, 2)),
                 c3: sum(a*b*c for a, b, c in combinations(roots, 3)), c4: sp.prod(roots)}
        row = self.report["flavor_GS_and_full_representation_scope"]["independent_new_SU4_test"]
        polynomial = sp.sympify(row["SU4_fundamental_I8"])
        self.assertEqual(sp.expand(polynomial.subs(chern)-sum(audit.I8(z+r) for r in roots)), 0)
        self.assertEqual(polynomial.coeff(c4), -sp.Rational(1, 6))
        self.assertEqual(polynomial.coeff(c3).coeff(z), sp.Rational(1, 2))
        self.assertFalse(row["ordinary_tensor_GS_products_can_cancel_c4_or_z_c3"])

    def test_diagonal_old_new_flavor_identification_does_not_fix_primitives(self):
        row = self.report["flavor_GS_and_full_representation_scope"]["diagonal_old_new_SU4_test"]
        z, c2, c3, c4 = sp.symbols("z c2 c3 c4")
        delta = sp.sympify(row["replacement_delta_I8"])
        self.assertEqual(delta.coeff(c4), sp.Rational(1, 2))
        self.assertEqual(delta.coeff(c3).coeff(z), sp.Rational(1, 2))
        self.assertFalse(row["this_flavor_identification_removes_primitive_anomaly_change"])

    def test_ordinary_degree_four_GS_products_have_no_SU4_primitive_terms(self):
        z, c2, c3, c4 = sp.symbols("z c2 c3 c4")
        basis = [audit.P1, z*z, c2]
        for left, right in product(basis, repeat=2):
            self.assertEqual(sp.expand(left*right).coeff(c4), 0)
            self.assertEqual(sp.expand(left*right).coeff(c3), 0)

    def test_full_flavor_projector_fails_to_commute_but_reduced_selection_allowed(self):
        row = self.report["flavor_GS_and_full_representation_scope"]["full_old_Sp267_compatibility"]
        gen, pi = audit.matrix(row["small_symplectic_generator"]), audit.matrix(row["selection_projector"])
        self.assertEqual(pi*pi, pi)
        self.assertNotEqual(gen*pi, pi*gen)
        self.assertFalse(row["proper_sixteen_hyper_subrepresentation_of_unchanged_fundamental_exists"])
        self.assertFalse(row["full_flavor_is_unbroken_by_original_gauging_and_twists"])
        self.assertTrue(row["smaller_commuting_subgroup_replacement_constructed_at_representation_level"])
        self.assertFalse(row["global_QK_SUSY_action_away_from_origin_constructed"])

    def test_global_flavor_tHooft_anomaly_is_not_a_universal_inconsistency_claim(self):
        scope = self.report["flavor_GS_and_full_representation_scope"]["global_flavor_vs_gauge_scope"]
        self.assertIn("not by itself a quantum inconsistency", scope)
        self.assertIn("No claim that the old QK/composite connection", scope)
        self.assertFalse(self.report["terminal_decision"]["all_spectator_carriers_or_V98_response_only_option_excluded"])

    def test_no_gate_parent_or_full_theory_promoted(self):
        row = self.report["terminal_decision"]
        self.assertEqual(row["closed_gates"], [])
        self.assertFalse(row["microscopic_parent_accepted"])
        self.assertFalse(row["theory_complete"])
        self.assertFalse(row["same_action_SUSY_spectrum_or_quantized_GS_completion_constructed"])
        self.assertFalse(row["full_old_Sp267_flavor_embedding_constructed"])

    def test_rehashed_polynomial_or_scope_mutations_rejected(self):
        cases = [(["terminal_decision", "theory_complete"], True),
                 (["minimal_sixteen_replacement_obstruction", "rationally_factorizing_removals"], [{"forged": True}]),
                 (["bounded_regular_character_extensions", "surviving_frozen_category_candidates"], 1),
                 (["full_independent_flavor_replacement", "old_removed_I8"], "0"),
                 (["full_independent_flavor_replacement", "V97_Dirac_gap_reused"], True)]
        for path, value in cases:
            changed = copy.deepcopy(self.report)
            target = changed
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            changed["core_sha256"] = audit.canonical_sha(changed)
            with self.assertRaises(RuntimeError):
                audit.validate_certificate(changed)

    def test_cached_math_returns_fresh_mutable_copies(self):
        changed = audit.build_certificate()
        changed["actual_old_slots"]["selected_six_dimensional_hypers"] = 0
        self.assertEqual(audit.build_certificate()["actual_old_slots"]["selected_six_dimensional_hypers"], 16)

    def test_invalid_removal_size_rejected(self):
        for number in (-1, 268, 1.5, True, False):
            with self.assertRaises(ValueError):
                audit.all_removals(number)


if __name__ == "__main__":
    unittest.main()
