"""F93: the shifted-character singlet contribution to the fixed-locus I6.

This extends the pinned V71 spin-half normal kernel with the actual continuous
charge operator of the pinned V92 eleven-mode witness.  It does not replace the
fixed-point character by the spectrum of fields nonzero at that point.  The
SMW factor one half is applied to the full conjugate symplectic representation.
No wall matter, GS counterterm, global determinant, or anomaly trivialization
is supplied by this helper.
"""
from __future__ import annotations

import copy
from functools import lru_cache
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v71": ("SUSY_V71_SPIN11_NORMAL_BUNDLE_EQUIVARIANT_GS_AUDIT.json",
            "0162828ebd2b1e28d4fcbcf4ea1e6c61178d305cec79abd6d36a55719bb0f1ea"),
    "v92_route": ("SUSY_V92_PROJECTORS_LENS_WCS_COMPACT_DECK_ROOT_AUDIT.json",
                  "3d4365681c9ebdbcbda6d9d57377a1046a6ab00b3a8b1b2290f2858a7ee4f4fb"),
    "v92_master": ("SUSY_V92_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
                   "e38e8b58d4f86e00271402c9580919a092e024b737a4fc5290e4d20709b5aae8"),
}
PROJECTOR_CORE = "5d4c91e596ef5182b63f5be4869a41c0c79005dc4dd0fc8cf3683d12c66363fd"
POINTS = ("z00", "z11", "z10", "z01")
MONOMIALS = ("f3", "f_p1T4", "x_f2", "x2_f", "x3", "x_p1T4")
# (power of the normal root, power of the continuous U1 root, Ahat coefficient)
TERMS = {"f3": (0, 3, 1), "f_p1T4": (0, 1, -sp.Rational(1, 24)),
         "x_f2": (1, 2, 1), "x2_f": (2, 1, 1), "x3": (3, 0, 1),
         "x_p1T4": (1, 0, -sp.Rational(1, 24))}
ZETA = (1 + sp.I) / sp.sqrt(2)


def canonical_sha(value):
    body = copy.deepcopy(value)
    body.pop("core_sha256", None)
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def matrix(rows):
    return sp.Matrix([[sp.sympify(x) for x in row] for row in rows])


def clean(value):
    return sp.Matrix(value).applyfunc(sp.simplify)


def zero(value):
    return clean(value) == sp.zeros(value.rows, value.cols)


def serialize_matrix(value):
    return [[str(x) for x in row] for row in clean(value).tolist()]


def serialize_polynomial(value):
    result = {}
    for name in MONOMIALS:
        coefficient = sp.simplify(value[name])
        if not coefficient.is_Rational:
            raise RuntimeError("localized anomaly coefficient is not exact rational")
        result[name] = str(coefficient)
    return result


def load_parents():
    reports = {}
    for name, (filename, expected) in PARENTS.items():
        report = json.loads((ROOT / filename).read_text(encoding="utf-8"))
        if report.get("core_sha256") != expected or canonical_sha(report) != expected:
            raise RuntimeError("changed or noncanonical F93 singlet parent: " + name)
        reports[name] = report
    if reports["v92_master"]["input_core_hashes"]["v92_route"] != PARENTS["v92_route"][1]:
        raise RuntimeError("V92 master-to-route edge changed")
    helper = reports["v92_route"]["smooth_singlet_projectors"]
    if helper.get("core_sha256") != PROJECTOR_CORE or canonical_sha(helper) != PROJECTOR_CORE:
        raise RuntimeError("V92 embedded singlet helper changed")
    for filename in ("v92_singlet_projector_certificate.py", "test_v92_singlet_projector_certificate.py"):
        if hashlib.sha256((ROOT / filename).read_bytes().replace(b"\r\n", b"\n")).hexdigest() != reports["v92_route"]["artifact_hashes"][filename]:
            raise RuntimeError("V92 singlet source/test differs from frozen route: " + filename)
    return reports


