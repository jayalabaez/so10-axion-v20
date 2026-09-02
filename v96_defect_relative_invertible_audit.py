"""F96: a quantized inverse of the *restricted, reduced* defect anomaly.

The CS connection below is a background, not an integrated gauge field.  An
explicit spin-CS/ABK response is constructed on ordinary Spin3 x C4/C8.  Its
identification with inflow from the frozen microscopic action is NOT supplied.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as F
from math import gcd, lcm
from pathlib import Path
from typing import Mapping

import sympy as sp

import v95_defect_finite_inflow_audit as parent


ROOT = Path(__file__).resolve().parent
SCHEMA = "v96_restricted_defect_spin_CS_ABK_inverse_v1"
V95_ROUTE_PATH = ROOT / "SUSY_V95_WALL_KERNEL_FINITE_INFLOW_RANK_AUDIT.json"
V95_MASTER_PATH = ROOT / "SUSY_V95_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V95_ROUTE_CORE = "e8ed3aa98cc23726cd41d0b62bbfb8822253d7a9282f1184ba22a77956cb4729"
V95_MASTER_CORE = "7a20530db05af160ce76e1b5e297001befc5eafd3696a13ba9ac692bbe94dd88"
V95_DEFECT_CORE = "fb8b6a33de1a19a48dff70bee4592298b2f58205db2c36fbe29e39432812ee37"
canonical_sha = parent.canonical_sha


def portable_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_inputs() -> tuple[dict, dict, dict]:
    reports = []
    for path, core in ((V95_ROUTE_PATH, V95_ROUTE_CORE), (V95_MASTER_PATH, V95_MASTER_CORE)):
        report = json.loads(path.read_text(encoding="utf-8"))
        if report.get("core_sha256") != core or canonical_sha(report) != core:
            raise RuntimeError("F96 requires immutable canonical V95 route/master")
        reports.append(report)
    route, master = reports
    if master["input_core_hashes"]["v95_route"] != V95_ROUTE_CORE:
        raise RuntimeError("V95 route/master lineage mismatch")
    defect = route["finite_defect_inflow"]
    if defect.get("core_sha256") != V95_DEFECT_CORE or canonical_sha(defect) != V95_DEFECT_CORE:
        raise RuntimeError("bound V95 finite-defect core changed")
    for name in ("v95_defect_finite_inflow_audit.py", "test_v95_defect_finite_inflow_audit.py"):
        if portable_sha(ROOT / name) != route["artifact_hashes"][name]:
            raise RuntimeError("bound V95 source/test changed: " + name)
    if defect != parent.build_certificate():
        raise RuntimeError("V95 finite-defect fails fresh reconstruction")
    return route, master, defect


def check_n(n: int) -> None:
    if type(n) is not int or n not in (4, 8):
        raise ValueError("this proof and coordinate dictionary are bounded to n=4,8")


def torus_rho(n: int, charge: int, circle_spin: int = 0) -> F:
    check_n(n)
    if type(charge) is not int:
        raise ValueError("integer charge required")
    xi = parent.torus_spectrum(charge * (8 // n), circle_spin=circle_spin)
    neutral = parent.torus_spectrum(0, circle_spin=circle_spin)
    return F(xi["xi_exact"]) - F(neutral["xi_exact"])


def coordinates(n: int, lens_exponent: F, torus_exponent: F) -> tuple[int, int]:
    """Evaluation pair before the theorem establishes that L,T are a basis."""
    check_n(n)
    a, b = 2*n*(F(lens_exponent) % 1), 2*(F(torus_exponent) % 1)
    if a.denominator != 1 or b.denominator != 1:
        raise ValueError("character not in the proved Z_(2n) x Z2 coordinate grid")
    return int(a), int(b)


def character_exponent(n: int, character: tuple[int, int], element: tuple[int, int]) -> F:
    check_n(n)
    if any(type(v) is not int for v in (*character, *element)):
        raise ValueError("integer character and bordism coordinates required")
    r, s = character
    a, b = element
    return (F(r*a, 2*n) + F(s*b, 2)) % 1


def character_order(n: int, character: tuple[int, int]) -> int:
    check_n(n)
    r, s = character
    if type(r) is not int or type(s) is not int:
        raise ValueError("integer character coordinates required")
    return lcm(2*n // gcd(2*n, r), 2 // gcd(2, s))


def add_characters(n: int, *terms: tuple[int, tuple[int, int]]) -> tuple[int, int]:
    check_n(n)
    if any(type(m) is not int or any(type(v) is not int for v in c) for m, c in terms):
        raise ValueError("integer multiplicities and characters required")
    return (sum(m*c[0] for m, c in terms) % (2*n), sum(m*c[1] for m, c in terms) % 2)


def complex_character(n: int, charge: int) -> tuple[int, int]:
    check_n(n)
    return coordinates(n, -parent.lens_rho(n, charge), -torus_rho(n, charge))


def sign_character(n: int) -> tuple[int, int]:
    check_n(n)
    # Never halve a mod-one residue: preserve the quaternionic/Pfaffian integer.
    return coordinates(n, -parent.lens_rho(n, n//2)/2, -torus_rho(n, n//2)/2)


def defect_character(n: int) -> tuple[int, int]:
    check_n(n)
    return add_characters(n, (3, complex_character(n, n//4)), (3, sign_character(n)))


def inverse_response_character(n: int, cs_level: int = 3, abk_level: int = 3) -> tuple[int, int]:
    check_n(n)
    if type(cs_level) is not int or type(abk_level) is not int:
        raise ValueError("quantized integer CS and ABK levels required")
    q = n//4
    # Q(D^q)=q^2 Q(D), checked independently against the full lens spectral sums.
    q_lens = q*q*parent.lens_rho(n, 1)
    q_torus = q*q*torus_rho(n, 1)
    b_lens = parent.lens_rho(n, n//2)/2
    b_torus = torus_rho(n, n//2)/2
    return coordinates(n, cs_level*q_lens + abk_level*b_lens,
                       cs_level*q_torus + abk_level*b_torus)


def bordism_classification(n: int) -> dict:
    check_n(n)
    alpha, beta = complex_character(n, 1), sign_character(n)
    pairs = {add_characters(n, (a, alpha), (b, beta)) for a in range(2*n) for b in range(2)}
    if len(pairs) != 4*n:
        raise RuntimeError("eta separation did not saturate the AHSS bound")
    lens_alpha = -parent.lens_rho(n, 1)
    lens_beta = -parent.lens_rho(n, n//2)/2
    if (lens_alpha % 1).denominator != 2*n or torus_rho(n, 1) % 1 != 0:
        raise RuntimeError("primitive complex lens character or torus kernel check failed")
    # Find the other spin lift's class using both separating characters.
    other_alpha = -parent.lens_rho(n, 1, n//2) % 1
    other_beta = -parent.lens_rho(n, n//2, n//2)/2 % 1
    candidates = [(a, b) for a in range(2*n) for b in range(2)
                  if character_exponent(n, alpha, (a, b)) == other_alpha
                  and character_exponent(n, beta, (a, b)) == other_beta]
    if len(candidates) != 1:
        raise RuntimeError("spin-lift class was not uniquely separated")
    bare = defect_character(n)
    inverse = inverse_response_character(n)
    return {
        "category": "ordinary spin bordism with independent internal C" + str(n),
        "group": "Z" + str(2*n) + " x Z2",
        "order": 4*n,
        "AHSS_total_degree3_E2": [
            {"p": 3, "q": 0, "term": "H3(BCn;Z)=Zn", "order": n},
            {"p": 2, "q": 1, "term": "H2(BCn;Z2)=Z2", "order": 2},
            {"p": 1, "q": 2, "term": "H1(BCn;Z2)=Z2", "order": 2},
            {"p": 0, "q": 3, "term": "OmegaSpin3(pt)=0", "order": 1},
        ],
        "AHSS_order_upper_bound": 4*n,
        "probe_definitions": {
            "alpha": "exp(-2*pi*i*rho_unit_complex)",
            "beta": "exp(-pi*i*rho_real_sign_complexification); half before modulo one",
            "unit_charge_probe_scope": "The unit character is a mathematical test representation of ordinary Spin3 x Cn, not a new physical field. In particular a q1 Spin11-singlet does NOT descend to the frozen Spin^c11 parent: odd U1 charge would require odd Spin11 center parity. The actual C8 defect and its inverse use D=rho2, never a physical q1 singlet.",
            "unit_C8_probe_added_to_physical_parent_spectrum": False,
            "rank_zero_flat_eta_is_a_bordism_character": "APS cancels local densities against the same-rank trivial twist; a real twist has even spin4 Dirac index, so the Pfaffian half also descends.",
        },
        "alpha_evaluation_pair": list(alpha), "beta_evaluation_pair": list(beta),
        "alpha_lens_exponent_exact": str(lens_alpha),
        "beta_lens_exponent_exact": str(lens_beta),
        "alpha_T_exponent_mod1": "0", "beta_T_exponent_mod1": "1/2",
        "distinct_probe_products_from_eta_evaluations": len(pairs),
        "proof": [
            "Spin bordism coefficients in degrees0,1,2,3 are Z,Z2,Z2,0. The three finite AHSS terms give order at most4n; differentials can only lower it.",
            "alpha(L) is a primitive2n-th root, alpha(T)=1 and beta(T)=-1. The4n products alpha^a beta^b, 0<=a<2n and b=0,1, have distinct evaluations on the actual L,T manifolds, independently of any assumed generator dictionary.",
            "The upper bound is saturated, so these characters exhaust the dual. Their values show L has order2n and T has order2. T cannot lie in <L>, since alpha(T)=1 but beta(T)=-1. Consequently L,T give the displayed direct-product basis.",
        ],
        "L_generator": "L3_n(1,1), primitive flat Cn holonomy, V95 canonical lens Dirac sign/spin lift",
        "T_generator": "S1_R x odd-spin T2, primitive Cn holonomy on S1 and no transverse holonomy",
        "opposite_lens_spin_lift_bordism_coordinates": list(candidates[0]),
        "character_coordinate_convention": "chi(a*L+b*T)=exp(2*pi*i*(r*a/(2n)+s*b/2)); coordinate=(r mod2n,s mod2)",
        "bare_defect_character": list(bare),
        "bare_defect_exact_order": character_order(n, bare),
        "inverse_character": list(inverse),
        "inverse_exact_order": character_order(n, inverse),
        "ABK_over8_character": list(add_characters(n, (-1, beta))),
        "ABK_over8_pullback_order": character_order(n, beta),
        "ABK_values_mod8_on_all_bordism_classes": sorted({int(8*character_exponent(n, add_characters(n, (-1, beta)), (a,b))) for a in range(2*n) for b in range(2)}),
        "full_restricted_bordism_basis_proved": True,
        "full_physical_Gammahat_bordism_identified_with_this_group": False,
    }


def effective_pullback() -> dict:
    alpha4, beta4 = complex_character(4, 1), sign_character(4)
    target_alpha = -parent.lens_rho(8, 2) % 1
    target_beta = -parent.lens_rho(8, 4)/2 % 1
    lens_images = [(a, b) for a in range(8) for b in range(2)
                   if character_exponent(4, alpha4, (a, b)) == target_alpha
                   and character_exponent(4, beta4, (a, b)) == target_beta]
    if lens_images != [(2, 0)]:
        raise RuntimeError("effective quotient lens map changed")
    rows = [{"C8_bordism": [a,b], "C4_bordism": [2*a % 8,b]} for a in range(16) for b in range(2)]
    image = {tuple(row["C4_bordism"]) for row in rows}
    kernel = [row["C8_bordism"] for row in rows if row["C4_bordism"] == [0,0]]
    inverse8 = inverse_response_character(8)
    preimages = [[r,s] for r in range(8) for s in range(2) if (4*r % 16,s) == inverse8]
    return {
        "group_map": "pi:C8->C4 sends k8 to k4; rho1(C4) pulls back to rho2(C8)",
        "representation_factorization": "3 complex rho1 plus3 real rho2 on effective C4; physical C8 charges are2 and4, not coefficient-bundle charges6 and0",
        "pi_star_on_bordism": "(a mod16,b mod2) -> (2a mod8,b mod2)",
        "image_L8": list(lens_images[0]), "image_T8": [0,1],
        "all_bordism_images": rows, "image_order": len(image),
        "kernel": kernel, "kernel_order": len(kernel), "kernel_group": "Z4",
        "pullback_on_characters": "(r mod8,s mod2) -> (4r mod16,s mod2)",
        "character_pullback_kernel": [[0,0],[4,0]],
        "inverse_C4_preimages_of_actual_C8_inverse": preimages,
        "natural_spectrum_selected_C4_inverse": list(inverse_response_character(4)),
        "four_copies_C8_bare_trivial": add_characters(8, (4, defect_character(8))) == (0,0),
        "four_copies_C4_bare_remaining_character": list(add_characters(4, (4, defect_character(4)))),
        "not_every_effective_C4_background_lifts_to_C8": True,
        "effective_C4_completion_is_not_forced_by_C8_character_alone": True,
    }


def quantized_response() -> dict:
    rp2_sum = sp.simplify((1+sp.I)/sp.sqrt(2))
    odd_torus_sum = sp.Rational(1-1-1-1, 2)
    if sp.simplify(rp2_sum-sp.expand_complex(sp.exp(sp.pi*sp.I/4))) != 0 or odd_torus_sum != -1:
        raise RuntimeError("ABK Gauss-sum calibration failed")
    quadratic_checks = []
    for n in (4,8):
        for spin in (0,n//2):
            for q in range(n):
                difference = parent.lens_rho(n,q,spin)-q*q*parent.lens_rho(n,1,spin)
                if difference.denominator != 1:
                    raise RuntimeError("spin CS quadratic charge dependence failed")
                quadratic_checks.append({"n":n,"spin_shift":spin,"charge":q,
                                         "rho_q_minus_q_squared_rho1_exact":str(difference)})
    return {
        "explicit_inverse": "Zinv(Y,s,a)=exp(2*pi*i*[3*Q_s(D)+3*ABK_s(PD(a2))/8])",
        "D_and_a2": "C8: D=rho2(a), a2=a mod2; effective C4: D=rho1(a), a2=a mod2",
        "spin_CS_definition": "Q_s(D)=(1/2)*integral_W (F_D/(2*pi))^2 mod1, for a spin4 extension with boundary(Y,s); the U1 bundle/connection extends, not necessarily its finite reduction",
        "CS_level_for_D": 3,
        "equivalent_CS_level_for_C8_covering_unit_line": 12,
        "covering_unit_line_scope": "rho1(a) is an auxiliary associated line of the restricted C8 bundle, not an added Spin^c11-singlet representation; the response is fundamentally written with the inherited determinant line D=rho2.",
        "ABK_level_mod8": 3,
        "spin_CS_extension_exists": "OmegaSpin3(BU1)=0. In the low-degree AHSS, the only possible totaldegree3 term H2(BU1;Z2) is killed by d2:H4(BU1;Z)->H2(BU1;Z2), dual to Sq2(u)=u^2; also stated in Belov-Moore Section2.1.",
        "spin_CS_extension_independence": "On a closed spin4 manifold, c1(D)^2 is even by Wu/intersection parity. Integer level k makes exp(2*pi*i*k*c1(D)^2/2)=1, so every choice of extension gives the same response.",
        "APS_identification": "For the rank-zero complex line twist, APS gives rho_D=(1/2)*integral_W c1(D)^2 mod1. The same boundary orientation/Dirac convention as V95 is used; changing it conjugates the response and the bare anomaly together.",
        "ABK_definition": "PD(a2) has the Pin-minus structure induced by spin(Y). For its quadratic enhancement q:H1(PD;Z2)->Z4, exp(2*pi*i*ABK/8)=|H1|^(-1/2)*sum_x i^q(x).",
        "ABK_sign_calibration": "Choose the induced Pin-minus quadratic-sign convention so the V95 canonical (RP3,sign) maps to (RP2,q(generator)=1): rho_sign/2=1/8=ABK/8. The opposite shared convention conjugates all expressions.",
        "ABK_eta_global_identification": "Smith identifies reduced OmegaSpin3(BZ2) with OmegaPin-minus2=Z8 and sends the RP3 generator to RP2. Both ABK/8 and rho_sign/2 are bordism characters, and the calibrated generator agrees, hence they agree on every ordinary spin3/Z2 background and on their C4/C8 pullbacks.",
        "ABK_calibration_checks": {
            "RP2_quadratic_values": [0,1], "RP2_Gauss_sum": "(1+i)/sqrt(2)", "RP2_ABK_mod8": 1,
            "V95_RP3_real_rho_exact": str(parent.lens_rho(2,1)),
            "V95_RP3_real_half_exact": str(parent.lens_rho(2,1)/2),
            "odd_T2_quadratic_values": [0,2,2,2], "odd_T2_Gauss_sum": "-1", "odd_T2_ABK_mod8": 4,
        },
        "quadratic_lens_checks": quadratic_checks,
        "auxiliary_ABK_surface_scope": "PD(a2) is a symmetry-wall surface in the three-dimensional anomaly test manifold; it has not been identified with an additional placed microscopic Phi defect.",
        "background_connection_is_not_integrated_over": True,
        "this_is_dynamical_U1_level3_CS_with_anyons": False,
        "tautological_eta_inverse_alone": "Complex conjugation always supplies an abstract inverse eta character; the additional result here is its independently quantized spin-CS/ABK decomposition and the complete restricted bordism check.",
        "quantized_abstract_restricted_inverse_response_constructed": True,
        "actual_same_action_bulk_inflow_constructed": False,
        "full_extended_functor_or_boundary_state_spaces_implemented_in_code": False,
    }


def complete_cancellation() -> dict:
    result = {}
    for n in (4,8):
        bare, inverse = defect_character(n), inverse_response_character(n)
        rows = []
        for a in range(2*n):
            for b in range(2):
                e = character_exponent(n, bare, (a,b))
                inv = character_exponent(n, inverse, (a,b))
                total = (e+inv) % 1
                if total:
                    raise RuntimeError("quantized response failed a restricted bordism class")
                rows.append({"bordism_coordinates":[a,b], "bare_exponent_mod1":str(e),
                             "CS_ABK_inverse_exponent_mod1":str(inv), "total_exponent_mod1":str(total)})
        result["C"+str(n)] = {"class_count":len(rows), "rows":rows,
            "all_restricted_reduced_characters_cancel":True,
            "bare_lens_phase":parent.phase_label(character_exponent(n,bare,(1,0))),
            "inverse_lens_phase":parent.phase_label(character_exponent(n,inverse,(1,0))),
            "bare_T_phase":"-1", "inverse_T_phase":"-1"}
    return result


def fermionic_screen() -> dict:
    levels = {}
    for n in (4,8):
        q_order = character_order(n, complex_character(n,n//4))
        b_order = character_order(n, sign_character(n))
        target = add_characters(n,(-1,defect_character(n)))
        matches = [[k,l] for k in range(q_order) for l in range(b_order)
                   if inverse_response_character(n,k,l) == target]
        levels["C"+str(n)] = {"CS_level_period_for_D_on_this_restriction":q_order,
                             "ABK_level_period_on_this_restriction":b_order,
                             "matching_CS_ABK_level_pairs_mod_these_periods":matches,
                             "all_matching_ABK_levels_odd":all(l%2 for _,l in matches)}
    return {
        "T3_exact_obstruction_to_CS_only": "On T=S1 x odd-spin T2, every finite character line is topologically trivial with flat holonomy only along S1. Its background CS invariant is zero (also rho_complex is an integer), while the real sign Pfaffian is -1.",
        "bosonic_DW_only_cannot_supply_T3_sign": "The classifying map on this test factors through S1, so any bosonic H3(BCn;U1) action pulls back to zero; its phase is+1.",
        "ABK_surface_on_T3": "PD(a2)=odd-spin T2 has ABK=4; odd ABK level supplies precisely-1.",
        "CS_only_inverse_possible": False,
        "bosonic_DW_only_inverse_possible": False,
        "odd_spin_refinement_needed_in_CS_ABK_family": True,
        "integer_level_quantization_obstructs_CS3_ABK3": False,
        "spin4_period_example": "On S2 x S2 with c1(D)=a*x+b*y, integral c1(D)^2=2ab and level3 change=3ab in the exponent over2*pi*i, an integer.",
        "level_classes": levels,
        "no_go_against_all_fermionic_relative_inflow_sectors": False,
    }


def primary_sources() -> list[dict]:
    return [
        {"url":"https://arxiv.org/abs/hep-th/0505235", "use":"Belov-Moore Eq(1.3), Section2.1 and(2.7) normalize integral-curvature background spin CS as exp(i*pi*integral K F^2), including integral odd K; Section2.1 states OmegaSpin3(BU1^N)=0, and Section2.2 relates CS to kernel-inclusive xi. Gauge fields are not integrated over in this certificate."},
        {"url":"https://arxiv.org/abs/1406.7329", "use":"Section6 gives the Smith isomorphism for an independent internal unitary Z2 with g^2=1, and its induced Pin-minus structure on PD(a). Section5 describes the Z8 ABK generator. The ordinary-spin scope is essential."},
        {"url":"https://arxiv.org/abs/1812.11959", "use":"Sections3.1-3.3 give low spin bordism coefficients, Eq(3.9) the ABK Gauss sum, ABK=4Arf on oriented surfaces, and the induced Pin-minus structure on PD(a). These calibrate the genuine spin response, not a new microscopic wall assignment."},
        {"url":"https://arxiv.org/abs/2606.18380", "use":"Section3.1(3.4),(3.7),(3.9),(3.12)-(3.15) fixes kernel-inclusive APS xi, rank-zero subtraction, complex determinant and real Pfaffian phases, and the even quaternionic index needed before halving."},
        {"url":"https://arxiv.org/abs/2604.19634", "use":"Eq(2.18) independently confirms Z_(2n) x Z2 and lens/odd-T2-product generators when4 divides n. Here the generator dictionary is also proved by AHSS-bound saturation and exact real/complex eta separation; a complex mod-one torus formula is never halved."},
        {"url":"https://arxiv.org/abs/2504.02934", "use":"AppendixC(C.2) is the finite lens sum inherited through V95, with our explicitly opposite Dirac sign. Exact spectral values and both spin lifts, not residues, fix the Pfaffian."},
    ]


def build_certificate() -> dict:
    _, _, old = load_inputs()
    spectrum = old["inherited_spectrum"]
    if (spectrum["complex_chiral_q2"],spectrum["real_chiral_q4"],spectrum["net_central_charge"]) != (3,3,"9/2"):
        raise RuntimeError("physical isolated-defect spectrum changed")
    result = {
        "schema":SCHEMA,
        "status":"RESTRICTED_REDUCED_DEFECT_INVERSE_CONSTRUCTED_AS_QUANTIZED_BACKGROUND_SPIN_CS_ABK__SAME_ACTION_GLUE_OPEN",
        "input_core_hashes":{"v95_route":V95_ROUTE_CORE,"v95_master":V95_MASTER_CORE,"v95_defect":V95_DEFECT_CORE},
        "inherited_restricted_model": {
            "C8_physical_complex_charge2_count":3, "C8_physical_real_charge4_count":3,
            "effective_C4_complex_charge1_count":3, "effective_C4_real_charge2_count":3,
            "D":"rho2 on C8; rho1 on effective C4", "normal":"N=D^-4=1", "normal_spin_root":"D^-2=sign",
            "tangent_spin_compensation":"induced spin=s+a2; S(s+a2) tensor D^-1 equals physical S(s) tensor rho2 on C8; a coefficient-neutral Majorana becomes the physical sign character",
            "ordinary_spin_C8_local_tubular_admissibility_inherited":old["restricted_spin_and_gauge_lift"]["normal_spin_and_tangent_spin_signs_cancel_in_ambient_spin"],
            "effective_C4_model_extension":"The same isolated tubular construction has D=rho1, N=D^-4=1 and Nspin=D^-2=sign. This is an abstract extension of the factorized defect representation, not a claim that every effective C4 bundle lifts through the microscopic gauge group.",
            "k_squared_is_total_fermion_parity":False, "full_Gammahat_replaced_by_Spin_times_C8":False,
        },
        "normalization": {
            "xi":"(eta_spectral+h)/2", "rho":"xi_twisted-xi_neutral on the same physical spin background",
            "bare_phase":"exp(-2*pi*i*(3*rho_D+(3/2)*rho_sign))",
            "real_half_before_modulo_one":True,
            "lens_sign":"V95 exact negative-DT spectral sum; reverse both response and bare anomaly if reversing common orientation/chirality",
            "same_action_bulk_sign_dictionary_resolved":False,
            "subtracted_reference_is_not_new_physical_fermions":True,
            "remaining_pure_gravitational_central_charge":"9/2",
            "physical_pure_gravitational_anomaly_cancelled":False,
        },
        "restricted_bordism_classification":{"C4":bordism_classification(4),"C8":bordism_classification(8)},
        "effective_C4_pullback":effective_pullback(),
        "quantized_inverse_response":quantized_response(),
        "complete_restricted_character_cancellation":complete_cancellation(),
        "fermionic_quantization_screen":fermionic_screen(),
        "limitations": {
            "actual_same_action_bulk_defect_inflow_constructed":False,
            "full_Gammahat_tangential_structure_bordism_computed":False,
            "physical_relative_Dai_Freed_trivialization_constructed":False,
            "regulated_heavy_mass_determinant_or_bump_inflow_constructed":False,
            "differential_normal_curvature_inflow_with_torsion_glued":False,
            "new_ABK_sector_placed_in_existing_compact_action":False,
            "supersymmetric_or_microscopic_realization_proved":False,
            "unsubtracted_gravitational_anomaly_cancelled":False,
            "bare_defect_or_total_theory_declared_anomaly_free_without_response":False,
            "same_action_parent_or_any_gate_closed":False,
        },
        "primary_sources":primary_sources(),
    }
    result["core_sha256"] = canonical_sha(result)
    return result


def validate_certificate(report: Mapping) -> None:
    if report.get("core_sha256") != canonical_sha(report) or dict(report) != build_certificate():
        raise RuntimeError("F96 inverse-response certificate differs from its fresh bound derivation")


if __name__ == "__main__":
    print(json.dumps(build_certificate(),indent=2,sort_keys=True))
