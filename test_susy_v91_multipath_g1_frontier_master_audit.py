import copy
import json
import unittest

import susy_v91_multipath_g1_frontier_master_audit as audit


class TestV91Master(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()

    def test_parent_pins(self):
        self.assertEqual(self.report["input_core_hashes"],audit.EXPECTED_CORES)

    def test_inherited_routes_unchanged(self):
        previous = audit.load_bound(audit.V90_PATH,audit.EXPECTED_CORES["v90_master"])
        self.assertEqual(self.report["route_matrix"][:-1],previous["route_matrix"])
        self.assertEqual(self.report["lineage"]["parent_route_matrix_sha256"],audit.canonical_sha(previous["route_matrix"]))

    def test_B91_appended_unaccepted(self):
        rows = self.report["route_matrix"]
        self.assertEqual(len(rows),19)
        self.assertEqual(rows[-1]["route_id"],"B91")
        self.assertEqual([r["ordinal"] for r in rows],list(range(1,20)))
        self.assertFalse(rows[-1]["accepted"])
        self.assertFalse(rows[-1]["same_action_microscopic_completion"])

    def test_card_has_correct_new_scout(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["new_singlet_counts_q0_q2_q4_q6_q8"],[144,3,19,11,90])
        self.assertEqual(card["new_abelian_coefficient"],["-472","-148"])
        self.assertEqual(card["smooth_bulk_D2_D4"],[7440,419136])
        self.assertTrue(card["full_cocharacter_integrality"])

    def test_partial_results_do_not_accept_theory(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["accepted_extension_count"],0)
        for key in ("quantum_anomaly_cancelled","primitive_C8_preserved",
                    "geometric_scout_smoothness_certified","soft_spectrum_unification_cosmology_complete"):
            self.assertFalse(card[key])

    def test_acceptance_criteria_distinguish_old_failure_and_new_scout(self):
        rows = {r["id"]:r["status"] for r in self.report["acceptance_criteria"]}
        self.assertEqual(rows["A4"],"REJECTED_ORDER_TWO_SOURCE_QUANTIZATION")
        self.assertEqual(rows["A6"],"PASS_EXACT")
        self.assertEqual(rows["A9"],"OPEN_UNCOMPUTED")
        self.assertEqual(rows["A13"],"OPEN_UNCOMPUTED")

    def test_no_historical_geometry_retraction_or_false_transfer(self):
        row = self.report["supersession_ledger"]
        self.assertFalse(row["old_V90_geometry_certificate_retracted"])
        self.assertFalse(row["new_coefficients_inherit_V90_compact_smoothness"])
        self.assertFalse(row["full_complex_no_deck_root_theorem_claimed"])

    def test_scope_and_gate_boundary(self):
        self.assertTrue(self.report["lineage"]["canonical_V21_gate_scope_unchanged"])
        self.assertEqual(self.report["strict_master_decision"]["closed_gates"],[])
        self.assertTrue(all(x.startswith("OPEN:") for x in self.report["gate_ledger"].values()))

    def test_next_action_F92(self):
        self.assertEqual(self.report["next_required_action"]["id"],"F92_QUANTIZED_SCOUT_PROJECTORS_RELATIVE_WCS_AND_DECK_ROOT")
        self.assertFalse(self.report["next_required_action"]["accepted"])

    def test_rehashed_false_promotions_rejected(self):
        for key in ("theory_complete","new_scout_accepted_as_same_action_parent",
                    "full_finite_or_relative_anomaly_cancelled",
                    "new_deck_root_scout_compact_smoothness_certified"):
            changed = copy.deepcopy(self.report)
            changed["strict_master_decision"][key] = True
            changed["core_sha256"] = audit.canonical_sha(changed)
            with self.assertRaises(RuntimeError):
                audit.validate_report(changed)

    def test_route_lineage_mutation_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["route_matrix"][0]["name"] = "forged"
        changed["core_sha256"] = audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_report(changed)

    def test_artifacts_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")),self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"),audit.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
