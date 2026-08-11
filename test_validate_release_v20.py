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

    def _assert_frozen_numerical_and_central_reports_are_read_only(self):
        frozen_sources = (
            "gauged_u1x_g2_derivative_audit_v20.py",
            "gauged_u1x_g3_sos_candidate_v20.py",
            "gauged_u1x_g3_stability_v20.py",
            "gauged_u1x_g3_corrected_common_kernel_v20.py",
            "g1_g8_gate_ledger_v20.py",
            "final_g3_acceptance_gate_v20.py",
            "g1_g8_execution_roadmap_v20.py",
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

    def test_final_theorem_core_paths_are_portable_unique_and_present(self):
        paths = release.FINAL_THEOREM_CORE_PATHS

        self.assertEqual(len(paths), len(set(paths)))
        self.assertNotIn(
            "exact_gauged_u1x_g3_su5_max_negative_sigma35_orbits_v20.py",
            paths,
        )
        for required in (
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
            ".github/workflows/current-main-full-reaudit.yml": (2, (120, 360)),
            ".github/workflows/g1-g8-execution-roadmap.yml": (1, (90,)),
            ".github/workflows/g1-g8-gate-ledger.yml": (1, (90,)),
            ".github/workflows/gauged-u1x-g3-stability.yml": (1, (75,)),
            ".github/workflows/replicate-and-falsify.yml": (2, (75,)),
        }
        total_heredocs = 0
        heavy_count = 0
        for relative, (expected_heredocs, timeouts) in workflow_contracts.items():
            source = (release.ROOT / relative).read_text(encoding="utf-8")
            self.assertEqual(source.count("python - <<'PY'"), expected_heredocs)
            self.assertEqual(
                source.count("_rank1_su4_augmented_sos_psd_target_exact("),
                expected_heredocs,
                relative,
            )
            self.assertEqual(
                source.count(
                    "_rank1_su4_augmented_sos_psd_routes_and_stale_payload_well_formed("
                ),
                expected_heredocs,
                relative,
            )
            self.assertEqual(
                source.count("central_view(corrected_publication)"),
                expected_heredocs,
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
                    source.count(required), expected_heredocs, (relative, required)
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
        self.assertEqual(total_heredocs, 7)
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
