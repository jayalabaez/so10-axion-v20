import copy
import json
import unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch

import sympy as sp

import v96_defect_relative_invertible_audit as audit


class TestRestrictedInverseResponse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = audit.build_certificate()

    def test_canonical_json_and_immutable_lineage(self):
        self.assertEqual(self.r, json.loads(json.dumps(self.r)))
        self.assertEqual(self.r["core_sha256"], audit.canonical_sha(self.r))
        self.assertEqual(self.r["input_core_hashes"], {"v95_route":audit.V95_ROUTE_CORE,
            "v95_master":audit.V95_MASTER_CORE,"v95_defect":audit.V95_DEFECT_CORE})

    def test_fresh_parent_pins_and_source_hashes(self):
        with patch.object(audit,"V95_ROUTE_CORE","0"*64):
            with self.assertRaises(RuntimeError): audit.build_certificate()
        with patch.object(audit,"V95_DEFECT_CORE","0"*64):
            with self.assertRaises(RuntimeError): audit.build_certificate()
        with patch.object(audit,"portable_sha",return_value="0"*64):
            with self.assertRaises(RuntimeError): audit.build_certificate()

    def test_LF_CRLF_hash_equivalence(self):
        for raw in (b"one\ntwo\n",b"one\r\ntwo\r\n"):
            with patch.object(Path,"read_bytes",return_value=raw):
                self.assertEqual(audit.portable_sha(Path("unused")),
                    audit.hashlib.sha256(b"one\ntwo\n").hexdigest())

    def test_AHSS_bound_and_eta_lower_bound_saturate(self):
        for n in (4,8):
            row=self.r["restricted_bordism_classification"]["C"+str(n)]
            upper=1
            for entry in row["AHSS_total_degree3_E2"]: upper*=entry["order"]
            self.assertEqual(upper,4*n)
            self.assertEqual(row["distinct_probe_products_from_eta_evaluations"],upper)
            alpha,beta=audit.complex_character(n,1),audit.sign_character(n)
            values={(audit.character_exponent(n,audit.add_characters(n,(a,alpha),(b,beta)),(1,0)),
                     audit.character_exponent(n,audit.add_characters(n,(a,alpha),(b,beta)),(0,1)))
                    for a in range(2*n) for b in range(2)}
            self.assertEqual(len(values),upper)

    def test_actual_probe_values_independent_of_group_dictionary(self):
        for n in (4,8):
            lens=-audit.parent.lens_rho(n,1)
            self.assertEqual((lens%1).denominator,2*n)
            self.assertEqual(audit.torus_rho(n,1),-1)
            self.assertEqual(audit.torus_rho(n,n//2),-1)
            self.assertEqual((-audit.torus_rho(n,1))%1,0)
            self.assertEqual((-audit.torus_rho(n,n//2)/2)%1,F(1,2))

    def test_lens_exact_spectral_sum_both_spin_lifts(self):
        for n in (4,8):
            for spin in (0,n//2):
                for q in range(n):
                    self.assertEqual(audit.parent.lens_xi(n,q,spin),
                                     audit.parent.lens_xi_from_sum(n,q,spin))

    def test_probe_character_orders_and_group_basis(self):
        self.assertEqual(audit.character_order(4,audit.complex_character(4,1)),8)
        self.assertEqual(audit.character_order(8,audit.complex_character(8,1)),16)
        self.assertEqual(audit.character_order(4,audit.sign_character(4)),4)
        self.assertEqual(audit.character_order(8,audit.sign_character(8)),2)
        for n in (4,8):
            chars=[audit.complex_character(n,1),audit.sign_character(n)]
            self.assertTrue(all(audit.character_exponent(n,c,(2*n,0))==0 for c in chars))
            self.assertTrue(all(audit.character_exponent(n,c,(0,2))==0 for c in chars))
            self.assertFalse(any(all(audit.character_exponent(n,c,(a,0))==
                                     audit.character_exponent(n,c,(0,1)) for c in chars)
                                 for a in range(2*n)))

    def test_defect_and_inverse_coordinates(self):
        self.assertEqual(audit.defect_character(4),(1,1))
        self.assertEqual(audit.defect_character(8),(4,1))
        self.assertEqual(audit.inverse_response_character(4),(7,1))
        self.assertEqual(audit.inverse_response_character(8),(12,1))

    def test_minimal_stacking_orders_are_exact(self):
        for n,order in ((4,8),(8,4)):
            c=audit.defect_character(n)
            self.assertEqual(audit.character_order(n,c),order)
            self.assertEqual(audit.add_characters(n,(order,c)),(0,0))
            for k in range(1,order): self.assertNotEqual(audit.add_characters(n,(k,c)),(0,0))

    def test_other_lens_spin_structure_classes(self):
        data=self.r["restricted_bordism_classification"]
        self.assertEqual(data["C4"]["opposite_lens_spin_lift_bordism_coordinates"],[5,1])
        self.assertEqual(data["C8"]["opposite_lens_spin_lift_bordism_coordinates"],[9,0])
        for n in (4,8):
            canonical=audit.parent.anomaly_row(audit.parent.lens_rho(n,n//4),
                                               audit.parent.lens_rho(n,n//2))
            other=audit.parent.anomaly_row(audit.parent.lens_rho(n,n//4,n//2),
                                          audit.parent.lens_rho(n,n//2,n//2))
            self.assertEqual(canonical["bare_log_phase_over_2pi_i_mod1"],
                             other["bare_log_phase_over_2pi_i_mod1"])

    def test_C8_C4_representation_pullback_and_bordism_map(self):
        row=self.r["effective_C4_pullback"]
        self.assertEqual(row["image_L8"],[2,0])
        self.assertEqual(row["image_T8"],[0,1])
        for q in range(4):
            c4=audit.complex_character(4,q)
            c8=audit.complex_character(8,2*q)
            self.assertEqual(c8,(4*c4[0]%16,c4[1]))
        self.assertEqual(audit.sign_character(8),(4*audit.sign_character(4)[0]%16,
                                                audit.sign_character(4)[1]))
        for row in row["all_bordism_images"]:
            e8,e4=tuple(row["C8_bordism"]),tuple(row["C4_bordism"])
            self.assertEqual(audit.character_exponent(8,audit.defect_character(8),e8),
                             audit.character_exponent(4,audit.defect_character(4),e4))

    def test_map_kernel_image_and_inverse_extension_ambiguity(self):
        row=self.r["effective_C4_pullback"]
        self.assertEqual(row["image_order"],8)
        self.assertEqual(row["kernel"],[[0,0],[4,0],[8,0],[12,0]])
        self.assertEqual(row["character_pullback_kernel"],[[0,0],[4,0]])
        self.assertEqual(row["inverse_C4_preimages_of_actual_C8_inverse"],[[3,1],[7,1]])
        self.assertEqual(row["four_copies_C4_bare_remaining_character"],[4,0])
        self.assertTrue(row["four_copies_C8_bare_trivial"])

    def test_spin_CS_charge_quadratic_law_and_orientation(self):
        for n in (4,8):
            for spin in (0,n//2):
                for q in range(n):
                    self.assertEqual((audit.parent.lens_rho(n,q,spin)-
                        q*q*audit.parent.lens_rho(n,1,spin))%1,0)
            for q in range(n):
                self.assertEqual((audit.torus_rho(n,q)-q*q*audit.torus_rho(n,1))%1,0)

    def test_ABK_RP2_and_odd_torus_Gauss_sums(self):
        rp2=sp.simplify(sum(sp.I**q for q in (0,1))/sp.sqrt(2))
        odd=sp.Rational(sum(sp.I**q for q in (0,2,2,2)),2)
        self.assertEqual(sp.simplify(rp2-sp.sqrt(2)*(1+sp.I)/2),0)
        self.assertEqual(odd,-1)
        self.assertEqual(audit.parent.lens_rho(2,1)/2,F(1,8))
        row=self.r["quantized_inverse_response"]["ABK_calibration_checks"]
        self.assertEqual(row["RP2_ABK_mod8"],1)
        self.assertEqual(row["odd_T2_ABK_mod8"],4)

    def test_ABK_pullback_restricted_value_sets(self):
        data=self.r["restricted_bordism_classification"]
        self.assertEqual(data["C4"]["ABK_values_mod8_on_all_bordism_classes"],[0,2,4,6])
        self.assertEqual(data["C8"]["ABK_values_mod8_on_all_bordism_classes"],[0,4])

    def test_real_half_before_reduction_essential_to_response(self):
        full=audit.parent.lens_rho(8,4)
        self.assertEqual(full,1)
        self.assertNotEqual((full/2)%1,((full%1)/2)%1)
        self.assertEqual(audit.sign_character(8),(8,1))
        wrong=audit.coordinates(8,-(full%1)/2,-(audit.torus_rho(8,4)%1)/2)
        self.assertEqual(wrong,(0,0))

    def test_torus_spin_compensator_retains_sign(self):
        for n in (4,8):
            for circle_spin in (0,1):
                weighted=3*audit.torus_rho(n,n//4,circle_spin)+F(3,2)*audit.torus_rho(n,n//2,circle_spin)
                self.assertEqual((-weighted)%1,F(1,2))
        row=self.r["inherited_restricted_model"]
        self.assertIn("induced spin=s+a2",row["tangent_spin_compensation"])
        self.assertFalse(row["k_squared_is_total_fermion_parity"])

    def test_inverse_response_cancels_every_restricted_class(self):
        for n in (4,8):
            rows=self.r["complete_restricted_character_cancellation"]["C"+str(n)]["rows"]
            self.assertEqual(len(rows),4*n)
            self.assertEqual(len({tuple(row["bordism_coordinates"]) for row in rows}),4*n)
            for row in rows:
                self.assertEqual((F(row["bare_exponent_mod1"])+F(row["CS_ABK_inverse_exponent_mod1"]))%1,0)
                self.assertEqual(row["total_exponent_mod1"],"0")

    def test_lens_and_torus_match_F95_frozen_targets(self):
        c8=self.r["complete_restricted_character_cancellation"]["C8"]
        self.assertEqual((c8["bare_lens_phase"],c8["inverse_lens_phase"]),("+i","-i"))
        self.assertEqual((c8["bare_T_phase"],c8["inverse_T_phase"]),("-1","-1"))
        c4=self.r["complete_restricted_character_cancellation"]["C4"]
        self.assertEqual(c4["bare_lens_phase"],"exp(2*pi*i*1/8)")
        self.assertEqual(c4["inverse_lens_phase"],"exp(2*pi*i*7/8)")

    def test_orientation_reversal_conjugates_both_characters(self):
        for n in (4,8):
            bare=audit.add_characters(n,(-1,audit.defect_character(n)))
            inverse=audit.add_characters(n,(-1,audit.inverse_response_character(n)))
            self.assertEqual(audit.add_characters(n,(1,bare),(1,inverse)),(0,0))

    def test_quantized_levels_and_CS_only_failure(self):
        row=self.r["fermionic_quantization_screen"]
        self.assertEqual(row["level_classes"]["C4"]["matching_CS_ABK_level_pairs_mod_these_periods"],[[3,3],[7,1]])
        self.assertEqual(row["level_classes"]["C8"]["matching_CS_ABK_level_pairs_mod_these_periods"],[[3,1]])
        for n in (4,8):
            for level in range(2*n):
                c=audit.inverse_response_character(n,level,0)
                self.assertEqual(audit.character_exponent(n,c,(0,1)),0)
                self.assertNotEqual(c,audit.add_characters(n,(-1,audit.defect_character(n))))
        self.assertFalse(row["CS_only_inverse_possible"])
        self.assertFalse(row["bosonic_DW_only_inverse_possible"])

    def test_integer_CS_level_spin_periods(self):
        for a in range(-7,8):
            for b in range(-7,8):
                period=F(3,2)*(2*a*b)
                self.assertEqual(period.denominator,1)
        self.assertEqual(self.r["quantized_inverse_response"]["CS_level_for_D"],3)
        self.assertEqual(self.r["quantized_inverse_response"]["equivalent_CS_level_for_C8_covering_unit_line"],12)

    def test_background_response_not_dynamical_CS_or_same_action(self):
        row=self.r["quantized_inverse_response"]
        self.assertTrue(row["background_connection_is_not_integrated_over"])
        self.assertTrue(row["quantized_abstract_restricted_inverse_response_constructed"])
        self.assertFalse(row["this_is_dynamical_U1_level3_CS_with_anyons"])
        self.assertFalse(row["actual_same_action_bulk_inflow_constructed"])
        self.assertIn("not been identified",row["auxiliary_ABK_surface_scope"])

    def test_no_full_Gamma_or_gravitational_promotion(self):
        self.assertTrue(all(value is False for value in self.r["limitations"].values()))
        self.assertEqual(self.r["normalization"]["remaining_pure_gravitational_central_charge"],"9/2")
        self.assertFalse(self.r["normalization"]["physical_pure_gravitational_anomaly_cancelled"])
        self.assertFalse(self.r["inherited_restricted_model"]["full_Gammahat_replaced_by_Spin_times_C8"])

    def test_unit_charge_probe_not_new_parent_singlet(self):
        row=self.r["restricted_bordism_classification"]["C8"]["probe_definitions"]
        self.assertFalse(row["unit_C8_probe_added_to_physical_parent_spectrum"])
        self.assertIn("q1 Spin11-singlet does NOT descend",row["unit_charge_probe_scope"])
        self.assertIn("D=rho2",self.r["quantized_inverse_response"]["covering_unit_line_scope"])

    def test_bad_domain_and_noninteger_levels_fail_closed(self):
        for n in (2,3,16,True):
            with self.assertRaises(ValueError): audit.bordism_classification(n)
        with self.assertRaises(ValueError): audit.inverse_response_character(8,F(1,2),3)
        with self.assertRaises(ValueError): audit.inverse_response_character(8,3,True)
        with self.assertRaises(ValueError): audit.torus_rho(8,True)
        with self.assertRaises(ValueError): audit.coordinates(8,F(1,3),0)
        with self.assertRaises(ValueError): audit.character_exponent(8,(True,0),(1,0))

    def test_rehashed_wrong_group_order_rejected(self):
        changed=copy.deepcopy(self.r)
        changed["restricted_bordism_classification"]["C8"]["order"]=16
        changed["core_sha256"]=audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError): audit.validate_certificate(changed)

    def test_rehashed_same_action_promotion_rejected(self):
        changed=copy.deepcopy(self.r)
        changed["limitations"]["actual_same_action_bulk_defect_inflow_constructed"]=True
        changed["core_sha256"]=audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError): audit.validate_certificate(changed)

    def test_rehashed_wrong_ABK_level_rejected(self):
        changed=copy.deepcopy(self.r)
        changed["quantized_inverse_response"]["ABK_level_mod8"]=0
        changed["core_sha256"]=audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError): audit.validate_certificate(changed)


if __name__ == "__main__":
    unittest.main()
