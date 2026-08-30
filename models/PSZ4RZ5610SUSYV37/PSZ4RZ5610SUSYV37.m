(* V37 axion-quality redesign of the V36 SUSY Pati--Salam EFT. *)
Off[General::spell];

Model`Name = "PSZ4RZ5610SUSYV37";
Model`NameLaTeX = "V37 Z_{5610}-selected SUSY Pati-Salam EFT";
Model`Authors = "V37 fail-closed quality redesign";
Model`Date = "2026-08-25";

(*
  Z5610 is the faithful cyclic presentation of Z66 x Z85.  The Z85
  spectator charges are (A2,A32,A15,A17,A16)=(1,-1,69,-69,0).
  A field with charges (q66,h85) has

      q5610 = 85 q66 + 66 h85  (mod 5610).

  The spectator is pairwise anomaly-free and forbids the two unnecessary
  V36 anomalon couplings.  The three retained mass terms already give
  det(M_A)=a^2 b^2 c.
*)
Global[[1]] = {Z[5610], Z5610Selector};
Z5610q0    = 1;
Z5610q170  = Exp[2*Pi*I*170/5610];
Z5610q1141 = Exp[2*Pi*I*1141/5610];
Z5610q2569 = Exp[2*Pi*I*2569/5610];
Z5610q3211 = Exp[2*Pi*I*3211/5610];
Z5610q4299 = Exp[2*Pi*I*4299/5610];
Z5610q5440 = Exp[2*Pi*I*5440/5610];
Z5610q5525 = Exp[2*Pi*I*5525/5610];

Gauge[[1]] = {GC, SU[4], color4, g4, False, Z5610q0};
Gauge[[2]] = {GL, SU[2], left,   gL, True,  Z5610q0};
Gauge[[3]] = {GR, SU[2], right,  gR, True,  Z5610q0};

SuperFields[[1]]  = {H,        1, h,      1,  2, 2, Z5610q0};
SuperFields[[2]]  = {Q,        3, q,      4,  2, 1, Z5610q0};
SuperFields[[3]]  = {Qc,       3, qc,    -4,  1, 2, Z5610q0};
SuperFields[[4]]  = {X,        1, sx,     1,  1, 1, Z5610q0};
SuperFields[[5]]  = {Sc,       1, sc,    -4,  1, 2, Z5610q0};
SuperFields[[6]]  = {Sbc,      1, sbc,    4,  1, 2, Z5610q0};
SuperFields[[7]]  = {Sig6,     1, sig6,   6,  1, 1, Z5610q0};
SuperFields[[8]]  = {PsiBar,   1, psib,  -4,  2, 1, Z5610q5440};
SuperFields[[9]]  = {Psi,      1, psi,    4,  2, 1, Z5610q0};
SuperFields[[10]] = {PsiC,     1, psic,  -4,  1, 2, Z5610q0};
SuperFields[[11]] = {PsiCBar,  1, psicb,  4,  1, 2, Z5610q5440};
SuperFields[[12]] = {P,        1, p,      1,  1, 1, Z5610q170};
SuperFields[[13]] = {Nv,       3, nv,     1,  1, 1, Z5610q0};
SuperFields[[14]] = {Pb,       1, pb,     1,  1, 1, Z5610q5440};
SuperFields[[15]] = {Zp,       1, szp,    1,  1, 1, Z5610q0};
SuperFields[[16]] = {A2,       1, a2,     1,  1, 1, Z5610q3211};
SuperFields[[17]] = {A32,      1, a32,    1,  1, 1, Z5610q2569};
SuperFields[[18]] = {A15,      1, a15,    1,  1, 1, Z5610q4299};
SuperFields[[19]] = {A17,      1, a17,    1,  1, 1, Z5610q1141};
SuperFields[[20]] = {A16,      1, a16,    1,  1, 1, Z5610q5525};

(* External Z4R superfield charges; every displayed W term has charge 2. *)
V37Z4RCharges = {
  {H,0}, {Q,1}, {Qc,1}, {X,2}, {Sc,0}, {Sbc,0},
  {Sig6,2}, {PsiBar,3}, {Psi,1}, {PsiC,1},
  {PsiCBar,3}, {P,2}, {Nv,1}, {Pb,2}, {Zp,2},
  {A2,0}, {A32,0}, {A15,2}, {A17,2}, {A16,0}
};

V37Z85Charges = {
  {H,0}, {Q,0}, {Qc,0}, {X,0}, {Sc,0}, {Sbc,0},
  {Sig6,0}, {PsiBar,0}, {Psi,0}, {PsiC,0},
  {PsiCBar,0}, {P,0}, {Nv,0}, {Pb,0}, {Zp,0},
  {A2,1}, {A32,84}, {A15,69}, {A17,16}, {A16,0}
};

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
 + yA16/2*P.A16.A16
);

AddSoftTerms = False;
AddSoftScalarMasses = False;
AddSoftGauginoMasses = False;

NameOfStates = {GaugeES};

V37SourceBoundary = {
  "ExactZ5610PureFiniteCounterclass",
  "Z85SpectatorQualityProtection",
  "ThreeTermFullRankAnomalonMassSector",
  "MixedPSSquaredSelectorAndFullRProductAuditOpen",
  "NoMicroscopicCompactificationOrMediationClaim"
};
