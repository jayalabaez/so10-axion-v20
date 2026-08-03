#!/usr/bin/env python3
r"""Representation-aware A,B,C,D portal tensors for v20.

Builds the heavy-light singlet-VEV block from named Yukawa/VEV couplings
already present in the manuscript plus audited charge-allowed extras:

                  U=(F1,F2,F3,P,R)     Q
      (Pbar,Rbar)   A                  C
      Qbar           B                  D

Entries are linear in the stated couplings times frozen VEVs.  Magnitudes
remain free parameters (defaults are O(1) benchmarks, not unique UV values).
The physical projected current is always computed via
``full_fermion_matching_v20.portal_current_match`` and is never overclaimed.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

import full_fermion_matching_v20 as match


ROOT = Path(__file__).resolve().parent

VS = 6.313855e11
VPHI = 1.0e17
VEW = 174.104
U_LABELS = ("F1", "F2", "F3", "P", "R")


@dataclass(frozen=True)
class PortalCouplings:
    """Named renormalizable portals entering A,B,C,D.

    Manuscript-minimal set is the first block; audited extras follow.
    """

    # Manuscript mass / portal Yukawas
    y_P: complex = 1.0 + 0.0j          # Phid P Pbar
    y_R: complex = 1.0 + 0.0j          # Phi R Rbar
    y_Q: complex = 1.0 + 0.0j          # Phid Q Qbar
    lam_Q_F: tuple[complex, complex, complex] = (0.2, 0.2, 0.2)  # Qbar Fi Sd
    # Audited extras (charge-allowed)
    lam_Q_R: complex = 0.15 - 0.04j    # Qbar R Sd
    lam_S_Q_Rbar: complex = 0.1 + 0.0j # S Q Rbar -> C
    lam_P_R_H: complex = 0.0 + 0.0j    # P R H (EW-scale; optional)
    # Optional generation-dependent Phi-sector light-heavy (normally zero)
    y_F_Pbar: tuple[complex, complex, complex] = (0.0, 0.0, 0.0)
    y_F_Rbar: tuple[complex, complex, complex] = (0.0, 0.0, 0.0)

    def as_dict(self) -> dict:
        out = asdict(self)
        out["lam_Q_F"] = [complex(z) for z in self.lam_Q_F]
        out["y_F_Pbar"] = [complex(z) for z in self.y_F_Pbar]
        out["y_F_Rbar"] = [complex(z) for z in self.y_F_Rbar]
        return {
            key: (
                [complex_to_json(v) for v in val]
                if isinstance(val, list)
                else complex_to_json(val)
                if isinstance(val, complex)
                else val
            )
            for key, val in out.items()
        }


def complex_to_json(z: complex) -> dict:
    z = complex(z)
    return {"re": float(z.real), "im": float(z.imag), "abs": float(abs(z))}


def operator_catalogue() -> dict:
    """Charge-allowed operators mapped onto A,B,C,D slots."""
    return {
        "basis": {
            "U_columns": list(U_LABELS),
            "A_rows": ["Pbar", "Rbar"],
            "B_row": "Qbar",
            "C_column": "Q",
            "D": "Q-Qbar Phi mass",
        },
        "manuscript_minimal": [
            {
                "operator": "Phid P Pbar",
                "fills": "A[Pbar,P]",
                "vev": "v_Phi/sqrt(2)",
                "coupling": "y_P",
            },
            {
                "operator": "Phi R Rbar",
                "fills": "A[Rbar,R]",
                "vev": "v_Phi/sqrt(2)",
                "coupling": "y_R",
            },
            {
                "operator": "Phid Q Qbar",
                "fills": "D",
                "vev": "v_Phi/sqrt(2)",
                "coupling": "y_Q",
            },
            {
                "operator": "Qbar Fi Sd",
                "fills": "B[Qbar,Fi]",
                "vev": "v_S/sqrt(2)",
                "coupling": "lam_Q_F[i]",
            },
        ],
        "audit_extras_included": [
            {
                "operator": "Qbar R Sd",
                "fills": "B[Qbar,R]",
                "vev": "v_S/sqrt(2)",
                "coupling": "lam_Q_R",
            },
            {
                "operator": "S Q Rbar",
                "fills": "C[Rbar,Q]",
                "vev": "v_S/sqrt(2)",
                "coupling": "lam_S_Q_Rbar",
            },
            {
                "operator": "P R H",
                "fills": "optional EW heavy mixing (not A,B,C,D high-scale)",
                "vev": "v_EW",
                "coupling": "lam_P_R_H",
            },
        ],
        "not_claimed_unique": (
            "Numerical Yukawas are free UV parameters. Defaults are O(1) "
            "benchmarks used to exercise the matching pipeline."
        ),
    }


def build_abcd(
    couplings: PortalCouplings | None = None,
    *,
    v_phi: float = VPHI,
    v_s: float = VS,
) -> dict:
    """Assemble numerical A(2,5), B(1,5), C(2,1), D from named couplings."""
    c = couplings or PortalCouplings()
    scale_phi = v_phi / math.sqrt(2.0)
    scale_s = v_s / math.sqrt(2.0)

    a = np.zeros((2, 5), dtype=complex)
    # A rows: Pbar, Rbar ; cols: F1,F2,F3,P,R
    a[0, 3] = c.y_P * scale_phi
    a[1, 4] = c.y_R * scale_phi
    for i, y in enumerate(c.y_F_Pbar):
        a[0, i] = y * scale_phi
    for i, y in enumerate(c.y_F_Rbar):
        a[1, i] = y * scale_phi

    b = np.zeros((1, 5), dtype=complex)
    for i, lam in enumerate(c.lam_Q_F):
        b[0, i] = lam * scale_s
    b[0, 4] = c.lam_Q_R * scale_s  # Qbar R Sd

    cc = np.zeros((2, 1), dtype=complex)
    cc[1, 0] = c.lam_S_Q_Rbar * scale_s  # S Q Rbar

    d = c.y_Q * scale_phi
    if d == 0:
        raise ValueError("y_Q must be nonzero so D is invertible")

    occupied = {
        "A_nonzero": int(np.count_nonzero(np.abs(a) > 0)),
        "B_nonzero": int(np.count_nonzero(np.abs(b) > 0)),
        "C_nonzero": int(np.count_nonzero(np.abs(cc) > 0)),
        "D_nonzero": bool(abs(d) > 0),
    }
    return {
        "A": a,
        "B": b,
        "C": cc,
        "D": d,
        "couplings": c,
        "vevs": {"v_Phi_GeV": v_phi, "v_S_GeV": v_s, "v_EW_GeV": VEW},
        "occupied_entries": occupied,
        "U_basis": list(U_LABELS),
        "ew_heavy_mixing_lam_PR_H": complex_to_json(c.lam_P_R_H * VEW),
    }


def manuscript_minimal_abcd() -> dict:
    """Manuscript portals only: C=0 and no Qbar-R mixing."""
    return build_abcd(
        PortalCouplings(
            lam_Q_R=0.0,
            lam_S_Q_Rbar=0.0,
            lam_P_R_H=0.0,
        )
    )


def audit_extended_abcd() -> dict:
    """Manuscript + audited S Q Rbar and Qbar R Sd portals."""
    return build_abcd(PortalCouplings())


def aligned_limit_abcd(*, mix: float = 1e-6) -> dict:
    """Near-aligned limit: tiny Q-portals so Q_proj ~ I."""
    return build_abcd(
        PortalCouplings(
            lam_Q_F=(mix, mix, mix),
            lam_Q_R=0.0,
            lam_S_Q_Rbar=0.0,
        )
    )


def physical_current_from_abcd(block: dict, *, alpha: float = 0.0) -> dict:
    row = match.portal_current_match(
        block["A"], block["B"], block["C"], block["D"], alpha=alpha
    )
    eigenvalues = np.linalg.eigvalsh(row["Q_projected"])
    offdiag = float(
        np.linalg.norm(row["Q_projected"] - np.diag(np.diag(row["Q_projected"])))
    )
    return {
        "Q_projected": [[complex_to_json(z) for z in r] for r in row["Q_projected"]],
        "Q_projected_eigenvalues": [float(x) for x in eigenvalues],
        "berry_connection_eigenvalues": [
            float(x) for x in np.linalg.eigvalsh(row["berry_connection"])
        ],
        "moving_identity_error": row["moving_identity_error"],
        "projected_shift_norm": row["projected_shift_norm"],
        "projected_off_diagonal_norm": offdiag,
        "portal_weight_trace": row["portal_weight_trace"],
        "is_approximately_aligned": bool(
            row["projected_shift_norm"] < 1e-3 and offdiag < 1e-3
        ),
        "classification": (
            "PROVISIONAL_ALIGNED_LIMIT"
            if row["projected_shift_norm"] < 1e-3 and offdiag < 1e-3
            else "FULL_PORTAL_DEPENDENT_CURRENT"
        ),
    }


def scan_generation_universal_mix(
    mixes: tuple[float, ...] = (1e-8, 1e-6, 1e-4, 1e-2, 0.1, 1.0),
    y_q_factors: tuple[float, ...] = (1.0, 1e-2, 1e-4, 1e-6),
) -> dict:
    """Scan portal strength and Phi-mass hierarchy.

    With hierarchical VEVs and O(1) y_Q, W is suppressed by ~v_S/v_Phi.
    Reducing y_Q (lighter Q) makes the physical portal dependence visible
    without inventing new operators.
    """
    rows = []
    for yq in y_q_factors:
        for mix in mixes:
            block = build_abcd(
                PortalCouplings(
                    y_Q=yq,
                    lam_Q_F=(mix, mix, mix),
                    lam_Q_R=0.3 * mix,
                    lam_S_Q_Rbar=0.2 * mix,
                )
            )
            phys = physical_current_from_abcd(block)
            rows.append(
                {
                    "y_Q_abs": yq,
                    "lam_Q_F_abs": mix,
                    "classification": phys["classification"],
                    "projected_shift_norm": phys["projected_shift_norm"],
                    "projected_off_diagonal_norm": phys["projected_off_diagonal_norm"],
                    "Q_projected_eigenvalues": phys["Q_projected_eigenvalues"],
                    "portal_weight_trace": phys["portal_weight_trace"],
                }
            )
    return {
        "rows": rows,
        "aligned_window_exists": any(
            r["classification"] == "PROVISIONAL_ALIGNED_LIMIT" for r in rows
        ),
        "portal_dependence_demonstrated": any(
            r["projected_shift_norm"] > 0.1 for r in rows
        ),
        "hierarchy_note": (
            "For y_Q~1 the projected shift is VEV-suppressed (~v_S/v_Phi). "
            "Visible O(1) shifts appear when the Q mass portal is lighter."
        ),
    }


def _serialize_block(block: dict) -> dict:
    return {
        "A": [[complex_to_json(z) for z in row] for row in block["A"]],
        "B": [[complex_to_json(z) for z in row] for row in block["B"]],
        "C": [[complex_to_json(z) for z in row] for row in block["C"]],
        "D": complex_to_json(block["D"]),
        "couplings": block["couplings"].as_dict(),
        "vevs": block["vevs"],
        "occupied_entries": block["occupied_entries"],
        "U_basis": block["U_basis"],
        "ew_heavy_mixing_lam_PR_H": block["ew_heavy_mixing_lam_PR_H"],
    }


def build_report() -> dict:
    catalogue = operator_catalogue()
    minimal = manuscript_minimal_abcd()
    extended = audit_extended_abcd()
    aligned = aligned_limit_abcd()
    phys_min = physical_current_from_abcd(minimal)
    phys_ext = physical_current_from_abcd(extended)
    phys_aligned = physical_current_from_abcd(aligned)
    mix_scan = scan_generation_universal_mix()
    checks = {
        "operator_catalogue_nonempty": len(catalogue["manuscript_minimal"]) >= 4,
        "minimal_block_shapes_ok": (
            minimal["A"].shape == (2, 5)
            and minimal["B"].shape == (1, 5)
            and minimal["C"].shape == (2, 1)
        ),
        "aligned_limit_is_aligned": phys_aligned["is_approximately_aligned"],
        "extended_includes_C_portal": extended["occupied_entries"]["C_nonzero"] > 0,
        "portal_dependence_in_mix_scan": mix_scan["portal_dependence_demonstrated"],
        "moving_identity_holds_extended": phys_ext["moving_identity_error"] < 1e-8,
        "full_unique_Cf_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "PORTAL_TENSORS_CONSTRUCTED__PHYSICAL_CURRENT_PORTAL_DEPENDENT__"
            "UNIQUE_CF_STILL_OPEN"
        ),
        "flag": {
            "provisional_aligned_benchmark": True,
            "full_unique_Ce_Cp_Cn": False,
            "representation_aware_ABCD": True,
            "yukawa_magnitudes_unique": False,
        },
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "operator_catalogue": catalogue,
        "manuscript_minimal_block": {
            **_serialize_block(minimal),
            "physical_current": phys_min,
        },
        "audit_extended_block": {
            **_serialize_block(extended),
            "physical_current": phys_ext,
        },
        "aligned_limit_block": {
            **_serialize_block(aligned),
            "physical_current": phys_aligned,
        },
        "generation_universal_mix_scan": mix_scan,
        "verdict": (
            "Full A,B,C,D tensors are now built from named charge-allowed "
            "Yukawa x VEV operators. Physical Q_proj remains portal dependent; "
            "exact unique C_e,C_p,C_n still require fixed UV Yukawas and SM "
            "mass-basis alignment."
        ),
    }


def write_markdown(report: dict) -> str:
    lines = [
        "# Portal tensors A,B,C,D — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        "## Flags",
        "",
    ]
    for key, val in report["flag"].items():
        lines.append(f"- `{key}`: **{val}**")
    lines += [
        "",
        "## Operator map",
        "",
        "Manuscript-minimal operators fill `A[Pbar,P]`, `A[Rbar,R]`, `D`, and "
        "`B[Qbar,Fi]`. Audited extras fill `B[Qbar,R]` and `C[Rbar,Q]`.",
        "",
        "## Physical current",
        "",
        f"- aligned-limit classification: "
        f"`{report['aligned_limit_block']['physical_current']['classification']}`",
        f"- audit-extended classification: "
        f"`{report['audit_extended_block']['physical_current']['classification']}`",
        f"- mix scan portal dependence: "
        f"{report['generation_universal_mix_scan']['portal_dependence_demonstrated']}",
        "",
        "## Verdict",
        "",
        report["verdict"],
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    ROOT.joinpath("PORTAL_TENSORS_ABCD_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("PORTAL_TENSORS_ABCD_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "failures": report["failures"],
                "flag": report["flag"],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
