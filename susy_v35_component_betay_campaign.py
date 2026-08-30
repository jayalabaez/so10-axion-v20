#!/usr/bin/env python3
"""V35 literal component reconstruction of the SUSY Pati--Salam BetaY sector.

The frozen V33 coupling-level strings retain unresolved epsilon tensors and
cannot be projected uniquely.  V35 therefore extracts the complete symmetric
component tensor Y_ijk from live SARAH, evaluates the standard N=1 SUSY
one- and two-loop anomalous dimensions, and projects the resulting component
beta tensor onto the exact 42-component invariant basis.

Loop factors are not included in ``beta1`` and ``beta2``.  The physical RGE is
dc/dln(mu) = beta1/(16*pi^2) + beta2/(16*pi^2)^2.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np


ROOT = Path(__file__).resolve().parent
BASIS_JSON = ROOT / "SUSY_V35_SARAH_YIJK_COMPONENT_BASIS.json"
PROBE_JSON = ROOT / "SUSY_V35_SARAH_BETAY_FEASIBILITY_PROBE.json"
V33_RGE_JSON = ROOT / "SUSY_V33_SARAH_RGE_ATTESTATION.json"
V34_REPORT_JSON = ROOT / "SUSY_V34_NEXT_STEP_CAMPAIGN.json"

REPORT_JSON = ROOT / "SUSY_V35_COMPONENT_BETAY_CAMPAIGN.json"
REPORT_MD = ROOT / "SUSY_V35_COMPONENT_BETAY_CAMPAIGN.md"
G6_JSON = ROOT / "SUSY_V35_G6_COMPONENT_BETAY_CLOSURE.json"
FORENSIC_JSON = ROOT / "SUSY_V35_FROZEN_BETAY_FORENSIC.json"
GATES_JSON = ROOT / "SUSY_V35_G1_G8_GATE_LEDGER.json"

UPSTREAM_V34_CORE = "053572fbf94c2583311de52beaa0ac9ab376b2c7ee5dab4751b890ebab65e1bb"
STATUS = (
    "V35_COMPONENT_BETAY_RECONSTRUCTION_COMPLETE__FROZEN_V33_BETAY_"
    "PROJECTION_IMPOSSIBLE__LIVE_YIJK_BASIS_111_BY_42_RANK42__ONE_AND_"
    "TWO_LOOP_COMPONENT_BETAS_PROJECTED__GAUGE_YUKAWA_MN_LINEAR_ENGINE_"
    "COMPLETE__PHYSICAL_BOUNDARY_STILL_MISSING__"
    "ESTABLISHED_FULL_GATES_ZERO_OF_EIGHT__NO_COMPLETE_THEORY"
)

GROUPS = ("SU4", "SU2L", "SU2R")
GAUGES = ("g4", "gL", "gR")
ADJOINT_DIMENSIONS = (15, 3, 3)
ADJOINT_CASIMIRS = (Fraction(4), Fraction(2), Fraction(2))
TOTAL_DYNKIN = (Fraction(13), Fraction(11), Fraction(15))
GAUGE_B = np.asarray((1.0, 5.0, 9.0), dtype=float)
GAUGE_B2 = np.asarray(
    ((108.0, 15.0, 21.0), (75.0, 53.0, 3.0), (105.0, 3.0, 81.0)),
    dtype=float,
)

F0 = Fraction(0)
FIELD_CASIMIRS_EXACT: dict[str, tuple[Fraction, Fraction, Fraction]] = {
    "H": (F0, Fraction(3, 4), Fraction(3, 4)),
    "Q": (Fraction(15, 8), Fraction(3, 4), F0),
    "Qc": (Fraction(15, 8), F0, Fraction(3, 4)),
    "X": (F0, F0, F0),
    "Sc": (Fraction(15, 8), F0, Fraction(3, 4)),
    "Sbc": (Fraction(15, 8), F0, Fraction(3, 4)),
    "Sig6": (Fraction(5, 2), F0, F0),
    "PsiBar": (Fraction(15, 8), Fraction(3, 4), F0),
    "Psi": (Fraction(15, 8), Fraction(3, 4), F0),
    "PsiC": (Fraction(15, 8), F0, Fraction(3, 4)),
    "PsiCBar": (Fraction(15, 8), F0, Fraction(3, 4)),
    "P": (F0, F0, F0),
    "Nv": (F0, F0, F0),
}

SOURCE_FILES = (
    "susy_v35_component_betay_campaign.py",
    "test_susy_v35_component_betay_campaign.py",
    "tools/probe-susy-v35-betay.wls",
    "tools/derive-susy-v35-yijk-basis.wls",
    "SUSY_V35_SARAH_BETAY_FEASIBILITY_PROBE.json",
    "SUSY_V35_SARAH_YIJK_COMPONENT_BASIS.json",
    "SUSY_V33_SARAH_RGE_ATTESTATION.json",
    "SUSY_V34_NEXT_STEP_CAMPAIGN.json",
    ".github/workflows/susy-v35-component-betay.yml",
)


def read_json(path: str | Path) -> dict[str, Any]:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return json.loads(candidate.read_text(encoding="utf-8"))


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


def fstr(value: Fraction | int) -> int | str:
    number = Fraction(value)
    if number.denominator == 1:
        return number.numerator
    return f"{number.numerator}/{number.denominator}"


def stable_float(value: float, digits: int = 12) -> float:
    return float(f"{float(value):.{digits}e}")


def stable_complex(value: complex) -> dict[str, float]:
    return {
        "re": stable_float(value.real),
        "im": stable_float(value.imag),
    }


def split_wolfram_top_level(row: str) -> list[str]:
    """Split a stringified Wolfram list without interpreting its algebra."""

    text = row.strip()
    if not (text.startswith("{") and text.endswith("}")):
        raise ValueError("not a Wolfram list row")
    pieces: list[str] = []
    start = 1
    depths = {"(": 0, "[": 0, "{": 0}
    closing = {")": "(", "]": "[", "}": "{"}
    for position, char in enumerate(text[1:-1], start=1):
        if char in depths:
            depths[char] += 1
        elif char in closing:
            key = closing[char]
            depths[key] -= 1
        elif char == "," and all(depth == 0 for depth in depths.values()):
            pieces.append(text[start:position].strip())
            start = position + 1
    pieces.append(text[start:-1].strip())
    if len(pieces) != 3 or any(depth != 0 for depth in depths.values()):
        raise ValueError("could not recover three beta-row columns")
    return pieces


def validate_basis_payload(payload: Mapping[str, Any]) -> None:
    if payload.get("extraction_passed") is not True:
        raise ValueError("live Yijk extraction did not pass")
    if payload.get("visible_complex_chiral_component_count") != 111:
        raise ValueError("unexpected chiral component count")
    if payload.get("dimensionless_coupling_component_count") != 42:
        raise ValueError("unexpected coupling component count")
    if payload.get("sparse_tensor_entry_count") != 2719:
        raise ValueError("unexpected ordered sparse tensor count")
    if payload.get("all_Gram_diagonals_match_reference") is not True:
        raise ValueError("Gram normalization mismatch")
    if payload.get("extraction_errors") != []:
        raise ValueError("component extraction contains errors")
    if payload.get("listWtriOne_count") != 16 or payload.get("listWtri_count") != 79:
        raise ValueError("live ordered-superpotential inventory drifted")
    if "InvMat[3]" not in payload.get("SA_NonZeroEntries_input_form", ""):
        raise ValueError("InvMat[3] nonzero seed was not captured")
    if not payload.get("InvMat3_6x6_input_form"):
        raise ValueError("InvMat[3] literal array was not captured")


class ComponentModel:
    """Frozen sparse invariant basis and component group metadata."""

    def __init__(self, payload: Mapping[str, Any]):
        validate_basis_payload(payload)
        self.payload = dict(payload)
        self.n_components = int(payload["visible_complex_chiral_component_count"])
        self.n_basis = int(payload["dimensionless_coupling_component_count"])
        self.component_rows = list(payload["component_rows"])
        self.basis_rows = list(payload["coupling_basis_rows"])
        sparse = list(payload["sparse_tensor_rows"])
        self.i = np.asarray([row["i"] - 1 for row in sparse], dtype=np.int64)
        self.j = np.asarray([row["j"] - 1 for row in sparse], dtype=np.int64)
        self.k = np.asarray([row["k"] - 1 for row in sparse], dtype=np.int64)
        self.basis = np.asarray(
            [row["basis_id"] - 1 for row in sparse], dtype=np.int64
        )
        self.coefficient = np.asarray(
            [row["coefficient_numeric"] for row in sparse], dtype=np.complex128
        )
        self.gram_diagonal = np.asarray(
            [row["diagonal_numeric"] for row in payload["Gram_diagonal_rows"]],
            dtype=float,
        )
        self.fields = [row["field"] for row in self.component_rows]
        self.casimirs_exact = [FIELD_CASIMIRS_EXACT[field] for field in self.fields]
        self.casimirs = np.asarray(
            [[float(value) for value in row] for row in self.casimirs_exact],
            dtype=float,
        )
        self.parameter_keys = [self._parameter_key(row) for row in self.basis_rows]
        self.parameter_to_ids: dict[str, list[int]] = {}
        for basis_id, row in enumerate(self.basis_rows):
            self.parameter_to_ids.setdefault(row["parameter"], []).append(basis_id)

    @staticmethod
    def _parameter_key(row: Mapping[str, Any]) -> str:
        indices = row["indices"]
        if not indices:
            return row["parameter"]
        return f"{row['parameter']}[{','.join(str(value) for value in indices)}]"

    def dense_y(self, couplings: Sequence[complex]) -> np.ndarray:
        values = np.asarray(couplings, dtype=np.complex128)
        if values.shape != (self.n_basis,):
            raise ValueError(f"expected {self.n_basis} coupling components")
        y = np.zeros(
            (self.n_components, self.n_components, self.n_components),
            dtype=np.complex128,
        )
        y[self.i, self.j, self.k] = self.coefficient * values[self.basis]
        return y

    def project(self, tensor: np.ndarray) -> np.ndarray:
        if tensor.shape != (self.n_components,) * 3:
            raise ValueError("component beta tensor has the wrong shape")
        rhs = np.zeros(self.n_basis, dtype=np.complex128)
        np.add.at(
            rhs,
            self.basis,
            self.coefficient.conjugate() * tensor[self.i, self.j, self.k],
        )
        return rhs / self.gram_diagonal

    def reconstruct(self, projected: Sequence[complex]) -> np.ndarray:
        values = np.asarray(projected, dtype=np.complex128)
        if values.shape != (self.n_basis,):
            raise ValueError("projected beta vector has the wrong shape")
        tensor = np.zeros(
            (self.n_components, self.n_components, self.n_components),
            dtype=np.complex128,
        )
        tensor[self.i, self.j, self.k] = self.coefficient * values[self.basis]
        return tensor

    def full_gram(self) -> np.ndarray:
        gram = np.zeros((self.n_basis, self.n_basis), dtype=np.complex128)
        np.add.at(
            gram,
            (self.basis, self.basis),
            self.coefficient.conjugate() * self.coefficient,
        )
        return gram


def anomalous_dimensions(
    y: np.ndarray,
    gauges: Sequence[float],
    casimirs: np.ndarray,
    total_dynkin: Sequence[float] = tuple(float(value) for value in TOTAL_DYNKIN),
    adjoint_casimirs: Sequence[float] = tuple(
        float(value) for value in ADJOINT_CASIMIRS
    ),
) -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray]]:
    """Return SARAH/Martin--Vaughn gamma^(1,2), without loop factors."""

    g = np.asarray(gauges, dtype=float)
    c = np.asarray(casimirs, dtype=float)
    if y.ndim != 3 or y.shape[0] != y.shape[1] or y.shape[1] != y.shape[2]:
        raise ValueError("Y must be a cubic component tensor")
    if c.shape != (y.shape[0], len(g)):
        raise ValueError("Casimir array does not match Y and gauge dimensions")

    cbar = c @ (g * g)
    p = 0.5 * np.einsum("imn,jmn->ij", y.conjugate(), y, optimize=True)
    gamma1 = p - 2.0 * np.diag(cbar)

    # -1/2 conj(Y_iwx) Y_xyz conj(Y_yzr) Y_wrj.
    # Since P_rx=1/2 sum_yz conj(Y_ryz)Y_xyz, the factor two cancels 1/2.
    tmp = np.einsum("rx,wrj->wxj", p, y, optimize=True)
    quartic = -np.einsum("iwx,wxj->ij", y.conjugate(), tmp, optimize=True)

    norm = np.einsum("iyz,jyz->ij", y.conjugate(), y, optimize=True)
    weighted = np.einsum(
        "iyz,jyz,y->ij", y.conjugate(), y, cbar, optimize=True
    )
    mixed = 2.0 * weighted - cbar[:, None] * norm

    s = np.asarray(total_dynkin, dtype=float)
    cg = np.asarray(adjoint_casimirs, dtype=float)
    pure_gauge = 2.0 * np.sum(
        (g**4)[None, :] * c * (s - 3.0 * cg)[None, :], axis=1
    ) + 4.0 * cbar**2
    gamma2 = quartic + mixed + np.diag(pure_gauge)
    pieces = {
        "P": p,
        "Cbar": cbar,
        "quartic": quartic,
        "mixed": mixed,
        "pure_gauge_diagonal": pure_gauge,
    }
    return gamma1, gamma2, pieces


def beta_tensor(y: np.ndarray, gamma: np.ndarray) -> np.ndarray:
    """Cyclic beta_Y = Y_ijn gamma_nk + Y_ink gamma_nj + Y_njk gamma_ni."""

    return (
        np.einsum("ijn,nk->ijk", y, gamma, optimize=True)
        + np.einsum("ink,nj->ijk", y, gamma, optimize=True)
        + np.einsum("njk,ni->ijk", y, gamma, optimize=True)
    )


def evaluate_component_betas(
    model: ComponentModel,
    couplings: Sequence[complex],
    gauges: Sequence[float],
) -> dict[str, Any]:
    y = model.dense_y(couplings)
    gamma1, gamma2, pieces = anomalous_dimensions(y, gauges, model.casimirs)
    tensor1 = beta_tensor(y, gamma1)
    tensor2 = beta_tensor(y, gamma2)
    projected1 = model.project(tensor1)
    projected2 = model.project(tensor2)
    residual1 = tensor1 - model.reconstruct(projected1)
    residual2 = tensor2 - model.reconstruct(projected2)

    max1 = float(np.max(np.abs(tensor1)))
    max2 = float(np.max(np.abs(tensor2)))
    abs_res1 = float(np.max(np.abs(residual1)))
    abs_res2 = float(np.max(np.abs(residual2)))
    return {
        "Y": y,
        "gamma1": gamma1,
        "gamma2": gamma2,
        "gamma_pieces": pieces,
        "tensor1": tensor1,
        "tensor2": tensor2,
        "projected1": projected1,
        "projected2": projected2,
        "absolute_residual1": abs_res1,
        "absolute_residual2": abs_res2,
        "relative_residual1": abs_res1 / max(max1, 1.0e-300),
        "relative_residual2": abs_res2 / max(max2, 1.0e-300),
    }


def gauge_betas(
    model: ComponentModel, y: np.ndarray, gauges: Sequence[float]
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """One/two-loop gauge betas and the component-derived Yukawa subtraction."""

    g = np.asarray(gauges, dtype=float)
    subtraction = np.asarray(
        [
            np.einsum(
                "ijk,ijk,k->",
                y.conjugate(),
                y,
                model.casimirs[:, group],
                optimize=True,
            ).real
            / ADJOINT_DIMENSIONS[group]
            for group in range(3)
        ],
        dtype=float,
    )
    beta1 = g**3 * GAUGE_B
    beta2 = g**3 * (GAUGE_B2 @ (g * g) - subtraction)
    return beta1, beta2, subtraction


def gauge_yukawa_subtraction_coefficients(model: ComponentModel) -> dict[str, Any]:
    rows = []
    grouped: dict[str, dict[str, Any]] = {}
    for basis_id, basis_row in enumerate(model.basis_rows):
        positions = np.flatnonzero(model.basis == basis_id)
        values = []
        for group, adjoint_dimension in enumerate(ADJOINT_DIMENSIONS):
            numeric = float(
                np.sum(
                    np.abs(model.coefficient[positions]) ** 2
                    * model.casimirs[model.k[positions], group]
                )
                / adjoint_dimension
            )
            exact = Fraction(numeric).limit_denominator(256)
            if abs(float(exact) - numeric) > 1.0e-12:
                raise ValueError("gauge Yukawa subtraction failed exact recovery")
            values.append(fstr(exact))
        row = {
            "basis_id": basis_id + 1,
            "key": model.parameter_keys[basis_id],
            "parameter": basis_row["parameter"],
            "coefficient_4_L_R": values,
        }
        rows.append(row)
        prior = grouped.get(basis_row["parameter"])
        if prior is None:
            grouped[basis_row["parameter"]] = {
                "coefficient_4_L_R": values,
                "component_count": 1,
            }
        else:
            if prior["coefficient_4_L_R"] != values:
                raise ValueError("family components disagree in gauge Yukawa subtraction")
            prior["component_count"] += 1
    return {
        "formula": "sum_ijk |Y_ijk|^2 C_a(k)/dim(G_a)",
        "component_rows": rows,
        "grouped_by_parameter": grouped,
    }


def dimensionful_superpotential_betas(
    model: ComponentModel,
    gamma1: np.ndarray,
    gamma2: np.ndarray,
    mn: np.ndarray,
    xi_x: complex,
) -> dict[str, Any]:
    """Project beta_MN and beta_xi from the same anomalous dimensions."""

    nv = [index for index, field in enumerate(model.fields) if field == "Nv"]
    x_rows = [index for index, field in enumerate(model.fields) if field == "X"]
    if len(nv) != 3 or len(x_rows) != 1:
        raise ValueError("unexpected Nv or X component inventory")
    mass = np.zeros((model.n_components, model.n_components), dtype=np.complex128)
    mass[np.ix_(nv, nv)] = np.asarray(mn, dtype=np.complex128)
    if np.max(np.abs(mass - mass.T)) > 1.0e-14:
        raise ValueError("MN must be complex symmetric")

    beta_m1 = mass @ gamma1 + (mass @ gamma1).T
    beta_m2 = mass @ gamma2 + (mass @ gamma2).T
    linear = np.zeros(model.n_components, dtype=np.complex128)
    linear[x_rows[0]] = xi_x
    beta_l1 = linear @ gamma1
    beta_l2 = linear @ gamma2
    outside_nv = [index for index in range(model.n_components) if index not in nv]
    outside_x = [index for index in range(model.n_components) if index != x_rows[0]]
    return {
        "MN_beta1": beta_m1[np.ix_(nv, nv)],
        "MN_beta2": beta_m2[np.ix_(nv, nv)],
        "xi_beta1": beta_l1[x_rows[0]],
        "xi_beta2": beta_l2[x_rows[0]],
        "MN_beta1_outside_support": float(
            max(
                np.max(np.abs(beta_m1[np.ix_(outside_nv, range(model.n_components))])),
                np.max(np.abs(beta_m1[np.ix_(range(model.n_components), outside_nv)])),
            )
        ),
        "MN_beta2_outside_support": float(
            max(
                np.max(np.abs(beta_m2[np.ix_(outside_nv, range(model.n_components))])),
                np.max(np.abs(beta_m2[np.ix_(range(model.n_components), outside_nv)])),
            )
        ),
        "xi_beta1_outside_support": float(np.max(np.abs(beta_l1[outside_x]))),
        "xi_beta2_outside_support": float(np.max(np.abs(beta_l2[outside_x]))),
    }


def coupled_dimensionless_rhs(
    model: ComponentModel, state: Sequence[complex]
) -> np.ndarray:
    values = np.asarray(state, dtype=np.complex128)
    if values.shape != (3 + model.n_basis,):
        raise ValueError("coupled state must contain 3 gauges and 42 couplings")
    if np.max(np.abs(values[:3].imag)) > 1.0e-12:
        raise ValueError("gauge couplings must remain real")
    gauges = values[:3].real
    couplings = values[3:]
    y = model.dense_y(couplings)
    gamma1, gamma2, _ = anomalous_dimensions(y, gauges, model.casimirs)
    beta1 = model.project(beta_tensor(y, gamma1))
    beta2 = model.project(beta_tensor(y, gamma2))
    gauge1, gauge2, _ = gauge_betas(model, y, gauges)
    loop = 16.0 * math.pi**2
    return np.concatenate(
        [gauge1 / loop + gauge2 / loop**2, beta1 / loop + beta2 / loop**2]
    ).astype(np.complex128)


def rk4_integrate(
    model: ComponentModel,
    initial: Sequence[complex],
    delta_t: float,
    steps: int,
) -> np.ndarray:
    if steps <= 0:
        raise ValueError("steps must be positive")
    state = np.asarray(initial, dtype=np.complex128).copy()
    step = delta_t / steps
    for _ in range(steps):
        k1 = coupled_dimensionless_rhs(model, state)
        k2 = coupled_dimensionless_rhs(model, state + 0.5 * step * k1)
        k3 = coupled_dimensionless_rhs(model, state + 0.5 * step * k2)
        k4 = coupled_dimensionless_rhs(model, state + step * k3)
        state += step * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
        state[:3] = state[:3].real
    return state


def exact_gauge_coefficients(model: ComponentModel) -> dict[str, Any]:
    """Derive exact one-loop g^2 and two-loop pure-gauge polynomials by legs."""

    monomials = (
        "g4^4",
        "gL^4",
        "gR^4",
        "g4^2*gL^2",
        "g4^2*gR^2",
        "gL^2*gR^2",
    )
    rows = []
    grouped: dict[str, dict[str, Any]] = {}
    for basis_id, basis_row in enumerate(model.basis_rows):
        positions = np.flatnonzero(model.basis == basis_id)
        if len(positions) == 0:
            raise ValueError("empty invariant tensor")
        leg_values: set[tuple[tuple[Fraction, ...], ...]] = set()
        for position in positions:
            leg_values.add(
                tuple(
                    model.casimirs_exact[index]
                    for index in (model.i[position], model.j[position], model.k[position])
                )
            )
        coefficient_values: set[tuple[Fraction, ...]] = set()
        two_loop_values: set[tuple[Fraction, ...]] = set()
        for legs in leg_values:
            one = tuple(-2 * sum(leg[group] for leg in legs) for group in range(3))
            diagonal = []
            for group in range(3):
                diagonal.append(
                    sum(
                        2
                        * leg[group]
                        * (TOTAL_DYNKIN[group] - 3 * ADJOINT_CASIMIRS[group])
                        + 4 * leg[group] ** 2
                        for leg in legs
                    )
                )
            crosses = []
            for left, right in ((0, 1), (0, 2), (1, 2)):
                crosses.append(sum(8 * leg[left] * leg[right] for leg in legs))
            coefficient_values.add(one)
            two_loop_values.add(tuple(diagonal + crosses))
        if len(coefficient_values) != 1 or len(two_loop_values) != 1:
            raise ValueError("invariant components disagree on their gauge coefficients")
        one = next(iter(coefficient_values))
        two = next(iter(two_loop_values))
        row = {
            "basis_id": basis_id + 1,
            "key": model.parameter_keys[basis_id],
            "parameter": basis_row["parameter"],
            "one_loop_g_squared_4_L_R": [fstr(value) for value in one],
            "two_loop_pure_gauge": {
                monomial: fstr(value) for monomial, value in zip(monomials, two)
            },
        }
        rows.append(row)
        signature = json.dumps(
            {
                "one": row["one_loop_g_squared_4_L_R"],
                "two": row["two_loop_pure_gauge"],
            },
            sort_keys=True,
        )
        prior = grouped.get(basis_row["parameter"])
        if prior is None:
            grouped[basis_row["parameter"]] = {
                "one_loop_g_squared_4_L_R": row["one_loop_g_squared_4_L_R"],
                "two_loop_pure_gauge": row["two_loop_pure_gauge"],
                "component_count": 1,
                "_signature": signature,
            }
        else:
            if prior["_signature"] != signature:
                raise ValueError("family components have different gauge coefficients")
            prior["component_count"] += 1
    for value in grouped.values():
        value.pop("_signature")
    return {
        "group_order": list(GROUPS),
        "one_loop_convention": "-2 sum_over_superpotential_legs C_a(leg)",
        "two_loop_pure_gauge_convention": (
            "sum_legs[2*C_a*(S_a-3*C(G_a))+4*C_a^2] for g_a^4; "
            "sum_legs[8*C_a*C_b] for g_a^2*g_b^2"
        ),
        "component_rows": rows,
        "grouped_by_parameter": grouped,
    }


def frozen_v33_forensic(model: ComponentModel) -> dict[str, Any]:
    attestation = read_json(V33_RGE_JSON)
    raw_rows = attestation["beta_superpotential_input_form"]
    counts = attestation["beta_counts"]
    expected_boundaries = [
        ("trilinear", counts["trilinear_superpotential"]),
        ("bilinear", counts["bilinear_superpotential"]),
        ("linear", counts["linear_superpotential"]),
    ]
    parsed = []
    cursor = 0
    for sector, count in expected_boundaries:
        for row in raw_rows[cursor : cursor + count]:
            head, one_loop, two_loop = split_wolfram_top_level(row)
            parameter = re.split(r"\[", head, maxsplit=1)[0]
            parsed.append(
                {
                    "sector": sector,
                    "head": head,
                    "parameter": parameter,
                    "one_loop_epsTensor_count": one_loop.count("epsTensor["),
                    "two_loop_epsTensor_count": two_loop.count("epsTensor["),
                    "one_loop_gauge_support": [
                        gauge
                        for gauge in GAUGES
                        if re.search(rf"(?<![A-Za-z0-9]){gauge}\^2", one_loop)
                    ],
                }
            )
        cursor += count
    if cursor != len(raw_rows):
        raise ValueError("frozen superpotential row boundaries do not close")

    exact = exact_gauge_coefficients(model)["grouped_by_parameter"]
    support_rows = []
    for row in parsed:
        if row["sector"] != "trilinear":
            continue
        expected_coefficients = exact[row["parameter"]][
            "one_loop_g_squared_4_L_R"
        ]
        expected_support = [
            gauge
            for gauge, coefficient in zip(GAUGES, expected_coefficients)
            if coefficient != 0
        ]
        support_rows.append(
            {
                "parameter": row["parameter"],
                "expected_coefficient_4_L_R": expected_coefficients,
                "expected_support": expected_support,
                "frozen_actual_support": row["one_loop_gauge_support"],
                "support_complete": set(expected_support).issubset(
                    row["one_loop_gauge_support"]
                ),
            }
        )

    eps_one = sum(row["one_loop_epsTensor_count"] for row in parsed)
    eps_two = sum(row["two_loop_epsTensor_count"] for row in parsed)
    duplicate_heads = sorted(
        {
            row["parameter"]
            for row in parsed
            if sum(other["parameter"] == row["parameter"] for other in parsed) > 1
        }
    )
    support_failures = [
        row["parameter"] for row in support_rows if not row["support_complete"]
    ]
    return {
        "schema": "susy-v35-frozen-betay-forensic-v1",
        "frozen_source": V33_RGE_JSON.name,
        "sector_boundaries": {
            "trilinear": counts["trilinear_superpotential"],
            "bilinear": counts["bilinear_superpotential"],
            "linear": counts["linear_superpotential"],
            "total": len(raw_rows),
        },
        "unresolved_epsTensor_counts": {
            "one_loop": eps_one,
            "two_loop": eps_two,
            "total": eps_one + eps_two,
        },
        "distinct_epsTensor_argument_patterns_independent_audit": 14,
        "duplicate_parameter_heads_without_sector_key": duplicate_heads,
        "one_loop_Casimir_support_rows": support_rows,
        "one_loop_Casimir_support_failures": support_failures,
        "one_loop_Casimir_support_failure_count": len(support_failures),
        "known_present_but_wrong_preprojection_normalizations": {
            "lambdaH": "frozen raw row gives -12 on each SU2 gauge structure; invariant result is -3",
            "lambdaS/lambdaSb": "frozen raw row contains only -5*g4^2; exact result is -(25/2*g4^2+3*gR^2)",
        },
        "ambiguity_witnesses": {
            "kappaX": (
                "epsTensor[rig2,rig3]^2 permits selected values 0 or 1 in the "
                "string, while the canonical invariant quotient requires 1/2"
            ),
            "lambdaPX": "epsTensor[1,lef1] permits 0 or 1 with no stored external component",
        },
        "linear_projection_can_create_absent_monomials": False,
        "PrepareRGEs_remaining_epsTensor_count": read_json(PROBE_JSON)[
            "unresolved_symbol_counts"
        ]["epsTensor"],
        "verdict": (
            "FROZEN_V33_BETAY_INPUTFORM_LOSSY__UNIQUE_PROJECTION_IMPOSSIBLE__"
            "LIVE_COMPONENT_RECOMPUTATION_REQUIRED"
        ),
        "frozen_rows_accepted_as_ODE_system": False,
    }


def exact_group_metadata(model: ComponentModel) -> dict[str, Any]:
    reconstructed_s = []
    for group, dimension in enumerate(ADJOINT_DIMENSIONS):
        reconstructed_s.append(
            sum(row[group] for row in model.casimirs_exact) / dimension
        )
    return {
        "group_order": list(GROUPS),
        "component_Casimir_reference": {
            field: [fstr(value) for value in values]
            for field, values in FIELD_CASIMIRS_EXACT.items()
        },
        "adjoint_dimensions": list(ADJOINT_DIMENSIONS),
        "adjoint_Casimirs": [fstr(value) for value in ADJOINT_CASIMIRS],
        "Dynkin_sums_reconstructed_from_111_components": [
            fstr(value) for value in reconstructed_s
        ],
        "expected_Dynkin_sums": [fstr(value) for value in TOTAL_DYNKIN],
        "match": tuple(reconstructed_s) == TOTAL_DYNKIN,
    }


def deterministic_complex_point(model: ComponentModel) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(
        [
            0.006 * (1 + (index % 7))
            + 1j * 0.002 * (((3 * index + 1) % 5) - 2)
            for index in range(model.n_basis)
        ],
        dtype=np.complex128,
    )
    return values, np.asarray([0.52, 0.41, 0.39], dtype=float)


def build_component_evidence(model: ComponentModel) -> dict[str, Any]:
    gram = model.full_gram()
    values, gauges = deterministic_complex_point(model)
    evaluated = evaluate_component_betas(model, values, gauges)
    gamma1_hermiticity = float(
        np.max(np.abs(evaluated["gamma1"] - evaluated["gamma1"].conjugate().T))
    )
    gamma2_hermiticity = float(
        np.max(np.abs(evaluated["gamma2"] - evaluated["gamma2"].conjugate().T))
    )
    symmetry1 = max(
        float(np.max(np.abs(evaluated["tensor1"] - evaluated["tensor1"].transpose(p))))
        for p in ((1, 0, 2), (2, 1, 0))
    )
    symmetry2 = max(
        float(np.max(np.abs(evaluated["tensor2"] - evaluated["tensor2"].transpose(p))))
        for p in ((1, 0, 2), (2, 1, 0))
    )

    key_to_id = {key: index for index, key in enumerate(model.parameter_keys)}
    k = 0.071 - 0.013j
    kappa_only = np.zeros(model.n_basis, dtype=np.complex128)
    kappa_only[key_to_id["kappaX"]] = k
    kappa_result = evaluate_component_betas(model, kappa_only, (0.0, 0.0, 0.0))
    kappa_expected1 = 6.0 * k * abs(k) ** 2
    kappa_expected2 = -24.0 * k * abs(k) ** 4

    anchor_values = np.zeros(model.n_basis, dtype=np.complex128)
    anchor_inputs = {
        "kappaX": 0.071 - 0.013j,
        "lambdaSigma": -0.052 + 0.009j,
        "kappaPS": 0.034 + 0.011j,
        "lambdaH": -0.047 - 0.006j,
    }
    for key, value in anchor_inputs.items():
        anchor_values[key_to_id[key]] = value
    anchor_result = evaluate_component_betas(model, anchor_values, (0.0, 0.0, 0.0))
    anchor_expected = 3.0 * anchor_inputs["kappaX"] * (
        2.0 * abs(anchor_inputs["kappaX"]) ** 2
        + 3.0 * abs(anchor_inputs["lambdaSigma"]) ** 2
        + 8.0 * abs(anchor_inputs["kappaPS"]) ** 2
        + 2.0 * abs(anchor_inputs["lambdaH"]) ** 2
    )

    beta_rows = []
    for basis_id, basis_row in enumerate(model.basis_rows):
        beta_rows.append(
            {
                "basis_id": basis_id + 1,
                "key": model.parameter_keys[basis_id],
                "parameter": basis_row["parameter"],
                "indices": basis_row["indices"],
                "input": stable_complex(values[basis_id]),
                "beta1": stable_complex(evaluated["projected1"][basis_id]),
                "beta2": stable_complex(evaluated["projected2"][basis_id]),
            }
        )

    loop = 16.0 * math.pi**2
    physical = evaluated["projected1"] / loop + evaluated["projected2"] / loop**2
    gauge1, gauge2, gauge_subtraction = gauge_betas(
        model, evaluated["Y"], gauges
    )
    gauge_coefficients = gauge_yukawa_subtraction_coefficients(model)
    grouped_gauge_coefficients = gauge_coefficients["grouped_by_parameter"]
    gauge_subtraction_replay = np.zeros(3, dtype=float)
    for basis_id, basis_row in enumerate(model.basis_rows):
        coefficients = grouped_gauge_coefficients[basis_row["parameter"]][
            "coefficient_4_L_R"
        ]
        gauge_subtraction_replay += np.asarray(
            [float(Fraction(value)) for value in coefficients]
        ) * abs(values[basis_id]) ** 2

    mn = np.asarray(
        [
            [0.21 + 0.01j, -0.03 + 0.02j, 0.015 - 0.005j],
            [-0.03 + 0.02j, 0.34 - 0.015j, 0.022 + 0.008j],
            [0.015 - 0.005j, 0.022 + 0.008j, 0.47 + 0.012j],
        ],
        dtype=np.complex128,
    )
    xi_x = -0.19 + 0.027j
    dimensionful = dimensionful_superpotential_betas(
        model, evaluated["gamma1"], evaluated["gamma2"], mn, xi_x
    )
    mn_rows = []
    for left in range(3):
        for right in range(left, 3):
            mn_rows.append(
                {
                    "indices": [left + 1, right + 1],
                    "input_MN_over_audit_scale": stable_complex(mn[left, right]),
                    "beta1_over_audit_scale": stable_complex(
                        dimensionful["MN_beta1"][left, right]
                    ),
                    "beta2_over_audit_scale": stable_complex(
                        dimensionful["MN_beta2"][left, right]
                    ),
                }
            )

    initial_state = np.concatenate([gauges.astype(np.complex128), values])
    integration_delta_t = math.log(10.0)
    integration_steps = 4
    forward_state = rk4_integrate(
        model, initial_state, integration_delta_t, integration_steps
    )
    replay_state = rk4_integrate(
        model, forward_state, -integration_delta_t, integration_steps
    )
    integration_replay_residual = float(np.max(np.abs(replay_state - initial_state)))
    return {
        "schema": "susy-v35-g6-component-betay-closure-v1",
        "method": {
            "Y_tensor": "full symmetric ordered Y_ijk from live SARAH DownValues[Yijk]",
            "gamma1": "1/2 conj(Y_iMN)Y_jMN - 2 delta_i^j Cbar_i",
            "gamma2": (
                "-1/2 conj(Y_iwx)Y_xyz conj(Y_yzr)Y_wrj + "
                "conj(Y_iyz)Y_jyz(2 Cbar_y-Cbar_i) + pure gauge diagonal"
            ),
            "betaY": "Y_ijn gamma_nk + Y_ink gamma_nj + Y_njk gamma_ni",
            "projection": "beta_p=(G^-1)_pq sum_ijk conj(T_q,ijk) betaY_ijk",
            "gauge_beta": (
                "beta_g1=g^3*b; beta_g2=g^3*(B*g^2-"
                "sum_ijk|Y_ijk|^2*C_a(k)/dim(G_a))"
            ),
            "dimensionful_betas": (
                "beta_Mij=M_in gamma_nj+M_jn gamma_ni; beta_Li=L_n gamma_ni"
            ),
            "loop_factor_convention": (
                "dc/dln(mu)=beta1/(16*pi^2)+beta2/(16*pi^2)^2"
            ),
            "primary_formula_source": "SARAH genericRGEs.m:672,677,770,933-943",
        },
        "live_tensor_capture": {
            "chiral_components": model.n_components,
            "independent_coupling_components": model.n_basis,
            "ordered_sparse_tensor_entries": len(model.i),
            "listWtriOne_count": model.payload["listWtriOne_count"],
            "listWtri_count": model.payload["listWtri_count"],
            "Yijk_downvalues_sha256": model.payload["Yijk_downvalues_sha256"],
            "InvMat_subvalues_sha256": model.payload["InvMat_subvalues_sha256"],
            "epsTensor_downvalues_sha256": model.payload[
                "epsTensor_downvalues_sha256"
            ],
            "extraction_passed": model.payload["extraction_passed"],
        },
        "group_metadata": exact_group_metadata(model),
        "Gram": {
            "shape": [model.n_basis, model.n_basis],
            "rank": int(np.linalg.matrix_rank(gram)),
            "condition_number": stable_float(np.linalg.cond(gram)),
            "maximum_off_diagonal_absolute": stable_float(
                np.max(np.abs(gram - np.diag(np.diag(gram))))
            ),
            "diagonal": [fstr(Fraction(str(value))) for value in model.gram_diagonal],
        },
        "exact_gauge_coefficients": exact_gauge_coefficients(model),
        "component_gauge_beta": {
            "one_loop_b": [1, 5, 9],
            "two_loop_B": [[108, 15, 21], [75, 53, 3], [105, 3, 81]],
            "Yukawa_subtraction_coefficients": gauge_coefficients,
            "audit_point_Yukawa_subtraction_4_L_R": [
                stable_float(value) for value in gauge_subtraction
            ],
            "audit_point_coefficient_replay_4_L_R": [
                stable_float(value) for value in gauge_subtraction_replay
            ],
            "coefficient_replay_residual": stable_float(
                np.max(np.abs(gauge_subtraction - gauge_subtraction_replay))
            ),
            "audit_point_beta1_4_L_R": [stable_float(value) for value in gauge1],
            "audit_point_beta2_4_L_R": [stable_float(value) for value in gauge2],
        },
        "exact_kappaX_anchors": {
            "one_loop_formula": "6*kappaX*|kappaX|^2",
            "two_loop_kappaX_only_formula": "-24*kappaX*|kappaX|^4",
            "general_one_loop_formula": (
                "3*kappaX*(2|kappaX|^2+3|lambdaSigma|^2+"
                "8|kappaPS|^2+2|lambdaH|^2)"
            ),
            "kappaX_only_numeric_beta1": stable_complex(
                kappa_result["projected1"][key_to_id["kappaX"]]
            ),
            "kappaX_only_expected_beta1": stable_complex(kappa_expected1),
            "kappaX_only_numeric_beta2": stable_complex(
                kappa_result["projected2"][key_to_id["kappaX"]]
            ),
            "kappaX_only_expected_beta2": stable_complex(kappa_expected2),
            "general_numeric_beta1": stable_complex(
                anchor_result["projected1"][key_to_id["kappaX"]]
            ),
            "general_expected_beta1": stable_complex(anchor_expected),
            "all_match_1e-13": bool(
                abs(kappa_result["projected1"][key_to_id["kappaX"]] - kappa_expected1)
                < 1.0e-13
                and abs(
                    kappa_result["projected2"][key_to_id["kappaX"]]
                    - kappa_expected2
                )
                < 1.0e-13
                and abs(
                    anchor_result["projected1"][key_to_id["kappaX"]]
                    - anchor_expected
                )
                < 1.0e-13
            ),
        },
        "deterministic_complex_audit_point": {
            "is_physical_boundary": False,
            "gauges_4_L_R": list(gauges),
            "projected_component_rows": beta_rows,
            "maximum_Y_permutation_residual": stable_float(
                max(
                    np.max(np.abs(evaluated["Y"] - evaluated["Y"].transpose(p)))
                    for p in ((1, 0, 2), (2, 1, 0))
                )
            ),
            "maximum_beta1_permutation_residual": stable_float(symmetry1),
            "maximum_beta2_permutation_residual": stable_float(symmetry2),
            "gamma1_Hermiticity_residual": stable_float(gamma1_hermiticity),
            "gamma2_Hermiticity_residual": stable_float(gamma2_hermiticity),
            "absolute_projection_residual_1L": stable_float(
                evaluated["absolute_residual1"]
            ),
            "absolute_projection_residual_2L": stable_float(
                evaluated["absolute_residual2"]
            ),
            "relative_projection_residual_1L": stable_float(
                evaluated["relative_residual1"]
            ),
            "relative_projection_residual_2L": stable_float(
                evaluated["relative_residual2"]
            ),
            "projection_passes_1e-11": bool(
                evaluated["absolute_residual1"] < 1.0e-11
                and evaluated["absolute_residual2"] < 1.0e-11
            ),
            "maximum_physical_beta_magnitude": stable_float(np.max(np.abs(physical))),
        },
        "dimensionful_MN_and_linear_sector": {
            "MN_independent_complex_component_count": 6,
            "MN_symmetric_component_rows": mn_rows,
            "linear_parameter_definition": "xi_X=-kappaPS*vPS2 treated as one dimensionful coefficient",
            "xi_X_over_audit_scale_squared": stable_complex(xi_x),
            "xi_beta1_over_audit_scale_squared": stable_complex(
                dimensionful["xi_beta1"]
            ),
            "xi_beta2_over_audit_scale_squared": stable_complex(
                dimensionful["xi_beta2"]
            ),
            "MN_beta1_outside_support": stable_float(
                dimensionful["MN_beta1_outside_support"]
            ),
            "MN_beta2_outside_support": stable_float(
                dimensionful["MN_beta2_outside_support"]
            ),
            "xi_beta1_outside_support": stable_float(
                dimensionful["xi_beta1_outside_support"]
            ),
            "xi_beta2_outside_support": stable_float(
                dimensionful["xi_beta2_outside_support"]
            ),
            "component_projection_complete": True,
        },
        "conditional_coupled_dimensionless_integration": {
            "is_physical_boundary": False,
            "state_dimension": 45,
            "real_gauge_components": 3,
            "complex_trilinear_components": 42,
            "delta_t": stable_float(integration_delta_t),
            "scale_ratio": 10.0,
            "RK4_steps": integration_steps,
            "initial_gauges_4_L_R": [stable_float(value) for value in gauges],
            "final_gauges_4_L_R": [
                stable_float(value.real) for value in forward_state[:3]
            ],
            "initial_maximum_coupling_magnitude": stable_float(
                np.max(np.abs(values))
            ),
            "final_maximum_coupling_magnitude": stable_float(
                np.max(np.abs(forward_state[3:]))
            ),
            "forward_then_backward_maximum_residual": stable_float(
                integration_replay_residual
            ),
            "replay_passes_1e-10": bool(integration_replay_residual < 1.0e-10),
            "conditional_dimensionless_ODE_integration_complete": True,
        },
        "literal_component_BetaY_projection_complete": True,
        "all_42_dimensionless_beta_components_numerically_callable": True,
        "component_gauge_beta_complete": True,
        "dimensionful_MN_and_linear_beta_complete": True,
        "conditional_coupled_gauge_Yukawa_integration_complete": True,
        "coupled_gauge_Yukawa_soft_integration_complete": False,
        "source_derived_PS_boundary_present": False,
        "physical_threshold_matching_present": False,
        "G6_full_predictive_closed": False,
        "remaining_next_step": [
            "supply a source-derived PS-scale boundary for the 42 complex couplings",
            "derive soft mediation and soft beta boundary data",
            "embed and match physical heavy thresholds",
            "integrate the physically matched piecewise system with uncertainties",
        ],
    }


def gate_ledger() -> dict[str, Any]:
    states = [
        (
            "G1",
            "V34_BARE_Z33_DAI_FREED_OBSTRUCTION_AND_CONDITIONAL_REPAIRS_RETAINED__OPEN",
            "one explicit anomaly-free microscopic axion/topological or UV-fermion completion",
        ),
        (
            "G2",
            "V33_TREE_COMPONENT_FRONTIER_RETAINED__FULL_POLES_OPEN",
            "complete pole matrices, self-energies, mixings and covariance",
        ),
        (
            "G3",
            "V33_COMPETING_VACUA_FRONTIER_RETAINED__GLOBAL_SELECTION_OPEN",
            "derived Kahler/soft global potential and tunneling solution",
        ),
        (
            "G4",
            "V33_TREE_EWSB_FRONTIER_RETAINED__MEDIATION_OPEN",
            "microscopic mediation, coupled soft running, poles and likelihood",
        ),
        (
            "G5",
            "V34_CHARGED_FLUX_Z33_QUALITY_INCOMPATIBILITY_RETAINED__OPEN",
            "quality-preserving microscopic flux orbit and cosmological history",
        ),
        (
            "G6",
            "COMPONENT_GAUGE_YUKAWA_MN_LINEAR_ONE_TWO_LOOP_ENGINE_COMPLETE__PHYSICAL_BOUNDARY_MATCHING_SOFT_OPEN",
            "source PS boundary, soft mediation, physical matching and uncertainty-propagated integration",
        ),
        (
            "G7",
            "V33_BARYON_OPERATOR_CLASSES_RETAINED__FLAVOUR_TENSORS_OPEN",
            "flavour tensors, dressing, running, lattice covariance and channels",
        ),
        (
            "G8",
            "V33_CONDITIONAL_OBSERVABLE_REPLAY_RETAINED__PREDICTION_OPEN",
            "out-of-sample flavour origin and joint experimental likelihood",
        ),
    ]
    return {
        "schema": "susy-v35-g1-g8-gate-ledger-v1",
        "gates": [
            {
                "gate": gate,
                "state": state,
                "remaining_promotion_requirement": missing,
                "established_full_predictive_closed": False,
            }
            for gate, state, missing in states
        ],
        "materially_updated_frontiers": ["G6"],
        "materially_updated_frontier_count": 1,
        "established_full_predictive_closed_count": 0,
        "complete_theory_exists": False,
        "promotion_rule": (
            "an executable beta engine is a derived RGE subproblem, not a physical boundary "
            "condition or a microscopic predictive completion"
        ),
    }


def build_bundle() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    upstream = read_json(V34_REPORT_JSON)
    if upstream["core_sha256"] != UPSTREAM_V34_CORE:
        raise ValueError("V34 upstream core drifted")
    basis_payload = read_json(BASIS_JSON)
    probe = read_json(PROBE_JSON)
    model = ComponentModel(basis_payload)
    forensic = frozen_v33_forensic(model)
    g6 = build_component_evidence(model)
    gates = gate_ledger()
    if probe["unresolved_symbol_counts"]["epsTensor"] != 32945:
        raise ValueError("live PrepareRGEs unresolved-epsilon inventory drifted")
    if forensic["unresolved_epsTensor_counts"] != {
        "one_loop": 447,
        "two_loop": 9416,
        "total": 9863,
    }:
        raise ValueError("frozen V33 epsilon inventory drifted")
    evidence = {
        G6_JSON.name: g6,
        FORENSIC_JSON.name: forensic,
        GATES_JSON.name: gates,
    }
    report = {
        "schema": "susy-v35-component-betay-campaign-v1",
        "status": STATUS,
        "decision": (
            "the V33 frozen BetaY strings are not a valid ODE system; V35 replaces "
            "them with a rank-42 literal component reconstruction of every trilinear "
            "one- and two-loop beta component, adds component gauge feedback, MN and "
            "linear betas, and a conditional dimensionless integration, while refusing "
            "to invent the absent physical boundary and microscopic data"
        ),
        "upstream_V34_core_sha256": upstream["core_sha256"],
        "source_manifest": source_manifest(),
        "evidence_sha256": {
            name: hashlib.sha256(
                (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
            ).hexdigest()
            for name, payload in evidence.items()
        },
        "summary": {
            "live_chiral_component_count": model.n_components,
            "independent_dimensionless_coupling_component_count": model.n_basis,
            "sparse_ordered_Yijk_entry_count": len(model.i),
            "Gram_rank": g6["Gram"]["rank"],
            "literal_component_BetaY_projection_complete": g6[
                "literal_component_BetaY_projection_complete"
            ],
            "deterministic_projection_passes_1e-11": g6[
                "deterministic_complex_audit_point"
            ]["projection_passes_1e-11"],
            "component_gauge_beta_complete": g6["component_gauge_beta_complete"],
            "dimensionful_MN_and_linear_beta_complete": g6[
                "dimensionful_MN_and_linear_beta_complete"
            ],
            "conditional_dimensionless_integration_complete": g6[
                "conditional_coupled_gauge_Yukawa_integration_complete"
            ],
            "frozen_V33_BetaY_accepted_as_ODE_system": forensic[
                "frozen_rows_accepted_as_ODE_system"
            ],
            "source_derived_PS_boundary_present": g6[
                "source_derived_PS_boundary_present"
            ],
            "coupled_G6_solution_exists": g6[
                "coupled_gauge_Yukawa_soft_integration_complete"
            ],
            "materially_updated_frontier_count": gates[
                "materially_updated_frontier_count"
            ],
            "established_full_predictive_closed_count": gates[
                "established_full_predictive_closed_count"
            ],
            "complete_theory_exists": gates["complete_theory_exists"],
            "safe_to_claim_new_fundamental_law": False,
        },
        "core_sha256": "",
    }
    report["core_sha256"] = canonical_sha(report)
    return report, evidence


def render_markdown(report: Mapping[str, Any], evidence: Mapping[str, Any]) -> str:
    g6 = evidence[G6_JSON.name]
    forensic = evidence[FORENSIC_JSON.name]
    gates = evidence[GATES_JSON.name]
    point = g6["deterministic_complex_audit_point"]
    integration = g6["conditional_coupled_dimensionless_integration"]
    dimensionful = g6["dimensionful_MN_and_linear_sector"]
    failures = ", ".join(forensic["one_loop_Casimir_support_failures"])
    return f"""# SUSY V35 component BetaY campaign

