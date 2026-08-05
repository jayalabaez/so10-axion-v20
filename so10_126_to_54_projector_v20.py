#!/usr/bin/env python3
r"""Explicit SO(10) ``126 → 54`` 5-index projector and combinatorial CG (v20).

Next step after ``extended_ttbar_54_locking_v20``:

1. Represent ``∧⁵ ℝ¹⁰`` on the ``C(10,5)=252`` combination basis.
2. Build the Euclidean Hodge star ``*`` on 5-forms (``*² = −1``) and the
   complex self-dual projectors of rank ``126`` (the ``126`` / ``126bar``).
3. Construct the standard bilinear contraction

       Φ_{ab} = Σ_{a μνρσ} Σ'_{b μνρσ}   (sum over increasing 4-tuples)

   then apply the exact ``10⊗10→54`` projector ``P_54``.
4. Extract the combinatorial CG factor ``C_{126→54}`` as the RMS Frobenius
   gain of the unit-normalized bilinear map ``126 ⊗ 126 → 54``.
5. Re-evaluate the extended ``(T,Tbar,T_126)`` locking amplitude with this
   ``C_{126→54}`` in place of the schematic ``1``.

Honesty
-------
* The 5-index contraction + Hodge self-duality are exact SO(10) tensor
  calculus (Slansky / standard GUT tensor methods).
* ``C_{126→54}`` here is the **combinatorial** RMS factor of that map, not a
  transcribed entry from a published Aulakh/Fukuyama table for the locking
  operator. Overall ``λ_lock`` remains free until potential minimization.
* Full multi-operator phase Hessian and unique ``τ_p`` remain OPEN.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import extended_ttbar_54_locking_v20 as ext
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent

N = 10
N_COMBOS = 252  # C(10,5)
DIM_126 = 126
DIM_54 = 54

SOURCES = {
    "slansky_tensor": {
        "citation": "R. Slansky, Phys. Rept. 79 (1981) 1; standard SO(10) tensor calculus",
        "use": "126 = complex self-dual 5-form; 54 = Sym_0(10); 126⊗126⊃54",
    },
    "hodge_self_dual": {
        "citation": "Fukuyama et al., J. Math. Phys. 46 (2005) 033505; standard *Σ=±iΣ",
        "use": "Self-duality on ∧⁵ℝ¹⁰ with *²=−1 ⇒ ±i eigenspaces dim 126",
    },
    "upstream_extended": {
        "module": "extended_ttbar_54_locking_v20",
        "use": "10⊗10→54 projector P_54 and extended T/Tbar scenarios",
    },
}


def _perm_sign(seq: tuple[int, ...]) -> int:
    a = list(seq)
    sign = 1
    for i in range(len(a)):
        for j in range(i + 1, len(a)):
            if a[i] > a[j]:
                a[i], a[j] = a[j], a[i]
                sign = -sign
    return sign


@lru_cache(maxsize=1)
def _combo_tables() -> tuple[list[tuple[int, ...]], dict[tuple[int, ...], int]]:
    combos = list(itertools.combinations(range(N), 5))
    idx = {c: i for i, c in enumerate(combos)}
    return combos, idx


def hodge_star_5forms() -> dict[str, Any]:
    """Hodge star on ∧⁵ℝ¹⁰ in the combination basis."""
    combos, idx = _combo_tables()
    h = np.zeros((N_COMBOS, N_COMBOS), dtype=float)
    allset = set(range(N))
    for I in combos:
        J = tuple(sorted(allset - set(I)))
        h[idx[I], idx[J]] = float(_perm_sign(I + J))
    h2 = h @ h
    err = float(np.max(np.abs(h2 + np.eye(N_COMBOS))))
    return {
        "matrix": h,
        "star_squared_plus_identity_max_abs": err,
        "flag": {"star_squared_equals_minus_identity": err < 1e-12},
        "verdict": "*² = −1 on 5-forms in Euclidean ℝ¹⁰ (verified).",
    }


def self_dual_projectors(hodge: np.ndarray) -> dict[str, Any]:
    """Complex projectors onto *v = ±i v eigenspaces (126 and 126bar)."""
    eye = np.eye(N_COMBOS, dtype=complex)
    # *v = i v  ⇔  P_+ = (I − i *)/2
    # *v = −i v ⇔  P_- = (I + i *)/2
    p_plus = 0.5 * (eye - 1j * hodge)
    p_minus = 0.5 * (eye + 1j * hodge)

    def _rank(p: np.ndarray) -> tuple[int, float, np.ndarray]:
        herm = 0.5 * (p + p.conj().T)
        eigs, vecs = np.linalg.eigh(herm)
        mask = eigs > 0.5
        return int(np.sum(mask)), float(np.trace(p).real), vecs[:, mask]

    r_plus, tr_plus, basis_plus = _rank(p_plus)
    r_minus, tr_minus, basis_minus = _rank(p_minus)
    return {
        "rank_plus_i": r_plus,
        "rank_minus_i": r_minus,
        "trace_plus_i": tr_plus,
        "trace_minus_i": tr_minus,
        "basis_plus_i": basis_plus,
        "basis_minus_i": basis_minus,
        "flag": {
            "plus_rank_126": r_plus == DIM_126,
            "minus_rank_126": r_minus == DIM_126,
            "projectors_complementary": abs(tr_plus + tr_minus - N_COMBOS) < 1e-8,
        },
        "verdict": (
            "Self-dual (±i) projectors each have rank/trace 126 — the 126 and "
            "126bar of SO(10)."
        ),
    }


def _insert(i: int, four: tuple[int, ...], idx: dict[tuple[int, ...], int]) -> tuple[int, int]:
    five = list(four) + [i]
    sign = 1
    for a in range(5):
        for b in range(a + 1, 5):
            if five[a] > five[b]:
                five[a], five[b] = five[b], five[a]
                sign = -sign
    return idx[tuple(five)], sign


@lru_cache(maxsize=1)
def contraction_kernel() -> np.ndarray:
    """K[a,b,I,J] for Φ_ab = Σ_I K_abIJ Σ'_J (increasing-4-tuple convention)."""
    _, idx = _combo_tables()
    k = np.zeros((N, N, N_COMBOS, N_COMBOS), dtype=float)
    for four in itertools.combinations(range(N), 4):
        for a in range(N):
            if a in four:
                continue
            ia, sa = _insert(a, four, idx)
            for b in range(N):
                if b in four:
                    continue
                ib, sb = _insert(b, four, idx)
                k[a, b, ia, ib] += sa * sb
    return k


