#!/usr/bin/env python3
"""Executable V37 certificates for the next viable physics routes.

V37 is deliberately fail-closed.  It promotes the polynomial axion-quality
construction, records two stronger ultraviolet routes for G1, and rejects a
tempting four-dimensional matter repair once its first allowed higher-
dimensional operator is included.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
REPORT_JSON = ROOT / "SUSY_V37_NEW_PHYSICS_ROUTES.json"
REPORT_MD = ROOT / "SUSY_V37_NEW_PHYSICS_ROUTES.md"
QUALITY_JSON = ROOT / "SUSY_V37_G5_QUALITY_CERTIFICATE.json"
GATES_JSON = ROOT / "SUSY_V37_G1_G8_GATE_LEDGER.json"
RGE_JSON = ROOT / "SUSY_V37_SARAH_RGE_ATTESTATION.json"

MODEL_NAME = "PSZ4RZ5610SUSYV37"
N66 = 66
N85 = 85
N5610 = N66 * N85

SOURCE_FILES = (
    "susy_v37_new_physics_routes.py",
    "test_susy_v37_new_physics_routes.py",
    "tools/validate-susy-v37-new-physics.wls",
    "tools/derive-susy-v33-ps-rges.wls",
    "models/PSZ4RZ5610SUSYV37/PSZ4RZ5610SUSYV37.m",
    "models/PSZ4RZ5610SUSYV37/parameters.m",
    "models/PSZ4RZ5610SUSYV37/particles.m",
    "models/PSZ4RZ5610SUSYV37/README.md",
    "SUSY_V37_SARAH_RGE_ATTESTATION.json",
    ".github/workflows/susy-v37-new-physics.yml",
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_manifest() -> list[dict[str, Any]]:
    return [
        {
            "path": name,
            "exists": (ROOT / name).is_file(),
            "sha256": sha256_file(ROOT / name) if (ROOT / name).is_file() else None,
        }
        for name in SOURCE_FILES
    ]


def combined_charge(q66: int, h85: int) -> int:
    """Charge for the simultaneous generator of Z66 x Z85 ~= Z5610."""

    return (N85 * q66 + N66 * h85) % N5610


def hsieh_audit(order: int, rows: Sequence[Mapping[str, int]]) -> dict[str, Any]:
    linear = sum(row["multiplicity"] * row["charge"] for row in rows)
    cubic = sum(row["multiplicity"] * row["charge"] ** 3 for row in rows)
    coefficient = order * order + 3 * order + 2
    linear_residue = (2 * linear) % order
    cubic_residue = (coefficient * cubic) % (6 * order)
    return {
        "order": order,
        "Delta_s1_canonical": linear,
        "Delta_s3_canonical": cubic,
        "linear_condition_2Delta_s1_mod_n": linear_residue,
        "cubic_condition_mod_6n": cubic_residue,
        "both_vanish": linear_residue == 0 and cubic_residue == 0,
    }


# q66, external Z4R superfield charge, h85, and optimized PQ numerator / 170.
SINGLET_FIELDS: dict[str, tuple[int, int, int, int]] = {
    "X": (0, 2, 0, 0),
    "Zp": (0, 2, 0, 0),
    "P": (2, 2, 0, 170),
    "Pbar": (64, 2, 0, -170),
    "Nv": (0, 1, 0, 0),
    "A2": (37, 0, 1, -23),
    "A32": (31, 0, 84, 193),
    "A15": (63, 2, 69, -57),
    "A17": (1, 2, 16, -113),
    "A16": (65, 0, 0, -85),
}

# The same optimized accidental current on the complete chiral spectrum.
# Keeping this table separate from SINGLET_FIELDS lets the renormalizable
# census retain its precise gauge-singlet scope while the quality search can
# establish a stronger, gauge-contraction-independent lower bound.
ALL_CHIRAL_FIELDS: dict[str, tuple[int, int, int, int]] = {
    "H": (0, 0, 0, 0),
    "Q": (0, 1, 0, 0),
    "Qc": (0, 1, 0, 0),
    "X": (0, 2, 0, 0),
    "Sc": (0, 0, 0, 0),
    "Sbc": (0, 0, 0, 0),
    "Sig6": (0, 2, 0, 0),
    "PsiBar": (64, 3, 0, -170),
    "Psi": (0, 1, 0, 0),
    "PsiC": (0, 1, 0, 0),
    "PsiCBar": (64, 3, 0, -170),
    "P": (2, 2, 0, 170),
    "Nv": (0, 1, 0, 0),
    "Pbar": (64, 2, 0, -170),
    "Zp": (0, 2, 0, 0),
    "A2": (37, 0, 1, -23),
    "A32": (31, 0, 84, 193),
    "A15": (63, 2, 69, -57),
    "A17": (1, 2, 16, -113),
    "A16": (65, 0, 0, -85),
}


RETAINED_ANOMALON_TERMS = (
    ("Pbar", "A2", "A32"),
    ("P", "A15", "A17"),
    ("P", "A16", "A16"),
)

REMOVED_V36_TERMS = (
    ("Pbar", "A17", "A17"),
    ("A16", "A17"),
)


def term_charge(term: Iterable[str], position: int) -> int:
    return sum(SINGLET_FIELDS[name][position] for name in term)


def renormalizable_singlet_census() -> dict[str, Any]:
    names = tuple(SINGLET_FIELDS)
    name_order = {name: index for index, name in enumerate(names)}

    def canonical_term(term: Iterable[str]) -> tuple[str, ...]:
        return tuple(sorted(term, key=name_order.__getitem__))

    allowed: list[list[str]] = []
    for degree in (1, 2, 3):
        for term in itertools.combinations_with_replacement(names, degree):
            q5610 = sum(
                combined_charge(SINGLET_FIELDS[name][0], SINGLET_FIELDS[name][2])
                for name in term
            )
            if q5610 % N5610:
                continue
            if term_charge(term, 1) % 4 != 2:
                continue
            allowed.append(list(term))
    allowed_set = {tuple(term) for term in allowed}
    return {
        "scope": "all gauge-singlet monomials of superfield degree <=3",
        "allowed_count": len(allowed),
        "allowed": allowed,
        "all_preserve_optimized_PQ": all(
            term_charge(term, 3) == 0 for term in allowed
        ),
        "retained_anomalon_terms_present": all(
            canonical_term(term) in allowed_set for term in RETAINED_ANOMALON_TERMS
        ),
        "removed_v36_terms_forbidden": all(
            canonical_term(term) not in allowed_set for term in REMOVED_V36_TERMS
        ),
        "dangerous_P_A32_forbidden": canonical_term(("P", "A32")) not in allowed_set,
    }


def _state_space_first_breaking(
    kahler: bool,
    max_degree: int = 33,
    fields: Mapping[str, tuple[int, int, int, int]] = SINGLET_FIELDS,
) -> dict[str, Any]:
    base = [
        (
            name,
            combined_charge(q66, h85),
            r4,
            h85,
            pq170,
        )
        for name, (q66, r4, h85, pq170) in fields.items()
    ]
    # Species with identical exact/PQ charges are interchangeable for this
    # pre-gauge-invariance lattice search.  Deduplicating them changes only
    # the displayed witness name, not the first possible degree.
    unique_base: list[tuple[str, int, int, int, int]] = []
    seen_base: set[tuple[int, int, int, int]] = set()
    for item in base:
        signature = item[1:]
        if signature not in seen_base:
            seen_base.add(signature)
            unique_base.append(item)
    base = unique_base
    items = list(base)
    if kahler:
        items += [
            (
                f"{name}dag",
                (-q5610) % N5610,
                (-r4) % 4,
                (-h85) % N85,
                -pq170,
            )
            for name, q5610, r4, h85, pq170 in base
        ]

    states: dict[tuple[int, int, int, int], tuple[int, ...]] = {
        (0, 0, 0, 0): (0,) * len(items)
    }
    target_r = 0 if kahler else 2
    state_counts: list[int] = []
    for degree in range(1, max_degree + 1):
        next_states: dict[tuple[int, int, int, int], tuple[int, ...]] = {}
        for (q, r4, h85, pq170), counts in states.items():
            for index, (_, iq, ir4, ih85, ipq170) in enumerate(items):
                state = (
                    (q + iq) % N5610,
                    (r4 + ir4) % 4,
                    (h85 + ih85) % N85,
                    pq170 + ipq170,
                )
                if state not in next_states:
                    updated = list(counts)
                    updated[index] += 1
                    next_states[state] = tuple(updated)
        states = next_states
        state_counts.append(len(states))
        for (q, r4, h85, pq170), counts in states.items():
            if q == 0 and r4 == target_r and h85 == 0 and pq170 != 0:
                multiplicities = {
                    items[index][0]: count
                    for index, count in enumerate(counts)
                    if count
                }
                return {
                    "search_max_degree": max_degree,
                    "first_breaking_degree": degree,
                    "witness_multiplicities": multiplicities,
                    "witness_PQ_charge": f"{pq170}/170",
                    "reachable_state_counts": state_counts,
                }
    return {
        "search_max_degree": max_degree,
        "first_breaking_degree": None,
        "witness_multiplicities": None,
        "witness_PQ_charge": None,
        "reachable_state_counts": state_counts,
    }


def finite_quality_certificate() -> dict[str, Any]:
    rows66 = [
        ("PsiBar", 8, 64, 0),
        ("PsiCBar", 8, 64, 0),
        ("P", 1, 2, 0),
        ("Pbar", 1, 64, 0),
        ("A2", 1, 37, 1),
        ("A32", 1, 31, 84),
        ("A15", 1, 63, 69),
        ("A17", 1, 1, 16),
        ("A16", 1, 65, 0),
    ]
    rows5610 = [
        {
            "field": field,
            "multiplicity": multiplicity,
            "charge": combined_charge(q66, h85),
        }
        for field, multiplicity, q66, h85 in rows66
    ]
    h_signed = {"A2": 1, "A32": -1, "A15": 69, "A17": -69}
    r_fermion = {"A2": -1, "A32": -1, "A15": 1, "A17": 1}
    mixed_r_h2 = sum(r_fermion[name] * charge**2 for name, charge in h_signed.items())
    w_breaking = _state_space_first_breaking(kahler=False)
    k_breaking = _state_space_first_breaking(kahler=True)
    all_w_breaking = _state_space_first_breaking(
        kahler=False, fields=ALL_CHIRAL_FIELDS
    )
    all_k_breaking = _state_space_first_breaking(
        kahler=True, fields=ALL_CHIRAL_FIELDS
    )
    pq_congruence = {
        name: (
            pq170 - (N85 * q66 + 2442 * h85)
        ) % N5610
        for name, (q66, _r4, h85, pq170) in ALL_CHIRAL_FIELDS.items()
    }

    f_p = 5.0e11
    a_soft = 1.0e4
    m_reduced = 2.4e18
    chi_qcd = 0.0756**4
    degree = w_breaking["first_breaking_degree"]
    log_amplitude = (
        math.log10(2.0 * a_soft)
        + degree * (math.log10(f_p) - 0.5 * math.log10(2.0))
        + (3 - degree) * math.log10(m_reduced)
    )
    log_theta = (
        math.log10(degree / 4.0) + log_amplitude - math.log10(chi_qcd)
    )

    return {
        "schema": "susy-v37-g5-quality-certificate-v1",
        "selector": {
            "factorization": "Z5610 ~= Z66 x Z85",
            "charge_map": "q5610=85*q66+66*h85 mod5610",
            "spontaneous_breaking_by_P_and_Pbar": {
                "P_q5610": combined_charge(2, 0),
                "Pbar_q5610": combined_charge(64, 0),
                "unbroken_subgroup_order": math.gcd(
                    N5610, combined_charge(2, 0)
                ),
                "unbroken_subgroup": "Z170 ~= Z2 x Z85",
                "relic_implication": (
                    "the lightest nontrivially Z85-charged anomalon is stable unless a "
                    "symmetry-preserving decay/dark sector or nonthermal history is supplied"
                ),
            },
            "spectator_charges": {
                "A2": 1,
                "A32": -1,
                "A15": 69,
                "A17": -69,
                "A16": 0,
            },
            "Z85_linear_sum": sum(h_signed.values()),
            "Z85_cubic_sum": sum(value**3 for value in h_signed.values()),
            "69_squared_mod85": 69**2 % 85,
            "mixed_Z4R_Z85_squared_integer": mixed_r_h2,
            "mixed_Z4R_Z85_squared_mod85": mixed_r_h2 % 85,
            "combined_charged_Weyl_rows": rows5610,
            "combined_Hsieh_Dai_Freed": hsieh_audit(N5610, rows5610),
        },
        "optimized_accidental_PQ_QP_equals_1": {
            name: f"{pq170}/170"
            for name, (_, _, _, pq170) in SINGLET_FIELDS.items()
            if pq170
        },
        "renormalizable_census": renormalizable_singlet_census(),
        "minimal_anomalon_mass": {
            "retained_terms": [list(term) for term in RETAINED_ANOMALON_TERMS],
            "removed_redundant_v36_terms": [list(term) for term in REMOVED_V36_TERMS],
            "field_order": ["A2", "A32", "A15", "A17", "A16"],
            "matrix": [
                ["0", "a", "0", "0", "0"],
                ["a", "0", "0", "0", "0"],
                ["0", "0", "0", "b", "0"],
                ["0", "0", "b", "0", "0"],
                ["0", "0", "0", "0", "c"],
            ],
            "determinant": "a^2*b^2*c",
            "full_rank_condition": "a*b*c != 0",
        },
        "complete_superpotential_ring": {
            "scope": "all monomials in the ten PS-singlet chiral species",
            **w_breaking,
        },
        "conservative_kahler_ring": {
            "scope": (
                "all monomials in the ten PS-singlet chiral species and their "
                "independently enumerated conjugates"
            ),
            **k_breaking,
        },
        "all_chiral_charge_lattice_lower_bound": {
            "scope": (
                "all 20 chiral species before imposing PS index contractions; "
                "absence below a degree is therefore stronger than a gauge-invariant census"
            ),
            "superpotential": all_w_breaking,
            "kahler_with_conjugates": all_k_breaking,
            "same_first_degrees_as_singlet_witnesses": (
                all_w_breaking["first_breaking_degree"]
                == w_breaking["first_breaking_degree"]
                and all_k_breaking["first_breaking_degree"]
                == k_breaking["first_breaking_degree"]
            ),
            "analytic_PQ_congruence": (
                "Q170 = 85*q66 + 2442*h85 (mod 5610) for every chiral species"
            ),
            "analytic_PQ_congruence_residues": pq_congruence,
            "analytic_PQ_congruence_holds_for_all_fields": all(
                residue == 0 for residue in pq_congruence.values()
            ),
        },
        "benchmark_unit_coefficient_W_degree33": {
            "fP_GeV": f_p,
            "Asoft_GeV": a_soft,
            "Mreduced_GeV": m_reduced,
            "chiQCD_GeV4": chi_qcd,
            "log10_abs_theta": log_theta,
            "passes_abs_theta_below_1e-10": log_theta < -10,
        },
        "promotion_boundary": {
            "polynomial_quality_materially_improved": True,
            "quality_gate_closed": False,
            "remaining": [
                "complete Spin^Z4R x Z5610 bordism and triple-mixed audit",
                "origin and quantum-gravity consistency of the Z85 spectator",
                "stable spectator-charged relic abundance or a symmetry-preserving decay path",
                "Kahler and soft coefficient matching",
                "global vacuum, inflation, reheating, and isocurvature history",
            ],
        },
    }


def rejected_pq_neutral_anomaly_higgs() -> dict[str, Any]:
    rows = [
        {"field": "B31", "multiplicity": 1, "charge": 31},
        {"field": "Bbar35", "multiplicity": 1, "charge": 35},
        {"field": "F16_12", "multiplicity": 16, "charge": 12},
        {"field": "Fbar16_23", "multiplicity": 16, "charge": 23},
        {"field": "S_q66_12", "multiplicity": 1, "charge": 12},
        {"field": "S_q66_65", "multiplicity": 1, "charge": 65},
        {"field": "S_q66_56", "multiplicity": 1, "charge": 56},
    ]
    m_soft = 1.0e4
    f = 5.0e11
    cutoff = 2.4e18
    chi_qcd = 0.0756**4
    loop_amplitude = m_soft**2 * f**4 / (16 * math.pi**2 * cutoff**2)
    log_theta = math.log10(loop_amplitude / chi_qcd)
    v_ps = 2.4e16
    log_theta_vps = log_theta + 2 * math.log10(v_ps / f)
    alpha_inverse = 15.2048
    completed_b = [5, 9, 13]
    return {
        "candidate": "PQ-neutral B/Bbar plus one complete 16+16bar",
        "field_content": {
            "B31_and_Bbar35": "PS (1,1,1), q66=(31,35), Z4R=(0,0)",
            "F16_12": "(4,2,1) + (bar4,1,2), q66=12, Z4R=1",
            "Fbar16_23": "(bar4,2,1) + (4,1,2), q66=23, Z4R=1",
            "S_q66_12_65_56": "three PS (1,1,1) singlets, Z4R=0",
            "row_multiplicity_note": "16 is Weyl representation dimension, not 16 copies",
        },
        "renormalizable_mass_terms": [
            "B31*F16_12*Fbar16_23",
            "P*S_q66_65^2/2",
            "Pbar*S_q66_12*S_q66_56",
            "YB*(B31*Bbar35-vB^2)",
        ],
        "finite_increment": hsieh_audit(66, rows),
        "mixed_PS_squared_Z66_increment_half_normalized": [4, 4, 4],
        "cancels_v36_mixed_residue": True,
        "QCD_PQ_anomaly_unchanged_at_renormalizable_level": True,
        "Delta_b_4_L_R": [4, 4, 4],
        "completed_one_loop_b_4_L_R": completed_b,
        "pole_ratios": [
            math.exp(2 * math.pi * alpha_inverse / coefficient)
            for coefficient in completed_b
        ],
        "pole_ratio_scope": (
            "optimistic common threshold vB=vPS; if vB is near fPQ, daughter-group "
            "running from fPQ to vPS must be included"
        ),
        "fatal_allowed_operator": {
            "operator": "Pbar^2 * Bbar * F16 * F16bar / M^2",
            "superfield_degree": 5,
            "Z66_charge_mod66": (2 * 64 + 35 + 12 + 23) % 66,
            "Z4R_charge_mod4": (2 * 2 + 0 + 1 + 1) % 4,
            "PQ_charge_QP_equals_1": -2,
            "estimated_loop_potential": "msoft^2*f^4/(16*pi^2*M^2)",
            "benchmark_assumption": "vB=fPQ=f for the quoted estimate",
            "log10_abs_theta_at_v36_benchmark": log_theta,
            "log10_abs_theta_if_vB_equals_vPS": log_theta_vps,
        },
        "verdict": (
            "rejected without an additional exact sequestering symmetry: the "
            "dimension-five operator defeats axion quality by about thirty decades"
        ),
    }


def alternative_routes() -> dict[str, Any]:
    return {
        "nonprimitive_Z132_R_consolidation": {
            "evidence_class": "parallel-search design assertion; not recomputed by this generator",
            "construction": "qtheta=33, qW=66; kernel Z33 and R quotient Z4R",
            "best_anomalon_charges": [35, 81, 82, 83, 65],
            "pure_finite_pass": True,
            "first_superpotential_PQ_breaking_degree": 11,
            "universal_doubled_mixed_gauge_residue_mod132": [62, 62, 62],
            "zero_residue_impossible_with_preserved_term_R_reassignments": True,
            "status": "cleaner symmetry product, but still needs a universal GS ultraviolet sector",
        },
        "five_dimensional_inflow": {
            "evidence_class": "UV scaffold arithmetic; no compactification certificate",
            "integer_U1X_lifts": {
                "PsiBar": -2,
                "PsiCBar": -2,
                "P": 2,
                "Pbar": -2,
                "A2": -29,
                "A32": 31,
                "A15": -3,
                "A17": 1,
                "A16": -1,
            },
            "continuous_anomalies": {
                "U1X_PS_squared_doubled": [-8, -8, -8],
                "U1X_gravity_squared": -33,
                "U1X_cubed": 5247,
            },
            "scaffold": (
                "5D N=1 U1X x GPS on S1/Z2, charge +/-66 Higgs pair, V37 visible "
                "wall, opposite-anomaly mirror wall, and an APS/eta inflow sector"
            ),
            "status": (
                "real 5D EFT ultraviolet scaffold; not strict closure until the second wall, "
                "PS center, Z4R, KK thresholds, and bulk quality spurions are explicit"
            ),
        },
        "composite_PS_axion_fork": {
            "evidence_class": "literature-backed different-model fork",
            "source": "https://arxiv.org/abs/2505.08866",
            "appeal": "dimension-12 leading axion-potential operator in a composite Pati-Salam construction",
            "not_adopted_reason": (
                "its QCD-like chiral breaking is not the present N=1 SUSY elementary-PQ theory; "
                "a supersymmetric completion and matching would be a different model"
            ),
        },
        "gauged_U1H_to_Z85_origin": {
            "evidence_class": "minimal microscopic scaffold; not a complete UV certificate",
            "continuous_charges": {
                "A2": 1,
                "A32": -1,
                "A15": 69,
                "A17": -69,
                "A16": 0,
                "Higgs_plus": 85,
                "Higgs_minus": -85,
            },
            "breaking_superpotential": "YH*(Higgs_plus*Higgs_minus-vH^2)",
            "continuous_gravitational_and_cubic_anomalies_pairwise_zero": True,
            "unbroken_group": "Z85",
            "continuous_Z4R_U1H_squared_residue_before_heavy_UV_completion": 9520,
            "large_charge_sum_q_squared_including_Higgs_pair": 23974,
            "status": (
                "explains the finite remnant, but needs heavy-threshold/GS cancellation of the "
                "continuous mixed R anomaly and a perturbative U1H running audit"
            ),
        },
    }


def gate_ledger() -> dict[str, Any]:
    inherited = {
        "G2": "full pole matrices and covariance open",
        "G3": "Kahler/soft global vacuum and tunneling open",
        "G4": "microscopic mediation and electroweak likelihood open",
        "G6": "physical boundary data and uncertainty-propagated running open",
        "G7": "flavour tensors, dressing, running, and lattice covariance open",
        "G8": "out-of-sample flavour origin and joint likelihood open",
    }
    gates = [
        {
            "gate": "G1",
            "closed": False,
            "state": (
                "PURE_Z5610_FINITE_AND_SPECTATOR_PAIRWISE_ARITHMETIC_PASS__"
                "MIXED_PS_SELECTOR_AND_FULL_Z4R_PRODUCT_UV_OPEN"
            ),
        },
        {
            "gate": "G5",
            "closed": False,
            "state": (
                "ALL_CHIRAL_CHARGE_LATTICE_W_DEGREE33_AND_KAHLER_DEGREE32__"
                "RELIC_COSMOLOGY_AND_FULL_SOFT_MATCHING_OPEN"
            ),
        },
    ] + [
        {"gate": gate, "closed": False, "state": state}
        for gate, state in inherited.items()
    ]
    gates.sort(key=lambda row: int(row["gate"][1:]))
    return {
        "schema": "susy-v37-g1-g8-gate-ledger-v1",
        "complete_theory_exists": False,
        "established_full_predictive_closed_count": 0,
        "materially_updated_frontiers": ["G1", "G5"],
        "gates": gates,
    }


def build_report() -> dict[str, Any]:
    quality = finite_quality_certificate()
    rge = json.loads(RGE_JSON.read_text(encoding="utf-8")) if RGE_JSON.is_file() else None
    manifest = source_manifest()
    missing_sources = [row["path"] for row in manifest if not row["exists"]]
    report = {
        "schema": "susy-v37-new-physics-routes-v1",
        "status": (
            "V37_Z85_SPECTATOR_IMPLEMENTED__Z5610_EXACT_FINITE_PASS__"
            "ALL_CHIRAL_CHARGE_LATTICE_W_DEGREE33__KAHLER_DEGREE32__"
            "THREE_TERM_FULL_RANK_ANOMALON_MASS__G1_G5_STILL_FAIL_CLOSED"
        ),
        "model": MODEL_NAME,
        "decision": (
            "Adopt the Z85 spectator as a research-EFT quality improvement; retain the "
            "five-dimensional inflow and nonprimitive Z132 constructions as UV alternatives; "
            "reject the standalone PQ-neutral anomaly-Higgs matter repair."
        ),
        "quality": quality,
        "rejected_PQ_neutral_anomaly_higgs": rejected_pq_neutral_anomaly_higgs(),
        "alternative_routes": alternative_routes(),
        "gate_ledger": gate_ledger(),
        "live_SARAH_RGE_attestation": rge,
        "primary_sources": [
            "https://arxiv.org/abs/1808.02881",
            "https://arxiv.org/abs/2009.04582",
            "https://arxiv.org/abs/1308.1227",
            "https://arxiv.org/abs/1909.08775",
            "https://arxiv.org/abs/hep-th/0305024",
            "https://arxiv.org/abs/hep-ph/9311340",
            "https://arxiv.org/abs/2505.08866",
        ],
        "source_manifest": manifest,
        "required_sources_missing": missing_sources,
        "required_sources_all_present": not missing_sources,
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def markdown_report(report: Mapping[str, Any]) -> str:
    q = report["quality"]
    bad = report["rejected_PQ_neutral_anomaly_higgs"]
    rge = report["live_SARAH_RGE_attestation"]
    rge_line = (
        "The live V37 SARAH RGE attestation is not present yet."
        if rge is None
        else (
            f"Live SARAH initialized `{rge['model']}` and the two-loop calculation "
            f"status is `{rge['two_loop_RGE_calculation_succeeded']}`."
        )
    )
    return f"""# SUSY V37 new-physics routes

