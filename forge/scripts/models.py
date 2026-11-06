# /// script
# requires-python = ">=3.11"
# dependencies = ["wandb==0.31.0"]
# ///
"""Publish sample-course evidence to an already-private W&B Models project."""
import base64
import json
import os
from pathlib import Path
import sys
import urllib.request
import wandb

def require_private_project():
    entity, project = os.environ["WANDB_ENTITY"], os.environ["WANDB_PROJECT"]
    payload = {"query": "query($e:String!,$p:String!){project(name:$p,entityName:$e){name access}}", "variables": {"e": entity, "p": project}}
    authorization = base64.b64encode(("api:" + os.environ["WANDB_API_KEY"]).encode()).decode()
    request = urllib.request.Request("https://api.wandb.ai/graphql", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json", "Authorization": "Basic " + authorization})
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.load(response)
    if result.get("data", {}).get("project", {}).get("access") != "PRIVATE":
        raise RuntimeError("An existing PRIVATE project is required")
    return entity, project

def log_trial(file):
    record = json.loads(file.read_text())
    entity, project = require_private_project()
    with wandb.init(entity=entity, project=project, id=record["wandbRunId"], resume="allow", job_type="course-trial",
                    group=record["project"], name=f'{record["project"]}-{record["variant"]}-{record["trial"]}',
                    config={key: record[key] for key in ["sourceCommit", "model", "variant", "trial", "configuration", "protocol", "applicationSha256", "checkerSha256"] if key in record},
                    settings=wandb.Settings(disable_git=True, disable_code=True)) as run:
        metrics = {"passed": int(record["outcome"] == "passed"), "outcome": record["outcome"]}
        for key in ["inputTokens", "outputTokens", "estimatedCostUsd", "sandboxSecondsUpperBound"]:
            if record.get(key) is not None:
                metrics[key] = record[key]
        metrics["completedChecks"] = sum(c["passed"] for c in record.get("grade", {}).get("checks", []))
        run.log(metrics)
        table = wandb.Table(columns=["trial", "variant", "outcome", "conversation_ids", "source_commit"],
                            data=[[record["id"], record["variant"], record["outcome"], json.dumps(record["conversationIds"]), record["sourceCommit"]]])
        run.log({"comparison": table})
        artifact = wandb.Artifact("trial-" + record["id"], type="course-evidence", metadata={"schemaVersion": 1, "sourceCommit": record["sourceCommit"]})
        artifact.add_dir(str(file.parent))
        run.log_artifact(artifact).wait()
        record["wandbRunUrl"] = run.url
        record["artifactUrl"] = f"https://wandb.ai/{entity}/{project}/artifacts/course-evidence/{artifact.name}"
    file.write_text(json.dumps(record, indent=2) + "\n")

if __name__ == "__main__":
    log_trial(Path(sys.argv[1]).resolve())
