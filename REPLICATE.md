# Replication guide — pristine v20 package

## What this repository is

A self-contained release of the **SO(10)×ℤ₁₇ axion candidate (v20)** with:

- anomaly / minimality / decay-portal engines
- independent error audit (imports no v20 engine narrative)
- broken-phase 10+126 Clebsch/flavour fit
- continuous one-/two-loop threshold RG
- 36.6–37.6 GHz haloscope **forecast** (software only)
- adversarial falsification suite
- arbitrary-matrix physical portal-current matching
- aligned fermion benchmark and corrected fixed-$v_R$ $\tan\beta$ profile

It is **not** a dark-matter discovery.

## Pristine inputs

Frozen experimental / benchmark numbers live in:

- `data/frozen_inputs_v20.json`
- `golden/expected_anchors_v20.json`

Do not silently edit these. If physics inputs change, bump the `version` field and update the golden file in the same commit.

## One-command replication

```bash
python -m pip install -r requirements.txt
python replicate.py
```

`replicate.py` will:

1. verify golden anomaly anchors
2. install pinned dependencies
3. run `audit_v20_errors.py`
4. run `so10_axion_v20_engine.py`
5. run the full unittest discovery
6. run `falsify_v20.py`
7. run all external/referee/extensive/public-data packages
8. run the portal-current theorem and exact $C_f(\tan\beta)$ matching
9. profile the constrained flavour objective versus $\tan\beta$

## Manual steps (optional)

```bash
python audit_v20_errors.py
python so10_axion_v20_engine.py --output so10_axion_v20_verdict.json
python -m unittest discover -v
python falsify_v20.py
python flavour_clebsch_fit_v20.py
python two_loop_thresholds_v20.py
python haloscope_scan_37ghz_v20.py
python run_v20_external_next_steps.py
python full_fermion_matching_v20.py
python tan_beta_profile_v20.py
```

PDF rebuild (optional; requires a TeX distribution):

```bash
pdflatex -interaction=nonstopmode -halt-on-error axion_so10_theory_v20.tex
pdflatex -interaction=nonstopmode -halt-on-error axion_so10_theory_v20.tex
```

## Expected honest outcomes

| Check | Expected |
|---|---|
| Anomaly cancellation | PASS |
| One-pair no-go | PASS |
| Soft overclaim detection (Γ inequality, α=1/40 reset, incomplete portals) | PASS (overclaims detected) |
| Flavour at exact $v_R=v_S$ | viable but stressed vs natural ~$10^{14}$ GeV |
| Anomalon portal current | moving-frame sum is universal; physical $Q_{\rm proj}$ remains portal dependent |
| Fermion coefficients | aligned benchmark only; exact full matching open |
| Corrected $v_R=v_S$ flavour profile | no $\chi^2<30$ point in current constrained ansatz |
| Continuous $\alpha^{-1}(v_\Phi)$ | ~16.6, **not** 40 |
| Haloscope mock | software forecast only |

If any **hard** check fails, the candidate construction is broken.
If a soft-overclaim detector fails, the repository is no longer labelling its own overclaims honestly.
