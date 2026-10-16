#!/usr/bin/env python3
"""Tests for the G7 evidence on the decoupled-singlet benchmark BM-DA1 (v20; status-neutral, G7 stays BLOCKED).

setUpClass builds one fresh report (exact SO(10) data and PGJ/MSS/QCD/MV coefficient checks, two integrators on every
alpha = 1 scale, quality and windows; about one second) and compares it with the committed artifact: every non-float
leaf must match exactly, float leaves within the module's declared FLOAT_TOLERANCES, timing keys ignored.  The pins
(statuses, check count, never-true flags, coefficients, loop-labelled Landau scales, windows, verdict phrases) are
asserted here, some re-derived independently from the pinned tables.  Each mutation test changes one input (a PGJ
coefficient, T(120), a research root, the three-loop factor, the RK4 step, the quality exponent, a research sha256,
a research label, the pinned check count) and requires the named checks to fail closed, G7 to stay BLOCKED, every
never-true flag to stay False and ``main --write`` to refuse (with the output paths redirected to a temporary
directory, so the committed artifacts are never touched).
"""
from __future__ import annotations

import contextlib
import copy
import io
import json
import math
import re
import tempfile
import unittest
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any
from unittest import mock

import g7_decoupled_singlet_benchmark_evidence_v20 as g7

TIMING_KEYS = {"runtime_seconds"}
M_PL_RED = 2.435e18


def _strip_timing(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _strip_timing(item) for key, item in value.items() if key not in TIMING_KEYS}
    if isinstance(value, list):
        return [_strip_timing(item) for item in value]
    return value


def _mismatches(committed: Any, fresh: Any, path: str = "") -> list[str]:
    """Paths where two JSON trees differ: floats within FLOAT_TOLERANCES, every other leaf exactly."""
    if isinstance(committed, dict) and isinstance(fresh, dict):
        if set(committed) != set(fresh):
            return [f"{path}: keys differ {sorted(set(committed) ^ set(fresh))}"]
        return [m for key in sorted(committed) for m in _mismatches(committed[key], fresh[key], f"{path}.{key}")]
    if isinstance(committed, list) and isinstance(fresh, list):
        if len(committed) != len(fresh):
            return [f"{path}: length {len(committed)} != {len(fresh)}"]
        return [m for i, (a, b) in enumerate(zip(committed, fresh)) for m in _mismatches(a, b, f"{path}[{i}]")]
    if isinstance(committed, bool) or isinstance(fresh, bool):
        return [] if committed is fresh else [f"{path}: {committed!r} != {fresh!r}"]
    if isinstance(committed, float) or isinstance(fresh, float):
        if not (isinstance(committed, (int, float)) and isinstance(fresh, (int, float))):
            return [f"{path}: {committed!r} != {fresh!r}"]
        rel, abs_tol = g7.FLOAT_TOLERANCES["rel"], g7.FLOAT_TOLERANCES["abs"]
        ok = abs(committed - fresh) <= max(rel * max(abs(committed), abs(fresh)), abs_tol)
        return [] if ok else [f"{path}: {committed!r} != {fresh!r}"]
    return [] if committed == fresh else [f"{path}: {committed!r} != {fresh!r}"]


class G7DecoupledSingletBenchmarkEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.committed = json.loads(g7.OUT_JSON.read_text(encoding="utf-8"))
        cls.fresh = g7.json_roundtrip(g7.build_report())

    # ------------------------------------------------------------------
    # Status, checks and flags.
    # ------------------------------------------------------------------

    def test_status_checks_and_flags(self) -> None:
        self.assertEqual(g7.EXPECTED_N_CHECKS, 46)
        self.assertEqual(
            g7.EXPECTED_SECTION_COUNTS,
            {"coefficients": 12, "running": 9, "landau_cost": 4, "quality": 5, "windows": 5, "uncertainty": 3,
             "planck_kinetic": 2, "research_record": 4, "verdict": 1, "scope": 1},
        )
        for report in (self.committed, self.fresh):
            self.assertEqual(report["n_failed"], 0, report["failures"])
            self.assertEqual(report["failures"], [])
            self.assertEqual(report["n_checks"], g7.EXPECTED_N_CHECKS)
            self.assertEqual(len(report["checks"]), g7.EXPECTED_N_CHECKS)
            self.assertTrue(all(report["checks"].values()))
            self.assertEqual(dict(Counter(key.split(".")[0] for key in report["checks"])), g7.EXPECTED_SECTION_COUNTS)
            self.assertEqual(report["status"], g7.STATUS_RECORDED)
            self.assertEqual(report["overall_state"], g7.OVERALL_STATE_RECORDED)
            self.assertEqual(report["G7_status"], "BLOCKED")
            self.assertEqual(report["gate"], "G7")
            self.assertEqual(report["module"], "g7_decoupled_singlet_benchmark_evidence_v20")
            self.assertEqual(report["model_contract_id"], "gauged_u1x_phi17_v20")
            for name in g7.DERIVED_FLAGS:
                self.assertIs(report["flags"][name], True, name)
            for name in g7.NEVER_TRUE_FLAGS:
                self.assertIs(report["flags"][name], False, name)
            self.assertEqual(set(report["flags"]), set(g7.DERIVED_FLAGS) | set(g7.NEVER_TRUE_FLAGS))
            self.assertTrue(g7.report_passes(report))
            for section, label in (
                ("coefficients", "EXACT"),
                ("running", "NUM"),
                ("landau_cost", "NUM"),
                ("quality", "NUM"),
                ("windows", "NUM, CONDITIONAL"),
                ("uncertainty", "NUM"),
                ("research_record", "RESEARCH_RECORD"),
            ):
                self.assertEqual(report[section]["label"], label, section)
            self.assertTrue(report["planck_kinetic"]["label"].startswith("EST"))

    def test_status_strings_and_never_true_flags(self) -> None:
        self.assertEqual(
            g7.STATUS_RECORDED,
            "G7_DECOUPLED_SINGLET_BENCHMARK_BM_DA1__TWO_LOOP_PASS__THREE_LOOP_WITHIN_TWO_CODE_ROOT_UNCERTAINTY"
            "__RG_IMPROVED_QUALITY_FAIL_CONDITIONAL__G7_BLOCKED",
        )
        self.assertEqual(g7.STATUS_INCOMPLETE, "G7_DECOUPLED_SINGLET_BENCHMARK_EVIDENCE_INCOMPLETE__G7_BLOCKED")
        for status in (g7.STATUS_RECORDED, g7.STATUS_INCOMPLETE):
            self.assertTrue(status.endswith("__G7_BLOCKED"), status)
        self.assertEqual(
            set(g7.NEVER_TRUE_FLAGS),
            {"G7_closed", "gate_status_changed", "wired_into_gate_ledger", "report_closes_G7_by_itself", "benchmark_adopted",
             "three_loop_includes_yukawa_quartic", "planck_kinetic_term_computed", "G6_closed_assumed_true"},
        )
        self.assertEqual(
            set(g7.PHYSICS_FLAGS),
            {"bm_da1_two_loop_pass_both_roots", "bm_da1_three_loop_fail_on_U1_root",
             "bm_da1_three_loop_marginal_pass_on_U2_root", "bm_da1_rg_improved_quality_fail_conditional",
             "bm_e_three_loop_fail_both_roots", "integrators_agree"},
        )
        # The withdrawn over-strong names must not come back.
        for name in ("bm_da1_three_loop_fail", "bm_da1_rg_improved_quality_fail"):
            self.assertNotIn(name, g7.PHYSICS_FLAGS)
        self.assertNotIn("THREE_LOOP_AND_QUALITY_FAIL", g7.STATUS_RECORDED)

    def test_model_contract_id_matches_candidate(self) -> None:
        import g3_sm_pati_salam_candidate_v20 as candidate

        self.assertEqual(g7.MODEL_CONTRACT_ID, candidate.MODEL_CONTRACT_ID)

    def test_committed_artifact_matches_fresh_report(self) -> None:
        self.assertEqual(_mismatches(_strip_timing(self.committed), _strip_timing(self.fresh)), [])

    def test_committed_markdown_regenerates(self) -> None:
        expected = g7._markdown(self.committed).replace("\r\n", "\n")
        self.assertEqual(g7.OUT_MD.read_text(encoding="utf-8").replace("\r\n", "\n"), expected)

    def test_tampered_artifact_is_detected(self) -> None:
        tampered = copy.deepcopy(self.committed)
        tampered["checks"]["running.bm_da1_two_loop_pass_three_loop_fail_on_U1_root"] = False
        self.assertNotEqual(_mismatches(_strip_timing(self.committed), _strip_timing(tampered)), [])
        tampered = copy.deepcopy(self.committed)
        tampered["coefficients"]["so10_phase_b"]["no_PQR"][2] = "132706058/864"
        self.assertNotEqual(_mismatches(_strip_timing(self.committed), _strip_timing(tampered)), [])
        tampered = copy.deepcopy(self.committed)
        tampered["running"]["benchmarks"]["BM-DA1"]["alpha_one_GeV"]["PQR_at_x0p"]["3L_gauge_only"] *= 1.0 + 1.0e-4
        self.assertNotEqual(_mismatches(_strip_timing(self.committed), _strip_timing(tampered)), [])

    def test_import_has_no_side_effects_and_no_scratch_paths(self) -> None:
        source = Path(g7.__file__).read_text(encoding="utf-8")
        for forbidden in ("AppData", "scratchpad\\", "C:\\\\Users", "open(", ".read_text("):
            self.assertNotIn(forbidden, source, forbidden)
        self.assertIs(self.fresh["provenance"]["never_reads_scratch_at_runtime"], True)
        self.assertEqual(self.fresh["provenance"]["repository_inputs"][0].split(" ")[0], "two_loop_thresholds_v20")

    # ------------------------------------------------------------------
    # (A) Exact coefficients, some re-derived independently here.
    # ------------------------------------------------------------------

    def test_exact_coefficient_pins(self) -> None:
        coeff = self.fresh["coefficients"]
        self.assertEqual(coeff["so10_phase_b"]["no_PQR"], ["28/3", "22283/6", "132706057/864"])
        self.assertEqual(coeff["so10_phase_b"]["with_PQR"], ["52/3", "25013/6", "109873879/864"])
        self.assertEqual(coeff["mv_cross_check"]["no_PQR"], ["28/3", "22283/6"])
        self.assertEqual(coeff["mv_cross_check"]["with_PQR"], ["52/3", "25013/6"])
        reps = {name: (data["dim"], data["T"], data["C2"]) for name, data in coeff["so10_reps"].items()}
        self.assertEqual(reps, {name: tuple(value) for name, value in g7.EXPECTED_SO10_REPS.items()})
        self.assertEqual(reps["120"], (120, "28", "21/2"))
        self.assertEqual(reps["210"], (210, "56", "12"))
        self.assertEqual(coeff["qcd_general_casimirs"]["residuals_b_plus_beta_1L_2L_3L"], ["0", "0", "0"])
        self.assertEqual(coeff["qcd_general_casimirs"]["numeric_b3"], {"5": "-9769/54", "6": "65/2"})
        self.assertEqual(coeff["mss_eq5"]["residuals"], {g: ["0", "0", "0"] for g in ("U1_Y", "SU2_L", "SU3_C")})
        self.assertEqual(coeff["mss_eq5"]["values_at_nG_3"]["U1_Y"][2], "-388613/24000")
        self.assertEqual(coeff["mss_eq5"]["values_at_nG_3"]["SU2_L"][2], "324953/1728")
        self.assertEqual(coeff["mss_eq5"]["values_at_nG_3"]["SU3_C"][2], "65/2")
        segments = coeff["chain_segments"]
        self.assertEqual(segments["SM_1HDM+all_remnants"]["b"], ["53/6", "-19/6", "-25/6"])
        self.assertEqual(segments["PS_witness"]["b"], ["-23/3", "-3", "11/3"])
        self.assertEqual(segments["PS_witness"]["bij"], [["643/6", "9/2", "153/2"], ["45/2", "8", "3"], ["765/2", "3", "584/3"]])
        self.assertEqual(segments["PS_witness+5pairs"]["b"], ["17/3", "31/3", "17"])
        self.assertEqual(coeff["remnant_delta_b"]["(6,1)_4/3"], ["32/15", "0", "5/6"])
        for name, (b, bij) in g7.U1_BETAS.items():
            self.assertEqual(segments[name], {"b": list(b), "bij": [list(row) for row in bij]}, name)
        # Independent one- and two-loop coefficients of the SO(10) phase from the (T, C2) table:
        # b1 = -11/3 C_G + 2/3 sum_Weyl T + 1/6 sum_real T; b2 = -34/3 C_G^2 + sum_Weyl T (2 C2 + 10/3 C_G)
        # + sum_real T (2 C2 + 1/3 C_G).
        table = {name: (Fraction(t), Fraction(c)) for name, (_d, t, c) in g7.EXPECTED_SO10_REPS.items()}
        weyl = [("16", 13)]
        real = [("210", 1), ("126bar", 2), ("10", 2)]

        def b12(weyl_content: list[tuple[str, int]]) -> tuple[Fraction, Fraction]:
            cg = Fraction(8)
            b1 = -Fraction(11, 3) * cg + sum(Fraction(2, 3) * n * table[r][0] for r, n in weyl_content) + sum(
                Fraction(1, 6) * n * table[r][0] for r, n in real)
            b2 = -Fraction(34, 3) * cg**2 + sum(n * table[r][0] * (2 * table[r][1] + Fraction(10, 3) * cg) for r, n in weyl_content) + sum(
                n * table[r][0] * (2 * table[r][1] + Fraction(1, 3) * cg) for r, n in real)
            return b1, b2

        self.assertEqual(b12(weyl), (Fraction(28, 3), Fraction(22283, 6)))
        self.assertEqual(b12([("16", 19)]), (Fraction(52, 3), Fraction(25013, 6)))
        options = coeff["landau_options_b"]
        for key, (lo, hi) in g7.EXPECTED_OPTION_B.items():
            self.assertEqual(options[key], {"below_PQR": list(lo), "above_PQR": list(hi)}, key)
        self.assertEqual(options["+120_H"]["below_PQR"], ["56/3", "30235/6", "100917097/864"])
        self.assertEqual(options["+second 126bar"]["below_PQR"], ["21", "11301/2", "3765131/32"])

    # ------------------------------------------------------------------
    # (B)-(G) Loop-labelled numbers.
    # ------------------------------------------------------------------

    def test_loop_labelled_benchmark_scales(self) -> None:
        running = self.fresh["running"]
        self.assertEqual(running["loop_labels"], ["1L", "2L", "3L_gauge_only"])
        for entry in running["benchmarks"].values():
            for placement in ("PQR_at_x0p", "PQR_at_max_x0p_MPlred"):
                self.assertEqual(set(entry["alpha_one_GeV"][placement]), {"1L", "2L", "3L_gauge_only"})
        da1 = running["benchmarks"]["BM-DA1"]["alpha_one_GeV"]
        self.assertLess(abs(da1["PQR_at_x0p"]["1L"] / 1.24858e21 - 1), 1.0e-5)
        self.assertLess(abs(da1["PQR_at_x0p"]["2L"] / 3.72351e18 - 1), 1.0e-5)
        self.assertLess(abs(da1["PQR_at_x0p"]["3L_gauge_only"] / 2.34352e18 - 1), 1.0e-5)
        self.assertLess(abs(da1["PQR_at_max_x0p_MPlred"]["3L_gauge_only"] / 2.4556e18 - 1), 1.0e-4)
        self.assertGreater(da1["PQR_at_x0p"]["2L"], M_PL_RED)
        self.assertLess(da1["PQR_at_x0p"]["3L_gauge_only"], M_PL_RED)
        miss = da1["PQR_at_x0p"]["3L_gauge_only"] / M_PL_RED - 1
        self.assertTrue(-0.04 < miss < -0.035, miss)
        bme = running["benchmarks"]["BM-E"]["alpha_one_GeV"]["PQR_at_x0p"]
        self.assertLess(abs(bme["2L"] / 3.58400e18 - 1), 1.0e-5)
        self.assertLess(abs(bme["3L_gauge_only"] / 2.26665e18 - 1), 1.0e-5)
        drho = running["benchmarks"]["D_rho1e3"]["alpha_one_GeV"]["PQR_at_x0p"]
        self.assertLess(abs(drho["2L"] / 7.45006e18 - 1), 1.0e-5)
        self.assertLess(abs(drho["3L_gauge_only"] / 4.69074e18 - 1), 1.0e-5)
        agreement = running["integrator_agreement"]
        self.assertLessEqual(agreement["max_rel_I1_I2"], 1.0e-6)
        self.assertEqual(agreement["missing_on_one_side"], [])
        self.assertGreaterEqual(agreement["n_pairs"], 100)
        root = running["benchmarks"]["BM-DA1"]["root_RESEARCH_RECORD_INPUT"]
        self.assertEqual(root["alpha_U_inv"], 23.915307659746492)
        self.assertEqual(root["x0p_GeV"], 1.5331635730399654e18)
        # Second-code (U2) roots through the same integrators (x0/p of the U1 BM-DA1 root).
        u2 = running["u2_roots"]
        self.assertLess(abs(u2["x0_over_p_BM_DA1_U1"] - 10.0831204) , 1.0e-6)
        u2_da1 = u2["runs"]["BM-DA1"]
        self.assertLess(abs(u2_da1["root_RESEARCH_RECORD_INPUT"]["x0p_GeV"] / 1.63974e18 - 1), 1.0e-5)
        self.assertLessEqual(u2_da1["p_rel_dev_vs_recorded_M_GUT_chart"], 1.0e-9)
        self.assertLess(abs(u2_da1["alpha_one_GeV"]["2L"] / 3.87714e18 - 1), 1.0e-5)
        self.assertLess(abs(u2_da1["alpha_one_GeV"]["3L_gauge_only"] / 2.43844e18 - 1), 1.0e-5)
        self.assertTrue(0.001 < u2_da1["margin_vs_MPlred"]["3L_gauge_only"] < 0.002)
        self.assertLess(u2["runs"]["BM-E"]["alpha_one_GeV"]["3L_gauge_only"], M_PL_RED)
        self.assertGreater(u2["runs"]["D_rho1e3"]["alpha_one_GeV"]["3L_gauge_only"], M_PL_RED)

    def test_landau_cost_table(self) -> None:
        spec = {  # 4-digit table of the rescue study (2L, 3L_gauge_only), P,Q,R at x0 p
            "baseline": (3.7235e18, 2.3435e18), "+real 45": (3.0320e18, 1.9923e18), "+real 45 +1VL": (2.2620e18, 1.5544e18),
            "+complex 45": (2.5180e18, 1.7134e18), "+second 126bar": (8.1240e17, 6.6673e17), "+10_F": (3.4198e18, 2.1897e18),
            "+2VL": (2.0452e18, 1.4156e18), "+120_H": (1.0833e18, 8.4955e17), "+120_H +real 45": (9.6468e17, 7.8403e17),
        }
        options = self.fresh["landau_cost"]["options"]
        self.assertEqual(set(options), set(spec))
        for key, (two, three) in spec.items():
            values = options[key]["alpha_one_GeV"]
            self.assertLess(abs(values["2L"] / two - 1), 1.0e-4, key)
            self.assertLess(abs(values["3L_gauge_only"] / three - 1), 1.0e-4, key)
            self.assertIs(options[key]["passes_reduced_Planck_criterion"]["3L_gauge_only"], False, key)
        for key in ("+120_H", "+120_H +real 45", "+second 126bar", "+2VL", "+real 45 +1VL"):
            self.assertIs(options[key]["passes_reduced_Planck_criterion"]["2L"], False, key)
        for key in ("baseline", "+real 45", "+complex 45", "+10_F"):
            self.assertIs(options[key]["passes_reduced_Planck_criterion"]["2L"], True, key)

    def test_quality_numbers(self) -> None:
        quality = self.fresh["quality"]
        g6 = quality["bm_da1_g6_masses"]["quality"]["0.30"]
        self.assertLess(abs(g6["dtheta_NDA"] / 1.443e-14 - 1), 1.0e-3)
        self.assertLess(abs(g6["dtheta_Z17"] / 2.527e-20 - 1), 1.0e-3)
        self.assertTrue(g6["NDA_ok"] and g6["Z17_ok"])
        d3 = quality["rg_improved_rho1e3"]
        self.assertLess(abs(d3["v_R_GeV"] / 8.5604e9 - 1), 1.0e-4)
        q = d3["quality"]["0.30"]
        self.assertLess(abs(q["S_vev_GeV"] / 2.8535e13 - 1), 1.0e-4)
        self.assertLess(abs(q["dtheta_NDA"] / 0.2737 - 1), 1.0e-3)
        self.assertLess(abs(q["dtheta_Z17"] / 3.240e-6 - 1), 1.0e-3)
        self.assertFalse(q["NDA_ok"] or q["Z17_ok"])
        # Independent arithmetic of the two quality formulas at the RG-improved root.
        s_vev = 1000.0 * d3["v_R_GeV"] / 0.30
        self.assertAlmostEqual(q["dtheta_NDA"] / (2 * s_vev**16 / (0.0755**4 * M_PL_RED**12)), 1.0, places=12)
        self.assertAlmostEqual(q["dtheta_Z17"] / (6.47e-37 * (math.sqrt(2) * s_vev / 6.31e11) ** 17), 1.0, places=12)
        self.assertEqual(d3["label"], "NUM, CONDITIONAL")
        self.assertTrue(any("anti-SOS" in item for item in d3["conditional_on"]))
        self.assertTrue(any("GUT scalar" in item for item in d3["conditional_on"]))
        self.assertLess(abs(q["dtheta_NDA_Ms"] / 1.1781e-9 - 1), 1.0e-3)
        variants = quality["scheme_variants_rho1e3"]["rows"]
        self.assertEqual(set(variants), {f"U1:{name}" for name in g7.E5_U1_VARIANTS_RHO1E3} | {"U2"})
        x2 = variants["U1:gut_mass_x2"]
        self.assertLess(abs(x2["root_RESEARCH_RECORD_INPUT"]["v_R_GeV"] / 1.961e9 - 1), 1.0e-3)
        self.assertLess(abs(x2["quality"]["0.30"]["dtheta_NDA"] / 1.574e-11 - 1), 1.0e-3)
        self.assertLess(abs(x2["quality"]["0.30"]["dtheta_Z17"] / 4.268e-17 - 1), 1.0e-3)
        self.assertTrue(0.98 < x2["margin_vs_MPlred"]["3L_gauge_only"] < 0.99)
        for name, row in variants.items():
            if name != "U1:gut_mass_x2":
                self.assertFalse(any(q["Z17_ok"] for q in row["quality"].values()), name)
        self.assertLess(abs(variants["U2"]["quality"]["0.30"]["dtheta_NDA"] / 0.18697 - 1), 1.0e-3)
        self.assertLess(abs(variants["U2"]["quality"]["0.30"]["dtheta_Z17"] / 2.1613e-6 - 1), 1.0e-3)
        self.assertEqual(quality["bm_e"]["e2_hard_coded_flags"], {"NDA_quality_ok(vR<=2.2e9)": False, "Z17_quality_ok(vR<=4.6e9)": False})
        self.assertTrue(quality["bm_e"]["quality"]["0.30"]["NDA_ok"])
        self.assertIn("NOT used", quality["convention"])
        self.assertIn("Lambda = max(M_s, <S>) = <S>", quality["convention"])
        self.assertIn("eq. (qualitybound), which uses Lambda = M_s", quality["convention"])

    def test_windows(self) -> None:
        windows = self.fresh["windows"]
        self.assertEqual(len(windows["rows"]), 24)
        for variant in ("D", "D_best"):
            for ys in ("0.30", "0.34"):
                self.assertEqual(windows["windows"][variant][ys], {k: list(v) for k, v in g7.EXPECTED_WINDOWS[variant].items()})
        self.assertEqual(windows["windows"]["D"]["0.30"]["3L_and_Z17"], ["2.55", "2.60", "2.65", "2.75"])
        self.assertEqual(windows["windows"]["D"]["0.30"]["3L_and_NDA"], ["2.55"])
        self.assertEqual(windows["windows"]["D_best"]["0.30"]["3L_and_Z17"], ["2.50"])
        self.assertEqual(windows["windows"]["D_best"]["0.30"]["3L_and_NDA"], [])
        # eq. (qualitybound) of the manuscript (Lambda = M_s): the NDA windows are convention-dependent.
        self.assertEqual(windows["windows"]["D"]["0.30"]["3L_and_NDA_Ms"], ["2.55", "2.60", "2.65", "2.75"])
        self.assertEqual(windows["windows"]["D_best"]["0.30"]["3L_and_NDA_Ms"], ["2.50", "2.75"])
        self.assertIn("convention-dependent", windows["window_definition"])
        knife = windows["knife_edge"]
        self.assertLess(abs(knife["3L_gauge_only_PQR_at_x0p_GeV"] / 2.444e18 - 1), 1.0e-3)
        self.assertTrue(0 < knife["margin_vs_MPlred"] < 0.005)
        self.assertLess(abs(knife["dtheta_NDA_ys0.30"] / 6.55e-11 - 1), 1.0e-2)
        self.assertEqual(windows["label"], "NUM, CONDITIONAL")
        self.assertTrue(any("anti-SOS" in item for item in windows["conditional_on"]))
        self.assertTrue(any("Yukawa" in item for item in windows["conditional_on"]))
        self.assertLessEqual(windows["record_max_rel_deviation"], 1.0e-6)
        self.assertEqual(windows["e6_duplicated_landau_columns"]["keys"], [["D", "2.00"]])

    def test_uncertainty_and_planck_kinetic(self) -> None:
        unc = self.fresh["uncertainty"]
        for name, value in {"BM-DA1": 1.589, "BM-E": 1.581, "D_rho1e3": 1.588}.items():
            self.assertLess(abs(unc["scale_ratio_2L_over_3L"][name] - value), 1.0e-3, name)
        ratios = unc["term_ratio_3L_over_2L_at_MPlred"]
        for name, value in {"BM-DA1": 0.320, "BM-E": 0.337, "D_rho1e3": 0.186}.items():
            self.assertLess(abs(ratios["benchmarks"][name] - value), 1.0e-3, name)
        low, high = ratios["range_over_window_rows"]
        self.assertLess(low, 0.186)
        self.assertGreater(high, 0.337)
        self.assertIn("not a computed range", ratios["research_quote_RESEARCH_RECORD_only"])
        sensitivity = unc["b3_sensitivity_BM_DA1"]
        for key, value in {"x0.5": 2.899e18, "x0.75": 2.598e18, "x1.25": 2.125e18}.items():
            self.assertLess(abs(sensitivity[key]["I2"] / value - 1), 1.0e-3, key)
        planck = self.fresh["planck_kinetic"]
        self.assertLess(abs(planck["delta_alpha_inv_per_unit_c_EST"]["BM-DA1"] - 0.765), 1.0e-3)
        self.assertLess(abs(planck["delta_alpha_inv_per_unit_c_EST"]["BM-E"] - 0.527), 1.0e-3)
        self.assertLess(abs(planck["dlnLambda_dalphaU_inv_NUM"]["2L"] - 0.220), 1.0e-3)
        self.assertLess(abs(planck["dlnLambda_dalphaU_inv_NUM"]["3L_gauge_only"] - 0.227), 1.0e-3)
        shift = planck["fractional_scale_shift_per_unit_c_EST"]
        self.assertTrue(all(0.15 <= value <= 0.20 for value in shift.values()), shift)
        self.assertIn("2.07e16", planck["final_0.23c_is_for"])
        self.assertIn("not BM-DA1", planck["final_0.23c_is_for"])
        self.assertIs(self.fresh["flags"]["planck_kinetic_term_computed"], False)

    def test_research_record_is_labelled(self) -> None:
        research = self.fresh["research_record"]
        self.assertEqual(research["provenance_note"], g7.RESEARCH_PROVENANCE_NOTE)
        self.assertIn("not in the repository", research["provenance_note"])
        self.assertIn("hashed at generation time", research["provenance_note"])
        self.assertTrue(research["entries"])
        for name, entry in research["entries"].items():
            self.assertIn(entry["label"], ("RESEARCH_RECORD", "RESEARCH_RECORD_INPUT", "LIT"), name)
            self.assertRegex(entry["source_json_sha256"], r"^[0-9a-f]{64}$", name)
            self.assertIs(entry["reproducible_from_repository"], False, name)
            self.assertEqual(entry["source_json_sha256"], g7.RESEARCH_FILES[entry["source_json"]][1], name)
        self.assertEqual(research["entries"]["mss_eq5"]["label"], "LIT")
        self.assertEqual(research["entries"]["pgj_eqs_28_33"]["label"], "LIT")
        for phrase in ("B512 (2001) 230", "B535 (2002) 377", "4 linear combinations of the 8 scalar coefficients", "PyR@TE 3"):
            self.assertIn(phrase, research["entries"]["pgj_eqs_28_33"]["meaning"])
        self.assertEqual(research["entries"]["pyrate3_so10_b3.no_PQR"]["value"], "132706057/864")
        self.assertEqual(research["entries"]["pyrate3_so10_b3.with_PQR"]["value"], "109873879/864")
        self.assertEqual(research["entries"]["mss2012_pgj_agreement"]["label"], "LIT")
        self.assertEqual(research["entries"]["e5_u1_scheme_variants_rho1e3"]["label"], "RESEARCH_RECORD_INPUT")
        constraints = self.fresh["coefficients"]["mss_eq5"]["scalar_coefficient_constraints"]
        self.assertEqual((constraints["n_scalar_coefficients"], constraints["rank_fixed_by_MSS"]), (8, 4))
        self.assertEqual(research["entries"]["window_roots.roots_e2_G6_rho1e3"]["label"], "RESEARCH_RECORD_INPUT")
        self.assertEqual(research["files_digest"], g7.RESEARCH_FILES_DIGEST)
        self.assertEqual(g7.research_files_digest(g7.RESEARCH_FILES), g7.RESEARCH_FILES_DIGEST)
        self.assertEqual(g7.RESEARCH_FILES["wfRESCUE/C-other-extensions/c6_landau_cost.json"][1],
                         "78cc4eb01879dae36a6aeeee96339ec1772c7409621ba237479fa4464afbb1a4")
        self.assertEqual(g7.RESEARCH_FILES["wfGNG/U1/betas.json"][1],
                         "79328ca11341b5638178a84c09982ba0db3ea87f77feb7a51b5fc59a245274b6")
        two_code = research["two_code_root_agreement_BM_DA1"]
        self.assertLessEqual(two_code["v_R"], 0.034)
        self.assertLessEqual(two_code["M_X"], 0.073)
        self.assertIs(research["critic_engine_reproduces_U1_bit_for_bit"], True)
        for path in g7.RESEARCH_FILES:
            self.assertFalse(re.match(r"^[A-Za-z]:", path), path)

    def test_verdict_and_scope_texts(self) -> None:
        verdict = self.fresh["verdict"]
        self.assertEqual(verdict, self.committed["verdict"])
        for phrase in (
            "G7 is not closed on BM-DA1",
            "passes the reduced-Planck Landau criterion at two loops (alpha = 1 at 3.72e18 GeV on the U1 root, 3.88e18 GeV "
            "on the second-code U2 root)",
            "it fails on the U1 root (2.34e18 GeV < 2.435e18 GeV, -3.8%)",
            "passes marginally on the U2 root (2.438e18 GeV, +0.14%)",
            "lies within the two-code root uncertainty",
            "CONDITIONAL: anti-SOS region points, committed GUT scalar spectrum",
            "v_R = 8.56e9 GeV, <S> = 2.85e13 GeV at y_s = 0.30",
            "fails both axion-quality bounds",
            "doubling the GUT scalar masses removes that failure",
            "BM-E passes at two loops only",
            "a 120_H, a second 126bar and vectorlike pairs already at two loops",
            "gauge + matter only at every order",
            "the NDA window is convention-dependent",
            "G7 stays BLOCKED",
        ):
            self.assertIn(phrase, verdict)
        self.assertNotIn("G7 is CLOSED", verdict)
        self.assertNotIn("benchmark adopted", verdict)
        self.assertNotIn("G7 not closable on BM-DA1", verdict)
        scope = self.fresh["scope"]
        self.assertEqual(set(scope), {"claimed", "not_claimed"})
        not_claimed = " ".join(scope["not_claimed"])
        for phrase in ("research-recorded", "U(1)_X feedback", "single coupling", "not computed (EST only)",
                       "anti-SOS", "no gate status changes", "gauge + matter only at every order",
                       "two-loop root with one-loop thresholds", "1/sqrt50", "a0 ~ 21.6"):
            self.assertIn(phrase, not_claimed)
        self.assertIn("two-code root uncertainty", " ".join(scope["claimed"]))
        disclosures = self.fresh["disclosures"]
        self.assertIn("U(1)_X breaking at the cutoff", disclosures["pqr_placement"]["meaning"])
        self.assertTrue(0 < disclosures["pqr_placement"]["margin_vs_MPlred"] < 0.01)
        self.assertTrue(0.05 < disclosures["pqr_placement"]["BM_E_margin_vs_MPlred"] < 0.07)
        self.assertIn("BM-E passes at two loops only (P,Q,R at x0 p; on both roots)", verdict)
        self.assertIn("research-recorded only", disclosures["term_ratio_quote"]["meaning"])
        for key in ("two_code_root_uncertainty", "three_loop_on_two_loop_root", "so10_phase_yukawa_terms_omitted",
                    "nda_convention", "rg_improved_quality_scheme_dependence", "normalisation_nonperturbative"):
            self.assertIn(key, disclosures)
        self.assertTrue(-0.04 < disclosures["two_code_root_uncertainty"]["U1_margin_vs_MPlred"] < -0.035)
        self.assertTrue(0.001 < disclosures["two_code_root_uncertainty"]["U2_margin_vs_MPlred"] < 0.002)
        self.assertIn("y_s^-16", g7.QUALITY_CONVENTION)

    # ------------------------------------------------------------------
    # Fail-closed mutations (one changed input each).
    # ------------------------------------------------------------------

    def _assert_fail_closed(self, report: dict[str, Any], expected: tuple[str, ...]) -> None:
        self.assertEqual(report["status"], g7.STATUS_INCOMPLETE)
        self.assertEqual(report["overall_state"], g7.OVERALL_STATE_OPEN)
        self.assertEqual(report["G7_status"], "BLOCKED")
        for name in expected:
            self.assertIn(name, report["failures"])
            if name in report["checks"]:
                self.assertIs(report["checks"][name], False, name)
        for name in g7.NEVER_TRUE_FLAGS:
            self.assertIs(report["flags"][name], False, name)
        self.assertIs(report["flags"]["evidence_recorded"], False)
        self.assertFalse(g7.report_passes(report))
        self.assertTrue(report["verdict"].startswith("FAIL-CLOSED"))
        with tempfile.TemporaryDirectory() as tmp:
            out_json, out_md = Path(tmp) / "g7.json", Path(tmp) / "g7.md"
            with mock.patch.object(g7, "OUT_JSON", out_json), mock.patch.object(g7, "OUT_MD", out_md):
                with contextlib.redirect_stdout(io.StringIO()) as stdout:
                    code = g7.main(["--write"], report_builder=lambda: report)
            self.assertEqual(code, 1)
            self.assertIn("REFUSED", stdout.getvalue())
            self.assertFalse(out_json.exists())
            self.assertFalse(out_md.exists())

    def test_main_writes_only_a_passing_report(self) -> None:
        passing = g7.build_report()
        with tempfile.TemporaryDirectory() as tmp:
            out_json, out_md = Path(tmp) / "g7.json", Path(tmp) / "g7.md"
            with mock.patch.object(g7, "OUT_JSON", out_json), mock.patch.object(g7, "OUT_MD", out_md):
                with contextlib.redirect_stdout(io.StringIO()):
                    code = g7.main(["--write"], report_builder=lambda: passing)
            self.assertEqual(code, 0)
            self.assertTrue(out_json.exists() and out_md.exists())
            written = json.loads(out_json.read_text(encoding="utf-8"))
            self.assertEqual(_mismatches(_strip_timing(written), _strip_timing(self.committed)), [])

    def test_mutation_pgj_coefficient(self) -> None:
        table = dict(g7.PGJ_COEFFICIENTS)
        self.assertEqual(table["c1.CG^3"], Fraction(2857, 162))
        table["c1.CG^3"] = Fraction(2858, 162)
        report = g7.build_report(pgj_table=table)
        self._assert_fail_closed(
            report,
            ("coefficients.pgj_reproduces_qcd_general_casimirs", "coefficients.pgj_matches_mss_as_nG_polynomials",
             "coefficients.so10_phase_coefficients_pinned"),
        )

    def test_mutation_t120(self) -> None:
        report = g7.build_report(rep_overrides={"120": {"T": 27}})
        self._assert_fail_closed(
            report,
            ("coefficients.so10_rep_data_from_weyl_formula", "coefficients.so10_index_casimir_relation",
             "coefficients.landau_option_coefficients_exact", "landau_cost.scales_match_research_records"),
        )

    def test_mutation_research_alpha_u(self) -> None:
        roots = copy.deepcopy(g7.default_window_roots())
        shifted = [row for row in roots if row["variant"] == "G6" and row["log10_rho"] == "3.00"]
        self.assertEqual(len(shifted), 1)
        shifted[0]["alpha_U_inv"] += 0.5
        report = g7.build_report(roots=roots)
        self._assert_fail_closed(report, ("running.bm_da1_matches_research_records", "running.bm_da1_scales_pinned"))

    def test_mutation_three_loop_factor_zero(self) -> None:
        report = g7.build_report(three_loop_factor=0.0)
        self._assert_fail_closed(
            report, ("running.bm_da1_two_loop_pass_three_loop_fail_on_U1_root",
                     "running.u2_roots_pinned_bm_da1_two_loop_pass_three_loop_marginal_pass",
                     "verdict.physics_flags_from_numbers")
        )
        self.assertIs(report["flags"]["bm_da1_three_loop_fail_on_U1_root"], False)
        self.assertIs(report["flags"]["bm_da1_three_loop_marginal_pass_on_U2_root"], False)
        self.assertIs(report["flags"]["bm_da1_two_loop_pass_both_roots"], True)

    def test_mutation_rk4_step(self) -> None:
        report = g7.build_report(rk4_step=0.2)
        self._assert_fail_closed(report, ("running.integrators_agree", "verdict.physics_flags_from_numbers"))
        self.assertIs(report["flags"]["integrators_agree"], False)
        self.assertGreater(report["running"]["integrator_agreement"]["max_rel_I1_I2"], 1.0e-6)

    def test_mutation_quality_exponent(self) -> None:
        report = g7.build_report(z17_exponent=16)
        self._assert_fail_closed(report, ("quality.matches_e6_record",))

    def test_mutation_research_sha256(self) -> None:
        files = dict(g7.RESEARCH_FILES)
        name = "wfRESCUE/E-G7-completion/verify-physics/v1_threeloop.json"
        script, sha = files[name]
        files[name] = (script, sha[:-1] + ("0" if sha[-1] != "0" else "1"))
        report = g7.build_report(research_files=files)
        self._assert_fail_closed(
            report, ("research_record.files_digest_pinned", "research_record.entries_labelled_with_provenance")
        )

    def test_mutation_research_label(self) -> None:
        record = copy.deepcopy(g7.RESEARCH_RECORD)
        record["c6_landau_cost"]["label"] = "EXACT"
        report = g7.build_report(research_record=record)
        self._assert_fail_closed(report, ("research_record.entries_labelled_with_provenance",))

    def test_mutation_check_count(self) -> None:
        with mock.patch.object(g7, "EXPECTED_N_CHECKS", g7.EXPECTED_N_CHECKS + 1):
            report = g7.build_report()
            self.assertEqual(report["n_checks"], 46)
            self.assertTrue(all(report["checks"].values()))
            self._assert_fail_closed(report, (g7.CHECK_COUNT_FAILURE,))


if __name__ == "__main__":
    unittest.main()
