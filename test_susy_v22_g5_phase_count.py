from __future__ import annotations

import json
import unittest

import susy_v22_g5_phase_count as phase


class SusyV22G5PhaseCountTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = phase.build_report()

    def test_exact_phase_quotient(self) -> None:
        self.assertEqual(self.report["n_failed"], 0)
        self.assertEqual(self.report["exact_counts"], {
            "fixed_nonquotient_phase_rank": 2,
            "GUT_phase_tangent_dimension": 3,
            "broken_gauge_phase_rank": 2,
            "physical_GUT_phase_dimension": 1,
        })

    def test_axion_is_independent_and_mp_goldstone_is_absent(self) -> None:
        self.assertEqual(phase.rank(list(self.report["broken_gauge_phase_rows"].values()) + [self.report["intended_axion_vector"]]), 3)
        self.assertTrue(self.report["checks"]["continuous_missing_partner_U1_is_absent_from_source"])

    def test_no_G5_overclaim(self) -> None:
        self.assertTrue(all(value is False for value in self.report["remaining_requirements"].values()))
        boundary = self.report["claim_boundary"]
        self.assertTrue(boundary["declared_VEV_sector_one_axion_phase_count_closed"])
        self.assertFalse(boundary["full_calG_revalidation_closed"])
        self.assertFalse(boundary["canonical_G5_closed"])

    def test_adversarial_loss_of_gauge_rank_leaves_two_phases(self) -> None:
        self.assertEqual(3 - phase.rank([[1, 0, 0], [2, 0, 0]]), 2)

    def test_frozen_outputs(self) -> None:
        self.assertEqual(json.loads(phase.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(phase.OUT_MD.read_text(encoding="utf-8"), phase.markdown(self.report))


if __name__ == "__main__":
    unittest.main()
