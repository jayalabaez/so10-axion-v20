#!/usr/bin/env python3
"""G1 contract-truncation scope: the SARAH-attested contract keeps 10 of 26 allowed fermion bilinears (v20; status-neutral).

User decision U5 (after the 2026-09-27 rescue study): G1 and the SARAH-attested model contract are scoped as the
attestation of a truncation.  G1 stays CLOSED, no gate status changes and no coupling is added (adding the omitted
couplings would be a new contract).  The gate ledger may cite the committed JSON as scope evidence only; it never
decides a gate.  Labels: EXACT (integer / fractions.Fraction arithmetic on models/SO10Z17AxionV20.m, no floats), BOUND
(read fail-closed from a committed certificate JSON, or recomputed through a committed module), ARGUMENT (reasoning with
its premises, not computed).

(model)   Own regex parser of ScalarFields / FermionFields / RealScalars / LagHC / LagNoHC [EXACT]: 14 multiplets (5
          scalars, 9 fermions; F x3, SpecS x5, SpecB x5), 11 LagHC terms (10 fermion bilinears and the scalar link
          kappaH H10.H10.S); every declared term is X and Z17 neutral.
(z17)     Z17 = X mod 17 for every contract field [EXACT], so every X-neutral monomial is Z17-neutral: the residual Z17
          adds no condition to the census or the kernels.
(census)  Every renormalizable fermion-fermion-scalar coupling allowed by SO(10) x U(1)_X x Z17 [EXACT]: 16x16 = 10 +
          120 + 126, 16x16bar = 1 + 45 + 210, 16bar x 16bar = 10 + 120 + 126bar, every scalar and its conjugate (Phi210
          is real).  26 allowed, 10 declared, 16 undeclared (74 generation-expanded); no bare 16.16bar mass and no
          Phi210 coupling; the undeclared ones are 8 of type 16.16, 6 of type 16.16bar (singlet-scalar mass terms) and
          2 of type 16bar.16bar.  The 16-label list refers to the model file's field basis (F, P and R are
          charge-degenerate); the truncation is basis independent by an exact dimension count: the undeclared
          couplings span 24 complex = 48 real generation-expanded dimensions, more than the 25 real dimensions of
          U(5) on the five X = 1 sixteens, the only gauge-covariant, linear, kinetic-term-preserving
          field-redefinition factor that mixes distinct multiplets.
(kernel)  U(1) kernels of the 14 multiplet charge vectors (the real Phi210 is forced to charge 0) [EXACT, Fraction
          RREF]: the 11 declared LagHC terms (with or without the 20 nontrivial scalar links of the committed G1
          symmetry census) and the 26 allowed couplings plus kappaH (with or without those links) have the same
          3-dimensional kernel span{X, PQ, Nspec} (X = PQ + 17 N17); the 26 couplings alone leave S's charge free
          (dimension 4).  F, P and R carry identical charges under every kernel element.
(pq)      PQ charges of exact_x_symmetry_consistency_gate_v20 [EXACT]: X - PQ = 17 N17 for every field, all 26
          couplings are PQ neutral, every X-neutral scalar monomial of degree <= 4 is PQ neutral, and the mixed
          SO(10)^2 anomaly coefficients (T(16) = T(16bar) = 2) are N(X) = 0, N(PQ) = -34, N(Nspec) = 0.
(lattice) [EXACT] The 11 LagHC charge vectors have rank 10 with the single relation Y10 + yQ + yR = lambdaR + lambdaQB +
          lambdaQR.  Each undeclared charge vector is an integer combination of declared ones (minimal-L1 certificate,
          verified exactly at assembly), as are P - F and R - F, so no multiplet-diagonal phase symmetry (continuous or
          discrete) of the declared Lagrangian protects the truncation.
(sector)  [EXACT, membership] Every undeclared coupling involves P, R, Pbar, Rbar or Qbar (the vectorlike sector) and
          none involves Q, SpecS or SpecB; exactly two (Phi17.F.Rbar, conj[Phi17].F.Pbar) are F-Rbar and F-Pbar mass
          mixings once Phi17 has its vev.
(cross)   [BOUND] The live g8_sm_pati_salam_flavour_nogo_v20.contract_section, the committed G8 flavour no-go JSON
          (status, 0 failed, the 16-label list, the model sha256 and its dimension-4 coupling lists), the committed G8
          structural-obstruction JSON (field-level census) and the committed G1 symmetry-census JSON (34 multidegrees,
          neutral under these charges).
(radiative) [ARGUMENT, not computed] No U(1) and no multiplet-diagonal phase symmetry protects the omitted couplings, so
          by naturalness the truncation is not expected to be stable under renormalisation; radiative generation, RG
          closure modulo field redefinitions and loop orders are not computed.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import re
import time
from collections.abc import Mapping, Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

import exact_x_symmetry_consistency_gate_v20 as xgate
import g8_sm_pati_salam_flavour_nogo_v20 as g8

ROOT = Path(__file__).resolve().parent
MODULE_NAME = "g1_contract_truncation_scope_v20"
MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
GATE = "G1"
OUT_JSON = ROOT / "G1_CONTRACT_TRUNCATION_SCOPE_V20.json"
OUT_MD = ROOT / "G1_CONTRACT_TRUNCATION_SCOPE_V20.md"
MODEL_FILE = ROOT / "models" / "SO10Z17AxionV20.m"
MODEL_FILE_REPOSITORY_PATH = "models/SO10Z17AxionV20.m"
G8_JSON = ROOT / "G8_SM_PATI_SALAM_FLAVOUR_NOGO_V20.json"
G8_STATUS_REQUIRED = "G8_SM_PATI_SALAM_WITNESS_FLAVOUR_NOGO__ROUTE_C_RECORDED__G8_OPEN"
STRUCTURAL_JSON = ROOT / "G8_SM_PATI_SALAM_STRUCTURAL_OBSTRUCTION_V20.json"
STRUCTURAL_STATUS_REQUIRED = (
    "G8_SM_PATI_SALAM_STRUCTURAL_OBSTRUCTION__SOS_CERTIFIED_FAMILY_FLAVOUR_DEAD__RECORDED__NO_GATE_CHANGE"
)
G1_CENSUS_JSON = ROOT / "G1_EXACT_DECLARED_SYMMETRY_CHARACTER_CENSUS_V20.json"
G1_CENSUS_STATUS_REQUIRED = "EXACT_GAUGED_U1X_RENORMALIZABLE_MULTIPLICITY_CENSUS_COMPLETE__COMPILER_REAUDIT_OPEN"
STATUS_RECORDED = "G1_CONTRACT_TRUNCATION_SCOPE__26_ALLOWED_10_DECLARED_16_UNDECLARED__EXACT__NO_GATE_CHANGE"
STATUS_INCOMPLETE = "G1_CONTRACT_TRUNCATION_SCOPE_INCOMPLETE__NO_GATE_CHANGE"
OVERALL_STATE_RECORDED = (
    "DECLARED_CONTRACT_IS_A_SYMMETRY_UNPROTECTED_TRUNCATION_EXACT__RADIATIVE_GENERATION_ARGUED_NOT_COMPUTED"
)
OVERALL_STATE_OPEN = "G1_CONTRACT_TRUNCATION_SCOPE_NOT_ESTABLISHED"

EXPECTED_ALLOWED = 26
EXPECTED_DECLARED = 10
EXPECTED_UNDECLARED = 16
EXPECTED_GENERATION_EXPANDED = 74
# Field-redefinition dimension count: the undeclared couplings span 24 complex generation-expanded directions; the only
# gauge-covariant field-redefinition factor mixing distinct multiplets is U(5) on (F x3, P, R).
EXPECTED_UNDECLARED_GENERATION_EXPANDED = 24
EXPECTED_MIXING_REDEFINITION_CLASSES = {"F.P.R": 25}
EXPECTED_UNDECLARED_LABELS = (
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
)
EXPECTED_F_MASS_MIXINGS = ("Phi17.F.Rbar", "conj[Phi17].F.Pbar")
VECTORLIKE_SECTOR_FIELDS = ("P", "R", "Pbar", "Rbar", "Qbar")
NON_TRUNCATED_FIELDS = ("Q", "SpecS", "SpecB")
EXPECTED_KERNEL_DIMENSIONS = {
    "declared_LagHC": 3,
    "declared_LagHC_plus_G1_scalar_links": 3,
    "allowed_26_plus_kappaH": 3,
    "allowed_26_plus_kappaH_plus_G1_scalar_links": 3,
    "allowed_26_without_scalar_links": 4,
}
DIMENSION_3_KERNELS = (
    "declared_LagHC",
    "declared_LagHC_plus_G1_scalar_links",
    "allowed_26_plus_kappaH",
    "allowed_26_plus_kappaH_plus_G1_scalar_links",
)
EXPECTED_DECLARED_RELATION = {"Y10": 1, "yQ": 1, "yR": 1, "lambdaR": -1, "lambdaQB": -1, "lambdaQR": -1}
EXPECTED_ANOMALY = {"T_16": 2, "N_X": 0, "N_PQ": -34, "N_spec": 0, "N17": 2}
EXPECTED_G1_MULTIDEGREES = 34
EXPECTED_G1_NONTRIVIAL_LINKS = 20
EXPECTED_SCALARS = ("Phi210", "Delta126bar", "H10", "S", "Phi17")
EXPECTED_FERMIONS = ("F", "P", "R", "SpecS", "SpecB", "Q", "Pbar", "Qbar", "Rbar")
EXPECTED_GENERATIONS = {"F": 3, "SpecS": 5, "SpecB": 5}
SPECTATOR_NUMBER = {"SpecS": 1, "SpecB": -1}
G8_LIGHT_STATE_PHRASE = "Yhat the symmetric 16.16.10_H coupling on the X = 1 sixteens"
G8_VECTORLIKE_RANK = 8

NEVER_TRUE_FLAGS = (
    "G1_reopened",
    "gate_status_changed",
    "couplings_added_to_contract",
    "radiative_generation_computed",
    "one_loop_generation_claimed_exact",
    "rg_closure_modulo_field_redefinitions_analysed",
    "falsifies_so10_contract",
    "changes_g8_flavour_conclusion",
)
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
EXPECTED_SECTION_COUNTS = {
    "model": 3,
    "z17": 1,
    "census": 7,
    "kernel": 7,
    "pq": 6,
    "lattice": 3,
    "sector": 3,
    "cross": 6,
    "scope": 1,
}
EXPECTED_N_CHECKS = 37
EXPECTED_CHECK_KEYS = (
    "model.parsed_14_multiplets_9_fermions_5_scalars",
    "model.LagHC_11_terms_10_fermion_bilinears_1_scalar_link",
    "model.declared_terms_X_and_Z17_neutral",
    "z17.equals_X_mod_17_for_every_field",
    "census.allowed_26",
    "census.declared_10_subset_of_allowed",
    "census.undeclared_16_exact_list",
    "census.generation_expanded_74",
    "census.no_bare_16_16bar_mass_and_no_Phi210_coupling",
    "census.undeclared_bilinear_classes_8_6_2",
    "census.undeclared_48_real_dimensions_exceed_mixing_field_redefinitions_25",
    "kernel.declared_LagHC_dimension_3",
    "kernel.declared_LagHC_plus_G1_links_dimension_3",
    "kernel.allowed_26_plus_kappaH_dimension_3",
    "kernel.allowed_26_plus_kappaH_plus_G1_links_dimension_3",
    "kernel.allowed_26_without_scalar_links_dimension_4",
    "kernel.every_dimension_3_kernel_equals_span_X_PQ_Nspec",
    "kernel.F_P_R_identical_under_every_kernel_element",
    "pq.charges_match_repository_contract",
    "pq.X_minus_PQ_equals_17_N17",
    "pq.all_26_allowed_couplings_PQ_neutral",
    "pq.all_16_undeclared_couplings_PQ_neutral",
    "pq.renormalizable_scalar_monomials_X_neutral_implies_PQ_neutral",
    "pq.anomaly_N_X_0_N_PQ_minus_34_N_spec_0",
    "lattice.declared_rows_rank_10_one_relation",
    "lattice.every_undeclared_is_an_integer_combination_of_declared_terms",
    "lattice.P_minus_F_and_R_minus_F_are_integer_combinations",
    "sector.every_undeclared_involves_P_R_Pbar_Rbar_or_Qbar",
    "sector.no_undeclared_involves_Q_SpecS_SpecB",
    "sector.exactly_two_F_16bar_mass_mixings",
    "cross.g8_live_contract_section_matches",
    "cross.g8_json_recorded_and_lists_match",
    "cross.g8_json_model_sha256_matches",
    "cross.g8_dimension4_lists_cover_all_allowed_couplings",
    "cross.structural_obstruction_json_census_matches",
    "cross.g1_census_json_bound_and_links_neutral",
    "scope.status_neutral_flags",
)
SECTION_ORDER = ("model", "z17", "census", "kernel", "pq", "lattice", "sector", "cross")
KERNEL_CHECK_NAMES = {
    "declared_LagHC": "declared_LagHC_dimension_3",
    "declared_LagHC_plus_G1_scalar_links": "declared_LagHC_plus_G1_links_dimension_3",
    "allowed_26_plus_kappaH": "allowed_26_plus_kappaH_dimension_3",
    "allowed_26_plus_kappaH_plus_G1_scalar_links": "allowed_26_plus_kappaH_plus_G1_links_dimension_3",
    "allowed_26_without_scalar_links": "allowed_26_without_scalar_links_dimension_4",
}

LABELS = {
    "EXACT": "integer / fractions.Fraction arithmetic on the parsed model file and the repository PQ table (no floats)",
    "BOUND": (
        "read fail-closed from a committed certificate JSON or recomputed through a committed module; any read error, "
        "missing key or mismatch makes the check False"
    ),
    "ARGUMENT": "reasoning recorded with its premises; not computed here",
}
Z17_STATEMENT = (
    "Z17 = X mod 17 for every contract field, so every X-neutral monomial is Z17-neutral: the residual Z17 adds no "
    "condition to the census or the kernels"
)
CENSUS_METHOD = (
    "combinations_with_replacement of the 9 fermion multiplets (model-file order) x every scalar option (each scalar "
    "and its conjugate; Phi210 is real); SO(10) singlet test from 16x16 = 10 + 120 + 126, 16x16bar = 1 + 45 + 210, "
    "16bar x 16bar = 10 + 120 + 126bar; U(1)_X and Z17 neutrality; a coupling is declared when a LagHC fermion "
    "bilinear has the same multiset of fields"
)
FIELD_REDEFINITION_STATEMENT = (
    "The 16-label list refers to the model file's field basis: F, P and R are charge-degenerate, so a U(5) rotation of "
    "the five X = 1 sixteens (F x3, P, R) can move couplings between declared and undeclared labels. The truncation "
    "is basis independent: the undeclared couplings span 24 complex = 48 real generation-expanded dimensions, while "
    "the only gauge-covariant (SO(10) x U(1)_X), linear, kinetic-term-preserving field-redefinition factor that "
    "mixes distinct multiplets is that U(5) (25 real dimensions); every other factor rotates the generations of a "
    "single multiplet or rephases it and maps the "
    "declared coupling space to itself. The orbit of the declared couplings (100 real dimensions) under all field "
    "redefinitions therefore has real dimension at most 100 + 25 = 125 < 148, the real dimension of all 26 couplings, "
    "so a generic Lagrangian with all 26 couplings is not field-redefinition-equivalent to a declared one"
)
FIELD_REDEFINITION_METHOD = (
    "fields grouped by (kind, SO(10) representation, X); complex scalars also with the conjugate of a field of the "
    "conjugate quantum numbers; a class with n generations in total has the redefinition group U(n) (O(n) for real "
    "scalars); a class is mixing when it contains two or more distinct multiplets; generation-expanded coupling counts "
    "as in the census (g(g+1)/2 for a repeated multiplet, g1 g2 otherwise), one complex coefficient each"
)
KERNEL_STATEMENT = (
    "The U(1) kernel of the 11 declared LagHC terms, with or without the G1 scalar links, and of all 26 allowed "
    "couplings plus kappaH (with or without the G1 scalar links) is the same 3-dimensional span of X, PQ and spectator "
    "number (X = PQ + 17 N17); without any scalar link the 26 couplings leave S's charge free (dimension 4). Every "
    "undeclared coupling is therefore neutral under every U(1) of the declared Lagrangian, and F, P and R carry "
    "identical charges"
)
KERNEL_GENERATION_NOTE = (
    "charges are per multiplet (all generations of F, SpecS and SpecB share one charge); generation-wise phases are "
    "covered by the lattice section (with generic flavour matrices every generation-wise phase symmetry is "
    "multiplet-diagonal)"
)
KERNEL_REAL_FIELD_CONSTRAINT = (
    "Phi210 is a real field, so no U(1) acts on it: the row e_Phi210 is added to every system"
)
LATTICE_STATEMENT = (
    "Each undeclared coupling's charge vector is an integer combination of the 11 declared LagHC monomials (verified "
    "exactly), so every phase rotation of the 14 multiplets (continuous or discrete) that leaves the declared terms "
    "invariant also leaves the undeclared coupling invariant; with generic flavour matrices every generation-wise phase "
    "symmetry is multiplet-diagonal"
)
LATTICE_SPURION_NOTE = (
    "the combination is the spurion monomial of declared couplings with the coupling's charges (a negative coefficient "
    "is a complex conjugate); its degree is a selection-rule order only, not a computed loop order"
)
LATTICE_METHOD = (
    "rational particular solution c0 of sum_k c_k D_k = target (D_k the 11 LagHC charge vectors, Fraction RREF) plus "
    "integer multiples of the primitive relation r; L1(c0 + t r) is convex in t, every integer t between the extreme "
    "breakpoints -c_i/r_i is scanned and the minimal-L1 integral solution is kept (tied minima differ by multiples of "
    "the relation; the tie is broken by the lexicographically largest coefficient vector in LagHC order, i.e. the "
    "largest Y10 coefficient); every certificate is re-verified exactly at assembly"
)
SECTOR_STATEMENT = (
    "Every undeclared coupling involves at least one of P, R, Pbar, Rbar, Qbar (the vectorlike sector), none involves "
    "Q, SpecS or SpecB, and exactly two (Phi17.F.Rbar, conj[Phi17].F.Pbar) are F-Rbar and F-Pbar mass mixings once "
    "Phi17 has its vev; mass-eigenstate composition is not computed here"
)
PQ_STATEMENT = (
    "All 26 allowed couplings are PQ neutral and every X-neutral renormalizable scalar monomial is PQ neutral, so PQ is "
    "accidental at the renormalizable level and the truncation changes neither the PQ symmetry nor its anomaly N = -34"
)
PQ_SOURCE = (
    "exact_x_symmetry_consistency_gate_v20.EXPECTED_SCALAR_CHARGES and EXPECTED_FERMION_SECTORS ((PQ, X) pairs; "
    "fermion sectors keyed by SO(10) representation and X)"
)
PQ_ANOMALY_NOTE = (
    "mixed SO(10)^2 x U(1) coefficient N = sum over fermion multiplets of generations x T(16) x q with T(16) = T(16bar) "
    "= 2 (the colour index of a 16 in units T(3) = 1/2)"
)
G8_COVERAGE_STATEMENT = (
    "The committed G8 flavour analysis lists every allowed coupling (contract.H10_yukawas, Delta126bar_yukawas, "
    "vectorlike_mass_couplings, sixteenbar_pair_couplings include the 16 undeclared ones) and its light-state lemma uses "
    "the general 16.16.10_H coupling on the X = 1 sixteens, so at the dimension-4 level the truncation does not lift the "
    "G8 witness-branch flavour obstruction (its rank-8 light-state assumption carries over)"
)
RADIATIVE_STATEMENT = (
    "No U(1) and no multiplet-diagonal phase symmetry of the declared Lagrangian protects the 16 omitted couplings "
    "(EXACT, kernel and lattice sections), so by naturalness the truncation is not expected to be stable under "
    "renormalisation. This is an argument: radiative generation is not computed here"
)
RADIATIVE_ONE_LOOP_EXAMPLE = (
    "In the model file's field basis the one-loop Yukawa RGE contains (Y Y^dagger Y)_PP \u2283 lambda_P Y10^* lambda_P for "
    "the 16.16.10_H matrix Y on the X = 1 sixteens; this comes from the fermion wave-function (P-F kinetic-mixing) term "
    "and is basis dependent (the vertex term with a holomorphically coupled complex H10 cancels). SO(10) group factors "
    "are not computed"
)
RADIATIVE_NOT_CLAIMED = [
    "that any omitted coupling is generated at one loop with a nonzero coefficient",
    "RG closure of the declared Lagrangian modulo field redefinitions",
    "the loop order at which each omitted coupling first appears",
    "the phenomenology of the omitted couplings",
]
SCOPE = {
    "claimed": [
        "EXACT: census 26 allowed / 10 declared / 16 undeclared (74 generation-expanded), Z17 = X mod 17",
        "EXACT: dimension count: the undeclared couplings (48 real generation-expanded dimensions) exceed the mixing "
        "field redefinitions (U(5) on F x3, P, R: 25), so the truncation is not a basis choice (the 16-label list "
        "refers to the model file's field basis)",
        "EXACT: U(1) kernels (dimension 3 = span{X, PQ, Nspec}; 4 without scalar links) and F/P/R charge degeneracy",
        "EXACT: PQ neutrality of all 26 couplings, accidental PQ at the renormalizable level, N = -34",
        "EXACT: integer-lattice certificates for the 16 undeclared couplings and for P-F, R-F",
        "EXACT: vectorlike-sector membership and the two F-16bar mass mixings",
        "BOUND: equality with the committed G8 contract census and structural-obstruction census; G8 dimension-4 coverage",
    ],
    "argued_not_computed": ["radiative generation of the omitted couplings (radiative.statement)"],
    "not_claimed": [
        "no coupling is added (adding them would be a new contract)",
        "no gate status changes; G1 stays CLOSED and is scoped as the attestation of a truncation",
        "no symmetry beyond multiplet-diagonal phase rotations is analysed",
        "no exclusion of the SO(10) contract",
    ],
}
VERDICT_RECORDED = (
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

FIELD_RE = re.compile(r"(ScalarFields|FermionFields)\[\[(\d+)\]\]\s*=\s*\{([^{}]*)\};")
PHASE_RE = re.compile(r"Exp\[2\*Pi\*I\*(\d+)/(\d+)\]")
REAL_RE = re.compile(r"RealScalars\s*=\s*\{([^{}]*)\};")
CONJ_RE = re.compile(r"conj\[(\w+)\]")
NAME_RE = re.compile(r"\w+")
SO10_CONJUGATE = {"1": "1", "10": "10", "45": "45", "120": "120", "210": "210", "126": "-126", "-126": "126",
                  "16": "-16", "-16": "16"}
BILINEAR_CONTENT = {
    ("16", "16"): ("10", "120", "126"),
    ("-16", "16"): ("1", "45", "210"),
    ("-16", "-16"): ("10", "120", "-126"),
}
BILINEAR_CLASS = {("16", "16"): "16.16", ("-16", "16"): "16.16bar", ("-16", "-16"): "16bar.16bar"}
EXPECTED_UNDECLARED_CLASS_COUNTS = {"16.16": 8, "16.16bar": 6, "16bar.16bar": 2}
SINGLET_SCALARS = ("S", "Phi17")
G1_LETTERS = {
    "P": ("Phi210", 1),
    "H": ("H10", 1),
    "Hb": ("H10", -1),
    "D": ("Delta126bar", 1),
    "Db": ("Delta126bar", -1),
    "S": ("S", 1),
    "Sb": ("S", -1),
    "X": ("Phi17", 1),
    "Xb": ("Phi17", -1),
}
SCALAR_MONOMIAL_MAX_DEGREE = 4


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return int(value) if value.denominator == 1 else str(value)
    return value


def json_roundtrip(value: Any) -> Any:
    return json.loads(json.dumps(_jsonable(value), sort_keys=True))


def _dig(value: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(value, Mapping) or key not in value:
            return None
        value = value[key]
    return value


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _sha256_lf(text: str) -> str:
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Exact linear algebra over Q (fractions.Fraction)
# ---------------------------------------------------------------------------


def _rref(rows: Sequence[Sequence[Any]], ncols: int) -> tuple[list[list[Fraction]], list[int]]:
    matrix = [[Fraction(value) for value in row] for row in rows]
    pivots: list[int] = []
    rank = 0
    for column in range(ncols):
        pivot = next((index for index in range(rank, len(matrix)) if matrix[index][column] != 0), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inverse = 1 / matrix[rank][column]
        matrix[rank] = [value * inverse for value in matrix[rank]]
        for index in range(len(matrix)):
            if index != rank and matrix[index][column] != 0:
                factor = matrix[index][column]
                matrix[index] = [a - factor * b for a, b in zip(matrix[index], matrix[rank])]
        pivots.append(column)
        rank += 1
    return matrix, pivots


def _rank(rows: Sequence[Sequence[Any]], ncols: int) -> int:
    return len(_rref(rows, ncols)[1]) if rows else 0


def _nullspace(rows: Sequence[Sequence[Any]], ncols: int) -> list[list[Fraction]]:
    matrix, pivots = _rref(rows, ncols) if rows else ([], [])
    basis = []
    for free in (column for column in range(ncols) if column not in pivots):
        vector = [Fraction(0)] * ncols
        vector[free] = Fraction(1)
        for index, column in enumerate(pivots):
            vector[column] = -matrix[index][free]
        basis.append(vector)
    return basis


def _primitive(vector: Sequence[Fraction]) -> list[int]:
    denominators = [Fraction(value).denominator for value in vector]
    scale = 1
    for denominator in denominators:
        scale = scale * denominator // math.gcd(scale, denominator)
    integers = [int(Fraction(value) * scale) for value in vector]
    divisor = 0
    for value in integers:
        divisor = math.gcd(divisor, abs(value))
    if divisor == 0:
        return integers
    integers = [value // divisor for value in integers]
    first = next((value for value in integers if value != 0), 0)
    return [-value for value in integers] if first < 0 else integers


def _dot(left: Sequence[Any], right: Sequence[Any]) -> Fraction:
    return sum((Fraction(a) * Fraction(b) for a, b in zip(left, right)), Fraction(0))


# ---------------------------------------------------------------------------
# (model) Parser of the SARAH model file
# ---------------------------------------------------------------------------


def _block(text: str, name: str, fields: Mapping[str, Any]) -> list[dict[str, Any]]:
    match = re.search(name + r"\s*=\s*-\((.*?)\);", text, re.S)
    if match is None:
        raise ValueError(f"{name} block not found")
    terms = []
    for line in match.group(1).splitlines():
        stripped = line.strip().lstrip("+").strip()
        if not stripped:
            continue
        coefficient, product = stripped.split(None, 1)
        product = product.strip()
        factors = []
        for factor in product.split("."):
            conj = CONJ_RE.fullmatch(factor)
            field = conj.group(1) if conj else factor
            if not NAME_RE.fullmatch(field) or field not in fields:
                raise ValueError(f"unknown field {factor!r} in {name}")
            factors.append((field, -1 if conj else 1))
        terms.append({"coefficient": coefficient, "monomial": product, "factors": factors})
    return terms


def parse_model(text: str) -> dict[str, Any]:
    fields: dict[str, dict[str, Any]] = {}
    for kind, _index, body in FIELD_RE.findall(text):
        parts = [part.strip() for part in body.split(",")]
        if len(parts) != 6:
            raise ValueError(f"unexpected field row {body!r}")
        name, generations, component, rep, xcharge, phase = parts
        if phase == "1":
            z17 = 0
        else:
            match = PHASE_RE.fullmatch(phase)
            if match is None or int(match.group(2)) != 17:
                raise ValueError(f"unexpected Z17 phase {phase!r}")
            z17 = int(match.group(1)) % 17
        if rep not in SO10_CONJUGATE:
            raise ValueError(f"unexpected SO(10) representation {rep!r}")
        fields[name] = {
            "kind": "scalar" if kind == "ScalarFields" else "fermion",
            "so10": rep,
            "X": int(xcharge),
            "Z17": z17,
            "generations": int(generations),
            "component": component,
        }
    real_match = REAL_RE.search(text)
    real_components = {item.strip() for item in real_match.group(1).split(",")} if real_match else set()
    for row in fields.values():
        row["real"] = row["component"] in real_components
    return {"fields": fields, "LagHC": _block(text, "LagHC", fields), "LagNoHC": _block(text, "LagNoHC", fields)}


def _scalar_label(name: str, sign: int) -> str:
    return name if sign > 0 else f"conj[{name}]"


def _term_kind(fields: Mapping[str, Any], factors: Sequence[tuple[str, int]]) -> str:
    kinds = [fields[name]["kind"] for name, _sign in factors]
    if kinds.count("fermion") == 2 and kinds.count("scalar") == 1 and all(
        sign > 0 for name, sign in factors if fields[name]["kind"] == "fermion"
    ):
        return "fermion_bilinear"
    if kinds.count("fermion") == 0:
        return "scalar_link"
    return "other"


def _charge_sum(fields: Mapping[str, Any], factors: Sequence[tuple[str, int]], key: str) -> int:
    return sum(sign * int(fields[name][key]) for name, sign in factors)


def _vector(order: Sequence[str], factors: Sequence[tuple[str, int]]) -> list[int]:
    index = {name: position for position, name in enumerate(order)}
    vector = [0] * len(order)
    for name, sign in factors:
        vector[index[name]] += sign
    return vector


def _monomial_factors(monomial: str) -> list[tuple[str, int]]:
    factors = []
    for factor in monomial.split("."):
        conj = CONJ_RE.fullmatch(factor)
        factors.append((conj.group(1), -1) if conj else (factor, 1))
    return factors


def _coupling_factors(row: Mapping[str, Any]) -> list[tuple[str, int]]:
    scalar = str(row["scalar"])
    conj = CONJ_RE.fullmatch(scalar)
    first = (conj.group(1), -1) if conj else (scalar, 1)
    return [first, (str(row["fermions"][0]), 1), (str(row["fermions"][1]), 1)]


def model_section(text: str, parsed: Mapping[str, Any]) -> dict[str, Any]:
    fields = parsed["fields"]
    scalars = [name for name, row in fields.items() if row["kind"] == "scalar"]
    fermions = [name for name, row in fields.items() if row["kind"] == "fermion"]

    def record(term: Mapping[str, Any], with_kind: bool) -> dict[str, Any]:
        row = {
            "coefficient": term["coefficient"],
            "monomial": term["monomial"],
            "X_sum": _charge_sum(fields, term["factors"], "X"),
            "Z17_sum_mod_17": _charge_sum(fields, term["factors"], "Z17") % 17,
        }
        if with_kind:
            row["kind"] = _term_kind(fields, term["factors"])
        return row

    laghc = [record(term, True) for term in parsed["LagHC"]]
    lagnohc = [record(term, False) for term in parsed["LagNoHC"]]
    kinds = [row["kind"] for row in laghc]
    generations_ok = all(
        int(fields[name]["generations"]) == EXPECTED_GENERATIONS.get(name, 1) for name in fields
    )
    real_ok = sorted(name for name, row in fields.items() if row["real"]) == ["Phi210"]
    checks = {
        "parsed_14_multiplets_9_fermions_5_scalars": len(fields) == 14
        and tuple(scalars) == EXPECTED_SCALARS
        and tuple(fermions) == EXPECTED_FERMIONS
        and generations_ok
        and real_ok,
        "LagHC_11_terms_10_fermion_bilinears_1_scalar_link": len(laghc) == 11
        and kinds.count("fermion_bilinear") == 10
        and kinds.count("scalar_link") == 1
        and kinds.count("other") == 0,
        "declared_terms_X_and_Z17_neutral": bool(laghc)
        and all(row["X_sum"] == 0 and row["Z17_sum_mod_17"] == 0 for row in laghc + lagnohc),
    }
    return {
        "file": MODEL_FILE_REPOSITORY_PATH,
        "text_sha256_lf": _sha256_lf(text),
        "fields": {
            name: {key: row[key] for key in ("kind", "so10", "X", "Z17", "generations", "real")}
            for name, row in fields.items()
        },
        "declared_LagHC_terms": laghc,
        "declared_LagNoHC_terms": lagnohc,
        "checks": checks,
    }


# ---------------------------------------------------------------------------
# (z17, census) The complete allowed set of renormalizable fermion bilinears
# ---------------------------------------------------------------------------


def census_rows(parsed: Mapping[str, Any]) -> dict[str, Any]:
    fields = parsed["fields"]
    fermions = [name for name, row in fields.items() if row["kind"] == "fermion"]
    scalars = [name for name, row in fields.items() if row["kind"] == "scalar"]
    options = []
    for name in scalars:
        options.append((name, 1))
        if not fields[name]["real"]:
            options.append((name, -1))
    declared: dict[tuple[str, ...], str] = {}
    declared_bilinears = 0
    for term in parsed["LagHC"]:
        if _term_kind(fields, term["factors"]) != "fermion_bilinear":
            continue
        declared_bilinears += 1
        declared[tuple(sorted(_scalar_label(name, sign) for name, sign in term["factors"]))] = term["coefficient"]
    allowed = []
    bare = []
    removed_by_z17 = []
    for first, second in itertools.combinations_with_replacement(fermions, 2):
        key = tuple(sorted((fields[first]["so10"], fields[second]["so10"])))
        content = BILINEAR_CONTENT.get(key)
        if content is None:
            continue
        x_pair = fields[first]["X"] + fields[second]["X"]
        z_pair = fields[first]["Z17"] + fields[second]["Z17"]
        if "1" in content and x_pair == 0 and z_pair % 17 == 0:
            bare.append(f"{first}.{second}")
        for name, sign in options:
            rep = fields[name]["so10"] if sign > 0 else SO10_CONJUGATE[fields[name]["so10"]]
            if SO10_CONJUGATE[rep] not in content:
                continue
            if x_pair + sign * fields[name]["X"] != 0:
                continue
            label = f"{_scalar_label(name, sign)}.{first}.{second}"
            if (z_pair + sign * fields[name]["Z17"]) % 17 != 0:
                removed_by_z17.append(label)
                continue
            multiset = tuple(sorted([_scalar_label(name, sign), first, second]))
            allowed.append(
                {
                    "coupling": label,
                    "fermions": [first, second],
                    "scalar": _scalar_label(name, sign),
                    "scalar_rep": rep,
                    "bilinear_class": BILINEAR_CLASS[key],
                    "declared": multiset in declared,
                    "declared_coefficient": declared.get(multiset),
                }
            )
    allowed_multisets = {tuple(sorted([row["scalar"], *row["fermions"]])) for row in allowed}
    declared_outside = sorted(".".join(key) for key in declared if key not in allowed_multisets)
    return {
        "allowed": allowed,
        "bare": bare,
        "removed_by_z17": removed_by_z17,
        "declared_bilinears": declared_bilinears,
        "declared_outside_allowed": declared_outside,
    }


def z17_section(parsed: Mapping[str, Any], rows: Mapping[str, Any]) -> dict[str, Any]:
    fields = parsed["fields"]
    per_field = {
        name: {"X": row["X"], "Z17": row["Z17"], "X_mod_17": row["X"] % 17} for name, row in fields.items()
    }
    equal = bool(per_field) and all(row["Z17"] == row["X_mod_17"] for row in per_field.values())
    return {
        "label": "EXACT",
        "per_field": per_field,
        "Z17_equals_X_mod_17_for_every_field": equal,
        "X_allowed_couplings_removed_by_Z17": list(rows["removed_by_z17"]),
        "statement": Z17_STATEMENT,
        "checks": {"equals_X_mod_17_for_every_field": equal and not rows["removed_by_z17"]},
    }


def census_section(parsed: Mapping[str, Any], rows: Mapping[str, Any]) -> dict[str, Any]:
    fields = parsed["fields"]
    allowed = rows["allowed"]
    declared = sorted(row["coupling"] for row in allowed if row["declared"])
    undeclared = sorted(row["coupling"] for row in allowed if not row["declared"])
    generation_expanded = 0
    for row in allowed:
        first, second = row["fermions"]
        g1, g2 = int(fields[first]["generations"]), int(fields[second]["generations"])
        generation_expanded += g1 * (g1 + 1) // 2 if first == second else g1 * g2
    phi210 = sorted(row["coupling"] for row in allowed if row["scalar"] in ("Phi210", "conj[Phi210]"))
    class_counts = {name: 0 for name in EXPECTED_UNDECLARED_CLASS_COUNTS}
    for row in allowed:
        if not row["declared"]:
            class_counts[row["bilinear_class"]] = class_counts.get(row["bilinear_class"], 0) + 1
    redefinitions = field_redefinition_count(fields, allowed)
    checks = {
        "allowed_26": len(allowed) == EXPECTED_ALLOWED,
        "declared_10_subset_of_allowed": len(declared) == EXPECTED_DECLARED
        and rows["declared_bilinears"] == EXPECTED_DECLARED
        and not rows["declared_outside_allowed"],
        "undeclared_16_exact_list": undeclared == list(EXPECTED_UNDECLARED_LABELS),
        "generation_expanded_74": generation_expanded == EXPECTED_GENERATION_EXPANDED,
        "no_bare_16_16bar_mass_and_no_Phi210_coupling": not rows["bare"] and not phi210,
        "undeclared_bilinear_classes_8_6_2": class_counts == EXPECTED_UNDECLARED_CLASS_COUNTS,
        "undeclared_48_real_dimensions_exceed_mixing_field_redefinitions_25": bool(
            redefinitions["undeclared_complex_dimension"] == EXPECTED_UNDECLARED_GENERATION_EXPANDED
            and redefinitions["declared_complex_dimension"] + redefinitions["undeclared_complex_dimension"]
            == generation_expanded
            and {key: row["real_dimension"] for key, row in redefinitions["mixing_classes"].items()}
            == EXPECTED_MIXING_REDEFINITION_CLASSES
            and redefinitions["undeclared_real_dimension"] > redefinitions["mixing_redefinition_real_dimension"]
            and redefinitions["declared_orbit_real_dimension_bound"] < redefinitions["all_couplings_real_dimension"]
        ),
    }
    return {
        "label": "EXACT",
        "method": CENSUS_METHOD,
        "allowed": allowed,
        "allowed_count": len(allowed),
        "declared": declared,
        "declared_count": len(declared),
        "declared_bilinears_outside_allowed_set": list(rows["declared_outside_allowed"]),
        "undeclared": undeclared,
        "undeclared_count": len(undeclared),
        "generation_expanded_count": generation_expanded,
        "bare_16_16bar_masses": list(rows["bare"]),
        "Phi210_couplings": phi210,
        "undeclared_class_counts": class_counts,
        "field_redefinitions": redefinitions,
        "checks": checks,
    }


def field_redefinition_count(fields: Mapping[str, Any], allowed: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Exact dimension count: can field redefinitions map the general 26-coupling Lagrangian into the declared form?

    The gauge-covariant redefinitions are unitary rotations among fields of equal (kind, SO(10) representation, X)
    (complex scalars also with the conjugate of a field of conjugate quantum numbers).  A class holding a single multiplet
    rotates its generations or rephases it and maps every declared monomial to the same monomial, so only classes with
    two or more distinct multiplets can mix declared and undeclared couplings.  If the undeclared real dimension exceeds
    the real dimension of those mixing factors, the orbit of the declared coupling space has positive codimension.
    """

    def generation_count(row: Mapping[str, Any]) -> int:
        first, second = row["fermions"]
        g1, g2 = int(fields[first]["generations"]), int(fields[second]["generations"])
        return g1 * (g1 + 1) // 2 if first == second else g1 * g2

    declared = sum(generation_count(row) for row in allowed if row["declared"])
    undeclared = sum(generation_count(row) for row in allowed if not row["declared"])
    classes: dict[tuple[str, str, int], list[str]] = {}
    for name, row in fields.items():
        key = (str(row["kind"]), str(row["so10"]), int(row["X"]))
        if row["kind"] == "scalar" and not row["real"]:
            conjugate = (str(row["kind"]), SO10_CONJUGATE.get(str(row["so10"]), str(row["so10"])), -int(row["X"]))
            key = min(key, conjugate)
        classes.setdefault(key, []).append(name)
    mixing: dict[str, dict[str, Any]] = {}
    for key, names in classes.items():
        if len(names) < 2:
            continue
        n = sum(int(fields[name]["generations"]) for name in names)
        real = all(bool(fields[name]["real"]) for name in names)
        mixing[".".join(names)] = {
            "fields": list(names),
            "kind": key[0],
            "so10": key[1],
            "X": key[2],
            "total_generations": n,
            "group": f"O({n})" if real else f"U({n})",
            "real_dimension": n * (n - 1) // 2 if real else n * n,
        }
    mixing_dimension = sum(row["real_dimension"] for row in mixing.values())
    return {
        "label": "EXACT",
        "method": FIELD_REDEFINITION_METHOD,
        "declared_complex_dimension": declared,
        "undeclared_complex_dimension": undeclared,
        "declared_real_dimension": 2 * declared,
        "undeclared_real_dimension": 2 * undeclared,
        "all_couplings_real_dimension": 2 * (declared + undeclared),
        "mixing_classes": mixing,
        "mixing_redefinition_real_dimension": mixing_dimension,
        "declared_orbit_real_dimension_bound": 2 * declared + mixing_dimension,
        "statement": FIELD_REDEFINITION_STATEMENT,
    }


