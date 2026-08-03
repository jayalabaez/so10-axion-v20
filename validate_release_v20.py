#!/usr/bin/env python3
"""Fail-closed release gate for the combined v17/v19/v20 package."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parent
V17_ENGINE = ROOT / "so10_axion_v17_engine.py"
V19_ENGINE = ROOT / "so10_axion_v19_engine.py"
V20_ENGINE = ROOT / "so10_axion_v20_engine.py"
V17_VERDICT = ROOT / "so10_axion_v17_verdict.json"
V19_VERDICT = ROOT / "so10_axion_v19_verdict.json"
V20_VERDICT = ROOT / "so10_axion_v20_verdict.json"
TEX = ROOT / "axion_so10_theory_v20.tex"
PDF = ROOT / "axion_so10_theory_v20.pdf"
LOG = ROOT / "axion_so10_theory_v20.log"


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    environment = os.environ.copy()
    environment["SOURCE_DATE_EPOCH"] = "1785638400"
    subprocess.run(command, cwd=ROOT, check=True, env=environment)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def write_checksums(files: list[Path]) -> None:
    lines = []
    for path in sorted(files, key=lambda item: item.name):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.name}")
    (ROOT / "SHA256SUMS").write_text("\n".join(lines) + "\n")


def main() -> int:
    run([sys.executable, "-m", "compileall", "-q", str(ROOT)])

    run(
        [
            sys.executable,
            str(V17_ENGINE),
            "--trials",
            "100000",
            "--output",
            str(V17_VERDICT),
        ]
    )
    v17 = json.loads(V17_VERDICT.read_text())
    require(v17["n_checks_total"] == 65, "v17 check count changed")
    require(v17["n_checks_failed"] == 0 and v17["failures"] == [], "v17 engine failed")

    run([sys.executable, str(V19_ENGINE), "--output", str(V19_VERDICT)])
    v19 = json.loads(V19_VERDICT.read_text())
    require(v19["n_checks_total"] == 59, "v19 check count changed")
    require(v19["n_checks_failed"] == 0 and v19["failures"] == [], "v19 engine failed")
    require(
        v19["uv_completion"]["quality_overcatalogue"]["minimum"]["P"] == 13,
        "v19 historical P=13 regression changed",
    )

    run([sys.executable, str(V20_ENGINE), "--output", str(V20_VERDICT)])
    v20 = json.loads(V20_VERDICT.read_text())
    require(v20["n_checks_total"] == 42, "v20 check count changed")
    require(v20["n_checks_failed"] == 0 and v20["failures"] == [], "v20 engine failed")
    require(
        v20["completion"]["quality_overcatalogue"]["minimum"]["P"] == 8,
        "v20 P=8 threshold result changed",
    )
    require(
        v20["completion"]["minimality"]["minimum_number_of_pairs"] == 3,
        "v20 three-pair minimum changed",
    )
    require(
        v20["amplitudes"]["dominant_computed_unit_coefficient_term"]
        == "v20_U1X_direct_scalar_dimension21",
        "dominant v20 computed term changed",
    )
    require(
        v20["completion"]["running"]["continuous_from_spectator_corrected_alpha_GUT"][
            "conservative"
        ]["landau_pole_below_MPl"],
        "continuous Spin(10) soft-falsification flag missing",
    )

    suite = unittest.defaultTestLoader.discover(str(ROOT))
    n_tests = suite.countTestCases()
    require(n_tests >= 154, f"expected at least 154 tests, found {n_tests}")
    run([sys.executable, "-m", "unittest", "-v"])

    pdflatex = shutil.which("pdflatex")
    require(pdflatex is not None, "pdflatex is required")
    latex = [pdflatex, "-interaction=nonstopmode", "-halt-on-error", TEX.name]
    run(latex)
    run(latex)
    stable = hashlib.sha256(PDF.read_bytes()).hexdigest()
    run(latex)
    rebuilt = hashlib.sha256(PDF.read_bytes()).hexdigest()
    require(rebuilt == stable, "PDF is not byte-reproducible after stabilization")

    forbidden = (
        "LaTeX Warning",
        "Package hyperref Warning",
        "Overfull \\hbox",
        "Underfull \\hbox",
        "Overfull \\vbox",
        "Underfull \\vbox",
        "undefined references",
        "multiply defined",
    )
    log_text = LOG.read_text(errors="replace")
    hits = [marker for marker in forbidden if marker in log_text]
    require(not hits, f"LaTeX log defects: {hits}")
    require(PDF.read_bytes()[:5] == b"%PDF-", "invalid PDF header")
    require(PDF.stat().st_size > 100_000, "PDF unexpectedly small")

    pdfinfo = shutil.which("pdfinfo")
    require(pdfinfo is not None, "pdfinfo is required")
    metadata = subprocess.run(
        [pdfinfo, str(PDF)], cwd=ROOT, check=True, text=True, capture_output=True
    ).stdout
    require("Pages:           12" in metadata, "expected a twelve-page manuscript")

    core = [
        ROOT / "README.md",
        ROOT / "REFEREE_AUDIT_v20.md",
        ROOT / "V20_ERROR_AUDIT.md",
        TEX,
        PDF,
        ROOT / "decay_safe_completion_v20.py",
        ROOT / "decay_threshold_v20.py",
        ROOT / "audit_v20_errors.py",
        ROOT / "physics_push_v20.py",
        ROOT / "full_fermion_matching_v20.py",
        ROOT / "portal_tensors_abcd_v20.py",
        ROOT / "physical_cf_matching_v20.py",
        ROOT / "global_flavour_fit_v20.py",
        ROOT / "cmb_public_data_pipeline_v20.py",
        ROOT / "empirical_roadmap_lock_v20.py",
        ROOT / "next_phenomenology_lock_v20.py",
        ROOT / "close_open_gaps_v20.py",
        ROOT / "verify_tan_beta_profile_semantics.py",
        ROOT / "tan_beta_profile_v20.py",
        ROOT / "reanalysis_portal_beta_v20.py",
        ROOT / "FERMION_PORTAL_CURRENT_THEOREM.md",
        ROOT / "FULL_FERMION_MATCHING_V20_VERDICT.json",
        ROOT / "PORTAL_TENSORS_ABCD_V20_VERDICT.json",
        ROOT / "PHYSICAL_CF_MATCHING_V20_VERDICT.json",
        ROOT / "GLOBAL_FLAVOUR_FIT_V20_VERDICT.json",
        ROOT / "CMB_PUBLIC_PIPELINE_V20_VERDICT.json",
        ROOT / "EMPIRICAL_ROADMAP_LOCK_V20_VERDICT.json",
        ROOT / "NEXT_PHENOMENOLOGY_LOCK_V20_VERDICT.json",
        ROOT / "OPEN_GAPS_CLOSURE_V20_VERDICT.json",
        ROOT / "TAN_BETA_PROFILE_V20_VERDICT.json",
        ROOT / "V20_PORTAL_BETA_REANALYSIS_VERDICT.json",
        V20_ENGINE,
        V20_VERDICT,
        ROOT / "test_decay_safe_completion_v20.py",
        ROOT / "test_decay_threshold_v20.py",
        ROOT / "test_audit_v20_errors.py",
        ROOT / "test_physics_push_v20.py",
        ROOT / "so10_axion_v17_engine.py",
        V17_VERDICT,
        ROOT / "so10_axion_v19_engine.py",
        V19_VERDICT,
        ROOT / "requirements.txt",
        Path(__file__),
    ]
    require(all(path.exists() for path in core), "release core is incomplete")
    write_checksums(core)
    print(
        f"RELEASE GATE PASS: v17 65/65; v19 59/59; v20 42/42; "
        f"tests {n_tests}/{n_tests}; clean 12-page PDF"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
