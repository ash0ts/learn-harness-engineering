export interface GraphObservation {phase:'plan'|'verified'; outcome:string; repairs:number; maxRepairs:number; cleanupVerified:boolean; usageComplete:boolean}
export function route(observation:GraphObservation):'verify'|'repair'|'approval'|'stop'|'recover' {
  if(!observation.cleanupVerified || !observation.usageComplete) return 'recover';
  if(observation.phase==='plan') return 'verify';
  if(observation.outcome==='passed') return 'approval';
  return observation.repairs<observation.maxRepairs ? 'repair' : 'stop';
}
export function verificationMode():'serial'|'parallel' { return 'parallel'; }
