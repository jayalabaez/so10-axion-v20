import copy
import unittest

import sympy as sp

import v93_mass_sector_symmetry_descent as target


class TestV93MassSectorSymmetryDescent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = target.build_certificate()

    def test_all267_pairs_and_minimal_flavor_support(self):
        row = self.result["singlet_R_extension"]
        self.assertEqual(row["complex_half_flavor_phase_multiplicities_rho0123"],[265,1,0,1])
        self.assertEqual(sum(r["copies"]*r["certificate"]["hyper_count_per_block"] for r in row["compressed_direct_sum_blocks"]),267)
        self.assertEqual(row["minimum_nontrivial_flavor_hyper_pairs_with_this_common_R_factor"],2)

    def test_exact_matrices_commute_and_descend(self):
        row = self.result["singlet_R_extension"]
        for item in row["compressed_direct_sum_blocks"]:
            cert = item["certificate"]
            self.assertTrue(all(cert["checks"].values()))
            self.assertEqual(cert["partner_superpotential_charge_mod4"],2)
            self.assertTrue(all(value==0 for values in cert["existing_kernel_action_exponents_mod2"].values() for value in values.values()))
        self.assertTrue(row["descends_through_all_current_smooth_kernel_generators"])
        self.assertFalse(row["new_relation_R_squared_equals_fermion_parity_imposed"])

    def test_selected_N1_R_charges(self):
        modes = self.result["singlet_R_extension"]["constant_mode_R_assignments"]
        self.assertEqual([r["charge"] for r in modes],[-8,2,2,2,4,4,4,6,6,6,8])
        self.assertEqual([r["scalar_R"] for r in modes],[0]+[1]*9+[0])
        self.assertEqual([r["fermion_R"] for r in modes],[3]+[0]*9+[3])

    def test_old_smooth_bulk_table_matches(self):
        row = self.result["old_smooth_bulk_R_extension"]
        self.assertTrue(all(row["checks"].values()))
        self.assertEqual([r["derived_scalar_R"] for r in row["bound_bulk_field_matches"]],[0,2,0,2,0])
        self.assertEqual((row["Sigma_scalar_R"],row["N1_vector_gaugino_R"]),(0,1))
        self.assertFalse(row["localized_Fi_PA_X_Xbar_S8_SB_SX_and_mediator_lifts_constructed"])

    def test_every_wall_uses_actual_minus_Phi(self):
        rows = self.result["fixed_wall_selection"]["rows"]
        self.assertEqual([r["stabilizer"] for r in rows],["A","UA","UA2","VA2"])
        for row in rows:
            self.assertEqual(row["fields"]["Phi_minus"]["N1_side"],"minus")
            self.assertTrue(all(f["phase"]=="1" and f["invariant_projector_rank"]==1 for f in row["fields"].values()))
            for channel in row["mass_channels"]:
                self.assertEqual(channel["orbifold_product_phase"],"1")
                self.assertEqual(channel["independent_R4_product_phase"],"-1")
                self.assertEqual(channel["independent_R4_d2theta_phase"],"-1")

    def test_wrong_Phi_side_is_a_noninvariant_field(self):
        _, report, _ = target.load_inputs()
        blocks = report["eleven_mode_normal_aligned_witness"]["direct_sum_blocks"]
        phi = next(r["certificate"] for r in blocks if r["certificate"]["q_magnitude"]==8 and r["certificate"]["m"]==3)
        self.assertEqual(target.matrix(phi["strata"]["z00"]["plus_matrix"]),sp.Matrix([[-sp.I]]))
        self.assertEqual(target.matrix(phi["strata"]["z00"]["plus_projector"]),sp.zeros(1))

    def test_dense_and_diagonal_R_families(self):
        row = self.result["R_assignment_family"]
        self.assertEqual(row["dense_solution_count"],8)
        self.assertEqual(row["fixed_diagonal_pairing_independent_generation_solution_count"],512)
        self.assertIn([1,1,1],row["dense_lambda_and_kappa_triplet_uniform_solutions_r2_r4_r6"])
        self.assertTrue(all((r2+r6)%4==2 and 2*r4%4==2 for r2,r4,r6 in row["dense_lambda_and_kappa_triplet_uniform_solutions_r2_r4_r6"]))

    def test_anomaly_does_not_disappear_after_mass(self):
        row = self.result["mass_anomaly_matching"]
        self.assertEqual((row["TrQ"],row["TrQ3"]),(36,864))
        self.assertEqual(row["heavy_fermion_R_charges"],[0]*9)
        self.assertFalse(row["mass_erases_anomaly_matching_obligation"])
        self.assertFalse(row["new_invented_axion_required"])
        self.assertEqual(row["mass_determinant_proportional_to"],"-Phi_minus^9")

    def test_local_descent_and_period_test(self):
        row = self.result["mass_anomaly_matching"]
        x,p1,phi,epsilon = sp.symbols("x p1 phi epsilon")
        exponent = sp.sympify(row["local_IR_matching_log_phase_over_2pi_i"])
        k4 = sp.sympify(row["consistent_descent_K4"])
        self.assertEqual(sp.expand(exponent.subs(phi,phi-8*epsilon)-exponent-epsilon*k4),0)
        self.assertEqual(sp.expand(exponent/phi),-18*x*x+sp.Rational(3,16)*p1)
        self.assertTrue(row["ordinary_spin4_axion_period_check"]["curvature_period_check_passes"])

    def test_spin_c11_gauge_half_integral_flux_periods_on_spin4(self):
        row = self.result["mass_anomaly_matching"]["ordinary_spin4_with_Spin_c11_gauge_quotient_period_check"]
        self.assertTrue(row["curvature_period_check_passes"])
        self.assertFalse(row["covers_nonspin_tangential_Gammahat_or_torsion_backgrounds"])
        for l in range(-5,6):
            for k in range(-5,6):
                period = -18*sp.Rational(2*l,4)+sp.Rational(3,16)*48*k
                self.assertEqual(period,-9*l+9*k)
                self.assertTrue(period.is_Integer)

    def test_pure_untwisted_C8_shadow_not_continuous_cancellation(self):
        row = self.result["mass_anomaly_matching"]["pure_untwisted_C8_heavy_fermion_screen"]
        self.assertEqual((row["linear_numerator"],row["cubic_numerator"]),(72,77760))
        self.assertEqual((row["linear_residue"],row["cubic_residue"]),(0,0))
        self.assertTrue(row["pure_heavy_fermion_Spin4_times_C8_restriction_passes"])
        self.assertFalse(row["full_Gammahat_or_mixed_or_continuous_anomaly_cancelled"])

    def test_wall_not_promoted_to_full_flavor_or_supergravity_invariance(self):
        row = self.result["fixed_wall_selection"]
        self.assertFalse(row["invariant_under_entire_unreduced_Sp267_flavor_group"])
        self.assertFalse(row["full_localized_frame_or_gauged_flavor_tensor_completion_constructed"])
        self.assertTrue(row["new_coupling_selects_flavor_tensor_and_reduces_flavor_symmetry"])
        self.assertEqual(row["wall_coupling_mass_dimension_for_canonical_6D_bulk_fields"],-3)

    def test_fail_closed_and_canonical(self):
        self.assertTrue(all(value is False for value in self.result["limitations"].values()))
        self.assertEqual(self.result["core_sha256"],target.projectors.canonical_sha(self.result))
        changed = copy.deepcopy(self.result)
        changed["limitations"]["quantum_Z4R_is_anomaly_free"] = True
        changed["core_sha256"] = target.projectors.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            target.validate_certificate(changed)

    def test_invalid_phase_rejected(self):
        with self.assertRaises(ValueError):
            target.block_R_certificate({},4)


if __name__ == "__main__":
    unittest.main()
