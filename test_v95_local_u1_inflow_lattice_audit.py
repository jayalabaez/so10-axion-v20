import copy
import unittest

import sympy as sp
import v95_local_u1_inflow_lattice_audit as audit


class TestV95LocalU1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=audit.build_certificate()

    def test_core_and_lineage(self):
        self.assertEqual(self.report["core_sha256"],audit.common.canonical_sha(self.report))
        self.assertEqual(self.report["input_core_hashes"],{k:v[1] for k,v in audit.PARENTS.items()})

    def test_all_integer_charges_obey_lattice(self):
        for q in range(-50,51):
            self.assertTrue(audit.lies_in_enlarged_Weyl_lattice(q,q**3))
            n1,n2=audit.lattice_coordinates(q,q**3)
            self.assertEqual((n1+2*n2,n1+8*n2),(q,q**3))

    def test_basis_determinant(self):
        self.assertEqual(sp.Matrix([[1,2],[1,8]]).det(),6)

    def test_converse_signed_basis(self):
        for n1 in range(-5,6):
            for n2 in range(-5,6):
                self.assertEqual(audit.lattice_coordinates(n1+2*n2,n1+8*n2),(n1,n2))

    def test_C4_fractional_trace(self):
        rows=self.report["physical_fixed_loci"][:2]
        self.assertTrue(all((r["TrQ"],r["TrQ3"])==("47/2","754") for r in rows))
        self.assertTrue(all(r["coordinates_mod_one"]==["0","3/4"] for r in rows))

    def test_physical_C2_not_cover_half(self):
        row=self.report["physical_fixed_loci"][2]
        self.assertEqual((row["TrQ"],row["TrQ3"]),("3","-60"))
        self.assertEqual(row["coordinates_mod_one"],["0","1/2"])

    def test_every_local_class_is_outside_lattice(self):
        self.assertTrue(all(not r["is_ordinary_Weyl_polynomial"] for r in self.report["physical_fixed_loci"]))

    def test_no_finite_integer_wall_shift_removes_class(self):
        for row in self.report["physical_fixed_loci"]:
            a,b=sp.Rational(row["TrQ"]),sp.Rational(row["TrQ3"])
            for q in range(-8,9):
                self.assertFalse(audit.lies_in_enlarged_Weyl_lattice(a+q,b+q**3))

    def test_CP3_periods(self):
        self.assertEqual([r["CP3_index_period"] for r in self.report["physical_fixed_loci"]],["487/4","487/4","-21/2"])
        for q in range(-20,21):
            self.assertEqual(audit.cp3_index_period(audit.weyl_index(q)),sp.Rational(q**3-q,6))

    def test_formal_transfer_zero_sum(self):
        rows=self.report["formal_zero_sum_inflow_target"]["rows"]
        self.assertEqual(sp.expand(sum(sp.sympify(r["formal_inflow_polynomial"]) for r in rows)),0)

    def test_transferred_local_moments(self):
        rows=self.report["formal_zero_sum_inflow_target"]["rows"]
        self.assertEqual([r["shifted_TrQ_TrQ3"] for r in rows],[["24","756"],["24","756"],["2","-64"]])

    def test_transferred_periods_integral(self):
        rows=self.report["formal_zero_sum_inflow_target"]["rows"]
        self.assertEqual([r["shifted_CP3_period"] for r in rows],["122","122","-11"])

    def test_global_moments_and_period(self):
        row=self.report["global_crosscheck"]
        self.assertEqual(row["TrQ_TrQ3"],[50,1448])
        self.assertEqual(row["CP3_period"],"233")
        self.assertFalse(row["integrated_bulk_anomaly_is_zero"])

    def test_no_false_quantization(self):
        row=self.report["formal_zero_sum_inflow_target"]
        self.assertEqual(row["minimum_common_denominator_in_enlarged_lattice"],4)
        self.assertFalse(row["quantized_bulk_tensor_or_relative_differential_action_constructed"])
        self.assertFalse(row["all_mixed_Spin11_normal_or_R_anomalies_cancelled"])

    def test_enlarged_lattice_not_actual_field_construction(self):
        row=self.report["ordinary_Weyl_lattice"]
        self.assertFalse(row["charge1_generator_is_an_allowed_Spin_c11_gauge_singlet"])
        self.assertFalse(row["enlarged_lattice_success_constructs_actual_wall_representations"])

    def test_visible_not_cancelled_by_redistribution(self):
        row=self.report["global_crosscheck"]
        self.assertEqual(row["full_visible_TrQ_TrQ3_unchanged"],[-68,1408])
        self.assertFalse(row["zero_sum_transfer_cancels_full_visible_anomaly"])

    def test_bad_polynomial_rejected(self):
        with self.assertRaises(ValueError):
            audit.moments(audit.f**2)

    def test_rehashed_arithmetic_forgery_rejected(self):
        changed=copy.deepcopy(self.report)
        changed["physical_fixed_loci"][0]["TrQ"]="0"
        changed["core_sha256"]=audit.common.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(changed)

    def test_rehashed_gate_promotion_rejected(self):
        changed=copy.deepcopy(self.report)
        changed["terminal_decision"]["closed_gates"]=["G1"]
        changed["core_sha256"]=audit.common.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(changed)


if __name__=="__main__":
    unittest.main()
