"""SKEPTIC count of renormalizable SO(10) x U(1)_X invariants of the v22-L2 scalar set (method: Weyl INTEGRATION on a
discrete maximal-torus grid with the weights READ OFF THE CHART'S OWN Cartan generators).

Different from the model builder's three methods (Brauer-Klimyk alternation over W(D5) on first-principles weight
multisets; explicit contraction graphs; Susyno plethysms):
  1. weights: simultaneous diagonalisation of the five Cartan generators J01, J23, J45, J67, J89 acting on each block of
     the ACTUAL 531 chart (repo 486 blocks; A block derived by me from the repo H10 block action, see sk_common);
  2. characters of Sym^n(V) from power sums p_j(t) = chi_V(t^j) (Newton), evaluated pointwise on an N^5 torus grid via
     FFT of the weight-multiplicity array;
  3. dim Inv = (1/|W|) (1/N^5) sum_t chi(t) prod_{alpha in Phi} (1 - t^alpha)   (Weyl integration formula).
     Exact for Laurent polynomials whose exponents satisfy |m_i| < N: degree <= 4 gives |m_i| <= 4 + 8 = 12, so any
     N >= 13 is exact; I run N = 13, 16 and 17 and require identical integers.
"""
from __future__ import annotations

import itertools
import sys
import time
from collections import Counter, OrderedDict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sk_common as C  # noqa: E402

OUT = C.HERE / "sk_charcount.json"
LOG = None  # opened in main() only (importing this module must not truncate the log)


def block_K(G: np.ndarray, sl: slice, complex_block: bool) -> np.ndarray:
    g = np.asarray(G)[sl, sl]
    if not complex_block:
        return g.astype(complex)
    gxx, gyx = g[0::2, 0::2], g[1::2, 0::2]
    return gxx + 1j * gyx


def weights_of_block(cartans: list[np.ndarray], tol: float = 1e-9) -> tuple[np.ndarray, float, float]:
    """simultaneous eigen-decomposition of commuting anti-hermitian K_i; returns integer weights (n x 5)."""
    Hs = [-1j * K for K in cartans]     # hermitian
    for Hm in Hs:
        assert np.max(np.abs(Hm - Hm.conj().T)) < 1e-12, "Cartan generator not anti-hermitian in this block"
    c = np.array([1.0, np.sqrt(2.0), np.sqrt(3.0), np.sqrt(5.0), np.sqrt(7.0)]) * 0.37
    Cm = sum(ci * Hm for ci, Hm in zip(c, Hs))
    ev, V = np.linalg.eigh(Cm)
    W = np.stack([np.real(np.einsum("ij,ik,kj->j", V.conj(), Hm, V)) for Hm in Hs], axis=1)
    offdiag = max(float(np.max(np.abs(V.conj().T @ Hm @ V - np.diag(np.diag(V.conj().T @ Hm @ V))))) for Hm in Hs)
    Wi = np.rint(W)
    resid = float(np.max(np.abs(W - Wi)))
    assert resid < tol and offdiag < 1e-8, (resid, offdiag)
    return Wi.astype(int), resid, offdiag


def chart_weights() -> dict:
    G486 = C.repo_generators486()
    adj = C.my_adjoint_block()
    cart = [C.PIDX[(2 * i, 2 * i + 1)] for i in range(5)]
    out = {}
    info = {}
    for name, sl, cplx in (("P", C.SL["P"], False), ("H", C.SL["H"], True), ("D", C.SL["D"], True)):
        Ks = [block_K(G486[k], sl, cplx) for k in cart]
        w, r, o = weights_of_block(Ks)
        out[name] = w
        info[name] = {"dim": int(w.shape[0]), "rounding_residual": r, "offdiag": o}
    Ks = [adj[k].astype(complex) for k in cart]
    w, r, o = weights_of_block(Ks)
    out["A"] = w
    info["A"] = {"dim": int(w.shape[0]), "rounding_residual": r, "offdiag": o}
    # expected weight multisets from first principles (for the record)
    e = np.eye(5, dtype=int)
    vec = [s * e[i] for i in range(5) for s in (1, -1)]
    def wedge(k):
        return Counter(tuple(np.sum(c, axis=0)) for c in itertools.combinations(vec, k))
    exp = {"H": Counter(tuple(v) for v in vec), "A": wedge(2), "P": wedge(4)}
    l5 = wedge(5)
    for name in ("H", "A", "P"):
        got = Counter(tuple(int(x) for x in row) for row in out[name])
        info[name]["matches_first_principles"] = bool(got == exp[name])
    gotD = Counter(tuple(int(x) for x in row) for row in out["D"])
    gotDb = Counter(tuple(-int(x) for x in row) for row in out["D"])
    info["D"]["D_plus_Dbar_equals_Lambda5"] = bool(gotD + gotDb == l5)
    # which half: does D contain (1,1,1,1,1) (even # of minus signs) or (1,1,1,1,-1)?
    info["D"]["contains_(1,1,1,1,1)"] = bool(gotD.get((1, 1, 1, 1, 1), 0))
    info["D"]["contains_(1,1,1,1,-1)"] = bool(gotD.get((1, 1, 1, 1, -1), 0))
    return out, info


