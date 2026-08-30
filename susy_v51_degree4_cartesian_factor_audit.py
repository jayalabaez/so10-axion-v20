#!/usr/bin/env python3
"""Exact V51 degree-four source-collar factor/copy audit.

The V49 retained action lists 120 charge-neutral rows with two bulk spinors
and two source chirals, but deliberately leaves each compact-Spin(10) Haar
image abstract.  This module resolves those images without guessing:

* exact D5 Weyl characters determine every row multiplicity;
* the bosonic Sym^2 quotient is imposed for repeated source fields;
* every nonzero channel is instantiated by normalized Cartesian form or
  Clifford factors, with deterministic raw-array hashes; and
* empty rows are retained as rigorous representation-intersection zeros.

This closes the degree-four *factor/copy basis* only.  It does not emit the
source-to-PS Wilson coefficient array, a physical mediator/link Lagrangian,
or any one-loop matching data, so C7 as a whole and G2 remain fail-closed.
"""

from __future__ import annotations

import argparse
import copy
import functools
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Mapping

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as forms
import exact_normalized_so10_yukawa_cgcs_v20 as yukawa
import g1_exact_declared_symmetry_character_census_v20 as characters
import susy_v50_c7_conjugate_incidence_audit as v50_c7
import susy_v50_clifford_tensor_extension_audit as clifford


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V51_DEGREE4_CARTESIAN_FACTOR_AUDIT.json"
MD_PATH = ROOT / "SUSY_V51_DEGREE4_CARTESIAN_FACTOR_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v51_degree4_cartesian_factor_audit.py"
UPSTREAM_V51 = ROOT / "SUSY_V51_CARTESIAN_MEDIATOR_C5_C7_FEASIBILITY_AUDIT.json"
UPSTREAM_V50 = ROOT / "SUSY_V50_C7_CONJUGATE_INCIDENCE_AUDIT.json"
EXPECTED_V51_CORE = "cce7c67c44e1a0f164bd226cbf7307054cd16b20604202b5d95e1083983a5da0"
STATUS = (
    "V51_ALL_120_DEGREE4_ROWS_EXACTLY_RESOLVED__"
    "76_EMPTY_44_NONEMPTY_72_NORMALIZED_CARTESIAN_DIRECTIONS__"
    "C7_DEGREE4_FACTOR_BASIS_CLOSED__FINAL_WILSON_ARRAY_AND_C5_OPEN__G2_OPEN"
)

DIMENSION = {"1": 1, "10": 10, "45": 45, "120": 120, "126": 126,
             "bar126": 126, "210": 210}
CONJUGATE_REP = {
    "1": "1", "10": "10", "45": "45", "120": "120",
    "126": "bar126", "bar126": "126", "210": "210",
}
FORM_DEGREE = {"1": 0, "10": 1, "45": 2, "120": 3, "210": 4,
               "126": 5, "bar126": 5}


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


def array_sha256(value: np.ndarray) -> str:
    array = np.ascontiguousarray(np.asarray(value, dtype=np.complex128))
    return hashlib.sha256(array.view(np.uint8).tobytes()).hexdigest()


def maximum_abs(value: np.ndarray) -> float:
    array = np.asarray(value)
    return float(np.max(np.abs(array))) if array.size else 0.0


def _add_characters(*values: Counter[tuple[int, ...]]) -> Counter[tuple[int, ...]]:
    result: Counter[tuple[int, ...]] = Counter()
    for value in values:
        result.update(value)
    return characters.clean(result)


@functools.lru_cache(maxsize=None)
def representation_character(label: str) -> Counter[tuple[int, ...]]:
    vector = characters.vector()
    registry = {
        "1": Counter({characters.ZERO: 1}),
        "10": vector,
        "16": characters.spinor(),
        "bar16": Counter(
            {tuple(-entry for entry in weight): multiplicity
             for weight, multiplicity in characters.spinor().items()}
        ),
        "45": characters.exterior(list(vector.elements()), 2),
        "120": characters.exterior(list(vector.elements()), 3),
        "126": characters.r126(),
        "bar126": characters.r126b(),
        "210": characters.r210(),
    }
    if label not in registry:
        raise KeyError(f"unknown Spin(10) representation {label}")
    return registry[label]


def spinor_channels(orientation: tuple[str, str]) -> dict[str, Counter[tuple[int, ...]]]:
    if orientation == ("16", "16"):
        labels = ("10", "120", "126")
    elif orientation == ("bar16", "bar16"):
        labels = ("10", "120", "bar126")
    elif orientation in (("16", "bar16"), ("bar16", "16")):
        labels = ("1", "45", "210")
    else:
        raise ValueError(f"unsupported ordered spinor orientation {orientation}")
    return {label: representation_character(label) for label in labels}


