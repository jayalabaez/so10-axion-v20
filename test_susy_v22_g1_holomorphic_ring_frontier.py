from __future__ import annotations

import copy
import json
import unittest

import susy_v22_g1_holomorphic_ring_frontier as ring


class SusyV22G1HolomorphicRingFrontierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = ring.build_report()

    def test_exact_character_and_flavour_anchors(self) -> None:
        anchors = self.report["anchors"]
        self.assertEqual(anchors["dimensions"], {
            "10": 10, "16": 16, "16bar": 16, "120": 120,
            "126": 126, "126bar": 126, "210": 210,
        })
        self.assertEqual(anchors["F_F_H10m_components"], 6)
        self.assertEqual(anchors["F_F_T120m_components"], 3)
        self.assertEqual(anchors["XMP_F_F_DeltaB_components"], 6)
        self.assertEqual(anchors["Splus_SpecS_SpecB_components"], 25)

    def test_declared_terms_are_allowed_but_catalogue_is_incomplete(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertFalse(self.report["declared_but_forbidden"])
        self.assertGreater(self.report["counts"]["allowed_undeclared_sectors"], 0)
        self.assertFalse(self.report["catalogue_verdict"]["complete_under_declared_symmetries"])
        self.assertIn("INCOMPLETE", self.report["status"])

    def test_exact_rows_are_charge_allowed(self) -> None:
        for row in self.report["all_allowed_sectors"]:
            self.assertEqual(row["X_sum"], 0)
            self.assertEqual(row["R4_sum_mod_4"], 2)
            self.assertGreater(row["so10_flavour_component_multiplicity"], 0)

    def test_claim_boundary_fails_closed(self) -> None:
        boundary = self.report["claim_boundary"]
        self.assertTrue(boundary["degree_le_4_holomorphic_charge_and_character_census_closed"])
        self.assertFalse(boundary["declared_superpotential_catalogue_complete"])
        self.assertFalse(boundary["full_V22_G1_closed"])
        self.assertFalse(boundary["V22_G2_closed"])

    def test_rendered_outputs_are_current(self) -> None:
        self.assertEqual(json.loads(ring.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(ring.OUT_MD.read_text(encoding="utf-8"), ring.markdown(self.report))

    def test_core_hash_covers_semantics(self) -> None:
        changed = copy.deepcopy(self.report)
        changed["claim_boundary"]["full_V22_G1_closed"] = True
        self.assertNotEqual(ring.canonical_sha(self.report), ring.canonical_sha(changed))


if __name__ == "__main__":
    unittest.main()
