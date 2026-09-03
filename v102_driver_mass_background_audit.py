"""F102: one component-line network for the written drivers, masses and Yukawas.

This constructs compatible restricted Cartan weights, not missing localized
Gammahat representations or a nonlinear quaternionic-Kahler vacuum. Fixed
constants are not replaced by transforming spurions. No gate is closed.
"""
from __future__ import annotations

import copy
from functools import lru_cache
import json
from pathlib import Path

import sympy as sp

import v101_higgs_background_restriction_audit as previous

ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v101_route": ("SUSY_V101_COVER_LIFT_HIGGS_SECTION_SOLVABILITY_AUDIT.json", "a2c321a1889b312305dca187fda511892a2d0e9b3e9e9b18fbcd0a2b9cba42b6"),
    "v101_master": ("SUSY_V101_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json", "f9ce5079b759b615190564bd41b6e9783e6244889bb3e7237e63132cb23f5300"),
}
HIGGS_CORE = "0bb2dc688f660d85e2d20dc1d1075251209d749a86497bd7b0ff4b67bcbe805b"
CHARGE_TABLE_CORE = "bb55101fbede403d6c2b8e6b3d7dcaf9029dcae6ffe850af42b54c56d79d984d"
canonical_sha, file_sha, matrix, mj = previous.canonical_sha, previous.file_sha, previous.matrix, previous.mj
x, r, d, h, s = sp.symbols("x r d h s")
W = x+2*r
FIELD_NAMES = ("Phi_+", "Phi_-", "B0", "X", "Xbar", "S8", "SB", "SX", "A0", "P_A",
               "H_uA", "H_uB", "H_dC", "H_dSigma", "D", "Dbar", "10", "5bar", "1", "S2", "S4", "S6")
FIELDS = {name: sp.Symbol("ell_"+name.replace("+", "plus").replace("-", "minus")) for name in FIELD_NAMES}
VEVS = ("Phi_+", "Phi_-", "B0", "X", "Xbar")
DRIVERS = (("S8", "v8_squared", ("Phi_+", "Phi_-")),
           ("SB", "vB_squared", ("Phi_-", "B0", "B0")),
           ("SX", "vX_squared", ("X", "Xbar")))


def load_inputs():
    p = {k: previous.common.load_bound(ROOT/name, core) for k, (name, core) in PARENTS.items()}
    route, master = p["v101_route"], p["v101_master"]
    if master["input_core_hashes"]["v101_route"] != PARENTS["v101_route"][1] or master["next_required_action"]["id"] != "F102_NONZERO_PIVOT_SECTION_CHARTS_AND_COMMON_ACTION_BACKGROUND_RECONSTRUCTION":
        raise RuntimeError("V101 lineage or F102 obligation changed")
    for report, base in ((route, "susy_v101_cover_lift_higgs_section_solvability_audit"),
                         (master, "susy_v101_multipath_g1_frontier_master_audit")):
        for name, key in ((base+".py", "generator_sha256"), ("test_"+base+".py", "test_sha256")):
            if file_sha(ROOT/name) != report["artifact_hashes"][key]:
                raise RuntimeError("V101 source/test changed: "+name)
    saved = route["Higgs_background_restriction"]
    if saved.get("core_sha256") != HIGGS_CORE or canonical_sha(saved) != HIGGS_CORE:
        raise RuntimeError("frozen Higgs certificate changed")
    for name in ("v101_higgs_background_restriction_audit.py", "test_v101_higgs_background_restriction_audit.py"):
        if file_sha(ROOT/name) != route["artifact_hashes"][name]:
            raise RuntimeError("frozen Higgs source/test changed: "+name)
    old = previous.load_inputs()  # Rebind V92 projectors, V93 R/tensors and V95 theta.
    for key, base in (("v90", "susy_v90_external_c8_quotient_daifreed_rees_equivariance_audit"),
                      ("v70", "susy_v70_spin11_localized_parent_spin_flavor_completion_audit")):
        for name, pin in ((base+".py", "generator_sha256"), ("test_"+base+".py", "test_sha256")):
            if file_sha(ROOT/name) != old[key]["artifact_hashes"][pin]:
                raise RuntimeError("actual old coupling source/test changed: "+name)
    repair = old["v90"]["charged_neutral_and_compensator_repair"]
    if repair["continuous_charge_table_sha256"] != CHARGE_TABLE_CORE or canonical_sha(repair["continuous_charge_table"]) != CHARGE_TABLE_CORE:
        raise RuntimeError("the authoritative V90 charges changed")
    p.update(old)
    p["saved_higgs"] = saved
    return p