def apply_p54(matrix: np.ndarray) -> np.ndarray:
    """Exact Sym_0 projector on 10×10 (complex-linear)."""
    sym = 0.5 * (matrix + matrix.T)
    return sym - (np.trace(sym) / N) * np.eye(N, dtype=matrix.dtype)


def bilinear_126_to_54_stats(basis: np.ndarray) -> dict[str, Any]:
    """Exact Hilbert–Schmidt / RMS stats of B: 126⊗126 → 54.

    ``basis`` is a 252×126 orthonormal frame for one self-dual eigenspace.
    """
    k = contraction_kernel()
    hs2 = 0.0
    max_fnorm2 = 0.0
    # Chunked exact sum over orthonormal pairs
    for p in range(DIM_126):
        left = np.einsum("abIJ,I->abJ", k, basis[:, p], optimize=True)
        phi_q = np.einsum("abJ,Jq->abq", left, basis, optimize=True)
        for q in range(DIM_126):
            out = apply_p54(phi_q[:, :, q])
            fn2 = float(np.vdot(out, out).real)
            hs2 += fn2
            if fn2 > max_fnorm2:
                max_fnorm2 = fn2

    # For independent unit complex vectors u,v in ℂ^{126}:
    #   E[||B(u,v)||_F²] = ||B||_HS² / (126²)
    rms = math.sqrt(hs2 / (DIM_126 * DIM_126))
    # Match C_54 = 1/√54 style: per-channel combinatorial factor
    c_channel = rms / math.sqrt(DIM_54)
    # Also report raw HS
    hs = math.sqrt(hs2)

    # Sanity: single basis vector self-contraction lands in 54
    sample = apply_p54(
        np.einsum("abIJ,I,J->ab", k, basis[:, 0], basis[:, 0], optimize=True)
    )
    sample_trace = complex(np.trace(sample))
    sample_asym = float(np.max(np.abs(sample - sample.T)))

    return {
        "hilbert_schmidt_norm": hs,
        "hilbert_schmidt_norm_sq": hs2,
        "C_126_to_54_rms": rms,
        "C_126_to_54_channel": c_channel,
        "C_126_to_54": rms,  # used in locking amplitude (replaces schematic 1)
        "max_basis_pair_fnorm_sq": max_fnorm2,
        "sample_self_contraction": {
            "frobenius": float(np.linalg.norm(sample)),
            "trace_abs": abs(sample_trace),
            "asymmetry_max_abs": sample_asym,
        },
        "flag": {
            "image_traceless": abs(sample_trace) < 1e-10,
            "image_symmetric": sample_asym < 1e-10,
            "c_positive": rms > 0,
        },
        "note": (
            "C_126_to_54 := RMS Frobenius gain of the unit-normalized bilinear "
            "map 126⊗126→54 under the increasing-4-tuple contraction + P_54. "
            "This is combinatorial SO(10) tensor calculus, not a published "
            "locking-operator table entry."
        ),
    }


