"""Repair the bound V104 exponent permutation without rewriting frozen history."""
from __future__ import annotations

import ast
import copy
from functools import lru_cache
import inspect
import json
from pathlib import Path

import sympy as sp
from sympy.polys.domains import QQ
from sympy.polys.rings import ring

import susy_v91_multipath_g1_frontier_master_audit as common
import v103_original_quartic_section_audit as geometry
import v104_q2_core_reduction_audit as historical
import v105_q2_index_correction_audit as independent

ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v104_route": ("SUSY_V104_Q2_CORE_REDUCTION_AUDIT.json", "b22468dd4bd4ab3c77839ba8fa561deee01a539f23fc64e176c4660a169cc41c"),
    "v104_master": ("SUSY_V104_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json", "ecaff36a770c6d3bea417b7ddfa7238345b0508e62e2c320aa7d2d6ccc13e064"),
    "v103_route": ("SUSY_V103_NORMAL_PARITY_QUARTIC_TARGET_AUDIT.json", "cb5074dae5e38ea34c167d869050abd1926053c6bda229edf919b7d7f2e16e53"),
}
PARENT_OBLIGATION = "F105_Q2_RESIDUAL_CLOSURE_Q1_AND_TARGET_SYSTEMS_WITH_COVARIANT_ACTION_REPAIR"
INDEPENDENT_CORE = "03f082a6f73b4919c4ea5b619c99049d6a641472341555d7cebb413de4d01088"
INDEPENDENT_PINS = {
    "v105_q2_index_correction_audit.py": "271c050ae93606aac0697e70b4bda841b15406a5c3d7e56bb37578fc207d1c9a",
    "test_v105_q2_index_correction_audit.py": "9455fa5f0e84b45525a083413d2972f8121cf2031319483780a6cd9b317c4e32",
    "SUSY_V105_Q2_INDEX_CORRECTION_AUDIT.md": "9502bf5e5f3a965a482483ec9b5269135d3bd6688acc4e55e39284b5fd4e773c",
}
canonical_sha, file_sha = common.canonical_sha, common.file_sha
t, p, q, r, h = geometry.t, geometry.p, geometry.q, geometry.r, geometry.h
PARAMETERS = geometry.PARAMETERS
VARIABLES = (t, p, q, h, *PARAMETERS)
RING, *GENERATORS = ring(VARIABLES, QQ)
rt, rp, rq, rh, *rparameters = GENERATORS


def load_inputs():
    for name, sha in INDEPENDENT_PINS.items():
        if file_sha(ROOT/name) != sha:
            raise RuntimeError("the independently committed correction changed: "+name)
    inputs = {key: common.load_bound(ROOT/name, core) for key, (name, core) in PARENTS.items()}
    if inputs["v104_master"]["input_core_hashes"]["v104_route"] != PARENTS["v104_route"][1]:
        raise RuntimeError("V104 master-to-route lineage changed")
    if inputs["v104_route"]["next_required_action"]["id"] != PARENT_OBLIGATION:
        raise RuntimeError("the original F105 obligation changed")
    bases = {"v104_route": "susy_v104_q2_core_reduction_audit", "v104_master": "susy_v104_multipath_g1_frontier_master_audit", "v103_route": "susy_v103_normal_parity_quartic_target_audit"}
    for key, base in bases.items():
        report = inputs[key]
        for name, pin in ((base+".py", "generator_sha256"), ("test_"+base+".py", "test_sha256")):
            if file_sha(ROOT/name) != report["artifact_hashes"][pin]:
                raise RuntimeError("frozen parent source/test changed: "+name)
        for name, sha in report["artifact_hashes"].items():
            if name.endswith(".py") and file_sha(ROOT/name) != sha:
                raise RuntimeError("frozen helper source/test changed: "+name)
    quartic = inputs["v103_route"]["original_quartic_sections"]
    if inputs["v104_route"]["input_core_hashes"]["v103_route"] != PARENTS["v103_route"][1]:
        raise RuntimeError("V104-to-V103 original-member lineage changed")
    if canonical_sha(quartic) != historical.V103_QUARTIC_CORE:
        raise RuntimeError("canonical V103 original quartic changed")
    if canonical_sha(quartic["exact_quartic_reduction"]["remaining_equations_T5_through_T0"]) != quartic["quartic_reduced_equations_sha256"]:
        raise RuntimeError("source residual coefficients changed")
    if {str(k): str(v) for k, v in geometry.COEFFICIENTS.items()} != quartic["coefficient_dictionary"]:
        raise RuntimeError("the imported parameter dictionary changed")
    if list(map(str, PARAMETERS)) != ["alpha", "beta", "gamma", "delta", "epsilon"]:
        raise RuntimeError("the declared parameter ordering changed")
    if dict(geometry.SPECIAL_VALUES) != {k: v.subs(geometry.X, 1) for k, v in geometry.COEFFICIENTS.items()}:
        raise RuntimeError("the witness payload is not the original X=1 specialization")
    return inputs