# ---------------------------------------------------------------------------
# (pq) Repository PQ charges, accidental PQ and anomaly coefficients
# ---------------------------------------------------------------------------


def repository_pq_charges(fields: Mapping[str, Mapping[str, Any]]) -> tuple[dict[str, int], bool]:
    """PQ charge of every multiplet from the stdlib-only exact X-symmetry gate constants ((PQ, X) pairs); the bool says
    whether the table matches the model file (scalar X values, fermion sectors and their multiplicities)."""
    charges: dict[str, int] = {}
    consistent = set(xgate.EXPECTED_SCALAR_CHARGES) == {n for n, r in fields.items() if r["kind"] == "scalar"}
    for name, row in fields.items():
        if row["kind"] == "scalar":
            entry = xgate.EXPECTED_SCALAR_CHARGES.get(name)
            if entry is None or int(entry[1]) != int(row["X"]):
                consistent = False
                continue
            charges[name] = int(entry[0])
        else:
            matches = [s for s in xgate.EXPECTED_FERMION_SECTORS if s[0] == row["so10"] and int(s[1][1]) == int(row["X"])]
            if len(matches) != 1:
                consistent = False
                continue
            charges[name] = int(matches[0][1][0])
    for rep, (_pq, xcharge), multiplicity, _note in xgate.EXPECTED_FERMION_SECTORS:
        total = sum(
            int(row["generations"])
            for row in fields.values()
            if row["kind"] == "fermion" and row["so10"] == rep and int(row["X"]) == int(xcharge)
        )
        consistent = consistent and total == int(multiplicity)
    return charges, bool(consistent)


