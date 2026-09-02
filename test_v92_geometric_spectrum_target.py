import unittest

import v92_geometric_spectrum_target as target


class TestV92GeometricSpectrumTarget(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = target.build_certificate()

    def test_vector_weights(self):
        weights = target.spin11_vector_weights()
        self.assertEqual(len(weights),11)
        self.assertEqual(sum(not any(w) for w in weights),1)
        self.assertEqual([sum(w[i] for w in weights) for i in range(5)],[0]*5)

    def test_full_cartan_neutral_census(self):
        row = self.result["weight_census"]
        self.assertEqual(row["Spin11_only_zero_weight_count"],3)
        self.assertEqual(row["full_B5_U1_zero_weight_count_from_vectors"],0)
        self.assertEqual((row["neutral_under_full_Cartan"],row["charged_under_full_Cartan"],row["total_H"]),(144,156,300))

    def test_zero_u1_charge_changes_only_weight_census(self):
        row = target.weight_census([144,3,19,11,90],[0,0,0])
        self.assertEqual(row["full_B5_U1_zero_weight_count_from_vectors"],3)
        self.assertEqual(row["neutral_under_full_Cartan"],147)

    def test_hodge_target_not_old_topology(self):
        self.assertEqual(self.result["necessary_hodge_tuple"],{"h11":9,"h21":143,"Euler":-268})
        self.assertEqual(self.result["older_Spin11_only_conditional_hodge_tuple"],{"h11":8,"h21":268,"Euler":-520})
        self.assertTrue(self.result["older_tuple_cannot_be_reused_for_this_spectrum"])
        self.assertEqual(self.result["gravitational_check"],273)

    def test_height_is_conditional(self):
        row = self.result["conditional_height_class"]
        self.assertEqual(row["class_in_S_F"],[148,768])
        self.assertEqual((row["self_intersection"],row["K_intersection"],row["S_intersection"]),(139712,-1240,176))
        self.assertEqual(row["arithmetic_genus"],"69237")
        self.assertFalse(row["actual_height_pairing_constructed"])
        self.assertFalse(row["arithmetic_genus_claims_a_smooth_irreducible_height_curve"])

    def test_no_geometric_or_four_dimensional_promotion(self):
        for key in ("V91_symmetry_member_Mordell_Weil_rank_verified",
                    "V91_symmetry_member_Hodge_numbers_computed",
                    "V91_symmetry_member_realizes_scout_spectrum",
                    "geometric_target_is_existence_or_nonexistence_proof"):
            self.assertFalse(self.result[key])
        self.assertIn("before finite Higgsing",self.result["assumptions"][-1])


if __name__ == "__main__":
    unittest.main()
