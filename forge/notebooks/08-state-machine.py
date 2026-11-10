# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.25.1",
#     "wandb==0.31.0",
# ]
# ///
# Canonical course notebook. Edit forge/lessons/*.md and shared native cells.
# Generate with forge/scripts/create_notebooks.py; evidence refresh is explicit.

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="normal")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import base64
    import io
    import json
    import os
    import subprocess
    import uuid
    import zipfile
    from pathlib import Path
    from collections import Counter

    return Counter, base64, io, json, mo, zipfile


@app.cell(hide_code=True)
def _(json):
    project_id = 'project-08'
    runner_commit = 'dcf7e447f565961e790ed1f4a25815b278db124e'
    saved = json.loads('{"schemaVersion": 1, "capturedAt": "2026-11-06T13:10:01.889869+00:00", "status": "Saved at 2026-11-06T13:10:01.889869+00:00: 12 completed coding attempts for project-08. Outcomes include unsuccessful attempts. No human time savings are inferred.", "trials": [{"id": "03ca01ca-eb64-45ae-9317-824ca4a26026", "project": "project-08", "variant": "graph", "trial": 1, "sourceCommit": "24ff7909edb286b0e66faae1d78968d12aac6c0c", "outcome": "passed", "inputTokens": 314551, "outputTokens": 9632, "estimatedCostUsd": 0.10332285, "conversationIds": ["01a1b0f6-3819-741a-8e19-36e4d0e86733"], "wandbRunUrl": "https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/03ca01caeb6445ae", "artifactUrl": "https://wandb.ai/wandb/learn-harness-engineering-forge/artifacts/course-evidence/trial-03ca01ca-eb64-45ae-9317-824ca4a26026:v0", "startedAt": "2026-11-06T13:04:42.629Z", "finishedAt": "2026-11-06T13:06:56.825Z", "actorCompleted": true, "error": null, "protocolRevision": 4, "protocolSha256": "64b1c08c477caf830124842e192ffeeadaa0142b5f3bdb5dc2f81d68e4420467", "grade": {"schemaVersion": 1, "task": "project-04", "checks": [{"name": "strict compile and renderer build", "passed": true}, {"name": "real import and persistence after reconstruction", "passed": true}, {"name": "actual indexing keeps every nonempty paragraph", "passed": true}, {"name": "actual retrieval and Q&A persist two turns", "passed": true}, {"name": "architecture checker rejects a seeded boundary violation", "passed": true}, {"name": "Electron window, preload, import, indexing and question UI under Xvfb", "passed": true}], "passed": true}, "reconciledEstimateUsd": 0.10332285, "chargedUnknownReservationUsd": null, "actorPhases": [{"conversationId": "01a1b0f6-3819-741a-8e19-36e4d0e86733", "requests": 22, "turns": 22, "completed": true, "telemetryComplete": true, "errors": []}]}, {"id": "22955029-2de6-4aed-8c35-dda6059b023d", "project": "project-08", "variant": "graph", "trial": 1, "sourceCommit": "945c5d3073026a4fea427372843ea79072221dde", "outcome": "task_failed", "inputTokens": 415339, "outputTokens": 8083, "estimatedCostUsd": 0.12844285333333333, "conversationIds": ["01a1b0ea-4115-778f-b948-16b9a1a4ed4d"], "wandbRunUrl": "https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/229550292de64aed", "artifactUrl": "https://wandb.ai/wandb/learn-harness-engineering-forge/artifacts/course-evidence/trial-22955029-2de6-4aed-8c35-dda6059b023d:v0", "startedAt": "2026-11-06T12:51:37.030Z", "finishedAt": "2026-11-06T12:54:10.853Z", "actorCompleted": false, "error": null, "protocolRevision": 4, "protocolSha256": "64b1c08c477caf830124842e192ffeeadaa0142b5f3bdb5dc2f81d68e4420467", "grade": {"schemaVersion": 1, "task": "project-04", "checks": [{"name": "strict compile and renderer build", "passed": true}, {"name": "real import and persistence after reconstruction", "passed": true}, {"name": "actual indexing keeps every nonempty paragraph", "passed": true}, {"name": "actual retrieval and Q&A persist two turns", "passed": true}, {"name": "architecture checker rejects a seeded boundary violation", "passed": false, "error": "AssertionError [ERR_ASSERTION]: The expression evaluated to a falsy value:\\n\\n  assert.ok(fs.existsSync(guard))\\n"}, {"name": "Electron window, preload, import, indexing and question UI under Xvfb", "passed": true}], "passed": false}, "reconciledEstimateUsd": 0.12844285333333333, "chargedUnknownReservationUsd": null, "actorPhases": [{"conversationId": "01a1b0ea-4115-778f-b948-16b9a1a4ed4d", "requests": 24, "turns": 25, "completed": false, "telemetryComplete": true, "errors": ["Model-call budget exhausted"]}]}, {"id": "287d745e-ca9f-49c1-bbf4-46048cc6dff9", "project": "project-08", "variant": "graph", "trial": 1, "sourceCommit": "8f4521bc34bb340dd4aa75e5bf1a6e6c49a68bef", "outcome": "task_failed", "inputTokens": 305590, "outputTokens": 6766, "estimatedCostUsd": 0.09711906666666667, "conversationIds": ["01a1b00d-5123-77f0-952f-7833df0616ea"], "wandbRunUrl": "https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/287d745eca9f49c1", "artifactUrl": "https://wandb.ai/wandb/learn-harness-engineering-forge/artifacts/course-evidence/trial-287d745e-ca9f-49c1-bbf4-46048cc6dff9:v0", "startedAt": "2026-11-06T08:50:11.625Z", "finishedAt": "2026-11-06T08:52:21.913Z", "actorCompleted": false, "error": null, "protocolRevision": 2, "protocolSha256": "87e457ec9cf3716839df078fadd5cae1e5a1a1e5cc4b14eed2e06e72fe041141", "grade": {"schemaVersion": 1, "task": "project-04", "checks": [{"name": "strict compile and renderer build", "passed": true}, {"name": "real import and persistence after reconstruction", "passed": true}, {"name": "actual indexing keeps every nonempty paragraph", "passed": true}, {"name": "actual retrieval and Q&A persist two turns", "passed": true}, {"name": "architecture checker rejects a seeded boundary violation", "passed": false, "error": "AssertionError [ERR_ASSERTION]: The expression evaluated to a falsy value:\\n\\n  assert.ok(fs.existsSync(guard))\\n"}, {"name": "Electron window, preload, import, indexing and question UI under Xvfb", "passed": false, "error": "Error: page.evaluate: TypeError: Cannot read properties of undefined (reading \'documents\')\\n    at eval (eval at evaluate (:302:30), <anonymous>:1:33)\\n    at UtilityScript.evaluate (<anonymous>:304:16)\\n    at UtilityScript.<anonymous> (<anonymous>:1:44)"}], "passed": false}, "reconciledEstimateUsd": 0.09711906666666667, "chargedUnknownReservationUsd": null, "actorPhases": [{"conversationId": "01a1b00d-5123-77f0-952f-7833df0616ea", "requests": 21, "turns": 22, "completed": false, "telemetryComplete": true, "errors": ["Frozen input byte budget exceeded"]}]}, {"id": "3e5cd770-94e5-49f9-b478-a2043dc9a682", "project": "project-08", "variant": "graph", "trial": 1, "sourceCommit": "24ff7909edb286b0e66faae1d78968d12aac6c0c", "outcome": "task_failed", "inputTokens": 366028, "outputTokens": 5004, "estimatedCostUsd": 0.11798033866666667, "conversationIds": ["01a1b0f0-5fff-72da-a0dc-c0192ac02147"], "wandbRunUrl": "https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/3e5cd77094e549f9", "artifactUrl": "https://wandb.ai/wandb/learn-harness-engineering-forge/artifacts/course-evidence/trial-3e5cd770-94e5-49f9-b478-a2043dc9a682:v0", "startedAt": "2026-11-06T12:58:18.721Z", "finishedAt": "2026-11-06T13:01:52.950Z", "actorCompleted": false, "error": null, "protocolRevision": 4, "protocolSha256": "64b1c08c477caf830124842e192ffeeadaa0142b5f3bdb5dc2f81d68e4420467", "grade": {"schemaVersion": 1, "task": "project-04", "checks": [{"name": "strict compile and renderer build", "passed": true}, {"name": "real import and persistence after reconstruction", "passed": true}, {"name": "actual indexing keeps every nonempty paragraph", "passed": true}, {"name": "actual retrieval and Q&A persist two turns", "passed": true}, {"name": "architecture checker rejects a seeded boundary violation", "passed": false, "error": "AssertionError [ERR_ASSERTION]: architecture checker accepted a Node import in the renderer"}, {"name": "Electron window, preload, import, indexing and question UI under Xvfb", "passed": true}], "passed": false}, "reconciledEstimateUsd": 0.11798033866666667, "chargedUnknownReservationUsd": null, "actorPhases": [{"conversationId": "01a1b0f0-5fff-72da-a0dc-c0192ac02147", "requests": 24, "turns": 25, "completed": false, "telemetryComplete": true, "errors": ["Model-call budget exhausted"]}]}, {"id": "43ad509b-7eb5-4d9e-97c7-ff33567693fd", "project": "project-08", "variant": "graph", "trial": 1, "sourceCommit": "24ff7909edb286b0e66faae1d78968d12aac6c0c", "outcome": "task_failed", "inputTokens": 374442, "outputTokens": 5462, "estimatedCostUsd": 0.11004467866666667, "conversationIds": ["01a1b0f4-27ac-75c4-a696-3508bd27ebb3"], "wandbRunUrl": "https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/43ad509b7eb54d9e", "artifactUrl": "https://wandb.ai/wandb/learn-harness-engineering-forge/artifacts/course-evidence/trial-43ad509b-7eb5-4d9e-97c7-ff33567693fd:v0", "startedAt": "2026-11-06T13:02:27.144Z", "finishedAt": "2026-11-06T13:04:09.277Z", "actorCompleted": false, "error": null, "protocolRevision": 4, "protocolSha256": "64b1c08c477caf830124842e192ffeeadaa0142b5f3bdb5dc2f81d68e4420467", "grade": {"schemaVersion": 1, "task": "project-04", "checks": [{"name": "strict compile and renderer build", "passed": false, "error": "Error: Command failed: node /opt/app/node_modules/typescript/bin/tsc --noEmit -p tsconfig.node.json"}], "passed": false}, "reconciledEstimateUsd": 0.11004467866666667, "chargedUnknownReservationUsd": null, "actorPhases": [{"conversationId": "01a1b0f4-27ac-75c4-a696-3508bd27ebb3", "requests": 24, "turns": 25, "completed": false, "telemetryComplete": true, "errors": ["Model-call budget exhausted"]}]}, {"id": "46f51f6a-b922-42e0-bb94-854421e9209c", "project": "project-08", "variant": "graph", "trial": 1, "sourceCommit": "3ebea13e260921c0c231ff43b6d13bc265d25157", "outcome": "task_failed", "inputTokens": 298274, "outputTokens": 6601, "estimatedCostUsd": 0.09722744866666666, "conversationIds": ["01a1b01f-5dbb-722e-a277-e80239748b3a"], "wandbRunUrl": "https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/46f51f6ab92242e0", "artifactUrl": "https://wandb.ai/wandb/learn-harness-engineering-forge/artifacts/course-evidence/trial-46f51f6a-b922-42e0-bb94-854421e9209c:v0", "startedAt": "2026-11-06T09:10:01.494Z", "finishedAt": "2026-11-06T09:12:34.752Z", "actorCompleted": false, "error": null, "protocolRevision": 2, "protocolSha256": "87e457ec9cf3716839df078fadd5cae1e5a1a1e5cc4b14eed2e06e72fe041141", "grade": {"schemaVersion": 1, "task": "project-04", "checks": [{"name": "strict compile and renderer build", "passed": true}, {"name": "real import and persistence after reconstruction", "passed": true}, {"name": "actual indexing keeps every nonempty paragraph", "passed": true}, {"name": "actual retrieval and Q&A persist two turns", "passed": true}, {"name": "architecture checker rejects a seeded boundary violation", "passed": false, "error": "AssertionError [ERR_ASSERTION]: The expression evaluated to a falsy value:\\n\\n  assert.ok(fs.existsSync(guard))\\n"}, {"name": "Electron window, preload, import, indexing and question UI under Xvfb", "passed": false, "error": "Error: page.evaluate: TypeError: Cannot read properties of undefined (reading \'documents\')\\n    at eval (eval at evaluate (:302:30), <anonymous>:1:33)\\n    at UtilityScript.evaluate (<anonymous>:304:16)\\n    at UtilityScript.<anonymous> (<anonymous>:1:44)"}], "passed": false}, "reconciledEstimateUsd": 0.09722744866666666, "chargedUnknownReservationUsd": null, "actorPhases": [{"conversationId": "01a1b01f-5dbb-722e-a277-e80239748b3a", "requests": 21, "turns": 22, "completed": false, "telemetryComplete": true, "errors": ["Frozen input byte budget exceeded"]}]}, {"id": "532b1822-b26a-438f-ba4f-3f6f30bcf837", "project": "project-08", "variant": "graph", "trial": 1, "sourceCommit": "8f4521bc34bb340dd4aa75e5bf1a6e6c49a68bef", "outcome": "task_failed", "inputTokens": 243503, "outputTokens": 8393, "estimatedCostUsd": 0.09327494933333333, "conversationIds": ["01a1b004-85b2-7170-aa92-3bae2719c3f9"], "wandbRunUrl": "https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/532b1822b26a438f", "artifactUrl": "https://wandb.ai/wandb/learn-harness-engineering-forge/artifacts/course-evidence/trial-532b1822-b26a-438f-ba4f-3f6f30bcf837:v0", "startedAt": "2026-11-06T08:39:26.769Z", "finishedAt": "2026-11-06T08:43:18.677Z", "actorCompleted": false, "error": null, "protocolRevision": 2, "protocolSha256": "87e457ec9cf3716839df078fadd5cae1e5a1a1e5cc4b14eed2e06e72fe041141", "grade": {"schemaVersion": 1, "task": "project-04", "checks": [{"name": "strict compile and renderer build", "passed": false, "error": "Error: Command failed: node /opt/app/node_modules/typescript/bin/tsc --noEmit -p tsconfig.json"}], "passed": false}, "reconciledEstimateUsd": 0.09327494933333333, "chargedUnknownReservationUsd": null, "actorPhases": [{"conversationId": "01a1b004-85b2-7170-aa92-3bae2719c3f9", "requests": 18, "turns": 19, "completed": false, "telemetryComplete": true, "errors": ["Frozen input byte budget exceeded"]}]}, {"id": "54bb7391-48b0-47f5-9ded-36194f52a76d", "project": "project-08", "variant": "graph", "trial": 1, "sourceCommit": "945c5d3073026a4fea427372843ea79072221dde", "outcome": "task_failed", "inputTokens": 379038, "outputTokens": 7923, "estimatedCostUsd": 0.119441758, "conversationIds": ["01a1b0ed-1ecd-74f6-842a-87fe5e7c60eb"], "wandbRunUrl": "https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/54bb739148b047f5", "artifactUrl": "https://wandb.ai/wandb/learn-harness-engineering-forge/artifacts/course-evidence/trial-54bb7391-48b0-47f5-9ded-36194f52a76d:v0", "startedAt": "2026-11-06T12:54:46.049Z", "finishedAt": "2026-11-06T12:57:22.817Z", "actorCompleted": false, "error": null, "protocolRevision": 4, "protocolSha256": "64b1c08c477caf830124842e192ffeeadaa0142b5f3bdb5dc2f81d68e4420467", "grade": {"schemaVersion": 1, "task": "project-04", "checks": [{"name": "strict compile and renderer build", "passed": true}, {"name": "real import and persistence after reconstruction", "passed": true}, {"name": "actual indexing keeps every nonempty paragraph", "passed": true}, {"name": "actual retrieval and Q&A persist two turns", "passed": true}, {"name": "architecture checker rejects a seeded boundary violation", "passed": false, "error": "AssertionError [ERR_ASSERTION]: The expression evaluated to a falsy value:\\n\\n  assert.ok(fs.existsSync(guard))\\n"}, {"name": "Electron window, preload, import, indexing and question UI under Xvfb", "passed": true}], "passed": false}, "reconciledEstimateUsd": 0.119441758, "chargedUnknownReservationUsd": null, "actorPhases": [{"conversationId": "01a1b0ed-1ecd-74f6-842a-87fe5e7c60eb", "requests": 24, "turns": 25, "completed": false, "telemetryComplete": true, "errors": ["Model-call budget exhausted"]}]}, {"id": "c0f6a4ba-cfcf-47c4-aded-3d06efa982d3", "project": "project-08", "variant": "graph", "trial": 1, "sourceCommit": "3ebea13e260921c0c231ff43b6d13bc265d25157", "outcome": "task_failed", "inputTokens": 256846, "outputTokens": 7768, "estimatedCostUsd": 0.096558856, "conversationIds": ["01a1b01c-95f2-7556-a709-8d3a852c7d73"], "wandbRunUrl": "https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/c0f6a4bacfcf47c4", "artifactUrl": "https://wandb.ai/wandb/learn-harness-engineering-forge/artifacts/course-evidence/trial-c0f6a4ba-cfcf-47c4-aded-3d06efa982d3:v0", "startedAt": "2026-11-06T09:05:21.553Z", "finishedAt": "2026-11-06T09:09:21.850Z", "actorCompleted": false, "error": null, "protocolRevision": 2, "protocolSha256": "87e457ec9cf3716839df078fadd5cae1e5a1a1e5cc4b14eed2e06e72fe041141", "grade": {"schemaVersion": 1, "task": "project-04", "checks": [{"name": "strict compile and renderer build", "passed": false, "error": "Error: Command failed: node /opt/app/node_modules/typescript/bin/tsc --noEmit -p tsconfig.node.json"}], "passed": false}, "reconciledEstimateUsd": 0.096558856, "chargedUnknownReservationUsd": null, "actorPhases": [{"conversationId": "01a1b01c-95f2-7556-a709-8d3a852c7d73", "requests": 19, "turns": 20, "completed": false, "telemetryComplete": true, "errors": ["Frozen input byte budget exceeded"]}]}, {"id": "f6ae2a06-3a5e-4cf0-88c4-80a2b0b03c2b", "project": "project-08", "variant": "graph", "trial": 1, "sourceCommit": "8f4521bc34bb340dd4aa75e5bf1a6e6c49a68bef", "outcome": "task_failed", "inputTokens": 184146, "outputTokens": 8241, "estimatedCostUsd": 0.08430663799999999, "conversationIds": ["01a1b009-a455-7032-a2ea-bf73f5ad9930"], "wandbRunUrl": "https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/f6ae2a063a5e4cf0", "artifactUrl": "https://wandb.ai/wandb/learn-harness-engineering-forge/artifacts/course-evidence/trial-f6ae2a06-3a5e-4cf0-88c4-80a2b0b03c2b:v0", "startedAt": "2026-11-06T08:44:28.696Z", "finishedAt": "2026-11-06T08:49:25.773Z", "actorCompleted": false, "error": null, "protocolRevision": 2, "protocolSha256": "87e457ec9cf3716839df078fadd5cae1e5a1a1e5cc4b14eed2e06e72fe041141", "grade": {"schemaVersion": 1, "task": "project-04", "checks": [{"name": "strict compile and renderer build", "passed": false, "error": "Error: Command failed: node /opt/app/node_modules/typescript/bin/tsc --noEmit -p tsconfig.json"}], "passed": false}, "reconciledEstimateUsd": 0.08430663799999999, "chargedUnknownReservationUsd": null, "actorPhases": [{"conversationId": "01a1b009-a455-7032-a2ea-bf73f5ad9930", "requests": 16, "turns": 17, "completed": false, "telemetryComplete": true, "errors": ["Frozen input byte budget exceeded"]}]}, {"id": "fbbb858f-935a-4281-b07d-1f4fb984e252", "project": "project-08", "variant": "graph", "trial": 1, "sourceCommit": "3ebea13e260921c0c231ff43b6d13bc265d25157", "outcome": "task_failed", "inputTokens": 254583, "outputTokens": 7195, "estimatedCostUsd": 0.09070795866666667, "conversationIds": ["01a1b024-6072-759b-b6ac-f98df019292e"], "wandbRunUrl": "https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/fbbb858f935a4281", "artifactUrl": "https://wandb.ai/wandb/learn-harness-engineering-forge/artifacts/course-evidence/trial-fbbb858f-935a-4281-b07d-1f4fb984e252:v0", "startedAt": "2026-11-06T09:15:29.777Z", "finishedAt": "2026-11-06T09:18:41.838Z", "actorCompleted": false, "error": null, "protocolRevision": 2, "protocolSha256": "87e457ec9cf3716839df078fadd5cae1e5a1a1e5cc4b14eed2e06e72fe041141", "grade": {"schemaVersion": 1, "task": "project-04", "checks": [{"name": "strict compile and renderer build", "passed": true}, {"name": "real import and persistence after reconstruction", "passed": true}, {"name": "actual indexing keeps every nonempty paragraph", "passed": true}, {"name": "actual retrieval and Q&A persist two turns", "passed": true}, {"name": "architecture checker rejects a seeded boundary violation", "passed": false, "error": "AssertionError [ERR_ASSERTION]: The expression evaluated to a falsy value:\\n\\n  assert.ok(fs.existsSync(guard))\\n"}, {"name": "Electron window, preload, import, indexing and question UI under Xvfb", "passed": false, "error": "Error: page.evaluate: TypeError: Cannot read properties of undefined (reading \'documents\')\\n    at eval (eval at evaluate (:302:30), <anonymous>:1:33)\\n    at UtilityScript.evaluate (<anonymous>:304:16)\\n    at UtilityScript.<anonymous> (<anonymous>:1:44)"}], "passed": false}, "reconciledEstimateUsd": 0.09070795866666667, "chargedUnknownReservationUsd": null, "actorPhases": [{"conversationId": "01a1b024-6072-759b-b6ac-f98df019292e", "requests": 19, "turns": 20, "completed": false, "telemetryComplete": true, "errors": ["Frozen input byte budget exceeded"]}]}, {"id": "fc80b4f3-6178-454f-a003-3e311dab6617", "project": "project-08", "variant": "graph", "trial": 1, "sourceCommit": "945c5d3073026a4fea427372843ea79072221dde", "outcome": "task_failed", "inputTokens": 394017, "outputTokens": 7424, "estimatedCostUsd": 0.12121640866666666, "conversationIds": ["01a1b0e7-9f72-720e-8b82-378a137f0943"], "wandbRunUrl": "https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/fc80b4f36178454f", "artifactUrl": "https://wandb.ai/wandb/learn-harness-engineering-forge/artifacts/course-evidence/trial-fc80b4f3-6178-454f-a003-3e311dab6617:v0", "startedAt": "2026-11-06T12:48:44.190Z", "finishedAt": "2026-11-06T12:51:06.726Z", "actorCompleted": false, "error": null, "protocolRevision": 4, "protocolSha256": "64b1c08c477caf830124842e192ffeeadaa0142b5f3bdb5dc2f81d68e4420467", "grade": {"schemaVersion": 1, "task": "project-04", "checks": [{"name": "strict compile and renderer build", "passed": true}, {"name": "real import and persistence after reconstruction", "passed": true}, {"name": "actual indexing keeps every nonempty paragraph", "passed": true}, {"name": "actual retrieval and Q&A persist two turns", "passed": true}, {"name": "architecture checker rejects a seeded boundary violation", "passed": false, "error": "AssertionError [ERR_ASSERTION]: The expression evaluated to a falsy value:\\n\\n  assert.ok(fs.existsSync(guard))\\n"}, {"name": "Electron window, preload, import, indexing and question UI under Xvfb", "passed": true}], "passed": false}, "reconciledEstimateUsd": 0.12121640866666666, "chargedUnknownReservationUsd": null, "actorPhases": [{"conversationId": "01a1b0e7-9f72-720e-8b82-378a137f0943", "requests": 24, "turns": 25, "completed": false, "telemetryComplete": true, "errors": ["Model-call budget exhausted"]}]}], "qualifications": [{"id": "qualification-17b194af-b3ef-4d47-95cc-178676315b60", "passed": false, "sourceCommit": "1b316ef2aadd5f0a2d87fbaac1c2c5a505054dd7", "protocolSha256": null, "startedAt": "2026-11-06T07:30:28.545Z", "finishedAt": "2026-11-06T07:30:53.897Z", "inputTokens": null, "outputTokens": null, "estimatedCostUsd": null, "error": "CWSandboxTransportError: Streaming command cancelled.", "reconciledEstimateUsd": 0.003, "chargedUnknownReservationUsd": null, "agentConversationId": null, "appConversationId": null}, {"id": "qualification-19560d68-131a-4318-8dd8-ed73a1219d2e", "passed": true, "sourceCommit": "8f4521bc34bb340dd4aa75e5bf1a6e6c49a68bef", "protocolSha256": "87e457ec9cf3716839df078fadd5cae1e5a1a1e5cc4b14eed2e06e72fe041141", "startedAt": "2026-11-06T08:10:36.582Z", "finishedAt": "2026-11-06T08:11:12.699Z", "inputTokens": 1379, "outputTokens": 1712, "estimatedCostUsd": 0.0047544779999999995, "error": null, "reconciledEstimateUsd": 0.0047544779999999995, "chargedUnknownReservationUsd": null, "agentConversationId": "01a1afe9-18f7-7426-9438-0a5ce055a5df", "appConversationId": "app-2e8a1266-70a9-4cc6-8baf-0b0d82729e8e"}, {"id": "qualification-1c68ebdf-feba-4158-8192-d5be5b3e2a98", "passed": false, "sourceCommit": "6907491cc07b3cad91f26bbdfaf60570fc1f246b", "protocolSha256": "87e457ec9cf3716839df078fadd5cae1e5a1a1e5cc4b14eed2e06e72fe041141", "startedAt": "2026-11-06T07:42:00.479Z", "finishedAt": "2026-11-06T07:43:56.209Z", "inputTokens": null, "outputTokens": null, "estimatedCostUsd": null, "error": "Error: Pi capability/usage qualification failed", "reconciledEstimateUsd": null, "chargedUnknownReservationUsd": 2, "agentConversationId": "01a1afce-f833-7499-9384-ce63ee41a908", "appConversationId": null}, {"id": "qualification-2ebe0500-a0d6-47dc-b3ae-b4ef8ba988ff", "passed": true, "sourceCommit": "30db3581757e79b9791b1b70262e6ac499fab87f", "protocolSha256": "64b1c08c477caf830124842e192ffeeadaa0142b5f3bdb5dc2f81d68e4420467", "startedAt": "2026-11-06T11:00:52.920Z", "finishedAt": "2026-11-06T11:02:12.857Z", "inputTokens": 1383, "outputTokens": 1699, "estimatedCostUsd": 0.004789874666666666, "error": null, "reconciledEstimateUsd": 0.004789874666666666, "chargedUnknownReservationUsd": null, "agentConversationId": "01a1b084-dd29-729e-b8d4-d0ee042d8f1b", "appConversationId": "app-bace80b4-24a6-4c67-bc75-def5cd385a2d"}, {"id": "qualification-37a4f9ea-2162-45a1-8322-82c1e5259a02", "passed": false, "sourceCommit": "e8ce7010369b1ac87a196f1f5abfdadbbf517a1d", "protocolSha256": "7b58c62370e7491386e1b3aff9caf6c750057aef77c4e50e269f72327b8ff9fb", "startedAt": "2026-11-06T10:39:59.601Z", "finishedAt": "2026-11-06T10:41:16.869Z", "inputTokens": null, "outputTokens": null, "estimatedCostUsd": null, "error": "Error: Live app service qualification failed", "reconciledEstimateUsd": null, "chargedUnknownReservationUsd": 2, "agentConversationId": "01a1b071-c165-75d3-abb7-47c1466a65d1", "appConversationId": "app-16d1c9fd-33ba-4a00-98dd-7e982e078409"}, {"id": "qualification-af9192de-dfe3-4631-934e-37729c2a4d56", "passed": false, "sourceCommit": "23f50a21e66e4baaf9a2c05e6298c114699865ae", "protocolSha256": null, "startedAt": "2026-11-06T07:32:07.987Z", "finishedAt": "2026-11-06T07:33:42.624Z", "inputTokens": null, "outputTokens": null, "estimatedCostUsd": null, "error": "Error: Missing usage or pricing", "reconciledEstimateUsd": 0.010988719333333332, "chargedUnknownReservationUsd": null, "agentConversationId": "01a1afc5-f26c-76f0-acd4-e04997acccae", "appConversationId": "app-bfc6a439-47d1-4283-bce9-67f87dd15754"}, {"id": "qualification-cff12c5e-6a23-4d3b-a138-f1961945be14", "passed": false, "sourceCommit": "3afbf9bf93c337492164a8c3980a8cc287eec0dd", "protocolSha256": "7b58c62370e7491386e1b3aff9caf6c750057aef77c4e50e269f72327b8ff9fb", "startedAt": "2026-11-06T10:41:52.740Z", "finishedAt": "2026-11-06T10:43:01.815Z", "inputTokens": null, "outputTokens": null, "estimatedCostUsd": null, "error": "Error: Live app service qualification failed", "reconciledEstimateUsd": null, "chargedUnknownReservationUsd": 2, "agentConversationId": "01a1b073-7d9f-77b2-97cc-558ae35acc9e", "appConversationId": "app-e618ce51-bff4-49f1-97c3-5683585feb0d"}, {"id": "qualification-e30ebcea-2c57-4e73-99cc-9b9b10c0f82f", "passed": true, "sourceCommit": "3627ca6dea154b1a875ac323616284bd00d331a1", "protocolSha256": "b538fa6c66cf2c46dd914d0697c69cb984c9f203d71a851f8bfdfbc9b6bac90f", "startedAt": "2026-11-06T10:44:27.761Z", "finishedAt": "2026-11-06T10:45:31.532Z", "inputTokens": 1387, "outputTokens": 1683, "estimatedCostUsd": 0.00512862, "error": null, "reconciledEstimateUsd": 0.00512862, "chargedUnknownReservationUsd": null, "agentConversationId": "01a1b075-dd3f-7068-8b45-88e2dc995650", "appConversationId": "app-e2986e15-9d75-4525-bdf3-d66d49017d88"}, {"id": "qualification-ed8a8028-bb60-4eff-a678-e5e74e94d2cc", "passed": true, "sourceCommit": "09a716af4cdd8467729f4185081dab019d7a8e1a", "protocolSha256": null, "startedAt": "2026-11-06T07:34:48.721Z", "finishedAt": "2026-11-06T07:35:41.927Z", "inputTokens": 1439, "outputTokens": 1667, "estimatedCostUsd": 0.004988329333333333, "error": null, "reconciledEstimateUsd": 0.004988329333333333, "chargedUnknownReservationUsd": null, "agentConversationId": "01a1afc8-6119-75c3-af09-4339c5f7c94f", "appConversationId": "app-d758b5b7-ca03-4fde-a743-5577fafe284e"}], "concurrencyQualifications": [{"schemaVersion": 1, "id": "concurrency-61ad1e33-0ede-46ff-b513-1a700e9798ce", "sourceCommit": "2947d9f6386cefefd1977fb2dd569a4d4226d74d", "startedAt": "2026-11-06T08:30:35.081Z", "passed": true, "sessions": [{"conversationId": "app-concurrency-61ad1e33-0ede-46ff-b513-1a700e9798ce-alpha", "usage": {"inputTokens": 186, "outputTokens": 1008, "calls": 2}, "attributes": {"course.app_variant": "concurrency-alpha", "course.role": "knowledge-base", "course.project": "qualification", "course.task": "concurrent-app-traces", "course.variant": "alpha", "course.trial": "concurrency-61ad1e33-0ede-46ff-b513-1a700e9798ce", "course.source_commit": "2947d9f6386cefefd1977fb2dd569a4d4226d74d", "course.sandbox_id": "local-app-process", "course.wandb_run_id": "course-audit-20261106"}}, {"conversationId": "app-concurrency-61ad1e33-0ede-46ff-b513-1a700e9798ce-beta", "usage": {"inputTokens": 186, "outputTokens": 635, "calls": 2}, "attributes": {"course.app_variant": "concurrency-beta", "course.role": "knowledge-base", "course.project": "qualification", "course.task": "concurrent-app-traces", "course.variant": "beta", "course.trial": "concurrency-61ad1e33-0ede-46ff-b513-1a700e9798ce", "course.source_commit": "2947d9f6386cefefd1977fb2dd569a4d4226d74d", "course.sandbox_id": "local-app-process", "course.wandb_run_id": "course-audit-20261106"}}], "results": [{"status": "fulfilled"}, {"status": "fulfilled"}], "inputTokens": 372, "outputTokens": 1643, "estimatedCostUsd": 0.00214675, "finishedAt": "2026-11-06T08:30:44.097Z"}], "sandboxQualifications": [{"schemaVersion": 1, "id": "sandbox-qualification-15043cce-9df6-4cc6-9e66-44b1947ea5e2", "sourceCommit": "f176ac0c3afe7b1cd0dc2042800a51472e422074", "startedAt": "2026-11-06T08:57:13.844Z", "passed": false, "checks": [{"name": "bounded command wait times out", "passed": true}], "reservationIds": {"interruptId": "304a61f2-46ea-442c-a1bd-d0ac41a6c21d", "resumeId": "3458c1a0-5de4-416b-81a9-1757d2093ef1"}, "error": "AssertionError [ERR_ASSERTION]: cancelled process must no longer exist\\n\\n1 !== 0\\n", "finishedAt": "2026-11-06T08:57:28.932Z", "estimatedCostUsd": null}, {"schemaVersion": 1, "id": "sandbox-qualification-eab8e9f7-6d4d-4d1c-8582-5cbf4f41197c", "sourceCommit": "4a247914feab11d0f868ab4083146e45fc28acda", "startedAt": "2026-11-06T09:01:55.766Z", "passed": true, "checks": [{"name": "bounded command wait times out", "passed": true}, {"name": "cancelled remote process group is no longer running", "passed": true}, {"name": "interrupted session exports patch and checkpoint before termination", "passed": true}, {"name": "fresh workspace resumes exact exported progress", "passed": true}, {"name": "both distinct sandboxes confirm terminal state", "passed": true}], "reservationIds": {"interruptId": "c0fbc6d2-2c3a-4337-82cf-6fa25e5c7403", "resumeId": "40a0261f-7f59-4c1d-982e-8632252a65b3"}, "finishedAt": "2026-11-06T09:03:14.081Z", "estimatedCostUsd": 0.007330418666666666}, {"schemaVersion": 1, "id": "sandbox-qualification-f566ddc3-297f-4483-98a8-47c6d15a402c", "sourceCommit": "5ab40f10d6c5275815bb9962006f445800d53d6b", "startedAt": "2026-11-06T08:55:51.478Z", "passed": false, "checks": [], "error": "CWSandboxValidationError: tags contains invalid value: sandbox-qualification-f566ddc3-297f-4483-98a8-47c6d15a402c-interrupt. tags may contain letters, numbers, \'.\', \'_\' or \'-\', must be 59 characters or fewer, must end with a letter or number, and may start with \'.\', \'_\' or \'-\'", "finishedAt": "2026-11-06T08:55:52.563Z", "estimatedCostUsd": null}], "completedComparisonBlocks": [], "loops": [], "graphs": [{"file": "project-08-control-flow-qualification-74896eb2-b69a-4e53-be6c-44a010bbf07d.json", "schemaVersion": 1, "id": "74896eb2-b69a-4e53-be6c-44a010bbf07d", "sourceCommit": "0cbd4fdb330cbc1c9346b4b8a7062c2a33fcb517", "node": "approval", "attempts": 2, "maxAttempts": 2, "transitions": [{"from": "plan", "to": "make", "at": "2026-11-06T11:12:35.190Z", "reason": "frozen task acceptance criteria"}, {"from": "make", "to": "verify", "at": "2026-11-06T11:12:35.195Z", "reason": "candidate patch exported"}, {"from": "verify", "to": "rollback", "at": "2026-11-06T11:14:13.941Z", "reason": "independent parallel verification results"}, {"from": "rollback", "to": "make", "at": "2026-11-06T11:14:13.944Z", "reason": "restore last verified patch or frozen baseline"}, {"from": "make", "to": "verify", "at": "2026-11-06T11:14:13.950Z", "reason": "candidate patch exported"}, {"from": "verify", "to": "approval", "at": "2026-11-06T11:14:55.404Z", "reason": "independent parallel verification results"}], "qualification": "deterministic control-flow fixture; excluded from coding trial counts", "plan": "Verify the seeded baseline fails, rollback, verify a documented manual repair, then pause for a human decision.", "candidate": {"patch": "/Users/ashah/Documents/GitHub/learn-harness-engineering/forge/local-results/graph-qualification-74896eb2-b69a-4e53-be6c-44a010bbf07d/candidate-2.diff", "sha256": "91c4a2df7b9a65921c221b68bc86cdd40db4d5945fce16510206a405ac7516e6", "trialId": "fixture-2"}, "verification": [{"lane": "services", "passed": true, "evidence": "/Users/ashah/Documents/GitHub/learn-harness-engineering/forge/local-results/graph-qualification-74896eb2-b69a-4e53-be6c-44a010bbf07d/attempt-2-services/grade.json"}, {"lane": "electron", "passed": true, "evidence": "/Users/ashah/Documents/GitHub/learn-harness-engineering/forge/local-results/graph-qualification-74896eb2-b69a-4e53-be6c-44a010bbf07d/attempt-2-electron/grade.json"}]}, {"file": "project-08-control-flow-qualification-7cbcac1f-849c-4b2a-affb-04f142ae03fb.json", "schemaVersion": 1, "id": "7cbcac1f-849c-4b2a-affb-04f142ae03fb", "sourceCommit": "e76a8dfa984116bbab4b8c31570da13b11daf87e", "node": "approval", "attempts": 2, "maxAttempts": 2, "transitions": [{"from": "plan", "to": "make", "at": "2026-11-06T13:08:05.457Z", "reason": "frozen task acceptance criteria"}, {"from": "make", "to": "verify", "at": "2026-11-06T13:08:28.517Z", "reason": "candidate patch exported"}, {"from": "verify", "to": "rollback", "at": "2026-11-06T13:08:46.718Z", "reason": "protected grade and independent parallel verification results"}, {"from": "rollback", "to": "make", "at": "2026-11-06T13:08:46.720Z", "reason": "restore last verified patch or frozen baseline"}, {"from": "make", "to": "verify", "at": "2026-11-06T13:09:08.907Z", "reason": "candidate patch exported"}, {"from": "verify", "to": "approval", "at": "2026-11-06T13:09:28.125Z", "reason": "protected grade and independent parallel verification results"}], "qualification": "deterministic control-flow fixture; excluded from coding trial counts", "plan": "Verify the seeded baseline fails, rollback, verify a documented manual repair, then pause for a human decision.", "candidate": {"patch": "/Users/ashah/Documents/GitHub/learn-harness-engineering/forge/local-results/graph-qualification-7cbcac1f-849c-4b2a-affb-04f142ae03fb/candidate-2.diff", "sha256": "91c4a2df7b9a65921c221b68bc86cdd40db4d5945fce16510206a405ac7516e6", "trialId": "fixture-2", "protectedGrade": {"passed": true, "evidence": "/Users/ashah/Documents/GitHub/learn-harness-engineering/forge/local-results/graph-qualification-7cbcac1f-849c-4b2a-affb-04f142ae03fb/attempt-2-protected/grade.json"}}, "verification": [{"lane": "services", "passed": true, "evidence": "/Users/ashah/Documents/GitHub/learn-harness-engineering/forge/local-results/graph-qualification-7cbcac1f-849c-4b2a-affb-04f142ae03fb/attempt-2-services/grade.json"}, {"lane": "electron", "passed": true, "evidence": "/Users/ashah/Documents/GitHub/learn-harness-engineering/forge/local-results/graph-qualification-7cbcac1f-849c-4b2a-affb-04f142ae03fb/attempt-2-electron/grade.json"}], "lastProtectedGrade": {"passed": true, "evidence": "/Users/ashah/Documents/GitHub/learn-harness-engineering/forge/local-results/graph-qualification-7cbcac1f-849c-4b2a-affb-04f142ae03fb/attempt-2-protected/grade.json"}}, {"file": "project-08-control-flow-qualification.json", "schemaVersion": 1, "id": "6fcc2091-f526-45e0-8fb1-aa0c1802aae5", "sourceCommit": "f3dc2cf8e55a3a58cb9d7f476d04c985fded0261", "node": "approval", "attempts": 2, "maxAttempts": 2, "transitions": [{"from": "plan", "to": "make", "at": "2026-11-06T08:54:12.691Z", "reason": "frozen task acceptance criteria"}, {"from": "make", "to": "verify", "at": "2026-11-06T08:54:12.694Z", "reason": "candidate patch exported"}, {"from": "verify", "to": "rollback", "at": "2026-11-06T08:54:52.871Z", "reason": "independent parallel verification results"}, {"from": "rollback", "to": "make", "at": "2026-11-06T08:54:52.877Z", "reason": "restore last verified patch or frozen baseline"}, {"from": "make", "to": "verify", "at": "2026-11-06T08:54:52.883Z", "reason": "candidate patch exported"}, {"from": "verify", "to": "approval", "at": "2026-11-06T08:55:34.037Z", "reason": "independent parallel verification results"}], "qualification": "deterministic control-flow fixture; excluded from coding trial counts", "plan": "Verify the seeded baseline fails, rollback, verify a documented manual repair, then pause for a human decision.", "candidate": {"patch": "/Users/ashah/Documents/GitHub/learn-harness-engineering/forge/local-results/graph-qualification-6fcc2091-f526-45e0-8fb1-aa0c1802aae5/candidate-2.diff", "sha256": "91c4a2df7b9a65921c221b68bc86cdd40db4d5945fce16510206a405ac7516e6", "trialId": "fixture-2"}, "verification": [{"lane": "services", "passed": true, "evidence": "/Users/ashah/Documents/GitHub/learn-harness-engineering/forge/local-results/graph-qualification-6fcc2091-f526-45e0-8fb1-aa0c1802aae5/attempt-2-services/grade.json"}, {"lane": "electron", "passed": true, "evidence": "/Users/ashah/Documents/GitHub/learn-harness-engineering/forge/local-results/graph-qualification-6fcc2091-f526-45e0-8fb1-aa0c1802aae5/attempt-2-electron/grade.json"}]}, {"file": "project-08-graph-contract.json", "schemaVersion": 1, "id": "c98b8bdc-0464-4661-b5ac-fb95b1954d31", "sourceCommit": "24ff7909edb286b0e66faae1d78968d12aac6c0c", "node": "approval", "attempts": 3, "maxAttempts": 3, "transitions": [{"from": "plan", "to": "make", "at": "2026-11-06T12:58:17.198Z", "reason": "frozen task acceptance criteria"}, {"from": "make", "to": "verify", "at": "2026-11-06T13:01:59.242Z", "reason": "candidate patch exported"}, {"from": "verify", "to": "rollback", "at": "2026-11-06T13:02:24.784Z", "reason": "protected grade and independent parallel verification results"}, {"from": "rollback", "to": "make", "at": "2026-11-06T13:02:24.787Z", "reason": "restore last verified patch or frozen baseline"}, {"from": "make", "to": "verify", "at": "2026-11-06T13:04:14.669Z", "reason": "candidate patch exported"}, {"from": "verify", "to": "rollback", "at": "2026-11-06T13:04:39.183Z", "reason": "protected grade and independent parallel verification results"}, {"from": "rollback", "to": "make", "at": "2026-11-06T13:04:39.185Z", "reason": "restore last verified patch or frozen baseline"}, {"from": "make", "to": "verify", "at": "2026-11-06T13:07:02.138Z", "reason": "candidate patch exported"}, {"from": "verify", "to": "approval", "at": "2026-11-06T13:07:19.499Z", "reason": "protected grade and independent parallel verification results"}], "plan": "Deliver a patch for the knowledge-base app: repair long-document empty chunks, preserve all text, produce source-grounded citations, and make the Electron window and typed preload bridge work. Add scripts/check-architecture.sh that rejects Node imports in the renderer. Verify actual service and UI behavior. Your patch will be checked independently and paused for human approval before being accepted.", "candidate": {"patch": "/Users/ashah/.codex/worktrees/forge-graph-qualified-coordinator/learn-harness-engineering/forge/local-results/03ca01ca-eb64-45ae-9317-824ca4a26026/candidate.diff", "sha256": "c74cf9cf37169db868996c2aa5328a527377a0c8656678d874edb4a0195c96d3", "trialId": "03ca01ca-eb64-45ae-9317-824ca4a26026", "protectedGrade": {"passed": true, "evidence": "/Users/ashah/.codex/worktrees/forge-graph-qualified-coordinator/learn-harness-engineering/forge/local-results/03ca01ca-eb64-45ae-9317-824ca4a26026/trial.json"}}, "verification": [{"lane": "services", "passed": true, "evidence": "/Users/ashah/.codex/worktrees/forge-graph-qualified-coordinator/learn-harness-engineering/forge/local-results/graph-5a3c475a-3852-4854-ba3b-ecaf7cf23dd1/grade.json"}, {"lane": "electron", "passed": true, "evidence": "/Users/ashah/.codex/worktrees/forge-graph-qualified-coordinator/learn-harness-engineering/forge/local-results/graph-40688e0f-33dd-4a53-bdf5-cdebec3c469b/grade.json"}], "lastProtectedGrade": {"passed": true, "evidence": "/Users/ashah/.codex/worktrees/forge-graph-qualified-coordinator/learn-harness-engineering/forge/local-results/03ca01ca-eb64-45ae-9317-824ca4a26026/trial.json"}}, {"file": "project-08-graph-diagnostic-feedback.json", "schemaVersion": 1, "id": "f80a2c7d-2749-419e-8912-ba471a184679", "sourceCommit": "3ebea13e260921c0c231ff43b6d13bc265d25157", "node": "failed", "attempts": 3, "maxAttempts": 3, "transitions": [{"from": "plan", "to": "make", "at": "2026-11-06T09:05:19.241Z", "reason": "frozen task acceptance criteria"}, {"from": "make", "to": "verify", "at": "2026-11-06T09:09:28.374Z", "reason": "candidate patch exported"}, {"from": "verify", "to": "rollback", "at": "2026-11-06T09:09:57.888Z", "reason": "independent parallel verification results"}, {"from": "rollback", "to": "make", "at": "2026-11-06T09:09:57.889Z", "reason": "restore last verified patch or frozen baseline"}, {"from": "make", "to": "verify", "at": "2026-11-06T09:12:43.686Z", "reason": "candidate patch exported"}, {"from": "verify", "to": "rollback", "at": "2026-11-06T09:15:25.997Z", "reason": "independent parallel verification results"}, {"from": "rollback", "to": "make", "at": "2026-11-06T09:15:26.001Z", "reason": "restore last verified patch or frozen baseline"}, {"from": "make", "to": "verify", "at": "2026-11-06T09:18:52.160Z", "reason": "candidate patch exported"}, {"from": "verify", "to": "rollback", "at": "2026-11-06T09:19:43.061Z", "reason": "independent parallel verification results"}, {"from": "rollback", "to": "failed", "at": "2026-11-06T09:19:43.064Z", "reason": "restore last verified patch or frozen baseline"}], "plan": "Deliver a patch for the knowledge-base app: repair long-document empty chunks, preserve all text, produce source-grounded citations, and make the Electron window and typed preload bridge work. Add an architecture check that rejects Node imports in the renderer. Verify actual service and UI behavior. Your patch will be checked independently and paused for human approval before being accepted.", "verification": [{"lane": "services", "passed": false, "evidence": "/Users/ashah/Documents/GitHub/learn-harness-engineering/forge/local-results/graph-bc1dd79b-44b3-425e-8e68-b81cea815635/grade.json"}, {"lane": "electron", "passed": false, "evidence": "/Users/ashah/Documents/GitHub/learn-harness-engineering/forge/local-results/graph-d2f43853-7138-48a1-a20e-fde85aae76b4/grade.json"}]}, {"file": "project-08-graph-live.json", "schemaVersion": 1, "id": "5f15fb08-0def-4907-a129-610511f9708b", "sourceCommit": "8f4521bc34bb340dd4aa75e5bf1a6e6c49a68bef", "node": "failed", "attempts": 3, "maxAttempts": 3, "transitions": [{"from": "plan", "to": "make", "at": "2026-11-06T08:39:25.613Z", "reason": "frozen task acceptance criteria"}, {"from": "make", "to": "verify", "at": "2026-11-06T08:43:24.478Z", "reason": "candidate patch exported"}, {"from": "verify", "to": "rollback", "at": "2026-11-06T08:44:10.386Z", "reason": "independent parallel verification results"}, {"from": "rollback", "to": "make", "at": "2026-11-06T08:44:10.455Z", "reason": "restore last verified patch or frozen baseline"}, {"from": "make", "to": "verify", "at": "2026-11-06T08:49:34.578Z", "reason": "candidate patch exported"}, {"from": "verify", "to": "rollback", "at": "2026-11-06T08:50:09.172Z", "reason": "independent parallel verification results"}, {"from": "rollback", "to": "make", "at": "2026-11-06T08:50:09.174Z", "reason": "restore last verified patch or frozen baseline"}, {"from": "make", "to": "verify", "at": "2026-11-06T08:52:28.047Z", "reason": "candidate patch exported"}, {"from": "verify", "to": "rollback", "at": "2026-11-06T08:53:18.720Z", "reason": "independent parallel verification results"}, {"from": "rollback", "to": "failed", "at": "2026-11-06T08:53:18.724Z", "reason": "restore last verified patch or frozen baseline"}], "plan": "Deliver a patch for the knowledge-base app: repair long-document empty chunks, preserve all text, produce source-grounded citations, and make the Electron window and typed preload bridge work. Add an architecture check that rejects Node imports in the renderer. Verify actual service and UI behavior. Your patch will be checked independently and paused for human approval before being accepted.", "verification": [{"lane": "services", "passed": false, "evidence": "/Users/ashah/.codex/worktrees/forge-experiment-coordinator/learn-harness-engineering/forge/local-results/graph-4df81aba-2c93-4281-8c74-197958708351/grade.json"}, {"lane": "electron", "passed": false, "evidence": "/Users/ashah/.codex/worktrees/forge-experiment-coordinator/learn-harness-engineering/forge/local-results/graph-1155be34-4b89-4534-911a-dd47c22e322a/grade.json"}]}, {"file": "project-08-graph-qualified.json", "schemaVersion": 1, "id": "1f44f07b-e4d2-4085-829f-0a9013c72f68", "sourceCommit": "945c5d3073026a4fea427372843ea79072221dde", "node": "failed", "attempts": 3, "maxAttempts": 3, "transitions": [{"from": "plan", "to": "make", "at": "2026-11-06T12:48:42.566Z", "reason": "frozen task acceptance criteria"}, {"from": "make", "to": "verify", "at": "2026-11-06T12:51:14.871Z", "reason": "candidate patch exported"}, {"from": "verify", "to": "rollback", "at": "2026-11-06T12:51:35.692Z", "reason": "protected grade and independent parallel verification results"}, {"from": "rollback", "to": "make", "at": "2026-11-06T12:51:35.694Z", "reason": "restore last verified patch or frozen baseline"}, {"from": "make", "to": "verify", "at": "2026-11-06T12:54:16.221Z", "reason": "candidate patch exported"}, {"from": "verify", "to": "rollback", "at": "2026-11-06T12:54:44.713Z", "reason": "protected grade and independent parallel verification results"}, {"from": "rollback", "to": "make", "at": "2026-11-06T12:54:44.714Z", "reason": "restore last verified patch or frozen baseline"}, {"from": "make", "to": "verify", "at": "2026-11-06T12:57:27.818Z", "reason": "candidate patch exported"}, {"from": "verify", "to": "rollback", "at": "2026-11-06T12:57:45.169Z", "reason": "protected grade and independent parallel verification results"}, {"from": "rollback", "to": "failed", "at": "2026-11-06T12:57:45.171Z", "reason": "restore last verified patch or frozen baseline"}], "plan": "Deliver a patch for the knowledge-base app: repair long-document empty chunks, preserve all text, produce source-grounded citations, and make the Electron window and typed preload bridge work. Add an architecture check that rejects Node imports in the renderer. Verify actual service and UI behavior. Your patch will be checked independently and paused for human approval before being accepted.", "verification": [{"lane": "services", "passed": false, "evidence": "/Users/ashah/.codex/worktrees/forge-graph-qualified-coordinator/learn-harness-engineering/forge/local-results/graph-4bc5a5cd-8b91-405c-9b52-2e663fe96d65/grade.json"}, {"lane": "electron", "passed": true, "evidence": "/Users/ashah/.codex/worktrees/forge-graph-qualified-coordinator/learn-harness-engineering/forge/local-results/graph-577d6b8a-6bf2-424d-9682-41e28d025da1/grade.json"}], "lastProtectedGrade": {"passed": false, "evidence": "/Users/ashah/.codex/worktrees/forge-graph-qualified-coordinator/learn-harness-engineering/forge/local-results/54bb7391-48b0-47f5-9ded-36194f52a76d/trial.json"}}], "budget": {"schemaVersion": 1, "limitUsd": null, "spentEstimateUsd": 19.001973120000017, "reservations": {}, "settled": {"qualification-17b194af-b3ef-4d47-95cc-178676315b60": 0.003, "qualification-af9192de-dfe3-4631-934e-37729c2a4d56": 0.010988719333333332, "qualification-ed8a8028-bb60-4eff-a678-e5e74e94d2cc": 0.004988329333333333, "ace2d466-a1f6-4998-bb1c-130618b52651": 0.010633104666666665, "qualification-1c68ebdf-feba-4158-8192-d5be5b3e2a98": 2, "qualification-19560d68-131a-4318-8dd8-ed73a1219d2e": 0.0047544779999999995, "362291eb-95fb-4738-bb3e-225d4d2cca9b": 0.09284877866666667, "68bb08fa-4f9b-42af-9232-dd7e50da8414": 0.10960137866666667, "1916807d-73a5-4d64-8444-0d4301c5c3fa": 0.1191367, "edd880ec-d379-4c91-8f32-6037f1001a94": 0.11645551200000001, "c8a5365b-8cfa-4566-b28e-6577ce081948": 0.10871942466666666, "2e7a67cd-96cb-46e0-92d5-1099b69ea31b": 0.06132203533333333, "174cab45-166d-42e2-b60d-4fe6d7d1916e": 0.10383150466666666, "a023c020-433a-42db-84c7-9288ae55ac21": 0.09555698533333333, "bd070321-5fd7-45b6-940b-157df5f3b512": 0.08383703733333332, "notebook-15313-editor-1": 0.06123702666666666, "745b1def-40ac-4900-96c9-b189c6b2e6f0": 0.08479798733333334, "aac13172-183d-49ee-b15c-514b2eb552ed": 0.086645138, "18e9a4d0-fd46-4848-a174-e059c11ffe09": 0.09487573066666666, "9b862fb6-9f2a-4f12-8084-3419e33db29f": 0.06312064466666667, "051868b4-ba7f-4727-acd6-7265657fb2c9": 0.09934614866666666, "9502dff3-7f5a-4b62-a067-e2d884ddfa21": 0.08551259, "4d83ad1a-8ff8-4923-8605-eb7693603f8a": 0.12516100133333333, "concurrency-61ad1e33-0ede-46ff-b513-1a700e9798ce": 0.00214675, "3bf22b16-6480-4721-820a-0aaaf70155be": 0.07821951199999999, "03707b50-d426-4961-b8e3-522d7f674f6c": 0.09086439266666665, "05beeb69-67d8-4b7a-b47b-ec8bfe2ab6ae": 0.08657200533333334, "b7f85e4f-b18a-473f-8e71-32dced0e282b": 0.08104619466666667, "1e7c395e-243b-4ca2-856c-c72dc8a7968b": 0.078047814, "f444fd47-b470-4986-8d41-a6aafc97e7fd": 0.06749585266666666, "224d57f1-4850-49a9-bd6c-47061d8d9d3d": 0.080031782, "3db63440-2515-400f-87d9-f742a5d72925": 0.07326100266666667, "ea29fe78-55f5-407b-9076-0bccb6e8f2e2": 0.06903174266666666, "532b1822-b26a-438f-ba4f-3f6f30bcf837": 0.09327494933333333, "b6c3da9e-7fd8-474b-a79c-19cbbc62e5ba": 0.08953384933333333, "ea192f25-ea5e-4a06-b166-8b136156f040": 0.11259213266666668, "df2cdaca-e25b-4635-a687-e7198bed6f51": 0.0037488946666666663, "9a9d742f-a43a-43fe-95bc-d5290a6c07c5": 0.00433668, "eb9e30d3-5101-4b49-91cf-23ff1aae392a": 0.06654817333333334, "f02c6078-1953-4544-bcc0-f877c849f6d7": 0.078776972, "adda1977-924d-4adb-9bb7-250219b5d2be": 0.10302612733333333, "f6ae2a06-3a5e-4cf0-88c4-80a2b0b03c2b": 0.08430663799999999, "1d01f434-8b00-48e2-bac3-83a0d514c5cc": 0.0014785986666666666, "d894c72d-12ad-4cb4-93ee-133f958fdb41": 0.0032740466666666664, "34290474-83eb-4792-9368-096c0ae83df0": 0.07926355, "7eb6c8d1-896c-49ab-bfc3-fd4c1fd230c0": 0.09184524533333333, "287d745e-ca9f-49c1-bbf4-46048cc6dff9": 0.09711906666666667, "1155be34-4b89-4534-911a-dd47c22e322a": 0.002634384, "4df81aba-2c93-4281-8c74-197958708351": 0.004796665333333333, "5ffb5a34-8a2f-4c05-8f57-989b8e771374": 0.0022277906666666666, "fb58d0b1-4b1d-4f62-bc48-9c07f91d8df1": 0.0038028546666666664, "d007e5a8-749c-4610-9294-2ecb5e35174c": 0.001699172, "7044390c-06be-4cd7-ae30-9b063600ead1": 0.05652102, "4cb6d584-ecfc-4f41-a0f3-86a1bdcf3556": 0.08113195200000001, "29ff179d-b736-44f4-8b0a-7e064b4491f8": 0.0038955333333333332, "sandbox-qualification-f566ddc3-297f-4483-98a8-47c6d15a402c-interrupt": 0, "sandbox-qualification-f566ddc3-297f-4483-98a8-47c6d15a402c-resume": 0, "304a61f2-46ea-442c-a1bd-d0ac41a6c21d": 0.0013523133333333333, "3f742e3b-8f37-49bd-bfb5-d55ac89bed80": 0.061650915333333334, "3458c1a0-5de4-416b-81a9-1757d2093ef1": 0, "37ec7440-8567-4905-a12d-e1b7912474b1": 0.08172274133333333, "86cc7a68-d9b8-42b7-abb6-735c757a1ebc": 0.05882531866666667, "eaf9902f-f9a9-48c6-b832-c245b12404f7": 0.061622868666666664, "c0fbc6d2-2c3a-4337-82cf-6fa25e5c7403": 0.006286056, "40a0261f-7f59-4c1d-982e-8632252a65b3": 0.0010443626666666666, "fd1411d4-3aee-47ed-a788-5007df5047e2": 0.06744222866666667, "2ca8dcd3-e132-4296-8755-e9722cfa003b": 0.06827620133333334, "41593b90-6493-4ab7-a001-1dc24878eeb0": 0.08399786066666667, "c0f6a4ba-cfcf-47c4-aded-3d06efa982d3": 0.096558856, "f06b8818-6754-4f4e-8f7f-d36107665dc7": 0.0014403533333333333, "ea2d89fd-a929-4bbd-a582-e6838e19523d": 0.0027935186666666664, "c64948bf-1452-41af-b95f-58648e67e496": 0.07752370866666666, "46f51f6a-b922-42e0-bb94-854421e9209c": 0.09722744866666666, "6d90a4b6-a012-4cc8-9d8c-79846c6dec22": 0.06298989066666666, "5b0bb0d1-9ccc-484c-a021-23f8b2a92f30": 0.013786022666666668, "410489a4-7e8f-4473-9750-139c3bffd8ce": 0.015363832000000001, "8bdd0310-17ca-4722-a527-b2960d08ef3b": 0.09775738733333333, "dae011e2-5055-4a64-ad78-460ec8bac773": 0.09565158, "fbbb858f-935a-4281-b07d-1f4fb984e252": 0.09070795866666667, "d2f43853-7138-48a1-a20e-fde85aae76b4": 0.0025032706666666665, "bc1dd79b-44b3-425e-8e68-b81cea815635": 0.00481806, "ac047ec9-ebbc-43f8-8f21-5d47a2cb93e3": 0.10110698933333334, "11500f73-bc29-4c22-83f4-1e95f0a9abd1": 0.06954726466666666, "e375487d-4743-4f01-8c68-2e4aea50edd8": 0.080974124, "98c21d2f-01ff-4684-a3c8-dd50f9e795d8": 0.08554729866666667, "notebook-15314-editor-1": 0, "3ceefbaf-7a49-4191-9c8a-3b4a39f779ed": 0.06384134333333333, "ca2a84d5-44c1-47da-8f29-151fbc8a9475": 0.06783366533333333, "notebook-15314-editor-2": 0.08099254, "notebook-15314-editor-3": 0.02370623733333333, "notebook-15315-editor-1": 0.03206378933333333, "bc00b68c-a28a-4b94-89d7-81539505e165": 0.10494891066666667, "notebook-15316-editor-1": 0.039289033333333334, "notebook-15317-editor-1": 0.03926849066666667, "notebook-15318-editor-1": 0.03842378, "notebook-15319-editor-1": 0.041706157333333334, "notebook-15321-editor-1": 0.043352978666666674, "notebook-15320-editor-1": 0.03871421733333333, "notebook-15313-editor-2": 0.06194674266666666, "qualification-37a4f9ea-2162-45a1-8322-82c1e5259a02": 2, "qualification-cff12c5e-6a23-4d3b-a138-f1961945be14": 2, "qualification-e30ebcea-2c57-4e73-99cc-9b9b10c0f82f": 0.00512862, "ca53b79e-eab4-4b69-8c1e-072c2baff44f": 0.14421109799999998, "b043a7b3-1843-4914-af0b-0504623b1059": 0.129465934, "visible-ui-e493a2f0-5475-4ad9-8e2f-fcfb48c75ec9": 0.018997517333333335, "97cb6fd5-7fd6-466c-b5f1-598126cf2d52": 0.12316753666666667, "d52e75ef-81cb-4fc0-b551-0884405ad2c1": 0.10617438066666667, "visible-ui-56f1ef46-deba-48b8-8bc4-8b2169169b55": 0.003847821333333333, "qualification-2ebe0500-a0d6-47dc-b3ae-b4ef8ba988ff": 0.004789874666666666, "813076fb-3550-4e34-a3a3-831c7ed43f14": 0.10724251400000001, "20e034ff-32bc-4225-8416-044011f5f68d": 0.08327558333333332, "71581d99-5fb7-4e57-bee4-56ec354858a2": 0.15087467266666665, "643a867a-74e8-4987-aa56-5640b4c1982e": 0.139101264, "6260ba09-aa6d-4529-83b5-066df4a23a9e": 0.007807444, "8c43a910-9c22-4ac1-af63-613f12cc8ba2": 0.009347576, "c121b6fe-8826-451c-87d4-6a870ba54fbd": 0.0014941239999999999, "e53c3cad-a475-4e49-a79c-e64cfc0316a9": 0.056398679333333326, "a7dcf5cb-dd20-4c3f-921b-f8a51a21f8f8": 0.11957918066666667, "246ff80a-d14b-403a-9ecb-81f2c90fa404": 0.003924028, "3398c0d0-a9f2-4383-b64f-c7469ff9d0df": 0.14776984733333334, "a09c89fc-d730-4e6c-980c-62b4e7d4993e": 0.116543516, "b394d28a-ebed-4aba-9566-61d6cc5dbedf": 0.098560644, "6e00cd09-8cfb-495e-ab90-dc16c7938030": 0.08907325733333332, "notebook-15314-editor-4": 0.016457799999999998, "ec18a893-0de1-44ac-8541-7f1564e1e8d4": 0.08954740466666666, "22873518-2d13-475d-ba37-7b9e94c48407": 0.09839233533333333, "6aeae35a-525b-448d-93eb-469a22e6cedf": 0.09475115266666667, "64419d93-5073-4632-bff0-8ccd75f2e21f": 0.090931016, "54b81e30-0be0-470e-ab3c-2a3783ead0f5": 0.07664293666666668, "1500360a-62ce-42cf-aa87-c82962c43655": 0.08375966866666668, "d5a939ba-ee04-422d-a681-0322111156a1": 0.09202667266666667, "9d859517-72db-4b1a-a683-cd81b9f7ca14": 0.07956944466666667, "22fa3879-a8ff-4219-847c-c5972efedf78": 0.07049977866666667, "0809587e-cc59-4276-8285-02dc5072f2aa": 0.06192300666666667, "9c2869e2-d150-4c35-82df-9602ca48f17b": 0.110878108, "0865dc24-2666-4fda-b6ae-3f488f5339cb": 0.12874192133333334, "fadf2407-4ef3-4635-bab7-0a8d987096d8": 0.14088486333333333, "1b0a25e5-ba13-4931-9c4f-ff6100f6672a": 0.10046582266666666, "9feeffa8-1836-485a-a52c-2b398b40a195": 0.12556704133333335, "bdc971f7-1a51-437d-b46a-8ed3c268eb97": 0.12889706533333334, "notebook-15315-editor-2": 0.060377926666666665, "b6969def-4dd9-4763-8b73-6de7cdcb59c2": 0.07337922933333334, "3b7cd608-2c28-4cb8-9d4f-aeb60ac3bc7a": 0.06969865533333333, "70336779-611e-48d8-839d-7e92aa1f63cb": 0.057835604, "notebook-15316-editor-2": 0.01588696, "df461eac-d90b-489e-a230-1ecc20511585": 0.064428758, "0c88671b-326d-4c20-b1b9-aaf95782c93c": 0.057479944666666664, "history-diagnostic-5410a71b-9980-4ad4-bc47-98e3df5b1f22": 0.003229932, "66558826-6e1a-46e0-abe9-ef951eff0c16": 0.056296415333333336, "cf87ff44-3f71-4ade-8f50-eaeb048b968a": 0.05308981333333333, "a2d447ed-75a6-4477-9308-e8eb60885b2b": 0.046166620000000005, "history-diagnostic-e8a1ea54-0fe5-4ba8-9929-76b07e2b5e29": 0.011016549333333334, "notebook-15317-editor-2": 0.044258370666666665, "5609c89b-f73f-4a9e-8702-a57758c3403c": 0.06756080333333334, "f6edbfa3-3682-4e3b-bff2-ba4b864e2511": 0.07249340800000001, "216527fa-6ff5-4cde-a203-696bb1e57f06": 0.17794718533333334, "checker-diagnostic-57f14e90-d62e-4fcb-ab78-60b52a12935a": 0.010578147999999999, "dd818c1d-aea4-4e7f-b2a2-a6398ac33877": 0.15102145933333333, "1c1228c9-2625-4256-9aa2-694d37def359": 0.13751677666666667, "0173b789-396b-4a83-922a-644c172ff4f4": 0.15151933466666667, "534ab4c7-9100-4d94-a379-fbfc4ad381c7": 0.16611393600000002, "39c8c943-15bf-4d53-a99e-aaa4cd9ff5a3": 0.060162492, "aff27d56-36a4-4cb0-a2f4-f86301f1dc68": 0.13397646, "44762357-664b-4d30-b390-8121b6d51b07": 0.05600771266666667, "checker-diagnostic-de8f9f04-3fa4-4332-b3a5-03f5fdf57808": 0.002372725333333333, "checker-diagnostic-d3c1c8a4-481f-4d17-b794-38f69702c9dc": 0.002311286666666667, "f5e5ab53-b1b4-4d70-af9d-5fb31516bd39": 0.14216638333333334, "3dd7e4f8-1155-4ffa-9da5-98c82c24c087": 0.06299844266666667, "bf9e17a2-c6a5-4a8d-b1d2-ccdff10121a3": 0.07121940066666665, "58ac2e5b-4ee4-4313-bbbd-4022117855bb": 0.053777083333333336, "73c46965-1093-4b68-a810-a901dd78bfc0": 0.08002206133333334, "ef04c221-aafe-4134-b9fc-0268fab0427f": 0.060202278666666664, "33bdfb7f-4f5e-49b8-86c8-92d6ce0e7b0b": 0.09126634533333333, "notebook-15320-editor-2": 0.047541978666666665, "79398b0b-a9eb-4892-bb24-194bdc289e2f": 0.06081800466666667, "d3ef30ab-0f2c-4d0e-aee1-7bdf6a8a011e": 0.048149267333333336, "ca16eac7-0eb5-4523-a975-638e30938a04": 0.06884904133333333, "1fb04273-5ca5-4a79-9a9d-686149623068": 0.060350619333333334, "fd98af3b-1b52-448c-bc7b-b6cc47e785ea": 0.13405509399999999, "notebook-15318-editor-2": 0.01391032, "a7bc0271-d547-4534-a15d-27b70072df40": 0.159469046, "0cb15597-b43e-4295-985b-af7ea9c1454a": 0.176008926, "b8f56d80-c72c-4e31-8c88-f8fc63d76f9a": 0.15079331799999998, "4eb48651-306d-44e9-a468-a6ffc322bf27": 0.14693331066666668, "fc80b4f3-6178-454f-a003-3e311dab6617": 0.12121640866666666, "f496d257-3de4-4507-a7d6-1d2d4f4d9a92": 0.0015263106666666667, "983ba1bb-86da-4900-a452-e80c2959390d": 0.001970770666666667, "notebook-15319-editor-2": 0.016575470666666665, "22955029-2de6-4aed-8c35-dda6059b023d": 0.12844285333333333, "f0da5cdf-bad6-4e14-a246-74621916258d": 0.0016541106666666664, "9ba0b694-69e2-45b6-ba8c-7826bc409a6f": 0.0026969586666666665, "54bb7391-48b0-47f5-9ded-36194f52a76d": 0.119441758, "4bc5a5cd-8b91-405c-9b52-2e663fe96d65": 0.001445276, "577d6b8a-6bf2-424d-9682-41e28d025da1": 0.0016421826666666666, "3e5cd770-94e5-49f9-b478-a2043dc9a682": 0.11798033866666667, "5c57b1db-4921-4284-aa8b-8b543fc64e43": 0.002244452, "e80b044a-800d-445e-a88e-ae1a0ba74bdd": 0.0024175973333333332, "43ad509b-7eb5-4d9e-97c7-ff33567693fd": 0.11004467866666667, "acf47e37-0067-4e43-8263-2b772e48e893": 0.0013801453333333335, "02884945-e798-4762-9f50-90ada6ec5ec5": 0.0023203746666666664, "03ca01ca-eb64-45ae-9317-824ca4a26026": 0.10332285, "5a3c475a-3852-4854-ba3b-ecaf7cf23dd1": 0.0015864239999999997, "40688e0f-33dd-4a53-bdf5-cdebec3c469b": 0.0016433186666666667, "875c7e96-9dc7-4aac-9000-399f494d4095": 0.0021821613333333333, "09e89bda-2798-4369-be31-e64e7374fc58": 0.0015804600000000001, "e165e08f-88b0-450b-9a76-667718a225a5": 0.001722744, "ff73108e-9088-432b-bc7c-a4113e3ddf3a": 0.0020997066666666665, "9e0d9f9c-86a4-4f75-8277-50a33537ba22": 0.0015203466666666666, "27b7d785-a76b-4cf7-aa76-091201325343": 0.001818925333333333}, "reconciliations": [{"id": "qualification-17b194af-b3ef-4d47-95cc-178676315b60", "estimatedUsd": 0.003, "evidence": "qualification.json ended at the cancellation probe before runPi; sandbox/sandbox.json confirms terminated. Charge conservative 32 seconds at 2 CPU + 4 GiB ($0.3408/hour), rounding upward. No inference launched.", "at": "2026-11-06T07:32:03.996Z"}, {"id": "qualification-af9192de-dfe3-4631-934e-37729c2a4d56", "estimatedUsd": 0.010988719333333332, "evidence": "Both agent and app calls completed with returned token usage. Sandbox journal confirms terminated. Original accounting rejected metadata keys rather than missing billable rates. This estimate conservatively bills the entire qualification wall-clock duration as sandbox time, including app inference after termination.", "at": "2026-11-06T07:34:24.698Z"}, {"id": "ace2d466-a1f6-4998-bb1c-130618b52651", "estimatedUsd": 0.010633104666666665, "evidence": "All eight submitted model calls returned usage (actor/phase-1.json and tool logs). The ninth attempt was refused locally before the provider due to the frozen input-byte guard. Both actor and grader sandbox journals confirm termination. Preserve the original telemetry_missing attempt; this audited estimate reclassifies only its billing uncertainty.", "at": "2026-11-06T07:41:23.512Z"}, {"id": "sandbox-qualification-f566ddc3-297f-4483-98a8-47c6d15a402c-interrupt", "estimatedUsd": 0, "evidence": "Pinned cwsandbox 1.0.0 client validates sandbox tags before transport.start (grpc-transport-DlmDQLSO.js lines 2108-2114 and 533). The 64-character tag was rejected locally; no create request or inference was sent. Original failed qualification is preserved. Resume phase was never reached.", "at": "2026-11-06T08:57:06.638Z"}], "authorizations": [{"at": "2026-11-06T08:09:55.199Z", "evidence": "User answered \\"unlimited budget\\" to the explicit question about charging the full $2 reservation and continuing experiments and notebook publication.", "action": "Remove spending cap; retain accounting and bounded execution"}], "uncertainEstimates": [{"id": "qualification-1c68ebdf-feba-4158-8192-d5be5b3e2a98", "reservedEstimateUsd": 2, "evidence": "User authorized continued paid work with unlimited budget; charge the full $2 reservation conservatively. Actual token usage remains unknown and the original failed qualification is unchanged.", "at": "2026-11-06T08:09:55.202Z"}, {"id": "qualification-37a4f9ea-2162-45a1-8322-82c1e5259a02", "reservedEstimateUsd": 2, "evidence": "Existing user authorization: unlimited budget in response to retaining full reservations for timed-out inference and continuing experiments. Retain this additional full 2 USD reservation; actual app token usage remains unknown. Original failed attempt and terminated sandbox journal are preserved.", "at": "2026-11-06T10:41:47.979Z"}, {"id": "qualification-cff12c5e-6a23-4d3b-a138-f1961945be14", "reservedEstimateUsd": 2, "evidence": "Existing unlimited-budget user authorization permits retaining full reservations for timed-out inference while continuing. Retain the full 2 USD reservation; app token usage remains unknown. Original failed qualification preserved.", "at": "2026-11-06T10:44:23.710Z"}]}, "costScope": "Budget snapshot as of capturedAt. Final publication/editor costs are recorded separately in the delivery report and W&B audit artifact.", "visibleUiQualifications": [{"schemaVersion": 1, "id": "visible-ui-56f1ef46-deba-48b8-8bc4-8b2169169b55", "sourceCommit": "30db3581757e79b9791b1b70262e6ac499fab87f", "trialId": "b043a7b3-1843-4914-af0b-0504623b1059", "candidateSourceCommit": "7c563eb14f3999ab3e659b77c4095c883619002f", "candidateSha256": "5ee2a7eef6c7d52f05cf52f664db5151226586c1ac9821c69ba7023b3c359b5a", "startedAt": "2026-11-06T10:59:57.147Z", "passed": true, "qualification": true, "checkerSha256": "0c1c629ec8a0211b5432193cbc6e7584dda5a94ae6e2d8f8faee74845ef08f66", "sandboxId": "0c14919f-53fb-4d0e-9995-0c367decf45c", "grade": {"schemaVersion": 1, "task": "project-01", "checks": [{"name": "strict compile and renderer build", "passed": true}, {"name": "real import and persistence after reconstruction", "passed": true}, {"name": "actual indexing keeps every nonempty paragraph", "passed": true}, {"name": "actual retrieval and Q&A persist two turns", "passed": true}, {"name": "Electron window, preload, import, indexing and question UI under Xvfb", "passed": true}], "passed": true}, "estimatedCostUsd": 0.003847821333333333, "finishedAt": "2026-11-06T11:00:38.643Z"}, {"schemaVersion": 1, "id": "visible-ui-e493a2f0-5475-4ad9-8e2f-fcfb48c75ec9", "sourceCommit": "71b172121b15a7625e48bae9007b7b38551f9a07", "trialId": "b043a7b3-1843-4914-af0b-0504623b1059", "candidateSourceCommit": "7c563eb14f3999ab3e659b77c4095c883619002f", "candidateSha256": "5ee2a7eef6c7d52f05cf52f664db5151226586c1ac9821c69ba7023b3c359b5a", "startedAt": "2026-11-06T10:52:15.180Z", "passed": false, "qualification": true, "checkerSha256": "89497cb5b8533069477f6686e12ac7a9f01fb4c688f987f78f785c4c13b77d97", "sandboxId": "51242ad9-c70a-426d-be46-12cda0e031b2", "grade": {"schemaVersion": 1, "task": "project-01", "checks": [{"name": "strict compile and renderer build", "passed": true}, {"name": "real import and persistence after reconstruction", "passed": true}, {"name": "actual indexing keeps every nonempty paragraph", "passed": true}, {"name": "actual retrieval and Q&A persist two turns", "passed": true}, {"name": "Electron window, preload, import, indexing and question UI under Xvfb", "passed": false, "error": "Error: page.evaluate: TypeError: Cannot read properties of undefined (reading \'response\')\\n    at eval (eval at evaluate (:302:30), <anonymous>:1:89)\\n    at async <anonymous>:328:30"}], "passed": false}, "estimatedCostUsd": 0.018997517333333335, "finishedAt": "2026-11-06T10:55:36.666Z"}], "measurementPolicy": {"schemaVersion": 1, "minimumUiProtocolRevision": 4, "exclusions": [{"sourceCommit": "b948c1fbac36bca7dae458795d9bfca3f5d2b7d3", "project": "project-05", "reason": "The citation selector clicked answer prose rather than an interactive expand control. Native grades are preserved but excluded from qualified comparisons. The corrected checker also supports native and custom confirmation dialogs."}, {"sourceCommit": "b948c1fbac36bca7dae458795d9bfca3f5d2b7d3", "project": "project-06", "reason": "The task omitted the feedback.submit argument contract while the checker assumed positional arguments. Native grades are preserved but excluded from qualified comparisons. Both treatments are rerun with an explicit object payload contract."}, {"sourceCommit": "945c5d3073026a4fea427372843ea79072221dde", "project": "project-08", "reason": "The graph task did not name the required scripts/check-architecture.sh path, and its failing grade omitted that path. These native outcomes are retained as diagnostic contract-discovery evidence; the explicit-contract graph is a separate frozen execution."}]}, "measurementCaveat": "Revision 2 and 3 native grades used unreliable asynchronous UI waits. They remain historical evidence. Revision 4 requires resolved IPC state and visible answer text; supplemental qualifications never rewrite original grades.", "scope": "project-08"}')
    variants = ['graph']
    primary_ids = ['0809587e-cc59-4276-8285-02dc5072f2aa', '0865dc24-2666-4fda-b6ae-3f488f5339cb', '0cb15597-b43e-4295-985b-af7ea9c1454a', '1500360a-62ce-42cf-aa87-c82962c43655', '1b0a25e5-ba13-4931-9c4f-ff6100f6672a', '1fb04273-5ca5-4a79-9a9d-686149623068', '22873518-2d13-475d-ba37-7b9e94c48407', '22fa3879-a8ff-4219-847c-c5972efedf78', '3398c0d0-a9f2-4383-b64f-c7469ff9d0df', '33bdfb7f-4f5e-49b8-86c8-92d6ce0e7b0b', '3dd7e4f8-1155-4ffa-9da5-98c82c24c087', '4eb48651-306d-44e9-a468-a6ffc322bf27', '54b81e30-0be0-470e-ab3c-2a3783ead0f5', '58ac2e5b-4ee4-4313-bbbd-4022117855bb', '643a867a-74e8-4987-aa56-5640b4c1982e', '64419d93-5073-4632-bff0-8ccd75f2e21f', '6aeae35a-525b-448d-93eb-469a22e6cedf', '6e00cd09-8cfb-495e-ab90-dc16c7938030', '71581d99-5fb7-4e57-bee4-56ec354858a2', '73c46965-1093-4b68-a810-a901dd78bfc0', '79398b0b-a9eb-4892-bb24-194bdc289e2f', '9c2869e2-d150-4c35-82df-9602ca48f17b', '9d859517-72db-4b1a-a683-cd81b9f7ca14', '9feeffa8-1836-485a-a52c-2b398b40a195', 'a09c89fc-d730-4e6c-980c-62b4e7d4993e', 'a7bc0271-d547-4534-a15d-27b70072df40', 'a7dcf5cb-dd20-4c3f-921b-f8a51a21f8f8', 'b394d28a-ebed-4aba-9566-61d6cc5dbedf', 'b8f56d80-c72c-4e31-8c88-f8fc63d76f9a', 'bdc971f7-1a51-437d-b46a-8ed3c268eb97', 'bf9e17a2-c6a5-4a8d-b1d2-ccdff10121a3', 'ca16eac7-0eb5-4523-a975-638e30938a04', 'd3ef30ab-0f2c-4d0e-aee1-7bdf6a8a011e', 'd5a939ba-ee04-422d-a681-0322111156a1', 'e53c3cad-a475-4e49-a79c-e64cfc0316a9', 'ec18a893-0de1-44ac-8541-7f1564e1e8d4', 'ef04c221-aafe-4134-b9fc-0268fab0427f', 'fadf2407-4ef3-4635-bab7-0a8d987096d8', 'fd98af3b-1b52-448c-bc7b-b6cc47e785ea']
    lesson_files = json.loads('{"LAB.md": "## Write down the workflow that\'s in your head\\n\\nYour loop already follows a graph: implement, test, inspect, retry, approve. You know which step comes after which and what happens when one fails, but so far only in your head. In this project you write it down as explicit steps and transitions, and save enough state that the work can pause, split into parallel checks, and resume.\\n\\nStart from the workflow you ran in Project 07. You don\'t need LangGraph or any other framework. A state machine in TypeScript is fine, as long as the state, the routing, the parallel work, the rollback and the human decisions are all written down.\\n\\n**What you hand in:** a graph contract, a serial-versus-parallel experiment, evidence of a targeted rollback, and two complete human reviews. Before you start, predict one transition that currently depends on a person remembering what comes next.\\n\\n\\n## The lab, experiment 1: draw the contract\\n\\nWrite `graph.md`. For each node (a step) give its purpose, inputs, outputs, the state it owns and what it does on failure. List every edge (a transition between two nodes) and the condition for taking it. Find at least one edge you\'d never written down, such as what happens to the UI test when the code doesn\'t compile.\\n\\nDefine the shared state that has to survive a restart: the task revision, the candidate patch\'s checksum, which checks have finished, where the evidence is, the retry count, any decision that\'s waiting, and the reason for stopping. Give each field one owner. A node working from an old copy of the state shouldn\'t be able to overwrite another node\'s result.\\n\\nSave a checkpoint before and after any work that happens outside the graph, like starting a sandbox. When the graph resumes, it should first settle anything that was in flight, and only then start replacements. Draw the paths for cancellation, infrastructure errors and missing telemetry next to the paths for success and task failure, because a diagram with only the success path leaves out the ones that cost money when they go wrong.\\n\\n\\n## The lab, experiment 2: serial versus parallel checks\\n\\nChoose checks that can each run in their own workspace against the same exported patch. Say what each lane (one check in its own workspace) receives, and write the rule for joining the results: which lanes are required, how failures combine, and what happens when a lane times out.\\n\\nRun the same patch through the same checks one after another, then side by side. Record the resources and fixtures both times. Give each lane its own worktree or sandbox so they can\'t change each other\'s files. Record wall-clock time, model and token usage where there is any, infrastructure cost, and the results.\\n\\nRunning in parallel isn\'t always faster. Startup time, competition for resources and waiting on the slowest lane can each eat the gain. Measure it, and if you want to talk about how much it varies, repeat the run under the same conditions.\\n\\n\\n## The lab, experiment 3: roll back to the right place, and ask a person\\n\\nWrite a routing rule for each kind of failure. A bad plan goes back to planning and a defect in the code goes back to the maker. An infrastructure timeout needs its unfinished work settled; rewriting the code won\'t help. Before any rollback, keep the rejected candidate and its evidence.\\n\\nAdd a node that pauses for a human decision. The review request has to name the exact candidate by checksum, the task, the grade, the known limitations, and the two choices (approve or reject). The graph resumes only on an explicit decision tied to that checksum, so an approval given to one patch does not carry over to another.\\n\\nDo two full reviews. For each, record the decision, what the reviewer caught, where they agreed or disagreed with your graph\'s checks, and how long the graph waited. Don\'t auto-approve to keep a demo moving. Show the class the paused graph instead.\\n\\n\\n## What happened when we ran it\\n\\nOur graph takes the task text as its plan and has Pi, our coding agent, write a patch. It sends the patch to the separate grader and to two verification lanes (one for the services, one for the Electron window), retries when a check fails, and pauses for approval when every check passes.\\n\\nIt covers less than the lab asks for. When a candidate fails its checks the only route is back to the maker, and after a third failed candidate the graph stops as `failed`, so it doesn\'t show the different rollback routes from experiment 3. We didn\'t time serial against parallel under controlled conditions, and we didn\'t do two human reviews.\\n\\nUnder **Checkpoints and decisions** below, the graph where Pi\'s patch reached approval is `project-08-graph-contract.json`, and its candidates are attempts 3e5cd770, 43ad509b and 03ca01ca, in that order. The architecture guard Pi wrote in the first (in the task we asked for a script that rejects Node imports in the renderer) let the grader\'s planted import through, and the second didn\'t compile. The third passed every check, and the graph paused there for approval, where it still is because nobody has approved that patch.\\n\\nPick 43ad509b and then 03ca01ca under **Inspect one attempt**, and in each follow **Open in Agent Lens** on the \\"Coding agent\\" step and go to the last command. In 43ad509b Pi writes a test file and is stopped at its 24-call limit, and that file is what fails to compile. In 03ca01ca Pi runs `npm run test` and one of the eight tests it wrote fails, while the grader and both lanes, none of which runs those tests, passed the patch.\\n\\nWe did approve one patch, later and separately, but it was a different one: a hand-written patch we used to test that the approval step works, which it does. That approval doesn\'t carry over to Pi\'s candidate (checksum starting `c74cf9cf`), and no entry below records it: the three `control-flow-qualification` entries hold the hand-written patch (checksum starting `91c4a2df`), and the one we approved, `project-08-control-flow-qualification.json`, was saved before the decision and still shows `node` as `approval`. The three entries that stopped as `failed` are graphs we ran before we named `scripts/check-architecture.sh` in the task, and six of their nine candidates failed the grader\'s architecture check because they had no file at that path.\\n\\n\\"Reached approval\\" and \\"accepted\\" are two separate states, and Pi\'s candidate is in the first. When you read a saved state, look at the candidate checksum, the node it stopped on and whether it has an `approval` record before you describe the outcome: an accepted graph has `node` set to `done` and an `approval` record naming the checksum.\\n\\n\\n## Hand in the transitions as well as the diagram\\n\\nHand in `graph.md`, the contract for each node and edge, who owns each piece of shared state, your serial and parallel measurements, evidence that the lanes were isolated, the rollback records, and two human decisions tied to checksums, with the review notes. Include at least one run that was interrupted and resumed, and explain what stopped it from doing work twice.\\n\\nUse `rollback.md` from the lab packet (**Download the lab brief and templates**, above) to route one real failed candidate. Say which layer is responsible (the plan, the code or the infrastructure), what evidence supports that, and what has to be marked invalid before the next attempt. Then compare your route with what our graph did.\\n\\n**Final discussion:** which of your routing rules are policy choices and which are technical facts? Which decision has to stay with a person? Which checkpoint would let another instructor resume your exercise without asking you anything?\\n", "README.md": "# Lab packet\\n\\nThese are templates for your own lab work. Nothing in them is filled in or graded. Replace every TODO with what you did in your own workspace, and keep your lab work separate from the recorded attempts in the notebook.\\n\\nCourse revision: a9342ff471f2c0e60be0c08b9f4a7c502df4e442\\n", "observations.csv": "condition,source_revision,fixture,started_at,finished_at,outcome,evidence_path,human_interventions,observed_human_minutes,limitations\\n", "comparison.md": "# Comparison\\n\\n## Prediction made before running\\nTODO\\n\\n## Frozen task and conditions\\nTODO\\n\\n## Observations and evidence\\nTODO\\n\\n## What remains unresolved\\nTODO\\n\\n## Proposed follow-up (new experiment)\\nTODO\\n", "interventions.csv": "timestamp,condition,round,reason,action,observed_minutes,evidence\\n", "graph.md": "# Graph contract\\n\\n## Nodes: purpose / inputs / outputs / owner / failure\\nTODO\\n\\n## Edges and conditions (include an implicit edge)\\nTODO\\n\\n## Durable state and ownership\\nTODO\\n\\n## Fan-out / fan-in and lane isolation\\nTODO\\n\\n## Targeted rollback and invalidation\\nTODO\\n\\n## Human approval and resume\\nTODO\\n", "serial-parallel.csv": "mode,candidate_sha256,fixture,resources,wall_seconds,input_tokens,output_tokens,cost_estimate,quality,evidence\\n", "review-decisions.json": "[\\n  {\\n    \\"pass\\": 1,\\n    \\"candidateSha256\\": null,\\n    \\"decision\\": null,\\n    \\"actor\\": null,\\n    \\"decidedAt\\": null,\\n    \\"observedWaitSeconds\\": null,\\n    \\"evidence\\": [],\\n    \\"issuesCaught\\": []\\n  },\\n  {\\n    \\"pass\\": 2,\\n    \\"candidateSha256\\": null,\\n    \\"decision\\": null,\\n    \\"actor\\": null,\\n    \\"decidedAt\\": null,\\n    \\"observedWaitSeconds\\": null,\\n    \\"evidence\\": [],\\n    \\"issuesCaught\\": []\\n  }\\n]\\n", "rollback.md": "# Rollback record\\n\\nTODO: failed candidate, evidence, responsible layer, chosen route, invalidated state, retained artifacts, resumed result.\\n"}')
    variant_notes = {'graph': 'a planned, checkpointed route with up to three candidates. Each is graded, then verified in two separate sandboxes, one for the services and one for the app window. The graph pauses for your approval when a candidate passes.'}
    run_facts = {'attempts': 12, 'minMinutes': 2, 'maxMinutes': 5, 'minUsd': 0.08, 'maxUsd': 0.13}

    def phase_labels(variant, count):
        """Name each coding-agent conversation by the role that produced it."""
        if variant in ("gen-eval", "maker-checker") and count == 3:
            return ["Maker", "Checker (read-only)", "Maker revision"]
        if variant == "plan-gen-eval" and count == 4:
            return ["Planner (read-only)", "Maker", "Checker (read-only)", "Maker revision"]
        if count == 1:
            return ["Coding agent"]
        return [f"Session {index}" for index in range(1, count + 1)]

    def evidence_link(url):
        """Forge opens an evidence version at .../name/v0. The recorded .../name:v0 form lands on a different artifact."""
        url = str(url or "")
        head, colon, version = url.rpartition(":v")
        if colon and version.isdigit() and "/artifacts/" in head:
            url = head + "/v" + version
        return url.replace("https://wandb.ai/", "https://forge.coreweave.com/wandb/", 1)

    return (
        evidence_link,
        lesson_files,
        phase_labels,
        primary_ids,
        project_id,
        run_facts,
        runner_commit,
        saved,
        variant_notes,
        variants,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 08 · Checkpointed graphs and human approval

    [Overview](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTM%3D) · [01](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTQ%3D) · [02](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTU%3D) · [03](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTY%3D) · [04](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTc%3D) · [05](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTg%3D) · [06](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTk%3D) · [07](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMjA%3D) · [08](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMjE%3D)

    Turn the loop into an explicit graph with saved state, parallel checks, rollback, and a pause for a human decision.

    **Start here**

    1. **Make your own copy.** Open the **⋯** menu at the top right, choose **Copy to project**, and pick a private project you can write to. Your copy opens by itself.
    2. **Load the page.** In your copy, click the yellow **▶** button at the bottom right of the editor. The figures, tables and controls below appear only after the cells have run. This makes no model call and starts no coding attempt.
    3. **Read, inspect, run.** Read the lab, open a recorded attempt in Agent Lens to see what the agent did, then run an attempt of your own.

    Jump to [recorded attempts](#inspect-one-attempt) · [run this lesson yourself](#run-this-lesson-yourself) · [my work](#my-work) · [my observations](#your-observation-worksheet). These links work once the cells have run.

    Each lesson is a separate notebook with its own copy and spending limit. The lesson links above open the course originals.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Write down the workflow that's in your head

    Your loop already follows a graph: implement, test, inspect, retry, approve. You know which step comes after which and what happens when one fails, but so far only in your head. In this project you write it down as explicit steps and transitions, and save enough state that the work can pause, split into parallel checks, and resume.

    Start from the workflow you ran in Project 07. You don't need LangGraph or any other framework. A state machine in TypeScript is fine, as long as the state, the routing, the parallel work, the rollback and the human decisions are all written down.

    **What you hand in:** a graph contract, a serial-versus-parallel experiment, evidence of a targeted rollback, and two complete human reviews. Before you start, predict one transition that currently depends on a person remembering what comes next.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The lab, experiment 1: draw the contract

    Write `graph.md`. For each node (a step) give its purpose, inputs, outputs, the state it owns and what it does on failure. List every edge (a transition between two nodes) and the condition for taking it. Find at least one edge you'd never written down, such as what happens to the UI test when the code doesn't compile.

    Define the shared state that has to survive a restart: the task revision, the candidate patch's checksum, which checks have finished, where the evidence is, the retry count, any decision that's waiting, and the reason for stopping. Give each field one owner. A node working from an old copy of the state shouldn't be able to overwrite another node's result.

    Save a checkpoint before and after any work that happens outside the graph, like starting a sandbox. When the graph resumes, it should first settle anything that was in flight, and only then start replacements. Draw the paths for cancellation, infrastructure errors and missing telemetry next to the paths for success and task failure, because a diagram with only the success path leaves out the ones that cost money when they go wrong.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The lab, experiment 2: serial versus parallel checks

    Choose checks that can each run in their own workspace against the same exported patch. Say what each lane (one check in its own workspace) receives, and write the rule for joining the results: which lanes are required, how failures combine, and what happens when a lane times out.

    Run the same patch through the same checks one after another, then side by side. Record the resources and fixtures both times. Give each lane its own worktree or sandbox so they can't change each other's files. Record wall-clock time, model and token usage where there is any, infrastructure cost, and the results.

    Running in parallel isn't always faster. Startup time, competition for resources and waiting on the slowest lane can each eat the gain. Measure it, and if you want to talk about how much it varies, repeat the run under the same conditions.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The lab, experiment 3: roll back to the right place, and ask a person

    Write a routing rule for each kind of failure. A bad plan goes back to planning and a defect in the code goes back to the maker. An infrastructure timeout needs its unfinished work settled; rewriting the code won't help. Before any rollback, keep the rejected candidate and its evidence.

    Add a node that pauses for a human decision. The review request has to name the exact candidate by checksum, the task, the grade, the known limitations, and the two choices (approve or reject). The graph resumes only on an explicit decision tied to that checksum, so an approval given to one patch does not carry over to another.

    Do two full reviews. For each, record the decision, what the reviewer caught, where they agreed or disagreed with your graph's checks, and how long the graph waited. Don't auto-approve to keep a demo moving. Show the class the paused graph instead.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What happened when we ran it

    Our graph takes the task text as its plan and has Pi, our coding agent, write a patch. It sends the patch to the separate grader and to two verification lanes (one for the services, one for the Electron window), retries when a check fails, and pauses for approval when every check passes.

    It covers less than the lab asks for. When a candidate fails its checks the only route is back to the maker, and after a third failed candidate the graph stops as `failed`, so it doesn't show the different rollback routes from experiment 3. We didn't time serial against parallel under controlled conditions, and we didn't do two human reviews.

    Under **Checkpoints and decisions** below, the graph where Pi's patch reached approval is `project-08-graph-contract.json`, and its candidates are attempts 3e5cd770, 43ad509b and 03ca01ca, in that order. The architecture guard Pi wrote in the first (in the task we asked for a script that rejects Node imports in the renderer) let the grader's planted import through, and the second didn't compile. The third passed every check, and the graph paused there for approval, where it still is because nobody has approved that patch.

    Pick 43ad509b and then 03ca01ca under **Inspect one attempt**, and in each follow **Open in Agent Lens** on the "Coding agent" step and go to the last command. In 43ad509b Pi writes a test file and is stopped at its 24-call limit, and that file is what fails to compile. In 03ca01ca Pi runs `npm run test` and one of the eight tests it wrote fails, while the grader and both lanes, none of which runs those tests, passed the patch.

    We did approve one patch, later and separately, but it was a different one: a hand-written patch we used to test that the approval step works, which it does. That approval doesn't carry over to Pi's candidate (checksum starting `c74cf9cf`), and no entry below records it: the three `control-flow-qualification` entries hold the hand-written patch (checksum starting `91c4a2df`), and the one we approved, `project-08-control-flow-qualification.json`, was saved before the decision and still shows `node` as `approval`. The three entries that stopped as `failed` are graphs we ran before we named `scripts/check-architecture.sh` in the task, and six of their nine candidates failed the grader's architecture check because they had no file at that path.

    "Reached approval" and "accepted" are two separate states, and Pi's candidate is in the first. When you read a saved state, look at the candidate checksum, the node it stopped on and whether it has an `approval` record before you describe the outcome: an accepted graph has `node` set to `done` and an `approval` record naming the checksum.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.image('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI2ODAiIGhlaWdodD0iNzU1IiB2aWV3Qm94PSIwIDAgNjgwIDc1NSIgcm9sZT0iaW1nIiBhcmlhLWxhYmVsbGVkYnk9InRpdGxlIGRlc2MiPgo8dGl0bGUgaWQ9InRpdGxlIj5UaHJlZSBQaSBjYW5kaWRhdGVzOyBvbmUgYXBwcm92YWwgcGF1c2U8L3RpdGxlPjxkZXNjIGlkPSJkZXNjIj5JbiB0aGUgZXhwbGljaXQtY29udHJhY3QgZ3JhcGggcnVuLCBhdHRlbXB0IG9uZSBmYWlscyB0aGUgYXJjaGl0ZWN0dXJlIGd1YXJkIGFuZCByb2xscyBiYWNrLiBBdHRlbXB0IHR3byBmYWlscyBjb21waWxhdGlvbiBhbmQgcm9sbHMgYmFjay4gQXR0ZW1wdCB0aHJlZSBwYXNzZXMgdGhlIHByb3RlY3RlZCBncmFkZSBhbmQgaW5kZXBlbmRlbnQgc2VydmljZSBhbmQgRWxlY3Ryb24gbGFuZXMsIHRoZW4gcGF1c2VzIGZvciBodW1hbiBhcHByb3ZhbC4gQSBzZXBhcmF0ZSBtYW51YWwgY2FuZGlkYXRlIHdhcyBhcHByb3ZlZCBsYXRlci48L2Rlc2M+CjxkZWZzPjxtYXJrZXIgaWQ9ImFycm93IiBtYXJrZXJXaWR0aD0iOCIgbWFya2VySGVpZ2h0PSI4IiByZWZYPSI3IiByZWZZPSI0IiBvcmllbnQ9ImF1dG8iPjxwYXRoIGQ9Ik0wLDAgTDgsNCBMMCw4IiBmaWxsPSIjNjI2NjVlIi8+PC9tYXJrZXI+PC9kZWZzPgo8cmVjdCB3aWR0aD0iNjgwIiBoZWlnaHQ9Ijc1NSIgcng9IjgiIGZpbGw9IiNmYWY5ZjYiLz4KPHN0eWxlPnRleHR7Zm9udC1mYW1pbHk6QXJpYWwsSGVsdmV0aWNhLHNhbnMtc2VyaWY7ZmlsbDojMjQyNzIyfS50aXRsZXtmb250LXNpemU6MjVweDtmb250LXdlaWdodDo3MDB9LmhlYWR7Zm9udC1zaXplOjIwcHg7Zm9udC13ZWlnaHQ6NzAwfS5ib2R5e2ZvbnQtc2l6ZToxNnB4fS5ub3Rle2ZvbnQtc2l6ZToxNXB4O2ZpbGw6IzYyNjY1ZX08L3N0eWxlPgo8dGV4dCBjbGFzcz0idGl0bGUiIHg9IjI4IiB5PSI0MCI+VGhyZWUgUGkgY2FuZGlkYXRlczsgb25lIGFwcHJvdmFsIHBhdXNlPC90ZXh0Pgo8cmVjdCB4PSIyOCIgeT0iNjUiIHdpZHRoPSI2MjQiIGhlaWdodD0iMTEyIiByeD0iNiIgZmlsbD0iI2Y1ZTVkZiIgc3Ryb2tlPSIjZDZkNmNlIi8+PHRleHQgY2xhc3M9ImhlYWQiIHg9IjQ2IiB5PSI5NSI+QXR0ZW1wdCAxIMK3IDNlNWNkNzcwPC90ZXh0Pjx0ZXh0IGNsYXNzPSJib2R5IiB4PSI0NiIgeT0iMTIyIj5HdWFyZCBhY2NlcHRzIGEgcHJvaGliaXRlZCBOb2RlIGltcG9ydC48L3RleHQ+PHRleHQgY2xhc3M9ImJvZHkiIHg9IjQ2IiB5PSIxNDQiPlByb3RlY3RlZCBncmFkZSBmYWlsczsgdGhlIGdyYXBoIHJvbGxzIGJhY2suPC90ZXh0PjxwYXRoIGQ9Ik0zNDAgMTc3IEwzNDAgMjA3IiBzdHJva2U9IiM2MjY2NWUiIHN0cm9rZS13aWR0aD0iMiIgbWFya2VyLWVuZD0idXJsKCNhcnJvdykiLz48dGV4dCBjbGFzcz0ibm90ZSIgeD0iMzU1IiB5PSIxOTcuMCI+cmVzdG9yZSBzdGFydGluZyBwb2ludDwvdGV4dD48cmVjdCB4PSIyOCIgeT0iMjE3IiB3aWR0aD0iNjI0IiBoZWlnaHQ9IjExMiIgcng9IjYiIGZpbGw9IiNmNWU1ZGYiIHN0cm9rZT0iI2Q2ZDZjZSIvPjx0ZXh0IGNsYXNzPSJoZWFkIiB4PSI0NiIgeT0iMjQ3Ij5BdHRlbXB0IDIgwrcgNDNhZDUwOWI8L3RleHQ+PHRleHQgY2xhc3M9ImJvZHkiIHg9IjQ2IiB5PSIyNzQiPlR5cGVTY3JpcHQgY29tcGlsYXRpb24gZmFpbHMuPC90ZXh0Pjx0ZXh0IGNsYXNzPSJib2R5IiB4PSI0NiIgeT0iMjk2Ij5UaGUgZ3JhcGggcmVjb3JkcyB0aGUgZmFpbHVyZSBhbmQgcm9sbHMgYmFjay48L3RleHQ+PHBhdGggZD0iTTM0MCAzMjkgTDM0MCAzNTkiIHN0cm9rZT0iIzYyNjY1ZSIgc3Ryb2tlLXdpZHRoPSIyIiBtYXJrZXItZW5kPSJ1cmwoI2Fycm93KSIvPjx0ZXh0IGNsYXNzPSJub3RlIiB4PSIzNTUiIHk9IjM0OS4wIj5yZXN0b3JlIHN0YXJ0aW5nIHBvaW50PC90ZXh0PjxyZWN0IHg9IjI4IiB5PSIzNjkiIHdpZHRoPSI2MjQiIGhlaWdodD0iMTEyIiByeD0iNiIgZmlsbD0iI2U3ZjBlYiIgc3Ryb2tlPSIjZDZkNmNlIi8+PHRleHQgY2xhc3M9ImhlYWQiIHg9IjQ2IiB5PSIzOTkiPkF0dGVtcHQgMyDCtyAwM2NhMDFjYTwvdGV4dD48dGV4dCBjbGFzcz0iYm9keSIgeD0iNDYiIHk9IjQyNiI+UHJvdGVjdGVkIGdyYWRlIHBhc3Nlcy48L3RleHQ+PHRleHQgY2xhc3M9ImJvZHkiIHg9IjQ2IiB5PSI0NDgiPkluZGVwZW5kZW50IHNlcnZpY2VzICsgRWxlY3Ryb24gbGFuZXMgYWxzbyBwYXNzLjwvdGV4dD48cGF0aCBkPSJNMzQwIDQ4MSBMMzQwIDUxMSIgc3Ryb2tlPSIjNjI2NjVlIiBzdHJva2Utd2lkdGg9IjIiIG1hcmtlci1lbmQ9InVybCgjYXJyb3cpIi8+PHJlY3QgeD0iMjgiIHk9IjUyMSIgd2lkdGg9IjYyNCIgaGVpZ2h0PSIxMTIiIHJ4PSI2IiBmaWxsPSIjZjVlZGRjIiBzdHJva2U9IiNkNmQ2Y2UiLz48dGV4dCBjbGFzcz0iaGVhZCIgeD0iNDYiIHk9IjU1MSI+U1RPUCDCtyBleHBsaWNpdCBodW1hbiBkZWNpc2lvbiByZXF1aXJlZDwvdGV4dD48dGV4dCBjbGFzcz0iYm9keSIgeD0iNDYiIHk9IjU3OCI+UGkgY2FuZGlkYXRlIGM3NGNmOWNmMzcxNuKApiByZW1haW5zIGF0IGFwcHJvdmFsLjwvdGV4dD48dGV4dCBjbGFzcz0iYm9keSIgeD0iNDYiIHk9IjYwMCI+UGFzc2luZyB0ZXN0cyBkbyBub3QgYXBwcm92ZSBvciBtZXJnZSB0aGUgcGF0Y2guPC90ZXh0Pjx0ZXh0IGNsYXNzPSJub3RlIiB4PSIyOCIgeT0iNjgwIj5TZXBhcmF0ZSBtYW51YWwgY2FuZGlkYXRlIDkxYzRhMmRmN2I5YeKApiB3YXMgYXBwcm92ZWQgbGF0ZXIuPC90ZXh0Pjx0ZXh0IGNsYXNzPSJub3RlIiB4PSIyOCIgeT0iNzEwIj5UaGF0IGRlY2lzaW9uIGNoYW5nZWQgb25seSBpdHMgb3duIHF1YWxpZmljYXRpb24gY2hlY2twb2ludC48L3RleHQ+PC9zdmc+Cg==', alt='The recorded graph candidates: one fails the architecture guard, one fails to compile, then one passes its checks and pauses for a human decision. The approval we recorded later belongs to a different, hand-written patch.', caption='The recorded graph candidates: one fails the architecture guard, one fails to compile, then one passes its checks and pauses for a human decision. The approval we recorded later belongs to a different, hand-written patch.', width="100%")
    return


@app.cell(hide_code=True)
def _(Counter, mo, primary_ids, project_id, saved):
    rows = [row for row in saved.get("trials", []) if project_id == "overview" or row["project"] == project_id]
    primary_rows = [row for row in rows if row["id"] in primary_ids]
    _primary = []
    for _task, _variant in sorted({(r["project"], r["variant"]) for r in primary_rows}):
        _group = [r for r in primary_rows if (r["project"], r["variant"]) == (_task, _variant)]
        _primary.append({"Project": _task, "Treatment": _variant, "Passed": sum(r["outcome"] == "passed" for r in _group), "Attempts": len(_group), "Other outcomes": ", ".join(f"{v} {k.replace('_', ' ')}" for k, v in Counter(r["outcome"] for r in _group if r["outcome"] != "passed").items()) or "None"})
    _history = []
    for _task, _variant, _source in sorted({(r["project"], r["variant"], r["sourceCommit"]) for r in rows}):
        _group = [r for r in rows if (r["project"], r["variant"], r["sourceCommit"]) == (_task, _variant, _source)]
        _counts = Counter(r["outcome"] for r in _group)
        _history.append({"project": _task, "variant": _variant, "source_commit": _source, "attempts": len(_group), "passed": _counts["passed"], "task_failed": _counts["task_failed"], "infrastructure_failed": _counts["infrastructure_failed"], "telemetry_missing": _counts["telemetry_missing"], "known_estimate_usd": round(sum(r.get("reconciledEstimateUsd", r.get("estimatedCostUsd")) or 0 for r in _group), 6), "unknown_cost_attempts": sum(r.get("estimatedCostUsd") is None and r.get("reconciledEstimateUsd") is None for r in _group)})
    mo.vstack([
        mo.md("## Saved results\n\nWe recorded these attempts while building the course. They ran a smaller version of the lab above, so treat them as worked examples, not as your grade."),
        mo.ui.table(_primary, selection=None, pagination=False, show_column_summaries=False) if _primary else mo.md("This project has no three-attempt comparison. " + ("Its recorded attempts are candidates in a graph. Each candidate starts again from the unchanged starter and is given the grader's feedback on the one before." if project_id == "project-08" else "Its recorded attempts are rounds of a loop, where a round can start from the patch of the round before.") + " Read their saved states below."),
        mo.md("The table counts the main comparison only: three attempts per treatment, where a treatment is the setup the agent starts with. Earlier trial runs and diagnostics are kept below with their original grades and are not counted here.") if _primary else mo.md(""),
        mo.accordion({"All recorded attempts, grouped by source revision": mo.vstack([mo.md(f"This notebook has {len(rows)} recorded attempts, captured on {str(saved.get('capturedAt', ''))[:10]}. That includes failed attempts" + (" and earlier trial runs that the main comparison leaves out." if _primary else ".")), mo.ui.table(_history, selection=None, pagination=False, show_column_summaries=False)]), "What these results do not measure": mo.md("\n\n".join(item["reason"] for item in saved.get("measurementPolicy", {}).get("exclusions", []) if project_id in ["overview", item["project"]]) or "Nothing here measures how much of your own time a harness saves. Where a time or effort number is missing, it was not measured.")})
    ])
    return primary_rows, rows


@app.cell(hide_code=True)
def _(mo, primary_rows, rows):
    _ordered = primary_rows + [r for r in rows if r not in primary_rows]
    _options = {f"{'Main comparison' if r in primary_rows else 'Archive'} · {r['project']} · {r['variant']} · attempt {r['trial']} · {str(r['outcome']).replace('_', ' ')} · {r['id'][:8]}": r["id"] for r in _ordered}
    selected_trial = mo.ui.dropdown(options=_options, value=next(iter(_options), None), searchable=True, full_width=True, label="Choose a recorded attempt")
    mo.vstack([mo.md("## Inspect one attempt\n\nPick a recorded attempt. Read its checks first: they were run by a separate process on the patch the agent delivered. Then open the agent's conversation in Agent Lens to see how it got there."), selected_trial])
    return (selected_trial,)


@app.cell(hide_code=True)
def _(evidence_link, json, mo, phase_labels, rows, selected_trial):
    _row = next((r for r in rows if r["id"] == selected_trial.value), None)
    if _row is None:
        _view = mo.md("No recorded attempt selected.")
    else:
        _lens = "https://forge.coreweave.com/agent-lens/wandb/learn-harness-engineering-forge"
        _phases = {p.get("conversationId"): p for p in (_row.get("actorPhases") or [])}
        _steps = []
        for _label, _conversation in zip(phase_labels(_row.get("variant"), len(_row.get("conversationIds", []))), _row.get("conversationIds", [])):
            _phase = _phases.get(_conversation, {})
            _ended = "yes" if _phase.get("completed") else ("no: " + str((_phase.get("errors") or ["it reached its limit"])[0]).lower()) if _phase.get("completed") is False else "not recorded"
            _steps.append(f"| {_label} | [Open in Agent Lens]({_lens}/conversations/{_conversation}) | {_phase.get('requests', 'not recorded')} | {_ended} |")
        _other = []
        if _row.get("artifactUrl"):
            _other.append(f"[Patch, logs and grade]({evidence_link(_row['artifactUrl'])})")
        if _row.get("wandbRunUrl"):
            _other.append(f"[Run record]({_row['wandbRunUrl']})")
        _checks = [{"Check": c["name"], "Result": "Pass" if c["passed"] else "Fail", "Detail": c.get("error", "")} for c in (_row.get("grade") or {}).get("checks", [])]
        _view = mo.vstack([
            mo.md(f"**{_row['project']} · {_row['variant']} · {str(_row['outcome']).replace('_', ' ')}**"),
            mo.ui.table(_checks, selection=None, pagination=False, wrapped_columns=["Check", "Detail"], show_column_summaries=False) if _checks else mo.md("No independent grade was recorded for this attempt. Read the error in the full record below before drawing a conclusion."),
            mo.md("### What the agent did\n\nAgent Lens keeps the whole conversation behind this attempt. The **Thread** tab shows the task the agent was given, then each step: what it reasoned, the command or edit it made, and what came back. **Timeline** shows where the time went, and the token totals are at the top right.\n\n| Step | Conversation | Model calls | Finished on its own |\n|---|---|---|---|\n" + "\n".join(_steps) + "\n\nIn the last column, \"model-call budget exhausted\" means the agent used every model call it was allowed in that step, which is 24 for a whole attempt. It has nothing to do with money.\n\nAs you read, answer three questions. What did the agent look at before its first edit? Did it build or launch the app before it stopped? If it finished on its own, does its last message agree with the checks above, and if it was stopped at its limit, what was it in the middle of? The conversation shows what the agent did, but only the checks show whether the app worked. The patch is `candidate.diff` behind **Patch, logs and grade**.") if _steps else mo.md("No agent conversation was recorded for this attempt."),
            mo.md(" · ".join(_other) + ("\n\n" if _other else "") + "These links open the course's own project, `wandb/learn-harness-engineering-forge`. If one says you do not have access, ask your instructor. Your own attempts open in your own project, under **My work**."),
            mo.md(f"Source `{_row['sourceCommit']}` · protocol revision {_row.get('protocolRevision', 1)} · tokens in/out: {_row.get('inputTokens', 'unknown')} / {_row.get('outputTokens', 'unknown')}."),
            mo.accordion({"Full record for this attempt": mo.md("```json\n" + json.dumps(_row, indent=2) + "\n```")})
        ])
    _view
    return


@app.cell(hide_code=True)
def _(json, mo, project_id, saved):
    _states = []
    if project_id in ["overview", "project-07"]:
        _states += saved.get("loops", [])
    if project_id in ["overview", "project-08"]:
        _states += saved.get("graphs", [])
    _items = {state["file"]: mo.md("```json\n" + json.dumps(state, indent=2) + "\n```") for state in _states}
    mo.vstack([mo.md("## Checkpoints and decisions\n\nEach entry shows where a recorded loop or graph stopped and why. They are records to read and are not to be resumed. A loop round can start from the patch of the round before, a graph candidate starts again from the unchanged starter, and an approval applies only to the exact patch it names."), mo.accordion(_items)]) if _items else None
    return


@app.cell(hide_code=True)
def _():
    def _load_learner():
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

        return LessonWorkspace
    LessonWorkspace = _load_learner()
    return (LessonWorkspace,)


@app.cell(hide_code=True)
def _(LessonWorkspace, project_id, runner_commit):
    learner = LessonWorkspace(runner_commit, project_id)
    return (learner,)


@app.cell(hide_code=True)
def _(mo, project_id, run_facts):
    learner_budget = mo.ui.number(start=5, stop=50, value=20, step=1, label="Spending limit for this copy (USD)")
    prepare_workspace = mo.ui.button(value=0, on_click=lambda value: value + 1, label="Prepare or restore my workspace", full_width=True)
    get_prepare_click, set_prepare_click = mo.state(0)
    _typical = (f"The recorded attempts for this lesson took {run_facts['minMinutes']} to {run_facts['maxMinutes']} minutes and an estimated ${run_facts['minUsd']:.2f} to ${run_facts['maxUsd']:.2f} each. " if run_facts else "")
    _where = "On this overview page the controls run the Project 01 exercise. If you are going to do Project 01, run it from the Project 01 notebook instead, so your attempts sit beside its lesson.\n\n" if project_id == "overview" else ""
    mo.vstack([
        mo.md("## Run this lesson yourself\n\nYou have read the lab and looked at recorded attempts. Now run one of your own and compare. Work through the six steps in order, and stay in the editor view: the API key prompt in step 3 does not appear in Preview.\n\n" + _where + _typical + "Running an attempt is optional and costs money on your project. The spending limit below caps this copy's own estimate of what it has spent. Before each sandbox or model request the copy sets aside its maximum estimated cost, and it stops before an operation that would pass the limit, so leave the limit at $20 unless you have a reason to lower it. Your project's own billing shows the real charge.\n\n**1. Use your own copy.** If you have not copied this notebook yet, open the **⋯** menu at the top right and choose **Copy to project**, then pick a private project you can write to. Come back to that same copy next time. A new copy starts with no saved work and a new spending limit.\n\n**2. Prepare your workspace.** This installs the course runner inside the notebook and restores anything this copy saved before. It takes a few minutes and starts no model call or coding attempt. Each notebook session also counts about $0.34 of notebook compute against your limit, so **My work** shows $0.34 as soon as setup finishes. A notebook session lasts one hour. Keep the same spending limit each time you return."),
        learner_budget, prepare_workspace
    ])
    return (
        get_prepare_click,
        learner_budget,
        prepare_workspace,
        set_prepare_click,
    )


@app.cell(hide_code=True)
def _(
    get_prepare_click,
    learner,
    learner_budget,
    mo,
    prepare_workspace,
    set_prepare_click,
):
    mo.stop(prepare_workspace.value <= get_prepare_click())
    set_prepare_click(prepare_workspace.value)
    try:
        with mo.status.spinner(title="Preparing your workspace. This takes a few minutes."):
            learner.prepare(float(learner_budget.value))
        _message = mo.callout(mo.md("**Workspace ready.** Go on to step 3 and connect your sandbox access."), kind="success")
    except Exception as _error:
        _message = mo.callout(mo.md("**Setup stopped.** " + learner.redact(_error)), kind="danger")
    _message
    return


@app.cell(hide_code=True)
def _(mo):
    connect_sandbox = mo.ui.button(value=0, on_click=lambda value: value + 1, label="Connect my sandbox access")
    get_connect_click, set_connect_click = mo.state(0)
    mo.vstack([mo.md("**3. Connect your sandbox access.** Each attempt runs in a fresh sandbox, and starting one needs your own W&B API key. Copy it from [your API key page](https://wandb.ai/authorize). Click the button, then paste the key into the masked box that appears just below it and press Enter.\n\nThe box appears **only in the editor view**. If you are in Preview and nothing appears, switch back to the editor and the box will be there. Use your own key, never someone else's. It is kept in this session's memory only: it is not written to the notebook, your saved progress or your downloads. You will need to connect again whenever the notebook session restarts."), connect_sandbox])
    return connect_sandbox, get_connect_click, set_connect_click


@app.cell(hide_code=True)
def _(connect_sandbox, get_connect_click, learner, mo, set_connect_click):
    mo.stop(connect_sandbox.value <= get_connect_click())
    set_connect_click(connect_sandbox.value)
    _state = learner.view()
    # Never ask for a key that cannot be used yet.
    if not _state["prepared"]:
        _message = mo.callout(mo.md("**Prepare your workspace first** (step 2). You have not been asked for your key."), kind="warn")
    elif _state["active"]:
        _message = mo.callout(mo.md(("**An action is still running.** Wait until **My work** shows it has finished, then connect." if _state["active"] else "**This copy is stopped** because an earlier action was interrupted, so a key cannot be used here.") + " You have not been asked for your key."), kind="warn")
    else:
        try:
            import getpass
            _key = getpass.getpass("Paste your W&B API key and press Enter (kept in session memory only): ")
            _text = learner.connect(_key)
            del _key
            _message = mo.callout(mo.md("**Connected.** " + _text + " Go on to step 4."), kind="success")
        except Exception as _error:
            _message = mo.callout(mo.md("**Connection stopped.** " + learner.redact(_error)), kind="danger")
        finally:
            _key = None
    _message
    return


@app.cell(hide_code=True)
def _(mo):
    prediction = mo.ui.text_area(label="My prediction, and why", rows=3, full_width=True)
    mo.vstack([mo.md("**4. Write your prediction.** Before you run anything, say what you expect to happen and where the agent is most likely to fall short. You will compare this with the result in step 6, so do not change it afterwards."), prediction])
    return (prediction,)


@app.cell(hide_code=True)
def _(mo, project_id, variant_notes, variants):
    learner_variant = mo.ui.dropdown(options=variants, value=variants[0], label="Treatment to try")
    learner_repeats = mo.ui.number(start=1, stop=3, value=1, label="Attempts in one go (each is paid)")
    _run_name = "Run the loop once" if project_id == "project-07" else "Run the graph" if project_id == "project-08" else "Run attempts"
    _actions = {"Check that everything works (small paid test)": "qualify", _run_name + " (paid)": "run"}
    if project_id == "project-08":
        _actions["Record my reviewed graph decision"] = "decision"
    learner_action = mo.ui.dropdown(options=_actions, value=next(iter(_actions)), label="What to do")
    learner_consent = mo.ui.checkbox(label="I understand this starts paid work on my project, counted against my spending limit")
    learner_launch = mo.ui.button(value=0, on_click=lambda value: value + 1, label="Start", full_width=True)
    learner_cancel = mo.ui.button(value=0, on_click=lambda value: value + 1, label="Cancel the running action")
    learner_decision = mo.ui.dropdown(options=["reject", "approve"], value="reject", label="Graph decision after reviewing the patch")
    learner_digest = mo.ui.text(label="Reviewed candidate SHA-256", full_width=True)
    get_action_click, set_action_click = mo.state(0)
    get_cancel_click, set_cancel_click = mo.state(0)
    _setups = "\n".join(f"- **{_name}**: {variant_notes.get(_name, 'See the lesson above.')}" for _name in variants)
    _compare = "Run one attempt with each treatment, one after the other, so you have rows to compare under **My work**. **Attempts in one go** sets how many attempts one Start runs, one after another. Each is paid, so leave it at 1 unless you want repeats." if len(variants) > 1 else "This lesson has one treatment."
    _special = ""
    if project_id == "project-07":
        _compare = "Run goal and maker-checker, one after the other, so you have two different setups to compare under **My work**. In one round, timer gives the agent the same setup as goal."
        _special = "\n\nIn this notebook each loop runs exactly one round, so the repeating described in the lab does not happen here. Goal and maker-checker finish as soon as their round has been graded. Timer runs the same single attempt as goal and then keeps the action open until its ten-minute deadline. Start can run another completed treatment; each attempt keeps its own checkpoint. The full two-hour monitoring exercise in the lab needs a runner that outlives a one-hour notebook session."
    if project_id == "project-08":
        _special = "\n\nHere the run action runs the whole graph once: up to three candidates by the agent, each followed by two verification sandboxes, so allow about three times the time and cost shown above. The graph pauses when a candidate passes its checks, and nothing is accepted until you review that exact patch and record a decision in the panel below. If no candidate passes, the graph stops at `failed`. Start can run another graph after the current graph finishes or you decide its approval candidate."
    mo.vstack([
        mo.md("**5. Check that everything works, then run an attempt.** The first time, choose **Check that everything works**. It is a small paid test that the model, the sandbox and the tracing all respond, followed by checks that the unfinished app fails and the protected repair passes; it cleans up after itself. Its result appears under **My work**. If it does not pass, the reason is shown there, and a check that fails without reporting what it used stops this copy until your instructor has looked at it. Once it passes, choose **" + _run_name + "**.\n\nA treatment is the setup the agent starts with. In this lesson you can try:\n\n" + _setups + "\n\n" + _compare + " The coding agent gets at most ten minutes and 24 model calls per attempt, and one copy runs one action at a time. A notebook session lasts one hour, so click **Save my notes and progress** first to keep your prediction, and start only when there is time to finish. Keep this tab open while it runs: if the notebook session ends mid-run, use Prepare and Connect to inspect the saved work. **Cancel the running action** waits for cleanup; missing usage or unverified cleanup keeps new paid work blocked until your instructor can reconcile it. Count a failed attempt as a result to explain, and do not hide it." + _special),
        learner_action, learner_variant,
        learner_repeats if project_id not in ["project-07", "project-08"] else mo.md(""),
        mo.accordion({"Project 08: record your review decision": mo.vstack([mo.md("Under **My work**, open **Details: checkpoints and approval candidate** and find the latest `project-08-graph-…-checkpoint.json`. You can record a decision only when its `node` is `approval`. There, `candidate.trialId` names the attempt to review and `candidate.sha256` is its checksum. Read that attempt's patch and both verification results, paste the full checksum below and choose approve or reject. Then set **What to do** to **Record my reviewed graph decision** and press **Start**. Recording a decision starts no paid work and needs no tick in the box. An approval of a different candidate does not count."), learner_decision, learner_digest])}) if project_id == "project-08" else mo.md(""),
        learner_consent, learner_launch, learner_cancel
    ])
    return (
        get_action_click,
        get_cancel_click,
        learner_action,
        learner_cancel,
        learner_consent,
        learner_decision,
        learner_digest,
        learner_launch,
        learner_repeats,
        learner_variant,
        set_action_click,
        set_cancel_click,
    )


@app.cell(hide_code=True)
def _(
    get_action_click,
    learner,
    learner_action,
    learner_consent,
    learner_decision,
    learner_digest,
    learner_launch,
    learner_repeats,
    learner_variant,
    mo,
    set_action_click,
):
    mo.stop(learner_launch.value <= get_action_click())
    set_action_click(learner_launch.value)
    try:
        if learner_action.value != "decision" and not learner_consent.value:
            raise RuntimeError("Tick the box above to confirm the paid work, then press Start again.")
        learner.start(learner_action.value, learner_variant.value, int(learner_repeats.value), learner_decision.value, learner_digest.value.strip())
        _message = mo.callout(mo.md("**Started.** Watch **My work** below; it refreshes by itself. Keep this tab open until the status says it has finished."), kind="info")
    except Exception as _error:
        _message = mo.callout(mo.md("**Not started.** " + learner.redact(_error)), kind="warn")
    _message
    return


@app.cell(hide_code=True)
def _(get_cancel_click, learner, learner_cancel, mo, set_cancel_click):
    mo.stop(learner_cancel.value <= get_cancel_click())
    set_cancel_click(learner_cancel.value)
    learner.cancel()
    mo.callout(mo.md("**Cancel requested.** Wait until the status under **My work** shows the action has finished or failed before closing this tab. If an attempt or check had already started, its cost is now unknown, so this copy will not start anything else until your instructor has checked it."), kind="warn")
    return


@app.cell(hide_code=True)
def _(mo):
    learner_refresh = mo.ui.refresh(options=[5, 15, 30], default_interval=15, label="Refresh my results")
    learner_refresh
    return (learner_refresh,)


@app.cell(hide_code=True)
def _(base64, evidence_link, json, learner, learner_refresh, mo, phase_labels):
    learner_refresh.value
    my_progress = learner.view()
    _lens = "https://forge.coreweave.com/agent-lens/" + my_progress["destination"]
    _own = my_progress["destination"] != "/"
    _budget = my_progress["budget"]
    _checks = my_progress["qualifications"]
    if not _checks:
        _access = "not run yet"
    elif _checks[-1].get("passed"):
        _access = "**passed**. You can run an attempt."
    else:
        _access = "**did not pass**. " + learner.redact(_checks[-1].get("error") or "Open the details below for the reason.") + (" This copy has now stopped and will not start anything else until your instructor has checked it." if _budget.get("halted") or _budget.get("reservations") else " Run the check again once that is fixed.")
    # The check is the only time the app itself calls a model, so link both of its conversations.
    _traces = []
    if _checks and _own:
        _agent_id = (_checks[-1].get("agent") or {}).get("conversationId")
        _app_id = (_checks[-1].get("app") or {}).get("conversationId")
        if _agent_id:
            _traces.append(f"[the test agent's conversation]({_lens}/conversations/{_agent_id})")
        if _app_id:
            _traces.append(f"[the app's own conversation]({_lens}/conversations/{_app_id})")
    if _traces:
        _access += " In Agent Lens you can open " + " and ".join(_traces) + ". The check is the only time the app itself calls a model, so this is where you can compare an app's conversation with an agent's."
    # The runner writes a placeholder outcome before the agent starts; do not show it as a failure.
    _result = lambda r: str(r.get("outcome", "unknown")).replace("_", " ") if r.get("finishedAt") else ("still running" if my_progress["active"] else "interrupted before it finished")
    _rows = [{"Attempt": r["id"][:8], "Treatment": r.get("variant"), "Result": _result(r), "Checks passed": (str(sum(bool(c.get("passed")) for c in (r.get("grade") or {}).get("checks", []))) + " of " + str(len((r.get("grade") or {}).get("checks", [])))) if (r.get("grade") or {}).get("checks") else "not graded", "Estimated USD": round(r["estimatedCostUsd"], 3) if isinstance(r.get("estimatedCostUsd"), (int, float)) else None} for r in my_progress["trials"]]
    _cards = []
    for _r in my_progress["trials"]:
        _labels = phase_labels(_r.get("variant"), len(_r.get("conversationIds", [])))
        _parts = [f"[{_label} in Agent Lens]({_lens}/conversations/{_conversation})" for _label, _conversation in zip(_labels, _r.get("conversationIds", []))]
        if _r.get("artifactUrl"):
            _parts.append(f"[Patch and test evidence]({evidence_link(_r['artifactUrl'])})")
        if _r.get("wandbRunUrl"):
            _parts.append(f"[Run record]({_r['wandbRunUrl']})")
        _failed = [str(c.get("name")) + (" (" + str(c["error"]) + ")" if c.get("error") else "") for c in (_r.get("grade") or {}).get("checks", []) if not c.get("passed")]
        _summary = f"**Attempt {_r['id'][:8]} · {_r.get('variant')} · {_result(_r)}**" + ("\n\nFailed checks: " + learner.redact("; ".join(_failed)) + "." if _failed else "") + ("\n\nThe agent used all of its allowed time or turns before saying it was done. The grade above is from the independent check of its patch." if _r.get("actorCompleted") is False else "")
        _card = [mo.md(_summary), mo.md(" · ".join(_parts))]
        if _r["id"] in my_progress["captures"]:
            _shot = learner.capture(_r["id"])
            _card.append(mo.image(("data:image/jpeg;base64," if _shot[:2] == b"\xff\xd8" else "data:image/png;base64,") + base64.b64encode(_shot).decode(), alt="The app window from this attempt, captured by the independent check", caption="Your attempt's app window, captured by the independent check, not by the agent.", width="100%"))
        _cards.append(mo.vstack(_card))
    _notes = my_progress["notes"]
    _saved_notes = "\n\n".join(f"**{_title}**\n\n{_notes[_key]}" for _key, _title in [("prediction", "Your prediction"), ("observation", "What you observed"), ("limitation", "What is still unresolved"), ("observedHumanMinutes", "Your time in minutes")] if _notes.get(_key))
    mo.vstack([
        mo.md("## My work\n\n**Status:** " + my_progress["status"] + "\n\n**Check that everything works:** " + _access + "\n\n**Sandbox access:** " + ("connected for this session." if my_progress["sandboxConnected"] else "not connected.") + (f"\n\n**Spending:** an estimated ${_budget.get('spentEstimateUsd', 0):.2f} of your ${_budget['limitUsd']:g} limit." if _budget.get("limitUsd") else "\n\n**Spending:** nothing yet. You choose your limit in step 2.") + ("\n\n**Stopped:** " + str(_budget["halted"]) + ". Ask your instructor before continuing." if _budget.get("halted") else "\n\n**Stopped:** the cost of an earlier action is uncertain. Ask your instructor before continuing." if _budget.get("reservations") and not my_progress["active"] else "") + "\n\nSaved in `" + (my_progress["destination"] if _own else "your own copy, once you make one") + "`. These are your attempts. The recorded attempts above never change."),
        mo.ui.table(_rows, selection=None, pagination=False, show_column_summaries=False) if _rows else mo.md("No attempts of your own yet."),
        mo.vstack(_cards) if _cards else mo.md(""),
        mo.md(f"**See what the agent did.** Each attempt links to its conversation in Agent Lens: the prompt, every step the agent reasoned through, each command it ran and what came back. [Open all conversations in your project]({_lens}/conversations)." + (f" · [Saved progress run]({my_progress['progressUrl']})" if my_progress.get("progressUrl") else "")) if _own else mo.md(""),
        mo.md("### Your saved notes\n\n" + _saved_notes) if _saved_notes else mo.md(""),
        mo.accordion({"Details: check that everything works": mo.md("```json\n" + json.dumps(_checks, indent=2) + "\n```"), "Details: checkpoints and approval candidate": mo.md("```json\n" + json.dumps(my_progress["checkpoints"], indent=2) + "\n```"), "Details: latest action log": mo.md("```text\n" + my_progress["log"] + "\n```")})
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    observation = mo.ui.text_area(label="What happened? Name the treatment, the result, and the evidence you looked at.", rows=5, full_width=True)
    limitation = mo.ui.text_area(label="What does that evidence not tell you? What would you check next?", rows=3, full_width=True)
    measured_minutes = mo.ui.text(value="", label="Minutes you spent, if you timed it (leave blank otherwise)")
    mo.vstack([mo.md("## Your observation worksheet\n\n**6. Explain what happened.** Look at your attempt under **My work**: its checks, the app window, and the agent's conversation in Agent Lens. Compare it with your prediction, then fill this in. If you only read the recorded attempts, write about one of those instead.\n\n**Save my notes and progress** keeps your notes with this copy. **Download my notes** gives you a file to hand in, since nothing is submitted for you."), observation, limitation, measured_minutes])
    return limitation, measured_minutes, observation


@app.cell(hide_code=True)
def _(mo):
    learner_save = mo.ui.button(value=0, on_click=lambda value: value + 1, label="Save my notes and progress")
    get_save_click, set_save_click = mo.state(0)
    learner_save
    return get_save_click, learner_save, set_save_click


@app.cell(hide_code=True)
def _(
    get_save_click,
    learner,
    learner_save,
    limitation,
    measured_minutes,
    mo,
    observation,
    prediction,
    set_save_click,
):
    mo.stop(learner_save.value <= get_save_click())
    set_save_click(learner_save.value)
    try:
        learner.save_notes(prediction.value, observation.value, limitation.value, measured_minutes.value)
        _message = mo.callout(mo.md("**Saved to your private project.** Anything you left blank keeps what you saved earlier."), kind="success")
    except Exception as _error:
        _message = mo.callout(mo.md("**Not saved.** " + learner.redact(_error).rstrip(".") + ". You can still use **Download my notes** below."), kind="warn")
    _message
    return


@app.cell(hide_code=True)
def _(
    io,
    json,
    lesson_files,
    limitation,
    measured_minutes,
    mo,
    observation,
    prediction,
    project_id,
    runner_commit,
    zipfile,
):
    _notes = {"project": project_id, "runnerRevisionForSavedCase": runner_commit, "prediction": prediction.value, "observation": observation.value, "limitationsAndNextCheck": limitation.value, "observedHumanMinutes": measured_minutes.value or None, "status": "learner notes; not an independently verified grade"}
    _buffer = io.BytesIO()
    with zipfile.ZipFile(_buffer, "w", zipfile.ZIP_DEFLATED) as _zip:
        for _name, _content in lesson_files.items():
            _zip.writestr(_name, _content)
    mo.vstack([mo.download(data=json.dumps(_notes, indent=2).encode(), filename=project_id + "-observations.json", mimetype="application/json", label="Download my notes"), mo.download(data=_buffer.getvalue(), filename=project_id + "-lab-packet.zip", mimetype="application/zip", label="Download the lab brief and templates")])
    return


@app.cell(hide_code=True)
def _(learner, mo):
    _checkpoint = learner.cached_checkpoint_bytes()
    if _checkpoint is not None:
        _download = mo.download(data=_checkpoint, filename="my-lesson-checkpoint.tar.gz", mimetype="application/gzip", label="Download my progress and evidence")
    else:
        _download = mo.md("Your progress download appears here after setup, and again once a running action has finished. Results are saved to your project after every completed action.")
    _download
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Hand in the transitions as well as the diagram

    Hand in `graph.md`, the contract for each node and edge, who owns each piece of shared state, your serial and parallel measurements, evidence that the lanes were isolated, the rollback records, and two human decisions tied to checksums, with the review notes. Include at least one run that was interrupted and resumed, and explain what stopped it from doing work twice.

    Use `rollback.md` from the lab packet (**Download the lab brief and templates**, above) to route one real failed candidate. Say which layer is responsible (the plan, the code or the infrastructure), what evidence supports that, and what has to be marked invalid before the next attempt. Then compare your route with what our graph did.

    **Final discussion:** which of your routing rules are policy choices and which are technical facts? Which decision has to stay with a person? Which checkpoint would let another instructor resume your exercise without asking you anything?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Sources and further reading

    - [Step-by-step guide to running these lessons](https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-publication/docs/en/forge/classroom.md), including costs and what to do if a session is interrupted.
    - [All recorded agent conversations in Agent Lens](https://forge.coreweave.com/agent-lens/wandb/learn-harness-engineering-forge/conversations).
    - [The original course brief for this project](https://github.com/walkinglabs/learn-harness-engineering/blob/a9342ff471f2c0e60be0c08b9f4a7c502df4e442/docs/en/projects/project-08-graph-engineering-first-graph/index.md), frozen at upstream revision `a9342ff471f2`.
    - [The long-form write-up of the recorded Forge case](https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-publication/docs/en/forge/08-state-machine.md).
    - Dashboards for the recorded attempts: [evidence](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge?nw=su19wan3xra) · [main comparison](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge?nw=dfs83wdpatt) · [execution audit](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge?nw=l9e45ofb461).

    The Agent Lens and dashboard links open the course's private project, so you need view access to it. Your own attempts in this copy run with course runner revision `dcf7e447f565`. Each recorded attempt shows its own source revision under **Inspect one attempt**.
    """)
    return


if __name__ == "__main__":
    app.run()