def _scalar_monomial_check(fields: Mapping[str, Any], pq: Mapping[str, int]) -> dict[str, Any]:
    letters = list(G1_LETTERS)
    tuples = 0
    x_neutral = 0
    violations = []
    for degree in range(SCALAR_MONOMIAL_MAX_DEGREE + 1):
        for combination in itertools.combinations_with_replacement(letters, degree):
            tuples += 1
            x_sum = sum(G1_LETTERS[letter][1] * int(fields[G1_LETTERS[letter][0]]["X"]) for letter in combination)
            if x_sum != 0:
                continue
            x_neutral += 1
            pq_sum = sum(G1_LETTERS[letter][1] * int(pq.get(G1_LETTERS[letter][0], 0)) for letter in combination)
            if pq_sum != 0:
                violations.append(" ".join(combination))
    return {"count_tuples": tuples, "X_neutral_tuples": x_neutral, "PQ_violations": violations}


# ---------------------------------------------------------------------------
# (lattice) Integer certificates
# ---------------------------------------------------------------------------


def integer_certificate(declared: Sequence[Sequence[int]], target: Sequence[int]) -> dict[str, Any] | None:
    """Minimal-L1 integer c with sum_k c_k declared_k = target, or None.  Supports a declared lattice with at most one
    relation (the contract's case); the relation family c1 + t r (r primitive, t integer) is scanned over every integer
    between the extreme breakpoints, which contains the minimum of the convex function L1(t)."""
    n, m = len(target), len(declared)
    augmented = [[Fraction(declared[k][i]) for k in range(m)] + [Fraction(target[i])] for i in range(n)]
    matrix, pivots = _rref(augmented, m)
    if any(all(value == 0 for value in row[:m]) and row[m] != 0 for row in matrix):
        return None
    particular = [Fraction(0)] * m
    for index, column in enumerate(pivots):
        particular[column] = matrix[index][m]
    relations = _nullspace([row[:m] for row in augmented], m)
    if len(relations) > 1:
        return None
    if not relations:
        if any(value.denominator != 1 for value in particular):
            return None
        best = [int(value) for value in particular]
        scan = {"relation_used": False, "scan_range": None, "scan_covers_breakpoints": True, "minimal_ties": 1}
    else:
        relation = _primitive(relations[0])
        pivot = min((i for i in range(m) if relation[i] != 0), key=lambda i: (abs(relation[i]), i))
        start = None
        base = math.floor(particular[pivot])
        for k in range(base - abs(relation[pivot]), base + abs(relation[pivot]) + 1):
            t = (Fraction(k) - particular[pivot]) / relation[pivot]
            candidate = [particular[i] + t * relation[i] for i in range(m)]
            if all(value.denominator == 1 for value in candidate):
                start = [int(value) for value in candidate]
                break
        if start is None:
            return None
        breakpoints = [Fraction(-start[i], relation[i]) for i in range(m) if relation[i] != 0]
        low, high = math.floor(min(breakpoints)), math.ceil(max(breakpoints))
        covers = all(low <= value <= high for value in breakpoints)
        scored = []
        for t in range(low, high + 1):
            candidate = [start[i] + t * relation[i] for i in range(m)]
            scored.append((sum(abs(value) for value in candidate), t, candidate))
        minimum = min(score for score, _t, _c in scored)
        ties = [entry for entry in scored if entry[0] == minimum]
        best = max(ties, key=lambda entry: entry[2])[2]
        scan = {"relation_used": True, "scan_range": [low, high], "scan_covers_breakpoints": covers,
                "minimal_ties": len(ties)}
    check = [sum(best[k] * declared[k][i] for k in range(m)) for i in range(n)]
    if check != list(target):
        return None
    return {"coefficients": best, "degree_l1": sum(abs(value) for value in best), **scan}


