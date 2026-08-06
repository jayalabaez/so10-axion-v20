#!/usr/bin/env python3
"""Project the exact Phi^2 H 126dag channels onto the p+Delta_R vacuum.

PR #146 constructed the canonical orthogonal 210 and 1050 tensor channels for

    210_H^2 10_H 126bar_H^dag + h.c.

This module performs the downstream G2/G4 projection on the verified
Pati--Salam p plus physical Delta_R background.  It does not introduce a
second tensor basis.

For both channels the symmetric Phi^2 tensor vanishes at Phi=p.  Consequently
there is no H tadpole and no H--126dag mixed block at H=0.  The derivative with
respect to a 210 fluctuation is nonzero.  In canonical normalization the
H--210 blocks have

  rank(B_210)=3, singular values 3 x (4 sqrt(2)/3),
  rank(B_1050)=7, singular values 4 x 2 plus 3 x (4 sqrt(2)/3).

Both blocks annihilate every 210 gauge tangent at p, as required by the
Noether identity.  They must therefore be inserted into the enlarged physical
Hessian even though H=0 stationarity survives.

This closes the selected-vacuum projection of this family only.  Nonzero
electroweak backreaction, the complete component potential, and whole-model
validation remain open.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_phi2_h_126dag_210_1050_channels_v20 as channels

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_PHI2_H126DAG_SELECTED_VACUUM_PROJECTION_V20.json"
OUT_MD = ROOT / "EXACT_PHI2_H126DAG_SELECTED_VACUUM_PROJECTION_V20.md"


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, complex):
        return {"re": float(value.real), "im": float(value.imag)}
    return value


def conjugate_form(form: channels.Form) -> channels.Form:
    return {indices: np.conjugate(value) for indices, value in form.items()}


def physical_background() -> tuple[channels.Form, channels.Form]:
    p = channels.singlet_basis()[0]
    delta_dagger = conjugate_form(direct.delta_r())
    return p, delta_dagger


def h_coefficient_vector(
    channel_tensor: np.ndarray, sigma_vector: np.ndarray
) -> np.ndarray:
    """Coefficient of H in <channel, H tensor Sigma>."""
    return np.einsum(
        "ai,i->a", np.conjugate(channel_tensor), sigma_vector, optimize=True
    )


def channel_projectors() -> dict[str, Callable[[np.ndarray], np.ndarray]]:
    return {
        "210": lambda tensor: channels.project_210(tensor, +1),
        "1050": lambda tensor: channels.project_1050(tensor, +1),
    }


@lru_cache(maxsize=1)
def projection_audit() -> dict[str, Any]:
    upstream = channels.build_report()
    p, delta_dagger = physical_background()
    sigma_vector = channels.five_to_vector(delta_dagger)
    base = channels.phi2_bilinear(p, p, +1)
    projectors = channel_projectors()

    four_basis = tuple(
        {indices: 1.0 + 0.0j} for indices in channels.C4
    )
    rows: dict[str, Any] = {}
    for name, projector in projectors.items():
        base_channel = projector(base)
        tadpole = h_coefficient_vector(base_channel, sigma_vector)
        hphi = np.empty((channels.N, len(channels.C4)), dtype=complex)
        for column, state in enumerate(four_basis):
            variation = channels.phi2_bilinear(state, p, +1) + channels.phi2_bilinear(
                p, state, +1
            )
            hphi[:, column] = h_coefficient_vector(
                projector(variation), sigma_vector
            )

        singular_values = np.linalg.svd(hphi, compute_uv=False)
        rank = int(np.sum(singular_values > 1.0e-12))
        gauge_residual = 0.0
        for first, second in itertools.combinations(range(channels.N), 2):
            tangent = channels.four_to_vector(
                channels.generator_action(p, first, second)
            )
            gauge_residual = max(
                gauge_residual, float(np.max(np.abs(hphi @ tangent)))
            )

        rows[name] = {
            "base_channel_norm": channels.tensor_norm(base_channel),
            "H_tadpole": tadpole,
            "H_tadpole_norm": float(np.linalg.norm(tadpole)),
            "H_126dag_block_rank": 0 if channels.tensor_norm(base_channel) < 1.0e-12 else None,
            "H_210_block": {
                "shape": list(hphi.shape),
                "rank": rank,
                "singular_values": singular_values,
                "frobenius_norm": float(np.linalg.norm(hphi)),
                "maximum_abs_entry": float(np.max(np.abs(hphi))),
                "gauge_tangent_residual": gauge_residual,
            },
        }

    expected = 4.0 * math.sqrt(2.0) / 3.0
    checks = {
        "upstream_two_channel_tensor_family_closed": upstream["n_failed"] == 0,
        "both_base_channels_vanish_at_p_squared": all(
            row["base_channel_norm"] < 1.0e-12 for row in rows.values()
        ),
        "both_H_tadpoles_zero": all(
            row["H_tadpole_norm"] < 1.0e-12 for row in rows.values()
        ),
        "both_H_126dag_blocks_zero": all(
            row["H_126dag_block_rank"] == 0 for row in rows.values()
        ),
        "canonical_H210_ranks_three_and_seven": (
            rows["210"]["H_210_block"]["rank"] == 3
            and rows["1050"]["H_210_block"]["rank"] == 7
        ),
        "210_singular_spectrum_exact": np.max(
            np.abs(
                np.asarray(rows["210"]["H_210_block"]["singular_values"][:3])
                - expected
            )
        ) < 1.0e-12,
        "1050_singular_spectrum_exact": (
            np.max(
                np.abs(
                    np.asarray(rows["1050"]["H_210_block"]["singular_values"][:4])
                    - 2.0
                )
            )
            < 1.0e-12
            and np.max(
                np.abs(
                    np.asarray(rows["1050"]["H_210_block"]["singular_values"][4:7])
                    - expected
                )
            )
            < 1.0e-12
        ),
        "both_blocks_annihilate_210_gauge_tangents": all(
            row["H_210_block"]["gauge_tangent_residual"] < 1.0e-12
            for row in rows.values()
        ),
        "nonzero_electroweak_backreaction_not_claimed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable(
        {
            "status": (
                "PHI2_H126DAG_SELECTED_VACUUM_PROJECTION_CLOSED"
                if not failures
                else "PHI2_H126DAG_SELECTED_VACUUM_PROJECTION_FAILED"
            ),
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "background": {
                "Phi": "normalized Pati-Salam p",
                "Sigma_dagger": "complex conjugate of physical Delta_R",
                "H": 0,
            },
            "channels": rows,
            "analytic_spectra": {
                "210": "3 x (4 sqrt(2)/3), then zeros",
                "1050": "4 x 2, 3 x (4 sqrt(2)/3), then zeros",
            },
            "flags": {
                "canonical_210_1050_projectors_reused": not failures,
                "selected_H_zero_stationarity_preserved": not failures,
                "selected_H126dag_blocks_zero": not failures,
                "selected_H210_blocks_derived": not failures,
                "selected_H210_ranks_three_and_seven": not failures,
                "complete_component_potential": False,
                "full_multifield_hessian": False,
                "nonzero_electroweak_backreaction_solved": False,
                "whole_model_validated": False,
                "empirical_discovery": False,
            },
            "next_exact_target": (
                "Insert both canonical H--210 blocks with independent "
                "coefficients into the 482-real physical quotient and derive "
                "the joint Loewner/Schur stability envelope."
            ),
            "verdict": (
                "The canonical 210 and 1050 tensors vanish at p^2, preserving "
                "H=0 stationarity and eliminating H--126dag mixing there. "
                "Their first 210 variations yield exact rank-3 and rank-7 "
                "H--210 blocks that annihilate all gauge tangents and must be "
                "included in the enlarged local-stability analysis."
            ),
        }
    )


def build_report() -> dict[str, Any]:
    return projection_audit()


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Phi² H 126dag selected-vacuum projection\n\n"
        f"**Status:** `{report['status']}`\n\n"
        + report["verdict"]
        + "\n\n"
        + f"**Next:** {report['next_exact_target']}\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