def exact_spinor_product_decompositions() -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for orientation in (
        ("16", "16"), ("bar16", "bar16"),
        ("16", "bar16"), ("bar16", "16"),
    ):
        direct = characters.tensor(
            representation_character(orientation[0]),
            representation_character(orientation[1]),
        )
        resolved = _add_characters(*spinor_channels(orientation).values())
        checks["x".join(orientation)] = direct == resolved
    return checks


@functools.lru_cache(maxsize=None)
def source_pair_character(sources: tuple[str, str]) -> Counter[tuple[int, ...]]:
    left, right = sources
    if left == right and left != "1":
        # V49 combinations_with_replacement means a repeated nontrivial source
        # is one commuting chiral species and therefore belongs to Sym^2(R).
        return characters.sym(representation_character(left), 2)
    return characters.tensor(
        representation_character(left), representation_character(right)
    )


@functools.lru_cache(maxsize=None)
def channel_multiplicities(
    orientation: tuple[str, str], sources: tuple[str, str]
) -> dict[str, int]:
    source = source_pair_character(sources)
    return {
        label: characters.singlet(characters.tensor(source, channel))
        for label, channel in spinor_channels(orientation).items()
    }


def bosonic_symmetry_kill_certificate() -> dict[str, Any]:
    channels = spinor_channels(("16", "bar16"))
    symmetric = characters.sym(representation_character("210"), 2)
    wrongly_ordered = characters.tensor(
        representation_character("210"), representation_character("210")
    )
    correct = {
        label: characters.singlet(characters.tensor(symmetric, channel))
        for label, channel in channels.items()
    }
    wrong = {
        label: characters.singlet(characters.tensor(wrongly_ordered, channel))
        for label, channel in channels.items()
    }
    return {
        "source_pair": "Phi Phi in Sym^2(210)",
        "correct_channel_multiplicities": correct,
        "incorrect_ordered_tensor_square_multiplicities": wrong,
        "correct_total": sum(correct.values()),
        "incorrect_total": sum(wrong.values()),
        "overcount_if_bosonic_quotient_is_dropped": sum(wrong.values()) - sum(correct.values()),
    }


@functools.lru_cache(maxsize=None)
def _labels(degree: int) -> tuple[tuple[int, ...], ...]:
    return tuple(itertools.combinations(range(10), degree))


@functools.lru_cache(maxsize=None)
def _minus_basis() -> tuple[dict[tuple[int, ...], complex], ...]:
    return tuple(forms.anti_self_dual_five_form_basis())


@functools.lru_cache(maxsize=None)
def _plus_basis() -> tuple[dict[tuple[int, ...], complex], ...]:
    return tuple(
        {indices: complex(value).conjugate() for indices, value in state.items()}
        for state in _minus_basis()
    )


@functools.lru_cache(maxsize=None)
def basis_states(label: str) -> tuple[dict[tuple[int, ...], complex], ...]:
    if label == "1":
        return ({(): 1.0 + 0.0j},)
    if label in ("10", "45", "120", "210"):
        return tuple({indices: 1.0 + 0.0j} for indices in _labels(FORM_DEGREE[label]))
    if label == "126":
        return _plus_basis()
    if label == "bar126":
        return _minus_basis()
    raise KeyError(label)


def _permutation_sign(sequence: tuple[int, ...]) -> int:
    inversions = sum(
        sequence[i] > sequence[j]
        for i in range(len(sequence))
        for j in range(i + 1, len(sequence))
    )
    return -1 if inversions % 2 else 1


def _interior_sign(indices: tuple[int, ...], contracted: tuple[int, ...]) -> tuple[tuple[int, ...], int]:
    residual = list(indices)
    sign = 1
    for index in contracted:
        position = residual.index(index)
        sign *= -1 if position % 2 else 1
        residual.pop(position)
    return tuple(residual), sign


@functools.lru_cache(maxsize=None)
def _singleton_kernel(
    left: tuple[int, ...],
    right: tuple[int, ...],
    contracted_degree: int,
    hodge_output: bool,
) -> tuple[tuple[int, ...], complex] | None:
    common = tuple(sorted(set(left).intersection(right)))
    if len(common) != contracted_degree:
        return None
    left_residual, left_sign = _interior_sign(left, common)
    right_residual, right_sign = _interior_sign(right, common)
    if set(left_residual).intersection(right_residual):
        return None
    sequence = left_residual + right_residual
    output = tuple(sorted(sequence))
    coefficient = complex(
        left_sign * right_sign * _permutation_sign(sequence)
    )
    if hodge_output:
        complement = tuple(index for index in range(10) if index not in output)
        coefficient *= _permutation_sign(output + complement)
        output = complement
    return output, coefficient


