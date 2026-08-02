#!/usr/bin/env python3
"""Multi-state test suite for the v18 engine.

Independently re-derives (without importing the engine) the anomalon
arithmetic, the UV quality theorem, the two-loop master integral and the
general-ansatz minimality; then exercises the engine subprocess in three
states: clean pass, forced failure, and determinism of the verdict JSON.

Usage: python test_so10_axion_v18.py
"""
import itertools, json, math, pathlib, subprocess, sys, unittest

HERE = pathlib.Path(__file__).resolve().parent
ENGINE = HERE / 'so10_axion_v18_engine.py'
PY = sys.executable


class AnomalonArithmeticTests(unittest.TestCase):
    """Independent integer re-derivation of the S11 UV completion."""

    def test_ir_residuals(self):
        a, b, k = 2, -6, 5
        self.assertEqual(6 + 2 * k * (a + b), -34)
        self.assertEqual(48 + 16 * k * (a + b), -272)
        self.assertEqual(48 + 80 * (a ** 3 + b ** 3), -16592)

    def test_exact_closure_of_the_chosen_set(self):
        c, d = 1, 16
        s1, s2 = (33, -16), (31, -48)
        self.assertEqual(-34 + 2 * (c + d), 0)
        self.assertEqual(-272 + 16 * (c + d) + sum(s1) + sum(s2), 0)
        cubic = (-16592 + 16 * (c ** 3 + d ** 3)
                 + s1[0] ** 3 + s1[1] ** 3 + s2[0] ** 3 + s2[1] ** 3)
        self.assertEqual(cubic, 0)

    def test_all_anomalons_vector_like_mod_17(self):
        for p, q in [(1, 16), (33, -16), (31, -48)]:
            self.assertEqual((p + q) % 17, 0)

    def test_masses_from_phi_only(self):
        # Phi charge +17; each pair must sum to +-17
        for p, q in [(1, 16), (33, -16), (31, -48)]:
            self.assertIn(p + q, (17, -17))


class UVQualityTheoremTests(unittest.TestCase):
    """Brute-force re-derivation of the dimension-21 minimum."""

    def test_dim21_is_minimal(self):
        best = None
        for a in [x for x in range(-10, 11) if x]:
            for b in range(-40, 41):
                num = -17 * a - 4 * b
                if num % 4:
                    continue
                jp = num // 4
                dim = abs(a) + abs(b) + 2 * abs(jp)
                if best is None or dim < best[0]:
                    best = (dim, a, b)
        self.assertEqual(best[0], 21)
        self.assertEqual(abs(best[1]), 4)
        self.assertEqual(abs(best[2]), 17)

    def test_suppression_at_mgut(self):
        cuv = (9.9176e15 / (math.sqrt(2) * 2.435e18)) ** 4
        self.assertAlmostEqual(cuv / 6.88e-11, 1.0, places=2)


class TwoLoopIntegralTests(unittest.TestCase):
    """The master integral has the exact analytic value 1 at mu = 0."""

    def test_exact_value_by_substitution(self):
        # int_0^inf ln(1+s)/(1+s)^2 ds = 1 exactly; midpoint Riemann
        # has O(1/n) endpoint error, so ~2e-6 at n = 200000
        n, total = 200000, 0.0
        for i in range(n):
            t = (i + 0.5) / n
            s = t / (1 - t)
            total += math.log(1 + s) / (1 + s) ** 2 / (1 - t) ** 2 / n
        self.assertAlmostEqual(total, 1.0, places=4)


class GeneralAnsatzMinimalityTests(unittest.TestCase):
    """Absolute enumeration beyond the identical-pair ansatz."""

    def test_mixed_class_forces_k5_for_any_charges(self):
        ks = [k for k in range(1, 18) if (6 + 9 * k) % 17 == 0]
        self.assertEqual(ks, [5])

    def test_no_solution_k_le_3_exhaustive(self):
        for k in (1, 2, 3):
            sols = [c for c in itertools.product(range(17), repeat=k)
                    if (6 + 26 * k) % 17 == 0
                    and (48 + 80 * sum(a ** 3 + (13 - a) ** 3
                                       for a in c)) % 17 == 0]
            self.assertEqual(sols, [])


class EngineStateTests(unittest.TestCase):
    """Multi-state subprocess tests of the actual engine."""

    @classmethod
    def setUpClass(cls):
        cls.clean = subprocess.run([PY, str(ENGINE)], cwd=HERE,
                                   capture_output=True, text=True)

    def test_state_clean_pass(self):
        self.assertEqual(self.clean.returncode, 0, self.clean.stdout)
        self.assertIn('ALL CHECKS PASS', self.clean.stdout)
        self.assertNotIn('[FAIL]', self.clean.stdout)

    def test_state_forced_failure(self):
        r = subprocess.run([PY, str(ENGINE), '--force-fail'], cwd=HERE,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn('[FAIL] intentional failure path', r.stdout)

    def test_state_deterministic_verdict(self):
        v1 = json.loads((HERE / 'so10_axion_v18_verdict.json')
                        .read_text())
        subprocess.run([PY, str(ENGINE)], cwd=HERE,
                       capture_output=True, text=True)
        v2 = json.loads((HERE / 'so10_axion_v18_verdict.json')
                        .read_text())
        # forced-fail run above must not have poisoned the clean verdict
        self.assertEqual(v2['n_checks_failed'], 0)
        self.assertEqual(v1['uv_completion'], v2['uv_completion'])
        self.assertEqual(v1['two_loop'], v2['two_loop'])

    def test_verdict_contents(self):
        v = json.loads((HERE / 'so10_axion_v18_verdict.json')
                       .read_text())
        self.assertEqual(v['uv_completion']['anomalon_16_pair'], [1, 16])
        self.assertEqual(v['uv_completion']['min_uv_pq_breaking']['dim'],
                         21)
        self.assertAlmostEqual(v['two_loop']['K'], 1.0, places=6)
        self.assertLess(v['two_loop']['delta_theta_bar_total'], 1e-10)
        self.assertEqual(v['falsification']['general_ansatz_k_min'], 5)
        self.assertEqual(len(v['falsification']['matrix']), 7)


if __name__ == '__main__':
    unittest.main(verbosity=2)
