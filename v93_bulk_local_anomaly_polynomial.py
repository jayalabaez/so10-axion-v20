"""Full bare smooth-bulk Cartan fixed-locus polynomial for the V92 scout.

The ordinary normal/gauge characteristic sector is computed, not the missing
composite-R, localized-wall, ghost/regulator or relative differential theory.
"""
from __future__ import annotations

import copy
from functools import lru_cache
from itertools import combinations
from pathlib import Path

import sympy as sp
import susy_v91_multipath_g1_frontier_master_audit as common

ROOT = Path(__file__).resolve().parent
PINS = {
    "v92_route":("SUSY_V92_PROJECTORS_LENS_WCS_COMPACT_DECK_ROOT_AUDIT.json",
                 "3d4365681c9ebdbcbda6d9d57377a1046a6ab00b3a8b1b2290f2858a7ee4f4fb"),
    "v92_master":("SUSY_V92_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
                  "e38e8b58d4f86e00271402c9580919a092e024b737a4fc5290e4d20709b5aae8"),
    "v70":("SUSY_V70_SPIN11_LOCALIZED_PARENT_SPIN_FLAVOR_COMPLETION_AUDIT.json",
           "3e7b8e53916fbbc05bdcdf9632bcf4359aa4888b037df775c37d8d7d2551b228"),
    "v71":("SUSY_V71_SPIN11_NORMAL_BUNDLE_EQUIVARIANT_GS_AUDIT.json",
           "0162828ebd2b1e28d4fcbcf4ea1e6c61178d305cec79abd6d36a55719bb0f1ea"),
    "v90":("SUSY_V90_EXTERNAL_C8_QUOTIENT_DAIFREED_REES_EQUIVARIANCE_AUDIT.json",
           "ec095daa641345934d285a56a1916bf701352ee5cb113018296487ade36b966f"),
}
E = sp.symbols("e1:6")
f,x,p = sp.symbols("f x p")
VARIABLES = E+(f,x,p)
POINTS = ("z00","z11","z10","z01")
Z4 = tuple(tuple(sp.Rational(v) for v in row) for row in (
    ("3/8","1/8","-7/64","-11/192"),
    ("1/8","-1/8","-5/64","11/192"),
    ("-1/8","-1/8","5/64","11/192"),
    ("-3/8","1/8","7/64","-11/192")))


def index_component(charge, coeffs):
    """[Ahat(T4) exp(charge) sum_j c_j*x^j]_6; charge is a 2-form."""
    c0,c1,c2,c3 = coeffs
    return sp.expand(c0*(charge**3/6-charge*p/24)
                     +c1*x*(charge**2/2-p/24)+c2*x*x*charge+c3*x**3)


def vector_weights():
    rows = [{"weight":0,"Q":0,"W":1}]
    for i,e in enumerate(E):
        for sign in (1,-1):
            rows.append({"weight":sign*e,"Q":sign%4,"W":1 if i<2 else -1})
    return rows


def adjoint_weights():
    return [{"weight":a["weight"]+b["weight"],"Q":(a["Q"]+b["Q"])%4,
             "W":a["W"]*b["W"]} for a,b in combinations(vector_weights(),2)]


def coefficients_at(point,row,m=0):
    phase = (row["Q"]+m)%4
    if point=="z00":
        return Z4[phase]
    if point=="z11":
        return Z4[(phase+(0 if row["W"]==1 else 2))%4]
    if point not in ("z10","z01"):
        raise ValueError("unknown fixed stratum")
    eta = row["W"]*(-1)**phase
    # Each original-cover point is half the single downstairs C2 orbit.
    return (sp.Rational(eta,8),0,sp.Rational(-eta,64),0)


def singlet_polynomials(witness):
    out = {point:sp.Integer(0) for point in POINTS}
    for blockrow in witness["direct_sum_blocks"]:
        b = blockrow["certificate"]
        q = b["q_magnitude"]
        copies = blockrow["copies"]
        for point in POINTS:
            data = b["strata"][point]
            if data["order"]==4:
                counts = data["plus_eigenphase_multiplicities_m0123"]
                coeffs = [sum(n*Z4[m][j] for m,n in enumerate(counts)) for j in range(4)]
            else:
                matrix = sp.Matrix([[sp.sympify(z) for z in row] for row in data["plus_matrix"]])
                if matrix**2!=sp.eye(matrix.rows):
                    raise RuntimeError("noninvolutive C2 singlet matrix")
                coeffs = (sp.trace(matrix)/8,0,-sp.trace(matrix)/64,0)
            out[point] += copies*index_component(q*f,coeffs)
    return {point:sp.expand(poly) for point,poly in out.items()}


