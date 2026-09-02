"""F95: finite anomaly witnesses for the isolated V94 unit Phi defect.

The answer is a bare, gravitationally subtracted defect anomaly and a necessary
inverse-inflow target.  It is not the anomaly of the complete theory.  In
particular a half-Pfaffian is evaluated before reduction modulo integers.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as F
from pathlib import Path
from typing import Mapping

import sympy as sp

import v94_phi_defect_anomaly_matching as parent


ROOT = Path(__file__).resolve().parent
SCHEMA = "v95_defect_finite_eta_and_inverse_inflow_targets_v1"
V94_ROUTE_PATH = ROOT / "SUSY_V94_BOUNDARY_DEFECTS_AND_MW_DESCENT_AUDIT.json"
V94_MASTER_PATH = ROOT / "SUSY_V94_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V94_ROUTE_CORE = "17fd3a60008545b7bde77756ed8b5ec7dd590c18c1cbb1344a5a7cc67dd2686f"
V94_MASTER_CORE = "8332984113477ebbbc8a1bc44915475cc3c38003c8c3a7ac9c9a5e35fc11da06"
V94_DEFECT_CORE = "ec80205bd8119a0b5be8675147417769ffcb48e8e067699fbdd2a5066e16164e"
canonical_sha = parent.canonical_sha


def portable_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_inputs() -> tuple[dict, dict, dict]:
    reports = []
    for path, core in ((V94_ROUTE_PATH, V94_ROUTE_CORE), (V94_MASTER_PATH, V94_MASTER_CORE)):
        report = json.loads(path.read_text(encoding="utf-8"))
        if report.get("core_sha256") != core or canonical_sha(report) != core:
            raise RuntimeError("F95 requires immutable canonical V94 route and master")
        reports.append(report)
    route, master = reports
    if master["input_core_hashes"]["v94_route"] != V94_ROUTE_CORE:
        raise RuntimeError("V94 route/master lineage mismatch")
    defect = route["Phi_zero_locus_and_defect_matching"]
    if defect.get("core_sha256") != V94_DEFECT_CORE or canonical_sha(defect) != V94_DEFECT_CORE:
        raise RuntimeError("bound V94 defect core changed")
    for name in ("v94_phi_defect_anomaly_matching.py", "test_v94_phi_defect_anomaly_matching.py"):
        if portable_sha(ROOT / name) != route["artifact_hashes"][name]:
            raise RuntimeError("bound V94 source/test changed: " + name)
    if defect != parent.build_certificate():
        raise RuntimeError("V94 defect fails fresh reconstruction")
    return route, master, defect


def _check_lens(n: int, charge: int, spin_shift: int) -> None:
    if type(n) is not int or n not in (2, 4, 8):
        raise ValueError("bounded lens arithmetic supports n=2,4,8")
    if type(charge) is not int or type(spin_shift) is not int or spin_shift not in (0, n//2):
        raise ValueError("integer charge and one of the two spin lifts required")


def lens_xi(n: int, charge: int, spin_shift: int = 0) -> F:
    """Exact spectral value, not a residue class; sign specified in certificate.

    This is minus DT Eq(C.2).  Positive scalar curvature and a flat twist give
    h=0.  Tests independently evaluate its finite trigonometric sum.
    """
    _check_lens(n, charge, spin_shift)
    q = (charge + spin_shift) % n
    return -F(n*n - 1 - 6*n*q + 6*q*q, 12*n)


def lens_xi_from_sum(n: int, charge: int, spin_shift: int = 0) -> F:
    _check_lens(n, charge, spin_shift)
    q = (charge + spin_shift) % n
    value = sp.simplify(-sum(sp.cos(2*sp.pi*j*q/n)/sp.sin(sp.pi*j/n)**2
                             for j in range(1, n))/(4*n))
    if not value.is_Rational:
        raise RuntimeError("lens finite sum did not simplify exactly")
    return F(int(value.p), int(value.q))


def lens_rho(n: int, charge: int, spin_shift: int = 0) -> F:
    return lens_xi(n, charge, spin_shift) - lens_xi(n, 0, spin_shift)


def phase_label(exponent: F) -> str:
    residue = exponent % 1
    return {F(0): "+1", F(1, 4): "+i", F(1, 2): "-1", F(3, 4): "-i"}.get(
        residue, "exp(2*pi*i*" + str(residue) + ")")


def anomaly_row(rho_complex: F, rho_real: F, complex_count: int = 3, real_count: int = 3) -> dict:
    if any(type(k) is not int or k < 0 for k in (complex_count, real_count)):
        raise ValueError("nonnegative integer channel counts required")
    rho_complex, rho_real = F(rho_complex), F(rho_real)
    # Essential: rho_real is the FULL spectral difference, not rho_real % 1.
    weighted = complex_count*rho_complex + F(real_count, 2)*rho_real
    exponent = -weighted
    return {
        "complex_rho_exact": str(rho_complex), "real_complexified_rho_exact": str(rho_real),
        "complex_channel_count": complex_count, "real_channel_count": real_count,
        "weighted_xi_exact": str(weighted),
        "bare_log_phase_over_2pi_i_exact": str(exponent),
        "bare_log_phase_over_2pi_i_mod1": str(exponent % 1),
        "bare_phase": phase_label(exponent),
        "required_inverse_inflow_exponent_mod1": str((-exponent) % 1),
        "required_inverse_inflow_phase": phase_label(-exponent),
        "opposite_orientation_or_chirality_bare_phase": phase_label(-exponent),
    }


def torus_spectrum(charge: int, holonomy: int = 1, circle_spin: int = 0) -> dict:
    """Flat T3: both transverse circles periodic; spin0/1 means R/NS on S1.

    Each Fourier momentum has eigenvalues +- |p| of a two-component Dirac
    operator.  Thus eta_spectral=0; h=2 exactly when every momentum can vanish.
    """
    if (type(charge) is not int or type(holonomy) is not int or
            type(circle_spin) is not int or circle_spin not in (0, 1)):
        raise ValueError("integer C8 charge/holonomy and R or NS circle required")
    shift = (F(charge*holonomy, 8) + F(circle_spin, 2)) % 1
    h = 2 if shift == 0 else 0
    return {"circle_momentum_shift_mod1": str(shift), "spectral_eta": "0",
            "complex_kernel_dimension": h, "xi_exact": str(F(h, 2))}


def restricted_lift(defect: Mapping) -> dict:
    old = defect["finite_lift_bookkeeping"]
    if (old["complex_mode_component_exponents_mod8"] != [2, 2] or
            old["real_mode_component_exponents_mod8"] != [4, 4] or
            old["complex_mode_multiplicity"] != 3 or old["real_mode_multiplicity"] != 3):
        raise RuntimeError("inherited physical defect characters changed")
    powers = defect["topological_patch_constraints"]["field_line_powers_of_D"]
    if powers != {"S2": 1, "S4": 2, "S6": 3, "Phi_minus": -4}:
        raise RuntimeError("frozen determinant line powers changed")
    table = []
    for h in range(8):
        d, root, tangent = 2*h % 8, -4*h % 8, 4*h % 8
        table.append({"power_of_k": h, "D": d, "N_D_minus4": -4*d % 8,
                      "normal_spin_root": root, "tangent_spin_compensator": tangent,
                      "complex_coefficient": -d % 8, "real_coefficient": 0,
                      "physical_complex": (-d+tangent) % 8, "physical_real": tangent})
    return {
        "category": "ordinary Spin3 x internal C8 pullback of the isolated four-dimensional unit-defect model",
        "spin_background_s": "physical product spin structure used in the eta operators",
        "a": "C8 flat bundle; a2 is its mod2 sign character",
        "normal_data": "D=rho2, N=D^-4=1 with its canonical C8 trivialization; Nspin=D^-2=rho4",
        "induced_tangent_spin_structure": "s+a2, so S(s+a2)=S(s) tensor rho4",
        "physical_complex_bundle": "S(s+a2) tensor D^-1 = S(s) tensor rho2",
        "physical_real_bundle": "S(s+a2) = S(s) tensor rho4",
        "central_gauge_map": "k maps to [(1,exp(pi*i/4))] in (Spin11 x U1)/<(z,-1)>; D has character2",
        "local_tubular_admissibility": "For a spin3 test Y and flat C8 bundle, take Y x disk2, a trivial geometric normal, D=rho2 and Phi=z. Changing the normal spin lift to D^-2 changes the induced tangent spin lift by the same sign and leaves the ambient product spin structure fixed.",
        "normal_spin_and_tangent_spin_signs_cancel_in_ambient_spin": True,
        "character_table_mod8": table,
        "all_physical_characters_k4_trivial": True,
        "k_squared_is_total_fermion_parity": False,
        "effective_C4_sector_exists": True,
        "backgrounds_need_not_exhaust_effective_C4_bundles": True,
        "full_Gammahat_map_or_fixed_wall_extension_constructed": False,
        "embedding_in_one_compact_microscopic_action_constructed": False,
        "normal_is_six_dimensional_orbifold_normal": False,
    }


def lens_tests() -> dict:
    rows = []
    for spin in (0, 4):
        xis = [lens_xi(8, q, spin) for q in range(8)]
        if xis != [lens_xi_from_sum(8, q, spin) for q in range(8)]:
            raise RuntimeError("closed formula differs from exact lens spectral sum")
        for h in range(8):
            row = {"holonomy_power": h, "spin_shift": spin,
                   "spin_lift": "exp(pi*e12/8) exp(pi*e34/8)" + ("" if spin == 0 else " times central -1"),
                   "xi_neutral": str(xis[0]), "xi_complex": str(xis[2*h % 8]),
                   "xi_real_complexification": str(xis[4*h % 8])}
            row.update(anomaly_row(xis[2*h % 8]-xis[0], xis[4*h % 8]-xis[0]))
            rows.append(row)
    return {
        "manifold": "round L3_8(1,1)=S3/<(z1,z2)->(exp(2pi*i/8)z1,exp(2pi*i/8)z2)>",
        "Dirac_sign_and_orientation_definition": "xi(q)=-1/(4*8) sum_{j=1}^7 cos(2*pi*j*q/8)/sin(pi*j/8)^2; this is explicitly minus the DT2504.02934(C.2) sign on this zero-mode-free lens",
        "source_sign_not_silently_identified_with_V94_bulk_inflow": True,
        "xi_includes_kernel": "xi=(eta_spectral+h)/2; h=0 here by positive scalar curvature and flat unitary twisting",
        "exact_polynomial": "-(n^2-1-6*n*r+6*r^2)/(12*n), r=(q+spin_shift) mod n",
        "finite_sum_verified_before_any_modulo_reduction": True,
        "all_holonomies_and_both_spin_lifts": rows,
        "primitive_holonomy_bare_phase_in_chosen_convention": "+i",
        "primitive_inverse_inflow_in_chosen_convention": "-i",
        "both_spin_lifts_give_same_primitive_phase": True,
        "orientation_independent_result": "a nontrivial fourth root, +i or -i according to the common orientation/chirality convention",
        "full_relative_action_orientation_dictionary_fixed": False,
    }


def torus_tests() -> dict:
    rows = []
    for spin in (0, 1):
        for h in range(8):
            values = {str(q): torus_spectrum(q, h, spin) for q in (0, 2, 4)}
            xi0, xi2, xi4 = (F(values[str(q)]["xi_exact"]) for q in (0, 2, 4))
            row = {"holonomy_power": h, "circle_spin": "R" if spin == 0 else "NS",
                   "spectra": values}
            row.update(anomaly_row(xi2-xi0, xi4-xi0))
            rows.append(row)
    return {
        "manifold": "flat T3=S1 x T2, with both T2 circles periodic (odd spin T2)",
        "gauge_holonomy": "k^h on S1, identity on the two T2 circles",
        "eigenvalue_derivation": "D(p)=sigma dot p has opposite nonzero eigenvalues; h=2 when all three shifts vanish and h=0 otherwise",
        "spectral_eta_alone_would_miss_kernel_term": True,
        "all_holonomies_and_circle_spins": rows,
        "primitive_holonomy_bare_phase": "-1",
        "primitive_required_inverse_inflow_phase": "-1",
        "both_circle_spins_give_same_primitive_phase": True,
        "complex_determinant_sector_phase_on_this_test": "+1",
        "three_real_Pfaffians_phase_on_this_test": "-1",
        "odd_Majorana_sign_is_not_determined_by_the_complex_determinant_phase": True,
    }


def spin_split_identity() -> dict:
    rows = []
    for spin in (0, 4):
        x0, x2, x4, x6 = (lens_xi(8, q, spin) for q in (0, 2, 4, 6))
        physical = 3*(x2-x0) + F(3, 2)*(x4-x0)
        induced_gauge = 3*(x2-x4)
        spin_change = F(9, 2)*(x4-x0)
        if induced_gauge+spin_change != physical:
            raise RuntimeError("equivariant tangent-spin decomposition failed")
        rows.append({"spin_shift": spin, "physical_weighted_xi": str(physical),
                     "induced_spin_D_minus1_gauge_piece": str(induced_gauge),
                     "nine_real_rank_spin_change_piece": str(spin_change),
                     "exact_difference": "0",
                     "incorrect_no_compensator_bare_phase": phase_label(-3*(x6-x0)),
                     "correct_bare_phase": phase_label(-physical)})
    return {
        "identity": "3*(xi_(s+a2,D^-1)-xi_(s+a2)) + (9/2)*(xi_(s+a2)-xi_s) = 3*(xi_(s,rho2)-xi_s)+(3/2)*(xi_(s,rho4)-xi_s)",
        "meaning": "The coefficient Majorana is neutral only relative to the induced spin s+a2. Its physical sign reappears in the rank-nine gravitational spin-change factor.",
        "lens_exact_checks": rows,
        "primitive_T3_induced_gauge_piece": "0",
        "primitive_T3_spin_change_piece_for_R_circle": "-9/2",
        "wrong_neutral_Majorana_T3_phase": "+1",
        "correct_T3_phase": "-1",
        "curvature_polynomial_alone_fixes_this_spin_refinement": False,
    }


def primary_sources() -> list[dict]:
    return [
        {"url": "https://arxiv.org/abs/2504.02934", "use": "AppendixC(C.2) finite spectral sum, (C.3)-(C.4) lens polynomials, and (3.13) change of spin lift. Our lens Dirac sign is explicitly the opposite of (C.2); exact sums, not mod-one polynomials, fix the real half."},
        {"url": "https://arxiv.org/abs/2606.18380", "use": "Section3.1 (3.4) includes the kernel in APS xi, (3.9) subtracts a same-rank trivial bundle, and (3.12)-(3.15) distinguish determinant/Pfaffian phases and the real-twisted even quaternionic index. The explicit negative-exponential phase convention is used here."},
        {"url": "https://arxiv.org/abs/1909.08775", "use": "Section2.4 and Eq(2.52) derive the fermion Pfaffian anomaly factor, including the real versus complex normalization; not an automatic global completion of the present bulk theory."},
        {"url": "https://arxiv.org/abs/2604.19634", "use": "Section2 (2.18)-(2.20) identifies useful lens and odd-T2 product tests for cyclic two-dimensional anomalies. Its complex mod-one product result must not be halved after discarding the kernel integer."},
    ]


def build_certificate() -> dict:
    _, _, defect = load_inputs()
    result = {
        "schema": SCHEMA,
        "status": "NONTRIVIAL_RESTRICTED_UNIT_DEFECT_FINITE_ANOMALY__INVERSE_INFLOW_TARGETS_FIXED__GLOBAL_GLUE_OPEN",
        "input_core_hashes": {"v94_route": V94_ROUTE_CORE, "v94_master": V94_MASTER_CORE,
                              "v94_defect": V94_DEFECT_CORE},
        "inherited_spectrum": {"complex_chiral_q2": 3, "real_chiral_q4": 3,
                               "net_real_chiral_index": 9, "net_central_charge": "9/2",
                               "source": "V94 isolated full-rank nine-field unit-vortex operator",
                               "extra_KK_gaugino_gravitino_or_wall_modes_added": False},
        "restricted_spin_and_gauge_lift": restricted_lift(defect),
        "normalization": {
            "xi": "(eta_spectral + complex_kernel_dimension)/2",
            "rho": "xi_twisted - xi_neutral on the SAME spin background",
            "chosen_bare_phase": "exp(-2*pi*i*(3*rho_q2 + (3/2)*rho_q4))",
            "real_half_taken_before_modulo_one": True,
            "real_half_is_not_an_arbitrary_square_root": "For a real flat bundle the spin4 Dirac index is even by its quaternionic structure; the eta/Pfaffian prescription retains the corresponding mod-two information.",
            "subtraction": "three trivial complex plus three trivial real characters; a formal reference, not new physical fermions",
            "pure_gravitational_anomaly_physically_cancelled_by_subtraction": False,
            "single_RP3_sign_Majorana_calibration": anomaly_row(F(0), lens_rho(2, 1), 0, 1),
        },
        "lens_C8_witnesses": lens_tests(),
        "torus_C8_Pfaffian_witnesses": torus_tests(),
        "spin_split_global_identity": spin_split_identity(),
        "inflow_obligation": {
            "bare_defect_is_anomaly_free_on_the_two_test_families": False,
            "primitive_lens_required_phase_chosen_convention": "-i",
            "primitive_torus_required_phase": "-1",
            "correct_conjugation_rule": "Reverse the common chirality/orientation convention on BOTH determinant and inflow; the lens phases conjugate and the torus sign remains -1.",
            "V94_local_curvature_matching_retracted": False,
            "V94_4D_C8_screen_implies_defect_anomaly_free": False,
            "new_global_obligation": "A genuine relative bulk/defect gluing must supply the inverse determinant/Pfaffian character on these admissible isolated-model pullbacks, including the spin-change sign. The inverse is a necessary target, not a constructed action.",
        },
        "limitations": {
            "complete_Gammahat_tangential_bordism_group_computed": False,
            "full_physical_relative_Dai_Freed_trivialization_constructed": False,
            "regulated_bump_form_or_bulk_determinant_constructed": False,
            "differential_normal_curvature_inflow_with_torsion_glued": False,
            "full_spin_C8_anomaly_cancellation_proved": False,
            "full_symmetry_broken_vacuum_C8_restoration_asserted": False,
            "bare_defect_anomaly_rejects_the_total_theory": False,
            "same_action_parent_or_any_gate_closed": False,
        },
        "primary_sources": primary_sources(),
    }
    result["core_sha256"] = canonical_sha(result)
    return result


def validate_certificate(report: Mapping) -> None:
    if report.get("core_sha256") != canonical_sha(report) or dict(report) != build_certificate():
        raise RuntimeError("F95 finite-defect certificate differs from fresh bound derivation")


if __name__ == "__main__":
    print(json.dumps(build_certificate(), indent=2, sort_keys=True))
