import copy
import json
import unittest

import sympy as sp
import susy_v96_quantized_responses_and_section_frontier_audit as audit


class TestV96Route(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=audit.build_report()

    def test_parent_pins_and_core(self):
        self.assertEqual(self.report["core_sha256"],audit.canonical_sha(self.report))
        self.assertEqual(self.report["input_core_hashes"],{k:v[1] for k,v in audit.PARENTS.items()})

    def test_fresh_helper_reconstruction(self):
        keys=("normal_relative_CS","local_transport_quantization","defect_relative_invertible","original_section_frontier")
        for key,module in zip(keys,audit.MODULES):
            self.assertEqual(self.report[key],module.build_certificate())

    def test_source_and_test_hashes(self):
        hashes=self.report["artifact_hashes"]
        self.assertEqual(hashes["generator_sha256"],audit.file_sha(audit.ROOT/(audit.__name__+".py")))
        self.assertEqual(hashes["test_sha256"],audit.file_sha(audit.TEST_PATH))
        for name,digest in hashes.items():
            if name.endswith(".py"):
                self.assertEqual(digest,audit.file_sha(audit.ROOT/name))

    def test_two_field_repair_and_integer_CS(self):
        n=self.report["normal_relative_CS"]
        self.assertEqual(n["new_normal_repairs"][0]["normal_root_charges"],[-3,-3])
        self.assertEqual(n["new_normal_repairs"][0]["CS_cubic_integer_level"],10)
        self.assertTrue(n["product_category_quantized_CS_construction"]["a_global_topological_action_in_the_stated_product_category_is_defined"])
        self.assertFalse(n["product_category_quantized_CS_construction"]["full_relative_anomaly_trivialization_constructed"])

    def test_restricted_full_bordism_characters(self):
        d=self.report["defect_relative_invertible"]
        for group,count,order in (("C4",16,8),("C8",32,4)):
            self.assertEqual(d["complete_restricted_character_cancellation"][group]["class_count"],count)
            self.assertTrue(d["complete_restricted_character_cancellation"][group]["all_restricted_reduced_characters_cancel"])
            self.assertEqual(d["restricted_bordism_classification"][group]["bare_defect_exact_order"],order)

    def test_inverse_response_not_same_action_inflow(self):
        row=self.report["defect_relative_invertible"]["quantized_inverse_response"]
        self.assertEqual(row["CS_level_for_D"],3)
        self.assertEqual(row["ABK_level_mod8"],3)
        self.assertTrue(row["quantized_abstract_restricted_inverse_response_constructed"])
        self.assertFalse(row["actual_same_action_bulk_inflow_constructed"])

    def test_smooth_mass_has_forced_zeros_not_holomorphic(self):
        row=self.report["local_transport_quantization"]["smooth_equivariant_mass_intertwiner"]
        self.assertTrue(row["smooth_on_whole_cover"])
        self.assertEqual(row["cover_mass_zero_windings"],{"z00":1,"z11":1,"z10":-1,"z01":-1})
        self.assertFalse(row["nowhere_nonzero_profile"])
        self.assertFalse(row["holomorphic_superpotential_mass_profile"])
        self.assertFalse(row["projected_defect_zero_modes_and_their_Gammahat_representations_computed"])

    def test_virtual_normal_anomaly_retained(self):
        f,u=sp.symbols("f u")
        row=self.report["formal_combination_and_quotient_periods"]
        self.assertEqual(sp.sympify(row["integrated_virtual_normal_delta_I6"]),-2*f*u**2)

    def test_formal_f_zero_cancellation_at_all_physical_loci(self):
        f=sp.Symbol("f")
        for row in self.report["formal_combination_and_quotient_periods"]["rows"]:
            self.assertEqual(sp.expand(sp.sympify(row["remaining_I6"]).subs(f,0)),0)

    def test_integral_covering_flux_periods(self):
        rows=self.report["formal_combination_and_quotient_periods"]["rows"]
        self.assertEqual([r["integral_covering_flux_CP3_period"] for r in rows],["122","122","-11"])

    def test_new_quotient_mixed_gauge_periods(self):
        rows=self.report["formal_combination_and_quotient_periods"]["rows"]
        self.assertEqual([r["quotient_mixed_gauge_CP3_period"] for r in rows],["61/4","61/4","-1/2"])
        self.assertEqual([r["quotient_period_mod_one"] for r in rows],["1/4","1/4","1/2"])
        self.assertEqual(sum(sp.Rational(r["quotient_mixed_gauge_CP3_period"]) for r in rows),30)

    def test_J2_is_zero_on_quotient_witness(self):
        row=self.report["formal_combination_and_quotient_periods"]["quotient_period_witness"]
        self.assertEqual(row["J2_equals_index_of_D_period"],"0")
        self.assertFalse(row["pure_J2_transport_can_remove_these_fractions"])
        self.assertFalse(row["ordinary_local_Weyls_alone_can_remove_these_fractions"])
        self.assertFalse(row["test_is_a_full_Gammahat_orbifold_Dai_Freed_calculation"])

    def test_compact_C4_residuals_match_expanded(self):
        f,p,u=sp.symbols("f p u")
        e=sp.symbols("e1:6")
        for row in self.report["formal_combination_and_quotient_periods"]["rows"][:2]:
            t=sum(e) if row["stratum"]=="z00" else sum(e[:2])-sum(e[2:])
            expected=f*(sum(z*z for z in e)+4*f*t+126*f*f-p-2*u*t+39*f*u-23*u*u)
            self.assertEqual(sp.expand(sp.sympify(row["remaining_I6"])-expected),0)

    def test_original_rank_improves_without_exact_rank_claim(self):
        row=self.report["original_section_frontier"]["stronger_original_MW_rank_bound"]
        self.assertEqual([row["previous_original_rank_upper_bound"],row["original_rank_upper_bound"]],[12,11])
        self.assertFalse(row["generic_Picard_rank_equals19_claimed"])
        self.assertFalse(row["nonzero_original_section_constructed"])

    def test_section_exclusions_are_bounded(self):
        row=self.report["original_section_frontier"]["polynomial_section_search_frontier"]
        self.assertFalse(row["degree_at_most_two"]["nonzero_section_with_this_ansatz_exists"])
        self.assertFalse(row["leading_twelve_branch"]["original_field_cubic_section_on_this_branch_exists"])
        self.assertFalse(row["remaining_leading_minus_twenty_four_system"]["existence_or_nonexistence_solved"])
        self.assertFalse(row["scope"]["all_rational_sections_excluded"])

    def test_no_scope_conflation(self):
        self.assertTrue(all(not value for value in self.report["formal_combination_and_quotient_periods"]["scope"].values()))
        self.assertFalse(self.report["supersession_boundary"]["restricted_reduced_inverse_cancels_unsubtracted_gravity_or_full_Gammahat"])

    def test_all_gates_open_and_F97(self):
        self.assertEqual(set(self.report["gate_ledger"]),{"G"+str(i) for i in range(1,9)})
        self.assertTrue(all(v.startswith("OPEN:") for v in self.report["gate_ledger"].values()))
        self.assertEqual(self.report["terminal_decision"]["closed_gates"],[])
        self.assertFalse(self.report["terminal_decision"]["all_F96_obligations_fully_completed"])
        self.assertEqual(self.report["next_required_action"]["id"],"F97_EQUIVARIANT_MASS_DEFECT_INDEX_AND_FULL_RELATIVE_GLUE")

    def test_rehashed_promotion_rejected(self):
        changed=copy.deepcopy(self.report)
        changed["terminal_decision"]["theory_complete"]=True
        changed["core_sha256"]=audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_report(changed)

    def test_rehashed_period_change_rejected(self):
        changed=copy.deepcopy(self.report)
        changed["formal_combination_and_quotient_periods"]["rows"][0]["quotient_mixed_gauge_CP3_period"]="0"
        changed["core_sha256"]=audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_report(changed)

    def test_generated_artifacts_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")),self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"),audit.render_markdown(self.report))
        self.assertIn("cancels the isolated defect's reduced anomaly on every bordism class",audit.render_markdown(self.report))
        self.assertNotIn("cancels every reduced character",audit.render_markdown(self.report))


if __name__=="__main__":
    unittest.main()