def lattice_section(
    order: Sequence[str],
    declared_terms: Sequence[Mapping[str, Any]],
    undeclared_vectors: Mapping[str, Sequence[int]],
) -> dict[str, Any]:
    names = [str(term["coefficient"]) for term in declared_terms]
    vectors = [list(term["vector"]) for term in declared_terms]
    rank = _rank(vectors, len(order))
    relations = _nullspace([list(column) for column in zip(*vectors)], len(vectors)) if vectors else []
    relation = {}
    if len(relations) == 1:
        primitive = _primitive(relations[0])
        relation = {name: value for name, value in zip(names, primitive) if value != 0}

    def certificate(target: Sequence[int]) -> dict[str, Any] | None:
        result = integer_certificate(vectors, target)
        if result is None:
            return None
        return {
            "combination": {name: value for name, value in zip(names, result["coefficients"]) if value != 0},
            "degree_l1": result["degree_l1"],
            "_scan": {key: result[key] for key in ("scan_range", "scan_covers_breakpoints", "minimal_ties")},
        }

    certificates = {}
    scans = {}
    for label in sorted(undeclared_vectors):
        result = certificate(undeclared_vectors[label])
        if result is not None:
            scans[label] = result.pop("_scan")
            certificates[label] = result
    index = {name: position for position, name in enumerate(order)}
    differences = {}
    for label, field in (("P-F", "P"), ("R-F", "R")):
        target = [0] * len(order)
        if field in index and "F" in index:
            target[index[field]] += 1
            target[index["F"]] -= 1
            result = certificate(target)
            if result is not None:
                scans[label] = result.pop("_scan")
                differences[label] = result
    checks = {
        "declared_rows_rank_10_one_relation": len(vectors) == 11 and rank == 10 and len(relations) == 1
        and relation == EXPECTED_DECLARED_RELATION,
    }
    return {
        "label": "EXACT",
        "method": LATTICE_METHOD,
        "declared_order": names,
        "declared_rank": rank,
        "declared_relation": relation,
        "certificates": certificates,
        "difference_certificates": differences,
        "scan": {
            "every_scan_covers_its_breakpoints": bool(scans) and all(row["scan_covers_breakpoints"] for row in scans.values()),
            "scan_ranges": {label: row["scan_range"] for label, row in scans.items()},
            "tied_minimal_l1_solutions": {label: row["minimal_ties"] for label, row in scans.items() if row["minimal_ties"] != 1},
        },
        "statement": LATTICE_STATEMENT,
        "spurion_note": LATTICE_SPURION_NOTE,
        "checks": checks,
    }


