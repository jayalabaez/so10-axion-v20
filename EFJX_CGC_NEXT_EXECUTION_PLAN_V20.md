# Next executable calculation: full non-SUSY scalar potential and Hessian

## Source correction

The former E/F/J/X Clebsch-normalization plan is retired.

Aulakh Appendix E/F/J/X are mixed chiral-gauge fermion/gaugino matrices. Their `g` is the SO(10) gauge coupling, not the superpotential `gamma` coupling. They cannot be used to define a non-supersymmetric scalar `lambda4` normalization or threshold.

The obsolete targets are forbidden:

- no E/F/J/X slot matching for scalar closure;
- no `gamma_eff/lambda4` extraction from E/F/J/X;
- no resurrection of the withdrawn `8.8e29` bound;
- no `EFJX_CGC_NORMALIZATION_INPUT_V20.json` closure artifact.

## Completed direct tensor work

The direct scalar invariant

`lambda4 S H_i Phi_jklm Sigmabar_ijklm / 4! + h.c.`

has been implemented as a canonically normalized `10 x 126` tensor map using the complete `(P,A,W)` singlet basis.

Its analytic singular branches are:

1. `sqrt((P+A/sqrt(3))^2+4 W^2/3)`, multiplicity 3;
2. `abs(P-A/sqrt(3))`, multiplicity 3;
3. `abs(A+W/sqrt(2))`, multiplicity 2;
4. `abs(A-W/sqrt(2))`, multiplicity 2.

The independent Aulakh VEV dictionary is

`P=p`, `A=sqrt(3)a`, `W=sqrt(6)omega`,

and the direct spectrum matches the genuine `gamma`-dependent chiral triplet/doublet Clebsch magnitudes.

## Completed scoped portal M² insertion

Repository Aulakh-style VEVs are traced into the canonical `(P,A,W)` dictionary and the portal block

`M^2_{H–Σ̄} = lambda4 v_S T_Phi`

is inserted into a scoped non-SUSY `10 x 126` mass-squared sector (`direct_phi_h_sigmabar_portal_m2_block_v20.py`).

This closes the VEV-dictionary trace and the *scoped* portal bilinear insertion only. It does **not** close the complete invariant ring, full component projection, global Hessian, or issue #86.

## Completed exact portal Schur gate

The holomorphic block `B = lambda4 vS T_Phi` is embedded in the exact 272-real-mode Hessian for `(Re H, Im H, Re Σ̄, Im Σ̄)` with positivity criterion

`sigma_max(A^{-1/2} B C^{-1/2}) < 1`.

Diagonal `A = M²_H` and `C = M²_Σ̄` remain open inputs.

## Completed diagonal-channel inventory scaffold

Classic Kronecker channels that can source those diagonals are inventoried and PQ/X/Z17-filtered in

`diagonal_h10_sigmabar_m2_channel_inventory_v20.py`:

- `210×210`: 45, 54, 210, 1050 (+ cubics);
- `210×126`: 10, 120, 320, 126;
- `126` quartics: 54, 1050, 4125;
- `10_H` via isotropic and 54 projections.

Cartesian second-derivative slots are recorded as `OPEN_AWAITING_CG`. Index CG tensors are **not** invented.

## Completed isotropic + 54 partial Schur A/C fill

`diagonal_h10_sigmabar_m2_isotropic_54_slots_v20.py` fills inventory slots that
already have repository support:

- isotropic H10 / Σ̄ soft-norm seeds;
- 210-norm portals into H10 and Σ̄.

