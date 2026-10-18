#!/usr/bin/env python3
"""SELECTOR cross-check (EXACT, explicit 32x32 spinor computation): sector patterns of the X-allowed d=5 Yukawa
channels available in design L2 (v20 scalars + real 45_H), relative to the renormalisable 10 channel.

Why: two Stage-1 designs (D-A, D-C) were falsified when their EST Clebsch structures were computed exactly.  The only
unkilled design (D-D L2) fitted flavour with a single antisymmetric matrix A and sector weights
   d: 1+rho, e: 1-3 rho, u: eta1+eps rho, nu: eta1-3 eps rho     (eta1 = +1, rho and eps FREE REALS for the 210 channel)
and, for L3', eta1 = -1, eps = +1 (45 channel).  Here we compute the exact weights of every 120-type channel.

Construction (adapted from the D-A skeptic's sk_clebsch.py; own code):
  * gammas G_0..G_9 (0-5 SO(6), 6-9 SO(4)), chirality G11, 16 = +1 eigenspace, B with B G_a B^-1 = -G_a^T.
  * Cartan h_k = -i Sigma_{2k,2k+1}.  Convention fixed by the REPO: omega = j6 ^ (e67 + e89) is an SM singlet, so
    T3R := (h4 + h5)/2 and T3L := (h4 - h5)/2.  SU(2)_L doublets (Q, L) = states with T3R = 0.  Quark/lepton from |B-L|.
  * Higgs neutral components of the 10: n_pm = (e8 +- i e9)/sqrt2 (h4 = 0 => Q = T3L + T3R = 0).
  * Channel forms for a given n:  10: n;  120_210_X: interior(X, n) (X = repo unit forms p, a, omega);
    120_45_Y: n ^ Y (Y = unit 2-forms T3R = (e67+e89)/sqrt2, BL = j6/sqrt3);  10_45_Y: (Y.n) (vector);
    126_210_X: n ^ X (5-form).
  * Y(form)[i,j] = psi_i^T B Gamma(form) psi_j.  Ratio = projection on the 10-channel coupling with the SAME n,
    separately on quark (Q x q^c) and lepton (L x l^c) pairs; residual = norm of the orthogonal remainder.
Output: sel_clebsch.json.  Labels: EXACT (finite-dimensional linear algebra, float64 at 1e-15).
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np

REPO = r"C:\Users\jayal\Downloads\So10Theory2\So10Theory\_v22research"
HERE = Path(__file__).resolve().parent
if REPO not in sys.path:
    sys.path.insert(0, REPO)
import direct_phi_h_sigmabar_tensor_v20 as direct  # noqa: E402  (read-only import)

s0 = np.eye(2); sx = np.array([[0, 1], [1, 0]], complex); sy = np.array([[0, -1j], [1j, 0]]); sz = np.diag([1.0, -1.0]).astype(complex)


def kron(*ms):
    out = np.array([[1.0 + 0j]])
    for m in ms:
        out = np.kron(out, m)
    return out


G = []
for k in range(5):
    pre = [sz] * k; post = [s0] * (4 - k)
    G.append(kron(*pre, sx, *post)); G.append(kron(*pre, sy, *post))
for i in range(10):
    for j in range(10):
        assert np.allclose(G[i] @ G[j] + G[j] @ G[i], 2 * np.eye(32) * (i == j))
G11 = np.eye(32, dtype=complex)
for g in G:
    G11 = G11 @ g
G11 = G11 * (-1j) ** 5
B = None
for parity in (0, 1):
    Bm = np.eye(32, dtype=complex)
    for a in range(10):
        if (a % 2 == 1) == bool(parity):
            Bm = Bm @ G[a]
    if all(np.allclose(Bm @ G[a] @ np.linalg.inv(Bm), -G[a].T) for a in range(10)):
        B = Bm; break
assert B is not None
w, U = np.linalg.eigh(G11)
P16 = U[:, w > 0]
assert P16.shape[1] == 16


def gamma_of_form(form):
    M = np.zeros((32, 32), complex)
    for idx, val in form.items():
        g = np.eye(32, dtype=complex)
        for i in idx:
            g = g @ G[i]
        M = M + val * g
    return M


Hc = [-1j * 0.5 * G[2 * k] @ G[2 * k + 1] for k in range(5)]
Hc16 = [P16.conj().T @ h @ P16 for h in Hc]
Mtot = sum((1.0 + 0.1 * k * np.pi) * h for k, h in enumerate(Hc16))
_, Ve = np.linalg.eigh(Mtot)
states = P16 @ Ve
weights = np.array([[np.real(np.vdot(states[:, n], Hc[k] @ states[:, n])) for k in range(5)] for n in range(16)])
assert np.allclose(weights, np.round(weights * 2) / 2, atol=1e-12)
weights = np.round(weights * 2) / 2
BL = -(2.0 / 3.0) * weights[:, :3].sum(1)
T3R = 0.5 * (weights[:, 3] + weights[:, 4])   # repo convention: e67 + e89 is the SU(2)_R Cartan direction
T3L = 0.5 * (weights[:, 3] - weights[:, 4])
doublet = np.abs(T3R) < 1e-9
lepton = np.abs(np.abs(BL) - 1) < 1e-9
assert doublet.sum() == 8 and lepton.sum() == 4


def unit(form):
    return direct.normalize_210_or_10(form)


def cvec_form(vec):
    return {(a,): complex(v) for a, v in enumerate(vec) if abs(v) > 0}


def interior_vec(form, vec):
    out = {}
    for a, v in enumerate(vec):
        if abs(v) == 0:
            continue
        for idx, c in direct.interior(form, a).items():
            out[idx] = out.get(idx, 0) + v * c
    return {k: c for k, c in out.items() if abs(c) > 1e-15}


def twoform_matrix(form):
    M = np.zeros((10, 10), complex)
    for (i, j), c in form.items():
        M[i, j] += c; M[j, i] -= c
    return M


basis = direct.singlet_basis()
PHI = {"P": basis["p"], "A": basis["a"], "W": basis["omega"]}
e67 = direct.wedge(direct.one_form(6), direct.one_form(7)); e89 = direct.wedge(direct.one_form(8), direct.one_form(9))
j6 = direct.add_forms(*[direct.wedge(direct.one_form(2 * k), direct.one_form(2 * k + 1)) for k in range(3)])
A45 = {"T3R": unit(direct.add_forms(e67, e89)), "BL": unit(j6), "T3L": unit(direct.add_forms(e67, direct.scale_form(e89, -1)))}
# sanity: omega (repo) and A45 T3R/BL are SM singlets <=> commute with SU(2)_L generators (e67 - e89, e68 + e79 ...)
nvec = {}
for sgn, lab in ((+1, "n+"), (-1, "n-")):
    v = np.zeros(10, complex); v[8] = 1 / np.sqrt(2); v[9] = sgn * 1j / np.sqrt(2)
    nvec[lab] = v


def bilinear(form):
    return states.T @ (B @ gamma_of_form(form)) @ states


pairs = {(q, s): [(i, j) for i in range(16) for j in range(16)
                  if doublet[i] and not doublet[j] and (lepton[i] == (q == "l")) and (lepton[j] == (q == "l"))
                  and np.sign(T3L[i]) == s]
         for q in ("q", "l") for s in (+1, -1)}


def channel_forms(v):
    nf = cvec_form(v)
    ch = {"10": nf}
    for k, f in PHI.items():
        ch[f"120_210_{k}"] = interior_vec(f, v)
        ch[f"126_210_{k}"] = direct.wedge(nf, f)
    for k, f in A45.items():
        ch[f"120_45_{k}"] = direct.wedge(nf, f)
        vec = twoform_matrix(f) @ v
        ch[f"10_45_{k}"] = cvec_form(np.where(np.abs(vec) > 1e-15, vec, 0))
    return ch


res = {"convention": "T3R=(h4+h5)/2 (repo omega = j6^(e67+e89) is SM singlet); n+-=(e8+-i e9)/sqrt2; 16 = G11=+1",
       "sector_def": "sector s = sign(T3L) of the doublet leg; the 10 channel with n+ populates exactly one sector"}
supp = {}
for lab, v in nvec.items():
    ch = channel_forms(v)
    Y10 = bilinear(ch["10"])
    # which sector does the 10 populate with this n?
    pop = {f"{q}{'+' if s > 0 else '-'}": float(np.sqrt(sum(abs(Y10[i, j]) ** 2 for i, j in pairs[(q, s)]))) for (q, s) in pairs}
    supp[lab] = pop
    entry = {"10_population": pop}
    for name, form in ch.items():
        if len(form) == 0:
            entry[name] = "ZERO"
            continue
        Y = bilinear(form)
        sym = float(np.max(np.abs(Y + Y.T))); asym = float(np.max(np.abs(Y - Y.T)))
        e = {"max|Y+Y^T|": sym, "max|Y-Y^T|": asym}
        tot_out = 0.0
        for (q, s), pl in pairs.items():
            den = sum(abs(Y10[i, j]) ** 2 for i, j in pl)
            if den < 1e-20:
                tot_out += sum(abs(Y[i, j]) ** 2 for i, j in pl)
                continue
            num = sum(Y[i, j] * np.conj(Y10[i, j]) for i, j in pl)
            r = num / den
            resid = float(np.sqrt(sum(abs(Y[i, j] - r * Y10[i, j]) ** 2 for i, j in pl) / den))
            e[f"{q}{'+' if s > 0 else '-'}"] = {"ratio": [round(float(np.real(r)), 12), round(float(np.imag(r)), 12)], "resid": resid}
        # anything outside the doublet x singlet pairs of the populated sector (charge conservation check)
        allp = set(p for pl in pairs.values() for p in pl)
        outside = float(np.sqrt(sum(abs(Y[i, j]) ** 2 for i in range(16) for j in range(16)
                                    if (i, j) not in allp and (j, i) not in allp)))
        e["off_sector_norm"] = outside + float(np.sqrt(tot_out))
        entry[name] = e
    res[lab] = entry

# sector patterns (d, e, u, nu) relative to the 10 channel: identify down/up sectors by T3L of the doublet leg:
# the up quark mass pairs u_L (T3L = +1/2) with u^c -> sector '+' = up, '-' = down (sign conventions only swap u <-> d,
# which leaves the +-1 / -3 patterns and the eta1, eps signs invariant).
def pat(name):
    out = {}
    for lab in nvec:
        e = res[lab].get(name)
        if not isinstance(e, dict):
            continue
        for key in ("q+", "q-", "l+", "l-"):
            if key in e:
                out[(lab, key)] = complex(*e[key]["ratio"]), e[key]["resid"]
    d = {}
    for (lab, key), (r, rs) in out.items():
        sector = ("u" if key[0] == "q" else "nu") if key[1] == "+" else ("d" if key[0] == "q" else "e")
        d[sector] = {"ratio": [r.real, r.imag], "resid": rs, "via": lab}
    return d


patterns = {name: pat(name) for name in channel_forms(nvec["n+"]).keys()}
res["patterns_dEUnu"] = patterns
json.dump(res, open(HERE / "sel_clebsch.json", "w"), indent=1, default=str)
print("10-channel population per neutral component:", json.dumps(supp))
for name, d in patterns.items():
    s = "  ".join(f"{k}: {v['ratio'][0]:+.4f}{v['ratio'][1]:+.4f}i (res {v['resid']:.1e})" for k, v in sorted(d.items()))
    print(f"{name:12s} {s}")
