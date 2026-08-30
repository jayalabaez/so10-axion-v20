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
            report["logical_pins"][
                "legacy_EFT_G6_formal_spectrum_core_sha256"
            ],
            freezer.LEGACY_EFT_G6_FORMAL_SPECTRUM_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"]["G6_SM_provenance_core_sha256"],
            freezer.G6_SM_PROVENANCE_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"][
                "EFT_G6_G7_parameterized_matching_core_sha256"
            ],
            freezer.EFT_G6_G7_PARAMETERIZED_MATCHING_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"]["EFT_G6_formal_gate_core_sha256"],
            freezer.EFT_G6_FORMAL_GATE_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"][
                "authoritative_SO10_U1X_gauge_betas_core_sha256"
            ],
            freezer.AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"][
                "PyRATE3_SO10_U1X_gauge_beta_replay_core_sha256"
            ],
            freezer.PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"][
                "EFT_G7_formal_U1_89_restriction_core_sha256"
            ],
            freezer.EFT_G7_FORMAL_RESTRICTION_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"][
                "physical_G7_component_threshold_core_sha256"
            ],
            freezer.PHYSICAL_G7_COMPONENT_THRESHOLD_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"]["normalized_SO10_Yukawa_CGC_core_sha256"],
            freezer.NORMALIZED_YUKAWA_CGCS_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"]["physical_SM_vacuum_core_sha256"],
            freezer.PHYSICAL_SM_VACUUM_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"][
                "conditional_physical_SM_EFT_Hessian_spectrum_core_sha256"
            ],
            freezer.CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"][
                "physical_SM_heavy_vector_masses_core_sha256"
            ],
            freezer.PHYSICAL_SM_HEAVY_VECTOR_MASSES_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"][
                "physical_SM_heavy_vector_MSbar_matching_core_sha256"
            ],
            freezer.PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"]["physical_SM_vector_Rxi_core_sha256"],
            freezer.PHYSICAL_SM_VECTOR_RXI_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"]["physical_SM_G6_G7_frontier_core_sha256"],
            freezer.PHYSICAL_SM_G6_G7_FRONTIER_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"]["physical_SM_G8_frontier_core_sha256"],
            freezer.PHYSICAL_SM_G8_FRONTIER_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"]["canonical_G1_G8_v21_definition_sha256"],
            freezer.CANONICAL_G1_G8_V21_DEFINITION_SHA256,
        )
        self.assertEqual(
            report["logical_pins"]["canonical_G1_G8_v21_core_sha256"],
            freezer.CANONICAL_G1_G8_V21_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"][
                "physical_SM_source_equality_frontier_core_sha256"
            ],
            freezer.PHYSICAL_SM_SOURCE_EQUALITY_FRONTIER_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"][
                "physical_SM_five_amplitude_equality_core_sha256"
            ],
            freezer.PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_CORE_SHA256,
        )
        self.assertEqual(
            report["logical_pins"][
                "exact_X_v3_trusted_SARAH_tree_core_sha256"
            ],
            freezer.EXACT_X_V3_TRUSTED_SARAH_TREE_CORE_SHA256,
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
        self.assertEqual(report["EFT_G6_truth_bundle"]["raw_file_count"], 16)
        self.assertTrue(report["EFT_G6_truth_bundle"]["all_checks_pass"])
        self.assertTrue(all(report["EFT_G6_truth_bundle"]["checks"].values()))
        self.assertEqual(report["EFT_G7_truth_bundle"]["raw_file_count"], 18)
        self.assertTrue(report["EFT_G7_truth_bundle"]["all_checks_pass"])
        self.assertTrue(all(report["EFT_G7_truth_bundle"]["checks"].values()))
        for key in (
            "normalized_SO10_Yukawa_CGC_truth_bundle",
            "physical_SM_vacuum_truth_bundle",
            "conditional_physical_SM_EFT_Hessian_spectrum_bundle",
            "physical_SM_heavy_vector_mass_bundle",
            "physical_SM_heavy_vector_MSbar_matching_bundle",
            "physical_SM_vector_Rxi_bundle",
            "physical_SM_G6_G7_frontier_bundle",
            "physical_SM_G8_frontier_bundle",
            "physical_SM_source_equality_frontier_bundle",
        ):
            self.assertEqual(report[key]["raw_file_count"], 4)
            self.assertTrue(report[key]["all_checks_pass"])
            self.assertTrue(all(report[key]["checks"].values()))
        five = report["physical_SM_five_amplitude_equality_bundle"]
        self.assertEqual(five["raw_file_count"], 4)
        self.assertEqual(five["transitive_portable_source_count"], 14)
        self.assertTrue(five["all_checks_pass"])
        self.assertFalse(five["full_486_equality_classified"])
        canonical = report["canonical_G1_G8_v21_bundle"]
        self.assertEqual(canonical["portable_file_count"], 4)
        self.assertEqual(canonical["qualified_gate_count"], 8)
        self.assertEqual(canonical["acceptance_criterion_count"], 33)
        self.assertTrue(canonical["closure_capable_contract_and_regression_test_frozen"])
        self.assertEqual(canonical["current_closed_gate_count"], 3)
        self.assertEqual(canonical["current_open_gate_count"], 5)
        self.assertTrue(canonical["canonical_G1_closed"])
        self.assertTrue(canonical["canonical_G2_closed"])
        self.assertTrue(canonical["canonical_G3_closed"])
        self.assertFalse(canonical["all_canonical_gates_closed"])
        self.assertFalse(canonical["whole_model_validated"])
        self.assertTrue(canonical["all_checks_pass"])
        exact_x = report["exact_X_v3_fail_closed_bundle"]
        self.assertEqual(exact_x["raw_file_count"], 9)
        self.assertEqual(exact_x["portable_file_count"], 2)
        self.assertTrue(exact_x["all_checks_pass"])
        self.assertTrue(exact_x["external_v3_execution_attestation_present"])
        self.assertTrue(exact_x["external_v3_execution_attestation_valid"])
        self.assertTrue(exact_x["authoritative_exact_X_contract_closed"])
        g1 = report["canonical_G1_dim6_bundle"]
        self.assertEqual(g1["portable_file_count"], 12)
        self.assertEqual(g1["neutral_field_content_sector_count"], 168)
        self.assertEqual(g1["real_potential_coefficient_count"], 891)
        self.assertTrue(g1["canonical_G1_closed"])
        g2 = report["canonical_G2_dim6_bundle"]
        self.assertEqual(g2["portable_file_count"], 11)
        self.assertEqual(g2["non_singlet_sector_count"], 105)
        self.assertEqual(g2["non_singlet_direction_count"], 794)
        self.assertEqual(g2["neutral_G1_sector_count"], 168)
        self.assertEqual(g2["canonical_direction_count"], 891)
        self.assertTrue(g2["canonical_G2_closed"])
        self.assertTrue(g2["all_checks_pass"])
        g3 = report["canonical_G3_global_vacuum_bundle"]
        self.assertEqual(g3["portable_file_count"], 6)
        self.assertEqual((g3["exact_rank"], g3["exact_nullity"]), (448, 38))
        self.assertTrue(g3["canonical_G3_closed"])
        self.assertFalse(g3["canonical_G4_closed"])
        self.assertTrue(g3["all_checks_pass"])
        legacy = report["legacy_SO10_210_beta_diagnostic_bundle"]
        self.assertEqual(legacy["raw_report_count"], 2)
        self.assertTrue(legacy["all_checks_pass"])
        self.assertTrue(all(legacy["checks"].values()))
        self.assertFalse(legacy["live_SARAH_or_PyRATE_execution_attested"])
        self.assertFalse(legacy["unique_physical_mathematical_release_G7_closed"])
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
        expected_read_only_report_sources = len(
            freezer.READ_ONLY_FROZEN_REPORT_SOURCES
        )
        expected_read_only_report_commands = (
            expected_read_only_report_sources
            * len(freezer.READ_ONLY_FROZEN_DEPENDENCY_ORCHESTRATORS)
        )
        self.assertEqual(expected_read_only_report_sources, 46)
        self.assertEqual(expected_read_only_report_commands, 138)
        self.assertEqual(
            report["workflow_contract"],
            {
                "corrected_assertion_heredocs": 7,
                "legacy_rejection_assertions": 7,
                "full_source_rebuild_invocations": 1,
                "read_only_frozen_dependency_orchestrators": 3,
                "read_only_frozen_report_sources": (
                    expected_read_only_report_sources
                ),
                "read_only_frozen_report_commands": (
                    expected_read_only_report_commands
                ),
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
        self.assertFalse(
            report["claim_boundary"][
                "EFT_dimension6_tree_level_mathematical_G6_closed"
            ]
        )
        self.assertTrue(
            report["claim_boundary"][
                "formal_SU3_x_U1_89_tree_mass_factorization_closed"
            ]
        )
        self.assertFalse(
            report["claim_boundary"]["mathematical_physical_G6_closed"]
        )
        self.assertFalse(
            report["claim_boundary"][
                "legacy_G6_spectrum_embedded_U1em_label_valid"
            ]
        )
        self.assertFalse(
            report["claim_boundary"]["EFT_release_G6_verified"]
        )
        self.assertTrue(
            report["claim_boundary"][
                "formal_U1_89_abstract_restriction_noninjectivity_proved"
            ]
        )
        self.assertFalse(
            report["claim_boundary"][
                "exact_physical_EFT_G7_input_nonidentifiability_proved"
            ]
        )
        self.assertFalse(
            report["claim_boundary"][
                "historical_electroweak_lift_interpretation_valid"
            ]
        )
        self.assertTrue(
            report["claim_boundary"][
                "exact_nonyukawa_two_loop_gauge_polynomial_closed"
            ]
        )
        self.assertTrue(
            report["claim_boundary"][
                "independent_gauge_only_PyRATE3_replay_closed"
            ]
        )
        self.assertFalse(
            report["claim_boundary"]["EFT_mathematical_G7_closed"]
        )
        self.assertFalse(report["claim_boundary"]["EFT_release_G7_verified"])
        self.assertFalse(
            report["claim_boundary"][
                "authoritative_renormalizable_G7_closed"
            ]
        )
        self.assertFalse(report["claim_boundary"]["positive_G7_certified"])
        self.assertFalse(
            report["claim_boundary"]["negative_G7_no_go_certified"]
        )
        self.assertTrue(
            report["claim_boundary"]["renormalizable_mathematical_G1_closed"]
        )
        self.assertTrue(
            report["claim_boundary"]["authoritative_renormalizable_G1_closed"]
        )
        self.assertTrue(report["claim_boundary"]["release_G1_verified"])
        for name in (
            "normalized_SO10_representation_Yukawa_CGCs_closed",
            "physical_SM_target_and_standard_stabilizer_constructed",
            "old_selected_EFT_U1em_label_superseded_by_U1_89",
            "conditional_reconstructed_physical_SM_tree_scalar_spectrum_closed",
            "physical_SM_tree_vector_mass_matrix_parameterized_closed",
            "physical_SM_unbroken_group_vector_threshold_logs_parameterized_closed",
            "physical_SM_radial_stationary_equality_classified_exactly",
            "physical_SM_five_amplitude_stationary_equality_classified_exactly",
            "exact_X_v3_static_native_contract_closed",
            "exact_X_v3_trusted_SARAH_tree_manifest_closed",
            "zero_background_arbitrary_positive_Rxi_vacuum_determinant_cancellation_closed",
            "all_37_broken_vector_directions_Rxi_cancelled",
            "continuous_G6_G7_nonidentifiability_proved",
            "canonical_G8_contract_audited",
            "canonical_G1_G8_v21_contract_frozen",
            "canonical_G1_G8_v21_closure_capable",
            "canonical_G3_physical_EW_global_vacuum_closed",
            "continuous_absolute_scale_G8_nonidentifiability_proved",
            "flavor_and_interference_G8_nonidentifiability_audited",
            "exact_101_case_G8_scale_audit_closed",
            "repository_frozen_PDG_2025_single_channel_constraint_verified",
        ):
            self.assertIs(report["claim_boundary"][name], True, name)
        for name in (
            "flavor_tensor_values_and_textures_closed",
            "full_one_two_loop_Yukawa_betas_closed",
            "physical_SM_G3_closed",
            "physical_SM_G4_closed",
            "physical_SM_G5_closed",
            "source_bound_physical_SM_tree_scalar_spectrum_closed",
            "absolute_physical_heavy_vector_masses_closed",
            "physical_scalar_pole_spectrum_closed",
            "physical_G6_closed",
            "physical_SM_direct_source_algebra_Hessian_closed",
            "physical_SM_complete_global_equality_orbit_closed",
            "physical_SM_five_amplitude_full_486_equality_classified",
            "physical_SM_five_amplitude_continuous_orbit_equivalence_classified",
            "physical_SM_five_amplitude_direct_source_algebra_Hessian_closed",
            "background_covariant_general_field_Rxi_determinants_closed",
            "background_covariant_heat_kernel_replay_closed",
            "unique_absolute_tree_spectrum_identified",
            "unique_pole_spectrum_identified",
            "unique_threshold_vector_identified",
            "unique_full_RGE_trajectory_identified",
            "unique_proton_lifetime_or_distribution_identified",
            "all_G8_acceptance_criteria_pass",
            "physical_G8_closed",
            "release_G8_verified",
            "authoritative_G8_closed",
            "whole_model_excluded_by_conditional_G8_points",
            "canonical_G1_G8_v21_all_gates_closed",
            "canonical_G1_G8_v21_whole_model_validated",
            "legacy_bare_gate_numbers_authoritative",
        ):
            self.assertIs(report["claim_boundary"][name], False, name)
        self.assertIs(
            report["claim_boundary"][
                "exact_X_v3_external_execution_attestation_present"
            ],
            True,
        )
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

    def test_canonical_g1_g8_v21_bundle_is_frozen_and_fail_closed(self) -> None:
        bundle = freezer._require_canonical_g1_g8_v21_bundle()
        self.assertTrue(bundle["all_checks_pass"])
        self.assertTrue(all(bundle["checks"].values()))
        self.assertEqual(bundle["contract_namespace"], freezer.CANONICAL_G1_G8_V21_NAMESPACE)
        self.assertEqual(bundle["definition_sha256"], freezer.CANONICAL_G1_G8_V21_DEFINITION_SHA256)
        self.assertEqual(bundle["core_sha256"], freezer.CANONICAL_G1_G8_V21_CORE_SHA256)
        self.assertEqual(bundle["current_closed_gate_count"], 3)
        self.assertEqual(bundle["current_open_gate_count"], 5)
        self.assertTrue(bundle["canonical_G1_closed"])
        self.assertTrue(bundle["canonical_G2_closed"])
        self.assertTrue(bundle["canonical_G3_closed"])
        self.assertFalse(bundle["whole_model_validated"])
        canonical_report = json.loads(
            (
                freezer.ROOT / "CANONICAL_G1_G8_GAUGED_U1X_V21.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(canonical_report["n_checks"], 10)
        self.assertTrue(
            canonical_report["checks"][
                "trusted_verifier_slots_are_unique_and_fail_closed"
            ]
        )
        self.assertEqual(
            [gate["trusted_verifier"] for gate in canonical_report["gates"]],
            [
                {
                    "path": path,
                    "mode": "raw",
                    "protocol": freezer.CANONICAL_G1_G8_V21_VERIFIER_PROTOCOL,
                    "sha256": (
                        freezer.CANONICAL_G1_TRUSTED_VERIFIER_SHA256
                        if index == 0
                        else (
                            freezer.CANONICAL_G2_TRUSTED_VERIFIER_SHA256
                            if index == 1
                            else (
                                freezer.CANONICAL_G3_TRUSTED_VERIFIER_SHA256
                                if index == 2
                                else None
                            )
                        )
                    ),
                }
                for index, path in enumerate(
                    freezer.CANONICAL_G1_G8_V21_TRUSTED_VERIFIER_PATHS
                )
            ],
        )

        report_name = "CANONICAL_G1_G8_GAUGED_U1X_V21.json"
        with tempfile.TemporaryDirectory() as directory:
            root = freezer.Path(directory)
            for relative in freezer.CANONICAL_G1_G8_V21_PORTABLE_PINS:
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((freezer.ROOT / relative).read_bytes())
            for row in freezer.CANONICAL_G1_G8_V21_LEGACY_SOURCE_BINDINGS.values():
                destination = root / row["path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((freezer.ROOT / row["path"]).read_bytes())
            report_path = root / report_name
            mutated = json.loads(report_path.read_text(encoding="utf-8"))
            mutated["overall_state"] = "PASS"
            mutated["closure_counts"] = {"closed": 8, "open": 0}
            mutated["classification"]["all_canonical_gates_closed"] = True
            mutated["classification"]["whole_model_validated"] = True
            mutated_without_integrity = {
                key: value for key, value in mutated.items() if key != "integrity"
            }
            forged_core = hashlib.sha256(
                (
                    json.dumps(
                        mutated_without_integrity,
                        sort_keys=True,
                        separators=(",", ":"),
                        ensure_ascii=True,
                    )
                    + "\n"
                ).encode("utf-8")
            ).hexdigest()
            mutated["integrity"] = {"core_sha256": forged_core}
            report_path.write_text(
                json.dumps(mutated, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            forged = dict(freezer.CANONICAL_G1_G8_V21_PORTABLE_PINS)
            forged[report_name] = hashlib.sha256(
                report_path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
            ).hexdigest()
            with patch.object(freezer, "ROOT", root), patch.object(
                freezer, "CANONICAL_G1_G8_V21_PORTABLE_PINS", forged
            ), patch.object(
                freezer, "CANONICAL_G1_G8_V21_CORE_SHA256", forged_core
            ):
                with self.assertRaisesRegex(
                    ArithmeticError, "canonical G1--G8 v21 bundle drifted"
                ):
                    freezer._require_canonical_g1_g8_v21_bundle()

        with tempfile.TemporaryDirectory() as directory:
            root = freezer.Path(directory)
            for relative in freezer.CANONICAL_G1_G8_V21_PORTABLE_PINS:
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((freezer.ROOT / relative).read_bytes())
            for row in freezer.CANONICAL_G1_G8_V21_LEGACY_SOURCE_BINDINGS.values():
                destination = root / row["path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((freezer.ROOT / row["path"]).read_bytes())
            report_path = root / report_name
            mutated = json.loads(report_path.read_text(encoding="utf-8"))
            mutated["gates"][0]["trusted_verifier"]["sha256"] = "0" * 64
            mutated_without_integrity = {
                key: value for key, value in mutated.items() if key != "integrity"
            }
            forged_core = hashlib.sha256(
                (
                    json.dumps(
                        mutated_without_integrity,
                        sort_keys=True,
                        separators=(",", ":"),
                        ensure_ascii=True,
                    )
                    + "\n"
                ).encode("utf-8")
            ).hexdigest()
            mutated["integrity"] = {"core_sha256": forged_core}
            report_path.write_text(
                json.dumps(mutated, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            forged = dict(freezer.CANONICAL_G1_G8_V21_PORTABLE_PINS)
            forged[report_name] = hashlib.sha256(
                report_path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
            ).hexdigest()
            with patch.object(freezer, "ROOT", root), patch.object(
                freezer, "CANONICAL_G1_G8_V21_PORTABLE_PINS", forged
            ), patch.object(
                freezer, "CANONICAL_G1_G8_V21_CORE_SHA256", forged_core
            ):
                with self.assertRaisesRegex(
                    ArithmeticError, "canonical G1--G8 v21 bundle drifted"
                ):
                    freezer._require_canonical_g1_g8_v21_bundle()

        with tempfile.TemporaryDirectory() as directory:
            root = freezer.Path(directory)
            for relative in freezer.CANONICAL_G1_G8_V21_PORTABLE_PINS:
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((freezer.ROOT / relative).read_bytes())
            for row in freezer.CANONICAL_G1_G8_V21_LEGACY_SOURCE_BINDINGS.values():
                destination = root / row["path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((freezer.ROOT / row["path"]).read_bytes())
            ledger = root / "g1_g8_gate_ledger_v20.py"
            source = ledger.read_text(encoding="utf-8")
            needle = "Invariant ring and component Clebsch tensors"
            self.assertIn(needle, source)
            ledger.write_text(
                source.replace(needle, "Mutated legacy G1 title", 1),
                encoding="utf-8",
            )
            with patch.object(freezer, "ROOT", root):
                with self.assertRaisesRegex(
                    ArithmeticError, "canonical G1--G8 v21 bundle drifted"
                ):
                    freezer._require_canonical_g1_g8_v21_bundle()

        wrong_pins = dict(freezer.CANONICAL_G1_G8_V21_PORTABLE_PINS)
        wrong_pins["canonical_g1_g8_gauged_u1x_v21.py"] = "0" * 64
        with patch.object(
            freezer, "CANONICAL_G1_G8_V21_PORTABLE_PINS", wrong_pins
        ):
            with self.assertRaisesRegex(
                ArithmeticError, "canonical G1--G8 v21 bundle member drifted"
            ):
                freezer._require_source_pins()

    def test_canonical_g1_g8_v21_paths_are_portable_and_inventoried(self) -> None:
        report = freezer.check_manifest()
        self.assertEqual(
            report["generation_source_pins"][
                "canonical_G1_G8_v21_portable_lf_sha256"
            ],
            dict(sorted(freezer.CANONICAL_G1_G8_V21_PORTABLE_PINS.items())),
        )
        for relative, expected in freezer.CANONICAL_G1_G8_V21_PORTABLE_PINS.items():
            self.assertIn(relative, freezer.PORTABLE_INTEGRATION_PATHS)
            self.assertIn(relative, freezer.CHECKSUM_REQUIRED_PATHS)
            row = report["inventory"][relative]
            self.assertEqual(row["hash_mode"], "portable-lf")
            self.assertEqual(row["content_sha256"], expected)
            self.assertIn("canonical closure-capable", row["role"])
        self.assertEqual(
            report["generation_source_pins"][
                "canonical_G1_dim6_portable_lf_sha256"
            ],
            dict(sorted(freezer.CANONICAL_G1_DIM6_PORTABLE_PINS.items())),
        )
        for relative, expected in freezer.CANONICAL_G1_DIM6_PORTABLE_PINS.items():
            self.assertIn(relative, freezer.PORTABLE_INTEGRATION_PATHS)
            self.assertIn(relative, freezer.CHECKSUM_REQUIRED_PATHS)
            row = report["inventory"][relative]
            self.assertEqual(row["hash_mode"], "portable-lf")
            self.assertEqual(row["content_sha256"], expected)
            self.assertIn("canonical G1", row["role"])
        self.assertEqual(
            report["generation_source_pins"][
                "canonical_G3_global_vacuum_portable_lf_sha256"
            ],
            dict(sorted(freezer.CANONICAL_G3_GLOBAL_VACUUM_PORTABLE_PINS.items())),
        )
        for relative, expected in freezer.CANONICAL_G3_GLOBAL_VACUUM_PORTABLE_PINS.items():
            self.assertIn(relative, freezer.PORTABLE_INTEGRATION_PATHS)
            self.assertIn(relative, freezer.CHECKSUM_REQUIRED_PATHS)
            row = report["inventory"][relative]
            self.assertEqual(row["hash_mode"], "portable-lf")
            self.assertEqual(row["content_sha256"], expected)
            self.assertIn("canonical G3", row["role"])

    def test_canonical_g3_global_vacuum_bundle_is_exact_and_fail_closed(self) -> None:
        bundle = freezer._require_canonical_g3_global_vacuum_bundle()
        self.assertTrue(bundle["all_checks_pass"])
        self.assertTrue(all(bundle["checks"].values()))
        self.assertTrue(bundle["canonical_G3_closed"])
        self.assertFalse(bundle["canonical_G4_closed"])
        self.assertEqual(bundle["exact_value"], "-1")
        self.assertEqual((bundle["exact_rank"], bundle["exact_nullity"]), (448, 38))
        self.assertEqual(bundle["gauge_orbit_rank"], 37)
        wrong = dict(freezer.CANONICAL_G3_GLOBAL_VACUUM_PORTABLE_PINS)
        wrong["CANONICAL_G3_PHYSICAL_EW_GLOBAL_VACUUM_V21.json"] = "0" * 64
        with patch.object(freezer, "CANONICAL_G3_GLOBAL_VACUUM_PORTABLE_PINS", wrong):
            with self.assertRaisesRegex(ArithmeticError, "canonical G3 global-vacuum"):
                freezer._require_canonical_g3_global_vacuum_bundle()

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

        corrected_g6_g7_pin_bundles = (
            (
                "legacy_EFT_G6_formal_spectrum_raw_sha256",
                freezer.LEGACY_EFT_G6_FORMAL_SPECTRUM_RAW_PINS,
                4,
            ),
            (
                "G6_SM_provenance_raw_sha256",
                freezer.G6_SM_PROVENANCE_RAW_PINS,
                4,
            ),
            (
                "G6_SM_provenance_transitive_raw_sha256",
                freezer.G6_SM_PROVENANCE_TRANSITIVE_RAW_PINS,
                3,
            ),
            (
                "EFT_G6_G7_parameterized_matching_raw_sha256",
                freezer.EFT_G6_G7_PARAMETERIZED_MATCHING_RAW_PINS,
                4,
            ),
            (
                "EFT_G6_formal_gate_raw_sha256",
                freezer.EFT_G6_FORMAL_GATE_RAW_PINS,
                4,
            ),
            (
                "authoritative_SO10_U1X_gauge_betas_raw_sha256",
                freezer.AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_RAW_PINS,
                4,
            ),
            (
                "PyRATE3_SO10_U1X_gauge_beta_replay_raw_sha256",
                freezer.PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_RAW_PINS,
                6,
            ),
            (
                "EFT_G7_formal_U1_89_restriction_raw_sha256",
                freezer.EFT_G7_FORMAL_RESTRICTION_RAW_PINS,
                4,
            ),
            (
                "physical_G7_component_threshold_raw_sha256",
                freezer.PHYSICAL_G7_COMPONENT_THRESHOLD_RAW_PINS,
                4,
            ),
            (
                "normalized_SO10_Yukawa_CGC_raw_sha256",
                freezer.NORMALIZED_YUKAWA_CGCS_RAW_PINS,
                4,
            ),
            (
                "physical_SM_vacuum_raw_sha256",
                freezer.PHYSICAL_SM_VACUUM_RAW_PINS,
                4,
            ),
            (
                "physical_SM_vacuum_transitive_raw_sha256",
                freezer.PHYSICAL_SM_VACUUM_TRANSITIVE_RAW_PINS,
                11,
            ),
            (
                "conditional_physical_SM_EFT_Hessian_spectrum_raw_sha256",
                freezer.CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_RAW_PINS,
                4,
            ),
            (
                "physical_SM_heavy_vector_masses_raw_sha256",
                freezer.PHYSICAL_SM_HEAVY_VECTOR_MASSES_RAW_PINS,
                4,
            ),
            (
                "physical_SM_heavy_vector_MSbar_matching_raw_sha256",
                freezer.PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_RAW_PINS,
                4,
            ),
            (
                "physical_SM_vector_Rxi_raw_sha256",
                freezer.PHYSICAL_SM_VECTOR_RXI_RAW_PINS,
                4,
            ),
            (
                "physical_SM_G6_G7_frontier_raw_sha256",
                freezer.PHYSICAL_SM_G6_G7_FRONTIER_RAW_PINS,
                4,
            ),
            (
                "physical_SM_G8_frontier_raw_sha256",
                freezer.PHYSICAL_SM_G8_FRONTIER_RAW_PINS,
                4,
            ),
            (
                "physical_SM_source_equality_frontier_raw_sha256",
                freezer.PHYSICAL_SM_SOURCE_EQUALITY_FRONTIER_RAW_PINS,
                4,
            ),
            (
                "legacy_SO10_210_beta_diagnostic_raw_sha256",
                freezer.LEGACY_SO10_210_BETA_DIAGNOSTIC_RAW_PINS,
                2,
            ),
        )
        for manifest_key, pins, expected_count in corrected_g6_g7_pin_bundles:
            self.assertEqual(len(pins), expected_count)
            self.assertEqual(
                report["generation_source_pins"][manifest_key],
                dict(sorted(pins.items())),
            )
            for relative, expected in pins.items():
                row = report["inventory"][relative]
                self.assertEqual(row["hash_mode"], "raw")
                self.assertEqual(row["content_sha256"], expected)
                self.assertIn(relative, freezer.CHECKSUM_REQUIRED_PATHS)

        self.assertEqual(
            len(freezer.NORMALIZED_YUKAWA_CGCS_TRANSITIVE_PORTABLE_PINS), 2
        )
        self.assertEqual(
            report["generation_source_pins"][
                "normalized_SO10_Yukawa_CGC_transitive_portable_lf_sha256"
            ],
            dict(
                sorted(
                    freezer.NORMALIZED_YUKAWA_CGCS_TRANSITIVE_PORTABLE_PINS.items()
                )
            ),
        )
        for (
            relative,
            expected,
        ) in freezer.NORMALIZED_YUKAWA_CGCS_TRANSITIVE_PORTABLE_PINS.items():
            row = report["inventory"][relative]
            self.assertEqual(row["hash_mode"], "portable-lf")
            self.assertEqual(row["content_sha256"], expected)
            self.assertIn(relative, freezer.CHECKSUM_REQUIRED_PATHS)

        workflow = freezer.LEGACY_SO10_210_BETA_DIAGNOSTIC_WORKFLOW
        self.assertIn(workflow, freezer.PORTABLE_INTEGRATION_PATHS)
        self.assertIn(workflow, freezer.CHECKSUM_REQUIRED_PATHS)
        self.assertEqual(report["inventory"][workflow]["hash_mode"], "portable-lf")

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

        self._assert_eft_g6_truth_bundle_and_claim_boundary()
        self._assert_eft_g7_truth_bundle_and_claim_boundary()
        self._assert_new_physical_sm_and_yukawa_truth_bundles()
        self._assert_renormalizable_g1_component_tensor_bundle()
        self._assert_renormalizable_g2_mathematical_bundle()

    def _assert_eft_g6_truth_bundle_and_claim_boundary(self) -> None:
        bundle = freezer._require_eft_g6_truth_bundle()
        self.assertEqual(bundle["raw_file_count"], 16)
        self.assertTrue(bundle["all_checks_pass"])
        self.assertTrue(all(bundle["checks"].values()))
        self.assertTrue(bundle["checks"]["complete_exact_positive_factorization"])
        self.assertTrue(
            bundle["checks"][
                "legacy_embedded_U1em_label_recorded_only_for_explicit_override"
            ]
        )
        self.assertTrue(bundle["checks"]["exact_algebraic_mixing_complete"])
        self.assertTrue(
            bundle["checks"][
                "legacy_formal_kernel_and_PQ_zero_mode_census_exact"
            ]
        )
        self.assertTrue(
            bundle["checks"][
                "independent_true_SM_singlet_swap_fails_stationarity_and_stability"
            ]
        )
        self.assertTrue(
            bundle["checks"]["standard_electromagnetic_vacuum_noninvariance_exact"]
        )
        self.assertTrue(
            bundle["checks"]["gate_completed_integration_and_blockers_exact"]
        )
        self.assertFalse(bundle["legacy_spectrum_physical_interpretation_accepted"])
        self.assertFalse(bundle["mathematical_physical_G6_closed"])

        with tempfile.TemporaryDirectory() as directory:
            root = freezer.Path(directory)
            names = (
                "exact_eft_physical_scalar_spectrum_v20.py",
                "EXACT_EFT_PHYSICAL_SCALAR_SPECTRUM_V20.json",
                "exact_g6_sm_provenance_feasibility_v20.py",
                "EXACT_G6_SM_PROVENANCE_FEASIBILITY_V20.json",
                "exact_eft_g6_g7_parameterized_matching_v20.py",
                "EXACT_EFT_G6_G7_PARAMETERIZED_MATCHING_V20.json",
                "final_g6_eft_mathematical_gate_v20.py",
                "FINAL_G6_EFT_MATHEMATICAL_GATE_V20.json",
            )
            for name in names:
                (root / name).write_bytes((freezer.ROOT / name).read_bytes())
            with patch.object(freezer, "ROOT", root):
                self.assertTrue(
                    freezer._require_eft_g6_truth_bundle()["all_checks_pass"]
                )
                gate_report = root / "FINAL_G6_EFT_MATHEMATICAL_GATE_V20.json"
                mutated = json.loads(gate_report.read_text(encoding="utf-8"))
                mutated["classification"]["mathematical_physical_G6_closed"] = True
                gate_report.write_text(
                    json.dumps(mutated, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                    ArithmeticError, "corrected EFT G6 truth bundle drifted"
                ):
                    freezer._require_eft_g6_truth_bundle()

    def _assert_eft_g7_truth_bundle_and_claim_boundary(self) -> None:
        bundle = freezer._require_eft_g7_truth_bundle()
        self.assertEqual(bundle["raw_file_count"], 18)
        self.assertTrue(bundle["all_checks_pass"])
        self.assertTrue(all(bundle["checks"].values()))
        self.assertTrue(
            bundle["checks"][
                "formal_U1_89_abstract_restriction_noninjectivity_exact"
            ]
        )
        self.assertTrue(bundle["checks"]["absolute_scale_collision_exact"])
        self.assertTrue(
            bundle["checks"]["authoritative_gauge_only_coefficients_exact"]
        )
        self.assertTrue(
            bundle["checks"][
                "independent_PyRATE3_exact_match_scoped_fail_closed"
            ]
        )
        self.assertTrue(
            bundle["checks"][
                "physical_component_threshold_scoped_truth_exact"
            ]
        )
        self.assertTrue(bundle["physical_PS_SM_matter_branching_closed"])
        self.assertTrue(
            bundle["parameterized_one_loop_matter_threshold_kernel_closed"]
        )
        self.assertFalse(bundle["physical_G7_closed"])
        self.assertTrue(
            bundle["checks"]["claim_boundary_remains_fail_closed"]
        )
        self.assertTrue(bundle["checks"]["central_integration_complete_exact"])
        self.assertFalse(
            bundle["exact_physical_EFT_G7_input_nonidentifiability_proved"]
        )
        self.assertFalse(bundle["full_mathematical_G7_closed"])

        with tempfile.TemporaryDirectory() as directory:
            root = freezer.Path(directory)
            names = (
                "exact_eft_g7_threshold_nonidentifiability_v20.py",
                "EXACT_EFT_G7_THRESHOLD_NONIDENTIFIABILITY_V20.json",
                "exact_authoritative_so10_u1x_gauge_betas_v20.py",
                "EXACT_AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_V20.json",
                "pyrate3_so10_u1x_gauge_beta_replay_v20.py",
                "PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_V20.json",
                "exact_physical_g7_component_threshold_contract_v20.py",
                "EXACT_PHYSICAL_G7_COMPONENT_THRESHOLD_CONTRACT_V20.json",
            )
            for name in names:
                (root / name).write_bytes((freezer.ROOT / name).read_bytes())
            with patch.object(freezer, "ROOT", root):
                self.assertTrue(
                    freezer._require_eft_g7_truth_bundle()[
                        "all_checks_pass"
                    ]
                )
                report_path = (
                    root / "EXACT_EFT_G7_THRESHOLD_NONIDENTIFIABILITY_V20.json"
                )
                mutated = json.loads(report_path.read_text(encoding="utf-8"))
                mutated["classification"][
                    "exact_physical_EFT_G7_input_nonidentifiability_proved"
                ] = True
                report_path.write_text(
                    json.dumps(mutated, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                    ArithmeticError,
                    "corrected EFT G7 truth bundle drifted",
                ):
                    freezer._require_eft_g7_truth_bundle()

    def _assert_new_physical_sm_and_yukawa_truth_bundles(self) -> None:
        helpers = (
            freezer._require_normalized_yukawa_cgc_truth_bundle,
            freezer._require_physical_sm_vacuum_truth_bundle,
            freezer._require_conditional_physical_sm_eft_hessian_spectrum_bundle,
            freezer._require_physical_sm_heavy_vector_mass_bundle,
            freezer._require_physical_sm_heavy_vector_msbar_matching_bundle,
            freezer._require_physical_sm_vector_rxi_bundle,
            freezer._require_physical_sm_g6_g7_frontier_bundle,
            freezer._require_physical_sm_g8_frontier_bundle,
            freezer._require_physical_sm_source_equality_frontier_bundle,
        )
        for helper in helpers:
            with self.subTest(helper=helper.__name__):
                bundle = helper()
                self.assertEqual(bundle["raw_file_count"], 4)
                self.assertTrue(bundle["all_checks_pass"])
                self.assertTrue(all(bundle["checks"].values()))

        adversarial = (
            (
                freezer._require_normalized_yukawa_cgc_truth_bundle,
                "EXACT_NORMALIZED_SO10_YUKAWA_CGCS_V20.json",
                lambda value: value["scope"].__setitem__("mathematical_G7", True),
                "Yukawa-CGC truth bundle drifted",
            ),
            (
                freezer._require_physical_sm_vacuum_truth_bundle,
                "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.json",
                lambda value: value["closure_claims"].__setitem__(
                    "physical_SM_G3", True
                ),
                "physical-SM vacuum truth bundle drifted",
            ),
            (
                freezer._require_conditional_physical_sm_eft_hessian_spectrum_bundle,
                "CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_V20.json",
                lambda value: value["closure_claims"].__setitem__(
                    "source_bound_physical_G6", True
                ),
                "Hessian spectrum bundle drifted",
            ),
            (
                freezer._require_physical_sm_heavy_vector_mass_bundle,
                "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MASSES_V20.json",
                lambda value: value["scope"].__setitem__("physical_G7", True),
                "heavy-vector mass bundle drifted",
            ),
            (
                freezer._require_physical_sm_heavy_vector_msbar_matching_bundle,
                "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_V20.json",
                lambda value: value["scope"].__setitem__("physical_G7", True),
                "heavy-vector MSbar matching bundle drifted",
            ),
            (
                freezer._require_physical_sm_vector_rxi_bundle,
                "EXACT_PHYSICAL_SM_VECTOR_RXI_VACUUM_CANCELLATION_V20.json",
                lambda value: value["scope"].__setitem__("physical_G7", True),
                "vector Rxi bundle drifted",
            ),
            (
                freezer._require_physical_sm_g6_g7_frontier_bundle,
                "EXACT_PHYSICAL_SM_G6_G7_CLOSURE_FRONTIER_V20.json",
                lambda value: value["scope"].__setitem__("physical_G6", True),
                "G6/G7 frontier bundle drifted",
            ),
            (
                freezer._require_physical_sm_g8_frontier_bundle,
                "EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_V20.json",
                lambda value: value["scope"].__setitem__("physical_G8", True),
                "G8 frontier bundle drifted",
            ),
            (
                freezer._require_physical_sm_source_equality_frontier_bundle,
                "PHYSICAL_SM_SOURCE_ALGEBRA_EQUALITY_FRONTIER_V20.json",
                lambda value: value["closure_claims"].__setitem__(
                    "complete_global_equality_orbit_proved", True
                ),
                "source/equality frontier bundle drifted",
            ),
        )
        for helper, report_name, mutate, message in adversarial:
            with self.subTest(helper=helper.__name__), tempfile.TemporaryDirectory() as directory:
                root = freezer.Path(directory)
                report_path = root / report_name
                value = json.loads(
                    (freezer.ROOT / report_name).read_text(encoding="utf-8")
                )
                mutate(value)
                report_path.write_text(
                    json.dumps(value, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                with patch.object(freezer, "ROOT", root):
                    with self.assertRaisesRegex(ArithmeticError, message):
                        helper()

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
        inventory_paths = set(freezer.RAW_INTEGRATION_PATHS) | set(
            freezer.PORTABLE_INTEGRATION_PATHS
        )
        self.assertLessEqual(inventory_paths - {"SHA256SUMS"}, names)
        self.assertNotIn(freezer.MANIFEST_NAME, names)

    def test_five_amplitude_and_exact_x_v3_freezer_helpers_fail_closed(self) -> None:
        five = freezer._require_physical_sm_five_amplitude_equality_bundle()
        self.assertTrue(five["all_checks_pass"])
        self.assertEqual(five["discrete_real_solution_count"], 16)
        self.assertFalse(five["full_486_equality_classified"])
        self.assertFalse(five["continuous_orbit_equivalence_classified"])
        exact_x = freezer._require_exact_x_v3_fail_closed_bundle()
        self.assertTrue(exact_x["all_checks_pass"])
        self.assertTrue(exact_x["static_native_contract_closed"])
        self.assertTrue(exact_x["authoritative_exact_X_contract_closed"])

        with tempfile.TemporaryDirectory() as directory:
            root = freezer.Path(directory)
            report_name = "EXACT_PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_V20.json"
            value = json.loads(
                (freezer.ROOT / report_name).read_text(encoding="utf-8")
            )
            for relative in value["source_bindings"]["files"]:
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((freezer.ROOT / relative).read_bytes())
            value["closure_claims"]["full_486_field_stationary_equality_classified"] = True
            (root / report_name).write_text(
                json.dumps(value, indent=2) + "\n", encoding="utf-8"
            )
            with patch.object(freezer, "ROOT", root):
                with self.assertRaisesRegex(ArithmeticError, "five-amplitude equality bundle drifted"):
                    freezer._require_physical_sm_five_amplitude_equality_bundle()

        with tempfile.TemporaryDirectory() as directory:
            root = freezer.Path(directory)
            for relative in freezer.EXACT_X_V3_RAW_PINS:
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((freezer.ROOT / relative).read_bytes())
            for relative in freezer.EXACT_X_V3_PORTABLE_PINS:
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((freezer.ROOT / relative).read_bytes())
            report_path = root / "EXACT_X_SYMMETRY_CONSISTENCY_GATE_V20.json"
            value = json.loads(report_path.read_text(encoding="utf-8"))
            value["external_model_validation"]["valid"] = False
            report_path.write_text(
                json.dumps(value, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with patch.object(freezer, "ROOT", root):
                with self.assertRaisesRegex(ArithmeticError, "exact-X v3 fail-closed bundle drifted"):
                    freezer._require_exact_x_v3_fail_closed_bundle()

    def test_five_amplitude_and_exact_x_v3_paths_are_frozen(self) -> None:
        for relative in freezer.PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_RAW_PINS:
            self.assertIn(relative, freezer.RAW_INTEGRATION_PATHS)
            self.assertIn(relative, freezer.CHECKSUM_REQUIRED_PATHS)
        for relative in freezer.PHYSICAL_SM_FIVE_AMPLITUDE_TRANSITIVE_PORTABLE_PINS:
            self.assertIn(relative, freezer.PORTABLE_INTEGRATION_PATHS)
            self.assertIn(relative, freezer.CHECKSUM_REQUIRED_PATHS)
        for relative in freezer.EXACT_X_V3_RAW_PINS:
            self.assertIn(relative, freezer.RAW_INTEGRATION_PATHS)
            self.assertIn(relative, freezer.CHECKSUM_REQUIRED_PATHS)
        for relative in freezer.EXACT_X_V3_PORTABLE_PINS:
            self.assertIn(relative, freezer.PORTABLE_INTEGRATION_PATHS)
            self.assertIn(relative, freezer.CHECKSUM_REQUIRED_PATHS)

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
                    '            "--no-write",'
                )
                classification_replacement = (
                    '            "theory_validation_matrix_v20.py",'
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

    def test_new_Hessian_and_branch_bundles_are_frozen_strictly(self) -> None:
        hard = freezer._require_physical_sm_hard_projector_hessians_bundle()
        self.assertTrue(hard["all_checks_pass"])
        self.assertEqual(hard["exact_source_Hessian_row_count"], 10)
        self.assertFalse(hard["all_37_source_Hessians_available"])
        last = freezer._require_physical_sm_last_six_hessians_bundle()
        self.assertTrue(last["all_checks_pass"])
        self.assertTrue(last["all_37_active_source_Hessians_available"])
        self.assertFalse(last["aggregate_stationarity_kernel_rank_PSD_closed"])
        aggregate = freezer._require_physical_sm_37_row_aggregate_bundle()
        self.assertTrue(aggregate["all_checks_pass"])
        self.assertTrue(aggregate["all_37_active_Hessians_source_derived"])
        self.assertEqual(aggregate["exact_symmetry_kernel_dimension"], 38)
        self.assertEqual(aggregate["exact_rank"], 448)
        self.assertTrue(aggregate["exact_PSD_strict_mod_symmetry"])
        self.assertFalse(aggregate["full_486_global_equality_orbit_closed"])
        mismatch = freezer._require_physical_sm_g4_g5_branch_mismatch_bundle()
        self.assertTrue(mismatch["all_checks_pass"])
        self.assertTrue(mismatch["exact_branch_mismatch_proved"])
        self.assertFalse(mismatch["global_no_go_for_other_physical_EW_branches"])

        for mapping, mode in (
            (freezer.PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_RAW_PINS, "raw"),
            (freezer.PHYSICAL_SM_LAST_SIX_HESSIANS_RAW_PINS, "raw"),
            (freezer.PHYSICAL_SM_37_ROW_AGGREGATE_RAW_PINS, "raw"),
            (freezer.PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_RAW_PINS, "raw"),
            (freezer.PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_TRANSITIVE_RAW_PINS, "raw"),
            (freezer.PHYSICAL_SM_HARD_PROJECTOR_TRANSITIVE_PORTABLE_PINS, "portable"),
            (freezer.PHYSICAL_SM_LAST_SIX_TRANSITIVE_PORTABLE_PINS, "portable"),
            (freezer.PHYSICAL_SM_37_ROW_AGGREGATE_TRANSITIVE_PORTABLE_PINS, "portable"),
        ):
            for relative in mapping:
                self.assertIn(relative, freezer.CHECKSUM_REQUIRED_PATHS)
                self.assertIn(
                    relative,
                    freezer.RAW_INTEGRATION_PATHS
                    if mode == "raw"
                    else freezer.PORTABLE_INTEGRATION_PATHS,
                )

        report_names = (
            "EXACT_PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_V20.json",
            "EXACT_PHYSICAL_SM_LAST_SIX_HESSIANS_V20.json",
            "EXACT_PHYSICAL_SM_37_ROW_AGGREGATE_V20.json",
            "EXACT_PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_V20.json",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = freezer.Path(directory)
            paths = set(report_names)
            for name in report_names:
                report = json.loads((freezer.ROOT / name).read_text(encoding="utf-8"))
                binding = report.get("source_bindings", report.get("source_binding", {}))
                for relative, row in binding.get("files", {}).items():
                    paths.add(str(row.get("path", relative)))
            for relative in paths:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((freezer.ROOT / relative).read_bytes())
            hard_path = root / report_names[0]
            hard_report = json.loads(hard_path.read_text(encoding="utf-8"))
            hard_report["claims"][
                "exact_source_algebra_Hessians_for_all_37_active_witness_rows"
            ] = True
            hard_path.write_text(json.dumps(hard_report), encoding="utf-8")
            with patch.object(freezer, "ROOT", root):
                with self.assertRaisesRegex(ArithmeticError, "hard-projector"):
                    freezer._require_physical_sm_hard_projector_hessians_bundle()

            hard_path.write_bytes((freezer.ROOT / report_names[0]).read_bytes())
            last_path = root / report_names[1]
            last_report = json.loads(last_path.read_text(encoding="utf-8"))
            last_report["claims"][
                "exact_37_row_aggregate_stationarity_kernel_rank_PSD_proved_here"
            ] = True
            last_path.write_text(json.dumps(last_report), encoding="utf-8")
            with patch.object(freezer, "ROOT", root):
                with self.assertRaisesRegex(ArithmeticError, "last-six"):
                    freezer._require_physical_sm_last_six_hessians_bundle()

            last_path.write_bytes((freezer.ROOT / report_names[1]).read_bytes())
            aggregate_path = root / report_names[2]
            aggregate_report = json.loads(
                aggregate_path.read_text(encoding="utf-8")
            )
            aggregate_report["claims"]["physical_SM_G3_closed"] = True
            aggregate_path.write_text(json.dumps(aggregate_report), encoding="utf-8")
            with patch.object(freezer, "ROOT", root):
                with self.assertRaisesRegex(ArithmeticError, "37-row aggregate"):
                    freezer._require_physical_sm_37_row_aggregate_bundle()

            aggregate_path.write_bytes((freezer.ROOT / report_names[2]).read_bytes())
            branch_path = root / report_names[3]
            branch_report = json.loads(branch_path.read_text(encoding="utf-8"))
            branch_report["scope"][
                "global_no_go_for_all_possible_physical_EW_branches"
            ] = True
            branch_path.write_text(json.dumps(branch_report), encoding="utf-8")
            with patch.object(freezer, "ROOT", root):
                with self.assertRaisesRegex(ArithmeticError, "branch-mismatch"):
                    freezer._require_physical_sm_g4_g5_branch_mismatch_bundle()

    def test_local_equality_orbit_bundle_is_frozen_strictly(self) -> None:
        bundle = freezer._require_physical_sm_local_equality_orbit_bundle()
        self.assertTrue(bundle["all_checks_pass"])
        self.assertTrue(bundle["full_486_local_stationary_orbit_classified"])
        self.assertTrue(
            bundle["full_486_local_stationary_equality_orbit_classified"]
        )
        self.assertTrue(bundle["all_16_sign_variants_one_continuous_K_orbit"])
        self.assertTrue(bundle["target_orbit_strict_local_minimum_mod_K"])
        self.assertFalse(bundle["quantitative_neighborhood_radius_proved"])
        self.assertFalse(bundle["complete_486_global_equality_orbit_classified"])
        for gate in ("G3", "G4", "G5"):
            self.assertFalse(bundle[f"physical_SM_{gate}_closed"])

        for mapping in (
            freezer.PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_PORTABLE_PINS,
            freezer.PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_TRANSITIVE_PORTABLE_PINS,
        ):
            for relative in mapping:
                self.assertIn(relative, freezer.PORTABLE_INTEGRATION_PATHS)
                self.assertIn(relative, freezer.CHECKSUM_REQUIRED_PATHS)

        report_name = "EXACT_PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_V20.json"
        baseline = json.loads(
            (freezer.ROOT / report_name).read_text(encoding="utf-8")
        )
        paths = {report_name, *baseline["source_bindings"]["files"]}
        with tempfile.TemporaryDirectory() as directory:
            root = freezer.Path(directory)
            for relative in paths:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((freezer.ROOT / relative).read_bytes())

            report_path = root / report_name
            mutations = (
                ("quantitative_radius_for_U_proved", True),
                ("complete_486_field_global_equality_orbit_classified", True),
                ("physical_SM_G3_closed", True),
            )
            for name, value in mutations:
                mutated = json.loads(json.dumps(baseline))
                mutated["claims"][name] = value
                report_path.write_text(json.dumps(mutated), encoding="utf-8")
                with patch.object(freezer, "ROOT", root):
                    with self.assertRaisesRegex(
                        ArithmeticError, "local equality-orbit"
                    ):
                        freezer._require_physical_sm_local_equality_orbit_bundle()

            report_path.write_text(json.dumps(baseline), encoding="utf-8")
            dependency = root / next(iter(baseline["source_bindings"]["files"]))
            dependency.write_bytes(dependency.read_bytes() + b"\n")
            with patch.object(freezer, "ROOT", root):
                with self.assertRaisesRegex(ArithmeticError, "local equality-orbit"):
                    freezer._require_physical_sm_local_equality_orbit_bundle()

        forged_pins = dict(freezer.PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_PORTABLE_PINS)
        forged_pins[next(iter(forged_pins))] = "0" * 64
        with patch.object(
            freezer, "PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_PORTABLE_PINS", forged_pins
        ):
            with self.assertRaisesRegex(
                ArithmeticError, "local equality-orbit bundle member drifted"
            ):
                freezer._require_source_pins()

    def test_legacy_so10_210_beta_diagnostic_is_strict_and_fail_closed(self) -> None:
        bundle = freezer._require_legacy_so10_210_beta_diagnostic_bundle()
        self.assertEqual(bundle["raw_report_count"], 2)
        self.assertTrue(bundle["all_checks_pass"])
        self.assertFalse(bundle["live_SARAH_or_PyRATE_execution_attested"])
        self.assertFalse(bundle["unique_physical_mathematical_release_G7_closed"])

        json_name = "SARAH_PYRATE_SO10_210_BETAS_V20_VERDICT.json"
        md_name = "SARAH_PYRATE_SO10_210_BETAS_V20.md"
        workflow_name = freezer.LEGACY_SO10_210_BETA_DIAGNOSTIC_WORKFLOW
        baseline = {
            name: (freezer.ROOT / name).read_bytes()
            for name in (json_name, md_name, workflow_name)
        }
        mutations = (
            (
                "status",
                lambda root: (root / json_name).write_bytes(
                    baseline[json_name].replace(
                        b"CORRECTED_SO10_NONYUKAWA_GAUGE_POLYNOMIAL__FULL_G7_OPEN",
                        b"FULL_G7_CLOSED__________________________________________",
                        1,
                    )
                ),
            ),
            (
                "CRLF",
                lambda root: (root / md_name).write_bytes(
                    baseline[md_name].replace(b"\r\n", b"\n")
                ),
            ),
            (
                "workflow",
                lambda root: (root / workflow_name).write_bytes(
                    baseline[workflow_name].replace(
                        b"assert not r['flag']['sarah_validated_210_betas']",
                        b"assert r['flag']['sarah_validated_210_betas']",
                        1,
                    )
                ),
            ),
        )
        for label, mutate in mutations:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as directory:
                root = freezer.Path(directory)
                for name, payload in baseline.items():
                    path = root / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(payload)
                mutate(root)
                with patch.object(freezer, "ROOT", root):
                    with self.assertRaisesRegex(
                        ArithmeticError,
                        r"legacy SO\(10\)\+210 beta diagnostic bundle drifted",
                    ):
                        freezer._require_legacy_so10_210_beta_diagnostic_bundle()

        wrong_pins = dict(freezer.LEGACY_SO10_210_BETA_DIAGNOSTIC_RAW_PINS)
        wrong_pins[json_name] = "0" * 64
        with patch.object(
            freezer, "LEGACY_SO10_210_BETA_DIAGNOSTIC_RAW_PINS", wrong_pins
        ):
            with self.assertRaisesRegex(
                ArithmeticError, r"legacy SO\(10\)\+210 beta diagnostic drifted"
            ):
                freezer._require_source_pins()


if __name__ == "__main__":
    unittest.main()
