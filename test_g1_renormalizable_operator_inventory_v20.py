#!/usr/bin/env python3
import unittest

import g1_renormalizable_operator_inventory_v20 as inventory


class G1RenormalizableOperatorInventoryTests(unittest.TestCase):
    def test_both_operators_are_charge_neutral_and_allowed(self):
        rows = inventory.missing_operators()
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertEqual(row["charge_totals"]["PQ"], 0)
            self.assertEqual(row["charge_totals"]["X"], 0)
            self.assertEqual(row["charge_totals"]["Z17"], 0)
            self.assertEqual(row["status"], "ALLOWED")
            self.assertEqual(row["multiplicity"], 1)

    def test_corrected_catalogue_adds_exactly_two(self):
        historical = inventory.historical.operator_catalogue()
        corrected = inventory.corrected_operator_catalogue()
        self.assertEqual(len(corrected), len(historical) + 2)
        for name in (inventory.CUBIC_NAME, inventory.QUARTIC_NAME):
            self.assertEqual(sum(row["name"] == name for row in corrected), 1)

    def test_selected_backgrounds_are_exact_nulls(self):
        report = inventory.build_report()
        self.assertEqual(report["n_failed"], 0, report)
        self.assertLess(report["cubic"]["selected_image_norm"], 1e-6)
        self.assertLess(report["quartic_54"]["selected_Q_Delta_frobenius"], 1e-12)
        self.assertFalse(report["cubic"]["selected_background_value_nonzero"])
        self.assertFalse(report["quartic_54"]["selected_background_value_nonzero"])
        self.assertFalse(report["flags"]["new_selected_phase_lock_found"])

    def test_generic_fluctuation_maps_are_nonzero(self):
        report = inventory.build_report()
        self.assertGreater(report["cubic"]["full_map_rank"], 0)
        self.assertGreater(report["cubic"]["largest_singular_value_GeV"], 0.0)
        self.assertTrue(report["cubic"]["generic_fluctuation_block_nonzero"])
        self.assertGreater(report["quartic_54"]["generic_C_126_to_54"], 0.0)
        self.assertTrue(report["quartic_54"]["generic_fluctuation_hessian_relevant"])

    def test_fail_closed_scope(self):
        report = inventory.build_report()
        self.assertEqual(report["overall_state"], "BLOCKED")
        self.assertTrue(report["scope"]["two_operator_existence_closed"])
        self.assertTrue(report["scope"]["two_operator_multiplicities_closed"])
        self.assertTrue(report["flags"]["dimensionful_cubic_required"])
        self.assertTrue(report["flags"]["renormalizable_54_quartic_required"])
        self.assertFalse(report["scope"]["full_cubic_fluctuation_block_closed"])
        self.assertFalse(report["scope"]["full_quartic_fluctuation_hessian_closed"])
        self.assertFalse(report["scope"]["complete_mixed_invariant_ring_G1_closed"])
        self.assertFalse(report["flags"]["whole_model_validated"])


if __name__ == "__main__":
    unittest.main()
