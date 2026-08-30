(* V33 anomaly-compatible Z33 EFT repair of the V24 SUSY Pati--Salam source. *)
(* The continuous field content and 18 renormalizable W terms are unchanged.  *)
Off[General::spell];

Model`Name = "PSZ4RZ33SUSYV33";
Model`NameLaTeX = "V33 SUSY Pati-Salam Z_4^R x Z_33 EFT";
Model`Authors = "V33 derivation campaign after Kawamura--Raby";
Model`Date = "2026-08-24";

Global[[1]] = {Z[33], Z33Selector};
Z33q0 = 1;
Z33q1 = Exp[2*Pi*I/33];
Z33q32 = Exp[64*Pi*I/33];

Gauge[[1]] = {GC, SU[4], color4, g4, False, Z33q0};
Gauge[[2]] = {GL, SU[2], left,   gL, True,  Z33q0};
Gauge[[3]] = {GR, SU[2], right,  gR, True,  Z33q0};

SuperFields[[1]]  = {H,        1, h,      1,  2, 2, Z33q0};
SuperFields[[2]]  = {Q,        3, q,      4,  2, 1, Z33q0};
SuperFields[[3]]  = {Qc,       3, qc,    -4,  1, 2, Z33q0};
SuperFields[[4]]  = {X,        1, sx,     1,  1, 1, Z33q0};
SuperFields[[5]]  = {Sc,       1, sc,    -4,  1, 2, Z33q0};
SuperFields[[6]]  = {Sbc,      1, sbc,    4,  1, 2, Z33q0};
SuperFields[[7]]  = {Sig6,     1, sig6,   6,  1, 1, Z33q0};
SuperFields[[8]]  = {PsiBar,   1, psib,  -4,  2, 1, Z33q32};
SuperFields[[9]]  = {Psi,      1, psi,    4,  2, 1, Z33q0};
SuperFields[[10]] = {PsiC,     1, psic,  -4,  1, 2, Z33q0};
SuperFields[[11]] = {PsiCBar,  1, psicb,  4,  1, 2, Z33q32};
SuperFields[[12]] = {P,        1, p,      1,  1, 1, Z33q1};
SuperFields[[13]] = {Nv,       3, nv,     1,  1, 1, Z33q0};

(* Checked independently: each term has Z4R charge 2 and Z33 charge zero. *)
V33Z4RCharges = {
  {H,0}, {Q,1}, {Qc,1}, {X,2}, {Sc,0}, {Sbc,0},
  {Sig6,2}, {PsiBar,3}, {Psi,1}, {PsiC,1},
  {PsiCBar,3}, {P,2}, {Nv,1}
};

SuperPotential = (-kappaPS*vPS2*X
 + kappaPS*X.Sbc.Sc + kappaX/3*X.X.X
 + lambdaH/2*X.H.H + lambdaSigma/2*X.Sig6.Sig6
 + lambdaS/2*Sc.Sc.Sig6 + lambdaSb/2*Sbc.Sbc.Sig6
 + YQQ*Q.H.Qc + YQX*Q.H.PsiC + YXQ*Psi.H.Qc + YXX*Psi.H.PsiC
 + lambdaPQ*P.PsiBar.Q + lambdaPX*P.PsiBar.Psi
 + lambdaPcQ*P.PsiCBar.Qc + lambdaPcX*P.PsiCBar.PsiC
 + yNQ*Sbc.Qc.Nv + yNX*Sbc.PsiC.Nv + MN/2*Nv.Nv);

(* The EFT admits higher symmetry-allowed operators; it does not assert FCMA-18. *)
AddSoftTerms = False;
AddSoftScalarMasses = False;
AddSoftGauginoMasses = False;

NameOfStates = {GaugeES};

V33SourceBoundary = {
  "DiscreteRCheckedOutsideSARAH",
  "Z33EncodedInSARAH",
  "Exact18RenormalizableTerms",
  "HigherWilsonianTowerAccepted",
  "NoMicroscopicOrFullGateClaim"
};
