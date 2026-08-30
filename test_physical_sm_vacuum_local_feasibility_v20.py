#!/usr/bin/env python3
"""Adversarial tests for the physical Standard-Model vacuum rebuild."""
from __future__ import annotations

import copy
import contextlib
import hashlib
import io
import json
import math
import os
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from unittest import mock

import numpy as np

import physical_sm_vacuum_local_feasibility_v20 as theorem


EXPECTED_CORE_SHA256 = "01f565d3382756bc467bfaa99d187188bc1bfc4060f2c3a472650f5e57537e80"
EXPECTED_SOURCE_SHA256 = "629ea8c45f101f82b6b4e963fd1fb19dcc5735fe52a1d8efb1fb0812dbaa565c"
EXPECTED_JSON_SHA256 = "ac575067550472afeae1d87503c04a47bf27386223a4417cf7c2341ad75af315"
EXPECTED_MD_SHA256 = "d312fb960e7a458fadf38977573315a6d0a5eee37437c49c149589abd36416c3"

EXPECTED_TRANSVERSE_SECTORS = {
    (0, 0): 18,
    (36, 0): 56,
    (16, 1): 72,
    (40, 1): 48,
    (16, 4): 54,
    (40, 4): 36,
    (0, 9): 16,
    (36, 9): 64,
    (16, 16): 18,
    (40, 16): 36,
    (16, 25): 24,
    (0, 36): 6,
}


def _flatten_live_leaves(value, prefix=""):
    leaves = {}
    if isinstance(value, dict):
        for key in sorted(value):
            path = f"{prefix}.{key}" if prefix else str(key)
            leaves.update(_flatten_live_leaves(value[key], path))
        return leaves
    if isinstance(value, list):
        if prefix == "physical_sector_decomposition.sectors":
            for row in value:
                identity = (
                    f"12C2_SU3={int(row['12C2_SU3'])},"
                    f"Q3_squared={int(row['Q3_squared'])}"
                )
                leaves.update(
                    _flatten_live_leaves(row, f"{prefix}[{identity}]")
                )
            return leaves
        for index, item in enumerate(value):
            leaves.update(_flatten_live_leaves(item, f"{prefix}[{index}]"))
        return leaves
    leaves[prefix] = value
    return leaves


class PhysicalSMVacuumLocalFeasibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(theorem.OUT_JSON.read_text(encoding="utf-8"))

    def test_rational_target_is_exactly_the_physical_embedding(self) -> None:
        lattice = theorem.integer_target_vector()
        target = theorem.target_certificate()
        self.assertEqual(lattice.shape, (486,))
        self.assertTrue(np.issubdtype(lattice.dtype, np.integer))
        self.assertEqual(int(lattice @ lattice), 1632)
        self.assertEqual(target["q_norm_squared"], "102/25")
        self.assertEqual(target["support_size"], 21)
        self.assertEqual(target["field_block_q_norm_squared"]["Phi210"], "1")
        self.assertEqual(target["field_block_q_norm_squared"]["H10"], "2")
        self.assertEqual(target["field_block_q_norm_squared"]["Sigma126bar"], "1/25")
        self.assertTrue(target["standard_Y6_annihilates_pre_EW_fields"])
        self.assertTrue(target["standard_Q3_annihilates_full_target"])
        self.assertFalse(target["bare_G89_annihilates_full_target"])
        np.testing.assert_array_equal(
            theorem.chart.pack(theorem.target_state()), lattice / 20
        )

    def test_exact_integer_orbit_certificate(self) -> None:
        certificate = theorem.exact_symmetry_certificate()
        self.assertEqual(certificate["orbits"]["SO10"]["exact_rank"], 36)
        self.assertEqual(
            certificate["orbits"]["SO10_x_U1X"]["exact_rank"], 37
        )
        self.assertEqual(
            certificate["orbits"]["SO10_x_U1X_x_PQ"]["exact_rank"], 38
        )
        for orbit in certificate["orbits"].values():
            self.assertTrue(orbit["minor_is_nonzero"])
            self.assertNotEqual(int(orbit["nonzero_minor_determinant"]), 0)
        unbroken = certificate["standard_unbroken_basis"]
        self.assertEqual(unbroken["exact_rank"], 9)
        self.assertEqual(len(unbroken["pivot_rows"]), 9)
        self.assertEqual(len(unbroken["pivot_columns"]), 9)
        self.assertNotEqual(int(unbroken["nonzero_minor_determinant"]), 0)
        self.assertNotEqual(int(unbroken["Gram_determinant"]), 0)
        self.assertTrue(unbroken["independent"])
        self.assertTrue(
            certificate["standard_unbroken_basis"][
                "annihilates_target_exactly"
            ]
        )
        self.assertTrue(certificate["exact_stabilizer_is_su3C_plus_u1em"])
        self.assertTrue(certificate["all_expected_ranks_proved"])
        self.assertEqual(
            certificate["live_chart_binding"]["maximum_abs_residual"], 0.0
        )

    def test_exact_radial_eft_completion_and_rejected_boundary(self) -> None:
        for kappa in (Fraction(1, 17), Fraction(1), Fraction(31, 7)):
            result = theorem.radial_eft_bfb_certificate(kappa)
            self.assertTrue(result["nonnegative_for_all_real_fields"])
            self.assertTrue(result["target_gradient_is_zero"])
            self.assertTrue(result["target_Hessian_is_PSD"])
            self.assertEqual(result["target_Hessian_rank"], 1)
            r0 = Fraction(result["R0"])
            self.assertEqual(
                Fraction(result["target_Hessian_nonzero_eigenvalue"]),
                8 * kappa * r0 * r0,
            )
            for radius in map(Fraction, (0, 1, 4, 5, 17, 101)):
                self.assertGreaterEqual(kappa * radius * (radius - r0) ** 2, 0)
        with self.assertRaises(ValueError):
            theorem.radial_eft_bfb_certificate(Fraction(0))
        with self.assertRaises(ValueError):
            theorem.radial_eft_bfb_certificate(Fraction(-1))

    def test_exact_reconstructed_hessian_rank_certificate(self) -> None:
        rank = self.report["exact_reconstructed_Hessian_rank"]
        reconstruction = rank["reconstruction"]
        self.assertEqual(reconstruction["coefficient_field"], "Q(sqrt(2))")
        self.assertEqual(reconstruction["source_nonzero_terms_before_sum"], 30900)
        self.assertEqual(reconstruction["aggregate_nonzero_entries"], 5840)
        self.assertEqual(reconstruction["aggregate_sqrt2_nonzero_entries"], 0)
        self.assertTrue(reconstruction["aggregate_matrix_is_rational"])
        self.assertTrue(reconstruction["aggregate_matrix_is_exactly_symmetric"])
        self.assertLess(
            reconstruction["maximum_live_source_entry_reconstruction_residual"],
            3e-13,
        )
        self.assertFalse(reconstruction["denominator_bound_source_derived"])
        self.assertEqual(
            reconstruction["continued_fraction_uniqueness_radius_given_bound"],
            "1/317520000",
        )
        self.assertTrue(
            reconstruction[
                "continued_fraction_reconstruction_unique_given_bound"
            ]
        )
        self.assertGreater(
            reconstruction["uniqueness_radius_to_maximum_residual_ratio"],
            100_000,
        )
        self.assertFalse(reconstruction["source_algebra_derivation_complete"])
        self.assertTrue(rank["all_47_generator_columns_annihilated_exactly"])
        self.assertEqual(rank["annihilated_generator_column_count"], 47)
        self.assertEqual(rank["exact_symmetry_tangent_span_dimension"], 38)
        self.assertEqual(rank["rank_upper_bound_from_kernel"], 448)
        self.assertEqual(rank["exact_reconstructed_rank"], 448)
        self.assertEqual(rank["exact_reconstructed_nullity"], 38)
        self.assertTrue(rank["kernel_equals_full_symmetry_tangent_span"])
        self.assertFalse(rank["source_proof_grade"])
        self.assertEqual(len(rank["modular_lower_bound_certificates"]), 4)
        for modular in rank["modular_lower_bound_certificates"]:
            self.assertEqual(modular["sqrt2_root_check"], 2)
            self.assertEqual(modular["rank"], 448)
            self.assertEqual(len(modular["pivot_rows"]), 448)
            self.assertEqual(len(modular["pivot_columns"]), 448)
            self.assertNotEqual(modular["minor_determinant_mod_prime"], 0)
            self.assertTrue(modular["minor_is_nonzero"])

    def test_squared_stationarity_global_eft_identity(self) -> None:
        completion = self.report["squared_stationarity_global_EFT_completion"]
        self.assertTrue(completion["nonnegative_for_all_real_fields"])
        self.assertTrue(completion["bounded_from_below"])
        self.assertEqual(
            completion["renormalizable_witness_nonzero_parameter_count"], 37
        )
        self.assertTrue(
            completion[
                "renormalizable_witness_global_PQ_X_invariance_source_supported"
            ]
        )
        self.assertTrue(completion["target_is_a_global_minimum"])
        self.assertFalse(completion["global_minimum_orbit_is_unique"])
        self.assertTrue(completion["global_zero_locus_classification_open"])
        self.assertEqual(
            completion["exact_zero_locus_condition"],
            "U=0 iff Vren=-1 and grad(Vren)=0",
        )
        self.assertEqual(
            completion["target_Hessian_identity_dimensionless"],
            "H_U=2*b*Hren^T*Hren",
        )
        self.assertTrue(completion["target_Hessian_is_PSD"])
        self.assertEqual(
            completion["target_Hessian_rank_on_reconstructed_lattice"], 448
        )
        self.assertEqual(
            completion["target_Hessian_nullity_on_reconstructed_lattice"], 38
        )
        self.assertTrue(
            completion[
                "target_Hessian_kernel_equals_symmetry_tangents_on_reconstructed_lattice"
            ]
        )
        self.assertTrue(
            completion[
                "strict_local_minimum_mod_full_symmetry_on_reconstructed_lattice"
            ]
        )
        self.assertFalse(completion["source_proof_grade_application"])
        self.assertTrue(
            all(value is False for value in completion["closure_effect"].values() if isinstance(value, bool))
        )

        # Exact sign/globality stress test over a range of rational values.
        for a, b in (
            (Fraction(1), Fraction(1)),
            (Fraction(1, 19), Fraction(37, 5)),
            (Fraction(101, 3), Fraction(2, 97)),
        ):
            for value in map(Fraction, (-11, -1, 0, 3, 29)):
                for gradient in (
                    (),
                    (Fraction(0),),
                    (Fraction(-7, 3), Fraction(11, 5), Fraction(2, 13)),
                ):
                    result = theorem.squared_stationarity_eft_value(
                        value, gradient, a=a, b=b
                    )
                    self.assertGreaterEqual(result, 0)
                    self.assertEqual(
                        result == 0,
                        value == -1 and all(component == 0 for component in gradient),
                    )
        for bad_a, bad_b in (
            (Fraction(0), Fraction(1)),
            (Fraction(-1), Fraction(1)),
            (Fraction(1), Fraction(0)),
            (Fraction(1), Fraction(-1)),
        ):
            with self.assertRaises(ValueError):
                theorem.squared_stationarity_global_eft_certificate(
                    a=bad_a, b=bad_b
                )
            with self.assertRaises(ValueError):
                theorem.squared_stationarity_eft_value(
                    Fraction(-1), (), a=bad_a, b=bad_b
                )

        # Exact directional-Hessian identity for a nontrivial indefinite Hren.
        hessian = (
            (Fraction(2), Fraction(1)),
            (Fraction(1), Fraction(-3)),
        )
        b = Fraction(7, 11)
        for direction in (
            (Fraction(1), Fraction(0)),
            (Fraction(0), Fraction(1)),
            (Fraction(5, 3), Fraction(-7, 2)),
        ):
            image = tuple(
                sum(row[column] * direction[column] for column in range(2))
                for row in hessian
            )
            second_derivative_from_gradient_square = 2 * b * sum(
                value * value for value in image
            )
            h_squared_direction = tuple(
                sum(hessian[row][column] * image[row] for row in range(2))
                for column in range(2)
            )
            quadratic_form = 2 * b * sum(
                direction[index] * h_squared_direction[index]
                for index in range(2)
            )
            self.assertEqual(second_derivative_from_gradient_square, quadratic_form)

        # Signed permutations are exact orthogonal transformations; gradient
        # norms and hence U are invariant.
        gradient = (Fraction(2, 3), Fraction(-5, 7), Fraction(11, 13))
        transformed = (-gradient[2], gradient[0], -gradient[1])
        self.assertEqual(
            theorem.squared_stationarity_eft_value(Fraction(4), gradient),
            theorem.squared_stationarity_eft_value(Fraction(4), transformed),
        )

    def test_nonzero_witness_support_is_globally_pq_neutral(self) -> None:
        live = self.report["live_local_feasibility"]
        support = live["global_PQ_support"]
        self.assertEqual(support["nonzero_parameter_count"], 37)
        self.assertEqual(
            sorted(support["nonzero_parameter_ids"]),
            sorted(live["coefficients"]),
        )
        self.assertTrue(
            support["all_nonzero_parameters_are_lambda_components"]
        )
        self.assertTrue(
            support["all_nonzero_directions_are_self_conjugate"]
        )
        self.assertTrue(
            support["all_nonzero_directions_have_exact_zero_PQ_charge"]
        )
        self.assertTrue(
            support["all_nonzero_directions_have_exact_zero_X_charge"]
        )
        self.assertTrue(
            support[
                "renormalizable_witness_is_globally_PQ_and_X_invariant"
            ]
        )
        self.assertTrue(
            all(
                row["parameter_id"].startswith("lambda::")
                and row["self_conjugate"]
                and row["PQ_charge"] == 0
                and row["X_charge"] == 0
                for row in support["support"]
            )
        )
        self.assertEqual(
            completion_ids := self.report[
                "squared_stationarity_global_EFT_completion"
            ]["renormalizable_witness_nonzero_parameter_ids"],
            support["nonzero_parameter_ids"],
        )
        self.assertEqual(len(completion_ids), 37)

    def test_frozen_reconstructed_stationarity_and_full_hessian(self) -> None:
        live = self.report["live_local_feasibility"]
        stationarity = live["stationarity"]
        hessian = live["Hessian"]
        self.assertEqual(stationarity["active_live_rows"], 76)
        self.assertEqual(stationarity["nonzero_live_entries"], 323)
        self.assertEqual(stationarity["mixed_Q_plus_sqrt2Q_live_rows"], [226, 229])
        self.assertEqual(stationarity["total_rational_equations_after_split"], 78)
        self.assertEqual(stationarity["exact_reconstructed_rank"], 15)
        self.assertEqual(stationarity["exact_reconstructed_nullity"], 36)
        self.assertEqual(stationarity["normalized_exact_potential_value"], "-1")
        self.assertTrue(stationarity["exact_reconstructed_stationarity"])
        self.assertLess(stationarity["maximum_live_reconstruction_residual"], 3e-14)
        self.assertLess(stationarity["gradient_max_abs"], 1e-12)
        self.assertEqual(hessian["symmetry_tangent_rank_float64"], 38)
        self.assertEqual(hessian["zero_eigenvalue_count_abs_lt_1e_minus_7"], 38)
        self.assertEqual(hessian["strictly_positive_transverse_dimension"], 448)
        self.assertGreater(hessian["minimum_transverse_eigenvalue"], 0.09)
        self.assertLess(
            abs(hessian["minimum_full_eigenvalue"]), 1e-11
        )
        self.assertLess(
            hessian["Hessian_times_full_symmetry_tangents_max_abs"], 1e-11
        )
        self.assertTrue(live["numerical_local_feasibility_checks_pass"])

    def test_physical_sector_census_is_complete(self) -> None:
        sectors = self.report["live_local_feasibility"][
            "physical_sector_decomposition"
        ]
        self.assertEqual(sectors["color_operator_eigenvalues"], [0, 16, 36, 40])
        self.assertEqual(
            sectors["charge_operator_eigenvalues"], [0, 1, 4, 9, 16, 25, 36]
        )
        self.assertEqual(sectors["full_dimension_sum"], 486)
        self.assertEqual(sectors["zero_mode_sum"], 38)
        self.assertEqual(sectors["transverse_dimension_sum"], 448)
        self.assertLess(sectors["Hessian_color_commutator_max_abs"], 1e-11)
        self.assertLess(sectors["Hessian_charge_commutator_max_abs"], 1e-11)
        actual = {
            (row["12C2_SU3"], row["Q3_squared"]): row[
                "transverse_dimension"
            ]
            for row in sectors["sectors"]
        }
        self.assertEqual(actual, EXPECTED_TRANSVERSE_SECTORS)
        self.assertTrue(
            all(
                row["minimum_transverse_eigenvalue"] > 0.09
                for row in sectors["sectors"]
            )
        )

    def test_reconstruction_rejects_values_off_the_declared_lattice(self) -> None:
        with self.assertRaises(ArithmeticError):
            theorem._recognize_q_or_sqrt2q(math.pi)

    def test_fail_closed_semantics(self) -> None:
        self.assertTrue(all(value is False for value in self.report["closure_claims"].values()))
        self.assertEqual(
            set(self.report["closure_claims"]),
            {
                "physical_SM_G3",
                "physical_SM_G4",
                "physical_SM_G5",
                "physical_SM_G6",
                "physical_SM_G7",
            },
        )
        supersession = self.report["supersession"]
        self.assertEqual(
            supersession["old_selected_EFT_target_actual_stabilizer"],
            "SU(3)_C x U(1)_89",
        )
        self.assertFalse(
            supersession["old_selected_EFT_target_was_standard_SU3C_x_U1em"]
        )
        self.assertEqual(
            supersession["new_target_exact_stabilizer"],
            "standard SU(3)_C x U(1)_em",
        )
        self.assertTrue(
            supersession[
                "old_abstract_EFT_mathematical_theorems_may_remain_true_in_formal_scope"
            ]
        )
        self.assertTrue(
            supersession[
                "old_abstract_EFT_theorems_do_not_close_physical_SM_G3_G4_G5"
            ]
        )
        stationarity = self.report["live_local_feasibility"]["stationarity"]
        summary = self.report["logical_summary"]
        self.assertFalse(stationarity["source_algebra_derivation_complete"])
        self.assertFalse(
            summary["source_bound_exact_stationary_PSD_witness_available"]
        )
        self.assertFalse(summary["source_bound_global_equality_orbit_proved"])
        self.assertFalse(summary["physical_G6_closed"])
        self.assertIn("OPEN", self.report["status"])

    def test_dependency_provenance_is_complete_and_validated(self) -> None:
        dependencies = self.report["source_binding"]["dependencies"]
        validation = dependencies["validation"]
        files = dependencies["files"]
        self.assertEqual(validation["dependency_file_count"], 20)
        self.assertEqual(len(files), 20)
        self.assertTrue(validation["all_dependency_files_present"])
        self.assertTrue(
            validation["provenance_core_matches_imported_expected_pin"]
        )
        self.assertTrue(validation["physical_quotient_frozen_certified"])
        self.assertTrue(
            validation["scalar_contract_frozen_has_zero_failures"]
        )
        self.assertTrue(
            validation["G2_derivative_audit_frozen_has_zero_failures"]
        )
        for required in (
            "exact_g6_sm_provenance_feasibility_v20.py",
            "EXACT_G6_SM_PROVENANCE_FEASIBILITY_V20.json",
            "exact_gauged_u1x_physical_quotient_v20.py",
            "gauged_u1x_scalar_contract_v20.py",
            "gauged_u1x_g2_derivative_audit_v20.py",
            "live_g2_canonical_486_field_chart_v20.py",
            "live_g2_arbitrary_component_potential_values_v20.py",
            "live_g2_exact_quadratic_family_derivatives_v20.py",
        ):
            self.assertIn(required, files)
        for binding in files.values():
            self.assertEqual(len(binding["raw_sha256"]), 64)
            self.assertEqual(len(binding["portable_lf_sha256"]), 64)

    def test_dependency_drift_triggers_cli_freeze_guard(self) -> None:
        drifted_dependencies = copy.deepcopy(theorem.dependency_bindings())
        name = "live_g2_canonical_486_field_chart_v20.py"
        drifted_dependencies["files"][name]["raw_sha256"] = "0" * 64
        with mock.patch.object(
            theorem, "dependency_bindings", return_value=drifted_dependencies
        ):
            with mock.patch.object(
                sys, "argv", ["physical-sm", "--skip-live"]
            ):
                with contextlib.redirect_stdout(io.StringIO()):
                    with self.assertRaisesRegex(
                        ArithmeticError,
                        "frozen physical-SM feasibility report drifted",
                    ):
                        theorem.main()
            with mock.patch.object(
                sys,
                "argv",
                ["physical-sm", "--skip-live", "--allow-unfrozen"],
            ):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(theorem.main(), 0)

    def test_cli_fails_on_drift_unless_explicitly_overridden(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            drifted = Path(directory) / "drifted.json"
            drifted.write_text("{}\n", encoding="utf-8")
            with mock.patch.object(theorem, "OUT_JSON", drifted):
                with mock.patch.object(
                    sys, "argv", ["physical-sm", "--skip-live"]
                ):
                    with contextlib.redirect_stdout(io.StringIO()):
                        with self.assertRaisesRegex(
                            ArithmeticError, "frozen physical-SM feasibility report drifted"
                        ):
                            theorem.main()
                with mock.patch.object(
                    sys,
                    "argv",
                    ["physical-sm", "--skip-live", "--allow-unfrozen"],
                ):
                    with contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(theorem.main(), 0)

    def test_live_compiler_replay_matches_frozen_certificate(self) -> None:
        live = theorem.live_local_feasibility()
        frozen = self.report["live_local_feasibility"]
        self.assertEqual(
            live["stationarity"]["exact_reconstructed_rank"],
            frozen["stationarity"]["exact_reconstructed_rank"],
        )
        self.assertLess(live["stationarity"]["gradient_max_abs"], 1e-12)
        self.assertEqual(
            live["Hessian"]["strictly_positive_transverse_dimension"], 448
        )
        self.assertGreater(
            live["Hessian"]["minimum_transverse_eigenvalue"], 0.09
        )
        self.assertEqual(
            live["physical_sector_decomposition"]["transverse_dimension_sum"],
            448,
        )

    def test_live_report_is_identical_under_ambient_and_single_thread_blas(self) -> None:
        command = [
            sys.executable,
            "-B",
            "-c",
            (
                "import json; "
                "import physical_sm_vacuum_local_feasibility_v20 as theorem; "
                "payload={'raw': theorem.live_local_feasibility(), "
                "'report': theorem.build_report()}; "
                "print(json.dumps(theorem._jsonable(payload), "
                "sort_keys=True, separators=(',', ':')))"
            ),
        ]
        ambient_environment = os.environ.copy()
        ambient_environment["PYTHONDONTWRITEBYTECODE"] = "1"
        ambient_environment["SO10_PUBLISHED_API_ROOT"] = str(theorem.ROOT)
        for name in (
            "OPENBLAS_NUM_THREADS",
            "OMP_NUM_THREADS",
            "MKL_NUM_THREADS",
            "NUMEXPR_NUM_THREADS",
        ):
            ambient_environment.pop(name, None)
        single_thread_environment = ambient_environment.copy()
        for name in (
            "OPENBLAS_NUM_THREADS",
            "OMP_NUM_THREADS",
            "MKL_NUM_THREADS",
            "NUMEXPR_NUM_THREADS",
        ):
            single_thread_environment[name] = "1"

        ambient = json.loads(
            subprocess.run(
                command,
                cwd=theorem.ROOT,
                env=ambient_environment,
                check=True,
                capture_output=True,
                text=True,
            ).stdout
        )
        single_thread = json.loads(
            subprocess.run(
                command,
                cwd=theorem.ROOT,
                env=single_thread_environment,
                check=True,
                capture_output=True,
                text=True,
            ).stdout
        )
        ambient_raw = _flatten_live_leaves(ambient["raw"])
        single_thread_raw = _flatten_live_leaves(single_thread["raw"])
        self.assertEqual(set(ambient_raw), set(single_thread_raw))
        raw_diff_paths = {
            path
            for path in ambient_raw
            if ambient_raw[path] != single_thread_raw[path]
        }
        self.assertEqual(raw_diff_paths, theorem.BLAS_DIAGNOSTIC_PATHS)
        self.assertEqual(ambient["report"], single_thread["report"])
        self.assertEqual(
            ambient["report"]["integrity"]["core_sha256"],
            single_thread["report"]["integrity"]["core_sha256"],
        )

    def test_diagnostic_float_canonicalizer_is_scoped_and_fail_closed(self) -> None:
        diagnostic = {
            "boolean": True,
            "integer": 38,
            "exact": "1/3",
            "tiny": -4.651663722860053e-15,
            "margin": 0.0999983599064178,
        }
        self.assertEqual(len(theorem.BLAS_DIAGNOSTIC_PATHS), 27)
        self.assertEqual(
            theorem._canonicalize_blas_diagnostic_float(diagnostic["tiny"]),
            0.0,
        )
        self.assertEqual(
            theorem._canonicalize_blas_diagnostic_float(diagnostic["margin"]),
            0.09999835991,
        )
        for nonfloat in (True, 38, "1/3", None):
            with self.assertRaisesRegex(TypeError, "must be a float"):
                theorem._canonicalize_blas_diagnostic_float(nonfloat)
        for nonfinite in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaisesRegex(ArithmeticError, "non-finite"):
                theorem._canonicalize_blas_diagnostic_float(nonfinite)

        live = copy.deepcopy(theorem.live_local_feasibility())
        reconstruction_residual = live["stationarity"][
            "maximum_live_reconstruction_residual"
        ]
        with mock.patch.object(
            theorem,
            "_canonicalize_blas_diagnostic_float",
            wraps=theorem._canonicalize_blas_diagnostic_float,
        ) as canonicalize:
            projected = theorem._canonicalize_live_blas_diagnostics(live)
        self.assertEqual(canonicalize.call_count, 27)
        raw_leaves = _flatten_live_leaves(live)
        projected_leaves = _flatten_live_leaves(projected)
        self.assertEqual(set(raw_leaves), set(projected_leaves))
        self.assertEqual(
            {
                path
                for path in raw_leaves
                if raw_leaves[path] != projected_leaves[path]
            },
            theorem.BLAS_DIAGNOSTIC_PATHS,
        )
        self.assertEqual(
            projected["stationarity"]["maximum_live_reconstruction_residual"],
            reconstruction_residual,
        )
        self.assertEqual(
            projected["stationarity"][
                "maximum_live_value_reconstruction_residual"
            ],
            live["stationarity"][
                "maximum_live_value_reconstruction_residual"
            ],
        )
        missing = copy.deepcopy(live)
        del missing["Hessian"]["maximum_eigenvalue"]
        with self.assertRaises(KeyError):
            theorem._canonicalize_live_blas_diagnostics(missing)
        wrong_type = copy.deepcopy(live)
        wrong_type["stationarity"]["gradient_l2_norm"] = True
        with self.assertRaisesRegex(TypeError, "must be a float"):
            theorem._canonicalize_live_blas_diagnostics(wrong_type)

    def test_integrity_pins(self) -> None:
        report = copy.deepcopy(self.report)
        integrity = report.pop("integrity")
        self.assertEqual(integrity["core_sha256"], EXPECTED_CORE_SHA256)
        self.assertEqual(
            hashlib.sha256(theorem.canonical_json_bytes(report)).hexdigest(),
            EXPECTED_CORE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(theorem.Path(theorem.__file__).read_bytes()).hexdigest(),
            EXPECTED_SOURCE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(theorem.OUT_JSON.read_bytes()).hexdigest(),
            EXPECTED_JSON_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(theorem.OUT_MD.read_bytes()).hexdigest(),
            EXPECTED_MD_SHA256,
        )
        self.assertEqual(
            self.report["source_binding"]["sha256"], EXPECTED_SOURCE_SHA256
        )


if __name__ == "__main__":
    unittest.main()
