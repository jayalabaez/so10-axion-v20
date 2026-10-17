#!/usr/bin/env python3
"""Tests for the G1 contract-truncation scope record (v20; user decision U5; status-neutral, no gate change).

setUpClass computes the sections once from the committed inputs (model file, G8 flavour no-go JSON, G8
structural-obstruction JSON, G1 symmetry-census JSON, the repository PQ table and the live G8 contract parser) and
compares the assembled report with the committed artifact (everything except runtime_seconds must match exactly; there
are no float leaves).  The content tests pin the census, the Z17 table, the U(1) kernels and generators, the PQ charges
and anomaly, the integer-lattice certificate table, the vectorlike-sector membership and the G8 dimension-4 coverage.
The fail-closed mutation tests change one input each (a model-file charge, phase or LagHC line, a forged or malformed
committed JSON, a wrong PQ table, a perturbed certificate, a dropped check, a forced never-true flag, the live G8
cross-check switched off) and require the named check to fail, the status to drop to INCOMPLETE, every claimed flag to
be False and main --write to refuse without writing.
"""
from __future__ import annotations

import contextlib
import copy
import io
import json
import tempfile
import time
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

import g1_contract_truncation_scope_v20 as truncation

TIMING_KEYS = {"runtime_seconds"}
RUNTIME_BUDGET_SECONDS = 60.0
COMMITTED_RUNTIME_LIMIT_SECONDS = 30.0
EXPECTED_STATUS = "G1_CONTRACT_TRUNCATION_SCOPE__26_ALLOWED_10_DECLARED_16_UNDECLARED__EXACT__NO_GATE_CHANGE"
EXPECTED_INCOMPLETE = "G1_CONTRACT_TRUNCATION_SCOPE_INCOMPLETE__NO_GATE_CHANGE"
EXPECTED_OVERALL = "DECLARED_CONTRACT_IS_A_SYMMETRY_UNPROTECTED_TRUNCATION_EXACT__RADIATIVE_GENERATION_ARGUED_NOT_COMPUTED"
EXPECTED_OPEN = "G1_CONTRACT_TRUNCATION_SCOPE_NOT_ESTABLISHED"
EXPECTED_N_CHECKS = 37
EXPECTED_SECTION_COUNTS = {"model": 3, "z17": 1, "census": 7, "kernel": 7, "pq": 6, "lattice": 3, "sector": 3, "cross": 6, "scope": 1}
TRUE_FLAGS = (
    "declared_lagrangian_is_a_truncation_exact",
    "undeclared_couplings_unprotected_by_any_U1_exact",
    "undeclared_couplings_unprotected_by_any_multiplet_diagonal_phase_symmetry_exact",
    "all_allowed_couplings_PQ_neutral_exact",
    "F_P_R_charge_degenerate_exact",
    "g8_dimension4_analysis_covers_all_allowed_couplings",
    "truncation_not_removable_by_field_redefinitions_exact",
    "evidence_only",
)
REDEFINITION_CHECK = "census.undeclared_48_real_dimensions_exceed_mixing_field_redefinitions_25"
NEVER_TRUE = (
    "G1_reopened",
    "gate_status_changed",
    "couplings_added_to_contract",
    "radiative_generation_computed",
    "one_loop_generation_claimed_exact",
    "rg_closure_modulo_field_redefinitions_analysed",
    "falsifies_so10_contract",
    "changes_g8_flavour_conclusion",
)
EXPECTED_DECLARED = [
    "Delta126bar.F.F",
    "H10.F.F",
    "H10.F.P",
    "H10.F.R",
    "Phi17.R.Rbar",
    "S.Q.Rbar",
    "S.SpecS.SpecB",
    "conj[Phi17].P.Pbar",
    "conj[Phi17].Q.Qbar",
    "conj[S].F.Qbar",
]
EXPECTED_UNDECLARED = [
    "Delta126bar.F.P",
    "Delta126bar.F.R",
    "Delta126bar.P.P",
    "Delta126bar.P.R",
    "Delta126bar.R.R",
    "H10.P.P",
    "H10.P.R",
    "H10.R.R",
    "Phi17.F.Rbar",
    "Phi17.P.Rbar",
    "conj[Delta126bar].Pbar.Rbar",
    "conj[H10].Pbar.Rbar",
    "conj[Phi17].F.Pbar",
    "conj[Phi17].R.Pbar",
    "conj[S].P.Qbar",
    "conj[S].R.Qbar",
]
EXPECTED_CLASSES = {"16.16": 8, "16.16bar": 6, "16bar.16bar": 2}
EXPECTED_F_MIXINGS = ["Phi17.F.Rbar", "conj[Phi17].F.Pbar"]
# Spec section 1 item 7: minimal-L1 integer certificates (coefficient: multiplicity; negative = complex conjugate).
EXPECTED_CERTIFICATES = {
    "Delta126bar.F.P": ({"Y10": -1, "Y126": 1, "lambdaP": 1}, 3),
    "Delta126bar.F.R": ({"Y10": -1, "Y126": 1, "lambdaR": 1}, 3),
    "Delta126bar.P.P": ({"Y10": -2, "Y126": 1, "lambdaP": 2}, 5),
    "Delta126bar.P.R": ({"Y10": -2, "Y126": 1, "lambdaP": 1, "lambdaR": 1}, 5),
    "Delta126bar.R.R": ({"Y10": -2, "Y126": 1, "lambdaR": 2}, 5),
    "H10.P.P": ({"Y10": -1, "lambdaP": 2}, 3),
    "H10.P.R": ({"Y10": -1, "lambdaP": 1, "lambdaR": 1}, 3),
    "H10.R.R": ({"Y10": -1, "lambdaR": 2}, 3),
    "Phi17.F.Rbar": ({"Y10": 1, "yR": 1, "lambdaR": -1}, 3),
    "Phi17.P.Rbar": ({"yR": 1, "lambdaP": 1, "lambdaR": -1}, 3),
    "conj[Delta126bar].Pbar.Rbar": ({"Y10": 2, "Y126": -1, "yP": 1, "yR": 1, "lambdaP": -1, "lambdaR": -1}, 7),
    "conj[H10].Pbar.Rbar": ({"Y10": 1, "yP": 1, "yR": 1, "lambdaP": -1, "lambdaR": -1}, 5),
    "conj[Phi17].F.Pbar": ({"Y10": 1, "yP": 1, "lambdaP": -1}, 3),
    "conj[Phi17].R.Pbar": ({"yP": 1, "lambdaP": -1, "lambdaR": 1}, 3),
    "conj[S].P.Qbar": ({"Y10": -1, "lambdaP": 1, "lambdaQB": 1}, 3),
    "conj[S].R.Qbar": ({"yQ": 1, "yR": 1, "lambdaQR": -1}, 3),
}
EXPECTED_DIFFERENCES = {"P-F": ({"Y10": -1, "lambdaP": 1}, 2), "R-F": ({"Y10": -1, "lambdaR": 1}, 2)}
EXPECTED_TIES = {"Phi17.F.Rbar": 2, "conj[Delta126bar].Pbar.Rbar": 2, "conj[H10].Pbar.Rbar": 2, "conj[S].R.Qbar": 2}
EXPECTED_RELATION = {"Y10": 1, "yQ": 1, "yR": 1, "lambdaR": -1, "lambdaQB": -1, "lambdaQR": -1}
EXPECTED_KERNEL_DIMENSIONS = {
    "declared_LagHC": 3,
    "declared_LagHC_plus_G1_scalar_links": 3,
    "allowed_26_plus_kappaH": 3,
    "allowed_26_plus_kappaH_plus_G1_scalar_links": 3,
    "allowed_26_without_scalar_links": 4,
}
EXPECTED_UNKNOWNS = ["Phi210", "Delta126bar", "H10", "S", "Phi17", "F", "P", "R", "SpecS", "SpecB", "Q", "Pbar", "Qbar", "Rbar"]
EXPECTED_X = {"Phi210": 0, "Delta126bar": -2, "H10": -2, "S": 4, "Phi17": 17, "F": 1, "P": 1, "R": 1, "SpecS": 2,
              "SpecB": -6, "Q": 14, "Pbar": 16, "Qbar": 3, "Rbar": -18}
