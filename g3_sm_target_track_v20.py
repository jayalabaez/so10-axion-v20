#!/usr/bin/env python3
"""The SM Pati-Salam track of the final G3 gate (v20): the only G3 closure route.

This module is pure.  It imports only the standard library (json, fractions,
pathlib, typing), writes no file and runs nothing at import time.  Both
g1_g8_gate_ledger_v20 (for the G3 and G5 statuses) and
final_g3_acceptance_gate_v20 (for the closure decision and the report) import
it, so there is no import cycle.

It reads four committed JSON artifacts (fail closed: a missing, unreadable,
non-object or empty file counts as {}):

  G3_SM_PATI_SALAM_CANDIDATE_V20.json      exact SOS global minimum, SM stabilizer,
                                           exact BFB certificate V4 >= |q|^4/167
  G3_SM_PATI_SALAM_EQUALITY_SET_V20.json   {V = V0} = G.q0 exactly (proof inputs pinned, D6)
  G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json  exact 486 x 486 Hessian; its eps_family section
                                           (L1, L2) and final_acceptance_test statement
  G3_SIGMA_HYPERCHARGE_AUDIT_V20.json      the Y = 0 singlet with p is the standard SM

and evaluates the track as exact conjunctions of evidence keys: 10 artifact
integrity checks, 13 science criteria and 3 release prerequisites (the
prerequisites and the G1/G2 scoped-calculation flag are supplied by the
caller from the ledger).  The decisions D1-D6 are binding user decisions:

  D1  the SM Pati-Salam track is the only route to closing G3; the SU(5)+Delta
      chiral-H track is an integrity-checked diagnostic that never closes G3;
  D2  the witness is the light-but-massive doublet member V_PS,eps = V_PS +
      eps N_H (O06 = 2|kappa| r0 + eps, 0 < eps < 599/50) at r0 = 1/5, x0 = 1,
      kappa = -r0/4, whose Hessian kernel is exactly the symmetry orbit
      (451/35); the tuned eps = 0 point (447/39) is not the witness;
  D3  G1-G3 CLOSED does not approve an internal candidate (the downstream
      caveats must be resolved, or G4 CLOSED);
  D4  G5 is carried by the BFB certificate on the Pati-Salam coupling vector;
  D5  the model-level caveats are routed to G4/G6/G7/G8 (or outside G1-G8)
      and G3 keeps only disclosures;
  D6  the cited classical theorems and the hand-argued elementary steps of
      the equality-set proof are accepted G3-grade inputs, pinned verbatim.

Every predicate is fail closed (an exception gives False), bools are compared
with ``is``, integers must be int and not bool, and rationals are parsed from
strings only.  The output contains only JSON-native types and is
deterministic.  ``python g3_sm_target_track_v20.py`` prints the evaluation
with the prerequisites not evaluated (so the track is not closed there) and
exits 0 iff every integrity entry and every science entry except the
prerequisite-gated G1_G2_exact_scoped_calculations_complete is True.
"""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent
MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
TRACK_NAME = "sm_pati_salam"
DIAGNOSTIC_TRACK_NAME = "chiral_H_SU5_Delta"
TRACK_ROLE = "ONLY_CLOSURE_ROUTE"

INPUT_FILES: dict[str, str] = {
    "candidate": "G3_SM_PATI_SALAM_CANDIDATE_V20.json",
    "equality_set": "G3_SM_PATI_SALAM_EQUALITY_SET_V20.json",
    "exact_hessian": "G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json",
    "sigma_hypercharge": "G3_SIGMA_HYPERCHARGE_AUDIT_V20.json",
}

CANDIDATE_STATUS = "SM_PATI_SALAM_G3_CANDIDATE__EXACT_GLOBAL_MINIMUM_OF_BENCHMARK_POTENTIAL__SM_UNBROKEN__G3_OPEN"
CANDIDATE_OVERALL_STATE = "CANDIDATE_CERTIFIED_G3_OPEN"
CANDIDATE_N_CHECKS = 31
EQUALITY_STATUS = "SM_PATI_SALAM_EQUALITY_SET__UNIQUE_MODULO_SYMMETRY_EXACT__G3_OPEN"
EQUALITY_N_CHECKS = 45
HESSIAN_STATUS = "SM_PATI_SALAM_EXACT_FULL_HESSIAN_RANK_447_NULLITY_39_CERTIFIED__G3_OPEN"
HESSIAN_OVERALL_STATE = "EXACT_LOCAL_HESSIAN_KERNEL_ORBIT_PLUS_TUNED_DOUBLET_CERTIFIED"
HESSIAN_N_CHECKS = 52
EPS_N_CHECKS = 30
SIGMA_STATUS = "G3_SIGMA_DIRECTION_IS_Y_MINUS_1_TRIPLET_COMPONENT__NAMED_VACUA_ARE_NOT_SM__G3_OPEN"
SIGMA_N_CHECKS = 28
SIGMA_STD_FORMULA = "z1^z2^z3^z4^z5"
EPS_KERNEL_TEXT = "span(T35), the SO(10) x U(1)_X x U(1)_PQ orbit tangent space"
O06_ID = "lambda::O06_B01_Hdag_H_norm"
PERTURBATIVE_BOUND = Fraction(12)          # < 4 pi because pi > 3: exact rational comparisons only
BENCHMARK = {"r0": Fraction(1, 5), "x0": Fraction(1), "kappa": Fraction(-1, 20), "O06": Fraction(1, 50)}
V0_EXPECTED = Fraction(-20661, 20000)
QUARTIC_BOUND_CONSTANT = "1/167"
EPS_WINDOW_UPPER = "599/50"                # = 12 - 2|kappa| r0, recomputed and compared
SELF_WEIGHTS = {"54": Fraction(2), "1050bar": Fraction(2), "2772bar": Fraction(1), "4125": Fraction(17, 16)}
O27_CHANNELS = (("lambda::O27_B01_126bar_self_projectors", "54"), ("lambda::O27_B02_126bar_self_projectors", "1050bar"),
                ("lambda::O27_B03_126bar_self_projectors", "2772bar"), ("lambda::O27_B04_126bar_self_projectors", "4125"))
MODEL_LEVEL_FLAGS = ("doublet_triplet_splitting_natural", "coloured_scalars_only_at_M_GUT",
                     "rg_anchor_field_content_reproduced", "higgs_mass_compatible",
                     "electroweak_symmetry_breaking_realized", "realistic_yukawa_sector",
                     "physical_benchmark_uses_canonical_phi17_scale")
PREREQUISITE_KEYS = ("authoritative_external_model_contract_executed", "G1_promoted_closed",
                     "G2_promoted_closed", "G1_G2_exact_scoped_calculations_complete")
RELEASE_PREREQUISITE_KEYS = PREREQUISITE_KEYS[:3]

# Unverified proof inputs of the equality-set theorem, accepted as G3-grade inputs under decision D6 and pinned
# verbatim (copied from g3_sm_pati_salam_gate_readiness_v20): a new or reworded cited theorem or elementary step
# fails sm_unchecked_proof_inputs_pinned and reopens G3.
PINNED_CITED_NOT_MACHINE_CHECKED = (
    "Pluecker relations: xi != 0 is decomposable iff (iota_alpha xi) ^ xi = 0 for all alpha",
    "Kostant's quadrics, set-theoretic form: {v in V(lambda) : v (x) v in V(2 lambda)} = G_C.v_lambda u {0}",
    "Iwasawa decomposition G_C = K A N of the complex group SO(10,C) with K = SO(10)",
    "Wirtinger inequality <xi, omega^p/p!> <= 1 for unit simple 2p-vectors, equality iff xi is a complex "
    "p-plane with its complex orientation",
    "U(n) is transitive on Gr_C(k, n) and preserves complex orientations",
    "a highest-weight vector of a finite-dimensional so(10,C)-module generates an irreducible submodule; "
    "Weyl dimension formula",
)
PINNED_ELEMENTARY_NOT_MACHINE_CHECKED = (
    "Cauchy-Schwarz |H.H| <= N_H (|sum_i H_i^2| <= sum_i |H_i|^2), used in P3 to reduce V_HS + r0^4 to the "
    "symbolically certified form",
    "the sign argument of HS_bracket_algebra.argument (cases |S| <= r0 and |S| > r0), which turns the exact "
    "sympy square-completion identities into V_HS + r0^4 >= 0 with equality iff H = 0 and |S| = r0 (P3)",
    "the Gram-Schmidt orbit step: a unit decomposable 4-vector equals u1^u2^u3^u4 with orthonormal u_i, and "
    "completing to a positively oriented orthonormal basis gives g in SO(10) with (Lambda^4 g) e6789 = Phi (P1)",
    "integrating the exact Lie-algebra identities over the connected groups: over SO(10), the invariance of D "
    "(from the checked intertwining identities, D' = 2 tr(T^T X5 T) - 2 tr(T^T T X3) = 0; P1) and the "
    "equivariance of M_Phi and C_Phi (P2(v)); over U(5), the u(5) line stabilisation of sigma_std (P2(viii))",
    "N sigma_std = sigma_std and A sigma_std in R_{>0} sigma_std for the Iwasawa factors N and A, from the "
    "checked weight (1,1,1,1,1) and positive-root data (P2(iv))",
    "the corollary's reduction: V_v = (|Phi|^2 - v^2)^2 - v^4 + I_45 + I_210 + I_5940 (from the checked "
    "Q = J0 + I_45 + I_210 + I_5940) and the rescaling Phi -> Phi/v",
)

