import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
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

    def seed(self, project="project-01", variants=None):
        self.w.project = project
        tasks = self.w.root / "forge/tasks"
        tasks.mkdir(parents=True, exist_ok=True)
        (tasks / (project + ".json")).write_text(json.dumps({"variants": variants or ["minimal", "explicit"]}))
        self.w.results.mkdir(parents=True, exist_ok=True)
        (self.w.results / "budget.json").write_text(json.dumps({"limitUsd": 20, "spentEstimateUsd": 1, "reservations": {}, "settled": {}}))
        self.w.state["prepared"] = True
        self.w.connected = True
        self.w.write()

    def test_construct_and_view_do_not_call_network_or_process(self):
        with patch("urllib.request.urlopen", side_effect=AssertionError), patch("subprocess.Popen", side_effect=AssertionError):
            w = LessonWorkspace("a" * 40, "project-01", self.env, self.temp.name)
            self.assertEqual(w.view()["status"], "Not launched")
            self.assertFalse(w.base.exists())

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
            with self.assertRaisesRegex(RuntimeError, "finish"):
                self.w.start("run", "minimal")

    def test_unknown_usage_blocks_further_paid_launches(self):
        self.seed()
        (self.w.results / "budget.json").write_text(json.dumps({"limitUsd": 20, "halted": "Missing usage", "reservations": {}}))
        with self.assertRaisesRegex(RuntimeError, "reconciliation"):
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
        with self.assertRaisesRegex(ValueError, "already exists"):
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

    def test_remote_failure_never_becomes_empty_budget(self):
        with patch.object(self.w, "private_project"), patch.object(self.w, "restore_remote", side_effect=RuntimeError("network failed")):
            with self.assertRaisesRegex(RuntimeError, "network failed"):
                self.w.prepare(20)
        self.assertFalse((self.w.results / "budget.json").exists())


if __name__ == "__main__":
    unittest.main()