def charged_polynomials():
    out={point:sp.Integer(0) for point in POINTS}
    for point in POINTS:
        for m,q in ((3,6),(0,4),(1,6)):
            for row in vector_weights():
                out[point]+=index_component(row["weight"]+q*f,coefficients_at(point,row,m))
        for row in adjoint_weights():
            out[point]-=index_component(row["weight"],coefficients_at(point,row))
        # The ordinary untwisted additional U1 gaugino is gauge neutral.
        out[point]-=index_component(0,coefficients_at(point,{"Q":0,"W":1}))
    return {point:sp.expand(poly) for point,poly in out.items()}


def constant_mode_gauge_polynomial(witness):
    out=sp.Integer(0)
    rows=[]
    for m,q in ((3,6),(0,4),(1,6)):
        for row in vector_weights():
            if row["W"]!=1:
                continue
            phase=(row["Q"]+m)%4
            if phase in (0,3):
                sign=1 if phase==0 else -1
                charge=sign*(row["weight"]+q*f)
                rows.append({"sector":"11","m":m,"charge":str(charge)})
                out+=charge**3/6-charge*p/24
    for row in adjoint_weights():
        if row["W"]==1 and row["Q"]==3:
            charge=row["weight"]
            rows.append({"sector":"Sigma","charge":str(charge)})
            out+=charge**3/6-charge*p/24
    # Unbroken vector gauginos form a real adjoint and have zero odd traces.
    for q in witness["constant_N1_signed_continuous_charges"]:
        rows.append({"sector":"singlet","charge":str(q*f)})
        out+=(q*f)**3/6-q*f*p/24
    return sp.expand(out),rows


def sparse(poly):
    return [{"powers":list(m),"coefficient":str(c)} for m,c in sp.Poly(poly,*VARIABLES).terms() if c]


def generalized_bulk_GS_span(poly):
    """Generous necessary span: ignore lattice coefficients and quantization.

    Any product of a bulk invariant 4-form and an Abelian wall 2-form is in
    this span. The physical two tensor sources form only a subspace of it.
    """
    t=sum(E)
    h2=sum(e*e for e in E)
    basis=[sp.expand(y*z) for y in (x,f,t) for z in (p+x*x,h2,f*f)]
    monomials=sorted(set().union(*(set(sp.Poly(z,*VARIABLES).monoms()) for z in basis+[poly])))
    vectors=[sp.Poly(z,*VARIABLES).as_dict() for z in basis+[poly]]
    matrix=sp.Matrix([[v.get(m,0) for v in vectors[:-1]] for m in monomials])
    target=sp.Matrix([vectors[-1].get(m,0) for m in monomials])
    return {"basis":[str(z) for z in basis],"basis_rank":matrix.rank(),
            "augmented_rank":matrix.row_join(target).rank(),
            "in_generous_bulk_invariant_product_span":matrix.rank()==matrix.row_join(target).rank(),
            "ignored_constraints":"fixed a,b,c lattice coefficients, integral periods and full wall descent",
            "physical_bulk_GS_span_is_subset":True}


def formal_local_two_axion_target(poly):
    """Polynomial descent target only; no periodic axion/action is constructed."""
    gauge_only=sp.expand(poly.subs(x,0))
    if sp.expand(gauge_only.subs(f,0))!=0:
        raise RuntimeError("an irreducible pure Spin11-wall polynomial remains")
    A=sp.cancel((poly-gauge_only)/x)
    B=sp.cancel(gauge_only/f)
    if sp.expand(poly-x*A-f*B)!=0:
        raise RuntimeError("formal Abelian factorization failed")
    return {"normal_shift_four_form_A":str(sp.expand(A)),"U1_shift_four_form_B":str(sp.expand(B)),
            "identity":"I6=x*A4+f*B4",
            "local_formal_counterterm":"-a_L*A4 + phi_minus*B4/8, with delta a_L=epsilon_L and delta phi_minus=-8*epsilon_8",
            "local_descent_algebra_identity_verified":True,
            "new_normal_axion_is_required_in_this_formal_ansatz":A!=0,
            "periodicity_integrality_or_relative_differential_completion_constructed":False,
            "quantum_counterterm_accepted":False}


