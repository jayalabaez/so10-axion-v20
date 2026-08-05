#!/usr/bin/env python3
import unittest

import selected_vacuum_phase_invariant_dim6_metric_audit_v20 as mod


class SelectedVacuumDim6MetricPhaseAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertEqual(
            self.report["status"],
            "DIM6_PHASE_METRIC_SECTOR_ZERO_ON_CANONICAL_SELECTED_VACUUM__EPSILON_OPEN",
        )

    def test_finite_enumeration_counts(self):
        counts = self.report["counts"]
        self.assertEqual(counts["charge_allowed_phase_sensitive_monomials"], 110)
        self.assertEqual(counts["distinct_tensor_signatures"], 88)
        self.assertEqual(
            counts["odd_H_signatures_removed_by_SU2L_doublet_parity"], 58
        )
        self.assertEqual(counts["even_H_signatures"], 30)
        self.assertEqual(counts["conjugacy_representatives"], 15)
        self.assertEqual(counts["metric_graphs_per_weak_embedding"], 1006)
        self.assertEqual(counts["weak_embeddings_tested"], 2)

    def test_selected_metric_sector_is_zero(self):
        selected = self.report["selected_vacuum"]
        self.assertLess(selected["maximum_abs_metric_contraction"], mod.ZERO_TOL)
        for rows in selected["evaluations"].values():
            self.assertEqual(len(rows), 15)
            for row in rows:
                self.assertTrue(row["all_metric_contractions_zero"], row)

    def test_engine_has_nonzero_generic_controls(self):
        controls = self.report["generic_engine_controls"]
        self.assertEqual(len(controls), 3)
        for row in controls:
            self.assertFalse(row["all_metric_contractions_zero"], row)
            self.assertGreater(row["max_abs_contraction"], mod.ZERO_TOL)

    def test_scope_is_not_overclaimed(self):
        flags = self.report["flags"]
        self.assertTrue(flags["charge_enumeration_through_dim6_complete"])
        self.assertTrue(
            flags["metric_graph_enumeration_complete_for_15_representatives"]
        )
        self.assertFalse(flags["nonzero_selected_metric_phase_channel_found"])
        self.assertFalse(flags["dimension6_full_SO10_no_go_proven"])
        self.assertTrue(flags["epsilon_sector_open"])
        self.assertTrue(flags["published_hEW_component_dictionary_open"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
