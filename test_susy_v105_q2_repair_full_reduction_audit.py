"""V105 retraction, source lineage and nonpromotion integration tests."""
import copy
import json
import unittest
from unittest.mock import patch

import susy_v105_q2_repair_full_reduction_audit as audit


class TestV105Route(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()
        cls.inputs = audit.helper.load_inputs()

    def test_canonical_and_fresh(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        audit.validate_report(self.report)

    def test_identical_helper_and_parent_binding(self):
        self.assertEqual(self.report["q2_repair_full_reduction"], audit.helper.build_certificate())
        self.assertEqual(self.report["input_core_hashes"], {k: v[1] for k, v in audit.PARENTS.items()})

    def test_all_source_and_test_pins_current(self):
        hashes = self.report["artifact_hashes"]
        self.assertEqual(hashes["generator_sha256"], audit.file_sha(audit.ROOT/(audit.__name__+".py")))
        self.assertEqual(hashes["test_sha256"], audit.file_sha(audit.TEST_PATH))
        for name, value in hashes.items():
            if name.endswith(".py"):
                self.assertEqual(value, audit.file_sha(audit.ROOT/name))

    def test_retraction_is_explicit_and_scoped(self):
        row = self.report["supersession_boundary"]
        self.assertTrue(row["V104_corrupted_cores_and_28_97_91_witnesses_retracted_as_original_Q2_evidence"])
        self.assertFalse(row["V104_hash_pinned_files_and_route_row_rewritten"])
        self.assertFalse(row["V104_A2_identity_and_h_independent_discriminant_retracted"])
        self.assertTrue(row["confinement_reestablished_using_corrected_V105_data"])

    def test_corrected_witnesses_are_not_the_old_snapshot_values(self):
        row = self.report["q2_repair_full_reduction"]["retraction_and_replacement"]
        self.assertEqual(row["corrected_witnesses_mod101"], [81, 14, 16])
        self.assertEqual(row["corrected_fixed_Sylvester_size"], 7)
        self.assertFalse(row["full_Q2_exclusion_follows_from_nonzero_resultant"])

    def test_all_residuals_and_zero_pivot_boundary_present(self):
        h = self.report["q2_repair_full_reduction"]
        self.assertEqual(len(h["corrected_reduction"]["rows"]), 5)
        self.assertEqual(len(h["all_five_residual_elimination"]["necessary_core_rows"]), 15)
        self.assertEqual(len(h["common_root_reconstruction_theorem"]["disjoint_regular_charts"]), 5)
        self.assertFalse(h["common_root_reconstruction_theorem"]["zero_slope_and_repeated_roots_discarded"])

    def test_old_rank_torsion_curve_and_physics_gates_preserved(self):
        h = self.report["q2_repair_full_reduction"]
        old = self.inputs["v103_route"]["original_quartic_sections"]
        self.assertEqual(h["preserved_frontier"], old["preserved_frontier"])
        for i in range(1, 8):
            self.assertEqual(self.report["gate_ledger"]["G"+str(i)], self.inputs["v104_route"]["gate_ledger"]["G"+str(i)])

    def test_no_gate_or_physical_parent_closed(self):
        self.assertEqual(set(self.report["gate_ledger"]), {"G"+str(i) for i in range(1, 9)})
        self.assertTrue(all(v.startswith("OPEN:") for v in self.report["gate_ledger"].values()))
        row = self.report["terminal_decision"]
        self.assertTrue(row["bounded_F105_repair_and_full_Q2_reduction_completed"])
        self.assertEqual(row["closed_gates"], [])
        for key in ("Q2_solved", "Q2_excluded", "Q1_or_target_systems_solved", "covariant_action_repair_constructed", "same_action_microscopic_parent_accepted", "theory_complete"):
            self.assertFalse(row[key])

    def test_next_obligation_is_concrete_and_retains_physics(self):
        row = self.report["next_required_action"]
        self.assertEqual(row["id"], audit.NEXT_ID)
        self.assertIn("q=-mu_i/ell_i", row["primary"])
        self.assertIn("Delta-square", row["primary"])
        self.assertIn("normal-covariant", row["parallel"])
        self.assertIn("not a constructed physical repair", row["parallel"])

    def test_crosscheck_rejects_restored_false_evidence(self):
        bad = copy.deepcopy(self.report["q2_repair_full_reduction"])
        bad["retraction_and_replacement"]["V104_derived_cores_and_28_97_91_witnesses_accepted_as_original_Q2_evidence"] = True
        with self.assertRaises(RuntimeError):
            audit.crosscheck(self.inputs, bad)

    def test_crosscheck_rejects_lost_degeneracy_or_promotion(self):
        for section, key in (("common_root_reconstruction_theorem", "zero_slope_and_repeated_roots_discarded"), ("terminal_decision", "Q2_excluded")):
            bad = copy.deepcopy(self.report["q2_repair_full_reduction"])
            bad[section][key] = True
            with self.assertRaises(RuntimeError):
                audit.crosscheck(self.inputs, bad)

    def test_warm_build_rechecks_historical_sources(self):
        with patch.object(audit.helper, "file_sha", return_value="0"*64):
            with self.assertRaises(RuntimeError):
                audit.build_report()

    def test_resealed_false_completion_rejected(self):
        bad = copy.deepcopy(self.report)
        bad["terminal_decision"]["theory_complete"] = True
        bad["core_sha256"] = audit.canonical_sha(bad)
        with self.assertRaises(RuntimeError):
            audit.validate_report(bad)

    def test_generated_json_and_readable_report_match(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")), self.report)
        rendered = audit.render_markdown(self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"), rendered)
        for phrase in ("h-1 to zero", "retracted as evidence", "81,14,16", "all five remaining", "All G1-G8 remain OPEN"):
            self.assertIn(phrase.lower(), rendered.lower())


if __name__ == "__main__":
    unittest.main()
