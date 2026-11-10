import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import textwrap
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from learner_workspace import LessonWorkspace


class LearnerWorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.env = {"WANDB_ENTITY": "class", "WANDB_PROJECT": "private-labs", "WANDB_API_KEY": "secret-for-test",
                    "WANDB_NOTEBOOK_COLLECTION": "lesson-one", "WANDB_NOTEBOOK_USER_ID": "12", "WANDB_NOTEBOOK_SESSION_ID": "123"}
        self.w = LessonWorkspace("a" * 40, "project-01", self.env, self.temp.name)

    def seed(self, project="project-01", variants=None, passed_check=True):
        self.w.project = project
        tasks = self.w.root / "forge/tasks"
        tasks.mkdir(parents=True, exist_ok=True)
        (tasks / (project + ".json")).write_text(json.dumps({"variants": variants or ["minimal", "explicit"]}))
        self.w.results.mkdir(parents=True, exist_ok=True)
        (self.w.results / "budget.json").write_text(json.dumps({"limitUsd": 20, "spentEstimateUsd": 1, "reservations": {}, "settled": {}}))
        self.w.state["prepared"] = True
        self.w.connected = True
        self.w.write()
        if passed_check:
            (self.w.results / "qualification-seed").mkdir(exist_ok=True)
            (self.w.results / "qualification-seed" / "qualification.json").write_text(json.dumps({"id": "seed", "finishedAt": "2026-11-09T17:00:00Z", "passed": True}))

    def test_construct_and_view_do_not_call_network_or_process(self):
        with patch("urllib.request.urlopen", side_effect=AssertionError), patch("subprocess.Popen", side_effect=AssertionError):
            w = LessonWorkspace("a" * 40, "project-01", self.env, self.temp.name)
            self.assertEqual(w.view()["status"], "Not launched")
            self.assertFalse(w.base.exists())

    def test_embedded_progress_save_is_valid_python(self):
        # Marimo embeds the entire helper two function levels deep. Exercise
        # that representation, which differs from importing the helper module.
        source = (Path(__file__).resolve().parents[1] / "scripts/learner_workspace.py").read_text()
        namespace = {}
        exec("def cell():\n    def load():\n" + textwrap.indent(source, "        ") +
             "\n        return LessonWorkspace\n    return load()\n", namespace)
        self.w = namespace["cell"]()("a" * 40, "project-01", self.env, self.temp.name)
        self.seed()
        def save_process(args, **kwargs):
            compile(args[2], "<isolated-progress-save>", "exec")
            self.assertNotIn("WANDB_SERVICE", kwargs["env"])
            return SimpleNamespace(returncode=0, stdout='{"progressUrl":"https://wandb.ai/test"}', stderr="")
        self.w.env["WANDB_SERVICE"] = "stale-service-handle"
        with patch("subprocess.run", side_effect=save_process):
            self.w.persist()
        self.assertEqual(self.w.state["progressUrl"], "https://wandb.ai/test")

    def test_identity_isolated_by_owner_notebook_and_destination(self):
        for key in ["WANDB_PROJECT", "WANDB_NOTEBOOK_COLLECTION", "WANDB_NOTEBOOK_USER_ID"]:
            other = LessonWorkspace("a" * 40, "project-01", {**self.env, key: "other"}, self.temp.name)
            self.assertNotEqual(self.w.key, other.key)

    def test_launch_requires_prepare(self):
        with patch("subprocess.Popen", side_effect=AssertionError):
            with self.assertRaisesRegex(RuntimeError, "Prepare"):
                self.w.start("run", "minimal")

    def test_live_work_requires_session_only_sandbox_key(self):
        self.seed()
        self.w.connected = False
        with patch("subprocess.Popen", side_effect=AssertionError):
            with self.assertRaisesRegex(RuntimeError, "Connect"):
                self.w.start("qualify", "minimal")

    def test_failed_prelaunch_save_prevents_paid_process(self):
        self.seed()
        with patch.object(self.w, "persist", side_effect=RuntimeError("offline")), patch("subprocess.Popen", side_effect=AssertionError):
            with self.assertRaisesRegex(RuntimeError, "offline"):
                self.w.start("run", "minimal")
        self.assertIn("pending", self.w.state)

    def test_pending_launch_cannot_be_replayed(self):
        self.seed()
        self.w.state["pending"] = {"id": "uncertain"}
        with patch("subprocess.Popen", side_effect=AssertionError):
            with self.assertRaisesRegex(RuntimeError, "interrupted"):
                self.w.start("run", "minimal")

    def test_unknown_usage_blocks_further_paid_launches(self):
        self.seed()
        (self.w.results / "budget.json").write_text(json.dumps({"limitUsd": 20, "halted": "Missing usage", "reservations": {}}))
        with self.assertRaisesRegex(RuntimeError, "uncertain"):
            self.w.start("run", "minimal")

    def test_exact_source_and_bounded_repeats(self):
        self.seed()
        command = self.w.command("run", "explicit", 3)
        self.assertEqual(command[command.index("--source") + 1], "a" * 40)
        for variant, repeats in [("solution", 1), ("minimal", 4)]:
            with self.assertRaises(ValueError):
                self.w.command("run", variant, repeats)

    def test_graph_requires_explicit_digest_and_actor(self):
        self.seed("project-08", ["graph"])
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            self.w.command("decision", "graph", decision="approve")
        command = self.w.command("decision", "graph", decision="reject", sha256="b" * 64)
        self.assertEqual(command[command.index("--actor") + 1], "12")
        self.assertNotIn("--execute", command)

    def test_loop_checkpoint_cannot_be_overwritten(self):
        self.seed("project-07", ["goal"])
        (self.w.results / "project-07-goal-checkpoint.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "already run"):
            self.w.command("run", "goal")
        command = self.w.command("resume", "goal")
        self.assertIn("--resume", command)
        self.assertEqual(command[command.index("--duration-seconds") + 1], "600")

    def test_checkpoint_roundtrip_retains_budget_and_pending(self):
        self.seed()
        self.w.state["pending"] = {"id": "do-not-retry"}
        self.w.write()
        data = self.w.bundle()
        with tempfile.TemporaryDirectory() as dest:
            other = LessonWorkspace("a" * 40, "project-01", self.env, dest)
            other.restore_bundle(data)
            self.assertEqual(other.ledger()["spentEstimateUsd"], 1)
            self.assertEqual(other.state["pending"]["id"], "do-not-retry")

    def test_restore_rejects_other_owner(self):
        self.seed()
        other = LessonWorkspace("a" * 40, "project-01", {**self.env, "WANDB_NOTEBOOK_USER_ID": "13"}, self.temp.name)
        with self.assertRaisesRegex(RuntimeError, "another learner"):
            other.restore_bundle(self.w.bundle())
        self.assertFalse(other.state_file.exists())

    def test_restore_rejects_traversal_before_writing(self):
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
            member = tarfile.TarInfo("results/../../escape")
            member.size = 3
            archive.addfile(member, io.BytesIO(b"bad"))
        with self.assertRaisesRegex(RuntimeError, "Unsafe"):
            self.w.restore_bundle(buffer.getvalue())

    def test_no_credential_in_exported_checkpoint(self):
        self.seed()
        (self.w.results / "action.log").write_text("error secret-for-test")
        with tarfile.open(fileobj=io.BytesIO(self.w.bundle()), mode="r:gz") as archive:
            for member in archive.getmembers():
                self.assertNotIn(b"secret-for-test", archive.extractfile(member).read())

    def test_prepare_keeps_saved_budget_on_interruption(self):
        self.seed()
        self.w.state["pending"] = {"id": "uncertain"}
        self.w.write()
        with patch.object(self.w, "private_project"), patch.object(self.w, "install_tools", side_effect=AssertionError):
            with self.assertRaisesRegex(RuntimeError, "interrupted"):
                self.w.prepare(20)
        self.assertEqual(self.w.ledger()["spentEstimateUsd"], 1)

    def test_blank_worksheet_never_erases_saved_notes(self):
        # A fresh runtime shows an empty worksheet; saving must merge, not replace.
        self.seed()
        with patch.object(self.w, "persist"):
            self.w.save_notes("It will skip the launch check", "", "", "")
            self.w.save_notes("", "Passed four of five checks", "  ", "25")
        self.assertEqual(self.w.state["notes"], {"prediction": "It will skip the launch check",
                                                 "observation": "Passed four of five checks", "observedHumanMinutes": "25"})

    def test_interrupted_copy_says_so_and_asks_for_no_key(self):
        # A restored marker with no live process is an interrupted copy, not a running action.
        self.seed()
        self.w.state["pending"] = {"id": "lost-runtime"}
        self.w.write()
        view = self.w.view()
        self.assertTrue(view["prepared"])
        self.assertFalse(view["active"])
        self.assertIn("interrupted", self.w.blocked())
        for call in (lambda: self.w.start("run", "minimal"), lambda: self.w.connect("a-key"), lambda: self.w.save_notes("p", "o", "l")):
            with patch("subprocess.Popen", side_effect=AssertionError), patch("urllib.request.urlopen", side_effect=AssertionError):
                with self.assertRaisesRegex(RuntimeError, "interrupted"):
                    call()
        with patch.object(self.w, "private_project"), patch.object(self.w, "install_tools", side_effect=AssertionError):
            with self.assertRaisesRegex(RuntimeError, "interrupted"):
                self.w.prepare(20)
        self.assertIn("Stopped", self.w.view()["status"])

    def test_running_child_is_active_until_it_exits(self):
        self.seed()
        self.w.state["pending"] = {"id": "live"}
        self.w.process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        self.addCleanup(self.w.process.kill)
        self.assertTrue(self.w.view()["active"])
        self.assertIn("still running", self.w.blocked())
        self.w.process.kill()
        self.w.process.wait()
        self.assertFalse(self.w.view()["active"])

    def test_only_the_graders_capture_of_a_real_attempt_is_shown(self):
        self.seed()
        trial = "c547bb71-3edb-49cc-a60c-9a727b62c4c5"
        grader = self.w.results / trial / "grader"
        grader.mkdir(parents=True)
        (self.w.results / trial / "trial.json").write_text(json.dumps({"id": trial, "variant": "minimal", "outcome": "passed"}))
        self.assertEqual(self.w.view()["captures"], [])
        (grader / "electron.png").write_bytes(b"window")
        self.assertEqual(self.w.view()["captures"], [trial])
        self.assertEqual(self.w.capture(trial), b"window")
        (grader / "visible-answer.png").write_bytes(b"answer")
        self.assertEqual(self.w.capture(trial), b"answer")
        self.w.project = "project-06"  # the reset lesson is about the window at the end of the check
        self.assertEqual(self.w.capture(trial), b"window")
        self.w.project = "project-01"
        # The id check, not a missing file, must be what refuses a path outside results.
        escaped = self.w.results.parent / trial / "grader"
        escaped.mkdir(parents=True)
        (escaped / "electron.png").write_bytes(b"outside")
        self.assertIsNone(self.w.capture("../" + trial))
        (grader / "visible-answer.png").unlink()
        (grader / "electron.png").unlink()
        (grader / "electron.png").symlink_to(escaped / "electron.png")
        self.assertIsNone(self.w.capture(trial))
        (grader / "electron.png").unlink()
        (grader / "electron.png").write_bytes(b"x" * 5_000_001)
        self.assertIsNone(self.w.capture(trial))

    def test_latest_access_check_is_last(self):
        self.seed()
        # Finish order differs from name order in both directions.
        for name, finished in [("c", "2026-11-09T19:00:00Z"), ("a", "2026-11-09T20:00:00Z"), ("b", "2026-11-09T18:00:00Z")]:
            folder = self.w.results / ("qualification-" + name)
            folder.mkdir()
            (folder / "qualification.json").write_text(json.dumps({"id": name, "finishedAt": finished, "passed": name == "a"}))
        self.assertEqual([q["id"] for q in self.w.view()["qualifications"]], ["seed", "b", "c", "a"])

    def test_run_waits_for_a_passing_access_check(self):
        self.seed(passed_check=False)
        with patch.object(self.w, "persist", side_effect=AssertionError), patch("subprocess.Popen", side_effect=AssertionError):
            with self.assertRaisesRegex(RuntimeError, "Check that everything works"):
                self.w.start("run", "minimal")
        self.assertNotIn("pending", self.w.state)

    def test_remote_failure_never_becomes_empty_budget(self):
        with patch.object(self.w, "private_project"), patch.object(self.w, "restore_remote", side_effect=RuntimeError("network failed")):
            with self.assertRaisesRegex(RuntimeError, "network failed"):
                self.w.prepare(20)
        self.assertFalse((self.w.results / "budget.json").exists())


if __name__ == "__main__":
    unittest.main()