## Outcome

V37 implements one real improvement, not a complete theory.  The V36 selector
is enlarged by an anomaly-paired `Z85` spectator and represented faithfully as
`Z5610`.  Two redundant anomalon terms are removed while the mass determinant
remains `a^2*b^2*c`.

The exact combined finite anomaly test passes.  The complete PS-singlet
chiral superpotential ring first violates the optimized accidental PQ symmetry at
degree `{q['complete_superpotential_ring']['first_breaking_degree']}`.  A
conservative search including conjugate fields first finds a Kahler invariant
at degree `{q['conservative_kahler_ring']['first_breaking_degree']}`.  This is a
large improvement over V36's degree-10 heavy-anomalon frontier.

As a stronger cross-check, a charge-lattice search over all 20 chiral species,
performed before imposing Pati--Salam index contractions, finds the same first
degrees.  Therefore no omitted gauge contraction can generate a lower-degree
polynomial operator; the displayed singlet witnesses show that the bounds are
attained.

The spectator charges are
`h85(A2,A32,A15,A17,A16)=(1,-1,69,-69,0)`.  Pairwise linear and cubic sums
vanish, `69^2=1 mod85`, and the tested mixed `Z4R-Z85^2` residue vanishes.
The full `Spin^Z4R x Z5610` bordism, however, is not inferred from these
pairwise checks.

