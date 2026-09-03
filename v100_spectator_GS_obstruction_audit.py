"""F100: independent-spectator GS obstruction and a gauge-only replacement.

This does not gauge W, remove old fields, change a frozen action, or close a gate.
All hyper counts are positive physical full-hyper units (SMW counted once).
"""
from __future__ import annotations

from collections import Counter
import copy
from functools import lru_cache
import json
from pathlib import Path

import sympy as sp

import susy_v91_multipath_g1_frontier_master_audit as common
import v99_spectator_replacement_anomaly_audit as previous


ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v99_route": ("SUSY_V99_QUOTIENT_OBSTRUCTIONS_NORMAL_PAIR_SECTION_AUDIT.json", "240bf71045bda94015027eccbaeebec93fc2caa8940a5dd100e914ad24330c4e"),
    "v99_master": ("SUSY_V99_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json", "72c499490e86c3b9da3e436d95bc6d7b9907806f214ac491be1336b310e2fd39"),
}
SPECTATOR_CORE = "f8bd023b0889f8898542e19d3a5a5e2fd4987b21bf2dc13cd9174c5619b9ade8"
canonical_sha, file_sha = common.canonical_sha, common.file_sha
G = sp.Matrix([[0, 1], [1, 0]])
A_VEC, B_VEC, OLD_C = sp.Matrix([2, 2]), sp.Matrix([2, -1]), sp.Matrix([-472, -148])
OLD_COUNTS = (144, 3, 19, 11, 90)
Q = (0, 2, 4, 6, 8)


def dot(left, right):
    return sp.expand((sp.Matrix(left).T*G*sp.Matrix(right))[0])


def load_inputs():
    parents = {key: common.load_bound(ROOT/name, core) for key, (name, core) in PARENTS.items()}
    route, master = parents["v99_route"], parents["v99_master"]
    if master["input_core_hashes"]["v99_route"] != PARENTS["v99_route"][1] or master["next_required_action"]["id"] != "F100_MODIFIED_EQUIVARIANT_ACTION_AND_ORIGINAL_SECTION_EXISTENCE":
        raise RuntimeError("V99 lineage or F100 obligation changed")
    spectator = route["spectator_replacement_anomaly"]
    if spectator.get("core_sha256") != SPECTATOR_CORE or canonical_sha(spectator) != SPECTATOR_CORE:
        raise RuntimeError("frozen spectator mathematics changed")
    for report, base in ((route, "susy_v99_quotient_obstructions_normal_pair_section_audit"),
                         (master, "susy_v99_multipath_g1_frontier_master_audit")):
        for name, key in ((base+".py", "generator_sha256"), ("test_"+base+".py", "test_sha256")):
            if file_sha(ROOT/name) != report["artifact_hashes"][key]:
                raise RuntimeError("frozen V99 source/test changed: "+name)
    for name in ("v99_spectator_replacement_anomaly_audit.py", "test_v99_spectator_replacement_anomaly_audit.py"):
        if file_sha(ROOT/name) != route["artifact_hashes"][name]:
            raise RuntimeError("frozen spectator source/test changed: "+name)
    # Rebind the actual projector, smooth-bulk, and V98 carrier source chains;
    # do not substitute a fictional collection of neutral trivial hypers.
    old = previous.load_inputs()
    a, b, c = previous.frozen_bulk_data(old["v91_route"])
    if (a, b, c) != (A_VEC, B_VEC, OLD_C):
        raise RuntimeError("actual U lattice or old charge ledger changed")
    if spectator["actual_old_slots"]["irreducible_plus_orbit"]["any_equivariant_q0_removal_has_even_hyper_count"] is not True:
        raise RuntimeError("the required old neutral projector divisibility changed")
    parents["actual_old_projectors"] = old["v92_route"]["smooth_singlet_projectors"]
    return parents


def regular_counts(t):
    if len(t) != 3 or any(type(n) is not int or n < 0 for n in t):
        raise ValueError("three nonnegative integral regular multiplicities are required")
    return (4+4*t[0], 8+4*t[1], 4+4*t[2])


def moments(counts, charges, powers=(1, 2, 3, 4)):
    return tuple(sum(n*q**power for n, q in zip(counts, charges)) for power in powers)


