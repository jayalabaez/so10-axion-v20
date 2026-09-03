import copy
from math import gcd
import unittest
from unittest.mock import patch

import sympy as sp

import v101_higgs_background_restriction_audit as audit


class TestV101HiggsBackground(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()
        cls.parents = audit.load_inputs()
        cls.saved = cls.parents["v92_route"]["smooth_singlet_projectors"]

    def test_canonical_build_and_parent_edge(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        self.assertEqual(self.report["input_core_hashes"], {k: v[1] for k, v in audit.PARENTS.items()})
        audit.validate_certificate(self.report)
        self.assertEqual(self.parents["v100_master"]["input_core_hashes"]["v100_route"], audit.PARENTS["v100_route"][1])

    def test_all_relevant_source_and_test_pins_are_live(self):
        original = audit.file_sha
        for name in ("v92_singlet_projector_certificate.py", "test_v92_singlet_mass_module.py",
                     "v93_mass_sector_symmetry_descent.py", "v95_wall_symmetry_lift_audit.py",
                     "v100_correlated_quotient_period_audit.py", "test_v100_spectator_GS_obstruction_audit.py",
                     "susy_v100_multipath_g1_frontier_master_audit.py"):
            with patch.object(audit, "file_sha", side_effect=lambda p: "0"*64 if p.name == name else original(p)):
                with self.assertRaises(RuntimeError):
                    audit.load_inputs()

    def test_actual_two_distinct_Phi_blocks_and_signs(self):
        rows = {r["name"]: r for r in self.report["actual_selected_scalar_weights"]}
        self.assertEqual((rows["Phi_plus"]["m"], rows["Phi_plus"]["side"], rows["Phi_plus"]["continuous_charge"]), (0, "plus", 8))
        self.assertEqual((rows["Phi_minus"]["m"], rows["Phi_minus"]["side"], rows["Phi_minus"]["continuous_charge"]), (3, "minus", -8))
        self.assertNotEqual(rows["Phi_plus"]["source_block_sha256"], rows["Phi_minus"]["source_block_sha256"])
        self.assertEqual(sum(r["copies"] for r in rows.values()), 11)

    def test_scalar_A_rows_are_derived_from_source_R_and_flavor(self):
        for item in self.saved["eleven_mode_normal_aligned_witness"]["direct_sum_blocks"]:
            b = item["certificate"]
            expected = sp.diag(audit.matrix(b["effective_plus"]["A"]), audit.matrix(b["effective_minus_column"]["A"]))
            actual = audit.projectors.clean(audit.ZETA**-1*audit.matrix(b["underlying_flavor"]["A"]))
            self.assertEqual(actual, expected)

    def test_actual_Rtilde_is_not_geometric_m(self):
        rows = {r["name"]: r for r in self.report["actual_selected_scalar_weights"]}
        self.assertEqual([rows[k]["flavor_Rtilde_rho_mod4"] for k in ("Phi_plus", "Phi_minus")], [3, 1])
        self.assertEqual([rows[k]["scalar_Rtilde_phase"] for k in ("Phi_plus", "Phi_minus")], ["1", "1"])
        self.assertTrue(all(rows[k]["scalar_Rtilde_phase"] == "I" for k in ("S2", "S4", "S6")))

    def test_selected_lines_are_invariant_at_every_source_stratum(self):
        for row in self.report["actual_selected_scalar_weights"]:
            self.assertEqual(set(row["strata"]), {"z00", "z11", "z10", "z01"})
            for source in row["strata"].values():
                P = audit.matrix(source["projector"])
                self.assertEqual(P*P, P)
                self.assertEqual(P.rank(), 1)
                self.assertEqual(sp.sympify(source["phase"]), 1)

    def test_scalar_kernel_needs_R_and_flavor_not_normal_half(self):
        old = audit.center.old_kernel()
        self.assertEqual(audit.center.character_descent(audit.SCALAR_BITS, old), [0]*len(old))
        for bits in ((0, 0, 0, 0, 0, 1, 0), (0, 0, 0, 1, 0, 0, 0), (0, 1, 0, 1, 0, 1, 0)):
            self.assertTrue(any(audit.center.character_descent(bits, old)))

    def test_symbolic_scalar_line_formulas_retain_every_root(self):
        r, ep, em, d = audit.r, audit.ep, audit.em, audit.d
        self.assertEqual(audit.scalar_line(r, ep, d, 8, "plus"), r+ep+4*d)
        self.assertEqual(audit.scalar_line(r, em, d, 8, "minus"), r-em-4*d)
        formulas = self.report["combined_Higgs_line_and_mass_tensor"]
        self.assertEqual(sp.sympify(formulas["Phi_plus_c1"]), r+ep+4*d)
        self.assertEqual(sp.sympify(formulas["Phi_minus_c1"]), r-em-4*d)
        self.assertEqual(formulas["normal_scalar_weight"], 0)

    def test_gauge_only_restriction_is_conditional(self):
        lp = audit.scalar_line(0, 0, audit.d, 8, "plus")
        lm = audit.scalar_line(0, 0, audit.d, 8, "minus")
        self.assertEqual((lp, lm), (4*audit.d, -4*audit.d))
        self.assertFalse(self.report["combined_Higgs_line_and_mass_tensor"]["relations_force_D4_trivial_without_internal_restriction"])

    def test_original_CP3_actual_weights_are_five_and_minus_four(self):
        r, e = sp.Rational(1, 2), sp.Rational(1, 2)
        self.assertEqual([audit.scalar_line(r, e, 1, 8, s) for s in ("plus", "minus")], [5, -4])
        row = self.report["CP3_original_cocharacter"]
        self.assertEqual([row["selected_N1_scalar_line_degrees"][k] for k in ("Phi_plus", "Phi_minus")], [5, -4])
        self.assertFalse(row["both_selected_Phi_lines_topologically_trivial"])

    def test_original_CP3_rank_two_Chern_obstruction(self):
        H = sp.Symbol("H")
        total = sp.expand((1+5*H)*(1-4*H))
        row = self.report["CP3_original_cocharacter"]
        self.assertEqual(total.coeff(H), row["Phi_pair_c1_coefficient_H"])
        self.assertEqual(total.coeff(H, 2), row["Phi_pair_c2_coefficient_H2"])
        self.assertNotEqual(total.coeff(H, 2), 0)

    def test_compensation_solved_from_actual_combined_lines(self):
        solution = sp.solve([audit.r+audit.ep+4*audit.d, audit.r-audit.em-4*audit.d], (audit.ep, audit.em))
        self.assertEqual(solution, {audit.ep: -4*audit.d-audit.r, audit.em: -4*audit.d+audit.r})
        chosen = {audit.d: 1, audit.r: sp.Rational(1, 2)}
        roots = audit.profile_roots("Phi_only_compensation")
        self.assertEqual((solution[audit.ep].subs(chosen), solution[audit.em].subs(chosen)), (roots["Phi_plus"], roots["Phi_minus"]))

    def test_each_complete_profile_accounts_for_actual267_hypers(self):
        for key in ("CP3_original_cocharacter", "CP3_Phi_only_compensated_cocharacter", "CP3_selected_mass_compensated_cocharacter"):
            rows = self.report[key]["all267_compressed_blocks"]
            self.assertEqual(sum(r["copies"]*r["hypers_per_copy"] for r in rows), 267)
            self.assertTrue(all(all(row["checks"].values()) for row in rows))
            self.assertEqual(sum(row["copies"]*len(row["full_real_scalar_complexification_weights"]) for row in rows), 4*267)

    def test_retuning_closes_at_exact_same_old_kernel_element(self):
        endpoint = tuple((a+b) % 2 for a, b in zip(audit.center.KN, audit.center.KS))
        self.assertEqual(endpoint, (0, 1, 0, 1, 1, 1, 1))
        self.assertIn(endpoint, audit.center.old_kernel())
        for profile in ("original", "Phi_only_compensation", "selected_mass_tensor_compensation"):
            for value in audit.profile_roots(profile).values():
                self.assertEqual(sp.simplify(sp.exp(2*sp.pi*sp.I*value)), -1)

    def test_symplectic_reality_and_scalar_real_involution(self):
        rows = self.report["CP3_selected_mass_compensated_cocharacter"]["all267_compressed_blocks"]
        for row in rows:
            H = audit.matrix(row["paired_generator"])
            n = row["hypers_per_copy"]
            J = audit.projectors.symplectic_form(n)
            self.assertEqual(H.T*J+J*H, sp.zeros(2*n))
            B = sp.kronecker_product(audit.projectors.symplectic_form(1), J)
            self.assertEqual(B*sp.conjugate(B), sp.eye(4*n))
            W = sp.diag(*[sp.sympify(z) for z in row["full_real_scalar_complexification_weights"]])
            self.assertEqual(B*sp.conjugate(W)+W*B, sp.zeros(4*n))

    def test_retuned_generators_commute_with_actual_frozen_matrices(self):
        rows = self.report["CP3_selected_mass_compensated_cocharacter"]["all267_compressed_blocks"]
        for row, item in zip(rows, self.saved["eleven_mode_normal_aligned_witness"]["direct_sum_blocks"]):
            H = audit.matrix(row["paired_generator"])
            b = item["certificate"]
            for key in ("A", "U", "V", "external_k"):
                M = audit.matrix(b["underlying_flavor"][key])
                self.assertEqual(H*M-M*H, sp.zeros(H.rows))
            P = audit.matrix(row["constant_projector"])
            self.assertEqual(H*P-P*H, sp.zeros(H.rows))

    def test_Phi_only_compensation_does_not_automatically_preserve_couplings(self):
        row = self.report["CP3_Phi_only_compensated_cocharacter"]
        self.assertTrue(row["both_selected_Phi_lines_topologically_trivial"])
        self.assertEqual(row["displayed_cubic_degrees"], [6, 6])
        self.assertEqual(row["required_lambda_kappa_coupling_line_degrees"], [-4, -4])
        self.assertFalse(row["constant_V93_lambda_kappa_covariant_under_this_Cartan"])

    def test_superpotential_and_fermion_weights_follow_N1_partner_rule(self):
        theta = audit.x/2+audit.r
        formulas = self.report["combined_Higgs_line_and_mass_tensor"]
        self.assertEqual(sp.sympify(formulas["selected_N1_theta_internal_curvature"]), theta)
        self.assertEqual(sp.sympify(formulas["superpotential_line_c1"]), 2*theta)
        for q, e in ((2, audit.e2), (4, audit.e4), (6, audit.e6)):
            fermion = sp.expand(audit.scalar_line(audit.r, e, audit.d, q, "plus")-theta)
            self.assertEqual(fermion, e+sp.Rational(q, 2)*audit.d-audit.x/2)

    def test_coupling_bundle_formula_not_just_charge_sum(self):
        f = self.report["combined_Higgs_line_and_mass_tensor"]
        self.assertEqual(sp.sympify(f["lambda_coupling_line_c1"]), audit.x-audit.r+audit.em-audit.e2-audit.e6)
        self.assertEqual(sp.sympify(f["kappa_coupling_line_c1"]), audit.x-audit.r+audit.em-2*audit.e4)
        self.assertNotIn(audit.d, sp.sympify(f["lambda_coupling_line_c1"]).free_symbols)

    def test_further_nine_line_retuning_preserves_selected_tensors(self):
        row = self.report["CP3_selected_mass_compensated_cocharacter"]
        self.assertEqual(row["selected_N1_scalar_line_degrees"], {"Phi_plus": 0, "Phi_minus": 0, "S2": 1, "S4": 1, "S6": 1})
        self.assertEqual(row["displayed_cubic_degrees"], [2, 2])
        self.assertEqual(row["required_lambda_kappa_coupling_line_degrees"], [0, 0])
        self.assertTrue(row["constant_V93_lambda_kappa_covariant_under_this_Cartan"])
        self.assertFalse(row["D_fourth_power_trivial"])

    def test_mandatory_bulk_derivative_pairing_survives_any_retuning(self):
        lp = audit.scalar_line(audit.r, audit.e4, audit.d, 4, "plus")
        lm = audit.scalar_line(audit.r, audit.e4, audit.d, 4, "minus")
        self.assertEqual(sp.expand(lp+lm+audit.x), audit.x+2*audit.r)
        self.assertEqual(sp.sympify(self.report["combined_Higgs_line_and_mass_tensor"]["full_hyper_normal_derivative_pairing_c1"]), audit.x+2*audit.r)

    def test_hypothetical_both_partner_Yukawas_have_normal_obstruction(self):
        row = self.report["combined_Higgs_line_and_mass_tensor"]["hypothetical_both_q4_partner_Yukawas"]
        yp, ym = [sp.sympify(row[k]) for k in ("after_both_Phi_lines_trivial_positive_c1", "after_both_Phi_lines_trivial_negative_c1")]
        self.assertEqual(sp.expand(yp+ym), -2*audit.x)
        solution = sp.solve([yp, ym], (audit.e4, audit.x))
        self.assertEqual(solution, {audit.e4: -2*audit.d, audit.x: 0})
        self.assertFalse(row["frozen_V93_contains_both"])
        self.assertFalse(row["CP3_N_O1_passes"])

    def test_local_mass_rank_requires_Phi_nonzero(self):
        v = sp.Symbol("v")
        M = v*sp.BlockMatrix([[sp.zeros(3), sp.eye(3), sp.zeros(3)],
                             [sp.eye(3), sp.zeros(3), sp.zeros(3)],
                             [sp.zeros(3), sp.zeros(3), sp.eye(3)]]).as_explicit()
        self.assertEqual(sp.factor(M.det()), -v**9)
        self.assertEqual(M.subs(v, 1).rank(), 9)
        self.assertEqual(M.subs(v, 0).rank(), 0)

    def test_compensation_does_not_change_target_or_genuine_completed_indices(self):
        h = sp.Symbol("h")
        target = (h**3+h*h*h/2)/4
        self.assertEqual(target.coeff(h, 3), sp.Rational(3, 8))
        index = lambda k: sp.Rational(k**3-k, 6)
        self.assertEqual([index(n+1)+index(n) for n in range(3)], [0, 1, 5])
        for key in ("CP3_original_cocharacter", "CP3_Phi_only_compensated_cocharacter", "CP3_selected_mass_compensated_cocharacter"):
            self.assertEqual(self.report[key]["V100_P_over4_period_unchanged"], "3/8")

    def test_full_flavor_and_missing_coupling_scope_not_promoted(self):
        row = self.report["constant_coupling_and_reduction_boundary"]
        self.assertFalse(row["source_wall_tensor_invariant_under_full_Sp267"])
        self.assertFalse(row["all_old_V90_Yukawa_driver_and_mediator_tensors_checked"])
        self.assertFalse(row["specific_retuned_cocharacter_is_accepted_physical_background"])
        for key in ("CP3_original_cocharacter", "CP3_Phi_only_compensated_cocharacter", "CP3_selected_mass_compensated_cocharacter"):
            self.assertFalse(self.report[key]["actual_physical_background_admissibility_proved"])
            self.assertFalse(self.report[key]["full_old_action_coupling_stabilizer_proved"])

    def test_Phi_only_finite_stabilizer_is_not_entire_V90_vacuum(self):
        row = self.report["UV_IR_and_finite_boundary"]
        self.assertEqual(gcd(*row["V90_full_VEV_charge_magnitudes"]), row["V90_full_VEV_external_stabilizer_order"])
        self.assertEqual(gcd(8, 8), 8)
        self.assertEqual(gcd(8, 4, 6), 2)
        self.assertFalse(row["finite_C8_or_residual_C2_torsion_anomaly_computed_here"])

    def test_N40_scout_cannot_borrow_removed_Phi_VEVs(self):
        row = self.report["N40_replacement_incompatibility"]
        self.assertEqual(row["bound_actual_removed_free_charges"], [4, 4, 8, -8])
        self.assertTrue(row["both_old_Phi_removed"])
        self.assertFalse(row["old_mass_module_preserved"])
        self.assertFalse(row["may_borrow_old_Phi_background_restriction_without_new_Higgs_sector"])

    def test_reject_invalid_charge_profile_and_endpoint_inputs(self):
        for q, side in ((True, "plus"), (3, "plus"), (-2, "minus"), (2, "unknown")):
            with self.assertRaises(ValueError):
                audit.scalar_line(0, 0, 1, q, side)
        with self.assertRaises(ValueError):
            audit.profile_roots("invented")
        b = self.saved["eleven_mode_normal_aligned_witness"]["direct_sum_blocks"][0]["certificate"]
        for root in (0, 1, sp.Rational(1, 3)):
            with self.assertRaises(ValueError):
                audit.block_cocharacter(b, 1, root)

    def test_tamper_rejected_even_with_recomputed_core(self):
        out = copy.deepcopy(self.report)
        out["CP3_original_cocharacter"]["selected_N1_scalar_line_degrees"]["Phi_plus"] = 4
        out["core_sha256"] = audit.canonical_sha(out)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(out)

    def test_every_completion_boundary_remains_open(self):
        row = self.report["terminal_decision"]
        self.assertEqual(row["closed_gates"], [])
        self.assertFalse(row["all_physical_backgrounds_classified"])
        self.assertFalse(row["microscopic_parent_accepted"])
        self.assertFalse(row["full_anomaly_cancelled"])
        self.assertFalse(row["theory_complete"])
        self.assertFalse(self.report["UV_IR_and_finite_boundary"]["UV_anomaly_erased_by_Higgsing"])
        self.assertFalse(self.report["nonzero_section_and_multiplet_boundary"]["compensated_line_triviality_implies_F_D_flat_SUSY_vacuum"])


if __name__ == "__main__":
    unittest.main()
