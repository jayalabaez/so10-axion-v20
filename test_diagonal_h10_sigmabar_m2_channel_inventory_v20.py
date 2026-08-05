#!/usr/bin/env python3
import unittest

import diagonal_h10_sigmabar_m2_channel_inventory_v20 as inv


class DiagonalM2ChannelInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = inv.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flag"]["classic_channel_inventory_transcribed"])
        self.assertFalse(self.report["flag"]["diagonal_h10_m2_derived"])
        self.assertFalse(self.report["flag"]["diagonal_sigmabar_m2_derived"])
        self.assertFalse(self.report["flag"]["cg_tensors_invented"])
        self.assertFalse(self.report["flag"]["full_invariant_ring"])
        self.assertFalse(self.report["flag"]["full_component_hessian"])
        self.assertFalse(self.report["flag"]["whole_model_validated"])
        self.assertFalse(self.report["flag"]["whole_model_excluded"])

    def test_classic_channels_present(self):
        ids = {row["id"] for row in self.report["channels"]}
        for required in (
            "210x210_45",
            "210x210_54",
            "210x210_210",
            "210x210_1050",
            "210x126_10",
            "210x126_120",
            "210x126_126",
            "210x126_320",
            "126_quartic_54",
            "126_quartic_1050",
            "126_quartic_4125",
            "10x10_54",
            "lambda4_portal_offdiag",
        ):
            self.assertIn(required, ids)

    def test_pq_filter_and_open_slots(self):
        self.assertTrue(self.report["flag"]["pq_z17_charge_filter_applied"])
        self.assertGreaterEqual(
            self.report["counts"]["n_open_cartesian_slots"], 10
        )
        portal = next(
            row
            for row in self.report["channels"]
            if row["id"] == "lambda4_portal_offdiag"
        )
        self.assertEqual(portal["ledger_status"], "OFFDIAG_CLOSED_DIAG_OPEN")
        self.assertFalse(portal["feeds_diag_H10"])
        self.assertFalse(portal["feeds_diag_Sigmabar"])

    def test_remaining_blockers(self):
        blockers = self.report["remaining_blockers"]
        self.assertTrue(blockers["derive_H10_diagonal_component_mass_squared"])
        self.assertTrue(
            blockers["derive_Sigmabar126_diagonal_component_mass_squared"]
        )
        self.assertTrue(blockers["complete_nonsusy_invariant_ring_G1"])


if __name__ == "__main__":
    unittest.main()
