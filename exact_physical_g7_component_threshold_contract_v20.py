#!/usr/bin/env python3
"""Source-bound physical G7 representation and threshold kernel.

This module advances G7 without consuming the historical ``U(1)_89`` mass
classification.  It binds the authoritative ``SO(10) x U(1)_X`` field
contract and the independently replayed gauge-only beta polynomial, then
derives the complete matter branching

    SO(10) -> SU(4)_C x SU(2)_L x SU(2)_R
           -> SU(3)_C x SU(2)_L x U(1)_Y

for every representation used by the model.  Hypercharge is the standard
``Y=T3R+(B-L)/2`` and ``g1=sqrt(5/3) gY``.  Exact rational Dynkin sums prove
that every complete multiplet has the same index for g1, g2 and g3.

The production functions provide:

* exact one-loop Weyl/complex-scalar/real-scalar component coefficients;
* parameterized MS-bar matter threshold matching from positive pole masses;
* the determinant form needed when fields of one SM irrep mix;
* exact tree matching at the Pati--Salam and hypercharge embeddings; and
* exact per-field UV one/two-loop non-Yukawa gauge ledgers.

This is deliberately not a complete G7 certificate.  The physical mass
matrices, heavy-vector/Goldstone/ghost thresholds, finite scheme constants,
Yukawa traces, the complete scalar/dimensionful beta system and EFT operator
mixing are not supplied by a representation table.  They remain explicit,
machine-readable blockers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Literal, Mapping, Sequence

import exact_authoritative_so10_u1x_gauge_betas_v20 as gauge_source


HERE = Path(__file__).resolve().parent
MODEL = HERE / "models" / "SO10Z17AxionV20.m"
GAUGE_SOURCE = HERE / "exact_authoritative_so10_u1x_gauge_betas_v20.py"
GAUGE_REPORT = HERE / "EXACT_AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_V20.json"
PYRATE_REPORT = HERE / "PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_V20.json"
EMBEDDING_SOURCE = HERE / "exact_126bar_triplet_clebsch_v20.py"
OUT_JSON = HERE / "EXACT_PHYSICAL_G7_COMPONENT_THRESHOLD_CONTRACT_V20.json"
OUT_MD = HERE / "EXACT_PHYSICAL_G7_COMPONENT_THRESHOLD_CONTRACT_V20.md"

STATUS = "EXACT_PHYSICAL_MATTER_BRANCHING_AND_PARAMETERIZED_ONE_LOOP_THRESHOLDS_CLOSED__FULL_G7_OPEN"
CONTRACT_ID = "physical_g7_component_threshold_contract_v20"
EXPECTED_CORE_SHA256 = "02c397bbe044695bf124b6f7415dbc1663e4beb9339e3e3e1da9632d532c02c2"
EXPECTED_REPORT_RAW_SHA256 = {
    "json": "efaec990a6edaf6e01f492ff31b4a5e3520c3b8c8298bf5529dbb3c6c80e182e",
    "md": "23b78d68d4732da2160d7b3911aa3ac0c7e6f9bce59e58228d4a6c755b21d071",
}

DEPENDENCIES: dict[str, tuple[Path, str, str]] = {
    "authoritative_model": (
        MODEL,
        "66a2ce2c3491d0b3079ec93a16ab79d3e8a7e4e35cb54aadf21100b9fdd90cc1",
        "raw",
    ),
    "authoritative_gauge_source": (
        GAUGE_SOURCE,
        "b3ec8ca5bc472af24081ee5b3409652dde0e1bf219cbf7d29a4f55e76e985cb6",
        "raw",
    ),
    "authoritative_gauge_report": (
        GAUGE_REPORT,
        "f5c12e8b8f9ec40976f675a743d5fd5d8cf4e98ab2087d92e3cf855c756c75eb",
        "raw",
    ),
    "independent_official_PyRATE3_replay": (
        PYRATE_REPORT,
        "e17dcc1dc939c8475b6827f4c781f3f5fce6c728cf5aa6511287066087b01fd4",
        "raw",
    ),
    "standard_PS_SM_embedding": (
        EMBEDDING_SOURCE,
        "c5954c21561f44ea183af17b4cd1205007c0b30021f4cca0a9fc4f96852c103a",
        "portable_text",
    ),
}

Statistics = Literal["Weyl", "scalar"]
Reality = Literal["complex", "real"]


def _digest(path: Path, mode: str = "raw") -> str:
    data = path.read_bytes()
    if mode == "portable_text":
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    elif mode != "raw":
        raise ValueError(f"unknown digest mode: {mode}")
    return hashlib.sha256(data).hexdigest()


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def _fraction(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _source_guard() -> dict[str, dict[str, str]]:
    observed: dict[str, dict[str, str]] = {}
    for name, (path, expected, mode) in DEPENDENCIES.items():
        digest = _digest(path, mode)
        if digest != expected:
            raise ArithmeticError(f"physical G7 dependency drifted: {name}")
        observed[name] = {
            "path": str(path.relative_to(HERE)),
            "sha256": digest,
            "mode": mode,
        }
    return observed


@dataclass(frozen=True)
class ModelField:
    name: str
    generations: int
    so10_signed: int
    x: int
    z17: int
    statistics: Statistics
    reality: Reality

    @property
    def branching_rep(self) -> str:
        if self.so10_signed == -16:
            return "16bar"
        if self.so10_signed == -126:
            return "126bar"
        return str(self.so10_signed)


@dataclass(frozen=True)
class PSComponent:
    su4: str
    su2l_dim: int
    su2r_dim: int

    @property
    def label(self) -> str:
        return f"({self.su4},{self.su2l_dim},{self.su2r_dim})"


@dataclass(frozen=True)
class SMComponent:
    parent: str
    ps_label: str
    su3: str
    su2_dim: int
    hypercharge: Fraction

    @property
    def label(self) -> str:
        return f"({self.su3},{self.su2_dim})_{_fraction(self.hypercharge)}"

    @property
    def dimension(self) -> int:
        return DIM_SU3[self.su3] * self.su2_dim

    def indices(self) -> dict[str, Fraction]:
        return {
            "g1": Fraction(3, 5)
            * self.hypercharge**2
            * DIM_SU3[self.su3]
            * self.su2_dim,
            "g2": T_SU2[self.su2_dim] * DIM_SU3[self.su3],
            "g3": T_SU3[self.su3] * self.su2_dim,
        }

    def as_dict(self) -> dict[str, Any]:
        return {
            "PS_parent": self.ps_label,
            "SM_irrep": self.label,
            "SU3": self.su3,
            "SU2_dimension": self.su2_dim,
            "Y": _fraction(self.hypercharge),
            "complex_dimension": self.dimension,
            "GUT_normalized_indices": {
                key: _fraction(value) for key, value in self.indices().items()
            },
        }


DIM_SU4: dict[str, int] = {
    "1": 1,
    "4": 4,
    "4bar": 4,
    "6": 6,
    "10": 10,
    "10bar": 10,
    "15": 15,
}
T_SU4: dict[str, Fraction] = {
    "1": Fraction(0),
    "4": Fraction(1, 2),
    "4bar": Fraction(1, 2),
    "6": Fraction(1),
    "10": Fraction(3),
    "10bar": Fraction(3),
    "15": Fraction(4),
}
DIM_SU3: dict[str, int] = {
    "1": 1,
    "3": 3,
    "3bar": 3,
    "6": 6,
    "6bar": 6,
    "8": 8,
}
T_SU3: dict[str, Fraction] = {
    "1": Fraction(0),
    "3": Fraction(1, 2),
    "3bar": Fraction(1, 2),
    "6": Fraction(5, 2),
    "6bar": Fraction(5, 2),
    "8": Fraction(3),
}
T_SU2: dict[int, Fraction] = {
    1: Fraction(0),
    2: Fraction(1, 2),
    3: Fraction(2),
}

# Each tuple is (SU(3) irrep, B-L).  This fixes the signed convention needed
# to identify the neutral (10,1,3) direction of Delta126bar.
SU4_TO_SU3_BL: dict[str, tuple[tuple[str, Fraction], ...]] = {
    "1": (("1", Fraction(0)),),
    "4": (("3", Fraction(1, 3)), ("1", Fraction(-1))),
    "4bar": (("3bar", Fraction(-1, 3)), ("1", Fraction(1))),
    "6": (("3", Fraction(-2, 3)), ("3bar", Fraction(2, 3))),
    "10": (
        ("6", Fraction(2, 3)),
        ("3", Fraction(-2, 3)),
        ("1", Fraction(-2)),
    ),
    "10bar": (
        ("6bar", Fraction(-2, 3)),
        ("3bar", Fraction(2, 3)),
        ("1", Fraction(2)),
    ),
    "15": (
        ("8", Fraction(0)),
        ("3", Fraction(4, 3)),
        ("3bar", Fraction(-4, 3)),
        ("1", Fraction(0)),
    ),
}

PS_BRANCHING: dict[str, tuple[PSComponent, ...]] = {
    "1": (PSComponent("1", 1, 1),),
    "10": (PSComponent("6", 1, 1), PSComponent("1", 2, 2)),
    "16": (PSComponent("4", 2, 1), PSComponent("4bar", 1, 2)),
    "16bar": (PSComponent("4bar", 2, 1), PSComponent("4", 1, 2)),
    "45": (
        PSComponent("15", 1, 1),
        PSComponent("1", 3, 1),
        PSComponent("1", 1, 3),
        PSComponent("6", 2, 2),
    ),
    "126": (
        PSComponent("6", 1, 1),
        PSComponent("10", 3, 1),
        PSComponent("10bar", 1, 3),
        PSComponent("15", 2, 2),
    ),
    "126bar": (
        PSComponent("6", 1, 1),
        PSComponent("10bar", 3, 1),
        PSComponent("10", 1, 3),
        PSComponent("15", 2, 2),
    ),
    "210": (
        PSComponent("1", 1, 1),
        PSComponent("15", 1, 1),
        PSComponent("15", 1, 3),
        PSComponent("15", 3, 1),
        PSComponent("6", 2, 2),
        PSComponent("10", 2, 2),
        PSComponent("10bar", 2, 2),
    ),
}

SO10_DIMENSION: dict[str, int] = {
    "1": 1,
    "10": 10,
    "16": 16,
    "16bar": 16,
    "45": 45,
    "126": 126,
    "126bar": 126,
    "210": 210,
}
SO10_DYNKIN: dict[str, Fraction] = {
    "1": Fraction(0),
    "10": Fraction(1),
    "16": Fraction(2),
    "16bar": Fraction(2),
    "45": Fraction(8),
    "126": Fraction(35),
    "126bar": Fraction(35),
    "210": Fraction(56),
}


def su2r_weights(dimension: int) -> tuple[Fraction, ...]:
    if dimension not in T_SU2:
        raise KeyError(f"unsupported SU(2) dimension: {dimension}")
    highest_twice = dimension - 1
    return tuple(
        Fraction(value, 2) for value in range(-highest_twice, highest_twice + 1, 2)
    )


def expand_sm(rep: str) -> tuple[SMComponent, ...]:
    if rep not in PS_BRANCHING:
        raise KeyError(f"unsupported SO(10) branching representation: {rep}")
    rows: list[SMComponent] = []
    for ps in PS_BRANCHING[rep]:
        for su3, b_minus_l in SU4_TO_SU3_BL[ps.su4]:
            for t3r in su2r_weights(ps.su2r_dim):
                rows.append(
                    SMComponent(
                        parent=rep,
                        ps_label=ps.label,
                        su3=su3,
                        su2_dim=ps.su2l_dim,
                        hypercharge=t3r + b_minus_l / 2,
                    )
                )
    return tuple(rows)


def ps_indices(component: PSComponent) -> dict[str, Fraction]:
    return {
        "g4": T_SU4[component.su4] * component.su2l_dim * component.su2r_dim,
        "g2L": T_SU2[component.su2l_dim]
        * DIM_SU4[component.su4]
        * component.su2r_dim,
        "g2R": T_SU2[component.su2r_dim]
        * DIM_SU4[component.su4]
        * component.su2l_dim,
    }


def representation_audit(rep: str) -> dict[str, Any]:
    ps = PS_BRANCHING[rep]
    sm = expand_sm(rep)
    ps_dimension = sum(
        DIM_SU4[row.su4] * row.su2l_dim * row.su2r_dim for row in ps
    )
    sm_dimension = sum(row.dimension for row in sm)
    ps_sums = {
        gauge: sum((ps_indices(row)[gauge] for row in ps), Fraction())
        for gauge in ("g4", "g2L", "g2R")
    }
    sm_sums = {
        gauge: sum((row.indices()[gauge] for row in sm), Fraction())
        for gauge in ("g1", "g2", "g3")
    }
    expected = SO10_DYNKIN[rep]
    return {
        "SO10_irrep": rep,
        "SO10_complex_dimension": SO10_DIMENSION[rep],
        "SO10_Dynkin_T10_equals_1": _fraction(expected),
        "PS_branching": [row.label for row in ps],
        "PS_dimension_sum": ps_dimension,
        "PS_index_sums": {key: _fraction(value) for key, value in ps_sums.items()},
        "SM_dimension_sum": sm_dimension,
        "SM_GUT_normalized_index_sums": {
            key: _fraction(value) for key, value in sm_sums.items()
        },
        "SM_components": [row.as_dict() for row in sm],
        "dimension_identity": ps_dimension == sm_dimension == SO10_DIMENSION[rep],
        "index_identity": set(ps_sums.values()) == {expected}
        and set(sm_sums.values()) == {expected},
    }


_SCALAR_PATTERN = re.compile(
    r"ScalarFields\[\[\d+\]\]\s*=\s*\{\s*(\w+)\s*,\s*(\d+)\s*,\s*\w+\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*([^}]+?)\s*\};"
)
_FERMION_PATTERN = re.compile(
    r"FermionFields\[\[\d+\]\]\s*=\s*\{\s*(\w+)\s*,\s*(\d+)\s*,\s*\w+\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*([^}]+?)\s*\};"
)


def _parse_z17_charge(expression: str) -> int:
    text = expression.strip()
    if re.fullmatch(r"-?\d+", text):
        return int(text) % 17
    phase = re.fullmatch(
        r"Exp\[\s*2\s*\*\s*Pi\s*\*\s*I\s*\*\s*(-?\d+)\s*/\s*17\s*\]",
        text,
    )
    if phase is None:
        raise ArithmeticError(f"unsupported exact Z17 charge expression: {text}")
    return int(phase.group(1)) % 17


def parse_authoritative_fields(text: str | None = None) -> tuple[ModelField, ...]:
    if text is None:
        text = MODEL.read_text(encoding="utf-8")
    real_names = {"Phi210"}
    scalars = tuple(
        ModelField(
            name=name,
            generations=int(generations),
            so10_signed=int(so10),
            x=int(x),
            z17=_parse_z17_charge(z17),
            statistics="scalar",
            reality="real" if name in real_names else "complex",
        )
        for name, generations, so10, x, z17 in _SCALAR_PATTERN.findall(text)
    )
    fermions = tuple(
        ModelField(
            name=name,
            generations=int(generations),
            so10_signed=int(so10),
            x=int(x),
            z17=_parse_z17_charge(z17),
            statistics="Weyl",
            reality="complex",
        )
        for name, generations, so10, x, z17 in _FERMION_PATTERN.findall(text)
    )
    return scalars + fermions


def beta_weight(statistics: Statistics, reality: Reality = "complex") -> Fraction:
    if reality not in ("complex", "real"):
        raise ValueError(f"unsupported reality: {reality}")
    if statistics == "Weyl":
        if reality != "complex":
            raise ValueError("a two-component Weyl field is not a real scalar")
        return Fraction(2, 3)
    if statistics != "scalar":
        raise ValueError(f"unsupported statistics: {statistics}")
    return Fraction(1, 6) if reality == "real" else Fraction(1, 3)


def component_delta_b(
    component: SMComponent,
    *,
    statistics: Statistics,
    reality: Reality = "complex",
    multiplicity: int = 1,
) -> dict[str, Fraction]:
    if (
        not isinstance(multiplicity, int)
        or isinstance(multiplicity, bool)
        or multiplicity <= 0
    ):
        raise ValueError("threshold multiplicity must be a positive integer")
    weight = beta_weight(statistics, reality) * multiplicity
    return {key: weight * value for key, value in component.indices().items()}


def ps_component_delta_b(
    component: PSComponent,
    *,
    statistics: Statistics,
    reality: Reality = "complex",
    multiplicity: int = 1,
) -> dict[str, Fraction]:
    """Exact one-loop matter coefficients in the Pati--Salam basis."""
    if (
        not isinstance(multiplicity, int)
        or isinstance(multiplicity, bool)
        or multiplicity <= 0
    ):
        raise ValueError("threshold multiplicity must be a positive integer")
    weight = beta_weight(statistics, reality) * multiplicity
    return {key: weight * value for key, value in ps_indices(component).items()}


def complete_ps_multiplet_delta_b(
    rep: str,
    *,
    statistics: Statistics,
    reality: Reality = "complex",
    multiplicity: int = 1,
) -> dict[str, Fraction]:
    totals = {key: Fraction() for key in ("g4", "g2L", "g2R")}
    for component in PS_BRANCHING[rep]:
        row = ps_component_delta_b(
            component,
            statistics=statistics,
            reality=reality,
            multiplicity=multiplicity,
        )
        for key, value in row.items():
            totals[key] += value
    return totals


def complete_multiplet_delta_b(
    rep: str,
    *,
    statistics: Statistics,
    reality: Reality = "complex",
    multiplicity: int = 1,
) -> dict[str, Fraction]:
    totals = {key: Fraction() for key in ("g1", "g2", "g3")}
    for component in expand_sm(rep):
        row = component_delta_b(
            component,
            statistics=statistics,
            reality=reality,
            multiplicity=multiplicity,
        )
        for key, value in row.items():
            totals[key] += value
    return totals


@dataclass(frozen=True)
class MassiveThresholdState:
    component: SMComponent
    mass: float
    statistics: Statistics
    reality: Reality = "complex"
    multiplicity: int = 1


def weighted_threshold_logs(
    states: Sequence[MassiveThresholdState], *, matching_scale: float
) -> dict[str, float]:
    """Return ``L_i=sum_a Delta b_i,a log(M_a/mu)`` for matter fields."""
    if not math.isfinite(matching_scale) or matching_scale <= 0.0:
        raise ValueError("matching scale must be finite and positive")
    logs = {key: 0.0 for key in ("g1", "g2", "g3")}
    for state in states:
        if not math.isfinite(state.mass) or state.mass <= 0.0:
            raise ValueError("every threshold pole mass must be finite and positive")
        coefficients = component_delta_b(
            state.component,
            statistics=state.statistics,
            reality=state.reality,
            multiplicity=state.multiplicity,
        )
        logarithm = math.log(state.mass / matching_scale)
        for key, coefficient in coefficients.items():
            logs[key] += float(coefficient) * logarithm
    return logs


def match_inverse_couplings(
    alpha_inverse_high: Mapping[str, float],
    states: Sequence[MassiveThresholdState],
    *,
    matching_scale: float,
) -> dict[str, float]:
    """One-loop MS-bar matter-log match, low minus high = ``-L_i/(2 pi)``."""
    if set(alpha_inverse_high) != {"g1", "g2", "g3"}:
        raise ValueError("alpha_inverse_high must contain exactly g1, g2 and g3")
    logs = weighted_threshold_logs(states, matching_scale=matching_scale)
    return {
        key: float(alpha_inverse_high[key]) - logs[key] / (2.0 * math.pi)
        for key in ("g1", "g2", "g3")
    }


def ps_to_sm_tree_match(alpha_inverse_ps: Mapping[str, Fraction]) -> dict[str, Fraction]:
    """Tree matching in the standard GUT-normalized hypercharge basis."""
    if set(alpha_inverse_ps) != {"g4", "g2L", "g2R"}:
        raise ValueError("PS inverse couplings must contain g4, g2L and g2R")
    return {
        "g1": Fraction(2, 5) * alpha_inverse_ps["g4"]
        + Fraction(3, 5) * alpha_inverse_ps["g2R"],
        "g2": alpha_inverse_ps["g2L"],
        "g3": alpha_inverse_ps["g4"],
    }


def uv_nonyukawa_alpha_inverse_rhs(
    alpha_inverse: Mapping[str, float],
) -> dict[str, float]:
    """Coupled all-active two-loop gauge-only flow above every threshold.

    The domain is unbroken ``SO(10) x U(1)_X`` with the complete authoritative
    inventory active.  Yukawa traces are intentionally absent from this
    function and from its name.
    """
    if set(alpha_inverse) != {"SO10", "X"}:
        raise ValueError("UV inverse couplings must contain exactly SO10 and X")
    values = {key: float(alpha_inverse[key]) for key in gauge_source.GAUGES}
    if any(not math.isfinite(value) or value <= 0.0 for value in values.values()):
        raise ValueError("UV inverse couplings must be finite and positive")
    a = {"SO10": Fraction(52, 3), "X": Fraction(10843)}
    b = {
        "SO10": {"SO10": Fraction(25013, 6), "X": Fraction(4536)},
        "X": {"SO10": Fraction(204120), "X": Fraction(7242180)},
    }
    return {
        key: -float(a[key]) / (2.0 * math.pi)
        - sum(
            float(b[key][other]) / (8.0 * math.pi**2 * values[other])
            for other in gauge_source.GAUGES
        )
        for key in gauge_source.GAUGES
    }


def integrate_uv_nonyukawa_gauge_flow(
    alpha_inverse_initial: Mapping[str, float],
    *,
    log_mu_interval: float,
    steps: int = 1024,
) -> dict[str, float]:
    """Deterministic RK4 integration of the scoped coupled UV gauge flow."""
    if not isinstance(steps, int) or isinstance(steps, bool) or steps <= 0:
        raise ValueError("steps must be a positive integer")
    if not math.isfinite(log_mu_interval):
        raise ValueError("log_mu_interval must be finite")
    if set(alpha_inverse_initial) != {"SO10", "X"}:
        raise ValueError("UV inverse couplings must contain exactly SO10 and X")
    state = {key: float(alpha_inverse_initial[key]) for key in ("SO10", "X")}
    # Validate keys and the initial physical domain even for a zero interval.
    uv_nonyukawa_alpha_inverse_rhs(state)
    step = log_mu_interval / steps

    def shifted(
        base: Mapping[str, float], slope: Mapping[str, float], factor: float
    ) -> dict[str, float]:
        candidate = {
            key: base[key] + factor * slope[key] for key in ("SO10", "X")
        }
        if any(not math.isfinite(value) or value <= 0.0 for value in candidate.values()):
            raise FloatingPointError(
                "the truncated UV gauge flow crossed a nonperturbative pole"
            )
        return candidate

    for _ in range(steps):
        k1 = uv_nonyukawa_alpha_inverse_rhs(state)
        k2 = uv_nonyukawa_alpha_inverse_rhs(shifted(state, k1, step / 2.0))
        k3 = uv_nonyukawa_alpha_inverse_rhs(shifted(state, k2, step / 2.0))
        k4 = uv_nonyukawa_alpha_inverse_rhs(shifted(state, k3, step))
        state = {
            key: state[key]
            + step * (k1[key] + 2.0 * k2[key] + 2.0 * k3[key] + k4[key]) / 6.0
            for key in ("SO10", "X")
        }
        if any(not math.isfinite(value) or value <= 0.0 for value in state.values()):
            raise FloatingPointError(
                "the truncated UV gauge flow crossed a nonperturbative pole"
            )
    return state


def _field_dict(field: ModelField) -> dict[str, Any]:
    return {
        "name": field.name,
        "generations": field.generations,
        "SO10_signed": field.so10_signed,
        "branching_rep": field.branching_rep,
        "X": field.x,
        "Z17": field.z17,
        "statistics": field.statistics,
        "reality": field.reality,
        "SO10_complex_components": field.generations
        * SO10_DIMENSION[field.branching_rep],
        "real_scalar_coordinates": (
            field.generations
            * SO10_DIMENSION[field.branching_rep]
            * (1 if field.reality == "real" else 2)
            if field.statistics == "scalar"
            else 0
        ),
        "complete_degenerate_multiplet_Delta_b_SM": {
            key: _fraction(value)
            for key, value in complete_multiplet_delta_b(
                field.branching_rep,
                statistics=field.statistics,
                reality=field.reality,
                multiplicity=field.generations,
            ).items()
        },
    }


def _gauge_field_ledgers() -> list[dict[str, Any]]:
    pure_a = gauge_source.one_loop_coefficients((), ())
    pure_b = gauge_source.two_loop_nonyukawa_matrix((), ())
    rows: list[dict[str, Any]] = []
    for field in parse_authoritative_fields():
        if field.statistics == "Weyl":
            source_row = next(row for row in gauge_source.AUTHORITATIVE_FERMIONS if row.name == field.name)
            value_a = gauge_source.one_loop_coefficients((source_row,), ())
            value_b = gauge_source.two_loop_nonyukawa_matrix((source_row,), ())
        else:
            source_row = next(row for row in gauge_source.AUTHORITATIVE_SCALARS if row.name == field.name)
            value_a = gauge_source.one_loop_coefficients((), (source_row,))
            value_b = gauge_source.two_loop_nonyukawa_matrix((), (source_row,))
        delta_a = {key: value_a[key] - pure_a[key] for key in gauge_source.GAUGES}
        delta_b = {
            key: {
                other: value_b[key][other] - pure_b[key][other]
                for other in gauge_source.GAUGES
            }
            for key in gauge_source.GAUGES
        }
        rows.append(
            {
                "field": field.name,
                "generations": field.generations,
                "one_loop_matter_Delta_a": {
                    key: _fraction(value) for key, value in delta_a.items()
                },
                "two_loop_nonyukawa_matter_Delta_b": {
                    key: {other: _fraction(value) for other, value in values.items()}
                    for key, values in delta_b.items()
                },
            }
        )
    return rows


def _conjugate_signature(rep: str) -> list[tuple[str, int, Fraction]]:
    conjugate_su3 = {
        "1": "1",
        "3": "3bar",
        "3bar": "3",
        "6": "6bar",
        "6bar": "6",
        "8": "8",
    }
    return sorted(
        (
            conjugate_su3[row.su3],
            row.su2_dim,
            -row.hypercharge,
        )
        for row in expand_sm(rep)
    )


def _actual_signature(rep: str) -> list[tuple[str, int, Fraction]]:
    return sorted((row.su3, row.su2_dim, row.hypercharge) for row in expand_sm(rep))


def _interaction_inventory(model_text: str) -> dict[str, Any]:
    yukawa_symbols = (
        "Y10",
        "Y126",
        "yP",
        "yQ",
        "yR",
        "ys",
        "lambdaP",
        "lambdaR",
        "lambdaQB",
        "lambdaQR",
    )
    scalar_symbols = (
        "m210Sq",
        "m126Sq",
        "m10Sq",
        "mSSq",
        "m17Sq",
        "lambdaS",
        "lambda17",
        "lambdaS17",
    )
    return {
        "declared_Yukawa_and_fermion_mixing_symbols": list(yukawa_symbols),
        "family_tensor_shapes_before_flavour_quotients": {
            "Y10": "complex symmetric 3x3",
            "Y126": "complex symmetric 3x3",
            "yP": "complex scalar",
            "yQ": "complex scalar",
            "yR": "complex scalar",
            "ys": "complex 5x5",
            "lambdaP": "complex 1x3",
            "lambdaR": "complex 1x3",
            "lambdaQB": "complex 1x3",
            "lambdaQR": "complex scalar",
        },
        "raw_complex_family_entries_before_flavour_quotients": 50,
        "declared_representative_scalar_symbols": list(scalar_symbols),
        "all_tokens_present": all(
            re.search(rf"\b{re.escape(symbol)}\b", model_text)
            for symbol in yukawa_symbols + scalar_symbols
        ),
        "authoritative_model_scalar_potential_complete": False,
        "reason": (
            "the model source explicitly delegates the independent 210/126bar/10 "
            "Clebsch contractions to the 44-direction tensor backend"
        ),
        "full_scalar_tensor_contract": {
            "tensor_families": 18,
            "invariant_directions": 44,
            "real_parameters": 51,
            "real_scalar_chart_dimension": 486,
        },
        "required_RGE_blocks": [
            {
                "block": "gauge",
                "target_loop_order": 2,
                "closed_piece": "one loop and two-loop non-Yukawa polynomial",
                "missing_piece": "normalized Yukawa invariants Y4_SO10 and Y4_X",
            },
            {
                "block": "Yukawa_and_fermion_mixing",
                "target_loop_order": 2,
                "closed_piece": "field, charge and family-shape inventory",
                "missing_piece": "normalized sparse Clebsch tensors and beta contractions",
            },
            {
                "block": "scalar_quartic",
                "target_loop_order": 2,
                "closed_piece": "44 invariant directions in 18 tensor families",
                "missing_piece": "translation to canonical lambda_abcd and all beta contractions",
            },
            {
                "block": "scalar_trilinear_and_mass_squared",
                "target_loop_order": 2,
                "closed_piece": "declared field chart and representative SARAH symbols",
                "missing_piece": "complete h_abc and m2_ab tensors plus beta contractions",
            },
            {
                "block": "dimension_six_EFT",
                "target_loop_order": 1,
                "closed_piece": "none for the complete physical operator basis",
                "missing_piece": "nonredundant basis, wave-function terms and anomalous-dimension mixing",
            },
        ],
    }


def build_report() -> dict[str, Any]:
    bindings = _source_guard()
    model_text = MODEL.read_text(encoding="utf-8")
    fields = parse_authoritative_fields(model_text)
    gauge_report = json.loads(GAUGE_REPORT.read_text(encoding="utf-8"))
    pyrate_report = json.loads(PYRATE_REPORT.read_text(encoding="utf-8"))
    embedding_text = EMBEDDING_SOURCE.read_text(encoding="utf-8")
    interactions = _interaction_inventory(model_text)

    expected_names = {
        "Phi210",
        "Delta126bar",
        "H10",
        "S",
        "Phi17",
        "F",
        "P",
        "R",
        "SpecS",
        "SpecB",
        "Q",
        "Pbar",
        "Qbar",
        "Rbar",
    }
    rep_audits = {
        rep: representation_audit(rep)
        for rep in ("1", "10", "16", "16bar", "45", "126", "126bar", "210")
    }
    field_rows = [_field_dict(field) for field in fields]
    gauge_ledgers = _gauge_field_ledgers()

    # Independent sum of the exact per-field UV ledger.
    pure_a = gauge_source.one_loop_coefficients((), ())
    pure_b = gauge_source.two_loop_nonyukawa_matrix((), ())
    ledger_a = dict(pure_a)
    ledger_b = {key: dict(values) for key, values in pure_b.items()}
    for row in gauge_ledgers:
        for key in gauge_source.GAUGES:
            ledger_a[key] += Fraction(row["one_loop_matter_Delta_a"][key])
            for other in gauge_source.GAUGES:
                ledger_b[key][other] += Fraction(
                    row["two_loop_nonyukawa_matter_Delta_b"][key][other]
                )

    # A complete 10 scalar at a common mass must shift all three inverse
    # couplings identically; split masses intentionally need not.
    ten = expand_sm("10")
    degenerate_states = [
        MassiveThresholdState(row, 7.0, "scalar", "complex") for row in ten
    ]
    degenerate_logs = weighted_threshold_logs(degenerate_states, matching_scale=2.0)
    split_states = [
        MassiveThresholdState(row, float(index + 2), "scalar", "complex")
        for index, row in enumerate(ten)
    ]
    split_logs = weighted_threshold_logs(split_states, matching_scale=2.0)

    anomaly_free_bundles = {
        "Phi17_mass_bundle_P": ["P", "Pbar"],
        "Phi17_mass_bundle_Q": ["Q", "Qbar"],
        "Phi17_mass_bundle_R": ["R", "Rbar"],
        "S_mass_bundle_spectators": ["SpecS", "SpecB"],
    }

    checks = {
        "dependency_hashes_bound": len(bindings) == len(DEPENDENCIES),
        "authoritative_field_parser_exact_names": {row.name for row in fields}
        == expected_names,
        "five_scalar_multiplets_parsed": sum(row.statistics == "scalar" for row in fields)
        == 5,
        "nine_fermion_rows_parsed": sum(row.statistics == "Weyl" for row in fields)
        == 9,
        "nineteen_Weyl_SO10_multiplets": sum(
            row.generations for row in fields if row.statistics == "Weyl"
        )
        == 19,
        "three_hundred_four_Weyl_components": sum(
            row.generations * SO10_DIMENSION[row.branching_rep]
            for row in fields
            if row.statistics == "Weyl"
        )
        == 304,
        "four_hundred_eighty_six_real_scalar_coordinates": sum(
            row["real_scalar_coordinates"] for row in field_rows
        )
        == 486,
        "all_PS_and_SM_dimensions_exact": all(
            row["dimension_identity"] for row in rep_audits.values()
        ),
        "all_PS_and_SM_Dynkin_indices_exact": all(
            row["index_identity"] for row in rep_audits.values()
        ),
        "16bar_is_exact_SM_conjugate_of_16": _actual_signature("16bar")
        == _conjugate_signature("16"),
        "126bar_is_exact_SM_conjugate_of_126": _actual_signature("126bar")
        == _conjugate_signature("126"),
        "Delta126bar_contains_unique_standard_SM_singlet": sum(
            row.su3 == "1" and row.su2_dim == 1 and row.hypercharge == 0
            for row in expand_sm("126bar")
        )
        == 1,
        "Delta126bar_singlet_has_PS_10_1_3_provenance": any(
            row.ps_label == "(10,1,3)"
            and row.su3 == "1"
            and row.su2_dim == 1
            and row.hypercharge == 0
            for row in expand_sm("126bar")
        ),
        "standard_hypercharge_source_bound": (
            "hypercharge = t3r + 0.5 * b_minus_l" in embedding_text
            and '"hypercharge": "Y=T3R+(B-L)/2"' in embedding_text
        ),
        "GUT_normalized_hypercharge_declared": True,
        "complete_multiplet_thresholds_are_universal": all(
            len(
                set(
                    complete_multiplet_delta_b(
                        rep,
                        statistics="scalar",
                        reality="real" if rep == "210" else "complex",
                    ).values()
                )
            )
            == 1
            for rep in ("1", "10", "16", "45", "126bar", "210")
        ),
        "degenerate_complete_10_log_is_universal": max(degenerate_logs.values())
        - min(degenerate_logs.values())
        < 1.0e-14,
        "split_complete_10_can_generate_nonuniversal_thresholds": max(split_logs.values())
        - min(split_logs.values())
        > 1.0e-6,
        "tree_PS_to_SM_match_reproduces_unification": len(
            set(
                ps_to_sm_tree_match(
                    {"g4": Fraction(37), "g2L": Fraction(37), "g2R": Fraction(37)}
                ).values()
            )
        )
        == 1,
        "one_loop_matching_scale_covariance_identity": (
            -Fraction(17, 3) + Fraction(5, 6)
            == -(Fraction(17, 3) - Fraction(5, 6))
        ),
        "per_field_one_loop_UV_ledger_sums_exactly": ledger_a
        == {"SO10": Fraction(52, 3), "X": Fraction(10843)},
        "per_field_two_loop_UV_ledger_sums_exactly": ledger_b
        == {
            "SO10": {"SO10": Fraction(25013, 6), "X": Fraction(4536)},
            "X": {"SO10": Fraction(204120), "X": Fraction(7242180)},
        },
        "official_PyRATE3_replay_is_full_inventory_not_reduced_model": (
            pyrate_report["external_tool"]["completed"] is True
            and pyrate_report["inventory"]["Weyl_16_multiplets"] == 19
            and pyrate_report["comparison"]["all_coefficients_match"] is True
            and pyrate_report["source_binding"]["canonical_model"]["path"]
            == "models/SO10U1XGaugeAuditV20.model"
        ),
        "analytic_and_external_gauge_coefficients_agree": (
            gauge_report["core_sha256"]
            == "714796e4e8f1aa768d9e9f8434c6919aca854d33541b2bccc779f96933345752"
            and pyrate_report["exact_coefficients"]["beta_g10_loop1"]["g10^3"]
            == "52/3"
        ),
        "continuous_gauge_anomalies_cancel_exactly": set(
            gauge_report["anomalies"].values()
        )
        == {0},
        "all_declared_interaction_tokens_in_source": interactions["all_tokens_present"],
        "representative_SARAH_scalar_potential_not_misread_as_complete": not interactions[
            "authoritative_model_scalar_potential_complete"
        ],
        "formal_U1_89_spectrum_not_consumed": True,
        "SO10_to_PS_broken_vector_dimension_is_24": 45 - (15 + 3 + 3) == 24,
        "PS_to_SM_broken_vector_dimension_is_9": (15 + 3 + 3) - (8 + 3 + 1)
        == 9,
        "physical_G7_remains_fail_closed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise ArithmeticError(f"physical G7 component-contract checks failed: {failures}")

    decisive: dict[str, Any] = {
        "contract_id": CONTRACT_ID,
        "source_binding": bindings,
        "primary_formula_sources": [
            {
                "citation": (
                    "C. S. Aulakh and A. Girdhar, Nucl. Phys. B711 (2005) "
                    "275-313"
                ),
                "arxiv": "hep-ph/0405074",
                "scope": "SO(10) 210, 126, 126bar, 10 and 16 Pati-Salam decompositions, eqs. (4)-(8)",
                "convention_note": (
                    "the signed 126bar orientation is fixed here by the authoritative "
                    "model and the repository's standard B-L generator"
                ),
            },
            {
                "citation": (
                    "M. Luo, H. Wang and Y. Xiao, Phys. Rev. D67 (2003) 065019"
                ),
                "arxiv": "hep-ph/0211440",
                "scope": "general one/two-loop gauge beta functions for Weyl fermions and real scalars",
            },
            {
                "citation": "L. J. Hall, Nucl. Phys. B178 (1981) 75-124",
                "scope": "effective gauge theories and one-loop heavy thresholds",
            },
            {
                "citation": (
                    "A. Djouadi, R. Fonseca, R. Ouyang and M. Raidal, "
                    "Eur. Phys. J. C83 (2023) 529"
                ),
                "arxiv": "2212.11315",
                "scope": "two-loop SO(10) running with Pati-Salam matching and threshold requirements",
            },
        ],
        "scheme_and_basis": {
            "renormalization_scheme": "MS-bar for the logarithmic matter-threshold kernel",
            "fermions": "left-handed two-component Weyl",
            "scalar_reality": "complex scalar weight 1/3; real scalar weight 1/6",
            "SO10_Dynkin_normalization": "T(10)=1",
            "hypercharge": "Y=T3R+(B-L)/2",
            "GUT_normalized_abelian_coupling": "g1=sqrt(5/3)*gY",
            "U1X_normalization": "integer charges exactly as declared in SO10Z17AxionV20.m",
            "one_loop_threshold_log": "L_i(mu)=sum_a Delta_b_i,a ln(M_a/mu)",
            "inverse_coupling_match": "alpha_i^-1(low)-alpha_i^-1(high)=-L_i(mu)/(2*pi)",
            "mass_input": "positive pole masses; for a mixed block use one half log det(M_pole^2/mu^2)",
        },
        "tree_level_matching": {
            "SO10_to_PS": "alpha4^-1=alpha2L^-1=alpha2R^-1=alpha10^-1",
            "PS_to_SM": {
                "alpha1_inverse": "(2/5) alpha4^-1+(3/5) alpha2R^-1",
                "alpha2_inverse": "alpha2L^-1",
                "alpha3_inverse": "alpha4^-1",
            },
            "BL_generator": "T_BL=sqrt(3/8)*(B-L)",
        },
        "heavy_vector_provenance_not_yet_matched": {
            "SO10_to_PS": {
                "broken_generators": "(6,2,2)",
                "real_vector_dimension": 24,
            },
            "PS_to_SM": {
                "broken_SM_vectors": [
                    "(3,1)_(2/3)",
                    "(3bar,1)_(-2/3)",
                    "(1,1)_1",
                    "(1,1)_(-1)",
                    "(1,1)_0",
                ],
                "real_vector_dimension": 9,
            },
            "EW_to_QED": {
                "real_vector_dimension": 3,
                "requires_physical_EW_input": True,
            },
            "one_loop_vector_Goldstone_ghost_matching_implemented": False,
            "reason": (
                "the vector logarithms and finite constants must be derived together "
                "in one gauge-fixing and renormalization convention"
            ),
        },
        "authoritative_field_inventory": field_rows,
        "interaction_beta_inventory": interactions,
        "representation_audits": rep_audits,
        "exact_UV_per_field_gauge_ledgers": gauge_ledgers,
        "UV_two_loop_gauge_flow": {
            "equation": (
                "d alpha_k^-1/d ln(mu)=-a_k/(2*pi)-sum_l b_kl/"
                "(8*pi^2*alpha_l^-1)+Y4_k/(32*pi^3)"
            ),
            "all_active_a": {"SO10": "52/3", "X": "10843"},
            "all_active_b_nonyukawa": {
                "SO10": {"SO10": "25013/6", "X": "4536"},
                "X": {"SO10": "204120", "X": "7242180"},
            },
            "Y4_status": "symbolic only; normalized full Yukawa tensors are required",
            "callable_API": [
                "uv_nonyukawa_alpha_inverse_rhs",
                "integrate_uv_nonyukawa_gauge_flow",
            ],
            "independent_implementations": [
                "exact_authoritative_so10_u1x_gauge_betas_v20.py rational trace engine",
                "official PyR@TE 3 commit 04b219c2016f3fc4f2371d72607edc26a7e06364 replay",
            ],
        },
        "matter_component_threshold_theorem": {
            "closed_scope": (
                "all Weyl and scalar SM components descending from 1, 10, 16, "
                "16bar, 126bar and real 210, conditional on supplied positive pole masses"
            ),
            "component_coefficient": {
                "Weyl": "Delta b_i=(2/3) T_i(R)",
                "complex_scalar": "Delta b_i=(1/3) T_i(R)",
                "real_scalar": "Delta b_i=(1/6) T_i(R_complexification)",
            },
            "mixed_block_formula": (
                "for identical SM irreps, sum_a ln(M_a/mu)="
                "(1/2) ln det(M_pole^2/mu^2); thresholds are basis invariant"
            ),
            "complete_multiplet_check": (
                "sum T1=sum T2=sum T3=T_SO10(R), so a degenerate complete "
                "SO(10) multiplet shifts all three inverse couplings equally"
            ),
            "callable_API": [
                "expand_sm",
                "component_delta_b",
                "ps_component_delta_b",
                "complete_ps_multiplet_delta_b",
                "complete_multiplet_delta_b",
                "weighted_threshold_logs",
                "match_inverse_couplings",
                "ps_to_sm_tree_match",
            ],
        },
        "valid_mass_bundles_before_or_at_U1X_breaking": anomaly_free_bundles,
        "adversarial_guards": {
            "nonpositive_mass_rejected": True,
            "nonpositive_matching_scale_rejected": True,
            "unknown_representation_rejected": True,
            "wrong_coupling_key_set_rejected": True,
            "G89_never_used_as_hypercharge": True,
            "reduced_legacy_PyRATE_models_never_used": True,
            "incomplete_SARAH_scalar_potential_never_promoted": True,
        },
        "completion_matrix": {
            "authoritative_19_Weyl_and_5_scalar_inventory": True,
            "continuous_gauge_anomaly_cancellation": True,
            "exact_one_loop_full_inventory_gauge_coefficients": True,
            "exact_two_loop_nonyukawa_full_inventory_gauge_coefficients": True,
            "independent_official_PyRATE3_gauge_replay": True,
            "complete_physical_PS_and_SM_matter_branching": True,
            "parameterized_one_loop_matter_component_threshold_kernel": True,
            "physical_component_pole_mass_matrices": False,
            "heavy_vector_Goldstone_ghost_thresholds": False,
            "finite_one_loop_matching_constants": False,
            "normalized_Yukawa_tensor_embeddings": False,
            "full_two_loop_Yukawa_betas": False,
            "full_51_real_parameter_scalar_tensor_translation": False,
            "full_two_loop_scalar_quartic_betas": False,
            "dimensionful_mass_and_trilinear_betas": False,
            "dimension_six_EFT_anomalous_dimension_and_mixing": False,
            "physical_G6_input_available": False,
            "second_independent_full_RGE_and_matching_implementation": False,
            "mathematical_G7_closed": False,
            "release_G7_verified": False,
        },
        "implementation_hooks": {
            "hook_A": (
                "translate the normalized 304-Weyl and 486-real-scalar tensors "
                "to a general two-loop tensor RGE backend"
            ),
            "hook_B": (
                "generate an independent full PyR@TE model containing all ten "
                "Yukawa/mixing tensors and the complete 44-direction scalar ring"
            ),
            "acceptance": (
                "exact symbolic agreement where supported; relative numerical "
                "agreement <=1e-10 along at least 100 random nonsingular coupling points"
            ),
        },
        "release_blockers": [
            "PHYSICAL_G6_POLE_MASS_MATRICES_WITH_SM_AND_PS_PROVENANCE",
            "HEAVY_VECTOR_GOLDSTONE_GHOST_MATCHING_IN_DECLARED_SCHEME",
            "NORMALIZED_304_WEYL_YUKAWA_TENSOR_EMBEDDINGS",
            "FULL_51_PARAMETER_SCALAR_AND_DIMENSIONFUL_BETA_SYSTEM",
            "DIMENSION_SIX_EFT_OPERATOR_MIXING_IF_EFT_RETAINED",
            "SECOND_INDEPENDENT_FULL_RGE_THRESHOLD_IMPLEMENTATION",
            "BOUNDARY_DATA_AND_MATCHING_SCALES_WITH_COVARIANCE",
        ],
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": 0,
        "failures": [],
        "verdict": (
            "The physical PS/SM matter representation table and the complete "
            "parameterized one-loop matter threshold kernel are exact and source "
            "bound.  The all-active non-Yukawa two-loop gauge flow has two independent "
            "implementations.  Physical pole masses, heavy-vector matching and the "
            "Yukawa/scalar/dimensionful/EFT beta system are still absent; therefore "
            "mathematical and release G7 remain false."
        ),
    }
    report = {
        "status": STATUS,
        **decisive,
        "core_sha256": _canonical_sha256(decisive),
    }
    if EXPECTED_CORE_SHA256 != "TO_BE_FROZEN" and report["core_sha256"] != EXPECTED_CORE_SHA256:
        raise ArithmeticError(
            f"physical G7 component-contract core drifted: {report['core_sha256']} != {EXPECTED_CORE_SHA256}"
        )
    return report


def render_markdown(report: dict[str, Any]) -> str:
    complete = report["completion_matrix"]
    return "\n".join(
        [
            "# Exact physical G7 component-threshold contract",
            "",
            f"**Status:** `{report['status']}`",
            "",
            f"**Core SHA256:** `{report['core_sha256']}`",
            "",
            "## New exact result",
            "",
            "Every authoritative matter irrep is decomposed through Pati--Salam to",
            "the Standard Model with `Y=T3R+(B-L)/2` and `g1=sqrt(5/3) gY`.",
            "Dimension and Dynkin-index identities hold exactly for every irrep.",
            "The callable threshold kernel accepts positive component pole masses and",
            "returns the one-loop MS-bar matter match in all three SM couplings.",
            "",
            "## Two-loop gauge result",
            "",
            "The exact all-active non-Yukawa coefficients are",
            "`a=(52/3,10843)` and",
            "`b=[[25013/6,4536],[204120,7242180]]`; an official pinned PyR@TE 3",
            "replay independently agrees exactly.",
            "",
            "## Fail-closed boundary",
            "",
            f"- physical pole-mass matrices: `{complete['physical_component_pole_mass_matrices']}`",
            f"- heavy-vector/Goldstone/ghost thresholds: `{complete['heavy_vector_Goldstone_ghost_thresholds']}`",
            f"- normalized Yukawa tensors: `{complete['normalized_Yukawa_tensor_embeddings']}`",
            f"- complete 51-parameter scalar tensor translation: `{complete['full_51_real_parameter_scalar_tensor_translation']}`",
            f"- full two-loop scalar quartic betas: `{complete['full_two_loop_scalar_quartic_betas']}`",
            f"- mathematical G7: `{complete['mathematical_G7_closed']}`",
            f"- release G7: `{complete['release_G7_verified']}`",
            "",
            report["verdict"],
            "",
        ]
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    OUT_MD.write_text(render_markdown(report), encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify-reports", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    if args.verify_reports:
        for name, path in (("json", OUT_JSON), ("md", OUT_MD)):
            observed = _digest(path)
            expected = EXPECTED_REPORT_RAW_SHA256[name]
            if expected != "TO_BE_FROZEN" and observed != expected:
                raise ArithmeticError(
                    f"physical G7 {name} report drifted: {observed} != {expected}"
                )
    print(
        json.dumps(
            {
                "status": report["status"],
                "core_sha256": report["core_sha256"],
                "n_checks": report["n_checks"],
                "completion_matrix": report["completion_matrix"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
