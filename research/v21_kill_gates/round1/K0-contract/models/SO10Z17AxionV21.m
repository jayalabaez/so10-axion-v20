(* ==================================================================== *)
(* Native non-supersymmetric SARAH 4 input: SO(10) x U(1)_X, residual  *)
(* Z_17, and the complete anomaly-cancelling v21 (F17) matter catalogue. *)
(*                                                                      *)
(* DRAFT (gate K0 of the v21-F17-G3221 research track, 2026-10-16).    *)
(* The gauge sector, the five scalars and the 51-parameter scalar       *)
(* potential are those of models/SO10Z17AxionV20.m, verbatim.  Only the *)
(* fermion catalogue changes: the v20 P, R, Q (+ bars) and the five     *)
(* spectator pairs are replaced by the F17 sector.                      *)
(*                                                                      *)
(* Completeness contract: LagHC lists EVERY renormalizable fermion      *)
(* bilinear term (Yukawa or bare mass) that is simultaneously an SO(10) *)
(* singlet and U(1)_X neutral (hence Z17 neutral), as enumerated exactly *)
(* by k0_couplings.py over all pairs of declared fermion fields and all  *)
(* declared scalars and their conjugates (12 coupling structures; no     *)
(* bare mass term is X-neutral).  The scalar potential is unchanged.     *)
(*                                                                      *)
(* This file establishes the gauge, matter, charge, kinetic, and        *)
(* representative renormalizable-interaction contract.  The independent *)
(* Clebsch contractions of the full 210/126bar/10 scalar potential are  *)
(* evaluated by the repository tensor backend; a single SARAH Dot       *)
(* contraction must not be interpreted as that multi-invariant basis.   *)
(*                                                                      *)
(* SARAH-native conventions (verified against SARAH 4.15.3 sources and  *)
(* its bundled Z[N] models):                                            *)
(*  - with a declared Global symmetry every Gauge row carries the gauge *)
(*    multiplet's global charge as its sixth entry;                     *)
(*  - a Z[N] charge q is the phase Exp[2 Pi I q/N] (neutral = 1), since  *)
(*    CheckChargeConservationGlobal tests Times@@charges === 1;          *)
(*  - gauge-group names need at least three characters because SARAH   *)
(*    derives index names with StringTake[name, 3];                     *)
(*  - field names avoid Mathematica built-ins (C, D, E, I, K, N, O).    *)
(* ==================================================================== *)

Model`Name = "SO10Z17AxionV21";
Model`NameLaTeX = "SO(10) x U(1)_X axion candidate v21 (F17 fermion sector)";
Model`Authors = "SO10 axion v21 draft (gate K0)";
Model`Date = "2026-10-16";

NameOfStates = {GaugeES};

(* Gauge groups: {field, group, name, coupling, expand, Z17 phase}.  Both
   gauge multiplets are Z17 neutral. *)
Gauge[[1]] = {G10, SO[10], SOGUT, g10, False, 1};
Gauge[[2]] = {GX, U[1], Xcharge, gX, False, 1};

(* The gauged field Phi17 leaves this exact residual subgroup after its VEV. *)
Global[[1]] = {Z[17], Z17};

(* Native order: {multiplet, generations, components, SO(10), X, Z17}.
   The Z17 phase of each field is Exp[2 Pi I (X mod 17)/17].  Unchanged from v20. *)
ScalarFields[[1]] = {Phi210,       1, phi210,      210,    0, 1};
ScalarFields[[2]] = {Delta126bar,  1, delta126bar, -126,  -2, Exp[2*Pi*I*15/17]};
ScalarFields[[3]] = {H10,          1, h10,           10,  -2, Exp[2*Pi*I*15/17]};
ScalarFields[[4]] = {S,            1, singletS,        1,   4, Exp[2*Pi*I*4/17]};
ScalarFields[[5]] = {Phi17,        1, phi17,           1,  17, 1};

(* The 210 is a real SO(10) representation. *)
RealScalars = {phi210};

(* F17 fermion catalogue (all two-component left-handed Weyl multiplets):
   three light families F; the S-sector (masses ~ y <S>): two tensor fermions
   TenA = 10_F(X=-1), TenB = 10_F(X=5), three vectorlike spinor pairs
   Vec1 = 16(0) + Vec1bar = 16bar(4), Vec2 = 16(-3) + Vec2bar = 16bar(7),
   Vec3 = 16(-6) + Vec3bar = 16bar(10), and two singlet pairs
   SingN = 1(-3) (x2) + SingM = 1(-1) (x2); the Phi-sector (mass ~ y <Phi17>):
   PhiV = 16(-9) + PhiVbar = 16bar(-8).
   Exact anomaly sums (k0_anomalies_pq.py): [SO(10)]^2 X = 0, grav-X = 0, X^3 = 0. *)
FermionFields[[1]]  = {F,        3, f16,        16,   1, Exp[2*Pi*I*1/17]};
FermionFields[[2]]  = {TenA,     1, tenA10,     10,  -1, Exp[2*Pi*I*16/17]};
FermionFields[[3]]  = {TenB,     1, tenB10,     10,   5, Exp[2*Pi*I*5/17]};
FermionFields[[4]]  = {Vec1,     1, vec1f16,    16,   0, 1};
FermionFields[[5]]  = {Vec1bar,  1, vec1b16bar, -16,  4, Exp[2*Pi*I*4/17]};
FermionFields[[6]]  = {Vec2,     1, vec2f16,    16,  -3, Exp[2*Pi*I*14/17]};
FermionFields[[7]]  = {Vec2bar,  1, vec2b16bar, -16,  7, Exp[2*Pi*I*7/17]};
FermionFields[[8]]  = {Vec3,     1, vec3f16,    16,  -6, Exp[2*Pi*I*11/17]};
FermionFields[[9]]  = {Vec3bar,  1, vec3b16bar, -16, 10, Exp[2*Pi*I*10/17]};
FermionFields[[10]] = {PhiV,     1, phiv16,     16,  -9, Exp[2*Pi*I*8/17]};
FermionFields[[11]] = {PhiVbar,  1, phivb16bar, -16, -8, Exp[2*Pi*I*9/17]};
FermionFields[[12]] = {SingN,    2, singn1,      1,  -3, Exp[2*Pi*I*14/17]};
FermionFields[[13]] = {SingM,    2, singm1,      1,  -1, Exp[2*Pi*I*16/17]};

DEFINITION[GaugeES][LagrangianInput] = {
  {LagHC,   {AddHC -> True}},
  {LagNoHC, {AddHC -> False}}
};

(* EVERY SO(10)-singlet, X-neutral renormalizable fermion bilinear term.
   Yukawa matrices: Y10, Y126 symmetric 3x3; lamF2 a 3-vector; yAM, yBN
   2-vectors; yNM a 2x2 matrix; the rest single couplings. *)
LagHC = -(
    Y10 F.F.H10
  + Y126 F.F.Delta126bar
  + lamF2 F.Vec2.conj[H10]
  + lam3P Vec3bar.PhiVbar.H10
  + y1 conj[S].Vec1.Vec1bar
  + y2 conj[S].Vec2.Vec2bar
  + y3 conj[S].Vec3.Vec3bar
  + yP Phi17.PhiV.PhiVbar
  + yAB conj[S].TenA.TenB
  + yAM TenA.SingM.conj[H10]
  + yBN TenB.SingN.H10
  + yNM S.SingN.SingM
);

(* Hermitian mass and singlet-quartic sector (unchanged from v20).  Covariant
   kinetic terms are generated by SARAH from the native gauge and matter
   declarations above. *)
LagNoHC = -(
    m210Sq/2 Phi210.Phi210
  + m126Sq conj[Delta126bar].Delta126bar
  + m10Sq conj[H10].H10
  + mSSq conj[S].S
  + m17Sq conj[Phi17].Phi17
  + lambdaS/2 conj[S].S.conj[S].S
  + lambda17/2 conj[Phi17].Phi17.conj[Phi17].Phi17
  + lambdaS17 conj[S].S.conj[Phi17].Phi17
);