def roots_D5() -> list[np.ndarray]:
    R = []
    for i in range(5):
        for j in range(i + 1, 5):
            for si in (1, -1):
                for sj in (1, -1):
                    v = np.zeros(5, dtype=int)
                    v[i], v[j] = si, sj
                    R.append(v)
    return R


class Torus:
    def __init__(self, N: int, weights: dict):
        self.N = N
        self.chi = {}
        for name, W in weights.items():
            M = np.zeros((N,) * 5)
            for row in W:
                M[tuple(int(x) % N for x in row)] += 1.0
            self.chi[name] = np.fft.ifftn(M) * N ** 5          # sum_w exp(+2 pi i k.w / N)
        self.chi["Hb"] = np.conj(self.chi["H"])
        self.chi["Db"] = np.conj(self.chi["D"])
        k = np.indices((N,) * 5).reshape(5, -1).T
        dens = np.ones(N ** 5, dtype=complex)
        for a in roots_D5():
            dens *= 1.0 - np.exp(2j * np.pi * (k @ a) / N)
        self.dens = dens.reshape((N,) * 5)
        self._sym = {}

    def power(self, name: str, j: int) -> np.ndarray:
        r = (j * np.arange(self.N)) % self.N
        return self.chi[name][np.ix_(r, r, r, r, r)]

    def sym(self, name: str, n: int) -> np.ndarray:
        key = (name, n)
        if key in self._sym:
            return self._sym[key]
        if n == 0:
            out = np.ones((self.N,) * 5, dtype=complex)
        else:
            out = np.zeros((self.N,) * 5, dtype=complex)
            for i in range(1, n + 1):
                out += self.power(name, i) * self.sym(name, n - i)
            out /= n
        self._sym[key] = out
        return out

    def count(self, degs: dict) -> float:
        f = np.ones((self.N,) * 5, dtype=complex)
        for name, n in degs.items():
            if n and name in self.chi:
                f = f * self.sym(name, n)
        return complex(np.sum(f * self.dens)) / (1920.0 * self.N ** 5)


FIELDS = ["P", "A", "H", "Hb", "D", "Db", "S", "Sb", "T", "Tb"]
X = {"P": 0, "A": 0, "H": -2, "Hb": 2, "D": -2, "Db": 2, "S": 4, "Sb": -4, "T": 17, "Tb": -17}
CONJ = {"P": "P", "A": "A", "H": "Hb", "Hb": "H", "D": "Db", "Db": "D", "S": "Sb", "Sb": "S", "T": "Tb", "Tb": "T"}


def multidegrees(maxdeg: int = 4):
    out = []
    for d in range(1, maxdeg + 1):
        for combo in itertools.combinations_with_replacement(FIELDS, d):
            c = Counter(combo)
            if sum(X[f] * n for f, n in c.items()) == 0:
                out.append(tuple(sorted(c.items(), key=lambda kv: FIELDS.index(kv[0]))))
    return out


def conj_md(md):
    c = Counter()
    for f, n in md:
        c[CONJ[f]] += n
    return tuple(sorted(c.items(), key=lambda kv: FIELDS.index(kv[0])))


def label(md) -> str:
    return " ".join(f"{f}^{n}" if n > 1 else f for f, n in md)