def line_sum(factors, values):
    return sp.expand(sum((-values["B0"] if f == "B0_dag" else values[f]) for f in factors))


def coupling_network(p):
    repair = p["v90"]["charged_neutral_and_compensator_repair"]
    ledger = copy.deepcopy(repair["corrected_compensator"]["operator_ledger"])
    if len(ledger) != 17 or sum(bool(row["superpotential_allowed"]) for row in ledger) != 12 or sum(bool(row["Kahler_allowed"]) for row in ledger) != 1:
        raise RuntimeError("the complete written V90 operator ledger changed")
    registry = repair["operator_charge_registry"]
    for row in ledger:
        q = sum(registry[f]["U1_8"] for f in row["factors"])
        X = sum(registry[f]["U1_X"] for f in row["factors"])
        R = sum(registry[f]["Z4R"] for f in row["factors"]) % 4
        if (q, X, R) != (row["U1_8_sum"], row["U1_X_sum"], row["Z4R_sum_mod4"]):
            raise RuntimeError("a source operator's continuous or discrete charges changed")
    rows = []
    for i, row in enumerate(ledger):
        allowed = row["selection_rule_allowed"]
        target = W if row["operator_kind"] == "superpotential" else sp.Integer(0)
        rows.append({"id": "V90_"+str(i+1), "source": "V90 corrected_compensator.operator_ledger", **row,
                     "include_in_constant_tensor_system": allowed,
                     "target_line_c1": str(target), "field_product_c1": str(line_sum(row["factors"], FIELDS)),
                     "required_coefficient_line_c1": str(sp.expand(target-line_sum(row["factors"], FIELDS)))})
    for driver, constant, factors in DRIVERS:
        source = next(row for row in ledger if row["factors"][0] == driver)
        if tuple(source["factors"][1:]) != factors:
            raise RuntimeError("a fixed driver polynomial changed")
        rows.append({"id": "V90_constant_"+driver, "source": "V90 named driver and F_flat_relations",
                     "operator": "-"+driver+"*"+constant, "factors": [driver],
                     "fixed_nonzero_neutral_constant": constant,
                     "include_in_constant_tensor_system": True, "operator_kind": "superpotential",
                     "target_line_c1": str(W), "field_product_c1": str(FIELDS[driver]),
                     "required_coefficient_line_c1": str(W-FIELDS[driver])})
    wall = p["v93_route"]["smooth_R_and_wall_mass_extension"]["fixed_wall_selection"]
    if wall["new_wall_tensor"] != "Phi_minus*(S2^T lambda S6 + S4^T kappa S4/2), with lambda=I3,kappa=I3 as a witness":
        raise RuntimeError("the selected V93 tensor changed")
    for label, factors in (("lambda", ["Phi_-", "S2", "S6"]), ("kappa", ["Phi_-", "S4", "S4"])):
        rows.append({"id": "V93_"+label, "source": "V93 fixed_wall_selection.new_wall_tensor",
                     "operator": "*".join(factors), "factors": factors, "operator_kind": "superpotential",
                     "include_in_constant_tensor_system": True, "target_line_c1": str(W),
                     "field_product_c1": str(line_sum(factors, FIELDS)),
                     "required_coefficient_line_c1": str(W-line_sum(factors, FIELDS))})
    return rows


def equations(network, include_GM=True):
    rows = [(row["id"], line_sum(row["factors"], FIELDS)-(W if row["operator_kind"] == "superpotential" else 0))
            for row in network if row["include_in_constant_tensor_system"] and (include_GM or row["operator_kind"] != "Kahler")]
    rows.extend(("nonzero_VEV_"+f, FIELDS[f]) for f in VEVS)
    rows += [("actual_hyper_A_partner", FIELDS["A0"]+FIELDS["H_uA"]-2*r),
             ("actual_hyper_B_partner", FIELDS["B0"]+FIELDS["H_uB"]-2*r),
             ("actual_Sigma_normal_character", FIELDS["H_dSigma"]-x)]
    return rows