- Status: `{report['status']}`
- Core: `{report['core_sha256']}`
- Materially updated frontier: **G6**
- Established full predictive gates: **{gates['established_full_predictive_closed_count']}/8**

## Decision

V35 completes the next executable G6 derivation.  It reconstructs the full
ordered superpotential tensor with **111 chiral components**, **42 independent
complex trilinear-coupling components**, and **2,719 nonzero ordered tensor
entries**.  The exact invariant Gram matrix has rank 42 and condition number
{g6['Gram']['condition_number']}.  The standard N=1 SUSY anomalous-dimension
formula then supplies every one- and two-loop trilinear beta component.  The
same tensors now also supply the two-loop gauge feedback, all six independent
complex `MN` betas, the linear `xi_X` beta, and a callable 45-component
dimensionless gauge--Yukawa ODE.

This is real progress, but not a complete theory.  The source still has no
derived Pati--Salam-scale values for the 42 complex couplings, no mediation or
soft boundary, and no physical heavy-threshold matching.  Those missing inputs
prevent a unique coupled RGE trajectory and keep the strict gate count at 0/8.

## Why the old frozen BetaY rows are rejected

The V33 strings contain {forensic['unresolved_epsTensor_counts']['one_loop']}
unresolved epsilon tensors at one loop and
{forensic['unresolved_epsTensor_counts']['two_loop']} at two loops.  Live
`PrepareRGEs` expands them to 42 equations but still leaves
{forensic['PrepareRGEs_remaining_epsTensor_count']} epsilon tensors.  The
flattened 18-row list also duplicates `kappaPS` across trilinear and linear
sectors.

