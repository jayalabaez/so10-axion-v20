#!/usr/bin/env python3
"""V46 global, parity, eta, and residual-discrete audit of the V45 core.

This module deliberately separates four logically different questions:

1. perturbative five-dimensional parity-odd Chern--Simons shifts;
2. traditional homotopy and four-dimensional Witten-anomaly screens;
3. exact Dai--Freed tests for the residual finite symmetry after Higgsing;
4. the unresolved relative eta invariant of the orbifold interval.

Passing the first three items does not imply the fourth.  In particular, the
actual Pati--Salam wall uses a diagonal centre quotient and the interval has
two different boundary gauge groups.  No relative bordism computation or
regulated KK eta spectrum for that stratified problem is imported here.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V46_GLOBAL_PARITY_ETA_AUDIT.json"
MD_PATH = ROOT / "SUSY_V46_GLOBAL_PARITY_ETA_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v46_global_parity_eta_audit.py"

STATUS = (
    "V46_NO_UNAVOIDABLE_FRACTIONAL_5D_HALF_LEVEL_OBSTRUCTION__"
    "TRADITIONAL_HOMOTOPY_AND_WITTEN_SCREENS_PASS__"
    "RESIDUAL_Z3_AND_MATTER_PARITY_COMBINED_Z6_DAI_FREED_CLASS_ZERO__"
    "U5_WALL_SHORTCUT_REJECTED_IN_5D__"
    "ACTUAL_QUOTIENT_INTERVAL_RELATIVE_ETA_BORDISM_OPEN__NO_GATE_PROMOTED"
)

# Primitive, faithful U(1)_F normalization fixed by V45.
HYPERS = (
    {"name": "HLF", "rep": "16", "qF": 1, "eta0": 1, "etaL": 1, "zero_mode": "LF"},
    {"name": "HLA", "rep": "bar16", "qF": -4, "eta0": 1, "etaL": 1, "zero_mode": "LA"},
    {"name": "HRA", "rep": "16", "qF": -1, "eta0": -1, "etaL": 1, "zero_mode": "RA"},
    {"name": "HRF", "rep": "bar16", "qF": 4, "eta0": -1, "etaL": 1, "zero_mode": "RF"},
)

# The 2T entries include spectator dimensions and use 2T(fundamental)=1.
PS_FERMIONS_LIGHT = (
    {
        "name": "3Q",
        "multiplicity": 3,
        "dimension": 8,
        "qF": 1,
        "matter_parity": 1,
        "index_2T": {"SU4": 2, "SU2L": 4, "SU2R": 0},
    },
    {
        "name": "3Qc",
        "multiplicity": 3,
        "dimension": 8,
        "qF": -1,
        "matter_parity": 1,
        "index_2T": {"SU4": 2, "SU2L": 0, "SU2R": 4},
    },
    {
        "name": "H",
        "multiplicity": 1,
        "dimension": 4,
        "qF": 0,
        "matter_parity": 0,
        "index_2T": {"SU4": 0, "SU2L": 2, "SU2R": 2},
    },
)

PS_FERMIONS_EXOTIC = (
    {
        "name": "LF",
        "multiplicity": 1,
        "dimension": 8,
        "qF": 1,
        "matter_parity": 1,
        "index_2T": {"SU4": 2, "SU2L": 4, "SU2R": 0},
    },
    {
        "name": "LA",
        "multiplicity": 1,
        "dimension": 8,
        "qF": -4,
        "matter_parity": 1,
        "index_2T": {"SU4": 2, "SU2L": 4, "SU2R": 0},
    },
    {
        "name": "RA",
        "multiplicity": 1,
        "dimension": 8,
        "qF": -1,
        "matter_parity": 1,
        "index_2T": {"SU4": 2, "SU2L": 0, "SU2R": 4},
    },
    {
        "name": "RF",
        "multiplicity": 1,
        "dimension": 8,
        "qF": 4,
        "matter_parity": 1,
        "index_2T": {"SU4": 2, "SU2L": 0, "SU2R": 4},
    },
)


def signed_mod(value: int, modulus: int) -> int:
    """Return the smallest signed lift, choosing +modulus/2 for an even tie."""

    residue = value % modulus
    if residue > modulus // 2:
        residue -= modulus
    return residue


def crt_z3_z2_to_z6(q3: int, q2: int) -> int:
    """Chinese-remainder lift of (q3 mod 3, q2 mod 2) to a signed Z6 charge."""

    candidates = [value for value in range(6) if value % 3 == q3 % 3 and value % 2 == q2 % 2]
    if len(candidates) != 1:
        raise RuntimeError("CRT lift is not unique")
    return signed_mod(candidates[0], 6)


def sum_rows(rows: Iterable[Mapping[str, int]], keys: Iterable[str]) -> dict[str, int]:
    keys = tuple(keys)
    return {key: sum(int(row[key]) for row in rows) for key in keys}


def parity_half_level_audit() -> dict[str, Any]:
    """Conventional 5D Dirac half-levels in the primitive charge lattice.

    We normalize T(10)=1 and T(16)=T(bar16)=2.  A complex 5D Dirac
    fermion then has the conventional parity-odd shifts

      (1/2) q T(R), (1/2) dim(R) q^3, (1/2) dim(R) q

    for F-Spin(10)^2, F^3, and F-gravity respectively.  A regulator/mass
    orientation multiplies all entries of a row by a sign.  The sign is not
    fixed by the V45 manifest.
    """

    rows = []
    for hyper in HYPERS:
        q = int(hyper["qF"])
        row = {
            **hyper,
            "dim_rep": 16,
            "T_rep_T10_vector_eq_1": 2,
            "delta_k_F_Spin10_squared": q,
            "delta_k_F_cubed": 8 * q**3,
            "delta_k_F_gravity": 8 * q,
            "delta_k_Spin10_cubed": 0,
        }
        # On a closed spin six-manifold the two free U(1) anomaly generators
        # can be labelled by ((A_cub-A_grav)/6, A_grav).  Check this correlated
        # lattice, not merely integrality of the two displayed coefficients.
        numerator = row["delta_k_F_cubed"] - row["delta_k_F_gravity"]
        if numerator % 6:
            raise RuntimeError("half-level misses the closed-spin U(1) lattice")
        row["closed_spin_U1_basis"] = {
            "(k_F_cubed-k_F_gravity)/6": numerator // 6,
            "k_F_gravity": row["delta_k_F_gravity"],
        }
        row["all_displayed_half_levels_integral"] = all(
            isinstance(row[key], int)
            for key in (
                "delta_k_F_Spin10_squared",
                "delta_k_F_cubed",
                "delta_k_F_gravity",
                "delta_k_Spin10_cubed",
            )
        )
        rows.append(row)

    keys = (
        "delta_k_F_Spin10_squared",
        "delta_k_F_cubed",
        "delta_k_F_gravity",
        "delta_k_Spin10_cubed",
    )
    totals = sum_rows(rows, keys)
    pair_totals = {
        "unit_charge_pair_HLF_HRA": sum_rows((rows[0], rows[2]), keys),
        "charge_four_pair_HLA_HRF": sum_rows((rows[1], rows[3]), keys),
    }

    # At the y=L Spin(10) wall, every H chiral is even.  The localized
    # coefficient is half the 4D anomaly.  The mixed row below uses 2T and is
    # consequently twice the bulk-CS convention above.
    source_rows = []
    for hyper in HYPERS:
        q = int(hyper["qF"])
        source_rows.append(
            {
                "name": hyper["name"],
                "qF": q,
                "etaL": hyper["etaL"],
                "half_4d_U1F_Spin10_squared_doubled": 2 * q,
                "half_4d_U1F_cubed": 8 * q**3,
                "half_4d_gravity_squared_U1F": 8 * q,
                "half_4d_Spin10_cubed": 0,
            }
        )
    source_keys = (
        "half_4d_U1F_Spin10_squared_doubled",
        "half_4d_U1F_cubed",
        "half_4d_gravity_squared_U1F",
        "half_4d_Spin10_cubed",
    )

    return {
        "normalization": {
            "primitive_U1F_unit": 1,
            "Spin10_quadratic_index": "T(10)=1, T(16)=T(bar16)=2",
            "bulk_Dirac_formula": {
                "F_Spin10_squared": "sigma q T(R)/2",
                "F_cubed": "sigma dim(R) q^3/2",
                "F_gravity": "sigma dim(R) q/2",
            },
            "sigma": "regulator or massive-fermion orientation sign, not fixed by V45",
        },
        "rows_at_sigma_plus": rows,
        "common_sigma_totals": totals,
        "pair_totals": pair_totals,
        "every_individual_displayed_shift_has_zero_fractional_part": all(
            row["all_displayed_half_levels_integral"] for row in rows
        ),
        "every_individual_shift_lies_in_closed_spin_U1_free_lattice": all(
            isinstance(row["closed_spin_U1_basis"]["(k_F_cubed-k_F_gravity)/6"], int)
            and isinstance(row["closed_spin_U1_basis"]["k_F_gravity"], int)
            for row in rows
        ),
        "common_regulator_orientation_net_shift_zero": all(value == 0 for value in totals.values()),
        "arbitrary_independent_regulator_signs_can_change_only_integer_levels": True,
        "unavoidable_fractional_parity_counterterm_obstruction_found": False,
        "physical_integer_CS_levels_determined": False,
        "why_not_determined": (
            "V45 does not fix the gauge-invariant regulator, odd bulk-mass signs, or the full compact "
            "product/relative Chern--Simons lattice.  Those choices can change integer levels even though "
            "no listed fermion misses the conventional closed-spin free lattice."
        ),
        "source_wall_half_anomaly_rows": source_rows,
        "source_wall_half_anomaly_totals": sum_rows(source_rows, source_keys),
        "pure_Spin10_cubic_note": (
            "D5 has no rank-three symmetric invariant, so the perturbative Spin(10)^3 row vanishes."
        ),
    }


def wittencounts(include_exotics: bool) -> dict[str, int]:
    fields = PS_FERMIONS_LIGHT + (PS_FERMIONS_EXOTIC if include_exotics else ())
    return {
        "SU2L_fundamental_doublets": sum(
            int(field["multiplicity"]) * int(field["index_2T"]["SU2L"])
            for field in fields
        ),
        "SU2R_fundamental_doublets": sum(
            int(field["multiplicity"]) * int(field["index_2T"]["SU2R"])
            for field in fields
        ),
    }


def homotopy_and_bordism_audit() -> dict[str, Any]:
    before = wittencounts(include_exotics=True)
    after = wittencounts(include_exotics=False)
    return {
        "traditional_sphere_mapping_screen": {
            "pi4_Spin10": 0,
            "pi5_Spin10": 0,
            "pi4_U1": 0,
            "pi5_U1": 0,
            "bulk_product_pi4": 0,
            "bulk_product_pi5": 0,
            "screen_passes": True,
            "qualification": (
                "These stable Bott-periodicity values exclude the traditional pi4/pi5 alarms; "
                "homotopy is neither a necessary nor a sufficient classification of global anomalies."
            ),
        },
        "PS_SU2_Witten_screen": {
            "before_Theta_exotic_masses": before,
            "after_Theta_exotic_masses": after,
            "all_counts_even": all(value % 2 == 0 for value in (*before.values(), *after.values())),
            "counting_note": (
                "The light values are 12 family doublets plus two doublets from H on each side; "
                "the four exotic zero modes add eight doublets to the corresponding side."
            ),
        },
        "known_closed_4d_bordism_results": {
            "Omega5Spin_BSpin10": "0 for Spin(n), n>=8",
            "source_Spin10_only_Dai_Freed_obstruction": False,
            "Omega5Spin_B_unquotiented_PS": "Z2 x Z2",
            "unquotiented_PS_generators": "the two ordinary SU(2) Witten anomalies",
            "unquotiented_PS_class_for_this_spectrum": "0 by the even counts above",
        },
        "neutral_210_repair_effect": {
            "if_adopted_from_V46_source_Higgs_audit": True,
            "qF": 0,
            "Spin10_rep_is_real": True,
            "matter_parity_even": True,
            "changes_displayed_U1F_or_residual_finite_rows": False,
            "must_still_be_included_in_full_boundary_eta_operator": True,
        },
        "actual_group_warning": {
            "actual_PS_wall": "(SU4 x SU2L x SU2R)/Z2_diag",
            "unquotiented_PS_result_applies_verbatim": False,
            "reason": (
                "The cited Pati--Salam bordism computation explicitly treats the unquotiented product and "
                "states that centre-quotient variants require a different computation."
            ),
        },
        "full_interval_bordism_or_eta_complete": False,
    }


def daifreed_spin_zn(charges_with_multiplicity: Iterable[tuple[int, int]], n: int) -> dict[str, Any]:
    signed_rows = tuple((signed_mod(charge, n), int(multiplicity)) for charge, multiplicity in charges_with_multiplicity)
    delta_s1 = sum(charge * multiplicity for charge, multiplicity in signed_rows)
    delta_s3 = sum(charge**3 * multiplicity for charge, multiplicity in signed_rows)
    cubic_lhs = (n * n + 3 * n + 2) * delta_s3
    cubic_modulus = 6 * n
    linear_lhs = 2 * delta_s1
    return {
        "n": n,
        "signed_charge_multiplicities": [
            {"charge": charge, "multiplicity": multiplicity}
            for charge, multiplicity in signed_rows
        ],
        "Delta_s1": delta_s1,
        "Delta_s3": delta_s3,
        "cubic_condition": f"(n^2+3n+2) Delta_s3 = 0 mod 6n",
        "cubic_lhs": cubic_lhs,
        "cubic_modulus": cubic_modulus,
        "cubic_residue": cubic_lhs % cubic_modulus,
        "linear_condition": "2 Delta_s1 = 0 mod n",
        "linear_lhs": linear_lhs,
        "linear_modulus": n,
        "linear_residue": linear_lhs % n,
        "Dai_Freed_class_zero": cubic_lhs % cubic_modulus == 0 and linear_lhs % n == 0,
    }


def spectrum_discrete_rows(include_exotics: bool) -> list[dict[str, Any]]:
    fields = PS_FERMIONS_LIGHT + (PS_FERMIONS_EXOTIC if include_exotics else ())
    rows = []
    for field in fields:
        q3 = signed_mod(int(field["qF"]), 3)
        q2 = int(field["matter_parity"]) % 2
        rows.append(
            {
                "name": field["name"],
                "weyl_multiplicity": int(field["multiplicity"]) * int(field["dimension"]),
                "qF": int(field["qF"]),
                "Z3F": q3,
                "Z2M": q2,
                "Z6_CRT": crt_z3_z2_to_z6(q3, q2),
            }
        )
    return rows


def discrete_mixed_ps_rows(include_exotics: bool, charge_key: str) -> dict[str, int]:
    fields = PS_FERMIONS_LIGHT + (PS_FERMIONS_EXOTIC if include_exotics else ())
    totals = {"SU4_squared": 0, "SU2L_squared": 0, "SU2R_squared": 0, "gravity": 0}
    for field in fields:
        if charge_key == "Z3F":
            charge = signed_mod(int(field["qF"]), 3)
        elif charge_key == "Z2M":
            charge = int(field["matter_parity"]) % 2
        elif charge_key == "Z6_CRT":
            charge = crt_z3_z2_to_z6(int(field["qF"]), int(field["matter_parity"]))
        else:
            raise ValueError(charge_key)
        multiplicity = int(field["multiplicity"])
        for group in ("SU4", "SU2L", "SU2R"):
            totals[f"{group}_squared"] += multiplicity * charge * int(field["index_2T"][group])
        totals["gravity"] += multiplicity * charge * int(field["dimension"])
    return totals


def residual_discrete_audit() -> dict[str, Any]:
    phases: dict[str, Any] = {}
    for phase_name, include_exotics in (("before_exotic_masses", True), ("light_after_exotic_masses", False)):
        rows = spectrum_discrete_rows(include_exotics)
        z3_pairs = [(int(row["Z3F"]), int(row["weyl_multiplicity"])) for row in rows]
        z2_pairs = [(int(row["Z2M"]), int(row["weyl_multiplicity"])) for row in rows]
        z6_pairs = [(int(row["Z6_CRT"]), int(row["weyl_multiplicity"])) for row in rows]
        z3_mixed = discrete_mixed_ps_rows(include_exotics, "Z3F")
        z2_mixed = discrete_mixed_ps_rows(include_exotics, "Z2M")
        z6_mixed = discrete_mixed_ps_rows(include_exotics, "Z6_CRT")
        phases[phase_name] = {
            "fermions": rows,
            "Spin_times_Z3F": daifreed_spin_zn(z3_pairs, 3),
            "Spin_times_Z2M": daifreed_spin_zn(z2_pairs, 2),
            "Spin_times_Z6_CRT": daifreed_spin_zn(z6_pairs, 6),
            "conventional_mixed_PS_doubled_rows": {
                "Z3F": z3_mixed,
                "Z2M": z2_mixed,
                "Z6_CRT": z6_mixed,
            },
            "mixed_rows_divisible_by_respective_modulus": {
                "Z3F": all(value % 3 == 0 for value in z3_mixed.values()),
                "Z2M": all(value % 2 == 0 for value in z2_mixed.values()),
                "Z6_CRT": all(value % 6 == 0 for value in z6_mixed.values()),
            },
        }

    return {
        "Higgsing": {
            "Theta_charges": [3, -3],
            "faithful_U1F_remnant": "Z3F",
            "matter_parity_origin": "the order-two square of the Spin(10) Z4 centre",
            "matter_parity_action": "odd on 16/bar16 matter, even on H, Theta, 126/bar126 and gauge fields",
            "Delta_126_VEV_preserves_Z2M": True,
            "abstract_finite_group": "Z3F x Z2M isomorphic to Z6 by CRT",
            "spacetime_structure": "untwisted Spin x Z6, not Spin^Z4 and not an R symmetry",
        },
        "mass_terms": {
            "ThetaPlus_HLF_HLA_Z3_sum": signed_mod(3 + 1 - 4, 3),
            "ThetaMinus_HRA_HRF_Z3_sum": signed_mod(-3 - 1 + 4, 3),
            "HLF_LA_Z6_sum": signed_mod(1 - 1, 6),
            "RA_RF_Z6_sum": signed_mod(-1 + 1, 6),
            "all_residual_finite_symmetries_preserved": True,
        },
        "phases": phases,
        "pure_finite_Dai_Freed_result": (
            "Both before and after the exotic masses, the Z3 and the full CRT-combined Z6 spectra "
            "are exactly balanced between signed charges +1 and -1.  Hsieh's exact Spin x Zn "
            "congruences therefore vanish.  The ordinary internal Z2 class is also trivial."
        ),
        "mod16_warning": (
            "No mod-16 condition is invoked: that condition belongs to twisted Spin^Z4/time-reversal-like "
            "structures, whereas Z2M here is an ordinary internal matter parity."
        ),
        "combined_with_actual_PS_quotient_and_interval_certified": False,
    }


def relative_eta_obligations() -> dict[str, Any]:
    return {
        "certified": False,
        "problem": (
            "Evaluate the exponentiated APS eta invariant of the complete 5D fermion/ghost system "
            "for every allowed large gauge transformation and gravitational background of the compact "
            "interval theory, including the two inequivalent boundary reductions."
        ),
        "missing_inputs_or_computations": [
            "the exact lift of both orbifold twists to Spin(10) on every bulk representation",
            "the compact line/operator lattice and all allowed non-liftable PS/Z2_diag boundary bundles",
            "the relative or stratified spin-bordism group for the bulk group with its two boundary reductions",
            "self-adjoint fermion boundary conditions after every allowed source mass, including "
            "bar126 HLF HRA and 126 HLA HRF as well as the two Theta masses",
            "the regulated KK eta spectrum, including gauginos, hyperinos, boundary fermions, ghosts and "
            "the neutral 210 boundary fermion if the V46 source-Higgs repair is adopted",
            "the regulator orientation, every odd bulk-mass sign and the quantized bare gauge/gravity CS lattice",
            "an evaluation on generators or a six-dimensional extension proof that the total phase is one",
        ],
        "why_local_cancellation_is_not_enough": (
            "The eta invariant agrees perturbatively with Chern--Simons inflow but contains torsion/global "
            "information.  Product symmetries can have mixed torsion absent in either factor separately."
        ),
        "example_supporting_fail_closed_policy": (
            "Spin x (U1 x Z2) has a Z4 bordism anomaly even though Spin x U1 alone has no 4D global "
            "anomaly; therefore factorwise screens cannot replace the actual combined calculation."
        ),
    }


def alternative_u5_wall_audit() -> dict[str, Any]:
    reps = (
        {"SU5_rep": "10", "n_ality": 2, "q_chi": -1},
        {"SU5_rep": "bar5", "n_ality": -1, "q_chi": 3},
        {"SU5_rep": "1", "n_ality": 0, "q_chi": -5},
    )
    quotient_checks = [
        {
            **rep,
            "n_ality_plus_2q_mod5": (int(rep["n_ality"]) + 2 * int(rep["q_chi"])) % 5,
        }
        for rep in reps
    ]
    singlets = (
        {"name": "chiMinus", "SU5_rep": "1", "q_chi": -10, "qF": 0},
        {"name": "chiPlus", "SU5_rep": "1", "q_chi": 10, "qF": 0},
    )
    return {
        "status": "REJECTED_BY_V46_5D_ZERO_MODE_AND_LOCAL_ANOMALY_AUDIT",
        "wall_group": "(SU5 x U1_chi)/Z5",
        "Spin10_branching_convention": "16 = 10_-1 + bar5_+3 + 1_-5",
        "quotient_representation_condition": "SU5 n-ality + 2 q_chi = 0 mod 5",
        "branching_checks": quotient_checks,
        "boundary_Higgs_pair": list(singlets),
        "singlets_are_honest_quotient_representations": all((2 * int(row["q_chi"])) % 5 == 0 for row in singlets),
        "singlet_pair_local_anomalies_cancel": {
            "U1chi_cubed": sum(int(row["q_chi"]) ** 3 for row in singlets),
            "gravity_squared_U1chi": sum(int(row["q_chi"]) for row in singlets),
            "all_U1F_rows": 0,
        },
        "formal_breaking": {
            "before_quotient": "SU5 x Z10",
            "global_form": "(SU5 x Z10)/Z5",
            "component_group": "Z2 matter parity",
            "matter_is_odd": True,
        },
        "potential_advantage": (
            "A neutral singlet pair can replace the full 126/bar126 boundary spectrum for the single job "
            "of removing U1_chi while retaining matter parity."
        ),
        "independent_V46_5D_result": {
            "source": "SUSY_V46_SOURCE_HIGGS_RANK_AUDIT.json",
            "vector_parity_sectors_Vpp_Vpm_Vmp_Vmm": [13, 8, 12, 12],
            "unwanted_adjoint_chiral_zero_modes": 12,
            "bulk_spinor_intrinsic_sign_assignments_scanned": 16,
            "locally_anomaly_free_assignments": 0,
            "former_PS_half_spinor_zero_modes_remain_intact": False,
            "five_dimensional_shortcut_accepted": False,
        },
        "new_exact_obligations": [
            "exhibit the SU5 x U1_chi involution and its lift in Spin(10), including its square on 16/bar16",
            "give every y=L component parity; an adjoint Z2 can lift as an order-four action on spinors",
            "recompute every localized SU5, U1_chi, U1F and gravitational anomaly, including mixed abelian rows",
            "prove the proposed paired etaL assignment cancels those rows rather than assuming it",
            "recompute the PS/U5 intersection, zero modes and full boundary-mass rank component by component",
            "write and solve a D-flat chiPlus/chiMinus boundary superpotential and physical Hessian",
            "fix the residual global line lattice and redo CS quantization and the relative eta invariant",
            "redo the local and cross-wall operator audit after removing 126/bar126",
        ],
        "global_half_level_screen_alone_does_not_add_a_new_no_go": True,
        "permitted_as_complete_5D_shortcut": False,
        "globally_certified": False,
        "promoted_to_authoritative_candidate": False,
    }


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def provenance() -> dict[str, Any]:
    paths = (
        ROOT / "SUSY_V45_NEW_PHYSICS_MASTER_AUDIT.json",
        ROOT / "SUSY_V45_RECONCILED_BULK_SPINOR_AUDIT.json",
        ROOT / "SUSY_V45_S0_GROUP_ZERO_MODE_AUDIT.json",
        ROOT / "SUSY_V46_SOURCE_HIGGS_RANK_AUDIT.json",
        Path(__file__).resolve(),
        TEST_PATH,
    )
    return {
        "files": [
            {
                "path": path.name,
                "exists": path.is_file(),
                "sha256": sha256_file(path) if path.is_file() else None,
            }
            for path in paths
        ]
    }


def build_report() -> dict[str, Any]:
    parity = parity_half_level_audit()
    homotopy = homotopy_and_bordism_audit()
    discrete = residual_discrete_audit()
    relative = relative_eta_obligations()
    alternative = alternative_u5_wall_audit()

    report = {
        "schema": "susy-v46-global-parity-eta-audit-v1",
        "status": STATUS,
        "scope": (
            "Global/parity/eta screens for the exact primitive-charge V45 compact witness, plus a "
            "fail-closed assessment of the proposed U5-wall simplification."
        ),
        "authoritative_input": {
            "bulk_group": "Spin(10) x U(1)_F, direct product",
            "PS_wall_group": "(SU4 x SU2L x SU2R)/Z2_diag x U(1)_F",
            "source_wall_group": "Spin(10) x U(1)_F before boundary Higgsing",
            "bulk_hypers": [dict(hyper) for hyper in HYPERS],
            "PS_boundary": ["3Q=(4,2,1)_+1", "3Qc=(bar4,1,2)_-1", "H=(1,2,2)_0"],
            "source_boundary": [
                "ThetaPlus_+3",
                "ThetaMinus_-3",
                "STheta_0",
                "126_0",
                "bar126_0",
            ],
            "charge_normalization": "primitive local-particle U(1)_F unit charge",
        },
        "five_dimensional_parity_half_levels": parity,
        "homotopy_and_four_dimensional_bordism_screens": homotopy,
        "residual_Z3F_and_matter_parity": discrete,
        "relative_interval_eta": relative,
        "conditional_U5_wall_simplification": alternative,
        "decision": {
            "unavoidable_fractional_5D_half_level_obstruction_found": False,
            "common_orientation_net_displayed_half_levels_zero": True,
            "physical_integer_CS_level_fixed": False,
            "traditional_homotopy_screen_passes": True,
            "PS_SU2_Witten_screens_pass": True,
            "source_Spin10_only_Dai_Freed_screen_passes": True,
            "pure_residual_Z3F_Dai_Freed_class_zero": True,
            "pure_residual_matter_parity_class_zero": True,
            "pure_combined_Z6_Dai_Freed_class_zero": True,
            "actual_quotient_relative_eta_certified": False,
            "complete_global_anomaly_audit": False,
            "V45_killed_by_this_audit": False,
            "G1_closed": False,
            "gates_promoted": [],
        },
        "scientific_verdict": (
            "V46 finds no fractional parity-level, traditional homotopy, SU(2) Witten, or residual finite-"
            "symmetry obstruction in the fixed V45 spectrum.  This is real progress but not closure: the "
            "compact PS centre quotient, two boundary reductions, regulator/CS lattice and full KK eta "
            "determinant have not been assembled into a relative bordism calculation."
        ),
        "primary_sources": [
            {
                "url": "https://arxiv.org/abs/1302.2918",
                "use": "one-loop 5D gauge and gravitational Chern--Simons shifts from massive Dirac fermions",
            },
            {
                "url": "https://arxiv.org/abs/1909.08775",
                "use": "nonperturbative anomaly inflow and the APS eta invariant",
            },
            {
                "url": "https://arxiv.org/abs/1808.02881",
                "use": "exact Dai--Freed anomaly congruences for untwisted Spin x Z_n",
            },
            {
                "url": "https://arxiv.org/abs/1808.00009",
                "use": "Omega_5^Spin(BSpin(n))=0 for n>=8 and Spin(10) Dai--Freed audit",
            },
            {
                "url": "https://arxiv.org/abs/1910.11277",
                "use": "unquotiented Pati--Salam bordism Z2 x Z2 and explicit quotient caveat",
            },
            {
                "url": "https://arxiv.org/abs/2012.11693",
                "use": "why homotopy groups do not classify global anomalies",
            },
            {
                "url": "https://arxiv.org/abs/hep-th/0110073",
                "use": "localized fermion anomalies in orbifold field theories",
            },
            {
                "url": "https://arxiv.org/abs/hep-th/0305024",
                "use": "orbifold projector formula and local versus integrated anomaly cancellation",
            },
            {
                "url": "https://arxiv.org/abs/2311.18023",
                "use": "explicit warning that product symmetries can possess new mixed torsion anomalies",
            },
        ],
        "provenance": provenance(),
    }
    report["core_sha256"] = canonical_sha(report)
    validate(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report["status"] != STATUS:
        raise RuntimeError("status drifted")
    if canonical_sha(report) != report["core_sha256"]:
        raise RuntimeError("stale core hash")
    parity = report["five_dimensional_parity_half_levels"]
    if parity["common_sigma_totals"] != {
        "delta_k_F_Spin10_squared": 0,
        "delta_k_F_cubed": 0,
        "delta_k_F_gravity": 0,
        "delta_k_Spin10_cubed": 0,
    }:
        raise RuntimeError("unexpected common-orientation half-level total")
    if not parity["every_individual_displayed_shift_has_zero_fractional_part"]:
        raise RuntimeError("a fractional parity level was introduced")
    if not parity["every_individual_shift_lies_in_closed_spin_U1_free_lattice"]:
        raise RuntimeError("a half-level misses the correlated spin-U1 lattice")
    if parity["physical_integer_CS_levels_determined"]:
        raise RuntimeError("V46 cannot fix integer CS levels without regulator data")

    homotopy = report["homotopy_and_four_dimensional_bordism_screens"]
    if homotopy["PS_SU2_Witten_screen"]["before_Theta_exotic_masses"] != {
        "SU2L_fundamental_doublets": 22,
        "SU2R_fundamental_doublets": 22,
    }:
        raise RuntimeError("unexpected pre-mass Witten count")
    if homotopy["PS_SU2_Witten_screen"]["after_Theta_exotic_masses"] != {
        "SU2L_fundamental_doublets": 14,
        "SU2R_fundamental_doublets": 14,
    }:
        raise RuntimeError("unexpected light Witten count")

    phases = report["residual_Z3F_and_matter_parity"]["phases"]
    for phase in phases.values():
        for key in ("Spin_times_Z3F", "Spin_times_Z2M", "Spin_times_Z6_CRT"):
            if not phase[key]["Dai_Freed_class_zero"]:
                raise RuntimeError(f"nonzero residual discrete class: {key}")
        if not all(phase["mixed_rows_divisible_by_respective_modulus"].values()):
            raise RuntimeError("a conventional mixed residual row is nonzero")

    alternative = report["conditional_U5_wall_simplification"]
    if not alternative["singlets_are_honest_quotient_representations"]:
        raise RuntimeError("the proposed U5 singlets are not quotient-valid")
    if any(alternative["singlet_pair_local_anomalies_cancel"].values()):
        raise RuntimeError("the proposed U5 singlet pair is locally anomalous")
    if alternative["globally_certified"] or alternative["promoted_to_authoritative_candidate"]:
        raise RuntimeError("conditional U5 route was incorrectly promoted")
    if alternative["permitted_as_complete_5D_shortcut"]:
        raise RuntimeError("rejected U5 route was incorrectly accepted")
    u5_result = alternative["independent_V46_5D_result"]
    if u5_result["unwanted_adjoint_chiral_zero_modes"] != 12:
        raise RuntimeError("unexpected U5 adjoint-chiral count")
    if u5_result["locally_anomaly_free_assignments"] != 0:
        raise RuntimeError("unexpected U5 anomaly scan result")

    decision = report["decision"]
    if decision["complete_global_anomaly_audit"] or decision["G1_closed"] or decision["gates_promoted"]:
        raise RuntimeError("fail-closed decision drifted")


def render_markdown(data: Mapping[str, Any]) -> str:
    parity = data["five_dimensional_parity_half_levels"]
    homotopy = data["homotopy_and_four_dimensional_bordism_screens"]
    phases = data["residual_Z3F_and_matter_parity"]["phases"]
    pre = phases["before_exotic_masses"]
    low = phases["light_after_exotic_masses"]
    before_witten = homotopy["PS_SU2_Witten_screen"]["before_Theta_exotic_masses"]
    after_witten = homotopy["PS_SU2_Witten_screen"]["after_Theta_exotic_masses"]
    half_rows = parity["rows_at_sigma_plus"]

    half_lines = "\n".join(
        f"- `{row['name']} {row['rep']}_{row['qF']:+d}`: "
        f"`Delta k_(F Spin10^2)={row['delta_k_F_Spin10_squared']:+d}`, "
        f"`Delta k_(F^3)={row['delta_k_F_cubed']:+d}`, "
        f"`Delta k_(F grav)={row['delta_k_F_gravity']:+d}`."
        for row in half_rows
    )
    obligations = "\n".join(
        f"- {item}" for item in data["relative_interval_eta"]["missing_inputs_or_computations"]
    )
    u5_obligations = "\n".join(
        f"- {item}" for item in data["conditional_U5_wall_simplification"]["new_exact_obligations"]
    )

    return f"""# V46 global, parity and eta audit