@lru_cache(maxsize=None)
def normal_kernel_series(order, power):
    """Exact x^0..x^3 coefficients of 1/[2 sinh((x+i theta)/2)]."""
    if order not in (2, 4) or power not in range(1, order):
        raise ValueError("only nonidentity C2/C4 sectors are in this certificate")
    t = ZETA**power if order == 4 else sp.I
    denominator = [sp.simplify((t - (-1)**k/t)/(2**k*sp.factorial(k))) for k in range(4)]
    inverse = [sp.simplify(1/denominator[0])]
    for n in range(1, 4):
        inverse.append(sp.simplify(-sum(denominator[k]*inverse[n-k] for k in range(1, n+1))/denominator[0]))
    return tuple(inverse)


def phase_series(order, phase):
    """One selected symplectic half; normalization is per original torus point."""
    if phase not in range(order):
        raise ValueError("phase outside the cyclic group")
    h = ZETA * sp.I**phase if order == 4 else sp.I * (-1)**phase
    return tuple(sp.simplify(sum(h**j * normal_kernel_series(order, j)[n]
                                 for j in range(1, order))/4) for n in range(4))


def phase_polynomial(q, order, phase):
    """Degree-six formula after the conjugate SMW half has been included."""
    if not isinstance(q, int):
        raise ValueError("continuous charge must be an integer")
    series = phase_series(order, phase)
    return {name: sp.simplify(series[n]*q**r*factor/sp.factorial(r))
            for name, (n, r, factor) in TERMS.items()}


def shifted_character_polynomial(h, charge, order):
    """I6 = [Ahat(T4) (1/8) sum K_j Tr(H^j exp(Q f))]_6.

    One factor 1/2 is SMW reality and the factor 1/4 is the global orbifold
    average.  The latter is still 1/4 at either of the two C2 *cover points*.
    """
    if h.rows != h.cols or charge.shape != h.shape:
        raise ValueError("incompatible half-angle and charge matrices")
    if not zero(h*charge-charge*h):
        raise ValueError("continuous curvature must commute with stabilizer")
    moments = {j: {r: sp.simplify(sp.trace(h**j * charge**r)) for r in range(4)}
               for j in range(1, order)}
    polynomial = {
        name: sp.simplify(factor * sum(normal_kernel_series(order, j)[n]*moments[j][r]
                                        for j in range(1, order))/(8*sp.factorial(r)))
        for name, (n, r, factor) in TERMS.items()
    }
    return polynomial, moments


def spectral_multiplicities(a, order):
    root = sp.I if order == 4 else sp.Integer(-1)
    dimensions = []
    for m in range(order):
        projector = clean(sum((root**(-m*j)*a**j for j in range(order)), sp.zeros(a.rows))/order)
        if not zero(projector**2-projector) or not zero(projector.conjugate().T-projector):
            raise RuntimeError("spectral projector failed")
        dimensions.append(int(projector.rank()))
    if sum(dimensions) != a.rows:
        raise RuntimeError("spectral projectors incomplete")
    return dimensions


