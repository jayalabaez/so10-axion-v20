"""Re-run of the researcher's vacuum-diagram ILP (read-only import of k0_vacuum_diagram / k0_quality_relics,
Susyno counts reused from susyno/cand_in.txt + cand_out.txt) with the missing physical constraint:

  the vev monomial of a vacuum diagram must be a gauge singlet.  The only Delta126bar vev is <Delta_R>
  (the B-L = 2, SM-singlet member of (10bar,1,3)); a holomorphic SO(10)-invariant polynomial restricted to a
  single non-zero-weight direction vanishes identically, so a net Delta count != 0 in the vev monomial
  makes the diagram ZERO (the researcher's variants A (K=9, Delta^4), B (K=10, Delta^2), D (K=11), F/G (P=6)
  are therefore not valid closures).  Constraint added: net Delta = 0.  Also reported: a Fermi-safe
  variant (<= 2 identical Weyl fields per operator) and a kappa-free (no H10 line) variant.

NDA for each optimum at the configuration in force (G3 family member: kappa = -r0^2/(4 r_S), tuned doublet
massless at tree level, Im-10 doublet at M_I; hence H-H pairing maximal and all light lines <= M_s):
  V ~ (16 pi^2)^-L  y^(n_yuk)  <S>^(nS) <Phi>^(nPhi) kappa^(n_k) <S>^(n_k)  M_s^D / M_Pl^K,  D = 4 + K - vev_dim - n_k
with M_s = y <S>; dtheta = V/chi.  EST (NDA).
"""
from __future__ import annotations

import json
import math
import sys
from fractions import Fraction as Fr
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

HERE = Path(__file__).resolve().parent
RES = HERE.parent                      # researcher folder (read-only)
sys.path.insert(0, str(RES))
import k0_vacuum_diagram as kvd        # noqa: E402  (read-only import; no writers executed)

MPL = 2.435e18
CHI = 0.0755 ** 4
L16 = 16 * math.pi ** 2


def load_ops():
    cands = kvd.enumerate_candidates(max_fermions=4, dim_max=Fr(8))
    multisets = sorted({kvd.rep_multiset(c["counts"]) for c in cands})
    # reuse the researcher's Susyno run: cand_in.txt lines "m%d r1 r2 ..." / cand_out.txt "m%d count"
    ms_by_id = {}
    for line in (RES / "susyno" / "cand_in.txt").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.split()
        reps = tuple(sorted(int(r) for r in parts[1:])) if parts[1:] != ["1"] else tuple()
        ms_by_id[parts[0]] = reps
    cnt_by_id = {}
    for line in (RES / "susyno" / "cand_out.txt").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        k, v = line.split()
        cnt_by_id[k] = int(v)
    singlets = {ms_by_id[k]: cnt_by_id[k] for k in ms_by_id}
    assert set(multisets) <= set(singlets), "multiset list differs from the researcher's Susyno input"
    ops = []
    for c in cands:
        ms = kvd.rep_multiset(c["counts"])
        if singlets[ms] <= 0:
            continue
        x, g2, f1, f2, f3, chir, snet = kvd.charge_vector(c["counts"])
        assert x == 0
        c.update({"G2": g2, "f": (f1, f2, f3), "chir": chir, "snet": snet, "singlets": singlets[ms]})
        ops.append(c)
    return ops


def ilp(ops, *, net_delta_zero=True, fermi_safe=False, forbid_h10=False, forbid_phi_sector=False,
        forbid_h10_yukawas=False, forbid_family_yukawas=False, g2_target=4, max_ops=12):
    yuk = []
    for name, (ferms, scal) in kvd.YUKAWAS.items():
        yuk.append((name, ferms, scal, +1))
        yuk.append((name + "*", ferms, scal, -1))
    nop, ny = len(ops), len(yuk)
    cost = [float(op["dim"] - 4) for op in ops]
    c = np.array([x + 1e-3 for x in cost] + [1e-3] * ny)
    rows, lbs, ubs = [], [], []
    for sp in kvd.FERMION_NAMES:
        rows.append([op["chir"][sp] for op in ops] + [s * ferms.count(sp) for _n, ferms, _sc, s in yuk])
        lbs.append(0); ubs.append(0)
    rows.append([op["snet"]["Phi17"] for op in ops] + [s * scal.get("Phi17", 0) for _n, _f, scal, s in yuk])
    lbs.append(g2_target); ubs.append(g2_target)
    if net_delta_zero:
        rows.append([op["snet"]["Delta"] for op in ops] + [s * scal.get("Delta", 0) for _n, _f, scal, s in yuk])
        lbs.append(0); ubs.append(0)
    # H10 legs must pair up (even net count; EW vevs cost v_EW/M_Pl ~ 1e-16 each and are excluded here)
    # -> enforce net H10 even via an integer slack: net_H = 2 k
    rows.append([op["snet"]["H10"] for op in ops] + [s * scal.get("H10", 0) for _n, _f, scal, s in yuk] )
    # (handled below with an auxiliary integer variable)
    rows.append([1] * nop + [0] * ny); lbs.append(1); ubs.append(max_ops)
    ub = np.full(nop + ny, 12.0)
    for j, op in enumerate(ops):
        labels = list(op["counts"].keys())
        bases = [l.rstrip("^") for l in labels]
        if fermi_safe and any(n > 2 for n in op["counts"].values()):
            ub[j] = 0
        if forbid_h10 and "H10" in bases:
            ub[j] = 0
        if forbid_phi_sector and any(b in ("PhiV", "PhiVbar") for b in bases):
            ub[j] = 0
    for k, (name, *_r) in enumerate(yuk):
        base = name.rstrip("*")
        if forbid_h10 and base in ("Y10", "lamF2", "lam3P", "yAM", "yBN"):
            ub[nop + k] = 0
        if forbid_phi_sector and base in ("yP", "lam3P"):
            ub[nop + k] = 0
        if forbid_h10_yukawas and base in ("lamF2", "lam3P", "yAM", "yBN"):
            ub[nop + k] = 0
        if forbid_family_yukawas and base in ("Y10", "Y126", "lamF2"):
            ub[nop + k] = 0
    # auxiliary variable for H10 parity: net_H - 2 k = 0, k integer in [-24, 24]
    A = np.array(rows, dtype=float)
    hrow = A[-2].copy()
    A = np.delete(A, -2, axis=0)
    lbs2 = lbs[:]; ubs2 = ubs[:]
    A = np.hstack([A, np.zeros((A.shape[0], 1))])
    hrow = np.append(hrow, -2.0)
    A = np.vstack([A, hrow]); lbs2.append(0); ubs2.append(0)
    c2 = np.append(c, 0.0)
    lo = np.append(np.zeros(nop + ny), -24.0); hi = np.append(ub, 24.0)
    res = milp(c2, constraints=LinearConstraint(A, lbs2, ubs2), integrality=np.ones(nop + ny + 1), bounds=Bounds(lo, hi))
    if not res.success:
        return None
    m = {j: int(round(res.x[j])) for j in range(nop) if round(res.x[j]) > 0}
    v = {yuk[k][0]: int(round(res.x[nop + k])) for k in range(ny) if round(res.x[nop + k]) > 0}
    return {"K": float(round(res.fun)), "ops": m, "yukawas": v}


