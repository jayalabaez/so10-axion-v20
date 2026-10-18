#!/usr/bin/env python3
"""SKEPTIC D3 counter-direction for L2: the light REAL colour octets required by the design ((8,1,0) at 1-3 TeV,
(8,3,0) at ~2e9 GeV) carry cubic invariants that are generically O(M_U) at the G3211 vacuum.

EXACT (numerical linear algebra on explicit so(10) tensors, integer-exact up to float round-off):
 (1) 45_H: with <A> = w_R T3R + w_BL T_{B-L}, the 45 quartic Tr(A^4) gives the octet cubic 4 Tr(<A> O^3) and
     Tr(T_{B-L} O^3) = 2 Tr_C(H^3) != 0 (O <-> iH, H hermitian traceless 3x3), Tr(T3R O^3) = 0.
     No vacuum symmetry forbids it: SU(3) charge conjugation maps T_{B-L} -> -T_{B-L}, so w_BL != 0 breaks it.
 (2) 210_H: the cubic invariant I3 = Phi_abcd Phi_cdef Phi_efab is nonzero on the (8,1,0) ⊂ (15,1,1) and on the
     (8,3,0) ⊂ (15,3,1) subspaces (f_abc eps_ijk invariant), so the v20 Phi^3 coupling (coefficient ~ M_U) feeds both.
NUM: the O(4) bounce for V = t^2/2 - t^3/3 (shooting) -> S = S0 m^2 / A^2 for V = m^2 t^2/2 - A t^3/3.
Consequence (EST): a light real octet with an O(M_U) cubic decays with S ~ 1e-25 (TeV octet) / 1e-11 ((8,3,0) at
2e9) unless the effective cubic of the light mode is tuned below ~0.7 m: two real fine-tunings (~1e-13 and ~1e-7)
that the design's tuning list (D5) does not contain, and that must be redone at one loop.
"""
from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

HERE = Path(__file__).resolve().parent
rng = np.random.default_rng(11)

# ---- R^10 = R^6 (x1,x2,x3,y1,y2,y3) + R^4 (indices 6..9) ----
J6 = np.zeros((6, 6))
J6[0:3, 3:6] = -np.eye(3)
J6[3:6, 0:3] = np.eye(3)
J = np.zeros((10, 10)); J[:6, :6] = J6                          # T_{B-L} direction (complex structure on R^6)
TR = np.zeros((10, 10)); TR[6, 7], TR[7, 6], TR[8, 9], TR[9, 8] = 1, -1, -1, 1   # Cartan of one SU(2) in SO(4)
TL = np.zeros((10, 10)); TL[6, 7], TL[7, 6], TL[8, 9], TL[9, 8] = 1, -1, 1, -1   # Cartan of the other SU(2)

gm = []
l = np.zeros((3, 3), complex); l[0, 1] = l[1, 0] = 1; gm.append(l)
l = np.zeros((3, 3), complex); l[0, 1] = -1j; l[1, 0] = 1j; gm.append(l)
l = np.diag([1, -1, 0]).astype(complex); gm.append(l)
l = np.zeros((3, 3), complex); l[0, 2] = l[2, 0] = 1; gm.append(l)
l = np.zeros((3, 3), complex); l[0, 2] = -1j; l[2, 0] = 1j; gm.append(l)
l = np.zeros((3, 3), complex); l[1, 2] = l[2, 1] = 1; gm.append(l)
l = np.zeros((3, 3), complex); l[1, 2] = -1j; l[2, 1] = 1j; gm.append(l)
l = np.diag([1, 1, -2]).astype(complex) / math.sqrt(3); gm.append(l)


def real6(M):
    X, Y = M.real, M.imag
    return np.block([[X, -Y], [Y, X]])


def octet10(H):
    O = np.zeros((10, 10)); O[:6, :6] = real6(1j * H)
    return O


