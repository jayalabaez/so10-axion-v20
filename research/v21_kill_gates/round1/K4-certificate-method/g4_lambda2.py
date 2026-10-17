"""g4: exact decomposition of Lambda^2(210) (the antisymmetric-matrix carrier) and the multiplicities of its
irreps in the degree-<=3 polynomials, to size the remaining blocks (945, 8085, 6930, ...) that are not in Sym^2(210).
Weyl-denominator method as in t4."""
import itertools, json, os, time
from collections import Counter
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


def char_210():
    vecs = []
    for i in range(5):
        e = [0] * 5; e[i] = 1; vecs.append(tuple(e))
        e = [0] * 5; e[i] = -1; vecs.append(tuple(e))
    ch = Counter()
    for comb in itertools.combinations(range(10), 4):
        ch[tuple(sum(vecs[k][j] for k in comb) for j in range(5))] += 1
    return ch


def mul(a, b):
    out = Counter()
    for ka, va in a.items():
        for kb, vb in b.items():
            out[tuple(x + y for x, y in zip(ka, kb))] += va * vb
    return out


def power_sub(ch, k):
    out = Counter()
    for key, v in ch.items():
        out[tuple(k * x for x in key)] += v
    return out


def decompose(ch):
    prod = mul(ch, DELTA)
    mult = {}
    for key, v in prod.items():
        if v == 0:
            continue
        l1, l2, l3, l4, l5 = key
        if l1 > l2 > l3 > l4 > abs(l5):
            mult[tuple(a - b for a, b in zip(key, RHO))] = v
    return mult


def weyl_dim(lam):
    from fractions import Fraction
    num = Fraction(1); den = Fraction(1)
    lr = [a + b for a, b in zip(lam, RHO)]
    for i in range(5):
        for j in range(i + 1, 5):
            num *= (lr[i] - lr[j]) * (lr[i] + lr[j]); den *= (RHO[i] - RHO[j]) * (RHO[i] + RHO[j])
    return int(num / den)


def C2(lam):
    return sum(l * (l + 2 * r) for l, r in zip(lam, RHO))


c = char_210()
sq = mul(c, c); p2 = power_sub(c, 2)
lam2 = Counter(); sym2 = Counter()
for k in set(sq) | set(p2):
    a = sq.get(k, 0); b = p2.get(k, 0)
    if (a - b):
        lam2[k] = (a - b) // 2
    if (a + b):
        sym2[k] = (a + b) // 2
dl = decompose(lam2); ds = decompose(sym2)
deg3 = json.load(open(os.path.join(HERE, "t4_sym_multiplicities_210.json")))["deg_le_3"]["irreps"]
m3 = {tuple(r["hw"]): r["mult"] for r in deg3}
hs = json.load(open(os.path.join(HERE, "t4c_h_singlets.json")))
out = {"Lambda2_dim": sum(m * weyl_dim(l) for l, m in dl.items()), "Sym2_dim": sum(m * weyl_dim(l) for l, m in ds.items()),
       "Lambda2": [], "Sym2": []}
for name, dec in (("Lambda2", dl), ("Sym2", ds)):
    for l, m in sorted(dec.items(), key=lambda kv: weyl_dim(kv[0])):
        key = str(l)
        out[name].append({"hw": list(l), "dim": weyl_dim(l), "mult_in_carrier": m, "C2": C2(l), "mult_deg_le_3": m3.get(l, 0),
                          "dim_V_H": hs.get(key, {}).get("dim_V_H")})
        print(name, l, "dim", weyl_dim(l), "mult", m, "C2", C2(l), "mult(deg<=3)", m3.get(l, 0), "dim V^H", hs.get(key, {}).get("dim_V_H"), flush=True)
# covariant counts: sum over irreps in carrier of (mult_in_carrier * mult_deg_le_3)
for name in ("Lambda2", "Sym2"):
    tot = sum(r["mult_in_carrier"] * r["mult_deg_le_3"] for r in out[name])
    out[name + "_total_covariants_deg_le_3"] = tot
    print(name, "total degree-<=3 covariants into the carrier:", tot, flush=True)
out["elapsed_s"] = time.time() - t0
json.dump(out, open(os.path.join(HERE, "g4_lambda2.json"), "w"), indent=1)
