"""Independent SO(10) = D5 singlet counter (verifier). No Susyno, no SARAH.

Method: Klimyk (Racah-Speiser) formula applied iteratively,
   V_lambda (x) V_mu = sum_{nu in wt(V_mu)} m_mu(nu) eps(w_nu) V_{w_nu(lambda+nu+rho) - rho},
with w_nu the Weyl element bringing lambda+nu+rho to the open dominant chamber (dropped when on a wall).
Orthogonal basis e_1..e_5, all weights scaled by 2 so that spinor weights are integers.
D5 dominant chamber: x1 >= x2 >= x3 >= x4 >= |x5|; walls x_i = +-x_j (i != j); Weyl group = signed
permutations with an even number of sign flips, eps(w) = sign(permutation).
Weight systems (scaled by 2):
  10   : +-2 e_i                                     (mult 1)
  16   : (+-1)^5 with an even number of minus signs  (mult 1);  16bar: odd number
  45   : +-2e_i +-2e_j (i<j), 0 (mult 5)
  54   : +-4 e_i, +-2e_i +-2e_j, 0 (mult 4)
  120  : Lambda^3: perms of (+-2,+-2,+-2,0,0) (mult 1), +-2e_i (mult 4)
  126  : self-dual Lambda^5: (+-2)^5 even minus (mult 1), perms of (+-2,+-2,+-2,0,0) (mult 1), +-2e_i (mult 3)
  126bar: same with odd minus signs
  210  : Lambda^4: perms of (+-2,+-2,+-2,+-2,0) (mult 1), perms of (+-2,+-2,0,0,0) (mult 3), 0 (mult 10)
Signed-dimension labels: 16bar = -16, 126bar = -126, 144 not needed.
"""
from __future__ import annotations

import itertools
import sys
from collections import defaultdict

RHO = (8, 6, 4, 2, 0)  # 2*rho = 2*(4,3,2,1,0)


def _perm_sign(seq):
    """Sign of the permutation that sorts seq (as the parity of inversions of the argsort)."""
    idx = sorted(range(len(seq)), key=lambda i: -seq[i])
    sign = 1
    visited = [False] * len(idx)
    for i in range(len(idx)):
        if visited[i]:
            continue
        j = i
        length = 0
        while not visited[j]:
            visited[j] = True
            j = idx[j]
            length += 1
        if length % 2 == 0:
            sign = -sign
    return sign


def weights_of(rep: int):
    out = defaultdict(int)
    n = 5
    if rep == 1:
        out[(0,) * n] += 1
    elif rep in (10, -10):
        for i in range(n):
            for s in (2, -2):
                v = [0] * n
                v[i] = s
                out[tuple(v)] += 1
    elif rep in (16, -16):
        want_even = rep == 16
        for signs in itertools.product((1, -1), repeat=n):
            neg = sum(1 for s in signs if s < 0)
            if (neg % 2 == 0) == want_even:
                out[tuple(signs)] += 1
    elif rep == 45:
        for i, j in itertools.combinations(range(n), 2):
            for si in (2, -2):
                for sj in (2, -2):
                    v = [0] * n
                    v[i], v[j] = si, sj
                    out[tuple(v)] += 1
        out[(0,) * n] += 5
    elif rep == 54:
        for i in range(n):
            for s in (4, -4):
                v = [0] * n
                v[i] = s
                out[tuple(v)] += 1
        for i, j in itertools.combinations(range(n), 2):
            for si in (2, -2):
                for sj in (2, -2):
                    v = [0] * n
                    v[i], v[j] = si, sj
                    out[tuple(v)] += 1
        out[(0,) * n] += 4
    elif rep == 120:
        for idx in itertools.combinations(range(n), 3):
            for signs in itertools.product((2, -2), repeat=3):
                v = [0] * n
                for k, s in zip(idx, signs):
                    v[k] = s
                out[tuple(v)] += 1
        for i in range(n):
            for s in (2, -2):
                v = [0] * n
                v[i] = s
                out[tuple(v)] += 4
    elif rep in (126, -126):
        want_even = rep == 126
        for signs in itertools.product((2, -2), repeat=n):
            neg = sum(1 for s in signs if s < 0)
            if (neg % 2 == 0) == want_even:
                out[tuple(signs)] += 1
        for idx in itertools.combinations(range(n), 3):
            for signs in itertools.product((2, -2), repeat=3):
                v = [0] * n
                for k, s in zip(idx, signs):
                    v[k] = s
                out[tuple(v)] += 1
        for i in range(n):
            for s in (2, -2):
                v = [0] * n
                v[i] = s
                out[tuple(v)] += 3
    elif rep == 210:
        for idx in itertools.combinations(range(n), 4):
            for signs in itertools.product((2, -2), repeat=4):
                v = [0] * n
                for k, s in zip(idx, signs):
                    v[k] = s
                out[tuple(v)] += 1
        for idx in itertools.combinations(range(n), 2):
            for signs in itertools.product((2, -2), repeat=2):
                v = [0] * n
                for k, s in zip(idx, signs):
                    v[k] = s
                out[tuple(v)] += 3
        out[(0,) * n] += 10
    else:
        raise ValueError(rep)
    assert sum(out.values()) == abs(rep), (rep, sum(out.values()))
    return dict(out)


HIGHEST = {1: (0, 0, 0, 0, 0), 10: (2, 0, 0, 0, 0), -10: (2, 0, 0, 0, 0), 16: (1, 1, 1, 1, 1), -16: (1, 1, 1, 1, -1),
           45: (2, 2, 0, 0, 0), 54: (4, 0, 0, 0, 0), 120: (2, 2, 2, 0, 0), 126: (2, 2, 2, 2, 2), -126: (2, 2, 2, 2, -2),
           210: (2, 2, 2, 2, 0)}