# The decisive theorem for the eps witness (emitted by the certifying artifact, the exact-Hessian report's
# eps_family.final_acceptance_test.required_statement).
SM_FINAL_THEOREM = (
    "For every 486-real field q, V_PS,eps(q)-V_PS,eps(q0)>=0; equality holds exactly on the "
    "SO(10)xU(1)_XxPQ orbit of q0."
)
DECISIVE_THEOREM_EMITTED_BY = (
    "G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json:eps_family.final_acceptance_test.required_statement"
)
CLOSURE_SCOPE = (
    "G3 closed on the SM Pati-Salam benchmark family: the exact SM-preserving global vacuum of the declared "
    "exact-X potential's 27-parameter benchmark with the light-doublet deformation eps > 0, unique modulo "
    "SO(10) x U(1)_X x accidental U(1)_PQ; tuned DT/M_I relations; G4 OPEN, G6-G8 blocked; caveats routed "
    "downstream; internal candidate withheld; whole model neither validated nor excluded."
)
WITNESS_SENTENCE = (
    "The G3 witness is the light-but-massive doublet member V_PS,eps = V_PS + eps N_H (O06 = 2|kappa| r0 + eps, "
    "0 < eps < 599/50) at r0 = 1/5, x0 = 1, kappa = -r0/4: its exact Hessian at q0 = (p, 0, r0 sigma_std, r0, x0) "
    "is PSD with rank 451 and nullity 35 and kernel exactly the symmetry-orbit tangent space; the tuned eps = 0 "
    "point (447/39) is not the witness."
)
CAVEAT_ROUTING_SENTENCE = (
    "Model-level caveats are routed downstream and G3 keeps only disclosures: sub-M_I coloured states and "
    "positivity (no EWSB) go to G6; RG-anchor content and the Higgs quartic go to G7; Yukawas and proton-decay "
    "mediators go to G8; zero-mode classification and the recomputed ranks (34 gauge -> 452, 35 -> 451) go to G4; "
    "the naturalness of the tunings (DT splitting, O05, M_I) lies outside G1-G8."
)
G3_LEDGER_CLOSED_SCOPE = (
    "SM Pati-Salam track (g3_sm_target_track_v20 via final_g3_acceptance_gate_v20): exact SM-preserving global "
    "vacuum of the declared exact-X potential's 27-parameter benchmark with the light-doublet deformation eps > 0 "
    "(O06 = 2|kappa| r0 + eps, 0 < eps < 599/50), unique modulo SO(10) x U(1)_X x accidental U(1)_PQ, exact "
    "Hessian 451/35 with kernel = the symmetry orbit; tuned DT/M_I relations; model-level caveats routed to "
    "G4/G6/G7/G8"
)
G5_LEDGER_CLOSED_SCOPE = (
    "source-bound complete-potential BFB certificate on the SM Pati-Salam coupling vector (V4 >= |q|^4/167, "
    "g3_sm_pati_salam_candidate_v20), covering the G3 witness family because eps N_H is quadratic"
)
D3_RULE = (
    "D3: G1-G3 CLOSED does not approve an internal candidate; the closing track's downstream caveats must also "
    "be resolved, or G4 must be CLOSED"
)
SELF_CLAIM_NOTE = (
    "Input-report statuses ending in __G3_OPEN and flags g3_closed / G3_closed / report_closes_g3_by_itself = "
    "false are per-report self-claims that no single report closes G3; G3 is decided only by "
    "final_g3_acceptance_gate_v20 through this track, which requires those self-claims to stay false."
)

DECISIONS: dict[str, str] = {
    "D1": (
        "The final G3 gate has an SM (Pati-Salam) track that is the only route to closing G3; the non-SM "
        "SU(5)+Delta chiral-H track stays an integrity-checked diagnostic that can never close G3."
    ),
    "D2": (
        "The G3 witness is the light-but-massive doublet member V_PS,eps = V_PS + eps N_H (O06 = 2|kappa| r0 + eps, "
        "eps > 0 inside the perturbative window 0 < eps < 599/50) at r0 = 1/5, x0 = 1, kappa = -r0/4, whose Hessian "
        "kernel is exactly the symmetry orbit (451/35); the tuned eps = 0 point is not the witness."
    ),
    "D3": (
        "The internal-candidate tier stays WITHHELD even when G1-G3 are CLOSED: theory_confirmation_verdict_v20 "
        "also requires the closing track's downstream caveats to be resolved, or G4 CLOSED."
    ),
    "D4": (
        "G5 (BFB) is rebound to the Pati-Salam coupling vector, whose exact certificate V4 >= |q|^4/167 also covers "
        "the witness family because the eps N_H term is quadratic and leaves the quartic part unchanged."
    ),
    "D5": CAVEAT_ROUTING_SENTENCE,
    "D6": (
        "The cited classical theorems (Pluecker, Kostant-Lichtenstein, Iwasawa, Wirtinger, U(n) transitivity, "
        "highest-weight/Weyl dimension) and the 6 hand-argued elementary steps of the equality-set proof are "
        "accepted as G3-grade inputs, pinned verbatim by an allowlist and disclosed."
    ),
}

DISCLOSURES = (
    "Uniqueness is modulo SO(10) x U(1)_X x U(1)_PQ, where U(1)_PQ is an accidental symmetry of the benchmark; "
    "modulo SO(10) x U(1)_X alone the minimum set is a circle of orbits (the axion direction).",
    "The witness is the eps > 0 member V_PS,eps = V_PS + eps N_H (O06 = 2|kappa| r0 + eps); the tuned eps = 0 point "
    "(rank 447, nullity 39) is not the witness.",
    "The exact Hessian is certified at r0 = 1/5, x0 = 1, kappa = -r0/4 only; the global-minimum and equality-set "
    "theorem holds for every r0 > 0, x0 > 0, kappa^2 < 8 r0^2.",
    "V_PS is the adapted SOS form: it equals the compiler potential exactly coefficient by coefficient and per "
    "source-bound operator, and only in float64 end to end.",
    "The equality-set proof rests on 6 cited classical theorems and 6 hand-argued elementary steps, accepted as "
    "G3-grade inputs under decision D6 and pinned by an allowlist.",
    "The doublet-triplet splitting, the O05 cancellation and M_I/M_GUT are tuned relations.",
    "Potentials outside the 27-parameter benchmark family and its O06 + eps members are not covered.",
)

DOWNSTREAM_BLOCKERS = (
    "GAUGED_U1X_G4_G6_G7_G8_CLOSURE_REQUIRED",
    "G4_SM_WITNESS_ZERO_MODES_AND_RANKS_34_35_UNCLASSIFIED",
    "G6_SUB_M_I_COLOURED_STATES_AND_POSITIVITY_WITHOUT_EWSB",
    "G7_RG_ANCHOR_CONTENT_AND_HIGGS_QUARTIC_MATCHING",
    "G8_YUKAWA_SECTOR_AND_PROTON_DECAY_MEDIATORS",
)
FAIL_CLOSED_BLOCKERS = ("GAUGED_U1X_G3_G8_CLOSURE_REQUIRED", "G3_SM_PATI_SALAM_TRACK_NOT_CERTIFIED")

