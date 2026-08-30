#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
OBJECT = ROOT / "observed" / "obj" / "symbol_relocation.o"


def run(*argv: str) -> str:
    return subprocess.run(
        argv,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


if not OBJECT.is_file():
    raise SystemExit(f"missing object file: {OBJECT.relative_to(ROOT)}")

file_output = run("file", str(OBJECT))
if "Mach-O 64-bit object arm64" not in file_output:
    raise SystemExit(f"unexpected object format: {file_output.strip()}")

symbols = run("nm", "-m", str(OBJECT))
required_symbol_patterns = {
    "defined external call_internal": r"\(__TEXT,__text\) external _call_internal$",
    "defined external call_external": r"\(__TEXT,__text\) external _call_external$",
    "defined non-external internal_double": r"\(__TEXT,__text\) non-external _internal_double$",
    "undefined external puts": r"\(undefined\) external _puts$",
}
for description, pattern in required_symbol_patterns.items():
    if not re.search(pattern, symbols, re.MULTILINE):
        raise SystemExit(f"missing symbol state: {description}")

undefined = [line.strip() for line in run("nm", "-u", str(OBJECT)).splitlines() if line.strip()]
if undefined != ["_puts"]:
    raise SystemExit(f"unexpected undefined symbols: {undefined}")

relocations = run("otool", "-rv", str(OBJECT))
text_match = re.search(
    r"Relocation information \(__TEXT,__text\) 2 entries\n(?P<table>.*?)(?=Relocation information|$)",
    relocations,
    re.DOTALL,
)
if text_match is None:
    raise SystemExit("missing two-entry __TEXT,__text relocation table")
text_relocations = text_match.group("table")
for symbol in ("_puts", "_internal_double"):
    if not re.search(rf"\bBR26\b.* {re.escape(symbol)}$", text_relocations, re.MULTILINE):
        raise SystemExit(f"missing BR26 relocation for {symbol}")

disassembly = run("otool", "-tvV", str(OBJECT))
for label in ("_call_internal:", "_internal_double:", "_call_external:"):
    if label not in disassembly:
        raise SystemExit(f"missing disassembly label: {label}")
if len(re.findall(r"\bbl\b", disassembly)) != 2:
    raise SystemExit("expected exactly two branch-with-link instructions")

print("Mach-O symbols and ARM64 branch relocations verified")
