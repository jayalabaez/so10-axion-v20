#!/usr/bin/env python3
"""V66 fail-closed route audit: GM overlap and unification repair.

V65 correctly retained the V64 Spin(11) orphan null mode, but it promoted an
allowed charge-zero Giudice-Masiero operator into a constructed mass and fast
decay mechanism.  This audit retracts that promotion.  It also performs the
first explicit one-loop threshold solve and gauge-only two-loop diagnostics
for the orphan pair, then tests a new complete-10 compensator candidate.

Nothing here closes G1.  The current action is rejected.  Two conditional
extensions are retained for further work: high-scale SUSY with only the
orphan pair, and low-scale SUSY after adding the missing U+Ubar and E+Ebar
members of a vectorlike SU(5) 10+10bar.  Neither is a complete theory.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V66_SPIN11_GM_OVERLAP_UNIFICATION_REPAIR_AUDIT.json"
MD_PATH = ROOT / "SUSY_V66_SPIN11_GM_OVERLAP_UNIFICATION_REPAIR_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v66_spin11_gm_overlap_unification_repair_audit.py"

V65_ROUTE_PATH = ROOT / "SUSY_V65_SPIN11_ORPHAN_LIFTING_CLASSIFICATION_AUDIT.json"
V65_MASTER_PATH = ROOT / "SUSY_V65_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V64_ROUTE_PATH = ROOT / "SUSY_V64_SPIN11_AB_TOWER_NULL_MODE_RETRACTION_AUDIT.json"

EXPECTED_V65_ROUTE_CORE = (
    "b87696403fb46c4a6b044be8abe58dd5f82b63a83a58fff262a6f00bdd6914ae"
)
EXPECTED_V65_MASTER_CORE = (
    "5b3056510129107959a6725139942307fc47b8cf56b375511a72cf9c6c8e58b8"
)
EXPECTED_V64_ROUTE_CORE = (
    "fe36b2f6f0e1786253827183bf7f8dc2dd9e15a94b7f036d5e9e6e0739717a1d"
)

STATUS = (
    "V66_SPIN11_GM_OVERLAP_UNIFICATION_REPAIR__V65_ARTIFACTS_VALID__"
    "V65_ACTION_UPGRADE_RETRACTED__GM_ALLOWED_NOT_CONSTRUCTED__V64_NULL_"
    "MODE_NORMALIZATION_SUPPRESSES_GM_AND_PORTALS__ONE_LOOP_THRESHOLD_"
    "SOLVE_EXACT__GAUGE_ONLY_TWO_LOOP_DIAGNOSTICS__FULL_SU5_TEN_"
    "COMPENSATOR_CANDIDATE_EXHIBITED__BARYON_SAFETY_NOT_INHERITED__"
    "CURRENT_ACTION_REJECTED__TWO_CONDITIONAL_EXTENSIONS__NO_WZ__"
    "G1_TO_G8_OPEN"
)

CLASSIFICATION = (
    "CURRENT_V65_ACTION_REJECTED__HIGH_SCALE_ORPHAN_ONLY_AND_LOW_SCALE_"
    "FULL_TEN_ARE_CANDIDATE_CONDITIONAL_EXTENSIONS__NEITHER_COMPLETE"
)

PI = math.pi
MZ = 91.1876
ALPHA_EM_INVERSE = 127.930
SIN2_THETA_W = 0.23122
ALPHA_S = 0.1177

B_SM = (Fraction(41, 10), Fraction(-19, 6), Fraction(-7))
B_MSSM = (Fraction(33, 5), Fraction(1), Fraction(-3))
B_ORPHAN = (Fraction(1, 5), Fraction(3), Fraction(2))
B_COMPANIONS = (Fraction(14, 5), Fraction(0), Fraction(1))
B_FULL_TEN = (Fraction(3), Fraction(3), Fraction(3))

SM_B_MATRIX = (
    (Fraction(199, 50), Fraction(27, 10), Fraction(44, 5)),
    (Fraction(9, 10), Fraction(35, 6), Fraction(12)),
    (Fraction(11, 10), Fraction(9, 2), Fraction(-26)),
)
EXPECTED_MSSM_B_MATRIX = (
    (Fraction(199, 25), Fraction(27, 5), Fraction(88, 5)),
    (Fraction(9, 5), Fraction(25), Fraction(24)),
    (Fraction(11, 5), Fraction(9), Fraction(14)),
)
EXPECTED_ORPHAN_DELTA_B = (
    (Fraction(1, 75), Fraction(3, 5), Fraction(16, 15)),
    (Fraction(1, 5), Fraction(21), Fraction(16)),
    (Fraction(2, 15), Fraction(6), Fraction(68, 3)),
)
EXPECTED_COMPANION_DELTA_B = (
    (Fraction(344, 75), Fraction(0), Fraction(128, 15)),
    (Fraction(0), Fraction(0), Fraction(0)),
    (Fraction(16, 15), Fraction(0), Fraction(34, 3)),
)
EXPECTED_FULL_TEN_DELTA_B = (
    (Fraction(23, 5), Fraction(3, 5), Fraction(48, 5)),
    (Fraction(1, 5), Fraction(21), Fraction(16)),
    (Fraction(6, 5), Fraction(6), Fraction(34)),
)

PINNED_TWO_LOOP = {
    "orphan_only_raw_no_matching": {
        "MS": 4.760378e11,
        "MQ": 4.760378e11,
        "MG": 2.266291e15,
        "alphaU": 0.02859797,
    },
    "orphan_only_universal_MSbar_to_DRbar": {
        "MS": 4.99199e11,
        "MQ": 4.99199e11,
        "MG": 2.36709e15,
        "alphaU_inverse": 34.9406,
    },
    "full_ten_raw_no_matching": {
        "MS": 1.383905e4,
        "M10": 1.383905e4,
        "MG": 1.216382e16,
        "alphaU": 0.07873997,
    },
}

PRIMARY_SOURCES = [
    {
        "id": "PDG_2025",
        "title": "Review of Particle Physics 2025",
        "url": "https://pdg.lbl.gov/2025/",
        "scope": "electroweak and strong-coupling inputs and scheme conventions",
    },
    {
        "id": "MARTIN_VAUGHN_1994",
        "title": "Two-loop renormalization group equations for soft supersymmetry-breaking couplings",
        "arxiv": "hep-ph/9311340",
        "url": "https://arxiv.org/abs/hep-ph/9311340",
        "scope": "N=1 supersymmetric one- and two-loop gauge beta functions",
    },
    {
        "id": "GIUDICE_MASIERO_1988",
        "title": "A natural solution to the mu problem in supergravity theories",
        "url": "https://doi.org/10.1016/0370-2693(88)91613-9",
        "scope": "Kahler-induced bilinear masses after supersymmetry breaking",
    },
    {
        "id": "LEE_ET_AL_2010",
        "title": "A unique Z4R symmetry for the MSSM",
        "arxiv": "1009.0905",
        "url": "https://arxiv.org/abs/1009.0905",
        "scope": "nonperturbative mu generation after Z4R breaking",
    },
    {
        "id": "HOSOTANI_YAMATSU_2015",
        "title": "Gauge-Higgs Grand Unification",
        "arxiv": "1504.03817",
        "url": "https://arxiv.org/abs/1504.03817",
        "scope": "Spin(11) gauge-Higgs route and twelve uneaten rank-breaking modes",
    },
]


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


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


def fstr(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def vector_strings(values: Sequence[Fraction]) -> list[str]:
    return [fstr(value) for value in values]


def matrix_strings(values: Sequence[Sequence[Fraction]]) -> list[list[str]]:
    return [vector_strings(row) for row in values]


def add_matrices(
    left: Sequence[Sequence[Fraction]],
    right: Sequence[Sequence[Fraction]],
) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(
        tuple(left[i][j] + right[i][j] for j in range(3)) for i in range(3)
    )


def representation(
    name: str,
    multiplicity: int,
    d3: int,
    d2: int,
    hypercharge: Fraction,
) -> dict[str, Any]:
    t3 = Fraction(1, 2) if d3 == 3 else Fraction(0)
    t2 = Fraction(1, 2) if d2 == 2 else Fraction(0)
    c3 = Fraction(4, 3) if d3 == 3 else Fraction(0)
    c2 = Fraction(3, 4) if d2 == 2 else Fraction(0)
    return {
        "name": name,
        "multiplicity": multiplicity,
        "d3": d3,
        "d2": d2,
        "Y": hypercharge,
        "T3": t3,
        "T2": t2,
        "C3": c3,
        "C2": c2,
    }


def indices(rep: Mapping[str, Any]) -> tuple[tuple[Fraction, ...], tuple[Fraction, ...]]:
    multiplicity = Fraction(rep["multiplicity"])
    y = rep["Y"]
    d3 = Fraction(rep["d3"])
    d2 = Fraction(rep["d2"])
    s = (
        multiplicity * Fraction(3, 5) * y * y * d3 * d2,
        multiplicity * rep["T2"] * d3,
        multiplicity * rep["T3"] * d2,
    )
    c = (Fraction(3, 5) * y * y, rep["C2"], rep["C3"])
    return s, c


def sum_indices(inventory: Sequence[Mapping[str, Any]]) -> tuple[Fraction, ...]:
    total = [Fraction(0), Fraction(0), Fraction(0)]
    for rep in inventory:
        s, _ = indices(rep)
        for i in range(3):
            total[i] += s[i]
    return tuple(total)


def mv_matrix(
    inventory: Sequence[Mapping[str, Any]], include_vector_multiplet: bool
) -> tuple[tuple[Fraction, ...], ...]:
    c_group = (Fraction(0), Fraction(2), Fraction(3))
    s_total = sum_indices(inventory)
    result = [[Fraction(0) for _ in range(3)] for _ in range(3)]
    if include_vector_multiplet:
        for a in range(3):
            result[a][a] = (
                -6 * c_group[a] * c_group[a]
                + 2 * c_group[a] * s_total[a]
            )
    else:
        for a in range(3):
            result[a][a] = 2 * c_group[a] * s_total[a]
    for rep in inventory:
        s, c = indices(rep)
        for a in range(3):
            for b in range(3):
                result[a][b] += 4 * s[a] * c[b]
    return tuple(tuple(row) for row in result)


def mssm_inventory() -> list[dict[str, Any]]:
    return [
        representation("Q", 3, 3, 2, Fraction(1, 6)),
        representation("Uc", 3, 3, 1, Fraction(-2, 3)),
        representation("Dc", 3, 3, 1, Fraction(1, 3)),
        representation("L", 3, 1, 2, Fraction(-1, 2)),
        representation("Ec", 3, 1, 1, Fraction(1)),
        representation("Hu", 1, 1, 2, Fraction(1, 2)),
        representation("Hd", 1, 1, 2, Fraction(-1, 2)),
    ]


def orphan_inventory() -> list[dict[str, Any]]:
    return [representation("Q_X + Qbar_X", 2, 3, 2, Fraction(1, 6))]


def companion_inventory() -> list[dict[str, Any]]:
    return [
        representation("Uc_X + U_X", 2, 3, 1, Fraction(2, 3)),
        representation("Ec_X + E_X", 2, 1, 1, Fraction(1)),
    ]


def martin_vaughn_derivation() -> dict[str, Any]:
    mssm = mssm_inventory()
    orphan = orphan_inventory()
    companions = companion_inventory()
    mssm_s = sum_indices(mssm)
    mssm_b = tuple(
        mssm_s[i] - 3 * (Fraction(0), Fraction(2), Fraction(3))[i]
        for i in range(3)
    )
    mssm_B = mv_matrix(mssm, include_vector_multiplet=True)
    orphan_b = sum_indices(orphan)
    orphan_B = mv_matrix(orphan, include_vector_multiplet=False)
    companion_b = sum_indices(companions)
    companion_B = mv_matrix(companions, include_vector_multiplet=False)
    full_B = add_matrices(orphan_B, companion_B)
    return {
        "convention": "rows and columns are ordered (U1_GUT, SU2_L, SU3_c)",
        "formula": {
            "b_a": "sum_i S_a(i) - 3 C_a(G)",
            "B_ab": (
                "-6 C_a(G)^2 delta_ab + 2 C_a(G) S_a delta_ab "
                "+ 4 sum_i S_a(i) C_b(i)"
            ),
        },
        "MSSM": {
            "sum_S": vector_strings(mssm_s),
            "b": vector_strings(mssm_b),
            "B": matrix_strings(mssm_B),
            "reproduces_standard_b": mssm_b == B_MSSM,
            "reproduces_standard_B": mssm_B == EXPECTED_MSSM_B_MATRIX,
        },
        "orphan_Q_pair": {
            "Delta_b": vector_strings(orphan_b),
            "Delta_B": matrix_strings(orphan_B),
            "matches_required": (
                orphan_b == B_ORPHAN and orphan_B == EXPECTED_ORPHAN_DELTA_B
            ),
        },
        "Uc_and_Ec_companions": {
            "Delta_b": vector_strings(companion_b),
            "Delta_B": matrix_strings(companion_B),
            "matches_required": (
                companion_b == B_COMPANIONS
                and companion_B == EXPECTED_COMPANION_DELTA_B
            ),
        },
        "complete_10_plus_10bar": {
            "Delta_b": vector_strings(
                tuple(orphan_b[i] + companion_b[i] for i in range(3))
            ),
            "Delta_B": matrix_strings(full_B),
            "one_loop_shift_is_universal": tuple(
                orphan_b[i] + companion_b[i] for i in range(3)
            )
            == B_FULL_TEN,
            "matches_required_B": full_B == EXPECTED_FULL_TEN_DELTA_B,
        },
    }


def initial_inverse_couplings() -> tuple[float, float, float]:
    return (
        Fraction(3, 5) * (1.0 - SIN2_THETA_W) * ALPHA_EM_INVERSE,
        SIN2_THETA_W * ALPHA_EM_INVERSE,
        1.0 / ALPHA_S,
    )


def solve_2x2(
    a: float, b: float, c: float, d: float, e: float, f: float
) -> tuple[float, float]:
    determinant = a * d - b * c
    if determinant == 0:
        raise RuntimeError("singular threshold system")
    return ((e * d - b * f) / determinant, (a * f - e * c) / determinant)


def threshold_inverse(
    log_ms: float, log_mx: float, log_mg: float, delta_b: Sequence[Fraction]
) -> tuple[float, float, float]:
    initial = initial_inverse_couplings()
    return tuple(
        initial[i]
        - float(B_SM[i]) * log_ms / (2 * PI)
        - float(B_MSSM[i]) * (log_mg - log_ms) / (2 * PI)
        - float(delta_b[i]) * (log_mg - log_mx) / (2 * PI)
        for i in range(3)
    )


def one_loop_ratio_solution(c_ratio: float) -> dict[str, Any]:
    if c_ratio <= 0:
        raise ValueError("c_ratio must be positive")
    log_c = math.log(c_ratio)
    x = tuple(B_SM[i] - B_MSSM[i] - B_ORPHAN[i] for i in range(3))
    y = tuple(B_MSSM[i] + B_ORPHAN[i] for i in range(3))
    rows: list[tuple[float, float]] = []
    rhs: list[float] = []
    initial = initial_inverse_couplings()
    for i, j in ((0, 1), (0, 2)):
        rows.append((float(x[i] - x[j]), float(y[i] - y[j])))
        rhs.append(
            2 * PI * (initial[i] - initial[j])
            + float(B_ORPHAN[i] - B_ORPHAN[j]) * log_c
        )
    log_ms, log_mg = solve_2x2(
        rows[0][0], rows[0][1], rows[1][0], rows[1][1], rhs[0], rhs[1]
    )
    log_mq = log_ms + log_c
    inverse = threshold_inverse(log_ms, log_mq, log_mg, B_ORPHAN)
    return {
        "c_ratio_MQ_over_MS": c_ratio,
        "MS_GeV": MZ * math.exp(log_ms),
        "MQ_GeV": MZ * math.exp(log_mq),
        "MG_GeV": MZ * math.exp(log_mg),
        "alphaU_inverse": sum(inverse) / 3,
        "max_inverse_coupling_residual": max(inverse) - min(inverse),
        "_logs": (log_ms, log_mq, log_mg),
    }


def one_loop_fixed_ms_solution(ms_gev: float) -> dict[str, Any]:
    if ms_gev <= MZ:
        raise ValueError("MS must be above MZ")
    log_ms = math.log(ms_gev / MZ)
    initial = initial_inverse_couplings()
    rows: list[tuple[float, float]] = []
    rhs: list[float] = []
    for i, j in ((0, 1), (0, 2)):
        rows.append(
            (
                -float(B_ORPHAN[i] - B_ORPHAN[j]),
                float(
                    B_MSSM[i]
                    + B_ORPHAN[i]
                    - B_MSSM[j]
                    - B_ORPHAN[j]
                ),
            )
        )
        rhs.append(
            2 * PI * (initial[i] - initial[j])
            - float(
                B_SM[i] - B_MSSM[i] - B_SM[j] + B_MSSM[j]
            )
            * log_ms
        )
    log_mq, log_mg = solve_2x2(
        rows[0][0], rows[0][1], rows[1][0], rows[1][1], rhs[0], rhs[1]
    )
    inverse = threshold_inverse(log_ms, log_mq, log_mg, B_ORPHAN)
    return {
        "MS_GeV": ms_gev,
        "MQ_GeV": MZ * math.exp(log_mq),
        "MG_GeV": MZ * math.exp(log_mg),
        "alphaU_inverse": sum(inverse) / 3,
        "max_inverse_coupling_residual": max(inverse) - min(inverse),
    }


def exact_ratio_exponents() -> dict[str, Fraction]:
    x = tuple(B_SM[i] - B_MSSM[i] - B_ORPHAN[i] for i in range(3))
    y = tuple(B_MSSM[i] + B_ORPHAN[i] for i in range(3))
    rows = [
        (x[i] - x[j], y[i] - y[j]) for i, j in ((0, 1), (0, 2))
    ]
    rhs = [B_ORPHAN[i] - B_ORPHAN[j] for i, j in ((0, 1), (0, 2))]
    a, b = rows[0]
    c, d = rows[1]
    e, f = rhs
    determinant = a * d - b * c
    ms = (e * d - b * f) / determinant
    mg = (a * f - e * c) / determinant
    mq = Fraction(1) + ms
    alpha_numerator = (
        -B_SM[0] * ms
        - B_MSSM[0] * (mg - ms)
        - B_ORPHAN[0] * (mg - ms - 1)
    )
    return {
        "MS_power": ms,
        "MQ_power": mq,
        "MG_power": mg,
        "alphaU_inverse_ln_c_numerator_over_2pi": alpha_numerator,
    }


def one_loop_audit() -> dict[str, Any]:
    c1 = one_loop_ratio_solution(1.0)
    low = one_loop_fixed_ms_solution(1000.0)
    powers = exact_ratio_exponents()
    return {
        "input_scheme": "PDG electroweak inputs at MZ treated as MSbar for this diagnostic",
        "inputs": {
            "input_literals": {
                "alphaEM_inverse": "127.930",
                "sin2_thetaW": "0.23122",
                "alphaS": "0.1177",
                "MZ_GeV": "91.1876",
            },
            "alphaEM_inverse": ALPHA_EM_INVERSE,
            "sin2_thetaW": SIN2_THETA_W,
            "alphaS": ALPHA_S,
            "MZ_GeV": MZ,
            "derived_alpha_inverse_GUT_order": list(initial_inverse_couplings()),
        },
        "conventional_order": ["b1_GUT", "b2", "b3"],
        "beta_coefficients": {
            "SM": vector_strings(B_SM),
            "MSSM": vector_strings(B_MSSM),
            "orphan_Q_pair_Delta_b": vector_strings(B_ORPHAN),
            "companion_Delta_b": vector_strings(B_COMPANIONS),
            "full_10_plus_10bar_Delta_b": vector_strings(B_FULL_TEN),
        },
        "threshold_equation": (
            "alpha_i^-1(MG)=alpha_i^-1(MZ)-b_i^SM ln(MS/MZ)/(2pi)"
            "-b_i^MSSM ln(MG/MS)/(2pi)-Delta_b_i ln(MG/MQ)/(2pi)"
        ),
        "analytic_c_family": {
            "definition": "c = MQ/MS",
            "MS": "2.25084e11 GeV * c^(-21/32)",
            "MQ": "2.25084e11 GeV * c^(11/32)",
            "MG": "4.54981e15 GeV * c^(3/64)",
            "alphaU_inverse": "34.16816 - [121/(128*pi)] ln(c)",
            "derived_exact_powers": {
                "MS": fstr(powers["MS_power"]),
                "MQ": fstr(powers["MQ_power"]),
                "MG": fstr(powers["MG_power"]),
                "alphaU_inverse_ln_c": "-121/(128*pi)",
            },
        },
        "c_equals_1": {
            key: value for key, value in c1.items() if not key.startswith("_")
        },
        "c_equals_1_quoted": {
            "MS_GeV": 2.25084e11,
            "MQ_GeV": 2.25084e11,
            "MG_GeV": 4.54981e15,
            "alphaU_inverse": 34.16816,
        },
        "fixed_MS_1_TeV": low,
        "fixed_MS_1_TeV_quoted": {
            "MQ_GeV": 5.337995621e15,
            "MG_GeV": 1.797161841e16,
        },
        "interpretation": (
            "the orphan-only spectrum unifies at one loop only with a very high "
            "common SUSY/orphan threshold, or with the orphan threshold driven "
            "near MG when MS is fixed to 1 TeV"
        ),
    }


def _float_vector(values: Sequence[Fraction]) -> Any:
    import numpy as np

    return np.array([float(value) for value in values], dtype=float)


def _float_matrix(values: Sequence[Sequence[Fraction]]) -> Any:
    import numpy as np

    return np.array([[float(value) for value in row] for row in values], dtype=float)


def _integrate_segment(alpha_inverse: Any, delta_t: float, b: Any, B: Any) -> Any:
    from scipy.integrate import solve_ivp

    def rhs(_: float, inverse: Any) -> Any:
        return -b / (2 * PI) - B.dot(1.0 / inverse) / (8 * PI * PI)

    solution = solve_ivp(
        rhs,
        (0.0, delta_t),
        alpha_inverse,
        rtol=2e-11,
        atol=2e-12,
        method="DOP853",
    )
    if not solution.success:
        raise RuntimeError(f"two-loop integration failed: {solution.message}")
    return solution.y[:, -1]


def _solve_two_loop_common_threshold(
    extra_b: Sequence[Fraction],
    extra_B: Sequence[Sequence[Fraction]],
    guess_ms: float,
    guess_mg: float,
    apply_universal_dr_shift: bool,
) -> dict[str, float]:
    import numpy as np
    from scipy.optimize import root

    initial = np.array(initial_inverse_couplings(), dtype=float)
    b_sm = _float_vector(B_SM)
    b_high = _float_vector(
        tuple(B_MSSM[i] + extra_b[i] for i in range(3))
    )
    B_sm = _float_matrix(SM_B_MATRIX)
    B_high = _float_matrix(
        add_matrices(EXPECTED_MSSM_B_MATRIX, extra_B)
    )
    casimirs = np.array([0.0, 2.0, 3.0], dtype=float)

    def run(log_ms: float, log_mg: float) -> Any:
        inverse = _integrate_segment(initial, log_ms, b_sm, B_sm)
        if apply_universal_dr_shift:
            inverse = inverse - casimirs / (12 * PI)
        return _integrate_segment(inverse, log_mg - log_ms, b_high, B_high)

    def residual(logs: Any) -> Any:
        inverse = run(float(logs[0]), float(logs[1]))
        return np.array(
            [inverse[0] - inverse[1], inverse[0] - inverse[2]], dtype=float
        )

    solution = root(
        residual,
        [
            math.log(guess_ms / MZ),
            math.log(guess_mg / MZ),
        ],
        tol=1e-11,
    )
    if not solution.success:
        raise RuntimeError(f"two-loop root solve failed: {solution.message}")
    log_ms, log_mg = (float(solution.x[0]), float(solution.x[1]))
    inverse = run(log_ms, log_mg)
    return {
        "MS": MZ * math.exp(log_ms),
        "MG": MZ * math.exp(log_mg),
        "alphaU": 1.0 / float(inverse.mean()),
        "alphaU_inverse": float(inverse.mean()),
        "max_inverse_coupling_residual": float(inverse.max() - inverse.min()),
    }


def relative_differences(
    computed: Mapping[str, float], reference: Mapping[str, float]
) -> dict[str, float]:
    aliases = {"MQ": "MS", "M10": "MS"}
    result: dict[str, float] = {}
    for key, target in reference.items():
        source_key = aliases.get(key, key)
        if source_key not in computed:
            continue
        result[key] = abs(computed[source_key] / target - 1.0)
    return result


@lru_cache(maxsize=1)
def _two_loop_cached() -> dict[str, Any]:
    mv = martin_vaughn_derivation()
    tolerance = {
        "scale_relative": 1.0e-5,
        "coupling_relative": 1.0e-5,
        "inverse_residual_absolute": 1.0e-8,
    }
    try:
        import scipy  # noqa: F401

        orphan_raw = _solve_two_loop_common_threshold(
            B_ORPHAN,
            EXPECTED_ORPHAN_DELTA_B,
            4.760378e11,
            2.266291e15,
            False,
        )
        orphan_dr = _solve_two_loop_common_threshold(
            B_ORPHAN,
            EXPECTED_ORPHAN_DELTA_B,
            4.99199e11,
            2.36709e15,
            True,
        )
        full_ten = _solve_two_loop_common_threshold(
            B_FULL_TEN,
            EXPECTED_FULL_TEN_DELTA_B,
            1.383905e4,
            1.216382e16,
            False,
        )
        engine = "scipy solve_ivp(DOP853) plus root"
        executed = True
    except ImportError:
        orphan_raw = {
            "MS": PINNED_TWO_LOOP["orphan_only_raw_no_matching"]["MS"],
            "MG": PINNED_TWO_LOOP["orphan_only_raw_no_matching"]["MG"],
            "alphaU": PINNED_TWO_LOOP["orphan_only_raw_no_matching"]["alphaU"],
            "alphaU_inverse": 1
            / PINNED_TWO_LOOP["orphan_only_raw_no_matching"]["alphaU"],
            "max_inverse_coupling_residual": 0.0,
        }
        orphan_dr = {
            "MS": PINNED_TWO_LOOP[
                "orphan_only_universal_MSbar_to_DRbar"
            ]["MS"],
            "MG": PINNED_TWO_LOOP[
                "orphan_only_universal_MSbar_to_DRbar"
            ]["MG"],
            "alphaU_inverse": PINNED_TWO_LOOP[
                "orphan_only_universal_MSbar_to_DRbar"
            ]["alphaU_inverse"],
            "alphaU": 1
            / PINNED_TWO_LOOP[
                "orphan_only_universal_MSbar_to_DRbar"
            ]["alphaU_inverse"],
            "max_inverse_coupling_residual": 0.0,
        }
        full_ten = {
            "MS": PINNED_TWO_LOOP["full_ten_raw_no_matching"]["MS"],
            "MG": PINNED_TWO_LOOP["full_ten_raw_no_matching"]["MG"],
            "alphaU": PINNED_TWO_LOOP["full_ten_raw_no_matching"]["alphaU"],
            "alphaU_inverse": 1
            / PINNED_TWO_LOOP["full_ten_raw_no_matching"]["alphaU"],
            "max_inverse_coupling_residual": 0.0,
        }
        engine = "pinned precomputed diagnostics (SciPy unavailable)"
        executed = False

    raw_diff = relative_differences(
        orphan_raw, PINNED_TWO_LOOP["orphan_only_raw_no_matching"]
    )
    dr_diff = relative_differences(
        orphan_dr, PINNED_TWO_LOOP["orphan_only_universal_MSbar_to_DRbar"]
    )
    ten_diff = relative_differences(
        full_ten, PINNED_TWO_LOOP["full_ten_raw_no_matching"]
    )
    all_diffs = [*raw_diff.values(), *dr_diff.values(), *ten_diff.values()]
    max_residual = max(
        orphan_raw["max_inverse_coupling_residual"],
        orphan_dr["max_inverse_coupling_residual"],
        full_ten["max_inverse_coupling_residual"],
    )
    return {
        "equation": (
            "d alpha_a^-1/d ln(mu) = -b_a/(2pi) "
            "- sum_b B_ab alpha_b/(8pi^2)"
        ),
        "engine": engine,
        "numerical_integration_executed": executed,
        "matrix_derivation_bound": (
            mv["MSSM"]["reproduces_standard_B"]
            and mv["orphan_Q_pair"]["matches_required"]
            and mv["complete_10_plus_10bar"]["matches_required_B"]
        ),
        "tolerance_policy": tolerance,
        "orphan_only_raw_no_matching": {
            "computed": orphan_raw,
            "pinned_reference": PINNED_TWO_LOOP[
                "orphan_only_raw_no_matching"
            ],
            "relative_difference": raw_diff,
            "description": (
                "gauge-only two-loop running with a common MS=MQ threshold "
                "and no finite matching"
            ),
        },
        "orphan_only_universal_MSbar_to_DRbar": {
            "computed": orphan_dr,
            "pinned_reference": PINNED_TWO_LOOP[
                "orphan_only_universal_MSbar_to_DRbar"
            ],
            "relative_difference": dr_diff,
            "matching": (
                "alpha_a^-1,DR = alpha_a^-1,MS - C_a(G)/(12pi) at MS"
            ),
            "description": (
                "same gauge-only solve with only the universal one-loop "
                "MSbar-to-DRbar conversion"
            ),
        },
        "full_ten_raw_no_matching": {
            "computed": full_ten,
            "pinned_reference": PINNED_TWO_LOOP[
                "full_ten_raw_no_matching"
            ],
            "relative_difference": ten_diff,
            "description": (
                "gauge-only two-loop running with a common MS=M10 threshold "
                "for a vectorlike 10+10bar"
            ),
        },
        "diagnostics_within_tolerance": (
            max(all_diffs, default=0.0) <= tolerance["scale_relative"]
            and max_residual <= tolerance["inverse_residual_absolute"]
        ),
        "not_included": [
            "finite one-loop decoupling beyond the universal scheme conversion",
            "Yukawa and tan(beta) contributions",
            "soft-spectrum mass splittings",
            "Mc, M*, KK and brane-kinetic thresholds",
        ],
        "claim_boundary": (
            "these are gauge-only diagnostics, not precision unification fits"
        ),
    }


def two_loop_audit() -> dict[str, Any]:
    return copy.deepcopy(_two_loop_cached())


def regression_inventory() -> dict[str, Any]:
    pattern = re.compile(r"^test_susy_v(?:59|60|61|62|63|64|65).*\.py$")
    rows = []
    for path in sorted(ROOT.glob("test_susy_v*.py"), key=lambda p: p.name.lower()):
        if not pattern.match(path.name):
            continue
        count = len(
            re.findall(
                r"^\s*def\s+test_[A-Za-z0-9_]*\s*\(",
                path.read_text(encoding="utf-8"),
                flags=re.MULTILINE,
            )
        )
        rows.append({"path": path.name, "test_functions": count})
    omitted = "test_susy_v59_heterotic_corrected_z4r_data_sufficiency_audit.py"
    omitted_count = next(
        row["test_functions"] for row in rows if row["path"] == omitted
    )
    total = sum(row["test_functions"] for row in rows)
    return {
        "selection": "every test_susy_v59 through test_susy_v65 Python file",
        "files": rows,
        "file_count": len(rows),
        "current_full_test_count": total,
        "claimed_narrow_count": total - omitted_count,
        "omitted_file_in_199_run": omitted,
        "omitted_file_test_count": omitted_count,
        "full_suite_is_208_not_199": total == 208
        and total - omitted_count == 199,
    }


def gm_overlap_audit() -> dict[str, Any]:
    return {
        "general_supergravity_mass": (
            "mu_Q = [m_3/2 Z_Q - Fbar^I partial_bar_I Z_Q]"
            "/sqrt(Y_Q Y_Qbar)"
        ),
        "symbols": {
            "Z_Q": "hidden-sector-dependent Kahler bilinear coefficient",
            "Y_Q_and_Y_Qbar": "wave-function metrics of the two light chiral modes",
            "Fbar_I": "hidden-sector auxiliary expectation values",
        },
        "z4r_allows_charge_zero_bilinear": True,
        "nonzero_mass_constructed_in_bound_action": False,
        "reason_allowed_is_not_constructed": (
            "the bound action specifies neither Z_Q, its hidden-sector "
            "derivative, nor the SUSY-breaking F terms; symmetry permission "
            "does not prove a nonzero numerator"
        ),
        "v64_null_mode_normalization": {
            "alpha_squared": "alpha^2 = g5^2 v^2 L",
            "norm_squared": "1 + alpha^2",
            "local_y0_Kahler_term": "c_K C Cbar",
            "effective_bilinear": "Z_eff = c_K/(1+alpha^2)",
            "portal_amplitude_overlap": "1/sqrt(1+alpha^2)",
            "portal_rate_suppression": "1/(1+alpha^2)",
        },
        "consequence": (
            "both the GM mass coefficient and decay portals can be small or "
            "zero; V65 did not establish a mass or a fast decay"
        ),
        "V65_action_upgrade": "RETRACTED",
        "replacement_status": "CANDIDATE_CONDITIONAL_EXTENSION",
    }


def candidate_branches() -> list[dict[str, Any]]:
    return [
        {
            "id": "H66",
            "name": "high-scale SUSY orphan-only extension",
            "field_content": "MSSM plus the V64 Q-type orphan pair",
            "diagnostic": (
                "gauge-only two-loop common threshold MS=MQ about 4.76e11 GeV "
                "(about 4.99e11 GeV with the universal MSbar-to-DRbar shift)"
            ),
            "status": "CANDIDATE_CONDITIONAL_EXTENSION",
            "not_complete": True,
            "open": [
                "construct nonzero GM mass from an explicit hidden/Kahler sector",
                "compute suppressed portal lifetime and cosmology",
                "supply full matching, Yukawa, soft, KK and brane thresholds",
            ],
        },
        {
            "id": "T66",
            "name": "low-scale full-10 compensator extension",
            "new_fields": (
                "add Uc_X+U_X and Ec_X+E_X at the orphan threshold, completing "
                "a vectorlike SU(5) 10+10bar"
            ),
            "companion_Delta_b": ["14/5", "0", "1"],
            "total_Delta_b": ["3", "3", "3"],
            "diagnostic": (
                "gauge-only two-loop common threshold MS=M10 about 1.383905e4 "
                "GeV and MG about 1.216382e16 GeV"
            ),
            "status": "CANDIDATE_CONDITIONAL_EXTENSION",
            "not_complete": True,
            "missing": [
                "local Spin(11)/Spin(10) representation and wall embedding",
                "localized anomaly and Green-Schwarz recomputation",
                "Kahler and soft-sector construction",
                "precision thresholds and phenomenology",
            ],
            "baryon_safety": {
                "inherits_V65_claim": False,
                "reason": (
                    "the full 10 portal 10_X 5bar 5bar contains "
                    "Uc_X dc dc and Ec_X L L, so the orphan-only effective "
                    "B-L assignment does not prove safety for the completion"
                ),
            },
        },
    ]


def acceptance_criteria() -> list[dict[str, str]]:
    requirements = [
        (
            "A1",
            "full pole and running spectrum with every superpartner and exotic threshold",
        ),
        ("A2", "tan(beta) and all relevant Yukawa boundary conditions"),
        (
            "A3",
            "two-loop running plus complete one-loop decoupling and scheme matching",
        ),
        (
            "A4",
            "Mc, M*, the KK tower and brane-kinetic threshold corrections",
        ),
        (
            "A5",
            "physical threshold ordering, perturbativity and vacuum stability",
        ),
        (
            "A6",
            "three-coupling residual smaller than a quantified truncation uncertainty",
        ),
        (
            "A7",
            "explicit hidden/Kahler/soft sector producing nonzero mu_Q and acceptable B terms",
        ),
        (
            "A8",
            "for T66, local Spin(11)/Spin(10) embedding, anomaly/GS closure and baryon safety",
        ),
    ]
    return [
        {"id": identifier, "requirement": text, "status": "OPEN"}
        for identifier, text in requirements
    ]


def gate_ledger() -> list[dict[str, str]]:
    decisions = {
        "G1": (
            "OPEN: the current action is rejected; H66 and T66 are conditional "
            "extensions without complete microscopic actions"
        ),
        "G2": "OPEN: no complete flavor/KK determinant fit",
        "G3": "OPEN: no full vacuum and SUSY-breaking stabilization",
        "G4": "OPEN: no Dai-Freed/global anomaly computation for either extension",
        "G5": "OPEN: no controlled proton and baryon analysis for the full completion",
        "G6": "OPEN: only gauge-only unification diagnostics exist",
        "G7": "OPEN: no pole spectrum, lifetimes, relic or collider calculation",
        "G8": "OPEN: no UV regulator or quantified predictivity score",
    }
    return [
        {"gate": f"G{i}", "status": "OPEN", "decision": decisions[f"G{i}"]}
        for i in range(1, 9)
    ]


def terminal_decision() -> dict[str, Any]:
    return {
        "current_bound_action_status": "REJECTED",
        "V65_conditionally_viable_upgrade": "RETRACTED",
        "V64_null_mode_retraction_preserved": True,
        "WZ_term": "NONE_FORCED",
        "candidate_extensions": ["H66", "T66"],
        "candidate_extension_count": 2,
        "accepted_extension_count": 0,
        "V66_G1_closed": False,
        "closed_gates": [],
        "complete_theory": False,
        "honest_outcome": (
            "V66 converts the V65 claim into two quantitative but conditional "
            "research branches.  Allowed GM physics is not a constructed "
            "mass, and gauge-only crossing is not precision unification."
        ),
    }


def source_manifest() -> dict[str, Any]:
    local_paths = [
        Path(__file__).resolve(),
        TEST_PATH.resolve(),
        V65_ROUTE_PATH.resolve(),
        V65_MASTER_PATH.resolve(),
        V64_ROUTE_PATH.resolve(),
    ]
    return {
        "local_files": [
            {
                "path": str(path),
                "exists": path.is_file(),
                "sha256": sha256_file(path),
            }
            for path in local_paths
        ],
        "primary_sources": PRIMARY_SOURCES,
    }


def build_report() -> dict[str, Any]:
    v65_route = load_bound(
        V65_ROUTE_PATH, EXPECTED_V65_ROUTE_CORE, "V65 route"
    )
    v65_master = load_bound(
        V65_MASTER_PATH, EXPECTED_V65_MASTER_CORE, "V65 master"
    )
    v64_route = load_bound(
        V64_ROUTE_PATH, EXPECTED_V64_ROUTE_CORE, "V64 route"
    )
    regression = regression_inventory()
    gm = gm_overlap_audit()
    mv = martin_vaughn_derivation()
    one_loop = one_loop_audit()
    two_loop = two_loop_audit()
    branches = candidate_branches()
    acceptance = acceptance_criteria()
    gates = gate_ledger()
    terminal = terminal_decision()
    integrity = {
        "V65_route_core_bound": v65_route["core_sha256"]
        == EXPECTED_V65_ROUTE_CORE,
        "V65_master_core_bound": v65_master["core_sha256"]
        == EXPECTED_V65_MASTER_CORE,
        "V64_null_mode_core_bound": v64_route["core_sha256"]
        == EXPECTED_V64_ROUTE_CORE,
        "regression_scope_corrected": regression["full_suite_is_208_not_199"],
        "GM_allowed_not_constructed": gm["z4r_allows_charge_zero_bilinear"]
        and not gm["nonzero_mass_constructed_in_bound_action"],
        "V65_upgrade_retracted": gm["V65_action_upgrade"] == "RETRACTED",
        "MSSM_B_reproduced": mv["MSSM"]["reproduces_standard_B"],
        "orphan_Delta_B_exact": mv["orphan_Q_pair"]["matches_required"],
        "full_ten_Delta_b_universal": mv["complete_10_plus_10bar"][
            "one_loop_shift_is_universal"
        ],
        "one_loop_exact_residual": one_loop["c_equals_1"][
            "max_inverse_coupling_residual"
        ]
        < 1e-10,
        "two_loop_diagnostics_match_pins": two_loop[
            "diagnostics_within_tolerance"
        ],
        "two_candidates_neither_accepted": len(branches) == 2
        and all(row["not_complete"] for row in branches),
        "all_acceptance_criteria_open": all(
            row["status"] == "OPEN" for row in acceptance
        ),
        "all_gates_open": all(row["status"] == "OPEN" for row in gates),
        "current_action_rejected": terminal["current_bound_action_status"]
        == "REJECTED",
        "no_WZ_forced": terminal["WZ_term"] == "NONE_FORCED",
    }
    report: dict[str, Any] = {
        "schema": "susy_so10.v66.spin11_gm_overlap_unification_repair_audit.v1",
        "version": "V66",
        "date": "2026-08-30",
        "status": STATUS,
        "classification": CLASSIFICATION,
        "lineage": {
            "bound_V65_route_core": v65_route["core_sha256"],
            "bound_V65_master_core": v65_master["core_sha256"],
            "bound_V64_null_mode_route_core": v64_route["core_sha256"],
            "relation": (
                "route-B66 correction: V65 files remain valid immutable "
                "artifacts, but its inference from allowed GM charge to a "
                "constructed lift is retracted"
            ),
        },
        "V65_integrity_scope_correction": regression,
        "gm_overlap_and_retraction": gm,
        "martin_vaughn_group_theory": mv,
        "one_loop_threshold_solution": one_loop,
        "two_loop_gauge_only_diagnostics": two_loop,
        "candidate_extensions": branches,
        "acceptance_criteria": acceptance,
        "falsifiers": [
            "an explicit normalized Kahler/hidden sector yields identically zero mu_Q",
            "precision thresholds cannot make any candidate satisfy three-coupling unification",
            "the T66 local embedding has an uncancelled localized/global anomaly",
            "the required T66 portals generate excluded baryon violation",
            "either candidate violates perturbativity or vacuum stability before MG",
        ],
        "gate_ledger": gates,
        "terminal_decision": terminal,
        "claim_boundary": {
            "new_physics_status": "CANDIDATE_ONLY",
            "no_empirical_discovery": True,
            "no_precision_unification_claim": True,
            "no_gate_promotion": True,
        },
        "integrity_checks": integrity,
        "n_integrity_checks": len(integrity),
        "n_failed_integrity_checks": sum(not value for value in integrity.values()),
        "source_manifest": source_manifest(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def _require_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise RuntimeError(f"V66 recomputation mismatch: {label}")


def validate(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("V66 canonical core mismatch")
    _require_equal(
        report.get("schema"),
        "susy_so10.v66.spin11_gm_overlap_unification_repair_audit.v1",
        "schema",
    )
    _require_equal(report.get("version"), "V66", "version")
    _require_equal(report.get("date"), "2026-08-30", "date")
    _require_equal(report.get("status"), STATUS, "status")
    _require_equal(report.get("classification"), CLASSIFICATION, "classification")

    v65_route = load_bound(
        V65_ROUTE_PATH, EXPECTED_V65_ROUTE_CORE, "V65 route"
    )
    v65_master = load_bound(
        V65_MASTER_PATH, EXPECTED_V65_MASTER_CORE, "V65 master"
    )
    v64_route = load_bound(
        V64_ROUTE_PATH, EXPECTED_V64_ROUTE_CORE, "V64 route"
    )
    expected_lineage = {
        "bound_V65_route_core": v65_route["core_sha256"],
        "bound_V65_master_core": v65_master["core_sha256"],
        "bound_V64_null_mode_route_core": v64_route["core_sha256"],
        "relation": (
            "route-B66 correction: V65 files remain valid immutable "
            "artifacts, but its inference from allowed GM charge to a "
            "constructed lift is retracted"
        ),
    }
    _require_equal(report.get("lineage"), expected_lineage, "lineage")
    _require_equal(
        report.get("V65_integrity_scope_correction"),
        regression_inventory(),
        "regression inventory",
    )
    _require_equal(
        report.get("gm_overlap_and_retraction"),
        gm_overlap_audit(),
        "GM overlap",
    )
    _require_equal(
        report.get("martin_vaughn_group_theory"),
        martin_vaughn_derivation(),
        "Martin-Vaughn derivation",
    )
    _require_equal(
        report.get("one_loop_threshold_solution"),
        one_loop_audit(),
        "one-loop solve",
    )
    _require_equal(
        report.get("two_loop_gauge_only_diagnostics"),
        two_loop_audit(),
        "two-loop diagnostics",
    )
    _require_equal(
        report.get("candidate_extensions"),
        candidate_branches(),
        "candidate branches",
    )
    _require_equal(
        report.get("acceptance_criteria"),
        acceptance_criteria(),
        "acceptance criteria",
    )
    _require_equal(report.get("gate_ledger"), gate_ledger(), "gate ledger")
    _require_equal(
        report.get("terminal_decision"), terminal_decision(), "terminal decision"
    )
    _require_equal(report.get("source_manifest"), source_manifest(), "source manifest")

    expected_integrity = build_report()["integrity_checks"]
    _require_equal(
        report.get("integrity_checks"), expected_integrity, "integrity checks"
    )
    _require_equal(
        report.get("n_integrity_checks"),
        len(expected_integrity),
        "integrity-check count",
    )
    _require_equal(
        report.get("n_failed_integrity_checks"),
        sum(not value for value in expected_integrity.values()),
        "failed-integrity count",
    )
    if any(not value for value in expected_integrity.values()):
        failed = [key for key, value in expected_integrity.items() if not value]
        raise RuntimeError(f"V66 integrity failures: {failed}")


def render_markdown(report: Mapping[str, Any]) -> str:
    gm = report["gm_overlap_and_retraction"]
    one = report["one_loop_threshold_solution"]
    two = report["two_loop_gauge_only_diagnostics"]
    mv = report["martin_vaughn_group_theory"]
    regression = report["V65_integrity_scope_correction"]
    raw = two["orphan_only_raw_no_matching"]["computed"]
    dr = two["orphan_only_universal_MSbar_to_DRbar"]["computed"]
    ten = two["full_ten_raw_no_matching"]["computed"]
    lines = [
        "# SUSY V66 Spin(11) GM-overlap and unification repair audit",
        "",
        f"Status: {report['status']}",
        "",
        f"Canonical core: {report['core_sha256']}",
        "",
        "## Decision",
        "",
        (
            "The current V65 action is REJECTED. Its immutable files and cores "
            "remain valid, but the upgrade to conditionally viable is retracted: "
            "Z4R permits a Giudice-Masiero bilinear, yet the bound action does "
            "not construct its coefficient or hidden-sector F terms. V64's "
            "normalizable orphan mode and the no-WZ correction are preserved. "
            "G1-G8 remain OPEN."
        ),
        "",
        "Two research branches survive only as conditional extensions: a "
        "high-scale orphan-only branch and a low-scale full-10 compensator.",
        "",
        "## Regression-scope correction",
        "",
        (
            f"The current complete V59-V65 selection contains "
            f"{regression['file_count']} files and "
            f"{regression['current_full_test_count']} tests. The 199-test run "
            f"omitted {regression['omitted_file_in_199_run']}, which contains "
            f"{regression['omitted_file_test_count']} tests."
        ),
        "",
        "## GM overlap: allowed is not constructed",
        "",
        gm["general_supergravity_mass"],
        "",
        gm["reason_allowed_is_not_constructed"] + ".",
        "",
        "The V64 null-mode normalization gives:",
        "",
        f"- {gm['v64_null_mode_normalization']['alpha_squared']}",
        f"- {gm['v64_null_mode_normalization']['norm_squared']}",
        f"- {gm['v64_null_mode_normalization']['effective_bilinear']}",
        f"- portal amplitude: {gm['v64_null_mode_normalization']['portal_amplitude_overlap']}",
        "",
        "## Exact one-loop threshold solution",
        "",
        (
            "The conventional beta-function order is (b1,b2,b3). The orphan "
            "pair has Delta b = (1/5,3,2). For c=MQ/MS:"
        ),
        "",
        f"- MS = {one['analytic_c_family']['MS']}",
        f"- MQ = {one['analytic_c_family']['MQ']}",
        f"- MG = {one['analytic_c_family']['MG']}",
        f"- alphaU^-1 = {one['analytic_c_family']['alphaU_inverse']}",
        "",
        (
            f"At c=1 the direct solve gives MS=MQ="
            f"{one['c_equals_1']['MS_GeV']:.9e} GeV, "
            f"MG={one['c_equals_1']['MG_GeV']:.9e} GeV and "
            f"alphaU^-1={one['c_equals_1']['alphaU_inverse']:.8f}."
        ),
        (
            f"At MS=1 TeV it instead requires MQ="
            f"{one['fixed_MS_1_TeV']['MQ_GeV']:.9e} GeV and "
            f"MG={one['fixed_MS_1_TeV']['MG_GeV']:.9e} GeV."
        ),
        "",
        "## Martin-Vaughn exact gauge coefficients",
        "",
        f"MSSM B = {mv['MSSM']['B']}",
        "",
        f"Orphan Delta B_Q = {mv['orphan_Q_pair']['Delta_B']}",
        "",
        f"Companion Delta b = {mv['Uc_and_Ec_companions']['Delta_b']}.",
        (
            " Together with Q this gives a complete 10+10bar with "
            f"Delta b = {mv['complete_10_plus_10bar']['Delta_b']}."
        ),
        "",
        "## Gauge-only two-loop diagnostics",
        "",
        (
            f"Raw orphan-only: MS=MQ={raw['MS']:.9e} GeV, "
            f"MG={raw['MG']:.9e} GeV, alphaU={raw['alphaU']:.8f}."
        ),
        (
            f"With only the universal MSbar-to-DRbar shift: MS=MQ="
            f"{dr['MS']:.9e} GeV, MG={dr['MG']:.9e} GeV, "
            f"alphaU^-1={dr['alphaU_inverse']:.6f}."
        ),
        (
            f"Full 10+10bar raw diagnostic: MS=M10={ten['MS']:.9e} GeV, "
            f"MG={ten['MG']:.9e} GeV, alphaU={ten['alphaU']:.8f}."
        ),
        "",
        (
            "These are diagnostics only. Finite decoupling, Yukawas, soft "
            "splittings, KK thresholds and brane kinetic terms are absent."
        ),
        "",
        "## Why the full-10 candidate is not accepted",
        "",
        (
            "Its local Spin(11)/Spin(10) embedding, localized anomaly/GS "
            "closure and Kahler/soft sector are absent. Moreover the full "
            "10_X 5bar 5bar portal contains Uc_X dc dc and Ec_X L L. The "
            "orphan-only V65 baryon-safety assignment therefore does not "
            "extend to this completion."
        ),
        "",
        "## Fail-closed acceptance criteria",
        "",
    ]
    lines.extend(
        f"- {row['id']} [{row['status']}]: {row['requirement']}"
        for row in report["acceptance_criteria"]
    )
    lines.extend(["", "## Gate ledger", ""])
    lines.extend(
        f"- {row['gate']} [{row['status']}]: {row['decision']}"
        for row in report["gate_ledger"]
    )
    lines.extend(
        [
            "",
            "No gate is promoted. No Wess-Zumino term is forced.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write JSON and Markdown")
    parser.add_argument("--check", action="store_true", help="verify generated artifacts")
    parser.add_argument("--emit-json", action="store_true", help="print generated JSON")
    parser.add_argument(
        "--emit-markdown", action="store_true", help="print generated Markdown"
    )
    args = parser.parse_args()
    report = build_report()
    validate(report)
    if args.write:
        write_outputs(report)
    if args.check:
        if not JSON_PATH.is_file() or not MD_PATH.is_file():
            raise RuntimeError("generated V66 route artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("generated V66 route JSON is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("generated V66 route Markdown is stale")
    if args.emit_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.emit_markdown:
        print(render_markdown(report), end="")
    else:
        print(report["status"])
        print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