_G4_BLOCKER = DOWNSTREAM_BLOCKERS[1]
_G6_BLOCKER = DOWNSTREAM_BLOCKERS[2]
_G7_BLOCKER = DOWNSTREAM_BLOCKERS[3]
_G8_BLOCKER = DOWNSTREAM_BLOCKERS[4]

# The model-level caveats of the candidate, routed downstream by decision D5.  Evidence paths are into the
# candidate JSON; an entry is resolved only when its evidence has the "resolved_when" value (a missing or
# non-bool value is unresolved).  The G4 entry has no evidence: it is resolved only by G4 CLOSED, which the
# consumers check.
CAVEAT_SPECS: tuple[dict[str, Any], ...] = (
    {
        "id": "sub_M_I_coloured_126bar_states",
        "gate": "G6",
        "also_affects": ["G8"],
        "blocker": _G6_BLOCKER,
        "text": (
            "Light 126bar coloured states lie below M_I at the benchmark ((3,1)_1/3 near 0.24 M_I, (6,1)_4/3 and "
            "(1,1)_2 at M_I/sqrt(96), and further (3,1)_4/3, (6,1)_1/3 and (6,1)_2/3 states), so the complete "
            "physical spectrum and its thresholds are a G6 task."
        ),
        "key": ("flags", "coloured_scalars_only_at_M_GUT"),
        "resolved_when": True,
    },
    {
        "id": "positivity_without_EWSB",
        "gate": "G6",
        "also_affects": ["G4"],
        "blocker": _G6_BLOCKER,
        "text": (
            "The witness has H = 0 and a light but massive doublet (mass^2 eps M_GUT^2), so electroweak symmetry is "
            "not broken and a positive physical spectrum with electroweak breaking is a G6 task."
        ),
        "key": ("flags", "electroweak_symmetry_breaking_realized"),
        "resolved_when": True,
    },
    {
        "id": "phi17_benchmark_scale",
        "gate": "G6",
        "also_affects": ["G7"],
        "blocker": _G6_BLOCKER,
        "text": (
            "The benchmark uses x0 = 1 instead of the canonical Phi17 scale, so its GeV values are illustrative "
            "and the physical Phi17 threshold is a G6 task."
        ),
        "key": ("flags", "physical_benchmark_uses_canonical_phi17_scale"),
        "resolved_when": True,
    },
    {
        "id": "rg_anchor_field_content",
        "gate": "G7",
        "also_affects": [],
        "blocker": _G7_BLOCKER,
        "text": (
            "The RG anchor assumes a light (15,2,2) above M_I and a 2HDM below, while the witness has the (15,2,2) "
            "near 0.7 M_GUT and one light doublet, so re-solving the RG chain with the witness's field content is a "
            "G7 task."
        ),
        "key": ("flags", "rg_anchor_field_content_reproduced"),
        "resolved_when": True,
    },
    {
        "id": "higgs_quartic_matching",
        "gate": "G7",
        "also_affects": ["G6"],
        "blocker": _G7_BLOCKER,
        "text": (
            "The benchmark's tree-level light-doublet quartic 127/64 at M_I is too large for the measured Higgs "
            "mass and tree-level global minimality forbids the slightly negative SM value, so Higgs-quartic "
            "matching is a G7 task."
        ),
        "key": ("flags", "higgs_mass_compatible"),
        "resolved_when": True,
    },
    {
        "id": "tan_beta_one_light_doublet",
        "gate": "G8",
        "also_affects": ["G7"],
        "blocker": _G8_BLOCKER,
        "text": (
            "The light doublet is an equal 5/5bar mixture (a tan beta = 1 structure), so with 10_H-only Yukawas "
            "m_t = m_b at matching and the flavour structure is a G8 task."
        ),
        "key": ("checks", "light_doublet_is_equal_5_5bar_mixture"),
        "resolved_when": False,
    },
    {
        "id": "realistic_yukawa_sector",
        "gate": "G8",
        "also_affects": ["theory_validation_matrix flavour gate"],
        "blocker": _G8_BLOCKER,
        "text": (
            "The H-linear portals O15, O38, O45 and O28 vanish at the benchmark, so the witness has no realistic "
            "Yukawa sector; building one is a G8 (and flavour-gate) task."
        ),
        "key": ("flags", "realistic_yukawa_sector"),
        "resolved_when": True,
    },
    {
        "id": "proton_decay_mediators",
        "gate": "G8",
        "also_affects": ["G6"],
        "blocker": _G8_BLOCKER,
        "text": (
            "The sub-M_I (3,1)_1/3 state has proton-decay mediator quantum numbers and couples to 16.16 through "
            "the 126bar Yukawa that Majorana neutrino masses need, so its proton-decay consequences are a G8 task."
        ),
        "key": ("flags", "coloured_scalars_only_at_M_GUT"),
        "resolved_when": True,
    },
    {
        "id": "zero_modes_and_ranks_at_witness",
        "gate": "G4",
        "also_affects": [],
        "blocker": _G4_BLOCKER,
        "text": (
            "Zero-mode classification at the witness belongs to G4: the recomputed ranks 34/35 (SO(10) x U(1)_X "
            "rank 34, gauge quotient 452 with the axion included; SO(10) x U(1)_X x U(1)_PQ rank 35, "
            "massive/transverse quotient 451, i.e. quotients 452/451), the axion/PQ direction and the eps -> 0 "
            "tuned light doublet (4 real modes); it is resolved only when G4 is CLOSED."
        ),
        "key": None,
        "resolved_when": None,
    },
    {
        "id": "naturalness_of_tunings",
        "gate": "OUTSIDE_G1_G8",
        "also_affects": ["G3 closure_scope disclosure"],
        "blocker": None,
        "text": (
            "The doublet-triplet splitting (O46_1 = -(3/5) O46_54 and O06 = 2|kappa| r0 + eps), the O05 "
            "cancellation and the M_I/M_GUT hierarchy are tuned relations whose radiative stability lies outside "
            "G1-G8 and is disclosed in the G3 closure scope."
        ),
        "key": ("flags", "doublet_triplet_splitting_natural"),
        "resolved_when": True,
    },
)

ARTIFACT_INTEGRITY_NAMES = (
    "sm_candidate_report_executes",
    "sm_equality_set_report_executes",
    "sm_exact_hessian_report_executes",
    "sm_exact_hessian_eps_family_executes",
    "sm_sigma_hypercharge_audit_executes",
    "sm_reports_cross_bound",
    "sm_reports_do_not_overclaim",
    "sm_model_level_caveats_disclosed",
    "sm_unchecked_proof_inputs_pinned",
    "sm_float_evidence_not_promoted",
)
SCIENCE_CRITERIA_NAMES = (
    "G1_G2_exact_scoped_calculations_complete",
    "sm_target_unbroken_algebra_is_standard_model_exact",
    "sm_symmetry_orbit_ranks_33_34_35_exact",
    "sm_eps_witness_couplings_perturbative_exact",
    "sm_full_homogeneous_quartic_BFB_exact",
    "sm_eps_witness_exactly_stationary",
    "sm_eps_witness_global_gap_exact",
    "sm_eps_witness_equality_set_single_G_orbit_exact",
    "sm_decisive_theorem_string_bound",
    "sm_eps_witness_full_Hessian_rank_451_nullity_35_exact",
    "sm_eps_witness_quotient_strictly_positive_kernel_is_orbit_exact",
    "sm_raised_O06_control_rank_451_nullity_35_exact",
    "sm_eps_witness_light_doublet_mass_squared_equals_eps_exact",
)

