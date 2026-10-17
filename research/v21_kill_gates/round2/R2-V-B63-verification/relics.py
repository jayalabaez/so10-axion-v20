"""R2-V item (6): R-parity (exact) and the lowest-dimension decay operators of each accidental sector of
v21-F17-B63, by direct enumeration with an exact SO(10) singlet check (so10_chars.py), no heuristic exclusions.

For a sector k (accidental U(1) f_k), a decay operator contains exactly ONE sector-k field (or conjugate), other
fermions from a q-neutral pool, and scalars; it must be X-neutral, Spin(10)-centre neutral, Lorentz-consistent
(#psi and #psibar both even, or both odd with one derivative, +1 dimension) and contain an SO(10) singlet.
Pools: 'SM' = {F, F^} (always kinematically open); 'SM+Rodd' = {F, F^, T, T^, NMm, NMm^}.
Lifetimes are EST (order of magnitude): 2-fermion operators -> either a physical light-Higgs leg (Gamma ~ y_eff^2 M/16pi)
or a mass mixing (Gamma ~ theta^2 M/25); 4-fermion -> Gamma ~ G^2 M^5/(192 pi^3).
"""
from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

import so10_chars as so

HERE = Path(__file__).resolve().parent
FERM = {"F": (16, 1), "V1": (16, -35), "Vb1": (-16, 39), "V2": (16, -28), "Vb2": (-16, 32), "V3": (16, 34),
        "Vb3": (-16, -30), "T": (10, 2), "Pb": (-16, 18), "N1": (1, -63), "N1b": (1, 59), "N2": (1, -58),
        "N2b": (1, 54), "N3": (1, -57), "N3b": (1, 61), "NMm": (1, -2)}
ZC = {16: 1, -16: 3, 10: 2, 1: 0, 126: 2, -126: 2, 210: 0}
SECTORS = {"f1 (V1,Vb1,Pb)": ["V1", "Vb1", "Pb"], "f2 (V2,Vb2,V3,Vb3)": ["V2", "Vb2", "V3", "Vb3"],
           "f3 (N1,N1b)": ["N1", "N1b"], "f4 (N2,N2b)": ["N2", "N2b"], "f5 (N3,N3b)": ["N3", "N3b"]}
POOLS = {"SM": ["F", "F^"], "SM+Rodd": ["F", "F^", "T", "T^", "NMm", "NMm^"]}
VEV = {"S": 3.0e13, "Phi17": 1.0e17, "Delta": 2.6e13, "Phi210": 2.1e16, "H10": 174.0}
MPL = 2.435e18
HBAR = 6.582e-25


def fdata(lab):
    base = lab.rstrip("^")
    r, x = FERM[base]
    if lab.endswith("^"):
        return so.conj_code(r) if r != 10 else 10, -x, (-ZC[r]) % 4, 0, 1
    return r, x, ZC[r] % 4, 1, 0


def scalar_options(X_need, z_need, dmax):
    """scalar monomials with total X = X_need, z = z_need mod 4, sorted by dimension."""
    out = []
    for h_p, h_m, d_p, d_m, p in itertools.product(range(3), range(3), range(3), range(3), range(2)):
        z = 2 * (h_p + h_m + d_p + d_m)
        if (z - z_need) % 4:
            continue
        rest = X_need + 2 * (h_p - h_m) + 2 * (d_p - d_m)  # 4 nS + 17 nP = rest
        base = h_p + h_m + d_p + d_m + p
        for nP in range(-6, 7):
            r = rest - 17 * nP
            if r % 4:
                continue
            nS = r // 4
            dim = base + abs(nS) + abs(nP)
            if dim > dmax:
                continue
            out.append((dim, {"H10": h_p, "H10^": h_m, "Delta": d_p, "Delta^": d_m, "Phi210": p, "S" if nS >= 0 else "S^": abs(nS),
                              "Phi17" if nP >= 0 else "Phi17^": abs(nP)}))
    out.sort(key=lambda t: t[0])
    return out


_SING = {}


def singlets_cached(reps):
    key = tuple(sorted(reps))
    if key not in _SING:
        _SING[key] = so.singlets_of(list(key))
    return _SING[key]


def reps_of(ferms, scal):
    reps = []
    for lab in ferms:
        r = fdata(lab)[0]
        if r != 1:
            reps.append(r)
    reps += [10] * (scal.get("H10", 0) + scal.get("H10^", 0)) + [-126] * scal.get("Delta", 0) + [126] * scal.get("Delta^", 0)
    reps += [210] * scal.get("Phi210", 0)
    return reps


