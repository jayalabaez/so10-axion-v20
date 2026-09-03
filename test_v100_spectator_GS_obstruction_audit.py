import copy
from itertools import product
import unittest
from unittest.mock import patch

import sympy as sp

import v100_spectator_GS_obstruction_audit as audit


class TestV100SpectatorGS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()
        cls.parents = audit.load_inputs()

    def test_canonical_parents_and_fresh_validation(self):
        self.assertEqual(self.report["input_core_hashes"], {k: v[1] for k, v in audit.PARENTS.items()})
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        audit.validate_certificate(self.report)
        self.assertEqual(self.report["bound_spectator_core"], audit.SPECTATOR_CORE)

    def test_frozen_source_and_test_changes_rejected(self):
        original = audit.file_sha
        for name in ("v99_spectator_replacement_anomaly_audit.py", "test_v99_spectator_replacement_anomaly_audit.py",
                     "susy_v99_multipath_g1_frontier_master_audit.py"):
            with patch.object(audit, "file_sha", side_effect=lambda p: "0"*64 if p.name == name else original(p)):
                with self.assertRaises(RuntimeError):
                    audit.load_inputs()

    def test_actual_projector_source_chain_rebound(self):
        original = audit.previous.file_sha
        with patch.object(audit.previous, "file_sha", side_effect=lambda p: "0"*64 if p.name == "v92_singlet_projector_certificate.py" else original(p)):
            with self.assertRaises(RuntimeError):
                audit.load_inputs()

    def test_frozen_bulk_sign_normalization(self):
        self.assertEqual(audit.dot(audit.A_VEC, audit.A_VEC), 8)
        self.assertEqual(audit.dot(audit.B_VEC, audit.B_VEC), -4)
        self.assertEqual(audit.dot(audit.A_VEC, audit.OLD_C), -1240)
        self.assertEqual(3*audit.dot(audit.OLD_C, audit.OLD_C), 419136)
        self.assertEqual(audit.dot(audit.B_VEC, audit.OLD_C), 176)

    def test_correct_charge_one_W_coefficient_is_solved_not_assumed(self):
        N, x, y = sp.symbols("N x y")
        solution = sp.solve([2*x+2*y+N/6, -x+2*y], (x, y))
        self.assertEqual(solution, {x: -N/18, y: -N/36})
        row = self.report["independent_W_GS_obstruction"]
        self.assertEqual([sp.sympify(z, locals={"N": N}) for z in row["correct_cWW"]], [solution[x], solution[y]])
        self.assertEqual(sp.factor(3*audit.dot([solution[x], solution[y]], [solution[x], solution[y]])-N), N*(N-108)/108)

    def test_factor_two_N27_error_cannot_return(self):
        N = sp.Symbol("N")
        self.assertEqual(audit.dot(audit.A_VEC, [-N/9, -N/18]), -N/3)
        self.assertNotEqual(audit.dot(audit.A_VEC, [-N/9, -N/18]), -N/6)
        self.assertEqual(audit.dot(audit.A_VEC, [-6, -3]), -18)
        self.assertEqual(3*audit.dot([-6, -3], [-6, -3]), 108)
        row = self.report["independent_W_GS_obstruction"]
        self.assertEqual(row["pure_W_allowed_N"], [0, 108])
        self.assertFalse(row["pure_W_equations_alone_exclude_all_regular_extensions"])

    def test_full_SMW_common_I8_includes_all_mixed_powers(self):
        f, w, P1, P2 = sp.symbols("f w P1 P2")
        N, L1, L2, L3, A, B = sp.symbols("N L1 L2 L3 A B")
        I8 = lambda z: z**4/24-P1*z*z/48+(7*P1**2-4*P2)/5760
        t, removed = (0, 2, 4), (28, 0, 2, 0, 10)
        new = audit.regular_counts(t)
        l1, l2, l3, l4 = audit.moments(new, (0, 2, 4))
        M2, M4 = audit.moments(removed, range(5), (2, 4))
        direct = sp.expand(sum(n*I8(q*f+w) for n, q in zip(new, (0, 2, 4)))
                           -sum(n*I8(q*f) for n, q in zip(removed, audit.Q)))
        symbolic = sp.sympify(self.report["independent_W_GS_obstruction"]["full_common_Q_W_replacement_delta_I8"], locals={"N": N})
        actual = symbolic.subs({N: sum(new), L1: l1, L2: l2, L3: l3, A: sp.Rational(l2, 4)-M2, B: sp.Rational(l4, 16)-M4})
        self.assertEqual(sp.expand(direct-actual), 0)
        self.assertEqual(direct.coeff(P2), 0)
        self.assertEqual(direct.coeff(P1, 2), 0)
        for monomial in (f**3*w, f*f*w*w, f*w**3, w**4, P1*f*w, P1*w*w):
            self.assertNotEqual(sp.Poly(direct, f, w, P1).coeff_monomial(monomial), 0)

    def test_pure_W_restriction_and_SMW_half_count_once(self):
        N, f, w, P1 = sp.symbols("N f w P1")
        row = self.report["independent_W_GS_obstruction"]
        self.assertEqual(sp.expand(sp.sympify(row["full_common_Q_W_replacement_delta_I8"], locals={"N": N}).subs(f, 0)), N*w**4/24-N*P1*w*w/48)
        self.assertEqual(sp.expand(sp.sympify(row["pure_W_new_minus_W_neutral_old_I8"], locals={"N": N})), N*w**4/24-N*P1*w*w/48)
        z = sp.Symbol("z")
        self.assertEqual(sp.expand((audit.previous.I8(z)+audit.previous.I8(-z))/2-audit.previous.I8(z)), 0)

    def test_complete_mixed_abelian_equations_have_correct_multiplicities(self):
        L1, N, A = sp.symbols("L1 N A")
        s, h = [-N/18, -N/36], [-L1/18, -L1/36]
        cp = audit.OLD_C+sp.Matrix([-2*A/9, -A/9])
        self.assertEqual(sp.factor(3*audit.dot(h, s)-L1), L1*(N-108)/108)
        self.assertEqual(sp.expand(audit.dot(cp, [-6, -3])), 2304+4*A/3)
        self.assertEqual(2*audit.dot(h, h), L1**2/162)
        row = self.report["independent_W_GS_obstruction"]
        self.assertEqual(len(row["complete_Q_W_quartic_system"]), 5)
        self.assertIn("3*cQQ.cQW=L3", row["complete_Q_W_quartic_system"])
        self.assertIn("3*cQW.cWW=L1", row["complete_Q_W_quartic_system"])

    def test_Cauchy_and_charge_bound_give_exact_C_interval(self):
        l1, l2 = sp.symbols("L1 L2")
        C = l2-l1*l1/162
        self.assertEqual(sp.expand(C.subs(l2, l1*l1/108)), l1*l1/324)
        self.assertEqual(sp.expand(C.subs(l2, 4*l1)), sp.expand(648-(l1-324)**2/162))
        for q in range(5):
            self.assertLessEqual(q*q, 4*q)
        self.assertEqual([sp.Rational(3, 4)*(c-2304) for c in (0, 648)], [-1728, -1242])

    def test_old_budget_contradiction_is_analytic_not_just_scan(self):
        A, s = sp.symbols("A s")
        B = 32*A+A*A/108
        self.assertEqual(sp.expand(B-(-27648+(A+1728)**2/108)), 0)
        self.assertEqual(sp.diff(B, A).subs(A, -1728+s), s/54)
        self.assertEqual(B.subs(A, -1242), -25461)
        self.assertEqual(sum(n*r**4 for n, r in zip(audit.OLD_COUNTS, range(5))), 24238)
        self.assertGreater(25461, 24238)
        self.assertEqual(self.report["independent_W_GS_obstruction"]["strict_budget_gap"], 1223)

    def test_all_300_N108_regular_cases_independently_checked(self):
        rows = []
        for t in product(range(24), repeat=3):
            if sum(t) != 23:
                continue
            counts = tuple(4*n+base for n, base in zip(t, (4, 8, 4)))
            self.assertEqual(sum(counts), 108)
            l1, l2, l4 = audit.moments(counts, (0, 2, 4), (1, 2, 4))
            C = sp.Rational(l2)-sp.Rational(l1*l1, 162)
            A = 3*(C-2304)/4
            required = sp.Rational(l4, 16)-32*A-A*A/108
            self.assertGreater(required, 24238)
            rows.append((required, t))
        self.assertEqual(len(rows), 300)
        self.assertEqual(min(rows), (sp.Rational(527687816, 19683), (8, 0, 15)))
        report = self.report["independent_W_GS_obstruction"]
        self.assertEqual(sp.Rational(report["N108_exact_minimum_required_old_r4"]["required_removed_r4"]), min(rows)[0])

    def test_regular_C4_positive_counts_retain_nonidentity_target(self):
        for t in ((0, 0, 0), (0, 2, 4), (8, 0, 15)):
            for coefficient, extra in zip((1, -2, 1), t):
                A = abs(coefficient)+extra
                counts = (A, A-coefficient, A+coefficient, A)
                self.assertTrue(all(n >= 0 for n in counts))
                for j in (1, 2, 3):
                    self.assertEqual(sp.simplify(sum(n*sp.I**(m*j) for m, n in enumerate(counts))+coefficient*(sp.I**j-sp.I**(2*j))), 0)
            self.assertEqual(sum(audit.regular_counts(t)), 16+4*sum(t))

    def test_quotient_integrality_requires_A_multiple72(self):
        A, k = sp.symbols("A k")
        cp = audit.OLD_C+sp.Matrix([-2*A/9, -A/9])
        self.assertEqual(list((cp+4*audit.B_VEC)/8), [-58-A/36, -19-A/72])
        self.assertEqual(sp.expand((32*A+A*A/108).subs(A, 72*k)), 48*k*k+2304*k)
        for number in range(-1600, 1020):
            half = ((-58-sp.Rational(number, 36)), (-19-sp.Rational(number, 72)))
            self.assertEqual(all(z.q == 1 for z in half), number % 72 == 0)

    def test_elimination_t1_t2_formulas_from_moments(self):
        A, B, n2, n4, n6, n8 = sp.symbols("A B n2 n4 n6 n8")
        M2, M4 = n2+4*n4+9*n6+16*n8, n2+16*n4+81*n6+256*n8
        t2 = (B-A-48+12*n4+72*n6+240*n8)/48
        t1 = (A-24+M2-16*t2)/4
        self.assertEqual(sp.expand(24+4*t1+16*t2-M2-A), 0)
        self.assertEqual(sp.expand(72+4*t1+64*t2-M4-B), 0)

    def test_complete_finite_search_bounds_and_seed_count(self):
        row = self.report["gauge_only_regular_replacement_search"]
        self.assertEqual(sum(audit.OLD_COUNTS), 267)
        self.assertEqual(4*(267//4), 264)
        self.assertEqual(24+16*(264//4-4), 1016)
        self.assertEqual(audit.moments(audit.OLD_COUNTS, range(5), (2,))[0], 1618)
        self.assertEqual((sp.ceiling(sp.Rational(24-1618, 72)), sp.floor(sp.Rational(1016, 72))), (-22, 14))
        seeds = audit.gauge_only_seeds()
        self.assertEqual(len(seeds), 672)
        self.assertEqual(audit.canonical_sha(seeds), row["all_seeds_sha256"])

    def test_every_seed_and_its_maximal_neutral_descendant_satisfies_equations(self):
        for seed in audit.gauge_only_seeds():
            for j in (0, min((144-seed["removed"][0])//4, (264-seed["N"])//4)):
                removed, t = seed["removed"][:], seed["t"][:]
                removed[0] += 4*j
                t[0] += j
                new = audit.regular_counts(t)
                self.assertEqual(sum(new), sum(removed))
                self.assertTrue(all(0 <= x <= cap for x, cap in zip(removed, audit.OLD_COUNTS)))
                self.assertEqual(removed[0] % 2, 0)
                old2, old4 = audit.moments(removed, range(5), (2, 4))
                new2, new4 = audit.moments(new, (0, 1, 2), (2, 4))
                A, B = new2-old2, new4-old4
                self.assertEqual(A, 72*seed["k"])
                self.assertEqual(108*B-3456*A-A*A, 0)

    def test_minimum40_by_independent_direct_search_through40(self):
        found = []
        for N in range(16, 41, 4):
            extra = N//4-4
            for removed in audit.previous.all_removals(N):
                if removed[0] % 2:
                    continue
                M2, M4 = audit.previous.removal_moments(removed)
                for t0 in range(extra+1):
                    for t1 in range(extra-t0+1):
                        t2 = extra-t0-t1
                        A = 24+4*t1+16*t2-M2
                        if A % 72:
                            continue
                        B = 72+4*t1+64*t2-M4
                        if 108*B == 3456*A+A*A:
                            found.append((N, (t0, t1, t2), removed, A, B))
        self.assertEqual(found, [(40, (0, 2, 4), (28, 0, 2, 0, 10), -72, -2256)])

    def test_minimum_scout_actual_GS_moments_and_half_source(self):
        row = self.report["gauge_only_regular_replacement_search"]["minimum_scout"]
        self.assertEqual(row["resulting_counts"], [120, 19, 37, 11, 80])
        cp = sp.Matrix([sp.Rational(z) for z in row["c_prime"]])
        self.assertEqual(list(cp), [-456, -140])
        self.assertEqual(list((cp+4*audit.B_VEC)/8), [-56, -18])
        self.assertEqual(row["total_D2"], 7152)
        self.assertEqual(row["total_D4"], 383040)
        self.assertEqual(-6*audit.dot(audit.A_VEC, cp), row["total_D2"])
        self.assertEqual(3*audit.dot(cp, cp), row["total_D4"])
        self.assertEqual(audit.dot(audit.B_VEC, cp), 176)

    def test_minimum40_still_fails_pure_W_not_complete(self):
        row = self.report["gauge_only_regular_replacement_search"]["minimum_scout"]
        cWW = [-sp.Rational(40, 18), -sp.Rational(40, 36)]
        self.assertEqual(3*audit.dot(cWW, cWW)-40, -sp.Rational(680, 27))
        self.assertEqual(sp.Rational(row["independent_W_pure_quartic_residual"]), -sp.Rational(680, 27))
        self.assertFalse(row["is_accepted_new_sector"])

    def test_actual_neutral_quaternionic_irrep_and_full_pair_even_rule(self):
        saved = self.parents["actual_old_projectors"]["eleven_mode_normal_aligned_witness"]
        block = next(r["certificate"] for r in saved["direct_sum_blocks"] if r["certificate"]["q_magnitude"] == 0)
        A, U, V = [audit.previous.matrix(block["effective_plus"][key]) for key in ("A", "U", "V")]
        row = self.report["minimum_scout_actual_projector_cost"]["actual_neutral_even_removal_proof"]
        T = audit.previous.matrix(row["quaternionic_intertwiner_T"])
        R = audit.previous.carrier.ZETA*A
        self.assertEqual(T*sp.conjugate(T), -sp.eye(4))
        S = sp.diag(sp.eye(4), T)
        for key, Z in (("A", R), ("U", U), ("V", V)):
            self.assertEqual(audit.previous.clean(T*sp.conjugate(Z)-Z*T), sp.zeros(4))
            self.assertEqual(audit.previous.clean(S*audit.previous.matrix(block["underlying_flavor"][key])*S.inv()-sp.diag(Z, Z)), sp.zeros(8))
        variables = sp.symbols("z0:16")
        M = sp.Matrix(4, 4, variables)
        equations = list(M*A-A*M)+list(M*U-U*M)+list(M*V-V*M)
        matrix, _ = sp.linear_eq_to_matrix(equations, variables)
        self.assertEqual(matrix.rank(), 15)
        self.assertEqual(288//4, 72)
        for number in range(145):
            self.assertEqual((2*number) % 4 == 0, number % 2 == 0)

    def test_charged_orbits_irreducible_and_no_line_intertwiner(self):
        rows = self.report["minimum_scout_actual_projector_cost"]["charged_blocks"]
        for row in rows.values():
            A, U, V = [audit.previous.matrix(row["orbit_A_U_V"][key]) for key in ("A", "U", "V")]
            self.assertEqual(len(set(zip(U.diagonal(), V.diagonal()))), 4)
            self.assertEqual((U-sp.eye(4)).col_join(V-sp.eye(4)).rank(), 4)
            cycle = row["A_cycle_of_joint_eigenlines"]
            self.assertEqual(set(cycle[:-1]), set(range(4)))
            self.assertEqual(cycle[0], cycle[-1])
            for before, after in zip(cycle, cycle[1:]):
                self.assertNotEqual(A[after, before], 0)

    def test_continuous_charge_prevents_false_half_orbit_removal(self):
        x = sp.symbols("x0:16")
        M = sp.Matrix(4, 4, x)
        for q in (4, 8):
            # A map between +q and-q cannot commute with continuous charge.
            self.assertEqual(q*M-M*(-q*sp.eye(4)), 2*q*M)
            self.assertNotEqual(q, -q)
        row = self.report["minimum_scout_actual_projector_cost"]
        self.assertTrue(row["continuous_Q_is_retained_not_only_Q_mod8"])

    def test_scout_forces_both_Phi_and_two_q4_lines_out(self):
        row = self.report["minimum_scout_actual_projector_cost"]
        for q, total, cap in ((4, 2, 3), (8, 10, 2)):
            possibilities = [lines for lines in range(cap+1) if total >= lines and (total-lines) % 4 == 0]
            self.assertEqual(possibilities, [2])
            self.assertEqual(row["charged_blocks"][str(q)]["forced_singletons_removed"], 2)
        self.assertEqual(row["actual_removed_free_charges"], [4, 4, 8, -8])
        self.assertTrue(row["both_old_Phi_plus_minus8_unavoidably_removed"])
        self.assertFalse(row["old_Phi_driven_mass_module_preserved"])

    def test_twenty_new_modes_and_seven_remaining_old_are_not_hidden(self):
        row = self.report["minimum_scout_actual_projector_cost"]
        table = row["new_free_Q_W_table"]
        self.assertEqual(sum(r["multiplicity"] for r in table), 20)
        self.assertEqual(row["remaining_old_free_charges"], [2, 2, 2, 4, 6, 6, 6])
        self.assertEqual(row["conditional_total_free_chiral_count"], 27)
        self.assertEqual(row["remaining_common_Q_TrQ_TrQ3"], [28, 736])
        for power in (1, 3):
            self.assertEqual(sum(r["multiplicity"]*r["Q"]**power for r in table), 0)
            self.assertEqual(sum(r["multiplicity"]*r["W"]**power for r in table), 0)

    def test_removed_shifted_normal_polynomials_crosscheck_zero_modes(self):
        row = self.report["minimum_scout_actual_projector_cost"]
        d, x, p = audit.previous.d, audit.previous.x, audit.previous.p
        c4, c2 = [sp.sympify(row["removed_old_full_normal_I6"][key]) for key in ("C4_each", "C2_each_cover")]
        self.assertEqual(c4, d**3+5*d*d*x/2-d*p/16-7*d*x*x/16-p*x/48-11*x**3/48)
        self.assertEqual(c2, d**3/3-d*p/48-d*x*x/16)
        self.assertEqual(sp.expand((2*c4+2*c2).subs(x, 0)-2*audit.previous.I6(2*d)), 0)
        self.assertNotEqual(c4.subs(d, 0), 0)
        self.assertFalse(row["removal_leaves_original_localized_anomaly_profile_unchanged"])

    def test_global_tHooft_and_full_Gamma_scope_is_fail_closed(self):
        w = self.report["independent_W_GS_obstruction"]
        t = self.report["terminal_decision"]
        self.assertFalse(w["global_W_tHooft_anomaly_alone_is_quantum_inconsistency"])
        self.assertIn("not by itself a quantum inconsistency", w["genuinely_global_W_scope"])
        self.assertFalse(t["new_dynamical_W_vector_installed"])
        self.assertFalse(t["full_old_Sp267_embedding_constructed"])
        self.assertFalse(t["all_spectator_or_response_only_alternatives_excluded"])
        self.assertFalse(t["microscopic_parent_accepted"])
        self.assertFalse(t["theory_complete"])
        self.assertEqual(t["closed_gates"], [])

    def test_resealed_physics_or_scope_changes_rejected(self):
        cases = [("independent_W_GS_obstruction", "pure_W_allowed_N", [0, 27]),
                 ("independent_W_GS_obstruction", "global_W_tHooft_anomaly_alone_is_quantum_inconsistency", True),
                 ("gauge_only_regular_replacement_search", "minimum_N", 24),
                 ("minimum_scout_actual_projector_cost", "old_Phi_driven_mass_module_preserved", True),
                 ("terminal_decision", "theory_complete", True)]
        for section, key, value in cases:
            changed = copy.deepcopy(self.report)
            changed[section][key] = value
            changed["core_sha256"] = audit.canonical_sha(changed)
            with self.assertRaises(RuntimeError):
                audit.validate_certificate(changed)

    def test_cached_math_returns_independent_objects(self):
        changed = audit.build_certificate()
        changed["gauge_only_regular_replacement_search"]["minimum_N"] = 0
        self.assertEqual(audit.build_certificate()["gauge_only_regular_replacement_search"]["minimum_N"], 40)

    def test_invalid_regular_multiplicities_rejected(self):
        for bad in ((0, 0), (0, 0, -1), (0, 1.5, 0), (True, 0, 0), (0, 0, False)):
            with self.assertRaises(ValueError):
                audit.regular_counts(bad)


if __name__ == "__main__":
    unittest.main()