def independent_W_obstruction():
    N, L1, L2, L3, L4, A, B = sp.symbols("N L1 L2 L3 L4 A B")
    s1, s2, h1, h2 = sp.symbols("s1 s2 h1 h2")
    s = sp.Matrix([s1, s2])
    h = sp.Matrix([h1, h2])
    sw = s.subs(sp.solve([dot(A_VEC, s)+N/6, dot(B_VEC, s)], (s1, s2)))
    hw = h.subs(sp.solve([dot(A_VEC, h)+L1/6, dot(B_VEC, h)], (h1, h2)))
    pure = sp.factor(3*dot(sw, sw)-N)
    cp = OLD_C+sp.Matrix([-2*A/9, -A/9])
    s108 = sw.subs(N, 108)
    mixed = sp.expand(dot(cp, s108))
    quartic = sp.expand((3*dot(cp, cp)-419136)/16)
    if sw != sp.Matrix([-N/18, -N/36]) or hw != sp.Matrix([-L1/18, -L1/36]):
        raise RuntimeError("charge-one anomaly normalization changed")
    if pure != N*(N-108)/108 or mixed != 2304+4*A/3 or quartic != 32*A+A*A/108:
        raise RuntimeError("independent-W elimination changed")
    old_m2, old_m4 = moments(OLD_COUNTS, range(5), (2, 4))
    lower_A, upper_A = -1728, -1242
    lower_removed_m4 = 27648-sp.Rational((upper_A+1728)**2, 108)
    if (old_m2, old_m4, lower_removed_m4) != (1618, 24238, 25461):
        raise RuntimeError("finite old-matter budget changed")
    # An independent exact exhaustion of the sole possible regular size.
    cases = []
    for t0 in range(24):
        for t1 in range(24-t0):
            t = (t0, t1, 23-t0-t1)
            l1, l2, l3, l4 = moments(regular_counts(t), (0, 2, 4))
            C = sp.Rational(l2)-sp.Rational(l1*l1, 162)
            aa = 3*(C-2304)/4
            bb = 32*aa+aa*aa/108
            required = sp.Rational(l4, 16)-bb
            if not 0 <= C <= 648 or required <= old_m4:
                raise RuntimeError("regular N108 mixed-W obstruction failed")
            cases.append({"t": list(t), "C": str(C), "A": str(aa), "B": str(bb),
                          "required_removed_r4": str(required),
                          "QQQW_residual": str(3*dot(cp.subs(A, aa), hw.subs(L1, l1))-l3)})
    minimum = min(cases, key=lambda r: sp.Rational(r["required_removed_r4"]))
    f, w, p1 = sp.symbols("f w P1")
    common_delta = sp.expand((16*B*f**4+4*L3*f**3*w+6*L2*f*f*w*w+4*L1*f*w**3+N*w**4)/24
                             -p1*(4*A*f*f+2*L1*f*w+N*w*w)/48)
    return {
        "scope": "Full independent W anomaly trivialization by the frozen rank-two ordinary GS sector, or gauging W while keeping the stated other anomaly contributions fixed. All new hypers are Spin11 singlets of W charge+1; all old remaining and removed fields are W-neutral. This is a necessary polynomial test, not an installed dynamical W vector.",
        "regular_family": "t0,t1,t2>=0; new counts(q0,q2,q4)=(4+4t0,8+4t1,4+4t2); N=16+4(t0+t1+t2)",
        "SMW_counting": "One full hyper contributes one I8(q*f+w); its symplectic conjugate is not a second hyper or opposite chirality.",
        "pure_W_new_minus_W_neutral_old_I8": str(N*(w**4/24-p1*w*w/48)),
        "full_common_Q_W_replacement_delta_I8": str(common_delta),
        "full_common_polynomial_conventions": "f is the original charge-one Q curvature, d=2f; L_j=sum_new(q^j), deltaD2=4A, deltaD4=16B, and N old full hypers are removed. The common rank/gravitational term cancels in this replacement restriction. Independent old/new flavor curvature terms remain outside this necessary restriction, not discarded from a complete action.",
        "normal_compensator_curvature": "w=u+v, not u alone; W is the changed-category spectator line. Setting other commuting backgrounds to zero is a necessary restriction if independent W trivialization is demanded.",
        "required_equations": ["a.cWW=-N/6", "b.cWW=0", "3*cWW^2=N", "a.cQW=-L1/6", "b.cQW=0", "cQQ.cWW+2*cQW^2=L2"],
        "complete_Q_W_quartic_system": ["3*cQQ^2=419136+16B", "3*cQQ.cQW=L3", "cQQ.cWW+2*cQW^2=L2", "3*cQW.cWW=L1", "3*cWW^2=N"],
        "QWWW_after_substitution_residual": str(sp.factor(3*dot(hw, sw)-L1)),
        "correct_cWW": [str(z) for z in sw], "correct_cQW": [str(z) for z in hw],
        "pure_W_quartic_residual": str(pure), "pure_W_allowed_N": [0, 108],
        "pure_W_equations_alone_exclude_all_regular_extensions": False,
        "factor_two_error_explicitly_excluded": "(-N/9,-N/18) has a.dot=-N/3, not-N/6; the corresponding N27 inference is invalid for unit W charge.",
        "at_only_positive_N": {"N": 108, "cWW": [str(z) for z in s108], "cQQ_dot_cWW": str(mixed),
                               "mixed_equation_C": "C=L2-L1^2/162=2304+4A/3", "A": "L2/4-M2_removed", "B": "L4/16-M4_removed"},
        "analytic_proof": [
            "The first three equations force N=108 for any nonempty positive sector.",
            "Cauchy-Schwarz gives L2>=L1^2/108, hence C>=0. Since every new charge is in[0,4], q^2<=4q, so C<=4L1-L1^2/162=648-(L1-324)^2/162<=648.",
            "Therefore-1728<=A<=-1242. The gauge-only Q quartic equation requires B=32A+A^2/108=-27648+(A+1728)^2/108<=-25461.",
            "New L4 is nonnegative, so the removed old r=q/2 fourth moment is L4/16-B>=25461. Even the entire actual old singlet spectrum has only24238. No allowed removal can meet the necessary mixed equations.",
        ],
        "C_bounds": [0, 648], "A_bounds": [lower_A, upper_A],
        "required_removed_r4_lower_bound": int(lower_removed_m4), "entire_old_r4_budget": old_m4,
        "strict_budget_gap": int(lower_removed_m4-old_m4),
        "all_N108_regular_triplets_checked": len(cases), "exact_N108_cases_sha256": canonical_sha(cases),
        "N108_exact_minimum_required_old_r4": copy.deepcopy(minimum),
        "all_regular_independent_W_GS_trivializations_rejected_in_stated_ansatz": True,
        "QQQW_and_quotient_integrality_needed_for_analytic_contradiction": False,
        "global_W_tHooft_anomaly_alone_is_quantum_inconsistency": False,
        "genuinely_global_W_scope": "A nonzero 't Hooft anomaly of a global spectator is not by itself a quantum inconsistency. This theorem requires its independent anomaly to be trivialized/gauged by this fixed GS sector; it does not silently impose that requirement on the frozen theory. Mixed ABJ/global-symmetry questions and a full coupled action require their own treatment.",
        "possible_evasion_changes_not_constructed": [
            "Leave W as an anomalous global symmetry or restrict/correlate its allowed backgrounds; the full independent-W equations then need not be imposed.",
            "Change tensor content, lattice or old a,b; add W-charged old/remnant/nonabelian fields, additional anomaly/inflow sectors, or new charges outside0,2,4.",
            "Change the carrier, chirality/multiplet content or replacement rule; each such change requires a fresh SUSY, anomaly, spectrum and global-quotient analysis.",
            "The V98 response-only Spin-c construction introduces no sixteen-hyper sector and is outside this obstruction.",
        ],
    }