def block_local_certificate(block):
    q, d = block["q_magnitude"], block["hyper_count"]
    flavor = block["underlying_flavor"]
    a, u, v, k, jform = (matrix(flavor[name]) for name in ("A", "U", "V", "external_k", "symplectic_J"))
    charge = sp.diag(*block["continuous_symplectic_charge_diagonal"])
    if list(charge.diagonal()) != [q]*d+[-q]*d:
        raise RuntimeError("continuous charges no longer reconstruct the symplectic pair")
    ue, ve = clean(u*k**2), clean(v*k**2)
    half_angles = {"z00": a, "z11": ue*a, "z10": ue*a**2, "z01": ve*a**2}
    strata = {}
    for point in POINTS:
        frozen = block["strata"][point]
        order = frozen["order"]
        h = clean(half_angles[point])
        plus = matrix(frozen["plus_matrix"])
        halfroot = ZETA if order == 4 else sp.I
        expected = sp.diag(halfroot*plus, sp.conjugate(halfroot*plus))
        checks = {
            "actual_flavor_word_equals_shifted_plus_and_conjugate": zero(h-expected),
            "half_angle_order_is_minus_identity": zero(h**order+sp.eye(2*d)),
            "symplectic": zero(h.T*jform*h-jform),
            "unitary": zero(h.conjugate().T*h-sp.eye(2*d)),
            "quaternionic_reality": zero(jform*sp.conjugate(h)-h*jform),
            "charge_is_symplectic": zero(charge.T*jform+jform*charge),
            "charge_commutes": zero(charge*h-h*charge),
        }
        if not all(checks.values()):
            raise RuntimeError("shifted singlet character fails its matrix lift: " + point)
        polynomial, moments = shifted_character_polynomial(h, charge, order)
        # The V92 hyperino uses the dual flavor.  Pairing by J identifies the
        # simultaneous dual of H and Q, hence not an independent sign choice.
        dual, _ = shifted_character_polynomial(h.inv().T, -charge.T, order)
        checks["dual_flavor_and_charge_give_identical_polynomial"] = all(sp.simplify(dual[name]-polynomial[name]) == 0 for name in MONOMIALS)
        mult = spectral_multiplicities(plus, order)
        spectral = {name: sum(n*phase_polynomial(q, order, m)[name]
                              for m, n in enumerate(mult)) for name in MONOMIALS}
        checks["spectral_and_full_SMW_trace_agree"] = all(sp.simplify(spectral[name]-polynomial[name]) == 0 for name in MONOMIALS)
        if not all(checks.values()):
            raise RuntimeError("SMW trace does not match independent half-spectrum calculation")
        strata[point] = {
            "order": order, "normal_weight": frozen["normal_weight"],
            "orbifold_average": "1/4", "SMW_factor": "1/2",
            "half_angle_matrix": serialize_matrix(h),
            "full_symplectic_charge_diagonal": [int(x) for x in charge.diagonal()],
            "plus_eigenphase_multiplicities": mult,
            "shifted_character_traces_Q_powers_0_to_3": {
                str(power): [str(moments[power][r]) for r in range(4)] for power in moments},
            "coefficients": serialize_polynomial(polynomial), "checks": checks,
        }
    return {"q_magnitude": q, "kind": block["kind"], "m": block["m"],
            "hyper_count": d, "strata": strata,
            "all_six_coefficients_vanish_at_all_strata": all(
                all(value == "0" for value in row["coefficients"].values()) for row in strata.values())}