def to_ring(expr):
    """The declared symbol ordering is handled by SymPy, not manual offsets."""
    return RING.from_expr(expr)


def historical_converter():
    """Extract only the actual frozen nested converter for forensic tests."""
    source = inspect.getsource(historical._reduction.__wrapped__)
    outer = ast.parse(source).body[0]
    node = next(n for n in outer.body if isinstance(n, ast.FunctionDef) and n.name == "to_ring")
    scope = {"sp": sp, "QQ": QQ, "PARAMETERS": PARAMETERS,
             "t": t, "p": p, "q": q, "h": h, "base": RING,
             "bt": rt, "bp": rp, "bq": rq, "bh": rh, "bpar": rparameters}
    program = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
    exec(compile(program, "<source-bound V104 converter>", "exec"), scope)
    return scope["to_ring"]


def q_coefficient(poly, exponent):
    out = RING.zero
    for powers, coefficient in poly.items():
        if powers[2] == exponent:
            monomial = list(powers)
            monomial[2] = 0
            out[tuple(monomial)] = coefficient
    return out


def pseudo_reduce(poly, divisor):
    """Return an exact division identity, retaining every coefficient pivot."""
    d = max((powers[2] for powers in poly), default=0)
    steps = max(0, d-1)
    a2 = q_coefficient(divisor, 2)
    if not a2 or max((powers[2] for powers in divisor), default=0) != 2:
        raise ValueError("a genuine quadratic divisor is required")
    quotient, residual = RING.zero, poly
    for k in range(d, 1, -1):
        lead = q_coefficient(residual, k)
        quotient = a2*quotient+lead*rq**(k-2)
        residual = a2*residual-lead*rq**(k-2)*divisor
    if a2**steps*poly != quotient*divisor+residual:
        raise RuntimeError("the universal polynomial division identity failed")
    if max((powers[2] for powers in residual), default=0) > 1:
        raise RuntimeError("q reduction did not terminate at degree at most one")
    return quotient, residual, steps


def primitive_t_pair(ell, mu):
    exponents = [powers[0] for poly in (ell, mu) for powers in poly]
    shift = min(exponents) if exponents else 0
    return ell.exquo(rt**shift), mu.exquo(rt**shift), shift


def sparse_sha(poly):
    return canonical_sha([[list(powers), str(value)] for powers, value in sorted(poly.items())])


def clear_nonzero_factors(poly, M):
    if not poly:
        return poly, 0, 0
    shift = min(powers[0] for powers in poly)
    core, m_power = poly.exquo(rt**shift), 0
    while core:
        quotient, remainder = divmod(core, M)
        if remainder:
            break
        core, m_power = quotient, m_power+1
    if poly != core*rt**shift*M**m_power:
        raise RuntimeError("nonzero factor removal is not exact")
    return core, shift, m_power