def gauge_only_seeds():
    """Exact elimination over all equal replacements of the finite old spectrum.

    Each seed has minimal n0 for fixed charged removals and k. Every descendant
    is n0->n0+4j, t0->t0+j while n0<=144. Thus seeds encode the entire search.
    """
    rows = []
    for n2 in range(4):
        for n4 in range(20):
            for n6 in range(12):
                for n8 in range(91):
                    charged = n2+n4+n6+n8
                    if charged % 2:
                        continue
                    M2 = n2+4*n4+9*n6+16*n8
                    delta = 12*n4+72*n6+240*n8
                    for k in range(-22, 15):
                        A, B = 72*k, 48*k*(k+48)
                        num2 = B-A-48+delta
                        if num2 < 0 or num2 % 48:
                            continue
                        t2 = num2//48
                        num1 = A-24+M2-16*t2
                        if num1 < 0 or num1 % 4:
                            continue
                        t1 = num1//4
                        n0 = max(0, 16+4*(t1+t2)-charged)
                        n0 += (-charged-n0) % 4
                        N = n0+charged
                        if n0 > 144 or N > 264:
                            continue
                        t0 = N//4-4-t1-t2
                        rows.append({"N": N, "t": [t0, t1, t2], "removed": [n0, n2, n4, n6, n8], "k": k})
    return rows