def _project_hodge(form: forms.Form, output_rep: str) -> forms.Form:
    if output_rep not in ("126", "bar126"):
        return form
    # plus-i uses (1-i*)/2; minus-i uses (1+i*)/2.
    phase = -1j if output_rep == "126" else 1j
    return forms.scale_form(
        forms.add_forms(form, forms.scale_form(forms.hodge_star(form), phase)),
        0.5,
    )


def bilinear_form_map(
    left: forms.Form,
    right: forms.Form,
    *,
    contracted_degree: int,
    hodge_output: bool = False,
    output_rep: str,
) -> forms.Form:
    output: dict[tuple[int, ...], complex] = {}
    for left_indices, left_value in left.items():
        for right_indices, right_value in right.items():
            kernel = _singleton_kernel(
                left_indices, right_indices, contracted_degree, hodge_output
            )
            if kernel is None:
                continue
            indices, coefficient = kernel
            output[indices] = (
                output.get(indices, 0.0)
                + left_value * right_value * coefficient
            )
    output = {
        indices: value for indices, value in output.items()
        if abs(value) > 1.0e-13
    }
    return _project_hodge(output, output_rep)


def _output_coordinates(form: forms.Form, output_rep: str) -> np.ndarray:
    if output_rep in ("126", "bar126"):
        basis = basis_states(output_rep)
        return np.asarray(
            [0.5 * forms.tensor_inner(state, form) for state in basis],
            dtype=complex,
        )
    position = {indices: index for index, indices in enumerate(_labels(FORM_DEGREE[output_rep]))}
    result = np.zeros(DIMENSION[output_rep], dtype=complex)
    for indices, value in form.items():
        result[position[indices]] = value
    return result


SOURCE_FACTOR_SPECS: dict[str, dict[str, Any]] = {
    "SRC_1x1_TO_1": {"inputs": ("1", "1"), "output": "1", "r": 0, "scale": 1},
    "SRC_1x210_TO_210": {"inputs": ("1", "210"), "output": "210", "r": 0, "scale": 1},
    "SRC_1x126_TO_126": {"inputs": ("1", "126"), "output": "126", "r": 0, "scale": 1},
    "SRC_1xbar126_TO_bar126": {"inputs": ("1", "bar126"), "output": "bar126", "r": 0, "scale": 1},
    "SRC_PHIxPHI_TO_1": {"inputs": ("210", "210"), "output": "1", "r": 4, "scale": 210, "symmetric": True},
    "SRC_PHIxPHI_TO_45": {"inputs": ("210", "210"), "output": "45", "r": 0, "hodge": True, "scale": 70, "symmetric": True},
    "SRC_PHIxPHI_TO_210": {"inputs": ("210", "210"), "output": "210", "r": 2, "scale": 90, "symmetric": True},
    "SRC_SIGMAxBARSIGMA_TO_1": {"inputs": ("126", "bar126"), "output": "1", "r": 5, "scale": 504},
    "SRC_SIGMAxBARSIGMA_TO_45": {"inputs": ("126", "bar126"), "output": "45", "r": 4, "scale": 280},
    "SRC_SIGMAxBARSIGMA_TO_210": {"inputs": ("126", "bar126"), "output": "210", "r": 3, "scale": 240},
    "SRC_PHIxSIGMA_TO_10": {"inputs": ("210", "126"), "output": "10", "r": 4, "scale": 126},
    "SRC_PHIxSIGMA_TO_120": {"inputs": ("210", "126"), "output": "120", "r": 3, "scale": 105},
    "SRC_PHIxSIGMA_TO_126": {"inputs": ("210", "126"), "output": "126", "r": 2, "scale": 100},
    "SRC_PHIxBARSIGMA_TO_10": {"inputs": ("210", "bar126"), "output": "10", "r": 4, "scale": 126},
    "SRC_PHIxBARSIGMA_TO_120": {"inputs": ("210", "bar126"), "output": "120", "r": 3, "scale": 105},
    "SRC_PHIxBARSIGMA_TO_bar126": {"inputs": ("210", "bar126"), "output": "bar126", "r": 2, "scale": 100},
}


@functools.lru_cache(maxsize=None)
def source_factor_array(identifier: str) -> np.ndarray:
    spec = SOURCE_FACTOR_SPECS[identifier]
    left_basis = basis_states(spec["inputs"][0])
    right_basis = basis_states(spec["inputs"][1])
    result = np.zeros(
        (DIMENSION[spec["output"]], len(left_basis), len(right_basis)),
        dtype=complex,
    )
    for left_index, left in enumerate(left_basis):
        for right_index, right in enumerate(right_basis):
            image = bilinear_form_map(
                left,
                right,
                contracted_degree=int(spec["r"]),
                hodge_output=bool(spec.get("hodge", False)),
                output_rep=str(spec["output"]),
            )
            result[:, left_index, right_index] = _output_coordinates(
                image, str(spec["output"])
            )
    return result


