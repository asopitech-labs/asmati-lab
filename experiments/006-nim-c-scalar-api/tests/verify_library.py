from __future__ import annotations

from pathlib import Path
import re
import subprocess

from toolchain import find_nim_lib


HEADER_PATTERNS = {
    "nimbase include": r'#include\s+"nimbase\.h"',
    "integer API": r"N_LIB_IMPORT\s+N_CDECL\(int,\s*asmati_add_ints\)\(int\s+left_p0,\s*int\s+right_p1\);",
    "floating API": r"N_LIB_IMPORT\s+N_CDECL\(double,\s*asmati_half\)\(double\s+value_p0\);",
    "NimMain declaration": r"N_LIB_IMPORT\s+N_CDECL\(void,\s*NimMain\)\(void\);",
}

GENERATED_C_PATTERNS = {
    "exported integer definition": r"N_LIB_EXPORT\s+N_CDECL\(int,\s*asmati_add_ints\)",
    "exported floating definition": r"N_LIB_EXPORT\s+N_CDECL\(double,\s*asmati_half\)",
    "exported NimMain": r"N_LIB_EXPORT\s+N_CDECL\(void,\s*NimMain\)",
    "POSIX initializer": r"N_LIB_PRIVATE\s+void\s+NIM_POSIX_INIT\s+NimMainInit\(void\)\s*\{\s*NimMain\(\);\s*\}",
}

NIMBASE_PATTERNS = {
    "cdecl expansion": r"#\s*define\s+N_CDECL\(rettype,\s*name\)\s+rettype\s+name",
    "default-visible export": r"#\s*define\s+N_LIB_EXPORT\s+NIM_EXTERNC\s+__attribute__\(\(visibility\(\"default\"\)\)\)",
    "POSIX constructor": r"#define\s+NIM_POSIX_INIT\s+__attribute__\(\(constructor\)\)",
}


def missing_patterns(source: str, patterns: dict[str, str]) -> list[str]:
    return [name for name, pattern in patterns.items() if re.search(pattern, source, re.MULTILINE | re.DOTALL) is None]


def main() -> int:
    experiment = Path(__file__).parents[1]
    header = (experiment / "observed" / "scalar_api.h").read_text(encoding="utf-8")
    generated_c = (experiment / "observed" / "nimcache" / "@mscalar_api.nim.c").read_text(encoding="utf-8")
    nimbase = (find_nim_lib(experiment) / "nimbase.h").read_text(encoding="utf-8")

    missing = []
    missing.extend(f"header: {name}" for name in missing_patterns(header, HEADER_PATTERNS))
    missing.extend(f"generated C: {name}" for name in missing_patterns(generated_c, GENERATED_C_PATTERNS))
    missing.extend(f"nimbase.h: {name}" for name in missing_patterns(nimbase, NIMBASE_PATTERNS))

    library = experiment / "observed" / "bin" / "libscalar_api.dylib"
    symbols = subprocess.run(
        ["nm", "-gU", str(library)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    for symbol in ("_asmati_add_ints", "_asmati_half", "_NimMain"):
        if symbol not in symbols:
            missing.append(f"library symbol: {symbol}")

    install_name = subprocess.run(
        ["otool", "-D", str(library)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if "@rpath/libscalar_api.dylib" not in install_name:
        missing.append("dylib install name: @rpath/libscalar_api.dylib")

    if missing:
        raise SystemExit("missing observations: " + ", ".join(missing))
    print("header, public symbols, and POSIX initialization verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
