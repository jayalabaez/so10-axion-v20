"""Gate K0b engine: exact analysis of an SO(10) x U(1)_X fermion content of the F17 type
(scalar sector fixed: Phi210(0), Delta126bar(-2), H10(-2), S(4), Phi17(17)).

Pieces (all exact integer/Fraction arithmetic unless stated):
  * anomalies                 [SO(10)]^2 X, grav-X, X^3; sector indices
  * renormalizable terms      every SO(10)-singlet X-neutral fermion bilinear x (nothing | scalar | conj scalar)
                              (SO(10) invariance by an independent Klimyk/Racah-Speiser singlet counter)
  * kernel                    accidental global U(1)s of the complete renormalizable Lagrangian (fermion terms +
                              the 4 phase-sensitive scalar terms of the fixed potential): X, G2 (Phi17 number
                              extended to fermions) and the fermion-only generators f_k
  * PQ data                   N, E, E/N, N_DW modulo gauge (PQ = X - 17 G2)
  * dual LP bound             a rigorous lower bound on the Planck power K of ANY PQ-violating vacuum diagram
                              closed by renormalizable vertices (cutting planes; separation oracle = ILP over all
                              X-neutral, centre-consistent, Lorentz-consistent monomials with 5 <= dim <= 20)
  * explicit closure ILP      K0's integer program (verified operators dim <= D, <= 4 fermions) for the cheapest
                              explicit closure + K0's NDA estimate of dtheta
  * decay operators / R-parity / stable states
"""
from __future__ import annotations

import itertools
import json
import math
from fractions import Fraction as Fr
from functools import lru_cache

import numpy as np
import sympy
from scipy.optimize import Bounds, LinearConstraint, linprog, milp

import so10_singlets_klimyk as klimyk

MPL = 2.435e18
CHI = 0.0755 ** 4
SCALARS = [("Phi210", 210, 0, True), ("Delta", -126, -2, False), ("H10", 10, -2, False), ("S", 1, 4, False),
           ("Phi17", 1, 17, False)]
SCALAR_NAMES = [s[0] for s in SCALARS]
SELF_CONJ = {1, 10, 45, 54, 120, 210}
T_SO10 = {1: Fr(0), 10: Fr(1), 16: Fr(2), 126: Fr(35), 210: Fr(56)}
DIM = {1: 1, 10: 10, 16: 16, 126: 126, 210: 210}
Z_CENTRE = {16: 1, -16: 3, 10: 2, -10: 2, 126: 2, -126: 2, 1: 0, 210: 0, 45: 0, 54: 0, 120: 0}
# SM content for QCD / EM anomalies (per Weyl multiplet)
T_SU3 = {16: Fr(2), 10: Fr(1), 1: Fr(0)}
TRQ2 = {16: Fr(16, 3), 10: Fr(8, 3), 1: Fr(0)}  # Tr Q^2 over the multiplet: 16 -> 16/3, 10 -> 8/3


def conj_rep(r):
    return r if abs(r) in SELF_CONJ else -r


@lru_cache(maxsize=None)
def n_singlets(reps):
    return klimyk.singlets(list(reps))