def _seed_form(degree: int, offset: int, count: int = 17) -> forms.Form:
    labels = _labels(degree)
    picked = [labels[(offset + 13 * index) % len(labels)] for index in range(min(count, len(labels)))]
    return {
        indices: complex(((7 * index + offset) % 11) - 5, ((5 * index + 2 * offset) % 9) - 4)
        for index, indices in enumerate(picked)
    }


def _seed_for_rep(label: str, offset: int) -> forms.Form:
    if label == "1":
        return {(): complex(offset + 1)}
    value = _seed_form(FORM_DEGREE[label], offset)
    return _project_hodge(value, label)


def covariance_witness(identifier: str) -> dict[str, float]:
    spec = SOURCE_FACTOR_SPECS[identifier]
    left = _seed_for_rep(spec["inputs"][0], 2)
    # Scalar contractions require overlapping supports; use the same support
    # offset there so the covariance witness cannot pass vacuously.
    right_offset = 2 if spec["output"] == "1" and spec["inputs"] != ("1", "1") else 7
    right = _seed_for_rep(spec["inputs"][1], right_offset)

    def operation(first: forms.Form, second: forms.Form) -> forms.Form:
        return bilinear_form_map(
            first,
            second,
            contracted_degree=int(spec["r"]),
            hodge_output=bool(spec.get("hodge", False)),
            output_rep=str(spec["output"]),
        )

    seed_output_norm = forms.tensor_norm(operation(left, right))
    worst = 0.0
    for a, b in itertools.combinations(range(10), 2):
        left_side = forms.generator_action(operation(left, right), a, b)
        right_side = forms.add_forms(
            operation(forms.generator_action(left, a, b), right),
            operation(left, forms.generator_action(right, a, b)),
        )
        worst = max(
            worst,
            forms.tensor_norm(
                forms.add_forms(left_side, forms.scale_form(right_side, -1.0))
            ),
        )
    return {
        "seed_output_norm": seed_output_norm,
        "all_45_generator_residual": worst,
    }


@functools.lru_cache(maxsize=1)
def normalized_source_factor_registry() -> dict[str, dict[str, Any]]:
    registry: dict[str, dict[str, Any]] = {}
    covariance_cache: dict[tuple[Any, ...], dict[str, float]] = {}
    for identifier, spec in SOURCE_FACTOR_SPECS.items():
        raw = source_factor_array(identifier)
        gram = np.einsum("oab,pab->op", raw.conjugate(), raw)
        scale = float(spec["scale"])
        normalized_gram_residual = maximum_abs(
            gram / scale - np.eye(DIMENSION[spec["output"]])
        )
        raw_isotropy_residual = maximum_abs(
            gram - scale * np.eye(DIMENSION[spec["output"]])
        )
        symmetry_residual = None
        if spec.get("symmetric"):
            symmetry_residual = maximum_abs(raw - raw.swapaxes(1, 2))
        covariance_key = (
            spec["inputs"], spec["output"], spec["r"], bool(spec.get("hodge", False))
        )
        if covariance_key not in covariance_cache:
            covariance_cache[covariance_key] = covariance_witness(identifier)
        registry[identifier] = {
            "input_representations": list(spec["inputs"]),
            "output_representation": spec["output"],
            "raw_shape": list(raw.shape),
            "raw_array_sha256": array_sha256(raw),
            "raw_gram_scale": int(spec["scale"]),
            "raw_gram_isotropy_residual": raw_isotropy_residual,
            "normalized_gram_residual": normalized_gram_residual,
            "covariance_seed_output_norm": covariance_cache[covariance_key]["seed_output_norm"],
            "all_45_generator_seed_covariance_residual": covariance_cache[covariance_key]["all_45_generator_residual"],
            "output_rank_from_positive_gram": DIMENSION[spec["output"]],
            "bosonic_exchange_symmetry_residual": symmetry_residual,
            "normalization": f"raw Cartesian map divided by sqrt({int(spec['scale'])})",
            "construction": (
                ("Hodge dual of the exterior product" if spec.get("hodge") else
                 f"contract exactly {int(spec['r'])} common exterior-form indices")
                + (f" and project to {spec['output']} Hodge chirality"
                   if spec["output"] in ("126", "bar126") else "")
            ),
        }
        # Keep peak memory bounded; the cached constructor can be cleared only
        # after the digest and Gram certificate have been emitted.
        source_factor_array.cache_clear()
    return registry


