#!/usr/bin/env python3
"""Tests for the exact G6 tree-level threshold spectrum of the SM Pati-Salam G3 witness family (v20).

setUpClass builds one fresh report (about forty seconds, fifteen of them the committed exact source tensors) and
compares it with the committed artifact through target.report_mismatches (exact leaves exactly, the few float
diagnostics within round-off).  The committed artifact is source-agnostic: only the G4 availability triple (state,
available, agrees) may depend on whether the G4 report exists, and it must be either present-and-agreeing or missing;
a second fresh build with the G4 loader pointed at a nonexistent path must match the committed artifact as well,
while an available but disagreeing G4 file must fail.  Independent checks re-derive the spectrum at a third rational point with the committed
exact-Hessian module's own LDL^T inertia routine and re-parse the committed closed forms with sympy.  The mutation
tests change one input each (a coefficient of the symbolic map, a pinned expectation, a binding-unit scalar at one
grid point, a portal id, the G4 report (disagreeing, empty, unreadable, missing) or the candidate report) and require
the report to fail closed (a genuinely missing G4 report only skips the cross-check); G6 must stay BLOCKED in the
committed gate ledger.
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

import sympy

import g3_candidate_physical_target_audit_v20 as target
import g3_sm_pati_salam_candidate_v20 as candidate
import g3_sm_pati_salam_exact_hessian_v20 as hessian
import g6_sm_pati_salam_tree_spectrum_v20 as g6

TIMING_KEYS = {"runtime_seconds", "seconds"}
LEDGER_JSON = g6.ROOT / "G1_G8_GATE_LEDGER_V20.json"
NEVER_TRUE_FLAGS = (
    "loop_level_positivity_certified",
    "electroweak_symmetry_breaking_realized",
    "eps_negative_ewsb_member_certified",
    "coloured_scalars_only_at_M_GUT",
    "uncertainties_complete",
    "G6_gate_wired",
    "report_closes_g6_by_itself",
    "G6_closed",
    "propagator_exactly_r0_independent",
)
LAM, R0, X0, EPS = sympy.symbols("lam r0 x0 eps")


def _strip(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _strip(item) for key, item in value.items() if key not in TIMING_KEYS}
    if isinstance(value, list):
        return [_strip(item) for item in value]
    return value


def _source_agnostic(report: dict[str, Any]) -> dict[str, Any]:
    return _strip(g6.without_g4_availability(report))


def _parse(text: str) -> sympy.Expr:
    return sympy.sympify(text.replace("^", "**"), locals={"lam": LAM, "r0": R0, "x0": X0, "eps": EPS})


def _roots_with_multiplicity(point: dict[str, Fraction], table: list[dict[str, Any]]) -> list[tuple[sympy.Expr, int]]:
    substitution = {R0: sympy.Rational(str(point["r0"])), X0: sympy.Rational(str(point["x0"])), EPS: sympy.Rational(str(point["eps"]))}
    output = []
    for row in table:
        poly = sympy.Poly(_parse(row["polynomial"]).subs(substitution), LAM)
        for root in sympy.real_roots(poly):
            output.append((root, row["multiplicity"]))
    return output


class G6SmPatiSalamTreeSpectrumTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.committed = json.loads(g6.OUT_JSON.read_text(encoding="utf-8"))
        cls.fresh = g6.json_roundtrip(g6.build_report())

    def assertFailsClosed(self, report: dict[str, Any], *expected_failures: str) -> None:
        self.assertEqual(report["status"], g6.STATUS_INCOMPLETE)
        self.assertEqual(report["overall_state"], g6.OVERALL_STATE_OPEN)
        self.assertGreater(report["n_failed"], 0)
        self.assertFalse(report["theorem_claimed"])
        self.assertTrue(report["theorem"].startswith("NOT CLAIMED"))
        self.assertTrue(report["verdict"].startswith("FAIL-CLOSED"))
        self.assertFalse(report["flags"]["theorem_claimed"])
        self.assertFalse(g6.report_passes(report))
        for name in NEVER_TRUE_FLAGS:
            self.assertIs(report["flags"][name], False, name)
        for name in expected_failures:
            self.assertIn(name, report["failures"])

    # ------------------------------------------------------------------
    # Status, checks and the committed artifact.
    # ------------------------------------------------------------------

    def test_all_checks_pass_and_certificate_is_tree_level_only_and_not_wired(self) -> None:
        for report in (self.committed, self.fresh):
            self.assertEqual(report["n_failed"], 0, report["failures"])
            self.assertEqual(report["failures"], [])
            self.assertEqual(report["n_checks"], len(report["checks"]))
            self.assertEqual(report["n_checks"], 81)
            self.assertTrue(all(report["checks"].values()))
            self.assertEqual(report["status"], "G6_SM_PATI_SALAM_TREE_SPECTRUM_EXACT__TREE_LEVEL_ONLY__NOT_WIRED")
            self.assertEqual(report["status"], g6.STATUS_CERTIFIED)
            self.assertEqual(report["overall_state"], g6.OVERALL_STATE_CERTIFIED)
            self.assertEqual(report["model_contract_id"], candidate.MODEL_CONTRACT_ID)
            self.assertEqual(report["gate"], "G6")
            self.assertTrue(report["theorem_claimed"])
            self.assertEqual(report["theorem"], g6.THEOREM)
            self.assertTrue(g6.report_passes(report))
            self.assertIs(report["G6_closed"], False)
            for name in NEVER_TRUE_FLAGS:
                self.assertIs(report["flags"][name], False, name)
            self.assertIs(report["flags"]["one_loop_risk_R1_open"], True)
            for name in (
                "tree_level_proof_grade",
                "tree_spectrum_parametric_in_r0_x0_eps",
                "tree_positivity_for_all_r0_x0_eps_positive",
                "tree_zero_modes_35_positive_451_negative_0",
                "sm_labels_exact_parametric",
                "benchmark_and_physical_member_point_certified",
                "triplet_sub_ledger_block_diagonal",
                "propagator_exact_rational_function_of_r0",
                "axion_closed_form_exact",
                "physical_member_uses_canonical_phi17_scale",
            ):
                self.assertIs(report["flags"][name], True, name)

    def test_committed_artifact_matches_fresh_report(self) -> None:
        self.assertEqual(target.report_mismatches(_source_agnostic(self.committed), _source_agnostic(self.fresh)), [])
        # Only the availability triple may depend on the G4 report: present-and-agreeing or missing, never disagreeing.
        for report in (self.committed, self.fresh):
            self.assertTrue(g6.g4_availability_consistent(report), report["axion"]["g4_crosscheck"])
            self.assertIsNot(report["axion"]["g4_crosscheck"]["agrees"], False)

    def test_committed_artifact_records_no_g4_location(self) -> None:
        crosscheck = self.committed["axion"]["g4_crosscheck"]
        self.assertEqual(
            set(crosscheck), {"G4_report", "compared_at_benchmark", *g6.G4_AVAILABILITY_KEYS}
        )
        self.assertEqual(crosscheck["G4_report"], g6.G4_REPORT_NAME)
        text = g6.OUT_JSON.read_text(encoding="utf-8")
        for fragment in ("_g4_sm_quotient", "sibling", "pre-integration", '"source": "injected"'):
            self.assertNotIn(fragment, text)
        self.assertNotIn("sibling", g6.OUT_MD.read_text(encoding="utf-8"))

    def test_committed_artifact_matches_fresh_build_without_the_g4_file(self) -> None:
        """A fresh build that cannot see any G4 report (loader pointed at a nonexistent path) differs from the committed
        artifact only in the tolerated availability triple."""
        with tempfile.TemporaryDirectory() as directory:
            absent = Path(directory) / "no_such_dir" / g6.G4_REPORT_NAME
            with mock.patch.object(g6, "G4_REPORT_LOCATIONS", (("repository root", absent),)):
                missing = g6.json_roundtrip(g6.build_report())
        self.assertEqual(missing["n_failed"], 0)
        self.assertEqual(
            tuple(missing["axion"]["g4_crosscheck"][key] for key in g6.G4_AVAILABILITY_KEYS), (g6.G4_MISSING, False, None)
        )
        self.assertTrue(g6.g4_availability_consistent(missing))
        self.assertEqual(target.report_mismatches(_source_agnostic(self.committed), _source_agnostic(missing)), [])

    def test_available_but_disagreeing_g4_file_fails_against_the_committed_artifact(self) -> None:
        wrong = {
            "n_failed": 0,
            "status": "file",
            "axion": {
                "axion_norm_squared": "1/2",
                "squared_norm_fractions": {"S": "7225/7241", "Phi17": "16/7241"},
                "decay_constant": {"v_a_squared": "2/7241"},
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / g6.G4_REPORT_NAME
            path.write_text(json.dumps(wrong), encoding="utf-8")
            with mock.patch.object(g6, "G4_REPORT_LOCATIONS", (("repository root", path),)):
                disagreeing = g6.json_roundtrip(g6.build_report())
        self.assertFailsClosed(disagreeing, "axion_agrees_with_G4_report_when_present")
        self.assertFalse(g6.g4_availability_consistent(disagreeing))
        self.assertNotEqual(target.report_mismatches(_source_agnostic(self.committed), _source_agnostic(disagreeing)), [])

    def test_committed_json_is_the_deterministic_rendering(self) -> None:
        text = g6.OUT_JSON.read_text(encoding="utf-8")
        self.assertTrue(text.endswith("\n"))
        self.assertEqual(g6.render_json(self.committed), text)

    def test_markdown_artifact_states_the_certificate(self) -> None:
        text = g6.OUT_MD.read_text(encoding="utf-8")
        for fragment in (
            self.committed["status"],
            g6.THEOREM,
            "Root counts (negative/zero/positive): `0/35/451`",
            "`lam = 1/96*r0^2` | 14 | (1,1)_\\|Y\\|=2: 2, (6,1)_\\|Y\\|=4/3: 12",
            "`lam = 8/9` | 75",
            g6.EXPECTED_PROPAGATOR_SQUARED,
            "28*sqrt(2)*(32 + 117*r0^2)/(1360 + 4316*r0^2 + 117*r0^4)",
            "|a|^2 = `9248/7241`",
            "v_a^2 = `2/7241` M_GUT^2",
            "Period modulo the gauge group: `2 pi/68`",
            "f_a = v_a/N_DW is not computed",
            "0 < eps < 12 - 2|kappa| r0",
            "R1 (one-loop Coleman-Weinberg risk, not certified here)",
            "G6 wiring: no ledger, gate, workflow or README change; G6 stays BLOCKED",
        ):
            self.assertIn(fragment, text)

    # ------------------------------------------------------------------
    # The certificate numbers.
    # ------------------------------------------------------------------

    def test_symbolic_hessian_and_bindings(self) -> None:
        symbolic = self.committed["symbolic_hessian"]
        self.assertEqual(symbolic["monomials"], ["1", "eps", "x0^2", "r0", "r0^2"])
        self.assertIs(symbolic["gradient_identically_zero"], True)
        self.assertEqual(symbolic["gradient_monomials_checked"], ["1", "x0^3", "r0", "r0^2", "r0^3"])
        coverage = symbolic["coverage"]
        self.assertIs(coverage["every_nonzero_parameter_covered"], True)
        self.assertEqual(coverage["uncovered_nonzero_parameters"], [])
        binding = symbolic["binding"]
        for variant in ("benchmark", "raised_O06", "tiny_eps"):
            self.assertIs(binding["committed_variants_at_benchmark"][variant]["equals_committed_exact_hessian"], True)
        self.assertIs(binding["physical_member_equals_direct_recomputation"], True)
        self.assertIs(binding["off_benchmark_point_equals_direct_recomputation"], True)
        self.assertIs(binding["off_benchmark_point_direct_gradient_zero_and_coverage"], True)
        self.assertEqual(binding["off_benchmark_point"], {"r0": "3/37", "x0": "7/5", "eps": "9/9583"})
        grid = symbolic["unit_scalar_grid"]
        self.assertEqual((grid["r0"], grid["x0"]), (["1", "2", "3", "5"], ["1", "3", "7", "11"]))
        self.assertEqual(grid["grid_points"], 16)
        self.assertEqual(grid["nonzero_pieces_checked_per_point"], 50)
        self.assertEqual(grid["max_monomial_power"], 3)
        self.assertEqual(grid["degree_bound_premise"], 3)
        self.assertIs(grid["piece_matrices_identical_on_grid"], True)
        self.assertIs(self.committed["checks"]["unit_piece_scalars_are_monomials_of_degree_le_3_on_4x4_grid"], True)
        self.assertEqual(symbolic["unit_provenance"]["O06 N_H"]["unit_coefficient"], "eps + 1/2*r0^2")
        self.assertEqual(symbolic["unit_provenance"]["re::O12 2 Re[conj(H.H) conj(S)]"]["unit_coefficient"], "-1/4*r0")

    def test_parametric_factor_table(self) -> None:
        spectrum = self.committed["parametric_spectrum"]
        self.assertEqual(spectrum["components"], 65)
        self.assertEqual(len(spectrum["factors"]), 28)
        self.assertEqual(sum(1 for row in spectrum["factors"] if row["degree"] == 1), 24)
        self.assertEqual(tuple((row["polynomial"], row["multiplicity"]) for row in spectrum["factors"]), g6.EXPECTED_FACTOR_TABLE)
        self.assertEqual(sum(row["degree"] * row["multiplicity"] for row in spectrum["factors"]), 486)
        for row in spectrum["factors"]:
            self.assertEqual(sum(row["sm_content_per_root_real"].values()), row["multiplicity"], row["polynomial"])
        by_text = {row["polynomial"]: row for row in spectrum["factors"]}
        expected_content = {
            "lam": g6.EXPECTED_ZERO_MODE_CONTENT,
            "lam - (eps)": {"(1,2)_|Y|=1/2": 4},
            "lam - (1/96*r0^2)": {"(1,1)_|Y|=2": 2, "(6,1)_|Y|=4/3": 12},
            "lam - (37/576*r0^2)": {"(3,1)_|Y|=4/3": 6, "(6,1)_|Y|=1/3": 12},
            "lam - (353/3360*r0^2)": {"(6,1)_|Y|=2/3": 12},
            "lam - (1/2*r0^2)": {"(1,1)_|Y|=0": 1},
            "lam - (4*r0^2)": {"(1,1)_|Y|=0": 1},
            "lam - (1/8*x0^2)": {"(1,1)_|Y|=0": 1},
            "lam - (1 + eps)": {"(3,1)_|Y|=1/3": 6},
            "lam - (1 + eps + r0^2)": {"(3,1)_|Y|=1/3": 6},
            "lam - (5/8 + 37/576*r0^2)": {"(3,1)_|Y|=1/3": 6},
            "lam - (8/9)": {
                "(1,3)_|Y|=0": 3,
                "(3,1)_|Y|=5/3": 6,
                "(3,3)_|Y|=2/3": 18,
                "(8,1)_|Y|=0": 8,
                "(8,1)_|Y|=1": 16,
                "(8,3)_|Y|=0": 24,
            },
            "lam - (12/5)": {"(8,1)_|Y|=0": 8},
        }
        for text, content in expected_content.items():
            self.assertEqual(by_text[text]["sm_content_per_root_real"], content, text)
        cubic = by_text[g6.EXPECTED_FACTOR_TABLE[3][0]]
        self.assertEqual(cubic["sm_content_per_root_real"], {"(3,1)_|Y|=1/3": 6})
        self.assertEqual(cubic["r0_to_0"]["light_branches"]["mu_limits_rational"], ["17/288"])
        self.assertEqual(cubic["r0_to_0"]["light_branches"]["count"], 1)

    def test_parametric_positivity_certificates(self) -> None:
        for row in self.committed["parametric_spectrum"]["factors"]:
            positivity = row["positivity"]
            if row["polynomial"] == "lam":
                self.assertIs(positivity["root_is_zero"], True)
                continue
            self.assertIs(positivity["monomial_sign_certificate_all_positive_parameters"], True, row["polynomial"])
            self.assertIs(positivity["all_roots_positive_for_positive_parameters"], True)
            self.assertIs(positivity["certified"], True)
            if row["variables"] in ([], ["r0"]):
                self.assertIs(positivity["sturm_certificate_0_lt_r0_le_1_5"], True, row["polynomial"])
            if row["degree"] > 1:
                self.assertIs(positivity["discriminant_positive_on_0_lt_r0_le_1_5"], True)

    def test_independent_sympy_positivity_on_sample_r0(self) -> None:
        """Re-parse the committed closed forms and isolate every root exactly at sample points of the interval."""
        table = self.committed["parametric_spectrum"]["factors"]
        for r0 in (Fraction(1, 5), Fraction(1, 7), Fraction(3, 47), Fraction(1, 1000)):
            point = {"r0": r0, "x0": Fraction(3, 2), "eps": r0 * r0 / 1000}
            roots = _roots_with_multiplicity(point, table)
            self.assertEqual(sum(multiplicity for _, multiplicity in roots), 486)  # every root real
            self.assertEqual(sum(multiplicity for root, multiplicity in roots if root == 0), 35)
            self.assertEqual(sum(multiplicity for root, multiplicity in roots if root < 0), 0)
            self.assertEqual(sum(multiplicity for root, multiplicity in roots if root > 0), 451)

    def test_independent_ldl_inertia_at_a_third_point(self) -> None:
        """The committed module's exact LDL^T inertia at a point certified by neither report."""
        r0, x0 = Fraction(3, 37), Fraction(7, 5)
        eps = r0 * r0 / 7
        units = hessian.exact_unit_matrices(r0, x0)
        coefficients = {key: Fraction(value) for key, value in candidate.candidate_coefficients(r0, x0, -r0 / 4, o06_offset=eps).items()}
        coverage = hessian.unit_coefficients(units, coefficients)
        self.assertTrue(coverage["every_nonzero_parameter_covered"] and coverage["coefficients_proportional_to_unit_weights"])
        terms = []
        for unit in units:
            numerator, denominator = unit["hessian"]
            terms.append((coverage["unit_coefficients"][unit["name"]] / denominator, numerator))
        numerator, denominator = hessian.combine(terms, (hessian.TOTAL_DIM, hessian.TOTAL_DIM))
        inertia = hessian.component_inertia(numerator, denominator)
        self.assertEqual((inertia["positive"], inertia["zero"], inertia["negative"]), (451, 35, 0))
        shift = Fraction(37, 576) * r0 * r0
        roots = _roots_with_multiplicity({"r0": r0, "x0": x0, "eps": eps}, self.committed["parametric_spectrum"]["factors"])
        target_shift = sympy.Rational(shift.numerator, shift.denominator)
        expected = (
            sum(m for root, m in roots if root > target_shift),
            sum(m for root, m in roots if root == target_shift),
            sum(m for root, m in roots if root < target_shift),
        )
        shifted = hessian.component_inertia(numerator, denominator, shift=shift)
        self.assertEqual((shifted["positive"], shifted["zero"], shifted["negative"]), expected)
        self.assertEqual(expected[1], 18)

    def test_point_certificates(self) -> None:
        for name in ("benchmark", "physical"):
            certificate = self.committed["point_certificates"][name]
            self.assertEqual(certificate["root_counts"], {"negative": 0, "zero": 35, "positive": 451, "real_roots": 486})
            self.assertEqual(certificate["distinct_levels"], 34)
            self.assertEqual(len(certificate["levels"]), 34)
            for key in (
                "gradient_exactly_zero",
                "component_charpolys_equal_specialised_products",
                "specialised_factors_irreducible_over_Q",
                "specialised_factors_pairwise_distinct",
                "all_roots_real",
                "eigenspaces_semisimple",
                "point_label_check_eigenspace_intersections",
                "weights_sum_to_one_exact",
            ):
                self.assertIs(certificate[key], True, (name, key))
            self.assertEqual(sum(level["real_multiplicity"] for level in certificate["levels"]), 486)
            below = {level["factor_index"] for level in certificate["levels"] if level["below_M_I"] and level["coloured"]}
            self.assertEqual(below, {0, 2, 3, 4, 5})  # Goldstones plus the four light coloured 126bar factors
        benchmark = self.committed["witness"]["points"]["benchmark"]
        self.assertEqual((benchmark["r0"], benchmark["x0"], benchmark["eps"]), ("1/5", "1", "1/2500"))
        physical = self.committed["witness"]["points"]["physical"]
        self.assertEqual(physical["r0"], "51544138/809635808795")
        self.assertEqual(Fraction(physical["x0"]), Fraction(10**17, 9917564798900000))
        self.assertEqual(Fraction(physical["eps"]), Fraction(physical["r0"]) ** 2 / 100)
        levels = {(level["factor_index"], level["root"]): level for level in self.committed["point_certificates"]["benchmark"]["levels"]}
        self.assertEqual(levels[(2, 0)]["mass_squared_exact"], "1/2400")
        self.assertEqual(levels[(1, 0)]["mass_squared_exact"], "1/2500")
        self.assertEqual(levels[(11, 0)]["block_weights_exact"], {"Phi210": "3/28", "Sigma126bar": "25/28"})
        light = levels[(3, 0)]
        self.assertAlmostEqual(light["mass_squared_over_r0_squared"], 0.0589506756688, places=10)
        self.assertGreater(light["block_weights_float"]["Sigma126bar"], 0.9999999)

    def test_sm_labels_and_casimirs(self) -> None:
        labels = self.committed["sm_labels"]
        self.assertTrue(all(labels["checks"].values()))
        self.assertEqual(labels["su3_gram_on_10"][4][7], 2)
        self.assertTrue(all(labels["component_diagonal"].values()))
        for row in self.committed["parametric_spectrum"]["factors"]:
            self.assertIsNotNone(row["sm_multiplets_per_root"])
            for label, count in row["sm_multiplets_per_root"].items():
                self.assertEqual(count * g6.multiplet_real_dimension(label), row["sm_content_per_root_real"][label])

    def test_triplet_sub_ledger_issue_106(self) -> None:
        ledger = self.committed["triplet_sub_ledger_issue_106"]
        self.assertIs(ledger["H_x_nonH_block_identically_zero"], True)
        self.assertIs(ledger["every_unit_H_block_decoupled"], True)
        self.assertIs(ledger["H_linear_portals_identically_zero"], True)
        self.assertIs(ledger["H_linear_portal_ids_all_known"], True)
        expected_ids = set(candidate.H_LINEAR_PORTAL_IDS) | {key.replace("re::", "im::") for key in candidate.H_LINEAR_PORTAL_IDS}
        self.assertEqual(len(expected_ids), 10)
        self.assertEqual(set(ledger["H_linear_portal_coefficients"]), expected_ids)
        self.assertEqual(set(ledger["H_linear_portal_ids_known_to_contract"]), expected_ids)
        self.assertTrue(all(ledger["H_linear_portal_ids_known_to_contract"].values()))
        self.assertTrue(all(value == "0" for value in ledger["H_linear_portal_coefficients"].values()))
        self.assertEqual(ledger["H_triplet_levels"], {"Re": "1 + eps", "Im": "1 + eps + r0^2"})
        self.assertEqual(ledger["H_triplet_component_labels"], ["(3,1)_|Y|=1/3"])
        provenance = ledger["per_operator_provenance_H_block"]
        self.assertEqual(provenance["O46 (3/5) I_1 - I_54 = H^dag(|Phi|^2 - C(Phi))H"]["H_triplet_level_contribution_Re"], "1")
        self.assertEqual(provenance["O06 N_H"]["H_triplet_level_contribution_Im"], "eps + 1/2*r0^2")
        self.assertEqual(provenance["re::O12 2 Re[conj(H.H) conj(S)]"]["H_triplet_level_contribution_Re"], "-1/2*r0^2")
        self.assertEqual(provenance["re::O12 2 Re[conj(H.H) conj(S)]"]["H_triplet_level_contribution_Im"], "1/2*r0^2")
        self.assertTrue(all(row["H_x_nonH_block_identically_zero"] for row in provenance.values()))
        self.assertEqual(len(ledger["phi_sigma_triplet_components"]), 6)
        self.assertIn("O14 Sigma^dag M_Phi Sigma", ledger["phi_sigma_triplet_operator_provenance"])

    def test_propagator_closed_form(self) -> None:
        propagator = self.committed["b_violating_propagator"]
        self.assertIs(propagator["identical_in_all_copies"], True)
        self.assertEqual(len(propagator["copies"]), 6)
        self.assertEqual(propagator["G_Delta_6Sigma_squared"], g6.EXPECTED_PROPAGATOR_SQUARED)
        self.assertEqual(propagator["G_Delta_6Sigma"], "28*sqrt(2)*(32 + 117*r0^2)/(1360 + 4316*r0^2 + 117*r0^4)")
        self.assertEqual(propagator["limit_r0_to_0_squared"], "6272/7225")
        self.assertEqual(propagator["limit_r0_to_0"], "56*sqrt(2)/85")
        self.assertIs(propagator["exactly_r0_independent"], False)
        self.assertIs(propagator["monotone_increasing_on_0_lt_r0_le_1_5"], True)
        self.assertEqual(propagator["relative_second_order_coefficient"], "1313/2720")
        expression = _parse(propagator["G_Delta_6Sigma_squared"])
        self.assertEqual(expression.subs(R0, sympy.Rational(1, 5)), sympy.Rational(propagator["values"]["benchmark"]["G_Delta_6Sigma_squared_exact"]))
        self.assertAlmostEqual(propagator["values"]["benchmark"]["G_Delta_6Sigma_M_GUT_minus2"], 0.947565320539, places=10)
        self.assertLess(abs(propagator["values"]["physical"]["relative_deviation_from_r0_to_0_limit"]), 1.0e-8)
        # g(1/5)/g(0) = h(1/25)/h(0) with h(s) = (117 s + 32)/(117 s^2 + 4316 s + 1360) = 1948625/1916034.
        self.assertAlmostEqual(propagator["relative_variation_on_0_lt_r0_le_1_5"], 1948625 / 1916034 - 1, places=10)
        weights = self.committed["triplet_fragment_weights"]["physical"]["levels"]["3"]["roots"][0]["fragment_weights_float"]
        self.assertGreater(weights[g6.DELTA_FRAGMENT], 0.99999999)

    def test_axion_closed_form(self) -> None:
        axion = self.committed["axion"]
        self.assertIs(axion["axion_norm_squared_equals_closed_form"], True)
        self.assertEqual(axion["axion_norm_squared"], "9248*r0^2*x0^2/(289*x0^2 + 16*r0^2)")
        self.assertEqual(axion["values"]["benchmark"]["axion_norm_squared_M_GUT2"], "9248/7241")
        self.assertEqual(axion["values"]["benchmark"]["S_phase_fraction"], "7225/7241")
        self.assertEqual(axion["values"]["benchmark"]["Phi17_phase_fraction"], "16/7241")
        r0, x0 = Fraction(51544138, 809635808795), Fraction(10**17, 9917564798900000)
        expected = 32 * r0 * r0 * 578 * x0 * x0 / (32 * r0 * r0 + 578 * x0 * x0)
        self.assertEqual(Fraction(axion["values"]["physical"]["axion_norm_squared_M_GUT2"]), expected)
        self.assertEqual(axion["cartan_sum_over_X_sigma_part"], "-5/2")
        # The period modulo the gauge group and the periodicity scale v_a = F_PQ/68 (G4 decay_constant).
        period = axion["period"]
        self.assertEqual(period["period_denominator"], 68)
        self.assertEqual(period["charge_minor_abs"], 68)
        self.assertEqual(period["gcd_qX_S_qX_Phi17"], 1)
        self.assertEqual(period["axion_angle_period_modulo_gauge"], "2 pi/68")
        self.assertIs(period["v_a_squared_equals_closed_form"], True)
        self.assertIn("N_DW", period["f_a_note"])
        self.assertEqual(axion["values"]["benchmark"]["v_a_squared_M_GUT2"], "2/7241")
        v_a_squared = Fraction(axion["values"]["physical"]["v_a_squared_M_GUT2"])
        self.assertEqual(v_a_squared, 2 * r0 * r0 * x0 * x0 / (16 * r0 * r0 + 289 * x0 * x0))
        self.assertEqual(v_a_squared * 68 * 68, expected)
        physical = axion["values"]["physical"]
        self.assertAlmostEqual(physical["F_PQ_GeV_illustrative"] / physical["v_a_GeV_illustrative"], 68.0, places=9)
        self.assertAlmostEqual(physical["v_a_GeV_illustrative"] / 5.2524e10, 1.0, places=3)

    def test_compiler_corroboration_and_routed_caveats(self) -> None:
        corroboration = self.committed["live_compiler_corroboration"]
        self.assertIs(corroboration["all_states_matched"], True)
        self.assertEqual(sorted(corroboration["points"]), ["1/100", "1/1000", "1/5", "M_I/M_GUT"])
        caveats = self.committed["routed_caveats"]
        self.assertEqual(set(caveats), {"sub_M_I_coloured_126bar_states", "positivity_without_EWSB", "phi17_benchmark_scale"})
        self.assertTrue(all(row["resolved"] is False for row in caveats.values()))
        classification = caveats["sub_M_I_coloured_126bar_states"]["tree_level_classification"]
        self.assertIs(classification["complete"], True)
        self.assertEqual([row["factor_index"] for row in classification["coloured_below_M_I"]], [2, 3, 4, 5])
        disclosures = self.committed["disclosures"]
        self.assertIn("NOT certified", disclosures["R1_one_loop"])
        self.assertIn("eps < 0", disclosures["EWSB"])

    def test_g6_stays_blocked_in_the_committed_ledger(self) -> None:
        ledger = json.loads(LEDGER_JSON.read_text(encoding="utf-8"))
        self.assertEqual(ledger["gates"]["G6"]["status"], "BLOCKED")

    # ------------------------------------------------------------------
    # Helpers.
    # ------------------------------------------------------------------

    def test_interval_and_monomial_helpers(self) -> None:
        self.assertTrue(g6._positive_on_interval({(2, 0, 0): Fraction(1)}))
        self.assertFalse(g6._positive_on_interval({(0, 0, 0): Fraction(1, 100), (2, 0, 0): Fraction(-1)}))
        self.assertTrue(g6._positive_on_interval({(0, 0, 0): Fraction(1, 24), (2, 0, 0): Fraction(-1)}))
        self.assertFalse(g6._positive_on_interval({(0, 0, 1): Fraction(1)}))
        grid = g6.unit_scalar_grid()
        self.assertEqual(len(grid), 16)

        def values(function: Any) -> dict[tuple[Fraction, Fraction], Fraction]:
            return {(r0, x0): Fraction(function(r0, x0)) for r0, x0 in grid}

        self.assertEqual(g6._monomial_exponents(values(lambda r0, x0: 3 * r0**2 * x0**2)), (2, 2))
        self.assertEqual(g6._monomial_exponents(values(lambda r0, x0: Fraction(-1, 16) * r0**3)), (3, 0))
        self.assertIsNone(g6._monomial_exponents(values(lambda r0, x0: 0)))
        # Not a monomial of degree <= 3 on the grid: a sum, a degree-4 monomial, one wrong grid value, a missing base point.
        self.assertIs(g6._monomial_exponents(values(lambda r0, x0: r0 + r0**2)), False)
        self.assertIs(g6._monomial_exponents(values(lambda r0, x0: r0**4)), False)
        broken = values(lambda r0, x0: r0 * x0**3)
        broken[(Fraction(5), Fraction(11))] += 1
        self.assertIs(g6._monomial_exponents(broken), False)
        missing_base = values(lambda r0, x0: r0)
        missing_base.pop(g6.GRID_BASE_POINT)
        self.assertIs(g6._monomial_exponents(missing_base), False)

    # ------------------------------------------------------------------
    # Fail-closed mutations.
    # ------------------------------------------------------------------

    def test_mutation_kappa_beyond_the_tuning_fails_closed(self) -> None:
        """kappa = -5 r0/4 with O06 unchanged: the doublet level becomes eps - 2 r0^2 < 0 (negative mode)."""
        report = g6.json_roundtrip(g6.build_report(coefficient_overrides={candidate.O12_ID: "-5*r0/4"}))
        self.assertFailsClosed(
            report,
            "every_other_factor_sign_alternation_certified",
            "symbolic_equals_committed_exact_hessian_eps_0",
            "benchmark_root_counts_0_35_451",
            "physical_root_counts_0_35_451",
            "factor_table_matches_pinned_closed_forms",
        )
        self.assertGreater(report["point_certificates"]["benchmark"]["root_counts"]["negative"], 0)

    def _analysis_with(self, overrides: dict[str, str]) -> dict[str, Any]:
        analysis = dict(g6._analysis())
        analysis["symbolic"] = g6.symbolic_hessian(g6._freeze(overrides))
        return analysis

    def test_mutation_uncovered_portal_fails_closed(self) -> None:
        analysis = self._analysis_with({"re::O15_B01_Phi_Hdag_Sigma": "1/10"})
        self.assertEqual(analysis["symbolic"]["coverage"]["uncovered_nonzero_parameters"], ["re::O15_B01_Phi_Hdag_Sigma"])
        with mock.patch.object(g6, "_analysis", return_value=analysis):
            report = g6.json_roundtrip(g6.build_report())
        self.assertFailsClosed(report, "every_nonzero_parameter_in_exactly_one_unit")

    def test_mutation_broken_stationarity_fails_closed(self) -> None:
        analysis = self._analysis_with({candidate.O05_ID: "1/2 - r0^2/5"})
        self.assertIs(analysis["symbolic"]["gradient_identically_zero"], False)
        with mock.patch.object(g6, "_analysis", return_value=analysis):
            report = g6.json_roundtrip(g6.build_report())
        self.assertFailsClosed(report, "gradient_vanishes_identically_in_r0_x0_eps")

    def test_mutation_pinned_expectations_fail_closed(self) -> None:
        altered = list(g6.EXPECTED_FACTOR_TABLE)
        altered[2] = ("lam - (1/95*r0^2)", 14)
        with mock.patch.object(g6, "EXPECTED_FACTOR_TABLE", tuple(altered)):
            self.assertFailsClosed(g6.json_roundtrip(g6.build_report()), "factor_table_matches_pinned_closed_forms")
        with mock.patch.object(g6, "EXPECTED_PROPAGATOR_SQUARED", "1"):
            self.assertFailsClosed(g6.json_roundtrip(g6.build_report()), "propagator_squared_closed_form")
        with mock.patch.object(g6, "EXPECTED_ZERO_MODE_CONTENT", {"(1,1)_|Y|=0": 35}):
            self.assertFailsClosed(g6.json_roundtrip(g6.build_report()), "zero_modes_are_broken_generators_plus_X_PQ")

    def test_mutation_g4_report_disagreement_fails_closed(self) -> None:
        agreeing = {
            "n_failed": 0,
            "status": "injected",
            "axion": {
                "axion_norm_squared": "9248/7241",
                "squared_norm_fractions": {"S": "7225/7241", "Phi17": "16/7241"},
                "decay_constant": {"v_a_squared": "2/7241"},
            },
        }
        report = g6.json_roundtrip(g6.build_report(g4_report=agreeing))
        self.assertEqual(report["n_failed"], 0)
        self.assertIs(report["axion"]["g4_crosscheck"]["agrees"], True)
        wrong_norm = copy.deepcopy(agreeing)
        wrong_norm["axion"]["axion_norm_squared"] = "1/2"
        self.assertFailsClosed(g6.json_roundtrip(g6.build_report(g4_report=wrong_norm)), "axion_agrees_with_G4_report_when_present")
        wrong_v_a = copy.deepcopy(agreeing)
        wrong_v_a["axion"]["decay_constant"]["v_a_squared"] = "9248/7241"  # F_PQ^2 mistaken for v_a^2
        self.assertFailsClosed(g6.json_roundtrip(g6.build_report(g4_report=wrong_v_a)), "axion_agrees_with_G4_report_when_present")
        no_v_a = copy.deepcopy(agreeing)
        no_v_a["axion"].pop("decay_constant")
        self.assertFailsClosed(g6.json_roundtrip(g6.build_report(g4_report=no_v_a)), "axion_agrees_with_G4_report_when_present")
        failed = copy.deepcopy(agreeing)
        failed["n_failed"] = 1
        self.assertFailsClosed(g6.json_roundtrip(g6.build_report(g4_report=failed)), "axion_agrees_with_G4_report_when_present")

    def test_mutation_empty_or_unreadable_g4_report_fails_closed_and_only_missing_skips(self) -> None:
        empty = g6.json_roundtrip(g6.build_report(g4_report={}))
        self.assertFailsClosed(empty, "axion_agrees_with_G4_report_when_present")
        self.assertEqual(empty["axion"]["g4_crosscheck"]["state"], "unreadable")
        with tempfile.TemporaryDirectory() as directory:
            corrupt = Path(directory) / "corrupt.json"
            corrupt.write_text('{"axion": ', encoding="utf-8")
            blank = Path(directory) / "blank.json"
            blank.write_text("{}", encoding="utf-8")
            listing = Path(directory) / "list.json"
            listing.write_text("[1, 2]", encoding="utf-8")
            absent = Path(directory) / "absent.json"
            for path in (corrupt, blank, listing):
                # An existing but unreadable file decides (never falls through to a later, readable location).
                locations = (("repository root", path), ("sibling", g6.G4_REPORT_LOCATIONS[-1][1]))
                self.assertEqual(g6.load_g4_report(locations)[2], "unreadable", path.name)
                with mock.patch.object(g6, "G4_REPORT_LOCATIONS", (("repository root", path),)):
                    report = g6.json_roundtrip(g6.build_report())
                self.assertFailsClosed(report, "axion_agrees_with_G4_report_when_present")
            with mock.patch.object(g6, "G4_REPORT_LOCATIONS", (("repository root", absent),)):
                missing = g6.json_roundtrip(g6.build_report())
        self.assertEqual(missing["n_failed"], 0)
        self.assertEqual(missing["axion"]["g4_crosscheck"]["state"], "missing")
        self.assertIsNone(missing["axion"]["g4_crosscheck"]["agrees"])
        self.assertIs(missing["axion"]["g4_crosscheck"]["available"], False)

    def test_mutation_unknown_portal_id_fails_closed(self) -> None:
        """A stale or renamed portal id reads as coefficient 0 in the map; it must fail closed, not pass vacuously."""
        with mock.patch.object(g6, "H_LINEAR_PORTAL_IDS", ("re::NOT_A_PARAMETER",)):
            report = g6.json_roundtrip(g6.build_report())
        self.assertFailsClosed(report, "H_linear_portals_identically_zero")
        ledger = report["triplet_sub_ledger_issue_106"]
        self.assertIs(ledger["H_linear_portal_ids_all_known"], False)
        self.assertEqual(ledger["H_linear_portal_coefficients"], {"re::NOT_A_PARAMETER": "0", "im::NOT_A_PARAMETER": "0"})
        with mock.patch.object(g6, "H_LINEAR_PORTAL_IDS", ()):
            self.assertFailsClosed(g6.json_roundtrip(g6.build_report()), "H_linear_portals_identically_zero")

    def test_mutation_non_monomial_unit_scalar_is_detected(self) -> None:
        """One binding-unit scalar changed at a single grid point (5, 11) breaks the monomial identification."""
        original = hessian.binding_units

        def perturbed(r0: Any, x0: Any) -> Any:
            units = original(r0, x0)
            if (Fraction(r0), Fraction(x0)) != (Fraction(5), Fraction(11)):
                return units
            units = list(units)
            unit = dict(units[0])
            scalar, matrix = unit["hessian"][0]
            unit["hessian"] = ((scalar + 1, matrix), *unit["hessian"][1:])
            units[0] = unit
            return tuple(units)

        g6.unit_piece_structure.cache_clear()
        try:
            with mock.patch.object(g6.hessian, "binding_units", perturbed):
                structure = g6.unit_piece_structure()
            self.assertIs(structure["consistent"], False)
            self.assertIs(structure["piece_matrices_identical_on_grid"], True)
        finally:
            g6.unit_piece_structure.cache_clear()
        self.assertIs(g6.unit_piece_structure()["consistent"], True)

    def test_mutation_candidate_report_fails_closed(self) -> None:
        data = json.loads(g6.CANDIDATE_JSON.read_text(encoding="utf-8"))
        wrong_r0 = copy.deepcopy(data)
        wrong_r0["hierarchy"]["r0_physical"] = "1/15708"
        self.assertFailsClosed(g6.json_roundtrip(g6.build_report(candidate_report=wrong_r0)), "physical_r0_physical_matches_candidate_report")
        wrong_state = copy.deepcopy(data)
        state = wrong_state["compiler"]["1/5"]["light_spectrum"]["states"][1]
        state["mass_squared"] = float(state["mass_squared"]) * (1 + 1.0e-6)
        self.assertFailsClosed(
            g6.json_roundtrip(g6.build_report(candidate_report=wrong_state)),
            "compiler_float64_light_spectra_match_parametric_levels_at_4_r0",
        )
        self.assertFailsClosed(g6.json_roundtrip(g6.build_report(candidate_report={})), "physical_M_GUT_matches_candidate_anchor")


if __name__ == "__main__":
    unittest.main()
