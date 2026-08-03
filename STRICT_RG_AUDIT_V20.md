# Strict RG / threshold / FCNC audit — v20

**Status:** `PASS`

## Classification

- full_two_loop_so10_210_yukawa_system: **OPEN**
- conditional_na62_yQ_survival_boundary: **SOLVED_ON_ONE_FIXED_PORTAL_RAY**
- full_heavy_singular_spectrum: **COMPUTED_ON_THE_FIXED_RAY**
- bare_D_mass_interpretation: **NOT_A_PHYSICAL_EIGENMASS**
- piecewise_component_threshold_matching: **OPEN**
- pati_salam_one_loop_yukawa_layer: **SOLVED_ON_MI_TO_MGUT**
- clebsch_threshold_matching_chain: **IMPLEMENTED_WITH_FACTOR_MINUS_THREE**
- published_two_loop_SO10_210_contractions: **OPEN**
- unique_Cf_from_charges_alone: **IMPOSSIBLE_BY_THEOREM**
- conditional_unique_Cf_under_named_axioms: **DERIVED**
- unique_Cf_under_vacuum_alignment_principle: **DERIVED**
- exact_fcnc_pointwise_ul_likelihood: **IMPLEMENTED_ON_VENDORED_ANCHORS**
- full_151_point_correlated_NA62_likelihood: **OPEN**
- portal_sector_posterior: **DISCRETE_GRID_ON_CONDITIONAL_SECTOR**
- full_portal_yukawa_posterior: **OPEN**
- complex_F1_F2_orientation_map: **SCANNED_AT_FIXED_NORM_AND_ORDERED_HEAVY_YQ**
- na62_orientation_dependence: **EXCLUDED_AND_SURVIVING_ORIENTATIONS_FOUND**
- twist_orientation_dependence: **ALL_5856_SAMPLED_ORIENTATIONS_BELOW_PUBLISHED_BENCHMARKS**
- orientation_grid_fraction: **NOT_A_PROBABILITY_OR_UV_POSTERIOR**
- full_complex_three_family_orientation: **OPEN**
- full_portal_parameter_space: **OPEN**
- lab_37ghz_limit_comparison: **EXECUTED__NO_DETECTION**
- whole_model_exclusion: **NOT_ESTABLISHED**

## Orientation summary

```json
{
  "n_grid_points": 5856,
  "n_NA62_excluded": 5664,
  "n_NA62_surviving": 192,
  "n_TWIST_excluded": 0,
  "min_NA62_ratio": 1.3873975425444243e-29,
  "max_NA62_ratio": 822.2130400577903,
  "max_TWIST_ratio": 0.0052556334376686956,
  "grid_fraction_is_probability": false
}
```

## Required for closure

- validated type-II matrix beta functions and running VEVs
- explicit component-level Pati-Salam and EW threshold matching of PQ currents
- reference-derived full two-loop SO(10)+210 representation contractions (SARAH/PyR@TE)
- component-specific left/right PQ currents after all thresholds
- full complex F1-F2-F3 orientation and all portal magnitudes/phases
- full UV portal-Yukawa prior/posterior beyond the conditional sector grid
- full 151-point correlated NA62 likelihood and continuous TWIST A likelihood
- real 36.6-37.6 GHz conversion data under the all-DM assumption
- a UV principle that uniquely fixes the full scalar-quartic landscape without extra axioms

## Verdict

Blueprint certification modules are fail-closed: vacuum alignment yields unique C_f only under a named principle; the piecewise Yukawa chain applies the −3 lepton Clebsch; exact FCNC BRs enter a pointwise UL likelihood on vendored anchors. Published SO(10)+210 two-loop contractions, full correlated NA62, and unconditional unique C_f remain open.
