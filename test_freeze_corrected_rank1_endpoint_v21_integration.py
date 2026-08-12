#!/usr/bin/env python3
"""Fail-closed tests for the corrected endpoint integration fingerprint."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import freeze_corrected_rank1_endpoint_v21_integration as freezer


class CorrectedEndpointIntegrationFreezeTests(unittest.TestCase):
    def test_frozen_manifest_matches_all_intended_paths(self) -> None:
        report = freezer.check_manifest()
        discovery = subprocess.run(
            [
                sys.executable,
                "-B",
                "-c",
                (
                    "import unittest; "
                    "print(unittest.defaultTestLoader.discover('.')"
                    ".countTestCases())"
                ),
            ],
            cwd=freezer.ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        current_test_count = int(discovery.stdout.strip())
        theory_verdict = json.loads(
            (freezer.ROOT / "THEORY_VALIDATION_MATRIX_V20_VERDICT.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(
            theory_verdict["current_tree_unit_tests_discovered"],
            current_test_count,
        )
        self.assertEqual(
            theory_verdict["gates"][-1]["evidence"][
                "current_tree_tests_discovered"
            ],
            current_test_count,
        )
        self.assertEqual(
            report["status"],
            "EXACT_CORRECTED_ENDPOINT_V21_CENTRAL_INTEGRATION_FROZEN",
        )
        self.assertEqual(
            report["legacy_v20_quarantine"]["CLI_exit_code"], 2
        )
        self.assertFalse(
            report["legacy_v20_quarantine"]["CLI_writes_files"]
        )
        self.assertTrue(
            report["legacy_v20_quarantine"][
                "public_report_render_write_entrypoints_disabled"
            ]
        )
        self.assertEqual(report["inventory_count"], len(report["inventory"]))
        self.assertEqual(
            report["publication_manifest_raw_sha256"],
            freezer.PUBLICATION_MANIFEST_SHA256,
        )
        self.assertEqual(
            report["logical_pins"][
                "global_Phi_classification_source_raw_sha256"
            ],
            "17038c6fb82ba565a16228f5f5c03026f0ab8e3ad7959792498c2785b9653066",
        )
        self.assertEqual(
            report["logical_pins"]["global_Phi_classification_core_sha256"],
            "db493a74303a57862f09c2a92118ea3d66b8b12ecbaea9162155d4ab3baafecc",
        )
        self.assertEqual(
            report["logical_pins"]["EFT_O6_current_endomorphism_core_sha256"],
            freezer.EFT_O6_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"]["EFT_global_G3_theorem_core_sha256"],
            freezer.EFT_GLOBAL_G3_THEOREM_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"]["EFT_G3_acceptance_gate_core_sha256"],
            freezer.EFT_G3_ACCEPTANCE_GATE_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"][
                "EFT_beta_zero_base_Hessian_payload_sha256"
            ],
            freezer.EFT_BETA_ZERO_BASE_HESSIAN_PAYLOAD_SHA256,
        )
        self.assertEqual(
            report["logical_pins"]["EFT_stabilized_Hessian_payload_sha256"],
            freezer.EFT_STABILIZED_HESSIAN_PAYLOAD_SHA256,
        )
        self.assertEqual(
            report["logical_pins"]["EFT_G4_mathematical_gate_core_sha256"],
            freezer.EFT_G4_MATHEMATICAL_GATE_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"]["EFT_G5_mathematical_gate_core_sha256"],
            freezer.EFT_G5_MATHEMATICAL_GATE_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"]["EFT_G5_exact_global_lower_bound"],
            freezer.EFT_G5_EXACT_GLOBAL_LOWER_BOUND,
        )
        self.assertEqual(
            report["logical_pins"]["EFT_G6_spectrum_core_sha256"],
            freezer.EFT_G6_SPECTRUM_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"]["EFT_G6_mathematical_gate_core_sha256"],
            freezer.EFT_G6_MATHEMATICAL_GATE_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"][
                "renormalizable_G1_component_tensor_core_sha256"
            ],
            freezer.RENORMALIZABLE_G1_COMPONENT_TENSOR_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"]["renormalizable_G2_mathematical_core_sha256"],
            freezer.RENORMALIZABLE_G2_MATHEMATICAL_CORE_SHA256,
        )
        self.assertEqual(report["EFT_G3_bundle"]["raw_file_count"], 13)
        self.assertTrue(report["EFT_G3_bundle"]["all_checks_pass"])
        self.assertEqual(
            report["EFT_G3_bundle"]["theorem_adapter_allowlist"][
                "allowlisted_difference_count"
            ],
            2,
        )
        self.assertEqual(report["EFT_G4_G5_bundle"]["raw_file_count"], 8)
        self.assertTrue(report["EFT_G4_G5_bundle"]["all_checks_pass"])
        self.assertTrue(all(report["EFT_G4_G5_bundle"]["checks"].values()))
        self.assertEqual(report["EFT_G6_bundle"]["raw_file_count"], 8)
        self.assertTrue(report["EFT_G6_bundle"]["all_checks_pass"])
        self.assertTrue(all(report["EFT_G6_bundle"]["checks"].values()))
        self.assertEqual(
            report["renormalizable_G1_component_tensor_bundle"][
                "raw_file_count"
            ],
            4,
        )
        self.assertTrue(
            report["renormalizable_G1_component_tensor_bundle"][
                "all_checks_pass"
            ]
        )
        self.assertEqual(
            report["renormalizable_G2_mathematical_bundle"]["raw_file_count"],
            4,
        )
        self.assertTrue(
            report["renormalizable_G2_mathematical_bundle"]["all_checks_pass"]
        )
        self.assertEqual(
            report["workflow_contract"],
            {
                "corrected_assertion_heredocs": 7,
                "legacy_rejection_assertions": 7,
                "full_source_rebuild_invocations": 1,
                "read_only_frozen_dependency_orchestrators": 3,
                "read_only_frozen_report_sources": 20,
                "read_only_frozen_report_commands": 60,
                "no_write_frozen_classification_sources": 3,
                "no_write_frozen_classification_commands": 9,
                "no_write_stochastic_report_orchestrators": 2,
                "no_write_stochastic_report_commands": 3,
            },
        )
        self.assertTrue(
            report["claim_boundary"]["arbitrary_real_Phi_at_fixed_endpoint"]
        )
        self.assertTrue(
            report["claim_boundary"][
                "all_PD_equality_orbits_classified_exactly"
            ]
        )
        self.assertTrue(
            report["claim_boundary"][
                "global_signed_kaehler_Phi_self_zero_classification_proved"
            ]
        )
        self.assertTrue(
            report["claim_boundary"][
                "Dynkin_maximal_subgroup_classification_external_dependency"
            ]
        )
        self.assertFalse(report["claim_boundary"]["renormalizable_G3_closed"])
        self.assertTrue(
            report["claim_boundary"]["EFT_dimension6_mathematical_G3_closed"]
        )
        self.assertFalse(
            report["claim_boundary"]["EFT_release_G3_verified"]
        )
        self.assertFalse(report["claim_boundary"]["G4_closed"])
        self.assertFalse(
            report["claim_boundary"]["renormalizable_G4_closed"]
        )
        self.assertTrue(
            report["claim_boundary"]["EFT_dimension6_mathematical_G4_closed"]
        )
        self.assertFalse(
            report["claim_boundary"]["EFT_release_G4_verified"]
        )
        self.assertFalse(
            report["claim_boundary"]["renormalizable_G5_closed"]
        )
        self.assertTrue(
            report["claim_boundary"]["EFT_dimension6_mathematical_G5_closed"]
        )
        self.assertFalse(
            report["claim_boundary"]["EFT_release_G5_verified"]
        )
        self.assertFalse(
            report["claim_boundary"]["authoritative_renormalizable_G6_closed"]
        )
        self.assertTrue(
            report["claim_boundary"][
                "EFT_dimension6_tree_level_mathematical_G6_closed"
            ]
        )
        self.assertFalse(
            report["claim_boundary"]["EFT_release_G6_verified"]
        )
        self.assertTrue(
            report["claim_boundary"]["renormalizable_mathematical_G1_closed"]
        )
        self.assertFalse(
            report["claim_boundary"]["authoritative_renormalizable_G1_closed"]
        )
        self.assertFalse(report["claim_boundary"]["release_G1_verified"])
        for name in (
            "quantitative_beta_global_coercivity_proved",
            "legacy_v20_physical_target_valid",
            "legacy_v20_primal_valid",
            "global_Sigma_proved",
            "general_H_proved",
            "full_H_proved",
            "full_Hessian_proved",
            "G3_closed",
        ):
            self.assertIs(report["claim_boundary"][name], False, name)

    def test_manifest_is_canonical_and_excludes_itself_and_quarantine(self) -> None:
        payload = freezer.MANIFEST.read_bytes()
        value = json.loads(payload.decode("utf-8"))
        self.assertEqual(payload, freezer._canonical_json_bytes(value))
        self.assertNotIn(freezer.MANIFEST_NAME, value["inventory"])
        for relative in freezer.QUARANTINED_SIGMA35_PATHS:
            self.assertNotIn(relative, value["inventory"])
        self.assertFalse(value["quarantine"]["touched_or_promoted"])

    def test_eft_raw_bundle_is_fully_inventoried(self) -> None:
        report = freezer.check_manifest()
        self.assertEqual(len(freezer.EFT_G3_RAW_PINS), 13)
        self.assertEqual(
            report["generation_source_pins"]["EFT_G3_raw_sha256"],
            dict(sorted(freezer.EFT_G3_RAW_PINS.items())),
        )
        for relative, expected in freezer.EFT_G3_RAW_PINS.items():
            row = report["inventory"][relative]
            self.assertEqual(row["hash_mode"], "raw")
            self.assertEqual(row["content_sha256"], expected)
            self.assertIn(relative, freezer.CHECKSUM_REQUIRED_PATHS)

        self.assertEqual(len(freezer.EFT_G4_G5_RAW_PINS), 8)
        self.assertEqual(
            report["generation_source_pins"]["EFT_G4_G5_raw_sha256"],
            dict(sorted(freezer.EFT_G4_G5_RAW_PINS.items())),
        )
        for relative, expected in freezer.EFT_G4_G5_RAW_PINS.items():
            row = report["inventory"][relative]
            self.assertEqual(row["hash_mode"], "raw")
            self.assertEqual(row["content_sha256"], expected)
            self.assertIn(relative, freezer.CHECKSUM_REQUIRED_PATHS)

        self.assertEqual(len(freezer.EFT_G6_RAW_PINS), 8)
        self.assertEqual(
            report["generation_source_pins"]["EFT_G6_raw_sha256"],
            dict(sorted(freezer.EFT_G6_RAW_PINS.items())),
        )
        for relative, expected in freezer.EFT_G6_RAW_PINS.items():
            row = report["inventory"][relative]
            self.assertEqual(row["hash_mode"], "raw")
            self.assertEqual(row["content_sha256"], expected)
            self.assertIn(relative, freezer.CHECKSUM_REQUIRED_PATHS)

        self.assertEqual(
            len(freezer.RENORMALIZABLE_G1_COMPONENT_TENSOR_RAW_PINS), 4
        )
        self.assertEqual(
            report["generation_source_pins"][
                "renormalizable_G1_component_tensor_raw_sha256"
            ],
            dict(
                sorted(
                    freezer.RENORMALIZABLE_G1_COMPONENT_TENSOR_RAW_PINS.items()
                )
            ),
        )
        for (
            relative,
            expected,
        ) in freezer.RENORMALIZABLE_G1_COMPONENT_TENSOR_RAW_PINS.items():
            row = report["inventory"][relative]
            self.assertEqual(row["hash_mode"], "raw")
            self.assertEqual(row["content_sha256"], expected)
            self.assertIn(relative, freezer.CHECKSUM_REQUIRED_PATHS)

        self.assertEqual(len(freezer.RENORMALIZABLE_G2_MATHEMATICAL_RAW_PINS), 4)
        self.assertEqual(
            report["generation_source_pins"][
                "renormalizable_G2_mathematical_raw_sha256"
            ],
            dict(sorted(freezer.RENORMALIZABLE_G2_MATHEMATICAL_RAW_PINS.items())),
        )
        for relative, expected in freezer.RENORMALIZABLE_G2_MATHEMATICAL_RAW_PINS.items():
            row = report["inventory"][relative]
            self.assertEqual(row["hash_mode"], "raw")
            self.assertEqual(row["content_sha256"], expected)
            self.assertIn(relative, freezer.CHECKSUM_REQUIRED_PATHS)

    def test_eft_adapter_allowlist_and_logical_bundle(self) -> None:
        bundle = freezer._require_eft_g3_bundle()
        self.assertTrue(bundle["all_checks_pass"])
        self.assertTrue(all(bundle["checks"].values()))
        self.assertEqual(
            bundle["theorem_adapter_allowlist"]["differences"],
            [
                "production core pin",
                "production-local equality-source raw pin",
            ],
        )

        with tempfile.TemporaryDirectory() as directory:
            root = freezer.Path(directory)
            names = (
                "FROZEN_EXACT_EFT_CURRENT_KERNEL_STABILIZED_GLOBAL_G3_SOURCE_V20.py",
                "exact_gauged_u1x_g3_su5_eft_current_kernel_stabilized_global_v20.py",
            )
            for name in names:
                (root / name).write_bytes((freezer.ROOT / name).read_bytes())
            with patch.object(freezer, "ROOT", root):
                self.assertTrue(
                    freezer._require_eft_theorem_adapter_allowlist()[
                        "all_other_bytes_identical"
                    ]
                )
                production = root / names[1]
                production.write_text(
                    production.read_text(encoding="utf-8")
                    + "\n# non-allowlisted mutation\n",
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                    ArithmeticError, "outside the two allowlisted"
                ):
                    freezer._require_eft_theorem_adapter_allowlist()

    def test_eft_g4_g5_logical_bundle(self) -> None:
        bundle = freezer._require_eft_g4_g5_bundle()
        self.assertEqual(bundle["raw_file_count"], 8)
        self.assertTrue(bundle["all_checks_pass"])
        self.assertTrue(all(bundle["checks"].values()))
        self.assertTrue(
            bundle["checks"]["G4_completed_integration_and_blockers_exact"]
        )
        self.assertTrue(
            bundle["checks"]["G5_completed_integration_and_blockers_exact"]
        )

        with tempfile.TemporaryDirectory() as directory:
            root = freezer.Path(directory)
            names = (
                "final_g4_eft_mathematical_gate_v20.py",
                "FINAL_G4_EFT_MATHEMATICAL_GATE_V20.json",
                "final_g5_eft_mathematical_gate_v20.py",
                "FINAL_G5_EFT_MATHEMATICAL_GATE_V20.json",
            )
            for name in names:
                (root / name).write_bytes((freezer.ROOT / name).read_bytes())
            with patch.object(freezer, "ROOT", root):
                self.assertTrue(
                    freezer._require_eft_g4_g5_bundle()["all_checks_pass"]
                )
                g4_report = root / "FINAL_G4_EFT_MATHEMATICAL_GATE_V20.json"
                mutated = json.loads(g4_report.read_text(encoding="utf-8"))
                mutated["classification"][
                    "mathematical_G4_closed_for_EFT_model"
                ] = False
                g4_report.write_text(
                    json.dumps(mutated, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                    ArithmeticError, "frozen EFT G4/G5 logical bundle drifted"
                ):
                    freezer._require_eft_g4_g5_bundle()

        self._assert_eft_g6_logical_bundle_and_claim_boundary()
        self._assert_renormalizable_g1_component_tensor_bundle()
        self._assert_renormalizable_g2_mathematical_bundle()

    def _assert_eft_g6_logical_bundle_and_claim_boundary(self) -> None:
        bundle = freezer._require_eft_g6_bundle()
        self.assertEqual(bundle["raw_file_count"], 8)
        self.assertTrue(bundle["all_checks_pass"])
        self.assertTrue(all(bundle["checks"].values()))
        self.assertTrue(bundle["checks"]["complete_exact_positive_factorization"])
        self.assertTrue(bundle["checks"]["SU3C_U1em_provenance_exact"])
        self.assertTrue(bundle["checks"]["exact_algebraic_mixing_complete"])
        self.assertTrue(bundle["checks"]["physical_quotient_and_PQ_axion_exact"])
        self.assertTrue(
            bundle["checks"]["gate_completed_integration_and_blockers_exact"]
        )

        with tempfile.TemporaryDirectory() as directory:
            root = freezer.Path(directory)
            names = (
                "exact_eft_physical_scalar_spectrum_v20.py",
                "EXACT_EFT_PHYSICAL_SCALAR_SPECTRUM_V20.json",
                "final_g6_eft_mathematical_gate_v20.py",
                "FINAL_G6_EFT_MATHEMATICAL_GATE_V20.json",
            )
            for name in names:
                (root / name).write_bytes((freezer.ROOT / name).read_bytes())
            with patch.object(freezer, "ROOT", root):
                self.assertTrue(freezer._require_eft_g6_bundle()["all_checks_pass"])
                spectrum_report = (
                    root / "EXACT_EFT_PHYSICAL_SCALAR_SPECTRUM_V20.json"
                )
                mutated = json.loads(spectrum_report.read_text(encoding="utf-8"))
                mutated["physical_quotient"]["physical_PQ_axion_count"] = 0
                spectrum_report.write_text(
                    json.dumps(mutated, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                    ArithmeticError, "frozen EFT G6 logical bundle drifted"
                ):
                    freezer._require_eft_g6_bundle()

    def _assert_renormalizable_g1_component_tensor_bundle(self) -> None:
        bundle = freezer._require_renormalizable_g1_component_tensor_bundle()
        self.assertEqual(bundle["raw_file_count"], 4)
        self.assertTrue(bundle["all_checks_pass"])
        self.assertTrue(all(bundle["checks"].values()))
        self.assertTrue(bundle["checks"]["complete_28_44_51_tensor_ring_exact"])
        self.assertTrue(bundle["checks"]["central_integration_completed_exact"])
        self.assertTrue(
            bundle["checks"][
                "authoritative_and_release_claims_remain_fail_closed"
            ]
        )

        with tempfile.TemporaryDirectory() as directory:
            root = freezer.Path(directory)
            names = (
                "exact_gauged_u1x_g1_component_tensor_closure_v20.py",
                "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.json",
            )
            for name in names:
                (root / name).write_bytes((freezer.ROOT / name).read_bytes())
            with patch.object(freezer, "ROOT", root):
                self.assertTrue(
                    freezer._require_renormalizable_g1_component_tensor_bundle()[
                        "all_checks_pass"
                    ]
                )
                report_path = (
                    root
                    / "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.json"
                )
                mutated = json.loads(report_path.read_text(encoding="utf-8"))
                mutated["classification"]["authoritative_G1_promoted_closed"] = True
                report_path.write_text(
                    json.dumps(mutated, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                    ArithmeticError,
                    "frozen renormalizable G1 component-tensor logical bundle drifted",
                ):
                    freezer._require_renormalizable_g1_component_tensor_bundle()

    def _assert_renormalizable_g2_mathematical_bundle(self) -> None:
        bundle = freezer._require_renormalizable_g2_mathematical_bundle()
        self.assertEqual(bundle["raw_file_count"], 4)
        self.assertTrue(bundle["all_checks_pass"])
        self.assertTrue(all(bundle["checks"].values()))
        self.assertTrue(
            bundle["checks"]["complete_44_51_18_486_projected_potential_exact"]
        )
        self.assertTrue(bundle["checks"]["central_integration_completed_exact"])
        self.assertTrue(
            bundle["checks"][
                "authoritative_and_release_claims_remain_fail_closed"
            ]
        )

        with tempfile.TemporaryDirectory() as directory:
            root = freezer.Path(directory)
            names = (
                "exact_gauged_u1x_g2_mathematical_closure_v20.py",
                "EXACT_GAUGED_U1X_G2_MATHEMATICAL_CLOSURE_V20.json",
            )
            for name in names:
                (root / name).write_bytes((freezer.ROOT / name).read_bytes())
            with patch.object(freezer, "ROOT", root):
                self.assertTrue(
                    freezer._require_renormalizable_g2_mathematical_bundle()[
                        "all_checks_pass"
                    ]
                )
                report_path = (
                    root / "EXACT_GAUGED_U1X_G2_MATHEMATICAL_CLOSURE_V20.json"
                )
                mutated = json.loads(report_path.read_text(encoding="utf-8"))
                mutated["classification"]["authoritative_G2_promoted_closed"] = True
                report_path.write_text(
                    json.dumps(mutated, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                    ArithmeticError,
                    "frozen renormalizable G2 mathematical logical bundle drifted",
                ):
                    freezer._require_renormalizable_g2_mathematical_bundle()

    def test_release_checksum_binds_adapter_regressions_and_workflows(self) -> None:
        lines = (freezer.ROOT / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
        names = {line.split("  ", 1)[1] for line in lines}
        for relative in freezer.CHECKSUM_REQUIRED_PATHS:
            self.assertIn(relative, names)
        self.assertNotIn(freezer.MANIFEST_NAME, names)

    def test_external_freeze_identifier_is_raw_manifest_sha256(self) -> None:
        digest = hashlib.sha256(freezer.MANIFEST.read_bytes()).hexdigest()
        self.assertRegex(digest, r"^[0-9a-f]{64}$")
        self.assertEqual(len(digest), 64)

    def test_mutating_frozen_dependency_commands_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = freezer.Path(directory)
            relative_paths = (
                *freezer.WORKFLOW_PATHS,
                *freezer.READ_ONLY_FROZEN_DEPENDENCY_ORCHESTRATORS,
            )
            for relative in relative_paths:
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((freezer.ROOT / relative).read_bytes())

            replicate = root / "replicate.py"
            baseline_replicate = replicate.read_text(encoding="utf-8")
            needle = (
                '"exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py",\n'
                "        ]"
            )
            replacement = (
                '"exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py",\n'
                '            "--write",\n'
                "        ]"
            )
            self.assertIn(needle, baseline_replicate)

            with patch.object(freezer, "ROOT", root):
                self.assertEqual(
                    freezer._require_workflow_contract()[
                        "read_only_frozen_dependency_orchestrators"
                    ],
                    3,
                )
                replicate.write_text(
                    baseline_replicate.replace(needle, replacement, 1),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                    ArithmeticError, "rewrites the frozen stabilizer dependency"
                ):
                    freezer._require_workflow_contract()

                replicate.write_text(baseline_replicate, encoding="utf-8")
                report_needle = (
                    'run([sys.executable, '
                    '"gauged_u1x_g2_derivative_audit_v20.py"])'
                )
                report_replacement = (
                    'run([sys.executable, '
                    '"gauged_u1x_g2_derivative_audit_v20.py", "--write"])'
                )
                self.assertIn(report_needle, baseline_replicate)
                replicate.write_text(
                    baseline_replicate.replace(
                        report_needle, report_replacement, 1
                    ),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                    ArithmeticError,
                    "rewrites a frozen validation report",
                ):
                    freezer._require_workflow_contract()

                replicate.write_text(baseline_replicate, encoding="utf-8")
                eft_needle = (
                    '            "exact_gauged_u1x_g3_su5_eft_current_kernel_'
                    'stabilized_global_v20.py",\n'
                    "        ]"
                )
                eft_replacement = (
                    '            "exact_gauged_u1x_g3_su5_eft_current_kernel_'
                    'stabilized_global_v20.py",\n'
                    '            "--write",\n'
                    "        ]"
                )
                self.assertIn(eft_needle, baseline_replicate)
                replicate.write_text(
                    baseline_replicate.replace(
                        eft_needle, eft_replacement, 1
                    ),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                    ArithmeticError,
                    "rewrites a frozen validation report",
                ):
                    freezer._require_workflow_contract()

                replicate.write_text(baseline_replicate, encoding="utf-8")
                for source in (
                    "final_g4_eft_mathematical_gate_v20.py",
                    "final_g5_eft_mathematical_gate_v20.py",
                ):
                    report_needle = f'run([sys.executable, "{source}"])'
                    report_replacement = (
                        f'run([sys.executable, "{source}", "--write"])'
                    )
                    self.assertIn(report_needle, baseline_replicate)
                    replicate.write_text(
                        baseline_replicate.replace(
                            report_needle, report_replacement, 1
                        ),
                        encoding="utf-8",
                    )
                    with self.assertRaisesRegex(
                        ArithmeticError,
                        "rewrites a frozen validation report",
                    ):
                        freezer._require_workflow_contract()
                    replicate.write_text(
                        baseline_replicate, encoding="utf-8"
                    )

                classification_needle = (
                    '            "theory_validation_matrix_v20.py",\n'
                    '            "--expect-blocked",\n'
                    '            "--no-write",'
                )
                classification_replacement = (
                    '            "theory_validation_matrix_v20.py",\n'
                    '            "--expect-blocked",'
                )
                self.assertIn(classification_needle, baseline_replicate)
                replicate.write_text(
                    baseline_replicate.replace(
                        classification_needle, classification_replacement, 1
                    ),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                    ArithmeticError,
                    "rewrites a frozen classification report",
                ):
                    freezer._require_workflow_contract()

                replicate.write_text(baseline_replicate, encoding="utf-8")
                stochastic_needle = (
                    'run([sys.executable, "global_flavour_fit_v20.py", '
                    '"--no-write"])'
                )
                stochastic_replacement = (
                    'run([sys.executable, "global_flavour_fit_v20.py"])'
                )
                self.assertIn(stochastic_needle, baseline_replicate)
                replicate.write_text(
                    baseline_replicate.replace(
                        stochastic_needle, stochastic_replacement, 1
                    ),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                    ArithmeticError,
                    "rewrites the stochastic frozen report",
                ):
                    freezer._require_workflow_contract()

                replicate.write_text(baseline_replicate, encoding="utf-8")
                workflow = root / freezer.WORKFLOW_PATHS[0]
                workflow.write_text(
                    workflow.read_text(encoding="utf-8")
                    + "\nrun: python -B  "
                    + freezer.FROZEN_STABILIZER_SOURCE
                    + "   --write\n",
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                    ArithmeticError, "workflow rewrites the frozen stabilizer"
                ):
                    freezer._require_workflow_contract()


if __name__ == "__main__":
    unittest.main()
