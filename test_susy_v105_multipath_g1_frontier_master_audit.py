"""Frozen history, explicit retraction and fail-closed V105 master checks."""
import copy
import json
import unittest
from unittest.mock import patch

import susy_v105_multipath_g1_frontier_master_audit as audit


class TestV105Master(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()
        cls.card = cls.report["consolidated_theory_card"]
        cls.previous = audit.load_bound(audit.PREVIOUS_PATH, audit.EXPECTED_CORES["v104_master"])
        cls.route = audit.load_bound(audit.ROUTE_PATH, audit.EXPECTED_CORES["v105_route"])

    def test_canonical_and_fresh(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        audit.validate_report(self.report)

    def test_route_and_helper_are_identical(self):
        self.assertEqual(self.card["q2_repair_full_reduction"], self.route["q2_repair_full_reduction"])
        self.assertEqual(self.report["input_core_hashes"], audit.EXPECTED_CORES)
        self.assertEqual(self.card["q2_core_reduction"]["helper_core_sha256"], self.route["q2_repair_full_reduction"]["core_sha256"])

    def test_all_32_historical_rows_preserved_verbatim(self):
        self.assertEqual(self.report["route_matrix"][:-1], self.previous["route_matrix"])
        self.assertEqual(self.report["lineage"]["parent_route_matrix_sha256"], audit.canonical_sha(self.previous["route_matrix"]))
        self.assertEqual(self.card["historical_V104_card_sha256"], audit.canonical_sha(self.previous["consolidated_theory_card"]))

    def test_B105_is_unaccepted_ordinal33(self):
        self.assertEqual(len(self.report["route_matrix"]), 33)
        row = self.report["route_matrix"][-1]
        self.assertEqual((row["route_id"], row["ordinal"]), ("B105", 33))
        self.assertFalse(row["accepted"])
        self.assertFalse(any(r["accepted"] for r in self.report["route_matrix"]))

    def test_invalid_B104_claims_are_historical_not_active(self):
        old = self.card["historical_V104_q2_derived_claims"]
        self.assertFalse(old["active_evidence"])
        self.assertEqual(old["status"], "SUPERSEDED_SOURCE_CONVERSION_ERROR")
        self.assertEqual(old["snapshot"], self.previous["consolidated_theory_card"]["q2_core_reduction"])
        self.assertTrue(self.report["supersession_ledger"]["V104_corrupted_cores_and_28_97_91_witnesses_retracted_as_original_Q2_evidence"])

    def test_active_Q2_evidence_has_only_corrected_provenance(self):
        row = self.card["q2_core_reduction"]
        self.assertIn("V105", row["source"])
        self.assertEqual(row["corrected_determinants_mod101"], [81, 14, 16])
        self.assertTrue(row["all_five_residuals_reconstructed"])
        self.assertEqual(row["regular_reconstruction_charts"], 5)
        self.assertFalse(row["Q2_solved"])
        self.assertFalse(row["Q2_excluded"])

    def test_original_rank_targets_and_normal_pair_preserved(self):
        old = self.previous["consolidated_theory_card"]
        for key in ("actual_original_MW_free_rank_bounds", "actual_original_MW_torsion_order", "conditional_unit_charge_section_height_S_F", "conditional_doubled_charge_section_height_S_F", "preserved_natural_Spin_c_normal_pair", "normal_frame_tensor_representations", "locked_parity_quantum_boundary", "target_section_jet_reduction"):
            self.assertEqual(self.card[key], old[key])
        self.assertIsNone(self.card["actual_original_MW_free_rank"])

    def test_all_gates_and_canonical_scope_preserved(self):
        self.assertEqual(set(self.report["gate_ledger"]), {"G"+str(i) for i in range(1, 9)})
        self.assertTrue(all(v.startswith("OPEN:") for v in self.report["gate_ledger"].values()))
        self.assertTrue(self.report["lineage"]["canonical_V21_gate_scope_unchanged"])
        self.assertEqual(self.report["strict_master_decision"]["closed_gates"], [])

    def test_all_current_source_pins(self):
        self.assertEqual(self.report["artifact_hashes"]["generator_sha256"], audit.file_sha(audit.ROOT/(audit.__name__+".py")))
        self.assertEqual(self.report["artifact_hashes"]["test_sha256"], audit.file_sha(audit.TEST_PATH))

    def test_all_fifteen_conditions_and_exceptional_square_retained(self):
        helper = self.card["q2_repair_full_reduction"]
        self.assertEqual(len(helper["all_five_residual_elimination"]["necessary_core_rows"]), 15)
        theorem = helper["common_root_reconstruction_theorem"]
        self.assertFalse(theorem["all_fifteen_conditions_alone_sufficient_over_C_X_on_zero_slope_chart"])
        self.assertFalse(theorem["zero_slope_and_repeated_roots_discarded"])

    def test_no_complete_theory_section_or_empirical_claim(self):
        self.assertEqual(self.card["accepted_extension_count"], 0)
        for key in ("all_original_quartic_sections_excluded", "all_original_rational_sections_excluded", "actual_original_nonzero_section_constructed", "actual_target_sections_constructed", "experimental_confirmation"):
            self.assertFalse(self.card[key])
        self.assertFalse(self.report["strict_master_decision"]["theory_complete"])

    def test_route_decisions_sources_and_retraction_copied_exactly(self):
        for target, source in (("strict_master_decision", "terminal_decision"), ("supersession_ledger", "supersession_boundary"), ("cross_sector_scope_checks", "cross_sector_scope_checks"), ("primary_sources", "primary_sources"), ("gate_ledger", "gate_ledger")):
            self.assertEqual(self.report[target], self.route[source])

    def test_warm_build_rechecks_sources(self):
        real = audit.file_sha
        for name in ("susy_v104_multipath_g1_frontier_master_audit.py", "test_susy_v105_q2_repair_full_reduction_audit.py", "v105_q2_repair_and_full_reduction_audit.py", "test_v105_q2_repair_and_full_reduction_audit.py", "v105_q2_index_correction_audit.py", "test_v105_q2_index_correction_audit.py", "SUSY_V105_Q2_INDEX_CORRECTION_AUDIT.md"):
            with patch.object(audit, "file_sha", side_effect=lambda p: "0"*64 if p.name == name else real(p)):
                with self.assertRaises(RuntimeError):
                    audit.build_report()

    def test_resealed_history_retraction_and_rank_promotions_rejected(self):
        for which in ("history", "retraction", "rank", "point"):
            bad = copy.deepcopy(self.report)
            if which == "history":
                bad["route_matrix"][0]["accepted"] = True
            elif which == "retraction":
                bad["consolidated_theory_card"]["historical_V104_q2_derived_claims"]["active_evidence"] = True
            elif which == "rank":
                bad["consolidated_theory_card"]["actual_original_MW_free_rank"] = 0
            else:
                bad["consolidated_theory_card"]["actual_original_nonzero_section_constructed"] = True
            bad["core_sha256"] = audit.canonical_sha(bad)
            with self.assertRaises(RuntimeError):
                audit.validate_report(bad)

    def test_generated_json_and_readable_report_match(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")), self.report)
        text = audit.render_markdown(self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"), text)
        for phrase in ("All 32 historical route records", "not valid evidence", "81,14,16", "All G1-G8 remain OPEN", "does not exclude"):
            self.assertIn(phrase, text)

    def test_next_obligation_retains_regular_and_zero_slope_cases(self):
        self.assertEqual(self.report["next_required_action"], self.route["next_required_action"])
        self.assertEqual(self.report["next_required_action"]["id"], audit.NEXT_ID)


if __name__ == "__main__":
    unittest.main()
