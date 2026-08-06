#!/usr/bin/env python3
"""NumPy-safe report driver for exact_10h_holomorphic_quartic_triplet_v20."""
from __future__ import annotations

import argparse
import json
from typing import Any

import numpy as np

import exact_10h_holomorphic_quartic_triplet_v20 as core


def _json_default(obj: Any) -> Any:
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, complex):
        return {"re": float(obj.real), "im": float(obj.imag)}
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = core.build_report()
    payload = json.dumps(report, indent=2, default=_json_default) + "\n"
    core.OUT_JSON.write_text(payload, encoding="utf-8")
    core.OUT_MD.write_text(core.write_markdown(report), encoding="utf-8")
    print(payload, end="")
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
