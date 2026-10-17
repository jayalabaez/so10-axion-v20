#!/usr/bin/env python3
"""Continuation patch of REPORT.txt (2026-10-17): amend section 0/3/14/15/16, append section 17."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "REPORT.txt")
s = io.open(P, encoding="utf-8", newline=None).read()


def rep(old, new):
    global s
    if old not in s:
        raise SystemExit("pattern not found: " + old[:80])
    s = s.replace(old, new, 1)


rep("v21-F17-B63-G3221 -- REPORT (2026-10-16)",
    "v21-F17-B63-G3221 -- REPORT (2026-10-16; continued 2026-10-17, section 17)")

rep("""  normalisation its nominal tau = 2.38e34 yr is 0.99 x the bound (knife edge) and only 49% of the scan passes; with
  the only REALISABLE GUT spectrum available (the explicit K3 vacuum points P831/P831b, transplanted, section 6) it
  fails by a factor 1.7-9 (tau = 2.7e33-1.4e34 yr).  So "not FAIL" rests on C2's nominal point in the repository
  normalisation and on the declared x1/2..x2 window.""",
    """  normalisation its nominal tau = 2.38e34 yr is 0.99 x the bound (knife edge) and only 49% of the scan passes; with
  the K3 C0-vacuum spectrum P831/P831b transplanted (EST, section 6) it fails by a factor 1.7-9, BUT with the first
  explicit C2-family spectra at Am45 (R2-A's in-progress stage-A LP points, recomputed and threshold-evaluated
  independently here, section 17a) it passes in the repository normalisation (tau = 7.5e34-1.6e35 yr, Lambda_2L =
  4.8-6.1, Lambda_3L = 1.8-2.4 M_Pl) and straddles the bound in the direct one (1.7e34-3.6e34 yr), v_R = 3.1e10-1.5e11.
  Those points are not BFB-complete vacua.  So "not FAIL" rests on C2 (nominal point and explicit C2-family spectra,
  repository normalisation); "not PASS" on the 13.5% / 51% threshold-scan failures and the unresolved normalisation.""")

rep("""  (M1) an explicit C2 (or C1', or rescue-content) vacuum point of the v20 potential and its heavy spectrum, run through
       the threshold code (r2b_p831.py does this in 2 s per point): the declared x1/2..x2 window vs the P831-type
       spectrum (states at 0.10-0.3 M_X) decides C2;""",
    """  (M1) an explicit, BFB-complete C2 (or C1', or rescue-content) VACUUM of the v20 potential (lambda_eff = lambda_SM,
       no deeper minimum found) and its heavy spectrum, run through the threshold code (r2b_r2a_c2check.py, 2 s per
       point); the stage-A C2-family spectra of section 17a pass (repo) / straddle (direct) -- the final vacuum decides;""")

rep("""be read (no WebFetch; the searches returned no text of them): the sign is therefore EXACT-conditional on (i), (ii).""",
    """be read (no WebFetch; the searches returned no text of them): the sign is therefore EXACT-conditional on (i), (ii).
[Continuation 2026-10-17: a direct one-loop derivation that does not use (i), (ii) gives the same sign (section 17b);
the label is upgraded to EXACT (derivation); the primary texts are still not read.]""")

rep("""the one-loop analytic (A, B) structure; the sign of the MS-bar constant GIVEN facts (i), (ii) of section 3.""",
    """the one-loop analytic (A, B) structure; the sign of the MS-bar constant (section 3, direct derivation section 17b).""")

rep("""1. (decisive) An explicit coupling point realising C2 (and/or C1', C1 + (8,1,3)_0, C1 + (6,2,2)_{2/3}) at a one-step
   G3221 vacuum of the v20 potential, with its full heavy spectrum fed to r2b_p831.py-style thresholds (R2-A).""",
    """1. (decisive) An explicit coupling point realising C2 (and/or C1', C1 + (8,1,3)_0, C1 + (6,2,2)_{2/3}) at a one-step
   G3221 vacuum of the v20 potential, with its full heavy spectrum fed to r2b_p831.py-style thresholds (R2-A).
   Partly addressed (section 17a): stage-A C2-family spectra at Am45 give tau = 7.5e34-1.6e35 (repo) / 1.7e34-3.6e34
   (direct); still missing: a BFB-complete, lambda_SM-matched C2 vacuum with no deeper minimum, and its spectrum.""")

rep("""5. The primary-text confirmation of the MS-bar constant sign (Weinberg 1980 / Hall 1981 / BDM 0912.1796).""",
    """5. The primary-text confirmation of the MS-bar constant sign (Weinberg 1980 / Hall 1981 / BDM 0912.1796); the sign
   itself is now derived directly (section 17b), so this is a citation check, not an open physics question.""")

rep("""Checkout status at the end: _g6_nogo 0 lines (54a2cd1), _record 0 lines (8707fda).""",
    """Continuation files (2026-10-17): r2b_r2a_c2check.py (+ r2b_r2a_c2check.json, r2a_c2check.out), validate_rerun.out,
r2b_validate_prev.json (previous validation output kept for the comparison), _patch3_report.py (this report patch).
Checkout status at the end: _g6_nogo 0 lines (54a2cd1), _record 0 lines (8707fda) -- re-checked 2026-10-17.""")

SEC17 = """
17. CONTINUATION (2026-10-17): EXPLICIT C2-FAMILY SPECTRA, DIRECT S_V DERIVATION, CROSS-GATE STATUS, HOUSEKEEPING
-------------------------------------------------------------------------------------------------------------------
17a. Explicit C2-family GUT spectra at Am45 [NUM for the given spectra; EST as a statement about 'the C2 vacuum']
R2-A (parallel round-2 gate, folder ..\\R2-A-vacuum-two-bidoublets, read only, files of 2026-10-16/17, in progress) has
coupling points of the v20 potential at the Am45 G3221 point with exactly the C2 light content: S5_Am45_C2 and
L5_Am45_C2_loc (heavy gap t = 0.01276) and L_Am45_C2_d6 (t = 0.00596); exact stationarity (|grad| <= 3e-14), Hessian
35 zero / 0 negative / 20 light / 431 heavy, singlet-channel |a0| <= 0.5.  They are heavy-gap-maximising (stage-A) LP
points WITHOUT BFB/competitor cuts: lambda_direct = -1 for S5/L5 (not bounded below along the neutral H ray) and +0.34
for d6, lambda_eff = -9.4 to -347 (not the SM value).  They are spectra of the C2 family, not vacua.
r2b_r2a_c2check.py recomputes the 451 non-Goldstone modes from K3's Am45 reduced Hessians (same chart point: all 21
compared blocks agree with R2-A's stored eigenvalues to <= 1e-16), assigns all 22 heavy G3221 multiplets with this
gate's routine (no unassigned multiplet), and solves the B63 chain with those thresholds (g_U iterated, MS-bar S_V,
M_s = 1e13, Phi pair 1e17, c = 0):
   point / variant          heavy m/M_X  loops  v_R       M_U       aU^-1  tau_repo  tau_dir   L2/MPl  L3/MPl
   S5_Am45_C2               0.28-1.25    1L     1.29e10   1.59e16   31.84  4.3e36    9.5e35    -       -
                                         2L     3.05e10   6.96e15   32.17  1.63e35   3.61e34   6.13    2.36
     S_V opposite / off                  2L     2.77e10 / 2.91e10   6.38e15 / 6.66e15     1.13e35 / 1.36e35  (dir 2.50e34 / 3.00e34)
     whole spectrum x1/2                 2L     3.14e10   8.05e15   29.71  2.49e35   5.49e34   2.78
     whole spectrum x2                   2L     2.96e10   6.03e15   34.61  1.06e35   2.35e34   13.98
   L5_Am45_C2_loc           0.28-1.11    2L     3.08e10   6.90e15   32.17  1.58e35   3.49e34   6.11    2.35
   L_Am45_C2_d6             0.19-1.47    2L     1.53e11   5.76e15   31.92  7.52e34   1.66e34   4.76    1.83
     S_V opposite                        2L     1.39e11   5.27e15   31.68  5.21e34   1.15e34   4.04
(The S5_Am45_C2 row equals the numbers R2-A obtained by running this gate's code, thr_S5_C2.json.)
Lightest heavy multiplets (S5): 126bar (3,1,1)_{-2/3}, (3b,1,1)_{2/3}, (3,2,2)_{4/3}, Delta_L (1,3,1)_{-2}, 210 (8,3,1)_0
and (8,1,1)_0 all at m = 0.113 |Phi| = 0.28 M_X; heaviest 10 (3b,1,1) at 1.25 M_X; geometric mean 0.50 M_X.
Reading: with actual C2-family spectra at Am45 the C2 content passes Super-K in the repository normalisation
(tau = 7.5e34-1.6e35 yr, margin x3-7, also with the opposite S_V sign) with Lambda_2L = 4.8-6.1 and Lambda_3L = 1.8-2.4
M_Pl,red; in the direct-lattice normalisation it straddles the bound (3.5e34-3.6e34 for the two t = 0.0128 points,
1.66e34 for d6).  v_R = 3.1e10 (S5/L5) and 1.5e11 (d6): the d6 spectrum is the first case found with tau (repo),
Landau AND v_R >= 1e11 together.  For C2 this supersedes the P831-transplant estimate of section 6 (EST; fails by
1.7-9): the C2-family spectra are also lighter than M_X (min 0.19-0.28 M_X, like P831's 0.10-0.14) but distributed
differently.  R2-A's angle scan of C2 at other 210 orientations (thr_S5_C2.json; not the Am45 configuration; R2-A's
numbers) gives tau = 1.7e32-8e34 (repo): Am45 is among the most favourable orientations.
Caveat: none of these points is BFB-complete, matched to lambda_SM, or screened for deeper minima; imposing those
constraints will move the tuned couplings and the heavy spectrum (in K3's C0 case the step stage A -> P831 halved the
lightest heavy m^2).  The independent threshold MC of section 5 (13.5% of C2 samples below Super-K in the repository
normalisation) quantifies how much such a spectrum shift can matter.

17b. MS-bar heavy-vector constant: direct derivation of the sign [EXACT derivation; primary texts not read]
One loop, background-field Feynman gauge, heavy vector V of mass M with its ghosts and its eaten Goldstone (all of mass
M).  Per unit index T_i(V) the heat-kernel coefficient of the background F^2 term is (d/12 - 2/12 - 2) for vector +
ghosts and +1/12 for the Goldstone, multiplying Gamma(eps) (4 pi mu^2/M^2)^eps with d = 4 - 2 eps.  d/12 is the
diamagnetic contribution of the d vector components and is the ONLY d-dependent piece (the spin term
tr_Lorentz(J^{rs} J^{kl}) gives the d-independent -2; the two ghosts give -2/12).  Writing the bracket as A + B eps
(vector + ghosts: A = -11/6, B = -1/6) and removing the MS-bar pole leaves the finite part -2 A ln(M/mu) + B.  Normalised
to the real scalar (A = 1/12, B = 0), which must reproduce the decoupling log lambda_S = +ln(M/mu) in
alpha_low^-1 = alpha_high^-1 - lambda/(12 pi), lambda = -6 x (finite part): vector + ghosts -22 ln(M/mu) + 1, Goldstone
+ln(M/mu), i.e. lambda_V = T_i(V) [1 - 21 ln(M_V/mu)] (the Weinberg-Hall form, b-check: -21/6 = -11/3 + 1/6).  Hence at
mu = M_V: alpha_i^-1(low) = alpha_G^-1(high) - S_V,i/(12 pi), the sign used throughout (code sv_sign = +1; U(1)_Y at v_R:
-(6/5)/(12 pi)).  In DR-bar the vector keeps four components (B = 0) and the constant vanishes, which is facts (i), (ii)
of section 3; the MS-bar/DR-bar offset C_i/(12 pi) was confirmed in this session at search-snippet level (LIT-snippet;
results list incl. hep-ph/9503214, hep-ph/9210235).  The opposite sign (round-1 physics skeptic: 'MS-bar has no
constant') contradicts this derivation; it stays in the tables only as a systematic (-31% on tau relative to the MS-bar sign; "off": -17%).

17c. Cross-gate status seen today (read only, in progress; NOT used for the verdict)
* R2-C (two-bidoublet 10 + 126bar flavour fits, src/campaign_main_*_I.log): best chi2 = 163-177 for v_R = 1e11-1e14
  (163 at 1e11, 177 at 1e14) -- still far from viable; v_R ~ 3e10 (C2's nominal region) is not in its grid.
* R2-A also tests the rescue contents C1 + (8,1,3)_0 and C1 + (6,2,2)_{2/3} (files S5_*_C1813, S5_*_C1622): several
  C1 + (6,2,2) points have LP gaps t ~ 1e-6-1e-7 with 200-450 light modes (collapse-type); its threshold runs of this
  gate's code (thr_S5_C1622.json, Am45 and D470) give tau = 3e36-1.6e37 yr but Lambda_3L = 0.56-0.59 M_Pl and
  Lambda_2L = 1.25-1.28 (1.07-1.10 with the opposite S_V sign), i.e. the Landau test becomes the binding one there.

17d. Housekeeping (honest record)
At the start of this continuation I copied K1's k1_lib.py over this folder's r2b_lib.py (which carried the _patch1.py
event_index change) and then deleted it together with k1_model_ref.py.  r2b_lib.py was rebuilt as k1_lib.py + _patch1.py
(the r2b_model.py part of that patch is idempotent: r2b_model.py byte-identical before/after), and k1_model_ref.py was
re-copied from round 1 (no script imports it).  r2b_validate.py was re-run: every number in r2b_validate.json equals the
previous run (kept as r2b_validate_prev.json) to 1e-9 relative, so all earlier results stand.  The C2 nominal point
(v_R = 2.130e10, M_U = 6.052e15, aU^-1 = 34.63, tau = 1.082e35, L2 = 14.16, L3 = 5.20) is also reproduced by the round-2
skeptic's independent code (skeptic/sk_checks.log; its 400-sample MC: pass fraction C2 87.8% repo / 51% direct, C1' 23%,
C0 15%, C1 0.25%, consistent with section 5).  baseline_git_status.txt was rewritten today (2026-10-17 baseline: 0 lines
in _g6_nogo 54a2cd1 and in _record 8707fda).  _rescope was not touched.

17e. Updated reading of the criterion: UNDECIDED (unchanged)
Not FAIL: C2 (flavour-capable) has two-loop solutions with tau > 2.4e34 yr and Lambda_2L > M_Pl,red at its nominal
point and with the explicit C2-family spectra at Am45 (repository normalisation).  Not PASS: under the declared threshold
scan 13.5% (repository) / 51% (direct) of the C2 samples fail Super-K; the explicit spectra are not vacua; the hadronic
normalisation (factor 4.53) decides C2's status in the direct normalisation.  C1 fails (factor 14 at nominal, 0.5% of
the scan), C1' fails nominally (factor 2.8; 20% of the scan), C0 (reference) fails (factor 3.9).  Item (e) stays
adverse for C2: v_R = 2e10-3e10 (1.5e11 only for the d6 spectrum), below the 1e11-1e14 seesaw window.
"""
s = s.rstrip("\n") + "\n" + SEC17
io.open(P, "w", encoding="utf-8", newline="\r\n").write(s)
print("patched", len(s.splitlines()), "lines")
