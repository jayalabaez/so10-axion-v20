# V20 error audit — independent of the release engine

## Verdict

**v20 is not falsified as an anomaly-free field-theory candidate.**
It is also **not** a verified UV-complete axion model, and it is **not**
a dark-matter discovery.

The 79/79 package checks still pass, but several of those checks only
reproduce assumptions already embedded in the engine.  This audit imports
**no** v20 engine code.

Reproduce:

```bash
python audit_v20_errors.py
python physics_push_v20.py
python -m unittest test_audit_v20_errors.py test_physics_push_v20.py -v
```

## Soft falsifications of manuscript overclaims

| Problem | Correct finding |
|---|---|
| Decay bound | $\Gamma\ge\lambda^2 M/(32\pi)$ is wrong. The two-body width contains $(1-m_\phi^2/M^2)^2$; the quoted expression is the **massless upper** benchmark, so $\Gamma\le\lambda^2 M/(32\pi)$. |
| Spin(10) running | The model derives $\alpha_{\rm GUT}^{-1}\simeq16.810$ after the spectator shift, then inconsistently resets $\alpha_{10}^{-1}(v_\Phi)=40$. Continuous one-loop running with the stated betas is **not** perturbative to $M_{\rm Pl}$ (conservative envelope hits a Landau pole below $M_{\rm Pl}$; physical real-$210$ gives $\alpha(M_{\rm Pl})\sim0.6$). |
| Quality normalization | The scalar $S^{17}$ and conservative $P=12$ NDA formulae in the manuscript omit the hermitian-conjugate factor two. Corrected: $\sim6.47\times10^{-37}$ and $\sim9.04\times10^{-28}$. |
| Incomplete Lagrangian | Extra gauge- and PQ-invariant operators exist, including $PR\,10_H$ and $\overline{Q}R S^\dagger$. They modify mass matrices and matching. |
| “Full amplitude” | $6.04\times10^{-47}$ is a **unit-coefficient kernel** for one selected graph—not a physical prediction. |

## What survives

- Exact continuous-anomaly cancellation with $(1,16)+(14,3)+(1,-18)$.
- Restricted one-pair no-go (discriminant $-15$).
- Displayed three-pair anomaly solution / portal-basis uniqueness under the stated ansatz.
- Charge-based absence of vector-neutral PQ closure through $P=7$.
- Independently checked repeated-pole integral structure.
- The $P=8$ number **only** as a per-unit-coefficient diagnostic.
- Existence (not the numerical lifetime) of renormalizable decay channels.

## Physics push (as far as the Lagrangian allows)

`physics_push_v20.py` separates:

1. **Fixed by stated charges/tensors** — anomalies, minimality ansatz, channel existence, $P=8$ topology existence, kernel finiteness.
2. **Needs external inputs** — Higgs vacuum alignment, full Yukawa/Clebsch tensors, two-loop thresholds, Wilson coefficients, $v_\Phi/v_S$ stabilization, string-network cosmology.

A Type-I toy seesaw at $v_R=v_S$ remains perturbative for the light-neutrino mass-squared targets, but that is only a lower-bound stress test—not a complete $10_H+\overline{126}_H$ flavour solution.

## Correct public claim

> We have a theoretically consistent, anomaly-free SO(10)×ℤ₁₇ construction that predicts a specific axion mass/coupling **window under stated benchmarks**. Whether nature realizes this model is still open. The 37 GHz band is an experimental target, not a detection.

Anything stronger is incorrect.
