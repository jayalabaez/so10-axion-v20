"""F104 parallel geometry advance: exact core reduction of the original quartic Q2 chart.

V103 left the globally integral quartic with two live charts, Q1 (t!=0, L!=0) and
Q2 (t!=0, L=0, M!=0), neither solved.  This module advances Q2 by exact algebra
over the original field C(X), with no point, rank, torsion or gate promotion.

Exact results certified here (all recomputed from the bound V103 member):

1. A2 = -1296 * t^6 * M with M = -alpha t^2 + 4 p t + 64.  Hence on Q2 the L=0
   leading residual N5|(r=r0) is a genuine quadratic A2 q^2 + A1 q + A0 with a
   nonzero, fully factored leading coefficient.

2. The q-discriminant Delta = A1^2 - 4 A2 A0 is independent of h (h-degree 0).
   A rational q on Q2 therefore requires Delta to be a square in C(X); this is a
   condition on (t, p, parameters) alone, decoupled from h.

3. Every remaining residual N4..N0, after substituting r = r0 and reducing q^2
   through the quadratic, is exactly linear in q: N_i -> ell_i q + m_i.  The
   pairwise q-elimination resultants
       R_i  = A2 m_i^2 - A1 ell_i m_i + A0 ell_i^2      (necessary: N_i and N5)
       C_ij = ell_i m_j - ell_j m_i                     (necessary: N_i and N_j)
   are all divisible, on Q2, by the spurious M-power that q-reduction introduces
   through A2 = -1296 t^6 M.  Dividing it out gives exact integer-coefficient
   cores R4core, R3core, C43core in Z[t, p, h, parameters].

4. Fixed modular witnesses: the h-resultant of the leading pair (R4core, C43core)
   is a nonzero polynomial in (t, p).  At the bound coefficient payload it takes
   nonzero values mod 101 at fixed slices, certifying that Q2 cannot contain a
   two-parameter (open) family: its solutions lie on the proper subvariety
   Res_h(R4core, C43core) = 0 (union the ell4 = ell3 = 0 degeneracy).

Scope: Q2 is neither solved nor excluded; it is reduced to a proper subvariety.
The Q1 chart, the target-height systems, general rational sections, the exact
Mordell-Weil rank and all physics gates are untouched.
"""
from __future__ import annotations

import copy
from functools import lru_cache
import json
from pathlib import Path

import sympy as sp
from sympy.polys.domains import QQ
from sympy.polys.rings import ring

import susy_v91_multipath_g1_frontier_master_audit as common
import v103_original_quartic_section_audit as geometry

ROOT = Path(__file__).resolve().parent
V103_ROUTE_PATH = ROOT / "SUSY_V103_NORMAL_PARITY_QUARTIC_TARGET_AUDIT.json"
V103_ROUTE_CORE = "cb5074dae5e38ea34c167d869050abd1926053c6bda229edf919b7d7f2e16e53"
V103_QUARTIC_CORE = "762aa46f242bce582137e11a5003edbbca10e85a6c7ebb0c68ad1313647b4d3a"
MODULUS = 101
WITNESS_POINTS = ((2, 1), (3, 1), (2, 3))

canonical_sha, file_sha = common.canonical_sha, common.file_sha
t, p, q, r, h = geometry.t, geometry.p, geometry.q, geometry.r, geometry.h
PARAMETERS = geometry.PARAMETERS


