#!/usr/bin/env python3
"""Own SO(10) (= D5) Weyl-character engine, written from scratch for stage-2a "model" (v22-L2).

Everything is EXACT integer arithmetic:
  * a (reducible) representation is stored as its weight multiset: integer weights in the orthogonal basis e1..e5,
    scaled by 2 (so that spinor weights (+-1/2,...) are integers), with integer multiplicities;
  * fundamental weight systems are built from first principles: 10 = {+-e_i}; Lambda^k(10) by the Newton identity
    for elementary symmetric functions in the Adams operations; 126 / 126bar = the two halves of Lambda^5(10)
    (weights with all |c_i| = 1 split by the parity of the number of minus signs, the remaining weights split
    equally, an exact consequence of the outer automorphism that flips one coordinate); 16 / 16bar = spinor weights
    with even / odd number of minus signs;
  * symmetric powers Sym^n(V) by the Newton identity h_n = (1/n) sum_{i=1}^n psi^i(V) h_{n-i} (psi^i = Adams);
  * the multiplicity of the irrep V_lambda in a representation with weight multiplicity m is
        n_lambda = sum_{w in W(D5)} det(w) m(lambda + rho - w rho)                    (Weyl/Brauer-Klimyk)
    with W(D5) = signed permutations with an even number of sign changes (|W| = 1920), rho = (4,3,2,1,0);
  * dimensions by the Weyl dimension formula for D5.
Conventions: 126 has highest weight (1,1,1,1,1) and lies in 16 x 16 (16 has highest weight (1/2,...,1/2)); hence the
126bar_H of the model (F F Delta126bar Yukawa) has the odd-minus weights, exactly as in the repository/Susyno labels.
"""
from __future__ import annotations

import itertools
from fractions import Fraction
from functools import lru_cache

import numpy as np

RANK = 5
SCALE = 2                     # weights stored as 2 x (orthogonal coordinates)
RHO = np.array([4, 3, 2, 1, 0]) * SCALE
OFF = 64                      # key encoding offset (|2 c_i| <= 63 is enforced)
BASE = 128


