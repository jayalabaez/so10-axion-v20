from __future__ import annotations

import copy
import json
import math
import unittest

import canonical_g2_full_component_projection_dim6_v21 as g2
from _g2_contraction_graphs import sector_candidates
from _g2_metric_rank_probe import evaluate_metric_graph, sample_fields


class CanonicalG2FullComponentProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = g2.build_report()

    def test_report_closes_all_four_acceptance_criteria(self):
        self.assertTrue(self.report["closure_complete"])
        self.assertEqual(self.report["n_failed"], 0)
        self.assertEqual(len(self.report["acceptance_evidence"]), 4)
        self.assertTrue(
            all(row["passed"] is True for row in self.report["acceptance_evidence"].values())
        )

    def test_all_891_projection_records_are_unique_and_reconstructible(self):
        rows = self.report["projection_catalog"]
        self.assertEqual(len(rows), 891)
        self.assertEqual(len({row["direction_id"] for row in rows}), 891)
        self.assertTrue(
            all(
                row["PS_component_block_combinations"] >= 1
                and row["SM_component_block_combinations"] >= 1
                and row["PS_reconstruction_sha256"]
                and row["SM_reconstruction_sha256"]
                for row in rows
            )
        )

    def test_branching_dimensions_are_exact_for_all_fields(self):
        expected = {"P": 210, "H": 10, "Hb": 10, "D": 126, "Db": 126, "S": 1, "Sb": 1, "X": 1, "Xb": 1}
        for field, dimension in expected.items():
            with self.subTest(field=field):
                row = self.report["representation_component_blocks"][field]
                self.assertEqual(row["SO10_complex_dimension"], dimension)
                self.assertEqual(row["PS_dimension_sum"], dimension)
                self.assertEqual(row["SM_dimension_sum"], dimension)
                self.assertIs(row["dimension_identity"], True)
                self.assertIs(row["index_identity"], True)

    def test_lambda4_graph_equals_direct_cartesian_contraction(self):
        counts = (1, 1, 0, 1, 0)
        species = (0, 1, 3)
        fields = sample_fields(counts, 7, 20260814)
        metric, _ = sector_candidates(counts)
        graph_value = evaluate_metric_graph(species, metric[0][1], fields)
        direct = 0
        for p_key, p_value in fields[0].items():
            for h_key, h_value in fields[1].items():
                d_value = fields[3].get(p_key + h_key, 0)
                direct = (direct + p_value * h_value * d_value) % 1009
        self.assertEqual(graph_value, direct)
        self.assertEqual(
            self.report["explicit_required_coefficients"]["lambda4"]["formula"],
            "lambda4*S*H_e*P_abcd*D_abcde/4! + h.c.",
        )

    def test_lock_graph_equals_direct_54_cartesian_contraction(self):
        counts = (0, 2, 0, 2, 0)
        species = (1, 1, 3, 3)
        fields = sample_fields(counts, 7, 20260815)
        metric, _ = sector_candidates(counts)
        selected = metric[0]
        graph_value = evaluate_metric_graph(species, selected[1], fields)
        direct = 0
        h = fields[1]
        d = fields[3]
        buckets = {}
        for key, value in d.items():
            buckets.setdefault(key[1:], []).append((key[0], value))
        for entries in buckets.values():
            for first, left in entries:
                for second, right in entries:
                    direct = (
                        direct
                        + h.get((first,), 0) * h.get((second,), 0) * left * right
                    ) % 1009
        self.assertEqual(graph_value, direct)
        lock = self.report["explicit_required_coefficients"]["dimension_six_lock"]
        self.assertIn("/4!", lock["formula"])
        self.assertIn("54", lock["channel"])

    def test_component_catalog_tampering_changes_catalog_hash(self):
        forged = copy.deepcopy(self.report["projection_catalog"])
        forged[0]["PS_component_block_combinations"] += 1
        self.assertNotEqual(
            g2.sha(forged), self.report["proof_summary"]["projection_catalog_sha256"]
        )

    def test_frozen_outputs_equal_fresh_build(self):
        stored = json.loads(g2.OUT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(stored, self.report)
        self.assertEqual(g2.OUT_MD.read_text(encoding="utf-8"), g2.markdown(self.report))


if __name__ == "__main__":
    unittest.main()
