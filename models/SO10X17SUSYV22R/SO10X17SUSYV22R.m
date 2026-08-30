(* ==================================================================== *)
(* Active V22R source completion of SO10X17SUSYV22.                   *)
(* Exact scope: 33 unchanged fields and 108 holomorphic base sectors *)
(* through field degree four, selected by Z28R x Z2S.                *)
(* The 265 SO(10)/flavour components are counted but their tensor     *)
(* contractions and Clebsches are NOT encoded in SuperPotential.      *)
(* ==================================================================== *)

Off[General::spell];

Model`Name = "SO10X17SUSYV22R";
Model`NameLaTeX = "SUSY SO(10) x U(1)_X V22R exact base-sector completion";
Model`Authors = "SO10 axion V22R verified completion";
Model`Date = "2026-08-19";

Global[[1]] = {Z[2], RParity};
Global[[2]] = {Z[17], Z17};
Global[[3]] = {Z[2], Z2S};
Global[[4]] = {U[1], RSymmetry};
RpM = {-1, -1, 1};
RpP = {1, 1, -1};
Z2SEven = 1;
Z2SOdd = -1;

(* The continuous RSymmetry slot is an integer lift used by SARAH.   *)
(* It is faithful only on the frozen degree<=4 census. At higher     *)
(* degree, finite Z28R data and the Python/JSON ledger are binding.  *)
(* No physical continuous U(1)R is declared; finite Z28R has W=2.   *)
V22RFiniteSymmetry = <|"RGroup" -> "Z28R", "ROrder" -> 28, "WCharge" -> 2, "Selector" -> "Z2S"|>;
V22ROperatorCatalogueCore = "0be5be830a3c8180224c3818870a3698eb111bb9260df0a2316ab7c1d5a3be70";

Gauge[[1]] = {G10, SO[10], SOGUT, g10, False, RpM, 1, Z2SEven, {0,1,0}};
Gauge[[2]] = {GX, U[1], xcharge, gX, False, RpM, 1, Z2SEven, {0,1,0}};

SuperFields[[1]] = {F, 3, f16, 16, 1, RpM, Exp[2*Pi*I*1/17], Z2SEven, {1,1,0}};
SuperFields[[2]] = {P, 1, p16, 16, 1, RpM, Exp[2*Pi*I*1/17], Z2SEven, {1,1,0}};
SuperFields[[3]] = {R, 1, r16, 16, 1, RpM, Exp[2*Pi*I*1/17], Z2SEven, {1,1,0}};
SuperFields[[4]] = {SpecS, 5, s16, 16, 2, RpM, Exp[2*Pi*I*2/17], Z2SEven, {9,9,8}};
SuperFields[[5]] = {SpecB, 5, b16bar, -16, -6, RpM, Exp[2*Pi*I*11/17], Z2SEven, {25,25,24}};
SuperFields[[6]] = {Q, 1, q16, 16, 14, RpM, Exp[2*Pi*I*14/17], Z2SEven, {9,9,8}};
SuperFields[[7]] = {Pbar, 1, pbar16, -16, 16, RpM, Exp[2*Pi*I*16/17], Z2SEven, {-23,-23,-24}};
SuperFields[[8]] = {Qbar, 1, qbar16, -16, 3, RpM, Exp[2*Pi*I*3/17], Z2SEven, {-31,-31,-32}};
SuperFields[[9]] = {Rbar, 1, rbar16, -16, -18, RpM, Exp[2*Pi*I*16/17], Z2SEven, {25,25,24}};
SuperFields[[10]] = {Phi210, 1, phi210, 210, 0, RpP, 1, Z2SEven, {0,0,-1}};
SuperFields[[11]] = {DeltaB, 1, deltaB, -126, -2, RpP, Exp[2*Pi*I*15/17], Z2SOdd, {0,0,-1}};
SuperFields[[12]] = {Delta, 1, delta, 126, 2, RpP, Exp[2*Pi*I*2/17], Z2SEven, {2,2,1}};
SuperFields[[13]] = {DeltaB2, 1, deltaB2, -126, -2, RpP, Exp[2*Pi*I*15/17], Z2SEven, {10,10,9}};
SuperFields[[14]] = {Delta2, 1, delta2, 126, 2, RpP, Exp[2*Pi*I*2/17], Z2SOdd, {-8,-8,-9}};
SuperFields[[15]] = {H10m, 1, h10m, 10, -2, RpP, Exp[2*Pi*I*15/17], Z2SEven, {0,0,-1}};
SuperFields[[16]] = {H10p, 1, h10p, 10, 2, RpP, Exp[2*Pi*I*2/17], Z2SEven, {-8,-8,-9}};
SuperFields[[17]] = {T120m, 1, t120m, 120, -2, RpP, Exp[2*Pi*I*15/17], Z2SEven, {0,0,-1}};
SuperFields[[18]] = {T120p, 1, t120p, 120, 2, RpP, Exp[2*Pi*I*2/17], Z2SEven, {-8,-8,-9}};
SuperFields[[19]] = {Splus, 1, splus, 1, 4, RpP, Exp[2*Pi*I*4/17], Z2SEven, {-32,-32,-33}};
SuperFields[[20]] = {Sminus, 1, sminus, 1, -4, RpP, Exp[2*Pi*I*13/17], Z2SEven, {32,32,31}};
SuperFields[[21]] = {Phi17p, 1, phi17p, 1, 17, RpP, 1, Z2SEven, {-24,-24,-25}};
SuperFields[[22]] = {Phi17m, 1, phi17m, 1, -17, RpP, 1, Z2SEven, {24,24,23}};
SuperFields[[23]] = {NX, 1, nx, 1, 0, RpP, 1, Z2SEven, {2,2,1}};
SuperFields[[24]] = {NS, 1, ns, 1, 0, RpP, 1, Z2SEven, {2,2,1}};
SuperFields[[25]] = {XMP, 1, xmp, 1, 0, RpP, 1, Z2SOdd, {0,0,-1}};
SuperFields[[26]] = {C16, 1, c16, 16, 0, RpP, 1, Z2SEven, {24,24,23}};
SuperFields[[27]] = {C16bar, 1, c16bar, -16, 0, RpP, 1, Z2SEven, {-24,-24,-25}};
SuperFields[[28]] = {Nphi, 1, nphi, 1, 0, RpP, 1, Z2SEven, {2,2,1}};
SuperFields[[29]] = {Z0, 1, z0, 1, 0, RpP, 1, Z2SOdd, {20,20,19}};
SuperFields[[30]] = {NC, 1, nc, 1, 0, RpP, 1, Z2SEven, {2,2,1}};
SuperFields[[31]] = {NMP, 1, nmp, 1, 0, RpP, 1, Z2SEven, {2,2,1}};
SuperFields[[32]] = {Z1, 1, z1, 1, 0, RpP, 1, Z2SEven, {12,12,11}};
SuperFields[[33]] = {Z2, 1, z2, 1, 0, RpP, 1, Z2SEven, {12,12,11}};

