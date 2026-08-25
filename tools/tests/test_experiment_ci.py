from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).parents[1] / "experiment_ci.py"
SPEC = importlib.util.spec_from_file_location("experiment_ci", MODULE_PATH)
assert SPEC and SPEC.loader
experiment_ci = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(experiment_ci)


def automated_manifest(experiment_id: str) -> dict:
    return {
        "$schema": "../../schemas/experiment-manifest.schema.json",
        "schema_version": 1,
        "id": experiment_id,
        "issue": 1,
        "artifacts": [{"path": "README.md", "kind": "file"}],
        "ci": {
            "mode": "automated",
            "os": "ubuntu-latest",
            "toolchain": {"kind": "python", "version": "3.13"},
            "steps": [{"name": "smoke", "argv": ["python3", "-c", "print('ok')"], "stdout_contains": ["ok"]}],
        },
    }


class ManifestTests(unittest.TestCase):
    def test_generated_only_directory_is_not_an_experiment(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            experiment = root / "experiments" / "001-generated" / "observed" / "bin"
            experiment.mkdir(parents=True)
            (experiment / "output").write_text("generated", encoding="utf-8")
            with self.assertRaisesRegex(experiment_ci.ManifestError, "no experiments found"):
                experiment_ci.load_manifests(root)

    def test_unregistered_source_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "experiments" / "001-unregistered" / "src"
            source.mkdir(parents=True)
            (source / "main.py").write_text("print('test')", encoding="utf-8")
            with self.assertRaisesRegex(experiment_ci.ManifestError, "README.md is required"):
                experiment_ci.load_manifests(root)

    def test_id_must_match_directory(self):
        with self.assertRaisesRegex(experiment_ci.ManifestError, "id must match"):
            experiment_ci.validate_manifest(automated_manifest("001-one"), "002-two")

    def test_artifact_cannot_escape_experiment(self):
        manifest = automated_manifest("001-one")
        manifest["artifacts"][0]["path"] = "../secret"
        with self.assertRaisesRegex(experiment_ci.ManifestError, "stay inside"):
            experiment_ci.validate_manifest(manifest, "001-one")

    def test_unknown_step_key_is_rejected(self):
        manifest = automated_manifest("001-one")
        manifest["ci"]["steps"][0]["shell"] = True
        with self.assertRaisesRegex(experiment_ci.ManifestError, "unknown keys"):
            experiment_ci.validate_manifest(manifest, "001-one")

    def test_shared_runner_change_selects_every_automated_experiment(self):
        manifests = {
            "001-one": automated_manifest("001-one"),
            "002-two": {"ci": {"mode": "manual"}},
            "003-three": automated_manifest("003-three"),
        }
        selected = experiment_ci.select_experiments(manifests, ["tools/experiment_ci.py"])
        self.assertEqual(selected, ["001-one", "003-three"])

    def test_changed_experiment_selects_only_itself(self):
        manifests = {
            "001-one": automated_manifest("001-one"),
            "003-three": automated_manifest("003-three"),
        }
        selected = experiment_ci.select_experiments(manifests, ["experiments/003-three/src/main.py"])
        self.assertEqual(selected, ["003-three"])

    def test_runner_checks_stdout_and_artifacts(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            experiment = root / "experiments" / "001-one"
            experiment.mkdir(parents=True)
            (experiment / "README.md").write_text("test", encoding="utf-8")
            manifest = automated_manifest("001-one")
            experiment_ci.run_experiment(root, "001-one", manifest)


if __name__ == "__main__":
    unittest.main()
