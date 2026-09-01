#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
CALLER = ROOT / "observed" / "bin" / "caller"
LIBRARY = ROOT / "observed" / "bin" / "lib" / "libanswer.dylib"
MISSING_CALLER = ROOT / "observed" / "bin" / "missing" / "caller"


for path in (CALLER, LIBRARY):
    if not path.is_file():
        raise SystemExit(f"missing generated artifact: {path.relative_to(ROOT)}")

success = subprocess.run([CALLER], capture_output=True, text=True)
if success.returncode != 0 or success.stdout != "answer=42\n":
    raise SystemExit(
        f"unexpected success case: returncode={success.returncode}, stdout={success.stdout!r}"
    )

trace_environment = os.environ.copy()
trace_environment["DYLD_PRINT_LIBRARIES"] = "1"
trace = subprocess.run(
    [CALLER],
    capture_output=True,
    text=True,
    env=trace_environment,
)
if trace.returncode != 0 or str(LIBRARY) not in trace.stderr:
    raise SystemExit("dyld trace did not report the expected shared library path")

MISSING_CALLER.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(CALLER, MISSING_CALLER)
failure = subprocess.run([MISSING_CALLER], capture_output=True, text=True)
expected_missing_path = MISSING_CALLER.parent / "lib" / "libanswer.dylib"
if failure.returncode == 0:
    raise SystemExit("missing-library case unexpectedly succeeded")
for expected in (
    "Library not loaded: @rpath/libanswer.dylib",
    str(expected_missing_path),
    "no such file",
):
    if expected not in failure.stderr:
        raise SystemExit(f"missing-library stderr lacks expected evidence: {expected}")

print("success: exit=0 stdout=answer=42")
print("trace: loaded=<EXPERIMENT>/observed/bin/lib/libanswer.dylib")
print("missing: exit_nonzero=true")
print("missing: library_not_loaded=@rpath/libanswer.dylib")
print("missing: tried=<EXPERIMENT>/observed/bin/missing/lib/libanswer.dylib")
print("shared library loader success and failure verified")