(* Complete machine-readable degree<=4 base-sector catalogue.       *)
(* Components gives the exact SO(10) x flavour invariant count.     *)
V22RBaseSectorCatalogue = {
  <|"ID" -> "V22R-S001", "Fields" -> {NX}, "Degree" -> 1, "Components" -> 1, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"linearNX"}|>,
  <|"ID" -> "V22R-S002", "Fields" -> {NS}, "Degree" -> 1, "Components" -> 1, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"linearNS"}|>,
  <|"ID" -> "V22R-S003", "Fields" -> {Nphi}, "Degree" -> 1, "Components" -> 1, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"linearNphi"}|>,
  <|"ID" -> "V22R-S004", "Fields" -> {NC}, "Degree" -> 1, "Components" -> 1, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"linearNC"}|>,
  <|"ID" -> "V22R-S005", "Fields" -> {NMP}, "Degree" -> 1, "Components" -> 1, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"linearNMP"}|>,
  <|"ID" -> "V22R-S006", "Fields" -> {F, F, H10m}, "Degree" -> 3, "Components" -> 6, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"Y10"}|>,
  <|"ID" -> "V22R-S007", "Fields" -> {F, F, T120m}, "Degree" -> 3, "Components" -> 3, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"Y120"}|>,
  <|"ID" -> "V22R-S008", "Fields" -> {F, P, H10m}, "Degree" -> 3, "Components" -> 3, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"lambdaP"}|>,
  <|"ID" -> "V22R-S009", "Fields" -> {F, P, T120m}, "Degree" -> 3, "Components" -> 3, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S010", "Fields" -> {F, R, H10m}, "Degree" -> 3, "Components" -> 3, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"lambdaR"}|>,
  <|"ID" -> "V22R-S011", "Fields" -> {F, R, T120m}, "Degree" -> 3, "Components" -> 3, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S012", "Fields" -> {F, Pbar, Phi17m}, "Degree" -> 3, "Components" -> 3, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S013", "Fields" -> {F, Qbar, Sminus}, "Degree" -> 3, "Components" -> 3, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"lambdaQB"}|>,
  <|"ID" -> "V22R-S014", "Fields" -> {F, Rbar, Phi17p}, "Degree" -> 3, "Components" -> 3, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S015", "Fields" -> {P, P, H10m}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S016", "Fields" -> {P, R, H10m}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S017", "Fields" -> {P, R, T120m}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S018", "Fields" -> {P, Pbar, Phi17m}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"yP"}|>,
  <|"ID" -> "V22R-S019", "Fields" -> {P, Qbar, Sminus}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S020", "Fields" -> {P, Rbar, Phi17p}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S021", "Fields" -> {R, R, H10m}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S022", "Fields" -> {R, Pbar, Phi17m}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S023", "Fields" -> {R, Qbar, Sminus}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S024", "Fields" -> {R, Rbar, Phi17p}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"yR"}|>,
  <|"ID" -> "V22R-S025", "Fields" -> {SpecS, SpecB, Splus}, "Degree" -> 3, "Components" -> 25, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"ys"}|>,
  <|"ID" -> "V22R-S026", "Fields" -> {Q, Qbar, Phi17m}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"yQ"}|>,
  <|"ID" -> "V22R-S027", "Fields" -> {Q, Rbar, Splus}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"lambdaQR"}|>,
  <|"ID" -> "V22R-S028", "Fields" -> {Phi210, Phi210, NX}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S029", "Fields" -> {Phi210, Phi210, NS}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S030", "Fields" -> {Phi210, Phi210, Nphi}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"kappaPhi"}|>,
  <|"ID" -> "V22R-S031", "Fields" -> {Phi210, Phi210, NC}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S032", "Fields" -> {Phi210, Phi210, NMP}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S033", "Fields" -> {Phi210, Delta, H10m}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"gammaH"}|>,
  <|"ID" -> "V22R-S034", "Fields" -> {Phi210, Delta, T120m}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"gammaT"}|>,
  <|"ID" -> "V22R-S035", "Fields" -> {Phi210, DeltaB2, H10p}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"gammaHb2"}|>,
  <|"ID" -> "V22R-S036", "Fields" -> {Phi210, DeltaB2, T120p}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"gammaTb2"}|>,
  <|"ID" -> "V22R-S037", "Fields" -> {DeltaB, Delta, XMP}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"rho1"}|>,
  <|"ID" -> "V22R-S038", "Fields" -> {DeltaB2, Delta2, XMP}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"rho2"}|>,
  <|"ID" -> "V22R-S039", "Fields" -> {Splus, Sminus, NX}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S040", "Fields" -> {Splus, Sminus, NS}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"kappaS"}|>,
  <|"ID" -> "V22R-S041", "Fields" -> {Splus, Sminus, Nphi}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S042", "Fields" -> {Splus, Sminus, NC}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S043", "Fields" -> {Splus, Sminus, NMP}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S044", "Fields" -> {Phi17p, Phi17m, NX}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"kappaX"}|>,
  <|"ID" -> "V22R-S045", "Fields" -> {Phi17p, Phi17m, NS}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S046", "Fields" -> {Phi17p, Phi17m, Nphi}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S047", "Fields" -> {Phi17p, Phi17m, NC}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S048", "Fields" -> {Phi17p, Phi17m, NMP}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S049", "Fields" -> {NX, XMP, XMP}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S050", "Fields" -> {NX, C16, C16bar}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S051", "Fields" -> {NS, XMP, XMP}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S052", "Fields" -> {NS, C16, C16bar}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S053", "Fields" -> {XMP, XMP, Nphi}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S054", "Fields" -> {XMP, XMP, NC}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S055", "Fields" -> {XMP, XMP, NMP}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"kappaMP"}|>,
  <|"ID" -> "V22R-S056", "Fields" -> {C16, C16bar, Nphi}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S057", "Fields" -> {C16, C16bar, NC}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"kappaC"}|>,
  <|"ID" -> "V22R-S058", "Fields" -> {C16, C16bar, NMP}, "Degree" -> 3, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S059", "Fields" -> {F, F, Phi210, H10m}, "Degree" -> 4, "Components" -> 9, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S060", "Fields" -> {F, F, Phi210, T120m}, "Degree" -> 4, "Components" -> 18, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S061", "Fields" -> {F, F, DeltaB, XMP}, "Degree" -> 4, "Components" -> 6, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"Y126eff"}|>,
  <|"ID" -> "V22R-S062", "Fields" -> {F, P, Phi210, H10m}, "Degree" -> 4, "Components" -> 6, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S063", "Fields" -> {F, P, Phi210, T120m}, "Degree" -> 4, "Components" -> 12, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S064", "Fields" -> {F, P, DeltaB, XMP}, "Degree" -> 4, "Components" -> 3, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S065", "Fields" -> {F, R, Phi210, H10m}, "Degree" -> 4, "Components" -> 6, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S066", "Fields" -> {F, R, Phi210, T120m}, "Degree" -> 4, "Components" -> 12, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S067", "Fields" -> {F, R, DeltaB, XMP}, "Degree" -> 4, "Components" -> 3, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S068", "Fields" -> {F, Pbar, Phi210, Phi17m}, "Degree" -> 4, "Components" -> 3, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S069", "Fields" -> {F, Qbar, Phi210, Sminus}, "Degree" -> 4, "Components" -> 3, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S070", "Fields" -> {F, Rbar, Phi210, Phi17p}, "Degree" -> 4, "Components" -> 3, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S071", "Fields" -> {P, P, Phi210, H10m}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S072", "Fields" -> {P, P, Phi210, T120m}, "Degree" -> 4, "Components" -> 2, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S073", "Fields" -> {P, P, DeltaB, XMP}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S074", "Fields" -> {P, R, Phi210, H10m}, "Degree" -> 4, "Components" -> 2, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S075", "Fields" -> {P, R, Phi210, T120m}, "Degree" -> 4, "Components" -> 4, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S076", "Fields" -> {P, R, DeltaB, XMP}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S077", "Fields" -> {P, Pbar, Phi210, Phi17m}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S078", "Fields" -> {P, Qbar, Phi210, Sminus}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S079", "Fields" -> {P, Rbar, Phi210, Phi17p}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S080", "Fields" -> {R, R, Phi210, H10m}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S081", "Fields" -> {R, R, Phi210, T120m}, "Degree" -> 4, "Components" -> 2, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S082", "Fields" -> {R, R, DeltaB, XMP}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S083", "Fields" -> {R, Pbar, Phi210, Phi17m}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S084", "Fields" -> {R, Qbar, Phi210, Sminus}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S085", "Fields" -> {R, Rbar, Phi210, Phi17p}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S086", "Fields" -> {SpecS, SpecB, Phi210, Splus}, "Degree" -> 4, "Components" -> 25, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S087", "Fields" -> {Q, Qbar, Phi210, Phi17m}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S088", "Fields" -> {Q, Rbar, Phi210, Splus}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S089", "Fields" -> {Phi210, Phi210, Phi210, NX}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S090", "Fields" -> {Phi210, Phi210, Phi210, NS}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S091", "Fields" -> {Phi210, Phi210, Phi210, Nphi}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"zetaPhi"}|>,
  <|"ID" -> "V22R-S092", "Fields" -> {Phi210, Phi210, Phi210, NC}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S093", "Fields" -> {Phi210, Phi210, Phi210, NMP}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S094", "Fields" -> {Phi210, Phi210, Delta, H10m}, "Degree" -> 4, "Components" -> 2, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S095", "Fields" -> {Phi210, Phi210, Delta, T120m}, "Degree" -> 4, "Components" -> 4, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S096", "Fields" -> {Phi210, Phi210, DeltaB2, H10p}, "Degree" -> 4, "Components" -> 2, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S097", "Fields" -> {Phi210, Phi210, DeltaB2, T120p}, "Degree" -> 4, "Components" -> 4, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S098", "Fields" -> {Phi210, DeltaB, Delta, XMP}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S099", "Fields" -> {Phi210, DeltaB2, Delta2, XMP}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S100", "Fields" -> {Phi210, NX, C16, C16bar}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S101", "Fields" -> {Phi210, NS, C16, C16bar}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S102", "Fields" -> {Phi210, C16, C16bar, Nphi}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S103", "Fields" -> {Phi210, C16, C16bar, NC}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "retained_v22_29", "V22Couplings" -> {"xiC"}|>,
  <|"ID" -> "V22R-S104", "Fields" -> {Phi210, C16, C16bar, NMP}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S105", "Fields" -> {Delta, H10m, C16, C16bar}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S106", "Fields" -> {Delta, T120m, C16, C16bar}, "Degree" -> 4, "Components" -> 2, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S107", "Fields" -> {DeltaB2, H10p, C16, C16bar}, "Degree" -> 4, "Components" -> 1, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>,
  <|"ID" -> "V22R-S108", "Fields" -> {DeltaB2, T120p, C16, C16bar}, "Degree" -> 4, "Components" -> 2, "Provenance" -> "abelian_forced_completion_79", "V22Couplings" -> {}|>
};

(* No component polynomial is asserted.  Downstream G1/G2 work must *)
(* source-land normalized invariant tensors before replacing zero.   *)
SuperPotential = 0;
NameOfStates = {GaugeES};
