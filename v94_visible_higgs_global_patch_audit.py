"""F94: distinguish a local Phi descent formula from its global domain.

This computes a necessary period screen for an independently periodic axion
extension.  It is deliberately NOT a no-go for a Higgs WZ action with defects.
"""
from __future__ import annotations

import copy
from pathlib import Path

import sympy as sp
import susy_v91_multipath_g1_frontier_master_audit as common

ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v93_route": ("SUSY_V93_LOCALIZED_ANOMALY_R_LIFT_JACOBIAN_AUDIT.json",
                  "4f81852d9e272d3fb12946ad41cb01d9f93462f75cef69123106a80b03f092f2"),
    "v93_master": ("SUSY_V93_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
                   "d34479d8daa9a37d090e2d2ace471464171a0c28208d3d88b77e5dc168a97932"),
    "v90_route": ("SUSY_V90_EXTERNAL_C8_QUOTIENT_DAIFREED_REES_EQUIVARIANCE_AUDIT.json",
                  "ec095daa641345934d285a56a1916bf701352ee5cb113018296487ade36b966f"),
}
f, p, phi, epsilon = sp.symbols("f p phi epsilon")
E = sp.symbols("e1:6")


def load_parents():
    return {key: common.load_bound(ROOT / name, core)
            for key, (name, core) in PARENTS.items()}


def moments(rows):
    return {"TrQ": sum(r["copies"] * r["dim"] * r["q"] for r in rows),
            "TrQ3": sum(r["copies"] * r["dim"] * r["q"] ** 3 for r in rows)}


def pure_polynomial(trace):
    return sp.expand(sp.Rational(trace["TrQ3"], 6) * f ** 3
                     - sp.Rational(trace["TrQ"], 24) * f * p)


def finite_screen(trace, n=8):
    """Only the pullback to ordinary Spin(4) x C_n, other bundles trivial."""
    if n < 2:
        raise ValueError("nontrivial cyclic order required")
    cubic = (n*n + 3*n + 2) * trace["TrQ3"]
    linear = 2 * trace["TrQ"]
    return {"n": n, "cubic_numerator": cubic, "cubic_modulus": 6*n,
            "cubic_residue": cubic % (6*n), "linear_numerator": linear,
            "linear_modulus": n, "linear_residue": linear % n,
            "passes_this_restriction": cubic % (6*n) == 0 and linear % n == 0}


def higgs_line_trivialized(c1, torsion_order=None, charge=-8):
    """Necessary and sufficient topological condition for a nonzero section.

    Covers a single free Z summand or one explicitly supplied cyclic summand
    of H2, not the differential connection or equations of motion.
    """
    if torsion_order is None:
        return charge * c1 == 0
    if torsion_order < 1:
        raise ValueError("positive torsion order required")
    return (charge * c1) % torsion_order == 0


