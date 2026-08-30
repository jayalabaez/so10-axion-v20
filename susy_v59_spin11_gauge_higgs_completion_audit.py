#!/usr/bin/env python3
"""Fail-closed V59 audit of a supersymmetric Spin(11) gauge-Higgs route.

The audit keeps the exact Spin(11) interval projector, constructs the smallest
rank-breaking brane sector that removes the uneaten 5+5bar, and writes the
most explicit anomaly-paired bulk-32 mediator skeleton supported by the
primary literature.  It then proves a sharp obstruction: an Abelian non-R
symmetry commuting with Spin(10), under which the gauge-Higgs field is neutral,
cannot simultaneously allow a full-rank symmetric three-family Yukawa matrix
and forbid every same-family 16_i^4 operator.  The published non-supersymmetric
fermion-number proposal does not evade that statement.

This is a certificate of exact progress and of a scoped obstruction, not a
claim that a UV-complete Spin(11) action or gate G1 has been constructed.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V59_SPIN11_GAUGE_HIGGS_COMPLETION_AUDIT.json"
MD_PATH = ROOT / "SUSY_V59_SPIN11_GAUGE_HIGGS_COMPLETION_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v59_spin11_gauge_higgs_completion_audit.py"
V56_PATH = ROOT / "SUSY_V56_ORBIFOLD_GEOMETRIC_Z4R_PROTECTION_AUDIT.json"
V58_PATH = ROOT / "SUSY_V58_HETEROTIC_G1_MICROSCOPIC_COMPLETION_AUDIT.json"

EXPECTED_V56_CORE = "09ba35b4e7cc05bf2375818e71610f565d6a330b5e8f0221373c301a58293a55"
EXPECTED_V58_CORE = "c31d5fe65fc5bd96279bb739f5284854a624b2ee1586004c9b84998225d382c6"

STATUS = (
    "V59_SPIN11_GAUGE_HIGGS_ONE_ACTION_ATTEMPT__EXACT_INTERVAL_PROJECTOR__"
    "TWO_WEAK_CHIRAL_ZERO_MODES__ZERO_COLORED_CHIRAL_ZERO_MODES__"
    "RANK_BREAKING_5_PLUS_5BAR_HAZARD_REPAIRED__MIRROR_32_MEDIATOR_KERNEL_"
    "CONSTRUCTIBLE_BUT_NOT_SOURCE_COMPLETED__ABELIAN_NON_R_PROTON_SELECTOR_"
    "NO_GO_PROVED__POINTWISE_PERTURBATIVE_ANOMALY_PAIRING_CONDITIONAL__"
    "DAI_FREED_AND_UV_COMPLETION_OPEN__STRICT_G1_OPEN__ZERO_GATES_CLOSED"
)

PRIMARY_SOURCES = [
    {
        "id": "HOSOTANI_YAMATSU_2015",
        "title": "Gauge-Higgs Grand Unification",
        "authors": "Yutaka Hosotani and Naoki Yamatsu",
        "arxiv": "1504.03817",
        "url": "https://arxiv.org/abs/1504.03817",
        "scope": (
            "Non-supersymmetric warped Spin(11) action; P0/P1 projectors, "
            "Spin(10)-wall 16 scalar, bulk 32/11 matter and global fermion-number proposal."
        ),
        "not_imported_as_proof": (
            "It has one real Higgs doublet rather than the supersymmetric complex "
            "bidoublet, and does not supply the V59 SUSY mediator/anomaly completion."
        ),
    },
    {
        "id": "FURUI_HOSOTANI_YAMATSU_2016",
        "title": "Toward Realistic Gauge-Higgs Grand Unification",
        "authors": "Atsushi Furui, Yutaka Hosotani and Naoki Yamatsu",
        "arxiv": "1606.07222",
        "url": "https://arxiv.org/abs/1606.07222",
        "scope": (
            "Explicit Spin(11) bulk and brane action, component parities, brane "
            "mixings, Wilson phase and proton-stability discussion."
        ),
        "source_falsifiers": (
            "The paper reports light exotic fermions and too small a Higgs mass; "
            "it states that Majorana singlet masses break N_Psi and can induce proton decay."
        ),
    },
    {
        "id": "BURDMAN_NOMURA_2003",
        "title": "Unification of Higgs and Gauge Fields in Five Dimensions",
        "authors": "Gustavo Burdman and Yasunori Nomura",
        "arxiv": "hep-ph/0210257",
        "url": "https://arxiv.org/abs/hep-ph/0210257",
        "scope": (
            "5D N=1 gauge-Higgs superfield transformation, two MSSM Higgs "
            "doublets, bulk-hypermultiplet gauge Yukawas, brane mixing, and soft mu routes."
        ),
        "source_boundary": (
            "Its explicit realistic models are SU(3)W and SU(6), not the Spin(11) "
            "local-family action audited here."
        ),
    },
    {
        "id": "HEBECKER_2001",
        "title": (
            "5D Super Yang-Mills Theory in 4D Superspace, Superfield Brane "
            "Operators, and Applications to Orbifold GUTs"
        ),
        "authors": "Arthur Hebecker",
        "arxiv": "hep-ph/0112230",
        "url": "https://arxiv.org/abs/hep-ph/0112230",
        "scope": "Gauge-covariant fifth derivative and classification of allowed brane operators.",
    },
    {
        "id": "VON_GERSDORFF_QUIROS_2003",
        "title": "Localized anomalies in orbifold gauge theories",
        "authors": "Gero von Gersdorff and Mariano Quiros",
        "arxiv": "hep-th/0305024",
        "url": "https://arxiv.org/abs/hep-th/0305024",
        "scope": (
            "Fixed-point anomaly formula; only globally vanishing pure-gauge "
            "profiles can be canceled by the 5D four-form/CS mechanism."
        ),
    },
    {
        "id": "SCRUCCA_SERONE_SILVESTRINI_ZWIRNER_2001",
        "title": "Anomalies in orbifold field theories",
        "authors": "C. A. Scrucca, M. Serone, L. Silvestrini and F. Zwirner",
        "arxiv": "hep-th/0110073",
        "url": "https://arxiv.org/abs/hep-th/0110073",
        "scope": "Demonstrates localized anomalies even when orbifold projections remove zero modes.",
    },
    {
        "id": "GARCIA_ETXEBARRIA_MONTERO_2018",
        "title": "Dai-Freed anomalies in particle physics",
        "authors": "Inaki Garcia-Etxebarria and Miguel Montero",
        "arxiv": "1808.00009",
        "url": "https://arxiv.org/abs/1808.00009",
        "scope": "Refined anomaly conditions; 4D Spin(10) GUT matter is found anomaly free.",
        "source_boundary": "Does not evaluate this 5D interval determinant with its wall conditions.",
    },
    {
        "id": "LEE_ET_AL_2010",
        "title": "A unique Z_4^R symmetry for the MSSM",
        "authors": "Hyun Min Lee et al.",
        "arxiv": "1009.0905",
        "url": "https://arxiv.org/abs/1009.0905",
        "scope": (
            "Classifies anomaly-free Abelian discrete symmetries commuting with "
            "Spin(10) that address mu and proton operators; selects Z4R."
        ),
    },
]


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def load_bound(path: Path, expected: str, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"missing {label}: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    actual = canonical_sha(value)
    if value.get("core_sha256") != actual:
        raise RuntimeError(f"{label} canonical core is stale")
    if actual != expected:
        raise RuntimeError(f"unexpected {label} canonical core")
    return value


def determinant(matrix: Sequence[Sequence[int | Fraction]]) -> Fraction:
    work = [[Fraction(x) for x in row] for row in matrix]
    n = len(work)
    if any(len(row) != n for row in work):
        raise ValueError("square matrix required")
    result = Fraction(1)
    for col in range(n):
        pivot = next((r for r in range(col, n) if work[r][col]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            result *= -1
        value = work[col][col]
        result *= value
        for r in range(col + 1, n):
            ratio = work[r][col] / value
            for c in range(col, n):
                work[r][c] -= ratio * work[col][c]
    return result


def gauge_parity_audit() -> dict[str, Any]:
    # A=1..4, B=5..10, c=11 in the vector representation.
    p0 = [1] * 10 + [-1]
    p1 = [1] * 4 + [-1] * 7
    classes: dict[str, dict[str, Any]] = {}
    rows: list[dict[str, Any]] = []
    for i, j in itertools.combinations(range(11), 2):
        v = (p0[i] * p0[j], p1[i] * p1[j])
        s = (-v[0], -v[1])
        if i < 4 and j < 4:
            block = "AA"
        elif 4 <= i < 10 and 4 <= j < 10:
            block = "BB"
        elif i < 4 and 4 <= j < 10:
            block = "AB"
        elif i < 4 and j == 10:
            block = "Ac"
        elif 4 <= i < 10 and j == 10:
            block = "Bc"
        else:  # pragma: no cover - the partition above is exhaustive
            raise AssertionError((i, j))
        rows.append({"generator": [i + 1, j + 1], "block": block, "V": list(v), "Sigma": list(s)})
    for block in ("AA", "BB", "AB", "Ac", "Bc"):
        selected = [r for r in rows if r["block"] == block]
        classes[block] = {
            "multiplicity": len(selected),
            "V_parity": selected[0]["V"],
            "Sigma_parity": selected[0]["Sigma"],
        }
    v_zero = [r for r in rows if r["V"] == [1, 1]]
    s_zero = [r for r in rows if r["Sigma"] == [1, 1]]
    return {
        "P0_vector": [1] * 10 + [-1],
        "P1_vector": [1] * 4 + [-1] * 7,
        "wall_groups": {"y0": "Spin(10)", "yL": "Spin(4)xSpin(7)"},
        "zero_mode_gauge_group_before_rank_breaking": "Spin(4)xSpin(6) (Pati-Salam global quotient not fixed here)",
        "classes": classes,
        "adjoint_generator_count": len(rows),
        "V_zero_generator_count": len(v_zero),
        "Sigma_zero_component_count": len(s_zero),
        "V_zero_blocks": sorted({r["block"] for r in v_zero}),
        "Sigma_zero_blocks": sorted({r["block"] for r in s_zero}),
        "Sigma_zero_representation": "complex (1,2,2) under SU(4)xSU(2)LxSU(2)R",
        "SM_decomposition": ["(1,2)_(+1/2)=Hu", "(1,2)_(-1/2)=Hd"],
        "weak_chiral_zero_modes": 2,
        "colored_chiral_zero_modes": 0,
        "direct_local_polynomial_Sigma_mass_allowed": False,
        "reason": "Sigma -> exp(Lambda)(Sigma-sqrt(2) partial5)exp(-Lambda) has an inhomogeneous shift.",
    }


def spinor_mediator_parities() -> dict[str, Any]:
    # P0sp and P1sp commute and each simultaneous eigenspace has dimension 8.
    eigenspaces = [
        {"P0sp": p0, "P1sp": p1, "dimension": 8}
        for p0, p1 in itertools.product((1, -1), repeat=2)
    ]
    return {
        "P0_spinor": "Gamma_11",
        "P1_spinor": "-Gamma_1 Gamma_2 Gamma_3 Gamma_4",
        "commute": True,
        "simultaneous_eigenspaces": eigenspaces,
        "single_32_hyper_warning": (
            "A source-like intrinsic-parity choice leaves chiral zero modes; a 32 is not a pure heavy mediator."
        ),
        "paired_regulator": {
            "hypermultiplets_per_channel": ["M_a in 32 with eta=(+,+)", "Mtilde_a in 32 with eta=(-,-)"],
            "localized_anomaly_relation": "A_f(Mtilde)=-A_f(M) at f=0,L",
            "net_localized_perturbative_anomaly": 0,
            "zero_modes": (
                "Complementary chiral zero sectors must be lifted by a full-rank Spin(10)-wall mass/mixing matrix."
            ),
            "conditional": True,
        },
    }


def rank_breaking_sector() -> dict[str, Any]:
    matrix = [[0, 1], [1, 1]]
    return {
        "location": "y=0 Spin(10) wall",
        "fields": {"C": "16", "Cbar": "bar16", "T": "10", "S": "1"},
        "superpotential": (
            "Wrank=kappa*S*(C*Cbar-v^2)+lambda*C*C*T+"
            "lambdabar*Cbar*Cbar*T+(M_T/2)*T*T"
        ),
        "supersymmetric_vacuum": {
            "C": "v in nu^c direction",
            "Cbar": "v in conjugate nu^c direction",
            "S": 0,
            "T": 0,
            "F_zero": True,
            "D_zero": True,
            "conditions": ["v nonzero", "kappa nonzero", "lambda*lambdabar nonzero"],
        },
        "breaking": "Spin(10)->SU(5); intersection with Pati-Salam is the SM gauge algebra",
        "minimal_pair_only_hazard": {
            "C_plus_Cbar_complex_components": 32,
            "broken_generators_and_eaten_chirals": 21,
            "uneaten_before_T": "5+bar5 plus one radial singlet; S pairs with the radial singlet",
        },
        "five_mass_matrix": "[[0,lambdabar*v],[lambda*v,M_T]]",
        "five_mass_determinant": "-lambda*lambdabar*v^2",
        "normalized_example_determinant": str(determinant(matrix)),
        "five_plus_fivebar_full_rank_if": "lambda*lambdabar*v^2 != 0",
        "new_light_colored_states_after_generic_rank_breaking": 0,
        "anomaly_character": "C+Cbar is vectorlike, T is real, S is neutral",
        "not_claimed": (
            "No UV symmetry is supplied that selects this superpotential from every allowed wall operator."
        ),
    }


def mediator_yukawa_sector() -> dict[str, Any]:
    return {
        "status": "EXPLICIT_LOCAL_SKELETON__NONLOCAL_KERNEL_DEFINED__COEFFICIENT_SPECTRUM_NOT_SOLVED",
        "local_families": "F_i in 16 of Spin(10), i=1,2,3, at y=0",
        "bulk_fields": (
            "For each mediator channel a, use the mirror 32-hyper pair M_a,Mtilde_a "
            "with complementary intrinsic parities listed in spinor_mediator_parities."
        ),
        "bulk_superpotential_density": (
            "M_a^c*(partial5-Sigma/sqrt(2)+m_a*epsilon(y))*M_a + "
            "Mtilde_a^c*(partial5-Sigma/sqrt(2)+mtilde_a*epsilon(y))*Mtilde_a"
        ),
        "y0_mixing": (
            "W0=[Mtilde_bar16,a]*(mu_ab*[M_16,b]+lambda_ai*F_i), "
            "with all brackets denoting the boundary-even Spin(10) fragments."
        ),
        "zero_mode_obligation": "mu and the complete boundary mass matrix must have maximal rank in every SM sector",
        "gauge_covariant_kernel": (
            "K[Sigma]=P_even*(partial5-Sigma/sqrt(2)+M+boundary masses)^(-1)*P_even"
        ),
        "schur_complement": "Weff[F]=-(1/2) F^T lambda^T K[Sigma] lambda F",
        "wilson_line_statement": (
            "K depends on the holonomy W=P exp(integral Sigma dy); its linear coset term is the "
            "Spin(10) invariant 16_i*16_j*10_Sigma, while a local polynomial brane Yukawa is forbidden."
        ),
        "yukawa_definition_without_invented_numbers": (
            "Y_ij is defined as the derivative of lambda^T K[h] lambda with respect to the "
            "normalized (1,2,2) holonomy coordinate h at h=0."
        ),
        "literature_support": [
            "Burdman-Nomura: bulk gauge interaction yields Yukawas and brane mixing yields flavor",
            "Furui-Hosotani-Yamatsu: Spin(11) 32/11 bulk matter plus Spin(10)-wall mixings",
        ],
        "unproved_rows": [
            "No primary source publishes this exact SUSY Spin(11), local-F_i, mirror-32 action.",
            "The full KK eigenvalue problem after C,Cbar,T wall VEVs is not solved.",
            "Full-rank, realistic and non-unified Yu,Yd,Ye,Ynu are not demonstrated.",
            "The same kernel's couplings to colored Sigma KK states and its dimension-five determinant are not evaluated.",
        ],
        "full_realistic_yukawa_sector_closed": False,
    }


def allowed_symmetric_support(charges: Sequence[int], modulus: int) -> list[list[bool]]:
    return [[(charges[i] + charges[j]) % modulus == 0 for j in range(3)] for i in range(3)]


def support_has_full_rank(support: Sequence[Sequence[bool]]) -> bool:
    # A generic 3x3 matrix with this support has full rank iff some determinant
    # permutation has all three supported entries.  Symmetry does not invalidate
    # the criterion over characteristic zero.
    return any(all(support[i][perm[i]] for i in range(3)) for perm in itertools.permutations(range(3)))


def finite_selector_scan(max_modulus: int = 24) -> dict[str, Any]:
    counterexamples: list[dict[str, Any]] = []
    full_rank_assignments = 0
    for modulus in range(2, max_modulus + 1):
        for charges in itertools.product(range(modulus), repeat=3):
            support = allowed_symmetric_support(charges, modulus)
            if not support_has_full_rank(support):
                continue
            full_rank_assignments += 1
            all_diagonal_proton_forbidden = all((4 * q) % modulus != 0 for q in charges)
            if all_diagonal_proton_forbidden:
                counterexamples.append({"N": modulus, "charges": list(charges)})
    return {
        "moduli_scanned": [2, max_modulus],
        "full_rank_charge_assignments_checked": full_rank_assignments,
        "counterexamples": counterexamples,
        "no_counterexample": not counterexamples,
    }


def selector_obstruction() -> dict[str, Any]:
    scan = finite_selector_scan()
    return {
        "theorem_scope": (
            "Any Abelian non-R 0-form symmetry (finite or continuous) commuting with "
            "Spin(10), with neutral gauge-Higgs 10 and three wall 16_i, when the "
            "symmetric Yukawa support is generically full rank."
        ),
        "proof": [
            "An allowed Yukawa entry ij obeys q_i+q_j=0 because q_H=0.",
            "A nonzero determinant monomial selects a permutation of three labels.",
            "Every permutation of three labels has an odd cycle: a fixed point or a 3-cycle.",
            "Alternating q_i=-q_j around that odd cycle gives 2q_i=0 for a label on it.",
            "Therefore 4q_i=0 and the same-family Spin(10) invariant 16_i^4 is allowed.",
        ],
        "finite_scan": scan,
        "continuous_U1_NPsi": {
            "q16": 1,
            "qSigma": 0,
            "Yukawa_charge": 2,
            "Yukawa_allowed": False,
            "conclusion": "The published Dirac-fermion N_Psi cannot be copied to a holomorphic 16*16*Sigma superpotential.",
        },
        "Z2_matter_parity": {"Yukawa_allowed": True, "16_four_allowed": True},
        "published_NPsi_warning": (
            "Furui-Hosotani-Yamatsu impose a global fermion number and explicitly state "
            "that Majorana singlet masses break it and can induce proton decay at higher loops."
        ),
        "sharp_conclusion": (
            "The requested exact commuting Abelian non-R proton selector does not exist "
            "for the local-family neutral-gauge-Higgs architecture."
        ),
        "loopholes_not_excluded": [
            "an exact R symmetry",
            "non-Abelian family symmetry with a complete anomaly-safe UV realization",
            "noncommuting symmetry after abandoning a local Spin(10) wall",
            "split or bulk physical families rather than three local 16s",
            "topological/noninvertible selection with an explicit regulator",
        ],
    }


def visible_sm_anomalies() -> dict[str, Any]:
    # (name, SU3 cubic sign, T3, d3, T2, d2, Y, multiplicity)
    fields = [
        ("Q", 1, Fraction(1, 2), 3, Fraction(1, 2), 2, Fraction(1, 6), 3),
        ("Uc", -1, Fraction(1, 2), 3, Fraction(0), 1, Fraction(-2, 3), 3),
        ("Dc", -1, Fraction(1, 2), 3, Fraction(0), 1, Fraction(1, 3), 3),
        ("L", 0, Fraction(0), 1, Fraction(1, 2), 2, Fraction(-1, 2), 3),
        ("Ec", 0, Fraction(0), 1, Fraction(0), 1, Fraction(1), 3),
        ("Nc", 0, Fraction(0), 1, Fraction(0), 1, Fraction(0), 3),
        ("Hu", 0, Fraction(0), 1, Fraction(1, 2), 2, Fraction(1, 2), 1),
        ("Hd", 0, Fraction(0), 1, Fraction(1, 2), 2, Fraction(-1, 2), 1),
    ]
    su3_cubic = sum(mult * sign * d2 for _, sign, _, _, _, d2, _, mult in fields)
    su3_sq_y = sum(mult * t3 * d2 * y for _, _, t3, _, _, d2, y, mult in fields)
    su2_sq_y = sum(mult * t2 * d3 * y for _, _, _, d3, t2, _, y, mult in fields)
    y3 = sum(mult * d3 * d2 * y**3 for _, _, _, d3, _, d2, y, mult in fields)
    grav_y = sum(mult * d3 * d2 * y for _, _, _, d3, _, d2, y, mult in fields)
    doublets = sum(mult * d3 for _, _, _, d3, t2, _, _, mult in fields if t2)
    return {
        "SU3_cubed": str(su3_cubic),
        "SU3_squared_Y": str(su3_sq_y),
        "SU2_squared_Y": str(su2_sq_y),
        "Y_cubed": str(y3),
        "gravity_squared_Y": str(grav_y),
        "SU2_doublet_count_with_color": doublets,
        "Witten_SU2_anomaly_absent": doublets % 2 == 0,
    }


def anomaly_audit() -> dict[str, Any]:
    sm = visible_sm_anomalies()
    return {
        "global_group_warning": (
            "Spin, not SO, is required for spinor 16/32 matter; exact central quotients "
            "of the Pati-Salam and SM subgroups must be fixed before a bordism calculation."
        ),
        "pointwise_continuous": {
            "y0_before_rank_breaking": {
                "group": "Spin(10)",
                "brane_matter": "3x16 + (16+bar16) + 10 + singlet",
                "cubic_gauge_anomaly": 0,
                "reason": "Spin(10) has no cubic invariant; C+Cbar is vectorlike and T is real.",
            },
            "yL": {
                "group": "Spin(4)xSpin(7)",
                "cubic_gauge_anomaly": 0,
                "reason": "SU(2), SU(2) and Spin(7) have no perturbative 4D cubic gauge anomaly.",
            },
            "y0_after_rank_breaking": {
                "group": "SU(5)",
                "per_family": "A(10)+A(bar5)=1-1=0",
                "three_family_sum": 0,
                "rank_sector": "vectorlike/real after Higgsing",
                "mirror_mediator_pairs": "cancel projector-weighted local anomalies pairwise",
            },
            "conditional_pointwise_total": 0,
            "condition": (
                "Every bulk 32 channel is accompanied by the exact opposite-intrinsic-parity "
                "mirror and the full boundary regulator preserves the pairing."
            ),
        },
        "Pati_Salam_zero_mode_checks": {
            "SU4_cubic_per_family": "2*A(4)+2*A(bar4)=2-2=0",
            "SU2L_doublets": 14,
            "SU2R_doublets": 14,
            "both_Witten_anomalies_absent": True,
        },
        "visible_SM": sm,
        "five_dimensional_CS": {
            "Spin11_invariant_polynomial_degrees": [2, 4, 6, 8, 10],
            "degree_three_invariant_for_tr_F_cubed": False,
            "canonical_pure_Spin11_CS5_available": False,
            "required_level_for_paired_candidate": 0,
            "warning": (
                "An unpaired fixed-point SU(5)/SU(4) cubic profile cannot be repaired by "
                "inventing a Spin(11)-invariant CS5 term; it must cancel pointwise or come "
                "with a demonstrated globally-vanishing inflow construction."
            ),
        },
        "Dai_Freed": {
            "four_dimensional_Spin10_result_in_literature": "anomaly free",
            "traditional_pi4_and_SU2_checks": "pass for the displayed light spectrum",
            "five_dimensional_relative_eta_invariant": "NOT_COMPUTED",
            "boundary_mass_phase_and_global_quotients": "NOT_FIXED",
            "invertible_bulk_counterterm": "NOT_EXHIBITED",
            "strict_status": "OPEN",
        },
        "pointwise_perturbative_closed_for_displayed_paired_skeleton": True,
        "full_quantum_anomaly_trivialization_closed": False,
    }


def proton_and_threshold_audit() -> dict[str, Any]:
    return {
        "direct_wall_operator": {
            "operator": "delta(y) c_ijkl F_i F_j F_k F_l / M_*",
            "Spin10_invariant": True,
            "forbidden_by_candidate_gauge_symmetry": False,
            "fatal_without_selector": True,
        },
        "dimension_five_KK": {
            "source": "colored Sigma/mediator KK exchange after Wilson-kernel expansion",
            "status": "OPEN",
            "required_calculation": "full colored boundary-to-boundary mass matrix and Schur complement",
        },
        "dimension_six": {
            "source": "broken Spin(10) gauge KK exchange at the family wall",
            "scaling_only": "C6 ~ g4^2/Mc^2",
            "status": "requires Mc and wavefunction fit to current nucleon-lifetime limits",
        },
        "mu": {
            "local_supersymmetric_mu": "forbidden by the 5D gauge shift",
            "published_route": "Scherk-Schwarz/radion SUSY breaking gives a Higgsino mass tied to the twist",
            "complete_soft_action": False,
        },
        "thresholds": [
            "independent y0 Spin(10) and yL Spin(4)xSpin(7) brane kinetic terms",
            "rank-breaking thresholds from v and M_T",
            "mirror-32 KK determinants and kink masses",
            "Scherk-Schwarz/radion soft threshold",
        ],
        "unification_prediction_closed": False,
    }


def falsifiers() -> list[dict[str, Any]]:
    return [
        {"id": "F1", "test": "Parity enumeration differs from 21 V++ and four Sigma++ components", "effect": "reject projector"},
        {"id": "F2", "test": "lambda*lambdabar*v^2=0", "effect": "uneaten 5+bar5 remains"},
        {"id": "F3", "test": "Any mediator 32 lacks its opposite-parity mirror", "effect": "redo pointwise anomaly and CS audit"},
        {"id": "F4", "test": "A claimed Abelian non-R charge assignment allows full-rank neutral-H Yukawas but forbids all 16_i^4", "effect": "it must exhibit the failed determinant-cycle premise"},
        {"id": "F5", "test": "Colored Wilson-kernel KK determinant generates excessive C5", "effect": "reject proton sector"},
        {"id": "F6", "test": "Relative 5D eta invariant is nontrivial without an allowed counterterm", "effect": "reject quantum action"},
        {"id": "F7", "test": "Boundary kinetic/KK thresholds cannot fit measured couplings perturbatively", "effect": "reject compactification"},
        {"id": "F8", "test": "No full-rank realistic Yu,Yd,Ye,Ynu solution after the exact KK solve", "effect": "reject flavor sector"},
    ]


def gate_ledger() -> list[dict[str, Any]]:
    decisions = {
        "G1": (
            "OPEN: the Higgs projector and rank sector are explicit, but the exact non-R "
            "proton selector is obstructed, the mediator determinant is not source-completed, "
            "and the 5D Dai-Freed/UV definition is absent."
        ),
        "G2": "OPEN: no coefficient-level complete 4D Wilsonian action or realistic flavor/soft solution.",
        "G3": "OPEN: no stabilized compactification, physical quotient or full KK Hessian.",
        "G4": "OPEN: two weak and zero colored zero modes pass, but colored KK dimension-five exchange is unsolved.",
        "G5": "OPEN: dark matter and cosmological history are not selected.",
        "G6": "OPEN: inflation, reheating and defect history are absent.",
        "G7": "OPEN: precision thresholds and a global data likelihood are absent.",
        "G8": "OPEN: no microscopic UV completion or quantified predictivity/stability score.",
    }
    return [{"gate": f"G{i}", "status": "OPEN", "decision": decisions[f"G{i}"]} for i in range(1, 9)]


def source_manifest() -> dict[str, Any]:
    return {
        "audit_script": {"path": str(Path(__file__).resolve()), "sha256": sha256_file(Path(__file__).resolve())},
        "pytest": {"path": str(TEST_PATH.resolve()), "sha256": sha256_file(TEST_PATH)},
        "bound_V56": {"path": str(V56_PATH.resolve()), "sha256": sha256_file(V56_PATH)},
        "bound_V58": {"path": str(V58_PATH.resolve()), "sha256": sha256_file(V58_PATH)},
        "primary_sources": PRIMARY_SOURCES,
    }


def build_report() -> dict[str, Any]:
    v56 = load_bound(V56_PATH, EXPECTED_V56_CORE, "V56 orbifold architecture")
    v58 = load_bound(V58_PATH, EXPECTED_V58_CORE, "V58 frontier")
    parity = gauge_parity_audit()
    spinor = spinor_mediator_parities()
    rank = rank_breaking_sector()
    mediator = mediator_yukawa_sector()
    selector = selector_obstruction()
    anomalies = anomaly_audit()
    gates = gate_ledger()
    integrity = {
        "V56_core_is_canonical_and_expected": v56["core_sha256"] == EXPECTED_V56_CORE,
        "V58_core_is_canonical_and_expected": v58["core_sha256"] == EXPECTED_V58_CORE,
        "all_55_generators_enumerated": parity["adjoint_generator_count"] == 55,
        "Pati_Salam_vector_zero_algebra_dimension_21": parity["V_zero_generator_count"] == 21,
        "exact_four_complex_Sigma_components": parity["Sigma_zero_component_count"] == 4,
        "exact_two_weak_chirals": parity["weak_chiral_zero_modes"] == 2,
        "zero_colored_chiral_zero_modes": parity["colored_chiral_zero_modes"] == 0,
        "rank_breaker_five_matrix_nonzero_generic_determinant": rank["normalized_example_determinant"] == "-1",
        "finite_selector_scan_finds_no_counterexample": selector["finite_scan"]["no_counterexample"],
        "continuous_NPsi_forbids_holomorphic_Yukawa": not selector["continuous_U1_NPsi"]["Yukawa_allowed"],
        "pointwise_perturbative_pairing_passes": anomalies["pointwise_perturbative_closed_for_displayed_paired_skeleton"],
        "Dai_Freed_not_overclaimed": anomalies["Dai_Freed"]["strict_status"] == "OPEN",
        "all_gates_remain_open": all(row["status"] == "OPEN" for row in gates),
    }
    report: dict[str, Any] = {
        "schema": "susy_so10.v59.spin11_gauge_higgs_completion_audit.v1",
        "version": "V59",
        "date": "2026-08-29",
        "status": STATUS,
        "lineage": {
            "bound_V56_orbifold_core": v56["core_sha256"],
            "bound_V58_frontier_core": v58["core_sha256"],
            "relation": (
                "Route-B replacement action; it reuses no V56 Z4R closure claim and "
                "does not patch the V58 heterotic action."
            ),
        },
        "research_question": (
            "Can the Spin(11) gauge-Higgs blueprint become one anomaly-safe action with "
            "local Spin(10) families and no assumed R symmetry?"
        ),
        "gauge_and_zero_mode_audit": parity,
        "spinor_mediator_parities": spinor,
        "rank_breaking_sector": rank,
        "bulk_mediator_and_nonlocal_Yukawa": mediator,
        "proton_selector_obstruction": selector,
        "local_global_and_Dai_Freed_anomalies": anomalies,
        "proton_decay_mu_and_thresholds": proton_and_threshold_audit(),
        "falsifiers": falsifiers(),
        "strict_G1_matrix": [
            {"criterion": "one_explicit_5D_SUSY_action_skeleton", "status": "PARTIAL", "evidence": "gauge, rank and paired-mediator terms are explicit; exact KK determinant is absent"},
            {"criterion": "exact_two_Higgs_zero_modes_no_colored_zero", "status": "PASS", "evidence": "55-generator parity enumeration gives Sigma Ac only"},
            {"criterion": "rank_breaking_without_light_5_plus_5bar", "status": "PASS_CONDITIONAL", "evidence": "det=-lambda*lambdabar*v^2"},
            {"criterion": "realistic_full_rank_Yukawas", "status": "OPEN", "evidence": "kernel defined, exact spectrum/flavor fit not solved"},
            {"criterion": "exact_proton_selector_without_R", "status": "FAIL_IN_ABELIAN_COMMUTING_CLASS", "evidence": "determinant-cycle theorem"},
            {"criterion": "pointwise_perturbative_local_anomalies", "status": "PASS_CONDITIONAL", "evidence": "opposite-parity 32 mirrors cancel projector traces"},
            {"criterion": "traditional_4D_global_anomalies", "status": "PASS", "evidence": "even SU2 counts and anomaly-free Spin10/SM ledgers"},
            {"criterion": "relative_5D_Dai_Freed_trivialization", "status": "OPEN", "evidence": "eta phase, wall quotients and counterterm not computed"},
            {"criterion": "UV_complete_regulator", "status": "OPEN", "evidence": "5D nonrenormalizable EFT has no exhibited string/M-theory completion"},
            {"criterion": "strict_G1", "status": "OPEN", "evidence": "proton selector obstruction plus quantum/UV obligations"},
        ],
        "gate_ledger": gates,
        "terminal_decision": {
            "V59_G1_closed": False,
            "V59_closed_gates": [],
            "full_gates_closed": 0,
            "one_action_candidate_accepted": False,
            "sharp_obstruction_proved": True,
            "obstruction_scope": "commuting Abelian non-R selector with neutral gauge-Higgs and full-rank symmetric local-family Yukawas",
            "complete_theory": False,
            "next_valid_routes": [
                "restore a microscopic anomaly-safe R symmetry",
                "abandon three local Spin(10) 16s and use bulk/split matter",
                "exhibit an anomaly-safe non-Abelian or topological selector and redo the full determinant",
            ],
        },
        "claim_boundary": {
            "new_fundamental_physics_invented": False,
            "symbolic_coefficients_not_numerically_fabricated": True,
            "published_nonSUSY_action_not_misrepresented_as_SUSY_completion": True,
            "conditional_mirror_anomaly_pairing_labeled": True,
            "no_gate_promotion": True,
        },
        "integrity_checks": integrity,
        "n_integrity_checks": len(integrity),
        "n_failed_integrity_checks": sum(not value for value in integrity.values()),
        "source_manifest": source_manifest(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("V59 canonical core mismatch")
    if report.get("n_failed_integrity_checks") != 0:
        failed = [name for name, passed in report["integrity_checks"].items() if not passed]
        raise RuntimeError(f"V59 integrity failure: {failed}")
    if report["terminal_decision"]["V59_G1_closed"]:
        raise RuntimeError("V59 overclaimed G1")
    if report["terminal_decision"]["one_action_candidate_accepted"]:
        raise RuntimeError("V59 accepted a candidate despite its selector/quantum obstruction")
    if report["terminal_decision"]["complete_theory"]:
        raise RuntimeError("V59 overclaimed a complete theory")


def render_markdown(report: Mapping[str, Any]) -> str:
    parity = report["gauge_and_zero_mode_audit"]
    rank = report["rank_breaking_sector"]
    selector = report["proton_selector_obstruction"]
    anomaly = report["local_global_and_Dai_Freed_anomalies"]
    lines = [
        "# SUSY V59 Spin(11) gauge-Higgs completion audit",
        "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        "- Outcome: **sharp scoped obstruction; candidate rejected; G1 remains open**.",
        "- Gate promotions: **0/8**.",
        "",
        "## Bottom line",
        "",
        "The Spin(11) route gives the cleanest exact Higgs projector found: a 5D N=1 vector multiplet produces precisely the two MSSM weak chiral doublets and no colored chiral zero mode.  A supersymmetric Spin(10)-wall rank sector can also remove the otherwise uneaten 5+5bar without invoking an R symmetry.",
        "",
        "It still does not yield the requested complete one-action theory.  A mirror-paired bulk-32 sector defines a legitimate gauge-covariant nonlocal Yukawa kernel, but no primary source solves that exact local-family Spin(11) KK determinant.  More decisively, every commuting Abelian non-R selector with a neutral gauge-Higgs and a full-rank symmetric three-family Yukawa support allows at least one same-family 16^4 operator.  The exact proton selector therefore fails in this architecture.  The relative five-dimensional Dai--Freed phase and a UV regulator are also absent.",
        "",
        "## Exact projector and zero modes",
        "",
        "`P0=diag(+^10,-)` and `P1=diag(+^4,-^7)` give:",
        "",
        "| Generator block | Multiplicity | V parity | Sigma parity |",
        "|---|---:|---|---|",
    ]
    for block in ("AA", "BB", "AB", "Ac", "Bc"):
        row = parity["classes"][block]
        lines.append(f"| {block} | {row['multiplicity']} | {tuple(row['V_parity'])} | {tuple(row['Sigma_parity'])} |")
    lines.extend(
        [
            "",
            f"The enumeration covers all {parity['adjoint_generator_count']} Spin(11) generators.  V has {parity['V_zero_generator_count']} zero generators, the Pati--Salam algebra.  Sigma has only the four complex `Ac` components: `(1,2,2)=Hu+Hd`.  Hence weak chiral zero modes = {parity['weak_chiral_zero_modes']}, colored chiral zero modes = {parity['colored_chiral_zero_modes']}.",
            "",
            "The inhomogeneous transformation `Sigma -> exp(Lambda)(Sigma-sqrt(2) partial5)exp(-Lambda)` forbids local polynomial Sigma masses and local wall Yukawas.  It does not forbid holonomy-dependent nonlocal kernels.",
            "",
            "## Rank-breaking sector",
            "",
            f"At the Spin(10) wall use `{rank['superpotential']}`.",
            "",
            "The D-flat vacuum `C=Cbar=v` in the conjugate neutrino directions, `S=T=0`, breaks Spin(10) to SU(5).  A bare 16+bar16 pair leaves a 5+bar5.  Adding T(10) gives the SU(5) mass matrix `[[0,lambdabar v],[lambda v,M_T]]`, with determinant `-lambda*lambdabar v^2`; it is full rank for nonzero `lambda*lambdabar*v^2`.  This closes the minimal uneaten-multiplet hazard, conditionally on the displayed coefficients.",
            "",
            "## Bulk mediator / Wilson-line Yukawa skeleton",
            "",
            "For every 32 hypermultiplet channel, add a second 32 with both intrinsic parities reversed.  Their fixed-point anomaly projectors cancel pairwise.  At y=0, mix the boundary-even bar16 fragment with `mu*M_16 + lambda*F_i`.  The bulk operator is the standard covariant `partial5-Sigma/sqrt(2)+m epsilon(y)`.",
            "",
            "Integrating out the massive paired tower is an exact Schur-complement definition: `Weff=-(1/2)F^T lambda^T K[Sigma] lambda F`, where K is the projected inverse covariant fifth-dimensional operator.  K depends on the Wilson line, and its linear coset term has the required `16*16*10_Sigma` tensor.  No numerical Yukawa coefficient is asserted.",
            "",
            "Open: the exact spectrum after all wall masses, full-rank realistic flavor, and the colored-KK part of the same determinant have not been published or solved here.",
            "",
            "## Sharp non-R proton-selector obstruction",
            "",
        ]
    )
    for step in selector["proof"]:
        lines.append(f"- {step}")
    scan = selector["finite_scan"]
    lines.extend(
        [
            "",
            f"The executable audit checks every Z_N charge triple for 2 <= N <= {scan['moduli_scanned'][1]}: {scan['full_rank_charge_assignments_checked']} full-rank supports and zero counterexamples.",
            "",
            "A continuous `N_Psi` with q(16)=1 and q(Sigma)=0 forbids the holomorphic Yukawa itself.  Z2 allows both the Yukawa and 16^4.  The published non-supersymmetric Spin(11) model instead imposes a global Dirac-fermion number and explicitly warns that Majorana masses break it and can induce proton decay.  It is not an exact SUSY proton selector.",
            "",
            "The theorem is deliberately scoped: it does not exclude an exact R symmetry, an explicit anomaly-safe non-Abelian/topological selector, or abandoning local Spin(10) families.",
            "",
            "## Local, global, CS and Dai--Freed audit",
            "",
            "- y=0 Spin(10): no cubic invariant; three 16 families are perturbatively gauge-anomaly free.  C+Cbar is vectorlike, T is real.",
            "- y=L Spin(4)xSpin(7): neither SU(2) factor nor Spin(7) has a perturbative 4D cubic anomaly.",
            "- After rank breaking: each SU(5) family has `A(10)+A(bar5)=1-1=0`; opposite-parity 32 mirrors cancel projector-weighted bulk contributions.",
            f"- Pati--Salam SU(2)L and SU(2)R doublet counts are both {anomaly['Pati_Salam_zero_mode_checks']['SU2L_doublets']}, so both Witten checks pass.",
            f"- The MSSM+N^c low spectrum has {anomaly['visible_SM']['SU2_doublet_count_with_color']} SU(2) doublets and all displayed continuous anomalies vanish.",
            "- Spin(11) invariant-polynomial degrees are 2,4,6,8,10, so there is no degree-three polynomial and no canonical pure Spin(11) CS5 rescue.  The paired construction requires level zero.",
            "- This is only a perturbative/traditional ledger.  The global subgroup quotients, relative eta invariant with boundary masses, and an allowed invertible counterterm are not computed.  Dai--Freed therefore remains open.",
            "",
            "## Proton, mu and threshold obligations",
            "",
            "The same-wall `F^4/M_*` contact is gauge allowed and is fatal without a selector.  Colored Sigma/mediator KK exchange requires a full dimension-five determinant.  Broken-gauge-boson KK exchange gives dimension six scaling `g4^2/Mc^2` and must be confronted with nucleon limits.  A Scherk--Schwarz/radion twist can generate mu together with soft terms, but no complete soft action is selected.  Independent brane kinetic terms and all rank/mediator KK thresholds remain free inputs.",
            "",
            "## Strict G1 matrix",
            "",
            "| Criterion | Status | Evidence |",
            "|---|---|---|",
        ]
    )
    for row in report["strict_G1_matrix"]:
        lines.append(f"| {row['criterion']} | {row['status']} | {row['evidence']} |")
    lines.extend(["", "## G1--G8 ledger", "", "| Gate | Status | Decision |", "|---|---|---|"])
    for row in report["gate_ledger"]:
        lines.append(f"| {row['gate']} | {row['status']} | {row['decision']} |")
    lines.extend(
        [
            "",
            "## Primary sources",
            "",
            "- [Hosotani and Yamatsu, Spin(11) gauge-Higgs grand unification](https://arxiv.org/abs/1504.03817): exact P0/P1 projectors, wall scalar and fermion-number proposal.",
            "- [Furui, Hosotani and Yamatsu, explicit Spin(11) spectrum and brane interactions](https://arxiv.org/abs/1606.07222): component parities, Wilson phase, exotics and Majorana/proton warning.",
            "- [Burdman and Nomura, 5D supersymmetric gauge-Higgs unification](https://arxiv.org/abs/hep-ph/0210257): Sigma shift, bulk gauge Yukawas, brane flavor mixing and soft-mu routes.",
            "- [Hebecker, gauge-covariant 5D superfield brane operators](https://arxiv.org/abs/hep-ph/0112230).",
            "- [von Gersdorff and Quiros, localized orbifold anomalies and 5D CS/GS limits](https://arxiv.org/abs/hep-th/0305024); [Scrucca et al., zero-mode cancellation is insufficient](https://arxiv.org/abs/hep-th/0110073).",
            "- [Garcia-Etxebarria and Montero, Dai--Freed anomaly analysis](https://arxiv.org/abs/1808.00009); [Lee et al., Spin(10)-compatible discrete selector classification](https://arxiv.org/abs/1009.0905).",
            "",
            "## Source boundary",
            "",
            "The primary papers support each imported building block, but none publishes the combined SUSY Spin(11), local-family, mirror-mediator and quantum-anomaly-complete action.  Symbolic coefficients define obligations; they are not numerical predictions.  The result is a useful projector/rank design plus a real selector no-go, not a completed theory.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate without writing outputs")
    args = parser.parse_args()
    report = build_report()
    validate(report)
    if not args.check:
        write_outputs(report)
    print(f"V59_SPIN11_GAUGE_HIGGS_G1_OPEN {report['core_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
