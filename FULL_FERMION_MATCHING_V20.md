# Full v20 fermion matching — C_e, C_p, C_n

**Status:** `UNIQUE_UNDER_STATED_ANSATZ__HADRONIC_UNCERTAINTY_REMAINS`

## Ansatz (required for uniqueness)

- Name: `manuscript_minimal_flavor_universal_unit_yukawa`
- Without this ansatz the charge-allowed Lagrangian does not fix unique C_e, C_p, C_n. With it, they are unique up to hadronic matching uncertainty on C_p, C_n.

## Unique values at v20 tanβ = 1.5

| Coefficient | Value |
|---|---:|
| C_e | `4.07239819e-02` |
| C_p | `-4.72579186e-01` |
| C_n | `6.60633484e-03` |
| g_ae | `5.60305081e-16` |
| g_ap | `-1.19387183e-11` |
| g_an | `1.67125194e-13` |
| max \|PQ shift\| | `1.595e-10` |
| TRGB margin | `232.0` |
| SN1987A amplitude margin | `98.1` |

## Portal-ratio robustness

- max \|ΔC_e\| in scan: `2.165e-10`
- max \|ΔC_p\| in scan: `1.371e-11`
- max \|ΔC_n\| in scan: `1.414e-10`

## Bound checks under ansatz

- `TRGB_conditional`: True
- `SN1987A_conditional`: True
- `universal_SN_fa`: True
- `portal_correction_below_hadronic_on_Cp`: True
- `three_light_families`: True
- `ansatz_fully_specified`: True
- `full_model_pass_without_ansatz`: None
- `full_model_pass_under_stated_ansatz`: True

## Still open without the ansatz

- Arbitrary generation-dependent λ_Q^{i}, λ_P^{iα}, λ_R^{iα}
- Extra charge-allowed portals (PR 10_H, Qbar R S†, …) as free matrices
- Correlated hadronic ΔC_p, ΔC_n beyond illustrative σ

## Verdict

Under the stated ansatz `manuscript_minimal_flavor_universal_unit_yukawa`, the v20 couplings are uniquely derived at tanβ=1.500: C_e=4.072398e-02, C_p=-4.725792e-01, C_n=6.606335e-03. Portal-induced shifts are |ΔC_p|=1.371e-13 (≪ illustrative hadronic σ=3.021e-02). Without that ansatz the fermion gap remains open. The 37 GHz photon benchmark is independent and still experimentally open.