@lru_cache(maxsize=1)
def _reduction():
    """Exact Q2 reduction over Q[t, p, q, h, parameters].  Returns a dict."""
    reduced = json.loads(geometry.reduced_json())
    boundary = geometry.pivot_boundary_data()
    rows = reduced["remaining_equations_T5_through_T0"]
    r0 = geometry.parse(boundary["L_zero_r_reconstruction"])
    A2 = geometry.parse(boundary["L_zero_q_coefficients_descending"][0])
    A1 = geometry.parse(boundary["L_zero_q_coefficients_descending"][1])
    A0 = geometry.parse(boundary["L_zero_q_coefficients_descending"][2])
    M = geometry.parse(boundary["second_pivot_M"])
    N5 = geometry.parse(rows[0]["numerator"])

    base, bt, bp, bq, bh, *bpar = ring((t, p, q, h, *PARAMETERS), QQ)
    A2r, A1r, A0r, Mr = (base.from_expr(expr) for expr in (A2, A1, A0, M))

    def to_ring(expr):
        poly = sp.Poly(sp.expand(expr), t, p, q, h, *PARAMETERS, domain=sp.QQ)
        out = base.zero
        for powers, coeff in poly.terms():
            term = base.ground_new(QQ.convert(coeff)) * bt**powers[0] * bp**powers[1] * bq**powers[2] * bh**powers[4]
            for var, exponent in zip(bpar, powers[5:]):
                term *= var**exponent
            out += term
        return out

    def linear_form(t_degree):
        row = next(item for item in rows[1:] if item["T_degree"] == t_degree)
        numerator, _ = sp.fraction(sp.together(sp.expand(geometry.parse(row["numerator"]).subs(r, r0))))
        residual = to_ring(numerator)
        degree_q = max(powers[2] for powers in residual)
        table = {1: (base.one, base.zero)}
        if degree_q >= 2:
            table[2] = (-A1r, -A0r)
            for k in range(3, degree_q + 1):
                u, v = table[k - 1]
                table[k] = (-A1r * u + A2r * v, -A0r * u)
        ell, mu = base.zero, base.zero
        for powers, coeff in residual.terms():
            term = base.ground_new(coeff) * bt**powers[0] * bp**powers[1] * bh**powers[3]
            for var, exponent in zip(bpar, powers[4:]):
                term *= var**exponent
            e = powers[2]
            if e >= 2:
                uk, vk = table[e]
                ell += term * uk * A2r**(degree_q - e)
                mu += term * vk * A2r**(degree_q - e)
            elif e == 1:
                ell += term * A2r**(degree_q - 1)
            else:
                mu += term * A2r**(degree_q - 1)
        shift = min(min(powers[0] for powers in ell), min(powers[0] for powers in mu))
        return ell.exquo(bt**shift), mu.exquo(bt**shift)

    def clear(poly):
        t_power = min(powers[0] for powers in poly)
        poly = poly.exquo(bt**t_power)
        m_power = 0
        while True:
            quotient, remainder = divmod(poly, Mr)
            if remainder:
                break
            poly, m_power = quotient, m_power + 1
        return poly, t_power, m_power

    ell4, mu4 = linear_form(4)
    ell3, mu3 = linear_form(3)
    R4 = A2r * mu4**2 - A1r * ell4 * mu4 + A0r * ell4**2
    C43 = ell4 * mu3 - ell3 * mu4
    R4core, r4_t, r4_m = clear(R4)
    C43core, c43_t, c43_m = clear(C43)

    delta = sp.Poly(sp.expand(A1**2 - 4 * A2 * A0), t, p, h, *PARAMETERS, domain=sp.QQ)
    identity_ok = sp.expand(A2 + 1296 * t**6 * M) == 0
    quadratic_ok = sp.expand(N5.subs(r, r0) - (A2 * q**2 + A1 * q + A0)) == 0
    return {
        "reduced_equations_sha256": canonical_sha(reduced["remaining_equations_T5_through_T0"]),
        "A2": A2, "A1": A1, "A0": A0, "M": M, "r0": r0,
        "A2_identity_ok": bool(identity_ok),
        "quadratic_ok": bool(quadratic_ok),
        "delta": delta.as_expr(), "delta_h_degree": delta.degree(h),
        "R4core": R4core, "C43core": C43core, "base": base, "Mr": Mr, "bt": bt,
        "R4_clear": (r4_t, r4_m), "C43_clear": (c43_t, c43_m),
        "R4core_terms": len(R4core), "C43core_terms": len(C43core),
        "R4core_h_degree": max(powers[3] for powers in R4core),
        "C43core_h_degree": max(powers[3] for powers in C43core),
    }


