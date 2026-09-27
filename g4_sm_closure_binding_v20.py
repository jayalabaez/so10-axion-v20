#!/usr/bin/env python3
"""Pure G4 closure predicate: binds the exact G4 certificate to the G1-G8 ledger (v20).

The G4 gate ("Gauge quotient, axion directions, and physical Hessian") is decided by g1_g8_gate_ledger_v20, and
only through this module: the ledger closes G4 iff the model contract is attested, G3 is CLOSED and
evaluate_g4_binding(G4_SM_PATI_SALAM_PHYSICAL_QUOTIENT_V20.json) is certified.  The certificate itself
(g4_sm_pati_salam_physical_quotient_v20) never closes G4 by itself.

evaluate_g4_binding checks 16 fail-closed criteria (5 integrity + 11 science): the report executes with 69/69
checks (every conclusion flag true, every section's checks true and mirrored exactly, the fresh exact Hessian
inertias bound by value), its premises hold, it does not overclaim, its float64 evidence is not promoted, its scope limits are
disclosed, and it certifies at the G3 witness (r0 = 1/5, x0 = 1, kappa = -r0/4, every 0 < eps < 599/50) the
orbit ranks 33/34/35, the gauge quotient 452 and the massive/transverse quotient 451, 34 eaten Goldstones with
PQ global, the exact physical axion, the Hessian inertia 451/1/0 on the gauge quotient, the 35 zero modes
(34 eaten + the axion) with no negative mode, the tuned-limit SM doublet lifted by lambda_eff = 127/64, the
vector-boson Gram rank 34, the verbatim required statement and the ledger's full G4 open scope.  Every
criterion is wrapped so that malformed input fails closed; counts are int-not-bool and rationals are compared
as exact canonical strings.

Scope (carried into the ledger's closed scope): tree level, at the benchmark witness only; the compiler
binding is float64; the axion zero mode is exact only for the renormalizable PQ-neutral benchmark potential
(the QCD anomaly and PQ-violating operators such as Phi17^4 conj(S)^17/M_Pl^17 give it a mass).  A CLOSED G4
meets decision D3's G4 condition but does not approve the internal-candidate tier: the user's decision D-E
(2026-09-26) holds that approval until G7 is CLOSED (theory_confirmation_verdict_v20); G6-G8 are not addressed.

The module imports only the standard library, writes nothing and runs nothing at import time.  The superseded
p+delta quotient report (ranks 37/38, quotients 449/448) and every chiral-track report fail the predicate.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parent
MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
G4_SOURCE = "g4_sm_pati_salam_physical_quotient_v20"
G4_REPORT_FILE = "G4_SM_PATI_SALAM_PHYSICAL_QUOTIENT_V20.json"
REQUIRED_STATUS = "G4_SM_PATI_SALAM_PHYSICAL_QUOTIENT_CERTIFIED__WIRED_AS_G4_EVIDENCE"
REQUIRED_OVERALL_STATE = "EXACT_G4_PHYSICAL_QUOTIENT_AT_G3_WITNESS__TREE_LEVEL"
INCOMPLETE_STATUS = "G4_SM_PATI_SALAM_PHYSICAL_QUOTIENT_NOT_CERTIFIED__G4_NOT_CLOSED"
REQUIRED_N_CHECKS = 69            # the G4 certificate's check count; change only together with the module
WITNESS = {"r0": "1/5", "x0": "1", "kappa": "-1/20"}
EPS_WINDOW = {"lower_exclusive": "0", "upper_exclusive": "599/50"}
WITNESS_VACUUM_PREFIX = "q0 = (Phi, H, Sigma, S, Phi17) = (p, 0, r0 sigma_std, r0, x0)"
EXPECTED_RANKS = {"SO10": 33, "SO10_x_U1X": 34, "SO10_x_U1X_x_PQ": 35}
EXPECTED_MINOR_DETERMINANTS = {"SO10": 1, "SO10_x_U1X": 4, "SO10_x_U1X_x_PQ": -68}
EXPECTED_NULL_VECTORS = 12
GAUGE_QUOTIENT = 452
TRANSVERSE_QUOTIENT = 451
EXPECTED_EATEN = {"total": 34, "SO10_over_SM": 33, "U1X": 1}
AXION_NORM_SQUARED = "9248/7241"
AXION_FRACTIONS = {"Phi210": "0", "H10": "0", "Sigma126bar": "0", "S": "7225/7241", "Phi17": "16/7241"}
AXION_PERIOD = "2 pi/68"
V_A_SQUARED = "2/7241"
W_INERTIA_EPS = "451/1/0"
W_INERTIA_TUNED = "447/5/0"
HESSIAN_INERTIA_EPS = "451/35/0"
HESSIAN_INERTIA_TUNED = "447/39/0"
LAMBDA_EFF = "127/64"
VECTOR_GRAM_RANK = 34
AXION_ZERO_MODE = "the physical axion a"
DOUBLET_LABEL_PREFIX = "(1,2)_{1/2}"
SCOPE_LIMIT_MARKERS = ("PQ-violating", "QCD anomaly", "loop corrections", "physical hierarchy point")
ROUTED_G4_CAVEAT_ID = "zero_modes_and_ranks_at_witness"
# The certificate's own conclusion flags (each equals certificate_passes in
# g4_sm_pati_salam_physical_quotient_v20): a report that denies any of them fails closed.
CERTIFIED_FLAGS = (
    "certificate_passes",
    "gauge_ranks_33_34_35_exact",
    "gauge_quotient_452_and_transverse_quotient_451_exact",
    "PQ_global_not_gauged_not_eaten",
    "physical_axion_identified_exact",
    "restricted_hessian_psd_single_zero_mode_axion",
    "no_negative_modes",
    "zero_modes_35_equal_34_eaten_plus_axion",
    "tuned_limit_doublet_is_SM_doublet_lifted_at_quartic_order",
    "vector_boson_gram_by_SM_sector_exact",
    "wired_into_gate_ledger_as_G4_evidence",
)

# The G4 certificate's final acceptance statement (moved verbatim from g4_sm_pati_salam_physical_quotient_v20).
G4_REQUIRED_STATEMENT = (
    "At the G3 witness q0 of V_PS,eps (0 < eps < 599/50; r0 = 1/5, x0 = 1, kappa = -r0/4) the SO(10)xU(1)_X orbit "
    "has rank 34 and the SO(10)xU(1)_XxPQ orbit rank 35 (gauge quotient 452, massive/transverse quotient 451); the "
    "Hessian has no negative mode and exactly 35 zero modes, 34 eaten Goldstones (33 SO(10)/SM + 1 U(1)_X) and 1 "
    "physical axion; restricted to the 452-dimensional gauge quotient (canonical chart metric) it is PSD with the "
    "axion as its only zero mode and 451 strictly positive modes; as eps -> 0 the only extra zero modes are the 4 "
    "real modes of one SM doublet (1,2)_{1/2}, of mass^2 eps and lifted at quartic order by lambda_eff = 127/64 > 0."
)
# The roadmap's W3-G4 acceptance (moved verbatim).
W3_G4_ACCEPTANCE = (
    "exact gauge/global-symmetry ranks remain compiler-bound and the completed G3 Hessian has no unexplained zero "
    "or negative modes"
)
# The ledger's gates.G4.authoritative_closed_scope entry.
G4_LEDGER_CLOSED_SCOPE = (
    "G4 gauge quotient and physical Hessian at the G3 witness benchmark (g4_sm_pati_salam_physical_quotient_v20 via "
    "g4_sm_closure_binding_v20; exact over Q at r0 = 1/5, x0 = 1, kappa = -r0/4 for every 0 < eps < 599/50; tree "
    "level): orbit ranks 33/34/35 (integer minors 1, 4, -68; 12 null vectors spanning the SM algebra), gauge "
    "quotient 452 and massive/transverse quotient 451, PQ global and not eaten; Hessian on the gauge quotient "
    "451/1/0 with the physical axion (S phase 7225/7241, Phi17 phase 16/7241; period 2 pi/68 modulo the gauge "
    "group, v_a^2 = 2/7241 M_GUT^2) as its only zero mode; 35 zero modes = 34 eaten Goldstones + the axion, no "
    "negative mode; eps -> 0 adds only one SM doublet (1,2)_{1/2} of mass^2 eps, lifted at quartic order by "
    "lambda_eff = 127/64; vector-boson Gram rank 34; axion massless only for the renormalizable PQ-neutral "
    "benchmark potential; compiler binding float64"
)
# The G4 sentence of the ledger, roadmap and confirmation verdicts.
G4_CLOSED_SENTENCE = (
    "G4 is CLOSED at the G3 witness benchmark (r0 = 1/5, x0 = 1, kappa = -r0/4, every 0 < eps < 599/50), tree "
    "level (g4_sm_pati_salam_physical_quotient_v20 through g4_sm_closure_binding_v20): SO(10)xU(1)_X rank 34 "
    "(gauge quotient 452) and SO(10)xU(1)_XxPQ rank 35 (massive/transverse quotient 451); on the gauge quotient "
    "the Hessian is 451/1/0 with the physical axion as its only zero mode, the 35 zero modes of the full Hessian "
    "are 34 eaten Goldstones and the axion, and no mode is negative; as eps -> 0 the only extra zero modes are one "
    "SM doublet (1,2)_{1/2}, lifted at quartic order by lambda_eff = 127/64. The axion is massless only for the "
    "renormalizable PQ-neutral benchmark potential: the QCD anomaly and PQ-violating operators such as Phi17^4 "
    "conj(S)^17/M_Pl^17 give it a mass."
)
G4_SCOPE_LIMITS = (
    "tree level only: loop corrections and running are not included",
    "the benchmark point r0 = 1/5, x0 = 1 only; the physical hierarchy point is not certified",
    "the compiler = exact-operator identity of the Hessian and the tangent binding are float64",
    "the axion zero mode is exact only for the renormalizable PQ-neutral benchmark potential: the QCD anomaly and "
    "PQ-violating operators such as Phi17^4 conj(S)^17/M_Pl^17 give the axion a mass, and f_a = v_a/N_DW is not computed",
    "G6-G8 physics (sub-M_I coloured states, electroweak symmetry breaking, RG content, the Higgs quartic, Yukawas and "
    "proton decay) is not addressed by G4",
)
G4_CLOSURE_DECISION = (
    "User instruction (2026-09-25, 'continue ... complete theory close all needed'): close G4 once its exact "
    "certificate passes; gates that are not proven stay OPEN or BLOCKED. User decision D-E (2026-09-26) overrides "
    "the decision-D3 cascade: a CLOSED G4 meets D3's G4 condition but does not approve the internal-candidate tier, "
    "which is held until G7 is CLOSED (theory_confirmation_verdict_v20)."
)
# ("GAUGED_U1X_G6_G7_G8_CLOSURE_REQUIRED",) + g3_sm_target_track_v20.DOWNSTREAM_BLOCKERS[2:], written out so that
# this module never imports the track.
DOWNSTREAM_BLOCKERS_AFTER_G4 = (
    "GAUGED_U1X_G6_G7_G8_CLOSURE_REQUIRED",
    "G6_SUB_M_I_COLOURED_STATES_AND_POSITIVITY_WITHOUT_EWSB",
    "G7_RG_ANCHOR_CONTENT_AND_HIGGS_QUARTIC_MATCHING",
    "G8_YUKAWA_SECTOR_AND_PROTON_DECAY_MEDIATORS",
)

INTEGRITY_NAMES = (
    "g4_report_executes",
    "g4_premises_all_hold",
    "g4_report_does_not_overclaim",
    "g4_float_evidence_not_promoted",
    "g4_scope_limits_disclosed",
)
SCIENCE_NAMES = (
    "g4_witness_is_the_g3_witness",
    "g4_orbit_ranks_33_34_35_exact",
    "g4_gauge_and_transverse_quotients_452_451_exact",
    "g4_eaten_goldstones_34_pq_global_not_eaten",
    "g4_physical_axion_exact",
    "g4_gauge_quotient_hessian_451_1_0",
    "g4_zero_modes_35_are_34_eaten_plus_axion_no_negative",
    "g4_tuned_limit_is_one_sm_doublet_lifted_127_64",
    "g4_vector_gram_rank_34",
    "g4_required_statement_bound",
    "g4_open_scope_fully_covered",
)

# (section, prefix) pairs of the certificate's top-level check mirror: each section's own checks must all hold
# and be mirrored exactly as "<prefix>__<name>" in the top-level checks.
_SECTION_CHECK_PREFIXES = (
    ("gauge_quotient", "gauge"),
    ("chart_normalisation", "chart"),
    ("axion", "axion"),
    ("fresh_exact_hessians", "fresh"),
    ("restricted_hessian", "restricted"),
    ("light_doublet", "doublet"),
    ("vector_bosons", "vectors"),
)
# The fresh exact Hessian variants and their exact inertias (positive/zero/negative).
_FRESH_INERTIAS = {
    "raised_O06": HESSIAN_INERTIA_EPS,
    "tiny_eps": HESSIAN_INERTIA_EPS,
    "benchmark": HESSIAN_INERTIA_TUNED,
}
_PREMISE_KEYS = frozenset({"hessian", "equality", "candidate", "sigma_audit", "contract"})
_NEVER_TRUE_FLAGS = ("G4_closed", "internal_candidate_approved", "G6_closed", "whole_model_validated")
_EXPECTED_COVERAGE_ITEMS = 3


# ---------------------------------------------------------------------------
# Strict helpers (same semantics as g3_sm_target_track_v20).
# ---------------------------------------------------------------------------


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


def _true(value: Any, *keys: str) -> bool:
    return _dig(value, *keys) is True


def _false(value: Any, *keys: str) -> bool:
    return _dig(value, *keys) is False


def _all_true(value: Any) -> bool:
    return isinstance(value, dict) and bool(value) and all(item is True for item in value.values())


def _all_true_n(value: Any, count: int) -> bool:
    return _all_true(value) and len(value) == count


def _str_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _nonempty_str_list(value: Any) -> bool:
    return _str_list(value) and bool(value)


def _str_eq(value: Any, expected: str) -> bool:
    return isinstance(value, str) and value == expected


def _str_dict_eq(value: Any, expected: Mapping[str, str]) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == set(expected)
        and all(_str_eq(value[key], text) for key, text in expected.items())
    )


def _int_dict_eq(value: Any, expected: Mapping[str, int]) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == set(expected)
        and all(_int_eq(value[key], number) for key, number in expected.items())
    )


def _safe(predicate: Any) -> bool:
    try:
        return bool(predicate()) is True
    except Exception:  # noqa: BLE001 - any malformed input fails closed
        return False


# ---------------------------------------------------------------------------
# Loading.
# ---------------------------------------------------------------------------


def load_g4_report(path: Path | str | None = None) -> dict[str, Any]:
    """The committed G4 certificate as a dict ({} when missing, unreadable, not JSON or not a non-empty dict)."""
    target = ROOT / G4_REPORT_FILE if path is None else Path(path)
    try:
        value = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError):
        return {}
    return value if isinstance(value, dict) and value else {}


# ---------------------------------------------------------------------------
# Integrity criteria.
# ---------------------------------------------------------------------------


def _report_executes(rep: Mapping[str, Any]) -> bool:
    theorem = rep.get("theorem")
    return bool(
        bool(rep)
        and _str_eq(rep.get("model_contract_id"), MODEL_CONTRACT_ID)
        and _str_eq(rep.get("status"), REQUIRED_STATUS)
        and _str_eq(rep.get("overall_state"), REQUIRED_OVERALL_STATE)
        and _int_eq(rep.get("n_failed"), 0)
        and rep.get("failures") == []
        and _int_eq(rep.get("n_checks"), REQUIRED_N_CHECKS)
        and _all_true_n(rep.get("checks"), REQUIRED_N_CHECKS)
        and rep.get("theorem_claimed") is True
        and isinstance(theorem, str)
        and bool(theorem)
        and not theorem.startswith("NOT CLAIMED")
        and all(_true(rep, "flags", name) for name in CERTIFIED_FLAGS)
        and _section_checks_bound(rep)
    )


def _section_checks_bound(rep: Mapping[str, Any]) -> bool:
    """Every section's own checks hold and match the top-level mirror; the fresh exact inertias are bound."""
    checks = rep.get("checks")
    if not isinstance(checks, dict):
        return False
    for section, prefix in _SECTION_CHECK_PREFIXES:
        own = _dig(rep, section, "checks")
        if not _all_true(own):
            return False
        mirrored = {key for key in checks if key.startswith(prefix + "__")}
        if mirrored != {prefix + "__" + key for key in own}:
            return False
    for member, inertia in _FRESH_INERTIAS.items():
        variant = _dig(rep, "fresh_exact_hessians", "variants", member)
        if not (
            _str_eq(_dig(variant, "inertia_positive_zero_negative"), inertia)
            and _true(variant, "exact_PSD")
            and _true(variant, "kernel_equals_expected_span")
        ):
            return False
    return True


