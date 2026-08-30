#!/usr/bin/env python3
"""Adversarial tests for the exact physical-SM five-amplitude theorem."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import sympy as sp

import exact_physical_sm_five_amplitude_equality_v20 as theorem


EXPECTED_CORE_SHA256 = "d0bf68bd5007f71295665add186761577dbe0d67d2d8e5bd1fb4e4eeb669a271"
EXPECTED_SOURCE_SHA256 = "777b11664047574432405373b71bf30ed473fa735bdce56ef95be43dccc76972"
EXPECTED_JSON_SHA256 = "61bca8d55230b798b1d45ae4496c2b1b39490f73d0596e671478a388f72449ce"
EXPECTED_MD_SHA256 = "5a22cb172ff26ac698ca19bb722590cf15368c30d37190a211e5f5f1eff214d6"


class ExactPhysicalSMFiveAmplitudeEqualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(theorem.OUT_JSON.read_text(encoding="utf-8"))

    def test_schema_status_checks_and_core_are_frozen(self) -> None:
        self.assertEqual(self.report["schema"], theorem.SCHEMA)
        self.assertEqual(self.report["status"], theorem.STATUS)
        self.assertEqual(self.report["n_checks"], 12)
        self.assertEqual(self.report["n_failed"], 0)
        self.assertEqual(self.report["failures"], [])
        self.assertTrue(all(self.report["checks"].values()))
        self.assertEqual(self.report["integrity"]["core_sha256"], EXPECTED_CORE_SHA256)

    def test_exact_source_table_and_polynomial_are_frozen(self) -> None:
        restriction = self.report["restriction"]
        polynomial = self.report["exact_polynomial"]
        self.assertEqual(restriction["ambient_real_field_dimension"], 486)
        self.assertEqual(restriction["slice_dimension"], 5)
        self.assertFalse(restriction["polynomial_fitting_or_float_sampling_used"])
        self.assertTrue(restriction["exact_algebra_is_conditional_on_frozen_upstream_witness_table"])
        self.assertFalse(restriction["witness_coefficients_directly_derived_from_integer_projector_source_algebra"])
        self.assertFalse(restriction["target_invariant_table_independently_rederived_by_integer_arithmetic_in_this_artifact"])
        self.assertEqual(restriction["renormalizable_witness_nonzero_parameter_count"], 37)
        self.assertEqual(restriction["nonzero_target_contribution_count"], 28)
        self.assertEqual(polynomial["common_denominator"], theorem.EXPECTED_DENOMINATOR)
        self.assertEqual(polynomial["aggregate_monomial_count"], 21)
        self.assertEqual(len(polynomial["source_contributions"]), 28)

    def test_exact_groebner_basis_and_mutual_ideal_reduction(self) -> None:
        certificate = self.report["exact_Groebner_certificate"]
        self.assertEqual(
            certificate["reduced_Groebner_basis"],
            ["h**2 - 1", "d**2 - 1", "s**2 - 1", "x**2 - 1", "p - 1"],
        )
        self.assertTrue(certificate["observed_basis_equals_expected"])
        self.assertTrue(certificate["source_ideal_contained_in_expected_ideal"])
        self.assertTrue(certificate["expected_ideal_contained_in_source_ideal"])
        self.assertTrue(certificate["ideals_equal_by_mutual_exact_reduction"])
        self.assertTrue(certificate["ideal_zero_dimensional"])
        self.assertTrue(certificate["ideal_is_radical_from_squarefree_separated_basis"])

    def test_exactly_sixteen_real_sign_variants_without_orbit_promotion(self) -> None:
        certificate = self.report["exact_Groebner_certificate"]
        variants = self.report["discrete_variants"]
        self.assertEqual(certificate["complex_solution_count_with_multiplicity"], 16)
        self.assertTrue(certificate["all_solutions_real"])
        self.assertEqual(variants["count"], 16)
        self.assertTrue(variants["exact_discrete_sign_symmetries_of_selected_witness"])
        self.assertEqual(variants["full_witness_support_row_count"], 37)
        self.assertEqual(variants["zero_at_target_but_parity_checked_row_count"], 9)
        self.assertTrue(variants["all_support_rows_even_in_h_d_s_x"])
        self.assertFalse(variants["continuous_SO10_x_U1X_x_PQ_orbit_equivalence_classified"])

    def test_target_and_slice_hessian_are_exact(self) -> None:
        potential = theorem.exact_slice_potential()
        variables = theorem.symbols()
        target = dict.fromkeys(variables, 1)
        self.assertEqual(potential.subs(target), -1)
        self.assertTrue(all(sp.diff(potential, value).subs(target) == 0 for value in variables))
        self.assertTrue(self.report["exact_Groebner_certificate"]["target_slice_Hessian_positive_definite"])

    def test_physical_g3_g4_g5_remain_fail_closed(self) -> None:
        claims = self.report["closure_claims"]
        self.assertTrue(claims["exact_radial_theorem_strictly_extended"])
        self.assertTrue(claims["five_real_amplitude_slice_stationary_equality_classified"])
        self.assertFalse(claims["full_486_field_stationary_equality_classified"])
        self.assertFalse(claims["declared_continuous_symmetry_orbit_equivalence_of_16_variants_proved"])
        self.assertFalse(claims["direct_source_algebra_full_486_Hessian_available"])
        self.assertFalse(claims["physical_SM_G3_closed"])
        self.assertFalse(claims["physical_SM_G4_closed"])
        self.assertFalse(claims["physical_SM_G5_closed"])

    def test_source_or_contribution_drift_fails_closed(self) -> None:
        with mock.patch.object(theorem, "_portable_lf_sha256", return_value="0" * 64):
            with self.assertRaisesRegex(ArithmeticError, "source dependency drifted"):
                theorem.source_bindings()
        rows = list(theorem.SOURCE_CONTRIBUTIONS)
        parameter_id, exponents, coefficient, target_value = rows[0]
        rows[0] = (parameter_id, exponents, str(sp.Rational(coefficient) + 1), target_value)
        with self.assertRaisesRegex(ArithmeticError, "source table drifted"):
            theorem.exact_slice_potential(rows)

    def test_dependency_hash_is_checkout_eol_portable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            lf = Path(directory) / "lf.txt"
            crlf = Path(directory) / "crlf.txt"
            lf.write_bytes(b"alpha\nbeta\n")
            crlf.write_bytes(b"alpha\r\nbeta\r\n")
            self.assertEqual(
                theorem._portable_lf_sha256(lf),
                theorem._portable_lf_sha256(crlf),
            )

    def test_outputs_and_raw_hashes_are_frozen(self) -> None:
        rebuilt = theorem.build_report()
        self.assertEqual(
            theorem.OUT_JSON.read_text(encoding="utf-8"),
            json.dumps(theorem._jsonable(rebuilt), indent=2) + "\n",
        )
        self.assertEqual(theorem.OUT_MD.read_text(encoding="utf-8"), theorem.render_markdown(rebuilt))
        expected = {
            Path(theorem.__file__).resolve(): EXPECTED_SOURCE_SHA256,
            theorem.OUT_JSON: EXPECTED_JSON_SHA256,
            theorem.OUT_MD: EXPECTED_MD_SHA256,
        }
        for path, digest in expected.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)

    def test_read_only_cli_does_not_mutate_outputs(self) -> None:
        before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in (theorem.OUT_JSON, theorem.OUT_MD)}
        result = subprocess.run(
            [sys.executable, str(Path(theorem.__file__).resolve())],
            cwd=theorem.ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in (theorem.OUT_JSON, theorem.OUT_MD)}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