def general_solution():
    return {"Phi_+": 0, "Phi_-": 0, "B0": 0, "X": 0, "Xbar": 0,
            "S8": W, "SB": W, "SX": W, "A0": 2*r-h, "P_A": x+h,
            "H_uA": h, "H_uB": 2*r, "H_dC": -h, "H_dSigma": x,
            "D": h, "Dbar": W-h, "10": (W-h)/2, "5bar": (W+3*h)/2,
            "1": (W-5*h)/2, "S2": s, "S4": W/2, "S6": W-s}


def solve_network(network):
    rows = equations(network)
    variables = [FIELDS[k] for k in FIELD_NAMES]
    M, b = sp.linear_eq_to_matrix([z for _, z in rows], variables)
    solution = general_solution()
    values = sp.Matrix([solution[k] for k in FIELD_NAMES])
    residual = (M*values-b).applyfunc(sp.expand)
    directions = sp.Matrix.hstack(values.diff(h), values.diff(s))
    noGM, _ = sp.linear_eq_to_matrix([z for _, z in equations(network, False)], variables)
    if residual != sp.zeros(M.rows, 1) or M.rank() != 20 or M.row_join(b).rank() != 20 or directions.rank() != 2 or M*directions != sp.zeros(M.rows, 2):
        raise RuntimeError("the exact common-action line solution changed")
    if noGM.rank() != 19:
        raise RuntimeError("the GM term ceased to impose an independent constraint")
    roots = {"A": h-r-3*d, "B": -r-2*d, "C": -h-r-3*d}
    return {
        "scope": "All actually displayed V90 allowed monomials, including the GM Kahler term, each nonzero neutral driver constant, the V93 lambda/kappa tensors, five selected line-valued VEVs, and the source-derived A/B hyper and Sigma relations. Use one common background line for each named matter component across families; this is a sufficient uniform-family tensor ansatz, not a proof that arbitrary missing family bundles share that line.",
        "field_order": list(FIELD_NAMES), "equation_order": [k for k, _ in rows],
        "integer_coefficient_matrix": [[int(v) for v in row] for row in M.tolist()],
        "parameter_rhs": [str(z) for z in b], "matrix_rank": M.rank(), "augmented_rank": M.row_join(b).rank(),
        "number_of_fields": len(FIELD_NAMES), "number_of_equations": len(rows),
        "rational_solution_dimension": 2, "rank_without_GM": noGM.rank(),
        "parameters": "h=L_HuA, s=L_S2, W=x+2r; the frozen V101 continuation chooses s=W/2",
        "complete_rational_component_line_solution": {k: str(sp.expand(solution[k])) for k in FIELD_NAMES},
        "nullspace_parameter_directions": [[str(z) for z in row] for row in directions.tolist()],
        "all_equation_residuals": [str(z) for z in residual],
        "required_actual_H3_positive_roots": {k: str(v) for k, v in roots.items()},
        "integral_line_class_boundary": "Every original tensor equation is a relation among integral associated line classes. The displayed general solution divides by2 and is complete over Q/real curvature only; on spaces with torsion, square-root choices and finite refinements are not classified by this elimination. CP3 is treated integrally below.",
        "GM_effect": "After the five nonzero VEV lines are trivial, the nonholomorphic operator Phi_minus B0^dag H_uA H_dC requires L_HuA+L_HdC=0. Discarding it would leave an extra free line parameter. It is not replaced by an arbitrary holomorphic Kahler transformation or a charged coefficient.",
        "bulk_Sigma_boundary": "H_dSigma carries the normal character N and adjoint gauge representation, with no R/flavor scalar factor. B0 H_uB H_dSigma is the selected component of the mandatory bulk gauge interaction, not a newly installed arbitrary local Sigma polynomial; its higher-dimensional gauge shift must still be respected.",
        "all_missing_localized_representations_constructed": False,
    }


