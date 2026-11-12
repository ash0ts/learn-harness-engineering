export interface Observation {round:number; maxRounds:number; now:number; deadline:number; outcome:string; checks:Array<{name:string;passed:boolean}>}
export function nextAction(observation:Observation):'run'|'stop' {
  if(observation.round>=observation.maxRounds || observation.now>=observation.deadline) return 'stop';
  return observation.outcome==='passed' ? 'stop' : 'run';
}
export function nextPrompt(observation:Observation):string {
  return 'Preserve the existing patch. Repair these observed failures: '+JSON.stringify(observation.checks.filter(check=>!check.passed));
}