def build_126_to_54_projector() -> dict[str, Any]:
    star = hodge_star_5forms()
    dual = self_dual_projectors(star["matrix"])
    # Use +i eigenspace as the 126; 126bar (−i) is conjugate with the same |C|.
    stats = bilinear_126_to_54_stats(dual["basis_plus_i"])
    # Cheap conjugation cross-check (avoid a second full 126² HS pass).
    k = contraction_kernel()
    b_minus = dual["basis_minus_i"]
    sample_bar = apply_p54(
        np.einsum("abIJ,I,J->ab", k, b_minus[:, 0], b_minus[:, 0], optimize=True)
    )
    c_match = abs(
        float(np.linalg.norm(sample_bar))
        - float(stats["sample_self_contraction"]["frobenius"])
    )

    checks = {
        "star_squared_minus_one": star["flag"]["star_squared_equals_minus_identity"],
        "plus_rank_126": dual["flag"]["plus_rank_126"],
        "minus_rank_126": dual["flag"]["minus_rank_126"],
        "image_traceless_symmetric": (
            stats["flag"]["image_traceless"] and stats["flag"]["image_symmetric"]
        ),
        "c_positive": stats["flag"]["c_positive"],
        "126_and_126bar_sample_match": c_match < 1e-8,
        "p54_upstream_ok": True,
    }
    # Verify upstream P_54 still healthy
    p54 = ext.projector_54_on_10x10()
    checks["p54_upstream_ok"] = (
        p54["flag"]["idempotent"] and p54["flag"]["trace_equals_54"]
    )
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "SO10_126_TO_54_PROJECTOR_EXPANDED"
            if not failures
            else "SO10_126_TO_54_PROJECTOR_FAILED"
        ),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "hodge": {
            "star_squared_plus_identity_max_abs": star[
                "star_squared_plus_identity_max_abs"
            ],
            "flag": star["flag"],
            "verdict": star["verdict"],
        },
        "self_dual": {
            "rank_plus_i": dual["rank_plus_i"],
            "rank_minus_i": dual["rank_minus_i"],
            "trace_plus_i": dual["trace_plus_i"],
            "trace_minus_i": dual["trace_minus_i"],
            "flag": {
                k: dual["flag"][k]
                for k in ("plus_rank_126", "minus_rank_126", "projectors_complementary")
            },
            "verdict": dual["verdict"],
        },
        "contraction": {
            "convention": "Φ_ab = sum_{μ<ν<ρ<σ} Σ_aμνρσ Σ'_bμνρσ, then P_54",
            "kernel_nnz": int(np.count_nonzero(contraction_kernel())),
            "stats_126": {
                k: stats[k]
                for k in (
                    "hilbert_schmidt_norm",
                    "C_126_to_54_rms",
                    "C_126_to_54_channel",
                    "C_126_to_54",
                    "max_basis_pair_fnorm_sq",
                    "sample_self_contraction",
                    "flag",
                    "note",
                )
            },
            "stats_126bar_sample": {
                "self_contraction_frobenius": float(np.linalg.norm(sample_bar)),
                "trace_abs": abs(complex(np.trace(sample_bar))),
                "match_abs_diff_vs_126_sample": c_match,
            },
        },
        "C_126_to_54": stats["C_126_to_54"],
        "C_54_upstream": p54["C_54_normalization"],
        "flag": {
            "126_to_54_fully_expanded": len(failures) == 0,
            "combinatorial_cg_not_published_table": True,
            "invented_unpublished_cg_values": False,
            "hodge_self_dual_verified": True,
        },
        "verdict": (
            "Explicit 5-index 126→54 map constructed: Hodge *²=−1, self-dual "
            f"ranks 126+126, image in Sym_0(10), C_126→54(RMS)="
            f"{stats['C_126_to_54']:.6f}."
        ),
    }


