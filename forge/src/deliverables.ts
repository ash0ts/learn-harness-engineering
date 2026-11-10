/** Format witnesses are recorded separately from semantic/task correctness. */
export function hasDeliverable(text:string,kind:'handoff'|'plan'|'review'){
  const headings=kind==='handoff'?['Changes','Verification','Unfinished','Next steps']:kind==='plan'?['Plan','Verification']:['Findings','Verification'];
  const title=kind==='handoff'?'Session handoff':kind==='plan'?'Plan':'Review';
  return new RegExp(`^# ${title}\\s*$`,'im').test(text)&&headings.every(heading=>new RegExp(`^#{1,3} ${heading}\\s*\\n\\s*\\S`,'im').test(text));
}
export function deliverableInstruction(kind:'handoff'|'plan'|'review'){
  return kind==='handoff'?'Return Markdown headed # Session handoff, with sections ## Changes, ## Verification, ## Unfinished and ## Next steps, each with concrete content or an explicit none. Include paths and observed checks; only this complete format will be saved verbatim as session-handoff.md.':
    kind==='plan'?'Return Markdown headed # Plan with a concrete implementation plan and ## Verification. Include inspected paths and planned checks.':
    'Return Markdown headed # Review with ## Findings and ## Verification. Include inspected paths, actual observed checks, failures and omissions.';
}
export function diagnosisEvidence(text:string,tools:Array<{command?:string;stdout?:string}>){
  return {schemaVersion:1,statementAboutLongDocumentEmptyChunks:/1[,]?000/.test(text)&&/empty/i.test(text)&&/chunk/i.test(text),
    sourceLocationMentioned:/indexing-service|chunkDocument/.test(text),
    runtimeCommandsObserved:tools.filter(t=>/node|npm|runtime-feedback/.test(t.command??'')&&/chunk|index/i.test(t.stdout??'')).length,
    interpretation:'Text and trace evidence indicators only; not a semantic diagnosis grade. Repair, logging and architecture are independently graded by the protected checker.'};
}
