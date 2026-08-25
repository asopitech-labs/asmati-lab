#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
SHARED_CI_PATHS = (
    ".github/workflows/experiments.yml",
    "schemas/experiment-manifest.schema.json",
    "tools/experiment_ci.py",
    "tools/tests/",
)
ALLOWED_TOP_LEVEL = {"$schema", "schema_version", "id", "issue", "artifacts", "ci"}
ALLOWED_TOOLCHAINS = {"system", "python", "nim"}
ALLOWED_OSES = {"ubuntu-latest", "macos-latest", "windows-latest"}
EXPERIMENT_ID = re.compile(r"^[0-9]{3}-[a-z0-9][a-z0-9-]*$")


class ManifestError(ValueError):
    pass


def _require_keys(value: dict[str, Any], required: set[str], allowed: set[str], where: str) -> None:
    missing = required - value.keys()
    extra = value.keys() - allowed
    if missing:
        raise ManifestError(f"{where}: missing keys: {', '.join(sorted(missing))}")
    if extra:
        raise ManifestError(f"{where}: unknown keys: {', '.join(sorted(extra))}")


def _relative_path(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value:
        raise ManifestError(f"{where}: expected a non-empty path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        raise ManifestError(f"{where}: path must stay inside the experiment: {value}")
    return value


def validate_manifest(data: Any, directory_name: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ManifestError(f"{directory_name}: manifest must be an object")
    _require_keys(
        data,
        {"schema_version", "id", "issue", "artifacts", "ci"},
        ALLOWED_TOP_LEVEL,
        directory_name,
    )
    if data["schema_version"] != 1:
        raise ManifestError(f"{directory_name}: unsupported schema_version")
    if "$schema" in data and (not isinstance(data["$schema"], str) or not data["$schema"]):
        raise ManifestError(f"{directory_name}: $schema must be a non-empty string")
    if not EXPERIMENT_ID.fullmatch(directory_name):
        raise ManifestError(f"{directory_name}: invalid experiment id")
    if data["id"] != directory_name:
        raise ManifestError(f"{directory_name}: id must match its directory")
    if not isinstance(data["issue"], int) or isinstance(data["issue"], bool) or data["issue"] < 1:
        raise ManifestError(f"{directory_name}: issue must be a positive integer")

    artifacts = data["artifacts"]
    if not isinstance(artifacts, list):
        raise ManifestError(f"{directory_name}: artifacts must be an array")
    for index, artifact in enumerate(artifacts):
        where = f"{directory_name}.artifacts[{index}]"
        if not isinstance(artifact, dict):
            raise ManifestError(f"{where}: expected an object")
        _require_keys(artifact, {"path", "kind"}, {"path", "kind"}, where)
        _relative_path(artifact["path"], f"{where}.path")
        if artifact["kind"] not in {"file", "directory"}:
            raise ManifestError(f"{where}.kind: expected file or directory")

    ci = data["ci"]
    if not isinstance(ci, dict):
        raise ManifestError(f"{directory_name}.ci: expected an object")
    mode = ci.get("mode")
    if mode == "manual":
        _require_keys(ci, {"mode", "reason"}, {"mode", "reason"}, f"{directory_name}.ci")
        if not isinstance(ci["reason"], str) or not ci["reason"].strip():
            raise ManifestError(f"{directory_name}.ci.reason: expected a non-empty string")
        return data
    if mode != "automated":
        raise ManifestError(f"{directory_name}.ci.mode: expected automated or manual")

    _require_keys(ci, {"mode", "os", "toolchain", "steps"}, {"mode", "os", "toolchain", "steps"}, f"{directory_name}.ci")
    if ci["os"] not in ALLOWED_OSES:
        raise ManifestError(f"{directory_name}.ci.os: unsupported runner")
    toolchain = ci["toolchain"]
    if not isinstance(toolchain, dict):
        raise ManifestError(f"{directory_name}.ci.toolchain: expected an object")
    _require_keys(toolchain, {"kind", "version"}, {"kind", "version"}, f"{directory_name}.ci.toolchain")
    if toolchain["kind"] not in ALLOWED_TOOLCHAINS:
        raise ManifestError(f"{directory_name}.ci.toolchain.kind: unsupported toolchain")
    if not isinstance(toolchain["version"], str) or not toolchain["version"]:
        raise ManifestError(f"{directory_name}.ci.toolchain.version: expected a non-empty string")

    steps = ci["steps"]
    if not isinstance(steps, list) or not steps:
        raise ManifestError(f"{directory_name}.ci.steps: expected at least one step")
    for index, step in enumerate(steps):
        where = f"{directory_name}.ci.steps[{index}]"
        if not isinstance(step, dict):
            raise ManifestError(f"{where}: expected an object")
        allowed = {"name", "argv", "timeout_seconds", "stdout_contains"}
        _require_keys(step, {"name", "argv"}, allowed, where)
        if not isinstance(step["name"], str) or not step["name"].strip():
            raise ManifestError(f"{where}.name: expected a non-empty string")
        argv = step["argv"]
        if not isinstance(argv, list) or not argv or not all(isinstance(arg, str) and arg for arg in argv):
            raise ManifestError(f"{where}.argv: expected a non-empty string array")
        timeout = step.get("timeout_seconds", 300)
        if not isinstance(timeout, int) or isinstance(timeout, bool) or not 1 <= timeout <= 1800:
            raise ManifestError(f"{where}.timeout_seconds: expected 1..1800")
        expected = step.get("stdout_contains", [])
        if not isinstance(expected, list) or not all(isinstance(item, str) and item for item in expected):
            raise ManifestError(f"{where}.stdout_contains: expected a string array")
    return data


def load_manifests(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    experiments = root / "experiments"
    manifests: dict[str, dict[str, Any]] = {}
    for directory in sorted(path for path in experiments.iterdir() if path.is_dir()):
        readme_path = directory / "README.md"
        manifest_path = directory / "experiment.json"
        if not readme_path.is_file() and not manifest_path.is_file():
            files = [path.relative_to(directory).parts for path in directory.rglob("*") if path.is_file()]
            generated_only = files and all(
                len(parts) >= 3 and parts[0] == "observed" and parts[1] in {"bin", "nimcache"}
                for parts in files
            )
            if generated_only:
                continue
        if not readme_path.is_file():
            raise ManifestError(f"{directory.name}: README.md is required")
        if not manifest_path.is_file():
            raise ManifestError(f"{directory.name}: experiment.json is required")
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ManifestError(f"{directory.name}: cannot read experiment.json: {error}") from error
        manifests[directory.name] = validate_manifest(data, directory.name)
    if not manifests:
        raise ManifestError("no experiments found")
    return manifests


def verify_artifacts(root: Path, experiment_id: str, manifest: dict[str, Any]) -> None:
    experiment = root / "experiments" / experiment_id
    for artifact in manifest["artifacts"]:
        path = experiment / artifact["path"]
        if artifact["kind"] == "file" and not path.is_file():
            raise ManifestError(f"{experiment_id}: missing artifact file: {artifact['path']}")
        if artifact["kind"] == "directory" and not path.is_dir():
            raise ManifestError(f"{experiment_id}: missing artifact directory: {artifact['path']}")


def validate_repository(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    manifests = load_manifests(root)
    for experiment_id, manifest in manifests.items():
        verify_artifacts(root, experiment_id, manifest)
    return manifests


def changed_paths(root: Path, base: str, head: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...{head}"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def select_experiments(manifests: dict[str, dict[str, Any]], paths: list[str]) -> list[str]:
    automated = {name for name, manifest in manifests.items() if manifest["ci"]["mode"] == "automated"}
    if any(path == shared or path.startswith(shared) for path in paths for shared in SHARED_CI_PATHS):
        return sorted(automated)
    selected = {
        parts[1]
        for path in paths
        if len(parts := PurePosixPath(path).parts) >= 2 and parts[0] == "experiments" and parts[1] in automated
    }
    return sorted(selected)


def matrix_for(manifests: dict[str, dict[str, Any]], selected: list[str]) -> dict[str, list[dict[str, str]]]:
    include = []
    for experiment_id in selected:
        ci = manifests[experiment_id]["ci"]
        toolchain = ci["toolchain"]
        include.append(
            {
                "experiment": experiment_id,
                "os": ci["os"],
                "toolchain": toolchain["kind"],
                "toolchain_version": toolchain["version"],
                "python_version": toolchain["version"] if toolchain["kind"] == "python" else "3.13",
            }
        )
    return {"include": include}


def run_experiment(root: Path, experiment_id: str, manifest: dict[str, Any]) -> None:
    ci = manifest["ci"]
    if ci["mode"] != "automated":
        raise ManifestError(f"{experiment_id}: manual experiment cannot be run by CI")
    required_command = {"python": "python3", "nim": "nim"}.get(ci["toolchain"]["kind"])
    if required_command and shutil.which(required_command) is None:
        raise ManifestError(f"{experiment_id}: required command is unavailable: {required_command}")

    cwd = root / "experiments" / experiment_id
    for step in ci["steps"]:
        print(f"::group::{experiment_id}: {step['name']}", flush=True)
        try:
            result = subprocess.run(
                step["argv"],
                cwd=cwd,
                check=False,
                capture_output=True,
                text=True,
                timeout=step.get("timeout_seconds", 300),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )
        except subprocess.TimeoutExpired as error:
            raise ManifestError(f"{experiment_id}: step timed out: {step['name']}") from error
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        print("::endgroup::", flush=True)
        if result.returncode != 0:
            raise ManifestError(f"{experiment_id}: step failed ({result.returncode}): {step['name']}")
        for expected in step.get("stdout_contains", []):
            if expected not in result.stdout:
                raise ManifestError(f"{experiment_id}: missing expected stdout in {step['name']}: {expected!r}")
    verify_artifacts(root, experiment_id, manifest)


def write_github_output(path: Path, matrix: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as output:
        output.write(f"matrix={json.dumps(matrix, separators=(',', ':'))}\n")
        output.write(f"count={len(matrix['include'])}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate, select, and run asmati-lab experiments")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate")

    plan = subparsers.add_parser("plan")
    plan.add_argument("--base", required=True)
    plan.add_argument("--head", required=True)
    plan.add_argument("--github-output", type=Path)

    run = subparsers.add_parser("run")
    run.add_argument("experiment")
    args = parser.parse_args()

    try:
        manifests = validate_repository()
        if args.command == "validate":
            print(f"validated {len(manifests)} experiment manifests")
        elif args.command == "plan":
            selected = select_experiments(manifests, changed_paths(ROOT, args.base, args.head))
            matrix = matrix_for(manifests, selected)
            print(json.dumps(matrix, indent=2))
            if args.github_output:
                write_github_output(args.github_output, matrix)
        elif args.command == "run":
            if args.experiment not in manifests:
                raise ManifestError(f"unknown experiment: {args.experiment}")
            run_experiment(ROOT, args.experiment, manifests[args.experiment])
    except (ManifestError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
