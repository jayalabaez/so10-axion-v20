#!/usr/bin/env python3
"""Adversarial tests for exact normalized SO(10) Yukawa CGCs."""

from __future__ import annotations

import hashlib
import itertools
import json
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

import exact_normalized_so10_yukawa_cgcs_v20 as theorem


ROOT = Path(__file__).resolve().parent
EXPECTED_SOURCE_PORTABLE_SHA256 = "432faa3fdf5adebf25015f7f2fda7f040d89d86bce31f6c85b4cc56e37eb14df"
EXPECTED_CORE_SHA256 = "c83671cff9c33043b5c7cad19e2f2a744cb5f861a8ea71937c5f3a7308dfffb7"
EXPECTED_REPORT_PORTABLE_SHA256 = {
    "json": "cac9de5d918a38962fc5ad1c8c3b6351e49051f64a5c8b7e005a6859dd1baf1b",
    "md": "5acbb5eb78451b8f37f1d8b990962a7ad4c39fe1974cb4720cf2131a85c14112",
}


def _sha256(path: Path, *, portable: bool = False) -> str:
    data = path.read_bytes()
    if portable:
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


class ExactNormalizedSO10YukawaCGCTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = theorem.build_report()
        cls.ten = theorem.cgc_10()
        cls.sigma = theorem.cgc_126bar()
        cls.singlet = theorem.cgc_singlet_dual_basis()

    def test_01_frozen_source_and_report_hashes(self) -> None:
        self.assertEqual(
            _sha256(Path(theorem.__file__), portable=True),
            EXPECTED_SOURCE_PORTABLE_SHA256,
        )
        self.assertEqual(
            _sha256(theorem.OUT_JSON, portable=True), EXPECTED_REPORT_PORTABLE_SHA256["json"]
        )
        self.assertEqual(
            _sha256(theorem.OUT_MD, portable=True), EXPECTED_REPORT_PORTABLE_SHA256["md"]
        )
        self.assertEqual(self.report["core_sha256"], EXPECTED_CORE_SHA256)

    def test_02_all_dependencies_are_source_bound(self) -> None:
        observed = theorem.source_guard()
        self.assertEqual(set(observed), set(theorem.DEPENDENCIES))
        for name, (_, expected, mode) in theorem.DEPENDENCIES.items():
            self.assertEqual(observed[name]["sha256"], expected)
            self.assertEqual(observed[name]["mode"], mode)

    def test_03_dependency_drift_fails_closed(self) -> None:
        original = theorem._digest

        def corrupt(path: Path, mode: str = "raw") -> str:
            if path == theorem.CLIFFORD_SOURCE:
                return "0" * 64
            return original(path, mode)

        with patch.object(theorem, "_digest", side_effect=corrupt):
            with self.assertRaisesRegex(ArithmeticError, "dependency drifted"):
                theorem.source_guard()

    def test_04_authoritative_304_weyl_inventory_offsets(self) -> None:
        inventory = theorem.canonical_304_inventory()
        expected = [
            ("F", 3, "16", 0, 48),
            ("P", 1, "16", 48, 64),
            ("R", 1, "16", 64, 80),
            ("SpecS", 5, "16", 80, 160),
            ("SpecB", 5, "16bar", 160, 240),
            ("Q", 1, "16", 240, 256),
            ("Pbar", 1, "16bar", 256, 272),
            ("Qbar", 1, "16bar", 272, 288),
            ("Rbar", 1, "16bar", 288, 304),
        ]
        self.assertEqual(
            [(row.name, row.generations, row.representation, row.start, row.stop) for row in inventory],
            expected,
        )
        self.assertEqual(sum(row.generations for row in inventory), 19)

    def test_05_all_ten_model_yukawas_are_found_exactly(self) -> None:
        self.assertIsNone(theorem.verify_declared_interactions())
        self.assertEqual(tuple(theorem.INTERACTION_SPECS), theorem.EXPECTED_INTERACTIONS)
        self.assertEqual(
            set(theorem.EXPECTED_INTERACTIONS),
            {row["symbol"] for row in self.report["declared_yukawa_closure"]},
        )

    def test_05b_chirality_labels_match_standard_ps_spinor_weights(self) -> None:
        self.assertEqual(
            theorem.spinor_standard_model_weight_multiset(-1),
            theorem.EXPECTED_MODEL_16_PS_CARTAN_WEIGHTS,
        )
        self.assertEqual(
            theorem.spinor_standard_model_weight_multiset(+1),
            theorem.EXPECTED_MODEL_16BAR_PS_CARTAN_WEIGHTS,
        )

    def test_06_vector_cgcs_are_exact_symmetric_gaussian_integers(self) -> None:
        numerator = self.ten.numerator
        self.assertEqual(numerator.shape, (10, 16, 16))
        self.assertTrue(all(np.array_equal(matrix, matrix.T) for matrix in numerator))
        self.assertEqual(set(np.abs(numerator.flat)), {0, 1})
        self.assertEqual(np.count_nonzero(numerator), 160)

    def test_07_vector_normalization_is_exact(self) -> None:
        self.assertEqual(self.ten.denominator, 4)
        self.assertTrue(self.ten.normalized_gram_is_identity())
        np.testing.assert_array_equal(self.ten.gram_numerator(), 16 * np.eye(10))

    def test_08_physical_126bar_basis_has_canonical_kinetic_norm(self) -> None:
        basis = theorem.canonical_126_basis()
        self.assertEqual(len(basis), 126)
        for state in basis:
            self.assertEqual(len(state), 2)
            self.assertEqual(theorem.five_forms.sigma_kinetic_inner(state, state), 1)
            star = theorem.five_forms.hodge_star(state)
            for indices in set(star).union(state):
                self.assertEqual(star.get(indices, 0), -1j * state.get(indices, 0))

    def test_09_126bar_cgcs_are_exact_symmetric_gaussian_integers(self) -> None:
        numerator = self.sigma.numerator
        self.assertEqual(numerator.shape, (126, 16, 16))
        self.assertTrue(all(np.array_equal(matrix, matrix.T) for matrix in numerator))
        self.assertEqual(set(np.abs(numerator.flat)), {0, 2})
        self.assertEqual(np.count_nonzero(numerator), 126 * 16)

    def test_10_126bar_normalization_includes_physical_kinetic_factor(self) -> None:
        self.assertEqual(self.sigma.denominator, 8)
        self.assertTrue(self.sigma.normalized_gram_is_identity())
        np.testing.assert_array_equal(self.sigma.gram_numerator(), 64 * np.eye(126))
        np.testing.assert_array_equal(
            self.sigma.numerator, theorem.physical_126_shortcut_numerators()
        )

    def test_11_wrong_chirality_is_an_exact_zero_obstruction(self) -> None:
        wrong = theorem.physical_126_numerators(+1)
        self.assertEqual(wrong.shape, (126, 16, 16))
        self.assertFalse(np.any(wrong))
        self.assertEqual(np.linalg.matrix_rank(wrong.reshape(126, -1)), 0)
        self.assertEqual(np.linalg.matrix_rank(self.sigma.numerator.reshape(126, -1)), 126)

    def test_12_ten_and_126bar_are_orthogonal(self) -> None:
        overlap = np.einsum(
            "aij,rij->ar", self.ten.numerator.conjugate(), self.sigma.numerator
        )
        self.assertFalse(np.any(overlap))

    def test_13_ten_plus_126bar_exactly_complete_symmetric_square(self) -> None:
        projector64 = 4 * np.einsum(
            "aij,akl->ijkl",
            self.ten.numerator,
            self.ten.numerator.conjugate(),
        )
        projector64 += np.einsum(
            "rij,rkl->ijkl",
            self.sigma.numerator,
            self.sigma.numerator.conjugate(),
        )
        expected = np.zeros_like(projector64)
        for i, j, k, ell in itertools.product(range(16), repeat=4):
            expected[i, j, k, ell] = 32 * (
                (i == k and j == ell) + (i == ell and j == k)
            )
        np.testing.assert_array_equal(projector64, expected)

    def test_14_all_45_generators_have_zero_exact_covariance_residual(self) -> None:
        self.assertEqual(
            theorem.covariance_residuals(), {"10": 0, "126bar": 0, "singlet": 0}
        )

    def test_15_singlet_is_exact_identity_in_c_dual_basis(self) -> None:
        raw = theorem.singlet_clifford_numerator()
        self.assertEqual(np.count_nonzero(raw), 16)
        np.testing.assert_array_equal(raw @ raw.conjugate().T, np.eye(16))
        np.testing.assert_array_equal(self.singlet.numerator, np.eye(16)[None, :, :])
        self.assertEqual(self.singlet.denominator, 4)
        self.assertTrue(self.singlet.normalized_gram_is_identity())

    def test_16_sparse_tensor_reconstruction_is_lossless(self) -> None:
        for tensor in (self.ten, self.sigma, self.singlet):
            reconstructed = np.zeros_like(tensor.numerator)
            for scalar, left, right, real, imag, denominator in tensor.sparse_entries():
                self.assertEqual(denominator, tensor.denominator)
                reconstructed[scalar, left, right] = real + 1j * imag
            np.testing.assert_array_equal(reconstructed, tensor.numerator)

    def test_17_all_embedded_support_stays_inside_304(self) -> None:
        for symbol in theorem.EXPECTED_INTERACTIONS:
            rows = theorem.embedded_sparse_support(symbol)
            self.assertTrue(rows, symbol)
            self.assertTrue(all(0 <= row[1] < 304 and 0 <= row[2] < 304 for row in rows))

    def test_18_embedded_sparse_counts_include_symbolic_flavor_pairs(self) -> None:
        base = {"10": 160, "126bar": 2016, "singlet": 16}
        blocks = {row.name: row for row in theorem.canonical_304_inventory()}
        for symbol, spec in theorem.INTERACTION_SPECS.items():
            expected = (
                base[spec["channel"]]
                * blocks[spec["left"]].generations
                * blocks[spec["right"]].generations
            )
            self.assertEqual(len(theorem.embedded_sparse_support(symbol)), expected)

    def test_19_y10_embedding_hits_exact_f_block_only(self) -> None:
        rows = theorem.embedded_sparse_support("Y10")
        self.assertEqual(len(rows), 9 * 160)
        self.assertEqual((min(row[1] for row in rows), max(row[1] for row in rows)), (0, 47))
        self.assertEqual((min(row[2] for row in rows), max(row[2] for row in rows)), (0, 47))

    def test_20_y126_embedding_hits_exact_f_block_only(self) -> None:
        rows = theorem.embedded_sparse_support("Y126")
        self.assertEqual(len(rows), 9 * 2016)
        self.assertEqual((min(row[1] for row in rows), max(row[1] for row in rows)), (0, 47))
        self.assertEqual((min(row[2] for row in rows), max(row[2] for row in rows)), (0, 47))

    def test_21_spectator_singlet_embedding_has_25_flavor_pairs(self) -> None:
        rows = theorem.embedded_sparse_support("ys")
        self.assertEqual(len(rows), 25 * 16)
        self.assertEqual((min(row[1] for row in rows), max(row[1] for row in rows)), (80, 159))
        self.assertEqual((min(row[2] for row in rows), max(row[2] for row in rows)), (160, 239))

    def test_22_invalid_chirality_channel_and_generation_fail(self) -> None:
        with self.assertRaises(ValueError):
            theorem.chiral_indices(0)
        with self.assertRaises(KeyError):
            theorem.cgc_for_channel("120")
        with self.assertRaises(IndexError):
            theorem.canonical_304_inventory()[0].copy_start(3)

    def test_23_report_is_machine_readable_and_reproducible(self) -> None:
        disk = json.loads(theorem.OUT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(disk, self.report)
        self.assertEqual(theorem.build_report(), self.report)
        self.assertEqual(len(self.report["declared_yukawa_closure"]), 10)

    def test_24_positive_representation_claims_close(self) -> None:
        checks = self.report["checks"]
        positives = {
            key: value
            for key, value in checks.items()
            if key not in {
                "flavor_boundary_values_closed",
                "sarah_symbol_normalization_closed",
                "full_yukawa_rge_closed",
                "full_physical_G7_closed",
            }
        }
        self.assertTrue(all(positives.values()), positives)

    def test_25_g7_and_uncomputed_physics_remain_fail_closed(self) -> None:
        scope = self.report["scope"]
        self.assertTrue(scope["normalized_representation_CGCs_for_all_declared_Yukawas"])
        self.assertTrue(scope["canonical_304_Weyl_sparse_embedding"])
        self.assertFalse(scope["flavor_tensor_values_or_textures"])
        self.assertFalse(scope["sarah_implicit_contraction_normalization"])
        self.assertFalse(scope["one_or_two_loop_Yukawa_betas"])
        self.assertFalse(scope["threshold_matching_and_running"])
        self.assertFalse(scope["full_yukawa_sector"])
        self.assertFalse(scope["mathematical_G7"])
        self.assertFalse(scope["release_G7"])
        self.assertIn("FULL_G7_OPEN", self.report["status"])

    def test_26_report_does_not_embed_dense_tensor_payloads(self) -> None:
        serialized = json.dumps(self.report)
        self.assertNotIn("sparse_entries", serialized)
        self.assertLess(theorem.OUT_JSON.stat().st_size, 100_000)
        for row in self.report["normalized_tensors"].values():
            self.assertRegex(row["numerator_sha256_i16_real_imag_C_order"], r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
