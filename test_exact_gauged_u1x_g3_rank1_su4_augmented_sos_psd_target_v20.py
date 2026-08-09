#!/usr/bin/env python3
"""Fail-closed tests for the exact PSD-route and physical-target certificate."""
from __future__ import annotations

import copy
import importlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np

SOURCE_HERE = Path(__file__).resolve().parent
SUBJECT_MODULE_NAME = (
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20"
)
DIRECT_SOURCE_DEPENDENCIES = (
    "exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py",
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py",
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py",
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20.py",
    "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py",
    "exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py",
    "exact_gauged_u1x_g3_su5_max_negative_rank1_su3_slice_v20.py",
    "exact_phisigma_casimir_projectors_v20.py",
    "exact_gauged_u1x_g3_pd_rank_certificate_v20.py",
)
DIRECT_ARTIFACT_DEPENDENCIES = (
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_V20.json",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.json",
)
SUBJECT_FILES = (
    f"{SUBJECT_MODULE_NAME}.py",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_V20.json",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_V20.md",
)


def _publication_dependencies_present(root: Path) -> bool:
    return all(
        (root / name).is_file()
        for name in (*DIRECT_SOURCE_DEPENDENCIES, *DIRECT_ARTIFACT_DEPENDENCIES)
    )


_PUBLICATION_FIXTURE: tempfile.TemporaryDirectory[str] | None = None
if _publication_dependencies_present(SOURCE_HERE):
    HERE = SOURCE_HERE
else:
    # Isolated-hold development mode only. The publication source itself never
    # searches outside HERE. This test mounts an exact temporary repository-root
    # fixture; once the quartet is copied into the repository this branch is unused.
    development_repository = SOURCE_HERE.parent / "so10-axion-v20-reaudit"
    if not development_repository.is_dir():
        raise FileNotFoundError(
            "repository-local dependencies are absent and no isolated fixture source exists"
        )
    _PUBLICATION_FIXTURE = tempfile.TemporaryDirectory(
        prefix="_publication_fixture_", dir=SOURCE_HERE
    )
    HERE = Path(_PUBLICATION_FIXTURE.name).resolve()
    for source in development_repository.iterdir():
        if source.is_file():
            shutil.copy2(source, HERE / source.name)
    # During isolated development the audited predecessor quartets may still be
    # siblings rather than tracked in the working repository. Overlay only their
    # exact files into the temporary publication root.
    for predecessor in (
        SOURCE_HERE.parent / "_g3_future_hold_cubic",
        SOURCE_HERE.parent / "_g3_future_hold_quartic",
    ):
        if predecessor.is_dir():
            for name in (*DIRECT_SOURCE_DEPENDENCIES, *DIRECT_ARTIFACT_DEPENDENCIES):
                candidate = predecessor / name
                if candidate.is_file():
                    shutil.copy2(candidate, HERE / name)
    for name in SUBJECT_FILES:
        shutil.copy2(SOURCE_HERE / name, HERE / name)
    missing = [
        name
        for name in (*DIRECT_SOURCE_DEPENDENCIES, *DIRECT_ARTIFACT_DEPENDENCIES)
        if not (HERE / name).is_file()
    ]
    if missing:
        raise FileNotFoundError(f"temporary publication fixture is incomplete: {missing}")

sys.path.insert(0, str(HERE))
for _name in DIRECT_SOURCE_DEPENDENCIES:
    sys.modules.pop(Path(_name).stem, None)
sys.modules.pop(SUBJECT_MODULE_NAME, None)
subject = importlib.import_module(SUBJECT_MODULE_NAME)