Status: `{data['status']}`

## Result

No unavoidable fractional five-dimensional parity level is generated by the four
primitive-charge bulk spinors.  The traditional large-gauge homotopy screens,
both Pati--Salam `SU(2)` Witten tests, and the exact discrete-only Dai--Freed
tests for `Z3_F`, matter parity, and their CRT-combined `Z6` all pass.

This does **not** close G1.  The actual interval has the centre-quotiented wall
`(SU4 x SU2L x SU2R)/Z2_diag`, a different full-Spin(10) wall, boundary mass
conditions, and an unspecified regulator/CS lattice.  Its relative APS eta
invariant has not been computed.  V46 therefore removes several candidate
obstructions but remains fail-closed.

## Five-dimensional half-level arithmetic

Use the primitive local-particle charge unit and `T(10)=1`,
`T(16)=T(bar16)=2`.  For one complex 5D Dirac fermion, the conventional
half-levels are `sigma q T(R)/2`, `sigma dim(R) q^3/2`, and
`sigma dim(R) q/2` for `F-Spin10^2`, `F^3`, and `F-gravity`.
At common orientation `sigma=+1`:

{half_lines}

Every entry is an integer.  More strongly, every pair
`((Delta k_F3-Delta k_Fgrav)/6, Delta k_Fgrav)` is integral in the standard
closed-spin `U1` free-anomaly basis, so no individual hyper forces a fractional
bare counterterm in that sector.  The `(+1,-1)` and `(-4,+4)` pairs each sum to zero; hence the
common-orientation total is exactly `(0,0,0)`.  The absence of a Spin(10)
cubic invariant makes the pure nonabelian row zero.