def best_operator(member_labels, pool, nf_extra_options=(1, 3), dmax_total=16):
    best = []
    for lab0 in member_labels:
        for m in nf_extra_options:
            for extra in itertools.combinations_with_replacement(pool, m):
                ferms = (lab0,) + extra
                X = sum(fdata(l)[1] for l in ferms)
                z = sum(fdata(l)[2] for l in ferms) % 4
                nu = sum(fdata(l)[3] for l in ferms)
                nb = sum(fdata(l)[4] for l in ferms)
                if (nu + nb) % 2:
                    continue
                deriv = 1 if nu % 2 else 0
                fdim = 1.5 * len(ferms) + deriv
                for sdim, sc in scalar_options(-X, (-z) % 4, int(dmax_total - fdim)):
                    if singlets_cached(reps_of(ferms, sc)) > 0:
                        best.append((fdim + sdim, ferms, {k: v for k, v in sc.items() if v}, deriv))
                        break
    best.sort(key=lambda t: t[0])
    return best


def lifetime(dim, ferms, sc, M=1.0e13, phys_higgs=True):
    K = dim - 4
    vev = 1.0
    nh = sc.get("H10", 0) + sc.get("H10^", 0)
    for k, v in sc.items():
        b = k.rstrip("^")
        if b == "H10" and phys_higgs and len(ferms) == 2:
            continue  # one H10 leg taken as the physical light Higgs (2-body decay)
        vev *= VEV[b] ** v
    if len(ferms) == 2:
        if nh and phys_higgs:
            y = vev / MPL ** K * (VEV["H10"] ** (nh - 1) if nh > 1 else 1.0)
            g = y * y * M / (16 * math.pi)
            mode = "psi -> F + h (physical light Higgs leg)"
        else:
            mmix = vev / MPL ** K
            g = (mmix / M) ** 2 * M / 25.0
            mode = "mass mixing with F, theta = m_mix/M"
    else:
        G = vev / MPL ** K
        g = G * G * M ** 5 / (192 * math.pi ** 3)
        mode = "4-fermion"
    return {"Gamma_GeV": g, "tau_s": HBAR / g if g > 0 else float("inf"), "mode": mode}


def main():
    out = {}
    # R-parity: R = (-1)^z (-1)^(2s); unbroken discrete subgroup of Spin(10)-centre x U(1)_X
    rpar = {n: (+1 if ZC[r] % 2 else -1) for n, (r, x) in FERM.items()}  # fermions: (-1)^z * (-1)
    vevs = {"Phi210": (210, 0), "Delta": (-126, -2), "H10": (10, -2), "S": (1, 4), "Phi17": (1, 17)}
    unbroken = []
    for k in range(4):
        for a_num in range(68):  # alpha = 2 pi a/68 suffices since 4 and 17 divide 68
            ok = True
            for nm, (r, x) in vevs.items():
                phase = (k * ZC[r]) / 4 + a_num * x / 68  # in units of 2 pi
                if abs(phase - round(phase)) > 1e-12:
                    ok = False
                    break
            if ok:
                unbroken.append((k, a_num))
    out["R_parity"] = {"R_of_fermions": rpar, "R_odd": [n for n, v in rpar.items() if v < 0],
                       "unbroken_(centre k, X angle 2pi a/68)": unbroken,
                       "note": "all scalars have even z -> R-even; the only unbroken element besides 1 is the Spin(10) centre "
                               "element k=2 ((-1)^z), so R = (-1)^z (-1)^(2s) is exact and the lightest R-odd state is absolutely stable"}
    print("R-odd:", out["R_parity"]["R_odd"], " unbroken:", unbroken, flush=True)
    out["sectors"] = {}
    for sec, members in SECTORS.items():
        labs = members + [m + "^" for m in members]
        res = {}
        for pname, pool in POOLS.items():
            rodd_sector = all(rpar[m] < 0 for m in members)
            if rodd_sector and pname == "SM":
                continue  # an R-odd state must decay into an R-odd state
            ops = best_operator(labs, pool)
            top = []
            seen_dim = None
            for dim, ferms, sc, deriv in ops[:12]:
                if seen_dim is None:
                    seen_dim = dim
                if dim > seen_dim + 1:
                    break
                lt = lifetime(dim, ferms, sc)
                top.append({"dim": dim, "fermions": list(ferms), "scalars": sc, "derivative": deriv, **lt})
            res[pname] = top
            print(sec, pname, [(t["dim"], t["fermions"], t["scalars"], "%.1e s" % t["tau_s"]) for t in top[:4]], flush=True)
        out["sectors"][sec] = res
    (HERE / "relics.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
