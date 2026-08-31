#!/usr/bin/env python3
"""V75 correlated quarter-spectator / eta-lattice audit.

V74 isolated a quarter endpoint obstruction for the pure class P=nu*ell^2.
V75 corrects the interpretation: an honest quotient fermion index does not
realize P by itself.  The minimal exact free-fermion completion found here is
an eight-Weyl module with index

    I6 = nu*ell^2 + nu*c2(R).

The extra R term is not an arbitrary spectator.  It is what repairs the
25/4 diagonal period to the integer 6.  Conversely, a clean +/-nu*c2(R)
sector has period 1/4 on the same spin CP3 quotient bundle.  Even granting
arbitrary signed half-index eta generators, such a clean quarter class is not
in the free-fermion eta curvature lattice: every half-index combination has
period in (1/2)Z on a closed spin six-manifold.

This closes the free-fermion "cancel the spectator separately" route, including
gauge-charged free eta sectors.  It does NOT construct the required
Z4-equivariant supersymmetric defect, the full Dai-Freed phase, or the physical
spectrum.  G1-G8 remain open.
"""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V75_QUARTER_SPECTATOR_ETA_LATTICE_AUDIT.json"
OUT_MD = ROOT / "SUSY_V75_QUARTER_SPECTATOR_ETA_LATTICE_AUDIT.md"

VERSION = "V75"
DATE = "2026-08-31"
SCHEMA = "susy_v75_quarter_spectator_eta_lattice_audit/v1"

V74_COMMIT = "ab544344fd46fc98faffe6a9342f82cd4d4a210a"
V74_ROUTE_CORE = "853833b9206e0eacb3a57ef72b7615c4d8c2b28b87a99155c93dc46d803e5603"
V74_MASTER_CORE = "3d51a7c13060dad547d8bedffb7f8299c0e24e67a21c8e121dd98b0efcbc57f9"

STATUS = (
    "V75_QUARTER_SPECTATOR_ETA_LATTICE_AUDIT__V74_ROUTE_AND_MASTER_CORES_BOUND__"
    "EIGHT_WEYL_FULL_QUOTIENT_MODULE_EXACT__INDEX_EQUALS_P_PLUS_NU_C2R__"
    "X3_XGRAV_NU3_NUGRAV_NU2X_CANCEL_EXACTLY__KAPPAD_PERIOD_SIX_INTEGRAL__"
    "ANTISYMMETRIC_R_COMPLETION_FORCED__CLEAN_QUARTER_R_PERIOD_ONE_OVER_FOUR__"
    "SIGNED_HALF_INDEX_ETA_LATTICE_NO_GO_UNIVERSAL_FOR_FREE_FERMIONS__"
    "GAUGE_CHARGED_FREE_ETA_ESCAPE_CLOSED__TORSION_ONLY_ESCAPE_REJECTED__"
    "CORRELATED_E5R_DEFECT_SELECTED_UNACCEPTED__SUPERSYMMETRIC_EQUIVARIANT_"
    "DAI_FREED_AND_SPECTRUM_REALIZATION_OPEN__G1_TO_G8_OPEN"
)

PRIMARY_SOURCES = [
    {
        "title": "Anomaly Inflow and the eta-Invariant",
        "url": "https://arxiv.org/abs/1909.08775",
        "scope": (
            "eta-invariant anomaly inflow and the APS-index relation; used for the "
            "free-fermion half-index lattice scope, not as a construction of this defect"
        ),
    },
    {
        "title": "Dai-Freed anomalies in particle physics",
        "url": "https://arxiv.org/abs/1808.00009",
        "scope": (
            "Dai-Freed refinement of fermion anomalies and global consistency of "
            "fermion spectra"
        ),
    },
    {
        "title": "Localized anomalies in orbifold gauge theories",
        "url": "https://arxiv.org/abs/hep-th/0305024",
        "scope": (
            "localized orbifold anomalies and the distinction between globally "
            "vanishing four-form inflow and surviving four-dimensional anomalies"
        ),
    },
    {
        "title": "Five-dimensional supersymmetric Chern-Simons action as a hypermultiplet quantum correction",
        "url": "https://arxiv.org/abs/hep-th/0609078",
        "scope": (
            "5D N=1 hypermultiplets can generate supersymmetric Chern-Simons terms; "
            "a possible realization framework only, not the missing Z4 defect completion"
        ),
    },
]

def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")

def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()

def fstr(x: Fraction | int) -> str:
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else str(x)

