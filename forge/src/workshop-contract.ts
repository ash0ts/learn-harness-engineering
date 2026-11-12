import {createHash, randomUUID} from 'node:crypto';
import {lstat, readFile, mkdir, writeFile} from 'node:fs/promises';
import {dirname, join, relative, resolve, sep} from 'node:path';

export const WORKSHOP_PROTOCOL = 'workshop-v1' as const;
export type WorkshopProject = 'project-01'|'project-02'|'project-03'|'project-04'|'project-05';
export interface WorkshopManifest {
  schemaVersion: 1; protocol: typeof WORKSHOP_PROTOCOL; project: WorkshopProject;
  sourceCommit: string; title: string; editable: string[]; files: Record<string,string>;
  scenarios: string[]; task: string; hints: string[]; checks: string[];
}
export interface WorkshopSnapshot {
  schemaVersion: 1; protocol: typeof WORKSHOP_PROTOCOL; id: string; project: WorkshopProject;
  sourceCommit: string; parent?: string; assisted: boolean; createdAt: string;
  files: Record<string,string>; checksums: Record<string,string>; sha256: string;
}
export interface WorkshopResult {
  schemaVersion: 1; protocol: typeof WORKSHOP_PROTOCOL; id: string; project: WorkshopProject;
  snapshotId: string; snapshotSha256: string; sourceCommit: string; action: string;
  startedAt: string; finishedAt?: string; outcome: string;
  checks: Array<{name:string;passed:boolean;detail?:string}>;
  evidence: string[]; conversationIds: string[]; sandboxIds: string[];
  cleanupStatus: string; telemetryStatus: string; publicationStatus: string;
  inputTokens?: number; outputTokens?: number; estimatedCostUsd?: number|null;
  error?: string; [key:string]: unknown;
}
export const sha256 = (value: string|Uint8Array) => createHash('sha256').update(value).digest('hex');
export function workshopPath(name:string) {
  if (!name || name.includes('\\') || name.includes('\0') || name.startsWith('/') || name.includes(':') ||
      name.split('/').some(p=>!p || p==='.' || p==='..') || /^(?:node_modules|\.git|\.env|dist)(?:\/|$)/.test(name)) {
    throw new Error(`Unsafe workshop path: ${name}`);
  }
  return name;
}
export async function safeWorkshopPath(root:string,name:string) {
  workshopPath(name);
  const base=resolve(root), destination=resolve(base,name);
  if(!destination.startsWith(base+sep))throw new Error('Workshop path escaped its workspace');
  // Inspect every existing component, including the root. Never follow a link.
  let cursor=base;
  for(const part of ['',...name.split('/')]) {
    if(part)cursor=join(cursor,part);
    try {if((await lstat(cursor)).isSymbolicLink())throw new Error('Workshop symlink rejected');}
    catch(error){if((error as NodeJS.ErrnoException).code!=='ENOENT')throw error;}
  }
  return destination;
}
function fileHashes(files:Record<string,string>) {
  const hashes:Record<string,string>={};
  for(const name of Object.keys(files).sort())hashes[workshopPath(name)]=sha256(files[name]);
  return hashes;
}
function fingerprint(snapshot:Pick<WorkshopSnapshot,'project'|'sourceCommit'|'checksums'>) {
  return sha256(JSON.stringify([WORKSHOP_PROTOCOL,snapshot.project,snapshot.sourceCommit,Object.entries(snapshot.checksums).sort()]));
}
export function validateSnapshot(value:WorkshopSnapshot,manifest?:WorkshopManifest,secrets:string[]=[]) {
  if(value.schemaVersion!==1 || value.protocol!==WORKSHOP_PROTOCOL || !/^project-0[1-5]$/.test(value.project) ||
     !/^[a-f0-9]{40}$/.test(value.sourceCommit) || !/^[A-Za-z0-9-]+$/.test(value.id))throw new Error('Invalid workshop snapshot');
  if(!value.files || typeof value.files!=='object' || Object.keys(value.files).length>250)throw new Error('Invalid snapshot files');
  let bytes=0;
  for(const [name,content]of Object.entries(value.files)) {
    workshopPath(name);
    if(typeof content!=='string'||(bytes+=Buffer.byteLength(content))>5_000_000)throw new Error('Workshop source exceeds 5 MB');
    if(secrets.some(secret=>secret&&content.includes(secret)) || /(?:\/Users\/|\/home\/|[A-Z]:\\Users\\)/.test(content) ||
      /(?:WANDB_API_KEY|OPENAI_API_KEY)\s*[=:]\s*["']?[A-Za-z0-9_-]{20,}/.test(content))throw new Error(`Private value in ${name}; remove it before saving`);
  }
  const hashes=fileHashes(value.files);
  if(JSON.stringify(Object.entries(hashes).sort())!==JSON.stringify(Object.entries(value.checksums??{}).sort()) ||
    fingerprint({...value,checksums:hashes})!==value.sha256)throw new Error('Workshop checksum mismatch');
  if(manifest) {
    if(value.project!==manifest.project||value.sourceCommit!==manifest.sourceCommit)throw new Error('Incompatible lesson or checkpoint revision');
    if(JSON.stringify(Object.keys(value.files).sort())!==JSON.stringify(Object.keys(manifest.files).sort()))throw new Error('Snapshot file set changed');
    for(const [name,content]of Object.entries(value.files))if(!manifest.editable.includes(name)&&sha256(content)!==manifest.files[name])throw new Error(`Protected workshop file changed: ${name}`);
  }
  return value;
}
export function makeSnapshot(manifest:WorkshopManifest,files:Record<string,string>,options:{parent?:string;assisted?:boolean;secrets?:string[]}={}) {
  const snapshot:WorkshopSnapshot={schemaVersion:1,protocol:WORKSHOP_PROTOCOL,id:randomUUID(),project:manifest.project,
    sourceCommit:manifest.sourceCommit,parent:options.parent,assisted:options.assisted??false,createdAt:new Date().toISOString(),files,
    checksums:fileHashes(files),sha256:''};
  snapshot.sha256=fingerprint(snapshot);
  return validateSnapshot(snapshot,manifest,options.secrets);
}
export async function readWorkshopFiles(root:string,manifest:WorkshopManifest) {
  const files:Record<string,string>={};
  for(const name of Object.keys(manifest.files).sort())files[name]=await readFile(await safeWorkshopPath(root,name),'utf8');
  return files;
}
export async function writeWorkshopEdits(root:string,manifest:WorkshopManifest,edits:Record<string,string>) {
  // Validate the entire submission before writing its first file.
  const paths:Record<string,string>={};
  for(const [name,content]of Object.entries(edits)) {
    if(!manifest.editable.includes(name)||typeof content!=='string')throw new Error(`Not an editable lesson file: ${name}`);
    paths[name]=await safeWorkshopPath(root,name);
  }
  for(const [name,content]of Object.entries(edits)){await mkdir(dirname(paths[name]),{recursive:true});await writeFile(paths[name],content);}
}
export async function storeSnapshot(root:string,snapshot:WorkshopSnapshot) {
  validateSnapshot(snapshot);
  const file=await safeWorkshopPath(root,`snapshots/${snapshot.id}.json`);
  await mkdir(dirname(file),{recursive:true});
  // Immutable even when a caller retries after a network or process interruption.
  try {await writeFile(file,JSON.stringify(snapshot,null,2)+'\n',{flag:'wx',mode:0o600});}
  catch(error){if((error as NodeJS.ErrnoException).code!=='EEXIST'||sha256(await readFile(file))!==sha256(JSON.stringify(snapshot,null,2)+'\n'))throw error;}
  return relative(root,file).split(sep).join('/');
}