EXPECTED_Z17 = {"Phi210": 0, "Delta126bar": 15, "H10": 15, "S": 4, "Phi17": 0, "F": 1, "P": 1, "R": 1, "SpecS": 2,
                "SpecB": 11, "Q": 14, "Pbar": 16, "Qbar": 3, "Rbar": 16}
EXPECTED_PQ = {"Phi210": 0, "Delta126bar": -2, "H10": -2, "S": 4, "Phi17": 0, "F": 1, "P": 1, "R": 1, "SpecS": 2,
               "SpecB": -6, "Q": -3, "Pbar": -1, "Qbar": 3, "Rbar": -1}
EXPECTED_N17 = {"Phi210": 0, "Delta126bar": 0, "H10": 0, "S": 0, "Phi17": 1, "F": 0, "P": 0, "R": 0, "SpecS": 0,
                "SpecB": 0, "Q": 1, "Pbar": 1, "Qbar": 0, "Rbar": -1}
EXPECTED_ANOMALY = {"T_16": 2, "N_X": 0, "N_PQ": -34, "N_spec": 0, "N17": 2}
EXPECTED_VERDICT = (
    "EXACT (37 checks): the SARAH-attested contract is a truncation. SO(10) x U(1)_X x Z17 (Z17 = X mod 17 for every "
    "field) allows 26 renormalizable fermion bilinears; 10 are declared and 16 are not (Delta126bar.F.P, "
    "Delta126bar.F.R, Delta126bar.P.P, Delta126bar.P.R, Delta126bar.R.R, H10.P.P, H10.P.R, H10.R.R, Phi17.F.Rbar, "
    "Phi17.P.Rbar, conj[Delta126bar].Pbar.Rbar, conj[H10].Pbar.Rbar, conj[Phi17].F.Pbar, conj[Phi17].R.Pbar, "
    "conj[S].P.Qbar, conj[S].R.Qbar; labels in the model file's field basis). The truncation is not a basis choice: "
    "the undeclared couplings span 48 real generation-expanded dimensions, more than the 25 of U(5) on the five "
    "X = 1 sixteens, the only field-redefinition factor that mixes distinct multiplets. The declared terms and the "
    "full allowed set (with the scalar links) have the same 3-dimensional U(1) kernel span{X, PQ, Nspec}; every omitted coupling is PQ neutral and an integer combination of "
    "declared terms, so no U(1) and no multiplet-diagonal phase symmetry of the declared Lagrangian protects it; F, P and "
    "R carry identical charges. Each omitted coupling involves P, R, Pbar, Rbar or Qbar; Phi17.F.Rbar and "
    "conj[Phi17].F.Pbar are F-Rbar and F-Pbar mass mixings. Radiative generation is argued, not computed. The G8 "
    "dimension-4 analysis already includes all 26 couplings. Status-neutral: G1 stays CLOSED as the attestation of a "
    "truncation; no coupling is added."
)
RBAR_ROW = "{Rbar,   1, rbar16,  -16, -18, Exp[2*Pi*I*16/17]};"
Q_ROW = "{Q,      1, q16,      16,  14, Exp[2*Pi*I*14/17]};"
SPECS_ROW = "{SpecS,  5, s16,      16,   2, Exp[2*Pi*I*2/17]};"
KAPPA_LINE = "  + kappaH H10.H10.S\n"


