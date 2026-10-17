"""t4: exact irrep multiplicities of Sym^d(210) for d=1,2,3 (and Sym^d of the full 486 chart under
SO(10) x U(1)_X), by the Weyl-denominator method:  chi * Delta = sum_lambda m_lambda sum_w eps(w) e^{w(lambda+rho)}.
D5: weights in the orthogonal basis (5 ints).  rho = (4,3,2,1,0).  Weyl group = signed permutations with
an even number of sign changes (order 1920).  Dominant: l1>=l2>=l3>=l4>=|l5|.
"""
import itertools, json, os, sys, time
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
t0 = time.time()
MODE = sys.argv[1] if len(sys.argv) > 1 else "210"

RHO = (4, 3, 2, 1, 0)
# Weyl group elements as (perm, signs) with even number of -1
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
assert len(WEYL) == 1920


def act(w, v):
    perm, signs, _ = w
    return tuple(signs[i] * v[perm[i]] for i in range(5))


def weyl_denominator():
    D = Counter()
    for w in WEYL:
        D[act(w, RHO)] += w[2]
    return D


DELTA = weyl_denominator()


def char_210():
    """weights of Lambda^4(10): sums of 4 distinct elements of {+-e_i}."""
    vecs = []
    for i in range(5):
        e = [0] * 5; e[i] = 1; vecs.append(tuple(e))
        e = [0] * 5; e[i] = -1; vecs.append(tuple(e))
    ch = Counter()
    for comb in itertools.combinations(range(10), 4):
        s = tuple(sum(vecs[k][j] for k in comb) for j in range(5))
        ch[s] += 1
    assert sum(ch.values()) == 210
    return ch


def char_10():
    ch = Counter()
    for i in range(5):
        e = [0] * 5; e[i] = 1; ch[tuple(e)] += 1
        e[i] = -1; ch[tuple(e)] += 1
    return ch


def char_126(bar=False):
    """self-dual 5-forms: (+-1)^5 weights with even (126) / odd (126bar) number of minus signs,
    plus (+-1,+-1,+-1,0,0)-type weights (mult 1) and (+-1,0,0,0,0) (mult 3)."""
    ch = Counter()
    for signs in itertools.product((1, -1), repeat=5):
        if (signs.count(-1) % 2 == 0) != bar:
            ch[signs] += 1
    for pos in itertools.combinations(range(5), 3):
        for signs in itertools.product((1, -1), repeat=3):
            v = [0] * 5
            for p, s in zip(pos, signs):
                v[p] = s
            ch[tuple(v)] += 1
    for i in range(5):
        for s in (1, -1):
            v = [0] * 5; v[i] = s; ch[tuple(v)] += 3
    assert sum(ch.values()) == 126
    return ch


def mul(a, b):
    out = Counter()
    for ka, va in a.items():
        for kb, vb in b.items():
            out[tuple(x + y for x, y in zip(ka, kb))] += va * vb
    return out


def power_sub(ch, k):
    """chi(x^k): weights scaled by k."""
    out = Counter()
    for key, v in ch.items():
        out[tuple(k * x for x in key)] += v
    return out


def sym2(ch):
    s = mul(ch, ch); s2 = power_sub(ch, 2)
    out = Counter()
    for k in set(s) | set(s2):
        val = (s.get(k, 0) + s2.get(k, 0))
        assert val % 2 == 0
        if val:
            out[k] = val // 2
    return out


def sym3(ch):
    s = mul(mul(ch, ch), ch); s12 = mul(ch, power_sub(ch, 2)); s3 = power_sub(ch, 3)
    out = Counter()
    for k in set(s) | set(s12) | set(s3):
        val = s.get(k, 0) + 3 * s12.get(k, 0) + 2 * s3.get(k, 0)
        assert val % 6 == 0
        if val:
            out[k] = val // 6
    return out


def decompose(ch):
    """return {lambda: multiplicity} by multiplying with Delta and reading strictly dominant coefficients."""
    prod = mul(ch, DELTA)
    mult = {}
    for key, v in prod.items():
        if v == 0:
            continue
        l1, l2, l3, l4, l5 = key
        if l1 > l2 > l3 > l4 > abs(l5):          # strictly dominant = lambda + rho
            lam = tuple(a - b for a, b in zip(key, RHO))
            mult[lam] = v
    return mult


def weyl_dim(lam):
    from fractions import Fraction
    # positive roots of D5: e_i - e_j, e_i + e_j (i<j)
    num = Fraction(1); den = Fraction(1)
    lr = [a + b for a, b in zip(lam, RHO)]
    for i in range(5):
        for j in range(i + 1, 5):
            num *= (lr[i] - lr[j]) * (lr[i] + lr[j])
            den *= (RHO[i] - RHO[j]) * (RHO[i] + RHO[j])
    return int(num / den)


def report(ch, label):
    dec = decompose(ch)
    total = sum(m * weyl_dim(l) for l, m in dec.items())
    rows = sorted(((weyl_dim(l), l, m) for l, m in dec.items()), key=lambda r: (-r[2], r[0]))
    out = {"label": label, "dim_check": total, "dim_expected": sum(ch.values()),
           "n_irreps": len(dec), "sum_mult": sum(dec.values()), "sum_mult_sq": sum(m * m for m in dec.values()),
           "max_mult": max(dec.values()), "irreps": [{"dim": d, "hw": list(l), "mult": m} for d, l, m in rows]}
    print(label, "dim", total, "/", sum(ch.values()), "n_irreps", len(dec), "sum m", sum(dec.values()),
          "sum m^2", sum(m * m for m in dec.values()), "max m", max(dec.values()), f"[{time.time() - t0:.0f}s]", flush=True)
    return out


