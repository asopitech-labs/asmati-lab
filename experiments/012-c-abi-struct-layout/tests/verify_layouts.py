#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
BINARIES = {
    "c": ROOT / "observed" / "bin" / "c_layout",
    "nim": ROOT / "observed" / "bin" / "nim_layout",
    "rust": ROOT / "observed" / "bin" / "rust_layout",
}
EXPECTED = {"size": 12, "align": 4, "first": 0, "second": 4, "ratio": 8}
OUTPUT = re.compile(
    r"^(?P<language>c|nim|rust) "
    r"size=(?P<size>\d+) align=(?P<align>\d+) "
    r"first=(?P<first>\d+) second=(?P<second>\d+) ratio=(?P<ratio>\d+)\n$"
)

source_patterns = {
    "C header field mapping": (
        ROOT / "src" / "layout.h",
        r"typedef struct AsmatiLayout \{\s*int32_t first;\s*int32_t second;\s*float ratio;\s*\} AsmatiLayout;",
    ),
    "Nim importc field mapping": (
        ROOT / "src" / "nim_layout.nim",
        r"importc: \"AsmatiLayout\".*?bycopy, completeStruct.*?first: int32\s*second: int32\s*ratio: cfloat",
    ),
    "Rust repr(C) field mapping": (
        ROOT / "src" / "rust_layout.rs",
        r"#\[repr\(C\)\]\s*struct AsmatiLayout \{\s*first: i32,\s*second: i32,\s*ratio: f32,\s*\}",
    ),
}
for description, (path, pattern) in source_patterns.items():
    if not re.search(pattern, path.read_text(encoding="utf-8"), re.DOTALL):
        raise SystemExit(f"missing source contract: {description}")


rust_version = subprocess.run(
    ["rustc", "-vV"],
    check=True,
    capture_output=True,
    text=True,
).stdout
if "host: x86_64-apple-darwin" in rust_version:
    expected_format = "Mach-O 64-bit executable x86_64"
elif "host: aarch64-apple-darwin" in rust_version:
    expected_format = "Mach-O 64-bit executable arm64"
else:
    raise SystemExit("unsupported rustc host")

observed: dict[str, dict[str, int]] = {}
for language, binary in BINARIES.items():
    if not binary.is_file():
        raise SystemExit(f"missing binary: {binary.relative_to(ROOT)}")
    file_output = subprocess.run(
        ["file", binary],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if expected_format not in file_output:
        raise SystemExit(f"unexpected {language} binary format: {file_output.strip()}")
    output = subprocess.run(
        [binary],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    match = OUTPUT.fullmatch(output)
    if match is None or match.group("language") != language:
        raise SystemExit(f"unexpected {language} output: {output!r}")
    observed[language] = {
        key: int(match.group(key))
        for key in ("size", "align", "first", "second", "ratio")
    }

for language, layout in observed.items():
    if layout != EXPECTED:
        raise SystemExit(f"unexpected {language} layout: {layout}")
if len({tuple(layout.items()) for layout in observed.values()}) != 1:
    raise SystemExit(f"language layouts differ: {observed}")

print("C, Nim, and Rust C-ABI struct layouts verified")
