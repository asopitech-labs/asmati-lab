from __future__ import annotations

from pathlib import Path
import re


NIMCACHE = Path(__file__).parents[1] / "observed" / "nimcache"
GENERATED_C = NIMCACHE / "@mscalar_proc.nim.c"
EXPECTED_PATTERNS = {
    "noArgs": r"N_NIMCALL\(NI,\s*noArgs[^)]*\)\(void\)",
    "addOne": r"N_NIMCALL\(NI,\s*addOne[^)]*\)\(NI\s+x_p0\)",
    "half": r"N_NIMCALL\(NF,\s*half[^)]*\)\(NF\s+x_p0\)",
}


def main() -> int:
    if not GENERATED_C.is_file():
        raise SystemExit(f"generated C file not found: {GENERATED_C}")
    source = GENERATED_C.read_text(encoding="utf-8")
    missing = [name for name, pattern in EXPECTED_PATTERNS.items() if re.search(pattern, source) is None]
    if missing:
        raise SystemExit(f"generated C signatures missing: {', '.join(missing)}")
    if "#define NIM_INTBITS 64" not in source:
        raise SystemExit("generated C does not define NIM_INTBITS 64")
    print("generated C signatures verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
