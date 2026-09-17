# Generation code for the v21 flavour witnesses

`../flavour_general_yukawa_v21.py` only *revalidates* the frozen witnesses, so
it is fast enough for CI. This directory holds the code that **produced** them,
so the fits can be reconstructed from scratch and audited independently.

Nothing here is imported by the release module or by any test; it is run by
hand. All scripts locate the release modules as the parent directory.

## What computes what

| script | produces | cost |
|---|---|---|
| `rg.py` | M_Z -> M_I running (type-II 2HDM, one loop + dominant two-loop QCD); `__main__` validates the SM mode against Huang & Zhou (2021) at 1e12 GeV | seconds |
| `so10fit.py` | the model: `M_u = r_H H + r_F F`, observables, residuals; `__main__` checks the degenerate limit `r_F = r_H` reproduces the v20 ansatz | seconds |
| `fitdriver.py` | parallel Levenberg-Marquardt driver **and the optimiser closure test** (fit observables generated from a known parameter point; recovery rate calibrates every "no solution" claim) | ~4 min |
| `realfit.py` | benchmark fits across `tan(beta)` and `v_R` -> `realfit.json` | ~45 min |
| `robust.py` | strict perturbativity (`Y <= 1`) and experimental-only errors -> `robust.json` | ~30 min |
| `predict.py` | forced `sum m_nu` scan (tree level) -> `predict.json` | ~65 min |
| `ordering.py` | inverted-ordering fits -> `ordering.json`, `ordering_extra.json` | ~10 min |
| `ordering_closure.py` | inverted-ordering closure test -> `ordering_closure.json` | ~25 min |
| `thresholds.py` | right-handed-neutrino threshold running; `__main__` runs the equivalence check against the baseline | seconds |
| `eval_thresholds.py` | threshold effect at fixed parameters (the 44-417% shifts) | ~2 min |
| `natural.py` | fine-tuning measure and the capped-cancellation search -> `natural.json` | ~60 min |
| `refit_thresholds.py` | threshold-aware refits at `lam2 = 0, 0.5, 1` -> `refit_thresholds.json` | ~55 min |
| `refit_edges.py` | threshold-aware forced edges and inverted ordering -> `refit_edges.json` | ~40 min |

`../FLAVOUR_GENERAL_YUKAWA_V21_WITNESSES.json` is assembled from those JSON
outputs; the release module then recomputes every quoted quantity from the
parameter vectors.

## Answers an auditor will want

**Where do CKM and PMNS come from?** `so10fit.Stratum.observables`. CKM is the
Takagi factorisation of the predicted `M_u` (`M_d` is diagonal); PMNS is the
charged-lepton basis from `Y_e^+Y_e` against the Takagi factorisation of
`m_nu`. No mixing angle is a fit parameter. In the degenerate limit
`r_F = r_H` the predicted CKM is exactly the identity, which is the v20 no-go.

**What is the likelihood?** `so10fit.Stratum.residuals`, 19 entries: 3 up-quark
masses, 4 CKM (`|V_us|, |V_cb|, |V_ub|, |J|`), 6 neutrino, 3 down-mass nuisance
priors, then Planck / perturbativity / vev-sum-rule penalties. `chi2_fermion`
is the first 13 only. Errors are diagonal, relative, with a 5% theory floor
unless stated; input correlations are not used.

**Is the forced `sum m_nu` scan circular?** No. The forcing pull is appended
*after* the 19 entries and is never part of `chi2_fermion`, so the quoted cost
is a profile likelihood at fixed `sum m_nu`.

**How is fine-tuning defined?** `natural.tuning`: sum of the norms of the
Type-II and individual right-handed-neutrino contributions divided by the norm
of `m_nu`, in the Takagi basis of `M_R`. 1 means no cancellation.

**How are thresholds implemented?** `thresholds.run_down`: full matrix running
of `Y_e`, `Y_nu`, `M_R` and the Weinberg operator, each `N_i` integrated out at
its own mass with tree-level matching. Two validations, both in the repository
history and rerunnable: it reproduces the baseline to `4e-7` when all `N` are
integrated out at `M_I` with the neutrino Yukawa off; and when the Type-I part
is forced to run exactly like the Weinberg operator, thresholds have zero
effect (`1e-8`) even at witnesses tuned to 1 part in 300-700.

## Reproducing a witness from scratch

    python fitdriver.py          # closure test first: it calibrates the rest
    python realfit.py 200        # or robust.py / predict.py / ordering.py

Fits are multistart and stochastic: a rerun finds an equally good solution,
not the identical parameter vector. The frozen witnesses are one such solution
each, and the release module revalidates them exactly.
