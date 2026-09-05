"""Build fresh openArray evidence; --record saves sanitized local observations."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import re
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = (
    "array len=4 first=10 last=40 total=100 aliases=true\n"
    "seq len=4 first=10 last=40 total=100 aliases=true\n"
    "slice len=2 first=20 last=30 total=50 aliases=true\n"
)
OOB_MESSAGE = "index out of bounds: 1..4 notin 0..3 [IndexDefect]"


def require(pattern: str, text: str) -> str:
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        raise AssertionError(f"missing evidence: {pattern}")
    return match.group(0)


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

    dump = subprocess.run(["nim", "dump", "--verbosity:0", "src/openarray_slice.nim"],
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
        "--nimcache:observed/nimcache", "--out:observed/bin/openarray_slice",
        "src/openarray_slice.nim")

    generated = (ROOT / "observed/nimcache/@mopenarray_slice.nim.c").read_text()
    summarize_decl = require(
        r"N_LIB_PRIVATE N_NOINLINE\([^\n]+, summarize__[^\n]+\)"
        r"\(NI\* values_p0, NI values_p0Len_0\);", generated)
    same_decl = require(
        r"N_LIB_PRIVATE N_NOINLINE\(NIM_BOOL, sameAddress__[^\n]+\)"
        r"\(NI\* values_p0, NI values_p0Len_0, NI\* expected_p1\);", generated)
    summarize_name = re.search(r"(summarize__[^)]+)", summarize_decl).group(1)  # type: ignore[union-attr]
    same_name = re.search(r"(sameAddress__[^)]+)", same_decl).group(1)  # type: ignore[union-attr]
    summarize_def = require(
        r"^N_LIB_PRIVATE N_NOINLINE\([^\n]+, " + re.escape(summarize_name)
        + r"\)\(NI\* values_p0, NI values_p0Len_0\) \{[\s\S]*?^\}", generated)
    same_def = require(
        r"^N_LIB_PRIVATE N_NOINLINE\(NIM_BOOL, " + re.escape(same_name)
        + r"\)\(NI\* values_p0, NI values_p0Len_0, NI\* expected_p1\) \{[\s\S]*?^\}", generated)

    module_def = require(
        r"^N_LIB_PRIVATE N_NIMCALL\(void, NimMainModule\)\(void\) \{[\s\S]*?^\}\s*^\}",
        generated,
    )
    require(r"values_p0Len_0", summarize_def)
    require(r"values_p0\[\(\(NI\)0\)\]", summarize_def)
    require(r"&values_p0\[i_1\]", summarize_def)
    require(r"&values_p0\[\(\(NI\)0\)\]", same_def)
    require(r"fixedValues__[^,]+, 4,", module_def)
    require(r"dynamicValues__[^.]+\)\.p\) \? \(dynamicValues__[^.]+\.p->data\) : NIM_NIL, dynamicValues__[^.]+\.len,", module_def)
    require(r"\(\(NI\*\)dynamicValues__[^.]+\.p->data\+\(\(\(NI\)1\)\)\)", module_def)
    require(r"\(\(\(NI\)2\)\)-\(\(\(NI\)1\)\)\+1", module_def)
    require(r"raiseIndexError4\(\(\(NI\)1\), \(\(NI\)4\), dynamicValues__[^.]+\.len\)", module_def)

    normal = run("observed/bin/openarray_slice")
    if normal != EXPECTED:
        raise AssertionError(f"unexpected normal output: {normal}")
    oob = execute("observed/bin/openarray_slice", "oob")
    if oob.returncode == 0:
        raise AssertionError("out-of-bounds slice unexpectedly succeeded")
    if OOB_MESSAGE not in oob.stderr:
        raise AssertionError(f"unexpected out-of-bounds stderr: {oob.stderr}")
    if "oob len=" in oob.stdout:
        raise AssertionError("callee ran after invalid slice construction")

    binary_info = run("file", "observed/bin/openarray_slice")
    require(r"openarray_slice: Mach-O 64-bit executable " + arch, binary_info)

    system_source = (nim_lib / "system.nim").read_text()
    checks_source = (nim_lib / "system/chcks.nim").read_text()
    seq_definition = require(
        r"proc toOpenArray\*\[T\]\(x: seq\[T\]; first, last: int\): openArray\[T\] \{\.\s*"
        r"magic: \"Slice\"\.\}[\s\S]*?Allows passing slices without copying,", system_source)
    array_definition = require(
        r"proc toOpenArray\*\[I, T\]\(x: array\[I, T\]; first, last: I\): openArray\[T\] \{\.\s*"
        r"magic: \"Slice\"\.\}", system_source)
    error_definition = require(
        r"proc raiseIndexError4\(l1, h1, h2: int\) \{\.compilerproc, noinline\.\} =\s*"
        r"sysFatal\(IndexDefect, [^\n]+\)", checks_source)
    definitions = (
        "# Nim 2.2.10 lib/system.nim and lib/system/chcks.nim.\n"
        "# Selected definitions only; source paths are repository-independent.\n\n"
        + seq_definition + "\n\n" + array_definition + "\n\n" + error_definition + "\n"
    )
    if not args.record:
        saved_definitions = (ROOT / "observed/toolchain-definition-excerpt.nim").read_text()
        if definitions != saved_definitions:
            raise AssertionError("saved toolchain definitions differ from Nim 2.2.10")

    excerpts = (
        "/* Nim 2.2.10 observed/nimcache/@mopenarray_slice.nim.c.\n"
        " * Selected openArray functions and caller lowering only.\n"
        " * Local source paths normalized to <EXPERIMENT> and <NIM_ROOT>. */\n\n"
        + summarize_decl + "\n" + same_decl + "\n\n"
        + summarize_def + "\n\n" + same_def + "\n\n" + module_def + "\n"
    )
    env = (
        "recorded_utc=" + datetime.now(timezone.utc).isoformat() + "\n"
        + run("sw_vers") + "machine=" + run("uname", "-m") + nim_version
        + run("clang", "--version").splitlines()[0] + "\nselected_target=" + target + "\n"
    )
    if args.record:
        artifacts = {
            "generated-c-excerpt.c": excerpts,
            "toolchain-definition-excerpt.nim": definitions,
            "run-2026-09-05.txt": (
                binary_info + "\nnormal case:\n" + normal + "exit=0\n\n"
                "out-of-bounds case:\nstdout:\n" + oob.stdout + "stderr:\n"
                + oob.stderr + f"exit={oob.returncode}\n"
            ),
            "environment.txt": env,
            "commands-2026-09-05.txt": "\n".join(logs),
        }
        for name, content in artifacts.items():
            (ROOT / "observed" / name).write_text(clean(content))

    print(f"target={target}")
    print(EXPECTED, end="")
    print(f"oob_exit={oob.returncode} oob_error={OOB_MESSAGE}")
    print("Nim openArray pointer, length, alias, and bounds verified")


if __name__ == "__main__":
    main()
