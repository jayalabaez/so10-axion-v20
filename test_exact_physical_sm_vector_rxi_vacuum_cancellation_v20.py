from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

import exact_physical_sm_vector_rxi_vacuum_cancellation_v20 as rxi


HERE = Path(__file__).resolve().parent


class ExactPhysicalSMVectorRxiVacuumCancellationTests(unittest.TestCase):
    def test_terminal_core_pin(self) -> None:
        self.assertEqual(
            rxi.build_report()["core_sha256"],
            "ff79272e5f9eea691cae4e05926723d882ced5dcf852154dcfc43f8add44ef93",
        )

    def test_terminal_source_pin(self) -> None:
        self.assertEqual(
            hashlib.sha256(Path(rxi.__file__).read_bytes()).hexdigest(),
            "5a850a37ac97043a4857002bbe96ab963380462a6ec17f1c43eb9a7a371e6a44",
        )

    def test_terminal_report_pins(self) -> None:
        self.assertEqual(
            hashlib.sha256(rxi.OUT_JSON.read_bytes()).hexdigest(),
            "e1553d18c5acb9fd738dfc8c16277a634ae42bca2960296656eee57a78101221",
        )
        self.assertEqual(
            hashlib.sha256(rxi.OUT_MD.read_bytes()).hexdigest(),
            "b549642e47656257c90b13361715c1602f202548ba4e01f068d26ffa163a4286",
        )

    def test_artifact_is_regenerated_exactly(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(Path(rxi.__file__)), "--check"],
            cwd=HERE,
            check=True,
            capture_output=True,
            text=True,
        )
        summary = json.loads(completed.stdout)
        self.assertEqual(summary["n_failed"], 0)
        self.assertEqual(summary["core_sha256"], rxi.EXPECTED_CORE_SHA256)

    def test_dependency_guard_is_terminal(self) -> None:
        bindings = rxi.source_guard()
        self.assertEqual(set(bindings), set(rxi.DEPENDENCIES))
        self.assertTrue(all(row["mode"] == "raw" for row in bindings.values()))

    def test_one_direction_exponents_cancel(self) -> None:
        theorem = rxi.exact_one_direction_exponent_ledger()
        exponents = theorem["effective_action_exponents"]
        self.assertEqual(
            exponents["longitudinal_vector_on_D_xiM_over_xi"]
            + exponents["real_Goldstone_on_D_xiM"]
            + exponents["complex_FP_ghost_pair_on_D_xiM"],
            0,
        )
        self.assertEqual(theorem["D_xiM_net_exponent"], 0)

    def test_three_transverse_polarizations_remain(self) -> None:
        theorem = rxi.exact_one_direction_exponent_ledger()
        self.assertEqual(theorem["physical_D_M_exponent"], Fraction(3, 2))

    def test_only_field_independent_xi_normalization_remains(self) -> None:
        theorem = rxi.exact_one_direction_exponent_ledger()
        self.assertEqual(
            theorem["field_independent_log_xi_coefficient"], Fraction(-1, 2)
        )
        self.assertEqual(theorem["normalized_unphysical_determinant"], 1)

    def test_exact_mode_identity_at_zero_momentum(self) -> None:
        result = rxi.exact_mode_certificate(
            momentum_squared=0, mass_squared=Fraction(7, 11), xi=Fraction(5, 3)
        )
        self.assertEqual(
            result["unphysical_squared_before_vacuum_normalization"],
            Fraction(3, 5),
        )
        self.assertEqual(
            result["unphysical_squared_after_vacuum_normalization"], 1
        )

    def test_exact_mode_identity_at_large_rational_values(self) -> None:
        result = rxi.exact_mode_certificate(
            momentum_squared=Fraction(10**9, 7),
            mass_squared=Fraction(10**8, 13),
            xi=Fraction(10**7, 17),
        )
        self.assertEqual(
            result["unphysical_squared_before_vacuum_normalization"],
            Fraction(17, 10**7),
        )
        self.assertEqual(
            result["unphysical_squared_after_vacuum_normalization"], 1
        )

    def test_exact_mode_rejects_nonexact_input(self) -> None:
        with self.assertRaises(TypeError):
            rxi.exact_mode_certificate(
                momentum_squared=0.0, mass_squared=1, xi=1
            )

    def test_exact_mode_rejects_negative_momentum_squared(self) -> None:
        with self.assertRaises(ValueError):
            rxi.exact_mode_certificate(
                momentum_squared=-1, mass_squared=1, xi=1
            )

    def test_exact_mode_rejects_zero_or_negative_mass(self) -> None:
        for mass_squared in (0, -1):
            with self.subTest(mass_squared=mass_squared), self.assertRaises(
                ValueError
            ):
                rxi.exact_mode_certificate(
                    momentum_squared=0, mass_squared=mass_squared, xi=1
                )

    def test_exact_mode_rejects_zero_or_negative_xi(self) -> None:
        for xi in (0, -1):
            with self.subTest(xi=xi), self.assertRaises(ValueError):
                rxi.exact_mode_certificate(
                    momentum_squared=0, mass_squared=1, xi=xi
                )

    def test_hundred_case_grid_covers_zero_through_ninety_nine(self) -> None:
        audit = rxi.exact_hundred_point_audit()
        self.assertEqual(audit["case_range"], [0, 99])
        self.assertEqual(audit["case_count"], 100)
        self.assertTrue(audit["all_exact_rational_cases_pass"])

    def test_hundred_case_grid_independent_replay(self) -> None:
        for index in range(100):
            with self.subTest(case=index):
                result = rxi.exact_mode_certificate(
                    momentum_squared=Fraction(index, 23),
                    mass_squared=Fraction(2 * index + 3, 19),
                    xi=Fraction(index + 1, 17),
                )
                self.assertEqual(
                    result["unphysical_squared_after_vacuum_normalization"], 1
                )

    def test_direction_census_is_34_plus_3(self) -> None:
        census = rxi.exact_direction_census()
        self.assertEqual(census["charged_non_neutral_real_directions"], 34)
        self.assertEqual(census["neutral_massive_real_directions"], 3)
        self.assertEqual(census["total_broken_real_directions"], 37)

    def test_gauge_kernel_census_closes_46_dimensions(self) -> None:
        census = rxi.exact_direction_census()
        self.assertEqual(
            census["total_broken_real_directions"]
            + census["massless_unbroken_real_directions"],
            census["total_gauge_dimension"],
        )

    def test_goldstone_count_is_37_and_PQ_is_excluded(self) -> None:
        census = rxi.exact_direction_census()
        self.assertEqual(census["gauge_Goldstone_directions"], 37)
        self.assertEqual(census["uneaten_global_PQ_direction_excluded"], 1)

    def test_multiplet_ledger_exhausts_every_massive_direction(self) -> None:
        rows = rxi.exact_multiplet_ledger()
        self.assertEqual(len(rows), 8)
        self.assertEqual(sum(row["real_broken_directions"] for row in rows), 37)
        self.assertEqual(rows[-1]["name"], "three_neutral_cubic_roots")

    def test_all_direction_identity_has_111_transverse_modes(self) -> None:
        report = rxi.build_report()
        identity = report["all_37_direction_identity"]
        self.assertEqual(identity["remaining_physical_polarizations"], 111)
        self.assertEqual(
            identity["vacuum_normalized_unphysical_squared_determinant"], "1"
        )

    def test_report_has_no_failed_checks(self) -> None:
        report = rxi.build_report()
        self.assertEqual(report["n_failed"], 0)
        self.assertEqual(report["failures"], [])
        self.assertTrue(all(report["checks"].values()))

    def test_scope_closes_only_vacuum_determinant_subproblem(self) -> None:
        scope = rxi.build_report()["scope"]
        self.assertTrue(
            scope["arbitrary_positive_Rxi_vacuum_mass_momentum_cancellation"]
        )
        self.assertTrue(scope["all_37_broken_real_directions_resolved"])
        self.assertFalse(scope["background_covariant_heat_kernel_matching_coefficient"])
        self.assertFalse(scope["sector_resolved_general_background_gauge_determinants"])

    def test_pole_and_release_claims_remain_false(self) -> None:
        scope = rxi.build_report()["scope"]
        for key in (
            "one_loop_vector_pole_masses",
            "tadpole_and_VEV_renormalization_prescription",
            "complete_scalar_and_fermion_thresholds",
            "physical_G6",
            "physical_G7",
            "release_G6",
            "release_G7",
        ):
            with self.subTest(key=key):
                self.assertFalse(scope[key])

    def test_report_is_canonical_json(self) -> None:
        frozen = json.loads(rxi.OUT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(frozen, rxi.build_report())
        self.assertEqual(rxi.OUT_JSON.read_bytes(), rxi._canonical_bytes(frozen))

    def test_new_artifacts_are_lf_only(self) -> None:
        for path in (Path(rxi.__file__), rxi.OUT_JSON, rxi.OUT_MD):
            with self.subTest(path=path.name):
                self.assertNotIn(b"\r", path.read_bytes())


if __name__ == "__main__":
    unittest.main()
