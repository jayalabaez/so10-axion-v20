#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import validate_release_v20 as release


class ValidateReleaseChecksumTests(unittest.TestCase):
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
        self.assertEqual(
            release.rank1_su4_release_predicates(
                stabilizer, intertwiners, aligned, quadratic, census
            ),
            (True, True, True, True, True),
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
            ) = (
                release.rank1_su4_release_predicates(
                    forged_stabilizer,
                    forged_intertwiners,
                    aligned,
                    quadratic,
                    census,
                )
            )
            self.assertFalse(stabilizer_exact and intertwiners_exact)
            self.assertFalse(intertwiners_exact)
            self.assertFalse(aligned_exact)
            self.assertFalse(quadratic_exact)
            self.assertFalse(census_exact)

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
                census,
            )
            self.assertFalse(predicates[2] and predicates[3])
            self.assertFalse(predicates[3])
            self.assertFalse(predicates[4])

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
                stabilizer, intertwiners, aligned, quadratic, forged_census
            )
            self.assertEqual(predicates[:4], (True, True, True, True))
            self.assertFalse(predicates[4])

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

    def test_current_main_heredocs_use_the_exact_census_scope_contract(self):
        source = (
            release.ROOT / ".github/workflows/current-main-full-reaudit.yml"
        ).read_text(encoding="utf-8")
        self.assertEqual(
            source.count("_rank1_su4_augmented_sos_census_exact("), 2
        )
        self.assertEqual(
            source.count(
                "all(rank1_su4_census['scope'][name] is False "
                "for name in census_false_scope)"
            ),
            2,
        )
        self.assertNotIn(
            "set(rank1_su4_census['scope'])==set(census_false_scope)", source
        )

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