def gauge_only_certificate():
    rows = gauge_only_seeds()
    minimum = min(row["N"] for row in rows)
    best = [row for row in rows if row["N"] == minimum]
    if best != [{"N": 40, "t": [0, 2, 4], "removed": [28, 0, 2, 0, 10], "k": -1}]:
        raise RuntimeError("minimum gauge-only replacement changed")
    r = best[0]
    A, B = 72*r["k"], 48*r["k"]*(r["k"]+48)
    cp = OLD_C+sp.Matrix([-sp.Rational(2*A, 9), -sp.Rational(A, 9)])
    added = list(regular_counts(r["t"]))+[0, 0]
    final = [old-rm+new for old, rm, new in zip(OLD_COUNTS, r["removed"], added)]
    D2, D4 = moments(final, Q, (2, 4))
    bulk2, bulk4 = moments((11, 11, 11), (6, 4, 6), (2, 4))
    if (D2+bulk2, D4+bulk4, dot(B_VEC, cp)) != (-6*dot(A_VEC, cp), 3*dot(cp, cp), 176):
        raise RuntimeError("minimum scout's smooth equations failed")
    histogram = Counter(row["N"] for row in rows)
    return {
        "scope": "Gauge-only rational smooth GS equations plus the frozen ordinary quotient half-source condition and necessary even neutral-projector removal. W/flavor cancellation, full new Gammahat/Sp267 action, local anomaly repair and masses are not claimed.",
        "actual_old_counts": list(OLD_COUNTS), "maximum_equal_replacement_N": 264,
        "analytic_elimination": {
            "quotient_source": "(c'+4b)/8=(-58-A/36,-19-A/72), so integrality is equivalent to A=72k",
            "B": "48*k*(k+48)", "removed_M2": "n2+4*n4+9*n6+16*n8",
            "t2": "(B-A-48+12*n4+72*n6+240*n8)/48",
            "t1": "(A-24+removed_M2-16*t2)/4", "t0": "(n0+n2+n4+n6+n8)/4-4-t1-t2",
            "necessary_k_bounds": [-22, 14],
            "bound_proof": "N<=264 implies sum(t)<=62 and new r^2 moment<=1016. All old r^2 moment is1618, so-1594<=A<=1016. Combined with A=72k this yields-22<=k<=14.",
            "complete_seed_rule": "For every capped charged-removal tuple and k, require integral nonnegative t1,t2. Choose the smallest n0>=max(0,16+4(t1+t2)-sum_charged) with n0+sum_charged divisible by4 and n0 even. All others are n0+4j,t0+j, subject to n0<=144 and total<=264.",
        },
        "number_of_minimal_neutral_seeds": len(rows), "all_seeds_sha256": canonical_sha(rows),
        "seed_minimum_N_histogram": [[n, count] for n, count in sorted(histogram.items())],
        "minimum_N": minimum, "number_of_minimum_scouts": len(best),
        "no_survivor_at_N16_through_N36": True,
        "minimum_scout": {**copy.deepcopy(r), "A": A, "B": B, "added_counts": added, "resulting_counts": final,
                          "c_prime": [str(z) for z in cp], "ordinary_quotient_half_source": [str(z) for z in (cp+4*B_VEC)/8],
                          "total_D2": int(D2+bulk2), "total_D4": int(D4+bulk4),
                          "new_free_chirals_before_removal": 8+2*sum(r["t"]),
                          "independent_W_pure_quartic_residual": str(sp.Rational(minimum*(minimum-108), 108)),
                          "is_accepted_new_sector": False},
    }


