"""t4c: for every SO(10) irrep lambda occurring in degree<=3 polynomials of the 210, compute
  dim V_lambda^H  for H = G3221 = SU(3)_c x SU(2)_L x SU(2)_R x U(1)_{B-L}
(the stabiliser of Phi0 = p e6789 + a *J, with SU(3) acting on e1,e2,e3 of the complex structure on R^6
and SO(4) on R^4), by Freudenthal weight multiplicities + the H-Weyl-denominator readout.
Roots: SO(10) D5 in the orthogonal basis; H roots: SU(3): e_i - e_j (i,j<=3); SO(4): +-e4 +- e5; U(1): e1+e2+e3.
A weight is H-trivial iff it is fixed by ... we count the trivial H-irrep multiplicity via Delta_H readout:
  mult_0 = coefficient of e^{rho_H} in chi_lambda * Delta_H, with Delta_H = prod over H-positive roots.
Then vanishing-combination lower bound at a generic G3221 point: max(0, m_lambda(deg<=3) - dim V_lambda^H).
"""
import itertools, json, os, sys, time
from collections import Counter
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__))
t0 = time.time()
RHO = (4, 3, 2, 1, 0)
POS_ROOTS = []
for i in range(5):
    for j in range(i + 1, 5):
        r = [0] * 5; r[i] = 1; r[j] = -1; POS_ROOTS.append(tuple(r))
        r = [0] * 5; r[i] = 1; r[j] = 1; POS_ROOTS.append(tuple(r))
WEYL = []
for perm in itertools.permutations(range(5)):
    for signs in itertools.product((1, -1), repeat=5):
        if signs.count(-1) % 2 == 0:
            WEYL.append((perm, signs))


def wact(w, v):
    perm, signs = w
    return tuple(signs[i] * v[perm[i]] for i in range(5))


def dominant(v):
    a = sorted([abs(x) for x in v], reverse=True)
    neg = sum(1 for x in v if x < 0)
    if neg % 2 == 1:
        a[4] = -a[4]
    return tuple(a)


def ip(a, b):
    return sum(x * y for x, y in zip(a, b))


def leq(lam, mu):
    """mu <= lam in the D5 dominance order: lam - mu is a nonnegative integer combination of simple roots."""
    v = [a - b for a, b in zip(lam, mu)]
    s1 = v[0]; s2 = s1 + v[1]; s3 = s2 + v[2]
    if s1 < 0 or s2 < 0 or s3 < 0:
        return False
    t5 = s3 + v[3] + v[4]; t4 = s3 + v[3] - v[4]
    if t5 < 0 or t4 < 0 or t5 % 2 or t4 % 2:
        return False
    return True


def freudenthal(lam):
    """weight multiplicities (dominant weights) of the D5 irrep with highest weight lam (Freudenthal)."""
    lr = tuple(a + b for a, b in zip(lam, RHO))
    c_lam = ip(lr, lr)
    doms = {lam}
    frontier = [lam]
    while frontier:
        new = []
        for mu in frontier:
            for a in POS_ROOTS:
                d = dominant(tuple(m - x for m, x in zip(mu, a)))
                if d not in doms and leq(lam, d):
                    doms.add(d); new.append(d)
        frontier = new
    order = sorted(doms, key=lambda v: -ip(v, RHO))
    mult = {lam: 1}
    for mu in order:
        if mu == lam:
            continue
        mr = tuple(a + b for a, b in zip(mu, RHO))
        denom = c_lam - ip(mr, mr)
        assert denom > 0, (lam, mu)
        tot = 0
        for a in POS_ROOTS:
            k = 1
            while True:
                nu = tuple(m + k * x for m, x in zip(mu, a))
                d = dominant(nu)
                m_nu = mult.get(d, 0)
                if m_nu == 0:
                    break
                tot += ip(nu, a) * m_nu
                k += 1
        val = Fraction(2 * tot, denom)
        assert val.denominator == 1
        if val:
            mult[mu] = int(val)
    return mult


def full_character(lam):
    dm = freudenthal(lam)
    ch = Counter()
    for mu, m in dm.items():
        for w in WEYL:
            ch[wact(w, mu)] = m
    return ch


