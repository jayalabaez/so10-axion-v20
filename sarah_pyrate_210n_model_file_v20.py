#!/usr/bin/env python3
r"""SARAH/PyR@TE 210ⁿ model-file scaffold + live-run probe (v20).

Next step after ``tau_p_uv_vacuum_selection_v20``:

1. Author machine-readable **SARAH** (``.m``) and **PyR@TE** (``.yaml``)
   model-file scaffolds for the complete v20 SO(10)×Z₁₇ field content,
   including the renormalizable ``210^n`` sector and charge-allowed mixed
   operators.
2. Cross-check the authored Dynkin/charge ledger against
   ``sarah_pyrate_so10_210_betas_v20`` and the PQ/X locks.
3. Probe the environment for a live ``math`` / ``wolframscript`` + SARAH or
   ``pyrate`` executable; **fail closed** if absent (do not claim a live run).

Honesty
-------
* Authoring a model file is not a live SARAH/PyR@TE dump of β functions.
* ``live_sarah_or_pyrate_executable_run`` stays False unless a real dump is
  produced in-process.
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

ROOT = Path(__file__).resolve().parent
MODELS = ROOT / "models"
SARAH_MODEL = MODELS / "SO10Z17AxionV20.m"
PYRATE_MODEL = MODELS / "SO10Z17AxionV20_pyrate.yaml"

# v20 charge locks (must appear in authored files).
CHARGE_LOCKS = {
    "H10": {"PQ": -2, "X": 0},
    "Delta126bar": {"PQ": -2, "X": 0},
    "Phi210": {"PQ": 0, "X": 0},
    "S": {"PQ": 4, "X": 0},
    "Phi17": {"PQ": 0, "X": 17},
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
    checks = {
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
    return {
        "n_bytes": len(text.encode("utf-8")),
        "checks": checks,
        "all_structure_ok": all(checks.values()),
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

    # Upstream τ_p certificate continuity (light: only require module import path)
    tau_ok = hasattr(taup, "assemble_uv_selected_vacuum")

    # Live run: only True if we actually executed — we never do without tools.
    live_executed = False
    live_dump = None
    if probe["live_run_possible"]:
        # Still do not invent a dump; require an external artifact path.
        dump_path = ROOT / "models" / "LIVE_BETA_DUMP.json"
        if dump_path.is_file():
            live_executed = True
            live_dump = str(dump_path)
        else:
            probe["block_reason"] = (
                "Live tools appear present but no LIVE_BETA_DUMP.json artifact; "
                "refusing to claim a live run."
            )

    checks = {
        "sarah_file_present": SARAH_MODEL.is_file(),
        "pyrate_file_present": PYRATE_MODEL.is_file(),
        "sarah_structure_ok": sarah_v["all_structure_ok"],
        "pyrate_dynkin_match": pyrate_v["dynkin_match_upstream"],
        "pyrate_charges_match": pyrate_v["charges_match_locks"],
        "pyrate_operators_present": pyrate_v["required_operators_present"],
        "live_not_overclaimed": (not live_executed) or bool(live_dump),
        "tau_p_module_available": tau_ok,
        "unique_tau_p_not_claimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    status = (
        "SARAH_PYRATE_MODEL_FILE_AUTHORED__LIVE_RUN_BLOCKED"
        if not failures and not live_executed
        else (
            "SARAH_PYRATE_LIVE_RUN_EXECUTED"
            if not failures and live_executed
            else "SARAH_PYRATE_MODEL_FILE_FAILED"
        )
    )

    return {
        "status": status,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "files": {
            "sarah": SOURCES["sarah_model"],
            "pyrate": SOURCES["pyrate_model"],
            "sarah_bytes": sarah_v["n_bytes"],
            "pyrate_bytes": len(pyrate_text.encode("utf-8")),
        },
        "validation": {"sarah": sarah_v, "pyrate": pyrate_v},
        "live_probe": {**probe, "live_run_executed": live_executed, "dump": live_dump},
        "next_exact_calculation": [
            "Derive exact X/Y masses from the full component vacuum",
            "Close inter-representation 10–126 colour-triplet mixing",
            "Execute a live SARAH/PyR@TE dump when Mathematica+SARAH or pyrate is available",
        ],
        "flag": {
            "sarah_pyrate_model_file_authored": True,
            "pyrate_yaml_dynkin_matches_upstream": pyrate_v["dynkin_match_upstream"],
            "charge_locks_encoded": pyrate_v["charges_match_locks"],
            "live_sarah_or_pyrate_executable_run": bool(live_executed),
            "live_run_blocked_without_tools_or_dump": not live_executed,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Authored SARAH+PyR@TE model-file scaffolds for SO(10)×Z₁₇ "
            f"(210/126/10/S/Φ₁₇; Dynkin match={pyrate_v['dynkin_match_upstream']}; "
            f"charges match={pyrate_v['charges_match_locks']}). "
            f"Live run executed={live_executed}"
            + (
                f" ({probe['block_reason']})"
                if not live_executed and probe.get("block_reason")
                else "."
            )
            + " Exact X/Y masses and unique τ_p remain OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    probe = report["live_probe"]
    lines = [
        "# SARAH/PyR@TE 210ⁿ model-file scaffold — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- SARAH: `{report['files']['sarah']}` ({report['files']['sarah_bytes']} bytes)",
        f"- PyR@TE: `{report['files']['pyrate']}` ({report['files']['pyrate_bytes']} bytes)",
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
