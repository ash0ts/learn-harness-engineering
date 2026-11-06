import {config, publicConfig} from './config.js';
import {runServices} from './headless.js';
import {writeJson} from './records.js';

const command = process.argv[2] ?? 'help';
if (command === 'doctor') {
  const c = config();
  console.log(JSON.stringify({node: process.version, config: publicConfig(c), credentialsConfigured: Boolean(c.apiKey), liveReady: Boolean(c.apiKey && c.entity)}, null, 2));
} else if (command === 'services') {
  const [app, output, ...fixtures] = process.argv.slice(3).filter(arg => arg !== '--live');
  if (!app || !output || !fixtures.length) throw new Error('services APP_DIR OUTPUT_JSON FIXTURE... [--live]');
  await writeJson(output, await runServices(app, fixtures, process.argv.includes('--live')));
} else {
  console.log('Forge course: doctor (offline configuration check)');
}
