#!/usr/bin/env python3
"""V54 Q4 flavour benchmark reconstruction and modern-data stress test.

This audit reconstructs the Babu--Pati--Tavartkiladze charged-lepton,
neutrino-Dirac, and right-handed-Majorana textures of arXiv:1003.2625.  It
first fixes the matrix convention by reproducing the published 2010 neutrino
benchmark.  It then compares that frozen point with the official NuFIT 6.1
IC24+SK normal-ordering 3-sigma ranges and performs a deterministic, bounded
four-seed search in the two complex Majorana texture parameters.

The numerical search is deliberately a no-fit audit, not a global theorem.
It holds the charged sector and Dirac texture fixed, omits a fresh RG and
threshold calculation, and searches only the declared finite box.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import scipy
from scipy.optimize import differential_evolution


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V54_Q4_FLAVOUR_MODERN_DATA_AUDIT.json"
MD_PATH = ROOT / "SUSY_V54_Q4_FLAVOUR_MODERN_DATA_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v54_q4_flavour_modern_data_audit.py"
UPSTREAM = ROOT / "SUSY_V54_ANOMALOUS_U1A_BLUEPRINT_AUDIT.json"
EXPECTED_UPSTREAM_CORE = "59bc36c4899a6ca2985bfa8d9cdbad927d6c33fc3ef326daf9e39c280589b1c7"

STATUS = (
    "V54_Q4_FLAVOUR_MODERN_DATA_AUDIT__BPT_EQ16_EQ19_RECONSTRUCTED__"
    "PUBLISHED_2010_NEUTRINO_BENCHMARK_REPRODUCED__FROZEN_BENCHMARK_"
    "EXCLUDED_BY_NUFIT61_3SIGMA__FOUR_SEED_BOUNDED_AB_NO_FIT__"
    "NOT_A_GLOBAL_TEXTURE_THEOREM__CHARGED_SECTOR_RG_AND_THRESHOLDS_OPEN__"
    "G8_NOT_PROMOTED"
)

SEARCH_BOUNDS = (
    (-12.0, 4.0),
    (-math.pi, math.pi),
    (-25.0, 4.0),
    (-math.pi, math.pi),
)
SEARCH_SEEDS = (1729, 2718, 31415, 65537)
SEARCH_SETTINGS = {
    "method": "scipy.optimize.differential_evolution",
    "population_multiplier": 16,
    "maximum_iterations": 400,
    "relative_tolerance": 1.0e-10,
    "absolute_tolerance": 1.0e-10,
    "polish": True,
    "updating": "immediate",
    "workers": 1,
}

SIGMA = 0.0508
EPSILON = complex(-0.0188, 0.0333)
EPSILON_BAR = complex(0.106, 0.0754)
EPSILON_PRIME = 1.56e-4
ETA_PRIME = complex(-0.00474, 0.00177)
XI22_D = 0.014 * np.exp(4.1j)
BENCHMARK_A = 0.0252 * np.exp(-0.018j)
BENCHMARK_B = 1.61e-6 * np.exp(-1.592j)
BENCHMARK_M0_GEV = 1.89e13

# Official NuFIT 6.1 (2025), IC24 with SK atmospheric data, normal ordering.
NUFIT61_RANGES = {
    "theta12_deg": (32.54, 35.03),
    "theta23_deg": (41.27, 49.86),
    "theta13_deg": (8.26, 8.95),
    "delta_m21_sq_eV2": (7.236e-5, 7.823e-5),
    "delta_m31_sq_eV2": (2.450e-3, 2.576e-3),
}


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


def load_upstream() -> dict[str, Any]:
    value = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    if value.get("core_sha256") != canonical_sha(value):
        raise RuntimeError("stale V54 anomalous-U1A blueprint core")
    if value["core_sha256"] != EXPECTED_UPSTREAM_CORE:
        raise RuntimeError("unexpected V54 anomalous-U1A blueprint core")
    return value


def complex_record(value: complex, digits: int = 12) -> dict[str, float]:
    return {
        "real": round(float(np.real(value)), digits),
        "imag": round(float(np.imag(value)), digits),
    }


def complex_matrix_records(matrix: np.ndarray) -> list[list[dict[str, float]]]:
    return [[complex_record(value) for value in row] for row in matrix]


def charged_lepton_matrix() -> np.ndarray:
    """Eq. (16), kappa_e=3, in the paper's (e^c rows, e columns) order."""
    return np.array(
        [
            [0.0, 3.0 * EPSILON_PRIME + ETA_PRIME, 0.0],
            [-3.0 * EPSILON_PRIME - ETA_PRIME, 3.0 * XI22_D, SIGMA + 3.0 * EPSILON],
            [0.0, SIGMA + 3.0 * EPSILON_BAR, 1.0],
        ],
        dtype=np.complex128,
    )