def cp3_values(k, s_degree=1):
    if type(k) is not int or type(s_degree) is not int:
        raise ValueError("integral CP3 parameters k and s_degree are required")
    substitutions = {x: 1, r: sp.Rational(1, 2), d: 1, h: 2*k, s: s_degree}
    return {name: sp.sympify(value).subs(substitutions) for name, value in general_solution().items()}


def H3_matrix_certificate(p, k):
    if type(k) is not int:
        raise ValueError("integer k required")
    saved = p["v93_route"]["smooth_R_and_wall_mass_extension"]["old_smooth_bulk_R_extension"]
    if saved["A3_exponents_mod8"] != [7, 1, 3, 1, 7, 5] or saved["H_AC_exponents_mod8"] != [4, 0, 4, 4, 0, 4]:
        raise RuntimeError("actual H3 ordered twists changed")
    positive = [2*k-sp.Rational(7, 2), -sp.Rational(5, 2), -2*k-sp.Rational(7, 2)]
    H = sp.diag(*(positive+[-z for z in positive]))
    J = previous.projectors.symplectic_form(3)
    A = sp.diag(*(previous.ZETA**n for n in saved["A3_exponents_mod8"]))
    T = sp.diag(*(previous.ZETA**n for n in saved["H_AC_exponents_mod8"]))
    Rtilde = matrix(saved["flavor_D_H3"])
    Q = sp.diag(6, 4, 6, -6, -4, -6)
    external = sp.diag(*(previous.ZETA**q for q in Q.diagonal()))
    real = sp.kronecker_product(previous.projectors.symplectic_form(1), J)
    scalar = sp.kronecker_product(sp.diag(sp.Rational(1, 2), -sp.Rational(1, 2)), sp.eye(6))+sp.kronecker_product(sp.eye(2), H+Q/2)
    checks = {"Hermitian": H.conjugate().T == H, "symplectic_Lie_algebra": H.T*J+J*H == sp.zeros(6),
              "quaternionic_path_reality": J*sp.conjugate(H)+H*J == sp.zeros(6),
              "same_endpoint_minus_I6": all(sp.simplify(sp.exp(2*sp.pi*sp.I*z)) == -1 for z in H.diagonal()),
              "full_scalar_real_involution": real*sp.conjugate(real) == sp.eye(12),
              "full_scalar_path_reality": real*sp.conjugate(scalar)+scalar*real == sp.zeros(12)}
    checks.update({"commutes_"+name: H*M == M*H for name, M in (("A3", A), ("H_AC", T), ("Rtilde", Rtilde), ("charge", Q), ("primitive_k", external))})
    if not all(checks.values()):
        raise RuntimeError("the retuned old H3 background failed matrix checks")
    return {"positive_roots": [str(z) for z in positive], "paired_generator": mj(H),
            "actual_A3": mj(A), "actual_H_AC": mj(T), "actual_Rtilde": mj(Rtilde),
            "continuous_charge_matrix": mj(Q), "full_scalar_weight_generator": mj(scalar), "checks": checks,
            "existing_H3_hyper_count": 3, "new_H3_matter_installed": False}


def cp3_certificate(p, network, k):
    values = cp3_values(k)
    residuals = [sp.expand(line_sum(row["factors"], values)-(2 if row["operator_kind"] == "superpotential" else 0))
                 for row in network if row["include_in_constant_tensor_system"]]
    if any(z != 0 for z in residuals) or any(value.q != 1 for value in values.values()):
        raise RuntimeError("CP3 common tensor solution is not integral or covariant")
    assigned = {name: int(z) for name, z in values.items()}
    return {"k": k, "h": 2*k, "s_degree": 1, "N_D": ["O(1)", "O(1)"],
            "R_first_root": "1/2", "W_line": "O(2)", "selected_component_degrees": assigned,
            "all_allowed_constant_tensor_residuals": [int(z) for z in residuals],
            "old_H3_matrix_certificate": H3_matrix_certificate(p, k),
            "H267_profile_unchanged_from_V101": "selected_mass_tensor_compensation",
            "full_known_cocharacter_endpoint": [0, 1, 0, 1, 1, 1, 1],
            "all_five_selected_VEV_lines_trivial": all(assigned[name] == 0 for name in VEVS),
            "linear_associated_weight_zero_sections_can_be_parallel": True,
            "parallel_scope": "For the explicitly induced one-parameter background connection, these five LINEAR associated characters are trivial, so constant sections are parallel. This is stronger than topological triviality alone, but does not extend the origin's linear representation to a nonlinear QK field configuration or supply a preserved supercharge on CP3.",
            "D4_trivial": False, "normal_N_trivial": False,
            "P_over4_period": "3/8", "normal_R_gauge_curvatures_unchanged": True,
            "full_new_background_anomaly_recomputed": False,
            "localized_component_line_weights_are_full_representations": False,
            "full_same_action_physical_background_proved": False,
            "unbroken_supercharge_or_SUSY_vacuum_constructed": False}


