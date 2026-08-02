#!/usr/bin/env python3
"""Regression tests for claims rejected from the alternate v18 merge."""

import unittest

import alternate_v18_adversarial_audit as audit


class AlternateCompletionAuditTests(unittest.TestCase):
    def test_anomaly_arithmetic_itself_is_correct(self):
        self.assertEqual(audit.anomaly_report()["total"], (0, 0, 0))

    def test_independent_accidental_pq_can_be_defined_but_was_required(self):
        result = audit.repaired_accidental_pq_assignment()
        self.assertEqual(result["heavy_mass_PQ_charge"], 0)
        self.assertEqual(result["decay_vertex_PQ_charge"], 0)
        self.assertEqual(result["heavy_mixed_QCD_PQ_anomaly"], 0)

    def test_heavy_singlet_renormalizable_terms_are_masses_only(self):
        self.assertEqual(
            audit.renormalizable_singlet_yukawas(),
            [("n31", "n-48", "Phi"), ("n33", "n-16", "Phidag")],
        )

    def test_scalar_only_scan_misses_a_p12_fermionic_closure(self):
        certificate = audit.fermionic_p12_certificate()
        self.assertEqual(certificate["O6"]["X"], 0)
        self.assertEqual(certificate["O8"]["X"], 0)
        self.assertEqual(
            (certificate["closure"]["P"], certificate["closure"]["Q_PQ"],
             certificate["closure"]["V_light"]),
            (12, -68, 0),
        )

    def test_alternate_u1_running_is_more_restrictive(self):
        running = audit.abelian_running()
        self.assertEqual(running["b_X_one_loop"], 8263.0)
        self.assertTrue(0.041 < running["gX_max_for_Landau_pole_above_MPl"] < 0.042)

    def test_quoted_old_graph_number_has_128_fold_normalisation_offset(self):
        comparison = audit.old_graph_normalisation()
        self.assertTrue(127.0 < comparison["quoted_over_exact"] < 129.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
