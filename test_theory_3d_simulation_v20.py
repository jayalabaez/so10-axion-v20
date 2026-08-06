#!/usr/bin/env python3
import json
import unittest

import next_gen_g1_g6_progress_31_gate_v20 as p31
import theory_3d_simulation_v20 as sim


class Progress31AndTheory3DTests(unittest.TestCase):
    def test_progress31_promotes_hsigma_without_claiming_closure(self):
        report = p31.build_report()
        self.assertEqual(report["n_failed"], 0, report["failures"])
        self.assertEqual(report["n_closed_subproblems"], 31)
        self.assertTrue(
            report["closed_subproblems"]["exact_HSigma_45_triplet_background_formula"]
        )
        self.assertEqual(report["gate_states"]["G1"], "OPEN")
        self.assertEqual(report["gate_states"]["G6"], "PARTIAL")
        self.assertFalse(report["flag"]["whole_model_validated"])
        self.assertFalse(report["flag"]["exact_unique_proton_lifetime"])

    def test_theory_3d_payload_and_html(self):
        payload = sim.build_payload(v_r=1.1, lambda_hsigma_45=0.3)
        self.assertEqual(payload["certificate"]["n_closed_subproblems"], 30)
        self.assertFalse(payload["honesty"]["whole_model_validated"])
        shift = 0.3 * 1.1**2
        self.assertAlmostEqual(payload["scene"]["hsigma_shift"], shift)
        kc = payload["scene"]["k_color"]
        self.assertAlmostEqual(payload["scene"]["masses_GeV2"]["T10"], -shift + 0.15 * kc)
        self.assertAlmostEqual(payload["scene"]["masses_GeV2"]["T10bar"], +shift - 0.15 * kc)
        self.assertEqual(payload["scene"]["delta_B"], 0.0)

        sim.write_artifacts(payload)
        self.assertTrue(sim.OUT_HTML.exists())
        html = sim.OUT_HTML.read_text(encoding="utf-8")
        self.assertIn("three", html.lower())
        self.assertIn("lambda_hsigma_45", html)
        self.assertTrue(sim.CERT_COPY.exists())
        cert = json.loads(sim.CERT_COPY.read_text(encoding="utf-8"))
        self.assertEqual(cert["n_closed_subproblems"], 30)


if __name__ == "__main__":
    unittest.main()