def V101_failure_diagnostic():
    # V101 retuned H267, but left all positive H3 roots at +1/2.
    r0 = sp.Rational(1, 2)
    B = previous.scalar_line(r0, r0, 1, 4, "plus")
    uA = previous.scalar_line(r0, r0, 1, 6, "plus")
    dC = previous.scalar_line(r0, r0, 1, 6, "plus")
    return {
        "unchanged_V101_H3_positive_roots": ["1/2", "1/2", "1/2"],
        "B0_degree": int(B), "H_uA_H_dC_degrees": [int(uA), int(dC)],
        "SB_linear_constant_term_forces_SB_degree": 2,
        "SB_Phi_minus_B0_squared_product_degree_with_SB2": int(2+2*B),
        "that_superpotential_term_required_degree": 2,
        "hypothetical_vB_squared_spurion_degree_to_avoid_conflict": int(2*B),
        "V101_selected_mass_cocharacter_extends_without_retuning_H3": False,
        "first_exact_obstruction": "B0 is O(3), hence cannot be the everywhere-nonzero selected field demanded by fixed nonzero Phi_minus B0^2/M*=vB^2. Independently, the SB linear and cubic terms disagree by O(6) when vB^2 is an actual fixed neutral constant.",
        "B_only_retuning": {"positive_hB": "-5/2", "B0_degree": 0,
                             "GM_product_degree_if_A_C_unchanged": int(uA+dC),
                             "required_GM_coefficient_line_degree": int(-uA-dC),
                             "all_written_constant_tensors_preserved": False},
        "spurions_or_charged_constants_installed": False,
    }


def optional_legacy_and_forbidden(p, network):
    legacy = p["v70"]["localized_parent_completion_branches"]["integer_m301_dynamical_reduction"]["complete_renormalizable_local_operator_ledger"]
    if "M_N N N X" not in legacy["allowed_local_terms"] or legacy["arbitrary_local_Sigma_polynomial"] != "FORBIDDEN_BY_THE_HIGHER_DIMENSIONAL_GAUGE_SHIFT":
        raise RuntimeError("legacy source boundary changed")
    registry = p["v90"]["charged_neutral_and_compensator_repair"]["operator_charge_registry"]
    q = 2*registry["1"]["U1_8"]+registry["X"]["U1_8"]
    Xq = 2*registry["1"]["U1_X"]+registry["X"]["U1_X"]
    R = (2*registry["1"]["Z4R"]+registry["X"]["Z4R"]) % 4
    extra = sp.expand(2*general_solution()["1"]+general_solution()["X"]-W)
    if (q, Xq, R, extra) != (0, 0, 2, -5*h):
        raise RuntimeError("optional legacy Majorana screen changed")
    old_extra = {}
    for name, factors in (("A0 H_uA H_dC", ("A0", "H_uA", "H_dC")), ("H_uB H_dC", ("H_uB", "H_dC"))):
        old_extra[name] = sum(registry[f]["U1_8"] for f in factors)
    forbidden = [row for row in network if not row["include_in_constant_tensor_system"]]
    return {
        "V90_forbidden_rows_retained_not_added": [{"operator": row["operator"], "source_factors": row["factors"],
                                                   "Z4R_sum_mod4": row["Z4R_sum_mod4"], "source_gauge_charge_sum": row["U1_8_sum"]} for row in forbidden],
        "forbidden_operators_promoted_by_Chern_class_coincidence": False,
        "optional_V70_Majorana": {"operator": "M_N N N X", "written_in_V70": True,
                                   "explicitly_reinstalled_in_V90_operator_ledger": False,
                                   "V90_charge_X_R_totals": [q, Xq, R],
                                   "additional_constant_tensor_residual": str(extra),
                                   "integral_necessary_condition": "5 L_HuA=0 in the tensor-line network; torsion solutions are not classified",
                                   "on_CP3_forces_h_k_zero": True,
                                   "k0_witness_passes": extra.subs(h, 0) == 0,
                                   "adopted_as_new_action_term": False},
        "nonimportable_legacy_terms_continuous_charge_sums": old_extra,
        "legacy_import_scope": "V70 terms that fail the V90 continuous charge selector are not part of the new network. The optional still-allowed Majorana term is tested separately; a permission in an older ledger is not a completed microscopic coupling.",
    }


