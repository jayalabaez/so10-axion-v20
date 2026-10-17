"""Verify SHA256SUMS with validate_release_v20's own payload normalisation, and
check that the core list the release gate would write is exactly the set of
paths in the file (fixed point of the refresh, without writing anything)."""
import hashlib
import os
import sys
import textwrap
from pathlib import Path

ROOT = Path(sys.argv[1])
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
import validate_release_v20 as release  # noqa: E402

lines = (ROOT / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
bad = []
seen = []
for line in lines:
    digest, rel = line.split("  ", 1)
    p = ROOT / rel
    seen.append(rel)
    if not p.exists():
        bad.append((rel, "missing"))
        continue
    actual = hashlib.sha256(release.portable_checksum_payload(p)).hexdigest()
    if actual != digest:
        bad.append((rel, "mismatch"))
print("entries:", len(lines), "bad:", len(bad))
for b in bad:
    print("  BAD", b)

source = Path(release.__file__).read_text(encoding="utf-8").splitlines()
start = next(i for i, line in enumerate(source) if line == "    core = [")
stop = next(i for i, line in enumerate(source) if line == "    write_checksums(core)")
snippet = textwrap.dedent("\n".join(source[start:stop]))
namespace = dict(vars(release))
exec(compile(snippet, "validate_release_v20.core", "exec"), namespace)
core = namespace["core"]
core_rel = sorted(Path(p).resolve().relative_to(ROOT.resolve()).as_posix() for p in core)
print("core list size:", len(core_rel), "unique:", len(set(core_rel)))
print("core == SHA256SUMS paths:", core_rel == sorted(seen))
print("in core not in file:", sorted(set(core_rel) - set(seen)))
print("in file not in core:", sorted(set(seen) - set(core_rel)))
new = [r for r in core_rel if any(k in r for k in (
    "structural_obstruction", "decoupled_singlet_benchmark_evidence",
    "higgs_quartic_member", "witness_unitarity",
    "STRUCTURAL_OBSTRUCTION", "BENCHMARK_EVIDENCE", "HIGGS_QUARTIC_MEMBER", "WITNESS_UNITARITY"))]
print("new-module entries in core:", len(new))
for r in new:
    print("  ", r)
