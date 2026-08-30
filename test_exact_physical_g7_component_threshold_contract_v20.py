#!/usr/bin/env python3
"""Adversarial tests for the physical G7 component-threshold subtheorem."""

from __future__ import annotations

import hashlib
import json
import math
import unittest
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

import exact_physical_g7_component_threshold_contract_v20 as theorem


ROOT = Path(__file__).resolve().parent
EXPECTED_SOURCE_RAW_SHA256 = "41f28313ee6cb10fe9b10625d10b075ada7eb8030ac82da92debe17f950e7bf0"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PhysicalG7ComponentThresholdContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = theorem.build_report()

    def test_01_core_and_report_hashes_are_frozen(self) -> None:
        self.assertEqual(self.report["core_sha256"], theorem.EXPECTED_CORE_SHA256)
        self.assertEqual(
            _sha256(theorem.OUT_JSON), theorem.EXPECTED_REPORT_RAW_SHA256["json"]
        )
        self.assertEqual(
            _sha256(theorem.OUT_MD), theorem.EXPECTED_REPORT_RAW_SHA256["md"]
        )

    def test_02_source_bytes_are_frozen(self) -> None:
        self.assertEqual(_sha256(Path(theorem.__file__)), EXPECTED_SOURCE_RAW_SHA256)

    def test_03_authoritative_inventory_is_exact(self) -> None:
        fields = theorem.parse_authoritative_fields()
        self.assertEqual(len(fields), 14)
        self.assertEqual(sum(row.generations for row in fields if row.statistics == "Weyl"), 19)
        self.assertEqual(
            sum(
                row.generations * theorem.SO10_DIMENSION[row.branching_rep]
                for row in fields
                if row.statistics == "Weyl"
            ),
            304,
        )
        self.assertEqual(
            sum(row["real_scalar_coordinates"] for row in self.report["authoritative_field_inventory"]),
            486,
        )

    def test_04_signed_conjugate_representations_are_not_erased(self) -> None:
        fields = {row.name: row for row in theorem.parse_authoritative_fields()}
        self.assertEqual(fields["SpecB"].branching_rep, "16bar")
        self.assertEqual(fields["Pbar"].branching_rep, "16bar")
        self.assertEqual(fields["Qbar"].branching_rep, "16bar")
        self.assertEqual(fields["Rbar"].branching_rep, "16bar")
        self.assertEqual(fields["Delta126bar"].branching_rep, "126bar")

    def test_05_all_branch_dimensions_and_indices_close_exactly(self) -> None:
        for rep in theorem.PS_BRANCHING:
            row = theorem.representation_audit(rep)
            self.assertTrue(row["dimension_identity"], rep)
            self.assertTrue(row["index_identity"], rep)
            self.assertEqual(row["PS_dimension_sum"], theorem.SO10_DIMENSION[rep])
            self.assertEqual(row["SM_dimension_sum"], theorem.SO10_DIMENSION[rep])

    def test_06_standard_sm_singlet_is_unique_and_has_correct_ps_provenance(self) -> None:
        singlets = [
            row
            for row in theorem.expand_sm("126bar")
            if row.su3 == "1" and row.su2_dim == 1 and row.hypercharge == 0
        ]
        self.assertEqual(len(singlets), 1)
        self.assertEqual(singlets[0].ps_label, "(10,1,3)")

    def test_07_h10_contains_triplets_and_two_ew_doublets(self) -> None:
        rows = theorem.expand_sm("10")
        self.assertEqual(
            sorted((row.su3, row.su2_dim, row.hypercharge) for row in rows),
            sorted(
                [
                    ("3", 1, Fraction(-1, 3)),
                    ("3bar", 1, Fraction(1, 3)),
                    ("1", 2, Fraction(-1, 2)),
                    ("1", 2, Fraction(1, 2)),
                ]
            ),
        )

    def test_08_complete_multiplet_thresholds_are_universal(self) -> None:
        expected = {
            ("10", "complex"): Fraction(1, 3),
            ("16", "complex"): Fraction(2, 3),
            ("126bar", "complex"): Fraction(35, 3),
            ("210", "real"): Fraction(28, 3),
        }
        for (rep, reality), value in expected.items():
            observed = theorem.complete_multiplet_delta_b(
                rep, statistics="scalar", reality=reality
            )
            self.assertEqual(set(observed.values()), {value})

    def test_09_weyl_16_has_four_thirds_per_sm_coupling(self) -> None:
        self.assertEqual(
            theorem.complete_multiplet_delta_b("16", statistics="Weyl"),
            {"g1": Fraction(4, 3), "g2": Fraction(4, 3), "g3": Fraction(4, 3)},
        )

    def test_10_ps_threshold_indices_are_also_universal(self) -> None:
        for rep, value in (("10", Fraction(1, 3)), ("126bar", Fraction(35, 3))):
            observed = theorem.complete_ps_multiplet_delta_b(rep, statistics="scalar")
            self.assertEqual(set(observed.values()), {value})
        self.assertEqual(
            set(
                theorem.complete_ps_multiplet_delta_b(
                    "210", statistics="scalar", reality="real"
                ).values()
            ),
            {Fraction(28, 3)},
        )

    def test_11_scalar_doublet_coefficient_matches_hand_calculation(self) -> None:
        doublet = theorem.SMComponent(
            parent="probe",
            ps_label="probe",
            su3="1",
            su2_dim=2,
            hypercharge=Fraction(1, 2),
        )
        self.assertEqual(
            theorem.component_delta_b(doublet, statistics="scalar"),
            {"g1": Fraction(1, 10), "g2": Fraction(1, 6), "g3": Fraction(0)},
        )

    def test_12_tree_ps_matching_uses_gut_normalized_hypercharge(self) -> None:
        self.assertEqual(
            theorem.ps_to_sm_tree_match(
                {"g4": Fraction(40), "g2L": Fraction(39), "g2R": Fraction(35)}
            ),
            {"g1": Fraction(37), "g2": Fraction(39), "g3": Fraction(40)},
        )

    def test_13_threshold_match_has_documented_sign(self) -> None:
        component = theorem.expand_sm("10")[0]
        state = theorem.MassiveThresholdState(component, 10.0, "scalar")
        high = {"g1": 40.0, "g2": 40.0, "g3": 40.0}
        low = theorem.match_inverse_couplings(high, [state], matching_scale=2.0)
        coefficients = theorem.component_delta_b(component, statistics="scalar")
        for key in high:
            expected = high[key] - float(coefficients[key]) * math.log(5.0) / (2.0 * math.pi)
            self.assertAlmostEqual(low[key], expected, places=14)

    def test_14_threshold_matching_is_permutation_invariant(self) -> None:
        rows = theorem.expand_sm("10")
        states = [
            theorem.MassiveThresholdState(row, float(index + 3), "scalar")
            for index, row in enumerate(rows)
        ]
        forward = theorem.weighted_threshold_logs(states, matching_scale=2.0)
        reverse = theorem.weighted_threshold_logs(list(reversed(states)), matching_scale=2.0)
        for key in forward:
            self.assertAlmostEqual(forward[key], reverse[key], places=15)

    def test_15_matching_scale_covariance_holds_at_one_loop(self) -> None:
        component = theorem.SMComponent(
            parent="probe",
            ps_label="probe",
            su3="1",
            su2_dim=2,
            hypercharge=Fraction(1, 2),
        )
        state = theorem.MassiveThresholdState(component, 5.0, "scalar")
        delta = theorem.component_delta_b(component, statistics="scalar")
        b_high = {"g1": 5.0, "g2": 3.0, "g3": -7.0}
        high_1 = {key: 40.0 for key in b_high}
        mu_1, mu_2 = 2.0, 3.0
        interval = math.log(mu_2 / mu_1)
        high_2 = {
            key: high_1[key] - b_high[key] * interval / (2.0 * math.pi)
            for key in b_high
        }
        low_1 = theorem.match_inverse_couplings(high_1, [state], matching_scale=mu_1)
        low_2 = theorem.match_inverse_couplings(high_2, [state], matching_scale=mu_2)
        for key in b_high:
            b_low = b_high[key] - float(delta[key])
            expected = low_1[key] - b_low * interval / (2.0 * math.pi)
            self.assertAlmostEqual(low_2[key], expected, places=13)

    def test_16_nonpositive_and_nonfinite_mass_is_rejected(self) -> None:
        component = theorem.expand_sm("10")[0]
        for mass in (0.0, -1.0, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                theorem.weighted_threshold_logs(
                    [theorem.MassiveThresholdState(component, mass, "scalar")],
                    matching_scale=1.0,
                )

    def test_17_nonpositive_and_nonfinite_scale_is_rejected(self) -> None:
        component = theorem.expand_sm("10")[0]
        state = theorem.MassiveThresholdState(component, 1.0, "scalar")
        for scale in (0.0, -1.0, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                theorem.weighted_threshold_logs([state], matching_scale=scale)

    def test_18_invalid_statistics_reality_and_multiplicity_are_rejected(self) -> None:
        component = theorem.expand_sm("10")[0]
        with self.assertRaises(ValueError):
            theorem.component_delta_b(component, statistics="Dirac")  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            theorem.component_delta_b(
                component, statistics="scalar", reality="pseudoreal"  # type: ignore[arg-type]
            )
        with self.assertRaises(ValueError):
            theorem.component_delta_b(component, statistics="scalar", multiplicity=0)
        for invalid in (True, 1.5):
            with self.assertRaises(ValueError):
                theorem.component_delta_b(
                    component,
                    statistics="scalar",
                    multiplicity=invalid,  # type: ignore[arg-type]
                )
        with self.assertRaises(ValueError):
            theorem.component_delta_b(
                component, statistics="Weyl", reality="real"
            )

    def test_19_unknown_representation_is_rejected(self) -> None:
        with self.assertRaises(KeyError):
            theorem.expand_sm("120")

    def test_20_wrong_matching_coupling_keys_are_rejected(self) -> None:
        component = theorem.expand_sm("10")[0]
        state = theorem.MassiveThresholdState(component, 1.0, "scalar")
        with self.assertRaises(ValueError):
            theorem.match_inverse_couplings(
                {"gY": 40.0, "g2": 40.0, "g3": 40.0},
                [state],
                matching_scale=1.0,
            )
        with self.assertRaises(ValueError):
            theorem.ps_to_sm_tree_match(
                {"gBL": Fraction(1), "g2L": Fraction(1), "g2R": Fraction(1)}
            )

    def test_21_official_full_inventory_pyrate_replay_is_bound(self) -> None:
        bound = self.report["source_binding"]["independent_official_PyRATE3_replay"]
        self.assertEqual(bound["path"], "PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_V20.json")
        flow = self.report["UV_two_loop_gauge_flow"]
        self.assertEqual(flow["all_active_a"], {"SO10": "52/3", "X": "10843"})
        self.assertEqual(flow["all_active_b_nonyukawa"]["SO10"]["X"], "4536")
        self.assertEqual(flow["all_active_b_nonyukawa"]["X"]["SO10"], "204120")

    def test_22_formal_g89_spectrum_is_not_a_dependency(self) -> None:
        paths = {row["path"] for row in self.report["source_binding"].values()}
        self.assertNotIn("EXACT_EFT_PHYSICAL_SCALAR_SPECTRUM_V20.json", paths)
        self.assertEqual(self.report["scheme_and_basis"]["hypercharge"], "Y=T3R+(B-L)/2")

    def test_23_full_g7_stays_fail_closed(self) -> None:
        matrix = self.report["completion_matrix"]
        self.assertTrue(matrix["complete_physical_PS_and_SM_matter_branching"])
        self.assertTrue(matrix["parameterized_one_loop_matter_component_threshold_kernel"])
        for key in (
            "physical_component_pole_mass_matrices",
            "heavy_vector_Goldstone_ghost_thresholds",
            "normalized_Yukawa_tensor_embeddings",
            "full_two_loop_Yukawa_betas",
            "full_51_real_parameter_scalar_tensor_translation",
            "full_two_loop_scalar_quartic_betas",
            "dimension_six_EFT_anomalous_dimension_and_mixing",
            "mathematical_G7_closed",
            "release_G7_verified",
        ):
            self.assertFalse(matrix[key], key)

    def test_24_reports_are_semantically_identical_to_live_build(self) -> None:
        frozen = json.loads(theorem.OUT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(frozen, self.report)
        markdown = theorem.OUT_MD.read_text(encoding="utf-8")
        self.assertEqual(markdown, theorem.render_markdown(self.report))

    def test_25_every_live_check_passes(self) -> None:
        self.assertEqual(self.report["n_checks"], len(self.report["checks"]))
        self.assertEqual(self.report["n_failed"], 0)
        self.assertTrue(all(self.report["checks"].values()))

    def test_26_coupled_uv_rhs_matches_exact_equation(self) -> None:
        point = {"SO10": 40.0, "X": 80.0}
        observed = theorem.uv_nonyukawa_alpha_inverse_rhs(point)
        expected_so10 = -float(Fraction(52, 3)) / (2.0 * math.pi) - (
            float(Fraction(25013, 6)) / point["SO10"]
            + 4536.0 / point["X"]
        ) / (8.0 * math.pi**2)
        expected_x = -10843.0 / (2.0 * math.pi) - (
            204120.0 / point["SO10"] + 7242180.0 / point["X"]
        ) / (8.0 * math.pi**2)
        self.assertAlmostEqual(observed["SO10"], expected_so10, places=14)
        self.assertAlmostEqual(observed["X"], expected_x, places=12)

    def test_27_coupled_uv_integrator_zero_and_reversibility(self) -> None:
        initial = {"SO10": 500.0, "X": 5000.0}
        self.assertEqual(
            theorem.integrate_uv_nonyukawa_gauge_flow(
                initial, log_mu_interval=0.0, steps=1
            ),
            initial,
        )
        forward = theorem.integrate_uv_nonyukawa_gauge_flow(
            initial, log_mu_interval=0.01, steps=100
        )
        backward = theorem.integrate_uv_nonyukawa_gauge_flow(
            forward, log_mu_interval=-0.01, steps=100
        )
        for key in initial:
            self.assertAlmostEqual(backward[key], initial[key], places=10)

    def test_28_coupled_uv_flow_domain_guards_are_adversarial(self) -> None:
        for point in (
            {"SO10": 0.0, "X": 1.0},
            {"SO10": 1.0, "X": -1.0},
            {"SO10": float("nan"), "X": 1.0},
            {"SO10": 1.0, "X": float("inf")},
        ):
            with self.assertRaises(ValueError):
                theorem.uv_nonyukawa_alpha_inverse_rhs(point)
        with self.assertRaises(ValueError):
            theorem.uv_nonyukawa_alpha_inverse_rhs({"g10": 1.0, "X": 1.0})
        with self.assertRaises(ValueError):
            theorem.integrate_uv_nonyukawa_gauge_flow(
                {"SO10": 1.0, "X": 1.0}, log_mu_interval=1.0, steps=0
            )
        with self.assertRaises(ValueError):
            theorem.integrate_uv_nonyukawa_gauge_flow(
                {"SO10": 1.0, "X": 1.0},
                log_mu_interval=float("nan"),
                steps=1,
            )

    def test_29_heavy_vector_provenance_is_counted_but_not_overclaimed(self) -> None:
        vectors = self.report["heavy_vector_provenance_not_yet_matched"]
        self.assertEqual(vectors["SO10_to_PS"]["broken_generators"], "(6,2,2)")
        self.assertEqual(vectors["SO10_to_PS"]["real_vector_dimension"], 24)
        self.assertEqual(vectors["PS_to_SM"]["real_vector_dimension"], 9)
        self.assertEqual(vectors["EW_to_QED"]["real_vector_dimension"], 3)
        self.assertFalse(
            vectors["one_loop_vector_Goldstone_ghost_matching_implemented"]
        )

    def test_30_dimension_mutation_breaks_the_representation_audit(self) -> None:
        corrupted = theorem.PS_BRANCHING["210"][:-1]
        with patch.dict(theorem.PS_BRANCHING, {"210": corrupted}):
            row = theorem.representation_audit("210")
            self.assertFalse(row["dimension_identity"])
            self.assertFalse(row["index_identity"])

    def test_31_signed_bl_mutation_breaks_the_index_audit(self) -> None:
        corrupted = (("3", Fraction(2, 3)), ("1", Fraction(-1)))
        with patch.dict(theorem.SU4_TO_SU3_BL, {"4": corrupted}):
            row = theorem.representation_audit("16")
            self.assertTrue(row["dimension_identity"])
            self.assertFalse(row["index_identity"])


if __name__ == "__main__":
    unittest.main()
