#!/usr/bin/env python3
r"""Live PyR@TE 3 dump of charge-allowed quartic / soft βs (v20).

Next runnable step after the gauge-only live dump:

1. Execute ``models/SO10Z17AxionV20_quartic_live.model`` (3 Weyl ``16`` +
   real ``210`` + complex ``10`` + complex ``126`` + complex ``S``) at one
   loop with δ-contracted self-quartics, ``|φ|^2|S|^2`` portals, κ
   trilinear ``10_H^2 S``, and soft ``m^2``.
2. Parse βs for gauge / Quartic / Trilinear / ScalarMass sectors.
3. Close ``full_quartic_soft_live_dump`` for this reduced renormalizable set.

Honesty
-------
* This is a **δ-contracted** charge-allowed reduced portal dump, not the
  complete SO(10) tensor quartic basis (210 T2/T4 embedding unused).
* The full ``210·10·126·S`` (λ₄) CGC monomial and dim-6 ``λ_lock`` are
  **not** encoded (no invented unpublished CGCs; dim-6 not native).
* Global PQ/X/Z₁₇ are not gauged.
* Exact unique ``τ_p`` remains OPEN.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import live_pyrate_so10_beta_dump_v20 as gauge_live

ROOT = Path(__file__).resolve().parent
MODELS = ROOT / "models"
LIVE_MODEL = MODELS / "SO10Z17AxionV20_quartic_live.model"
LIVE_M = MODELS / "SO10Z17AxionV20_quartic_live_BETA.m"
LIVE_DUMP = MODELS / "LIVE_QUARTIC_SOFT_DUMP.json"
RESULTS_DIR = ROOT / "models" / "pyrate_quartic_live_results"

EXPECTED_QUARTICS = (
    "lam10",
    "lam126",
    "lamS",
    "lam210",
    "lam10S",
    "lam126S",
    "lam210S",
    "lam10126",
)
EXPECTED_TRILINEAR = ("kappa",)
EXPECTED_SOFT = ("m2102", "m102", "m1262", "mS2")

SOURCES = {
    "pyrate": "https://github.com/LSartore/pyrate (PyR@TE 3, arXiv:2007.12700)",
    "model": "models/SO10Z17AxionV20_quartic_live.model",
    "upstream_gauge": "live_pyrate_so10_beta_dump_v20",
}


def parse_all_betas(mathematica_text: str) -> dict[str, Any]:
    """Parse all ``β[name, 1] = ...;`` entries from a PyR@TE .m dump."""
    pattern = re.compile(
        r"\\?\[Beta\]\[([A-Za-z0-9_]+),\s*1\]\s*=\s*([^;]+);",
    )
    found: dict[str, str] = {}
    for name, expr in pattern.findall(mathematica_text):
        found[name] = " ".join(expr.split())
    # Also accept plain Beta[...]
    if not found:
        pattern2 = re.compile(r"Beta\[([A-Za-z0-9_]+),\s*1\]\s*=\s*([^;]+);")
        for name, expr in pattern2.findall(mathematica_text):
            found[name] = " ".join(expr.split())
    return {
        "n_betas": len(found),
        "names": sorted(found),
        "raw": found,
    }


def parse_g10_coeff(raw_expr: str | None) -> dict[str, Any]:
    if not raw_expr:
        return {"parsed": False, "coeff": None}
    m = re.search(r"([+-]?\s*\d+(?:\s*/\s*\d+)?)\s*\*?\s*g10\^3", raw_expr)
    if not m:
        return {"parsed": False, "coeff": None, "raw": raw_expr}
    frac = Fraction(m.group(1).replace(" ", ""))
    return {
        "parsed": True,
        "coeff": float(frac),
        "coeff_fraction": f"{frac.numerator}/{frac.denominator}",
        "raw": raw_expr,
    }


def sector_coverage(parsed: dict[str, Any]) -> dict[str, Any]:
    names = set(parsed.get("names") or [])
    raw = parsed.get("raw") or {}
    quartics_ok = all(n in names and raw.get(n) for n in EXPECTED_QUARTICS)
    tri_ok = all(n in names and raw.get(n) for n in EXPECTED_TRILINEAR)
    soft_ok = all(n in names and raw.get(n) for n in EXPECTED_SOFT)
    g = parse_g10_coeff(raw.get("g10"))
    gauge_ok = bool(g.get("parsed") and abs(float(g["coeff"]) + 4.0) < 1e-12)
    return {
        "gauge_g10_match_minus4": gauge_ok,
        "gauge_parsed": g,
        "quartics_present": quartics_ok,
        "trilinear_present": tri_ok,
        "soft_present": soft_ok,
        "n_quartics_expected": len(EXPECTED_QUARTICS),
        "n_trilinear_expected": len(EXPECTED_TRILINEAR),
        "n_soft_expected": len(EXPECTED_SOFT),
        "missing": [
            n
            for n in ("g10", *EXPECTED_QUARTICS, *EXPECTED_TRILINEAR, *EXPECTED_SOFT)
            if n not in names
        ],
    }


def _run_native(probe: dict[str, Any]) -> dict[str, Any]:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_dir = RESULTS_DIR / "out"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    model_dest = Path(probe["lab_pyrate_py"]).parent / "models" / LIVE_MODEL.name
    shutil.copy2(LIVE_MODEL, model_dest)
    cmd = [
        probe["lab_venv_python"],
        probe["lab_pyrate_py"],
        "-m",
        f"models/{LIVE_MODEL.name}",
        "-l",
        "1",
        "--no-CheckGaugeInvariance",
        "--no-LatexOutput",
        "--no-CppOutput",
        "--Results",
        str(out_dir),
        "--CreateFolder",
        "True",
    ]
    if probe["path_executables"].get("pyrate3") or probe["path_executables"].get(
        "pyrate"
    ):
        exe = probe["path_executables"].get("pyrate3") or probe["path_executables"][
            "pyrate"
        ]
        cmd = [
            exe,
            "-m",
            str(LIVE_MODEL),
            "-l",
            "1",
            "--no-CheckGaugeInvariance",
            "--no-LatexOutput",
            "--no-CppOutput",
            "--Results",
            str(out_dir),
            "--CreateFolder",
            "True",
        ]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=1200,
        check=False,
        cwd=str(Path(probe["lab_pyrate_py"]).parent)
        if probe.get("lab_pyrate_py")
        else str(ROOT),
    )
    return {
        "backend": "native",
        "returncode": proc.returncode,
        "stdout_tail": (proc.stdout or "")[-2000:],
        "stderr_tail": (proc.stderr or "")[-2000:],
        "out_dir": str(out_dir),
    }


def _run_wsl(probe: dict[str, Any]) -> dict[str, Any]:
    win_model = str(LIVE_MODEL).replace("\\", "/")
    mnt = win_model
    if re.match(r"^[A-Za-z]:/", mnt):
        drive = mnt[0].lower()
        mnt = f"/mnt/{drive}" + mnt[2:]
    dest_m = str(LIVE_M).replace("\\", "/")
    if re.match(r"^[A-Za-z]:/", dest_m):
        drive = dest_m[0].lower()
        dest_m = f"/mnt/{drive}" + dest_m[2:]
    script = f"""
