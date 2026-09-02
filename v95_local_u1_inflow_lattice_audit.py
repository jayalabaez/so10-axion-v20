"""F95: the bare fixed-locus U1 anomaly modulo ordinary Weyl polynomials.

This derives a necessary fractional inflow class, not a quantized inflow action.
The charge lattice is deliberately enlarged to all integer covering U1 charges:
failure in this lattice excludes ordinary localized Weyl matter in the frozen
gauge group, but success need not give a representation of that full group.
"""
from __future__ import annotations

import copy
from pathlib import Path

import sympy as sp
import susy_v91_multipath_g1_frontier_master_audit as common

ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v94_route": ("SUSY_V94_BOUNDARY_DEFECTS_AND_MW_DESCENT_AUDIT.json",
                  "17fd3a60008545b7bde77756ed8b5ec7dd590c18c1cbb1344a5a7cc67dd2686f"),
    "v94_master": ("SUSY_V94_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
                   "8332984113477ebbbc8a1bc44915475cc3c38003c8c3a7ac9c9a5e35fc11da06"),
    "v93_route": ("SUSY_V93_LOCALIZED_ANOMALY_R_LIFT_JACOBIAN_AUDIT.json",
                  "4f81852d9e272d3fb12946ad41cb01d9f93462f75cef69123106a80b03f092f2"),
}
f, p, x = sp.symbols("f p x")
E = sp.symbols("e1:6")


def load_parents():
    out = {key: common.load_bound(ROOT/name, core) for key,(name,core) in PARENTS.items()}
    if out["v94_master"]["next_required_action"]["id"] != "F95_RELATIVE_SPIN_NORMAL_DEFECT_GLUE_AND_INVARIANT_MW_SECTION":
        raise RuntimeError("F95 obligation changed")
    return out


def weyl_index(q):
    q = sp.Rational(q)
    return q**3*f**3/6-q*f*p/24


def moments(poly):
    poly = sp.Poly(sp.expand(poly), f, p)
    a, b = -24*poly.coeff_monomial(f*p), 6*poly.coeff_monomial(f**3)
    if sp.expand(poly.as_expr() - (b*f**3/6-a*f*p/24)) != 0:
        raise ValueError("expected only the pure U1 and mixed gravitational slice")
    return a, b


def lattice_coordinates(a, b):
    """(a,b) = n1*(1,1)+n2*(2,8); signed coefficients allow conjugates."""
    a,b = sp.Rational(a),sp.Rational(b)
    n2 = (b-a)/6
    return a-2*n2,n2


def lies_in_enlarged_Weyl_lattice(a, b):
    return all(v.is_integer for v in lattice_coordinates(a,b))


def cp3_index_period(poly):
    """CP3 is spin, p1=4H^2, f=H and integral(H^3)=1."""
    a,b = moments(poly)
    return sp.Rational(b-a,6)