def _premises_all_hold(rep: Mapping[str, Any]) -> bool:
    premises = rep.get("premises")
    return bool(
        isinstance(premises, dict)
        and set(premises) == _PREMISE_KEYS
        and all(_all_true(premises[key]) for key in _PREMISE_KEYS)
    )


def _does_not_overclaim(rep: Mapping[str, Any]) -> bool:
    return bool(
        _false(rep, "flags", "report_closes_g4_by_itself")
        and _false(rep, "final_acceptance_test", "closes_g4_by_itself")
        and "G4_closed" not in rep
        and all(_dig(rep, "flags", key) is not True for key in _NEVER_TRUE_FLAGS)
        and _true(rep, "flags", "tree_level_only")
    )


def _float_evidence_not_promoted(rep: Mapping[str, Any]) -> bool:
    return bool(
        _true(rep, "flags", "compiler_binding_float64_only")
        and _nonempty_str_list(_dig(rep, "scope", "float64_evidence_only"))
        and _true(rep, "live_compiler_binding", "compiler_binding_passes")
        and _true(rep, "float64_corroboration", "consistent")
    )


def _scope_limits_disclosed(rep: Mapping[str, Any]) -> bool:
    not_covered = _dig(rep, "scope", "not_covered")
    return bool(
        _nonempty_str_list(not_covered)
        and all(any(marker in item for item in not_covered) for marker in SCOPE_LIMIT_MARKERS)
        and _true(rep, "flags", "axion_massless_only_for_renormalizable_PQ_neutral_potential")
    )


