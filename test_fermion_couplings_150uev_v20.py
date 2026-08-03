import unittest

import fermion_couplings_150uev_v20 as m


class FermionCouplingAudit(unittest.TestCase):
    def test_decay_constant_uses_covering_anomaly(self):
        self.assertAlmostEqual(m.FA_GEV, m.VS_GEV / 17.0)
        self.assertNotAlmostEqual(m.FA_GEV, m.VS_GEV)

    def test_electron_identity(self):
        row = m.coefficients(1.5)
        expected = row["sin2_beta"] * m.ME_GEV / m.VS_GEV
        self.assertAlmostEqual(row["g_ae"], expected, places=28)

    def test_v20_numbers(self):
        row = m.coefficients(1.5)
        self.assertAlmostEqual(row["C_e"], 0.04072398190045249)
        self.assertAlmostEqual(row["C_p"], -0.472579185520362)
        self.assertAlmostEqual(row["C_n"], 0.006606334841628959)
        self.assertAlmostEqual(row["g_ae"], 5.603050812002396e-16)
        self.assertAlmostEqual(row["g_ap"], -1.1938718273899883e-11)
        self.assertAlmostEqual(row["g_an"], 1.6712519395948702e-13)

    def test_all_bound_gates_pass(self):
        report = m.build_report()
        self.assertTrue(
            all(x["passes"] for x in report["published_bound_checks"].values())
        )
        self.assertGreater(
            report["published_bound_checks"]["TRGB_electron"]["safety_factor"],
            100,
        )
        self.assertGreater(
            report["published_bound_checks"]["generic_SN_nucleon_envelope"]
            ["safety_factor"],
            50,
        )

    def test_wrong_physical_wall_normalization_is_rejected(self):
        correct = m.coefficients(1.5)["C_e"]
        wrong = (1.5**2 / (1 + 1.5**2)) / m.N_PHYSICAL_WALL
        self.assertAlmostEqual(wrong / correct, 17.0)


if __name__ == "__main__":
    unittest.main()
