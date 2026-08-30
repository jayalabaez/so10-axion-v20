# Exact physical-SM G8 identifiability frontier v20

Status: `EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_CLOSED__PHYSICAL_RELEASE_AUTHORITATIVE_G8_OPEN`

## Outcome

The canonical G8 acceptance contract is now audited against the corrected physical-SM G6/G7 artifacts.  An exact positive vector-scale family changes a nonzero gauge-mediated lifetime as lambda^4 and crosses any finite limit while preserving the normalized spectrum.  Fifty complex flavour entries, the triplet pole matrix and relative interference phases are also unfixed.  Therefore the current repository data do not identify a unique lifetime or uncertainty distribution; physical, release and authoritative G8 remain false.  No new laboratory measurement is required merely to complete the missing theory calculations.

## Exact finite-limit crossing

For `M_X -> lambda M_X` at fixed dimensionless data,
`C -> lambda^-2 C`, `Gamma -> lambda^-4 Gamma`, and
`tau -> lambda^4 tau`.

- `lambda=1/2`: margin `1/16`
- `lambda=2`: margin `16`

The 101-case exact audit covers cases `0..100`.

## Canonical acceptance

- criterion_1: `False` - all gauge and scalar mediators are included with physical pole masses (absolute scalar/vector/fermion pole spectrum and physical triplet matrix are open)
- criterion_2: `False` - mass-basis Wilson coefficients are matched and run in a declared scheme (complete Wilson matching, anomalous dimensions and full RGE trajectory are open)
- criterion_3: `False` - the flavour/Clebsch solution is unique or its fitted covariance distribution is propagated (50 complex flavour entries and their fitted covariance/distribution are absent)
- criterion_4: `False` - gauge-scalar interference phases are fixed by the same physical vacuum and flavour solution (the physical vacuum does not yet fix gauge-scalar relative phases)
- criterion_5: `False` - every reported channel is compared with a versioned experimental-limit and lattice-input ledger (only one repository-frozen 2020 channel limit is represented)

## Missing inputs

### continuous_boundary_values_or_distributions

- absolute breaking scales and g10/gX with covariance
- the complete 51-real scalar tensor and dimensionful renormalized boundary data
- ten flavour tensors (50 complex entries before flavour quotients) fitted to low-energy data with covariance
- matching scales and correlated nuisance parameters
- physical CP/interference phases fixed by the same vacuum and flavour solution

### derivable_but_not_yet_derived

- source-algebra global physical-SM vacuum and stage-resolved Hessians
- source-exact scalar/vector/fermion tree matrices at every breaking stage
- self-energy pole equations in a declared tadpole/VEV and MS-bar scheme
- complete scalar and fermion thresholds including finite terms
- full two-loop gauge/Yukawa/scalar/dimensionful flow and required EFT mixing
- mass-basis gauge and scalar baryon-violating Wilson coefficients and their running
- second independent full RGE/matching replay

### measured_or_lattice_inputs_to_freeze_with_covariance

- low-energy gauge couplings, fermion masses, CKM and neutrino observables
- channel-specific lattice-QCD hadronic matrix elements
- a versioned all-channel experimental lifetime-limit ledger

### software_environment_not_laboratory

- hash-bound genuine SARAH/Wolfram execution attestation required upstream

### new_laboratory_measurement_required_for_theory_gate

- none

Checks: `20`; failures: `0`.

Core SHA256: `029dfd8b707825742c85b6d223a54ee964c76cf519496c5d5da28a7cad407fd5`
