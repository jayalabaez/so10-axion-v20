#!/usr/bin/env python3
import unittest

import nonsusy_triplet_component_ledger_v20 as mod


class SignedTripletLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_signed_ledger_passes(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(
            self.report["status"],
            "SIGNED_TRIPLET_COMPONENT_LEDGER_BUILT__CG_AND_MULTIPLICITY_OPEN",
        )

    def test_forbidden_operators_absent(self):
        listed = {
            name
            for entry in self.report["matrix_entries"].values()
            for name in entry["operators"]
        }
        self.assertFalse(listed.intersection(mod.FORBIDDEN))
        self.assertEqual(
            self.report["forbidden_operator_status"]["210_H 10_H^dag 10_H"],
            "SO10_FORBIDDEN",
        )

    def test_mass_squared_and_cg_fail_closed(self):
        self.assertTrue(
            all(name.endswith("_GeV2") for name in self.report["matrix_entries"])
        )
        self.assertFalse(self.report["flag"]["physical_component_CG_complete"])
        self.assertFalse(self.report["flag"]["physical_triplet_spectrum_complete"])
        self.assertFalse(self.report["flag"]["exact_unique_proton_lifetime"])

    def test_unknown_multiplicities_are_explicit(self):
        states = {row["id"]: row for row in self.report["components"]}
        self.assertIsNone(states["T126_additional_OPEN"]["sm"])
        self.assertIsNone(states["T210_mixing_fragments_OPEN"]["sm"])
        self.assertFalse(self.report["flag"]["full_component_basis_complete"])


if __name__ == "__main__":
    unittest.main()
