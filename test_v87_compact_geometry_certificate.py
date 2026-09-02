import json
import unittest

import sympy as sp

import v87_compact_geometry_certificate as certificate


class TestV87CompactGeometryCertificate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = certificate.build_report()

    def test_report_validates_is_canonical_and_json_serializable(self):
        certificate.validate_report(self.report)
        self.assertEqual(
            certificate.canonical_sha(self.report), self.report["core_sha256"]
        )
        json.dumps(self.report, sort_keys=True)

    def test_all_chart_component_pairs_are_generated_from_the_fan(self):
        charts = self.report["chart_jacobian_certificate"]
        expected_pairs = sum(
            len(set(cone) & set(certificate.VERTICAL_COMPONENTS))
            for cone in certificate.LOCAL_MAXIMAL_CONES
        )
        self.assertEqual(expected_pairs, 25)
        self.assertEqual(charts["n_chart_component_pairs"], expected_pairs)
        observed = {
            (row["chart_index"], row["component"]) for row in charts["rows"]
        }
        self.assertEqual(len(observed), expected_pairs)

    def test_all_25_symbolic_groebner_bases_are_unit(self):
        charts = self.report["chart_jacobian_certificate"]
        self.assertEqual(charts["n_unit_ideals"], 25)
        self.assertTrue(charts["all_chart_component_ideals_are_unit"])
        for row in charts["rows"]:
            self.assertEqual(row["groebner_basis"], ["1"])
            self.assertTrue(row["unit_ideal"])
            self.assertEqual(len(row["chart_polynomial_sha256"]), 64)

    def test_branch_transversality_is_derived_from_P_prime(self):
        self.assertEqual(certificate.branch_transversality_value(1), sp.Rational(1, 4))
        self.assertEqual(certificate.branch_transversality_value(2), sp.Rational(1, 2))
        self.assertEqual(certificate.branch_transversality_value(0), 0)

    def test_total_pullback_and_six_component_restrictions_are_derived(self):
        flatness = self.report["flatness_certificate"]
        self.assertEqual(flatness["derived_total_pullback"], "e1*e2*e3*e4*e5**2*s")
        self.assertEqual(flatness["n_components"], 6)
        self.assertEqual(flatness["n_nonzero_component_restrictions"], 6)
        self.assertEqual(
            {row["component"] for row in flatness["witnesses"]},
            set(certificate.VERTICAL_COMPONENTS),
        )
        for row in flatness["witnesses"]:
            self.assertTrue(row["nonzero"])
            self.assertNotEqual(row["restriction"], "0")

    def test_flatness_conclusion_retains_its_exact_scope(self):
        flatness = self.report["flatness_certificate"]
        self.assertTrue(flatness["no_ambient_surface_component_contained"])
        self.assertTrue(flatness["hypersurface_is_effective_Cartier_in_smooth_ambient"])
        self.assertTrue(flatness["fibers_projective_nonempty_and_pure_dimension_one"])
        self.assertTrue(flatness["miracle_flatness_applies"])

    def test_chern_pushforward_runs_all_five_exceptional_stages(self):
        chern = self.report["chern_pushforward_certificate"]
        self.assertEqual(
            chern["post_exceptional_push_term_counts"],
            {"E5": 138, "E4": 83, "E3": 46, "E2": 24, "E1": 14},
        )
        self.assertEqual(chern["n_degree_four_integrand_terms"], 220)
        self.assertEqual(len(chern["after_exceptional_push_terms"]), 14)
        self.assertEqual(chern["after_exceptional_push_terms"]["H^4"], -24)
        self.assertEqual(chern["after_exceptional_push_terms"]["H^2*L*S"], 364)

    def test_projective_pushforward_and_euler_are_derived(self):
        chern = self.report["chern_pushforward_certificate"]
        self.assertEqual(
            chern["base_pushforward_terms"],
            {"S^2": -32, "L*S": 84, "L^2": -60},
        )
        self.assertEqual(chern["base_class"], "-60*L^2+84*L*S-32*S^2")
        self.assertEqual(
            chern["Euler_contributions"], {"L^2": -480, "L*S": -168, "S^2": 128}
        )
        self.assertEqual(chern["formal_Euler"], -520)

    def test_hodge_pair_remains_conditional(self):
        hodge = self.report["chern_pushforward_certificate"]["conditional_Hodge"]
        self.assertEqual((hodge["h11"], hodge["h21"]), (8, 268))
        self.assertEqual(hodge["Mordell_Weil_rank_assumed"], 0)
        self.assertFalse(hodge["unconditional"])
        boundary = self.report["claim_boundary"]
        self.assertFalse(boundary["global_Cox_Jacobian_saturation_run"])
        self.assertFalse(boundary["compact_strict_transform_smooth_unconditionally_certified"])
        self.assertFalse(boundary["Hodge_numbers_unconditional"])


if __name__ == "__main__":
    unittest.main()