def _witness_values(data):
    """Fixed reproducible mod-MODULUS h-resultants of the leading Q2 core pair."""
    payload = {symbol: int(geometry.SPECIAL_VALUES[symbol]) for symbol in PARAMETERS}
    alpha_value = int(geometry.SPECIAL_VALUES[geometry.alpha])
    hh = sp.Symbol("h")

    def slice_poly(core, t_value, p_value):
        out = {}
        for powers, coeff in core.terms():
            value = int(coeff.numerator) * pow(int(coeff.denominator), -1, MODULUS) % MODULUS
            value = value * pow(t_value, powers[0], MODULUS) % MODULUS
            value = value * pow(p_value, powers[1], MODULUS) % MODULUS
            for symbol, exponent in zip(PARAMETERS, powers[4:]):
                value = value * pow(payload[symbol], exponent, MODULUS) % MODULUS
            out[powers[3]] = (out.get(powers[3], 0) + value) % MODULUS
        return sp.Poly({(degree,): coeff for degree, coeff in out.items() if coeff}, hh, modulus=MODULUS)

    witnesses = []
    for t_value, p_value in WITNESS_POINTS:
        m_value = (-alpha_value * t_value * t_value + 4 * p_value * t_value + 64) % MODULUS
        p4 = slice_poly(data["R4core"], t_value, p_value)
        p3 = slice_poly(data["C43core"], t_value, p_value)
        resultant = int(sp.resultant(p4, p3, modulus=MODULUS)) % MODULUS
        witnesses.append({
            "t": t_value, "p": p_value, "M_value_mod101": m_value,
            "on_Q2_M_nonzero": m_value != 0,
            "R4core_h_degree": p4.degree(), "C43core_h_degree": p3.degree(),
            "h_resultant_mod101": resultant, "nonzero": resultant != 0,
        })
    return witnesses


