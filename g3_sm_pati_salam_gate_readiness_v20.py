#!/usr/bin/env python3
"""Dry-run readiness audit: the SM Pati-Salam target against the final G3 gate (v20).

This module changes NO gate status and writes nothing except its own report.
G3 is decided only by final_g3_acceptance_gate_v20 through its sm_pati_salam
track (g3_sm_target_track_v20); this module is kept as an independent
pre-integration cross-check of that track.  It maps the final gate's chiral-H
criteria (the diagnostic track tracks.chiral_H_SU5_Delta, or the top-level
criteria of a pre-integration gate report) onto the Pati-Salam vacuum of
g3_sm_pati_salam_candidate_v20,

    q0 = (Phi, H, Sigma, S, Phi17) = (p, 0, r0 sigma_std, r0, x0),
    p = e6789,  sigma_std = z1^z2^z3^z4^z5,  r0 = 1/5, x0 = 1, kappa = -r0/4,

and asks which of those criteria that target satisfies, and on what kind of
evidence.

For EVERY science criterion and release criterion of the chiral-H track of the
committed final gate report it records the Pati-Salam analogue (statement,
evidence keys, exact or float64), its value, and one classification:

  SATISFIED_EXACT                 exact (non-float) evidence holds (the grade
                                  and conditional_on_decisions name any
                                  adopted decision, e.g. D6, it presumes);
  SATISFIED_FLOAT_ONLY            exact evidence is unavailable (a required
                                  artifact is missing or not executing) and
                                  only float64 evidence holds;
  FAILED                          exact evidence from a loaded, executing
                                  artifact refutes the claim, or nothing holds;
  ROUTE_SPECIFIC_NOT_APPLICABLE   a proof route used only for the chiral-H
                                  SU(5)+Delta candidate.

The analogue of each criterion is its literal one: the chiral-H 448/38 is
(486 - orbit rank)/(orbit rank), so the PS analogue is 451/35 with kernel = the
35-dimensional orbit; the tuned benchmark's certified 447/39 fails both Hessian
criteria (the planner's S11 would have replaced them by a gate-contract
change; the adopted decision D2 takes the eps > 0 member instead).
would_close_G3_mathematically_if_SM_track_added is True only if every
non-route-specific criterion (science and release) is SATISFIED_EXACT and every
readiness integrity check passes; the wiring conjunct required_statement ==
theorem (S9) is not evaluated here (the track evaluates it), and
SATISFIED_EXACT for the equality-set and global-gap criteria presumes decision
D6 (adopted).  The decisive theorem is compared with the equality module's
theorem textually and semantically.  The candidate's physics caveats are
tabulated with the ADOPTED routing (decision D5): the ledger/roadmap wave-3 G3
deliverable carries the caveat-routing sentence of g3_sm_target_track_v20.
The planner's option analysis and the adopted decisions D1-D6 are recorded.

Every criterion is evaluated a second time (section eps_member) on the SM track
witness family O06 = 2|kappa| r0 + eps, eps > 0, i.e. V_eps = V + eps N_H with
the other 26 couplings unchanged.  The exact Hessian report's eps_family
section supplies L1 ({V_eps = V0} = {V = V0} = G.q0 for every eps >= 0, given
the equality-set theorem) and L2 (for every eps > 0 the Hessian at q0 is PSD
with kernel exactly the 35-dimensional orbit: 451/35, strictly positive on the
symmetry quotient).  On that member both literal Hessian criteria hold exactly,
the equality-set and global-gap criteria hold via L1 plus the equality report
(still presuming D6), and every other criterion as for the benchmark (same
vacuum, same G, same contract; O06 = 1/50 + eps stays perturbative for
eps < 12 - 1/50).  would_close_G3_mathematically_on_eps_member_if_SM_track_added
records the result inside that perturbative window (D2 adopted: an eps > 0
member is the G3 witness; D6 adopted for the equality-set and global-gap
criteria; the wiring conjunct S9 not evaluated here).  It must agree with
g3_sm_target_track_v20's closed verdict.  The
doublet has mass^2 eps M_GUT^2: light for eps << r0^2, but electroweak
symmetry is not broken; the tuned eps = 0 limit is not a strict minimum.

Inputs (read only, fail closed; nothing heavy is imported; the only repository
module imported is the pure g3_sm_target_track_v20, for its shared texts):

  FINAL_G3_ACCEPTANCE_GATE_V20.json        the gate's chiral-H criteria and theorem
  G3_SM_PATI_SALAM_CANDIDATE_V20.json      SOS global minimum, SM stabilizer
  G3_SM_PATI_SALAM_EQUALITY_SET_V20.json   {V = V0} = G.q0 exactly
  G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json  exact 486 x 486 inertia 447/39/0;
                                           eps family (L1, L2) 451/35/0
  G3_SIGMA_HYPERCHARGE_AUDIT_V20.json      Y = 0 singlet with p is the SM
  G1_G8_GATE_LEDGER_V20.json               G1/G2 status, contract, G5 vector

A missing, unparseable or non-executing artifact fails every criterion and
integrity check that depends on it, and the readiness booleans go False.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import g3_sm_target_track_v20 as sm_track

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G3_SM_PATI_SALAM_GATE_READINESS_V20.json"
OUT_MD = ROOT / "G3_SM_PATI_SALAM_GATE_READINESS_V20.md"

STATUS = "G3_SM_TARGET_READINESS_DRY_RUN__NO_GATE_STATUS_CHANGED"
MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"

ARTIFACT_FILES: dict[str, str] = {
    "final_gate": "FINAL_G3_ACCEPTANCE_GATE_V20.json",
    "candidate": "G3_SM_PATI_SALAM_CANDIDATE_V20.json",
    "equality_set": "G3_SM_PATI_SALAM_EQUALITY_SET_V20.json",
    "exact_hessian": "G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json",
    "sigma_hypercharge": "G3_SIGMA_HYPERCHARGE_AUDIT_V20.json",
    "ledger": "G1_G8_GATE_LEDGER_V20.json",
}

FINAL_GATE_STATUS = "FINAL_G3_ACCEPTANCE_TEST_EXECUTED"
CANDIDATE_STATUS = (
    "SM_PATI_SALAM_G3_CANDIDATE__EXACT_GLOBAL_MINIMUM_OF_BENCHMARK_POTENTIAL__SM_UNBROKEN__G3_OPEN"
)
CANDIDATE_OVERALL_STATE = "CANDIDATE_CERTIFIED_G3_OPEN"
CANDIDATE_N_CHECKS = 31
EQUALITY_STATUS = "SM_PATI_SALAM_EQUALITY_SET__UNIQUE_MODULO_SYMMETRY_EXACT__G3_OPEN"
EQUALITY_N_CHECKS = 45
HESSIAN_STATUS = "SM_PATI_SALAM_EXACT_FULL_HESSIAN_RANK_447_NULLITY_39_CERTIFIED__G3_OPEN"
HESSIAN_OVERALL_STATE = "EXACT_LOCAL_HESSIAN_KERNEL_ORBIT_PLUS_TUNED_DOUBLET_CERTIFIED"
HESSIAN_N_CHECKS = 52
EPS_N_CHECKS = 30  # checks of the exact Hessian report's eps_family section (L1, L2, doublet, one float64 diagnostic)
EPS_FLAGS = (
    "eps_family_theorem_claimed",
    "eps_family_equality_set_unchanged",
    "eps_family_kernel_equals_symmetry_orbit",
    "eps_family_strictly_positive_on_symmetry_quotient_for_all_eps_positive",
    "doublet_mass_squared_equals_eps",
)
EPS_MEMBER = "SM track witness family: O06 = 2|kappa| r0 + eps, eps > 0"
O06_ID = "lambda::O06_B01_Hdag_H_norm"
PERTURBATIVE_BOUND = Fraction(12)  # < 4 pi (pi > 3): exact rational comparisons only
EPS_KERNEL_TEXT = "span(T35), the SO(10) x U(1)_X x U(1)_PQ orbit tangent space"
S9_CONJUNCT = "required_statement == theorem (wiring; S9)"
SIGMA_STATUS = "G3_SIGMA_DIRECTION_IS_Y_MINUS_1_TRIPLET_COMPONENT__NAMED_VACUA_ARE_NOT_SM__G3_OPEN"
SIGMA_N_CHECKS = 28
SIGMA_STD_FORMULA = "z1^z2^z3^z4^z5"

# The final gate's decisive theorem (final_g3_acceptance_gate_v20.FINAL_THEOREM),
# pinned so that a drifted gate report fails closed.
FINAL_THEOREM = (
    "For every 486-real field q, V_beta(q)-V_beta(q0)>=0; equality holds "
    "exactly on the SO(10)xU(1)_XxPQ orbit of q0."
)
# Its SM-track counterpart: the same sentence with V_beta -> V_PS (the
# 27-parameter Pati-Salam benchmark) and q0 -> (p, 0, r0 sigma_std, r0, x0).
SM_FINAL_THEOREM = (
    "For every 486-real field q, V_PS(q)-V_PS(q0)>=0; equality holds "
    "exactly on the SO(10)xU(1)_XxPQ orbit of q0."
)
# The same sentence on the eps member V_PS,eps = V_PS + eps N_H (O06 = 2|kappa| r0 + eps).
SM_EPS_FINAL_THEOREM = FINAL_THEOREM.replace("V_beta", "V_PS,eps")

SATISFIED_EXACT = "SATISFIED_EXACT"
SATISFIED_FLOAT_ONLY = "SATISFIED_FLOAT_ONLY"
FAILED = "FAILED"
ROUTE_SPECIFIC = "ROUTE_SPECIFIC_NOT_APPLICABLE"
CLASSIFICATIONS = (SATISFIED_EXACT, SATISFIED_FLOAT_ONLY, FAILED, ROUTE_SPECIFIC)

FLOAT_TOLERANCE = 1e-12
TOTAL_DIM = 486

# The integrity check that says an artifact was loaded and executes: a false exact evidence item from an artifact
# whose check fails is "unavailable" (fail closed); a false item from an executing artifact refutes the claim.
ARTIFACT_EXECUTES: dict[str, str] = {
    "final_gate": "final_gate_report_executes",
    "candidate": "sm_candidate_report_executes",
    "equality_set": "sm_equality_set_report_executes",
    "exact_hessian": "sm_exact_hessian_report_executes",
    "sigma_hypercharge": "sigma_hypercharge_audit_executes",
    "ledger": "ledger_executes",
}

# The caveat allocation below is the adopted routing (decision D5), which is the repository's current definition:
# the ledger/roadmap wave-3 G3 deliverable carries g3_sm_target_track_v20's caveat-routing sentence.
CAVEAT_ROUTING_STATUS = "ADOPTED_UNDER_D5__CURRENT_REPO_DEFINITION"
WAVE3_CLAUSE = sm_track.CAVEAT_ROUTING_SENTENCE

# Unverified proof inputs of the equality-set theorem, pinned verbatim: a new or
# reworded cited theorem or elementary step fails the readiness check.
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

# The candidate's model-level flags: they must be present as bools and are
# forwarded to the caveat table.  This dry run does not require them to be True:
# decision D5 (adopted) routes the model-level caveats downstream (G4/G6/G7/G8,
# or outside G1-G8), and G3 keeps only disclosures.
MODEL_LEVEL_FLAGS = (
    "doublet_triplet_splitting_natural",
    "coloured_scalars_only_at_M_GUT",
    "rg_anchor_field_content_reproduced",
    "higgs_mass_compatible",
    "electroweak_symmetry_breaking_realized",
    "realistic_yukawa_sector",
    "physical_benchmark_uses_canonical_phi17_scale",
)

# O27 self-projector parameters in the order (54, 1050bar, 2772bar, 4125).
O27_CHANNELS = (
    ("lambda::O27_B01_126bar_self_projectors", "54"),
    ("lambda::O27_B02_126bar_self_projectors", "1050bar"),
    ("lambda::O27_B03_126bar_self_projectors", "2772bar"),
    ("lambda::O27_B04_126bar_self_projectors", "4125"),
)
SELF_WEIGHTS = {"54": Fraction(2), "1050bar": Fraction(2), "2772bar": Fraction(1), "4125": Fraction(17, 16)}


# ----------------------------------------------------------------------------
# Fail-closed loading and small helpers.
# ----------------------------------------------------------------------------


def _read_bytes(path: Path) -> tuple[bytes | None, str | None]:
    try:
        return path.read_bytes(), None
    except FileNotFoundError:
        return None, "missing"
    except OSError as exc:  # pragma: no cover - platform dependent
        return None, f"unreadable ({type(exc).__name__})"


def load_artifact(path: Path) -> tuple[dict[str, Any], str | None, str | None]:
    """Return (report, error, sha256 of LF-normalised bytes); report is {} on any failure."""
    payload, error = _read_bytes(path)
    if payload is None:
        return {}, error, None
    digest = hashlib.sha256(payload.replace(b"\r\n", b"\n")).hexdigest()
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}, "unparseable JSON", digest
    if not isinstance(value, dict):
        return {}, "not a JSON object", digest
    if not value:
        return {}, "empty JSON object", digest
    return value, None, digest


def load_reports(
    paths: Mapping[str, Path] | None = None,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    """Load the six input artifacts; returns (reports, per-artifact load metadata)."""
    paths = dict(paths or {})
    reports: dict[str, dict[str, Any]] = {}
    meta: dict[str, dict[str, Any]] = {}
    for key, name in ARTIFACT_FILES.items():
        path = Path(paths.get(key, ROOT / name))
        report, error, digest = load_artifact(path)
        reports[key] = report
        meta[key] = {
            "file": name,
            "path_is_default": path == ROOT / name,
            "loaded": error is None,
            "error": error,
            "sha256_lf": digest,
        }
    return reports, meta


def _dig(value: Any, *keys: str, default: Any = None) -> Any:
    current = value
    for key in keys:
        if not isinstance(current, Mapping) or key not in current:
            return default
        current = current[key]
    return current


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _frac(value: Any) -> Fraction | None:
    if isinstance(value, bool):
        return None
    if _is_int(value):
        return Fraction(value)
    if isinstance(value, str):
        try:
            return Fraction(value.strip())
        except (ValueError, ZeroDivisionError):
            return None
    return None


def _strict_eq(actual: Any, expected: Any) -> bool:
    if isinstance(expected, bool):
        return actual is expected
    if _is_int(expected):
        return _is_int(actual) and actual == expected
    return type(actual) is type(expected) and actual == expected


def _safe(predicate: Callable[[Any], Any], value: Any) -> bool:
    try:
        return bool(predicate(value))
    except Exception:  # noqa: BLE001 - any malformed input fails closed
        return False


def _brief(value: Any) -> Any:
    if isinstance(value, str):
        return value if len(value) <= 160 else value[:157] + "..."
    if isinstance(value, list):
        if len(value) <= 8 and all(not isinstance(item, (dict, list)) for item in value):
            return [_brief(item) for item in value]
        return f"<list of {len(value)} items>"
    if isinstance(value, Mapping):
        if len(value) <= 8 and all(not isinstance(item, (dict, list)) for item in value.values()):
            return {str(k): _brief(item) for k, item in value.items()}
        return f"<object with {len(value)} keys>"
    return value


def _path_text(path: Sequence[str]) -> str:
    return ".".join(path)


def _all_true(value: Any, count: int | None = None) -> bool:
    return (
        isinstance(value, Mapping)
        and bool(value)
        and (count is None or len(value) == count)
        and all(item is True for item in value.values())
    )


def _float_below(limit: float) -> Callable[[Any], bool]:
    return lambda value: isinstance(value, (int, float)) and not isinstance(value, bool) and abs(value) < limit


def _final_gate_criteria_view(fg: Any) -> Mapping[str, Any]:
    """The final gate's chiral-H criteria: tracks.chiral_H_SU5_Delta when present, else the report itself.

    After integration the final gate's top-level criteria are the SM Pati-Salam track's; the chiral-H criteria
    this dry run maps live in its diagnostic track.  A pre-integration report has them at top level.
    """
    if not isinstance(fg, Mapping):
        return {}
    track = _dig(fg, "tracks", "chiral_H_SU5_Delta")
    return track if isinstance(track, Mapping) else fg


class _Evidence:
    """Evidence items of one criterion, split into exact and float64 lists."""

    def __init__(self, reports: Mapping[str, Mapping[str, Any]], integrity: Mapping[str, bool]) -> None:
        self.reports = reports
        self.integrity = integrity
        self.exact: list[dict[str, Any]] = []
        self.float64: list[dict[str, Any]] = []
        self.preconditions: list[str] = []
        # Parallel to self.exact (not serialised): (kind, artifact key) with kind in precondition/artifact/computed.
        self.exact_sources: list[tuple[str, str | None]] = []

    def _store(self, item: dict[str, Any], grade: str, source: tuple[str, str | None]) -> bool:
        if grade == "exact":
            self.exact.append(item)
            self.exact_sources.append(source)
        else:
            self.float64.append(item)
        return item["ok"]

    def refuting_exact_items(self) -> list[dict[str, Any]]:
        """False exact items that refute the claim, as opposed to inputs that are missing or not executing.

        A failed precondition, or a false item read from an artifact that does not load or execute, only makes the
        exact evidence unavailable.  A false item read from a loaded, executing artifact refutes the claim, and so
        does a false value computed here unless one of the criterion's preconditions failed.
        """
        failed_preconditions = any(self.integrity.get(name) is not True for name in self.preconditions)
        refuting = []
        for item, (kind, artifact) in zip(self.exact, self.exact_sources, strict=True):
            if item["ok"] or kind == "precondition":
                continue
            if kind == "artifact":
                executes = ARTIFACT_EXECUTES.get(artifact or "")
                if not self.reports.get(artifact or "") or executes is None or self.integrity.get(executes) is not True:
                    continue
            elif failed_preconditions:
                continue
            refuting.append(item)
        return refuting

    def require(self, *names: str) -> None:
        for name in names:
            self.preconditions.append(name)
            ok = self.integrity.get(name) is True
            self._store(
                {
                    "artifact": "readiness integrity check",
                    "key": name,
                    "expected": "True",
                    "actual": self.integrity.get(name),
                    "ok": ok,
                },
                "exact",
                ("precondition", None),
            )

    def check(
        self,
        artifact: str,
        path: Sequence[str],
        expected: str,
        predicate: Callable[[Any], Any],
        *,
        grade: str = "exact",
    ) -> bool:
        actual = _dig(self.reports.get(artifact) or {}, *path)
        return self._store(
            {
                "artifact": ARTIFACT_FILES[artifact],
                "key": _path_text(path),
                "expected": expected,
                "actual": _brief(actual),
                "ok": _safe(predicate, actual),
            },
            grade,
            ("artifact", artifact),
        )

    def eq(self, artifact: str, path: Sequence[str], expected: Any, *, grade: str = "exact") -> bool:
        return self.check(artifact, path, f"== {json.dumps(expected)}", lambda a: _strict_eq(a, expected), grade=grade)

    def computed(self, name: str, ok: bool, actual: Any, expected: str, *, grade: str = "exact") -> bool:
        return self._store(
            {
                "artifact": "computed here from the artifacts' recorded exact values"
                if grade == "exact"
                else "computed here from the artifacts' recorded float64 values",
                "key": name,
                "expected": expected,
                "actual": _brief(actual),
                "ok": bool(ok),
            },
            grade,
            ("computed", None),
        )


# ----------------------------------------------------------------------------
# Exact values re-derived from the artifacts' recorded rationals.
# ----------------------------------------------------------------------------


def _derived(reports: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    cand = reports.get("candidate") or {}
    hess = reports.get("exact_hessian") or {}
    bench = _dig(cand, "candidate", "benchmarks", "1/5", default={})
    r0 = _frac(_dig(bench, "r0"))
    kappa = _frac(_dig(bench, "kappa"))
    o06 = _frac(_dig(bench, "O06"))
    x0 = _frac(_dig(cand, "candidate", "defaults", "x0"))
    out: dict[str, Any] = {"r0": r0, "kappa": kappa, "x0": x0, "O06": o06}

    ok_params = None not in (r0, kappa, x0) and r0 > 0 and x0 > 0
    out["benchmark_parameters_parsed"] = ok_params
    out["kappa_squared_below_8_r0_squared"] = bool(ok_params and kappa * kappa < 8 * r0 * r0)
    out["O06_equals_2_abs_kappa_r0"] = bool(ok_params and o06 is not None and o06 == 2 * abs(kappa) * r0)
    out["lambda_eff"] = (2 - kappa * kappa / (4 * r0 * r0)) if ok_params else None
    out["V0"] = (-1 - r0**4 / 8 - r0**4 - x0**4 / 32) if ok_params else None

    coefficients = _dig(cand, "candidate", "exact_nonzero_coefficients", default={})
    parsed = {name: _frac(value) for name, value in coefficients.items()} if isinstance(coefficients, Mapping) else {}
    out["coefficients_all_rational"] = bool(parsed) and all(value is not None for value in parsed.values())
    out["coefficients_nonzero_count"] = (
        sum(1 for value in parsed.values() if value) if out["coefficients_all_rational"] else None
    )
    out["coefficients_max_abs"] = max((abs(v) for v in parsed.values()), default=None) if out["coefficients_all_rational"] else None
    out["coefficients"] = parsed if out["coefficients_all_rational"] else {}

    alpha = _dig(cand, "exact_certificate", "exact_quartic_bound", "coefficients_alpha", default={})
    beta = _dig(cand, "exact_certificate", "exact_quartic_bound", "chart_norm_weights_beta", default={})
    constant = None
    if isinstance(alpha, Mapping) and isinstance(beta, Mapping) and alpha and set(alpha) == set(beta):
        terms = [(_frac(beta[k]), _frac(alpha[k])) for k in alpha]
        if all(b is not None and a is not None and a > 0 for b, a in terms):
            constant = 1 / sum(b * b / a for b, a in terms)
    out["quartic_bound_constant"] = constant

    raised = _frac(_dig(hess, "benchmark", "O06_raised"))
    raise_by = _frac(_dig(hess, "benchmark", "O06_raise"))
    out["O06_raised"] = raised
    out["O06_raise_equals_r0_squared_over_100"] = bool(ok_params and raise_by is not None and raise_by == r0 * r0 / 100)
    out["O06_raised_inside_27_parameter_family"] = bool(
        ok_params and raised is not None and raised == 2 * abs(kappa) * r0
    )

    # The eps member O06 = 2|kappa| r0 + eps: exact offsets recorded by the Hessian report's eps family.
    base_o06 = 2 * abs(kappa) * r0 if ok_params else None
    others = [abs(v) for name, v in out["coefficients"].items() if name != O06_ID]
    out["eps_family_O06_base"] = base_o06
    out["eps_raised"] = raised - base_o06 if raised is not None and base_o06 is not None else None
    out["eps_tiny"] = _frac(_dig(hess, "eps_family", "consistency_certificates", "tiny_eps", "eps"))
    out["O06_tiny"] = _frac(_dig(hess, "eps_family", "consistency_certificates", "tiny_eps", "O06"))
    out["other_26_couplings_max_abs"] = max(others) if others and len(others) == len(out["coefficients"]) - 1 else None
    # O06_eps = base + eps < 12 (< 4 pi) iff eps < 12 - base; the other 26 couplings do not move.
    out["eps_perturbative_upper"] = PERTURBATIVE_BOUND - base_o06 if base_o06 is not None else None
    return out


# ----------------------------------------------------------------------------
# Readiness integrity checks (all feed the readiness booleans).
# ----------------------------------------------------------------------------


def _executes(
    report: Any,
    *,
    status: str,
    n_checks: int | None = None,
    overall_state: str | None = None,
    theorem_claimed: bool = False,
) -> bool:
    if not isinstance(report, Mapping) or not report:
        return False
    n_failed = report.get("n_failed")
    if not (_is_int(n_failed) and n_failed == 0):
        return False
    if report.get("failures") != []:
        return False
    if report.get("status") != status or report.get("model_contract_id") != MODEL_CONTRACT_ID:
        return False
    if overall_state is not None and report.get("overall_state") != overall_state:
        return False
    if n_checks is not None:
        if not (_is_int(report.get("n_checks")) and report["n_checks"] == n_checks):
            return False
        if not _all_true(report.get("checks"), n_checks):
            return False
    if theorem_claimed and report.get("theorem_claimed") is not True:
        return False
    return True


def _renamed_self_claim_flag(report: Any) -> bool:
    """flags.report_closes_g3_by_itself is False and the retired candidate_wired_into_g3_gate flag is absent."""
    flags = _dig(report, "flags")
    return bool(
        isinstance(flags, Mapping)
        and flags.get("report_closes_g3_by_itself") is False
        and "candidate_wired_into_g3_gate" not in flags
    )


def _integrity_checks(reports: Mapping[str, Mapping[str, Any]], derived: Mapping[str, Any]) -> dict[str, bool]:
    fg = reports.get("final_gate") or {}
    cand = reports.get("candidate") or {}
    eq = reports.get("equality_set") or {}
    hess = reports.get("exact_hessian") or {}
    sigma = reports.get("sigma_hypercharge") or {}
    ledger = reports.get("ledger") or {}

    # The chiral-H criteria and theorem (the diagnostic track after integration); status, n_failed, failures and
    # the contract id are read from the top level of the gate report.
    view = _final_gate_criteria_view(fg)
    science = view.get("science_criteria")
    release = view.get("release_criteria")
    checks: dict[str, bool] = {}

    checks["final_gate_report_executes"] = bool(
        _is_int(fg.get("n_failed"))
        and fg.get("n_failed") == 0
        and fg.get("failures") == []
        and fg.get("status") == FINAL_GATE_STATUS
        and fg.get("model_contract_id") == MODEL_CONTRACT_ID
        and view.get("decisive_theorem") == FINAL_THEOREM
        and isinstance(science, Mapping)
        and bool(science)
        and isinstance(release, Mapping)
        and bool(release)
    )
    checks["final_gate_criteria_match_readiness_map"] = bool(
        isinstance(science, Mapping)
        and isinstance(release, Mapping)
        and set(science) == set(SCIENCE_SPECS)
        and set(release) == set(RELEASE_SPECS)
    )
    checks["ledger_executes"] = bool(
        _is_int(ledger.get("n_failed"))
        and ledger.get("n_failed") == 0
        and ledger.get("failures") == []
        and ledger.get("model_contract_id") == MODEL_CONTRACT_ID
        and isinstance(ledger.get("gates"), Mapping)
    )
    checks["sigma_hypercharge_audit_executes"] = bool(
        _executes(sigma, status=SIGMA_STATUS, n_checks=SIGMA_N_CHECKS)
        and isinstance(sigma.get("flags"), Mapping)
        and _dig(sigma, "flags", "sm_singlet_direction_found") is True
        and _dig(sigma, "checks", "p_sm_singlet_Y0_is_the_standard_sm") is True
        and _dig(sigma, "pair_stabilizers", "p|sm_singlet_Y0", "is_sm_type") is True
        and _dig(sigma, "sigma_directions", "sm_singlet_Y0", "formula") == SIGMA_STD_FORMULA
    )
    checks["sm_candidate_report_executes"] = _executes(
        cand, status=CANDIDATE_STATUS, n_checks=CANDIDATE_N_CHECKS, overall_state=CANDIDATE_OVERALL_STATE
    )
    checks["sm_equality_set_report_executes"] = _executes(
        eq, status=EQUALITY_STATUS, n_checks=EQUALITY_N_CHECKS, theorem_claimed=True
    )
    checks["sm_exact_hessian_report_executes"] = _executes(
        hess,
        status=HESSIAN_STATUS,
        n_checks=HESSIAN_N_CHECKS,
        overall_state=HESSIAN_OVERALL_STATE,
        theorem_claimed=True,
    )
    eps_family = hess.get("eps_family")
    checks["sm_exact_hessian_eps_family_executes"] = bool(
        checks["sm_exact_hessian_report_executes"]
        and isinstance(eps_family, Mapping)
        and _strict_eq(eps_family.get("n_failed"), 0)
        and eps_family.get("failures") == []
        and _strict_eq(eps_family.get("n_checks"), EPS_N_CHECKS)
        and _all_true(eps_family.get("checks"), EPS_N_CHECKS)
        and eps_family.get("theorem_claimed") is True
        and isinstance(eps_family.get("theorem"), str)
        and not eps_family["theorem"].startswith("NOT CLAIMED")
    )

    # One coupling vector, one benchmark, one sigma_std across the three reports.
    coefficients = _dig(cand, "candidate", "exact_nonzero_coefficients")
    weights_eq = _dig(eq, "P2_sigma", "self_weights_54_1050bar_2772bar_4125", default={})
    weights_from_eq = {k: _frac(v) for k, v in weights_eq.items()} if isinstance(weights_eq, Mapping) else {}
    weights_from_candidate = {}
    if isinstance(coefficients, Mapping):
        for name, channel in O27_CHANNELS:
            value = _frac(coefficients.get(name))
            weights_from_candidate[channel] = None if value is None else 8 * value
    symbolic = _dig(eq, "sos_decomposition", "symbolic_coefficient_identity", default={})
    checks["sm_candidate_equality_set_hessian_cross_bound"] = bool(
        weights_from_eq == SELF_WEIGHTS
        and weights_from_candidate == SELF_WEIGHTS
        and _dig(eq, "P3_H_S_Phi17_phases", "operators", "count") == 27
        and _dig(eq, "P3_H_S_Phi17_phases", "operators", "count_at_kappa_0") == 25
        and _dig(cand, "exact_certificate", "equality_set", "equality_set_certificate", "status") == EQUALITY_STATUS
        and _strict_eq(_dig(cand, "exact_certificate", "equality_set", "equality_set_certificate", "n_failed"), 0)
        and _dig(symbolic, "negative", "all_residuals_zero") is True
        and _dig(symbolic, "negative", "parameters_compared") == 27
        and _dig(symbolic, "positive", "all_residuals_zero") is True
        and _dig(symbolic, "positive", "parameters_compared") == 27
        and _dig(symbolic, "zero", "all_residuals_zero") is True
        and _dig(symbolic, "zero", "parameters_compared") == 25
        and isinstance(coefficients, Mapping)
        and bool(coefficients)
        and _dig(hess, "benchmark", "exact_coefficients") == coefficients
        and derived.get("benchmark_parameters_parsed") is True
        and _frac(_dig(hess, "benchmark", "r0")) == derived.get("r0")
        and _frac(_dig(hess, "benchmark", "kappa")) == derived.get("kappa")
        and _frac(_dig(hess, "benchmark", "x0")) == derived.get("x0")
        and _frac(_dig(hess, "benchmark", "O06")) == derived.get("O06")
        and derived.get("O06_equals_2_abs_kappa_r0") is True
        and _dig(hess, "candidate_float64_claims", "all_claims_present_and_consistent") is True
        and _dig(hess, "symmetry_tangents", "matches_equality_module_ranks") is True
        and _dig(cand, "sm_embedding", "sigma_std_formula") == SIGMA_STD_FORMULA
    )
    # Per-report self-claims (g3_sm_target_track_v20.SELF_CLAIM_NOTE): no single report closes G3.
    checks["sm_reports_do_not_overclaim"] = bool(
        _dig(cand, "flags", "g3_closed") is False
        and _dig(cand, "flags", "whole_model_validated") is False
        and _dig(cand, "flags", "whole_model_excluded") is False
        and _dig(eq, "flags", "g3_closed") is False
        and _renamed_self_claim_flag(eq)
        and _dig(eq, "flags", "whole_model_validated") is False
        and _dig(eq, "flags", "whole_model_excluded") is False
        and _dig(hess, "flags", "G3_closed") is False
        and _renamed_self_claim_flag(hess)
        and hess.get("G3_closed") is False
        and _dig(sigma, "flags", "g3_closed") is False
    )
    scope_open = _dig(cand, "scope", "open")
    # Disclosure only: the flags are present as bools and scope.open is non-empty.  They are not G3 requirements:
    # decision D5 (adopted) routes them downstream (see caveat_routing_status).
    checks["sm_model_level_caveats_disclosed"] = bool(
        all(isinstance(_dig(cand, "flags", name), bool) for name in MODEL_LEVEL_FLAGS)
        and isinstance(scope_open, list)
        and bool(scope_open)
        and all(isinstance(item, str) and item for item in scope_open)
    )
    checks["sm_unchecked_proof_inputs_pinned"] = bool(
        _dig(eq, "scope", "cited_not_machine_checked") == list(PINNED_CITED_NOT_MACHINE_CHECKED)
        and _dig(eq, "scope", "elementary_not_machine_checked") == list(PINNED_ELEMENTARY_NOT_MACHINE_CHECKED)
    )
    eq_float = _dig(eq, "scope", "float64_evidence_only")
    hess_float = _dig(hess, "scope", "float64_evidence_only")
    cand_float = _dig(cand, "scope", "float64_only")
    checks["sm_float_evidence_not_promoted"] = bool(
        _dig(cand, "flags", "hessian_kernel_count_is_float64") is True
        and isinstance(cand_float, list)
        and bool(cand_float)
        and str(_dig(cand, "numerical_global_search", "note", default="")).startswith("numerical evidence")
        and isinstance(eq_float, list)
        and any(isinstance(item, str) and item.startswith("end-to-end compiler = SOS form") for item in eq_float)
        and isinstance(hess_float, list)
        and any(isinstance(item, str) and item.startswith("compiler = exact operators end to end") for item in hess_float)
    )
    return checks


# ----------------------------------------------------------------------------
# The decisive theorem: FINAL_THEOREM vs the equality module's theorem.
# ----------------------------------------------------------------------------


def _normalise_group(text: str) -> str:
    return re.sub(r"\s+", "", text).replace("U(1)_PQ", "PQ")


def decisive_theorem_comparison(
    reports: Mapping[str, Mapping[str, Any]], derived: Mapping[str, Any]
) -> dict[str, Any]:
    fg = reports.get("final_gate") or {}
    eq = reports.get("equality_set") or {}
    cand = reports.get("candidate") or {}
    hess = reports.get("exact_hessian") or {}
    # The chiral-H track's theorem (FINAL_THEOREM); the gate's top-level decisive theorem is the SM track's.
    gate_theorem = _final_gate_criteria_view(fg).get("decisive_theorem")
    eq_theorem = eq.get("theorem") if isinstance(eq.get("theorem"), str) else ""

    gate_match = re.search(r"exactly on the (\S+) orbit of q0", gate_theorem or "")
    eq_match = re.search(r"G = ([^,]+),", eq_theorem)
    gate_group = _normalise_group(gate_match.group(1)) if gate_match else None
    eq_group = _normalise_group(eq_match.group(1)) if eq_match else None

    components = {
        "same_field_chart_486_real": bool(
            "486-real field q" in (gate_theorem or "") and "canonical 486-real chart" in eq_theorem
        ),
        "lower_bound_V_ge_V0_on_whole_chart": bool(
            "satisfies V >= V0" in eq_theorem
            and _dig(cand, "exact_certificate", "V_at_vacuum_equals_V0") is True
        ),
        "equality_set_is_exactly_the_orbit_of_q0": bool(
            re.search(r"\{V = V0\} = G\.\(p, r0 sigma_std, 0, r0, x0\)", eq_theorem)
        ),
        "same_symmetry_group_G": bool(gate_group and eq_group and gate_group == eq_group),
        "uniqueness_quotient_includes_accidental_PQ_in_both": bool(
            gate_group is not None
            and gate_group.endswith("PQ")
            and _dig(eq, "flags", "uniqueness_is_modulo_G_including_accidental_U1_PQ") is True
        ),
        "q0_is_the_sm_benchmark_vacuum": bool(
            "p = e6789" in eq_theorem
            and "sigma_std = z1^z2^z3^z4^z5" in eq_theorem
            and _dig(cand, "compiler", "1/5", "state") == "(p, r0 sigma_std, 0, r0, x0)"
        ),
        "benchmark_inside_theorem_domain_kappa_squared_below_8_r0_squared": bool(
            derived.get("kappa_squared_below_8_r0_squared") is True
            and "kappa^2 < 8 r0^2" in eq_theorem
        ),
    }
    required_statement = _dig(eq, "final_acceptance_test", "required_statement")
    hessian_statement = _dig(hess, "eps_family", "final_acceptance_test", "required_statement")
    return {
        "final_theorem_pinned": FINAL_THEOREM,
        "final_theorem_in_gate_report": gate_theorem,
        "gate_report_theorem_equals_pinned": gate_theorem == FINAL_THEOREM,
        "final_gate_top_level_decisive_theorem": fg.get("decisive_theorem"),
        "final_gate_top_level_decisive_theorem_is_sm_eps_theorem": fg.get("decisive_theorem") == SM_EPS_FINAL_THEOREM,
        "sm_final_theorem": SM_FINAL_THEOREM,
        "sm_final_theorem_is_final_theorem_with_V_beta_replaced_by_V_PS": SM_FINAL_THEOREM
        == FINAL_THEOREM.replace("V_beta", "V_PS"),
        "substitutions": {
            "V_beta": "V_PS: the 27-parameter Pati-Salam benchmark of g3_sm_pati_salam_candidate_v20 (a member of "
            "the declared 51-parameter exact-X potential)",
            "q0": "(Phi, Sigma, H, S, Phi17) = (p, r0 sigma_std, 0, r0, x0), p = e6789, sigma_std = z1^z2^z3^z4^z5",
            "G": "unchanged: SO(10) x U(1)_X x U(1)_PQ (U(1)_PQ accidental in both)",
        },
        "equality_module_theorem": eq_theorem,
        "gate_symmetry_group_normalised": gate_group,
        "equality_module_symmetry_group_normalised": eq_group,
        "exact_textual_agreement": bool(eq_theorem) and eq_theorem == FINAL_THEOREM,
        "equality_module_emits_required_statement": required_statement == SM_FINAL_THEOREM,
        "sm_eps_final_theorem": SM_EPS_FINAL_THEOREM,
        "sm_eps_final_theorem_equals_track_theorem": SM_EPS_FINAL_THEOREM == sm_track.SM_FINAL_THEOREM,
        "exact_hessian_emits_sm_eps_required_statement": hessian_statement == SM_EPS_FINAL_THEOREM,
        "semantic_components": components,
        "semantic_agreement": all(components.values()),
        "differences": [
            "the equality module's theorem is a longer sentence, not the gate's one-line statement: exact textual "
            "agreement is False, and the equality module emits no final_acceptance_test.required_statement; the "
            "SM-track required statement (planner item S9, a wiring step, not a mathematical gap) is emitted for "
            "the eps witness by the exact Hessian report's eps_family.final_acceptance_test, which "
            "g3_sm_target_track_v20 reads",
            "the equality module is stronger: it holds for every r0 > 0, x0 > 0, kappa^2 < 8 r0^2, not only at "
            "the benchmark r0 = 1/5, x0 = 1, kappa = -1/20",
            "the equality module's V is the candidate's adapted SOS form, equal to the compiler potential exactly "
            "coefficient by coefficient and per source-bound operator, and in float64 end to end",
        ],
    }


# ----------------------------------------------------------------------------
# Criterion specifications: one function per final-gate criterion.
# ----------------------------------------------------------------------------


def _c_g1_g2(ev: _Evidence, d: Mapping[str, Any], ctx: Mapping[str, Any]) -> dict[str, Any]:
    ev.require("ledger_executes", "sm_candidate_report_executes")
    ev.check("ledger", ("gauged_u1x_scalar_subtheorems", "G1", "scoped_status"), "startswith 'COMPLETE'",
             lambda v: isinstance(v, str) and v.startswith("COMPLETE"))
    ev.check("ledger", ("gauged_u1x_scalar_subtheorems", "G2", "scoped_status"), "startswith 'COMPLETE'",
             lambda v: isinstance(v, str) and v.startswith("COMPLETE"))
    ev.eq("candidate", ("candidate", "exact_X_parameter_count"), 51)
    ev.eq("candidate", ("candidate", "all_parameters_in_exact_X_contract"), True)
    ledger_id = _dig(ctx["reports"].get("ledger") or {}, "model_contract_id")
    cand_id = _dig(ctx["reports"].get("candidate") or {}, "model_contract_id")
    ev.computed("candidate_and_ledger_share_the_contract_id", ledger_id == cand_id == MODEL_CONTRACT_ID,
                [ledger_id, cand_id], f"both == {MODEL_CONTRACT_ID!r}")
    return {
        "analogue": "shared_G1_G2_exact_scoped_calculations_complete",
        "statement": "The exact-X 44-direction/51-parameter G1 census and G2 derivative audit are COMPLETE on the "
        "authoritative contract, and the PS benchmark is a 27-parameter member of that declared 51-parameter "
        "potential (same contract id).",
        "why_exact": "Shared prerequisite, identical for both targets: the ledger's G1/G2 scoped statuses are "
        "COMPLETE and the PS coupling vector lies in the same 51-parameter exact-X contract.",
    }


def _c_stationary(ev: _Evidence, d: Mapping[str, Any], ctx: Mapping[str, Any]) -> dict[str, Any]:
    ev.require("sm_candidate_report_executes")
    ev.eq("candidate", ("exact_certificate", "exactly_stationary"), True)
    ev.eq("candidate", ("exact_certificate", "global_minimum_certified"), True)
    ev.eq("candidate", ("exact_slice", "gradient_vanishes_exactly"), True)
    ev.eq("candidate", ("exact_slice", "gradient_at_vacuum"), ["0", "0", "0", "0"])
    ev.eq("candidate", ("checks", "exact_state_binding"), True)
    ev.check("candidate", ("compiler", "1/5", "gradient_max_abs"), f"< {FLOAT_TOLERANCE}",
             _float_below(FLOAT_TOLERANCE), grade="float64")
    hess = ctx["reports"].get("exact_hessian") or {}
    return {
        "analogue": "sm_candidate_exactly_stationary",
        "statement": "grad V_PS(q0) = 0 exactly at q0 = (p, 0, r0 sigma_std, r0, x0): a global minimiser of a "
        "smooth function is a critical point, and the exact slice gradient vanishes identically.",
        "why_exact": "Exact: stationarity follows from the exact SOS global minimum (every r0 > 0) and is bound "
        "to the compiler state; the exact Hessian report also finds the full 486-component gradient exactly 0.",
        "notes": [
            "supporting, not required here: exact Hessian report flags.exact_gradient_zero = "
            f"{_dig(hess, 'flags', 'exact_gradient_zero')!r}, exact_certificate.gradient_exactly_zero = "
            f"{_dig(hess, 'exact_certificate', 'gradient_exactly_zero')!r}",
        ],
    }


def _c_bfb(ev: _Evidence, d: Mapping[str, Any], ctx: Mapping[str, Any]) -> dict[str, Any]:
    ev.require("sm_candidate_report_executes")
    ev.eq("candidate", ("flags", "bfb_certified"), True)
    ev.eq("candidate", ("exact_certificate", "bfb_certified"), True)
    ev.eq("candidate", ("exact_certificate", "checks", "quartic_part_strictly_positive"), True)
    ev.eq("candidate", ("exact_certificate", "exact_quartic_bound", "constant"), "1/167")
    ev.eq("candidate", ("exact_certificate", "exact_quartic_bound", "matches_recorded_constant"), True)
    constant = d.get("quartic_bound_constant")
    ev.computed("quartic_bound_constant_equals_1_over_sum_beta_squared_over_alpha", constant == Fraction(1, 167),
                str(constant) if constant is not None else None, "== 1/167")
    for name in ("A_square_recoupling_exact", "C_square_recoupling_exact", "Phi_H_term_is_exact_wedge_square",
                 "coefficient_map_equals_adapted_SOS_expansion_symbolically"):
        ev.eq("candidate", ("exact_certificate", "checks", name), True)
    ev.eq("candidate", ("numerical_global_search", "quartic_directions", "lowest_at_or_above_exact_bound"), True,
          grade="float64")
    return {
        "analogue": "sm_full_homogeneous_quartic_BFB_exact",
        "statement": "The homogeneous quartic part of V_PS is strictly positive on the full 486-real chart: "
        "V4(q) >= |q|^4/167 (exact, source-bound recouplings).",
        "why_exact": "Exact: the candidate's source-bound SOS certificate gives V4 >= |q|^4/167, and 1/167 = "
        "1/sum(beta^2/alpha) is recomputed here from its recorded rationals.",
    }


def _c_sm_algebra(ev: _Evidence, d: Mapping[str, Any], ctx: Mapping[str, Any]) -> dict[str, Any]:
    ev.require("sm_candidate_report_executes", "sigma_hypercharge_audit_executes")
    for key in (("flags", "target_unbroken_algebra_is_standard_model"), ("flags", "candidate_is_sm_vacuum"),
                ("checks", "unbroken_algebra_is_exactly_standard_model"),
                ("sm_embedding", "heavy_pair_stabilizer", "is_sm_type"),
                ("sm_embedding", "heavy_pair_stabilizer", "contains_standard_sm_algebra"),
                ("sm_embedding", "sigma_std_exact_charges", "SU3_colour_singlet")):
        ev.eq("candidate", key, True)
    ev.eq("candidate", ("sm_embedding", "heavy_pair_stabilizer", "contains_flipped_sm_algebra"), False)
    ev.eq("candidate", ("sm_embedding", "heavy_pair_stabilizer", "stabilizer_dimension"), 12)
    ev.eq("candidate", ("sm_embedding", "full_state_stabilizer_so10_plus_u1x", "stabilizer_dimension"), 12)
    ev.eq("candidate", ("sm_embedding", "full_state_stabilizer_so10_plus_u1x", "u1x_admixture_dimension"), 0)
    ev.eq("candidate", ("sm_embedding", "sigma_std_exact_charges", "Y"), "0")
    ev.eq("candidate", ("sm_embedding", "sigma_std_exact_charges", "Q_em"), "0")
    ev.eq("sigma_hypercharge", ("checks", "p_sm_singlet_Y0_is_the_standard_sm"), True)
    ev.eq("sigma_hypercharge", ("pair_stabilizers", "p|sm_singlet_Y0", "is_sm_type"), True)
    ev.eq("sigma_hypercharge", ("pair_stabilizers", "p|sm_singlet_Y0", "centre_proportional_to"), ["Y_standard"])
    ev.eq("sigma_hypercharge", ("sigma_directions", "sm_singlet_Y0", "formula"), SIGMA_STD_FORMULA)
    return {
        "analogue": "sm_target_unbroken_algebra_is_standard_model_exact",
        "statement": "The unbroken algebra of the full vacuum inside so(10) + u(1)_X is exactly su(3)_c + su(2)_L "
        "+ u(1)_Y in the standard embedding; sigma_std = z1^z2^z3^z4^z5 is the Y = 0, Q_em = 0 colour-singlet "
        "member of the 126bar (10bar,1,3).",
        "why_exact": "Exact integer stabilizer computation, confirmed independently by the sigma-hypercharge "
        "audit (p with the Y = 0 singlet leaves exactly the standard SM); the chiral-H point fails this.",
    }


def _c_orbit_ranks(ev: _Evidence, d: Mapping[str, Any], ctx: Mapping[str, Any]) -> dict[str, Any]:
    ev.require("sm_equality_set_report_executes", "sm_candidate_report_executes")
    base = ("P3_H_S_Phi17_phases", "tangent_rank")
    ev.eq("equality_set", base + ("rank_so10",), 33)
    ev.eq("equality_set", base + ("rank_so10_plus_X",), 34)
    ev.eq("equality_set", base + ("rank_so10_plus_X_plus_PQ",), 35)
    ev.eq("equality_set", base + ("kernel_dimension",), 12)
    ev.eq("equality_set", base + ("kernel_has_no_X_or_PQ_component",), True)
    ev.eq("equality_set", ("checks", "P3_orbit_tangent_rank_35_kernel_12_pure_so10"), True)
    stab = _dig(ctx["reports"].get("candidate") or {}, "sm_embedding", "full_state_stabilizer_so10_plus_u1x",
                "stabilizer_dimension")
    rank = _dig(ctx["reports"].get("equality_set") or {}, *base, "rank_so10")
    ev.computed("45_minus_so10_rank_equals_candidate_stabilizer_dimension",
                _is_int(stab) and _is_int(rank) and 45 - rank == stab, [rank, stab], "45 - 33 == 12")
    ev.eq("candidate", ("compiler", "1/5", "symmetry_ranks"),
          {"so10_orbit_rank": 33, "so10_plus_u1x_plus_pq_rank": 35, "so10_plus_u1x_rank": 34}, grade="float64")
    hess = ctx["reports"].get("exact_hessian") or {}
    return {
        "analogue": "sm_symmetry_orbit_ranks_33_34_35_exact",
        "statement": "Exact orbit tangent ranks at q0 (486 x 47 integer tangents, all r0, x0 > 0): so(10) 33, "
        "+U(1)_X 34, +U(1)_PQ 35, with a 12-dimensional pure-so(10) stabilizer; orbit dimension 35, transverse "
        "quotient 486 - 35 = 451.",
        "why_exact": "Exact integer ranks from the equality module (P3), consistent with the candidate's exact "
        "12-dimensional SM stabilizer (45 - 33 = 12); the chiral-H ranks 36/37/38 belong to a 9-dimensional "
        "stabilizer and do not transfer.",
        "notes": [
            "supporting, not required here: the exact Hessian report re-derives these ranks, "
            f"symmetry_tangents.exact_ranks = {_brief(_dig(hess, 'symmetry_tangents', 'exact_ranks'))!r}",
        ],
    }


def _c_couplings(ev: _Evidence, d: Mapping[str, Any], ctx: Mapping[str, Any]) -> dict[str, Any]:
    ev.require("sm_candidate_report_executes")
    ev.eq("candidate", ("candidate", "nonzero_count"), 27)
    ev.eq("candidate", ("candidate", "all_parameters_in_exact_X_contract"), True)
    ev.eq("candidate", ("candidate", "maximum_absolute_coefficient"), "73/8")
    count = d.get("coefficients_nonzero_count")
    ev.computed("exact_nonzero_coefficient_count", count == 27 and len(d.get("coefficients", {})) == 27, count,
                "== 27 (all recorded coefficients nonzero rationals)")
    maximum = d.get("coefficients_max_abs")
    ev.computed("maximum_absolute_coefficient_recomputed", maximum == Fraction(73, 8),
                str(maximum) if maximum is not None else None, "== 73/8")
    ev.computed("maximum_below_12_hence_below_4pi", maximum is not None and maximum < 12,
                str(maximum) if maximum is not None else None, "< 12 < 4 pi (pi > 3): exact rational comparison")
    ev.eq("candidate", ("candidate", "float_map_inside_4pi_box"), True, grade="float64")
    return {
        "analogue": "sm_couplings_perturbative_exact",
        "statement": "Exactly 27 nonzero real couplings, all in the exact-X contract, with max |coefficient| = "
        "73/8 < 12 < 4 pi.",
        "why_exact": "Exact rational comparison (73/8 < 12 and pi > 3); the gate's chiral-H criterion compares "
        "floats against 4 pi with 28 couplings.",
    }


def _orbit_rank(ctx: Mapping[str, Any]) -> int | None:
    """Exact SO(10) x U(1)_X x U(1)_PQ orbit dimension at q0 recorded by the equality module (35), or None."""
    value = _dig(ctx["reports"].get("equality_set") or {}, "P3_H_S_Phi17_phases", "tangent_rank",
                 "rank_so10_plus_X_plus_PQ")
    return value if _is_int(value) and 0 < value < TOTAL_DIM else None


def _c_rank_nullity(ev: _Evidence, d: Mapping[str, Any], ctx: Mapping[str, Any]) -> dict[str, Any]:
    ev.require("sm_exact_hessian_report_executes", "sm_equality_set_report_executes",
               "sm_candidate_equality_set_hessian_cross_bound")
    hess = ctx["reports"].get("exact_hessian") or {}
    # The chiral-H criterion's 448/38 is (486 - orbit rank) / orbit rank: 38 is the SO(10) x U(1)_X x PQ rank and
    # 448 the gate's physical_quotient_dimension.  The literal PS analogue is therefore 451/35, not whatever the
    # certificate happens to find.
    orbit = _orbit_rank(ctx)
    expected_nullity = orbit
    expected_rank = TOTAL_DIM - orbit if orbit is not None else None
    ev.computed("orbit_rank_recorded_by_equality_module", orbit == 35, orbit,
                "equality_set P3 tangent_rank.rank_so10_plus_X_plus_PQ == 35")
    for name in ("source_binding_exact", "proof_grade"):
        ev.eq("exact_hessian", ("flags", name), True)
    ev.check("exact_hessian", ("exact_certificate", "exact_rank"), f"== 486 - orbit rank = {expected_rank}",
             lambda v: expected_rank is not None and _strict_eq(v, expected_rank))
    ev.check("exact_hessian", ("exact_certificate", "exact_nullity"), f"== orbit rank = {expected_nullity}",
             lambda v: expected_nullity is not None and _strict_eq(v, expected_nullity))
    inertia = _dig(hess, "exact_certificate", "inertia", default={})
    rank = _dig(hess, "exact_certificate", "exact_rank")
    nullity = _dig(hess, "exact_certificate", "exact_nullity")
    consistent = bool(
        isinstance(inertia, Mapping)
        and all(_is_int(inertia.get(k)) for k in ("positive", "zero", "negative"))
        and _is_int(rank) and _is_int(nullity)
        and inertia["positive"] + inertia["negative"] == rank
        and inertia["zero"] == nullity
        and rank + nullity == TOTAL_DIM
    )
    triple = (
        "/".join(str(inertia.get(k)) for k in ("positive", "zero", "negative")) if isinstance(inertia, Mapping) else None
    )
    ev.computed("inertia_consistent_with_rank_and_nullity_and_sums_to_486", consistent,
                {"inertia_positive_zero_negative": triple, "rank": rank, "nullity": nullity},
                "positive + negative == rank, zero == nullity, rank + nullity == 486")
    for key, value in (("r0", "1/5"), ("kappa", "-1/20"), ("x0", "1"), ("O06", "1/50")):
        ev.eq("exact_hessian", ("benchmark", key), value)
    # float64 analogue of nullity == orbit rank: no projected (non-symmetry) zero mode.
    ev.eq("candidate", ("compiler", "1/5", "projected_hessian", "n_negative"), 0, grade="float64")
    ev.eq("candidate", ("compiler", "1/5", "projected_hessian", "n_zero"), 0, grade="float64")
    ev.eq("candidate", ("compiler", "1/5", "symmetry_ranks", "so10_plus_u1x_plus_pq_rank"), 35, grade="float64")
    spanning = _dig(hess, "exact_certificate", "kernel_spanning_set")
    extra = nullity - expected_nullity if _is_int(nullity) and expected_nullity is not None else None
    return {
        "analogue": "sm_full_Hessian_rank_451_nullity_35_exact",
        "statement": "Literal analogue: proof-grade, source-bound exact certificate that the complete 486 x 486 "
        f"Hessian at the benchmark (r0 = 1/5, x0 = 1, kappa = -r0/4, O06 = 2|kappa| r0) has rank 486 - orbit rank "
        f"= {expected_rank} and nullity = orbit rank = {expected_nullity} (the chiral-H 448/38 is 486 - 38 / 38).",
        "why_exact": f"Exact over Q: rank {expected_rank} / nullity {expected_nullity} by rational LDL inertia in "
        "radical-free coordinates (Sylvester), source-bound entries.",
        "why_failed": (
            f"Exactly false at the tuned benchmark: exact rank/nullity {rank}/{nullity} instead of the literal "
            f"{expected_rank}/{expected_nullity}; the certified kernel is {spanning}, i.e. {extra} tuned "
            f"light-doublet zero modes beyond the {expected_nullity}-dimensional orbit."
            if consistent and _is_int(extra) and extra > 0
            else f"Exact evidence refutes it: exact rank/nullity {rank}/{nullity}, inertia (+/0/-) {triple}, "
            f"literal {expected_rank}/{expected_nullity}."
        ),
        "notes": [
            f"certified facts (exact, not the literal analogue): rank {rank}, nullity {nullity}, inertia (+/0/-) "
            f"{triple}, flags.exact_rank_447 = {_dig(hess, 'flags', 'exact_rank_447')!r}, "
            f"flags.exact_nullity_39 = {_dig(hess, 'flags', 'exact_nullity_39')!r}, exact_PSD = "
            f"{_dig(hess, 'exact_certificate', 'exact_PSD')!r}",
            "the planner's S11 (see full_448_quotient_strictly_positive_exact.alternative_analogues) would replace "
            "this criterion and the quotient criterion together by 'rank 447 / nullity 39, kernel = orbit (+) tuned "
            "doublet'; the O06-raised member (S12) meets the literal 451/35 exactly",
            "benchmark-only: exact Hessian flags.other_r0_x0_kappa_certified = "
            f"{_dig(hess, 'flags', 'other_r0_x0_kappa_certified')!r}",
            "the float64 analogue (no projected zero mode) also fails: the candidate records 4 projected zero modes "
            "beside symmetry rank 35; the exact report's live numerical inertia (zero modes at 1e-10) is "
            f"{_dig(hess, 'live_binding', 'numerical_inertia', 'zero_at_1e_minus_10')!r}",
        ],
    }


def _s11_evidence(ev: _Evidence, d: Mapping[str, Any], ctx: Mapping[str, Any]) -> None:
    ev.require("sm_exact_hessian_report_executes", "sm_candidate_report_executes",
               "sm_candidate_equality_set_hessian_cross_bound")
    for name in ("source_binding_exact", "proof_grade", "exact_PSD", "exact_rank_447", "exact_nullity_39",
                 "kernel_equals_35_symmetry_tangents_plus_4_light_doublet",
                 "positive_definite_on_complement_of_39_dim_kernel"):
        ev.eq("exact_hessian", ("flags", name), True)
    cert = ("exact_certificate",)
    ev.eq("exact_hessian", cert + ("exact_rank",), 447)
    ev.eq("exact_hessian", cert + ("exact_nullity",), 39)
    ev.eq("exact_hessian", cert + ("inertia", "negative"), 0)
    for name in ("kernel_equals_expected_span", "symmetry_tangents_in_kernel_exact",
                 "doublet_directions_in_kernel_exact", "strictly_positive_on_kernel_complement", "exact_PSD"):
        ev.eq("exact_hessian", cert + (name,), True)
    ev.eq("exact_hessian", cert + ("kernel_spanning_rank_exact",), 39)
    ev.eq("exact_hessian", cert + ("zero_modes_beyond_symmetry_orbit",), 4)
    ev.eq("exact_hessian", cert + ("positive_pivot_complement", "dimension"), 447)
    ev.eq("exact_hessian", cert + ("spectral_gap", "lambda_over_r0_squared"), "1/96")
    ev.eq("exact_hessian", ("light_doublet_directions", "chart_indices"), [222, 224, 226, 228])
    lam = d.get("lambda_eff")
    recorded = _frac(_dig(ctx["reports"].get("candidate") or {}, "light_doublet_quartic", "exact_by_benchmark",
                          "1/5", "lambda_eff"))
    ev.computed("tuned_doublet_lifted_at_quartic_order_lambda_eff_positive",
                lam is not None and lam == Fraction(127, 64) and lam == recorded and lam > 0,
                [str(lam) if lam is not None else None, str(recorded) if recorded is not None else None],
                "lambda_eff = 2 - kappa^2/(4 r0^2) == recorded == 127/64 > 0")
    ev.eq("candidate", ("flags", "hessian_psd_kernel_is_symmetry_plus_tuned_light_doublet"), True, grade="float64")


def _s12_evidence(ev: _Evidence, d: Mapping[str, Any], ctx: Mapping[str, Any]) -> None:
    ev.require("sm_exact_hessian_report_executes", "sm_candidate_equality_set_hessian_cross_bound")
    raised = ("exact_certificate_raised_O06",)
    ev.eq("exact_hessian", raised + ("exact_rank",), 451)
    ev.eq("exact_hessian", raised + ("exact_nullity",), 35)
    ev.eq("exact_hessian", raised + ("kernel_spanning_set",), "35 symmetry tangents")
    for name in ("kernel_equals_expected_span", "strictly_positive_on_kernel_complement", "exact_PSD",
                 "gradient_exactly_zero", "strictly_positive_on_symmetry_quotient"):
        ev.eq("exact_hessian", raised + (name,), True)
    ev.eq("exact_hessian", raised + ("inertia", "negative"), 0)
    ev.eq("exact_hessian", raised + ("zero_modes_beyond_symmetry_orbit",), 0)
    ev.eq("exact_hessian", raised + ("spectral_gap", "lambda_over_r0_squared"), "1/100")
    ev.eq("exact_hessian", ("flags", "raised_O06_strict_quotient_positive"), True)
    ev.eq("exact_hessian", ("flags", "raised_O06_strictly_positive_on_symmetry_quotient"), True)
    ev.computed("raise_is_r0_squared_over_100", d.get("O06_raise_equals_r0_squared_over_100") is True,
                d.get("O06_raise_equals_r0_squared_over_100"), "O06_raise == r0^2/100")


def _c_quotient_positive(ev: _Evidence, d: Mapping[str, Any], ctx: Mapping[str, Any]) -> dict[str, Any]:
    ev.require("sm_exact_hessian_report_executes", "sm_equality_set_report_executes")
    hess = ctx["reports"].get("exact_hessian") or {}
    orbit = _orbit_rank(ctx)
    # The gate's criterion: exact_PSD, strict_quotient_positive and kernel_equals_38_symmetry_tangents.  The PS
    # exact Hessian report uses strict_quotient_positive in the repository's sense (kernel = symmetry tangents).
    ev.eq("exact_hessian", ("flags", "exact_PSD"), True)
    ev.eq("exact_hessian", ("flags", "strict_quotient_positive"), True)
    ev.eq("exact_hessian", ("flags", "strictly_positive_on_symmetry_quotient"), True)
    ev.eq("exact_hessian", ("flags", "all_zero_modes_are_symmetry_tangents"), True)
    cert = ("exact_certificate",)
    ev.eq("exact_hessian", cert + ("exact_PSD",), True)
    ev.eq("exact_hessian", cert + ("inertia", "negative"), 0)
    ev.eq("exact_hessian", cert + ("strictly_positive_on_symmetry_quotient",), True)
    ev.eq("exact_hessian", cert + ("zero_modes_beyond_symmetry_orbit",), 0)
    ev.eq("exact_hessian", cert + ("symmetry_tangents_in_kernel_exact",), True)
    ev.eq("exact_hessian", cert + ("kernel_equals_expected_span",), True)
    ev.eq("exact_hessian", cert + ("strictly_positive_on_kernel_complement",), True)
    ev.check("exact_hessian", cert + ("exact_nullity",), f"== orbit rank = {orbit}",
             lambda v: orbit is not None and _strict_eq(v, orbit))
    ev.eq("exact_hessian", cert + ("kernel_spanning_set",), "35 symmetry tangents")
    ev.eq("candidate", ("flags", "hessian_psd_kernel_is_symmetry"), True, grade="float64")
    ev.eq("candidate", ("compiler", "1/5", "projected_hessian", "n_zero"), 0, grade="float64")
    nullity = _dig(hess, "exact_certificate", "exact_nullity")
    spanning = _dig(hess, "exact_certificate", "kernel_spanning_set")
    psd = _dig(hess, "exact_certificate", "exact_PSD")
    extra = _dig(hess, "exact_certificate", "zero_modes_beyond_symmetry_orbit")
    complement = _dig(hess, "exact_certificate", "positive_pivot_complement", "dimension")
    quotient_dimension = TOTAL_DIM - orbit if orbit is not None else None

    s11 = _Evidence(ctx["reports"], ctx["integrity"])
    _s11_evidence(s11, d, ctx)
    s12 = _Evidence(ctx["reports"], ctx["integrity"])
    _s12_evidence(s12, d, ctx)
    inside = d.get("O06_raised_inside_27_parameter_family") is True
    out_of_scope = _dig(ctx["reports"].get("equality_set") or {}, "scope", "not_proved_or_out_of_scope", default=[])
    listed = isinstance(out_of_scope, list) and "potentials outside the candidate's 27-parameter family" in out_of_scope
    eps_covered = bool(
        ctx["integrity"].get("sm_exact_hessian_eps_family_executes") is True
        and all(_dig(hess, "flags", name) is True for name in EPS_FLAGS)
        and d.get("eps_raised") is not None
        and d["eps_raised"] > 0
    )
    return {
        "analogue": "sm_full_451_quotient_strictly_positive_exact",
        "statement": "Literal analogue: the Hessian at q0 is PSD, its kernel is exactly the 35-dimensional G-orbit "
        "tangent space, and it is strictly positive on the 451-dimensional quotient by it.",
        "why_exact": "Exact: PSD, kernel = orbit tangents and strictly positive on the 451-dimensional quotient.",
        "why_failed": (
            f"Exactly false at the tuned benchmark: the certified kernel is {spanning} (exact nullity {nullity} vs "
            f"orbit dimension {orbit}; exact_PSD {psd}), so the {quotient_dimension}-dimensional symmetry quotient "
            f"has an exact {extra}-dimensional kernel and the Hessian is positive definite only on a "
            f"{complement}-dimensional complement of its kernel."
            if psd is True and _is_int(extra) and extra > 0
            else f"Exact evidence refutes it: exact_PSD {psd}, exact nullity {nullity} vs orbit dimension {orbit}, "
            f"kernel spanned by {spanning}."
        ),
        "notes": [
            "the PS exact Hessian report uses the repository's meaning: flags.strict_quotient_positive = "
            f"{_dig(hess, 'flags', 'strict_quotient_positive')!r} (kernel = symmetry tangents, as in the chiral-H "
            "certificate); its flags.positive_definite_on_complement_of_39_dim_kernel = "
            f"{_dig(hess, 'flags', 'positive_definite_on_complement_of_39_dim_kernel')!r} is positivity on a "
            "complement of the full kernel (orbit + tuned doublet), which any PSD matrix has once its kernel is "
            "identified, and is not this criterion",
            "the 4 flat quadratic directions are not flat globally: the equality set is exactly the G-orbit, and "
            "the doublet is lifted at quartic order by lambda_eff = 127/64 > 0 (exact)",
        ],
        "alternative_analogues": {
            "S11_kernel_is_orbit_plus_tuned_light_doublet_exact": {
                "statement": "Planner replacement criterion S11, replacing BOTH full_Hessian_rank_448_nullity_38_exact "
                "and full_448_quotient_strictly_positive_exact: proof-grade, source-bound exact rank 447 / nullity 39 "
                "with ker Hess V(q0) = T35 (+) D4 exactly (35 orbit tangents plus the 4 real light-doublet directions "
                "Re H_6..9), PSD, positive definite on a 447-dimensional complement, smallest nonzero eigenvalue "
                "r0^2/96, and the doublet lifted at quartic order by lambda_eff = 127/64 > 0.",
                "replaces_criteria": ["full_Hessian_rank_448_nullity_38_exact", "full_448_quotient_strictly_positive_exact"],
                "value": bool(s11.exact) and all(item["ok"] for item in s11.exact),
                "grade": "exact",
                "evidence_exact": s11.exact,
                "evidence_float64": s11.float64,
                "adopting_it_changes_the_gate_contract": True,
                "decision": "D2",
            },
            "S12_O06_raised_member_rank_451_nullity_35_exact": {
                "statement": "Planner control S12: raising O06 by r0^2/100 gives rank 451, nullity 35, kernel exactly "
                "the orbit tangents, strictly positive on the symmetry quotient, smallest nonzero eigenvalue "
                "r0^2/100 -- both literal Hessian criteria hold exactly for that member.",
                "value": bool(s12.exact) and all(item["ok"] for item in s12.exact),
                "grade": "exact",
                "evidence_exact": s12.exact,
                "raised_member_inside_certified_27_parameter_family": inside,
                "family_boundary_listed_out_of_scope_by_equality_module": listed,
                "global_minimum_and_equality_set_artifacts_cover_raised_member": inside,
                "covered_by_exact_hessian_eps_family_L1_L2": eps_covered,
                "comment": "O06 = 51/2500 != 2|kappa| r0 = 1/50 lies outside the candidate's 27-parameter family, so the "
                "candidate and equality-set artifacts alone do not cover it; it is the eps = r0^2/100 member of the "
                "eps family V_eps = V + eps N_H, which the exact Hessian report's eps_family covers (L1: {V_eps = V0} = "
                "G.q0 given the equality-set theorem; L2: kernel = orbit for every eps > 0); see eps_member",
            },
        },
    }


def _route_specific(analogue: str, statement: str, counterpart_artifact: str, counterpart_key: Sequence[str],
                    counterpart_text: str) -> Callable[[_Evidence, Mapping[str, Any], Mapping[str, Any]], dict[str, Any]]:
    def build(ev: _Evidence, d: Mapping[str, Any], ctx: Mapping[str, Any]) -> dict[str, Any]:
        ev.eq(counterpart_artifact, counterpart_key, True)
        return {
            "analogue": analogue,
            "statement": statement,
            "route_specific": True,
            "pati_salam_counterpart": counterpart_text,
        }

    return build


_C_FIXED_F = _route_specific(
    "none (chiral-H route: fixed Phi = F stratum)",
    "Not applicable: the chiral-H proof bounds V on the fixed Phi = F stratum first because its SOS does not "
    "cover arbitrary Phi at once.",
    "candidate", ("exact_certificate", "global_minimum_certified"),
    "the adapted SOS27 identity bounds V_PS on the whole chart for arbitrary Phi at once",
)
_C_MAX_NEG_ZERO = _route_specific(
    "none (chiral-H route: maximally-negative pure-Delta sector, zero residuals)",
    "Not applicable: this excludes a Sigma sector where the chiral-H SOS completion could fail; the PS proof has "
    "no such sector.",
    "equality_set", ("checks", "P0_eight_terms_expand_to_the_candidate_operator_map_with_constant_minus_V0"),
    "V_PS - V0 is a sum of eight terms each >= 0 on the whole chart (P0), with no residual sectors",
)
_C_MAX_NEG_FULL = _route_specific(
    "none (chiral-H route: maximally-negative pure-Delta sector, all residuals)",
    "Not applicable: residual-gap bound specific to the chiral-H SOS reduction.",
    "equality_set", ("checks", "P0_coefficient_map_equals_SOS_expansion_for_kappa_negative_positive_zero"),
    "the eight-term SOS expansion matches the coefficient map exactly (kappa < 0, > 0, = 0)",
)
_C_RANK1_SU3 = _route_specific(
    "none (chiral-H route: rank-one SU(3) four-dimensional Phi slice)",
    "Not applicable: a slice of the chiral-H rank-one Phi program.",
    "candidate", ("exact_certificate", "checks", "exact_210_global_bound_and_P_saturation"),
    "the exact 210 bound V_Phi >= -1 holds for every real Phi, saturated on SO(10).p",
)
_C_RANK1_SU4 = _route_specific(
    "none (chiral-H route: rank-one SU(4) Schur SOS infrastructure)",
    "Not applicable: infrastructure for the chiral-H fixed-endpoint Schur SOS/SDP program; the PS proof needs no "
    "SDP.",
    "candidate", ("exact_certificate", "checks", "coefficient_map_equals_adapted_SOS_expansion_symbolically"),
    "a closed-form SOS identity (symbolic, all r0 > 0) replaces the SDP program",
)
_C_SIGNED_PHI = _route_specific(
    "none (chiral-H route: signed +-F Phi orbits)",
    "Not applicable: local isolation of the signed Phi = +-F orbits of the chiral-H route.",
    "equality_set", ("corollary_exact_210", "uniqueness_of_global_orbit"),
    "the Phi minimum set is the single global orbit SO(10).p (exact_210 corollary of P1)",
)
_C_SU3_SLICE = _route_specific(
    "none (chiral-H route: SU(3)-fixed Phi slice)",
    "Not applicable: slice-by-slice Phi classification of the chiral-H route.",
    "equality_set", ("checks", "P1_pluecker_defect_detects_decomposability"),
    "P1 classifies every Phi with |Phi| = 1, I45 = I210 = I5940 = 0 at once via the Pluecker defect",
)


def _c_equality_set(ev: _Evidence, d: Mapping[str, Any], ctx: Mapping[str, Any]) -> dict[str, Any]:
    ev.require("sm_equality_set_report_executes", "sm_candidate_report_executes", "sm_unchecked_proof_inputs_pinned")
    ev.eq("equality_set", ("flags", "equality_set_unique_modulo_symmetry_certified"), True)
    ev.eq("equality_set", ("flags", "theorem_claimed"), True)
    ev.eq("equality_set", ("flags", "uniqueness_is_modulo_G_including_accidental_U1_PQ"), True)
    ev.eq("equality_set", ("flags", "unique_modulo_SO10_x_U1X_alone"), False)
    ev.eq("equality_set", ("flags", "kappa_squared_equal_8_r0_squared_claimed"), False)
    ev.computed("benchmark_inside_domain_kappa_squared_below_8_r0_squared",
                d.get("kappa_squared_below_8_r0_squared") is True,
                [str(d.get("kappa")), str(d.get("r0"))], "kappa^2 < 8 r0^2 (exact)")
    ev.eq("candidate", ("exact_certificate", "equality_set", "unique_modulo_symmetry_certified"), True)
    ev.eq("candidate", ("exact_certificate", "equality_set", "equality_set_certificate", "status"), EQUALITY_STATUS)
    ev.eq("equality_set", ("numerical_corroboration", "consistent"), True, grade="float64")
    ev.eq("candidate", ("numerical_global_search", "endpoint_classification", "all_converged_endpoints_on_sm_vacuum_orbit"),
          True, grade="float64")
    return {
        "analogue": "sm_equality_set_single_G_orbit_exact",
        "statement": "Every equality point is classified: {V_PS = V0} = G.q0, one orbit of G = SO(10) x U(1)_X x "
        "U(1)_PQ, for every r0 > 0, x0 > 0, kappa^2 < 8 r0^2 (the benchmark lies inside); there are no other "
        "equality orbits.",
        "why_exact": "Exact proof (P0-P3; 45 checks) that rests on 6 cited classical theorems and 6 hand-argued "
        "elementary steps that are not machine-checked (pinned verbatim here and in g3_sm_target_track_v20); "
        "counting it as exact presumes decision D6 (cited classical theorems and hand-argued steps accepted as "
        "G3-grade inputs), which is adopted.  Uniqueness uses the accidental U(1)_PQ, which the gate's theorem "
        "already quotients by.",
        "exact_grade": "exact (cited classical theorems + 6 hand-argued steps; D6)",
        "conditional_on_decisions": ["D6"],
        "notes": [
            "outside the Pati-Salam program (the candidate, the equality set and the exact_210 corollary bound to "
            "it) no repository artifact, in particular none of the chiral-H evidence the final gate reads, relies on "
            "cited or non-machine-checked theorems; decision D6 (adopted) accepts them at G3 grade, pinned by an "
            "allowlist and disclosed",
        ],
    }


def _c_global_gap(ev: _Evidence, d: Mapping[str, Any], ctx: Mapping[str, Any]) -> dict[str, Any]:
    ev.require("sm_candidate_report_executes", "sm_equality_set_report_executes", "sm_unchecked_proof_inputs_pinned")
    ev.eq("candidate", ("exact_certificate", "global_minimum_certified"), True)
    ev.eq("candidate", ("exact_certificate", "V_at_vacuum_equals_V0"), True)
    ev.check("candidate", ("exact_certificate", "checks"), "16 entries, all True", lambda v: _all_true(v, 16))
    ev.eq("candidate", ("exact_certificate", "symbolic_identity", "all_residuals_zero"), True)
    ev.eq("candidate", ("exact_certificate", "symbolic_identity", "parameters_compared"), 27)
    ev.eq("equality_set", ("flags", "equality_set_unique_modulo_symmetry_certified"), True)
    v0 = d.get("V0")
    recorded = _frac(_dig(ctx["reports"].get("candidate") or {}, "candidate", "benchmarks", "1/5", "V0"))
    slice_value = _frac(_dig(ctx["reports"].get("candidate") or {}, "exact_slice", "value_at_vacuum"))
    ev.computed("V0_formula_equals_recorded_benchmark_value",
                v0 is not None and v0 == recorded == slice_value == Fraction(-20661, 20000),
                [str(v0), str(recorded), str(slice_value)],
                "-1 - r0^4/8 - r0^4 - x0^4/32 == recorded V0 == exact slice value == -20661/20000")
    ev.computed("decisive_theorem_semantic_agreement", ctx["theorem"]["semantic_agreement"] is True,
                ctx["theorem"]["semantic_agreement"], "True (see decisive_theorem)")
    ev.check("candidate", ("compiler", "1/5", "V_minus_V0"), f"|.| < {FLOAT_TOLERANCE}",
             _float_below(FLOAT_TOLERANCE), grade="float64")
    ev.eq("candidate", ("numerical_global_search", "nothing_found_below_V0"), True, grade="float64")
    return {
        "analogue": "sm_global_gap_and_unique_equality_exact",
        "statement": SM_FINAL_THEOREM + "  (Proved for the whole family r0 > 0, x0 > 0, kappa^2 < 8 r0^2; at the "
        "benchmark V0 = -20661/20000.)",
        "why_exact": "Exact up to pinned hand-argued steps: the adapted SOS27 identity (symbolic in r0, x0, kappa; "
        "16 exact certificate checks) gives V_PS >= V0 with V(q0) = V0, but its H/S sector bound V_HS >= -r0^4 also "
        "uses the hand-argued Cauchy-Schwarz step |H.H| <= N_H and the sign case analysis (|S| <= r0, |S| > r0) that "
        "turns the exact sympy square-completion identities into the inequality (not machine-checked); the equality "
        "module proves {V_PS = V0} = G.q0 with 6 cited classical theorems and 6 hand-argued steps.  Counting it as "
        "exact presumes decision D6 (adopted).",
        "exact_grade": "exact (cited classical theorems + 6 hand-argued steps; D6)",
        "conditional_on_decisions": ["D6"],
        "literal_conjuncts_not_evaluated": ["required_statement == theorem (wiring; S9)"],
        "notes": [
            "the chiral-H criterion has the conjunct gap_acceptance.required_statement == FINAL_THEOREM; it is not "
            "evaluated here (the equality module emits no final_acceptance_test block: "
            f"required_statement emitted = {ctx['theorem']['equality_module_emits_required_statement']!r}); the "
            "decisive-theorem semantic agreement stands in for it.  The SM track's wiring step (planner S9) is the "
            "exact Hessian report's eps_family.final_acceptance_test.required_statement (emitted = "
            f"{ctx['theorem']['exact_hessian_emits_sm_eps_required_statement']!r}), evaluated by "
            "g3_sm_target_track_v20 and listed under integration_gaps",
            "V_PS is the candidate's adapted SOS form: equal to the compiler potential exactly per coefficient and "
            "per source-bound operator, and in float64 end to end",
        ],
    }


def _c_release_contract(ev: _Evidence, d: Mapping[str, Any], ctx: Mapping[str, Any]) -> dict[str, Any]:
    ev.require("ledger_executes")
    ev.eq("ledger", ("contract_consistent",), True)
    ev.eq("ledger", ("model_contract_id",), MODEL_CONTRACT_ID)
    ids = [(_dig(ctx["reports"].get(key) or {}, "model_contract_id")) for key in ("candidate", "equality_set", "exact_hessian")]
    ev.computed("pati_salam_reports_use_the_authoritative_contract", all(i == MODEL_CONTRACT_ID for i in ids), ids,
                f"all == {MODEL_CONTRACT_ID!r}")
    return {
        "analogue": "authoritative_external_model_contract_executed (shared)",
        "statement": "The authoritative gauged-U(1)_X contract is executed and consistent, and the three PS "
        "reports are built on it.",
        "why_exact": "Non-numerical status evidence: ledger contract_consistent = True and every PS report "
        "carries the authoritative contract id.",
    }


def _c_release_gate(gate: str) -> Callable[[_Evidence, Mapping[str, Any], Mapping[str, Any]], dict[str, Any]]:
    def build(ev: _Evidence, d: Mapping[str, Any], ctx: Mapping[str, Any]) -> dict[str, Any]:
        ev.require("ledger_executes")
        ev.eq("ledger", ("gates", gate, "status"), "CLOSED")
        return {
            "analogue": f"{gate}_promoted_closed (shared)",
            "statement": f"{gate} is CLOSED in the G1-G8 ledger on the authoritative contract.",
            "why_exact": f"Non-numerical status evidence: ledger gates.{gate}.status == 'CLOSED'.",
        }

    return build


SCIENCE_SPECS: dict[str, Callable[..., dict[str, Any]]] = {
    "G1_G2_exact_scoped_calculations_complete": _c_g1_g2,
    "full_candidate_exactly_stationary": _c_stationary,
    "full_homogeneous_quartic_BFB_exact": _c_bfb,
    "target_unbroken_algebra_is_standard_model": _c_sm_algebra,
    "target_symmetry_orbit_ranks_36_37_38_exact": _c_orbit_ranks,
    "couplings_perturbative": _c_couplings,
    "full_Hessian_rank_448_nullity_38_exact": _c_rank_nullity,
    "full_448_quotient_strictly_positive_exact": _c_quotient_positive,
    "full_fixed_F_offkernel_gap_and_equality_exact": _C_FIXED_F,
    "max_negative_all_zero_residual_route_excluded_exactly": _C_MAX_NEG_ZERO,
    "max_negative_pure_Delta_full_residual_gap_excluded_exactly": _C_MAX_NEG_FULL,
    "rank1_SU3_four_dimensional_slice_gap_certified_without_closing_G3": _C_RANK1_SU3,
    "rank1_SU4_representation_infrastructure_ready_without_closing_G3": _C_RANK1_SU4,
    "signed_Phi_orbits_locally_isolated_exactly": _C_SIGNED_PHI,
    "complete_SU3_fixed_Phi_slice_classified_exactly": _C_SU3_SLICE,
    "all_PD_equality_orbits_classified_exactly": _c_equality_set,
    "beta_global_gap_and_unique_equality_exact": _c_global_gap,
}
RELEASE_SPECS: dict[str, Callable[..., dict[str, Any]]] = {
    "authoritative_external_model_contract_executed": _c_release_contract,
    "G1_promoted_closed": _c_release_gate("G1"),
    "G2_promoted_closed": _c_release_gate("G2"),
}
HESSIAN_CRITERIA = ("full_Hessian_rank_448_nullity_38_exact", "full_448_quotient_strictly_positive_exact")
ROUTE_SPECIFIC_CRITERIA = (
    "full_fixed_F_offkernel_gap_and_equality_exact",
    "max_negative_all_zero_residual_route_excluded_exactly",
    "max_negative_pure_Delta_full_residual_gap_excluded_exactly",
    "rank1_SU3_four_dimensional_slice_gap_certified_without_closing_G3",
    "rank1_SU4_representation_infrastructure_ready_without_closing_G3",
    "signed_Phi_orbits_locally_isolated_exactly",
    "complete_SU3_fixed_Phi_slice_classified_exactly",
)


# ----------------------------------------------------------------------------
# The SM track witness family O06 = 2|kappa| r0 + eps, eps > 0 (V_eps = V + eps N_H).
# ----------------------------------------------------------------------------

EPS_SHARED_NOTE = (
    "eps member: V_eps = V + eps N_H differs from the benchmark only in the O06 coefficient (exact, eps_family L1); "
    "the vacuum q0 = (p, 0, r0 sigma_std, r0, x0), the group G and the contract are unchanged, so the benchmark "
    "evidence below applies verbatim"
)


def _eps_hessian_check(ev: _Evidence, name: str) -> None:
    ev.eq("exact_hessian", ("eps_family", "checks", name), True)


def _eps_wrap(
    base: Callable[[_Evidence, Mapping[str, Any], Mapping[str, Any]], dict[str, Any]],
    analogue: str,
    statement: str,
    why_exact: str,
    *,
    vacuum: bool = True,
    extra: Callable[[_Evidence, Mapping[str, Any], Mapping[str, Any]], None] | None = None,
) -> Callable[[_Evidence, Mapping[str, Any], Mapping[str, Any]], dict[str, Any]]:
    """The benchmark criterion plus the eps-family evidence that carries it to V_eps (fail closed on both)."""

    def build(ev: _Evidence, d: Mapping[str, Any], ctx: Mapping[str, Any]) -> dict[str, Any]:
        info = dict(base(ev, d, ctx))
        ev.require("sm_exact_hessian_report_executes", "sm_exact_hessian_eps_family_executes")
        _eps_hessian_check(ev, "L1_V_eps_differs_from_V_only_in_O06_by_eps")
        if vacuum:
            # q0 is the vacuum of V_eps, with the same equality set (L1).
            ev.eq("exact_hessian", ("flags", "eps_family_equality_set_unchanged"), True)
        if extra is not None:
            extra(ev, d, ctx)
        info.update(
            {
                "analogue": analogue,
                "statement": statement,
                "why_exact": why_exact,
                "notes": [EPS_SHARED_NOTE, *info.get("notes", [])],
            }
        )
        return info

    return build


def _eps_stationary_extra(ev: _Evidence, d: Mapping[str, Any], ctx: Mapping[str, Any]) -> None:
    _eps_hessian_check(ev, "L1_grad_V_eps_vanishes_at_q0_for_every_eps")
    ev.eq("exact_hessian", ("exact_certificate_raised_O06", "gradient_exactly_zero"), True)


def _eps_bfb_extra(ev: _Evidence, d: Mapping[str, Any], ctx: Mapping[str, Any]) -> None:
    _eps_hessian_check(ev, "L1_N_H_homogeneous_quadratic_so_quartic_part_unchanged")


def _eps_equality_extra(ev: _Evidence, d: Mapping[str, Any], ctx: Mapping[str, Any]) -> None:
    for name in ("L1_equality_report_proved_status_and_premises", "L1_N_H_is_sum_of_squares_of_u_H",
                 "L1_N_H_invariant_under_G", "L1_operator_dictionary_maps_O06_to_N_H",
                 "L1_O06_compiler_direction_is_unit_Hdag_i_H_i_without_dressing"):
        _eps_hessian_check(ev, name)
    ev.eq("exact_hessian", ("eps_family", "L1_equality_set", "relies_on", "required_status"), EQUALITY_STATUS)


def _c_eps_couplings(ev: _Evidence, d: Mapping[str, Any], ctx: Mapping[str, Any]) -> dict[str, Any]:
    ev.require("sm_candidate_report_executes", "sm_exact_hessian_report_executes", "sm_exact_hessian_eps_family_executes")
    ev.eq("candidate", ("candidate", "nonzero_count"), 27)
    ev.eq("candidate", ("candidate", "all_parameters_in_exact_X_contract"), True)
    ev.eq("candidate", ("candidate", "maximum_absolute_coefficient"), "73/8")
    _eps_hessian_check(ev, "L1_V_eps_differs_from_V_only_in_O06_by_eps")
    base = d.get("eps_family_O06_base")
    others = d.get("other_26_couplings_max_abs")
    upper = d.get("eps_perturbative_upper")
    raised, raised_eps = d.get("O06_raised"), d.get("eps_raised")
    tiny, tiny_eps = d.get("O06_tiny"), d.get("eps_tiny")
    count = d.get("coefficients_nonzero_count")
    ev.computed("eps_member_keeps_27_nonzero_couplings", count == 27 and base is not None and base > 0,
                [count, str(base) if base is not None else None], "27 nonzero; O06_eps = 2|kappa| r0 + eps > 0")
    ev.computed("other_26_couplings_below_12", others is not None and others == Fraction(73, 8) and others < PERTURBATIVE_BOUND,
                str(others) if others is not None else None, "max |c| over the other 26 == 73/8 < 12 (unchanged)")
    ev.computed("perturbative_eps_window_is_0_to_12_minus_O06_base", upper is not None and base is not None and upper > 0
                and base + upper == PERTURBATIVE_BOUND, str(upper) if upper is not None else None,
                "0 < eps < 12 - 2|kappa| r0 (= 599/50): O06_eps < 12 < 4 pi")
    ev.computed("raised_O06_coupling_perturbative",
                raised is not None and raised_eps is not None and upper is not None and 0 < raised_eps < upper
                and raised < PERTURBATIVE_BOUND and raised_eps == d.get("r0") ** 2 / 100,
                [str(raised), str(raised_eps)], "O06 = 51/2500 < 12, eps = r0^2/100 inside the window")
    ev.computed("tiny_eps_coupling_perturbative",
                tiny is not None and tiny_eps is not None and upper is not None and base is not None and 0 < tiny_eps < upper
                and tiny == base + tiny_eps and tiny < PERTURBATIVE_BOUND,
                [str(tiny), str(tiny_eps)], "O06 = 1/50 + r0^2/10^6 < 12, inside the window")
    ev.eq("candidate", ("candidate", "float_map_inside_4pi_box"), True, grade="float64")
    return {
        "analogue": "eps_member_couplings_perturbative_exact",
        "statement": "Exactly 27 nonzero real couplings in the exact-X contract: the benchmark's 26 unchanged (max |c| = "
        "73/8) and O06 = 2|kappa| r0 + eps; all < 12 < 4 pi for 0 < eps < 12 - 2|kappa| r0 = 599/50, e.g. the raised "
        "member O06 = 51/2500 and the tiny member O06 = 1/50 + r0^2/10^6.",
        "why_exact": "Exact rational comparisons (pi > 3); only O06 moves with eps (eps_family L1 coefficient shift).",
    }


def _eps_hessian_evidence(ev: _Evidence, d: Mapping[str, Any], ctx: Mapping[str, Any]) -> tuple[int | None, int | None]:
    ev.require("sm_exact_hessian_report_executes", "sm_exact_hessian_eps_family_executes",
               "sm_equality_set_report_executes", "sm_candidate_equality_set_hessian_cross_bound")
    orbit = _orbit_rank(ctx)
    expected_rank = TOTAL_DIM - orbit if orbit is not None else None
    ev.computed("orbit_rank_recorded_by_equality_module", orbit == 35, orbit,
                "equality_set P3 tangent_rank.rank_so10_plus_X_plus_PQ == 35")
    for name in ("source_binding_exact", "proof_grade", "exact_PSD", "eps_family_theorem_claimed"):
        ev.eq("exact_hessian", ("flags", name), True)
    # L2's premises, read one by one: H_0 PSD with kernel T35 + D4, Hess_u N_H = 2 P_H, D4 in the H block, T35 zero
    # there, rank 39, and the kernel intersection of dimension 35.
    for name in ("L2_H0_PSD_exact", "L2_H0_kernel_is_span_T35_plus_D4", "L2_hess_u_N_H_is_2_P_H_hence_PSD_with_kernel_H_equal_0",
                 "L2_D4_inside_H_block", "L2_T35_vanishes_on_H_block", "L2_rank_T35_35_rank_D4_4_rank_T35_plus_D4_39",
                 "L2_hess_N_H_annihilates_T35_and_doubles_D4", "L2_dim_ker_H0_cap_ker_hess_N_H_equals_35"):
        _eps_hessian_check(ev, name)
    ev.eq("exact_hessian", ("exact_certificate", "exact_PSD"), True)
    ev.check("exact_hessian", ("eps_family", "L2_hessian", "dim_ker_H0_cap_ker_B"), f"== orbit rank = {orbit}",
             lambda v: orbit is not None and _strict_eq(v, orbit))
    every = ("eps_family", "L2_hessian", "for_every_eps_positive")
    ev.eq("exact_hessian", every + ("PSD",), True)
    ev.check("exact_hessian", every + ("rank",), f"== 486 - orbit rank = {expected_rank}",
             lambda v: expected_rank is not None and _strict_eq(v, expected_rank))
    ev.check("exact_hessian", every + ("nullity",), f"== orbit rank = {orbit}",
             lambda v: orbit is not None and _strict_eq(v, orbit))
    ev.eq("exact_hessian", every + ("kernel",), EPS_KERNEL_TEXT)
    triple = f"{expected_rank}/{orbit}/0" if orbit is not None else None
    for variant in ("raised_O06", "tiny_eps"):
        row = ("eps_family", "consistency_certificates", variant)
        ev.check("exact_hessian", row + ("inertia_positive_zero_negative",), f"== {triple!r} (consistency)",
                 lambda v: triple is not None and v == triple)
        ev.eq("exact_hessian", row + ("kernel_equals_symmetry_tangents",), True)
    ev.eq("exact_hessian", ("live_binding_raised_O06", "numerical_inertia", "zero_at_1e_minus_10"), 35, grade="float64")
    ev.eq("candidate", ("compiler", "1/5", "all_massive_variant", "n_zero"), 0, grade="float64")
    ev.eq("candidate", ("compiler", "1/5", "all_massive_variant", "n_negative"), 0, grade="float64")
    return orbit, expected_rank


def _c_eps_rank_nullity(ev: _Evidence, d: Mapping[str, Any], ctx: Mapping[str, Any]) -> dict[str, Any]:
    orbit, expected_rank = _eps_hessian_evidence(ev, d, ctx)
    ev.eq("exact_hessian", ("flags", "eps_family_kernel_equals_symmetry_orbit"), True)
    return {
        "analogue": "eps_member_full_Hessian_rank_451_nullity_35_exact",
        "statement": "Literal analogue on the eps member: for every eps > 0 the complete 486 x 486 Hessian of V_eps at "
        f"q0 has rank 486 - orbit rank = {expected_rank} and nullity = orbit rank = {orbit} (L2).",
        "why_exact": "Exact: Hess V_eps(q0) = H_0 + eps Hess N_H with both PSD, so its kernel is ker H_0 cap ker "
        "Hess N_H = span(T35) (H_0 PSD with kernel T35 + D4, Hess_u N_H = 2 P_H, D4 inside the H block, T35 zero "
        "there, rank 39; all exact over Q); inertia 451/35/0 re-certified by exact LDL at eps = r0^2/100 and "
        "r0^2/10^6.",
        "why_failed": "Exact evidence refutes the eps-family rank/nullity claim (see false exact evidence).",
    }


def _c_eps_quotient_positive(ev: _Evidence, d: Mapping[str, Any], ctx: Mapping[str, Any]) -> dict[str, Any]:
    orbit, expected_rank = _eps_hessian_evidence(ev, d, ctx)
    ev.eq("exact_hessian", ("flags", "eps_family_strictly_positive_on_symmetry_quotient_for_all_eps_positive"), True)
    ev.check("exact_hessian", ("eps_family", "L2_hessian", "for_every_eps_positive",
                               "strictly_positive_on_symmetry_quotient_dimension"),
             f"== 486 - orbit rank = {expected_rank}", lambda v: expected_rank is not None and _strict_eq(v, expected_rank))
    for variant in ("raised_O06", "tiny_eps"):
        ev.eq("exact_hessian", ("eps_family", "consistency_certificates", variant,
                                "strictly_positive_on_symmetry_quotient"), True)
    return {
        "analogue": "eps_member_full_451_quotient_strictly_positive_exact",
        "statement": "Literal analogue on the eps member: for every eps > 0 the Hessian of V_eps at q0 is PSD, its "
        "kernel is exactly the 35-dimensional G-orbit tangent space, and it is strictly positive on the "
        f"{expected_rank}-dimensional quotient by it (L2).",
        "why_exact": "Exact: a PSD matrix whose kernel is exactly the orbit tangent space is strictly positive on the "
        "quotient; L2 gives PSD and kernel = span(T35) for every eps > 0 (the tuned eps = 0 limit, 447/39, is not).",
        "why_failed": "Exact evidence refutes the eps-family quotient positivity (see false exact evidence).",
    }


EPS_SCIENCE_SPECS: dict[str, Callable[..., dict[str, Any]]] = {
    "G1_G2_exact_scoped_calculations_complete": _eps_wrap(
        _c_g1_g2,
        "eps_member_shared_G1_G2_exact_scoped_calculations_complete",
        "The G1 census and G2 derivative audit are COMPLETE on the authoritative contract, and the eps member is the "
        "27-parameter benchmark with only O06 changed, so it lies in the same declared 51-parameter potential.",
        "Shared prerequisite: ledger G1/G2 COMPLETE, and V_eps differs from V only in the O06 coefficient (exact).",
        vacuum=False,
    ),
    "full_candidate_exactly_stationary": _eps_wrap(
        _c_stationary,
        "eps_member_exactly_stationary",
        "grad V_eps(q0) = grad V(q0) + eps grad N_H(q0) = 0 exactly for every eps >= 0 (H = 0 at q0); q0 is also a "
        "global minimiser of V_eps (L1).",
        "Exact: the benchmark gradient vanishes exactly, grad N_H vanishes at H = 0, and V_eps >= V0 = V_eps(q0).",
        extra=_eps_stationary_extra,
    ),
    "full_homogeneous_quartic_BFB_exact": _eps_wrap(
        _c_bfb,
        "eps_member_full_homogeneous_quartic_BFB_exact",
        "N_H is quadratic, so the quartic part of V_eps is that of V_PS: V_eps4(q) = V4(q) >= |q|^4/167 on the full "
        "486-real chart for every eps.",
        "Exact: the benchmark's source-bound bound V4 >= |q|^4/167 and N_H homogeneous of degree 2 (sympy, census "
        "counts (H, Hbar) = (1, 1)).",
        vacuum=False,
        extra=_eps_bfb_extra,
    ),
    "target_unbroken_algebra_is_standard_model": _eps_wrap(
        _c_sm_algebra,
        "eps_member_target_unbroken_algebra_is_standard_model_exact",
        "The vacuum of V_eps is the same q0 (L1), whose unbroken algebra inside so(10) + u(1)_X is exactly su(3)_c + "
        "su(2)_L + u(1)_Y in the standard embedding.",
        "Exact integer stabilizer computation at q0 (unchanged), confirmed by the sigma-hypercharge audit.",
    ),
    "target_symmetry_orbit_ranks_36_37_38_exact": _eps_wrap(
        _c_orbit_ranks,
        "eps_member_symmetry_orbit_ranks_33_34_35_exact",
        "Same vacuum and same G: exact orbit tangent ranks 33 / 34 / 35 at q0, transverse quotient 486 - 35 = 451.",
        "Exact integer ranks from the equality module (P3), independent of the O06 coefficient.",
    ),
    "couplings_perturbative": _c_eps_couplings,
    "full_Hessian_rank_448_nullity_38_exact": _c_eps_rank_nullity,
    "full_448_quotient_strictly_positive_exact": _c_eps_quotient_positive,
    "full_fixed_F_offkernel_gap_and_equality_exact": _C_FIXED_F,
    "max_negative_all_zero_residual_route_excluded_exactly": _C_MAX_NEG_ZERO,
    "max_negative_pure_Delta_full_residual_gap_excluded_exactly": _C_MAX_NEG_FULL,
    "rank1_SU3_four_dimensional_slice_gap_certified_without_closing_G3": _C_RANK1_SU3,
    "rank1_SU4_representation_infrastructure_ready_without_closing_G3": _C_RANK1_SU4,
    "signed_Phi_orbits_locally_isolated_exactly": _C_SIGNED_PHI,
    "complete_SU3_fixed_Phi_slice_classified_exactly": _C_SU3_SLICE,
    "all_PD_equality_orbits_classified_exactly": _eps_wrap(
        _c_equality_set,
        "eps_member_equality_set_single_G_orbit_exact",
        "{V_eps = V0} = {V = V0} = G.q0 for every eps >= 0 (L1: V_eps = V + eps N_H >= V >= V0, N_H = |u_H|^2 = 0 iff "
        "H = 0, and H = 0 on {V = V0}); one orbit of G = SO(10) x U(1)_X x U(1)_PQ, no other equality orbits.",
        "Exact given the equality-set theorem for V (P0-P3; 6 cited classical theorems and 6 hand-argued steps, "
        "pinned verbatim here), plus one exact step (L1) recorded by the exact Hessian report; counting it as exact "
        "presumes decision D6 (adopted), as for the benchmark.",
        extra=_eps_equality_extra,
    ),
    "beta_global_gap_and_unique_equality_exact": _eps_wrap(
        _c_global_gap,
        "eps_member_global_gap_and_unique_equality_exact",
        SM_EPS_FINAL_THEOREM + "  (V_PS,eps = V_PS + eps N_H, eps > 0; V_PS,eps(q0) = V0 = -20661/20000.)",
        "Exact up to the same pinned hand-argued steps and cited theorems as the benchmark (decision D6): V_PS >= V0 "
        "with {V_PS = V0} = G.q0, and L1 carries both to V_PS,eps exactly (N_H >= 0, zero exactly at H = 0).",
        extra=_eps_equality_extra,
    ),
}


def _evaluate(name: str, kind: str, ctx: Mapping[str, Any],
              specs: Mapping[str, Callable[..., dict[str, Any]]] | None = None) -> dict[str, Any]:
    if specs is None:
        specs = SCIENCE_SPECS if kind == "science" else RELEASE_SPECS
    gate_values = _dig(_final_gate_criteria_view(ctx["reports"].get("final_gate") or {}), f"{kind}_criteria",
                       default={})
    chiral_value = gate_values.get(name) if isinstance(gate_values, Mapping) else None
    record: dict[str, Any] = {
        "final_gate_criterion": name,
        "kind": kind,
        "present_in_final_gate_report": isinstance(gate_values, Mapping) and name in gate_values,
        "chiral_H_track_value": chiral_value,
    }
    spec = specs.get(name)
    if spec is None:
        record.update(
            {
                "route_specific": False,
                "pati_salam_analogue": {"name": None, "statement": "no analogue is defined for this criterion",
                                        "grade": "n/a"},
                "evidence_exact": [],
                "evidence_float64": [],
                "value": False,
                "classification": FAILED,
                "justification": "Fail closed: the final gate reports a criterion this readiness map does not know.",
            }
        )
        return record

    ev = _Evidence(ctx["reports"], ctx["integrity"])
    info = spec(ev, ctx["derived"], ctx)
    route_specific = bool(info.get("route_specific"))
    exact_ok = bool(ev.exact) and all(item["ok"] for item in ev.exact)
    float_ok = bool(ev.float64) and all(item["ok"] for item in ev.float64)
    failed_preconditions = [p for p in ev.preconditions if ctx["integrity"].get(p) is not True]
    failing_keys = [f"{item['artifact']}:{item['key']}" for item in ev.exact if not item["ok"]]
    refuting = ev.refuting_exact_items()
    refuting_keys = [f"{item['artifact']}:{item['key']}" for item in refuting]

    if route_specific:
        classification = ROUTE_SPECIFIC
        value = exact_ok
        justification = (
            f"Proof route used only for the chiral-H SU(5)+Delta candidate. {info['statement']} "
            f"PS counterpart: {info['pati_salam_counterpart']} ({'holds' if exact_ok else 'NOT confirmed'})."
        )
        grade = "n/a (route-specific)"
    else:
        value = exact_ok
        grade = "exact"
        if exact_ok:
            classification = SATISFIED_EXACT
            grade = info.get("exact_grade", "exact")
            justification = info["why_exact"]
        elif refuting:
            # Loaded, executing exact evidence contradicts the claim: FAILED, whatever the float64 evidence says.
            classification = FAILED
            justification = (
                (info.get("why_failed") or "Exact evidence refutes the claim.")
                + f" [false exact evidence: {', '.join(refuting_keys)}]"
            )
        elif float_ok:
            # Only possible when every false exact item is a missing/non-executing input.
            classification = SATISFIED_FLOAT_ONLY
            grade = "float64"
            justification = (
                "Exact evidence unavailable (required artifact(s) missing or not executing: "
                f"{', '.join(failed_preconditions) or ', '.join(failing_keys)}); only float64 evidence holds."
            )
        else:
            classification = FAILED
            justification = (
                "Fail closed: required artifact(s) missing or not executing: "
                f"{', '.join(failed_preconditions) or ', '.join(failing_keys)}."
            )
    record.update(
        {
            "route_specific": route_specific,
            "pati_salam_analogue": {"name": info["analogue"], "statement": info["statement"], "grade": grade},
            "evidence_exact": ev.exact,
            "evidence_float64": ev.float64,
            "value": value,
            "classification": classification,
            "justification": justification,
        }
    )
    if route_specific:
        record["pati_salam_counterpart"] = info["pati_salam_counterpart"]
    for extra in ("conditional_on_decisions", "literal_conjuncts_not_evaluated", "notes", "alternative_analogues"):
        if extra in info:
            record[extra] = info[extra]
    if failed_preconditions:
        record["failed_preconditions"] = failed_preconditions
    return record


# ----------------------------------------------------------------------------
# Proposed additional criteria, caveats, planner summary, integration gaps.
# ----------------------------------------------------------------------------


def _g5_vector_comparison(reports: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    """G5's BFB binding (decision D4: ledger gates.G5.bfb_coupling_vector) against the PS coupling vector.

    covers_closing_coupling_vector is True only if the ledger's G5 binding is certified and its coefficients equal
    the candidate's exact_nonzero_coefficients.  The comparison with the historical 27-parameter SOS vector, which
    no longer carries G5, is kept under historical_vector_comparison.
    """
    binding = _dig(reports.get("ledger") or {}, "gates", "G5", "bfb_coupling_vector")
    ps = _dig(reports.get("candidate") or {}, "candidate", "exact_nonzero_coefficients")
    bound = _dig(binding, "coefficients")
    certified = _dig(binding, "certified") is True
    same_vector = bool(isinstance(ps, Mapping) and ps and isinstance(bound, Mapping) and dict(bound) == dict(ps))
    covers = bool(certified and same_vector)
    if not isinstance(binding, Mapping):
        why = "the ledger's G5 row has no bfb_coupling_vector binding (fail closed)"
    elif not certified:
        why = "the ledger's G5 binding is not certified"
    elif not same_vector:
        why = "the ledger's G5 binding coefficients differ from the PS coupling vector"
    else:
        why = "G5 is bound to the PS coupling vector with a certified exact BFB bound (decision D4)"
    return {
        "evaluated": isinstance(binding, Mapping),
        "G5_vector_source": "ledger gates.G5.bfb_coupling_vector (g3_sm_target_track_v20 g5_bfb_binding; decision D4)",
        "binding_source": _dig(binding, "source"),
        "binding_certified": certified,
        "binding_covers_eps_witness_family": _dig(binding, "covers_eps_witness_family") is True,
        "binding_coefficients_equal_PS_vector": same_vector,
        "covers_closing_coupling_vector": covers,
        "why": why,
        "historical_vector_comparison": _historical_g5_vector_comparison(reports),
    }


def _historical_g5_vector_comparison(reports: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    """The historical 27-parameter SOS vector (the pre-D4 G5 evidence) against the PS vector."""
    g5 = _dig(reports.get("ledger") or {}, "model_contract_reports", "gauged_G3_SOS_candidate", "coefficient_vector",
              "symbolic_nonzero")
    ps = _dig(reports.get("candidate") or {}, "candidate", "exact_nonzero_coefficients")
    if not isinstance(g5, Mapping) or not g5 or not isinstance(ps, Mapping) or not ps:
        return {"evaluated": False, "covers_closing_coupling_vector": False,
                "reason": "G5 or PS coupling vector missing (fail closed)"}
    constant_mismatch = {}
    symbolic = {}
    for name in sorted(set(g5) | set(ps)):
        g5_value, ps_value = g5.get(name), ps.get(name)
        g5_frac, ps_frac = _frac(g5_value), _frac(ps_value)
        if g5_frac is not None and ps_frac is not None:
            if g5_frac != ps_frac:
                constant_mismatch[name] = {"G5_vector": g5_value, "PS_vector": ps_value}
        elif g5_value != ps_value:
            symbolic[name] = {"G5_vector": g5_value, "PS_vector": ps_value}
    same_names = set(g5) == set(ps)
    if not same_names:
        why = "the parameter sets differ"
    elif constant_mismatch:
        why = "constant (r, h, x-independent) entries differ, so no choice of r, h, x makes the vectors equal"
    elif symbolic:
        why = "symbolic entries are not compared here (fail closed)"
    else:
        why = "every entry agrees"
    return {
        "evaluated": True,
        "G5_vector_source": "ledger model_contract_reports.gauged_G3_SOS_candidate.coefficient_vector.symbolic_nonzero "
        "(symbolic in r, h, x)",
        "same_parameter_names": same_names,
        "constant_entries_that_differ": constant_mismatch,
        "symbolic_entries_not_compared": symbolic,
        "covers_closing_coupling_vector": bool(same_names and not constant_mismatch and not symbolic),
        "why": why,
    }


def _proposed_criteria(reports: Mapping[str, Mapping[str, Any]], science: Sequence[Mapping[str, Any]],
                       g5: Mapping[str, Any]) -> dict[str, Any]:
    quotient = next((c for c in science if c["final_gate_criterion"] == "full_448_quotient_strictly_positive_exact"), {})
    alternatives = quotient.get("alternative_analogues", {})
    fg = reports.get("final_gate") or {}
    ledger_g3 = _dig(reports.get("ledger") or {}, "gates", "G3", "status")
    gate_closed = _dig(fg, "classification", "G3_closed")
    return {
        "note": "The retargeting planner's proposed SM-track criteria that the chiral-H criteria map does not "
        "contain; recorded for readiness only, not part of the booleans below.  The adopted SM track "
        "(g3_sm_target_track_v20) uses S12 as a control and the final gate carries the last two as release "
        "criteria; S11 was not adopted (decision D2 takes the eps > 0 member as the witness).  (Planner item S9, "
        "the required_statement string binding, is not listed here: it is a conjunct of the chiral-H criterion "
        "beta_global_gap_and_unique_equality_exact, recorded there under literal_conjuncts_not_evaluated and under "
        "integration_gaps.)",
        "S11_sm_Hessian_kernel_is_35_symmetry_plus_4_light_doublet_exact": {
            "statement": "replaces full_Hessian_rank_448_nullity_38_exact and full_448_quotient_strictly_positive_"
            "exact (see the quotient criterion's alternative_analogues)",
            "value": _dig(alternatives, "S11_kernel_is_orbit_plus_tuned_light_doublet_exact", "value") is True,
        },
        "S12_sm_O06_raised_control_rank_451_nullity_35_exact": {
            "value": _dig(alternatives, "S12_O06_raised_member_rank_451_nullity_35_exact", "value") is True,
        },
        "ledger_G3_status_matches_gate_closure": {
            "statement": "ledger G3 CLOSED <=> final gate release_G3_verified",
            "value": isinstance(gate_closed, bool) and isinstance(ledger_g3, str)
            and ((ledger_g3 == "CLOSED") == gate_closed),
            "actual": {"ledger_G3_status": ledger_g3, "final_gate_G3_closed": gate_closed},
        },
        "G5_BFB_evidence_covers_closing_coupling_vector": {
            "statement": "G5's closed BFB evidence is on the same coupling vector as the G3 witness",
            "value": g5.get("covers_closing_coupling_vector") is True,
            "comparison": g5,
            "resolution": "decision D4 (adopted): G5 is rebound to the PS vector, which has its own exact BFB "
            "certificate V4 >= |q|^4/167 covering the eps witness family (eps N_H is quadratic)",
        },
    }


# (id, caveat, assigned gate, also affects, basis, effect on G3, evidence artifact, evidence key)
CAVEAT_SPECS: tuple[tuple[str, str, str, tuple[str, ...], str, str, str, tuple[str, ...]], ...] = (
    (
        "uniqueness_uses_accidental_U1_PQ",
        "The minimum is unique modulo G = SO(10) x U(1)_X x U(1)_PQ; modulo SO(10) x U(1)_X alone {V = V0} is a "
        "circle of orbits (the axion direction, Phi17^4 conj(S)^17).",
        "G3", ("G4",),
        "the final gate's decisive theorems (both tracks) already quotient by PQ; g3_sm_target_track_v20 "
        "disclosure 1; ledger G4: 'the axion/PQ direction'",
        "disclosure in the closure scope; no blocker (same G as FINAL_THEOREM)",
        "equality_set", ("flags", "unique_modulo_SO10_x_U1X_alone"),
    ),
    (
        "tuned_light_doublet_hessian_zero_modes",
        "At the tuned benchmark the exact Hessian kernel is the 35 orbit tangents plus 4 real light-doublet "
        "directions (Re H_6..9): the symmetry quotient is not strictly positive.",
        "G3", ("G4", "G6"),
        "final gate criteria full_Hessian_rank_448_nullity_38_exact (exact_rank_448, exact_nullity_38) and "
        "full_448_quotient_strictly_positive_exact (exact_PSD, strict_quotient_positive, kernel_equals_38_symmetry_"
        "tangents); ledger G4: 'classify all remaining Hessian zero and negative modes'",
        "fails both Hessian criteria under the literal contract (451/35, kernel = orbit) at the tuned benchmark; "
        "resolved by decision D2 (adopted): the G3 witness is the eps > 0 member O06 = 2|kappa| r0 + eps, on which "
        "both hold exactly; the eps -> 0 tuned doublet is a G4 classification item",
        "exact_hessian", ("flags", "kernel_equals_35_symmetry_tangents_plus_4_light_doublet"),
    ),
    (
        "exact_hessian_certified_at_one_benchmark_only",
        "The exact Hessian is certified at r0 = 1/5, x0 = 1, kappa = -r0/4 only (with the O06 + eps family through "
        "that point); the global theorem holds for every r0 > 0, x0 > 0, kappa^2 < 8 r0^2.",
        "G3", (),
        "g3_sm_target_track_v20 disclosure 3 (adopted closure-scope disclosure)",
        "disclosure in the closure scope (the G3 witness is the eps member at the r0 = 1/5 benchmark)",
        "exact_hessian", ("flags", "other_r0_x0_kappa_certified"),
    ),
    (
        "compiler_equals_SOS_end_to_end_float64_only",
        "V_PS is the adapted SOS form; it equals the compiler potential exactly per coefficient and per "
        "source-bound operator, and only in float64 end to end.",
        "G3", (),
        "same binding status as the accepted chiral-H exact Hessian (source-bound exact entries, float64 "
        "compiler cross-check)",
        "disclosure; float evidence stays diagnostic",
        "equality_set", ("scope", "float64_evidence_only"),
    ),
    (
        "cited_theorems_and_elementary_steps_not_machine_checked",
        "The equality-set proof cites 6 classical theorems (Pluecker, Kostant-Lichtenstein, Iwasawa, Wirtinger, "
        "U(n) transitivity, highest weight/Weyl) and 6 elementary steps that are not machine-checked.",
        "G3", (),
        "decision D6 (adopted): cited classical theorems and hand-argued steps are accepted as G3-grade inputs, "
        "pinned by an allowlist (g3_sm_target_track_v20) and disclosed; outside the Pati-Salam program no "
        "repository artifact relies on such inputs",
        "the equality-set and global-gap criteria count as exact under D6 (adopted); pinned allowlist here and in "
        "g3_sm_target_track_v20; disclosure in README and manuscript",
        "equality_set", ("scope", "cited_not_machine_checked"),
    ),
    (
        "benchmark_family_only",
        "Potentials outside the candidate's 27-parameter family are not covered by the global theorem, except the "
        "O06 + eps members (the O06-raised member among them), which the exact Hessian report's eps_family L1 "
        "covers given that theorem.",
        "G3", (),
        "closure scope (g3_sm_target_track_v20.CLOSURE_SCOPE, adopted): 'the exact SM-preserving global vacuum of "
        "the declared exact-X potential's 27-parameter benchmark with the light-doublet deformation eps > 0'",
        "disclosure in the closure scope (g3_sm_target_track_v20 disclosure 7)",
        "equality_set", ("scope", "not_proved_or_out_of_scope"),
    ),
    (
        "symmetry_ranks_differ_from_G4_spec",
        "The superseded p+delta point's rank-37/38 (449/448) quotients do not transfer: at the PS vacuum the ranks "
        "are 34 (gauge + X; 452 including the axion) and 35 (451), which the ledger's G4 spec now names.",
        "G4", (),
        "ledger G4: 'carry the exact gauge quotient to the accepted G3 witness (the SM Pati-Salam eps member) and "
        "recompute its ranks there'",
        "none (routed to G4 by decision D5)",
        "ledger", ("gates", "G4", "open_scope"),
    ),
    (
        "G5_certified_on_a_different_coupling_vector",
        "G5 was CLOSED on the historical 27-parameter SOS vector, which differs from the PS vector (O27_B03/B04 "
        "swapped; O05, O06 and re::O12 differ at h = 0); decision D4 rebinds G5 to the PS vector so that G3, G5 and "
        "G6 refer to one vector.",
        "G5", (),
        "ledger G5 closed scope (g3_sm_target_track_v20.G5_LEDGER_CLOSED_SCOPE; decision D4, adopted)",
        "none (G5 rebound under D4)",
        "ledger", ("gates", "G5", "authoritative_closed_scope"),
    ),
    (
        "coloured_126bar_remnants_below_M_I",
        "126bar (10bar,1,3) remnants (6,1)_4/3, (3,1)_1/3, (3,1)_4/3, (6,1)_1/3, (6,1)_2/3 lie below M_I; only the "
        "10_H triplets sit at M_GUT.",
        "G6", ("G8",),
        "ledger G6: 'emit the complete positive spectrum'",
        "none",
        "candidate", ("flags", "coloured_scalars_only_at_M_GUT"),
    ),
    (
        "no_electroweak_symmetry_breaking",
        "H = 0 at the vacuum: no EWSB.  At the tuned benchmark one doublet is massless at tree level, so the "
        "spectrum is not positive; on the eps > 0 member it is light but massive (mass^2 eps M_GUT^2), still "
        "without EWSB.",
        "G6", ("G4",),
        "ledger G6: 'emit the complete positive spectrum'",
        "none (the 4 zero modes are G4/G6 classification items)",
        "candidate", ("flags", "electroweak_symmetry_breaking_realized"),
    ),
    (
        "phi17_not_at_canonical_scale",
        "x0 = 1 at every benchmark (canonical x0 ~ 10.08); the GeV masses are illustrative.",
        "G6", ("G7",),
        "roadmap W4-G6 acceptance: 'all eigenmasses, irreps, mixings, and uncertainties are complete'",
        "none",
        "candidate", ("flags", "physical_benchmark_uses_canonical_phi17_scale"),
    ),
    (
        "rg_anchor_field_content_not_reproduced",
        "The anchor's betas assume a light (15,2,2) above M_I and a 2HDM below; the candidate has neither and "
        "re-solving moves M_I and M_GUT.",
        "G7", (),
        "ledger G7: 'Validated two-loop RGE and threshold matching'",
        "none (the G3 theorem holds for every r0 > 0, so it does not depend on the anchor)",
        "candidate", ("flags", "rg_anchor_field_content_reproduced"),
    ),
    (
        "higgs_quartic_too_large_at_benchmark",
        "Tree-level lambda_eff = 127/64 (m_h ~ 195 GeV); tree-level minimality forbids the slightly negative "
        "lambda(M_I) the SM running prefers.",
        "G7", ("G6",),
        "ledger G7: 'Validated two-loop RGE and threshold matching'",
        "none (a potential future G6/G7 FAIL, not a G3 issue)",
        "candidate", ("flags", "higgs_mass_compatible"),
    ),
    (
        "tan_beta_one_light_doublet",
        "The light doublet is an equal 5/5bar mixture (tan beta = 1): with 10_H-only Yukawas m_t = m_b at matching.",
        "G8", ("G7",),
        "decision D5 (adopted): Yukawas go to G8 (g3_sm_target_track_v20 routes tan_beta_one_light_doublet to G8, "
        "also affecting G7)",
        "none",
        "candidate", ("checks", "light_doublet_is_equal_5_5bar_mixture"),
    ),
    (
        "no_realistic_yukawa_sector",
        "The H-linear portals O15, O38, O45, O28 vanish: no realistic Yukawa sector.",
        "G8", ("theory_validation_matrix flavour gate",),
        "roadmap W6-G8 acceptance: 'one authoritative vacuum fixes all Wilson, running, phase, and uncertainty "
        "inputs'",
        "none",
        "candidate", ("flags", "realistic_yukawa_sector"),
    ),
    (
        "proton_decay_mediators_below_M_I",
        "(3,1)_1/3 at ~0.24 M_I carries proton-decay mediator quantum numbers and couples to 16.16 through the "
        "126bar Yukawa.",
        "G8", ("G6",),
        "ledger G8: 'Proton-decay prediction and falsification'",
        "none",
        "candidate", ("flags", "coloured_scalars_only_at_M_GUT"),
    ),
    (
        "doublet_triplet_splitting_tuned",
        "O46_1 = -(3/5) O46_54 (to ~2e-28) and O06 = 2|kappa| r0 (to ~4e-20) are tuned; no symmetry enforces them.",
        "OUTSIDE_G1_G8", ("G3 closure_scope disclosure",),
        "manuscript remaining tasks (axion_so10_theory_v20.tex: 'a radiatively stable v_Phi/v_S hierarchy'); no "
        "G1-G8 ledger definition names naturalness (the separate irreducible_gap_closure_contract_v20, with its own "
        "G-numbering, requires 'radiative stability or symmetry protection demonstrated' for its G4 hierarchy "
        "mechanism)",
        "disclosure in the closure scope ('tuned DT/M_I relations', g3_sm_target_track_v20.CLOSURE_SCOPE; decision "
        "D5, adopted)",
        "candidate", ("flags", "doublet_triplet_splitting_natural"),
    ),
    (
        "intermediate_scale_O05_cancellation",
        "O05 = (1/8)(4 - 2 r0^2) cancels the Phi-induced (10bar,1,3) mass to ~(M_I/M_GUT)^2 ~ 4e-9; its radiative "
        "stability is not addressed.",
        "OUTSIDE_G1_G8", (),
        "manuscript remaining tasks (axion_so10_theory_v20.tex): 'a radiatively stable v_Phi/v_S hierarchy'",
        "none under the adopted routing (decision D5)",
        "candidate", ("candidate", "exact_nonzero_coefficients", "lambda::O05_B01_126bar_norm"),
    ),
    (
        "hierarchy_radiative_stability",
        "Radiative stability of the M_I/M_GUT hierarchy is not addressed.",
        "OUTSIDE_G1_G8", (),
        "manuscript remaining tasks (axion_so10_theory_v20.tex)",
        "none under the adopted routing (decision D5)",
        "candidate", ("scope", "open"),
    ),
)

# Caveats that are model-level in the sense of the wave-3 clause (the equality set's scope lists tuned DT
# splitting and the O05 cancellation, sub-M_I coloured remnants, RG-anchor content, the Higgs quartic, no EWSB and
# no Yukawa sector; the rest are the candidate's other model-level flags and their consequences).  Decision D5
# (adopted) routes them out of G3: to G4/G6/G7/G8, or outside G1-G8 for the naturalness of the tunings.
MODEL_LEVEL_CAVEAT_IDS = frozenset(
    {
        "coloured_126bar_remnants_below_M_I",
        "no_electroweak_symmetry_breaking",
        "phi17_not_at_canonical_scale",
        "rg_anchor_field_content_not_reproduced",
        "higgs_quartic_too_large_at_benchmark",
        "tan_beta_one_light_doublet",
        "no_realistic_yukawa_sector",
        "proton_decay_mediators_below_M_I",
        "doublet_triplet_splitting_tuned",
        "intermediate_scale_O05_cancellation",
        "hierarchy_radiative_stability",
    }
)


def _caveats(reports: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    ledger = reports.get("ledger") or {}
    rows = []
    for cid, text, gate, also, basis, effect, artifact, key in CAVEAT_SPECS:
        value = _dig(reports.get(artifact) or {}, *key)
        definition = _dig(ledger, "gates", gate, "title") if gate.startswith("G") else None
        model_level = cid in MODEL_LEVEL_CAVEAT_IDS
        rows.append(
            {
                "id": cid,
                "caveat": text,
                "assigned_gate": gate,
                "assignment_status": CAVEAT_ROUTING_STATUS,
                "gate_title_from_ledger": definition,
                "also_affects": list(also),
                "basis": basis,
                "effect_on_G3": effect,
                "model_level_caveat": model_level,
                "under_current_repo_text": (
                    f"routed out of G3 by decision D5 (adopted) to {gate}: the ledger/roadmap wave-3 deliverable "
                    "carries the caveat-routing sentence of g3_sm_target_track_v20"
                    if model_level
                    else "not a model-level caveat of the wave-3 clause"
                ),
                "evidence": {"artifact": ARTIFACT_FILES[artifact], "key": _path_text(key), "value": _brief(value)},
                "evidence_present": value is not None,
            }
        )
    return rows


PLANNER_OPTION_ANALYSIS: dict[str, Any] = {
    "source": "retargeting planner (read-only plan), summarised verbatim in substance; not re-derived here",
    "planner_reading_of_repo_G3_definition": "an exact global-vacuum theorem with uniqueness modulo symmetry at an "
    "SM-preserving point of the declared potential, certified through the final gate on the full 486-real chart; "
    "the gate's own contract adds an exact full-Hessian rank/nullity certificate. No text requires a particular "
    "candidate, a physical hierarchy, a Higgs mass, natural DT splitting or RG consistency.",
    "repo_text_in_tension_with_that_reading": "the former ledger/roadmap wave-3 G3 deliverable (G1_G8_GATE_LEDGER_V20 "
    "closure_waves[3], g1_g8_execution_roadmap_v20 task W3-G3-FULL-STATIONARITY) said the PS candidate 'still "
    "needs its model-level "
    "caveats resolved and gate integration'; the equality set lists those caveats (tuned DT splitting and the O05 "
    "cancellation, sub-M_I coloured remnants, RG-anchor content, Higgs quartic, no EWSB, no Yukawa sector); "
    "routing them out of G3 is decision D5, adopted: the wave-3 deliverable now carries the caveat-routing "
    "sentence of g3_sm_target_track_v20",
    "options": {
        "i_either_track_closes": {
            "summary": "add an SM track; G3 closes if either track passes",
            "pros": ["keeps all 24 chiral-H integrity checks and their tests", "one authoritative final gate",
                     "small conceptual change"],
            "cons": ["the chiral-H track can never pass (target_unbroken_algebra_is_standard_model is False), so "
                     "calling it a closure route misleads", "'either' logic complicates a fail-closed gate",
                     "top-level science_criteria/blockers become ambiguous"],
            "risks": ["name collisions", "wrong track attribution in the verdict",
                      "latent chiral-track string mismatch ('only on' vs 'exactly on') carries over"],
        },
        "ii_retarget_entirely": {
            "summary": "retarget the gate to the PS candidate",
            "pros": ["simplest closure logic", "one decisive theorem", "no dead track"],
            "cons": ["drops the gate's fail-closed net over ~20 chiral-H artifacts",
                     "heavy churn (759-line test, workflow asserts, README/manuscript history)",
                     "loses the record of why the chiral-H point fails"],
            "risks": ["looks like switching targets until it passed (mitigate with historical_targets)"],
        },
        "iii_separate_SM_gate": {
            "summary": "keep the gate; add a separate 'G3 on SM target' gate",
            "pros": ["zero risk to the existing gate", "isolated tests", "reviewable before any status flip"],
            "cons": ["two final G3 gates with contradictory verdicts",
                     "every consumer must learn which gate is authoritative", "same ledger import-cycle problem"],
            "risks": ["consumers reading the wrong gate", "a stale OPEN verdict next to a closed ledger"],
        },
        "i_prime_hybrid": {
            "summary": "SM track is the only closure route; chiral-H kept as an integrity-checked diagnostic track "
            "that never closes G3; SM evaluation in a pure json/pathlib module (g3_sm_target_track_v20.py) imported "
            "by both ledger and final gate (no cycle); ledger_G3_status_matches_gate_closure check",
            "recommended": True,
        },
    },
    "recommendation": "i_prime_hybrid",
    "decisions_needed": {
        "D1": "structure: (i') recommended vs (ii) or (iii)",
        "D2": "G3 witness: the tuned benchmark with exact kernel 35 + 4 (recommended; needs the S11 replacement "
        "criterion) or the O06-raised member (literal 451/35, no light Higgs; needs the equality-set theorem "
        "extended to O06 >= 2|kappa| r0)",
        "D3": "internal-candidate semantics: (A) G1-G3 CLOSED approves an internal candidate (edit validate_release, "
        "ultimate/confirmation tests, tiers) or (B, recommended) also require empty downstream_caveats or G4 CLOSED",
        "D4": "G5: rebind to the PS vector (recommended) or keep both vectors and require them to match",
        "D5": "wave-3 clause: route 'model-level caveats' to G4/G6/G7/G8 (recommended) or keep them as G3 "
        "requirements (keeps G3 open indefinitely)",
        "D6": "accept cited classical theorems as G3-grade inputs, with the pinned allowlist and disclosure",
    },
    "automatic_downstream_effects_of_closing_G3": [
        "theory_confirmation_verdict_v20 sets internal_candidate from G1, G2, G3 CLOSED",
        "validate_release_v20 then fails (it requires final gate OPEN and no approved internal candidate)",
        "G5's closure evidence certifies the historical 27-parameter SOS vector, not the PS vector",
        "workflow asserts in g1-g8-gate-ledger.yml, g1-g8-execution-roadmap.yml and current-main-full-reaudit.yml "
        "pin G3 OPEN",
    ],
    "side_findings_reported_by_planner": [
        "chiral-track gap report required_statement says 'equality holds only on' while FINAL_THEOREM says "
        "'exactly on', so beta_global_gap_and_unique_equality_exact can never pass on that track (moot: non-SM point)",
        "G5 coupling-vector mismatch with the PS vector",
        "the PS candidate and equality-set artifacts are absent from validate_release's checksum core lists",
        "authoritative_full_model_gate_v20 verdict text is stale about G5",
        "theory_confirmation_verdict_v20 hard-codes tiers 'WITHHELD' regardless of internal_candidate",
    ],
    "side_findings_re_verified_by_this_module": False,
}
# The user's decisions D1-D6, as adopted (decisions_needed above is kept as the historical record).
PLANNER_OPTION_ANALYSIS["decisions_adopted"] = dict(sm_track.DECISIONS)


def _integration_gaps(reports: Mapping[str, Mapping[str, Any]], integrity: Mapping[str, bool],
                      theorem: Mapping[str, Any], g5: Mapping[str, Any]) -> list[dict[str, Any]]:
    cand = reports.get("candidate") or {}
    eq = reports.get("equality_set") or {}
    hess = reports.get("exact_hessian") or {}
    fg = reports.get("final_gate") or {}
    scope_open = _dig(cand, "scope", "open", default=[])
    stale = isinstance(scope_open, list) and any(
        isinstance(item, str) and item.startswith("exact (non-float) Hessian kernel/rank certificate")
        for item in scope_open
    )
    flag_renamed = _renamed_self_claim_flag(eq) and _renamed_self_claim_flag(hess)
    closing_track = fg.get("closing_track")
    return [
        {
            "item": "exact full-Hessian certificate for the PS target (planner step 1)",
            "state": "DONE" if integrity.get("sm_exact_hessian_report_executes") else "OPEN",
            "detail": "G3_SM_PATI_SALAM_EXACT_HESSIAN_V20 (447/39 exact; raised control 451/35); its tests run in "
            "CI and rebuild the report in memory against the committed artifact, which is not regenerated (--write) "
            "in the CI chain; g3_sm_target_track_v20 reads it as an SM-track input",
        },
        {
            "item": "exact Hessian report emits eps_family.final_acceptance_test.required_statement == "
            "SM_EPS_FINAL_THEOREM (S9)",
            "state": "DONE" if theorem.get("exact_hessian_emits_sm_eps_required_statement") else "OPEN",
            "detail": "wiring for the SM track's decisive-theorem string binding (g3_sm_target_track_v20 criterion "
            "sm_decisive_theorem_string_bound); the certifying artifact of the eps witness emits it, the equality "
            "module does not; not evaluated as a criterion by this dry run",
        },
        {
            "item": "candidate scope.open still lists the exact Hessian certificate as open",
            "state": "STALE" if stale else "OK",
            "detail": "refresh g3_sm_pati_salam_candidate_v20 scope once the exact Hessian is wired in",
        },
        {
            "item": "self-claim flag candidate_wired_into_g3_gate renamed report_closes_g3_by_itself (equality set and "
            "exact Hessian)",
            "state": "DONE" if flag_renamed else "OPEN",
            "detail": "flags.report_closes_g3_by_itself is False and candidate_wired_into_g3_gate is absent in both "
            "reports (a per-report self-claim; g3_sm_target_track_v20.SELF_CLAIM_NOTE)",
        },
        {
            "item": "eps-family extension of the equality set and the Hessian to O06 = 2|kappa| r0 + eps (L1, L2)",
            "state": "DONE" if integrity.get("sm_exact_hessian_eps_family_executes") else "OPEN",
            "detail": "G3_SM_PATI_SALAM_EXACT_HESSIAN_V20 eps_family: {V_eps = V0} = G.q0 for every eps >= 0 (given the "
            "equality-set theorem) and kernel = orbit, 451/35, for every eps > 0; its tests run in CI and rebuild the "
            "report in memory against the committed artifact, which is not regenerated (--write) in the CI chain",
        },
        {
            "item": "decision D2 on full_Hessian_rank_448_nullity_38_exact and full_448_quotient_strictly_positive_exact "
            "for the tuned benchmark",
            "state": "DECIDED",
            "detail": sm_track.DECISIONS["D2"],
        },
        {
            "item": "decision D6 on cited classical theorems and hand-argued steps as G3-grade inputs",
            "state": "DECIDED",
            "detail": sm_track.DECISIONS["D6"],
        },
        {
            "item": "decision D5 on the wave-3 clause (model-level caveats)",
            "state": "DECIDED",
            "detail": sm_track.DECISIONS["D5"],
        },
        {
            "item": "G5 rebind to the PS coupling vector (D4)",
            "state": "DONE" if g5.get("covers_closing_coupling_vector") is True else "OPEN",
            "detail": "ledger gates.G5.bfb_coupling_vector: " + str(g5.get("why")),
        },
        {
            "item": "pure SM-track module g3_sm_target_track_v20.py, final-gate tracks layout, ledger/roadmap/matrix/"
            "confirmation/ultimate/validate_release updates, workflows, tests, README/manuscript, refreeze",
            "state": "DONE" if closing_track == sm_track.TRACK_NAME else "OPEN",
            "detail": "planner steps 3-11 (none is performed by this dry run); final gate closing_track = "
            f"{closing_track!r}",
        },
    ]


# ----------------------------------------------------------------------------
# Report.
# ----------------------------------------------------------------------------


def build_report(
    *,
    reports: Mapping[str, Mapping[str, Any]] | None = None,
    paths: Mapping[str, Path] | None = None,
) -> dict[str, Any]:
    """Build the dry-run report.  ``reports`` injects artifacts (tests); otherwise they are loaded."""
    if reports is None:
        loaded, meta = load_reports(paths)
    else:
        loaded = {key: dict(reports.get(key) or {}) if isinstance(reports.get(key), Mapping) else {}
                  for key in ARTIFACT_FILES}
        meta = {
            key: {"file": name, "path_is_default": None, "loaded": bool(loaded[key]),
                  "error": None if loaded[key] else "not supplied or empty", "sha256_lf": None}
            for key, name in ARTIFACT_FILES.items()
        }

    derived = _derived(loaded)
    integrity = _integrity_checks(loaded, derived)
    theorem = decisive_theorem_comparison(loaded, derived)
    ctx = {"reports": loaded, "integrity": integrity, "derived": derived, "theorem": theorem}

    fg = loaded.get("final_gate") or {}
    view = _final_gate_criteria_view(fg)
    gate_science = view.get("science_criteria") if isinstance(view.get("science_criteria"), Mapping) else {}
    gate_release = view.get("release_criteria") if isinstance(view.get("release_criteria"), Mapping) else {}
    science_names = list(SCIENCE_SPECS) + [n for n in gate_science if n not in SCIENCE_SPECS]
    release_names = list(RELEASE_SPECS) + [n for n in gate_release if n not in RELEASE_SPECS]
    science = [_evaluate(name, "science", ctx) for name in science_names]
    release = [_evaluate(name, "release", ctx) for name in release_names]
    criteria = science + release

    non_route = [c for c in criteria if not c["route_specific"]]
    integrity_ok = all(integrity.values())
    science_exact = all(c["classification"] == SATISFIED_EXACT for c in science if not c["route_specific"])
    release_exact = all(c["classification"] == SATISFIED_EXACT for c in release)
    would_close = bool(integrity_ok and science_exact and release_exact)

    quotient = next(c for c in science if c["final_gate_criterion"] == "full_448_quotient_strictly_positive_exact")
    s11 = _dig(quotient, "alternative_analogues", "S11_kernel_is_orbit_plus_tuned_light_doublet_exact", default={})
    s12 = _dig(quotient, "alternative_analogues", "S12_O06_raised_member_rank_451_nullity_35_exact", default={})
    # S11 (tuned benchmark) and S12 (O06-raised member) each stand in for BOTH Hessian criteria.
    others_exact = all(
        c["classification"] == SATISFIED_EXACT
        for c in non_route
        if c["final_gate_criterion"] not in HESSIAN_CRITERIA
    )
    with_s11 = bool(integrity_ok and others_exact and s11.get("value") is True)

    # The SM track witness family O06 = 2|kappa| r0 + eps, eps > 0: every criterion again, with the eps-family
    # evidence (release criteria are shared, so their records are reused).
    eps_science = [_evaluate(name, "science", ctx, specs=EPS_SCIENCE_SPECS) for name in science_names]
    eps_criteria = eps_science + release
    eps_non_route = [c for c in eps_criteria if not c["route_specific"]]
    eps_all_exact = bool(eps_non_route) and all(c["classification"] == SATISFIED_EXACT for c in eps_non_route)
    would_close_eps = bool(integrity_ok and eps_all_exact)
    eps_conditional = {
        c["final_gate_criterion"]: list(c["conditional_on_decisions"])
        for c in eps_non_route
        if c["classification"] == SATISFIED_EXACT and c.get("conditional_on_decisions")
    }
    # Taking an eps > 0 member as the G3 witness is itself the second option of decision D2 (adopted).
    eps_presumed = sorted({"D2", *{decision for decisions in eps_conditional.values() for decision in decisions}})
    eps_literal_not_evaluated = {
        c["final_gate_criterion"]: list(c["literal_conjuncts_not_evaluated"])
        for c in eps_non_route
        if c.get("literal_conjuncts_not_evaluated")
    }
    eps_blocking = [c["final_gate_criterion"] for c in eps_non_route if c["classification"] != SATISFIED_EXACT]
    # The O06-raised member is the eps = r0^2/100 member of the family.
    on_raised = bool(
        would_close_eps
        and s12.get("value") is True
        and s12.get("covered_by_exact_hessian_eps_family_L1_L2") is True
        and derived.get("O06_raise_equals_r0_squared_over_100") is True
    )

    counts = {name: sum(1 for c in criteria if c["classification"] == name) for name in CLASSIFICATIONS}
    blocking = [c["final_gate_criterion"] for c in non_route if c["classification"] != SATISFIED_EXACT]
    conditional = {
        c["final_gate_criterion"]: list(c["conditional_on_decisions"])
        for c in non_route
        if c["classification"] == SATISFIED_EXACT and c.get("conditional_on_decisions")
    }
    presumed = sorted({decision for decisions in conditional.values() for decision in decisions})
    literal_not_evaluated = {
        c["final_gate_criterion"]: list(c["literal_conjuncts_not_evaluated"])
        for c in non_route
        if c.get("literal_conjuncts_not_evaluated")
    }
    g5 = _g5_vector_comparison(loaded)
    caveats = _caveats(loaded)
    by_gate: dict[str, list[str]] = {}
    for row in caveats:
        by_gate.setdefault(row["assigned_gate"], []).append(row["id"])

    ledger = loaded.get("ledger") or {}
    baseline = {
        "final_gate_overall_state": fg.get("overall_state"),
        "final_gate_G3_closed": _dig(fg, "classification", "G3_closed"),
        "final_gate_mathematical_G3_closed": _dig(fg, "classification", "mathematical_G3_closed"),
        "final_gate_closing_track": fg.get("closing_track"),
        "ledger_status": ledger.get("status"),
        "ledger_gate_statuses": {
            gate: _dig(ledger, "gates", gate, "status") for gate in ("G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8")
        },
        "this_module_writes_only": [OUT_JSON.name, OUT_MD.name],
    }

    failures = [name for name, ok in integrity.items() if not ok]
    table = [
        {
            "criterion": c["final_gate_criterion"],
            "kind": c["kind"],
            "chiral_H_value": c["chiral_H_track_value"],
            "pati_salam_analogue": c["pati_salam_analogue"]["name"],
            "pati_salam_value": c["value"],
            "classification": c["classification"],
            "grade": c["pati_salam_analogue"]["grade"],
            "justification": c["justification"],
        }
        for c in criteria
    ]
    report: dict[str, Any] = {
        "status": STATUS,
        "dry_run": True,
        "gate_status_changed": False,
        "G3_closed": False,
        "model_contract_id": MODEL_CONTRACT_ID,
        "n_checks": len(integrity),
        "n_failed": len(failures),
        "failures": failures,
        "integrity_checks": integrity,
        "artifacts": meta,
        "missing_artifacts": [meta[k]["file"] for k in ARTIFACT_FILES if not meta[k]["loaded"]],
        "baseline_state": baseline,
        "target": {
            "candidate": "g3_sm_pati_salam_candidate_v20 (27-parameter benchmark of the declared 51-parameter "
            "exact-X potential)",
            "vacuum": "(Phi, H, Sigma, S, Phi17) = (p, 0, r0 sigma_std, r0, x0)",
            "benchmark": {k: (str(derived[k]) if derived.get(k) is not None else None) for k in ("r0", "x0", "kappa", "O06")},
            "symmetry_group": "SO(10) x U(1)_X x U(1)_PQ (U(1)_PQ accidental)",
        },
        "criteria": {"science": science, "release": release},
        "criterion_table": table,
        "classification_counts": counts,
        "n_criteria": len(criteria),
        "n_route_specific": sum(1 for c in criteria if c["route_specific"]),
        "n_non_route_specific": len(non_route),
        "n_non_route_specific_satisfied_exact": sum(1 for c in non_route if c["classification"] == SATISFIED_EXACT),
        "satisfied_exact_conditional_on_decisions": conditional,
        "n_satisfied_exact_conditional_on_decisions": len(conditional),
        "literal_conjuncts_not_evaluated": literal_not_evaluated,
        "blocking_criteria": blocking,
        "would_close_G3_mathematically_if_SM_track_added": would_close,
        "would_close_G3_mathematically_on_eps_member_if_SM_track_added": would_close_eps,
        "readiness_booleans": {
            "would_close_G3_mathematically_if_SM_track_added": would_close,
            "definition": "True only if every readiness integrity check passes and every non-route-specific "
            "criterion of the final gate (science and release) is SATISFIED_EXACT under its mathematical analogue; "
            "the wiring conjunct required_statement == theorem (S9) is excluded, and SATISFIED_EXACT for the "
            "equality-set and global-gap criteria presumes decision D6 (cited classical theorems and hand-argued "
            "steps accepted as G3-grade inputs)",
            "decisions_presumed": presumed,
            "science_criteria_all_satisfied_exact": bool(integrity_ok and science_exact),
            "release_criteria_all_satisfied_exact": bool(integrity_ok and release_exact),
            "integrity_checks_all_pass": integrity_ok,
            "with_planner_S11_replacement_criterion": with_s11,
            "with_planner_S11_replacement_criterion_decisions_presumed": sorted({"D2", *presumed}),
            "with_planner_S11_replacement_criterion_note": "replaces the literal analogues of BOTH Hessian criteria "
            "(full_Hessian_rank_448_nullity_38_exact and full_448_quotient_strictly_positive_exact) by S11 (rank "
            "447 / nullity 39, kernel = orbit tangents (+) exactly identified tuned doublet, quartic lift 127/64 > 0); "
            "would be True subject to decisions D2 (adopting S11 would change the gate contract) and D6; S11 was not "
            "adopted: decision D2 takes the eps > 0 member as the G3 witness instead",
            "on_O06_raised_member": on_raised,
            "on_O06_raised_member_note": "the raised member (O06 + r0^2/100) lies outside the candidate's 27-parameter "
            "family, so the global-minimum and equality-set artifacts alone do not cover it; it is the eps = r0^2/100 "
            "member of the eps family, and this boolean equals the eps-member boolean for it (S12 value and eps-family "
            "coverage required)",
            "would_close_G3_mathematically_on_eps_member_if_SM_track_added": would_close_eps,
            "would_close_G3_mathematically_on_eps_member_if_SM_track_added_decisions_presumed": eps_presumed,
            "would_close_G3_mathematically_on_eps_member_if_SM_track_added_wiring_conjuncts_not_evaluated": sorted(
                {conjunct for conjuncts in eps_literal_not_evaluated.values() for conjunct in conjuncts}
            ),
            "would_close_G3_mathematically_on_eps_member_if_SM_track_added_note": f"{EPS_MEMBER}: True only if every "
            "readiness integrity check passes and every non-route-specific criterion (science and release) is "
            "SATISFIED_EXACT on V_eps = V + eps N_H for every eps > 0 in the perturbative window; SATISFIED_EXACT for "
            "the equality-set and global-gap criteria presumes decision D6 (adopted), and the wiring conjunct "
            "required_statement == theorem (S9) is not evaluated here (g3_sm_target_track_v20 evaluates it).  "
            "Choosing this member as the G3 witness is the second option of D2, which was adopted (it needs no "
            "gate-contract change).  This boolean must agree with g3_sm_target_track_v20's closed verdict.  The "
            "doublet has mass^2 eps M_GUT^2 (light for eps << r0^2) but "
            "electroweak symmetry is not broken; the tuned eps = 0 limit is not a strict minimum.",
        },
        "eps_member": {
            "member": EPS_MEMBER,
            "definition": "V_eps = V_PS + eps N_H: O06 = 2|kappa| r0 + eps, the other 26 benchmark couplings unchanged, "
            "same vacuum q0 = (p, 0, r0 sigma_std, r0, x0) and same G",
            "evidence_source": f"{ARTIFACT_FILES['exact_hessian']} eps_family (L1: equality set, L2: Hessian kernel, "
            "doublet mass^2 = eps) plus the benchmark evidence",
            "eps_window": {
                "lower": "0 (exclusive): eps = 0 is the tuned benchmark (447/39, not strictly positive on the quotient)",
                "upper_perturbative": str(derived["eps_perturbative_upper"])
                if derived.get("eps_perturbative_upper") is not None else None,
                "upper_meaning": "O06_eps = 2|kappa| r0 + eps < 12 < 4 pi",
                "raised_member_eps": str(derived["eps_raised"]) if derived.get("eps_raised") is not None else None,
                "tiny_member_eps": str(derived["eps_tiny"]) if derived.get("eps_tiny") is not None else None,
            },
            "criteria": {"science": eps_science, "release": "shared with the benchmark (criteria.release)"},
            "criterion_table": [
                {
                    "criterion": c["final_gate_criterion"],
                    "kind": c["kind"],
                    "pati_salam_analogue": c["pati_salam_analogue"]["name"],
                    "pati_salam_value": c["value"],
                    "classification": c["classification"],
                    "grade": c["pati_salam_analogue"]["grade"],
                    "justification": c["justification"],
                }
                for c in eps_criteria
            ],
            "classification_counts": {
                name: sum(1 for c in eps_criteria if c["classification"] == name) for name in CLASSIFICATIONS
            },
            "n_non_route_specific": len(eps_non_route),
            "n_non_route_specific_satisfied_exact": sum(
                1 for c in eps_non_route if c["classification"] == SATISFIED_EXACT
            ),
            "blocking_criteria": eps_blocking,
            "satisfied_exact_conditional_on_decisions": eps_conditional,
            "literal_conjuncts_not_evaluated": eps_literal_not_evaluated,
            "would_close_G3_mathematically_on_eps_member_if_SM_track_added": would_close_eps,
            "physics": "the doublet Re H_6..9 has tree-level mass^2 eps M_GUT^2: light but massive for eps << r0^2, "
            "eps -> 0+ is the tuned massless limit; H = 0, so electroweak symmetry is not broken on any member",
            "planner_D2_link": "D2's second option ('the O06-raised member ... needs the equality-set theorem extended "
            "to O06 >= 2|kappa| r0'): that extension is L1 of the exact Hessian report's eps_family, and the whole "
            "eps > 0 family (not only eps = r0^2/100) meets the literal Hessian criteria; decision D2 (adopted) makes "
            "the eps > 0 member the G3 witness",
        },
        "decisive_theorem": theorem,
        "proposed_additional_criteria": _proposed_criteria(loaded, science, g5),
        "caveat_routing_status": CAVEAT_ROUTING_STATUS,
        "physics_caveats": caveats,
        "caveat_gate_assignment": by_gate,
        "caveat_gate_assignment_status": CAVEAT_ROUTING_STATUS,
        "wave3_clause_reading": {
            "clause": "ledger wave 3 (closure_waves[3].deliverable) and roadmap W3-G3-FULL-STATIONARITY carry the "
            f"caveat-routing sentence of g3_sm_target_track_v20: '{WAVE3_CLAUSE}'",
            "status": CAVEAT_ROUTING_STATUS,
            "current_repo_reading": "decision D5 (adopted): the model-level caveats (the equality set's scope lists "
            "tuned DT splitting and the O05 cancellation, sub-M_I coloured remnants, RG-anchor content, Higgs "
            "quartic, no EWSB and no Yukawa sector) are routed downstream to G4/G6/G7/G8, or outside G1-G8 for the "
            "naturalness of the tunings; G3 keeps only disclosures",
            "reading_used": "the adopted D5 routing: only the G3-assigned caveats bear on G3, as disclosures or "
            "through the Hessian criteria (the tuned-doublet kernel is resolved by the D2 eps > 0 witness); G5's "
            "coupling vector is rebound under D4",
            "if_kept_as_G3_requirements": "the alternative D5 rejected: G3 would stay open indefinitely (DT "
            "naturalness, Higgs mass and EWSB would become G3 conditions)",
        },
        "planner_option_analysis": PLANNER_OPTION_ANALYSIS,
        "integration_gaps": _integration_gaps(loaded, integrity, theorem, g5),
    }
    report["verdict"] = _verdict(report)
    return report


def _verdict(report: Mapping[str, Any]) -> str:
    baseline = report["baseline_state"]
    boolean = report["would_close_G3_mathematically_if_SM_track_added"]
    flags = report["readiness_booleans"]
    parts = [
        "DRY RUN ONLY -- this is not a G3 closure. This module changes no gate status, gate report, ledger entry, "
        "workflow or checksum; it is the pre-integration map of the final gate's chiral-H criteria onto the SM "
        "Pati-Salam target. G3 is decided only by final_g3_acceptance_gate_v20 through its sm_pati_salam track "
        f"(g3_sm_target_track_v20): the final G3 gate is currently {baseline['final_gate_overall_state']!s} and the "
        f"ledger's G3 is {baseline['ledger_gate_statuses'].get('G3')!s}.",
        f"Of the final gate's {report['n_criteria']} chiral-H criteria, {report['n_route_specific']} are proof routes "
        f"specific to the chiral-H candidate; of the other {report['n_non_route_specific']}, the Pati-Salam target "
        f"satisfies {report['n_non_route_specific_satisfied_exact']} exactly"
        + (
            f" ({report['n_satisfied_exact_conditional_on_decisions']} of them, "
            f"{', '.join(report['satisfied_exact_conditional_on_decisions'])}, only under decision(s) "
            f"{', '.join(flags['decisions_presumed'])}: they rest on cited classical theorems and hand-argued steps "
            "that are not machine-checked)"
            if report["n_satisfied_exact_conditional_on_decisions"]
            else ""
        )
        + ".",
    ]
    if report["n_failed"]:
        parts.append(
            "Readiness integrity checks failed (" + ", ".join(report["failures"]) + "), so every readiness boolean "
            "is False (fail closed)."
        )
    if boolean:
        parts.append(
            "would_close_G3_mathematically_if_SM_track_added is True: every non-route-specific criterion is "
            "SATISFIED_EXACT under its mathematical analogue (presuming decision(s) "
            f"{', '.join(flags['decisions_presumed']) or 'none'}; wiring conjunct S9 excluded). G3 itself is "
            "decided by the final gate's sm_pati_salam track."
        )
    else:
        blocking = ", ".join(report["blocking_criteria"]) or "integrity checks"
        parts.append(
            f"would_close_G3_mathematically_if_SM_track_added is False; blocking: {blocking}."
        )
        if sorted(report["blocking_criteria"]) == sorted(HESSIAN_CRITERIA) and not report["n_failed"]:
            parts.append(
                "Both Hessian criteria are exactly false at the tuned benchmark under their literal analogues (rank "
                "451 / nullity 35 and kernel = the 35-dimensional orbit): the certified rank/nullity is 447/39 and the "
                "kernel is the 35 orbit tangents plus 4 tuned light-doublet directions, so the 451-dimensional "
                f"symmetry quotient is not strictly positive. The remaining {report['n_non_route_specific_satisfied_exact']} "
                f"of the {report['n_non_route_specific']} non-route-specific criteria are satisfied exactly."
            )
    parts.append(
        "With the planner's replacement criterion S11 in place of both Hessian criteria (rank 447 / nullity 39, "
        "kernel = orbit tangents plus the exactly identified tuned doublet, lifted at quartic order by lambda_eff = "
        f"127/64 > 0) the result would be {flags['with_planner_S11_replacement_criterion']}, subject to decisions "
        f"{' and '.join(flags['with_planner_S11_replacement_criterion_decisions_presumed'])} (adopting S11 would "
        "change the gate contract; the adopted D2 takes the eps > 0 member as the G3 witness instead)."
    )
    eps = report["eps_member"]
    eps_key = "would_close_G3_mathematically_on_eps_member_if_SM_track_added"
    if flags[eps_key]:
        parts.append(
            f"On the {EPS_MEMBER} (V_eps = V + eps N_H), inside the perturbative window 0 < eps < "
            f"{eps['eps_window']['upper_perturbative']} ({eps['eps_window']['upper_meaning']}; couplings_perturbative is "
            "certified only there, while L1 and L2 hold for every eps > 0), the literal criteria are met exactly: all "
            f"{eps['n_non_route_specific_satisfied_exact']} of the {eps['n_non_route_specific']} non-route-specific "
            "criteria are SATISFIED_EXACT, including both Hessian criteria (for every eps > 0 the Hessian at q0 is PSD "
            "with kernel exactly the 35-dimensional orbit, 451/35, strictly positive on the symmetry quotient; L2) and "
            "the equality-set and global-gap criteria ({V_eps = V0} = G.q0 for every eps >= 0 by L1 plus the equality "
            "report), so "
            f"{eps_key} = True, presuming decision(s) {', '.join(flags[eps_key + '_decisions_presumed']) or 'none'} "
            "with the wiring conjunct S9 not evaluated. The tuned eps = 0 limit is not a strict minimum on the "
            "symmetry quotient (447/39); the O06-raised member is eps = r0^2/100 (on_O06_raised_member = "
            f"{flags['on_O06_raised_member']}). The doublet has mass^2 eps M_GUT^2, light for eps << r0^2, but "
            "electroweak symmetry is not broken."
        )
    else:
        parts.append(
            f"On the {EPS_MEMBER}: {eps_key} = False; blocking: "
            + (", ".join(eps["blocking_criteria"]) or "integrity checks")
            + f" (on_O06_raised_member = {flags['on_O06_raised_member']})."
        )
    theorem = report["decisive_theorem"]
    parts.append(
        f"Decisive theorem: semantic agreement {theorem['semantic_agreement']} (same 486-real chart, same G = SO(10) "
        f"x U(1)_X x U(1)_PQ, V and q0 replaced by the SM benchmark), exact textual agreement "
        f"{theorem['exact_textual_agreement']} (the equality module emits no required_statement; the SM-track "
        "statement for the eps witness is emitted by the exact Hessian report: "
        f"{theorem['exact_hessian_emits_sm_eps_required_statement']}); the conjunct required_statement == theorem "
        "(wiring, S9) is not evaluated here."
    )
    parts.append(
        "Under the adopted caveat routing (decision D5, adopted; the ledger/roadmap wave-3 G3 deliverable carries "
        "the caveat-routing sentence), G3 carries the disclosures (accidental U(1)_PQ, benchmark-only Hessian, "
        "float64 end-to-end binding, cited theorems, family scope) and the tuned-doublet Hessian kernel (resolved by "
        "D2: the eps > 0 witness), while the coloured remnants, EWSB, RG content, Higgs quartic, Yukawas and the "
        "recomputed ranks belong to G4-G8 (the doublet zero modes also as G4/G6 classification items), G5's "
        "coupling vector is rebound under D4, and DT/O05/hierarchy naturalness lies outside G1-G8."
    )
    return " ".join(parts)


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _md_value(value: Any) -> str:
    if isinstance(value, list):
        return f"<list of {len(value)} items>"
    if isinstance(value, Mapping):
        return f"<object with {len(value)} keys>"
    return _cell(value)


def _markdown(report: Mapping[str, Any]) -> str:
    flags = report["readiness_booleans"]
    lines = [
        "# G3 SM Pati-Salam gate readiness (dry run) -- v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        f"**Gate status changed:** `{report['gate_status_changed']}` -- **This dry run closes G3:** `{report['G3_closed']}`",
        "",
        report["verdict"],
        "",
        "## Readiness booleans",
        "",
        f"- `would_close_G3_mathematically_if_SM_track_added`: `{report['would_close_G3_mathematically_if_SM_track_added']}`",
        f"- `science_criteria_all_satisfied_exact`: `{flags['science_criteria_all_satisfied_exact']}`",
        f"- `release_criteria_all_satisfied_exact`: `{flags['release_criteria_all_satisfied_exact']}`",
        f"- `integrity_checks_all_pass`: `{flags['integrity_checks_all_pass']}`",
        f"- `with_planner_S11_replacement_criterion`: `{flags['with_planner_S11_replacement_criterion']}` "
        f"({flags['with_planner_S11_replacement_criterion_note']})",
        f"- `on_O06_raised_member`: `{flags['on_O06_raised_member']}` ({flags['on_O06_raised_member_note']})",
        f"- `would_close_G3_mathematically_on_eps_member_if_SM_track_added`: "
        f"`{flags['would_close_G3_mathematically_on_eps_member_if_SM_track_added']}` (decisions presumed: "
        + (", ".join(f"`{d}`" for d in flags["would_close_G3_mathematically_on_eps_member_if_SM_track_added_decisions_presumed"])
           or "none")
        + "; wiring conjuncts not evaluated: "
        + (", ".join(flags["would_close_G3_mathematically_on_eps_member_if_SM_track_added_wiring_conjuncts_not_evaluated"])
           or "none")
        + ")",
        f"- blocking criteria: {', '.join(f'`{b}`' for b in report['blocking_criteria']) or 'none'}",
        f"- decisions presumed by SATISFIED_EXACT: {', '.join(f'`{d}`' for d in flags['decisions_presumed']) or 'none'} "
        f"(criteria: {', '.join(f'`{c}`' for c in report['satisfied_exact_conditional_on_decisions']) or 'none'})",
        "- literal conjuncts not evaluated: "
        + (
            "; ".join(f"`{c}`: {', '.join(v)}" for c, v in report["literal_conjuncts_not_evaluated"].items())
            or "none"
        ),
        f"- definition: {flags['definition']}",
        f"- caveat routing status: `{report['caveat_routing_status']}`",
        "",
        "## Criterion table",
        "",
        "| final-gate criterion | kind | chiral-H | Pati-Salam analogue | PS value | classification | grade | justification |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in report["criterion_table"]:
        lines.append(
            f"| `{row['criterion']}` | {row['kind']} | `{row['chiral_H_value']}` | {_cell(row['pati_salam_analogue'])} | "
            f"`{row['pati_salam_value']}` | **{row['classification']}** | {row['grade']} | {_cell(row['justification'])} |"
        )
    lines += ["", "Counts: " + ", ".join(f"{k} {v}" for k, v in report["classification_counts"].items()) + ".", ""]

    eps = report["eps_member"]
    lines += [
        f"## {eps['member']}",
        "",
        f"{eps['definition']}. Evidence: {eps['evidence_source']}.",
        "",
        f"- `would_close_G3_mathematically_on_eps_member_if_SM_track_added`: "
        f"`{eps['would_close_G3_mathematically_on_eps_member_if_SM_track_added']}`",
        f"- eps window: 0 < eps < `{eps['eps_window']['upper_perturbative']}` ({eps['eps_window']['upper_meaning']}); "
        f"raised member eps = `{eps['eps_window']['raised_member_eps']}`, tiny member eps = "
        f"`{eps['eps_window']['tiny_member_eps']}`",
        f"- blocking criteria: {', '.join(f'`{b}`' for b in eps['blocking_criteria']) or 'none'}",
        f"- conditional on decisions: "
        + (", ".join(f"`{c}`: {', '.join(v)}" for c, v in eps["satisfied_exact_conditional_on_decisions"].items()) or "none"),
        f"- physics: {eps['physics']}",
        f"- planner D2: {eps['planner_D2_link']}",
        "",
        "| final-gate criterion | kind | eps-member analogue | value | classification | grade | justification |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in eps["criterion_table"]:
        lines.append(
            f"| `{row['criterion']}` | {row['kind']} | {_cell(row['pati_salam_analogue'])} | `{row['pati_salam_value']}` | "
            f"**{row['classification']}** | {row['grade']} | {_cell(row['justification'])} |"
        )
    lines += ["", "Counts: " + ", ".join(f"{k} {v}" for k, v in eps["classification_counts"].items()) + ".", ""]

    theorem = report["decisive_theorem"]
    lines += [
        "## Decisive theorem",
        "",
        f"- Final gate (chiral-H track): {theorem['final_theorem_pinned']}",
        f"- SM counterpart: {theorem['sm_final_theorem']}",
        f"- SM track (eps witness): {theorem['sm_eps_final_theorem']} (emitted by the exact Hessian report: "
        f"`{theorem['exact_hessian_emits_sm_eps_required_statement']}`; final gate top-level decisive theorem equals "
        f"it: `{theorem['final_gate_top_level_decisive_theorem_is_sm_eps_theorem']}`)",
        f"- Equality module: {theorem['equality_module_theorem']}",
        f"- Exact textual agreement: `{theorem['exact_textual_agreement']}`; required_statement emitted: "
        f"`{theorem['equality_module_emits_required_statement']}`; semantic agreement: `{theorem['semantic_agreement']}`",
        f"- Symmetry group (normalised): gate `{theorem['gate_symmetry_group_normalised']}`, equality module "
        f"`{theorem['equality_module_symmetry_group_normalised']}`",
        "",
        "| semantic component | holds |",
        "|---|---|",
    ]
    lines += [f"| `{k}` | `{v}` |" for k, v in theorem["semantic_components"].items()]
    lines += ["", "Differences:", ""] + [f"- {item}" for item in theorem["differences"]]

    lines += ["", "## The Hessian criteria", ""]
    for criterion in HESSIAN_CRITERIA:
        record = next(c for c in report["criteria"]["science"] if c["final_gate_criterion"] == criterion)
        lines.append(f"`{criterion}` (literal analogue `{record['pati_salam_analogue']['name']}`: "
                     f"**{record['classification']}**)")
        lines.append("")
        lines += [f"- {note}" for note in record.get("notes", [])]
        for name, alt in record.get("alternative_analogues", {}).items():
            lines.append(f"- `{name}`: value `{alt['value']}`. {alt['statement']}")
        lines.append("")
    lines += ["## Criteria satisfied exactly only under adopted decisions", ""]
    for criterion, decisions in report["satisfied_exact_conditional_on_decisions"].items():
        record = next(c for c in report["criteria"]["science"] + report["criteria"]["release"]
                      if c["final_gate_criterion"] == criterion)
        lines.append(f"- `{criterion}`: {', '.join(decisions)}; grade: {record['pati_salam_analogue']['grade']}")

    lines += ["", "## Proposed additional criteria (planner; not in the booleans)", ""]
    for name, row in report["proposed_additional_criteria"].items():
        if isinstance(row, Mapping):
            lines.append(f"- `{name}`: `{row.get('value')}`")

    wave3 = report["wave3_clause_reading"]
    lines += [
        "",
        "## Physics caveats by gate (adopted routing, decision D5)",
        "",
        f"Routing status: `{report['caveat_routing_status']}`. Current repository text: {wave3['clause']}; "
        f"{wave3['current_repo_reading']}. The gate column below is the adopted routing; no model-level caveat is "
        "a G3 condition.",
        "",
        "| caveat | gate | also | model-level | effect on G3 | basis | evidence | value |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in report["physics_caveats"]:
        lines.append(
            f"| {_cell(row['caveat'])} | **{row['assigned_gate']}** | {_cell(', '.join(row['also_affects']))} | "
            f"`{row['model_level_caveat']}` | {_cell(row['effect_on_G3'])} | {_cell(row['basis'])} | "
            f"`{_cell(row['evidence']['key'])}` | `{_md_value(row['evidence']['value'])}` |"
        )

    analysis = report["planner_option_analysis"]
    lines += [
        "",
        "## Planner option analysis (summary)",
        "",
        "Planner's reading of the repository's G3 definition: " + analysis["planner_reading_of_repo_G3_definition"],
        "",
        "In tension with it: " + analysis["repo_text_in_tension_with_that_reading"] + ".",
        "",
    ]
    for name, option in analysis["options"].items():
        lines.append(f"- **{name}**{' (recommended)' if option.get('recommended') else ''}: {option['summary']}")
    lines += ["", "Decisions adopted:", ""]
    lines += [f"- **{k}**: {v}" for k, v in analysis["decisions_adopted"].items()]
    lines += ["", "Decisions needed (historical record of the planner's questions):", ""]
    lines += [f"- **{k}**: {v}" for k, v in analysis["decisions_needed"].items()]

    lines += ["", "## Integration gaps", "", "| item | state | detail |", "|---|---|---|"]
    lines += [f"| {_cell(g['item'])} | `{g['state']}` | {_cell(g['detail'])} |" for g in report["integration_gaps"]]

    lines += ["", "## Readiness integrity checks", "", "| check | passed |", "|---|---|"]
    lines += [f"| `{k}` | `{v}` |" for k, v in report["integrity_checks"].items()]
    lines += ["", "## Inputs", "", "| artifact | loaded | error | sha256 (LF) |", "|---|---|---|---|"]
    lines += [
        f"| `{m['file']}` | `{m['loaded']}` | `{m['error']}` | `{m['sha256_lf']}` |" for m in report["artifacts"].values()
    ]
    return "\n".join(lines) + "\n"


def write_report(report: Mapping[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_markdown(report), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true", help="write the JSON and Markdown readiness report")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    summary = {
        key: report[key]
        for key in ("status", "gate_status_changed", "G3_closed", "n_checks", "n_failed", "failures",
                    "classification_counts", "blocking_criteria", "would_close_G3_mathematically_if_SM_track_added",
                    "would_close_G3_mathematically_on_eps_member_if_SM_track_added", "readiness_booleans", "satisfied_exact_conditional_on_decisions", "literal_conjuncts_not_evaluated",
                    "caveat_routing_status")
    }
    summary["caveat_routing_note"] = (
        "caveat allocation is the adopted routing (decision D5); the ledger/roadmap wave-3 G3 deliverable carries "
        "the caveat-routing sentence of g3_sm_target_track_v20"
    )
    summary["criterion_table"] = [
        {k: row[k] for k in ("criterion", "classification", "pati_salam_value")} for row in report["criterion_table"]
    ]
    print(json.dumps(summary, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