def verify_lattice(sections: Mapping[str, Mapping[str, Any]]) -> dict[str, bool]:
    """Re-verify the stored certificates exactly from the recorded model terms and census rows (fail closed)."""
    output = {
        "every_undeclared_is_an_integer_combination_of_declared_terms": False,
        "P_minus_F_and_R_minus_F_are_integer_combinations": False,
    }
    try:
        order = list(sections["kernel"]["unknowns"])
        declared = {
            str(term["coefficient"]): _vector(order, _monomial_factors(str(term["monomial"])))
            for term in sections["model"]["declared_LagHC_terms"]
        }
        lattice = sections["lattice"]
        if list(lattice["declared_order"]) != list(declared):
            return output
        census = sections["census"]
        targets = {
            str(row["coupling"]): _vector(order, _coupling_factors(row)) for row in census["allowed"] if not row["declared"]
        }

        def verified(combination: Any, degree: Any, target: Sequence[int]) -> bool:
            if not isinstance(combination, Mapping) or not combination or not _is_int(degree):
                return False
            total = [0] * len(order)
            for name, value in combination.items():
                if name not in declared or not _is_int(value) or value == 0:
                    return False
                total = [a + value * b for a, b in zip(total, declared[name])]
            return total == list(target) and degree == sum(abs(value) for value in combination.values())

        certificates = lattice["certificates"]
        output["every_undeclared_is_an_integer_combination_of_declared_terms"] = bool(
            set(certificates) == set(targets) == set(census["undeclared"])
            and len(targets) == EXPECTED_UNDECLARED
            and all(
                verified(certificates[label]["combination"], certificates[label]["degree_l1"], targets[label])
                for label in targets
            )
        )
        index = {name: position for position, name in enumerate(order)}
        differences = lattice["difference_certificates"]
        ok = set(differences) == {"P-F", "R-F"}
        for label, field in (("P-F", "P"), ("R-F", "R")):
            target = [0] * len(order)
            target[index[field]] += 1
            target[index["F"]] -= 1
            ok = ok and verified(differences[label]["combination"], differences[label]["degree_l1"], target)
        output["P_minus_F_and_R_minus_F_are_integer_combinations"] = bool(ok)
    except (KeyError, TypeError, ValueError, IndexError, AttributeError):
        pass
    return output


# ---------------------------------------------------------------------------
# (cross) Bindings to the committed G8 and G1 artifacts
# ---------------------------------------------------------------------------


def _g8_live_cross_check(text: str, census: Mapping[str, Any], live: bool) -> dict[str, Any]:
    record: dict[str, Any] = {"computed": False, "allowed_labels_match": False, "declared_flags_match": False,
                              "undeclared_match": False, "model_contract_id_matches": False}
    if not live:
        record["note"] = "live cross-check not run (mandatory: the check is False)"
        return record
    try:
        contract = g8.contract_section(text)
        theirs = {row["coupling"]: row["declared"] for row in contract["allowed_renormalizable_fermion_couplings"]}
        ours = {row["coupling"]: row["declared"] for row in census["allowed"]}
        record.update(
            {
                "computed": True,
                "allowed_labels_match": sorted(theirs) == sorted(ours) and len(theirs) == len(ours),
                "declared_flags_match": theirs == ours,
                "undeclared_match": list(contract["allowed_but_undeclared"]) == list(census["undeclared"]),
                "model_contract_id_matches": getattr(g8, "MODEL_CONTRACT_ID", None) == MODEL_CONTRACT_ID,
            }
        )
    except Exception as error:  # noqa: BLE001 - any failure of the live cross-check fails closed
        record["error"] = f"{type(error).__name__}: {error}"
    return record


def _g8_json_cross_check(report: Any, text: str, census: Mapping[str, Any], reps: Mapping[str, str]) -> dict[str, Any]:
    allowed = census["allowed"]
    record: dict[str, Any] = {"report": G8_JSON.name, "status": None}
    try:
        contract = report["contract"]
        record["status"] = report["status"]
        record["status_and_zero_failed"] = bool(
            report["status"] == G8_STATUS_REQUIRED and _is_int(report["n_failed"]) and report["n_failed"] == 0
            and report.get("model_contract_id") == MODEL_CONTRACT_ID
        )
        record["allowed_count_26"] = bool(_is_int(contract["allowed_count"]) and contract["allowed_count"] == EXPECTED_ALLOWED)
        record["undeclared_equals_expected"] = contract["allowed_but_undeclared"] == list(EXPECTED_UNDECLARED_LABELS)
        record["undeclared_equals_census"] = contract["allowed_but_undeclared"] == list(census["undeclared"])
        record["model_sha256_matches"] = contract["model_text_sha256"] == _sha256_lf(text)

        def pick(predicate: Any) -> list[str]:
            return sorted(row["coupling"] for row in allowed if predicate(row))

        lists = {
            "H10_yukawas": pick(lambda row: row["scalar"] == "H10" and row["bilinear_class"] == "16.16"),
            "Delta126bar_yukawas": pick(lambda row: row["scalar"] == "Delta126bar" and row["bilinear_class"] == "16.16"),
            "conj_H10_yukawas": pick(lambda row: row["scalar"] == "conj[H10]" and row["bilinear_class"] == "16.16"),
            "vectorlike_mass_couplings": pick(lambda row: row["bilinear_class"] == "16.16bar"),
            "sixteenbar_pair_couplings": pick(lambda row: row["bilinear_class"] == "16bar.16bar"),
        }
        lists_equal = {name: contract[name] == expected for name, expected in lists.items()}
        union = [label for name in lists for label in contract[name]]
        pairs = []
        for row in allowed:
            if row["bilinear_class"] != "16.16bar":
                continue
            first, second = row["fermions"]
            bar, sixteen = (first, second) if reps.get(first) == "-16" else (second, first)
            pairs.append(f"{bar}-{sixteen}")
        rank = contract["vectorlike_rank_certificate"]
        record["dimension4"] = {
            "lists_equal_census": lists_equal,
            "union_is_the_allowed_set": len(union) == len(set(union)) == len(allowed)
            and set(union) == {row["coupling"] for row in allowed},
            "undeclared_contained": set(census["undeclared"]) <= set(union),
            "X1_sixteens_F_P_R": contract["X1_sixteens"] == ["F", "P", "R"],
            "light_state_lemma_uses_general_16_16_10H_coupling": G8_LIGHT_STATE_PHRASE in str(contract["light_state_lemma"]),
            "vectorlike_rank_8_on_all_allowed_pairs": _is_int(rank["rank_at_integer_couplings"])
            and rank["rank_at_integer_couplings"] == G8_VECTORLIKE_RANK
            and sorted(rank["coupled_pairs"]) == sorted(set(pairs)),
        }
    except (KeyError, TypeError, AttributeError) as error:
        record["error"] = f"{type(error).__name__}: {error}"
    return record


