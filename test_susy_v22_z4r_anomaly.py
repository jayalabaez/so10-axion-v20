from __future__ import annotations

import json
import unittest

import susy_v22_z4r_anomaly as anomaly


class SusyV22Z4RAnomalyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = anomaly.build_report()

    def test_all_mixed_anomalies_pass(self) -> None:
        self.assertEqual(self.report["n_failed"], 0)
        self.assertTrue(all(self.report["checks"].values()))

    def test_mod_eta_and_exact_conditions(self) -> None:
        a = self.report["anomalies"]
        self.assertEqual(a["SO10_squared_Z4R"] % 2, 0)
        self.assertEqual(a["U1X_squared_Z4R"] % 2, 0)
        self.assertEqual(a["U1X_Z4R_squared"], 0)
        self.assertEqual(a["gravity_squared_Z4R"] % 2, 0)

    def test_R0_anomaly_partner_is_not_optional(self) -> None:
        self.assertNotEqual((self.report["anomalies"]["gravity_squared_Z4R"] + 1) % 2, 0)

    def test_no_gate_overclaim(self) -> None:
        b = self.report["claim_boundary"]
        self.assertTrue(b["Z4R_mixed_anomaly_arithmetic_closed"])
        self.assertTrue(b["Z4R_source_bound"])
        self.assertFalse(b["Z4R_vacuum_and_soft_sector_preserved"])
        self.assertFalse(b["canonical_G4_closed"])

    def test_outputs_fresh(self) -> None:
        self.assertEqual(json.loads(anomaly.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(anomaly.OUT_MD.read_text(encoding="utf-8"), anomaly.markdown(self.report))


if __name__ == "__main__": unittest.main()
