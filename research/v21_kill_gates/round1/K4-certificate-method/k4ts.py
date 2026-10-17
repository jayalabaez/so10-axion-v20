"""k4ts: the carrier 210 x Sym^2_0(10) = 8085 + 1050 + 1050bar + 945 + 210 for the 8085 block (the only degree-<=3
isotypic block of the 210 with vanishing combinations that lies neither in Sym^2(210) nor in Lambda^2(210)).

A covariant Z(Phi)[I, i, j] (210 x 10 x 10, symmetric traceless in ij) of degree d is the (Psi, v, v)-derivative of an
invariant F(Phi^d; Psi, v, v): loopless multigraphs with d Phi vertices (degree 4; or one Hodge-dual 6-form vertex
for the odd ones), one slot vertex (E4, degree 4) and two vector vertices of degree 1 (not joined to each other).
Pair operator on the carrier: C(Z) = sum_A T_A Z rho_A^T with rho_A = L_A (x) 1 + 1 (x) L_A on the ij pair.
"""
from __future__ import annotations
import itertools
import numpy as np
from scipy import sparse
import k4lib as K
import k4g as G

N = 10
DIM = 210
EYE = np.eye(N)
TS_LETTERS = "abcdefghklmnopqrstuvwxyz"   # no i, j (output indices)


def vertex_graphs(degrees, forbidden_pairs=()):
    pairs, graphs = G.regular_multigraphs(degrees)
    out = []
    for g in graphs:
        if any(g[pairs.index(p)] > 0 for p in forbidden_pairs):
            continue
        out.append(g)
    return pairs, out


def canonical(pairs, graphs, classes, n):
    pidx = {p: i for i, p in enumerate(pairs)}
    perms = []
    for combo in itertools.product(*[itertools.permutations(c) for c in classes]):
        sigma = list(range(n))
        for cls, img in zip(classes, combo):
            for a, b in zip(cls, img):
                sigma[a] = b
        perms.append(sigma)
    seen = {}
    for g in graphs:
        key = None
        for sigma in perms:
            m = [0] * len(pairs)
            for (u, v), k in zip(pairs, g):
                a, b = sorted((sigma[u], sigma[v]))
                m[pidx[(a, b)]] = k
            t = tuple(m)
            if key is None or t < key:
                key = t
        seen.setdefault(key, g)
    return list(seen.values())


class TSCovariant:
    """vtypes: 'P' (Phi), 'D' (*Phi), 'I' (slot), 'u', 'w' (vector vertices with output indices i, j)."""

    def __init__(self, name, pairs, mult, vtypes):
        self.name = name; self.pairs = pairs; self.mult = mult; self.vtypes = vtypes
        slots = {v: [] for v in range(len(vtypes))}
        li = 0
        for (u, v), k in zip(pairs, mult):
            for _ in range(k):
                slots[u].append(TS_LETTERS[li]); slots[v].append(TS_LETTERS[li]); li += 1
        subs = []
        for v, t in enumerate(vtypes):
            s = "".join(slots[v])
            if t == "I":
                s = "I" + s
            elif t == "u":
                s = "i" + s
            elif t == "w":
                s = "j" + s
            subs.append(s)
        self.subs = ",".join(subs) + "->Iij"
        self.degree = sum(1 for t in vtypes if t in ("P", "D"))
        self.plan = None

    def operands(self, T4, T6):
        ops = []
        for t in self.vtypes:
            ops.append({"P": T4, "D": T6, "I": G.E4, "u": EYE, "w": EYE}[t])
        return ops

    def evaluate(self, T4, T6=None):
        ops = self.operands(T4, T6)
        if self.plan is None:
            path, info = np.einsum_path(self.subs, *ops, optimize=("greedy", 3.0e7))
            fl = G.GraphCovariant._flops(info)
            if fl < 2.0e11:
                self.plan = ("direct", path)
            else:
                best = None
                terms = self.subs.split("->")[0].split(",")
                for L in sorted(set("".join(terms)) - set("Iij")):
                    sub_terms = [t.replace(L, "") for t in terms]
                    sub_ops = [np.take(o, 0, axis=t.index(L)) if L in t else o for t, o in zip(terms, ops)]
                    sp_, si = np.einsum_path(",".join(sub_terms) + "->Iij", *sub_ops, optimize=("greedy", 3.0e7))
                    f2 = G.GraphCovariant._flops(si) * N
                    if best is None or f2 < best[0]:
                        best = (f2, L, ",".join(sub_terms) + "->Iij", sp_)
                self.plan = ("sliced",) + best[1:]
        if self.plan[0] == "direct":
            Z = np.einsum(self.subs, *ops, optimize=self.plan[1])
        else:
            _, L, subs2, path2 = self.plan
            terms = self.subs.split("->")[0].split(",")
            Z = None
            for v in range(N):
                sub_ops = [np.take(o, v, axis=t.index(L)) if L in t else o for t, o in zip(terms, ops)]
                Y = np.einsum(subs2, *sub_ops, optimize=path2)
                Z = Y if Z is None else Z + Y
        return Z