def neutrino_dirac_matrix() -> np.ndarray:
    """Eq. (16) up texture after epsilon-prime -> -3 epsilon-prime."""
    return np.array(
        [
            [0.0, -3.0 * EPSILON_PRIME, 0.0],
            [3.0 * EPSILON_PRIME, 0.0, SIGMA],
            [0.0, SIGMA, 1.0],
        ],
        dtype=np.complex128,
    )


def majorana_matrix(a: complex, b: complex) -> np.ndarray:
    """Dimensionless Eq. (19); its overall M0 cancels from this audit."""
    return np.array(
        [[b, 0.0, 0.0], [0.0, b, a], [0.0, a, 1.0]],
        dtype=np.complex128,
    )


@lru_cache(maxsize=1)
def charged_lepton_left_basis() -> np.ndarray:
    # Eq. (16) labels the charged-lepton columns as e_L and rows as e^c.
    # Consequently the physical left basis diagonalizes M_e^dagger M_e.
    hermitian = charged_lepton_matrix().conj().T @ charged_lepton_matrix()
    _, vectors = np.linalg.eigh(hermitian)
    return vectors


def neutrino_observables(a: complex, b: complex) -> dict[str, Any]:
    md = neutrino_dirac_matrix()
    mr = majorana_matrix(a, b)
    # The irrelevant overall sign and (m_U^0)^2/M0 scale are omitted.
    light = md @ np.linalg.solve(mr, md.T)
    mass_sq, u_nu = np.linalg.eigh(light.conj().T @ light)
    ordering = np.argsort(mass_sq)
    mass_sq = np.maximum(np.real(mass_sq[ordering]), 0.0)
    u_nu = u_nu[:, ordering]
    pmns = charged_lepton_left_basis().conj().T @ u_nu

    theta13 = math.degrees(math.asin(float(np.clip(abs(pmns[0, 2]), 0.0, 1.0))))
    theta12 = math.degrees(math.atan2(abs(pmns[0, 1]), abs(pmns[0, 0])))
    theta23 = math.degrees(math.atan2(abs(pmns[1, 2]), abs(pmns[2, 2])))
    denominator = mass_sq[2] - mass_sq[0]
    if denominator <= 0.0:
        raise FloatingPointError("non-normal neutrino mass ordering")
    splitting_ratio = math.sqrt(max(0.0, (mass_sq[1] - mass_sq[0]) / denominator))

    return {
        "theta12_deg": float(theta12),
        "theta23_deg": float(theta23),
        "theta13_deg": float(theta13),
        "sqrt_delta_m21_sq_over_delta_m31_sq": float(splitting_ratio),
        "dimensionless_mass_singular_values": [
            float(math.sqrt(value)) for value in mass_sq
        ],
        "pmns_moduli": [[float(abs(value)) for value in row] for row in pmns],
    }


def ratio_range_from_nufit() -> tuple[float, float]:
    dm21 = NUFIT61_RANGES["delta_m21_sq_eV2"]
    dm31 = NUFIT61_RANGES["delta_m31_sq_eV2"]
    return math.sqrt(dm21[0] / dm31[1]), math.sqrt(dm21[1] / dm31[0])


