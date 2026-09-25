# G3 Phi-orbit lemma: independent numerical evidence -- v20

**Status:** `PHI_ORBIT_LEMMA_NUMERICAL_EVIDENCE_SUPPORTS_SIGNED_TWO_ORBIT_STATEMENT__PROOF_OPEN`  
**Mode:** `full`; checks: 44/44 passed

All 150 multistart runs end on SO(10).F (68) or SO(10).(-F) (82), certified by A-spectrum and an explicit orbit witness; the constrained profile g(t) is strictly positive for I3(F) > t >= 0; near F its growth law is 'linear in delta: g/delta -> mu_star > 0, g/delta^2 not constant' (fitted slope 0.00819795 vs exact 0.0081985; the claimed 1.9e-3*delta^2 law is checked in claims_vs_reproduced); g(0) = 0.0545898. I3 is maximised by the Cayley form (25.65707922), not by F. This is numerical evidence for the signed two-orbit statement only: the lemma is not proved, G3 stays open and the whole model is neither validated nor excluded.

Flags: `phi_orbit_lemma_proved=False`, `numerical_evidence_only=True`, `g3_closed=False`, `whole_model_validated=False`, `whole_model_excluded=False`

Independent of the repository projector code (stdlib + numpy + scipy only).

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

Small-delta law: g/delta -> 0.00819795 (fit) vs mu* = 0.0081985 (exact Hessian pencil, closed form 7/(270*sqrt(10)) = (28/45)/(24*sqrt(10))); g/delta^2 drifts by a factor 8.46303 over the four smallest delta; growth law: linear in delta: g/delta -> mu_star > 0, g/delta^2 not constant. Excess (5+5bar) kernel directions of the f-Hessian raising I3: True (curvature +45.53679831 on 10 directions), i.e. F is a saddle of I3 on the sphere.

## Cubic maximum

max I3 = 25.65707922 over 60 starts (60 at the max) vs I3(F) = 15.17893277; maximiser A-spectrum x sqrt14 = [[-1.0, 21], [0.0, 17], [3.0, 7]] (Cayley form).

## Claims vs reproduced

| claim | reproduced | verdict |
|---|---|---|
| 150/150 random starts reach f ~ 0 and every zero lies on SO(10).F or SO(10).(-F) | 150/150 starts reach f <= 1e-10 (full run); 150 on +-F by A-spectrum (tol 0.001) and orbit witness (tol 0.001); 0 off-orbit zeros; 0 nonzero local minima | `REPRODUCED` |
| 70 on +F, 80 on -F | 68 on +F, 82 on -F (seed 1500210) | `DIFFERENT_SPLIT__SEED_AND_OPTIMIZER_DEPENDENT` |
| g(t) ~ 1.9e-3 * delta^2 near F (delta = I3(F) - t) | growth law near F: linear in delta: g/delta -> mu_star > 0, g/delta^2 not constant; g/delta -> 0.00819795 (fit) vs mu* = 0.0081985 (exact Hessian pencil at F); g/delta^2 = [0.209643, 0.10351, 0.0508339, 0.0247717] at delta = [0.0379473, 0.0758947, 0.151789, 0.303579] | `NOT_REPRODUCED__GROWTH_IS_LINEAR_IN_DELTA` |
| g(0) ~ 0.052 | g(0) = 0.0545898 | `APPROXIMATELY_REPRODUCED` |
| g grows smoothly with no zero off +-F | min g over delta > 0 grid = 0.000301886; nondecreasing in delta: True | `REPRODUCED` |
| I3(F) = 8*60/10^(3/2) ~ 15.18, I3(-F) = -I3(F) | I3(F) = 15.17893277, I3(-F) = -15.17893277 | `REPRODUCED` |
| unit Cayley form: I3 = 8*168/14^(3/2) ~ 25.66 | I3(Cayley) = 25.65707922 | `REPRODUCED` |
| F does not maximise I3 on the sphere; the maximum 25.66 is attained by the Cayley form | max over 60 starts = 25.65707922 (60 starts); maximiser spectral distance to Cayley = 1e-08 | `REPRODUCED` |
| 3/sqrt14 (x7), -1/sqrt14 (x21), 0 (x17) | A-spectrum x sqrt14 = [[-1.0, 21], [0.0, 17], [3.0, 7]] | `REPRODUCED` |
| K = 24 on the singlet, 14 on the 54, 0 on the 4125 | K_1 = 24, K_54 = 14, K_4125 = 0 (C2(210) = 24) | `REPRODUCED` |
| I_54 = (3a^2-3b^2+4c^2)^2/35, I_4125 = 80(a^2-b^2-c^2)^2/21 on a*A+b*B+c*C (repo normalization) | Gram-level agreement, factor mine/repo = 1.0 (54), 1.0 (4125); max residual 0.0 | `REPRODUCED_EXACTLY_FACTOR_ONE` |

Failures: none