def certificate_content():
    parents = load_parents()
    helper = parents["v92_route"]["smooth_singlet_projectors"]
    witness = helper["eleven_mode_normal_aligned_witness"]
    v71_rows = parents["v71"]["spin_half_equivariant_index"]["rows"]
    for row in v71_rows:
        if [str(x) for x in phase_series(4, row["m"])] != row["series_coefficients_1_x_x2_x3"]:
            raise RuntimeError("derived normal kernel differs from pinned V71")
    total = {point: {name: sp.Integer(0) for name in MONOMIALS} for point in POINTS}
    blocks = []
    for source in witness["direct_sum_blocks"]:
        block = block_local_certificate(source["certificate"])
        blocks.append({"copies": source["copies"], "certificate": block})
        for point in POINTS:
            for name in MONOMIALS:
                total[point][name] += source["copies"]*sp.Rational(block["strata"][point]["coefficients"][name])
    charges = witness["constant_N1_signed_continuous_charges"]
    first, third = sum(charges), sum(q**3 for q in charges)
    integrated = {name: sp.simplify(sum(total[point][name] for point in POINTS))
                  for name in ("f3", "f_p1T4")}
    if integrated != {"f3": sp.Rational(third, 6), "f_p1T4": -sp.Rational(first, 24)}:
        raise RuntimeError("localized gauge polynomial fails the zero-mode index check")
    normal = {point: [str(total[point]["x3"]), str(total[point]["x_p1T4"])] for point in POINTS}
    for point in ("z00", "z11"):
        delta = witness["normal_Delta_by_corner"][point]
        if normal[point] != [str(sp.Rational(11*delta, 192)), str(sp.Rational(delta, 192))]:
            raise RuntimeError("V92 normal-channel contribution changed")
    naive = {}
    for point in POINTS:
        q1 = q3 = 0
        for source in witness["direct_sum_blocks"]:
            block = source["certificate"]
            local = block["strata"][point]
            # This intentionally computes the wrong local-spectrum substitute,
            # to demonstrate why it cannot replace the shifted character.
            net = int(matrix(local["plus_projector"]).rank()-matrix(local["minus_projector"]).rank())
            q1 += source["copies"]*block["q_magnitude"]*net
            q3 += source["copies"]*block["q_magnitude"]**3*net
        naive[point] = {"local_invariant_TrQ": q1, "local_invariant_TrQ3": q3,
                        "naive_f3": str(sp.Rational(q3, 6)), "actual_localized_f3": str(total[point]["f3"]),
                        "naive_local_spectrum_equals_localized_anomaly": sp.Rational(q3, 6) == total[point]["f3"]}
    return {
        "schema": "v93_localized_singlet_anomaly_v1",
        "input_core_hashes": {**{name: core for name, (_, core) in PARENTS.items()},
                              "v92_singlet_projector_helper": PROJECTOR_CORE},
        "scope": "bare singlet-hyper spin-half perturbative fixed-locus polynomial of the selected frozen V92 flat lift, before wall fields or inflow",
        "conventions": {
            "f": "continuous covering U1_8 Chern root; a charge q contributes exp(q f); never reduce q modulo 8",
            "x": "c1 of the complex normal line, local rotation weight +1 at every stratum",
            "p1T4": "tangent first Pontryagin class; Ahat(T4)=1-p1T4/24+...",
            "four_dimensional_left_Weyl": "I6(q)=q^3 f^3/6-q f p1T4/24",
            "sign_calibration": "the V71 normal-kernel convention and V92 N1 charge assignment; no additional six-dimensional chirality sign is applied to this calibrated hyper formula",
            "shifted_equivariant_character": "I6=[(1-p1T4/24) (1/2)(1/4) sum_(j=1..n-1) K_j(x) Tr_sympl(H^j exp(Q f))]_degree6",
            "normal_kernel": "K_j(x)=[2 sinh((x+2 pi i j/n)/2)]^-1",
            "H": "actual full flavor half-angle stabilizer, conjugate pair diag(h,hbar), H^n=-I",
            "conjugate_pair": "C4 Phi+ phase i^m has h=zeta*i^m; hbar corresponds to phase 3-m. Q=diag(q,-q). The SMW half avoids double counting.",
            "cover_point_normalization": "global C4 average 1/4 at all four original torus fixed points; a C2 cover point contains only the global g^2 sector",
            "physical_orbits": "z00 and z11 are C4 orbits; z10 and z01 are exchanged and sum to one physical C2 orbit with local average 1/2",
            "six_monomials": {"f3": "f^3", "f_p1T4": "f*p1(T4)", "x_f2": "x*f^2", "x2_f": "x^2*f", "x3": "x^3", "x_p1T4": "x*p1(T4)"},
            "forms_are_wedge_products": True,
            "mixed_anomaly_current_assignment": "the formal degree-six polynomial is reported; choice of descent/current and local counterterms is not fixed here",
        },
        "derived_kernel_series_by_phase": {
            "C4": [[str(x) for x in phase_series(4, m)] for m in range(4)],
            "C2_per_cover_point": [[str(x) for x in phase_series(2, m)] for m in range(2)],
            "coefficient_order": ["1", "x", "x^2", "x^3"],
            "C4_series_reproduces_frozen_V71": True,
        },
        "block_certificates": blocks,
        "coefficients_by_stratum": {point: serialize_polynomial(total[point]) for point in POINTS},
        "coefficients_by_physical_orbit": {
            "z00_C4": serialize_polynomial(total["z00"]),
            "z11_C4": serialize_polynomial(total["z11"]),
            "z10_z01_C2": serialize_polynomial({name: total["z10"][name]+total["z01"][name] for name in MONOMIALS}),
        },
        "normal_only_coefficients_x3_xp1T4": normal,
        "zero_mode_cross_check": {
            "signed_continuous_charges": charges, "independent_chiral_count": len(charges),
            "TrQ": first, "TrQ3": third,
            "sum_cover_point_f3": str(integrated["f3"]), "sum_cover_point_f_p1T4": str(integrated["f_p1T4"]),
            "ordinary_4D_gauge_polynomial": "144*f^3-(3/2)*f*p1(T4)",
            "zero_mode_index_matches": True,
            "restriction_for_global_comparison": "x=0, common invariant continuous U1 and tangent backgrounds, zero flux, frozen free bulk kinetic lift",
            "normal_terms_are_identified_with_ordinary_zero_mode_trace": False,
            "massive_local_ansatz_erases_anomaly": False,
        },
        "local_projector_trace_counterexample": naive,
        "scope_boundaries": {
            "charges_reduced_mod8": False,
            "field_count_267_substituted_for_zero_modes": False,
            "half_angle_twist_dropped": False,
            "four_orbit_zero_mode_absence_implies_zero_anomaly_in_general": False,
            "four_orbit_equal_charge_cancellation_is_verified_for_this_actual_witness": True,
            "full_fixed_wall_Gammahat_representations_supplied": False,
            "independent_4D_Z4R_mixed_anomalies_included": False,
            "global_gauged_QK_target_away_from_origin_included": False,
            "GS_or_WCS_inflow_included": False,
            "torsion_Dai_Freed_KK_eta_or_relative_anomaly_computed": False,
            "smooth_character_calculation_is_full_quantum_completion": False,
        },
        "missing_data": [
            "localized fields' actual full stabilizer and tangential representations, including normal and continuous U1 charges",
            "gravity, tensor, other charged bulk sectors and their common action/regulator",
            "globally glued GS/WCS descent and any allowed localized counterterms",
            "nonzero-VEV background and Wess-Zumino/GS matching when the nine singlets are integrated out",
            "full relative orbifold anomaly character and all G1-G8 same-action obligations",
        ],
        "primary_sources": [
            {"url": "https://arxiv.org/abs/hep-th/0612212",
             "use": "Sections 3.1-3.2 require shifted stabilizer characters, include the normal Lorentz anomaly, and distinguish them from local invariant spectra; section 4 identifies two C4 and one C2 physical singularity. The detailed normal series here is derived from and checked against frozen V71, not claimed to be a new theorem in that paper."},
            {"url": "https://arxiv.org/abs/hep-th/0602155",
             "use": "Equations 43-46 fix the orbifold delta/projector and full-hyper N1 partner relation Zplus Zminus exp(i phi)=1 used by V70 and V92."},
        ],
        "terminal_decision": {"singlet_shifted_character_polynomial_computed": True,
                              "integrated_gauge_zero_mode_check_passes": True,
                              "singlet_sector_alone_anomaly_free": False,
                              "full_theory_ruled_out_by_singlet_sector_alone": False,
                              "full_fixed_wall_anomaly_cancelled": False,
                              "full_relative_or_global_anomaly_trivialized": False,
                              "accepted_extensions": 0, "closed_gates": []},
    }


def build_certificate():
    report = certificate_content()
    report["core_sha256"] = canonical_sha(report)
    return report


def validate_certificate(report):
    if report.get("core_sha256") != canonical_sha(report) or report != build_certificate():
        raise RuntimeError("localized singlet certificate changed")


if __name__ == "__main__":
    print(json.dumps(build_certificate(), indent=2, sort_keys=True))
