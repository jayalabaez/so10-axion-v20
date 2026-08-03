#!/usr/bin/env python3
"""Tests for uniqueness-obstruction / conditional-certification math."""

from __future__ import annotations

import unittest

import theory_certification_math_v20 as cert


class TheoryCertificationMathTests(unittest.TestCase):
    def test_obstruction_rejects_charge_only_uniqueness(self) -> None:
        proof = cert.uniqueness_obstruction_proof()
        self.assertTrue(proof["flag"]["obstruction_demonstrated"])
        self.assertFalse(proof["flag"]["uniqueness_from_charges_alone"])
        self.assertGreaterEqual(len(proof["witness_portals"]), 2)

    def test_conditional_point_under_named_axioms(self) -> None:
        point = cert.conditional_unique_cf_under_maximal_axioms()
        self.assertEqual(
            point["status"], "CONDITIONAL_UNIQUE_CF_UNDER_NAMED_AXIOMS"
        )
        self.assertTrue(point["flag"]["conditional_unique_Cf_under_named_axioms"])
        self.assertFalse(point["flag"]["unconditional_unique_Cf"])
        self.assertIn("C_e", point["selected_point"])
        self.assertIn("C_p_central", point["selected_point"])
        self.assertIn("C_n_central", point["selected_point"])

    def test_report_refuses_unconditional_unique_cf(self) -> None:
        report = cert.build_report()
        self.assertEqual(report["n_failed"], 0)
        self.assertFalse(report["flag"]["unconditional_unique_Cf"])
        self.assertTrue(report["flag"]["mathematical_obstruction_proved"])
        self.assertEqual(
            report["roadmap"]["front_1_uv_coupling"]["unique_Cf_from_charges"],
            "IMPOSSIBLE_BY_THEOREM",
        )


if __name__ == "__main__":
    unittest.main()
