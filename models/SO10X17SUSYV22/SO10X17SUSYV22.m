(* ==================================================================== *)
(* Candidate V22 supersymmetric continuation of gauged_u1x_phi17_v20.  *)
(* This file is a model-contract scaffold, not a closed G1-G5 artifact. *)
(* It keeps the v20 matter charges, adds anomaly-vectorlike Higgs chiral *)
(* multiplets, and uses Phi17p/Phi17m to break U(1)_X -> Z_17.          *)
(* ==================================================================== *)

Off[General::spell];

Model`Name = "SO10X17SUSYV22";
Model`NameLaTeX = "SUSY SO(10) x U(1)_X with residual Z_{17}, V22";
Model`Authors = "SO10 axion V22 continuation";
Model`Date = "2026-08-16";

Global[[1]] = {Z[2], RParity};
Global[[2]] = {Z[17], Z17};
Global[[3]] = {U[1], RSymmetry};
RpM = {-1, -1, 1};
RpP = {1, 1, -1};

Gauge[[1]] = {G10, SO[10], SOGUT, g10, False, RpM, 0, {0,1,0}};
Gauge[[2]] = {GX, U[1], xcharge, gX, False, RpM, 0, {0,1,0}};

(* Matter superfields: the anomaly-cancelling v20 chiral catalogue. *)
SuperFields[[1]] = {F,     3, f16,      16,   1, RpM, Exp[2*Pi*I*1/17],  {1,1,0}};
SuperFields[[2]] = {P,     1, p16,      16,   1, RpM, Exp[2*Pi*I*1/17],  {1,1,0}};
SuperFields[[3]] = {R,     1, r16,      16,   1, RpM, Exp[2*Pi*I*1/17],  {1,1,0}};
SuperFields[[4]] = {SpecS, 5, s16,      16,   2, RpM, Exp[2*Pi*I*2/17],  {1,1,0}};
SuperFields[[5]] = {SpecB, 5, b16bar,  -16,  -6, RpM, Exp[2*Pi*I*11/17], {1,1,0}};
SuperFields[[6]] = {Q,     1, q16,      16,  14, RpM, Exp[2*Pi*I*14/17], {1,1,0}};
SuperFields[[7]] = {Pbar,  1, pbar16,  -16,  16, RpM, Exp[2*Pi*I*16/17], {1,1,0}};
SuperFields[[8]] = {Qbar,  1, qbar16,  -16,   3, RpM, Exp[2*Pi*I*3/17],  {1,1,0}};
SuperFields[[9]] = {Rbar,  1, rbar16,  -16, -18, RpM, Exp[2*Pi*I*16/17], {1,1,0}};