This arithmetic does not determine the physical integer levels.  Independent
regulator choices or unspecified odd bulk-mass signs can shift them by integers,
and the complete product/relative compact CS lattice has not been derived.  The source-wall localized
half-anomaly rows also sum exactly to zero in V45's doubled-index convention.

## Homotopy and bordism screens

Stable Bott periodicity gives `pi4(Spin10)=pi5(Spin10)=0`; the corresponding
groups for `U1` also vanish.  This rules out the traditional sphere-mapping
alarms, not every global anomaly.  Modern global anomaly classification uses
bordism and exponentiated eta invariants, and nonzero homotopy is neither
necessary nor sufficient.

The Pati--Salam doublet counts are
`({before_witten['SU2L_fundamental_doublets']},{before_witten['SU2R_fundamental_doublets']})`
before the four exotic masses and
`({after_witten['SU2L_fundamental_doublets']},{after_witten['SU2R_fundamental_doublets']})`
afterward.  They are even on both `SU(2)` factors.  The published result
`Omega5^Spin(B(SU2 x SU2 x SU4)) = Z2 x Z2` identifies precisely these two
Witten classes.  Crucially, that calculation explicitly does not cover the
V45 diagonal-centre quotient.

For a four-dimensional full-Spin(10) boundary,
`Omega5^Spin(BSpin(10))=0`; thus there is no Spin(10)-only Dai--Freed class.
The neutral real `210` selected by the parallel V46 source-Higgs repair changes
none of the displayed `U1_F`, `Z3_F`, or matter-parity rows, although its
boundary fermion must be included in the eventual full eta operator.
That fact does not by itself compute the bulk/direct-product/relative interval
problem.

