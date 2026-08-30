#!/usr/bin/env python3
"""Regression tests for the contract-aware G1-G8 gate ledger."""
from __future__ import annotations

import copy
import unittest
from pathlib import Path

import g1_g8_gate_ledger_v20 as mod


EXACT_HESSIAN_TRANSITIVE_SOURCES = (
    "exact_126bar_self_quartic_basis_v20",
    "exact_210_self_invariant_basis_v20",
    "exact_h10_self_quartic_family_v20",
    "exact_hsigma_hermitian_family_closure_v20",
    "exact_mixed_45_triplet_channel_v20",
    "exact_p_delta_second_stage_hessian_v20",
    "exact_phi2_126dag126_six_contractions_v20",
    "exact_phi2_hdagh_channel_family_v20",
    "exact_phisigma_126bar_minus_projectors_v20",
    "exact_phisigma_casimir_projectors_v20",
    "live_g1_tensor_closure_ledger_v20",
    "nonsusy_z17_pq_potential_filter_v20",
)


def _bind_tool_native_root_evidence(report):
    scaffold = report["executable_scaffold_contract"]
    scaffold["model_syntax_class"] = "sarah_native"
    scaffold["tool_native_sarah_syntax"] = True
    scaffold["statically_executable_model_contract"] = True
    scaffold["lagrangian"][
        "registered_in_GaugeES_LagrangianInput"
    ] = True
    external = report["external_model_validation"]
    external["schema"] = mod.exact_x.EXTERNAL_VALIDATION_SCHEMA
    external["present"] = True
    external["valid"] = True
    external["fresh_for_exact_model_bytes"] = True
    for name in mod.EXPECTED_EXACT_X_V3_EXTERNAL_CHECKS:
        external["checks"][name] = True


