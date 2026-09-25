# H-S portal threshold at the tuned G3 target -- v20

**Status:** `G3_TUNED_TARGET_HS_PORTAL_THRESHOLD_CAN_MATCH_SM_HIGGS_QUARTIC__G3_OPEN`

Switching on the declared H-S portal O34 couples the light doublet to the S radial mode. The exact compiler reproduces the singlet threshold lambda_eff = lambda_H - lambda_HS^2/(4 lambda_S) to machine precision. With the certified lambda_H = lambda_S = 1, lambda_HS = 2.0333 gives the one-loop SM value lambda(M_GUT) = -0.0335; that is perturbative and keeps the potential bounded below. The Higgs-mass tension is therefore not structural: it asks for exactly the axion-Higgs portal the benchmark switched off. G3 stays open.

| lambda_HS | retuned O06 | lambda_eff (compiler) | formula |
|---|---|---|---|
| 0.5 | -0.02 | 0.9375 | 0.9375 |
| 1 | -0.04 | 0.75 | 0.75 |
| 2 | -0.08 | 0 | 0 |
| 2.03326 | -0.0813305 | -0.03353820998 | -0.03353820998 |

- lambda_HS needed at lambda_H = 1: `2.03326`; at the BFB floor lambda_H = 1/200: `0.392623`;
- resulting m_h (tree-level from one-loop lambda(M_t)): `123.62` GeV (the SM calibration gives 123.6 GeV tree-level for the measured mass);
- G3: `OPEN`; whole model: neither validated nor excluded.
