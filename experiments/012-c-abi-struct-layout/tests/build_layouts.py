#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def run(*argv: str) -> None:
    subprocess.run(argv, cwd=ROOT, check=True)


rust_version = subprocess.run(
    ["rustc", "-vV"],
    check=True,
    capture_output=True,
    text=True,
).stdout
host_line = next((line for line in rust_version.splitlines() if line.startswith("host: ")), None)
if host_line == "host: x86_64-apple-darwin":
    clang_arch = "x86_64"
    nim_cpu = "amd64"
elif host_line == "host: aarch64-apple-darwin":
    clang_arch = "arm64"
    nim_cpu = "arm64"
else:
    raise SystemExit(f"unsupported rustc host: {host_line}")

run(
    "clang",
    "-arch",
    clang_arch,
    "-std=c11",
    "-Wall",
    "-Wextra",
    "-Werror",
    "-Isrc",
    "src/c_layout.c",
    "-o",
    "observed/bin/c_layout",
)
run(
    "nim",
    "c",
    "--cc:clang",
    f"--cpu:{nim_cpu}",
    f"--passC:-arch {clang_arch}",
    "--passC:-Isrc",
    f"--passL:-arch {clang_arch}",
    "--out:observed/bin/nim_layout",
    "src/nim_layout.nim",
)
run(
    "rustc",
    "--edition=2024",
    "-o",
    "observed/bin/rust_layout",
    "src/rust_layout.rs",
)

print(f"layout target prepared: {host_line.removeprefix('host: ')}")
