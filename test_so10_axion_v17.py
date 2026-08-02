#!/usr/bin/env python3
"""Regression, property and end-to-end tests for the v17 package."""

from __future__ import annotations

import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np

import so10_quality_v17 as quality


PACKAGE_DIR = Path(__file__).resolve().parent
ENGINE = PACKAGE_DIR / "so10_axion_v17_engine.py"


class ExplicitOperatorTests(unittest.TestCase):
    def test_all_regression_operators_are_lorentz_and_centre_admissible(self):
        for name, operator in quality.EXPLICIT_OPERATORS.items():
            with self.subTest(name=name):
                self.assertEqual(operator.n_fermions % 2, 0)
                self.assertEqual(operator.centre % 4, 0)
                self.assertEqual(operator.pq % 17, 0)

    def test_dimension_six_portal(self):
        operator = quality.EXPLICIT_OPERATORS["O6_portal"]
        self.assertEqual((operator.dimension, operator.pq, operator.vector), (6, -17, -1))

    def test_dimension_eight_vector_breaker(self):
        operator = quality.EXPLICIT_OPERATORS["O8_vector_breaker"]
        self.assertEqual((operator.dimension, operator.pq, operator.vector), (8, 0, 4))

    def test_v15_omitted_dimension_ten_operator(self):
        operator = quality.EXPLICIT_OPERATORS["O10_six_fermion"]
        self.assertEqual((operator.dimension, operator.pq, operator.vector), (10, -34, -6))
        self.assertEqual(operator.triality % 3, 0)

    def test_v15_omitted_dimension_twelve_operator(self):
        operator = quality.EXPLICIT_OPERATORS["O12_mixed"]
        self.assertEqual((operator.dimension, operator.pq, operator.vector), (12, -17, 3))
        self.assertEqual(operator.triality % 3, 0)

    def test_family_operator_has_required_conjugate_higgs(self):
        operator = quality.EXPLICIT_OPERATORS["O20_family"]
        self.assertEqual((operator.dimension, operator.pq), (20, 68))
        self.assertIn("Hp", operator.label)


class CatalogueAndClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = quality.enumerate_overcomplete_catalog(max_dimension=20)
        cls.catalog_z3 = quality.enumerate_overcomplete_catalog(
            max_dimension=20, require_triality=True
        )

    def test_local_minimum_is_not_misidentified_as_vacuum_term(self):
        self.assertEqual(quality.minimum_local_pq_dimension(self.catalog), 6)
        closure = quality.minimum_vacuum_closure(self.catalog, max_planck_power=16)
        self.assertIsNotNone(closure)
        self.assertEqual(closure.planck_power, 12)

    def test_no_renormalizable_spectator_vector_breaker(self):
        self.assertEqual(quality.renormalizable_vector_breakers(self.catalog), [])
        self.assertEqual(
            quality.minimum_q0_vector_breaking_dimension(self.catalog), 8
        )

    def test_exhaustive_overcatalogue_has_no_closure_through_p11(self):
        self.assertIsNone(
            quality.minimum_vacuum_closure(self.catalog, max_planck_power=11)
        )

    def test_first_overcatalogue_closure(self):
        closure = quality.minimum_vacuum_closure(self.catalog, max_planck_power=12)
        self.assertIsNotNone(closure)
        self.assertEqual((closure.planck_power, closure.pq, closure.vector), (12, -68, 0))

    def test_cutoff_is_complete_for_p11_exclusion(self):
        # Any item participating at P<=11 has d=P+4<=15.  The result must
        # therefore be unchanged when the catalogue cutoff rises to 20.
        cutoff_catalog = quality.enumerate_overcomplete_catalog(max_dimension=15)
        self.assertIsNone(
            quality.minimum_vacuum_closure(cutoff_catalog, max_planck_power=11)
        )
        closure = quality.minimum_vacuum_closure(cutoff_catalog, max_planck_power=12)
        self.assertIsNotNone(closure)
        self.assertEqual(closure.planck_power, 12)

    def test_explicit_so10_saturation_certificate(self):
        certificate = quality.explicit_p12_certificate()
        labels = [op.label for op in certificate.operators]
        self.assertEqual((certificate.planck_power, certificate.pq, certificate.vector), (12, -68, 0))
        self.assertEqual(labels.count(quality.EXPLICIT_OPERATORS["O6_portal"].label), 4)
        self.assertEqual(labels.count(quality.EXPLICIT_OPERATORS["O8_vector_breaker"].label), 1)

    def test_optional_z3_regressions(self):
        self.assertEqual(quality.minimum_local_pq_dimension(self.catalog_z3), 10)
        closure = quality.minimum_vacuum_closure(
            self.catalog_z3, max_planck_power=16
        )
        self.assertIsNotNone(closure)
        self.assertEqual(closure.planck_power, 13)