def conditional_visible_gauge_slice(v90,witness,bulk_integrated):
    """Existing visible content, no assignment of unknown normal charges.

    The gauge-only integrated anomaly does not depend on wall placement.
    Displaying the entire wall polynomial at z00 is a new explicit placement
    candidate, not proof of its missing tangential wall representations.
    """
    repair=v90["charged_neutral_and_compensator_repair"]
    table={row["field"]:row for row in repair["continuous_charge_table"]}
    t=sum(E)
    family=[a+b-t/2 for a,b in combinations(E,2)]+[t/2-e for e in E]+[-t/2]
    if (table["F_i"]["continuous_U1_8_charge"],table["D"]["continuous_U1_8_charge"],
        table["Dbar"]["continuous_U1_8_charge"],table["P_A"]["continuous_U1_8_charge"])!=(-3,6,-2,6):
        raise RuntimeError("conditional wall charge table changed")
    wall_charges=3*[w-3*f for w in family]+[e+6*f for e in E]+[-e-2*f for e in E]
    wall_charges += [6*f,t+6*f,-t-6*f]
    wall=sp.expand(sum(z**3/6-z*p/24 for z in wall_charges))
    expected_wall=-16*f*sum(e*e for e in E)+16*f*f*t-sp.Rational(20,3)*f**3+sp.Rational(59,12)*f*p
    if sp.expand(wall-expected_wall)!=0:
        raise RuntimeError("wall gauge-only polynomial mismatch")
    shadow=repair["visible_zero_mode_conditional_shadow"]
    keys=shadow["tensor_order"]
    out=dict.fromkeys(keys,0)
    rows=copy.deepcopy(shadow["signed_component_rows"])
    for q in witness["constant_N1_signed_continuous_charges"]:
        rows.append({"field":"new_singlet","q":q,"copies":1,"dim":1,"twoT3":0,"twoT2":0,"y6":0,"X":0})
    for r in rows:
        n,q,d,y,z=(r[k] for k in ("copies","q","dim","y6","X"))
        out["A3"]+=n*q*r["twoT3"]
        out["A2"]+=n*q*r["twoT2"]
        out["F_Y6_squared"]+=n*d*q*y*y
        out["F_X_squared"]+=n*d*q*z*z
        out["TrF"]+=n*d*q
        out["TrF_cubed"]+=n*d*q**3
        out["F_squared_Y6"]+=n*d*q*q*y
        out["F_squared_X"]+=n*d*q*q*z
        out["F_Y6_X"]+=n*d*q*y*z
    if list(out.values())!=[-32,-24,-816,-576,-68,1408,96,384,96]:
        raise RuntimeError("full conditional visible tensor mismatch")
    full=sp.expand(bulk_integrated+wall)
    purely_abelian=full.subs({e:0 for e in E})
    if sp.expand(purely_abelian-out["TrF_cubed"]*f**3/6+out["TrF"]*f*p/24)!=0:
        raise RuntimeError("Cartan and SM component traces disagree")
    # Independent pullback: e1,e2=weak roots+3Y6+2X,
    # e3,e4,e5=color roots-2Y6+2X. No SU2/SU3 curvature is hidden in Y6,X.
    Y,X=sp.symbols("Y X")
    pulled=sp.expand(full.subs({e:(3*Y+2*X if i<2 else -2*Y+2*X) for i,e in enumerate(E)}))
    expected=(out["TrF_cubed"]*f**3/6-out["TrF"]*f*p/24
              +out["F_Y6_squared"]*f*Y*Y/2+out["F_X_squared"]*f*X*X/2
              +out["F_squared_Y6"]*f*f*Y/2+out["F_squared_X"]*f*f*X/2
              +out["F_Y6_X"]*f*Y*X)
    if sp.expand(pulled-expected)!=0:
        raise RuntimeError("SM Abelian pullback does not match component census")
    return {"wall_gauge_only_polynomial":str(wall),"full_integrated_gauge_only_polynomial":str(full),
            "visible_tensor_order":keys,"visible_tensor":list(out.values()),
            "SM_Abelian_pullback":str(pulled),"component_pullback_verified":True,
            "normal_curvature_set_to_zero_is_not_normal_charge_zero_assignment":True,
            "wall_placement_for_a_local_display":"conditional new z00 placement of P_A and other local drivers together with the V90 split families/rank/compensator candidate",
            "integrated_result_depends_on_wall_placement":False,
            "bulk_Phi_pair_and_nine_modes_included_once":True,
            "full_localized_normal_polynomial_constructed":False,
            "nonzero_continuous_anomaly_erased_by_spontaneous_breaking":False,
            "bare_continuous_U1_requires_matching_or_additional_cancellation":True}