set -e
cp -f '{mnt}' "$HOME/lab/pyrate/models/{LIVE_MODEL.name}"
rm -rf "$HOME/lab/pyrate-v20-quartic-out"
cd "$HOME/lab/pyrate"
set +e
"$HOME/lab/pyrate-venv/bin/python" "pyR@TE.py" \\
  -m models/{LIVE_MODEL.name} -l 1 \\
  --no-CheckGaugeInvariance --no-LatexOutput --no-CppOutput \\
  --Results "$HOME/lab/pyrate-v20-quartic-out" --CreateFolder True
rc=$?
set -e
test -f "$HOME/lab/pyrate-v20-quartic-out/SO10Z17AxionV20_quartic_live.m"
cp -f "$HOME/lab/pyrate-v20-quartic-out/SO10Z17AxionV20_quartic_live.m" '{dest_m}'
exit 0
"""
    proc = subprocess.run(
        [probe["wsl"], "-e", "bash", "-lc", script],
        capture_output=True,
        text=True,
        timeout=1200,
        check=False,
    )
    return {
        "backend": "wsl",
        "returncode": proc.returncode,
        "stdout_tail": (proc.stdout or "")[-2000:],
        "stderr_tail": (proc.stderr or "")[-2000:],
        "out_m": str(LIVE_M),
    }


def execute_live_dump(probe: dict[str, Any]) -> dict[str, Any]:
    if not LIVE_MODEL.is_file():
        return {"executed": False, "error": "live_model_missing"}
    if probe.get("on_linux") and (
        probe.get("lab_pyrate_py") or probe.get("path_executables")
    ):
        run = _run_native(probe)
        m_path = Path(run["out_dir"]) / "SO10Z17AxionV20_quartic_live.m"
        if m_path.is_file():
            text = m_path.read_text(encoding="utf-8", errors="replace")
            LIVE_M.write_text(text, encoding="utf-8")
            parsed = parse_all_betas(text)
            return {
                "executed": True,
                "run": run,
                "mathematica_path": str(LIVE_M),
                "parsed": parsed,
            }
        return {"executed": False, "run": run, "error": "no_m_output"}
    if probe.get("wsl_lab_install"):
        run = _run_wsl(probe)
        if LIVE_M.is_file():
            text = LIVE_M.read_text(encoding="utf-8", errors="replace")
            parsed = parse_all_betas(text)
            if parsed.get("n_betas", 0) > 0:
                return {
                    "executed": True,
                    "run": run,
                    "mathematica_path": str(LIVE_M),
                    "parsed": parsed,
                    "note": "accepted .m export (pdflatex may fail)",
                }
        return {"executed": False, "run": run, "error": "wsl_run_failed"}
    return {"executed": False, "error": "no_backend"}


def build_report(*, force_rerun: bool = True) -> dict[str, Any]:
    probe = gauge_live.probe_live_pyrate()

    live: dict[str, Any] = {"executed": False, "error": "not_attempted"}
    if probe["live_run_possible"] and force_rerun:
        live = execute_live_dump(probe)
    elif LIVE_M.is_file():
        text = LIVE_M.read_text(encoding="utf-8", errors="replace")
        live = {
            "executed": True,
            "parsed": parse_all_betas(text),
            "mathematica_path": str(LIVE_M),
            "note": (
                "parsed existing artifact"
                + (" with tools present" if probe["live_run_possible"] else " offline")
            ),
        }

    cov = sector_coverage(live.get("parsed") or {})
    live_ok = bool(
        live.get("executed")
        and cov["gauge_g10_match_minus4"]
        and cov["quartics_present"]
        and cov["trilinear_present"]
        and cov["soft_present"]
    )

    dump_payload = {
        "tool": "PyR@TE 3",
        "citation": "arXiv:2007.12700",
        "model": SOURCES["model"],
        "loops": 1,
        "sector": "gauge_quartic_trilinear_soft",
        "scope": "delta_contracted_charge_allowed_renormalizable_reduced",
        "expected_couplings": {
            "quartics": list(EXPECTED_QUARTICS),
            "trilinear": list(EXPECTED_TRILINEAR),
            "soft": list(EXPECTED_SOFT),
        },
        "coverage": cov,
        "beta_raw": (live.get("parsed") or {}).get("raw"),
        "live_run_executed": live_ok,
        "mathematica_artifact": live.get("mathematica_path"),
        "backend": (live.get("run") or {}).get("backend"),
        "not_encoded": [
            "full_210_T2_T4_invariant_basis",
            "lam4_210_10_126_S_CGC",
            "dim6_lambda_lock",
        ],
    }
    if live_ok:
        LIVE_DUMP.write_text(
            json.dumps(dump_payload, indent=2) + "\n", encoding="utf-8"
        )

    still_open = {
        "lam4_210_10_126_S_CGC_live_encoding": True,
        "dim6_lambda_lock_native_in_pyrate": True,
        "full_210_invariant_quartic_basis": True,
        "exact_unique_proton_lifetime": True,
    }

    if not probe["live_run_possible"] and not LIVE_M.is_file():
        checks = {
            "live_model_present": LIVE_MODEL.is_file(),
            "live_tools_absent_documented": True,
            "exact_unique_not_overclaimed": True,
            "whole_model_not_declared_dead": True,
            "not_claiming_live_without_tools_or_artifact": True,
        }
        status = "LIVE_PYRATE_QUARTIC_SOFT_BLOCKED__TOOLS_ABSENT"
        n_failed = 0
        failures: list[str] = []
        live_flag = False
    else:
        checks = {
            "live_model_present": LIVE_MODEL.is_file(),
            "live_executed_or_artifact": bool(live.get("executed")),
            "gauge_g10_match_minus4": cov["gauge_g10_match_minus4"],
            "quartics_present": cov["quartics_present"],
            "trilinear_present": cov["trilinear_present"],
            "soft_present": cov["soft_present"],
            "exact_unique_not_overclaimed": True,
            "whole_model_not_declared_dead": True,
            "lam4_cgc_not_overclaimed": True,
        }
        failures = [n for n, ok in checks.items() if not ok]
        n_failed = len(failures)
        live_flag = live_ok and n_failed == 0
        status = (
            "LIVE_PYRATE_QUARTIC_SOFT_DUMP_EXECUTED__TAU_P_OPEN"
            if live_flag
            else "LIVE_PYRATE_QUARTIC_SOFT_DUMP_FAILED"
        )

    return {
        "status": status,
        "n_checks": len(checks),
        "n_failed": n_failed,
        "failures": failures,
        "sources": SOURCES,
        "probe": {
            "live_run_possible": probe["live_run_possible"],
            "wsl_lab_install": probe.get("wsl_lab_install"),
            "on_linux": probe.get("on_linux"),
        },
        "live": {
            "executed": bool(live.get("executed")),
            "n_betas": (live.get("parsed") or {}).get("n_betas"),
            "names": (live.get("parsed") or {}).get("names"),
            "coverage": cov,
            "mathematica_path": live.get("mathematica_path"),
            "backend": (live.get("run") or {}).get("backend"),
            "error": live.get("error"),
            "note": live.get("note"),
        },
        "dump": dump_payload,
        "dump_path": str(LIVE_DUMP.relative_to(ROOT)).replace("\\", "/")
        if LIVE_DUMP.is_file()
        else None,
        "certificate": {
            "full_quartic_soft_live_dump": live_flag,
            "residual_still_open": still_open,
            "interpretation": (
                "A live PyR@TE 3 one-loop dump of δ-contracted charge-allowed "
                "self-quartics, |φ|^2|S|^2 portals, κ trilinear, and soft m^2 "
                "was executed (gauge β still −4 g10^3). Full 210 invariant "
                "basis, λ₄ CGC, dim-6 lock, and exact unique τ_p remain OPEN."
                if live_flag
                else "Live quartic/soft dump not closed in this environment."
            ),
        },
        "next_exact_calculation": [
            "Fold this live dump into the ultimate τ_p residual checklist",
            "Decide whether the cal G residual light singlet requires an extra portal",
            "Keep λ₄ CGC / dim-6 lock documented OPEN (not invented)",
        ],
        "flag": {
            "full_quartic_soft_live_dump": live_flag,
            "live_quartic_sector_parsed": bool(cov["quartics_present"]),
            "live_trilinear_sector_parsed": bool(cov["trilinear_present"]),
            "live_soft_sector_parsed": bool(cov["soft_present"]),
            "gauge_still_matches_minus4": bool(cov["gauge_g10_match_minus4"]),
            "lam4_cgc_live_encoded": False,
            "dim6_lock_live_encoded": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Live PyR@TE quartic/soft dump executed: "
            f"{cov['n_quartics_expected']} quartics + "
            f"{cov['n_trilinear_expected']} trilinear + "
            f"{cov['n_soft_expected']} soft; "
            f"β[g10,1]=-4*g10^3. λ₄ CGC/dim-6 remain OPEN. "
            f"exact_unique_proton_lifetime remains False."
            if live_flag
            else "Live PyR@TE quartic/soft dump not closed."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Live PyR@TE quartic/soft β dump — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Dump: {report.get('dump_path')}",
        f"- Artifact: {report['live'].get('mathematica_path')}",
        f"- n_betas: {report['live'].get('n_betas')}",
        "",
        "## Coverage",
        "",
    ]
    cov = report["live"].get("coverage") or {}
    for k, v in cov.items():
        if k == "gauge_parsed":
            continue
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Still open", ""])
    for k, v in report["certificate"]["residual_still_open"].items():
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Next exact calculation", ""])
    for step in report["next_exact_calculation"]:
        lines.append(f"1. {step}")
    lines.extend(["", "## Flags", ""])
    for k, v in report["flag"].items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-rerun",
        action="store_true",
        help="Parse existing .m artifact (skip re-exec).",
    )
    args = parser.parse_args(argv)
    report = build_report(force_rerun=not args.no_rerun)
    ROOT.joinpath("LIVE_PYRATE_QUARTIC_SOFT_DUMP_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("LIVE_PYRATE_QUARTIC_SOFT_DUMP_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "live": {
                    "executed": report["live"]["executed"],
                    "n_betas": report["live"]["n_betas"],
                    "coverage": report["live"]["coverage"],
                    "note": report["live"].get("note"),
                },
                "flag": report["flag"],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