def all_ts_covariants(max_degree=3):
    covs = []
    for d in range(1, max_degree + 1):
        for odd in (False, True):
            if odd and d < 1:
                continue
            vtypes = (["D"] + ["P"] * (d - 1)) if odd else ["P"] * d
            vtypes = vtypes + ["I", "u", "w"]
            degrees = ([6] + [4] * (d - 1)) if odd else [4] * d
            degrees = degrees + [4, 1, 1]
            n = len(vtypes)
            pairs, graphs = vertex_graphs(degrees, forbidden_pairs=[(n - 2, n - 1)])
            classes = ([[0], list(range(1, d))] if odd else [list(range(d))]) + [[n - 3], [n - 2, n - 1]]
            graphs = canonical(pairs, graphs, classes, n)
            for gi, g in enumerate(graphs):
                covs.append(TSCovariant(f"{'o' if odd else 'e'}ts{d}_{gi}", pairs, g, vtypes))
    return covs


def sym_traceless(Z):
    """symmetrise in (i,j) (times 2 to stay integral) and remove the trace (times 10 to stay integral)."""
    S = Z + np.transpose(Z, (0, 2, 1))
    tr = np.einsum("Iii->I", S)
    return 10 * S - np.einsum("I,ij->Iij", tr, EYE)


# ---- pair operator
def _L(a, b):
    m = np.zeros((N, N)); m[a, b] = 1.0; m[b, a] = -1.0
    return m


LVEC = [_L(a, b) for (a, b) in K.TWO]
RHO2 = [sparse.csr_matrix(np.kron(L, EYE) + np.kron(EYE, L)) for L in LVEC]      # 100 x 100
RHO2_T = [r.T.tocsr() for r in RHO2]
RHO2_INT = [sparse.csr_matrix((np.kron(L, EYE) + np.kron(EYE, L)).astype(np.int64)) for L in LVEC]
RHO2_INT_T = [r.T.tocsr() for r in RHO2_INT]
GENS_INT = [g for g in K.generators()]


def C_ts(Z):
    Z2 = Z.reshape(DIM, N * N)
    out = np.zeros_like(Z2)
    for g, gt, r, rt in zip(G.GENS, G.GENS_T, RHO2, RHO2_T):
        out += g @ (Z2 @ rt)
    return out.reshape(DIM, N, N)


def C_ts_mod(Z2, p):
    """Z2: int64 (210 x 100) reduced mod p; returns sum_A T_A Z2 rho_A^T mod p (int64, exact)."""
    out = np.zeros_like(Z2)
    for g, rt in zip(GENS_INT, RHO2_INT_T):
        out += (g @ (Z2 @ rt))
    return out % p


# channel eigenvalues of C_ts on the traceless carrier (verified numerically in g0ts): 8085, 1050+bar, 945, 210
TS_SO_EIG = {"8085": None, "1050t": None, "945t": None, "210t": None}
TS_CHANNELS = ("8085",)


def set_eigenvalues(vals):
    """vals: dict channel -> eigenvalue (filled from the numerical spectrum, then used exactly as integers)."""
    for k, v in vals.items():
        TS_SO_EIG[k] = v


def ts_projector(channel):
    from fractions import Fraction
    vals = [TS_SO_EIG[c] for c in TS_SO_EIG]
    assert all(v is not None for v in vals)
    return G._lagrange_poly(TS_SO_EIG[channel], vals), [Fraction(1)]
