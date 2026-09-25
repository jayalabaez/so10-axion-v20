# G3 Phi-orbit lemma: independent numerical evidence -- v20

**Status:** `PHI_ORBIT_LEMMA_NUMERICAL_EVIDENCE_SUPPORTS_SIGNED_TWO_ORBIT_STATEMENT__PROOF_OPEN`  
**Mode:** `full`; checks: 51/51 passed

All 150 multistart runs end on SO(10).F (68) or SO(10).(-F) (82), certified by A-spectrum and an explicit orbit witness; at the 26 sampled t values in [-7.58947, 24.2863] the best constrained local minimum of f (an upper bound on g(t)) is >= 5.69918e-08, so no zero off +-F was found. The growth of g near F is one-sided: below F only (t < I3(F), delta = I3(F) - t > 0): linear in delta: g/delta -> mu_star > 0, g/delta^2 not constant (fitted slope 0.00819795 vs exact 0.0081985); above F only (t > I3(F), Delta = t - I3(F) > 0): quadratic: g/Delta^2 -> c_up > 0, g/Delta -> 0 (fitted 3.95316e-05 vs exact 3.95289e-05). The claimed 1.9e-3*delta^2 law is checked in claims_vs_reproduced; g(0) = 0.0545898. I3 = 8 Tr(A^3) is maximised by the Cayley form (25.65707922), not by F. This is numerical evidence for the signed two-orbit statement only: the lemma is not proved, G3 stays open and the whole model is neither validated nor excluded.

Flags: `phi_orbit_lemma_proved=False`, `numerical_evidence_only=True`, `g3_closed=False`, `whole_model_validated=False`, `whole_model_excluded=False`

Independent of the repository projector code (stdlib + numpy + scipy only).

## Convention

I3(Phi) = 8 Tr(A_Phi^3), the all-orderings contraction sum_{a..f} Phi_abcd Phi_cdef Phi_efab; the repository/manuscript Tr(A_Phi^3) is I3/8. Every I3, delta and slope in this report uses I3 unless labelled per_unit_TrA3. In Tr(A^3) units: Tr A^3 = 6/sqrt(10) = 1.897366596 at F and 12/sqrt(14) = 3.207134903 at the Cayley form; the below-F slope is 8*mu* = 28/(135*sqrt(10)) = 0.065587981 per unit Tr A^3 (mu* = 7/(270*sqrt(10)) = 0.0081984976 per unit I3); the above-F quadratic coefficient is 0.0025298523 per (unit Tr A^3)^2 (3.9528942e-05 per (unit I3)^2).

## Sym^2(210) and the pair Casimir K

| irrep | highest weight | mult | C2 | K |
|---|---|---|---|---|
| 1 | (0, 0, 0, 0, 0) | 1 | 0 | 24 |
| 45 | (1, 1, 0, 0, 0) | 1 | 16 | 16 |
| 54 | (2, 0, 0, 0, 0) | 1 | 20 | 14 |
| 210 | (1, 1, 1, 1, 0) | 1 | 24 | 12 |
| 1050bar | (2, 1, 1, 1, -1) | 1 | 36 | 6 |
| 1050 | (2, 1, 1, 1, 1) | 1 | 36 | 6 |
| 770 | (2, 2, 0, 0, 0) | 1 | 36 | 6 |
| 5940 | (2, 2, 1, 1, 0) | 1 | 44 | 2 |
| 4125 | (2, 2, 2, 0, 0) | 1 | 48 | 0 |
| 8910 | (2, 2, 2, 2, 0) | 1 | 56 | -4 |

Dimension sum 22155; distinct K eigenvalues ['24', '16', '14', '12', '6', '2', '0', '-4'] (Lanczos Krylov dimension 8, max Ritz defect 1e-13); max projector idempotence defect 1e-13.

## Slice cross-check against the repository identities

- I_54: factor mine/repo = 1.0, Gram residual 0.0;
- I_4125: factor mine/repo = 1.0, Gram residual 0.0.

## Multistart

- 150/150 starts reach f <= 1e-10; +F: 68, -F: 82, off-orbit zeros: 0, nonzero local minima: 0;
- after the projector polish: max f = 1.4e-16, max spectral distance 0.0002 (tol 0.001), max witness distance 0.00029 (tol 0.001); distance to the other orbit >= 0.948683.

## Adversarial profile g(t) = min{f : |Phi|=1, I3=t}

