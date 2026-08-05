# Source audit of Sym^2(210) — v20

**Status:** `SOURCE_CORRECTED_SYM2_210_DECOMPOSITION__G1_REVALIDATION_REQUIRED`

- Dimension: `22155`
- True residual after 1/45/54/210: `21845`
- Old residual: `5945`

PR #98 contains valuable partial calculations, but its 210-channel inventory cannot be merged as a complete scalar closure. The exact symmetric product restores a nonzero same-field 45 and four omitted sectors. G1 remains open; downstream reduced-potential results must be revalidated with the source-correct quartic basis.

## Reopened dependencies

- same-field symmetric 45 channel marked absent
- old residual irrep dimension 5945
- G1 ring completeness arguments that omit 45/1050bar/8910/5940
- BFB or vacuum conclusions that set the symmetric 45 quartic to zero
- component Hessian and threshold conclusions inheriting that reduced potential
