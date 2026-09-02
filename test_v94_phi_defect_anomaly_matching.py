import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

import sympy as sp

import v94_phi_defect_anomaly_matching as audit


class TestPhiDefectMatching(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()

    def test_canonical_json_and_lineage(self):
        r = self.report
        self.assertEqual(r,json.loads(json.dumps(r)))
        self.assertEqual(r["core_sha256"],audit.canonical_sha(r))
        self.assertEqual(r["input_core_hashes"],{"v93_route":audit.V93_CORE,"v93_mass":audit.MASS_CORE})

    def test_mass_matrix_rank_and_symmetric_winding(self):
        phi = sp.symbols("Phi")
        M = audit.mass_matrix(phi)
        self.assertEqual(M,M.T)
        self.assertEqual(M.det(),-phi**9)
        self.assertEqual(M.subs(phi,1).rank(),9)
        self.assertEqual(M.subs(phi,0).rank(),0)

    def test_general_tensor_determinant_and_singular_boundary(self):
        phi = sp.symbols("Phi")
        for L,K in ((sp.diag(2,3,5),sp.diag(7,11,13)),
                    (sp.Matrix([[1,2,3],[0,4,5],[0,0,6]]),sp.Matrix([[2,1,0],[1,3,1],[0,1,2]])),
                    (sp.diag(1,1,0),sp.eye(3))):
            self.assertEqual(sp.expand(audit.mass_matrix(phi,L,K).det()+phi**9*L.det()**2*K.det()),0)
        self.assertLess(audit.mass_matrix(1,sp.diag(1,1,0),sp.eye(3)).rank(),9)

    def test_invalid_mass_tensor_rejected(self):
        with self.assertRaises(ValueError):
            audit.mass_matrix(1,sp.eye(2),sp.eye(3))
        with self.assertRaises(ValueError):
            audit.mass_matrix(1,sp.eye(3),sp.Matrix([[1,2,0],[0,1,0],[0,0,1]]))

    def test_real_versus_complex_index(self):
        for n in range(-4,5):
            r = audit.winding_index(n)
            self.assertEqual(r["signed_total_real_index"],2*r["signed_complex_channel_index"]+r["signed_real_Majorana_channel_index"])
            self.assertEqual(r["signed_total_real_index"],9*n)
            self.assertEqual(sp.Rational(r["signed_chiral_central_charge"]),sp.Rational(9*n,2))
            self.assertEqual(sp.Rational(r["signed_gravitational_I4_coefficient_p1T"]),-sp.Rational(3*n,16))
        for bad in (True,1.0,"1",sp.Rational(1,2)):
            with self.assertRaises(ValueError):
                audit.winding_index(bad)

    def test_index_is_conditional_not_full_kernel(self):
        r = self.report["mass_and_index"]
        self.assertTrue(r["net_index_not_absolute_kernel_count"])
        self.assertFalse(r["full_SUGRA_gravitino_gaugino_or_KK_operator_index_computed"])
        self.assertFalse(r["dynamically_stable_vortex_or_cosmological_abundance_constructed"])

    def test_quotient_line_powers_and_global_patch_condition(self):
        r = self.report["topological_patch_constraints"]
        self.assertEqual(r["field_line_powers_of_D"],{"S2":1,"S4":2,"S6":3,"Phi_minus":-4})
        self.assertTrue(r["no_independent_square_root_of_D_required"])
        self.assertIn("4*d=0",r["global_nonvanishing_condition"])
        self.assertFalse(r["torsion_or_discrete_flat_data_removed_by_deRham_f_zero"])

    def test_defect_normal_is_not_orbifold_normal(self):
        r = self.report["topological_patch_constraints"]["oriented_simple_zero_surface"]
        self.assertFalse(r["normal_is_six_dimensional_orbifold_normal"])
        self.assertEqual(r["normal_spin_root"],"N^(1/2)=D^-2 restricted to Sigma")
        self.assertIn("N^n",self.report["topological_patch_constraints"]["higher_multiplicity_boundary"])

    def test_closed_spin_global_zero_class_witness(self):
        r = self.report["topological_patch_constraints"]["topological_witness"]
        self.assertEqual(r["total_self_intersection"],16*r["integral_d_squared"])
        self.assertEqual(r["total_self_intersection"]%32,0)
        period=-sp.Rational(9,2)*r["integral_d_squared"]+sp.Rational(3,16)*r["integral_p1T4"]
        self.assertEqual(period,r["Phi_phase_curvature_period"])
        self.assertFalse(r["holomorphic_or_BPS_section_asserted"])

    def test_spin_normal_component_tensor_products(self):
        r = self.report["unit_defect_curvature_matching"]["spinor_bundle_derivation"]
        self.assertEqual([r[k] for k in ("S2_spin_normal_power","conjugate_S6_spin_normal_power","S4_spin_normal_power")],[-1,-1,0])
        self.assertTrue(r["fractional_normal_charge_needs_mass_determined_fourth_root"])
        self.assertFalse(r["ordinary_SO2_normal_representations_with_no_extension_claimed"])

    def test_independent_degree_four_anomaly_calculation(self):
        d,pT=sp.symbols("d pT")
        r = self.report["unit_defect_curvature_matching"]
        independently=3*(d*d/2-pT/24)+3*(-pT/48)
        self.assertEqual(sp.expand(sp.sympify(r["defect_I4"])-independently),0)
        self.assertEqual(sp.expand(sp.sympify(r["restricted_phase_coefficient"])+independently),0)

    def test_normal_curvature_term_is_essential(self):
        d,pT=sp.symbols("d pT")
        B_without_normal=-sp.Rational(9,2)*d*d+sp.Rational(3,16)*pT
        I4=sp.Rational(3,2)*d*d-sp.Rational(3,16)*pT
        self.assertEqual(sp.expand(B_without_normal+I4),-3*d*d)
        self.assertNotEqual(sp.expand(B_without_normal+I4),0)

    def test_euler_and_character_independent_checks(self):
        r = self.report["unit_defect_curvature_matching"]
        self.assertEqual(r["Euler_residue_exact_difference"],"0")
        self.assertTrue(r["odd_character_identity_verified"])
        d,pT=sp.symbols("d pT")
        I6=18*d**3-sp.Rational(3,4)*d*(pT+16*d*d)
        I4=sp.Rational(3,2)*d*d-sp.Rational(3,16)*pT
        self.assertEqual(sp.expand(I6-4*d*I4),0)

    def test_primitive_C8_Majorana_sign_not_lost(self):
        r=self.report["finite_lift_bookkeeping"]
        self.assertEqual(r["complex_mode_component_exponents_mod8"],[2,2])
        self.assertEqual(r["real_mode_component_exponents_mod8"],[4,4])
        self.assertFalse(r["Majorana_mode_is_neutral_under_primitive_k"])
        self.assertFalse(r["k_squared_is_total_fermion_parity"])
        split=r["spin_split_bookkeeping_exponents_mod8"]
        self.assertEqual((split["complex_coefficient_D_minus1"]+split["induced_tangent_spin_compensator"])%8,2)
        self.assertEqual((split["real_coefficient"]+split["induced_tangent_spin_compensator"])%8,4)

    def test_R_and_wall_lifts_inherited_not_invented(self):
        r=self.report["topological_patch_constraints"]["inherited_R_and_wall_data"]
        self.assertEqual(r["Phi_scalar_independent_R4_charge"],0)
        self.assertEqual(r["heavy_fermion_independent_R4_charges"],[0]*9)
        self.assertEqual(r["orbifold_wall_characters_of_selected_Phi"],["1"]*4)
        self.assertFalse(r["new_assignment_of_unfrozen_wall_normal_charges"])

    def test_no_global_or_quantum_promotion(self):
        self.assertTrue(all(value is False for value in self.report["limitations"].values()))
        r=self.report["unit_defect_curvature_matching"]
        self.assertFalse(r["bump_form_profile_or_connection_level_transgression_constructed"])
        self.assertFalse(r["full_inflow_sign_and_Pfaffian_orientation_fixed_on_all_relative_backgrounds"])
        self.assertFalse(self.report["finite_lift_bookkeeping"]["C8_or_Gammahat_eta_invariant_computed"])

    def test_portable_source_hash_CRLF(self):
        for data in (b"a\nb\n",b"a\r\nb\r\n"):
            with patch.object(Path,"read_bytes",return_value=data):
                self.assertEqual(audit.portable_file_sha(Path("unused")),audit.hashlib.sha256(b"a\nb\n").hexdigest())

    def test_parent_binding_fresh(self):
        with patch.object(audit,"V93_CORE","0"*64):
            with self.assertRaises(RuntimeError):
                audit.build_certificate()
        with patch.object(audit,"portable_file_sha",return_value="0"*64):
            with self.assertRaises(RuntimeError):
                audit.build_certificate()

    def test_rehashed_false_promotion_rejected(self):
        changed=copy.deepcopy(self.report)
        changed["limitations"]["same_action_theory_or_any_gate_closed"]=True
        changed["core_sha256"]=audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(changed)

    def test_changed_parent_phase_rejected(self):
        _,mass=audit.load_inputs()
        mass["mass_anomaly_matching"]["local_IR_matching_log_phase_over_2pi_i"]="-18*phi*x**2"
        with self.assertRaises(RuntimeError):
            audit.unit_defect_curvature_matching(mass)


if __name__ == "__main__":
    unittest.main()