## Important rejected loophole

A PQ-neutral anomaly-Higgs plus one complete `16+16bar` really does cancel the
three mixed selector anomalies with only `Delta b=(4,4,4)`.  It nevertheless
fails quality: the exact symmetries allow
`Pbar^2 Bbar 16 16bar/M^2`.  The conservative soft-loop estimate gives
`log10|theta|={bad['fatal_allowed_operator']['log10_abs_theta_at_v36_benchmark']:.3f}`
at the frozen V36 benchmark, roughly thirty orders above the limit.  The route
is rejected unless another exact sequestering mechanism is supplied.

## Other routes retained

- A nonprimitive cyclic `Z132` consolidates `Z4R` and `Z33` and reaches
  degree 11, but its universal mixed residue is nonzero.
- A five-dimensional `U(1)_X -> Z66` interval with a mirror wall and APS/eta
  inflow is a concrete UV scaffold.  It still needs the second wall, global PS
  form, `Z4R`, KK thresholds, and quality spurions made explicit.
- A four-dimensional gauged `U(1)_H -> Z85` candidate with charge-`+/-85`
  Higgs fields would produce the spectator remnant.  Its continuous mixed R
  anomaly and unusually large Abelian charge running make the parent theory
  incomplete until a heavy UV sector is supplied.
