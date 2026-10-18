(* ==================================================================== *)
(* Native non-supersymmetric SARAH 4 input: SO(10) x U(1)_X, residual  *)
(* Z_17, B63 anomaly-cancelling fermion catalogue, v20 scalars + one   *)
(* real 45_H (design v22-L2).                                          *)
(*                                                                      *)
(* DRAFT (stage 2a "model" of the v22 scalar redesign, 2026-10-17).    *)
(* Changes with respect to models/SO10Z17AxionV20.m:                   *)
(*  - the Gauge, Global, five ScalarFields rows and every v20 scalar-   *)
(*    potential row (LagNoHC verbatim, kappaH H10.H10.S verbatim) are  *)
(*    kept verbatim; the v20 Yukawas Y10 F.F.H10 and Y126              *)
(*    F.F.Delta126bar are kept verbatim;                               *)
(*  - NEW scalar A45: a real 45_H with X = 0 (Z17 phase 1, Spin(10)    *)
(*    centre class 0) and its renormalizable invariants;               *)
(*  - the v20 fermion catalogue (P, R, SpecS, SpecB, Q, Pbar, Qbar,    *)
(*    Rbar and their eight Yukawa / mixing rows) is REPLACED by the    *)
(*    B63 catalogue with its 12 renormalizable Yukawa structures (the  *)
(*    exhaustive enumeration census_v22.py finds exactly these 12; no  *)
(*    bare mass and no A45 Yukawa is X-neutral and SO(10)-invariant).  *)
(*                                                                      *)
(* Scalar-potential contract (census_v22.py, explicit_basis_v22.py,    *)
(* susyno_count_v22.wls; invariants.json):                             *)
(*  v20 part : 44 invariant directions, 51 real parameters (verbatim,   *)
(*             reproduced exactly by an independent character census); *)
(*  A part   : 30 invariant directions, 34 real parameters             *)
(*             (17 orbits; 26 real + 4 complex couplings);             *)
(*  total    : 74 directions, 85 real parameters, all exactly X = 0.   *)
(* The independent Clebsch contractions of the multi-invariant         *)
(* families are defined by the explicit index contractions of          *)
(* invariants.json and evaluated by a tensor backend; a single SARAH   *)
(* Dot contraction must not be interpreted as such a multi-invariant   *)
(* basis.  The Lagrangian below therefore registers, besides the v20   *)
(* rows, only those A45 terms whose non-symmetrised SO(10) product has *)
(* exactly ONE invariant (so the SARAH/Susyno Dot is unambiguous) AND  *)
(* whose product is small enough for SARAH's explicit Clebsch          *)
(* construction (<= 4500 components, cf. the largest v20/v21 row        *)
(* F.F.Delta126bar with 32256): m45Sq, lambdaAS, lambdaA17, kappaHA.   *)
(* Four further unique A45 invariants (kappaPAA, kappaDA, lambdaPAH,   *)
(* lambdaAAHD; 4.3e5 - 2.6e6 components) made SARAH 4.15.3 Start[]     *)
(* exceed 900 s and are listed, with all remaining A45 families, in    *)
(* the comment block at the end (v20 likewise registers none of its    *)
(* Phi210-containing unique rows O14, O15, O17).                       *)
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

Model`Name = "SO10Z17AxionV22";
Model`NameLaTeX = "SO(10) x U(1)_X axion candidate v22-L2 (B63 fermions, v20 scalars + real 45_H)";
Model`Authors = "SO10 axion v22 draft (stage 2a model)";
Model`Date = "2026-10-17";

NameOfStates = {GaugeES};

(* Gauge groups: {field, group, name, coupling, expand, Z17 phase}.  Both
   gauge multiplets are Z17 neutral. *)
Gauge[[1]] = {G10, SO[10], SOGUT, g10, False, 1};
Gauge[[2]] = {GX, U[1], Xcharge, gX, False, 1};

(* The gauged field Phi17 leaves this exact residual subgroup after its VEV. *)
Global[[1]] = {Z[17], Z17};

(* Native order: {multiplet, generations, components, SO(10), X, Z17}.
   The Z17 phase of each field is Exp[2 Pi I (X mod 17)/17].
   Rows 1-5 verbatim from v20; row 6 is the new real 45_H. *)
ScalarFields[[1]] = {Phi210,       1, phi210,      210,    0, 1};
ScalarFields[[2]] = {Delta126bar,  1, delta126bar, -126,  -2, Exp[2*Pi*I*15/17]};
ScalarFields[[3]] = {H10,          1, h10,           10,  -2, Exp[2*Pi*I*15/17]};
ScalarFields[[4]] = {S,            1, singletS,        1,   4, Exp[2*Pi*I*4/17]};
ScalarFields[[5]] = {Phi17,        1, phi17,           1,  17, 1};
ScalarFields[[6]] = {A45,          1, a45,            45,   0, 1};

(* The 210 and the 45 are real SO(10) representations. *)
RealScalars = {phi210, a45};

(* B63 fermion catalogue (all two-component left-handed Weyl multiplets;
   {name, generations, components, SO(10), X, Z17 phase}):
     F 3x16(1) | Vec1 2x16(-35), Vec1bar 16bar(39) | Vec2 16(-28), Vec2bar 16bar(32) |
     Vec3 16(34), Vec3bar 16bar(-30) | TenF 2x10(2) | Pbar 16bar(18) |
     SingN1 1(-63), SingN1bar 1(59) | SingN2 1(-58), SingN2bar 1(54) |
     SingN3 1(-57), SingN3bar 1(61) | SingM 2x1(-2).
   (B63 labels: Vec1 = V1, Vec1bar = Vb1, Vec2 = V2, Vec2bar = Vb2, Vec3 = V3, Vec3bar = Vb3, TenF = T,
    Pbar = Pb, SingN1 = N1, SingN1bar = N1b, ..., SingM = NMm.)
   Exact anomaly sums (d1_contract_v22.py): [SO(10)]^2 X = 0, X^3 = 0, grav-X = 0; net 16 - 16bar = 3. *)
FermionFields[[1]]  = {F,          3, f16,          16,   1, Exp[2*Pi*I*1/17]};
FermionFields[[2]]  = {Vec1,       2, vec1f16,      16, -35, Exp[2*Pi*I*16/17]};
FermionFields[[3]]  = {Vec1bar,    1, vec1b16bar,  -16,  39, Exp[2*Pi*I*5/17]};
FermionFields[[4]]  = {Vec2,       1, vec2f16,      16, -28, Exp[2*Pi*I*6/17]};
FermionFields[[5]]  = {Vec2bar,    1, vec2b16bar,  -16,  32, Exp[2*Pi*I*15/17]};
FermionFields[[6]]  = {Vec3,       1, vec3f16,      16,  34, 1};
FermionFields[[7]]  = {Vec3bar,    1, vec3b16bar,  -16, -30, Exp[2*Pi*I*4/17]};
FermionFields[[8]]  = {TenF,       2, tenf10,       10,   2, Exp[2*Pi*I*2/17]};
FermionFields[[9]]  = {Pbar,       1, pbar16bar,   -16,  18, Exp[2*Pi*I*1/17]};
FermionFields[[10]] = {SingN1,     1, singn1,        1, -63, Exp[2*Pi*I*5/17]};
FermionFields[[11]] = {SingN1bar,  1, singn1b,       1,  59, Exp[2*Pi*I*8/17]};
FermionFields[[12]] = {SingN2,     1, singn2,        1, -58, Exp[2*Pi*I*10/17]};
FermionFields[[13]] = {SingN2bar,  1, singn2b,       1,  54, Exp[2*Pi*I*3/17]};
FermionFields[[14]] = {SingN3,     1, singn3,        1, -57, Exp[2*Pi*I*11/17]};
FermionFields[[15]] = {SingN3bar,  1, singn3b,       1,  61, Exp[2*Pi*I*10/17]};
FermionFields[[16]] = {SingM,      2, singm,         1,  -2, Exp[2*Pi*I*15/17]};

DEFINITION[GaugeES][LagrangianInput] = {
  {LagHC,   {AddHC -> True}},
  {LagNoHC, {AddHC -> False}}
};

(* EVERY SO(10)-singlet, X-neutral renormalizable fermion term (the 12 B63
   structures; Y10, Y126, yT, yM symmetric matrices, yP and y1 2-vectors),
   the v20 holomorphic scalar term kappaH (verbatim), and the unique A45
   cubic i Hdag.A.H, whose Clebsch is antisymmetric in the conjugate pair
   (SARAH adds the h.c., which keeps 2 i Im(kappaHA) times the real
   invariant). *)
LagHC = -(
    Y10 F.F.H10
  + Y126 F.F.Delta126bar
  + y1 conj[S].Vec1.Vec1bar
  + yP Vec1.Pbar.Phi17
  + y2 conj[S].Vec2.Vec2bar
  + lam23 Vec2bar.Vec3bar.H10
  + y3 conj[S].Vec3.Vec3bar
  + yT conj[S].TenF.TenF
  + yN1 S.SingN1.SingN1bar
  + yN2 S.SingN2.SingN2bar
  + yN3 conj[S].SingN3.SingN3bar
  + yM S.SingM.SingM
  + kappaH H10.H10.S
  + kappaHA A45.conj[H10].H10
);

(* Hermitian mass and singlet-quartic sector: the eight v20 rows verbatim,
   then the A45 mass and the two A45^2 singlet portals.  Covariant kinetic
   terms are generated by SARAH from the native gauge and matter
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
  + m45Sq/2 A45.A45
  + lambdaAS conj[S].S.A45.A45
  + lambdaA17 conj[Phi17].Phi17.A45.A45
);

(* ==================================================================== *)
(* COMPLETE A45 INVARIANT BASIS (tensor backend; explicit contractions   *)
(* and normalisations in invariants.json).  A_ab real antisymmetric,     *)
(* P_abcd = Phi210 real 4-form, H_a = H10, D_abcde = Delta126bar with   *)
(* *D = -i D, eps = Levi-Civita; Hb = conj[H], Db = conj[D].            *)
(*  pure A    : m45Sq (A.A), lambdaA1 (A_ab A_ab)^2, lambdaA2 Tr(A^4)    *)
(*              [A^3: 0 identically]                                    *)
(*  A-Phi     : kappaPPA eps.P.P.A [pseudo-scalar; the ONLY A P P        *)
(*              invariant, 45 in Sym^2(210)], kappaPAA P_abcd A_ab A_cd,*)
(*              lambdaPPPA1,2 eps-type P^3 A, lambdaPPAA1..4 P^2 A^2,   *)
(*              lambdaPAAA eps.P.A.A.A  [P A: 0]                        *)
(*  A-H10     : kappaHA i Hb.A.H, lambdaAAH1 (A.A)(Hb.H),               *)
(*              lambdaAAH2 |A.H|^2 = -Hb.A.A.H,                         *)
(*              lambdaPAH i P_abcd A_ab H_c Hb_d                        *)
(*  A-Delta   : kappaDA i Db.A.D, lambdaAAD1..3, lambdaPAD1..4          *)
(*  A-H-Delta : lambdaAAHD (complex) (AA)_210.Hb.D,                     *)
(*              lambdaPAHD1..3 (complex): A x P -> 2 x 210 + 1050       *)
(*              channels contracted with Hb.D (10 x 126bar = 210+1050bar)*)
(*  singlets  : lambdaAS (A.A)|S|^2, lambdaA17 (A.A)|Phi17|^2            *)
(* Unique invariants NOT registered above (SARAH-ready rows, valid but  *)
(* too large for SARAH 4.15.3's explicit Clebsch step within 900 s):   *)
(*   LagNoHC:  + kappaPAA Phi210.A45.A45                                *)
(*   LagHC:    + kappaDA A45.conj[Delta126bar].Delta126bar              *)
(*             + lambdaPAH Phi210.A45.conj[H10].H10                     *)
(*             + lambdaAAHD conj[H10].Delta126bar.A45.A45               *)
(* X-allowed but identically zero (no SO(10) singlet): A, A P, A^3,     *)
(* A Hb D, A |S|^2, A |Phi17|^2, A P |S|^2, A P |Phi17|^2, A H H S,     *)
(* A H D S, A D D S (+ conjugates); no A45 fermion bilinear exists.     *)
(* ==================================================================== *)
