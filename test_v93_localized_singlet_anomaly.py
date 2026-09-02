import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import sympy as sp

import v93_localized_singlet_anomaly as audit


class TestV93LocalizedSingletAnomaly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parents = audit.load_parents()
        cls.report = audit.build_certificate()

    def test_all_canonical_parents_and_helper_are_bound(self):
        expected = {key: core for key, (_, core) in audit.PARENTS.items()}
        expected["v92_singlet_projector_helper"] = audit.PROJECTOR_CORE
        self.assertEqual(self.report["input_core_hashes"], expected)
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        self.assertEqual(self.parents["v92_master"]["input_core_hashes"]["v92_route"], expected["v92_route"])

    def test_changed_or_rehashed_parent_is_rejected(self):
        original = Path.read_text
        def changed(path, *args, **kwargs):
            text = original(path, *args, **kwargs)
            if path.name == audit.PARENTS["v92_route"][0]:
                value = json.loads(text)
                value["smooth_singlet_projectors"]["eleven_mode_normal_aligned_witness"]["constant_chiral_charge_moments"]["TrQ"] = 0
                value["core_sha256"] = audit.canonical_sha(value)
                return json.dumps(value)
            return text
        with patch.object(Path, "read_text", changed):
            with self.assertRaises(RuntimeError):
                audit.load_parents()

    def test_changed_frozen_projector_source_is_rejected(self):
        original = Path.read_bytes
        def changed(path, *args, **kwargs):
            value = original(path, *args, **kwargs)
            return value+b"\n" if path.name == "v92_singlet_projector_certificate.py" else value
        with patch.object(Path, "read_bytes", changed):
            with self.assertRaises(RuntimeError):
                audit.load_parents()

    def test_frozen_source_pins_are_portable_across_CRLF_checkout(self):
        original = Path.read_bytes
        def crlf(path, *args, **kwargs):
            return original(path, *args, **kwargs).replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        with patch.object(Path, "read_bytes", crlf):
            self.assertEqual(audit.load_parents()["v92_route"]["core_sha256"], audit.PARENTS["v92_route"][1])

    def test_inverse_series_matches_independent_hyperbolic_derivatives(self):
        x = sp.Symbol("x")
        for order in (2, 4):
            for j in range(1, order):
                kernel = 1/(2*sp.sinh((x+2*sp.pi*sp.I*j/order)/2))
                exact = tuple(sp.simplify(sp.diff(kernel, x, n).subs(x, 0)/sp.factorial(n)) for n in range(4))
                self.assertEqual(audit.normal_kernel_series(order, j), exact)

    def test_derived_C4_series_equals_V71(self):
        expected = [["3/8", "1/8", "-7/64", "-11/192"],
                    ["1/8", "-1/8", "-5/64", "11/192"],
                    ["-1/8", "-1/8", "5/64", "11/192"],
                    ["-3/8", "1/8", "7/64", "-11/192"]]
        self.assertEqual(self.report["derived_kernel_series_by_phase"]["C4"], expected)
        self.assertTrue(self.report["derived_kernel_series_by_phase"]["C4_series_reproduces_frozen_V71"])

    def test_C2_cover_series_not_twice_normalized(self):
        self.assertEqual(self.report["derived_kernel_series_by_phase"]["C2_per_cover_point"],
                         [["1/8", "0", "-1/64", "0"], ["-1/8", "0", "1/64", "0"]])
        for phase in range(2):
            coefficients = audit.phase_polynomial(2, 2, phase)
            self.assertEqual(coefficients["x3"], 0)
            self.assertEqual(coefficients["x_p1T4"], 0)
            self.assertEqual(coefficients["x_f2"], 0)
            self.assertNotEqual(coefficients["f3"], 0)
            self.assertNotEqual(coefficients["x2_f"], 0)

    def test_conjugate_SMW_half_reconstruction_all_phases(self):
        for order in (2, 4):
            for phase in range(order):
                partner = 3-phase if order == 4 else 1-phase
                own, other = audit.phase_series(order, phase), audit.phase_series(order, partner)
                for n in range(4):
                    self.assertEqual(other[n], (-1)**(n+1)*own[n])
                for q in (0, 2, 4, 6, 8):
                    self.assertEqual(audit.phase_polynomial(q, order, phase),
                                     audit.phase_polynomial(-q, order, partner))
                    for name, (n, r, factor) in audit.TERMS.items():
                        pair = factor*(own[n]*q**r+other[n]*(-q)**r)/(2*sp.factorial(r))
                        self.assertEqual(sp.simplify(pair), audit.phase_polynomial(q, order, phase)[name])

    def test_matrix_trace_SMW_factor_is_not_double_counted(self):
        h = sp.diag(audit.ZETA, sp.conjugate(audit.ZETA))
        q = sp.diag(2, -2)
        coefficients, _ = audit.shifted_character_polynomial(h, q, 4)
        self.assertEqual(coefficients["f3"], sp.Rational(1, 2))
        self.assertEqual(coefficients["x3"], -sp.Rational(11, 192))
        self.assertEqual(coefficients, audit.phase_polynomial(2, 4, 0))

    def test_full_267_direct_sum_is_used(self):
        blocks = self.report["block_certificates"]
        self.assertEqual(sum(row["copies"]*row["certificate"]["hyper_count"] for row in blocks), 267)
        self.assertEqual(sum(row["copies"] for row in blocks if row["certificate"]["kind"] == "four_orbit"), 64)
        counts = {q: 0 for q in (0, 2, 4, 6, 8)}
        for row in blocks:
            counts[row["certificate"]["q_magnitude"]] += row["copies"]*row["certificate"]["hyper_count"]
        self.assertEqual(counts, {0: 144, 2: 3, 4: 19, 6: 11, 8: 90})

    def test_all_actual_half_angle_matrices_and_charge_checks(self):
        for source in self.report["block_certificates"]:
            for row in source["certificate"]["strata"].values():
                self.assertTrue(all(row["checks"].values()))
                h = audit.matrix(row["half_angle_matrix"])
                q = sp.diag(*row["full_symplectic_charge_diagonal"])
                self.assertTrue(audit.zero(h**row["order"]+sp.eye(h.rows)))
                self.assertTrue(audit.zero(h*q-q*h))
                self.assertEqual(row["SMW_factor"], "1/2")
                self.assertEqual(row["orbifold_average"], "1/4")
                self.assertEqual(row["normal_weight"], 1)

    def test_all_polynomial_coefficients_are_real_exact_rationals(self):
        for source in self.report["block_certificates"]:
            for row in source["certificate"]["strata"].values():
                self.assertEqual(set(row["coefficients"]), set(audit.MONOMIALS))
                for value in row["coefficients"].values():
                    self.assertTrue(sp.sympify(value).is_Rational)

    def test_equal_charge_four_orbit_characters_cancel_locally(self):
        for source in self.report["block_certificates"]:
            block = source["certificate"]
            if block["kind"] == "four_orbit":
                self.assertTrue(block["all_six_coefficients_vanish_at_all_strata"])
                self.assertEqual(block["strata"]["z00"]["plus_eigenphase_multiplicities"], [1, 1, 1, 1])
                self.assertEqual(block["strata"]["z11"]["plus_eigenphase_multiplicities"], [1, 1, 1, 1])
                self.assertEqual(block["strata"]["z10"]["plus_eigenphase_multiplicities"], [2, 2])
                self.assertEqual(block["strata"]["z01"]["plus_eigenphase_multiplicities"], [2, 2])

    def test_continuous_q8_is_not_discrete_residue_zero(self):
        q8 = audit.phase_polynomial(8, 4, 0)
        q0 = audit.phase_polynomial(0, 4, 0)
        self.assertEqual(q8["f3"], 32)
        self.assertEqual(q8["x_f2"], 4)
        self.assertEqual(q0["f3"], 0)
        self.assertEqual(q0["x_f2"], 0)
        self.assertEqual(q8["x3"], q0["x3"])
        self.assertFalse(self.report["scope_boundaries"]["charges_reduced_mod8"])

    def test_selected_exact_C4_coefficients(self):
        expected = {"f3": "54", "f_p1T4": "-9/16", "x_f2": "37/2",
                    "x2_f": "-63/16", "x3": "-121/192", "x_p1T4": "-11/192"}
        for point in ("z00", "z11"):
            self.assertEqual(self.report["coefficients_by_stratum"][point], expected)

    def test_selected_exact_C2_cover_coefficients(self):
        expected = {"f3": "18", "f_p1T4": "-3/16", "x_f2": "0",
                    "x2_f": "-9/16", "x3": "0", "x_p1T4": "0"}
        for point in ("z10", "z01"):
            self.assertEqual(self.report["coefficients_by_stratum"][point], expected)

    def test_physical_C2_orbit_is_sum_of_two_cover_points(self):
        row = self.report["coefficients_by_physical_orbit"]["z10_z01_C2"]
        self.assertEqual(row, {"f3": "36", "f_p1T4": "-3/8", "x_f2": "0",
                               "x2_f": "-9/8", "x3": "0", "x_p1T4": "0"})
        for name in audit.MONOMIALS:
            self.assertEqual(sp.Rational(row[name]), sum(sp.Rational(self.report["coefficients_by_stratum"][p][name]) for p in ("z10", "z01")))

    def test_integrated_zero_mode_linear_and_cubic_anomaly(self):
        row = self.report["zero_mode_cross_check"]
        self.assertEqual(row["signed_continuous_charges"], [-8, 2, 2, 2, 4, 4, 4, 6, 6, 6, 8])
        self.assertEqual((row["independent_chiral_count"], row["TrQ"], row["TrQ3"]), (11, 36, 864))
        self.assertEqual(row["sum_cover_point_f3"], "144")
        self.assertEqual(row["sum_cover_point_f_p1T4"], "-3/2")
        self.assertTrue(row["zero_mode_index_matches"])
        self.assertFalse(row["normal_terms_are_identified_with_ordinary_zero_mode_trace"])
        self.assertFalse(row["massive_local_ansatz_erases_anomaly"])

    def test_index_normalization_all_line_phases_and_translation_signs(self):
        for m in range(4):
            for eta in (-1, 1):
                at11 = (m+(2 if eta == -1 else 0)) % 4
                at2 = (m+(1 if eta == -1 else 0)) % 2
                index = audit.phase_series(4, m)[0]+audit.phase_series(4, at11)[0]+2*audit.phase_series(2, at2)[0]
                expected = int(m == 0 and eta == 1)-int(m == 3 and eta == 1)
                self.assertEqual(index, expected)

    def test_local_invariant_spectrum_is_not_the_anomaly(self):
        for row in self.report["local_projector_trace_counterexample"].values():
            self.assertEqual(row["local_invariant_TrQ"], 36)
            self.assertEqual(row["local_invariant_TrQ3"], 864)
            self.assertEqual(row["naive_f3"], "144")
            self.assertFalse(row["naive_local_spectrum_equals_localized_anomaly"])

    def test_invalid_noncommuting_curvature_is_rejected(self):
        with self.assertRaises(ValueError):
            audit.shifted_character_polynomial(sp.diag(audit.ZETA, sp.conjugate(audit.ZETA)), sp.Matrix([[0, 1], [1, 0]]), 4)
        with self.assertRaises(ValueError):
            audit.normal_kernel_series(4, 0)
        with self.assertRaises(ValueError):
            audit.normal_kernel_series(3, 1)

    def test_no_unearned_anomaly_or_gate_promotion(self):
        row = self.report["terminal_decision"]
        self.assertFalse(row["singlet_sector_alone_anomaly_free"])
        self.assertFalse(row["full_theory_ruled_out_by_singlet_sector_alone"])
        self.assertFalse(row["full_fixed_wall_anomaly_cancelled"])
        self.assertFalse(row["full_relative_or_global_anomaly_trivialized"])
        self.assertEqual(row["accepted_extensions"], 0)
        self.assertEqual(row["closed_gates"], [])
        self.assertFalse(self.report["scope_boundaries"]["full_fixed_wall_Gammahat_representations_supplied"])
        self.assertFalse(self.report["scope_boundaries"]["GS_or_WCS_inflow_included"])

    def test_rehashed_numerical_or_scope_mutation_rejected(self):
        candidate = copy.deepcopy(self.report)
        candidate["coefficients_by_stratum"]["z00"]["x_f2"] = "0"
        candidate["terminal_decision"]["full_fixed_wall_anomaly_cancelled"] = True
        candidate["core_sha256"] = audit.canonical_sha(candidate)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(candidate)

    def test_JSON_serializable(self):
        self.assertEqual(json.loads(json.dumps(self.report)), self.report)


if __name__ == "__main__":
    unittest.main()