## Residual `Z3_F` and matter parity

`Theta+/-` with primitive charges `+/-3` leave faithful `Z3_F`.  The order-two
square of the `Spin(10)` centre is matter parity: all `16/bar16` matter is odd,
while `H`, `Theta`, `126/bar126`, and gauge fields are even.  A 126 VEV therefore
preserves it.  Because the parent group is a direct product, the finite subgroup
is abstractly `Z3_F x Z2_M ~= Z6`.

For untwisted `Spin x Z_n`, Hsieh's exact conditions are
`(n^2+3n+2) Delta s3 = 0 mod 6n` and `2 Delta s1 = 0 mod n`.
In the light spectrum, the 24 Weyl components in `3Q` have combined signed
`Z6` charge `+1`, and the 24 in `3Qc` have `-1`.  Before exotic lifting there
are an additional 16 of each sign.  Therefore `Delta s1=Delta s3=0` exactly
for both `Z3` and `Z6` in both phases.  The computed class flags are:

- before masses: `Z3={pre['Spin_times_Z3F']['Dai_Freed_class_zero']}`,
  `Z2_M={pre['Spin_times_Z2M']['Dai_Freed_class_zero']}`,
  `Z6={pre['Spin_times_Z6_CRT']['Dai_Freed_class_zero']}`;