Each g is the best of up to 6 constrained local minimisations, i.e. an upper bound on g(t), not a proof of positivity. At the 26 sampled t values in [-7.58947, 24.2863] (16 below I3(F), 10 above) the best local minimum is >= 5.69918e-08; no zero off +-F was found.

Below F (t < I3(F), delta = I3(F) - t > 0):

| delta/I3(F) | t | g | g/delta | g/delta^2 | runs agreeing |
|---|---|---|---|---|---|
| 0 | 15.178933 | 0 | - | - | (F) |
| 0.0025 | 15.140985 | 0.000301886 | 0.0079554 | 0.209643 | 6/6 |
| 0.005 | 15.103038 | 0.000596216 | 0.00785584 | 0.10351 | 6/6 |
| 0.01 | 15.027143 | 0.00117121 | 0.00771604 | 0.0508339 | 6/6 |
| 0.02 | 14.875354 | 0.00228296 | 0.00752015 | 0.0247717 | 6/6 |
| 0.05 | 14.419986 | 0.00541637 | 0.00713669 | 0.00940342 | 6/6 |
| 0.1 | 13.661039 | 0.0101864 | 0.00671089 | 0.00442118 | 6/6 |
| 0.2 | 12.143146 | 0.0185668 | 0.00611597 | 0.00201463 | 6/6 |
| 0.3 | 10.625253 | 0.0257845 | 0.00566234 | 0.00124346 | 6/6 |
| 0.4 | 9.1073597 | 0.0320588 | 0.00528015 | 0.000869652 | 6/6 |
| 0.5 | 7.5894664 | 0.0375123 | 0.00494267 | 0.000651254 | 6/6 |
| 0.6 | 6.0715731 | 0.0422243 | 0.00463628 | 0.00050907 | 6/6 |
| 0.7 | 4.5536798 | 0.0462511 | 0.00435294 | 0.000409679 | 6/6 |
| 0.8 | 3.0357866 | 0.0496343 | 0.00408743 | 0.000336604 | 5/6 |
| 0.9 | 1.5178933 | 0.0524056 | 0.00383614 | 0.000280809 | 6/6 |
| 1.0 | 0.0 | 0.0545898 | 0.00359642 | 0.000236935 | 6/6 |
| 1.5 | -7.5894664 | 0.0375123 | 0.00164756 | 7.23616e-05 | 4/6 |

Small-delta law, one-sided (below F only): g/delta -> 0.00819795 (fit) vs mu* = 0.0081985 (exact Hessian pencil, closed form 7/(270*sqrt(10)) = (28/45)/(24*sqrt(10))); g/delta^2 drifts by a factor 8.46303 over the four smallest delta; growth law: below F only (t < I3(F), delta = I3(F) - t > 0): linear in delta: g/delta -> mu_star > 0, g/delta^2 not constant. Excess (5+5bar) kernel directions of the f-Hessian raising I3: True (curvature +45.53679831 on 10 directions), i.e. F is a saddle of I3 on the sphere.

Above F (t > I3(F), Delta = t - I3(F) > 0; feasible up to Delta = I3(Cayley) - I3(F)):

| delta/I3(F) | t | Delta | g | g/Delta^2 | runs agreeing |
|---|---|---|---|---|---|
| -0.0025 | 15.21688 | 0.037947332 | 5.69918e-08 | 3.95777e-05 | 6/6 |
| -0.005 | 15.254827 | 0.075894664 | 2.28249e-07 | 3.96266e-05 | 6/6 |
| -0.01 | 15.330722 | 0.15178933 | 9.1526e-07 | 3.97248e-05 | 6/6 |
| -0.02 | 15.482511 | 0.30357866 | 3.67934e-06 | 3.99234e-05 | 6/6 |
| -0.05 | 15.937879 | 0.75894664 | 2.33486e-05 | 4.05358e-05 | 6/6 |
| -0.1 | 16.696826 | 1.5178933 | 9.58833e-05 | 4.1616e-05 | 6/6 |
| -0.2 | 18.214719 | 3.0357866 | 0.000405817 | 4.4034e-05 | 6/6 |
| -0.3 | 19.732613 | 4.5536798 | 0.000972001 | 4.6875e-05 | 6/6 |
| -0.45 | 22.009453 | 6.8305197 | 0.00243644 | 5.22213e-05 | 6/6 |
| -0.6 | 24.286292 | 9.1073597 | 0.00493123 | 5.94525e-05 | 6/6 |