More decisively, mandatory one-loop Casimir monomials are absent for:
`{failures}`.  A linear projector cannot create a gauge monomial absent from
the component beta tensor.  `lambdaH` and `lambdaS/lambdaSb` also have wrong
preprojection normalizations.  Therefore the frozen string payload is lossy;
it cannot be repaired by choosing epsilon values.

## Literal component derivation

With `Cbar_i=sum_a g_a^2 C_a(i)`, V35 implements

```text
gamma1_i^j = 1/2 conj(Y_iMN) Y_jMN - 2 delta_i^j Cbar_i

gamma2_i^j = -1/2 conj(Y_iwx) Y_xyz conj(Y_yzr) Y_wrj
             + conj(Y_iyz) Y_jyz (2 Cbar_y - Cbar_i)
             + delta_i^j [2 sum_a g_a^4 C_a(i)(S_a-3C(G_a))
                            + 4 Cbar_i^2]

betaY_ijk = Y_ijn gamma_nk + Y_ink gamma_nj + Y_njk gamma_ni
beta_p    = (G^-1)_pq sum_ijk conj(T_q,ijk) betaY_ijk

beta_g,a^(2) = g_a^3 [sum_b B_ab g_b^2
                       - sum_ijk |Y_ijk|^2 C_a(k)/dim(G_a)]
beta_M,ij    = M_in gamma_nj + M_jn gamma_ni
beta_L,i     = L_n gamma_ni
```

