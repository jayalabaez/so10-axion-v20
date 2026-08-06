#!/usr/bin/env python3
from __future__ import annotations

import unittest

import next_gen_triplet_tensor_gate_v20 as gate


class NextGenTripletTensorGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = gate.build_report()

    def test_gate_executes_fail_closed(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "PARTIAL")

    def test_all_exact_subproblems_closed(self) -> None:
        self.assertTrue(all(self.report["exact_subproblems_closed"].values()))

    def test_legacy_proxy_rejected(self) -> None:
        structure = self.report["accepted_quadratic_structure"]
        self.assertFalse(structure["legacy_symmetric_4x4_authoritative"])
        self.assertFalse(self.report["flag"]["legacy_triplet_proxy_authoritative"])

    def test_full_model_claims_remain_false(self) -> None:
        flags = self.report["flag"]
        self.assertFalse(flags["complete_G1_invariant_ring"])
        self.assertFalse(flags["complete_G2_component_potential"])
        self.assertFalse(flags["physical_triplet_spectrum_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])
        self.assertFalse(flags["empirical_discovery"])

    def test_nambu_hessian_requirement_recorded(self) -> None:
        text = self.report["accepted_quadratic_structure"][
            "physical_real_hessian_requirement"
        ]
        self.assertIn("Nambu-doubled", text)
        self.assertIn("dimension-one 4x4", text)


if __name__ == "__main__":
    unittest.main()
