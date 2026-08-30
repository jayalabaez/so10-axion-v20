#!/usr/bin/env python3
"""V39 live-soft-RGE and 5D gaugino-mediation boundary audit.

The calculation makes the strongest spectrum-side advance available without
inventing a hidden sector.  A transient formal-soft mirror of the active V39
split-six/Z3 source is consumed, and the gauge-only one-loop trajectory from a
sequestered gaugino-mediation boundary is solved analytically.  The benchmark
is a calculational witness, not a claimed prediction: singlet soft masses,
mu/Bmu, thresholds and the broken-phase pole system remain microscopic inputs.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
MODEL_NAME = "PSZ4RZ5610Z3SUSYV39"
RGE_PATH = ROOT / "SUSY_V39_Z3_FORMAL_SOFT_RGE_ATTESTATION.json"
DECLARED_RGE_PATH = ROOT / "SUSY_V39_SARAH_RGE_ATTESTATION.json"
REPORT_JSON = ROOT / "SUSY_V39_SOFT_BOUNDARY_AUDIT.json"
REPORT_MD = ROOT / "SUSY_V39_SOFT_BOUNDARY_AUDIT.md"

GAUGE_ORDER = ("SU4", "SU2L", "SU2R")
ONE_LOOP_B = {"SU4": 2.0, "SU2L": 5.0, "SU2R": 9.0}

# Quadratic Casimirs in the V37 representations.  Singlet entries are retained
# so the unlifted directions are a tested result rather than a prose caveat.
CASIMIRS: dict[str, dict[str, float]] = {
    "H": {"SU4": 0.0, "SU2L": 0.75, "SU2R": 0.75},
    "Q": {"SU4": 15.0 / 8.0, "SU2L": 0.75, "SU2R": 0.0},
    "Qc": {"SU4": 15.0 / 8.0, "SU2L": 0.0, "SU2R": 0.75},
    "X": {"SU4": 0.0, "SU2L": 0.0, "SU2R": 0.0},
    "Sc": {"SU4": 15.0 / 8.0, "SU2L": 0.0, "SU2R": 0.75},
    "Sbc": {"SU4": 15.0 / 8.0, "SU2L": 0.0, "SU2R": 0.75},
    "SigC": {"SU4": 2.5, "SU2L": 0.0, "SU2R": 0.0},
    "SigBc": {"SU4": 2.5, "SU2L": 0.0, "SU2R": 0.0},
    "PsiBar": {"SU4": 15.0 / 8.0, "SU2L": 0.75, "SU2R": 0.0},
    "Psi": {"SU4": 15.0 / 8.0, "SU2L": 0.75, "SU2R": 0.0},
    "PsiC": {"SU4": 15.0 / 8.0, "SU2L": 0.0, "SU2R": 0.75},
    "PsiCBar": {"SU4": 15.0 / 8.0, "SU2L": 0.0, "SU2R": 0.75},
    "P": {"SU4": 0.0, "SU2L": 0.0, "SU2R": 0.0},
    "Nv": {"SU4": 0.0, "SU2L": 0.0, "SU2R": 0.0},
    "Pbar": {"SU4": 0.0, "SU2L": 0.0, "SU2R": 0.0},
    "Zp": {"SU4": 0.0, "SU2L": 0.0, "SU2R": 0.0},
    "A2": {"SU4": 0.0, "SU2L": 0.0, "SU2R": 0.0},
    "A32": {"SU4": 0.0, "SU2L": 0.0, "SU2R": 0.0},
    "A15": {"SU4": 0.0, "SU2L": 0.0, "SU2R": 0.0},
    "A17": {"SU4": 0.0, "SU2L": 0.0, "SU2R": 0.0},
    "A16": {"SU4": 0.0, "SU2L": 0.0, "SU2R": 0.0},
    "D2": {"SU4": 0.0, "SU2L": 0.0, "SU2R": 0.0},
    "Db2": {"SU4": 0.0, "SU2L": 0.0, "SU2R": 0.0},
    "D17": {"SU4": 0.0, "SU2L": 0.0, "SU2R": 0.0},
    "Db17": {"SU4": 0.0, "SU2L": 0.0, "SU2R": 0.0},
    "D16": {"SU4": 0.0, "SU2L": 0.0, "SU2R": 0.0},
    "Db16": {"SU4": 0.0, "SU2L": 0.0, "SU2R": 0.0},
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_rge() -> dict[str, Any]:
    if not RGE_PATH.is_file():
        raise RuntimeError(
            "live soft RGE attestation is missing; run tools/derive-susy-v33-ps-rges.wls with --soft-mirror"
        )
    payload = json.loads(RGE_PATH.read_text(encoding="utf-8"))
    counts = payload.get("beta_counts", {})
    required_positive = (
        "gauge",
        "soft_trilinear",
        "soft_bilinear",
        "soft_linear",
        "soft_scalar_mass",
        "gaugino_mass",
    )
    if not payload.get("two_loop_RGE_calculation_succeeded"):
        raise RuntimeError("live SARAH soft RGE derivation did not succeed")
    if not payload.get("source_soft_terms_enabled"):
        raise RuntimeError("soft mirror did not enable soft terms")
    if payload.get("model") != MODEL_NAME or payload.get("mode") != "formal_soft_mirror":
        raise RuntimeError("attestation is not the active V39 formal soft mirror")
    if not payload.get("model_initialized"):
        raise RuntimeError("formal soft-mirror model did not initialize")
    expected_one_loop = ["2*g4^3", "5*gL^3", "9*gR^3"]
    if payload.get("one_loop_gauge_coefficients_input_form") != expected_one_loop:
        raise RuntimeError("live one-loop gauge coefficients do not equal (1,5,9)")
    mirror_hash = payload.get("soft_mirror_source_sha256")
    if not isinstance(mirror_hash, str) or len(mirror_hash) != 64:
        raise RuntimeError("formal soft-mirror source hash is missing")
    if any(int(counts.get(name, 0)) <= 0 for name in required_positive):
        raise RuntimeError("live SARAH output is missing one or more soft beta classes")
    return payload


def load_declared_rge() -> dict[str, Any]:
    """Verify that the unchanged source itself, not only its soft mirror, loads."""

    if not DECLARED_RGE_PATH.is_file():
        raise RuntimeError("declared-source V39 SARAH attestation is missing")
    payload = json.loads(DECLARED_RGE_PATH.read_text(encoding="utf-8"))
    if payload.get("model") != MODEL_NAME or payload.get("mode") != "declared_source":
        raise RuntimeError("declared-source attestation is not the active V39 model")
    if not payload.get("model_initialized") or not payload.get("two_loop_RGE_calculation_succeeded"):
        raise RuntimeError("active V39 source did not complete its supersymmetric two-loop RGE derivation")
    if payload.get("source_soft_terms_enabled"):
        raise RuntimeError("active V39 source unexpectedly contains a declared soft sector")
    expected_one_loop = ["2*g4^3", "5*gL^3", "9*gR^3"]
    if payload.get("one_loop_gauge_coefficients_input_form") != expected_one_loop:
        raise RuntimeError("active V39 declared-source gauge coefficients do not equal (2,5,9)")
    return payload


def one_loop_gaugino_mediation_witness(
    *, g_unified: float = 0.70, compactification_over_ps: float = 100.0, m_half_gev: float = 5.0e4
) -> dict[str, Any]:
    if not 0.0 < g_unified < 1.0:
        raise ValueError("g_unified must be perturbative and positive")
    if compactification_over_ps <= 1.0 or m_half_gev <= 0.0:
        raise ValueError("the hierarchy and gaugino mass must be positive")

    log_ratio = math.log(compactification_over_ps)
    gauge_couplings: dict[str, float] = {}
    gaugino_ratios: dict[str, float] = {}
    for gauge in GAUGE_ORDER:
        inverse_g2 = 1.0 / (g_unified * g_unified) + ONE_LOOP_B[gauge] * log_ratio / (8.0 * math.pi**2)
        gauge_couplings[gauge] = math.sqrt(1.0 / inverse_g2)
        gaugino_ratios[gauge] = gauge_couplings[gauge] ** 2 / g_unified**2

    scalar_rows: dict[str, dict[str, Any]] = {}
    for field, casimirs in CASIMIRS.items():
        m2_ratio = sum(
            2.0
            * casimirs[gauge]
            / ONE_LOOP_B[gauge]
            * (1.0 - gaugino_ratios[gauge] ** 2)
            for gauge in GAUGE_ORDER
        )
        # Numerical roundoff cannot carry physical information here.
        if abs(m2_ratio) < 1.0e-14:
            m2_ratio = 0.0
        scalar_rows[field] = {
            "casimirs": casimirs,
            "m2_over_Mhalf2_gauge_only": m2_ratio,
            "mass_GeV_if_positive": m_half_gev * math.sqrt(m2_ratio) if m2_ratio > 0.0 else 0.0,
            "gauge_lifted": m2_ratio > 0.0,
        }

    charged = [field for field, row in scalar_rows.items() if any(row["casimirs"].values())]
    singlets = [field for field, row in scalar_rows.items() if not any(row["casimirs"].values())]
    return {
        "boundary_scale_ratio_Mc_over_vPS": compactification_over_ps,
        "g_unified_at_Mc": g_unified,
        "Mhalf_GeV_at_Mc": m_half_gev,
        "boundary": {
            "M4_equals_ML_equals_MR": "Mhalf",
            "brane_chiral_m2": 0,
            "brane_A_terms": 0,
            "interpretation": "sequestered 5D gaugino-mediation witness at Mc",
            "scope_assumption": (
                "U1X and U1H are already broken or localized above Mc; only the Spin(10)/PS gauge multiplet "
                "propagates between Mc and vPS, with negligible brane kinetic/contact and KK threshold terms."
            ),
        },
        "one_loop_solution": {
            "formula_gauge": "1/g_a(vPS)^2 = 1/g_U^2 + b_a log(Mc/vPS)/(8 pi^2)",
            "formula_gaugino": "M_a(vPS)/Mhalf = g_a(vPS)^2/g_U^2",
            "formula_scalar": "m_i^2/Mhalf^2 = sum_a 2 C_a(i)/b_a * (1-(M_a/Mhalf)^2)",
            "one_loop_b_SU4_SU2L_SU2R": [ONE_LOOP_B[gauge] for gauge in GAUGE_ORDER],
            "gauge_couplings_at_vPS": gauge_couplings,
            "gaugino_mass_ratios_at_vPS": gaugino_ratios,
            "scalar_rows": scalar_rows,
        },
        "all_PS_charged_m2_positive_in_gauge_only_solution": all(
            scalar_rows[field]["m2_over_Mhalf2_gauge_only"] > 0.0 for field in charged
        ),
        "PS_charged_fields": charged,
        "unlifted_exact_singlets": singlets,
        "all_exact_singlets_remain_unlifted_gauge_only": all(
            scalar_rows[field]["m2_over_Mhalf2_gauge_only"] == 0.0 for field in singlets
        ),
    }


def report() -> dict[str, Any]:
    rge = load_rge()
    declared_rge = load_declared_rge()
    witness = one_loop_gaugino_mediation_witness()
    counts = rge["beta_counts"]
    sources = (
        "susy_v39_soft_boundary_audit.py",
        "test_susy_v39_soft_boundary_audit.py",
        "SUSY_V39_Z3_FORMAL_SOFT_RGE_ATTESTATION.json",
        "SUSY_V39_SARAH_RGE_ATTESTATION.json",
        "tools/derive-susy-v33-ps-rges.wls",
        "models/PSZ4RZ5610Z3SUSYV39/PSZ4RZ5610Z3SUSYV39.m",
    )
    data: dict[str, Any] = {
        "schema": "susy-v39-soft-boundary-audit-v1",
        "status": "V39_ACTIVE_Z3_SOURCE_AND_FORMAL_SOFT_TWO_LOOP_RGES_DERIVED__5D_GAUGINO_MEDIATION_TRAJECTORY_SOLVED__SINGLET_AND_POLE_BOUNDARY_OPEN",
        "live_soft_RGE": {
            "model": rge["model"],
            "engine": rge["engine"],
            "tool": rge["tool"],
            "mode": rge["mode"],
            "two_loop_succeeded": rge["two_loop_RGE_calculation_succeeded"],
            "beta_counts": counts,
            "soft_beta_expression_sha256": rge["soft_beta_expression_sha256"],
            "soft_mirror_source_sha256": rge["soft_mirror_source_sha256"],
            "one_loop_gauge_coefficients_input_form": rge["one_loop_gauge_coefficients_input_form"],
            "attestation_sha256": sha256_file(RGE_PATH),
            "declared_source_attestation_sha256": sha256_file(DECLARED_RGE_PATH),
            "declared_source_soft_terms_enabled": declared_rge["source_soft_terms_enabled"],
            "declared_source_two_loop_succeeded": declared_rge["two_loop_RGE_calculation_succeeded"],
        },
        "gaugino_mediation_witness": witness,
        "exact_boundary_exposed": {
            "advance": (
                "A live transient formal-soft mirror of the active 21-field V39 source has a two-loop standard soft beta system, and the gauge-only 5D gaugino-mediation "
                "trajectory is analytic and positive for every PS-charged chiral multiplet."
            ),
            "obstruction": (
                "X, P, Pbar, Zp, Nv and the anomalon/dark singlets have no gauge Casimir and remain unlifted at this "
                "order. Their soft masses, tadpoles, phases and A/B terms require a microscopic hidden-sector coupling."
            ),
            "why_no_pole_spectrum": (
                "No broken-phase state, canonical numerical Yukawa point, mu/Bmu solution, individual PS/KK thresholds, "
                "or self-energy/covariance prescription follows from the gaugino boundary alone."
            ),
            "active_abelian_parent_alternative": {
                "boundary": (
                    "If U1X and U1H remain bulk/active below Mc, the PS-only solution is inapplicable: kinetic "
                    "mixing and an Abelian gauge/gaugino mass matrix must be evolved."
                ),
                "Tr_X2_light": 1885,
                "Tr_H2_light": 9524,
                "Tr_XH_light": -336,
                "bX_with_plusminus66_breaking_pair": 10597,
                "bH_with_plusminus85_breaking_pair": 23974,
                "gX_max_for_100x_one_loop_headroom": math.sqrt(8.0 * math.pi**2 / (10597.0 * math.log(100.0))),
                "gH_max_for_100x_one_loop_headroom": math.sqrt(8.0 * math.pi**2 / (23974.0 * math.log(100.0))),
            },
        },
        "gate_decisions": {
            "G2_closed": False,
            "G3_closed": False,
            "G4_closed": False,
            "G6_closed": False,
            "G6_calculational_scaffold_advance": True,
            "reason": "A beta system and a boundary ansatz do not select the missing microscopic singlet soft sector or physical pole solution.",
        },
        "literature_basis": [
            "https://arxiv.org/abs/0808.3598",
            "https://arxiv.org/abs/0803.1758",
            "https://arxiv.org/abs/0909.2863",
            "https://arxiv.org/abs/1309.7223",
        ],
        "source_manifest": [
            {
                "path": name,
                "exists": (ROOT / name).is_file(),
                "sha256": sha256_file(ROOT / name) if (ROOT / name).is_file() else None,
            }
            for name in sources
        ],
    }
    data["core_sha256"] = canonical_sha(data)
    return data


def markdown(data: Mapping[str, Any]) -> str:
    witness = data["gaugino_mediation_witness"]
    counts = data["live_soft_RGE"]["beta_counts"]
    return f"""# SUSY V39 live-soft and boundary audit