results = {}
if MODE == "210":
    c210 = char_210()
    results["Sym1"] = report(c210, "Sym^1(210)")
    s2 = sym2(c210)
    results["Sym2"] = report(s2, "Sym^2(210)")
    s3 = sym3(c210)
    results["Sym3"] = report(s3, "Sym^3(210)")
    # degree <= 3 polynomials = Sym^3(210 + 1): add multiplicities
    tot = defaultdict(int)
    for key in ("Sym1", "Sym2", "Sym3"):
        for r in results[key]["irreps"]:
            tot[tuple(r["hw"])] += r["mult"]
    tot[(0, 0, 0, 0, 0)] += 1
    results["deg_le_3"] = {"n_irreps": len(tot), "sum_mult": sum(tot.values()), "sum_mult_sq": sum(m * m for m in tot.values()),
                           "max_mult": max(tot.values()), "irreps": [{"dim": weyl_dim(l), "hw": list(l), "mult": m} for l, m in sorted(tot.items(), key=lambda kv: -kv[1])]}
    print("deg<=3 in 210:", {k: v for k, v in results["deg_le_3"].items() if k != "irreps"}, flush=True)
    # Sym^4 is needed for degree-4 squares (Gram on degree <= 4); its multiplicities give those block sizes
    if len(sys.argv) > 2 and sys.argv[2] == "sym4":
        s4 = Counter()
        # plethysm Sym^4: (p1^4 + 6 p1^2 p2 + 3 p2^2 + 8 p1 p3 + 6 p4)/24
        p1 = c210; p2 = power_sub(c210, 2); p3 = power_sub(c210, 3); p4 = power_sub(c210, 4)
        terms = [(1, mul(mul(mul(p1, p1), p1), p1)), (6, mul(mul(p1, p1), p2)), (3, mul(p2, p2)), (8, mul(p1, p3)), (6, p4)]
        for coef, t in terms:
            for k, v in t.items():
                s4[k] += coef * v
        for k in list(s4):
            assert s4[k] % 24 == 0
            s4[k] //= 24
            if s4[k] == 0:
                del s4[k]
        results["Sym4"] = report(s4, "Sym^4(210)")
elif MODE == "486":
    # full chart: SO(10) x U(1)_X; weights carry a 6th entry = X charge
    def lift(ch, x):
        return Counter({k + (x,): v for k, v in ch.items()})
    c = Counter()
    for ch, x in ((char_210(), 0), (char_126(bar=True), -2), (char_126(bar=False), 2), (char_10(), -2), (char_10(), 2)):
        c.update(lift(ch, x))
    c[(0, 0, 0, 0, 0, 4)] += 1; c[(0, 0, 0, 0, 0, -4)] += 1
    c[(0, 0, 0, 0, 0, 17)] += 1; c[(0, 0, 0, 0, 0, -17)] += 1
    assert sum(c.values()) == 486
    DELTA6 = Counter({k + (0,): v for k, v in DELTA.items()})

    def decompose6(ch):
        prod = mul(ch, DELTA6)
        mult = {}
        for key, v in prod.items():
            if v == 0:
                continue
            l1, l2, l3, l4, l5, x = key
            if l1 > l2 > l3 > l4 > abs(l5):
                lam = tuple(a - b for a, b in zip(key[:5], RHO)) + (x,)
                mult[lam] = v
        return mult

    def report6(ch, label):
        dec = decompose6(ch)
        total = sum(m * weyl_dim(l[:5]) for l, m in dec.items())
        byx = defaultdict(lambda: [0, 0, 0])
        for l, m in dec.items():
            byx[l[5]][0] += 1; byx[l[5]][1] += m; byx[l[5]][2] += m * m
        out = {"label": label, "dim_check": total, "dim_expected": sum(ch.values()), "n_irreps": len(dec),
               "sum_mult": sum(dec.values()), "sum_mult_sq": sum(m * m for m in dec.values()), "max_mult": max(dec.values()),
               "by_X": {str(x): {"n_irreps": v[0], "sum_mult": v[1], "sum_mult_sq": v[2]} for x, v in sorted(byx.items())},
               "top": [{"dim": weyl_dim(l[:5]), "hw": list(l[:5]), "X": l[5], "mult": m} for l, m in sorted(dec.items(), key=lambda kv: -kv[1])[:40]]}
        print(label, "dim", total, "/", sum(ch.values()), "n_irreps", len(dec), "sum m", sum(dec.values()),
              "sum m^2", sum(m * m for m in dec.values()), "max m", max(dec.values()), f"[{time.time() - t0:.0f}s]", flush=True)
        return out
    results["Sym1"] = report6(c, "Sym^1(486)")
    s2 = sym2(c); results["Sym2"] = report6(s2, "Sym^2(486)")
    s3 = sym3(c); results["Sym3"] = report6(s3, "Sym^3(486)")
    tot = defaultdict(int)
    for key in ("Sym1", "Sym2", "Sym3"):
        pass
    # recompute full dict for deg<=3
    d1 = decompose6(c); d2 = decompose6(s2); d3 = decompose6(s3)
    for d in (d1, d2, d3):
        for l, m in d.items():
            tot[l] += m
    tot[(0, 0, 0, 0, 0, 0)] += 1
    results["deg_le_3"] = {"n_irreps": len(tot), "sum_mult": sum(tot.values()), "sum_mult_sq": sum(m * m for m in tot.values()), "max_mult": max(tot.values())}
    print("deg<=3 in 486:", results["deg_le_3"], flush=True)
results["elapsed_s"] = time.time() - t0
json.dump(results, open(os.path.join(HERE, f"t4_sym_multiplicities_{MODE}.json"), "w"), indent=1)
print("done", time.time() - t0)
