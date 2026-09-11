"""Build object type/cast evidence; --record saves sanitized observations."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import re
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
NORMAL_EXPECTED = (
    "dogOfDog=true\n"
    "catOfDog=false\n"
    "dogResult=7\n"
    "catResult=-9\n"
    "forcedDog=7\n"
)
FAIL_STDOUT = "checkedDog=7\n"


def require(pattern: str, value: str) -> str:
    match = re.search(pattern, value, re.MULTILINE)
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

    dump = subprocess.run(["nim", "dump", "--verbosity:0", "src/object_type_cast.nim"],
                          cwd=ROOT, capture_output=True, text=True, check=True)
    for line in (dump.stdout + "\n" + dump.stderr).splitlines():
        candidate = Path(line.strip())
        if (candidate / "system.nim").is_file():
            nim_lib = candidate.resolve()
            break
    if nim_lib is None:
        raise RuntimeError("Nim library source not found in search paths")

    (ROOT / "observed/bin").mkdir(parents=True, exist_ok=True)
    (ROOT / "observed/nimcache/normal").mkdir(parents=True, exist_ok=True)
    (ROOT / "observed/nimcache/fail").mkdir(parents=True, exist_ok=True)
    common = ["nim", "c", "--forceBuild:on", "--cc:clang", f"--cpu:{cpu}",
              f"--passC:-arch {arch}", f"--passL:-arch {arch}", "--mm:orc"]
    run(*common, "--nimcache:observed/nimcache/normal",
        "--out:observed/bin/object_type_cast", "src/object_type_cast.nim")
    run(*common, "-d:forceFailedCast", "--nimcache:observed/nimcache/fail",
        "--out:observed/bin/object_type_cast_fail", "src/object_type_cast.nim")

    normal_c = (ROOT / "observed/nimcache/normal/@mobject_type_cast.nim.c").read_text()
    fail_c = (ROOT / "observed/nimcache/fail/@mobject_type_cast.nim.c").read_text()
    fail_runtime = (ROOT / "observed/nimcache/fail/@psystem.nim.c").read_text()

    type_info = require(
        r"struct TNimTypeV2 \{\s*void\* destructor;\s*NI size;\s*NI16 align;\s*"
        r"NI16 depth;\s*NU32\* display;[\s\S]*?void\* vTable\[SEQ_DECL_SIZE\];\s*\};",
        normal_c)
    root_obj = require(r"struct RootObj \{\s*TNimTypeV2\* m_type;\s*\};", normal_c)

    animal_match = re.search(
        r"struct (tyObject_AnimalcolonObjectType__[^\s]+) \{\s*RootObj Sup;\s*NI id;\s*\};",
        normal_c)
    if not animal_match:
        raise AssertionError("missing Animal struct")
    animal_type = animal_match.group(1)
    animal_struct = animal_match.group(0)
    dog_match = re.search(
        rf"struct (tyObject_DogcolonObjectType__[^\s]+) \{{\s*{re.escape(animal_type)} Sup;\s*"
        r"NI barkVolume;\s*\};", normal_c)
    cat_match = re.search(
        rf"struct (tyObject_CatcolonObjectType__[^\s]+) \{{\s*{re.escape(animal_type)} Sup;\s*"
        r"NI lives;\s*\};", normal_c)
    if not dog_match or not cat_match:
        raise AssertionError("missing Dog or Cat struct")
    dog_type, cat_type = dog_match.group(1), cat_match.group(1)
    dog_struct, cat_struct = dog_match.group(0), cat_match.group(0)

    def metadata_for(type_name: str, text: str) -> tuple[str, str, list[str]]:
        pattern = (
            r"static NIM_CONST NU32 (?P<array>[A-Za-z0-9_]+)\[3\] = "
            r"\{(?P<tokens>[0-9, ]+)\};\s*"
            r"N_LIB_PRIVATE TNimTypeV2 (?P<desc>[A-Za-z0-9_]+) = "
            rf"\{{\.destructor = [\s\S]{{0,220}}?\.size = sizeof\({re.escape(type_name)}\), "
            rf"[\s\S]{{0,260}}?\.depth = 2, \.display = (?P=array),[\s\S]{{0,220}}?\}};"
        )
        match = re.search(pattern, text)
        if not match:
            raise AssertionError(f"missing metadata for {type_name}")
        tokens = [part.strip() for part in match.group("tokens").split(",")]
        if len(tokens) != 3:
            raise AssertionError(f"unexpected display tokens for {type_name}")
        return match.group(0), match.group("desc"), tokens

    dog_metadata, dog_desc, dog_tokens = metadata_for(dog_type, normal_c)
    cat_metadata, cat_desc, cat_tokens = metadata_for(cat_type, normal_c)
    if dog_tokens[:2] != cat_tokens[:2]:
        raise AssertionError("Dog and Cat ancestor tokens must match")
    dog_token, cat_token = dog_tokens[2], cat_tokens[2]
    if dog_token == cat_token:
        raise AssertionError("Dog and Cat class tokens must differ")

    display_check = function_at(normal_c, "isObjDisplayCheck)(")
    require(r"targetDepth_p1 <= \(\*source_p0\)\.depth", display_check)
    require(r"\(\*source_p0\)\.display\[targetDepth_p1\] == token_p2", display_check)

    identify_decl = require(
        rf"N_LIB_PRIVATE N_NOINLINE\(NI, identify__[^\n]+\)\({re.escape(animal_type)}\* animal_p0\);",
        normal_c)
    identify_name = re.search(r"(identify__[^)]+)", identify_decl).group(1)  # type: ignore[union-attr]
    identify_def = function_at(normal_c, identify_name + ")(")
    require(r"\(\*animal_p0\)\.Sup\.m_type", identify_def)
    require(rf"isObjDisplayCheck\([^\n]+, 2, {dog_token}\)", identify_def)
    require(rf"isObjDisplayCheck\([^\n]+, 2, {cat_token}\)", identify_def)
    require(r"raiseObjectConversionError\(\)", identify_def)
    require(rf"\*\(\({re.escape(dog_type)}\*\) \(animal_p0\)\)\)\.barkVolume", identify_def)
    require(rf"\*\(\({re.escape(cat_type)}\*\) \(animal_p0\)\)\)\.lives", identify_def)

    fail_dog_match = re.search(r"struct (tyObject_DogcolonObjectType__[^\s]+) \{", fail_c)
    fail_animal_match = re.search(r"struct (tyObject_AnimalcolonObjectType__[^\s]+) \{", fail_c)
    if not fail_dog_match or not fail_animal_match:
        raise AssertionError("missing failed-build object types")
    fail_dog_type, fail_animal_type = fail_dog_match.group(1), fail_animal_match.group(1)
    force_decl = require(
        rf"N_LIB_PRIVATE N_NOINLINE\(NI, forceDog__[^\n]+\)\({re.escape(fail_animal_type)}\* animal_p0\);",
        fail_c)
    force_name = re.search(r"(forceDog__[^)]+)", force_decl).group(1)  # type: ignore[union-attr]
    force_def = function_at(fail_c, force_name + ")(")
    require(rf"!isObjDisplayCheck\([^\n]+, 2, {dog_token}\)", force_def)
    require(r"raiseObjectConversionError\(\)", force_def)
    require(rf"\*\(\({re.escape(fail_dog_type)}\*\) \(animal_p0\)\)\)\.barkVolume", force_def)
    raise_def = function_at(fail_runtime, "raiseObjectConversionError)(void)")
    require(r"sysFatal__system_[A-Za-z0-9_]+\(", raise_def)

    dog_init = require(
        rf"(?P<tmp>T[0-9]+_) = \({re.escape(dog_type)}\*\) nimNewObjUninit\([^;]+;\s*"
        rf"\(\*(?P=tmp)\)\.Sup\.Sup\.m_type = \(&{re.escape(dog_desc)}\);\s*"
        rf"\(\*(?P=tmp)\)\.Sup\.id = \(\(NI\)1\);\s*"
        rf"\(\*(?P=tmp)\)\.barkVolume = \(\(NI\)7\);\s*"
        rf"dog__[A-Za-z0-9_]+ = &(?P=tmp)->Sup;", normal_c)
    cat_init = require(
        rf"(?P<tmp>T[0-9]+_) = \({re.escape(cat_type)}\*\) nimNewObjUninit\([^;]+;\s*"
        rf"\(\*(?P=tmp)\)\.Sup\.Sup\.m_type = \(&{re.escape(cat_desc)}\);\s*"
        rf"\(\*(?P=tmp)\)\.Sup\.id = \(\(NI\)2\);\s*"
        rf"\(\*(?P=tmp)\)\.lives = \(\(NI\)9\);\s*"
        rf"cat__[A-Za-z0-9_]+ = &(?P=tmp)->Sup;", normal_c)

    normal = run("observed/bin/object_type_cast")
    if normal != NORMAL_EXPECTED:
        raise AssertionError(f"unexpected normal output: {normal}")
    failed = execute("observed/bin/object_type_cast_fail")
    if failed.returncode == 0:
        raise AssertionError("invalid cast unexpectedly succeeded")
    if failed.stdout != FAIL_STDOUT:
        raise AssertionError(f"unexpected failed-cast stdout: {failed.stdout}")
    require(r"invalid object conversion", failed.stderr)
    require(r"\[ObjectConversionDefect\]", failed.stderr)
    require(r"forceDog", failed.stderr)
    normal_info = run("file", "observed/bin/object_type_cast")
    fail_info = run("file", "observed/bin/object_type_cast_fail")
    require(r"object_type_cast: Mach-O 64-bit executable " + arch, normal_info)
    require(r"object_type_cast_fail: Mach-O 64-bit executable " + arch, fail_info)

    system_source = (nim_lib / "system.nim").read_text()
    arc_source = (nim_lib / "system/arc.nim").read_text()
    checks_source = (nim_lib / "system/chcks.nim").read_text()
    exceptions_source = (nim_lib / "system/exceptions.nim").read_text()
    metadata_source = require(
        r"when not defined\(js\) and defined\(nimV2\):\n  type\n[\s\S]*?"
        r"    TNimTypeV2 \{\.compilerproc\.\} = object\n"
        r"[\s\S]*?    PNimTypeV2 = ptr TNimTypeV2", system_source)
    display_source = require(
        r"proc isObjDisplayCheck\(source: PNimTypeV2, targetDepth: int16, token: uint32\): bool "
        r"\{\.compilerRtl, inl\.\} =\n"
        r"  result = targetDepth <= source\.depth and source\.display\[targetDepth\] == token",
        arc_source)
    raise_source = require(
        r"proc raiseObjectConversionError\(\) \{\.compilerproc, noinline\.\} =\n"
        r"  sysFatal\(ObjectConversionDefect, \"invalid object conversion\"\)", checks_source)
    defect_source = require(
        r"  ObjectConversionDefect\* = object of Defect ## \\\n"
        r"    ## Raised if an object is converted to an incompatible object type\.\n"
        r"    ## You can use `of` operator to check if conversion will succeed\.", exceptions_source)
    definitions = (
        "# Nim 2.2.10 lib/system.nim, system/arc.nim, system/chcks.nim,\n"
        "# and system/exceptions.nim. Selected definitions only.\n\n"
        + metadata_source + "\n\n" + display_source + "\n\n"
        + raise_source + "\n\n" + defect_source + "\n"
    )
    if not args.record:
        saved = (ROOT / "observed/toolchain-definition-excerpt.nim").read_text()
        if definitions != saved:
            raise AssertionError("saved toolchain definitions differ from Nim 2.2.10")

    normal_excerpt = (
        "/* Nim 2.2.10 normal generated C. Selected type metadata and checks. */\n\n"
        + type_info + "\n" + root_obj + "\n" + animal_struct + "\n"
        + dog_struct + "\n" + cat_struct + "\n\n" + dog_metadata + "\n"
        + cat_metadata + "\n\n" + dog_init + "\n" + cat_init + "\n\n"
        + display_check + "\n\n" + identify_decl + "\n\n" + identify_def + "\n"
    )
    failure_excerpt = (
        "/* Nim 2.2.10 failed-cast generated C and runtime helper. */\n\n"
        + force_decl + "\n\n" + force_def + "\n\n" + raise_def + "\n"
    )
    env = (
        "recorded_utc=" + datetime.now(timezone.utc).isoformat() + "\n"
        + run("sw_vers") + "machine=" + run("uname", "-m") + nim_version
        + run("clang", "--version").splitlines()[0] + "\nselected_target=" + target + "\n"
        + "memory_manager=orc\nbuild_mode=debug\nthreads=on\nobject_checks=default_on\n"
    )
    if args.record:
        artifacts = {
            "generated-c-excerpt.c": normal_excerpt,
            "failed-cast-c-excerpt.c": failure_excerpt,
            "toolchain-definition-excerpt.nim": definitions,
            "run-2026-09-11.txt": normal_info + normal + "exit=0\n\n"
                + fail_info + failed.stdout + clean(failed.stderr)
                + f"exit={failed.returncode}\n",
            "environment.txt": env,
            "commands-2026-09-11.txt": "\n".join(logs),
        }
        for name, content in artifacts.items():
            (ROOT / "observed" / name).write_text(clean(content))

    print(f"target={target}")
    print(NORMAL_EXPECTED, end="")
    print(f"failedCastExit={failed.returncode} defect=ObjectConversionDefect")
    print("Nim object metadata, type checks, valid casts, and invalid-cast failure verified")


if __name__ == "__main__":
    main()
