(* REJECTED V39 Z5 exploration; retained only as a negative-control source. *)
Off[General::spell];

Model`Name = "PSZ4RZ5610Z5SUSYV39";
Model`NameLaTeX = "V39 Z_{5610} times Z_5 selected SUSY Pati-Salam EFT";
Model`Authors = "V39 fail-closed baryon-operator redesign";
Model`Date = "2026-08-26";

(*)
  The V37 single real 6 is replaced by two chiral 6s, SigC and SigBc.
  The new Z5 assignments forbid X Q^4, X Qc^4, Zp Q^4, and Zp Qc^4,
  while retaining all renormalizable Yukawa and type-I seesaw source terms.

  V39 Z5 charges:
    Q,Qc = 4,1; Sc,Sbc = 1,4; SigC,SigBc = 3,2;
    PsiBar,Psi,PsiC,PsiCBar = 1,4,1,4;
    A2,A32,A15,A17,A16 = 1,4,2,3,0.

  Rejection reason: the standard mixed Pati--Salam x Z5 residues of this
  charge choice are nonzero (SU2L=3 and SU2R=2 mod 5). It must not be used as
  a candidate completion or included in the V39 final source manifest.
*)
Global[[1]] = {Z[5610], Z5610Selector};
Global[[2]] = {Z[5], V39BaryonSelector};

Z5610q0    = 1;
Z5610q170  = Exp[2*Pi*I*170/5610];
Z5610q1141 = Exp[2*Pi*I*1141/5610];
Z5610q2569 = Exp[2*Pi*I*2569/5610];
Z5610q3211 = Exp[2*Pi*I*3211/5610];
Z5610q4299 = Exp[2*Pi*I*4299/5610];
Z5610q5440 = Exp[2*Pi*I*5440/5610];
Z5610q5525 = Exp[2*Pi*I*5525/5610];

Z5q0 = 1;
Z5q1 = Exp[2*Pi*I/5];
Z5q2 = Exp[2*Pi*I*2/5];
Z5q3 = Exp[2*Pi*I*3/5];
Z5q4 = Exp[2*Pi*I*4/5];

Gauge[[1]] = {GC, SU[4], color4, g4, False, Z5610q0, Z5q0};
Gauge[[2]] = {GL, SU[2], left,   gL, True,  Z5610q0, Z5q0};
Gauge[[3]] = {GR, SU[2], right,  gR, True,  Z5610q0, Z5q0};

SuperFields[[1]]  = {H,        1, h,      1,  2, 2, Z5610q0,    Z5q0};
SuperFields[[2]]  = {Q,        3, q,      4,  2, 1, Z5610q0,    Z5q4};
SuperFields[[3]]  = {Qc,       3, qc,    -4,  1, 2, Z5610q0,    Z5q1};
SuperFields[[4]]  = {X,        1, sx,     1,  1, 1, Z5610q0,    Z5q0};
SuperFields[[5]]  = {Sc,       1, sc,    -4,  1, 2, Z5610q0,    Z5q1};
SuperFields[[6]]  = {Sbc,      1, sbc,    4,  1, 2, Z5610q0,    Z5q4};
SuperFields[[7]]  = {SigC,     1, sigc,   6,  1, 1, Z5610q0,    Z5q3};
SuperFields[[8]]  = {SigBc,    1, sigbc,  6,  1, 1, Z5610q0,    Z5q2};
SuperFields[[9]]  = {PsiBar,   1, psib,  -4,  2, 1, Z5610q5440, Z5q1};
SuperFields[[10]] = {Psi,      1, psi,    4,  2, 1, Z5610q0,    Z5q4};
SuperFields[[11]] = {PsiC,     1, psic,  -4,  1, 2, Z5610q0,    Z5q1};
SuperFields[[12]] = {PsiCBar,  1, psicb,  4,  1, 2, Z5610q5440, Z5q4};
SuperFields[[13]] = {P,        1, p,      1,  1, 1, Z5610q170,  Z5q0};
SuperFields[[14]] = {Nv,       3, nv,     1,  1, 1, Z5610q0,    Z5q0};
SuperFields[[15]] = {Pb,       1, pb,     1,  1, 1, Z5610q5440, Z5q0};
SuperFields[[16]] = {Zp,       1, szp,    1,  1, 1, Z5610q0,    Z5q0};
SuperFields[[17]] = {A2,       1, a2,     1,  1, 1, Z5610q3211, Z5q1};
SuperFields[[18]] = {A32,      1, a32,    1,  1, 1, Z5610q2569, Z5q4};
SuperFields[[19]] = {A15,      1, a15,    1,  1, 1, Z5610q4299, Z5q2};
SuperFields[[20]] = {A17,      1, a17,    1,  1, 1, Z5610q1141, Z5q3};
SuperFields[[21]] = {A16,      1, a16,    1,  1, 1, Z5610q5525, Z5q0};

(* External Z4R superfield charges; all displayed W terms have charge 2. *)
V39Z4RCharges = {
  {H,0}, {Q,1}, {Qc,1}, {X,2}, {Sc,0}, {Sbc,0},
  {SigC,2}, {SigBc,2}, {PsiBar,3}, {Psi,1}, {PsiC,1},
  {PsiCBar,3}, {P,2}, {Nv,1}, {Pb,2}, {Zp,2},
  {A2,0}, {A32,0}, {A15,2}, {A17,2}, {A16,0}
};

V39Z5Charges = {
  {H,0}, {Q,4}, {Qc,1}, {X,0}, {Sc,1}, {Sbc,4},
  {SigC,3}, {SigBc,2}, {PsiBar,1}, {Psi,4}, {PsiC,1},
  {PsiCBar,4}, {P,0}, {Nv,0}, {Pb,0}, {Zp,0},
  {A2,1}, {A32,4}, {A15,2}, {A17,3}, {A16,0}
};

SuperPotential = (
 - (kappaPS*vPS2 + kappaPQ*fPQ2)*X
 - (rhoPS*vPS2 + rhoPQ*fPQ2)*Zp
 + kappaPS*X.Sbc.Sc + kappaPQ*X.P.Pb
 + rhoPS*Zp.Sbc.Sc + rhoPQ*Zp.P.Pb
 + kappaX/3*X.X.X + kappaXXZ/2*X.X.Zp
 + kappaXZZ/2*X.Zp.Zp + kappaZ/3*Zp.Zp.Zp
 + lambdaH/2*X.H.H + lambdaXSig*X.SigC.SigBc
 + lambdaZH/2*Zp.H.H + lambdaZSig*Zp.SigC.SigBc
 + lambdaSc/2*Sc.Sc.SigC + lambdaSbc/2*Sbc.Sbc.SigBc
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

V39SourceBoundary = {
  "Z5ForbidsDriverDressedFourMatterSources",
  "SplitSixArchitecturePreservesCanonicalFDEqualVEVBranch",
  "V37Z5610QualityChargeLatticeRetained",
  "FullZ5610TimesZ5ProductBordismAndUVOriginOpen",
  "NoPoleSpectrumSoftVacuumOrFlavourLikelihoodClaim"
};