@lru_cache(maxsize=2)
def reduction_json(quartic_json):
    quartic = json.loads(quartic_json)
    boundary = quartic["pivot_boundary_data"]
    r0 = geometry.parse(boundary["L_zero_r_reconstruction"])
    F = to_ring(geometry.parse(boundary["L_zero_first_equation_F"]))
    A2, A1, A0 = (q_coefficient(F, k) for k in (2, 1, 0))
    M = to_ring(geometry.parse(boundary["second_pivot_M"]))
    if A2 != -1296*rt**6*M or any(powers[3] for powers in A1*A1-4*A2*A0):
        raise RuntimeError("the unaffected V104 leading-coefficient/discriminant facts changed")
    old = historical_converter()
    basis_rows = [{"variable": str(symbol), "historical_image": str(old(symbol).as_expr()),
                   "correct_image": str(to_ring(symbol).as_expr())} for symbol in VARIABLES]
    rows = []
    for row in quartic["exact_quartic_reduction"]["remaining_equations_T5_through_T0"][1:]:
        original = sp.expand(geometry.parse(row["numerator"]).subs(r, r0))
        numerator, denominator = sp.fraction(sp.together(original))
        P, den = to_ring(numerator), to_ring(denominator)
        if den != RING.one:
            raise RuntimeError("the inherited residual reconstruction must be polynomial here")
        if sp.expand(P.as_expr()-numerator) != 0:
            raise RuntimeError("actual source residual changed in ring conversion")
        quotient, remainder, steps = pseudo_reduce(P, F)
        ell, mu, shift = primitive_t_pair(q_coefficient(remainder, 1), q_coefficient(remainder, 0))
        if A2**steps*P != quotient*F+rt**shift*(ell*rq+mu):
            raise RuntimeError("the normalized source reconstruction identity failed")
        rows.append({"T_degree": row["T_degree"], "source_numerator_sha256": sparse_sha(P),
                     "source_q_degree": max(powers[2] for powers in P),
                     "A2_power": steps, "removed_t_power": shift,
                     "quotient_sha256": sparse_sha(quotient), "division_identity_verified": True,
                     "ell": str(ell.as_expr()), "mu": str(mu.as_expr()),
                     "ell_h_degree": max((powers[3] for powers in ell), default=-1),
                     "mu_h_degree": max((powers[3] for powers in mu), default=-1),
                     "historical_conversion_matches_source": old(numerator) == P})
    return json.dumps({"F": str(F.as_expr()), "A2": str(A2.as_expr()), "A1": str(A1.as_expr()),
                       "A0": str(A0.as_expr()), "M": str(M.as_expr()), "r0": str(r0),
                       "basis_round_trips": basis_rows, "rows": rows}, sort_keys=True)


def load_polynomials(reduced):
    a2, a1, a0, M = (to_ring(geometry.parse(reduced[key])) for key in ("A2", "A1", "A0", "M"))
    pairs = {row["T_degree"]: tuple(to_ring(geometry.parse(row[key])) for key in ("ell", "mu")) for row in reduced["rows"]}
    return a2, a1, a0, M, pairs


def slice_h(poly, t_value, p_value, prime=101):
    values = [t_value, p_value, 0, 0, *[int(geometry.SPECIAL_VALUES[z]) for z in PARAMETERS]]
    out = {}
    for powers, coefficient in poly.items():
        if powers[2]:
            raise ValueError("slice requires q-free polynomial")
        scalar = int(coefficient.numerator)*pow(int(coefficient.denominator), -1, prime) % prime
        for i, exponent in enumerate(powers):
            if i != 3:
                scalar = scalar*pow(values[i], exponent, prime) % prime
        out[powers[3]] = (out.get(powers[3], 0)+scalar) % prime
    return sp.Poly.from_dict({(i,): v for i, v in out.items() if v}, h, modulus=prime)


def sylvester_mod(first, second, prime=101):
    """Explicit descending-coefficient row convention, including degree checks."""
    m, n = first.degree(), second.degree()
    if min(m, n) < 1:
        raise ValueError("positive degrees required for these witnesses")
    a, b = first.all_coeffs(), second.all_coeffs()
    rows = [[0]*i+a+[0]*(n-1-i) for i in range(n)]+[[0]*i+b+[0]*(m-1-i) for i in range(m)]
    matrix = [[int(v) % prime for v in row] for row in rows]
    det = 1
    for k in range(m+n):
        pivot = next((i for i in range(k, m+n) if matrix[i][k]), None)
        if pivot is None:
            return 0
        if pivot != k:
            matrix[k], matrix[pivot] = matrix[pivot], matrix[k]
            det = -det % prime
        diagonal = matrix[k][k]
        det = det*diagonal % prime
        for i in range(k+1, m+n):
            factor = matrix[i][k]*pow(diagonal, -1, prime) % prime
            for j in range(k, m+n):
                matrix[i][j] = (matrix[i][j]-factor*matrix[k][j]) % prime
    return det