def four_observable_ranges() -> tuple[tuple[float, float], ...]:
    return (
        NUFIT61_RANGES["theta12_deg"],
        NUFIT61_RANGES["theta23_deg"],
        NUFIT61_RANGES["theta13_deg"],
        ratio_range_from_nufit(),
    )


def observable_vector(a: complex, b: complex) -> np.ndarray:
    obs = neutrino_observables(a, b)
    return np.array(
        [
            obs["theta12_deg"],
            obs["theta23_deg"],
            obs["theta13_deg"],
            obs["sqrt_delta_m21_sq_over_delta_m31_sq"],
        ],
        dtype=float,
    )


def decode_search_point(point: Sequence[float]) -> tuple[complex, complex]:
    log_abs_a, arg_a, log_abs_b, arg_b = map(float, point)
    return (
        complex(np.exp(log_abs_a + 1j * arg_a)),
        complex(np.exp(log_abs_b + 1j * arg_b)),
    )


def outside_interval_components(values: Sequence[float]) -> list[dict[str, float | bool]]:
    rows: list[dict[str, float | bool]] = []
    for value, (low, high) in zip(values, four_observable_ranges(), strict=True):
        half_width = 0.5 * (high - low)
        if value < low:
            signed_distance = value - low
        elif value > high:
            signed_distance = value - high
        else:
            signed_distance = 0.0
        normalized = signed_distance / half_width
        rows.append(
            {
                "value": float(value),
                "low": float(low),
                "high": float(high),
                "inside": bool(low <= value <= high),
                "signed_distance_to_interval": float(signed_distance),
                "normalized_outside_distance": float(normalized),
                "squared_contribution": float(normalized * normalized),
            }
        )
    return rows


def objective_from_values(values: Sequence[float]) -> float:
    return float(sum(row["squared_contribution"] for row in outside_interval_components(values)))


def search_objective(point: Sequence[float]) -> float:
    try:
        a, b = decode_search_point(point)
        values = observable_vector(a, b)
        if not np.all(np.isfinite(values)):
            return 1.0e12
        return objective_from_values(values)
    except (FloatingPointError, np.linalg.LinAlgError, ValueError):
        return 1.0e12


def rounded_search_run(seed: int) -> dict[str, Any]:
    result = differential_evolution(
        search_objective,
        SEARCH_BOUNDS,
        seed=seed,
        popsize=SEARCH_SETTINGS["population_multiplier"],
        maxiter=SEARCH_SETTINGS["maximum_iterations"],
        tol=SEARCH_SETTINGS["relative_tolerance"],
        atol=SEARCH_SETTINGS["absolute_tolerance"],
        polish=SEARCH_SETTINGS["polish"],
        updating=SEARCH_SETTINGS["updating"],
        workers=SEARCH_SETTINGS["workers"],
    )
    point = np.asarray(result.x, dtype=float)
    a, b = decode_search_point(point)
    values = observable_vector(a, b)
    labels = (
        "theta12_deg",
        "theta23_deg",
        "theta13_deg",
        "sqrt_delta_m21_sq_over_delta_m31_sq",
    )
    return {
        "seed": seed,
        "objective": round(float(result.fun), 6),
        "point": {
            "log_abs_a": round(float(point[0]), 8),
            "arg_a": round(float(point[1]), 8),
            "log_abs_b": round(float(point[2]), 8),
            "arg_b": round(float(point[3]), 8),
        },
        "a": complex_record(a),
        "b": complex_record(b),
        "observables": {
            label: round(float(value), 8) for label, value in zip(labels, values, strict=True)
        },
        "iterations": int(result.nit),
        "function_evaluations": int(result.nfev),
        "optimizer_success": bool(result.success),
        "optimizer_message": str(result.message),
        "feasible": bool(float(result.fun) <= 1.0e-12),
    }


@lru_cache(maxsize=1)
def bounded_refit_search() -> tuple[dict[str, Any], ...]:
    return tuple(rounded_search_run(seed) for seed in SEARCH_SEEDS)