def minimum_scout_projectors(saved):
    blocks = saved["eleven_mode_normal_aligned_witness"]["direct_sum_blocks"]
    neutral = next(r["certificate"] for r in blocks if r["certificate"]["q_magnitude"] == 0)
    a0, u0, v0 = [previous.matrix(neutral["effective_plus"][key]) for key in ("A", "U", "V")]
    R = previous.carrier.ZETA*a0
    T = sp.diag(1, sp.I, -1, -sp.I)*a0**2
    pair_map = sp.diag(sp.eye(4), T)
    neutral_checks = [previous.clean(T*sp.conjugate(Z)-Z*T) == sp.zeros(4) for Z in (R, u0, v0)]
    neutral_checks += [previous.clean(pair_map*previous.matrix(neutral["underlying_flavor"][key])*pair_map.inv()-sp.diag(Z, Z)) == sp.zeros(8)
                       for key, Z in (("A", R), ("U", u0), ("V", v0))]
    if not all(neutral_checks) or T*sp.conjugate(T) != -sp.eye(4):
        raise RuntimeError("actual neutral quaternionic multiplicity proof failed")
    charged = {}
    for q, removal in ((4, 2), (8, 10)):
        orbit = next(r["certificate"] for r in blocks if r["certificate"]["q_magnitude"] == q and r["certificate"]["kind"] == "four_orbit")
        A, U, V = [previous.matrix(orbit["effective_plus"][key]) for key in ("A", "U", "V")]
        common_fixed = (U-sp.eye(4)).col_join(V-sp.eye(4)).nullspace()
        joint = [(str(U[j, j]), str(V[j, j])) for j in range(4)]
        cycle = [0]
        for _ in range(4):
            support = [j for j in range(4) if A[j, cycle[-1]] != 0]
            if len(support) != 1:
                raise RuntimeError("orbit generator does not permute the joint eigenlines")
            cycle.append(support[0])
        lines = [r for r in blocks if r["certificate"]["q_magnitude"] == q and r["certificate"]["kind"] == "line"]
        line_count = sum(row["copies"] for row in lines)
        allowed = [n for n in range(line_count+1) if removal >= n and (removal-n) % 4 == 0]
        if common_fixed or len(set(joint)) != 4 or set(cycle[:-1]) != set(range(4)) or cycle[-1] != cycle[0] or allowed != [2]:
            raise RuntimeError("charged old-module divisibility changed")
        if any(previous.matrix(r["certificate"]["effective_plus"][key]) != sp.eye(1) for r in lines for key in ("U", "V")):
            raise RuntimeError("the old singleton translations changed")
        charged[str(q)] = {"removed_hyper_count": removal, "old_singleton_count": line_count,
                           "forced_singletons_removed": allowed[0], "four_orbit_hypers_removed": removal-allowed[0],
                           "orbit_A_U_V": {key: previous.mj(mat) for key, mat in zip(("A", "U", "V"), (A, U, V))},
                           "joint_U_V_eigenlines": joint, "A_cycle_of_joint_eigenlines": cycle,
                           "orbit_common_translation_fixed_dimension": len(common_fixed),
                           "line_certificates_sha256": [canonical_sha(r["certificate"]) for r in lines]}
    lost = [4, 4, 8, -8]
    old_modes = saved["eleven_mode_normal_aligned_witness"]["constant_N1_signed_continuous_charges"][:]
    for charge in lost:
        old_modes.remove(charge)
    new_modes = [{"Q": sign*q, "W": sign, "multiplicity": count}
                 for q, count in ((0, 1), (2, 4), (4, 5)) for sign in (1, -1)]
    local = {}
    d = previous.d
    for order in (4, 2):
        lost_poly = sp.expand(2*previous.carrier.local_I6(order, 0, 2*d)+previous.carrier.local_I6(order, 0, 4*d)+previous.carrier.local_I6(order, 3 % order, 4*d))
        local["C4_each" if order == 4 else "C2_each_cover"] = str(lost_poly)
    zero_index = sp.expand((2*sp.sympify(local["C4_each"])+2*sp.sympify(local["C2_each_cover"])).subs(previous.x, 0))
    if sp.expand(zero_index-2*previous.I6(2*d)) != 0:
        raise RuntimeError("removed exact local trace disagrees with lost zero modes")
    return {
        "continuous_Q_is_retained_not_only_Q_mod8": True,
        "charged_orbit_argument": "For q!=0 a charge-preserving subrepresentation cannot mix the plus and minus continuous charge spaces. The four distinct translation eigenlines cycled by A form a complex irreducible of dimension4. It has no U=V=1 eigenvector, so no intertwiner with the singleton lines. Removed plus-space dimensions are4k+number_of_removed_lines, even under arbitrary mixing of identical copies.",
        "charged_blocks": charged,
        "actual_neutral_even_removal_proof": {
            "bound_block_sha256": canonical_sha(neutral), "quaternionic_intertwiner_T": previous.mj(T),
            "intertwiner_and_full_pair_R_plus_R_checks": neutral_checks,
            "complex_irrep_dimension": 4, "full_neutral_complex_dimension": 288,
            "irrep_multiplicity": 72, "necessary_removal_rule": "A full-hyper removal r has complex symplectic dimension2r, a multiple of4; hence r is even. The full neutral pair is R plus R, so this allows mixing identical copies rather than assuming whole four-orbit deletion.",
        },
        "q0_restricted_block_witness": "Remove seven of the actual thirty-six neutral four-orbit copies, i.e.28 hypers with no free modes.",
        "actual_removed_free_charges": lost, "both_old_Phi_plus_minus8_unavoidably_removed": True,
        "old_Phi_driven_mass_module_preserved": False,
        "remaining_old_free_charges": sorted(old_modes), "new_free_Q_W_table": new_modes,
        "new_free_chiral_count": sum(r["multiplicity"] for r in new_modes),
        "conditional_total_free_chiral_count": len(old_modes)+sum(r["multiplicity"] for r in new_modes),
        "remaining_common_Q_TrQ_TrQ3": list(moments([1]*len(old_modes), old_modes, (1, 3))),
        "removed_old_full_normal_I6": local,
        "removed_integrated_4D_I6_in_d": str(zero_index),
        "removal_leaves_original_localized_anomaly_profile_unchanged": False,
        "all_new_W_and_independent_flavor_curvatures_may_be_discarded": False,
        "free_operator_scope": "Counts refer to the frozen flat, zero-flux free projectors and the restricted new C4 multiplicity ansatz. They are not an interacting mass spectrum, an installed full Gammahat/Sp267 representation, or a borrowed V97 Dirac gap.",
        "new_mass_or_global_QK_SUSY_action_constructed": False,
    }