def _structural_cross_check(report: Any, census: Mapping[str, Any]) -> dict[str, Any]:
    record: dict[str, Any] = {"report": STRUCTURAL_JSON.name, "status": None, "census_matches": False}
    try:
        corollaries = report["corollaries"]
        couplings = corollaries["field_level_couplings"]
        record["status"] = report["status"]
        record["status_and_zero_failed"] = bool(
            report["status"] == STRUCTURAL_STATUS_REQUIRED and _is_int(report["n_failed"]) and report["n_failed"] == 0
            and report.get("model_contract_id") == MODEL_CONTRACT_ID
        )
        record["field_level_couplings_equal_allowed_set"] = bool(
            isinstance(couplings, list)
            and len(couplings) == len(set(couplings)) == census["allowed_count"]
            and set(couplings) == {row["coupling"] for row in census["allowed"]}
        )
        record["generation_expanded_74"] = bool(
            _is_int(corollaries["generation_expanded_count"])
            and corollaries["generation_expanded_count"] == EXPECTED_GENERATION_EXPANDED == census["generation_expanded_count"]
        )
        record["no_X_neutral_16bar_16_pair"] = corollaries["X_neutral_16bar_16_pairs"] == []
        record["census_matches"] = all(
            record[key] is True
            for key in ("status_and_zero_failed", "field_level_couplings_equal_allowed_set", "generation_expanded_74",
                        "no_X_neutral_16bar_16_pair")
        )
    except (KeyError, TypeError, AttributeError) as error:
        record["error"] = f"{type(error).__name__}: {error}"
    return record


def g1_census_links(report: Any, order: Sequence[str]) -> tuple[dict[str, list[int]], bool]:
    """Charge vectors of the committed G1 multidegrees (letters -> multiplets); only nonzero vectors are links."""
    links: dict[str, list[int]] = {}
    try:
        index = {name: position for position, name in enumerate(order)}
        for multidegree in report["multidegrees"]:
            vector = [0] * len(order)
            for letter, count in multidegree["counts"].items():
                if letter not in G1_LETTERS or not _is_int(count) or count < 0:
                    return {}, False
                field, sign = G1_LETTERS[letter]
                vector[index[field]] += sign * count
            if any(vector):
                links[str(multidegree["monomial"])] = vector
    except (KeyError, TypeError, AttributeError):
        return {}, False
    return links, True


def _g1_census_cross_check(report: Any, fields: Mapping[str, Any], pq: Mapping[str, int], links: Mapping[str, Any],
                           links_ok: bool) -> dict[str, Any]:
    record: dict[str, Any] = {"report": G1_CENSUS_JSON.name, "status": None, "bound": False}
    try:
        multidegrees = report["multidegrees"]
        record["status"] = report["status"]
        record["status_and_zero_failed"] = bool(
            report["status"] == G1_CENSUS_STATUS_REQUIRED and _is_int(report["n_failed"]) and report["n_failed"] == 0
            and report.get("model_contract_id") == MODEL_CONTRACT_ID
        )
        allowed_count = report["counts"]["charge_and_so10_allowed_multidegrees"]
        record["multidegrees_34"] = bool(
            isinstance(multidegrees, list) and len(multidegrees) == EXPECTED_G1_MULTIDEGREES
            and _is_int(allowed_count) and allowed_count == EXPECTED_G1_MULTIDEGREES
        )
        neutral = links_ok
        for multidegree in multidegrees:
            x_sum = pq_sum = z_sum = 0
            for letter, count in multidegree["counts"].items():
                if not _is_int(count):
                    raise ValueError(f"non-integer count {count!r}")
                field, sign = G1_LETTERS[letter]
                x_sum += sign * count * int(fields[field]["X"])
                z_sum += sign * count * int(fields[field]["Z17"])
                pq_sum += sign * count * int(pq.get(field, 0))
            neutral = neutral and x_sum == 0 and pq_sum == 0 and z_sum % 17 == 0
        record["every_multidegree_X_PQ_Z17_neutral"] = bool(neutral)
        record["nontrivial_links"] = len(links)
        record["nontrivial_links_20"] = len(links) == EXPECTED_G1_NONTRIVIAL_LINKS
        record["bound"] = all(
            record[key] is True
            for key in ("status_and_zero_failed", "multidegrees_34", "every_multidegree_X_PQ_Z17_neutral",
                        "nontrivial_links_20")
        )
    except (KeyError, TypeError, AttributeError, ValueError) as error:
        record["error"] = f"{type(error).__name__}: {error}"
    return record


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------


def compute_sections(
    *,
    model_text: str | None = None,
    g8_report: Any = None,
    structural_report: Any = None,
    g1_census_report: Any = None,
    pq_charges: Mapping[str, int] | None = None,
    live_g8: bool = True,
) -> dict[str, dict[str, Any]]:
    """Every computed section; None loads the committed file, any other value is a fail-closed mutation."""
    text = MODEL_FILE.read_text(encoding="utf-8") if model_text is None else model_text
    g8_json = _load_json(G8_JSON) if g8_report is None else g8_report
    structural = _load_json(STRUCTURAL_JSON) if structural_report is None else structural_report
    g1_census = _load_json(G1_CENSUS_JSON) if g1_census_report is None else g1_census_report

    parsed = parse_model(text)
    fields = parsed["fields"]
    scalars = [name for name, row in fields.items() if row["kind"] == "scalar"]
    fermions = [name for name, row in fields.items() if row["kind"] == "fermion"]
    order = scalars + fermions

    model = model_section(text, parsed)
    rows = census_rows(parsed)
    z17 = z17_section(parsed, rows)
    census = census_section(parsed, rows)

    # ---- charge vectors and U(1) kernels
    for term in parsed["LagHC"]:
        term["vector"] = _vector(order, term["factors"])
    coupling_vectors = {row["coupling"]: _vector(order, _coupling_factors(row)) for row in census["allowed"]}
    scalar_links = {
        term["coefficient"]: term["vector"]
        for term in parsed["LagHC"]
        if _term_kind(fields, term["factors"]) == "scalar_link"
    }
    links, links_ok = g1_census_links(g1_census, order)
    real_rows = [_vector(order, [(name, 1)]) for name in order if fields[name]["real"]]
    declared_vectors = [term["vector"] for term in parsed["LagHC"]]
    systems = {
        "declared_LagHC": declared_vectors + real_rows,
        "declared_LagHC_plus_G1_scalar_links": declared_vectors + list(links.values()) + real_rows,
        "allowed_26_plus_kappaH": list(coupling_vectors.values()) + list(scalar_links.values()) + real_rows,
        "allowed_26_plus_kappaH_plus_G1_scalar_links": list(coupling_vectors.values()) + list(scalar_links.values())
        + list(links.values()) + real_rows,
        "allowed_26_without_scalar_links": list(coupling_vectors.values()) + real_rows,
    }
    kernels = {name: _nullspace(matrix, len(order)) for name, matrix in systems.items()}
    dimensions = {name: len(basis) for name, basis in kernels.items()}

    repo_pq, repo_ok = repository_pq_charges(fields)
    pq = dict(repo_pq) if pq_charges is None else {str(k): int(v) for k, v in pq_charges.items()}
    x_vec = [int(fields[name]["X"]) for name in order]
    pq_vec = [int(pq.get(name, 0)) for name in order]
    spec_vec = [SPECTATOR_NUMBER.get(name, 0) for name in order]
    n17_vec = [Fraction(x - p, 17) for x, p in zip(x_vec, pq_vec)]
    span_rank = _rank([x_vec, pq_vec, spec_vec], len(order))
    equals_span = {}
    for name in DIMENSION_3_KERNELS:
        matrix = systems[name]
        equals_span[name] = bool(
            dimensions[name] == 3
            and span_rank == 3
            and all(_dot(row, generator) == 0 for row in matrix for generator in (x_vec, pq_vec, spec_vec))
        )
    position = {name: index for index, name in enumerate(order)}
    fpr_identical = bool(
        all(name in position for name in ("F", "P", "R"))
        and all(
            basis[position["F"]] == basis[position["P"]] == basis[position["R"]]
            for kernel in kernels.values()
            for basis in kernel
        )
    )
    kernel_checks = {
        KERNEL_CHECK_NAMES[name]: dimensions[name] == EXPECTED_KERNEL_DIMENSIONS[name] for name in EXPECTED_KERNEL_DIMENSIONS
    }
    kernel_checks["every_dimension_3_kernel_equals_span_X_PQ_Nspec"] = all(equals_span.values())
    kernel_checks["F_P_R_identical_under_every_kernel_element"] = fpr_identical
    kernel = {
        "label": "EXACT",
        "unknowns": order,
        "generation_note": KERNEL_GENERATION_NOTE,
        "real_field_constraint": KERNEL_REAL_FIELD_CONSTRAINT,
        "scalar_links": {**scalar_links, "G1_census_links": links},
        "dimensions": dimensions,
        "generators": {
            "X": dict(zip(order, x_vec)),
            "PQ": dict(zip(order, pq_vec)),
            "N_spec": dict(zip(order, spec_vec)),
            "N17": {name: (int(value) if value.denominator == 1 else str(value)) for name, value in zip(order, n17_vec)},
        },
        "equals_span_X_PQ_Nspec": equals_span,
        "F_P_R_identical": fpr_identical,
        "statement": KERNEL_STATEMENT,
        "checks": kernel_checks,
    }

    # ---- PQ
    def sums(vector: Sequence[int]) -> dict[str, Any]:
        n17 = _dot(vector, n17_vec)
        return {
            "X_sum": int(_dot(vector, x_vec)),
            "PQ_sum": int(_dot(vector, pq_vec)),
            "N_spec_sum": int(_dot(vector, spec_vec)),
            "N17_sum": int(n17) if n17.denominator == 1 else str(n17),
            "Z17_sum_mod_17": int(sum(v * int(fields[name]["Z17"]) for v, name in zip(vector, order))) % 17,
        }

    per_coupling = {label: sums(vector) for label, vector in coupling_vectors.items()}
    undeclared = census["undeclared"]
    monomials = _scalar_monomial_check(fields, pq)

    def anomaly(charges: Sequence[Any]) -> Any:
        value = sum(int(fields[name]["generations"]) * 2 * Fraction(q) for name, q in zip(order, charges)
                    if fields[name]["kind"] == "fermion")
        return int(value) if value.denominator == 1 else str(value)

    anomalies = {"T_16": 2, "N_X": anomaly(x_vec), "N_PQ": anomaly(pq_vec), "N_spec": anomaly(spec_vec),
                 "N17": anomaly(n17_vec)}
    pq_section = {
        "label": "EXACT",
        "source": PQ_SOURCE,
        "charges": dict(zip(order, pq_vec)),
        "per_coupling": per_coupling,
        "all_allowed_PQ_neutral": all(row["PQ_sum"] == 0 for row in per_coupling.values()),
        "all_undeclared_PQ_neutral": all(per_coupling[label]["PQ_sum"] == 0 for label in undeclared),
        "scalar_monomials_X_neutral_implies_PQ_neutral": not monomials["PQ_violations"],
        "scalar_monomial_census": monomials,
        "anomaly": anomalies,
        "anomaly_note": PQ_ANOMALY_NOTE,
        "statement": PQ_STATEMENT,
        "checks": {
            "charges_match_repository_contract": bool(repo_ok and pq == repo_pq and set(pq) == set(order)),
            "X_minus_PQ_equals_17_N17": all(value.denominator == 1 for value in n17_vec),
            "all_26_allowed_couplings_PQ_neutral": len(per_coupling) == EXPECTED_ALLOWED
            and all(row["PQ_sum"] == 0 and row["N_spec_sum"] == 0 for row in per_coupling.values()),
            "all_16_undeclared_couplings_PQ_neutral": len(undeclared) == EXPECTED_UNDECLARED
            and all(per_coupling[label]["PQ_sum"] == 0 for label in undeclared),
            "renormalizable_scalar_monomials_X_neutral_implies_PQ_neutral": monomials["count_tuples"] == 715
            and not monomials["PQ_violations"],
            "anomaly_N_X_0_N_PQ_minus_34_N_spec_0": anomalies == EXPECTED_ANOMALY,
        },
    }

    # ---- lattice
    declared_terms = [{"coefficient": term["coefficient"], "vector": term["vector"]} for term in parsed["LagHC"]]
    lattice = lattice_section(order, declared_terms, {label: coupling_vectors[label] for label in undeclared})

    # ---- sector
    reps = {name: fields[name]["so10"] for name in fermions}
    per_undeclared = {}
    for row in census["allowed"]:
        if row["declared"]:
            continue
        members = [name for name in VECTORLIKE_SECTOR_FIELDS if name in row["fermions"]]
        first, second = row["fermions"]
        other = second if first == "F" else first
        mixing = (
            "F" in row["fermions"]
            and reps.get(other) == "-16"
            and row["scalar"].replace("conj[", "").rstrip("]") in SINGLET_SCALARS
        )
        per_undeclared[row["coupling"]] = {
            "vectorlike_sector_fields": members,
            "bilinear_class": row["bilinear_class"],
            "is_F_16bar_mass_mixing": bool(mixing),
        }
    mixings = sorted(label for label, row in per_undeclared.items() if row["is_F_16bar_mass_mixing"])
    sector = {
        "label": "EXACT (membership)",
        "vectorlike_sector_fields": list(VECTORLIKE_SECTOR_FIELDS),
        "per_undeclared": dict(sorted(per_undeclared.items())),
        "F_16bar_mass_mixings": mixings,
        "statement": SECTOR_STATEMENT,
        "checks": {
            "every_undeclared_involves_P_R_Pbar_Rbar_or_Qbar": len(per_undeclared) == EXPECTED_UNDECLARED
            and all(row["vectorlike_sector_fields"] for row in per_undeclared.values()),
            "no_undeclared_involves_Q_SpecS_SpecB": bool(per_undeclared)
            and all(
                not set(NON_TRUNCATED_FIELDS) & set(row["fermions"]) for row in census["allowed"] if not row["declared"]
            ),
            "exactly_two_F_16bar_mass_mixings": mixings == list(EXPECTED_F_MASS_MIXINGS),
        },
    }

    # ---- cross checks
    live = _g8_live_cross_check(text, census, live_g8)
    g8_record = _g8_json_cross_check(g8_json, text, census, reps)
    dimension4 = g8_record.get("dimension4", {})
    structural_record = _structural_cross_check(structural, census)
    g1_record = _g1_census_cross_check(g1_census, fields, pq, links, links_ok)
    cross = {
        "label": "BOUND",
        "g8_live_contract_section": live,
        "g8_json": g8_record,
        "structural_json": structural_record,
        "g1_census_json": g1_record,
        "checks": {
            "g8_live_contract_section_matches": all(
                live.get(key) is True
                for key in ("computed", "allowed_labels_match", "declared_flags_match", "undeclared_match",
                            "model_contract_id_matches")
            ),
            "g8_json_recorded_and_lists_match": all(
                g8_record.get(key) is True
                for key in ("status_and_zero_failed", "allowed_count_26", "undeclared_equals_expected",
                            "undeclared_equals_census")
            ),
            "g8_json_model_sha256_matches": g8_record.get("model_sha256_matches") is True,
            "g8_dimension4_lists_cover_all_allowed_couplings": bool(dimension4)
            and all(value is True for value in dimension4.get("lists_equal_census", {"missing": False}).values())
            and all(dimension4.get(key) is True for key in dimension4 if key != "lists_equal_census"),
            "structural_obstruction_json_census_matches": structural_record.get("census_matches") is True,
            "g1_census_json_bound_and_links_neutral": g1_record.get("bound") is True,
        },
    }
    return {
        "model": model,
        "z17": z17,
        "census": census,
        "kernel": kernel,
        "pq": pq_section,
        "lattice": lattice,
        "sector": sector,
        "cross": cross,
    }


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------