Small-Delta law, one-sided (above F only): g/Delta^2 -> 3.95316e-05 (fit) vs c_up = 3.95289e-05 (exact fourth-order reduction on the 5+5bar excess space, q_eff = 0.02049180328, candidate 5/244); g/Delta^2 drifts by 1.00874 over the four smallest Delta; growth law: above F only (t > I3(F), Delta = t - I3(F) > 0): quadratic: g/Delta^2 -> c_up > 0, g/Delta -> 0.

## Cubic maximum

max I3 = 25.65707922 over 60 starts (60 at the max) vs I3(F) = 15.17893277; maximiser A-spectrum x sqrt14 = [[-1.0, 21], [0.0, 17], [3.0, 7]] (Cayley form).

## Claims vs reproduced

| claim | reproduced | verdict |
|---|---|---|
| 150/150 random starts reach f ~ 0 and every zero lies on SO(10).F or SO(10).(-F) | 150/150 starts reach f <= 1e-10 (full run); 150 on +-F by A-spectrum (tol 0.001) and orbit witness (tol 0.001); 0 off-orbit zeros; 0 nonzero local minima | `REPRODUCED` |
| 70 on +F, 80 on -F | 68 on +F, 82 on -F (seed 1500210) | `DIFFERENT_SPLIT__SEED_AND_OPTIMIZER_DEPENDENT` |
| g(t) ~ 1.9e-3 * delta^2 near F (delta = I3(F) - t) | The growth law is one-sided. below F only (t < I3(F), delta = I3(F) - t > 0): linear in delta: g/delta -> mu_star > 0, g/delta^2 not constant; g/delta -> 0.00819795 (fit) vs mu* = 0.0081985 (exact Hessian pencil at F); g/delta^2 = [0.209643, 0.10351, 0.0508339, 0.0247717] at delta = [0.0379473, 0.0758947, 0.151789, 0.303579]. above F only (t > I3(F), Delta = t - I3(F) > 0): quadratic: g/Delta^2 -> c_up > 0, g/Delta -> 0; g/(t-I3(F))^2 -> 3.95316e-05 (fit) vs c_up = 3.95289e-05 (exact fourth-order reduction on the 5+5bar excess space). Neither side shows 1.9e-3*delta^2. | `NOT_REPRODUCED__LINEAR_BELOW_F_QUADRATIC_ABOVE_F` |
| g(0) ~ 0.052 | g(0) = 0.0545898 | `APPROXIMATELY_REPRODUCED` |
| g grows smoothly with no zero off +-F | at the 26 sampled t values in [-7.58947, 24.2863] (16 below I3(F), 10 above; with g(-t) = g(t) the grid spans |t| from 0 to 24.2863 of the feasible |t| <= 25.6571) the best constrained local minimum (best of up to 6 local runs, an upper bound on g, not a proof of positivity) is >= 5.69918e-08 (>= 0.000301886 below F, >= 5.69918e-08 above F, smallest at the grid points nearest I3(F)); no zero off +-F was found; best values nondecreasing in |t - I3(F)| on each side: True | `REPRODUCED_ON_SAMPLED_RANGE` |
| I3(F) = 8*60/10^(3/2) ~ 15.18, I3(-F) = -I3(F) | I3(F) = 15.17893277, I3(-F) = -15.17893277 | `REPRODUCED` |
| unit Cayley form: I3 = 8*168/14^(3/2) ~ 25.66 | I3(Cayley) = 25.65707922 | `REPRODUCED` |
| F does not maximise I3 on the sphere; the maximum 25.66 is attained by the Cayley form | max over 60 starts = 25.65707922 (60 starts); maximiser spectral distance to Cayley = 1e-08 | `REPRODUCED` |
| 3/sqrt14 (x7), -1/sqrt14 (x21), 0 (x17) | A-spectrum x sqrt14 = [[-1.0, 21], [0.0, 17], [3.0, 7]] | `REPRODUCED` |
| K = 24 on the singlet, 14 on the 54, 0 on the 4125 | K_1 = 24, K_54 = 14, K_4125 = 0 (C2(210) = 24) | `REPRODUCED` |
| I_54 = (3a^2-3b^2+4c^2)^2/35, I_4125 = 80(a^2-b^2-c^2)^2/21 on a*A+b*B+c*C (repo normalization) | Gram-level agreement, factor mine/repo = 1.0 (54), 1.0 (4125); max residual 0.0 | `REPRODUCED_EXACTLY_FACTOR_ONE` |

Failures: none
