(* V36 pure-finite-repaired, conditional-topological redesign of the V35 PS EFT. *)
Off[General::spell];

Model`Name = "PSZ4RZ66SUSYV36";
Model`NameLaTeX = "V36 Z_{66}-selected SUSY Pati-Salam EFT";
Model`Authors = "V36 redesign after the V34/V35 fail-closed audits";
Model`Date = "2026-08-25";

(*
  Z66 is the CRT combination of the old Z33 selector and anomalon parity.
  Its charge is s=2 q33+33 p (mod 66).  P and Pb have even charges, so
  their VEVs leave the anomalon-odd residual Z2 unbroken.
*)
Global[[1]] = {Z[66], Z66Selector};
Z66q0  = 1;
Z66q1  = Exp[2*Pi*I/66];
Z66q2  = Exp[4*Pi*I/66];
Z66q31 = Exp[62*Pi*I/66];
Z66q37 = Exp[74*Pi*I/66];
Z66q63 = Exp[126*Pi*I/66];
Z66q64 = Exp[128*Pi*I/66];
Z66q65 = Exp[130*Pi*I/66];

Gauge[[1]] = {GC, SU[4], color4, g4, False, Z66q0};
Gauge[[2]] = {GL, SU[2], left,   gL, True,  Z66q0};
Gauge[[3]] = {GR, SU[2], right,  gR, True,  Z66q0};

SuperFields[[1]]  = {H,        1, h,      1,  2, 2, Z66q0};
SuperFields[[2]]  = {Q,        3, q,      4,  2, 1, Z66q0};
SuperFields[[3]]  = {Qc,       3, qc,    -4,  1, 2, Z66q0};
SuperFields[[4]]  = {X,        1, sx,     1,  1, 1, Z66q0};
SuperFields[[5]]  = {Sc,       1, sc,    -4,  1, 2, Z66q0};
SuperFields[[6]]  = {Sbc,      1, sbc,    4,  1, 2, Z66q0};
SuperFields[[7]]  = {Sig6,     1, sig6,   6,  1, 1, Z66q0};
SuperFields[[8]]  = {PsiBar,   1, psib,  -4,  2, 1, Z66q64};
SuperFields[[9]]  = {Psi,      1, psi,    4,  2, 1, Z66q0};
SuperFields[[10]] = {PsiC,     1, psic,  -4,  1, 2, Z66q0};
SuperFields[[11]] = {PsiCBar,  1, psicb,  4,  1, 2, Z66q64};
SuperFields[[12]] = {P,        1, p,      1,  1, 1, Z66q2};
SuperFields[[13]] = {Nv,       3, nv,     1,  1, 1, Z66q0};

(* New anomaly-finite PQ and driver sector. *)
SuperFields[[14]] = {Pb,       1, pb,     1,  1, 1, Z66q64};
SuperFields[[15]] = {Zp,       1, szp,    1,  1, 1, Z66q0};
SuperFields[[16]] = {A2,       1, a2,     1,  1, 1, Z66q37};
SuperFields[[17]] = {A32,      1, a32,    1,  1, 1, Z66q31};
SuperFields[[18]] = {A15,      1, a15,    1,  1, 1, Z66q63};
SuperFields[[19]] = {A17,      1, a17,    1,  1, 1, Z66q1};
SuperFields[[20]] = {A16,      1, a16,    1,  1, 1, Z66q65};

(* External Z4R superfield charges; every displayed W term has charge 2. *)
V36Z4RCharges = {
  {H,0}, {Q,1}, {Qc,1}, {X,2}, {Sc,0}, {Sbc,0},
  {Sig6,2}, {PsiBar,3}, {Psi,1}, {PsiC,1},
  {PsiCBar,3}, {P,2}, {Nv,1}, {Pb,2}, {Zp,2},
  {A2,0}, {A32,0}, {A15,2}, {A17,2}, {A16,0}
};

(*
  The two neutral R=2 drivers span the complete renormalizable driver basis.
  The five anomalons have odd Z66 charge.  Consequently the dangerous bilinear
  P.A32 is absent while every required even-anomalon mass operator is retained.
*)
SuperPotential = (
 - (kappaPS*vPS2 + kappaPQ*fPQ2)*X
 - (rhoPS*vPS2 + rhoPQ*fPQ2)*Zp
 + kappaPS*X.Sbc.Sc + kappaPQ*X.P.Pb
 + rhoPS*Zp.Sbc.Sc + rhoPQ*Zp.P.Pb
 + kappaX/3*X.X.X + kappaXXZ/2*X.X.Zp
 + kappaXZZ/2*X.Zp.Zp + kappaZ/3*Zp.Zp.Zp
 + lambdaH/2*X.H.H + lambdaSigma/2*X.Sig6.Sig6
 + lambdaZH/2*Zp.H.H + lambdaZSigma/2*Zp.Sig6.Sig6
 + lambdaS/2*Sc.Sc.Sig6 + lambdaSb/2*Sbc.Sbc.Sig6
 + YQQ*Q.H.Qc + YQX*Q.H.PsiC + YXQ*Psi.H.Qc + YXX*Psi.H.PsiC
 + lambdaPQ*P.PsiBar.Q + lambdaPX*P.PsiBar.Psi
 + lambdaPcQ*P.PsiCBar.Qc + lambdaPcX*P.PsiCBar.PsiC
 + yNQ*Sbc.Qc.Nv + yNX*Sbc.PsiC.Nv + MN/2*Nv.Nv
 + yAbar*Pb.A2.A32 + yA15*P.A15.A17
 + yA16/2*P.A16.A16 + yA17/2*Pb.A17.A17
 + MA*A16.A17
);

AddSoftTerms = False;
AddSoftScalarMasses = False;
AddSoftGauginoMasses = False;

NameOfStates = {GaugeES};

V36SourceBoundary = {
  "ExactZ66PureFiniteCounterclass",
  "NonUniversalQuantizedGSTopologicalMultipletExternalToSARAH",
  "CompleteRenormalizableDriverAndAnomalonTerms",
  "NoChargedInstantonCoefficientSpurions",
  "NoMicroscopicCompactificationOrMediationClaim"
};
