from __future__ import annotations

import copy
import json
import unittest

import susy_v22_g1_shaping_symmetry_nogo as nogo


class SusyV22G1ShapingSymmetryNoGoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = nogo.build_report()

    def test_exact_five_by_five_replacement_grid(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["counts"], {
            "drivers": 5,
            "replacement_grid_sectors": 25,
            "diagonal_declared_sectors": 5,
            "off_diagonal_allowed_undeclared_sectors": 20,
        })

    def test_no_ordinary_Abelian_patch_is_claimed(self) -> None:
        resolution = self.report["resolution"]
        self.assertFalse(resolution["ordinary_Abelian_shaping_charge_patch_exists"])
        self.assertFalse(resolution["G2_promotion_allowed_before_G1_repair"])
        self.assertIn("linear tadpoles", resolution["reason"])

    def test_scope_keeps_real_escape_routes_open(self) -> None:
        boundary = self.report["claim_boundary"]
        self.assertTrue(boundary["neutral_coefficient_Abelian_shaping_no_go_closed"])
        self.assertFalse(boundary["all_possible_UV_selection_mechanisms_excluded"])
        self.assertFalse(boundary["V22_G1_closed"])
        self.assertFalse(boundary["V22_G2_closed"])

    def test_rendered_outputs_are_current(self) -> None:
        self.assertEqual(json.loads(nogo.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(nogo.OUT_MD.read_text(encoding="utf-8"), nogo.markdown(self.report))

    def test_core_hash_covers_resolution(self) -> None:
        changed = copy.deepcopy(self.report)
        changed["resolution"]["ordinary_Abelian_shaping_charge_patch_exists"] = True
        self.assertNotEqual(nogo.canonical_sha(self.report), nogo.canonical_sha(changed))


if __name__ == "__main__":
    unittest.main()