_TOTAL_DIM = 486
_SO10_DIM = 45
_CANDIDATE_EXACT_CHECKS = 16
_COEFFICIENT_COUNT = 27
_MAX_COEFFICIENT = "73/8"
_TINY_INERTIA = "451/35/0"
_DOUBLET_CHART_INDICES = [222, 224, 226, 228]
_EXPECTED_EXACT_RANKS = {"scaled_T_u": 35, "so10": 33, "so10_plus_X": 34, "so10_plus_X_plus_PQ": 35}
_HESSIAN_BENCHMARK_STRINGS = {"r0": "1/5", "kappa": "-1/20", "x0": "1", "O06": "1/50"}
_EPS_MEMBERS = {"raised_O06": ("1/2500", "51/2500"), "tiny_eps": ("1/25000000", "500001/25000000")}


# ----------------------------------------------------------------------------
# Loading (fail closed) and strict helpers.
# ----------------------------------------------------------------------------


def load_inputs(paths: Mapping[str, Path | str] | None = None) -> dict[str, dict[str, Any]]:
    """Load the four SM inputs; each entry is {} if missing, unreadable, not a JSON object or empty."""
    chosen = dict(paths or {})
    loaded: dict[str, dict[str, Any]] = {}
    for key, name in INPUT_FILES.items():
        path = Path(chosen[key]) if key in chosen else ROOT / name
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, ValueError):
            value = {}
        loaded[key] = value if isinstance(value, dict) and value else {}
    return loaded


def missing_inputs(inputs: Mapping[str, Any]) -> list[str]:
    """INPUT_FILES names (in order) whose entry is not a non-empty dict."""
    source = inputs if isinstance(inputs, Mapping) else {}
    return [name for key, name in INPUT_FILES.items() if not _nonempty_dict(source.get(key))]


def _nonempty_dict(value: Any) -> bool:
    return isinstance(value, dict) and bool(value)


def _normalise(inputs: Mapping[str, Any] | None) -> dict[str, dict[str, Any]]:
    source = load_inputs() if inputs is None else inputs
    if not isinstance(source, Mapping):
        source = {}
    return {key: (source.get(key) if isinstance(source.get(key), dict) else {}) for key in INPUT_FILES}


def _dig(value: Any, *keys: str) -> Any:
    current = value
    for key in keys:
        if not isinstance(current, Mapping) or key not in current:
            return None
        current = current[key]
    return current


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _int_eq(value: Any, expected: int) -> bool:
    return _is_int(value) and value == expected


def _frac(value: Any) -> Fraction | None:
    """An exact rational from a string only (a bool, int or float is never parsed)."""
    if not isinstance(value, str):
        return None
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError):
        return None


def _all_true(value: Any, count: int) -> bool:
    return isinstance(value, dict) and len(value) == count and all(item is True for item in value.values())


def _true(value: Any, *keys: str) -> bool:
    return _dig(value, *keys) is True


def _false(value: Any, *keys: str) -> bool:
    return _dig(value, *keys) is False


def _safe(predicate: Any) -> bool:
    try:
        return bool(predicate()) is True
    except Exception:  # noqa: BLE001 - any malformed input fails closed
        return False


def _executes(report: Any, *, status: str, n_checks: int) -> bool:
    return bool(
        isinstance(report, dict)
        and bool(report)
        and _int_eq(report.get("n_failed"), 0)
        and report.get("failures") == []
        and report.get("status") == status
        and report.get("model_contract_id") == MODEL_CONTRACT_ID
        and _int_eq(report.get("n_checks"), n_checks)
        and _all_true(report.get("checks"), n_checks)
    )


def _str_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


# ----------------------------------------------------------------------------
# Exact values derived from the recorded rationals.
# ----------------------------------------------------------------------------


def _benchmark(inputs: Mapping[str, Mapping[str, Any]]) -> dict[str, Fraction | None]:
    """r0, kappa, O06 from the candidate's 1/5 benchmark and x0 from its defaults (None if unparseable)."""
    cand = inputs["candidate"]
    bench = _dig(cand, "candidate", "benchmarks", "1/5")
    return {
        "r0": _frac(_dig(bench, "r0")),
        "kappa": _frac(_dig(bench, "kappa")),
        "O06": _frac(_dig(bench, "O06")),
        "x0": _frac(_dig(cand, "candidate", "defaults", "x0")),
    }


def _benchmark_is_pinned(values: Mapping[str, Fraction | None]) -> bool:
    return all(values.get(key) is not None and values.get(key) == expected for key, expected in BENCHMARK.items())


def _o06_base(values: Mapping[str, Fraction | None]) -> Fraction:
    """2|kappa| r0 (raises on missing values: callers are fail closed)."""
    kappa, r0 = values["kappa"], values["r0"]
    if kappa is None or r0 is None:
        raise ValueError("benchmark not parsed")
    return 2 * abs(kappa) * r0


def _coefficients(cand: Mapping[str, Any]) -> dict[str, Fraction] | None:
    """The candidate's exact nonzero coefficients as rationals, or None unless all 27 are nonzero rational strings."""
    raw = _dig(cand, "candidate", "exact_nonzero_coefficients")
    if not isinstance(raw, dict) or len(raw) != _COEFFICIENT_COUNT:
        return None
    parsed = {name: _frac(value) for name, value in raw.items()}
    if not all(isinstance(name, str) for name in parsed):
        return None
    if any(value is None or value == 0 for value in parsed.values()):
        return None
    return parsed  # type: ignore[return-value]


def _eps_upper(values: Mapping[str, Fraction | None]) -> Fraction:
    return PERTURBATIVE_BOUND - _o06_base(values)


# ----------------------------------------------------------------------------
# Artifact integrity.
# ----------------------------------------------------------------------------