# ---------------------------------------------------------------------------
# Science criteria.
# ---------------------------------------------------------------------------


def _witness_is_the_g3_witness(w: Any, g3_witness: Mapping[str, Any] | None) -> bool:
    vacuum = _dig(w, "vacuum")
    own = bool(
        isinstance(w, dict)
        and all(_str_eq(w.get(key), value) for key, value in WITNESS.items())
        and _str_dict_eq(w.get("eps_window"), EPS_WINDOW)
        and isinstance(vacuum, str)
        and vacuum.startswith(WITNESS_VACUUM_PREFIX)
    )
    if not own or g3_witness is None:
        return own
    g3_vacuum = _dig(g3_witness, "vacuum")
    return bool(
        isinstance(g3_witness, Mapping)
        and _str_eq(g3_witness.get("id"), "sm_pati_salam_eps_member")
        and all(_str_eq(_dig(g3_witness, "benchmark", key), w[key]) for key in ("r0", "x0", "kappa"))
        and _str_eq(_dig(g3_witness, "eps_window", "lower_exclusive"), "0")
        and _str_eq(_dig(g3_witness, "eps_window", "upper_exclusive"), "599/50")
        and isinstance(g3_vacuum, str)
        and bool(g3_vacuum)
        and g3_vacuum in vacuum
    )


