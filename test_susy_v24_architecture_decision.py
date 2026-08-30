from __future__ import annotations

import copy
import json
import math
import unittest
from fractions import Fraction

import susy_v24_architecture_decision as decision


class SusyV24ArchitectureDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = decision.build_report()

    def test_published_Z5_control_and_derived_Z11_charges_are_not_conflated(self) -> None:
        control = self.report["published_Z5_control"]
        selected = self.report["selected_architecture"]
        self.assertEqual(control["charges"]["Z4R"], [0, 1, 1, 2, 0, 0, 2, 0, 1, 1, 0, 1])
        self.assertEqual(control["charges"]["Z5"], [0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 4, 1])
        self.assertEqual(selected["derived_minimal_parameters"]["N"], 11)
        self.assertEqual(selected["derived_minimal_parameters"]["r"], 2)
        self.assertIn("not published", selected["derived_selector_audit"]["provenance"])

    def test_Z11_selector_retains_required_mass_and_decay_terms(self) -> None:
        audit = decision.z11_selector_audit()
        self.assertTrue(all(audit["required_PQ_mass_and_decay_terms_allowed"].values()))
        self.assertTrue(decision.term_is_allowed(("P", "Psibar", "Psi")))
        self.assertTrue(decision.term_is_allowed(("P", "Psicbar", "Psic")))
        self.assertTrue(decision.term_is_allowed(("Psi", "Hcal", "Qc")))
        self.assertTrue(decision.term_is_allowed(("Q", "Hcal", "Psic")))

    def test_first_pure_P_term_matter_parity_and_domain_wall_arithmetic(self) -> None:
        audit = decision.z11_selector_audit()
        self.assertEqual(decision.first_pure_p_superpotential_power(N=11, r=2, p=1), 11)
        self.assertEqual(decision.first_pure_p_superpotential_power(N=5, r=1, p=1), 10)
        self.assertEqual(audit["pure_P_selector"]["same_benchmark_log10_Delta_theta_from_paper_formula"], -25)
        parity = audit["residual_visible_matter_parity"]
        self.assertEqual(parity["field_parities"]["Q"], -1)
        self.assertEqual(parity["field_parities"]["Qc"], -1)
        self.assertEqual(parity["field_parities"]["Hcal"], 1)
        self.assertEqual(parity["field_parities"]["P"], 1)
        self.assertTrue(parity["renormalizable_MSSM_RPV_forbidden"])
        self.assertTrue(parity["dimension_five_Q4_is_not_forbidden"])
        wall = audit["domain_wall_arithmetic"]
        self.assertEqual(wall["P_only_fixed_GS_phase_integer_gcd"], math.gcd(11, 4))
        self.assertFalse(wall["dynamical_GS_axion_mixing_landed"])
        self.assertFalse(wall["discrete_gauge_quotient_landed"])
        self.assertIsNone(wall["physical_GS_inclusive_vacuum_degeneracy"])
        self.assertIsNone(wall["physical_P11_lifting_of_NDW4_vacua"])
        self.assertIsNone(wall["physical_wall_collapse_time"])
        self.assertEqual(wall["physical_wall_analysis_state"], "OPEN")

    def test_mixed_and_visible_gravitational_anomaly_arithmetic(self) -> None:
        audit = decision.z11_selector_audit()
        mixed = audit["mixed_gauge_anomalies"]
        self.assertEqual(mixed["Z4R"]["raw"], (-3, -3, -3))
        self.assertEqual(mixed["Z4R"]["residue"], (1, 1, 1))
        self.assertEqual(mixed["Z11"]["raw"], (-2, -2, -2))
        self.assertEqual(mixed["Z11"]["residue"], (9, 9, 9))
        gravity = audit["visible_gravitational_GS_congruences"]
        self.assertEqual(gravity["visible_Z4R"]["raw"], 20)
        self.assertEqual(gravity["visible_Z11"]["raw"], 161)
        self.assertEqual(gravity["visible_Z11"]["residue_mod_11"], 7)
        self.assertEqual(gravity["visible_Z11"]["24rho_residue_mod_11"], 7)
        self.assertTrue(gravity["visible_Z4R"]["congruence_satisfied"])
        self.assertTrue(gravity["visible_Z11"]["congruence_satisfied"])
        self.assertFalse(gravity["full_GS_and_hidden_sector_completion_landed"])

    def test_local_gauge_anomalies_and_exact_PS_beta_coefficients(self) -> None:
        local = decision.local_gauge_anomaly_accounting()
        self.assertEqual(local["SU4C_cubic_anomaly"], 0)
        self.assertEqual(local["SU2L_doublets_for_Witten_test"], 22)
        self.assertEqual(local["SU2R_doublets_for_Witten_test"], 30)
        self.assertTrue(local["local_gauge_anomalies_cancel"])
        coefficients = decision.ps_gauge_coefficients()
        self.assertEqual(coefficients["sum_T"], (Fraction(13), Fraction(11), Fraction(15)))
        self.assertEqual(coefficients["b"], (Fraction(1), Fraction(5), Fraction(9)))
        self.assertEqual(coefficients["B_gauge_only"], (
            (Fraction(108), Fraction(15), Fraction(21)),
            (Fraction(75), Fraction(53), Fraction(3)),
            (Fraction(105), Fraction(3), Fraction(81)),
        ))

    def test_published_superpotential_DT_and_vacuum_boundary_are_retained(self) -> None:
        selected = self.report["selected_architecture"]
        terms = selected["superpotential"]["W_PS_retained_in_minimal_model"]
        self.assertIn("Sc Sigma Sc", terms)
        self.assertIn("Scbar Sigma Scbar", terms)
        self.assertIn("(Scbar Qc Scbar Qc)/(2 Lambda)", terms)
        dt = selected["PS_breaking_and_doublet_triplet"]
        self.assertIn("all triplets", dt["published_conclusion"])
        self.assertIn("other directions", dt["published_stabilization_boundary"])
        self.assertFalse(dt["normalized_component_mass_matrices_landed_here"])

    def test_conditional_Planck120_screen_is_reproducible_but_bounded(self) -> None:
        initial = decision.pq_threshold_inverse_alpha()
        endpoint = decision.rk4_inverse_alpha_endpoint(initial_inverse=initial)
        self.assertAlmostEqual(initial, 15.204772813446867, places=11)
        for actual, expected in zip(endpoint, (13.80400253, 10.81562621, 7.44348638)):
            self.assertAlmostEqual(actual, expected, places=7)
        screen = self.report["independent_exact_accounting"]["conditional_Planck120_screen"]
        self.assertTrue(screen["screen_passes"])
        self.assertFalse(screen["physical_UV_completion_demonstrated"])

    def test_ranked_alternatives_have_exact_fatal_or_promotion_blockers(self) -> None:
        alternatives = self.report["ranked_alternatives"]
        self.assertEqual([row["rank"] for row in alternatives], [2, 3, 4, 5, 6])
        by_name = {row["route"]: row for row in alternatives}
        flipped = by_name["MAEKAWA_YAMASHITA_FLIPPED_SO10_X_U1_VPRIME"]
        self.assertEqual(flipped["derived_accounting"]["b_SO10"], 1)
        self.assertEqual(flipped["derived_accounting"]["published_generic_triplet_rank"], "7/7")
        filter_route = by_name["CHEN_ZHANG_FILTER_DW_SO10"]["derived_accounting"]
        missing = by_name["BABU_ET_AL_LARGE_REP_MISSING_PARTNER_SO10"]["derived_accounting_for_smallest_126_pair_option"]
        self.assertEqual((filter_route["sum_T"], filter_route["b_SO10"]), (311, 287))
        self.assertEqual((missing["sum_T"], missing["b_SO10"]), (113, 89))
        self.assertLess(filter_route["one_loop_pole_mu_over_MGUT_for_alpha_inverse_24"], 120)
        self.assertLess(missing["one_loop_pole_mu_over_MGUT_for_alpha_inverse_24"], 120)

    def test_no_hidden_no_go_is_claimed_and_all_full_gates_remain_open(self) -> None:
        selector = self.report["selected_architecture"]["derived_selector_audit"]
        self.assertFalse(selector["known_hidden_no_go"])
        self.assertGreaterEqual(len(selector["unresolved_non_no_go_boundaries"]), 4)
        self.assertEqual(self.report["closure_counts"], {"closed": 0, "open": 8})
        self.assertTrue(all(not row["closed"] and not row["full_gate_claim"] for row in self.report["gates"]))
        self.assertFalse(self.report["decision"]["go_as_complete_predictive_theory"])
        self.assertFalse(self.report["source_and_claim_boundary"]["PSZ4RZ11_is_described_as_published"])

    def test_frozen_outputs_and_core_hash(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(json.loads(decision.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(decision.OUT_MD.read_text(encoding="utf-8"), decision.markdown(self.report))
        changed = copy.deepcopy(self.report)
        changed["decision"]["go_as_complete_predictive_theory"] = True
        self.assertNotEqual(decision.canonical_sha(self.report), decision.canonical_sha(changed))


if __name__ == "__main__":
    unittest.main()
