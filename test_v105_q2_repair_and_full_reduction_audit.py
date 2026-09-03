"""Independent source-polynomial checks that the frozen V104 tests omitted."""
import copy
import json
import unittest
from unittest.mock import patch

import sympy as sp
import v105_q2_repair_and_full_reduction_audit as audit


class TestV105Q2Repair(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()
        cls.inputs = audit.load_inputs()
        cls.quartic = cls.inputs["v103_route"]["original_quartic_sections"]
        cls.reduced = cls.report["corrected_reduction"]

    def independent_remainders(self, tv, pv, parameters=None, prime=None):
        g = audit.geometry
        values = dict(g.SPECIAL_VALUES if parameters is None else zip(audit.PARAMETERS, parameters))
        values.update({audit.t: tv, audit.p: pv})
        r0 = g.parse(self.quartic["pivot_boundary_data"]["L_zero_r_reconstruction"])
        F = g.parse(self.quartic["pivot_boundary_data"]["L_zero_first_equation_F"]).subs(values)
        a2 = sp.Poly(F, audit.q).nth(2)
        if prime:
            self.assertNotEqual(int(a2) % prime, 0)
        remainders = {}
        for source, result in zip(self.quartic["exact_quartic_reduction"]["remaining_equations_T5_through_T0"][1:], self.reduced["rows"]):
            original = sp.expand(g.parse(source["numerator"]).subs(audit.r, r0)).subs(values)
            if prime:
                remainder = sp.reduced(original, [F], audit.q, audit.h, modulus=prime)[1]
            else:
                domain = sp.QQ.poly_ring(audit.h)
                remainder = sp.Poly(original, audit.q, domain=domain).rem(sp.Poly(F, audit.q, domain=domain)).as_expr()
            expected = tv**result["removed_t_power"]*(g.parse(result["ell"])*audit.q+g.parse(result["mu"])).subs(values)
            difference = sp.expand(a2**result["A2_power"]*remainder-expected)
            self.assertTrue(sp.Poly(difference, audit.q, audit.h, modulus=prime).is_zero if prime else difference == 0)
            remainders[source["T_degree"]] = sp.expand(a2**result["A2_power"]*remainder/tv**result["removed_t_power"])
        return F, remainders, values

    def test_canonical(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))

    def test_bound_parents_and_member(self):
        self.assertEqual(self.report["input_core_hashes"], {k: v[1] for k, v in audit.PARENTS.items()})
        self.assertEqual(self.report["bound_reduced_equations_sha256"], self.quartic["quartic_reduced_equations_sha256"])

    def test_exact_old_converter_basis_counterexamples(self):
        rows = self.report["source_conversion_forensics"]
        self.assertEqual([r["historical_image"] for r in rows], ["t", "p", "q", "1", "h", "alpha", "beta", "gamma", "delta"])
        self.assertEqual([r["correct_image"] for r in rows], list(map(str, audit.VARIABLES)))

    def test_all_basis_powers_and_mixed_monomials_round_trip(self):
        for symbol in audit.VARIABLES:
            self.assertEqual(audit.to_ring(symbol**3+2*symbol).as_expr(), symbol**3+2*symbol)
        example = sp.prod(symbol**(i+1) for i, symbol in enumerate(audit.VARIABLES))+audit.h/3-audit.geometry.epsilon/7
        self.assertEqual(sp.expand(audit.to_ring(example).as_expr()-example), 0)

    def test_old_converter_destroys_h_minus_one(self):
        old = audit.historical_converter()
        self.assertEqual(old(audit.h-1), audit.RING.zero)
        self.assertNotEqual(audit.to_ring(audit.h-1), audit.RING.zero)
        self.assertNotEqual(old(audit.geometry.alpha), audit.to_ring(audit.geometry.alpha))

    def test_all_five_original_residuals_were_corrupted(self):
        self.assertEqual([r["historical_conversion_matches_source"] for r in self.reduced["rows"]], [False]*5)

    def test_pseudo_division_abstract_identity(self):
        F = audit.rq**2+audit.rt*audit.rq+audit.rh
        P = audit.rq**5+audit.rp*audit.rq**2+audit.rh**3
        Q, remainder, steps = audit.pseudo_reduce(P, F)
        self.assertEqual(steps, 4)
        self.assertEqual(P, Q*F+remainder)
        independent = sp.rem(P.as_expr(), F.as_expr(), audit.q)
        self.assertEqual(sp.expand(remainder.as_expr()-independent), 0)

    def test_nonmonic_abstract_identity(self):
        F = 3*audit.rt*audit.rq**2+audit.rp*audit.rq+audit.rh
        P = audit.rq**4-audit.rt*audit.rq+audit.rh
        Q, remainder, steps = audit.pseudo_reduce(P, F)
        self.assertEqual((3*audit.rt)**steps*P, Q*F+remainder)

    def test_constant_and_linear_dividends(self):
        F = audit.rq**2+audit.rt
        for P in (audit.RING.zero, audit.rt, audit.rq+audit.rh):
            Q, rem, steps = audit.pseudo_reduce(P, F)
            self.assertEqual((Q, rem, steps), (audit.RING.zero, P, 0))

    def test_genuine_quadratic_required(self):
        for F in (audit.RING.zero, audit.rq+audit.rh, audit.rq**3+audit.rq**2):
            with self.assertRaises(ValueError):
                audit.pseudo_reduce(audit.rq**4, F)

    def test_original_equations_direct_rational_division(self):
        self.independent_remainders(2, 1)
        self.independent_remainders(3, 2)

    def test_universal_parameter_assignment_direct_modular_division(self):
        self.independent_remainders(2, 3, [7, 11, 13, 17, 19], 103)

    def test_actual_original_X_two_payload_direct_division(self):
        values = [int(audit.geometry.COEFFICIENTS[z].subs(audit.geometry.X, 2)) for z in audit.PARAMETERS]
        self.independent_remainders(5, 4, values, 101)

    def test_all_five_division_powers_and_q_degrees(self):
        rows = self.reduced["rows"]
        self.assertEqual([r["T_degree"] for r in rows], [4, 3, 2, 1, 0])
        self.assertEqual([r["source_q_degree"] for r in rows], [3, 3, 4, 4, 5])
        self.assertEqual([r["A2_power"] for r in rows], [2, 2, 3, 3, 4])
        self.assertEqual([r["removed_t_power"] for r in rows], [12, 12, 18, 18, 24])
        self.assertTrue(all(r["division_identity_verified"] for r in rows))

    def test_correct_h_degrees_retained(self):
        self.assertEqual([(r["ell_h_degree"], r["mu_h_degree"]) for r in self.reduced["rows"]], [(1, 2), (1, 2), (2, 2), (2, 2), (2, 3)])

    def test_full_fifteen_conditions_defined(self):
        rows = self.report["all_five_residual_elimination"]["necessary_core_rows"]
        expected = ["R"+str(i) for i in range(4, -1, -1)]+["C"+str(i)+str(j) for i in range(4, -1, -1) for j in range(i-1, -1, -1)]
        self.assertEqual([r["id"] for r in rows], expected)
        self.assertTrue(all(r["definition"] for r in rows))
        self.assertEqual(sum(r["expanded"] for r in rows), 2)

    def test_corrected_leading_core_content_and_degrees(self):
        rows = {r["id"]: r for r in self.report["all_five_residual_elimination"]["necessary_core_rows"]}
        self.assertEqual(rows["R4"]["removed_t_M_powers"], [6, 2])
        self.assertEqual(rows["C43"]["removed_t_M_powers"], [3, 2])
        self.assertEqual((rows["R4"]["h_degree"], rows["C43"]["h_degree"]), (4, 3))
        self.assertEqual((rows["R4"]["term_count"], rows["C43"]["term_count"]), (1815, 930))

    def test_corrected_fixed_degree_witnesses(self):
        rows = self.report["all_five_residual_elimination"]["fixed_modular_witnesses"]
        self.assertEqual([r["fixed_Sylvester_determinant_mod101"] for r in rows], [81, 14, 16])
        self.assertEqual([r["M_mod101"] for r in rows], [64, 58, 80])
        self.assertTrue(all(r["h_degrees"] == [4, 3] for r in rows))
        compatibility = self.report["independent_V105_correction_compatibility"]
        self.assertEqual(compatibility["independent_raw_resultants_mod101"], [65, 52, 20])
        self.assertTrue(compatibility["four_N4_N3_linear_coefficients_identical_as_universal_expressions"])
        self.assertTrue(compatibility["all_three_scaling_residues_verified"])
        self.assertFalse(compatibility["independent_correction_retracted_or_overwritten"])

    def test_leading_witnesses_from_independent_source_division(self):
        # No sparse converter, saved ell/mu, or expanded core is used to derive
        # these two polynomials; start again from V103 source residuals.
        for row in self.report["all_five_residual_elimination"]["fixed_modular_witnesses"]:
            F, pairs, values = self.independent_remainders(row["t"], row["p"])
            A2, A1, A0 = (sp.Poly(F, audit.q).nth(k) for k in (2, 1, 0))
            e4, m4 = (sp.Poly(pairs[4], audit.q).nth(k) for k in (1, 0))
            e3, m3 = (sp.Poly(pairs[3], audit.q).nth(k) for k in (1, 0))
            M = audit.geometry.parse(self.reduced["M"]).subs(values)
            core4 = sp.expand((A2*m4**2-A1*e4*m4+A0*e4**2)/(row["t"]**6*M**2))
            core43 = sp.expand((e4*m3-e3*m4)/(row["t"]**3*M**2))
            P4, P43 = (sp.Poly(core, audit.h, modulus=101) for core in (core4, core43))
            self.assertEqual(P4, sp.Poly(audit.geometry.parse(row["R4_slice"]), audit.h, modulus=101))
            self.assertEqual(P43, sp.Poly(audit.geometry.parse(row["C43_slice"]), audit.h, modulus=101))
            self.assertEqual(int(sp.resultant(P4, P43, modulus=101)) % 101, row["fixed_Sylvester_determinant_mod101"])

    def test_sylvester_singular_and_nonsingular(self):
        variable = audit.h
        A = sp.Poly(variable**2+1, variable, modulus=101)
        B = sp.Poly(variable+1, variable, modulus=101)
        self.assertEqual(audit.sylvester_mod(A, B), 2)
        self.assertEqual(audit.sylvester_mod(A, A), 0)
        with self.assertRaises(ValueError):
            audit.sylvester_mod(A, sp.Poly(1, variable, modulus=101))

    def test_common_root_symbolic_identities(self):
        self.assertEqual(self.report["common_root_reconstruction_theorem"]["checked_abstract_identity_residuals"], ["0"]*3)

    def test_five_disjoint_regular_charts_and_exceptional_boundary(self):
        row = self.report["common_root_reconstruction_theorem"]
        self.assertEqual([r["pivot_index"] for r in row["disjoint_regular_charts"]], [4, 3, 2, 1, 0])
        self.assertEqual(row["disjoint_regular_charts"][-1]["earlier_ell_indices_required_zero"], [4, 3, 2, 1])
        self.assertTrue(all(r["remaining_equation_count"] == 5 for r in row["disjoint_regular_charts"]))
        self.assertFalse(row["zero_slope_and_repeated_roots_discarded"])

    def test_norms_alone_do_not_force_a_common_root(self):
        # q-1 and q+1 each meet q^2-1 but never at the same q.
        a2, a1, a0 = 1, 0, -1
        pairs = [(1, -1), (1, 1)]
        self.assertEqual([a2*m*m-a1*e*m+a0*e*e for e, m in pairs], [0, 0])
        self.assertEqual(pairs[0][0]*pairs[1][1]-pairs[1][0]*pairs[0][1], 2)

    def test_cross_conditions_alone_do_not_impose_the_quadratic(self):
        self.assertEqual(1*0-2*0, 0)
        self.assertEqual(1*0**2+1*1**2, 1)  # q=0 is not a root of q^2+1.

    def test_regular_rational_root_and_automatic_square(self):
        X = audit.geometry.X
        root = X
        a2, a1, a0 = 1, -(X+1), X
        pairs = [(0, 0), (0, 0), (1, -X), (X, -X**2), (2, -2*X)]
        self.assertEqual([sp.expand(e*root+m) for e, m in pairs], [0]*5)
        self.assertEqual(sp.expand(a2*root**2+a1*root+a0), 0)
        self.assertEqual(sp.expand(a1*a1-4*a2*a0-(X-1)**2), 0)

    def test_zero_slope_chart_still_needs_original_field_square(self):
        X = audit.geometry.X
        self.assertFalse(sp.sqrt(X).is_rational_function(X))
        self.assertFalse(self.report["common_root_reconstruction_theorem"]["all_fifteen_conditions_alone_sufficient_over_C_X_on_zero_slope_chart"])
        self.assertTrue(self.report["common_root_reconstruction_theorem"]["all_fifteen_conditions_sufficient_over_algebraic_closure"])

    def test_repeated_root_not_discarded(self):
        a2, a1, a0 = 1, -4, 4
        self.assertEqual(a1*a1-4*a2*a0, 0)
        self.assertEqual(a2*2**2+a1*2+a0, 0)
        self.assertIn("including zero", self.report["common_root_reconstruction_theorem"]["zero_slope_chart"])

    def test_old_evidence_retracted_not_relabelled(self):
        row = self.report["retraction_and_replacement"]
        self.assertFalse(row["V104_derived_cores_and_28_97_91_witnesses_accepted_as_original_Q2_evidence"])
        self.assertTrue(row["V104_leading_A2_identity_and_h_independent_discriminant_retained"])
        self.assertTrue(row["Q2_confinement_reestablished_by_new_valid_proof"])
        self.assertFalse(row["frozen_V104_files_changed"])

    def test_no_point_rank_or_gate_promotions(self):
        self.assertEqual(self.report["preserved_frontier"], self.quartic["preserved_frontier"])
        decision = self.report["terminal_decision"]
        self.assertTrue(decision["bounded_F105_repair_and_full_Q2_reduction_completed"])
        for key in ("Q2_solved", "Q2_excluded", "actual_nonzero_original_section_constructed", "original_exact_MW_rank_computed", "covariant_action_repair_constructed", "same_action_microscopic_parent_accepted", "theory_complete"):
            self.assertFalse(decision[key])
        self.assertEqual(decision["closed_gates"], [])

    def test_mutating_returned_certificate_does_not_mutate_cache(self):
        other = audit.build_certificate()
        other["corrected_reduction"]["rows"][0]["ell"] = "0"
        self.assertEqual(audit.build_certificate(), self.report)

    def test_warm_cache_rechecks_parent(self):
        with patch.object(audit.common, "load_bound", side_effect=RuntimeError("changed parent")):
            with self.assertRaises(RuntimeError):
                audit.build_certificate()

    def test_warm_cache_rechecks_source(self):
        with patch.object(audit, "file_sha", return_value="0"*64):
            with self.assertRaises(RuntimeError):
                audit.build_certificate()

    def test_warm_cache_rechecks_parameter_dictionary_and_slice(self):
        changed = dict(audit.geometry.COEFFICIENTS)
        changed[audit.geometry.alpha] += 1
        with patch.object(audit.geometry, "COEFFICIENTS", changed):
            with self.assertRaises(RuntimeError):
                audit.build_certificate()
        changed = dict(audit.geometry.SPECIAL_VALUES)
        changed[audit.geometry.alpha] = 99
        with patch.object(audit.geometry, "SPECIAL_VALUES", changed):
            with self.assertRaises(RuntimeError):
                audit.build_certificate()

    def test_resealed_promotion_rejected(self):
        bad = copy.deepcopy(self.report)
        bad["terminal_decision"]["Q2_excluded"] = True
        bad["core_sha256"] = audit.canonical_sha(bad)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(bad)

    def test_sources_and_primary_scope(self):
        rows = self.report["primary_sources"]
        self.assertEqual(len(rows), len({r["url"] for r in rows}))
        self.assertTrue(all(r["url"].startswith("https://") for r in rows))


if __name__ == "__main__":
    unittest.main()
