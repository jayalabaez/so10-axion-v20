#!/usr/bin/env python3
import unittest

import scalar_proton_falsification_gate_v20 as audit


class CanonicalScalarProtonAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()

    def test_canonical_stack_executes(self):
        self.assertEqual(self.report["execution_failures"], [])
        self.assertEqual(self.report["hard_theory_failures"], [])
        self.assertTrue(
            self.report["certificates"]["all_canonical_modules_executed"]
        )

    def test_all_repaired_breakpoints_reproduce(self):
        self.assertTrue(
            all(self.report["resolved_breakpoints"].values()),
            self.report["resolved_breakpoints"],
        )
        cert = self.report["certificates"]
        self.assertTrue(cert["pati_salam_subgroup_RGE_repaired"])
        self.assertTrue(cert["forbidden_210_10dag10_removed"])
        self.assertTrue(cert["signed_floor34_emitted"])
        self.assertTrue(cert["physical_EW_survival_point_reproduced"])
        self.assertTrue(cert["historical_lambda4_point_excluded"])
        self.assertTrue(cert["perturbative_even_H_no_rescue_proved"])
        self.assertTrue(cert["signed_mass_squared_triplet_proxy_built"])
        self.assertTrue(cert["kronecker_gate_corrected"])
        self.assertTrue(cert["legacy_triplet_dependency_graph_classified"])
        self.assertTrue(cert["exact_gauge_orbit_reproduced"])

    def test_legacy_chain_is_invalidated_not_executed_as_physics(self):
        self.assertTrue(
            self.report["certificates"][
                "legacy_modules_not_used_as_physical_certificates"
            ]
        )
        self.assertTrue(
            self.report["remaining_blockers"][
                "legacy_triplet_threshold_lifetime_chain_rebuild"
            ]
        )
        self.assertTrue(
            self.report["remaining_blockers"][
                "physical_component_triplet_CG_coefficients"
            ]
        )

    def test_final_state_is_honest(self):
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertFalse(self.report["certificates"]["whole_model_excluded"])
        self.assertFalse(self.report["certificates"]["whole_model_validated"])
        self.assertTrue(
            self.report["remaining_blockers"]["full_component_nonsusy_hessian"]
        )
        self.assertTrue(
            self.report["remaining_blockers"]["full_tensor_two_loop_betas"]
        )
        self.assertTrue(
            self.report["remaining_blockers"]["exact_unique_proton_lifetime"]
        )


if __name__ == "__main__":
    unittest.main()
