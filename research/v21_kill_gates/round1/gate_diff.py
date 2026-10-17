"""Independent gate-status diff: worktree vs base commit, leaf-level JSON diff.

usage: python gate_diff.py <worktree> <base_commit>
"""
import json
import subprocess
import sys
from pathlib import Path

WT = Path(sys.argv[1])
BASE = sys.argv[2]
FILES = [
    "G1_G8_GATE_LEDGER_V20.json",
    "LIVE_G1_G8_GATE_LEDGER_V20.json",
    "G1_G8_EXECUTION_ROADMAP_V20.json",
    "THEORY_CONFIRMATION_VERDICT.json",
    "ULTIMATE_THEORY_GATE_V20_VERDICT.json",
    "THEORY_VALIDATION_MATRIX_V20_VERDICT.json",
    "FINAL_G3_ACCEPTANCE_GATE_V20.json",
    "AUTHORITATIVE_FULL_MODEL_GATE_V20.json",
    "G3_SM_PATI_SALAM_GATE_READINESS_V20.json",
    "G8_SM_PATI_SALAM_FLAVOUR_NOGO_V20.json",
]


def leaves(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from leaves(v, f"{prefix}.{k}" if prefix else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from leaves(v, f"{prefix}[{i}]")
    else:
        yield prefix, obj


def base_json(name):
    out = subprocess.run(["git", "show", f"{BASE}:{name}"], cwd=WT, capture_output=True)
    if out.returncode != 0:
        return None
    return json.loads(out.stdout.decode("utf-8"))


STATUS_KEYS = ("status", "verdict", "gate", "decision", "approval", "closed", "open", "blocked")

for name in FILES:
    b = base_json(name)
    w = json.loads((WT / name).read_text(encoding="utf-8"))
    if b is None:
        print(f"## {name}: not in base")
        continue
    lb = dict(leaves(b))
    lw = dict(leaves(w))
    keys = sorted(set(lb) | set(lw))
    diffs = [k for k in keys if lb.get(k, "<absent>") != lw.get(k, "<absent>")]
    print(f"## {name}: {len(diffs)} leaf diffs")
    for k in diffs:
        bv = lb.get(k, "<absent>")
        wv = lw.get(k, "<absent>")
        sb = str(bv)
        sw = str(wv)
        if len(sb) > 160:
            sb = sb[:160] + "..."
        if len(sw) > 160:
            sw = sw[:160] + "..."
        flag = " <-- STATUS-LIKE" if any(s in k.lower() for s in STATUS_KEYS) else ""
        print(f"   {k}{flag}\n      base: {sb}\n      work: {sw}")
    # explicit status-like fields unchanged?
    stat_keys = [k for k in keys if any(s in k.lower() for s in STATUS_KEYS)]
    changed_stat = [k for k in stat_keys if lb.get(k) != lw.get(k)]
    print(f"   status-like leaves: {len(stat_keys)}, changed: {len(changed_stat)}")

# gate summary from the ledger
led = json.loads((WT / "G1_G8_GATE_LEDGER_V20.json").read_text(encoding="utf-8"))
print("\n## ledger top-level keys:", list(led.keys())[:30])
