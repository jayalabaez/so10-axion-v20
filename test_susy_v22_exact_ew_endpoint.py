from __future__ import annotations

import json
import unittest

import susy_v22_exact_ew_endpoint as endpoint


class ExactEwEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None: cls.report = endpoint.build_report()

    def test_exact_endpoint(self) -> None:
        self.assertEqual(self.report["n_failed"], 0)
        self.assertTrue(all(self.report["checks"].values()))
        self.assertEqual(self.report["exact_inputs"]["tan_beta"], "4/3")

    def test_stationarity_and_positive_physical_modes(self) -> None:
        self.assertEqual(set(self.report["stationarity"].values()), {"0"})
        cert=self.report["tree_scalar_certificate"]
        self.assertNotEqual(cert["CP_even_determinant_GeV4"], "0")
        self.assertEqual(cert["CP_odd_characteristic"]["determinant_GeV4"], "0")

    def test_does_not_overclaim_G4(self) -> None:
        self.assertTrue(self.report["claim_boundary"]["exact_tree_EW_endpoint_closed"])
        self.assertFalse(self.report["claim_boundary"]["canonical_G4_closed"])
        self.assertFalse(self.report["protection_boundary"]["full_superpartner_threshold_and_RGE_replay_complete"])

    def test_outputs_fresh(self) -> None:
        self.assertEqual(json.loads(endpoint.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(endpoint.OUT_MD.read_text(encoding="utf-8"), endpoint.markdown(self.report))


if __name__ == "__main__": unittest.main()
