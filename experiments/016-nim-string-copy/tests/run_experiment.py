"""Build fresh Nim string evidence; --record saves sanitized observations."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import re
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = (
    "pass len=4 same=true value=ABCD\n"
    "return len=4 same=false value=ABCD\n"
    "assign before_same=false original=ABCD assigned=ABCD\n"
    "assign after_same=false original=ABCD assigned=ZBCD\n"
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

    dump = subprocess.run(["nim", "dump", "--verbosity:0", "src/string_copy.nim"],
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
        "--nimcache:observed/nimcache", "--out:observed/bin/string_copy",
        "src/string_copy.nim")

    generated = (ROOT / "observed/nimcache/@mstring_copy.nim.c").read_text()
    runtime = (ROOT / "observed/nimcache/@psystem.nim.c").read_text()

    string_struct = require(
        r"struct NimStringV2 \{\s*NI len;\s*NimStrPayload\* p;\s*\};", generated)
    pass_decl = require(
        r"N_LIB_PRIVATE N_NOINLINE\(NIM_BOOL, passAliases__[^\n]+\)"
        r"\(NimStringV2 value_p0, void\* expected_p1\);", generated)
    identity_decl = require(
        r"N_LIB_PRIVATE N_NOINLINE\(NimStringV2, identity__[^\n]+\)"
        r"\(NimStringV2 value_p0\);", generated)
    pass_name = re.search(r"(passAliases__[^)]+)", pass_decl).group(1)  # type: ignore[union-attr]
    identity_name = re.search(r"(identity__[^)]+)", identity_decl).group(1)  # type: ignore[union-attr]
    pass_def = function_at(generated, pass_name + ")")
    identity_def = function_at(generated, identity_name + ")")
    mutation_inline = function_at(generated, "nimPrepareStrMutationV2)(")
    module_def = function_at(generated, "NimMainModule)(void)")

    require(r"address__[^\n]+\(value_p0\)", pass_def)
    if "eqcopy" in pass_def or "nimAsgnStrV2" in pass_def:
        raise AssertionError("string parameter unexpectedly copied in passAliases")
    require(r"result\.len = 0; result\.p = NIM_NIL;", identity_def)
    eqcopy_call = require(r"eqcopy___system_[^(]+\(\(&result\), value_p0\);", identity_def)
    eqcopy_name = re.search(r"(eqcopy___system_[^(]+)", eqcopy_call).group(1)  # type: ignore[union-attr]
    require(r"eqcopy___system_[^(]+\(\(&assigned__[^,]+\), original__[^)]+\);", module_def)
    require(r"nimPrepareStrMutationV2\(\(&assigned__[^)]+\)\);", module_def)
    require(r"assigned__[^.]+\.p->data\[\(\(NI\)0\)\] = 90;", module_def)
    for name in ("assigned", "returned", "original"):
        require(name + r"__[^.]+\.p && !\(" + name
                + r"__[^.]+\.p->cap & NIM_STRLIT_FLAG\)[\s\S]{0,100}deallocShared\(", module_def)
    require(r"cap & \(\(NI\)IL64\(4611686018427387904\)\)", mutation_inline)
    require(r"nimPrepareStrMutationImpl__system_[^(]+\(s_p0\);", mutation_inline)

    assign_runtime = function_at(runtime, "nimAsgnStrV2)(")
    eqcopy_runtime = function_at(runtime, eqcopy_name + ")(")
    mutation_impl = function_at(runtime, "nimPrepareStrMutationImpl__system_")
    require(r"nimAsgnStrV2\(\(\(NimStringV2\*\) \(dest_p0\)\), src_p1\);", eqcopy_runtime)
    require(r"\(\*a_p0\)\.p = b_p1\.p;", assign_runtime)
    require(r"allocSharedImpl\(", assign_runtime)
    require(r"copyMem__system_[^(]+\([\s\S]+b_p1\.len \+ \(\(NI\)1\)", assign_runtime)
    require(r"oldP_1 = \(\*s_p0\)\.p;", mutation_impl)
    require(r"copyMem__system_[^(]+\([\s\S]+\(\*s_p0\)\.len \+ \(\(NI\)1\)", mutation_impl)

    normal = run("observed/bin/string_copy")
    if normal != EXPECTED:
        raise AssertionError(f"unexpected output: {normal}")
    binary_info = run("file", "observed/bin/string_copy")
    require(r"string_copy: Mach-O 64-bit executable " + arch, binary_info)

    strs_source = (nim_lib / "system/strs_v2.nim").read_text()
    system_source = (nim_lib / "system.nim").read_text()
    representation = require(
        r"type\s+NimStrPayloadBase = object[\s\S]*?NimStringV2 \{\.core\.\} = object\s*"
        r"len: int\s*p: ptr NimStrPayload ## can be nil if len == 0\.", strs_source)
    frees_definition = require(
        r"template frees\(s\) =[\s\S]*?\n\s*else:\s*\n\s*dealloc\(s\.p\)", strs_source)
    assignment_definition = require(
        r"proc nimAsgnStrV2\(a: var NimStringV2, b: NimStringV2\) \{\.compilerRtl\.\} ="
        r"[\s\S]*?copyMem\(unsafeAddr a\.p\.data\[0\], unsafeAddr b\.p\.data\[0\], b\.len\+1\)",
        strs_source)
    mutation_definition = require(
        r"proc nimPrepareStrMutationImpl\(s: var NimStringV2\) =[\s\S]*?"
        r"proc nimPrepareStrMutationV2\(s: var NimStringV2\) \{\.compilerRtl, inl\.\} ="
        r"[\s\S]*?nimPrepareStrMutationImpl\(s\)", strs_source)
    magic_definition = require(
        r"proc `=`\*\[T\]\(dest: var T; src: T\) \{\.noSideEffect, magic: \"Asgn\"\.\}\s*"
        r"proc `=copy`\*\[T\]\(dest: var T; src: T\) \{\.noSideEffect, magic: \"Asgn\"\.\}",
        system_source)
    definitions = (
        "# Nim 2.2.10 lib/system/strs_v2.nim and lib/system.nim.\n"
        "# Selected definitions only; source paths are repository-independent.\n\n"
        + representation + "\n\n" + frees_definition + "\n\n"
        + assignment_definition + "\n\n" + mutation_definition + "\n\n"
        + magic_definition + "\n"
    )
    if not args.record:
        saved = (ROOT / "observed/toolchain-definition-excerpt.nim").read_text()
        if definitions != saved:
            raise AssertionError("saved toolchain definitions differ from Nim 2.2.10")

    generated_excerpt = (
        "/* Nim 2.2.10 observed/nimcache/@mstring_copy.nim.c.\n"
        " * Selected string layout, pass/return functions, mutation guard, and caller only.\n"
        " * Local paths normalized to <EXPERIMENT> and <NIM_ROOT>. */\n\n"
        + string_struct + "\n\n" + pass_decl + "\n" + identity_decl + "\n\n"
        + pass_def + "\n\n" + identity_def + "\n\n" + mutation_inline + "\n\n"
        + module_def + "\n"
    )
    runtime_excerpt = (
        "/* Nim 2.2.10 observed/nimcache/@psystem.nim.c.\n"
        " * Selected string assignment and literal-mutation helpers only. */\n\n"
        + assign_runtime + "\n\n" + eqcopy_runtime + "\n\n" + mutation_impl + "\n"
    )
    env = (
        "recorded_utc=" + datetime.now(timezone.utc).isoformat() + "\n"
        + run("sw_vers") + "machine=" + run("uname", "-m") + nim_version
        + run("clang", "--version").splitlines()[0] + "\nselected_target=" + target + "\n"
        + "memory_manager=orc\nbuild_mode=debug\n"
    )
    if args.record:
        artifacts = {
            "generated-c-excerpt.c": generated_excerpt,
            "runtime-c-excerpt.c": runtime_excerpt,
            "toolchain-definition-excerpt.nim": definitions,
            "run-2026-09-08.txt": binary_info + "\n" + normal + "exit=0\n",
            "environment.txt": env,
            "commands-2026-09-08.txt": "\n".join(logs),
        }
        for name, content in artifacts.items():
            (ROOT / "observed" / name).write_text(clean(content))

    print(f"target={target}")
    print(EXPECTED, end="")
    print("Nim string pass, return, assignment, copy, mutation, and cleanup verified")


if __name__ == "__main__":
    main()
