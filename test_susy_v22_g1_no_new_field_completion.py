from __future__ import annotations

import copy
import json
import unittest

import susy_v22_g1_no_new_field_completion as completion


class SusyV22G1NoNewFieldCompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = completion.build_report()

    def test_exact_minimum_and_selector(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["counts"]["intended_sectors"], 29)
        self.assertEqual(self.report["counts"]["unavoidable_extra_sectors"], 79)
        self.assertEqual(self.report["counts"]["minimum_selected_sectors"], 108)
        self.assertEqual(self.report["counts"]["rejected_sectors"], 937)
        self.assertEqual(self.report["counts"]["intended_flavour_components"], 71)
        self.assertEqual(self.report["counts"]["unavoidable_extra_flavour_components"], 194)
        self.assertTrue(self.report["checks"]["Z7R_times_Z2S_selects_exactly_the_Smith_zero_class"])

    def test_discrete_anomaly_arithmetic(self) -> None:
        self.assertEqual(self.report["shaping_symmetry"]["Z7R_anomalies"]["mod_7"], {
            "SO10_squared_Z7R": 0,
            "U1X_squared_Z7R": 0,
            "U1X_Z7R_squared": 0,
            "gravity_squared_Z7R": 0,
        })
        self.assertTrue(self.report["checks"]["Z2S_has_even_gravity_SO10_and_X2_ledgers"])
        self.assertTrue(self.report["checks"]["Z2S_U1X_Z2_squared_vanishes_exactly"])
        self.assertTrue(self.report["checks"]["Z28R_is_the_CRT_combination_of_source_Z4R_and_new_Z7R"])
        self.assertTrue(self.report["checks"]["all_Z28R_mixed_anomalies_vanish_under_eta_14_convention"])
        self.assertTrue(self.report["checks"]["required_VEVs_leave_exactly_a_Z4R_subgroup_of_Z28R"])

    def test_generic_driver_grid_is_complete_but_old_vacuum_is_not_inherited(self) -> None:
        grid = self.report["driver_constraint_matrix"]
        self.assertEqual(grid["shape"], [5, 5])
        self.assertTrue(grid["all_entries_selected"])
        self.assertTrue(grid["generic_full_rank_point_exists"])
        self.assertFalse(self.report["physics_effect"]["original_diagonal_F_flat_solution_inherited"])

    def test_candidate_is_not_silently_activated(self) -> None:
        verdict = self.report["completion_verdict"]
        boundary = self.report["claim_boundary"]
        self.assertTrue(verdict["classical_degree_le_4_sector_completion_exists_without_new_fields"])
        self.assertFalse(verdict["accept_79_new_operators_as_active_V22"])
        self.assertFalse(verdict["source_land_as_active_V22"])
        self.assertFalse(boundary["full_V22_G1_closed"])

    def test_outputs_are_frozen(self) -> None:
        self.assertEqual(json.loads(completion.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(completion.OUT_MD.read_text(encoding="utf-8"), completion.markdown(self.report))

    def test_core_hash_covers_activation_boundary(self) -> None:
        changed = copy.deepcopy(self.report)
        changed["completion_verdict"]["source_land_as_active_V22"] = True
        self.assertNotEqual(completion.canonical_sha(self.report), completion.canonical_sha(changed))


if __name__ == "__main__":
    unittest.main()
