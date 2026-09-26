#!/usr/bin/env python3
"""Tests for the exact G4 physical-quotient certificate at the accepted G3 witness (v20).

setUpClass builds one fresh report (about fifteen seconds: the exact tangent matrix and three fresh exact Hessian
certificates) and compares it with the committed artifact through target.report_mismatches: exact leaves must
match exactly, the float64 binding sections only within a loose tolerance.  The mutation tests reuse the
lru_cached exact inputs, change one input each (a committed report, the integer tangent matrix, the PQ charges,
the doublet directions) and require the certificate to fail closed.  The ledger and roadmap texts of G4 are pinned
against the committed artifacts, and G4 must still be OPEN there: this certificate does not wire G4.
"""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from typing import Any
from unittest import mock

import numpy as np

import g3_candidate_physical_target_audit_v20 as target
import g3_sm_pati_salam_exact_hessian_v20 as hessian
import g4_sm_pati_salam_physical_quotient_v20 as g4
import live_g2_canonical_486_field_chart_v20 as chart

TIMING_KEYS = {"runtime_seconds"}
LEDGER_JSON = g4.ROOT / "G1_G8_GATE_LEDGER_V20.json"
ROADMAP_JSON = g4.ROOT / "G1_G8_EXECUTION_ROADMAP_V20.json"
NEVER_TRUE_FLAGS = (
    "G4_closed",
    "G4_wired_into_gate_ledger",
    "report_closes_g4_by_itself",
    "gate_status_changed",
    "internal_candidate_approved",
)


def _strip_timing(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _strip_timing(item) for key, item in value.items() if key not in TIMING_KEYS}
    if isinstance(value, list):
        return [_strip_timing(item) for item in value]
    return value


def _chart_tangents() -> np.ndarray:
    """D M in float64 (chart coordinates), built independently of the exact certificate."""
    matrix = np.asarray(g4.witness_integer_tangent_matrix(), dtype=float)
    scale_u = np.asarray([float(value) for value in hessian.tangent_row_scale()])
    return hessian.congruence_scale()[:, None] * scale_u[:, None] * matrix


class G4SmPatiSalamPhysicalQuotientTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.committed = json.loads(g4.OUT_JSON.read_text(encoding="utf-8"))
        cls.fresh = g4.json_roundtrip(g4.build_report())

    def _mutated(self, **keywords: Any) -> dict[str, Any]:
        return g4.json_roundtrip(g4.build_report(**keywords))

    def assertFailsClosed(self, report: dict[str, Any], *expected_failures: str) -> None:
        self.assertEqual(report["status"], g4.STATUS_INCOMPLETE)
        self.assertEqual(report["overall_state"], g4.OVERALL_STATE_OPEN)
        self.assertGreater(report["n_failed"], 0)
        self.assertFalse(report["theorem_claimed"])
        self.assertTrue(report["theorem"].startswith("NOT CLAIMED"))
        self.assertTrue(report["verdict"].startswith("FAIL-CLOSED"))
        self.assertFalse(report["final_acceptance_test"]["currently_passes"])
        self.assertFalse(report["flags"]["certificate_passes"])
        self.assertFalse(g4.report_passes(report))
        for name in NEVER_TRUE_FLAGS:
            self.assertFalse(report["flags"][name], name)
        for name in expected_failures:
            self.assertIn(name, report["failures"])

    # ------------------------------------------------------------------
    # Status, checks and the committed artifact.
    # ------------------------------------------------------------------

    def test_all_checks_pass_and_certificate_is_claimed_but_not_wired(self) -> None:
        for report in (self.committed, self.fresh):
            self.assertEqual(report["n_failed"], 0, report["failures"])
            self.assertEqual(report["failures"], [])
            self.assertEqual(report["n_checks"], len(report["checks"]))
            self.assertEqual(report["n_checks"], 69)
            self.assertTrue(all(report["checks"].values()))
            self.assertEqual(report["status"], g4.STATUS_CERTIFIED)
            self.assertEqual(report["status"], "G4_SM_PATI_SALAM_PHYSICAL_QUOTIENT_CERTIFIED__G4_NOT_WIRED")
            self.assertEqual(report["overall_state"], g4.OVERALL_STATE_CERTIFIED)
            self.assertEqual(report["model_contract_id"], g4.MODEL_CONTRACT_ID)
            self.assertTrue(report["theorem_claimed"])
            self.assertEqual(report["theorem"], g4.THEOREM)
            self.assertTrue(report["flags"]["certificate_passes"])
            self.assertTrue(report["flags"]["compiler_binding_float64_only"])
            for name in NEVER_TRUE_FLAGS:
                self.assertIs(report["flags"][name], False, name)
            self.assertIs(report["G4_closed"], False)
            self.assertTrue(g4.report_passes(report))
            final = report["final_acceptance_test"]
            self.assertEqual(final["gate"], "G4")
            self.assertEqual(final["required_statement"], g4.G4_REQUIRED_STATEMENT)
            self.assertIs(final["currently_passes"], True)
            self.assertEqual(final["status"], g4.STATUS_CERTIFIED)
            self.assertIs(final["wired_into_gate_ledger"], False)
            self.assertIs(final["closes_g4_by_itself"], False)
            self.assertIn("decision D3", final["wiring_decision"])
            self.assertIn("G4 OPEN", final["wiring_decision"])

    def test_committed_artifact_matches_fresh_report(self) -> None:
        committed = _strip_timing(self.committed)
        fresh = _strip_timing(self.fresh)
        committed_float = {key: committed.pop(key) for key in g4.FLOAT_EVIDENCE_SECTIONS}
        fresh_float = {key: fresh.pop(key) for key in g4.FLOAT_EVIDENCE_SECTIONS}
        self.assertEqual(target.report_mismatches(committed, fresh), [])
        self.assertEqual(
            target.report_mismatches(committed_float, fresh_float, "float_evidence", rel_tol=1.0e-6, abs_tol=1.0e-9), []
        )

    def test_committed_json_is_the_deterministic_rendering(self) -> None:
        text = g4.OUT_JSON.read_text(encoding="utf-8")
        self.assertTrue(text.endswith("\n"))
        self.assertEqual(json.loads(text), self.committed)
        self.assertEqual(g4.render_json(self.committed), text)

    def test_markdown_artifact_states_the_certificate(self) -> None:
        text = g4.OUT_MD.read_text(encoding="utf-8")
        for fragment in (
            self.committed["status"],
            g4.G4_REQUIRED_STATEMENT,
            "**Currently passes:** `True`; wired into the gate ledger: `False`; closes G4 by itself: `False`.",
            "inertia on W `451/1/0`",
            "inertia on W `447/5/0`",
            "|a|^2 = `9248/7241`",
            "S_phase `7225/7241`",
            "Phi17_phase `16/7241`",
            "Sigma_phase `0`",
            "(1,2)_{1/2}",
            "lambda_eff = `127/64`",
            "Wiring: left to the user",
            "live compiler binding (float64, max residual): `0.0`",
            "axion-angle period modulo SO(10) x U(1)_X: `2 pi/68`",
            "v_a^2 = `2/7241` M_GUT^2",
            "unexplained zero or negative modes: `0`",
        ):
            self.assertIn(fragment, text)
        self.assertNotIn("primitive_integer_vector", text)

    def test_ledger_and_roadmap_texts_are_pinned_and_G4_stays_open(self) -> None:
        ledger = json.loads(LEDGER_JSON.read_text(encoding="utf-8"))
        gate = ledger["gates"]["G4"]
        self.assertEqual(gate["status"], "OPEN")
        self.assertEqual(gate["title"], "Gauge quotient, axion directions, and physical Hessian")
        self.assertEqual(gate["open_scope"], list(g4.G4_OPEN_SCOPE))
        self.assertEqual(gate["authoritative_closed_scope"], [])
        roadmap = json.loads(ROADMAP_JSON.read_text(encoding="utf-8"))
        tasks = {task["id"]: task for task in roadmap["tasks"]}
        task = tasks["W3-G4-FULL-GAUGE-QUOTIENT"]
        self.assertEqual(task["status"], "OPEN")
        self.assertEqual(task["acceptance"], g4.W3_G4_ACCEPTANCE)
        coverage = self.committed["g4_open_scope_coverage"]
        self.assertEqual([row["item"] for row in coverage], list(g4.G4_OPEN_SCOPE))
        self.assertTrue(all(row["content_certified"] for row in coverage))
        self.assertIs(coverage[2]["resolved"], False)
        acceptance = self.committed["roadmap_W3_G4_acceptance"]
        self.assertEqual(acceptance["text"], g4.W3_G4_ACCEPTANCE)
        self.assertTrue(acceptance["ranks_compiler_bound"])
        self.assertTrue(acceptance["no_unexplained_zero_or_negative_modes"])

    # ------------------------------------------------------------------
    # The certificate numbers.
    # ------------------------------------------------------------------

    def test_gauge_quotient_rank_certificate_numbers(self) -> None:
        for report in (self.committed, self.fresh):
            gauge = report["gauge_quotient"]
            expected = {
                "SO10": (33, "1", "1/512000000000", 9, "sqrt(2)*(1/32000000000)"),
                "SO10_x_U1X": (34, "4", "1/640000000000", 10, "1/20000000000"),
                "SO10_x_U1X_x_PQ": (35, "-68", "-17/640000000000", 11, "sqrt(2)*(-17/20000000000)"),
            }
            for name, (rank, det, det_u, complex_rows, det_chart) in expected.items():
                cert = gauge["certificates"][name]
                self.assertEqual(cert["rank"], rank)
                self.assertEqual(cert["minor"]["shape"], [rank, rank])
                self.assertEqual(str(cert["minor"]["determinant_integer_M"]), det)
                self.assertEqual(cert["minor"]["determinant_D_u_M"], det_u)
                self.assertEqual(cert["minor"]["complex_block_rows"], complex_rows)
                self.assertEqual(cert["minor"]["determinant_D_chart_M"], det_chart)
                self.assertEqual(cert["null_vector_count"], 12)
                self.assertEqual(cert["null_vector_rank"], 12)
                self.assertEqual(len(cert["right_null_vectors"]), 12)
                self.assertTrue(cert["null_residuals_exactly_zero"])
                self.assertTrue(cert["null_vectors_without_X_or_PQ_coefficient"])
                for vector in cert["right_null_vectors"]:
                    self.assertTrue(all(label.startswith("SO10:") for label in vector["nonzero_coefficients"]))
            self.assertEqual(gauge["ranks"], {"SO10": 33, "SO10_x_U1X": 34, "SO10_x_U1X_x_PQ": 35})
            self.assertTrue(gauge["stabilizer"]["equals_standard_SM_algebra"])
            self.assertEqual(gauge["stabilizer"]["rank_of_SM_basis_plus_null_vectors"], 12)
            self.assertEqual(gauge["U1X_PQ_independence"]["minor"], [[4, 4], [17, 0]])
            self.assertEqual(gauge["U1X_PQ_independence"]["determinant"], -68)
            self.assertEqual(gauge["gauge_quotient_dimension_including_axion"], 452)
            self.assertEqual(gauge["massive_transverse_quotient_dimension"], 451)
            self.assertEqual(gauge["eaten_goldstones"], {"total": 34, "SO10_over_SM": 33, "U1X": 1})
            self.assertIs(gauge["PQ"]["gauged"], False)
            self.assertIs(gauge["PQ"]["eaten"], False)
            self.assertEqual(gauge["PQ"]["rank_increase_over_gauge_orbit"], 1)
            superseded = gauge["superseded_point_values"]
            self.assertEqual(
                (superseded["gauge_rank"], superseded["full_rank"], superseded["gauge_quotient"], superseded["transverse_quotient"]),
                (37, 38, 449, 448),
            )

    def test_float_ranks_of_D_M_agree_independently(self) -> None:
        tangents = _chart_tangents()
        self.assertEqual(np.linalg.matrix_rank(tangents[:, :45]), 33)
        self.assertEqual(np.linalg.matrix_rank(tangents[:, :46]), 34)
        self.assertEqual(np.linalg.matrix_rank(tangents), 35)

    def test_axion_exact_direction_norm_and_composition(self) -> None:
        for report in (self.committed, self.fresh):
            axion = report["axion"]
            self.assertEqual(axion["axion_norm_squared"], "9248/7241")
            self.assertEqual(axion["axion_norm_squared_closed_form_value"], "9248/7241")
            self.assertEqual(axion["decay_constant"]["F_PQ_squared"], "9248/7241")
            self.assertEqual(axion["PQ_tangent_norm_squared"], "8/5")
            self.assertEqual(axion["PQ_tangent_norm_squared_inside_gauge_span"], "11688/36205")
            self.assertEqual(
                axion["composition"],
                {"Sigma_phase": "0", "S_phase": "7225/7241", "Phi17_phase": "16/7241", "Phi210": "0", "H10": "0"},
            )
            self.assertEqual(axion["axion_u_components"], {"S.y": "5780/7241", "Phi17.y": "-272/7241"})
            self.assertEqual(
                axion["axion_chart_components"], {"S.y": "sqrt(2)*(5780/7241)", "Phi17.y": "sqrt(2)*(-272/7241)"}
            )
            self.assertEqual(axion["projection_coefficients"], {"SO10:T[0,1]": "-14450/7241", "U1X": "16/7241"})
            self.assertEqual(
                axion["rank_data"],
                {
                    "rank_T47": 35,
                    "rank_T47_plus_axion": 35,
                    "rank_gauge_46": 34,
                    "rank_gauge_46_plus_axion": 35,
                    "rank_of_gauge_pairing_with_T47": 34,
                    "dim_T35_cap_gauge_complement": 1,
                },
            )
            self.assertIn("QCD anomaly", axion["decay_constant"]["convention"])
            self.assertIn("PQ-violating", axion["decay_constant"]["convention"])
            self.assertEqual(sum(Fraction(value) for value in axion["squared_norm_fractions"].values()), 1)
            # Modulo SO(10) x U(1)_X the axion angle has period 2 pi/68, so v_a = F_PQ/68.
            decay = axion["decay_constant"]
            self.assertEqual(decay["axion_angle_period_modulo_gauge"], "2 pi/68")
            self.assertEqual(decay["v_a_squared"], "2/7241")
            self.assertEqual(Fraction(decay["v_a_squared"]) * 68**2, Fraction(decay["F_PQ_squared"]))
            period = decay["period_certificate"]
            self.assertEqual(
                (period["S_Phi17_charge_minor_det"], period["gcd_qX_S_qX_Phi17"], period["period_denominator"]), (68, 1, 68)
            )
            self.assertEqual(
                period["explicit_gauge_element_units_of_2pi"],
                {"theta_PQ": "1/68", "beta_U1X": "13/17", "so10_generator": "SO10:T[0,1]", "psi_so10": "1/2"},
            )
            self.assertEqual(period["v_a_squared_closed_form_value"], "2/7241")
            self.assertIs(period["SO10_acts_trivially_on_S_and_Phi17"], True)
            self.assertIs(period["H_vanishes_at_q0"], True)
            self.assertIs(period["certified"], True)

    def test_axion_agrees_with_an_independent_float_projection(self) -> None:
        tangents = _chart_tangents()
        gauge, pq = tangents[:, :46], tangents[:, 46]
        coefficients, *_ = np.linalg.lstsq(gauge, pq, rcond=None)
        axion = pq - gauge @ coefficients
        norm_squared = float(axion @ axion)
        self.assertAlmostEqual(norm_squared, 9248 / 7241, places=12)
        self.assertLess(float(np.max(np.abs(gauge.T @ axion))), 1.0e-12)
        for name, block in g4.BLOCK_SLICES.items():
            fraction = float(axion[block] @ axion[block]) / norm_squared
            self.assertAlmostEqual(fraction, float(g4.EXPECTED_AXION_FRACTIONS[name]), places=12)
        self.assertAlmostEqual(axion[chart.S_SLICE.start + 1], np.sqrt(2) * 5780 / 7241, places=12)
        self.assertAlmostEqual(axion[chart.X_SLICE.start + 1], -np.sqrt(2) * 272 / 7241, places=12)
        # The axion-angle period modulo the gauge group, independently in float64 on the live chart vacuum:
        # PQ(pi/34) moves q0 but equals U(1)_X(26 pi/17) exp(pi L_01) q0, with L_01 a pure Sigma phase on q0;
        # PQ(pi/68) is not gauge-equivalent (S, Phi17 are SO(10) singlets and no U(1)_X angle matches both phases).
        state = g4.candidate.candidate_state(g4.R0, g4.X0)
        q0 = chart.pack(state)

        def rotate(vector: np.ndarray, phases: dict[str, float]) -> np.ndarray:
            output = np.array(vector, dtype=float)
            for name, angle in phases.items():
                block = output[g4.BLOCK_SLICES[name]]
                x, y = block[0::2].copy(), block[1::2].copy()
                block[0::2] = np.cos(angle) * x - np.sin(angle) * y
                block[1::2] = np.sin(angle) * x + np.cos(angle) * y
            return output

        def charged(charges: dict[str, int], angle: float) -> dict[str, float]:
            return {name: angle * charges[name] for name in ("Sigma126bar", "H10", "S", "Phi17")}

        moved = rotate(q0, charged(g4.PQ_CHARGES, np.pi / 34))
        self.assertGreater(float(np.linalg.norm(moved - q0)), 1.0e-2)
        gauge_image = rotate(rotate(q0, charged(g4.X_CHARGES, 26 * np.pi / 17)), {"Sigma126bar": np.pi})
        self.assertLess(float(np.max(np.abs(moved - gauge_image))), 1.0e-12)
        sigma_phase = np.zeros(g4.TOTAL_DIM)
        sigma_phase[chart.SIGMA_SLICE.start:chart.SIGMA_SLICE.stop:2] = -q0[chart.SIGMA_SLICE][1::2]
        sigma_phase[chart.SIGMA_SLICE.start + 1:chart.SIGMA_SLICE.stop:2] = q0[chart.SIGMA_SLICE][0::2]
        l01 = chart.gauge_orbit_matrix(state)[:, g4.GENERATOR_LABELS.index("SO10:T[0,1]")]
        self.assertLess(float(np.max(np.abs(l01 - sigma_phase))), 1.0e-12)
        half = rotate(q0, charged(g4.PQ_CHARGES, np.pi / 68))
        s_phase = np.exp(1j * np.arctan2(half[chart.S_SLICE.start + 1], half[chart.S_SLICE.start]))
        for step in range(17):  # the U(1)_X angles 2 pi step/17 that fix Phi17
            self.assertGreater(abs(s_phase - np.exp(4j * 2 * np.pi * step / 17)), 1.0e-2)

    def test_restricted_hessian_and_zero_mode_classification(self) -> None:
        for report in (self.committed, self.fresh):
            restricted = report["restricted_hessian"]
            self.assertEqual(
                restricted["dimensions"],
                {"W": 452, "kernel_T35": 35, "W_cap_kernel_eps_positive": 1, "kernel_T35_plus_D4_tuned": 39, "W_cap_kernel_tuned": 5},
            )
            self.assertEqual(restricted["eps_positive"]["inertia_on_W_positive_zero_negative"], "451/1/0")
            self.assertEqual(restricted["tuned_eps_0"]["inertia_on_W_positive_zero_negative"], "447/5/0")
            self.assertTrue(restricted["tuned_eps_0"]["doublet_orthogonal_to_all_tangents_exact"])
            levels = restricted["eps_positive"]["lowest_levels_for_eps_below_r0sq_over_96"]
            self.assertEqual((levels["eps"], levels["1/2400"], levels["above_1/2400"]), (4, 14, 433))
            self.assertIs(levels["holds"], True)
            self.assertIs(restricted["eps_positive"]["certified"], True)
            self.assertIs(restricted["tuned_eps_0"]["certified"], True)
            self.assertEqual(restricted["eps_positive"]["zero_mode"], "the physical axion a")
            classification = report["zero_mode_classification"]
            self.assertIs(classification["certified"], True)
            eps = classification["eps_positive"]
            self.assertEqual(eps["hessian_inertia_positive_zero_negative"], "451/35/0")
            self.assertEqual(eps["negative_modes"], 0)
            self.assertEqual(eps["zero_modes"], 35)
            self.assertEqual(
                (eps["eaten_goldstones"]["total"], eps["eaten_goldstones"]["SO10_over_SM"], eps["eaten_goldstones"]["U1X"]),
                (34, 33, 1),
            )
            self.assertEqual(eps["physical_axion"], 1)
            self.assertEqual(classification["tuned_eps_0"]["hessian_inertia_positive_zero_negative"], "447/39/0")
            self.assertEqual(classification["tuned_eps_0"]["zero_modes"], 39)
            self.assertEqual(classification["unexplained_zero_or_negative_modes"], 0)

    def test_fresh_exact_hessians_at_the_witness_members(self) -> None:
        for report in (self.committed, self.fresh):
            fresh = report["fresh_exact_hessians"]
            expected = {
                "benchmark": ("0", "447/39/0", "1/2400", 14),
                "raised_O06": ("1/2500", "451/35/0", "1/2500", 4),
                "tiny_eps": ("1/25000000", "451/35/0", "1/25000000", 4),
            }
            for variant, (eps, inertia, smallest, multiplicity) in expected.items():
                row = fresh["variants"][variant]
                self.assertEqual(row["eps"], eps)
                self.assertEqual(row["inertia_positive_zero_negative"], inertia)
                self.assertEqual(row["smallest_nonzero_eigenvalue"], smallest)
                self.assertEqual(row["smallest_nonzero_multiplicity"], multiplicity)
                for key in (
                    "exact_PSD",
                    "kernel_equals_expected_span",
                    "gradient_exactly_zero",
                    "H_u_annihilates_all_47_tangents",
                    "H_u_annihilates_axion",
                    "H_u_doublet_equals_2_eps_doublet",
                    "smallest_nonzero_is_certified",
                ):
                    self.assertIs(row[key], True, (variant, key))
            self.assertEqual(
                fresh["second_level_pencil_at_r0sq_over_100"]["inertia_of_H_u_minus_shift_D_c_squared"],
                {"negative": 39, "zero": 14, "positive": 433},
            )

    def test_light_doublet_exact_SM_label_mass_and_quartic_lift(self) -> None:
        for report in (self.committed, self.fresh):
            light = report["light_doublet"]
            self.assertEqual(light["directions"]["chart_indices"], [222, 224, 226, 228])
            self.assertEqual(light["directions"]["names"], ["H[6].x", "H[7].x", "H[8].x", "H[9].x"])
            values = light["exact_values"]
            self.assertIs(values["colour_generators_vanish"], True)
            self.assertEqual(values["SU2L_casimir"], "3/4")
            self.assertEqual(values["Y_squared"], "1/4")
            self.assertEqual(values["T3L_squared"], "1/4")
            self.assertTrue(light["SM_label"].startswith("(1,2)_{1/2}"))
            self.assertIn("|Y| = 1/2", light["SM_label"])
            self.assertEqual(light["tuned_limit"]["quartic_lift_lambda_eff"], "127/64")
            self.assertEqual(light["tuned_limit"]["zero_modes"], 4)
            self.assertIn("r0^2/96 = 1/2400", light["mass_squared"]["lightest_level_multiplicity_4_for"])

    def test_vector_boson_gram_by_SM_sector(self) -> None:
        for report in (self.committed, self.fresh):
            vectors = report["vector_bosons"]
            self.assertEqual(vectors["gram_rank"], 34)
            rows = {row["sector"]: (row["real_dimension"], row["gamma_eigenvalue"]) for row in vectors["sectors"]}
            self.assertEqual(
                rows,
                {
                    "(8,1)_0": (8, "0"),
                    "(1,3)_0": (3, "0"),
                    "(3,2)_-5/6 + conj": (12, "1"),
                    "(3,2)_1/6 + conj": (12, "27/25"),
                    "(3,1)_2/3 + conj": (6, "2/25"),
                    "(1,1)_1 + conj": (2, "2/25"),
                    "(1,1)_0": (2, None),
                },
            )
            neutral = vectors["neutral_block"]
            self.assertEqual(neutral["characteristic_polynomial"], "lambda (" + g4.NEUTRAL_POLYNOMIAL + ")/125")
            self.assertEqual(neutral["roots_at_t_1"], ["290 - (4/25)*sqrt(3276105)", "290 + (4/25)*sqrt(3276105)"])
            self.assertEqual(
                vectors["characteristic_polynomial_at_unit_couplings"],
                "lambda^12 (lambda - 1)^12 (lambda - 27/25)^12 (lambda - 2/25)^8 (125 lambda^2 - 72500 lambda + 28964)/125",
            )

    def test_float64_bindings(self) -> None:
        for report in (self.committed, self.fresh):
            binding = report["live_compiler_binding"]
            self.assertEqual(binding["live_shape"], [486, 47])
            self.assertLessEqual(binding["maximum_absolute_residual"], 1.0e-12)
            self.assertIs(binding["compiler_binding_passes"], True)
            corroboration = report["float64_corroboration"]
            self.assertIs(corroboration["consistent"], True)
            self.assertIs(corroboration["chart_kinetic_metric_identity"], True)
            spectrum = corroboration["restricted_spectrum_eps_r0sq_over_100"]
            self.assertEqual(
                (
                    spectrum["W_dimension_float"],
                    spectrum["negative_below_minus_1e_minus_10"],
                    spectrum["zero_within_1e_minus_10"],
                    spectrum["positive_above_1e_minus_10"],
                    spectrum["multiplicity_of_eps"],
                    spectrum["multiplicity_of_r0sq_over_96"],
                ),
                (452, 0, 1, 451, 4, 14),
            )
            self.assertAlmostEqual(spectrum["smallest_positive"], 1 / 2500, places=12)

    def test_chart_is_canonically_normalised(self) -> None:
        for report in (self.committed, self.fresh):
            normalisation = report["chart_normalisation"]
            self.assertTrue(all(normalisation["checks"].values()))
            self.assertEqual(normalisation["vacuum_norm_squared_chart"], "79/25")
            self.assertEqual(
                normalisation["metric_D_c_squared_by_block"],
                {"Phi210": [1], "H10": [2], "Sigma126bar": [2], "S": [2], "Phi17": [2]},
            )

    def test_scope_lists_what_is_not_covered(self) -> None:
        for report in (self.committed, self.fresh):
            scope = report["scope"]
            not_covered = " ".join(scope["not_covered"])
            for fragment in ("physical hierarchy point", "loop corrections", "G6 positivity/EWSB", "decision D3", "PQ-violating"):
                self.assertIn(fragment, not_covered)
            self.assertIn("float64", " ".join(scope["float64_evidence_only"]))
            self.assertIn("G4 is NOT wired", report["verdict"])

    # ------------------------------------------------------------------
    # Fail-closed mutations.
    # ------------------------------------------------------------------

    def test_failed_hessian_report_fails_closed(self) -> None:
        base = g4.load_report(hessian.OUT_JSON)
        failed = copy.deepcopy(base)
        failed["n_failed"] = 1
        failed["failures"] = ["tampered"]
        self.assertFailsClosed(self._mutated(hessian_report=failed), "premise_hessian_report")
        not_orbit = copy.deepcopy(base)
        not_orbit["flags"]["eps_family_kernel_equals_symmetry_orbit"] = False
        report = self._mutated(hessian_report=not_orbit)
        self.assertFailsClosed(
            report,
            "premise_hessian_report",
            "restricted__restricted_hessian_inputs_PSD_and_kernel_T35_for_every_eps_positive",
            "restricted__restricted_hessian_psd_one_zero_mode_axion_451_positive",
        )
        # The restricted-Hessian and zero-mode statements are withheld, not printed as if certified.
        restricted = report["restricted_hessian"]["eps_positive"]
        self.assertIs(restricted["certified"], False)
        self.assertIsNone(restricted["inertia_on_W_positive_zero_negative"])
        self.assertIsNone(restricted["zero_mode"])
        self.assertIs(restricted["lowest_levels_for_eps_below_r0sq_over_96"]["holds"], False)
        classification = report["zero_mode_classification"]
        self.assertIs(classification["certified"], False)
        self.assertIsNone(classification["unexplained_zero_or_negative_modes"])
        self.assertIsNone(classification["eps_positive"]["hessian_inertia_positive_zero_negative"])
        self.assertIsNone(classification["eps_positive"]["negative_modes"])
        self.assertIsNone(classification["eps_positive"]["zero_modes"])
        self.assertIsNone(classification["eps_positive"]["eaten_goldstones"])
        self.assertIsNone(classification["tuned_eps_0"]["hessian_inertia_positive_zero_negative"])
        markdown = g4._markdown(report)
        self.assertIn("NOT CLAIMED", markdown)
        self.assertNotIn("inertia on W `451/1/0`", markdown)
        self.assertFailsClosed(self._mutated(hessian_report={}), "premise_hessian_report")

    def test_failed_equality_report_fails_closed(self) -> None:
        failed = copy.deepcopy(g4.load_report(g4.equality.OUT_JSON))
        failed["n_failed"] = 1
        failed["failures"] = ["tampered"]
        self.assertFailsClosed(self._mutated(equality_report=failed), "premise_equality_report")
        wrong_rank = copy.deepcopy(g4.load_report(g4.equality.OUT_JSON))
        wrong_rank["P3_H_S_Phi17_phases"]["tangent_rank"]["rank_so10_plus_X"] = 35
        self.assertFailsClosed(self._mutated(equality_report=wrong_rank), "premise_equality_report")

    def test_failed_candidate_sigma_audit_and_contract_reports_fail_closed(self) -> None:
        candidate_report = copy.deepcopy(g4.load_report(g4.candidate.OUT_JSON))
        candidate_report["light_doublet_quartic"]["lambda_eff"] = "2"
        self.assertFailsClosed(self._mutated(candidate_report=candidate_report), "premise_candidate_report")
        audit_report = copy.deepcopy(g4.load_report(g4.sigma_audit.OUT_JSON))
        audit_report["pair_stabilizers"]["p|sm_singlet_Y0"]["is_sm_type"] = False
        self.assertFailsClosed(self._mutated(sigma_audit_report=audit_report), "premise_sigma_audit_report")
        contract = copy.deepcopy(g4.load_report(g4.CONTRACT_JSON))
        contract["authoritative_contract"]["gauge"] = ["SO(10)", "U(1)_X", "U(1)_PQ"]
        contract["authoritative_contract"]["accidental_global"] = []
        self.assertFailsClosed(
            self._mutated(contract_report=contract),
            "premise_contract_report",
            "gauge__PQ_global_not_gauged_and_not_in_gauge_span",
        )

    def test_corrupted_tangent_fails_closed(self) -> None:
        pristine = np.array(g4.witness_integer_tangent_matrix())
        column = g4.GENERATOR_LABELS.index("SO10:T[0,6]")
        row = int(np.flatnonzero(pristine[chart.PHI_SLICE, column])[0])
        shifted = pristine.copy()
        shifted[row, column] += 1
        self.assertFailsClosed(
            self._mutated(tangent_override=shifted),
            "gauge__tangent_matrix_equals_equality_module_construction",
            "fresh__fresh_eps_r0sq_over_100_inertia_451_35_0_kernel_T35_annihilates_axion",
        )
        dropped = pristine.copy()
        dropped[:, column] = 0
        report = self._mutated(tangent_override=dropped)
        self.assertFailsClosed(
            report,
            "gauge__tangent_matrix_equals_equality_module_construction",
            "gauge__SO10_rank_33_nonzero_33x33_integer_minor",
            "gauge__gauge_quotient_dimension_452",
        )
        self.assertEqual(report["gauge_quotient"]["ranks"]["SO10"], 32)

    def test_gauge_dependent_PQ_charge_fails_closed(self) -> None:
        # PQ = X: the PQ tangent lies in the gauge span, so there is no physical axion.
        report = self._mutated(pq_charges=dict(g4.X_CHARGES))
        self.assertFailsClosed(
            report,
            "gauge__SO10_x_U1X_x_PQ_rank_35_nonzero_35x35_integer_minor",
            "gauge__massive_transverse_quotient_dimension_451",
            "gauge__PQ_global_not_gauged_and_not_in_gauge_span",
            "axion__axion_nonzero",
            "axion__axion_not_in_gauge_span",
            "axion__axion_period_modulo_gauge_2pi_over_68",
        )
        self.assertEqual(report["gauge_quotient"]["ranks"]["SO10_x_U1X_x_PQ"], 34)
        self.assertEqual(report["axion"]["axion_norm_squared"], "0")
        self.assertIsNone(report["axion"]["decay_constant"]["v_a_squared"])
        self.assertIsNone(report["axion"]["decay_constant"]["axion_angle_period_modulo_gauge"])
        # PQ acting on Sigma alone: the Sigma phase is an so(10) Cartan direction, again inside the gauge span.
        sigma_only = {"H10": -2, "Sigma126bar": -2, "S": 0, "Phi17": 0}
        report = self._mutated(pq_charges=sigma_only)
        self.assertFailsClosed(report, "gauge__SO10_x_U1X_x_PQ_rank_35_nonzero_35x35_integer_minor", "axion__axion_nonzero")
        self.assertEqual(report["gauge_quotient"]["ranks"]["SO10_x_U1X_x_PQ"], 34)

    def test_wrong_doublet_label_fails_closed(self) -> None:
        start = chart.H_SLICE.start
        # Im H_6..9: SM-invariant with the same label, but not zero modes of the tuned Hessian.
        imaginary = tuple(start + 2 * index + 1 for index in range(6, 10))
        report = self._mutated(doublet_indices=imaginary)
        self.assertFailsClosed(
            report,
            "doublet__doublet_directions_are_Re_H6_to_H9",
            "doublet__doublet_is_zero_mode_of_tuned_hessian_exact",
            "restricted__tuned_limit_W_inertia_447_5_0_axion_plus_doublet",
        )
        self.assertIsNone(report["restricted_hessian"]["tuned_eps_0"]["inertia_on_W_positive_zero_negative"])
        self.assertIsNone(report["zero_mode_classification"]["unexplained_zero_or_negative_modes"])
        # Re H_0..3: colour components, not an SM-invariant subspace and not a colour singlet.
        colour = tuple(start + 2 * index for index in range(4))
        report = self._mutated(doublet_indices=colour)
        self.assertFailsClosed(
            report,
            "doublet__doublet_span_invariant_under_SM_algebra_exact",
            "doublet__doublet_colour_singlet_exact",
            "doublet__doublet_SU2L_casimir_3_over_4_exact",
        )
        self.assertIsNone(report["light_doublet"]["SM_label"])

    # ------------------------------------------------------------------
    # Artifacts and CLI.
    # ------------------------------------------------------------------

    def test_write_report_is_deterministic(self) -> None:
        report = g4.build_report()
        with tempfile.TemporaryDirectory() as directory:
            out_json = Path(directory) / "certificate.json"
            out_md = Path(directory) / "certificate.md"
            g4.write_report(report, out_json=out_json, out_md=out_md)
            first_json = out_json.read_text(encoding="utf-8")
            first_md = out_md.read_text(encoding="utf-8")
            g4.write_report(report, out_json=out_json, out_md=out_md)
            self.assertEqual(out_json.read_text(encoding="utf-8"), first_json)
            self.assertEqual(out_md.read_text(encoding="utf-8"), first_md)
            self.assertEqual(first_json, g4.render_json(report))
            self.assertTrue(json.loads(first_json)["theorem_claimed"])

    def test_cli_writes_on_request_and_fails_closed(self) -> None:
        report = g4.build_report()
        with mock.patch.object(g4, "build_report", return_value=report), mock.patch.object(g4, "write_report") as writer, \
                mock.patch("builtins.print"):
            self.assertEqual(g4.main(["--write"]), 0)
            writer.assert_called_once_with(report)
        failed = copy.deepcopy(report)
        failed["n_failed"] = 1
        with mock.patch.object(g4, "build_report", return_value=failed), mock.patch.object(g4, "write_report") as writer, \
                mock.patch("builtins.print"):
            self.assertEqual(g4.main([]), 1)
            writer.assert_not_called()


if __name__ == "__main__":
    unittest.main()
