# V42 G7 Pati--Salam VEV epsilon audit

Status: `V42_G7_PS_PQ_EW_VEV_EPSILON_AUDIT__LOW_DEGREE_PROTECTION_EXACT__SELECTOR_ALLOWED_SIX_MATTER_DELTA_B_MINUS_ONE_WITNESS__G7_FAIL_CLOSED`

## Outcome

The V40 `Z9` selector still proves an all-order statement for the conventional
same-orientation `Q4` and `Qc4` epsilon source families: every declared PS,
PQ, electroweak, Theta, or conjugate VEV dressing has `Z9=0`, while the two
sources have residues `3` and `6`.  PS breaking does introduce genuine
low-degree precursors, `ThetaMinus Q3 Sbc H` and `ThetaPlus Qc3 Sc`, but each
has three R-odd matter fields and `Z4R=3`.  Since every declared VEV is
R-even, neither can become a W-charge-two or Kahler-charge-zero operator.

| Low-degree class | Z9 | Z4R | Component boundary |
|---|---:|---:|---|
| conventional_left_same_orientation_epsilon | 3 | 0 | actual MSSM-like DeltaB=+1, DeltaL=+1 four-matter epsilon source |
| conventional_right_same_orientation_epsilon | 6 | 0 | actual MSSM-like DeltaB=-1, DeltaL=-1 four-matter epsilon source |
| left_epsilon_one_PS_VEV_precursor | 0 | 3 | genuine PS-VEV precursor to a DeltaB=+1 source; not a rate calculation |
| right_epsilon_one_PS_VEV_precursor | 0 | 3 | genuine PS-VEV precursor to a DeltaB=-1 UDD source; not a rate calculation |
| delta_left_lepton_RPV_control | 3 | 3 | genuine DeltaL=+1 PS-VEV RPV control class |
| delta_bilinear_LH_control | 3 | 1 | DeltaL=+1 bilinear control; distinct from V40's allowed Q H Sc NDirac term |

## Exact limitation found

The protection cannot be promoted to all of G7.  The field operator

`ThetaPlus^2 (Qc)^6 (Sbc)^2 / M^7`

has selector signature `{'U1F': 0, 'Z9': 0, 'Z4R': 2, 'Z5610': 0, 'PQ_numerator_over_170': 0, 'W_allowed_by_listed_selectors': True, 'Kahler_allowed_by_listed_selectors': False}`.  Its explicit
SU(4)-epsilon plus delta contraction is nonzero on the canonical `Sbc` branch
and contains a six-matter component of the form
`epsilon_rgb (u^c_r d^c_g d^c_b) (ell^c ell^c ell^c)`, so it carries
`DeltaB=-1`, `DeltaL=-3`.  This is an
allowed EFT witness, not a claim that an unspecified UV completion produces
its coefficient and not a proton-lifetime result.

## Bounded frontier

The representation-count scan tests one-epsilon classes through complete
field degree `12`.  It
finds `6` selector-clean rows and no clean
row below degree ten: `True`.
The earliest row is `{'counts': {'Q': 0, 'Qc': 6, 'Sbc': 2, 'Sc': 0, 'H': 0}, 'net_SU4_fundamental_number': -4, 'matter_difference_Q_minus_Qc': -6, 'raw_field_degree_without_theta': 8, 'minimal_U1F_theta_completion': ['ThetaPlus', 'ThetaPlus'], 'complete_field_degree': 10, 'Z9': 0, 'Z4R_from_matter': 2, 'selector_clean_without_P_or_Pb': True, 'qualification': 'Representation-count and rank-one-VEV pairing conditions pass.  This is not by itself a full flavour-tensor or component matching calculation.'}`.  The scan is a
finite consistency check, not a complete invariant-ring enumeration.

## Boundary

G7 remains open.  A UV construction would need either to prove the witness
coefficient absent or to analyze it together with the complete PS/Kahler/soft
operator basis, flavour, thresholds, dressing, running, and physical decay
observables.

For context on PS fundamental-breaking-induced B/L structures, see
[Chen et al.](https://mediatum.ub.tum.de/doc/1349870/document.pdf) and
[Dutka--Gargalionis](https://arxiv.org/abs/2211.02054).

Core SHA-256: `9e1bc52a7111b89613b3fad819b95af6c3e2da70c7de6ab3237216e62e351bd2`