- after masses: `Z3={low['Spin_times_Z3F']['Dai_Freed_class_zero']}`,
  `Z2_M={low['Spin_times_Z2M']['Dai_Freed_class_zero']}`,
  `Z6={low['Spin_times_Z6_CRT']['Dai_Freed_class_zero']}`.

The conventional doubled mixed PS rows are divisible by 3, 2, and 6 as
appropriate.  Both Theta mass terms preserve the finite group.  No mod-16
claim is used: that belongs to a twisted `Spin^Z4` structure, not this ordinary
internal matter parity.

These statements certify the finite-symmetry-only eta class and its conventional
mixed polynomial reductions.  They do not certify finite symmetry combined with
non-liftable bundles of the actual PS quotient on the interval.

## Exact remaining eta obligation

{data['relative_interval_eta']['problem']}

The missing inputs/calculations are:

{obligations}

This separation is essential.  The eta invariant agrees perturbatively with a
Chern--Simons functional but contains additional global information.  There are
known examples where a product such as `U1 x Z2` has mixed torsion even though
the continuous factor alone has no global anomaly.

## Conditional `(SU5 x U1_chi)/Z5` wall

The proposed boundary singlets `chi_(-10)+chibar_(+10)` are honest
representations of `(SU5 x U1_chi)/Z5`: with
`16=10_-1+bar5_+3+1_-5`, the quotient condition is
`SU5 n-ality + 2 q_chi = 0 mod 5`.  Their cubic and gravitational `U1_chi`
anomalies cancel pairwise.  Formally their VEV leaves
`(SU5 x Z10)/Z5`, whose component group is the desired matter-parity `Z2`.
This can remove the need for the full 126 spectrum for that one breaking job.

