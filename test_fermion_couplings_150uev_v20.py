import unittest

import fermion_couplings_150uev_v20 as m


class FermionCouplingAudit(unittest.TestCase):
    def test_exact_axion_projection(self):
        expected = (
            m.VS_GEV
            * m.VPHI_GEV
            / ((17.0 * m.VPHI_GEV) ** 2 + (4.0 * m.VS_GEV) ** 2) ** 0.5
        )
        self.assertAlmostEqual(m.FA_GEV, expected)
        self.assertLess(abs(m.FA_GEV / (m.VS_GEV / 17.0) - 1.0), 2e-12)

    def test_extrapolation_requires_explicit_acknowledgement(self):
        with self.assertRaises(RuntimeError):
            m.ert_leading_extrapolation(1.5)

    def test_provisional_numbers_are_reproducible(self):
        row = m.ert_leading_extrapolation(
            1.5, acknowledge_not_full_matching=True
        )
        self.assertAlmostEqual(row["C_e"], 0.04072398190045249)
        self.assertAlmostEqual(row["C_p"], -0.472579185520362)
        self.assertAlmostEqual(row["C_n"], 0.006606334841628959)
        self.assertAlmostEqual(row["g_ae"], 5.60305081200856e-16, places=27)
        self.assertAlmostEqual(row["g_ap"], -1.1938718273913018e-11, places=22)
        self.assertAlmostEqual(row["g_an"], 1.671251939596709e-13, places=24)

    def test_sn1987a_correlated_form(self):
        row = m.ert_leading_extrapolation(
            1.5, acknowledge_not_full_matching=True
        )
        lhs = m.sn1987a_quadratic(g_an=row["g_an"], g_ap=row["g_ap"])
        self.assertAlmostEqual(lhs, row["SN1987A_quadratic_lhs"])
        self.assertLess(lhs, m.SN1987A_QUADRATIC_BOUND)
        self.assertGreater(row["SN1987A_amplitude_margin"], 90.0)

    def test_report_fails_closed(self):
        report = m.build_report()
        self.assertIn("PROVISIONAL", report["status"])
        self.assertIsNone(
            report["conditional_bound_checks"]["TRGB_electron"]["full_model_pass"]
        )
        self.assertIsNone(
            report["conditional_bound_checks"]["SN1987A_correlated_nucleon"][
                "full_model_pass"
            ]
        )
        self.assertIn("NOT closed", report["verdict"])
        self.assertNotIn("gap is closed", report["verdict"])
        self.assertIn("full_fermion_matching_v20.py", report["verdict"])

    def test_q_portal_diagnostic_is_not_declared_zero(self):
        row = m.q_portal_one_family_diagnostic(lambda_q=1.0, y_q=1.0)
        self.assertLess(abs(row["light_PQ_charge_shift"]), 1e-8)
        self.assertNotEqual(row["light_PQ_charge_shift"], 0.0)
        self.assertIn("NOT_FULL_MATCHING", row["classification"])


if __name__ == "__main__":
    unittest.main()
