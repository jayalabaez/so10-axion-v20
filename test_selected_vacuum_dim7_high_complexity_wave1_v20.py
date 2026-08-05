#!/usr/bin/env python3
import json
import unittest

import selected_vacuum_dim7_high_complexity_wave1_v20 as mod


class SelectedVacuumDim7HighComplexityWave1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if mod.OUT_JSON.is_file():
            cls.report = json.loads(mod.OUT_JSON.read_text(encoding="utf-8"))
        else:
            cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertIn(
            self.report["status"],
            {
                "DIM7_HIGH_COMPLEXITY_WAVE1_NONZERO_CHANNEL_FOUND__STATIONARITY_OPEN",
                "DIM7_HIGH_COMPLEXITY_WAVE1_ZERO__THREE_REPRESENTATIVES_OPEN",
            },
        )

    def test_wave_counts(self):
        wave = self.report["wave1"]
        self.assertEqual(len(wave["representatives"]), 2)
        self.assertEqual(wave["total_metric_graphs"], 11934)
        self.assertEqual(wave["total_graph_coefficient_evaluations"], 11934)
        signatures = [
            tuple(row["signature_P_D_Db_H_Hb"])
            for row in wave["representatives"]
        ]
        self.assertEqual(signatures, mod.EXPECTED_SIGNATURES)
        self.assertEqual(
            wave["n_nonzero_representatives"],
            len(wave["nonzero_representatives"]),
        )

    def test_remaining_count(self):
        self.assertEqual(
            len(self.report["remaining_high_complexity_representatives"]),
            3,
        )

    def test_nonzero_rank_if_found(self):
        for row in self.report["wave1"]["nonzero_representatives"]:
            self.assertGreater(row["maximum_abs_coefficient"], mod.TOL)
            for record in row["phase_rank_records"]:
                self.assertEqual(record["rank_with_kappa"], 2, record)
                self.assertTrue(record["null_is_PQ_1_1_minus2"], record)

    def test_scientific_boundary(self):
        flags = self.report["flags"]
        self.assertTrue(flags["wave1_complete"])
        self.assertFalse(flags["stationarity_rebuilt"])
        self.assertFalse(flags["selected_vacuum_fully_stabilized"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])
        self.assertEqual(
            flags["nonzero_dimension7_phase_channel_found"],
            bool(self.report["wave1"]["nonzero_representatives"]),
        )


if __name__ == "__main__":
    unittest.main()