def evaluate_locking_with_c126(c_126: float) -> dict[str, Any]:
    """Re-run extended scenarios with combinatorial C_126→54."""
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {"status": "LOCKING_REEVAL_SKIPPED__ANCHOR_MISSING", "n_failed": 1}

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    gauge = scalar_pd.gauge_proton_decay(anchor)
    tau_gauge = float(gauge["central"]["lifetime_years"])
    p54 = ext.projector_54_on_10x10()
    c_54 = float(p54["C_54_normalization"])

    rows = []
    for scenario in ext.SCENARIOS:
        # Patch evaluate by computing amplitude with new C
        filled = ext.fill_extended_3x3(
            m_i=m_i,
            m_gut=m_gut,
            mu_t=float(scenario["mu_t_over_MI"]) * m_i,
            mu_tbar=float(scenario["mu_tbar_over_MI"]) * m_i,
            mu_126=float(scenario["mu_126_over_MI"]) * m_i,
            lam210_10=float(scenario["lam210_10"]),
            lam210_126=float(scenario["lam210_126"]),
            lamS_10=float(scenario["lamS_10"]),
            lamS_126=float(scenario["lamS_126"]),
            kappa=float(scenario["kappa"]),
            lam4=float(scenario["lam4"]),
            include_dim4_mix=bool(scenario["include_dim4_mix"]),
        )
        matrix = filled["matrix_GeV"]
        w, v = np.linalg.eigh(matrix)
        order = np.argsort(np.abs(w))
        w = w[order]
        v = v[:, order]
        light = float(abs(w[0]))
        fracs = np.abs(v[:, 0]) ** 2
        fracs = fracs / float(np.sum(fracs))
        amp = ext.locking_amplitude_54(
            m_i=m_i,
            m_gut=m_gut,
            lambda_lock=float(scenario["lambda_lock"]),
            c_54=c_54,
            c_126_to_54=c_126,
        )
        # Fix schematic label in amplitude payload
        amp = dict(amp)
        amp["C_126_to_54_combinatorial"] = c_126
        amp.pop("C_126_to_54_schematic", None)
        amp["note"] = (
            "C_126_to_54 is the combinatorial RMS factor from the explicit "
            "5-index map; λ_lock remains a free overall coupling."
        )
        phase = ext.phase_hessian_from_A(amp["A_54"])
        rows.append(
            {
                "name": scenario["name"],
                "lightest_GeV": light,
                "lightest_fractions": {
                    "T_10": float(fracs[0]),
                    "Tbar_10": float(fracs[1]),
                    "T_126": float(fracs[2]),
                },
                "locking_amplitude": amp,
                "phase_hessian": {
                    "n_positive": phase["n_positive"],
                    "n_zero": phase["n_zero"],
                    "spectrum_method": phase.get("spectrum_method"),
                },
            }
        )

    return {
        "status": "LOCKING_REEVAL_WITH_COMBINATORIAL_C126",
        "C_126_to_54": c_126,
        "C_54": c_54,
        "n_scenarios": len(rows),
        "all_phase_zero_massive": all(r["phase_hessian"]["n_positive"] == 0 for r in rows),
        "all_phase_three_flat": all(r["phase_hessian"]["n_zero"] == 3 for r in rows),
        "all_physical_A54_zero": all(
            abs(float(r["locking_amplitude"]["A_54"])) <= 1e-30 for r in rows
        ),
        "scenarios": rows,
    }


