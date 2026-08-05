#!/usr/bin/env python3
"""Tests for 210+126+10 component lift of the reduced vacuum."""

from __future__ import annotations

import unittest

import component_lift_210_126_10_v20 as mod


class ComponentLiftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()
        cls.by_name = {p["name"]: p for p in cls.report["points"]}

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "COMPONENT_LIFT_OF_REDUCED_VACUUM_COMPLETE__FULL_CG_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["component_lift_of_reduced_vacuum"])
        self.assertTrue(flags["210_split_into_a_omega_p"])
        self.assertTrue(flags["lifted_radial_hessian_pd"])
        self.assertTrue(flags["phase_hessian_embedded"])
        self.assertTrue(flags["goldstone_counting_recorded"])
        self.assertFalse(flags["full_cg_tensors_normalized"])
        self.assertFalse(flags["complete_so10_scalar_potential"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_ledger_and_goldstones(self):
        self.assertEqual(self.report["component_ledger"]["n_radial_components"], 8)
        self.assertEqual(
            self.report["goldstone_ledger"]["broken_generators_eaten"], 33
        )
        self.assertAlmostEqual(
            self.report["component_ledger"]["210_sum_check"][
                "a_plus_omega_plus_p_over_MGUT"
            ],
            1.0,
            places=12,
        )

    def test_phase_embedding(self):
        lo = self.by_name["locking_only"]
        self.assertEqual(lo["phase"]["reduced_n_positive"], 0)
        self.assertEqual(lo["phase"]["reduced_n_zero"], 3)
        self.assertEqual(lo["phase"]["extra_spectator_zeros"], 4)
        fk = self.by_name["finite_kappa_benchmark"]
        self.assertEqual(fk["phase"]["reduced_n_positive"], 1)
        self.assertEqual(fk["phase"]["reduced_n_zero"], 2)
        phys = fk["phase"]["physical_after_gauge_quotient"]
        self.assertIsNotNone(phys)
        self.assertEqual(phys["rank"], 1)
        self.assertEqual(phys["nullity"], 1)
        self.assertFalse(phys["extra_nonaxion_flat_phase"])

    def test_all_radial_pd(self):
        for p in self.report["points"]:
            self.assertTrue(p["radial"]["positive_definite"])
            self.assertEqual(p["radial"]["n_negative"], 0)


if __name__ == "__main__":
    unittest.main()
