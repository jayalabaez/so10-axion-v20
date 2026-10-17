"""One-off patch: v2 fixes on top of the copied first-attempt code (run once from the v2 folder).
 (1) B63 S-sector at M_s = 3 x (16+16bar) + 2 x 10_F (T_S = 14 -> universal SM shift 28/3); the Phi17 pair sits at
     M_Phi ~ 1e17 > M_U (R2-B convention) and is NOT in the G3221/SM running.  (First attempt used 4 pairs: shift 12.)
 (2) Content names aligned with R2-B: C1 = 2 bid + (8,3,1)_0 + Delta_R, C2 = 2 bid + Delta_R, C1p = 2 bid + (1,3,1)_0
     + Delta_R, R813 = C1 + (8,1,3)_0 (real), R622 = C1 + (6,2,2)_{B-L=2/3} (complex).
 (3) M_U per content from the R2-B two-loop nominal solutions (REPORT section 4 / 12).
 (4) Exact model: perturbativity penalty |Y_act| <= 1.5 (Y10, Y126 at M_U and v_R) as 2 extra residuals.
"""
import re, io

def sub(path, old, new, count=1):
    s = open(path, encoding="utf-8").read()
    n = s.count(old)
    if n != count:
        raise SystemExit(f"{path}: expected {count} occurrence(s) of {old[:60]!r}, found {n}")
    s = s.replace(old, new)
    open(path, "w", encoding="utf-8").write(s)

# ---- lib_r2c.py ----
sub("lib_r2c.py",
    '''SCAL = {"bid": b_rep(1, 2, 2, 0, "cplx"), "DR": b_rep(1, 1, 3, 1, "cplx"), "831": b_rep(8, 3, 1, 0, "real"),
        "822": b_rep(8, 2, 2, 0, "cplx"), "131": b_rep(1, 3, 1, 0, "real"), "811": b_rep(8, 1, 1, 0, "real")}
CONTENTS = {
    "C2": ["bid", "bid", "DR", "831"],            # two light bidoublets + (8,3,1)_0 + Delta_R  (R2 default)
    "C2m": ["bid", "bid", "DR"],                  # without the colour octet (RG-robustness variant)
    "T3": ["bid", "bid", "DR", "831", "822", "131", "811"],
}''',
    '''SCAL = {"bid": b_rep(1, 2, 2, 0, "cplx"), "DR": b_rep(1, 1, 3, 1, "cplx"), "831": b_rep(8, 3, 1, 0, "real"),
        "822": b_rep(8, 2, 2, 0, "cplx"), "131": b_rep(1, 3, 1, 0, "real"), "811": b_rep(8, 1, 1, 0, "real"),
        "813": b_rep(8, 1, 3, 0, "real"), "622": b_rep(6, 2, 2, Fr(1, 3), "cplx"),
        "DL": b_rep(1, 3, 1, 1, "cplx")}
# v2: names as in R2-B (REPORT section 2); q = (B-L)/2, so (6,2,2)_{B-L=2/3} has q = 1/3, Delta_R/L q = 1
CONTENTS = {
    "C1": ["bid", "bid", "831", "DR"],            # R2-B C1: both bidoublets + (8,3,1)_0 + Delta_R
    "C2": ["bid", "bid", "DR"],                   # R2-B C2: both bidoublets + Delta_R
    "C1p": ["bid", "bid", "131", "DR"],           # R2-B C1': both bidoublets + (1,3,1)_0 + Delta_R
    "R813": ["bid", "bid", "831", "DR", "813"],   # R2-B rescue C1 + (8,1,3)_0
    "R622": ["bid", "bid", "831", "DR", "622"],   # R2-B rescue C1 + (6,2,2)_{2/3}
    "C2DL": ["bid", "bid", "DR", "DL"],           # C2 + a light Delta_L (only for the type-II realisability note)
}
# R2-B two-loop nominal solutions (v_R, M_U) [R2-B REPORT sections 4 and 12; MS-bar heavy-vector constant]
R2B_NOMINAL = {"C1": (7.78e12, 2.18e15), "C2": (2.13e10, 6.05e15), "C1p": (1.14e11, 3.20e15),
               "R813": (2.7e11, 2.4e16), "R622": (9.5e12, 1.9e16)}''')
sub("lib_r2c.py",
    '''    if s_sector:      # B63: 4 x (16 + 16bar) [3 conj-S pairs + 1 Phi17 pair] + 2 x 10_F
        rows += [ONE16] * 8 + [ONE10] * 2''',
    '''    if s_sector:      # v2: B63 at M_s = 3 x (16 + 16bar) [conj-S pairs] + 2 x 10_F (T_S = 14); Phi17 pair at ~1e17
        rows += [ONE16] * 6 + [ONE10] * 2''')
sub("lib_r2c.py",
    '''B63_SM_SHIFT = 12.0     # complete SO(10) multiplets 4 x (16+16bar) + 2 x 10 (Weyl): +12 to each SM b_i above M_s''',
    '''B63_SM_SHIFT = 28.0 / 3  # v2: 3 x (16+16bar) + 2 x 10 (Weyl), T_S = 14: +(2/3) T_S = 28/3 to each SM b_i above M_s''')

# ---- bexact.py: perturbativity penalty + stored Yukawa maxima ----
sub("bexact.py",
    '''        self.h_g = h_g; self.h_sm = h_sm; self.nev = 0
        self.mask = None''',
    '''        self.h_g = h_g; self.h_sm = h_sm; self.nev = 0
        self.mask = None
        self.ypert = 1.5          # v2: |Y_act| bound (Y10_act = Y10_def/(2 sqrt2), Y126_act = (sqrt3/4) Y126_def)
        self.wpert = 100.0        # residual = wpert * max(0, max|Y_act|/ypert - 1)  (1% excess -> chi2 + 1)
        self.last_ymax = None''')
sub("bexact.py",
    '''            s = run_g3221_b(s, env["MU"], vR, env["b_lo"], env["b_hi"], self.h_g)
            gq, Yq0, Yq1, Yl0, Yl1, fh = s''',
    '''            y10U = np.abs(Y10).reshape(N, -1).max(1) * L.Y10_ACT
            y126U = np.abs(Y126).reshape(N, -1).max(1) * L.Y126_ACT
            s = run_g3221_b(s, env["MU"], vR, env["b_lo"], env["b_hi"], self.h_g)
            gq, Yq0, Yq1, Yl0, Yl1, fh = s
            y10R = np.abs(Yq0).reshape(N, -1).max(1) * L.Y10_ACT
            y126R = np.abs(Yq1).reshape(N, -1).max(1) * L.Y126_ACT
            self.last_ymax = np.stack([np.maximum(y10U, y10R), np.maximum(y126U, y126R)], 1)''')
sub("bexact.py",
    '''        R[o[:, 17] <= 0] += 1e3
        R = np.where(np.isfinite(R), R, 1e3)
        R[~fin] = 1e3
        if self.mask is not None:
            R = R * (~self.mask)
        return R''',
    '''        R[o[:, 17] <= 0] += 1e3
        R = np.where(np.isfinite(R), R, 1e3)
        R[~fin] = 1e3
        if self.mask is not None:
            R = R * (~self.mask)
        ym = np.where(np.isfinite(self.last_ymax), self.last_ymax, 1e3)
        P = self.wpert * np.clip(ym / self.ypert - 1.0, 0, None)
        return np.concatenate([R, P], 1)''')
print("patched")
