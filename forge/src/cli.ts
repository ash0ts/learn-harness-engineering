import {config, publicConfig} from './config.js';

const command = process.argv[2] ?? 'help';
if (command === 'doctor') {
  const c = config();
  console.log(JSON.stringify({node: process.version, config: publicConfig(c), credentialsConfigured: Boolean(c.apiKey), liveReady: Boolean(c.apiKey && c.entity)}, null, 2));
} else {
  console.log('Forge course: doctor (offline configuration check)');
}
