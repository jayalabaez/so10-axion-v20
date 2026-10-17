# Research branch: beyond v20 (not part of the release)

This directory is on the research branch `research/v22-scalar-redesign`. It holds research calculations and reports.
None of it is part of the v20 release:

- It does not change any G1-G8 gate, the gate ledger, SHA256SUMS or the manuscript.
- The v20 program verdict stays as recorded in PR #207: not viable as a complete theory under the declared standards.
- Every result here carries the label it was computed with:
  - EXACT: proved;
  - NUM: numerical, with an uncertainty;
  - EST: order of magnitude;
  - CONJ: argued, not computed;
  - LIT: read in the literature.

## `v21_kill_gates/`: the v21 rescue lead, adjudicated NO_GO (2026-10-17)

The lead tested was the F17/B63 fermion sector plus a one-step G3221 vacuum, with the v20 scalar potential kept
verbatim.

- `round1/`: kill gates K0-K5.
  - `ROUND1_SUMMARY.md` is the summary; `ROUND1_RESULTS.json` holds the structured results.
  - Each gate folder has a `REPORT.txt`, its scripts and the skeptic checks (`verify-*`).
- `round2/`: the decisive gates R2-A (vacuum), R2-B (unification), R2-C (flavour) and R2-V (B63 quality
  verification), each with its skeptic. The final adjudication is `round2/FINAL.txt`.

Outcome:

- **NO_GO**, because of four kills:
  - The one-bidoublet flavour lemma (EXACT): X forbids F.F.H10*, so a single light bidoublet gives CKM = 1.
  - Global minimality fails for two light bidoublets (NUM): 60 of 60 descents reach deeper SU(2)_L-breaking H-Sigma
    vacua.
  - Proton decay or three-loop Landau kills the contents whose v_R lies in the seesaw window.
  - The renormalizable 10 + 126bar type-I fit has chi2 >= 110.
- **Positive results** that carry over:
  - The B63 fermion sector has an exact axion-quality certificate: K_min = 17, by three independent methods.
  - K5 cosmology passes.

Not committed: `.npz` binaries (regenerable) and JSON/log files over 1 MB. The scripts expect read-only repository
checkouts at the paths recorded in each report; adjust those paths to rerun.

## `v22_scalar_redesign/`: scalar-sector redesign (in progress)

This is the staged programme the user requested on 2026-10-17. Its rules:

- Start from the B63 fermions, and re-check the anomalies and axion quality after every scalar change.
- Diagnose why the earlier vacua failed, then make the minimal modification that removes the cause.
- First find one concrete point that passes, with its real spectrum, all of: local stability, perturbativity, a
  flavour fit, two-loop unification and the proton-decay limits.
- Only after that, address quantum corrections and global stability.
- The global-minimum requirement is kept. Any metastable alternative is reported separately.
- Every stage states explicit discard criteria.
