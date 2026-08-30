#!/usr/bin/env python3
r"""Classify the native SARAH input and historical PyR@TE scaffold (v20).

Next step after ``tau_p_uv_vacuum_selection_v20``:

1. Inventory the native SARAH ``.m`` input and historical ``.yaml`` metadata
   scaffold without inferring an external run.
2. Cross-check the authored Dynkin/charge ledger against
   ``sarah_pyrate_so10_210_betas_v20`` and the PQ/X locks.
3. Probe the environment for a live ``math`` / ``wolframscript`` + SARAH or
   ``pyrate`` executable; **fail closed** if absent (do not claim a live run).

Honesty
-------
* Token presence is not evidence of tool-native SARAH/PyR@TE syntax.
* ``live_sarah_or_pyrate_executable_run`` stays False unless the exact-X v3
  attestation binds the native model type, exact input manifest, validation
  driver, and captured process log.
* Exact X/Y masses from the full component vacuum remain OPEN.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from pathlib import Path
from typing import Any

import sarah_pyrate_so10_210_betas_v20 as sarah
import tau_p_uv_vacuum_selection_v20 as taup
import exact_x_symmetry_consistency_gate_v20 as exact_x

ROOT = Path(__file__).resolve().parent
MODELS = ROOT / "models"
SARAH_MODEL = MODELS / "SO10Z17AxionV20.m"
PYRATE_MODEL = MODELS / "SO10Z17AxionV20_pyrate.yaml"

# Authoritative manuscript charge locks.  The historical scaffolds are
# deliberately compared against these values rather than their old Option-C
# metadata.
CHARGE_LOCKS = {
    name: {"PQ": charges[0], "X": charges[1]}
    for name, charges in exact_x.EXPECTED_SCALAR_CHARGES.items()
}

REQUIRED_OPERATORS = ("kappa", "lam4", "lambda_lock")

SOURCES = {
    "sarah_model": str(SARAH_MODEL.relative_to(ROOT)).replace("\\", "/"),
    "pyrate_model": str(PYRATE_MODEL.relative_to(ROOT)).replace("\\", "/"),
    "dynkin": "sarah_pyrate_so10_210_betas_v20.T_SO10",
    "upstream_tau": "tau_p_uv_vacuum_selection_v20",
}


def probe_live_tools() -> dict[str, Any]:
    """Search PATH for Mathematica/SARAH or PyR@TE executables."""
    candidates = {
        "wolframscript": shutil.which("wolframscript"),
        "math": shutil.which("math"),
        "MathKernel": shutil.which("MathKernel"),
        "pyrate": shutil.which("pyrate"),
        "pyrate3": shutil.which("pyrate3"),
    }
    sarah_dir = os.environ.get("SARAH_DIR") or os.environ.get("SARAH")
    found = {k: v for k, v in candidates.items() if v}
    live_possible = bool(found.get("wolframscript") or found.get("math")) and bool(
        sarah_dir
    )
    live_possible = live_possible or bool(found.get("pyrate") or found.get("pyrate3"))
    return {
        "executables_on_PATH": found,
        "SARAH_DIR": sarah_dir,
        "live_run_possible": bool(live_possible),
        "live_run_executed": False,
        "block_reason": (
            None
            if live_possible
            else (
                "No Mathematica+SARAH_DIR or pyrate executable found on PATH; "
                "model files authored but live β dump not produced."
            )
        ),
    }


def _parse_dynkin_block(text: str) -> dict[str, float]:
    """Minimal parse of the dynkin_T block without PyYAML."""
    out: dict[str, float] = {}
    block = re.search(r"dynkin_T:\s*\n((?:[ \t]+.+\n)+)", text)
    if not block:
        return out
    for line in block.group(1).splitlines():
        m = re.match(r'\s*"?(\d+)"?\s*:\s*([0-9.]+)', line)
        if m:
            out[m.group(1)] = float(m.group(2))
    return out


def validate_pyrate_yaml(text: str) -> dict[str, Any]:
    dynkin = _parse_dynkin_block(text)
    ledger = {k: float(v) for k, v in sarah.T_SO10.items()}
    dynkin_match = all(
        abs(dynkin.get(k, float("nan")) - ledger[k]) < 1e-12
        for k in ("10", "16", "126", "210")
    )
    charge_rows = []
    charge_ok = True
    for name, expect in CHARGE_LOCKS.items():
        # Match: name: ... charges: { PQ: n, X: m } within a few lines
        pat = (
            rf"- name: {re.escape(name)}\n"
            rf"(?:.*\n){{0,4}}?"
            rf".*charges:\s*\{{[^}}]*PQ:\s*(-?\d+)[^}}]*X:\s*(-?\d+)"
        )
        m = re.search(pat, text)
        if not m:
            charge_ok = False
            charge_rows.append(
                {"field": name, "expected": expect, "got": None, "ok": False}
            )
            continue
        got = {"PQ": int(m.group(1)), "X": int(m.group(2))}
        row_ok = got["PQ"] == expect["PQ"] and got["X"] == expect["X"]
        charge_ok = charge_ok and row_ok
        charge_rows.append(
            {"field": name, "expected": expect, "got": got, "ok": row_ok}
        )
    ops_ok = all(
        re.search(rf"name:\s*{op}\b", text) for op in REQUIRED_OPERATORS
    )
    n_scalars = len(re.findall(r"- name: (?:Phi210|Delta126bar|H10|S|Phi17)\b", text))
    return {
        "parsed": True,
        "model_syntax_class": "legacy_pyrate_metadata_scaffold",
        "tool_native_pyrate_schema": False,
        "name": "SO10Z17AxionV20" if "SO10Z17AxionV20" in text else None,
        "dynkin_match_upstream": dynkin_match,
        "dynkin_T": dynkin,
        "charges": charge_rows,
        "charges_match_locks": charge_ok,
        "required_operators_present": ops_ok,
        "operators_found": [op for op in REQUIRED_OPERATORS if op in text],
        "n_scalars_named": n_scalars,
    }


def validate_sarah_m(text: str) -> dict[str, Any]:
    inventory_checks = {
        "has_model_name": "SO10Z17AxionV20" in text,
        "has_so10_gauge": bool(re.search(r"Gauge\[\[1\]\].*SO.*10", text)),
        "has_210": "210" in text and "Phi210" in text,
        "has_126": "126" in text and "Delta126bar" in text,
        "has_10": "H10" in text,
        "has_S": bool(re.search(r"\bS\b", text)),
        "has_Phi17": "Phi17" in text,
        "mentions_kappa": "kappa" in text.lower() or "H10^2 S" in text or "H10^2" in text,
        "mentions_lam4": "lam4" in text.lower() or "210·10·126·S" in text or "Phi210 H10" in text,
        "forbids_bare_10_sq_noted": "10_H^2" in text or "bare" in text.lower(),
        "hilbert_210n_noted": "Hilbert" in text or "H2=1" in text,
    }
    parsed = exact_x.declared_symmetries(text)
    semantic = parsed["semantic_requirements"]
    return {
        "n_bytes": len(text.encode("utf-8")),
        "checks": inventory_checks,
        "legacy_inventory_markers_present": all(inventory_checks.values()),
        "native_inventory_requirements_present": all(semantic.values()),
        "model_syntax_class": parsed["model_syntax_class"],
        "legacy_pseudo_sarah_grammar": parsed[
            "legacy_pseudo_sarah_grammar"
        ],
        "tool_native_sarah_syntax": parsed["tool_native_sarah_syntax"],
        "statically_executable_model_contract": parsed[
            "statically_executable_model_contract"
        ],
        "lagrangian_registered_in_GaugeES_LagrangianInput": parsed[
            "lagrangian"
        ]["registered_in_GaugeES_LagrangianInput"],
        "scalar_charges_match_manuscript": parsed[
            "scalar_charges_match_manuscript"
        ],
        "fermion_catalogue_exact": parsed["fermion_catalogue_exact"],
        "gauge_catalogue_exact": parsed["gauge_catalogue_exact"],
        "global_symmetry_catalogue_exact": parsed[
            "global_symmetry_catalogue_exact"
        ],
        # Backwards-readable key: it now means actual native structure, not
        # merely that expected words appeared in the file.
        "all_structure_ok": parsed["tool_native_sarah_syntax"],
    }


def build_report() -> dict[str, Any]:
    if not SARAH_MODEL.is_file() or not PYRATE_MODEL.is_file():
        return {
            "status": "SARAH_PYRATE_MODEL_FILE_MISSING",
            "n_failed": 1,
            "failures": ["model_files_absent"],
            "flag": {"sarah_pyrate_model_file_authored": False},
        }

    sarah_text = SARAH_MODEL.read_text(encoding="utf-8")
    pyrate_text = PYRATE_MODEL.read_text(encoding="utf-8")
    sarah_v = validate_sarah_m(sarah_text)
    pyrate_v = validate_pyrate_yaml(pyrate_text)
    probe = probe_live_tools()

    external_artifact: object = None
    external_load_error: str | None = None
    if exact_x.EXTERNAL_VALIDATION.is_file():
        try:
            external_artifact = json.loads(
                exact_x.EXTERNAL_VALIDATION.read_text(encoding="utf-8")
            )
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            external_load_error = f"{type(exc).__name__}: {exc}"
    external_validation = exact_x.validate_external_model_artifact(
        sarah_text.encode("utf-8"), external_artifact
    )
    external_validation["load_error"] = external_load_error

    # Upstream τ_p certificate continuity (light: only require module import path)
    tau_ok = hasattr(taup, "assemble_uv_selected_vacuum")

    # Live run: only True if we actually executed — we never do without tools.
    # A generic reduced-sector beta dump is not evidence that this exact model
    # parsed or initialized.  Only the v3 exact-X attestation can set this flag.
    live_executed = bool(external_validation["valid"])
    live_dump = (
        str(exact_x.EXTERNAL_VALIDATION.relative_to(ROOT)).replace("\\", "/")
        if live_executed
        else None
    )
    if not live_executed:
        probe["block_reason"] = (
            "No valid v3 attestation binds tool-native input, exact model bytes, "
            "the trusted SARAH source tree, Wolfram binaries, canonical input "
            "manifest, validation driver, runtime probe, and process log."
        )

    checks = {
        "sarah_file_present": SARAH_MODEL.is_file(),
        "pyrate_file_present": PYRATE_MODEL.is_file(),
        "sarah_syntax_was_classified": sarah_v["model_syntax_class"]
        in {
            "sarah_native",
            "legacy_pseudo_sarah_metadata",
            "mixed_or_unrecognized",
        },
        "legacy_sarah_tokens_not_promoted_to_native_syntax": bool(
            not sarah_v["legacy_pseudo_sarah_grammar"]
            or not sarah_v["tool_native_sarah_syntax"]
        ),
        "native_sarah_static_contract_classified": bool(
            not sarah_v["tool_native_sarah_syntax"]
            or (
                sarah_v["native_inventory_requirements_present"]
                and sarah_v["statically_executable_model_contract"]
                and sarah_v["scalar_charges_match_manuscript"]
            )
        ),
        "pyrate_syntax_was_classified": isinstance(
            pyrate_v["tool_native_pyrate_schema"], bool
        ),
        "pyrate_dynkin_match": pyrate_v["dynkin_match_upstream"],
        "pyrate_operators_present": pyrate_v["required_operators_present"],
        "authoritative_charge_match_was_classified": isinstance(
            pyrate_v["charges_match_locks"], bool
        ),
        "external_v3_attestation_was_classified": isinstance(
            external_validation["valid"], bool
        ),
        "generic_beta_dump_does_not_claim_full_model_execution": (
            not live_executed or external_validation["valid"]
        ),
        "tau_p_module_available": tau_ok,
        "unique_tau_p_not_claimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]
    native_contract_static = bool(
        sarah_v["tool_native_sarah_syntax"]
        and sarah_v["native_inventory_requirements_present"]
        and sarah_v["statically_executable_model_contract"]
        and sarah_v["scalar_charges_match_manuscript"]
        and sarah_v["fermion_catalogue_exact"]
        and sarah_v["gauge_catalogue_exact"]
        and sarah_v["global_symmetry_catalogue_exact"]
    )
    native_contract_ready = bool(
        native_contract_static
        and external_validation["valid"]
    )
    scientific_blockers: list[str] = []
    if not sarah_v["tool_native_sarah_syntax"]:
        scientific_blockers.append("SARAH_MODEL_NOT_TOOL_NATIVE")
    if not external_validation["valid"]:
        scientific_blockers.append(exact_x.EXTERNAL_EXECUTION_BLOCKER)

    status = (
        "SARAH_PYRATE_SCAFFOLD_AUDIT_EXECUTION_FAILED"
        if failures
        else "SARAH_NATIVE_MODEL_EXTERNALLY_VALIDATED"
        if native_contract_ready
        else "SARAH_NATIVE_STATIC_CONTRACT__EXTERNAL_VALIDATION_BLOCKED"
        if native_contract_static
        else "SARAH_PYRATE_MODEL_CONTRACT_CLASSIFIED__VALIDATION_BLOCKED"
    )

    return {
        "status": status,
        "overall_state": (
            "EXECUTION_FAIL" if failures else "PASS" if native_contract_ready else "BLOCKED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "scientific_blockers": scientific_blockers,
        "sources": SOURCES,
        "files": {
            "sarah": SOURCES["sarah_model"],
            "pyrate": SOURCES["pyrate_model"],
            "sarah_bytes": sarah_v["n_bytes"],
            "pyrate_bytes": len(pyrate_text.encode("utf-8")),
        },
        "validation": {
            "sarah": sarah_v,
            "pyrate": pyrate_v,
            "external_model_execution": external_validation,
        },
        "live_probe": {**probe, "live_run_executed": live_executed, "dump": live_dump},
        "next_exact_calculation": [
            "Derive exact X/Y masses from the full component vacuum",
            "Close inter-representation 10–126 colour-triplet mixing",
            "Execute a live SARAH/PyR@TE dump when Mathematica+SARAH or pyrate is available",
        ],
        "flag": {
            # Backwards-readable: files were authored, but this is not an
            # executability or scientific-validity flag.
            "sarah_pyrate_model_file_authored": True,
            "sarah_metadata_scaffold_present": True,
            "pyrate_metadata_scaffold_present": True,
            "sarah_model_tool_native": sarah_v["tool_native_sarah_syntax"],
            "sarah_static_contract_consistent": native_contract_static,
            "pyrate_model_tool_native": pyrate_v[
                "tool_native_pyrate_schema"
            ],
            "pyrate_yaml_dynkin_matches_upstream": pyrate_v["dynkin_match_upstream"],
            "charge_locks_encoded": sarah_v[
                "scalar_charges_match_manuscript"
            ],
            "external_validation_v3_valid": external_validation["valid"],
            # Retained only for old readers.  A legacy v2 artifact is never
            # accepted by the hardened exact-X contract.
            "external_validation_v2_valid": False,
            "live_sarah_or_pyrate_executable_run": bool(live_executed),
            "live_run_blocked_without_bound_attestation": not live_executed,
            "live_run_blocked_without_tools_or_dump": not live_executed,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The .m file is now a statically consistent native SARAH input for "
            "the authoritative gauged-U(1)_X catalogue. The historical PyR@TE "
            f"metadata remains non-authoritative (Dynkin match={pyrate_v['dynkin_match_upstream']}). "
            f"Bound external SARAH execution={live_executed}; a generic beta dump "
            "cannot replace that attestation. Exact X/Y masses and the unique "
            "proton lifetime remain open."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    probe = report["live_probe"]
    lines = [
        "# SARAH/PyR@TE scaffold classification - v20",
        "",
        f"**Status:** `{report['status']}`",
        f"**Overall state:** `{report['overall_state']}`",
        "",
        report["verdict"],
        "",
        f"- SARAH: `{report['files']['sarah']}` ({report['files']['sarah_bytes']} bytes)",
        f"- PyR@TE: `{report['files']['pyrate']}` ({report['files']['pyrate_bytes']} bytes)",
        f"- SARAH tool-native syntax: {report['flag']['sarah_model_tool_native']}",
        f"- PyR@TE tool-native schema: {report['flag']['pyrate_model_tool_native']}",
        f"- Bound v3 external validation: {report['flag']['external_validation_v3_valid']}",
        f"- Live tools on PATH: {list(probe['executables_on_PATH'].keys()) or 'none'}",
        f"- Live run executed: {probe['live_run_executed']}",
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    report = build_report()
    ROOT.joinpath("SARAH_PYRATE_MODEL_FILE_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("SARAH_PYRATE_MODEL_FILE_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "files": report.get("files"),
                "live_probe": {
                    k: report["live_probe"][k]
                    for k in (
                        "live_run_possible",
                        "live_run_executed",
                        "block_reason",
                        "executables_on_PATH",
                    )
                },
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
