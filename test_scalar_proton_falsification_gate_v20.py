#!/usr/bin/env python3
import unittest

import scalar_proton_falsification_gate_v20 as audit


class CurrentMainScalarProtonAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()

    def test_current_stack_executes(self):
        self.assertTrue(
            self.report["certificates"]["all_critical_modules_executed"],
            self.report["execution_failures"],
        )
        self.assertEqual(self.report["execution_failures"], [])

    def test_current_verdict_is_fail_closed(self):
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertFalse(self.report["certificates"]["whole_model_excluded"])
        self.assertFalse(self.report["certificates"]["whole_model_validated"])
        self.assertEqual(self.report["hard_theory_failures"], [])

    def test_documented_hessian_stack_reproduces(self):
        self.assertTrue(
            self.report["certificates"]["hessian_residuals_closed_in_repository_stack"]
        )
        self.assertTrue(
            self.report["certificates"]["mixed_spectrum_positive_in_repository_stack"]
        )

    def test_charged_ps_fields_are_not_accepted_as_zero_casimir(self):
        cert = self.report["certificates"]
        self.assertTrue(cert["charged_PS_fields_zero_casimir_in_quartic_rg"])
        rows = self.report["rge_audit"][
            "charged_parent_sectors_evolved_with_zero_casimir"
        ]
        names = {row["name"] for row in rows}
        self.assertIn("DeltaR_126bar", names)
        self.assertIn("H10_eff", names)
        blockers = "\n".join(self.report["scientific_blockers"])
        self.assertIn("Pati-Salam-stage", blockers)
        self.assertIn("subgroup RGEs", blockers)

    def test_susy_component_transfer_is_conditional(self):
        self.assertFalse(
            self.report["certificates"][
                "nonsusy_component_hessian_independently_derived"
            ]
        )
        modules = self.report["component_matrix_audit"][
            "aulakh_msgut_dependent_modules"
        ]
        self.assertGreaterEqual(len(modules), 1)
        blockers = "\n".join(self.report["scientific_blockers"])
        self.assertIn("supersymmetric component matrices", blockers)
        self.assertIn("non-supersymmetric", blockers)

    def test_exact_pq_kernel_lift_reproduces_but_light_modes_remain(self):
        self.assertTrue(self.report["certificates"]["exact_pq_kernel_lifted"])
        self.assertFalse(
            self.report["certificates"]["selected_lam4_clears_null_tolerance"]
        )
        self.assertTrue(self.report["certificates"]["cal_G_soft_mode_remaining"])

    def test_live_external_tensor_run_is_not_overclaimed(self):
        self.assertFalse(self.report["certificates"]["live_sarah_or_pyrate_run"])
        self.assertFalse(self.report["certificates"]["exact_unique_proton_lifetime"])
        blockers = "\n".join(self.report["scientific_blockers"])
        self.assertIn("live SARAH/PyR@TE", blockers)
        self.assertIn("exact_unique_proton_lifetime", blockers)

    def test_selected_proton_lifetime_is_reported_conditionally(self):
        numerical = self.report["numerical_findings"]
        self.assertIsNotNone(numerical["selected_tau_e_years"])
        self.assertGreater(numerical["selected_tau_e_years"], 0.0)
        if numerical["selected_point_excluded_conditionally"]:
            self.assertFalse(self.report["certificates"]["whole_model_excluded"])

    def test_recursive_helpers_are_fail_closed(self):
        sample = {"a": {"flag": False}, "b": [{"flag": True}]}
        self.assertTrue(audit._any_true(sample, "flag"))
        self.assertTrue(audit._all_true_mapping({"x": {"gate": {"a": True}}}, "gate"))
        self.assertFalse(
            audit._all_true_mapping({"x": {"gate": {"a": True, "b": False}}}, "gate")
        )


if __name__ == "__main__":
    unittest.main()
