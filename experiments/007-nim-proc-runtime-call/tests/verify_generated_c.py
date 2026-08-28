from __future__ import annotations

from pathlib import Path
import re

from toolchain import find_nim_lib


SOURCE_PATTERNS = {
    "source proc": r"proc addSuffix\(value: string\): string\s*=\s*value & \"!\"",
    "source call": r"echo addSuffix\(\"nim\"\)",
}

MODULE_PATTERNS = {
    "NimStringV2 layout": r"struct NimStringV2\s*\{\s*NI len;\s*NimStrPayload\* p;\s*\};",
    "generated proc declaration": r"N_NIMCALL\(NimStringV2,\s*addSuffix__proc95runtime_u1\)\(NimStringV2 value_p0\);",
    "generated proc definition": r"N_NIMCALL\(NimStringV2,\s*addSuffix__proc95runtime_u1\)\(NimStringV2 value_p0\)\s*\{",
    "result capacity": r"rawNewString\(value_p0\.len \+ 1\)",
    "source value append": r"appendString\(\(&T1_\),\s*value_p0\);",
    "suffix append": r"appendString\(\(&T1_\),\s*TM__[A-Za-z0-9_]+_3\);",
    "result return": r"result = T1_;.*return result;",
    "append copy": r"appendString.*copyMem__system_u1755",
    "append length": r"\(\*dest_p0\)\.len \+= src_p1\.len;",
    "append terminator": r"data\[\(\*dest_p0\)\.len\] = 0;",
    "copy helper": r"nimCopyMem\(dest_p0,\s*source_p1,\s*size_p2\);",
    "memcpy boundary": r"memcpy\(dest_p0,\s*source_p1,",
    "main proc call": r"addSuffix__proc95runtime_u1\(TM__[A-Za-z0-9_]+_5\)",
}

SYSTEM_C_PATTERNS = {
    "rawNewString definition": r"N_NIMCALL\(NimStringV2,\s*rawNewString\)\(NI space_p0\)\s*\{",
    "rawNewString capacity": r"\(\*p_1\)\.cap = space_p0;",
    "rawNewString terminator": r"\(\*p_1\)\.data\[\(\(NI\)0\)\] = 0;",
    "rawNewString empty result": r"result\.len = \(\(NI\)0\);.*result\.p = p_1;",
}

SYSTEM_NIM_PATTERNS = {
    "string-string concatenation magic": r"proc `&`\*\(x, y: string\): string\s*\{\.\s*magic: \"ConStrStr\"",
}

STRS_V2_PATTERNS = {
    "NimStringV2 source layout": r"NimStringV2 \{\.core\.\} = object\s*len: int\s*p: ptr NimStrPayload",
    "appendString source": r"proc appendString\(dest: var NimStringV2; src: NimStringV2\).*?copyMem.*?inc dest\.len, src\.len.*?dest\.p\.data\[dest\.len\] = '\\0'",
    "rawNewString source": r"proc rawNewString\(space: int\): NimStringV2.*?if space <= 0:.*?p\.cap = space.*?p\.data\[0\] = '\\0'.*?result = NimStringV2\(len: 0, p: p\)",
}


def missing_patterns(source: str, patterns: dict[str, str]) -> list[str]:
    flags = re.MULTILINE | re.DOTALL
    return [name for name, pattern in patterns.items() if re.search(pattern, source, flags) is None]


def main() -> int:
    experiment = Path(__file__).parents[1]
    nimcache = experiment / "observed" / "nimcache"
    source = (experiment / "src" / "proc_runtime.nim").read_text(encoding="utf-8")
    module_c = (nimcache / "@mproc_runtime.nim.c").read_text(encoding="utf-8")
    system_c = (nimcache / "@psystem.nim.c").read_text(encoding="utf-8")
    nim_lib = find_nim_lib(experiment)
    system_nim = (nim_lib / "system.nim").read_text(encoding="utf-8")
    strs_v2 = (nim_lib / "system" / "strs_v2.nim").read_text(encoding="utf-8")

    missing = []
    missing.extend(f"source: {name}" for name in missing_patterns(source, SOURCE_PATTERNS))
    missing.extend(f"generated module C: {name}" for name in missing_patterns(module_c, MODULE_PATTERNS))
    missing.extend(f"generated system C: {name}" for name in missing_patterns(system_c, SYSTEM_C_PATTERNS))
    missing.extend(f"system.nim: {name}" for name in missing_patterns(system_nim, SYSTEM_NIM_PATTERNS))
    missing.extend(f"system/strs_v2.nim: {name}" for name in missing_patterns(strs_v2, STRS_V2_PATTERNS))

    if missing:
        raise SystemExit("missing observations: " + ", ".join(missing))
    print("source proc, generated C function, and string runtime calls verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