The former isotropic `54-locking` mass seed that used `H10_eff=M_I` is
**withdrawn** (PR #97): `10_H` has no PS/SM singlet, and
`P_54(Delta_R,Delta_R)=0` on the selected vacuum. Selected-vacuum `lambda4`
radial/phase amplitudes are likewise null (`T_Phi Delta_R=0`). Partial
positive diagonals therefore come only from soft/norm and 210-norm seeds.
Channels 120/320/1050/4125 remain open.

## Completed selected-vacuum phase-Hessian revalidation

Root `A_54=0` and κ-only multi-operator phase Hessian consumers have been
rewritten against the exact nulls.

## Corrected: the "extra flat phase" was a gauge Goldstone

The unquotiented reduced Hessian on `(φ_Δ,φ_10,φ_S)` has rank one and two
nulls when `A_κ>0`. One null is the eaten Pati–Salam `Z'_R/B-L` orbit
`q=(1,0,0)`. After that gauge quotient the physical sector `(φ_10,φ_S)` has

- one massive CP-odd eigenvalue `5 A_κ`;
- exactly one physical null `(1,-2)`, the PQ axion;
- **no** additional physical non-axion flat phase.

All-orders: B−L neutrality forces `d=0` and PQ/Z17 then forces every nonzero
selected-vacuum polynomial phase vector parallel to `κ`. Finite dim-6/7/8
zeros corroborate this identity; they are not required to prove physical
phase closure of the reduced sector.

Core pre-quotient consumers (`multi_operator_phase_hessian`,
`gauge_fixing_goldstone_eating`, `phase_operator_independence_audit`) and
UV/CP descendants (`uv_cp_phases_from_potential`, `component_lift_210_126_10`,
`uv_delta_i_cp_reality_principle`) are source-rewritten against the Z' quotient.

## Completed physical 54-channel Hessian at hEW=174 GeV

`physical_54_component_hessian_at_hew_v20.py` differentiates the charge-allowed
54-locking operator on the physical electroweak background:

- `P54(hEW,hEW)` is nonzero;
- selected-vacuum amplitude `⟨P54(hEW,hEW), P54(Δ_R,Δ_R)⟩ = 0`;
- `OPEN_H10_54` remains exact zero from `P54(Δ_R,Δ_R)=0`;
- `OPEN_126_54_LOCKING` is a holomorphic `ΣΣ` kernel on the Δ_R eigenspace,
  suppressed by `(hEW/M_I)^2`, and is **not** a positive Hermitian Schur C seed.

## Correct next goal

Continue the full component scalar mass-squared matrix and global
`hEW=174 GeV` vacuum: fill remaining diagonal channels that do not invent
120/320/1050/4125 CG (e.g. `OPEN_MIXED_126`), then root-by-root removal of
all 33 Goldstones, stationarity, boundedness, thresholds, and τ_p. Do not
reopen a reduced-sector phase hunt.

## Executable sequence

1. **Complete invariant ring**
   - Enumerate every charge-allowed independent scalar operator through the declared engineering dimension.
   - Prove linear independence and record Hermitian-conjugation conventions.
   - Transcribe missing CG tensors (especially 120, 320, 1050, 4125) into the Cartesian basis.
   - Prefer operators with nonzero tensor projection on the actual `(Delta_R,hEW,S,Phi)` vacuum for phase locking.

2. **Full component projection**
   - Project every invariant into canonical Pati-Salam and Standard Model component fields.
   - The direct `lambda4 vS T_Phi` off-diagonal block is already available as a scoped insertion; extend it to the full projected potential.
   - Fill diagonal `H10` and `Sigmabar126` mass-squared matrices from charge-allowed channels.
   - Do not import SUSY fermion/gaugino matrices as scalar masses.

3. **Stationarity and hierarchy**
   - Solve all stationarity equations with `hEW=174 GeV`.
   - Trace every numerical VEV and coupling to the canonical `(P,A,W)` convention.
   - Demonstrate a technically stable hierarchy mechanism.

4. **Gauge-projected component Hessian**
   - Construct the complete real scalar `M^2` matrix.
   - Remove exactly 33 gauge Goldstones.
   - Require every remaining eigenvalue to be positive.

5. **Global vacuum and boundedness**
   - Check all enumerated competing extrema.
   - Prove the target vacuum is lower.
   - Apply a boundedness certificate to the complete potential.

6. **Physical thresholds and downstream predictions**
   - Emit physical triplet, doublet and singlet masses with multiplicities and SM quantum numbers.
   - Only then run full two-loop threshold evolution and calculate proton decay.

## Required closure artifacts

- `FULL_MIXED_REP_INVARIANT_RING_V20.json`
- `FULL_TENSOR_PROJECTED_POTENTIAL_V20.json`
- `FULL_NONSUSY_VACUUM_HESSIAN_V20.json`

The direct tensor, scoped portal block, exact Schur gate, classic diagonal-channel inventory, corrected isotropic/norm A/C seeds, and selected-vacuum A54/λ₄ null revalidation of the reduced phase Hessian are in place. Missing CG transcription and the complete scalar theory remain open.
