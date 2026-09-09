"""Build fresh seq capacity evidence; --record saves sanitized observations."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import re
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = (
    "step=0 len=0 cap=0 total=0\n"
    "step=1 len=1 cap=1 total=1\n"
    "step=2 len=2 cap=2 total=3\n"
    "step=3 len=3 cap=4 total=6\n"
    "step=4 len=4 cap=4 total=10\n"
    "step=5 len=5 cap=8 total=15\n"
    "step=6 len=6 cap=8 total=21\n"
    "step=7 len=7 cap=8 total=28\n"
    "step=8 len=8 cap=8 total=36\n"
    "step=9 len=9 cap=16 total=45\n"
    "step=10 len=10 cap=16 total=55\n"
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

    dump = subprocess.run(["nim", "dump", "--verbosity:0", "src/seq_capacity.nim"],
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
        "--nimcache:observed/nimcache", "--out:observed/bin/seq_capacity",
        "src/seq_capacity.nim")

    generated = (ROOT / "observed/nimcache/@mseq_capacity.nim.c").read_text()
    runtime = (ROOT / "observed/nimcache/@psystem.nim.c").read_text()

    sequence_struct = require(
        r"struct tySequence__[^\s]+ \{\s*NI len; tySequence__[^\s]+_Content\* p;\s*\};",
        generated)
    payload_struct = require(
        r"struct tySequence__[^\s]+_Content \{ NI cap; NI data\[SEQ_DECL_SIZE\]; \};",
        generated)
    capacity_decl = require(
        r"static N_INLINE\(NI, capacity__[^\n]+\)\(tySequence__[^\s]+ self_p0\);",
        generated)
    capacity_name = re.search(r"(capacity__[^)]+)", capacity_decl).group(1)  # type: ignore[union-attr]
    capacity_def = function_at(generated, capacity_name + ")(")
    add_decl = require(
        r"N_LIB_PRIVATE N_NIMCALL\(void, add__[^\n]+\)"
        r"\(tySequence__[^\s]+\* x_p0, NI y_p1\);", generated)
    add_name = re.search(r"(add__[^)]+)", add_decl).group(1)  # type: ignore[union-attr]
    cleanup_decl = require(
        r"N_LIB_PRIVATE N_NIMCALL\(void, eqdestroy__[^\n]+\)"
        r"\(tySequence__[^\s]+ dest_p0\);", generated)
    cleanup_name = re.search(r"(eqdestroy__[^)]+)", cleanup_decl).group(1)  # type: ignore[union-attr]
    cleanup_def = function_at(generated, cleanup_name + ")(")
    module_def = function_at(generated, "NimMainModule)(void)")

    require(r"\.p == [^\n]+NIM_NIL", capacity_def)
    require(r"\.cap & \(\(NI\)IL64\(-4611686018427387905\)\)", capacity_def)
    require(r"result = \(\(NI\)0\);", capacity_def)
    require(re.escape(add_name) + r"\(\(&values__", module_def)
    require(re.escape(cleanup_name) + r"\(values__", module_def)
    require(r"alignedDealloc\(dest_p0\.p, NIM_ALIGNOF\(NI\)\);", cleanup_def)

    add_runtime = function_at(runtime, add_name + ")(")
    prepare_runtime = function_at(runtime, "prepareSeqAddUninit)(")
    new_payload_runtime = function_at(runtime, "newSeqPayloadUninit)(")
    realloc_name = re.search(r"(alignedRealloc__system_[^(]+)\(", prepare_runtime).group(1)  # type: ignore[union-attr]
    realloc_runtime = function_at(runtime, realloc_name + ")(")
    resize_name = re.search(r"(resize__system_[^(]+)\(oldCap_1\)", prepare_runtime).group(1)  # type: ignore[union-attr]
    resize_runtime = function_at(runtime, resize_name + ")(")

    require(r"\.p == [^\n]+NIM_NIL", add_runtime)
    require(r"\.cap & \(\(NI\)IL64\(-4611686018427387905\)\)\) <", add_runtime)
    require(r"prepareSeqAddUninit\(oldLen_1, [\s\S]{0,120}\(\(NI\)1\), \(\(NI\)8\), \(\(NI\)8\)\)", add_runtime)
    require(r"nimAddInt\(oldLen_1, \(\(NI\)1\),", add_runtime)
    require(r"\.len = \(NI\)\(TM__[^;]+\);", add_runtime)
    require(r"\.data\[oldLen_1\] = y_p1;", add_runtime)
    require(r"p_p1 == NIM_NIL", prepare_runtime)
    require(r"newSeqPayloadUninit\(", prepare_runtime)
    require(re.escape(resize_name) + r"\(oldCap_1\)", prepare_runtime)
    require(r"newCap_1 = \(\(T[0-9]+_ >= [^?]+\? T[0-9]+_ :", prepare_runtime)
    require(re.escape(realloc_name) + r"\(", prepare_runtime)
    require(r"\.cap = newCap_1;", prepare_runtime)
    require(r"\(\(NI\)0\) < cap_p0", new_payload_runtime)
    require(r"\.cap = cap_p0;", new_payload_runtime)
    require(r"old_p0 <= \(\(NI\)0\)", resize_runtime)
    require(r"old_p0 \* \(\(NI\)2\)", resize_runtime)
    require(r"reallocSharedImpl__system_[^(]+\(p_p0, newSize_p2\)", realloc_runtime)

    normal = run("observed/bin/seq_capacity")
    if normal != EXPECTED:
        raise AssertionError(f"unexpected output: {normal}")
    binary_info = run("file", "observed/bin/seq_capacity")
    require(r"seq_capacity: Mach-O 64-bit executable " + arch, binary_info)

    seq_source = (nim_lib / "system/seqs_v2.nim").read_text()
    strs_source = (nim_lib / "system/strs_v2.nim").read_text()
    mem_source = (nim_lib / "system/memalloc.nim").read_text()
    representation = require(
        r"type\s+NimSeqPayloadBase = object[\s\S]*?NimRawSeq = object\s*"
        r"len: int\s*p: pointer", seq_source)
    new_payload_definition = require(
        r"proc newSeqPayloadUninit\(cap, elemSize, elemAlign: int\): pointer"
        r"[\s\S]*?else:\s*\n\s*result = nil", seq_source)
    prepare_definition = require(
        r"proc prepareSeqAddUninit\(len: int; p: pointer; addlen, elemSize, elemAlign: int\): pointer"
        r"[\s\S]*?result = q\n", seq_source)
    add_definition = require(
        r"proc add\*\[T\]\(x: var seq\[T\]; y: sink T\) \{\.magic: \"AppendSeqElem\", noSideEffect, nodestroy\.\} ="
        r"[\s\S]*?xu\.p\.data\[oldLen\] = y", seq_source)
    capacity_definition = require(
        r"func capacity\*\[T\]\(self: seq\[T\]\): int \{\.inline\.\} ="
        r"[\s\S]*?result = if sek\.p != nil: sek\.p\.cap and not strlitFlag else: 0",
        seq_source)
    resize_definition = require(
        r"proc resize\(old: int\): int \{\.inline\.\} =[\s\S]*?"
        r"else: result = old div 2 \+ old # for large arrays \* 3/2 is better", strs_source)
    realloc_definition = require(
        r"proc alignedRealloc\(p: pointer, oldSize, newSize, align: Natural\): pointer ="
        r"[\s\S]*?alignedDealloc\(p, align\)", mem_source)
    definitions = (
        "# Nim 2.2.10 lib/system/seqs_v2.nim, strs_v2.nim, and memalloc.nim.\n"
        "# Selected definitions only; source paths are repository-independent.\n\n"
        + representation + "\n\n" + new_payload_definition + "\n\n"
        + prepare_definition + "\n" + add_definition + "\n\n"
        + capacity_definition + "\n\n" + resize_definition + "\n\n"
        + realloc_definition + "\n"
    )
    if not args.record:
        saved = (ROOT / "observed/toolchain-definition-excerpt.nim").read_text()
        if definitions != saved:
            raise AssertionError("saved toolchain definitions differ from Nim 2.2.10")

    generated_excerpt = (
        "/* Nim 2.2.10 observed/nimcache/@mseq_capacity.nim.c.\n"
        " * Selected seq layout, capacity, caller, and cleanup only.\n"
        " * Local paths normalized to <EXPERIMENT> and <NIM_ROOT>. */\n\n"
        + sequence_struct + "\n" + payload_struct + "\n\n" + capacity_decl + "\n"
        + add_decl + "\n" + cleanup_decl + "\n\n" + capacity_def + "\n\n"
        + cleanup_def + "\n\n" + module_def + "\n"
    )
    runtime_excerpt = (
        "/* Nim 2.2.10 observed/nimcache/@psystem.nim.c.\n"
        " * Selected seq append, allocation, growth, and reallocation helpers only. */\n\n"
        + add_runtime + "\n\n" + new_payload_runtime + "\n\n" + resize_runtime + "\n\n"
        + prepare_runtime + "\n\n" + realloc_runtime + "\n"
    )
    env = (
        "recorded_utc=" + datetime.now(timezone.utc).isoformat() + "\n"
        + run("sw_vers") + "machine=" + run("uname", "-m") + nim_version
        + run("clang", "--version").splitlines()[0] + "\nselected_target=" + target + "\n"
        + "memory_manager=orc\nbuild_mode=debug\nthreads=on\nelement_type=int\n"
    )
    if args.record:
        artifacts = {
            "generated-c-excerpt.c": generated_excerpt,
            "runtime-c-excerpt.c": runtime_excerpt,
            "toolchain-definition-excerpt.nim": definitions,
            "run-2026-09-09.txt": binary_info + "\n" + normal + "exit=0\n",
            "environment.txt": env,
            "commands-2026-09-09.txt": "\n".join(logs),
        }
        for name, content in artifacts.items():
            (ROOT / "observed" / name).write_text(clean(content))

    print(f"target={target}")
    print(EXPECTED, end="")
    print("Nim seq capacity growth, append lowering, reallocation path, and cleanup verified")


if __name__ == "__main__":
    main()