def _orbit_ranks_exact(gq: Any) -> bool:
    ranks = _dig(gq, "ranks")
    certificates = _dig(gq, "certificates")
    if not (_int_dict_eq(ranks, EXPECTED_RANKS) and isinstance(certificates, dict)):
        return False
    for name, rank in EXPECTED_RANKS.items():
        cert = certificates.get(name)
        if not (
            isinstance(cert, dict)
            and _int_eq(cert.get("rank"), rank)
            and _int_eq(_dig(cert, "minor", "determinant_integer_M"), EXPECTED_MINOR_DETERMINANTS[name])
            and _int_eq(cert.get("null_vector_count"), EXPECTED_NULL_VECTORS)
            and _int_eq(cert.get("null_vector_rank"), EXPECTED_NULL_VECTORS)
            and cert.get("null_vectors_without_X_or_PQ_coefficient") is True
        ):
            return False
    return bool(
        _true(gq, "stabilizer", "equals_standard_SM_algebra")
        and _int_eq(_dig(gq, "stabilizer", "dimension"), EXPECTED_NULL_VECTORS)
    )


def _quotients_exact(rep: Mapping[str, Any], gq: Any) -> bool:
    return bool(
        _int_eq(_dig(gq, "gauge_quotient_dimension_including_axion"), GAUGE_QUOTIENT)
        and _int_eq(_dig(gq, "massive_transverse_quotient_dimension"), TRANSVERSE_QUOTIENT)
        and _int_eq(_dig(rep, "restricted_hessian", "dimensions", "W"), GAUGE_QUOTIENT)
    )


