from __future__ import annotations

import json
import unittest

import susy_v22_g4_protection_frontier as frontier


class SusyV22G4ProtectionFrontierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = frontier.build_report()

    def test_scoped_protection_is_exact(self) -> None:
        self.assertEqual(self.report["n_failed"], 0)
        self.assertTrue(all(self.report["positive_frontier"].values()))
        self.assertTrue(all(row["supertrace_dof"] == 0 for row in self.report["exact_supersymmetric_cancellation"].values()))

    def test_no_canonical_overclaim(self) -> None:
        self.assertTrue(all(value is False for value in self.report["open_canonical_requirements"].values()))
        boundary = self.report["claim_boundary"]
        self.assertTrue(boundary["scoped_hierarchy_protection_mechanism_closed"])
        self.assertFalse(boundary["canonical_V22_G4_closed"])
        self.assertFalse(boundary["canonical_V22_G5_closed"])

    def test_v21_g3_scope_is_preserved_not_inherited(self) -> None:
        state = self.report["scientific_interpretation"]
        self.assertFalse(state["V21_G3_invalidated"])
        self.assertFalse(state["V22_inherits_V21_G3"])

    def test_R_protection_and_anomaly_theorems_are_source_bound(self) -> None:
        deps = self.report["dependencies"]
        self.assertIn("holomorphic_R_protection", deps)
        self.assertIn("discrete_R_anomaly", deps)
        self.assertTrue(self.report["positive_frontier"]["holomorphic_light_bilinears_are_forbidden_by_source_landed_R_rule"])
        self.assertTrue(self.report["positive_frontier"]["mixed_discrete_R_anomalies_cancel_mod_eta"])
        self.assertFalse(self.report["open_canonical_requirements"]["full_F_D_soft_vacuum_proves_every_R_charge_two_missing_partner_126_VEV_is_zero"])

    def test_frozen_outputs(self) -> None:
        self.assertEqual(json.loads(frontier.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(frontier.OUT_MD.read_text(encoding="utf-8"), frontier.markdown(self.report))


if __name__ == "__main__": unittest.main()
