#!/usr/bin/env python3
"""Tests for the Route C flavour no-go of the SM Pati-Salam G3 witness branch (G8, v20).

setUpClass builds one fresh report (census, exact Hessians at eight r0 values, spinor algebra, one-loop running,
the five H-linear portals on the full H block with exact Schur data at five r0 values, seesaw scan, and the six
status-neutral v2 lemma sections: the (1,2,2) Clebsch via T15, the SU(5)-Casimir selection rule, |S| independence of
tan beta = 1, the (B-L, T3R) Sigma-balance census to dimension 12 with the PS-invariant remainder, the G3221 s = 1
theorem and the B1a inequality; one to two minutes) and compares it with the committed artifact: exact leaves must
match exactly, the float diagnostics (data comparison, O28 and portal-set repository bounds, eigenvalue-based colour
radii, seesaw scan, the NDA cutoff of the census lemma) only within declared tolerances.  The mutation tests call the
section functions with one changed input each (model text, benchmark coefficients, census rows, doublet vev, data,
repository scales, vectorlike couplings, upstream reports, pinned closed form, portal couplings, triplet couplings,
hypercharge sources, Yukawa content, colour bracket; and for the v2 lemmas: a neutral PS-breaking spurion, a changed
126bar X charge, an SU(2)_R-breaking mixing map, the wrong down-type doublet, an S-coupled binding unit, a symmetric
"antisymmetric" matrix, a (15,2,2) form fed as a (1,2,2) source, and a Sigma vev overlapping e_0 ^ p in the exact O38
form check) and require the corresponding checks to fail closed.  The Route B, Route A, census and s = 1 scope texts
and the renamed v2 flags are pinned, so that no over-broad claim (Route B reduced to a 120_H among all extensions, a
census exhaustive beyond its single-Higgs class, an all-orders statement beyond the H-linear operators) reappears.
"""
from __future__ import annotations

import copy
import json
import math
import unittest
from collections import Counter
from fractions import Fraction
from typing import Any
from unittest import mock

import numpy as np
import sympy

import g3_candidate_physical_target_audit_v20 as target
import g8_sm_pati_salam_flavour_nogo_v20 as nogo

TIMING_KEYS = {"runtime_seconds"}
O28_RE = "re::O28_B01_unique_Hdag_Sigma2_Sigmadag"
O15 = "O15_B01_Phi_Hdag_Sigma"
O28 = "O28_B01_unique_Hdag_Sigma2_Sigmadag"
O38 = "O38_B01_Phi_Hdag_Sigmadag"
O45_B01 = "O45_B01_Phi2_Hdag_Sigma_210_1050"
O45_B02 = "O45_B02_Phi2_Hdag_Sigma_210_1050"
TWO_HDM = "candidate_PS_content_with_2HDM_below_M_I"
EXPECTED_CHECK_COUNTS = {
    "contract": 20,
    "spinor": 18,
    "light_doublet": 15,
    "H_linear_portals": 20,
    "O28_fix": 13,
    "upstream": 7,
    "data": 5,
    "flavour_structure": 5,
    "lemma_122_clebsch": 7,
    "lemma_su5_casimir": 7,
    "lemma_S_independence": 8,
    "lemma_eft_census": 19,
    "lemma_s1_g3221": 9,
    "lemma_b1a": 4,
}
V2_TRUE_FLAGS = (
    "one_two_two_clebsch_plus_one_via_T15_exact",
    "su5_casimir_selection_rule_exact",
    "light_doublet_pure_10H_and_tan_beta_one_for_every_S_modulus_exact",
    "dirac_yukawas_sigma_balanced_at_every_dimension_exact",
    "eft_census_single_higgs_light_16_monomials_exhaustive_to_dimension_12",
    "ps_invariant_remainder_Me_equals_phase_Md_generic_Y_exact",
    "tan_beta_one_forces_Md_equal_phase_Mu_for_H_linear_PS_invariant_operators_every_dimension_exact",
    "s_equals_one_for_one_light_G3221_bidoublet_exact",
    "b1a_inequality_proved_exact",
    "route_B_one_two_two_source_extensions_excluded",
    "v2_lemmas_status_neutral",
)
V2_FALSE_FLAGS = (
    "second_10H_10H_conjugate_or_FFHstarSstar_can_split_d_from_e",
    "su5_casimir_rule_covers_p_mediated_portal_paths",
    "ps_invariant_remainder_Me_equals_phase_Md_transpose_generic_Y",
    "multi_higgs_PS_invariant_composites_proved_exactly",
    "g3221_vacuum_existence_or_certifiability_claimed",
    "b1a_data_consequence_load_bearing",
    "census_PQ_neutrality_claimed",
    "route_B_reduced_to_120H_among_all_extensions",
    "route_B_120H_repair_established",
)
# Over-broad flag names of the first v2 draft (must not reappear).
V2_WITHDRAWN_FLAGS = (
    "route_B_reduced_to_120H",
    "eft_census_exhaustive_to_dimension_12",
    "tan_beta_one_forces_Md_equal_phase_Mu_to_all_orders_in_PS_invariant_part_exact",
)
# Per-direction row entries computed with a float eigensolver (compared within tolerance, not exactly).
EIGEN_FLOAT_KEYS = (
    "colour_radius",
    "colour_radius_outer_bound_any_combination",
    "colour_radius_with_O06_compensation_upper",
    "doublet_compensation_eps_at_abs_c_4pi",
)


def _strip_timing(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _strip_timing(item) for key, item in value.items() if key not in TIMING_KEYS}
    if isinstance(value, list):
        return [_strip_timing(item) for item in value]
    return value