Obasis = [octet10(g / 2) for g in gm]
checks = {}
checks["octet_antisym"] = max(np.abs(O + O.T).max() for O in Obasis)
checks["octet_commutes_J"] = max(np.abs(O @ J - J @ O).max() for O in Obasis)
checks["octet_commutes_TR_TL"] = max(max(np.abs(O @ TR - TR @ O).max(), np.abs(O @ TL - TL @ O).max()) for O in Obasis)
checks["octet_orth_J"] = max(abs(np.trace(J.T @ O)) for O in Obasis)


def unit(O):
    return O / math.sqrt(0.5 * np.trace(O.T @ O))       # canonical: sum_{a<b} O_ab^2 = 1


Jh, TRh = unit(J), unit(TR)
# (1) cubic from Tr A^4
Hd = np.diag([1, 1, -2]) / math.sqrt(6.0)               # unit-normalised lambda_8-like direction (Tr H^2 = 1 ... )
O8 = unit(octet10(Hd.astype(complex)))
res = {}
res["Tr(J O^3)_lambda8"] = float(np.trace(Jh @ O8 @ O8 @ O8))
res["Tr(TR O^3)_lambda8"] = float(np.trace(TRh @ O8 @ O8 @ O8))
# identity Tr_R(J O^3) = 2 Tr_C(H^3) (unnormalised check)
H = rng.normal(size=(3, 3)) + 1j * rng.normal(size=(3, 3)); H = (H + H.conj().T) / 2; H -= np.trace(H) / 3 * np.eye(3)
Or = octet10(H)
res["identity_check"] = [float(np.trace(J @ Or @ Or @ Or)), float(2 * np.trace(H @ H @ H).real)]
# max over random unit octet directions of |Tr(J^ O^3)|
best = 0.0
for _ in range(20000):
    x = rng.normal(size=8); x /= np.linalg.norm(x)
    O = unit(sum(c * B for c, B in zip(x, Obasis)))
    best = max(best, abs(np.trace(Jh @ O @ O @ O)))
res["max_unit_|Tr(J^ O^3)|"] = float(best)
# finite-difference check: cubic coefficient of Tr((A0 + t O)^4) = 4 Tr(A0 O^3)
wR, wBL = 0.7, -1.3
A0 = wR * TRh + wBL * Jh
ts = np.array([-2, -1, 1, 2]) * 1e-2
f = [np.trace(np.linalg.matrix_power(A0 + t * O8, 4)) for t in ts]
c3_fd = (f[3] - 2 * f[2] + 2 * f[1] - f[0]) / (2 * 1e-6) / 6.0
res["Tr(A^4)_cubic_fd_vs_4Tr(A0 O^3)"] = [float(c3_fd), float(4 * np.trace(A0 @ O8 @ O8 @ O8))]
# charge conjugation: complex conjugation K on C^3 (an O(6) element) maps J -> -J
K6 = np.diag([1, 1, 1, -1, -1, -1.0]); K = np.eye(10); K[:6, :6] = K6
res["K J K^-1 = -J"] = bool(np.allclose(K @ J @ K.T, -J))


# (2) 210 cubic invariant on octet subspaces
def antisym4(T):
    out = np.zeros_like(T)
    for p in itertools.permutations(range(4)):
        sgn = np.linalg.det(np.eye(4)[list(p)])
        out += sgn * np.transpose(T, p)
    return out / 24.0


def wedge(a, b):
    return antisym4(np.einsum("ab,cd->abcd", a, b))


def I3(P):
    return float(np.einsum("abcd,cdef,efab->", P, P, P))


# self-dual / anti-self-dual 2-forms on R^4 (indices 6..9)
def two_form(i, j):
    w = np.zeros((10, 10)); w[i, j], w[j, i] = 1, -1
    return w


SD = [two_form(6, 7) + two_form(8, 9), two_form(6, 8) - two_form(7, 9), two_form(6, 9) + two_form(7, 8)]
ASD = [two_form(6, 7) - two_form(8, 9), two_form(6, 8) + two_form(7, 9), two_form(6, 9) - two_form(7, 8)]
# Levi-Civita on R^6 for the (15,1,1) = *_6(2-form)
eps6 = np.zeros((6,) * 6)
for p in itertools.permutations(range(6)):
    eps6[p] = np.linalg.det(np.eye(6)[list(p)])


