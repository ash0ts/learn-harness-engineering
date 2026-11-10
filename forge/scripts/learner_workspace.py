"""Per-learner notebook coordinator. Embedded as a native Python cell at generation.

Import and construction perform no network calls or paid work. Prepare and every
paid action are explicit. Remote state is written before a launch; an interrupted
launch cannot silently restart in a new notebook runtime.
"""
import base64
import gzip
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
import uuid
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
        self.root = self.base / "runners" / revision
        self.results = self.base / "evidence"
        self.state_file = self.base / "learner.json"
        self.artifact_name = "learner-" + self.key
        self.state = {"schemaVersion": 2, "identity": self.identity, "revision": revision,
                      "status": "Not launched", "actions": [], "notes": {}}
        self.env.update(FORGE_RESULTS_DIR=str(self.results), FORGE_BUDGET_MODE="incremental",
                        FORGE_NOTEBOOK_OWNER=self.identity["WANDB_NOTEBOOK_USER_ID"],
                        FORGE_NOTEBOOK_ID=self.identity["WANDB_NOTEBOOK_COLLECTION"])
        self._cached_checkpoint = None
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

    def safe_path(self, root, name):
        parts = name.split("/")
        if not name or any(p in ("", ".", "..") for p in parts) or "\\" in name or ":" in name:
            raise RuntimeError("Unsafe checkpoint entry")
        path = Path(root)
        if path.is_symlink():
            raise RuntimeError("Checkpoint root cannot be a symlink")
        for part in parts:
            path = path / part
            if path.is_symlink():
                raise RuntimeError("Checkpoint cannot contain symlinks")
        return path

    def projection(self, data):
        text = self.redact(data)
        # Display/export projections never replace the protected local originals.
        text = text.replace(str(self.results) + "/", "")
        text = re.sub(r"/(?:Users|home)/[^/\s\"']+", "[home]", text)
        text = re.sub(r"(?i)(authorization[\"' :]+(?:bearer|basic)\s+)[A-Za-z0-9_./+=-]+", r"\1[REDACTED]", text)
        return text

    def load_state(self, state):
        if state.get("identity") != self.identity:
            raise RuntimeError("Checkpoint belongs to another learner, notebook, or destination")
        if state.get("schemaVersion") not in (1, 2):
            raise RuntimeError("Unsupported progress version")
        old = state.get("revision")
        if state.get("pending"):
            state["pending"].setdefault("revision", old)
        if old != self.revision or state["schemaVersion"] == 1:
            state.setdefault("migrations", []).append({"fromSchema": state["schemaVersion"], "fromRevision": old,
                "toRevision": self.revision, "at": time.time(), "reason": "Explicitly updated notebook source; spending and outcomes retained"})
        state.update(schemaVersion=2, revision=self.revision)
        self.state = state

    def bundle(self):
        files = {"learner.json": self.state_file.read_bytes()}
        if self.results.exists():
            for path in sorted(self.results.rglob("*")):
                name = path.relative_to(self.results).as_posix()
                self.safe_path(self.results, name)
                if path.is_file():
                    files["results/" + name] = path.read_bytes()
                elif path.name.endswith((".lock", "-lock")):
                    raise RuntimeError("A checkpoint writer is still active")
        if sum(map(len, files.values())) > 200_000_000:
            raise RuntimeError("Checkpoint exceeds 200 MB; ask the instructor to archive evidence")
        originals = {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}
        for name, data in list(files.items()):
            try:
                files[name] = self.projection(data.decode()).encode()
            except UnicodeDecodeError:
                if any(secret and secret.encode() in data for secret in self.secrets):
                    raise RuntimeError("Credential detected in binary evidence")
        # References in a sanitized projection point at the projected bytes. Keep
        # original hashes in the manifest for comparison with private artifacts.
        for name, data in list(files.items()):
            if name.startswith("results/operations/") and name.endswith(".json"):
                op = json.loads(data)
                for ref in op.get("evidence", {}).values():
                    target = "results/" + ref["path"]
                    if target in files:
                        ref["sha256"] = hashlib.sha256(files[target]).hexdigest()
                files[name] = json.dumps(op, indent=2).encode()
        manifest = {"schemaVersion": 2, "projection": "sanitized checkpoint; original evidence remains in private artifacts",
                    "files": {name: {"sha256": hashlib.sha256(data).hexdigest(), "originalSha256": originals[name]} for name, data in files.items()}}
        files["manifest.json"] = json.dumps(manifest, sort_keys=True).encode()
        buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode="wb", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as archive:
                for name, data in sorted(files.items()):
                    info = tarfile.TarInfo(name)
                    info.size, info.mode = len(data), 0o600
                    archive.addfile(info, io.BytesIO(data))
        return buffer.getvalue()

    def restore_bundle(self, data):
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
            members = archive.getmembers()
            if sum(m.size for m in members) > 200_000_000:
                raise RuntimeError("Checkpoint is too large")
            files = {}
            for member in members:
                self.safe_path(self.base, member.name)
                if not member.isfile() or member.name in files or not (member.name in ("learner.json", "manifest.json") or member.name.startswith("results/")):
                    raise RuntimeError("Unsafe checkpoint entry")
                files[member.name] = archive.extractfile(member).read()
        state = json.loads(files["learner.json"])
        if state.get("identity") != self.identity:
            raise RuntimeError("Checkpoint belongs to another learner, notebook, or destination")
        manifest = json.loads(files.pop("manifest.json")) if "manifest.json" in files else None
        if manifest:
            if manifest.get("schemaVersion") != 2 or set(manifest["files"]) != set(files):
                raise RuntimeError("Checkpoint manifest does not cover every file")
            for name, value in files.items():
                if hashlib.sha256(value).hexdigest() != manifest["files"][name]["sha256"]:
                    raise RuntimeError("Checkpoint checksum mismatch")
        elif state.get("schemaVersion") != 1:
            raise RuntimeError("Checkpoint manifest missing")
        # Validate all destination ancestors before making the first write.
        destinations = {name: self.state_file if name == "learner.json" else self.safe_path(self.results, name.removeprefix("results/")) for name in files}
        self.safe_path(self.base, "learner.json")
        for name, dest in destinations.items():
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(files[name])
        self.load_state(state)
        self.connected = False
        self._cached_checkpoint = None
        self.write()

    def operation_records(self):
        schema_file = self.root / "forge/operation.schema.json"
        schema = json.loads(schema_file.read_text()) if schema_file.exists() else None
        rows = []
        for path in sorted((self.results / "operations").glob("*.json")):
            self.safe_path(self.results, path.relative_to(self.results).as_posix())
            row = json.loads(path.read_text())
            if not schema:
                raise RuntimeError("Runner operation contract is missing")
            def validate(rule, value):
                if "const" in rule and value != rule["const"] or "enum" in rule and value not in rule["enum"]:
                    raise RuntimeError("Unsupported operation state")
                kind = rule.get("type")
                types = {"object": dict, "array": list, "string": str, "integer": int}
                if kind in types and (not isinstance(value, types[kind]) or kind == "integer" and isinstance(value, bool)):
                    raise RuntimeError("Invalid operation value")
                if "minimum" in rule and value < rule["minimum"] or "pattern" in rule and not re.search(rule["pattern"], value):
                    raise RuntimeError("Invalid operation constraint")
                if kind == "object":
                    if any(key not in value for key in rule.get("required", [])):
                        raise RuntimeError("Operation is incomplete; retain its reservation")
                    for key, item in value.items():
                        nested = rule.get("properties", {}).get(key, rule.get("additionalProperties"))
                        if isinstance(nested, dict):
                            validate(nested, item)
                if "items" in rule:
                    for item in value:
                        validate(rule["items"], item)
            validate(schema, row)
            if any(r["status"] == "reported" and ("inputTokens" not in r or "outputTokens" not in r) for r in row["requests"].values()):
                raise RuntimeError("Reported usage requires both token counts")
            identity = row["identity"]
            if identity.get("entity") != self.identity["WANDB_ENTITY"] or identity.get("project") != self.identity["WANDB_PROJECT"] or identity.get("owner") != self.identity["WANDB_NOTEBOOK_USER_ID"] or identity.get("notebook") != self.identity["WANDB_NOTEBOOK_COLLECTION"]:
                raise RuntimeError("Operation owner or destination mismatch")
            for ref in row["evidence"].values():
                target = self.safe_path(self.results, ref["path"])
                if hashlib.sha256(target.read_bytes()).hexdigest() != ref["sha256"]:
                    raise RuntimeError("Operation evidence checksum mismatch")
            rows.append(row)
        return rows

    def incomplete_operations(self):
        return [r for r in self.operation_records() if r["phase"] != "completed" or r["cleanup"] != "verified" or r["telemetry"] != "complete" or r["publication"] not in ("verified", "not_required")]

    def cached_checkpoint_bytes(self):
        if self.state.get("pending") or self.process and self.process.poll() is None or self.ledger().get("halted") or self.ledger().get("reservations"):
            return None
        if self._cached_checkpoint and self.incomplete_operations():
            return None
        return self._cached_checkpoint

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
        self._cached_checkpoint = None
        self.state["progressUrl"] = f"https://wandb.ai/{self.identity['WANDB_ENTITY']}/{self.identity['WANDB_PROJECT']}/runs/lesson-{self.key}"
        self.write()
        data = self.bundle()
        digest = hashlib.sha256(data).hexdigest()
        checkpoint = self.base / "checkpoint.tar.gz"
        checkpoint.write_bytes(data)
        # Stable content aliases recover an interrupted save without a new agent
        # attempt. A network failure during read-back never means "not found".
        script = '''
import base64,hashlib,json,os,sys,urllib.request,wandb
from pathlib import Path
base=Path(sys.argv[1]); key=sys.argv[2]; digest=sys.argv[3]
state=json.loads((base/'learner.json').read_text()); identity=state['identity']
ledger=json.loads((base/'evidence/budget.json').read_text()); api=wandb.Api(timeout=30)
entity=identity['WANDB_ENTITY']; project=identity['WANDB_PROJECT']; name='learner-'+key
query='query($e:String!,$p:String!,$n:String!){project(entityName:$e,name:$p){access artifactType(name:"course-learner-state"){artifactCollection(name:$n){id}}}}'
body={'query':query,'variables':{'e':entity,'p':project,'n':name}}
auth=base64.b64encode(('api:'+os.environ['WANDB_API_KEY']).encode()).decode()
request=urllib.request.Request('https://api.wandb.ai/graphql',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','Authorization':'Basic '+auth})
with urllib.request.urlopen(request,timeout=30) as response: result=json.load(response)
project_value=result.get('data',{}).get('project')
if result.get('errors') or not project_value or project_value.get('access')!='PRIVATE' or 'artifactType' not in project_value: raise RuntimeError('Cannot verify private saved progress; no new artifact was created')
typ=project_value['artifactType']
if typ is not None and 'artifactCollection' not in typ: raise RuntimeError('Saved progress response is incomplete')
collection=typ and typ['artifactCollection'];existing=None
if collection:
 for item in api.artifact_versions('course-learner-state',entity+'/'+project+'/'+name):
  if item.metadata.get('checkpointSha256') == digest: existing=item; break
with wandb.init(entity=entity,project=project,id='lesson-'+key,resume='allow',job_type='course-learner-progress',group='self-service-lessons',settings=wandb.Settings(disable_git=True,disable_code=True,silent=True)) as run:
 if existing is None:
  artifact=wandb.Artifact(name,type='course-learner-state',metadata={'revision':state['revision'],'pending':bool(state.get('pending')),'checkpointSha256':digest})
  artifact.add_file(str(base/'checkpoint.tar.gz'),name='checkpoint.tar.gz')
  existing=run.log_artifact(artifact,aliases=['latest','sha-'+digest[:24]]).wait()
 else:
  if 'latest' not in existing.aliases: existing.aliases.append('latest'); existing.save()
 run.summary.update({'lesson_status':state['status'],'completed_actions':len(state['actions']),'spent_estimate_usd':ledger.get('spentEstimateUsd',0),'budget_usd':ledger.get('limitUsd')})
 downloaded=Path(existing.get_entry('checkpoint.tar.gz').download(root=str(base/'verify-save'))).read_bytes()
 if hashlib.sha256(downloaded).hexdigest()!=digest: raise RuntimeError('Saved checkpoint checksum mismatch')
 print(json.dumps({'progressUrl':run.url,'verified':True,'sha256':digest,'artifact':existing.qualified_name}))
'''
        env = {k: v for k, v in self.env.items() if k not in {"WANDB_SERVICE", "_WANDB_SERVICE"}}
        result = subprocess.run([sys.executable, "-c", textwrap.dedent(script), str(self.base), self.key, digest], env=env, capture_output=True, text=True, timeout=180)
        if result.returncode:
            raise RuntimeError("Progress upload failed: " + self.redact(result.stderr[-2500:]))
        receipt = json.loads(result.stdout.strip().splitlines()[-1])
        if receipt.get("verified") is not True or receipt.get("sha256") != digest:
            raise RuntimeError("Progress upload has no verified receipt")
        (self.base / "save-receipt.json").write_text(json.dumps(receipt))
        if not self.state.get("pending") and not self.ledger().get("halted") and not self.ledger().get("reservations") and not self.incomplete_operations():
            self._cached_checkpoint = data

    def cli(self):
        return ["node", "--import", str(self.root / "forge/node_modules/tsx/dist/loader.mjs"), str(self.root / "forge/src/cli.ts")]

    def recover(self):
        """Only inspect, settle verified receipts, and retry missing publication."""
        if self.process and self.process.poll() is None:
            return {"recovered": False, "reason": "Worker is still active"}
        report = json.loads(self.run_command(self.cli() + ["recovery-report", "--output", str(self.results)], cwd=self.root))
        results = []
        pending = self.state.get("pending")
        for operation in report["operations"]:
            if operation["phase"] == "completed":
                continue
            try:
                text = self.run_command(self.cli() + ["recover", "--operation", operation["id"], "--output", str(self.results), "--publish"], cwd=self.root, timeout=360)
                results.append(json.loads(text))
            except Exception as error:
                results.append({"id": operation["id"], "recovered": False, "reason": self.redact(error)})
        self.state["recovery"] = {"at": time.time(), "results": results}
        ledger = self.ledger()
        blocked = ledger.get("halted") or ledger.get("reservations") or any(not r.get("recovered") for r in results)
        if pending and not blocked:
            ids = pending.get("operationIds", [pending["id"]])
            operations = {row["id"]: row for row in report["operations"]}
            # An action saved before Popen is provably not launched. Once the
            # launch boundary is crossed, absence of an operation is ambiguous.
            accounted = pending.get("launchStatus") == "not_created" or all(i in operations for i in ids[:pending.get("nextIndex", 0) + 1])
            if accounted:
                self.state.setdefault("actions", []).append({**pending, "recoveredAt": time.time(), "event": "recovered_without_replacement_work"})
                self.state.pop("pending", None)
            else:
                blocked = "Legacy or interrupted launch has no operation receipt; instructor reconciliation required"
        self.state["status"] = "Recovery needs evidence: " + str(blocked) if blocked else "Workspace ready; recovered saved work"
        self.persist()
        return {"recovered": not bool(blocked), "results": results}

    def blocked(self):
        """Why nothing new can start in this copy, or None."""
        if not self.state.get("prepared"):
            return "Prepare your workspace first (step 2)."
        if self.state.get("pending"):
            if self.process and self.process.poll() is None:
                return "An action is still running. Wait until My work shows it has finished."
            return "An earlier action was interrupted. Prepare and Connect to inspect its saved work; no replacement work starts automatically."
        return None

    def connect(self, api_key):
        """Accept only a masked, session-memory credential; never save it."""
        with self.lock:
            if not self.state.get("prepared"):
                raise RuntimeError("Prepare your workspace first (step 2).")
            if self.process and self.process.poll() is None:
                raise RuntimeError("An action is still running")
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
                script = "import {createSandboxClient} from '@coreweave/cwsandbox/wandb'; const c=createSandboxClient({apiKey:process.env.WANDB_API_KEY,entity:process.env.WANDB_ENTITY,project:process.env.WANDB_PROJECT}); await c.listAll({tags:['course-access-check'],timeoutMs:30000}); await c.transport.clients.client._transport.close(); console.log('Sandbox access checked');"
                self.run_command(["node", "--input-type=module", "-e", script], cwd=self.root / "forge", timeout=45)
            except Exception:
                self.env["WANDB_API_KEY"] = previous
                self.connected = False
                raise
            self.connected = True
            if self.state.get("pending") or self.ledger().get("halted") or self.ledger().get("reservations"):
                self.recover()
        return "Sandbox access connected for this session. The key is held in memory only. " + self.state["status"]

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
        if self.process and self.process.poll() is None:
            return self.view()
        if not isinstance(limit, (float, int)) or not 5 <= limit <= 50:
            raise ValueError("Choose a budget between $5 and $50")
        self.private_project()
        self.base.mkdir(parents=True, exist_ok=True)
        if self.state_file.exists():
            self.load_state(json.loads(self.state_file.read_text()))
        else:
            self.restore_remote()
        legacy = self.base / "course/forge/local-results"
        if legacy.exists() and not self.results.exists():
            if legacy.is_symlink():
                raise RuntimeError("Legacy evidence root cannot be a symlink")
            shutil.copytree(legacy, self.results, symlinks=True)
            self.state.setdefault("migrations", []).append({"event": "copied_v1_evidence", "originalRetained": True})
        existing = self.ledger()
        if existing and existing.get("limitUsd") != limit:
            raise RuntimeError(f"This copy already has a ${existing.get('limitUsd')} budget. Keep that value when resuming.")
        self.results.mkdir(parents=True, exist_ok=True)
        ledger = existing or {"schemaVersion": 1, "limitUsd": limit, "spentEstimateUsd": 0, "reservations": {}, "settled": {}}
        session = "notebook-" + self.env.get("WANDB_NOTEBOOK_SESSION_ID", "")
        if session == "notebook-":
            raise RuntimeError("Forge did not supply a notebook session identity")
        if session not in ledger["settled"]:
            if ledger["spentEstimateUsd"] + sum(ledger["reservations"].values()) + self.NOTEBOOK_ALLOWANCE > limit:
                raise RuntimeError("Budget exhausted before notebook runtime allowance")
            ledger["settled"][session] = self.NOTEBOOK_ALLOWANCE
            ledger["spentEstimateUsd"] += self.NOTEBOOK_ALLOWANCE
        ledger_file = self.results / "budget.json"
        lock = self.results / "budget.json.lock"
        lock.mkdir()  # Same exclusion protocol as TypeScript; never steal a lock.
        try:
            temporary = ledger_file.with_suffix(".tmp")
            temporary.write_text(json.dumps(ledger, indent=2))
            temporary.replace(ledger_file)
        finally:
            lock.rmdir()
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
        self.state.update(status="Workspace ready; Connect to inspect unfinished work" if self.state.get("pending") or existing.get("halted") or existing.get("reservations") else "Workspace ready", prepared=True)
        self.persist()
        return self.view()

    def active_checkpoint(self, variant):
        name = self.state.get("checkpoints", {}).get(variant)
        if not name:
            legacy = f"{self.project}-{variant}-checkpoint.json"
            name = legacy if (self.results / legacy).exists() else None
        return self.safe_path(self.results, name) if name else None

    def command(self, action, variant, repeats=1, decision=None, sha256=None, operation_id=None):
        task = "project-01" if self.project == "overview" else self.project
        spec = json.loads((self.root / "forge/tasks" / (task + ".json")).read_text())
        if variant not in spec["variants"] or repeats not in [1, 2, 3]:
            raise ValueError("Choose a listed treatment and one to three repeats")
        prefix = self.cli()
        operation_id = operation_id or str(uuid.uuid4())
        common = ["--output", str(self.results), "--operation-id", operation_id]
        if action == "qualify":
            return prefix + ["doctor", "--qualify", "--execute"] + common
        current = self.active_checkpoint(variant)
        if action == "decision":
            if self.project != "project-08" or decision not in ["approve", "reject"] or not re.fullmatch(r"[a-f0-9]{64}", sha256 or ""):
                raise ValueError("Review the Project 08 candidate and enter its full SHA-256 before deciding")
            if not current:
                raise ValueError("No graph is waiting for a decision")
            return prefix + ["graph", "--checkpoint", str(current), "--output", str(self.results), "--decision", decision,
                             "--actor", self.identity["WANDB_NOTEBOOK_USER_ID"], "--sha256", sha256]
        if action not in ["run", "resume"]:
            raise ValueError("Unknown lesson action")
        if current and task == "project-08" and json.loads(current.read_text()).get("node") == "approval":
            raise ValueError("Review and decide the pending graph candidate before starting another graph")
        if action == "resume":
            if not current:
                raise ValueError("No checkpoint exists to resume")
            checkpoint = current
            previous = json.loads(current.read_text())
            common = ["--output", str(self.results), "--operation-id", previous["id"]]
        else:
            checkpoint = self.results / (self.project + "-" + variant + "-" + operation_id + "-checkpoint.json")
        if task == "project-07":
            args = ["loop", "--mode", variant, "--checkpoint", str(checkpoint), "--duration-seconds", "600", "--max-rounds", "1", "--execute"] + common
        elif task == "project-08":
            args = ["graph", "--checkpoint", str(checkpoint), "--execute"] + common
        else:
            if action == "resume":
                raise ValueError("Projects 01 to 06 always start a fresh attempt; choose the run action")
            args = ["compare", "--project", task, "--variant", variant, "--repeats", str(repeats), "--source", self.revision, "--execute", "--output", str(self.results)]
            if repeats == 1:
                args += ["--operation-id", operation_id]
        if task in ["project-07", "project-08"] and action == "resume":
            args.append("--resume")
        return prefix + args

    def start(self, action, variant, repeats=1, decision=None, sha256=None):
        with self.lock:
            if self.blocked():
                raise RuntimeError(self.blocked())
            if action != "decision" and not self.connected:
                raise RuntimeError("Connect your sandbox access first (step 3). It has to be done again in every new notebook session.")
            ledger = self.ledger()
            if action != "decision" and (ledger.get("halted") or ledger.get("reservations")):
                raise RuntimeError("The cost or cleanup of an earlier action is uncertain. Prepare and Connect to inspect its evidence.")
            if action in ("run", "resume") and not any(q.get("passed") for q in self.view()["qualifications"]):
                raise RuntimeError("Choose Check that everything works first, and wait for it to pass.")
            count = repeats if action == "run" and self.project not in ["project-07", "project-08"] else 1
            ids = [("qualification-" if action == "qualify" else "") + str(uuid.uuid4()) for _ in range(count)]
            commands = [self.command(action, variant, 1, decision, sha256, i) for i in ids]
            if action == "qualify":
                task = "project-01" if self.project == "overview" else self.project
                for kind in ("baseline", "reference", "regression"):
                    control_id = "control-" + task + "-" + kind + "-" + str(uuid.uuid4())
                    ids.append(control_id)
                    commands.append(self.cli() + ["controls", "--project", task, "--kind", kind, "--source", self.revision,
                        "--output", str(self.results), "--operation-id", control_id, "--execute"])
            self.env["FORGE_BUDGET_USD"] = str(ledger["limitUsd"])
            self.state.update(status="Starting " + action, pending={"id": ids[0], "operationIds": ids, "action": action,
                "variant": variant, "revision": self.revision, "session": self.env.get("WANDB_NOTEBOOK_SESSION_ID"),
                "nextIndex": 0, "launchStatus": "not_created"})
            self._cached_checkpoint = None
            if "--checkpoint" in commands[0] and action != "decision":
                self.state.setdefault("checkpoints", {})[variant] = Path(commands[0][commands[0].index("--checkpoint") + 1]).relative_to(self.results).as_posix()
            self.persist()
            self.launch(commands, 0)
        return self.view()

    def launch(self, commands, index):
        pending = self.state["pending"]
        pending.update(nextIndex=index, launchStatus="launching")
        self.persist()  # A lost runtime at this boundary requires inspection.
        log_path = self.results / ("lesson-action-" + pending["operationIds"][index] + ".log")
        try:
            with log_path.open("w") as log:
                child_env = {k: v for k, v in self.env.items() if k not in {"WANDB_SERVICE", "_WANDB_SERVICE"}}
                self.process = subprocess.Popen(commands[index], cwd=self.root, env=child_env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        except Exception:
            pending["launchStatus"] = "not_created"
            self.write()
            raise
        pending.update(launchStatus="started", pid=self.process.pid)
        self.state["status"] = "Running " + pending["action"]
        self.write()
        threading.Thread(target=self.finish, args=(self.process, commands, index, log_path), daemon=True).start()

    def finish(self, process, commands, index, log_path):
        forced = False
        try:
            try:
                code = process.wait(timeout=3000)
            except subprocess.TimeoutExpired:
                forced = True
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    code = process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    code = process.wait(timeout=10)
            with self.lock:
                pending = self.state["pending"]
                record = {**pending, "exitCode": code, "forced": forced}
                self.state["actions"].append(record)
                log_path.write_text(self.redact(log_path.read_text(errors="replace")))
                ledger = self.ledger()
                if forced or ledger.get("halted") or ledger.get("reservations") or self.incomplete_operations():
                    self.state["status"] = "Action stopped; Connect to inspect accounting, cleanup and publication"
                    self.persist()
                    return
                # Each repeat has its own durable ID. A lost notebook never
                # continues the remaining queue without a new explicit Start.
                if code == 0 and index + 1 < len(commands):
                    self.launch(commands, index + 1)
                    return
                self.state.pop("pending", None)
                self.state["status"] = "Action finished; inspect results" if code == 0 else "Action failed; inspect evidence"
                try:
                    self.persist()
                except Exception:
                    self.state["pending"] = {**pending, "launchStatus": "finished", "publicationRetry": True}
                    raise
        except Exception as error:
            self.state["status"] = "Checkpoint save needs attention: " + self.redact(error)
            self.write()

    def cancel(self):
        with self.lock:
            if self.process and self.process.poll() is None:
                os.killpg(self.process.pid, signal.SIGTERM)
                self.state["status"] = "Cancellation requested; waiting for cleanup and checkpoint"
                self.write()
        return self.view()

    def save_notes(self, prediction, observation, limitation, minutes=""):
        with self.lock:
            if self.blocked():
                raise RuntimeError(self.blocked())
            # A fresh runtime shows an empty worksheet. An empty field must not
            # erase the prediction or notes saved in an earlier session.
            notes = dict(self.state.get("notes") or {})
            entries = {"prediction": prediction, "observation": observation, "limitation": limitation, "observedHumanMinutes": minutes}
            for name, value in entries.items():
                if str(value or "").strip():
                    notes[name] = str(value).strip()
            self.state["notes"] = notes
            self.persist()

    def capture_path(self, trial_id):
        """Locate the protected grader's own screenshot of a learner attempt."""
        if not re.fullmatch(r"[a-f0-9-]{36}", str(trial_id)):
            return None
        names = ("electron.png", "visible-answer.png") if self.project in ("project-05", "project-06") else ("visible-answer.png", "electron.png")
        for name in names:
            path = self.results / str(trial_id) / "grader" / name
            if path.is_file() and not path.is_symlink() and path.stat().st_size <= 5_000_000:
                return path
        return None

    def capture(self, trial_id):
        path = self.capture_path(trial_id)
        return path.read_bytes() if path else None

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
        controls = []
        for path in self.results.glob("control-*/control.json") if self.results.exists() else []:
            controls.append(json.loads(path.read_text()))
        qualifications.sort(key=lambda item: str(item.get("finishedAt") or item.get("startedAt") or ""))
        # "active" is a process in this runtime. "pending" can also be a marker
        # restored from a runtime that disappeared; that state must stay downloadable.
        active = bool(self.process and self.process.poll() is None)
        view = {"status": self.state["status"], "destination": "/".join(self.identity[k] for k in ["WANDB_ENTITY", "WANDB_PROJECT"]),
                "prepared": self.state.get("prepared", False), "sandboxConnected": self.connected, "pending": self.state.get("pending"), "revision": self.revision,
                "active": active, "captures": [r["id"] for r in trials if isinstance(r.get("id"), str) and self.capture_path(r["id"])],
                "budget": self.ledger(), "controls": controls, "trials": trials, "checkpoints": checkpoints, "qualifications": qualifications,
                "notes": self.state.get("notes", {}), "progressUrl": self.state.get("progressUrl"),
                "log": self.redact(logs[-1].read_text(errors="replace")[-12000:]) if logs else ""}
        return json.loads(self.projection(json.dumps(view)))
