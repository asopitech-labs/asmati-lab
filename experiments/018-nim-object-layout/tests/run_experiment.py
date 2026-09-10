"""Build fresh Nim object-layout evidence; --record saves sanitized observations."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import re
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = (
    "size=24 align=8\n"
    "fieldSizes int=8 bool=1 float=8\n"
    "count=0 enabled=8 ratio=16\n"
    "score=9.0\n"
)


def require(pattern: str, text: str) -> str:
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        raise AssertionError(f"missing evidence: {pattern}")
    return match.group(0)


def function_at(text: str, marker: str) -> str:
    search_from = 0
    while True:
        found = text.find(marker, search_from)
        if found < 0:
            raise AssertionError(f"missing function body: {marker}")
        start = text.rfind("\n", 0, found) + 1
        brace = text.find("{", found)
        semicolon = text.find(";", found)
        if brace >= 0 and (semicolon < 0 or brace < semicolon):
            break
        search_from = found + len(marker)
    depth = 0
    for index in range(brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    raise AssertionError(f"unterminated function: {marker}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    logs: list[str] = []
    nim_lib: Path | None = None

    def clean(text: str) -> str:
        text = text.replace(str(ROOT), "<EXPERIMENT>")
        if nim_lib:
            text = text.replace(str(nim_lib.parent), "<NIM_ROOT>")
            text = text.replace(str(nim_lib), "<NIM_LIB>")
        text = re.sub(r"InstalledDir: .*", "InstalledDir: <CLANG_TOOLCHAIN>", text)
        return "\n".join(line.rstrip() for line in text.splitlines()) + "\n"

    def execute(*argv: str) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True, timeout=120)
        logs.append(clean("$ " + shlex.join(argv) + "\n" + result.stdout
                          + result.stderr + f"exit={result.returncode}\n"))
        return result

    def run(*argv: str) -> str:
        result = execute(*argv)
        if result.returncode:
            raise RuntimeError(logs[-1])
        return result.stdout

    nim_version = run("nim", "--version")
    require(r"Version 2\.2\.10\b", nim_version)
    nim_cpu = require(r"\[MacOSX: (amd64|arm64)\]", nim_version)
    cpu = re.search(r"(amd64|arm64)", nim_cpu).group(1)  # type: ignore[union-attr]
    arch = {"amd64": "x86_64", "arm64": "arm64"}[cpu]
    target = {"amd64": "x86_64-apple-darwin", "arm64": "aarch64-apple-darwin"}[cpu]

    dump = subprocess.run(["nim", "dump", "--verbosity:0", "src/object_layout.nim"],
                          cwd=ROOT, capture_output=True, text=True, check=True)
    for line in (dump.stdout + "\n" + dump.stderr).splitlines():
        candidate = Path(line.strip())
        if (candidate / "system.nim").is_file():
            nim_lib = candidate.resolve()
            break
    if nim_lib is None:
        raise RuntimeError("Nim library source not found in search paths")

    (ROOT / "observed/bin").mkdir(parents=True, exist_ok=True)
    (ROOT / "observed/nimcache").mkdir(parents=True, exist_ok=True)
    run("nim", "c", "--forceBuild:on", "--cc:clang", f"--cpu:{cpu}",
        f"--passC:-arch {arch}", f"--passL:-arch {arch}", "--mm:orc",
        "--nimcache:observed/nimcache", "--out:observed/bin/object_layout",
        "src/object_layout.nim")

    generated = (ROOT / "observed/nimcache/@mobject_layout.nim.c").read_text()
    intbits = require(r"#define NIM_INTBITS 64", generated)
    object_struct = require(
        r"struct tyObject_Sample__[^\s]+ \{\s*NI count;\s*"
        r"NIM_BOOL enabled;\s*NF ratio;\s*\};", generated)
    score_decl = require(
        r"N_LIB_PRIVATE N_NOINLINE\(NF, score__[^\n]+\)"
        r"\(tyObject_Sample__[^\s]+ sample_p0\);", generated)
    score_name = re.search(r"(score__[^)]+)", score_decl).group(1)  # type: ignore[union-attr]
    score_def = function_at(generated, score_name + ")(")
    require(r"if \(!sample_p0\.enabled\)", score_def)
    require(r"sample_p0\.count", score_def)
    require(r"sample_p0\.ratio", score_def)

    normal = run("observed/bin/object_layout")
    if normal != EXPECTED:
        raise AssertionError(f"unexpected output: {normal}")
    binary_info = run("file", "observed/bin/object_layout")
    require(r"object_layout: Mach-O 64-bit executable " + arch, binary_info)

    nimbase = (nim_lib / "nimbase.h").read_text()
    bool_definition = require(
        r"/\* bool types \(C\+\+ has it\): \*/\n"
        r"#ifdef __cplusplus\n#define NIM_BOOL bool\n"
        r"#elif \(defined\(__STDC_VERSION__\) && __STDC_VERSION__ >= 199901\)\n"
        r"//[^\n]+\n#define NIM_BOOL _Bool\n#else\n"
        r"typedef unsigned char NIM_BOOL;[^\n]*\n#endif", nimbase)
    int64_definition = require(
        r"#ifdef __INT64_TYPE__\ntypedef __INT64_TYPE__ NI64;\n"
        r"#else\ntypedef long long int NI64;\n#endif", nimbase)
    int_definition = require(
        r"#ifdef NIM_INTBITS\n#  if NIM_INTBITS == 64\n"
        r"typedef NI64 NI;\ntypedef NU64 NU;[\s\S]*?#endif", nimbase)
    float_definition = require(
        r"typedef float NF32;\ntypedef double NF64;\ntypedef double NF;", nimbase)
    definitions = (
        "/* Nim 2.2.10 lib/nimbase.h. Selected definitions only. */\n\n"
        + bool_definition + "\n\n" + int64_definition + "\n\n"
        + int_definition + "\n\n" + float_definition + "\n"
    )
    if not args.record:
        saved = (ROOT / "observed/nimbase-definition-excerpt.h").read_text()
        if definitions != saved:
            raise AssertionError("saved nimbase definitions differ from Nim 2.2.10")

    generated_excerpt = (
        "/* Nim 2.2.10 observed/nimcache/@mobject_layout.nim.c.\n"
        " * Selected int width, Sample struct, declaration, and field access only.\n"
        " * Local paths normalized to <EXPERIMENT> and <NIM_ROOT>. */\n\n"
        + intbits + "\n\n" + object_struct + "\n\n" + score_decl + "\n\n"
        + score_def + "\n"
    )
    env = (
        "recorded_utc=" + datetime.now(timezone.utc).isoformat() + "\n"
        + run("sw_vers") + "machine=" + run("uname", "-m") + nim_version
        + run("clang", "--version").splitlines()[0] + "\nselected_target=" + target + "\n"
        + "memory_manager=orc\nbuild_mode=debug\nthreads=on\n"
        + "object_fields=int,bool,float\n"
    )
    if args.record:
        artifacts = {
            "generated-c-excerpt.c": generated_excerpt,
            "nimbase-definition-excerpt.h": definitions,
            "run-2026-09-10.txt": binary_info + "\n" + normal + "exit=0\n",
            "environment.txt": env,
            "commands-2026-09-10.txt": "\n".join(logs),
        }
        for name, content in artifacts.items():
            (ROOT / "observed" / name).write_text(clean(content))

    print(f"target={target}")
    print(EXPECTED, end="")
    print("Nim object field order, padding evidence, sizeof, offsets, and generated C verified")


if __name__ == "__main__":
    main()
