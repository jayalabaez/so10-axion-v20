"""Exact Jacobian/section audit of the actual V91 member resolved in V92.

The nonsplit I2* assertion concerns the Jacobian's codimension-one Tate data.
It does not identify a global gauge group, prove a Mordell-Weil rank, transfer
Jacobian Hodge numbers to a torsor, or construct a six-dimensional spectrum.
"""
from __future__ import annotations

import copy
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import sympy as sp

import v92_deck_root_geometry_certificate as geometry


ROOT = Path(__file__).resolve().parent
V92_PATH = ROOT / "SUSY_V92_PROJECTORS_LENS_WCS_COMPACT_DECK_ROOT_AUDIT.json"
V92_CORE = "3d4365681c9ebdbcbda6d9d57377a1046a6ab00b3a8b1b2290f2858a7ee4f4fb"
SCHEMA = "v93_actual_quartic_jacobian_section_compatibility_v1"


def canonical_sha(value: Any) -> str:
    return geometry.canonical_sha(value)


def load_bound_inputs() -> tuple[dict, dict]:
    """Lineage is freshly checked even when the pure algebra cache is warm."""
    payload = geometry.load_payload()
    parent = json.loads(V92_PATH.read_text(encoding="utf-8"))
    if parent.get("core_sha256") != V92_CORE or canonical_sha(parent) != V92_CORE:
        raise RuntimeError("V93 requires the exact canonical V92 parent")
    saved = parent["compact_deck_root_geometry"]
    if saved["coefficient_payload_sha256"] != canonical_sha(payload):
        raise RuntimeError("V92 compact member does not bind the V91 coefficients")
    if saved["coefficient_payload"] != payload:
        raise RuntimeError("V92 saved coefficients differ from the canonical member")
    return payload, parent


def quartic_invariants(a, b, c, d, e) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    I = sp.expand(12*a*e - 3*b*d + c*c)
    J = sp.expand(72*a*c*e + 9*b*c*d - 27*a*d*d - 27*b*b*e - 2*c**3)
    return I, J, sp.expand(4*I**3-J**2)


def polynomial_data(poly: sp.Expr, variables: tuple) -> dict:
    p = sp.Poly(poly, *variables, domain=sp.QQ)
    data = [[list(powers), str(coefficient)] for powers, coefficient in p.terms()]
    return {"variable_order": [str(x) for x in variables],
            "degrees": [int(p.degree(x)) for x in variables],
            "total_degree": int(p.total_degree()), "term_count": len(data),
            "rational_term_list_sha256": canonical_sha(data)}


def order_at(poly: sp.Expr, variable: sp.Symbol) -> int:
    p = sp.Poly(poly, variable)
    if p.is_zero:
        raise ValueError("the zero polynomial has no finite vanishing order")
    return min(power[0] for power, coefficient in p.terms() if coefficient != 0)


def universal_algebra() -> dict:
    z, ell, p0, p1, p4 = sp.symbols("z ell p0 p1 p4")
    I, J, D = quartic_invariants(z*ell+z*z*p0, z*z*p1, -2*z*ell,
                                 0, z*ell+z*z*p4)
    E = ell+z*p4
    R = sp.cancel(D/(27*z**8*E))
    if not R.is_polynomial(z, ell, p0, p1, p4):
        raise RuntimeError("universal discriminant factor is not polynomial")
    if sp.expand(D-27*z**8*E*R) != 0:
        raise RuntimeError("universal discriminant reconstruction failed")
    B2 = 144*z*ell
    B4 = sp.expand((B2**2-1296*I)/24)
    B6 = sp.expand((-23328*J-B2**3+36*B2*B4)/216)
    A2 = sp.cancel(B2/(4*z))
    A4 = sp.cancel(B4/(2*z**3))
    A6 = sp.cancel(B6/(4*z**5))
    if any(not a.is_polynomial(z,ell,p0,p1,p4) for a in (A2,A4,A6)):
        raise RuntimeError("Tate reconstruction is not regular")
    monodromy = sp.factor((A4**2-4*A2*A6).subs(z,0))
    expected = 324**2*ell**2*(p0-p1+p4)*(p0+p1+p4)
    if sp.expand(monodromy-expected) != 0:
        raise RuntimeError("Tate monodromy identity failed")
    # Verify Weierstrass conventions rather than assuming a discriminant factor.
    f, g = -27*I, -27*J
    if sp.expand(-16*(4*f**3+27*g**2)-16*3**9*D) != 0:
        raise RuntimeError("Weierstrass discriminant normalization failed")
    return {"symbols": (z,ell,p0,p1,p4), "I":I, "J":J, "D":D,
            "E":E, "R":sp.expand(R), "A2":A2, "A4":A4, "A6":A6,
            "monodromy":monodromy}