def to_dominant(x):
    """Return (sign, dominant image) of x under the D5 Weyl group, or (0, None) if x lies on a wall."""
    absx = [abs(v) for v in x]
    # wall test: |x_i| = |x_j| for i != j
    if len(set(absx)) < 5:
        return 0, None
    neg = sum(1 for v in x if v < 0)
    order = sorted(range(5), key=lambda i: -absx[i])
    y = [absx[i] for i in order]
    if neg % 2 == 1:
        y[4] = -y[4]  # leave one sign on the smallest entry (even number of flips applied)
    # sign of the permutation applied: sorting permutation sign
    sign = _perm_sign(absx)
    return sign, tuple(y)


def tensor_with(decomp: dict, rep: int) -> dict:
    """decomp: {dominant highest weight (scaled): multiplicity}; returns decomposition of decomp (x) V_rep."""
    wts = weights_of(rep)
    out = defaultdict(int)
    for lam, mult in decomp.items():
        for nu, mnu in wts.items():
            x = tuple(lam[i] + nu[i] + RHO[i] for i in range(5))
            sgn, dom = to_dominant(x)
            if sgn == 0:
                continue
            new = tuple(dom[i] - RHO[i] for i in range(5))
            out[new] += sgn * mult * mnu
    return {k: v for k, v in out.items() if v != 0}


def decompose(reps):
    """Full decomposition of the tensor product of the signed-dimension labels in reps."""
    reps = [r for r in reps if r != 1]
    if not reps:
        return {(0, 0, 0, 0, 0): 1}
    # start with the first rep as its highest weight, then multiply by the rest (small reps first for speed)
    reps = sorted(reps, key=lambda r: abs(r))
    decomp = {HIGHEST[reps[0]]: 1}
    for r in reps[1:]:
        decomp = tensor_with(decomp, r)
    return decomp


def singlets(reps) -> int:
    return decompose(reps).get((0, 0, 0, 0, 0), 0)


def weyl_dim(hw):
    """Weyl dimension formula for D5 with hw in the scaled orthogonal basis (lambda = hw/2)."""
    from fractions import Fraction as Fr
    lam = [Fr(h, 2) for h in hw]
    rho = [Fr(r, 2) for r in RHO]
    num = Fr(1)
    den = Fr(1)
    for i in range(5):
        for j in range(i + 1, 5):
            num *= (lam[i] + rho[i] - lam[j] - rho[j]) * (lam[i] + rho[i] + lam[j] + rho[j])
            den *= (rho[i] - rho[j]) * (rho[i] + rho[j])
    return num / den


def _selftest():
    # weight-system dimensions and highest weights via Weyl's formula
    for r, hw in HIGHEST.items():
        assert weyl_dim(hw) == abs(r), (r, weyl_dim(hw))
    # products with known decompositions
    d = decompose([10, 10])
    assert d == {(0, 0, 0, 0, 0): 1, (2, 2, 0, 0, 0): 1, (4, 0, 0, 0, 0): 1}, d
    d = decompose([16, 16])
    assert d == {(2, 0, 0, 0, 0): 1, (2, 2, 2, 0, 0): 1, (2, 2, 2, 2, 2): 1}, d
    d = decompose([16, -16])
    assert d == {(0, 0, 0, 0, 0): 1, (2, 2, 0, 0, 0): 1, (2, 2, 2, 2, 0): 1}, d
    d = decompose([-16, -16])
    assert d == {(2, 0, 0, 0, 0): 1, (2, 2, 2, 0, 0): 1, (2, 2, 2, 2, -2): 1}, d
    d = decompose([10, 16])
    assert sum(v * weyl_dim(k) for k, v in d.items()) == 160 and (1, 1, 1, 1, -1) in d, d  # 10 x 16 = 16bar + 144
    # dimension sums of a few products
    for reps in ([126, 10], [-126, 16, 16], [210, 10], [45, 45]):
        d = decompose(reps)
        tot = sum(v * weyl_dim(k) for k, v in d.items())
        prod = 1
        for r in reps:
            prod *= abs(r)
        assert tot == prod, (reps, tot, prod)
    # Susyno reference values (researcher's test set, computed with SARAH's Susyno) - cross-check
    ref = {(16, 16, -126): 1, (16, 16, 126): 0, (-16, -16, 10): 1, (10, 10): 1, (16, -16, 210): 1,
           (16, 16, 16, 16): 2, (16, 16, -126, 1): 1, (-126, -126): 0, (-126, -126, -126, -126): 3,
           (-126, -126, 210, 210): 6, (16, 16, -126, -126, 126): 10, (-16,) * 8: 175}
    for reps, want in ref.items():
        got = singlets(list(reps))
        print("  singlets%s = %d (Susyno: %d) %s" % (reps, got, want, "OK" if got == want else "MISMATCH"))
        assert got == want, (reps, got, want)
    print("selftest OK")


if __name__ == "__main__":
    _selftest()
    if len(sys.argv) > 2:
        inp, outp = sys.argv[1], sys.argv[2]
        lines = [ln for ln in open(inp, encoding="utf-8").read().splitlines() if ln.strip()]
        res = []
        for ln in lines:
            parts = ln.split()
            reps = [int(p) for p in parts[1:]]
            res.append("%s %d" % (parts[0], singlets(reps)))
        open(outp, "w", encoding="utf-8").write("\n".join(res) + "\n")
        print("wrote", outp, len(res))
