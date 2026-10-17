"""Verifier v7: explicit-formula NDA for the two decisive PQ-violating vacuum closures of the v21-F17 theory,
with every operator re-checked by hand (X sum, Spin(10) centre, Klimyk singlet count, chirality closure,
vev monomial), the repository kappa convention (kappa = -r0/4 in chart units -> kappa = M_I/4 in GeV, the
one-light-doublet tuning; B-type doublet mass^2 = 4|kappa|<S> = M_I^2) and the anomaly sums in Fractions.

Closure E (researcher's variant E): 7 Planck operators, y1^2 y2^4 y3^2, three kappa* vertices, 5 loops.
Closure C (most conservative, from v5): 4 Planck operators of dim 7/8 only, y1 y2^2 y3^2, 2 loops,
  no H10 line, no kappa, no Delta vev, no Phi-sector, no family or tensor fermion.
"""
from __future__ import annotations

import json
import math
import sys
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from so10_singlets_klimyk import singlets  # noqa: E402

MPL = 2.435e18
CHI = 0.0755 ** 4          # GeV^4, chi_QCD = (75.5 MeV)^4
L16 = 16 * math.pi ** 2

# name -> (signed SO(10) dim, X, is_fermion, generations)
FIELDS = {"F": (16, 1, True, 3), "TenA": (10, -1, True, 1), "TenB": (10, 5, True, 1),
          "Vec1": (16, 0, True, 1), "Vec1bar": (-16, 4, True, 1), "Vec2": (16, -3, True, 1), "Vec2bar": (-16, 7, True, 1),
          "Vec3": (16, -6, True, 1), "Vec3bar": (-16, 10, True, 1), "PhiV": (16, -9, True, 1), "PhiVbar": (-16, -8, True, 1),
          "SingN": (1, -3, True, 2), "SingM": (1, -1, True, 2),
          "H10": (10, -2, False, 1), "Delta": (-126, -2, False, 1), "S": (1, 4, False, 1), "Phi17": (1, 17, False, 1)}
CENTRE = {16: 1, -16: 3, 10: 2, -126: 2, 1: 0}


def conj_rep(r):
    return r if abs(r) in (1, 10) else -r


def op_check(fields):
    """fields: list of (name, barred). Returns dict with X sum, centre, dim, singlets."""
    x = 0
    z = 0
    dim = Fr(0)
    reps = []
    nu = nb = 0
    for n, b in fields:
        r, X, ferm, _g = FIELDS[n]
        s = -1 if b else 1
        x += s * X
        rr = conj_rep(r) if b else r
        z += CENTRE[rr]
        dim += Fr(3, 2) if ferm else 1
        if rr != 1:
            reps.append(rr)
        if ferm:
            if b:
                nb += 1
            else:
                nu += 1
    lorentz_ok = (nu % 2 == 0 and nb % 2 == 0)
    return {"X_sum": x, "centre_mod4": z % 4, "dim": dim, "so10_singlets": singlets(reps), "lorentz_scalar_no_derivative": lorentz_ok}


def closure_check(ops, yukawas, kappa_conj):
    """ops: list of (multiplicity, [(name, barred), ...]); yukawas: dict name->(mult, sign) with field content;
    kappa_conj: number of kappa* (H10* H10* S*) vertices.  Returns chirality balance, vev monomial, K, loops."""
    YUK = {"y1": (["Vec1", "Vec1bar"], {"S": -1}), "y2": (["Vec2", "Vec2bar"], {"S": -1}), "y3": (["Vec3", "Vec3bar"], {"S": -1})}
    chir = {}
    scal = {"H10": 0, "Delta": 0, "S": 0, "Phi17": 0}
    K = 0
    nferm = 0
    nvert = 0
    for m, fl in ops:
        info = op_check(fl)
        assert info["X_sum"] == 0, fl
        assert info["so10_singlets"] > 0, fl
        assert info["lorentz_scalar_no_derivative"], fl
        K += m * (info["dim"] - 4)
        nvert += m
        for n, b in fl:
            s = -1 if b else 1
            if FIELDS[n][2]:
                chir[n] = chir.get(n, 0) + s * m
                nferm += m
            else:
                scal[n] += s * m
    for name, (m, sgn) in yukawas.items():
        ferms, sc = YUK[name]
        for f in ferms:
            chir[f] = chir.get(f, 0) + sgn * m
        for n, q in sc.items():
            scal[n] += sgn * q * m
        nferm += 2 * m
        nvert += m
    scal["H10"] -= 2 * kappa_conj
    scal["S"] -= kappa_conj
    nvert += kappa_conj
    nH = sum(m * sum(1 for n, b in fl if n == "H10") for m, fl in ops)
    # H10 fields of the Planck operators: each contracts with one leg of a kappa* vertex (nH propagators) when
    # kappa vertices are used; otherwise with each other (nH/2 propagators).
    nH_props = nH if kappa_conj else nH // 2
    props = nferm // 2 + nH_props
    loops = props - nvert + 1
    return {"chirality_balance": chir, "vev_monomial": {k: v for k, v in scal.items() if v}, "K": int(K), "fermion_fields": nferm,
            "H10_propagators": nH_props, "vertices": nvert, "loops": loops}