def _eaten_and_pq(gq: Any) -> bool:
    return bool(
        _int_dict_eq(_dig(gq, "eaten_goldstones"), EXPECTED_EATEN)
        and _false(gq, "PQ", "gauged")
        and _false(gq, "PQ", "eaten")
        and _int_eq(_dig(gq, "PQ", "rank_increase_over_gauge_orbit"), 1)
    )


def _axion_exact(rep: Mapping[str, Any]) -> bool:
    axion = rep.get("axion")
    return bool(
        _str_eq(_dig(axion, "axion_norm_squared"), AXION_NORM_SQUARED)
        and _str_dict_eq(_dig(axion, "squared_norm_fractions"), AXION_FRACTIONS)
        and _str_eq(_dig(axion, "decay_constant", "axion_angle_period_modulo_gauge"), AXION_PERIOD)
        and _str_eq(_dig(axion, "decay_constant", "v_a_squared"), V_A_SQUARED)
        and _all_true(_dig(axion, "checks"))
    )


def _restricted_hessian(rep: Mapping[str, Any]) -> bool:
    restricted = rep.get("restricted_hessian")
    return bool(
        _true(restricted, "eps_positive", "certified")
        and _str_eq(_dig(restricted, "eps_positive", "inertia_on_W_positive_zero_negative"), W_INERTIA_EPS)
        and _str_eq(_dig(restricted, "eps_positive", "zero_mode"), AXION_ZERO_MODE)
        and _str_eq(_dig(restricted, "tuned_eps_0", "inertia_on_W_positive_zero_negative"), W_INERTIA_TUNED)
        and _all_true(_dig(restricted, "checks"))
    )


