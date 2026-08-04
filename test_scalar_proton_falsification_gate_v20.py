#!/usr/bin/env python3
import copy
import json
import unittest
from pathlib import Path

import scalar_proton_falsification_gate_v20 as mod

BASE = json.loads(Path("data/scalar_proton_falsification_inputs_v20.json").read_text())


class GateTests(unittest.TestCase):
    def test_current_state_is_blocked(self):
        r = mod.build_report(copy.deepcopy(BASE))
        self.assertEqual(r["overall_state"], "BLOCKED")
        self.assertFalse(r["hard_findings"]["whole_model_excluded"])
        self.assertFalse(r["hard_findings"]["whole_model_validated"])

    def test_tachyon_fails(self):
        r = copy.deepcopy(BASE)
        r["scalar_completion"]["physical_hessian_eigenvalues_GeV2"] = [1.0, -0.1]
        self.assertEqual(mod.scalar_gate(r)["state"], "FAIL")

    def test_goldstone_mismatch_fails(self):
        r = copy.deepcopy(BASE)
        r["scalar_completion"]["goldstone_count_found"] = 32
        self.assertEqual(mod.scalar_gate(r)["state"], "FAIL")

    def test_lower_competing_vacuum_fails(self):
        r = copy.deepcopy(BASE)
        s = r["scalar_completion"]
        s["target_vacuum_energy_GeV4"] = -1.0
        s["competing_vacua_energies_GeV4"] = [-2.0, 0.0]
        self.assertEqual(mod.scalar_gate(r)["state"], "FAIL")

    def test_synthetic_complete_scalar_certificate_passes(self):
        r = copy.deepcopy(BASE)
        inv = ["I2_210", "I2_126", "I2_10", "I3_210"]
        r["scalar_completion"].update({
            "external_invariant_basis_reference": "synthetic-test-only",
            "invariant_basis_sha256": mod.sha(inv),
            "expected_independent_invariant_count": len(inv),
            "declared_independent_invariants": inv,
            "stationarity_residual_inf": 1e-14,
            "physical_hessian_eigenvalues_GeV2": [1.0, 2.0],
            "goldstone_count_found": 33,
            "target_vacuum_energy_GeV4": -3.0,
            "competing_vacua_energies_GeV4": [-2.0, -1.0],
            "bounded_from_below_certificate": True,
            "xy_mass_eigenvalues_GeV": [1e16],
            "color_triplet_states": [{"mass_GeV": 1e16, "effective_yukawa": 1e-5}],
        })
        self.assertEqual(mod.scalar_gate(r)["state"], "PASS")

    def test_gauge_lifetime_scales_as_m4(self):
        p, a = BASE["proton_decay"], BASE["unification_anchor"]
        t1 = mod.gauge_lifetime(1e16, a["alpha_inv_GUT"], p["central_A_R"], p["central_hadronic_W_GeV2"], p["V_ud"])
        t2 = mod.gauge_lifetime(2e16, a["alpha_inv_GUT"], p["central_A_R"], p["central_hadronic_W_GeV2"], p["V_ud"])
        self.assertAlmostEqual(t2 / t1, 16.0, places=12)

    def test_proxy_never_becomes_hard_fail(self):
        r = copy.deepcopy(BASE)
        r["scalar_completion"]["color_triplet_states"] = [{"mass_GeV": r["unification_anchor"]["M_I_GeV"], "effective_yukawa": 1e-4}]
        p = mod.proton_gate(r)
        self.assertEqual(p["state"], "BLOCKED")
        self.assertFalse(p["model_excluded"])
        self.assertGreater(p["conditional_triplet_points_excluded"], 0)

    def test_certified_exact_lifetime_can_fail(self):
        r = copy.deepcopy(BASE)
        r["proton_decay"]["exact_operator_running_hadronic_matching"] = True
        r["proton_decay"]["exact_combined_channel_lifetime_years"] = 1e34
        p = mod.proton_gate(r)
        self.assertEqual(p["state"], "FAIL")
        self.assertTrue(p["model_excluded"])


if __name__ == "__main__":
    unittest.main()