@lru_cache(maxsize=2)
def elimination_json(reduced_json):
    reduced = json.loads(reduced_json)
    a2, a1, a0, M, pairs = load_polynomials(reduced)
    cores, rows = {}, []
    for i, (ell, mu) in pairs.items():
        if i != 4:
            rows.append({"id": "R"+str(i), "definition": "A2*mu_i^2-A1*ell_i*mu_i+A0*ell_i^2", "expanded": False})
            continue
        raw = a2*mu**2-a1*ell*mu+a0*ell**2
        core, tp, mp = clear_nonzero_factors(raw, M)
        cores["R"+str(i)] = core
        rows.append({"id": "R"+str(i), "definition": "A2*mu_i^2-A1*ell_i*mu_i+A0*ell_i^2", "expanded": True,
                     "removed_t_M_powers": [tp, mp], "term_count": len(core),
                     "h_degree": max((e[3] for e in core), default=-1), "core_sparse_sha256": sparse_sha(core)})
    order = list(pairs)
    for index, i in enumerate(order):
        for j in order[index+1:]:
            label = "C"+str(i)+str(j)
            if (i, j) != (4, 3):
                rows.append({"id": label, "definition": "ell_i*mu_j-ell_j*mu_i", "expanded": False})
                continue
            ell_i, mu_i = pairs[i]
            ell_j, mu_j = pairs[j]
            raw = ell_i*mu_j-ell_j*mu_i
            core, tp, mp = clear_nonzero_factors(raw, M)
            cores[label] = core
            rows.append({"id": label, "definition": "ell_i*mu_j-ell_j*mu_i", "expanded": True,
                         "removed_t_M_powers": [tp, mp], "term_count": len(core),
                         "h_degree": max((e[3] for e in core), default=-1), "core_sparse_sha256": sparse_sha(core)})
    degrees = [max(e[3] for e in cores[key]) for key in ("R4", "C43")]
    witnesses = []
    for tv, pv in historical.WITNESS_POINTS:
        first, second = (slice_h(cores[key], tv, pv) for key in ("R4", "C43"))
        if [first.degree(), second.degree()] != degrees:
            raise RuntimeError("specialization changed a fixed resultant degree")
        witnesses.append({"t": tv, "p": pv, "M_mod101": (-int(geometry.SPECIAL_VALUES[geometry.alpha])*tv*tv+4*pv*tv+64) % 101,
                          "h_degrees": degrees, "fixed_Sylvester_determinant_mod101": sylvester_mod(first, second),
                          "R4_slice": str(first.as_expr()), "C43_slice": str(second.as_expr())})
    return json.dumps({"necessary_core_rows": rows, "leading_pair_h_degrees": degrees,
                       "fixed_modular_witnesses": witnesses}, sort_keys=True)


def common_root_theorem():
    a2, a1, a0, ei, mi, ej, mj = sp.symbols("a2 a1 a0 ei mi ej mj")
    reconstructed = -mi/ei
    Ri, Cij = a2*mi**2-a1*ei*mi+a0*ei**2, ei*mj-ej*mi
    identities = [sp.cancel(ei**2*(a2*reconstructed**2+a1*reconstructed+a0)-Ri),
                  sp.cancel(ei*(ej*reconstructed+mj)-Cij),
                  sp.expand((a1*ei-2*a2*mi)**2-(a1*a1-4*a2*a0)*ei**2-4*a2*Ri)]
    if identities != [0, 0, 0]:
        raise RuntimeError("the exact common-root reconstruction theorem failed")
    return {
        "field": "k=C(X), characteristic zero; point-set equivalence, not an equality of scheme ideals",
        "Q2_domain": ["t!=0", "M!=0", "t,p,h in k", "r reconstructed from L=0"],
        "five_quadratic_norms": "R_i=A2*mu_i^2-A1*ell_i*mu_i+A0*ell_i^2, i=4,3,2,1,0",
        "ten_cross_conditions": "C_ij=ell_i*mu_j-ell_j*mu_i for all ten unordered pairs, with i>j",
        "regular_reconstruction": "If any ell_i!=0, impose R_i=0 and the four C_ij=0, then q=-mu_i/ell_i is the unique common root in k. These five equations are necessary and sufficient on that chart; all other R,C then vanish.",
        "regular_discriminant_square_automatic": "Delta=(A1-2*A2*mu_i/ell_i)^2 once R_i=0; no separate square-root extension or regular-chart square test is needed.",
        "disjoint_regular_charts": [{"pivot_index": i, "earlier_ell_indices_required_zero": list(range(4, i, -1)), "required_nonzero": "ell_"+str(i), "remaining_equation_count": 5} for i in range(4, -1, -1)],
        "zero_slope_chart": "If all five ell_i=0, the five R_i=0 force all five mu_i=0 because A2!=0 in a field. The remaining quadratic has a k-root iff Delta is a square in k, including zero; q=(-A1+s)/(2*A2), s^2=Delta.",
        "all_fifteen_conditions_sufficient_over_algebraic_closure": True,
        "all_fifteen_conditions_alone_sufficient_over_C_X_on_zero_slope_chart": False,
        "zero_slope_and_repeated_roots_discarded": False,
        "checked_abstract_identity_residuals": [str(z) for z in identities],
        "exceptional_zero_slope_chart_solved_or_excluded": False,
        "any_of_five_regular_charts_solved_or_excluded": False,
        "full_Q2_point_set_reduced_exactly": True,
        "full_Q2_solvability_decided": False,
    }


