#!/usr/bin/env python3
"""Tests for the pure G4 closure predicate g4_sm_closure_binding_v20 (v20).

The predicate decides, fail closed, whether the committed exact G4 certificate
(G4_SM_PATI_SALAM_PHYSICAL_QUOTIENT_V20.json) closes G4 in the ledger.  These
tests pin its purity (standard library only), its constants, its output shape,
its 16 criteria (one forged mutation per criterion must flip exactly that
criterion and the certification), its strict typing (int-not-bool counts and
exact rational strings), its rejection of the superseded p+delta quotient and
of the chiral-track reports, and the strict ledger_g4_closed reader used by the
confirmation verdict.  They are light: no heavy module is imported.
"""
from __future__ import annotations

import ast
import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any, Callable
from unittest import mock

import g3_sm_target_track_v20 as sm_track
import g4_sm_closure_binding_v20 as binding

ROOT = binding.ROOT
LEDGER_JSON = ROOT / "G1_G8_GATE_LEDGER_V20.json"
ALLOWED_IMPORTS = {"__future__", "json", "pathlib", "typing"}
OUTPUT_KEYS = [
    "source",
    "report",
    "required_status",
    "status",
    "n_failed",
    "n_checks",
    "integrity",
    "science",
    "blockers",
    "certified",
    "witness_bound_to_g3_track",
    "required_statement",
    "closure_scope",
    "scope_limits",
    "decision",
]
HISTORICAL_AND_CHIRAL_ARTIFACTS = (
    "EXACT_GAUGED_U1X_PHYSICAL_QUOTIENT_V20.json",
    "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXACT_HESSIAN_V20.json",
    "FINAL_G3_ACCEPTANCE_GATE_V20.json",
)
Mutation = Callable[[dict[str, Any]], None]


def _set(*keys: str, value: Any) -> Mutation:
    def mutate(report: dict[str, Any]) -> None:
        target = report
        for key in keys[:-1]:
            target = target[key]
        target[keys[-1]] = value

    return mutate


def _delete(*keys: str) -> Mutation:
    def mutate(report: dict[str, Any]) -> None:
        target = report
        for key in keys[:-1]:
            target = target[key]
        del target[keys[-1]]

    return mutate


def _first_check_false(report: dict[str, Any]) -> None:
    first = next(iter(report["checks"]))
    report["checks"][first] = False


def _first_premise_false(report: dict[str, Any]) -> None:
    premise = report["premises"]["hessian"]
    premise[next(iter(premise))] = False


def _drop_pq_violating_item(report: dict[str, Any]) -> None:
    report["scope"]["not_covered"] = [
        item for item in report["scope"]["not_covered"] if "PQ-violating" not in item
    ]


def _superseded_ranks(report: dict[str, Any]) -> None:
    gauge = report["gauge_quotient"]
    gauge["ranks"]["SO10_x_U1X"] = 37
    gauge["ranks"]["SO10_x_U1X_x_PQ"] = 38
    gauge["gauge_quotient_dimension_including_axion"] = 449
    gauge["massive_transverse_quotient_dimension"] = 448


def _statement_one_character(report: dict[str, Any]) -> None:
    final = report["final_acceptance_test"]
    final["required_statement"] = final["required_statement"][:-1] + ";"


def _coverage_two_items(report: dict[str, Any]) -> None:
    report["g4_open_scope_coverage"] = report["g4_open_scope_coverage"][:2]


def _first_section_check_false(section: str) -> Mutation:
    def mutate(report: dict[str, Any]) -> None:
        checks = report[section]["checks"]
        checks[next(iter(checks))] = False

    return mutate


def _extra_section_check(report: dict[str, Any]) -> None:
    report["chart_normalisation"]["checks"]["unmirrored_extra_check"] = True


