"""R2-V: independent SO(10) (D5) character machinery (own code; does not use the round-1 Klimyk counter).

Weights are stored in the orthogonal basis e_1..e_5 with DOUBLED integer coordinates (so the spinor weights
(+-1/2,...) become (+-1,...)).  Characters are Counters weight -> multiplicity.

Irrep characters are built without any multiplicity formula, from elementary constructions:
  10      = {+-e_i}
  16      = (+-1/2)^5 with an even number of minus signs;  16bar: odd number
  45      = Lambda^2(10),  120 = Lambda^3(10),  210 = Lambda^4(10)   (irreducible for SO(10))
  54      = Sym^2(10) - 1
  126     = Sym^2(16) - 10,   126bar = Sym^2(16bar) - 10
  144     = 16bar x 10 - 16   (wait: 16 x 10 = 16bar + 144 -> 144 = 16 x 10 - 16bar)
Multiplicity of the irrep V(lam) in a representation with weight multiplicities m:
  n_lam = sum_{w in W(D5)} sign(w) m(lam + rho - w rho)          (Weyl denominator identity)
W(D5) = permutations x even sign changes (1920 elements), sign(w) = sign of the permutation part.
"""
from __future__ import annotations

import itertools
from collections import Counter
from functools import lru_cache

RHO2 = (8, 6, 4, 2, 0)  # 2*rho for D5: rho = (4,3,2,1,0)


def _perm_sign(p):
    s = 1
    p = list(p)
    for i in range(len(p)):
        while p[i] != i:
            j = p[i]
            p[i], p[j] = p[j], p[i]
            s = -s
    return s


@lru_cache(maxsize=None)
def weyl_group():
    """list of (perm, signs, sign(w)); w(x)_i = signs[i] * x[perm[i]]."""
    out = []
    for perm in itertools.permutations(range(5)):
        ps = _perm_sign(perm)
        for signs in itertools.product((1, -1), repeat=5):
            if signs.count(-1) % 2:
                continue
            out.append((perm, signs, ps))
    assert len(out) == 1920
    return out


def w_act(w, x):
    perm, signs, _ = w
    return tuple(signs[i] * x[perm[i]] for i in range(5))


@lru_cache(maxsize=None)
def rho_shifts():
    """list of (rho - w rho (doubled), sign(w))."""
    out = []
    for w in weyl_group():
        wr = w_act(w, RHO2)
        out.append((tuple(RHO2[i] - wr[i] for i in range(5)), w[2]))
    return out


def multiplicity(char, lam2):
    """multiplicity of irrep with doubled highest weight lam2 in the character char."""
    tot = 0
    for shift, sg in rho_shifts():
        key = tuple(lam2[i] + shift[i] for i in range(5))
        tot += sg * char.get(key, 0)
    return tot


def n_singlets(char):
    return multiplicity(char, (0, 0, 0, 0, 0))


def product(*chars):
    out = Counter({(0, 0, 0, 0, 0): 1})
    for ch in chars:
        new = Counter()
        for a, ma in out.items():
            for b, mb in ch.items():
                new[tuple(a[i] + b[i] for i in range(5))] += ma * mb
        out = new
    return out


def conj(char):
    return Counter({tuple(-c for c in k): v for k, v in char.items()})


def _ten():
    c = Counter()
    for i in range(5):
        for s in (2, -2):
            v = [0] * 5
            v[i] = s
            c[tuple(v)] += 1
    return c


def _spinor(even=True):
    c = Counter()
    for signs in itertools.product((1, -1), repeat=5):
        if (signs.count(-1) % 2 == 0) == even:
            c[tuple(signs)] += 1
    return c


def _ext(char, k):
    ws = []
    for w, m in char.items():
        ws += [w] * m
    c = Counter()
    for comb in itertools.combinations(range(len(ws)), k):
        c[tuple(sum(ws[j][i] for j in comb) for i in range(5))] += 1
    return c


def _sym2(char):
    ws = []
    for w, m in char.items():
        ws += [w] * m
    c = Counter()
    for a in range(len(ws)):
        for b in range(a, len(ws)):
            c[tuple(ws[a][i] + ws[b][i] for i in range(5))] += 1
    return c


def _sub(a, b):
    c = Counter(a)
    for k, v in b.items():
        c[k] -= v
        if c[k] == 0:
            del c[k]
    assert all(v > 0 for v in c.values()), "negative multiplicity"
    return c


