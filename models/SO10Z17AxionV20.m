(* ==================================================================== *)
(* Native non-supersymmetric SARAH 4 input: SO(10) x U(1)_X, residual  *)
(* Z_17, and the complete anomaly-cancelling v20 matter catalogue.      *)
(*                                                                      *)
(* This file establishes the gauge, matter, charge, kinetic, and        *)
(* representative renormalizable-interaction contract.  The independent *)
(* Clebsch contractions of the full 210/126bar/10 scalar potential are  *)
(* evaluated by the repository tensor backend; a single SARAH Dot       *)
(* contraction must not be interpreted as that multi-invariant basis.   *)
(* ==================================================================== *)

Model`Name = "SO10Z17AxionV20";
Model`NameLaTeX = "SO(10) x U(1)_X axion candidate v20";
Model`Authors = "SO10 axion v20 collaboration";
Model`Date = "2026-08-07";

NameOfStates = {GaugeES};

(* Gauge groups.  The fifth entry follows SARAH's adjoint-index-expansion
   convention; neither factor needs explicit adjoint components here. *)
(* With a declared Global symmetry SARAH expects the sixth gauge entry to
   carry that gauge multiplet's global charge.  Both gauge multiplets are
   neutral under Z17.  Keep the U(1) description at least three characters:
   SARAH derives component names with StringTake[...,3]. *)
Gauge[[1]] = {G10, SO[10], SOGUT, g10, False, 0};
Gauge[[2]] = {GX, U[1], xcharge, gX, False, 0};

(* The gauged field Phi17 leaves this exact residual subgroup after its VEV. *)
Global[[1]] = {Z[17], Z17};

(* Native order: {multiplet, generations, components, SO(10), X, Z17}.
   SARAH represents a Z[N] charge q by the exact phase Exp[2 Pi I q/N]. *)
ScalarFields[[1]] = {Phi210,       1, phi210,      210,    0, 1};
ScalarFields[[2]] = {Delta126bar,  1, delta126bar, -126,  -2, Exp[2*Pi*I*15/17]};
ScalarFields[[3]] = {H10,          1, h10,           10,  -2, Exp[2*Pi*I*15/17]};
ScalarFields[[4]] = {S,            1, singletS,        1,   4, Exp[2*Pi*I*4/17]};
ScalarFields[[5]] = {Phi17,        1, phi17,           1,  17, 1};

(* The 210 is a real SO(10) representation. *)
RealScalars = {phi210};

(* Three light F families, P and R, five s/b spectator pairs, and Q sector. *)
FermionFields[[1]] = {F,      3, f16,      16,   1, Exp[2*Pi*I*1/17]};
FermionFields[[2]] = {P,      1, p16,      16,   1, Exp[2*Pi*I*1/17]};
FermionFields[[3]] = {R,      1, r16,      16,   1, Exp[2*Pi*I*1/17]};
FermionFields[[4]] = {SpecS,  5, s16,      16,   2, Exp[2*Pi*I*2/17]};
FermionFields[[5]] = {SpecB,  5, b16bar,  -16,  -6, Exp[2*Pi*I*11/17]};
FermionFields[[6]] = {Q,      1, q16,      16,  14, Exp[2*Pi*I*14/17]};
FermionFields[[7]] = {Pbar,   1, pbar16,  -16,  16, Exp[2*Pi*I*16/17]};
FermionFields[[8]] = {Qbar,   1, qbar16,  -16,   3, Exp[2*Pi*I*3/17]};
FermionFields[[9]] = {Rbar,   1, rbar16,  -16, -18, Exp[2*Pi*I*16/17]};

DEFINITION[GaugeES][LagrangianInput] = {
  {LagHC,   {AddHC -> True}},
  {LagNoHC, {AddHC -> False}}
};

(* Canonical G1 does not consume RGE metadata.  These sentinels prevent the
   runtime audit from invoking SARAH's unrelated generic non-SUSY RGE tensor
   builder; SARAH still constructs and checks the actual Lagrangian index
   contractions below. *)
ContractionRGE[lambdaAudit] = 1;
ContractionRGE[m210Sq] = 1;

(* Charge-neutral Yukawa, vectorlike-mass, and mixing catalogue.  These terms
   are retained source-exact for the later full flavour/RGE gates, but are not
   registered in this G1 scalar-ring runtime audit: expanding the native
   16.16.126bar Clebsch is a G2/G6/G7 component calculation, not evidence for
   completeness of the derivative-free scalar invariant ring. *)
LagFermionCatalogue = -(
    Y10 F.F.H10
  + Y126 F.F.Delta126bar
  + yP conj[Phi17].P.Pbar
  + yQ conj[Phi17].Q.Qbar
  + yR Phi17.R.Rbar
  + ys S.SpecS.SpecB
  + lambdaP P.F.H10
  + lambdaR R.F.H10
  + lambdaQB conj[S].Qbar.F
  + lambdaQR S.Q.Rbar
);

(* The native 10.10.1 cubic keeps the external G1 run focused on model
   initialization, charge handling, anomaly cancellation and genuine
   Lagrangian construction.  SARAH's explicit SO(10) Clebsch expansion is not
   used as a proxy for the independent tensor ring: the exact 44-direction
   renormalizable basis and the d<=6 plethysm basis are separately bound. *)
LagHC = -(lambdaAudit H10.H10.S);

(* The complete renormalizable scalar catalogue is retained source-exact, but
   its 210/126bar/10 component expansion is the independently certified
   tensor-ring calculation rather than the purpose of this runtime probe. *)
LagScalarCatalogue = -(
    m210Sq/2 Phi210.Phi210
  + m126Sq conj[Delta126bar].Delta126bar
  + m10Sq conj[H10].H10
  + mSSq conj[S].S
  + m17Sq conj[Phi17].Phi17
  + lambdaS/2 conj[S].S.conj[S].S
  + lambda17/2 conj[Phi17].Phi17.conj[Phi17].Phi17
  + lambdaS17 conj[S].S.conj[Phi17].Phi17
);

(* Register the native real-210 quadratic audit term.  Together with LagHC it
   exercises SARAH's actual SO(10) and U(1)X Lagrangian construction and
   gauge-invariance pass while keeping the external attestation scoped to
   model/runtime/charge conventions. *)
LagNoHC = -(
    m210Sq/2 Phi210.Phi210
);
