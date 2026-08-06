#!/usr/bin/env python3
import unittest

import nonsusy_sm_triplet_branching_census_v20 as mod


class BranchingCensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_census_passes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(
            self.report["status"],
            "NONSUSY_SM_TRIPLET_BRANCHING_CENSUS_PARTIAL__NORM_AND_CG_OPEN",
        )
        self.assertEqual(self.report["overall_state"], "BLOCKED")

    def test_working_basis_aulakh_t1_t2_t4(self):
        basis = self.report["working_light_basis"]
        self.assertEqual(
            basis, ["T_10", "Tbar_10", "T_126", "Tprime_126"]
        )
        self.assertEqual(
            self.report["aulakh_mapping"]["t4"], "Tprime_126"
        )
        self.assertIn("absent", self.report["aulakh_mapping"]["t3"])

    def test_no_invented_completion(self):
        flag = self.report["flag"]
        self.assertTrue(flag["published_ps_branching_census_ready"])
        self.assertFalse(flag["kinetic_normalization_derived"])
        self.assertFalse(flag["nonsusy_component_cg_derived"])
        self.assertFalse(flag["physical_component_CG_complete"])
        self.assertFalse(flag["physical_triplet_spectrum_complete"])
        self.assertFalse(flag["exact_unique_proton_lifetime"])
        self.assertFalse(flag["whole_model_validated"])
        self.assertFalse(flag["whole_model_excluded"])

    def test_issue_106_next_steps_present(self):
        self.assertEqual(self.report["issue"]["number"], 106)
        self.assertTrue(self.report["next_exact_calculation"])
        self.assertTrue(
            any("Clebsch" in step or "clebsch" in step.lower()
                for step in self.report["next_exact_calculation"])
        )


if __name__ == "__main__":
    unittest.main()