def _zero_modes(rep: Mapping[str, Any]) -> bool:
    classification = rep.get("zero_mode_classification")
    eps = _dig(classification, "eps_positive")
    eaten = _dig(eps, "eaten_goldstones")
    return bool(
        _true(classification, "certified")
        and _str_eq(_dig(eps, "hessian_inertia_positive_zero_negative"), HESSIAN_INERTIA_EPS)
        and _int_eq(_dig(eps, "negative_modes"), 0)
        and _int_eq(_dig(eps, "zero_modes"), 35)
        and _int_eq(_dig(eps, "physical_axion"), 1)
        and isinstance(eaten, dict)
        and all(_int_eq(eaten.get(key), value) for key, value in EXPECTED_EATEN.items())
        and _str_eq(_dig(classification, "tuned_eps_0", "hessian_inertia_positive_zero_negative"), HESSIAN_INERTIA_TUNED)
        and _int_eq(_dig(classification, "unexplained_zero_or_negative_modes"), 0)
    )


def _tuned_doublet(rep: Mapping[str, Any]) -> bool:
    light = rep.get("light_doublet")
    label = _dig(light, "SM_label")
    mass = _dig(light, "mass_squared", "value")
    return bool(
        isinstance(label, str)
        and label.startswith(DOUBLET_LABEL_PREFIX)
        and _str_eq(_dig(light, "exact_values", "SU2L_casimir"), "3/4")
        and _str_eq(_dig(light, "exact_values", "Y_squared"), "1/4")
        and _true(light, "exact_values", "colour_generators_vanish")
        and _str_eq(_dig(light, "tuned_limit", "quartic_lift_lambda_eff"), LAMBDA_EFF)
        and _int_eq(_dig(light, "tuned_limit", "zero_modes"), 4)
        and isinstance(mass, str)
        and mass.startswith("eps")
        and _all_true(_dig(light, "checks"))
    )