# ----------------------------------------------------------------------------------------------------------------
# weight multisets
# ----------------------------------------------------------------------------------------------------------------
class Char:
    """weight multiset: W (n,5) int64 (scaled), M (n,) int64; always aggregated (unique weights, nonzero M)."""

    __slots__ = ("W", "M")

    def __init__(self, W, M, aggregate=True):
        W = np.asarray(W, dtype=np.int64).reshape(-1, RANK)
        M = np.asarray(M, dtype=object if False else np.int64).reshape(-1)
        if aggregate:
            W, M = _aggregate(W, M)
        self.W, self.M = W, M

    # algebra --------------------------------------------------------------------------------------------------
    def __add__(self, other):
        return Char(np.vstack([self.W, other.W]), np.concatenate([self.M, other.M]))

    def __sub__(self, other):
        return Char(np.vstack([self.W, other.W]), np.concatenate([self.M, -other.M]))

    def scale_mult(self, k):
        return Char(self.W, self.M * k, aggregate=False)

    def __mul__(self, other):
        if len(self.M) == 0 or len(other.M) == 0:
            return Char(np.zeros((0, RANK)), np.zeros(0))
        # chunk to keep memory bounded
        a, b = (self, other) if len(self.M) <= len(other.M) else (other, self)
        Ws, Ms = [], []
        chunk = max(1, 4_000_000 // max(1, len(b.M)))
        for s in range(0, len(a.M), chunk):
            aw = a.W[s:s + chunk]
            am = a.M[s:s + chunk]
            W = (aw[:, None, :] + b.W[None, :, :]).reshape(-1, RANK)
            M = (am[:, None] * b.M[None, :]).reshape(-1)
            W, M = _aggregate(W, M)
            Ws.append(W)
            Ms.append(M)
        return Char(np.vstack(Ws), np.concatenate(Ms))

    def adams(self, k):
        return Char(self.W * k, self.M, aggregate=False)

    def conj(self):
        return Char(-self.W, self.M)

    def dim(self):
        return int(self.M.sum())

    def mult_dict(self):
        return {tuple(int(x) for x in w): int(m) for w, m in zip(self.W, self.M)}


def _encode(W):
    if W.size and (np.abs(W).max() >= OFF):
        raise OverflowError("weight coordinate too large for the key encoding")
    k = np.zeros(len(W), dtype=np.int64)
    for i in range(RANK):
        k = k * BASE + (W[:, i] + OFF)
    return k


def _aggregate(W, M):
    if len(M) == 0:
        return W.reshape(0, RANK), M.reshape(0)
    k = _encode(W)
    uk, inv = np.unique(k, return_inverse=True)
    Mt = np.zeros(len(uk), dtype=np.int64)
    np.add.at(Mt, inv, M)
    # decode
    Wd = np.zeros((len(uk), RANK), dtype=np.int64)
    kk = uk.copy()
    for i in range(RANK - 1, -1, -1):
        Wd[:, i] = kk % BASE - OFF
        kk //= BASE
    nz = Mt != 0
    return Wd[nz], Mt[nz]


def trivial():
    return Char(np.zeros((1, RANK)), np.array([1]))


def zero_char():
    return Char(np.zeros((0, RANK)), np.zeros(0))


# ----------------------------------------------------------------------------------------------------------------
# fundamental representations
# ----------------------------------------------------------------------------------------------------------------
@lru_cache(maxsize=None)
def vector10():
    W = []
    for i in range(RANK):
        for s in (1, -1):
            w = [0] * RANK
            w[i] = s * SCALE
            W.append(w)
    return Char(W, [1] * 10)


def exterior_power(V, n):
    """Lambda^n(V) via e_n = (1/n) sum_{i=1}^n (-1)^(i-1) psi^i(V) e_{n-i}."""
    e = [trivial()]
    for k in range(1, n + 1):
        acc = zero_char()
        for i in range(1, k + 1):
            term = V.adams(i) * e[k - i]
            acc = acc + (term if (i - 1) % 2 == 0 else term.scale_mult(-1))
        assert np.all(acc.M % k == 0)
        e.append(Char(acc.W, acc.M // k))
    return e[n]


@lru_cache(maxsize=None)
def sym_power_cached(name, n):
    return sym_power(REPS[name](), n)


def sym_power(V, n):
    """Sym^n(V) via h_n = (1/n) sum_{i=1}^n psi^i(V) h_{n-i}."""
    h = [trivial()]
    for k in range(1, n + 1):
        acc = zero_char()
        for i in range(1, k + 1):
            acc = acc + V.adams(i) * h[k - i]
        assert np.all(acc.M % k == 0)
        h.append(Char(acc.W, acc.M // k))
    return h[n]


@lru_cache(maxsize=None)
def rep45():
    return exterior_power(vector10(), 2)


@lru_cache(maxsize=None)
def rep120():
    return exterior_power(vector10(), 3)


@lru_cache(maxsize=None)
def rep210():
    return exterior_power(vector10(), 4)


@lru_cache(maxsize=None)
def rep54():
    return sym_power(vector10(), 2) - trivial()


@lru_cache(maxsize=None)
def _lambda5_split():
    L5 = exterior_power(vector10(), 5)
    W126, M126, W126b, M126b = [], [], [], []
    for w, m in zip(L5.W, L5.M):
        if np.all(np.abs(w) == SCALE):
            nminus = int(np.sum(w < 0))
            assert m == 1
            if nminus % 2 == 0:
                W126.append(w); M126.append(1)
            else:
                W126b.append(w); M126b.append(1)
        else:
            assert m % 2 == 0
            W126.append(w); M126.append(m // 2)
            W126b.append(w); M126b.append(m // 2)
    return Char(W126, M126), Char(W126b, M126b)


def rep126():
    return _lambda5_split()[0]


def rep126bar():
    return _lambda5_split()[1]


@lru_cache(maxsize=None)
def _spinors():
    Wp, Wm = [], []
    for signs in itertools.product((1, -1), repeat=RANK):
        w = [s * SCALE // 2 for s in signs]
        (Wp if sum(1 for s in signs if s < 0) % 2 == 0 else Wm).append(w)
    return Char(Wp, [1] * 16), Char(Wm, [1] * 16)


def rep16():
    return _spinors()[0]


def rep16bar():
    return _spinors()[1]


REPS = {"1": trivial, "10": vector10, "45": rep45, "54": rep54, "120": rep120, "210": rep210, "126": rep126,
        "126bar": rep126bar, "16": rep16, "16bar": rep16bar}


# ----------------------------------------------------------------------------------------------------------------
# Weyl group of D5 and irrep multiplicities
# ----------------------------------------------------------------------------------------------------------------
@lru_cache(maxsize=None)
def weyl_shifts():
    """list of (rho - w rho, det w) for the 1920 elements of W(D5)."""
    out = []
    for perm in itertools.permutations(range(RANK)):
        # sign of permutation
        p = list(perm); sgn = 1
        for i in range(RANK):
            while p[i] != i:
                j = p[i]; p[i], p[j] = p[j], p[i]; sgn = -sgn
        for signs in itertools.product((1, -1), repeat=RANK):
            if sum(1 for s in signs if s < 0) % 2:
                continue
            wr = np.array([signs[i] * RHO[perm[i]] for i in range(RANK)])
            out.append((RHO - wr, sgn))   # det = sgn(perm) * prod(signs) = sgn(perm)
    assert len(out) == 1920
    return out


def irrep_multiplicity(ch: Char, lam) -> int:
    """n_lambda = sum_w det(w) m(lambda + rho - w rho); lam in SCALED orthogonal coordinates."""
    lam = np.asarray(lam, dtype=np.int64)
    md = _lookup(ch)
    tot = 0
    for shift, sgn in weyl_shifts():
        tot += sgn * md.get(tuple(int(x) for x in (lam + shift)), 0)
    return tot


def _lookup(ch):
    return ch.mult_dict()


def n_singlets(ch: Char) -> int:
    md = ch.mult_dict()
    tot = 0
    for shift, sgn in weyl_shifts():
        tot += sgn * md.get(tuple(int(x) for x in shift), 0)
    return tot


def weyl_dim(lam) -> int:
    """Weyl dimension formula for D5 (lam scaled orthogonal coordinates)."""
    l = (np.asarray(lam, dtype=object) + RHO.astype(object))
    r = RHO.astype(object)
    num = Fraction(1); den = Fraction(1)
    for i in range(RANK):
        for j in range(i + 1, RANK):
            num *= (l[i] - l[j]) * (l[i] + l[j])
            den *= (r[i] - r[j]) * (r[i] + r[j])
    v = num / den
    assert v.denominator == 1
    return int(v)


def is_dominant(w):
    return all(w[i] >= w[i + 1] for i in range(RANK - 2)) and w[RANK - 2] >= abs(w[RANK - 1])


def decompose(ch: Char):
    """full decomposition into irreps: list of (highest weight (unscaled, as Fractions-friendly tuple), dim, mult)."""
    md = ch.mult_dict()
    out = []
    for w in md:
        if is_dominant(w):
            lam = np.array(w)
            tot = 0
            for shift, sgn in weyl_shifts():
                tot += sgn * md.get(tuple(int(x) for x in (lam + shift)), 0)
            if tot:
                out.append((tuple(Fraction(int(x), SCALE) for x in w), weyl_dim(lam), tot))
    out.sort(key=lambda t: (t[1], t[0]))
    # consistency: dimensions add up
    assert sum(d * m for _, d, m in out) == ch.dim(), "decomposition does not exhaust the character"
    return out


def label(hw, dim):
    """human label for an irrep from its highest weight and dimension (distinguishes conjugate pairs)."""
    hw = tuple(hw)
    if hw[-1] < 0:
        return f"{dim}bar"
    named_conj = {(Fraction(1, 2),) * 5: "16"}
    return named_conj.get(hw, str(dim))


def pretty(dec):
    return " + ".join((f"{m}x" if m > 1 else "") + label(hw, d) for hw, d, m in dec)


if __name__ == "__main__":
    for nm in ("10", "45", "54", "120", "210", "126", "126bar", "16", "16bar"):
        c = REPS[nm]()
        print(nm, c.dim(), pretty(decompose(c)))
    print("10x10 =", pretty(decompose(vector10() * vector10())))
    print("16x16 =", pretty(decompose(rep16() * rep16())))
    print("16x16bar =", pretty(decompose(rep16() * rep16bar())))
    print("126x126bar =", pretty(decompose(rep126() * rep126bar())))
    print("Sym2(45) =", pretty(decompose(sym_power(rep45(), 2))))
    print("Sym2(210) =", pretty(decompose(sym_power(rep210(), 2))))
    print("Sym2(126bar) =", pretty(decompose(sym_power(rep126bar(), 2))))
    print("45x210 =", pretty(decompose(rep45() * rep210())))
    print("10x126bar =", pretty(decompose(vector10() * rep126bar())))