def _spin_factor_array(orientation: tuple[str, str], channel: str) -> np.ndarray:
    if orientation == ("16", "16"):
        if channel == "10":
            return yukawa.cgc_10().numerator / yukawa.cgc_10().denominator
        if channel == "120":
            return clifford.kform_tensor(3, -1, -1)
        if channel == "126":
            tensor = yukawa.cgc_126bar()
            return tensor.numerator / tensor.denominator
    if orientation == ("bar16", "bar16"):
        conjugate = _spin_factor_array(("16", "16"), CONJUGATE_REP[channel])
        return conjugate.conjugate()
    if orientation == ("16", "bar16"):
        degree = {"1": 0, "45": 2, "210": 4}[channel]
        return clifford.kform_tensor(degree, -1, +1)
    if orientation == ("bar16", "16"):
        degree = {"1": 0, "45": 2, "210": 4}[channel]
        return clifford.kform_tensor(degree, +1, -1)
    raise KeyError((orientation, channel))


@functools.lru_cache(maxsize=1)
def normalized_spin_factor_registry() -> dict[str, dict[str, Any]]:
    registry: dict[str, dict[str, Any]] = {}
    for orientation in (
        ("16", "16"), ("bar16", "bar16"),
        ("16", "bar16"), ("bar16", "16"),
    ):
        for channel in spinor_channels(orientation):
            identifier = f"SPIN_{orientation[0]}x{orientation[1]}_TO_{channel}"
            tensor = np.asarray(_spin_factor_array(orientation, channel), dtype=complex)
            gram = np.einsum("oij,pij->op", tensor.conjugate(), tensor)
            registry[identifier] = {
                "ordered_chirality": list(orientation),
                "output_representation": channel,
                "shape": list(tensor.shape),
                "array_sha256": array_sha256(tensor),
                "normalized_gram_residual": maximum_abs(
                    gram - np.eye(DIMENSION[channel])
                ),
                "normalization": "ordered-spinor-pair Hilbert--Schmidt Gram identity",
                "provenance": (
                    "exact_normalized_so10_yukawa_cgcs_v20"
                    if channel in ("10", "126", "bar126")
                    else "susy_v50_clifford_tensor_extension_audit.kform_tensor"
                ),
            }
    return registry


def source_factor_id(sources: tuple[str, str], spin_channel: str) -> str:
    required_output = CONJUGATE_REP[spin_channel]
    key = (sources, required_output)
    registry = {
        (("1", "1"), "1"): "SRC_1x1_TO_1",
        (("1", "210"), "210"): "SRC_1x210_TO_210",
        (("1", "126"), "126"): "SRC_1x126_TO_126",
        (("1", "bar126"), "bar126"): "SRC_1xbar126_TO_bar126",
        (("210", "210"), "1"): "SRC_PHIxPHI_TO_1",
        (("210", "210"), "45"): "SRC_PHIxPHI_TO_45",
        (("210", "210"), "210"): "SRC_PHIxPHI_TO_210",
        (("126", "bar126"), "1"): "SRC_SIGMAxBARSIGMA_TO_1",
        (("126", "bar126"), "45"): "SRC_SIGMAxBARSIGMA_TO_45",
        (("126", "bar126"), "210"): "SRC_SIGMAxBARSIGMA_TO_210",
        (("210", "126"), "10"): "SRC_PHIxSIGMA_TO_10",
        (("210", "126"), "120"): "SRC_PHIxSIGMA_TO_120",
        (("210", "126"), "126"): "SRC_PHIxSIGMA_TO_126",
        (("210", "bar126"), "10"): "SRC_PHIxBARSIGMA_TO_10",
        (("210", "bar126"), "120"): "SRC_PHIxBARSIGMA_TO_120",
        (("210", "bar126"), "bar126"): "SRC_PHIxBARSIGMA_TO_bar126",
    }
    if key not in registry:
        raise KeyError(f"no source factor for sources={sources}, channel={spin_channel}")
    return registry[key]