def _integrity(inputs: Mapping[str, Mapping[str, Any]]) -> dict[str, bool]:
    cand = inputs["candidate"]
    eq = inputs["equality_set"]
    hess = inputs["exact_hessian"]
    sig = inputs["sigma_hypercharge"]
    checks: dict[str, bool] = {}

    checks["sm_candidate_report_executes"] = _safe(
        lambda: _executes(cand, status=CANDIDATE_STATUS, n_checks=CANDIDATE_N_CHECKS)
        and cand.get("overall_state") == CANDIDATE_OVERALL_STATE
    )
    checks["sm_equality_set_report_executes"] = _safe(
        lambda: _executes(eq, status=EQUALITY_STATUS, n_checks=EQUALITY_N_CHECKS) and eq.get("theorem_claimed") is True
    )
    checks["sm_exact_hessian_report_executes"] = _safe(
        lambda: _executes(hess, status=HESSIAN_STATUS, n_checks=HESSIAN_N_CHECKS)
        and hess.get("overall_state") == HESSIAN_OVERALL_STATE
        and hess.get("theorem_claimed") is True
    )

    def eps_family_executes() -> bool:
        eps = hess.get("eps_family")
        return bool(
            checks["sm_exact_hessian_report_executes"]
            and isinstance(eps, dict)
            and _int_eq(eps.get("n_failed"), 0)
            and eps.get("failures") == []
            and _int_eq(eps.get("n_checks"), EPS_N_CHECKS)
            and _all_true(eps.get("checks"), EPS_N_CHECKS)
            and eps.get("theorem_claimed") is True
            and isinstance(eps.get("theorem"), str)
            and not eps["theorem"].startswith("NOT CLAIMED")
        )

    checks["sm_exact_hessian_eps_family_executes"] = _safe(eps_family_executes)
    checks["sm_sigma_hypercharge_audit_executes"] = _safe(
        lambda: _executes(sig, status=SIGMA_STATUS, n_checks=SIGMA_N_CHECKS)
        and _true(sig, "flags", "sm_singlet_direction_found")
        and _true(sig, "checks", "p_sm_singlet_Y0_is_the_standard_sm")
        and _true(sig, "pair_stabilizers", "p|sm_singlet_Y0", "is_sm_type")
        and _dig(sig, "sigma_directions", "sm_singlet_Y0", "formula") == SIGMA_STD_FORMULA
    )

    def cross_bound() -> bool:
        # One coupling vector, one benchmark and one sigma_std across the candidate, equality and Hessian reports.
        weights_raw = _dig(eq, "P2_sigma", "self_weights_54_1050bar_2772bar_4125")
        weights_eq = {key: _frac(value) for key, value in weights_raw.items()} if isinstance(weights_raw, dict) else {}
        coefficients = _dig(cand, "candidate", "exact_nonzero_coefficients")
        weights_cand: dict[str, Fraction | None] = {}
        if isinstance(coefficients, dict):
            for name, channel in O27_CHANNELS:
                value = _frac(coefficients.get(name))
                weights_cand[channel] = None if value is None else 8 * value
        symbolic = _dig(eq, "sos_decomposition", "symbolic_coefficient_identity")
        cand_values = _benchmark(inputs)
        hess_values = {key: _frac(_dig(hess, "benchmark", key)) for key in ("r0", "kappa", "x0", "O06")}
        return bool(
            weights_eq == SELF_WEIGHTS
            and weights_cand == SELF_WEIGHTS
            and _int_eq(_dig(eq, "P3_H_S_Phi17_phases", "operators", "count"), 27)
            and _int_eq(_dig(eq, "P3_H_S_Phi17_phases", "operators", "count_at_kappa_0"), 25)
            and _dig(cand, "exact_certificate", "equality_set", "equality_set_certificate", "status") == EQUALITY_STATUS
            and _int_eq(_dig(cand, "exact_certificate", "equality_set", "equality_set_certificate", "n_failed"), 0)
            and _true(symbolic, "negative", "all_residuals_zero")
            and _int_eq(_dig(symbolic, "negative", "parameters_compared"), 27)
            and _true(symbolic, "positive", "all_residuals_zero")
            and _int_eq(_dig(symbolic, "positive", "parameters_compared"), 27)
            and _true(symbolic, "zero", "all_residuals_zero")
            and _int_eq(_dig(symbolic, "zero", "parameters_compared"), 25)
            and isinstance(coefficients, dict)
            and bool(coefficients)
            and _dig(hess, "benchmark", "exact_coefficients") == coefficients
            and _benchmark_is_pinned(cand_values)
            and _benchmark_is_pinned(hess_values)
            and all(hess_values[key] == cand_values[key] for key in BENCHMARK)
            and cand_values["O06"] == _o06_base(cand_values)
            and _true(hess, "candidate_float64_claims", "all_claims_present_and_consistent")
            and _true(hess, "symmetry_tangents", "matches_equality_module_ranks")
            and _dig(cand, "sm_embedding", "sigma_std_formula") == SIGMA_STD_FORMULA
            and _dig(hess, "eps_family", "L1_equality_set", "relies_on", "required_status") == EQUALITY_STATUS
        )

    checks["sm_reports_cross_bound"] = _safe(cross_bound)

    def no_overclaim() -> bool:
        eq_flags = eq.get("flags")
        hess_flags = hess.get("flags")
        return bool(
            _false(cand, "flags", "g3_closed")
            and _false(cand, "flags", "whole_model_validated")
            and _false(cand, "flags", "whole_model_excluded")
            and isinstance(eq_flags, dict)
            and _false(eq_flags, "g3_closed")
            and _false(eq_flags, "report_closes_g3_by_itself")
            and _false(eq_flags, "whole_model_validated")
            and _false(eq_flags, "whole_model_excluded")
            and "candidate_wired_into_g3_gate" not in eq_flags
            and isinstance(hess_flags, dict)
            and _false(hess_flags, "G3_closed")
            and _false(hess_flags, "report_closes_g3_by_itself")
            and "candidate_wired_into_g3_gate" not in hess_flags
            and hess.get("G3_closed") is False
            and _false(hess, "eps_family", "final_acceptance_test", "closes_g3_by_itself")
            and _false(sig, "flags", "g3_closed")
        )

    checks["sm_reports_do_not_overclaim"] = _safe(no_overclaim)

    def caveats_disclosed() -> bool:
        scope_open = _dig(cand, "scope", "open")
        return bool(
            all(isinstance(_dig(cand, "flags", name), bool) for name in MODEL_LEVEL_FLAGS)
            and isinstance(scope_open, list)
            and bool(scope_open)
            and all(isinstance(item, str) and bool(item) for item in scope_open)
        )

    checks["sm_model_level_caveats_disclosed"] = _safe(caveats_disclosed)
    checks["sm_unchecked_proof_inputs_pinned"] = _safe(
        lambda: _dig(eq, "scope", "cited_not_machine_checked") == list(PINNED_CITED_NOT_MACHINE_CHECKED)
        and _dig(eq, "scope", "elementary_not_machine_checked") == list(PINNED_ELEMENTARY_NOT_MACHINE_CHECKED)
    )

    def float_not_promoted() -> bool:
        eq_float = _dig(eq, "scope", "float64_evidence_only")
        hess_float = _dig(hess, "scope", "float64_evidence_only")
        cand_float = _dig(cand, "scope", "float64_only")
        note = _dig(cand, "numerical_global_search", "note")
        return bool(
            _true(cand, "flags", "hessian_kernel_count_is_float64")
            and isinstance(cand_float, list)
            and bool(cand_float)
            and isinstance(note, str)
            and note.startswith("numerical evidence")
            and isinstance(eq_float, list)
            and any(isinstance(item, str) and item.startswith("end-to-end compiler = SOS form") for item in eq_float)
            and isinstance(hess_float, list)
            and any(
                isinstance(item, str) and item.startswith("compiler = exact operators end to end") for item in hess_float
            )
        )

    checks["sm_float_evidence_not_promoted"] = _safe(float_not_promoted)
    return {name: checks[name] is True for name in ARTIFACT_INTEGRITY_NAMES}


# ----------------------------------------------------------------------------
# Science criteria.
# ----------------------------------------------------------------------------


def _bfb_candidate_items(cand: Mapping[str, Any]) -> bool:
    """The candidate's part of the BFB criterion: the exact certificate V4 >= |q|^4/167, recomputed."""
    alpha = _dig(cand, "exact_certificate", "exact_quartic_bound", "coefficients_alpha")
    beta = _dig(cand, "exact_certificate", "exact_quartic_bound", "chart_norm_weights_beta")
    if not (isinstance(alpha, dict) and isinstance(beta, dict) and alpha and set(alpha) == set(beta)):
        return False
    terms = [(_frac(beta[key]), _frac(alpha[key])) for key in sorted(alpha)]
    if not all(b is not None and a is not None and a > 0 for b, a in terms):
        return False
    constant = 1 / sum(b * b / a for b, a in terms)  # type: ignore[operator]
    return bool(
        _true(cand, "flags", "bfb_certified")
        and _true(cand, "exact_certificate", "bfb_certified")
        and _true(cand, "exact_certificate", "checks", "quartic_part_strictly_positive")
        and _dig(cand, "exact_certificate", "exact_quartic_bound", "constant") == QUARTIC_BOUND_CONSTANT
        and _true(cand, "exact_certificate", "exact_quartic_bound", "matches_recorded_constant")
        and constant == Fraction(1, 167)
        and Fraction(QUARTIC_BOUND_CONSTANT) == constant
        and _true(cand, "exact_certificate", "checks", "A_square_recoupling_exact")
        and _true(cand, "exact_certificate", "checks", "C_square_recoupling_exact")
        and _true(cand, "exact_certificate", "checks", "Phi_H_term_is_exact_wedge_square")
        and _true(cand, "exact_certificate", "checks", "coefficient_map_equals_adapted_SOS_expansion_symbolically")
    )


def _eps_check(hess: Mapping[str, Any], name: str) -> bool:
    return _true(hess, "eps_family", "checks", name)


