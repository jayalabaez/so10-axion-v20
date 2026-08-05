#!/usr/bin/env python3
import unittest

import g1_exact_renormalizable_character_census_v20 as census


class ExactG1CharacterCensusTests(unittest.TestCase):
    def test_fundamental_character_dimensions(self):
        self.assertEqual(census.character_dimension(census.vector_character()), 10)
        self.assertEqual(census.character_dimension(census.chiral_spinor_character()), 16)
        self.assertEqual(census.character_dimension(census.rep126_character()), 126)
        self.assertEqual(census.character_dimension(census.rep126bar_character()), 126)
        self.assertEqual(census.character_dimension(census.rep210_character()), 210)

    def test_known_pure_rep_singlet_multiplicities(self):
        self.assertEqual(census.singlet_multiplicity(census.symmetric_rep_character("H", 2)), 1)
        self.assertEqual(census.singlet_multiplicity(census.symmetric_rep_character("H", 4)), 1)
        self.assertEqual(census.singlet_multiplicity(census.symmetric_rep_character("P", 2)), 1)
        self.assertEqual(census.singlet_multiplicity(census.symmetric_rep_character("P", 3)), 1)
        self.assertEqual(census.singlet_multiplicity(census.symmetric_rep_character("P", 4)), 4)

    def test_known_126_products(self):
        rows = census.census()
        self.assertEqual(census.find_multiplicity(rows, D=1, Db=1), 1)
        self.assertEqual(census.find_multiplicity(rows, D=2, Db=2), 4)
        self.assertEqual(census.find_multiplicity(rows, H=2, Db=2), 1)

    def test_charge_aware_portal_orientations(self):
        rows = census.census()
        self.assertEqual(census.find_multiplicity(rows, P=1, H=1, Db=1), 1)
        self.assertEqual(census.find_multiplicity(rows, P=1, Hb=1, D=1), 1)
        self.assertEqual(census.find_multiplicity(rows, P=1, H=1, D=1, S=1), 1)
        self.assertEqual(census.find_multiplicity(rows, P=1, Hb=1, Db=1, Sb=1), 1)
        self.assertEqual(census.find_multiplicity(rows, P=1, H=1, D=1), 0)

    def test_exact_counts_and_new_multiplicities(self):
        report = census.build_report()
        self.assertEqual(report["counts"]["charge_and_so10_allowed_multidegrees"], 34)
        self.assertEqual(report["counts"]["hermitian_conjugacy_orbits"], 28)
        self.assertEqual(report["counts"]["total_complex_invariant_multiplicity"], 51)
        self.assertEqual(report["counts"]["total_potential_orbit_multiplicity"], 44)
        self.assertEqual(report["counts"]["total_real_potential_parameters"], 51)
        self.assertEqual(report["new_exact_multiplicity_findings"]["210_H^2 10_H 126bar_H^dag"], 2)
        self.assertEqual(report["new_exact_multiplicity_findings"]["210_H^2 126bar_H 126bar_H^dag"], 6)
        self.assertEqual(report["new_exact_multiplicity_findings"]["210_H^2 10_H 10_H^dag"], 3)
        self.assertEqual(report["new_exact_multiplicity_findings"]["10_H 10_H^dag 126bar_H 126bar_H^dag"], 2)
        self.assertEqual(report["new_exact_multiplicity_findings"]["10_H^2 10_H^dag^2"], 2)

    def test_charge_filter_and_conjugacy(self):
        rows = census.census()
        for row in rows:
            self.assertEqual(row["charge"], {"PQ": 0, "X": 0, "Z17": 0})
            conjugate = tuple(row["conjugate_count_tuple"])
            self.assertTrue(census.charge_neutral(conjugate))
            self.assertEqual(
                row["so10_singlet_multiplicity"],
                census.find_multiplicity(
                    rows,
                    **{field: count for field, count in zip(census.FIELD_ORDER, conjugate)},
                ),
            )

    def test_report_closes_multiplicity_not_tensors(self):
        report = census.build_report()
        self.assertEqual(report["n_failed"], 0, report)
        self.assertEqual(report["overall_state"], "BLOCKED")
        self.assertTrue(report["closure"]["so10_singlet_multiplicities_degree_le_4_closed"])
        self.assertTrue(report["flags"]["renormalizable_G1_multiplicity_census_closed"])
        self.assertFalse(report["closure"]["explicit_component_tensor_basis_closed"])
        self.assertFalse(report["closure"]["full_component_potential_G2_closed"])
        self.assertFalse(report["flags"]["whole_model_validated"])


if __name__ == "__main__":
    unittest.main()