def star6(O):
    P = np.zeros((10,) * 4)
    P[:6, :6, :6, :6] = 0.5 * np.einsum("ijklmn,mn->ijkl", eps6, O[:6, :6])
    return P


vals = {"(8,1,0)c(15,1,1)": [], "(8,3,0)c(15,3,1)": [], "(8,1,0)c(15,1,3)_T3R=0": []}
for _ in range(6):
    x = rng.normal(size=8)
    O = sum(c * B for c, B in zip(x, Obasis))
    vals["(8,1,0)c(15,1,1)"].append(I3(star6(O)))
    vals["(8,1,0)c(15,1,3)_T3R=0"].append(I3(wedge(O, ASD[0])))
    C = rng.normal(size=(8, 3))
    P = sum(C[a, i] * wedge(Obasis[a], SD[i]) for a in range(8) for i in range(3))
    vals["(8,3,0)c(15,3,1)"].append(I3(P))
res["210_cubic_I3_random_octet_vectors"] = vals
# the (8,3,0) invariant must be the f-eps one: vanishes if all three SU(2) components are equal-direction
P1 = sum(rng.normal() * wedge(Obasis[a], SD[0]) for a in range(8))
res["210_I3_(8,3,0)_single_SU2_component(expect 0)"] = I3(P1)


# (3) O(4) bounce for V = t^2/2 - t^3/3 (S = S0 m^2/A^2 for V = m^2 t^2/2 - A t^3/3)
def shoot(p0, rmax=40.0):
    def rhs(r, y):
        return [y[1], y[0] - y[0] ** 2 - 3.0 / max(r, 1e-9) * y[1]]

    def over(r, y):
        return y[0]
    over.terminal = True
    over.direction = -1
    def under(r, y):
        return y[1]
    under.terminal = True
    under.direction = 1
    r0 = 1e-6
    sol = solve_ivp(rhs, (r0, rmax), [p0, 0.0], events=[over, under], rtol=1e-12, atol=1e-14, max_step=0.01,
                    dense_output=True)
    return sol


lo, hi = 1.5, 30.0
for _ in range(200):
    mid = 0.5 * (lo + hi)
    s = shoot(mid)
    if s.t_events[0].size and (not s.t_events[1].size or s.t_events[0][0] < s.t_events[1][0]):
        hi = mid      # overshoot (crosses zero)
    else:
        lo = mid
p0 = 0.5 * (lo + hi)
s = shoot(lo)
r = s.t
y0, y1 = s.y
cut = len(r)
Sb = 2 * math.pi ** 2 * np.trapezoid(r[:cut] ** 3 * (0.5 * y1[:cut] ** 2 + 0.5 * y0[:cut] ** 2 - y0[:cut] ** 3 / 3.0), r[:cut])
res["bounce_phi0"] = p0
res["bounce_S0"] = float(Sb)

# (4) consequences
S0 = float(Sb)
cons = {}
c3 = res["max_unit_|Tr(J^ O^3)|"]
for a2 in (0.1, 1.0):
    for m in (1e3, 3e3):
        A = 3 * a2 * 1e16 * c3          # V(t) = m^2 t^2/2 + a2 w_BL c3 t^3 (w_BL ~ 1e16) -> A = 3 a2 w_BL c3
        cons[f"TeV octet m={m:.0e} a2={a2}: S"] = S0 * m ** 2 / A ** 2
for m in (1.7e9,):
    for mu in (1e15, 1e16):
        cons[f"(8,3,0) m={m:.1e} cubic {mu:.0e}: S (order)"] = S0 * m ** 2 / mu ** 2
cons["A_max for S >= 400 (units of m)"] = math.sqrt(S0 / 400.0)
cons["required tuning TeV octet (A/M_U)"] = math.sqrt(S0 / 400.0) * 1e3 / 1e16
cons["required tuning (8,3,0) (A/M_U)"] = math.sqrt(S0 / 400.0) * 1.7e9 / 1e16
res["consequences"] = cons
res["checks"] = {k: float(v) for k, v in checks.items()}
print(json.dumps(res, indent=1))
(HERE / "sk_d3_octet.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