- Status: `{data['status']}`
- Core: `{data['core_sha256']}`
- Full G2/G3/G4/G6 closure: **no**.

## Live result

SARAH initialized both the declared active V39 source and a transient
formal-soft mirror of its 21-field split-six/Z3 field content, then
completed its two-loop calculation.  The derived soft rows are trilinear
`{counts['soft_trilinear']}`, bilinear `{counts['soft_bilinear']}`, linear
`{counts['soft_linear']}`, scalar-mass `{counts['soft_scalar_mass']}`, and
gaugino `{counts['gaugino_mass']}`.

## 5D gaugino-mediation witness

For `gU={witness['g_unified_at_Mc']}`, `Mc/vPS={witness['boundary_scale_ratio_Mc_over_vPS']}`
and `M1/2={witness['Mhalf_GeV_at_Mc']:.1f} GeV`, assuming `U1X,U1H` are broken
or localized above `Mc`, the analytic gauge-only
one-loop solution gives positive soft mass-squared to every PS-charged chiral
multiplet.  The exact singlets remain unlifted:
`{', '.join(witness['unlifted_exact_singlets'])}`.

This is the decisive boundary: gaugino mediation is a viable calculational
route, but it cannot determine the PQ/driver/anomalon vacuum, mu/Bmu, the
broken-phase pole matrices, or threshold covariance without a microscopic
singlet mediation sector.  No full gate is promoted.

Literature basis: [5D SO(10) gaugino mediation](https://arxiv.org/abs/0808.3598),
[orbifold SO(10)/Pati--Salam construction](https://arxiv.org/abs/0803.1758), and
[SARAH](https://arxiv.org/abs/0909.2863).
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write and args.check:
        raise SystemExit("choose at most one of --write and --check")
    data = report()
    if args.write:
        REPORT_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        REPORT_MD.write_text(markdown(data), encoding="utf-8")
    if args.check:
        if not REPORT_JSON.is_file() or not REPORT_MD.is_file():
            raise SystemExit("generated V39 soft report is missing; run with --write")
        if json.loads(REPORT_JSON.read_text(encoding="utf-8")) != data:
            raise SystemExit("generated V39 soft JSON is stale; run with --write")
        if REPORT_MD.read_text(encoding="utf-8") != markdown(data):
            raise SystemExit("generated V39 soft Markdown is stale; run with --write")
        print("SUSY V39 soft-boundary audit: PASS")
        return
    print(json.dumps(data, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