def independent_compatibility(reduced, eliminated):
    external = independent.build_certificate()
    if external.get("core_sha256") != INDEPENDENT_CORE or canonical_sha(external) != INDEPENDENT_CORE:
        raise RuntimeError("the independently committed correction core changed")
    data = independent.corrected_data()
    for row in reduced["rows"][:2]:
        for field in ("ell", "mu"):
            if sp.expand(data[field+str(row["T_degree"])]-geometry.parse(row[field])) != 0:
                raise RuntimeError("independent direct-expression and sparse reductions disagree")
    raw = external["corrected_witness_values_mod101"]
    reconciled = [row["fixed_Sylvester_determinant_mod101"]*pow(row["t"], 30, 101)*pow(row["M_mod101"], 14, 101) % 101 for row in eliminated["fixed_modular_witnesses"]]
    if raw != reconciled or raw != [65, 52, 20]:
        raise RuntimeError("raw versus normalized resultant scaling failed")
    return {"source_commit": "3cf518be4bed43e986c443e3ab107ba803e7ed01", "helper_core_sha256": INDEPENDENT_CORE,
            "source_and_test_pins": copy.deepcopy(INDEPENDENT_PINS),
            "four_N4_N3_linear_coefficients_identical_as_universal_expressions": True,
            "independent_raw_resultants_mod101": raw, "normalized_core_resultants_mod101": [81, 14, 16],
            "exact_scaling_law": "R4=t^6*M^2*R4core and C43=t^3*M^2*C43core; their h-degrees4,3 imply Res_h(R4,C43)=t^30*M^14*Res_h(R4core,C43core).",
            "all_three_scaling_residues_verified": True,
            "independent_correction_retracted_or_overwritten": False}


