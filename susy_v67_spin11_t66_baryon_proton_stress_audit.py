from __future__ import annotations

"""V67 fail-closed baryon/proton stress audit for the V66 Spin(11) routes.

This certificate does four things and deliberately does not promote a gate:

* derives the U-type T66 Schur complement, including the antisymmetric-family
  ``1/2`` convention;
* proves a scoped one-sided-portal no-go for Abelian selectors with full-rank
  unified Yukawa support, zero Higgs charge and a GM-neutral bilinear;
* exhibits a conditional low-energy ``Z3`` baryon-triality assignment whose
  standard linear and integer-parent cubic checks pass, and which is minimal
  only inside the declared finite scan, while rejecting it as a current-action
  repair because it splits unified multiplets; and
* applies the repository-frozen dimension-six proton proxy to the H66 and T66
  gauge-only crossings.

All numerical proton results are conditional diagnostics.  No pole mass,
Wilson likelihood, lifetime prediction, current-action acceptance, or gate
closure is asserted.
"""

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
ROUTE_PATH = ROOT / "SUSY_V66_SPIN11_GM_OVERLAP_UNIFICATION_REPAIR_AUDIT.json"
MASTER_PATH = ROOT / "SUSY_V66_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V55_PATH = ROOT / "SUSY_V55_R1_DEGREE9_PROTON_FEASIBILITY_AUDIT.json"
PROTON_SOURCE_PATH = ROOT / "proton_decay_falsification_gate_v20.py"
FLAVOUR_SOURCE_PATH = ROOT / "xy_flavour_rotations_gauge_v20.py"
SCALAR_SOURCE_PATH = ROOT / "scalar_vacuum_proton_decay_v20.py"
TEST_PATH = ROOT / "test_susy_v67_spin11_t66_baryon_proton_stress_audit.py"
JSON_PATH = ROOT / "SUSY_V67_SPIN11_T66_BARYON_PROTON_STRESS_AUDIT.json"
MD_PATH = ROOT / "SUSY_V67_SPIN11_T66_BARYON_PROTON_STRESS_AUDIT.md"

EXPECTED_V66_ROUTE_CORE = (
    "07593002755158c96647701da7453b1942114424a5d3aff5318ebb891a2964ae"
)
EXPECTED_V66_MASTER_CORE = (
    "499382834b9b63a23e10dbc16106dfb1db0f2bfeae17163862afd4f1467e9fa4"
)
EXPECTED_V55_CORE = (
    "6959457039b2828c1602e0e0e225b90a24da402260c24b39535a6c3783cbc665"
)
EXPECTED_PROTON_SOURCE_RAW = (
    "f2d875ba665707a929bf912dfc83af547452d04cb8ebb6932e67dffd076dd921"
)
EXPECTED_FLAVOUR_SOURCE_RAW = (
    "a14afb173bca71fbdab0e87995945b1e9de1f1591c5a564e41eecfffaf42ce49"
)
EXPECTED_SCALAR_SOURCE_RAW = (
    "3b82f262193d585d27d4b19ffc80ad656b9f19e7ff00cef6eefe19c4a6e25d9f"
)

SCHEMA = "susy_v67_spin11_t66_baryon_proton_stress_audit/v1"
STATUS = (
    "V67_SPIN11_T66_BARYON_PROTON_STRESS__V66_ROUTE_AND_MASTER_CORES_BOUND__"
    "UPTYPE_PORTAL_SCHUR_COMPLEMENT_EXACT__PRE_MAJORANA_DELTA_B_EQUALS_DELTA_L_"
    "EQUALS_MINUS_ONE__SCOPED_FAMILY_DEPENDENT_UNIFIED_ABELIAN_ONE_SIDED_"
    "SELECTOR_NO_GO__CONDITIONAL_"
    "IR_BARYON_TRIALITY_LINEAR_MOD3_AND_CUBIC_MOD9_PASS_BUT_NOT_LOCALLY_EMBEDDED__"
    "H66_CENTRAL_GAUGE_PROXY_"
    "FAILS__T66_CENTRAL_GAUGE_PROXY_PASSES__NO_LIFETIME_PREDICTION__CURRENT_"
    "ACTION_REJECTED__G1_TO_G8_OPEN_ZERO_PROMOTIONS"
)

