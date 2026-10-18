#!/usr/bin/env python3
"""SKEPTIC D2 (EXACT, explicit spinor computation): SM Clebsches of the d=5 operators F.F.(H10 x Phi210)_{120,126}/Lambda
at the design orientation Phi210 = p P + a A (+ omega W), with the repo's own p, a, omega four-forms.

Construction (own code):
  * SO(10) Clifford algebra, 32x32 gammas G_0..G_9 (indices 0-5 = SO(6) ~ SU(4), 6-9 = SO(4) ~ SU(2)_L x SU(2)_R, as in
    direct_phi_h_sigmabar_tensor_v20.singlet_basis), chirality G11, 16 = +1 eigenspace, charge-conjugation matrix B with
    B G_a B^-1 = -G_a^T (so psi^T B G_[k] psi is invariant).
  * A k-form w acts as Gamma(w) = sum_{i1<..<ik} w_{i1..ik} G_i1...G_ik.
  * Effective Yukawa bilinear of an operator with tensor w: Y(w)[psi1, psi2] = psi1^T B Gamma(w) psi2 on 16 x 16.
  * SM states inside the 16: simultaneous eigenvectors of the Cartan generators; B-L from J6 = e01+e23+e45, T3L/T3R from
    e67, e89.  The doublet direction H = unit vector along an SO(4) index alpha (the (1,2,2) of the 10).
  * Clebsch ratio e/d, nu/u: coefficient of (L e^c) over (Q d^c) [and (L nu^c) over (Q u^c)] for the same H component.
Channels: 10 (w = H), 120 (w = interior(H, Phi)), 126+126bar (w = H ^ Phi, both duality projections).
Expected (tensor argument): 120 channel with P: e/d = 1, nu/u = 1, and the same H-component selection as the 10, so
c_e = c_u = c_D = 1; the A form contributes nothing to the 120 channel for a doublet H; 126 channel from A: e/d = -3.
"""
from __future__ import annotations
import itertools, json
import numpy as np
import sk_loader as LD

direct = LD.direct
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
G = [np.asarray(g, complex) for g in G]
for i in range(10):
    for j in range(10):
        ac = G[i] @ G[j] + G[j] @ G[i]
        assert np.allclose(ac, 2 * np.eye(32) * (i == j))
G11 = np.eye(32, dtype=complex)
for g in G:
    G11 = G11 @ g
G11 = G11 * (-1j) ** 5
assert np.allclose(G11 @ G11, np.eye(32))
# B: product of the antisymmetric(=imaginary sy-type) or symmetric gammas; find B with B G_a B^-1 = -G_a^T by search
cands = []
for parity in (0, 1):
    Bm = np.eye(32, dtype=complex)
    for a in range(10):
        if (a % 2 == 1) == bool(parity):   # odd-index gammas contain sy (imaginary, antisymmetric)
            Bm = Bm @ G[a]
    ok = all(np.allclose(Bm @ G[a] @ np.linalg.inv(Bm), -G[a].T) for a in range(10))
    if ok:
        cands.append(Bm)
assert cands, "no B found"
B = cands[0]
# 16 subspace
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


def gen(i, j):
    return 0.5 * G[i] @ G[j]   # Sigma_ij (anti-Hermitian)