def _split_float_sections(report: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    report = copy.deepcopy(_strip_timing(report))
    data = report.pop("data")
    seesaw = report.pop("seesaw")
    bounds = report["O28_fix"].pop("repository_r0_bounds")
    portals = report["H_linear_portals"]
    portal_bounds = portals.pop("repository_r0_bounds")
    portal_theta = portals.pop("theta_up_type_max_box_at_physical_r0")
    eigen = {
        direction: [{key: row.pop(key) for key in EIGEN_FLOAT_KEYS} for row in rows]
        for direction, rows in portals["per_direction"].items()
    }
    nda = report["lemma_eft_census"].pop("float_diagnostics")  # NDA cutoff (float, not a check)
    report.pop("verdict")  # formats float minima; checked separately
    return (
        report,
        {
            "data": data,
            "bounds": bounds,
            "portal_bounds": portal_bounds,
            "portal_theta": portal_theta,
            "eigen": eigen,
            "lemma_eft_census_float": nda,
        },
        {"seesaw": seesaw},
    )


class G8FlavourNogoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.committed = json.loads(nogo.OUT_JSON.read_text(encoding="utf-8"))
        cls.fresh = nogo.json_roundtrip(nogo.build_report())

    # ------------------------------------------------------------------
    # Status, checks and flags.
    # ------------------------------------------------------------------

    def test_all_checks_pass_and_route_c_is_recorded(self) -> None:
        for report in (self.committed, self.fresh):
            self.assertEqual(report["n_failed"], 0, report["failures"])
            self.assertEqual(report["n_checks"], len(report["checks"]))
            self.assertTrue(all(report["checks"].values()))
            self.assertEqual(report["status"], nogo.STATUS_RECORDED)
            self.assertEqual(report["overall_state"], nogo.OVERALL_STATE_RECORDED)
            self.assertEqual(report["G8_status"], "OPEN")
            self.assertEqual(report["model_contract_id"], "gauged_u1x_phi17_v20")
            flags = report["flags"]
            for name in (
                "witness_branch_flavour_excluded_at_renormalizable_tree_level",
                "light_doublet_pure_10H_exact",
                "no_induced_heavy_doublet_vev_at_tree_level",
                "flavour_relations_exact",
                "data_exclusion_many_sigma",
                "O28_alone_fix_excluded",
                "O28_portal_breaks_SOS27_certificate",
                "every_doublet_coupled_portal_breaks_SOS27_certificate",
                "colour_stable_region_computed_on_full_H_block",
                "O28_colour_radius_below_4pi_at_some_repository_r0",
                "O15_frees_tan_beta_only_beyond_its_colour_radius",
                "O45_B02_frees_tan_beta_inside_colour_stable_region",
                "portal_induced_126bar_vev_up_type_only_exact",
                "M_e_equals_phase_M_d_transpose_for_every_portal_combination",
                "H_linear_portal_fix_excluded_at_anchor_chain_r0",
                "H_linear_portal_fix_excluded_at_every_repository_r0",
                "seesaw_generic_nonperturbative_if_MD_equals_Mu_data",
                "route_C_recorded",
                *V2_TRUE_FLAGS,
            ):
                self.assertIs(flags[name], True, name)
            for name in (
                "G8_closed",
                "falsifies_G3_G5_scalar_vacuum_certificates",
                "falsifies_so10_contract",
                "seesaw_load_bearing",
                # Findings the portal-set analysis does NOT support (recorded, not claimed).
                "O28_alone_t_b_bound_survives_other_portals",
                "O28_alone_b_tau_repairable",
                # Scope statements of the v2 lemmas (not claimed).
                *V2_FALSE_FLAGS,
            ):
                self.assertIs(flags[name], False, name)
            for name in ("O28_in_contract_fix_excluded", "seesaw_generic_nonperturbative", *V2_WITHDRAWN_FLAGS):
                self.assertNotIn(name, flags)
            self.assertEqual(report["n_checks"], 157)
            self.assertEqual(dict(Counter(key.split(".")[0] for key in report["checks"])), EXPECTED_CHECK_COUNTS)
            self.assertEqual(set(report["routes"]), {"A", "B", "C"})
            self.assertIn("DOWN-type", report["routes"]["A"])

    def test_status_strings(self) -> None:
        self.assertTrue(nogo.STATUS_RECORDED.endswith("__G8_OPEN"))
        self.assertTrue(nogo.STATUS_INCOMPLETE.endswith("__G8_OPEN"))
        self.assertNotEqual(nogo.STATUS_RECORDED, nogo.STATUS_INCOMPLETE)

    def test_committed_artifact_matches_fresh_report(self) -> None:
        committed_exact, committed_float, committed_scan = _split_float_sections(self.committed)
        fresh_exact, fresh_float, fresh_scan = _split_float_sections(self.fresh)
        self.assertEqual(target.report_mismatches(committed_exact, fresh_exact), [])
        self.assertEqual(target.report_mismatches(committed_float, fresh_float, "float", rel_tol=1.0e-6, abs_tol=1.0e-9), [])
        self.assertEqual(target.report_mismatches(committed_scan, fresh_scan, "scan", rel_tol=5.0e-2, abs_tol=1.0e-6), [])

    def test_committed_markdown_regenerates(self) -> None:
        expected = nogo._markdown(self.committed).replace("\r\n", "\n")
        self.assertEqual(nogo.OUT_MD.read_text(encoding="utf-8").replace("\r\n", "\n"), expected)

    def test_tampered_artifact_is_detected(self) -> None:
        tampered = copy.deepcopy(self.committed)
        tampered["checks"]["light_doublet.H_block_decoupled_at_every_r0"] = False
        committed_exact, _, _ = _split_float_sections(self.committed)
        tampered_exact, _, _ = _split_float_sections(tampered)
        self.assertNotEqual(target.report_mismatches(committed_exact, tampered_exact), [])

    # ------------------------------------------------------------------
    # Exact content.
    # ------------------------------------------------------------------

    def test_light_doublet_is_pure_10h(self) -> None:
        section = self.fresh["light_doublet"]
        self.assertEqual(tuple(section["H_linear_directions"]), nogo.EXPECTED_H_LINEAR_DIRECTIONS)
        self.assertEqual(len(section["H_linear_parameters"]), 10)
        self.assertEqual(tuple(section["nonzero_H_quadratic_parameters"]), nogo.EXPECTED_NONZERO_H_QUADRATIC)
        self.assertEqual(len(section["exact_hessian_audits"]), 4)
        for audit in section["exact_hessian_audits"]:
            for key in ("gradient_zero", "H_rows_vanish_outside_H_block", "H_block_matches_exact_formula", "Re_H_6_9_exact_null_vectors"):
                self.assertIs(audit[key], True, (audit["r0"], key))
        self.assertIn(str(nogo.physical_r0()), [audit["r0"] for audit in section["exact_hessian_audits"]])

    def test_spinor_clebsches(self) -> None:
        spinor = self.fresh["spinor"]
        self.assertEqual(len(spinor["clebsch_at_vev"]), 8)
        self.assertEqual(set(spinor["clebsch_moduli"].values()), {"a**2 + b**2"})
        self.assertEqual(spinor["sigma_std_bilinear_entries"], [["nuc[---]", "nuc[---]", [0, 32]]])
        for row in spinor["fifteen_two_two"].values():
            self.assertEqual(row["lepton_over_quark_relative_clebsch"], "-3")
        self.assertTrue(spinor["tensor_products"]["decomposition_proved"])
        blocks = spinor["tensor_products"]["blocks"]
        self.assertEqual([blocks["16x16"][str(k)]["rank_lower_bound_GFp"] for k in range(6)], [0, 10, 0, 120, 0, 126])
        self.assertEqual([blocks["16x16bar"][str(k)]["rank_lower_bound_GFp"] for k in range(6)], [1, 0, 45, 0, 210, 0])

    def test_contract_enumeration(self) -> None:
        contract = self.fresh["contract"]
        self.assertEqual(contract["conj_H10_yukawas"], [])
        self.assertEqual(set(contract["X1_sixteens"]), {"F", "P", "R"})
        self.assertIn("H10.F.F", contract["H10_yukawas"])
        self.assertIn("Delta126bar.F.F", contract["Delta126bar_yukawas"])
        self.assertTrue(all("Phi17" in row or "S" in row.split(".")[0] for row in contract["vectorlike_mass_couplings"]))
        self.assertEqual(contract["sixteenbar_pair_couplings"], ["conj[Delta126bar].Pbar.Rbar", "conj[H10].Pbar.Rbar"])
        self.assertEqual(contract["chirality"], {"n16": 11, "n16bar": 8, "net": 3})

    def test_o28_exact_closed_form(self) -> None:
        o28 = self.fresh["O28_fix"]
        closed = o28["closed_form"]
        self.assertEqual(closed["R_theta_sigma_squared_over_c2_r4"], "7962624*(13*r**2 + 6)**2/(13*r**4 + 12*r**2 + 36)**2")
        self.assertEqual(closed["light_mass_shift_over_c2_r4"], "-663552*(13*r**2 + 6)/(13*r**4 + 12*r**2 + 36)")
        self.assertEqual(closed["R_at_zero"], "221184")
        first = o28["exact_rows"][0]
        self.assertEqual(first["r0"], "1/5")
        self.assertEqual(first["theta_sigma_squared_over_c2_r0_4"], "132224348160000/520432969")
        self.assertEqual(first["light_mass_shift_over_c2_r0_4"], "-2703974400/22813")
        for row in o28["exact_rows"]:
            self.assertTrue(row["closed_form_matches"])
            self.assertTrue(row["saddle_for_every_c_nonzero"])
        self.assertLess(o28["theta_max_at_anchor_abs_c_4pi"], 3.0e-5)
        # JSON keeps 12 significant digits, so ratios of stored floats agree to ~1e-11.
        self.assertAlmostEqual(o28["theta_max_at_anchor_abs_c_4pi_any_tan_beta"] / o28["theta_max_at_anchor_abs_c_4pi"], math.sqrt(2.0), places=9)
        self.assertEqual(set(o28["repository_r0_bounds"]), set(nogo.EXPECTED_REPOSITORY_SCALES))
        self.assertEqual(len(o28["exact_rows"]), 8)
        for key, row in o28["repository_r0_bounds"].items():
            self.assertGreater(row["t_b_split_requires_Y_F_at_least"], nogo.PORTAL_BOX)
            self.assertNotIn("t_b_split_requires_Y126_at_least", row)
            self.assertNotIn("b_tau_split_requires_Y_F_at_least", row)  # alpha_d = 0 exactly: no b-tau requirement
            self.assertIs(row["induced_126bar_vev_up_type_only"], True)
            self.assertLessEqual(row["abs_c_max_colour_stable"], nogo.PORTAL_BOX + 1.0e-9)  # JSON keeps 12 digits
            self.assertAlmostEqual(row["abs_c_max_colour_stable"], min(nogo.PORTAL_BOX, row["colour_radius"]), places=9, msg=key)
        two_hdm = o28["repository_r0_bounds"][TWO_HDM]
        self.assertLess(two_hdm["colour_radius"], nogo.PORTAL_BOX)  # |c_O28| = 4 pi lies beyond the colour-stable range
        self.assertAlmostEqual(two_hdm["colour_radius"], 4.537, delta=0.01)
        self.assertEqual(o28["findings"]["colour_radius_below_4pi_at"], [TWO_HDM])
        self.assertIs(o28["findings"]["b_tau_repairable_by_O28"], False)
        self.assertIn("Y_F", o28["mirsky_argument"])
        self.assertIn("alpha_d = 0", o28["mirsky_argument"])
        self.assertIn("conservative for the no-go", o28["coefficient_box_note"])
        self.assertIn("O(c^2)", o28["sos27_statement"])

    def test_all_h_linear_portals(self) -> None:
        portals = self.fresh["H_linear_portals"]
        self.assertTrue(all(portals["checks"].values()))
        patterns = portals["lattice_binding"]["patterns"]
        expected = {
            O15: ("Phi210", 1, ["-1/2", "1/2"], {"Phi210": 1, "Sigma126bar": 0}, "+"),
            O28: ("Sigma126bar", 2, ["-192", "192"], {"Sigma126bar": 2}, "+"),
            O38: ("Phi210", 2, ["-1/2", "1/2"], {"Phi210": 2, "Sigma126bar": 1}, "-"),
            O45_B01: ([], 0, [], {"Phi210": 1}, None),
            O45_B02: ("Phi210", 1, ["-1", "1"], {"Phi210": 1}, "+"),
        }
        for direction, (block, power, entries, triplets, source) in expected.items():
            for prefix in ("re", "im"):
                row = patterns[f"{prefix}::{direction}"]
                self.assertEqual((row["doublet_column_block"], row["r0_power"], row["doublet_column_entries"]), (block, power, entries))
                self.assertEqual({name: value["r0_power"] for name, value in row["triplet_column_blocks"].items()}, triplets)
                self.assertEqual(row["doublet_source_hypercharge"], source)
                self.assertIs(row["H_by_H_and_nonH_by_nonH_blocks_zero"], True)
                self.assertIs(row["bound"], True)
        self.assertEqual(patterns[f"re::{O15}"]["triplet_column_blocks"]["Sigma126bar"]["entries"], ["-2", "2"])
        per_direction = portals["per_direction"]
        self.assertEqual(set(per_direction), set(nogo.EXPECTED_H_LINEAR_DIRECTIONS))
        for direction, rows in per_direction.items():
            self.assertEqual(len(rows), 5)  # physical member + the four repository r0
            self.assertEqual(rows[0]["r0"], str(nogo.physical_r0()))
            for row in rows:
                self.assertIs(row["colour_triplet_coupling"], True)
                self.assertIs(row["colour_radius_exact_bracket"], True)
                self.assertEqual(row["triplet_heavy_component_sizes"], [14])
                self.assertIs(row["triplet_schur_phase_independent"], True)
                self.assertIs(row["doublet_schur_phase_independent"], True)
                self.assertIs(row["sigma_admixture_gram_equals_2_theta2_times_source_projector"], True)
                if direction == O45_B01:
                    self.assertIs(row["doublet_coupling"], False)
                    self.assertEqual(row["theta_sigma_squared_per_unit_c"], "0")
                    continue
                self.assertIs(row["saddle_for_every_c_nonzero"], True)
                self.assertEqual(row["heavy_component_sizes"], [14])
                self.assertIs(row["induced_126bar_vev_up_type_only"], True)
                self.assertIs(row["induced_lepton_over_quark_modulus_3"], True)
                self.assertEqual(row["induced_126bar_yukawa_pairs"], ["d-uc", "e-nuc", "nu-nuc", "u-uc"])
                self.assertAlmostEqual(
                    row["theta_sigma_max_over_tan_beta_per_unit_c_float"] / row["theta_sigma_per_unit_c_float"], math.sqrt(2.0), places=9
                )
                self.assertGreaterEqual(row["colour_radius_outer_bound_any_combination"], row["colour_radius"])
        anchor = {direction: rows[0] for direction, rows in per_direction.items()}
        self.assertAlmostEqual(anchor[O28]["theta_sigma_over_c_r0_2_float"], 470.302, places=3)
        self.assertAlmostEqual(anchor[O15]["theta_sigma_over_c_r0_2_float"], 1.63299, places=4)
        self.assertAlmostEqual(anchor[O45_B02]["theta_sigma_over_c_r0_2_float"], 3.26599, places=4)
        r0 = float(Fraction(anchor[O38]["r0"]))
        self.assertAlmostEqual(anchor[O38]["theta_sigma_over_c_r0_2_float"] / r0, 1.63299, places=4)
        for rows in (per_direction[O15],):
            for row in rows:
                self.assertAlmostEqual(row["colour_radius"], math.sqrt(5.0 / 8.0), delta=1.0e-5)  # r0-independent
        bounds = portals["repository_r0_bounds"]
        self.assertEqual(set(bounds), set(nogo.EXPECTED_REPOSITORY_SCALES))
        for key, row in bounds.items():
            self.assertLess(row["theta_up_type_max_box_triangle_bound"], nogo.PORTAL_THETA_THRESHOLD)
            self.assertLessEqual(row["theta_up_type_max_colour_stable_triangle_bound"], row["theta_up_type_max_box_triangle_bound"])
            self.assertGreater(row["O28_share_of_box_bound"], 0.98)
            self.assertEqual(row["tan_beta_reaches_m_t_over_m_b_in_box_with"], [O15, O45_B02], key)
            self.assertEqual(row["tan_beta_reaches_m_t_over_m_b_colour_stable_with"], [O45_B02], key)
            self.assertLess(row["tan_beta_scan_colour_stable"][O15]["tan_beta_max_over_scan"], row["m_t_over_m_b_at_M_I"])
            self.assertLess(row["tan_beta_scan_box"][O28]["tan_beta_max_over_scan"], 4.0)
            self.assertIs(row["induced_126bar_vev_up_type_only_every_direction"], True)
            self.assertGreaterEqual(row["portal_immune_tests_min_pull_conservative_sigma"], nogo.NOGO_PULL_THRESHOLD)
            self.assertIs(row["portal_fix_excluded"], True)
            self.assertLess(row["colour_radius"][O15], 1.0)
            for direction in (O38, O45_B01, O45_B02):
                self.assertGreater(row["colour_radius"][direction], nogo.PORTAL_BOX)
        self.assertLess(bounds[TWO_HDM]["colour_radius"][O28], nogo.PORTAL_BOX)
        findings = portals["findings"]
        self.assertIs(findings["portal_fix_excluded_at_anchor_chain_r0"], True)
        self.assertIs(findings["portal_fix_excluded_at_every_repository_r0"], True)
        self.assertEqual(findings["portal_fix_not_excluded_at"], [])
        self.assertIs(findings["down_type_and_charged_lepton_masses_untouched_by_every_portal_combination"], True)
        self.assertIs(findings["t_b_bound_survives_portal_set_at_every_repository_r0"], False)
        self.assertIs(findings["O15_frees_tan_beta_only_beyond_its_colour_radius"], True)
        self.assertNotIn("NOT excluded", self.fresh["verdict"])
        self.assertIn("no in-contract H-linear portal repair of the flavour sector survives at any repository r0", self.fresh["verdict"])
        self.assertIn("O(c^2)", portals["scope_note"])
        self.assertIn("Haynsworth", portals["scope_note"])
        self.assertIn("new G3 certificate", portals["colour_stable_region"]["compensation"])

    def test_induced_vev_lemma_and_vectorlike_rank(self) -> None:
        section = self.fresh["light_doublet"]
        self.assertEqual(section["H_degree_histogram"], {"0": 27, "1": 5, "2": 10, "4": 2})
        self.assertIs(section["checks"]["no_H_degree_3_live_direction"], True)
        self.assertIs(section["checks"]["potential_even_in_H_on_the_witness"], True)
        certificate = self.fresh["contract"]["vectorlike_rank_certificate"]
        self.assertEqual(certificate["rank_at_integer_couplings"], 8)
        self.assertEqual(certificate["kernel_dimension"], 3)
        self.assertEqual(certificate["kernel_support_fields"], ["F", "P", "Q", "R"])
        self.assertIs(self.fresh["contract"]["checks"]["vectorlike_pattern_generic_rank_8"], True)
        proved = " ".join(self.fresh["scope"]["proved_exactly"])
        self.assertIn("no heavy doublet", proved)
        self.assertIn("generic rank 8", proved)
        self.assertIn("matched exactly by the first-order solve at 8 r0 values", proved)
        self.assertIn("M_e = phase x M_d^T for every portal combination", proved)
        self.assertNotIn("exact at five r0 values", proved)

    def test_seesaw_premise_is_labelled(self) -> None:
        seesaw = self.fresh["seesaw"]
        self.assertIn("M_D = M_u(data) is the generic SO(10) premise", seesaw["assumptions"])
        for row in seesaw["rows"].values():
            self.assertLess(row["generic_Y_R_if_MD_has_charged_lepton_singular_values"], row["generic_Y_R"] / 1000.0)
        at_1e12 = seesaw["rows"]["1e+12 GeV"]["generic_Y_R_if_MD_has_charged_lepton_singular_values"]
        self.assertAlmostEqual(at_1e12, 0.063, delta=0.01)

    def test_data_exclusion(self) -> None:
        data = self.fresh["data"]
        self.assertGreaterEqual(data["minimum_load_bearing_pull_raw_sigma"], nogo.NOGO_PULL_THRESHOLD)
        self.assertGreaterEqual(data["minimum_load_bearing_pull_conservative_sigma"], nogo.NOGO_PULL_THRESHOLD)
        vus = next(row for row in data["tests_scale_free"] if row["test"] == "|V_us|")
        self.assertAlmostEqual(vus["pull_raw_sigma"], 0.2243 / 0.0008, places=6)

    # ------------------------------------------------------------------
    # Status-neutral v2 lemmas (exact content).
    # ------------------------------------------------------------------

    def _lemma(self, key: str, count: int) -> dict[str, Any]:
        """The fresh lemma section (committed-vs-fresh equality is test_committed_artifact_matches_fresh_report)."""
        lemma = self.fresh[key]
        self.assertEqual(len(lemma["checks"]), count, key)
        self.assertTrue(all(lemma["checks"].values()), key)
        return lemma

    def test_lemma_122_clebsch_via_T15(self) -> None:
        lemma = self._lemma("lemma_122_clebsch", 7)
        self.assertEqual(
            lemma["T15_values"], {"u": "1", "d": "1", "e": "-3", "nu": "-3", "uc": "-1", "dc": "-1", "ec": "3", "nuc": "3"}
        )
        self.assertEqual(lemma["oriented_ratio_120_over_10"], ["-1"])  # one constant: lepton/quark Clebsch +1
        self.assertEqual(lemma["oriented_ratio_126bar_15_over_T15_10"], ["-I"])
        self.assertEqual(lemma["oriented_ratio_120_15_over_T15_10"], ["I"])
        self.assertIn("does not exclude a 120_H", lemma["scope"])
        self.assertIn("F.F.H10^*.S^*", lemma["scope"])
        self.assertIs(self.fresh["flags"]["second_10H_10H_conjugate_or_FFHstarSstar_can_split_d_from_e"], False)

    def test_lemma_su5_casimir_selection_rule(self) -> None:
        lemma = self._lemma("lemma_su5_casimir", 7)
        self.assertEqual(
            lemma["casimir"],
            {
                "z_k": "12/5",
                "zbar_k": "12/5",
                "sigma_std": "0",
                "w_u": "12/5",
                "w_d": "32/5",
                "126_part_of_omega6_iota_zbar5_p": "12/5",
                "126_part_of_zbar5_J_J": "12/5",
            },
        )
        self.assertEqual(set(lemma["casimir_by_vector"].values()), {"12/5"})
        self.assertEqual(lemma["doublet_spaces"], {"Y=+1/2": [3, 1], "Y=-1/2": [3, 1]})
        self.assertEqual(lemma["doublet_space_monomials"], {"Y=+1/2": 6, "Y=-1/2": 6})
        self.assertEqual(lemma["pairs"], {"w_u": ["nu-nuc", "u-uc"], "w_d": ["d-dc", "e-ec"]})
        # Scope: p is not an SU(5) singlet, so the p-mediated portal paths rest on the per-r0 Schur computation.
        self.assertIs(lemma["p_is_su5_singlet"], False)
        self.assertIn("not on this lemma", lemma["scope"])
        self.assertIs(self.fresh["flags"]["su5_casimir_rule_covers_p_mediated_portal_paths"], False)

    def test_lemma_S_independence(self) -> None:
        lemma = self._lemma("lemma_S_independence", 8)
        self.assertEqual(lemma["S_block_units"], ["O04 |S|^2", "O23 |S|^4"])
        self.assertEqual(lemma["units_coupling_S_to_other_blocks"], [])
        self.assertEqual(lemma["S_dependent_nonzero_benchmark_directions"], list(nogo.S_DEPENDENT_NONZERO_DIRECTIONS))
        self.assertEqual(lemma["S_dependent_H_linear_directions"], [O38])
        self.assertEqual(
            lemma["O12_component_block"], "Matrix([[2*c06 + 4*c12*s_r, -4*c12*s_i], [-4*c12*s_i, 2*c06 - 4*c12*s_r]])"
        )
        self.assertEqual(lemma["retuned_block_formula"], "diag(2, 2 + 2 r0 r_S | 0, 2 r0 r_S)")
        self.assertEqual(lemma["tested_r_S_over_r0"], [1, 10, 1000])
        self.assertEqual(lemma["tested_r0"], ["1/5", "1/20", "1/100", str(nogo.physical_r0())])
        self.assertEqual(len(lemma["retuned_rows"]), 12)
        self.assertTrue(all(row["matches_formula"] for row in lemma["retuned_rows"]))
        self.assertIn("global minimum", lemma["scope"])
        # (vii) is exact on forms; the compiler's lattice-bound O38 pattern is a corroboration, not a check.
        self.assertEqual(
            lemma["O38_exact_form_blocks"],
            {
                "H_by_S_block_zero_for_every_H_direction": True,
                "doublet_H_by_Sigma_block_zero_e_a_wedge_p_vanishes": True,
                "triplet_H_by_Sigma_block_nonzero": True,
                "doublet_columns_reach_Phi": True,
            },
        )
        self.assertIs(lemma["O38_compiler_pattern_corroboration_not_a_check"], True)
        self.assertIn("unique 10 x 210 -> 126 contraction", lemma["scope"])
        self.assertIn("recorded as a corroboration only", lemma["scope"])
        self.assertIn("O38_compiler_pattern_corroboration_not_a_check", " ".join(self.fresh["scope"]["float_diagnostics"]))

    def test_lemma_eft_census(self) -> None:
        lemma = self._lemma("lemma_eft_census", 19)
        self.assertEqual(lemma["max_dimension"], 12)
        self.assertEqual(lemma["counts"], nogo.EFT_CENSUS_COUNTS)
        self.assertEqual(lemma["counts"], {"X_neutral_monomials": 4657, "dirac": 1460, "majorana": 800})
        self.assertEqual(
            lemma["dirac_dimension_histogram"],
            {"4": 6, "5": 15, "6": 36, "7": 64, "8": 110, "9": 167, "10": 248, "11": 344, "12": 470},
        )
        self.assertEqual(lemma["min_dimensions"], {"ps_breaking_dirac": 6, "Htilde_dirac": 5})
        self.assertEqual(lemma["spurion_charges"]["Sigma"]["B_minus_L_T3R"], "(-2, 1)")
        self.assertEqual(lemma["spurion_charges"]["Sigma*"]["B_minus_L_T3R"], "(2, -1)")
        for name in ("Phi", "S", "S*", "Phi17", "Phi17*"):
            self.assertEqual(lemma["spurion_charges"][name]["B_minus_L_T3R"], "(0, 0)", name)
            self.assertIs(lemma["spurion_charges"][name]["ps_breaking"], False, name)
        self.assertEqual(lemma["dirac_targets"], ["(0, -1)", "(0, 0)", "(0, 1)"])
        self.assertEqual(lemma["majorana_target"], "(-2, 1)")
        # Net Phi17 numbers are data only: no PQ-neutrality claim.
        self.assertEqual(lemma["net_Phi17_numbers_dirac"], [-2, -1, 0])
        self.assertIn("no PQ-neutrality claim", lemma["net_Phi17_note"])
        self.assertIs(self.fresh["flags"]["census_PQ_neutrality_claimed"], False)
        # Orientation: M_e = kappa M_d (no transpose) for generic Yukawas; the transposed form only for symmetric Y.
        self.assertEqual(lemma["kappa_e_over_d"], {"d[+--]": "-1", "d[-+-]": "1", "d[--+]": "-1"})
        self.assertEqual(lemma["kappa_nu_over_u"], {"u[+--]": "-1", "u[-+-]": "1", "u[--+]": "-1"})
        self.assertEqual(set(lemma["tan_beta_one_ratios"].values()), {"exp(I*(-theta1 + theta2))"})
        self.assertIn("no transpose", lemma["orientation_note"])
        self.assertIs(self.fresh["flags"]["ps_invariant_remainder_Me_equals_phase_Md_transpose_generic_Y"], False)
        self.assertIn("exhaustive to mass dimension 12", lemma["cutoff_statement"]["exact"])
        self.assertIn("not a check", lemma["cutoff_statement"]["float"])
        # The census class and the H-linear scope of the remainder are stated wherever exhaustiveness is claimed.
        for text in (lemma["statement"], lemma["scope"], lemma["cutoff_statement"]["exact"]):
            self.assertIn("single-Higgs (or Higgs-free) monomials", text)
        for text in (lemma["statement"], lemma["scope"]):
            self.assertIn("linear in H10 or H10^*", text)
        self.assertIn("Multi-Higgs operators", lemma["scope"])
        self.assertIn("covered only through the cited light-state lemma", lemma["scope"])
        self.assertIn("multi-Higgs composites only hand-argued", lemma["cutoff_statement"]["exact"])
        proved = " ".join(self.fresh["scope"]["proved_exactly"])
        self.assertIn("single-Higgs (or Higgs-free) monomials of two light 16s (F, P, Q, R)", proved)
        self.assertIn("SU(2)_L x SU(2)_R covariance", " ".join(self.fresh["scope"]["cited_or_hand_argued"]))
        self.assertIn("multi-Higgs monomials", " ".join(self.fresh["scope"]["not_claimed"]))
        self.assertIs(self.fresh["flags"]["multi_higgs_PS_invariant_composites_proved_exactly"], False)
        nda = lemma["float_diagnostics"]["nda_Lambda_max_over_v_R"]
        self.assertEqual(set(nda), set(self.fresh["data"]["tests_per_scale"]))
        for row in nda.values():
            self.assertTrue(150.0 < row["s_mu"] < 200.0, row)
            self.assertTrue(50.0 < row["b_tau"] < 100.0, row)

    def test_lemma_s1_g3221(self) -> None:
        lemma = self._lemma("lemma_s1_g3221", 9)
        self.assertEqual(
            lemma["O15_ratio_to_iota15"],
            {
                "a": {"e6": "I", "e7": "I", "e8": "I", "e9": "I"},
                "omega": {"e8": "none", "e9": "none", "z4": "I", "z5": "I", "zbar4": "-I", "zbar5": "-I"},
                "p": "0",
            },
        )
        self.assertEqual(set(lemma["one_bidoublet_Mu_over_Md"].values()), {"alpha/beta"})
        self.assertEqual(len(lemma["one_bidoublet_Mu_over_Md"]), 3)
        self.assertEqual(lemma["conjugate_mixing_determinant"], "16*I*c*d*(alpha*alphabar - beta*betabar)")
        self.assertEqual(lemma["two_bidoublet_determinant"], "16*I*(alpha1*beta2 - alpha2*beta1)")
        self.assertIn("Not claimed: existence or certifiability of any G3221 vacuum", lemma["scope"])
        self.assertIs(self.fresh["flags"]["g3221_vacuum_existence_or_certifiability_claimed"], False)
        # s is defined, and the <Sigma>-mediated (v_R-scale SU(2)_R-breaking) mixings are named as unanalysed.
        self.assertIn("Definition: s = (v_u^126/v_u^10)/(v_d^126/v_d^10)", lemma["statement"])
        self.assertIn("v_R-scale SU(2)_R breaking through <Sigma>", lemma["statement"])
        self.assertIn("<Phi>-mediated O15 H-Sigma block", lemma["scope"])
        self.assertIn("<Sigma>-mediated mixings, which break SU(2)_R at v_R, are not analysed", lemma["scope"])
        self.assertNotIn("(true for O15 at a (15,1,1) vev", lemma["scope"])

    def test_lemma_b1a_proved(self) -> None:
        lemma = self._lemma("lemma_b1a", 4)
        self.assertEqual(lemma["sharp_case"], "S = 0, x_d = 0")
        for step in ("Tr(A^dag S) = 0", "Frobenius-orthogonal", "reverse triangle inequality", "Cauchy-Binet"):
            self.assertIn(step, lemma["proof"])
        self.assertIn("Not claimed: its data consequence", lemma["scope"])
        self.assertIs(self.fresh["flags"]["b1a_data_consequence_load_bearing"], False)
        self.assertNotIn("FLOAT", json.dumps(lemma))
        # Float smoke test of the proved inequality (not a check of the report): random complex S, a, x_d, x_e.
        rng = np.random.default_rng(20260926)

        def adjugate_norm(matrix: np.ndarray) -> float:
            values = np.linalg.svd(matrix, compute_uv=False)
            return float(math.sqrt(values[0] ** 2 * values[1] ** 2 + values[0] ** 2 * values[2] ** 2 + values[1] ** 2 * values[2] ** 2))

        worst = 0.0
        for _ in range(2000):
            symmetric = rng.normal(size=(3, 3)) + 1j * rng.normal(size=(3, 3))
            symmetric = symmetric + symmetric.T
            a = rng.normal(size=3) + 1j * rng.normal(size=3)
            antisymmetric = np.array([[0, a[2], -a[1]], [-a[2], 0, a[0]], [a[1], -a[0], 0]])
            x_d, x_e = (complex(*rng.normal(size=2)) * 10 ** rng.uniform(-1, 1) for _ in range(2))
            m_d, m_e = symmetric + x_d * antisymmetric, symmetric + x_e * antisymmetric
            lhs = abs(np.linalg.norm(m_e) ** 2 - np.linalg.norm(m_d) ** 2)
            worst = max(worst, lhs / (2.0 * (adjugate_norm(m_d) + adjugate_norm(m_e))))
        self.assertLessEqual(worst, 1.0 + 1.0e-9)

    def test_route_b_text_is_corrected(self) -> None:
        for routes in (self.fresh["routes"], self.committed["routes"], nogo.ROUTES):
            route_b = routes["B"]
            for text in ("120_H", "excluded", "Route A", "lemma_122_clebsch", "lemma_eft_census", "lemma_S_independence"):
                self.assertIn(text, route_b)
            self.assertNotIn("a 120_H, a second 10_H, or a UV completion", route_b)
            # Scoped to the analysed candidates: not "reduced to a 120_H" among all extensions.
            self.assertNotIn("reduced to a 120_H:", route_b)
            self.assertNotIn("any UV completion that generates", route_b)
            self.assertIn("Among the analysed candidate extensions", route_b)
            self.assertIn("so Route B is not reduced to a 120_H among all extensions", route_b)
            self.assertIn("the operator F.F.H10^*.S^* (whatever completion generates it)", route_b)
            self.assertIn("H10's (X, Z17) = (-2, 15) or H10^*'s (2, 2) (hand-argued, not recomputed)", route_b)
            for text in ("second 126bar_H", "a new B-L-breaking scalar vev (e.g. a 45_H", "vectorlike matter", "further PS-breaking operators near v_R"):
                self.assertIn(text, route_b)
            self.assertIn("A 120_H is not shown to repair G8", route_b)
            self.assertIn("DOWN-type", routes["A"])
            self.assertIn("lemma_s1_g3221", routes["A"])
            self.assertIn("v_R-scale SU(2)_R breaking through <Sigma>", routes["A"])
            self.assertIn("with a G3221-equivariant composition", routes["A"])
        self.assertNotIn("120_H or a second 10_H", nogo.__doc__)
        self.assertNotIn("reduced to a 120_H", nogo.__doc__)
        self.assertIn("among the analysed candidates only a 120_H", nogo.__doc__)
        for report in (self.fresh, self.committed):
            self.assertNotIn("Route B reduces to a 120_H", report["verdict"])
            self.assertIn("among the analysed candidate extensions only a 120_H can", report["verdict"])
            self.assertIs(report["flags"]["route_B_reduced_to_120H_among_all_extensions"], False)
            self.assertIs(report["flags"]["route_B_one_two_two_source_extensions_excluded"], True)
            cited = " ".join(report["scope"]["cited_or_hand_argued"])
            self.assertIn("H' -> H or H' -> conj(H)", cited)

    def test_v2_lemmas_are_status_neutral(self) -> None:
        for report in (self.committed, self.fresh):
            self.assertEqual(report["status"], nogo.STATUS_RECORDED)
            self.assertEqual(report["overall_state"], nogo.OVERALL_STATE_RECORDED)
            self.assertEqual(report["G8_status"], "OPEN")
            self.assertIs(report["flags"]["G8_closed"], False)
            self.assertIs(report["flags"]["falsifies_so10_contract"], False)
            self.assertIs(report["flags"]["v2_lemmas_status_neutral"], True)
            v1_checks = [key for key in report["checks"] if not key.startswith(nogo.LEMMA_KEYS)]
            self.assertEqual(len(v1_checks), 103)
            not_claimed = " ".join(report["scope"]["not_claimed"])
            self.assertIn(
                "they do not falsify the contract: a 120_H extension, a Route A branch and the extensions not analysed "
                "here remain logically open",
                not_claimed,
            )
            self.assertIn("Route B is not reduced to a 120_H among all extensions", not_claimed)
            self.assertIn("a UV completion that adds further PS-breaking operators near v_R is not analysed", not_claimed)
            self.assertIn("its list of escapes is exhaustive only for G3221-equivariant compositions", not_claimed)
            self.assertIn("radiative (loop-level) Pati-Salam breaking is not analysed", not_claimed)
            self.assertIn("G8 stays OPEN and the contract is not falsified.", report["verdict"])
            self.assertNotIn("M_e = phase x M_d^T for generic", report["verdict"])
        # A failing lemma check fails closed like every other check.
        report = copy.deepcopy(self.fresh)
        report["n_failed"] = 1
        report["failures"] = ["lemma_b1a.adjugate_parity_decomposition"]
        self.assertIn("NOT recorded", nogo._verdict(report))

    # ------------------------------------------------------------------
    # Fail-closed mutations.
    # ------------------------------------------------------------------

    def _model_text(self) -> str:
        return nogo.MODEL_FILE.read_text(encoding="utf-8")

    def test_mutation_conjugate_10h_yukawa_is_rejected(self) -> None:
        text = self._model_text().replace("Y10 F.F.H10", "Y10 F.F.conj[H10]")
        checks = nogo.contract_section(text)["checks"]
        self.assertFalse(checks["declared_terms_U1X_neutral"])
        self.assertFalse(checks["declared_yukawas_subset_of_allowed"])

    def test_mutation_second_10h_breaks_the_premise(self) -> None:
        extra = "ScalarFields[[6]] = {H10b,         1, h10b,          10,   2, Exp[2*Pi*I*2/17]};\n"
        text = self._model_text().replace("(* The 210 is a real SO(10) representation. *)", extra + "(* The 210 is a real SO(10) representation. *)")
        section = nogo.contract_section(text)
        self.assertIn("conj[H10b].F.F", {row["coupling"] for row in section["allowed_renormalizable_fermion_couplings"]})
        self.assertFalse(section["checks"]["sixteen_sixteen_scalars_only_H10_and_Delta126bar"])
        self.assertFalse(section["checks"]["model_fields_parsed"])

    def test_mutation_120h_breaks_the_premise(self) -> None:
        extra = "ScalarFields[[6]] = {Sigma120,     1, sig120,       120,  -2, Exp[2*Pi*I*15/17]};\n"
        text = self._model_text().replace("(* The 210 is a real SO(10) representation. *)", extra + "(* The 210 is a real SO(10) representation. *)")
        checks = nogo.contract_section(text)["checks"]
        self.assertFalse(checks["no_120_scalar_in_contract"])
        self.assertFalse(checks["sixteen_sixteen_scalars_only_H10_and_Delta126bar"])

    def test_mutation_portal_on_fails_closed(self) -> None:
        checks = nogo.portal_section({O28_RE: Fraction(1)}, r0_values=[Fraction(1, 5)])["checks"]
        self.assertFalse(checks["H_linear_parameters_zero_in_benchmark"])
        self.assertFalse(checks["H_linear_parameters_zero_for_all_r0_x0_symbolic"])
        self.assertFalse(checks["binding_unit_coverage_complete_at_every_r0"])

    def test_mutation_o06_retune_breaks_the_exact_h_block(self) -> None:
        o06 = "lambda::O06_B01_Hdag_H_norm"
        value = nogo.candidate.candidate_coefficients()[o06] + Fraction(1, 2500)
        checks = nogo.portal_section({o06: value}, r0_values=[Fraction(1, 5)])["checks"]
        self.assertFalse(checks["H_block_equals_exact_formula_at_every_r0"])
        self.assertFalse(checks["Re_H_6_9_exact_null_vectors_at_every_r0"])
        self.assertFalse(checks["my_exact_hessian_reproduces_certified_benchmark_hessian"])

    def test_mutation_non_real_doublet_breaks_tan_beta_one(self) -> None:
        vev = {8: nogo.A_SYMBOL, 9: sympy.I * nogo.B_SYMBOL}
        spinor = nogo.spinor_section(vev)
        self.assertFalse(spinor["checks"]["equal_5_5bar_components_tan_beta_one"])
        self.assertFalse(spinor["checks"]["clebsch_moduli_equal_a2_plus_b2"])
        structure = nogo.flavour_structure_section(spinor)
        self.assertFalse(structure["checks"]["MuMu_dagger_equals_MdMd_dagger"])

    def test_mutation_data_without_mixing_fails_closed(self) -> None:
        data = copy.deepcopy(nogo.DATA)
        for key in ("V_us", "V_cb", "V_ub"):
            data["ckm_moduli"][key]["value"] = 1.0e-4
        checks = nogo.data_section(data)["checks"]
        self.assertFalse(checks["every_load_bearing_test_excluded_raw_at_threshold"])
        self.assertFalse(checks["every_load_bearing_test_excluded_conservative_at_threshold"])

    def test_mutation_down_lepton_data_breaks_the_portal_no_go(self) -> None:
        """If the down-quark and charged-lepton ratios agreed with M_e = phase x M_d^T, the portal no-go must not hold."""
        comparison = copy.deepcopy(self.fresh["data"])
        for row in comparison["tests_scale_free"]:
            if row["test"] == "(m_s/m_d)/(m_mu/m_e)":
                row["pull_raw_sigma"] = row["pull_conservative_sigma"] = 0.5
        section = nogo.portals_section(nogo.DATA, comparison=comparison)
        self.assertFalse(section["checks"]["portal_immune_tests_excluded_at_every_repository_r0"])
        self.assertFalse(section["findings"]["portal_fix_excluded_at_every_repository_r0"])
        self.assertEqual(section["findings"]["portal_fix_not_excluded_at"], sorted(nogo.EXPECTED_REPOSITORY_SCALES))

    def test_mutation_upstream_reports_fail_closed(self) -> None:
        cand = json.loads(nogo.CANDIDATE_JSON.read_text(encoding="utf-8"))
        hess = json.loads(nogo.EXACT_HESSIAN_JSON.read_text(encoding="utf-8"))
        cand["checks"]["H_linear_portals_are_zero"] = False
        hess["n_failed"] = 1
        checks = nogo.upstream_section(cand, hess)["checks"]
        self.assertFalse(checks["candidate_H_linear_portals_are_zero"])
        self.assertFalse(checks["exact_hessian_certified"])

    def test_mutation_pinned_closed_form_fails_closed(self) -> None:
        lattice = nogo.o28_lattice_binding()["_integer"]
        with mock.patch.object(nogo, "O28_R_NUMERATOR", "7962624*(13*r**2 + 7)**2"):
            closed = nogo.o28_closed_form(lattice)
        self.assertFalse(closed["matches_pinned_closed_form"])

    def test_mutation_missing_repository_scales_fail_closed(self) -> None:
        """Without the candidate's one-loop RG solutions every 'every repository r0' check must fail by name, never pass
        over an empty set or crash."""
        self.assertEqual(nogo.repository_scales({}), {})
        self.assertEqual(nogo.run_sm_masses([]), {})
        partial = dict(list(nogo.repository_scales().items())[:3])
        for scales in ({}, partial):
            data_checks = nogo.data_section(nogo.DATA, scales)["checks"]
            self.assertFalse(data_checks["repository_M_I_rows_present"])
            o28_checks = nogo.o28_section(nogo.DATA, scales)["checks"]
            self.assertFalse(o28_checks["repository_scales_present"])
            portal_checks = nogo.portals_section(nogo.DATA, scales)["checks"]
            self.assertFalse(portal_checks["repository_scales_present"])
            self.assertFalse(portal_checks["general_solver_reproduces_O28_alone_exactly"])  # no O28 section passed
        empty_o28 = nogo.o28_section(nogo.DATA, {})["checks"]
        self.assertFalse(empty_o28["theta_max_small_at_every_repository_r0"])
        self.assertFalse(empty_o28["t_b_repair_nonperturbative_at_every_repository_r0"])
        self.assertFalse(empty_o28["admixture_up_type_only_at_every_repository_r0"])
        empty_portals = nogo.portals_section(nogo.DATA, {})
        self.assertFalse(empty_portals["checks"]["every_H_linear_portal_theta_below_1e-3_at_every_repository_r0"])
        self.assertFalse(empty_portals["checks"]["portal_immune_tests_excluded_at_every_repository_r0"])
        self.assertFalse(empty_portals["findings"]["portal_fix_excluded_at_every_repository_r0"])

    def test_mutation_vectorlike_pattern_rank_drop_is_detected(self) -> None:
        fields = nogo.parse_model(self._model_text())["fields"]
        couplings = [
            {"fermions": row.split(".")[1:]} for row in self.fresh["contract"]["vectorlike_mass_couplings"]
        ]
        full = nogo.vectorlike_rank_certificate(fields, couplings)
        self.assertEqual(full["rank_at_integer_couplings"], 8)
        without_spectators = [row for row in couplings if "SpecB" not in row["fermions"]]
        self.assertEqual(nogo.vectorlike_rank_certificate(fields, without_spectators)["rank_at_integer_couplings"], 3)
        only_pbar = [row for row in couplings if "Pbar" in row["fermions"] or "SpecB" in row["fermions"]]
        self.assertEqual(nogo.vectorlike_rank_certificate(fields, only_pbar)["rank_at_integer_couplings"], 6)

    def test_mutation_h_degree_three_direction_breaks_the_even_potential(self) -> None:
        rows = nogo.census_rows()
        fake = dict(rows[0], direction_id="O99_B01_fake_H3", H_degree=3, parameters=["re::O99_B01_fake_H3"])
        with mock.patch.object(nogo, "census_rows", return_value=(*rows, fake)):
            checks = nogo.portal_section(r0_values=[Fraction(1, 5)])["checks"]
        self.assertFalse(checks["no_H_degree_3_live_direction"])
        self.assertFalse(checks["potential_even_in_H_on_the_witness"])

    def test_mutation_portal_pins_fail_closed(self) -> None:
        pinned = dict(nogo.PORTAL_DOUBLET_COUPLING)
        pinned[O15] = ("Phi210", 2)  # wrong r0 power
        with mock.patch.object(nogo, "PORTAL_DOUBLET_COUPLING", pinned):
            binding = nogo.portal_lattice_binding()
        self.assertFalse(binding["bound"])
        self.assertFalse(binding["patterns"][f"re::{O15}"]["bound"])
        pinned = dict(nogo.PORTAL_DOUBLET_COUPLING)
        pinned[O45_B01] = ("Phi210", 1)  # claims a doublet coupling that is absent
        with mock.patch.object(nogo, "PORTAL_DOUBLET_COUPLING", pinned):
            self.assertFalse(nogo.portal_lattice_binding()["bound"])

    def test_mutation_triplet_pins_and_hypercharge_sources_fail_closed(self) -> None:
        triplets = dict(nogo.PORTAL_TRIPLET_COUPLING)
        triplets[O15] = (("Phi210", 1),)  # hides the O(1) coupling to the 126bar (6,1,1)
        with mock.patch.object(nogo, "PORTAL_TRIPLET_COUPLING", triplets):
            binding = nogo.portal_lattice_binding()
        self.assertFalse(binding["bound"])
        self.assertFalse(binding["patterns"][f"re::{O15}"]["bound"])
        triplets = dict(nogo.PORTAL_TRIPLET_COUPLING)
        triplets[O28] = (("Sigma126bar", 1),)  # wrong r0 power
        with mock.patch.object(nogo, "PORTAL_TRIPLET_COUPLING", triplets):
            self.assertFalse(nogo.portal_lattice_binding()["patterns"][f"im::{O28}"]["bound"])
        sources = dict(nogo.PORTAL_DOUBLET_SOURCE)
        sources[O38] = "+"  # O38 acts on the Y = -1/2 component
        with mock.patch.object(nogo, "PORTAL_DOUBLET_SOURCE", sources):
            binding = nogo.portal_lattice_binding()
        self.assertFalse(binding["bound"])
        self.assertEqual(binding["patterns"][f"re::{O38}"]["doublet_source_hypercharge"], "-")

    def test_mutation_down_type_sigma_vev_is_detected(self) -> None:
        """A Sigma vector with a generic (15,2,2) component has down-type 16.16 entries: the selection-rule check fails."""
        start = nogo.SIGMA_SLICE.start
        down = nogo.induced_yukawa_content({start + 2 * 4: Fraction(1)})
        self.assertIn("d-dc", down["pairs"])
        self.assertIn("e-ec", down["pairs"])
        self.assertIs(down["up_type_only"], False)
        self.assertIs(nogo.induced_yukawa_content({})["up_type_only"], False)  # an empty response proves nothing
        sigma_std = nogo.candidate.sigma_std_raw_coordinates()
        response = {
            start + 2 * index + part: Fraction(int(value))
            for index, (re_value, im_value) in enumerate(zip(*sigma_std, strict=True))
            for part, value in ((0, re_value), (1, im_value))
            if value
        }
        self.assertEqual(nogo.induced_yukawa_content(response)["pairs"], ["nuc-nuc"])

    def test_mutation_colour_bracket_fails_closed(self) -> None:
        gram = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1, 4)]]
        h = [Fraction(2), Fraction(2)]
        result = nogo.colour_radius(gram, h)
        self.assertAlmostEqual(result["radius"], math.sqrt(2.0), places=12)
        self.assertIs(result["exact_bracket"], True)
        self.assertEqual(result["negative_modes_just_beyond"], 1)
        with mock.patch.object(nogo, "COLOUR_BRACKET_RELATIVE", -1.0e-3):  # brackets on the wrong side
            self.assertIs(nogo.colour_radius(gram, h)["exact_bracket"], False)
        self.assertIsNone(nogo.colour_radius([[Fraction(0)]], [Fraction(2)])["radius"])

    def test_mutation_neutral_ps_breaking_spurion_breaks_the_census(self) -> None:
        """A (B-L, T3R)-neutral Pati-Salam-breaking vev (a (15,1,1)-type Route A 210 orientation) evades the grading:
        the Sigma-pair statement must fail by name and the minimal PS-breaking Dirac dimension drops to 5."""
        contract = nogo.contract_section()
        table = nogo.eft_spurion_table(contract)
        table["Phi15"] = {"field": "Phi210[(15,1,1)]", "X": 0, "Z17": 0, "charge": (Fraction(0), Fraction(0)), "ps_breaking": True}
        section = nogo.lemma_eft_census_section(contract, {}, spurions=table)
        self.assertFalse(section["checks"]["every_ps_breaking_dirac_monomial_carries_a_sigma_pair"])
        self.assertFalse(section["checks"]["min_dimension_ps_breaking_dirac_is_6"])
        self.assertEqual(section["min_dimensions"]["ps_breaking_dirac"], 5)
        self.assertTrue(section["checks"]["grading_forces_sigma_balance_at_every_dimension"])  # Sigma balance itself holds

    def test_mutation_model_X_change_breaks_the_pinned_census(self) -> None:
        text = self._model_text()
        old = "{Delta126bar,  1, delta126bar, -126,  -2,"
        self.assertIn(old, text)
        contract = nogo.contract_section(text.replace(old, "{Delta126bar,  1, delta126bar, -126,  -4,"))
        section = nogo.lemma_eft_census_section(contract, {})
        self.assertFalse(section["checks"]["census_counts_to_dimension_12_pinned"])
        self.assertNotEqual(section["counts"], nogo.EFT_CENSUS_COUNTS)

    def test_mutation_su2r_breaking_mixing_breaks_s1(self) -> None:
        """The O15 map at the G3211 direction omega (SU(2)_R-breaking) as the bidoublet mixing: M_u is no longer
        proportional to M_d with a Yukawa-free ratio, and the equivariance hypothesis fails."""
        section = nogo.lemma_s1_g3221_section(nogo.lemma_su5_casimir_section(), mixing_map=nogo._omega_mixing)
        self.assertFalse(section["checks"]["one_light_bidoublet_Mu_proportional_Md_for_any_tan_beta"])
        self.assertFalse(section["checks"]["iota15_is_G3221_equivariant"])

    def test_mutation_wrong_down_doublet_breaks_casimir(self) -> None:
        section = nogo.lemma_su5_casimir_section(down_doublet_vector=nogo.Z5_VECTOR)
        self.assertFalse(section["checks"]["sigma_down_doublet_casimir_32_over_5_down_type_only"])
        self.assertEqual(section["casimir"]["w_d"], "12/5")
        self.assertEqual(section["pairs"]["w_d"], ["nu-nuc", "u-uc"])

    def test_mutation_S_coupled_unit_breaks_the_decoupling(self) -> None:
        original = nogo.exact_hessian.exact_unit_matrices

        def with_s_phi_unit(r0: Fraction, x0: Fraction) -> tuple[dict[str, Any], ...]:
            numerator = np.zeros((nogo.TOTAL_DIM, nogo.TOTAL_DIM), dtype=np.int64)
            s_index, phi_index = nogo.chart.S_SLICE.start, nogo.PHI_SLICE.start
            numerator[s_index, phi_index] = numerator[phi_index, s_index] = 1
            fake = {
                "name": "fake S-Phi unit",
                "weights": {},
                "source": "mutation",
                "hessian": (numerator, 1),
                "gradient": (np.zeros(nogo.TOTAL_DIM, dtype=np.int64), 1),
            }
            return (*original(r0, x0), fake)

        patterns = self.fresh["H_linear_portals"]["lattice_binding"]["patterns"]
        with mock.patch.object(nogo.exact_hessian, "exact_unit_matrices", side_effect=with_s_phi_unit):
            section = nogo.lemma_S_independence_section(patterns)
        self.assertFalse(section["checks"]["S_block_decoupled_in_every_binding_unit"])
        self.assertIn("fake S-Phi unit @ r0 = 1/5", section["units_coupling_S_to_other_blocks"])

    def test_mutation_sigma_overlapping_e_a_wedge_p_breaks_the_exact_O38_check(self) -> None:
        """A Sigma vev whose support meets e_0 ^ p (here e0 ^ e6789) gives O38 an H x S block: the exact form check
        (vii) must fail by name, while the lattice-pattern corroboration (not a check) is unaffected."""
        patterns = self.fresh["H_linear_portals"]["lattice_binding"]["patterns"]
        section = nogo.lemma_S_independence_section(patterns, o38_sigma_form={(0, 6, 7, 8, 9): (1, 0)})
        self.assertFalse(section["checks"]["O38_H_columns_have_no_S_block"])
        self.assertIs(section["O38_exact_form_blocks"]["H_by_S_block_zero_for_every_H_direction"], False)
        self.assertIs(section["O38_compiler_pattern_corroboration_not_a_check"], True)
        with mock.patch.object(nogo, "ps_singlet_form", return_value={(0, 1, 2, 3): (1, 0)}):
            blocks = nogo.o38_exact_form_blocks()
        self.assertIs(blocks["doublet_H_by_Sigma_block_zero_e_a_wedge_p_vanishes"], False)

    def test_mutation_symmetric_A_breaks_b1a(self) -> None:
        def symmetric(vector: Any) -> sympy.Matrix:
            return sympy.Matrix([[0, vector[2], vector[1]], [vector[2], 0, vector[0]], [vector[1], vector[0], 0]])

        checks = nogo.lemma_b1a_section(symmetric)["checks"]
        self.assertFalse(checks["adjugate_parity_decomposition"])
        self.assertFalse(checks["frobenius_pythagoras_TrAdagS_zero"])

    def test_mutation_fifteen_as_one_two_two_source_breaks_clebsch_plus_one(self) -> None:
        """omega6 ^ e_a (the T15-carrying (15,2,2) of a 120_H) fed as a (1,2,2) source: the oriented ratio to the 10 is
        no longer one constant."""
        section = nogo.lemma_122_clebsch_section(one_two_two_source=nogo._hypothetical_120_fifteen)
        self.assertFalse(section["checks"]["one_two_two_120_clebsch_equals_ten_clebsch"])
        self.assertEqual(section["oriented_ratio_120_over_10"], ["-3*I", "I"])

    def test_failed_check_changes_status(self) -> None:
        report = copy.deepcopy(self.fresh)
        report["n_failed"] = 1
        report["failures"] = ["light_doublet.H_block_decoupled_at_every_r0"]
        self.assertIn("NOT recorded", nogo._verdict(report))


if __name__ == "__main__":
    unittest.main()