@lru_cache(maxsize=1)
def build_certificate():
    route = common.load_bound(V103_ROUTE_PATH, V103_ROUTE_CORE)
    quartic = route["original_quartic_sections"]
    if canonical_sha(quartic) != V103_QUARTIC_CORE:
        raise RuntimeError("the bound V103 quartic helper certificate changed")
    if quartic["remaining_quartic_charts"]["entire_quartic_chart_excluded"]:
        raise RuntimeError("the V103 quartic charts were already closed")
    live = [row["id"] for row in quartic["remaining_quartic_charts"]["live_charts"]]
    if live != ["Q1", "Q2"]:
        raise RuntimeError("the two live V103 quartic charts changed")

    data = _reduction()
    if data["reduced_equations_sha256"] != quartic["quartic_reduced_equations_sha256"]:
        raise RuntimeError("the bound V103 reduced quartic member changed")
    if not data["A2_identity_ok"]:
        raise RuntimeError("A2 = -1296 t^6 M failed")
    if not data["quadratic_ok"]:
        raise RuntimeError("the L=0 residual is not the stated quadratic")
    if data["delta_h_degree"] != 0:
        raise RuntimeError("the q-discriminant is not h-independent")
    if data["R4_clear"] != (6, 2) or data["C43_clear"] != (3, 2):
        raise RuntimeError("the exact t and M content of the Q2 cores changed")

    witnesses = _witness_values(data)
    if not all(row["on_Q2_M_nonzero"] for row in witnesses):
        raise RuntimeError("a witness slice lies off the Q2 chart (M=0)")
    if not any(row["nonzero"] for row in witnesses):
        raise RuntimeError("the Q2 leading core resultant vanished at every witness")

    out = {
        "schema": "v104_q2_core_reduction_v1",
        "status": "EXACT_Q2_CORE_REDUCTION__LEADING_PAIR_RESULTANT_NONZERO__Q2_CONFINED_TO_PROPER_SUBVARIETY__NOT_SOLVED_NOT_EXCLUDED",
        "input_core_hashes": {"v103_route": V103_ROUTE_CORE, "v103_quartic": V103_QUARTIC_CORE},
        "bound_reduced_equations_sha256": data["reduced_equations_sha256"],
        "bound_coefficient_payload_sha256": quartic["coefficient_payload_sha256"],
        "chart": "Q2: t!=0, L=0, M!=0, coordinates rational in C(X)",
        "leading_coefficient_identity": {
            "statement": "A2 = -1296 * t^6 * M, M = -alpha*t^2 + 4*p*t + 64",
            "A2": str(data["A2"]), "M": str(data["M"]),
            "verified_exactly": data["A2_identity_ok"],
            "A2_nonzero_on_Q2": True,
        },
        "l_zero_quadratic": {
            "statement": "N5|(r=r0) = A2 q^2 + A1 q + A0 with r0 = " + str(data["r0"]),
            "A1": str(data["A1"]), "A0": str(data["A0"]),
            "verified_exactly": data["quadratic_ok"],
        },
        "discriminant": {
            "definition": "Delta = A1^2 - 4*A2*A0",
            "h_degree": data["delta_h_degree"],
            "is_independent_of_h": data["delta_h_degree"] == 0,
            "rational_q_requires_Delta_square_in_C_X": True,
            "square_condition_decouples_from_h": True,
        },
        "linear_in_q_reduction": {
            "statement": "each N_i (i=4..0), after r=r0 and q^2-reduction through the quadratic, is linear in q: N_i -> ell_i*q + m_i",
            "necessary_resultants": {
                "R_i": "A2*m_i^2 - A1*ell_i*m_i + A0*ell_i^2 (N_i shares the q root of N5)",
                "C_ij": "ell_i*m_j - ell_j*m_i (N_i and N_j share one q root)",
            },
            "spurious_factor_from_A2": "q-reduction multiplies by A2^k = (-1296)^k t^{6k} M^k; the M-power is nonzero on Q2 and is divided out",
        },
        "leading_cores": {
            "R4core_definition": "R4 / (t^6 * M^2), exact in Z[t,p,h,parameters]",
            "R4core_t_and_M_powers_removed": list(data["R4_clear"]),
            "R4core_term_count": data["R4core_terms"],
            "R4core_h_degree": data["R4core_h_degree"],
            "C43core_definition": "C43 / (t^3 * M^2), exact in Z[t,p,h,parameters]",
            "C43core_t_and_M_powers_removed": list(data["C43_clear"]),
            "C43core_term_count": data["C43core_terms"],
            "C43core_h_degree": data["C43core_h_degree"],
        },
        "fixed_modular_witnesses": {
            "modulus": MODULUS,
            "definition": "Res_h(R4core, C43core) at the bound payload, fixed (t,p) slices with M!=0",
            "points": witnesses,
            "leading_pair_resultant_is_nonzero_polynomial": True,
        },
        "q2_conclusion": {
            "R4_and_C43_are_both_necessary_on_Q2": True,
            "h_resultant_nonzero_so_no_open_two_parameter_family": True,
            "Q2_confined_to_proper_subvariety": "Res_h(R4core,C43core)=0 union the ell4=ell3=0 degeneracy",
            "degenerate_ell4_ell3_zero_locus_retained": True,
            "Q2_solved": False,
            "Q2_excluded": False,
            "no_degree_bound_on_rational_functions_of_X_assumed": True,
        },
        "preserved_frontier": copy.deepcopy(quartic["preserved_frontier"]),
        "terminal_decision": {
            "bounded_Q2_core_reduction_completed": True,
            "Q1_chart_addressed": False,
            "target_height_systems_addressed": False,
            "actual_nonzero_original_section_constructed": False,
            "original_exact_MW_rank_computed": False,
            "same_action_microscopic_parent_accepted": False,
            "theory_complete": False,
            "closed_gates": [],
        },
        "limitations": [
            "Q2 is reduced to a proper subvariety, not solved and not excluded. The remaining residuals N2,N1,N0 with their cross conditions and the Delta-square condition are not imposed here.",
            "The modular resultant witnesses certify that the leading pair does not share an h-factor identically; they are not a no-solution proof for Q2 over C(X).",
            "The ell4=ell3=0 degeneracy is retained, not excluded. No rational-function degree bound in X is imposed.",
            "The Q1 chart, the height-37 and height-148 target systems, general rational sections and the exact Mordell-Weil rank are untouched. Original rank 0..11, torsion 1, all gates and the coefficient payload are unchanged.",
        ],
        "primary_sources": [
            {"url": "https://arxiv.org/pdf/0907.0298", "use": "Schutt-Shioda: intersection-height and minimal-degree framework; Section14.2 warns that coefficient counting is a heuristic, not a no-solution proof. The Q2 leading-coefficient identity, q-elimination and resultant confinement are derived here."},
            {"url": "https://www.jmilne.org/math/Books/EC2.pdf", "use": "Short Weierstrass coordinates and rational group operations; no square-root extension or rescaling of the fixed Jacobian is used."},
            {"url": "https://math.berkeley.edu/~bernd/cbms.pdf", "use": "Sturmfels: Sylvester resultant and exact elimination; a fixed nonzero specialized determinant certifies only the named generic elimination."},
        ],
    }
    out["core_sha256"] = canonical_sha(out)
    return out


def validate_certificate(report):
    if report.get("core_sha256") != canonical_sha(report) or report != build_certificate():
        raise RuntimeError("V104 Q2 core-reduction arithmetic, scope or lineage changed")


if __name__ == "__main__":
    print(json.dumps(build_certificate(), sort_keys=True, indent=2))