def _science(inputs: Mapping[str, Mapping[str, Any]], prerequisites: Mapping[str, bool]) -> dict[str, bool]:
    cand = inputs["candidate"]
    eq = inputs["equality_set"]
    hess = inputs["exact_hessian"]
    sig = inputs["sigma_hypercharge"]
    values = _benchmark(inputs)
    criteria: dict[str, bool] = {}

    criteria["G1_G2_exact_scoped_calculations_complete"] = _safe(
        lambda: prerequisites.get("G1_G2_exact_scoped_calculations_complete") is True
        and _int_eq(_dig(cand, "candidate", "exact_X_parameter_count"), 51)
        and _true(cand, "candidate", "all_parameters_in_exact_X_contract")
    )

    def standard_model() -> bool:
        heavy = _dig(cand, "sm_embedding", "heavy_pair_stabilizer")
        full = _dig(cand, "sm_embedding", "full_state_stabilizer_so10_plus_u1x")
        charges = _dig(cand, "sm_embedding", "sigma_std_exact_charges")
        pair = _dig(sig, "pair_stabilizers", "p|sm_singlet_Y0")
        return bool(
            _true(cand, "flags", "target_unbroken_algebra_is_standard_model")
            and _true(cand, "flags", "candidate_is_sm_vacuum")
            and _true(cand, "checks", "unbroken_algebra_is_exactly_standard_model")
            and _true(heavy, "is_sm_type")
            and _true(heavy, "contains_standard_sm_algebra")
            and _false(heavy, "contains_flipped_sm_algebra")
            and _int_eq(_dig(heavy, "stabilizer_dimension"), 12)
            and _int_eq(_dig(full, "stabilizer_dimension"), 12)
            and _int_eq(_dig(full, "u1x_admixture_dimension"), 0)
            and _dig(charges, "Y") == "0"
            and _dig(charges, "Q_em") == "0"
            and _true(charges, "SU3_colour_singlet")
            and _true(sig, "checks", "p_sm_singlet_Y0_is_the_standard_sm")
            and _true(pair, "is_sm_type")
            and _dig(pair, "centre_proportional_to") == ["Y_standard"]
            and _dig(sig, "sigma_directions", "sm_singlet_Y0", "formula") == SIGMA_STD_FORMULA
        )

    criteria["sm_target_unbroken_algebra_is_standard_model_exact"] = _safe(standard_model)

    def orbit_ranks() -> bool:
        tangent = _dig(eq, "P3_H_S_Phi17_phases", "tangent_rank")
        exact_ranks = _dig(hess, "symmetry_tangents", "exact_ranks")
        stabilizer = _dig(cand, "sm_embedding", "full_state_stabilizer_so10_plus_u1x", "stabilizer_dimension")
        return bool(
            _int_eq(_dig(tangent, "rank_so10"), 33)
            and _int_eq(_dig(tangent, "rank_so10_plus_X"), 34)
            and _int_eq(_dig(tangent, "rank_so10_plus_X_plus_PQ"), 35)
            and _int_eq(_dig(tangent, "kernel_dimension"), 12)
            and _true(tangent, "kernel_has_no_X_or_PQ_component")
            and _true(eq, "checks", "P3_orbit_tangent_rank_35_kernel_12_pure_so10")
            and _int_eq(stabilizer, 12)
            and _SO10_DIM - tangent["rank_so10"] == stabilizer
            and isinstance(exact_ranks, dict)
            and set(exact_ranks) == set(_EXPECTED_EXACT_RANKS)
            and all(_int_eq(exact_ranks[key], value) for key, value in _EXPECTED_EXACT_RANKS.items())
        )

    criteria["sm_symmetry_orbit_ranks_33_34_35_exact"] = _safe(orbit_ranks)

    def couplings() -> bool:
        coefficients = _coefficients(cand)
        if coefficients is None or O06_ID not in coefficients:
            return False
        base = _o06_base(values)
        upper = PERTURBATIVE_BOUND - base
        maximum = max(abs(value) for value in coefficients.values())
        others = max(abs(value) for name, value in coefficients.items() if name != O06_ID)
        members_ok = True
        for variant, (eps_text, o06_text) in _EPS_MEMBERS.items():
            member = _dig(hess, "eps_family", "consistency_certificates", variant)
            eps = _frac(_dig(member, "eps"))
            o06 = _frac(_dig(member, "O06"))
            members_ok = bool(
                members_ok
                and eps is not None
                and o06 is not None
                and _dig(member, "eps") == eps_text
                and _dig(member, "O06") == o06_text
                and 0 < eps < upper
                and o06 == base + eps
            )
        return bool(
            _int_eq(_dig(cand, "candidate", "nonzero_count"), _COEFFICIENT_COUNT)
            and _true(cand, "candidate", "all_parameters_in_exact_X_contract")
            and _dig(cand, "candidate", "maximum_absolute_coefficient") == _MAX_COEFFICIENT
            and maximum == Fraction(_MAX_COEFFICIENT)
            and others == Fraction(_MAX_COEFFICIENT)
            and others < PERTURBATIVE_BOUND
            and _benchmark_is_pinned(values)
            and base == BENCHMARK["O06"]
            and coefficients[O06_ID] == base
            and upper > 0
            and str(upper) == EPS_WINDOW_UPPER
            and members_ok
            and _eps_check(hess, "L1_V_eps_differs_from_V_only_in_O06_by_eps")
            and _dig(hess, "eps_family", "final_acceptance_test", "eps_window", "upper_exclusive") == EPS_WINDOW_UPPER
        )

    criteria["sm_eps_witness_couplings_perturbative_exact"] = _safe(couplings)
    criteria["sm_full_homogeneous_quartic_BFB_exact"] = _safe(
        lambda: _bfb_candidate_items(cand) and _eps_check(hess, "L1_N_H_homogeneous_quadratic_so_quartic_part_unchanged")
    )
    criteria["sm_eps_witness_exactly_stationary"] = _safe(
        lambda: _true(cand, "exact_certificate", "exactly_stationary")
        and _true(cand, "exact_certificate", "global_minimum_certified")
        and _true(cand, "exact_slice", "gradient_vanishes_exactly")
        and _dig(cand, "exact_slice", "gradient_at_vacuum") == ["0", "0", "0", "0"]
        and _true(cand, "checks", "exact_state_binding")
        and _true(hess, "flags", "exact_gradient_zero")
        and _eps_check(hess, "L1_grad_V_eps_vanishes_at_q0_for_every_eps")
        and _true(hess, "exact_certificate_raised_O06", "gradient_exactly_zero")
    )

    def global_gap() -> bool:
        r0, x0 = values["r0"], values["x0"]
        if r0 is None or x0 is None:
            return False
        v0 = -1 - r0**4 / 8 - r0**4 - x0**4 / 32
        recorded = _frac(_dig(cand, "candidate", "benchmarks", "1/5", "V0"))
        slice_value = _frac(_dig(cand, "exact_slice", "value_at_vacuum"))
        return bool(
            _true(cand, "exact_certificate", "global_minimum_certified")
            and _true(cand, "exact_certificate", "V_at_vacuum_equals_V0")
            and _all_true(_dig(cand, "exact_certificate", "checks"), _CANDIDATE_EXACT_CHECKS)
            and _true(cand, "exact_certificate", "symbolic_identity", "all_residuals_zero")
            and _int_eq(_dig(cand, "exact_certificate", "symbolic_identity", "parameters_compared"), _COEFFICIENT_COUNT)
            and recorded is not None
            and slice_value is not None
            and v0 == recorded == slice_value == V0_EXPECTED
            and _true(hess, "flags", "eps_family_equality_set_unchanged")
        )

    criteria["sm_eps_witness_global_gap_exact"] = _safe(global_gap)

    def single_orbit() -> bool:
        r0, kappa = values["r0"], values["kappa"]
        if r0 is None or kappa is None:
            return False
        return bool(
            _true(eq, "flags", "equality_set_unique_modulo_symmetry_certified")
            and _true(eq, "flags", "theorem_claimed")
            and _true(eq, "flags", "uniqueness_is_modulo_G_including_accidental_U1_PQ")
            and _false(eq, "flags", "unique_modulo_SO10_x_U1X_alone")
            and _false(eq, "flags", "kappa_squared_equal_8_r0_squared_claimed")
            and kappa * kappa < 8 * r0 * r0
            and _true(cand, "exact_certificate", "equality_set", "unique_modulo_symmetry_certified")
            and _eps_check(hess, "L1_equality_report_proved_status_and_premises")
            and _eps_check(hess, "L1_N_H_is_sum_of_squares_of_u_H")
            and _eps_check(hess, "L1_N_H_invariant_under_G")
            and _eps_check(hess, "L1_operator_dictionary_maps_O06_to_N_H")
            and _eps_check(hess, "L1_O06_compiler_direction_is_unit_Hdag_i_H_i_without_dressing")
            and _eps_check(hess, "L1_benchmark_inside_equality_domain_kappa_squared_below_8_r0_squared")
            and _true(hess, "flags", "eps_family_equality_set_unchanged")
        )

    criteria["sm_eps_witness_equality_set_single_G_orbit_exact"] = _safe(single_orbit)
    criteria["sm_decisive_theorem_string_bound"] = _safe(
        lambda: _dig(hess, "eps_family", "final_acceptance_test", "required_statement") == SM_FINAL_THEOREM
        and _true(hess, "eps_family", "final_acceptance_test", "currently_passes")
        and _false(hess, "eps_family", "final_acceptance_test", "closes_g3_by_itself")
    )

    def full_hessian() -> bool:
        orbit = _dig(eq, "P3_H_S_Phi17_phases", "tangent_rank", "rank_so10_plus_X_plus_PQ")
        if not _int_eq(orbit, 35):
            return False
        l2 = _dig(hess, "eps_family", "L2_hessian")
        every = _dig(l2, "for_every_eps_positive")
        members = _dig(hess, "eps_family", "consistency_certificates")
        benchmark = _dig(hess, "benchmark")
        return bool(
            _true(hess, "flags", "source_binding_exact")
            and _true(hess, "flags", "proof_grade")
            and _true(hess, "flags", "exact_PSD")
            and _true(hess, "flags", "eps_family_theorem_claimed")
            and _true(hess, "flags", "eps_family_kernel_equals_symmetry_orbit")
            and _eps_check(hess, "L2_H0_PSD_exact")
            and _eps_check(hess, "L2_H0_kernel_is_span_T35_plus_D4")
            and _eps_check(hess, "L2_hess_u_N_H_is_2_P_H_hence_PSD_with_kernel_H_equal_0")
            and _eps_check(hess, "L2_D4_inside_H_block")
            and _eps_check(hess, "L2_T35_vanishes_on_H_block")
            and _eps_check(hess, "L2_rank_T35_35_rank_D4_4_rank_T35_plus_D4_39")
            and _eps_check(hess, "L2_hess_N_H_annihilates_T35_and_doubles_D4")
            and _eps_check(hess, "L2_dim_ker_H0_cap_ker_hess_N_H_equals_35")
            and _int_eq(_dig(l2, "dim_ker_H0_cap_ker_B"), orbit)
            and _true(every, "PSD")
            and _int_eq(_dig(every, "rank"), _TOTAL_DIM - orbit)
            and _int_eq(_dig(every, "nullity"), orbit)
            and _dig(every, "kernel") == EPS_KERNEL_TEXT
            and all(
                _dig(members, variant, "inertia_positive_zero_negative") == _TINY_INERTIA
                and _true(members, variant, "kernel_equals_symmetry_tangents")
                for variant in _EPS_MEMBERS
            )
            and all(_dig(benchmark, key) == value for key, value in _HESSIAN_BENCHMARK_STRINGS.items())
        )

    criteria["sm_eps_witness_full_Hessian_rank_451_nullity_35_exact"] = _safe(full_hessian)

    def quotient_positive() -> bool:
        members = _dig(hess, "eps_family", "consistency_certificates")
        tuned = _dig(hess, "exact_certificate")
        return bool(
            _true(hess, "flags", "eps_family_strictly_positive_on_symmetry_quotient_for_all_eps_positive")
            and _int_eq(
                _dig(hess, "eps_family", "L2_hessian", "for_every_eps_positive",
                     "strictly_positive_on_symmetry_quotient_dimension"),
                451,
            )
            and all(_true(members, variant, "strictly_positive_on_symmetry_quotient") for variant in _EPS_MEMBERS)
            and _int_eq(_dig(tuned, "exact_rank"), 447)
            and _int_eq(_dig(tuned, "exact_nullity"), 39)
            and _int_eq(_dig(tuned, "zero_modes_beyond_symmetry_orbit"), 4)
            and _true(tuned, "kernel_equals_expected_span")
            and _true(tuned, "exact_PSD")
            and _int_eq(_dig(tuned, "inertia", "negative"), 0)
            and _int_list_eq(_dig(hess, "light_doublet_directions", "chart_indices"), _DOUBLET_CHART_INDICES)
        )

    criteria["sm_eps_witness_quotient_strictly_positive_kernel_is_orbit_exact"] = _safe(quotient_positive)

    def raised_control() -> bool:
        raised = _dig(hess, "exact_certificate_raised_O06")
        r0 = values["r0"]
        raise_by = _frac(_dig(hess, "benchmark", "O06_raise"))
        return bool(
            r0 is not None
            and _int_eq(_dig(raised, "exact_rank"), 451)
            and _int_eq(_dig(raised, "exact_nullity"), 35)
            and _dig(raised, "kernel_spanning_set") == "35 symmetry tangents"
            and _true(raised, "kernel_equals_expected_span")
            and _true(raised, "strictly_positive_on_kernel_complement")
            and _true(raised, "exact_PSD")
            and _true(raised, "gradient_exactly_zero")
            and _true(raised, "strictly_positive_on_symmetry_quotient")
            and _int_eq(_dig(raised, "inertia", "negative"), 0)
            and _int_eq(_dig(raised, "zero_modes_beyond_symmetry_orbit"), 0)
            and _dig(raised, "spectral_gap", "lambda_over_r0_squared") == "1/100"
            and _dig(hess, "benchmark", "O06_raise") == "1/2500"
            and raise_by is not None
            and raise_by == r0 * r0 / 100
            and _true(hess, "flags", "raised_O06_strict_quotient_positive")
            and _true(hess, "flags", "raised_O06_strictly_positive_on_symmetry_quotient")
        )

    criteria["sm_raised_O06_control_rank_451_nullity_35_exact"] = _safe(raised_control)
    criteria["sm_eps_witness_light_doublet_mass_squared_equals_eps_exact"] = _safe(
        lambda: _true(hess, "flags", "doublet_mass_squared_equals_eps")
        and _eps_check(hess, "doublet_H_block_decouples_from_the_rest_at_q0")
        and _eps_check(hess, "doublet_H_block_diagonal_Re_H6_9_curvature_0_others_positive")
        and _eps_check(hess, "doublet_H_block_curvatures_are_0_r0sq_1_and_1_plus_r0sq_as_stated")
        and _eps_check(hess, "doublet_rest_block_has_no_eigenvalue_in_open_interval_0_to_r0sq_over_96")
        and _eps_check(hess, "doublet_Re_H6_9_exact_eigenvectors_with_eigenvalue_eps_at_raised_and_tiny")
        and _eps_check(hess, "doublet_eps_is_smallest_nonzero_eigenvalue_multiplicity_4_at_raised_and_tiny")
    )
    return {name: criteria[name] is True for name in SCIENCE_CRITERIA_NAMES}