def main() -> None:
    global LOG
    LOG = open(C.HERE / "sk_charcount.log", "w", encoding="utf-8")
    t0 = time.time()
    W, winfo = chart_weights()
    C.log(f"weights read off the chart: {winfo}", LOG)
    mds = multidegrees(4)
    C.log(f"X-allowed multidegrees of degree 1..4: {len(mds)}", LOG)
    counts_by_N = {}
    for N in (13, 16, 17):
        T = Torus(N, W)
        res = {}
        for md in mds:
            v = T.count(dict(md))
            iv = int(round(v.real))
            assert abs(v - iv) < 1e-7, (N, md, v)
            res[label(md)] = iv
        counts_by_N[N] = res
        C.log(f"N={N}: done ({time.time() - t0:.1f}s)", LOG)
    assert counts_by_N[13] == counts_by_N[16] == counts_by_N[17], "grid-size dependence -> aliasing"
    cnt = counts_by_N[16]
    # sanity table
    T = Torus(16, W)
    sanity = OrderedDict()
    for name, degs, expect in (
        ("Sym2(45)->1", {"A": 2}, 1), ("Sym4(45)->2", {"A": 4}, 2), ("Sym3(45)->0", {"A": 3}, 0),
        ("Sym2(210)->1", {"P": 2}, 1), ("Sym3(210)->1", {"P": 3}, 1), ("Sym4(210)->4", {"P": 4}, 4),
        ("10x10bar->1", {"H": 1, "Hb": 1}, 1), ("126x126bar->1", {"D": 1, "Db": 1}, 1),
        ("Sym2(126)->0", {"D": 2}, 0), ("Sym5(45)->? (Pf)", {"A": 5}, None),
    ):
        v = int(round(T.count(degs).real))
        sanity[name] = {"value": v, "expected": expect, "ok": (expect is None or v == expect)}
    C.log(f"sanity: {dict(sanity)}", LOG)

    # orbits, directions, real parameters
    seen = set()
    orbits = []
    for md in mds:
        if md in seen:
            continue
        cmd = conj_md(md)
        seen.add(md)
        seen.add(cmd)
        selfc = (cmd == md)
        d = cnt[label(md)]
        assert d == cnt[label(cmd)]
        hasA = any(f == "A" for f, _ in md)
        orbits.append({"rep": label(md), "conj": label(cmd), "self_conjugate": selfc, "n_invariants": d,
                       "real_parameters": d if selfc else 2 * d, "contains_A": hasA,
                       "multidegrees": 1 if selfc else 2})
    def tally(sel):
        nz = [o for o in orbits if sel(o) and o["n_invariants"] > 0]
        z = [o for o in orbits if sel(o) and o["n_invariants"] == 0]
        return {"multidegrees_nonzero": sum(o["multidegrees"] for o in nz), "orbits": len(nz),
                "directions": sum(o["n_invariants"] for o in nz),
                "real_parameters": sum(o["real_parameters"] for o in nz),
                "vanishing_multidegrees": sum(o["multidegrees"] for o in z),
                "vanishing_list": [o["rep"] + ("" if o["self_conjugate"] else " (+conj)") for o in z]}
    tv20 = tally(lambda o: not o["contains_A"])
    tA = tally(lambda o: o["contains_A"])
    tall = tally(lambda o: True)
    C.log(f"v20 part: {tv20}", LOG)
    C.log(f"A part:   {tA}", LOG)
    C.log(f"total:    {tall}", LOG)
    builder = {"v20": (34, 28, 44, 51), "A": (19, 17, 30, 34), "total": (53, 45, 74, 85), "A_vanishing": 15}
    agree = {
        "v20": (tv20["multidegrees_nonzero"], tv20["orbits"], tv20["directions"], tv20["real_parameters"]) == builder["v20"],
        "A": (tA["multidegrees_nonzero"], tA["orbits"], tA["directions"], tA["real_parameters"]) == builder["A"],
        "total": (tall["multidegrees_nonzero"], tall["orbits"], tall["directions"], tall["real_parameters"]) == builder["total"],
        "A_vanishing": tA["vanishing_multidegrees"] == builder["A_vanishing"],
    }
    C.log(f"agreement with builder counts: {agree}", LOG)
    A_orbits = [o for o in orbits if o["contains_A"] and o["n_invariants"] > 0]
    for o in A_orbits:
        C.log(f"  A-orbit {o['rep']:<22s} n={o['n_invariants']}  real={o['real_parameters']}  self-conj={o['self_conjugate']}", LOG)
    C.json_dump({"method": __doc__, "weights_info": winfo, "grid_sizes": [13, 16, 17],
                 "grid_independent": True, "sanity": sanity, "counts": cnt, "orbits": orbits,
                 "tally_v20": tv20, "tally_A": tA, "tally_total": tall, "builder": builder,
                 "agreement": agree, "runtime_s": time.time() - t0}, OUT)
    C.log(f"wrote {OUT} ({time.time() - t0:.1f}s)", LOG)


if __name__ == "__main__":
    main()
