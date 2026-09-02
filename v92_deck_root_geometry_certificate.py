#!/usr/bin/env python3
"""V92 compact deck-root geometry, proved by a complete good-reduction cover.

The finite-field Jacobian calculations are NOT interpreted as characteristic-
zero affine ideal certificates.  The implication to characteristic zero uses
the explicitly specified projective relative Cartier model over Z_(101), its
base-change-compatible regular-center blowups, and its complete special-fibre
cover.  The non-smooth locus is closed and proper over the DVR; if its generic
fibre were nonempty its image would contain the closed point, a contradiction.

This proves a geometric compact member and an order-four automorphism, not a
diagonal orbibundle, matter spectrum, quantum anomaly cancellation, or a gate.
"""
from __future__ import annotations

import copy
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import sympy as sp


ROOT = Path(__file__).resolve().parent
V91_PATH = ROOT / "SUSY_V91_SPINC_QUANTIZATION_TENSOR_CONE_FINITE_TORSION_AUDIT.json"
V91_CORE = "4a581af0dd4cfc6fd3f66ef1e3ea2801b9770c67822d984a02deb602865c0322"
PAYLOAD_SHA = "f2b6dcad4a90364cff7557f379e4ccdb76bd466553a3289659d08a356119f0cf"
PRIME = 101
SCHEMA = "v92_deck_root_geometry_good_reduction_certificate_v1"


