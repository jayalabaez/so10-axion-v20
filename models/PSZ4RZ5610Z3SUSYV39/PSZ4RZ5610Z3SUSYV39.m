(* V39 baryon-operator redesign of the V37 SUSY Pati--Salam EFT. *)
Off[General::spell];

Model`Name = "PSZ4RZ5610Z3SUSYV39";
Model`NameLaTeX = "V39 Z_{5610} times Z_3 selected SUSY Pati-Salam EFT";
Model`Authors = "V39 fail-closed baryon-operator redesign";
Model`Date = "2026-08-26";

(*
  The V37 single real 6 is replaced by two chiral 6s, SigC and SigBc.
  The ordinary Z3 selector is deliberately minimal: it preserves the full
  displayed renormalizable driver, Yukawa, mixing, seesaw, and anomalon
  mass terms while forbidding X Q^4, X Qc^4, Zp Q^4, and Zp Qc^4.

  V39 Z3 charges:
    Q,Qc = 1,2; Sc,Sbc = 2,1; SigC,SigBc = 2,1;
    PsiBar,Psi,PsiC,PsiCBar = 2,1,2,1;
    A2,A32,A15,A17,A16 = 1,2,0,0,0.

  The charge choice makes the standard mixed Pati--Salam x Z3 residues and
  the two raw Z3--Z5610 cross residues vanish modulo 3.  It is not a claim
  of a complete product-bordism, discrete-R, or UV anomaly completion.
*)
Global[[1]] = {Z[5610], Z5610Selector};
Global[[2]] = {Z[3], V39BaryonSelector};

Z5610q0    = 1;
Z5610q170  = Exp[2*Pi*I*170/5610];
Z5610q1141 = Exp[2*Pi*I*1141/5610];
Z5610q2569 = Exp[2*Pi*I*2569/5610];
Z5610q3211 = Exp[2*Pi*I*3211/5610];
Z5610q4299 = Exp[2*Pi*I*4299/5610];
Z5610q5440 = Exp[2*Pi*I*5440/5610];
Z5610q5525 = Exp[2*Pi*I*5525/5610];

Z3q0 = 1;
Z3q1 = Exp[2*Pi*I/3];
Z3q2 = Exp[2*Pi*I*2/3];

Gauge[[1]] = {GC, SU[4], color4, g4, False, Z5610q0, Z3q0};
Gauge[[2]] = {GL, SU[2], left,   gL, True,  Z5610q0, Z3q0};
Gauge[[3]] = {GR, SU[2], right,  gR, True,  Z5610q0, Z3q0};

SuperFields[[1]]  = {H,        1, h,      1,  2, 2, Z5610q0,    Z3q0};
SuperFields[[2]]  = {Q,        3, q,      4,  2, 1, Z5610q0,    Z3q1};
SuperFields[[3]]  = {Qc,       3, qc,    -4,  1, 2, Z5610q0,    Z3q2};
SuperFields[[4]]  = {X,        1, sx,     1,  1, 1, Z5610q0,    Z3q0};
SuperFields[[5]]  = {Sc,       1, sc,    -4,  1, 2, Z5610q0,    Z3q2};
SuperFields[[6]]  = {Sbc,      1, sbc,    4,  1, 2, Z5610q0,    Z3q1};
SuperFields[[7]]  = {SigC,     1, sigc,   6,  1, 1, Z5610q0,    Z3q2};
SuperFields[[8]]  = {SigBc,    1, sigbc,  6,  1, 1, Z5610q0,    Z3q1};
SuperFields[[9]]  = {PsiBar,   1, psib,  -4,  2, 1, Z5610q5440, Z3q2};
SuperFields[[10]] = {Psi,      1, psi,    4,  2, 1, Z5610q0,    Z3q1};
SuperFields[[11]] = {PsiC,     1, psic,  -4,  1, 2, Z5610q0,    Z3q2};
SuperFields[[12]] = {PsiCBar,  1, psicb,  4,  1, 2, Z5610q5440, Z3q1};
SuperFields[[13]] = {P,        1, p,      1,  1, 1, Z5610q170,  Z3q0};
SuperFields[[14]] = {Nv,       3, nv,     1,  1, 1, Z5610q0,    Z3q0};
SuperFields[[15]] = {Pb,       1, pb,     1,  1, 1, Z5610q5440, Z3q0};
SuperFields[[16]] = {Zp,       1, szp,    1,  1, 1, Z5610q0,    Z3q0};
SuperFields[[17]] = {A2,       1, a2,     1,  1, 1, Z5610q3211, Z3q1};
SuperFields[[18]] = {A32,      1, a32,    1,  1, 1, Z5610q2569, Z3q2};
SuperFields[[19]] = {A15,      1, a15,    1,  1, 1, Z5610q4299, Z3q0};
SuperFields[[20]] = {A17,      1, a17,    1,  1, 1, Z5610q1141, Z3q0};
SuperFields[[21]] = {A16,      1, a16,    1,  1, 1, Z5610q5525, Z3q0};

(* External Z4R superfield charges; all displayed W terms have charge 2. *)
V39Z4RCharges = {
  {H,0}, {Q,1}, {Qc,1}, {X,2}, {Sc,0}, {Sbc,0},
  {SigC,2}, {SigBc,2}, {PsiBar,3}, {Psi,1}, {PsiC,1},
  {PsiCBar,3}, {P,2}, {Nv,1}, {Pb,2}, {Zp,2},
  {A2,0}, {A32,0}, {A15,2}, {A17,2}, {A16,0}
};

V39Z3Charges = {
  {H,0}, {Q,1}, {Qc,2}, {X,0}, {Sc,2}, {Sbc,1},
  {SigC,2}, {SigBc,1}, {PsiBar,2}, {Psi,1}, {PsiC,2},
  {PsiCBar,1}, {P,0}, {Nv,0}, {Pb,0}, {Zp,0},
  {A2,1}, {A32,2}, {A15,0}, {A17,0}, {A16,0}
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
  "Z3ForbidsLocalDriverDressedFourMatterSources",
  "SplitSixArchitecturePreservesCanonicalFDEqualVEVBranch",
  "V37Z5610QualityChargeLatticeRetained",
  "FullZ5610TimesZ3ProductBordismAndUVOriginOpen",
  "NoPoleSpectrumSoftVacuumOrFlavourLikelihoodClaim"
};
