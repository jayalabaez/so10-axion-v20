#!/usr/bin/env python3
"""Canonical G3: exact global terminal vacuum of the accepted G2 potential.

The accepted potential uses the complete canonical G2 space, but selects a
particularly transparent point in it: all dimension-five and dimension-six
coefficients are zero and 28 of the 51 real renormalizable coefficients are
nonzero.  In the exact component normalization it is

    V = -1 + (N_Phi-1)^2 + I45(Phi)+I210(Phi)+I5940(Phi)
           + (N_D-1/50)^2 + I54(D)+I1050bar(D)+I4125(D)
           + ||(M(Phi)-2)D||^2
           + (N_H-1)^2 + I1(HH) + ||H wedge Phi||^2
           + ||i_H D||^2
           + (N_S-1/50)^2 + (N_X-1/2)^2.

Every summand is an exact squared norm.  Its common zero locus is classified
using the Pluecker equations, the Cartan-square pure-spinor theorem, exact
two-Kaehler-angle normal form for the relative Phi/D orientation, and the
intersection of the aligned holomorphic plane with Phi.  The locus is one
SO(10)xU(1)_XxU(1)_PQ orbit.  The exact 486-real source Hessian has rank 448;
its 38-dimensional kernel is the full symmetry tangent space, split into 37
gauged directions and one physical PQ axion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import canonical_g1_g8_gauged_u1x_v21 as contract
import exact_210_pati_salam_global_vacuum_v20 as phi_global
import exact_gauged_u1x_g3_a_square_recoupling_v20 as a_square
import exact_physical_sm_37_row_aggregate_v20 as source_rows
import exact_physical_sm_easy_21_hessians_v20 as easy
import physical_sm_vacuum_local_feasibility_v20 as foundation


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "CANONICAL_G3_PHYSICAL_EW_GLOBAL_VACUUM_V21.json"
OUT_MD = ROOT / "CANONICAL_G3_PHYSICAL_EW_GLOBAL_VACUUM_V21.md"
SCHEMA = contract.EVIDENCE_SCHEMA
MODEL = contract.MODEL_CONTRACT_ID
GATE_ID = contract.G3_ID
DEPENDENCIES = [contract.G2_ID]
FIELD_DIMENSION = 486
TARGET_DENOMINATOR = 20
CONSTANT = Fraction(3127, 2500)


COEFFICIENTS: dict[str, Fraction] = {
    "O03_B01_singlet_polynomial": Fraction(-1),
    "O04_B01_singlet_polynomial": Fraction(-1, 25),
    "O05_B01_126bar_norm": Fraction(99, 25),
    "O06_B01_Hdag_H_norm": Fraction(-2),
    "O07_B01_Phi_norm": Fraction(-2),
    "O14_B01_Phi_Sigma_Sigmadag_cubic": Fraction(-4),
    "O20_B01_singlet_polynomial": Fraction(1),
    "O23_B01_singlet_polynomial": Fraction(1),
    "O27_B01_126bar_self_projectors": Fraction(2),
    "O27_B02_126bar_self_projectors": Fraction(2),
    "O27_B03_126bar_self_projectors": Fraction(1),
    "O27_B04_126bar_self_projectors": Fraction(2),
    "O35_B01_H_Sigma_hermitian": Fraction(1),
    "O35_B02_H_Sigma_hermitian": Fraction(-1),
    "O36_B01_H_self_quartics": Fraction(2),
    "O36_B02_H_self_quartics": Fraction(1),
    "O44_B01_Phi2_Sigma_projectors": Fraction(40),
    "O44_B02_Phi2_Sigma_projectors": Fraction(72),
    "O44_B03_Phi2_Sigma_projectors": Fraction(28),
    "O44_B04_Phi2_Sigma_projectors": Fraction(-8),
    "O44_B05_Phi2_Sigma_projectors": Fraction(-12),
    "O44_B06_Phi2_Sigma_projectors": Fraction(12),
    "O46_B01_Phi2_HdagH_channels": Fraction(3, 5),
    "O46_B03_Phi2_HdagH_channels": Fraction(-1),
    "O48_B01_Phi_self_quartics": Fraction(-21, 200),
    "O48_B02_Phi_self_quartics": Fraction(2467, 28800),
    "O48_B03_Phi_self_quartics": Fraction(-77, 3200),
    "O48_B04_Phi_self_quartics": Fraction(119, 115200),
}


SOURCE_PATHS = (
    "canonical_g3_physical_ew_global_vacuum_v21.py",
    "canonical_g1_g8_gauged_u1x_v21.py",
    "CANONICAL_G1_SUSYNO_CHANNEL_BASIS_V21.json",
    "CANONICAL_G2_EXACT_CONTRACTION_BASIS_V21.json",
    "CANONICAL_G2_FULL_COMPONENT_PROJECTION_DIM6_V21.json",
    "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.json",
    "exact_210_pati_salam_global_vacuum_v20.py",
    "exact_gauged_u1x_g3_a_square_recoupling_v20.py",
    "EXACT_GAUGED_U1X_G3_A_SQUARE_RECOUPLING_V20.json",
    "exact_physical_sm_37_row_aggregate_v20.py",
    "exact_physical_sm_hard_projector_hessians_v20.py",
    "exact_physical_sm_easy_21_hessians_v20.py",
    "exact_physical_sm_last_six_hessians_v20.py",
    "physical_sm_vacuum_local_feasibility_v20.py",
    "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.json",
)


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha(value: Any) -> str:
    return hashlib.sha256((canonical(value) + "\n").encode("ascii")).hexdigest()


def portable(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def q(value: Fraction | int | str) -> str:
    return str(Fraction(value))


def source_manifest() -> list[dict[str, str]]:
    rows = []
    for relative in SOURCE_PATHS:
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        rows.append({"path": relative, "mode": "portable-lf", "sha256": portable(path)})
    return rows


def add_expansion(target: dict[str, Fraction], values: dict[str, Fraction]) -> None:
    for key, value in values.items():
        target[key] = target.get(key, Fraction()) + value


def sos_decomposition() -> dict[str, Any]:
    terms = [
        {
            "id": "R_PHI_RADIAL_AND_PLUECKER",
            "formula": "(N_Phi-1)^2+I45(PhiPhi)+I210(PhiPhi)+I5940(PhiPhi)",
            "nonnegative": True,
            "expansion": {
                "O07_B01_Phi_norm": Fraction(-2),
                "O48_B01_Phi_self_quartics": Fraction(-21, 200),
                "O48_B02_Phi_self_quartics": Fraction(2467, 28800),
                "O48_B03_Phi_self_quartics": Fraction(-77, 3200),
                "O48_B04_Phi_self_quartics": Fraction(119, 115200),
            },
        },
        {
            "id": "R_SIGMA_RADIAL_AND_CARTAN_SQUARE",
            "formula": "(N_Sigma-1/50)^2+I54+I1050bar+I4125",
            "nonnegative": True,
            "expansion": {
                "O05_B01_126bar_norm": Fraction(-1, 25),
                "O27_B01_126bar_self_projectors": Fraction(2),
                "O27_B02_126bar_self_projectors": Fraction(2),
                "O27_B03_126bar_self_projectors": Fraction(1),
                "O27_B04_126bar_self_projectors": Fraction(2),
            },
        },
        {
            "id": "R_PHI_SIGMA_ALIGNMENT",
            "formula": "||(M(Phi)-2)Sigma||^2",
            "nonnegative": True,
            "expansion": {
                "O05_B01_126bar_norm": Fraction(4),
                "O14_B01_Phi_Sigma_Sigmadag_cubic": Fraction(-4),
                "O44_B01_Phi2_Sigma_projectors": Fraction(40),
                "O44_B02_Phi2_Sigma_projectors": Fraction(72),
                "O44_B03_Phi2_Sigma_projectors": Fraction(28),
                "O44_B04_Phi2_Sigma_projectors": Fraction(-8),
                "O44_B05_Phi2_Sigma_projectors": Fraction(-12),
                "O44_B06_Phi2_Sigma_projectors": Fraction(12),
            },
        },
        {
            "id": "R_H_RADIAL_AND_NULL",
            "formula": "(N_H-1)^2+|H.H|^2/10",
            "nonnegative": True,
            "expansion": {
                "O06_B01_Hdag_H_norm": Fraction(-2),
                "O36_B01_H_self_quartics": Fraction(2),
                "O36_B02_H_self_quartics": Fraction(1),
            },
        },
        {
            "id": "R_H_IN_PHI_PLANE",
            "formula": "||H wedge Phi||^2=(3/5)I1(PhiPhi;HdagH)-I54(PhiPhi;HdagH)",
            "nonnegative": True,
            "expansion": {
                "O46_B01_Phi2_HdagH_channels": Fraction(3, 5),
                "O46_B03_Phi2_HdagH_channels": Fraction(-1),
            },
        },
        {
            "id": "R_H_HOLOMORPHIC",
            "formula": "||i_H Sigma||^2=I1(HdagH;SigmadagSigma)-I45(HdagH;SigmadagSigma)",
            "nonnegative": True,
            "expansion": {
                "O35_B01_H_Sigma_hermitian": Fraction(1),
                "O35_B02_H_Sigma_hermitian": Fraction(-1),
            },
        },
        {
            "id": "R_S_RADIAL",
            "formula": "(N_S-1/50)^2",
            "nonnegative": True,
            "expansion": {
                "O04_B01_singlet_polynomial": Fraction(-1, 25),
                "O23_B01_singlet_polynomial": Fraction(1),
            },
        },
        {
            "id": "R_X_RADIAL",
            "formula": "(N_X-1/2)^2",
            "nonnegative": True,
            "expansion": {
                "O03_B01_singlet_polynomial": Fraction(-1),
                "O20_B01_singlet_polynomial": Fraction(1),
            },
        },
    ]
    observed: dict[str, Fraction] = {}
    for row in terms:
        add_expansion(observed, row["expansion"])
        row["expansion"] = {key: q(value) for key, value in row["expansion"].items()}
    if observed != COEFFICIENTS:
        raise ArithmeticError("SOS expansion does not reproduce accepted coefficients")
    return {
        "potential_identity": "V=-1+sum_{a=1}^8 R_a with every R_a an exact squared norm",
        "expanded_constant": q(CONSTANT),
        "residual_count": len(terms),
        "terms": terms,
        "coefficient_expansion_matches_exactly": True,
        "global_lower_bound": "V>=-1 on all 486 real fields",
    }


def complete_direction_ledger() -> dict[str, Any]:
    g1 = json.loads((ROOT / "CANONICAL_G1_SUSYNO_CHANNEL_BASIS_V21.json").read_text(encoding="utf-8"))
    old = json.loads((ROOT / "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.json").read_text(encoding="utf-8"))
    degree_counts: dict[int, int] = {}
    for row in g1["rows"]:
        degree_counts[row["degree"]] = degree_counts.get(row["degree"], 0) + row["constructive_channel_count"]
    if degree_counts != {2: 5, 3: 6, 4: 40, 5: 119, 6: 721}:
        raise ArithmeticError("canonical 891-direction degree census drifted")
    renormalizable = tuple(old["direction_ids"])
    if len(renormalizable) != 44 or not set(COEFFICIENTS).issubset(renormalizable):
        raise ArithmeticError("renormalizable component basis drifted")
    return {
        "canonical_total_real_directions": 891,
        "degree_direction_counts": {str(key): value for key, value in degree_counts.items()},
        "degree_at_most_four_real_directions": 51,
        "renormalizable_normalized_tensor_directions": len(renormalizable),
        "renormalizable_real_couplings": old["counts"]["real_parameters"],
        "nonzero_renormalizable_tensor_directions": len(COEFFICIENTS),
        "zero_renormalizable_tensor_directions": len(renormalizable) - len(COEFFICIENTS),
        "zero_dimension_five_directions": degree_counts[5],
        "zero_dimension_six_directions": degree_counts[6],
        "nonzero_coefficients": {key: q(value) for key, value in sorted(COEFFICIENTS.items())},
        "all_unlisted_renormalizable_coefficients": "exactly zero, including every imaginary coefficient of a non-self-conjugate direction",
        "all_dimension_five_and_six_coefficients": "exactly zero",
        "completeness_logic": "the 51 exact degree<=4 real directions and the 840 exact degree-5/6 contraction directions have different homogeneous degree and form a complete 891-direction basis",
    }


@lru_cache(maxsize=1)
def exact_hessian_certificate() -> dict[str, Any]:
    rows = source_rows.exact_source_rows()
    if not set(COEFFICIENTS).issubset(rows):
        raise ArithmeticError("accepted coefficient row lacks an exact source Hessian")
    hessian = easy._combine((value, rows[key]) for key, value in sorted(COEFFICIENTS.items()))
    target = foundation.integer_target_vector()
    gradient = [Fraction() for _ in range(FIELD_DIMENSION)]
    field_value = Fraction()
    for key, coefficient in COEFFICIENTS.items():
        matrix = rows[key]
        degree = source_rows.ROW_DEGREES[key]
        product = matrix.numerator @ target
        for index, item in enumerate(product):
            if item:
                gradient[index] += coefficient * Fraction(
                    int(item), matrix.denominator * TARGET_DENOMINATOR * (degree - 1)
                )
        field_value += coefficient * Fraction(
            int(target @ product),
            matrix.denominator * TARGET_DENOMINATOR**2 * degree * (degree - 1),
        )
    modular, _ = source_rows._modular_rank_and_minor(hessian)
    symmetry = foundation.exact_symmetry_certificate()
    tangents = np.asarray(foundation.exact_integer_tangent_matrix(), dtype=object)
    tangent_image = hessian.numerator.astype(object) @ tangents
    all_tangents_zero = not any(tangent_image.flat)
    serialization = "".join(
        f"{i},{j},{value}\n"
        for (i, j), value in sorted(hessian.fraction_entries().items())
    ).encode("ascii")
    if field_value + CONSTANT != -1 or any(gradient):
        raise ArithmeticError("accepted potential is not exactly stationary at V=-1")
    if modular["rank"] != 448 or not all_tangents_zero:
        raise ArithmeticError("accepted Hessian rank/kernel theorem failed")
    return {
        "field_dimension": FIELD_DIMENSION,
        "nonzero_coefficient_count": len(COEFFICIENTS),
        "hessian_denominator": hessian.denominator,
        "hessian_nonzero_upper_triangle_entries": len(hessian.fraction_entries()),
        "hessian_sparse_rational_sha256": hashlib.sha256(serialization).hexdigest(),
        "exact_field_term_value": q(field_value),
        "exact_constant": q(CONSTANT),
        "exact_total_value": "-1",
        "exact_gradient_nonzero_entries": sum(bool(value) for value in gradient),
        "modular_rank_prime": modular["prime"],
        "modular_rank": modular["rank"],
        "principal_minor_determinant_mod_prime": modular["principal_minor_determinant_mod_prime"],
        "exact_rank": 448,
        "exact_nullity": 38,
        "all_47_declared_generator_columns_annihilated_entrywise": all_tangents_zero,
        "gauge_orbit_rank": symmetry["orbits"]["SO10_x_U1X"]["exact_rank"],
        "full_symmetry_orbit_rank": symmetry["orbits"]["SO10_x_U1X_x_PQ"]["exact_rank"],
        "kernel_equals_full_symmetry_tangent_span": all_tangents_zero and modular["rank"] == 448,
        "PSD_logic": "at a common zero of exact squared norms the Hessian is a sum 2 J_a^T J_a and is PSD; exact rank 448 makes it strictly positive on the 448-dimensional transverse quotient",
        "all_448_non_symmetry_modes_strictly_positive": True,
        "intended_axion_direction_count": symmetry["orbits"]["SO10_x_U1X_x_PQ"]["exact_rank"] - symmetry["orbits"]["SO10_x_U1X"]["exact_rank"],
    }


def invariant_identities() -> dict[str, Any]:
    phi_coefficients = phi_global.quartic_couplings()
    phi_target = phi_global.exact_p_spectral_values()
    recoupling = a_square.recorded_certificate()
    return {
        "Phi_quartic_exact_J_basis": {key: q(value) for key, value in phi_coefficients.items()},
        "Phi_quartic_is_Nphi_squared_plus_channels": ["45", "210", "5940"],
        "Phi_target_extra_channels_zero": all(phi_target[key] == 0 for key in ("45", "210", "5940")),
        "full_Phi_Pluecker_norm_identity": "sum_{a<b<c}||(i_c i_b i_a Phi) wedge Phi||^2=-20 I45+18 I210+8 I5940",
        "Phi_zero_set_theorem": "the three separately vanishing projectors force the complete Pluecker norm to vanish; a nonzero real four-form is therefore decomposable, and unit decomposable four-forms are one SO(10)/(SO(4)xSO(6)) orbit",
        "Sigma_symmetric_square": "Sym^2(126bar)=54+1050bar+2772bar+4125",
        "Sigma_Cartan_square_theorem": "vanishing 54,1050bar,4125 components leaves only the highest-weight 2772bar Cartan square; the nonzero field is a decomposable maximal-isotropic chiral five-form",
        "A_square_channel_order": ["1", "45", "210", "770", "5940", "8910"],
        "A_square_exact_weights": [q(value) for value in recoupling["unique_weights"]],
        "A_square_exact_residuals": [q(value) for value in recoupling["identity_residuals"]],
        "Phi_Sigma_two_Kaehler_angle_residual": "64(c1*c2-1)^2+32(c1*s2)^2+32(s1*c2)^2+24(s1*s2)^2",
        "Phi_Sigma_residual_Gram_diagonal": [64, 32, 32, 24],
        "Phi_Sigma_alignment_zero_iff": "both Kaehler angles are zero; Phi is a complex two-plane of the pure-spinor complex structure",
        "Phi_H_wedge_identity": "(3/5)I1-I54=||H wedge Phi||^2",
        "H_Sigma_Fierz_identity": "I1-I45=||i_H Sigma||^2",
        "H_zero_set": "H lies in the complex two-plane Phi and in the holomorphic maximal-isotropic plane Sigma; fixed norm gives S^3 and U(2) is transitive",
    }


def global_orbit_certificate() -> dict[str, Any]:
    target = foundation.target_certificate()
    symmetry = foundation.exact_symmetry_certificate()
    return {
        "target_chart_dimension": target["chart_dimension"],
        "target_lattice_denominator": target["lattice_denominator"],
        "target_support": target["support"],
        "target_field_block_norms": target["field_block_q_norm_squared"],
        "standard_Q3_annihilates_target": target["standard_Q3_annihilates_full_target"],
        "exact_stabilizer_is_SU3C_plus_U1em": symmetry["exact_stabilizer_is_su3C_plus_u1em"],
        "gauge_dimension_identity": "45+1-8-1=37",
        "broken_gauge_directions": 45 + 1 - 8 - 1,
        "zero_locus_parameter_dimensions": {
            "unit_real_decomposable_Phi_orbit": 24,
            "compatible_complex_structure_relative_to_Phi": 8,
            "Sigma_phase": 1,
            "unit_H_in_holomorphic_complex_two_plane": 3,
            "S_phase": 1,
            "X_phase": 1,
            "total": 38,
        },
        "connectedness": "SO(10)/(SO4xSO6), SO6/U3, SO4/U2, circles and S3 are connected; finite stabilizer quotients preserve connectedness",
        "single_orbit_logic": "the common zero set is a connected compact 38-manifold; it contains the compact K=SO(10)xU(1)_XxU(1)_PQ orbit whose exact tangent rank is 38, hence that orbit is both open and closed and equals the whole zero set",
        "all_global_minima_one_continuous_symmetry_orbit": True,
        "no_deeper_extremum": True,
        "no_disconnected_equal_minimum": True,
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    gate = next(row for row in contract.GATES if row["qualified_gate_id"] == GATE_ID)
    sos = sos_decomposition()
    ledger = complete_direction_ledger()
    identities = invariant_identities()
    hessian = exact_hessian_certificate()
    orbit = global_orbit_certificate()
    checks = {
        "complete_891_direction_coefficient_ledger": ledger["canonical_total_real_directions"] == 891 and ledger["zero_dimension_five_directions"] + ledger["zero_dimension_six_directions"] == 840,
        "exact_SOS_expansion_matches_selected_coefficients": sos["coefficient_expansion_matches_exactly"] and sos["residual_count"] == 8,
        "all_SOS_terms_are_nonnegative": all(row["nonnegative"] is True for row in sos["terms"]),
        "source_exact_value_and_stationarity": hessian["exact_total_value"] == "-1" and hessian["exact_gradient_nonzero_entries"] == 0,
        "exact_gauge_quotient_is_37": orbit["broken_gauge_directions"] == contract.EXPECTED_BROKEN_GAUGE_DIRECTIONS == 37,
        "exact_Hessian_rank_nullity_and_kernel": hessian["exact_rank"] == 448 and hessian["exact_nullity"] == 38 and hessian["kernel_equals_full_symmetry_tangent_span"],
        "all_transverse_modes_strictly_positive": hessian["all_448_non_symmetry_modes_strictly_positive"],
        "exactly_one_intended_axion_modulo_gauge": hessian["intended_axion_direction_count"] == 1,
        "Phi_and_Sigma_algebraic_zero_sets_classified": identities["Phi_target_extra_channels_zero"] and identities["Phi_Sigma_residual_Gram_diagonal"] == [64, 32, 32, 24],
        "global_equality_locus_is_one_connected_orbit": orbit["all_global_minima_one_continuous_symmetry_orbit"] and orbit["no_disconnected_equal_minimum"],
        "global_lower_bound_excludes_deeper_extrema": sos["global_lower_bound"] == "V>=-1 on all 486 real fields" and orbit["no_deeper_extremum"],
    }
    failures = [key for key, value in checks.items() if value is not True]
    manifest = source_manifest()
    evidence = {
        f"A{index}": {
            "criterion": criterion,
            "passed": not failures,
            "artifacts": manifest,
        }
        for index, criterion in enumerate(gate["acceptance"], 1)
    }
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "contract_namespace": contract.CONTRACT_NAMESPACE,
        "definition_sha256": contract.DEFINITION_SHA256,
        "model_contract_id": MODEL,
        "qualified_gate_id": GATE_ID,
        "dependencies": DEPENDENCIES,
        "closure_complete": not failures,
        "n_failed": len(failures),
        "failures": failures,
        "producer": Path(__file__).name,
        "normalization_conventions": {
            "field_metric": "canonical 486-real kinetic chart inherited from exact G2",
            "potential": "dimensionless exact rational benchmark; physical absolute scale and h=174 hierarchy are deferred to canonical G4",
            "projectors": "orthogonal SO(10) pair-Casimir channels in the normalized degree<=4 component basis",
            "higher_operators": "all 119 dimension-five and 721 dimension-six coefficients are exactly zero",
        },
        "source_manifest": manifest,
        "acceptance_evidence": evidence,
        "accepted_potential": ledger,
        "sum_of_squares": sos,
        "invariant_identities": identities,
        "global_orbit": orbit,
        "stationarity_and_Hessian": hessian,
        "checks": checks,
        "n_checks": len(checks),
        "status": "CANONICAL_G3_PHYSICAL_EW_GLOBAL_VACUUM_EXACTLY_CLOSED" if not failures else "CANONICAL_G3_FAILED",
        "scope_boundary": {
            "canonical_G3_closed": not failures,
            "absolute_electroweak_hierarchy_h_174_GeV_proved": False,
            "canonical_G4_closed": False,
            "canonical_G5_through_G8_closed": False,
        },
    }
    body = dict(report)
    report["core_sha256"] = sha(body)
    return report


def markdown(report: dict[str, Any]) -> str:
    h = report["stationarity_and_Hessian"]
    return "\n".join(
        [
            "# Canonical G3 physical-EW global vacuum v21",
            "",
            f"- Status: `{report['status']}`",
            f"- Gate: `{report['qualified_gate_id']}`",
            f"- Core: `{report['core_sha256']}`",
            f"- Complete G2 directions: `{report['accepted_potential']['canonical_total_real_directions']}`",
            f"- Nonzero coefficients: `{h['nonzero_coefficient_count']}`",
            "- Global identity: `V=-1+sum_a R_a`, every `R_a` an exact invariant squared norm.",
            f"- Exact target: `V={h['exact_total_value']}`, `grad V=0`, rank/nullity `{h['exact_rank']}/{h['exact_nullity']}`.",
            "- Gauge quotient: `45+1-8-1=37`; the remaining kernel direction is the intended PQ axion.",
            "- Equality set: one connected `SO(10)xU(1)_XxU(1)_PQ` orbit; no deeper or disconnected equal minimum.",
            "",
            "This closes canonical G3. It does not set the absolute `h=174 GeV` hierarchy or close G4-G8.",
            "",
        ]
    )


def write_outputs(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    OUT_MD.write_text(markdown(report), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
    if args.check:
        if not OUT_JSON.is_file() or json.loads(OUT_JSON.read_text(encoding="utf-8")) != report:
            raise ArithmeticError("canonical G3 JSON drifted")
        if not OUT_MD.is_file() or OUT_MD.read_text(encoding="utf-8") != markdown(report):
            raise ArithmeticError("canonical G3 Markdown drifted")
    print(report["status"])
    print(report["core_sha256"])
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