def nda(desc, sigma, phi, y, kappa, m_s=None):
    """Researcher-style NDA with M_loop = M_s for D < 0 (all light lines at <= M_s in the configuration in force)."""
    m_s = y * sigma if m_s is None else m_s
    L = desc["loops"]
    lg = -L * math.log10(L16)
    for name, m in desc["yukawa_vertices"].items():
        base = name.rstrip("*")
        lg += m * math.log10(y if base in ("y1", "y2", "y3", "yAB", "yNM", "yP") else (0.5 if base in ("Y10", "Y126") else 1.0))
    vm = desc["vev_monomial"]
    lg += abs(vm.get("S", 0)) * math.log10(sigma) + abs(vm.get("Phi17", 0)) * math.log10(phi)
    lg += abs(vm.get("Delta", 0)) * math.log10(2.6e13)
    lg += desc["kappa_vertices"] * (math.log10(sigma) + math.log10(kappa))
    D = desc["loop_integral_dimension_D"]
    lg += D * math.log10(m_s if D < 0 else MPL) - desc["K_uv"] * math.log10(MPL)
    return lg - math.log10(CHI)


def main():
    ops = load_ops()
    print("verified SO(10)-singlet operators:", len(ops), flush=True)
    variants = {
        "all_couplings_netDelta0": dict(),
        "all_couplings_netDelta0_fermiSafe": dict(fermi_safe=True),
        "noPhiSector_netDelta0": dict(forbid_phi_sector=True),
        "noPhiSector_noH10Yuk_noFamilyYuk_netDelta0 (researcher E)": dict(forbid_phi_sector=True, forbid_h10_yukawas=True, forbid_family_yukawas=True),
        "kappaFree_noH10_netDelta0": dict(forbid_h10=True),
        "kappaFree_noH10_netDelta0_fermiSafe": dict(forbid_h10=True, fermi_safe=True),
        "kappaFree_noH10_noPhiSector_netDelta0_fermiSafe": dict(forbid_h10=True, fermi_safe=True, forbid_phi_sector=True),
        "RESEARCHER_UNCONSTRAINED_all (netDelta free, for comparison)": dict(net_delta_zero=False),
    }
    out = {}
    for tag, kw in variants.items():
        best = None
        for g2 in (4, -4):
            r = ilp(ops, g2_target=g2, **kw)
            if r and (best is None or r["K"] < best["K"]):
                best = r
        if best is None:
            out[tag] = None
            print("==", tag, "INFEASIBLE", flush=True)
            continue
        d = kvd.describe(best, ops)
        est = {}
        for (sig, y) in ((1e13 / 0.304, 0.304), (1e13 / 0.374, 0.374), (3e12 / 0.35, 0.35), (3e12 / 0.091, 0.091)):
            for phi in (1e17, 3e16):
                kappa = (2.6e13) ** 2 / (4 * sig)          # kappa <S> = M_I^2/4 (configuration in force)
                est["<S>=%.3g(y=%.3f),<Phi>=%.0e,kappa=%.2g" % (sig, y, phi, kappa)] = round(nda(d, sig, phi, y, kappa), 2)
        out[tag] = {"K": best["K"], **d, "log10_dtheta_NDA": est}
        print("==", tag, "K =", best["K"], "| loops", d["loops"], "| vev", d["vev_monomial"], "| kappa", d["kappa_vertices"], "| D", d["loop_integral_dimension_D"])
        for s in d["planck_operators"]:
            print("     ", s)
        print("      yukawas", d["yukawa_vertices"])
        for k, v in est.items():
            print("      log10 dtheta", k, "=", v)
        sys.stdout.flush()
    (HERE / "v2_closure_gauge_invariant.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