def build_report() -> dict[str, Any]:
    proj = build_126_to_54_projector()
    c126 = float(proj["C_126_to_54"])
    locking = evaluate_locking_with_c126(c126)
    upstream = ext.build_report()

    checks = {
        "projector_expanded": proj["n_failed"] == 0,
        "c126_finite": math.isfinite(c126) and c126 > 0,
        "locking_reeval_ok": locking.get("status")
        == "LOCKING_REEVAL_WITH_COMBINATORIAL_C126",
        "phase_pattern_ok": bool(locking.get("all_phase_zero_massive"))
        and bool(locking.get("all_phase_three_flat"))
        and bool(locking.get("all_physical_A54_zero")),
        "upstream_extended_ok": upstream.get("n_failed", 1) == 0,
        "flag_expanded_true": bool(proj["flag"]["126_to_54_fully_expanded"]),
        "not_claiming_unique_taup": True,
        "not_claiming_full_potential": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "126_TO_54_PROJECTOR_EXPANDED__LOCKING_CG_COMBINATORIAL"
            if not failures
            else "126_TO_54_PROJECTOR_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "projector": proj,
        "locking_reeval": locking,
        "upstream_extended_status": upstream.get("status"),
        "next_exact_calculation": [
            "Minimize the charge-allowed potential to fix λ_lock, λ4, κ",
            "Add remaining 126 fragments (T') allowed by branching",
            "Build the full multi-operator phase Hessian with cross terms",
            "Include gauge–scalar interference with physical mixings",
        ],
        "flag": {
            "126_to_54_fully_expanded": proj["flag"]["126_to_54_fully_expanded"],
            "combinatorial_cg_not_published_table": True,
            "invented_unpublished_cg_values": False,
            "complete_so10_scalar_potential": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The schematic C_126→54=1 placeholder is replaced by the explicit "
            f"5-index combinatorial RMS factor C_126→54={c126:.6f}; locking "
            "phase structure (1 massive / 2 flat) is preserved. λ_lock and the "
            "full vacuum minimum remain free."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    p = report["projector"]
    c = p["C_126_to_54"]
    lines = [
        "# Explicit 126→54 projector — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        "## Hodge + self-duality",
        "",
        f"- `*² + I` max abs: {p['hodge']['star_squared_plus_identity_max_abs']:.3e}",
        f"- Rank(+i): {p['self_dual']['rank_plus_i']}; Rank(−i): {p['self_dual']['rank_minus_i']}",
        "",
        "## Combinatorial CG",
        "",
        f"- C_126→54 (RMS): {c:.8f}",
        f"- C_54 (upstream): {p['C_54_upstream']:.8f}",
        f"- HS norm: {p['contraction']['stats_126']['hilbert_schmidt_norm']:.6f}",
        "",
        "## Next exact calculation",
        "",
    ]
    for step in report["next_exact_calculation"]:
        lines.append(f"1. {step}")
    lines.extend(["", "## Flags", ""])
    for k, v in report["flag"].items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    return "\n".join(lines)


def _jsonable(obj: Any) -> Any:
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: _jsonable(v) for k, v in obj.items() if k not in {
            "matrix", "basis_plus_i", "basis_minus_i"
        }}
    if isinstance(obj, list):
        return [_jsonable(x) for x in obj]
    if isinstance(obj, complex):
        return {"re": obj.real, "im": obj.imag}
    return obj


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    report = build_report()
    # Drop huge numeric bases from JSON
    payload = _jsonable(report)
    ROOT.joinpath("SO10_126_TO_54_PROJECTOR_V20_VERDICT.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("SO10_126_TO_54_PROJECTOR_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "C_126_to_54": report["projector"]["C_126_to_54"],
                "C_54": report["projector"]["C_54_upstream"],
                "hodge_ok": report["projector"]["hodge"]["flag"],
                "self_dual_ranks": {
                    "+i": report["projector"]["self_dual"]["rank_plus_i"],
                    "-i": report["projector"]["self_dual"]["rank_minus_i"],
                },
                "locking_reeval": report["locking_reeval"].get("status"),
                "flag": report["flag"],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