# ----------------------------------------------------------------------------------------------------------
class Model:
    """fermions: list of (name, signed rep, X, gens)."""

    def __init__(self, fermions, label=""):
        self.label = label
        self.fermions = [tuple(f) for f in fermions]
        self.fnames = [f[0] for f in self.fermions]
        self.frep = {f[0]: f[1] for f in self.fermions}
        self.fX = {f[0]: f[2] for f in self.fermions}
        self.fgen = {f[0]: f[3] for f in self.fermions}
        self.terms = None
        self.kernel = None

    # ---- anomalies -----------------------------------------------------------------------------------
    def anomalies(self):
        a_so10 = sum(Fr(g) * T_SO10[abs(r)] * x for _n, r, x, g in self.fermions)
        a_grav = sum(Fr(g) * DIM[abs(r)] * x for _n, r, x, g in self.fermions)
        a_x3 = sum(Fr(g) * DIM[abs(r)] * x ** 3 for _n, r, x, g in self.fermions)
        bx = sum(Fr(2, 3) * g * DIM[abs(r)] * x * x for _n, r, x, g in self.fermions)
        bx += sum(Fr(1, 3) * DIM[abs(r)] * x * x for _n, r, x, real in SCALARS if not real)
        return {"SO10^2_X": a_so10, "grav_X": a_grav, "X^3": a_x3, "b_X": bx,
                "all_zero": a_so10 == 0 and a_grav == 0 and a_x3 == 0}

    # ---- renormalizable terms --------------------------------------------------------------------------
    def scalar_insertions(self):
        out = [("mass", 1, 0)]
        for name, rep, x, real in SCALARS:
            out.append((name, rep, x))
            if not real:
                out.append(("conj[%s]" % name, conj_rep(rep), -x))
        return out

    def renormalizable_terms(self):
        if self.terms is not None:
            return self.terms
        terms = []
        for (fa, ra, xa, ga), (fb, rb, xb, gb) in itertools.combinations_with_replacement(self.fermions, 2):
            for sname, srep, sx in self.scalar_insertions():
                if xa + xb + sx != 0:
                    continue
                reps = tuple(sorted([ra, rb] + ([srep] if sname != "mass" else [])))
                if n_singlets(reps) <= 0:
                    continue
                terms.append({"fermions": [fa, fb], "scalar": sname, "scalar_rep": srep if sname != "mass" else 1,
                              "gens": "%dx%d" % (ga, gb)})
        self.terms = terms
        return terms

    def bare_masses(self):
        return [t for t in self.renormalizable_terms() if t["scalar"] == "mass"]

    def phi210_yukawas(self):
        return [t for t in self.renormalizable_terms() if t["scalar"] == "Phi210"]

    def family_exotic_yukawas(self):
        return [t for t in self.renormalizable_terms()
                if ("F" in t["fermions"]) and any(f != "F" for f in t["fermions"]) and t["scalar"] != "mass"]

    # ---- kernel ------------------------------------------------------------------------------------------
    def compute_kernel(self):
        if self.kernel is not None:
            return self.kernel
        terms = self.renormalizable_terms()
        snames = ["H10", "Delta", "S", "Phi17"]
        names = self.fnames + snames
        idx = {n: i for i, n in enumerate(names)}
        rows = []
        labels = []
        for t in terms:
            row = [0] * len(names)
            for f in t["fermions"]:
                row[idx[f]] += 1
            s = t["scalar"]
            if s not in ("mass", "Phi210"):
                if s.startswith("conj["):
                    row[idx[s[5:-1]]] -= 1
                else:
                    row[idx[s]] += 1
            rows.append(row)
            labels.append(".".join(t["fermions"]) + "." + s)
        h, d, s_, p = idx["H10"], idx["Delta"], idx["S"], idx["Phi17"]
        for lab, coeffs in (("kappa H10.H10.S", {h: 2, s_: 1}), ("Phi210.conj[H10].Delta", {h: -1, d: 1}),
                            ("O38 Phi210.conj[H10].conj[Delta].conj[S]", {h: -1, d: -1, s_: -1}),
                            ("Delta^2.conj[H10]^2", {d: 2, h: -2})):
            row = [0] * len(names)
            for k, v in coeffs.items():
                row[k] = v
            rows.append(row)
            labels.append(lab)
        A = sympy.Matrix(rows)
        null = A.nullspace()
        kdim = len(null)
        nf = len(self.fnames)
        # scalar projection rank
        P = sympy.Matrix.hstack(*[v[nf:, :] for v in null]) if null else sympy.zeros(4, 0)
        scalar_rank = P.rank()
        # G2-extended vector: kernel vector with scalar part (0,0,0,1)
        g2vec = None
        if null:
            K = sympy.Matrix.hstack(*null)
            # solve K c = target on scalar rows
            target = sympy.Matrix([0, 0, 0, 1])
            sol = sympy.linsolve((K[nf:, :], target))
            if sol != sympy.S.EmptySet:
                c = list(sol)[0]
                free = list(c.free_symbols)
                c = sympy.Matrix(c).subs({f: 0 for f in free})
                g2vec = K * c
        # fermion-only generators: kernel vectors with zero scalar part
        fonly = []
        if null:
            K = sympy.Matrix.hstack(*null)
            Ns = (K[nf:, :]).nullspace()
            for c in Ns:
                v = K * c
                den = sympy.ilcm(*[sympy.fraction(sympy.nsimplify(e))[1] for e in v]) if any(e != 0 for e in v) else 1
                v = v * den
                g = sympy.igcd(*[int(e) for e in v if e != 0]) if any(e != 0 for e in v) else 1
                fonly.append(v / g)
            # make the fermion-only basis as "sparse" as possible: Hermite normal form via sympy
            if fonly:
                M = sympy.Matrix.hstack(*fonly).T
                M = M.rref()[0]
                fonly = []
                for i in range(M.rows):
                    v = M.row(i).T
                    if all(e == 0 for e in v):
                        continue
                    den = sympy.ilcm(*[sympy.fraction(e)[1] for e in v])
                    v = v * den
                    g = sympy.igcd(*[int(e) for e in v if e != 0])
                    fonly.append(v / g)
        xvec = sympy.Matrix([self.fX[n] for n in self.fnames] + [-2, -2, 4, 17])
        in_kernel_x = (A * xvec).is_zero_matrix
        self.kernel = {"names": names, "nf": nf, "rank": A.rank(), "dim": kdim, "scalar_rank": scalar_rank,
                       "X_in_kernel": bool(in_kernel_x), "G2": g2vec, "fonly": fonly, "labels": labels,
                       "n_fermion_only": len(fonly)}
        # check completeness: X, G2, fonly span the kernel
        basis = [xvec] + ([g2vec] if g2vec is not None else []) + fonly
        B = sympy.Matrix.hstack(*basis)
        self.kernel["span_ok"] = (B.rank() == kdim) and (len(basis) == kdim)
        return self.kernel

    # ---- PQ data -----------------------------------------------------------------------------------------
    def pq_data(self):
        k = self.compute_kernel()
        if k["G2"] is None:
            return {"PQ_exists": False}
        names = k["names"]
        g2 = {n: k["G2"][i] for i, n in enumerate(names)}
        pq = {n: self.fX.get(n, {"H10": -2, "Delta": -2, "S": 4, "Phi17": 17}.get(n)) - 17 * g2[n] for n in names}
        n_pq = sum(self.fgen[n] * T_SU3[abs(self.frep[n])] * Fr(pq[n]) for n in self.fnames)
        e_pq = sum(self.fgen[n] * TRQ2[abs(self.frep[n])] * Fr(pq[n]) for n in self.fnames)
        fonly_n = [sum(self.fgen[n] * T_SU3[abs(self.frep[n])] * Fr(v[i]) for i, n in enumerate(self.fnames)) for v in k["fonly"]]
        # N_DW modulo gauge: minimal PQ angle that is a lattice shift modulo U(1)_X: 2 pi gcd(17,4)/68 = 2 pi/68
        ndw = Fr(abs(2 * n_pq), 68)
        return {"PQ_exists": True, "G2_charges": {n: int(g2[n]) for n in names}, "PQ_charges": {n: int(pq[n]) for n in names},
                "N": n_pq, "E": e_pq, "E_over_N": (e_pq / n_pq) if n_pq else None, "N_DW_mod_gauge": ndw,
                "fermion_only_N_QCD": fonly_n}

    # ---- field table for integer programs ------------------------------------------------------------------
    def field_table(self):
        """list of dicts: label, X, z, charges (G2, f_1..f_n), dim2 (2*dim), fermion, barred, base."""
        k = self.compute_kernel()
        names = k["names"]
        gens = [k["G2"]] + k["fonly"]
        out = []
        base_fields = [(n, self.frep[n], self.fX[n], True) for n in self.fnames]
        base_fields += [(n, r, x, False) for n, r, x, real in SCALARS]
        for n, r, x, ferm in base_fields:
            i = names.index(n) if n in names else None
            q = [int(g[i]) if i is not None else 0 for g in gens]
            z = Z_CENTRE[r]
            dim2 = 3 if ferm else 2
            out.append({"label": n, "base": n, "rep": r, "X": x, "z": z % 4, "q": q, "dim2": dim2, "fermion": ferm, "barred": False})
            real = (not ferm) and n == "Phi210"
            if not real:
                out.append({"label": n + "^", "base": n, "rep": conj_rep(r), "X": -x, "z": (-z) % 4, "q": [-c for c in q],
                            "dim2": dim2, "fermion": ferm, "barred": True})
        return out

    # ---- separation oracle: min_{monomials} [cost - mu.q] over 5 <= dim <= dim_max --------------------------
    def oracle(self, mu, dim_max=20, fields=None, forbid=(), require_fermion=False):
        fields = fields or self.field_table()
        fields = [f for f in fields if f["label"] not in forbid]
        n = len(fields)
        best = None
        for parity in (0, 1):
            w = np.array([f["dim2"] / 2.0 - sum(m * c for m, c in zip(mu, f["q"])) for f in fields])
            c = np.concatenate([w, np.zeros(3)])
            rows, lbs, ubs = [], [], []

            def add(cf, aux, lb, ub):
                rows.append(np.concatenate([np.array(cf, dtype=float), np.array(aux, dtype=float)]))
                lbs.append(lb)
                ubs.append(ub)
            add([f["X"] for f in fields], [0, 0, 0], 0, 0)
            add([f["z"] for f in fields], [-4, 0, 0], 0, 0)
            add([1 if (f["fermion"] and not f["barred"]) else 0 for f in fields], [0, -2, 0], parity, parity)
            add([1 if (f["fermion"] and f["barred"]) else 0 for f in fields], [0, 0, -2], parity, parity)
            add([f["dim2"] for f in fields], [0, 0, 0], 10 - 2 * parity, 2 * dim_max - 2 * parity)
            if require_fermion:
                add([1 if f["fermion"] else 0 for f in fields], [0, 0, 0], 1, 100)
            A = np.vstack(rows)
            lb = np.zeros(n + 3)
            ub = np.full(n + 3, float(dim_max))
            lb[n:] = -100
            ub[n:] = 100
            res = milp(c, constraints=LinearConstraint(A, lbs, ubs), integrality=np.ones(n + 3),
                       bounds=Bounds(lb, ub), options={"mip_rel_gap": 0.0})
            if res.success:
                counts = {fields[i]["label"]: int(round(res.x[i])) for i in range(n) if round(res.x[i]) > 0}
                val = float(res.fun) + parity - 4.0  # cost - mu.q  (cost = dim - 4)
                if best is None or val < best["value"]:
                    best = {"value": val, "counts": counts, "parity": parity}
        return best

    def charges_of(self, counts, fields=None):
        fields = fields or self.field_table()
        tab = {f["label"]: f for f in fields}
        nq = len(fields[0]["q"])
        q = [0] * nq
        dim2 = 0
        x = 0
        z = 0
        for lab, m in counts.items():
            f = tab[lab]
            for i in range(nq):
                q[i] += m * f["q"][i]
            dim2 += m * f["dim2"]
            x += m * f["X"]
            z += m * f["z"]
        return q, dim2, x, z % 4

    def dual_bound(self, dim_max=20, mu_box=30.0, max_iter=400, early_stop_below=17.0, verbose=False, forbid=(),
                   initial_cuts=None, log=None):
        """Cutting-plane LP: maximise 4*mu_0 subject to mu.q(O) <= cost(O) for every monomial O found by the oracle.
        Returns dict(bound=4*mu_0 at termination, certified=bool, mu, cuts)."""
        fields = self.field_table()
        nq = len(fields[0]["q"])
        cuts = []  # (q vector, cost)
        if initial_cuts:
            cuts += initial_cuts
        # the pure scalar operator Phi17^4 S*^17 (dim 21 > dim_max is outside the oracle range, but its cost 17 bounds
        # mu_0 <= 17/4 anyway; include it as a cut so the LP is bounded)
        q0 = [0] * nq
        q0[0] = 4
        cuts.append((q0, 17.0))
        cuts.append(([-c for c in q0], 17.0))
        mu = None
        for it in range(max_iter):
            cvec = np.zeros(nq)
            cvec[0] = -4.0
            A_ub = np.array([c[0] for c in cuts], dtype=float)
            b_ub = np.array([c[1] for c in cuts], dtype=float)
            res = linprog(cvec, A_ub=A_ub, b_ub=b_ub, bounds=[(-mu_box, mu_box)] * nq, method="highs")
            if not res.success:
                return {"bound": None, "certified": False, "error": res.message, "cuts": cuts}
            mu = res.x
            bound = -res.fun
            if bound < early_stop_below - 1e-9:
                return {"bound": bound, "certified": False, "mu": mu.tolist(), "cuts": cuts, "iterations": it,
                        "reason": "LP bound fell below %g" % early_stop_below}
            o = self.oracle(mu, dim_max=dim_max, fields=fields, forbid=forbid)
            if o is None:
                return {"bound": bound, "certified": True, "mu": mu.tolist(), "cuts": cuts, "iterations": it, "reason": "oracle empty"}
            if o["value"] >= -1e-7:
                return {"bound": bound, "certified": True, "mu": mu.tolist(), "cuts": cuts, "iterations": it,
                        "reason": "no violated monomial with 5<=dim<=%d" % dim_max, "last_oracle": o}
            q, dim2, _x, _z = self.charges_of(o["counts"], fields)
            cost = dim2 / 2.0 + o["parity"] - 4.0
            cuts.append((q, cost))
            cuts.append(([-c for c in q], cost))  # conjugate operator
            if log is not None:
                log.append({"iter": it, "bound": bound, "op": o["counts"], "cost": cost, "q": q, "parity": o["parity"]})
            if verbose:
                print("  it %d bound %.3f cut %s cost %g q %s" % (it, bound, o["counts"], cost, q), flush=True)
        return {"bound": bound, "certified": False, "mu": mu.tolist(), "cuts": cuts, "iterations": max_iter, "reason": "max_iter"}

    # ---- explicit operators (verified singlets) and K0's closure ILP -------------------------------------------
    def enumerate_operators(self, dim_max=8, max_fermions=4, max_210=1):
        fields = self.field_table()
        ferms = [f for f in fields if f["fermion"]]
        scal = {f["label"]: f for f in fields if not f["fermion"]}
        ops = []
        seen = set()
        for nf in range(0, max_fermions + 1):
            for combo in itertools.combinations_with_replacement(range(len(ferms)), nf):
                fs = [ferms[i] for i in combo]
                nu = sum(1 for f in fs if not f["barred"])
                nb = nf - nu
                if (nu + nb) % 2:
                    continue
                deriv = 1 if nu % 2 == 1 else 0
                fx = sum(f["X"] for f in fs)
                fz = sum(f["z"] for f in fs)
                fcost = Fr(3 * nf, 2) + deriv
                budget = Fr(dim_max) - fcost
                if budget < 0:
                    continue
                R = int(budget)
                for nh in range(-R, R + 1):
                    for nd in range(-R, R + 1):
                        for npp in range(-R, R + 1):
                            for n210 in range(0, max_210 + 1):
                                c = abs(nh) + abs(nd) + abs(npp) + n210
                                if c > budget:
                                    continue
                                xs = fx - 2 * nh - 2 * nd + 17 * npp
                                if xs % 4:
                                    continue
                                ns = -xs // 4
                                dim = fcost + c + abs(ns)
                                if dim > dim_max or dim < 5:
                                    continue
                                if (fz + 2 * nh + 2 * nd) % 4:
                                    continue
                                counts = {}
                                for f in fs:
                                    counts[f["label"]] = counts.get(f["label"], 0) + 1
                                for name, m in (("H10", nh), ("Delta", nd), ("S", ns), ("Phi17", npp)):
                                    if m > 0:
                                        counts[name] = m
                                    elif m < 0:
                                        counts[name + "^"] = -m
                                if n210:
                                    counts["Phi210"] = n210
                                key = tuple(sorted(counts.items()))
                                if key in seen:
                                    continue
                                seen.add(key)
                                ops.append({"counts": counts, "dim": dim, "derivative": deriv, "nf": nf})
        # verify SO(10) invariance
        tab = {f["label"]: f for f in fields}
        verified = []
        for op in ops:
            reps = []
            for lab, m in op["counts"].items():
                r = tab[lab]["rep"]
                if r != 1:
                    reps += [r] * m
            ns = n_singlets(tuple(sorted(reps)))
            if ns <= 0:
                continue
            q, dim2, x, z = self.charges_of(op["counts"], fields)
            assert x == 0 and z == 0
            chir = {n: 0 for n in self.fnames}
            snet = {n: 0 for n in SCALAR_NAMES}
            for lab, m in op["counts"].items():
                f = tab[lab]
                s = -1 if f["barred"] else 1
                if f["fermion"]:
                    chir[f["base"]] += s * m
                else:
                    snet[f["base"]] += s * m
            op.update({"q": q, "singlets": ns, "chir": chir, "snet": snet, "cost": float(op["dim"] - 4)})
            verified.append(op)
        return verified, len(ops)

    def vertices(self):
        """renormalizable Yukawa vertices as (name, fermion list, scalar net dict, sign)."""
        out = []
        for i, t in enumerate(self.renormalizable_terms()):
            s = t["scalar"]
            sc = {}
            if s not in ("mass", "Phi210"):
                if s.startswith("conj["):
                    sc[s[5:-1]] = -1
                else:
                    sc[s] = 1
            name = "v%d(%s.%s)" % (i, ".".join(t["fermions"]), s)
            out.append((name, t["fermions"], sc, +1))
            out.append((name + "*", t["fermions"], sc, -1))
        return out

    def closure_ilp(self, ops, g2_target=4, forbid_ops=(), forbid_vertices=(), max_ops=16, eft=False):
        yuk = [v for v in self.vertices() if v[0] not in forbid_vertices]
        nop, ny = len(ops), len(yuk)
        if nop == 0:
            return None
        cost = []
        for op in ops:
            d = op["dim"]
            if eft:
                d -= op["counts"].get("Phi17", 0) + op["counts"].get("Phi17^", 0)
            cost.append(float(d - 4))
        c = np.array([x + 1e-3 for x in cost] + [1e-3] * ny)
        rows, lbs, ubs = [], [], []
        for sp in self.fnames:
            row = [op["chir"][sp] for op in ops] + [s * ferms.count(sp) for _n, ferms, _sc, s in yuk]
            rows.append(row)
            lbs.append(0)
            ubs.append(0)
        row = [op["snet"]["Phi17"] for op in ops] + [s * sc.get("Phi17", 0) for _n, _f, sc, s in yuk]
        rows.append(row)
        lbs.append(g2_target)
        ubs.append(g2_target)
        rows.append([1] * nop + [0] * ny)
        lbs.append(1)
        ubs.append(max_ops)
        ub = np.full(nop + ny, 16.0)
        for j in forbid_ops:
            ub[j] = 0
        res = milp(c, constraints=LinearConstraint(np.array(rows, dtype=float), lbs, ubs), integrality=np.ones(nop + ny),
                   bounds=Bounds(np.zeros(nop + ny), ub), options={"mip_rel_gap": 0.0})
        if not res.success:
            return None
        m = {j: int(round(res.x[j])) for j in range(nop) if round(res.x[j]) > 0}
        v = {yuk[k][0]: int(round(res.x[nop + k])) for k in range(ny) if round(res.x[nop + k]) > 0}
        return {"K": float(round(sum(cost[j] * mj for j, mj in m.items()))), "ops": m, "vertices": v}

    def describe(self, sol, ops):
        ydef = {v[0]: v for v in self.vertices()}
        snet = {n: 0 for n in SCALAR_NAMES}
        nferm = 0
        K = 0
        nvert = 0
        op_list = []
        for j, m in sol["ops"].items():
            op = ops[j]
            op_list.append("%d x [%s] (dim %s)" % (m, label(op["counts"]), op["dim"]))
            for n in SCALAR_NAMES:
                snet[n] += m * op["snet"][n]
            nferm += m * op["nf"]
            K += m * (op["dim"] - 4)
            nvert += m
        for name, m in sol["vertices"].items():
            _n, ferms, sc, s = ydef[name]
            for n, q in sc.items():
                snet[n] += m * s * q
            nferm += 2 * m
            nvert += m
        n_h = snet["H10"]
        vev_dim = abs(snet["S"]) + abs(snet["Phi17"]) + abs(snet["Delta"]) + abs(snet["Phi210"])
        h_internal = abs(n_h) // 2 * 2
        h_ew = abs(n_h) - h_internal
        n_kappa = h_internal // 2
        vev_dim += n_kappa
        nvert += n_kappa
        props = nferm // 2 + h_internal
        loops = props - nvert + 1
        D = 4 + int(K) - vev_dim - h_ew - n_kappa
        return {"planck_operators": op_list, "vertices": sol["vertices"], "K": int(K),
                "vev_monomial": {k: v for k, v in snet.items() if v}, "H10_internal_lines": h_internal, "H10_EW_vevs": h_ew,
                "kappa_vertices": n_kappa, "fermion_fields": nferm, "loops": loops, "loop_integral_dimension_D": D}

    @staticmethod
    def estimate(desc, m_s=1.0e13, sigma=3.0e13, phi=1.0e17, v_r=2.6e13, y=0.35, lam=1.0, Y=0.5, kappa=5.0e12,
                 v_ew=174.0, v_u=2.1e16):
        L = desc["loops"]
        lg = -L * math.log10(16 * math.pi ** 2)
        for name, m in desc["vertices"].items():
            # S-type (mass) vertices ~ y; H10/Delta family vertices ~ Y; other H10 vertices ~ lam
            if ".S)" in name or ".conj[S])" in name or ".Phi17)" in name or ".conj[Phi17])" in name:
                lg += m * math.log10(y)
            elif name.startswith("v") and "F.F." in name:
                lg += m * math.log10(Y)
            else:
                lg += m * math.log10(lam)
        vm = desc["vev_monomial"]
        lg += abs(vm.get("S", 0)) * math.log10(sigma) + abs(vm.get("Phi17", 0)) * math.log10(phi)
        lg += abs(vm.get("Delta", 0)) * math.log10(v_r) + desc["H10_EW_vevs"] * math.log10(v_ew)
        lg += abs(vm.get("Phi210", 0)) * math.log10(v_u)
        lg += desc["kappa_vertices"] * (math.log10(sigma) + math.log10(kappa))
        D = desc["loop_integral_dimension_D"]
        mloop = m_s if D < 0 else MPL
        lg += D * math.log10(mloop) - desc["K"] * math.log10(MPL)
        lg_tree = math.log10(2) + 4 * math.log10(phi) + 17 * math.log10(sigma) - 17 * math.log10(MPL)
        return {"log10_V_GeV4": lg, "log10_dtheta": lg - math.log10(CHI), "log10_ratio_to_tree": lg - lg_tree,
                "log10_dtheta_tree_dim21": lg_tree - math.log10(CHI)}

    # ---- decay operators ------------------------------------------------------------------------------------
    def min_operator(self, q_target, forbid=(), max_fermions=None, exact_fermions=None, dim_max=30, allow_free=()):
        """minimal-dimension monomial (necessary conditions) with kernel charges q_target (list, None = free)."""
        fields = [f for f in self.field_table() if f["label"] not in forbid]
        n = len(fields)
        nq = len(fields[0]["q"])
        best = None
        for parity in (0, 1):
            c = np.concatenate([np.array([f["dim2"] for f in fields], dtype=float), np.zeros(3)])
            rows, lbs, ubs = [], [], []

            def add(cf, aux, lb, ub):
                rows.append(np.concatenate([np.array(cf, dtype=float), np.array(aux, dtype=float)]))
                lbs.append(lb)
                ubs.append(ub)
            add([f["X"] for f in fields], [0, 0, 0], 0, 0)
            add([f["z"] for f in fields], [-4, 0, 0], 0, 0)
            add([1 if (f["fermion"] and not f["barred"]) else 0 for f in fields], [0, -2, 0], parity, parity)
            add([1 if (f["fermion"] and f["barred"]) else 0 for f in fields], [0, 0, -2], parity, parity)
            for i in range(nq):
                if q_target[i] is None:
                    continue
                add([f["q"][i] for f in fields], [0, 0, 0], q_target[i], q_target[i])
            if max_fermions is not None:
                add([1 if f["fermion"] else 0 for f in fields], [0, 0, 0], 0, max_fermions)
            if exact_fermions is not None:
                add([1 if f["fermion"] else 0 for f in fields], [0, 0, 0], exact_fermions, exact_fermions)
            add([1] * n, [0, 0, 0], 1, 200)
            add([f["dim2"] for f in fields], [0, 0, 0], 0, 2 * dim_max)
            A = np.vstack(rows)
            lb = np.zeros(n + 3)
            ub = np.full(n + 3, 60.0)
            lb[n:] = -60
            res = milp(c, constraints=LinearConstraint(A, lbs, ubs), integrality=np.ones(n + 3), bounds=Bounds(lb, ub),
                       options={"mip_rel_gap": 0.0})
            if res.success:
                counts = {fields[i]["label"]: int(round(res.x[i])) for i in range(n) if round(res.x[i]) > 0}
                dim = Fr(int(round(res.fun)), 2) + parity
                if best is None or dim < best[0]:
                    best = (dim, counts, parity)
        return best

    def is_singlet(self, counts):
        tab = {f["label"]: f for f in self.field_table()}
        reps = []
        for lab, m in counts.items():
            r = tab[lab]["rep"]
            if r != 1:
                reps += [r] * m
        return n_singlets(tuple(sorted(reps)))

    def r_parity(self):
        odd = [n for n in self.fnames if abs(self.frep[n]) != 16]
        return {"R_odd_fermions": odd, "R_even_fermions": [n for n in self.fnames if abs(self.frep[n]) == 16]}


def label(counts):
    return " ".join("%s^%d" % (k, v) if v > 1 else k for k, v in counts.items())


def jsonable(o):
    if isinstance(o, Fr):
        return str(o)
    if isinstance(o, (sympy.Basic,)):
        return str(o)
    if isinstance(o, sympy.Matrix):
        return [str(e) for e in o]
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    return o


F17 = [("F", 16, 1, 3), ("TenA", 10, -1, 1), ("TenB", 10, 5, 1), ("Vec1", 16, 0, 1), ("Vec1bar", -16, 4, 1),
       ("Vec2", 16, -3, 1), ("Vec2bar", -16, 7, 1), ("Vec3", 16, -6, 1), ("Vec3bar", -16, 10, 1),
       ("PhiV", 16, -9, 1), ("PhiVbar", -16, -8, 1), ("SingN", 1, -3, 2), ("SingM", 1, -1, 2)]