def resolve_degree_four_row(row: Mapping[str, Any]) -> dict[str, Any]:
    if int(row["degree"]) != 4 or row["sector"] not in ("HH", "HcHc", "HcH"):
        raise ValueError("only V49 degree-four two-bulk rows are accepted")
    orientation = tuple(str(value) for value in row["ordered_chirality"])
    sources = tuple(str(value) for value in row["source_representations"])
    if len(orientation) != 2 or len(sources) != 2:
        raise ValueError(f"malformed degree-four row {row['id']}")
    multiplicities = channel_multiplicities(orientation, sources)
    directions: list[dict[str, Any]] = []
    for channel, multiplicity in multiplicities.items():
        for copy_index in range(1, multiplicity + 1):
            spin_id = f"SPIN_{orientation[0]}x{orientation[1]}_TO_{channel}"
            source_id = source_factor_id(sources, channel)
            directions.append(
                {
                    "direction_id": f"{row['id']}__{channel}__copy_{copy_index}",
                    "channel_representation": channel,
                    "source_output_representation": CONJUGATE_REP[channel],
                    "channel_copy_index": copy_index,
                    "spin_factor_tensor_id": spin_id,
                    "source_factor_tensor_id": source_id,
                    "normalized_composite_tensor_id": (
                        f"NORM_INV__{spin_id}__PAIR__{source_id}__COPY_{copy_index}"
                    ),
                    "normalized_composite_formula": (
                        f"(1/sqrt({DIMENSION[channel]})) sum_o "
                        "T_spin[o] T_source[o]"
                    ),
                }
            )
    multiplicity = len(directions)
    return {
        "id": row["id"],
        "sector": row["sector"],
        "degree": 4,
        "monomial": row["monomial"],
        "bulk_fields": list(row["bulk_fields"]),
        "ordered_chirality": list(orientation),
        "source_representations": list(sources),
        "U1F_charge": row["U1F_charge"],
        "source_pair_rule": (
            "Sym^2 of one commuting nontrivial source species"
            if sources[0] == sources[1] and sources[0] != "1"
            else "ordered representation product; field monomial fixes species"
        ),
        "spinor_channel_intersection_multiplicities": multiplicities,
        "invariant_multiplicity": multiplicity,
        "instantiation_status": (
            "RESOLVED_EMPTY_EXACT_D5_INTERSECTION"
            if multiplicity == 0
            else "RESOLVED_NONEMPTY_NORMALIZED_CARTESIAN_FACTORS"
        ),
        "directions": directions,
        "zero_reason": (
            "the exact D5 source-pair character contains none of the conjugates "
            "of the three irreducible spinor-product channels"
            if multiplicity == 0 else None
        ),
    }


@functools.lru_cache(maxsize=1)
def degree_four_rows() -> tuple[dict[str, Any], ...]:
    rows = [
        row for row in v50_c7.census()
        if row["sector"] in ("HH", "HcHc", "HcH") and int(row["degree"]) == 4
    ]
    return tuple(resolve_degree_four_row(row) for row in rows)


def degree_four_certificate() -> dict[str, Any]:
    rows = list(degree_four_rows())
    histogram = Counter(int(row["invariant_multiplicity"]) for row in rows)
    status_histogram = Counter(str(row["instantiation_status"]) for row in rows)
    by_sector = {
        sector: {
            "rows": sum(row["sector"] == sector for row in rows),
            "zero_rows": sum(
                row["sector"] == sector and row["invariant_multiplicity"] == 0
                for row in rows
            ),
            "nonempty_rows": sum(
                row["sector"] == sector and row["invariant_multiplicity"] > 0
                for row in rows
            ),
            "invariant_directions": sum(
                int(row["invariant_multiplicity"])
                for row in rows if row["sector"] == sector
            ),
        }
        for sector in ("HH", "HcHc", "HcH")
    }
    channel_histogram = Counter(
        direction["channel_representation"]
        for row in rows for direction in row["directions"]
    )
    return {
        "total_rows": len(rows),
        "zero_rows": histogram[0],
        "nonempty_rows": len(rows) - histogram[0],
        "total_invariant_directions": sum(
            int(row["invariant_multiplicity"]) for row in rows
        ),
        "multiplicity_histogram": {
            str(key): value for key, value in sorted(histogram.items())
        },
        "status_histogram": dict(sorted(status_histogram.items())),
        "by_sector": by_sector,
        "direction_channel_histogram": dict(sorted(channel_histogram.items())),
        "all_nonzero_copy_multiplicities_one": all(
            multiplicity in (0, 1)
            for row in rows
            for multiplicity in row["spinor_channel_intersection_multiplicities"].values()
        ),
        "rows": rows,
    }


def _load_upstream() -> dict[str, Any]:
    if not UPSTREAM_V51.is_file():
        raise RuntimeError(f"missing upstream {UPSTREAM_V51.name}")
    value = json.loads(UPSTREAM_V51.read_text(encoding="utf-8"))
    if value.get("core_sha256") != EXPECTED_V51_CORE:
        raise RuntimeError(
            f"V51 C5/C7 upstream core drifted: {value.get('core_sha256')}"
        )
    return value


