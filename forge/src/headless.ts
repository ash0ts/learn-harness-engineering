import {createRequire} from 'node:module';
import {resolve, join} from 'node:path';
import {mkdtemp, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {performance} from 'node:perf_hooks';

/** Load the selected application's actual compiled services, never a Python reimplementation. */
export async function runServices(appDir: string, fixturePaths: string[], live = false) {
  const app = resolve(appDir);
  const require = createRequire(join(app, 'package.json'));
  const {PersistenceService} = require(join(app, 'dist/services/persistence-service.js'));
  const {DocumentService} = require(join(app, 'dist/services/document-service.js'));
  const {IndexingService} = require(join(app, 'dist/services/indexing-service.js'));
  const {QaService} = require(join(app, 'dist/services/qa-service.js'));
  const hooks = require(join(app, 'dist/services/forge-hooks.js'));
  if (live) hooks.setForgeHooks(await (await import('./app.js')).createAppHooks(appDir));
  const dataDir = await mkdtemp(join(tmpdir(), 'forge-services-'));
  try {
    const persistence = new PersistenceService(dataDir);
    const documents = new DocumentService(persistence);
    const index = new IndexingService(persistence);
    const qa = new QaService(persistence, index);
    const start = performance.now();
    const imported = fixturePaths.map(file => documents.importDocument(resolve(file)));
    const importedAt = performance.now();
    const status = await index.startIndexing();
    const indexedAt = performance.now();
    const answers = [];
    for (const question of ['How are documents indexed?', 'What architecture does the app use?']) answers.push(await qa.ask(question));
    const endedAt = performance.now();
    return {mode: live ? 'live' : 'offline', imported: imported.length, status,
      chunks: index.getAllChunks(), answers, history: qa.getHistory(),
      timingsMs: {import: importedAt-start, index: indexedAt-importedAt, qa: endedAt-indexedAt}};
  } finally {
    await hooks.shutdownForgeHooks(); hooks.setForgeHooks(undefined);
    await rm(dataDir, {recursive: true, force: true});
  }
}