def _without_timing(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _without_timing(item) for key, item in value.items() if key not in TIMING_KEYS}
    if isinstance(value, list):
        return [_without_timing(item) for item in value]
    return value


class G1ContractTruncationScopeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.committed = json.loads(truncation.OUT_JSON.read_text(encoding="utf-8"))
        started = time.time()
        cls.sections = truncation.compute_sections()
        cls.report = truncation.assemble_report(cls.sections, started=started)
        cls.fresh = truncation.json_roundtrip(cls.report)
        cls.setup_seconds = time.time() - started
        cls.model_text = truncation.MODEL_FILE.read_text(encoding="utf-8").replace("\r\n", "\n")
        cls.g8_committed = json.loads(truncation.G8_JSON.read_text(encoding="utf-8"))
        cls.structural_committed = json.loads(truncation.STRUCTURAL_JSON.read_text(encoding="utf-8"))
        cls.g1_census_committed = json.loads(truncation.G1_CENSUS_JSON.read_text(encoding="utf-8"))

    # ------------------------------------------------------------------ helpers

    def _assert_fails_closed(self, report: dict[str, Any], *checks: str) -> None:
        for check in checks:
            self.assertIs(report["checks"].get(check), False, check)
            self.assertIn(check, report["failures"])
        self.assertEqual(report["status"], EXPECTED_INCOMPLETE)
        self.assertEqual(report["overall_state"], EXPECTED_OPEN)
        self.assertGreater(report["n_failed"], 0)
        self.assertFalse(truncation.report_passes(report))
        for name in TRUE_FLAGS:
            self.assertIs(report["flags"][name], False, name)
        self.assertTrue(report["verdict"].startswith("FAIL-CLOSED"))
        self._assert_write_refused(report)

    def _assert_write_refused(self, report: dict[str, Any]) -> None:
        with tempfile.TemporaryDirectory() as directory:
            out_json = Path(directory) / "refused.json"
            out_md = Path(directory) / "refused.md"
            with mock.patch.object(truncation, "OUT_JSON", out_json), mock.patch.object(truncation, "OUT_MD", out_md), \
                    mock.patch.object(truncation, "build_report", return_value=report), contextlib.redirect_stdout(io.StringIO()):
                code = truncation.main(["--write"])
            self.assertNotEqual(code, 0)
            self.assertFalse(out_json.exists())
            self.assertFalse(out_md.exists())

    def _model_report(self, old: str, new: str) -> dict[str, Any]:
        self.assertEqual(self.model_text.count(old), 1, old)
        return truncation.assemble_report(truncation.compute_sections(model_text=self.model_text.replace(old, new)))

    # ------------------------------------------------------------------ status, counts, flags, artifact

    def test_status_checks_and_flags(self) -> None:
        for report in (self.committed, self.fresh):
            self.assertEqual(report["module"], "g1_contract_truncation_scope_v20")
            self.assertEqual(report["model_contract_id"], "gauged_u1x_phi17_v20")
            self.assertEqual(report["gate"], "G1")
            self.assertEqual(report["status"], EXPECTED_STATUS)
            self.assertEqual(report["overall_state"], EXPECTED_OVERALL)
            self.assertEqual(report["n_failed"], 0, report["failures"])
            self.assertEqual(report["failures"], [])
            self.assertEqual(report["n_checks"], EXPECTED_N_CHECKS)
            self.assertEqual(report["expected_n_checks"], EXPECTED_N_CHECKS)
            self.assertEqual(sorted(report["checks"]), sorted(truncation.EXPECTED_CHECK_KEYS))
            self.assertTrue(all(value is True for value in report["checks"].values()))
            counts: dict[str, int] = {}
            for key in report["checks"]:
                counts[key.split(".")[0]] = counts.get(key.split(".")[0], 0) + 1
            self.assertEqual(counts, EXPECTED_SECTION_COUNTS)
            for name in TRUE_FLAGS:
                self.assertIs(report["flags"][name], True, name)
            for name in NEVER_TRUE:
                self.assertIs(report["flags"][name], False, name)
            self.assertEqual(set(report["flags"]), set(TRUE_FLAGS) | set(NEVER_TRUE))
            self.assertEqual(set(report["labels"]), {"EXACT", "BOUND", "ARGUMENT"})
        self.assertEqual(list(self.report["checks"]), list(truncation.EXPECTED_CHECK_KEYS))
        self.assertEqual(len(truncation.EXPECTED_CHECK_KEYS), EXPECTED_N_CHECKS)
        self.assertEqual(truncation.STATUS_RECORDED, EXPECTED_STATUS)
        self.assertEqual(truncation.STATUS_INCOMPLETE, EXPECTED_INCOMPLETE)
        self.assertEqual(truncation.OVERALL_STATE_RECORDED, EXPECTED_OVERALL)
        self.assertEqual(truncation.OVERALL_STATE_OPEN, EXPECTED_OPEN)
        self.assertEqual(truncation.EXPECTED_N_CHECKS, EXPECTED_N_CHECKS)
        self.assertEqual(truncation.EXPECTED_SECTION_COUNTS, EXPECTED_SECTION_COUNTS)
        self.assertEqual(tuple(truncation.NEVER_TRUE_FLAGS), NEVER_TRUE)
        self.assertEqual(tuple(truncation.TRUE_FLAGS), TRUE_FLAGS)
        self.assertEqual(truncation.EXPECTED_KERNEL_DIMENSIONS, EXPECTED_KERNEL_DIMENSIONS)
        self.assertEqual(truncation.EXPECTED_DECLARED_RELATION, EXPECTED_RELATION)
        self.assertEqual(list(truncation.EXPECTED_UNDECLARED_LABELS), EXPECTED_UNDECLARED)
        self.assertEqual(list(truncation.EXPECTED_F_MASS_MIXINGS), EXPECTED_F_MIXINGS)
        self.assertTrue(truncation.report_passes(self.report))

    def test_committed_artifact_matches_fresh_report(self) -> None:
        self.assertEqual(_without_timing(self.committed), _without_timing(self.fresh))

    def test_committed_markdown_regenerates(self) -> None:
        expected = truncation._markdown(self.committed).replace("\r\n", "\n")
        self.assertEqual(truncation.OUT_MD.read_text(encoding="utf-8").replace("\r\n", "\n"), expected)

    def test_runtime_budget(self) -> None:
        self.assertLess(self.setup_seconds, RUNTIME_BUDGET_SECONDS)
        self.assertIsInstance(self.committed["runtime_seconds"], float)
        self.assertLess(self.committed["runtime_seconds"], COMMITTED_RUNTIME_LIMIT_SECONDS)

    def test_write_report_writes_a_passing_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            out_json = Path(directory) / "ok.json"
            out_md = Path(directory) / "ok.md"
            with mock.patch.object(truncation, "OUT_JSON", out_json), mock.patch.object(truncation, "OUT_MD", out_md):
                self.assertTrue(truncation.write_report(self.report))
            self.assertEqual(_without_timing(json.loads(out_json.read_text(encoding="utf-8"))), _without_timing(self.fresh))
            self.assertEqual(out_md.read_text(encoding="utf-8").replace("\r\n", "\n"), truncation._markdown(self.fresh))

    # ------------------------------------------------------------------ exact content

    def test_model_and_z17(self) -> None:
        model = self.fresh["model"]
        self.assertEqual(model["file"], "models/SO10Z17AxionV20.m")
        self.assertEqual(sorted(model["fields"]), sorted(EXPECTED_UNKNOWNS))
        self.assertEqual(list(self.report["model"]["fields"]), EXPECTED_UNKNOWNS)  # model-file order before sort_keys
        self.assertEqual({name: row["X"] for name, row in model["fields"].items()}, EXPECTED_X)
        self.assertEqual({name: row["Z17"] for name, row in model["fields"].items()}, EXPECTED_Z17)
        self.assertEqual([name for name, row in model["fields"].items() if row["real"]], ["Phi210"])
        self.assertEqual({name: row["generations"] for name, row in model["fields"].items() if row["generations"] != 1},
                         {"F": 3, "SpecS": 5, "SpecB": 5})
        terms = model["declared_LagHC_terms"]
        self.assertEqual([row["coefficient"] for row in terms],
                         ["Y10", "Y126", "yP", "yQ", "yR", "ys", "lambdaP", "lambdaR", "lambdaQB", "lambdaQR", "kappaH"])
        self.assertEqual([row["kind"] for row in terms], ["fermion_bilinear"] * 10 + ["scalar_link"])
        self.assertEqual(terms[-1]["monomial"], "H10.H10.S")
        self.assertTrue(all(row["X_sum"] == 0 and row["Z17_sum_mod_17"] == 0 for row in terms + model["declared_LagNoHC_terms"]))
        self.assertEqual(len(model["declared_LagNoHC_terms"]), 8)
        z17 = self.fresh["z17"]
        self.assertIs(z17["Z17_equals_X_mod_17_for_every_field"], True)
        self.assertEqual(z17["X_allowed_couplings_removed_by_Z17"], [])
        for name, row in z17["per_field"].items():
            self.assertEqual(row["Z17"], EXPECTED_X[name] % 17, name)
        self.assertEqual(z17["statement"], truncation.Z17_STATEMENT)

    def test_census_lists_and_counts(self) -> None:
        census = self.fresh["census"]
        self.assertEqual(census["allowed_count"], 26)
        self.assertEqual(sorted(row["coupling"] for row in census["allowed"]), sorted(EXPECTED_DECLARED + EXPECTED_UNDECLARED))
        self.assertEqual(census["declared"], EXPECTED_DECLARED)
        self.assertEqual(census["declared_count"], 10)
        self.assertEqual(census["undeclared"], EXPECTED_UNDECLARED)
        self.assertEqual(census["undeclared_count"], 16)
        self.assertEqual(census["generation_expanded_count"], 74)
        self.assertEqual(census["bare_16_16bar_masses"], [])
        self.assertEqual(census["Phi210_couplings"], [])
        self.assertEqual(census["declared_bilinears_outside_allowed_set"], [])
        self.assertEqual(census["undeclared_class_counts"], EXPECTED_CLASSES)
        coefficients = {row["coupling"]: row["declared_coefficient"] for row in census["allowed"] if row["declared"]}
        self.assertEqual(coefficients, {
            "H10.F.F": "Y10", "Delta126bar.F.F": "Y126", "conj[Phi17].P.Pbar": "yP", "conj[Phi17].Q.Qbar": "yQ",
            "Phi17.R.Rbar": "yR", "S.SpecS.SpecB": "ys", "H10.F.P": "lambdaP", "H10.F.R": "lambdaR",
            "conj[S].F.Qbar": "lambdaQB", "S.Q.Rbar": "lambdaQR",
        })
        self.assertTrue(all(row["declared_coefficient"] is None for row in census["allowed"] if not row["declared"]))

    def test_field_redefinitions_cannot_remove_the_truncation(self) -> None:
        # Independent recount: generation-expanded undeclared couplings from the label list and the generation table,
        # and the field-redefinition factor that mixes distinct multiplets (U(5) on F x3, P, R).
        generations = {"F": 3}
        undeclared = 0
        for label in EXPECTED_UNDECLARED:
            first, second = label.split(".")[1:]
            g1, g2 = generations.get(first, 1), generations.get(second, 1)
            undeclared += g1 * (g1 + 1) // 2 if first == second else g1 * g2
        self.assertEqual(undeclared, 24)
        redefinitions = self.fresh["census"]["field_redefinitions"]
        self.assertEqual(redefinitions["label"], "EXACT")
        self.assertEqual(redefinitions["undeclared_complex_dimension"], undeclared)
        self.assertEqual(redefinitions["declared_complex_dimension"], 74 - undeclared)
        self.assertEqual(
            (redefinitions["declared_real_dimension"], redefinitions["undeclared_real_dimension"],
             redefinitions["all_couplings_real_dimension"]),
            (100, 48, 148),
        )
        self.assertEqual(list(redefinitions["mixing_classes"]), ["F.P.R"])
        mixing = redefinitions["mixing_classes"]["F.P.R"]
        self.assertEqual(mixing["fields"], ["F", "P", "R"])
        self.assertEqual((mixing["kind"], mixing["so10"], mixing["X"]), ("fermion", "16", 1))
        self.assertEqual((mixing["total_generations"], mixing["group"], mixing["real_dimension"]), (5, "U(5)", 25))
        self.assertEqual(redefinitions["mixing_redefinition_real_dimension"], 25)
        self.assertEqual(redefinitions["declared_orbit_real_dimension_bound"], 125)
        self.assertGreater(2 * undeclared, 5 * 5)
        self.assertEqual(redefinitions["statement"], truncation.FIELD_REDEFINITION_STATEMENT)
        self.assertIn("refers to the model file's field basis", redefinitions["statement"])
        self.assertIn("linear, kinetic-term-preserving", redefinitions["statement"])
        self.assertIs(self.fresh["checks"][REDEFINITION_CHECK], True)
        self.assertIs(self.fresh["flags"]["truncation_not_removable_by_field_redefinitions_exact"], True)
        # RG closure modulo field redefinitions stays unanalysed.
        self.assertIs(self.fresh["flags"]["rg_closure_modulo_field_redefinitions_analysed"], False)

    def test_kernel_dimensions_generators_and_degeneracy(self) -> None:
        kernel = self.fresh["kernel"]
        self.assertEqual(kernel["unknowns"], EXPECTED_UNKNOWNS)
        self.assertEqual(kernel["dimensions"], EXPECTED_KERNEL_DIMENSIONS)
        self.assertEqual(kernel["equals_span_X_PQ_Nspec"], {name: True for name in truncation.DIMENSION_3_KERNELS})
        self.assertEqual(kernel["generators"]["X"], EXPECTED_X)
        self.assertEqual(kernel["generators"]["PQ"], EXPECTED_PQ)
        self.assertEqual(kernel["generators"]["N17"], EXPECTED_N17)
        self.assertEqual({k: v for k, v in kernel["generators"]["N_spec"].items() if v}, {"SpecS": 1, "SpecB": -1})
        for name in EXPECTED_UNKNOWNS:
            self.assertEqual(EXPECTED_X[name], EXPECTED_PQ[name] + 17 * EXPECTED_N17[name], name)
        self.assertIs(kernel["F_P_R_identical"], True)
        self.assertEqual(kernel["scalar_links"]["kappaH"], [0, 0, 2, 1] + [0] * 10)
        self.assertEqual(len(kernel["scalar_links"]["G1_census_links"]), 20)
        self.assertEqual(kernel["statement"], truncation.KERNEL_STATEMENT)

    def test_pq_charges_and_anomaly(self) -> None:
        pq = self.fresh["pq"]
        self.assertEqual(pq["charges"], EXPECTED_PQ)
        self.assertEqual(pq["anomaly"], EXPECTED_ANOMALY)
        self.assertEqual(len(pq["per_coupling"]), 26)
        for label, row in pq["per_coupling"].items():
            self.assertEqual((row["X_sum"], row["PQ_sum"], row["N_spec_sum"], row["N17_sum"], row["Z17_sum_mod_17"]),
                             (0, 0, 0, 0, 0), label)
        self.assertIs(pq["all_allowed_PQ_neutral"], True)
        self.assertIs(pq["all_undeclared_PQ_neutral"], True)
        self.assertIs(pq["scalar_monomials_X_neutral_implies_PQ_neutral"], True)
        self.assertEqual(pq["scalar_monomial_census"]["count_tuples"], 715)
        self.assertEqual(pq["scalar_monomial_census"]["PQ_violations"], [])
        self.assertEqual(pq["statement"], truncation.PQ_STATEMENT)

    def test_lattice_relation_and_certificates(self) -> None:
        lattice = self.fresh["lattice"]
        self.assertEqual(lattice["declared_rank"], 10)
        self.assertEqual(lattice["declared_relation"], EXPECTED_RELATION)
        self.assertEqual(set(lattice["certificates"]), set(EXPECTED_UNDECLARED))
        for label, (combination, degree) in EXPECTED_CERTIFICATES.items():
            self.assertEqual(lattice["certificates"][label]["combination"], combination, label)
            self.assertEqual(lattice["certificates"][label]["degree_l1"], degree, label)
        for label, (combination, degree) in EXPECTED_DIFFERENCES.items():
            self.assertEqual(lattice["difference_certificates"][label]["combination"], combination, label)
            self.assertEqual(lattice["difference_certificates"][label]["degree_l1"], degree, label)
        self.assertIs(lattice["scan"]["every_scan_covers_its_breakpoints"], True)
        self.assertEqual(lattice["scan"]["tied_minimal_l1_solutions"], EXPECTED_TIES)
        self.assertEqual(lattice["statement"], truncation.LATTICE_STATEMENT)
        self.assertEqual(lattice["spurion_note"], truncation.LATTICE_SPURION_NOTE)
        # Independent integer re-verification of the pinned table from the recorded charge vectors.
        order = self.fresh["kernel"]["unknowns"]
        declared = {row["coefficient"]: truncation._vector(order, truncation._monomial_factors(row["monomial"]))
                    for row in self.fresh["model"]["declared_LagHC_terms"]}
        relation = [0] * len(order)
        for name, value in EXPECTED_RELATION.items():
            relation = [a + value * b for a, b in zip(relation, declared[name])]
        self.assertEqual(relation, [0] * len(order))
        rows = {row["coupling"]: row for row in self.fresh["census"]["allowed"]}
        for label, (combination, _degree) in EXPECTED_CERTIFICATES.items():
            total = [0] * len(order)
            for name, value in combination.items():
                total = [a + value * b for a, b in zip(total, declared[name])]
            self.assertEqual(total, truncation._vector(order, truncation._coupling_factors(rows[label])), label)

    def test_sector_membership(self) -> None:
        sector = self.fresh["sector"]
        self.assertEqual(sector["vectorlike_sector_fields"], ["P", "R", "Pbar", "Rbar", "Qbar"])
        self.assertEqual(sorted(sector["per_undeclared"]), EXPECTED_UNDECLARED)
        self.assertTrue(all(row["vectorlike_sector_fields"] for row in sector["per_undeclared"].values()))
        self.assertEqual(sector["F_16bar_mass_mixings"], EXPECTED_F_MIXINGS)
        self.assertEqual(sorted(label for label, row in sector["per_undeclared"].items() if row["is_F_16bar_mass_mixing"]),
                         EXPECTED_F_MIXINGS)
        self.assertEqual(sector["per_undeclared"]["Phi17.F.Rbar"]["vectorlike_sector_fields"], ["Rbar"])
        self.assertEqual(sector["per_undeclared"]["conj[Phi17].F.Pbar"]["vectorlike_sector_fields"], ["Pbar"])
        for row in self.fresh["census"]["allowed"]:
            if not row["declared"]:
                self.assertFalse({"Q", "SpecS", "SpecB"} & set(row["fermions"]), row["coupling"])
        self.assertEqual(sector["statement"], truncation.SECTOR_STATEMENT)

    def test_cross_checks_and_g8_coverage(self) -> None:
        cross = self.fresh["cross_checks"]
        self.assertEqual(cross["label"], "BOUND")
        contract = self.g8_committed["contract"]
        self.assertEqual(contract["allowed_but_undeclared"], EXPECTED_UNDECLARED)
        self.assertEqual(contract["H10_yukawas"], ["H10.F.F", "H10.F.P", "H10.F.R", "H10.P.P", "H10.P.R", "H10.R.R"])
        self.assertEqual(len(contract["Delta126bar_yukawas"]), 6)
        self.assertEqual(len(contract["vectorlike_mass_couplings"]), 12)
        self.assertEqual(contract["sixteenbar_pair_couplings"], ["conj[Delta126bar].Pbar.Rbar", "conj[H10].Pbar.Rbar"])
        union = (contract["H10_yukawas"] + contract["Delta126bar_yukawas"] + contract["vectorlike_mass_couplings"]
                 + contract["sixteenbar_pair_couplings"])
        self.assertEqual(sorted(union), sorted(EXPECTED_DECLARED + EXPECTED_UNDECLARED))
        self.assertIs(cross["g8_json"]["dimension4"]["union_is_the_allowed_set"], True)
        self.assertIs(cross["g8_json"]["dimension4"]["vectorlike_rank_8_on_all_allowed_pairs"], True)
        self.assertIs(cross["g8_json"]["model_sha256_matches"], True)
        self.assertIs(cross["g8_live_contract_section"]["computed"], True)
        self.assertIs(cross["structural_json"]["census_matches"], True)
        self.assertIs(cross["g1_census_json"]["bound"], True)
        self.assertEqual(cross["g1_census_json"]["nontrivial_links"], 20)
        self.assertEqual(self.fresh["g8_coverage"], {"label": "BOUND", "statement": truncation.G8_COVERAGE_STATEMENT})

    def test_texts_scope_and_verdict(self) -> None:
        self.assertEqual(self.fresh["verdict"], EXPECTED_VERDICT)
        radiative = self.fresh["radiative"]
        self.assertEqual(radiative["label"], "ARGUMENT (not computed)")
        self.assertEqual(radiative["statement"], truncation.RADIATIVE_STATEMENT)
        self.assertIn("(Y Y^dagger Y)_PP \u2283 lambda_P Y10^* lambda_P", radiative["one_loop_example"])
        self.assertIn("basis dependent", radiative["one_loop_example"])
        self.assertEqual(len(radiative["not_claimed"]), 4)
        self.assertEqual(set(self.fresh["scope"]), {"claimed", "argued_not_computed", "not_claimed"})
        self.assertIn("no coupling is added (adding them would be a new contract)", self.fresh["scope"]["not_claimed"])
        self.assertIn("no gate status changes; G1 stays CLOSED and is scoped as the attestation of a truncation",
                      self.fresh["scope"]["not_claimed"])
        texts = json.dumps(self.fresh) + truncation.OUT_MD.read_text(encoding="utf-8") + (truncation.__doc__ or "")
        self.assertNotIn("v21", texts)
        self.assertNotIn("FAILED", texts)
        self.assertNotIn("NOT_CLOSABLE", texts)

    # ------------------------------------------------------------------ fail-closed mutations

    def test_mutation_1_rbar_charge_breaks_census_and_sha(self) -> None:
        report = self._model_report(RBAR_ROW, "{Rbar,   1, rbar16,  -16, -17, 1};")
        self._assert_fails_closed(report, "census.allowed_26", "census.undeclared_16_exact_list",
                                  "cross.g8_json_model_sha256_matches")

    def test_mutation_2_q_phase_breaks_z17(self) -> None:
        report = self._model_report(Q_ROW, "{Q,      1, q16,      16,  14, Exp[2*Pi*I*13/17]};")
        self._assert_fails_closed(report, "z17.equals_X_mod_17_for_every_field")

    def test_mutation_3_declared_extra_coupling_breaks_census_and_g8_binding(self) -> None:
        report = self._model_report(KAPPA_LINE, KAPPA_LINE + "  + lambdaPP H10.P.P\n")
        self.assertEqual(report["census"]["declared_count"], 11)
        self.assertEqual(report["census"]["undeclared_count"], 15)
        self._assert_fails_closed(report, "census.declared_10_subset_of_allowed", "census.undeclared_16_exact_list",
                                  "cross.g8_json_recorded_and_lists_match")

    def test_mutation_4_without_kappaH_breaks_declared_kernel(self) -> None:
        report = self._model_report(KAPPA_LINE, "")
        self.assertEqual(report["kernel"]["dimensions"]["declared_LagHC"], 4)
        self._assert_fails_closed(report, "kernel.declared_LagHC_dimension_3")

    def test_mutation_5_g8_json_forged_or_malformed(self) -> None:
        check = "cross.g8_json_recorded_and_lists_match"
        removed = copy.deepcopy(self.g8_committed)
        removed["contract"]["allowed_but_undeclared"] = removed["contract"]["allowed_but_undeclared"][1:]
        forged = copy.deepcopy(self.g8_committed)
        forged["status"] = forged["status"] + "_FORGED"
        boolean = copy.deepcopy(self.g8_committed)
        boolean["n_failed"] = False
        for g8_report in (removed, forged, boolean, {}, [], "null"):
            report = truncation.assemble_report(truncation.compute_sections(g8_report=g8_report))
            self._assert_fails_closed(report, check)
        with tempfile.TemporaryDirectory() as directory:
            with mock.patch.object(truncation, "G8_JSON", Path(directory) / "missing.json"):
                report = truncation.assemble_report(truncation.compute_sections())
            self._assert_fails_closed(report, check, "cross.g8_json_model_sha256_matches",
                                      "cross.g8_dimension4_lists_cover_all_allowed_couplings")
            null_file = Path(directory) / "null.json"
            null_file.write_text("null\n", encoding="utf-8")
            with mock.patch.object(truncation, "G8_JSON", null_file):
                report = truncation.assemble_report(truncation.compute_sections())
            self._assert_fails_closed(report, check)

    def test_mutation_6_g8_json_forged_model_sha(self) -> None:
        forged = copy.deepcopy(self.g8_committed)
        sha = forged["contract"]["model_text_sha256"]
        forged["contract"]["model_text_sha256"] = ("0" if sha[0] != "0" else "1") + sha[1:]
        report = truncation.assemble_report(truncation.compute_sections(g8_report=forged))
        self._assert_fails_closed(report, "cross.g8_json_model_sha256_matches")

    def test_mutation_7_g8_json_reduced_h10_list_breaks_coverage(self) -> None:
        reduced = copy.deepcopy(self.g8_committed)
        reduced["contract"]["H10_yukawas"] = ["H10.F.F", "H10.F.P", "H10.F.R"]
        report = truncation.assemble_report(truncation.compute_sections(g8_report=reduced))
        self._assert_fails_closed(report, "cross.g8_dimension4_lists_cover_all_allowed_couplings")

    def test_mutation_8_wrong_pq_table(self) -> None:
        charges = dict(self.fresh["pq"]["charges"])
        charges["Q"] = -2
        report = truncation.assemble_report(truncation.compute_sections(pq_charges=charges))
        self._assert_fails_closed(report, "pq.charges_match_repository_contract", "pq.all_26_allowed_couplings_PQ_neutral")

    def test_mutation_9_perturbed_certificate(self) -> None:
        sections = copy.deepcopy(self.sections)
        sections["lattice"]["certificates"]["H10.P.P"]["combination"]["Y10"] += 1
        report = truncation.assemble_report(sections)
        self._assert_fails_closed(report, "lattice.every_undeclared_is_an_integer_combination_of_declared_terms")
        sections = copy.deepcopy(self.sections)
        sections["lattice"]["difference_certificates"]["R-F"]["combination"]["lambdaR"] = 2
        report = truncation.assemble_report(sections)
        self._assert_fails_closed(report, "lattice.P_minus_F_and_R_minus_F_are_integer_combinations")
        sections = copy.deepcopy(self.sections)
        del sections["lattice"]["certificates"]["conj[S].R.Qbar"]
        report = truncation.assemble_report(sections)
        self._assert_fails_closed(report, "lattice.every_undeclared_is_an_integer_combination_of_declared_terms")

    def test_mutation_10_structural_json_dropped_coupling(self) -> None:
        dropped = copy.deepcopy(self.structural_committed)
        dropped["corollaries"]["field_level_couplings"] = dropped["corollaries"]["field_level_couplings"][:-1]
        report = truncation.assemble_report(truncation.compute_sections(structural_report=dropped))
        self._assert_fails_closed(report, "cross.structural_obstruction_json_census_matches")
        report = truncation.assemble_report(truncation.compute_sections(structural_report={}))
        self._assert_fails_closed(report, "cross.structural_obstruction_json_census_matches")

    def test_mutation_11_g1_census_json_short_or_forged(self) -> None:
        short = copy.deepcopy(self.g1_census_committed)
        short["multidegrees"] = short["multidegrees"][:33]
        forged = copy.deepcopy(self.g1_census_committed)
        forged["status"] = "FORGED"
        for g1_report in (short, forged, {}):
            report = truncation.assemble_report(truncation.compute_sections(g1_census_report=g1_report))
            self._assert_fails_closed(report, "cross.g1_census_json_bound_and_links_neutral")

    def test_mutation_12_check_count_is_enforced(self) -> None:
        fewer = copy.deepcopy(self.sections)
        fewer["sector"]["checks"].pop("exactly_two_F_16bar_mass_mixings")
        report = truncation.assemble_report(fewer)
        self.assertEqual(report["n_checks"], EXPECTED_N_CHECKS - 1)
        self.assertIn(f"check_count_{EXPECTED_N_CHECKS - 1}_expected_{EXPECTED_N_CHECKS}", report["failures"])
        self.assertEqual(report["status"], EXPECTED_INCOMPLETE)
        self.assertFalse(truncation.report_passes(report))
        for name in TRUE_FLAGS:
            self.assertIs(report["flags"][name], False, name)
        self.assertTrue(report["verdict"].startswith("FAIL-CLOSED"))
        self._assert_write_refused(report)
        extra = copy.deepcopy(self.sections)
        extra["sector"]["checks"]["an_unpinned_extra_check"] = True
        report = truncation.assemble_report(extra)
        self.assertEqual(report["n_checks"], EXPECTED_N_CHECKS + 1)
        self.assertIn("check_keys_differ_from_expected", report["failures"])
        self.assertFalse(truncation.report_passes(report))
        self._assert_write_refused(report)
        dropped = copy.deepcopy(self.fresh)
        dropped["checks"].pop("scope.status_neutral_flags")
        self.assertFalse(truncation.report_passes(dropped))

    def test_mutation_13_forced_never_true_flag(self) -> None:
        for name in NEVER_TRUE:
            report = truncation.assemble_report(self.sections, flag_overrides={name: True})
            self.assertIs(report["flags"][name], True, name)
            self._assert_fails_closed(report, "scope.status_neutral_flags")

    def test_mutation_14_live_g8_cross_check_is_mandatory(self) -> None:
        report = truncation.assemble_report(truncation.compute_sections(live_g8=False))
        self.assertEqual(report["census"]["allowed_count"], 26)
        self._assert_fails_closed(report, "cross.g8_live_contract_section_matches")

    def test_mutation_15_enlarged_mixing_class_breaks_the_dimension_count(self) -> None:
        # Giving SpecS the X = 1 charges joins it to the F/P/R class: U(10) (100 real dimensions) exceeds 48.
        report = self._model_report(SPECS_ROW, "{SpecS,  5, s16,      16,   1, Exp[2*Pi*I*1/17]};")
        mixing = report["census"]["field_redefinitions"]["mixing_classes"]
        self.assertEqual(list(mixing), ["F.P.R.SpecS"])
        self.assertEqual(mixing["F.P.R.SpecS"]["real_dimension"], 100)
        self._assert_fails_closed(report, REDEFINITION_CHECK)


if __name__ == "__main__":
    unittest.main()
