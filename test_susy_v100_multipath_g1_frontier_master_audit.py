"""Immutable history and explicit non-closure checks for the V100 master."""
import copy
import json
import unittest
from unittest.mock import patch

import susy_v100_multipath_g1_frontier_master_audit as audit


class TestV100Master(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()
        cls.card = cls.report["consolidated_theory_card"]
        cls.previous = audit.load_bound(audit.V99_PATH, audit.EXPECTED_CORES["v99_master"])
        cls.route = audit.load_bound(audit.V100_PATH, audit.EXPECTED_CORES["v100_route"])

    def test_canonical(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))

    def test_reconstruction(self):
        audit.validate_report(self.report)

    def test_all_27_historical_routes_preserved(self):
        self.assertEqual(self.report["route_matrix"][:-1], self.previous["route_matrix"])
        self.assertEqual(self.report["lineage"]["parent_route_matrix_sha256"], audit.canonical_sha(self.previous["route_matrix"]))

    def test_B100_is_28th_route(self):
        self.assertEqual(len(self.report["route_matrix"]), 28)
        row = self.report["route_matrix"][-1]
        self.assertEqual((row["ordinal"], row["route_id"]), (28, "B100"))
        self.assertFalse(row["accepted"])

    def test_zero_accepted_extensions(self):
        self.assertEqual(self.card["accepted_extension_count"], 0)
        self.assertFalse(any(row["accepted"] for row in self.report["route_matrix"]))

    def test_all_bound_helpers_embedded_exactly(self):
        for key in audit.HELPER_KEYS:
            self.assertEqual(self.card[key], self.route[key])
            self.assertEqual(self.card["bound_helper_core_hashes"][key], self.route[key]["core_sha256"])

    def test_exact_response_levels_kept_distinct(self):
        self.assertEqual(self.card["modified_equivariant_cover"]["minimal_combined_operator_cover"]["minimum_simultaneous_operator_cover_degree"], 4)
        self.assertEqual(self.card["correlated_quotient_period"]["exact_quantization"]["minimum_positive_stack"], 8)

    def test_response_not_single_target_repair(self):
        self.assertFalse(self.card["correlated_quotient_period"]["terminal_decision"]["single_local_P_over4_repair_accepted"])
        self.assertFalse(self.card["physical_background_category_identified"])

    def test_changed_cover_not_installed(self):
        row = self.card["modified_equivariant_cover"]["pulled_back_square_space_group"]
        self.assertFalse(row["space_group_lift_installed_in_frozen_theory"])
        self.assertFalse(row["orbifold_Dirac_domain_or_twisted_sectors_constructed"])

    def test_spectator_obstruction_and_not_global_no_go(self):
        row = self.card["spectator_GS_obstruction"]["independent_W_GS_obstruction"]
        self.assertTrue(row["all_regular_independent_W_GS_trivializations_rejected_in_stated_ansatz"])
        self.assertFalse(row["global_W_tHooft_anomaly_alone_is_quantum_inconsistency"])
        self.assertEqual(row["strict_budget_gap"], 1223)

    def test_gauge_only_cost_not_hidden(self):
        row = self.card["spectator_GS_obstruction"]
        self.assertEqual(row["gauge_only_regular_replacement_search"]["minimum_N"], 40)
        cost = row["minimum_scout_actual_projector_cost"]
        self.assertFalse(cost["old_Phi_driven_mass_module_preserved"])
        self.assertEqual(cost["conditional_total_free_chiral_count"], 27)

    def test_natural_normal_pair_preserved_exactly(self):
        self.assertEqual(self.card["preserved_natural_Spin_c_normal_pair"], self.previous["consolidated_theory_card"]["normal_pair"])

    def test_rank_torsion_and_conditional_targets_preserved(self):
        for key in ("actual_original_MW_torsion_order", "actual_original_MW_free_rank_bounds", "conditional_unit_charge_section_height_S_F", "conditional_doubled_charge_section_height_S_F"):
            self.assertEqual(self.card[key], self.previous["consolidated_theory_card"][key])
        self.assertIsNone(self.card["actual_original_MW_free_rank"])
        self.assertFalse(self.card["actual_original_nonzero_section_constructed"])

    def test_every_scope_decision_copied(self):
        for key, route_key in (("strict_master_decision", "terminal_decision"), ("supersession_ledger", "supersession_boundary"),
                               ("cross_sector_scope_checks", "cross_sector_scope_checks"), ("gate_ledger", "gate_ledger"),
                               ("next_required_action", "next_required_action"), ("primary_sources", "primary_sources")):
            self.assertEqual(self.report[key], self.route[route_key])

    def test_branch_gates_open_and_V21_untouched(self):
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

    def test_source_and_test_pins(self):
        self.assertEqual(self.report["artifact_hashes"]["generator_sha256"], audit.file_sha(audit.ROOT/(audit.__name__+".py")))
        self.assertEqual(self.report["artifact_hashes"]["test_sha256"], audit.file_sha(audit.TEST_PATH))

    def test_fresh_source_change_rejected(self):
        with patch.object(audit, "file_sha", return_value="0"*64):
            with self.assertRaises(RuntimeError):
                audit.build_report()

    def test_resealed_history_change_rejected(self):
        report = copy.deepcopy(self.report)
        report["route_matrix"][0]["accepted"] = True
        report["core_sha256"] = audit.canonical_sha(report)
        with self.assertRaises(RuntimeError):
            audit.validate_report(report)

    def test_resealed_completion_rejected(self):
        report = copy.deepcopy(self.report)
        report["strict_master_decision"]["theory_complete"] = True
        report["core_sha256"] = audit.canonical_sha(report)
        with self.assertRaises(RuntimeError):
            audit.validate_report(report)

    def test_generated_artifacts_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"), audit.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
