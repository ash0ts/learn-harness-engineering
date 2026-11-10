import contextlib
import ast
import base64
import hashlib
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

sys.path.append(str(Path(__file__).resolve().parents[1] / "scripts"))
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
            return SimpleNamespace(returncode=0, stdout=json.dumps({"progressUrl":"https://wandb.ai/test", "verified": True, "sha256": args[-1]}), stderr="")
        self.w.env["WANDB_SERVICE"] = "stale-service-handle"
        with patch("subprocess.run", side_effect=save_process):
            self.w.persist()
        self.assertTrue(self.w.state["progressUrl"].endswith("/runs/lesson-" + self.w.key))
        self.assertIsInstance(self.w.cached_checkpoint_bytes(), bytes)

    def test_identity_isolated_by_owner_notebook_and_destination(self):
        for key in ["WANDB_PROJECT", "WANDB_NOTEBOOK_COLLECTION", "WANDB_NOTEBOOK_USER_ID"]:
            other = LessonWorkspace("a" * 40, "project-01", {**self.env, key: "other"}, self.temp.name)
            self.assertNotEqual(self.w.key, other.key)

    def test_save_before_runner_install_retains_operations_and_withholds_download(self):
        self.seed()
        operations = self.w.results / "operations"
        operations.mkdir()
        (operations / "previous.json").write_text(json.dumps({"evidence": {}}))
        def save_process(args, **kwargs):
            return SimpleNamespace(returncode=0, stdout=json.dumps({"verified": True, "sha256": args[-1]}), stderr="")
        with patch("subprocess.run", side_effect=save_process):
            self.w.persist()
        self.assertTrue((self.w.base / "save-receipt.json").exists())
        self.assertEqual(self.w.ledger()["spentEstimateUsd"], 1)
        self.assertTrue((operations / "previous.json").exists())
        self.assertIsNone(self.w.cached_checkpoint_bytes())
        # The same unvalidated record must still be refused after installation.
        (self.w.root / "forge/operation.schema.json").write_text((Path(__file__).resolve().parents[1] / "operation.schema.json").read_text())
        with self.assertRaises(RuntimeError):
            self.w.operation_records()

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
        (self.w.results / "project-08-graph-checkpoint.json").write_text(json.dumps({"id": "graph-one", "node": "approval"}))
        command = self.w.command("decision", "graph", decision="reject", sha256="b" * 64)
        self.assertEqual(command[command.index("--actor") + 1], "12")
        self.assertNotIn("--execute", command)

    def test_repeat_loop_uses_fresh_checkpoint_and_retains_previous(self):
        self.seed("project-07", ["goal"])
        original = self.w.results / "project-07-goal-checkpoint.json"
        original.write_text(json.dumps({"id": "old", "status": "finished", "deadlineAt": 123}))
        first = self.w.command("run", "goal")
        second = self.w.command("run", "goal")
        self.assertNotEqual(first[first.index("--checkpoint") + 1], second[second.index("--checkpoint") + 1])
        self.assertEqual(json.loads(original.read_text())["deadlineAt"], 123)
        resumed = self.w.command("resume", "goal")
        self.assertIn("--resume", resumed)
        self.assertEqual(resumed[resumed.index("--duration-seconds") + 1], "600")

    def test_pending_approval_prevents_new_graph(self):
        self.seed("project-08", ["graph"])
        (self.w.results / "project-08-graph-checkpoint.json").write_text('{"node":"approval"}')
        with self.assertRaisesRegex(ValueError, "decide"):
            self.w.command("run", "graph")

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

    def test_prepare_restores_pending_and_installs_recovery_tools(self):
        self.seed()
        self.w.state["pending"] = {"id": "uncertain"}
        self.w.write()
        self.w.root.mkdir(parents=True, exist_ok=True)
        (self.w.root / ".git").mkdir()
        (self.w.root / "projects/shared").mkdir(parents=True)
        with patch.object(self.w, "private_project"), patch.object(self.w, "persist"), patch.object(self.w, "install_tools") as install, patch.object(self.w, "run_command", return_value="a" * 40), patch("subprocess.run", return_value=SimpleNamespace(returncode=0)):
            self.w.prepare(20)
        install.assert_called_once()
        self.assertEqual(self.w.state["pending"]["id"], "uncertain")
        self.assertAlmostEqual(self.w.ledger()["spentEstimateUsd"], 1 + self.w.NOTEBOOK_ALLOWANCE)
        self.assertIn("Connect", self.w.state["status"])

    def test_completed_worker_has_a_separate_thirty_second_finalization_bound(self):
        self.seed()
        operation = self.w.results / "operations/done.json"
        operation.parent.mkdir()
        operation.write_text(json.dumps({"phase": "completed"}))
        def waiting(**kwargs):
            raise subprocess.TimeoutExpired(["node", "course"], kwargs["timeout"])
        with patch("time.monotonic", side_effect=[0, 1, 32]):
            with self.assertRaises(subprocess.TimeoutExpired):
                self.w.wait_for_worker(SimpleNamespace(wait=waiting), "done")
        self.assertEqual(self.w.wait_for_worker(SimpleNamespace(wait=lambda **kwargs: 0), "done"), 0)

    def test_blank_worksheet_never_erases_saved_notes(self):
        # A fresh runtime shows an empty worksheet; saving must merge, not replace.
        self.seed()
        with patch.object(self.w, "persist"):
            self.w.save_notes("It will skip the launch check", "", "", "")
            self.w.save_notes("", "Passed four of five checks", "  ", "25")
        self.assertEqual(self.w.state["notes"], {"prediction": "It will skip the launch check",
                                                 "observation": "Passed four of five checks", "observedHumanMinutes": "25"})

    def test_interrupted_copy_can_authenticate_for_readback_only(self):
        self.seed()
        self.w.state["pending"] = {"id": "lost-runtime"}
        self.w.write()
        with patch("subprocess.Popen", side_effect=AssertionError):
            with self.assertRaisesRegex(RuntimeError, "interrupted"):
                self.w.start("run", "minimal")
        viewer = base64.b64encode(b"User:12").decode()
        with patch.object(self.w, "private_project"), patch.object(self.w, "query", return_value={"data":{"viewer":{"id":viewer}}}), patch.object(self.w, "run_command"), patch.object(self.w, "recover") as recovery:
            self.w.connect("learner-key")
        recovery.assert_called_once()
        self.assertTrue(self.w.connected)

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

    def test_bundle_is_deterministic_sanitized_and_restores_disconnected(self):
        self.seed()
        self.w.state["notes"] = {"observation": "Retained notes"}
        self.w.write()
        (self.w.results / "old.log").write_text("/Users/student/private secret-for-test")
        data = self.w.bundle()
        self.assertEqual(data, self.w.bundle())
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
            text = archive.extractfile("results/old.log").read()
            self.assertNotIn(b"/Users/", text)
            self.assertNotIn(b"secret-for-test", text)
        with tempfile.TemporaryDirectory() as dest:
            other = LessonWorkspace("b" * 40, "project-01", self.env, dest)
            other.restore_bundle(data)
            self.assertFalse(other.connected)
            self.assertEqual(other.state["notes"], self.w.state["notes"])
            self.assertEqual(other.ledger(), self.w.ledger())
            self.assertNotIn("runners", str(other.results))
            self.assertEqual(other.state["migrations"][-1]["fromRevision"], "a" * 40)

    def test_manifest_tamper_and_symlink_ancestors_are_rejected(self):
        self.seed()
        buffer = io.BytesIO()
        with tarfile.open(fileobj=io.BytesIO(self.w.bundle()), mode="r:gz") as source, tarfile.open(fileobj=buffer, mode="w:gz") as target:
            for member in source.getmembers():
                data = source.extractfile(member).read()
                if member.name == "results/budget.json":
                    data = data.replace(b'"spentEstimateUsd": 1', b'"spentEstimateUsd": 0')
                member.size = len(data)
                target.addfile(member, io.BytesIO(data))
        with self.assertRaisesRegex(RuntimeError, "checksum"):
            self.w.restore_bundle(buffer.getvalue())
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        (self.w.results / "link").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(RuntimeError, "symlink"):
            self.w.bundle()

    def test_native_download_is_only_cached_after_verified_save(self):
        self.seed()
        self.assertIsNone(self.w.cached_checkpoint_bytes())
        def save(args, **kwargs):
            return SimpleNamespace(returncode=0, stdout=json.dumps({"verified": True, "sha256": args[-1]}), stderr="")
        with patch("subprocess.run", side_effect=save):
            self.w.persist()
        data = self.w.cached_checkpoint_bytes()
        self.assertIsInstance(data, bytes)
        self.w.state["pending"] = {"id":"pending"}
        self.assertIsNone(self.w.cached_checkpoint_bytes())
        self.w.state.pop("pending")
        with patch("subprocess.run", return_value=SimpleNamespace(returncode=1, stdout="", stderr="network")):
            with self.assertRaisesRegex(RuntimeError, "upload failed"):
                self.w.persist()
        self.assertIsNone(self.w.cached_checkpoint_bytes())

    def test_download_reacts_to_progress_and_completed_save(self):
        from learner_cells import DOWNLOAD, PERSIST
        # Marimo infers dependencies from reads, not the function signature;
        # an unused progress argument gets removed by its formatter.
        tree = ast.parse(DOWNLOAD)
        reads = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
        self.assertTrue({"my_progress", "get_checkpoint_epoch"} <= reads)
        namespace = {}
        exec(PERSIST, namespace)
        epochs = []
        ui = SimpleNamespace(value="note")
        mo = SimpleNamespace(stop=lambda value: None, md=lambda value: value, callout=lambda value, **kw: value)
        learner = SimpleNamespace(save_notes=lambda *args: None, redact=str)
        args = (lambda: 0, learner, SimpleNamespace(value=1), ui, ui, mo, ui, ui, epochs.append, lambda value: None)
        namespace["_"](*args)
        self.assertEqual(epochs[0](7), 8)
        epochs.clear()
        def failed_save(*args):
            raise RuntimeError("publication failed")
        learner.save_notes = failed_save
        namespace["_"](*args)
        self.assertEqual(epochs, [])

    def test_unknown_recovery_never_clears_pending(self):
        self.seed()
        self.w.state["pending"] = {"id":"unknown"}
        report = {"operations":[{"id":"unknown", "phase":"blocked_unknown"}]}
        with patch.object(self.w, "run_command", side_effect=[json.dumps(report), json.dumps({"id":"unknown", "recovered":False})]), patch.object(self.w, "persist"), patch("subprocess.Popen", side_effect=AssertionError):
            result = self.w.recover()
        self.assertFalse(result["recovered"])
        self.assertIn("pending", self.w.state)
        self.assertEqual(self.w.ledger()["spentEstimateUsd"], 1)

    def test_completed_publication_recovery_does_not_launch_agent(self):
        self.seed()
        self.w.state["pending"] = {"id":"done", "operationIds":["done"], "publicationRetry":True}
        report = {"operations":[{"id":"done", "phase":"recoverable"}]}
        with patch.object(self.w, "run_command", side_effect=[json.dumps(report), json.dumps({"id":"done", "recovered":True})]) as command, patch.object(self.w, "persist"), patch("subprocess.Popen", side_effect=AssertionError):
            result = self.w.recover()
        self.assertTrue(result["recovered"])
        self.assertNotIn("pending", self.w.state)
        self.assertIn("--publish", command.call_args.args[0])
        self.assertEqual(self.w.ledger()["spentEstimateUsd"], 1)

    def test_v1_migration_preserves_unresolved_revision_and_reservations(self):
        self.seed()
        self.w.state.update(schemaVersion=1, pending={"id":"old-operation"})
        self.w.write()
        budget = {"schemaVersion":1,"limitUsd":20,"spentEstimateUsd":3.2,"reservations":{"old-operation":2},"settled":{"old-trial":3.2},"halted":"Missing usage for old-operation"}
        (self.w.results / "budget.json").write_text(json.dumps(budget))
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
            for name, data in [("learner.json", self.w.state_file.read_bytes()), ("results/budget.json", json.dumps(budget).encode())]:
                member = tarfile.TarInfo(name); member.size=len(data); archive.addfile(member,io.BytesIO(data))
        with tempfile.TemporaryDirectory() as dest:
            other = LessonWorkspace("b"*40, "project-01", self.env, dest)
            other.restore_bundle(buffer.getvalue())
            self.assertEqual(other.ledger(), budget)
            self.assertEqual(other.state["pending"]["revision"], "a"*40)
            self.assertEqual(other.state["schemaVersion"], 2)
            self.assertIsNone(other.cached_checkpoint_bytes())

    def test_python_and_typescript_use_the_same_operation_contract(self):
        self.seed()
        source = Path(__file__).resolve().parents[1] / "operation.schema.json"
        target = self.w.root / "forge/operation.schema.json"
        target.write_bytes(source.read_bytes())
        operation = {"schemaVersion":2,"id":"operation-one","kind":"qualification","sourceCommit":"a"*40,"protocolSha256":"b"*64,
            "identity":{"entity":"class","project":"private-labs","owner":"12","notebook":"lesson-one"},"phase":"completed",
            "cleanup":"verified","telemetry":"complete","publication":"not_required","createdAt":"now","updatedAt":"now",
            "sandboxIds":[],"reservationIds":[],"requests":{"agent-1":{"status":"reported","payloadBytes":10,"inputTokens":1,"outputTokens":2}},"evidence":{},"events":[]}
        folder=self.w.results/"operations";folder.mkdir()
        path=folder/"operation-one.json";path.write_text(json.dumps(operation))
        self.assertEqual(self.w.incomplete_operations(), [])
        operation["requests"]["agent-1"]["inputTokens"]=-1;path.write_text(json.dumps(operation))
        with self.assertRaisesRegex(RuntimeError, "constraint"):
            self.w.operation_records()

    def test_first_private_save_handles_absent_artifact_type(self):
        self.seed()
        uploaded=[]
        remote=SimpleNamespace(qualified_name='class/private-labs/learner:v0',get_entry=lambda name:SimpleNamespace(download=lambda root:str(self.w.base/'checkpoint.tar.gz')))
        class Run:
            url='https://wandb.ai/class/private-labs/runs/lesson'
            summary={}
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def log_artifact(self,artifact,aliases):
                uploaded.append(artifact)
                return SimpleNamespace(wait=lambda:remote)
        fake=SimpleNamespace(Api=lambda **kwargs:object(),init=lambda **kwargs:Run(),Settings=lambda **kwargs:kwargs,
            Artifact=lambda *args,**kwargs:SimpleNamespace(add_file=lambda *args,**kwargs:None))
        def child(args,**kwargs):
            output=io.StringIO()
            response={'data':{'project':{'access':'PRIVATE','artifactType':None}}}
            with patch.dict(sys.modules,{'wandb':fake}),patch.object(sys,'argv',args[2:]),patch.dict('os.environ',{'WANDB_API_KEY':'test-only'}),patch('urllib.request.urlopen',return_value=io.BytesIO(json.dumps(response).encode())),contextlib.redirect_stdout(output):
                exec(args[2],{})
            return SimpleNamespace(returncode=0,stdout=output.getvalue(),stderr='')
        with patch('subprocess.run',side_effect=child):self.w.persist()
        self.assertEqual(len(uploaded),1)
        self.assertIsInstance(self.w.cached_checkpoint_bytes(),bytes)


if __name__ == "__main__":
    unittest.main()
