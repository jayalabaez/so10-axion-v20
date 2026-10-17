"""Verifier: independent exact recomputation of the K0 contract items (anomalies, complete renormalizable
coupling catalogue, accidental U(1) kernel, PQ/N/E/N_DW/f_a, the mod-4 lemma, R-parity) plus a parse of the
researcher's model-file draft (field rows, Z17 phases, LagHC terms, presence of the v20 kappa H H S term).
All arithmetic in integers / Fractions / sympy rationals.
"""
from __future__ import annotations

import itertools
import json
import re
import sys
from fractions import Fraction as Fr
from math import gcd
from pathlib import Path

import sympy

HERE = Path(__file__).resolve().parent
MODEL = HERE.parent / "models" / "SO10Z17AxionV21.m"
V20 = Path(r"C:\Users\jayal\Downloads\So10Theory2\So10Theory\_g6_nogo\models\SO10Z17AxionV20.m")

# (name, signed dim, X, generations)  -- the F17 catalogue as stated in the task text
FERM = [("F", 16, 1, 3), ("TenA", 10, -1, 1), ("TenB", 10, 5, 1), ("Vec1", 16, 0, 1), ("Vec1bar", -16, 4, 1),
        ("Vec2", 16, -3, 1), ("Vec2bar", -16, 7, 1), ("Vec3", 16, -6, 1), ("Vec3bar", -16, 10, 1),
        ("PhiV", 16, -9, 1), ("PhiVbar", -16, -8, 1), ("SingN", 1, -3, 2), ("SingM", 1, -1, 2)]
SCAL = [("Phi210", 210, 0, True), ("Delta126bar", -126, -2, False), ("H10", 10, -2, False), ("S", 1, 4, False),
        ("Phi17", 1, 17, False)]
T = {1: Fr(0), 10: Fr(1), 16: Fr(2)}
DIM = {1: 1, 10: 10, 16: 16}
# SO(10) tensor products needed for bilinears (Slansky); signed labels; self-conjugate: 1,10,45,54,120,210
TP = {(16, 16): {10, 120, 126}, (-16, -16): {10, 120, -126}, (-16, 16): {1, 45, 210}, (10, 10): {1, 45, 54},
      (10, 16): {16, 144}, (-16, 10): {-16, -144}, (1, 1): {1}, (1, 10): {10}, (1, 16): {16}, (-16, 1): {-16}}
SELFC = {1, 10, 45, 54, 120, 210}


def conj(r):
    return r if abs(r) in SELFC else -r


def enumerate_couplings():
    ins = [("mass", 1, 0)]
    for n, r, x, real in SCAL:
        ins.append((n, r, x))
        if not real:
            ins.append(("conj[%s]" % n, conj(r), -x))
    found = []
    for (fa, ra, xa, ga), (fb, rb, xb, gb) in itertools.combinations_with_replacement(FERM, 2):
        prod = TP[tuple(sorted((ra, rb)))]
        for lab, sr, sx in ins:
            if xa + xb + sx != 0:
                continue
            if conj(sr) in prod:
                found.append((tuple(sorted((fa, fb))), lab))
    return sorted(found)


def parse_model(path):
    txt = path.read_text(encoding="utf-8")
    rows = {}
    pat = r"(FermionFields|ScalarFields)\[\[\d+\]\]\s*=\s*\{(\w+),\s*(\d+),\s*(\w+),\s*(-?\d+),\s*(-?\d+),\s*([^}]+)\}"
    for m in re.finditer(pat, txt):
        rows[m.group(2)] = dict(kind=m.group(1), gen=int(m.group(3)), rep=int(m.group(5)), X=int(m.group(6)),
                                z17=m.group(7).strip().replace(" ", ""))
    body = txt.split("LagHC = -(", 1)[1].split(");", 1)[0]
    terms = []
    for line in body.splitlines():
        line = line.strip().lstrip("+").strip()
        if line:
            c, prod = line.split(None, 1)
            terms.append((c, [f.strip() for f in prod.split(".")]))
    return rows, terms