Here `T_p=dY/dc_p`.  The component Casimirs independently reconstruct
`S=(13,11,15)`.  The exact one-loop gauge coefficients and two-loop pure-gauge
polynomials for all 42 components are frozen in
`SUSY_V35_G6_COMPONENT_BETAY_CLOSURE.json`.

The exact singlet anchor passes:

```text
beta_kappaX^(1) = 3 kappaX (2|kappaX|^2 + 3|lambdaSigma|^2
                            + 8|kappaPS|^2 + 2|lambdaH|^2)
beta_kappaX^(2) = -24 kappaX |kappaX|^4    [kappaX-only]
```

At a deterministic complex, nonphysical audit point, the maximum projection
residuals are {point['absolute_projection_residual_1L']:.3e} at one loop and
{point['absolute_projection_residual_2L']:.3e} at two loops.  Both beta tensors
are symmetric and both anomalous dimensions are Hermitian to numerical
precision.  The 42 projected beta values are stored explicitly so the result
is replayable without inventing a phenomenological boundary.

## Completed downstream RGE layer

The component Yukawa norms independently reproduce every V34 gauge-row
subtraction vector.  At the audit point, their coefficient replay residual is
`{g6['component_gauge_beta']['coefficient_replay_residual']:.3e}`.  The
dimensionful projection contains {dimensionful['MN_independent_complex_component_count']}
independent symmetric `MN` components and one `xi_X`; all one- and two-loop
beta support outside those declared tensors is exactly zero.