@lru_cache(maxsize=1)
def exact_calculation():
    bound={key:common.load_bound(ROOT/name,core) for key,(name,core) in PINS.items()}
    p92=bound["v92_route"]["smooth_singlet_projectors"]
    if p92["core_sha256"]!=common.canonical_sha(p92):
        raise RuntimeError("noncanonical nested projector input")
    expected_phases=[(r["hyper"],r["m"]) for r in bound["v70"]["fixed_locus_twist_ledger"]["selected_integer_m301_11s"]]
    if expected_phases!=[("A",3),("B",0),("C",1)]:
        raise RuntimeError("charged projector phases changed")
    input_series=bound["v71"]["spin_half_equivariant_index"]["rows"]
    if tuple(tuple(sp.Rational(z) for z in row["series_coefficients_1_x_x2_x3"]) for row in input_series)!=Z4:
        raise RuntimeError("V71 normal index convention changed")
    witness=p92["eleven_mode_normal_aligned_witness"]
    singlets=singlet_polynomials(witness)
    charged=charged_polynomials()
    # The inherited standard untwisted gravity/tensor complex, not a new R-curvature calculation.
    gravity={point:(sp.Rational(42,192)*x**3-sp.Rational(18,192)*x*p)
             if point in ("z00","z11") else sp.Integer(0) for point in POINTS}
    total={point:sp.expand(singlets[point]+charged[point]+gravity[point]) for point in POINTS}
    integrated=sp.expand(sum(total.values()).subs(x,0))
    zero,zero_rows=constant_mode_gauge_polynomial(witness)
    if sp.expand(integrated-zero)!=0:
        raise RuntimeError("fixed-point sum does not match independent constant-mode anomaly")
    if any(sp.expand(total[point].subs({e:0 for e in E}).subs(f,0)+x*(p+x*x)/8)!=0 for point in ("z00","z11")):
        raise RuntimeError("inherited V92 normal alignment not reproduced")
    coeff=sp.Poly(total["z00"],*VARIABLES).coeff_monomial(x*E[0]*E[1])
    if coeff!=sp.Rational(1,2):
        raise RuntimeError("off-diagonal nonbulk-invariant witness changed")
    span=generalized_bulk_GS_span(total["z00"])
    if span["in_generous_bulk_invariant_product_span"]:
        raise RuntimeError("bare-bulk ordinary GS obstruction disappeared")
    normal_A=sp.cancel((total["z00"]-total["z00"].subs(x,0))/x)
    c2=sp.expand(sum(a*b for a,b in combinations(E,2)))
    instanton_four_form=sp.expand(normal_A.subs({f:0,x:0,p:0}))
    if sp.expand(instanton_four_form-c2/2)!=0:
        raise RuntimeError("isolated normal-axion half-period screen changed")
    return {
        "variables":[str(z) for z in VARIABLES],
        "normalization":"e_i are orthogonal Spin11 Cartan Chern roots, f=F8/(2pi) in covering de Rham normalization, x=c1(normal), p=p1(T4); hyper-positive index convention. On Spin^c(11) gauge bundles f=c1(det)/2 need not be independently integral.",
        "C2_counting":"z10,z01 each have cover weight1/2; the physical C2 orbit is their sum",
            "per_stratum":{point:{"singlet":str(singlets[point]),"charged_and_U1_gaugino":str(charged[point]),
                              "gravity_tensor":str(gravity[point]),"total":str(total[point]),
                              "total_sparse_coefficients":sparse(total[point]),
                              "formal_local_axion_target":formal_local_two_axion_target(total[point])}
                       for point in POINTS},
        "compact_C4_formula":{
            "definition":"t=sum e_i, h2=sum e_i^2; at z11 replace t by e1+e2-e3-e4-e5",
            "polynomial":"f*h2+4*f^2*t-f*x*t+x*(t^2-h2)/4+377*f^3/3+39*f^2*x/2-47*f*p/48-87*f*x^2/16-x*(p+x^2)/8"},
        "compact_C2_cover_formula":"f*(e1^2+e2^2-e3^2-e4^2-e5^2)-5*f^3-f*p/16-3*f*x^2/16",
        "conditional_visible_gauge_slice":conditional_visible_gauge_slice(bound["v90"],witness,integrated),
        "zero_mode_index_crosscheck":{"integrated_fixed_gauge_polynomial":str(integrated),
                                      "independently_projected_zero_mode_polynomial":str(zero),
                                      "constant_mode_rows":zero_rows,"exact_difference":"0"},
        "ordinary_bulk_GS_obstruction":{
            "at_z00":span,
            "simple_separating_functional":"coefficient of x*e1*e2",
            "bare_bulk_value":str(coeff),"every_generous_bulk_GS_basis_value":"0",
            "C2_cover_separating_functional":"coefficient(f*e1^2)-coefficient(f*e3^2)",
            "C2_cover_bare_bulk_value":"2",
            "C2_every_bulk_invariant_product_value":"0",
            "independent_normal_axion_period_screen":{
                "assumptions":"an independently period-one ordinary normal axion with integer normal-shift charges and integer SU5 instanton levels",
                "test_background":"spin S4 with the basic SU2 bundle embedded in SU5, c2(SU5)=1; f=x=p1(T4)=0",
                "normal_four_form_restriction":"c2(SU5)/2",
                "period_shift_one_exponent":"-1/2",
                "period_shift_one_phase":"-1",
                "standalone_period_one_normal_axion_works":False,
                "integer_level_axions_can_sum_to_required_half_integer_coefficient":False,
                "all_extended_tangential_or_coupled_GS_completions_excluded":False,
                "boundary":"This excludes only the independently periodic local axion ansatz. Extended periods/normal lifts, coupled global GS data and added wall matter are not excluded."},
            "off_diagonal_normal_Spin11_Cartan_terms_survive_new_U1_singlets":True,
            "local_U5_invariant_rewrite":"x*((sum e_i)^2-sum(e_i^2))/4",
            "claim_scope":"bare smooth bulk with the V92 lifts; not a no-go for added wall fermions, normal axions or more general inflow",
        },
    }


