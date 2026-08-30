(* V24 Kawamura--Raby SUSY Pati--Salam source contract. *)
(* Source architecture: arXiv:2009.04582; derived Z4^R x Z11 selector. *)
(* Z4^R is verified independently because W carries R charge 2.       *)
Off[General::spell];

Model`Name = "PSZ4RZ11SUSYV24";
Model`NameLaTeX = "V24 SUSY Pati-Salam Z_4^R x Z_11 source";
Model`Authors = "V24 source reconstruction after Kawamura--Raby";
Model`Date = "2026-08-20";

Global[[1]] = {Z[11], Z11Selector};
Z11q0 = 1;
Z11q1 = Exp[2*Pi*I/11];
Z11q10 = Exp[20*Pi*I/11];

Gauge[[1]] = {GC, SU[4], color4, g4, False, Z11q0};
Gauge[[2]] = {GL, SU[2], left,   gL, True,  Z11q0};
Gauge[[3]] = {GR, SU[2], right,  gR, True,  Z11q0};

SuperFields[[1]]  = {H,        1, h,      1,  2, 2, Z11q0};
SuperFields[[2]]  = {Q,        3, q,      4,  2, 1, Z11q0};
SuperFields[[3]]  = {Qc,       3, qc,    -4,  1, 2, Z11q0};
SuperFields[[4]]  = {X,        1, sx,     1,  1, 1, Z11q0};
SuperFields[[5]]  = {Sc,       1, sc,    -4,  1, 2, Z11q0};
SuperFields[[6]]  = {Sbc,      1, sbc,    4,  1, 2, Z11q0};
(* Sig6 avoids collision with SARAH's protected Pauli-matrix symbol Sigma. *)
SuperFields[[7]]  = {Sig6,     1, sig6,   6,  1, 1, Z11q0};
SuperFields[[8]]  = {PsiBar,   1, psib,  -4,  2, 1, Z11q10};
SuperFields[[9]]  = {Psi,      1, psi,    4,  2, 1, Z11q0};
SuperFields[[10]] = {PsiC,     1, psic,  -4,  1, 2, Z11q0};
SuperFields[[11]] = {PsiCBar,  1, psicb,  4,  1, 2, Z11q10};
SuperFields[[12]] = {P,        1, p,      1,  1, 1, Z11q1};
SuperFields[[13]] = {Nv,       3, nv,     1,  1, 1, Z11q0};

(* Independent additive charges; every term below sums to 2 modulo 4. *)
V24Z4RCharges = {
  {H,0}, {Q,1}, {Qc,1}, {X,2}, {Sc,0}, {Sbc,0},
  {Sig6,2}, {PsiBar,3}, {Psi,1}, {PsiC,1},
  {PsiCBar,3}, {P,2}, {Nv,1}
};

(* Symmetry-complete renormalizable W.  X.H.H, X.Sig6.Sig6 and all *)
(* fourth-family/PQ mixings are required by Z4^R x Z11, even though the *)
(* paper writes the leading source schematically.                         *)
SuperPotential = (-kappaPS*vPS2*X
 + kappaPS*X.Sbc.Sc + kappaX/3*X.X.X
 + lambdaH/2*X.H.H + lambdaSigma/2*X.Sig6.Sig6
 + lambdaS/2*Sc.Sc.Sig6 + lambdaSb/2*Sbc.Sbc.Sig6
 + YQQ*Q.H.Qc + YQX*Q.H.PsiC + YXQ*Psi.H.Qc + YXX*Psi.H.PsiC
 + lambdaPQ*P.PsiBar.Q + lambdaPX*P.PsiBar.Psi
 + lambdaPcQ*P.PsiCBar.Qc + lambdaPcX*P.PsiCBar.PsiC
 + yNQ*Sbc.Qc.Nv + yNX*Sbc.PsiC.Nv + MN/2*Nv.Nv);

(* This source attests the exact supersymmetric theory.  Soft/PQ-vacuum *)
(* construction is a separate, explicitly open matching stage.          *)
AddSoftTerms = False;
AddSoftScalarMasses = False;
AddSoftGauginoMasses = False;

NameOfStates = {GaugeES};

V24SourceBoundary = {
  "DiscreteRCheckedOutsideSARAH",
  "Z11EncodedInSARAH",
  "NonzeroSuperPotential",
  "EFTMajoranaUVCompletedByNv",
  "GSTopologicalTermIsExternalToSARAH",
  "NoFullG1G2ClosureClaim"
};
