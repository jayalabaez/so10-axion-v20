"""F105 correction of the V104 Q2 ring-index mapping.

V104's exact L=0 quadratic and h-independent discriminant are unaffected.
Its helper conversion of the remaining residuals, however, used powers[4] for
h and powers[5:] for the parameter tuple after constructing Poly(...,
t,p,q,h,alpha,beta,gamma,delta,epsilon). That drops the actual h exponent and
shifts the parameter exponents. This audit recomputes the N4/N3 reductions
without that conversion and checks the same fixed witnesses.

The corrected witnesses remain nonzero, so the qualitative V104 conclusion
(Q2 is confined to a proper subvariety) survives. The saved V104 core
polynomials/witness values do not survive and must not be used as F105 inputs.
Q2 is still neither solved nor excluded.
"""
from __future__ import annotations

import copy
from functools import lru_cache
import json
from pathlib import Path

import sympy as sp

import susy_v91_multipath_g1_frontier_master_audit as common
import v103_original_quartic_section_audit as geometry

ROOT = Path(__file__).resolve().parent
V104_ROUTE_PATH = ROOT / "SUSY_V104_Q2_CORE_REDUCTION_AUDIT.json"
V104_ROUTE_CORE = "b22468dd4bd4ab3c77839ba8fa561deee01a539f23fc64e176c4660a169cc41c"
MODULUS = 101
WITNESS_POINTS = ((2, 1), (3, 1), (2, 3))
EXPECTED_OLD = (28, 97, 91)
EXPECTED_CORRECTED = (65, 52, 20)

t, p, q, r, h = geometry.t, geometry.p, geometry.q, geometry.r, geometry.h
PARAMETERS = geometry.PARAMETERS
canonical_sha = common.canonical_sha


def _common_t_shift(ell, mu):
    variables = (t, p, h, *PARAMETERS)
    pe = sp.Poly(sp.expand(ell), *variables, domain=sp.QQ)
    pm = sp.Poly(sp.expand(mu), *variables, domain=sp.QQ)
    shift = min(min(m[0] for m, _ in pe.terms()), min(m[0] for m, _ in pm.terms()))
    return sp.expand(ell / t**shift), sp.expand(mu / t**shift), int(shift)


@lru_cache(maxsize=1)
def corrected_data():
    reduced = json.loads(geometry.reduced_json())
    boundary = geometry.pivot_boundary_data()
    rows = reduced["remaining_equations_T5_through_T0"]
    r0 = geometry.parse(boundary["L_zero_r_reconstruction"])
    A2, A1, A0 = [geometry.parse(value) for value in boundary["L_zero_q_coefficients_descending"]]
    M = geometry.parse(boundary["second_pivot_M"])
    N5 = geometry.parse(rows[0]["numerator"])
    if sp.expand(A2 + 1296*t**6*M) != 0:
        raise RuntimeError("the immutable Q2 leading coefficient changed")
    if sp.expand(N5.subs(r, r0) - (A2*q*q + A1*q + A0)) != 0:
        raise RuntimeError("the immutable Q2 quadratic changed")

    def linear_form(t_degree):
        row = next(item for item in rows[1:] if item["T_degree"] == t_degree)
        numerator, _ = sp.fraction(sp.together(geometry.parse(row["numerator"]).subs(r, r0)))
        poly = sp.Poly(sp.expand(numerator), q, domain="EX")
        degree = poly.degree()
        reps = {0: (sp.Integer(0), sp.Integer(1)),
                1: (sp.Integer(1), sp.Integer(0)),
                2: (-A1, -A0)}
        for exponent in range(3, degree + 1):
            u, v = reps[exponent - 1]
            reps[exponent] = (sp.expand(-A1*u + A2*v), sp.expand(-A0*u))
        ell = sp.Integer(0)
        mu = sp.Integer(0)
        for (exponent,), coefficient in poly.terms():
            if exponent >= 2:
                u, v = reps[exponent]
                scale = A2**(degree - exponent)
                ell += coefficient*u*scale
                mu += coefficient*v*scale
            elif exponent == 1:
                ell += coefficient*A2**(degree - 1)
            else:
                mu += coefficient*A2**(degree - 1)
        ell, mu, shift = _common_t_shift(ell, mu)
        return ell, mu, degree, shift

    ell4, mu4, degree4, shift4 = linear_form(4)
    ell3, mu3, degree3, shift3 = linear_form(3)
    delta = sp.Poly(sp.expand(A1*A1 - 4*A2*A0), t, p, h, *PARAMETERS, domain=sp.QQ)
    return {"A2": A2, "A1": A1, "A0": A0, "M": M,
            "ell4": ell4, "mu4": mu4, "ell3": ell3, "mu3": mu3,
            "degree4": degree4, "degree3": degree3,
            "shift4": shift4, "shift3": shift3,
            "delta_h_degree": int(delta.degree(h))}