def rounded_observables(a: complex, b: complex) -> dict[str, Any]:
    raw = neutrino_observables(a, b)
    return {
        key: [round(float(item), 10) for item in value]
        if key == "dimensionless_mass_singular_values"
        else [[round(float(item), 10) for item in row] for row in value]
        if key == "pmns_moduli"
        else round(float(value), 10)
        for key, value in raw.items()
    }


def build_report() -> dict[str, Any]:
    upstream = load_upstream()
    benchmark = rounded_observables(BENCHMARK_A, BENCHMARK_B)
    benchmark_values = np.array(
        [
            benchmark["theta12_deg"],
            benchmark["theta23_deg"],
            benchmark["theta13_deg"],
            benchmark["sqrt_delta_m21_sq_over_delta_m31_sq"],
        ],
        dtype=float,
    )
    benchmark_components = outside_interval_components(benchmark_values)
    search_runs = list(bounded_refit_search())
    best_run = min(search_runs, key=lambda row: row["objective"])
    ratio_range = ratio_range_from_nufit()

    published_inputs = {
        "sigma": SIGMA,
        "epsilon": complex_record(EPSILON),
        "epsilon_bar": complex_record(EPSILON_BAR),
        "epsilon_prime": EPSILON_PRIME,
        "eta_prime": complex_record(ETA_PRIME),
        "xi22_d": {
            "magnitude": 0.014,
            "phase_rad": 4.1,
            "cartesian": complex_record(XI22_D),
        },
        "a": {
            "magnitude": 0.0252,
            "phase_rad": -0.018,
            "cartesian": complex_record(BENCHMARK_A),
        },
        "b": {
            "magnitude": 1.61e-6,
            "phase_rad": -1.592,
            "cartesian": complex_record(BENCHMARK_B),
        },
        "M0_GeV": BENCHMARK_M0_GEV,
    }

    integrity = {
        "V54_BPT_blueprint_is_bound": upstream["core_sha256"] == EXPECTED_UPSTREAM_CORE,
        "published_Eq16_and_Eq19_inputs_are_exact": (
            SIGMA == 0.0508
            and EPSILON == complex(-0.0188, 0.0333)
            and EPSILON_BAR == complex(0.106, 0.0754)
            and EPSILON_PRIME == 1.56e-4
            and ETA_PRIME == complex(-0.00474, 0.00177)
            and BENCHMARK_M0_GEV == 1.89e13
        ),
        "correct_matrix_convention_reproduces_published_angles": (
            abs(benchmark["theta12_deg"] - 29.90695238) < 1.0e-6
            and abs(benchmark["theta23_deg"] - 42.52900076) < 1.0e-6
            and abs(benchmark["theta13_deg"] - 3.57896136) < 1.0e-6
        ),
        "correct_splitting_definition_reproduces_published_ratio": abs(
            benchmark["sqrt_delta_m21_sq_over_delta_m31_sq"] - 0.12813379
        )
        < 1.0e-7,
        "NuFIT61_ratio_interval_is_derived_from_absolute_ranges": (
            abs(ratio_range[0] - math.sqrt(7.236e-5 / 2.576e-3)) < 1.0e-15
            and abs(ratio_range[1] - math.sqrt(7.823e-5 / 2.450e-3)) < 1.0e-15
        ),
        "only_theta23_of_frozen_benchmark_is_inside_current_intervals": [
            row["inside"] for row in benchmark_components
        ]
        == [False, True, False, False],
        "four_fixed_seeds_were_run": [row["seed"] for row in search_runs]
        == list(SEARCH_SEEDS),
        "bounded_search_reproduces_known_no_fit_minimum": abs(
            float(best_run["objective"]) - 141.065166
        )
        < 1.0e-3,
        "no_bounded_search_run_is_feasible": not any(
            row["feasible"] for row in search_runs
        ),
        "bounded_no_fit_is_not_promoted_to_global_theorem": True,
        "G8_is_not_promoted": True,
    }

    report: dict[str, Any] = {
        "schema": "susy-v54-q4-flavour-modern-data-audit-v1",
        "status": STATUS,
        "upstream": {
            "path": UPSTREAM.name,
            "core_sha256": upstream["core_sha256"],
            "binding_reason": (
                "This flavour audit is bound to the stable V54 anomalous-U1A BPT-style "
                "blueprint core; that upstream core transitively binds the V53 master."
            ),
        },
        "published_texture": {
            "source": "arXiv:1003.2625, Eqs. (16) and (19)",
            "inputs": published_inputs,
            "charged_lepton_symbolic": [
                ["0", "3 epsilon_prime + eta_prime", "0"],
                ["-3 epsilon_prime - eta_prime", "3 xi22_d", "sigma + 3 epsilon"],
                ["0", "sigma + 3 epsilon_bar", "1"],
            ],
            "neutrino_Dirac_symbolic": [
                ["0", "-3 epsilon_prime", "0"],
                ["+3 epsilon_prime", "0", "sigma"],
                ["0", "sigma", "1"],
            ],
            "right_handed_Majorana_symbolic": [
                ["b", "0", "0"],
                ["0", "b", "a"],
                ["0", "a", "1"],
            ],
            "charged_lepton_numeric": complex_matrix_records(charged_lepton_matrix()),
            "neutrino_Dirac_numeric": complex_matrix_records(neutrino_dirac_matrix()),
            "right_handed_Majorana_numeric_without_M0": complex_matrix_records(
                majorana_matrix(BENCHMARK_A, BENCHMARK_B)
            ),
        },
        "diagonalization_convention": {
            "charged_lepton_left_basis": "ascending eigenvectors of M_e^dagger M_e",
            "light_neutrino_matrix": "m_nu = M_D M_R^{-1} M_D^T; overall sign and scale omitted",
            "neutrino_basis": "ascending eigenvectors of m_nu^dagger m_nu",
            "PMNS": "U_e^dagger U_nu",
            "angles": {
                "theta13": "asin(|U_e3|)",
                "theta12": "atan2(|U_e2|, |U_e1|)",
                "theta23": "atan2(|U_mu3|, |U_tau3|)",
            },
            "splitting_ratio": (
                "sqrt((m2^2-m1^2)/(m3^2-m1^2)); this is not the m2/m3 approximation"
            ),
        },
        "published_benchmark_reproduction": {
            "observables": benchmark,
            "paper_rounded_values": {
                "theta12_deg": 30.0,
                "theta23_deg": 43.0,
                "theta13_deg": 3.6,
                "m2_over_m3_approximation": 0.13,
            },
            "reproduction_success": True,
            "scope": (
                "This algebraic texture reconstruction reproduces the benchmark convention. "
                "It does not independently reproduce the paper's RG and right-handed-neutrino "
                "threshold evolution."
            ),
        },
        "modern_data": {
            "dataset": "NuFIT 6.1 (2025), IC24 with SK atmospheric data, normal ordering",
            "three_sigma_ranges": {
                key: list(value) for key, value in NUFIT61_RANGES.items()
            },
            "derived_scale_free_ratio_range": list(ratio_range),
            "ratio_derivation": (
                "Conservative independent-endpoint envelope: "
                "sqrt(dm21_low/dm31_high) to sqrt(dm21_high/dm31_low)."
            ),
        },
        "frozen_2010_benchmark_test": {
            "observable_order": [
                "theta12_deg",
                "theta23_deg",
                "theta13_deg",
                "sqrt_delta_m21_sq_over_delta_m31_sq",
            ],
            "components": benchmark_components,
            "objective": objective_from_values(benchmark_values),
            "inside_all_four": all(row["inside"] for row in benchmark_components),
            "excluded_at_independent_3sigma_range_level": True,
            "failed_observables": [
                name
                for name, row in zip(
                    (
                        "theta12_deg",
                        "theta23_deg",
                        "theta13_deg",
                        "sqrt_delta_m21_sq_over_delta_m31_sq",
                    ),
                    benchmark_components,
                    strict=True,
                )
                if not row["inside"]
            ],
            "decision_scope": (
                "Only this frozen 2010 parameter point is excluded here. This statement does "
                "not exclude the Q4 texture family or the wider BPT-style theory."
            ),
        },
        "bounded_refit": {
            "varied_parameters": ["log|a|", "arg(a)", "log|b|", "arg(b)"],
            "logarithm": "natural",
            "bounds": [list(pair) for pair in SEARCH_BOUNDS],
            "fixed_parameters": (
                "sigma, epsilon, epsilon_bar, epsilon_prime, eta_prime, xi22_d and all "
                "charged-sector conventions are fixed to the 2010 benchmark"
            ),
            "objective_definition": (
                "sum_i [d_i/(half-width_i)]^2, where d_i is zero inside an interval "
                "and the signed distance to its nearest endpoint outside"
            ),
            "settings": {**SEARCH_SETTINGS, "scipy_version": scipy.__version__},
            "seeds": list(SEARCH_SEEDS),
            "runs": search_runs,
            "best_run": best_run,
            "feasible_point_found": any(row["feasible"] for row in search_runs),
            "classification": "BOUNDED_NUMERICAL_NO_FIT",
            "not_a_global_theorem": True,
            "limitations": [
                "the finite four-dimensional search box is not the full complex parameter space",
                "four deterministic global-optimizer seeds do not certify a global minimum",
                "the charged-lepton and neutrino-Dirac textures were not refitted",
                "no updated GUT-to-low-energy RG or right-handed-neutrino threshold evolution was performed",
                "correlated NuFIT likelihood surfaces were replaced by independent 3-sigma intervals",
            ],
        },
        "gate_effect": {
            "G8": "OPEN_FROZEN_2010_POINT_EXCLUDED_BOUNDED_AB_REFIT_FOUND_NO_FEASIBLE_POINT",
            "promotions": [],
            "whole_theory_excluded": False,
        },
        "next_required_work": [
            "refit the charged-fermion texture and complex Majorana parameters jointly",
            "run current two-loop SUSY/GUT RG evolution with sequential right-handed-neutrino thresholds",
            "evaluate the correlated NuFIT likelihood rather than interval-only penalties",
            "reserve at least one flavour observable as a withheld prediction",
            "propagate the refitted Yukawas into the proton-decay Wilson calculation",
        ],
        "verdict": {
            "published_2010_benchmark_reproduced": True,
            "frozen_2010_benchmark_excluded": True,
            "bounded_ab_refit_feasible": False,
            "texture_globally_excluded": False,
            "complete_flavour_theory": False,
            "statement": (
                "The published convention is reproducible, but the frozen 2010 point misses "
                "the current theta12, theta13, and mass-splitting-ratio 3-sigma intervals. "
                "A deterministic four-seed search varying only complex a and b found no "
                "feasible point in the declared box. That numerical no-fit is evidence "
                "against this frozen subspace, not a theorem against the Q4 texture: an "
                "updated charged-sector plus RG/threshold refit remains open."
            ),
        },
        "primary_sources": [
            {
                "title": "Babu, Pati, Tavartkiladze (2010), arXiv:1003.2625",
                "url": "https://arxiv.org/abs/1003.2625",
                "use": "Eqs. (16), (19), and the published benchmark",
            },
            {
                "title": "NuFIT 6.0 analysis paper, arXiv:2410.05380",
                "url": "https://arxiv.org/abs/2410.05380",
                "use": "primary global-analysis methodology reference requested by NuFIT",
            },
            {
                "title": "NuFIT 6.1 official parameter table",
                "url": "https://www.nu-fit.org/sites/default/files/v61.tbl-parameters.pdf",
                "use": "IC24+SK normal-ordering 3-sigma ranges",
            },
        ],
        "integrity_checks": integrity,
        "n_failed_integrity_checks": sum(not value for value in integrity.values()),
        "source_manifest": [
            {"path": Path(__file__).name, "sha256": sha256_file(Path(__file__))},
            {"path": TEST_PATH.name, "sha256": sha256_file(TEST_PATH)},
            {"path": UPSTREAM.name, "sha256": sha256_file(UPSTREAM)},
        ],
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report["status"] != STATUS or report["core_sha256"] != canonical_sha(report):
        raise RuntimeError("status or core drift")
    if report["n_failed_integrity_checks"] or not all(report["integrity_checks"].values()):
        raise RuntimeError("integrity failure")
    if report["gate_effect"]["promotions"] or report["gate_effect"]["whole_theory_excluded"]:
        raise RuntimeError("bounded flavour result overpromoted")
    if report["verdict"]["texture_globally_excluded"]:
        raise RuntimeError("numerical no-fit mislabeled as global theorem")


def render_markdown(report: Mapping[str, Any]) -> str:
    benchmark = report["published_benchmark_reproduction"]["observables"]
    best = report["bounded_refit"]["best_run"]
    best_obs = best["observables"]
    ratio_range = report["modern_data"]["derived_scale_free_ratio_range"]
    return f"""# V54 Q4 flavour benchmark and modern-data audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Outcome

{report['verdict']['statement']}

## Reconstructed convention

The charged-lepton left basis is obtained from `M_e^dagger M_e`.  The light
Majorana matrix is `m_nu = M_D M_R^(-1) M_D^T`, its basis is obtained from
`m_nu^dagger m_nu`, and `U_PMNS = U_e^dagger U_nu`.  This removes a material
row/column ambiguity in Eq. (16).

At the published point the executable reconstruction gives:

- theta12 = `{benchmark['theta12_deg']:.6f}` degrees;
- theta23 = `{benchmark['theta23_deg']:.6f}` degrees;
- theta13 = `{benchmark['theta13_deg']:.6f}` degrees;
- sqrt(Delta m21^2 / Delta m31^2) =
  `{benchmark['sqrt_delta_m21_sq_over_delta_m31_sq']:.8f}`.

The last quantity uses the mass-squared differences, including nonzero m1; it
is not the approximate ratio m2/m3.

## NuFIT 6.1 check

The official IC24+SK normal-ordering 3-sigma ranges used here are theta12
`32.54--35.03` degrees, theta23 `41.27--49.86` degrees, theta13
`8.26--8.95` degrees, Delta m21^2 `(7.236--7.823)e-5 eV^2`, and Delta m31^2
`(2.450--2.576)e-3 eV^2`.  Their conservative scale-free ratio envelope is
`{ratio_range[0]:.8f}--{ratio_range[1]:.8f}`.

The frozen benchmark passes theta23 only; theta12, theta13, and the splitting
ratio are outside.  Thus the **frozen 2010 point**, and only that point at this
stage, is excluded by this independent-range test.

## Bounded refit

Four fixed-seed differential-evolution runs varied natural-log magnitudes and
phases over `log|a| in [-12,4]`, `arg(a) in [-pi,pi]`, `log|b| in [-25,4]`,
and `arg(b) in [-pi,pi]`.  The best normalized outside-interval objective was
`{best['objective']:.6f}`.  Its observables were theta12
`{best_obs['theta12_deg']:.5f}` degrees, theta23
`{best_obs['theta23_deg']:.5f}` degrees, theta13
`{best_obs['theta13_deg']:.5f}` degrees, and splitting ratio
`{best_obs['sqrt_delta_m21_sq_over_delta_m31_sq']:.8f}`.  No zero-objective
point was found.

This is a bounded numerical no-fit, not a global theorem.  The charged sector
was frozen, the RG and sequential-neutrino-threshold calculation was not
updated, and independent intervals replaced the correlated likelihood.  G8
therefore remains open.

Primary texture: https://arxiv.org/abs/1003.2625

NuFIT methodology: https://arxiv.org/abs/2410.05380

NuFIT 6.1 ranges: https://www.nu-fit.org/sites/default/files/v61.tbl-parameters.pdf
"""


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    validate(report)
    JSON_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> None:
    report = build_report()
    validate(report)
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if JSON_PATH.read_text(encoding="utf-8") != expected_json:
        raise RuntimeError("stale JSON")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("stale Markdown")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        report = write_artifacts()
        print(report["status"])
        print(report["core_sha256"])
    if args.check:
        check_artifacts()
        print("V54_Q4_FLAVOUR_MODERN_DATA_AUDIT_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
