#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "observed" / "lib" / "libvalues.a"
BINARY = ROOT / "observed" / "bin" / "caller"
LINK_MAP = ROOT / "observed" / "bin" / "link-map.txt"


def run(*argv: str) -> str:
    return subprocess.run(
        argv,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


for path in (ARCHIVE, BINARY, LINK_MAP):
    if not path.is_file():
        raise SystemExit(f"missing generated artifact: {path.relative_to(ROOT)}")

members = [line.strip() for line in run("ar", "-t", str(ARCHIVE)).splitlines()]
object_members = [member for member in members if member.endswith(".o")]
if object_members != ["used.o", "unused.o"]:
    raise SystemExit(f"unexpected archive object members: {object_members}")

archive_symbols = run("nm", "-m", str(ARCHIVE))
if not re.search(r"^used\.o:.*?_used_value$", archive_symbols, re.MULTILINE | re.DOTALL):
    raise SystemExit("archive is missing defined _used_value in used.o")
if not re.search(r"^unused\.o:.*?_unused_value$", archive_symbols, re.MULTILINE | re.DOTALL):
    raise SystemExit("archive is missing defined _unused_value in unused.o")

binary_info = run("file", str(BINARY))
if "Mach-O 64-bit executable arm64" not in binary_info:
    raise SystemExit(f"unexpected binary format: {binary_info.strip()}")

binary_symbols = run("nm", "-m", str(BINARY))
if not re.search(r"\(__TEXT,__text\) external _used_value$", binary_symbols, re.MULTILINE):
    raise SystemExit("linked binary is missing _used_value")
if "_unused_value" in binary_symbols:
    raise SystemExit("linked binary unexpectedly contains _unused_value")

link_map = LINK_MAP.read_text(encoding="utf-8")
if "libvalues.a(used.o)" not in link_map:
    raise SystemExit("link map is missing loaded archive member used.o")
if "libvalues.a(unused.o)" in link_map:
    raise SystemExit("link map unexpectedly contains unused archive member unused.o")

run_output = run(str(BINARY))
if run_output != "used=42\n":
    raise SystemExit(f"unexpected caller output: {run_output!r}")

print("static archive member extraction and linked symbols verified")