class ExactRank1SU4PSDTargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frozen = json.loads((HERE / subject.JSON_NAME).read_text(encoding="utf-8"))
        cls.regenerated_object = subject.build_report()
        cls.regenerated = subject._jsonable(cls.regenerated_object)

    def assert_rejected(self, report: dict[str, object]) -> None:
        valid, failures = subject.validate_report(report)
        self.assertFalse(valid)
        self.assertTrue(failures)

    def test_exact_regeneration_matches_frozen_json(self) -> None:
        self.assertEqual(self.regenerated, self.frozen)

    def test_markdown_is_deterministic_rendering(self) -> None:
        expected = subject.render_markdown(self.frozen)
        actual = (HERE / subject.MARKDOWN_NAME).read_text(encoding="utf-8")
        self.assertEqual(actual, expected)

    def test_live_dependency_provenance_is_exact(self) -> None:
        self.assertEqual(subject.HERE, HERE)
        self.assertEqual(subject.dependency_hashes(), subject.EXPECTED_DEPENDENCY_HASHES)
        valid, failures = subject.validate_report(
            self.frozen, check_live_dependencies=True
        )
        self.assertTrue(valid, failures)

    def test_private_cache_returns_fresh_equal_public_graphs(self) -> None:
        before = subject.build_report_cache_info()
        first = subject.build_report()
        second = subject.build_report()
        after = subject.build_report_cache_info()
        self.assertIsNot(first, second)
        self.assertEqual(first, second)
        self.assertIsNot(first["scope"], second["scope"])
        self.assertIsNot(
            first["physical_target"]["quartic"]["numerator"],
            second["physical_target"]["quartic"]["numerator"],
        )
        self.assertIsNot(
            first["standard_PSD_coordinate_routes"]["real_type_rows"][0][
                "augmented_real_structure"
            ],
            second["standard_PSD_coordinate_routes"]["real_type_rows"][0][
                "augmented_real_structure"
            ],
        )
        self.assertEqual(after.hits, before.hits + 2)
        self.assertEqual(after.misses, before.misses)

    def test_public_report_mutations_cannot_poison_private_cache_or_contract(self) -> None:
        poisoned = subject.build_report()
        poisoned["scope"]["G3_closed"] = True
        poisoned["claim_boundary"]["proved_here"].append("false injected claim")
        poisoned["provenance"]["actual_dependency_hashes"][
            next(iter(subject.EXPECTED_DEPENDENCY_HASHES))
        ] = "0" * 64
        poisoned["standard_PSD_coordinate_routes"]["real_type_rows"][0][
            "augmented_real_structure"
        ][0][0] += 1
        poisoned["physical_target"]["quartic"]["numerator"][0] += 1
        fresh = subject.build_report()
        self.assertEqual(fresh, self.frozen)
        self.assertIs(fresh["scope"]["G3_closed"], False)
        self.assertIs(subject.EXPECTED_SCOPE["G3_closed"], False)
        valid, failures = subject.validate_report(fresh)
        self.assertTrue(valid, failures)

    def test_signed_int64_guard_rejects_overflow(self) -> None:
        self.assertEqual(subject._require_int64(subject.INT64_MAX, "test"), subject.INT64_MAX)
        self.assertEqual(subject._require_int64(-subject.INT64_MAX, "test"), -subject.INT64_MAX)
        with self.assertRaises(OverflowError):
            subject._require_int64(subject.INT64_MAX + 1, "test")
        with self.assertRaises(OverflowError):
            subject._require_int64(-subject.INT64_MAX - 1, "test")

    def test_all_recorded_bounds_fit_int64(self) -> None:
        safety = self.frozen["exact_arithmetic_safety"]
        self.assertTrue(safety["all_recorded_bounds_fit_signed_int64"])
        for key in (
            "observed_spectral_power_maximum",
            "observed_spectral_response_maximum",
            "observed_quartic_image_maximum",
            "full_target_maximum_absolute_numerator",
        ):
            self.assertGreaterEqual(safety[key], 0)
            self.assertLessEqual(safety[key], subject.INT64_MAX)

    def test_congruence_identities_hold_over_integers(self) -> None:
        rows = self.frozen["standard_PSD_coordinate_routes"]["real_type_rows"]
        self.assertEqual(len(rows), 9)
        for row in rows:
            b = np.asarray(row["augmented_real_structure"], dtype=object)
            p = np.asarray(row["fixed_basis_real_numerator"], dtype=object)
            q = np.asarray(row["fixed_basis_imaginary_numerator"], dtype=object)
            m = row["augmented_multiplicity"]
            self.assertTrue(np.array_equal(b @ b, np.eye(m, dtype=object)))
            self.assertFalse(np.any(b @ p - p))
            self.assertFalse(np.any(b @ q + q))
            self.assertEqual(p.shape[1] + q.shape[1], m)
            self.assertEqual(row["fixed_basis_rank_at_first_prime"], m)
            self.assertEqual(row["fixed_basis_rank_at_second_prime"], m)

    def test_naive_raw_coordinate_counterexample_is_frozen(self) -> None:
        counterexample = self.frozen["standard_PSD_coordinate_routes"][
            "naive_coordinate_counterexample"
        ]
        self.assertEqual(counterexample["failing_block_count"], 4)
        self.assertEqual(
            counterexample["failing_representatives"],
            [[0, 1, 0], [0, 2, 0], [1, 0, 1], [1, 1, 1]],
        )

    def test_full_target_chart_is_exact_and_cubic_is_zero(self) -> None:
        full = self.frozen["physical_target"]["full_graded_chart"]
        numerator = np.asarray(full["numerator"], dtype=np.int64)
        self.assertEqual(full["grade_lengths"], [1, 4, 45, 478, 6057])
        self.assertEqual(numerator.shape, (6585,))
        self.assertEqual(full["common_denominator"], 1_728_000)
        self.assertEqual(full["total_nonzero_count"], 845)
        self.assertEqual(
            full["numerator_sha256"],
            "e2d9eec1b01b3eeefc4a54d404db93171aa6600ea9ef646a215ab0b5401f7630",
        )
        self.assertFalse(np.any(numerator[50:528]))

    def test_quartic_target_is_bound_to_frozen_chart(self) -> None:
        quartic = self.frozen["physical_target"]["quartic"]
        self.assertEqual(quartic["row_count"], 6057)
        self.assertEqual(quartic["common_denominator"], 3375)
        self.assertEqual(quartic["nonzero_count"], 825)
        self.assertEqual(
            quartic["pivot_physical_quartic_coordinates_sha256"],
            "f33cb0163f3cdc4a3480cb55e09329888c8cf0641cc0acab4cb01f8075058ce4",
        )
        self.assertEqual(
            quartic["numerator_sha256"],
            "38476cff340ef8702735d48d7dbdf644ed41f8dc4a359264d33d966f177145ad",
        )
        self.assertTrue(quartic["all_i_times_anti_real_rows_zero_exact"])

    def test_scope_remains_fail_closed(self) -> None:
        scope = self.frozen["scope"]
        for key in (
            "coefficient_map_reparameterized_in_standard_PSD_coordinates",
            "semidefinite_feasibility_solved",
            "exact_primal_PSD_certificate_constructed",
            "exact_dual_Farkas_certificate_constructed",
            "arbitrary_Phi_lower_bound_proved",
            "equality_orbit_classification_proved",
            "full_486_field_Hessian_classification_proved",
            "G3_closed",
        ):
            self.assertIs(scope[key], False)
            mutated = copy.deepcopy(self.frozen)
            mutated["scope"][key] = True
            self.assert_rejected(mutated)

    def test_textual_claim_boundary_mutations_are_rejected(self) -> None:
        for section in ("proved_here", "not_proved_here"):
            mutated = copy.deepcopy(self.frozen)
            mutated["claim_boundary"][section].append("injected claim")
            self.assert_rejected(mutated)
            mutated = copy.deepcopy(self.frozen)
            mutated["claim_boundary"][section].pop()
            self.assert_rejected(mutated)

    def test_dependency_hash_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.frozen)
        name = next(iter(subject.EXPECTED_DEPENDENCY_HASHES))
        mutated["provenance"]["actual_dependency_hashes"][name] = "0" * 64
        self.assert_rejected(mutated)

    def test_imported_module_file_binding_uses_live_resolved_path(self) -> None:
        for name, module in subject.IMPORTED_SOURCE_MODULES.items():
            self.assertEqual(
                subject._imported_module_dependency_path(name),
                Path(module.__file__).resolve(),
            )
            binding = self.frozen["provenance"]["dependency_file_bindings"][name]
            self.assertEqual(Path(module.__file__).resolve().parent, subject.HERE)
            self.assertEqual(
                binding["binding_kind"], "Path(imported_module.__file__).resolve()"
            )
            self.assertEqual(binding["module_name"], module.__name__)
            self.assertEqual(binding["imported_file_basename"], name)
            self.assertEqual(binding["repository_local_path"], name)
            self.assertEqual(binding["required_parent"], ".")

    def test_external_exact_module_shadow_is_rejected(self) -> None:
        name, module = next(iter(subject.IMPORTED_SOURCE_MODULES.items()))
        actual = Path(module.__file__).resolve()
        with tempfile.TemporaryDirectory(prefix="external_exact_shadow_") as directory:
            shadow = Path(directory).resolve() / name
            shutil.copy2(actual, shadow)
            self.assertEqual(
                subject._portable_file_sha256(shadow),
                subject.EXPECTED_DEPENDENCY_HASHES[name],
            )
            with mock.patch.object(module, "__file__", str(shadow)):
                with self.assertRaises(ArithmeticError):
                    subject.dependency_hashes()
                valid, failures = subject.validate_report(
                    self.frozen, check_live_dependencies=True
                )
                self.assertFalse(valid)
                self.assertTrue(
                    any(
                        "live dependency validation failed" in failure
                        for failure in failures
                    )
                )

    def test_external_exact_artifact_shadow_cannot_be_resolved(self) -> None:
        name = subject.ARTIFACT_DEPENDENCIES[0]
        local = subject._artifact_dependency_path(name)
        self.assertEqual(local.parent, subject.HERE)
        with tempfile.TemporaryDirectory(prefix="external_artifact_shadow_") as directory:
            shadow = Path(directory).resolve() / name
            shutil.copy2(local, shadow)
            self.assertEqual(
                subject._portable_file_sha256(shadow),
                subject.EXPECTED_DEPENDENCY_HASHES[name],
            )
            self.assertEqual(subject._artifact_dependency_path(name), local)
            with self.assertRaises(ArithmeticError):
                subject._require_repository_local_file(
                    shadow, name, "external artifact shadow regression"
                )

    def test_imported_module_file_path_drift_fails_closed(self) -> None:
        name, module = next(iter(subject.IMPORTED_SOURCE_MODULES.items()))
        nonexistent = HERE / "missing_import_binding" / name
        with mock.patch.object(module, "__file__", str(nonexistent)):
            with self.assertRaises(FileNotFoundError):
                subject.dependency_hashes()
            valid, failures = subject.validate_report(
                self.frozen, check_live_dependencies=True
            )
            self.assertFalse(valid)
            self.assertTrue(
                any("live dependency validation failed" in failure for failure in failures)
            )

    def test_imported_module_basename_drift_fails_closed(self) -> None:
        entries = list(subject.IMPORTED_SOURCE_MODULES.items())
        name, module = entries[0]
        wrong_existing_path = Path(entries[1][1].__file__).resolve()
        with mock.patch.object(module, "__file__", str(wrong_existing_path)):
            with self.assertRaises(ArithmeticError):
                subject.dependency_hashes()
            valid, failures = subject.validate_report(
                self.frozen, check_live_dependencies=True
            )
            self.assertFalse(valid)
            self.assertTrue(
                any("live dependency validation failed" in failure for failure in failures)
            )

    def test_quartic_target_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.frozen)
        mutated["physical_target"]["quartic"]["numerator"][0] += 1
        self.assert_rejected(mutated)

    def test_quadratic_target_coordinate_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.frozen)
        mutated["physical_target"]["quadratic"]["SU4_invariant_basis"][
            "target_coordinates"
        ][0]["numerator"] += 1
        self.assert_rejected(mutated)

    def test_full_target_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.frozen)
        mutated["physical_target"]["full_graded_chart"]["numerator"][50] = 1
        self.assert_rejected(mutated)

    def test_real_structure_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.frozen)
        mutated["standard_PSD_coordinate_routes"]["real_type_rows"][0][
            "augmented_real_structure"
        ][0][0] += 1
        self.assert_rejected(mutated)

    def test_fixed_basis_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.frozen)
        mutated["standard_PSD_coordinate_routes"]["real_type_rows"][0][
            "fixed_basis_real_numerator"
        ][0][0] += 1
        self.assert_rejected(mutated)

    def test_rank_and_proof_mutations_are_rejected(self) -> None:
        for path in (
            ("standard_PSD_coordinate_routes", "real_type_rows", 0, "fixed_basis_rank_at_first_prime"),
            ("physical_target", "quartic", "proof_grade"),
            ("physical_target", "full_graded_chart", "proof_grade"),
            ("proof_grade",),
        ):
            mutated = copy.deepcopy(self.frozen)
            cursor = mutated
            for key in path[:-1]:
                cursor = cursor[key]
            leaf = path[-1]
            cursor[leaf] = False if isinstance(cursor[leaf], bool) else cursor[leaf] - 1
            self.assert_rejected(mutated)

    def test_publication_source_does_not_depend_on_research_diagnostics(self) -> None:
        source = Path(subject.__file__).read_text(encoding="utf-8")
        for forbidden in (
            "derive_real_type_congruences",
            "probe_augmented_real_structures",
            "derive_physical_target",
            "stream_quartic_target_restrictions",
            "analyze_quartic_target_schur",
            "stream_quartic_target_chart",
        ):
            self.assertNotIn(forbidden, source)
        for forbidden in (
            "_g3_future_hold_quartic",
            "_g3_future_hold_cubic",
            "so10-axion-v20-reaudit",
            "SEARCH_DIRECTORIES",
        ):
            self.assertNotIn(forbidden, source)

    def test_congruence_wording_is_dimensionally_exact(self) -> None:
        source = Path(subject.__file__).read_text(encoding="utf-8")
        markdown = (HERE / subject.MARKDOWN_NAME).read_text(encoding="utf-8")
        payload = json.dumps(self.frozen, sort_keys=True)
        for text in (source, markdown, payload):
            self.assertNotIn("F=P+iQ", text)
            self.assertIn("F=[P | iQ]", text)
        for row in self.frozen["standard_PSD_coordinate_routes"]["real_type_rows"]:
            m = row["augmented_multiplicity"]
            p = np.asarray(row["fixed_basis_real_numerator"], dtype=object)
            q = np.asarray(row["fixed_basis_imaginary_numerator"], dtype=object)
            self.assertEqual(p.shape[0], m)
            self.assertEqual(q.shape[0], m)
            self.assertEqual(p.shape[1] + q.shape[1], m)


if __name__ == "__main__":
    unittest.main()
