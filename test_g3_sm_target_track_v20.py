#!/usr/bin/env python3
"""Tests for the SM Pati-Salam track of the final G3 gate (g3_sm_target_track_v20).

The track is pure: it reads four committed JSON artifacts and evaluates exact
conjunctions of their evidence keys.  These tests run on deep copies of the
committed inputs (fast; nothing heavy is imported), check that the committed
inputs close the track when the release prerequisites hold, and forge one
input at a time to show that every criterion fails closed.  They run under
both unittest and pytest.
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

import g3_sm_target_track_v20 as sm_track

ALL = {key: True for key in sm_track.PREREQUISITE_KEYS}
ALLOWED_IMPORTS = {"__future__", "json", "fractions", "pathlib", "typing"}
RELEASE_NAMES = [
    "authoritative_external_model_contract_executed",
    "G1_promoted_closed",
    "G2_promoted_closed",
]
RESULT_KEYS = {
    "track",
    "role",
    "model_contract_id",
    "inputs",
    "missing_inputs",
    "artifact_integrity",
    "science_criteria",
    "release_prerequisites",
    "prerequisites_evaluated",
    "mathematically_closed",
    "closed",
    "blockers",
    "decisive_theorem",
    "decisive_theorem_emitted_by",
    "witness",
    "closure_scope",
    "disclosures",
    "downstream_caveats",
    "downstream_caveats_scope_open",
    "downstream_caveats_resolved",
    "downstream_blockers",
    "unchecked_proof_inputs",
    "g5_bfb_binding",
    "decisions",
    "self_claim_note",
}
WITNESS_KEYS = {
    "id",
    "potential",
    "definition",
    "benchmark",
    "vacuum",
    "p",
    "sigma_std",
    "symmetry_group",
    "eps_window",
    "certified_members",
    "hessian_for_every_eps_positive",
    "doublet_mass_squared",
    "tuned_limit_not_the_witness",
    "sentence",
    "decision",
}
CAVEAT_GATES = [
    ("sub_M_I_coloured_126bar_states", "G6"),
    ("positivity_without_EWSB", "G6"),
    ("phi17_benchmark_scale", "G6"),
    ("rg_anchor_field_content", "G7"),
    ("higgs_quartic_matching", "G7"),
    ("tan_beta_one_light_doublet", "G8"),
    ("realistic_yukawa_sector", "G8"),
    ("proton_decay_mediators", "G8"),
    ("zero_modes_and_ranks_at_witness", "G4"),
    ("naturalness_of_tunings", "OUTSIDE_G1_G8"),
]
# The user's CLAIM SCOPE, pinned verbatim.
USER_CLAIM_SCOPE = (
    "G3 closed on the SM Pati-Salam benchmark family: the exact SM-preserving global vacuum of the declared "
    "exact-X potential's 27-parameter benchmark with the light-doublet deformation eps > 0, unique modulo "
    "SO(10) x U(1)_X x accidental U(1)_PQ; tuned DT/M_I relations; G4 OPEN, G6-G8 blocked; caveats routed "
    "downstream; internal candidate withheld; whole model neither validated nor excluded."
)
SM_FINAL_THEOREM_TEXT = (
    "For every 486-real field q, V_PS,eps(q)-V_PS,eps(q0)>=0; equality holds exactly on the SO(10)xU(1)_XxPQ "
    "orbit of q0."
)


class SmTargetTrackTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base = sm_track.load_inputs()

    def inputs(self) -> dict[str, dict[str, Any]]:
        return copy.deepcopy(self.base)

    def evaluate(self, inputs: Any, prerequisites: Any = ALL) -> dict[str, Any]:
        prereq = dict(prerequisites) if isinstance(prerequisites, dict) else prerequisites
        return sm_track.evaluate_sm_track(inputs, prerequisites=prereq)

    # ------------------------------------------------------------------
    # Purity.
    # ------------------------------------------------------------------

    def test_module_imports_only_the_standard_library(self) -> None:
        tree = ast.parse(Path(sm_track.__file__).read_text(encoding="utf-8"))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                self.assertEqual(node.level, 0)
                imported.add((node.module or "").split(".")[0])
        self.assertTrue(imported <= ALLOWED_IMPORTS, imported - ALLOWED_IMPORTS)
        self.assertEqual(imported, ALLOWED_IMPORTS)

    def test_pinned_strings(self) -> None:
        self.assertEqual(sm_track.CLOSURE_SCOPE, USER_CLAIM_SCOPE)
        self.assertEqual(sm_track.SM_FINAL_THEOREM, SM_FINAL_THEOREM_TEXT)
        self.assertEqual(sm_track.DECISIONS["D5"], sm_track.CAVEAT_ROUTING_SENTENCE)
        self.assertEqual(list(sm_track.DECISIONS), ["D1", "D2", "D3", "D4", "D5", "D6"])
        self.assertEqual(len(sm_track.DISCLOSURES), 7)
        self.assertEqual(len(sm_track.PINNED_CITED_NOT_MACHINE_CHECKED), 6)
        self.assertEqual(len(sm_track.PINNED_ELEMENTARY_NOT_MACHINE_CHECKED), 6)
        self.assertEqual(str(sm_track.PERTURBATIVE_BOUND - 2 * abs(sm_track.BENCHMARK["kappa"]) * sm_track.BENCHMARK["r0"]),
                         sm_track.EPS_WINDOW_UPPER)
        for text in (sm_track.WITNESS_SENTENCE, sm_track.G3_LEDGER_CLOSED_SCOPE):
            self.assertIn("0 < eps < 599/50", text)
        self.assertIn("rank 451 and nullity 35", sm_track.WITNESS_SENTENCE)
        self.assertIn("the tuned eps = 0 point (447/39) is not the witness", sm_track.WITNESS_SENTENCE)
        self.assertIn("exact Hessian 451/35", sm_track.G3_LEDGER_CLOSED_SCOPE)
        self.assertIn("(34 gauge -> 452, 35 -> 451)", sm_track.CAVEAT_ROUTING_SENTENCE)
        self.assertIn("V4 >= |q|^4/167", sm_track.G5_LEDGER_CLOSED_SCOPE)
        self.assertTrue(sm_track.D3_RULE.startswith("D3: G1-G3 CLOSED does not approve an internal candidate"))
        self.assertEqual(len(sm_track.DOWNSTREAM_BLOCKERS), 5)
        self.assertEqual(sm_track.FAIL_CLOSED_BLOCKERS,
                         ("GAUGED_U1X_G3_G8_CLOSURE_REQUIRED", "G3_SM_PATI_SALAM_TRACK_NOT_CERTIFIED"))

    # ------------------------------------------------------------------
    # The committed inputs close the track.
    # ------------------------------------------------------------------

    def test_committed_inputs_close_the_track(self) -> None:
        result = self.evaluate(self.inputs())
        self.assertEqual(set(result), RESULT_KEYS)
        self.assertEqual(result["track"], "sm_pati_salam")
        self.assertEqual(result["role"], "ONLY_CLOSURE_ROUTE")
        self.assertEqual(result["model_contract_id"], "gauged_u1x_phi17_v20")
        self.assertEqual(result["missing_inputs"], [])
        self.assertTrue(all(row["loaded"] for row in result["inputs"].values()))
        self.assertEqual(list(result["artifact_integrity"]), list(sm_track.ARTIFACT_INTEGRITY_NAMES))
        self.assertEqual(list(result["science_criteria"]), list(sm_track.SCIENCE_CRITERIA_NAMES))
        self.assertEqual(list(result["release_prerequisites"]), RELEASE_NAMES)
        self.assertEqual((len(result["artifact_integrity"]), len(result["science_criteria"])), (10, 13))
        for block in ("artifact_integrity", "science_criteria", "release_prerequisites"):
            for name, value in result[block].items():
                self.assertIs(value, True, name)
        self.assertIs(result["prerequisites_evaluated"], True)
        self.assertIs(result["mathematically_closed"], True)
        self.assertIs(result["closed"], True)
        self.assertEqual(result["blockers"], [])

        committed_statement = self.base["exact_hessian"]["eps_family"]["final_acceptance_test"]["required_statement"]
        self.assertEqual(result["decisive_theorem"], sm_track.SM_FINAL_THEOREM)
        self.assertEqual(result["decisive_theorem"], committed_statement)
        self.assertEqual(
            result["decisive_theorem_emitted_by"],
            "G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json:eps_family.final_acceptance_test.required_statement",
        )

        witness = result["witness"]
        self.assertEqual(set(witness), WITNESS_KEYS)
        self.assertEqual(witness["eps_window"]["upper_exclusive"], "599/50")
        self.assertEqual(witness["eps_window"]["lower_exclusive"], "0")
        self.assertEqual(witness["benchmark"], {"r0": "1/5", "x0": "1", "kappa": "-1/20", "O06_base": "1/50"})
        self.assertEqual(witness["certified_members"], {"raised_O06": "1/2500", "tiny_eps": "1/25000000"})
        self.assertEqual(witness["sentence"], sm_track.WITNESS_SENTENCE)
        self.assertEqual(witness["decision"], "D2")
        self.assertEqual(witness["sigma_std"], "z1^z2^z3^z4^z5")

        self.assertEqual([(row["id"], row["gate"]) for row in result["downstream_caveats"]], CAVEAT_GATES)
        for row in result["downstream_caveats"]:
            self.assertEqual(set(row), {"id", "gate", "also_affects", "blocker", "text", "evidence", "resolved"})
            self.assertEqual(set(row["evidence"]), {"artifact", "key", "value"})
            self.assertIs(row["resolved"], False, row["id"])
            self.assertTrue(row["blocker"] is None or row["blocker"] in sm_track.DOWNSTREAM_BLOCKERS, row["id"])
            self.assertTrue(row["blocker"] is None or row["blocker"].startswith(row["gate"]), row["id"])
        g4 = next(row for row in result["downstream_caveats"] if row["gate"] == "G4")
        for fragment in ("34/35", "452/451", "axion/PQ", "eps -> 0"):
            self.assertIn(fragment, g4["text"])
        self.assertIs(result["downstream_caveats_resolved"], False)
        self.assertEqual(result["downstream_caveats_scope_open"], self.base["candidate"]["scope"]["open"])
        self.assertEqual(result["downstream_blockers"], list(sm_track.DOWNSTREAM_BLOCKERS))

        g5 = result["g5_bfb_binding"]
        self.assertIs(g5["certified"], True)
        self.assertIs(g5["certified_on_coupling_vector"], True)
        self.assertIs(g5["covers_eps_witness_family"], True)
        self.assertEqual(len(g5["coefficients"]), 27)
        self.assertEqual(g5["coefficients"], self.base["candidate"]["candidate"]["exact_nonzero_coefficients"])
        self.assertEqual(g5["quartic_bound_constant"], "1/167")
        self.assertEqual(g5["decision"], "D4")
        self.assertEqual(sm_track.g5_bfb_binding(self.inputs()), g5)

        proof = result["unchecked_proof_inputs"]
        self.assertIs(proof["allowlist_matches"], True)
        self.assertEqual(proof["accepted_under"], "D6")
        self.assertEqual(proof["cited_theorems"], self.base["equality_set"]["scope"]["cited_not_machine_checked"])
        self.assertEqual(proof["elementary_steps"], self.base["equality_set"]["scope"]["elementary_not_machine_checked"])
        self.assertEqual(result["closure_scope"], USER_CLAIM_SCOPE)
        self.assertEqual(result["disclosures"], list(sm_track.DISCLOSURES))
        self.assertEqual(result["decisions"], sm_track.DECISIONS)
        self.assertEqual(result["self_claim_note"], sm_track.SELF_CLAIM_NOTE)

    def test_default_arguments_load_the_committed_inputs(self) -> None:
        self.assertEqual(sm_track.evaluate_sm_track(prerequisites=dict(ALL)), self.evaluate(self.inputs()))

    # ------------------------------------------------------------------
    # Release prerequisites.
    # ------------------------------------------------------------------

    def test_prerequisites_not_evaluated_keep_the_track_open(self) -> None:
        for result in (self.evaluate(self.inputs(), None), sm_track.evaluate_sm_track(self.inputs())):
            self.assertIs(result["closed"], False)
            self.assertIs(result["prerequisites_evaluated"], False)
            self.assertIs(result["mathematically_closed"], False)
            self.assertEqual(result["blockers"], ["G1_G2_exact_scoped_calculations_complete", *RELEASE_NAMES])
            self.assertTrue(all(value is False for value in result["release_prerequisites"].values()))
            self.assertTrue(all(result["artifact_integrity"].values()))

    def test_each_prerequisite_is_required(self) -> None:
        for key in sm_track.PREREQUISITE_KEYS:
            for value in (False, None, "True", 1):
                prereq = {**ALL, key: value}
                result = self.evaluate(self.inputs(), prereq)
                self.assertIs(result["closed"], False, (key, value))
                self.assertIs(result["prerequisites_evaluated"], True)
                self.assertIn(key, result["blockers"], (key, value))
            result = self.evaluate(self.inputs(), {k: v for k, v in ALL.items() if k != key})
            self.assertIs(result["closed"], False, key)
            self.assertIn(key, result["blockers"])

    # ------------------------------------------------------------------
    # Forgery: every criterion fails closed.
    # ------------------------------------------------------------------

    def _assert_forgery(self, label: str, mutate: Callable[[dict[str, Any]], None], *names: str) -> dict[str, Any]:
        inputs = self.inputs()
        mutate(inputs)
        result = self.evaluate(inputs)
        self.assertIs(result["closed"], False, label)
        self.assertIs(result["mathematically_closed"], False, label)
        for name in names:
            block = result["artifact_integrity"] if name in result["artifact_integrity"] else result["science_criteria"]
            self.assertIs(block[name], False, (label, name))
            self.assertIn(name, result["blockers"], (label, name))
        return result

    def test_forged_inputs_fail_closed(self) -> None:
        def setter(*path: str, value: Any) -> Callable[[dict[str, Any]], None]:
            def mutate(inputs: dict[str, dict[str, Any]]) -> None:
                target: Any = inputs
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = value
            return mutate

        def deleter(*path: str) -> Callable[[dict[str, Any]], None]:
            def mutate(inputs: dict[str, dict[str, Any]]) -> None:
                target: Any = inputs
                for key in path[:-1]:
                    target = target[key]
                del target[path[-1]]
            return mutate

        def append_cited(inputs: dict[str, dict[str, Any]]) -> None:
            inputs["equality_set"]["scope"]["cited_not_machine_checked"].append("Hilbert's Nullstellensatz")

        def reword_elementary(inputs: dict[str, dict[str, Any]]) -> None:
            steps = inputs["equality_set"]["scope"]["elementary_not_machine_checked"]
            steps[0] = steps[0].replace("Cauchy-Schwarz", "Cauchy-Schwarz-Bunyakovsky")

        def first_exact_check_false(inputs: dict[str, dict[str, Any]]) -> None:
            checks = inputs["candidate"]["exact_certificate"]["checks"]
            checks[sorted(checks)[0]] = False

        o06 = sm_track.O06_ID
        cases = [
            ("candidate status", setter("candidate", "status", value="SM_PATI_SALAM_G3_CANDIDATE__FORGED"),
             ("sm_candidate_report_executes",)),
            ("candidate n_failed bool", setter("candidate", "n_failed", value=False), ("sm_candidate_report_executes",)),
            ("candidate check is int", setter("candidate", "checks", "exact_state_binding", value=1),
             ("sm_candidate_report_executes",)),
            ("equality self-weight", setter("equality_set", "P2_sigma", "self_weights_54_1050bar_2772bar_4125", "4125",
                                            value="1"), ("sm_reports_cross_bound",)),
            ("extra cited theorem", append_cited, ("sm_unchecked_proof_inputs_pinned",)),
            ("reworded elementary step", reword_elementary, ("sm_unchecked_proof_inputs_pinned",)),
            ("caveat flag is a string", setter("candidate", "flags", "higgs_mass_compatible", value="false"),
             ("sm_model_level_caveats_disclosed",)),
            ("V_beta required statement",
             setter("exact_hessian", "eps_family", "final_acceptance_test", "required_statement",
                    value=SM_FINAL_THEOREM_TEXT.replace("V_PS,eps", "V_beta")),
             ("sm_decisive_theorem_string_bound",)),
            ("final_acceptance_test deleted", deleter("exact_hessian", "eps_family", "final_acceptance_test"),
             ("sm_decisive_theorem_string_bound",)),
            ("currently_passes False",
             setter("exact_hessian", "eps_family", "final_acceptance_test", "currently_passes", value=False),
             ("sm_decisive_theorem_string_bound",)),
            ("closes_g3_by_itself True",
             setter("exact_hessian", "eps_family", "final_acceptance_test", "closes_g3_by_itself", value=True),
             ("sm_reports_do_not_overclaim", "sm_decisive_theorem_string_bound")),
            ("L2 intersection check False",
             setter("exact_hessian", "eps_family", "checks", "L2_dim_ker_H0_cap_ker_hess_N_H_equals_35", value=False),
             ("sm_exact_hessian_eps_family_executes", "sm_eps_witness_full_Hessian_rank_451_nullity_35_exact")),
            ("equality report closes G3", setter("equality_set", "flags", "report_closes_g3_by_itself", value=True),
             ("sm_reports_do_not_overclaim",)),
            ("wired flag re-added", setter("exact_hessian", "flags", "candidate_wired_into_g3_gate", value=False),
             ("sm_reports_do_not_overclaim",)),
            ("candidate claims G3", setter("candidate", "flags", "g3_closed", value=True), ("sm_reports_do_not_overclaim",)),
            ("candidate O06 1/25", setter("candidate", "candidate", "exact_nonzero_coefficients", o06, value="1/25"),
             ("sm_reports_cross_bound", "sm_eps_witness_couplings_perturbative_exact")),
            ("eps window upper 12",
             setter("exact_hessian", "eps_family", "final_acceptance_test", "eps_window", "upper_exclusive", value="12"),
             ("sm_eps_witness_couplings_perturbative_exact",)),
            ("tiny inertia 450/36/0",
             setter("exact_hessian", "eps_family", "consistency_certificates", "tiny_eps",
                    "inertia_positive_zero_negative", value="450/36/0"),
             ("sm_eps_witness_full_Hessian_rank_451_nullity_35_exact",)),
            ("candidate exact check False", first_exact_check_false, ("sm_eps_witness_global_gap_exact",)),
            ("Hessian r0 as a float", setter("exact_hessian", "benchmark", "r0", value=0.2),
             ("sm_reports_cross_bound", "sm_eps_witness_full_Hessian_rank_451_nullity_35_exact")),
            ("raised O06 rank", setter("exact_hessian", "exact_certificate_raised_O06", "exact_rank", value=450),
             ("sm_raised_O06_control_rank_451_nullity_35_exact",)),
            ("doublet flag", setter("exact_hessian", "flags", "doublet_mass_squared_equals_eps", value=False),
             ("sm_eps_witness_light_doublet_mass_squared_equals_eps_exact",)),
            ("tuned limit nullity", setter("exact_hessian", "exact_certificate", "exact_nullity", value=35),
             ("sm_eps_witness_quotient_strictly_positive_kernel_is_orbit_exact",)),
            ("PQ not needed", setter("equality_set", "flags", "unique_modulo_SO10_x_U1X_alone", value=True),
             ("sm_eps_witness_equality_set_single_G_orbit_exact",)),
            ("orbit rank", setter("equality_set", "P3_H_S_Phi17_phases", "tangent_rank", "rank_so10", value=34),
             ("sm_symmetry_orbit_ranks_33_34_35_exact",)),
            ("slice gradient", setter("candidate", "exact_slice", "gradient_at_vacuum", value=["0", "0", "0", "1/10"]),
             ("sm_eps_witness_exactly_stationary",)),
            ("exact-X count", setter("candidate", "candidate", "exact_X_parameter_count", value=50),
             ("G1_G2_exact_scoped_calculations_complete",)),
            ("float evidence promoted", setter("candidate", "flags", "hessian_kernel_count_is_float64", value=False),
             ("sm_float_evidence_not_promoted",)),
        ]
        for label, mutate, names in cases:
            with self.subTest(label=label):
                self._assert_forgery(label, mutate, *names)

    def test_missing_hessian_fails_closed_and_is_named(self) -> None:
        inputs = self.inputs()
        inputs["exact_hessian"] = {}
        result = self.evaluate(inputs)
        self.assertIs(result["closed"], False)
        self.assertIs(result["artifact_integrity"]["sm_exact_hessian_report_executes"], False)
        self.assertIn("sm_exact_hessian_report_executes", result["blockers"])
        self.assertIn("G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json", result["missing_inputs"])
        self.assertEqual(sm_track.missing_inputs(inputs), ["G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json"])
        self.assertIs(result["inputs"]["exact_hessian"]["loaded"], False)
        self.assertIs(result["g5_bfb_binding"]["covers_eps_witness_family"], False)
        self.assertIs(result["g5_bfb_binding"]["certified"], False)
        self.assertIsNone(result["witness"]["eps_window"]["upper_exclusive"])
        self.assertEqual(result["witness"]["certified_members"], {"raised_O06": None, "tiny_eps": None})
        json.dumps(result)

    def test_missing_sigma_audit_fails_closed(self) -> None:
        inputs = self.inputs()
        inputs["sigma_hypercharge"] = {}
        result = self.evaluate(inputs)
        self.assertIs(result["closed"], False)
        for name in ("sm_sigma_hypercharge_audit_executes", "sm_target_unbroken_algebra_is_standard_model_exact"):
            self.assertIn(name, result["blockers"])
        self.assertEqual(result["missing_inputs"], ["G3_SIGMA_HYPERCHARGE_AUDIT_V20.json"])

    def test_non_dict_entries_count_as_empty(self) -> None:
        inputs: dict[str, Any] = self.inputs()
        inputs["candidate"] = [1, 2, 3]
        inputs["equality_set"] = "not a report"
        del inputs["sigma_hypercharge"]
        result = self.evaluate(inputs)
        self.assertIs(result["closed"], False)
        self.assertEqual(
            result["missing_inputs"],
            ["G3_SM_PATI_SALAM_CANDIDATE_V20.json", "G3_SM_PATI_SALAM_EQUALITY_SET_V20.json",
             "G3_SIGMA_HYPERCHARGE_AUDIT_V20.json"],
        )
        self.assertEqual(result["g5_bfb_binding"]["coefficients"], {})
        self.assertEqual(result["downstream_caveats_scope_open"], [])
        result = self.evaluate({}, None)
        self.assertEqual(result["missing_inputs"], list(sm_track.INPUT_FILES.values()))
        self.assertTrue(all(value is False for value in result["artifact_integrity"].values()))
        self.assertTrue(all(value is False for value in result["science_criteria"].values()))

    def test_bfb_constant_forgery_uncertifies_g5(self) -> None:
        def forge_constant(inputs: dict[str, dict[str, Any]]) -> None:
            inputs["candidate"]["exact_certificate"]["exact_quartic_bound"]["constant"] = "1/168"

        result = self._assert_forgery("constant 1/168", forge_constant, "sm_full_homogeneous_quartic_BFB_exact")
        self.assertIs(result["g5_bfb_binding"]["certified"], False)
        self.assertIs(result["g5_bfb_binding"]["certified_on_coupling_vector"], False)
        self.assertEqual(result["g5_bfb_binding"]["quartic_bound_constant"], "1/168")
        # A drifted alpha weight is caught by the exact recomputation even with the recorded constant intact.
        inputs = self.inputs()
        inputs["candidate"]["exact_certificate"]["exact_quartic_bound"]["coefficients_alpha"]["N_H"] = "1"
        result = self.evaluate(inputs)
        self.assertIs(result["science_criteria"]["sm_full_homogeneous_quartic_BFB_exact"], False)
        self.assertIs(sm_track.g5_bfb_binding(inputs)["certified"], False)

    # ------------------------------------------------------------------
    # Loading, determinism, caveats, CLI.
    # ------------------------------------------------------------------

    def test_load_inputs_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "bad.json").write_text("{not json", encoding="utf-8")
            (root / "list.json").write_text("[1, 2]", encoding="utf-8")
            (root / "empty.json").write_text("{}", encoding="utf-8")
            (root / "binary.json").write_bytes(b"\xff\xfe\x00")
            paths = {
                "candidate": root / "missing.json",
                "equality_set": str(root / "bad.json"),
                "exact_hessian": root / "list.json",
                "sigma_hypercharge": root / "empty.json",
            }
            loaded = sm_track.load_inputs(paths)
            self.assertEqual(loaded, {key: {} for key in sm_track.INPUT_FILES})
            self.assertEqual(sm_track.load_inputs({"candidate": root / "binary.json"})["candidate"], {})
            result = self.evaluate(loaded)
            self.assertIs(result["closed"], False)
            self.assertEqual(result["missing_inputs"], list(sm_track.INPUT_FILES.values()))
            # A valid path is read; unnamed keys fall back to the committed artifacts.
            (root / "sigma.json").write_text(json.dumps(self.base["sigma_hypercharge"]), encoding="utf-8")
            partial = sm_track.load_inputs({"sigma_hypercharge": root / "sigma.json"})
            self.assertEqual(partial, self.base)

    def test_evaluation_is_deterministic_and_json_native(self) -> None:
        for prerequisites in (ALL, None):
            first = self.evaluate(self.inputs(), prerequisites)
            second = self.evaluate(self.inputs(), prerequisites)
            self.assertEqual(first, second)
            self.assertEqual(json.loads(json.dumps(first)), first)
            self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))

    def test_downstream_caveats_stay_unresolved_without_g4(self) -> None:
        inputs = self.inputs()
        for name in sm_track.MODEL_LEVEL_FLAGS:
            inputs["candidate"]["flags"][name] = True
        inputs["candidate"]["checks"]["light_doublet_is_equal_5_5bar_mixture"] = False
        result = self.evaluate(inputs)
        resolved = {row["id"]: row["resolved"] for row in result["downstream_caveats"]}
        self.assertIs(resolved.pop("zero_modes_and_ranks_at_witness"), False)
        self.assertTrue(all(value is True for value in resolved.values()), resolved)
        self.assertIs(result["downstream_caveats_resolved"], False)
        # A non-bool evidence value never resolves a caveat.
        inputs["candidate"]["flags"]["higgs_mass_compatible"] = "true"
        rows = {row["id"]: row for row in self.evaluate(inputs)["downstream_caveats"]}
        self.assertIs(rows["higgs_quartic_matching"]["resolved"], False)
        self.assertEqual(rows["higgs_quartic_matching"]["evidence"]["value"], "true")

    def test_main_prints_the_unevaluated_track(self) -> None:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = sm_track.main([])
        printed = json.loads(buffer.getvalue())
        self.assertEqual(printed, sm_track.evaluate_sm_track())
        self.assertIs(printed["prerequisites_evaluated"], False)
        self.assertIs(printed["closed"], False)
        # Healthy committed inputs: exit 0 although the prerequisite-gated
        # science entry is False without the ledger.
        self.assertIs(printed["science_criteria"]["G1_G2_exact_scoped_calculations_complete"], False)
        self.assertEqual(code, 0)

    def test_main_exits_1_on_a_forged_input(self) -> None:
        forged = self.inputs()
        forged["candidate"]["n_failed"] = False
        original = sm_track.load_inputs
        sm_track.load_inputs = lambda paths=None: copy.deepcopy(forged)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                code = sm_track.main([])
        finally:
            sm_track.load_inputs = original
        self.assertEqual(code, 1)
        forged = self.inputs()
        forged["exact_hessian"]["eps_family"]["final_acceptance_test"]["required_statement"] = "forged"
        sm_track.load_inputs = lambda paths=None: copy.deepcopy(forged)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                code = sm_track.main([])
        finally:
            sm_track.load_inputs = original
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
