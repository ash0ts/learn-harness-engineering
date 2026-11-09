"""Per-learner notebook coordinator. Embedded as a native Python cell at generation.

Import and construction perform no network calls or paid work. Prepare and every
paid action are explicit. Remote state is written before a launch; an interrupted
launch cannot silently restart in a new notebook runtime.
"""
import base64
import hashlib
import io
import json
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import textwrap
import threading
import time
import urllib.request
from pathlib import Path


class LessonWorkspace:
    REPOSITORY = "https://github.com/ash0ts/learn-harness-engineering.git"
    NODE_VERSION = "22.19.0"
    NODE_SHA = {
        "x86_64": "c0649af18e6a24f6fe5535a3e86b341dd49a8e71117c8b68bde973ef834f16f2",
        "aarch64": "0b2d9f564b6594222a62c82e1df2efe119dd4a4aff29644f4dd325bf360b6bcc",
    }
    # Verified Forge EDIT shape: 2 CPU / 4 GiB, one-hour lifetime. This is a
    # conservative session allowance, not a platform-enforced billing cap.
    NOTEBOOK_ALLOWANCE = 0.3408

    def __init__(self, revision, project, env=None, base=None):
        if not re.fullmatch(r"[a-f0-9]{40}", revision):
            raise ValueError("An exact runner revision is required")
        if project not in ["overview"] + [f"project-{i:02}" for i in range(1, 9)]:
            raise ValueError("Unknown lesson")
        self.env = dict(os.environ if env is None else env)
        self.secrets = {self.env.get("WANDB_API_KEY", "")}
        self.connected = False
        self.revision, self.project = revision, project
        self.identity = {k: self.env.get(k, "") for k in (
            "WANDB_ENTITY", "WANDB_PROJECT", "WANDB_NOTEBOOK_COLLECTION", "WANDB_NOTEBOOK_USER_ID")}
        self.key = hashlib.sha256(json.dumps(self.identity, sort_keys=True).encode()).hexdigest()[:20]
        self.base = Path(base or self.env.get("FORGE_LEARNER_HOME", "/workspace/forge-lessons")) / self.key
        self.root = self.base / "course"
        self.results = self.root / "forge/local-results"
        self.state_file = self.base / "learner.json"
        self.artifact_name = "learner-" + self.key
        self.state = {"schemaVersion": 1, "identity": self.identity, "revision": revision,
                      "status": "Not launched", "actions": [], "notes": {}}
        self.process = None
        self.lock = threading.Lock()

    def redact(self, value):
        text = str(value)
        for secret in self.secrets:
            if secret:
                text = text.replace(secret, "[REDACTED]")
        return text

    def write(self):
        self.base.mkdir(parents=True, exist_ok=True)
        temporary = self.state_file.with_suffix(".tmp")
        temporary.write_text(self.redact(json.dumps(self.state, indent=2)))
        temporary.replace(self.state_file)

    def require_identity(self):
        if not all(self.identity.values()) or not self.env.get("WANDB_API_KEY"):
            raise RuntimeError("Open your own copy in an authenticated Forge Edit session. Its identity and credential must be injected by Forge.")

    def query(self, query, variables):
        self.require_identity()
        payload = {"query": query, "variables": variables}
        auth = base64.b64encode(("api:" + self.env["WANDB_API_KEY"]).encode()).decode()
        req = urllib.request.Request("https://api.wandb.ai/graphql", data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json", "Authorization": "Basic " + auth})
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.load(response)
        if result.get("errors"):
            raise RuntimeError("Forge API request failed: " + self.redact(result["errors"]))
        return result

    def private_project(self):
        result = self.query("query($e:String!,$p:String!){project(entityName:$e,name:$p){access}}",
                            {"e": self.identity["WANDB_ENTITY"], "p": self.identity["WANDB_PROJECT"]})
        if result.get("data", {}).get("project", {}).get("access") != "PRIVATE":
            raise RuntimeError("Copy this lesson to a writable private project before preparing a workspace.")

    def run_command(self, args, cwd=None, timeout=600):
        completed = subprocess.run(args, cwd=cwd, env=self.env, capture_output=True, text=True, timeout=timeout)
        if completed.returncode:
            raise RuntimeError(self.redact("Command failed: " + " ".join(map(str, args)) + "\n" + completed.stderr[-3000:]))
        return completed.stdout

    def install_tools(self):
        if not shutil.which("git", path=self.env.get("PATH")):
            if platform.system() != "Linux" or os.geteuid() != 0 or not shutil.which("apt-get"):
                raise RuntimeError("This runtime needs Git. Use the standard Forge CPU notebook image.")
            self.run_command(["apt-get", "update", "-qq"])
            self.run_command(["apt-get", "install", "-y", "--no-install-recommends", "git", "ca-certificates"])
        node = self.base / "node"
        if not (node / "bin/node").exists():
            arch = platform.machine()
            if platform.system() != "Linux" or arch not in self.NODE_SHA:
                raise RuntimeError("Automatic setup supports Forge Linux x64/arm64 notebooks.")
            name = f"node-v{self.NODE_VERSION}-linux-{'x64' if arch == 'x86_64' else 'arm64'}"
            with urllib.request.urlopen(f"https://nodejs.org/dist/v{self.NODE_VERSION}/{name}.tar.xz", timeout=60) as response:
                data = response.read(60_000_001)
            if len(data) > 60_000_000 or hashlib.sha256(data).hexdigest() != self.NODE_SHA[arch]:
                raise RuntimeError("Node download checksum mismatch")
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:xz") as archive:
                archive.extractall(self.base, filter="data")
            (self.base / name).rename(node)
        self.env["PATH"] = str(node / "bin") + os.pathsep + self.env.get("PATH", "")
        if self.run_command([str(node / "bin/node"), "--version"]).strip() != "v" + self.NODE_VERSION:
            raise RuntimeError("Unexpected Node version")
        if not shutil.which("uv", path=self.env["PATH"]):
            raise RuntimeError("The standard Forge notebook image must include uv")

    def bundle(self):
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
            files = [(self.state_file, "learner.json")]
            if self.results.exists():
                files += [(p, "results/" + str(p.relative_to(self.results))) for p in self.results.rglob("*") if p.is_file()]
            total = 0
            for path, name in files:
                if path.is_symlink():
                    raise RuntimeError("Checkpoint cannot contain symlinks")
                data = path.read_bytes()
                for secret in self.secrets:
                    if secret:
                        data = data.replace(secret.encode(), b"[REDACTED]")
                total += len(data)
                if total > 200_000_000:
                    raise RuntimeError("Checkpoint exceeds 200 MB; download evidence and ask the instructor to archive it")
                info = tarfile.TarInfo(name)
                info.size, info.mode = len(data), 0o600
                archive.addfile(info, io.BytesIO(data))
        return buffer.getvalue()

    def restore_bundle(self, data):
        # Validate the complete archive before writing any entry.
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
            members = archive.getmembers()
            if sum(m.size for m in members) > 200_000_000:
                raise RuntimeError("Checkpoint is too large")
            for member in members:
                path = Path(member.name)
                if not member.isfile() or path.is_absolute() or ".." in path.parts or not (member.name == "learner.json" or member.name.startswith("results/")):
                    raise RuntimeError("Unsafe checkpoint entry")
            state = json.loads(archive.extractfile("learner.json").read())
            if state["identity"] != self.identity or state["revision"] != self.revision:
                raise RuntimeError("Checkpoint belongs to another learner, notebook, destination, or runner revision")
            for member in members:
                dest = self.state_file if member.name == "learner.json" else self.results / member.name.removeprefix("results/")
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(archive.extractfile(member).read())
        self.state = state

    def restore_remote(self):
        import wandb
        name = f"{self.identity['WANDB_ENTITY']}/{self.identity['WANDB_PROJECT']}/{self.artifact_name}:latest"
        api = wandb.Api(timeout=30)
        result = self.query("query($e:String!,$p:String!,$n:String!){project(entityName:$e,name:$p){access artifactType(name:\"course-learner-state\"){artifactCollection(name:$n){id}}}}",
                            {"e": self.identity["WANDB_ENTITY"], "p": self.identity["WANDB_PROJECT"], "n": self.artifact_name})
        project = result.get("data", {}).get("project")
        if not project or project.get("access") != "PRIVATE" or "artifactType" not in project:
            raise RuntimeError("Cannot verify saved progress; no new budget was created")
        artifact_type = project["artifactType"]
        if artifact_type is None or artifact_type.get("artifactCollection") is None:
            return False
        artifact = api.artifact(name, type="course-learner-state")
        path = artifact.get_entry("checkpoint.tar.gz").download(root=str(self.base / "download"))
        self.restore_bundle(Path(path).read_bytes())
        return True

    def persist(self):
        self.write()
        checkpoint = self.base / "checkpoint.tar.gz"
        checkpoint.write_bytes(self.bundle())
        # W&B owns a background service. Give each save its own process so a
        # completed coding child cannot invalidate the notebook's service handle.
        script = '''import json,sys,wandb
from pathlib import Path
base=Path(sys.argv[1]); state=json.loads((base/'learner.json').read_text()); identity=state['identity']
key=sys.argv[2]; ledger=json.loads((base/'course/forge/local-results/budget.json').read_text())
with wandb.init(entity=identity['WANDB_ENTITY'],project=identity['WANDB_PROJECT'],id='lesson-'+key,resume='allow',job_type='course-learner-progress',group='self-service-lessons',settings=wandb.Settings(disable_git=True,disable_code=True,silent=True)) as run:
 artifact=wandb.Artifact('learner-'+key,type='course-learner-state',metadata={'revision':state['revision'],'pending':bool(state.get('pending'))})
 artifact.add_file(str(base/'checkpoint.tar.gz'),name='checkpoint.tar.gz')
 run.log_artifact(artifact,aliases=['latest']).wait()
 run.summary.update({'lesson_status':state['status'],'completed_actions':len(state['actions']),'spent_estimate_usd':ledger.get('spentEstimateUsd',0),'budget_usd':ledger.get('limitUsd')})
 print(json.dumps({'progressUrl':run.url}))
'''
        env = {k: v for k, v in self.env.items() if k not in {"WANDB_SERVICE", "_WANDB_SERVICE"}}
        result = subprocess.run([sys.executable, "-c", textwrap.dedent(script), str(self.base), self.key], env=env, capture_output=True, text=True, timeout=180)
        if result.returncode:
            raise RuntimeError("Progress upload failed: " + self.redact(result.stderr[-2500:]))
        self.state["progressUrl"] = json.loads(result.stdout.strip().splitlines()[-1])["progressUrl"]
        self.write()

    def connect(self, api_key):
        """Accept only a masked, session-memory credential; never save it."""
        with self.lock:
            if not self.state.get("prepared") or self.state.get("pending"):
                raise RuntimeError("Prepare your workspace and finish the current action first")
            if not api_key.strip():
                raise ValueError("A learner-owned Sandbox-capable API key is required")
            previous = self.env.get("WANDB_API_KEY", "")
            self.secrets.add(api_key.strip())
            self.env["WANDB_API_KEY"] = api_key.strip()
            try:
                self.private_project()
                result = self.query("query{viewer{id}}", {})
                viewer_id = result["data"]["viewer"]["id"]
                decoded = base64.b64decode(viewer_id).decode().split(":")[-1]
                if decoded != self.identity["WANDB_NOTEBOOK_USER_ID"]:
                    raise RuntimeError("Use the API key belonging to the owner of this notebook session")
                script = "import {createSandboxClient} from '@coreweave/cwsandbox/wandb'; const c=createSandboxClient({apiKey:process.env.WANDB_API_KEY,entity:process.env.WANDB_ENTITY,project:process.env.WANDB_PROJECT}); await c.listAll({tags:['course-access-check'],timeoutMs:30000}); console.log('Sandbox access checked'); process.exit(0);"
                self.run_command(["node", "--input-type=module", "-e", script], cwd=self.root / "forge", timeout=45)
            except Exception:
                self.env["WANDB_API_KEY"] = previous
                self.connected = False
                raise
            self.connected = True
        return "Sandbox access connected for this session. The key is held in memory only."

    def ledger(self):
        file = self.results / "budget.json"
        return json.loads(file.read_text()) if file.exists() else {}

    def prepare(self, limit=20):
        if not self.lock.acquire(blocking=False):
            raise RuntimeError("Another lesson action is updating this workspace")
        try:
            return self._prepare(limit)
        finally:
            self.lock.release()

    def _prepare(self, limit):
        if not isinstance(limit, (float, int)) or not 5 <= limit <= 50:
            raise ValueError("Choose a budget between $5 and $50")
        self.private_project()
        self.base.mkdir(parents=True, exist_ok=True)
        if self.state_file.exists():
            self.state = json.loads(self.state_file.read_text())
        else:
            self.restore_remote()
        if self.state.get("identity") != self.identity or self.state.get("revision") != self.revision:
            raise RuntimeError("Saved identity or revision differs; keep the original copy for its progress")
        if self.state.get("pending"):
            raise RuntimeError("An earlier action was interrupted. Its paid work may still exist. Download the checkpoint and ask your instructor to reconcile it; setup will not reset your budget.")
        existing = self.ledger()
        if existing and existing.get("limitUsd") != limit:
            raise RuntimeError(f"This copy already has a ${existing.get('limitUsd')} budget. Keep that value when resuming.")
        if existing.get("halted") or existing.get("reservations"):
            raise RuntimeError("The saved ledger needs reconciliation before another launch")
        self.results.mkdir(parents=True, exist_ok=True)
        ledger = existing or {"schemaVersion": 1, "limitUsd": limit, "spentEstimateUsd": 0, "reservations": {}, "settled": {}}
        session = "notebook-" + self.env.get("WANDB_NOTEBOOK_SESSION_ID", "")
        if session == "notebook-":
            raise RuntimeError("Forge did not supply a notebook session identity")
        if session not in ledger["settled"]:
            if ledger["spentEstimateUsd"] + self.NOTEBOOK_ALLOWANCE > limit:
                raise RuntimeError("Budget exhausted before notebook runtime allowance")
            ledger["settled"][session] = self.NOTEBOOK_ALLOWANCE
            ledger["spentEstimateUsd"] += self.NOTEBOOK_ALLOWANCE
        (self.results / "budget.json").write_text(json.dumps(ledger, indent=2))
        self.state["status"] = "Preparing workspace"
        self.persist()  # Save the ledger before installing or launching anything.
        self.install_tools()
        if not (self.root / ".git").exists():
            self.root.mkdir(parents=True, exist_ok=True)
            self.run_command(["git", "init", "-q"], cwd=self.root)
            self.run_command(["git", "remote", "add", "origin", self.REPOSITORY], cwd=self.root)
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.root, env=self.env, capture_output=True, text=True)
        if head.returncode:
            self.run_command(["git", "fetch", "--depth=1", "origin", self.revision], cwd=self.root)
            self.run_command(["git", "checkout", "--detach", "FETCH_HEAD"], cwd=self.root)
        if self.run_command(["git", "rev-parse", "HEAD"], cwd=self.root).strip() != self.revision:
            raise RuntimeError("The runner checkout changed; restore the pinned workspace")
        self.run_command(["npm", "ci", "--prefix", "forge"], cwd=self.root)
        self.run_command(["npm", "run", "build", "--prefix", "forge"], cwd=self.root)
        self.run_command(["npm", "ci", "--ignore-scripts", "--prefix", "forge/sandbox"], cwd=self.root)
        shared_modules = self.root / "projects/shared/node_modules"
        if not shared_modules.exists():
            shared_modules.symlink_to(self.root / "forge/sandbox/node_modules", target_is_directory=True)
        self.run_command([str(self.root / "forge/sandbox/node_modules/.bin/tsc"), "-p", "projects/shared/tsconfig.node.json"], cwd=self.root)
        self.env["FORGE_BUDGET_USD"] = str(limit)
        self.state.update(status="Workspace ready", prepared=True)
        self.persist()
        return self.view()

    def command(self, action, variant, repeats=1, decision=None, sha256=None):
        task = "project-01" if self.project == "overview" else self.project
        spec = json.loads((self.root / "forge/tasks" / (task + ".json")).read_text())
        if variant not in spec["variants"] or repeats not in [1, 2, 3]:
            raise ValueError("Choose a listed treatment and one to three repeats")
        prefix = ["node", "--import", str(self.root / "forge/node_modules/tsx/dist/loader.mjs"), str(self.root / "forge/src/cli.ts")]
        checkpoint = str(self.results / (self.project + "-" + variant + "-checkpoint.json"))
        if action == "qualify":
            return prefix + ["doctor", "--qualify", "--execute"]
        if action == "decision":
            if self.project != "project-08" or decision not in ["approve", "reject"] or not re.fullmatch(r"[a-f0-9]{64}", sha256 or ""):
                raise ValueError("Review the Project 08 candidate and enter its full SHA-256 before deciding")
            return prefix + ["graph", "--checkpoint", checkpoint, "--decision", decision,
                             "--actor", self.identity["WANDB_NOTEBOOK_USER_ID"], "--sha256", sha256]
        if action not in ["run", "resume"]:
            raise ValueError("Unknown lesson action")
        if task == "project-07":
            args = ["loop", "--mode", variant, "--checkpoint", checkpoint, "--duration-seconds", "600", "--max-rounds", "1", "--execute"]
        elif task == "project-08":
            args = ["graph", "--checkpoint", checkpoint, "--execute"]
        else:
            if action == "resume":
                raise ValueError("Projects 01–06 start fresh trials; choose Run exercise")
            args = ["compare", "--project", task, "--variant", variant, "--repeats", str(repeats), "--source", self.revision, "--execute"]
        if task in ["project-07", "project-08"]:
            exists = Path(checkpoint).exists()
            if exists and action != "resume":
                raise ValueError("A checkpoint already exists. Inspect it and choose Resume checkpoint.")
            if action == "resume":
                if not exists:
                    raise ValueError("No checkpoint exists to resume")
                args.append("--resume")
        return prefix + args

    def start(self, action, variant, repeats=1, decision=None, sha256=None):
        with self.lock:
            if not self.state.get("prepared") or self.state.get("pending"):
                raise RuntimeError("Prepare your workspace and finish the current action first")
            if action != "decision" and not self.connected:
                raise RuntimeError("Connect your own sandbox access for this session first")
            ledger = self.ledger()
            if ledger.get("halted") or ledger.get("reservations"):
                raise RuntimeError("Budget or cleanup needs reconciliation; paid launches stopped")
            args = self.command(action, variant, repeats, decision, sha256)
            self.env["FORGE_BUDGET_USD"] = str(ledger["limitUsd"])
            action_id = str(time.time_ns())
            self.state.update(status="Starting " + action, pending={"id": action_id, "action": action, "variant": variant, "session": self.env.get("WANDB_NOTEBOOK_SESSION_ID")})
            self.persist()  # A new runtime sees this marker before any paid child exists.
            log_path = self.results / ("lesson-action-" + action_id + ".log")
            try:
                with log_path.open("w") as log:
                    child_env = {k: v for k, v in self.env.items() if k not in {"WANDB_SERVICE", "_WANDB_SERVICE"}}
                    self.process = subprocess.Popen(args, cwd=self.root, env=child_env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            except Exception:
                self.state.update(status="Launch failed before process creation")
                self.state.pop("pending", None)
                self.persist()
                raise
            self.state["status"] = "Running " + action
            self.write()
            threading.Thread(target=self.finish, args=(self.process, action_id, log_path), daemon=True).start()
        return self.view()

    def finish(self, process, action_id, log_path):
        try:
            try:
                code = process.wait(timeout=3000)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    code = process.wait(timeout=90)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    code = process.wait(timeout=10)
            with self.lock:
                self.state["actions"].append({"id": action_id, **self.state["pending"], "exitCode": code})
                self.state.pop("pending", None)
                self.state["status"] = "Action finished; inspect results" if code == 0 else "Action failed; inspect evidence"
                log_path.write_text(self.redact(log_path.read_text(errors="replace")))
                self.persist()
        except Exception as error:
            # Never erase a pending marker after an uncertain save/cleanup.
            self.state["status"] = "Checkpoint save needs attention: " + self.redact(error)
            self.state["pending"] = {"id": action_id, "action": "reconcile"}
            self.write()

    def cancel(self):
        with self.lock:
            if self.process and self.process.poll() is None:
                os.killpg(self.process.pid, signal.SIGTERM)
                self.state["status"] = "Cancellation requested; waiting for cleanup and checkpoint"
                self.write()
        return self.view()

    def save_notes(self, prediction, observation, limitation):
        with self.lock:
            if self.state.get("pending") or not self.state.get("prepared"):
                raise RuntimeError("Prepare the workspace and wait for the current action to finish before saving notes")
            self.state["notes"] = {"prediction": prediction, "observation": observation, "limitation": limitation}
            self.persist()

    def view(self):
        trials = []
        for path in sorted(self.results.glob("*/trial.json")) if self.results.exists() else []:
            try:
                record = json.loads(path.read_text())
                trials.append(record)
            except (ValueError, OSError):
                continue
        checkpoints = {}
        for path in self.results.glob("*-checkpoint.json") if self.results.exists() else []:
            checkpoints[path.name] = json.loads(path.read_text())
        qualifications = []
        for path in self.results.glob("qualification-*/qualification.json") if self.results.exists() else []:
            qualifications.append(json.loads(path.read_text()))
        logs = sorted(self.results.glob("lesson-action-*.log")) if self.results.exists() else []
        return {"status": self.state["status"], "destination": "/".join(self.identity[k] for k in ["WANDB_ENTITY", "WANDB_PROJECT"]),
                "prepared": self.state.get("prepared", False), "sandboxConnected": self.connected, "pending": self.state.get("pending"), "revision": self.revision,
                "budget": self.ledger(), "trials": trials, "checkpoints": checkpoints, "qualifications": qualifications,
                "notes": self.state.get("notes", {}), "progressUrl": self.state.get("progressUrl"),
                "log": self.redact(logs[-1].read_text(errors="replace")[-12000:]) if logs else ""}
