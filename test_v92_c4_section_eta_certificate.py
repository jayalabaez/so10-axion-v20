import unittest
from fractions import Fraction as F

import sympy as sp

import v92_c4_section_eta_certificate as target


class TestV92C4SectionEtaCertificate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = target.build_certificate()

    def test_pinned_scout_and_field_census(self):
        row = self.result["input_scout"]
        self.assertEqual(row["singlet_counts_q0_q2_q4_q6_q8"], [144, 3, 19, 11, 90])
        census = self.result["representation_census"]
        self.assertEqual(census["adjoint55_section_multiplicities"], [37, 9, 0, 9])
        self.assertEqual(census["section_C4"]["hyper"], [236, 4, 30, 30])
        self.assertEqual(census["section_C4"]["vector"], [38, 9, 0, 9])
        self.assertEqual(census["section_C4"]["hyper_minus_vector"], [198, -5, 30, 21])
        self.assertEqual(census["central_C8"]["hyper"], [234, 0, 3, 0, 30, 0, 33, 0])
        for key in ("section_C4", "central_C8"):
            self.assertEqual(sum(census[key]["hyper"]), 300)
            self.assertEqual(sum(census[key]["vector"]), 56)

    def test_independent_cyclotomic_root_sum(self):
        # Exact Q[x]/Phi_n arithmetic, independently of the MM polynomial.
        x = sp.Symbol("x")
        for n in (4, 8):
            phi = sp.Poly(sp.cyclotomic_poly(n, x), x, domain=sp.QQ)
            for r in range(n):
                result = sp.Poly(0, x, domain=sp.QQ)
                for k in range(1, n):
                    inv = sp.invert(sp.Poly((1-x**k)**4, x, domain=sp.QQ), phi)
                    power = sp.Poly(x**(k*(r+2)), x, domain=sp.QQ)
                    result += (power*inv).rem(phi)
                result = result.rem(phi)
                self.assertEqual(result.degree(), 0)
                expected = target.complex_dirac_xi(n, r)
                self.assertEqual(result.nth(0)/n, sp.Rational(expected.numerator, expected.denominator))

    def test_exact_section_spin_lifts(self):
        rows = self.result["lens_fermion_tests"][:2]
        self.assertEqual(rows[0]["reduced_complex_Dirac_xi_by_charge"], ["0", "-5/32", "-1/4", "-5/32"])
        self.assertEqual(rows[1]["reduced_complex_Dirac_xi_by_charge"], ["0", "3/32", "1/4", "3/32"])
        self.assertEqual([r["MM_bare_fermion_phase_exponent"] for r in rows], ["10", "-9"])
        self.assertEqual([r["bare_fermion_ratio"] for r in rows], ["+1", "+1"])

    def test_exact_central_spin_lifts_and_no_bare_rejection(self):
        rows = self.result["lens_fermion_tests"][2:]
        self.assertEqual([r["MM_bare_fermion_phase_exponent"] for r in rows], ["153/2", "-135/2"])
        self.assertEqual([r["bare_fermion_ratio"] for r in rows], ["-1", "-1"])
        self.assertTrue(all(not r["bare_fermion_ratio_is_total_anomaly"] for r in rows))

    def test_charge_conjugation_and_periodicity(self):
        for n in (4, 8):
            for spin in (0, n//2):
                for r in range(n):
                    value = target.reduced_dirac_xi(n, r, spin)
                    self.assertEqual(value, target.reduced_dirac_xi(n, -r, spin))
                    self.assertEqual(value, target.reduced_dirac_xi(n, r+3*n, spin))

    def test_tangent_half_p1_not_naive_modular_division(self):
        self.assertEqual(self.result["tangent_characteristic"]["p1_mod_n"], {"4": 0, "8": 4})
        for n in (4, 8):
            self.assertEqual([target.tangent_lambda(n, s) for s in (0, n//2)], [2, 2])

    def test_u_null_axes_and_polarization(self):
        for n in (4, 8):
            for x in range(n):
                self.assertEqual(target.u_wcs_relative_action(n, [x, 0], gravity=(0, 0)), 0)
                self.assertEqual(target.u_wcs_relative_action(n, [0, x], gravity=(0, 0)), 0)
                for y in range(n):
                    self.assertEqual(target.u_wcs_relative_action(n, [x, y], gravity=(0, 0)), F(x*y, n) % 1)

    def test_eight_torsion_labels_pass_lens_screen(self):
        row = self.result["torsion_refinement_lens_screen"]
        self.assertEqual(row["labels_passing_this_screen"], 8)
        self.assertEqual(row["passing_tau_mod4"], [[0, 0], [0, 2], [1, 2], [2, 0], [2, 1], [2, 2], [2, 3], [3, 2]])
        self.assertTrue(row["V91_selected_label"]["passes_both_lens_spin_lifts_in_both_embeddings"])
        self.assertFalse(row["passing_labels_are_anomaly_free_theories"])

    def test_all_sixteen_central_bare_signs_cancel_in_model(self):
        rows = self.result["torsion_refinement_lens_screen"]["rows"]
        self.assertEqual(len(rows), 16)
        self.assertTrue(all(r["central_WCS_action_difference_mod1"] == "1/2" for r in rows))
        self.assertTrue(all(r["central_combined_exponent_mod1"] == "0" for r in rows))

    def test_opposite_linking_orientation_same_pass_filter(self):
        plus, minus = target.refinement_tests(linking_sign=1), target.refinement_tests(linking_sign=-1)
        self.assertEqual([r["passes_both_lens_spin_lifts_in_both_embeddings"] for r in plus],
                         [r["passes_both_lens_spin_lifts_in_both_embeddings"] for r in minus])

    def test_refinement_representatives_mod4_do_not_change_action(self):
        for n, gauge in ((4, [0, 2]), (8, [4, 6])):
            value = target.u_wcs_relative_action(n, gauge)
            self.assertEqual(value, target.u_wcs_relative_action(n, [gauge[0]+n, gauge[1]-n]))

    def test_fail_closed_scope(self):
        scope = self.result["bordism_scope"]
        for key, value in scope.items():
            if key not in ("ordinary_OmegaSpin7_BC4_from_literature", "generator_dictionary_note"):
                self.assertFalse(value, key)
        self.assertFalse(self.result["WCS_derivation"]["absolute_eta_to_linking_orientation_dictionary_fixed"])

    def test_bad_inputs_rejected(self):
        with self.assertRaises(ValueError):
            target.representation_census([1, 2], [6, 4, 6])
        with self.assertRaises(ValueError):
            target.representation_census([144, 3, 19, 11, 90], [1, 4, 6])
        with self.assertRaises(ValueError):
            target.reduced_dirac_xi(4, 1, 1)
        with self.assertRaises(ValueError):
            target.complex_dirac_xi(3, 1)


if __name__ == "__main__":
    unittest.main()