def boundary_squareclasses(payload: Mapping[str, Any]) -> dict:
    m = geometry.expressions(payload)
    symbols = m["symbols"]
    s,t,r0,r1,U,V = (symbols[n] for n in ("s","t","r0","r1","U","V"))
    x = sp.symbols("x")
    polynomials = [sp.expand(m["P"].subs(
        {s:0,t:1,r0:x,r1:1,U:sign,V:1}, simultaneous=True)) for sign in (1,-1)]
    degrees = [int(sp.degree(p,x)) for p in polynomials]
    leading = [int(sp.Poly(p,x).LC()) for p in polynomials]
    discriminants = [int(sp.discriminant(p,x)) for p in polynomials]
    resultant = int(sp.resultant(*polynomials,x))
    if degrees != [4,4] or not all(leading+discriminants+[resultant]):
        raise RuntimeError("simple disjoint degree-four boundary squareclasses not proved")
    product = sp.expand(polynomials[0]*polynomials[1])
    if sp.degree(sp.gcd(product,sp.diff(product,x)),x) != 0:
        raise RuntimeError("boundary product is not squarefree")
    return {"coordinate": "x=r0/r1 on S, t=r1=1",
            "P_plus":str(polynomials[0]), "P_minus":str(polynomials[1]),
            "product":str(product), "degrees":degrees,
            "leading_coefficients":leading, "discriminants":discriminants,
            "resultant":resultant, "squareclass_rank_over_C_x":2,
            "reason": "Each polynomial has four simple roots; their root sets are disjoint. Each polynomial and their product has an odd valuation and is not a square in C(x).",
            "no_root_at_infinity":True,
            "individual_double_cover_genera":[1,1],
            "product_double_cover_genus":3}


def _bidegree(poly: sp.Expr, variables: tuple) -> list[int]:
    weights = ((1,0),(1,4),(0,1),(0,1))
    all_degrees = {tuple(sum(powers[j]*weights[j][axis] for j in range(4))
                         for axis in range(2))
                   for powers,_ in sp.Poly(poly,*variables).terms()}
    if len(all_degrees) != 1:
        raise RuntimeError("global polynomial is not homogeneous in the F4 Cox grading")
    return list(all_degrees.pop())


