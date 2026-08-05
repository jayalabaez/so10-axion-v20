#!/usr/bin/env python3
import unittest

import g1_renormalizable_operator_inventory_v20 as inventory


class G1RenormalizableOperatorInventoryTests(unittest.TestCase):
    def test_operator_charge_and_existence(self):
        row = inventory.missing_operator()
        self.assertEqual(row["charge_totals"]["PQ"], 0)
        self.assertEqual(row["charge_totals"]["X"], 0)
        self.assertEqual(row["charge_totals"]["Z17"], 0)
        self.assertEqual(row["status"], "ALLOWED")
        self.assertEqual(row["multiplicity"], 1)

    def test_corrected_catalogue_adds_exactly_one(self):
        historical = inventory.historical.operator_catalogue()
        corrected = inventory.corrected_operator_catalogue()
        self.assertEqual(len(corrected), len(historical) + 1)
        self.assertEqual(
            sum(row["name"] == inventory.MISSING_NAME for row in corrected), 1
        )

    def test_selected_vacuum_is_exact_null(self):
        report = inventory.build_report()
        self.assertEqual(report["n_failed"], 0, report)
        self.assertLess(report["selected_vacuum"]["Q_Delta_frobenius"], 1e-12)
        self.assertFalse(report["selected_vacuum"]["operator_value_nonzero"])
        self.assertFalse(report["flags"]["new_selected_phase_lock_found"])

    def test_fail_closed_scope(self):
        report = inventory.build_report()
        self.assertEqual(report["overall_state"], "BLOCKED")
        self.assertTrue(report["scope"]["operator_existence_closed"])
        self.assertTrue(report["scope"]["operator_multiplicity_closed"])
        self.assertFalse(report["scope"]["full_fluctuation_hessian_contribution_closed"])
        self.assertFalse(report["scope"]["complete_mixed_invariant_ring_G1_closed"])
        self.assertFalse(report["flags"]["whole_model_validated"])


if __name__ == "__main__":
    unittest.main()
