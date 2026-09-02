import copy
from itertools import product
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import sympy as sp

import v97_mixed_gauge_relative_glue_audit as audit


class TestMixedGaugeRelativeGlue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()

    def test_canonical_roundtrip_and_fresh_validation(self):
        self.assertEqual(self.report, json.loads(json.dumps(self.report)))
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        audit.validate_certificate(self.report)

    def test_immutable_parent_and_helper_pins(self):
        self.assertEqual(self.report["input_core_hashes"], {
            "v96_route":audit.V96_ROUTE_CORE,"v96_master":audit.V96_MASTER_CORE,
            "v96_transport":audit.TRANSPORT_CORE,"v96_finite_inverse":audit.FINITE_CORE})
        for name in ("V96_ROUTE_CORE","V96_MASTER_CORE","TRANSPORT_CORE","FINITE_CORE"):
            with patch.object(audit,name,"0"*64):
                with self.assertRaises(RuntimeError): audit.load_inputs()
        with patch.object(audit,"portable_sha",return_value="0"*64):
            with self.assertRaises(RuntimeError): audit.load_inputs()

    def test_portable_source_hash(self):
        expected=audit.hashlib.sha256(b"first\nsecond\n").hexdigest()
        for raw in (b"first\nsecond\n",b"first\r\nsecond\r\n"):
            with patch.object(Path,"read_bytes",return_value=raw):
                self.assertEqual(audit.portable_sha(Path("unused")),expected)

    def test_rehashed_parent_tampering_fails(self):
        original=Path.read_text
        def changed(path,*args,**kwargs):
            value=original(path,*args,**kwargs)
            if path==audit.V96_ROUTE:
                report=json.loads(value)
                report["formal_combination_and_quotient_periods"]["rows"][0]["remaining_I6"]="0"
                report["core_sha256"]=audit.canonical_sha(report)
                return json.dumps(report)
            return value
        with patch.object(Path,"read_text",changed):
            with self.assertRaises(RuntimeError): audit.load_inputs()

    def test_genuine_quotient_determinant_and_reflected_line(self):
        a,b,ell=audit.a,audit.b,audit.ell
        self.assertEqual(sp.expand((a-b)+2*(ell+b)-(a+b+2*ell)),0)
        row=self.report["quotient_background_category"]
        self.assertTrue(row["reflection_preserves_determinant_relation"])
        self.assertFalse(row["local_L_character_is_a_full_Spin11_singlet_with_odd_covering_charge"])
        self.assertFalse(row["all_local_gauge_backgrounds_or_full_Gammahat_exhausted"])

    def test_K_is_an_exact_integer_index_difference(self):
        d,u=audit.d,audit.u
        self.assertEqual(sp.expand(audit.K()-(d*d*u+d*u*u)/2),0)
        self.assertEqual(sp.expand(audit.K()-audit.I(d+u)+audit.I(d)+audit.I(u)),0)

    def test_P_is_exact_primitive_virtual_index(self):
        d,u=audit.d,audit.u
        self.assertEqual(sp.expand(audit.I(2*d+u)-2*audit.I(d+u)+audit.I(u)-audit.P()),0)
        self.assertEqual(audit.virtual_chern_components(),[0,0,d*d,sp.expand(audit.P())])
        self.assertFalse(audit.P().has(audit.p))

    def test_C4_exact_generic_decomposition(self):
        self.assertEqual(sp.expand(audit.R4(audit.d-2*audit.ell,audit.c2)-audit.Z4()-audit.P()/4),0)
        self.assertNotEqual(sp.expand(audit.R4()-audit.Z4()-audit.P()/4),0)

    def test_C2_exact_generic_decomposition(self):
        self.assertEqual(sp.expand(audit.R2()-audit.Z2()+audit.P()/2),0)

    def test_frozen_remainders_rebound_and_mutation_detected(self):
        route,_=audit.load_inputs()
        result=audit.index_decomposition(route)
        self.assertEqual(len(result["all_actual_V96_remainders_rebound"]),3)
        self.assertTrue(all(row["exact_reconstruction_difference"]=="0"
                            for row in result["all_actual_V96_remainders_rebound"]))
        bad=copy.deepcopy(route)
        old=bad["formal_combination_and_quotient_periods"]["rows"][1]["remaining_I6"]
        bad["formal_combination_and_quotient_periods"]["rows"][1]["remaining_I6"]=old+"+f*p"
        with self.assertRaises(RuntimeError): audit.index_decomposition(bad)

    def test_integer_eta_levels_match_each_index_part(self):
        d,u=audit.d,audit.u
        self.assertEqual(sp.expand(17*audit.I(d+u)-5*audit.I(d)-17*audit.I(u)
                                  -12*audit.I(d)-17*audit.K()),0)
        self.assertEqual(sp.expand(audit.I(d+u)-audit.I(u)-audit.I(d)-audit.K()),0)
        row=self.report["quantized_integer_piece_responses"]
        for key in ("C4_integer_eta_levels","C2_integer_eta_levels","P_integer_eta_levels"):
            self.assertTrue(all(type(v) is int for v in row[key].values()))

    def test_all_cup_coefficients_integral(self):
        row=self.report["exact_index_decomposition"]
        for key in ("C4_integral_cup_part","C2_integral_cup_part","common_total_integral_cup_part"):
            polynomial=sp.Poly(sp.sympify(row[key]),audit.d,audit.u,audit.ell,audit.c2,
                               audit.a,audit.b,audit.A2,audit.B2)
            self.assertTrue(all(v.is_Integer for v in polynomial.coeffs()))

    def test_common_total_exact_but_requires_common_quotient_relation(self):
        a,b,A2,B2,d,ell=audit.a,audit.b,audit.A2,audit.B2,audit.d,audit.ell
        raw=audit.R4(a+b,A2+B2+a*b)+audit.R4(a-b,A2+B2-a*b)+audit.R2()
        quantized=audit.Z4(ell,A2+B2+a*b)+audit.Z4(ell+b,A2+B2-a*b)+audit.Z2()
        self.assertNotEqual(sp.expand(raw-quantized),0)
        self.assertEqual(sp.expand((raw-quantized).subs(d,a+b+2*ell)),0)

    def test_CP3_primitive_witness_and_normal_dependence(self):
        rows=self.report["primitive_period_and_order"]["rows"]
        self.assertEqual(rows[0]["R_periods"],["61/4","61/4","-1/2"])
        self.assertEqual([r["P_period"] for r in rows],["1","2","3","4"])
        self.assertEqual(rows[0]["Z_periods"],["15","15","0"])
        self.assertEqual(rows[1]["R_periods"],["25/2","25/2","-1"])
        self.assertTrue(all(sp.Rational(q).is_Integer for r in rows for q in r["Z_periods"]))

    def test_CP3_integrality_on_many_genuine_line_and_vector_bundles(self):
        # E=sum O(roots), A=first2, B=last3, d=sum roots+2ell.
        for degrees in ((1,0,0,0,0),(2,-1,1,0,-2),(1,1,1,1,1),(-3,0,2,1,0)):
            av,bv=sum(degrees[:2]),sum(degrees[2:])
            A2v=degrees[0]*degrees[1]
            B2v=sum(degrees[i]*degrees[j] for i in range(2,5) for j in range(i+1,5))
            c2v=sum(degrees[i]*degrees[j] for i in range(5) for j in range(i+1,5))
            for ellv,uv in product(range(-2,3),repeat=2):
                vals={audit.a:av,audit.b:bv,audit.A2:A2v,audit.B2:B2v,audit.t:av+bv,
                      audit.c2:c2v,audit.ell:ellv,audit.d:av+bv+2*ellv,audit.u:uv,audit.p:4}
                for q in (audit.I(audit.d),audit.K(),audit.P(),audit.Z4(),audit.Z2()):
                    self.assertTrue(sp.expand(q).subs(vals).is_Integer)

    def test_minimum_integer_multiples_from_primitive_period(self):
        row=self.report["primitive_period_and_order"]
        self.assertEqual(row["P_over4_exact_order_mod_quantized_curvatures"],4)
        for n in range(1,17):
            self.assertEqual((n*sp.Rational(61,4)).is_Integer,n%4==0)
            self.assertEqual((-n*sp.Rational(1,2)).is_Integer,n%2==0)
        self.assertFalse(row["this_is_the_order_of_the_full_Gammahat_global_anomaly"])
        self.assertFalse(row["this_is_the_same_group_as_the_2D_defect_bordism_character"])

    def test_correlated_filling_image_and_kernel(self):
        row=self.report["correlated_filling_screen"]
        tests=row["all_32_residue_tests"]
        self.assertEqual(len(tests),32)
        self.assertEqual(row["kernel_order"],8)
        self.assertEqual({r["phase"] for r in tests},{"+1","+i","-1","-i"})
        for r in tests:
            n0,n1,n2=r["independent_P_period_changes_mod_4_4_2"]
            self.assertEqual(sp.Rational(r["total_ambiguity_exponent_mod1"]),
                             sp.Rational((n0+n1-2*n2)%4,4))

    def test_diagonal_correlation_is_not_independent_gluing(self):
        row=self.report["correlated_filling_screen"]
        kernel={tuple(r) for r in row["phase_trivial_subgroup"]}
        for n in range(-12,13): self.assertIn((n%4,n%4,n%2),kernel)
        self.assertNotIn((1,0,0),kernel)
        self.assertTrue(row["diagonal_correlation_removes_this_period_ambiguity"])
        self.assertFalse(row["diagonal_correlation_is_supplied_by_existing_orbifold_action"])
        self.assertFalse(row["formal_transgression_is_a_quantized_relative_action"])

    def test_formal_carrier_full_SMW_trace(self):
        for order,w in ((4,sp.Rational(1,4)),(2,-sp.Rational(1,4))):
            row=audit.raw_carrier_profile(1,order)
            self.assertEqual(sp.sympify(row["coefficient_of_ch3"]),w)
            self.assertEqual(row["coefficient_of_x_ch2"],"0")
            self.assertEqual(sp.expand(sp.sympify(row["delta_I6"])-w*audit.P()),0)
        with self.assertRaises(ValueError): audit.raw_carrier_profile(1,8)

    def test_actual_normal_isotropy_changes_closure_and_raw_trace(self):
        row=self.report["equivariant_virtual_carrier_and_normal_lift"]["cases"]
        actual=row["actual_normal_root_uncompensated"]
        self.assertEqual(actual["H_fourth_powers"],["1","1"])
        self.assertFalse(actual["frozen_H_fourth_minus_identity_condition_passes"])
        self.assertEqual(actual["raw_stratum_profile"],["0","0","0"])
        self.assertFalse(actual["physical_sector_or_relative_action_constructed"])
        self.assertEqual(sp.simplify(audit.ZETA**3*audit.ZETA),-1)
        self.assertEqual(sp.simplify(audit.ZETA**5*audit.ZETA),-sp.I)

    def test_ordinary_C4_character_cannot_repair_closure(self):
        rows=self.report["equivariant_virtual_carrier_and_normal_lift"]["ordinary_C4_character_repairs"]
        self.assertEqual(len(rows),4)
        for r in rows:
            n=r["ordinary_C4_character_power"]
            self.assertEqual(sp.simplify((audit.ZETA**3*audit.ZETA*sp.I**n)**4),1)
            self.assertFalse(r["restores_required_minus_identity"])

    def test_projective_compensator_exact_unitary_symplectic_quaternionic(self):
        z=audit.ZETA
        F=sp.diag(1/z,z)
        J=sp.Matrix([[0,1],[-1,0]])
        for lhs,rhs in ((F.adjoint()*F,sp.eye(2)),(F.T*J*F,J),
                        (J*sp.conjugate(F)*J.inv(),F),(sp.diag(z,1/z)*F,sp.eye(2)),
                        (F**4,-sp.eye(2)),(F**8,sp.eye(2))):
            self.assertEqual((lhs-rhs).applyfunc(sp.simplify),sp.zeros(2))
        for n in range(1,8): self.assertNotEqual((F**n-sp.eye(2)).applyfunc(sp.simplify),sp.zeros(2))

    def test_compensated_formal_profile_not_promoted_to_Gammahat(self):
        row=self.report["equivariant_virtual_carrier_and_normal_lift"]
        cases=row["cases"]
        self.assertEqual(cases["independent_line_formal"],
                         cases["normal_root_with_conditional_projective_compensator"])
        self.assertFalse(row["conditional_compensator"]["ordinary_independent_C4_flavor_character"])
        self.assertFalse(row["conditional_compensator"]["compatible_full_Gammahat_kernel_representation_constructed"])
        self.assertFalse(row["negative_virtual_multiplicity_is_an_accepted_6D_SUSY_multiplet"])

    def test_finite_common_D_is_inherited_and_distinct_normal_geometries(self):
        row=self.report["compatibility_with_restricted_defect_inverse"]
        self.assertEqual(row["inherited_defect_inverse_CS_ABK_levels"],[3,3])
        self.assertEqual(row["inherited_defect_inverse_C8_character"],[12,1])
        self.assertTrue(row["same_D_line_is_available_in_both_restricted_categories"])
        self.assertFalse(row["wall_normal_root_identified_with_Phi_defect_normal_root"])
        self.assertFalse(row["degree6_response_transgressed_to_the_required_degree4_CS_ABK_functor"])

    def test_finite_integral_characteristic_class_only(self):
        row=self.report["compatibility_with_restricted_defect_inverse"]
        self.assertEqual([r["P_class_coefficient_mod8"] for r in row["all_normal_character_restrictions"]],
                         [0,4,0,4,0,4,0,4])
        for r in range(8): self.assertEqual((2**2*(2+r))%8,4*(r%2))
        self.assertEqual(row["P_integral_class_at_Mwall_trivial"],0)
        self.assertIn("No quarter-level differential refinement",row["scope_of_zero_P_class"])

    def test_curvature_response_is_not_original_global_anomaly_functor(self):
        row=self.report["quantized_integer_piece_responses"]
        self.assertTrue(row["quantized_integer_piece_responses_constructed"])
        self.assertTrue(row["negative_combined_curvature_response_on_common_product_category_constructed"])
        for key in ("same_curvature_fixes_all_flat_or_global_anomalies",
                    "combined_original_anomaly_character_proved_cancelled",
                    "integer_eta_factors_are_new_physical_Weyl_particles",
                    "full_Gammahat_descent_or_local_boundary_state_gluing_constructed"):
            self.assertFalse(row[key])

    def test_no_false_gate_or_relative_completion(self):
        self.assertTrue(all(v is False for v in self.report["limitations"].values()))
        self.assertTrue(all(r["url"].startswith("https://") for r in self.report["primary_sources"]))

    def test_rehashed_scope_and_phase_mutations_rejected(self):
        for key,value in (("same_action_parent_or_any_gate_closed",True),
                          ("normal_root_compensator_full_Gammahat_descent_proved",True)):
            bad=copy.deepcopy(self.report)
            bad["limitations"][key]=value
            bad["core_sha256"]=audit.canonical_sha(bad)
            with self.assertRaises(RuntimeError): audit.validate_certificate(bad)
        bad=copy.deepcopy(self.report)
        bad["primitive_period_and_order"]["P_over4_exact_order_mod_quantized_curvatures"]=1
        bad["core_sha256"]=audit.canonical_sha(bad)
        with self.assertRaises(RuntimeError): audit.validate_certificate(bad)


if __name__ == "__main__":
    unittest.main()