def quotient_check(*, x: int, n: int, r_parity: int, five_ality: int = 0) -> dict[str, Any]:
    u5 = (five_ality + 2 * x) % 5 == 0
    diag = (n + x + r_parity) % 2 == 0
    return {
        "x": x,
        "n": n,
        "qN": fstr(Fraction(n, 2)),
        "r_parity": r_parity,
        "five_ality": five_ality,
        "U5tilde_center": u5,
        "diagonal_center": diag,
        "honest_full_quotient": u5 and diag,
    }

def weyl_index_moments(*, copies: int, x: int, q: Fraction, su2_doublet: bool) -> dict[str, Fraction]:
    """Degree-six moments for gauge-singlet Weyl fermions."""
    rdim = 2 if su2_doublet else 1
    return {
        "weyl_count": Fraction(copies * rdim),
        "X3": Fraction(copies * rdim) * Fraction(x**3, 6),
        "X_p1": -Fraction(copies * rdim) * Fraction(x, 24),
        "nu_X2": Fraction(copies * rdim) * q * Fraction(x**2, 2),
        "nu2_X": Fraction(copies * rdim) * q**2 * Fraction(x, 2),
        "nu3": Fraction(copies * rdim) * q**3 / 6,
        "nu_p1": -Fraction(copies * rdim) * q / 24,
        "X_c2R": -Fraction(copies * x) if su2_doublet else Fraction(0),
        "nu_c2R": -Fraction(copies) * q if su2_doublet else Fraction(0),
    }

def add_moments(rows: list[dict[str, Fraction]]) -> dict[str, Fraction]:
    keys = rows[0].keys()
    return {k: sum((row[k] for row in rows), Fraction(0)) for k in keys}

def eight_weyl_module() -> dict[str, Any]:
    rows = [
        ("two_plus5", 2, +5, Fraction(1, 2), False, quotient_check(x=+5, n=+1, r_parity=0)),
        ("two_minus5", 2, -5, Fraction(1, 2), False, quotient_check(x=-5, n=+1, r_parity=0)),
        ("two_neutral_R_doublets", 2, 0, Fraction(-1, 2), True, quotient_check(x=0, n=-1, r_parity=1)),
    ]
    moments = []
    fields = []
    for name, copies, x, q, doublet, qc in rows:
        mm = weyl_index_moments(copies=copies, x=x, q=q, su2_doublet=doublet)
        moments.append(mm)
        fields.append({
            "name": name,
            "copies": copies,
            "X": x,
            "qN": fstr(q),
            "SU2R": "doublet" if doublet else "singlet",
            "quotient": qc,
            "moments": {k: fstr(v) for k, v in mm.items()},
        })
    total = add_moments(moments)
    expected = {
        "weyl_count": Fraction(8),
        "X3": Fraction(0),
        "X_p1": Fraction(0),
        "nu_X2": Fraction(25),
        "nu2_X": Fraction(0),
        "nu3": Fraction(0),
        "nu_p1": Fraction(0),
        "X_c2R": Fraction(0),
        "nu_c2R": Fraction(1),
    }
    if total != expected:
        raise RuntimeError(f"eight-Weyl ledger drift: {total} != {expected}")
    if not all(f["quotient"]["honest_full_quotient"] for f in fields):
        raise RuntimeError("eight-Weyl quotient descent failed")
    return {
        "status": "EXACT_HONEST_EIGHT_WEYL_CORRELATED_INDEX",
        "fields": fields,
        "total_moments": {k: fstr(v) for k, v in total.items()},
        "identification": "25 nu fX^2 + nu c2(R) = nu ell^2 + nu c2(R), ell=5 fX",
        "complete_index": "I6 = P + nu c2(R)",
        "P": "nu ell^2",
        "all_unwanted_abelian_and_gravity_correlations_cancel": True,
        "pure_SU5_anomaly": 0,
        "mixed_SU5_anomaly": 0,
        "reason_SU5": "all eight Weyl fermions are SU(5) singlets",
    }

