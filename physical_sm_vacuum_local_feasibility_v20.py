#!/usr/bin/env python3
"""Fail-closed physical-SM vacuum rebuild and local-feasibility scout.

This module starts from the *standard* SO(10) embedding rather than the
formal ``U(1)_89`` stabilizer used by the historical G6 spectrum.  The target
is the rational point in the canonical 486-real chart

    Phi   = e_6789,
    H     = (e_8 + i e_9)/sqrt(2),
    Sigma = (z_0 z_1 z_2 z_3 z_4)/(20 sqrt(2)),
    S     = 1/(5 sqrt(2)),
    X     = 1/sqrt(2),

where ``z_k=e_(2k)+i e_(2k+1)``.  Equivalently, ``20 q`` is an integer
vector.  Exact integer tangent algebra proves that the SO(10) orbit has rank
36, adding gauged U(1)_X gives rank 37, and adding the accidental PQ tangent
gives rank 38.  The nine-dimensional SO(10) stabilizer is the standard
``su(3)_C + u(1)_em`` algebra.

The full 44-direction/51-parameter live G2 compiler is then evaluated at this
new target.  Its stationarity matrix reconstructs on a Q+sqrt(2)Q lattice;
the two mixed rows are split into their rational and sqrt(2) parts.  Exact
rational elimination has rank/nullity 15/36 and produces a rational
coefficient witness with V=-1.  This reconstruction is rebound to the live
compiler at machine precision.  Its complete 486-real Hessian has 38 symmetry
zero modes and a positive 448-dimensional transverse spectrum.  The Hessian
claim remains a float64 local-feasibility scout: a source-algebra derivation of
every reconstructed matrix entry and an exact PSD certificate remain open.

There is, however, a separate exact boundedness completion.  If
``R=q.q=2 K`` and ``R0=102/25``, then for any kappa>0

    W6 = kappa R (R-R0)^2

is gauge/PQ invariant, nonnegative, stationary at the target, and has the
rank-one PSD Hessian ``8 kappa R0 q q^T`` there.  Its positive ``kappa R^3``
leading term makes any finite renormalizable polynomial coercive.  This does
not prove the target is the global minimum by itself.

Finally, the universal degree-eight completion

    U = a(Vren+1)^2 + b ||grad Vren||^2

is exactly nonnegative and makes the stationary Vren=-1 target a global
minimum.  Its target Hessian is ``2b Hren^T Hren``.  Exact modular minors prove
rank 448 for the reconstructed rational Hren, with its kernel equal to the
38-dimensional symmetry span.  The application remains fail-closed because
the rational lattice was reconstructed from float64 compiler output rather
than derived entry-by-entry from source algebra, and all global zeros of U
have not been classified.  Therefore this artifact does not close G3, G4, or
G6.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import numpy as np

import exact_g6_sm_provenance_feasibility_v20 as provenance
import exact_gauged_u1x_physical_quotient_v20 as quotient
import gauged_u1x_g2_derivative_audit_v20 as g2_audit
import gauged_u1x_scalar_contract_v20 as scalar_contract
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_quadratic_family_derivatives_v20 as derivatives

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.json"
OUT_MD = ROOT / "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.md"

MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
STATUS = (
    "PHYSICAL_SM_RECONSTRUCTED_GLOBAL_EFT_CERTIFICATE__DIRECT_SOURCE_"
    "ALGEBRA_AND_GLOBAL_EQUALITY_ORBIT_OPEN"
)
TARGET_DENOMINATOR = 20
TARGET_NORM_SQUARED = Fraction(102, 25)
EXPECTED_SO10_ORBIT_RANK = 36
EXPECTED_GAUGE_ORBIT_RANK = 37
EXPECTED_FULL_SYMMETRY_ORBIT_RANK = 38
EXPECTED_TRANSVERSE_DIMENSION = 448
DIAGNOSTIC_FLOAT_SIGNIFICANT_DIGITS = 10
DIAGNOSTIC_ZERO_ABS_TOLERANCE = 1.0e-12
BLAS_DIAGNOSTIC_SCALAR_PATHS = (
    ("stationarity", "gradient_l2_norm"),
    ("Hessian", "minimum_full_eigenvalue"),
    ("Hessian", "minimum_transverse_eigenvalue"),
    ("Hessian", "maximum_eigenvalue"),
)
BLAS_DIAGNOSTIC_SECTOR_FIELDS = {
    (0, 0): ("minimum_transverse_eigenvalue", "maximum_eigenvalue"),
    (0, 9): ("minimum_transverse_eigenvalue", "maximum_eigenvalue"),
    (0, 36): ("minimum_transverse_eigenvalue", "maximum_eigenvalue"),
    (16, 1): ("minimum_transverse_eigenvalue", "maximum_eigenvalue"),
    (16, 4): ("minimum_transverse_eigenvalue", "maximum_eigenvalue"),
    (16, 16): ("minimum_transverse_eigenvalue", "maximum_eigenvalue"),
    # The (16,25) minimum was bitwise stable in the dual-BLAS replay.
    (16, 25): ("maximum_eigenvalue",),
    (36, 0): ("minimum_transverse_eigenvalue", "maximum_eigenvalue"),
    (36, 9): ("minimum_transverse_eigenvalue", "maximum_eigenvalue"),
    (40, 1): ("minimum_transverse_eigenvalue", "maximum_eigenvalue"),
    (40, 4): ("minimum_transverse_eigenvalue", "maximum_eigenvalue"),
    (40, 16): ("minimum_transverse_eigenvalue", "maximum_eigenvalue"),
}


def _blas_diagnostic_paths() -> frozenset[str]:
    scalar = {
        f"{group}.{field}" for group, field in BLAS_DIAGNOSTIC_SCALAR_PATHS
    }
    sector = {
        (
            "physical_sector_decomposition.sectors"
            f"[12C2_SU3={color},Q3_squared={charge}].{field}"
        )
        for (color, charge), fields in BLAS_DIAGNOSTIC_SECTOR_FIELDS.items()
        for field in fields
    }
    paths = frozenset(scalar | sector)
    if len(paths) != 27:
        raise ArithmeticError("BLAS diagnostic allowlist must contain 27 paths")
    return paths


BLAS_DIAGNOSTIC_PATHS = _blas_diagnostic_paths()


# The seed is the minimum-norm solution returned by a CVXPY/Clarabel search
# with H_transverse >= 0.1 I.  It is not itself treated as exact data.  Its
# free coordinates are rounded on one common rational lattice before exact
# stationarity elimination.
SDP_SEED: dict[str, float] = {
    "lambda::O03_B01_singlet_polynomial": -0.42479758136805407,
    "lambda::O04_B01_singlet_polynomial": -0.03726994675429551,
    "lambda::O05_B01_126bar_norm": 0.05245524389373779,
    "lambda::O06_B01_Hdag_H_norm": -0.7330225889040509,
    "lambda::O07_B01_Phi_norm": -1.0544553696577585,
    "lambda::O14_B01_Phi_Sigma_Sigmadag_cubic": -0.021347834673266234,
    "lambda::O17_B01_Phi_cubic": 2.8044339712152144e-06,
    "lambda::O20_B01_singlet_polynomial": 0.12628605124072922,
    "lambda::O22_B01_singlet_polynomial": -0.0022454290592824194,
    "lambda::O23_B01_singlet_polynomial": 1.2500431504981835,
    "lambda::O25_B01_126bar_norm": -0.005606266025714013,
    "lambda::O26_B01_126bar_norm": 0.0005794503507250415,
    "lambda::O27_B01_126bar_self_projectors": 1.6009634035141218e-08,
    "lambda::O27_B02_126bar_self_projectors": 0.039245497225237375,
    "lambda::O27_B03_126bar_self_projectors": 1.252422199753267,
    "lambda::O27_B04_126bar_self_projectors": 5.002422195980859,
    "lambda::O33_B01_Hdag_H_norm": 0.2161633707131353,
    "lambda::O34_B01_Hdag_H_norm": -0.004303167101683623,
    "lambda::O35_B01_H_Sigma_hermitian": 0.07773989815364239,
    "lambda::O35_B02_H_Sigma_hermitian": -0.0961540306654452,
    "lambda::O36_B01_H_self_quartics": 0.4303342296056108,
    "lambda::O36_B02_H_self_quartics": 0.18994957749679775,
    "lambda::O42_B01_Phi_norm": 0.08250519331588954,
    "lambda::O43_B01_Phi_norm": -0.007317486641213539,
    "lambda::O44_B01_Phi2_Sigma_projectors": 0.02786562460508182,
    "lambda::O44_B02_Phi2_Sigma_projectors": 0.006128825337186783,
    "lambda::O44_B03_Phi2_Sigma_projectors": 0.3327255754449676,
    "lambda::O44_B04_Phi2_Sigma_projectors": 0.17793684370858925,
    "lambda::O44_B05_Phi2_Sigma_projectors": -0.3550448820483179,
    "lambda::O44_B06_Phi2_Sigma_projectors": -0.189616093685798,
    "lambda::O46_B01_Phi2_HdagH_channels": 0.27549629681854804,
    "lambda::O46_B02_Phi2_HdagH_channels": -0.00015422963160085018,
    "lambda::O46_B03_Phi2_HdagH_channels": -0.050000337120663124,
    "lambda::O48_B01_Phi_self_quartics": 0.00022657713864052988,
    "lambda::O48_B02_Phi_self_quartics": 0.0008272951762417109,
    "lambda::O48_B03_Phi_self_quartics": -0.013083987497778424,
    "lambda::O48_B04_Phi_self_quartics": 0.0008098452811102214,
    "im::O38_B01_Phi_Hdag_Sigmadag": -4.697538838271263e-10,
    "im::O45_B01_Phi2_Hdag_Sigma_210_1050": 8.68118975522799e-10,
    "re::O15_B01_Phi_Hdag_Sigma": -5.443787590847515e-10,
    "re::O38_B01_Phi_Hdag_Sigmadag": -3.035297356995819e-09,
    "re::O45_B02_Phi2_Hdag_Sigma_210_1050": 2.7219007343176616e-10,
}


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def _canonicalize_blas_diagnostic_float(value: Any) -> float:
    """Return one deterministic, explicitly allowlisted BLAS diagnostic.

    The live local-feasibility scout uses LAPACK eigenvalue/norm routines whose
    last few bits can depend on the BLAS thread configuration.  Only the 27
    paths proven environment-sensitive by the dual-BLAS replay call this
    helper.  Exact ranks, nullities, rational certificates, reconstruction
    residuals, booleans, integer counts, and scope claims remain verbatim.
    Values already checked against the live scout's ``1e-12`` zero tolerance
    are serialized as ``0.0``.  Rounding the remaining diagnostic floats to
    ten significant digits is more than
    eight orders below the certified numerical transverse margin (greater
    than ``0.09``), while making the frozen report independent of BLAS
    scheduling and avoiding sensitivity near a fixed decimal-place boundary.
    Non-finite diagnostics are rejected rather than serialized.
    """
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, bool) or not isinstance(value, float):
        raise TypeError("allowlisted BLAS diagnostic must be a float")
    if not math.isfinite(value):
        raise ArithmeticError("non-finite live diagnostic cannot be frozen")
    if abs(value) < DIAGNOSTIC_ZERO_ABS_TOLERANCE:
        return 0.0
    rounded = float(format(value, f".{DIAGNOSTIC_FLOAT_SIGNIFICANT_DIGITS}g"))
    return 0.0 if rounded == 0.0 else rounded


def _canonicalize_live_blas_diagnostics(live: dict[str, Any]) -> dict[str, Any]:
    """Canonicalize only values computed by BLAS/LAPACK reductions.

    Lattice-recognition residuals and their ratios are deliberately excluded:
    they are deterministic evidence from scalar arithmetic, not backend-
    dependent eigensolver or norm diagnostics.
    """
    canonical = dict(live)
    stationarity = dict(canonical["stationarity"])
    stationarity["gradient_l2_norm"] = _canonicalize_blas_diagnostic_float(
        stationarity["gradient_l2_norm"]
    )
    canonical["stationarity"] = stationarity

    hessian = dict(canonical["Hessian"])
    for _group, key in BLAS_DIAGNOSTIC_SCALAR_PATHS[1:]:
        hessian[key] = _canonicalize_blas_diagnostic_float(hessian[key])
    canonical["Hessian"] = hessian

    decomposition = dict(canonical["physical_sector_decomposition"])
    identities = {
        (int(row["12C2_SU3"]), int(row["Q3_squared"]))
        for row in decomposition["sectors"]
    }
    if identities != set(BLAS_DIAGNOSTIC_SECTOR_FIELDS):
        raise ArithmeticError("physical-sector identity set drifted")
    sectors = []
    for source_sector in decomposition["sectors"]:
        sector = dict(source_sector)
        identity = (int(sector["12C2_SU3"]), int(sector["Q3_squared"]))
        for key in BLAS_DIAGNOSTIC_SECTOR_FIELDS[identity]:
            sector[key] = _canonicalize_blas_diagnostic_float(sector[key])
        sectors.append(sector)
    decomposition["sectors"] = sectors
    canonical["physical_sector_decomposition"] = decomposition
    return canonical


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(_jsonable(value), sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _portable_text_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def dependency_bindings() -> dict[str, Any]:
    """Bind every direct proof/compiler dependency by raw and portable hash."""
    modules = {
        provenance.__name__: Path(provenance.__file__).resolve(),
        quotient.__name__: Path(quotient.__file__).resolve(),
        g2_audit.__name__: Path(g2_audit.__file__).resolve(),
        scalar_contract.__name__: Path(scalar_contract.__file__).resolve(),
        potential.__name__: Path(potential.__file__).resolve(),
        chart.__name__: Path(chart.__file__).resolve(),
        derivatives.__name__: Path(derivatives.__file__).resolve(),
    }
    for owner in g2_audit._adapter_modules_by_family().values():
        modules[owner.__name__] = Path(owner.__file__).resolve()
    files = {
        path.name: path for path in modules.values()
    }
    for name in (
        "EXACT_G6_SM_PROVENANCE_FEASIBILITY_V20.json",
        "EXACT_GAUGED_U1X_PHYSICAL_QUOTIENT_V20.json",
        "GAUGED_U1X_G2_DERIVATIVE_AUDIT_V20.json",
        "GAUGED_U1X_SCALAR_CONTRACT_V20.json",
    ):
        files[name] = ROOT / name
    missing = sorted(name for name, path in files.items() if not path.is_file())
    if missing:
        raise FileNotFoundError(f"physical-SM proof dependencies missing: {missing}")
    bindings = {
        name: {
            "path": name,
            "raw_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "portable_lf_sha256": hashlib.sha256(
                _portable_text_bytes(path)
            ).hexdigest(),
        }
        for name, path in sorted(files.items())
    }
    frozen_provenance = json.loads(
        (ROOT / "EXACT_G6_SM_PROVENANCE_FEASIBILITY_V20.json").read_text(
            encoding="utf-8"
        )
    )
    provenance_core = frozen_provenance.get("core_sha256")
    provenance_expected = provenance.EXPECTED_CORE_SHA256
    if provenance_core != provenance_expected:
        raise ArithmeticError(
            "physical-SM dependency provenance core is not source-frozen"
        )
    quotient_report = json.loads(
        (ROOT / "EXACT_GAUGED_U1X_PHYSICAL_QUOTIENT_V20.json").read_text(
            encoding="utf-8"
        )
    )
    contract_report = json.loads(
        (ROOT / "GAUGED_U1X_SCALAR_CONTRACT_V20.json").read_text(
            encoding="utf-8"
        )
    )
    g2_report = json.loads(
        (ROOT / "GAUGED_U1X_G2_DERIVATIVE_AUDIT_V20.json").read_text(
            encoding="utf-8"
        )
    )
    validation = {
        "dependency_file_count": len(bindings),
        "all_dependency_files_present": not missing,
        "provenance_core_sha256": provenance_core,
        "provenance_core_matches_imported_expected_pin": (
            provenance_core == provenance_expected
        ),
        "physical_quotient_frozen_certified": bool(
            quotient_report.get("certified")
        ),
        "scalar_contract_frozen_has_zero_failures": (
            contract_report.get("n_failed") == 0
        ),
        "G2_derivative_audit_frozen_has_zero_failures": (
            g2_report.get("n_failed") == 0
        ),
    }
    if not all(
        value
        for key, value in validation.items()
        if key.endswith("_pass")
        or key.endswith("_has_zero_failures")
        or key.endswith("_certified")
        or key.startswith("all_")
        or key.endswith("_pin")
    ):
        raise ArithmeticError("physical-SM dependency validation failed")
    return {"files": bindings, "validation": validation}


@lru_cache(maxsize=1)
def integer_target_vector() -> np.ndarray:
    """Return the exact integer lattice vector ``20 q_*``."""
    output = np.zeros(chart.TOTAL_DIM, dtype=np.int64)
    p_index = chart.phi_indices().index((6, 7, 8, 9))
    output[chart.PHI_SLICE.start + p_index] = TARGET_DENOMINATOR
    output[chart.H_SLICE.start + 2 * 8] = TARGET_DENOMINATOR
    output[chart.H_SLICE.start + 2 * 9 + 1] = TARGET_DENOMINATOR
    raw_sigma = provenance._true_sm_singlet_vector()
    output[chart.SIGMA_SLICE] = raw_sigma[chart.SIGMA_SLICE]
    output[chart.S_SLICE.start] = TARGET_DENOMINATOR // 5
    output[chart.X_SLICE.start] = TARGET_DENOMINATOR
    if int(output @ output) != 1632:
        raise ArithmeticError("physical target lattice norm drifted")
    return output


@lru_cache(maxsize=1)
def target_state() -> potential.FieldState:
    """Return the physical target through the canonical chart bijection."""
    state = chart.unpack(integer_target_vector() / TARGET_DENOMINATOR)
    if chart.pack(state).tobytes() != (
        integer_target_vector() / TARGET_DENOMINATOR
    ).tobytes():
        raise ArithmeticError("target failed canonical chart round trip")
    return state


def target_certificate() -> dict[str, Any]:
    lattice = integer_target_vector()
    q = lattice / TARGET_DENOMINATOR
    support = np.flatnonzero(lattice)
    ancestry = provenance._ancestry_operators()
    pre_ew_lattice = lattice.copy()
    pre_ew_lattice[chart.H_SLICE] = 0
    return {
        "chart_dimension": chart.TOTAL_DIM,
        "lattice_denominator": TARGET_DENOMINATOR,
        "lattice_norm_squared": int(lattice @ lattice),
        "q_norm_squared": str(TARGET_NORM_SQUARED),
        "support_size": int(support.size),
        "support": {str(int(index)): int(lattice[index]) for index in support},
        "field_block_q_norm_squared": {
            "Phi210": str(Fraction(int(lattice[chart.PHI_SLICE] @ lattice[chart.PHI_SLICE]), 400)),
            "H10": str(Fraction(int(lattice[chart.H_SLICE] @ lattice[chart.H_SLICE]), 400)),
            "Sigma126bar": str(Fraction(int(lattice[chart.SIGMA_SLICE] @ lattice[chart.SIGMA_SLICE]), 400)),
            "S": str(Fraction(int(lattice[chart.S_SLICE] @ lattice[chart.S_SLICE]), 400)),
            "Phi17": str(Fraction(int(lattice[chart.X_SLICE] @ lattice[chart.X_SLICE]), 400)),
        },
        "standard_Y6_annihilates_pre_EW_fields": bool(
            not np.any(ancestry["standard_Y6"] @ pre_ew_lattice)
        ),
        "standard_Q3_annihilates_full_target": bool(
            not np.any(ancestry["standard_Q3"] @ lattice)
        ),
        "bare_G89_annihilates_full_target": bool(
            not np.any(ancestry["actual_G89"] @ lattice)
        ),
        "interpretation": (
            "The full target is neutral under the standard Q3=3Q generator; "
            "the pre-EW Phi+Sigma+S+X target is neutral under standard Y6."
        ),
    }


def _canonical_exact_shapes() -> tuple[
    quotient.ExactForm, tuple[quotient.GaussianInteger, ...], quotient.ExactForm
]:
    """Exact unnormalized field shapes with the actual lattice amplitudes."""
    imaginary = quotient.I
    phi = {(6, 7, 8, 9): (TARGET_DENOMINATOR, 0)}
    h = tuple(
        (TARGET_DENOMINATOR, 0)
        if index == 8
        else (0, TARGET_DENOMINATOR)
        if index == 9
        else quotient.ZERO
        for index in range(10)
    )
    first_factor = quotient._add_forms(
        quotient._one_form(0), quotient._one_form(1, imaginary)
    )
    form = first_factor
    for first in (2, 4, 6, 8):
        form = quotient._wedge(
            form,
            quotient._add_forms(
                quotient._one_form(first),
                quotient._one_form(first + 1, imaginary),
            ),
        )
    if len(form) != 32:
        raise ArithmeticError("true SM singlet support drifted")
    return phi, h, form


def _append_interleaved(
    output: list[int], values: Iterable[quotient.GaussianInteger]
) -> None:
    for real, imaginary in values:
        output.extend((real, imaginary))


def _so10_tangent_column(first: int, second: int) -> tuple[int, ...]:
    phi, h, sigma = _canonical_exact_shapes()
    delta_phi = quotient._generator_action(phi, first, second)
    delta_h = [quotient.ZERO] * 10
    delta_h[first] = h[second]
    delta_h[second] = quotient._g_neg(h[first])
    delta_sigma = quotient._generator_action(sigma, first, second)
    output: list[int] = []
    for indices in chart.phi_indices():
        real, imaginary = delta_phi.get(indices, quotient.ZERO)
        if imaginary:
            raise ArithmeticError("real 210 tangent acquired imaginary component")
        output.append(real)
    _append_interleaved(output, delta_h)
    _append_interleaved(
        output,
        (
            delta_sigma.get(indices, quotient.ZERO)
            for indices in quotient._sigma_representatives()
        ),
    )
    output.extend((0, 0, 0, 0))
    return tuple(output)


def _phase_tangent_column(charges: dict[str, int]) -> tuple[int, ...]:
    _phi, h, sigma = _canonical_exact_shapes()
    output = [0] * chart.PHI_DIM
    _append_interleaved(
        output,
        (quotient._g_mul((0, charges["H10"]), item) for item in h),
    )
    _append_interleaved(
        output,
        (
            quotient._g_mul(
                (0, charges["Sigma126bar"]),
                sigma.get(indices, quotient.ZERO),
            )
            for indices in quotient._sigma_representatives()
        ),
    )
    _append_interleaved(output, (((0, charges["S"] * 4)),))
    _append_interleaved(output, (((0, charges["Phi17"] * 20)),))
    return tuple(output)


@lru_cache(maxsize=1)
def exact_integer_tangent_matrix() -> tuple[tuple[int, ...], ...]:
    columns = [
        _so10_tangent_column(first, second)
        for first, second in itertools.combinations(range(10), 2)
    ]
    columns.extend(
        (
            _phase_tangent_column(quotient.U1X_CHARGES),
            _phase_tangent_column(quotient.PQ_CHARGES),
        )
    )
    return tuple(
        tuple(column[row] for column in columns)
        for row in range(chart.TOTAL_DIM)
    )


def _generator_coefficient_vector(terms: dict[tuple[int, int], int]) -> tuple[int, ...]:
    labels = tuple(itertools.combinations(range(10), 2))
    return tuple(terms.get(label, 0) for label in labels)


def standard_unbroken_vectors() -> tuple[tuple[int, ...], ...]:
    g = _generator_coefficient_vector
    return (
        g({(0, 1): 1, (2, 3): -1}),
        g({(2, 3): 1, (4, 5): -1}),
        g({(0, 2): 1, (1, 3): 1}),
        g({(0, 3): 1, (1, 2): -1}),
        g({(0, 4): 1, (1, 5): 1}),
        g({(0, 5): 1, (1, 4): -1}),
        g({(2, 4): 1, (3, 5): 1}),
        g({(2, 5): 1, (3, 4): -1}),
        g({(6, 7): 3, (0, 1): -1, (2, 3): -1, (4, 5): -1}),
    )


@lru_cache(maxsize=1)
def exact_symmetry_certificate() -> dict[str, Any]:
    full = exact_integer_tangent_matrix()
    so10 = tuple(tuple(row[:45]) for row in full)
    gauge = tuple(tuple(row[:46]) for row in full)
    matrices = {"SO10": so10, "SO10_x_U1X": gauge, "SO10_x_U1X_x_PQ": full}
    expected = {
        "SO10": EXPECTED_SO10_ORBIT_RANK,
        "SO10_x_U1X": EXPECTED_GAUGE_ORBIT_RANK,
        "SO10_x_U1X_x_PQ": EXPECTED_FULL_SYMMETRY_ORBIT_RANK,
    }
    reports: dict[str, Any] = {}
    for name, matrix in matrices.items():
        rank, pivot_rows, pivot_columns = quotient._row_echelon_metadata(matrix)
        minor = [[matrix[row][column] for column in pivot_columns] for row in pivot_rows]
        determinant = quotient._bareiss_determinant(minor)
        reports[name] = {
            "shape": [len(matrix), len(matrix[0])],
            "exact_rank": rank,
            "expected_rank": expected[name],
            "pivot_rows": list(pivot_rows),
            "pivot_columns": list(pivot_columns),
            "nonzero_minor_determinant": str(determinant),
            "minor_is_nonzero": determinant != 0,
        }
    unbroken = standard_unbroken_vectors()
    annihilated = all(quotient._matrix_vector_product_is_zero(so10, vector) for vector in unbroken)
    gram = np.asarray(unbroken, dtype=np.int64) @ np.asarray(unbroken, dtype=np.int64).T
    unbroken_rank, unbroken_pivot_rows, unbroken_pivot_columns = (
        quotient._row_echelon_metadata(unbroken)
    )
    unbroken_minor = [
        [unbroken[row][column] for column in unbroken_pivot_columns]
        for row in unbroken_pivot_rows
    ]
    unbroken_minor_determinant = quotient._bareiss_determinant(unbroken_minor)
    gram_determinant = quotient._bareiss_determinant(gram.tolist())
    independent = bool(
        unbroken_rank == 9
        and unbroken_minor_determinant != 0
        and gram_determinant != 0
    )
    state = target_state()
    live_tangents = np.column_stack(
        (
            chart.gauge_orbit_matrix(state),
            g2_audit.u1x_tangent(state),
            _phase_tangent(state, quotient.PQ_CHARGES),
        )
    )
    exact_tangents = np.asarray(full, dtype=float) / TARGET_DENOMINATOR
    binding_residual = float(
        np.max(np.abs(live_tangents - exact_tangents), initial=0.0)
    )
    return {
        "evidence_kind": "exact_integer_tangent_minors_plus_explicit_kernel",
        "target_lattice_denominator": TARGET_DENOMINATOR,
        "orbits": reports,
        "standard_unbroken_basis": {
            "dimension": len(unbroken),
            "interpretation": "8 generators of su(3)_C plus Q3=3Q",
            "annihilates_target_exactly": annihilated,
            "exact_rank": unbroken_rank,
            "pivot_rows": list(unbroken_pivot_rows),
            "pivot_columns": list(unbroken_pivot_columns),
            "nonzero_minor_determinant": str(unbroken_minor_determinant),
            "Gram_determinant": str(gram_determinant),
            "independent": independent,
        },
        "exact_stabilizer_is_su3C_plus_u1em": bool(
            reports["SO10"]["exact_rank"] == 36 and annihilated and independent
        ),
        "live_chart_binding": {
            "expected_relation": "T_live=M_integer/20",
            "maximum_abs_residual": binding_residual,
            "passes": binding_residual < 1.0e-12,
        },
        "all_expected_ranks_proved": all(
            report["exact_rank"] == report["expected_rank"]
            and report["minor_is_nonzero"]
            for report in reports.values()
        ),
    }


@lru_cache(maxsize=1)
def compiler_parameter_rows() -> tuple[Any, ...]:
    state = target_state()
    q = chart.pack(state)
    selection = g2_audit.contract_selection()
    values = potential.evaluate_directions(state)
    by_direction = {row.direction_id: row for row in values}
    owners = g2_audit._adapter_modules_by_family()
    direction_rows = tuple(
        owners[by_direction[direction_id].base_family].direction_derivative(
            q, by_direction[direction_id]
        )
        for direction_id in sorted(selection["direction_ids"])
    )
    rows = derivatives.parameter_derivatives(direction_rows)
    if len(direction_rows) != 44 or len(rows) != 51:
        raise ArithmeticError("gauged compiler dimension drifted")
    return tuple(rows)


def _recognize_q_or_sqrt2q(value: float) -> tuple[str, Fraction, float]:
    """Uniquely recognize a compiler entry on the declared small lattice."""
    rational = Fraction(float(value)).limit_denominator(10_000)
    rational_residual = abs(float(rational) - value)
    sqrt_rational = Fraction(float(value / math.sqrt(2.0))).limit_denominator(
        10_000
    )
    sqrt_residual = abs(float(sqrt_rational) * math.sqrt(2.0) - value)
    if rational_residual < 1.0e-10:
        return "Q", rational, rational_residual
    if sqrt_residual < 1.0e-10:
        return "sqrt2Q", sqrt_rational, sqrt_residual
    raise ArithmeticError(
        f"compiler stationarity entry {value!r} left the Q+sqrt(2)Q lattice"
    )


def reconstructed_stationarity_system(
    gradient_matrix: np.ndarray,
) -> tuple[list[list[Fraction]], dict[str, Any]]:
    """Split the live matrix into exact rational and sqrt(2) coefficients.

    This is an auditable lattice reconstruction, not a replacement for a
    future direct symbolic derivation from every tensor projector source.
    """
    source = np.asarray(gradient_matrix, dtype=float)
    active_rows = np.flatnonzero(np.max(np.abs(source), axis=1) > 1.0e-13)
    equations: list[list[Fraction]] = []
    rational_rows = 0
    sqrt_rows = 0
    mixed_rows: list[int] = []
    maximum_residual = 0.0
    nonzero_entries = 0
    for row_index in active_rows:
        rational = [Fraction(0) for _ in range(source.shape[1])]
        sqrt_part = [Fraction(0) for _ in range(source.shape[1])]
        kinds: set[str] = set()
        for column, value in enumerate(source[row_index]):
            if abs(value) <= 1.0e-13:
                continue
            kind, exact, residual = _recognize_q_or_sqrt2q(float(value))
            maximum_residual = max(maximum_residual, residual)
            nonzero_entries += 1
            kinds.add(kind)
            if kind == "Q":
                rational[column] = exact
            else:
                sqrt_part[column] = exact
        if any(rational):
            equations.append(rational)
            rational_rows += 1
        if any(sqrt_part):
            equations.append(sqrt_part)
            sqrt_rows += 1
        if len(kinds) == 2:
            mixed_rows.append(int(row_index))
    reduced, pivots = quotient._rref(equations, source.shape[1])
    return equations, {
        "active_live_rows": int(active_rows.size),
        "active_live_row_indices": [int(value) for value in active_rows],
        "nonzero_live_entries": nonzero_entries,
        "rational_equation_rows_after_split": rational_rows,
        "sqrt2_equation_rows_after_split": sqrt_rows,
        "mixed_Q_plus_sqrt2Q_live_rows": mixed_rows,
        "total_rational_equations_after_split": len(equations),
        "maximum_live_reconstruction_residual": maximum_residual,
        "denominator_bound": 10_000,
        "exact_reconstructed_rank": len(pivots),
        "exact_reconstructed_nullity": source.shape[1] - len(pivots),
        "pivot_columns": list(pivots),
        "_reduced": reduced,
    }


def exact_reconstructed_stationary_coefficients(
    gradient_matrix: np.ndarray,
    values: np.ndarray,
    parameter_ids: tuple[str, ...],
) -> tuple[tuple[Fraction, ...], dict[str, Any]]:
    equations, reconstruction = reconstructed_stationarity_system(
        gradient_matrix
    )
    reduced = reconstruction.pop("_reduced")
    pivots = tuple(reconstruction["pivot_columns"])
    free = tuple(index for index in range(len(parameter_ids)) if index not in pivots)
    common_seed_denominator = 100_000_000
    coefficients = [Fraction(0) for _ in parameter_ids]
    for index in free:
        seed = SDP_SEED.get(parameter_ids[index], 0.0)
        coefficients[index] = Fraction(
            round(seed * common_seed_denominator), common_seed_denominator
        )
    for row, pivot in enumerate(pivots):
        coefficients[pivot] = -sum(
            reduced[row][index] * coefficients[index] for index in free
        )
    if not all(
        sum(entry * coefficient for entry, coefficient in zip(row, coefficients))
        == 0
        for row in equations
    ):
        raise ArithmeticError("exact reconstructed witness is not stationary")
    exact_values: list[Fraction] = []
    maximum_value_residual = 0.0
    for value in values:
        exact = Fraction(float(value)).limit_denominator(100_000)
        residual = abs(float(exact) - float(value))
        if residual >= 1.0e-10:
            raise ArithmeticError("potential value left the rational lattice")
        maximum_value_residual = max(maximum_value_residual, residual)
        exact_values.append(exact)
    raw_value = sum(
        value * coefficient
        for value, coefficient in zip(exact_values, coefficients)
    )
    if raw_value >= 0:
        raise ArithmeticError("rational stationary witness lost negative V")
    coefficients = [coefficient / (-raw_value) for coefficient in coefficients]
    exact_value = sum(
        value * coefficient
        for value, coefficient in zip(exact_values, coefficients)
    )
    if exact_value != -1:
        raise ArithmeticError("exact V=-1 normalization failed")
    reconstruction.update(
        {
            "free_columns": list(free),
            "free_parameter_ids": [parameter_ids[index] for index in free],
            "common_free_seed_denominator": common_seed_denominator,
            "raw_exact_potential_value": str(raw_value),
            "normalized_exact_potential_value": str(exact_value),
            "maximum_live_value_reconstruction_residual": maximum_value_residual,
            "exact_reconstructed_stationarity": True,
            "source_algebra_derivation_complete": False,
        }
    )
    return tuple(coefficients), reconstruction


def _phase_tangent(state: potential.FieldState, charges: dict[str, int]) -> np.ndarray:
    tangent = np.zeros(chart.TOTAL_DIM, dtype=float)

    def block(values: Iterable[complex], charge: int) -> np.ndarray:
        varied = 1j * charge * np.asarray(tuple(values), dtype=complex)
        output = np.empty(2 * varied.size, dtype=float)
        output[0::2] = chart.SQRT2 * varied.real
        output[1::2] = chart.SQRT2 * varied.imag
        return output

    tangent[chart.H_SLICE] = block(state.h, charges["H10"])
    tangent[chart.SIGMA_SLICE] = block(
        chart.sigma_coordinates(state.sigma), charges["Sigma126bar"]
    )
    tangent[chart.S_SLICE] = block((state.s,), charges["S"])
    tangent[chart.X_SLICE] = block((state.x,), charges["Phi17"])
    return tangent


def _joint_sector_report(hessian: np.ndarray) -> dict[str, Any]:
    ancestry = provenance._ancestry_operators()
    color = ancestry["standard_12C2_SU3"].toarray().astype(float)
    q3 = ancestry["standard_Q3"].toarray().astype(float)
    charge = -(q3 @ q3)
    color_eigenvalues, color_vectors = np.linalg.eigh(color)
    sectors: list[dict[str, Any]] = []
    for color_label in sorted({int(round(value)) for value in color_eigenvalues}):
        color_indices = np.flatnonzero(np.abs(color_eigenvalues - color_label) < 1.0e-7)
        color_basis = color_vectors[:, color_indices]
        charge_block = color_basis.T @ charge @ color_basis
        q_eigenvalues, q_vectors = np.linalg.eigh(0.5 * (charge_block + charge_block.T))
        for q_label in sorted({int(round(value)) for value in q_eigenvalues}):
            q_indices = np.flatnonzero(np.abs(q_eigenvalues - q_label) < 1.0e-7)
            basis = color_basis @ q_vectors[:, q_indices]
            block = basis.T @ hessian @ basis
            eigenvalues = np.linalg.eigvalsh(0.5 * (block + block.T))
            zero_count = int(np.sum(np.abs(eigenvalues) < 1.0e-7))
            sectors.append(
                {
                    "12C2_SU3": color_label,
                    "Q3_squared": q_label,
                    "full_dimension": int(basis.shape[1]),
                    "symmetry_zero_modes": zero_count,
                    "transverse_dimension": int(basis.shape[1] - zero_count),
                    "minimum_transverse_eigenvalue": (
                        float(eigenvalues[zero_count])
                        if zero_count < eigenvalues.size
                        else None
                    ),
                    "maximum_eigenvalue": float(eigenvalues[-1]),
                }
            )
    return {
        "operator_convention": "(12*C2_SU3,Q3^2) in repository integer normalization",
        "color_operator_eigenvalues": sorted(
            {int(round(value)) for value in color_eigenvalues}
        ),
        "charge_operator_eigenvalues": sorted(
            {int(round(value)) for value in np.linalg.eigvalsh(charge)}
        ),
        "Hessian_color_commutator_max_abs": float(
            np.max(np.abs(hessian @ color - color @ hessian), initial=0.0)
        ),
        "Hessian_charge_commutator_max_abs": float(
            np.max(np.abs(hessian @ charge - charge @ hessian), initial=0.0)
        ),
        "sectors": sectors,
        "full_dimension_sum": sum(row["full_dimension"] for row in sectors),
        "zero_mode_sum": sum(row["symmetry_zero_modes"] for row in sectors),
        "transverse_dimension_sum": sum(row["transverse_dimension"] for row in sectors),
    }


@lru_cache(maxsize=1)
def live_local_feasibility() -> dict[str, Any]:
    rows = compiler_parameter_rows()
    parameter_ids = tuple(row.parameter_id for row in rows)
    values = np.asarray([float(row.value) for row in rows])
    gradient_matrix = np.column_stack(
        [np.asarray(row.gradient, dtype=float) for row in rows]
    )
    hessian_stack = np.stack(
        [np.asarray(row.hessian, dtype=float) for row in rows]
    )
    exact_coefficients, reconstruction = (
        exact_reconstructed_stationary_coefficients(
            gradient_matrix, values, parameter_ids
        )
    )
    coefficients = np.asarray(
        [float(value) for value in exact_coefficients], dtype=float
    )
    contract_directions, _contract_parameters, _contract_report = (
        g2_audit._contract_selection_cached()
    )
    metadata_by_parameter: dict[str, dict[str, Any]] = {}
    for direction in contract_directions:
        for parameter_id in direction["parameter_ids"]:
            metadata_by_parameter[parameter_id] = direction
    support_rows: list[dict[str, Any]] = []
    for parameter_id, exact in zip(parameter_ids, exact_coefficients):
        if not exact:
            continue
        metadata = metadata_by_parameter.get(parameter_id)
        if metadata is None:
            raise KeyError(f"parameter left scalar contract: {parameter_id}")
        support_rows.append(
            {
                "parameter_id": parameter_id,
                "direction_id": metadata["direction_id"],
                "representative": metadata["representative"],
                "self_conjugate": bool(metadata["self_conjugate"]),
                "PQ_charge": int(metadata["charge"]["PQ"]),
                "X_charge": int(metadata["charge"]["X"]),
            }
        )
    pq_support = {
        "evidence_kind": "exact_gauged_scalar_contract_character_metadata",
        "nonzero_parameter_count": len(support_rows),
        "nonzero_parameter_ids": [row["parameter_id"] for row in support_rows],
        "support": support_rows,
        "all_nonzero_parameters_are_lambda_components": all(
            row["parameter_id"].startswith("lambda::") for row in support_rows
        ),
        "all_nonzero_directions_are_self_conjugate": all(
            row["self_conjugate"] for row in support_rows
        ),
        "all_nonzero_directions_have_exact_zero_PQ_charge": all(
            row["PQ_charge"] == 0 for row in support_rows
        ),
        "all_nonzero_directions_have_exact_zero_X_charge": all(
            row["X_charge"] == 0 for row in support_rows
        ),
        "renormalizable_witness_is_globally_PQ_and_X_invariant": all(
            row["self_conjugate"]
            and row["PQ_charge"] == 0
            and row["X_charge"] == 0
            for row in support_rows
        ),
    }
    gradient = gradient_matrix @ coefficients
    hessian = np.tensordot(coefficients, hessian_stack, axes=1)
    hessian = 0.5 * (hessian + hessian.T)
    eigenvalues = np.linalg.eigvalsh(hessian)
    state = target_state()
    tangents = np.column_stack(
        (
            chart.gauge_orbit_matrix(state),
            g2_audit.u1x_tangent(state),
            _phase_tangent(state, quotient.PQ_CHARGES),
        )
    )
    tangent_singular_values = np.linalg.svd(tangents, compute_uv=False)
    tangent_rank = int(np.sum(tangent_singular_values > 1.0e-10))
    zero_count = int(np.sum(np.abs(eigenvalues) < 1.0e-7))
    numerical_pass = bool(
        reconstruction["exact_reconstructed_rank"] == 15
        and np.max(np.abs(gradient), initial=0.0) < 1.0e-10
        and tangent_rank == EXPECTED_FULL_SYMMETRY_ORBIT_RANK
        and zero_count == EXPECTED_FULL_SYMMETRY_ORBIT_RANK
        and eigenvalues[EXPECTED_FULL_SYMMETRY_ORBIT_RANK] > 0.09
        and np.max(np.abs(hessian @ tangents), initial=0.0) < 1.0e-8
        and pq_support["renormalizable_witness_is_globally_PQ_and_X_invariant"]
    )
    sector_report = _joint_sector_report(hessian)
    return {
        "evidence_kind": "independent_live_44_direction_51_parameter_float64_compiler",
        "proof_grade": False,
        "direction_count": 44,
        "parameter_count": len(parameter_ids),
        "field_dimension": chart.TOTAL_DIM,
        "stationarity": {
            **reconstruction,
            "live_potential_value_after_exact_normalization": float(
                values @ coefficients
            ),
            "gradient_max_abs": float(np.max(np.abs(gradient), initial=0.0)),
            "gradient_l2_norm": float(np.linalg.norm(gradient)),
            "gradient_entries_above_1e_minus_10": int(np.sum(np.abs(gradient) > 1.0e-10)),
        },
        "coefficients": {
            parameter_id: {
                "exact_fraction": str(exact),
                "float64": float(exact),
            }
            for parameter_id, exact in zip(parameter_ids, exact_coefficients)
            if exact
        },
        "global_PQ_support": pq_support,
        "Hessian": {
            "full_dimension": chart.TOTAL_DIM,
            "symmetry_tangent_rank_float64": tangent_rank,
            "zero_eigenvalue_count_abs_lt_1e_minus_7": zero_count,
            "minimum_full_eigenvalue": float(eigenvalues[0]),
            "minimum_transverse_eigenvalue": float(
                eigenvalues[EXPECTED_FULL_SYMMETRY_ORBIT_RANK]
            ),
            "maximum_eigenvalue": float(eigenvalues[-1]),
            "Hessian_times_full_symmetry_tangents_max_abs": float(
                np.max(np.abs(hessian @ tangents), initial=0.0)
            ),
            "strictly_positive_transverse_dimension": int(
                np.sum(eigenvalues > 1.0e-7)
            ),
        },
        "physical_sector_decomposition": sector_report,
        "numerical_local_feasibility_checks_pass": numerical_pass,
        "limitations": [
            "stationarity entries are lattice-reconstructed from the live compiler; a direct source-algebra derivation remains open",
            "transverse positivity is numerical, not an exact PSD certificate",
            "no claim that the target is the global minimum",
            "no pole spectrum, matching, or RG closure is inferred",
        ],
    }


def _recognize_hessian_entry(value: float) -> tuple[Fraction, Fraction, float]:
    """Recognize one Hessian entry as ``a + sqrt(2)b``.

    Individual chiral source Hessians contain sqrt(2), although those source
    coefficients vanish in the rational witness.  Choosing the smaller of
    the Q and sqrt(2)Q residuals avoids misclassifying a radical as a large
    continued-fraction rational.
    """
    rational = Fraction(float(value)).limit_denominator(12_600)
    rational_residual = abs(float(rational) - value)
    sqrt_rational = Fraction(float(value / math.sqrt(2.0))).limit_denominator(
        12_600
    )
    sqrt_residual = abs(float(sqrt_rational) * math.sqrt(2.0) - value)
    if rational_residual <= sqrt_residual and rational_residual < 1.0e-10:
        return rational, Fraction(0), rational_residual
    if sqrt_residual < 1.0e-10:
        return Fraction(0), sqrt_rational, sqrt_residual
    raise ArithmeticError(
        f"compiler Hessian entry {value!r} left the Q+sqrt(2)Q lattice"
    )


@lru_cache(maxsize=1)
def reconstructed_exact_hessian() -> tuple[
    dict[tuple[int, int], tuple[Fraction, Fraction]], dict[str, Any]
]:
    """Reconstruct the stationary Hessian over Q(sqrt(2))."""
    rows = compiler_parameter_rows()
    parameter_ids = tuple(row.parameter_id for row in rows)
    values = np.asarray([float(row.value) for row in rows])
    gradient_matrix = np.column_stack(
        [np.asarray(row.gradient, dtype=float) for row in rows]
    )
    coefficients, _stationarity = exact_reconstructed_stationary_coefficients(
        gradient_matrix, values, parameter_ids
    )
    entries: dict[tuple[int, int], tuple[Fraction, Fraction]] = {}
    source_nonzero_terms = 0
    rational_source_terms = 0
    radical_source_terms = 0
    maximum_residual = 0.0
    for coefficient, row in zip(coefficients, rows):
        if not coefficient:
            continue
        hessian = np.asarray(row.hessian, dtype=float)
        for first, second in zip(*np.nonzero(np.abs(hessian) > 1.0e-13)):
            rational, radical, residual = _recognize_hessian_entry(
                float(hessian[first, second])
            )
            source_nonzero_terms += 1
            rational_source_terms += bool(rational)
            radical_source_terms += bool(radical)
            maximum_residual = max(maximum_residual, residual)
            old_rational, old_radical = entries.get(
                (int(first), int(second)), (Fraction(0), Fraction(0))
            )
            value = (
                old_rational + coefficient * rational,
                old_radical + coefficient * radical,
            )
            if value == (0, 0):
                entries.pop((int(first), int(second)), None)
            else:
                entries[(int(first), int(second))] = value
    symmetric = all(
        entries.get((second, first), (Fraction(0), Fraction(0))) == value
        for (first, second), value in entries.items()
    )
    radical_entries = sum(radical != 0 for _rational, radical in entries.values())
    serialization = "".join(
        f"{first},{second},{rational},{radical}\n"
        for (first, second), (rational, radical) in sorted(entries.items())
    ).encode("ascii")
    uniqueness_radius = Fraction(1, 2 * 12_600 * 12_600)
    return entries, {
        "field_dimension": chart.TOTAL_DIM,
        "coefficient_field": "Q(sqrt(2))",
        "source_nonzero_terms_before_sum": source_nonzero_terms,
        "rational_source_terms": rational_source_terms,
        "sqrt2_source_terms": radical_source_terms,
        "aggregate_nonzero_entries": len(entries),
        "aggregate_sqrt2_nonzero_entries": radical_entries,
        "aggregate_matrix_is_rational": radical_entries == 0,
        "aggregate_matrix_is_exactly_symmetric": symmetric,
        "source_entry_denominator_bound": 12_600,
        "denominator_bound_source_derived": False,
        "maximum_live_source_entry_reconstruction_residual": maximum_residual,
        "continued_fraction_uniqueness_radius_given_bound": str(
            uniqueness_radius
        ),
        "continued_fraction_reconstruction_unique_given_bound": (
            maximum_residual < float(uniqueness_radius)
        ),
        "uniqueness_radius_to_maximum_residual_ratio": float(
            uniqueness_radius
        )
        / maximum_residual,
        "canonical_sparse_matrix_sha256": hashlib.sha256(serialization).hexdigest(),
        "source_algebra_derivation_complete": False,
    }


def _fraction_mod(value: Fraction, prime: int) -> int:
    if value.denominator % prime == 0:
        raise ZeroDivisionError("reconstruction denominator vanishes modulo prime")
    return (
        (value.numerator % prime)
        * pow(value.denominator % prime, -1, prime)
    ) % prime


def _matrix_mod_prime(
    entries: dict[tuple[int, int], tuple[Fraction, Fraction]],
    prime: int,
    sqrt2_root: int,
) -> np.ndarray:
    matrix = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=np.int64)
    for (first, second), (rational, radical) in entries.items():
        matrix[first, second] = (
            _fraction_mod(rational, prime)
            + sqrt2_root * _fraction_mod(radical, prime)
        ) % prime
    return matrix


def _determinant_mod_prime(matrix: np.ndarray, prime: int) -> int:
    work = np.asarray(matrix, dtype=np.int64).copy() % prime
    determinant = 1
    for column in range(work.shape[0]):
        candidates = np.flatnonzero(work[column:, column])
        if not candidates.size:
            return 0
        selected = column + int(candidates[0])
        if selected != column:
            work[[column, selected]] = work[[selected, column]]
            determinant = -determinant
        pivot = int(work[column, column])
        determinant = (determinant * pivot) % prime
        inverse = pow(pivot, -1, prime)
        work[column] = (work[column] * inverse) % prime
        below = np.flatnonzero(work[column + 1 :, column]) + column + 1
        if below.size:
            work[below] = (
                work[below]
                - work[below, column, None] * work[column, None, :]
            ) % prime
    return determinant % prime


def _modular_rank_certificate(
    entries: dict[tuple[int, int], tuple[Fraction, Fraction]],
    prime: int,
    sqrt2_root: int,
) -> dict[str, Any]:
    original = _matrix_mod_prime(entries, prime, sqrt2_root)
    work = original.copy()
    origins = np.arange(chart.TOTAL_DIM)
    pivot_rows: list[int] = []
    pivot_columns: list[int] = []
    rank = 0
    for column in range(chart.TOTAL_DIM):
        candidates = np.flatnonzero(work[rank:, column])
        if not candidates.size:
            continue
        selected = rank + int(candidates[0])
        if selected != rank:
            work[[rank, selected]] = work[[selected, rank]]
            origins[[rank, selected]] = origins[[selected, rank]]
        pivot = int(work[rank, column])
        work[rank] = (work[rank] * pow(pivot, -1, prime)) % prime
        below = np.flatnonzero(work[rank + 1 :, column]) + rank + 1
        if below.size:
            work[below] = (
                work[below]
                - work[below, column, None] * work[rank, None, :]
            ) % prime
        pivot_rows.append(int(origins[rank]))
        pivot_columns.append(column)
        rank += 1
        if rank == chart.TOTAL_DIM:
            break
    minor = original[np.ix_(pivot_rows, pivot_columns)]
    determinant = _determinant_mod_prime(minor, prime)
    return {
        "prime": prime,
        "sqrt2_root": sqrt2_root,
        "sqrt2_root_check": (sqrt2_root * sqrt2_root) % prime,
        "rank": rank,
        "pivot_rows": pivot_rows,
        "pivot_columns": pivot_columns,
        "minor_determinant_mod_prime": determinant,
        "minor_is_nonzero": determinant != 0,
    }


@lru_cache(maxsize=1)
def exact_reconstructed_hessian_rank_certificate() -> dict[str, Any]:
    """Prove rank 448 on the reconstructed rational Hessian lattice."""
    entries, reconstruction = reconstructed_exact_hessian()
    tangents = exact_integer_tangent_matrix()
    tangent_columns_annihilated: list[bool] = []
    for column in range(47):
        tangent = {
            row: tangents[row][column]
            for row in range(chart.TOTAL_DIM)
            if tangents[row][column]
        }
        image: dict[int, tuple[Fraction, Fraction]] = {}
        for (first, second), (rational, radical) in entries.items():
            coefficient = tangent.get(second, 0)
            if not coefficient:
                continue
            old = image.get(first, (Fraction(0), Fraction(0)))
            image[first] = (
                old[0] + coefficient * rational,
                old[1] + coefficient * radical,
            )
        tangent_columns_annihilated.append(
            all(value == (0, 0) for value in image.values())
        )
    modular = [
        _modular_rank_certificate(entries, 1009, root)
        for root in (439, 570)
    ] + [
        _modular_rank_certificate(entries, 1031, root)
        for root in (473, 558)
    ]
    symmetry = exact_symmetry_certificate()
    exact_rank = (
        448
        if reconstruction["aggregate_matrix_is_exactly_symmetric"]
        and all(tangent_columns_annihilated)
        and symmetry["orbits"]["SO10_x_U1X_x_PQ"]["exact_rank"] == 38
        and all(row["rank"] == 448 and row["minor_is_nonzero"] for row in modular)
        else None
    )
    return {
        "evidence_kind": "exact_on_reconstructed_Q_sqrt2_lattice",
        "reconstruction": reconstruction,
        "all_47_generator_columns_annihilated_exactly": all(
            tangent_columns_annihilated
        ),
        "annihilated_generator_column_count": sum(tangent_columns_annihilated),
        "exact_symmetry_tangent_span_dimension": symmetry["orbits"][
            "SO10_x_U1X_x_PQ"
        ]["exact_rank"],
        "rank_upper_bound_from_kernel": 448,
        "modular_lower_bound_certificates": modular,
        "exact_reconstructed_rank": exact_rank,
        "exact_reconstructed_nullity": (
            chart.TOTAL_DIM - exact_rank if exact_rank is not None else None
        ),
        "kernel_equals_full_symmetry_tangent_span": exact_rank == 448,
        "proof_logic": (
            "38 independent exact symmetry tangents in ker(H) give rank_Q<=448; "
            "each nonzero rank-448 modular minor gives rank_Q>=448"
        ),
        "proof_boundary": (
            "the linear algebra is exact after Q+sqrt(2)Q reconstruction, but "
            "the reconstructed entries are not yet derived symbolically from "
            "every tensor-projector source"
        ),
        "source_proof_grade": False,
    }


def squared_stationarity_eft_value(
    potential_value: Fraction,
    gradient: Iterable[Fraction],
    *,
    a: Fraction = Fraction(1),
    b: Fraction = Fraction(1),
) -> Fraction:
    """Evaluate ``a(V+1)^2+b||grad V||^2`` over exact rationals."""
    if a <= 0 or b <= 0:
        raise ValueError("a and b must be strictly positive")
    return a * (potential_value + 1) ** 2 + b * sum(
        value * value for value in gradient
    )


def squared_stationarity_global_eft_certificate(
    *, a: Fraction = Fraction(1), b: Fraction = Fraction(1)
) -> dict[str, Any]:
    """Exact universal completion, applied fail-closed to the rebuilt target."""
    if a <= 0 or b <= 0:
        raise ValueError("a and b must be strictly positive")
    rank = exact_reconstructed_hessian_rank_certificate()
    pq_support = live_local_feasibility()["global_PQ_support"]
    if not pq_support[
        "renormalizable_witness_is_globally_PQ_and_X_invariant"
    ]:
        raise ArithmeticError(
            "squared-stationarity EFT input is not globally PQ/X invariant"
        )
    application_ready = bool(
        rank["exact_reconstructed_rank"] == 448
        and rank["kernel_equals_full_symmetry_tangent_span"]
    )
    return {
        "evidence_kind": "exact_universal_calculus_identity_plus_reconstructed_application",
        "dimensionless_operator": "U=a*(Vren+1)^2+b*||grad_q Vren||^2",
        "dimensionful_operator": (
            "U=a/Lambda^4*(Vren+Lambda^4)^2+"
            "b/Lambda^2*||grad_phi Vren||^2"
        ),
        "a": str(a),
        "b": str(b),
        "maximum_operator_degree_for_renormalizable_V": 8,
        "gauge_and_PQ_invariance": (
            "V is invariant and the canonical real representation is "
            "orthogonal, so grad(V) transforms covariantly and its norm is invariant"
        ),
        "renormalizable_witness_nonzero_parameter_count": pq_support[
            "nonzero_parameter_count"
        ],
        "renormalizable_witness_nonzero_parameter_ids": pq_support[
            "nonzero_parameter_ids"
        ],
        "renormalizable_witness_global_PQ_X_invariance_source_supported": True,
        "nonnegative_for_all_real_fields": True,
        "bounded_from_below": True,
        "target_exact_inputs": {"Vren": "-1", "gradient": "0"},
        "target_value": "0",
        "target_is_a_global_minimum": True,
        "global_minimum_orbit_is_unique": False,
        "global_zero_locus_classification_open": True,
        "exact_zero_locus_condition": "U=0 iff Vren=-1 and grad(Vren)=0",
        "target_gradient_is_zero": True,
        "target_Hessian_identity_dimensionless": "H_U=2*b*Hren^T*Hren",
        "first_square_Hessian_at_target": "0",
        "gradient_square_Hessian_at_target": "2*b*Hren^T*Hren",
        "target_Hessian_is_PSD": True,
        "target_Hessian_rank_on_reconstructed_lattice": (
            448 if application_ready else None
        ),
        "target_Hessian_nullity_on_reconstructed_lattice": (
            38 if application_ready else None
        ),
        "target_Hessian_kernel_equals_symmetry_tangents_on_reconstructed_lattice": (
            application_ready
        ),
        "strict_local_minimum_mod_full_symmetry_on_reconstructed_lattice": (
            application_ready
        ),
        "spectrum_map": "lambda_i(H_U)=2*b*lambda_i(Hren)^2",
        "source_proof_grade_application": False,
        "closure_effect": {
            "G3": False,
            "G4": False,
            "G6": False,
            "reason": (
                "universal positivity/globality is exact, but the physical "
                "application remains reconstruction-bound and the complete "
                "global zero locus is not classified"
            ),
        },
    }


def radial_eft_bfb_certificate(kappa: Fraction = Fraction(1)) -> dict[str, Any]:
    """Return the exact theorem data for kappa*R*(R-R0)^2."""
    if kappa <= 0:
        raise ValueError("kappa must be strictly positive")
    r0 = TARGET_NORM_SQUARED
    lattice = integer_target_vector()
    # H_target = 8*kappa*r0*q*q^T.  Its sole nonzero eigenvalue is
    # 8*kappa*r0*(q.q)=8*kappa*r0^2.
    radial_eigenvalue = 8 * kappa * r0 * r0
    return {
        "evidence_kind": "exact_polynomial_identity",
        "operator": "W6=kappa*R*(R-R0)^2",
        "R_definition": "R=q^T q=2 times the canonical kinetic quadratic",
        "kappa": str(kappa),
        "R0": str(r0),
        "expanded_coefficients": {
            "R_cubed": str(kappa),
            "R_squared": str(-2 * kappa * r0),
            "R": str(kappa * r0 * r0),
        },
        "target_value": "0",
        "target_gradient_is_zero": True,
        "target_Hessian": "8*kappa*R0*q*q^T",
        "target_Hessian_rank": 1,
        "target_Hessian_nonzero_eigenvalue": str(radial_eigenvalue),
        "target_Hessian_is_PSD": True,
        "nonnegative_for_all_real_fields": True,
        "leading_term": "kappa*R^3",
        "coercive_completion_for_any_finite_degree_at_most_4_potential": True,
        "target_lattice_dot_product": int(lattice @ lattice),
        "does_not_prove_target_global_minimum": True,
    }


def build_report(*, include_live: bool = True) -> dict[str, Any]:
    exact_symmetry = exact_symmetry_certificate()
    dependencies = dependency_bindings()
    live = (
        _canonicalize_live_blas_diagnostics(live_local_feasibility())
        if include_live
        else None
    )
    exact_hessian_rank = (
        exact_reconstructed_hessian_rank_certificate() if include_live else None
    )
    squared_completion = (
        squared_stationarity_global_eft_certificate() if include_live else None
    )
    report: dict[str, Any] = {
        "schema": "physical_sm_vacuum_local_feasibility_v1",
        "model_contract_id": MODEL_CONTRACT_ID,
        "status": STATUS,
        "source_binding": {
            "path": Path(__file__).name,
            "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "portable_lf_sha256": hashlib.sha256(
                _portable_text_bytes(Path(__file__))
            ).hexdigest(),
            "dependencies": dependencies,
        },
        "closure_claims": {
            "physical_SM_G3": False,
            "physical_SM_G4": False,
            "physical_SM_G5": False,
            "physical_SM_G6": False,
            "physical_SM_G7": False,
        },
        "supersession": {
            "old_selected_EFT_target_actual_stabilizer": "SU(3)_C x U(1)_89",
            "old_selected_EFT_target_was_standard_SU3C_x_U1em": False,
            "new_target_exact_stabilizer": "standard SU(3)_C x U(1)_em",
            "old_abstract_EFT_mathematical_theorems_may_remain_true_in_formal_scope": True,
            "old_abstract_EFT_theorems_do_not_close_physical_SM_G3_G4_G5": True,
            "physical_SM_G3_G4_G5_remain_false_until_source_bound_application_and_global_zero_locus": True,
        },
        "target": target_certificate(),
        "exact_symmetry": exact_symmetry,
        "exact_radial_EFT_BFB_completion": radial_eft_bfb_certificate(),
        "exact_reconstructed_Hessian_rank": exact_hessian_rank,
        "squared_stationarity_global_EFT_completion": squared_completion,
        "live_local_feasibility": live,
        "logical_summary": {
            "physical_SM_target_exactly_constructed": True,
            "standard_SU3C_x_U1em_stabilizer_proved": exact_symmetry[
                "exact_stabilizer_is_su3C_plus_u1em"
            ],
            "full_38_dimensional_symmetry_orbit_proved": exact_symmetry[
                "all_expected_ranks_proved"
            ],
            "exact_BFB_EFT_completion_available": True,
            "strict_local_minimum_mod_symmetry_numerically_found": bool(
                include_live and live["numerical_local_feasibility_checks_pass"]
            ),
            "exact_rational_witness_on_reconstructed_stationarity_lattice": bool(
                include_live
                and live["stationarity"]["exact_reconstructed_stationarity"]
            ),
            "exact_rank_448_on_reconstructed_Hessian_lattice": bool(
                include_live
                and exact_hessian_rank["exact_reconstructed_rank"] == 448
            ),
            "squared_stationarity_EFT_is_exactly_nonnegative": bool(
                include_live
                and squared_completion["nonnegative_for_all_real_fields"]
            ),
            "target_is_global_minimum_of_squared_stationarity_EFT": bool(
                include_live and squared_completion["target_is_a_global_minimum"]
            ),
            "global_minimum_orbit_classified": False,
            "source_bound_exact_stationary_PSD_witness_available": False,
            "source_bound_global_equality_orbit_proved": False,
            "physical_G6_closed": False,
        },
        "next_required_proofs": [
            "derive every reconstructed Q+sqrt(2)Q stationarity entry directly from source algebra",
            "derive every reconstructed rational Hessian entry directly from source algebra",
            "classify every zero of Vren+1 and grad(Vren) to prove the complete global equality orbit",
            "derive the physical pole spectrum and threshold matching only afterward",
        ],
    }
    core = hashlib.sha256(canonical_json_bytes(report)).hexdigest()
    report["integrity"] = {"core_sha256": core}
    return report


def render_markdown(report: dict[str, Any]) -> str:
    live = report["live_local_feasibility"]
    symmetry = report["exact_symmetry"]
    lines = [
        "# Physical SM vacuum local-feasibility rebuild v20",
        "",
        f"- Status: `{report['status']}`",
        f"- Core SHA-256: `{report['integrity']['core_sha256']}`",
        "- Physical-SM G3/G4/G5/G6/G7 closure claims: all `false`.",
        "",
        "## Exact results",
        "",
        f"- Rational target: `20 q` integral, `q.q={report['target']['q_norm_squared']}`.",
        f"- SO(10) orbit rank: `{symmetry['orbits']['SO10']['exact_rank']}`.",
        f"- Gauged SO(10)xU(1)_X orbit rank: `{symmetry['orbits']['SO10_x_U1X']['exact_rank']}`.",
        f"- Full gauge+PQ orbit rank: `{symmetry['orbits']['SO10_x_U1X_x_PQ']['exact_rank']}`.",
        "- Exact stabilizer: standard `SU(3)_C x U(1)_em`.",
        "- Supersedes the old selected-target stabilizer label: that target is actually `SU(3)_C x U(1)_89`, not standard electromagnetism.",
        "- `W6=kappa R(R-R0)^2`, `kappa>0`, is a nonnegative coercive EFT completion and adds only a PSD radial Hessian at the target.",
        "- `U=a(V+1)^2+b||grad V||^2`, `a,b>0`, is exactly nonnegative and has `H_U=2b H_V^T H_V` at the target.",
        "",
        "## Live local scout",
        "",
    ]
    if live is None:
        lines.append("Live 51-parameter compiler replay was not requested.")
    else:
        lines.extend(
            [
                f"- Reconstructed exact stationarity rank/nullity: `{live['stationarity']['exact_reconstructed_rank']}/{live['stationarity']['exact_reconstructed_nullity']}`.",
                f"- Maximum Q+sqrt(2)Q reconstruction residual: `{live['stationarity']['maximum_live_reconstruction_residual']:.6e}`.",
                f"- Gradient max norm: `{live['stationarity']['gradient_max_abs']:.6e}`.",
                f"- Hessian zero modes: `{live['Hessian']['zero_eigenvalue_count_abs_lt_1e_minus_7']}`.",
                f"- Minimum transverse eigenvalue: `{live['Hessian']['minimum_transverse_eigenvalue']:.12g}`.",
                f"- Maximum eigenvalue: `{live['Hessian']['maximum_eigenvalue']:.12g}`.",
                f"- Physical-sector transverse dimension sum: `{live['physical_sector_decomposition']['transverse_dimension_sum']}`.",
                f"- Numerical local-feasibility checks: `{str(live['numerical_local_feasibility_checks_pass']).lower()}`.",
                f"- Exact reconstructed Hessian rank/nullity: `{report['exact_reconstructed_Hessian_rank']['exact_reconstructed_rank']}/{report['exact_reconstructed_Hessian_rank']['exact_reconstructed_nullity']}`.",
                f"- Reconstructed sparse-Hessian SHA-256: `{report['exact_reconstructed_Hessian_rank']['reconstruction']['canonical_sparse_matrix_sha256']}`.",
                "- Squared-stationarity EFT target is an exact global minimum; classification of all other zero-action minima remains open.",
            ]
        )
    lines.extend(
        [
            "",
            "## Fail-closed boundary",
            "",
            "Stationarity and Hessian rank are exact on a rational lattice reconstructed from the live compiler, and the squared-stationarity EFT identity gives exact nonnegativity, globality, and PSD on that lattice. Direct source-algebra derivations of every reconstructed entry and classification of the complete global zero locus remain open, so G3/G4 and physical G6 stay fail-closed.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(*, include_live: bool = True) -> dict[str, Any]:
    report = build_report(include_live=include_live)
    OUT_JSON.write_bytes(
        json.dumps(_jsonable(report), indent=2, sort_keys=True).encode("utf-8") + b"\n"
    )
    OUT_MD.write_text(render_markdown(report), encoding="utf-8", newline="\n")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--skip-live", action="store_true")
    parser.add_argument(
        "--allow-unfrozen",
        action="store_true",
        help="permit intentional development drift before terminal hash freeze",
    )
    args = parser.parse_args()
    report = (
        write_outputs(include_live=not args.skip_live)
        if args.write
        else build_report(include_live=not args.skip_live)
    )
    frozen = json.loads(OUT_JSON.read_text(encoding="utf-8")) if OUT_JSON.exists() else None
    if not args.write and frozen != report:
        if not args.allow_unfrozen:
            raise ArithmeticError("frozen physical-SM feasibility report drifted")
    print(json.dumps(_jsonable(report), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