@lru_cache(maxsize=2)
def _pure_json(input_json):
    p = json.loads(input_json)
    network = coupling_network(p)
    return json.dumps({"source_bound_operator_network": network, "common_component_line_system": solve_network(network),
                       "V101_unretuned_H3_obstruction": V101_failure_diagnostic(),
                       "CP3_common_tensor_witness_k0": cp3_certificate(p, network, 0),
                       "CP3_common_tensor_witness_k2": cp3_certificate(p, network, 2),
                       "legacy_and_forbidden_boundary": optional_legacy_and_forbidden(p, network)},
                      sort_keys=True, separators=(",", ":"))


def build_certificate():
    p = load_inputs()
    compact = {k: p[k] for k in ("v70", "v90", "v93_route")}
    out = {
        "schema": "v102_written_driver_mass_and_GM_common_background_network_v1",
        "status": "V101_H3_BACKGROUND_FAILS_FIXED_B_DRIVER__PARAMETERIZED_WRITTEN_TENSOR_REPAIR__FULL_REPRESENTATIONS_AND_VACUUM_OPEN",
        "input_core_hashes": {k: v[1] for k, v in PARENTS.items()}, "bound_V101_Higgs_core": HIGGS_CORE,
        "bound_earlier_core_hashes": {k: p[k]["core_sha256"] for k in ("v70", "v90", "v92_route", "v93_route", "v95_route")},
        "bound_V90_charge_table_sha256": CHARGE_TABLE_CORE,
        "curvature_and_tensor_conventions": {
            "normal_gauge_R": "x=c1(N),d=c1(D),r=first formal R root; theta has internal curvature x/2+r and the superpotential line is W=N R_+^2 with c1=x+2r",
            "normal_Sigma": "Sigma transforms like the holomorphic normal derivative, with character N and adjoint gauge action; H_dSigma has common normal line x on the gauge-trivial CP3 scout",
            "background_gauge_scope": "Common line factors are evaluated on the V100 Spin11-trivial cocharacter; full U5 representation contractions, their center descent and localized flavor modules are not supplied by naming these component lines.",
            "Kahler_measure": "The normal/R characters of d2theta and d2bar_theta cancel. The displayed nonholomorphic GM monomial must be an ordinary scalar for a fixed neutral coefficient.",
            "constants": "v8^2,vB^2,vX^2,M*,M_A and the displayed nonzero mass/Yukawa tensors are fixed neutral coefficients in this test, not additional transforming fields. A nonzero fixed tensor reduces the allowed background symmetry to its stabilizer.",
            "line_section_scope": "The five VEVs are selected complex component sections. With fixed nonzero driver constants the F-product equations force these five sections nowhere zero. If a full higher-rank contraction replaces them, its nonzero value is a different reduction problem, not proof that every component line is trivial.",
            "full_curved_N1_or_QK_action_constructed": False,
        },
        **json.loads(_pure_json(json.dumps(compact, sort_keys=True))),
        "integral_CP3_family": {
            "parameter_rule": "h=2k and s integer, k integer; V101 mass-sector continuation fixes s=1",
            "necessity": "With x=d=1,r=1/2, the genuine selected 10 line has degree1-h/2; integer HuA and10 degrees therefore force h even. S2 andS6 have degrees s and2-s. Every other displayed line is then integral.",
            "H3_positive_roots": ["2k-7/2", "-5/2", "-2k-7/2"],
            "same_KN_plus_KS_endpoint_for_every_integer_k": True,
            "k0_advantage": "Small integral component degrees; also preserves the optional legacy N N X tensor.",
            "k2_advantage": "Leaves the original positive A-hyper flavor root+1/2 untouched and retunes only B and C within H3; does not preserve the optional legacy Majorana tensor without a further change.",
            "full_background_or_supersymmetric_vacuum_accepted": False,
        },
        "F_D_and_spectrum_boundary": {
            "source_F_products": copy.deepcopy(p["v90"]["charged_neutral_and_compensator_repair"]["vacuum"]["F_flat_relations"]),
            "source_D_flat_magnitude_witness": copy.deepcopy(p["v90"]["charged_neutral_and_compensator_repair"]["vacuum"]["D_flat_witness"]),
            "magnitude_witness_is_global_covariantly_constant_solution": False,
            "drivers_are_not_assumed_to_have_nonzero_VEVs": True,
            "linear_driver_terms_still_impose_tensor_constraints_at_zero_driver_VEV": True,
            "derived_M_mu": "Both M D Dbar and mu H_uA Dbar come from Phi_minus B0 times fixed coefficients; on the selected nonzero-VEV patch their coefficient lines are trivial. The one-sided tree-level elimination retains W_eff=-mu H_uA A_matter/M, with no A_matter^2 term in this local algebra.",
            "mass_gap_of_entire_background_proved": False,
            "all_projected_out_UV_fields_or_flavor_curvatures_discarded": False,
            "old_N40_replacement_can_borrow_this_Phi_sector": False,
            "UV_zeros": "Outside the everywhere-nonzero component patch, zeros of Phi/B0/X or mass determinants require the ultraviolet fields and anomaly matching. Tensor covariance of one low-energy patch does not erase these backgrounds or compute their defects.",
            "external_gauge_only_VEV_charge_gcd": 2,
            "gcd2_is_full_internal_R_flavor_stabilizer": False,
            "finite_residual_anomaly_computed": False,
        },
        "terminal_decision": {
            "written_constant_tensor_network_reconstructed": True,
            "unretuned_V101_selected_mass_cocharacter_satisfies_V90_fixed_driver": False,
            "restricted_CP3_common_tensor_weights_constructed": True,
            "all_localized_Gammahat_representations_constructed": False,
            "all_global_QK_and_constant_tensor_stabilizers_constructed": False,
            "full_spectrum_vacuum_or_anomaly_completion": False,
            "same_action_microscopic_parent_accepted": False, "theory_complete": False, "closed_gates": [],
        },
        "primary_sources": [
            {"url": "https://arxiv.org/abs/hep-th/0602155", "use": "The bulk hyper action in equation1 uses the covariant normal derivative plus Sigma. Equations44-45 give Sigma its derivative character and paired hyper twists. This supports the actual bulk B relation; it does not authorize arbitrary local Sigma polynomials."},
            {"url": "https://arxiv.org/abs/2009.04692", "use": "Section4 distinguishes a bundle reduction admitting a nonzero Higgs/mass field from UV configurations forced through zeros; full anomaly matching persists beyond the fixed-modulus patch."},
            {"url": "https://arxiv.org/abs/1808.01334", "use": "Section2.1 describes six-dimensional hypermultiplet reality. The H3 Cartan generator retains the paired real representation without adding particles; component weights alone do not construct a gauged QK action or its quantum anomaly trivialization."},
        ],
    }
    out["core_sha256"] = canonical_sha(out)
    return out


def validate_certificate(out):
    if out.get("core_sha256") != canonical_sha(out) or out != build_certificate():
        raise RuntimeError("F102 driver tensor, background, source binding or scope changed")


if __name__ == "__main__":
    print(json.dumps(build_certificate(), indent=2, sort_keys=True))
