# H-S portal threshold at the tuned G3 point -- v20

**Status:** `G3_PORTAL_THRESHOLD_EXACT__SM_MATCHED_PORTAL_MAKES_TUNED_POINT_A_SADDLE__G3_OPEN`

The declared H-S portal gives the exact singlet threshold lambda_eff = lambda_H - lambda_HS^2/(4 lambda_S), but the tuned point stays a tree-level local minimum only while lambda_eff >= 0 (lambda_HS <= 2 at the benchmark). Matching the two-loop SM value lambda(M_GUT) = -0.0151 needs lambda_HS = 2.0151; the point is then a PSD but degenerate saddle that descends along the H-S valley to an electroweak-breaking, PQ-restoring configuration with S = 0. A tree-level portal threshold therefore cannot supply the negative matching quartic at a G3-admissible point. G3 stays open; nothing is excluded.

| lambda_HS | retuned O06 | lambda_eff (compiler) | formula |
|---|---|---|---|
| 0.5 | -0.02 | 0.9375 | 0.9375 |
| 1 | -0.04 | 0.75 | 0.75 |
| 2 | -0.08 | 0 | 0 |
| 2.01505 | -0.0806022 | -0.01511154997 | -0.01511154997 |

- local minimum requires lambda_HS <= `2`;
- two-loop SM target lambda(M_GUT) = `-0.01511` needs lambda_HS = `2.01505`;
- at that coupling the S = 0 branch lies `-2.418e-05` M^4 below the tuned point (analytic `-2.418e-05`), at |H|/|Phi| = `0.201`;
- G3: `OPEN`; whole model: neither validated nor excluded.