class G1G8GateLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_central_workflows_cover_exact_hessian_transitive_sources(self):
        root = Path(__file__).resolve().parent
        workflows = (
            (
                ".github/workflows/g1-g8-gate-ledger.yml",
                2,
                "Compile gates",
                "Run gate tests",
            ),
            (
                ".github/workflows/g1-g8-execution-roadmap.yml",
                1,
                "Compile roadmap",
                "Test roadmap contracts",
            ),
            (
                ".github/workflows/gauged-u1x-g3-stability.yml",
                2,
                "Compile gauged-X G2/G3 audits",
                "Run focused gauged-X tests",
            ),
        )

        def step_block(text, name):
            marker = f"      - name: {name}\n"
            self.assertIn(marker, text)
            block = text.split(marker, 1)[1]
            return block.split("\n      - ", 1)[0]

        for relative, trigger_copies, compile_name, test_name in workflows:
            with self.subTest(workflow=relative):
                text = (root / relative).read_text(encoding="utf-8")
                trigger = text.split("\nconcurrency:", 1)[0]
                trigger_entries = []
                for line in trigger.splitlines():
                    item = line.strip()
                    if item.startswith("- "):
                        trigger_entries.append(item[2:].strip('"'))
                compile_tokens = step_block(text, compile_name).replace(
                    "\\", " "
                ).split()
                test_tokens = step_block(text, test_name).replace("\\", " ").split()
                for stem in EXACT_HESSIAN_TRANSITIVE_SOURCES:
                    source = f"{stem}.py"
                    test = f"test_{stem}.py"
                    self.assertEqual(trigger_entries.count(source), trigger_copies)
                    self.assertEqual(trigger_entries.count(test), trigger_copies)
                    self.assertEqual(compile_tokens.count(source), 1)
                    self.assertEqual(compile_tokens.count(test), 1)
                    self.assertEqual(test_tokens.count(test), 1)

    def test_audit_succeeds_and_tracks_contract_state(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["audit_failures"])
        if self.report["contract_consistent"]:
            self.assertEqual(self.report["overall_state"], mod.STATUS_OPEN)
            self.assertNotIn(mod.CONTRACT_BLOCKER, self.report["scientific_blockers"])
        else:
            self.assertEqual(self.report["overall_state"], mod.STATUS_BLOCKED)
            self.assertIn(mod.CONTRACT_BLOCKER, self.report["scientific_blockers"])
        self.assertIn(
            "G3_ARBITRARY_NON_PURE_DELTA_SIGMA_UNIFORM_COERCIVITY_OPEN",
            self.report["scientific_blockers"],
        )
        self.assertIn(
            "G6_GLOBAL_EQUALITY_SCALE_FULL_MASS_MIXING_POLE_AND_THRESHOLD_INPUTS_REQUIRED",
            self.report["scientific_blockers"],
        )
        self.assertNotIn(
            "G6_DIRECT_SOURCE_ALGEBRA_GLOBAL_EQUALITY_ORBIT_AND_POLE_SPECTRUM_REQUIRED",
            self.report["scientific_blockers"],
        )
        self.assertNotIn(
            "G6_FROZEN_STABILIZER_IS_SU3_X_U1_89_NOT_PHYSICAL_ELECTROMAGNETISM",
            self.report["scientific_blockers"],
        )

    def test_exact_x_v3_trusted_tree_and_execution_state_are_bound(self):
        scoped = self.report["exact_X_v3_fail_closed_contract"]
        self.assertTrue(scoped["source_bound"])
        self.assertTrue(scoped["static_native_contract_closed"])
        self.assertTrue(scoped["input_manifest_v2_closed"])
        self.assertTrue(
            scoped["trusted_SARAH_4_15_3_source_tree_manifest_closed"]
        )
        self.assertEqual(scoped["trusted_SARAH_source_tree_file_count"], 1056)
        self.assertEqual(
            scoped["trusted_SARAH_source_tree_core_sha256"],
            mod.EXACT_X_V3_TRUSTED_SARAH_TREE_CORE_SHA256,
        )
        self.assertEqual(
            scoped["external_attestation_schema_required"],
            "so10-exact-x-external-model-validation-v3",
        )
        consistent = self.report["contract_consistent"]
        self.assertIs(scoped["external_v3_execution_attestation_present"], consistent)
        self.assertIs(scoped["resolved_Wolfram_runtime_bound"], consistent)
        self.assertIs(scoped["runtime_probe_log_bound"], consistent)
        self.assertIs(scoped["validation_process_log_bound"], consistent)
        self.assertIs(scoped["contract_consistent"], consistent)
        self.assertIs(scoped["authoritative_G1_closed"], consistent)
        self.assertIs(scoped["release_G1_verified"], consistent)
        self.assertEqual(
            self.report["gates"]["G1"]["status"],
            mod.STATUS_CLOSED if consistent else mod.STATUS_BLOCKED,
        )
        self.assertTrue(
            self.report["checks"][
                "exact_X_v3_contract_state_is_fail_closed_and_consistent"
            ]
        )

    def test_exact_x_v3_contract_rejects_forgery_and_raw_pin_drift(self):
        valid = mod.exact_x.build_report()
        pins = {
            "source_raw_sha256": mod.EXACT_X_V3_SOURCE_RAW_SHA256,
            "test_raw_sha256": mod.EXACT_X_V3_TEST_RAW_SHA256,
            "json_raw_sha256": mod.EXACT_X_V3_JSON_RAW_SHA256,
            "markdown_raw_sha256": mod.EXACT_X_V3_MD_RAW_SHA256,
            "input_manifest_raw_sha256": (
                mod.EXACT_X_V3_INPUT_MANIFEST_RAW_SHA256
            ),
            "trusted_sarah_manifest_raw_sha256": (
                mod.EXACT_X_V3_TRUSTED_SARAH_MANIFEST_RAW_SHA256
            ),
            "external_validation_file_present": True,
        }
        self.assertTrue(
            mod._exact_x_v3_fail_closed_contract(valid, **pins)["source_bound"]
        )
        mutations = (
            lambda value: value["repository_external_input_manifest"][
                "trusted_sarah_release_manifest"
            ]["tree"].__setitem__("sha256", "0" * 64),
            lambda value: value["repository_external_input_manifest"].__setitem__(
                "role", "external attestation"
            ),
            lambda value: value["external_model_validation"].__setitem__(
                "valid", False
            ),
            lambda value: value.__setitem__("contract_consistent", False),
        )
        for mutate in mutations:
            forged = copy.deepcopy(valid)
            mutate(forged)
            audited = mod._exact_x_v3_fail_closed_contract(forged, **pins)
            self.assertFalse(audited["source_bound"])
            self.assertFalse(audited["authoritative_G1_closed"])
        for pin_name in pins:
            forged_pins = dict(pins)
            forged_pins[pin_name] = "0" * 64
            self.assertFalse(
                mod._exact_x_v3_fail_closed_contract(
                    valid, **forged_pins
                )["source_bound"]
            )

    def test_parallel_eft_g3_is_bound_without_mutating_g3_or_g4(self):
        parallel = self.report["parallel_EFT_G3_acceptance"]
        self.assertTrue(parallel["source_bound"])
        self.assertEqual(
            parallel["core_sha256"],
            mod.FINAL_G3_EFT_ACCEPTANCE_CORE_SHA256,
        )
        self.assertEqual(
            parallel["raw_sha256"],
            mod.FINAL_G3_EFT_ACCEPTANCE_RAW_SHA256,
        )
        self.assertTrue(parallel["checks"]["raw_sha256_exact"])
        self.assertTrue(parallel["mathematical_G3_closed_for_EFT_model"])
        self.assertFalse(parallel["release_G3_verified_for_EFT_model"])
        self.assertFalse(
            parallel[
                "mathematical_G3_closed_for_original_renormalizable_model"
            ]
        )
        self.assertFalse(parallel["renormalizable_gate_mutated"])
        self.assertFalse(parallel["G4_closed"])
        self.assertEqual(self.report["gates"]["G3"]["status"], mod.STATUS_OPEN)
        self.assertEqual(self.report["gates"]["G4"]["status"], mod.STATUS_BLOCKED)
        self.assertFalse(
            self.report["gauged_u1x_g3_constructive_frontier"]["G3_closed"]
        )
        self.assertTrue(
            self.report["checks"][
                "parallel_EFT_G3_acceptance_is_source_bound_and_release_open"
            ]
        )
        self.assertEqual(
            self.report["model_contract_reports"][
                "parallel_EFT_G3_acceptance_gate"
            ]["core_sha256"],
            mod.FINAL_G3_EFT_ACCEPTANCE_CORE_SHA256,
        )

        forged = copy.deepcopy(
            mod._load_json_artifact(mod.FINAL_G3_EFT_ACCEPTANCE_JSON)
        )
        forged["core_sha256"] = "0" * 64
        self.assertFalse(
            mod._parallel_eft_g3_acceptance(
                forged,
                raw_sha256=mod.FINAL_G3_EFT_ACCEPTANCE_RAW_SHA256,
            )["source_bound"]
        )
        valid = mod._load_json_artifact(mod.FINAL_G3_EFT_ACCEPTANCE_JSON)
        self.assertFalse(
            mod._parallel_eft_g3_acceptance(
                valid,
                raw_sha256="0" * 64,
            )["source_bound"]
        )

    def test_parallel_eft_g4_g5_g6_are_bound_without_authoritative_promotion(self):
        g4 = self.report["parallel_EFT_G4_mathematical"]
        g5 = self.report["parallel_EFT_G5_mathematical"]
        g6 = self.report["parallel_EFT_G6_spectrum"]
        self.assertTrue(g4["source_bound"])
        self.assertEqual(g4["core_sha256"], mod.FINAL_G4_EFT_MATHEMATICAL_CORE_SHA256)
        self.assertEqual(g4["raw_sha256"], mod.FINAL_G4_EFT_MATHEMATICAL_RAW_SHA256)
        self.assertTrue(g4["mathematical_G4_closed_for_EFT_model"])
        self.assertFalse(g4["release_G4_verified_for_EFT_model"])
        self.assertFalse(
            g4["mathematical_G4_closed_for_original_renormalizable_model"]
        )
        self.assertFalse(g4["authoritative_renormalizable_G4_gate_mutated"])
        self.assertTrue(g4["checks"]["parallel_integration_completed"])
        self.assertNotIn(
            "parallel_EFT_G4_integrated_into_release_orchestrators",
            g4["release_blockers"],
        )

        self.assertTrue(g5["source_bound"])
        self.assertEqual(g5["core_sha256"], mod.FINAL_G5_EFT_MATHEMATICAL_CORE_SHA256)
        self.assertEqual(g5["raw_sha256"], mod.FINAL_G5_EFT_MATHEMATICAL_RAW_SHA256)
        self.assertTrue(g5["mathematical_G5_closed_for_EFT_model"])
        self.assertFalse(g5["release_G5_verified_for_EFT_model"])
        self.assertFalse(g5["authoritative_renormalizable_G5_closed"])
        self.assertFalse(g5["authoritative_renormalizable_G5_mutated"])
        self.assertFalse(g5["new_SOS_claimed"])
        self.assertTrue(g5["checks"]["parallel_integration_completed"])
        self.assertNotIn(
            "downstream_parallel_G5_integration_completed",
            g5["release_blockers"],
        )

        self.assertTrue(g6["source_bound"])
        self.assertEqual(g6["core_sha256"], mod.FINAL_G6_EFT_MATHEMATICAL_CORE_SHA256)
        self.assertEqual(g6["raw_sha256"], mod.FINAL_G6_EFT_MATHEMATICAL_RAW_SHA256)
        self.assertEqual(
            g6["gate_source_raw_sha256"],
            mod.FINAL_G6_EFT_GATE_SOURCE_RAW_SHA256,
        )
        self.assertEqual(
            g6["spectrum_core_sha256"], mod.FINAL_G6_EFT_SPECTRUM_CORE_SHA256
        )
        self.assertEqual(
            g6["spectrum_source_raw_sha256"],
            mod.FINAL_G6_EFT_SPECTRUM_SOURCE_RAW_SHA256,
        )
        self.assertEqual(
            g6["spectrum_JSON_raw_sha256"],
            mod.FINAL_G6_EFT_SPECTRUM_JSON_RAW_SHA256,
        )
        self.assertTrue(g6["formal_SU3_x_U1_89_tree_factorization_closed"])
        self.assertFalse(g6["mathematical_G6_closed_for_EFT_model"])
        self.assertFalse(g6["physical_mathematical_G6_closed"])
        self.assertFalse(g6["release_G6_verified_for_EFT_model"])
        self.assertFalse(g6["authoritative_renormalizable_G6_closed"])
        self.assertFalse(g6["authoritative_G6_gate_mutated"])
        self.assertFalse(g6["whole_model_validated"])
        self.assertEqual(g6["spectrum_summary"]["ambient_real_fields"], 486)
        self.assertEqual(g6["spectrum_summary"]["gauge_quotient_dimension"], 449)
        self.assertEqual(g6["spectrum_summary"]["ungauged_PQ_zero_modes"], 1)
        self.assertEqual(g6["spectrum_summary"]["positive_massive_modes"], 448)
        self.assertTrue(g6["checks"]["parallel_integration_state_classified"])
        self.assertEqual(
            g6["parallel_integration_completed"],
            "parallel_EFT_G6_integrated_into_release_orchestrators"
            not in g6["release_blockers"],
        )
        self.assertFalse(
            mod._parallel_eft_g6_spectrum(
                mod._load_json_artifact(mod.FINAL_G6_EFT_MATHEMATICAL_JSON),
                raw_sha256=mod.FINAL_G6_EFT_MATHEMATICAL_RAW_SHA256,
                gate_source_raw_sha256="0" * 64,
            )["source_bound"]
        )

        expected = {
            "G3": mod.STATUS_OPEN,
            "G4": mod.STATUS_BLOCKED,
            "G5": mod.STATUS_CLOSED,
            "G6": mod.STATUS_BLOCKED,
        }
        for name, status in expected.items():
            self.assertEqual(self.report["gates"][name]["status"], status)
        self.assertTrue(
            self.report["checks"][
                "parallel_EFT_G4_mathematical_is_source_bound_and_release_open"
            ]
        )
        self.assertTrue(
            self.report["checks"][
                "parallel_EFT_G5_mathematical_is_source_bound_and_release_open"
            ]
        )
        self.assertTrue(
            self.report["checks"][
                "parallel_EFT_G6_formal_spectrum_is_bound_but_physical_G6_open"
            ]
        )

        cases = (
            (
                mod._parallel_eft_g4_mathematical,
                mod.FINAL_G4_EFT_MATHEMATICAL_JSON,
                mod.FINAL_G4_EFT_MATHEMATICAL_RAW_SHA256,
            ),
            (
                mod._parallel_eft_g5_mathematical,
                mod.FINAL_G5_EFT_MATHEMATICAL_JSON,
                mod.FINAL_G5_EFT_MATHEMATICAL_RAW_SHA256,
            ),
            (
                mod._parallel_eft_g6_spectrum,
                mod.FINAL_G6_EFT_MATHEMATICAL_JSON,
                mod.FINAL_G6_EFT_MATHEMATICAL_RAW_SHA256,
            ),
        )
        for validator, path, raw_sha256 in cases:
            with self.subTest(artifact=path.name, mutation="core"):
                forged = copy.deepcopy(mod._load_json_artifact(path))
                forged["core_sha256"] = "0" * 64
                self.assertFalse(
                    validator(forged, raw_sha256=raw_sha256)["source_bound"]
                )
            with self.subTest(artifact=path.name, mutation="raw"):
                valid = mod._load_json_artifact(path)
                self.assertFalse(
                    validator(valid, raw_sha256="0" * 64)["source_bound"]
                )

    def test_exact_eft_g7_input_obstruction_is_bound_without_closing_g7(self):
        g7 = self.report["parallel_EFT_G7_nonidentifiability"]
        self.assertTrue(g7["source_bound"])
        self.assertEqual(g7["core_sha256"], mod.EFT_G7_NONIDENTIFIABILITY_CORE_SHA256)
        self.assertEqual(g7["raw_sha256"], mod.EFT_G7_NONIDENTIFIABILITY_RAW_SHA256)
        self.assertEqual(
            g7["source_raw_sha256"],
            mod.EFT_G7_NONIDENTIFIABILITY_SOURCE_RAW_SHA256,
        )
        self.assertTrue(
            g7["formal_U1_89_abstract_restriction_noninjectivity_proved"]
        )
        self.assertFalse(
            g7["exact_physical_EFT_G7_input_nonidentifiability_proved"]
        )
        self.assertFalse(g7["historical_electroweak_lift_interpretation_valid"])
        self.assertTrue(g7["formal_U1_89_restriction_map_noninjective"])
        self.assertTrue(g7["absolute_scale_unidentified"])
        self.assertFalse(g7["mathematical_EFT_G7_closed"])
        self.assertFalse(g7["positive_G7_certified"])
        self.assertFalse(g7["negative_G7_no_go_certified"])
        self.assertFalse(g7["EFT_release_G7_verified"])
        self.assertFalse(g7["authoritative_renormalizable_G7_closed"])
        self.assertTrue(g7["downstream_integration_completed"])
        self.assertEqual(self.report["gates"]["G7"]["status"], mod.STATUS_BLOCKED)
        self.assertEqual(self.report["gates"]["G8"]["status"], mod.STATUS_BLOCKED)

        valid = mod._load_json_artifact(mod.EFT_G7_NONIDENTIFIABILITY_JSON)
        self.assertFalse(
            mod._parallel_eft_g7_nonidentifiability(
                valid,
                raw_sha256="0" * 64,
                source_raw_sha256=mod.EFT_G7_NONIDENTIFIABILITY_SOURCE_RAW_SHA256,
            )["source_bound"]
        )
        forged = copy.deepcopy(valid)
        forged["classification"]["positive_G7_certified"] = True
        self.assertFalse(
            mod._parallel_eft_g7_nonidentifiability(
                forged,
                raw_sha256=mod.EFT_G7_NONIDENTIFIABILITY_RAW_SHA256,
                source_raw_sha256=mod.EFT_G7_NONIDENTIFIABILITY_SOURCE_RAW_SHA256,
            )["source_bound"]
        )

    def test_physical_g7_component_threshold_contract_is_raw_bound_and_scoped(self):
        scoped = self.report["physical_G7_component_threshold_contract"]
        self.assertTrue(scoped["source_bound"])
        self.assertTrue(scoped["authoritative_inventory_closed"])
        self.assertTrue(scoped["physical_PS_SM_matter_branching_closed"])
        self.assertTrue(
            scoped["parameterized_one_loop_matter_threshold_kernel_closed"]
        )
        self.assertTrue(scoped["exact_two_loop_nonyukawa_gauge_flow_closed"])
        self.assertFalse(scoped["physical_component_pole_mass_matrices_closed"])
        self.assertFalse(scoped["physical_G7_closed"])
        self.assertFalse(scoped["mathematical_G7_closed"])
        self.assertFalse(scoped["release_G7_verified"])
        self.assertFalse(scoped["authoritative_renormalizable_G7_closed"])
        self.assertEqual(self.report["gates"]["G7"]["status"], mod.STATUS_BLOCKED)
        obstruction = self.report["gates"]["G7"]["certified_input_obstruction"]
        self.assertEqual(
            obstruction["physical_PS_SM_component_threshold_contract"], scoped
        )

    def test_physical_g7_consumer_rejects_schema_hash_and_closure_forgery(self):
        valid = mod._load_json_artifact(mod.PHYSICAL_G7_COMPONENT_THRESHOLD_JSON)
        pins = {
            "raw_sha256": mod.PHYSICAL_G7_COMPONENT_THRESHOLD_RAW_SHA256,
            "source_raw_sha256": (
                mod.PHYSICAL_G7_COMPONENT_THRESHOLD_SOURCE_RAW_SHA256
            ),
            "test_raw_sha256": mod.PHYSICAL_G7_COMPONENT_THRESHOLD_TEST_RAW_SHA256,
            "markdown_raw_sha256": (
                mod.PHYSICAL_G7_COMPONENT_THRESHOLD_MD_RAW_SHA256
            ),
        }
        self.assertTrue(
            mod._physical_g7_component_threshold_contract(valid, **pins)[
                "source_bound"
            ]
        )
        mutations = (
            lambda value: value.__setitem__("unexpected", True),
            lambda value: value["completion_matrix"].__setitem__(
                "mathematical_G7_closed", True
            ),
            lambda value: value["completion_matrix"].__setitem__(
                "physical_component_pole_mass_matrices", True
            ),
            lambda value: value["release_blockers"].pop(),
            lambda value: value["adversarial_guards"].__setitem__(
                "G89_never_used_as_hypercharge", False
            ),
        )
        for mutate in mutations:
            forged = copy.deepcopy(valid)
            mutate(forged)
            audited = mod._physical_g7_component_threshold_contract(
                forged, **pins
            )
            self.assertFalse(audited["source_bound"])
            self.assertFalse(audited["physical_PS_SM_matter_branching_closed"])
            self.assertFalse(
                audited["parameterized_one_loop_matter_threshold_kernel_closed"]
            )
            self.assertFalse(audited["mathematical_G7_closed"])
            self.assertFalse(audited["release_G7_verified"])

        forged_pin = dict(pins)
        forged_pin["test_raw_sha256"] = "0" * 64
        self.assertFalse(
            mod._physical_g7_component_threshold_contract(
                valid, **forged_pin
            )["source_bound"]
        )

    def test_physical_sm_truth_overlay_supersedes_old_stabilizer_fail_closed(self):
        overlay = self.report["physical_SM_vacuum_truth_overlay"]
        self.assertTrue(overlay["source_bound"])
        self.assertTrue(overlay["physical_SM_target_exactly_constructed"])
        self.assertTrue(overlay["standard_SU3C_x_U1em_stabilizer_proved"])
        self.assertTrue(
            overlay["reconstructed_stationary_transverse_PSD_witness_available"]
        )
        self.assertFalse(
            overlay["direct_source_algebra_stationary_PSD_witness_available"]
        )
        self.assertFalse(overlay["source_bound_global_equality_orbit_proved"])
        self.assertTrue(overlay["old_selected_EFT_stabilizer_label_superseded"])
        self.assertEqual(
            overlay["old_selected_EFT_target_actual_stabilizer"],
            "SU(3)_C x U(1)_89",
        )
        expected = {
            "G3": mod.STATUS_OPEN,
            "G4": mod.STATUS_BLOCKED,
            "G5": mod.STATUS_CLOSED,
            "G6": mod.STATUS_BLOCKED,
            "G7": mod.STATUS_BLOCKED,
        }
        for gate, status in expected.items():
            self.assertFalse(overlay[f"physical_SM_{gate}_closed"])
            self.assertEqual(self.report["gates"][gate]["status"], status)

    def test_physical_sm_truth_overlay_rejects_pins_schema_and_claim_forgery(self):
        valid = mod._load_json_artifact(mod.PHYSICAL_SM_VACUUM_JSON)
        pins = {
            "raw_sha256": mod.PHYSICAL_SM_VACUUM_RAW_SHA256,
            "source_raw_sha256": mod.PHYSICAL_SM_VACUUM_SOURCE_RAW_SHA256,
            "test_raw_sha256": mod.PHYSICAL_SM_VACUUM_TEST_RAW_SHA256,
            "markdown_raw_sha256": mod.PHYSICAL_SM_VACUUM_MD_RAW_SHA256,
        }
        self.assertTrue(
            mod._physical_sm_vacuum_truth_overlay(valid, **pins)["source_bound"]
        )
        mutations = (
            lambda value: value.__setitem__("unexpected", True),
            lambda value: value["closure_claims"].__setitem__(
                "physical_SM_G3", True
            ),
            lambda value: value["supersession"].__setitem__(
                "old_selected_EFT_target_was_standard_SU3C_x_U1em", True
            ),
            lambda value: value["logical_summary"].__setitem__(
                "source_bound_global_equality_orbit_proved", True
            ),
            lambda value: value["exact_reconstructed_Hessian_rank"][
                "reconstruction"
            ].__setitem__("source_algebra_derivation_complete", True),
        )
        for mutate in mutations:
            forged = copy.deepcopy(valid)
            mutate(forged)
            audited = mod._physical_sm_vacuum_truth_overlay(forged, **pins)
            self.assertFalse(audited["source_bound"])
            self.assertFalse(audited["physical_SM_target_exactly_constructed"])
            self.assertFalse(audited["physical_SM_G3_closed"])

        forged_pin = dict(pins)
        forged_pin["markdown_raw_sha256"] = "0" * 64
        self.assertFalse(
            mod._physical_sm_vacuum_truth_overlay(valid, **forged_pin)[
                "source_bound"
            ]
        )

    def test_physical_sm_radial_equality_frontier_is_exact_and_fail_closed(self):
        scoped = self.report["physical_SM_source_algebra_equality_frontier"]
        self.assertTrue(scoped["source_bound"])
        self.assertEqual(
            scoped["core_sha256"], mod.PHYSICAL_SM_SOURCE_EQUALITY_CORE_SHA256
        )
        self.assertTrue(scoped["radial_stationary_equality_classified_exactly"])
        self.assertEqual(scoped["radial_gcd"], "t - 1")
        self.assertEqual(scoped["observed_source_Hessian_row_lcm"], 126000)
        self.assertEqual(
            scoped["reconstructed_aggregate_Hessian_lcm"], 6300103327590
        )
        self.assertFalse(scoped["direct_source_algebra_stationary_Hessian_available"])
        self.assertFalse(scoped["complete_nonradial_equality_orbit_proved"])
        self.assertFalse(scoped["old_formal_U1_89_EFT_scope_promoted"])
        expected = {
            "G3": mod.STATUS_OPEN,
            "G4": mod.STATUS_BLOCKED,
            "G5": mod.STATUS_CLOSED,
        }
        for gate, status in expected.items():
            self.assertFalse(scoped[f"physical_SM_{gate}_closed"])
            self.assertEqual(self.report["gates"][gate]["status"], status)
            self.assertEqual(
                self.report["gates"][gate][
                    "physical_SM_source_algebra_equality_frontier"
                ],
                scoped,
            )
        self.assertTrue(
            self.report["checks"][
                "physical_SM_radial_equality_is_exact_but_G3_G4_G5_remain_open"
            ]
        )

    def test_physical_sm_radial_frontier_rejects_report_and_pin_forgery(self):
        valid = mod._load_json_artifact(mod.PHYSICAL_SM_SOURCE_EQUALITY_JSON)
        pins = {
            "raw_sha256": mod.PHYSICAL_SM_SOURCE_EQUALITY_RAW_SHA256,
            "source_raw_sha256": (
                mod.PHYSICAL_SM_SOURCE_EQUALITY_SOURCE_RAW_SHA256
            ),
            "test_raw_sha256": mod.PHYSICAL_SM_SOURCE_EQUALITY_TEST_RAW_SHA256,
            "markdown_raw_sha256": (
                mod.PHYSICAL_SM_SOURCE_EQUALITY_MD_RAW_SHA256
            ),
        }
        self.assertTrue(
            mod._physical_sm_source_algebra_equality_frontier_contract(
                valid, **pins
            )["source_bound"]
        )
        mutations = (
            lambda value: value.__setitem__("unexpected", True),
            lambda value: value["integrity"].__setitem__("core_sha256", "0" * 64),
            lambda value: value["exact_radial_equality"].__setitem__(
                "gcd_V_plus_1_and_dV_dt_monic", "1"
            ),
            lambda value: value["source_row_lattice_frontier"].__setitem__(
                "source_algebra_derivation_complete", True
            ),
            lambda value: value["closure_claims"].__setitem__(
                "physical_SM_G3_closed", True
            ),
            lambda value: value["next_required_calculation"].pop(),
            lambda value: value["checks"].__setitem__(
                "full_equality_orbit_remains_fail_closed", False
            ),
        )
        for mutate in mutations:
            forged = copy.deepcopy(valid)
            mutate(forged)
            audited = mod._physical_sm_source_algebra_equality_frontier_contract(
                forged, **pins
            )
            self.assertFalse(audited["source_bound"])
            self.assertFalse(
                audited["radial_stationary_equality_classified_exactly"]
            )
            self.assertFalse(audited["physical_SM_G3_closed"])

        for pin_name in pins:
            forged_pins = dict(pins)
            forged_pins[pin_name] = "0" * 64
            self.assertFalse(
                mod._physical_sm_source_algebra_equality_frontier_contract(
                    valid, **forged_pins
                )["source_bound"]
            )

    def test_physical_sm_five_amplitude_equality_is_exact_and_fail_closed(self):
        scoped = self.report["physical_SM_five_amplitude_equality_contract"]
        self.assertTrue(scoped["source_bound"])
        self.assertTrue(scoped["exact_radial_theorem_strictly_extended"])
        self.assertTrue(
            scoped["five_real_amplitude_slice_stationary_equality_classified"]
        )
        self.assertEqual(scoped["exact_real_discrete_sign_variant_count"], 16)
        self.assertTrue(scoped["target_strict_minimum_on_five_amplitude_slice"])
        self.assertFalse(scoped["full_486_field_stationary_equality_classified"])
        self.assertFalse(
            scoped["continuous_symmetry_orbit_equivalence_of_16_variants_proved"]
        )
        self.assertFalse(scoped["direct_source_algebra_full_486_Hessian_available"])
        expected = {
            "G3": mod.STATUS_OPEN,
            "G4": mod.STATUS_BLOCKED,
            "G5": mod.STATUS_CLOSED,
        }
        for gate, status in expected.items():
            self.assertFalse(scoped[f"physical_SM_{gate}_closed"])
            self.assertEqual(self.report["gates"][gate]["status"], status)
            self.assertEqual(
                self.report["gates"][gate]["physical_SM_five_amplitude_equality"],
                scoped,
            )
        self.assertTrue(
            self.report["checks"][
                "physical_SM_five_amplitude_equality_is_exact_but_full_G3_G4_G5_remain_open"
            ]
        )

    def test_physical_sm_five_amplitude_equality_rejects_forgery_and_pins(self):
        valid = mod._load_json_artifact(
            mod.PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_JSON
        )
        pins = {
            "raw_sha256": mod.PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_RAW_SHA256,
            "source_raw_sha256": (
                mod.PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_SOURCE_RAW_SHA256
            ),
            "test_raw_sha256": (
                mod.PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_TEST_RAW_SHA256
            ),
            "markdown_raw_sha256": (
                mod.PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_MD_RAW_SHA256
            ),
        }
        self.assertTrue(
            mod._physical_sm_five_amplitude_equality_contract(valid, **pins)[
                "source_bound"
            ]
        )
        mutations = (
            lambda value: value.__setitem__("unexpected", True),
            lambda value: value["integrity"].__setitem__(
                "core_sha256", "0" * 64
            ),
            lambda value: value["restriction"].__setitem__(
                "witness_coefficients_directly_derived_from_integer_projector_source_algebra",
                True,
            ),
            lambda value: value["exact_Groebner_certificate"].__setitem__(
                "complex_solution_count_with_multiplicity", 15
            ),
            lambda value: value["discrete_variants"].__setitem__(
                "continuous_SO10_x_U1X_x_PQ_orbit_equivalence_classified", True
            ),
            lambda value: value["closure_claims"].__setitem__(
                "full_486_field_stationary_equality_classified", True
            ),
            lambda value: value["closure_claims"].__setitem__(
                "physical_SM_G3_closed", True
            ),
            lambda value: value["remaining_scope"].pop(),
        )
        for mutate in mutations:
            forged = copy.deepcopy(valid)
            mutate(forged)
            audited = mod._physical_sm_five_amplitude_equality_contract(
                forged, **pins
            )
            self.assertFalse(audited["source_bound"])
            self.assertFalse(
                audited["five_real_amplitude_slice_stationary_equality_classified"]
            )
            self.assertFalse(audited["physical_SM_G3_closed"])
        for pin_name in pins:
            forged_pins = dict(pins)
            forged_pins[pin_name] = "0" * 64
            self.assertFalse(
                mod._physical_sm_five_amplitude_equality_contract(
                    valid, **forged_pins
                )["source_bound"]
            )

    def test_hard_projector_Hessians_are_exact_and_fail_closed(self):
        scoped = self.report["physical_SM_hard_projector_Hessians_contract"]
        self.assertTrue(scoped["source_bound"])
        self.assertEqual(scoped["exact_source_Hessian_row_count"], 10)
        self.assertEqual(scoped["remaining_active_row_count"], 27)
        self.assertTrue(scoped["all_10_O27_O44_source_Hessians_closed"])
        self.assertFalse(scoped["all_37_active_source_Hessians_closed"])
        self.assertFalse(scoped["full_witness_stationarity_rank_PSD_closed"])
        for gate in ("G3", "G4", "G5"):
            self.assertFalse(scoped[f"physical_SM_{gate}_closed"])
            self.assertEqual(
                self.report["gates"][gate]["physical_SM_hard_projector_Hessians"],
                scoped,
            )
        valid = mod._load_json_artifact(mod.PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_JSON)
        pins = {
            "raw_sha256": mod.PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_RAW_SHA256,
            "source_raw_sha256": mod.PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_SOURCE_RAW_SHA256,
            "test_raw_sha256": mod.PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_TEST_RAW_SHA256,
            "markdown_raw_sha256": mod.PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_MD_RAW_SHA256,
        }
        forged = copy.deepcopy(valid)
        forged["claims"]["exact_source_algebra_Hessians_for_all_37_active_witness_rows"] = True
        self.assertFalse(
            mod._physical_sm_hard_projector_hessians_contract(forged, **pins)["source_bound"]
        )
        forged = copy.deepcopy(valid)
        forged["certified_rows"][0]["Hessian"]["dimension"] = 485
        self.assertFalse(
            mod._physical_sm_hard_projector_hessians_contract(forged, **pins)["source_bound"]
        )

    def test_G4_G5_branch_mismatch_is_exact_not_a_global_no_go(self):
        scoped = self.report["physical_SM_G4_G5_branch_mismatch_contract"]
        self.assertTrue(scoped["source_bound"])
        self.assertTrue(scoped["exact_branch_mismatch_proved"])
        self.assertEqual(scoped["unit_rescaling_case_count"], 101)
        self.assertFalse(scoped["current_five_amplitude_target_is_canonical_physical_EW_branch"])
        self.assertFalse(scoped["global_no_go_for_other_physical_EW_branches"])
        for gate in range(4, 9):
            self.assertFalse(scoped[f"physical_SM_G{gate}_closed"])
            self.assertEqual(
                self.report["gates"][f"G{gate}"]["physical_SM_G4_G5_branch_mismatch"],
                scoped,
            )
        valid = mod._load_json_artifact(mod.PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_JSON)
        pins = {
            "raw_sha256": mod.PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_RAW_SHA256,
            "source_raw_sha256": mod.PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_SOURCE_RAW_SHA256,
            "test_raw_sha256": mod.PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_TEST_RAW_SHA256,
            "markdown_raw_sha256": mod.PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_MD_RAW_SHA256,
        }
        forged = copy.deepcopy(valid)
        forged["scope"]["global_no_go_for_all_possible_physical_EW_branches"] = True
        self.assertFalse(
            mod._physical_sm_g4_g5_branch_mismatch_contract(forged, **pins)["source_bound"]
        )
        forged = copy.deepcopy(valid)
        forged["gate_acceptance_boundary"]["G4"]["physical_SM_G4_closed"] = True
        self.assertFalse(
            mod._physical_sm_g4_g5_branch_mismatch_contract(forged, **pins)["source_bound"]
        )

    def test_last_six_make_all_37_source_Hessians_available_but_leave_G3_G5_open(self):
        scoped = self.report["physical_SM_last_six_Hessians_contract"]
        self.assertTrue(scoped["source_bound"])
        self.assertTrue(scoped["exact_last_six_source_Hessians_closed"])
        self.assertTrue(scoped["all_37_active_source_Hessians_available"])
        self.assertFalse(
            scoped["exact_37_row_aggregate_stationarity_kernel_rank_PSD_closed"]
        )
        self.assertFalse(scoped["full_486_global_equality_orbit_closed"])
        for gate in ("G3", "G4", "G5"):
            self.assertFalse(scoped[f"physical_SM_{gate}_closed"])
            self.assertEqual(
                self.report["gates"][gate]["physical_SM_last_six_Hessians"],
                scoped,
            )
        valid = mod._load_json_artifact(mod.PHYSICAL_SM_LAST_SIX_HESSIANS_JSON)
        pins = {
            "raw_sha256": mod.PHYSICAL_SM_LAST_SIX_HESSIANS_RAW_SHA256,
            "source_raw_sha256": mod.PHYSICAL_SM_LAST_SIX_HESSIANS_SOURCE_RAW_SHA256,
            "test_raw_sha256": mod.PHYSICAL_SM_LAST_SIX_HESSIANS_TEST_RAW_SHA256,
            "markdown_raw_sha256": mod.PHYSICAL_SM_LAST_SIX_HESSIANS_MD_RAW_SHA256,
        }
        forged = copy.deepcopy(valid)
        forged["claims"][
            "exact_37_row_aggregate_stationarity_kernel_rank_PSD_proved_here"
        ] = True
        self.assertFalse(
            mod._physical_sm_last_six_hessians_contract(forged, **pins)[
                "source_bound"
            ]
        )
        forged = copy.deepcopy(valid)
        forged["certified_rows"][0]["Hessian"]["dimension"] = 485
        self.assertFalse(
            mod._physical_sm_last_six_hessians_contract(forged, **pins)[
                "source_bound"
            ]
        )

    def test_37_row_aggregate_closes_local_Hessian_not_global_G3_G5(self):
        scoped = self.report["physical_SM_37_row_aggregate_contract"]
        self.assertTrue(scoped["source_bound"])
        self.assertTrue(scoped["all_37_active_Hessians_source_derived"])
        self.assertTrue(
            scoped["exact_source_aggregate_value_minus_one_and_stationary"]
        )
        self.assertEqual(scoped["exact_source_aggregate_kernel_dimension"], 38)
        self.assertEqual(scoped["exact_source_aggregate_rank"], 448)
        self.assertTrue(
            scoped["exact_source_aggregate_PSD_and_strict_mod_symmetry"]
        )
        self.assertTrue(
            scoped["source_bound_local_stationary_Hessian_problem_complete"]
        )
        self.assertFalse(scoped["full_486_global_equality_orbit_closed"])
        g6_wave = next(
            wave
            for wave in self.report["closure_waves"]
            if wave.get("gates") == ["G6"]
        )
        self.assertIn("LOCAL_SOURCE_HESSIAN_CLOSED", g6_wave["status"])
        self.assertIn("exact source-derived all-37 Hessian", g6_wave["deliverable"])
        self.assertIn("kernel/rank 38/448", g6_wave["deliverable"])
        self.assertIn("complete global equality orbit", g6_wave["deliverable"])
        self.assertIn("full scalar and fermion mass/mixing", g6_wave["deliverable"])
        self.assertNotIn("derive the scalar Hessian", g6_wave["deliverable"].lower())
        for gate in ("G3", "G4", "G5"):
            self.assertFalse(scoped[f"physical_SM_{gate}_closed"])
            self.assertEqual(
                self.report["gates"][gate]["physical_SM_37_row_aggregate"],
                scoped,
            )
        valid = mod._load_json_artifact(mod.PHYSICAL_SM_37_ROW_AGGREGATE_JSON)
        pins = {
            "raw_sha256": mod.PHYSICAL_SM_37_ROW_AGGREGATE_RAW_SHA256,
            "source_raw_sha256": mod.PHYSICAL_SM_37_ROW_AGGREGATE_SOURCE_RAW_SHA256,
            "test_raw_sha256": mod.PHYSICAL_SM_37_ROW_AGGREGATE_TEST_RAW_SHA256,
            "markdown_raw_sha256": mod.PHYSICAL_SM_37_ROW_AGGREGATE_MD_RAW_SHA256,
        }
        forged = copy.deepcopy(valid)
        forged["claims"]["physical_SM_G3_closed"] = True
        self.assertFalse(
            mod._physical_sm_37_row_aggregate_contract(forged, **pins)[
                "source_bound"
            ]
        )
        forged = copy.deepcopy(valid)
        forged["exact_kernel_and_rank"]["exact_rank"] = 447
        self.assertFalse(
            mod._physical_sm_37_row_aggregate_contract(forged, **pins)[
                "source_bound"
            ]
        )

    def test_local_equality_orbit_is_full_486_but_not_global_G3_G5(self):
        scoped = self.report["physical_SM_local_equality_orbit_contract"]
        self.assertTrue(scoped["source_bound"])
        self.assertTrue(scoped["full_486_local_stationary_orbit_classified"])
        self.assertTrue(
            scoped["full_486_local_stationary_equality_orbit_classified"]
        )
        self.assertTrue(scoped["all_16_sign_variants_one_continuous_K_orbit"])
        self.assertTrue(scoped["target_orbit_strict_local_minimum_mod_K"])
        self.assertFalse(scoped["quantitative_neighborhood_radius_proved"])
        self.assertFalse(scoped["complete_486_global_equality_orbit_classified"])
        for gate in ("G3", "G4", "G5"):
            self.assertFalse(scoped[f"physical_SM_{gate}_closed"])
            self.assertEqual(
                self.report["gates"][gate]["physical_SM_local_equality_orbit"],
                scoped,
            )
        valid = mod._load_json_artifact(mod.PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_JSON)
        pins = {
            "portable_lf_sha256": mod.PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_PORTABLE_LF_SHA256,
            "source_portable_lf_sha256": mod.PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_SOURCE_PORTABLE_LF_SHA256,
            "test_portable_lf_sha256": mod.PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_TEST_PORTABLE_LF_SHA256,
            "markdown_portable_lf_sha256": mod.PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_MD_PORTABLE_LF_SHA256,
        }
        for mutation in (
            lambda value: value["claims"].__setitem__(
                "quantitative_radius_for_U_proved", True
            ),
            lambda value: value["claims"].__setitem__(
                "complete_486_field_global_equality_orbit_classified", True
            ),
            lambda value: value["claims"].__setitem__("physical_SM_G3_closed", True),
            lambda value: value["sixteen_sign_orbit"]["rows"][0].__setitem__(
                "actual_486_coordinate_endpoint_matches_amplitude_variant", False
            ),
        ):
            forged = copy.deepcopy(valid)
            mutation(forged)
            self.assertFalse(
                mod._physical_sm_local_equality_orbit_contract(forged, **pins)[
                    "source_bound"
                ]
            )
        wrong_pins = dict(pins)
        wrong_pins["source_portable_lf_sha256"] = "0" * 64
        self.assertFalse(
            mod._physical_sm_local_equality_orbit_contract(valid, **wrong_pins)[
                "source_bound"
            ]
        )
    def test_normalized_yukawa_cgc_contract_is_scoped_and_G7_open(self):
        scoped = self.report["normalized_SO10_Yukawa_CGC_contract"]
        self.assertTrue(scoped["source_bound"])
        self.assertTrue(scoped["normalized_10_CGCs_closed"])
        self.assertTrue(scoped["normalized_126bar_CGCs_closed"])
        self.assertTrue(scoped["normalized_singlet_duality_CGC_closed"])
        self.assertTrue(scoped["canonical_304_Weyl_sparse_embedding_closed"])
        self.assertTrue(scoped["all_declared_representation_CGCs_closed"])
        self.assertFalse(scoped["flavor_boundary_values_closed"])
        self.assertFalse(scoped["SARAH_Dot_conversion_closed"])
        self.assertFalse(scoped["full_one_two_loop_Yukawa_betas_closed"])
        self.assertFalse(scoped["physical_threshold_matching_and_running_closed"])
        self.assertFalse(scoped["full_yukawa_sector_closed"])
        self.assertFalse(scoped["physical_G7_closed"])
        self.assertFalse(scoped["mathematical_G7_closed"])
        self.assertFalse(scoped["release_G7_verified"])
        self.assertEqual(self.report["gates"]["G7"]["status"], mod.STATUS_BLOCKED)

    def test_normalized_yukawa_cgc_consumer_rejects_forged_scope_and_pins(self):
        valid = mod._load_json_artifact(mod.NORMALIZED_YUKAWA_CGCS_JSON)
        pins = {
            "raw_sha256": mod.NORMALIZED_YUKAWA_CGCS_RAW_SHA256,
            "source_raw_sha256": mod.NORMALIZED_YUKAWA_CGCS_SOURCE_RAW_SHA256,
            "test_raw_sha256": mod.NORMALIZED_YUKAWA_CGCS_TEST_RAW_SHA256,
            "markdown_raw_sha256": mod.NORMALIZED_YUKAWA_CGCS_MD_RAW_SHA256,
        }
        self.assertTrue(
            mod._normalized_so10_yukawa_cgc_contract(valid, **pins)[
                "source_bound"
            ]
        )
        mutations = (
            lambda value: value.__setitem__("unexpected", True),
            lambda value: value["scope"].__setitem__("mathematical_G7", True),
            lambda value: value["scope"].__setitem__(
                "one_or_two_loop_Yukawa_betas", True
            ),
            lambda value: value["checks"].__setitem__(
                "full_physical_G7_closed", True
            ),
            lambda value: value["normalized_tensors"]["126bar"].__setitem__(
                "denominator", 4
            ),
            lambda value: value["blockers"].pop(),
        )
        for mutate in mutations:
            forged = copy.deepcopy(valid)
            mutate(forged)
            audited = mod._normalized_so10_yukawa_cgc_contract(forged, **pins)
            self.assertFalse(audited["source_bound"])
            self.assertFalse(audited["normalized_10_CGCs_closed"])
            self.assertFalse(audited["full_yukawa_sector_closed"])
            self.assertFalse(audited["physical_G7_closed"])

        forged_pin = dict(pins)
        forged_pin["source_raw_sha256"] = "0" * 64
        self.assertFalse(
            mod._normalized_so10_yukawa_cgc_contract(valid, **forged_pin)[
                "source_bound"
            ]
        )

    def test_physical_sm_heavy_vector_contract_is_scoped_and_G6_G7_open(self):
        scoped = self.report["physical_SM_heavy_vector_mass_contract"]
        self.assertTrue(scoped["source_bound"])
        self.assertTrue(scoped["exact_parameterized_tree_vector_mass_matrix_closed"])
        self.assertTrue(scoped["exact_vector_rank_kernel_and_Goldstone_image_closed"])
        self.assertTrue(scoped["exact_SU3C_x_U1em_vector_sector_resolution_closed"])
        self.assertTrue(scoped["parameterized_vector_threshold_log_inputs_closed"])
        self.assertFalse(scoped["absolute_physical_vector_masses_closed"])
        self.assertFalse(scoped["pole_vector_masses_closed"])
        self.assertFalse(scoped["vector_Goldstone_ghost_matching_closed"])
        self.assertFalse(scoped["physical_G6_closed"])
        self.assertFalse(scoped["physical_G7_closed"])
        self.assertEqual(self.report["gates"]["G6"]["status"], mod.STATUS_BLOCKED)
        self.assertEqual(self.report["gates"]["G7"]["status"], mod.STATUS_BLOCKED)

    def test_physical_sm_heavy_vector_consumer_rejects_forgery_and_pins(self):
        valid = mod._load_json_artifact(mod.PHYSICAL_SM_HEAVY_VECTOR_JSON)
        pins = {
            "raw_sha256": mod.PHYSICAL_SM_HEAVY_VECTOR_RAW_SHA256,
            "source_raw_sha256": mod.PHYSICAL_SM_HEAVY_VECTOR_SOURCE_RAW_SHA256,
            "test_raw_sha256": mod.PHYSICAL_SM_HEAVY_VECTOR_TEST_RAW_SHA256,
            "markdown_raw_sha256": mod.PHYSICAL_SM_HEAVY_VECTOR_MD_RAW_SHA256,
        }
        self.assertTrue(
            mod._physical_sm_heavy_vector_mass_contract(valid, **pins)[
                "source_bound"
            ]
        )
        mutations = (
            lambda value: value.__setitem__("unexpected", True),
            lambda value: value["scope"].__setitem__("physical_G6", True),
            lambda value: value["checks"].__setitem__(
                "pole_masses_fixed", True
            ),
            lambda value: value["source_binding"][
                "physical_SM_target_report"
            ].__setitem__("sha256", "0" * 64),
            lambda value: value["rank_kernel_Goldstone"].__setitem__(
                "exact_gram_rank", 38
            ),
            lambda value: value["blockers"].pop(),
        )
        for mutate in mutations:
            forged = copy.deepcopy(valid)
            mutate(forged)
            audited = mod._physical_sm_heavy_vector_mass_contract(
                forged, **pins
            )
            self.assertFalse(audited["source_bound"])
            self.assertFalse(
                audited["exact_parameterized_tree_vector_mass_matrix_closed"]
            )
            self.assertFalse(audited["physical_G6_closed"])
            self.assertFalse(audited["physical_G7_closed"])

        forged_pin = dict(pins)
        forged_pin["markdown_raw_sha256"] = "0" * 64
        self.assertFalse(
            mod._physical_sm_heavy_vector_mass_contract(
                valid, **forged_pin
            )["source_bound"]
        )

    def test_conditional_physical_sm_scalar_spectrum_is_scoped_G6_open(self):
        scoped = self.report[
            "conditional_physical_SM_EFT_Hessian_spectrum_contract"
        ]
        self.assertTrue(scoped["source_bound"])
        self.assertTrue(scoped["conditional_reconstructed_tree_scalar_spectrum_closed"])
        self.assertTrue(scoped["conditional_tree_Hessian_factorization_closed"])
        self.assertTrue(scoped["conditional_tree_sector_assignment_closed"])
        self.assertFalse(scoped["source_algebra_derived_tree_scalar_spectrum_closed"])
        self.assertFalse(scoped["physical_scalar_pole_spectrum_closed"])
        self.assertFalse(scoped["dimensionful_physical_scalar_masses_closed"])
        self.assertFalse(scoped["physical_G6_closed"])
        self.assertFalse(scoped["release_G6_verified"])
        self.assertEqual(self.report["gates"]["G6"]["status"], mod.STATUS_BLOCKED)

    def test_physical_sm_heavy_vector_msbar_contract_is_scoped_fail_closed(self):
        scoped = self.report[
            "physical_SM_heavy_vector_MSbar_matching_contract"
        ]
        self.assertTrue(scoped["source_bound"])
        self.assertTrue(
            scoped[
                "combined_heavy_vector_FPghost_Goldstone_MSbar_kernel_closed"
            ]
        )
        self.assertTrue(scoped["finite_MSbar_vector_constant_closed"])
        self.assertTrue(scoped["Goldstone_double_count_guard_active"])
        self.assertEqual(scoped["complex_index_totals"], {"SU3": "5/2", "QED": "32/3"})
        self.assertEqual(
            scoped["per_complex_vector_matching_formula"],
            "Delta_i=-T_i/(6*pi)+7*T_i/(2*pi)*log(M_tree/mu)",
        )
        self.assertFalse(scoped["arbitrary_Rxi_sector_resolved_matching_closed"])
        self.assertFalse(scoped["pole_mass_conversion_closed"])
        self.assertFalse(scoped["SM_symmetric_pre_EW_matching_closed"])
        self.assertFalse(scoped["complete_scalar_fermion_threshold_matching_closed"])
        self.assertFalse(scoped["physical_G6_closed"])
        self.assertFalse(scoped["physical_G7_closed"])

    def test_physical_sm_heavy_vector_msbar_consumer_rejects_forgery_and_pins(self):
        valid = mod._load_json_artifact(mod.PHYSICAL_SM_HEAVY_VECTOR_MSBAR_JSON)
        pins = {
            "raw_sha256": mod.PHYSICAL_SM_HEAVY_VECTOR_MSBAR_RAW_SHA256,
            "source_raw_sha256": (
                mod.PHYSICAL_SM_HEAVY_VECTOR_MSBAR_SOURCE_RAW_SHA256
            ),
            "test_raw_sha256": mod.PHYSICAL_SM_HEAVY_VECTOR_MSBAR_TEST_RAW_SHA256,
            "markdown_raw_sha256": (
                mod.PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MD_RAW_SHA256
            ),
        }
        self.assertTrue(
            mod._physical_sm_heavy_vector_msbar_matching_contract(valid, **pins)[
                "source_bound"
            ]
        )
        mutations = (
            lambda value: value.__setitem__("unexpected", True),
            lambda value: value["scope"].__setitem__("physical_G7", True),
            lambda value: value["checks"].__setitem__(
                "finite_MSbar_vector_constant_closed", False
            ),
            lambda value: value["exact_group_factors"][
                "complex_index_totals"
            ].__setitem__("QED", "31/3"),
            lambda value: value["gauge_parameter_obstruction"].__setitem__(
                "arbitrary_Rxi_sector_resolved_matching_closed", True
            ),
            lambda value: value["blockers"].pop(),
        )
        for mutate in mutations:
            forged = copy.deepcopy(valid)
            mutate(forged)
            audited = mod._physical_sm_heavy_vector_msbar_matching_contract(
                forged, **pins
            )
            self.assertFalse(audited["source_bound"])
            self.assertFalse(
                audited[
                    "combined_heavy_vector_FPghost_Goldstone_MSbar_kernel_closed"
                ]
            )
            self.assertFalse(audited["physical_G6_closed"])
            self.assertFalse(audited["physical_G7_closed"])

        forged_pin = dict(pins)
        forged_pin["test_raw_sha256"] = "0" * 64
        self.assertFalse(
            mod._physical_sm_heavy_vector_msbar_matching_contract(
                valid, **forged_pin
            )["source_bound"]
        )

    def test_conditional_scalar_spectrum_consumer_rejects_forgery_and_pins(self):
        valid = mod._load_json_artifact(
            mod.CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_JSON
        )
        pins = {
            "raw_sha256": mod.CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_RAW_SHA256,
            "source_raw_sha256": (
                mod.CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_SOURCE_RAW_SHA256
            ),
            "test_raw_sha256": (
                mod.CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_TEST_RAW_SHA256
            ),
            "markdown_raw_sha256": (
                mod.CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_MD_RAW_SHA256
            ),
        }
        self.assertTrue(
            mod._conditional_physical_sm_eft_hessian_spectrum_contract(
                valid, **pins
            )["source_bound"]
        )
        mutations = (
            lambda value: value.__setitem__("unexpected", True),
            lambda value: value["closure_claims"].__setitem__(
                "source_bound_physical_G6", True
            ),
            lambda value: value["proof_boundary"].__setitem__(
                "upstream_source_algebra_derivation_complete", True
            ),
            lambda value: value["kernel_and_physics_boundary"].__setitem__(
                "rho_is_a_pole_mass_squared", True
            ),
            lambda value: value["source_binding"]["foundation"].__setitem__(
                "all_terminal_foundation_pins_match", False
            ),
            lambda value: value["squared_EFT_spectrum"].__setitem__(
                "positive_root_count_with_multiplicity", 449
            ),
        )
        for mutate in mutations:
            forged = copy.deepcopy(valid)
            mutate(forged)
            audited = (
                mod._conditional_physical_sm_eft_hessian_spectrum_contract(
                    forged, **pins
                )
            )
            self.assertFalse(audited["source_bound"])
            self.assertFalse(
                audited["conditional_reconstructed_tree_scalar_spectrum_closed"]
            )
            self.assertFalse(audited["physical_G6_closed"])

        forged_pin = dict(pins)
        forged_pin["test_raw_sha256"] = "0" * 64
        self.assertFalse(
            mod._conditional_physical_sm_eft_hessian_spectrum_contract(
                valid, **forged_pin
            )["source_bound"]
        )

    def test_physical_sm_vector_rxi_contract_is_strictly_scoped(self):
        scoped = self.report[
            "physical_SM_vector_Rxi_vacuum_cancellation_contract"
        ]
        self.assertTrue(scoped["source_bound"])
        self.assertTrue(
            scoped["zero_background_Rxi_vacuum_determinant_cancellation_closed"]
        )
        self.assertTrue(scoped["all_37_broken_directions_closed"])
        self.assertTrue(scoped["Goldstone_FPghost_double_count_guard_closed"])
        self.assertFalse(scoped["background_covariant_heat_kernel_matching_closed"])
        self.assertFalse(
            scoped["sector_resolved_general_background_determinants_closed"]
        )
        self.assertFalse(scoped["pole_vector_masses_closed"])
        self.assertFalse(scoped["physical_G6_closed"])
        self.assertFalse(scoped["physical_G7_closed"])
        self.assertTrue(
            any(
                "closed exact source-derived 37-row Hessian" in blocker
                for blocker in scoped["blockers"]
            )
        )
        self.assertFalse(
            any(
                "derive the scalar Hessian" in blocker.lower()
                for blocker in scoped["blockers"]
            )
        )

    def test_physical_sm_vector_rxi_consumer_rejects_forgery_and_pins(self):
        valid = mod._load_json_artifact(mod.PHYSICAL_SM_VECTOR_RXI_JSON)
        pins = {
            "raw_sha256": mod.PHYSICAL_SM_VECTOR_RXI_RAW_SHA256,
            "source_raw_sha256": mod.PHYSICAL_SM_VECTOR_RXI_SOURCE_RAW_SHA256,
            "test_raw_sha256": mod.PHYSICAL_SM_VECTOR_RXI_TEST_RAW_SHA256,
            "markdown_raw_sha256": mod.PHYSICAL_SM_VECTOR_RXI_MD_RAW_SHA256,
        }
        self.assertTrue(
            mod._physical_sm_vector_rxi_vacuum_cancellation_contract(
                valid, **pins
            )["source_bound"]
        )
        mutations = (
            lambda value: value.__setitem__("unexpected", True),
            lambda value: value["scope"].__setitem__("physical_G7", True),
            lambda value: value["checks"].__setitem__(
                "vacuum_normalized_unphysical_determinant_is_one", False
            ),
            lambda value: value["direction_census"].__setitem__(
                "total_broken_real_directions", 36
            ),
            lambda value: value["quadratic_operator_scope"].__setitem__(
                "background", "general background"
            ),
            lambda value: value["multiplet_ledger"][0].__setitem__(
                "mass_squared", "forged"
            ),
            lambda value: value["one_real_broken_direction_theorem"][
                "effective_action_exponents"
            ].__setitem__("complex_FP_ghost_pair_on_D_xiM", "0"),
            lambda value: value["quadratic_operator_scope"].__setitem__(
                "vacuum_normalization", "forged"
            ),
            lambda value: value["blockers"].pop(),
        )
        for mutate in mutations:
            forged = copy.deepcopy(valid)
            mutate(forged)
            audited = mod._physical_sm_vector_rxi_vacuum_cancellation_contract(
                forged, **pins
            )
            self.assertFalse(audited["source_bound"])
            self.assertFalse(
                audited[
                    "zero_background_Rxi_vacuum_determinant_cancellation_closed"
                ]
            )
            self.assertFalse(audited["physical_G6_closed"])
            self.assertFalse(audited["physical_G7_closed"])
        forged_pins = dict(pins)
        forged_pins["source_raw_sha256"] = "0" * 64
        self.assertFalse(
            mod._physical_sm_vector_rxi_vacuum_cancellation_contract(
                valid, **forged_pins
            )["source_bound"]
        )

    def test_physical_sm_g6_g7_frontier_is_negative_and_fail_closed(self):
        scoped = self.report["physical_SM_G6_G7_closure_frontier_contract"]
        self.assertTrue(scoped["source_bound"])
        self.assertTrue(scoped["corrected_terminal_artifacts_composed"])
        self.assertTrue(scoped["continuous_nonidentifiability_proved"])
        self.assertTrue(scoped["minimal_closure_path_machine_readable"])
        self.assertEqual(len(scoped["minimal_closure_path"]), 7)
        self.assertFalse(scoped["unique_absolute_tree_spectrum"])
        self.assertFalse(scoped["unique_pole_spectrum"])
        self.assertFalse(scoped["unique_threshold_vector"])
        self.assertFalse(scoped["unique_full_RGE_trajectory"])
        self.assertFalse(scoped["physical_G6_closed"])
        self.assertFalse(scoped["physical_G7_closed"])

    def test_physical_sm_g6_g7_frontier_rejects_forgery_and_pins(self):
        valid = mod._load_json_artifact(mod.PHYSICAL_SM_G6_G7_FRONTIER_JSON)
        pins = {
            "raw_sha256": mod.PHYSICAL_SM_G6_G7_FRONTIER_RAW_SHA256,
            "source_raw_sha256": (
                mod.PHYSICAL_SM_G6_G7_FRONTIER_SOURCE_RAW_SHA256
            ),
            "test_raw_sha256": mod.PHYSICAL_SM_G6_G7_FRONTIER_TEST_RAW_SHA256,
            "markdown_raw_sha256": (
                mod.PHYSICAL_SM_G6_G7_FRONTIER_MD_RAW_SHA256
            ),
        }
        self.assertTrue(
            mod._physical_sm_g6_g7_closure_frontier_contract(valid, **pins)[
                "source_bound"
            ]
        )
        mutations = (
            lambda value: value.__setitem__("unexpected", True),
            lambda value: value["scope"].__setitem__("physical_G6", True),
            lambda value: value["completed_and_open_matrix"]["open"].__setitem__(
                "unique_pole_spectrum", False
            ),
            lambda value: value["exact_nonidentifiability_witnesses"][
                "vector_common_scale"
            ]["log_shift_coefficients"].__setitem__("SU3", "9"),
            lambda value: value["minimal_closure_path"].pop(),
            lambda value: value["completed_and_open_matrix"]["closed"].__setitem__(
                "forged_closed_item",
                value["completed_and_open_matrix"]["closed"].pop(
                    "standard_SU3C_x_U1em_target_and_stabilizer"
                ),
            ),
            lambda value: value["exact_nonidentifiability_witnesses"][
                "scalar_EFT_b_scale"
            ].__setitem__("source_algebra_derived", True),
            lambda value: value["exact_nonidentifiability_witnesses"][
                "flavor_boundaries"
            ].__setitem__(
                "different_two_loop_gauge_Y4_and_Yukawa_beta_terms", False
            ),
            lambda value: value["minimal_closure_path"][3].__setitem__(
                "acceptance", "forged acceptance"
            ),
        )
        for mutate in mutations:
            forged = copy.deepcopy(valid)
            mutate(forged)
            audited = mod._physical_sm_g6_g7_closure_frontier_contract(
                forged, **pins
            )
            self.assertFalse(audited["source_bound"])
            self.assertFalse(audited["continuous_nonidentifiability_proved"])
            self.assertFalse(audited["physical_G6_closed"])
            self.assertFalse(audited["physical_G7_closed"])
        forged_pins = dict(pins)
        forged_pins["markdown_raw_sha256"] = "0" * 64
        self.assertFalse(
            mod._physical_sm_g6_g7_closure_frontier_contract(
                valid, **forged_pins
            )["source_bound"]
        )

    def test_physical_sm_g8_frontier_is_negative_and_fail_closed(self):
        scoped = self.report["physical_SM_G8_identifiability_frontier_contract"]
        self.assertTrue(scoped["source_bound"])
        self.assertTrue(scoped["canonical_G8_contract_audited"])
        self.assertTrue(scoped["continuous_absolute_scale_nonidentifiability_proved"])
        self.assertTrue(scoped["flavor_and_interference_nonidentifiability_audited"])
        self.assertTrue(
            scoped["repository_frozen_PDG_2025_single_channel_constraint_verified"]
        )
        self.assertEqual(scoped["minimal_exhibited_joint_free_real_dimension"], 1)
        self.assertFalse(scoped["unique_proton_lifetime_or_distribution"])
        self.assertFalse(scoped["physical_G8_closed"])
        self.assertFalse(scoped["release_G8_verified"])
        self.assertFalse(scoped["authoritative_G8_closed"])
        self.assertFalse(scoped["whole_model_excluded_by_conditional_points"])
        self.assertFalse(scoped["all_acceptance_criteria_pass"])
        self.assertIs(
            self.report["gates"]["G8"][
                "physical_SM_G8_identifiability_frontier"
            ]["source_bound"],
            True,
        )

    def test_physical_sm_g8_frontier_rejects_forgery_and_pins(self):
        valid = mod._load_json_artifact(mod.PHYSICAL_SM_G8_FRONTIER_JSON)
        pins = {
            "raw_sha256": mod.PHYSICAL_SM_G8_FRONTIER_RAW_SHA256,
            "source_raw_sha256": mod.PHYSICAL_SM_G8_FRONTIER_SOURCE_RAW_SHA256,
            "test_raw_sha256": mod.PHYSICAL_SM_G8_FRONTIER_TEST_RAW_SHA256,
            "markdown_raw_sha256": mod.PHYSICAL_SM_G8_FRONTIER_MD_RAW_SHA256,
        }
        self.assertTrue(
            mod._physical_sm_g8_identifiability_frontier_contract(valid, **pins)[
                "source_bound"
            ]
        )
        mutations = (
            lambda value: value.__setitem__("unexpected", True),
            lambda value: value["scope"].__setitem__("physical_G8", True),
            lambda value: value["canonical_G8_definition"].__setitem__(
                "gap_id", "G8_exact_unique_proton_lifetime"
            ),
            lambda value: value["canonical_G8_definition"].__setitem__(
                "definition_sha256", "0" * 64
            ),
            lambda value: value["canonical_G8_definition"].__setitem__(
                "dependencies", []
            ),
            lambda value: value["acceptance_matrix"]["criterion_1"].__setitem__(
                "passed", True
            ),
            lambda value: value["exact_nonidentifiability_witnesses"][
                "absolute_vector_scale"
            ].__setitem__("partial_lifetime_ratio_at_fixed_dimensionless_data", "15"),
            lambda value: value["exact_nonidentifiability_witnesses"][
                "flavor_and_interference"
            ].__setitem__("flavor_tensor_values_or_textures_fixed", True),
            lambda value: value["scale_audit_0_through_100"].__setitem__(
                "case_count", 100
            ),
            lambda value: value["repository_frozen_experimental_input"].__setitem__(
                "usable_as_unique_G8_prediction", True
            ),
            lambda value: value["minimal_exhibited_free_input_vector"][
                "smallest_exhibited_joint_witness"
            ].__setitem__("real_dimension", 0),
            lambda value: value["exact_missing_inputs"].__setitem__(
                "new_laboratory_measurement_required_for_theory_gate", ["forged"]
            ),
        )
        for mutate in mutations:
            forged = copy.deepcopy(valid)
            mutate(forged)
            audited = mod._physical_sm_g8_identifiability_frontier_contract(
                forged, **pins
            )
            self.assertFalse(audited["source_bound"])
            self.assertFalse(audited["physical_G8_closed"])
            self.assertFalse(audited["release_G8_verified"])
            self.assertFalse(audited["authoritative_G8_closed"])
        forged_pins = dict(pins)
        forged_pins["source_raw_sha256"] = "0" * 64
        self.assertFalse(
            mod._physical_sm_g8_identifiability_frontier_contract(
                valid, **forged_pins
            )["source_bound"]
        )

    def test_recalculated_G7_inputs_supersede_only_stale_broad_blockers(self):
        resolution = self.report["physical_G7_recalculated_input_resolution"]
        self.assertTrue(resolution["source_bound"])
        self.assertTrue(resolution["all_resolved_scoped_inputs_closed"])
        self.assertTrue(all(resolution["resolved_scoped_inputs"].values()))
        self.assertTrue(all(resolution["superseded_stale_blockers"].values()))
        self.assertTrue(
            all(value is False for value in resolution["precise_open_inputs"].values())
        )
        self.assertFalse(resolution["physical_G6_closed"])
        self.assertFalse(resolution["mathematical_G7_closed"])
        self.assertFalse(resolution["physical_G7_closed"])
        self.assertFalse(resolution["release_G7_verified"])
        self.assertIn(
            "SARAH_implicit_Dot_to_identical_Weyl_contraction_conversion",
            resolution["precise_open_inputs"],
        )
        self.assertIn(
            "background_covariant_heat_kernel_and_general_background_determinants",
            resolution["precise_open_inputs"],
        )
        self.assertIn(
            "zero_background_Rxi_vacuum_determinant_cancellation",
            resolution["resolved_scoped_inputs"],
        )
        self.assertNotIn(
            "finite_vector_matching_constants", resolution["precise_open_inputs"]
        )

    def test_recalculated_G7_resolution_fails_closed_with_any_unbound_input(self):
        component = copy.deepcopy(
            self.report["physical_G7_component_threshold_contract"]
        )
        cgcs = copy.deepcopy(self.report["normalized_SO10_Yukawa_CGC_contract"])
        vectors = copy.deepcopy(self.report["physical_SM_heavy_vector_mass_contract"])
        vector_msbar = copy.deepcopy(
            self.report["physical_SM_heavy_vector_MSbar_matching_contract"]
        )
        vector_rxi = copy.deepcopy(
            self.report["physical_SM_vector_Rxi_vacuum_cancellation_contract"]
        )
        scalars = copy.deepcopy(
            self.report[
                "conditional_physical_SM_EFT_Hessian_spectrum_contract"
            ]
        )
        frontier = copy.deepcopy(
            self.report["physical_SM_G6_G7_closure_frontier_contract"]
        )
        for forged in (
            component,
            cgcs,
            vectors,
            vector_msbar,
            vector_rxi,
            scalars,
            frontier,
        ):
            forged["source_bound"] = False
            resolution = mod._physical_g7_recalculated_input_resolution(
                component,
                cgcs,
                vectors,
                vector_msbar,
                vector_rxi,
                scalars,
                frontier,
            )
            self.assertFalse(resolution["source_bound"])
            self.assertFalse(resolution["all_resolved_scoped_inputs_closed"])
            self.assertFalse(any(resolution["resolved_scoped_inputs"].values()))
            self.assertFalse(resolution["physical_G6_closed"])
            self.assertFalse(resolution["physical_G7_closed"])
            forged["source_bound"] = True

    def test_rank1_slice_rejects_wrong_fixed_H_orientation(self):
        forged = copy.deepcopy(
            mod._load_json_artifact(mod.G3_SU5_MAX_NEGATIVE_RANK1_SU3_SLICE_JSON)
        )
        forged["scope"]["H_fixed_to_h_minus"] = False
        report = mod._build_report_from_inputs(
            x_report=mod.exact_x.build_report(),
            g1_report=mod.gauged_g1.build_report(),
            g2_report=mod._load_or_build_gauged_g2_report(),
            filter_report=mod.gauged_filter.build_report(),
            g3_su5_max_negative_rank1_su3_slice_report=forged,
        )
        frontier = report["gauged_u1x_g3_constructive_frontier"]
        self.assertFalse(
            frontier[
                "SU5_max_negative_rank1_SU3_four_dimensional_slice_closed"
            ]
        )
        self.assertFalse(frontier["integrity_pass"])
        self.assertFalse(
            report["checks"][
                "gauged_G3_rank1_SU3_four_dimensional_slice_is_exact_and_fail_closed"
            ]
        )

    def test_fresh_contract_reports_are_integrated(self):
        reports = self.report["model_contract_reports"]
        x_report = reports["exact_X"]
        g1_report = reports["gauged_G1_character_census"]
        g2_report = reports["gauged_G2_derivative_audit"]
        filter_report = reports["gauged_scalar_filter"]
        sos_report = reports["gauged_G3_SOS_candidate"]
        pd_report = reports["gauged_G3_direct_exact_PD_rank"]
        a_square_report = reports["gauged_G3_exact_A_square_recoupling"]
        sos_bfb_report = reports["gauged_G3_exact_SOS_BFB_stationarity"]
        kernel_bound = reports["gauged_G3_fixed_P_kernel_no_go"]
        replacement = reports["gauged_G3_lower_replacement_orbit"]
        su5_pd = reports["gauged_G3_SU5_Delta_PD_global_SOS"]
        su5_hsx = reports["gauged_G3_SU5_Delta_HSX_extension"]
        su5_hsx_exact = reports["gauged_G3_SU5_Delta_HSX_exact_Hessian"]
        su5_equality = reports["gauged_G3_SU5_Delta_equality_orbit"]
        su5_phi_orbit = reports[
            "gauged_G3_SU5_Delta_Phi_orbit_lemma_audit"
        ]
        su5_phi_local = reports[
            "gauged_G3_SU5_Delta_Phi_local_component_theorem"
        ]
        su5_phi_su3 = reports[
            "gauged_G3_SU5_Delta_Phi_SU3_fixed_slice_theorem"
        ]
        su5_gap = reports["gauged_G3_SU5_Delta_chiral_global_gap"]
        fixed_f_bound = reports["gauged_G3_SU5_fixed_F_full_offkernel_bound"]
        max_negative_bound = reports[
            "gauged_G3_SU5_max_negative_all_zero_residual_bound"
        ]
        max_negative_full_bound = reports[
            "gauged_G3_SU5_max_negative_full_residual_pure_Delta_bound"
        ]
        rank1_su3_bound = reports[
            "gauged_G3_SU5_max_negative_rank1_SU3_four_dimensional_slice_bound"
        ]
        rank1_su4_stabilizer = reports[
            "gauged_G3_rank1_SU4_stabilizer_infrastructure"
        ]
        rank1_su4_intertwiners = reports[
            "gauged_G3_rank1_SU4_Phi210_intertwiner_infrastructure"
        ]
        rank1_su4_aligned = reports[
            "gauged_G3_rank1_SU4_aligned_carrier_infrastructure"
        ]
        rank1_su4_quadratic = reports[
            "gauged_G3_rank1_SU4_Phi210_quadratic_basis"
        ]
        rank1_su4_census = reports[
            "gauged_G3_rank1_SU4_augmented_SOS_census"
        ]
        rank1_su4_cubic = reports[
            "gauged_G3_rank1_SU4_augmented_SOS_cubic_map"
        ]
        rank1_su4_quartic = reports[
            "gauged_G3_rank1_SU4_augmented_SOS_quartic_map"
        ]
        rank1_su4_psd_target = reports[
            "gauged_G3_rank1_SU4_legacy_v20_PSD_routes_and_rejected_target"
        ]
        rank1_su4_corrected = reports[
            "gauged_G3_rank1_SU4_corrected_fixed_endpoint_publication_v21"
        ]
        alternative_sos = reports["gauged_G3_alternative_global_SOS_audit"]
        self.assertEqual(x_report["n_failed"], 0)
        self.assertIs(
            x_report["contract_consistent"], self.report["contract_consistent"]
        )
        self.assertEqual(
            x_report["blocker"],
            None if self.report["contract_consistent"] else mod.CONTRACT_BLOCKER,
        )
        self.assertEqual(g1_report["model_contract_id"], mod.AUTHORITATIVE_CONTRACT_ID)
        self.assertEqual(g1_report["counts"]["hermitian_conjugacy_orbits"], 28)
        self.assertEqual(g1_report["counts"]["total_potential_orbit_multiplicity"], 44)
        self.assertEqual(g1_report["counts"]["total_real_potential_parameters"], 51)
        self.assertEqual(g2_report["n_failed"], 0, g2_report["failures"])
        self.assertEqual(g2_report["counts"]["invariant_directions"], 44)
        self.assertEqual(g2_report["counts"]["real_parameters"], 51)
        self.assertEqual(g2_report["counts"]["real_field_dimension"], 486)
        self.assertEqual(g2_report["counts"]["Hessian_shape_per_parameter"], [486, 486])
        self.assertTrue(g2_report["flags"]["G2_gauged_u1x_derivatives_certified"])
        self.assertTrue(
            filter_report["declared_symmetry_contract"]["continuous_X_imposed"]
        )
        self.assertEqual(sos_report["n_failed"], 0, sos_report["failures"])
        self.assertEqual(pd_report["n_failed"], 0, pd_report["failures"])
        self.assertEqual(
            a_square_report["status"], "EXACT_A_SQUARE_RECOUPLING_CERTIFIED"
        )
        self.assertEqual(sos_bfb_report["n_failed"], 0)
        self.assertEqual(kernel_bound["n_failed"], 0)
        self.assertEqual(replacement["n_failed"], 0)
        self.assertEqual(su5_pd["n_failed"], 0)
        self.assertEqual(su5_hsx["n_failed"], 0)
        self.assertEqual(su5_hsx_exact["n_failed"], 0)
        self.assertEqual(su5_equality["n_failed"], 0)
        self.assertEqual(su5_phi_orbit["n_failed"], 0)
        self.assertEqual(su5_phi_local["n_failed"], 0)
        self.assertEqual(su5_phi_su3["n_failed"], 0)
        self.assertEqual(su5_gap["n_failed"], 0)
        self.assertEqual(fixed_f_bound["n_failed"], 0)
        self.assertEqual(max_negative_bound["n_failed"], 0)
        self.assertEqual(
            max_negative_bound["exact_stratum_gap"]["strict_margin"],
            "7859/140295000",
        )
        self.assertEqual(max_negative_full_bound["n_failed"], 0)
        self.assertEqual(
            max_negative_full_bound["scope"]["restricted_gap_global_minimum"],
            "1/5000",
        )
        self.assertEqual(rank1_su3_bound["n_failed"], 0)
        self.assertEqual(
            rank1_su3_bound["model_contract_id"], mod.AUTHORITATIVE_CONTRACT_ID
        )
        self.assertTrue(rank1_su3_bound["scope"]["H_fixed_to_h_minus"])
        self.assertEqual(rank1_su3_bound["scope"]["Phi_slice_real_dimension"], 4)
        self.assertEqual(
            rank1_su3_bound["scope"]["full_SU3_fixed_space_real_dimension"],
            16,
        )
        self.assertEqual(
            rank1_su3_bound["radial_patch"]["restricted_global_minimum"],
            "1/5000",
        )
        self.assertFalse(rank1_su3_bound["checks"]["arbitrary_rank1_Phi_proved"])
        self.assertFalse(rank1_su3_bound["checks"]["arbitrary_Sigma35_proved"])
        self.assertFalse(rank1_su3_bound["checks"]["G3_closed"])
        self.assertEqual(rank1_su4_stabilizer["n_failed"], 0)
        self.assertTrue(rank1_su4_stabilizer["scope"]["infrastructure_only"])
        self.assertFalse(rank1_su4_stabilizer["scope"]["G3_closed"])
        self.assertEqual(rank1_su4_intertwiners["n_failed"], 0)
        self.assertEqual(
            rank1_su4_intertwiners["carriers"][
                "Sym2_Phi210_SU4_singlet_dimension"
            ],
            45,
        )
        self.assertFalse(
            rank1_su4_intertwiners["scope"]["Schur_SOS_SDP_constructed"]
        )
        self.assertFalse(rank1_su4_intertwiners["scope"]["G3_closed"])
        self.assertEqual(
            rank1_su4_aligned["alignment"][
                "concatenated_aligned_basis_rank_mod_prime"
            ],
            210,
        )
        self.assertTrue(
            rank1_su4_aligned["scope"][
                "physical_real_structure_and_Gaussian_embeddings_constructed"
            ]
        )
        self.assertEqual(
            rank1_su4_quadratic["constraint_system"]["reduced_constraint_shape"],
            [5952, 551],
        )
        self.assertEqual(
            rank1_su4_quadratic["constraint_system"]["exact_rational_rank"], 506
        )
        self.assertEqual(
            rank1_su4_quadratic["constraint_system"]["exact_rational_nullity"], 45
        )
        self.assertFalse(
            rank1_su4_quadratic["scope"][
                "augmented_homogeneous_Schur_SOS_SDP_constructed"
            ]
        )
        self.assertEqual(
            rank1_su4_census["augmented_representation"][
                "augmented_homogeneous_dimension"
            ],
            22_366,
        )
        self.assertEqual(
            rank1_su4_census["augmented_representation"][
                "complex_irreducible_copy_count"
            ],
            824,
        )
        self.assertEqual(
            rank1_su4_census["augmented_representation"][
                "Schur_real_parameter_count"
            ],
            19_594,
        )
        self.assertEqual(
            rank1_su4_census["invariant_quartic_target"][
                "invariant_equation_count"
            ],
            6_585,
        )
        self.assertFalse(
            rank1_su4_census["scope"][
                "Schur_coordinate_6585_by_19594_coefficient_matrix_constructed"
            ]
        )
        self.assertEqual(
            rank1_su4_cubic["cubic_coordinate_map"]["coordinate_map_shape"],
            [478, 1_414],
        )
        self.assertEqual(
            rank1_su4_cubic["cubic_coordinate_map"]["exact_rank"], 478
        )
        self.assertEqual(
            rank1_su4_cubic["cubic_coordinate_map"]["exact_kernel_dimension"],
            936,
        )
        self.assertTrue(
            rank1_su4_cubic["cubic_coordinate_map"][
                "abstract_zero_placeholder_is_not_a_physical_G3_target"
            ]
        )
        self.assertFalse(
            rank1_su4_cubic["scope"][
                "physical_G3_gap_target_vector_constructed"
            ]
        )
        self.assertFalse(rank1_su4_cubic["scope"]["G3_closed"])
        self.assertEqual(
            rank1_su4_quartic["coefficient_map_certificate"]["shape"],
            [6_057, 18_085],
        )
        self.assertEqual(
            rank1_su4_quartic["coefficient_map_certificate"]["rank_over_Q_exact"],
            6_057,
        )
        self.assertEqual(
            rank1_su4_quartic["coefficient_map_certificate"][
                "kernel_dimension_over_Q_exact"
            ],
            12_028,
        )
        self.assertFalse(
            rank1_su4_quartic["scope"]["physical_quartic_target_constructed"]
        )
        self.assertFalse(rank1_su4_quartic["scope"]["G3_closed"])
        self.assertTrue(
            rank1_su4_psd_target["scope"][
                "all_22_standard_PSD_coordinate_routes_constructed"
            ]
        )
        self.assertEqual(
            rank1_su4_psd_target["standard_PSD_coordinate_routes"][
                "standard_total_parameter_count"
            ],
            19_594,
        )
        self.assertTrue(
            mod.corrected_rank1.corrected_fixed_endpoint_theorem_exact(
                rank1_su4_corrected
            )
        )
        self.assertFalse(
            rank1_su4_psd_target["scope"]["semidefinite_feasibility_solved"]
        )
        self.assertFalse(rank1_su4_psd_target["scope"]["G3_closed"])
        self.assertEqual(alternative_sos["n_failed"], 0)

    def test_constructive_g3_frontier_is_present_but_fail_closed(self):
        frontier = self.report["gauged_u1x_g3_constructive_frontier"]
        self.assertTrue(all(frontier["artifacts_present"].values()))
        self.assertTrue(frontier["integrity_pass"])
        self.assertTrue(frontier["exact_A_square_recoupling_source_bound"])
        self.assertTrue(frontier["exact_SOS_BFB_stationarity_source_bound"])
        self.assertTrue(frontier["direct_exact_PD_rank_honestly_scoped"])
        self.assertTrue(
            frontier["SOS_candidate_exact_local_and_globally_rejected"]
        )
        self.assertTrue(frontier["fixed_P_branch_exactly_excluded"])
        self.assertTrue(
            frontier["lower_replacement_rejected_for_wrong_symmetry"]
        )
        self.assertTrue(frontier["SU5_Delta_PD_exact_global_frontier"])
        self.assertEqual(frontier["SU5_Delta_PD_exact_Hessian_rank"], 429)
        self.assertEqual(frontier["SU5_Delta_PD_exact_Hessian_nullity"], 33)
        self.assertTrue(frontier["SU5_Delta_PD_full_486_extension_open"])
        self.assertFalse(
            frontier["SU5_Delta_PD_disconnected_equality_orbits_open"]
        )
        self.assertTrue(
            frontier["SU5_Delta_PD_equality_orbits_classified_exactly"]
        )
        self.assertTrue(frontier["SU5_Delta_HSX_honest_frontier"])
        self.assertEqual(frontier["SU5_Delta_HSX_nonzero_real_parameters"], 28)
        self.assertEqual(
            frontier["SU5_Delta_HSX_maximum_absolute_coefficient"], 11.0
        )
        self.assertEqual(
            frontier["SU5_Delta_HSX_exact_symmetry_ranks"], [36, 37, 38]
        )
        self.assertEqual(frontier["SU5_Delta_HSX_transverse_dimension"], 448)
        self.assertGreater(
            frontier["SU5_Delta_HSX_minimum_transverse_eigenvalue_numeric"],
            0.0,
        )
        self.assertFalse(frontier["SU5_Delta_HSX_full_Hessian_proof_grade"])
        self.assertTrue(frontier["SU5_Delta_HSX_exact_Hessian_closed"])
        self.assertEqual(frontier["SU5_Delta_HSX_exact_Hessian_rank"], 448)
        self.assertEqual(frontier["SU5_Delta_HSX_exact_Hessian_nullity"], 38)
        self.assertTrue(frontier["SU5_Delta_HSX_exact_Hessian_PSD"])
        self.assertTrue(
            frontier["SU5_Delta_HSX_exact_Hessian_kernel_is_symmetry"]
        )
        self.assertTrue(frontier["SU5_Delta_HSX_exact_quotient_positive"])
        self.assertTrue(frontier["SU5_Delta_HSX_full_quartic_BFB_exact"])
        self.assertTrue(frontier["SU5_Delta_HSX_finite_field_global_gap_open"])
        self.assertTrue(
            frontier["SU5_Delta_HSX_global_equality_classification_open"]
        )
        self.assertTrue(frontier["SU5_Delta_equality_honestly_reduced"])
        self.assertTrue(frontier["SU5_Delta_Phi_orbit_audit_honest"])
        self.assertTrue(frontier["SU5_Delta_literal_single_Phi_orbit_refuted"])
        self.assertFalse(frontier["SU5_Delta_signed_Phi_orbit_theorem_open"])
        self.assertTrue(frontier["SU5_Delta_signed_Phi_orbit_theorem_closed"])
        self.assertTrue(frontier["SU5_Delta_SU4_Phi_slice_classified"])
        self.assertTrue(frontier["SU5_Delta_signed_Phi_local_components_closed"])
        self.assertTrue(frontier["SU5_Delta_distant_Phi_components_excluded"])
        self.assertTrue(frontier["SU5_Delta_Phi_SU3_fixed_slice_closed"])
        self.assertEqual(frontier["SU5_Delta_Phi_SU3_fixed_slice_dimension"], 16)
        self.assertTrue(frontier["SU5_Delta_fixed_F_Sigma_one_orbit_exact"])
        self.assertTrue(
            frontier["SU5_Delta_diagonal_Phi_slice_one_orbit_exact"]
        )
        self.assertFalse(frontier["SU5_Delta_global_Phi_orbit_lemma_open"])
        self.assertTrue(frontier["SU5_Delta_global_Phi_orbit_lemma_closed"])
        self.assertEqual(
            frontier["SU5_Delta_global_Phi_orbit_theorem_core_sha256"],
            "db493a74303a57862f09c2a92118ea3d66b8b12ecbaea9162155d4ab3baafecc",
        )
        self.assertTrue(
            frontier["SU5_Delta_chiral_global_gap_honestly_reduced"]
        )
        self.assertFalse(frontier["SU5_Delta_chiral_lower_witness_found"])
        self.assertTrue(frontier["SU5_Delta_chiral_small_beta_route_exists"])
        self.assertFalse(
            frontier["SU5_Delta_chiral_beta_1_over_20_global_certified"]
        )
        self.assertFalse(
            frontier["SU5_Delta_chiral_final_acceptance_test_passes"]
        )
        self.assertTrue(frontier["SU5_fixed_F_full_offkernel_gap_closed"])
        self.assertTrue(frontier["SU5_fixed_F_gap_equality_is_selected_flag"])
        self.assertTrue(frontier["SU5_arbitrary_Phi_offstratum_gap_open"])
        self.assertTrue(
            frontier["SU5_max_negative_all_zero_residual_route_excluded"]
        )
        self.assertEqual(
            frontier["SU5_max_negative_all_zero_residual_strict_margin"],
            "7859/140295000",
        )
        self.assertTrue(
            frontier["SU5_max_negative_pure_Delta_full_residual_gap_closed"]
        )
        self.assertEqual(
            frontier["SU5_max_negative_pure_Delta_full_residual_minimum"],
            "1/5000",
        )
        self.assertTrue(
            frontier[
                "SU5_max_negative_rank1_SU3_four_dimensional_slice_closed"
            ]
        )
        self.assertEqual(
            frontier["SU5_max_negative_rank1_SU3_slice_dimension"], 4
        )
        self.assertEqual(
            frontier["SU5_max_negative_rank1_SU3_ambient_dimension"], 16
        )
        self.assertEqual(
            frontier["SU5_max_negative_rank1_SU3_slice_minimum"], "1/5000"
        )
        self.assertTrue(frontier["SU5_max_negative_arbitrary_rank1_Phi_open"])
        self.assertTrue(
            frontier["SU5_max_negative_arbitrary_Sigma_orientation_open"]
        )
        self.assertTrue(frontier["rank1_SU4_stabilizer_infrastructure_exact"])
        self.assertEqual(frontier["rank1_SU4_joint_stabilizer_dimension"], 15)
        self.assertTrue(
            frontier["rank1_SU4_Phi210_intertwiner_infrastructure_exact"]
        )
        self.assertEqual(frontier["rank1_SU4_Phi210_carrier_count"], 25)
        self.assertEqual(frontier["rank1_SU4_Sym2_invariant_dimension"], 45)
        self.assertTrue(frontier["rank1_SU4_aligned_carriers_exact"])
        self.assertEqual(frontier["rank1_SU4_aligned_direct_sum_rank"], 210)
        self.assertTrue(frontier["rank1_SU4_physical_real_maps_exact"])
        self.assertTrue(frontier["rank1_SU4_Phi210_quadratic_basis_exact"])
        self.assertEqual(
            frontier["rank1_SU4_quadratic_constraint_shape"], [5952, 551]
        )
        self.assertEqual(frontier["rank1_SU4_quadratic_constraint_rank"], 506)
        self.assertEqual(frontier["rank1_SU4_quadratic_constraint_nullity"], 45)
        self.assertEqual(frontier["rank1_SU4_quadratic_basis_count"], 45)
        self.assertEqual(frontier["rank1_SU4_quadratic_basis_rank"], 45)
        self.assertTrue(frontier["rank1_SU4_quadratic_live_invariance_exact"])
        self.assertTrue(frontier["rank1_SU4_Schur_SOS_SDP_open"])
        self.assertTrue(frontier["rank1_SU4_arbitrary_Phi_bound_open"])
        self.assertTrue(frontier["rank1_SU4_augmented_SOS_census_exact"])
        self.assertEqual(
            frontier["rank1_SU4_augmented_homogeneous_dimension"], 22_366
        )
        self.assertEqual(
            frontier["rank1_SU4_augmented_complex_isotypic_type_count"], 35
        )
        self.assertEqual(
            frontier["rank1_SU4_augmented_complex_irreducible_copy_count"], 824
        )
        self.assertEqual(
            frontier["rank1_SU4_augmented_real_isotypic_block_count"], 22
        )
        self.assertEqual(
            frontier["rank1_SU4_augmented_Schur_real_parameter_count"], 19_594
        )
        self.assertEqual(
            frontier["rank1_SU4_augmented_invariant_equation_count"], 6_585
        )
        self.assertTrue(frontier["rank1_SU4_augmented_coordinate_Schur_map_open"])
        self.assertTrue(frontier["rank1_SU4_augmented_isotypic_maps_open"])
        self.assertTrue(frontier["rank1_SU4_augmented_physical_target_open"])
        self.assertTrue(frontier["rank1_SU4_augmented_Schur_SOS_SDP_open"])
        self.assertTrue(frontier["rank1_SU4_augmented_arbitrary_Phi_bound_open"])
        self.assertTrue(frontier["rank1_SU4_augmented_cubic_map_exact"])
        self.assertEqual(
            frontier["rank1_SU4_augmented_cubic_coordinate_map_shape"],
            [478, 1_414],
        )
        self.assertEqual(
            frontier["rank1_SU4_augmented_cubic_coordinate_map_rank"], 478
        )
        self.assertEqual(
            frontier[
                "rank1_SU4_augmented_cubic_coordinate_map_kernel_dimension"
            ],
            936,
        )
        self.assertTrue(
            frontier["rank1_SU4_augmented_cubic_zero_placeholder_nonphysical"]
        )
        self.assertTrue(
            frontier["rank1_SU4_augmented_cubic_other_graded_maps_open"]
        )
        self.assertTrue(
            frontier["rank1_SU4_augmented_cubic_physical_target_open"]
        )
        self.assertTrue(
            frontier["rank1_SU4_augmented_cubic_Schur_SOS_SDP_open"]
        )
        self.assertTrue(frontier["rank1_SU4_augmented_cubic_G3_open"])
        self.assertTrue(frontier["rank1_SU4_augmented_quartic_map_exact"])
        self.assertEqual(
            frontier["rank1_SU4_augmented_quartic_coordinate_map_shape"],
            [6_057, 18_085],
        )
        self.assertEqual(
            frontier["rank1_SU4_augmented_quartic_coordinate_map_rank"], 6_057
        )
        self.assertEqual(
            frontier[
                "rank1_SU4_augmented_quartic_coordinate_map_kernel_dimension"
            ],
            12_028,
        )
        self.assertTrue(
            frontier["rank1_SU4_augmented_quartic_physical_target_open"]
        )
        self.assertTrue(
            frontier[
                "rank1_SU4_augmented_quartic_standard_PSD_congruences_open"
            ]
        )
        self.assertTrue(frontier["rank1_SU4_augmented_quartic_SDP_open"])
        self.assertTrue(frontier["rank1_SU4_augmented_quartic_G3_open"])
        self.assertTrue(
            frontier[
                "rank1_SU4_legacy_v20_PSD_routes_and_stale_payload_well_formed"
            ]
        )
        self.assertFalse(frontier["rank1_SU4_legacy_v20_physical_target_valid"])
        self.assertFalse(frontier["rank1_SU4_legacy_v20_primal_valid"])
        self.assertEqual(
            frontier["rank1_SU4_augmented_standard_PSD_route_count"], 22
        )
        self.assertEqual(
            frontier["rank1_SU4_augmented_standard_PSD_parameter_count"],
            19_594,
        )
        self.assertTrue(frontier["rank1_SU4_corrected_fixed_endpoint_theorem_exact"])
        self.assertEqual(
            frontier["rank1_SU4_corrected_positive_Gram_map_shape"],
            [6_585, 19_594],
        )
        self.assertEqual(
            frontier["rank1_SU4_corrected_positive_Gram_map_common_denominator"],
            256,
        )
        self.assertEqual(
            frontier["rank1_SU4_corrected_positive_Gram_map_nnz"], 138_550
        )
        self.assertEqual(
            frontier["rank1_SU4_corrected_physical_target_common_denominator"],
            576_000,
        )
        self.assertEqual(
            frontier["rank1_SU4_corrected_physical_target_nonzero_count"], 512
        )
        self.assertEqual(
            frontier["rank1_SU4_corrected_exact_coefficient_equalities"], 6_585
        )
        self.assertEqual(
            frontier["rank1_SU4_corrected_strict_positive_Gram_blocks"], 22
        )
        self.assertEqual(
            frontier["rank1_SU4_corrected_strict_positive_LDL_pivots"], 824
        )
        self.assertTrue(
            frontier["rank1_SU4_corrected_arbitrary_real_Phi_at_fixed_endpoint"]
        )
        self.assertFalse(frontier["rank1_SU4_corrected_global_Sigma_proved"])
        self.assertFalse(frontier["rank1_SU4_corrected_general_H_proved"])
        self.assertFalse(frontier["rank1_SU4_corrected_full_Hessian_proved"])
        self.assertFalse(frontier["rank1_SU4_corrected_G3_closed"])
        self.assertFalse(
            frontier["SU5_arbitrary_Phi_nonzero_residual_cancellations_open"]
        )
        self.assertTrue(
            frontier[
                "SU5_arbitrary_non_pure_Delta_Sigma_uniform_coercivity_open"
            ]
        )
        self.assertTrue(frontier["SU5_arbitrary_Phi_uniform_coercivity_open"])
        self.assertTrue(frontier["alternative_global_SOS_audit_honestly_open"])
        self.assertTrue(
            frontier["all_vanishing_global_SOS_replacements_excluded"]
        )
        self.assertFalse(
            frontier["nonvanishing_residual_global_SOS_replacements_excluded"]
        )
        self.assertEqual(frontier["candidate_nonzero_real_parameters"], 27)
        self.assertEqual(frontier["candidate_real_parameter_count"], 51)
        self.assertEqual(frontier["candidate_maximum_absolute_coefficient"], 9.125)
        self.assertEqual(frontier["candidate_J0"], "-21/200")
        self.assertEqual(frontier["exact_PD_rank"], 429)
        self.assertEqual(frontier["exact_PD_nullity"], 33)
        self.assertEqual(frontier["exact_full_Hessian_rank"], 448)
        self.assertTrue(frontier["direct_exact_PD_source_binding"])
        self.assertTrue(frontier["complete_potential_BFB_exactly_certified"])
        self.assertTrue(frontier["selected_vacuum_stationarity_exactly_certified"])
        self.assertTrue(frontier["strict_local_minimum_certified"])
        self.assertFalse(frontier["global_minimum_certified"])
        self.assertTrue(frontier["selected_global_minimum_disproved"])
        self.assertTrue(frontier["exact_lower_energy_field_witness_certified"])
        self.assertTrue(frontier["constructive_candidate_rejected_for_G3"])
        self.assertFalse(frontier["global_uniqueness_certified"])
        self.assertFalse(frontier["G3_closed"])
        self.assertFalse(frontier["whole_model_validated"])
        self.assertFalse(frontier["whole_model_excluded"])
        self.assertTrue(
            self.report["checks"][
                "gauged_G3_rank1_SU3_four_dimensional_slice_is_exact_and_fail_closed"
            ]
        )
        self.assertTrue(
            self.report["checks"][
                "gauged_G3_rank1_SU4_infrastructure_is_exact_and_fail_closed"
            ]
        )
        self.assertEqual(self.report["gates"]["G3"]["status"], mod.STATUS_OPEN)
        self.assertEqual(
            self.report["gates"]["G3"]["constructive_frontier_evidence"],
            frontier,
        )

    def test_source_bound_g1_ring_and_g2_derivative_audit_are_scoped(self):
        scoped = self.report["gauged_u1x_scalar_subtheorems"]
        self.assertEqual(scoped["model_contract_id"], mod.AUTHORITATIVE_CONTRACT_ID)
        self.assertFalse(scoped["whole_model_gate_closure"])
        self.assertEqual(
            scoped["G1"]["scoped_status"],
            "COMPLETE_GAUGED_U1X_FULL_COMPONENT_TENSOR_INTEGRATION",
        )
        self.assertTrue(scoped["G1"]["multiplicity_census_complete"])
        self.assertTrue(
            scoped["G1"]["explicit_component_tensor_subset_integration_complete"]
        )
        self.assertTrue(scoped["G1"]["mathematical_component_tensor_closure_complete"])
        self.assertTrue(scoped["G1"]["character_census_remains_multiplicity_only"])
        self.assertTrue(scoped["G1"]["full_G1_closed"])
        self.assertTrue(scoped["G1"]["authoritative_G1_promoted_closed"])
        self.assertTrue(scoped["G1"]["release_G1_verified"])
        self.assertEqual(scoped["G1"]["invariant_directions"], 44)
        self.assertEqual(scoped["G1"]["real_potential_parameters"], 51)
        closure = self.report["renormalizable_G1_component_tensor_closure"]
        self.assertTrue(closure["source_bound"])
        self.assertTrue(
            closure["mathematical_G1_closed_for_renormalizable_model"]
        )
        consistent = self.report["contract_consistent"]
        # This frozen theorem records mathematical closure only; authoritative
        # promotion is performed by the live ledger after exact-X validation.
        self.assertFalse(closure["authoritative_G1_promoted_closed"])
        self.assertFalse(closure["release_G1_verified"])
        self.assertTrue(closure["downstream_integration_completed"])
        self.assertIn(mod.CONTRACT_BLOCKER, closure["release_blockers"])
        self.assertNotIn(
            "G1_COMPONENT_TENSOR_CLOSURE_DOWNSTREAM_INTEGRATION_REQUIRED",
            closure["release_blockers"],
        )
        self.assertTrue(scoped["G2"]["scoped_derivative_audit_complete"])
        self.assertFalse(scoped["G2"]["authoritative_promotion_blocked_on_full_G1"])
        self.assertIs(
            scoped["G2"]["authoritative_promotion_blocked_on_model_contract"],
            not consistent,
        )
        self.assertEqual(scoped["G2"]["invariant_directions"], 44)
        self.assertEqual(scoped["G2"]["real_potential_parameters"], 51)
        self.assertEqual(scoped["G2"]["real_field_dimension"], 486)
        self.assertEqual(scoped["G2"]["promoted_stationarity_rank"], 13)
        self.assertEqual(scoped["G2"]["promoted_stationarity_nullity"], 38)
        self.assertFalse(scoped["G2"]["raw_dense_rank_14_certified"])
        self.assertTrue(scoped["G2"]["exact_Delta_R_projector_zero_certificate"])
        self.assertTrue(
            scoped["G2"]["exact_projector_zero_corrected_normalized_SVD_rank_13"]
        )
        self.assertTrue(scoped["G2"]["stationarity_rank_13_exactly_certified"])
        self.assertTrue(scoped["G2"]["stationarity_nullity_38_exactly_certified"])
        self.assertFalse(scoped["G2"]["G3_closed"])
        for gate_name in ("G1", "G2"):
            gate = self.report["gates"][gate_name]
            self.assertEqual(
                gate["status"], mod.STATUS_CLOSED if consistent else mod.STATUS_BLOCKED
            )
            self.assertTrue(gate["scoped_calculation_complete"])
        self.assertTrue(
            self.report["gates"]["G1"]["full_gate_calculation_complete"]
        )
        if not consistent:
            self.assertEqual(
                self.report["gates"]["G1"]["open_scope"],
                [
                    "obtain a real hash-bound external SARAH execution attestation for authoritative G1 promotion"
                ],
            )
        self.assertTrue(
            self.report["gates"]["G2"]["full_gate_calculation_complete"]
        )

    def test_legacy_gate_frontier_tracks_contract_state(self):
        gates = self.report["gates"]
        self.assertEqual(set(gates), {f"G{i}" for i in range(1, 9)})
        if self.report["contract_consistent"]:
            self.assertEqual(self.report["summary"]["closed"], ["G1", "G2", "G5"])
            self.assertEqual(self.report["summary"]["open"], ["G3"])
            self.assertEqual(
                self.report["summary"]["blocked"], ["G4", "G6", "G7", "G8"]
            )
        else:
            self.assertTrue(
                all(row["status"] == mod.STATUS_BLOCKED for row in gates.values())
            )
            self.assertEqual(self.report["summary"]["closed"], [])
            self.assertEqual(self.report["summary"]["blocked"], list(gates))

    def test_wave_zero_model_contract_precedes_g1(self):
        self.assertTrue(mod._acyclic_dependencies())
        self.assertEqual(self.report["dependencies"]["MODEL_CONTRACT"], [])
        self.assertEqual(self.report["dependencies"]["G1"], ["MODEL_CONTRACT"])
        wave0 = self.report["closure_waves"][0]
        self.assertEqual(wave0["wave"], 0)
        self.assertEqual(wave0["id"], "MODEL_CONTRACT")
        self.assertEqual(
            wave0["status"],
            mod.STATUS_CLOSED
            if self.report["contract_consistent"]
            else mod.STATUS_BLOCKED,
        )

    def test_historical_g1_g2_results_are_preserved_but_scoped(self):
        historical = self.report["historical_option_c_subtheorems"]
        self.assertEqual(historical["model_contract_id"], mod.HISTORICAL_CONTRACT_ID)
        self.assertFalse(historical["authoritative_for_gauged_model"])
        self.assertEqual(
            set(historical["source_contract_ids"].values()),
            {mod.HISTORICAL_CONTRACT_ID},
        )
        self.assertEqual(historical["G1"]["base_tensor_families"], 18)
        self.assertEqual(historical["G1"]["invariant_directions"], 64)
        self.assertEqual(historical["G1"]["real_potential_parameters"], 91)
        self.assertEqual(historical["G2"]["real_field_dimension"], 486)
        self.assertEqual(historical["G2"]["dense_Hessian_shape"], [486, 486])

    def test_historical_g3_saddle_and_search_facts_are_not_erased(self):
        g3 = self.report["historical_option_c_subtheorems"]["G3"]
        self.assertEqual(g3["massive_physical_quotient_dimension"], 449)
        self.assertEqual(g3["anchored_witness_negative_modes"], 46)
        self.assertEqual(g3["anchored_witness_zero_modes"], 0)
        self.assertEqual(g3["anchored_witness_positive_modes"], 403)
        self.assertEqual(g3["stationary_affine_dimension"], 77)
        self.assertEqual(g3["stability_search_iterations"], 80)
        self.assertEqual(
            g3["best_minimum_equilibrated_eigenvalue"],
            -0.025502339625368114,
        )
        self.assertFalse(g3["strict_local_minimum_found"])
        self.assertFalse(g3["whole_gauged_model_excluded"])

    def test_no_whole_model_validation_or_exclusion_claim(self):
        feasibility = self.report["feasibility"]
        self.assertEqual(
            feasibility["current_authoritative_closed_gates"],
            3 if self.report["contract_consistent"] else 0,
        )
        self.assertFalse(feasibility["guarantee_model_survives_recertification"])
        self.assertTrue(
            feasibility["gauged_G1_multiplicity_census_complete"]
        )
        self.assertTrue(
            feasibility["gauged_G1_full_component_tensor_integration_complete"]
        )
        self.assertTrue(
            feasibility["gauged_G2_dense_derivative_scoped_subtheorem_complete"]
        )
        self.assertFalse(feasibility["whole_model_validated"])
        self.assertFalse(feasibility["whole_model_excluded"])
        self.assertTrue(feasibility["gauged_G3_constructive_candidate_available"])
        self.assertTrue(
            feasibility["gauged_G3_direct_exact_source_binding_complete"]
        )

    def test_repaired_contract_promotes_source_bound_g1_g2_and_g5_only(self):
        inputs = self.report["model_contract_reports"]
        repaired_x = copy.deepcopy(inputs["exact_X"])
        repaired_x.update(
            contract_consistent=True,
            blocker=None,
            scientific_blockers=[],
            contract_conflicts=[],
            overall_state="PASS",
        )
        repaired_x["flag"]["contract_consistent"] = True
        repaired_x["flag"]["x_selection_rule_consistently_declared"] = True
        _bind_tool_native_root_evidence(repaired_x)

        report = mod._build_report_from_inputs(
            x_report=repaired_x,
            g1_report=inputs["gauged_G1_character_census"],
            g2_report=inputs["gauged_G2_derivative_audit"],
            filter_report=inputs["gauged_scalar_filter"],
            g3_sos_report=inputs["gauged_G3_SOS_candidate"],
            g3_pd_report=inputs["gauged_G3_direct_exact_PD_rank"],
            g3_a_square_report=inputs["gauged_G3_exact_A_square_recoupling"],
            g3_sos_bfb_report=inputs["gauged_G3_exact_SOS_BFB_stationarity"],
        )

        self.assertEqual(report["n_failed"], 0, report["audit_failures"])
        self.assertEqual(report["overall_state"], mod.STATUS_OPEN)
        self.assertEqual(report["summary"]["closed"], ["G1", "G2", "G5"])
        self.assertEqual(report["summary"]["open"], ["G3"])
        self.assertEqual(
            report["summary"]["blocked"],
            ["G4", "G6", "G7", "G8"],
        )
        self.assertEqual(
            {name: row["status"] for name, row in report["gates"].items()},
            {
                "G1": mod.STATUS_CLOSED,
                "G2": mod.STATUS_CLOSED,
                "G3": mod.STATUS_OPEN,
                "G4": mod.STATUS_BLOCKED,
                "G5": mod.STATUS_CLOSED,
                "G6": mod.STATUS_BLOCKED,
                "G7": mod.STATUS_BLOCKED,
                "G8": mod.STATUS_BLOCKED,
            },
        )

    def test_repaired_contract_cannot_bypass_drifted_g1_theorem(self):
        inputs = self.report["model_contract_reports"]
        repaired_x = copy.deepcopy(inputs["exact_X"])
        repaired_x.update(
            contract_consistent=True,
            blocker=None,
            scientific_blockers=[],
            contract_conflicts=[],
            overall_state="PASS",
        )
        repaired_x["flag"]["contract_consistent"] = True
        repaired_x["flag"]["x_selection_rule_consistently_declared"] = True
        _bind_tool_native_root_evidence(repaired_x)
        drifted = copy.deepcopy(inputs["gauged_G1_component_tensor_closure"])
        drifted["core_sha256"] = "0" * 64

        report = mod._build_report_from_inputs(
            x_report=repaired_x,
            g1_report=inputs["gauged_G1_character_census"],
            g1_component_tensor_report=drifted,
            g1_component_tensor_raw_sha256=(
                mod.RENORMALIZABLE_G1_COMPONENT_TENSOR_RAW_SHA256
            ),
            g1_component_tensor_source_raw_sha256=(
                mod.RENORMALIZABLE_G1_COMPONENT_TENSOR_SOURCE_RAW_SHA256
            ),
            g2_report=inputs["gauged_G2_derivative_audit"],
            filter_report=inputs["gauged_scalar_filter"],
        )

        self.assertGreater(report["n_failed"], 0)
        self.assertFalse(
            report["renormalizable_G1_component_tensor_closure"]["source_bound"]
        )
        self.assertEqual(report["gates"]["G1"]["status"], mod.STATUS_OPEN)
        self.assertEqual(report["gates"]["G2"]["status"], mod.STATUS_BLOCKED)
        self.assertEqual(report["gates"]["G2"]["unsatisfied_dependencies"], ["G1"])
        self.assertEqual(report["gates"]["G3"]["unsatisfied_dependencies"], ["G2"])
        self.assertEqual(
            report["gates"]["G5"]["unsatisfied_dependencies"], ["G1", "G2"]
        )
        self.assertEqual(report["gates"]["G7"]["unsatisfied_dependencies"], ["G6"])
        self.assertNotIn(mod.CONTRACT_BLOCKER, report["scientific_blockers"])
        self.assertIn(
            "G1_EXPLICIT_COMPONENT_TENSOR_INTEGRATION_OPEN",
            report["scientific_blockers"],
        )
        self.assertFalse(
            report["gauged_u1x_scalar_subtheorems"]["promoted_to_authoritative_G1_G2"]
        )
        self.assertIn("full G1 remains OPEN", report["verdict"])

    def test_unbound_boolean_cannot_promote_model_contract(self):
        inputs = self.report["model_contract_reports"]
        forged = copy.deepcopy(inputs["exact_X"])
        forged.update(
            contract_consistent=True,
            blocker=None,
            scientific_blockers=[],
            contract_conflicts=[],
            overall_state="PASS",
        )
        forged["external_model_validation"]["valid"] = False
        forged["external_model_validation"]["fresh_for_exact_model_bytes"] = False
        report = mod._build_report_from_inputs(
            x_report=forged,
            g1_report=inputs["gauged_G1_character_census"],
            g2_report=inputs["gauged_G2_derivative_audit"],
            filter_report=inputs["gauged_scalar_filter"],
            g3_sos_report=inputs["gauged_G3_SOS_candidate"],
            g3_pd_report=inputs["gauged_G3_direct_exact_PD_rank"],
            g3_a_square_report=inputs["gauged_G3_exact_A_square_recoupling"],
            g3_sos_bfb_report=inputs["gauged_G3_exact_SOS_BFB_stationarity"],
        )
        self.assertFalse(report["contract_evidence_complete"])
        self.assertFalse(report["contract_consistent"])
        self.assertNotEqual(report["overall_state"], mod.STATUS_OPEN)
        self.assertIn(
            "consistent_contract_requires_tool_native_bound_evidence",
            report["audit_failures"],
        )

    def test_dropped_pd_source_binding_breaks_fail_closed_frontier(self):
        inputs = self.report["model_contract_reports"]
        forged_pd = copy.deepcopy(inputs["gauged_G3_direct_exact_PD_rank"])
        forged_pd["flags"]["direct_exact_source_binding"] = False
        report = mod._build_report_from_inputs(
            x_report=inputs["exact_X"],
            g1_report=inputs["gauged_G1_character_census"],
            g2_report=inputs["gauged_G2_derivative_audit"],
            filter_report=inputs["gauged_scalar_filter"],
            g3_sos_report=inputs["gauged_G3_SOS_candidate"],
            g3_pd_report=forged_pd,
            g3_a_square_report=inputs["gauged_G3_exact_A_square_recoupling"],
            g3_sos_bfb_report=inputs["gauged_G3_exact_SOS_BFB_stationarity"],
        )
        self.assertEqual(report["overall_state"], "EXECUTION_FAIL")
        self.assertFalse(
            report["gauged_u1x_g3_constructive_frontier"][
                "direct_exact_PD_rank_honestly_scoped"
            ]
        )
        self.assertIn(
            "gauged_G3_direct_exact_PD_rank_is_honestly_scoped",
            report["audit_failures"],
        )

    def test_rank1_slice_cannot_overclaim_arbitrary_sigma_or_g3(self):
        inputs = self.report["model_contract_reports"]
        forged = copy.deepcopy(
            inputs[
                "gauged_G3_SU5_max_negative_rank1_SU3_four_dimensional_slice_bound"
            ]
        )
        forged["checks"]["arbitrary_Sigma35_proved"] = True
        report = mod._build_report_from_inputs(
            x_report=inputs["exact_X"],
            g1_report=inputs["gauged_G1_character_census"],
            g2_report=inputs["gauged_G2_derivative_audit"],
            filter_report=inputs["gauged_scalar_filter"],
            g3_su5_max_negative_rank1_su3_slice_report=forged,
        )
        self.assertEqual(report["overall_state"], "EXECUTION_FAIL")
        self.assertFalse(
            report["gauged_u1x_g3_constructive_frontier"][
                "SU5_max_negative_rank1_SU3_four_dimensional_slice_closed"
            ]
        )
        self.assertIn(
            "gauged_G3_rank1_SU3_four_dimensional_slice_is_exact_and_fail_closed",
            report["audit_failures"],
        )

    def test_rank1_su4_infrastructure_mutations_fail_closed(self):
        inputs = self.report["model_contract_reports"]
        stabilizer = inputs["gauged_G3_rank1_SU4_stabilizer_infrastructure"]
        intertwiners = inputs[
            "gauged_G3_rank1_SU4_Phi210_intertwiner_infrastructure"
        ]
        mutations = []

        forged_stabilizer = copy.deepcopy(stabilizer)
        forged_stabilizer["scope"]["G3_closed"] = True
        mutations.append((forged_stabilizer, copy.deepcopy(intertwiners)))

        forged_intertwiners = copy.deepcopy(intertwiners)
        forged_intertwiners["scope"]["Schur_SOS_SDP_constructed"] = True
        mutations.append((copy.deepcopy(stabilizer), forged_intertwiners))

        forged_intertwiners = copy.deepcopy(intertwiners)
        forged_intertwiners["companion_stabilizer_provenance"][
            "all_required_provenance_exact"
        ] = False
        mutations.append((copy.deepcopy(stabilizer), forged_intertwiners))

        forged_intertwiners = copy.deepcopy(intertwiners)
        forged_intertwiners["intertwiner"]["intertwining_count"] = 14
        mutations.append((copy.deepcopy(stabilizer), forged_intertwiners))

        for forged_stabilizer, forged_intertwiners in mutations:
            with self.subTest(
                stabilizer_G3=forged_stabilizer["scope"]["G3_closed"],
                sdp=forged_intertwiners["scope"]["Schur_SOS_SDP_constructed"],
                provenance=forged_intertwiners[
                    "companion_stabilizer_provenance"
                ]["all_required_provenance_exact"],
                count=forged_intertwiners["intertwiner"]["intertwining_count"],
            ):
                report = mod._build_report_from_inputs(
                    x_report=inputs["exact_X"],
                    g1_report=inputs["gauged_G1_character_census"],
                    g2_report=inputs["gauged_G2_derivative_audit"],
                    filter_report=inputs["gauged_scalar_filter"],
                    g3_rank1_su4_stabilizer_report=forged_stabilizer,
                    g3_rank1_su4_phi210_intertwiners_report=forged_intertwiners,
                )
                frontier = report["gauged_u1x_g3_constructive_frontier"]
                self.assertEqual(report["overall_state"], "EXECUTION_FAIL")
                self.assertFalse(frontier["integrity_pass"])
                self.assertFalse(
                    frontier[
                        "rank1_SU4_Phi210_intertwiner_infrastructure_exact"
                    ]
                )
                self.assertIn(
                    "gauged_G3_rank1_SU4_infrastructure_is_exact_and_fail_closed",
                    report["audit_failures"],
                )

    def test_rank1_su4_predicates_reject_schema_and_stale_aggregates(self):
        inputs = self.report["model_contract_reports"]
        stabilizer = inputs["gauged_G3_rank1_SU4_stabilizer_infrastructure"]
        intertwiners = inputs[
            "gauged_G3_rank1_SU4_Phi210_intertwiner_infrastructure"
        ]

        stabilizer_mutations = (
            lambda value: value["checks"].__setitem__(
                "unexpected_new_critical_check", False
            ),
            lambda value: value["joint_stabilizer_tangent"].__setitem__(
                "displayed_kernel_residual_max_abs", 1
            ),
            lambda value: value["joint_stabilizer_tangent"].__setitem__(
                "joint_tangent_rank_mod_prime", 29
            ),
            lambda value: value["Phi210_action"].__setitem__(
                "skew_transpose_max_abs_residual", 1
            ),
            lambda value: value["Lie_algebra"].__setitem__(
                "Jacobi_max_abs_residual", 1
            ),
            lambda value: value["generator_basis"].__setitem__(
                "coefficient_rank_mod_prime", 14
            ),
            lambda value: value["generator_basis"].__setitem__("prime", 4),
            lambda value: value["joint_stabilizer_tangent"].__setitem__(
                "prime", 4
            ),
            lambda value: value["Phi210_action"].__setitem__("prime", 4),
            lambda value: value["generator_basis"]["ordered_labels"].__setitem__(
                0, "WRONG"
            ),
            lambda value: value["Phi210_action"]["ordered_labels"].__setitem__(
                0, "WRONG"
            ),
        )
        for mutate in stabilizer_mutations:
            forged = copy.deepcopy(stabilizer)
            mutate(forged)
            self.assertFalse(
                mod._rank1_su4_stabilizer_infrastructure_exact(forged),
                mutate.__code__.co_firstlineno,
            )

        intertwiner_mutations = (
            lambda value: value["checks"].__setitem__(
                "unexpected_new_critical_check", False
            ),
            lambda value: value["companion_stabilizer_provenance"].__setitem__(
                "module", "quarantined_or_wrong.py"
            ),
            lambda value: value["integral_C8"].__setitem__(
                "minimal_polynomial_annihilates_exact", False
            ),
            lambda value: value["integral_C8"].__setitem__(
                "modular_nullities_sum", 0
            ),
            lambda value: value["integral_C8"].__setitem__("modular_prime", 4),
            lambda value: value["carriers"].__setitem__(
                "all_carrier_dimensions_eigenvalues_characters_exact", False
            ),
            lambda value: value["carriers"].__setitem__(
                "future_Schur_SDP_multiplicity_matrix_dimension", 45
            ),
            lambda value: value["intertwiner"]["intertwinings"][0].__setitem__(
                "generator", "WRONG"
            ),
        )
        for mutate in intertwiner_mutations:
            forged = copy.deepcopy(intertwiners)
            mutate(forged)
            self.assertFalse(
                mod._rank1_su4_phi210_intertwiners_exact(forged, stabilizer),
                mutate.__code__.co_firstlineno,
            )

        forged_stabilizer = copy.deepcopy(stabilizer)
        forged_intertwiners = copy.deepcopy(intertwiners)
        forged_stabilizer["joint_stabilizer_tangent"]["fixed_endpoint"][
            "H"
        ] = "wrong_H"
        forged_intertwiners["companion_stabilizer_provenance"]["fixed_endpoint"][
            "H"
        ] = "wrong_H"
        self.assertFalse(
            mod._rank1_su4_stabilizer_infrastructure_exact(forged_stabilizer)
        )
        self.assertFalse(
            mod._rank1_su4_phi210_intertwiners_exact(
                forged_intertwiners,
                forged_stabilizer,
            )
        )

    def test_rank1_su4_stage2_predicates_reject_adversarial_mutations(self):
        inputs = self.report["model_contract_reports"]
        stabilizer = inputs["gauged_G3_rank1_SU4_stabilizer_infrastructure"]
        intertwiners = inputs[
            "gauged_G3_rank1_SU4_Phi210_intertwiner_infrastructure"
        ]
        aligned = inputs["gauged_G3_rank1_SU4_aligned_carrier_infrastructure"]
        quadratic = inputs["gauged_G3_rank1_SU4_Phi210_quadratic_basis"]

        aligned_mutations = (
            lambda value: value["scope"].__setitem__("G3_closed", True),
            lambda value: value["checks"].__setitem__(
                "aligned_25_carrier_direct_sum_rank_210_exact", False
            ),
            lambda value: value["alignment"].__setitem__(
                "concatenated_aligned_basis_rank_mod_prime", 209
            ),
            lambda value: value["alignment"]["carriers"][0].__setitem__(
                "physical_conjugation_embedding_exact", False
            ),
            lambda value: value["upstream_provenance"].__setitem__(
                "upstream_report_sha256", "0" * 64
            ),
            lambda value: value["upstream_provenance"][
                "source_contract"
            ].__setitem__("upstream_module_sha256", "0" * 64),
            lambda value: (
                value["alignment"].__setitem__("carrier_count", 24),
                value["alignment_provenance"].__setitem__(
                    "certificate_sha256",
                    mod._canonical_json_sha256(value["alignment"]),
                ),
                value["alignment_provenance"].__setitem__(
                    "expected_live_certificate_sha256",
                    mod._canonical_json_sha256(value["alignment"]),
                ),
            ),
        )
        for mutate in aligned_mutations:
            forged = copy.deepcopy(aligned)
            mutate(forged)
            self.assertFalse(
                mod._rank1_su4_aligned_carriers_exact(
                    forged, intertwiners, stabilizer
                ),
                mutate.__code__.co_firstlineno,
            )

        quadratic_mutations = (
            lambda value: value["scope"].__setitem__(
                "augmented_homogeneous_Schur_SOS_SDP_constructed", True
            ),
            lambda value: value["constraint_system"].__setitem__(
                "reduced_constraint_shape", [5951, 551]
            ),
            lambda value: value["constraint_system"].__setitem__(
                "exact_rational_rank", 505
            ),
            lambda value: value["quadratic_basis"].__setitem__(
                "matrix_count", 44
            ),
            lambda value: value["quadratic_basis"].__setitem__(
                "all_45_commute_with_all_15_live_Phi210_generators_exact", False
            ),
            lambda value: value["construction_metadata"][
                "selected_candidate_indices"
            ].__setitem__(0, 72),
            lambda value: value["reconstruction_api"].__setitem__(
                "basis_accessor", "forged()"
            ),
            lambda value: value["source_provenance"].__setitem__(
                "intertwiner_module_sha256", "0" * 64
            ),
            lambda value: value["scope"].__setitem__(
                "arbitrary_real_Phi_lower_bound_proved", True
            ),
            lambda value: value["scope"].__setitem__(
                "arbitrary_rank1_Phi_proved", True
            ),
            lambda value: value["scope"].__setitem__("G3_closed", True),
            lambda value: value["scope"].__setitem__(
                "whole_model_validated", True
            ),
            lambda value: value["scope"].__setitem__(
                "whole_model_excluded", True
            ),
        )
        for mutate in quadratic_mutations:
            forged = copy.deepcopy(quadratic)
            mutate(forged)
            self.assertFalse(
                mod._rank1_su4_phi210_quadratic_basis_exact(
                    forged, stabilizer, intertwiners, aligned
                ),
                mutate.__code__.co_firstlineno,
            )

        forged = copy.deepcopy(quadratic)
        forged["scope"]["G3_closed"] = True
        report = mod._build_report_from_inputs(
            x_report=inputs["exact_X"],
            g1_report=inputs["gauged_G1_character_census"],
            g2_report=inputs["gauged_G2_derivative_audit"],
            filter_report=inputs["gauged_scalar_filter"],
            g3_rank1_su4_stabilizer_report=stabilizer,
            g3_rank1_su4_phi210_intertwiners_report=intertwiners,
            g3_rank1_su4_aligned_carriers_report=aligned,
            g3_rank1_su4_phi210_quadratic_basis_report=forged,
        )
        self.assertEqual(report["overall_state"], "EXECUTION_FAIL")
        self.assertFalse(
            report["gauged_u1x_g3_constructive_frontier"][
                "rank1_SU4_Phi210_quadratic_basis_exact"
            ]
        )
        self.assertFalse(
            report["gauged_u1x_g3_constructive_frontier"][
                "rank1_SU4_augmented_quartic_map_exact"
            ]
        )

    def test_rank1_su4_augmented_census_rejects_every_physical_overclaim(self):
        inputs = self.report["model_contract_reports"]
        stabilizer = inputs["gauged_G3_rank1_SU4_stabilizer_infrastructure"]
        intertwiners = inputs[
            "gauged_G3_rank1_SU4_Phi210_intertwiner_infrastructure"
        ]
        aligned = inputs["gauged_G3_rank1_SU4_aligned_carrier_infrastructure"]
        quadratic = inputs["gauged_G3_rank1_SU4_Phi210_quadratic_basis"]
        census = inputs["gauged_G3_rank1_SU4_augmented_SOS_census"]

        mutations = [
            lambda value: value.__setitem__("status", "FORGED"),
            lambda value: value.__setitem__("n_failed", 1),
            lambda value: value["checks"].__setitem__("unexpected_check", True),
            lambda value: value["checks"].__setitem__(
                "universal_GL211_equivariant_section_exact", False
            ),
            lambda value: value["source_provenance"].__setitem__(
                "aligned_source_sha256", "0" * 64
            ),
            lambda value: value["source_provenance"].__setitem__(
                "quadratic_report_sha256", "0" * 64
            ),
            lambda value: value["augmented_representation"].__setitem__(
                "complex_isotypic_type_count", 34
            ),
            lambda value: value["augmented_representation"].__setitem__(
                "Schur_real_parameter_count", 19_593
            ),
            lambda value: value["invariant_quartic_target"].__setitem__(
                "invariant_equation_count", 6_584
            ),
            lambda value: value["abstract_coefficient_map_census"].__setitem__(
                "abstract_total_rank_exact", 6_584
            ),
        ]
        false_scope = (
            "all_35_isotypic_type_maps_spanning_824_irreducible_copies_constructed",
            "ordered_invariant_cubic_basis_constructed",
            "ordered_invariant_quartic_basis_constructed",
            "Schur_coordinate_6585_by_19594_coefficient_matrix_constructed",
            "physical_G3_gap_target_vector_constructed",
            "physical_G3_gap_cubic_zero_RHS_certified",
            "augmented_Schur_SOS_SDP_constructed",
            "augmented_Schur_SOS_SDP_feasibility_certified",
            "augmented_Schur_SOS_SDP_infeasibility_certified",
            "arbitrary_real_Phi_lower_bound_proved",
            "arbitrary_rank1_Phi_proved",
            "G3_closed",
            "whole_model_validated",
            "whole_model_excluded",
        )
        mutations.extend(
            lambda value, key=key: value["scope"].__setitem__(key, True)
            for key in false_scope
        )
        for mutate in mutations:
            forged = copy.deepcopy(census)
            mutate(forged)
            self.assertFalse(
                mod._rank1_su4_augmented_sos_census_exact(
                    forged, stabilizer, intertwiners, aligned, quadratic
                )
            )

        forged = copy.deepcopy(census)
        forged["scope"]["G3_closed"] = True
        report = mod._build_report_from_inputs(
            x_report=inputs["exact_X"],
            g1_report=inputs["gauged_G1_character_census"],
            g2_report=inputs["gauged_G2_derivative_audit"],
            filter_report=inputs["gauged_scalar_filter"],
            g3_rank1_su4_stabilizer_report=stabilizer,
            g3_rank1_su4_phi210_intertwiners_report=intertwiners,
            g3_rank1_su4_aligned_carriers_report=aligned,
            g3_rank1_su4_phi210_quadratic_basis_report=quadratic,
            g3_rank1_su4_augmented_sos_census_report=forged,
        )
        self.assertEqual(report["overall_state"], "EXECUTION_FAIL")
        self.assertFalse(
            report["gauged_u1x_g3_constructive_frontier"][
                "rank1_SU4_augmented_SOS_census_exact"
            ]
        )
        self.assertFalse(
            report["gauged_u1x_g3_constructive_frontier"][
                "rank1_SU4_augmented_quartic_map_exact"
            ]
        )

    def test_rank1_su4_augmented_cubic_map_is_canonical_and_fail_closed(self):
        inputs = self.report["model_contract_reports"]
        stabilizer = inputs["gauged_G3_rank1_SU4_stabilizer_infrastructure"]
        intertwiners = inputs[
            "gauged_G3_rank1_SU4_Phi210_intertwiner_infrastructure"
        ]
        aligned = inputs["gauged_G3_rank1_SU4_aligned_carrier_infrastructure"]
        quadratic = inputs["gauged_G3_rank1_SU4_Phi210_quadratic_basis"]
        census = inputs["gauged_G3_rank1_SU4_augmented_SOS_census"]
        cubic = inputs["gauged_G3_rank1_SU4_augmented_SOS_cubic_map"]

        self.assertTrue(
            mod._rank1_su4_augmented_sos_cubic_map_exact(
                cubic, stabilizer, intertwiners, aligned, quadratic, census
            )
        )
        mutations = [
            lambda value: value.__setitem__("status", "FORGED"),
            lambda value: value.__setitem__("n_failed", 1),
            lambda value: value["checks"].__setitem__("unexpected_check", True),
            lambda value: value["source_provenance"].__setitem__(
                "census_report_sha256", "0" * 64
            ),
            lambda value: value["source_provenance"].__setitem__(
                "quadratic_basis_sha256", "0" * 64
            ),
            lambda value: value["source_provenance"].__setitem__(
                "live_target_invariant_grade_counts", [1, 4, 45, 477, 6_058]
            ),
            lambda value: value["Sym2_target_carriers"].__setitem__(
                "total_complex_carrier_copy_count", 539
            ),
            lambda value: value["Sym2_target_carriers"]["families"][0].__setitem__(
                "nullity", 44
            ),
            lambda value: value["contragredient_pairings"].__setitem__(
                "all_15_compact_tensor_equations_exact", False
            ),
            lambda value: value["physical_cubic_domain"].__setitem__(
                "physical_basis_count", 1_413
            ),
            lambda value: value["physical_cubic_domain"][
                "all_22_augmented_block_rows"
            ][0].__setitem__("constructed_physical_basis_variable_count", 179),
            lambda value: value["cubic_coordinate_map"].__setitem__(
                "coordinate_map_sha256", "f" * 64
            ),
            lambda value: value["cubic_coordinate_map"].__setitem__(
                "coordinate_map_shape", [477, 1_414]
            ),
            lambda value: value["cubic_coordinate_map"].__setitem__(
                "exact_rank", 477
            ),
            lambda value: value["cubic_coordinate_map"].__setitem__(
                "exact_kernel_dimension", 937
            ),
            lambda value: value["cubic_coordinate_map"].__setitem__(
                "selected_minor_determinant_nonzero_mod_prime", False
            ),
            lambda value: value["cubic_coordinate_map"].__setitem__(
                "abstract_zero_interface_placeholder_nnz", 1
            ),
            lambda value: value["cubic_coordinate_map"].__setitem__(
                "abstract_zero_placeholder_is_not_a_physical_G3_target", False
            ),
            lambda value: value["exact_arithmetic_safety"].__setitem__(
                "proof_grade", False
            ),
        ]
        true_scope = (
            "H_fixed_to_h_minus",
            "Sigma_fixed_to_q_over_4",
            "rank1_endpoint_SU4_stabilizer_used",
            "all_1414_real_structure_fixed_cubic_Schur_cross_variables_constructed",
            "explicit_478_by_1414_cubic_coordinate_map_constructed",
            "cubic_map_rank_478_and_kernel_dimension_936_exact",
            "abstract_478_coordinate_zero_placeholder_available",
        )
        false_scope = (
            "degree_zero_coefficient_map_constructed",
            "degree_one_coefficient_map_constructed",
            "degree_two_coefficient_map_constructed",
            "degree_four_coefficient_map_constructed",
            "full_6585_by_19594_Schur_coordinate_matrix_constructed",
            "physical_G3_gap_target_vector_constructed",
            "physical_G3_gap_cubic_zero_RHS_certified",
            "augmented_Schur_SOS_SDP_constructed",
            "augmented_Schur_SOS_SDP_feasibility_certified",
            "augmented_Schur_SOS_SDP_infeasibility_certified",
            "arbitrary_real_Phi_lower_bound_proved",
            "arbitrary_rank1_Phi_proved",
            "G3_closed",
            "whole_model_validated",
            "whole_model_excluded",
        )
        mutations.extend(
            lambda value, key=key: value["scope"].__setitem__(key, False)
            for key in true_scope
        )
        mutations.extend(
            lambda value, key=key: value["scope"].__setitem__(key, True)
            for key in false_scope
        )
        for field in (
            "physical_G3_gap_target_vector_constructed",
            "physical_G3_gap_cubic_zero_RHS_certified",
        ):
            mutations.append(
                lambda value, field=field: value["cubic_coordinate_map"].__setitem__(
                    field, True
                )
            )
        for field in (
            "census_physical_G3_gap_target_vector_constructed",
            "census_physical_G3_gap_cubic_zero_RHS_certified",
        ):
            mutations.append(
                lambda value, field=field: value["source_provenance"].__setitem__(
                    field, True
                )
            )
        for mutate in mutations:
            forged = copy.deepcopy(cubic)
            mutate(forged)
            self.assertFalse(
                mod._rank1_su4_augmented_sos_cubic_map_exact(
                    forged, stabilizer, intertwiners, aligned, quadratic, census
                ),
                mutate.__code__.co_firstlineno,
            )

        forged = copy.deepcopy(cubic)
        forged["cubic_coordinate_map"][
            "physical_G3_gap_target_vector_constructed"
        ] = True
        report = mod._build_report_from_inputs(
            x_report=inputs["exact_X"],
            g1_report=inputs["gauged_G1_character_census"],
            g2_report=inputs["gauged_G2_derivative_audit"],
            filter_report=inputs["gauged_scalar_filter"],
            g3_rank1_su4_stabilizer_report=stabilizer,
            g3_rank1_su4_phi210_intertwiners_report=intertwiners,
            g3_rank1_su4_aligned_carriers_report=aligned,
            g3_rank1_su4_phi210_quadratic_basis_report=quadratic,
            g3_rank1_su4_augmented_sos_census_report=census,
            g3_rank1_su4_augmented_sos_cubic_map_report=forged,
        )
        frontier = report["gauged_u1x_g3_constructive_frontier"]
        self.assertEqual(report["overall_state"], "EXECUTION_FAIL")
        self.assertFalse(frontier["integrity_pass"])
        self.assertFalse(frontier["rank1_SU4_augmented_cubic_map_exact"])
        self.assertFalse(frontier["rank1_SU4_augmented_quartic_map_exact"])
        self.assertFalse(
            report["checks"][
                "gauged_G3_rank1_SU4_infrastructure_is_exact_and_fail_closed"
            ]
        )

    def test_rank1_su4_augmented_quartic_map_is_canonical_and_fail_closed(self):
        inputs = self.report["model_contract_reports"]
        census = inputs["gauged_G3_rank1_SU4_augmented_SOS_census"]
        cubic = inputs["gauged_G3_rank1_SU4_augmented_SOS_cubic_map"]
        quartic = inputs["gauged_G3_rank1_SU4_augmented_SOS_quartic_map"]

        self.assertTrue(
            mod._rank1_su4_augmented_sos_quartic_map_exact(
                quartic, census, cubic
            )
        )
        mutations = (
            lambda value: value.__setitem__("status", "FORGED"),
            lambda value: value["scope"].__setitem__("G3_closed", True),
            lambda value: value["scope"].__setitem__(
                "physical_quartic_target_constructed", True
            ),
            lambda value: value["scope"].__setitem__(
                "standard_PSD_congruences_for_real_type_fixed_bases_constructed",
                True,
            ),
            lambda value: value["scope"].__setitem__(
                "semidefinite_feasibility_solved", True
            ),
            lambda value: value["dimensions"].__setitem__(
                "quartic_kernel", 12_029
            ),
            lambda value: value["provenance"].__setitem__(
                "cubic_source_sha256_canonical_LF", "0" * 64
            ),
            lambda value: value["carrier_certificate"].__setitem__(
                "irreducible_copy_count", 797
            ),
            lambda value: value["pairing_certificate"].__setitem__(
                "real_block_count", 21
            ),
            lambda value: value["realification_certificate"].__setitem__(
                "domain_dimension", 18_084
            ),
            lambda value: value["coefficient_map_certificate"].__setitem__(
                "shape", [6_056, 18_085]
            ),
            lambda value: value["coefficient_map_certificate"].__setitem__(
                "nnz", 115_640
            ),
            lambda value: value["coefficient_map_certificate"].__setitem__(
                "rank_over_Q_exact", 6_056
            ),
            lambda value: value["coefficient_map_certificate"].__setitem__(
                "kernel_dimension_over_Q_exact", 12_029
            ),
            lambda value: value["coefficient_map_certificate"].__setitem__(
                "coordinate_map_sha256", "f" * 64
            ),
            lambda value: value["coefficient_map_certificate"].__setitem__(
                "unexpected_schema_key", True
            ),
        )
        for mutate in mutations:
            forged = copy.deepcopy(quartic)
            mutate(forged)
            self.assertFalse(
                mod._rank1_su4_augmented_sos_quartic_map_exact(
                    forged, census, cubic
                ),
                mutate.__code__.co_firstlineno,
            )

        forged = copy.deepcopy(quartic)
        forged["scope"]["semidefinite_feasibility_solved"] = True
        report = mod._build_report_from_inputs(
            x_report=inputs["exact_X"],
            g1_report=inputs["gauged_G1_character_census"],
            g2_report=inputs["gauged_G2_derivative_audit"],
            filter_report=inputs["gauged_scalar_filter"],
            g3_rank1_su4_augmented_sos_quartic_map_report=forged,
        )
        frontier = report["gauged_u1x_g3_constructive_frontier"]
        self.assertEqual(report["overall_state"], "EXECUTION_FAIL")
        self.assertFalse(frontier["integrity_pass"])
        self.assertFalse(frontier["rank1_SU4_augmented_quartic_map_exact"])
        self.assertFalse(
            report["checks"][
                "gauged_G3_rank1_SU4_infrastructure_is_exact_and_fail_closed"
            ]
        )

    def test_rank1_su4_corrected_endpoint_supersedes_v20_target_fail_closed(self):
        inputs = self.report["model_contract_reports"]
        census = inputs["gauged_G3_rank1_SU4_augmented_SOS_census"]
        cubic = inputs["gauged_G3_rank1_SU4_augmented_SOS_cubic_map"]
        quartic = inputs["gauged_G3_rank1_SU4_augmented_SOS_quartic_map"]
        psd_target = inputs[
            "gauged_G3_rank1_SU4_legacy_v20_PSD_routes_and_rejected_target"
        ]
        corrected_publication = inputs[
            "gauged_G3_rank1_SU4_corrected_fixed_endpoint_publication_v21"
        ]

        self.assertFalse(
            mod._rank1_su4_augmented_sos_psd_target_exact(
                psd_target, census, cubic, quartic
            )
        )
        self.assertTrue(
            mod._rank1_su4_augmented_sos_psd_routes_and_stale_payload_well_formed(
                psd_target, census, cubic, quartic
            )
        )
        self.assertTrue(
            mod.corrected_rank1.corrected_fixed_endpoint_theorem_exact(
                corrected_publication
            )
        )
        verdict = self.report["verdict"]
        self.assertIn("legacy v20 assembled physical target is rejected", verdict)
        self.assertIn("corrected 6585x19594 standard positive-Gram map", verdict)
        self.assertIn("strict 22-block/824-pivot primal", verdict)
        self.assertIn("every real Phi210", verdict)
        self.assertIn(
            "For that historical fixed-H/Sigma frontier, global Sigma, "
            "general/full H, and its then-unassembled Hessian remained open",
            verdict,
        )
        self.assertIn(
            "exact source-derived all-37 physical-branch Hessian", verdict
        )
        self.assertNotIn("the full Hessian, and G3 remain open", verdict)
        self.assertNotIn("only a four-real-dimensional Phi sub-slice", verdict)
        self.assertNotIn("arbitrary-Phi bound remain open", verdict)
        self.assertNotIn("pending a corrected vacuum and recomputed spectrum", verdict)
        self.assertIn("corrected SU(3)_C x U(1)_em target/stabilizer", verdict)
        self.assertIn("conditional reconstructed 486-state scalar tree spectrum", verdict)
        self.assertIn("canonical sparse 304-Weyl embedding", verdict)
        self.assertIn("SARAH implicit/identical-Weyl contraction conversion", verdict)
        mutations = (
            lambda value: value["scope"].__setitem__("G3_closed", True),
            lambda value: value["scope"].__setitem__(
                "semidefinite_feasibility_solved", True
            ),
            lambda value: value["standard_PSD_coordinate_routes"].__setitem__(
                "standard_total_parameter_count", 19_593
            ),
            lambda value: value["physical_target"]["full_graded_chart"].__setitem__(
                "row_count", 6_584
            ),
        )
        for mutate in mutations:
            forged = copy.deepcopy(psd_target)
            mutate(forged)
            self.assertFalse(
                mod._rank1_su4_augmented_sos_psd_routes_and_stale_payload_well_formed(
                    forged, census, cubic, quartic
                ),
                mutate.__code__.co_firstlineno,
            )

        forged = copy.deepcopy(psd_target)
        forged["scope"]["G3_closed"] = True
        report = mod._build_report_from_inputs(
            x_report=inputs["exact_X"],
            g1_report=inputs["gauged_G1_character_census"],
            g2_report=inputs["gauged_G2_derivative_audit"],
            filter_report=inputs["gauged_scalar_filter"],
            g3_rank1_su4_augmented_sos_psd_target_report=forged,
        )
        frontier = report["gauged_u1x_g3_constructive_frontier"]
        self.assertEqual(report["overall_state"], "EXECUTION_FAIL")
        self.assertFalse(frontier["integrity_pass"])
        self.assertFalse(
            frontier[
                "rank1_SU4_legacy_v20_PSD_routes_and_stale_payload_well_formed"
            ]
        )
        self.assertFalse(
            report["checks"][
                "gauged_G3_rank1_SU4_infrastructure_is_exact_and_fail_closed"
            ]
        )


if __name__ == "__main__":
    unittest.main()
