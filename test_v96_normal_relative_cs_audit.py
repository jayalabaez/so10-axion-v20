import copy
import unittest

import sympy as sp
import v96_normal_relative_cs_audit as audit


class TestV96NormalCS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=audit.build_certificate()

    def test_canonical_and_parent_lineage(self):
        self.assertEqual(self.report["core_sha256"],audit.common.canonical_sha(self.report))
        self.assertEqual(self.report["input_core_hashes"],{k:v[1] for k,v in audit.PARENTS.items()})

    def test_odd_charge_lattice_congruence(self):
        for k in range(-61,62,2):
            self.assertEqual((k**3-k)%24,0)
            self.assertTrue(all(v.is_Integer for v in audit.odd_charge_coordinates(k,k**3)))

    def test_lattice_basis_and_converse(self):
        self.assertEqual(sp.Matrix([[1,3],[1,27]]).det(),24)
        for n1 in range(-4,5):
            for n3 in range(-4,5):
                self.assertEqual(audit.odd_charge_coordinates(n1+3*n3,n1+27*n3),(n1,n3))

    def test_target_odd_charge_lattice_obstruction(self):
        self.assertEqual(audit.odd_charge_coordinates(-6,6),(-sp.Rational(15,2),sp.Rational(1,2)))
        self.assertFalse(self.report["stronger_fermions_only_obstruction"]["SU5_cubic_cancellation_assumption_needed"])

    def test_CP3_period_screen(self):
        self.assertEqual(audit.cp3_period(audit.target_polynomial()),2)
        for k in range(-11,12,2):
            self.assertEqual(audit.cp3_period(audit.line_index(k*audit.u))%4,0)

    def test_three_exact_repairs(self):
        rows=self.report["new_normal_repairs"]
        self.assertEqual([r["Weyl_components_per_C4"] for r in rows],[2,4,6])
        self.assertEqual([r["CS_cubic_integer_level"] for r in rows],[10,6,2])
        for row in rows:
            self.assertEqual(row["fermions_plus_CS_minus_target"],"0")
            self.assertEqual(row["Tr_k"],-6)
            self.assertEqual(row["CP3_combined_period"],"2")

    def test_explicit_two_field_polynomial(self):
        row=audit.repair_row([-3,-3])
        self.assertEqual(sp.sympify(row["fermion_I6"]),-9*audit.u**3+audit.u*audit.p/4)
        self.assertEqual(sp.sympify(row["CS_curvature_I6"]),-audit.u*audit.c2+10*audit.u**3)

    def test_known_kernel_for_all_new_components(self):
        for row in self.report["new_normal_repairs"]:
            for field in row["N1_center_and_phase_bookkeeping"]:
                self.assertEqual(field["fermion_kernel_exponents"],[0]*4)
                self.assertEqual(field["scalar_kernel_exponents"],[0]*4)
                self.assertEqual(field["shared_qN_minus_rR_over2"],"0")

    def test_R_terms_retained(self):
        row=audit.repair_row([-3,-3])
        expected=sp.expand(-9*((audit.u+audit.y)**3-audit.u**3)+audit.p*audit.y/4)
        self.assertEqual(sp.sympify(row["R_terms_not_cancelled_by_frozen_CS"]),expected)
        self.assertFalse(row["Cartan_and_center_data_construct_full_localized_Gammahat_representations"])

    def test_CS_character_is_integral_and_degree_six(self):
        row=self.report["product_category_quantized_CS_construction"]
        self.assertEqual(row["differential_character_degree"],6)
        self.assertTrue(row["a_global_topological_action_in_the_stated_product_category_is_defined"])
        self.assertFalse(row["action_requires_a_nowhere_nonzero_section_of_M"])
        for gamma in (2,6,10):
            for uc2 in range(-2,3):
                for u3 in range(-2,3):
                    self.assertEqual((-uc2+gamma*u3)%1,0)

    def test_two_field_family_and_minimality_scope(self):
        for r in range(-4,5):
            row=audit.repair_row([-3+2*r,-3-2*r])
            self.assertEqual(row["CS_cubic_integer_level"],10+12*r*r)
        self.assertFalse(self.report["minimality_scope"]["minimum_over_all_spin_invertible_or_interacting_theories_claimed"])

    def test_even_or_wrong_total_charges_rejected(self):
        for charges in ([],[-6],[-2,-4],[-1,-1],[0,-3,-3]):
            with self.assertRaises(ValueError):
                audit.repair_row(charges)

    def test_Spin_c_product_index_is_integral_for_all_odd_charges(self):
        for k in range(-15,16,2):
            period=audit.spin_c_product_period(audit.line_index(k*audit.u))
            j=(k-1)//2
            self.assertEqual(period,sp.Rational(k**3-k,8))
            self.assertEqual(period,sp.Rational(j*(j+1)*(2*j+1),2))
            self.assertTrue(period.is_Integer)

    def test_Spin_c_unchanged_target_has_half_period(self):
        self.assertEqual(audit.spin_c_product_period(audit.target_polynomial()),sp.Rational(3,2))
        row=self.report["descent_obstruction_to_natural_Spin_c_category"]
        self.assertEqual(row["extension_ambiguity_phase"],"-1")
        self.assertTrue(row["no_separate_integral_normal_root_u_exists"])
        self.assertFalse(row["all_these_backgrounds_proved_admissible_in_full_Gammahat_orbifold"])

    def test_CS_fails_to_descend_with_unchanged_polynomial(self):
        rows=self.report["new_normal_repairs"]
        self.assertEqual([r["Spin_c6_formal_CS_period"] for r in rows],["15/2","9/2","3/2"])
        self.assertTrue(all(sp.Rational(r["Spin_c6_formal_fermion_period"]).is_Integer for r in rows))
        self.assertTrue(all(r["Spin_c6_formal_combined_period"]=="3/2" for r in rows))

    def test_quantized_functional_not_parent_trivialization(self):
        row=self.report["product_category_quantized_CS_construction"]
        self.assertFalse(row["identification_with_the_parent_anomaly_functor_proved"])
        self.assertFalse(row["full_relative_anomaly_trivialization_constructed"])
        self.assertFalse(row["action_descends_to_full_Gammahat_orbifold"])
        self.assertEqual(self.report["terminal_decision"]["closed_gates"],[])

    def test_corrupted_core_rejected(self):
        changed=copy.deepcopy(self.report)
        changed["core_sha256"]="0"*64
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(changed)

    def test_rehashed_global_promotion_rejected(self):
        changed=copy.deepcopy(self.report)
        changed["terminal_decision"]["same_action_parent_accepted"]=True
        changed["core_sha256"]=audit.common.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(changed)

    def test_rehashed_arithmetic_change_rejected(self):
        changed=copy.deepcopy(self.report)
        changed["new_normal_repairs"][0]["CS_cubic_integer_level"]=2
        changed["core_sha256"]=audit.common.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(changed)


if __name__=="__main__":
    unittest.main()