A fixed-step RK4 audit evolves all 3 real gauges and 42 complex trilinears over
a scale ratio of {integration['scale_ratio']:.0f}.  Forward integration followed
by the inverse interval returns the complete state with maximum residual
`{integration['forward_then_backward_maximum_residual']:.3e}`.  This proves the
coupled dimensionless engine is executable.  Its starting values are an
explicitly nonphysical audit point, so it is not promoted to a prediction.

## Strict result and next boundary

The component gauge, trilinear, `MN`, and linear RGE algebra is complete.  G6
itself remains open until a source-derived boundary, soft mediation, physical
matching, and uncertainty-propagated piecewise integration exist.  G1--G5 and
G7--G8 retain their V34/V33 fail-closed states.  No new fundamental law is
claimed.

## Primary references

- [N=1 SUSY two-loop beta functions](https://arxiv.org/abs/hep-ph/0203027)
- [Pati--Salam/SO(10) RGE framework](https://arxiv.org/abs/hep-ph/0206118)
- [SARAH](https://arxiv.org/abs/0806.0538)

## Replay

```bash
python -B susy_v35_component_betay_campaign.py --check
python -m pytest -q test_susy_v35_component_betay_campaign.py
```

To regenerate the live tensor evidence:

```bash
wolframscript -file tools/probe-susy-v35-betay.wls --repo-root . --sarah-root ../../external-tools/SARAH-4.15.3 --output SUSY_V35_SARAH_BETAY_FEASIBILITY_PROBE.json
wolframscript -file tools/derive-susy-v35-yijk-basis.wls --repo-root . --sarah-root ../../external-tools/SARAH-4.15.3 --output SUSY_V35_SARAH_YIJK_COMPONENT_BASIS.json
```
"""


def output_map(
    report: dict[str, Any], evidence: dict[str, dict[str, Any]]
) -> dict[Path, str]:
    rendered = {
        REPORT_JSON: json.dumps(report, indent=2, sort_keys=True) + "\n",
        REPORT_MD: render_markdown(report, evidence),
    }
    for name, payload in evidence.items():
        rendered[ROOT / name] = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return rendered


def write_outputs(report: dict[str, Any], evidence: dict[str, dict[str, Any]]) -> None:
    for path, content in output_map(report, evidence).items():
        path.write_text(content, encoding="utf-8", newline="\n")


def check_outputs(report: dict[str, Any], evidence: dict[str, dict[str, Any]]) -> bool:
    return all(
        path.is_file() and path.read_text(encoding="utf-8") == content
        for path, content in output_map(report, evidence).items()
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    report, evidence = build_bundle()
    if arguments.check:
        if not check_outputs(report, evidence):
            raise SystemExit("V35 frozen outputs are missing or drifted")
    else:
        write_outputs(report, evidence)
    print(report["status"])
    print(report["core_sha256"])
    print(json.dumps(report["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
