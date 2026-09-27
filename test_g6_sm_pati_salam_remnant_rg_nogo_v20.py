#!/usr/bin/env python3
"""Tests for the G6 remnant RG no-go on the SOS-certified witness family (v20; evidence only, G6 stays OPEN).

setUpClass builds one fresh report (exact integer model of Delta_R = (10bar,1,3), exact c_qk in the repository 126bar
chart, sympy matching, float running, LP margins and the joint-RK4 accuracy estimate, FJ R_xi pole masses and CW
curvature masses; about one minute) and compares it with the committed artifact: the EXACT sections must match
exactly, the FLOAT sections (running, one_loop_masses, disclosures and the research-record consistency deviations)
only within declared tolerances.  The exact pins (tree mass matrix, c_qk, Fierz vectors, beta tensors, witness betas,
levels, gap identity) are re-derived independently here from the pinned tables, the G6 cross-check is re-done from the
committed G6 JSON, and the mutation tests change one input each (historical weights, swapped c_qk rows, a Fierz sign, a
beta-tensor entry, a gauge boundary value, the SOS cone without its 4125 row, a region point, the G6 tree report, the
research record, the research pole reference) and require the named checks to fail closed with G6 still OPEN.  The
ledger test checks that G1_G8_GATE_LEDGER_V20.json cites the report as evidence only and that the ledger's fail-closed
predicate uses exactly this module's never-true flags.
"""
from __future__ import annotations

import copy
import json
import math
import unittest
from collections import Counter
from fractions import Fraction
from typing import Any

import sympy

import g3_candidate_physical_target_audit_v20 as target
import g3_sm_pati_salam_candidate_v20 as candidate
import g6_sm_pati_salam_remnant_rg_nogo_v20 as nogo

TIMING_KEYS = {"runtime_seconds"}
FLOAT_SECTIONS = ("running", "one_loop_masses", "disclosures")


def _strip_timing(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _strip_timing(item) for key, item in value.items() if key not in TIMING_KEYS}
    if isinstance(value, list):
        return [_strip_timing(item) for item in value]
    return value