# Cartan generators (Hermitian): h1..h5 = -i Sigma_{01}, -i Sigma_{23}, -i Sigma_{45}, -i Sigma_{67}, -i Sigma_{89}
Hc = [-1j * gen(0, 1), -1j * gen(2, 3), -1j * gen(4, 5), -1j * gen(6, 7), -1j * gen(8, 9)]
Hc16 = [P16.conj().T @ h @ P16 for h in Hc]
# simultaneous eigenbasis of the 5 commuting Cartan generators in the 16
Mtot = sum((1.0 + 0.1 * k * np.pi) * h for k, h in enumerate(Hc16))
we, Ve = np.linalg.eigh(Mtot)
states = P16 @ Ve
weights = np.array([[np.real(np.vdot(states[:, n], Hc[k] @ states[:, n])) for k in range(5)] for n in range(16)])
weights = np.round(weights * 2) / 2
# quantum numbers: B-L = -(2/3)(h1+h2+h3) up to sign convention; T3L, T3R = (h4 +- h5)/2
BL = -(2.0 / 3.0) * weights[:, :3].sum(1)
T3L = 0.5 * (weights[:, 3] + weights[:, 4]); T3R = 0.5 * (weights[:, 3] - weights[:, 4])
# the convention signs (which of T3L/T3R is 'left') are fixed below by the chirality of SO(4): left doublets have T3R = 0
lab = []
for n in range(16):
    bl, tl, tr = BL[n], T3L[n], T3R[n]
    lepton = abs(abs(bl) - 1) < 1e-9
    if abs(tr) < 1e-9:   # SU(2)_L doublet member (Q or L)
        kind = ("L" if lepton else "Q") + ("_up" if tl > 0 else "_dn")
    else:
        if lepton:
            kind = "nuc" if tr * np.sign(-bl) > 0 else "ec"
        else:
            kind = "uc" if tr * np.sign(-bl) > 0 else "dc"
    lab.append(kind)
# The sign conventions of B-L / T3R inside the conjugate states are ambiguous by an overall flip; we only need the
# PAIRINGS: a Yukawa with H component couples (doublet member) x (singlet member) of the same SU(3)-colour contraction.
# We therefore classify bilinears by (lepton/quark) and by which doublet member they involve, and compare channels.
out = {"weights": weights.tolist(), "labels": lab}
basis = direct.singlet_basis()
pf, af, wf = basis["p"], basis["a"], basis["omega"]


def bilinear(form):
    M = B @ gamma_of_form(form)
    return states.T @ M @ states      # Y[n, m] = psi_n^T B Gamma psi_m


res = {}
for alpha in (6, 7, 8, 9):
    Hf = direct.one_form(alpha)
    chans = {"10": Hf,
             "120_P": direct.interior(pf, alpha) if True else None,
             "120_A": direct.interior(af, alpha),
             "120_W": direct.interior(wf, alpha),
             "5form_P": direct.wedge(Hf, pf),
             "5form_A": direct.wedge(Hf, af),
             "5form_W": direct.wedge(Hf, wf)}
    entry = {}
    Y10 = bilinear(chans["10"])
    for name, form in chans.items():
        if len(form) == 0:
            entry[name] = "ZERO form (no coupling)"
            continue
        Y = bilinear(form)
        # quark-sector and lepton-sector couplings: sum |Y|^2 over (quark doublet, quark singlet) and (lepton, lepton) pairs
        qq = [(i, j) for i in range(16) for j in range(16) if lab[i].startswith("Q") and lab[j] in ("uc", "dc")]
        ll = [(i, j) for i in range(16) for j in range(16) if lab[i].startswith("L") and lab[j] in ("nuc", "ec")]
        # ratio relative to the 10-channel coefficient on the SAME (i, j) entries (projection onto the 10 pattern)
        def ratio(pairs):
            num = sum(Y[i, j] * np.conj(Y10[i, j]) for i, j in pairs); den = sum(abs(Y10[i, j]) ** 2 for i, j in pairs)
            resid = np.sqrt(sum(abs(Y[i, j] - (num / den) * Y10[i, j]) ** 2 for i, j in pairs)) if den > 0 else None
            return (num / den if den > 0 else None), resid
        rq, eq = ratio(qq); rl, el = ratio(ll)
        sym = float(np.max(np.abs(Y + Y.T))); asym = float(np.max(np.abs(Y - Y.T)))
        entry[name] = {"quark_ratio_to_10": [complex(rq).real, complex(rq).imag] if rq is not None else None, "quark_resid": eq,
                       "lepton_ratio_to_10": [complex(rl).real, complex(rl).imag] if rl is not None else None, "lepton_resid": el,
                       "lepton/quark": (complex(rl / rq).real if (rq not in (None, 0) and abs(rq) > 1e-12) else None),
                       "max|Y+Y^T|": sym, "max|Y-Y^T|": asym}
    res[f"H_alpha={alpha}"] = entry
out["channels"] = res
print(json.dumps(res, indent=1, default=str))
json.dump(out, open(LD.HERE / "sk_clebsch.json", "w"), indent=1, default=str)