- The recent composite Pati--Salam axion is a serious radical fork, but is not
  the present elementary N=1 SUSY theory and cannot be spliced in without a new
  dynamical model.

## Validation boundary

{rge_line}

The `P,Pbar` vacuum leaves `Z170 ~= Z2 x Z85` unbroken.  Consequently the
lightest spectator-charged anomalon is stable in the current field content;
reheating below its mass or a symmetry-preserving decay/dark-sector completion
is mandatory before cosmological promotion.

Strict gate count remains `0/8`.  G5's polynomial subproblem is materially
stronger, while G1 has sharper ultraviolet options; neither gate is promoted.

Core SHA-256: `{report['core_sha256']}`
"""


def expected_outputs(report: Mapping[str, Any]) -> dict[Path, str]:
    return {
        REPORT_JSON: json.dumps(report, indent=2, sort_keys=True) + "\n",
        REPORT_MD: markdown_report(report),
        QUALITY_JSON: json.dumps(report["quality"], indent=2, sort_keys=True) + "\n",
        GATES_JSON: json.dumps(report["gate_ledger"], indent=2, sort_keys=True) + "\n",
    }


def write_outputs(outputs: Mapping[Path, str]) -> None:
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8")


def check_outputs(outputs: Mapping[Path, str]) -> bool:
    good = True
    for path, expected in outputs.items():
        if not path.is_file() or path.read_text(encoding="utf-8") != expected:
            print(f"V37_MISMATCH {path.name}")
            good = False
    return good


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report()
    if report["required_sources_missing"]:
        print(
            "V37_REQUIRED_SOURCE_MISSING "
            + ",".join(report["required_sources_missing"])
        )
        return 1
    outputs = expected_outputs(report)
    if args.check:
        good = check_outputs(outputs)
        print(
            f"V37_NEW_PHYSICS_CHECK {'PASS' if good else 'FAIL'} "
            f"{report['core_sha256']}"
        )
        return 0 if good else 1
    write_outputs(outputs)
    print(f"V37_NEW_PHYSICS_WRITE PASS {report['core_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