# Repository-frozen p -> e+ pi0 proxy constants.  The width skeleton and
# defaults are independently replayed here and source-hash pinned above.
PROTON_PROXY = {
    "m_p_GeV": 0.9382720813,
    "m_pi0_GeV": 0.1349768,
    "V_ud": 0.97367,
    "A_R": 2.5,
    "hadronic_W_GeV2": 0.11,
    "hbar_GeV_s": 6.582119569e-25,
    "seconds_per_year": 365.25 * 24.0 * 3600.0,
    "limit_years_90CL": 2.4e34,
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha(value: Mapping[str, Any], key: str = "core_sha256") -> str:
    payload = dict(value)
    payload.pop(key, None)
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_bound(path: Path, expected_core: str, label: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    actual = value.get("core_sha256")
    if actual != expected_core:
        raise RuntimeError(
            f"{label} core drifted: expected {expected_core}, observed {actual}"
        )
    if canonical_sha(value) != expected_core:
        raise RuntimeError(f"{label} canonical payload does not reproduce its core")
    return value


def _require_raw(path: Path, expected: str, label: str) -> None:
    actual = file_sha(path)
    if actual != expected:
        raise RuntimeError(
            f"{label} raw source drifted: expected {expected}, observed {actual}"
        )


def portal_schur_complement() -> dict[str, Any]:
    """Derive the exact U-companion Schur complement.

    In the heavy basis ``(Uc_X, U_X)`` the normalized quadratic matrix is the
    off-diagonal involution.  With sources ``A=(1/2) lambda dd`` and
    ``B=rho u N``, eliminating the two heavy fields gives ``-AB/M10``.
    """

    normalized_mass = [[0, 1], [1, 0]]
    inverse = [[0, 1], [1, 0]]
    product = [
        [sum(normalized_mass[i][k] * inverse[k][j] for k in range(2)) for j in range(2)]
        for i in range(2)
    ]
    determinant = normalized_mass[0][0] * normalized_mass[1][1] - (
        normalized_mass[0][1] * normalized_mass[1][0]
    )
    return {
        "heavy_basis": ["Uc_X", "U_X"],
        "superpotential": (
            "W=M10 Uc_X U_X + (1/2) lambda_ij epsilon^abc Uc_X,a "
            "dc_i,b dc_j,c + rho_kl U_X^a uc_k,a Nc_l"
        ),
        "family_convention": {
            "lambda_symmetry": "lambda_ij=-lambda_ji",
            "full_ordered_family_sum_prefactor": "1/2",
            "i_less_than_j_sum_prefactor": "1",
        },
        "normalized_quadratic_matrix": normalized_mass,
        "normalized_inverse": inverse,
        "matrix_times_inverse": product,
        "normalized_determinant": determinant,
        "sources": {
            "A": "(1/2) lambda_ij epsilon^abc dc_i,b dc_j,c",
            "B": "rho_kl uc_k,a Nc_l",
        },
        "stationary_solution": {
            "Uc_X": "-B/M10",
            "U_X": "-A/M10",
        },
        "schur_identity": "-1/2 J^T M_H^-1 J = -A B/M10",
        "effective_superpotential_ordered_sum": (
            "W_eff=-(lambda_ij rho_kl/(2 M10)) epsilon^abc "
            "uc_k,a dc_i,b dc_j,c Nc_l"
        ),
        "effective_superpotential_i_less_than_j": (
            "W_eff=-(lambda_ij rho_kl/M10) epsilon^abc "
            "uc_k,a dc_i,b dc_j,c Nc_l"
        ),
        "global_numbers": {
            "scope": "pre-Majorana matching: uc dc dc Nc",
            "B_of_uc_dc_dc": "-1",
            "L_of_Nc": "-1",
            "Delta_B": -1,
            "Delta_L": -1,
            "Delta_B_minus_L": 0,
        },
        "heavy_N_matching": {
            "index_convention": (
                "W_N=(1/2) Nc_l (M_N)_{lm} Nc_m + "
                "(y_nu)_{r m} L_r Hu Nc_m"
            ),
            "mixing_tensor": (
                "theta_{l r}=sum_m (M_N^-1)_{l m} (y_nu)_{r m} v_u"
            ),
            "before_EWSB": (
                "C6_hol_{ijkr}=+(lambda_ij/(2 M10)) sum_l rho_{k l} "
                "sum_m (M_N^-1)_{l m} (y_nu)_{r m} for the ordered-family "
                "uc_k dc_i dc_j L_r Hu operator"
            ),
            "after_EWSB": (
                "C5_{ijkr}=+(lambda_ij/(2 M10)) sum_l rho_{k l} "
                "theta_{l r}; omit 1/2 when summing only i<j"
            ),
            "post_Majorana_field_numbers": {
                "operator": "uc dc dc L Hu",
                "Delta_B": -1,
                "Delta_L": 1,
                "Delta_B_minus_L": -2,
                "Delta_B_plus_L": 0,
                "reason": "the Majorana inverse-mass insertion violates lepton number by two units",
                "physical_amplitude_caveat": (
                    "the Hermitian-conjugate process reverses all displayed field-number signs"
                ),
            },
            "claim": "conditional coefficient map, not a proton lifetime",
        },
        "exact_derivation_pass": product == [[1, 0], [0, 1]] and determinant == -1,
    }


def unified_selector_no_go() -> dict[str, Any]:
    """Exact family-dependent no-go for the scoped unified Abelian selector.

    Structural full rank means that the allowed Yukawa support has at least
    one nonzero determinant monomial.  Its permutation supplies the
    complementary family pair for the conjugate portal.
    """

    families = range(3)
    family_pairs = list(itertools.combinations(families, 2))
    permutations = list(itertools.permutations(families))
    by_type: dict[str, Any] = {}
    total_charge_assignments = 0
    total_full_rank_assignments = 0
    total_wanted_portal_cases = 0
    counterexamples: list[dict[str, Any]] = []
    sample_witnesses: list[dict[str, Any]] = []
    for selector_type in ("ordinary", "R"):
        modulus_rows = []
        for modulus in range(2, 25):
            w = 0 if selector_type == "ordinary" else 2 % modulus
            assignments = modulus**3
            full_rank_assignments = 0
            wanted_portal_cases = 0
            total_charge_assignments += assignments
            for charges in itertools.product(range(modulus), repeat=3):
                determinant_permutations = [
                    permutation
                    for permutation in permutations
                    if all(
                        (charges[i] + charges[permutation[i]] - w) % modulus == 0
                        for i in families
                    )
                ]
                if not determinant_permutations:
                    continue
                full_rank_assignments += 1
                total_full_rank_assignments += 1
                determinant_permutation = determinant_permutations[0]
                for i, j in family_pairs:
                    wanted_portal_cases += 1
                    total_wanted_portal_cases += 1
                    c = (w - charges[i] - charges[j]) % modulus
                    cbar = (-c) % modulus  # Kahler/GM C Cbar neutrality
                    allowed_conjugate_pairs = [
                        [k, ell]
                        for k in families
                        for ell in families
                        if (cbar + charges[k] + charges[ell] - w) % modulus == 0
                    ]
                    if not allowed_conjugate_pairs:
                        counterexamples.append(
                            {
                                "type": selector_type,
                                "modulus": modulus,
                                "family_charges": list(charges),
                                "wanted_pair": [i, j],
                                "c": c,
                                "cbar": cbar,
                            }
                        )
                        continue
                    k = determinant_permutation[i]
                    ell = determinant_permutation[j]
                    if [k, ell] not in allowed_conjugate_pairs:
                        raise RuntimeError("determinant-permutation witness failed")
                    if len(sample_witnesses) < 8:
                        sample_witnesses.append(
                            {
                                "type": selector_type,
                                "modulus": modulus,
                                "family_charges": list(charges),
                                "determinant_permutation": list(
                                    determinant_permutation
                                ),
                                "wanted_pair": [i, j],
                                "wanted_companion_charge_c": c,
                                "GM_partner_charge_cbar": cbar,
                                "guaranteed_conjugate_pair": [k, ell],
                            }
                        )
            modulus_rows.append(
                {
                    "modulus": modulus,
                    "charge_assignments": assignments,
                    "structurally_full_rank_assignments": full_rank_assignments,
                    "wanted_portal_cases": wanted_portal_cases,
                }
            )
        by_type[selector_type] = modulus_rows
    if counterexamples:
        raise RuntimeError(
            f"family-dependent unified-selector counterexamples: {counterexamples[:3]}"
        )
    return {
        "assumptions": [
            "the selector is Abelian and component-uniform inside each unified matter multiplet, but family charges f_i may differ",
            "the gauge-Higgs selector charge h is zero",
            "the allowed symmetric FFH Yukawa support is structurally full rank",
            "at least one wanted C F_i F_j portal with i not equal to j is allowed",
            "the vectorlike C Cbar bilinear is Kahler/GM neutral: c+cbar=0",
            "the conjugate Cbar F_k F_l gauge contraction exists for arbitrary family labels, as it does for the T66 U-channel",
        ],
        "determinant_permutation_theorem": {
            "structural_rank_statement": (
                "a nonzero Yukawa determinant term supplies one permutation sigma "
                "with f_i+f_sigma(i)=w for every i"
            ),
            "wanted_portal": "c+f_i+f_j=w",
            "GM_neutrality": "cbar=-c",
            "complementary_families": (
                "f_sigma(i)=w-f_i and f_sigma(j)=w-f_j"
            ),
            "conjugate_identity": (
                "cbar+f_sigma(i)+f_sigma(j)="
                "-c+(w-f_i)+(w-f_j)=w"
            ),
            "conclusion": (
                "some complementary-family conjugate portal is selector-allowed; "
                "the theorem does not assert that its Wilson coefficient is nonzero"
            ),
        },
        "extension_to_products": (
            "a nonzero determinant term of the combined Yukawa support supplies the "
            "same sigma in every Abelian factor, so the identity holds factor by factor"
        ),
        "family_dependent_scan": {
            "families": 3,
            "selector_types": ["ordinary", "R"],
            "moduli": [2, 24],
            "charge_assignment_count": total_charge_assignments,
            "structurally_full_rank_assignment_count": total_full_rank_assignments,
            "wanted_portal_case_count": total_wanted_portal_cases,
            "counterexample_count": len(counterexamples),
            "counterexamples": counterexamples,
            "sample_determinant_witnesses": sample_witnesses,
            "by_type": by_type,
        },
        "result": (
            "NO_SCOPED_FAMILY_DEPENDENT_UNIFIED_ABELIAN_SELECTOR_CAN_FORBID_"
            "ALL_CONJUGATE_PORTALS"
        ),
        "escape_classes_not_excluded": [
            "a nonzero Higgs selector charge or changed Yukawa architecture",
            "a direct superpotential mass or charged mass spurion instead of a GM-neutral bilinear",
            "a selector that acts only after unified multiplets are split",
            "a non-Abelian or topological/space-group rule",
            "a texture mechanism that sets a selector-allowed Wilson coefficient to zero",
            "abandoning the current local unified-family architecture",
        ],
    }


def _b3_field_data(charges: Mapping[str, int]) -> dict[str, tuple[int, int, int, int, int]]:
    """Return d3,d2,6Y,Z_N,generations for the IR chiral spectrum."""

    return {
        "Q": (3, 2, 1, charges["Q"], 3),
        "Uc": (3, 1, -4, charges["Uc"], 3),
        "Dc": (3, 1, 2, charges["Dc"], 3),
        "L": (1, 2, -3, charges["L"], 3),
        "Ec": (1, 1, 6, charges["Ec"], 3),
        "Nc": (1, 1, 0, charges["Nc"], 3),
        "Hu": (1, 2, 3, charges["Hu"], 1),
        "Hd": (1, 2, -3, charges["Hd"], 1),
        "QX": (3, 2, 1, charges["QX"], 1),
        "QbarX": (3, 2, -1, charges["QbarX"], 1),
        "UcX": (3, 1, -4, charges["UcX"], 1),
        "UX": (3, 1, 4, charges["UX"], 1),
        "EcX": (1, 1, 6, charges["EcX"], 1),
        "EX": (1, 1, -6, charges["EX"], 1),
    }


def discrete_anomaly_sums(charges: Mapping[str, int]) -> dict[str, int]:
    sums = {
        "A3_2T": 0,
        "A2_2T": 0,
        "Agrav": 0,
        "AYY_6Y_integer": 0,
        "AYZZ_6Y_integer": 0,
        "AZZZ": 0,
    }
    for d3, d2, y6, z, generations in _b3_field_data(charges).values():
        sums["A3_2T"] += generations * z * d2 * int(d3 == 3)
        sums["A2_2T"] += generations * z * d3 * int(d2 == 2)
        sums["Agrav"] += generations * z * d3 * d2
        sums["AYY_6Y_integer"] += generations * z * d3 * d2 * y6 * y6
        sums["AYZZ_6Y_integer"] += generations * z * z * d3 * d2 * y6
        sums["AZZZ"] += generations * z**3 * d3 * d2
    return sums


def _operator_charge(charges: Mapping[str, int], names: tuple[str, ...], n: int) -> int:
    return sum(charges[name] for name in names) % n


def _derived_b3_like_charges(n: int, q: int, ell: int, hu: int) -> dict[str, int]:
    hd = (-hu) % n
    uc = (-q - hu) % n
    dc = (-q - hd) % n
    ec = (-ell - hd) % n
    nc = (-ell - hu) % n
    qx = (-dc - ell) % n
    ucx = (-2 * dc) % n
    ecx = (-2 * ell) % n
    return {
        "Q": q,
        "Uc": uc,
        "Dc": dc,
        "L": ell,
        "Ec": ec,
        "Nc": nc,
        "Hu": hu,
        "Hd": hd,
        "QX": qx,
        "UcX": ucx,
        "EcX": ecx,
        "QbarX": (-qx) % n,
        "UX": (-ucx) % n,
        "EX": (-ecx) % n,
    }


def minimal_b3_scan() -> dict[str, Any]:
    """Finite, deliberately scoped scan of the stated charge ansatz.

    The extra purely-Abelian congruences are a strong representative filter,
    not universal low-energy discrete-anomaly conditions.  For N=3 we also
    impose the integer-parent cubic condition AZZZ=0 mod 9.
    """

    counts: dict[str, int] = {}
    solutions: dict[str, list[list[int]]] = {}
    for n in range(2, 13):
        rows: list[list[int]] = []
        for q, ell, hu in itertools.product(range(n), repeat=3):
            charges = _derived_b3_like_charges(n, q, ell, hu)
            if 2 * charges["Nc"] % n:
                continue
            if _operator_charge(charges, ("UX", "Uc", "Nc"), n) == 0:
                continue
            if _operator_charge(charges, ("Uc", "Dc", "Dc"), n) == 0:
                continue
            anomalies = discrete_anomaly_sums(charges)
            if any(value % n for value in anomalies.values()):
                continue
            if n == 3 and anomalies["AZZZ"] % 9:
                continue
            rows.append([q, ell, hu])
        counts[str(n)] = len(rows)
        if rows:
            solutions[str(n)] = rows
    nonzero = [int(n) for n, count in counts.items() if count]
    minimum = min(nonzero)
    minimum_rows = solutions[str(minimum)]
    b3_base = (0, 2, 1)
    b3_equivalence_orbit = sorted(
        {
            (
                (sign * b3_base[0] + hypercharge_shift) % 3,
                (sign * b3_base[1]) % 3,
                (sign * b3_base[2]) % 3,
            )
            for sign in (1, -1)
            for hypercharge_shift in range(3)
        }
    )
    return {
        "scan_moduli": [2, 12],
        "scope": (
            "family-universal MSSM charges derived from (q,l,hu), the displayed "
            "T66 companion charges, required masses/Yukawas/lambda portals, forbidden "
            "rho_U and UDD, and the explicitly stated strong congruence filter"
        ),
        "not_a_complete_discrete_symmetry_classification": True,
        "strong_representative_filter": (
            "all six displayed integer sums vanish mod N; for N=3 AZZZ also "
            "vanishes mod 9"
        ),
        "solution_counts": counts,
        "minimal_modulus_within_scan": minimum,
        "minimal_raw_solutions_q_l_hu": minimum_rows,
        "N3_equivalence_orbit_q_l_hu": [list(row) for row in b3_equivalence_orbit],
        "N3_orbit_equals_all_minimal_rows": sorted(map(tuple, minimum_rows))
        == b3_equivalence_orbit,
        "minimal_class_within_scan": (
            "standard Z3 baryon triality, one class within this ansatz up to inversion "
            "and an integer-hypercharge redefinition"
        ),
    }


def b3_escape_audit() -> dict[str, Any]:
    n = 3
    charges = {
        "Q": 0,
        "Uc": 2,
        "Dc": 1,
        "L": 2,
        "Ec": 2,
        "Nc": 0,
        "Hu": 1,
        "Hd": 2,
        "QX": 0,
        "UcX": 1,
        "EcX": 2,
        "QbarX": 0,
        "UX": 2,
        "EX": 1,
    }
    operators = {
        "M_Q_QX_QbarX": ("QX", "QbarX"),
        "M_U_UcX_UX": ("UcX", "UX"),
        "M_E_EcX_EX": ("EcX", "EX"),
        "lambda_QX_Dc_L": ("QX", "Dc", "L"),
        "lambda_UcX_Dc_Dc": ("UcX", "Dc", "Dc"),
        "lambda_EcX_L_L": ("EcX", "L", "L"),
        "rho_QbarX_Q_Nc": ("QbarX", "Q", "Nc"),
        "rho_UX_Uc_Nc": ("UX", "Uc", "Nc"),
        "rho_EX_Ec_Nc": ("EX", "Ec", "Nc"),
        "Y_u": ("Q", "Uc", "Hu"),
        "Y_d": ("Q", "Dc", "Hd"),
        "Y_e": ("L", "Ec", "Hd"),
        "Y_nu": ("L", "Nc", "Hu"),
        "mu": ("Hu", "Hd"),
        "Majorana_NcNc": ("Nc", "Nc"),
        "MSSM_UDD": ("Uc", "Dc", "Dc"),
        "MSSM_LLE": ("L", "L", "Ec"),
        "MSSM_LQD": ("L", "Q", "Dc"),
        "QQQL": ("Q", "Q", "Q", "L"),
        "UUDE": ("Uc", "Uc", "Dc", "Ec"),
    }
    operator_charges = {
        name: _operator_charge(charges, fields, n) for name, fields in operators.items()
    }
    anomalies = discrete_anomaly_sums(charges)
    return {
        "name": "Z3 baryon triality B3",
        "scope": "four-dimensional SM-effective zero-mode spectrum only",
        "modulus": n,
        "charges": charges,
        "operator_charges_mod3": operator_charges,
        "allowed_operator_charge": 0,
        "wanted_and_safe_checks": {
            "all_vectorlike_masses_allowed": all(
                operator_charges[name] == 0
                for name in ("M_Q_QX_QbarX", "M_U_UcX_UX", "M_E_EcX_EX")
            ),
            "all_lambda_portals_allowed": all(
                operator_charges[name] == 0
                for name in ("lambda_QX_Dc_L", "lambda_UcX_Dc_Dc", "lambda_EcX_L_L")
            ),
            "Qbar_and_Ebar_portals_allowed": all(
                operator_charges[name] == 0
                for name in ("rho_QbarX_Q_Nc", "rho_EX_Ec_Nc")
            ),
            "dangerous_Ubar_portal_forbidden": operator_charges["rho_UX_Uc_Nc"] != 0,
            "MSSM_Yukawa_mu_and_Majorana_allowed": all(
                operator_charges[name] == 0
                for name in ("Y_u", "Y_d", "Y_e", "Y_nu", "mu", "Majorana_NcNc")
            ),
            "DeltaB1_superpotential_classes_forbidden": all(
                operator_charges[name] != 0 for name in ("MSSM_UDD", "QQQL", "UUDE")
            ),
        },
        "integer_anomaly_normalization": {
            "nonabelian": "2T(fundamental)=1",
            "hypercharge": "integer 6Y",
            "odd_N_linear_condition": (
                "A3_2T, A2_2T and Agrav vanish mod 3 in this normalization"
            ),
        },
        "anomaly_sums": anomalies,
        "standard_discrete_anomaly_checks": {
            "linear_residues_mod3": {
                key: anomalies[key] % 3 for key in ("A3_2T", "A2_2T", "Agrav")
            },
            "integer_parent_cubic_AZZZ_residue_mod9": anomalies["AZZZ"] % 9,
            "integer_parent_cubic_condition": (
                "for the Z3 integer-charge parent used in the standard B3 "
                "classification, AZZZ must be a multiple of 9"
            ),
            "pass": all(
                anomalies[key] % 3 == 0 for key in ("A3_2T", "A2_2T", "Agrav")
            )
            and anomalies["AZZZ"] % 9 == 0,
        },
        "extra_representative_abelian_congruences": {
            "not_universal_low_energy_constraints": True,
            "reason": (
                "YYZ and YZZ depend on U(1) normalization and the heavy charged "
                "sector; their displayed mod-3 zeros are additional ledger checks, "
                "not the basis of the B3 anomaly claim"
            ),
            "residues_mod3": {
                key: anomalies[key] % 3
                for key in ("AYY_6Y_integer", "AYZZ_6Y_integer")
            },
        },
        "known_class_and_exotic_extension": {
            "MSSM_class": (
                "the charges are the standard family-universal B3 class up to "
                "inversion and an integer-hypercharge shift"
            ),
            "T66_pairs": ["(QX,QbarX)=(0,0)", "(UcX,UX)=(1,2)", "(EcX,EX)=(2,1)"],
            "pair_statement": (
                "each exotic pair has a Z3-neutral mass and shifts the linear "
                "conditions by multiples of 3 and AZZZ by multiples of 9"
            ),
        },
        "symmetry_stack": {
            "B3_role": "additional conditional ordinary Z3 selector",
            "retained_inherited_remnant": "Z4R -> Z2 matter parity",
            "B3_alone_allows": ["L L Ec", "L Q Dc"],
            "operator_charges_mod3": {
                "MSSM_LLE": operator_charges["MSSM_LLE"],
                "MSSM_LQD": operator_charges["MSSM_LQD"],
            },
            "matter_parity_role": (
                "the retained Z2, not B3 alone, forbids these odd-matter "
                "lepton-number-violating superpotential terms"
            ),
            "B3_is_not_a_replacement_for_matter_parity": True,
        },
        "minimality_scan": minimal_b3_scan(),
        "current_action_compatibility": {
            "accepted": False,
            "reason": (
                "B3 gives different charges to components of a Spin(10)/Pati-Salam "
                "multiplet and therefore cannot simply be imposed on either existing wall"
            ),
            "required_new_physics": (
                "an explicit local orbifold/VEV, non-Abelian, or topological embedding "
                "with complete wall anomalies, GS quantization and Dai-Freed phase"
            ),
            "IR_anomaly_pass_is_not_a_5D_embedding": True,
        },
        "classification": "CONDITIONAL_IR_ESCAPE_ONLY",
    }


def _gauge_proxy_lifetime(m_x_gev: float, alpha_inverse: float) -> float:
    p = PROTON_PROXY
    alpha = 1.0 / alpha_inverse
    flavour = 1.0 + (1.0 + p["V_ud"] ** 2) ** 2
    coefficient = 4.0 * math.pi * alpha / m_x_gev**2
    width = (
        p["m_p_GeV"]
        / (32.0 * math.pi)
        * (1.0 - (p["m_pi0_GeV"] / p["m_p_GeV"]) ** 2) ** 2
        * coefficient**2
        * p["A_R"] ** 2
        * p["hadronic_W_GeV2"] ** 2
        * flavour
    )
    return p["hbar_GeV_s"] / width / p["seconds_per_year"]


def _proxy_row(branch: str, point: Mapping[str, float]) -> dict[str, Any]:
    mg = float(point["MG"])
    alpha_inverse = float(point["alphaU_inverse"])
    lifetime = _gauge_proxy_lifetime(mg, alpha_inverse)
    limit = PROTON_PROXY["limit_years_90CL"]
    required_ratio = (limit / lifetime) ** 0.25
    return {
        "branch": branch,
        "conditional_identification": "M_X=MG and alpha_X=alphaU",
        "MG_GeV": mg,
        "alphaU_inverse": alpha_inverse,
        "central_proxy_lifetime_years": lifetime,
        "repository_frozen_limit_years": limit,
        "lifetime_over_limit": lifetime / limit,
        "required_MX_over_MG": required_ratio,
        "required_MX_GeV": mg * required_ratio,
        "central_proxy_passes": lifetime >= limit,
        "branch_globally_decided": False,
    }


def dimension_six_proxy_matrix(route: Mapping[str, Any]) -> dict[str, Any]:
    two = route["two_loop_gauge_only_diagnostics"]
    h = _proxy_row(
        "H66",
        two["orphan_only_universal_MSbar_to_DRbar"]["computed"],
    )
    t = _proxy_row("T66", two["full_ten_raw_no_matching"]["computed"])
    h["scoped_decision"] = (
        "CENTRAL_PROXY_FAIL: M_X=MG is below the frozen single-channel limit; "
        "H66 itself is not rejected without its physical KK/vector spectrum"
    )
    t["scoped_decision"] = (
        "CENTRAL_PROXY_PASS_ONLY: no G7 promotion because M_X, KK sums, flavour, "
        "matrix elements and the T66 dimension-five portal are unresolved"
    )
    return {
        "formula": (
            "Gamma=m_p/(32 pi) [1-(m_pi/m_p)^2]^2 "
            "[4 pi alpha_X/M_X^2]^2 A_R^2 W^2 "
            "{1+[1+|V_ud|^2]^2}; tau=hbar/Gamma"
        ),
        "constants": dict(PROTON_PROXY),
        "source_scope": (
            "repository-frozen conditional p->e+pi0 width proxy; not a current "
            "all-channel likelihood and not a model-derived lifetime"
        ),
        "rows": [h, t],
        "scaling_identity": "tau(lambda M_X)=lambda^4 tau(M_X)",
        "claim_boundary": "NO_LIFETIME_PREDICTION",
    }


def dimension_five_conditional_bound(
    route: Mapping[str, Any], v55: Mapping[str, Any]
) -> dict[str, Any]:
    tpoint = route["two_loop_gauge_only_diagnostics"]["full_ten_raw_no_matching"][
        "computed"
    ]
    m10 = float(tpoint["MS"])
    comparison = v55["comparison_contract"]
    tau_limit = float(v55["experimental_input"]["partial_lifetime_lower_limit_yr_90CL"])
    tau0 = float(comparison["reference_lifetime_yr"])
    meff0 = float(comparison["reference_Meff_GeV"])
    msq0 = float(comparison["reference_msquark_TeV"])
    mwino0 = float(comparison["reference_mwino_GeV"])
    msq = m10 / 1000.0
    mwino = m10
    spectrum_factor = (msq / msq0) ** 4 * (mwino0 / mwino) ** 2
    required_meff = meff0 * math.sqrt(tau_limit / (tau0 * spectrum_factor))
    maximum_product = m10 / required_meff
    return {
        "operator_after_heavy_N_and_EWSB": (
            "C5_{ijkr} uc_k dc_i dc_j nu_r with C5_{ijkr}="
            "+(lambda_ij/(2 M10)) sum_l rho_{k l} theta_{l r} in the "
            "ordered-family convention"
        ),
        "theta_N": (
            "theta_{l r}=sum_m (M_N^-1)_{l m} (y_nu)_{r m} v_u; "
            "the matrix-index convention is fixed in the Schur section"
        ),
        "effective_scale": "M_eff=M10/abs(lambda rho theta_N D_flavour)",
        "comparison_contract": (
            "repository-frozen V55 p->anti-nu K+ scaling only; channel, flavour, "
            "dressing and spectrum are not a T66 calculation"
        ),
        "illustrative_common_T66_threshold": {
            "M10_GeV": m10,
            "m_squark_TeV": msq,
            "m_wino_GeV": mwino,
            "spectrum_factor": spectrum_factor,
            "required_Meff_GeV": required_meff,
            "maximum_abs_lambda_rho_thetaN_D": maximum_product,
        },
        "testable_condition": (
            "abs(lambda rho theta_N D_flavour) < M10/M_required"
        ),
        "O1_unprotected_portals_pass_comparison": False,
        "protection_routes": [
            "forbid rho_U exactly with an action-compatible selector",
            "derive sufficient flavour/seesaw suppression in the same action",
            "raise the physical companion mass while redoing unification and thresholds",
        ],
        "claim_boundary": "CONDITIONAL_FEASIBILITY_BOUND_NOT_A_LIFETIME",
    }


def gate_closability_ranking() -> list[dict[str, Any]]:
    rows = [
        ("G7", "proton/baryon", "exact selectors and proxy inputs exist; full matching remains"),
        ("G4", "protected hierarchy", "projector exact, but V64 null pair and GM coefficient block"),
        ("G5", "LSP/exotic phenomenology", "R parity exact; mass, lifetime, relic and collider calculations absent"),
        ("G2", "coefficient action/flavour/soft", "broad Wilsonian action and KK determinant reconstruction required"),
        ("G3", "vacuum/compactification", "hidden vacuum, saxion and full Hessian absent"),
        ("G6", "cosmological history", "inflation, reheating, defects and moduli history absent"),
        ("G8", "UV/global quantum completion", "UV regulator, Dai-Freed phase and predictivity score absent"),
    ]
    return [
        {"rank": rank, "gate": gate, "topic": topic, "reason": reason, "status": "OPEN"}
        for rank, (gate, topic, reason) in enumerate(rows, start=1)
    ]


def source_manifest() -> list[dict[str, Any]]:
    paths = [
        Path(__file__),
        TEST_PATH,
        ROUTE_PATH,
        MASTER_PATH,
        V55_PATH,
        PROTON_SOURCE_PATH,
        FLAVOUR_SOURCE_PATH,
        SCALAR_SOURCE_PATH,
    ]
    return [
        {"path": path.name, "exists": path.is_file(), "raw_sha256": file_sha(path)}
        for path in paths
    ]


def primary_sources(v55: Mapping[str, Any]) -> list[dict[str, Any]]:
    inherited = [
        {
            "title": row["title"],
            "url": row["url"],
            "scope": "inherited through the exact V55 comparison core",
        }
        for row in v55["primary_sources"]
    ]
    return [
        {
            "title": "What is the Discrete Gauge Symmetry of the MSSM?",
            "url": "https://arxiv.org/abs/hep-ph/0512163",
            "scope": (
                "family-independent B3 classification, linear anomaly conditions, "
                "purely-Abelian caveats and the integer-parent cubic condition"
            ),
        },
        {
            "title": (
                "Search for proton decay via p to e+ pi0 and p to mu+ pi0 with "
                "an enlarged fiducial volume in Super-Kamiokande I-IV"
            ),
            "url": "https://arxiv.org/abs/2010.16098",
            "scope": "p to e+ pi0 lower limit used by the frozen gauge proxy",
        },
        *inherited,
    ]


def _integrity_checks(report: Mapping[str, Any]) -> dict[str, bool]:
    portal = report["t66_u_portal_schur_complement"]
    selector = report["unified_selector_one_sided_no_go"]
    b3 = report["conditional_b3_ir_escape"]
    standard_anomalies = b3["standard_discrete_anomaly_checks"]
    proxies = {row["branch"]: row for row in report["dimension_six_proton_proxy"]["rows"]}
    bound = report["dimension_five_portal_stress"]["illustrative_common_T66_threshold"]
    return {
        "V66_route_core_bound": report["lineage"]["V66_route"]["core_sha256"]
        == EXPECTED_V66_ROUTE_CORE,
        "V66_master_core_bound": report["lineage"]["V66_master"]["core_sha256"]
        == EXPECTED_V66_MASTER_CORE,
        "V55_comparison_core_bound": report["lineage"]["V55_proton_comparison"]["core_sha256"]
        == EXPECTED_V55_CORE,
        "frozen_proton_source_bound": report["lineage"]["frozen_proton_sources"][
            "proton_raw_sha256"
        ]
        == EXPECTED_PROTON_SOURCE_RAW,
        "frozen_flavour_source_bound": report["lineage"]["frozen_proton_sources"][
            "flavour_raw_sha256"
        ]
        == EXPECTED_FLAVOUR_SOURCE_RAW,
        "frozen_scalar_source_bound": report["lineage"]["frozen_proton_sources"][
            "scalar_raw_sha256"
        ]
        == EXPECTED_SCALAR_SOURCE_RAW,
        "Schur_inverse_exact": portal["matrix_times_inverse"] == [[1, 0], [0, 1]],
        "Schur_determinant_nonzero": portal["normalized_determinant"] == -1,
        "ordered_sum_half_convention_present": portal["family_convention"][
            "full_ordered_family_sum_prefactor"
        ]
        == "1/2",
        "DeltaB_DeltaL_exact": portal["global_numbers"]["Delta_B"] == -1
        and portal["global_numbers"]["Delta_L"] == -1
        and portal["global_numbers"]["Delta_B_minus_L"] == 0,
        "post_Majorana_numbers_exact": portal["heavy_N_matching"][
            "post_Majorana_field_numbers"
        ]["Delta_B"]
        == -1
        and portal["heavy_N_matching"]["post_Majorana_field_numbers"]["Delta_L"]
        == 1
        and portal["heavy_N_matching"]["post_Majorana_field_numbers"][
            "Delta_B_minus_L"
        ]
        == -2,
        "unified_selector_counterexamples_zero": selector["family_dependent_scan"][
            "counterexample_count"
        ]
        == 0,
        "unified_selector_family_dependent_cases_scanned": selector[
            "family_dependent_scan"
        ]["wanted_portal_case_count"]
        > 0,
        "B3_forbids_only_dangerous_conjugate_U_among_rho": b3[
            "operator_charges_mod3"
        ]["rho_UX_Uc_Nc"]
        != 0
        and b3["operator_charges_mod3"]["rho_QbarX_Q_Nc"] == 0
        and b3["operator_charges_mod3"]["rho_EX_Ec_Nc"] == 0,
        "B3_standard_linear_and_cubic_checks_pass": standard_anomalies["pass"] is True
        and standard_anomalies["integer_parent_cubic_AZZZ_residue_mod9"] == 0,
        "B3_extra_U1_ledger_residues_zero": all(
            value == 0
            for value in b3["extra_representative_abelian_congruences"][
                "residues_mod3"
            ].values()
        ),
        "B3_is_minimal_in_scoped_scan": b3["minimality_scan"][
            "minimal_modulus_within_scan"
        ]
        == 3
        and b3["minimality_scan"]["solution_counts"]["2"] == 0,
        "B3_N3_equivalence_orbit_exact": b3["minimality_scan"][
            "N3_orbit_equals_all_minimal_rows"
        ]
        is True,
        "B3_supplements_retained_matter_parity": b3["symmetry_stack"][
            "B3_is_not_a_replacement_for_matter_parity"
        ]
        is True
        and all(
            value == 0
            for value in b3["symmetry_stack"]["operator_charges_mod3"].values()
        ),
        "B3_not_promoted_to_5D_action": b3["current_action_compatibility"]["accepted"] is False,
        "T66_dim5_product_bound_is_tiny": math.isclose(
            bound["maximum_abs_lambda_rho_thetaN_D"],
            2.521534213303378e-16,
            rel_tol=2e-12,
        ),
        "H66_proxy_central_fails": proxies["H66"]["central_proxy_passes"] is False
        and math.isclose(
            proxies["H66"]["required_MX_over_MG"], 1.980571509992, rel_tol=2e-12
        ),
        "T66_proxy_central_passes": proxies["T66"]["central_proxy_passes"] is True
        and math.isclose(
            proxies["T66"]["required_MX_over_MG"], 0.6392872608832292, rel_tol=2e-12
        ),
        "all_ranked_gates_remain_open": all(
            row["status"] == "OPEN" for row in report["G2_G8_closability_ranking"]
        ),
        "fail_closed_terminal_decision": report["terminal_decision"] == {
            "current_Spin11_action_status": "REJECTED",
            "H66_status": "CANDIDATE_ONLY__CENTRAL_GAUGE_PROXY_FAIL",
            "T66_status": "CANDIDATE_ONLY__UNPROTECTED_PORTAL_NOT_ACCEPTED",
            "B3_status": "IR_ESCAPE_ONLY__NEW_EMBEDDING_REQUIRED",
            "G7_closed": False,
            "closed_gates": [],
            "complete_theory": False,
        },
    }


def build_report() -> dict[str, Any]:
    route = _load_bound(ROUTE_PATH, EXPECTED_V66_ROUTE_CORE, "V66 route")
    master = _load_bound(MASTER_PATH, EXPECTED_V66_MASTER_CORE, "V66 master")
    v55 = _load_bound(V55_PATH, EXPECTED_V55_CORE, "V55 proton comparison")
    _require_raw(PROTON_SOURCE_PATH, EXPECTED_PROTON_SOURCE_RAW, "proton proxy")
    _require_raw(FLAVOUR_SOURCE_PATH, EXPECTED_FLAVOUR_SOURCE_RAW, "flavour proxy")
    _require_raw(SCALAR_SOURCE_PATH, EXPECTED_SCALAR_SOURCE_RAW, "scalar gauge proxy")

    master_gates = master["gate_ledger"]
    if any(row["status"] != "OPEN" for row in master_gates):
        raise RuntimeError("V66 master no longer has a fully open G1-G8 ledger")
    if route["terminal_decision"]["current_bound_action_status"] != "REJECTED":
        raise RuntimeError("V66 route current action is no longer rejected")

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": "V67",
        "date": "2026-08-30",
        "status": STATUS,
        "lineage": {
            "V66_route": {
                "path": ROUTE_PATH.name,
                "core_sha256": route["core_sha256"],
                "binding": "exact canonical core",
            },
            "V66_master": {
                "path": MASTER_PATH.name,
                "core_sha256": master["core_sha256"],
                "binding": "exact canonical core",
            },
            "V55_proton_comparison": {
                "path": V55_PATH.name,
                "core_sha256": v55["core_sha256"],
                "binding": "exact canonical core; scaling comparison only",
            },
            "frozen_proton_sources": {
                "proton_path": PROTON_SOURCE_PATH.name,
                "proton_raw_sha256": file_sha(PROTON_SOURCE_PATH),
                "flavour_path": FLAVOUR_SOURCE_PATH.name,
                "flavour_raw_sha256": file_sha(FLAVOUR_SOURCE_PATH),
                "scalar_path": SCALAR_SOURCE_PATH.name,
                "scalar_raw_sha256": file_sha(SCALAR_SOURCE_PATH),
            },
            "supersession": (
                "route-local V67 stress audit only; V66 is not edited and no "
                "cross-route evidence is spliced"
            ),
        },
        "t66_u_portal_schur_complement": portal_schur_complement(),
        "unified_selector_one_sided_no_go": unified_selector_no_go(),
        "conditional_b3_ir_escape": b3_escape_audit(),
        "dimension_five_portal_stress": dimension_five_conditional_bound(route, v55),
        "dimension_six_proton_proxy": dimension_six_proxy_matrix(route),
        "G2_G8_closability_ranking": gate_closability_ranking(),
        "same_action_dependencies": [
            "physical X/Y and complete KK vector pole spectrum with Mc, brane kinetic terms and wavefunctions",
            "mass-basis lambda, rho and neutrino tensors with their covariance",
            "SUSY dressing, operator running and channel-specific lattice matrix elements",
            "a local/topological realization of any component-splitting selector",
            "full localized anomaly/GS and relative Dai-Freed recomputation",
            "soft spectrum, finite thresholds and a quantified truncation error",
        ],
        "gate_decision": {
            "gate": "G7",
            "status": "OPEN_WITH_MATERIAL_ADVANCE",
            "advance": (
                "the displayed T66 U-channel pre-Majorana DeltaB=DeltaL=-1 "
                "Schur operator, the scoped family-dependent unified-selector "
                "no-go, a conditional IR B3 escape within the stated ansatz, and "
                "H66/T66 gauge-proxy conditions are now exact"
            ),
            "why_not_closed": (
                "neither a physical lifetime nor an action-compatible B3 embedding "
                "and same-action Wilson/pole calculation exists"
            ),
            "V67_master_gate_promotion": False,
        },
        "terminal_decision": {
            "current_Spin11_action_status": "REJECTED",
            "H66_status": "CANDIDATE_ONLY__CENTRAL_GAUGE_PROXY_FAIL",
            "T66_status": "CANDIDATE_ONLY__UNPROTECTED_PORTAL_NOT_ACCEPTED",
            "B3_status": "IR_ESCAPE_ONLY__NEW_EMBEDDING_REQUIRED",
            "G7_closed": False,
            "closed_gates": [],
            "complete_theory": False,
        },
        "claim_boundary": {
            "new_empirical_discovery": False,
            "proton_lifetime_predicted": False,
            "current_action_accepted": False,
            "B3_embedded_in_5D": False,
            "any_gate_closed": False,
            "conditional_diagnostics_only": True,
        },
        "primary_sources": primary_sources(v55),
        "source_manifest": source_manifest(),
    }
    checks = _integrity_checks(report)
    report["integrity_checks"] = checks
    report["n_integrity_checks"] = len(checks)
    report["n_failed_integrity_checks"] = sum(not value for value in checks.values())
    if report["n_failed_integrity_checks"]:
        failed = [key for key, value in checks.items() if not value]
        raise RuntimeError(f"V67 integrity checks failed: {failed}")
    report["core_sha256"] = canonical_sha(report)
    return report


def validate_report(report: Mapping[str, Any]) -> None:
    observed_core = report.get("core_sha256")
    if observed_core != canonical_sha(report):
        raise RuntimeError("V67 canonical core mismatch")
    expected = build_report()
    if canonical_bytes(report) != canonical_bytes(expected):
        raise RuntimeError("V67 report differs from independent live recomputation")


def render_markdown(report: Mapping[str, Any]) -> str:
    portal = report["t66_u_portal_schur_complement"]
    selector = report["unified_selector_one_sided_no_go"]
    b3 = report["conditional_b3_ir_escape"]
    bound = report["dimension_five_portal_stress"]["illustrative_common_T66_threshold"]
    proxies = {row["branch"]: row for row in report["dimension_six_proton_proxy"]["rows"]}
    ranking = "\n".join(
        f"| {row['rank']} | {row['gate']} | {row['topic']} | {row['reason']} |"
        for row in report["G2_G8_closability_ranking"]
    )
    anomaly_rows = "\n".join(
        f"| {name} | {value} | "
        + (
            f"{value % 9} mod 9 | standard integer-parent cubic |"
            if name == "AZZZ"
            else (
                f"{value % 3} mod 3 | standard linear |"
                if name in ("A3_2T", "A2_2T", "Agrav")
                else f"{value % 3} mod 3 | extra representative U(1) ledger only |"
            )
        )
        for name, value in sorted(b3["anomaly_sums"].items())
    )
    source_rows = "\n".join(
        f"- [{row['title']}]({row['url']}): {row['scope']}"
        for row in report["primary_sources"]
    )
    h, t = proxies["H66"], proxies["T66"]
    return f"""# SUSY V67 Spin(11) T66 baryon/proton stress audit

Status: `{report['status']}`

Canonical core: `{report['core_sha256']}`

## Decision

G7 receives a material exact advance but remains **OPEN**.  The displayed T66
conjugate up-type portal generates a baryon-violating Schur operator.  Under
the assumptions stated below, no family-dependent Abelian selector commuting
with the unified multiplets can allow the wanted portal and GM-neutral mass
while symmetry-forbidding every conjugate portal.  A conditional IR `Z3`
baryon-triality assignment passes the standard linear and integer-parent cubic
checks, but it splits Spin(10)/Pati-Salam multiplets and is therefore not a
repair of the current 5D action.

The current Spin(11) action remains **REJECTED**.  H66 and T66 remain candidate
extensions only.  No proton lifetime is predicted and no gate is promoted.

## Bound lineage

- V66 route core: `{report['lineage']['V66_route']['core_sha256']}`
- V66 master core: `{report['lineage']['V66_master']['core_sha256']}`
- V55 comparison core: `{report['lineage']['V55_proton_comparison']['core_sha256']}`

## Exact T66 up-type Schur complement

`{portal['superpotential']}`

With `A=(1/2) lambda_ij epsilon dc_i dc_j`, `B=rho_kl uc_k Nc_l`, and
`lambda_ij=-lambda_ji`, the exact elimination is

`{portal['schur_identity']}`,

hence

`{portal['effective_superpotential_ordered_sum']}`.

Before Majorana-neutrino matching it carries
`Delta B={portal['global_numbers']['Delta_B']}` and
`Delta L={portal['global_numbers']['Delta_L']}`, while conserving `B-L`.
The fixed tensor convention is
`{portal['heavy_N_matching']['mixing_tensor']}`.  After eliminating `Nc` and
inserting `v_u`, `{portal['heavy_N_matching']['after_EWSB']}`.  The resulting
`uc dc dc L Hu` field monomial instead has `Delta B=-1`, `Delta L=+1` and
`Delta(B-L)=-2`; the Majorana insertion supplies the two-unit change.

## Unified-selector no-go

Family charges may differ.  Structural full rank supplies a determinant
permutation `sigma` with `f_i+f_sigma(i)=w`.  If `C F_i F_j` is allowed, then
`c=w-f_i-f_j`; GM neutrality gives `cbar=-c`.  The complementary pair obeys

`cbar+f_sigma(i)+f_sigma(j)=-c+(w-f_i)+(w-f_j)=w`.

Thus at least one conjugate portal is selector-allowed.  This does not prove
that its Wilson coefficient is nonzero.  The executable scan covers arbitrary
three-family charges for ordinary and R selectors with `2 <= N <= 24`:
{selector['family_dependent_scan']['charge_assignment_count']} charge assignments,
{selector['family_dependent_scan']['structurally_full_rank_assignment_count']} structurally
full-rank assignments and {selector['family_dependent_scan']['wanted_portal_case_count']}
wanted-portal cases, with {selector['family_dependent_scan']['counterexample_count']}
counterexamples.  A common determinant permutation makes the proof factorwise
for products.  Nonzero Higgs charge, direct/charged-spurion masses, split
multiplets, non-Abelian/topological rules and texture zeros remain outside the
theorem.

## Conditional IR baryon triality

One representative charge order is

`[Q,Uc,Dc,L,Ec,Nc,Hu,Hd]=[0,2,1,2,2,0,1,2] mod 3`,

with

`[QX,UcX,EcX,QbarX,UX,EX]=[0,1,2,0,2,1] mod 3`.

This keeps all vectorlike masses, MSSM Yukawas, `mu`, `Nc Nc`, the three
`lambda` portals and the Qbar/Ebar `rho` portals, while forbidding `UX Uc Nc`
and the displayed `Delta B=1` superpotential classes.

| Anomaly numerator | Value | Residue | Role |
|---|---:|---:|---|
{anomaly_rows}

The standard linear residues vanish mod 3 and `AZZZ={b3['anomaly_sums']['AZZZ']}`
vanishes mod 9, as required for the integer-charge parent used in the standard
B3 classification.  The `YYZ` and `YZZ` rows are extra representative-
normalization checks, not universal low-energy anomaly constraints.  Within
the explicitly stated finite charge/portal ansatz, the scan finds no `Z2`
solution and one `Z3` B3 orbit up to inversion and an integer-hypercharge shift;
it is not a universal discrete-symmetry classification.

B3 is an additional conditional selector, not a replacement for the inherited
`Z4R -> Z2` matter parity.  B3 alone allows `L L Ec` and `L Q Dc`; the retained
matter parity is what forbids those odd-matter terms.  This remains an **IR
escape only**: it cannot simply be placed on either existing unified wall.  A
new local/topological embedding, wall anomaly/GS ledger and Dai-Freed
computation are mandatory.

## Conditional dimension-five stress

Using only the repository-frozen V55 scaling comparison at the illustrative
common T66 threshold gives

- `M10 = {bound['M10_GeV']:.9e} GeV`;
- required `M_eff > {bound['required_Meff_GeV']:.9e} GeV`;
- `|lambda rho theta_N D_flavour| < {bound['maximum_abs_lambda_rho_thetaN_D']:.9e}`.

This is a feasibility bound, not a T66 lifetime calculation.  An order-one
unprotected portal fails this comparison by many orders of magnitude.

## H66/T66 dimension-six proxy matrix

The frozen conditional identification is `M_X=MG`, `alpha_X=alphaU`.

| Branch | Proxy tau (yr) | tau/limit | Required M_X/MG | Scoped result |
|---|---:|---:|---:|---|
| H66 | {h['central_proxy_lifetime_years']:.9e} | {h['lifetime_over_limit']:.6g} | {h['required_MX_over_MG']:.9f} | central proxy fails; branch not globally rejected |
| T66 | {t['central_proxy_lifetime_years']:.9e} | {t['lifetime_over_limit']:.6g} | {t['required_MX_over_MG']:.9f} | central proxy passes; G7 not closed |

H66 therefore needs `M_X > {h['required_MX_GeV']:.9e} GeV` under the frozen
proxy.  T66 passes that one diagnostic if
`M_X > {t['required_MX_GeV']:.9e} GeV`, but its dimension-five exotic portal
remains the sharper obstruction.

## Primary sources

{source_rows}

## G2-G8 closability ranking

| Rank | Gate | Topic | Reason |
|---:|---|---|---|
{ranking}

## Fail-closed boundary

Still required in one action: the physical X/Y and KK pole spectrum, local B3
or alternative portal protection, localized/global anomaly completion,
mass-basis Wilson tensors, neutrino/flavour data, SUSY dressing and running,
channel-specific lattice inputs, and correlated uncertainties.  Consequently
G1-G8 remain open with zero promotions.
"""


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def check_outputs() -> dict[str, Any]:
    if not JSON_PATH.is_file() or not MD_PATH.is_file():
        raise RuntimeError("V67 output files are missing")
    report = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    validate_report(report)
    expected_md = render_markdown(report)
    if MD_PATH.read_text(encoding="utf-8") != expected_md:
        raise RuntimeError("V67 Markdown does not match the canonical report")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write JSON and Markdown")
    parser.add_argument("--check", action="store_true", help="validate persisted outputs")
    args = parser.parse_args()
    if args.check:
        report = check_outputs()
    else:
        report = build_report()
        if args.write:
            write_outputs(report)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
