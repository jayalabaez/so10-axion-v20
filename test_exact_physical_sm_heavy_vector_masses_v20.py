#!/usr/bin/env python3
"""Adversarial tests for the exact physical-SM heavy-vector mass theorem."""

from __future__ import annotations

import hashlib
import json
import math
import unittest
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

import numpy as np
import sympy as sp

import exact_physical_sm_heavy_vector_masses_v20 as theorem


EXPECTED_SOURCE_PORTABLE_SHA256 = "6839c8fdada9fc89efdde26c62188dfa99b7a34ee072cec93c0b3405c117d587"
EXPECTED_CORE_SHA256 = "86c3e0dfda09366b1cf06c8c3a8dcb3dfdf3bfe1555a41214d380ed4db329894"
EXPECTED_REPORT_PORTABLE_SHA256 = {
    "json": "665840c68ce5522f8faeb9cadceba56288c7d9ad0d2e468d29a6a5c4413b17e0",
    "md": "47b598aed6af33a89ecc47598d5280258e0b5304a23a8873764c9c4778768fff",
}


def _sha256(path: Path, *, portable: bool = False) -> str:
    data = path.read_bytes()
    if portable:
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


class ExactPhysicalSMHeavyVectorMassTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = theorem.build_report()
        cls.tangent = theorem.integer_tangent_matrix()
        cls.gram = theorem.bare_gram_matrix()

    def test_01_frozen_source_core_and_reports(self) -> None:
        self.assertEqual(
            _sha256(Path(theorem.__file__), portable=True),
            EXPECTED_SOURCE_PORTABLE_SHA256,
        )
        self.assertEqual(self.report["core_sha256"], EXPECTED_CORE_SHA256)
        self.assertEqual(
            _sha256(theorem.OUT_JSON, portable=True),
            EXPECTED_REPORT_PORTABLE_SHA256["json"],
        )
        self.assertEqual(
            _sha256(theorem.OUT_MD, portable=True),
            EXPECTED_REPORT_PORTABLE_SHA256["md"],
        )

    def test_02_all_direct_inputs_are_source_bound(self) -> None:
        observed = theorem.source_guard()
        self.assertEqual(set(observed), set(theorem.DEPENDENCIES))
        for name, (_path, expected, mode) in theorem.DEPENDENCIES.items():
            self.assertEqual(observed[name]["sha256"], expected)
            self.assertEqual(observed[name]["mode"], mode)

    def test_03_dependency_drift_fails_closed(self) -> None:
        original = theorem._digest

        def drift(path: Path, mode: str = "raw") -> str:
            if path == theorem.PHYSICAL_SOURCE:
                return "0" * 64
            return original(path, mode)

        with patch.object(theorem, "_digest", side_effect=drift):
            with self.assertRaisesRegex(ArithmeticError, "dependency drifted"):
                theorem.source_guard()

    def test_04_target_and_chart_normalizations_are_exact(self) -> None:
        self.assertEqual(theorem.TARGET_DENOMINATOR, 20)
        self.assertEqual(theorem.physical.TARGET_DENOMINATOR, 20)
        self.assertEqual(theorem.physical.integer_target_vector() @ theorem.physical.integer_target_vector(), 1632)
        self.assertIn("K_2 = 1/2 q^T q", theorem.CHART_SOURCE.read_text(encoding="utf-8"))

    def test_05_so10_generator_rescaling_matches_T10_one(self) -> None:
        audit = theorem.vector_generator_normalization()
        self.assertEqual(audit["bare_plane_trace_LtL"], 2)
        self.assertEqual(audit["canonical_Tr10_H2"], "1")
        self.assertEqual(audit["authoritative_T10"], "1")
        self.assertTrue(audit["normalization_matches"])

    def test_06_exact_tangent_and_gram_shapes(self) -> None:
        self.assertEqual(self.tangent.shape, (486, 46))
        self.assertEqual(self.gram.shape, (46, 46))
        self.assertEqual(self.tangent.dtype, np.int64)
        self.assertEqual(self.gram.dtype, np.int64)
        np.testing.assert_array_equal(self.gram, self.tangent.T @ self.tangent)
        np.testing.assert_array_equal(self.gram, self.gram.T)

    def test_07_field_block_grams_reconstruct_full_gram(self) -> None:
        blocks = theorem.field_block_gram_matrices()
        self.assertEqual(set(blocks), {"Phi210", "H10", "Sigma126bar", "S", "Phi17"})
        observed = sum(blocks.values(), np.zeros((46, 46), dtype=np.int64))
        np.testing.assert_array_equal(observed, self.gram)
        self.assertEqual(
            {name: int(np.trace(value)) for name, value in blocks.items()},
            {"Phi210": 9600, "H10": 10400, "Sigma126bar": 464, "S": 256, "Phi17": 115600},
        )

    def test_07b_u1x_block_entries_replay_declared_charges(self) -> None:
        blocks = theorem.field_block_gram_matrices()
        self.assertEqual(
            {name: int(value[45, 45]) for name, value in blocks.items()},
            {"Phi210": 0, "H10": 3200, "Sigma126bar": 64, "S": 256, "Phi17": 115600},
        )
        self.assertEqual(int(blocks["H10"][44, 45]), -1600)
        self.assertEqual(int(blocks["Sigma126bar"][44, 45]), -32)
        self.assertEqual(
            theorem.physical.exact_symmetry_certificate()["live_chart_binding"]["maximum_abs_residual"],
            0.0,
        )

    def test_08_sparse_exact_matrix_is_lossless(self) -> None:
        reconstructed = np.zeros((46, 46), dtype=np.int64)
        for row in theorem.sparse_exact_mass_matrix():
            first, second = row["row"], row["column"]
            reconstructed[first, second] = row["bare_gram"]
            reconstructed[second, first] = row["bare_gram"]
        np.testing.assert_array_equal(reconstructed, self.gram)
        self.assertEqual(np.count_nonzero(self.gram), 116)
        self.assertEqual(len(theorem.sparse_exact_mass_matrix()), 81)

    def test_09_canonical_matrix_matches_exact_sparse_formula(self) -> None:
        g10, gx, scale = 0.71, 0.23, 17.0
        observed = theorem.canonical_mass_matrix(g10=g10, g_x=gx, vev_scale=scale)
        reconstructed = np.zeros((46, 46), dtype=float)
        for row in theorem.sparse_exact_mass_matrix():
            coefficient = row["coefficient_rational"] + math.sqrt(2) * row["coefficient_sqrt2"]
            if row["monomial"] == "g10^2":
                monomial = g10**2
            elif row["monomial"] == "gX^2":
                monomial = gx**2
            else:
                monomial = g10 * gx
            value = scale**2 * coefficient * monomial / 800
            reconstructed[row["row"], row["column"]] = value
            reconstructed[row["column"], row["row"]] = value
        np.testing.assert_allclose(observed, reconstructed, rtol=3e-16, atol=2e-13)

    def test_10_exact_rank_and_nullity_are_37_and_9(self) -> None:
        certificate = theorem.exact_rank_kernel_certificate()
        self.assertEqual(certificate["exact_tangent_rank"], 37)
        self.assertEqual(certificate["exact_gram_rank"], 37)
        self.assertEqual(certificate["exact_gram_nullity"], 9)

    def test_11_standard_su3_plus_em_basis_is_complete_kernel(self) -> None:
        basis = sp.Matrix.hstack(*(sp.Matrix(row) for row in theorem.unbroken_basis()))
        self.assertEqual(basis.shape, (46, 9))
        self.assertEqual(basis.rank(), 9)
        self.assertEqual(sp.Matrix(self.gram) * basis, sp.zeros(46, 9))
        self.assertTrue(theorem.exact_rank_kernel_certificate()["declared_basis_is_complete_kernel"])

    def test_12_goldstone_image_and_uneaten_pq_dimensions(self) -> None:
        certificate = theorem.exact_rank_kernel_certificate()
        self.assertEqual(certificate["gauge_Goldstone_image_dimension"], 37)
        self.assertTrue(certificate["ker_M2_equals_ker_coupled_tangent"])
        self.assertEqual(certificate["full_gauge_plus_PQ_tangent_rank"], 38)
        self.assertEqual(certificate["uneaten_accidental_PQ_dimension"], 1)

    def test_13_positive_couplings_preserve_rank_and_psd(self) -> None:
        for g10, gx, scale in ((1.0, 1.0, 1.0), (0.7, 0.2, 11.0), (0.13, 1.9, 0.04)):
            values = np.linalg.eigvalsh(theorem.canonical_mass_matrix(g10=g10, g_x=gx, vev_scale=scale))
            tolerance = max(values[-1], 1.0) * 2e-11
            self.assertEqual(np.count_nonzero(values > tolerance), 37)
            self.assertGreaterEqual(values[0], -tolerance)

    def test_14_nonpositive_or_nonfinite_parameters_are_rejected(self) -> None:
        for kwargs in (
            {"g10": 0.0, "g_x": 1.0, "vev_scale": 1.0},
            {"g10": 1.0, "g_x": -1.0, "vev_scale": 1.0},
            {"g10": 1.0, "g_x": 1.0, "vev_scale": 0.0},
            {"g10": math.inf, "g_x": 1.0, "vev_scale": 1.0},
        ):
            with self.assertRaises(ValueError):
                theorem.canonical_mass_matrix(**kwargs)
        with self.assertRaises(ValueError):
            theorem.one_loop_vector_log_inputs(g10=1, g_x=1, vev_scale=1, matching_scale=0)

    def test_15_exact_color_and_charge_operators_commute_with_mass_gram(self) -> None:
        color, charge = theorem.adjoint_sector_operators()
        np.testing.assert_array_equal(self.gram @ color, color @ self.gram)
        np.testing.assert_array_equal(self.gram @ charge, charge @ self.gram)
        self.assertEqual(sorted(set(np.linalg.eigvalsh(color).round().astype(int))), [0, 16, 36])
        self.assertEqual(sorted(set(np.linalg.eigvalsh(charge).round().astype(int))), [0, 1, 4, 9, 16])

    def test_16_exact_joint_projectors_are_complete(self) -> None:
        projectors = theorem.exact_joint_sector_projectors()
        self.assertEqual(set(projectors), {(0, 0), (0, 9), (16, 1), (16, 4), (16, 16), (36, 0)})
        self.assertEqual(
            {key: int(sp.trace(value)) for key, value in projectors.items()},
            {(0, 0): 4, (0, 9): 4, (16, 1): 12, (16, 4): 12, (16, 16): 6, (36, 0): 8},
        )
        self.assertEqual(sum(projectors.values(), sp.zeros(46)), sp.eye(46))

    def test_17_non_neutral_sector_polynomials_and_multiplicities_are_exact(self) -> None:
        audit = theorem.exact_sector_audit()
        self.assertTrue(audit["all_sector_mass_polynomials_exact"])
        self.assertTrue(audit["all_sector_multiplicities_exact"])
        actual = {
            (row["12C2_SU3"], row["Q3_squared"]): row.get("bare_gram_spectrum")
            for row in audit["sectors"]
            if "bare_gram_spectrum" in row
        }
        expected = {
            key: [{"bare_gram_eigenvalue": value, "multiplicity": multiplicity} for value, multiplicity in spectrum]
            for key, spectrum in theorem.RAW_SECTOR_SPECTRA.items()
        }
        self.assertEqual(actual, expected)

    def test_18_neutral_block_is_exact_projection_of_full_matrix(self) -> None:
        g10, gx = 0.73, 0.19
        full = theorem.canonical_mass_matrix(g10=g10, g_x=gx)
        basis = np.zeros((46, 3))
        for label in ((0, 1), (2, 3), (4, 5), (6, 7)):
            basis[theorem.SO10_LABELS.index(label), 0] = 0.5
        basis[theorem.SO10_LABELS.index((8, 9)), 1] = 1
        basis[45, 2] = 1
        np.testing.assert_allclose(basis.T @ full @ basis, theorem.neutral_mass_block(g10, gx), atol=2e-15, rtol=0)
        np.testing.assert_allclose(basis.T @ basis, np.eye(3), atol=0, rtol=0)

    def test_19_neutral_cubic_and_sylvester_minors_are_exact(self) -> None:
        a, b = sp.symbols("a b", positive=True)
        lam = sp.Symbol("lambda")
        root2 = sp.sqrt(2)
        block = sp.Matrix(
            [
                [sp.Rational(2, 25) * a, sp.Rational(1, 25) * a, -sp.Rational(2, 25) * root2 * sp.sqrt(a * b)],
                [sp.Rational(1, 25) * a, sp.Rational(51, 50) * a, -sp.Rational(51, 25) * root2 * sp.sqrt(a * b)],
                [-sp.Rational(2, 25) * root2 * sp.sqrt(a * b), -sp.Rational(51, 25) * root2 * sp.sqrt(a * b), sp.Rational(1489, 5) * b],
            ]
        )
        self.assertEqual(
            [sp.factor(block[:size, :size].det()) for size in range(1, 4)],
            [sp.Rational(2, 25) * a, sp.Rational(2, 25) * a**2, sp.Rational(14482, 625) * a**2 * b],
        )
        expected = (
            lam**3
            - (sp.Rational(11, 10) * a + sp.Rational(1489, 5) * b) * lam**2
            + (sp.Rational(2, 25) * a**2 + sp.Rational(79811, 250) * a * b) * lam
            - sp.Rational(14482, 625) * a**2 * b
        )
        self.assertEqual(sp.expand(block.charpoly(lam).as_expr() - expected), 0)

    def test_20_neutral_roots_are_positive_and_satisfy_cubic(self) -> None:
        for g10, gx in ((1.0, 1.0), (0.72, 0.3), (0.1, 2.0)):
            roots = theorem.neutral_mass_factors(g10, gx)
            self.assertEqual(len(roots), 3)
            self.assertTrue(all(value > 0 for value in roots))
            a, b = g10**2, gx**2
            for value in roots:
                residual = (
                    value**3
                    - (11 * a / 10 + 1489 * b / 5) * value**2
                    + (2 * a**2 / 25 + 79811 * a * b / 250) * value
                    - 14482 * a**2 * b / 625
                )
                scale = max(value**3, a**2 * b, 1.0)
                self.assertLess(abs(residual), 2e-10 * scale)

    def test_21_compiled_spectrum_matches_full_46_eigenvalues(self) -> None:
        for g10, gx, scale in ((1.0, 0.4, 1.0), (0.63, 1.2, 7.0)):
            expected = [0.0] * 9
            for row in theorem.MASSIVE_MULTIPLETS:
                expected.extend([row.mass_squared(g10, scale)] * row.real_vector_dimension)
            expected.extend(value * scale**2 for value in theorem.neutral_mass_factors(g10, gx))
            observed = np.linalg.eigvalsh(theorem.canonical_mass_matrix(g10=g10, g_x=gx, vev_scale=scale))
            np.testing.assert_allclose(sorted(expected), observed, rtol=2e-11, atol=max(observed[-1], 1) * 2e-13)

    def test_22_massive_multiplet_census_is_34_plus_3(self) -> None:
        self.assertEqual(sum(row.real_vector_dimension for row in theorem.MASSIVE_MULTIPLETS), 34)
        self.assertEqual(sum(row.complex_multiplets for row in theorem.MASSIVE_MULTIPLETS), 7)
        spectrum = theorem.mass_spectrum(g10=0.7, g_x=0.2, vev_scale=3)
        self.assertEqual(len(spectrum), 10)
        self.assertEqual(sum(row["real_vector_dimension"] for row in spectrum), 37)
        self.assertTrue(all(row["mass_squared"] > 0 for row in spectrum))

    def test_23_threshold_indices_follow_color_and_charge(self) -> None:
        for row in theorem.MASSIVE_MULTIPLETS:
            expected_su3 = Fraction(1, 2) if row.su3 == "3" else Fraction(0)
            expected_qed = (3 if row.su3 == "3" else 1) * row.abs_q**2
            self.assertEqual(row.su3_dynkin, expected_su3)
            self.assertEqual(row.qed_index, expected_qed)
        self.assertEqual(sum(row.su3_dynkin for row in theorem.MASSIVE_MULTIPLETS), Fraction(5, 2))
        self.assertEqual(sum(row.qed_index for row in theorem.MASSIVE_MULTIPLETS), Fraction(32, 3))

    def test_24_threshold_log_interface_is_scale_covariant(self) -> None:
        first = theorem.one_loop_vector_log_inputs(g10=0.7, g_x=0.3, vev_scale=11, matching_scale=2)
        second = theorem.one_loop_vector_log_inputs(g10=0.7, g_x=0.3, vev_scale=11, matching_scale=5)
        shift = math.log(5 / 2)
        self.assertAlmostEqual(
            second["index_weighted_logs"]["SU3"] - first["index_weighted_logs"]["SU3"],
            -2.5 * shift,
            places=13,
        )
        self.assertAlmostEqual(
            second["index_weighted_logs"]["QED"] - first["index_weighted_logs"]["QED"],
            -(32 / 3) * shift,
            places=13,
        )

    def test_25_threshold_interface_does_not_invent_loop_matching(self) -> None:
        result = theorem.one_loop_vector_log_inputs(g10=0.7, g_x=0.3, vev_scale=11, matching_scale=2)
        self.assertEqual(result["unbroken_group"], "SU(3)_C x U(1)_em")
        self.assertFalse(result["combined_vector_Goldstone_ghost_log_coefficient_applied"])
        self.assertFalse(result["finite_scheme_constants_applied"])
        self.assertFalse(result["is_complete_one_loop_matching"])

    def test_26_report_reproduces_disk_json(self) -> None:
        disk = json.loads(theorem.OUT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(disk, self.report)
        self.assertEqual(theorem.build_report(), self.report)

    def test_27_all_positive_checks_pass_and_open_claims_stay_false(self) -> None:
        deliberately_open = {
            "physical_scale_and_coupling_boundaries_fixed",
            "pole_masses_fixed",
            "vector_Goldstone_ghost_matching_closed",
            "finite_scheme_constants_closed",
            "SM_symmetric_pre_EW_threshold_closed",
            "physical_G6_closed",
            "physical_G7_closed",
        }
        for name, value in self.report["checks"].items():
            self.assertEqual(value, name not in deliberately_open, name)

    def test_28_g6_g7_and_uncomputed_physics_fail_closed(self) -> None:
        scope = self.report["scope"]
        self.assertTrue(scope["exact_parameterized_46x46_tree_mass_matrix"])
        self.assertTrue(scope["exact_rank_kernel_and_Goldstone_image"])
        self.assertFalse(scope["absolute_physical_masses"])
        self.assertFalse(scope["pole_masses"])
        self.assertFalse(scope["complete_one_loop_vector_threshold_matching"])
        self.assertFalse(scope["complete_physical_scalar_spectrum"])
        self.assertFalse(scope["physical_G6"])
        self.assertFalse(scope["physical_G7"])
        self.assertIn("FULL_G6_G7_OPEN", self.report["status"])


if __name__ == "__main__":
    unittest.main()
