#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "observed" / "bin" / "lib" / "libanswer.dylib"
CALLER = ROOT / "observed" / "bin" / "caller"


def run(*argv: str) -> str:
    return subprocess.run(
        argv,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


for path in (LIBRARY, CALLER):
    if not path.is_file():
        raise SystemExit(f"missing generated artifact: {path.relative_to(ROOT)}")

if "Mach-O 64-bit dynamically linked shared library arm64" not in run("file", str(LIBRARY)):
    raise SystemExit("unexpected shared library format")
if "Mach-O 64-bit executable arm64" not in run("file", str(CALLER)):
    raise SystemExit("unexpected caller format")

install_name = run("otool", "-D", str(LIBRARY))
if "@rpath/libanswer.dylib" not in install_name:
    raise SystemExit("shared library is missing @rpath install name")

dependencies = run("otool", "-L", str(CALLER))
if "@rpath/libanswer.dylib" not in dependencies:
    raise SystemExit("caller is missing @rpath shared library dependency")

load_commands = run("otool", "-l", str(CALLER))
if not re.search(r"cmd LC_RPATH.*?path @loader_path/lib \(offset \d+\)", load_commands, re.DOTALL):
    raise SystemExit("caller is missing @loader_path/lib LC_RPATH")

symbols = run("nm", "-m", str(LIBRARY))
if not re.search(r"\(__TEXT,__text\) external _shared_answer$", symbols, re.MULTILINE):
    raise SystemExit("shared library is missing exported _shared_answer")

print("shared library dependency and loader path verified")
