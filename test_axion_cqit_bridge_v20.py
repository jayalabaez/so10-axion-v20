import math
import unittest

import numpy as np

from axion_cqit_bridge_v20 import (
    axion_coherence_budget,
    build_bridge_report,
    candidate_screen,
    gaussian_template_capture,
    normalized_mode_capture,
    receiver_budget,
    redshifted_mode_parameters,
)


class AxionCQITBridgeTests(unittest.TestCase):
    def test_local_haloscope_redshift_is_identity(self):
        f, bw = redshifted_mode_parameters(37.11e9, 37.11e3, 0.0)
        self.assertEqual(f, 37.11e9)
        self.assertEqual(bw, 37.11e3)

    def test_identical_template_has_unit_capture(self):
        x = np.linspace(-5, 5, 1001)
        s = np.exp(-x*x)
        self.assertAlmostEqual(normalized_mode_capture(s, s), 1.0, places=12)

    def test_frequency_offset_reduces_capture(self):
        exact = gaussian_template_capture(0.0, 10.0)
        shifted = gaussian_template_capture(20.0, 10.0)
        self.assertGreater(exact, 0.999999)
        self.assertLess(shifted, 0.2)

    def test_coherence_budget_matches_q_definition(self):
        b = axion_coherence_budget(37.11e9, 1e6, 10.0)
        self.assertAlmostEqual(b.linewidth_hz, 37110.0)
        self.assertAlmostEqual(b.coherence_time_s, 1.0 / (math.pi * 37110.0))
        self.assertGreater(b.independent_coherence_intervals, 1e6)

    def test_receiver_loss_reduces_snr(self):
        b = receiver_budget(10.0, detector_efficiency=0.8, mode_capture=0.5, excess_noise_factor=2.0)
        self.assertAlmostEqual(b.calibrated_signal_fraction, 0.4)
        self.assertAlmostEqual(b.effective_snr, 2.0)

    def test_coupling_bias_is_square_root_of_power_fraction(self):
        b = receiver_budget(10.0, detector_efficiency=0.64, mode_capture=1.0)
        self.assertAlmostEqual(b.coupling_bias_if_uncorrected, 0.8)
        self.assertAlmostEqual(b.coupling_correction_factor, 1.25)

    def test_single_repeat_cannot_survive_triage(self):
        s = candidate_screen(10.0, 37.11, 37110.0, independent_repeats=1)
        self.assertFalse(s["candidate_survives_triage"])
        self.assertFalse(s["checks"]["independent_repeats"])

    def test_instrumental_veto_blocks_candidate(self):
        s = candidate_screen(10.0, 37.11, 37110.0, independent_repeats=3, veto_triggered=True)
        self.assertFalse(s["candidate_survives_triage"])
        self.assertFalse(s["checks"]["instrumental_veto_clear"])

    def test_report_is_honest_about_scope(self):
        r = build_bridge_report()
        self.assertFalse(r["claims"]["validates_so10_model"])
        self.assertFalse(r["claims"]["detects_axion"])
        self.assertFalse(r["claims"]["new_physics"])
        self.assertTrue(r["claims"]["improves_falsification_and_receiver_accounting"])
        self.assertFalse(r["scientific_scope"]["cosmological_redshift_relevant_to_haloscope_signal"])


if __name__ == "__main__":
    unittest.main()