def content():
    parents = load_parents()
    source = parents["v93_route"]["bare_bulk_local_anomaly"]["calculation"]
    fields = parents["v94_route"]["normal_wall_quantization"]["conditional_product_lift_wall_module"]["field_blocks"]
    if any(row["continuous_U1_8_charge"] != 0 for row in fields):
        raise RuntimeError("V94 normal module now changes the pure U1 slice")
    cover = {point:sp.expand(sp.sympify(row["total"]).subs(dict.fromkeys(E+(x,),0)))
             for point,row in source["per_stratum"].items()}
    physical = {"z00":cover["z00"], "z11":cover["z11"],
                "physical_C2_orbit":sp.expand(cover["z10"]+cover["z01"])}
    expected = {"z00":(sp.Rational(47,2),754), "z11":(sp.Rational(47,2),754),
                "physical_C2_orbit":(3,-60)}
    rows = []
    for point,poly in physical.items():
        a,b = moments(poly)
        if (a,b) != expected[point]:
            raise RuntimeError("frozen fixed-locus U1 moments changed")
        coordinates = lattice_coordinates(a,b)
        period = cp3_index_period(poly)
        rows.append({"stratum":point, "pure_I6":str(poly), "TrQ":str(a), "TrQ3":str(b),
                     "Q1_Q2_lattice_coordinates":[str(v) for v in coordinates],
                     "coordinates_mod_one":[str(v%1) for v in coordinates],
                     "CP3_index_period":str(period), "CP3_period_mod_one":str(period%1),
                     "is_ordinary_Weyl_polynomial":bool(lies_in_enlarged_Weyl_lattice(a,b))})
    total = sp.expand(sum(physical.values()))
    old_total = sp.sympify(source["zero_mode_index_crosscheck"]["integrated_fixed_gauge_polynomial"])
    if sp.expand(total-old_total.subs(dict.fromkeys(E,0))) != 0 or moments(total) != (50,1448):
        raise RuntimeError("integrated bulk and independently projected modes disagree")
    # A minimum-denominator representative in the enlarged Weyl lattice.
    coefficients = {"z00":sp.Rational(1,4), "z11":sp.Rational(1,4),
                    "physical_C2_orbit":-sp.Rational(1,2)}
    transfers = {point:sp.expand(c*weyl_index(2)) for point,c in coefficients.items()}
    if sp.expand(sum(transfers.values())) != 0:
        raise RuntimeError("fractional anomaly transfer is not zero-sum")
    repaired = []
    for point,poly in physical.items():
        shifted = sp.expand(poly+transfers[point])
        a,b = moments(shifted)
        if not lies_in_enlarged_Weyl_lattice(a,b):
            raise RuntimeError("proposed formal transfer fails to remove the fractional class")
        repaired.append({"stratum":point,"coefficient_of_charge2_Weyl_index":str(coefficients[point]),
                         "formal_inflow_polynomial":str(transfers[point]),
                         "bare_plus_transfer":str(shifted),
                         "shifted_TrQ_TrQ3":[str(a),str(b)],
                         "shifted_Q1_Q2_integer_coordinates":[str(v) for v in lattice_coordinates(a,b)],
                         "shifted_CP3_period":str(cp3_index_period(shifted))})
    A,B = moments(total)
    return {
        "schema":"v95_local_U1_inflow_lattice_v1",
        "status":"BARE_LOCAL_U1_FRACTION_REQUIRES_INFLOW_BEYOND_ORDINARY_WALL_WEYLS__FORMAL_ZERO_SUM_CLASS_FOUND",
        "input_core_hashes":{key:value[1] for key,value in PARENTS.items()},
        "normalization":{
            "gauge":"f=covering U1 curvature F/(2pi); all representations of the frozen covering U1 have integer q. Spin^c11 parity correlates q with Spin11 center but does not make q fractional.",
            "scope":"bare fixed-locus polynomial, x=0 and all Spin11 Cartan curvatures zero; bulk GS/inflow and unknown wall fields are not silently included",
            "V94_normal_module_changes_this_slice":False,
            "physical_C2_is_two_cover_points_summed":True,
        },
        "ordinary_Weyl_lattice":{
            "generators_TrQ_TrQ3":[[1,1],[2,8]],"matrix_determinant":6,
            "complete_criterion_for_enlarged_integer_charge_lattice":"TrQ is an integer and TrQ3-TrQ is divisible by6",
            "proof":"q^3-q=q(q-1)(q+1) is divisible by6 for every integerq. Conversely n2=(TrQ3-TrQ)/6 and n1=TrQ-2n2 reconstruct the pair using charge1 and charge2 Weyl polynomials. Negative coefficients are conjugate charges.",
            "adding_ordinary_wall_Weyls_changes_coordinates_by_integers":True,
            "actual_Gammahat_gauge_representation_lattice_is_subset":True,
            "charge1_generator_is_an_allowed_Spin_c11_gauge_singlet":False,
            "enlarged_lattice_success_constructs_actual_wall_representations":False,
        },
        "physical_fixed_loci":rows,
        "CP3_period_witness":{
            "manifold":"CP3", "tangent_c1":"4H", "spin":True,
            "p1":"4H^2", "gauge_line":"L=O(1), f=H", "integral_H_cubed":1,
            "gauge_quotient_admissibility":"trivial Spin11 bundle and covering lineL give a Spin^c11 bundle with determinantD=L^2",
            "ordinary_charge_q_index":"(q^3-q)/6, always integral",
            "test_is_a_standalone_Weyl_index_integrality_requirement":True,
            "test_is_full_six_dimensional_orbifold_Dai_Freed_phase":False,
            "nonzero_Higgs_phase_or_defect_free_condition_assumed":False,
        },
        "formal_zero_sum_inflow_target":{
            "charge2_index":str(weyl_index(2)),"rows":repaired,
            "sum_transfer":"0", "minimum_common_denominator_in_enlarged_lattice":4,
            "denominator_proof":"the Q2 coordinate at either C4 has fractional part 3/4. Integer wall shifts cannot remove it, so a common denominator for the rational lattice coordinates must be divisible by 4; the displayed representative attains 4",
            "signed_localized_source_weights":["1/4","1/4","-1/2"],
            "global_integrated_polynomial_unchanged":True,
            "not_unique":"integer Weyl-polynomial transfers can be added with zero total; the displayed choice is a representative of the required fractional classes",
            "quantized_bulk_tensor_or_relative_differential_action_constructed":False,
            "all_mixed_Spin11_normal_or_R_anomalies_cancelled":False,
            "success_means":"only that the PURE U1 local remainder lands in an enlarged ordinary-Weyl lattice; the remainder is nonzero and still needs physical cancellation",
        },
        "global_crosscheck":{
            "TrQ_TrQ3":[int(A),int(B)],"pure_bulk_I6":str(total),
            "Q1_Q2_coordinates":[str(v) for v in lattice_coordinates(A,B)],
            "CP3_period":str(cp3_index_period(total)),
            "fractional_classes_sum_to_zero":True,
            "integrated_bulk_anomaly_is_zero":False,
            "full_visible_TrQ_TrQ3_unchanged":[parents["v94_route"]["visible_Higgs_patch_and_periods"]["census"]["moments"]["full"][key] for key in ("TrQ","TrQ3")],
            "zero_sum_transfer_cancels_full_visible_anomaly":False,
        },
        "terminal_decision":{
            "ordinary_localized_Weyl_matter_alone_cancels_bare_local_U1_anomaly":False,
            "new_inflow_obligation_specified_exactly_in_pure_U1_slice":True,
            "all_possible_inflow_or_topological_completions_excluded":False,
            "quantized_relative_completion_constructed":False,
            "same_action_parent_accepted":False,"closed_gates":[],
        },
        "primary_sources":[
            {"url":"https://arxiv.org/abs/hep-th/0612212","use":"Sections3.1 and4 distinguish fractional bare bulk fixed-point contributions, localized Weyl anomalies and bulk Green-Schwarz inflow; integrated cancellation alone is insufficient."},
            {"url":"https://arxiv.org/abs/0802.0634","use":"Weyl anomaly as the degree-six Ahat*Chern-character index density; local descent is distinct from global completion."},
            {"url":"https://arxiv.org/abs/1808.01334","use":"Index integrality and the distinction between polynomial matching and a differential anomaly theory."},
        ],
    }


def build_certificate():
    out=content()
    out["core_sha256"]=common.canonical_sha(out)
    return out


def validate_certificate(out):
    if out.get("core_sha256")!=common.canonical_sha(out):
        raise RuntimeError("noncanonical local U1 inflow certificate")
    body=copy.deepcopy(out)
    body.pop("core_sha256")
    if body!=content():
        raise RuntimeError("local U1 lattice arithmetic, lineage or scope changed")
