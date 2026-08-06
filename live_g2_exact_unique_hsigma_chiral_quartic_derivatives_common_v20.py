"""Shared exact multilinear jets for the two unique chiral H--Sigma quartics."""
from __future__ import annotations

from functools import lru_cache

import numpy as np

import exact_unique_hsigma_chiral_quartics_v20 as source
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart


@lru_cache(maxsize=1)
def _sigma_variations() -> tuple[tuple[np.ndarray, ...], tuple[np.ndarray, ...]]:
    """Dense canonical-real Sigma tangents and their conjugates.

    Each chart coordinate is linear, so these are the exact first slot
    variations; there are no same-slot second variations.
    """
    sigma: list[np.ndarray] = []
    sigma_dag: list[np.ndarray] = []
    scale = 1.0 / chart.SQRT2
    for form in chart.sigma_basis():
        dense = source.forms.dense_antisymmetric(form, 5)
        sigma.extend((scale * dense, 1j * scale * dense))
        dense_dag = np.conjugate(dense)
        sigma_dag.extend((scale * dense_dag, -1j * scale * dense_dag))
    return tuple(sigma), tuple(sigma_dag)


def _hdag_variations() -> tuple[np.ndarray, ...]:
    scale = 1.0 / chart.SQRT2
    output: list[np.ndarray] = []
    for index in range(chart.H_COMPLEX_DIM):
        real = np.zeros(chart.H_COMPLEX_DIM, dtype=complex)
        real[index] = scale
        imaginary = np.zeros(chart.H_COMPLEX_DIM, dtype=complex)
        imaginary[index] = -1j * scale
        output.extend((real, imaginary))
    return tuple(output)


H_DAG_VARIATIONS = _hdag_variations()


def _slot_variation(
    family: str, slot: int, active_index: int
) -> np.ndarray | None:
    if active_index < chart.H_REAL_DIM:
        return H_DAG_VARIATIONS[active_index] if (
            (family == "Hdag_Sigma2_Sigmadag" and slot == 0)
            or (family == "Hdag2_Sigma2" and slot in (0, 1))
        ) else None

    sigma, sigma_dag = _sigma_variations()
    sigma_index = active_index - chart.H_REAL_DIM
    if family == "Hdag_Sigma2_Sigmadag":
        if slot in (1, 2):
            return sigma[sigma_index]
        if slot == 3:
            return sigma_dag[sigma_index]
    elif family == "Hdag2_Sigma2" and slot in (2, 3):
        return sigma[sigma_index]
    return None


def _graph_spec(family: str) -> tuple[tuple[int, ...], tuple[int, ...]]:
    if family == "Hdag_Sigma2_Sigmadag":
        return source.FAMILY_A_DEGREES, source.FAMILY_A_SELECTED
    if family == "Hdag2_Sigma2":
        return source.FAMILY_B_DEGREES, source.FAMILY_B_SELECTED
    raise KeyError(f"unsupported unique chiral family {family}")


def _base_tensors(
    q: np.ndarray, family: str
) -> tuple[tuple[int, ...], tuple[int, ...], tuple[np.ndarray, ...]]:
    state = chart.unpack(q)
    dense = potential._dense_state(state)
    hdag = np.conjugate(state.h)
    degrees, selected = _graph_spec(family)
    if family == "Hdag_Sigma2_Sigmadag":
        tensors = (hdag, dense["sigma_dense"], dense["sigma_dense"], dense["sigma_dag_dense"])
    else:
        tensors = (hdag, hdag, dense["sigma_dense"], dense["sigma_dense"])
    return degrees, selected, tensors


def base_derivative(q: np.ndarray, family: str) -> tuple[complex, np.ndarray, np.ndarray]:
    coordinates = np.ascontiguousarray(
        np.asarray(q, dtype=float).reshape(chart.TOTAL_DIM)
    )
    return _base_derivative_cached(family, coordinates.tobytes())


@lru_cache(maxsize=4)
def _base_derivative_cached(
    family: str, coordinate_bytes: bytes
) -> tuple[complex, np.ndarray, np.ndarray]:
    """Differentiate the fixed four-slot graph exactly by the product rule."""
    coordinates = np.frombuffer(coordinate_bytes, dtype=float).reshape(chart.TOTAL_DIM)
    degrees, selected, tensors = _base_tensors(coordinates, family)
    active_dim = chart.H_REAL_DIM + chart.SIGMA_REAL_DIM
    active_start = chart.H_SLICE.start
    subscript = source.graph_subscript(degrees, selected)
    path = np.einsum_path(subscript, *tensors, optimize="greedy")[0]

    def evaluate(items: tuple[np.ndarray, ...]) -> complex:
        return complex(np.einsum(subscript, *items, optimize=path))

    value = evaluate(tensors)
    gradient = np.zeros(chart.TOTAL_DIM, dtype=complex)
    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=complex)
    variations = [
        [_slot_variation(family, slot, index) for slot in range(4)]
        for index in range(active_dim)
    ]

    for left in range(active_dim):
        derivative = 0.0j
        for slot, variation in enumerate(variations[left]):
            if variation is None:
                continue
            items = list(tensors)
            items[slot] = variation
            derivative += evaluate(tuple(items))
        gradient[active_start + left] = derivative

    for left in range(active_dim):
        for right in range(left, active_dim):
            derivative = 0.0j
            for first, first_variation in enumerate(variations[left]):
                if first_variation is None:
                    continue
                for second, second_variation in enumerate(variations[right]):
                    if second == first or second_variation is None:
                        continue
                    items = list(tensors)
                    items[first] = first_variation
                    items[second] = second_variation
                    derivative += evaluate(tuple(items))
            hessian[active_start + left, active_start + right] = derivative
            hessian[active_start + right, active_start + left] = derivative
    return value, gradient, hessian
