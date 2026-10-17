"""t4b: exact number of SO(10)-invariants in Sym^d(210), d = 0..6, by the Weyl-denominator method.
Plethysm via Newton's identity on characters:  h_n = (1/n) sum_{k=1}^{n} p_k h_{n-k},  p_k(x) = chi(x^k).
Also the invariant counts of Sym^d(486 chart) for d <= 4 under SO(10) x U(1)_X (X = 0 singlets).
"""
import itertools, json, os, sys, time
from collections import Counter
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__))
t0 = time.time()
RHO = (4, 3, 2, 1, 0)
WEYL = []
for perm in itertools.permutations(range(5)):
    psign = 1
    for i in range(5):
        for j in range(i + 1, 5):
            if perm[i] > perm[j]:
                psign = -psign
    for signs in itertools.product((1, -1), repeat=5):
        if signs.count(-1) % 2:
            continue
        WEYL.append((perm, signs, psign))


def act(w, v):
    perm, signs, _ = w
    return tuple(signs[i] * v[perm[i]] for i in range(5))


DELTA = Counter()
for w in WEYL:
    DELTA[act(w, RHO)] += w[2]


def mul(a, b):
    out = Counter()
    for ka, va in a.items():
        for kb, vb in b.items():
            out[tuple(x + y for x, y in zip(ka, kb))] += va * vb
    return out


def scale(a, c):
    return Counter({k: v * c for k, v in a.items()})


def add(a, b):
    out = Counter(a)
    for k, v in b.items():
        out[k] += v
    return out


def power_sub(ch, k):
    return Counter({tuple(k * x for x in key): v for key, v in ch.items()})


def char_210():
    vecs = []
    for i in range(5):
        e = [0] * 5; e[i] = 1; vecs.append(tuple(e))
        e = [0] * 5; e[i] = -1; vecs.append(tuple(e))
    ch = Counter()
    for comb in itertools.combinations(range(10), 4):
        ch[tuple(sum(vecs[k][j] for k in comb) for j in range(5))] += 1
    return ch


def sym_powers(ch, nmax):
    """h_0..h_nmax via Newton; exact integer characters (divide at the end)."""
    rank = len(next(iter(ch)))
    p = {k: power_sub(ch, k) for k in range(1, nmax + 1)}
    h = {0: Counter({tuple([0] * rank): 1})}
    for n in range(1, nmax + 1):
        acc = Counter()
        for k in range(1, n + 1):
            acc = add(acc, mul(p[k], h[n - k]))
        for key in list(acc):
            assert acc[key] % n == 0
            acc[key] //= n
            if acc[key] == 0:
                del acc[key]
        h[n] = acc
        print(f"  Sym^{n}: {len(acc)} distinct weights, dim {sum(acc.values())} [{time.time() - t0:.0f}s]", flush=True)
    return h


def invariant_count(ch, delta):
    """coefficient of e^{rho} in chi * Delta (= multiplicity of the trivial irrep)."""
    rho = tuple(RHO) + tuple([0] * (len(next(iter(ch))) - 5))
    tot = 0
    for k, v in ch.items():
        key = tuple(r - x for r, x in zip(rho, k))
        tot += v * delta.get(key[:5], 0) if len(key) == 5 else v * (delta.get(key[:5], 0) if all(x == 0 for x in key[5:]) else 0)
    return tot


out = {}
c210 = char_210()
h = sym_powers(c210, 6)
counts = {d: invariant_count(h[d], DELTA) for d in range(7)}
out["Sym_d_210_invariants"] = counts
out["dim_invariants_deg_le_6"] = sum(counts.values())
out["dim_invariants_deg_le_4"] = sum(counts[d] for d in range(5))
print("invariant counts Sym^d(210):", counts, "deg<=6 total", sum(counts.values()), flush=True)
out["elapsed_s"] = time.time() - t0
json.dump(out, open(os.path.join(HERE, "t4b_invariant_counts.json"), "w"), indent=1)
print("done", time.time() - t0)