@lru_cache(maxsize=4)
def _algebra_json(payload_json: str) -> str:
    """Cache only exact pure computations, return immutable canonical JSON."""
    payload = json.loads(payload_json)
    m = geometry.expressions(payload)
    c, sym = m["coefficients"], m["symbols"]
    if c["p2"] != 0 or c["p3"] != 0:
        raise RuntimeError("this factorization requires the actual p2=p3=0 member")
    s,t,r0,r1 = (sym[n] for n in ("s","t","r0","r1"))
    a = universal_algebra()
    z,ell,p0,p1,p4 = a["symbols"]
    substitution = {z:s,ell:c["L"],p0:c["p0"],p1:c["p1"],p4:c["p4"]}
    I,J,D,E,R = [sp.expand(a[n].subs(substitution, simultaneous=True))
                 for n in ("I","J","D","E","R")]
    if sp.expand(D-27*s**8*E*R) != 0:
        raise RuntimeError("actual global factorization failed")
    degrees = {n:_bidegree(p,(s,t,r0,r1))
               for n,p in zip(("I","J","D","E","R"),(I,J,D,E,R))}
    if degrees != {"I":[8,24],"J":[12,36],"D":[24,72],"E":[3,12],"R":[13,60]}:
        raise RuntimeError("unexpected discriminant divisor classes")
    T,X = sp.symbols("T X")
    affine = {s:1,r1:1,t:T,r0:X}
    ia,ja,da,ea,ra = [sp.expand(p.subs(affine,simultaneous=True)) for p in (I,J,D,E,R)]
    constant,factors = sp.factor_list(da,T,X)
    if len(factors) != 2 or sorted(int(n) for _,n in factors) != [1,1]:
        raise RuntimeError("the two reduced affine discriminant factors were not recovered")
    reconstructed = constant*sp.prod(p**n for p,n in factors)
    if sp.expand(da-reconstructed) != 0:
        raise RuntimeError("affine rational factorization did not reconstruct D")
    factor_sets = {sp.Poly(p,T,X).monic().as_expr() for p,_ in factors}
    if factor_sets != {sp.Poly(p,T,X).monic().as_expr() for p in (ea,ra)}:
        raise RuntimeError("computed factors differ from E and R")
    gcd_pairs = {"I_J":(ia,ja),"I_D":(ia,da),"J_D":(ja,da),
                 "D_dD_dT":(da,sp.diff(da,T)),"D_dD_dX":(da,sp.diff(da,X))}
    gcds = {name:sp.Poly(sp.gcd(*pair),T,X).monic().as_expr()
            for name,pair in gcd_pairs.items()}
    if any(value != 1 for value in gcds.values()):
        raise RuntimeError("affine discriminant has an unclassified repeated/additive factor")
    # The dense affine omits exactly the divisors S and r1=0. Audit both.
    infinity = sp.factor(D.subs({r1:0,r0:1},simultaneous=True))
    expected_inf = -27*s**8*t**6*(t*t+s*s)**2*(256*t**6+27*s*s*(t*t+s*s)**2)
    if sp.expand(infinity-expected_inf) != 0 or infinity == 0:
        raise RuntimeError("r1=0 boundary discriminant changed or vanishes identically")
    actual_orders = [order_at(p,s) for p in (I,J,D)]
    if actual_orders != [2,3,8]:
        raise RuntimeError("actual S Kodaira orders changed")
    boundary = boundary_squareclasses(payload)
    leading = [sp.factor(sp.Poly(p,s).nth(n)) for p,n in zip((I,J,D),actual_orders)]
    bisection = sp.expand(m["Q"].subs({sym["U"]:0,sym["V"]:1},simultaneous=True))
    if order_at(bisection,s) != 1:
        raise RuntimeError("U=0 no longer gives the ramified irreducible bisection")
    out = {
        "universal_algebra": {
            "quartic_coefficients": ["z*ell+z^2*p0","z^2*p1","-2*z*ell","0","z*ell+z^2*p4"],
            "I":str(sp.factor(a["I"])),"J":str(sp.factor(a["J"])),
            "normalized_discriminant":"D=4*I^3-J^2=27*z^8*(ell+z*p4)*R",
            "R":str(a["R"]), "Jacobian_equation":"y^2=x^3-27*I*x-27*J",
            "Weierstrass_discriminant_factor_relative_to_D":16*3**9,
            "Tate_A2":str(a["A2"]),"Tate_A4":str(a["A4"]),"Tate_A6":str(a["A6"]),
            "Tate_convention":"a1=a3=0; a2=z*A2,a4=z^3*A4,a6=z^5*A6; c4=1296*I,c6=23328*J",
            "monodromy_discriminant":str(a["monodromy"]),
            "factorization_and_Tate_identities_verified":True,
        },
        "global_discriminant": {
            "factorization":"D=27*s^8*E*R, E=L+s*p4; R uses the displayed universal polynomial and bound coefficients",
            "divisor_classes_in_S_F":degrees,"S_multiplicity":8,
            "main_chart":"s=r1=1, T=t, X=r0; t=0 and r0=0 are included",
            "E_affine":str(ea),"E_affine_polynomial":polynomial_data(ea,(T,X)),
            "R_affine_polynomial":polynomial_data(ra,(T,X)),
            "D_affine_polynomial":polynomial_data(da,(T,X)),
            "Q_irreducible_factor_count":2,"Q_factor_multiplicities":[1,1],
            "Q_irreducibility_claims_geometric_irreducibility":False,
            "normalized_polynomial_gcds":{k:str(v) for k,v in gcds.items()},
            "all_off_S_geometric_discriminant_components_reduced":True,
            "all_off_S_generic_orders_f_g_D":[0,0,1],
            "all_off_S_generic_Kodaira_types":"I1",
            "additional_off_S_nonabelian_discriminant_divisor":False,
            "r1_zero_restriction_r0_one":str(infinity),
            "r1_zero_is_discriminant_divisor":False,
            "codimension_one_cover_complete":True,
            "cover_argument":"The complement of s=r1=1 in F4 is S union {r1=0}. Both have separately computed generic restrictions. No codimension-two fiber classification is asserted.",
        },
        "S_Jacobian_fiber": {
            "actual_orders_I_J_D":actual_orders,
            "actual_leading_coefficients_in_s":[str(p) for p in leading],
            "minimal":True,"Kodaira_type":"I2* non-split",
            "Tate_gauge_algebra":"B5 = so(11)","global_gauge_group_proved":False,
            "monodromy_squareclass":"P_plus*P_minus in C(x)^*/C(x)^{*2}",
            "Tate_monodromy_square_prefactor":324**2,
            "boundary_squareclasses":boundary,
            "applies_to":"Jacobian generic codimension-one fiber, not a completed torsor F-theory spectrum",
        },
        "torsor_section_obstruction": {
            "field":"K=C(F4) subset C(x)((s)), using t=r1=1 near S",
            "generic_fiber_is_smooth_genus_one":True,
            "valuation_proof":[
                "Normalize U,V in C(x)[[s]] with at least one a unit; weighted scaling sends W to the square-scaled coordinate.",
                "If U^2-V^2 is a unit, s*(U^2-V^2)^2+s^2*P has valuation one and cannot equal W^2.",
                "Otherwise U=epsilon*V modulo s, epsilon=+1 or -1, and V is a unit. The first term has valuation at least three.",
                "The second term has valuation two with nonzero leading coefficient V^4*P_epsilon. Reducing (W/s)^2 forces P_epsilon to be a square in C(x), contradicting the derived simple roots.",
                "Thus there is no point over the completion, hence none over K, and no rational section of the genus-one fibration. A resolution leaves its generic fiber unchanged.",
            ],
            "rational_section_exists":False,
            "bisection":"U=0: W^2=s*(L+s*p4)*V^4",
            "bisection_rhs_order_at_S":1,"bisection_degree":2,
            "index":2,"period":2,
            "period_index_reason":"The irreducible degree-two divisor bounds index by two. Index one would give a degree-one divisor and, by genus-one Riemann-Roch, a K-point. Period divides index; period one would trivialize the torsor.",
            "Jacobian_has_zero_section":True,
            "no_torsor_section_implies_Jacobian_MW_rank_zero":False,
        },
    }
    return json.dumps(out,sort_keys=True,separators=(",",":"))


