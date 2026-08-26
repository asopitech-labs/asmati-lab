from __future__ import annotations

from pathlib import Path
import re


NIMCACHE = Path(__file__).parents[1] / "observed" / "nimcache"
GENERATED_C = NIMCACHE / "@mref_proc.nim.c"
READING_TYPE = r"tyObject_Reading[^\s*]*"
EXPECTED_PATTERNS = {
    "Reading object layout": rf"struct\s+{READING_TYPE}\s*\{{\s*NI\s+value;",
    "readValue pointer argument": (
        rf"N_NOINLINE\(NI,\s*readValue[^)]*\)\({READING_TYPE}\*\s+reading_p0\)"
    ),
    "keepReading pointer argument and return": (
        rf"N_NOINLINE\({READING_TYPE}\*,\s*keepReading[^)]*\)"
        rf"\({READING_TYPE}\*\s+reading_p0\)"
    ),
    "nil branch": r"if\s*\(!\(reading_p0\s*==\s*0\)\)",
    "field dereference": r"result\s*=\s*\(\*reading_p0\)\.value;",
    "nil return initialization": r"result\s*=\s*NIM_NIL;",
    "ref return copy": r"eqcopy[^;]*\(&result,\s*reading_p0\);",
}


def main() -> int:
    if not GENERATED_C.is_file():
        raise SystemExit(f"generated C file not found: {GENERATED_C}")
    source = GENERATED_C.read_text(encoding="utf-8")
    missing = [
        name
        for name, pattern in EXPECTED_PATTERNS.items()
        if re.search(pattern, source, re.MULTILINE) is None
    ]
    if missing:
        raise SystemExit(f"generated C observations missing: {', '.join(missing)}")
    print("generated C ref pointer and nil branch verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
