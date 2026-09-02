import copy
import json
import unittest

import susy_v92_multipath_g1_frontier_master_audit as audit


class TestV92Master(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()

    def test_parent_pins(self):
        self.assertEqual(self.report["input_core_hashes"],audit.EXPECTED_CORES)

    def test_inherited_routes_unchanged(self):
        previous = audit.load_bound(audit.V91_PATH,audit.EXPECTED_CORES["v91_master"])
        self.assertEqual(self.report["route_matrix"][:-1],previous["route_matrix"])
        self.assertEqual(self.report["lineage"]["parent_route_matrix_sha256"],audit.canonical_sha(previous["route_matrix"]))

    def test_B92_appended_unaccepted(self):
        rows = self.report["route_matrix"]
        self.assertEqual(len(rows),20)
        self.assertEqual(rows[-1]["route_id"],"B92")
        self.assertEqual([r["ordinal"] for r in rows],list(range(1,21)))
        self.assertFalse(rows[-1]["accepted"])
        self.assertFalse(rows[-1]["same_action_microscopic_completion"])

    def test_card_projectors_and_mass_are_separate(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["bulk_singlet_counts_q0_q2_q4_q6_q8"],[144,3,19,11,90])
        self.assertEqual(card["selected_constant_chiral_modes"],11)
        self.assertEqual(card["conditionally_massive_extra_modes"],9)
        self.assertFalse(card["full_R_mass_module_embedding_certified"])

    def test_lens_scope_and_geometry_form_character(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["ordinary_closed_lens_tests_passed"],4)
        self.assertEqual(card["torsion_labels_passing_this_screen"],8)
        self.assertTrue(card["compact_geometric_smoothness_certified"])
        self.assertTrue(card["global_order_four_deck_root_certified"])
        self.assertEqual(card["holomorphic_volume_form_character"],"I")

    def test_hodge_target_not_result(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["necessary_hodge_target"],{"h11":9,"h21":143,"Euler":-268})
        self.assertFalse(card["actual_geometric_hodge_numbers_computed"])
        self.assertFalse(card["same_action_spectrum_and_geometry_realized"])

    def test_partial_results_do_not_accept_theory(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["accepted_extension_count"],0)
        for key in ("quantum_anomaly_cancelled","primitive_C8_preserved_by_retained_vacuum",
                    "soft_spectrum_unification_cosmology_complete"):
            self.assertFalse(card[key])

    def test_acceptance_criteria_keep_open_obligations(self):
        rows = {r["id"]:r["status"] for r in self.report["acceptance_criteria"]}
        self.assertEqual(rows["A4"],"PASS_LOCAL_ANSATZ_WITH_NEW_R_ASSIGNMENT")
        self.assertEqual(rows["A8"],"OPEN_UNCOMPUTED")
        self.assertEqual(rows["A11"],"REJECTED_OMEGA_CHARACTER_I")
        self.assertEqual(rows["A14"],"OPEN_UNCOMPUTED")

    def test_scope_gates_and_next_F93(self):
        self.assertTrue(self.report["lineage"]["canonical_V21_gate_scope_unchanged"])
        self.assertEqual(self.report["strict_master_decision"]["closed_gates"],[])
        self.assertEqual(set(self.report["gate_ledger"]),{"G"+str(i) for i in range(1,9)})
        self.assertTrue(all(x.startswith("OPEN:") for x in self.report["gate_ledger"].values()))
        self.assertEqual(self.report["next_required_action"]["id"],"F93_LOCALIZED_ANOMALY_GAMMAHAT_AND_SPECTRUM_GLUE")
        self.assertFalse(self.report["next_required_action"]["accepted"])

    def test_rehashed_false_promotions_rejected(self):
        for key in ("theory_complete","same_action_microscopic_parent_accepted",
                    "full_relative_anomaly_cancelled","standalone_volume_preserving_CY_quotient",
                    "all_F92_obligations_fully_completed"):
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
