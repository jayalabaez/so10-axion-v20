#!/usr/bin/env python3
"""Tests for the hypercharge audit of the G3 126bar vacuum directions."""
from __future__ import annotations

import json
import math
import unittest
from fractions import Fraction

import numpy as np

import g3_candidate_physical_target_audit_v20 as target
import g3_sigma_hypercharge_audit_v20 as audit


class SigmaHyperchargeAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # The fast report: every exact section, without the compiler probe.
        cls.report = audit.build_report(include_potential_probe=False)

    def test_all_checks_pass_and_scope_is_fail_closed(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(
            self.report["status"],
            "G3_SIGMA_DIRECTION_IS_Y_MINUS_1_TRIPLET_COMPONENT__NAMED_VACUA_ARE_NOT_SM__G3_OPEN",
        )
        flags = self.report["flags"]
        self.assertFalse(flags["certified_g3_point_is_sm_vacuum"])
        self.assertFalse(flags["physical_hierarchy_state_is_sm_vacuum"])
        self.assertFalse(flags["historical_27_parameter_candidate_is_sm_vacuum"])
        self.assertFalse(flags["direct_delta_r_is_sm_singlet"])
        self.assertTrue(flags["sm_singlet_direction_found"])
        self.assertTrue(flags["sm_type_sigma_for_certified_F_found"])
        self.assertFalse(flags["g3_closed"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_sigma_charges_in_repository_convention(self) -> None:
        expected = {
            "direct_delta_r": (Fraction(-2), Fraction(0), Fraction(0), Fraction(-1)),
            "sm_singlet_Y0": (Fraction(-2), Fraction(0), Fraction(1), Fraction(0)),
            "flipped_P_minus_i": (Fraction(-2), Fraction(0), Fraction(-1), Fraction(-2)),
        }
        for name, charges in expected.items():
            row = self.report["sigma_directions"][name]
            self.assertEqual((row["B_minus_L"], row["T3L"], row["T3R"], row["Y"]), charges, name)
            self.assertEqual(row["C2_SU2R"], 2)
            self.assertTrue(row["exactly_in_chart_minus_i_space"])
            self.assertTrue(row["P_minus_i_is_identity_on_raw"])
        self.assertTrue(self.report["sigma_directions"]["sm_singlet_Y0"]["annihilated_by_standard_SM_algebra"])
        self.assertFalse(self.report["sigma_directions"]["direct_delta_r"]["annihilated_by_standard_SM_algebra"])

    def test_y0_singlet_is_the_conjugate_of_the_hsigma_delta_r_form(self) -> None:
        binding = self.report["repository_bindings"]["hsigma_delta_r_form"]
        self.assertLess(binding["plus_i_hodge_residual"], 1.0e-12)
        self.assertLess(binding["conjugate_minus_i_hodge_residual"], 1.0e-12)
        self.assertLess(binding["conjugate_alignment_defect_with_sm_singlet_Y0"], 1.0e-12)
        self.assertAlmostEqual(binding["numeric_charges_of_form"]["B_minus_L"], 2.0, places=12)
        self.assertAlmostEqual(binding["numeric_charges_of_conjugate"]["B_minus_L"], -2.0, places=12)
        classified = self.report["repository_bindings"]["repository_minus_i_su2r_triplet_classification"]
        self.assertEqual(
            {key: row["matches_exact_direction"] for key, row in classified.items()},
            {"T3R=+0": "direct_delta_r", "T3R=+1": "sm_singlet_Y0", "T3R=-1": "flipped_P_minus_i"},
        )

    def test_pair_stabilizer_table(self) -> None:
        pairs = self.report["pair_stabilizers"]
        for phi in audit.PHI_NAMES:
            row = pairs[f"{phi}|direct_delta_r"]
            self.assertEqual(row["stabilizer_dimension"], 12)
            self.assertFalse(row["is_sm_type"])
            self.assertEqual(row["centre_proportional_to"], ["T3R"])
            spectrum = row["centre_spectrum_on_vector_10"]
            self.assertEqual(spectrum["colour_block_0_5"], {"0": 6})
            self.assertEqual(spectrum["weak_block_6_9"], {"1/2": 4})
        self.assertTrue(pairs["F|sm_singlet_Y0"]["is_su5_type"])
        self.assertEqual(pairs["F|sm_singlet_Y0"]["stabilizer_dimension"], 24)
        flipped = pairs["F|flipped_P_minus_i"]
        self.assertTrue(flipped["is_sm_type"])
        self.assertEqual(flipped["centre_proportional_to"], ["Y_flipped"])
        self.assertEqual(
            flipped["centre_spectrum_on_vector_10"]["hypercharge_normalized"], {"1/3": 6, "1/2": 4}
        )
        standard = pairs["p|sm_singlet_Y0"]
        self.assertTrue(standard["is_sm_type"])
        self.assertTrue(standard["contains_standard_sm_algebra"])
        self.assertTrue(pairs["p|flipped_P_minus_i"]["is_sm_type"])
        self.assertEqual(
            self.report["sm_type_pairs"],
            sorted(
                f"{phi}|{sigma}"
                for phi in audit.PHI_NAMES
                for sigma in ("sm_singlet_Y0", "flipped_P_minus_i")
                if (phi, sigma) != ("F", "sm_singlet_Y0")
            ),
        )

    def test_named_vacua_are_not_sm_vacua(self) -> None:
        vacua = self.report["named_vacua"]
        self.assertEqual(
            sorted(vacua),
            [
                "certified_g3_point",
                "certified_gut_point_H0",
                "historical_27_parameter_p_branch_candidate",
                "physical_hierarchy_state",
                "replacement_stationary_orbit",
            ],
        )
        for name, row in vacua.items():
            self.assertTrue(row["binding"]["bound"], name)
            self.assertFalse(row["is_sm_vacuum"], name)
            self.assertTrue(row["full_state_stabilizer_so10_plus_u1x"]["u1x_broken"], name)
        for name in ("certified_g3_point", "certified_gut_point_H0", "physical_hierarchy_state"):
            self.assertEqual(vacua[name]["heavy_pair_stabilizer"]["stabilizer_dimension"], 12)
            self.assertEqual(vacua[name]["heavy_pair_stabilizer"]["centre_proportional_to"], ["T3R"])
        h = vacua["certified_g3_point"]["H_standard_embedding_charges"]
        self.assertEqual((h["T3L"], h["T3R"], h["Q_em"]), (Fraction(1, 2), Fraction(1, 2), Fraction(1)))
        self.assertTrue(
            vacua["historical_27_parameter_p_branch_candidate"]["historical_binding"][
                "compiler_rows_use_physical_hierarchy_state"
            ]
        )

    def test_committed_artifact_matches_fresh_report(self) -> None:
        committed = json.loads(audit.OUT_JSON.read_text(encoding="utf-8"))
        fresh = json.loads(json.dumps(audit._jsonable(self.report), sort_keys=True))
        self.assertEqual(set(committed) - {audit.PROBE_KEY}, set(fresh))
        for key in sorted(fresh):
            self.assertEqual(target.report_mismatches(committed[key], fresh[key], key), [])

    def test_committed_certified_coupling_probe(self) -> None:
        committed = json.loads(audit.OUT_JSON.read_text(encoding="utf-8"))
        probe = committed[audit.PROBE_KEY]
        self.assertFalse(probe["recomputed_by_fast_test"])
        points = probe["points"]
        self.assertEqual(
            sorted(points),
            ["F_with_direct_delta_r", "F_with_flipped_P_minus_i", "F_with_sm_singlet_Y0"],
        )
        self.assertTrue(probe["probe_checks"]["certified_gut_point_is_stationary"])
        self.assertLess(points["F_with_direct_delta_r"]["gradient_max_abs"], 1.0e-10)
        self.assertEqual(points["F_with_direct_delta_r"]["potential_minus_certified_gut_point"], 0.0)
        for row in points.values():
            self.assertAlmostEqual(row["sigma_kinetic_norm"], 0.2, places=12)
            self.assertTrue(math.isfinite(row["potential_value"]))
            self.assertEqual(
                sum(group["complex_multiplicity"] for group in row["h10_mass_squared_spectrum"]), 10
            )


class ExactHelperTest(unittest.TestCase):
    def test_hodge_star_squares_to_minus_one_on_five_forms(self) -> None:
        form = audit._wedge_all(audit._z(1), audit._z(2), audit._e(6), audit._e(8), audit._z(5))
        self.assertEqual(audit._hodge(audit._hodge(form)), audit.g2_audit._exact_form_scale(form, -1))

    def test_nullspace_and_rank_are_exact(self) -> None:
        rows = [[1, 2, 3], [2, 4, 6], [1, 0, -1]]
        self.assertEqual(audit._rank(rows, 3), 2)
        self.assertEqual(audit._nullspace(rows, 3), [(1, -2, 1)])

    def test_su3_colour_basis_commutes_with_j6(self) -> None:
        basis = audit.su3_colour_integer_basis()
        self.assertEqual(len(basis), 8)
        j6 = audit._matrix(audit.BL_INTEGER)
        for vector in basis:
            matrix = audit._matrix(vector)
            self.assertFalse(np.any(matrix @ j6 - j6 @ matrix))
            self.assertEqual(int(np.trace(matrix @ j6)), 0)

    def test_standard_sm_algebra_passes_the_convention_free_test(self) -> None:
        record = audit.classify_stabilizer(audit.standard_sm_integer_basis())
        self.assertTrue(record["is_sm_type"])
        self.assertEqual(record["centre_proportional_to"], ["Y_standard"])
        self.assertTrue(record["contains_standard_sm_algebra"])
        self.assertFalse(record["contains_flipped_sm_algebra"])

    def test_cartan_charges_of_one_forms(self) -> None:
        z4 = audit.exact_charges(audit._z(4))
        self.assertEqual((z4["T3L"], z4["T3R"], z4["Y"], z4["Q_em"]), (Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(1)))
        z5 = audit.exact_charges(audit._z(5))
        self.assertEqual((z5["T3L"], z5["T3R"], z5["Q_em"]), (Fraction(-1, 2), Fraction(1, 2), Fraction(0)))
        self.assertFalse(audit.exact_charges(audit._e(6))["cartan_eigenform"])

    def test_reflection_maps_standard_singlet_to_flipped(self) -> None:
        certificate = audit.reflection_certificate()
        self.assertEqual(certificate["determinant"], 1)
        self.assertTrue(certificate["R_maps_sm_singlet_Y0_to_flipped"])
        self.assertTrue(certificate["R_fixes_p"])
        self.assertFalse(certificate["R_fixes_F"])


if __name__ == "__main__":
    unittest.main()
