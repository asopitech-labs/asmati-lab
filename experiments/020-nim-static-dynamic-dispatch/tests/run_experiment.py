"""Build static/dynamic dispatch evidence; --record saves sanitized observations."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import re
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = "static=105\ndynamic=12\n"


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


def declaration_name(text: str, source_name: str, argument_type: str) -> str:
    declaration = require(
        rf"N_LIB_PRIVATE N_NOINLINE\(NI, {source_name}__[A-Za-z0-9_]+\)"
        rf"\({re.escape(argument_type)}\* [a-z]+_p0\);",
        text,
    )
    return re.search(rf"({source_name}__[A-Za-z0-9_]+)", declaration).group(1)  # type: ignore[union-attr]


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

    dump = subprocess.run(
        ["nim", "dump", "--verbosity:0", "src/static_dynamic_dispatch.nim"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    for line in (dump.stdout + "\n" + dump.stderr).splitlines():
        candidate = Path(line.strip())
        if (candidate / "system.nim").is_file():
            nim_lib = candidate.resolve()
            break
    if nim_lib is None:
        raise RuntimeError("Nim library source not found in search paths")

    (ROOT / "observed/bin").mkdir(parents=True, exist_ok=True)
    (ROOT / "observed/nimcache").mkdir(parents=True, exist_ok=True)
    run(
        "nim", "c", "--forceBuild:on", "--cc:clang", f"--cpu:{cpu}",
        f"--passC:-arch {arch}", f"--passL:-arch {arch}", "--mm:orc",
        "--nimcache:observed/nimcache", "--out:observed/bin/static_dynamic_dispatch",
        "src/static_dynamic_dispatch.nim",
    )

    generated = (ROOT / "observed/nimcache/@mstatic_dynamic_dispatch.nim.c").read_text()
    type_info = require(
        r"struct TNimTypeV2 \{\s*void\* destructor;\s*NI size;\s*NI16 align;\s*"
        r"NI16 depth;\s*NU32\* display;[\s\S]*?void\* vTable\[SEQ_DECL_SIZE\];\s*\};",
        generated,
    )
    root_obj = require(r"struct RootObj \{\s*TNimTypeV2\* m_type;\s*\};", generated)
    animal_match = re.search(
        r"struct (tyObject_AnimalcolonObjectType__[A-Za-z0-9_]+) \{\s*RootObj Sup;\s*NI id;\s*\};",
        generated,
    )
    if not animal_match:
        raise AssertionError("missing Animal struct")
    animal_type = animal_match.group(1)
    animal_struct = animal_match.group(0)
    dog_match = re.search(
        rf"struct (tyObject_DogcolonObjectType__[A-Za-z0-9_]+) \{{\s*"
        rf"{re.escape(animal_type)} Sup;\s*NI bonus;\s*\}};",
        generated,
    )
    if not dog_match:
        raise AssertionError("missing Dog struct")
    dog_type = dog_match.group(1)
    dog_struct = dog_match.group(0)

    static_name = declaration_name(generated, "staticScore", animal_type)
    static_def = function_at(generated, static_name + ")(")
    static_call_name = declaration_name(generated, "callStatic", animal_type)
    static_call = function_at(generated, static_call_name + ")(")
    require(rf"result = {re.escape(static_name)}\(animal_p0\);", static_call)

    dynamic_declarations = re.findall(
        r"N_LIB_PRIVATE N_NOINLINE\(NI, (dynamicScore__[A-Za-z0-9_]+)\)\(([^)]+)\);",
        generated,
    )
    if len(dynamic_declarations) != 3:
        raise AssertionError(f"expected 3 dynamicScore functions, got {len(dynamic_declarations)}")
    dynamic_functions = {name: function_at(generated, name + ")(") for name, _ in dynamic_declarations}
    derived_name = next(
        name for name, argument in dynamic_declarations if dog_type in argument
    )
    animal_names = [name for name, argument in dynamic_declarations if animal_type in argument]
    dispatcher_name = next(name for name in animal_names if "isObjDisplayCheck" in dynamic_functions[name])
    base_name = next(name for name in animal_names if name != dispatcher_name)
    dispatcher = dynamic_functions[dispatcher_name]
    base_def = dynamic_functions[base_name]
    derived_def = dynamic_functions[derived_name]

    dynamic_call_name = declaration_name(generated, "callDynamic", animal_type)
    dynamic_call = function_at(generated, dynamic_call_name + ")(")
    require(rf"result = {re.escape(dispatcher_name)}\(animal_p0\);", dynamic_call)
    require(r"chckNilDisp\(animal_p0\);", dispatcher)
    require(r"\(\*animal_p0\)\.Sup\.m_type", dispatcher)
    dog_check = require(r"isObjDisplayCheck\([^\n]+, 2, [0-9]+\)", dispatcher)
    animal_check = require(r"isObjDisplayCheck\([^\n]+, 1, [0-9]+\)", dispatcher)
    dog_token = re.search(r", 2, ([0-9]+)\)", dog_check).group(1)  # type: ignore[union-attr]
    animal_token = re.search(r", 1, ([0-9]+)\)", animal_check).group(1)  # type: ignore[union-attr]
    require(rf"result = {re.escape(derived_name)}\(\(\({re.escape(dog_type)}\*\)", dispatcher)
    require(rf"result = {re.escape(base_name)}\(animal_p0\);", dispatcher)

    descriptor = require(
        rf"N_LIB_PRIVATE TNimTypeV2 [A-Za-z0-9_]+ = \{{\.destructor = [\s\S]{{0,220}}?"
        rf"\.size = sizeof\({re.escape(dog_type)}\), [\s\S]{{0,260}}?\.depth = 2, "
        r"\.display = [A-Za-z0-9_]+,[\s\S]{0,220}?\};",
        generated,
    )
    require(rf"\{{[0-9]+, {animal_token}, {dog_token}\}};", generated)
    if ".vTable" in descriptor:
        raise AssertionError("Dog descriptor unexpectedly initializes vTable")
    if generated.count("vTable") != 1:
        raise AssertionError("generated unit unexpectedly reads or writes vTable")

    display_check = function_at(generated, "isObjDisplayCheck)(")
    require(r"targetDepth_p1 <= \(\*source_p0\)\.depth", display_check)
    require(r"\(\*source_p0\)\.display\[targetDepth_p1\] == token_p2", display_check)

    output = run("observed/bin/static_dynamic_dispatch")
    if output != EXPECTED:
        raise AssertionError(f"unexpected output: {output}")
    binary_info = run("file", "observed/bin/static_dynamic_dispatch")
    require(r"static_dynamic_dispatch: Mach-O 64-bit executable " + arch, binary_info)

    system_source = (nim_lib / "system.nim").read_text()
    arc_source = (nim_lib / "system/arc.nim").read_text()
    metadata_source = require(
        r"when not defined\(js\) and defined\(nimV2\):\n  type\n[\s\S]*?"
        r"    TNimTypeV2 \{\.compilerproc\.\} = object\n"
        r"[\s\S]*?    PNimTypeV2 = ptr TNimTypeV2",
        system_source,
    )
    display_source = require(
        r"proc isObjDisplayCheck\(source: PNimTypeV2, targetDepth: int16, token: uint32\): bool "
        r"\{\.compilerRtl, inl\.\} =\n"
        r"  result = targetDepth <= source\.depth and source\.display\[targetDepth\] == token",
        arc_source,
    )
    definitions = (
        "# Nim 2.2.10 lib/system.nim and system/arc.nim. Selected definitions only.\n\n"
        + metadata_source + "\n\n" + display_source + "\n"
    )
    if not args.record:
        saved = (ROOT / "observed/toolchain-definition-excerpt.nim").read_text()
        if definitions != saved:
            raise AssertionError("saved toolchain definitions differ from Nim 2.2.10")

    excerpt = (
        "/* Nim 2.2.10 generated C. Selected static and dynamic dispatch evidence. */\n\n"
        + type_info + "\n" + root_obj + "\n" + animal_struct + "\n" + dog_struct + "\n\n"
        + descriptor + "\n\n" + display_check + "\n\n"
        + static_def + "\n\n" + base_def + "\n\n" + derived_def + "\n\n"
        + static_call + "\n\n" + dynamic_call + "\n\n" + dispatcher + "\n"
    )
    table = (
        "# 呼び出し先選択表\n\n"
        "| Nim呼び出し | 生成Cの入口 | 選択条件 | 呼び出し先 | 実行値 |\n"
        "| --- | --- | --- | --- | ---: |\n"
        f"| `callStatic(Animal)` | `{static_name}` | 静的に確定 | 基底型用proc | 105 |\n"
        f"| `callDynamic(Animal)` | `{dispatcher_name}` | depth 2 / token `{dog_token}` | Dog用method | 12 |\n"
        f"| dispatcher fallback | `{dispatcher_name}` | depth 1 / token `{animal_token}` | Animal用base method | 今回は未実行 |\n\n"
        "今回の生成単位では`TNimTypeV2`に`vTable`欄があるが、Dog descriptorはその欄を明示初期化せず、"
        "生成単位内にslotの設定・参照もない。呼び出し先選択は`isObjDisplayCheck`を並べたdispatcherで行われた。\n"
    )
    env = (
        "recorded_utc=" + datetime.now(timezone.utc).isoformat() + "\n"
        + run("sw_vers") + "machine=" + run("uname", "-m") + nim_version
        + run("clang", "--version").splitlines()[0] + "\nselected_target=" + target + "\n"
        + "memory_manager=orc\nbuild_mode=debug\nthreads=on\ndispatch=default_methods\n"
    )
    if args.record:
        artifacts = {
            "generated-c-excerpt.c": excerpt,
            "toolchain-definition-excerpt.nim": definitions,
            "dispatch-table.md": table,
            "run-2026-09-12.txt": binary_info + output + "exit=0\n",
            "environment.txt": env,
            "commands-2026-09-12.txt": "\n".join(logs),
        }
        for name, content in artifacts.items():
            (ROOT / "observed" / name).write_text(clean(content))

    print(f"target={target}")
    print(EXPECTED, end="")
    print("static direct call, method dispatcher, type checks, and vTable non-use verified")


if __name__ == "__main__":
    main()
