import unittest
from fractions import Fraction
import json

import exact_physical_sm_local_equality_orbit_v20 as theorem


class LocalEqualityOrbitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = theorem.build_report()

    def test_zero_failures_and_pins(self):
        self.assertEqual(self.report["n_failed"], 0)
        self.assertTrue(self.report["checks"]["dependency_pins_match"])
        self.assertTrue(self.report["checks"]["upstream_core_pins_match"])

    def test_frozen_report_is_live_report(self):
        frozen = json.loads(theorem.OUT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(frozen, self.report)
        core = dict(self.report)
        integrity = core.pop("integrity")
        self.assertEqual(
            integrity["core_sha256"],
            theorem.hashlib.sha256(theorem.canonical_json_bytes(core)).hexdigest(),
        )

    def test_full_486_local_orbit_theorem(self):
        local = self.report["local_orbit_theorem"]
        self.assertEqual(local["ambient_real_dimension"], 486)
        self.assertEqual(local["target_orbit_dimension"], 38)
        self.assertEqual(local["normal_slice_dimension"], 448)
        self.assertTrue(self.report["claims"]["Crit_V_intersection_U_equals_target_orbit"])
        self.assertTrue(self.report["claims"]["target_orbit_is_strict_local_minimum_in_U_mod_K"])
        self.assertIsNone(local["quantitative_radius"])

    def test_all_sign_actions_exact(self):
        rows = self.report["sixteen_sign_orbit"]["rows"]
        self.assertEqual(len(rows), 16)
        self.assertEqual(len({tuple(row["bits_h_d_s_x"]) for row in rows}), 16)
        for row in rows:
            self.assertEqual(
                list(row["verified_net_phase_exponents_over_pi"].values()),
                [str(value) for value in row["bits_h_d_s_x"]],
            )
            self.assertTrue(
                row["actual_486_coordinate_endpoint_matches_amplitude_variant"]
            )

    @staticmethod
    def _parameters(row):
        return (
            tuple(row["bits_h_d_s_x"]),
            tuple(Fraction(value) for value in row["SO10_Cartan_theta_0_to_4_over_pi"]),
            Fraction(row["U1X_alpha_over_pi"]),
            Fraction(row["PQ_beta_over_pi"]),
        )

    def test_wrong_h_plane_is_rejected(self):
        row = next(
            row for row in self.report["sixteen_sign_orbit"]["rows"]
            if row["bits_h_d_s_x"] == [1, 0, 0, 0]
        )
        bits, theta, alpha, beta = self._parameters(row)
        _phases, matches = theorem.phase_action(
            bits, theta, alpha, beta, h_plane=3
        )
        self.assertFalse(matches)

    def test_wrong_sigma_chirality_weights_are_rejected(self):
        row = next(
            row for row in self.report["sixteen_sign_orbit"]["rows"]
            if row["bits_h_d_s_x"] == [0, 0, 1, 0]
        )
        bits, theta, alpha, beta = self._parameters(row)
        _phases, matches = theorem.phase_action(
            bits,
            theta,
            alpha,
            beta,
            sigma_cartan_weights=(-1, -1, -1, -1, -1),
        )
        self.assertFalse(matches)

    def test_wrong_phi17_charge_is_rejected(self):
        row = next(
            row for row in self.report["sixteen_sign_orbit"]["rows"]
            if row["bits_h_d_s_x"] == [0, 0, 0, 1]
        )
        bits, theta, alpha, beta = self._parameters(row)
        _phases, matches = theorem.phase_action(
            bits, theta, alpha, beta, u1x_charges=(-2, -2, 4, 16)
        )
        self.assertFalse(matches)

    def test_global_claims_fail_closed(self):
        claims = self.report["claims"]
        self.assertFalse(claims["quantitative_radius_for_U_proved"])
        self.assertFalse(claims["complete_486_field_global_equality_orbit_classified"])
        self.assertFalse(claims["physical_SM_G3_closed"])
        self.assertFalse(claims["physical_SM_G4_closed"])
        self.assertFalse(claims["physical_SM_G5_closed"])


if __name__ == "__main__":
    unittest.main()