ONE = Counter({(0, 0, 0, 0, 0): 1})
TEN = _ten()
S16 = _spinor(True)
S16B = _spinor(False)
R45 = _ext(TEN, 2)
R120 = _ext(TEN, 3)
R210 = _ext(TEN, 4)
R54 = _sub(_sym2(TEN), ONE)
R126 = _sub(_sym2(S16), TEN)
R126B = _sub(_sym2(S16B), TEN)
R144 = _sub(product(S16, TEN), S16B)

# signed-rep code -> character  (convention of the task: 16bar = -16, 126bar = -126)
CHAR = {1: ONE, 10: TEN, -10: TEN, 16: S16, -16: S16B, 45: R45, 54: R54, 120: R120, 126: R126, -126: R126B,
        210: R210, 144: R144, -144: conj(R144)}
HW = {1: (0, 0, 0, 0, 0), 10: (2, 0, 0, 0, 0), 16: (1, 1, 1, 1, 1), -16: (1, 1, 1, 1, -1), 45: (2, 2, 0, 0, 0),
      54: (4, 0, 0, 0, 0), 120: (2, 2, 2, 0, 0), 126: (2, 2, 2, 2, 2), -126: (2, 2, 2, 2, -2), 210: (2, 2, 2, 2, 0),
      144: (3, 1, 1, 1, 1), -144: (3, 1, 1, 1, -1)}
DIMS = {k: sum(v.values()) for k, v in CHAR.items()}


def conj_code(r):
    return r if r in (1, 10, -10, 45, 54, 120, 210) else -r


def singlets_of(codes):
    return n_singlets(product(*[CHAR[c] for c in codes]))


def decompose(char, candidates=(1, 10, 16, -16, 45, 54, 120, 126, -126, 210, 144, -144)):
    out = {}
    rest = Counter(char)
    for c in candidates:
        n = multiplicity(char, HW[c])
        if n:
            out[c] = n
            for k, v in CHAR[c].items():
                rest[k] -= n * v
    rest = {k: v for k, v in rest.items() if v}
    return out, (len(rest) == 0)


def self_test():
    res = {}
    # dimensions
    res["dims"] = {k: DIMS[k] for k in (10, 16, -16, 45, 54, 120, 126, -126, 210, 144)}
    assert res["dims"] == {10: 10, 16: 16, -16: 16, 45: 45, 54: 54, 120: 120, 126: 126, -126: 126, 210: 210, 144: 144}
    # irreducibility check: each built character contains its own irrep exactly once and nothing else
    for c in (10, 16, -16, 45, 54, 120, 126, -126, 210, 144, -144):
        dec, ok = decompose(CHAR[c])
        assert dec == {c: 1} and ok, (c, dec)
    prods = {"16x16": (16, 16), "16x16bar": (16, -16), "10x10": (10, 10), "16x10": (16, 10), "16barx16bar": (-16, -16),
             "16barx10": (-16, 10)}
    for name, (a, b) in prods.items():
        dec, ok = decompose(product(CHAR[a], CHAR[b]))
        res[name] = {str(k): v for k, v in dec.items()}
        assert ok, name
    assert res["16x16"] == {"10": 1, "120": 1, "126": 1}
    assert res["16x16bar"] == {"1": 1, "45": 1, "210": 1}
    assert res["10x10"] == {"1": 1, "45": 1, "54": 1}
    assert res["16x10"] == {"-16": 1, "144": 1}
    assert res["16barx16bar"] == {"10": 1, "120": 1, "-126": 1}
    tests = {"16.16.126bar": (16, 16, -126), "16.16.126": (16, 16, 126), "16bar.16bar.10": (-16, -16, 10),
             "16.16bar.210": (16, -16, 210), "126bar^2": (-126, -126), "126.126bar": (126, -126),
             "210^3": (210, 210, 210), "210.126.126bar": (210, 126, -126), "210.10.126bar": (210, 10, -126),
             "210.10.126": (210, 10, 126), "10.10.210": (10, 10, 210), "126bar^4": (-126, -126, -126, -126)}
    res["singlet_tests"] = {k: singlets_of(v) for k, v in tests.items()}
    return res


if __name__ == "__main__":
    import json
    print(json.dumps(self_test(), indent=1))
