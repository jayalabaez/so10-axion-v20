#!/usr/bin/env python3
from __future__ import annotations

import ast
import copy
import hashlib
import json
from pathlib import Path
import re
import tempfile
import unittest

import validate_release_v20 as release


class ValidateReleaseChecksumTests(unittest.TestCase):
    def test_release_uses_canonical_current_or_future_consistency_not_fixed_block(self):
        source = (release.ROOT / "validate_release_v20.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("--expect-blocked", source)
        for required in (
            '"canonical_g1_g8_gauged_u1x_v21.py", "--check"',
            "canonical_integrity = authoritative_gate._canonical_evidence_complete(",
            'expected_state = "PASS" if canonical_closed else "BLOCKED"',
            'matrix["full_theory_validated"] is canonical_closed',
            'ultimate["full_phenomenology_approved"] is canonical_closed',
            '"legacy_ledger_controls_authoritative_closure"',
        ):
            self.assertIn(required, source)

    def test_superseding_g8_frontier_bundle_is_exactly_pinned(self):
        report = json.loads(
            (
                release.ROOT
                / "EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_V20.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(
            report["core_sha256"], release.PHYSICAL_SM_G8_FRONTIER_CORE_SHA256
        )
        for relative, expected in (
            (
                "exact_physical_sm_g8_identifiability_frontier_v20.py",
                release.PHYSICAL_SM_G8_FRONTIER_SOURCE_RAW_SHA256,
            ),
            (
                "test_exact_physical_sm_g8_identifiability_frontier_v20.py",
                release.PHYSICAL_SM_G8_FRONTIER_TEST_RAW_SHA256,
            ),
            (
                "EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_V20.json",
                release.PHYSICAL_SM_G8_FRONTIER_JSON_RAW_SHA256,
            ),
            (
                "EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_V20.md",
                release.PHYSICAL_SM_G8_FRONTIER_MD_RAW_SHA256,
            ),
        ):
            self.assertEqual(
                hashlib.sha256((release.ROOT / relative).read_bytes()).hexdigest(),
                expected,
            )

    def test_readme_current_physical_sm_truth_is_not_stale_or_branch_ambiguous(self):
        readme = (release.ROOT / "README.md").read_text(encoding="utf-8")
        normalized = " ".join(readme.split())
        for required in (
            "all `37` active scalar Hessians are now derived from exact source algebra",
            "aggregate has `V=-1`, zero gradient, rank/nullity `448/38`",
            "kernel equal to the 38-dimensional symmetry tangent span",
            "`CANONICAL_G3_PHYSICAL_EW_GLOBAL_VACUUM_V21.json` now additionally gives the complete 891-direction coefficient ledger",
            "an exact sum-of-squares global lower bound",
            "a connected single-orbit classification of every equality point",
            "Canonical V21 G3 is therefore closed",
            "canonical G4 remains open",
        ):
            with self.subTest(required=required):
                self.assertIn(required, normalized)

        for stale in (
            "still requires a direct source-algebra scalar proof",
            "The new target has a reconstructed rational stationary PSD witness",
            "the reconstruction's denominator bound is not derived from the source algebra",
            "`H`, the full Hessian, and G3 remain open",
            "the full Hessian, G3, and whole-model conclusions remain open",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, normalized)

        self.assertGreaterEqual(
            normalized.count("fixed-endpoint `SU(4)` branch"),
            2,
        )

    def test_physical_sm_source_hessian_chain_is_wired_read_only_and_pinned(self):
        theorem_rows = (
            (
                "exact_physical_sm_hard_projector_hessians_v20.py",
                "test_exact_physical_sm_hard_projector_hessians_v20.py",
                "EXACT_PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_V20.json",
                "EXACT_PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_V20.md",
                "2ac49af04f3bbec17a4e616c82898de6a0710ddcfa3462d7ec8d59dad69de27e",
            ),
            (
                "exact_physical_sm_easy_21_hessians_v20.py",
                "test_exact_physical_sm_easy_21_hessians_v20.py",
                "EXACT_PHYSICAL_SM_EASY_21_HESSIANS_V20.json",
                "EXACT_PHYSICAL_SM_EASY_21_HESSIANS_V20.md",
                "e8b6fcf9bc459ee4c05a74d41cae6d9a82680de88683ba5ffcc4ceb30fe73311",
            ),
            (
                "exact_physical_sm_last_six_hessians_v20.py",
                "test_exact_physical_sm_last_six_hessians_v20.py",
                "EXACT_PHYSICAL_SM_LAST_SIX_HESSIANS_V20.json",
                "EXACT_PHYSICAL_SM_LAST_SIX_HESSIANS_V20.md",
                "78d712d3573ec3377a331eb52dbf429452aa1c7ed82aeb7eeb0aa5900b3774ce",
            ),
            (
                "exact_physical_sm_37_row_aggregate_v20.py",
                "test_exact_physical_sm_37_row_aggregate_v20.py",
                "EXACT_PHYSICAL_SM_37_ROW_AGGREGATE_V20.json",
                "EXACT_PHYSICAL_SM_37_ROW_AGGREGATE_V20.md",
                "801b456743d9037d4478dcb3c94fef3d745ad312b58c3b262324aeded7567f5c",
            ),
            (
                "exact_physical_sm_local_equality_orbit_v20.py",
                "test_exact_physical_sm_local_equality_orbit_v20.py",
                "EXACT_PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_V20.json",
                "EXACT_PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_V20.md",
                "5358c084cd46bdf154fd42505e51d28dc75c6817d392e9bbad5b0d47c55184c7",
            ),
            (
                "exact_physical_sm_g4_g5_branch_mismatch_v20.py",
                "test_exact_physical_sm_g4_g5_branch_mismatch_v20.py",
                "EXACT_PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_V20.json",
                "EXACT_PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_V20.md",
                "cf87a140b031ba625e2f656646402d0eb68aea3d34a555dc391274a198573251",
            ),
        )
        for source, test, report, markdown, digest in theorem_rows:
            with self.subTest(source=source):
                self.assertIn(source, release.FINAL_THEOREM_CORE_PATHS)
                self.assertIn(test, release.FINAL_THEOREM_CORE_PATHS)
                self.assertIn(report, release.FINAL_THEOREM_CORE_PATHS)
                self.assertIn(markdown, release.FINAL_THEOREM_CORE_PATHS)
                self.assertEqual(
                    hashlib.sha256((release.ROOT / source).read_bytes()).hexdigest(),
                    digest,
                )

        ordered_sources = tuple(row[0] for row in theorem_rows)
        for relative in (
            "prepare_validation_artifacts_v20.py",
            "replicate.py",
            "validate_release_v20.py",
        ):
            source = (release.ROOT / relative).read_text(encoding="utf-8")
            positions = [source.index(f'"{name}"') for name in ordered_sources]
            self.assertEqual(positions, sorted(positions), relative)
            for name in ordered_sources:
                self.assertNotRegex(
                    source,
                    rf'"{re.escape(name)}"\s*,\s*"--write"',
                    relative,
                )

        for relative in (
            ".github/workflows/g1-g8-gate-ledger.yml",
            ".github/workflows/g1-g8-execution-roadmap.yml",
            ".github/workflows/gauged-u1x-g3-stability.yml",
        ):
            source = (release.ROOT / relative).read_text(encoding="utf-8")
            commands = [f"python -B {name}" for name in ordered_sources]
            positions = [source.index(command) for command in commands]
            self.assertEqual(positions, sorted(positions), relative)
            central_position = source.find("python g1_g8_", positions[-1])
            if central_position >= 0:
                self.assertLess(positions[-1], central_position)
            for theorem_source, test, report, markdown, digest in theorem_rows:
                for token in (theorem_source, test, report, markdown, digest):
                    self.assertIn(token, source, (relative, token))

    def test_physical_sm_transitive_dependencies_trigger_central_ci_and_are_frozen(self):
        trigger_dependencies = (
            "EXACT_GAUGED_U1X_PHYSICAL_QUOTIENT_V20.json",
            "GAUGED_U1X_G2_DERIVATIVE_AUDIT_V20.json",
            "GAUGED_U1X_SCALAR_CONTRACT_V20.json",
            "direct_phi_h_sigmabar_tensor_v20.py",
            "exact_126bar_self_quartic_basis_v20.py",
            "exact_210_self_invariant_basis_v20.py",
            "exact_gauged_u1x_physical_quotient_v20.py",
            "exact_h10_self_quartic_family_v20.py",
            "exact_hsigma_hermitian_family_closure_v20.py",
            "exact_mixed_45_triplet_channel_v20.py",
            "exact_p_delta_second_stage_hessian_v20.py",
            "exact_phi2_126dag126_six_contractions_v20.py",
            "exact_phi2_hdagh_channel_family_v20.py",
            "exact_phisigma_126bar_minus_projectors_v20.py",
            "exact_phisigma_casimir_projectors_v20.py",
            "gauged_u1x_g2_derivative_audit_v20.py",
            "live_g1_tensor_closure_ledger_v20.py",
            "live_g2_arbitrary_component_potential_values_v20.py",
            "live_g2_exact_final_mixed_quartic_derivatives_v20.py",
            "live_g2_exact_h10_self_quartic_derivatives_v20.py",
            "live_g2_exact_hsigma_hermitian_derivatives_v20.py",
            "live_g2_exact_phi2_hdagh_derivatives_v20.py",
            "live_g2_exact_phi_self_quartic_derivatives_v20.py",
            "live_g2_exact_portal_family_derivatives_v20.py",
            "live_g2_exact_quadratic_family_derivatives_v20.py",
            "live_g2_exact_remaining_cubic_derivatives_v20.py",
            "live_g2_exact_sigma_self_quartic_derivatives_v20.py",
            "live_g2_exact_unique_hsigma_chiral_derivatives_v20.py",
            "nonsusy_z17_pq_potential_filter_v20.py",
            "spin10_referee_audit.py",
        )
        for workflow in (
            ".github/workflows/g1-g8-gate-ledger.yml",
            ".github/workflows/g1-g8-execution-roadmap.yml",
            ".github/workflows/gauged-u1x-g3-stability.yml",
        ):
            text = (release.ROOT / workflow).read_text(encoding="utf-8")
            for relative in trigger_dependencies:
                with self.subTest(workflow=workflow, relative=relative):
                    self.assertIn(relative, text)

        checksum_paths = {
            line.split("  ", 1)[1]
            for line in (release.ROOT / "SHA256SUMS").read_text(
                encoding="utf-8"
            ).splitlines()
        }
        for relative in trigger_dependencies:
            with self.subTest(checksum=relative):
                self.assertIn(relative, checksum_paths)
        for relative in (
            "direct_phi_h_sigmabar_tensor_v20.py",
            "exact_126bar_self_quartic_basis_v20.py",
            "exact_210_self_invariant_basis_v20.py",
            "exact_h10_self_quartic_family_v20.py",
            "exact_hsigma_hermitian_family_closure_v20.py",
            "exact_mixed_45_triplet_channel_v20.py",
            "exact_p_delta_second_stage_hessian_v20.py",
            "exact_phi2_126dag126_six_contractions_v20.py",
            "exact_phi2_hdagh_channel_family_v20.py",
            "exact_phisigma_126bar_minus_projectors_v20.py",
            "exact_phisigma_casimir_projectors_v20.py",
            "live_g1_tensor_closure_ledger_v20.py",
            "spin10_referee_audit.py",
            "live_g2_arbitrary_component_potential_values_v20.py",
            "live_g2_exact_final_mixed_quartic_derivatives_v20.py",
            "live_g2_exact_h10_self_quartic_derivatives_v20.py",
            "live_g2_exact_hsigma_hermitian_derivatives_v20.py",
            "live_g2_exact_phi2_hdagh_derivatives_v20.py",
            "live_g2_exact_phi_self_quartic_derivatives_v20.py",
            "live_g2_exact_portal_family_derivatives_v20.py",
            "live_g2_exact_quadratic_family_derivatives_v20.py",
            "live_g2_exact_remaining_cubic_derivatives_v20.py",
            "live_g2_exact_sigma_self_quartic_derivatives_v20.py",
            "live_g2_exact_unique_hsigma_chiral_derivatives_v20.py",
            "nonsusy_z17_pq_potential_filter_v20.py",
        ):
            with self.subTest(release_core=relative):
                self.assertIn(relative, release.FINAL_THEOREM_CORE_PATHS)

    def test_frozen_stabilizer_dependency_is_read_only_in_all_orchestrators(self):
        stabilizer = "exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py"
        mutating_command = re.compile(
            rf'["\']{re.escape(stabilizer)}["\']\s*,\s*["\']--write["\']'
        )
        for relative in (
            "prepare_validation_artifacts_v20.py",
            "replicate.py",
            "validate_release_v20.py",
        ):
            source = (release.ROOT / relative).read_text(encoding="utf-8")
            with self.subTest(relative=relative):
                self.assertIn(stabilizer, source)
                self.assertIsNone(mutating_command.search(source))
        self._assert_frozen_numerical_and_central_reports_are_read_only()
        self._assert_stochastic_global_flavour_report_is_read_only()

    def _assert_stochastic_global_flavour_report_is_read_only(self):
        script = "global_flavour_fit_v20.py"
        for relative in (
            "prepare_validation_artifacts_v20.py",
            "replicate.py",
        ):
            source = (release.ROOT / relative).read_text(encoding="utf-8")
            tree = ast.parse(source, filename=relative)
            commands = []
            for node in ast.walk(tree):
                if not isinstance(node, (ast.List, ast.Tuple)):
                    continue
                literals = {
                    item.value
                    for item in node.elts
                    if isinstance(item, ast.Constant)
                    and isinstance(item.value, str)
                }
                if script in literals:
                    commands.append(literals)
            with self.subTest(relative=relative, script=script):
                self.assertTrue(commands)
                self.assertTrue(
                    all("--no-write" in command for command in commands)
                )
        workflow = (
            release.ROOT / ".github/workflows/replicate-and-falsify.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("python global_flavour_fit_v20.py --no-write", workflow)
        self.assertNotRegex(
            workflow,
            r"(?m)^\s*python global_flavour_fit_v20\.py\s*$",
        )

    def _assert_frozen_numerical_and_central_reports_are_read_only(self):
        frozen_sources = (
            "exact_gauged_u1x_g1_component_tensor_closure_v20.py",
            "exact_gauged_u1x_stationarity_rank_certificate_v20.py",
            "gauged_u1x_g2_derivative_audit_v20.py",
            "exact_gauged_u1x_g2_mathematical_closure_v20.py",
            "exact_phi_self_zero_global_signed_kaehler_classification_v20.py",
            "exact_gauged_u1x_g3_su5_equality_orbit_v20.py",
            "exact_gauged_u1x_g3_su5_chiral_global_gap_reduction_v20.py",
            "gauged_u1x_g3_sos_candidate_v20.py",
            "gauged_u1x_g3_stability_v20.py",
            "gauged_u1x_g3_corrected_common_kernel_v20.py",
            "final_g3_eft_acceptance_gate_v20.py",
            "final_g4_eft_mathematical_gate_v20.py",
            "final_g5_eft_mathematical_gate_v20.py",
            "exact_eft_physical_scalar_spectrum_v20.py",
            "exact_g6_sm_provenance_feasibility_v20.py",
            "physical_sm_vacuum_local_feasibility_v20.py",
            "exact_physical_sm_five_amplitude_equality_v20.py",
            "exact_physical_sm_hard_projector_hessians_v20.py",
            "exact_physical_sm_easy_21_hessians_v20.py",
            "exact_physical_sm_last_six_hessians_v20.py",
            "exact_physical_sm_37_row_aggregate_v20.py",
            "exact_physical_sm_local_equality_orbit_v20.py",
            "exact_physical_sm_g4_g5_branch_mismatch_v20.py",
            "conditional_physical_sm_eft_hessian_spectrum_v20.py",
            "exact_eft_g6_g7_parameterized_matching_v20.py",
            "final_g6_eft_mathematical_gate_v20.py",
            "exact_authoritative_so10_u1x_gauge_betas_v20.py",
            "exact_physical_sm_heavy_vector_masses_v20.py",
            "exact_physical_sm_heavy_vector_msbar_matching_v20.py",
            "exact_physical_sm_vector_rxi_vacuum_cancellation_v20.py",
            "pyrate3_so10_u1x_gauge_beta_replay_v20.py",
            "exact_normalized_so10_yukawa_cgcs_v20.py",
            "exact_eft_g7_threshold_nonidentifiability_v20.py",
            "exact_physical_g7_component_threshold_contract_v20.py",
            "exact_physical_sm_g6_g7_closure_frontier_v20.py",
            "exact_physical_sm_g8_identifiability_frontier_v20.py",
            "g1_g8_gate_ledger_v20.py",
            "final_g3_acceptance_gate_v20.py",
            "g1_g8_execution_roadmap_v20.py",
            "canonical_g1_g8_gauged_u1x_v21.py",
        )
        for relative in (
            "prepare_validation_artifacts_v20.py",
            "replicate.py",
            "validate_release_v20.py",
        ):
            source = (release.ROOT / relative).read_text(encoding="utf-8")
            tree = ast.parse(source, filename=relative)
            for script in frozen_sources:
                commands = []
                for node in ast.walk(tree):
                    if not isinstance(node, (ast.List, ast.Tuple)):
                        continue
                    literals = {
                        item.value
                        for item in node.elts
                        if isinstance(item, ast.Constant)
                        and isinstance(item.value, str)
                    }
                    if script in literals:
                        commands.append(literals)
                with self.subTest(relative=relative, script=script):
                    self.assertTrue(commands)
                    self.assertTrue(
                        all("--write" not in command for command in commands)
                    )
                    if script == "canonical_g1_g8_gauged_u1x_v21.py":
                        self.assertTrue(
                            any("--check" in command for command in commands)
                        )
            for script in (
                "theory_validation_matrix_v20.py",
                "theory_confirmation_verdict_v20.py",
                "ultimate_theory_gate_v20.py",
            ):
                commands = []
                for node in ast.walk(tree):
                    if not isinstance(node, (ast.List, ast.Tuple)):
                        continue
                    literals = {
                        item.value
                        for item in node.elts
                        if isinstance(item, ast.Constant)
                        and isinstance(item.value, str)
                    }
                    if script in literals:
                        commands.append(literals)
                with self.subTest(relative=relative, script=script):
                    self.assertTrue(commands)
                    self.assertTrue(
                        all("--no-write" in command for command in commands)
                    )

    def test_release_latex_build_is_out_of_tree(self):
        source = (release.ROOT / "validate_release_v20.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('tempfile.TemporaryDirectory(prefix="so10-latex-")', source)
        self.assertIn('"MIKTEX_COMMONSTARTUPFILE": str(miktex_startup)', source)
        self.assertIn('"MIKTEX_USERSTARTUPFILE": str(miktex_startup)', source)
        self.assertIn('"Config=Portable\\n"', source)
        self.assertIn('"--disable-installer"', source)
        self.assertIn("pdfinfo_environment.update(miktex_environment)", source)
        self.assertIn("[pdfinfo, str(built_pdf)]", source)
        self.assertEqual(
            source.count("run(latex, environment_overrides=miktex_environment)"),
            3,
        )
        self.assertIn('f"-output-directory={build_root}"', source)
        self.assertIn("built_pdf = build_root / PDF.name", source)
        self.assertIn("built_log = build_root / LOG.name", source)
        self.assertIn(
            "release checksum regeneration drifted from the frozen", source
        )
        self.assertIn("regenerated_sums != committed_sums", source)

    def test_focused_pytest_uses_a_private_auto_cleaned_basetemp(self):
        source = (release.ROOT / "validate_release_v20.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("def run_pytest_with_private_basetemp", source)
        self.assertIn(
            'tempfile.TemporaryDirectory(prefix=".so10-release-pytest-", dir=ROOT)',
            source,
        )
        self.assertIn('run([*command, "--basetemp", directory])', source)
        self.assertIn("run_pytest_with_private_basetemp(\n        [", source)

    def test_release_runs_parallel_eft_gates_read_only_in_dependency_order(self):
        source = (release.ROOT / "validate_release_v20.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(source, filename="validate_release_v20.py")
        commands = []
        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "run"
                and node.args
                and isinstance(node.args[0], ast.List)
            ):
                continue
            literals = [
                item.value
                for item in node.args[0].elts
                if isinstance(item, ast.Constant) and isinstance(item.value, str)
            ]
            commands.append((node.lineno, literals))
        gate_names = (
            "final_g3_eft_acceptance_gate_v20.py",
            "final_g4_eft_mathematical_gate_v20.py",
            "final_g5_eft_mathematical_gate_v20.py",
            "exact_eft_physical_scalar_spectrum_v20.py",
            "exact_g6_sm_provenance_feasibility_v20.py",
            "physical_sm_vacuum_local_feasibility_v20.py",
            "exact_physical_sm_five_amplitude_equality_v20.py",
            "exact_physical_sm_hard_projector_hessians_v20.py",
            "exact_physical_sm_easy_21_hessians_v20.py",
            "exact_physical_sm_last_six_hessians_v20.py",
            "exact_physical_sm_37_row_aggregate_v20.py",
            "exact_physical_sm_local_equality_orbit_v20.py",
            "exact_physical_sm_g4_g5_branch_mismatch_v20.py",
            "conditional_physical_sm_eft_hessian_spectrum_v20.py",
            "exact_eft_g6_g7_parameterized_matching_v20.py",
            "final_g6_eft_mathematical_gate_v20.py",
            "exact_authoritative_so10_u1x_gauge_betas_v20.py",
            "exact_physical_sm_heavy_vector_masses_v20.py",
            "exact_physical_sm_heavy_vector_msbar_matching_v20.py",
            "exact_physical_sm_vector_rxi_vacuum_cancellation_v20.py",
            "pyrate3_so10_u1x_gauge_beta_replay_v20.py",
            "exact_normalized_so10_yukawa_cgcs_v20.py",
            "exact_eft_g7_threshold_nonidentifiability_v20.py",
            "exact_physical_g7_component_threshold_contract_v20.py",
            "exact_physical_sm_g6_g7_closure_frontier_v20.py",
            "exact_physical_sm_g8_identifiability_frontier_v20.py",
        )
        gate_rows = []
        for name in gate_names:
            rows = [row for row in commands if name in row[1]]
            self.assertEqual(len(rows), 1, name)
            self.assertNotIn("--write", rows[0][1], name)
            gate_rows.append(rows[0])
        self.assertEqual(
            [row[0] for row in gate_rows],
            sorted(row[0] for row in gate_rows),
        )
        ledger_line = next(
            line
            for line, command in commands
            if "g1_g8_gate_ledger_v20.py" in command
        )
        self.assertLess(gate_rows[-1][0], ledger_line)

    def test_release_pins_corrected_g6_and_scoped_g7_evidence(self):
        source = (release.ROOT / "validate_release_v20.py").read_text(
            encoding="utf-8"
        )
        for token in (
            "32bed88b5fad0fe6e51cf19c3b3e120d53362150cfc1db6eafd8c897e24223b7",
            "ca2b92198cbb7cbe6c7051b9c5952bc4af1462ba33db02eaa126533213b1e87f",
            "bec8587376c7dc5a29b45c9c7f0110fcbed98a3ae2d130aaf00bb42f6997aca4",
            "931a152aed49eb28bf415a1aca093e923850cf68db3f40ccf1d2027b447a8c09",
            "1b578471e74626e3b186cf7398aebd35349a67f45940b9c37d42bb49c1b8c8ba",
            "abb704133c8be22b424ba20e23387d6f30412e6c82ab3a214e88bd8df5bef9cc",
            "FINAL_EFT_G6_FORMAL_SU3_X_U1_89_FACTOR_PASS__PHYSICAL_G6_OPEN",
            "parallel_EFT_G4_integrated_into_release_orchestrators",
            "release_integration_completed",
            "downstream_parallel_G5_integration_completed",
            "downstream_integration_completed",
            "parallel_EFT_G6_integrated_into_release_orchestrators",
            "FORMAL_U1_89_ABSTRACT_RESTRICTION_NONINJECTIVE__NO_PHYSICAL_G7_CLAIM",
            "formal_U1_89_abstract_restriction_noninjectivity_proved",
            "exact_physical_EFT_G7_input_nonidentifiability_proved",
            "INDEPENDENT_PYRATE3_GAUGE_ONLY_REPLAY_MATCHES__FULL_G7_OPEN",
            "second_implementation_for_scoped_gauge_subtheorem",
            "mathematical_EFT_G7_closed",
            "EFT_release_G7_verified",
            "authoritative_renormalizable_G7_closed",
            "positive_G7_certified",
            "negative_G7_no_go_certified",
            "release_orchestrators_and_workflows_consume_obstruction",
            "restriction_map_noninjective",
            "absolute_scale_unidentified",
            "EXACT_PHYSICAL_MATTER_BRANCHING_AND_PARAMETERIZED_ONE_LOOP_THRESHOLDS_CLOSED__FULL_G7_OPEN",
            "physical_PS_SM_matter_branching_closed",
            "parameterized_one_loop_matter_threshold_kernel_closed",
            "physical_component_pole_mass_matrices_closed",
            "02c397bbe044695bf124b6f7415dbc1663e4beb9339e3e3e1da9632d532c02c2",
            "41f28313ee6cb10fe9b10625d10b075ada7eb8030ac82da92debe17f950e7bf0",
            "bdceea8f8e10f566119793c0e0cfc31316bd9704aab89a1b70a9fdc880f7cd4a",
            "c83671cff9c33043b5c7cad19e2f2a744cb5f861a8ea71937c5f3a7308dfffb7",
            "all_declared_representation_CGCs_closed",
            "full_one_two_loop_Yukawa_betas_closed",
            "01f565d3382756bc467bfaa99d187188bc1bfc4060f2c3a472650f5e57537e80",
            "old_selected_EFT_target_actual_stabilizer",
            "physical_SM_G3_closed",
            "36bc4131dfb55ca93ab8e0b14caccc18476625e9b443c34672063725ffb6446a",
            "conditional_reconstructed_tree_scalar_spectrum_closed",
            "source_algebra_derived_tree_scalar_spectrum_closed",
            "86c3e0dfda09366b1cf06c8c3a8dcb3dfdf3bfe1555a41214d380ed4db329894",
            "exact_parameterized_tree_vector_mass_matrix_closed",
            "vector_Goldstone_ghost_matching_closed",
            "CORRECTED_SO10_NONYUKAWA_GAUGE_POLYNOMIAL__FULL_G7_OPEN",
            "LEGACY_SO10_210_BETA_DIAGNOSTIC_SOURCE_RAW_SHA256",
            "sarah_validated_210_betas",
            "live_sarah_or_pyrate_executable_run",
            "two_loop_so10_nonyukawa_gauge_polynomial_complete",
        ):
            self.assertIn(token, source)

    def test_final_theorem_core_paths_are_portable_unique_and_present(self):
        paths = release.FINAL_THEOREM_CORE_PATHS

        self.assertEqual(len(paths), len(set(paths)))
        self.assertNotIn(
            "exact_gauged_u1x_g3_su5_max_negative_sigma35_orbits_v20.py",
            paths,
        )
        for required in (
            "test_global_flavour_fit_v20.py",
            "CANONICAL_G1_G8_GAUGED_U1X_V21.json",
            "CANONICAL_G1_G8_GAUGED_U1X_V21.md",
            "canonical_g1_g8_gauged_u1x_v21.py",
            "test_canonical_g1_g8_gauged_u1x_v21.py",
            "FROZEN_PHI_SELF_ZERO_GLOBAL_SIGNED_KAEHLER_CLASSIFICATION_SOURCE_V20.py",
            "exact_phi_self_zero_global_signed_kaehler_classification_v20.py",
            "test_exact_phi_self_zero_global_signed_kaehler_classification_v20.py",
            "exact_gauged_u1x_g3_su5_max_negative_rank1_su3_slice_v20.py",
            "test_exact_gauged_u1x_g3_su5_max_negative_rank1_su3_slice_v20.py",
            "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_RANK1_SU3_SLICE_V20.json",
            "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_RANK1_SU3_SLICE_V20.md",
            "exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py",
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_STABILIZER_V20.json",
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_STABILIZER_V20.md",
            "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py",
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_INTERTWINERS_V20.json",
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_INTERTWINERS_V20.md",
            "exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py",
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_ALIGNED_CARRIERS_V20.json",
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_ALIGNED_CARRIERS_V20.md",
            "exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py",
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_QUADRATIC_BASIS_V20.json",
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_QUADRATIC_BASIS_V20.md",
            "exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py",
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CENSUS_V20.json",
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CENSUS_V20.md",
            "exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py",
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_V20.json",
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_V20.md",
            "exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20.py",
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.json",
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.md",
            "exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py",
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_V20.json",
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_V20.md",
            "corrected_rank1_endpoint_v21.py",
            "freeze_corrected_rank1_endpoint_v21_integration.py",
            "test_corrected_rank1_endpoint_v21.py",
            "test_freeze_corrected_rank1_endpoint_v21_integration.py",
            "FINAL_G4_EFT_MATHEMATICAL_GATE_V20.json",
            "FINAL_G4_EFT_MATHEMATICAL_GATE_V20.md",
            "final_g4_eft_mathematical_gate_v20.py",
            "test_final_g4_eft_mathematical_gate_v20.py",
            "FINAL_G5_EFT_MATHEMATICAL_GATE_V20.json",
            "FINAL_G5_EFT_MATHEMATICAL_GATE_V20.md",
            "final_g5_eft_mathematical_gate_v20.py",
            "test_final_g5_eft_mathematical_gate_v20.py",
            "EXACT_EFT_PHYSICAL_SCALAR_SPECTRUM_V20.json",
            "EXACT_EFT_PHYSICAL_SCALAR_SPECTRUM_V20.md",
            "exact_eft_physical_scalar_spectrum_v20.py",
            "test_exact_eft_physical_scalar_spectrum_v20.py",
            "EXACT_G6_SM_PROVENANCE_FEASIBILITY_V20.json",
            "EXACT_G6_SM_PROVENANCE_FEASIBILITY_V20.md",
            "exact_g6_sm_provenance_feasibility_v20.py",
            "test_exact_g6_sm_provenance_feasibility_v20.py",
            "EXACT_EFT_G6_G7_PARAMETERIZED_MATCHING_V20.json",
            "EXACT_EFT_G6_G7_PARAMETERIZED_MATCHING_V20.md",
            "exact_eft_g6_g7_parameterized_matching_v20.py",
            "test_exact_eft_g6_g7_parameterized_matching_v20.py",
            "FINAL_G6_EFT_MATHEMATICAL_GATE_V20.json",
            "FINAL_G6_EFT_MATHEMATICAL_GATE_V20.md",
            "final_g6_eft_mathematical_gate_v20.py",
            "test_final_g6_eft_mathematical_gate_v20.py",
            "EXACT_AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_V20.json",
            "EXACT_AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_V20.md",
            "exact_authoritative_so10_u1x_gauge_betas_v20.py",
            "test_exact_authoritative_so10_u1x_gauge_betas_v20.py",
            "PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_V20.json",
            "PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_V20.md",
            "pyrate3_so10_u1x_gauge_beta_replay_v20.py",
            "test_pyrate3_so10_u1x_gauge_beta_replay_v20.py",
            "models/SO10U1XGaugeAuditV20.model",
            "data/PYRATE3_SO10_U1X_GAUGE_BETA_FROZEN_V20.json",
            "EXACT_EFT_G7_THRESHOLD_NONIDENTIFIABILITY_V20.json",
            "EXACT_EFT_G7_THRESHOLD_NONIDENTIFIABILITY_V20.md",
            "exact_eft_g7_threshold_nonidentifiability_v20.py",
            "test_exact_eft_g7_threshold_nonidentifiability_v20.py",
            "EXACT_PHYSICAL_G7_COMPONENT_THRESHOLD_CONTRACT_V20.json",
            "EXACT_PHYSICAL_G7_COMPONENT_THRESHOLD_CONTRACT_V20.md",
            "exact_physical_g7_component_threshold_contract_v20.py",
            "test_exact_physical_g7_component_threshold_contract_v20.py",
            "EXACT_NORMALIZED_SO10_YUKAWA_CGCS_V20.json",
            "EXACT_NORMALIZED_SO10_YUKAWA_CGCS_V20.md",
            "exact_normalized_so10_yukawa_cgcs_v20.py",
            "test_exact_normalized_so10_yukawa_cgcs_v20.py",
            "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.json",
            "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.md",
            "physical_sm_vacuum_local_feasibility_v20.py",
            "test_physical_sm_vacuum_local_feasibility_v20.py",
            "CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_V20.json",
            "CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_V20.md",
            "conditional_physical_sm_eft_hessian_spectrum_v20.py",
            "test_conditional_physical_sm_eft_hessian_spectrum_v20.py",
            "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MASSES_V20.json",
            "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MASSES_V20.md",
            "exact_physical_sm_heavy_vector_masses_v20.py",
            "test_exact_physical_sm_heavy_vector_masses_v20.py",
            "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_V20.json",
            "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_V20.md",
            "exact_physical_sm_heavy_vector_msbar_matching_v20.py",
            "test_exact_physical_sm_heavy_vector_msbar_matching_v20.py",
            "EXACT_PHYSICAL_SM_VECTOR_RXI_VACUUM_CANCELLATION_V20.json",
            "EXACT_PHYSICAL_SM_VECTOR_RXI_VACUUM_CANCELLATION_V20.md",
            "exact_physical_sm_vector_rxi_vacuum_cancellation_v20.py",
            "test_exact_physical_sm_vector_rxi_vacuum_cancellation_v20.py",
            "EXACT_PHYSICAL_SM_G6_G7_CLOSURE_FRONTIER_V20.json",
            "EXACT_PHYSICAL_SM_G6_G7_CLOSURE_FRONTIER_V20.md",
            "exact_physical_sm_g6_g7_closure_frontier_v20.py",
            "test_exact_physical_sm_g6_g7_closure_frontier_v20.py",
            "EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_V20.json",
            "EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_V20.md",
            "exact_physical_sm_g8_identifiability_frontier_v20.py",
            "test_exact_physical_sm_g8_identifiability_frontier_v20.py",
            "EXACT_PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_V20.json",
            "EXACT_PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_V20.md",
            "exact_physical_sm_five_amplitude_equality_v20.py",
            "test_exact_physical_sm_five_amplitude_equality_v20.py",
            "EXACT_PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_V20.json",
            "EXACT_PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_V20.md",
            "exact_physical_sm_hard_projector_hessians_v20.py",
            "test_exact_physical_sm_hard_projector_hessians_v20.py",
            "EXACT_PHYSICAL_SM_EASY_21_HESSIANS_V20.json",
            "EXACT_PHYSICAL_SM_EASY_21_HESSIANS_V20.md",
            "exact_physical_sm_easy_21_hessians_v20.py",
            "test_exact_physical_sm_easy_21_hessians_v20.py",
            "EXACT_PHYSICAL_SM_LAST_SIX_HESSIANS_V20.json",
            "EXACT_PHYSICAL_SM_LAST_SIX_HESSIANS_V20.md",
            "exact_physical_sm_last_six_hessians_v20.py",
            "test_exact_physical_sm_last_six_hessians_v20.py",
            "EXACT_PHYSICAL_SM_37_ROW_AGGREGATE_V20.json",
            "EXACT_PHYSICAL_SM_37_ROW_AGGREGATE_V20.md",
            "exact_physical_sm_37_row_aggregate_v20.py",
            "test_exact_physical_sm_37_row_aggregate_v20.py",
            "EXACT_PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_V20.json",
            "EXACT_PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_V20.md",
            "exact_physical_sm_local_equality_orbit_v20.py",
            "test_exact_physical_sm_local_equality_orbit_v20.py",
            "EXACT_PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_V20.json",
            "EXACT_PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_V20.md",
            "exact_physical_sm_g4_g5_branch_mismatch_v20.py",
            "test_exact_physical_sm_g4_g5_branch_mismatch_v20.py",
            "SARAH_PYRATE_SO10_210_BETAS_V20_VERDICT.json",
            "SARAH_PYRATE_SO10_210_BETAS_V20.md",
            ".github/workflows/sarah-pyrate-so10-210-betas.yml",
            "direct_phi_h_sigmabar_tensor_v20.py",
            "spin10_referee_audit.py",
            "live_g2_arbitrary_component_potential_values_v20.py",
            "live_g2_exact_final_mixed_quartic_derivatives_v20.py",
            "live_g2_exact_h10_self_quartic_derivatives_v20.py",
            "live_g2_exact_hsigma_hermitian_derivatives_v20.py",
            "live_g2_exact_phi2_hdagh_derivatives_v20.py",
            "live_g2_exact_phi_self_quartic_derivatives_v20.py",
            "live_g2_exact_portal_family_derivatives_v20.py",
            "live_g2_exact_quadratic_family_derivatives_v20.py",
            "live_g2_exact_remaining_cubic_derivatives_v20.py",
            "live_g2_exact_sigma_self_quartic_derivatives_v20.py",
            "live_g2_exact_unique_hsigma_chiral_derivatives_v20.py",
            "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.json",
            "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.md",
            "exact_gauged_u1x_g1_component_tensor_closure_v20.py",
            "test_exact_gauged_u1x_g1_component_tensor_closure_v20.py",
            "EXACT_GAUGED_U1X_G2_MATHEMATICAL_CLOSURE_V20.json",
            "EXACT_GAUGED_U1X_G2_MATHEMATICAL_CLOSURE_V20.md",
            "exact_gauged_u1x_g2_mathematical_closure_v20.py",
            "test_exact_gauged_u1x_g2_mathematical_closure_v20.py",
            ".github/workflows/current-main-full-reaudit.yml",
            ".github/workflows/g1-g8-execution-roadmap.yml",
            ".github/workflows/g1-g8-gate-ledger.yml",
            ".github/workflows/gauged-u1x-g3-stability.yml",
            ".github/workflows/latest-main-final-scalar-gate.yml",
            ".github/workflows/replicate-and-falsify.yml",
            "corrected_rank1_publication_v21/EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_PUBLICATION_V21_MANIFEST.json",
            "corrected_rank1_publication_v21/EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_FIXED_ENDPOINT_THEOREM_V21.json",
            "corrected_rank1_publication_v21/EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_POSITIVE_GRAM_SYSTEM_V21.npz",
            "corrected_rank1_publication_v21/verify_exact_gauged_u1x_g3_rank1_su4_corrected_fixed_endpoint_theorem_v21.py",
            "corrected_rank1_publication_v21/heavy_regenerate_exact_gauged_u1x_g3_rank1_su4_corrected_system_v21.py",
            "corrected_rank1_publication_v21/test_exact_gauged_u1x_g3_rank1_su4_corrected_publication_v21.py",
        ):
            self.assertIn(required, paths)
        for relative in paths:
            with self.subTest(relative=relative):
                path = Path(relative)
                self.assertFalse(path.is_absolute())
                self.assertEqual(relative, path.as_posix())
                self.assertTrue((release.ROOT / path).is_file())

    def test_checksums_use_sorted_repository_relative_posix_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            readme = root / "README.md"
            model = root / "models" / "SO10Z17AxionV20.m"
            manual = root / "release.pdf"
            model.parent.mkdir()
            readme.write_bytes(b"release\r\n")
            model.write_bytes(b"model\x97legacy\r")
            manual.write_bytes(b"%PDF-1.7\r\nraw-binary\r")

            release.write_checksums([manual, model, readme], root=root)

            expected = [
                f"{hashlib.sha256(b'release\n').hexdigest()}  README.md",
                (
                    f"{hashlib.sha256(b'model\x97legacy\n').hexdigest()}  "
                    "models/SO10Z17AxionV20.m"
                ),
                f"{hashlib.sha256(manual.read_bytes()).hexdigest()}  release.pdf",
            ]
            lines = (root / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
            self.assertEqual(lines, expected)
            self.assertNotIn("\\", "\n".join(lines))
            self.assertEqual(
                release.portable_checksum_payload(readme),
                b"release\n",
            )
            self.assertEqual(
                release.portable_checksum_payload(model), b"model\x97legacy\n"
            )

    def test_rank1_release_predicate_requires_all_false_scope_flags(self):
        source = Path(release.__file__).read_text(encoding="utf-8")
        start = source.index("rank1_scope =")
        end = source.index("alternative_flags =", start)
        predicate = source[start:end]
        for required in (
            'rank1_scope["H_fixed_to_h_minus"] is True',
            'rank1_checks["arbitrary_rank1_Phi_proved"] is False',
            'rank1_checks["arbitrary_Sigma35_proved"] is False',
            'rank1_checks["G3_closed"] is False',
        ):
            self.assertIn(required, predicate)

    def test_rank1_su4_release_predicates_are_exact_and_fail_closed(self):
        stabilizer = json.loads(
            (release.ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_STABILIZER_V20.json")
            .read_text(encoding="utf-8")
        )
        intertwiners = json.loads(
            (
                release.ROOT
                / "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_INTERTWINERS_V20.json"
            ).read_text(encoding="utf-8")
        )
        aligned = json.loads(
            (
                release.ROOT
                / "EXACT_GAUGED_U1X_G3_RANK1_SU4_ALIGNED_CARRIERS_V20.json"
            ).read_text(encoding="utf-8")
        )
        quadratic = json.loads(
            (
                release.ROOT
                / "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_QUADRATIC_BASIS_V20.json"
            ).read_text(encoding="utf-8")
        )
        census = json.loads(
            (
                release.ROOT
                / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CENSUS_V20.json"
            ).read_text(encoding="utf-8")
        )
        cubic = json.loads(
            (
                release.ROOT
                / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_V20.json"
            ).read_text(encoding="utf-8")
        )
        quartic = json.loads(
            (
                release.ROOT
                / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.json"
            ).read_text(encoding="utf-8")
        )
        psd_target = json.loads(
            (
                release.ROOT
                / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_V20.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(
            release.rank1_su4_release_predicates(
                stabilizer, intertwiners, aligned, quadratic, census, cubic,
                quartic, psd_target,
            ),
            (True, True, True, True, True, True, True, True),
        )
        publication = release.corrected_rank1.load_validated_publication()
        forged_publication = copy.deepcopy(publication)
        forged_publication["manifest"]["schema"] = "evil"
        self.assertFalse(
            release.rank1_su4_release_predicates(
                stabilizer,
                intertwiners,
                aligned,
                quadratic,
                census,
                cubic,
                quartic,
                psd_target,
                forged_publication,
            )[-1]
        )

        mutations = []
        forged_stabilizer = copy.deepcopy(stabilizer)
        forged_stabilizer["scope"]["whole_model_excluded"] = True
        mutations.append((forged_stabilizer, copy.deepcopy(intertwiners)))

        forged_intertwiners = copy.deepcopy(intertwiners)
        forged_intertwiners["scope"]["arbitrary_rank1_Phi_proved"] = True
        mutations.append((copy.deepcopy(stabilizer), forged_intertwiners))

        forged_intertwiners = copy.deepcopy(intertwiners)
        forged_intertwiners["companion_stabilizer_provenance"][
            "fixed_endpoint"
        ]["q_coordinate_norm_squared"] = 0
        mutations.append((copy.deepcopy(stabilizer), forged_intertwiners))

        forged_intertwiners = copy.deepcopy(intertwiners)
        forged_intertwiners["intertwiner"]["intertwinings"] = []
        mutations.append((copy.deepcopy(stabilizer), forged_intertwiners))

        forged_stabilizer = copy.deepcopy(stabilizer)
        forged_stabilizer["checks"]["unexpected_new_critical_check"] = False
        mutations.append((forged_stabilizer, copy.deepcopy(intertwiners)))

        forged_intertwiners = copy.deepcopy(intertwiners)
        forged_intertwiners["checks"]["unexpected_new_critical_check"] = False
        mutations.append((copy.deepcopy(stabilizer), forged_intertwiners))

        forged_stabilizer = copy.deepcopy(stabilizer)
        forged_stabilizer["Lie_algebra"]["Jacobi_max_abs_residual"] = 1
        mutations.append((forged_stabilizer, copy.deepcopy(intertwiners)))

        forged_intertwiners = copy.deepcopy(intertwiners)
        forged_intertwiners["companion_stabilizer_provenance"][
            "module"
        ] = "quarantined_or_wrong.py"
        mutations.append((copy.deepcopy(stabilizer), forged_intertwiners))

        forged_intertwiners = copy.deepcopy(intertwiners)
        forged_intertwiners["integral_C8"][
            "minimal_polynomial_annihilates_exact"
        ] = False
        mutations.append((copy.deepcopy(stabilizer), forged_intertwiners))

        forged_intertwiners = copy.deepcopy(intertwiners)
        forged_intertwiners["integral_C8"]["modular_prime"] = 4
        mutations.append((copy.deepcopy(stabilizer), forged_intertwiners))

        forged_intertwiners = copy.deepcopy(intertwiners)
        forged_intertwiners["carriers"][
            "future_Schur_SDP_multiplicity_matrix_dimension"
        ] = 45
        mutations.append((copy.deepcopy(stabilizer), forged_intertwiners))

        forged_intertwiners = copy.deepcopy(intertwiners)
        forged_intertwiners["intertwiner"]["intertwinings"][0][
            "generator"
        ] = "WRONG"
        mutations.append((copy.deepcopy(stabilizer), forged_intertwiners))

        forged_stabilizer = copy.deepcopy(stabilizer)
        forged_intertwiners = copy.deepcopy(intertwiners)
        forged_stabilizer["joint_stabilizer_tangent"]["fixed_endpoint"][
            "H"
        ] = "wrong_H"
        forged_intertwiners["companion_stabilizer_provenance"]["fixed_endpoint"][
            "H"
        ] = "wrong_H"
        mutations.append((forged_stabilizer, forged_intertwiners))

        for forged_stabilizer, forged_intertwiners in mutations:
            (
                stabilizer_exact,
                intertwiners_exact,
                aligned_exact,
                quadratic_exact,
                census_exact,
                cubic_exact,
                quartic_exact,
                psd_target_exact,
            ) = (
                release.rank1_su4_release_predicates(
                    forged_stabilizer,
                    forged_intertwiners,
                    aligned,
                    quadratic,
                    census,
                    cubic,
                    quartic,
                    psd_target,
                )
            )
            self.assertFalse(stabilizer_exact and intertwiners_exact)
            self.assertFalse(intertwiners_exact)
            self.assertFalse(aligned_exact)
            self.assertFalse(quadratic_exact)
            self.assertFalse(census_exact)
            self.assertFalse(cubic_exact)
            self.assertFalse(quartic_exact)
            self.assertFalse(psd_target_exact)

        stage2_mutations = []
        forged_aligned = copy.deepcopy(aligned)
        forged_aligned["alignment"]["concatenated_aligned_basis_rank_mod_prime"] = 209
        stage2_mutations.append((forged_aligned, copy.deepcopy(quadratic)))
        forged_aligned = copy.deepcopy(aligned)
        forged_aligned["upstream_provenance"]["source_contract"][
            "upstream_module_sha256"
        ] = "0" * 64
        stage2_mutations.append((forged_aligned, copy.deepcopy(quadratic)))
        forged_quadratic = copy.deepcopy(quadratic)
        forged_quadratic["constraint_system"]["exact_rational_rank"] = 505
        stage2_mutations.append((copy.deepcopy(aligned), forged_quadratic))
        forged_quadratic = copy.deepcopy(quadratic)
        forged_quadratic["scope"][
            "augmented_homogeneous_Schur_SOS_SDP_constructed"
        ] = True
        stage2_mutations.append((copy.deepcopy(aligned), forged_quadratic))
        for forged_aligned, forged_quadratic in stage2_mutations:
            predicates = release.rank1_su4_release_predicates(
                stabilizer, intertwiners, forged_aligned, forged_quadratic,
                census, cubic, quartic, psd_target,
            )
            self.assertFalse(predicates[2] and predicates[3])
            self.assertFalse(predicates[3])
            self.assertFalse(predicates[4])
            self.assertFalse(predicates[5])
            self.assertFalse(predicates[6])
            self.assertFalse(predicates[7])

        census_mutations = []
        for key in (
            "Schur_coordinate_6585_by_19594_coefficient_matrix_constructed",
            "physical_G3_gap_target_vector_constructed",
            "augmented_Schur_SOS_SDP_constructed",
            "arbitrary_real_Phi_lower_bound_proved",
            "G3_closed",
            "whole_model_validated",
            "whole_model_excluded",
        ):
            forged_census = copy.deepcopy(census)
            forged_census["scope"][key] = True
            census_mutations.append(forged_census)
        forged_census = copy.deepcopy(census)
        forged_census["source_provenance"]["quadratic_source_sha256"] = "0" * 64
        census_mutations.append(forged_census)
        forged_census = copy.deepcopy(census)
        forged_census["augmented_representation"]["complex_irreducible_copy_count"] = 823
        census_mutations.append(forged_census)
        for forged_census in census_mutations:
            predicates = release.rank1_su4_release_predicates(
                stabilizer, intertwiners, aligned, quadratic, forged_census,
                cubic, quartic, psd_target,
            )
            self.assertEqual(predicates[:4], (True, True, True, True))
            self.assertFalse(predicates[4])
            self.assertFalse(predicates[5])
            self.assertFalse(predicates[6])
            self.assertFalse(predicates[7])

        cubic_mutations = []
        for section, key, value in (
            ("source_provenance", "census_report_sha256", "0" * 64),
            ("Sym2_target_carriers", "total_complex_carrier_copy_count", 539),
            ("physical_cubic_domain", "physical_basis_count", 1_413),
            ("cubic_coordinate_map", "coordinate_map_sha256", "f" * 64),
            ("cubic_coordinate_map", "exact_rank", 477),
            ("cubic_coordinate_map", "exact_kernel_dimension", 937),
            (
                "cubic_coordinate_map",
                "abstract_zero_placeholder_is_not_a_physical_G3_target",
                False,
            ),
            (
                "cubic_coordinate_map",
                "physical_G3_gap_target_vector_constructed",
                True,
            ),
            (
                "cubic_coordinate_map",
                "physical_G3_gap_cubic_zero_RHS_certified",
                True,
            ),
        ):
            forged_cubic = copy.deepcopy(cubic)
            forged_cubic[section][key] = value
            cubic_mutations.append(forged_cubic)
        for key in (
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
        ):
            forged_cubic = copy.deepcopy(cubic)
            forged_cubic["scope"][key] = True
            cubic_mutations.append(forged_cubic)
        for forged_cubic in cubic_mutations:
            predicates = release.rank1_su4_release_predicates(
                stabilizer, intertwiners, aligned, quadratic, census,
                forged_cubic, quartic, psd_target,
            )
            self.assertEqual(predicates[:5], (True, True, True, True, True))
            self.assertFalse(predicates[5])
            self.assertFalse(predicates[6])
            self.assertFalse(predicates[7])

        quartic_mutations = []
        for section, key, value in (
            ("scope", "physical_quartic_target_constructed", True),
            (
                "scope",
                "standard_PSD_congruences_for_real_type_fixed_bases_constructed",
                True,
            ),
            ("scope", "semidefinite_feasibility_solved", True),
            ("scope", "arbitrary_Phi_stationarity_or_lower_bound_proved", True),
            ("scope", "G3_closed", True),
            ("dimensions", "quartic_kernel", 12_029),
            ("coefficient_map_certificate", "shape", [6_056, 18_085]),
            ("coefficient_map_certificate", "nnz", 115_640),
            ("coefficient_map_certificate", "rank_over_Q_exact", 6_056),
            (
                "coefficient_map_certificate",
                "kernel_dimension_over_Q_exact",
                12_029,
            ),
        ):
            forged_quartic = copy.deepcopy(quartic)
            forged_quartic[section][key] = value
            quartic_mutations.append(forged_quartic)
        for forged_quartic in quartic_mutations:
            predicates = release.rank1_su4_release_predicates(
                stabilizer, intertwiners, aligned, quadratic, census, cubic,
                forged_quartic, psd_target,
            )
            self.assertEqual(
                predicates[:6], (True, True, True, True, True, True)
            )
            self.assertFalse(predicates[6])
            self.assertFalse(predicates[7])

        psd_target_mutations = []
        for section, key, value in (
            ("scope", "semidefinite_feasibility_solved", True),
            ("scope", "exact_primal_PSD_certificate_constructed", True),
            ("scope", "exact_dual_Farkas_certificate_constructed", True),
            ("scope", "arbitrary_Phi_lower_bound_proved", True),
            ("scope", "G3_closed", True),
            ("standard_PSD_coordinate_routes", "standard_total_parameter_count", 19_593),
        ):
            forged_psd_target = copy.deepcopy(psd_target)
            forged_psd_target[section][key] = value
            psd_target_mutations.append(forged_psd_target)
        for forged_psd_target in psd_target_mutations:
            predicates = release.rank1_su4_release_predicates(
                stabilizer, intertwiners, aligned, quadratic, census, cubic,
                quartic, forged_psd_target,
            )
            self.assertEqual(
                predicates[:7], (True, True, True, True, True, True, True)
            )
            self.assertFalse(predicates[7])

    def test_su4_release_does_not_mislabel_the_full_augmented_sos_as_45_by_45(
        self,
    ):
        paths = (
            "README.md",
            "axion_so10_theory_v20.tex",
            "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py",
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_INTERTWINERS_V20.json",
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_INTERTWINERS_V20.md",
            "g1_g8_execution_roadmap_v20.py",
            "G1_G8_EXECUTION_ROADMAP_V20.json",
            "G1_G8_EXECUTION_ROADMAP_V20.md",
            "theory_validation_matrix_v20.py",
            "THEORY_VALIDATION_MATRIX_V20_VERDICT.json",
            "THEORY_VALIDATION_MATRIX_V20.md",
        )
        forbidden = (
            "45-by-45",
            "45\\times45",
            "future_Schur_SDP_multiplicity_matrix_dimension",
        )
        for relative in paths:
            text = (release.ROOT / relative).read_text(encoding="utf-8")
            for phrase in forbidden:
                self.assertNotIn(phrase, text, (relative, phrase))
        source = (
            release.ROOT
            / "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py"
        ).read_text(encoding="utf-8")
        self.assertIn("full augmented SU(4)-equivariant degree-2", source)
        self.assertIn("every real/Hermitian isotypic block", source)
        self.assertIn("homogenizing cross terms", source)

    def test_current_main_heredocs_reject_legacy_target_and_accept_corrected_endpoint(self):
        source = (
            release.ROOT / ".github/workflows/current-main-full-reaudit.yml"
        ).read_text(encoding="utf-8")
        for required in (
            "_rank1_su4_augmented_sos_psd_routes_and_stale_payload_well_formed(",
            "_rank1_su4_augmented_sos_psd_target_exact(",
            "corrected=central_view(corrected_publication)",
            "corrected['legacy_v20_physical_target_valid'] is False",
            "corrected['corrected_fixed_endpoint_theorem_exact'] is True",
            "corrected['map_shape'] == [6585, 19594]",
            "corrected['target_common_denominator'] == 576000",
            "corrected['exact_coefficient_equalities'] == 6585",
            "corrected['strict_positive_Gram_blocks'] == 22",
            "corrected['strict_positive_LDL_pivots'] == 824",
            "corrected['arbitrary_real_Phi_at_fixed_endpoint'] is True",
        ):
            self.assertEqual(source.count(required), 2, required)
        for required in (
            "'global_Sigma_proved'",
            "'general_H_proved'",
            "'full_Hessian_proved'",
            "'G3_closed'",
        ):
            self.assertGreaterEqual(source.count(required), 2, required)
        self.assertNotIn(
            "python exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py",
            source,
        )
        self.assertEqual(
            source.count(
                "heavy_regenerate_exact_gauged_u1x_g3_rank1_su4_corrected_system_v21.py --check"
            ),
            1,
        )

    def test_all_seven_release_heredocs_pin_corrected_endpoint_and_reject_legacy(self):
        requirements = (release.ROOT / "requirements.txt").read_text(
            encoding="utf-8"
        )
        self.assertIn("sympy==1.14.0", requirements.splitlines())
        workflow_contracts = {
            ".github/workflows/current-main-full-reaudit.yml": (2, 2, (120, 360)),
            ".github/workflows/g1-g8-execution-roadmap.yml": (2, 1, (90,)),
            ".github/workflows/g1-g8-gate-ledger.yml": (2, 1, (90,)),
            ".github/workflows/gauged-u1x-g3-stability.yml": (2, 1, (75,)),
            ".github/workflows/replicate-and-falsify.yml": (2, 2, (75,)),
        }
        total_heredocs = 0
        heavy_count = 0
        for relative, (
            expected_heredocs,
            endpoint_heredocs,
            timeouts,
        ) in workflow_contracts.items():
            source = (release.ROOT / relative).read_text(encoding="utf-8")
            self.assertEqual(source.count("python - <<'PY'"), expected_heredocs)
            self.assertEqual(
                source.count("_rank1_su4_augmented_sos_psd_target_exact("),
                endpoint_heredocs,
                relative,
            )
            self.assertEqual(
                source.count(
                    "_rank1_su4_augmented_sos_psd_routes_and_stale_payload_well_formed("
                ),
                endpoint_heredocs,
                relative,
            )
            self.assertEqual(
                source.count("central_view(corrected_publication)"),
                endpoint_heredocs,
                relative,
            )
            total_heredocs += expected_heredocs
            heavy_count += source.count(
                "heavy_regenerate_exact_gauged_u1x_g3_rank1_su4_corrected_system_v21.py --check"
            )
            for timeout in timeouts:
                self.assertIn(f"timeout-minutes: {timeout}", source, relative)
            for required in (
                "exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py",
                "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py",
                "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_V20.json",
                "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_V20.md",
                "corrected_rank1_endpoint_v21.py",
                "corrected_rank1_publication_v21",
                "PYTHONDONTWRITEBYTECODE",
                "SO10_PUBLISHED_API_ROOT",
                "python -B",
            ):
                self.assertIn(required, source, (relative, required))
            for required in (
                "legacy_v20_physical_target_valid",
                "corrected_fixed_endpoint_theorem_exact",
                "map_shape",
                "target_common_denominator",
                "exact_coefficient_equalities",
                "strict_positive_Gram_blocks",
                "strict_positive_LDL_pivots",
                "arbitrary_real_Phi_at_fixed_endpoint",
                "global_Sigma_proved",
                "general_H_proved",
                "full_Hessian_proved",
                "G3_closed",
            ):
                self.assertGreaterEqual(
                    source.count(required), endpoint_heredocs, (relative, required)
                )
            self.assertNotIn(
                "python exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py",
                source,
            )
            self.assertNotIn(
                "python exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py --write",
                source,
                relative,
            )
            self.assertIsNone(
                re.search(
                    r"\bpython(?:\s+-B)?\s+"
                    r"exact_gauged_u1x_g3_rank1_su4_stabilizer_v20\.py"
                    r"\s+--write\b",
                    source,
                ),
                relative,
            )
            self.assertIn(
                "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py",
                source,
            )
        self.assertEqual(total_heredocs, 10)
        self.assertEqual(heavy_count, 1)

    def test_checksums_reject_files_outside_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "repository"
            root.mkdir()
            outside = base / "outside.txt"
            outside.write_text("outside\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "outside repository"):
                release.write_checksums([outside], root=root)


if __name__ == "__main__":
    unittest.main()