def build_certificate():
    inputs = load_inputs()
    quartic = inputs["v103_route"]["original_quartic_sections"]
    reduced_string = reduction_json(json.dumps(quartic, sort_keys=True))
    reduced = json.loads(reduced_string)
    eliminated = json.loads(elimination_json(reduced_string))
    witnesses = eliminated["fixed_modular_witnesses"]
    if [row["fixed_Sylvester_determinant_mod101"] for row in witnesses] != [81, 14, 16]:
        raise RuntimeError("the corrected fixed-degree determinant witnesses changed")
    if not all(row["M_mod101"] and row["h_degrees"] == [4, 3] for row in witnesses):
        raise RuntimeError("the corrected witness moved off Q2 or changed fixed degrees")
    out = {"schema": "v105_q2_source_conversion_repair_and_full_residual_reduction_v1",
           "status": "V104_DERIVED_CORE_EVIDENCE_RETRACTED__CORRECTED_CONFINEMENT_AND_FULL_Q2_POINT_SET_REDUCTION__NO_SECTION_OR_GATE_CLOSURE",
           "input_core_hashes": {k: v[1] for k, v in PARENTS.items()},
           "bound_quartic_core": canonical_sha(quartic),
           "bound_reduced_equations_sha256": quartic["quartic_reduced_equations_sha256"],
           "bound_coefficient_payload_sha256": quartic["coefficient_payload_sha256"],
           "source_conversion_forensics": reduced["basis_round_trips"],
           "corrected_reduction": reduced,
           "all_five_residual_elimination": eliminated,
           "independent_V105_correction_compatibility": independent_compatibility(reduced, eliminated),
           "common_root_reconstruction_theorem": common_root_theorem(),
           "retraction_and_replacement": {
               "frozen_V104_files_changed": False,
               "V104_source_converter_preserves_the_original_residuals": False,
               "all_five_actual_source_residuals_changed_by_old_converter": all(not row["historical_conversion_matches_source"] for row in reduced["rows"]),
               "specific_defect": "In declared ordering (t,p,q,h,alpha,beta,gamma,delta,epsilon), the old converter uses powers[4] for h and powers[5:] for parameters; it sends h to1, alpha to h, beta to alpha, gamma to beta, delta to gamma and epsilon to delta. Leading F/A2 calculations used a separate correct conversion, so reduction mixed different polynomial systems.",
               "V104_derived_cores_and_28_97_91_witnesses_accepted_as_original_Q2_evidence": False,
               "V104_leading_A2_identity_and_h_independent_discriminant_retained": True,
               "corrected_residual_division_identity_count": 5,
               "corrected_leading_R4_C43_t_M_contents": [[6, 2], [3, 2]],
               "corrected_R4_C43_h_degrees": [4, 3],
               "corrected_fixed_Sylvester_size": 7,
               "corrected_witnesses_mod101": [81, 14, 16],
               "Q2_confinement_reestablished_by_new_valid_proof": True,
               "proof_scope": "The universal h-degrees4 and3 are attained at all three coefficientwise X=1/mod101 slices. A nonzero fixed7x7 Sylvester determinant implies the determinant polynomial in X,t,p is not identically zero. Any actual common h root makes that fixed determinant vanish, including zero leading coefficients. Thus the projection of Q2 lies in its proper zero locus; no modular affine emptiness, no bounds on poles of t(X),p(X), and no rank specialization are used.",
               "full_Q2_exclusion_follows_from_nonzero_resultant": False,
           },
           "source_and_cache_boundary": {
               "parent_cores_and_sources_rechecked_on_every_build": True,
               "only_pure_immutable_json_calculations_cached": True,
               "returned_certificate_is_cached_mutable_state": False,
               "old_snapshot_self_consistency_is_an_independent_correctness_proof": False,
           },
           "preserved_frontier": copy.deepcopy(quartic["preserved_frontier"]),
           "terminal_decision": {"bounded_F105_repair_and_full_Q2_reduction_completed": True,
                                 "Q2_solved": False, "Q2_excluded": False, "Q1_or_target_systems_solved": False,
                                 "actual_nonzero_original_section_constructed": False, "original_exact_MW_rank_computed": False,
                                 "covariant_action_repair_constructed": False, "same_action_microscopic_parent_accepted": False,
                                 "theory_complete": False, "closed_gates": []},
           "primary_sources": [
               {"url": "https://docs.sympy.org/latest/modules/polys/internals.html", "use": "Polynomial rings bind monomial exponent tuples to an explicit generator ordering. V105 uses from_expr and independently checks all basis symbols and source-polynomial round trips; the old indexing error is reproduced directly from its frozen source."},
               {"url": "https://math.berkeley.edu/~bernd/cbms.pdf", "use": "Chapter4 gives the Sylvester resultant framework. V105 uses an explicitly assembled fixed-degree7x7 determinant for a necessary projection equation, not a generic no-point inference from a modular search."},
               {"url": "https://arxiv.org/pdf/0907.0298", "use": "The inherited elliptic-surface height and globally integral degree framework is retained. This step repairs algebra for the existing original quartic only and does not change rank, height targets, or physical gates."},
           ]}
    out["core_sha256"] = canonical_sha(out)
    return out


def validate_certificate(report):
    if report.get("core_sha256") != canonical_sha(report) or report != build_certificate():
        raise RuntimeError("V105 arithmetic, source lineage or scientific scope changed")


if __name__ == "__main__":
    inputs = load_inputs()
    snapshot = reduction_json(json.dumps(inputs["v103_route"]["original_quartic_sections"], sort_keys=True))
    print("All five exact source-division identities computed", flush=True)
    result = build_certificate()
    print(json.dumps({"core": result["core_sha256"], "rows": [{k: v for k, v in r.items() if k not in ("ell", "mu")} for r in result["corrected_reduction"]["rows"]], "elimination": result["all_five_residual_elimination"]}, indent=2))