# One forged mutation per criterion: (label, mutation, criterion it must flip).
MUTATIONS: tuple[tuple[str, Mutation, str], ...] = (
    ("old status", _set("status", value="G4_SM_PATI_SALAM_PHYSICAL_QUOTIENT_CERTIFIED__G4_NOT_WIRED"), "g4_report_executes"),
    ("n_failed False", _set("n_failed", value=False), "g4_report_executes"),
    ("n_failed str", _set("n_failed", value="0"), "g4_report_executes"),
    ("n_failed float", _set("n_failed", value=0.0), "g4_report_executes"),
    ("n_checks 70", _set("n_checks", value=70), "g4_report_executes"),
    ("n_checks float", _set("n_checks", value=69.0), "g4_report_executes"),
    ("one check False", _first_check_false, "g4_report_executes"),
    ("theorem not claimed", _set("theorem_claimed", value=False), "g4_report_executes"),
    ("theorem NOT CLAIMED", _set("theorem", value="NOT CLAIMED: failed checks x"), "g4_report_executes"),
    ("overall state", _set("overall_state", value="G4_PHYSICAL_QUOTIENT_OPEN"), "g4_report_executes"),
    ("certificate_passes False", _set("flags", "certificate_passes", value=False), "g4_report_executes"),
    ("gauge_ranks_33_34_35_exact False", _set("flags", "gauge_ranks_33_34_35_exact", value=False), "g4_report_executes"),
    ("gauge_quotient_452_and_transverse_quotient_451_exact False", _set("flags", "gauge_quotient_452_and_transverse_quotient_451_exact", value=False), "g4_report_executes"),
    ("PQ_global_not_gauged_not_eaten False", _set("flags", "PQ_global_not_gauged_not_eaten", value=False), "g4_report_executes"),
    ("physical_axion_identified_exact False", _set("flags", "physical_axion_identified_exact", value=False), "g4_report_executes"),
    ("restricted_hessian_psd_single_zero_mode_axion False", _set("flags", "restricted_hessian_psd_single_zero_mode_axion", value=False), "g4_report_executes"),
    ("no_negative_modes False", _set("flags", "no_negative_modes", value=False), "g4_report_executes"),
    ("zero_modes_35_equal_34_eaten_plus_axion False", _set("flags", "zero_modes_35_equal_34_eaten_plus_axion", value=False), "g4_report_executes"),
    ("tuned_limit_doublet_is_SM_doublet_lifted_at_quartic_order False", _set("flags", "tuned_limit_doublet_is_SM_doublet_lifted_at_quartic_order", value=False), "g4_report_executes"),
    ("vector_boson_gram_by_SM_sector_exact False", _set("flags", "vector_boson_gram_by_SM_sector_exact", value=False), "g4_report_executes"),
    ("wired_into_gate_ledger_as_G4_evidence False", _set("flags", "wired_into_gate_ledger_as_G4_evidence", value=False), "g4_report_executes"),
    ("gauge_quotient section check False", _first_section_check_false("gauge_quotient"), "g4_report_executes"),
    ("fresh_exact_hessians section check False", _first_section_check_false("fresh_exact_hessians"), "g4_report_executes"),
    ("chart_normalisation section check False", _first_section_check_false("chart_normalisation"), "g4_report_executes"),
    ("section check not mirrored", _extra_section_check, "g4_report_executes"),
    ("fresh raised_O06 inertia 450/35/1", _set("fresh_exact_hessians", "variants", "raised_O06", "inertia_positive_zero_negative", value="450/35/1"), "g4_report_executes"),
    ("fresh benchmark not PSD", _set("fresh_exact_hessians", "variants", "benchmark", "exact_PSD", value=False), "g4_report_executes"),
    ("model contract", _set("model_contract_id", value="historical_option_c_no_x_v20"), "g4_report_executes"),
    ("one premise False", _first_premise_false, "g4_premises_all_hold"),
    ("premise removed", _delete("premises", "sigma_audit"), "g4_premises_all_hold"),
    ("closes G4 by itself", _set("flags", "report_closes_g4_by_itself", value=True), "g4_report_does_not_overclaim"),
    ("final closes G4", _set("final_acceptance_test", "closes_g4_by_itself", value=True), "g4_report_does_not_overclaim"),
    ("internal candidate flag", _set("flags", "internal_candidate_approved", value=True), "g4_report_does_not_overclaim"),
    ("G6 closed flag", _set("flags", "G6_closed", value=True), "g4_report_does_not_overclaim"),
    ("top-level G4_closed", _set("G4_closed", value=False), "g4_report_does_not_overclaim"),
    ("tree_level_only False", _set("flags", "tree_level_only", value=False), "g4_report_does_not_overclaim"),
    ("float64 promoted", _set("flags", "compiler_binding_float64_only", value=False), "g4_float_evidence_not_promoted"),
    ("live binding fails", _set("live_compiler_binding", "compiler_binding_passes", value=False), "g4_float_evidence_not_promoted"),
    ("PQ-violating item removed", _drop_pq_violating_item, "g4_scope_limits_disclosed"),
    ("axion scope flag", _set("flags", "axion_massless_only_for_renormalizable_PQ_neutral_potential", value=False), "g4_scope_limits_disclosed"),
    ("witness r0", _set("witness", "r0", value="1/10"), "g4_witness_is_the_g3_witness"),
    ("eps window", _set("witness", "eps_window", "upper_exclusive", value="12"), "g4_witness_is_the_g3_witness"),
    ("witness vacuum", _set("witness", "vacuum", value="q0 = (F, 0, r Delta_R, r0, x0)"), "g4_witness_is_the_g3_witness"),
    ("witness kappa as float", _set("witness", "kappa", value=-0.05), "g4_witness_is_the_g3_witness"),
    ("superseded ranks 37/38", _superseded_ranks, "g4_orbit_ranks_33_34_35_exact"),
    ("superseded quotients 449/448", _superseded_ranks, "g4_gauge_and_transverse_quotients_452_451_exact"),
    ("minor determinant", _set("gauge_quotient", "certificates", "SO10_x_U1X_x_PQ", "minor", "determinant_integer_M", value=68), "g4_orbit_ranks_33_34_35_exact"),
    ("null vectors with X", _set("gauge_quotient", "certificates", "SO10_x_U1X", "null_vectors_without_X_or_PQ_coefficient", value=False), "g4_orbit_ranks_33_34_35_exact"),
    ("rank float", _set("gauge_quotient", "ranks", "SO10", value=33.0), "g4_orbit_ranks_33_34_35_exact"),
    ("null vector count bool", _set("gauge_quotient", "certificates", "SO10", "null_vector_count", value=True), "g4_orbit_ranks_33_34_35_exact"),
    ("W dimension", _set("restricted_hessian", "dimensions", "W", value=451), "g4_gauge_and_transverse_quotients_452_451_exact"),
    ("eaten total 37", _set("gauge_quotient", "eaten_goldstones", "total", value=37), "g4_eaten_goldstones_34_pq_global_not_eaten"),
    ("PQ gauged", _set("gauge_quotient", "PQ", "gauged", value=True), "g4_eaten_goldstones_34_pq_global_not_eaten"),
    ("axion norm", _set("axion", "axion_norm_squared", value="9248/7240"), "g4_physical_axion_exact"),
    ("axion S fraction", _set("axion", "squared_norm_fractions", "S", value="1"), "g4_physical_axion_exact"),
    ("axion period", _set("axion", "decay_constant", "axion_angle_period_modulo_gauge", value="2 pi/34"), "g4_physical_axion_exact"),
    ("v_a squared", _set("axion", "decay_constant", "v_a_squared", value="1/7241"), "g4_physical_axion_exact"),
    ("W inertia", _set("restricted_hessian", "eps_positive", "inertia_on_W_positive_zero_negative", value="450/2/0"), "g4_gauge_quotient_hessian_451_1_0"),
    ("W zero mode", _set("restricted_hessian", "eps_positive", "zero_mode", value="the doublet"), "g4_gauge_quotient_hessian_451_1_0"),
    ("negative mode", _set("zero_mode_classification", "eps_positive", "negative_modes", value=1), "g4_zero_modes_35_are_34_eaten_plus_axion_no_negative"),
    ("unexplained mode", _set("zero_mode_classification", "unexplained_zero_or_negative_modes", value=1), "g4_zero_modes_35_are_34_eaten_plus_axion_no_negative"),
    ("physical axion count bool", _set("zero_mode_classification", "eps_positive", "physical_axion", value=True), "g4_zero_modes_35_are_34_eaten_plus_axion_no_negative"),
    ("doublet label", _set("light_doublet", "SM_label", value="(1,2)_{-1/2}: conjugate"), "g4_tuned_limit_is_one_sm_doublet_lifted_127_64"),
    ("lambda_eff", _set("light_doublet", "tuned_limit", "quartic_lift_lambda_eff", value="2"), "g4_tuned_limit_is_one_sm_doublet_lifted_127_64"),
    ("doublet zero modes", _set("light_doublet", "tuned_limit", "zero_modes", value=5), "g4_tuned_limit_is_one_sm_doublet_lifted_127_64"),
    ("gram rank", _set("vector_bosons", "gram_rank", value=33), "g4_vector_gram_rank_34"),
    ("required statement", _statement_one_character, "g4_required_statement_bound"),
    ("currently passes", _set("final_acceptance_test", "currently_passes", value=False), "g4_required_statement_bound"),
    ("coverage two items", _coverage_two_items, "g4_open_scope_fully_covered"),
    ("coverage not certified", _set("roadmap_W3_G4_acceptance", "no_unexplained_zero_or_negative_modes", value=False), "g4_open_scope_fully_covered"),
)