(* Higgs superfields.  Every charged Higgsino has its anomaly-conjugate. *)
SuperFields[[10]] = {Phi210,  1, phi210,   210,   0, RpP, 1,                   {0,0,-1}};
SuperFields[[11]] = {DeltaB,  1, deltaB,  -126,  -2, RpP, Exp[2*Pi*I*15/17], {0,0,-1}};
SuperFields[[12]] = {Delta,   1, delta,     126,   2, RpP, Exp[2*Pi*I*2/17],  {2,2,1}};
SuperFields[[13]] = {DeltaB2, 1, deltaB2, -126,  -2, RpP, Exp[2*Pi*I*15/17], {2,2,1}};
SuperFields[[14]] = {Delta2,  1, delta2,    126,   2, RpP, Exp[2*Pi*I*2/17],  {0,0,-1}};
SuperFields[[15]] = {H10m,    1, h10m,       10,  -2, RpP, Exp[2*Pi*I*15/17], {0,0,-1}};
SuperFields[[16]] = {H10p,    1, h10p,       10,   2, RpP, Exp[2*Pi*I*2/17],  {0,0,-1}};
SuperFields[[17]] = {T120m,   1, t120m,     120,  -2, RpP, Exp[2*Pi*I*15/17], {0,0,-1}};
SuperFields[[18]] = {T120p,   1, t120p,     120,   2, RpP, Exp[2*Pi*I*2/17],  {0,0,-1}};
SuperFields[[19]] = {Splus,   1, splus,       1,   4, RpP, Exp[2*Pi*I*4/17],  {0,0,-1}};
SuperFields[[20]] = {Sminus,  1, sminus,      1,  -4, RpP, Exp[2*Pi*I*13/17], {0,0,-1}};
SuperFields[[21]] = {Phi17p,  1, phi17p,      1,  17, RpP, 1,                  {0,0,-1}};
SuperFields[[22]] = {Phi17m,  1, phi17m,      1, -17, RpP, 1,                  {0,0,-1}};
SuperFields[[23]] = {NX,      1, nx,           1,   0, RpP, 1,                  {2,2,1}};
SuperFields[[24]] = {NS,      1, ns,           1,   0, RpP, 1,                  {2,2,1}};
SuperFields[[25]] = {XMP,     1, xmp,          1,   0, RpP, 1,                  {0,0,-1}};
SuperFields[[26]] = {C16,     1, c16,         16,   0, RpP, 1,                  {0,0,-1}};
SuperFields[[27]] = {C16bar,  1, c16bar,     -16,   0, RpP, 1,                  {0,0,-1}};
SuperFields[[28]] = {Nphi,    1, nphi,         1,   0, RpP, 1,                  {2,2,1}};
SuperFields[[29]] = {Z0,      1, z0,           1,   0, RpP, 1,                  {0,0,-1}};
SuperFields[[30]] = {NC,      1, nc,           1,   0, RpP, 1,                  {2,2,1}};
SuperFields[[31]] = {NMP,     1, nmp,          1,   0, RpP, 1,                  {2,2,1}};
SuperFields[[32]] = {Z1,      1, z1,           1,   0, RpP, 1,                  {0,0,-1}};
SuperFields[[33]] = {Z2,      1, z2,           1,   0, RpP, 1,                  {0,0,-1}};

(* SARAH-runtime sentinel.  The high-representation contractions below are *)
(* independently tensor-certified before they may enter a canonical gate. *)
SuperPotential = kappaX NX.Phi17p.Phi17m + kappaS NS.Splus.Sminus
               + kappaMP NMP.XMP.XMP;

(* Intended superpotential catalogue; it is not complete under the       *)
(* currently declared symmetries.  The exact degree<=4 census and driver *)
(* shaping no-go are frozen as separate V22 G1 obstruction artifacts.    *)
(* Tensor-copy normalization and all component CGs remain V22 G1/G2 work. *)
SuperPotentialCatalogue =
    kappaPhi Nphi.(Phi210.Phi210 - vPhi2)
  + zetaPhi Nphi.Phi210.Phi210.Phi210/Mstar
  + kappaC NC.(C16bar.C16 - vC2)
  + xiC NC.C16bar.Phi210.C16/Mstar
  + kappaMP NMP.(XMP.XMP - vMP2)
  + rho1 XMP.DeltaB.Delta
  + rho2 XMP.DeltaB2.Delta2
  + gammaH Phi210.H10m.Delta
  + gammaHb2 Phi210.H10p.DeltaB2
  + gammaT Phi210.T120m.Delta
  + gammaTb2 Phi210.T120p.DeltaB2
  + kappaX NX.(Phi17p.Phi17m - vX2)
  + kappaS NS.(Splus.Sminus - vS2)
  + Y10 F.F.H10m
  + Y120 F.F.T120m
  + Y126eff XMP.F.F.DeltaB/Mstar
  + yP Phi17m.P.Pbar
  + yQ Phi17m.Q.Qbar
  + yR Phi17p.R.Rbar
  + ys Splus.SpecS.SpecB
  + lambdaP P.F.H10m
  + lambdaR R.F.H10m
  + lambdaQB Sminus.Qbar.F
  + lambdaQR Splus.Q.Rbar;

NameOfStates = {GaugeES};