def corrected_witnesses(data):
    out = []
    for tv, pv in WITNESS_POINTS:
        subs = {**geometry.SPECIAL_VALUES, t: tv, p: pv}
        a2 = int(data["A2"].subs(subs)) % MODULUS
        a1 = int(data["A1"].subs(subs)) % MODULUS
        a0 = int(data["A0"].subs(subs)) % MODULUS
        e4 = sp.Poly(data["ell4"].subs(subs), h, modulus=MODULUS)
        m4 = sp.Poly(data["mu4"].subs(subs), h, modulus=MODULUS)
        e3 = sp.Poly(data["ell3"].subs(subs), h, modulus=MODULUS)
        m3 = sp.Poly(data["mu3"].subs(subs), h, modulus=MODULUS)
        R4 = a2*m4*m4 - a1*e4*m4 + a0*e4*e4
        C43 = e4*m3 - e3*m4
        resultant = int(sp.resultant(R4, C43, h)) % MODULUS
        mvalue = int(data["M"].subs(subs)) % MODULUS
        out.append({"t": tv, "p": pv, "M_value_mod101": mvalue,
                    "on_Q2_M_nonzero": mvalue != 0,
                    "R4_h_degree": int(R4.degree()),
                    "C43_h_degree": int(C43.degree()),
                    "h_resultant_mod101": resultant,
                    "nonzero": resultant != 0})
    return out


@lru_cache(maxsize=1)
def build_certificate():
    old = common.load_bound(V104_ROUTE_PATH, V104_ROUTE_CORE)
    old_values = tuple(row["h_resultant_mod101"] for row in old["q2_core_reduction"]["fixed_modular_witnesses"]["points"])
    if old_values != EXPECTED_OLD:
        raise RuntimeError("the bound V104 witness payload changed")
    data = corrected_data()
    witnesses = corrected_witnesses(data)
    corrected = tuple(row["h_resultant_mod101"] for row in witnesses)
    if corrected != EXPECTED_CORRECTED:
        raise RuntimeError("the corrected Q2 witnesses changed")
    if not all(row["on_Q2_M_nonzero"] and row["nonzero"] for row in witnesses):
        raise RuntimeError("a corrected witness is not a valid nonzero Q2 slice")
    out = {
        "schema": "v105_v104_q2_index_correction_v1",
        "status": "V104_RING_INDEX_DEFECT_CORRECTED__QUALITATIVE_Q2_CONFINEMENT_SURVIVES__Q2_NOT_SOLVED_NOT_EXCLUDED",
        "parent_commit": "8d8c7b2bbf5ce377c0c34519de0b9061fd9eb564",
        "bound_v104_route_core": V104_ROUTE_CORE,
        "defect": {
            "old_mapping": "Poly variable order is (t,p,q,h,alpha,beta,gamma,delta,epsilon), but V104 to_ring used h<-powers[4] and parameters<-powers[5:]",
            "correct_mapping": "h<-powers[3] and parameters<-powers[4:] (implemented here by direct SymPy expressions, avoiding manual index remapping)",
            "A2_quadratic_affected": False,
            "delta_h_independence_affected": False,
            "saved_R4core_C43core_affected": True,
            "saved_witness_values_affected": True
        },
        "old_witness_values_mod101": list(old_values),
        "corrected_witnesses": witnesses,
        "corrected_witness_values_mod101": list(corrected),
        "corrected_linear_reduction": {
            "N4_q_degree": data["degree4"], "N3_q_degree": data["degree3"],
            "N4_common_t_shift": data["shift4"], "N3_common_t_shift": data["shift3"],
            "delta_h_degree": data["delta_h_degree"]
        },
        "conclusion": {
            "corrected_leading_pair_resultant_is_nonzero_polynomial": True,
            "Q2_still_confined_to_a_proper_subvariety": True,
            "Q2_solved": False, "Q2_excluded": False,
            "old_saved_cores_may_be_used_for_F105": False,
            "must_recompute_all_N4_through_N0_cross_conditions_before_F105_closure": True,
            "gate_promotion": False
        }
    }
    out["core_sha256"] = canonical_sha(out)
    return out


def validate_certificate(report):
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("V105 correction certificate hash mismatch")
    fresh = build_certificate()
    if report != fresh:
        raise RuntimeError("V105 correction differs from fresh recomputation")
    if report["conclusion"]["Q2_solved"] or report["conclusion"]["Q2_excluded"]:
        raise RuntimeError("the correction does not decide Q2")
    return True