def period_and_eta_theorem() -> dict[str, Any]:
    nu = Fraction(1)
    ell = Fraction(5, 2)
    rho = Fraction(1, 2)
    c2r = -(rho**2)
    p = nu * ell**2
    r = nu * c2r
    corr = p + r
    nu3quarter = nu**3 / 4
    half_eta_period_lattice_step = Fraction(1, 2)
    return {
        "status": "CP3_QUOTIENT_WITNESS__CLEAN_QUARTER_FREE_ETA_NO_GO",
        "witness": {
            "manifold": "CP3 (spin)",
            "bundle": "full diagonal quotient bundle induced by kappaD",
            "nu": fstr(nu),
            "ell": fstr(ell),
            "rhoR": fstr(rho),
            "c2R": fstr(c2r),
            "P_period": fstr(p),
            "nu_c2R_period": fstr(r),
            "correlated_period": fstr(corr),
            "nu3_over4_period": fstr(nu3quarter),
        },
        "correlated_class_integral_on_witness": corr.denominator == 1,
        "half_index_eta_scope": {
            "assumption": (
                "grant arbitrary signed half-index eta generators built from honest "
                "full-quotient fermion representations"
            ),
            "closed_spin_six_manifold_period_lattice": "(1/2) Z",
            "reason": (
                "each honest fermion Dirac index is integral; multiplying generators "
                "by signed half-levels gives periods in (1/2)Z"
            ),
            "clean_plus_or_minus_nu_c2R_allowed": abs(r) % half_eta_period_lattice_step == 0,
            "clean_nu3_over4_allowed": nu3quarter % half_eta_period_lattice_step == 0,
            "conclusion": (
                "no free-fermion eta sector, gauge-neutral or gauge-charged, can carry "
                "a clean +/-nu c2(R) or nu^3/4 curvature while every other free-curvature "
                "term cancels"
            ),
        },
        "ordinary_integral_counterterm_clean_R_allowed": r.denominator == 1,
        "torsion_only_can_change_free_curvature": False,
    }

def endpoint_completion() -> dict[str, Any]:
    return {
        "status": "ANTISYMMETRIC_R_COMPLETION_FORCED_AND_BRIDGE_UNCHANGED",
        "z00": {
            "pure_residual": "+P=+nu ell^2",
            "quantized_correlated_completion": "+nu[ell^2+c2(R)]",
            "diagonal_period": "6",
            "forced_R_sign": "+nu c2(R)",
        },
        "z11": {
            "pure_residual": "-Pprime=-nu ellprime^2",
            "quantized_correlated_completion": "-nu[ellprime^2+c2(R)]",
            "diagonal_period": "-6",
            "forced_R_sign": "-nu c2(R)",
        },
        "required_R_profile": ["+nu c2(R)", "-nu c2(R)"],
        "common_overlap_identity": (
            "nu[(ell^2+c2R)-(ellprime^2+c2R)] = nu(ell^2-ellprime^2) = nu A B"
        ),
        "V74_primitive_common_K_bridge_preserved": True,
        "interpretation": (
            "the quarter term is not an independent spectator to cancel; it signals "
            "that the pure P ledger is not itself the complete index of honest quotient matter"
        ),
    }

def build_audit() -> dict[str, Any]:
    audit = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "lineage": {
            "V74_commit": V74_COMMIT,
            "V74_route_core": V74_ROUTE_CORE,
            "V74_master_core": V74_MASTER_CORE,
            "settled_V74_results_preserved": [
                "primitive common-K bridge r=nu A B",
                "integer and candidate spin half-level bridge shifts cannot alter the quarter class",
                "conditional vector-linear/four-form BF scaffold",
                "existing Spin(11) tensor restriction has no AB term",
            ],
        },
        "eight_weyl_correlated_module": eight_weyl_module(),
        "period_eta_lattice_theorem": period_and_eta_theorem(),
        "endpoint_quantized_completion": endpoint_completion(),
        "candidate_matrix": [
            {"id": "F75_EIGHT_WEYL_CORRELATED_ENDPOINT", "selected": True, "accepted": False,
             "status": "FREE_CURVATURE_AND_FULL_QUOTIENT_INDEX_PASS__SUPERSYMMETRIC_Z4_EQUIVARIANT_DEFECT_AND_SPECTRUM_OPEN"},
            {"id": "F75_CLEAN_R_ETA_SPECTATOR", "selected": False, "accepted": False,
             "status": "REJECTED_UNIVERSAL_HALF_INDEX_PERIOD_NO_GO"},
            {"id": "F75_GAUGE_CHARGED_FREE_ETA_ESCAPE", "selected": False, "accepted": False,
             "status": "REJECTED_IF_ALL_OTHER_FREE_CURVATURE_TERMS_CANCEL__SAME_CP3_HALF_INDEX_PERIOD_NO_GO"},
            {"id": "F75_INTERACTING_OR_NONFERMIONIC_REFINED_DEFECT", "selected": False, "accepted": False,
             "status": "OPEN_NOT_CLASSIFIED"},
        ],
        "decision": {
            "quarter_obstruction_interpretation_updated": True,
            "pure_P_as_complete_honest_endpoint_index": False,
            "P_plus_R_has_exact_free_fermion_realization": True,
            "clean_R_free_eta_repair_exists": False,
            "gauge_charged_free_eta_repair_exists_if_clean": False,
            "V74_common_bridge_still_required": True,
            "current_Spin11_action_accepted": False,
            "G1_to_G8": "OPEN",
        },
        "next_required_work": [
            "recompute the raw z00/z11 SU2R equivariant index of gaugino, gravitino, tensorino and ghosts in one normalization and test for the forced (+R,-R) profile",
            "construct a 5D/defect supersymmetric realization of the correlated P+R index, or prove that no such gapped realization exists with the required quotient lifts",
            "construct the Z4 orbit, isotropy lifts, cap/source data and Dai-Freed phase for the primitive K bridge plus correlated endpoint theory",
            "derive parities and the complete spectrum; prove no unwanted chiral colored/charged remainder",
            "construct the mixed normal-supergravity deformed linear superform and solve BPS/source equations, positivity, stabilization and Hessian",
            "retain the V74/V73 KK, thresholds, flavor, proton, operator-ring and cosmology obligations",
        ],
        "primary_sources": PRIMARY_SOURCES,
    }
    audit["core_sha256"] = canonical_sha(audit)
    return audit

