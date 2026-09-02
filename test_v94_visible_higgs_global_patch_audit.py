import copy
import unittest

import sympy as sp
import v94_visible_higgs_global_patch_audit as audit


class TestV94VisiblePatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()

    def test_parents_and_core(self):
        self.assertEqual(self.report["input_core_hashes"], {k: v[1] for k,v in audit.PARENTS.items()})
        self.assertEqual(self.report["core_sha256"], audit.common.canonical_sha(self.report))

    def test_independent_moments(self):
        self.assertEqual(self.report["census"]["moments"]["full"], {"TrQ": -68, "TrQ3": 1408})
        self.assertEqual(self.report["census"]["moments"]["light"], {"TrQ": -104, "TrQ3": 544})
        self.assertTrue(self.report["census"]["independent_Cartan_crosscheck"])

    def test_threshold_identity(self):
        row = self.report["census"]["pure_I6_by_sector"]
        self.assertEqual(sp.expand(sp.sympify(row["full"])-sp.sympify(row["light"])-sp.sympify(row["heavy"])), 0)

    def test_exact_cancellation_variation(self):
        row = self.report["local_descent"]
        exponent = sp.sympify(row["new_formal_canceller"])
        variation = sp.expand(exponent.subs(audit.phi, audit.phi-8*audit.epsilon)-exponent)
        self.assertEqual(sp.expand(variation+audit.epsilon*sp.sympify(row["B4"])), 0)

    def test_matching_is_not_cancelling(self):
        row = self.report["local_descent"]
        self.assertTrue(row["heavy_matching_has_opposite_sign_to_canceller"])
        self.assertFalse(row["adding_matching_erases_full_anomaly"])

    def test_combined_threshold_counterterm(self):
        row = self.report["local_descent"]
        combined = sp.sympify(row["canceller_plus_heavy_matching_below_threshold"])
        self.assertEqual(sp.expand(combined-sp.sympify(row["new_formal_canceller"])-sp.sympify(row["existing_heavy_matching_term"])), 0)
        pure = sp.expand(combined.subs(dict.fromkeys(audit.E, 0)))
        light = sp.sympify(self.report["census"]["pure_I6_by_sector"]["light"])
        self.assertEqual(sp.expand(pure-audit.phi*light/(8*audit.f)), 0)

    def test_S2xS2_periods(self):
        rows = {r["sector"]: r for r in self.report["ordinary_period_screen"]["periods"]}
        self.assertEqual([rows[k]["S2xS2_f_square_2_period"] for k in ("light","heavy","full")], ["68/3","36","176/3"])
        self.assertEqual([rows[k]["period_mod_one"] for k in ("light","heavy","full")], ["2/3","0","2/3"])

    def test_obstruction_not_a_Higgs_no_go(self):
        row = self.report["ordinary_period_screen"]
        self.assertTrue(row["naive_full_independent_periodic_scalar_extension_rejected"])
        self.assertFalse(row["all_global_Higgs_WZ_completions_excluded"])
        self.assertFalse(row["period_triple_is_the_actual_Phi_phase"])

    def test_free_line_needs_zero_class(self):
        self.assertTrue(audit.higgs_line_trivialized(0))
        self.assertFalse(audit.higgs_line_trivialized(1))
        self.assertFalse(audit.higgs_line_trivialized(-1))

    def test_torsion_line_may_have_nonzero_Phi(self):
        self.assertTrue(audit.higgs_line_trivialized(1, 8))
        self.assertFalse(audit.higgs_line_trivialized(1, 16))
        self.assertTrue(audit.higgs_line_trivialized(2, 16))

    def test_bad_torsion_order(self):
        with self.assertRaises(ValueError):
            audit.higgs_line_trivialized(0, 0)

    def test_test_flux_requires_zeros(self):
        row = self.report["defect_free_domain"]
        self.assertFalse(row["test_background_admits_everywhere_nonzero_Phi"])
        self.assertEqual(row["test_obstruction_class_in_H2_S2xS2"], [-8,-8])

    def test_pure_C8_full_heavy_light(self):
        rows = self.report["pure_C8_restrictions"]["sectors"]
        self.assertTrue(all(r["passes_this_restriction"] for r in rows.values()))
        self.assertFalse(self.report["pure_C8_restrictions"]["pure_finite_pass_implies_continuous_or_global_anomaly_cancellation"])

    def test_charge_residue_invariance(self):
        for q in range(-20,21):
            signed = audit.finite_screen({"TrQ": q, "TrQ3": q**3})
            residue = audit.finite_screen({"TrQ": q%8, "TrQ3": (q%8)**3})
            self.assertEqual(signed["linear_residue"], residue["linear_residue"])
            self.assertEqual(signed["cubic_residue"], residue["cubic_residue"])

    def test_nonabelian_levels_from_tensor(self):
        route = audit.load_parents()["v93_route"]
        tensor = route["bare_bulk_local_anomaly"]["calculation"]["conditional_visible_gauge_slice"]["visible_tensor"]
        self.assertEqual([-tensor[0]//8,-tensor[1]//8], [4,3])

    def test_scope_not_promoted(self):
        self.assertTrue(all(v is False for v in self.report["boundary"].values()))

    def test_mutated_arithmetic_rejected_even_rehashed(self):
        changed = copy.deepcopy(self.report)
        changed["ordinary_period_screen"]["full_period_shift_phase"] = "1"
        changed["core_sha256"] = audit.common.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(changed)

    def test_false_completion_rejected_even_rehashed(self):
        changed = copy.deepcopy(self.report)
        changed["boundary"]["full_quantized_relative_action_constructed"] = True
        changed["core_sha256"] = audit.common.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(changed)


if __name__ == "__main__":
    unittest.main()