@lru_cache(maxsize=1)
def _math_json(projector_json):
    return json.dumps({"independent_W_GS_obstruction": independent_W_obstruction(),
                       "gauge_only_regular_replacement_search": gauge_only_certificate(),
                       "minimum_scout_actual_projector_cost": minimum_scout_projectors(json.loads(projector_json))},
                      sort_keys=True, separators=(",", ":"))


def build_certificate():
    parents = load_inputs()
    result = {
        "schema": "v100_spectator_GS_obstruction_and_minimum_gauge_only_replacement_v1",
        "status": "ALL_REGULAR_INDEPENDENT_W_GS_COMPLETIONS_REJECTED__MINIMUM_GAUGE_ONLY40_LOSES_BOTH_PHI__PARENT_OPEN",
        "input_core_hashes": {key: value[1] for key, value in PARENTS.items()},
        "bound_spectator_core": SPECTATOR_CORE,
        **json.loads(_math_json(json.dumps(parents["actual_old_projectors"], sort_keys=True))),
        "terminal_decision": {
            "pure_W_N27_claim_rejected_by_correct_normalization": True,
            "all_regular_independent_W_fixed_GS_trivializations_rejected": True,
            "gauge_only_minimum40_is_full_completion": False,
            "global_flavor_anomaly_alone_declared_inconsistent": False,
            "all_spectator_or_response_only_alternatives_excluded": False,
            "new_dynamical_W_vector_installed": False,
            "full_old_Sp267_embedding_constructed": False,
            "microscopic_parent_accepted": False, "theory_complete": False, "closed_gates": [],
        },
        "primary_sources": [
            {"url": "https://arxiv.org/abs/1803.07998", "use": "Equations2.9-2.12 set a.cAB=-sum(qAqB)/6 and the three-term quartic contraction. Section2 distinguishes gauge-anomaly cancellation from a global flavor 't Hooft anomaly; both distinctions are used here."},
            {"url": "https://arxiv.org/abs/1110.5916", "use": "Equations2.22-2.25 independently fix the mixed-abalian normalization, including cQQ.cWW+2*cQW^2. The corrected N108 restriction and the finite-budget contradiction are derived here, not inferred from a pure-W N27 claim."},
            {"url": "https://arxiv.org/abs/1808.01334", "use": "Global six-dimensional GS consistency needs quantized lattice and differential data beyond rational polynomial factorization. The gauge-only40 scout is not promoted to a quantum action."},
            {"url": "https://arxiv.org/abs/hep-th/0612212", "use": "The normal-shifted localized index is evaluated through the frozen source-bound kernel; the removed nonzero local polynomial is checked against the independent free zero modes."},
        ],
    }
    result["core_sha256"] = canonical_sha(result)
    return result


def validate_certificate(result):
    if result.get("core_sha256") != canonical_sha(result) or result != build_certificate():
        raise RuntimeError("F100 spectator arithmetic, lineage or scope changed")


if __name__ == "__main__":
    print(json.dumps(build_certificate(), sort_keys=True, indent=2))