class G4SmClosureBindingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.committed = binding.load_g4_report()
        cls.ledger = json.loads(LEDGER_JSON.read_text(encoding="utf-8"))
        cls.g3_witness = cls.ledger["g3_sm_target_track"]["witness"]
        cls.g4_open_scope = cls.ledger["gates"]["G4"]["open_scope"]

    def report(self) -> dict[str, Any]:
        return copy.deepcopy(self.committed)

    def evaluate(self, report: Any, **keywords: Any) -> dict[str, Any]:
        return binding.evaluate_g4_binding(report, **keywords)

    # ------------------------------------------------------------------
    # Purity and constants.
    # ------------------------------------------------------------------

    def test_module_imports_only_the_standard_library(self) -> None:
        tree = ast.parse(Path(binding.__file__).read_text(encoding="utf-8"))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                self.assertEqual(node.level, 0)
                imported.add((node.module or "").split(".")[0])
        self.assertEqual(imported, ALLOWED_IMPORTS)

    def test_pinned_constants(self) -> None:
        self.assertEqual(
            binding.DOWNSTREAM_BLOCKERS_AFTER_G4,
            ("GAUGED_U1X_G6_G7_G8_CLOSURE_REQUIRED",) + sm_track.DOWNSTREAM_BLOCKERS[2:],
        )
        self.assertNotIn("G4_SM_WITNESS_ZERO_MODES_AND_RANKS_34_35_UNCLASSIFIED", binding.DOWNSTREAM_BLOCKERS_AFTER_G4)
        self.assertEqual(len(binding.INTEGRITY_NAMES), 5)
        self.assertEqual(len(binding.SCIENCE_NAMES), 11)
        self.assertEqual(len(set(binding.INTEGRITY_NAMES + binding.SCIENCE_NAMES)), 16)
        self.assertEqual(
            binding.G4_REQUIRED_STATEMENT, self.committed["final_acceptance_test"]["required_statement"]
        )
        self.assertEqual(binding.REQUIRED_N_CHECKS, 69)
        self.assertEqual(binding.REQUIRED_STATUS, "G4_SM_PATI_SALAM_PHYSICAL_QUOTIENT_CERTIFIED__WIRED_AS_G4_EVIDENCE")
        self.assertEqual(binding.WITNESS, {"r0": "1/5", "x0": "1", "kappa": "-1/20"})
        self.assertEqual(binding.EXPECTED_RANKS, {"SO10": 33, "SO10_x_U1X": 34, "SO10_x_U1X_x_PQ": 35})
        self.assertEqual((binding.GAUGE_QUOTIENT, binding.TRANSVERSE_QUOTIENT), (452, 451))
        self.assertEqual(binding.ROUTED_G4_CAVEAT_ID, "zero_modes_and_ranks_at_witness")
        routed = [spec["id"] for spec in sm_track.CAVEAT_SPECS if spec["gate"] == "G4"]
        self.assertEqual(routed, [binding.ROUTED_G4_CAVEAT_ID])
        self.assertEqual(len(binding.G4_SCOPE_LIMITS), 5)
        for text in (binding.G4_CLOSED_SENTENCE, binding.G4_LEDGER_CLOSED_SCOPE):
            self.assertIn("r0 = 1/5, x0 = 1, kappa = -r0/4", text)
            self.assertIn("tree level", text)
            self.assertIn("renormalizable PQ-neutral benchmark potential", text)
            self.assertIn("127/64", text)
        self.assertIn("QCD anomaly", binding.G4_CLOSED_SENTENCE)
        self.assertIn("PQ-violating", binding.G4_CLOSED_SENTENCE)
        # Decision D-E overrides the D3 cascade: G4 CLOSED approves nothing.
        self.assertFalse(hasattr(binding, "D3_CASCADE"))
        self.assertIn("decision D-E (2026-09-26) overrides the decision-D3 cascade", binding.G4_CLOSURE_DECISION)
        self.assertIn("held until G7 is CLOSED", binding.G4_CLOSURE_DECISION)
        self.assertIn("stay OPEN or BLOCKED", binding.G4_CLOSURE_DECISION)
        self.assertNotIn("the internal-candidate tier is approved", binding.G4_CLOSURE_DECISION)
        for marker in binding.SCOPE_LIMIT_MARKERS:
            self.assertTrue(any(marker in item for item in self.committed["scope"]["not_covered"]), marker)
        self.assertEqual(len(binding.CERTIFIED_FLAGS), 11)
        self.assertEqual(len(set(binding.CERTIFIED_FLAGS)), 11)
        for name in binding.CERTIFIED_FLAGS:
            self.assertIs(self.committed["flags"][name], True, name)

    # ------------------------------------------------------------------
    # The committed certificate.
    # ------------------------------------------------------------------

    def test_committed_report_is_certified(self) -> None:
        result = self.evaluate(self.committed)
        self.assertEqual(list(result), OUTPUT_KEYS)
        self.assertIs(result["certified"], True, result["blockers"])
        self.assertEqual(result["blockers"], [])
        self.assertEqual(list(result["integrity"]), list(binding.INTEGRITY_NAMES))
        self.assertEqual(list(result["science"]), list(binding.SCIENCE_NAMES))
        self.assertTrue(all(value is True for value in result["integrity"].values()))
        self.assertTrue(all(value is True for value in result["science"].values()))
        self.assertEqual(result["source"], binding.G4_SOURCE)
        self.assertEqual(result["report"], binding.G4_REPORT_FILE)
        self.assertEqual(result["required_status"], binding.REQUIRED_STATUS)
        self.assertEqual(result["status"], binding.REQUIRED_STATUS)
        self.assertEqual(result["n_failed"], 0)
        self.assertEqual(result["n_checks"], 69)
        self.assertIs(result["witness_bound_to_g3_track"], False)
        self.assertEqual(result["required_statement"], binding.G4_REQUIRED_STATEMENT)
        self.assertEqual(result["closure_scope"], binding.G4_LEDGER_CLOSED_SCOPE)
        self.assertEqual(result["scope_limits"], list(binding.G4_SCOPE_LIMITS))
        self.assertEqual(result["decision"], binding.G4_CLOSURE_DECISION)

    def test_committed_report_is_certified_against_the_ledger_witness_and_open_scope(self) -> None:
        result = self.evaluate(self.committed, g3_witness=self.g3_witness, g4_open_scope=self.g4_open_scope)
        self.assertIs(result["certified"], True, result["blockers"])
        self.assertIs(result["witness_bound_to_g3_track"], True)
        self.assertEqual(result["blockers"], [])
        self.assertEqual(self.g3_witness["id"], "sm_pati_salam_eps_member")
        self.assertEqual(len(self.g4_open_scope), 3)

    def test_output_is_json_native_and_deterministic(self) -> None:
        first = self.evaluate(self.committed, g3_witness=self.g3_witness, g4_open_scope=tuple(self.g4_open_scope))
        second = self.evaluate(self.report(), g3_witness=self.g3_witness, g4_open_scope=list(self.g4_open_scope))
        self.assertEqual(first, second)
        self.assertEqual(json.loads(json.dumps(first)), first)
        self.assertIsInstance(first["n_failed"], int)
        self.assertIsInstance(first["scope_limits"], list)

    # ------------------------------------------------------------------
    # Fail-closed inputs.
    # ------------------------------------------------------------------

    def test_non_report_inputs_fail_closed(self) -> None:
        for value in ({}, None, [], "report", 0, [self.committed]):
            with self.subTest(value=type(value).__name__):
                result = self.evaluate(value)
                self.assertIs(result["certified"], False)
                self.assertEqual(result["blockers"], list(binding.INTEGRITY_NAMES + binding.SCIENCE_NAMES))
                self.assertIsNone(result["status"])
                self.assertIsNone(result["n_failed"])
                self.assertIsNone(result["n_checks"])

    def test_unreadable_missing_or_non_dict_files_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            cases = {
                "missing": folder / "missing.json",
                "directory": folder,
                "not_utf8": folder / "binary.json",
                "not_json": folder / "text.json",
                "json_list": folder / "list.json",
                "empty_dict": folder / "empty.json",
            }
            cases["not_utf8"].write_bytes(b"\xff\xfe\xfa{")
            cases["not_json"].write_text("{not json", encoding="utf-8")
            cases["json_list"].write_text(json.dumps([self.committed]), encoding="utf-8")
            cases["empty_dict"].write_text("{}", encoding="utf-8")
            for label, path in cases.items():
                with self.subTest(label=label):
                    loaded = binding.load_g4_report(path)
                    self.assertEqual(loaded, {})
                    self.assertIs(self.evaluate(loaded)["certified"], False)
            good = folder / "good.json"
            good.write_text(json.dumps(self.committed), encoding="utf-8")
            self.assertIs(self.evaluate(binding.load_g4_report(str(good)))["certified"], True)

    # ------------------------------------------------------------------
    # One mutation per criterion.
    # ------------------------------------------------------------------

    def test_each_forged_mutation_flips_its_criterion(self) -> None:
        covered: set[str] = set()
        for label, mutate, criterion in MUTATIONS:
            with self.subTest(mutation=label):
                report = self.report()
                mutate(report)
                result = self.evaluate(report, g3_witness=self.g3_witness, g4_open_scope=self.g4_open_scope)
                section = "integrity" if criterion in binding.INTEGRITY_NAMES else "science"
                self.assertIs(result[section][criterion], False, criterion)
                self.assertIn(criterion, result["blockers"])
                self.assertIs(result["certified"], False)
                covered.add(criterion)
        self.assertEqual(covered, set(binding.INTEGRITY_NAMES + binding.SCIENCE_NAMES))

    def test_malformed_sections_fail_closed_without_raising(self) -> None:
        for key in ("witness", "gauge_quotient", "axion", "restricted_hessian", "zero_mode_classification",
                    "light_doublet", "vector_bosons", "final_acceptance_test", "g4_open_scope_coverage",
                    "flags", "scope", "premises", "checks"):
            for value in (None, [], "x", 7):
                with self.subTest(key=key, value=value):
                    report = self.report()
                    report[key] = value
                    self.assertIs(self.evaluate(report)["certified"], False)

    def test_mismatched_g3_witness_fails_closed(self) -> None:
        kappa = copy.deepcopy(self.g3_witness)
        kappa["benchmark"]["kappa"] = "-1/10"
        vacuum = copy.deepcopy(self.g3_witness)
        vacuum["vacuum"] = "(F, r Delta_R)"
        chiral_id = copy.deepcopy(self.g3_witness)
        chiral_id["id"] = "chiral_H_SU5_Delta"
        window = copy.deepcopy(self.g3_witness)
        window["eps_window"]["upper_exclusive"] = "12"
        for label, witness in (("kappa", kappa), ("vacuum", vacuum), ("id", chiral_id), ("window", window),
                               ("empty", {}), ("list", [])):
            with self.subTest(witness=label):
                result = self.evaluate(self.committed, g3_witness=witness, g4_open_scope=self.g4_open_scope)
                self.assertIs(result["science"]["g4_witness_is_the_g3_witness"], False)
                self.assertIs(result["certified"], False)
                self.assertEqual(result["blockers"], ["g4_witness_is_the_g3_witness"])

    def test_coverage_item_changed_against_the_ledger_open_scope_fails_closed(self) -> None:
        report = self.report()
        report["g4_open_scope_coverage"][1]["item"] += " (edited)"
        result = self.evaluate(report, g4_open_scope=self.g4_open_scope)
        self.assertIs(result["science"]["g4_open_scope_fully_covered"], False)
        self.assertIs(result["certified"], False)
        edited_scope = list(self.g4_open_scope)
        edited_scope[0] += " (edited)"
        for scope in (edited_scope, self.g4_open_scope[:2], "one string", []):
            with self.subTest(scope=str(scope)[:20]):
                result = self.evaluate(self.committed, g4_open_scope=scope)
                self.assertIs(result["science"]["g4_open_scope_fully_covered"], False)
                self.assertIs(result["certified"], False)

    def test_historical_and_chiral_artifacts_are_not_certified(self) -> None:
        for name in HISTORICAL_AND_CHIRAL_ARTIFACTS:
            with self.subTest(artifact=name):
                report = binding.load_g4_report(ROOT / name)
                self.assertTrue(report, name)
                result = self.evaluate(report, g3_witness=self.g3_witness, g4_open_scope=self.g4_open_scope)
                self.assertIs(result["certified"], False)
                self.assertIn("g4_report_executes", result["blockers"])
        superseded = self.evaluate(binding.load_g4_report(ROOT / HISTORICAL_AND_CHIRAL_ARTIFACTS[0]))
        for criterion in (
            "g4_report_executes",
            "g4_orbit_ranks_33_34_35_exact",
            "g4_gauge_and_transverse_quotients_452_451_exact",
        ):
            self.assertIn(criterion, superseded["blockers"])

    # ------------------------------------------------------------------
    # ledger_g4_closed.
    # ------------------------------------------------------------------

    def _ledger(self, **row: Any) -> dict[str, Any]:
        return {"gates": {"G4": row}}

    def _evidence(self, **overrides: Any) -> dict[str, Any]:
        evidence = {
            "certified": True,
            "required_status": binding.REQUIRED_STATUS,
            "status": binding.REQUIRED_STATUS,
        }
        evidence.update(overrides)
        return evidence

    def test_ledger_g4_closed_is_strict(self) -> None:
        self.assertIs(binding.ledger_g4_closed(self._ledger(status="CLOSED", closure_evidence=self._evidence())), True)
        false_cases = {
            "empty": {},
            "none": None,
            "list": [],
            "no gates": {"gates": None},
            "closed without evidence": self._ledger(status="CLOSED"),
            "evidence not a mapping": self._ledger(status="CLOSED", closure_evidence=[True]),
            "certified str": self._ledger(status="CLOSED", closure_evidence=self._evidence(certified="true")),
            "certified int": self._ledger(status="CLOSED", closure_evidence=self._evidence(certified=1)),
            "required status changed": self._ledger(
                status="CLOSED", closure_evidence=self._evidence(required_status=binding.INCOMPLETE_STATUS)
            ),
            "report status changed": self._ledger(
                status="CLOSED",
                closure_evidence=self._evidence(status="G4_SM_PATI_SALAM_PHYSICAL_QUOTIENT_CERTIFIED__G4_NOT_WIRED"),
            ),
            "open with certified evidence": self._ledger(status="OPEN", closure_evidence=self._evidence()),
            "status lowercase": self._ledger(status="closed", closure_evidence=self._evidence()),
        }
        for label, ledger in false_cases.items():
            with self.subTest(case=label):
                self.assertIs(binding.ledger_g4_closed(ledger), False)

    def test_ledger_g4_closed_agrees_with_the_committed_ledger_row(self) -> None:
        row = self.ledger["gates"]["G4"]
        evidence = row.get("closure_evidence")
        expected = bool(
            row.get("status") == "CLOSED"
            and isinstance(evidence, dict)
            and evidence.get("certified") is True
            and evidence.get("status") == binding.REQUIRED_STATUS
        )
        self.assertIs(binding.ledger_g4_closed(self.ledger), expected)

    # ------------------------------------------------------------------
    # CLI.
    # ------------------------------------------------------------------

    def test_main_prints_the_binding_and_exits_zero_on_the_committed_report(self) -> None:
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            self.assertEqual(binding.main(), 0)
        printed = json.loads(stream.getvalue())
        self.assertIs(printed["certified"], True)
        self.assertEqual(printed["blockers"], [])
        self.assertEqual(stream.getvalue(), json.dumps(printed, indent=2, sort_keys=True) + "\n")

    def test_main_exits_nonzero_on_a_missing_report(self) -> None:
        with mock.patch.object(binding, "load_g4_report", return_value={}), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(binding.main([]), 1)


if __name__ == "__main__":
    unittest.main()
