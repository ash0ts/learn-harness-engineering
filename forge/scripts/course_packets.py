"""Editable submission scaffolds. These do not implement or grade the exercises."""
import json

ORIGINAL = 'a9342ff471f2c0e60be0c08b9f4a7c502df4e442'
SLUGS = [
    '', 'project-01-baseline-vs-minimal-harness', 'project-02-agent-readable-workspace',
    'project-03-multi-session-continuity', 'project-04-incremental-indexing',
    'project-05-grounded-qa-verification', 'project-06-runtime-observability-and-debugging',
    'project-07-loop-engineering-first-loop', 'project-08-graph-engineering-first-graph',
]

def packet(index, lesson):
    files = {
        'LAB.md': lesson.replace('<!-- cell -->', ''),
        'README.md': '# Lab packet\n\nThese are templates for your own lab work. Nothing in them is filled in or graded. Replace every TODO with what you did in your own workspace, and keep your lab work separate from the recorded attempts in the notebook.\n\nCourse revision: '+ORIGINAL+'\n',
        'observations.csv': 'condition,source_revision,fixture,started_at,finished_at,outcome,evidence_path,human_interventions,observed_human_minutes,limitations\n',
        'comparison.md': '# Comparison\n\n## Prediction made before running\nTODO\n\n## Frozen task and conditions\nTODO\n\n## Observations and evidence\nTODO\n\n## What remains unresolved\nTODO\n\n## Proposed follow-up (new experiment)\nTODO\n',
        'interventions.csv': 'timestamp,condition,round,reason,action,observed_minutes,evidence\n',
    }
    if index in [1,2,3,6]:
        files.update({
            'AGENTS.md': '# Workspace contract\n\nTODO: startup commands, file boundaries, verification commands, acceptance criteria, and honest handoff rules.\n',
            'docs/ARCHITECTURE.md': '# Architecture\n\nTODO: map main, preload, renderer, services, persistence, and permitted dependencies to actual paths.\n',
            'docs/PRODUCT.md': '# Product contract\n\nTODO: user-visible requirements and concrete acceptance cases.\n',
            'feature_list.json': json.dumps([{'id':'TODO-feature-id','description':'TODO','dependencies':[],'status':'not_started','verificationCommand':'TODO','evidence':[],'testedAt':None}],indent=2)+'\n',
            'session-handoff.md': '# Handoff\n\n## Verified state\nTODO: revision and evidence\n\n## Incomplete work / failed checks\nTODO\n\n## Next eligible feature\nTODO\n',
            'claude-progress.md': '# Progress\n\nNo work recorded. Add timestamped observations from this attempt only.\n',
            'clean-state-checklist.md': '# Clean state\n\n- [ ] Exact revision recorded\n- [ ] Working tree inspected\n- [ ] Checks rerun and evidence retained\n- [ ] Feature statuses match evidence\n- [ ] Temporary artifacts handled\n- [ ] Handoff names incomplete work\n',
            'init.sh': '#!/usr/bin/env sh\nset -eu\n# Replace with verified commands for your selected starter.\nprintf "%s\\n" "TODO: configure and verify this startup script" >&2\nexit 1\n',
        })
    if index==1:
        files['CLAUDE.md']='# Agent entry point\n\nRead AGENTS.md. TODO: record any agent-specific startup behavior without duplicating contradictory rules.\n'
    if index==4:
        files['diagnosis.md']='# Diagnosis\n\n## Reproduction and fixture\nTODO\n\n## First guess / first supported diagnosis / final repair timestamps\nTODO\n\n## Logs establishing the cause\nTODO\n\n## Repair scope and architecture guard\nTODO\n'
    if index in [5,6]:
        files['quality-rubric.md']='# Independent rubric\n\n| Requirement | Fixture / command | Observed result | Evidence |\n|---|---|---|---|\n| TODO | TODO | Not executed | |\n'
        files['review-notes.md']='# Evaluator findings\n\nTODO: candidate checksum, concrete finding, evidence, requested change, maker response, independent verification.\n'
        files['sprint-contract.md']='# Plan\n\nTODO: scope, acceptance criteria, role inputs/outputs, allowance, and handoff rules.\n'
    if index==6:
        files['ablations.csv']='condition,removed_component,application_hash,task_hash,quality_result,cleanup_result,rerun_result,evidence\n'
    if index==7:
        files.update({
            'goal-v1.md':'# Goal v1\n\n## Desired behavior\nTODO\n\n## Verification\nTODO: command and threshold\n\n## Stop conditions\nTODO: success, deadline, rounds, cost, no progress\n\n## Constraints\nTODO\n',
            'goal-v2.md':'# Goal v2\n\nTODO: retain v1; explain which observed failure motivates each change. Label any task or budget change.\n',
            'monitoring.md':'# Monitoring contract\n\nTODO: task, interval (10–30 minutes), duration (at least two hours), permitted repair, escalation rule, cancellation, durable evidence.\n',
            'monitoring.csv':'scheduled_at,started_at,finished_at,finding,repair,false_positive,regression,followup_minutes,evidence\n',
            'maker.md':'# Maker\n\nTODO: task, allowed edits, candidate export, checks, and handoff.\n',
            'checker.md':'# Checker\n\nTODO: fresh context, acceptance contract, independent checks, concrete findings.\n',
            'controller.md':'# Controller\n\nTODO: state transitions, retry rules, budgets, duplicate-launch reconciliation, and stop conditions.\n',
            'loop-state.md':'# Loop state\n\n| Round | Candidate checksum | Maker action | Checker evidence | Outcome | Intervention | Next action |\n|---|---|---|---|---|---|---|\n| TODO | | | | Not executed | | |\n',
        })
    if index==8:
        files.update({
            'graph.md':'# Graph contract\n\n## Nodes: purpose / inputs / outputs / owner / failure\nTODO\n\n## Edges and conditions (include an implicit edge)\nTODO\n\n## Durable state and ownership\nTODO\n\n## Fan-out / fan-in and lane isolation\nTODO\n\n## Targeted rollback and invalidation\nTODO\n\n## Human approval and resume\nTODO\n',
            'serial-parallel.csv':'mode,candidate_sha256,fixture,resources,wall_seconds,input_tokens,output_tokens,cost_estimate,quality,evidence\n',
            'review-decisions.json':json.dumps([{'pass':i,'candidateSha256':None,'decision':None,'actor':None,'decidedAt':None,'observedWaitSeconds':None,'evidence':[],'issuesCaught':[]} for i in [1,2]],indent=2)+'\n',
            'rollback.md':'# Rollback record\n\nTODO: failed candidate, evidence, responsible layer, chosen route, invalidated state, retained artifacts, resumed result.\n',
        })
    return files
