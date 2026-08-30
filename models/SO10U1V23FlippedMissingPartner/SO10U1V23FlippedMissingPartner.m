(* Fail-closed V23 Maekawa--Yamashita flipped missing-partner scaffold. *)
(* Source: arXiv:hep-ph/0304293.  No normalized tensor W is asserted. *)
Off[General::spell];

Model`Name = "SO10U1V23FlippedMissingPartner";
Model`NameLaTeX = "V23 flipped SO(10) x U(1) missing-partner frontier";
Model`Authors = "SO10 V23 frontier";
Model`Date = "2026-08-20";

Global[[1]] = {Z[2], TableIZ2};
Global[[2]] = {U[1], AnomalousU1ASelector};
TableIEven = 1; TableIOdd = -1;

Gauge[[1]] = {G10, SO[10], SOGUT, g10, False, TableIEven, 0};
Gauge[[2]] = {GV, U[1], vprime, gV, False, TableIEven, 0};

SuperFields[[1]] = {Psi16a, 1, psi16a, 16, 1, TableIEven, 4};
SuperFields[[2]] = {Psi10a, 1, psi10a, 10, -2, TableIEven, 4};
SuperFields[[3]] = {Psi1a, 1, psi1a, 1, 4, TableIEven, 4};
SuperFields[[4]] = {Psi16b, 1, psi16b, 16, 1, TableIEven, 3};
SuperFields[[5]] = {Psi10b, 1, psi10b, 10, -2, TableIEven, 3};
SuperFields[[6]] = {Psi1b, 1, psi1b, 1, 4, TableIEven, 3};
SuperFields[[7]] = {Psi16c, 1, psi16c, 16, 1, TableIEven, 1};
SuperFields[[8]] = {Psi10c, 1, psi10c, 10, -2, TableIEven, 1};
SuperFields[[9]] = {Psi1c, 1, psi1c, 1, 4, TableIEven, 1};
SuperFields[[10]] = {Phi, 1, phi16, 16, 1, TableIOdd, 0};
SuperFields[[11]] = {CHiggs, 1, c16, 16, 1, TableIEven, -2};
SuperFields[[12]] = {PhiPrime, 2, phip16, 16, 1, TableIOdd, 5};
SuperFields[[13]] = {PhiBar, 1, phib16, -16, -1, TableIOdd, -1};
SuperFields[[14]] = {CBar, 1, cb16, -16, -1, TableIEven, -2};
SuperFields[[15]] = {PhiBarPrime, 2, phibp16, -16, -1, TableIOdd, 4};
SuperFields[[16]] = {Theta, 1, theta, 1, 0, TableIEven, -1};
SuperFields[[17]] = {ZBar, 2, zb, 1, 0, TableIEven, -1};
SuperFields[[18]] = {Z, 1, z, 1, 0, TableIOdd, -4};
SuperFields[[19]] = {SPrime, 1, sp, 1, 0, TableIEven, 8};

V23SourceBoundary = <|
  "PrimarySource" -> "arXiv:hep-ph/0304293",
  "PublishedFieldRows" -> 19,
  "AnomalousU1AGaugeDynamicsEncoded" -> False,
  "NormalizedComponentTensorsLanded" -> False,
  "OptionalKSVZEncodedAsSuperFields" -> False,
  "SuperPotentialEncoded" -> False
|>;

V23OptionalKSVZ = <|"Fields" -> {K10, PQ, PQBar, YPQ}, "U1ACompatibilityLanded" -> False|>;

SuperPotential = 0;
NameOfStates = {GaugeES};
