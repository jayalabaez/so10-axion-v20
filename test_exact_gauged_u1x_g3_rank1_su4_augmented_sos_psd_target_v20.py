#!/usr/bin/env python3
"""Regression tests for rejection of the superseded v20 physical target.

The byte-pinned v20 source remains importable only as a generation-time
structural API for the corrected v21 map.  This test deliberately does not run
its obsolete target generator or accept any target/primal theorem from it.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import g1_g8_gate_ledger_v20 as ledger


ROOT = Path(__file__).resolve().parent
ARTIFACT = ROOT / (
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_V20.json"
)
SOURCE = ROOT / "exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py"
SOURCE_RAW_SHA256 = (
    "8493a90d9b689bc02479151529ac697425f56087f2bdbebb40176f418b7c0ff8"
)


def load(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


class RejectedV20PhysicalTargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.census = load(
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CENSUS_V20.json"
        )
        cls.cubic = load(
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_V20.json"
        )
        cls.quartic = load(
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.json"
        )

    def test_artifact_is_unmistakably_rejected_and_superseded(self) -> None:
        report = self.report
        self.assertEqual(
            report["status"],
            "REJECTED_V20_PHYSICAL_TARGET__STRUCTURAL_PSD_ROUTES_ONLY",
        )
        self.assertEqual(
            report["overall_state"],
            "STRUCTURAL_PSD_ROUTES_RETAINED__V20_PHYSICAL_TARGET_REJECTED__SUPERSEDED_BY_V21",
        )
        self.assertIs(report["proof_grade"], False)
        self.assertIs(report["physical_target"]["accepted_as_physical_target"], False)
        self.assertIs(report["rejection"]["v20_physical_target_accepted"], False)
        self.assertIs(
            report["rejection"]["v20_primal_or_arbitrary_Phi_theorem_accepted"],
            False,
        )
        self.assertEqual(
            report["rejection"]["superseded_by"],
            "corrected_rank1_publication_v21",
        )
        self.assertTrue(report["scope"]["legacy_physical_target_rejected"])
        self.assertTrue(
            report["scope"]["structural_PSD_routes_retained_for_v21_generation"]
        )
        self.assertFalse(
            report["scope"]["physical_target_formula_all_five_grades_constructed"]
        )
        self.assertFalse(
            report["scope"]["physical_target_full_6585_row_vector_constructed"]
        )
        for path in (
            ("full_graded_chart", "proof_grade"),
            ("linear", "SU4_invariant_basis", "proof_grade"),
            ("quadratic", "SU4_invariant_basis", "proof_grade"),
            ("quartic", "proof_grade"),
        ):
            value = report["physical_target"]
            for key in path:
                value = value[key]
            self.assertIs(value, False, path)
        self.assertIs(report["physical_target"]["lower_grade_proof_grade"], False)

    def test_only_structural_routes_are_recognized_and_target_is_never_exact(self) -> None:
        self.assertTrue(
            ledger._rank1_su4_augmented_sos_psd_routes_and_stale_payload_well_formed(
                self.report, self.census, self.cubic, self.quartic
            )
        )
        self.assertFalse(
            ledger._rank1_su4_augmented_sos_psd_target_exact(
                self.report, self.census, self.cubic, self.quartic
            )
        )

    def test_updated_echo_mutations_fail_structural_recognition(self) -> None:
        attacks = []
        changed = copy.deepcopy(self.report)
        changed["rejection"]["v20_physical_target_accepted"] = True
        attacks.append(changed)
        changed = copy.deepcopy(self.report)
        changed["proof_grade"] = True
        attacks.append(changed)
        changed = copy.deepcopy(self.report)
        changed["scope"]["physical_target_full_6585_row_vector_constructed"] = True
        attacks.append(changed)
        changed = copy.deepcopy(self.report)
        changed["standard_PSD_coordinate_routes"]["standard_total_parameter_count"] = 19_593
        attacks.append(changed)
        for changed in attacks:
            with self.subTest(index=attacks.index(changed)):
                self.assertFalse(
                    ledger._rank1_su4_augmented_sos_psd_routes_and_stale_payload_well_formed(
                        changed, self.census, self.cubic, self.quartic
                    )
                )

    def test_legacy_generator_is_raw_pinned_but_never_executed_by_release(self) -> None:
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(), SOURCE_RAW_SHA256)
        orchestration = "\n".join(
            (ROOT / name).read_text(encoding="utf-8")
            for name in (
                "prepare_validation_artifacts_v20.py",
                "replicate.py",
                "validate_release_v20.py",
                ".github/workflows/current-main-full-reaudit.yml",
                ".github/workflows/g1-g8-execution-roadmap.yml",
                ".github/workflows/g1-g8-gate-ledger.yml",
                ".github/workflows/gauged-u1x-g3-stability.yml",
                ".github/workflows/replicate-and-falsify.yml",
            )
        )
        for forbidden in (
            "python exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py",
            "python -B exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py",
        ):
            self.assertNotIn(forbidden, orchestration)

    def test_public_entrypoints_and_cli_fail_without_mutating_files(self) -> None:
        import exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20 as source

        with self.assertRaisesRegex(ArithmeticError, "rejected and superseded"):
            source.build_report()
        with self.assertRaisesRegex(ArithmeticError, "renderer is disabled"):
            source.render_markdown({})
        self.assertEqual(
            source.validate_report(self.report),
            (
                False,
                (
                    "the v20 physical target is rejected and superseded by "
                    "corrected_rank1_publication_v21",
                ),
            ),
        )
        before = {
            path: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (
                ARTIFACT,
                ROOT
                / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_V20.md",
            )
        }
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "forbidden.json"
            markdown = Path(directory) / "forbidden.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(SOURCE),
                    "--output",
                    str(output),
                    "--markdown-output",
                    str(markdown),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 2)
            self.assertIn("REJECTED", completed.stderr)
            self.assertIn("no files were read or written", completed.stderr)
            self.assertFalse(output.exists())
            self.assertFalse(markdown.exists())
        after = {
            path: hashlib.sha256(path.read_bytes()).hexdigest() for path in before
        }
        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
