#!/usr/bin/env python3
"""Tests for the historical mixed-representation ledger snapshot."""
from __future__ import annotations

import unittest

import mixed_rep_hilbert_series_v20 as mod


class HistoricalMixedRepLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "HISTORICAL_MIXED_REP_LEDGER_EXECUTED__SIGNED_AUDIT_REQUIRED",
        )
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        flags = self.report["flag"]
        self.assertTrue(flags["historical_ledger_snapshot"])
        self.assertTrue(flags["historical_complete_claim_falsified"])
        self.assertFalse(flags["mixed_rep_charge_so10_filtered_renorm_hilbert_closed"])
        self.assertFalse(flags["mixed_rep_full_hilbert_series"])
        self.assertFalse(flags["mixed_rep_unfiltered_molien_haar_series"])
        self.assertFalse(flags["kronecker_forbidden_channels_excluded"])
        self.assertTrue(flags["signed_audit_required"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_historical_count_and_grades(self):
        basis = self.report["filtered_basis"]
        self.assertEqual(basis["historical_claimed_total"], 25)
        self.assertEqual(basis["n_invariants_total"], 25)
        self.assertFalse(basis["complete_filtered_renorm_basis"])
        self.assertTrue(basis["signed_audit_required"])
        self.assertTrue(basis["is_historical_snapshot"])
        self.assertEqual(basis["multiplicity_by_grade"]["t2"], 5)
        self.assertIn("t^2", basis["generating_function_filtered"])
        self.assertIn("t^3", basis["generating_function_filtered"])
        self.assertIn("t^4", basis["generating_function_filtered"])

    def test_forbidden_historical_entry_detected(self):
        invalid = {
            row["name"]: row
            for row in self.report["filtered_basis"]["historical_invalid_entries"]
        }
        self.assertIn("210_H 10_H^dag 10_H", invalid)
        self.assertEqual(
            invalid["210_H 10_H^dag 10_H"]["canonical_status"],
            "SO10_FORBIDDEN",
        )
        self.assertFalse(invalid["210_H 10_H^dag 10_H"]["signed_valid"])

    def test_signed_audit_module_is_required(self):
        included_names = {
            row["name"] for row in self.report["filtered_basis"]["included"]
        }
        self.assertIn("210 · 10 · 126 · S", included_names)
        self.assertIn("210_H 10_H^dag 10_H", included_names)
        self.assertTrue(self.report["filtered_basis"]["signed_audit_required"])


if __name__ == "__main__":
    unittest.main()
