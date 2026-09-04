"""Build fresh buffer evidence; --record saves sanitized local observations."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import re
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = ("input empty=0 padded=2 full=6\n"
            "output query=6 full_required=6 short_required=6\n"
            "output full=ASMATI short=ASM tails=CC,CC\n")


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
        text = re.sub(r"InstalledDir: .*", "InstalledDir: <CLANG_TOOLCHAIN>", text)
        return "\n".join(line.rstrip() for line in text.splitlines()) + "\n"

    def run(*argv: str, input_text: str | None = None) -> str:
        result = subprocess.run(argv, cwd=ROOT, text=True, input=input_text,
                                capture_output=True, timeout=120)
        logs.append(clean("$ " + shlex.join(argv) + "\n" + result.stdout
                          + result.stderr + f"exit={result.returncode}\n"))
        if result.returncode:
            raise RuntimeError(logs[-1])
        return result.stdout

    nim_version = run("nim", "--version")
    require(r"Version 2\.2\.10\b", nim_version)
    nim_cpu = require(r"\[MacOSX: (amd64|arm64)\]", nim_version)
    cpu = re.search(r"(amd64|arm64)", nim_cpu).group(1)  # type: ignore[union-attr]
    arch = {"amd64": "x86_64", "arm64": "arm64"}[cpu]
    target = {"amd64": "x86_64-apple-darwin", "arm64": "aarch64-apple-darwin"}[cpu]
    dump = subprocess.run(["nim", "dump", "--verbosity:0", "src/buffer_api.nim"],
                          cwd=ROOT, capture_output=True, text=True, check=True)
    for line in (dump.stdout + "\n" + dump.stderr).splitlines():
        candidate = Path(line.strip())
        if (candidate / "nimbase.h").is_file():
            nim_lib = candidate.resolve()
            break
    if nim_lib is None:
        raise RuntimeError("nimbase.h not found in Nim search paths")
    (ROOT / "observed/bin").mkdir(parents=True, exist_ok=True)
    (ROOT / "observed/nimcache").mkdir(parents=True, exist_ok=True)
    run("nim", "c", "--forceBuild:on", "--cc:clang", f"--cpu:{cpu}",
        f"--passC:-arch {arch}", f"--passL:-arch {arch}", "--mm:orc",
        "--app:lib", "--header:buffer_api.h", "--nimcache:observed/nimcache",
        "--out:observed/bin/libbuffer_api.dylib",
        "--passL:-Wl,-install_name,@rpath/libbuffer_api.dylib", "src/buffer_api.nim")
    header = (ROOT / "observed/nimcache/buffer_api.h").read_text()
    generated = (ROOT / "observed/nimcache/@mbuffer_api.nim.c").read_text()
    target_define = "#define NIM_EmulateOverflowChecks\n"
    if (target_define in header) != (arch == "arm64"):
        raise AssertionError("unexpected target-specific overflow macro")
    if not args.record:
        saved = (ROOT / "observed/buffer_api.h").read_text()
        if clean(header).replace(target_define, "") != saved.replace(target_define, ""):
            raise AssertionError("generated header differs beyond known target macro")
    for name in ("asmati_trimmed_length", "asmati_write_label"):
        require(r"N_LIB_IMPORT N_CDECL\(size_t, " + name
                + r"\)\(NU8\* [a-z]+_p0, size_t [a-z]+_p1\);", header)
        require(r"N_LIB_EXPORT N_CDECL\(size_t, " + name
                + r"\)\(NU8\* [a-z]+_p0, size_t [a-z]+_p1\) \{", generated)
    require(r"NIM_POSIX_INIT NimMainInit\(void\) \{\s+NimMain\(\);\s+\}", generated)
    cflags = ["clang", "-arch", arch, "-std=c11", "-Iobserved/nimcache", f"-I{nim_lib}"]
    run(*cflags, "-Wall", "-Wextra", "-Werror", "src/caller.c", "-Lobserved/bin",
        "-lbuffer_api", "-Wl,-rpath,@loader_path", "-o", "observed/bin/caller")
    expanded = run(*cflags, "-E", "-P", "-x", "c", "-", input_text='#include "buffer_api.h"\n')
    declarations = "\n".join(line for line in expanded.splitlines()
                             if re.search(r"extern size_t asmati_", line)) + "\n"
    require(r"extern size_t asmati_trimmed_length\(NU8\* input_p0, size_t length_p1\);", declarations)
    require(r"extern size_t asmati_write_label\(NU8\* output_p0, size_t capacity_p1\);", declarations)
    macros = run(*cflags, "-dM", "-E", "-x", "c", "-", input_text='#include "buffer_api.h"\n')
    selected_macros = "\n".join(line for line in macros.splitlines()
                                if re.match(r"#define (NIM_EXTERNC|N_CDECL\(|N_LIB_EXPORT |N_LIB_IMPORT |NIM_POSIX_INIT )", line)) + "\n"
    require(r"^#define NIM_EXTERNC\s*$", selected_macros)
    require(r'^#define N_CDECL\(rettype,name\) rettype name', selected_macros)
    require(r'^#define NIM_POSIX_INIT __attribute__\(\(constructor\)\)', selected_macros)
    symbols = run("nm", "-gU", "observed/bin/libbuffer_api.dylib")
    for symbol in ("_asmati_trimmed_length", "_asmati_write_label", "_NimMain"):
        require(r"\bT " + symbol + r"$", symbols)
    imports = run("nm", "-u", "observed/bin/caller")
    for symbol in ("_asmati_trimmed_length", "_asmati_write_label"):
        require(symbol + r"$", imports)
    if "_NimMain" in imports:
        raise AssertionError("C caller unexpectedly imports NimMain")
    linkage = run("otool", "-L", "observed/bin/caller")
    require(r"@rpath/libbuffer_api\.dylib", linkage)
    binary_info = run("file", "observed/bin/libbuffer_api.dylib") + run("file", "observed/bin/caller")
    require(r"libbuffer_api\.dylib: Mach-O 64-bit .*" + arch, binary_info)
    require(r"caller: Mach-O 64-bit executable " + arch, binary_info)
    output = run("observed/bin/caller")
    if output != EXPECTED:
        raise AssertionError(f"unexpected caller output: {output}")

    def function(name: str) -> str:
        return require(r"^N_LIB_EXPORT N_CDECL\([^\n]+, " + name
                       + r"\)[^\n]+ \{[\s\S]*?^\}", generated)

    min_helper = require(r"^static N_INLINE\(size_t, min__[^\n]+\)\([^\n]+\) \{[\s\S]*?^\}", generated)
    excerpts = [function("asmati_trimmed_length"), min_helper, function("asmati_write_label")]
    for excerpt in excerpts:
        if re.search(r"rawNewString|newSeq|nimNewObj|malloc|alloc", excerpt):
            raise AssertionError("exported buffer function contains an allocation helper")
    excerpts.append(require(r"^N_LIB_PRIVATE void NIM_POSIX_INIT NimMainInit\(void\) \{[\s\S]*?^\}", generated))
    env = ("recorded_utc=" + datetime.now(timezone.utc).isoformat() + "\n"
           + run("sw_vers") + "machine=" + run("uname", "-m") + nim_version
           + run("clang", "--version").splitlines()[0] + "\nselected_target=" + target + "\n")
    if args.record:
        artifacts = {
            "buffer_api.h": header,
            "generated-c-excerpt.c": "/* Nim 2.2.10 observed/nimcache/@mbuffer_api.nim.c.\n"
                " * Excerpt: exported functions and constructor; helpers omitted.\n"
                " * Local source paths normalized to <EXPERIMENT>. */\n\n" + "\n\n".join(excerpts) + "\n",
            "c-macro-expansion.txt": "Nim 2.2.10 lib/nimbase.h, Clang C11 preprocessing:\n"
                + selected_macros + "\nSelected typedef:\n"
                + require(r"^typedef unsigned char uint8_t;$", expanded) + "\n"
                + require(r"^typedef uint8_t NU8;$", expanded)
                + "\n\nExpanded API declarations:\n" + declarations,
            "symbols-linkage.txt": symbols + "\nCaller imports (selected):\n"
                + "\n".join(line for line in imports.splitlines() if "asmati_" in line)
                + "\nNo _NimMain import in C caller.\n" + linkage,
            "run-2026-09-04.txt": binary_info + "\n" + output + "exit=0\n",
            "environment.txt": env,
            "commands-2026-09-04.txt": "Input for Clang stdin probes: #include \"buffer_api.h\"\n\n"
                + "\n".join(entry.splitlines()[0] + "\n[Selected output in c-macro-expansion.txt]\nexit=0\n"
                             if entry.startswith("$ clang -arch") and " -E " in entry else entry
                             for entry in logs),
        }
        for name, content in artifacts.items():
            (ROOT / "observed" / name).write_text(clean(content))
    print(f"target={target}")
    print(EXPECTED, end="")
    print("Nim C buffer pointer, length, capacity, and canaries verified")


if __name__ == "__main__":
    main()
