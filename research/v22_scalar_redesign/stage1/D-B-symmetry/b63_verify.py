"""R2-V: independent verification of v21-F17-B63, items (1)-(3) and the quality numbers of (4).
Own code: SO(10) singlets from so10_chars.py (Weyl-denominator multiplicity formula on explicitly built characters),
exact Fractions for anomalies, own Fraction Gaussian elimination for the accidental kernel.
Writes b63_verify.json.
"""
from __future__ import annotations

import itertools
import json
import math
import sys
from fractions import Fraction as Fr
from pathlib import Path

import numpy as np

import so10_chars as so

HERE = Path(__file__).resolve().parent
R1 = Path(r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21\K0b-charge-variants")

# ---- content typed from the task statement (species = fields with identical quantum numbers merged) --------------
# (name, signed SO(10) rep, X, generations)
FERMIONS = [
    ("F", 16, 1, 3),
    ("V1", 16, -35, 2),   # 16(-35) of the conj[S] pair AND 16(-35) of the Phi17 pair: one 2-generation species
    ("Vb1", -16, 39, 1),
    ("V2", 16, -28, 1), ("Vb2", -16, 32, 1),
    ("V3", 16, 34, 1), ("Vb3", -16, -30, 1),
    ("T", 10, 2, 2),
    ("Pb", -16, 18, 1),
    ("N1", 1, -63, 1), ("N1b", 1, 59, 1),
    ("N2", 1, -58, 1), ("N2b", 1, 54, 1),
    ("N3", 1, -57, 1), ("N3b", 1, 61, 1),
    ("NMm", 1, -2, 2),
]
# scalars (name, signed rep, X, real)
SCALARS = [("Phi210", 210, 0, True), ("Delta", -126, -2, False), ("H10", 10, -2, False), ("S", 1, 4, False),
           ("Phi17", 1, 17, False)]
T_IDX = {1: Fr(0), 10: Fr(1), 16: Fr(2), 126: Fr(35), 210: Fr(56)}
T_SU3 = {1: Fr(0), 10: Fr(1), 16: Fr(2)}
TRQ2 = {1: Fr(0), 10: Fr(8, 3), 16: Fr(16, 3)}
MPL = 2.435e18
CHI = 0.0755 ** 4


def check_against_round1():
    d = json.loads((R1 / "candB63.json").read_text(encoding="utf-8"))
    r1 = sorted((f[0], f[1], f[2], f[3]) for f in d["fermions"])
    mine = sorted(FERMIONS)
    return {"round1_candB63_json_equals_task_statement": r1 == mine, "round1": r1}


# ---- (1) anomalies -------------------------------------------------------------------------------------------
def anomalies():
    so10_x = sum(g * T_IDX[abs(r)] * x for _n, r, x, g in FERMIONS)
    grav = sum(g * so.DIMS[r] * x for _n, r, x, g in FERMIONS)
    x3 = sum(g * so.DIMS[r] * Fr(x) ** 3 for _n, r, x, g in FERMIONS)
    # SO(10)^3: SO(10) has no cubic Casimir (no symmetric d-tensor); check the net spinor chirality anyway
    net16 = sum(g * (1 if r == 16 else -1 if r == -16 else 0) for _n, r, x, g in FERMIONS)
    bx = sum(Fr(2, 3) * g * so.DIMS[r] * x * x for _n, r, x, g in FERMIONS)
    bx += sum(Fr(1, 3) * so.DIMS[r] * x * x for _n, r, x, real in SCALARS if not real)
    # mass partnerships (as stated): charge sums and indices
    parts = {
        "V1'+Vb1 [conj S]": ((-35, 16), (39, -16)), "V2+Vb2 [conj S]": ((-28, 16), (32, -16)),
        "V3+Vb3 [conj S]": ((34, 16), (-30, -16)), "T1+T2 Majorana [conj S]": ((2, 10), (2, 10)),
        "V1''+Pb [Phi17]": ((-35, 16), (18, -16)),
    }
    pinfo = {}
    T_S = Fr(0)
    T_Phi = Fr(0)
    for k, ((xa, ra), (xb, rb)) in parts.items():
        tp = T_IDX[abs(ra)] + T_IDX[abs(rb)]
        pinfo[k] = {"charge_sum": xa + xb, "T_p": str(tp)}
        if "[conj S]" in k:
            assert xa + xb == 4
            T_S += tp
        else:
            assert xa + xb == -17
            T_Phi += tp
    lemma = 6 + 2 * T_S - Fr(17, 2) * T_Phi
    # S-coupled Dirac-equivalent components
    s_comp = 16 + 16 + 16 + 10 + 1 + 1 + 1 + 1
    return {"SO10^2_X": str(so10_x), "grav_X": str(grav), "X^3": str(x3), "net_16_minus_16bar": net16,
            "SO10^3": "0 identically (SO(10) has no cubic Casimir); net chirality 3 = families",
            "b_X_integer_X": str(bx), "partnerships": pinfo, "T_S": str(T_S), "T_Phi": str(T_Phi),
            "lemmaA_6+2T_S-17/2T_Phi": str(lemma), "S_coupled_Dirac_equivalent_components": s_comp,
            "all_zero": so10_x == 0 and grav == 0 and x3 == 0}


# ---- (2) renormalizable couplings ------------------------------------------------------------------------------
def insertions():
    out = [("mass", 1, 0)]
    for n, r, x, real in SCALARS:
        out.append((n, r, x))
        if not real:
            out.append(("conj[%s]" % n, so.conj_code(r), -x))
    return out


def sym_antisym_singlets(r, srep):
    """for a same-species bilinear: singlets in Sym^2(r) x srep and Lambda^2(r) x srep."""
    ch = so.CHAR[r]
    ws = []
    for w, m in ch.items():
        ws += [w] * m
    from collections import Counter
    sym, asym = Counter(), Counter()
    for a in range(len(ws)):
        for b in range(a, len(ws)):
            sym[tuple(ws[a][i] + ws[b][i] for i in range(5))] += 1
            if b > a:
                asym[tuple(ws[a][i] + ws[b][i] for i in range(5))] += 1
    s2 = so.n_singlets(so.product(sym, so.CHAR[srep]))
    a2 = so.n_singlets(so.product(asym, so.CHAR[srep]))
    return s2, a2


def couplings():
    terms = []
    x_allowed_not_singlet = []
    for i, j in itertools.combinations_with_replacement(range(len(FERMIONS)), 2):
        na, ra, xa, ga = FERMIONS[i]
        nb, rb, xb, gb = FERMIONS[j]
        for sn, sr, sx in insertions():
            if xa + xb + sx != 0:
                continue
            ns = so.singlets_of([ra, rb] + ([sr] if sn != "mass" else []))
            rec = {"fermions": [na, nb], "insertion": sn, "gens": "%dx%d" % (ga, gb), "n_singlets_plain": ns}
            if i == j:
                s2, a2 = sym_antisym_singlets(ra, sr if sn != "mass" else 1)
                rec["sym_singlets"] = s2
                rec["antisym_singlets"] = a2
                # Weyl bilinear psi_a psi_b (Lorentz eps x Grassmann) is symmetric in the flavour x gauge index pair;
                # flavour-symmetric part needs gauge-symmetric invariant; flavour-antisymmetric (gens>1) needs Lambda^2
                ok = s2 > 0 or (ga > 1 and a2 > 0)
                rec["flavour_structure"] = ("sym %dx%d" % (ga, ga) if s2 > 0 else "") + (" antisym" if (ga > 1 and a2 > 0) else "")
            else:
                ok = ns > 0
            if ok:
                terms.append(rec)
            else:
                x_allowed_not_singlet.append(rec)
    bare = [t for t in terms if t["insertion"] == "mass"]
    p210 = [t for t in terms if t["insertion"] == "Phi210"]
    fam_ex = [t for t in terms if "F" in t["fermions"] and any(f != "F" for f in t["fermions"])]
    # kinetic mixing: distinct species with identical (rep, X)
    kin = [(a[0], b[0]) for a, b in itertools.combinations(FERMIONS, 2) if a[1] == b[1] and a[2] == b[2]]
    return {"terms": terms, "n_structures": len(terms), "bare_masses": bare, "phi210_yukawas": p210,
            "family_exotic_yukawas": fam_ex, "kinetic_mixings_between_distinct_species": kin,
            "X_allowed_but_SO10_forbidden": x_allowed_not_singlet}


def mass_matrices(seed=7, S=3.0e13, P=1.0e17):
    rng = np.random.default_rng(seed)
    c = lambda *s: (rng.normal(size=s) + 1j * rng.normal(size=s)) * 0.3  # noqa: E731
    Sc = np.conj(S)
    # 16 x 16bar Dirac matrix. rows: F1,F2,F3,V1a,V1b,V2,V3 ; cols: Vb1,Vb2,Vb3,Pb
    M16 = np.zeros((7, 4), dtype=complex)
    y1, yP = c(2), c(2)
    M16[3, 0], M16[4, 0] = y1[0] * Sc, y1[1] * Sc
    M16[3, 3], M16[4, 3] = yP[0] * P, yP[1] * P
    M16[5, 1] = c(1)[0] * Sc
    M16[6, 2] = c(1)[0] * Sc
    sv16 = np.linalg.svd(M16, compute_uv=False)
    u, s, vh = np.linalg.svd(M16)
    null_left = u[:, 4:]  # massless 16 combinations
    fam_weight = float(np.sum(np.abs(null_left[:3, :]) ** 2) / null_left.shape[1])
    yT = c(2, 2)
    yT = yT + yT.T
    sv10 = np.linalg.svd(yT * Sc, compute_uv=False)
    # singlet Majorana matrix: N1,N1b,N2,N2b,N3,N3b,NMm1,NMm2
    Ms = np.zeros((8, 8), dtype=complex)
    a = c(4)
    Ms[0, 1] = Ms[1, 0] = a[0] * S
    Ms[2, 3] = Ms[3, 2] = a[1] * S
    Ms[4, 5] = Ms[5, 4] = a[2] * Sc
    yM = c(2, 2)
    yM = yM + yM.T
    Ms[6:, 6:] = yM * S
    sv1 = np.linalg.svd(Ms, compute_uv=False)
    return {"16x16bar_singular_values_GeV": sorted(sv16.tolist()), "rank_16": int(np.sum(sv16 > 1e-6 * S)),
            "massless_16_combinations": int(null_left.shape[1]), "massless_16_family_weight": fam_weight,
            "10_singular_values_GeV": sorted(sv10.tolist()), "singlet_singular_values_GeV": sorted(sv1.tolist()),
            "rank_singlets": int(np.sum(sv1 > 1e-6 * S)),
            "note": "random O(0.3) complex Yukawas; exotic 16bar all paired (rank 4), the 3 massless 16 are pure F; "
                    "T (2x2) and the 8 singlets full rank; F couples only via Y10/Y126 (light families)"}


# ---- (3) kernel ------------------------------------------------------------------------------------------------
def rref_fr(rows, ncol):
    M = [[Fr(v) for v in r] for r in rows]
    piv = []
    r = 0
    for col in range(ncol):
        p = None
        for i in range(r, len(M)):
            if M[i][col] != 0:
                p = i
                break
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        inv = 1 / M[r][col]
        M[r] = [v * inv for v in M[r]]
        for i in range(len(M)):
            if i != r and M[i][col] != 0:
                f = M[i][col]
                M[i] = [M[i][k] - f * M[r][k] for k in range(ncol)]
        piv.append(col)
        r += 1
        if r == len(M):
            break
    return M[:r], piv


def nullspace_fr(rows, ncol):
    R, piv = rref_fr(rows, ncol)
    free = [c for c in range(ncol) if c not in piv]
    basis = []
    for f in free:
        v = [Fr(0)] * ncol
        v[f] = Fr(1)
        for i, pc in enumerate(piv):
            v[pc] = -R[i][f]
        basis.append(v)
    return basis, len(piv)


def rank_fr(vecs, ncol):
    return len(rref_fr(vecs, ncol)[1]) if vecs else 0


def kernel(terms):
    names = [f[0] for f in FERMIONS] + ["H10", "Delta", "S", "Phi17"]
    idx = {n: i for i, n in enumerate(names)}
    n = len(names)
    rows, labels = [], []
    for t in terms:
        row = [0] * n
        for f in t["fermions"]:
            row[idx[f]] += 1
        s = t["insertion"]
        if s not in ("mass", "Phi210"):
            if s.startswith("conj["):
                row[idx[s[5:-1]]] -= 1
            else:
                row[idx[s]] += 1
        rows.append(row)
        labels.append(".".join(t["fermions"]) + "." + s)
    # phase-sensitive renormalizable scalar terms of the v20 potential (SO(10)-invariance checked below)
    h, d, s_, p = idx["H10"], idx["Delta"], idx["S"], idx["Phi17"]
    scal = [("kappaH H10.H10.S", {h: 2, s_: 1}, [10, 10]),
            ("Phi210.conj[H10].Delta", {h: -1, d: 1}, [210, 10, -126]),
            ("Phi210.conj[H10].conj[Delta].conj[S] (O38-type)", {h: -1, d: -1, s_: -1}, None),
            ("Delta^2.conj[H10]^2", {d: 2, h: -2}, [-126, -126, 10, 10])]
    scal_info = {}
    for lab, cf, reps in scal:
        row = [0] * n
        for k, v in cf.items():
            row[k] = v
        rows.append(row)
        labels.append(lab)
        scal_info[lab] = so.singlets_of(reps if reps else [210, 10, 126])
    null, rank = nullspace_fr(rows, n)
    xvec = [Fr(f[2]) for f in FERMIONS] + [Fr(-2), Fr(-2), Fr(4), Fr(17)]
    x_in = all(sum(Fr(r[k]) * xvec[k] for k in range(n)) == 0 for r in rows)
    # round-1 basis
    def vec(dct):
        v = [Fr(0)] * n
        for k, val in dct.items():
            v[idx[k]] = Fr(val)
        return v
    G2 = vec({"V1": -1, "Vb1": 1, "Phi17": 1})
    f = [vec({"V1": 1, "Vb1": -1, "Pb": -1}), vec({"V2": 1, "Vb2": -1, "V3": -1, "Vb3": 1}), vec({"N1": 1, "N1b": -1}),
         vec({"N2": 1, "N2b": -1}), vec({"N3": 1, "N3b": -1})]
    in_ker = {}
    for lab, v in [("X", xvec), ("G2", G2)] + [("f%d" % (i + 1), fv) for i, fv in enumerate(f)]:
        in_ker[lab] = all(sum(Fr(r[k]) * v[k] for k in range(n)) == 0 for r in rows)
    span_rank = rank_fr([xvec, G2] + f, n)
    # scalar-only part of kernel
    scal_rank = rank_fr([v[len(FERMIONS):] for v in null], 4)
    return {"names": names, "n_charges": n, "constraint_rank": rank, "kernel_dim": len(null), "X_in_kernel": x_in,
            "round1_basis_in_kernel": in_ker, "rank_of_X_G2_f1..f5": span_rank,
            "basis_spans_kernel": span_rank == len(null) and all(in_ker.values()),
            "scalar_projection_rank": scal_rank, "scalar_terms_SO10_singlets": scal_info,
            "G2": {k: str(G2[idx[k]]) for k in names if G2[idx[k]] != 0},
            "f": [{k: str(fv[idx[k]]) for k in names if fv[idx[k]] != 0} for fv in f]}, (idx, xvec, G2, f)


def pq_data(idx, xvec, G2, f):
    names = list(idx)
    pq = {k: xvec[idx[k]] - 17 * G2[idx[k]] for k in names}
    N = sum(g * T_SU3[abs(r)] * pq[nm] for nm, r, x, g in FERMIONS)
    E = sum(g * TRQ2[abs(r)] * pq[nm] for nm, r, x, g in FERMIONS)
    NX = sum(g * T_SU3[abs(r)] * xvec[idx[nm]] for nm, r, x, g in FERMIONS)
    NG2 = sum(g * T_SU3[abs(r)] * G2[idx[nm]] for nm, r, x, g in FERMIONS)
    Nf = [str(sum(g * T_SU3[abs(r)] * fv[idx[nm]] for nm, r, x, g in FERMIONS)) for fv in f]
    # SU(2)_L-type and SO(10) anomalies of f_k equal the QCD ones (complete multiplets)
    # theta_eff = theta0 + c_S theta_S + c_P theta_P from the decomposition alpha_S = 4b, alpha_P = 17b + g:
    # Delta theta = 2 [N(X) b + N(G2) g] with b = alpha_S/4, g = alpha_P - 17 alpha_S/4
    cS = 2 * (NX / 4 - NG2 * Fr(17, 4))
    cP = 2 * NG2
    # gauge orbit direction (4, 17): invariant iff cS*4 + cP*17 = 0
    inv = cS * 4 + cP * 17
    # N_DW mod gauge: theta_eff = c_S theta_S + c_P theta_P on the torus modulo the orbit (4,17); with gcd(4,17)=1
    # the gauge-invariant coordinate is u = 17 theta_S - 4 theta_P (period 2 pi); theta_eff = k u with k = cS/17
    k = cS / 17
    return {"PQ_charges": {kk: str(v) for kk, v in pq.items()}, "N": str(N), "E": str(E), "E_over_N": str(E / N),
            "N(X)": str(NX), "N(G2)": str(NG2), "N(f_k)": Nf, "theta_eff_coefficients(theta_S,theta_Phi)": [str(cS), str(cP)],
            "theta_eff_gauge_invariant": inv == 0, "theta_eff = k*(17 theta_S - 4 theta_Phi), k": str(k),
            "N_DW_mod_gauge": str(abs(k)), "N_DW_S_phase_alone": str(abs(cS)), "2N": str(2 * N)}


# ---- (4b) the explicit K = 17 closure and dtheta --------------------------------------------------------------
def closure_check():
    X = {f[0]: f[2] for f in FERMIONS}
    X.update({"S": 4, "Phi17": 17})
    ops = [  # (multiplicity, {field: (n, n_conj)}, )
        (4, {"N1": (1, 0), "N2b": (1, 0), "S": (0, 2), "Phi17": (1, 0)}),
        (1, {"N1": (0, 2), "N3b": (0, 2), "S": (0, 1)}),
        (2, {"N1b": (1, 0), "N2": (2, 0), "N3b": (1, 0), "S": (0, 1)}),
    ]
    verts = [  # conj of yN1 S N1 N1b and of yN2 S N2 N2b
        (2, {"N1": (0, 1), "N1b": (0, 1), "S": (0, 1)}),
        (4, {"N2": (0, 1), "N2b": (0, 1), "S": (0, 1)}),
    ]
    out = {"operators": []}
    K = 0
    net = {}
    nfields = 0
    for m, op in ops:
        dim = Fr(0)
        x = 0
        nu = nb = 0
        for fld, (a, b) in op.items():
            ferm = fld not in ("S", "Phi17")
            dim += (Fr(3, 2) if ferm else 1) * (a + b)
            x += X[fld] * (a - b)
            if ferm:
                nu += a
                nb += b
            net[fld] = net.get(fld, 0) + m * (a - b)
            if ferm:
                nfields += m * (a + b)
        lorentz_ok = (nu % 2 == 0 and nb % 2 == 0)
        # Grassmann: a single Weyl singlet can appear at most twice (2 spinor components)
        grass_ok = all(a <= 2 and b <= 2 for fld, (a, b) in op.items() if fld not in ("S", "Phi17"))
        out["operators"].append({"mult": m, "op": op, "dim": str(dim), "X": x, "lorentz_ok": lorentz_ok,
                                 "grassmann_nonzero": grass_ok})
        K += m * (dim - 4)
    for m, v in verts:
        for fld, (a, b) in v.items():
            net[fld] = net.get(fld, 0) + m * (a - b)
            if fld not in ("S", "Phi17"):
                nfields += m * (a + b)
    # chirality closure: every fermion species must have equal numbers of psi and psi^dagger in total? no -
    # propagators are <psi psi^dag> (kinetic) or <psi chi> via the Dirac mass (N1-N1b: S-mass). The conserved
    # quantities are the accidental charges; check them:
    f3 = net.get("N1", 0) - net.get("N1b", 0)
    f4 = net.get("N2", 0) - net.get("N2b", 0)
    f5 = net.get("N3", 0) - net.get("N3b", 0)
    out.update({"K": str(K), "vev_monomial": {"S": net["S"], "Phi17": net["Phi17"]}, "f3": f3, "f4": f4, "f5": f5,
                "G2": net["Phi17"], "fermion_fields": nfields, "planck_ops": sum(m for m, _ in ops),
                "yukawa_vertices": sum(m for m, _ in verts)})
    out["loops_if_connected"] = nfields // 2 - (out["planck_ops"] + out["yukawa_vertices"]) + 1
    out["loop_integral_dimension_D"] = 4 + int(K) - (abs(net["S"]) + abs(net["Phi17"]))
    # NDA magnitude (round-1 convention: (16pi^2)^-L y^6, D = 0 -> M_Pl^0) relative to the tree operator
    L = out["loops_if_connected"]
    for y in (0.304, 0.35, 0.368):
        out["log10_ratio_to_tree_y=%.3f" % y] = -L * math.log10(16 * math.pi ** 2) + 6 * math.log10(y) - math.log10(2)
    return out


def dtheta(S, P=1.0e17, coeff=2.0):
    return coeff * (P / MPL) ** 4 * (S / MPL) ** 17 * MPL ** 4 / CHI


def quality_numbers():
    out = {}
    for S in (2.72e13, 3.0e13, 3.29e13, 3.6e13):
        out["dtheta_tree(<S>=%.3g)" % S] = dtheta(S)
    smax = MPL * (1e-10 * CHI / (2 * (1.0e17 / MPL) ** 4 * MPL ** 4)) ** (1 / 17)
    out["<S>_max(dtheta=1e-10)"] = smax
    out["y_s_min(M_s=1e13)"] = 1.0e13 / smax
    # sensitivity: <Phi17> and chi
    out["<S>_max if <Phi17>=2e17"] = MPL * (1e-10 * CHI / (2 * (2.0e17 / MPL) ** 4 * MPL ** 4)) ** (1 / 17)
    out["<S>_max if coefficient 1 (no h.c. factor 2)"] = MPL * (1e-10 * CHI / (1 * (1.0e17 / MPL) ** 4 * MPL ** 4)) ** (1 / 17)
    # axion mass / f_a (round-1 convention f_a = v_S v_P / sqrt(16 v_S^2 + 289 v_P^2), v = sqrt2 <.>)
    for S in (1.0e13 / 0.368, 1.0e13 / 0.304):
        vS, vP = math.sqrt(2) * S, math.sqrt(2) * 1.0e17
        fa = vS * vP / math.sqrt(16 * vS ** 2 + 289 * vP ** 2)
        out["f_a, m_a(ueV) at <S>=%.3g" % S] = [fa, 5.70 * 1e12 / fa]
    return out


def main():
    out = {"content_check": check_against_round1(), "so10_selftest": so.self_test()}
    out["anomalies"] = anomalies()
    c = couplings()
    out["couplings"] = c
    k, (idx, xvec, G2, f) = kernel(c["terms"])
    out["kernel"] = k
    out["pq"] = pq_data(idx, xvec, G2, f)
    out["mass_matrices"] = mass_matrices()
    out["closure_K17"] = closure_check()
    out["quality"] = quality_numbers()
    (HERE / "b63_verify.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print("content == round1:", out["content_check"]["round1_candB63_json_equals_task_statement"])
    print("anomalies:", {kk: out["anomalies"][kk] for kk in ("SO10^2_X", "grav_X", "X^3", "b_X_integer_X", "T_S", "T_Phi",
                                                               "lemmaA_6+2T_S-17/2T_Phi", "S_coupled_Dirac_equivalent_components")})
    print("n structures:", c["n_structures"])
    for t in c["terms"]:
        print("   ", ".".join(t["fermions"]), t["insertion"], t["gens"], t.get("flavour_structure", ""), "singlets", t["n_singlets_plain"])
    print("bare:", c["bare_masses"], " 210:", c["phi210_yukawas"], " fam-exotic:", c["family_exotic_yukawas"])
    print("kinetic mixings:", c["kinetic_mixings_between_distinct_species"])
    print("X-allowed SO(10)-forbidden:", [(".".join(t["fermions"]), t["insertion"]) for t in c["X_allowed_but_SO10_forbidden"]])
    print("kernel:", {kk: k[kk] for kk in ("constraint_rank", "kernel_dim", "X_in_kernel", "round1_basis_in_kernel",
                                           "rank_of_X_G2_f1..f5", "basis_spans_kernel", "scalar_projection_rank",
                                           "scalar_terms_SO10_singlets")})
    print("pq:", {kk: v for kk, v in out["pq"].items() if kk != "PQ_charges"})
    print("mass:", out["mass_matrices"])
    print("closure:", json.dumps(out["closure_K17"], default=str))
    print("quality:", json.dumps(out["quality"], indent=1))


if __name__ == "__main__":
    main()
