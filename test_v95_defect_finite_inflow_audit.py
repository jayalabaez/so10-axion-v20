import copy
import json
import unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch

import v95_defect_finite_inflow_audit as audit


class TestDefectFiniteInflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = audit.build_certificate()

    def test_canonical_and_immutable_lineage(self):
        self.assertEqual(self.r, json.loads(json.dumps(self.r)))
        self.assertEqual(self.r["core_sha256"], audit.canonical_sha(self.r))
        self.assertEqual(self.r["input_core_hashes"], {"v94_route": audit.V94_ROUTE_CORE,
            "v94_master": audit.V94_MASTER_CORE, "v94_defect": audit.V94_DEFECT_CORE})

    def test_exact_lens_sum_independent_of_polynomial(self):
        for n in (2, 4, 8):
            for spin in (0, n//2):
                for q in range(n):
                    self.assertEqual(audit.lens_xi(n,q,spin), audit.lens_xi_from_sum(n,q,spin))

    def test_periodic_and_conjugate_characters(self):
        for n in (2,4,8):
            for spin in (0,n//2):
                for q in range(n):
                    self.assertEqual(audit.lens_rho(n,q,spin),audit.lens_rho(n,q+3*n,spin))
                    self.assertEqual(audit.lens_rho(n,q,spin),audit.lens_rho(n,-q,spin))

    def test_exact_canonical_lens_values(self):
        self.assertEqual([audit.lens_xi(8,q) for q in (0,2,4,6)],
                         [F(-21,32),F(3,32),F(11,32),F(3,32)])
        self.assertEqual(audit.lens_rho(8,2),F(3,4))
        self.assertEqual(audit.lens_rho(8,4),1)

    def test_second_spin_structure_full_values(self):
        self.assertEqual(audit.lens_rho(8,2,4),F(-1,4))
        self.assertEqual(audit.lens_rho(8,4,4),-1)
        self.assertEqual(audit.anomaly_row(F(3,4),1)["weighted_xi_exact"],"15/4")
        self.assertEqual(audit.anomaly_row(F(-1,4),-1)["weighted_xi_exact"],"-9/4")

    def test_primitive_lens_phases_both_spin_lifts(self):
        rows=self.r["lens_C8_witnesses"]["all_holonomies_and_both_spin_lifts"]
        for row in rows:
            self.assertEqual(row["bare_phase"],"+i" if row["holonomy_power"]%2 else "+1")
            self.assertEqual(row["required_inverse_inflow_phase"],"-i" if row["holonomy_power"]%2 else "+1")

    def test_real_half_cannot_use_mod_one_rho(self):
        good=audit.anomaly_row(F(3,4),F(1))
        bad=audit.anomaly_row(F(3,4),F(1)%1)
        self.assertEqual(good["bare_phase"],"+i")
        self.assertEqual(bad["bare_phase"],"-i")
        self.assertNotEqual(good["bare_phase"],bad["bare_phase"])

    def test_single_RP3_Majorana_order_eight(self):
        row=self.r["normalization"]["single_RP3_sign_Majorana_calibration"]
        self.assertEqual(row["real_complexified_rho_exact"],"1/4")
        self.assertEqual(row["bare_log_phase_over_2pi_i_mod1"],"7/8")
        self.assertEqual(audit.anomaly_row(0,F(1,4),0,8)["bare_phase"],"+1")

    def test_torus_exact_kernel_is_retained(self):
        self.assertEqual(audit.torus_spectrum(0)["complex_kernel_dimension"],2)
        self.assertEqual(audit.torus_spectrum(0)["xi_exact"],"1")
        self.assertEqual(audit.torus_spectrum(2)["complex_kernel_dimension"],0)
        self.assertEqual(audit.torus_spectrum(4)["complex_kernel_dimension"],0)
        self.assertEqual(audit.torus_spectrum(4,circle_spin=1)["complex_kernel_dimension"],2)

    def test_torus_primitive_phase_not_complex_mod_one(self):
        rows=self.r["torus_C8_Pfaffian_witnesses"]["all_holonomies_and_circle_spins"]
        for row in rows:
            self.assertEqual(row["bare_phase"],"-1" if row["holonomy_power"]%2 else "+1")
            self.assertEqual(row["required_inverse_inflow_phase"],row["bare_phase"])
        primitive=next(row for row in rows if row["holonomy_power"]==1 and row["circle_spin"]=="R")
        self.assertEqual(primitive["weighted_xi_exact"],"-9/2")
        self.assertEqual(primitive["bare_phase"],"-1")
        self.assertEqual(audit.anomaly_row(-1,-1,3,0)["bare_phase"],"+1")

    def test_character_tensor_products_for_every_k(self):
        for row in self.r["restricted_spin_and_gauge_lift"]["character_table_mod8"]:
            h=row["power_of_k"]
            self.assertEqual(row["normal_spin_root"],row["tangent_spin_compensator"])
            self.assertEqual((row["normal_spin_root"]+row["tangent_spin_compensator"])%8,0)
            self.assertEqual(row["N_D_minus4"],0)
            self.assertEqual(row["physical_complex"],2*h%8)
            self.assertEqual(row["physical_real"],4*h%8)

    def test_restricted_lift_no_false_tangent_quotient(self):
        row=self.r["restricted_spin_and_gauge_lift"]
        self.assertFalse(row["k_squared_is_total_fermion_parity"])
        self.assertFalse(row["full_Gammahat_map_or_fixed_wall_extension_constructed"])
        self.assertFalse(row["normal_is_six_dimensional_orbifold_normal"])
        self.assertIn("s+a2",row["physical_complex_bundle"])

    def test_spin_split_eta_identity_not_just_local_polynomial(self):
        for row in self.r["spin_split_global_identity"]["lens_exact_checks"]:
            self.assertEqual(F(row["induced_spin_D_minus1_gauge_piece"])+F(row["nine_real_rank_spin_change_piece"]),
                             F(row["physical_weighted_xi"]))
            self.assertEqual(row["exact_difference"],"0")
            self.assertNotEqual(row["incorrect_no_compensator_bare_phase"],row["correct_bare_phase"])

    def test_wrong_neutral_Majorana_loses_torus_sign(self):
        row=self.r["spin_split_global_identity"]
        self.assertEqual(row["primitive_T3_induced_gauge_piece"],"0")
        self.assertEqual(row["primitive_T3_spin_change_piece_for_R_circle"],"-9/2")
        self.assertNotEqual(row["wrong_neutral_Majorana_T3_phase"],row["correct_T3_phase"])

    def test_orientation_and_inverse_targets(self):
        for row in self.r["lens_C8_witnesses"]["all_holonomies_and_both_spin_lifts"]:
            total=F(row["bare_log_phase_over_2pi_i_mod1"])+F(row["required_inverse_inflow_exponent_mod1"])
            self.assertEqual(total%1,0)
            self.assertEqual(row["opposite_orientation_or_chirality_bare_phase"],row["required_inverse_inflow_phase"])
        self.assertFalse(self.r["lens_C8_witnesses"]["full_relative_action_orientation_dictionary_fixed"])

    def test_no_pure_gravity_or_total_theory_promotion(self):
        self.assertFalse(self.r["normalization"]["pure_gravitational_anomaly_physically_cancelled_by_subtraction"])
        self.assertTrue(all(value is False for value in self.r["limitations"].values()))
        self.assertFalse(self.r["inflow_obligation"]["V94_local_curvature_matching_retracted"])
        self.assertFalse(self.r["inflow_obligation"]["bare_defect_is_anomaly_free_on_the_two_test_families"])

    def test_bad_arguments_rejected(self):
        for args in ((3,1,0),(8,1,1),(8,True,0),(True,1,0)):
            with self.assertRaises(ValueError): audit.lens_xi(*args)
        for args in ((0,1,2),(True,1,0),(0,False,0)):
            with self.assertRaises(ValueError): audit.torus_spectrum(*args)
        with self.assertRaises(ValueError): audit.anomaly_row(0,0,real_count=-1)

    def test_fresh_parent_pin_and_source_binding(self):
        with patch.object(audit,"V94_ROUTE_CORE","0"*64):
            with self.assertRaises(RuntimeError): audit.build_certificate()
        with patch.object(audit,"portable_sha",return_value="0"*64):
            with self.assertRaises(RuntimeError): audit.build_certificate()

    def test_portable_LF_CRLF_hash(self):
        for raw in (b"a\nb\n",b"a\r\nb\r\n"):
            with patch.object(Path,"read_bytes",return_value=raw):
                self.assertEqual(audit.portable_sha(Path("unused")),audit.hashlib.sha256(b"a\nb\n").hexdigest())

    def test_rehashed_false_promotion_rejected(self):
        changed=copy.deepcopy(self.r)
        changed["limitations"]["full_physical_relative_Dai_Freed_trivialization_constructed"]=True
        changed["core_sha256"]=audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError): audit.validate_certificate(changed)

    def test_rehashed_wrong_Pfaffian_phase_rejected(self):
        changed=copy.deepcopy(self.r)
        changed["torus_C8_Pfaffian_witnesses"]["primitive_holonomy_bare_phase"]="+1"
        changed["core_sha256"]=audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError): audit.validate_certificate(changed)


if __name__ == "__main__":
    unittest.main()