def _collect_checks(sections: Mapping[str, Mapping[str, Any]]) -> dict[str, bool]:
    output = {}
    for prefix, section in sections.items():
        for key, value in section.get("checks", {}).items():
            output[f"{prefix}.{key}"] = value is True
    return output


def _derive_flags(checks: Mapping[str, bool], overrides: Mapping[str, bool] | None = None) -> dict[str, bool]:
    passed = (
        bool(checks)
        and all(value is True for value in checks.values())
        and len(checks) == EXPECTED_N_CHECKS
        and set(checks) == set(EXPECTED_CHECK_KEYS)
    )

    def section_passed(prefix: str) -> bool:
        return all(value for key, value in checks.items() if key.startswith(prefix + "."))

    flags = {
        "declared_lagrangian_is_a_truncation_exact": passed and section_passed("census") and section_passed("z17"),
        "undeclared_couplings_unprotected_by_any_U1_exact": passed and section_passed("kernel"),
        "undeclared_couplings_unprotected_by_any_multiplet_diagonal_phase_symmetry_exact": passed
        and section_passed("lattice"),
        "all_allowed_couplings_PQ_neutral_exact": passed and section_passed("pq"),
        "F_P_R_charge_degenerate_exact": passed
        and checks.get("kernel.F_P_R_identical_under_every_kernel_element") is True
        and checks.get("lattice.P_minus_F_and_R_minus_F_are_integer_combinations") is True,
        "g8_dimension4_analysis_covers_all_allowed_couplings": passed
        and checks.get("cross.g8_dimension4_lists_cover_all_allowed_couplings") is True,
        "truncation_not_removable_by_field_redefinitions_exact": passed
        and checks.get("census.undeclared_48_real_dimensions_exceed_mixing_field_redefinitions_25") is True,
        "evidence_only": passed,
    }
    flags = {name: bool(value) for name, value in flags.items()}
    for name in NEVER_TRUE_FLAGS:
        flags[name] = False
    for name, value in (overrides or {}).items():
        if name in NEVER_TRUE_FLAGS:
            flags[name] = bool(value)
    return flags


def _public(section: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in section.items() if key != "checks" and not key.startswith("_")}


def assemble_report(
    sections: Mapping[str, Mapping[str, Any]],
    started: float | None = None,
    *,
    flag_overrides: Mapping[str, bool] | None = None,
) -> dict[str, Any]:
    """Assemble the report; the lattice certificates are re-verified from the recorded data, the scope check is the
    status-neutral flag test.  flag_overrides (NEVER_TRUE names only) is a fail-closed mutation hook for the tests."""
    started = time.time() if started is None else started
    ordered: dict[str, dict[str, Any]] = {}
    for name in SECTION_ORDER:
        section = dict(sections.get(name, {}))
        section["checks"] = dict(section.get("checks", {}))
        ordered[name] = section
    ordered["lattice"]["checks"].update(verify_lattice(ordered))
    provisional = _collect_checks(ordered)
    provisional["scope.status_neutral_flags"] = True
    flags = _derive_flags(provisional, flag_overrides)
    ordered["scope"] = {"checks": {"status_neutral_flags": all(flags[name] is False for name in NEVER_TRUE_FLAGS)}}
    checks = _collect_checks(ordered)
    flags = _derive_flags(checks, flag_overrides)
    failures = sorted(name for name, value in checks.items() if not value)
    if len(checks) != EXPECTED_N_CHECKS:
        failures.append(f"check_count_{len(checks)}_expected_{EXPECTED_N_CHECKS}")
    if set(checks) != set(EXPECTED_CHECK_KEYS):
        failures.append("check_keys_differ_from_expected")
    passed = not failures
    report = {
        "module": MODULE_NAME,
        "model_contract_id": MODEL_CONTRACT_ID,
        "gate": GATE,
        "status": STATUS_RECORDED if passed else STATUS_INCOMPLETE,
        "overall_state": OVERALL_STATE_RECORDED if passed else OVERALL_STATE_OPEN,
        "n_checks": len(checks),
        "expected_n_checks": EXPECTED_N_CHECKS,
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "labels": dict(LABELS),
        "model": _public(ordered["model"]),
        "z17": _public(ordered["z17"]),
        "census": _public(ordered["census"]),
        "kernel": _public(ordered["kernel"]),
        "pq": _public(ordered["pq"]),
        "lattice": _public(ordered["lattice"]),
        "sector": _public(ordered["sector"]),
        "cross_checks": _public(ordered["cross"]),
        "g8_coverage": {"label": "BOUND", "statement": G8_COVERAGE_STATEMENT},
        "radiative": {
            "label": "ARGUMENT (not computed)",
            "statement": RADIATIVE_STATEMENT,
            "one_loop_example": RADIATIVE_ONE_LOOP_EXAMPLE,
            "not_claimed": list(RADIATIVE_NOT_CLAIMED),
        },
        "scope": {key: list(value) for key, value in SCOPE.items()},
        "flags": flags,
        "verdict": "",
        "runtime_seconds": 0.0,
    }
    report["verdict"] = _verdict(report)
    report["runtime_seconds"] = round(time.time() - started, 6)
    return report


def build_report(**mutations: Any) -> dict[str, Any]:
    started = time.time()
    return assemble_report(compute_sections(**mutations), started=started)


def report_passes(report: Mapping[str, Any]) -> bool:
    try:
        return bool(
            report["status"] == STATUS_RECORDED
            and report["overall_state"] == OVERALL_STATE_RECORDED
            and _is_int(report["n_failed"])
            and report["n_failed"] == 0
            and report["failures"] == []
            and report["n_checks"] == EXPECTED_N_CHECKS
            and len(report["checks"]) == EXPECTED_N_CHECKS
            and set(report["checks"]) == set(EXPECTED_CHECK_KEYS)
            and all(value is True for value in report["checks"].values())
            and all(report["flags"][name] is True for name in TRUE_FLAGS)
            and all(report["flags"][name] is False for name in NEVER_TRUE_FLAGS)
        )
    except (KeyError, TypeError):
        return False


def _verdict(report: Mapping[str, Any]) -> str:
    if report["n_failed"]:
        return (
            "FAIL-CLOSED: the G1 contract-truncation scope is NOT established (failed: " + ", ".join(report["failures"])
            + ").  No truncation statement is recorded; the G1 status does not depend on this record and no gate "
            "status changes."
        )
    return VERDICT_RECORDED


