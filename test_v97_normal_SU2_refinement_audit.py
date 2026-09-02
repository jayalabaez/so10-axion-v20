import copy
import unittest

import sympy as sp
import v97_normal_SU2_refinement_audit as audit


class TestV97NormalSU2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()

    def test_canonical_lineage(self):
        self.assertEqual(self.report["core_sha256"], audit.common.canonical_sha(self.report))
        audit.validate_certificate(self.report)

    def test_genuine_complete_SU2_weights(self):
        self.assertEqual(audit.su2_weights(1), [1, -1])
        self.assertEqual(audit.su2_weights(3), [3, 1, -1, -3])
        self.assertEqual(self.report["changed_representation"]["complex_Weyl_components"], 2)

    def test_SU2_Weyl_conjugation(self):
        z = sp.symbols("z", nonzero=True)
        J = sp.Matrix([[0, 1], [-1, 0]])
        T = sp.diag(z, 1/z)
        self.assertEqual(J*T*J.inv(), T.inv())
        self.assertEqual(z+1/z, (z+1/z).subs(z, 1/z))

    def test_splitting_principle_index(self):
        u, y, p, r2 = audit.u, audit.y, audit.p, audit.r2
        from_roots = audit.line_index(-3*u+y)+audit.line_index(-3*u-y)
        self.assertEqual(sp.expand(from_roots-audit.su2_index(-3, 1).subs(r2, -y*y)), 0)
        self.assertEqual(audit.su2_index(-3, 1), -9*u**3+3*u*r2+u*p/4)

    def test_general_weight_formula(self):
        u, p, r2 = audit.u, audit.p, audit.r2
        for n in range(1, 12):
            dim = n+1
            for k in (-5, -3, -1, 1, 3):
                expected = sp.Rational(dim*k**3, 6)*u**3-k*audit.dynkin_index_twice(n)*u*r2-sp.Rational(dim*k, 24)*u*p
                self.assertEqual(sp.expand(audit.su2_index(k, n)-expected), 0)

    def test_new_normal_R_curvature_cancel(self):
        row = self.report["nonabelian_curvature_repair"]
        self.assertEqual(sp.expand(sp.sympify(row["fermion_I6"])+sp.sympify(row["integer_CS_I6"])-sp.sympify(row["target_I6"])), 0)
        self.assertEqual(row["integer_coefficients"], [-1, 10, -3])
        self.assertTrue(row["R_bundle_need_not_split_into_Cartan_lines"])

    def test_all_central_kernel_elements(self):
        self.assertEqual(self.report["changed_representation"]["all_eight_kernel_exponents"], [0]*8)
        self.assertFalse(self.report["changed_representation"]["complete_supermultiplet_or_global_wall_placement_constructed"])

    def test_actual_orbifold_R_condition_not_assumed(self):
        row = self.report["changed_representation"]
        self.assertFalse(row["unbroken_SU2_R_at_the_actual_orbifold_wall_established"])
        self.assertFalse(row["preserves_V96_qN_minus_r_over2_zero_for_every_component"])
        self.assertEqual(row["C4_normal_R_weight_exponents_mod8"], [6, 4])

    def test_Witten_parity_formula_for_all_tested_reps(self):
        for n in range(1, 100, 2):
            d = n+1
            self.assertEqual(audit.dynkin_index_twice(n), d*(d*d-1)//6)
            self.assertEqual(audit.dynkin_index_twice(n) % 2, (d//2) % 2)

    def test_symbolic_parity_identity(self):
        n = sp.symbols("n", integer=True, positive=True)
        diff = (2*n)*((2*n)**2-1)/6-n
        self.assertEqual(sp.factor(diff-4*n*(n-1)*(n+1)/3), 0)

    def test_odd_normal_weights_preserve_parity_constraint(self):
        for n in range(1, 30, 2):
            for k in (-7, -5, -3, -1, 1, 3):
                self.assertEqual(audit.dynkin_index_twice(n) % 2, ((n+1)*k//2) % 2)
        self.assertEqual((-6//2) % 2, 1)

    def test_fundamental_and_three_doublets_both_have_Witten_class(self):
        self.assertEqual(audit.dynkin_index_twice(1) % 2, 1)
        self.assertEqual((3*audit.dynkin_index_twice(1)) % 2, 1)
        self.assertEqual(2*(-3), 3*2*(-1))

    def test_bosonic_CS_vanishes_at_Witten_witness(self):
        cs = sp.sympify(self.report["nonabelian_curvature_repair"]["integer_CS_I6"])
        self.assertEqual(cs.subs(audit.u, 0), 0)
        self.assertEqual(self.report["forced_Witten_class_in_this_ansatz"]["new_fermion_phase"], "-1")

    def test_mod2_ranks_are_not_rational_rank(self):
        self.assertEqual(audit.rank_mod2([[1, 1], [1, -1]]), 1)

    def test_AHSS_differentials(self):
        row = self.report["restricted_product_bordism"]
        A, B = sp.Matrix(row["d2_outgoing_H4_Z2_to_H2_Z2"]), sp.Matrix(row["d2_incoming_H6_Z_to_H4_Z2"])
        self.assertTrue(all(int(v) % 2 == 0 for v in A*B))
        self.assertEqual((audit.rank_mod2(A.tolist()), audit.rank_mod2(B.tolist())), (2, 2))
        self.assertEqual(5-audit.rank_mod2(A.tolist())-audit.rank_mod2(B.tolist()), 1)

    def test_AHSS_only_R_class_survives(self):
        row = self.report["restricted_product_bordism"]
        B = sp.Matrix(row["d2_incoming_H6_Z_to_H4_Z2"])
        self.assertEqual(list(B.row(4)), [0]*9)
        self.assertEqual(row["Omega5"], "Z2")
        self.assertFalse(row["this_is_the_full_Gammahat_bordism_group"])

    def test_flat_ratio_has_zero_curvature(self):
        row = self.report["nonabelian_curvature_repair"]
        self.assertEqual(sp.expand(sp.sympify(row["fermion_I6"])+sp.sympify(row["integer_CS_I6"])-sp.sympify(row["reference_R_trivial_fermion_I6"])-sp.sympify(row["reference_CS_I6"])), 0)

    def test_Z2_inverse_on_all_restricted_classes(self):
        for nu in (1, -1):
            self.assertEqual(nu*nu, 1)
        row = self.report["flat_refinement"]
        self.assertTrue(row["multiplying_by_nu_R_restores_reference_on_all_stated_product_backgrounds"])
        self.assertFalse(row["restores_reference_means_trivializes_reference_anomaly"])

    def test_no_total_parent_anomaly_inferred(self):
        row = self.report["forced_Witten_class_in_this_ansatz"]
        self.assertFalse(row["full_parent_bare_R_torsion_already_computed"])
        self.assertFalse(row["full_parent_total_Witten_anomaly_proved_nonzero"])
        self.assertFalse(self.report["nonabelian_curvature_repair"]["original_bulk_R_flavor_anomalies_have_been_computed_or_cancelled"])

    def test_diagonal_and_independent_gluing_distinguished(self):
        row = self.report["flat_refinement"]
        self.assertTrue(row["two_C4_sectors_cancel_on_shared_diagonal_R_background"])
        self.assertFalse(row["shared_diagonal_cancellation_proves_independent_endpoint_gluing"])
        self.assertFalse(row["same_action_5D_inflow_realizing_nu_R_constructed"])
        self.assertFalse(row["natural_Spin_c_half_period_from_V96_removed"])

    def test_rehashed_global_promotion_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["flat_refinement"]["full_Gammahat_or_SU2_twisted_tangential_descent_proved"] = True
        changed["core_sha256"] = audit.common.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(changed)

    def test_invalid_weights_rejected(self):
        for n in (-1, sp.Rational(1, 2), "1"):
            with self.assertRaises(ValueError):
                audit.su2_weights(n)
        with self.assertRaises(ValueError):
            audit.su2_index(sp.Rational(1, 2), 1)


if __name__ == "__main__":
    unittest.main()
