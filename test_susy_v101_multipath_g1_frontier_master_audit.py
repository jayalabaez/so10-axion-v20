"""Immutable history, evidence boundaries and artifact checks for V101 master."""
import copy
import json
import unittest
from unittest.mock import patch

import susy_v101_multipath_g1_frontier_master_audit as audit


class TestV101Master(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()
        cls.card = cls.report["consolidated_theory_card"]
        cls.previous = audit.load_bound(audit.V100_PATH, audit.EXPECTED_CORES["v100_master"])
        cls.route = audit.load_bound(audit.V101_PATH, audit.EXPECTED_CORES["v101_route"])

    def test_canonical(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))

    def test_reconstruction(self):
        audit.validate_report(self.report)

    def test_all28_historical_routes_preserved(self):
        self.assertEqual(self.report["route_matrix"][:-1], self.previous["route_matrix"])
        self.assertEqual(self.report["lineage"]["parent_route_matrix_sha256"], audit.canonical_sha(self.previous["route_matrix"]))

    def test_B101_is_29th_route(self):
        self.assertEqual(len(self.report["route_matrix"]), 29)
        row = self.report["route_matrix"][-1]
        self.assertEqual((row["ordinal"], row["route_id"]), (29, "B101"))
        self.assertFalse(row["accepted"])

    def test_zero_accepted_extensions(self):
        self.assertEqual(self.card["accepted_extension_count"], 0)
        self.assertFalse(any(row["accepted"] for row in self.report["route_matrix"]))

    def test_helpers_embedded_with_exact_cores(self):
        for key in audit.HELPER_KEYS:
            self.assertEqual(self.card[key], self.route[key])
            self.assertEqual(self.card["bound_helper_core_hashes"][key], self.route[key]["core_sha256"])

    def test_exact_levels_not_interpreted_as_particles(self):
        q = self.card["intermediate_cover_quantization"]
        self.assertEqual([r["minimum_positive_integer_stack"] for r in q["classification"]], [8, 2, 4, 8, 1])
        self.assertFalse(q["response_scope"]["eightfold_response_requires_new_particles_or_R_doublet_in_spectrum"])

    def test_exhaustive_fixed_action_obstruction(self):
        f = self.card["frozen_space_group_cover_obstruction"]["exact_obstruction_theorem"]
        self.assertEqual(f["number_of_central_generator_choices_checked"], 89)
        self.assertEqual(f["number_of_proper_covers_admitting_frozen_representation"], 0)

    def test_changed_domain_not_adopted(self):
        f = self.card["frozen_space_group_cover_obstruction"]["explicit_changed_spatial_domains"]
        self.assertFalse(f["changed_compactification_or_subgroup_adopted"])
        self.assertFalse(f["new_projectors_twisted_sectors_or_spectrum_computed"])

    def test_Higgs_compensation_not_full_physical_background(self):
        h = self.card["Higgs_background_restriction"]["CP3_selected_mass_compensated_cocharacter"]
        self.assertTrue(h["constant_V93_lambda_kappa_covariant_under_this_Cartan"])
        self.assertFalse(h["actual_physical_background_admissibility_proved"])
        self.assertFalse(self.card["physical_background_category_identified"])

    def test_one_chart_excluded_not_all_sections(self):
        self.assertTrue(self.card["exceptional_all_zero_linear_pivot_chart_excluded"])
        self.assertEqual(self.card["nonzero_linear_pivot_charts_still_open"], [1, 2, 3])
        self.assertFalse(self.card["all_original_cubic_sections_excluded"])
        self.assertFalse(self.card["all_original_rational_sections_excluded"])

    def test_empty_conditional_antecedent_not_actual_lattice(self):
        self.assertFalse(self.card["historical_conditional_exceptional_pair_has_instance_on_original_member"])
        self.assertFalse(self.card["actual_original_nonzero_section_constructed"])

    def test_natural_normal_pair_preserved(self):
        self.assertEqual(self.card["preserved_natural_Spin_c_normal_pair"], self.previous["consolidated_theory_card"]["preserved_natural_Spin_c_normal_pair"])

    def test_original_rank_torsion_and_targets_preserved(self):
        for key in ("actual_original_MW_torsion_order", "actual_original_MW_free_rank_bounds", "conditional_unit_charge_section_height_S_F", "conditional_doubled_charge_section_height_S_F"):
            self.assertEqual(self.card[key], self.previous["consolidated_theory_card"][key])
        self.assertIsNone(self.card["actual_original_MW_free_rank"])

    def test_route_scope_copied_exactly(self):
        for key, source in (("strict_master_decision", "terminal_decision"), ("supersession_ledger", "supersession_boundary"),
                            ("cross_sector_scope_checks", "cross_sector_scope_checks"), ("gate_ledger", "gate_ledger"),
                            ("next_required_action", "next_required_action"), ("primary_sources", "primary_sources")):
            self.assertEqual(self.report[key], self.route[source])

    def test_all_branch_gates_open_and_V21_unchanged(self):
        self.assertEqual(self.report["strict_master_decision"]["closed_gates"], [])
        self.assertEqual(len(self.report["gate_ledger"]), 8)
        self.assertTrue(all(v.startswith("OPEN:") for v in self.report["gate_ledger"].values()))
        self.assertTrue(self.report["lineage"]["canonical_V21_gate_scope_unchanged"])

    def test_no_complete_or_empirical_claim(self):
        self.assertFalse(self.report["strict_master_decision"]["theory_complete"])
        for key in ("experimental_confirmation", "full_quantum_anomaly_cancelled", "same_action_spectrum_and_geometry_realized", "soft_spectrum_unification_cosmology_complete"):
            self.assertFalse(self.card[key])

    def test_next_obligation(self):
        self.assertEqual(self.report["next_required_action"]["id"], audit.NEXT_ID)

    def test_fresh_source_and_test_pins(self):
        self.assertEqual(self.report["artifact_hashes"]["generator_sha256"], audit.file_sha(audit.ROOT/(audit.__name__+".py")))
        self.assertEqual(self.report["artifact_hashes"]["test_sha256"], audit.file_sha(audit.TEST_PATH))

    def test_fresh_source_change_rejected(self):
        with patch.object(audit, "file_sha", return_value="0"*64):
            with self.assertRaises(RuntimeError):
                audit.build_report()

    def test_resealed_history_and_completion_changes_rejected(self):
        for path in ("history", "completion"):
            bad = copy.deepcopy(self.report)
            if path == "history":
                bad["route_matrix"][0]["accepted"] = True
            else:
                bad["strict_master_decision"]["theory_complete"] = True
            bad["core_sha256"] = audit.canonical_sha(bad)
            with self.assertRaises(RuntimeError):
                audit.validate_report(bad)

    def test_generated_artifacts_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"), audit.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