def main():
    out = {}
    # 1. anomalies
    a10 = sum(g * T[abs(r)] * x for _, r, x, g in FERM)
    agr = sum(g * DIM[abs(r)] * x for _, r, x, g in FERM)
    ax3 = sum(g * DIM[abs(r)] * x ** 3 for _, r, x, g in FERM)
    ts = sum(g * T[abs(r)] for n, r, x, g in FERM if n not in ("F", "PhiV", "PhiVbar"))
    tp = sum(g * T[abs(r)] for n, r, x, g in FERM if n in ("PhiV", "PhiVbar"))
    out["anomalies"] = dict(SO10_SO10_X=str(a10), grav_X=str(agr), X3=str(ax3), T_S=str(ts), T_Phi=str(tp))
    print("anomalies:", out["anomalies"])
    # 2. couplings
    enum = enumerate_couplings()
    rows, terms = parse_model(MODEL)
    fn = {f[0] for f in FERM}
    declared = sorted((tuple(sorted(f for f in facs if f in fn)), next((f for f in facs if f not in fn), "mass")) for _, facs in terms)
    out["couplings"] = dict(enumerated=[list(k[0]) + [k[1]] for k in enum], n_enumerated=len(enum),
                            declared=[list(k[0]) + [k[1]] for k in declared],
                            enum_minus_declared=[list(k[0]) + [k[1]] for k in sorted(set(enum) - set(declared))],
                            declared_minus_enum=[list(k[0]) + [k[1]] for k in sorted(set(declared) - set(enum))])
    print("enumerated couplings:", len(enum), "declared:", len(declared), "| diff:", set(enum) ^ set(declared))
    # model rows vs catalogue, Z17 phases
    bad_rows = []
    for n, r, x, g in FERM:
        row = rows.get(n)
        q = x % 17
        want = "1" if q == 0 else "Exp[2*Pi*I*%d/17]" % q
        if row is None or row["rep"] != r or row["X"] != x or row["gen"] != g or row["z17"] != want:
            bad_rows.append((n, row))
    for n, r, x, real in SCAL:
        row = rows.get(n)
        q = x % 17
        want = "1" if q == 0 else "Exp[2*Pi*I*%d/17]" % q
        if row is None or row["rep"] != r or row["X"] != x or row["z17"] != want:
            bad_rows.append((n, row))
    out["model_rows_bad"] = [str(b) for b in bad_rows]
    print("bad model rows:", bad_rows)
    # kappa H H S present?  (v20 LagHC has kappaH H10.H10.S)
    v21_txt = MODEL.read_text(encoding="utf-8")
    v20_txt = V20.read_text(encoding="utf-8")
    out["kappaH_in_v21_LagHC"] = "kappaH" in v21_txt
    out["kappaH_in_v20_LagHC"] = "kappaH" in v20_txt
    # compare LagNoHC blocks verbatim
    def nohc(t):
        return t.split("LagNoHC = -(", 1)[1].split(");", 1)[0].strip()
    out["LagNoHC_identical_to_v20"] = nohc(v21_txt) == nohc(v20_txt)
    v20_scalar_hc = [ln.strip().lstrip("+").strip() for ln in v20_txt.split("LagHC = -(", 1)[1].split(");", 1)[0].splitlines()
                     if ln.strip() and not any(f in ln for f in ("F.", "P.", "R.", "Q", "Spec"))]
    out["v20_LagHC_scalar_only_terms"] = v20_scalar_hc
    print("kappaH in v21:", out["kappaH_in_v21_LagHC"], "| in v20:", out["kappaH_in_v20_LagHC"],
          "| LagNoHC identical:", out["LagNoHC_identical_to_v20"], "| v20 scalar-only LagHC terms:", v20_scalar_hc)
    # 3. kernel of the coupling charge matrix (my own derivation, 17 unknowns)
    names = [f[0] for f in FERM] + ["H10", "Delta126bar", "S", "Phi17"]
    q = {n: sympy.Symbol("q_" + n) for n in names}
    eqs = []
    for (fa, fb), lab in enum:
        e = q[fa] + q[fb]
        if lab != "mass":
            if lab.startswith("conj["):
                e -= q[lab[5:-1]]
            elif lab != "Phi210":
                e += q[lab]
        eqs.append(e)
    # scalar potential phase-sensitive terms (v20 potential): kappa H H S, Phi210 H* Delta, Phi210 H* Delta* S*, Delta^2 H*^2
    eqs += [2 * q["H10"] + q["S"], -q["H10"] + q["Delta126bar"], -q["H10"] - q["Delta126bar"] - q["S"], 2 * q["Delta126bar"] - 2 * q["H10"]]
    A = sympy.Matrix([[sympy.diff(e, q[n]) for n in names] for e in eqs])
    ns = A.nullspace()
    out["kernel"] = dict(rank=A.rank(), dim=len(ns))
    # the hand-derived parametrisation: free h, V1, V3, PV, A
    h, v1, v3, pv, a = sympy.symbols("h v1 v3 pv a")
    param = {"F": -h / 2, "TenA": a, "TenB": -2 * h - a, "Vec1": v1, "Vec1bar": -2 * h - v1, "Vec2": 3 * h / 2, "Vec2bar": -7 * h / 2,
             "Vec3": v3, "Vec3bar": -2 * h - v3, "PhiV": pv, "PhiVbar": h + v3, "SingN": h + a, "SingM": h - a,
             "H10": h, "Delta126bar": h, "S": -2 * h, "Phi17": -pv - h - v3}
    vec = sympy.Matrix([param[n] for n in names])
    out["kernel"]["hand_parametrisation_in_kernel"] = bool((A * vec).applyfunc(sympy.simplify).is_zero_matrix)
    xv = sympy.Matrix([f[2] for f in FERM] + [-2, -2, 4, 17])
    g2 = sympy.Matrix([(-1 if n == "PhiV" else 0) for n in names[:-4]] + [0, 0, 0, 1])
    f1 = sympy.Matrix([{"Vec1": 1, "Vec1bar": -1}.get(n, 0) for n in names])
    f2 = sympy.Matrix([{"Vec3": -1, "Vec3bar": 1, "PhiV": 1, "PhiVbar": -1}.get(n, 0) for n in names])
    f3 = sympy.Matrix([{"TenA": 1, "TenB": -1, "SingN": 1, "SingM": -1}.get(n, 0) for n in names])
    gens = {"X": xv, "G2": g2, "f1": f1, "f2": f2, "f3": f3}
    out["kernel"]["generators_in_kernel"] = {k: bool((A * v).is_zero_matrix) for k, v in gens.items()}
    B = sympy.Matrix.hstack(*gens.values())
    out["kernel"]["generators_rank"] = B.rank()
    print("kernel:", out["kernel"])
    # 4. QCD / EM anomalies: T_SU3(16)=2, T_SU3(10)=1; TrQ^2(16)=16/3, TrQ^2(10)=4/3 (from SM decomposition)
    sixteen = [(3, 2, Fr(1, 6)), (3, 1, Fr(-2, 3)), (3, 1, Fr(1, 3)), (1, 2, Fr(-1, 2)), (1, 1, Fr(1)), (1, 1, Fr(0))]
    ten = [(3, 1, Fr(-1, 3)), (3, 1, Fr(1, 3)), (1, 2, Fr(1, 2)), (1, 2, Fr(-1, 2))]

    def t3q2(content):
        t3 = Fr(0)
        q2 = Fr(0)
        for c, w, y in content:
            if c == 3:
                t3 += Fr(w, 2)
            chs = [y + Fr(1, 2), y - Fr(1, 2)] if w == 2 else [y]
            q2 += c * sum(ch * ch for ch in chs)
        return t3, q2
    t16, q16 = t3q2(sixteen)
    t10, q10 = t3q2(ten)
    assert t16 == 2 and t10 == 1 and q16 == Fr(16, 3) and q10 == Fr(8, 3), (t16, t10, q16, q10)
    tsu3 = {16: t16, 10: t10, 1: Fr(0)}
    trq2 = {16: q16, 10: q10, 1: Fr(0)}

    def NE(charges):
        n = sum(g * tsu3[abs(r)] * Fr(int(charges[i])) for i, (nm, r, x, g) in enumerate(FERM))
        e = sum(g * trq2[abs(r)] * Fr(int(charges[i])) for i, (nm, r, x, g) in enumerate(FERM))
        return n, e
    pq = xv - 17 * g2
    npq, epq = NE(pq)
    out["PQ"] = dict(N=str(npq), E=str(epq), E_over_N=str(epq / npq), two_N=str(2 * npq),
                     N_of_generators={k: str(NE(v)[0]) for k, v in gens.items()},
                     PQ_charges={n: int(pq[i]) for i, n in enumerate(names)})
    print("PQ:", out["PQ"])
    # N_DW: theta_eff = T_S theta_S - T_Phi theta_Phi + 3 theta_S (families via theta_H = -theta_S/2) = 17 theta_S - 4 theta_Phi
    # gauge orbit (4,17) on the torus; the quotient circle generator (a,b) with 4b - 17a = +-1 -> (1,4): winding 17*1 - 4*4 = 1
    coeff_S = int(ts) + 3  # 14 + 3
    coeff_P = -int(tp)
    # find (a,b) with det[[4,17],[a,b]] = 4b - 17a = 1
    sol = next(((a_, b_) for a_ in range(-20, 21) for b_ in range(-20, 21) if 4 * b_ - 17 * a_ == 1))
    wind = coeff_S * sol[0] + coeff_P * sol[1]
    out["N_DW"] = dict(theta_eff="%d theta_S %+d theta_Phi" % (coeff_S, coeff_P), quotient_generator=sol,
                       winding_mod_gauge=abs(wind), N_DW_S_phase_only=Fr(abs(2 * npq), 4).numerator if Fr(abs(2 * npq), 4).denominator == 1 else str(Fr(abs(2 * npq), 4)))
    print("N_DW:", out["N_DW"])
    # f_a and m_a numbers (v = sqrt2 <field>)
    import math
    chi = 0.0755 ** 4
    MPL = 2.435e18
    vphi = math.sqrt(2) * 1e17
    rows_fa = {}
    for ys in (0.304, 0.35, 0.374, 0.388):
        S = 1e13 / ys
        vs = math.sqrt(2) * S
        fa = vs * vphi / math.sqrt(16 * vs ** 2 + 289 * vphi ** 2)
        ma = 5.70e-6 * 1e12 / fa
        dth = 2 * (1e17 / MPL) ** 4 * (S / MPL) ** 17 * MPL ** 4 / chi
        rows_fa["y_s=%.3f" % ys] = dict(S=S, f_a=fa, m_a_ueV=ma * 1e6, dtheta_declared=dth)
    Smax = MPL * (1e-10 * chi / (2 * 1e17 ** 4)) ** (1 / 17)
    out["axion_numbers"] = dict(rows=rows_fa, S_max_declared=Smax, y_min_declared_Ms1e13=1e13 / Smax)
    print("axion numbers:", json.dumps(out["axion_numbers"], indent=1))
    # 5. mod-4 lemma: X = z + G2 - f1 + 3 f2 + f3 (mod 4)
    zc = {16: 1, -16: 3, 10: 2, -126: 2, 1: 0, 210: 0}
    G2c = {"Phi17": 1, "PhiV": -1}
    f1c = {"Vec1": 1, "Vec1bar": -1}
    f2c = {"Vec3": -1, "Vec3bar": 1, "PhiV": 1, "PhiVbar": -1}
    f3c = {"TenA": 1, "TenB": -1, "SingN": 1, "SingM": -1}
    viol = []
    for n, r, x, _ in [(a_, b_, c_, d_) for a_, b_, c_, d_ in FERM] + [(a_, b_, c_, d_) for a_, b_, c_, d_ in SCAL]:
        rhs = zc[r] + G2c.get(n, 0) - f1c.get(n, 0) + 3 * f2c.get(n, 0) + f3c.get(n, 0)
        if (x - rhs) % 4:
            viol.append(n)
    out["lemma_violations"] = viol
    print("lemma violations:", viol)
    # 6. R-parity
    out["R_odd"] = [n for n, r, x, g in FERM if abs(r) != 16]
    print("R-odd:", out["R_odd"])
    (HERE / "v1_exact_contract.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
