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
- full_complex_three_family_orientation: **HAAR_S5_LOW_DISCREPANCY_SAMPLE_AT_FIXED_NORM**
- chosen_geometric_NA62_excluded_fraction: **0.9940185546875**
- geometric_fraction_interpretation: **NOT_A_UV_PROBABILITY_OR_POSTERIOR**
- na62_orientation_dependence: **EXCLUDED_AND_SURVIVING_ORIENTATIONS_FOUND**
- twist_orientation_dependence: **ALL_16384_SAMPLED_ORIENTATIONS_BELOW_PUBLISHED_BENCHMARKS**
- joint_orientation_and_portal_magnitudes: **OPEN**
- full_portal_parameter_space: **OPEN**
- lab_37ghz_limit_comparison: **EXECUTED__NO_DETECTION**
- whole_model_exclusion: **NOT_ESTABLISHED**

## Orientation summary

```json
{
  "F1_F2_plane": {
    "n_grid_points": 5856,
    "n_NA62_excluded": 5664,
    "n_NA62_surviving": 192,
    "min_NA62_ratio": 1.3873975425444243e-29,
    "max_NA62_ratio": 822.2130400577903,
    "grid_fraction_is_probability": false
  },
  "full_complex_S5": {
    "n_total_points": 16384,
    "n_NA62_excluded": 16286,
    "n_NA62_surviving": 98,
    "n_TWIST_excluded": 0,
    "chosen_measure_excluded_fraction": 0.9940185546875,
    "replicate_min": 0.99169921875,
    "replicate_max": 0.99658203125,
    "sampled_min_NA62_ratio": 0.0008303658272651671,
    "sampled_max_NA62_ratio": 820.9303432095173,
    "sampled_max_TWIST_ratio": 0.005664625615732507,
    "geometric_fraction_is_uv_probability": false
  }
}
```

## Required for closure

- validated type-II matrix beta functions and running VEVs
- explicit component-level Pati-Salam and EW threshold matching of PQ currents
- reference-derived full two-loop SO(10)+210 representation contractions (SARAH/PyR@TE)
- component-specific left/right PQ currents after all thresholds
- joint scan of portal magnitudes/phases beyond the fixed-norm orientation sphere
- full UV portal-Yukawa prior/posterior beyond the conditional sector grid
- full 151-point correlated NA62 likelihood and continuous TWIST A likelihood
- real 36.6-37.6 GHz conversion data under the all-DM assumption
- a UV principle that uniquely fixes the full scalar-quartic landscape without extra axioms

## Verdict

The full complex three-family orientation sphere is sampled at fixed norm and ordered-heavy y_Q using an explicit rotationally invariant measure. Under that chosen geometric measure 16286/16384 samples exceed NA62, but 98 survive and exact survivor anchors exist; all sampled orientations remain below TWIST. The 0.9940186 fraction is not a UV probability. Blueprint certification modules remain fail-closed: vacuum alignment yields unique C_f only under a named principle; the piecewise Yukawa chain applies the −3 lepton Clebsch; exact FCNC BRs enter a pointwise UL likelihood on vendored anchors. Joint portal-magnitude inference, published SO(10)+210 two-loop contractions, full correlated NA62, and unconditional unique C_f remain open.
