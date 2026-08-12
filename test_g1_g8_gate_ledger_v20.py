#!/usr/bin/env python3
"""Regression tests for the contract-aware G1-G8 gate ledger."""
from __future__ import annotations

import copy
import unittest

import g1_g8_gate_ledger_v20 as mod


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
    external["valid"] = True
    for name in (
        "tool_native_model_format_matches_path",
        "external_process_command_matches_tool",
        "input_manifest_schema_is_supported",
        "input_manifest_sha256_matches_entries",
        "primary_model_is_bound_in_input_manifest",
        "validation_driver_is_bound_to_command",
        "captured_process_log_is_hash_bound",
        "captured_process_log_has_all_required_pass_markers",
    ):
        external["checks"][name] = True


class G1G8GateLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_audit_succeeds_while_science_is_blocked(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["audit_failures"])
        self.assertEqual(
            self.report["status"],
            "G1_G8_LEDGER_AUDIT_COMPLETE__MODEL_CONTRACT_BLOCKED__"
            "G1_MULTIPLICITY_CENSUS_AND_G2_DERIVATIVE_AUDIT_RECERTIFIED",
        )
        self.assertEqual(self.report["overall_state"], mod.STATUS_BLOCKED)
        self.assertFalse(self.report["contract_consistent"])
        self.assertIn(mod.CONTRACT_BLOCKER, self.report["scientific_blockers"])
        self.assertIn(
            "G3_ARBITRARY_NON_PURE_DELTA_SIGMA_UNIFORM_COERCIVITY_OPEN",
            self.report["scientific_blockers"],
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
        self.assertEqual(self.report["gates"]["G3"]["status"], mod.STATUS_BLOCKED)
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
        self.assertTrue(g6["mathematical_G6_closed_for_EFT_model"])
        self.assertFalse(g6["release_G6_verified_for_EFT_model"])
        self.assertFalse(g6["authoritative_renormalizable_G6_closed"])
        self.assertFalse(g6["authoritative_G6_gate_mutated"])
        self.assertFalse(g6["whole_model_validated"])
        self.assertEqual(g6["spectrum_summary"]["ambient_real_fields"], 486)
        self.assertEqual(g6["spectrum_summary"]["gauge_quotient_dimension"], 449)
        self.assertEqual(g6["spectrum_summary"]["physical_PQ_axions"], 1)
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

        for name in ("G3", "G4", "G5", "G6"):
            self.assertEqual(self.report["gates"][name]["status"], mod.STATUS_BLOCKED)
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
                "parallel_EFT_G6_spectrum_is_source_bound_and_release_open"
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
        self.assertFalse(x_report["contract_consistent"])
        self.assertEqual(x_report["blocker"], mod.CONTRACT_BLOCKER)
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
        self.assertEqual(self.report["gates"]["G3"]["status"], mod.STATUS_BLOCKED)
        self.assertEqual(
            self.report["gates"]["G3"]["constructive_frontier_evidence"],
            frontier,
        )

    def test_g1_multiplicity_census_and_g2_derivative_audit_are_scoped(self):
        scoped = self.report["gauged_u1x_scalar_subtheorems"]
        self.assertEqual(scoped["model_contract_id"], mod.AUTHORITATIVE_CONTRACT_ID)
        self.assertFalse(scoped["whole_model_gate_closure"])
        self.assertEqual(
            scoped["G1"]["scoped_status"],
            "COMPLETE_GAUGED_U1X_MULTIPLICITY_CENSUS__FULL_G1_OPEN",
        )
        self.assertTrue(scoped["G1"]["multiplicity_census_complete"])
        self.assertFalse(
            scoped["G1"]["explicit_component_tensor_subset_integration_complete"]
        )
        self.assertFalse(scoped["G1"]["full_G1_closed"])
        self.assertEqual(scoped["G1"]["invariant_directions"], 44)
        self.assertEqual(scoped["G1"]["real_potential_parameters"], 51)
        self.assertTrue(scoped["G2"]["scoped_derivative_audit_complete"])
        self.assertTrue(scoped["G2"]["authoritative_promotion_blocked_on_full_G1"])
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
            self.assertEqual(gate["status"], mod.STATUS_BLOCKED)
            self.assertTrue(gate["scoped_calculation_complete"])
        self.assertFalse(
            self.report["gates"]["G1"]["full_gate_calculation_complete"]
        )
        self.assertTrue(
            self.report["gates"]["G2"]["full_gate_calculation_complete"]
        )

    def test_every_authoritative_gate_is_blocked_and_none_is_closed(self):
        gates = self.report["gates"]
        self.assertEqual(set(gates), {f"G{i}" for i in range(1, 9)})
        self.assertTrue(all(row["status"] == mod.STATUS_BLOCKED for row in gates.values()))
        self.assertEqual(self.report["summary"]["closed"], [])
        self.assertEqual(self.report["summary"]["blocked"], list(gates))
        self.assertEqual(self.report["summary"]["n_closed"], 0)
        self.assertEqual(self.report["summary"]["n_blocked"], 8)

    def test_wave_zero_model_contract_precedes_g1(self):
        self.assertTrue(mod._acyclic_dependencies())
        self.assertEqual(self.report["dependencies"]["MODEL_CONTRACT"], [])
        self.assertEqual(self.report["dependencies"]["G1"], ["MODEL_CONTRACT"])
        wave0 = self.report["closure_waves"][0]
        self.assertEqual(wave0["wave"], 0)
        self.assertEqual(wave0["id"], "MODEL_CONTRACT")
        self.assertEqual(wave0["status"], mod.STATUS_BLOCKED)

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
        self.assertEqual(feasibility["current_authoritative_closed_gates"], 0)
        self.assertFalse(feasibility["guarantee_model_survives_recertification"])
        self.assertTrue(
            feasibility["gauged_G1_multiplicity_census_complete"]
        )
        self.assertFalse(
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

    def test_repaired_contract_cannot_close_g1_without_component_tensors(self):
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
        self.assertEqual(report["summary"]["closed"], [])
        self.assertEqual(report["summary"]["open"], ["G1"])
        self.assertEqual(
            report["summary"]["blocked"],
            ["G2", "G3", "G4", "G5", "G6", "G7", "G8"],
        )
        self.assertEqual(
            {name: row["status"] for name, row in report["gates"].items()},
            {
                "G1": mod.STATUS_OPEN,
                "G2": mod.STATUS_BLOCKED,
                "G3": mod.STATUS_BLOCKED,
                "G4": mod.STATUS_BLOCKED,
                "G5": mod.STATUS_BLOCKED,
                "G6": mod.STATUS_BLOCKED,
                "G7": mod.STATUS_BLOCKED,
                "G8": mod.STATUS_BLOCKED,
            },
        )
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
            "Global Sigma, general/full H, the full Hessian, and G3 remain open",
            verdict,
        )
        self.assertNotIn("only a four-real-dimensional Phi sub-slice", verdict)
        self.assertNotIn("arbitrary-Phi bound remain open", verdict)
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