def _vector_gram(rep: Mapping[str, Any]) -> bool:
    return bool(
        _int_eq(_dig(rep, "vector_bosons", "gram_rank"), VECTOR_GRAM_RANK)
        and _all_true(_dig(rep, "vector_bosons", "checks"))
    )


def _required_statement(rep: Mapping[str, Any]) -> bool:
    final = rep.get("final_acceptance_test")
    return bool(
        _str_eq(_dig(final, "gate"), "G4")
        and _str_eq(_dig(final, "required_statement"), G4_REQUIRED_STATEMENT)
        and _true(final, "currently_passes")
        and _str_eq(_dig(final, "status"), REQUIRED_STATUS)
    )


def _open_scope_covered(rep: Mapping[str, Any], g4_open_scope: Sequence[str] | None) -> bool:
    coverage = rep.get("g4_open_scope_coverage")
    if not (
        isinstance(coverage, list)
        and len(coverage) == _EXPECTED_COVERAGE_ITEMS
        and all(
            isinstance(row, dict) and isinstance(row.get("item"), str) and row.get("content_certified") is True
            for row in coverage
        )
    ):
        return False
    if g4_open_scope is not None:
        if isinstance(g4_open_scope, (str, bytes)) or [row["item"] for row in coverage] != list(g4_open_scope):
            return False
    return bool(
        _str_eq(_dig(rep, "roadmap_W3_G4_acceptance", "text"), W3_G4_ACCEPTANCE)
        and _true(rep, "roadmap_W3_G4_acceptance", "ranks_compiler_bound")
        and _true(rep, "roadmap_W3_G4_acceptance", "no_unexplained_zero_or_negative_modes")
    )


# ---------------------------------------------------------------------------
# Public predicate.
# ---------------------------------------------------------------------------


