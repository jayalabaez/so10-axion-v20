from __future__ import annotations

import copy
import json
import unittest
from fractions import Fraction

import susy_v23_chacko_route_rejection as rejection


class SusyV23ChackoRouteRejectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = rejection.build_report()

    def test_exact_additive_Abelian_identities(self) -> None:
        identities = self.report["additive_Abelian_rejection"]["identities"]
        self.assertEqual(set(identities), {
            "superpotential_charge_is_zero",
            "S_charge_is_zero",
            "P_Pbar_is_forced",
            "H1_H2_is_forced",
        })
        self.assertTrue(all(row["exact_match"] for row in identities.values()))
        self.assertEqual(identities["P_Pbar_is_forced"]["target_vector"], {
            "P": 1, "Pbar": 1, "omega": -1,
        })
        self.assertEqual(identities["H1_H2_is_forced"]["target_vector"], {
            "H1": 1, "H2": 1, "omega": -1,
        })

    def test_S2_plus_S3_excludes_a_genuine_R_selector(self) -> None:
        conclusions = self.report["additive_Abelian_rejection"]["conclusions"]
        self.assertEqual(conclusions["superpotential_charge_omega"], 0)
        self.assertFalse(conclusions["genuine_R_selector_for_unchanged_W1_W2"])
        self.assertFalse(conclusions["P_Pbar_can_be_forbidden"])
        self.assertFalse(conclusions["H1_H2_can_be_forbidden"])

    def test_exact_one_and_two_loop_coefficients(self) -> None:
        coefficients = rejection.gauge_coefficients()
        self.assertEqual(coefficients["sum_T"], 51)
        self.assertEqual(coefficients["sum_C2_times_T"], Fraction(1487, 4))
        self.assertEqual(coefficients["b"], 27)
        self.assertEqual(coefficients["B"], 1919)

    def test_two_loop_strong_coupling_scales_reject_Planck120(self) -> None:
        scales = self.report["gauge_running_rejection"]["two_loop_strong_coupling_scales"]
        self.assertEqual([row["alpha"] for row in scales], ["1/10", "3/10", "1"])
        expected = [11.21385794, 25.49052495, 29.54021000]
        for row, value in zip(scales, expected):
            self.assertAlmostEqual(row["mu_over_MGUT"], value, places=7)
            self.assertTrue(row["below_MPlanck_over_MGUT_120"])
        self.assertFalse(self.report["gauge_running_rejection"]["Planck120_perturbative_completion_demonstrated"])

    def test_extra_45B_fails_already_at_one_loop(self) -> None:
        repair = self.report["extra_45B_repair_rejection"]
        self.assertEqual(repair["b_one_loop"], 35)
        self.assertAlmostEqual(repair["one_loop_pole_mu_over_MGUT"], 74.32667650, places=7)
        self.assertLess(repair["one_loop_pole_mu_over_MGUT"], 120)
        self.assertFalse(repair["repairs_Planck120_running"])

    def test_all_G1_through_G8_claims_are_false_and_open(self) -> None:
        self.assertEqual(self.report["closure_counts"], {"closed": 0, "open": 8})
        self.assertEqual([row["gate"] for row in self.report["gates"]], [f"G{i}" for i in range(1, 9)])
        self.assertTrue(all(row["closed"] is False for row in self.report["gates"]))
        self.assertTrue(all(row["full_gate_claim"] is False for row in self.report["gates"]))
        self.assertFalse(self.report["route_verdict"]["accepted_as_V23_completion"])
        self.assertFalse(self.report["route_verdict"]["safe_to_promote"])

    def test_claim_boundary_does_not_overstate_the_rejection(self) -> None:
        boundary = self.report["claim_boundary"]
        self.assertTrue(boundary["unchanged_neutral_coefficient_additive_Abelian_selector_excluded"])
        self.assertTrue(boundary["stated_gauge_only_two_loop_Planck120_trajectory_excluded"])
        self.assertFalse(boundary["all_small_representation_models_excluded"])
        self.assertFalse(boundary["an_interacting_gauge_Yukawa_UV_fixed_point_excluded"])

    def test_frozen_outputs_and_core_hash(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(json.loads(rejection.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(rejection.OUT_MD.read_text(encoding="utf-8"), rejection.markdown(self.report))
        changed = copy.deepcopy(self.report)
        changed["route_verdict"]["safe_to_promote"] = True
        self.assertNotEqual(rejection.canonical_sha(self.report), rejection.canonical_sha(changed))


if __name__ == "__main__":
    unittest.main()