def weyl_dim(lam):
    num = Fraction(1); den = Fraction(1)
    lr = [a + b for a, b in zip(lam, RHO)]
    for i in range(5):
        for j in range(i + 1, 5):
            num *= (lr[i] - lr[j]) * (lr[i] + lr[j]); den *= (RHO[i] - RHO[j]) * (RHO[i] + RHO[j])
    return int(num / den)


# H = SU(3) x SU(2) x SU(2) x U(1): positive roots e1-e2, e1-e3, e2-e3, e4-e5, e4+e5 ; Weyl group S3 x (Z2)^2
H_POS = [(1, -1, 0, 0, 0), (1, 0, -1, 0, 0), (0, 1, -1, 0, 0), (0, 0, 0, 1, -1), (0, 0, 0, 1, 1)]
H_WEYL = []
for perm3 in itertools.permutations(range(3)):
    ps = 1
    for i in range(3):
        for j in range(i + 1, 3):
            if perm3[i] > perm3[j]:
                ps = -ps
    for s45 in ((1, 1), (-1, -1)):
        for swap in (False, True):
            H_WEYL.append((perm3, s45, swap, ps))
RHO_H = (1, 0, -1, 1, 0)   # half-sum of H positive roots


def hact(w, v):
    perm3, s45, swap, _ = w
    a = [v[perm3[0]], v[perm3[1]], v[perm3[2]]]
    b = [s45[0] * v[3], s45[1] * v[4]]
    if swap:
        b = [b[1], b[0]]
    return tuple(a + b)


def hsign(w):
    perm3, s45, swap, ps = w
    # sign for SO(4) part: swap (e4<->e5) is the reflection in e4-e5 (sign -1), (-,-) is reflection in e4+e5 composed...
    # D2 Weyl group = {1, s_{e4-e5}, s_{e4+e5}, s_{e4-e5}s_{e4+e5}}: s_{e4-e5}: swap (sign -1); s_{e4+e5}: swap+(-,-) (sign -1); both: (-,-) (sign +1)
    if swap and s45 == (1, 1):
        s4 = -1
    elif swap and s45 == (-1, -1):
        s4 = -1
    elif (not swap) and s45 == (-1, -1):
        s4 = 1
    else:
        s4 = 1
    return ps * s4


DELTA_H = Counter()
for w in H_WEYL:
    DELTA_H[hact(w, RHO_H)] += hsign(w)


def h_singlets(ch):
    tot = 0
    for mu, m in ch.items():
        key = tuple(r - x for r, x in zip(RHO_H, mu))
        tot += m * DELTA_H.get(key, 0)
    return tot


# sanity: 210 -> G3221 singlets = 2 (p and a); 45 -> 1 (B-L); 54 -> 1; 10 -> 0; 16 -> 0; 126 -> 0? (126 has (10bar,1,3)... no G3221 singlet with B-L=... )
tests = {"210": (1, 1, 1, 1, 0), "45": (1, 1, 0, 0, 0), "54": (2, 0, 0, 0, 0), "10": (1, 0, 0, 0, 0), "1": (0, 0, 0, 0, 0)}
for n, lam in tests.items():
    ch = full_character(lam)
    print("check", n, "dim", sum(ch.values()), "(Weyl", weyl_dim(lam), ") H-singlets", h_singlets(ch), flush=True)

deg3 = json.load(open(os.path.join(HERE, "t4_sym_multiplicities_210.json")))["deg_le_3"]["irreps"]
out = {}
for r in deg3:
    lam = tuple(r["hw"]); m = r["mult"]
    ch = full_character(lam)
    assert sum(ch.values()) == r["dim"], (lam, sum(ch.values()), r["dim"])
    hs = h_singlets(ch)
    out[str(lam)] = {"dim": r["dim"], "mult_deg_le_3": m, "dim_V_H": hs, "vanishing_lower_bound": max(0, m - hs)}
    print(lam, "dim", r["dim"], "mult(deg<=3)", m, "H-singlets", hs, "-> vanishing combos >=", max(0, m - hs), f"[{time.time() - t0:.0f}s]", flush=True)
json.dump(out, open(os.path.join(HERE, "t4c_h_singlets.json"), "w"), indent=1)
print("done", time.time() - t0)
