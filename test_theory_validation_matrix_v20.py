#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import theory_validation_matrix_v20 as matrix


def write_json(root: Path, name: str, value: dict) -> None:
    root.joinpath(name).write_text(json.dumps(value), encoding="utf-8")


def minimal_tree(
    root: Path,
    *,
    engine_pass: bool = True,
    unit_pass: bool = True,
    sphere_probability: bool = False,
    vacuum_minimized: bool = False,
    full_rg: bool = False,
) -> None:
    write_json(
        root,
        "so10_axion_v20_verdict.json",
        {
            "status": "PASS" if engine_pass else "FAIL",
            "n_checks_total": 42,
            "n_checks_failed": 0 if engine_pass else 1,
        },
    )
    write_json(
        root,
        "V20_ERROR_AUDIT.json",
        {
            "status": "PASS",
            "n_checks_failed": 0,
            "soft_falsifications_of_manuscript_overclaims": [
                "manuscript portal list is incomplete"
            ],
        },
    )
    write_json(
        root,
        "FALSIFICATION_VERDICT.json",
        {
            "status": "PASS",
            "n_hard_failed": 0,
            "n_soft_overclaim_missed": 0,
        },
    )
    write_json(
        root,
        "EXTENSIVE_CONFIRM_FALSIFY_VERDICT.json",
        {
            "status": "PASS",
            "n_extensive_checks": 53,
            "n_failed": 0,
        },
    )
    write_json(
        root,
        "GLOBAL_FLAVOUR_FIT_V20_VERDICT.json",
        {
            "best_point": {
                "chi2": 4.9,
                "viable_chi2_lt_30": True,
                "rg_threshold_status": {
                    "common_scale_RG_inputs_applied": False,
                    "two_loop_thresholds_coupled": False,
                },
            }
        },
    )
    write_json(
        root,
        "UV_VACUUM_ALIGNMENT_V20_VERDICT.json",
        {
            "status": "CONDITIONAL_ALIGNMENT_AXIOM",
            "flag": {
                "vacuum_alignment_principle_stated": True,
                "exact_W_zero_vacuum_selected": True,
                "scalar_quartic_landscape_fully_minimized": vacuum_minimized,
                "unconditional_unique_Cf": False,
            },
        },
    )
    write_json(
        root,
        "YUKAWA_RGE_2LOOP_V20_VERDICT.json",
        {
            "status": "DIAGNOSTIC_CHAIN",
            "flag": {
                "piecewise_yukawa_chain_integrated": True,
                "clebsch_threshold_matching_implemented": True,
                "two_loop_so10_complete": full_rg,
                "published_210_tensor_contractions": full_rg,
                "piecewise_component_threshold_matching_complete": full_rg,
            },
        },
    )
    write_json(
        root,
        "PORTAL_FULL_COMPLEX_ORIENTATION_SPHERE_V20_VERDICT.json",
        {
            "scan": {
                "aggregate_counts": {
                    "n_total_points": 100,
                    "n_NA62_excluded": 90,
                    "n_NA62_surviving": 10,
                    "geometric_fraction_is_uv_probability": sphere_probability,
                }
            }
        },
    )
    write_json(
        root,
        "PORTAL_YUKAWA_POSTERIOR_V20_VERDICT.json",
        {"flag": {"full_portal_yukawa_posterior_derived": False}},
    )
    write_json(root, "NEXT_PHYSICS_ANALYSIS_VERDICT.json", {"status": "PASS"})
    write_json(
        root,
        "HALOSCOPE_37GHZ_LIMIT_COMPARE_V20_VERDICT.json",
        {
            "flag": {
                "real_37GHz_detection": False,
                "benchmark_excluded": False,
            }
        },
    )
    write_json(
        root,
        "CURRENT_UNIT_TEST_ATTESTATION.json",
        {
            "passed": unit_pass,
            "tests_discovered": 1,
            "commit_sha": "test",
        },
    )


class TheoryValidationMatrixTests(unittest.TestCase):
    def test_conditional_candidate_is_not_full_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root)
            report = matrix.build_report(root)
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(
                report["classification"],
                "INTERNALLY_CONSISTENT_CONDITIONAL_CANDIDATE",
            )
            self.assertFalse(report["full_theory_validated"])
            states = {gate["name"]: gate["state"] for gate in report["gates"]}
            self.assertEqual(states["proton_decay"], "OPEN")
            self.assertEqual(
                states["full_scalar_potential_vacuum_and_spectrum"],
                "CONDITIONAL",
            )
            self.assertEqual(states["UV_portal_selection_and_FCNC"], "CONDITIONAL")

    def test_core_failure_rejects_current_realization(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root, engine_pass=False)
            report = matrix.build_report(root)
            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(report["decision"], "REJECT")
            self.assertIn(
                "mathematical_and_software_core",
                report["failed_gates"],
            )

    def test_geometric_fraction_cannot_be_promoted_to_uv_probability(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root, sphere_probability=True)
            report = matrix.build_report(root)
            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(
                report["classification"],
                "VALIDATION_MATRIX_FAIL__OVERCLAIM",
            )
            self.assertTrue(
                any("UV probability" in item for item in report["overclaim_errors"])
            )

    def test_partial_rge_and_axiom_vacuum_stay_conditional(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root, vacuum_minimized=False, full_rg=False)
            report = matrix.build_report(root)
            states = {gate["name"]: gate["state"] for gate in report["gates"]}
            self.assertEqual(
                states["full_scalar_potential_vacuum_and_spectrum"],
                "CONDITIONAL",
            )
            self.assertEqual(
                states["two_loop_RGE_unification_and_thresholds"],
                "CONDITIONAL",
            )

    def test_current_repository_can_never_claim_discovery_from_internal_tests(self):
        report = matrix.build_report(matrix.ROOT)
        self.assertFalse(report["empirical_discovery"])
        self.assertFalse(report["full_theory_validated"])
        self.assertIn(
            report["classification"],
            {
                "INTERNALLY_CONSISTENT_CONDITIONAL_CANDIDATE",
                "INSUFFICIENT_CURRENT_REPRODUCIBILITY",
            },
        )


if __name__ == "__main__":
    unittest.main()
