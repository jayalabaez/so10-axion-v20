#!/usr/bin/env python3
"""Fast fail-closed tests for the corrected v21 publication bundle."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import numpy as np
from scipy import sparse

import exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_primal_v21 as primal
import freeze_exact_gauged_u1x_g3_rank1_su4_corrected_publication_v21 as freezer
import verify_exact_gauged_u1x_g3_rank1_su4_corrected_fixed_endpoint_theorem_v21 as theorem


HERE = Path(__file__).resolve().parent
EXPECTED_REPORT_RAW_SHA256 = {
    theorem.SOURCE_REPORT.name: theorem.EXPECTED_REPORT_RAW_SHA256[
        theorem.SOURCE_REPORT.name
    ],
    theorem.EXACT_VERIFY_REPORT.name: theorem.EXPECTED_REPORT_RAW_SHA256[
        theorem.EXACT_VERIFY_REPORT.name
    ],
    theorem.LIVE_REPORT.name: theorem.EXPECTED_REPORT_RAW_SHA256[
        theorem.LIVE_REPORT.name
    ],
    theorem.OVERFLOW_REPORT.name: theorem.EXPECTED_REPORT_RAW_SHA256[
        theorem.OVERFLOW_REPORT.name
    ],
}


class CorrectedPublicationV21Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = primal.load_certificate()
        cls.matrix, cls.map_denominator, cls.target, cls.target_denominator = (
            primal.load_system()
        )
        cls.source = theorem._load_pinned(theorem.SOURCE_REPORT)
        cls.exact = theorem._load_pinned(theorem.EXACT_VERIFY_REPORT)
        cls.live = theorem._load_pinned(theorem.LIVE_REPORT)
        cls.overflow = theorem._load_pinned(theorem.OVERFLOW_REPORT)

    def test_corrected_canonical_pins(self) -> None:
        self.assertEqual(self.matrix.shape, (6_585, 19_594))
        self.assertEqual(self.matrix.nnz, 138_550)
        self.assertEqual(self.map_denominator, 256)
        self.assertEqual(self.target_denominator, 576_000)
        self.assertEqual(primal.sparse_sha256(self.matrix), primal.EXPECTED_MAP_NUMERATOR_CSR_SHA256)
        self.assertEqual(primal.int64_array_sha256(self.target), primal.EXPECTED_TARGET_NUMERATOR_SHA256)
        self.assertEqual(
            self.certificate["exact_primal_coordinates_sha256"],
            primal.EXPECTED_COORDINATE_SHA256,
        )
        self.assertEqual(
            self.certificate["exact_verification"]["all_exact_LDL_pivots_sha256"],
            primal.EXPECTED_LDL_PIVOT_SHA256,
        )

    def test_exact_equalities_and_strict_blocks_are_pinned(self) -> None:
        theorem._validate_exact_verify(self.exact)
        self.assertEqual(self.exact["exact_coefficient_equalities_verified"], 6_585)
        self.assertEqual(self.exact["strictly_positive_Gram_blocks_verified"], 22)
        self.assertEqual(
            sum(
                row["positive_leading_principal_minor_count"]
                for row in self.exact["block_diagnostics"]
            ),
            824,
        )

    def test_complete_carrier_map_and_ordered_spectral_rhs(self) -> None:
        theorem._validate_source(self.source)
        self.assertEqual(
            self.source["carrier_exhaustion"]["complete_real_carrier_dimension"],
            211 * 212 // 2,
        )
        self.assertEqual(self.source["map"]["full_column_reconstruction_count"], 19_594)
        self.assertEqual(
            self.source["physical_RHS"]["row_by_row_direct_evaluator_mismatch_count"],
            0,
        )
        self.assertEqual(
            self.source["physical_RHS"]["first_quartic_value_correct"],
            "27776/1125",
        )
        self.assertEqual(
            self.source["physical_RHS"]["first_quartic_value_rejected_raw_schur"],
            "129568/3375",
        )
        self.assertFalse(
            self.source["generation_boundary"]["v20_physical_target_payload_read"]
        )

    def test_live_SU3_bridge_and_grade_zero_shift(self) -> None:
        theorem._validate_live(self.live)
        self.assertEqual(
            self.live["raw_live_anchor_A_by_grade"],
            [
                "6/5",
                "-3183/10000",
                "-753023067/400000000",
                "0",
                "3063315748321207/3000000000000000",
            ],
        )
        self.assertEqual(self.live["reserve_subtracted_from_grade_zero"], "3/200")
        self.assertTrue(self.live["reserve_changes_only_grade_zero_exact"])
        self.assertEqual(
            self.live["target_and_carrier_total"],
            "15742745821207/3000000000000000",
        )

    def test_theorem_bridge_and_scope(self) -> None:
        report = theorem.build_report()
        self.assertTrue(report["theorem"]["complete_polynomial_identity_for_all_real_t_Phi"])
        self.assertTrue(report["theorem"]["strict_positive_off_homogeneous_origin"])
        self.assertEqual(report["theorem"]["p_zero_set_at_t_equals_one"], "empty")
        boundary = report["claim_boundary"]
        self.assertTrue(boundary["fixed_H_h_minus"])
        self.assertTrue(boundary["fixed_Sigma_q_over_4"])
        self.assertTrue(boundary["arbitrary_real_Phi_at_this_fixed_endpoint"])
        for false_claim in (
            "global_Sigma_proved",
            "general_H_proved",
            "full_H_proved",
            "full_Hessian_proved",
            "G3_closed",
        ):
            self.assertIs(boundary[false_claim], False)

    def test_updated_echo_mutations_fail_closed(self) -> None:
        mutations = []
        mutated = copy.deepcopy(self.certificate)
        mutated["schema"] = mutated["schema"] + "-updated"
        mutations.append(mutated)
        mutated = copy.deepcopy(self.certificate)
        mutated["corrected_system"]["map_numerator_csr_sha256"] = "0" * 64
        mutations.append(mutated)
        mutated = copy.deepcopy(self.certificate)
        mutated["corrected_system"]["target_numerator_int64_sha256"] = "0" * 64
        mutations.append(mutated)
        mutated = copy.deepcopy(self.certificate)
        mutated["exact_primal_coordinates_fraction_pairs"][0] = ["2", "1"]
        mutated["exact_primal_coordinates_sha256"] = primal.canonical_sha256(
            mutated["exact_primal_coordinates_fraction_pairs"]
        )
        mutations.append(mutated)
        mutated = copy.deepcopy(self.certificate)
        mutated["exact_primal_coordinates_sha256"] = "0" * 64
        mutations.append(mutated)
        mutated = copy.deepcopy(self.certificate)
        mutated["exact_verification"]["all_exact_LDL_pivots_sha256"] = "0" * 64
        mutations.append(mutated)
        mutated = copy.deepcopy(self.certificate)
        mutated["exact_verification"]["all_6585_coefficient_equalities_hold"] = False
        mutations.append(mutated)
        for payload in mutations:
            with self.subTest(payload=payload):
                with self.assertRaises(ArithmeticError):
                    primal.validate_certificate(payload)

        mutated_source = copy.deepcopy(self.source)
        mutated_source["carrier_exhaustion"]["carrier_transform_square_shape"] = [
            22_365,
            22_365,
        ]
        mutated_source["carrier_exhaustion"]["complete_real_carrier_dimension"] = 22_365
        with self.assertRaises(ArithmeticError):
            theorem._validate_source(mutated_source)

    def test_updated_npz_payload_and_echo_mutations_fail_closed(self) -> None:
        with np.load(primal.SYSTEM, allow_pickle=False) as archive:
            canonical = {name: np.asarray(archive[name]).copy() for name in archive.files}
        original_system = primal.SYSTEM
        original_raw_pin = primal.EXPECTED_SYSTEM_RAW_SHA256
        try:
            for member, index in (("map_data", 0), ("target_numerator", 0)):
                with self.subTest(member=member):
                    payload = {name: value.copy() for name, value in canonical.items()}
                    payload[member][index] += 1
                    with tempfile.NamedTemporaryFile(
                        suffix=".npz", dir=HERE, delete=False
                    ) as handle:
                        candidate = Path(handle.name)
                    try:
                        np.savez_compressed(candidate, **payload)
                        refreshed_raw = primal.raw_sha256(candidate)
                        primal.SYSTEM = candidate
                        primal.EXPECTED_SYSTEM_RAW_SHA256 = refreshed_raw
                        with self.assertRaises(ArithmeticError):
                            primal.load_system()

                        refreshed_certificate = copy.deepcopy(self.certificate)
                        refreshed_certificate["corrected_system"][
                            "numerical_system_raw_sha256"
                        ] = refreshed_raw
                        if member == "map_data":
                            mutated_matrix = sparse.csr_matrix(
                                (
                                    payload["map_data"],
                                    payload["map_indices"],
                                    payload["map_indptr"],
                                ),
                                shape=tuple(
                                    int(value) for value in payload["map_shape"]
                                ),
                            )
                            refreshed_certificate["corrected_system"][
                                "map_numerator_csr_sha256"
                            ] = primal.sparse_sha256(mutated_matrix)
                        else:
                            refreshed_certificate["corrected_system"][
                                "target_numerator_int64_sha256"
                            ] = primal.int64_array_sha256(
                                payload["target_numerator"]
                            )
                        with self.assertRaises(ArithmeticError):
                            primal.validate_certificate(refreshed_certificate)
                    finally:
                        primal.SYSTEM = original_system
                        primal.EXPECTED_SYSTEM_RAW_SHA256 = original_raw_pin
                        candidate.unlink(missing_ok=True)
        finally:
            primal.SYSTEM = original_system
            primal.EXPECTED_SYSTEM_RAW_SHA256 = original_raw_pin

    def test_loaders_return_unshared_mutable_values(self) -> None:
        changed = primal.load_certificate()
        changed["corrected_system"]["map_shape"][0] = 1
        fresh = primal.load_certificate()
        self.assertEqual(fresh["corrected_system"]["map_shape"], [6_585, 19_594])
        matrix, _, target, _ = primal.load_system()
        matrix.data[0] += 1
        target[0] += 1
        fresh_matrix, _, fresh_target, _ = primal.load_system()
        self.assertEqual(
            primal.sparse_sha256(fresh_matrix), primal.EXPECTED_MAP_NUMERATOR_CSR_SHA256
        )
        self.assertEqual(
            primal.int64_array_sha256(fresh_target), primal.EXPECTED_TARGET_NUMERATOR_SHA256
        )

    def test_python_integer_overflow_regressions(self) -> None:
        # Import the explicit generation-time source only for its arithmetic guards.
        import exact_gauged_u1x_g3_rank1_su4_corrected_physical_rhs_v21 as rhs

        coarse = rhs._python_dot({0: 1 << 67}, {0: 1})
        self.assertIs(type(coarse), int)
        self.assertEqual(coarse.bit_length(), 68)
        safety = {
            "maximum_preoperation_scale_bound": 0,
            "guarded_sparse_scale_count": 0,
        }
        unsafe = sparse.csr_matrix(
            (np.asarray([rhs.INT64_MAX], dtype=np.int64), ([0], [0])),
            shape=(1, 1),
        )
        with self.assertRaisesRegex(ArithmeticError, "before unsafe int64"):
            rhs._guarded_scale(unsafe, 2, safety)
        live_safety = self.live["exact_arithmetic_safety"]
        self.assertTrue(live_safety["physical_path_exceeds_signed_int64"])
        self.assertFalse(live_safety["fixed_width_physical_contraction_used"])
        theorem._validate_overflow(self.overflow)
        self.assertEqual(
            self.overflow["coarse_SU3_witness"][
                "raw_spectral_contraction_numerator"
            ],
            "225852143492225949696",
        )
        self.assertEqual(
            self.overflow["coarse_SU3_witness"][
                "raw_spectral_contraction_abs_bit_length"
            ],
            68,
        )
        self.assertEqual(
            self.overflow["sharp_SU3_witness"][
                "raw_spectral_contraction_numerator"
            ],
            "225742872026058646911271963582464",
        )
        self.assertEqual(
            self.overflow["sharp_SU3_witness"][
                "raw_spectral_contraction_abs_bit_length"
            ],
            108,
        )

    def test_every_noncanonical_map_or_target_echo_is_rejected(self) -> None:
        for key in (
            "map_numerator_csr_sha256",
            "target_numerator_int64_sha256",
        ):
            mutated = copy.deepcopy(self.certificate)
            mutated["corrected_system"][key] = "0" * 64
            with self.assertRaises(ArithmeticError):
                primal.validate_certificate(mutated)

    def test_runtime_is_relocatable_and_ignores_shadow_paths(self) -> None:
        runtime_files = (
            primal.__file__,
            primal.CERTIFICATE,
            primal.SYSTEM,
            theorem.__file__,
            theorem.SOURCE_REPORT,
            theorem.EXACT_VERIFY_REPORT,
            theorem.LIVE_REPORT,
            theorem.OVERFLOW_REPORT,
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            relocated = root / "relocated"
            shadow = root / "shadow"
            relocated.mkdir()
            shadow.mkdir()
            for raw in runtime_files:
                shutil.copy2(Path(raw), relocated / Path(raw).name)
            (shadow / Path(primal.__file__).name).write_text(
                "raise RuntimeError('shadow import used')\n", encoding="utf-8"
            )
            environment = os.environ.copy()
            environment["PYTHONPATH"] = str(shadow)
            environment["SO10_PUBLISHED_API_ROOT"] = str(shadow)
            command = [
                sys.executable,
                "-B",
                "-I",
                str(relocated / Path(theorem.__file__).name),
            ]
            completed = subprocess.run(
                command,
                cwd=shadow,
                env=environment,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn(theorem.STATUS, completed.stdout)
            self.assertNotIn(str(HERE), completed.stdout)

    def test_byte_inventory_manifest(self) -> None:
        manifest = freezer.check_manifest()
        self.assertEqual(manifest["inventory_count"], len(freezer.EXPECTED_FILES))
        self.assertEqual(set(manifest["inventory"]), set(freezer.EXPECTED_FILES))
        self.assertEqual(manifest["logical_pins"], freezer.LOGICAL_PINS)


if __name__ == "__main__":
    unittest.main()