def content():
    parents = load_parents()
    route = parents["v93_route"]
    repair = parents["v90_route"]["charged_neutral_and_compensator_repair"]
    table = {r["field"]: r for r in repair["continuous_charge_table"]}
    if table["Phi_-"]["continuous_U1_8_charge"] != -8:
        raise RuntimeError("Phi charge changed")
    if not all(r["finite_is_continuous_mod8"] and
               r["finite_q8"] == r["continuous_U1_8_charge"] % 8
               for r in table.values()):
        raise RuntimeError("visible finite charge embedding changed")
    light_rows = repair["visible_zero_mode_conditional_shadow"]["signed_component_rows"]
    heavy_charges = route["smooth_R_and_wall_mass_extension"]["mass_anomaly_matching"]["heavy_left_Weyl_charges"]
    heavy_rows = [{"copies": 1, "dim": 1, "q": q} for q in heavy_charges]
    # Phi +/- is a vectorlike pair: it contributes zero odd moments.
    traces = {"light": moments(light_rows), "heavy": moments(heavy_rows),
              "full": moments(light_rows + heavy_rows)}
    if traces != {"light": {"TrQ": -104, "TrQ3": 544},
                  "heavy": {"TrQ": 36, "TrQ3": 864},
                  "full": {"TrQ": -68, "TrQ3": 1408}}:
        raise RuntimeError("independent visible moment census changed")
    polynomials = {key: pure_polynomial(value) for key, value in traces.items()}
    visible = route["bare_bulk_local_anomaly"]["calculation"]["conditional_visible_gauge_slice"]
    full_cartan = sp.sympify(visible["full_integrated_gauge_only_polynomial"])
    if sp.expand(full_cartan.subs(dict.fromkeys(E, 0)) - polynomials["full"]) != 0:
        raise RuntimeError("component census and frozen full Cartan polynomial disagree")
    if sp.expand(polynomials["full"] - polynomials["light"] - polynomials["heavy"]) != 0:
        raise RuntimeError("threshold anomaly sum failed")
    B = sp.cancel(full_cartan / f)
    counterterm = sp.expand(phi * B / 8)
    variation = sp.expand(counterterm.subs(phi, phi - 8*epsilon) - counterterm)
    if sp.expand(variation + epsilon*B) != 0:
        raise RuntimeError("local Phi cancellation sign failed")
    heavy_match = sp.expand(-phi * polynomials["heavy"] / (8*f))
    if sp.expand(heavy_match.subs(phi, phi - 8*epsilon) - heavy_match
                 - epsilon*polynomials["heavy"]/f) != 0:
        raise RuntimeError("heavy matching sign failed")
    below_threshold = sp.expand(counterterm + heavy_match)
    if sp.expand(below_threshold - phi*(full_cartan-polynomials["heavy"])/(8*f)) != 0:
        raise RuntimeError("matching plus cancellation fails the threshold identity")
    period_rows = []
    for key, poly in polynomials.items():
        four_form = sp.cancel(poly / (8*f))
        period = sp.expand(four_form.subs({p: 0, f**2: 2}))
        period_rows.append({"sector": key, "cancelling_phase_coefficient": str(four_form),
                            "S2xS2_f_square_2_period": str(period),
                            "period_mod_one": str(period % 1),
                            "passes_independent_periodic_scalar_test": bool(period.is_integer)})
    return {
        "schema": "v94_visible_higgs_global_patch_audit_v1",
        "status": "EXACT_VISIBLE_THRESHOLD_AND_PERIOD_SCREEN__DEFECT_FREE_DOMAIN_RESTRICTED__NO_GLOBAL_CANCELLATION",
        "input_core_hashes": {key: value[1] for key, value in PARENTS.items()},
        "census": {"moments": traces, "full_Phi_pair_odd_moments": [0, 0],
                   "independent_Cartan_crosscheck": True,
                   "pure_I6_by_sector": {key: str(value) for key, value in polynomials.items()},
                   "light_plus_heavy_equals_full": True},
        "local_descent": {"full_gauge_only_I6": str(full_cartan), "B4": str(B),
                          "new_formal_canceller": str(counterterm),
                          "variation": str(variation), "variation_is_minus_full_anomaly": True,
                          "existing_heavy_matching_term": str(heavy_match),
                          "canceller_plus_heavy_matching_below_threshold": str(below_threshold),
                          "below_threshold_variation_cancels_light_polynomial": True,
                          "heavy_matching_has_opposite_sign_to_canceller": True,
                          "adding_matching_erases_full_anomaly": False},
        "ordinary_period_screen": {
            "assumptions": "independently defined period-one scalar with delta phi=-8 epsilon; ordinary spin4 and integral covering U1 bundle; all other curvatures zero",
            "test_manifold": "S2 x S2, cohomology generators a,b with a^2=b^2=0 and integral(a*b)=1",
            "test_line": "c1(L)=f=a+b, integral(f^2)=2, p1=0; allowed liftable Spin^c(11) gauge background with trivial Spin11 bundle",
            "periods": period_rows,
            "full_period_shift_phase": "exp(2*pi*i*2/3)",
            "naive_full_independent_periodic_scalar_extension_rejected": True,
            "required_period_multiple_on_this_one_test_only": 3,
            "period_triple_is_the_actual_Phi_phase": False,
            "all_global_Higgs_WZ_completions_excluded": False,
        },
        "defect_free_domain": {
            "ordinary_covering_bundle": "Phi_minus is a section of L^(-8)",
            "nonzero_Phi_requires": "8*c1(L)=0 in integral H2; torsion may survive",
            "gauge_Spin_c11_bundle": "for determinant D and f=c1(D)/2, Phi_minus is a section of D^(-4), so 4*c1(D)=0",
            "test_background_admits_everywhere_nonzero_Phi": False,
            "test_obstruction_class_in_H2_S2xS2": [-8, -8],
            "zero_locus_signed_PD_class_if_transverse": "-8*(a+b)",
            "curvature_free_part_on_actual_nonzero_patch": "[f]_deRham=0, not pointwise F=0 and not trivial finite holonomy",
            "meaning": "The failed independent-scalar extension cannot be used to reject the actual nonzero-Higgs EFT: the test background forces Phi zeros and lies outside that patch. A theory including those backgrounds needs defect data or another completion.",
            "nonspin_or_full_Gammahat_bundle_reduction_solved": False,
        },
        "pure_C8_restrictions": {
            "formula": "(n^2+3n+2)*TrQ3=0 mod6n; 2*TrQ=0 modn",
            "scope": "ordinary Spin4 x C8 pullback with all other backgrounds trivial; not the mixed/full Gammahat anomaly and not the actual full-vacuum unbroken group",
            "sectors": {key: finite_screen(value) for key, value in traces.items()},
            "replacing_signed_charges_by_residues_preserves_the_screen": True,
            "pure_finite_pass_implies_continuous_or_global_anomaly_cancellation": False,
        },
        "nonabelian_slice_periods": {
            "SU3_c2_level_in_B_over_8": 4, "SU2_c2_level_in_B_over_8": 3,
            "derivation": "I6_mixed=-A_G*f*c2, with A3=-32 and A2=-24; each unit-instanton period is integral",
            "covers_all_mixed_quotient_bundles": False,
        },
        "boundary": {"full_quantized_relative_action_constructed": False,
                     "local_wall_normal_representations_frozen": False,
                     "all_gates_closed": False},
        "primary_sources": [
            {"url": "https://arxiv.org/abs/0802.0634", "use": "local anomaly descent and formal axion variation, equations12.6-12.9; not global quantization"},
            {"url": "https://arxiv.org/abs/1808.02881", "use": "equation1.2 on the explicitly restricted ordinary Spin4 x C8 background"},
            {"url": "https://arxiv.org/abs/2009.04692", "use": "section4: Goldstone fields require bundle reduction; nonreducible backgrounds force mass-field zeros beyond the Goldstone EFT"},
        ],
    }


def build_certificate():
    out = content()
    out["core_sha256"] = common.canonical_sha(out)
    return out


def validate_certificate(out):
    if out.get("core_sha256") != common.canonical_sha(out):
        raise RuntimeError("noncanonical visible patch certificate")
    body = copy.deepcopy(out)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("visible period arithmetic, lineage or scope changed")
