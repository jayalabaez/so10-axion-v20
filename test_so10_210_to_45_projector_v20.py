#!/usr/bin/env python3
"""Tests for SO(10) (210⊗210)→45 adjoint projector / same-field vanishing."""

from __future__ import annotations

import unittest

import so10_210_to_45_projector_v20 as mod


class So10210To45Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flags"]["so10_210_to_45_projector_ready"])
        self.assertTrue(self.report["flags"]["open_210_channel_45_same_field_vanishes"])
        self.assertTrue(self.report["flags"]["open_210_channel_45_mixed_still_open"])
        self.assertTrue(self.report["flags"]["symmetric_45_quartic_not_closed_by_this_map"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])
        self.assertEqual(
            self.report["inventory_slot"]["status"],
            "PARTIAL_ANTISYM_SAME_FIELD_VANISHES__SYMMETRIC_SOURCE_OPEN",
        )

    def test_theorem_same_field_vanishes_mixed_lives(self):
        self.assertTrue(self.report["checks"]["same_field_45_vanishes_generic"])
        self.assertTrue(self.report["checks"]["mixed_45_nontrivial_generic"])
        self.assertTrue(self.report["checks"]["ps_singlet_span_45_closes"])
        self.assertTrue(
            self.report["checks"]["ps_singlet_times_off_singlet_45_nontrivial"]
        )
        self.assertLess(self.report["mathematics"]["generic_same_field_fnorm"], 1e-20)
        self.assertGreater(self.report["mathematics"]["generic_mixed_fnorm"], 1e-12)
        self.assertLess(self.report["mathematics"]["ps_p_a_mixed_fnorm"], 1e-12)


if __name__ == "__main__":
    unittest.main()