class PhysicsInvariantTests(unittest.TestCase):
    def test_one_sided_mass_matrix_is_phase_independent(self):
        phases = np.linspace(0.0, 2.0 * math.pi, 257)
        expected = quality.one_sided_mass_invariants(7.0, 0.31, phases)
        self.assertTrue(all(pair == expected[0] for pair in expected))
        spectra = []
        for phase in phases:
            matrix = np.array(
                [[0.0, 7.0], [7.0, 0.31 * np.exp(1j * phase)]],
                dtype=complex,
            )
            spectra.append(np.linalg.eigvalsh(matrix.conj().T @ matrix))
        np.testing.assert_allclose(spectra, np.repeat([spectra[0]], len(phases), axis=0), rtol=1e-13)

    def test_quality_numbers(self):
        scale = 6.313855e11
        scalar = quality.scalar_quality_numbers(scale)
        self.assertEqual(scalar["leading_dimension"], 17)
        self.assertEqual(scalar["minimum_safe_dimension"], 14)
        self.assertAlmostEqual(scalar["delta_theta_scalar"] / 3.2358e-37, 1.0, places=3)
        bound = quality.nda_vacuum_bound(scale, 12)
        self.assertAlmostEqual(bound / 4.51792e-28, 1.0, places=5)
        self.assertGreater(1.0e-10 / bound, 2.0e17)

    def test_optional_z51_anomaly_arithmetic(self):
        anomaly = quality.combined_z51_anomalies()
        self.assertEqual(
            [anomaly["mixed"], anomaly["gravitational"], anomaly["cubic"]],
            [408, 3264, 935136],
        )
        self.assertEqual(anomaly["quotients"], [8, 64, 18336])
        self.assertTrue(anomaly["all_divisible_by_51"])


class EngineIntegrationTests(unittest.TestCase):
    def run_engine(self, *extra: str):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        verdict = Path(temporary.name) / "verdict.json"
        command = [
            sys.executable,
            str(ENGINE),
            "--output",
            str(verdict),
            *extra,
        ]
        completed = subprocess.run(
            command,
            cwd=PACKAGE_DIR,
            text=True,
            capture_output=True,
            timeout=90,
            check=False,
        )
        payload = json.loads(verdict.read_text()) if verdict.exists() else None
        return completed, payload

    def test_engine_success_exit_and_verdict(self):
        completed, payload = self.run_engine("--trials", "10000")
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(payload["n_checks_total"], 65)
        self.assertEqual(payload["n_checks_failed"], 0)
        self.assertEqual(payload["failures"], [])
        self.assertEqual(
            payload["quality"]["vacuum_closure_minimum"]["overcatalogue_result"]["P"],
            12,
        )
        self.assertEqual(payload["referee_audit"]["vacuum_graph"]["loops"], 2)
        self.assertEqual(
            payload["referee_audit"]["invariants"]["closure_group_factor"],
            2560,
        )

    def test_engine_failure_exit_and_machine_readable_failure(self):
        completed, payload = self.run_engine(
            "--trials", "1000", "--inject-failure"
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(payload["n_checks_total"], 66)
        self.assertIn(
            "injected failure exercises nonzero-exit path", payload["failures"]
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
