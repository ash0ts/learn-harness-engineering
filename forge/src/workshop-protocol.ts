import {readFile} from 'node:fs/promises';
import {join} from 'node:path';
import {protocol} from './trial.js';
import {workshopCourseRoot} from './workshop-workspace.js';
/** Research settings and denominators remain frozen in protocol.json. */
export async function workshopProtocol(){
  const research=await protocol();
  return {...research,protocolRevision:'workshop-v1',pricing:JSON.parse(await readFile(join(workshopCourseRoot,'forge/workshop/base/workshop/pricing.json'),'utf8')),controlsRequired:false,cohort:'workshop-v1'};
}