@functools.lru_cache(maxsize=1)
def _build_report_cached() -> dict[str, Any]:
    upstream = _load_upstream()
    certificate = degree_four_certificate()
    source_registry = normalized_source_factor_registry()
    spin_registry = normalized_spin_factor_registry()
    all_directions = [
        direction
        for row in certificate["rows"]
        for direction in row["directions"]
    ]
    symmetry_kill = bosonic_symmetry_kill_certificate()
    checks = {
        "upstream_v51_repaired_core_bound": upstream["core_sha256"] == EXPECTED_V51_CORE,
        "all_four_spinor_products_exactly_decomposed": all(
            exact_spinor_product_decompositions().values()
        ),
        "all_120_rows_resolved": certificate["total_rows"] == 120,
        "exact_76_zero_44_nonempty_split": (
            certificate["zero_rows"] == 76 and certificate["nonempty_rows"] == 44
        ),
        "exact_72_direction_count": certificate["total_invariant_directions"] == 72,
        "multiplicity_histogram_0_76_1_28_2_4_3_12": (
            certificate["multiplicity_histogram"]
            == {"0": 76, "1": 28, "2": 4, "3": 12}
        ),
        "sector_direction_counts_16_16_40": (
            certificate["by_sector"]["HH"]["invariant_directions"] == 16
            and certificate["by_sector"]["HcHc"]["invariant_directions"] == 16
            and certificate["by_sector"]["HcH"]["invariant_directions"] == 40
        ),
        "all_nonzero_source_channel_copies_are_one": certificate[
            "all_nonzero_copy_multiplicities_one"
        ],
        "all_source_factors_normalized_and_covariant": all(
            row["normalized_gram_residual"] < 1.0e-12
            and row["raw_gram_isotropy_residual"] < 1.0e-12
            and row["covariance_seed_output_norm"] > 1.0e-12
            and row["all_45_generator_seed_covariance_residual"] < 1.0e-9
            and (
                row["bosonic_exchange_symmetry_residual"] is None
                or row["bosonic_exchange_symmetry_residual"] < 1.0e-12
            )
            for row in source_registry.values()
        ),
        "all_spin_factors_normalized": all(
            row["normalized_gram_residual"] < 1.0e-12
            for row in spin_registry.values()
        ),
        "all_direction_factor_ids_resolve": all(
            direction["spin_factor_tensor_id"] in spin_registry
            and direction["source_factor_tensor_id"] in source_registry
            for direction in all_directions
        ),
        "bosonic_symmetry_kill_detects_two_copy_overcount": (
            symmetry_kill["correct_total"] == 3
            and symmetry_kill["incorrect_total"] == 5
            and symmetry_kill["overcount_if_bosonic_quotient_is_dropped"] == 2
        ),
        "all_rows_remain_U1F_neutral": all(
            row["U1F_charge"] == 0 for row in certificate["rows"]
        ),
        "fail_closed_without_final_wilson_array": True,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError("V51 degree-four factor audit failed: " + ", ".join(failed))
    report: dict[str, Any] = {
        "schema": "susy-v51-degree4-cartesian-factor-audit-v1",
        "status": STATUS,
        "upstream": {
            "V51_cartesian_mediator_C5_C7": {
                "path": UPSTREAM_V51.name,
                "sha256": sha256_file(UPSTREAM_V51),
                "core_sha256": upstream["core_sha256"],
            },
            "V50_C7_incidence": {
                "path": UPSTREAM_V50.name,
                "sha256": sha256_file(UPSTREAM_V50),
            },
            "exact_D5_character_engine": {
                "path": Path(characters.__file__).name,
                "sha256": sha256_file(Path(characters.__file__)),
            },
        },
        "representation_theorem": {
            "spinor_product_decompositions": {
                "16x16": "10 + 120 + 126",
                "bar16xbar16": "10 + 120 + bar126",
                "16xbar16": "1 + 45 + 210",
                "bar16x16": "1 + 45 + 210",
            },
            "exact_decomposition_checks": exact_spinor_product_decompositions(),
            "multiplicity_formula": (
                "m_R = mult_1(source_pair_character tensor R), with Sym^2(Rs) "
                "for two copies of the same commuting nontrivial source field"
            ),
            "bosonic_symmetry_kill": symmetry_kill,
        },
        "degree_four_certificate": certificate,
        "normalized_factor_registry": {
            "source_factors": source_registry,
            "spin_factors": spin_registry,
            "composite_invariant_convention": (
                "For channel R of dimension d_R, pair the two Gram-orthonormal "
                "factor arrays with C=(1/sqrt(d_R))*sum_o T_spin[o] T_source[o]. "
                "The factor Gram identities imply ||C||_HS=1 exactly."
            ),
            "source_factor_count": len(source_registry),
            "spin_factor_count": len(spin_registry),
            "normalized_composite_direction_count": len(all_directions),
        },
        "C7_decision": {
            "closed": False,
            "degree_four_factor_copy_clause": "PASS_V51",
            "newly_closed_scope": (
                "all 120 V49 degree-four source-collar row multiplicities, all 72 "
                "nonzero normalized Cartesian factor/copy directions, and all 76 exact zeros"
            ),
            "remaining_open_scope": [
                "assemble and publish the final source-to-PS Wilson coefficient array",
                "bind every coefficient to a physical mediator/link field table and UV parameter",
                "complete strict C5 one-loop matching, subtraction, mixing and RG cancellation",
            ],
            "gates_promoted": [],
            "G2_closed": False,
        },
        "integrity_checks": checks,
        "n_failed_integrity_checks": 0,
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def build_report() -> dict[str, Any]:
    return copy.deepcopy(_build_report_cached())


def render_markdown(report: Mapping[str, Any]) -> str:
    certificate = report["degree_four_certificate"]
    sectors = certificate["by_sector"]
    return f"""# V51 degree-four Cartesian factor audit

Status: `{report['status']}`  
Core SHA-256: `{report['core_sha256']}`

## Result

All **{certificate['total_rows']}** degree-four V49 source-collar candidates are
resolved by exact D5 characters and explicit normalized Cartesian factors.
There are **{certificate['zero_rows']}** rigorous empty rows and
**{certificate['nonempty_rows']}** nonempty rows carrying
**{certificate['total_invariant_directions']}** invariant directions.  The
multiplicity histogram is `{certificate['multiplicity_histogram']}`.  Every
nonzero channel occurs with source-side copy multiplicity one.

The sector direction counts are HH={sectors['HH']['invariant_directions']},
HcHc={sectors['HcHc']['invariant_directions']}, and
HcH={sectors['HcH']['invariant_directions']}.

## Cartesian factor registry

Sixteen source-factor maps cover exactly the surviving intersections:

- singlet identity maps into `1`, `210`, `126`, and `bar126`;
- `Phi Phi -> 1,45,210`, including the symmetric Hodge-wedge 45;
- `Sigma barSigma -> 1,45,210`;
- `Phi Sigma -> 10,120,126` and its conjugate orientation.

Every raw array has a deterministic hash, scalar output Gram matrix, explicit
normalization, full output rank, and an all-45-generator covariance witness.
The spin factors use the locked Clifford/Yukawa tensors.  A normalized
quartic direction is `(1/sqrt(dim R)) sum_o T_spin[o] T_source[o]`.

The bosonic quotient is essential: treating `Phi Phi` as the ordered tensor
square would give five small-channel copies rather than the correct three.
The executable kill test therefore detects a two-direction overcount.

## Fail-closed boundary

This closes C7's degree-four factor/copy obligation, not C7 as a whole.  The
final source-to-PS Wilson array, the physical mediator/link field and parameter
table, and strict C5 one-loop matching remain absent.  No G2 gate is promoted.
"""


def validate(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("core hash mismatch")
    if report.get("n_failed_integrity_checks") != 0:
        raise RuntimeError("integrity failure count is nonzero")
    if not all(report.get("integrity_checks", {}).values()):
        raise RuntimeError("one or more integrity checks failed")
    certificate = report.get("degree_four_certificate", {})
    expected = {
        "total_rows": 120,
        "zero_rows": 76,
        "nonempty_rows": 44,
        "total_invariant_directions": 72,
    }
    for key, value in expected.items():
        if certificate.get(key) != value:
            raise RuntimeError(f"degree-four certificate drifted at {key}")
    if report.get("C7_decision", {}).get("closed") is not False:
        raise RuntimeError("C7 was overpromoted")


def write_artifacts(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def check_artifacts(report: Mapping[str, Any]) -> None:
    if not JSON_PATH.is_file() or not MD_PATH.is_file():
        raise RuntimeError("checked artifacts are missing")
    stored = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    if stored != report:
        raise RuntimeError("stored JSON differs from executable report")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("stored markdown differs from executable rendering")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate(report)
    if args.write:
        write_artifacts(report)
    if args.check:
        check_artifacts(report)
    print(
        json.dumps(
            {
                "status": report["status"],
                "core_sha256": report["core_sha256"],
                "degree_four_certificate": {
                    key: report["degree_four_certificate"][key]
                    for key in (
                        "total_rows", "zero_rows", "nonempty_rows",
                        "total_invariant_directions", "multiplicity_histogram",
                        "all_nonzero_copy_multiplicities_one",
                    )
                },
                "C7_closed": report["C7_decision"]["closed"],
                "n_failed_integrity_checks": report["n_failed_integrity_checks"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
