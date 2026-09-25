#!/usr/bin/env python3
"""Tests for the physical-target audit of the certified G3 candidate."""
from __future__ import annotations

import json
import unittest

import numpy as np

import g3_candidate_physical_target_audit_v20 as audit


class PhysicalTargetAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = audit.build_report()

    def test_all_checks_pass_and_scope_is_fail_closed(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(
            self.report["status"],
            "G3_CERTIFIED_POINT_IS_NOT_AN_SM_VACUUM__DELTA_R_BREAKS_HYPERCHARGE__H_BREAKS_SU2L_AT_GUT_SCALE__G3_OPEN",
        )
        flags = self.report["flags"]
        self.assertFalse(flags["certified_candidate_is_physical_vacuum"])
        self.assertTrue(flags["certified_candidate_breaks_electroweak_symmetry_at_gut_scale"])
        self.assertFalse(flags["certified_candidate_is_sm_vacuum"])
        self.assertTrue(flags["certified_candidate_breaks_hypercharge_at_gut_scale"])
        self.assertFalse(flags["g3_closed"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_certified_h_vev_is_an_electroweak_doublet_at_the_gut_scale(self) -> None:
        candidate = self.report["certified_candidate"]
        self.assertLess(candidate["gradient_max_abs"], 1.0e-10)
        self.assertAlmostEqual(candidate["H_over_Phi_complex_norm_ratio"], 1.0, places=12)
        self.assertAlmostEqual(candidate["H_weight_in_electroweak_doublet_block"], 1.0, places=12)
        self.assertEqual(sorted(candidate["H_components"]["nonzero"]), ["6", "7"])

    def test_gut_point_h10_modes_are_all_tachyonic(self) -> None:
        spectrum = self.report["gut_point_h10"]["spectrum"]
        doublets = [(row["mass_squared"], row["complex_multiplicity"]) for row in spectrum["weak_doublets"]]
        triplets = [(row["mass_squared"], row["complex_multiplicity"]) for row in spectrum["colour_triplets"]]
        np.testing.assert_allclose([value for value, _ in doublets], [-2.0, -0.8], atol=1.0e-12)
        np.testing.assert_allclose([value for value, _ in triplets], [-1.998, -0.802], atol=1.0e-12)
        self.assertEqual([count for _, count in doublets], [2, 2])
        self.assertEqual([count for _, count in triplets], [3, 3])
        self.assertLess(spectrum["maximum_eigenvalue"], 0.0)

    def test_only_beta_term_splits_the_five_plets(self) -> None:
        gut = self.report["gut_point_h10"]
        np.testing.assert_allclose(gut["doublet_triplet_splitting_per_five_plet"], [0.002, 0.002], atol=1.0e-12)
        self.assertLess(gut["O46_54_channel_block_max_abs_at_F"], 1.0e-12)
        np.testing.assert_allclose(gut["beta_O35_45_block"]["colour_triplets"], [-0.002, 0.002], atol=1.0e-12)
        np.testing.assert_allclose(gut["beta_O35_45_block"]["weak_doublets"], [0.0], atol=1.0e-12)

    def test_o06_tuning_gives_one_massless_doublet_and_light_triplet(self) -> None:
        tuning = self.report["o06_tuning"]
        self.assertEqual(tuning["certified_O06"], -2.0)
        self.assertAlmostEqual(tuning["tuned_O06"], 0.0, places=12)
        self.assertEqual(tuning["massless_doublets"], 1)
        self.assertAlmostEqual(tuning["partner_triplet_mass_squared_over_M2"], 1 / 500, places=12)
        self.assertAlmostEqual(tuning["partner_triplet_mass_over_M"], 500 ** -0.5, places=12)

    def test_axion_singlet_has_no_portal_in_the_benchmark(self) -> None:
        portals = self.report["singlet_portals"]
        self.assertTrue(portals["all_portals_vanish"])
        self.assertIn("O12_B01_Hdag_Hdag_pair", portals["S_and_Phi17_portals"])
        self.assertEqual(len(portals["S_and_Phi17_portals"]), 8)

    def test_certified_vevs_are_not_at_the_physical_hierarchy(self) -> None:
        hierarchy = self.report["hierarchy"]
        self.assertFalse(hierarchy["certified_candidate_at_physical_hierarchy"])
        self.assertFalse(self.report["flags"]["certified_candidate_at_physical_hierarchy"])
        scales = hierarchy["Sigma_and_S_scale_over_M_GUT"]
        self.assertEqual(scales["certified"], 0.2)
        self.assertLess(scales["physical"], 1.0e-4)
        self.assertGreater(hierarchy["block_norms"]["Sigma126bar"]["ratio"], 1.0e3)
        partner = hierarchy["triplet_partner_mass_GeV"]["F_branch_extrapolated_to_M_I"]
        self.assertAlmostEqual(partner, (1 / 20) ** 0.5 * hierarchy["M_I_GeV"], delta=1.0)

    def test_sm_embedding_is_bound_to_the_exact_charge_audit(self) -> None:
        embedding = self.report["sm_embedding"]
        self.assertTrue(embedding["binding_ok"])
        self.assertFalse(embedding["certified_point_is_sm_vacuum"])
        self.assertFalse(embedding["gut_point_is_sm_vacuum"])
        self.assertEqual(embedding["heavy_pair_stabilizer_dimension"], 12)
        self.assertEqual(embedding["heavy_pair_centre_spectrum_on_10"]["colour_block_0_5"], {"0": 6})
        self.assertEqual(str(embedding["H_chi_standard_embedding_charges"]["Q_em"]), "1")

    def test_committed_artifact_matches_fresh_report(self) -> None:
        committed = json.loads(audit.OUT_JSON.read_text(encoding="utf-8"))
        fresh = json.loads(json.dumps(audit._jsonable(self.report), sort_keys=True))
        for key in ("status", "checks", "flags", "gut_point_h10", "o06_tuning", "singlet_portals", "hierarchy", "sm_embedding"):
            self.assertEqual(audit.report_mismatches(committed[key], fresh[key], key), [])


class MassMatrixHelpersTest(unittest.TestCase):
    def test_holomorphic_mass_term_is_detected(self) -> None:
        import live_g2_canonical_486_field_chart_v20 as chart

        hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM))
        start = chart.H_SLICE.start
        # V = m (Re h0^2 - Im h0^2): a holomorphic h0 h0 + c.c. mass.
        hessian[start, start] = 1.0
        hessian[start + 1, start + 1] = -1.0
        _, holomorphic = audit.hermitian_h_mass_matrix(hessian)
        self.assertEqual(holomorphic, 2.0)

    def test_colour_weak_mixing_is_reported(self) -> None:
        matrix = np.eye(10, dtype=complex)
        matrix[0, 6] = matrix[6, 0] = 0.25
        self.assertEqual(audit.sm_branch_spectrum(matrix)["triplet_doublet_mixing_residual"], 0.25)


if __name__ == "__main__":
    unittest.main()