The global half-level screen by itself adds no new obstruction.  However, the
independent V46 source-Higgs audit now rejects this as a five-dimensional
shortcut: the vector parity sectors are `(13,8,12,12)`, so the twelve `V--`
generators become twelve unwanted adjoint-chiral zero modes; the GG parity
fragments the intended PS half-spinor zero modes; and an exhaustive scan of all
16 intrinsic bulk-spinor sign assignments finds zero assignments cancelling
all displayed source-wall anomaly rows.  The healthy singlet Hessian therefore
does not rescue the route.

Any materially redesigned version would incur these exact obligations:

{u5_obligations}

In particular, saying that paired `etaL` signs cancel the split wall spectrum is
false for the fixed four-spinor V45 content under the scanned GG parity.  Extra
matter or a different higher-dimensional construction would be new physics,
not a simplification of the present 5D witness.

## Decision

V46 does not kill the V45 core, but it does not close G1 or any other gate.
The next decisive calculation is the relative/stratified bordism and regulated
KK eta invariant for the fixed global groups and boundary conditions.  If that
cannot be supplied, the theory remains incomplete rather than anomaly-free by
assertion.

Primary sources: [Bonetti, Grimm and Hohenegger](https://arxiv.org/abs/1302.2918),
[Witten and Yonekura](https://arxiv.org/abs/1909.08775),
[Hsieh](https://arxiv.org/abs/1808.02881),
[Garcia-Etxebarria and Montero](https://arxiv.org/abs/1808.00009),
[Davighi, Gripaios and Lohitsiri](https://arxiv.org/abs/1910.11277),
[Davighi and Lohitsiri](https://arxiv.org/abs/2012.11693),
[Scrucca et al.](https://arxiv.org/abs/hep-th/0110073),
[von Gersdorff and Quiros](https://arxiv.org/abs/hep-th/0305024), and
[Davighi, Lohitsiri and Poovuttikul](https://arxiv.org/abs/2311.18023).

Core SHA-256: `{data['core_sha256']}`
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    expected_md = render_markdown(report)
    if args.write:
        JSON_PATH.write_text(expected_json, encoding="utf-8")
        MD_PATH.write_text(expected_md, encoding="utf-8")
        print("V46_GLOBAL_PARITY_ETA_AUDIT_WRITE_PASS")
    if args.check:
        if not JSON_PATH.is_file() or not MD_PATH.is_file():
            raise SystemExit("V46 artifacts missing; run --write")
        if JSON_PATH.read_text(encoding="utf-8") != expected_json:
            raise SystemExit("V46 JSON stale; run --write")
        if MD_PATH.read_text(encoding="utf-8") != expected_md:
            raise SystemExit("V46 Markdown stale; run --write")
        print("V46_GLOBAL_PARITY_ETA_AUDIT_CHECK_PASS")


if __name__ == "__main__":
    main()
