"""Independent cocharacter, response-level and scope tests for F101."""
import copy
import itertools
import unittest
from unittest.mock import patch

import sympy as sp
import v101_intermediate_cover_quantization_audit as audit


class IntermediateCoverQuantizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()
        cls.rows = {row["id"]: row for row in cls.report["classification"]}

    def test_canonical(self):
        self.assertEqual(self.report["core_sha256"], audit.common.canonical_sha(self.report))

    def test_reconstruction(self):
        audit.validate_certificate(self.report)

    def test_exhaustive_intermediate_subgroups(self):
        old = tuple(audit.kernels()["old"])
        zero = (0,)*7
        found = set()
        for mask in range(1 << len(old)):
            subset = frozenset(old[i] for i in range(len(old)) if mask >> i & 1)
            if zero not in subset or audit.covers.D not in subset:
                continue
            if all(tuple((a+b) % 2 for a, b in zip(u, v)) in subset for u in subset for v in subset):
                found.add(subset)
        self.assertEqual(found, {frozenset(k) for k in audit.kernels().values()})
        self.assertEqual(len(found), 5)

    def test_degrees_not_stack_counts(self):
        self.assertEqual([r["cover_degree_over_old"] for r in self.rows.values()], [1, 2, 2, 2, 4])
        self.assertEqual([r["minimum_positive_integer_stack"] for r in self.rows.values()], [8, 2, 4, 8, 1])

    def test_genuine_character_descent_independent(self):
        sigma = (1, 1, 0, 0, 0, 0, 0)
        root = (0, 0, 0, 0, 0, 0, 1)
        def descends(bits, kernel):
            return all(sum(a*b for a, b in zip(bits, k)) % 2 == 0 for k in kernel)
        for row in self.rows.values():
            self.assertEqual(row["C_genuine"], descends(root, row["kernel"]))
            self.assertEqual(row["Sigma_N_genuine"], descends(sigma, row["kernel"]))
            self.assertTrue(row["Sigma_R_genuine"])
        self.assertEqual([r["C_genuine"] for r in self.rows.values()], [False, True, False, False, True])
        self.assertEqual([r["Sigma_N_genuine"] for r in self.rows.values()], [False, False, True, False, True])

    def test_diagonal_module_not_separate_factors(self):
        row = self.rows["diagonal"]
        self.assertTrue(row["Sigma_C_with_determinant_ND_genuine"])
        self.assertFalse(row["C_genuine"])
        self.assertFalse(row["Sigma_N_genuine"])

    def test_index_polynomial_independent_series(self):
        t, q = sp.symbols("t q")
        for with_R in (False, True):
            ch = (2-audit.r2*t*t) if with_R else 1
            integrand = (1-audit.p*t*t/24)*sp.exp((q+audit.x/2)*t)*ch
            degree = sp.series(integrand, t, 0, 4).removeO().expand().coeff(t, 3)
            self.assertEqual(sp.expand(degree-audit.J(q, with_R=with_R)), 0)

    def test_bare_index_difference(self):
        self.assertEqual(audit.index_difference(audit.d), audit.d**3+audit.x*audit.d**2/2)

    def test_completed_index_difference(self):
        self.assertEqual(audit.index_difference(audit.d, True), 2*audit.d**3+audit.x*audit.d**2)

    def test_root_index_plus_cup(self):
        self.assertEqual(sp.expand(audit.index_difference(audit.c)+audit.c**3-audit.Q(determinant=2*audit.c)), 0)

    def test_level_curvatures(self):
        for row in self.rows.values():
            self.assertEqual(sp.expand(sp.sympify(row["quantized_level_density"])-row["minimum_positive_integer_stack"]*sp.sympify(row["Q_in_genuine_line_coordinates"])), 0)

    def test_no_gravity_or_R_remainder(self):
        for row in self.rows.values():
            self.assertFalse(sp.sympify(row["quantized_level_density"]).has(audit.p, audit.r2))

    def test_integral_cup_coefficients(self):
        for key in ("old", "gauge_root", "diagonal"):
            row = self.rows[key]
            self.assertTrue(all(coefficient.is_Integer for coefficient in sp.Poly(sp.sympify(row["quantized_level_density"])).coeffs()))
            self.assertIn("hol(", row["positive_closed5_response"])

    def test_primitive_CP3_periods(self):
        for row in self.rows.values():
            w = row["primitive_CP3_witness"]
            nx, dd = w["N_degree"], w["D_degree"]
            independent = sp.Rational(dd*dd*(2*dd+nx), 8)
            self.assertEqual(independent, sp.Rational(1, row["minimum_positive_integer_stack"]))

    def test_cp3_endpoints_close_in_correct_kernel(self):
        for row in self.rows.values():
            w = row["primitive_CP3_witness"]
            nx, dd, rr, ss = w["N_degree"], w["D_degree"], w["R_H3_H267_path_endpoint_bit"], w["Spin11_path_endpoint_bit"]
            endpoint = (0, nx % 2, ss, rr, rr, rr, dd % 2)
            self.assertEqual(list(endpoint), w["cocharacter_endpoint"])
            self.assertIn(endpoint, audit.kernels()[row["id"]])

    def test_primitive_necessity_for_all_tested_stacks(self):
        for row in self.rows.values():
            q = sp.Rational(row["primitive_CP3_witness"]["Q_period"])
            for n in range(1, 65):
                self.assertEqual((n*q).is_Integer, n % row["minimum_positive_integer_stack"] == 0)

    def test_independent_CP3_euler_indices(self):
        for row in self.rows.values():
            w = row["primitive_CP3_witness"]
            got = []
            for n in range(3):
                weights = [k+n*w["index_twist_line_degree"] for k in w["total_Clifford_base_line_degrees"]]
                got.append(int(sum(sp.Rational(k*(k*k-1), 6) for k in weights)))
            self.assertEqual(got, w["indices_at_powers_0_1_2"])

    def test_negative_index_is_not_kernel_dimension(self):
        self.assertEqual(self.rows["gauge_root"]["primitive_CP3_witness"]["indices_at_powers_0_1_2"], [-1, 0, 0])
        self.assertIn("negative kernel dimensions", self.report["primary_sources"][-1]["use"])

    def test_CP3_tangent_spin_and_p1(self):
        self.assertEqual(4 % 2, 0)
        self.assertEqual(4**2-2*6, 4)
        for row in self.rows.values():
            self.assertIn("p1=4H^2", row["primitive_CP3_witness"]["manifold"])

    def test_diagonal_normal_determinant(self):
        self.assertEqual(sp.expand(audit.Q().subs(audit.x, audit.ell-audit.d)), (audit.d**3+audit.ell*audit.d**2)/8)
        w = self.rows["diagonal"]["primitive_CP3_witness"]
        self.assertEqual(w["N_degree"]+w["D_degree"], 0)
        self.assertEqual(w["D_degree"] % 2, 1)

    def test_quantization_on_small_cocharacter_grid(self):
        for identifier, kernel in audit.kernels().items():
            level = self.rows[identifier]["minimum_positive_integer_stack"]
            for nx, dd, ss, rr in itertools.product(range(-3, 4), range(-3, 4), (0, 1), (0, 1)):
                if (0, nx % 2, ss, rr, rr, rr, dd % 2) in kernel:
                    self.assertTrue((level*sp.Rational(dd*dd*(2*dd+nx), 8)).is_Integer)

    def test_nonbounding_not_boundary_trivialization(self):
        scope = self.report["response_scope"]
        self.assertIn("dim(kernel)", scope["xi"])
        self.assertIn("without a chosen filling", scope["nonbounding_closed5"])
        self.assertFalse(scope["closed_boundary_corner_Dai_Freed_trivializations_constructed"])

    def test_equal_curvature_not_equal_phase(self):
        for row in self.rows.values():
            self.assertFalse(row["matching_curvature_claims_full_phase_equality"])
            self.assertFalse(row["any_flat_bordism_difference_between_choices_computed"])

    def test_physical_scope_not_promoted(self):
        self.assertFalse(self.report["category_scope"]["physical_orbifold_or_Higgs_background_category_identified"])
        self.assertFalse(self.report["category_scope"]["finite_C8_only_torsion_anomaly_classification"])
        for row in self.rows.values():
            self.assertFalse(row["primitive_CP3_witness"]["actual_physical_or_Higgs_background_admissibility_proved"])
        self.assertEqual(self.report["terminal_decision"]["closed_gates"], [])

    def test_resealed_minimum_tamper_rejected(self):
        bad = copy.deepcopy(self.report)
        bad["classification"][3]["minimum_positive_integer_stack"] = 1
        bad["core_sha256"] = audit.common.canonical_sha(bad)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(bad)

    def test_resealed_scope_tamper_rejected(self):
        bad = copy.deepcopy(self.report)
        bad["terminal_decision"]["full_physical_anomaly_cancelled"] = True
        bad["core_sha256"] = audit.common.canonical_sha(bad)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(bad)

    def test_fresh_source_pins(self):
        with patch.object(audit.common, "file_sha", return_value="0"*64):
            with self.assertRaises(RuntimeError):
                audit.build_certificate()

    def test_unknown_cover_rejected(self):
        with self.assertRaises(ValueError):
            audit.cp3_witness("all_other_groups")


if __name__ == "__main__":
    unittest.main()