def _int_list_eq(value: Any, expected: list[int]) -> bool:
    return (
        isinstance(value, list)
        and len(value) == len(expected)
        and all(_int_eq(item, target) for item, target in zip(value, expected))
    )


# ----------------------------------------------------------------------------
# Witness, caveats and the G5 binding.
# ----------------------------------------------------------------------------


def _string_or_none(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _json_leaf(value: Any) -> Any:
    """A JSON-native scalar for the caveat evidence record (anything else is recorded as None)."""
    if value is None or isinstance(value, (bool, str)) or _is_int(value):
        return value
    return None


def _witness(inputs: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    hess = inputs["exact_hessian"]
    bench = _dig(hess, "benchmark")
    hess_values = {"r0": _frac(_dig(bench, "r0")), "kappa": _frac(_dig(bench, "kappa"))}
    upper: str | None
    try:
        upper = str(_eps_upper(hess_values))
    except Exception:  # noqa: BLE001 - an unparsed benchmark records None
        upper = None
    members = _dig(hess, "eps_family", "consistency_certificates")
    return {
        "id": "sm_pati_salam_eps_member",
        "potential": "V_PS,eps = V_PS + eps N_H",
        "definition": "O06 = 2|kappa| r0 + eps, the other 26 couplings of the 27-parameter benchmark unchanged",
        "benchmark": {
            "r0": _string_or_none(_dig(bench, "r0")),
            "x0": _string_or_none(_dig(bench, "x0")),
            "kappa": _string_or_none(_dig(bench, "kappa")),
            "O06_base": _string_or_none(_dig(bench, "O06")),
        },
        "vacuum": "(Phi, H, Sigma, S, Phi17) = (p, 0, r0 sigma_std, r0, x0)",
        "p": "e6789",
        "sigma_std": SIGMA_STD_FORMULA,
        "symmetry_group": "SO(10) x U(1)_X x U(1)_PQ (U(1)_PQ accidental)",
        "eps_window": {
            "lower_exclusive": "0",
            "upper_exclusive": upper,
            "meaning": "O06_eps = 2|kappa| r0 + eps < 12 < 4 pi",
        },
        "certified_members": {
            "raised_O06": _string_or_none(_dig(members, "raised_O06", "eps")),
            "tiny_eps": _string_or_none(_dig(members, "tiny_eps", "eps")),
        },
        "hessian_for_every_eps_positive": "PSD, rank 451, nullity 35, kernel = the 35-dimensional orbit tangent space",
        "doublet_mass_squared": (
            "eps (units M_GUT^2): light but massive for 0 < eps << r0^2; no electroweak symmetry breaking"
        ),
        "tuned_limit_not_the_witness": (
            "eps = 0: rank 447, nullity 39, kernel = 35 orbit tangents + 4 tuned light-doublet directions"
        ),
        "sentence": WITNESS_SENTENCE,
        "decision": "D2",
    }


def _downstream_caveats(inputs: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    cand = inputs["candidate"]
    rows = []
    for spec in CAVEAT_SPECS:
        key = spec["key"]
        if key is None:
            evidence = {"artifact": None, "key": None, "value": None}
            resolved = False
        else:
            raw = _dig(cand, *key)
            evidence = {"artifact": INPUT_FILES["candidate"], "key": ".".join(key), "value": _json_leaf(raw)}
            resolved = isinstance(raw, bool) and raw is spec["resolved_when"]
        rows.append(
            {
                "id": spec["id"],
                "gate": spec["gate"],
                "also_affects": list(spec["also_affects"]),
                "blocker": spec["blocker"],
                "text": spec["text"],
                "evidence": evidence,
                "resolved": bool(resolved),
            }
        )
    return rows


def _scope_open(cand: Mapping[str, Any]) -> list[str]:
    value = _dig(cand, "scope", "open")
    return list(value) if _str_list(value) else []


def _valid_coefficient_strings(cand: Mapping[str, Any]) -> dict[str, str]:
    raw = _dig(cand, "candidate", "exact_nonzero_coefficients")
    if _coefficients(cand) is None or not isinstance(raw, dict):
        return {}
    if not all(isinstance(value, str) for value in raw.values()):
        return {}
    return {name: raw[name] for name in sorted(raw)}


def _g5_binding(inputs: Mapping[str, Mapping[str, Any]], integrity: Mapping[str, bool]) -> dict[str, Any]:
    cand = inputs["candidate"]
    hess = inputs["exact_hessian"]
    on_vector = bool(integrity["sm_candidate_report_executes"] and _safe(lambda: _bfb_candidate_items(cand)))
    covers = bool(
        integrity["sm_exact_hessian_eps_family_executes"]
        and _safe(lambda: _eps_check(hess, "L1_N_H_homogeneous_quadratic_so_quartic_part_unchanged"))
    )
    return {
        "source": "g3_sm_pati_salam_candidate_v20",
        "report": INPUT_FILES["candidate"],
        "key": "candidate.exact_nonzero_coefficients",
        "coupling_vector": "SM Pati-Salam 27-parameter benchmark (r0 = 1/5, x0 = 1, kappa = -r0/4, O06 = 2|kappa| r0)",
        "coefficients": _valid_coefficient_strings(cand),
        "quartic_bound": "V4(q) >= |q|^4/167",
        "quartic_bound_constant": _string_or_none(_dig(cand, "exact_certificate", "exact_quartic_bound", "constant")),
        "certified_on_coupling_vector": on_vector,
        "covers_eps_witness_family": covers,
        "certified": bool(on_vector and covers),
        "superseded_vector": (
            "historical 27-parameter SOS vector (GAUGED_U1X_G3_SOS_CANDIDATE_V20.json coefficient_vector): its BFB "
            "certificate stays valid for that vector and is retained as constructive_frontier_evidence, but it no "
            "longer carries G5"
        ),
        "decision": "D4",
    }


def g5_bfb_binding(inputs: Mapping[str, Any]) -> dict[str, Any]:
    """The G5 BFB binding on the Pati-Salam coupling vector (decision D4), fail closed."""
    normalised = _normalise(inputs)
    return _g5_binding(normalised, _integrity(normalised))


# ----------------------------------------------------------------------------
# The track.
# ----------------------------------------------------------------------------


def evaluate_sm_track(
    inputs: Mapping[str, Any] | None = None,
    *,
    prerequisites: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate the SM Pati-Salam track; ``prerequisites`` None means not evaluated (all False)."""
    normalised = _normalise(inputs)
    evaluated = prerequisites is not None
    supplied = prerequisites if isinstance(prerequisites, Mapping) else {}
    prereq = {key: supplied.get(key) is True for key in PREREQUISITE_KEYS}

    integrity = _integrity(normalised)
    science = _science(normalised, prereq)
    release = {key: prereq[key] for key in RELEASE_PREREQUISITE_KEYS}
    mathematically_closed = all(integrity.values()) and all(science.values())
    closed = bool(mathematically_closed and all(release.values()))
    blockers = [
        name
        for block in (integrity, science, release)
        for name, value in block.items()
        if value is not True
    ]
    caveats = _downstream_caveats(normalised)
    return {
        "track": TRACK_NAME,
        "role": TRACK_ROLE,
        "model_contract_id": MODEL_CONTRACT_ID,
        "inputs": {
            key: {"file": name, "loaded": _nonempty_dict(normalised[key])} for key, name in INPUT_FILES.items()
        },
        "missing_inputs": missing_inputs(normalised),
        "artifact_integrity": integrity,
        "science_criteria": science,
        "release_prerequisites": release,
        "prerequisites_evaluated": evaluated,
        "mathematically_closed": bool(mathematically_closed),
        "closed": closed,
        "blockers": blockers,
        "decisive_theorem": SM_FINAL_THEOREM,
        "decisive_theorem_emitted_by": DECISIVE_THEOREM_EMITTED_BY,
        "witness": _witness(normalised),
        "closure_scope": CLOSURE_SCOPE,
        "disclosures": list(DISCLOSURES),
        "downstream_caveats": caveats,
        "downstream_caveats_scope_open": _scope_open(normalised["candidate"]),
        "downstream_caveats_resolved": all(row["resolved"] for row in caveats),
        "downstream_blockers": list(DOWNSTREAM_BLOCKERS),
        "unchecked_proof_inputs": {
            "cited_theorems": list(PINNED_CITED_NOT_MACHINE_CHECKED),
            "elementary_steps": list(PINNED_ELEMENTARY_NOT_MACHINE_CHECKED),
            "accepted_under": "D6",
            "allowlist_matches": integrity["sm_unchecked_proof_inputs_pinned"],
        },
        "g5_bfb_binding": _g5_binding(normalised, integrity),
        "decisions": dict(DECISIONS),
        "self_claim_note": SELF_CLAIM_NOTE,
    }


def main(argv: list[str] | None = None) -> int:
    """Print the evaluation (prerequisites not evaluated) and return a health code.

    Returns 0 iff every artifact-integrity entry and every science entry except
    the prerequisite-gated ``G1_G2_exact_scoped_calculations_complete`` is
    True, else 1.  That entry and the release prerequisites need the ledger,
    which this pure CLI does not evaluate, so they are excluded here (the track
    is still reported as not closed).
    """
    del argv  # no options
    result = evaluate_sm_track()
    print(json.dumps(result, indent=2, sort_keys=True))
    science = {
        name: value
        for name, value in result["science_criteria"].items()
        if name != "G1_G2_exact_scoped_calculations_complete"
    }
    passed = all(result["artifact_integrity"].values()) and all(science.values())
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