def derive_member_certificate(payload: Mapping[str, Any]) -> dict:
    return json.loads(_algebra_json(json.dumps(dict(payload),sort_keys=True,separators=(",",":"))))


def double_cover_genus(base_genus: int, simple_branch_points: int) -> int:
    """Riemann-Hurwitz for a connected degree-two cover of smooth curves."""
    if (type(base_genus) is not int or type(simple_branch_points) is not int
            or base_genus < 0 or simple_branch_points < 0 or simple_branch_points % 2):
        raise ValueError("nonnegative genus and an even simple branch count required")
    result = 2*base_genus-1+simple_branch_points//2
    if result < 0:
        raise ValueError("these data cannot describe a connected double cover")
    return result


@lru_cache(maxsize=4)
def orthogonal_adjoint_branching(n: int = 11) -> tuple:
    """Exact matrix proof so(n+1)|so(n) = adj(so(n)) + standard(n)."""
    if type(n) is not int or n < 3:
        raise ValueError("this branching audit uses n>=3")
    entries = iter(sp.symbols(f"a0:{n*(n-1)//2}"))
    A = sp.zeros(n)
    for i in range(n):
        for j in range(i+1,n):
            A[i,j] = next(entries)
            A[j,i] = -A[i,j]
    v = sp.Matrix(sp.symbols(f"v0:{n}"))
    H = sp.diag(A,0)
    embed_vector = lambda w: sp.Matrix.vstack(
        sp.Matrix.hstack(sp.zeros(n),w), sp.Matrix.hstack(-w.T,sp.zeros(1)))
    M = embed_vector(v)
    reflection = sp.diag(*([1]*n+[-1]))
    checks = (H*M-M*H-embed_vector(A*v),
              reflection*H*reflection-H, reflection*M*reflection+M)
    if any(sp.expand(entry) != 0 for matrix in checks for entry in matrix):
        raise RuntimeError("orthogonal adjoint branching or involution identity failed")
    return (n*(n+1)//2,n*(n-1)//2,n,True,True)


def conditional_nonlocal_matter(boundary: Mapping[str,Any], target_count: int) -> dict:
    # Re-read the actual polynomials rather than trusting a reported branch count.
    x = sp.symbols("x")
    pp,pm = [sp.sympify(boundary[name],locals={"x":x}) for name in ("P_plus","P_minus")]
    product = sp.expand(pp*pm)
    branch_count = int(sp.degree(product,x))
    if (branch_count != 8 or sp.degree(sp.gcd(product,sp.diff(product,x)),x) != 0
            or not boundary["no_root_at_infinity"]):
        raise RuntimeError("the actual simple eight-point monodromy cover is not certified")
    base_genus = 0  # S is the negative section P1 of the explicitly fixed F4 base.
    cover_genus = double_cover_genus(base_genus,branch_count)
    multiplicity = cover_genus-base_genus
    dim_parent,dim_fixed,dim_vector,action_ok,involution_ok = orthogonal_adjoint_branching()
    # Independent intersection-form check, Table E of Grassi-Morrison.
    S_squared,K_dot_S = -4,2
    intersection_prediction = -sp.Rational(7,2)*K_dot_S-sp.Rational(5,2)*S_squared
    if intersection_prediction != multiplicity or multiplicity != target_count:
        raise RuntimeError("conditional monodromy matter count fails its independent comparison")
    return {
        "status":"CONDITIONAL_JACOBIAN_NONLOCAL_MATTER_CONTRIBUTION__NOT_TORSOR_SPECTRUM",
        "base_curve":"S=P1 inside F4", "base_genus":base_genus,
        "cover_equation":"eta^2=P_plus*P_minus", "cover_degree":2,
        "simple_branch_point_count":branch_count, "cover_genus":cover_genus,
        "Riemann_Hurwitz":{"lhs_2g_cover_minus_2":2*cover_genus-2,
                           "rhs_2_times_2g_base_minus_2_plus_branch":2*(2*base_genus-2)+branch_count},
        "branching":"adj so(12) restricts to adj so(11) plus the real vector 11",
        "branching_dimensions":[dim_parent,dim_fixed,dim_vector],
        "branching_matrix_check":"[diag(A,0),J(v)]=J(A*v), J(v)=[[0,v],[-v^T,0]]; reflection diag(I11,-1) fixes diag(A,0) and negates J(v)",
        "vector_action_identity_verified":action_ok,
        "involution_eigenspaces_verified":involution_ok,
        "standard_nonlocal_matter_rule":"g_cover-g_base full hypermultiplets in the minus-eigenspace representation",
        "conditional_nonlocal_vector11_full_hypermultiplets":multiplicity,
        "conditional_adjoint_full_hypermultiplets":base_genus,
        "intersection_crosscheck":{"S_squared":S_squared,"K_dot_S":K_dot_S,
                                    "formula":"(-7*K/2-5*S/2).S", "value":int(intersection_prediction)},
        "V91_scout_vector_multiplicity":target_count,
        "matches_nonabelian_multiplicity_only":multiplicity==target_count,
        "assumptions":[
            "standard Jacobian F-theory interpretation with the usual section-preserving D6-to-B5 monodromy and admissible fiber contraction",
            "usual resolved elliptic Calabi-Yau wrapped-brane/nonlocal-matter rule; this is not a proof that its global prerequisites hold for the compact Jacobian",
        ],
        "additional_codimension_two_matter_excluded":False,
        "U1_charges_determined":False,
        "actual_torsor_physical_contraction_verified":False,
        "Jacobian_MW_rank_or_height_determined":False,
        "full_V91_spectrum_realized":False,
        "sources":["AspinwallKatzMorrison2000 section3, equation6 and preceding so(2k) paragraph",
                   "GrassiMorrison2000 Theorem8.2, Proposition8.9 and TableE Spin11 row"],
    }


def primary_sources() -> list[dict]:
    return [
        {"id":"Fisher2022","url":"https://arxiv.org/abs/2208.14977",
         "role":"Section 2 gives binary quartic I,J and y^2=x^3-27Ix-27J for its Jacobian; only characteristic-zero invariant formulas are used."},
        {"id":"KatzMorrisonSchaferNamekiSully2011","url":"https://arxiv.org/abs/1106.3854",
         "role":"Kodaira/Tate orders and split versus nonsplit fiber classification; the Tate coordinates here are explicitly reconstructed."},
        {"id":"BraunMorrison2014","url":"https://arxiv.org/abs/1401.7844",
         "role":"Sections 2, 7 and 8 distinguish a genus-one fibration from its Jacobian, permit affine-component monodromies, and relate continuous U1 factors to Jacobian MW rank."},
        {"id":"AspinwallKatzMorrison2000","url":"https://arxiv.org/abs/hep-th/0002012",
         "role":"Section 3 derives the standard nonlocal hypermultiplet rule g_cover-g_base in the anti-invariant representation, explicitly including so(2k) to so(2k-1). Used conditionally for the Jacobian interpretation."},
        {"id":"GrassiMorrison2000","url":"https://arxiv.org/abs/math/0005196",
         "role":"Theorem 8.2, Proposition 8.9 and Table E give the monodromy contribution, orthogonal adjoint branching, and independent Spin11 intersection formula. No full-spectrum theorem is applied to the torsor."},
    ]


def build_certificate() -> dict:
    payload,parent = load_bound_inputs()
    derived = derive_member_certificate(payload)
    target = parent["conditional_spectrum_geometry_target"]
    nonlocal_matter = conditional_nonlocal_matter(
        derived["S_Jacobian_fiber"]["boundary_squareclasses"],
        len(target["weight_census"]["vector_hyper_charge_magnitudes"]))
    report = {
        "schema":SCHEMA,
        "status":"PASS_EXACT_ACTUAL_JACOBIAN_CODIM1_AND_PERIOD2_TORSOR__MW_RANK_AND_SPECTRUM_OPEN",
        "input_core_hashes":{"v91":geometry.V91_CORE,"v92":V92_CORE},
        "coefficient_payload_sha256":canonical_sha(payload),
        "coefficient_payload":copy.deepcopy(payload),
        **derived,
        "conditional_Jacobian_nonlocal_matter":nonlocal_matter,
        "spectrum_compatibility":{
            "standard_Jacobian_B5_codimension_one_necessary_test_passes":True,
            "Spin11_global_form_established_by_Kodaira_algebra":False,
            "continuous_U1_requires_non_torsion_Jacobian_section":True,
            "Jacobian_Mordell_Weil_rank_computed":False,
            "Jacobian_Mordell_Weil_rank":None,
            "non_torsion_Jacobian_section_constructed":False,
            "torsor_bisection_is_proof_of_continuous_U1":False,
            "actual_height_pairing_constructed":False,
            "conditional_target_hodge_tuple":copy.deepcopy(target["necessary_hodge_tuple"]),
            "conditional_target_height_class_in_S_F":copy.deepcopy(target["conditional_height_class"]["class_in_S_F"]),
            "conditional_targets_are_actual_member_invariants":False,
            "actual_member_realizes_V91_scout":False,
            "actual_member_is_excluded_by_no_section_alone":False,
            "torsor_affine_component_monodromy_requires_separate_audit":True,
            "same_action_physical_completion":False,
        },
        "limitations":[
            "No Jacobian Mordell-Weil rank, independence, torsion subgroup or height pairing computation.",
            "The no-section theorem is for the torsor, not a prohibition on Jacobian sections or continuous U1 factors.",
            "P_plus and P_minus define independent local quadratic extensions. Torsor affine-component monodromy and its physical contraction cannot be inferred only from the Jacobian B5 label.",
            "No actual Hodge numbers, codimension-two matter, global gauge group, flux, diagonal R/bundle lift or full anomaly theory are constructed.",
            "All gates remain OPEN; no theory completion follows from these necessary geometry tests.",
        ],
        "primary_sources":primary_sources(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate_certificate(report: Mapping[str, Any]) -> None:
    expected = build_certificate()
    if dict(report) != expected:
        raise RuntimeError("V93 geometric compatibility certificate differs from fresh exact derivation")


if __name__ == "__main__":
    print(json.dumps(build_certificate(),indent=2,sort_keys=True))