def build_certificate():
    # Verify immutable dependencies even when exact symbolic arithmetic is cached.
    for name,core in PINS.values():
        common.load_bound(ROOT/name,core)
    return {"schema":"v93_bulk_local_anomaly_polynomial_v1",
            "status":"EXACT_BARE_SMOOTH_BULK_LOCAL_POLYNOMIAL__ORDINARY_BULK_GS_ALONE_INSUFFICIENT",
            "input_core_hashes":{k:v[1] for k,v in PINS.items()},
            "calculation":copy.deepcopy(exact_calculation()),
            "boundary":{"full_localized_wall_fields_included":False,
                        "composite_R_curvature_and_all_tangential_backgrounds_included":False,
                        "full_regulated_KK_or_Dai_Freed_anomaly_computed":False,
                        "formal_axion_target_is_a_quantized_action":False,
                        "all_gates_closed":False},
            "primary_sources":[
                {"url":"https://arxiv.org/abs/hep-th/0612212","use":"fixed-point gauge/normal anomalies, bulk-invariant inflow restriction and zero-mode index check; sections3-4"},
                {"url":"https://arxiv.org/abs/hep-th/0602155","use":"N1 hyper partner and adjoint orbifold phases; equations44-45"},
                {"url":"https://arxiv.org/abs/1808.01334","use":"bulk GS polynomial versus differential global anomaly completion; equations2.5-2.10"}]}


def validate_certificate(report):
    if report!=build_certificate():
        raise RuntimeError("bare bulk polynomial or its scope changed")
