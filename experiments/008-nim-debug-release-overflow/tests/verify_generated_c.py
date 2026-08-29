from __future__ import annotations

from pathlib import Path
import re

from toolchain import find_nim_lib


ADD_ONE = re.compile(
    r"N_NOINLINE\(NI,\s*addOne[^)]*\)\(NI value_p0\)\s*\{(?P<body>.*?)\n\}",
    re.DOTALL,
)


def require(source: str, pattern: str, label: str, flags: int = 0) -> None:
    if re.search(pattern, source, flags) is None:
        raise SystemExit(f"missing observation: {label}")


def config_block(source: str, condition: str) -> str:
    match = re.search(rf"@if {re.escape(condition)}:\n(?P<body>.*?)@end", source, re.DOTALL)
    if match is None:
        raise SystemExit(f"missing config block: {condition}")
    return match.group("body")


def main() -> int:
    experiment = Path(__file__).parents[1]
    source = (experiment / "src" / "overflow_compare.nim").read_text(encoding="utf-8")
    debug_c = (experiment / "observed" / "nimcache" / "debug" / "@moverflow_compare.nim.c").read_text(encoding="utf-8")
    release_c = (experiment / "observed" / "nimcache" / "release" / "@moverflow_compare.nim.c").read_text(encoding="utf-8")
    debug_system_c = (experiment / "observed" / "nimcache" / "debug" / "@psystem.nim.c").read_text(encoding="utf-8")
    release_system_c = (experiment / "observed" / "nimcache" / "release" / "@psystem.nim.c").read_text(encoding="utf-8")

    require(source, r"proc addOne\(value: int\): int \{\.noinline\.\}\s*=\s*value \+ 1", "fixed source proc", re.DOTALL)
    debug_match = ADD_ONE.search(debug_c)
    release_match = ADD_ONE.search(release_c)
    if debug_match is None or release_match is None:
        raise SystemExit("missing observation: addOne generated C function")

    for mode, generated_c, body, system_c in (
        ("debug", debug_c, debug_match.group("body"), debug_system_c),
        ("release", release_c, release_match.group("body"), release_system_c),
    ):
        require(generated_c, r"#define NIM_INTBITS 64", f"{mode} NIM_INTBITS")
        require(body, r"nimAddInt\(value_p0,\s*\(\(NI\)1\),\s*&[A-Za-z0-9_]+\)", f"{mode} nimAddInt")
        require(body, r"raiseOverflow\(\);", f"{mode} raiseOverflow branch")
        require(system_c, r"N_NOINLINE\(void,\s*raiseOverflow\)\(void\)\s*\{\s*sysFatal", f"{mode} raiseOverflow definition", re.DOTALL)

    debug_header = "\n".join(debug_c.splitlines()[:6])
    release_header = "\n".join(release_c.splitlines()[:6])
    if " -O3 " in debug_header:
        raise SystemExit("unexpected observation: debug C compiler command contains -O3")
    if " -O3 " not in release_header:
        raise SystemExit("missing observation: release C compiler command contains -O3")
    for marker in ("nimfr_", "nimlf_", "popFrame"):
        if marker not in debug_match.group("body"):
            raise SystemExit(f"missing observation: debug {marker}")
        if marker in release_match.group("body"):
            raise SystemExit(f"unexpected observation: release {marker}")

    nim_lib = find_nim_lib(experiment)
    nim_cfg = (nim_lib.parent / "config" / "nim.cfg").read_text(encoding="utf-8")
    nimbase = (nim_lib / "nimbase.h").read_text(encoding="utf-8")
    release_block = config_block(nim_cfg, "release or danger")
    danger_block = config_block(nim_cfg, "danger or quick")
    for setting in ("stacktrace:off", "opt:speed", "define:release"):
        if setting not in release_block:
            raise SystemExit(f"missing release config: {setting}")
    if "overflow_checks:off" in release_block:
        raise SystemExit("unexpected release config: overflow_checks:off")
    if "overflow_checks:off" not in danger_block:
        raise SystemExit("missing danger config: overflow_checks:off")
    require(nimbase, r"#define nimAddInt\(a, b, res\) __builtin_saddll_overflow", "nimAddInt 64-bit macro")

    print("debug/release overflow generation and definitions verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