def render_md(audit: Mapping[str, Any]) -> str:
    t = audit["period_eta_lattice_theorem"]["witness"]
    lines = [
        "# V75 quarter-spectator eta-lattice audit", "", f"Status: `{audit['status']}`", "",
        f"Core SHA-256: `{audit['core_sha256']}`", "", "## Exact correlated endpoint module", "",
        "The honest eight-Weyl quotient module is", "",
        "`2 x 1_(+5,qN=+1/2) + 2 x 1_(-5,qN=+1/2) + 2 x (2_R)_(0,qN=-1/2)`.", "",
        "Its complete degree-six index is", "", "`I6 = nu ell^2 + nu c2(R)`.", "",
        "The X^3, X-gravity, nu^3, nu-gravity, nu^2 X and X c2(R) terms cancel exactly.",
        "All eight fields descend through the full quotient.", "", "## Quarter theorem", "",
        "On the spin `CP3` diagonal-quotient witness,", "",
        f"`int P={t['P_period']}`, `int nu c2(R)={t['nu_c2R_period']}`, and",
        f"`int [P+nu c2(R)]={t['correlated_period']}`.", "",
        "Thus the correlated class has integer period six, while a clean `+/-nu c2(R)` has quarter period.",
        "Even granting arbitrary signed half-index eta generators, every free-fermion eta curvature has periods in `(1/2) Z`.",
        "Therefore a clean `+/-nu c2(R)` (and likewise `nu^3/4`) is impossible in the full free-fermion eta lattice.",
        "This includes gauge-charged free fermions once every other free-curvature coefficient is required to cancel.", "",
        "## Endpoint consequence", "", "The quantized endpoint completions are", "",
        "- `z00: +nu[ell^2+c2(R)]`, period `+6`;", "- `z11: -nu[ellprime^2+c2(R)]`, period `-6`.", "",
        "The forced R profile is antisymmetric `(+R,-R)` and cancels out of the common overlap difference, so V74's bridge stays `nu A B`.", "",
        "## Strict decision", "", "The free-curvature/global-form part advances, but the theory is not finished.",
        "The eight-Weyl module has not been realized as a supersymmetric Z4-equivariant gapped defect, and the Dai-Freed/torsion phase and spectrum remain open.",
        "The current Spin(11) action remains rejected and G1-G8 remain OPEN.", "", "## Primary sources", "",
    ]
    for src in audit["primary_sources"]:
        lines.append(f"- [{src['title']}]({src['url']}): {src['scope']}")
    return "\n".join(lines) + "\n"

def write_outputs() -> dict[str, Any]:
    audit = build_audit()
    OUT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_md(audit), encoding="utf-8")
    return audit

def check_outputs() -> dict[str, Any]:
    audit = build_audit()
    if not OUT_JSON.is_file() or OUT_JSON.read_text(encoding="utf-8") != json.dumps(audit, indent=2, sort_keys=True) + "\n":
        raise RuntimeError("stale V75 JSON artifact")
    if not OUT_MD.is_file() or OUT_MD.read_text(encoding="utf-8") != render_md(audit):
        raise RuntimeError("stale V75 markdown artifact")
    loaded = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    if loaded.get("core_sha256") != canonical_sha(loaded):
        raise RuntimeError("noncanonical V75 core")
    return audit

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        audit = write_outputs()
    elif args.check:
        audit = check_outputs()
    else:
        audit = build_audit()
        print(json.dumps(audit, indent=2, sort_keys=True))
        return 0
    print(audit["status"])
    print(audit["core_sha256"])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
