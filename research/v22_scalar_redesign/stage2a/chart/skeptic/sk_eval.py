"""My own tensor-level evaluator of index-string contractions (independent of chart531's polynomial compiler).

A contraction is a list of (type, index string); lower-case letters are summed between two tensors (einsum), upper-case
letters are contracted with eps_{a1..a10} in order of appearance, evaluated as the FULL sum over the 10! permutations
(sign(pi) * prod of tensor entries) - no sorted-block shortcut, so its normalisation is that of the literal formula.
"""
from __future__ import annotations

import itertools
import math

import numpy as np

_PERMS = None


def perms10():
    global _PERMS
    if _PERMS is None:
        flat = np.fromiter(itertools.chain.from_iterable(itertools.permutations(range(10))), dtype=np.int8,
                           count=math.factorial(10) * 10)
        P = flat.reshape(-1, 10)
        inv = np.zeros(P.shape[0], dtype=np.int64)
        for i in range(10):
            for j in range(i + 1, 10):
                inv += (P[:, i] > P[:, j])
        s = (1 - 2 * (inv % 2)).astype(np.float64)
        _PERMS = (P, s)
    return _PERMS


def tensor_of(t: dict, ty: str):
    if ty == "A":
        return t["A"]
    if ty == "P":
        return t["P"]
    if ty == "H":
        return t["H"]
    if ty == "Hb":
        return np.conj(t["H"])
    if ty == "D":
        return t["D"]
    if ty == "Db":
        return np.conj(t["D"])
    raise KeyError(ty)


def evaluate(t: dict, factors: list[tuple[str, str]]) -> complex:
    tens = [tensor_of(t, ty) for ty, _ in factors]
    idxs = [s for _, s in factors]
    upper = [ch for s in idxs for ch in s if ch.isupper()]
    if not upper:
        return complex(np.einsum(",".join(idxs) + "->", *tens, optimize="greedy"))
    assert len(upper) == 10 and len(set(upper)) == 10, "eps needs 10 distinct upper-case letters"
    order = {ch: k for k, ch in enumerate(upper)}
    # connected components through lower-case letters
    n = len(factors)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for i in range(n):
        for j in range(i + 1, n):
            if set(c for c in idxs[i] if c.islower()) & set(c for c in idxs[j] if c.islower()):
                parent[find(i)] = find(j)
    comps = {}
    for i in range(n):
        comps.setdefault(find(i), []).append(i)
    blocks = []
    for members in comps.values():
        ups = [ch for i in members for ch in idxs[i] if ch.isupper()]
        if len(members) == 1:
            T = tens[members[0]]
            s = idxs[members[0]]
            if any(c.islower() for c in s):
                raise ValueError("self-contraction not supported")
        else:
            T = np.einsum(",".join(idxs[i] for i in members) + "->" + "".join(ups), *[tens[i] for i in members],
                          optimize="greedy")
        blocks.append((T, [order[ch] for ch in ups]))
    P, sgn = perms10()
    val = sgn.astype(complex)
    for T, pos in blocks:
        val = val * T[tuple(P[:, p].astype(np.intp) for p in pos)]
    return complex(val.sum())


def evaluate_spec(t: dict, spec: dict) -> complex:
    """invariants.json machine_spec (prefactor, part and singlet factors applied)."""
    TY = {"A45": "A", "Phi210": "P", "H10": "H", "H10^dag": "Hb", "Delta126bar": "D", "Delta126bar^dag": "Db"}
    factors = [(TY[a], b) for a, b in zip(spec["tensors"], spec["indices"])]
    v = evaluate(t, factors)
    for s in spec.get("singlet_factors", []) or []:
        v *= {"S": t["S"], "Sb": np.conj(t["S"]), "T": t["T"], "Tb": np.conj(t["T"])}[s]
    pref = spec["prefactor"]
    v *= {"1": 1.0, "1/2": 0.5, "i": 1j}[pref]
    part = spec["part"]
    if part == "Re":
        v = complex(v.real)
    elif part == "Im":
        v = complex(v.imag)
    return v
