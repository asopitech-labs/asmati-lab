"""Build fresh evidence; --record explicitly saves this machine's sanitized observations."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import re
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = ("size=8 align=4 left=0 right=4\n"
            "case=0 scalar=42 pair=42\n"
            "case=1 scalar=-93 pair=-93\n"
            "case=2 scalar=32768 pair=32768\n")


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
        text = re.sub(r"InstalledDir: .*", "InstalledDir: <CLANG_TOOLCHAIN>", text)
        text = text.replace(str(ROOT), "<EXPERIMENT>")
        if nim_lib:
            text = text.replace(str(nim_lib.parent), "<NIM_ROOT>")
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
    rust_version = run("rustc", "-vV")
    host = require(r"^host: .+$", rust_version).removeprefix("host: ")
    targets = {"x86_64-apple-darwin": ("x86_64", "amd64"),
               "aarch64-apple-darwin": ("arm64", "arm64")}
    if host not in targets:
        raise RuntimeError(f"unsupported native Rust target: {host}")
    arch, cpu = targets[host]
    dump = subprocess.run(["nim", "dump", "--verbosity:0", "src/pair_api.nim"],
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
    # Explicit forceBuild avoids verifying stale object files after source changes.
    run("nim", "c", "--forceBuild:on", "--cc:clang", f"--cpu:{cpu}",
        f"--passC:-arch {arch}", f"--passL:-arch {arch}", "--mm:orc",
        "--app:lib", "--header:pair_api.h", "--nimcache:observed/nimcache",
        "--out:observed/bin/libpair_api.dylib",
        "--passL:-Wl,-install_name,@rpath/libpair_api.dylib", "src/pair_api.nim")
    header = (ROOT / "observed/nimcache/pair_api.h").read_text()
    target_define = "#define NIM_EmulateOverflowChecks\n"
    if (target_define in header) != (arch == "arm64"):
        raise AssertionError("unexpected target-specific overflow macro")
    if not args.record:
        saved = (ROOT / "observed/pair_api.h").read_text()
        if clean(header).replace(target_define, "") != saved.replace(target_define, ""):
            raise AssertionError("generated header differs beyond known target macro")
    generated = (ROOT / "observed/nimcache/@mpair_api.nim.c").read_text()
    require(r"struct AsmatiPair \{\s+int left;\s+int right;\s+\};", header)
    require(r"N_LIB_IMPORT N_CDECL\(int, asmati_sum_pair\)\(AsmatiPair pair_p0\);", header)
    require(r"N_LIB_EXPORT N_CDECL\(int, asmati_sum_pair\)\(AsmatiPair pair_p0\) \{", generated)
    require(r"NIM_POSIX_INIT NimMainInit\(void\) \{\s+NimMain\(\);\s+\}", generated)
    rust_source = (ROOT / "src/rust_caller.rs").read_text()
    require(r'#\[repr\(C\)\][\s\S]*?struct AsmatiPair \{\s+left: c_int,\s+right: c_int,\s+\}', rust_source)
    require(r'unsafe extern "C" \{\s+fn asmati_add\(left: c_int, right: c_int\) -> c_int;\s+fn asmati_sum_pair\(pair: AsmatiPair\) -> c_int;', rust_source)
    cflags = ["clang", "-arch", arch, "-std=c11", "-Iobserved/nimcache", f"-I{nim_lib}"]
    run(*cflags, "-Wall", "-Wextra", "-Werror", "src/c_caller.c",
        "-Lobserved/bin", "-lpair_api", "-Wl,-rpath,@loader_path",
        "-o", "observed/bin/c_caller")
    run("rustc", "--edition=2024", "-Dwarnings", "-Dimproper_ctypes", "--target", host,
        "src/rust_caller.rs", "-L", "native=observed/bin", "-l", "dylib=pair_api",
        "-C", "link-arg=-Wl,-rpath,@loader_path", "-o", "observed/bin/rust_caller")
    # Clang preprocess resolves macros under the actual C caller conditions.
    expanded = run(*cflags, "-E", "-P", "-x", "c", "-", input_text='#include "pair_api.h"\n')
    declarations = "\n".join(line for line in expanded.splitlines()
                             if re.search(r"extern int asmati_(add|sum_pair)\(", line)) + "\n"
    require(r"extern int asmati_sum_pair\(AsmatiPair pair_p0\);", declarations)
    macros = run(*cflags, "-dM", "-E", "-x", "c", "-", input_text='#include "pair_api.h"\n')
    selected_macros = "\n".join(line for line in macros.splitlines()
                                if re.match(r"#define (NIM_EXTERNC|N_CDECL\(|N_LIB_EXPORT |N_LIB_IMPORT |NIM_POSIX_INIT )", line)) + "\n"
    require(r"^#define NIM_EXTERNC\s*$", selected_macros)
    require(r'^#define NIM_POSIX_INIT __attribute__\(\(constructor\)\)', selected_macros)
    require(r'^#define N_CDECL\(rettype,name\) rettype name', selected_macros)
    require(r'^#define N_LIB_EXPORT NIM_EXTERNC __attribute__\(\(visibility\("default"\)\)\)', selected_macros)
    symbols = run("nm", "-gU", "observed/bin/libpair_api.dylib")
    for symbol in ("_asmati_add", "_asmati_sum_pair", "_NimMain"):
        require(r"\bT " + symbol + r"$", symbols)
    imports = run("nm", "-u", "observed/bin/rust_caller")
    require(r"_asmati_sum_pair$", imports)
    require(r"_asmati_add$", imports)
    if "_NimMain" in imports:
        raise AssertionError("Rust caller unexpectedly imports NimMain")
    linkage = run("otool", "-L", "observed/bin/rust_caller")
    require(r"@rpath/libpair_api\.dylib", linkage)
    binaries = []
    outputs = []
    for name in ("libpair_api.dylib", "c_caller", "rust_caller"):
        info = run("file", f"observed/bin/{name}")
        require(r"Mach-O 64-bit .*" + arch, info)
        binaries.append(info)
    for name in ("c_caller", "rust_caller"):
        output = run(f"observed/bin/{name}")
        if output != EXPECTED:
            raise AssertionError(f"unexpected {name} result: {output}")
        outputs.append(name + "\n" + output + "exit=0\n")
    # Preserve focused generated definitions, not a second hand-written API header.
    excerpts = [require(r"typedef struct AsmatiPair AsmatiPair;[\s\S]*?\n\};", generated)]
    for name in ("asmati_add", "asmati_sum_pair", "NimMain"):
        excerpts.append(require(r"^N_LIB_EXPORT N_CDECL\([^\n]+, " + name
                                + r"\)[^\n]+ \{[\s\S]*?^\}", generated))
    excerpts.append(require(r"^N_LIB_PRIVATE void NIM_POSIX_INIT NimMainInit\(void\) \{[\s\S]*?^\}", generated))
    env = ("recorded_utc=" + datetime.now(timezone.utc).isoformat() + "\n"
           + run("sw_vers") + "machine=" + run("uname", "-m")
           + nim_version + rust_version + run("clang", "--version").splitlines()[0]
           + "\nselected_target=" + host + "\n")
    if args.record:
        artifacts = {
            "pair_api.h": header,
            "generated-c-excerpt.c": "/* Nim 2.2.10: observed/nimcache/@mpair_api.nim.c.\n"
                " * Excerpt: struct, APIs, NimMain, constructor; runtime helper bodies omitted.\n"
                " * Local source paths normalized to <EXPERIMENT>. */\n\n" + "\n\n".join(excerpts) + "\n",
            "c-macro-expansion.txt": "Nim 2.2.10 lib/nimbase.h, actual Clang C11 preprocessing:\n"
                + selected_macros + "\nExpanded generated header declarations:\n" + declarations,
            "symbols-linkage.txt": symbols + "\nRust imports (selected):\n"
                + "\n".join(line for line in imports.splitlines() if "asmati_" in line)
                + "\nNo _NimMain import in Rust caller.\n" + linkage,
            "run-2026-09-03.txt": "".join(binaries) + "\n" + "\n".join(outputs),
            "environment.txt": env,
            "commands-2026-09-03.txt": "Input for Clang stdin probes: #include \"pair_api.h\"\n\n"
                + "\n".join(entry.splitlines()[0] + "\n[Selected output in c-macro-expansion.txt]\nexit=0\n"
                             if entry.startswith("$ clang -arch") and " -E " in entry else entry
                             for entry in logs)
        }
        for name, content in artifacts.items():
            (ROOT / "observed" / name).write_text(clean(content))
    print(f"target={host}")
    print(EXPECTED, end="")
    print("Nim library C/Rust scalar and by-value struct calls verified")


if __name__ == "__main__":
    main()
