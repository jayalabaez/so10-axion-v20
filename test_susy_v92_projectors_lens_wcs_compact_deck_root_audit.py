import copy
import json
import unittest

import susy_v92_projectors_lens_wcs_compact_deck_root_audit as audit


class TestV92IntegratedRoute(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()

    def test_canonical_lineage(self):
        self.assertEqual(self.report["input_core_hashes"],{key:core for key,(_,core) in audit.PARENTS.items()})
        self.assertEqual(self.report["core_sha256"],audit.canonical_sha(self.report))

    def test_projector_mass_module_bindings(self):
        p = self.report["smooth_singlet_projectors"]
        m = self.report["conditional_extra_singlet_mass_module"]
        self.assertEqual(m["selected_projector_core_sha256"],p["core_sha256"])
        self.assertEqual(p["eleven_mode_normal_aligned_witness"]["constant_N1_chiral_count"],11)
        self.assertEqual(m["calculation"]["rank_for_v_nonzero"],9)

    def test_lens_screen_not_bare_fermion_veto(self):
        e = self.report["ordinary_closed_lens_anomaly_screen"]
        self.assertEqual([x["bare_fermion_ratio"] for x in e["lens_fermion_tests"]],["+1","+1","-1","-1"])
        s = e["torsion_refinement_lens_screen"]
        self.assertEqual(s["labels_passing_this_screen"],8)
        self.assertTrue(s["bare_phases_derived_from_the_representation_census"])
        self.assertTrue(s["V91_selected_label"]["passes_both_lens_spin_lifts_in_both_embeddings"])

    def test_compact_geometry_and_volume_character(self):
        g = self.report["compact_deck_root_geometry"]
        self.assertTrue(g["proper_specialization"]["resolved_compact_member_geometrically_smooth_over_Q"])
        lift = g["integral_projective_model_and_lift"]["order_four_lift"]
        self.assertTrue(lift["global_regular_lift_exists"])
        self.assertEqual(lift["holomorphic_three_form_character"],"I")
        self.assertFalse(lift["standalone_volume_preserving_CY_quotient"])

    def test_hodge_target_not_geometric_realization(self):
        row = self.report["conditional_spectrum_geometry_target"]
        self.assertEqual(row["necessary_hodge_tuple"],{"h11":9,"h21":143,"Euler":-268})
        self.assertFalse(row["V91_symmetry_member_realizes_scout_spectrum"])

    def test_all_helper_source_and_test_hashes_bound(self):
        hashes = self.report["artifact_hashes"]
        for stem in audit.HELPERS:
            for name in (stem+".py","test_"+stem+".py"):
                self.assertEqual(hashes[name],audit.file_sha(audit.ROOT/name))

    def test_no_mixed_action_promotion(self):
        row = self.report["integration_boundary"]
        for key in ("mass_module_R_assignment_and_global_wall_embedding_certified",
                    "four_closed_lens_ratios_equal_full_relative_Dai_Freed_functor",
                    "geometry_and_projectors_are_one_diagonal_orbibundle",
                    "compact_smoothness_proves_required_Mordell_Weil_rank_or_spectrum"):
            self.assertFalse(row[key])

    def test_all_gates_open_and_F93_selected(self):
        self.assertEqual(self.report["terminal_decision"]["closed_gates"],[])
        self.assertTrue(all(x.startswith("OPEN:") for x in self.report["gate_ledger"].values()))
        self.assertEqual(self.report["next_required_action"]["id"],audit.NEXT_ID)
        self.assertFalse(self.report["terminal_decision"]["all_F92_obligations_fully_completed"])

    def test_rehashed_false_promotions_rejected(self):
        for key in ("theory_complete","full_relative_anomaly_cancelled",
                    "same_action_microscopic_parent_accepted"):
            changed = copy.deepcopy(self.report)
            changed["terminal_decision"][key] = True
            changed["core_sha256"] = audit.canonical_sha(changed)
            with self.assertRaises(RuntimeError):
                audit.validate_report(changed)

    def test_rehashed_numeric_change_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["terminal_decision"]["torsion_labels_passing_this_screen"] = 16
        changed["core_sha256"] = audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_report(changed)

    def test_artifacts_match_generator(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")),self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"),audit.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