def evaluate_g4_binding(
    report: Any,
    *,
    g3_witness: Mapping[str, Any] | None = None,
    g4_open_scope: Sequence[str] | None = None,
) -> dict[str, Any]:
    """The 16 fail-closed G4 closure criteria for a G4 certificate report (a dict; anything else fails)."""
    rep: dict[str, Any] = report if isinstance(report, dict) else {}
    w = rep.get("witness")
    gq = rep.get("gauge_quotient")
    integrity = {
        "g4_report_executes": _safe(lambda: _report_executes(rep)),
        "g4_premises_all_hold": _safe(lambda: _premises_all_hold(rep)),
        "g4_report_does_not_overclaim": _safe(lambda: _does_not_overclaim(rep)),
        "g4_float_evidence_not_promoted": _safe(lambda: _float_evidence_not_promoted(rep)),
        "g4_scope_limits_disclosed": _safe(lambda: _scope_limits_disclosed(rep)),
    }
    science = {
        "g4_witness_is_the_g3_witness": _safe(lambda: _witness_is_the_g3_witness(w, g3_witness)),
        "g4_orbit_ranks_33_34_35_exact": _safe(lambda: _orbit_ranks_exact(gq)),
        "g4_gauge_and_transverse_quotients_452_451_exact": _safe(lambda: _quotients_exact(rep, gq)),
        "g4_eaten_goldstones_34_pq_global_not_eaten": _safe(lambda: _eaten_and_pq(gq)),
        "g4_physical_axion_exact": _safe(lambda: _axion_exact(rep)),
        "g4_gauge_quotient_hessian_451_1_0": _safe(lambda: _restricted_hessian(rep)),
        "g4_zero_modes_35_are_34_eaten_plus_axion_no_negative": _safe(lambda: _zero_modes(rep)),
        "g4_tuned_limit_is_one_sm_doublet_lifted_127_64": _safe(lambda: _tuned_doublet(rep)),
        "g4_vector_gram_rank_34": _safe(lambda: _vector_gram(rep)),
        "g4_required_statement_bound": _safe(lambda: _required_statement(rep)),
        "g4_open_scope_fully_covered": _safe(lambda: _open_scope_covered(rep, g4_open_scope)),
    }
    blockers = [name for name in INTEGRITY_NAMES if integrity[name] is not True]
    blockers += [name for name in SCIENCE_NAMES if science[name] is not True]
    status = rep.get("status")
    n_failed = rep.get("n_failed")
    n_checks = rep.get("n_checks")
    return {
        "source": G4_SOURCE,
        "report": G4_REPORT_FILE,
        "required_status": REQUIRED_STATUS,
        "status": status if isinstance(status, str) else None,
        "n_failed": n_failed if _is_int(n_failed) else None,
        "n_checks": n_checks if _is_int(n_checks) else None,
        "integrity": integrity,
        "science": science,
        "blockers": blockers,
        "certified": bool(all(integrity.values()) and all(science.values())),
        "witness_bound_to_g3_track": g3_witness is not None,
        "required_statement": G4_REQUIRED_STATEMENT,
        "closure_scope": G4_LEDGER_CLOSED_SCOPE,
        "scope_limits": list(G4_SCOPE_LIMITS),
        "decision": G4_CLOSURE_DECISION,
    }


def ledger_g4_closed(ledger_report: Any) -> bool:
    """True only for a ledger whose G4 row is CLOSED on certified evidence with the required status."""

    def _closed() -> bool:
        row = _dig(ledger_report, "gates", "G4")
        evidence = _dig(row, "closure_evidence")
        return bool(
            isinstance(row, Mapping)
            and row.get("status") == "CLOSED"
            and isinstance(evidence, Mapping)
            and evidence.get("certified") is True
            and _str_eq(evidence.get("required_status"), REQUIRED_STATUS)
            and _str_eq(evidence.get("status"), REQUIRED_STATUS)
        )

    return _safe(_closed)


def main(argv: list[str] | None = None) -> int:
    """Print the binding of the committed G4 certificate (sorted JSON); exit 0 iff it is certified."""
    del argv  # no options: the predicate always reads the committed report
    result = evaluate_g4_binding(load_g4_report())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["certified"] is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
