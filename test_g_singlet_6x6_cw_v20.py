#!/usr/bin/env python3
import unittest

import g_singlet_6x6_cw_v20 as mod


class GSingletSourceCorrectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_withdrawn_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertEqual(
            self.report["status"],
            "CAL_G_SOURCE_CORRECTED__SCALAR_CW_WITHDRAWN",
        )

    def test_source_matrix_remains_available(self):
        self.assertEqual(self.report["spectrum"]["n_modes"], 6)
        self.assertGreater(self.report["spectrum"]["mass_min_GeV"], 0.0)
        self.assertTrue(self.report["flag"]["cal_G_eq102_transcribed"])
        self.assertTrue(
            self.report["flag"][
                "cal_G_susy_chiral_gaugino_diagnostic_only"
            ]
        )
        self.assertTrue(
            self.report["flag"]["g6_gaugino_admixture_identified"]
        )

    def test_no_scalar_cw_contribution(self):
        self.assertTrue(
            self.report["flag"]["scalar_CW_contribution_withdrawn"]
        )
        self.assertFalse(self.report["flag"]["g_singlet_6x6_complete"])
        self.assertEqual(self.report["spectrum"]["n_modes_in_cw"], 0)
        self.assertEqual(self.report["spectrum"]["masses_in_cw_GeV"], [])
        self.assertEqual(self.report["g_singlet_cw"]["n_entries"], 0)
        self.assertEqual(self.report["g_singlet_cw"]["V1_GeV4"], 0.0)
        self.assertEqual(self.report["combined"]["abs_g_over_abs_prev"], 0.0)
        self.assertEqual(mod.cw_entries([1.0, 2.0]), [])

    def test_formal_null_is_not_called_scalar_goldstone(self):
        null = self.report["chiral_5x5_null"]
        self.assertFalse(null["physical_scalar_interpretation_allowed"])
        self.assertTrue(
            self.report["flag"][
                "goldstone_compatible_M_slice_is_susy_only"
            ]
        )

    def test_no_model_overclaim(self):
        self.assertFalse(self.report["flag"]["whole_model_validated"])
        self.assertFalse(self.report["flag"]["whole_model_excluded"])
        self.assertFalse(self.report["flag"]["exact_unique_proton_lifetime"])


if __name__ == "__main__":
    unittest.main()