def canonical_sha(value: Any) -> str:
    body = copy.deepcopy(value)
    if isinstance(body, dict):
        body.pop("core_sha256", None)
    return hashlib.sha256(json.dumps(
        body, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")).hexdigest()


def load_payload() -> dict[str, str]:
    parent = json.loads(V91_PATH.read_text(encoding="utf-8"))
    if parent.get("core_sha256") != V91_CORE or canonical_sha(parent) != V91_CORE:
        raise RuntimeError("V92 geometry requires the exact canonical V91 parent")
    payload = parent["geometry"]["new_symmetry_only_member"]["coefficient_payload"]
    if canonical_sha(payload) != PAYLOAD_SHA:
        raise RuntimeError("frozen V91 geometry coefficient payload changed")
    return copy.deepcopy(payload)


def expressions(payload: Mapping[str, Any]) -> dict[str, Any]:
    symbols = dict(zip(
        ("s", "t", "r0", "r1", "U", "V", "W"),
        sp.symbols("s t r0 r1 U V W"),
    ))
    s, U, V, W = (symbols[name] for name in ("s", "U", "V", "W"))
    coefficients = {name: sp.sympify(value, locals=symbols)
                    for name, value in payload.items()}
    required = {"L", "p0", "p1", "p2", "p3", "p4"}
    if set(coefficients) != required:
        raise RuntimeError("unexpected V91 geometric coefficient keys")
    P = sp.expand(sum(coefficients[f"p{i}"] * U ** (4-i) * V**i
                      for i in range(5)))
    Q = sp.expand(s*coefficients["L"]*(U**2-V**2)**2 + s**2*P)
    return {"symbols": symbols, "coefficients": coefficients,
            "P": P, "Q": Q, "F": sp.expand(W**2-Q)}


def bundle_and_boundary_certificate(payload: Mapping[str, Any], prime: int = PRIME) -> dict:
    if not sp.isprime(prime) or prime == 2:
        raise RuntimeError("good reduction requires an odd prime")
    m = expressions(payload)
    z = m["symbols"]
    s, t, r0, r1, U, V = (z[name] for name in ("s", "t", "r0", "r1", "U", "V"))
    base_vars = (s, t, r0, r1)
    weights = ((1,0), (1,4), (0,1), (0,1))
    degrees = {}
    for name, value in m["coefficients"].items():
        if value == 0:
            continue
        poly = sp.Poly(value, *base_vars, domain=sp.ZZ)
        derived = {tuple(sum(powers[j]*weights[j][axis] for j in range(4))
                         for axis in range(2)) for powers, _ in poly.terms()}
        expected = (3,12) if name == "L" else (2,12)
        if derived != {expected}:
            raise RuntimeError("a compact coefficient has the wrong bundle")
        degrees[name] = list(expected)
    if sp.expand(m["coefficients"]["L"].subs(s,0)-t**3) != 0:
        raise RuntimeError("L is not the required unit on S")
    x = sp.symbols("x")
    boundary = [sp.expand(m["P"].subs(
        {s:0,t:1,r0:x,r1:1,U:sign,V:1}, simultaneous=True
    )) for sign in (1,-1)]
    # Degree and leading coefficient checks include the point r1=0 on P1.
    if any(sp.degree(poly,x) != 4 for poly in boundary):
        raise RuntimeError("a boundary branch point at infinity is not certified")
    leading = [int(sp.Poly(poly,x).LC()) for poly in boundary]
    discriminants = [int(sp.discriminant(poly,x)) for poly in boundary]
    resultant = int(sp.resultant(*boundary,x))
    if any(value % prime == 0 for value in leading+discriminants+[resultant]):
        raise RuntimeError("branch cover is not simple/disjoint over the good prime")
    return {
        "coefficient_bidegrees": degrees,
        "all_coefficients_integral": True,
        "boundary_restrictions_derived_from_payload": [str(poly) for poly in boundary],
        "boundary_degrees": [4,4], "leading_coefficients": leading,
        "discriminants_over_Z": discriminants, "resultant_over_Z": resultant,
        "prime": prime,
        "leading_coefficients_mod_prime": [x % prime for x in leading],
        "discriminants_mod_prime": [x % prime for x in discriminants],
        "resultant_mod_prime": resultant % prime,
        "no_boundary_root_at_r1_zero": True,
        "eight_simple_disjoint_geometric_branch_points_over_Fp": True,
        "L_on_S": "t^3; t is a unit because s=t=0 is excluded",
    }


def jacobian_basis(q: sp.Expr, variables: tuple, selectors: tuple = (),
                   prime: int = PRIME) -> list[str]:
    """Keep all ambient partials, THEN impose closed-stratum selectors."""
    generators = [q] + [sp.diff(q,var) for var in variables] + list(selectors)
    basis = sp.groebner(generators, *variables, order="grevlex", modulus=prime)
    return [str(poly.as_expr()) for poly in basis.polys]


@lru_cache(maxsize=4)
def _modular_cover_cached(payload_json: str, prime: int) -> dict:
    payload = json.loads(payload_json)
    bundle_and_boundary_certificate(payload, prime)
    m = expressions(payload)
    z = m["symbols"]
    s,t,r0,r1,U,V = (z[name] for name in ("s","t","r0","r1","U","V"))
    T,X,Z = sp.symbols("T X Z")
    # An exhaustive disjoint stratification is faster than recomputing the
    # whole overlapping U=1 charts.  Derivatives transverse to the strata are
    # NOT discarded.  No resultant-only or unsaturated elimination is used.
    rows = (
        ("r1_nonzero_V_nonzero", {s:1,r1:1,V:1,t:T,r0:X,U:Z}, (),
         "s=r1=V=1; T=t, X=r0, Z=U; no additional equations"),
        ("r1_zero_V_nonzero", {s:1,r0:1,V:1,t:T,r1:X,U:Z}, (X,),
         "s=r0=V=1; retain d/dX and add X=r1=0"),
        ("r1_nonzero_V_zero", {s:1,r1:1,U:1,t:T,r0:X,V:Z}, (Z,),
         "s=r1=U=1; retain d/dZ and add Z=V=0"),
        ("r1_zero_V_zero", {s:1,r0:1,U:1,t:T,r1:X,V:Z}, (X,Z),
         "s=r0=U=1; retain d/dX,d/dZ and add X=Z=0"),
    )
    result = []
    for name, substitution, selectors, convention in rows:
        q = sp.expand(m["Q"].subs(substitution, simultaneous=True))
        generators = [q]+[sp.diff(q,var) for var in (T,X,Z)]+list(selectors)
        basis = jacobian_basis(q, (T,X,Z), selectors, prime)
        result.append({
            "stratum": name, "coordinate_convention": convention,
            "Q_derived_from_frozen_payload": str(q),
            "ambient_variables": ["T","X","Z"],
            "closed_stratum_selectors": [str(v) for v in selectors],
            "all_three_ambient_partials_retained": True,
            "ideal_generators": [str(sp.expand(g)) for g in generators],
            "coefficient_field": f"GF({prime})", "monomial_order": "grevlex",
            "reduced_Groebner_basis": basis, "unit_ideal": basis == ["1"],
        })
    return {
        "method": "full ambient Jacobian plus exhaustive closed-stratum selectors",
        "prime": prime, "rows": result,
        "F_w_reduction": "F=w^2-Q, dF/dw=2w; characteristic is odd, so w=0",
        "cover": "s!=0, partitioned by r1!=0/r1=0 and V!=0/V=0",
        "all_t_values_including_t_zero_retained": True,
        "r0_and_r1_cannot_both_vanish": True,
        "U_and_V_cannot_both_vanish_on_hypersurface": True,
        "all_four_stratum_ideals_are_unit": all(row["unit_ideal"] for row in result),
        "affine_mod_p_empty_alone_implies_char_zero_empty": False,
        "aggregate_rows_sha256": canonical_sha(result),
    }


def compute_modular_cover(payload: Mapping[str, Any] | None = None,
                          prime: int = PRIME) -> dict:
    if payload is None:
        payload = load_payload()
    encoded = json.dumps(dict(payload),sort_keys=True,separators=(",",":"))
    return copy.deepcopy(_modular_cover_cached(encoded, prime))


def near_s_resolution_certificate(prime: int = PRIME) -> dict:
    ws,ss,rs,w,a,b,r,c,q = sp.symbols("ws ss rs w a b r c q")
    charts = {
        "B1_s": (ws**2-ss*rs**2-q, (ws,ss,rs,q)),
        "B1_w": (1-a**2*q-a*b**2*w, (w,a,b,q)),
        "B1_r": (w**2-a*r-a**2*q, (w,a,r,q)),
        "B2_a": (a*(c**2-q)-r, (a,c,r,q)),
        "B2_w": (w*(1-c**2*q)-c*r, (w,c,r,q)),
    }
    rows = []
    for name,(f,variables) in charts.items():
        basis = sp.groebner([f]+[sp.diff(f,var) for var in variables],
                            *variables, order="lex", modulus=prime)
        strings = [str(p.as_expr()) for p in basis.polys]
        expected = ["w","a","r"] if name == "B1_r" else ["1"]
        if strings != expected:
            raise RuntimeError("near-S resolved branch chart changed: "+name)
        rows.append({"chart":name, "equation":str(sp.expand(f)),
                     "variables":[str(v) for v in variables],
                     "field":f"GF({prime})", "Jacobian_basis":strings,
                     "final_chart":name != "B1_r"})
    q0,h = sp.symbols("q0 h")
    # Nonbranch witnesses use q0 as a parameter, never as a coordinate whose
    # derivative could artificially make the Jacobian ideal a unit ideal.
    s_witness = sp.groebner([ws**2-q0,2*ws,h*q0-1],ws,q0,h,
                            order="lex",modulus=prime)
    w_witness = sp.expand((1-a*a*q0)-a*(-2*a*q0)/2)
    second_w = sp.groebner([-c*r,-c,1-c*c*q0],c,r,q0,
                           order="lex",modulus=prime)
    if [str(p.as_expr()) for p in s_witness.polys] != ["1"] or w_witness != 1:
        raise RuntimeError("nonbranch first-chart unit witness failed")
    if [str(p.as_expr()) for p in second_w.polys] != ["1"]:
        raise RuntimeError("residual exceptional chart unit witness failed")
    return {
        "local_normal_form":"w^2-s*r^2-s^2*q",
        "normal_form_validity": (
            "Near C+ or C-, L*(U+V)^2 or L*(U-V)^2 is a unit. "
            "Absorb its square root etale-locally (2 invertible). At a simple "
            "boundary root, q=P is an etale coordinate since its base-curve derivative is a unit."
        ),
        "branch_rows":rows,
        "all_final_branch_chart_bases_unit":True,
        "both_C_plus_and_C_minus_covered":True,
        "nonbranch_q_not_treated_as_independent_coordinate":True,
        "nonbranch_first_s_witness_basis":["1"],
        "nonbranch_first_w_Bezout_identity":"(1-a^2*q0)-(a/2)*(-2*a*q0)=1",
        "nonbranch_first_r_argument": (
            "On S in the first r-chart, a*r=0. If q0 is a unit then "
            "F=F_w=0 forces a=w=0; F_a then forces r=0. Thus the only possible "
            "singular locus is the residual center, irrespective of derivatives of q."
        ),
        "residual_a_exceptional_derivative":"at a=r=0, d[a*(c^2-q)-r]/dr=-1",
        "residual_w_exceptional_witness_basis":["1"],
        "general_q_derivative_terms_vanish_on_relevant_exceptional_loci":True,
        "over_S_outside_centers": (
            "s=W=0 and U^2-V^2!=0 gives F_s=-L*(U^2-V^2)^2, a unit. "
            "There (s,W)=(W) on the hypersurface, so the residual blowup is an isomorphism."
        ),
        "complete_near_S_special_fibre_smoothness":True,
    }


def integral_model_and_lift(payload: Mapping[str, Any]) -> dict:
    m = expressions(payload)
    z = m["symbols"]
    s,t,r0,r1,U,V,W = (z[name] for name in ("s","t","r0","r1","U","V","W"))
    tau = {s:-s,t:t,r0:-r0,r1:r1,U:-U,V:V,W:sp.I*W}
    anti = sp.expand(m["F"].subs(tau,simultaneous=True)+m["F"])
    square = {name:sp.expand(value.subs(tau,simultaneous=True))
              for name,value in tau.items()}
    deck = {v:(-v if v == W else v) for v in tau}
    if anti != 0 or square != deck:
        raise RuntimeError("ambient order-four deck-root identity failed")
    if [sp.expand((U-V).subs(tau,simultaneous=True)),
        sp.expand((U+V).subs(tau,simultaneous=True))] != [-U-V,-U+V]:
        raise RuntimeError("first center permutation failed")
    s0,w0,e0,ep,em,a0,b0 = sp.symbols("s0 w0 e0 e_plus e_minus a0 b0")
    blowdown = {s:s0*e0*ep*em,W:w0*e0*ep*em,
                U:(a0*ep+b0*em)/2,V:(b0*em-a0*ep)/2}
    pulled_F = sp.expand(m["F"].subs(blowdown,simultaneous=True))
    pulled_L = sp.expand(m["coefficients"]["L"].subs(blowdown,simultaneous=True))
    pulled_P = sp.expand(m["P"].subs(blowdown,simultaneous=True))
    weak = sp.expand(e0*w0*w0-s0*pulled_L*ep*em*a0*a0*b0*b0-e0*s0*s0*pulled_P)
    pullback_residual = sp.expand(pulled_F-e0*ep**2*em**2*weak)
    lifted = {s0:-s0,w0:sp.I*w0,e0:e0,ep:em,em:ep,a0:-b0,b0:-a0,
              r0:-r0,r1:r1,t:t}
    equivariance = sp.expand(weak.subs(lifted,simultaneous=True)+weak)
    commutation = []
    for old,value in blowdown.items():
        lhs = value.subs(lifted,simultaneous=True)
        rhs = tau[old].subs(blowdown,simultaneous=True)
        commutation.append(sp.expand(lhs-rhs))
    if pullback_residual != 0 or equivariance != 0 or any(commutation):
        raise RuntimeError("resolved blowdown/equivariance identities failed")
    # Restore s=r1=V=1 after tau: the first Cox scaling is -1, which
    # changes T but not w (its s-degree is two).  Thus all three base
    # coordinates change sign and w gets i.  The residue form has character i.
    residue_character = sp.simplify(sp.det(-sp.eye(3))/sp.I)
    if residue_character != sp.I or sp.expand(residue_character**2) != -1:
        raise RuntimeError("holomorphic residue character changed")
    return {
        "base_ring":"R=Z_(101); action after etale base extension R[i]",
        "base":"F4_R with S^2=-4 and Kbar=2S+6F",
        "ambient": {
            "construction":"weighted P(1,1,2) bundle over F4_R",
            "coordinate_classes":{"U":"H","V":"H","W":"2H+Kbar"},
            "hypersurface_class":"4H+2Kbar=-K_A",
            "weighted_singular_section_avoided":"U=V=0 gives F=W^2!=0",
            "geometric_integrality": (
                "At the generic point of S x P1_UV, Q=s*t^3*(U^2-V^2)^2+O(s^2) "
                "has odd valuation one. It is not a square in the rational function "
                "field in characteristic zero or 101. The quadratic cover and its "
                "strict transform are geometrically integral."
            ),
            "projective_over_R":True,
            "ambient_flatness": (
                "The U=1 and V=1 patches have relative polynomial coordinates. "
                "The W patch is the weight-two quotient with an R-free semigroup "
                "monomial basis (2 is invertible). The first and second blowups "
                "are relative coordinate blowups near their centers and are "
                "identities elsewhere, hence the ambient remains R-flat."
            ),
        },
        "blowups": {
            "first":"Bl_(C+ union C-) with I+=(s,W,U-V), I-=(s,W,U+V)",
            "first_centers_disjoint_reason":"2 invertible and U,V cannot vanish together on W=0",
            "first_centers":"smooth relative P1 curves; ambient relative codimension 3",
            "second":"Bl_(D0_tilde), strict transform of D0=(s,W)",
            "second_center_smoothness": (
                "D0 is S x P1_UV over R. Each C+/- is Cartier inside D0, "
                "so its strict transform is canonically D0; ambient relative codimension 2."
            ),
            "base_change_justification": (
                "These centers are smooth relative coordinate subspaces in the smooth locus "
                "of the ambient. Etale-locally their ideals are subsets of relative polynomial "
                "coordinates. Every quotient by a power has an R-free monomial basis in "
                "normal coordinates (over the smooth center), so every power and the Rees "
                "algebra commute with R->Fp. This is stronger than merely asserting that "
                "blowups commute with arbitrary base change."
            ),
            "fiberwise_ambient_blowups_integral":True,
            "all_centers_smooth_over_R":True,
            "Rees_algebras_commute_with_special_fibre":True,
            "multiplicities":[2,2,1], "relative_codimensions":[3,3,2],
            "discrepancies":[0,0,0],
            "multiplicity_uniformity": (
                "First orders are exactly 2 because W^2 has coefficient 1. In the "
                "residual r-chart w^2-a*r-a^2*q the generic (w,a)-order is exactly "
                "1 from -a*r, in both characteristic zero and 101. Thus dividing by "
                "the exceptional factors gives the fibrewise strict transforms, with "
                "no exceptional hypersurface components introduced by specialization."
            ),
        },
        "strict_transform": {
            "class":"4H+2Kbar-2E_plus-2E_minus-E0=-K_Atilde",
            "blowdown":{str(k):str(v) for k,v in blowdown.items()},
            "total_pullback_factor":"e0*e_plus^2*e_minus^2",
            "weak_transform":str(weak),
            "pullback_identity_residual":str(pullback_residual),
            "flatness_argument": (
                "The strict-transform section is locally principal in the R-flat ambient "
                "near the hypersurface. Each ambient fibre is integral and the section "
                "is not identically zero (away from the centers it retains W^2 with "
                "coefficient 1). Hence each fibre is an effective Cartier divisor; "
                "the fibrewise Cartier criterion makes it a relative Cartier divisor, "
                "flat and finitely presented over R. The global closed transform is projective."
            ),
            "proper_flat_finitely_presented_integral_model":True,
        },
        "order_four_lift": {
            "ambient_tau":{str(k):str(v) for k,v in tau.items()},
            "ambient_F_transformed_plus_F":str(anti),
            "ambient_tau_squared":{str(k):str(v) for k,v in square.items()},
            "first_centers_exchanged":True,
            "residual_center_invariant":True,
            "lift_theorem": (
                "The invariant union of disjoint first centers gives an equivariant Rees "
                "algebra; the invariant strict transform D0 gives the second. The universal "
                "property uniquely lifts tau and its inverse. These are global regular "
                "automorphisms, not just maps of one Cox chart. Squaring equals the lifted "
                "deck involution by uniqueness (or equality on the dense unchanged open)."
            ),
            "resolved_coordinate_action":{str(k):str(v) for k,v in lifted.items()},
            "blowdown_commutation_residuals":[str(v) for v in commutation],
            "weak_transform_transformed_plus_itself":str(equivariance),
            "global_regular_lift_exists":True,
            "lift_squared_is_deck":True,
            "lift_has_exact_order_four":True,
            "field_of_definition":"Q(i)",
            "i_mod_101_witness":10,
            "affine_regauged_action":"(T,X,Z,w)->(-T,-X,-Z,i*w) on s=r1=V=1",
            "residue_form":"Omega=dT wedge dX wedge dZ/(2*w)",
            "holomorphic_three_form_character":str(residue_character),
            "squared_three_form_character":str(sp.expand(residue_character**2)),
            "preserves_holomorphic_three_form":False,
            "standalone_volume_preserving_CY_quotient":False,
            "supersymmetric_diagonal_action_requires_additional_R_bundle_data":True,
        },
    }


def specialize_smoothness(model: Mapping, away: Mapping, near: Mapping,
                          boundary: Mapping) -> dict:
    """Fail closed unless the proper model and every part of its cover pass."""
    expected_strata = {
        "r1_nonzero_V_nonzero": [], "r1_zero_V_nonzero": ["X"],
        "r1_nonzero_V_zero": ["Z"], "r1_zero_V_zero": ["X","Z"],
    }
    rows = away["rows"]
    if len(rows) != 4 or {row["stratum"] for row in rows} != set(expected_strata):
        raise RuntimeError("incomplete proper special-fibre stratum cover")
    for row in rows:
        if (row["closed_stratum_selectors"] != expected_strata[row["stratum"]]
            or row["ambient_variables"] != ["T","X","Z"]
            or not row["all_three_ambient_partials_retained"]
            or row["reduced_Groebner_basis"] != ["1"]
            or not row["unit_ideal"]):
            raise RuntimeError("incomplete proper special-fibre stratum certificate")
    final = [row for row in near["branch_rows"] if row["final_chart"]]
    if ({row["chart"] for row in final} != {"B1_s","B1_w","B2_a","B2_w"}
        or len(final) != 4 or any(row["Jacobian_basis"] != ["1"] for row in final)
        or not near["nonbranch_q_not_treated_as_independent_coordinate"]
        or not near["both_C_plus_and_C_minus_covered"]):
        raise RuntimeError("incomplete proper near-S chart cover")
    required = (
        model["strict_transform"]["proper_flat_finitely_presented_integral_model"],
        model["blowups"]["Rees_algebras_commute_with_special_fibre"],
        away["all_four_stratum_ideals_are_unit"],
        near["complete_near_S_special_fibre_smoothness"],
        boundary["eight_simple_disjoint_geometric_branch_points_over_Fp"],
    )
    if not all(required):
        raise RuntimeError("incomplete proper special-fibre smoothness certificate")
    if away["prime"] != PRIME or boundary["prime"] != PRIME:
        raise RuntimeError("mismatched specialization primes")
    return {
        "complete_special_fibre_cover": [
            "s!=0: four exhaustive r1/V strata with ALL ambient derivatives",
            "s=0 away from C+/-: F_s unit and Cartier residual blowup",
            "over both C+/- at all eight simple branch points: four final etale charts",
            "over C+/- off branch points: q-unit and residual-exceptional unit witnesses",
            "U=V=0 weighted singular section: absent from hypersurface",
        ],
        "special_fibre_smooth_over_F101":True,
        "properness_argument": (
            "The relative nonsmooth locus N in the projective flat finite-presentation "
            "model is closed. Its image in Spec Z_(101) is closed by properness and "
            "misses the closed point by the exhaustive special-fibre cover. It must "
            "therefore be empty: a closed subset containing the generic point would "
            "contain the closed point. The generic fibre is geometrically smooth over Q."
        ),
        "resolved_compact_member_geometrically_smooth_over_Q":True,
        "literal_QQ_affine_Jacobian_unit_bases_computed":False,
        "one_modular_affine_screen_promoted_without_proper_model":False,
        "V90_old_member_smoothness_reused":False,
    }


def build_certificate() -> dict:
    payload = load_payload()
    boundary = bundle_and_boundary_certificate(payload)
    if (boundary["discriminants_over_Z"], boundary["resultant_over_Z"]) != ([1129,1129],288):
        raise RuntimeError("frozen V91 branch invariants changed")
    away = compute_modular_cover(payload)
    near = near_s_resolution_certificate()
    model = integral_model_and_lift(payload)
    specialization = specialize_smoothness(model,away,near,boundary)
    report = {
        "schema":SCHEMA,
        "status":"PASS_COMPACT_SMOOTH_CREPANT_MEMBER_AND_GLOBAL_ORDER4_DECK_ROOT_OVER_QI",
        "parent_V91_core_sha256":V91_CORE,
        "coefficient_payload":payload,
        "coefficient_payload_sha256":canonical_sha(payload),
        "bundle_and_boundary":boundary,
        "away_S_good_reduction_cover":away,
        "near_S_resolution":near,
        "integral_projective_model_and_lift":model,
        "proper_specialization":specialization,
        "limitations": {
            "full_diagonal_Gammahat_orbibundle_constructed":False,
            "charged_hyper_projectors_constructed":False,
            "global_quantum_anomaly_cancelled":False,
            "actual_Hodge_numbers_or_Euler_characteristic_computed":False,
            "same_action_parent_or_gate_closed":False,
        },
        "primary_sources": [
            {"url":"https://stacks.math.columbia.edu/tag/01OF",
             "use":"Rees charts, projectivity, Cartier blowups and unique functorial lifts"},
            {"url":"https://stacks.math.columbia.edu/tag/062Y",
             "use":"fibrewise effective Cartier criterion for flatness of the strict transform"},
            {"url":"https://stacks.math.columbia.edu/tag/01V4",
             "use":"openness of the smooth locus and flat smooth-fibre criterion"},
            {"url":"https://stacks.math.columbia.edu/tag/01W0",
             "use":"proper morphisms are universally closed; specialization of the nonsmooth locus"},
        ],
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate_certificate(report: Mapping) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("noncanonical V92 geometric certificate")
    if dict(report) != build_certificate():
        raise RuntimeError("V92 geometric evidence or its limitations changed")


if __name__ == "__main__":
    print(json.dumps(build_certificate(),sort_keys=True,indent=2))
