(* V23 Barr--Raby small-representation source scaffold.            *)
(* The operator ledger is binding; normalized component tensors are open. *)
Off[General::spell];

Model`Name = "SO10U1V23BarrRaby";
Model`NameLaTeX = "V23 Barr--Raby SUSY SO(10) x U(1)_X";
Model`Authors = "SO10 V23 completion frontier";
Model`Date = "2026-08-20";

Global[[1]] = {Z[2], FamilyParity};
Global[[2]] = {Z[4], BRSelector};
Global[[3]] = {U[1], HShape};
FamOdd = -1; FamEven = 1;

Gauge[[1]] = {G10, SO[10], SOGUT, g10, False, FamEven, 1, 0};
Gauge[[2]] = {GX, U[1], xcharge, gX, False, FamEven, 1, 0};

SuperFields[[1]] = {F, 3, f16, 16, 1, FamOdd, Exp[2*Pi*I*1/4], 1};
SuperFields[[2]] = {E10, 3, e10, 10, -2, FamOdd, Exp[2*Pi*I*0/4], -2};
SuperFields[[3]] = {NSterile, 3, n1, 1, 4, FamOdd, Exp[2*Pi*I*1/4], 5};
SuperFields[[4]] = {A45, 1, a45, 45, 0, FamEven, Exp[2*Pi*I*2/4], 0};
SuperFields[[5]] = {C16, 1, c16, 16, 1, FamEven, Exp[2*Pi*I*1/4], -1};
SuperFields[[6]] = {C16b, 1, c16b, -16, -1, FamEven, Exp[2*Pi*I*3/4], -1};
SuperFields[[7]] = {Cp16, 1, cp16, 16, 1, FamEven, Exp[2*Pi*I*3/4], -4};
SuperFields[[8]] = {Cp16b, 1, cp16b, -16, -1, FamEven, Exp[2*Pi*I*1/4], -2};
SuperFields[[9]] = {H1, 1, h1, 10, -2, FamEven, Exp[2*Pi*I*2/4], -2};
SuperFields[[10]] = {H2, 1, h2, 10, 2, FamEven, Exp[2*Pi*I*0/4], 2};
SuperFields[[11]] = {PA, 1, pa, 1, 0, FamEven, Exp[2*Pi*I*0/4], 0};
SuperFields[[12]] = {XC, 1, xc, 1, 0, FamEven, Exp[2*Pi*I*0/4], 2};
SuperFields[[13]] = {PC, 1, pc, 1, 0, FamEven, Exp[2*Pi*I*0/4], -1};
SuperFields[[14]] = {P, 1, p, 1, 0, FamEven, Exp[2*Pi*I*0/4], 3};
SuperFields[[15]] = {Pbar, 1, pb, 1, 0, FamEven, Exp[2*Pi*I*0/4], 5};
SuperFields[[16]] = {Z, 1, z, 1, 0, FamEven, Exp[2*Pi*I*2/4], 3};
SuperFields[[17]] = {Zbar, 1, zb, 1, 0, FamEven, Exp[2*Pi*I*2/4], 5};
SuperFields[[18]] = {XHplus, 1, xhp, 1, 4, FamEven, Exp[2*Pi*I*0/4], 4};
SuperFields[[19]] = {XHminus, 1, xhm, 1, -4, FamEven, Exp[2*Pi*I*0/4], -4};
SuperFields[[20]] = {YH, 1, yh, 1, 0, FamEven, Exp[2*Pi*I*0/4], 0};
SuperFields[[21]] = {Xnuplus, 1, xnp, 1, 4, FamEven, Exp[2*Pi*I*1/4], 5};
SuperFields[[22]] = {Xnuminus, 1, xnm, 1, -4, FamEven, Exp[2*Pi*I*3/4], -5};
SuperFields[[23]] = {Ynu, 1, ynu, 1, 0, FamEven, Exp[2*Pi*I*0/4], 0};
SuperFields[[24]] = {M, 3, mess, 1, 0, FamOdd, Exp[2*Pi*I*0/4], 0};
SuperFields[[25]] = {Mbar, 3, messb, 1, 0, FamOdd, Exp[2*Pi*I*0/4], 0};
SuperFields[[26]] = {L, 3, lmsg, 1, 0, FamOdd, Exp[2*Pi*I*0/4], 0};
SuperFields[[27]] = {PQ, 1, pq, 1, 0, FamEven, Exp[2*Pi*I*2/4], 18};
SuperFields[[28]] = {PQbar, 1, pqb, 1, 0, FamEven, Exp[2*Pi*I*2/4], -18};
SuperFields[[29]] = {YPQ, 1, ypq, 1, 0, FamEven, Exp[2*Pi*I*0/4], 0};
SuperFields[[30]] = {K10, 1, k10, 10, 0, FamEven, Exp[2*Pi*I*1/4], -9};

V23SourceBoundary = <|
  "SelectedOperatorCount" -> 25,
  "SuperPotentialEncoded" -> False,
  "Reason" -> "quartic trace and spinor bridge require frozen tensor choices"
|>;

(* Fail-closed: no polynomial is asserted before tensor normalization. *)
SuperPotential = 0;
NameOfStates = {GaugeES};