def _vector_text(order: Sequence[str], vector: Sequence[int]) -> str:
    parts = []
    for name, value in zip(order, vector):
        if value:
            parts.append(f"{'+' if value > 0 else '-'}{'' if abs(value) == 1 else abs(value)}{name}")
    return " ".join(parts) if parts else "0"


def _combination_text(combination: Mapping[str, int], order: Sequence[str]) -> str:
    """The certificate in declared-term order (the JSON stores it with sorted keys)."""
    names = [name for name in order if name in combination] + sorted(set(combination) - set(order))
    return ", ".join(f"{name}: {combination[name]}" for name in names)


def _flat_text(record: Mapping[str, Any], prefix: str = "") -> str:
    """A cross-check record as 'key = value' pairs (nested keys dotted) for the Markdown summary."""
    parts = []
    for key, value in record.items():
        if isinstance(value, Mapping):
            parts.append(_flat_text(value, f"{prefix}{key}."))
        else:
            parts.append(f"{prefix}{key} = {value}")
    return "; ".join(part for part in parts if part)


def _markdown(report: Mapping[str, Any]) -> str:
    model, census, kernel, pq, lattice = report["model"], report["census"], report["kernel"], report["pq"], report["lattice"]
    sector, cross = report["sector"], report["cross_checks"]
    order = kernel["unknowns"]
    lines = [
        "# G1 contract-truncation scope: 26 allowed, 10 declared, 16 undeclared fermion bilinears (v20, status-neutral)",
        "",
        f"- Status: `{report['status']}`",
        f"- Overall state: `{report['overall_state']}`",
        f"- Checks: {report['n_checks'] - report['n_failed']}/{report['n_checks']} pass (expected {report['expected_n_checks']})",
        "- No gate status changes: G1 stays CLOSED and is scoped as the attestation of a truncation; no coupling is added.",
        "",
        "## Verdict",
        "",
        report["verdict"],
        "",
        "## Labels",
        "",
    ]
    lines += [f"- {name}: {text}." for name, text in report["labels"].items()]
    lines += [
        "",
        "## Model file [EXACT]",
        "",
        f"- File: `{model['file']}` (sha256 of the LF-normalised text `{model['text_sha256_lf']}`).",
        "",
        "| field | kind | SO(10) | X | Z17 | generations | real | PQ | N17 | Nspec |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for name in order:
        row = model["fields"][name]
        lines.append(
            f"| {name} | {row['kind']} | {row['so10']} | {row['X']} | {row['Z17']} | {row['generations']} | {row['real']} "
            f"| {kernel['generators']['PQ'].get(name)} | {kernel['generators']['N17'].get(name)} "
            f"| {kernel['generators']['N_spec'].get(name)} |"
        )
    lines += ["", "| LagHC coefficient | monomial | kind | X sum | Z17 sum mod 17 |", "|---|---|---|---|---|"]
    for row in model["declared_LagHC_terms"]:
        lines.append(f"| {row['coefficient']} | `{row['monomial']}` | {row['kind']} | {row['X_sum']} | {row['Z17_sum_mod_17']} |")
    lines += [
        "",
        f"- LagNoHC terms (all X and Z17 neutral): "
        + ", ".join(f"`{row['coefficient']} {row['monomial']}`" for row in model["declared_LagNoHC_terms"]) + ".",
        "",
        "## Z17 [EXACT]",
        "",
        f"- {report['z17']['statement']}.",
        f"- X-allowed couplings removed by Z17: {report['z17']['X_allowed_couplings_removed_by_Z17'] or 'none'}.",
        "",
        "## Census [EXACT]",
        "",
        f"- Method: {census['method']}.",
        f"- Allowed {census['allowed_count']}, declared {census['declared_count']}, undeclared {census['undeclared_count']}; "
        f"generation-expanded {census['generation_expanded_count']}; bare 16.16bar masses: "
        f"{census['bare_16_16bar_masses'] or 'none'}; Phi210 couplings: {census['Phi210_couplings'] or 'none'}.",
        "- Undeclared by bilinear class: " + ", ".join(f"{k}: {v}" for k, v in census["undeclared_class_counts"].items()) + ".",
        f"- Field redefinitions: declared {census['field_redefinitions']['declared_real_dimension']} and undeclared "
        f"{census['field_redefinitions']['undeclared_real_dimension']} real generation-expanded dimensions; mixing classes "
        + ", ".join(
            f"{'/'.join(row['fields'])} ({row['group']}, {row['real_dimension']} real)"
            for row in census["field_redefinitions"]["mixing_classes"].values()
        )
        + f"; declared-orbit bound {census['field_redefinitions']['declared_orbit_real_dimension_bound']} < "
        f"{census['field_redefinitions']['all_couplings_real_dimension']}.",
        f"- {census['field_redefinitions']['statement']}.",
        f"- Method: {census['field_redefinitions']['method']}.",
        "",
        "| coupling | scalar rep | class | declared | coefficient | PQ sum | N17 sum |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in census["allowed"]:
        sums = pq["per_coupling"][row["coupling"]]
        lines.append(
            f"| `{row['coupling']}` | {row['scalar_rep']} | {row['bilinear_class']} | {row['declared']} "
            f"| {row['declared_coefficient'] or '-'} | {sums['PQ_sum']} | {sums['N17_sum']} |"
        )
    lines += [
        "",
        "## U(1) kernels [EXACT]",
        "",
        f"- Unknowns: {', '.join(order)}.",
        f"- {kernel['real_field_constraint']}.",
        f"- {kernel['generation_note']}.",
        "",
        "| system | kernel dimension | equals span{X, PQ, Nspec} |",
        "|---|---|---|",
    ]
    for name in EXPECTED_KERNEL_DIMENSIONS:
        lines.append(
            f"| {name} | {kernel['dimensions'].get(name)} | {kernel['equals_span_X_PQ_Nspec'].get(name, '- (S charge free)')} |"
        )
    links = kernel["scalar_links"]
    lines += [
        "",
        "- Scalar links: " + "; ".join(
            f"{name} = {_vector_text(order, vector)}" for name, vector in links.items() if name != "G1_census_links"
        ) + f"; {len(links['G1_census_links'])} nontrivial G1 census links.",
        f"- F, P, R identical under every kernel element: {kernel['F_P_R_identical']}.",
        f"- {kernel['statement']}.",
        "",
        "## PQ and anomaly [EXACT]",
        "",
        f"- Source: {pq['source']}.",
        f"- All allowed couplings PQ neutral: {pq['all_allowed_PQ_neutral']}; all undeclared PQ neutral: "
        f"{pq['all_undeclared_PQ_neutral']}.",
        f"- Scalar monomials of degree <= {SCALAR_MONOMIAL_MAX_DEGREE}: {pq['scalar_monomial_census']['count_tuples']} count "
        f"tuples, {pq['scalar_monomial_census']['X_neutral_tuples']} X-neutral, PQ violations: "
        f"{pq['scalar_monomial_census']['PQ_violations'] or 'none'}.",
        "- Anomaly: " + ", ".join(f"{k} = {pq['anomaly'].get(k)}" for k in EXPECTED_ANOMALY) + f" ({pq['anomaly_note']}).",
        f"- {pq['statement']}.",
        "",
        "## Integer lattice [EXACT]",
        "",
        f"- Method: {lattice['method']}.",
        f"- Declared order: {', '.join(lattice['declared_order'])}; rank {lattice['declared_rank']}; relation "
        f"{_combination_text(lattice['declared_relation'], lattice['declared_order'])} (sum = 0).",
        f"- Every scan covers its breakpoints: {lattice['scan']['every_scan_covers_its_breakpoints']}; tied minimal-L1 "
        "solutions (resolved by the stated tie-break): "
        + (", ".join(f"{label}: {count}" for label, count in lattice["scan"]["tied_minimal_l1_solutions"].items()) or "none")
        + ".",
        "",
        "| target | certificate (coefficient: multiplicity) | L1 |",
        "|---|---|---|",
    ]
    for label, row in lattice["certificates"].items():
        lines.append(f"| `{label}` | {_combination_text(row['combination'], lattice['declared_order'])} | {row['degree_l1']} |")
    for label, row in lattice["difference_certificates"].items():
        lines.append(f"| {label} | {_combination_text(row['combination'], lattice['declared_order'])} | {row['degree_l1']} |")
    lines += [
        "",
        f"- {lattice['statement']}.",
        f"- Spurion note: {lattice['spurion_note']}.",
        "",
        "## Vectorlike sector [EXACT, membership]",
        "",
        "| undeclared coupling | vectorlike-sector fields | class | F-16bar mass mixing |",
        "|---|---|---|---|",
    ]
    for label, row in sector["per_undeclared"].items():
        lines.append(
            f"| `{label}` | {', '.join(row['vectorlike_sector_fields'])} | {row['bilinear_class']} | {row['is_F_16bar_mass_mixing']} |"
        )
    lines += [
        "",
        f"- {sector['statement']}.",
        "",
        "## Cross-checks [BOUND]",
        "",
        f"- Live G8 contract section (g8_sm_pati_salam_flavour_nogo_v20.contract_section): {_flat_text(cross['g8_live_contract_section'])}.",
        f"- G8 flavour no-go JSON: {_flat_text(cross['g8_json'])}.",
        f"- G8 structural-obstruction JSON: {_flat_text(cross['structural_json'])}.",
        f"- G1 symmetry-census JSON: {_flat_text(cross['g1_census_json'])}.",
        "",
        "## G8 dimension-4 coverage [BOUND]",
        "",
        f"- {report['g8_coverage']['statement']}.",
        "",
        "## Radiative stability [ARGUMENT, not computed]",
        "",
        f"- {report['radiative']['statement']}.",
        f"- One-loop example: {report['radiative']['one_loop_example']}.",
        "- Not claimed: " + "; ".join(report["radiative"]["not_claimed"]) + ".",
        "",
        "## Scope",
        "",
    ]
    for key, items in report["scope"].items():
        lines.append(f"**{key}**")
        lines += [f"- {item}" for item in items]
        lines.append("")
    lines += ["## Flags", ""]
    lines += [f"- `{key}`: {value}" for key, value in report["flags"].items()]
    lines += ["", "## Checks", ""]
    lines += [f"- {'PASS' if value else 'FAIL'} `{key}`" for key, value in report["checks"].items()]
    # Keep the Markdown ASCII like every tracked .md file: the superset sign becomes its HTML entity.
    return ("\n".join(lines) + "\n").replace("\u2283", "&#8835;")


def write_report(report: Mapping[str, Any]) -> bool:
    """Write the JSON and Markdown only for a passing report (fail closed); returns whether they were written."""
    if not report_passes(report):
        return False
    OUT_JSON.write_text(json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_markdown(json_roundtrip(report)), encoding="utf-8")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true", help="write the JSON and Markdown artifacts (only if every check passes)")
    args = parser.parse_args(argv)
    report = build_report()
    written = write_report(report) if args.write else False
    summary = {key: report[key] for key in ("status", "overall_state", "n_checks", "n_failed", "failures", "flags", "runtime_seconds")}
    summary["written"] = written
    print(json.dumps(_jsonable(summary), indent=2))
    if not report_passes(report):
        return 1
    if args.write and not written:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
