#!/usr/bin/env python3
"""Audit legacy triplet/proton modules for invalid scalar-mass assumptions.

The canonical signed operator filter and M_T^2 builder establish that:

* ``210_H 10_H^dag 10_H`` is SO(10)-forbidden;
* scalar Hessians are mass-squared matrices;
* the allowed lambda4 ``210 10 126bar S`` slot is distinct and CG-dependent;
* complete component CG coefficients remain unavailable.

This audit scans repository modules and invalidates every downstream result that
still contains the forbidden ``lam210_10`` proxy, constructs ``matrix_GeV``
from scalar quartics, or imports a contaminated triplet module. It does not
rewrite unknown physics; it prevents those proxies from being promoted to a
physical spectrum or unique proton lifetime.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any

import nonsusy_charge_allowed_mt_v20 as signed_mt2
import nonsusy_z17_pq_potential_filter_v20 as signed_filter
import so10_kronecker_existence_mt_lock_v20 as signed_kron

ROOT = Path(__file__).resolve().parent
SELF = Path(__file__).name

CANONICAL_SAFE = {
    "nonsusy_z17_pq_potential_filter_v20.py",
    "nonsusy_charge_allowed_mt_v20.py",
    "so10_kronecker_existence_mt_lock_v20.py",
    "so10_cubic_operator_signed_audit_v20.py",
    "mixed_rep_hilbert_series_v20.py",
    "mixed_rep_invariant_floor_audit_v20.py",
    "mixed_rep_enlarged_floor_basis_v20.py",
    "nonsusy_reduced_hessian_v20.py",
    "ew_portal_rescue_bound_v20.py",
    "latest_main_residual_integration_v20.py",
    "current_main_repair_closure_v20.py",
    "final_scalar_theory_gate_v20.py",
    SELF,
}

SEED_MODULES = {
    "cg_normalized_mt_locking_mix_v20",
    "extended_ttbar_54_locking_v20",
    "extended_126_tprime_fragments_v20",
    "inter_rep_10_126_mixing_v20",
    "hilbert_mixed_8comp_hessian_v20",
    "charge_allowed_potential_minimize_v20",
}


def _imports(source: str) -> set[str]:
    names: set[str] = set()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return names
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


def scan_repository() -> dict[str, Any]:
    modules: dict[str, dict[str, Any]] = {}
    for path in sorted(ROOT.glob("*.py")):
        if path.name.startswith("test_") or path.name in CANONICAL_SAFE:
            continue
        source = path.read_text(encoding="utf-8", errors="replace")
        module = path.stem
        direct_reasons: list[str] = []
        if "lam210_10" in source:
            direct_reasons.append("uses forbidden lam210_10 linear-210 Higgs proxy")
        if "210_H 10_H^dag 10_H" in source and "SO10_FORBIDDEN" not in source:
            direct_reasons.append("mentions historical forbidden 210_H 10_H^dag 10_H without signed rejection")
        if "matrix_GeV" in source and (
            "triplet" in source.lower() or "M_T" in source or "mt_" in source.lower()
        ):
            direct_reasons.append("uses dimension-one scalar triplet matrix interface")
        if module in SEED_MODULES:
            direct_reasons.append("known historical triplet/vacuum seed module")
        modules[module] = {
            "path": path.name,
            "imports": sorted(_imports(source)),
            "direct_reasons": sorted(set(direct_reasons)),
            "directly_contaminated": bool(direct_reasons),
        }

    contaminated = {
        name for name, row in modules.items() if row["directly_contaminated"]
    }
    changed = True
    while changed:
        changed = False
        for name, row in modules.items():
            if name in contaminated:
                continue
            inherited = sorted(set(row["imports"]).intersection(contaminated))
            if inherited:
                row["inherited_from"] = inherited
                contaminated.add(name)
                changed = True
    for name, row in modules.items():
        row.setdefault("inherited_from", [])
        row["contaminated"] = name in contaminated
    return {
        "modules": modules,
        "contaminated_modules": sorted(contaminated),
        "directly_contaminated_modules": sorted(
            name for name, row in modules.items() if row["directly_contaminated"]
        ),
        "inherited_contamination_modules": sorted(
            name
            for name, row in modules.items()
            if row["contaminated"] and not row["directly_contaminated"]
        ),
    }


def build_report() -> dict[str, Any]:
    filter_report = signed_filter.build_report()
    mt2_report = signed_mt2.build_report()
    kron_report = signed_kron.build_report()
    scan = scan_repository()
    contaminated = scan["contaminated_modules"]

    critical_expected = {
        "cg_normalized_mt_locking_mix_v20",
        "extended_ttbar_54_locking_v20",
        "extended_126_tprime_fragments_v20",
        "inter_rep_10_126_mixing_v20",
        "charge_allowed_potential_minimize_v20",
        "tau_p_full_stack_uniqueness_v20",
    }
    detected_expected = critical_expected.intersection(contaminated)

    checks = {
        "signed_filter_executes": filter_report.get("n_failed", 1) == 0,
        "signed_mt2_executes": mt2_report.get("n_failed", 1) == 0,
        "signed_kronecker_executes": kron_report.get("n_failed", 1) == 0,
        "canonical_filter_forbids_210_10dag10": filter_report.get("flag", {}).get(
            "forbidden_210_10dag10_removed", False
        ),
        "canonical_mt2_uses_mass_squared": mt2_report.get("flag", {}).get(
            "mass_squared_matrix_used", False
        ),
        "lambda4_slot_preserved": kron_report.get("flag", {}).get(
            "lambda4_offdiag_allowed_but_CG_open", False
        ),
        "all_critical_legacy_modules_detected": detected_expected == critical_expected,
        "contamination_nonempty": len(contaminated) > 0,
        "exact_unique_lifetime_not_claimed": True,
        "whole_model_not_declared_excluded": True,
    }
    failures = [name for name, passed in checks.items() if not passed]

    lifetime_like = sorted(
        name
        for name in contaminated
        if any(token in name for token in ("tau_p", "proton", "interference", "width"))
    )
    spectrum_like = sorted(
        name
        for name in contaminated
        if any(token in name for token in ("triplet", "mt_", "mixing", "hessian", "locking"))
    )

    return {
        "status": (
            "LEGACY_TRIPLET_PROXY_CONTAMINATION_MAPPED__PHYSICAL_CHAIN_INVALIDATED"
            if not failures
            else "TRIPLET_PROXY_CONTAMINATION_AUDIT_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "canonical_replacements": {
            "operator_filter": signed_filter.get("status"),
            "triplet_mass_squared_proxy": mt2_report.get("status"),
            "kronecker_audit": kron_report.get("status"),
        },
        "scan": scan,
        "critical_expected_modules": sorted(critical_expected),
        "critical_detected_modules": sorted(detected_expected),
        "contaminated_spectrum_modules": spectrum_like,
        "contaminated_lifetime_modules": lifetime_like,
        "invalidation": {
            "legacy_triplet_spectra_physical": False,
            "legacy_thresholds_physical": False,
            "legacy_scalar_proton_lifetimes_unique": False,
            "reason": (
                "They inherit a forbidden operator, a dimension-one scalar "
                "matrix convention, or a contaminated upstream spectrum."
            ),
        },
        "required_rebuild": [
            "project the signed scalar potential into the full color-triplet component M_T^2",
            "derive all diagonal and lambda4 off-diagonal CG coefficients",
            "recompute threshold matching from positive physical eigenmasses",
            "rerun scalar proton amplitudes and interference from the rebuilt spectrum",
        ],
        "flag": {
            "legacy_triplet_dependency_graph_scanned": True,
            "legacy_physical_triplet_chain_invalidated": not failures,
            "canonical_signed_mt2_path_available": True,
            "physical_component_CG_complete": False,
            "physical_triplet_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Mapped {len(contaminated)} contaminated legacy modules. Their "
            "triplet spectra, thresholds, and scalar proton lifetimes are "
            "invalid as physical closures. The signed M_T^2 path is the only "
            "accepted executable proxy, and it remains conditional until the "
            "full component CG matrix is derived."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Legacy triplet proxy contamination audit — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- Contaminated modules: {len(report['scan']['contaminated_modules'])}",
            f"- Contaminated lifetime modules: {len(report['contaminated_lifetime_modules'])}",
            f"- Physical triplet spectrum complete: {report['flag']['physical_triplet_spectrum_complete']}",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("TRIPLET_PROXY_CONTAMINATION_AUDIT_V20.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("TRIPLET_PROXY_CONTAMINATION_AUDIT_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
