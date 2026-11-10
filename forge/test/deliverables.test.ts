import {test} from 'node:test';
import assert from 'node:assert/strict';
import {hasDeliverable,diagnosisEvidence} from '../src/deliverables.js';
test('a bare completion or partial handoff is never manufactured into a handoff',()=>{
 assert.equal(hasDeliverable('Done. Fixed it.','handoff'),false);
 assert.equal(hasDeliverable('# Session handoff\n## Changes\nFixed indexing.','handoff'),false);
 assert.equal(hasDeliverable('# Session handoff\n## Changes\nsrc/indexing.ts\n## Verification\nnpm test failed\n## Unfinished\nUI check\n## Next steps\nRun Electron','handoff'),true);
});
test('plans and reviews need their requested deliverables, without manufacturing missing text',()=>{
 assert.equal(hasDeliverable("I'll inspect the files next.",'plan'),false);
 assert.equal(hasDeliverable('# Plan\nInspect the service and repair it.\n## Verification\nRun the long fixture.','plan'),true);
 assert.equal(hasDeliverable('# Review\n## Findings\nMissing reset.\n## Verification\nObserved stale history.','review'),true);
});
test('diagnosis statement evidence stays separate from runtime observations and repair',()=>{
 const empty=diagnosisEvidence('Done',[]);assert.equal(empty.statementAboutLongDocumentEmptyChunks,false);assert.equal(empty.runtimeCommandsObserved,0);
 const observed=diagnosisEvidence('chunkDocument in indexing-service emits empty chunks above 1000 characters.',[{command:'node probe.js',stdout:'chunks empty'}]);assert.equal(observed.statementAboutLongDocumentEmptyChunks,true);assert.equal(observed.runtimeCommandsObserved,1);assert.match(observed.interpretation,/not a semantic diagnosis grade/);
});
