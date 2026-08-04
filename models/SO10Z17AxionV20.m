(* =====================================================================
   SARAH model-file scaffold: SO(10)×Z17 axion candidate v20
   =====================================================================
   Purpose: complete field-content + charge ledger for a *live* SARAH run
   of the renormalizable 210^n + mixed 126/10/S sector.

   This repository does NOT claim a live Mathematica/SARAH execution unless
   an external probe finds `math`/`wolframscript` + SARAH and returns a dump.
   Coefficients used elsewhere still come from published MV/Dynkin formulas.

   Charges (v20 lock):
     10_H, 126bar_H : PQ = -2
     210_H          : PQ = 0
     S              : PQ = +4
     Phi17          : (X, PQ) = (17, 0)
   Forbidden: bare 10_H^2 (PQ); 10·126·S (SO(10) invariant absent at dim-3
   without 210). Legal dim-4 mix: 210·10·126·S.
   ===================================================================== *)

NameOfModel = "SO10Z17AxionV20";
GlobalSymmetry = {Z[17]};

(* --- Gauge --- *)
Gauge[[1]] = {G10, SO, 10, globalU1Charges -> {0}};

(* --- Scalars --- *)
(* Real 210 adjoint-like SO(10) tensor; PQ=0 *)
ScalarFields[[1]] = {
  Phi210, {210}, SO10Real, {0 (*PQ*), 0 (*X*)}
};
(* Complex 126bar, PQ=-2 *)
ScalarFields[[2]] = {
  Delta126bar, {126}, Complex, {-2, 0}
};
(* Complex 10, PQ=-2 *)
ScalarFields[[3]] = {
  H10, {10}, Complex, {-2, 0}
};
(* Complex SO(10) singlet S, PQ=+4 *)
ScalarFields[[4]] = {
  S, {1}, Complex, {4, 0}
};
(* Complex U(1)_X breaking singlet Phi17, X=17, PQ=0 *)
ScalarFields[[5]] = {
  Phi17, {1}, Complex, {0, 17}
};

(* --- Fermions --- *)
(* Three light 16 + decay-safe heavy 16 pairs entered via matter content *)
FermionFields[[1]] = {Psi16, {16}, 3 (*generations*), {0, 0}};

(* --- Superpotential / scalar potential operators (nonsusy: listed as V) ---
   SARAH nonsusy: encode as Potential terms with charge-allowed monomials.
   Pure 210^n: Hilbert H2=1, H3=2, H4=4 (see hilbert_210n_residual_certificate).
   Mixed: kappa * H10^2 S ; lam4 * Phi210 H10 Delta126bar S ;
          lambda_lock * Delta126bar^2 H10^2 S^2 / M_* ^2 (dim-6 locking).
*)

DEFINITION[EWSB][VEVs] = {
  {Phi210, 0, v210},   (* PS/GUT direction; detailed CG external *)
  {Delta126bar, 0, v126},
  {H10, 0, v10},
  {S, 0, vS},
  {Phi17, 0, vPhi}
};

(* Boundary conditions / soft terms: M_1/2 from stationarity matching upstream *)
SoftGauginoMass[G10] = M12;

(* End of scaffold — live SARAH must expand CG for 210^n and emit β dump. *)