def _split(report: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """(exact part, float part): the float sections and the float consistency deviations of the research record."""
    report = copy.deepcopy(_strip_timing(report))
    floats = {name: report.pop(name) for name in FLOAT_SECTIONS}
    floats["research_record_consistency"] = report["research_record"].pop("consistency")
    return report, floats


def _fractions(values: Any) -> list[Fraction]:
    return [Fraction(value) for value in values]


class G6RemnantRgNogoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.committed = json.loads(nogo.OUT_JSON.read_text(encoding="utf-8"))
        cls.fresh = nogo.json_roundtrip(nogo.build_report())

    # ------------------------------------------------------------------
    # Status, checks and flags.
    # ------------------------------------------------------------------

    def test_all_checks_pass_and_status_recorded(self) -> None:
        for report in (self.committed, self.fresh):
            self.assertEqual(report["n_failed"], 0, report["failures"])
            self.assertEqual(report["failures"], [])
            self.assertEqual(report["n_checks"], nogo.EXPECTED_N_CHECKS)
            self.assertEqual(report["n_checks"], len(report["checks"]))
            self.assertEqual(nogo.EXPECTED_N_CHECKS, 58)
            self.assertTrue(all(report["checks"].values()))
            self.assertEqual(report["status"], nogo.STATUS_RECORDED)
            self.assertEqual(report["overall_state"], nogo.OVERALL_STATE_RECORDED)
            self.assertEqual(report["G6_status"], "OPEN")
            self.assertEqual(report["gate"], "G6")
            self.assertEqual(report["model_contract_id"], "gauged_u1x_phi17_v20")
            for name in nogo.DERIVED_FLAGS:
                self.assertIs(report["flags"][name], True, name)
            for name in nogo.NEVER_TRUE_FLAGS:
                self.assertIs(report["flags"][name], False, name)
            self.assertEqual(set(report["flags"]), set(nogo.DERIVED_FLAGS) | set(nogo.NEVER_TRUE_FLAGS))
            self.assertEqual(report["tree_certificate_scope"], "tree level at mu = M_GUT")
            self.assertEqual(dict(Counter(key.split(".")[0] for key in report["checks"])), nogo.EXPECTED_SECTION_COUNTS)
            self.assertEqual(
                nogo.EXPECTED_SECTION_COUNTS,
                {"group_theory": 17, "chart": 9, "matching": 9, "running": 13, "one_loop": 6, "research_record": 3, "scope": 1},
            )
            self.assertTrue(nogo.report_passes(report))
            for section, kind in (
                ("group_theory", "EXACT"),
                ("chart_binding", "EXACT"),
                ("matching", "EXACT"),
                ("running", "FLOAT"),
                ("one_loop_masses", "FLOAT"),
                ("research_record", "RESEARCH_RECORD"),
            ):
                self.assertEqual(report[section]["kind"], kind, section)
            self.assertIn("tolerances", report["running"])
            self.assertIn("tolerances", report["one_loop_masses"])

    def test_status_strings(self) -> None:
        for status in (nogo.STATUS_RECORDED, nogo.STATUS_INCOMPLETE):
            self.assertTrue(status.endswith("__G6_OPEN"), status)
        self.assertNotEqual(nogo.STATUS_RECORDED, nogo.STATUS_INCOMPLETE)
        self.assertIn("NOT_CLOSABLE_ON_SOS_WITNESS_FAMILY", nogo.STATUS_RECORDED)
        self.assertEqual(nogo.STATUS_RECORDED, "G6_SM_PATI_SALAM_REMNANT_RG__NOT_CLOSABLE_ON_SOS_WITNESS_FAMILY__G6_OPEN")

    def test_committed_artifact_matches_fresh_report(self) -> None:
        committed_exact, committed_float = _split(self.committed)
        fresh_exact, fresh_float = _split(self.fresh)
        self.assertEqual(target.report_mismatches(committed_exact, fresh_exact), [])
        self.assertEqual(target.report_mismatches(committed_float, fresh_float, "float", rel_tol=1.0e-6, abs_tol=1.0e-9), [])

    def test_committed_markdown_regenerates(self) -> None:
        expected = nogo._markdown(self.committed).replace("\r\n", "\n")
        self.assertEqual(nogo.OUT_MD.read_text(encoding="utf-8").replace("\r\n", "\n"), expected)

    def test_tampered_artifact_is_detected(self) -> None:
        tampered = copy.deepcopy(self.committed)
        tampered["checks"]["matching.gap_identity_exact"] = False
        committed_exact, _ = _split(self.committed)
        tampered_exact, _ = _split(tampered)
        self.assertNotEqual(target.report_mismatches(committed_exact, tampered_exact), [])
        tampered = copy.deepcopy(self.committed)
        tampered["chart_binding"]["c_qk"]["4125"][3] = "0"
        self.assertNotEqual(target.report_mismatches(_split(self.committed)[0], _split(tampered)[0]), [])

    # ------------------------------------------------------------------
    # Exact content, re-derived independently from the pinned tables.
    # ------------------------------------------------------------------

    def test_exact_pins(self) -> None:
        group = self.fresh["group_theory"]
        chart = self.fresh["chart_binding"]
        matching = self.fresh["matching"]
        self.assertEqual(group["tree_mass_matrix"]["A"], [list(row) for row in nogo.EXPECTED_TREE_MATRIX])
        self.assertEqual(group["sym2"]["dimensions"], ["20", "35", "135", "100", "175"])
        self.assertEqual(chart["c_qk"], {channel: list(values) for channel, values in nogo.EXPECTED_CQK.items()})
        self.assertEqual(group["fierz_vectors"]["f"], {channel: list(values) for channel, values in nogo.EXPECTED_FIERZ.items()})
        self.assertEqual(group["beta_scalar_tensor"]["Q"], {f"{i},{j}": list(values) for (i, j), values in nogo.EXPECTED_Q.items()})
        self.assertEqual(group["beta_gauge_tensor"]["G"], {name: list(values) for name, values in nogo.EXPECTED_G.items()})
        self.assertEqual(group["witness_betas"]["beta_16pi2"], list(nogo.EXPECTED_WITNESS_BETA16))
        self.assertEqual(matching["witness"]["lambda"], list(nogo.WITNESS_LAMBDA))
        self.assertEqual([matching["witness"]["tree_levels"][name] for name in nogo.STATE_ORDER], list(nogo.WITNESS_LEVELS))
        self.assertEqual(matching["witness"]["lam4_minus_lam5"], "1/128")
        self.assertEqual(matching["historical_weights"]["lam4_minus_lam5"], "-1/128")
        # Independent re-derivations from the pinned tables.
        cqk = {channel: _fractions(values) for channel, values in nogo.EXPECTED_CQK.items()}
        fierz = {channel: _fractions(values) for channel, values in nogo.EXPECTED_FIERZ.items()}
        self.assertEqual([sum(cqk[channel][k] for channel in cqk) for k in range(5)], [1] * 5)
        w = dict(zip(("54", "1050bar", "2772bar", "4125"), sympy.symbols("w54 w1050 w2772 w4125")))
        b = dict(zip(("(1,1,1)", "(15,1,1)", "(15,1,3)"), sympy.symbols("b111 b1511 b1513")))

        def rational(value: Fraction) -> sympy.Rational:
            return sympy.Rational(value.numerator, value.denominator)

        lam = [
            sum(w[q] * rational(cqk[q][k]) for q in w) / 8 - sum(b[c] * rational(fierz[c][k]) for c in b)
            for k in range(5)
        ]
        gap = sympy.expand(lam[3] - lam[4])
        self.assertEqual(sympy.expand(gap - ((w["4125"] - w["2772bar"]) / 8 + 3 * b["(15,1,1)"] + 3 * b["(15,1,3)"])), 0)
        self.assertEqual(sympy.expand(lam[1].subs({symbol: 0 for symbol in b.values()}) - w["4125"] / 8), 0)
        weights = {channel: Fraction(value) for channel, value in candidate.SWAPPED_SELF_WEIGHTS.items()}
        witness = [sum(weights[q] * cqk[q][k] for q in cqk) / 8 for k in range(5)]
        self.assertEqual(witness, _fractions(nogo.WITNESS_LAMBDA))
        tree = [_fractions(row) for row in nogo.EXPECTED_TREE_MATRIX]
        levels = [sum(tree[s][k] * witness[k] for k in range(5)) for s in range(7)]
        self.assertEqual(levels, _fractions(nogo.WITNESS_LEVELS))
        self.assertTrue(all(sum(row) == 0 for row in tree[:6]))
        q_tensor = {key: _fractions(values) for key, values in nogo.EXPECTED_Q.items()}
        self.assertEqual([sum(q_tensor[key][k] for key in q_tensor) for k in range(5)], [136] * 5)
        g_tensor = {key: _fractions(values) for key, values in nogo.EXPECTED_G.items()}
        g4s, grs = Fraction(9, 25), Fraction(1, 4)
        c2 = Fraction(9, 2) * g4s + 2 * grs
        monomials = {"g4^4": g4s * g4s, "gR^4": grs * grs, "g4^2gR^2": g4s * grs}
        beta = [
            sum(q_tensor[(i, j)][k] * witness[i] * witness[j] for (i, j) in q_tensor)
            + sum(g_tensor[name][k] * monomials[name] for name in monomials)
            - 12 * c2 * witness[k]
            for k in range(5)
        ]
        self.assertEqual(beta, _fractions(nogo.EXPECTED_WITNESS_BETA16))
        for value, recorded in zip(beta, group["witness_betas"]["beta_float"]):
            self.assertTrue(math.isclose(float(value) / (16 * math.pi**2), recorded, rel_tol=1.0e-11))
        # Farkas certificate of the SOS gap and the 210 channels.
        certificate = matching["sos_cone"]["farkas_certificate"]
        self.assertEqual(certificate["binding_row"], ["4125"])
        self.assertEqual(certificate["cone_row_multipliers_w_q_minus_w_2772"], {"54": "0", "1050bar": "0", "4125": "1/8"})
        self.assertEqual(certificate["beta_multipliers"], {"(1,1,1)": "0", "(15,1,1)": "3", "(15,1,3)": "3"})
        self.assertEqual(group["exchange_channels_210"]["channels_coupling_to_delta_dagger_delta"], ["(1,1,1)", "(15,1,1)", "(15,1,3)"])
        self.assertEqual(group["exchange_channels_210"]["dimension_210"], 210)
        self.assertTrue(group["sm_higgs_beta_identity"]["identity_exact"])
        self.assertEqual(group["sm_higgs_beta_identity"]["scalar_coefficient"], "24")
        self.assertEqual(group["vacuum"]["broken_generator_rank"], 9)
        self.assertEqual(chart["krylov_basis"]["rank_mod_p"], 60)
        self.assertEqual(chart["witness_portal"]["max_abs_residual_on_krylov_basis"], 0)

    def test_g6_cross_check_reads_committed_certificate(self) -> None:
        g6 = json.loads(nogo.G6_TREE_JSON.read_text(encoding="utf-8"))
        self.assertEqual(g6["status"], nogo.G6_TREE_STATUS)
        self.assertEqual(g6["n_failed"], 0)
        pairs = set()
        for factor in g6["parametric_spectrum"]["factors"]:
            limits = factor.get("r0_to_0")
            if not isinstance(limits, dict):
                continue
            mus = limits.get("light_branches", {}).get("mu_limits_rational")
            if isinstance(mus, list) and len(mus) == 1 and mus[0] != "0":
                for label, dim in factor["sm_content_per_root_real"].items():
                    pairs.add((label, str(Fraction(mus[0])), int(dim)))
        expected = {
            (label, level, dim)
            for label, level, dim in zip(nogo.G6_LABELS, nogo.WITNESS_LEVELS, nogo.EXPECTED_STATE_REAL_DIMS)
        } | {("(1,1)_|Y|=0", "4", 1)}
        self.assertEqual(pairs, expected)
        self.assertEqual(
            sorted(tuple(item) for item in self.fresh["matching"]["g6_cross_check"]["pairs_from_certificate"]), sorted(expected)
        )

    # ------------------------------------------------------------------
    # Float values and margins.
    # ------------------------------------------------------------------

    def test_float_values_and_margins(self) -> None:
        running = self.fresh["running"]
        for tag in nogo.PROFILE_TAGS:
            profile = running["profiles"][tag]
            crossing = profile["witness_lambda5_zero_crossing_GeV"]
            self.assertLess(abs(crossing / nogo.EXPECTED_CROSSING_GEV[tag] - 1), 1.0e-5, tag)
            self.assertLess(profile["v_R_GeV"], crossing)
            self.assertLess(crossing, profile["M_GUT_GeV"])
            self.assertGreater(profile["witness_events_GeV"]["1e3"], profile["v_R_GeV"])
            gap = running["gap_lam4_minus_lam5_GUT"][tag]
            self.assertLess(gap, -0.2, tag)
            self.assertLess(abs(running["tree_matching_min_slack"][tag] + gap / 2), 1.0e-7, tag)
            # D08 is record-only: the threshold margins are pinned for both pairings, with no pass criterion.
            for pairing in nogo.THRESHOLD_PAIRINGS:
                for gx in nogo.GX_VALUES:
                    value = running["threshold_matching_min_slack_all_pairings"][tag][pairing][gx]
                    self.assertLess(abs(value - nogo.EXPECTED_THRESHOLD_SLACK[tag][pairing][gx]), 1.0e-5, (tag, pairing, gx))
            self.assertEqual(
                running["threshold_matching_min_slack"][tag],
                running["threshold_matching_min_slack_all_pairings"][tag][nogo.THRESHOLD_PAIRING[tag]],
            )
            self.assertLessEqual(running["bfb_only_min_slack"][tag], 1.0e-9)
            grid = running["sos_safe_grid"]["per_profile"][tag]
            self.assertEqual(grid["tree_vacuum_at_v_R"], 0)
            self.assertEqual(grid["not_blown_up"], nogo.EXPECTED_D11_NOT_BLOWN_UP[tag])
            self.assertTrue(all(value > 0 for value in running["tree_levels_at_v_R"][tag]))
            # Accuracy against the joint (non-interpolated) reference.
            accuracy = running["accuracy_estimate"]["per_profile"][tag]
            self.assertLess(accuracy["primary_minus_reference_lambda_GUT_max_abs"], 1.0e-5, tag)
            self.assertLess(abs(accuracy["primary_over_reference_crossing_minus_1"]), 5.0e-5, tag)
            self.assertLess(accuracy["reference_gap_lam4_minus_lam5_GUT"], -0.2, tag)
            self.assertLess(accuracy["reference_self_convergence_lambda_abs"], 1.0e-9, tag)
        self.assertIs(running["accuracy_estimate"]["within_budget"], True)
        self.assertIn("regression tolerances", running["tolerance_semantics"])
        # The witness threshold removes the lambda4 >= lambda5 obstruction at rho = 1e3 (disclosed, not robust).
        shift = running["threshold_gap_shift"]["alphainv23.78_gX1.0"]["dlam4_minus_dlam5"]
        self.assertLess(shift, running["gap_lam4_minus_lam5_GUT"]["rho1e3"])
        self.assertGreater(running["target_gap_after_threshold"]["rho1e3"]["alphainv23.78"]["gX1.0"], 0)
        self.assertLess(running["threshold_matching_min_slack_all_pairings"]["no_spec"]["alphainv23.78"]["gX1.0"], 0.03)
        scale = running["threshold_scale"]
        self.assertTrue(1.18 <= scale["scale_for_slack_le_research_0.03"] <= 1.23)
        self.assertTrue(1.70 <= scale["scale_for_exact_reach"] <= 1.76)
        self.assertLess(abs(scale["gX0_min_slack_over_scale_0_to_8"] - nogo.EXPECTED_THRESHOLD_SCALE["gX0_min_slack"]), 1.0e-5)
        one_loop = self.fresh["one_loop_masses"]
        masses = one_loop["masses_over_v_R_squared"]
        self.assertTrue(all(value > 0 for tag in nogo.PROFILE_TAGS for value in masses[tag]["cw"]))
        self.assertLess(one_loop["max_abs_deviation_from_independent_record"], 1.0e-6)
        # FJ R_xi pole masses: positive for every xi, xi independent, equal to the research record.
        poles = one_loop["fj_pole_masses_over_v_R_squared"]
        for tag in nogo.PROFILE_TAGS:
            self.assertEqual(set(poles[tag]["pole_by_xi"]), {str(xi) for xi in nogo.POLE_XIS})
            for xi, values in poles[tag]["pole_by_xi"].items():
                self.assertEqual(len(values), 7)
                self.assertTrue(all(value > 0 for value in values), (tag, xi))
                reference = nogo.BEST_CONTROLLED_POLE_REFERENCE[tag]["pole_by_xi"][xi]
                self.assertTrue(all(abs(a - b) <= 1.0e-9 for a, b in zip(values, reference)), (tag, xi))
            self.assertLessEqual(poles[tag]["xi_spread"], 1.0e-12, tag)
            self.assertTrue(all(value > 0 for value in poles[tag]["VF_L"]), tag)
            self.assertLessEqual(abs(poles[tag]["dv_feyn"]), 0.2)
            self.assertLessEqual(abs(poles[tag]["dv_landau"]), 0.2)
        self.assertLess(one_loop["fj_pole_max_abs_deviation_from_research_record"], 1.0e-9)

    def test_research_record_is_labelled_and_not_rederived(self) -> None:
        entries = self.fresh["research_record"]["entries"]
        self.assertTrue(entries)
        for name, entry in entries.items():
            self.assertIn(entry["label"], ("RESEARCH_RECORD", "RESEARCH_RECORD_INPUT"), name)
            self.assertRegex(entry["source_json_sha256"], r"^[0-9a-f]{64}$", name)
            self.assertIs(entry["reproducible_from_repository"], False, name)
        for name in nogo.UNVERIFIED_RECORD_KEYS:
            self.assertIs(entries[name]["value"], False, name)
        for name in (
            "region_counts",
            "BG_max_quantiles",
            "matching_tree_LP",
            "pole_mass_xi_spread",
            "scale_variation",
            "region_scan_box_rho1e3",
            "box_extension_rho1e3",
            "box_extension_no_spec",
            "best_controlled_pole_reference",
        ):
            self.assertEqual(entries[name]["label"], "RESEARCH_RECORD", name)
        for tag in nogo.PROFILE_TAGS:
            box = entries[f"region_scan_box_{tag}"]["value"]
            self.assertEqual((box["box_lo"], box["box_hi"], box["N_box"]), ([-0.8, -0.1, -0.1, -0.1, 0.0], [0.8, 0.8, 0.35, 0.45, 0.08], 1500000))
            self.assertEqual(entries[f"region_scan_box_{tag}"]["source_json"], f"d13_region_{tag}.json")
        self.assertLess(entries["box_extension_rho1e3"]["value"]["share_inside_prod_box"], 1.0)
        self.assertIn("not recorded", entries["box_extension_rho1e3"]["meaning"])
        self.assertEqual(entries["profile_M_X"]["label"], "RESEARCH_RECORD_INPUT")
        # Pole masses at Q = v_R are recomputed now; their scale variation, the region volume and tuning are not.
        self.assertIs(self.fresh["flags"]["pole_masses_recomputed_in_module"], True)
        self.assertIs(self.fresh["flags"]["best_region_points_one_loop_pole_positive_recomputed"], True)
        self.assertIs(self.fresh["flags"]["pole_mass_scale_variation_recomputed_in_module"], False)
        self.assertIs(self.fresh["flags"]["region_volume_and_tuning_recomputed_in_module"], False)
        self.assertIs(self.fresh["flags"]["region_scan_exhaustive_beyond_sampled_box"], False)
        self.assertIs(self.fresh["flags"]["disjointness_robust_to_one_loop_threshold"], False)
        self.assertNotIn("pole_masses_recomputed_in_module", nogo.NEVER_TRUE_FLAGS)
        self.assertIn("not verifiable from the repository", self.fresh["research_record"]["provenance_note"])

    def test_scope_texts_pinned(self) -> None:
        verdict = self.fresh["verdict"]
        for phrase in (
            "not closable on the SOS-certified witness family",
            "tree level at mu = M_GUT",
            "not shown impossible in the contract",
            "G3 and G4 are unchanged",
            "assumed weight independent, not verified",
            "G6 stays OPEN",
            "Only the tree-matching statement is robust",
            "removes the lambda4 >= lambda5 obstruction",
            "the remaining separation is 0.042 at rho = 1e3 and closes at 1.20 to 1.73 times that threshold",
            "sampling statement, not a proof over all couplings",
            "closing G6 would need",
        ):
            self.assertIn(phrase, verdict)
        self.assertNotIn("G6 is CLOSED", verdict)
        self.assertNotIn("gauge independent to 1e-13", verdict)
        self.assertNotIn("closing G6 needs", verdict)
        self.assertEqual(verdict.count("impossible"), verdict.count("not shown impossible"))
        self.assertEqual(self.fresh["verdict"], self.committed["verdict"])
        scope = self.fresh["scope"]
        self.assertEqual(set(scope), {"proved_exactly", "float_recomputed", "research_recorded", "not_proved_or_out_of_scope", "status_statement"})
        self.assertTrue(any("anti-SOS" in item for item in scope["not_proved_or_out_of_scope"]))
        self.assertTrue(any("assumed weight independent, not verified" in item for item in scope["not_proved_or_out_of_scope"]))
        self.assertTrue(any("sampling statement, not a proof over all couplings" in item for item in scope["not_proved_or_out_of_scope"]))
        self.assertTrue(any("only the tree-matching statement is robust" in item for item in scope["not_proved_or_out_of_scope"]))
        self.assertFalse(any("pole masses and their xi independence (research-recorded" in item for item in scope["not_proved_or_out_of_scope"]))
        self.assertEqual(
            set(self.fresh["disclosures"]),
            {
                "threshold_fragility",
                "region_sampling",
                "pole_scheme_dependence",
                "xi_spread_actual",
                "scale_statement_rho_specific",
                "sigma_not_global_min_in_region",
            },
        )
        fragility = self.fresh["disclosures"]["threshold_fragility"]["meaning"]
        for phrase in ("removes the lambda4 >= lambda5 obstruction", "4 pi/g^2 at the matching scale M_GUT", "only the tree-level version of the disjointness is robust"):
            self.assertIn(phrase, fragility)
        self.assertIn("not a vacuum analysis", self.fresh["running"]["sos_safe_grid"]["meaning"])

    # ------------------------------------------------------------------
    # Fail-closed mutations (one changed input each).
    # ------------------------------------------------------------------

    def _assert_fail_closed(self, report: dict[str, Any], expected: tuple[str, ...]) -> None:
        self.assertEqual(report["status"], nogo.STATUS_INCOMPLETE)
        self.assertEqual(report["overall_state"], nogo.OVERALL_STATE_OPEN)
        self.assertEqual(report["G6_status"], "OPEN")
        for name in expected:
            self.assertIn(name, report["failures"])
        for name in nogo.NEVER_TRUE_FLAGS:
            self.assertIs(report["flags"][name], False, name)
        self.assertIs(report["flags"]["not_closable_on_sos_witness_family"], False)
        self.assertFalse(nogo.report_passes(report))
        self.assertTrue(report["verdict"].startswith("FAIL-CLOSED"))

    def test_mutation_historical_weights(self) -> None:
        report = nogo.build_report(witness_weights=candidate.HISTORICAL_SELF_WEIGHTS)
        self._assert_fail_closed(
            report,
            (
                "matching.witness_couplings_exact",
                "matching.witness_tree_levels_exact",
                "matching.witness_tree_levels_match_committed_g6_certificate",
            ),
        )

    def test_mutation_cqk_swapped_columns(self) -> None:
        swapped = {channel: list(values) for channel, values in nogo.EXPECTED_CQK.items()}
        swapped["4125"], swapped["2772bar"] = swapped["2772bar"], swapped["4125"]
        report = nogo.build_report(cqk_override=swapped)
        self._assert_fail_closed(report, ("chart.c_qk_exact", "matching.witness_couplings_exact", "matching.witness_tree_levels_exact"))

    def test_mutation_fierz_sign(self) -> None:
        negated = {"(15,1,3)": [str(-Fraction(value)) for value in nogo.EXPECTED_FIERZ["(15,1,3)"]]}
        report = nogo.build_report(fierz_override=negated)
        self._assert_fail_closed(report, ("group_theory.fierz_vectors_exact", "group_theory.exchange_channels_of_210_never_lower_gap"))

    def test_mutation_beta_tensor(self) -> None:
        mutated = {(0, 0): [str(Fraction(nogo.EXPECTED_Q[(0, 0)][0]) + Fraction(1, 27)), *nogo.EXPECTED_Q[(0, 0)][1:]]}
        report = nogo.build_report(beta_override=mutated)
        self._assert_fail_closed(
            report,
            ("group_theory.beta_scalar_tensor_exact", "group_theory.beta_scalar_tensor_o60_point_136", "group_theory.witness_betas_exact"),
        )

    def test_mutation_gauge_input(self) -> None:
        inputs = copy.deepcopy(nogo.PROFILE_INPUTS)
        y = list(inputs["rho1e3"]["y_MI"])
        y[2] += 1.0
        inputs["rho1e3"]["y_MI"] = tuple(y)
        report = nogo.build_report(profile_inputs=inputs)
        self._assert_fail_closed(report, ("running.gauge_profiles_reproduce_recorded_inputs", "running.witness_lambda5_zero_crossing"))

    def test_mutation_sos_cone_without_4125_row(self) -> None:
        report = nogo.build_report(sos_cone_rows=("54", "1050bar"))
        self._assert_fail_closed(report, ("running.tree_matching_min_slack_is_half_gap",))

    def test_mutation_region_point(self) -> None:
        points = dict(nogo.REGION_POINTS)
        points["rho1e3"] = tuple(1.01 * value for value in points["rho1e3"])
        report = nogo.build_report(region_points=points)
        self._assert_fail_closed(report, ("running.region_points_run_up", "research_record.consistent_with_recomputation"))
        lam = list(nogo.EXPECTED_LAMBDA_GUT["rho1e3"])
        lam[3] = lam[4] + 0.01
        self.assertIs(nogo.gap_excludes_sos_tree_image(lam), False)
        self.assertIs(nogo.gap_excludes_sos_tree_image(nogo.EXPECTED_LAMBDA_GUT["rho1e3"]), True)

    def test_mutation_g6_tree_report(self) -> None:
        committed = nogo.load_g6_tree_report()
        self.assertIsNotNone(committed)
        changed_status = copy.deepcopy(committed)
        changed_status["status"] = "G6_CLOSED"
        changed_mu = copy.deepcopy(committed)
        for factor in changed_mu["parametric_spectrum"]["factors"]:
            limits = factor.get("r0_to_0")
            if isinstance(limits, dict) and limits.get("light_branches", {}).get("mu_limits_rational") == ["17/288"]:
                limits["light_branches"]["mu_limits_rational"] = ["17/289"]
        for case in (None, {}, changed_status, changed_mu):
            report = nogo.build_report(g6_tree_report=case)
            self._assert_fail_closed(report, ("matching.witness_tree_levels_match_committed_g6_certificate",))

    def test_mutation_research_record(self) -> None:
        cases = []
        shortened = copy.deepcopy(nogo.RESEARCH_RECORD)
        shortened["region_counts"]["source_json_sha256"] = shortened["region_counts"]["source_json_sha256"][:40]
        cases.append((shortened, "research_record.entries_labelled_with_provenance"))
        relabelled = copy.deepcopy(nogo.RESEARCH_RECORD)
        relabelled["BG_max_quantiles"]["label"] = "EXACT"
        cases.append((relabelled, "research_record.entries_labelled_with_provenance"))
        claimed = copy.deepcopy(nogo.RESEARCH_RECORD)
        claimed["threshold_w_independence_verified"]["value"] = True
        cases.append((claimed, "research_record.unverified_items_not_claimed"))
        positive_gap = copy.deepcopy(nogo.RESEARCH_RECORD)
        positive_gap["region_gap_quantiles_rho1e3"]["value"][-1] = 0.01
        cases.append((positive_gap, "research_record.consistent_with_recomputation"))
        for record, failure in cases:
            report = nogo.build_report(research_record=record)
            self._assert_fail_closed(report, (failure,))

    def test_mutation_pole_reference(self) -> None:
        shifted = copy.deepcopy(nogo.RESEARCH_RECORD)
        shifted["best_controlled_pole_reference"]["value"]["rho1e3"]["pole_by_xi"]["1.0"][0] += 1.0e-6
        report = nogo.build_report(research_record=shifted)
        self._assert_fail_closed(report, ("one_loop.fj_pole_masses_match_research_record",))
        self.assertIs(report["flags"]["pole_masses_recomputed_in_module"], False)
        vev = copy.deepcopy(nogo.RESEARCH_RECORD)
        vev["fj_vs_vf_vev_shift"]["value"]["no_spec"]["dv_landau"] += 1.0e-6
        report = nogo.build_report(research_record=vev)
        self._assert_fail_closed(report, ("one_loop.vev_fixed_landau_masses_positive_and_dv_controlled",))

    # ------------------------------------------------------------------
    # Ledger: evidence only.
    # ------------------------------------------------------------------

    def test_ledger_cites_report_as_evidence_only(self) -> None:
        import g1_g8_gate_ledger_v20 as ledger

        committed = json.loads(ledger.OUT_JSON.read_text(encoding="utf-8"))
        g6 = committed["gates"]["G6"]
        self.assertEqual(g6["status"], "OPEN")
        evidence = g6["remnant_rg_evidence"]
        self.assertIs(evidence["recorded"], True)
        self.assertIs(evidence["closes_gate"], False)
        self.assertEqual(evidence["required_status"], nogo.STATUS_RECORDED)
        self.assertEqual(evidence["required_status"], ledger.G6_REMNANT_RG_NOGO_STATUS)
        self.assertEqual(ledger.G6_REMNANT_RG_NOGO_N_CHECKS, nogo.EXPECTED_N_CHECKS)
        self.assertEqual(ledger.G6_REMNANT_RG_NEVER_TRUE_FLAGS, nogo.NEVER_TRUE_FLAGS)
        self.assertEqual(ledger.G6_REMNANT_RG_TREE_SCOPE, nogo.TREE_CERTIFICATE_SCOPE)
        self.assertEqual(evidence["scope"], list(ledger.G6_REMNANT_RG_SCOPE))
        self.assertTrue(any("tree matching only" in item for item in evidence["scope"]))
        self.assertIn("only the tree-matching statement is robust", ledger.G6_REMNANT_RG_RECORDED_ITEM)
        self.assertEqual(g6["open_scope"][-1], ledger.G6_REMNANT_RG_RECORDED_ITEM)
        self.assertEqual(g6["open_scope"][-2], ledger.G6_EVIDENCE_RECORDED_ITEM)
        self.assertIn("at mu = M_GUT", ledger.G6_EVIDENCE_RECORDED_ITEM)
        self.assertIs(g6["tree_level_evidence"]["closes_gate"], False)
        self.assertEqual({name: row["status"] for name, row in committed["gates"].items()}, {
            "G1": "CLOSED", "G2": "CLOSED", "G3": "CLOSED", "G4": "CLOSED", "G5": "CLOSED",
            "G6": "OPEN", "G7": "BLOCKED", "G8": "BLOCKED",
        })


if __name__ == "__main__":
    unittest.main()