def main():
    out = {}
    # ---- anomalies (Fractions)
    T = {16: Fr(2), 10: Fr(1), 1: Fr(0)}
    DIM = {16: 16, 10: 10, 1: 1}
    a2 = sum(g * T[abs(r)] * X for n, (r, X, f, g) in FIELDS.items() if f)
    ag = sum(g * DIM[abs(r)] * X for n, (r, X, f, g) in FIELDS.items() if f)
    a3 = sum(g * DIM[abs(r)] * X ** 3 for n, (r, X, f, g) in FIELDS.items() if f)
    out["anomalies"] = {"SO10^2 X": str(a2), "grav X": str(ag), "X^3": str(a3)}
    print("anomalies:", out["anomalies"])

    # ---- closure E (researcher's variant E)
    E_ops = [(2, [("Vec1", True), ("Vec3", True), ("H10", False), ("S", True)]),
             (2, [("Vec1bar", True), ("Vec2bar", True), ("H10", False), ("S", True), ("Phi17", False)]),
             (2, [("Vec2", True), ("Vec2", True), ("H10", False), ("S", True)]),
             (1, [("Vec2bar", True), ("Vec2bar", True), ("Vec3bar", True), ("Vec3bar", True), ("Phi17", False), ("Phi17", False)])]
    E_yuk = {"y1": (2, +1), "y2": (4, +1), "y3": (2, +1)}
    out["E_operators"] = [{"mult": m, "fields": ["%s%s" % (n, "*" if b else "") for n, b in fl], **{k: str(v) for k, v in op_check(fl).items()}} for m, fl in E_ops]
    out["E_closure"] = closure_check(E_ops, E_yuk, kappa_conj=3)
    print("E operators:", json.dumps(out["E_operators"], indent=1))
    print("E closure:", out["E_closure"])

    # ---- closure C (most conservative; v5 'safe_noH10_noPhi_noFamily_noDelta_noTensors')
    C_ops = [(1, [("Vec1bar", True), ("Vec2", True), ("S", True), ("S", True), ("S", True), ("S", True), ("Phi17", False)]),
             (2, [("Vec2bar", True), ("Vec3", True), ("S", True), ("S", True), ("S", True), ("S", True), ("Phi17", False)]),
             (1, [("Vec1", True), ("Vec2", True), ("Vec3bar", True), ("Vec3bar", True), ("Phi17", False)])]
    C_yuk = {"y1": (1, +1), "y2": (2, +1), "y3": (2, +1)}
    out["C_operators"] = [{"mult": m, "fields": ["%s%s" % (n, "*" if b else "") for n, b in fl], **{k: str(v) for k, v in op_check(fl).items()}} for m, fl in C_ops]
    out["C_closure"] = closure_check(C_ops, C_yuk, kappa_conj=0)
    print("C operators:", json.dumps(out["C_operators"], indent=1))
    print("C closure:", out["C_closure"])

    # ---- explicit NDA
    # kappa convention: repository default kappa = -r0/4 (chart units, |Phi210| = 1 <-> M_GUT, r0 = M_I/M_GUT):
    # kappa = M_I/4 in GeV; doublet mass matrix A = 2|kappa|<S>, B = 2 kappa <S> -> eigenvalues 0 and 4|kappa|<S> = M_H^2.
    # B-type propagator <H_u H_d>(k) = B/((k^2+m_u^2)(k^2+m_d^2) - B^2) = B/(k^2 (k^2 + M_H^2)) -> 1/(2 k^2) for k << M_H.
    rows = {}
    for vR in (2.5e13, 3.4e13):
        kappa = vR / 4
        rows["v_R=%.1e" % vR] = {"kappa_GeV": kappa, "M_H^2=4|kappa|<S> at <S>=3.3e13": 4 * kappa * 3.3e13, "M_H_GeV": math.sqrt(4 * kappa * 3.3e13)}
    out["kappa_from_repository_convention"] = rows
    print("kappa:", json.dumps(rows, indent=1))

    def est_E(Ms, ys, Phi=1.0e17, MH=2.6e13):
        S = Ms / ys
        # V = c (16pi^2)^-5 (1/2)^3 M_s^6 <S>^6 <Phi>^4 / M_Pl^12   (fermion lines at M_s, 6 B-type H10 lines ~ 1/(2k^2), M_s <= M_H)
        # if M_s > M_H the B-lines are ~ (M_H^2/2)/k^4: replace M_s^6 by M_s^6 (M_H/M_s)^6 -> min(M_s, M_H)^6 as the loop factor
        Ml = min(Ms, MH)
        lg = -5 * math.log10(L16) - 3 * math.log10(2) + 6 * math.log10(Ml) + 6 * math.log10(S) + 4 * math.log10(Phi) - 12 * math.log10(MPL)
        # researcher-style accounting for comparison: (16pi^2)^-5 y^8 kappa^3 <S>^17 Phi^4 /(M_Pl^12 M_s^8), kappa = 5e12
        lg_r = -5 * math.log10(L16) + 8 * math.log10(ys) + 3 * math.log10(5e12) + 17 * math.log10(S) + 4 * math.log10(Phi) - 12 * math.log10(MPL) - 8 * math.log10(Ms)
        return {"<S>": S, "log10_V_GeV4": lg, "log10_dtheta": lg - math.log10(CHI), "log10_dtheta_researcher_accounting": lg_r - math.log10(CHI)}

    def est_C(Ms, ys, Phi=1.0e17):
        S = Ms / ys
        mu = S ** 4 * Phi / MPL ** 4          # dim-8 mass mixing Vec1bar-Vec2 and Vec2bar-Vec3
        c7 = Phi / MPL ** 3                   # dim-7 four-fermion coefficient
        # figure-8: V = c (16pi^2)^-2 c7 * [mu12 mu23 M_s] * [mu23 M_s^2] (two coincident-point flip propagators)
        V = c7 * (mu * mu * Ms) * (mu * Ms ** 2) / L16 ** 2
        return {"<S>": S, "mu_mixing_GeV": mu, "log10_V_GeV4": math.log10(V), "log10_dtheta": math.log10(V / CHI),
                "log10_dtheta_with_log_enhancement_ln(MPl^2/Ms^2)": math.log10(V / CHI * math.log(MPL ** 2 / Ms ** 2))}

    def est_tree(Ms, ys, Phi=1.0e17):
        S = Ms / ys
        return math.log10(2) + 4 * math.log10(Phi) + 17 * math.log10(S) - 17 * math.log10(MPL) - math.log10(CHI)

    pts = [(1.0e13, 0.304), (1.0e13, 0.35), (1.0e13, 0.374), (3.0e12, 0.091), (3.0e12, 0.2), (3.0e12, 0.35)]
    tab = {}
    for Ms, ys in pts:
        key = "Ms=%.0e ys=%.3f" % (Ms, ys)
        tab[key] = {"closure_E": est_E(Ms, ys), "closure_C": est_C(Ms, ys), "log10_dtheta_declared_tree": est_tree(Ms, ys)}
        print(key, "| E: log10 dtheta = %.2f (researcher acc. %.2f) | C: %.2f (with log %.2f) | tree: %.2f" % (
            tab[key]["closure_E"]["log10_dtheta"], tab[key]["closure_E"]["log10_dtheta_researcher_accounting"],
            tab[key]["closure_C"]["log10_dtheta"], tab[key]["closure_C"]["log10_dtheta_with_log_enhancement_ln(MPl^2/Ms^2)"],
            tab[key]["log10_dtheta_declared_tree"]))
    out["nda_table"] = tab
    # what reduction of Planck coefficients would be needed for closure C to pass at (1e13, 0.374)
    need = tab["Ms=1e+13 ys=0.374"]["closure_C"]["log10_dtheta"] + 10
    out["closure_C_orders_above_1e-10_at_1e13_0.374"] = need
    out["closure_E_orders_above_1e-10_at_1e13_0.374"] = tab["Ms=1e+13 ys=0.374"]["closure_E"]["log10_dtheta"] + 10
    print("orders above 1e-10 at (1e13, 0.374): C %.2f, E %.2f" % (need, out["closure_E_orders_above_1e-10_at_1e13_0.374"]))
    (HERE / "v7_explicit_nda.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
